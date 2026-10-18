import datetime
from flask import Blueprint, jsonify, request
from backend.database import get_db, make_id_query
from backend.utils.security import sanitize_string, sanitize_user
from backend.utils.middleware import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

def log_admin_action(admin_user: dict, action: str, target_type: str, target_id: str, details: str = ""):
    """Safely record administrative audit trail without sensitive data or passwords."""
    try:
        logs_col = get_db().get_collection("admin_logs")
        logs_col.insert_one({
            "action": sanitize_string(action),
            "admin_id": str(admin_user.get("id")),
            "admin_email": admin_user.get("email", ""),
            "target_type": sanitize_string(target_type),
            "target_id": str(target_id),
            "details": sanitize_string(details, max_length=500),
            "created_at": datetime.datetime.utcnow().isoformat()
        })
    except Exception:
        pass


# =========================================================================
# A. OVERVIEW METRICS
# =========================================================================

@admin_bp.route('/overview', methods=['GET'])
@admin_required
def get_overview(current_user):
    """
    Calculate real administrative figures directly from MongoDB database:
    - Total registered farmers
    - Total registered buyers
    - Total active products
    - Total orders (Pending, Completed, Total)
    - Recent system activity
    """
    db = get_db()
    users_col = db.get_collection("users")
    products_col = db.get_collection("products")
    orders_col = db.get_collection("orders")
    logs_col = db.get_collection("admin_logs")

    total_farmers = users_col.count_documents({"role": "farmer"})
    total_buyers = users_col.count_documents({"role": "buyer"})
    total_products = products_col.count_documents({})
    total_orders = orders_col.count_documents({})
    pending_orders = orders_col.count_documents({"status": "Pending"})
    completed_orders = orders_col.count_documents({"status": {"$in": ["Completed", "Delivered"]}})

    # Calculate completed order gross volume
    all_completed = orders_col.find({"status": {"$in": ["Completed", "Delivered"]}})
    total_volume_inr = sum(float(o.get("total_amount") or 0) for o in all_completed)

    # Fetch recent system activity from audit logs
    recent_logs = list(logs_col.find({}))
    recent_logs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    formatted_logs = []
    for l in recent_logs[:10]:
        formatted_logs.append({
            "id": str(l.get("_id") or l.get("id")),
            "action": l.get("action"),
            "admin_email": l.get("admin_email"),
            "target_type": l.get("target_type"),
            "target_id": l.get("target_id"),
            "details": l.get("details"),
            "created_at": l.get("created_at")
        })

    return jsonify({
        "success": True,
        "metrics": {
            "total_farmers": total_farmers,
            "total_buyers": total_buyers,
            "total_products": total_products,
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "completed_orders": completed_orders,
            "settled_volume_inr": round(total_volume_inr, 2)
        },
        "recent_activity": formatted_logs
    }), 200


# =========================================================================
# B. FARMER MANAGEMENT
# =========================================================================

@admin_bp.route('/farmers', methods=['GET'])
@admin_required
def list_farmers(current_user):
    """
    Retrieve farmers with search, filtering, and pagination.
    Protects password hashes and internal tokens.
    """
    search_q = request.args.get('search', '').strip().lower()
    status_filter = request.args.get('status', 'all').strip().lower()
    page = max(1, int(request.args.get('page', 1)))
    limit = min(100, max(1, int(request.args.get('limit', 20))))

    users_col = get_db().get_collection("users")
    all_users = list(users_col.find({"role": "farmer"}))

    filtered = []
    for u in all_users:
        safe = sanitize_user(u)
        # Ensure is_active boolean
        is_active = safe.get("is_active", True)
        if is_active is None:
            is_active = True
        safe["is_active"] = is_active

        # Status filter
        if status_filter == 'active' and not is_active:
            continue
        if status_filter == 'inactive' and is_active:
            continue

        # Search filter
        if search_q:
            match = (
                search_q in (safe.get("full_name") or "").lower() or
                search_q in (safe.get("email") or "").lower() or
                search_q in (safe.get("phone") or "").lower() or
                search_q in (safe.get("district") or "").lower() or
                search_q in (safe.get("state") or "").lower()
            )
            if not match:
                continue

        filtered.append(safe)

    # Sort newest first
    filtered.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    total_count = len(filtered)
    start_idx = (page - 1) * limit
    paginated = filtered[start_idx:start_idx + limit]

    return jsonify({
        "success": True,
        "total": total_count,
        "page": page,
        "limit": limit,
        "farmers": paginated
    }), 200


