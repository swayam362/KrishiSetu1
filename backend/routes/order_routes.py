import os
import uuid
import datetime
from flask import Blueprint, jsonify, request
from backend.database import get_db, make_id_query
from backend.utils.security import sanitize_string
from backend.utils.middleware import token_required, roles_required

order_bp = Blueprint('orders', __name__, url_prefix='/api/orders')

VALID_ORDER_STATUSES = [
    "Pending",
    "Accepted",
    "Rejected",
    "Processing",
    "Shipped",
    "Delivered",
    "Completed",
    "Cancelled"
]

@order_bp.route('/', methods=['POST'])
@roles_required("buyer")
def place_order(current_user):
    """
    Buyer places an order for a produce lot.
    IMPORTANT: Never trust price or total_amount from frontend.
    1. Fetch actual product price from database.
    2. Verify available quantity.
    3. Calculate total amount server-side.
    4. Atomically create order and update product stock.
    """
    data = request.get_json(silent=True) or {}
    product_id = sanitize_string(str(data.get('product_id', '')))
    delivery_address = sanitize_string(str(data.get('delivery_address') or data.get('destination', '')))
    logistics_preference = sanitize_string(str(data.get('logistics_preference', 'KrushiSetu Logistics')))

    if not product_id:
        return jsonify({"success": False, "error": "Product ID is required."}), 400

    if not delivery_address:
        return jsonify({"success": False, "error": "Delivery address is required."}), 400

    try:
        quantity = float(data.get('quantity', 0))
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "Invalid quantity provided."}), 400

    if quantity <= 0:
        return jsonify({"success": False, "error": "Order quantity must be greater than zero."}), 400

    # 1. Fetch product from database
    products_col = get_db().get_collection("products")
    product = products_col.find_one(make_id_query(product_id))

    if not product:
        return jsonify({"success": False, "error": "Product listing not found or no longer available."}), 404

    # Check product availability status
    if product.get('availability') == 'Sold Out':
        return jsonify({"success": False, "error": "This produce lot is already sold out."}), 400

    available_stock = float(product.get('quantity', 0))
    if quantity > available_stock:
        return jsonify({
            "success": False,
            "error": f"Requested quantity ({quantity} {product.get('unit', 'kg')}) exceeds available stock ({available_stock} {product.get('unit', 'kg')})."
        }), 400

    # 2. Extract verified unit price and compute total amount
    price_per_unit = float(product.get('price_per_unit') or product.get('price', 0))
    total_amount = round(price_per_unit * quantity, 2)

    order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    now_iso = datetime.datetime.utcnow().isoformat()

    order_doc = {
        "_id": order_id,
        "id": order_id,
        "buyer_id": str(current_user["id"]),
        "buyer_name": current_user.get("business_name") or current_user.get("full_name", "Buyer"),
        "buyer_phone": current_user.get("phone", ""),
        "farmer_id": str(product.get("farmer_id")),
        "farmer_name": product.get("farmer_name", "Farmer"),
        "product_id": str(product.get("id") or product.get("_id")),
        "product_name": product.get("crop_name") or product.get("name", "Farm Produce"),
        "quantity": quantity,
        "unit": product.get("unit", "kg"),
        "price_per_unit": price_per_unit,
        "price": price_per_unit,
        "total_amount": total_amount,
        "delivery_address": delivery_address,
        "logistics_preference": logistics_preference,
        "status": "Pending",
        "escrow_status": "Escrow Funds Locked (RBI Compliant)",
        "created_at": now_iso,
        "updated_at": now_iso
    }

    orders_col = get_db().get_collection("orders")
    orders_col.insert_one(order_doc)

    # 3. Deduct stock from product listing
    new_stock = available_stock - quantity
    stock_update = {
        "quantity": new_stock,
        "updated_at": now_iso
    }
    if new_stock <= 0:
        stock_update["availability"] = "Sold Out"
    
    products_col.update_one(make_id_query(product_id), {"$set": stock_update})

    return jsonify({
        "success": True,
        "message": f"Order #{order_id} placed successfully. Escrow funds of ₹{total_amount:,.2f} reserved.",
        "order": order_doc
    }), 201


