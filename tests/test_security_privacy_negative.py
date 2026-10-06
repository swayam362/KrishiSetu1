"""
KrushiSetu Security, Privacy, and Negative Testing Suite
Tests edge cases, invalid inputs, malicious payloads, role permission violations,
data minimization, and AI safety disclaimers.
"""

import os
import sys
import io
import json
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app import create_app
from backend.database import get_db
from backend.utils.security import hash_password, verify_password, generate_token, sanitize_string, sanitize_user
from backend.utils.location_privacy import mask_location_for_public, format_public_region
from backend.utils.upload_utils import is_allowed_image

class TestSecurityPrivacyAndNegativeCases(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

        # Seed test users into database
        db = get_db()
        users_col = db.get_collection("users")
        
        # Farmer
        self.farmer_id = "farmer_test_101"
        self.farmer_email = "farmer101@krushisetu.test"
        users_col.delete_one({"_id": self.farmer_id})
        users_col.insert_one({
            "_id": self.farmer_id,
            "id": self.farmer_id,
            "full_name": "Ramesh Patil",
            "email": self.farmer_email,
            "role": "farmer",
            "district": "Nashik",
            "state": "Maharashtra"
        })

        # Buyer
        self.buyer_id = "buyer_test_202"
        self.buyer_email = "buyer202@krushisetu.test"
        users_col.delete_one({"_id": self.buyer_id})
        users_col.insert_one({
            "_id": self.buyer_id,
            "id": self.buyer_id,
            "full_name": "Vikram Sethi",
            "email": self.buyer_email,
            "role": "buyer",
            "district": "Mumbai",
            "state": "Maharashtra"
        })

        # Tokens
        self.farmer_token = generate_token(user_id=self.farmer_id, role="farmer", email=self.farmer_email)
        self.buyer_token = generate_token(user_id=self.buyer_id, role="buyer", email=self.buyer_email)
        self.farmer_headers = {"Authorization": f"Bearer {self.farmer_token}"}
        self.buyer_headers = {"Authorization": f"Bearer {self.buyer_token}"}

    # =========================================================================
    # 1. SECURITY & PASSWORD HASHING
    # =========================================================================

    def test_password_hashing_and_verification(self):
        """Test bcrypt salted hashes with zero plaintext leakage."""
        pwd = "FarmerSecurePassword#2026"
        hashed = hash_password(pwd)
        self.assertNotEqual(pwd, hashed)
        self.assertTrue(hashed.startswith("$2b$") or hashed.startswith("$2a$"))
        self.assertTrue(verify_password(pwd, hashed))
        self.assertFalse(verify_password("WrongPassword123", hashed))

    def test_sanitize_user_strips_secrets(self):
        """Test user document sanitization strips password and password_hash."""
        user_doc = {
            "_id": "user_123",
            "full_name": "Ramesh Patil",
            "email": "ramesh@example.com",
            "password": "plaintext_pass",
            "password_hash": "$2b$12$eX4mP1eH4sH...",
            "role": "farmer"
        }
        cleaned = sanitize_user(user_doc)
        self.assertNotIn("password", cleaned)
        self.assertNotIn("password_hash", cleaned)
        self.assertNotIn("_id", cleaned)
        self.assertEqual(cleaned["id"], "user_123")

    def test_nosql_injection_sanitization(self):
        """Test sanitization of leading MongoDB query operators."""
        malicious_input = "$gt: ''"
        sanitized = sanitize_string(malicious_input)
        self.assertFalse(sanitized.startswith("$"))
        self.assertEqual(sanitized, "gt: ''")

    # =========================================================================
    # 2. AUTHENTICATION & ROLE AUTHORIZATION NEGATIVE TESTS
    # =========================================================================

    def test_unauthorized_api_access(self):
        """Test accessing protected farmer endpoint without token returns 401."""
        res = self.client.post("/api/products/", json={"crop_name": "Tomato", "quantity": 100})
        self.assertEqual(res.status_code, 401)
        data = res.get_json()
        self.assertFalse(data["success"])
        self.assertIn("Authentication token is missing", data["error"])

    def test_tampered_jwt_token(self):
        """Test corrupted token fails validation."""
        bad_headers = {"Authorization": "Bearer invalid.tampered.token"}
        res = self.client.post("/api/products/", headers=bad_headers, json={"crop_name": "Wheat"})
        self.assertEqual(res.status_code, 401)

    def test_wrong_user_role_authorization(self):
        """Test Buyer attempting to create a product (Farmer role only) returns 403."""
        res = self.client.post("/api/products/", headers=self.buyer_headers, json={
            "crop_name": "Wheat",
            "quantity": 100,
            "expected_price": 35.0
        })
        self.assertEqual(res.status_code, 403)
        data = res.get_json()
        self.assertFalse(data["success"])
        self.assertIn("Access denied", data["error"])

    # =========================================================================
    # 3. INPUT VALIDATION & BOUNDS CHECKING NEGATIVE TESTS
    # =========================================================================

    def test_create_product_missing_input(self):
        """Test product creation with missing crop name."""
        res = self.client.post("/api/products/", headers=self.farmer_headers, json={
            "quantity": 500,
            "expected_price": 25.0
        })
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertFalse(data["success"])
        self.assertIn("Crop name is required", data["error"])

    def test_create_product_negative_quantity(self):
        """Test product creation with negative or zero quantity fails."""
        res = self.client.post("/api/products/", headers=self.farmer_headers, json={
            "crop_name": "Tomato",
            "quantity": -50,
            "expected_price": 25.0
        })
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertIn("Quantity must be greater than zero", data["error"])

    def test_create_product_negative_price(self):
        """Test product creation with negative price fails."""
        res = self.client.post("/api/products/", headers=self.farmer_headers, json={
            "crop_name": "Tomato",
            "quantity": 500,
            "expected_price": -10.0
        })
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertIn("Expected price must be greater than zero", data["error"])

    # =========================================================================
    # 4. ORDER VALIDATION & STOCK NEGATIVE TESTS
    # =========================================================================

    def test_place_order_excess_quantity(self):
        """Test ordering more quantity than available stock fails."""
        # 1. First list a crop with 100 kg
        create_res = self.client.post("/api/products/", headers=self.farmer_headers, json={
            "crop_name": "Limited Organic Berries",
            "quantity": 100,
            "expected_price": 120.0,
            "category": "Fruits"
        })
        self.assertEqual(create_res.status_code, 201)
        prod_id = create_res.get_json()["product"]["id"]

        # 2. Buyer attempts to order 500 kg
        order_res = self.client.post("/api/orders/", headers=self.buyer_headers, json={
            "product_id": prod_id,
            "quantity": 500,
            "delivery_address": "Mumbai Market Depot"
        })
        self.assertEqual(order_res.status_code, 400)
        order_data = order_res.get_json()
        self.assertFalse(order_data["success"])
        self.assertIn("exceeds available stock", order_data["error"])

    def test_place_order_invalid_product_id(self):
        """Test placing order for nonexistent product ID returns 404."""
        order_res = self.client.post("/api/orders/", headers=self.buyer_headers, json={
            "product_id": "nonexistent_prod_9999",
            "quantity": 100,
            "delivery_address": "Pune Central Hub"
        })
        self.assertEqual(order_res.status_code, 404)

    # =========================================================================
    # 5. FILE UPLOAD SECURITY & NEGATIVE TESTS
    # =========================================================================

    def test_file_upload_disallowed_extension(self):
        """Test uploading executable or script is rejected."""
        class MockFile:
            filename = "malicious_script.php"
            mimetype = "application/x-php"
        
        is_valid, msg = is_allowed_image(MockFile())
        self.assertFalse(is_valid)
        self.assertIn("Disallowed file extension", msg)

    def test_file_upload_allowed_image_types(self):
        """Test valid JPG, PNG, WEBP extensions pass validation."""
        class MockImageFile:
            filename = "healthy_leaf.jpg"
            mimetype = "image/jpeg"
        
        is_valid, msg = is_allowed_image(MockImageFile())
        self.assertTrue(is_valid)

    # =========================================================================
    # 6. DATA PRIVACY & LOCATION MASKING AUDIT
    # =========================================================================

    def test_location_privacy_masking(self):
        """Test exact coordinates/streets are masked to district/region for public floor."""
        raw_address = "Survey No 45, Near Hanuman Temple, Pimpalgaon Village, Nashik, Maharashtra 422209"
        masked = mask_location_for_public(raw_address)
        self.assertEqual(masked["district"], "Nashik")
        self.assertEqual(masked["state"], "Maharashtra")
        self.assertNotIn("Survey No 45", masked["display_location"])
        self.assertNotIn("422209", masked["display_location"])

    # =========================================================================
    # 7. AI SAFETY & DISCLAIMERS AUDIT
    # =========================================================================

    def test_demand_forecast_contains_safety_disclaimer(self):
        """Test demand prediction explicitly disclaims certainty and declares forecast."""
        res = self.client.get("/api/ai/market-intelligence/forecast?crop=Tomato&location=Nashik&period=Next 7 days")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("disclaimer", data)
        self.assertIn("Forecast — not a guarantee.", data["disclaimer"])
        self.assertIn("expected_price_range", data)

    def test_smart_selling_net_realization_decision_support(self):
        """Test Smart Selling Net Realization calculation with transparent deductions."""
        res = self.client.post("/api/smart-selling/calculate", json={
            "crop": "Tomato",
            "quantity_kg": 500,
            "quality": "Grade A",
            "farmer_location": "Nashik"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("comparisons", data)
        self.assertIn("how_estimate_calculated", data)
        self.assertIn("decision_support_notice", data)
        self.assertIn("farmer retains 100% final authority", data["decision_support_notice"].lower())

        # Check top recommendation is determined by Net Realization, not highest nominal price
        comparisons = data["comparisons"]
        self.assertTrue(len(comparisons) >= 2)
        top_offer = comparisons[0]
        self.assertTrue(top_offer["is_recommended"])
        for other in comparisons[1:]:
            self.assertGreaterEqual(top_offer["net_realization"], other["net_realization"])

if __name__ == "__main__":
    unittest.main()
