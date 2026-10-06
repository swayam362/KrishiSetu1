import os
import datetime
from flask import Blueprint, jsonify, request
from backend.database import get_db
from backend.utils.security import sanitize_string
from backend.utils.middleware import token_required, roles_required
from backend.utils.upload_utils import save_crop_image

product_bp = Blueprint('products', __name__, url_prefix='/api/products')

VALID_CATEGORIES = ["Grains", "Vegetables", "Fruits", "Pulses", "Oilseeds", "Spices"]
VALID_UNITS = ["kg", "Quintals", "Tonnes"]
VALID_GRADES = ["Grade A+", "Grade A", "Export Grade", "Grade B", "Standard"]
VALID_AVAILABILITY = ["Available", "Sold Out", "Reserved"]

# Curated realistic default crop images catalog
CROP_IMAGE_CATALOG = {
    "tomato": "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?auto=format&fit=crop&w=600&q=80",
    "tomatoes": "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?auto=format&fit=crop&w=600&q=80",
    "berry": "https://images.unsplash.com/photo-1519996529931-28324d5a630e?auto=format&fit=crop&w=600&q=80",
    "berries": "https://images.unsplash.com/photo-1519996529931-28324d5a630e?auto=format&fit=crop&w=600&q=80",
    "strawberry": "https://images.unsplash.com/photo-1519996529931-28324d5a630e?auto=format&fit=crop&w=600&q=80",
    "onion": "https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?auto=format&fit=crop&w=600&q=80",
    "onions": "https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?auto=format&fit=crop&w=600&q=80",
    "potato": "https://images.unsplash.com/photo-1518977676601-b53f82aba655?auto=format&fit=crop&w=600&q=80",
    "potatoes": "https://images.unsplash.com/photo-1518977676601-b53f82aba655?auto=format&fit=crop&w=600&q=80",
    "wheat": "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?auto=format&fit=crop&w=600&q=80",
    "rice": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=600&q=80",
    "basmati": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=600&q=80",
    "paddy": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=600&q=80",
    "orange": "https://images.unsplash.com/photo-1547514701-42782101795e?auto=format&fit=crop&w=600&q=80",
    "oranges": "https://images.unsplash.com/photo-1547514701-42782101795e?auto=format&fit=crop&w=600&q=80",
    "santra": "https://images.unsplash.com/photo-1547514701-42782101795e?auto=format&fit=crop&w=600&q=80",
    "mandarin": "https://images.unsplash.com/photo-1547514701-42782101795e?auto=format&fit=crop&w=600&q=80",
    "apple": "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?auto=format&fit=crop&w=600&q=80",
    "apples": "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?auto=format&fit=crop&w=600&q=80",
    "cotton": "https://images.unsplash.com/photo-1606041008023-472dfb5e530f?auto=format&fit=crop&w=600&q=80",
    "chilli": "https://images.unsplash.com/photo-1588252303782-cb80119abd6d?auto=format&fit=crop&w=600&q=80",
    "chili": "https://images.unsplash.com/photo-1588252303782-cb80119abd6d?auto=format&fit=crop&w=600&q=80",
    "mirchi": "https://images.unsplash.com/photo-1588252303782-cb80119abd6d?auto=format&fit=crop&w=600&q=80",
    "pepper": "https://images.unsplash.com/photo-1588252303782-cb80119abd6d?auto=format&fit=crop&w=600&q=80",
    "tur dal": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=600&q=80",
    "pulses": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=600&q=80",
    "dal": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=600&q=80",
    "soybean": "https://images.unsplash.com/photo-1599940824399-b87987ceb72a?auto=format&fit=crop&w=600&q=80",
    "mustard": "https://images.unsplash.com/photo-1508747703725-719777637510?auto=format&fit=crop&w=600&q=80",
    "banana": "https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?auto=format&fit=crop&w=600&q=80",
    "mango": "https://images.unsplash.com/photo-1553279768-865429fa0078?auto=format&fit=crop&w=600&q=80",
    "corn": "https://images.unsplash.com/photo-1551754655-cd27e38d2076?auto=format&fit=crop&w=600&q=80",
    "maize": "https://images.unsplash.com/photo-1551754655-cd27e38d2076?auto=format&fit=crop&w=600&q=80"
}