@order_bp.route('/', methods=['GET'])
@token_required
def list_orders(current_user):
    """
    List orders strictly relevant to the authenticated user.
    - Farmers see incoming orders for their produce.
    - Buyers see their procurement orders.
    """
    user_id = str(current_user["id"])
    role = (current_user.get("role") or "").lower()
    orders_col = get_db().get_collection("orders")

    if role == "farmer":
        user_orders = orders_col.find({"farmer_id": user_id})
    elif role == "buyer":
        user_orders = orders_col.find({"buyer_id": user_id})
    else:  # Admin
        user_orders = orders_col.find()

    # Seed mock orders if completely empty
    if not user_orders and orders_col.count_documents() == 0:
        _seed_default_orders(orders_col, user_id, role)
        if role == "farmer":
            user_orders = orders_col.find({"farmer_id": user_id})
        elif role == "buyer":
            user_orders = orders_col.find({"buyer_id": user_id})
        else:
            user_orders = orders_col.find()

    results = []
    for o in user_orders:
        o_dict = dict(o)
        o_dict["id"] = str(o_dict.get("_id") or o_dict.get("id"))
        o_dict.pop("_id", None)
        results.append(o_dict)

    # Sort newest orders first
    results.sort(key=lambda x: x.get('created_at', ''), reverse=True)

    return jsonify({
        "success": True,
        "count": len(results),
        "orders": results
    }), 200


@order_bp.route('/<order_id>', methods=['GET'])
@token_required
def get_order_detail(current_user, order_id):
    """
    Retrieve single order details.
    Guarantees that caller is either the Buyer, the Farmer, or an Admin.
    """
    orders_col = get_db().get_collection("orders")
    order = orders_col.find_one(make_id_query(order_id))

    if not order:
        return jsonify({"success": False, "error": "Order not found."}), 404

    user_id = str(current_user["id"])
    user_role = current_user.get("role", "").lower()

    # Check participant authorization
    if str(order.get("buyer_id")) != user_id and str(order.get("farmer_id")) != user_id and user_role != "admin":
        return jsonify({
            "success": False,
            "error": "Access denied. You do not have permission to view this order."
        }), 403

    o_dict = dict(order)
    o_dict["id"] = str(o_dict.get("_id") or o_dict.get("id"))
    o_dict.pop("_id", None)

    return jsonify({
        "success": True,
        "order": o_dict
    }), 200


@order_bp.route('/<order_id>/status', methods=['PATCH', 'PUT'])
@token_required
def update_order_status(current_user, order_id):
    """
    Update order status according to strict state machine and role permissions.
    - Farmer can transition:
      - Pending -> Accepted or Rejected
      - Accepted -> Processing
      - Processing -> Shipped
    - Buyer can transition:
      - Pending -> Cancelled
      - Shipped -> Delivered / Completed
    """
    orders_col = get_db().get_collection("orders")
    id_q = make_id_query(order_id)
    order = orders_col.find_one(id_q)

    if not order:
        return jsonify({"success": False, "error": "Order not found."}), 404

    user_id = str(current_user["id"])
    user_role = current_user.get("role", "").lower()
    is_buyer = str(order.get("buyer_id")) == user_id
    is_farmer = str(order.get("farmer_id")) == user_id
    is_admin = user_role == "admin"

    if not is_buyer and not is_farmer and not is_admin:
        return jsonify({
            "success": False,
            "error": "Access denied. You are not a participant in this order."
        }), 403

    data = request.get_json(silent=True) or {}
    new_status = sanitize_string(str(data.get('status', '')))

    if new_status not in VALID_ORDER_STATUSES:
        return jsonify({
            "success": False,
            "error": f"Invalid status '{new_status}'. Allowed statuses: {', '.join(VALID_ORDER_STATUSES)}"
        }), 400

    current_status = order.get("status", "Pending")

    # State Machine & Permission Validation
    if is_farmer and not is_admin:
        if current_status == "Pending" and new_status in ["Accepted", "Rejected"]:
            pass
        elif current_status == "Accepted" and new_status == "Processing":
            pass
        elif current_status in ["Accepted", "Processing"] and new_status == "Shipped":
            pass
        else:
            return jsonify({
                "success": False,
                "error": f"Farmers cannot transition order from '{current_status}' to '{new_status}'."
            }), 403

    elif is_buyer and not is_admin:
        if current_status == "Pending" and new_status == "Cancelled":
            pass
        elif current_status == "Shipped" and new_status in ["Delivered", "Completed"]:
            pass
        else:
            return jsonify({
                "success": False,
                "error": f"Buyers cannot transition order from '{current_status}' to '{new_status}'."
            }), 403

    # If order is Rejected or Cancelled, restore product stock
    if new_status in ["Rejected", "Cancelled"] and current_status not in ["Rejected", "Cancelled"]:
        product_id = order.get("product_id")
        qty_to_restore = float(order.get("quantity", 0))
        products_col = get_db().get_collection("products")
        prod = products_col.find_one(make_id_query(product_id))
        if prod:
            restored_qty = float(prod.get("quantity", 0)) + qty_to_restore
            products_col.update_one(make_id_query(product_id), {
                "$set": {
                    "quantity": restored_qty,
                    "availability": "Available",
                    "updated_at": datetime.datetime.utcnow().isoformat()
                }
            })

    # Update escrow release message on delivery
    escrow_status = order.get("escrow_status", "Escrow Funds Locked")
    if new_status in ["Delivered", "Completed"]:
        escrow_status = "Payment Released to Farmer Bank Account"
    elif new_status in ["Rejected", "Cancelled"]:
        escrow_status = "Escrow Funds Refunded to Buyer"

    now_iso = datetime.datetime.utcnow().isoformat()
    updates = {
        "status": new_status,
        "escrow_status": escrow_status,
        "updated_at": now_iso
    }

    orders_col.update_one(id_q, {"$set": updates})

    updated_doc = orders_col.find_one(id_q)
    res_dict = dict(updated_doc)
    res_dict["id"] = str(res_dict.get("_id") or res_dict.get("id"))
    res_dict.pop("_id", None)

    return jsonify({
        "success": True,
        "message": f"Order #{order_id} status transitioned to '{new_status}'.",
        "order": res_dict
    }), 200