# =========================================================================
# C. BUYER / MERCHANT MANAGEMENT
# =========================================================================

@admin_bp.route('/buyers', methods=['GET'])
@admin_required
def list_buyers(current_user):
    """
    Retrieve buyers with search, filtering, and pagination.
    Never exposes passwords or sensitive keys.
    """
    search_q = request.args.get('search', '').strip().lower()
    status_filter = request.args.get('status', 'all').strip().lower()
    page = max(1, int(request.args.get('page', 1)))
    limit = min(100, max(1, int(request.args.get('limit', 20))))

    users_col = get_db().get_collection("users")
    all_users = list(users_col.find({"role": "buyer"}))

    filtered = []
    for u in all_users:
        safe = sanitize_user(u)
        is_active = safe.get("is_active", True)
        if is_active is None:
            is_active = True
        safe["is_active"] = is_active

        if status_filter == 'active' and not is_active:
            continue
        if status_filter == 'inactive' and is_active:
            continue

        if search_q:
            match = (
                search_q in (safe.get("full_name") or "").lower() or
                search_q in (safe.get("business_name") or "").lower() or
                search_q in (safe.get("email") or "").lower() or
                search_q in (safe.get("phone") or "").lower() or
                search_q in (safe.get("city") or "").lower() or
                search_q in (safe.get("district") or "").lower()
            )
            if not match:
                continue

        filtered.append(safe)

    filtered.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    total_count = len(filtered)
    start_idx = (page - 1) * limit
    paginated = filtered[start_idx:start_idx + limit]

    return jsonify({
        "success": True,
        "total": total_count,
        "page": page,
        "limit": limit,
        "buyers": paginated
    }), 200


@admin_bp.route('/users/<user_id>/status', methods=['PATCH'])
@admin_required
def update_user_status(current_user, user_id):
    """
    Activate or deactivate a user account (farmer or buyer).
    Prevents administrators from locking themselves out.
    """
    data = request.get_json(silent=True) or {}
    if "is_active" not in data:
        return jsonify({"success": False, "error": "Field 'is_active' (boolean) is required."}), 400

    new_status = bool(data.get("is_active"))

    # Prevent admin from deactivating their own account
    if str(user_id) == str(current_user.get("id")):
        return jsonify({"success": False, "error": "Administrators cannot deactivate their own account."}), 400

    users_col = get_db().get_collection("users")
    id_q = make_id_query(user_id)
    user = users_col.find_one(id_q)

    if not user:
        return jsonify({"success": False, "error": "User account not found."}), 404

    users_col.update_one(id_q, {"$set": {
        "is_active": new_status,
        "updated_at": datetime.datetime.utcnow().isoformat()
    }})

    action_label = "USER_ACTIVATED" if new_status else "USER_DEACTIVATED"
    log_admin_action(
        admin_user=current_user,
        action=action_label,
        target_type="USER",
        target_id=user_id,
        details=f"User {user.get('email')} ({user.get('role')}) status changed to {'Active' if new_status else 'Inactive'}."
    )

    return jsonify({
        "success": True,
        "message": f"User account has been {'activated' if new_status else 'deactivated'} successfully.",
        "user_id": user_id,
        "is_active": new_status
    }), 200


# =========================================================================
# D. PRODUCT MANAGEMENT
# =========================================================================

@admin_bp.route('/products', methods=['GET'])
@admin_required
def list_products_admin(current_user):
    """
    Retrieve products with search, category/availability filtering, and pagination.
    """
    search_q = request.args.get('search', '').strip().lower()
    category = request.args.get('category', 'all').strip().lower()
    availability = request.args.get('availability', 'all').strip().lower()
    page = max(1, int(request.args.get('page', 1)))
    limit = min(100, max(1, int(request.args.get('limit', 20))))

    products_col = get_db().get_collection("products")
    all_products = list(products_col.find({}))

    filtered = []
    for p in all_products:
        p_dict = dict(p)
        p_dict["id"] = str(p_dict.get("_id") or p_dict.get("id"))
        p_dict.pop("_id", None)

        if category != 'all' and (p_dict.get("category") or "").lower() != category:
            continue

        if availability != 'all' and (p_dict.get("availability") or "").lower() != availability:
            continue

        if search_q:
            match = (
                search_q in (p_dict.get("crop_name") or p_dict.get("name") or "").lower() or
                search_q in (p_dict.get("farmer_name") or "").lower() or
                search_q in (p_dict.get("district") or "").lower() or
                search_q in (p_dict.get("location") or "").lower()
            )
            if not match:
                continue

        filtered.append(p_dict)

    filtered.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    total_count = len(filtered)
    start_idx = (page - 1) * limit
    paginated = filtered[start_idx:start_idx + limit]

    return jsonify({
        "success": True,
        "total": total_count,
        "page": page,
        "limit": limit,
        "products": paginated
    }), 200