CATEGORY_DEFAULT_IMAGES = {
    "Vegetables": "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?auto=format&fit=crop&w=600&q=80",
    "Fruits": "https://images.unsplash.com/photo-1547514701-42782101795e?auto=format&fit=crop&w=600&q=80",
    "Grains": "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?auto=format&fit=crop&w=600&q=80",
    "Pulses": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=600&q=80",
    "Oilseeds": "https://images.unsplash.com/photo-1599940824399-b87987ceb72a?auto=format&fit=crop&w=600&q=80",
    "Spices": "https://images.unsplash.com/photo-1588252303782-cb80119abd6d?auto=format&fit=crop&w=600&q=80"
}

# Neutral agricultural fallback (not wheat)
NEUTRAL_AGRICULTURAL_IMAGE = "https://images.unsplash.com/photo-1500937386664-56d1dfef3854?auto=format&fit=crop&w=600&q=80"
DEFAULT_CROP_IMAGE = NEUTRAL_AGRICULTURAL_IMAGE

def get_crop_default_image(crop_name: str, category: str = "Grains") -> str:
    """Resolve crop-specific realistic photo based on crop name or category, or neutral fallback."""
    name_lower = (crop_name or "").lower()
    for key, img_url in CROP_IMAGE_CATALOG.items():
        if key in name_lower:
            return img_url
    if category in CATEGORY_DEFAULT_IMAGES:
        return CATEGORY_DEFAULT_IMAGES[category]
    return NEUTRAL_AGRICULTURAL_IMAGE

@product_bp.route('/', methods=['POST'])
@roles_required("farmer")
def create_product(current_user):
    """Create a new crop/produce listing. Only authenticated Farmers can create products."""
    data = request.get_json(silent=True) or {}

    crop_name = sanitize_string(str(data.get('crop_name') or data.get('name') or ''))
    category = sanitize_string(str(data.get('category', 'Grains')))
    unit = sanitize_string(str(data.get('unit', 'kg')))
    grade = sanitize_string(str(data.get('grade') or data.get('quality') or 'Grade A'))
    harvest_date = sanitize_string(str(data.get('harvest_date', datetime.date.today().isoformat())))
    description = sanitize_string(str(data.get('description', 'Fresh harvest direct from farm.')))
    organic = bool(data.get('organic', True))
    
    # Safe public location: District & State (protecting exact private address)
    user_state = current_user.get('state', 'Maharashtra')
    user_dist = current_user.get('district', 'Nashik')
    user_village = current_user.get('village', '')
    location = sanitize_string(str(data.get('location') or f"{user_dist}, {user_state}"))

    # Validate numbers
    try:
        quantity = float(data.get('quantity', 0))
        price_per_unit = float(data.get('expected_price') or data.get('price_per_unit') or data.get('price') or 0)
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "Quantity and Expected Price must be valid numbers."}), 400

    if not crop_name:
        return jsonify({"success": False, "error": "Crop name is required."}), 400

    if quantity <= 0:
        return jsonify({"success": False, "error": "Quantity must be greater than zero."}), 400

    if price_per_unit <= 0:
        return jsonify({"success": False, "error": "Expected price must be greater than zero."}), 400

    images = data.get('images', [])
    if not isinstance(images, list):
        images = [str(images)] if images else []
    
    # Prioritize explicitly uploaded or provided image
    raw_img = data.get('image_url')
    if raw_img and not images:
        images = [raw_img]
    elif images and not raw_img:
        raw_img = images[0]
        
    # If no image was uploaded, assign crop-specific default catalog image
    if not images or not images[0]:
        resolved_img = get_crop_default_image(crop_name, category)
        images = [resolved_img]
        raw_img = resolved_img

    import uuid
    prod_id = str(uuid.uuid4())
    product_doc = {
        "_id": prod_id,
        "id": prod_id,
        "farmer_id": str(current_user["id"]),
        "farmer_name": current_user.get("full_name", "Farmer"),
        "farmer_phone": current_user.get("phone", ""),
        "crop_name": crop_name,
        "name": crop_name,  # for compatibility
        "category": category if category in VALID_CATEGORIES else "Grains",
        "quantity": quantity,
        "unit": unit if unit in VALID_UNITS else "kg",
        "price_per_unit": price_per_unit,
        "price": price_per_unit,  # for compatibility
        "grade": grade if grade in VALID_GRADES else "Grade A",
        "harvest_date": harvest_date,
        "location": location,
        "district": user_dist,
        "state": user_state,
        "description": description,
        "images": images,
        "image_url": raw_img or images[0],  # for compatibility
        "organic": organic,
        "organic_certified": organic,
        "availability": "Available",
        "created_at": datetime.datetime.utcnow().isoformat(),
        "updated_at": datetime.datetime.utcnow().isoformat()
    }

    products_col = get_db().get_collection("products")
    products_col.insert_one(product_doc)

    return jsonify({
        "success": True,
        "message": f"Crop '{crop_name}' listed successfully on KrushiSetu Marketplace.",
        "product": product_doc
    }), 201