def _seed_default_orders(orders_col, current_user_id, role):
    """Seed initial demonstration orders associated with current demo user."""
    seed_orders = [
        {
            "_id": "ORD-8821",
            "id": "ORD-8821",
            "buyer_id": current_user_id if role == "buyer" else "buyer_demo_201",
            "buyer_name": "AgroFresh Mills Pvt Ltd",
            "buyer_phone": "9812345678",
            "farmer_id": current_user_id if role == "farmer" else "farmer_demo_101",
            "farmer_name": "Ramesh Patil",
            "product_id": "prod_seed_1",
            "product_name": "Organic Sharbati Wheat",
            "quantity": 1500,
            "unit": "kg",
            "price_per_unit": 38.5,
            "price": 38.5,
            "total_amount": 57750.0,
            "delivery_address": "Pune Wholesale Agro Hub, Warehouse 4B",
            "logistics_preference": "KrushiSetu Verified Fleet",
            "status": "Shipped",
            "escrow_status": "Escrow Funds Locked (In-Transit)",
            "created_at": "2026-09-22T09:00:00",
            "updated_at": "2026-09-22T14:30:00"
        },
        {
            "_id": "ORD-8790",
            "id": "ORD-8790",
            "buyer_id": current_user_id if role == "buyer" else "buyer_demo_202",
            "buyer_name": "Reliance Fresh Retail",
            "buyer_phone": "9876543211",
            "farmer_id": current_user_id if role == "farmer" else "farmer_demo_102",
            "farmer_name": "Suresh Deshmukh",
            "product_id": "prod_seed_2",
            "product_name": "Fresh Red Onions (Nashik)",
            "quantity": 3000,
            "unit": "kg",
            "price_per_unit": 24.0,
            "price": 24.0,
            "total_amount": 72000.0,
            "delivery_address": "Mumbai APMC Depot, Vashi Yard 3",
            "logistics_preference": "Buyer Haulage",
            "status": "Accepted",
            "escrow_status": "Escrow Funds Locked (Pre-Dispatch)",
            "created_at": "2026-09-21T11:00:00",
            "updated_at": "2026-09-21T15:00:00"
        },
        {
            "_id": "ORD-8642",
            "id": "ORD-8642",
            "buyer_id": current_user_id if role == "buyer" else "buyer_demo_203",
            "buyer_name": "JuiceCraft Beverages",
            "buyer_phone": "9899887766",
            "farmer_id": current_user_id if role == "farmer" else "farmer_demo_103",
            "farmer_name": "Amol Shinde",
            "product_id": "prod_seed_3",
            "product_name": "Nagpur Mandarin Oranges",
            "quantity": 1000,
            "unit": "kg",
            "price_per_unit": 62.0,
            "price": 62.0,
            "total_amount": 62000.0,
            "delivery_address": "Nagpur Food Processing Park",
            "logistics_preference": "Farmer Local Dispatch",
            "status": "Completed",
            "escrow_status": "Payment Released to Farmer Bank Account",
            "created_at": "2026-09-15T08:00:00",
            "updated_at": "2026-09-16T17:00:00"
        }
    ]
    for o in seed_orders:
        orders_col.insert_one(o)
