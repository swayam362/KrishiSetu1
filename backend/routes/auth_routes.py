import datetime
from flask import Blueprint, jsonify, request
from backend.database import get_db
from backend.utils.security import (
    hash_password,
    verify_password,
    generate_token,
    validate_email,
    validate_phone,
    sanitize_string,
    sanitize_user
)
from backend.utils.middleware import token_required, roles_required

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

VALID_ROLES = ["farmer", "buyer", "admin"]

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user (Farmer, Buyer, or Admin) with secure validation."""
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"success": False, "error": "Invalid JSON body provided."}), 400

    # 1. Validate & normalize role
    role = sanitize_string(str(data.get('role', 'farmer'))).lower()
    if role not in VALID_ROLES:
        return jsonify({"success": False, "error": f"Invalid role '{role}'. Allowed roles: {', '.join(VALID_ROLES)}"}), 400

    # 2. Extract & validate core fields
    full_name = sanitize_string(str(data.get('full_name') or data.get('name') or ''))
    email = sanitize_string(str(data.get('email', ''))).lower()
    phone = sanitize_string(str(data.get('phone', '')))
    password = data.get('password')
    state = sanitize_string(str(data.get('state', '')))
    district = sanitize_string(str(data.get('district', '')))

    if not full_name:
        return jsonify({"success": False, "error": "Full name is required."}), 400
    
    if not validate_email(email):
        return jsonify({"success": False, "error": "Please provide a valid email address."}), 400

    if not validate_phone(phone):
        return jsonify({"success": False, "error": "Please provide a valid 10-digit mobile number."}), 400

    if not password or not isinstance(password, str) or len(password) < 6:
        return jsonify({"success": False, "error": "Password must be at least 6 characters long."}), 400

    if not state or not district:
        return jsonify({"success": False, "error": "State and District are required."}), 400

    # 3. Role-specific validation
    user_doc = {
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "role": role,
        "state": state,
        "district": district,
        "created_at": datetime.datetime.utcnow().isoformat(),
        "is_active": True
    }

    if role == "farmer":
        village = sanitize_string(str(data.get('village') or data.get('city') or ''))
        if not village:
            return jsonify({"success": False, "error": "Village/City is required for Farmer registration."}), 400
        user_doc["village"] = village
        user_doc["farm_size_acres"] = sanitize_string(str(data.get('farm_size_acres', '')))
        user_doc["primary_crops"] = sanitize_string(str(data.get('primary_crops', '')))
    elif role == "buyer":
        business_name = sanitize_string(str(data.get('business_name', '')))
        city = sanitize_string(str(data.get('city') or data.get('village') or ''))
        if not business_name:
            return jsonify({"success": False, "error": "Business name is required for Buyer registration."}), 400
        if not city:
            return jsonify({"success": False, "error": "City is required for Buyer registration."}), 400
        user_doc["business_name"] = business_name
        user_doc["city"] = city
        user_doc["gstin"] = sanitize_string(str(data.get('gstin', '')))

    # 4. Check for duplicate email or phone in database
    users_col = get_db().get_collection("users")
    existing_user = users_col.find_one({"$or": [{"email": email}, {"phone": phone}]})
    if existing_user:
        if existing_user.get("email") == email:
            return jsonify({"success": False, "error": "An account with this email address already exists."}), 409
        if existing_user.get("phone") == phone:
            return jsonify({"success": False, "error": "An account with this phone number already exists."}), 409

    # 5. Hash password with bcrypt and persist
    hashed_pwd = hash_password(password)
    user_doc["password_hash"] = hashed_pwd

    insert_result = users_col.insert_one(user_doc)
    user_id = str(insert_result.inserted_id if hasattr(insert_result, 'inserted_id') else user_doc.get('_id', ''))
    user_doc["_id"] = user_id

    # 6. Generate signed JWT token
    token = generate_token(user_id=user_id, role=role, email=email)
    safe_user = sanitize_user(user_doc)

    return jsonify({
        "success": True,
        "message": f"{role.capitalize()} account created successfully.",
        "token": token,
        "user": safe_user
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user with email/phone and password, returning JWT."""
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"success": False, "error": "Invalid JSON body provided."}), 400

    identifier = sanitize_string(str(data.get('email') or data.get('identifier') or '')).lower()
    password = data.get('password')
    requested_role = sanitize_string(str(data.get('role', ''))).lower()

    if not identifier:
        return jsonify({"success": False, "error": "Email or mobile number is required."}), 400

    if not password or not isinstance(password, str):
        return jsonify({"success": False, "error": "Password is required."}), 400

    # Query user by email or phone
    users_col = get_db().get_collection("users")
    user = users_col.find_one({"$or": [{"email": identifier}, {"phone": identifier}]})

    if not user:
        return jsonify({"success": False, "error": "Invalid email/phone or password."}), 401

    # Verify bcrypt password
    stored_hash = user.get("password_hash")
    if not stored_hash or not verify_password(password, stored_hash):
        return jsonify({"success": False, "error": "Invalid email/phone or password."}), 401

    # Optional role check if frontend requested a specific dashboard mode
    actual_role = user.get("role", "farmer")
    if requested_role and requested_role in VALID_ROLES and actual_role != requested_role and actual_role != "admin":
        return jsonify({
            "success": False,
            "error": f"Account is registered as '{actual_role.upper()}', not '{requested_role.upper()}'."
        }), 403

    user_id = str(user.get("_id"))
    token = generate_token(user_id=user_id, role=actual_role, email=user.get("email", ""))
    safe_user = sanitize_user(user)

    return jsonify({
        "success": True,
        "message": "Login successful.",
        "token": token,
        "user": safe_user
    }), 200


@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """Retrieve authenticated user's profile strictly identified from JWT."""
    return jsonify({
        "success": True,
        "user": current_user
    }), 200


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Client token invalidation acknowledgement."""
    return jsonify({
        "success": True,
        "message": "Logged out successfully."
    }), 200


@auth_bp.route('/farmer-only-action', methods=['GET'])
@roles_required("farmer")
def farmer_protected_route(current_user):
    """Protected test endpoint accessible only by Farmers and Admins."""
    return jsonify({
        "success": True,
        "message": f"Hello Farmer {current_user.get('full_name')}, you have access to proprietary crop data.",
        "user_id": current_user.get("id")
    }), 200


@auth_bp.route('/buyer-only-action', methods=['GET'])
@roles_required("buyer")
def buyer_protected_route(current_user):
    """Protected test endpoint accessible only by Buyers and Admins."""
    return jsonify({
        "success": True,
        "message": f"Hello Buyer {current_user.get('full_name')} ({current_user.get('business_name')}), you have access to procurement quotes.",
        "user_id": current_user.get("id")
    }), 200