@product_bp.route('/', methods=['GET'])
def list_products():
    """
    Public marketplace feed with multi-parameter search, category,
    price, quantity, quality grade filters, and sorting.
    """
    search_q = request.args.get('search', '').strip().lower()
    category = request.args.get('category', '').strip()
    grade = request.args.get('grade', '').strip()
    location_q = request.args.get('location', '').strip().lower()
    sort_by = request.args.get('sort', 'newest').strip().lower()
    availability = request.args.get('availability', 'Available').strip()

    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    min_qty = request.args.get('min_qty')

    products_col = get_db().get_collection("products")
    all_products = products_col.find()

    # Seed initial items if collection is empty
    if not all_products:
        _seed_default_products(products_col)
        all_products = products_col.find()

    filtered = []
    for p in all_products:
        p_dict = dict(p)
        p_dict["id"] = str(p_dict.get("_id") or p_dict.get("id"))
        p_dict.pop("_id", None)
        p_dict.pop("farmer_phone", None) # Protect private phone on public list

        # Filter: Availability
        if availability and availability.lower() != 'all' and p_dict.get('availability', 'Available').lower() != availability.lower():
            continue

        # Filter: Category
        if category and category.lower() != 'all' and p_dict.get('category', '').lower() != category.lower():
            continue

        # Filter: Quality Grade
        if grade and grade.lower() != 'all' and p_dict.get('grade', '').lower() != grade.lower():
            continue

        # Filter: Search query (crop name, category, or location)
        if search_q:
            c_name = p_dict.get('crop_name', '').lower()
            c_cat = p_dict.get('category', '').lower()
            c_loc = p_dict.get('location', '').lower()
            c_farmer = p_dict.get('farmer_name', '').lower()
            if search_q not in c_name and search_q not in c_cat and search_q not in c_loc and search_q not in c_farmer:
                continue

        # Filter: Location query
        if location_q and location_q not in p_dict.get('location', '').lower() and location_q not in p_dict.get('district', '').lower():
            continue

        # Filter: Price range
        p_price = float(p_dict.get('price_per_unit', 0))
        if min_price:
            try:
                if p_price < float(min_price): continue
            except ValueError: pass
        if max_price:
            try:
                if p_price > float(max_price): continue
            except ValueError: pass

        # Filter: Min Quantity
        if min_qty:
            try:
                if float(p_dict.get('quantity', 0)) < float(min_qty): continue
            except ValueError: pass

        filtered.append(p_dict)

    # Sorting
    if sort_by == 'price_asc':
        filtered.sort(key=lambda x: float(x.get('price_per_unit', 0)))
    elif sort_by == 'price_desc':
        filtered.sort(key=lambda x: float(x.get('price_per_unit', 0)), reverse=True)
    elif sort_by == 'qty_desc':
        filtered.sort(key=lambda x: float(x.get('quantity', 0)), reverse=True)
    else: # newest
        filtered.sort(key=lambda x: x.get('created_at', ''), reverse=True)

    return jsonify({
        "success": True,
        "count": len(filtered),
        "products": filtered
    }), 200


from backend.database import get_db, make_id_query

# ... rest of file ...

@product_bp.route('/<product_id>', methods=['GET'])
def get_product_detail(product_id):
    """Retrieve detailed product view with safe farmer profile summary."""
    products_col = get_db().get_collection("products")
    product = products_col.find_one(make_id_query(product_id))
    
    if not product:
        return jsonify({"success": False, "error": "Product not found."}), 404

    p_dict = dict(product)
    p_dict["id"] = str(p_dict.get("_id") or p_dict.get("id"))
    p_dict.pop("_id", None)

    return jsonify({
        "success": True,
        "product": p_dict
    }), 200