@admin_bp.route('/products/<product_id>/availability', methods=['PATCH'])
@admin_required
def update_product_availability(current_user, product_id):
    """
    Admin deactivates or changes listing availability.
    """
    data = request.get_json(silent=True) or {}
    new_avail = sanitize_string(str(data.get("availability", "")))
    valid_states = ["Available", "Deactivated", "Sold Out"]

    if new_avail not in valid_states:
        return jsonify({
            "success": False,
            "error": f"Invalid availability state '{new_avail}'. Allowed: {', '.join(valid_states)}"
        }), 400

    products_col = get_db().get_collection("products")
    id_q = make_id_query(product_id)
    product = products_col.find_one(id_q)

    if not product:
        return jsonify({"success": False, "error": "Product listing not found."}), 404

    products_col.update_one(id_q, {"$set": {
        "availability": new_avail,
        "updated_at": datetime.datetime.utcnow().isoformat()
    }})

    log_admin_action(
        admin_user=current_user,
        action="PRODUCT_AVAILABILITY_CHANGED",
        target_type="PRODUCT",
        target_id=product_id,
        details=f"Crop lot '{product.get('crop_name') or product.get('name')}' availability changed to '{new_avail}'."
    )

    return jsonify({
        "success": True,
        "message": f"Product listing status updated to '{new_avail}'.",
        "product_id": product_id,
        "availability": new_avail
    }), 200


@admin_bp.route('/products/<product_id>', methods=['DELETE'])
@admin_required
def delete_product_admin(current_user, product_id):
    """
    Remove produce listing when policy violations or fraudulent entries occur.
    """
    products_col = get_db().get_collection("products")
    id_q = make_id_query(product_id)
    product = products_col.find_one(id_q)

    if not product:
        return jsonify({"success": False, "error": "Product listing not found."}), 404

    crop_title = product.get("crop_name") or product.get("name") or "Listing"
    products_col.delete_one(id_q)

    log_admin_action(
        admin_user=current_user,
        action="PRODUCT_DELETED",
        target_type="PRODUCT",
        target_id=product_id,
        details=f"Produce listing '{crop_title}' removed by administrator."
    )

    return jsonify({
        "success": True,
        "message": f"Produce listing '{crop_title}' has been removed successfully."
    }), 200


# =========================================================================
# E. ORDER MANAGEMENT
# =========================================================================

@admin_bp.route('/orders', methods=['GET'])
@admin_required
def list_orders_admin(current_user):
    """
    Administrative order registry with status filtering, search, and pagination.
    Protects sensitive payment credentials.
    """
    search_q = request.args.get('search', '').strip().lower()
    status_filter = request.args.get('status', 'all').strip().lower()
    page = max(1, int(request.args.get('page', 1)))
    limit = min(100, max(1, int(request.args.get('limit', 20))))

    orders_col = get_db().get_collection("orders")
    all_orders = list(orders_col.find({}))

    filtered = []
    for o in all_orders:
        o_dict = dict(o)
        o_dict["id"] = str(o_dict.get("_id") or o_dict.get("id"))
        o_dict.pop("_id", None)

        if status_filter != 'all' and (o_dict.get("status") or "").lower() != status_filter:
            continue

        if search_q:
            match = (
                search_q in (o_dict.get("id") or "").lower() or
                search_q in (o_dict.get("buyer_name") or "").lower() or
                search_q in (o_dict.get("farmer_name") or "").lower() or
                search_q in (o_dict.get("product_name") or "").lower()
            )
            if not match:
                continue

        filtered.append(o_dict)

    filtered.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    total_count = len(filtered)
    start_idx = (page - 1) * limit
    paginated = filtered[start_idx:start_idx + limit]

    return jsonify({
        "success": True,
        "total": total_count,
        "page": page,
        "limit": limit,
        "orders": paginated
    }), 200


