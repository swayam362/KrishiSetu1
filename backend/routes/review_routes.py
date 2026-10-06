import uuid
import datetime
from flask import Blueprint, jsonify, request
from backend.database import get_db, make_id_query
from backend.utils.security import sanitize_string
from backend.utils.middleware import token_required, roles_required

review_bp = Blueprint('reviews', __name__, url_prefix='/api/reviews')

@review_bp.route('/', methods=['POST'])
@roles_required("buyer")
def submit_review(current_user):
    """
    Submit a verified review for a completed purchase.
    Anti-fraud check: Buyer must have an order for this product in 'Delivered' or 'Completed' status.
    """
    data = request.get_json(silent=True) or {}
    order_id = sanitize_string(str(data.get('order_id', '')))
    comment = sanitize_string(str(data.get('comment') or data.get('review_text') or ''), max_length=1500)

    try:
        rating = int(data.get('rating', 5))
        if rating < 1 or rating > 5:
            return jsonify({"success": False, "error": "Rating must be an integer between 1 and 5 stars."}), 400
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "Invalid rating format."}), 400

    if not order_id:
        return jsonify({"success": False, "error": "Order ID is required to verify legitimate purchase."}), 400

    if not comment:
        return jsonify({"success": False, "error": "Review feedback text cannot be empty."}), 400

    # Verify order exists and belongs to current buyer
    buyer_id = str(current_user["id"])
    orders_col = get_db().get_collection("orders")
    order = orders_col.find_one(make_id_query(order_id))

    if not order:
        return jsonify({"success": False, "error": "Associated order record not found."}), 404

    if str(order.get("buyer_id")) != buyer_id and current_user.get("role") != "admin":
        return jsonify({
            "success": False,
            "error": "Access denied. You can only review orders that you purchased."
        }), 403

    # Check that order is in Delivered or Completed state
    order_status = order.get("status")
    if order_status not in ["Delivered", "Completed"]:
        return jsonify({
            "success": False,
            "error": f"Reviews are only permitted for delivered or completed orders. Current order status is '{order_status}'."
        }), 400

    # Prevent duplicate reviews on the same order
    reviews_col = get_db().get_collection("reviews")
    existing_review = reviews_col.find_one({"order_id": order_id})
    if existing_review:
        return jsonify({
            "success": False,
            "error": "You have already submitted a verified review for this completed order."
        }), 409

    review_id = f"REV-{uuid.uuid4().hex[:10]}"
    now_iso = datetime.datetime.utcnow().isoformat()

    review_doc = {
        "_id": review_id,
        "id": review_id,
        "buyer_id": buyer_id,
        "buyer_name": current_user.get("business_name") or current_user.get("full_name", "Verified Buyer"),
        "farmer_id": str(order.get("farmer_id")),
        "farmer_name": order.get("farmer_name", "Farmer"),
        "product_id": str(order.get("product_id")),
        "product_name": order.get("product_name", "Farm Produce"),
        "order_id": order_id,
        "rating": rating,
        "comment": comment,
        "is_verified_purchase": True,
        "created_at": now_iso
    }

    reviews_col.insert_one(review_doc)

    return jsonify({
        "success": True,
        "message": "Verified purchase review submitted successfully.",
        "review": review_doc
    }), 201


@review_bp.route('/product/<product_id>', methods=['GET'])
def get_product_reviews(product_id):
    """Retrieve verified reviews and rating stats for a specific product."""
    reviews_col = get_db().get_collection("reviews")
    product_reviews = reviews_col.find({"product_id": str(product_id)})

    results = []
    total_rating = 0
    for r in product_reviews:
        r_dict = dict(r)
        r_dict["id"] = str(r_dict.get("_id") or r_dict.get("id"))
        r_dict.pop("_id", None)
        results.append(r_dict)
        total_rating += r_dict.get("rating", 5)

    avg_rating = round(total_rating / len(results), 1) if results else 5.0

    return jsonify({
        "success": True,
        "product_id": product_id,
        "count": len(results),
        "average_rating": avg_rating,
        "reviews": results
    }), 200


@review_bp.route('/farmer/<farmer_id>', methods=['GET'])
def get_farmer_reviews(farmer_id):
    """Retrieve verified reviews and reputation score for a farmer profile."""
    reviews_col = get_db().get_collection("reviews")
    farmer_reviews = reviews_col.find({"farmer_id": str(farmer_id)})

    results = []
    total_rating = 0
    for r in farmer_reviews:
        r_dict = dict(r)
        r_dict["id"] = str(r_dict.get("_id") or r_dict.get("id"))
        r_dict.pop("_id", None)
        results.append(r_dict)
        total_rating += r_dict.get("rating", 5)

    avg_rating = round(total_rating / len(results), 1) if results else 5.0

    return jsonify({
        "success": True,
        "farmer_id": farmer_id,
        "count": len(results),
        "average_rating": avg_rating,
        "reviews": results
    }), 200