@product_bp.route('/farmer/my-products', methods=['GET'])
@roles_required("farmer")
def get_my_products(current_user):
    """Retrieve products listed by the authenticated Farmer."""
    farmer_id = str(current_user["id"])
    products_col = get_db().get_collection("products")
    my_products = products_col.find({"farmer_id": farmer_id})

    results = []
    for p in my_products:
        p_dict = dict(p)
        p_dict["id"] = str(p_dict.get("_id") or p_dict.get("id"))
        p_dict.pop("_id", None)
        results.append(p_dict)

    return jsonify({
        "success": True,
        "count": len(results),
        "products": results
    }), 200


@product_bp.route('/<product_id>', methods=['PUT'])
@roles_required("farmer")
def update_product(current_user, product_id):
    """Update an existing product listing. Verifies that caller is the owner."""
    products_col = get_db().get_collection("products")
    id_q = make_id_query(product_id)
    existing = products_col.find_one(id_q)

    if not existing:
        return jsonify({"success": False, "error": "Product not found."}), 404

    # Strict ownership verification
    if str(existing.get("farmer_id")) != str(current_user["id"]) and current_user.get("role") != "admin":
        return jsonify({
            "success": False,
            "error": "Access denied. You can only edit your own produce listings."
        }), 403

    data = request.get_json(silent=True) or {}
    updates = {"updated_at": datetime.datetime.utcnow().isoformat()}

    if "crop_name" in data or "name" in data:
        name = sanitize_string(str(data.get("crop_name") or data.get("name")))
        updates["crop_name"] = name
        updates["name"] = name

    if "category" in data:
        cat = sanitize_string(str(data.get("category")))
        if cat in VALID_CATEGORIES:
            updates["category"] = cat

    if "grade" in data or "quality" in data:
        gr = sanitize_string(str(data.get("grade") or data.get("quality")))
        if gr in VALID_GRADES:
            updates["grade"] = gr

    if "quantity" in data:
        try:
            qty = float(data["quantity"])
            if qty > 0: updates["quantity"] = qty
        except (ValueError, TypeError): pass

    if "expected_price" in data or "price_per_unit" in data or "price" in data:
        try:
            p_val = float(data.get("expected_price") or data.get("price_per_unit") or data.get("price"))
            if p_val > 0:
                updates["price_per_unit"] = p_val
                updates["price"] = p_val
        except (ValueError, TypeError): pass

    if "description" in data:
        updates["description"] = sanitize_string(str(data["description"]))

    if "availability" in data:
        avail = sanitize_string(str(data["availability"]))
        if avail in VALID_AVAILABILITY:
            updates["availability"] = avail

    if "images" in data and isinstance(data["images"], list) and data["images"]:
        updates["images"] = data["images"]
        updates["image_url"] = data["images"][0]

    products_col.update_one(id_q, {"$set": updates})

    updated_doc = products_col.find_one(id_q)
    res_dict = dict(updated_doc)
    res_dict["id"] = str(res_dict.get("_id") or res_dict.get("id"))
    res_dict.pop("_id", None)

    return jsonify({
        "success": True,
        "message": "Product listing updated successfully.",
        "product": res_dict
    }), 200


@product_bp.route('/<product_id>', methods=['DELETE'])
@roles_required("farmer")
def delete_product(current_user, product_id):
    """Delete a product listing. Verifies that caller is the owner."""
    products_col = get_db().get_collection("products")
    id_q = make_id_query(product_id)
    existing = products_col.find_one(id_q)

    if not existing:
        return jsonify({"success": False, "error": "Product not found."}), 404

    # Strict ownership verification
    if str(existing.get("farmer_id")) != str(current_user["id"]) and current_user.get("role") != "admin":
        return jsonify({
            "success": False,
            "error": "Access denied. You can only delete your own produce listings."
        }), 403

    products_col.delete_one(id_q)

    return jsonify({
        "success": True,
        "message": "Product listing deleted successfully."
    }), 200