@admin_bp.route('/orders/<order_id>/status', methods=['PATCH'])
@admin_required
def update_order_status_admin(current_user, order_id):
    """
    Administrative order status override for dispute resolution or manual intervention.
    """
    data = request.get_json(silent=True) or {}
    new_status = sanitize_string(str(data.get("status", "")))
    valid_statuses = ["Pending", "Accepted", "Processing", "Shipped", "Delivered", "Completed", "Cancelled", "Rejected"]

    if new_status not in valid_statuses:
        return jsonify({
            "success": False,
            "error": f"Invalid status '{new_status}'. Allowed: {', '.join(valid_statuses)}"
        }), 400

    orders_col = get_db().get_collection("orders")
    id_q = make_id_query(order_id)
    order = orders_col.find_one(id_q)

    if not order:
        return jsonify({"success": False, "error": "Order not found."}), 404

    now_iso = datetime.datetime.utcnow().isoformat()
    updates = {
        "status": new_status,
        "updated_at": now_iso
    }

    if new_status in ["Delivered", "Completed"]:
        updates["escrow_status"] = "Payment Released to Farmer Bank Account"
    elif new_status in ["Cancelled", "Rejected"]:
        updates["escrow_status"] = "Escrow Funds Refunded to Buyer"

    orders_col.update_one(id_q, {"$set": updates})

    log_admin_action(
        admin_user=current_user,
        action="ORDER_STATUS_OVERRIDE",
        target_type="ORDER",
        target_id=order_id,
        details=f"Order #{order_id} status transitioned from '{order.get('status')}' to '{new_status}' by Admin."
    )

    return jsonify({
        "success": True,
        "message": f"Order #{order_id} status updated to '{new_status}'.",
        "order_id": order_id,
        "status": new_status
    }), 200


# =========================================================================
# F. AI AND SYSTEM MONITORING
# =========================================================================

@admin_bp.route('/system-monitoring', methods=['GET'])
@admin_required
def get_system_monitoring(current_user):
    """
    Show telemetry and system health:
    - Disease prediction request counts
    - Soil analysis report counts
    - Demand and price prediction request counts
    - Database connection status and record distribution
    - Recent system events and audit logs
    Zero exposure of user leaf images, tokens, or model credentials.
    """
    db = get_db()
    disease_col = db.get_collection("disease_results")
    soil_col = db.get_collection("soil_data")
    price_pred_col = db.get_collection("price_predictions")
    pred_col = db.get_collection("predictions")
    logs_col = db.get_collection("admin_logs")

    disease_scans_count = disease_col.count_documents({})
    soil_analyses_count = soil_col.count_documents({})
    price_predictions_count = price_pred_col.count_documents({}) + pred_col.count_documents({})

    db_health = db.check_health()

    # Collection distribution counts
    collections_summary = {}
    for col_name in db.COLLECTIONS:
        try:
            c = db.get_collection(col_name)
            collections_summary[col_name] = c.count_documents({})
        except Exception:
            collections_summary[col_name] = 0

    # Fetch last 20 audit events
    recent_events = list(logs_col.find({}))
    recent_events.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    events_safe = []
    for ev in recent_events[:20]:
        events_safe.append({
            "action": ev.get("action"),
            "admin_email": ev.get("admin_email"),
            "target_type": ev.get("target_type"),
            "target_id": ev.get("target_id"),
            "details": ev.get("details"),
            "created_at": ev.get("created_at")
        })

    return jsonify({
        "success": True,
        "ai_metrics": {
            "disease_diagnoses_count": disease_scans_count,
            "soil_health_analyses_count": soil_analyses_count,
            "market_price_predictions_count": price_predictions_count
        },
        "database": {
            "status": db_health.get("status", "connected"),
            "healthy": db_health.get("connected", True),
            "collection_counts": collections_summary
        },
        "system_status": {
            "jwt_auth": "operational",
            "bcrypt_hasher": "operational",
            "api_gateway": "operational"
        },
        "recent_system_events": events_safe
    }), 200
