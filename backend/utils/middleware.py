from functools import wraps
from flask import request, jsonify, g
from backend.utils.security import decode_token, sanitize_user
from backend.database import get_db, make_id_query

def token_required(f):
    """Decorator ensuring request contains a valid JWT Bearer token."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"success": False, "error": "Authentication token is missing. Please log in."}), 401
        
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({"success": False, "error": "Invalid Authorization header format. Expected 'Bearer <token>'."}), 401
        
        token = parts[1]
        payload = decode_token(token)
        if not payload:
            return jsonify({"success": False, "error": "Token is invalid or has expired. Please log in again."}), 401
        
        user_id = payload.get("sub")
        users_col = get_db().get_collection("users")
        user = None
        if user_id:
            user = users_col.find_one(make_id_query(user_id))
        
        # Fallback query by email if not found by id
        if not user and payload.get("email"):
            user = users_col.find_one({"email": payload.get("email")})

        if user:
            # Check account active status
            if user.get("is_active") is False:
                return jsonify({
                    "success": False,
                    "error": "Your account has been deactivated. Please contact system administrator."
                }), 403
            cleaned_user = sanitize_user(user)
        else:
            # Validly signed token whose user record is not directly indexed
            cleaned_user = {
                "id": str(user_id or "user"),
                "_id": str(user_id or "user"),
                "email": payload.get("email", ""),
                "role": (payload.get("role") or "farmer").lower(),
                "full_name": payload.get("email", "User"),
                "is_active": True
            }

        g.current_user = cleaned_user
        
        return f(current_user=cleaned_user, *args, **kwargs)
    return decorated

def roles_required(*allowed_roles):
    """Decorator ensuring authenticated user possesses one of the allowed roles."""
    def decorator(f):
        @wraps(f)
        @token_required
        def decorated_function(current_user, *args, **kwargs):
            user_role = (current_user.get("role") or "").lower()
            normalized_allowed = [r.lower() for r in allowed_roles]
            
            if user_role not in normalized_allowed and user_role != "admin":
                return jsonify({
                    "success": False,
                    "error": f"Access denied. Required role: {', '.join(allowed_roles)}. Your role is '{user_role}'."
                }), 403
            
            return f(current_user=current_user, *args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Decorator strictly restricting endpoint access to authenticated ADMIN role only."""
    @wraps(f)
    @token_required
    def decorated(current_user, *args, **kwargs):
        role = (current_user.get("role") or "").lower()
        if role != "admin":
            return jsonify({
                "success": False,
                "error": "Access denied: Administrative privileges required."
            }), 403
        return f(current_user=current_user, *args, **kwargs)
    return decorated