@product_bp.route('/upload-image', methods=['POST'])
@roles_required("farmer")
def upload_product_image(current_user):
    """Upload crop photo with safe UUID generation and format verification."""
    if 'image' not in request.files:
        return jsonify({"success": False, "error": "No image file provided in 'image' form field."}), 400

    file_storage = request.files['image']
    try:
        relative_url = save_crop_image(file_storage)
        return jsonify({
            "success": True,
            "image_url": relative_url,
            "message": "Crop image uploaded securely."
        }), 201
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception:
        return jsonify({"success": False, "error": "Failed to upload image. Please try again."}), 500


def _seed_default_products(products_col):
    """Seed initial realistic farm produce listings."""
    seed_data = [
        {
            "id": "prod_seed_1",
            "farmer_id": "farmer_seed_101",
            "farmer_name": "Ramesh Patil",
            "crop_name": "Organic Sharbati Wheat",
            "name": "Organic Sharbati Wheat",
            "category": "Grains",
            "quantity": 4500,
            "unit": "kg",
            "price_per_unit": 38.5,
            "price": 38.5,
            "grade": "Grade A+",
            "harvest_date": "2026-09-10",
            "location": "Nashik, Maharashtra",
            "district": "Nashik",
            "state": "Maharashtra",
            "description": "Premium Sharbati variety wheat. Grown organically without chemical pesticides. Moisture below 11%.",
            "images": ["https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?auto=format&fit=crop&w=600&q=80"],
            "image_url": "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?auto=format&fit=crop&w=600&q=80",
            "organic": True,
            "organic_certified": True,
            "availability": "Available",
            "created_at": "2026-09-20T10:00:00"
        },
        {
            "id": "prod_seed_2",
            "farmer_id": "farmer_seed_102",
            "farmer_name": "Suresh Deshmukh",
            "crop_name": "Fresh Red Onions (Nashik)",
            "name": "Fresh Red Onions (Nashik)",
            "category": "Vegetables",
            "quantity": 8000,
            "unit": "kg",
            "price_per_unit": 24.0,
            "price": 24.0,
            "grade": "Grade A",
            "harvest_date": "2026-09-18",
            "location": "Lasalgaon, Maharashtra",
            "district": "Nashik",
            "state": "Maharashtra",
            "description": "Export quality dried red onions. Well cured and sorted for long shelf life.",
            "images": ["https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?auto=format&fit=crop&w=600&q=80"],
            "image_url": "https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?auto=format&fit=crop&w=600&q=80",
            "organic": False,
            "organic_certified": False,
            "availability": "Available",
            "created_at": "2026-09-21T11:30:00"
        },
        {
            "id": "prod_seed_3",
            "farmer_id": "farmer_seed_103",
            "farmer_name": "Amol Shinde",
            "crop_name": "Nagpur Mandarin Oranges",
            "name": "Nagpur Mandarin Oranges",
            "category": "Fruits",
            "quantity": 3200,
            "unit": "kg",
            "price_per_unit": 62.0,
            "price": 62.0,
            "grade": "Export Grade",
            "harvest_date": "2026-09-20",
            "location": "Nagpur, Maharashtra",
            "district": "Nagpur",
            "state": "Maharashtra",
            "description": "Sweet juicy Nagpur Santra, direct from orchard. Handpicked and graded.",
            "images": ["https://images.unsplash.com/photo-1547514701-42782101795e?auto=format&fit=crop&w=600&q=80"],
            "image_url": "https://images.unsplash.com/photo-1547514701-42782101795e?auto=format&fit=crop&w=600&q=80",
            "organic": True,
            "organic_certified": True,
            "availability": "Available",
            "created_at": "2026-09-22T08:15:00"
        },
        {
            "id": "prod_seed_4",
            "farmer_id": "farmer_seed_104",
            "farmer_name": "Ganpat Yadav",
            "crop_name": "Desi Tur Dal (Pigeon Pea)",
            "name": "Desi Tur Dal (Pigeon Pea)",
            "category": "Pulses",
            "quantity": 2000,
            "unit": "kg",
            "price_per_unit": 115.0,
            "price": 115.0,
            "grade": "Grade A+",
            "harvest_date": "2026-08-30",
            "location": "Gulbarga, Karnataka",
            "district": "Gulbarga",
            "state": "Karnataka",
            "description": "Naturally grown unpolished desi tur dal. High protein and rich natural aroma.",
            "images": ["https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=600&q=80"],
            "image_url": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=600&q=80",
            "organic": True,
            "organic_certified": True,
            "availability": "Available",
            "created_at": "2026-09-22T14:45:00"
        },
        {
            "id": "prod_seed_5",
            "farmer_id": "farmer_seed_105",
            "farmer_name": "Sanjay Jagtap",
            "crop_name": "Organic Tomatoes (Hybrid Red)",
            "name": "Organic Tomatoes (Hybrid Red)",
            "category": "Vegetables",
            "quantity": 3500,
            "unit": "kg",
            "price_per_unit": 28.0,
            "price": 28.0,
            "grade": "Grade A+",
            "harvest_date": "2026-09-24",
            "location": "Pune, Maharashtra",
            "district": "Pune",
            "state": "Maharashtra",
            "description": "Firm, ripe vine-grown red tomatoes. Farm fresh with 8-day storage life.",
            "images": ["https://images.unsplash.com/photo-1592924357228-91a4daadcfea?auto=format&fit=crop&w=600&q=80"],
            "image_url": "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?auto=format&fit=crop&w=600&q=80",
            "organic": True,
            "organic_certified": True,
            "availability": "Available",
            "created_at": "2026-09-23T09:00:00"
        },
        {
            "id": "prod_seed_6",
            "farmer_id": "farmer_seed_106",
            "farmer_name": "Pooja Kadam",
            "crop_name": "Limited Organic Berries (Farm Fresh)",
            "name": "Limited Organic Berries (Farm Fresh)",
            "category": "Fruits",
            "quantity": 1200,
            "unit": "kg",
            "price_per_unit": 180.0,
            "price": 180.0,
            "grade": "Export Grade",
            "harvest_date": "2026-09-24",
            "location": "Mahabaleshwar, Maharashtra",
            "district": "Satara",
            "state": "Maharashtra",
            "description": "Handpicked fresh organic strawberries & mixed berries directly from hill-slopes.",
            "images": ["https://images.unsplash.com/photo-1519996529931-28324d5a630e?auto=format&fit=crop&w=600&q=80"],
            "image_url": "https://images.unsplash.com/photo-1519996529931-28324d5a630e?auto=format&fit=crop&w=600&q=80",
            "organic": True,
            "organic_certified": True,
            "availability": "Available",
            "created_at": "2026-09-23T11:00:00"
        },
        {
            "id": "prod_seed_7",
            "farmer_id": "farmer_seed_107",
            "farmer_name": "Vikram Singh",
            "crop_name": "Fresh Farm Potatoes (Kufri Jyoti)",
            "name": "Fresh Farm Potatoes (Kufri Jyoti)",
            "category": "Vegetables",
            "quantity": 10000,
            "unit": "kg",
            "price_per_unit": 19.5,
            "price": 19.5,
            "grade": "Grade A",
            "harvest_date": "2026-09-21",
            "location": "Indore, Madhya Pradesh",
            "district": "Indore",
            "state": "Madhya Pradesh",
            "description": "Medium-to-large clean table potatoes. High starch, excellent for cooking and processing.",
            "images": ["https://images.unsplash.com/photo-1518977676601-b53f82aba655?auto=format&fit=crop&w=600&q=80"],
            "image_url": "https://images.unsplash.com/photo-1518977676601-b53f82aba655?auto=format&fit=crop&w=600&q=80",
            "organic": False,
            "organic_certified": False,
            "availability": "Available",
            "created_at": "2026-09-23T14:30:00"
        },
        {
            "id": "prod_seed_8",
            "farmer_id": "farmer_seed_108",
            "farmer_name": "Harpreet Gill",
            "crop_name": "Super Basmati Rice (Aromatic)",
            "name": "Super Basmati Rice (Aromatic)",
            "category": "Grains",
            "quantity": 6000,
            "unit": "kg",
            "price_per_unit": 68.0,
            "price": 68.0,
            "grade": "Export Grade",
            "harvest_date": "2026-09-15",
            "location": "Karnal, Haryana",
            "district": "Karnal",
            "state": "Haryana",
            "description": "Extra long grain traditional Basmati. Naturally aged with delicate fragrant aroma.",
            "images": ["https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=600&q=80"],
            "image_url": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=600&q=80",
            "organic": True,
            "organic_certified": True,
            "availability": "Available",
            "created_at": "2026-09-23T16:00:00"
        }
    ]
    for item in seed_data:
        products_col.insert_one(item)
