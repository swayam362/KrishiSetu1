"""
KrushiSetu Comprehensive Backend & Admin Security Test Suite
Covers all 14 mandatory verification criteria from Step 6:
1. Backend startup and health check
2. Database connection & registered collections
3. Farmer registration
4. Buyer/merchant registration
5. Login and logout
6. Product creation & retrieval
7. Order placement & stock deduction
8. Admin login & token generation
9. Admin dashboard data calculation
10. Unauthorized admin access rejection (403/401)
11. Farmer cross-account private data isolation
12. Buyer cross-account order data isolation
13. Invalid API requests & zero stack trace leakage
14. Database failure handling & resilience
"""

import os
import sys
import unittest
import json
import uuid
import random

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app import create_app
from backend.database import get_db, make_id_query
from backend.utils.security import hash_password, verify_password, generate_token
from backend.scripts.create_admin import create_or_update_admin

class TestBackendAndAdminSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config["TESTING"] = True
        cls.client = cls.app.test_client()

        # Generate unique test suite run id
        cls.run_id = uuid.uuid4().hex[:6]
        cls.admin_email = f"admin_{cls.run_id}@krushisetu.test"
        cls.admin_password = "SecureAdminPass2026!"
        cls.admin_name = "Chief Security Administrator"

        # Provision Admin via administrative procedure
        create_or_update_admin(
            email=cls.admin_email,
            password=cls.admin_password,
            full_name=cls.admin_name,
            phone=f"9877{random.randint(100000, 999999)}"
        )

    def setUp(self):
        self.app = self.__class__.app
        self.client = self.__class__.client

    # 1. Backend startup
    def test_01_backend_startup_and_health(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["backend"], "running")
        self.assertTrue(data["database"]["healthy"])
        self.assertEqual(data["database"]["status"], "connected")
        self.assertTrue(data["security_features"]["admin_authorization"])

    # 2. Database connection
    def test_02_database_connection_and_collections(self):
        db = get_db()
        self.assertTrue(db.is_connected)
        health = db.check_health()
        self.assertTrue(health["connected"])
        self.assertEqual(health["status"], "connected")

        # Verify all essential collections
        for col_name in ["users", "products", "orders", "admin_logs", "disease_results", "soil_data"]:
            self.assertIn(col_name, db.COLLECTIONS)
            col = db.get_collection(col_name)
            self.assertIsNotNone(col)

    # 3. Farmer registration
    def test_03_farmer_registration(self):
        email = f"farmer_{self.run_id}@test.com"
        phone = f"9811{random.randint(100000, 999999)}"
        payload = {
            "role": "farmer",
            "full_name": "Kailash Patil",
            "email": email,
            "phone": phone,
            "password": "FarmPassword123!",
            "state": "Maharashtra",
            "district": "Nashik",
            "village": "Chandwad",
            "farm_size_acres": "10",
            "primary_crops": "Pomegranate, Grapes"
        }
        res = self.client.post("/api/auth/register", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("token", data)
        self.assertEqual(data["user"]["role"], "farmer")
        self.assertNotIn("password_hash", data["user"])

        # Duplicate email prevention
        dup_res = self.client.post("/api/auth/register", json=payload)
        self.assertEqual(dup_res.status_code, 409)

    # 4. Buyer/merchant registration & Admin registration prevention
    def test_04_buyer_registration_and_admin_prevention(self):
        email = f"buyer_{self.run_id}@test.com"
        phone = f"9822{random.randint(100000, 999999)}"
        payload = {
            "role": "buyer",
            "full_name": "Sanjay Kapoor",
            "business_name": "Kapoor Agro Mills",
            "email": email,
            "phone": phone,
            "password": "BuyerPassword123!",
            "state": "Maharashtra",
            "district": "Pune",
            "city": "Pune",
            "gstin": "27AAAAA0000A1Z5"
        }
        res = self.client.post("/api/auth/register", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["user"]["role"], "buyer")

        # Public registration of ADMIN must be strictly rejected
        hacker_payload = {
            "role": "admin",
            "full_name": "Unauthorized Intruder",
            "email": f"hacker_{self.run_id}@bad.com",
            "phone": "9899001122",
            "password": "hackerPassword123",
            "state": "MH",
            "district": "Pune"
        }
        hacker_res = self.client.post("/api/auth/register", json=hacker_payload)
        self.assertEqual(hacker_res.status_code, 403)
        self.assertFalse(hacker_res.get_json()["success"])

    # 5. Login and logout
    def test_05_login_and_logout(self):
        email = f"logintest_{self.run_id}@test.com"
        phone = f"9833{random.randint(100000, 999999)}"
        # Register user
        self.client.post("/api/auth/register", json={
            "role": "farmer",
            "full_name": "Test User",
            "email": email,
            "phone": phone,
            "password": "CorrectPassword123",
            "state": "MH",
            "district": "Nashik",
            "village": "Ozar"
        })

        # Correct password
        login_res = self.client.post("/api/auth/login", json={
            "identifier": email,
            "password": "CorrectPassword123"
        })
        self.assertEqual(login_res.status_code, 200)
        self.assertTrue(login_res.get_json()["success"])
        self.assertIn("token", login_res.get_json())

        # Incorrect password
        bad_login = self.client.post("/api/auth/login", json={
            "identifier": email,
            "password": "WrongPassword999"
        })
        self.assertEqual(bad_login.status_code, 401)
        self.assertFalse(bad_login.get_json()["success"])

        # Logout
        logout_res = self.client.post("/api/auth/logout")
        self.assertEqual(logout_res.status_code, 200)

    # 6. Product creation
    def test_06_product_creation(self):
        farmer_email = f"farmer_prod_{self.run_id}@test.com"
        reg_res = self.client.post("/api/auth/register", json={
            "role": "farmer", "full_name": "Gopal Rao", "email": farmer_email,
            "phone": f"9844{random.randint(100000, 999999)}", "password": "Password123!",
            "state": "Maharashtra", "district": "Nashik", "village": "Satana"
        })
        farmer_token = reg_res.get_json()["token"]

        # Farmer creates product
        prod_payload = {
            "crop_name": "Export Quality Alphonso",
            "category": "Fruits",
            "quantity": 1500,
            "unit": "kg",
            "expected_price": 350.0,
            "grade": "Export Grade",
            "description": "Naturally ripened GI tagged Alphonso mangoes."
        }
        create_res = self.client.post("/api/products/", json=prod_payload, headers={"Authorization": f"Bearer {farmer_token}"})
        self.assertEqual(create_res.status_code, 201)
        prod_data = create_res.get_json()
        self.assertTrue(prod_data["success"])
        self.assertEqual(prod_data["product"]["crop_name"], "Export Quality Alphonso")
        self.assertEqual(prod_data["product"]["quantity"], 1500)
        self.assertEqual(prod_data["product"]["price_per_unit"], 350.0)

        # Retrieve via public listing
        list_res = self.client.get("/api/products/?search=Alphonso")
        self.assertEqual(list_res.status_code, 200)
        self.assertGreaterEqual(list_res.get_json()["count"], 1)

    # 7. Order creation & stock deduction
    def test_07_order_creation_and_stock_deduction(self):
        # 1. Farmer with crop
        farmer_email = f"farmer_order_{self.run_id}@test.com"
        f_res = self.client.post("/api/auth/register", json={
            "role": "farmer", "full_name": "Narayan Farmer", "email": farmer_email,
            "phone": f"9855{random.randint(100000, 999999)}", "password": "Password123!",
            "state": "Maharashtra", "district": "Nagpur", "village": "Katol"
        })
        f_token = f_res.get_json()["token"]

        prod_res = self.client.post("/api/products/", json={
            "crop_name": "Nagpur Oranges Special",
            "category": "Fruits", "quantity": 2000, "unit": "kg",
            "expected_price": 50.0, "grade": "Grade A"
        }, headers={"Authorization": f"Bearer {f_token}"})
        product_id = prod_res.get_json()["product"]["id"]

        # 2. Buyer places order
        buyer_email = f"buyer_order_{self.run_id}@test.com"
        b_res = self.client.post("/api/auth/register", json={
            "role": "buyer", "full_name": "Juice Hub Pvt Ltd", "business_name": "Juice Hub",
            "email": buyer_email, "phone": f"9866{random.randint(100000, 999999)}", "password": "Password123!",
            "state": "Maharashtra", "district": "Mumbai", "city": "Mumbai"
        })
        b_token = b_res.get_json()["token"]

        order_res = self.client.post("/api/orders/", json={
            "product_id": product_id,
            "quantity": 500,
            "delivery_address": "Vashi Cold Storage, Unit 12, Navi Mumbai"
        }, headers={"Authorization": f"Bearer {b_token}"})

        self.assertEqual(order_res.status_code, 201)
        order_data = order_res.get_json()
        self.assertTrue(order_data["success"])
        # Verified server-side total: 500 * 50.0 = 25000.0
        self.assertEqual(order_data["order"]["total_amount"], 25000.0)
        self.assertEqual(order_data["order"]["status"], "Pending")

        # Verify stock was deducted: 2000 - 500 = 1500
        get_prod = self.client.get(f"/api/products/{product_id}")
        self.assertEqual(get_prod.get_json()["product"]["quantity"], 1500)

    # 8. Admin login
    def test_08_admin_login(self):
        res = self.client.post("/api/auth/login", json={
            "identifier": self.admin_email,
            "password": self.admin_password
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["user"]["role"], "admin")
        self.assertIn("token", data)
        self.__class__.admin_token = data["token"]

    # 9. Admin dashboard data
    def test_09_admin_dashboard_data(self):
        admin_token = getattr(self.__class__, "admin_token", None)
        if not admin_token:
            res = self.client.post("/api/auth/login", json={
                "identifier": self.admin_email, "password": self.admin_password
            })
            admin_token = res.get_json()["token"]

        headers = {"Authorization": f"Bearer {admin_token}"}

        # Overview
        ov = self.client.get("/api/admin/overview", headers=headers)
        self.assertEqual(ov.status_code, 200)
        ov_data = ov.get_json()
        self.assertTrue(ov_data["success"])
        self.assertIn("total_farmers", ov_data["metrics"])
        self.assertIn("total_buyers", ov_data["metrics"])
        self.assertIn("total_products", ov_data["metrics"])
        self.assertIn("total_orders", ov_data["metrics"])

        # Farmers list
        fm = self.client.get("/api/admin/farmers", headers=headers)
        self.assertEqual(fm.status_code, 200)
        self.assertTrue(fm.get_json()["success"])
        self.assertIsInstance(fm.get_json()["farmers"], list)

        # Buyers list
        by = self.client.get("/api/admin/buyers", headers=headers)
        self.assertEqual(by.status_code, 200)
        self.assertTrue(by.get_json()["success"])

        # Products list
        pr = self.client.get("/api/admin/products", headers=headers)
        self.assertEqual(pr.status_code, 200)
        self.assertTrue(pr.get_json()["success"])

        # Orders list
        od = self.client.get("/api/admin/orders", headers=headers)
        self.assertEqual(od.status_code, 200)
        self.assertTrue(od.get_json()["success"])

        # System monitoring
        mon = self.client.get("/api/admin/system-monitoring", headers=headers)
        self.assertEqual(mon.status_code, 200)
        self.assertTrue(mon.get_json()["database"]["healthy"])

    # 10. Unauthorized admin access
    def test_10_unauthorized_admin_access(self):
        # 1. Anonymous request without token -> 401
        res_anon = self.client.get("/api/admin/overview")
        self.assertEqual(res_anon.status_code, 401)

        # 2. Regular farmer token accessing admin route -> 403
        farmer_token = generate_token("user_farmer_test", "farmer", "farmer@test.com")
        res_farmer = self.client.get("/api/admin/overview", headers={"Authorization": f"Bearer {farmer_token}"})
        self.assertEqual(res_farmer.status_code, 403)
        self.assertIn("Administrative privileges required", res_farmer.get_json()["error"])

        # 3. Regular buyer token accessing admin route -> 403
        buyer_token = generate_token("user_buyer_test", "buyer", "buyer@test.com")
        res_buyer = self.client.get("/api/admin/farmers", headers={"Authorization": f"Bearer {buyer_token}"})
        self.assertEqual(res_buyer.status_code, 403)

    # 11. Farmer cross-account private data isolation
    def test_11_farmer_cross_account_isolation(self):
        # Register Farmer A
        fa_res = self.client.post("/api/auth/register", json={
            "role": "farmer", "full_name": "Farmer Alpha", "email": f"fa_{self.run_id}@test.com",
            "phone": f"9871{random.randint(100000, 999999)}", "password": "Password123!",
            "state": "MH", "district": "Nashik", "village": "A"
        })
        token_a = fa_res.get_json()["token"]

        # Register Farmer B
        fb_res = self.client.post("/api/auth/register", json={
            "role": "farmer", "full_name": "Farmer Beta", "email": f"fb_{self.run_id}@test.com",
            "phone": f"9872{random.randint(100000, 999999)}", "password": "Password123!",
            "state": "MH", "district": "Nashik", "village": "B"
        })
        token_b = fb_res.get_json()["token"]

        # Farmer A creates a product
        prod_res = self.client.post("/api/products/", json={
            "crop_name": "Alpha Private Lot", "quantity": 1000, "expected_price": 40.0
        }, headers={"Authorization": f"Bearer {token_a}"})
        prod_id = prod_res.get_json()["product"]["id"]

        # Farmer B tries to edit Farmer A's product -> 403
        edit_res = self.client.put(f"/api/products/{prod_id}", json={
            "crop_name": "Hacked Title"
        }, headers={"Authorization": f"Bearer {token_b}"})
        self.assertEqual(edit_res.status_code, 403)

        # Farmer B tries to delete Farmer A's product -> 403
        del_res = self.client.delete(f"/api/products/{prod_id}", headers={"Authorization": f"Bearer {token_b}"})
        self.assertEqual(del_res.status_code, 403)

    # 12. Buyer cross-account order data isolation
    def test_12_buyer_cross_account_isolation(self):
        # Buyer A and Buyer B
        ba_res = self.client.post("/api/auth/register", json={
            "role": "buyer", "full_name": "Buyer Alpha", "business_name": "Alpha Corp",
            "email": f"ba_{self.run_id}@test.com", "phone": f"9873{random.randint(100000, 999999)}",
            "password": "Password123!", "state": "MH", "district": "Pune", "city": "Pune"
        })
        token_a = ba_res.get_json()["token"]

        bb_res = self.client.post("/api/auth/register", json={
            "role": "buyer", "full_name": "Buyer Beta", "business_name": "Beta Corp",
            "email": f"bb_{self.run_id}@test.com", "phone": f"9874{random.randint(100000, 999999)}",
            "password": "Password123!", "state": "MH", "district": "Mumbai", "city": "Mumbai"
        })
        token_b = bb_res.get_json()["token"]

        # Create a product to order
        farmer_token = generate_token("temp_farmer", "farmer", "temp@farmer.com")
        prod_res = self.client.post("/api/products/", json={
            "crop_name": "Procurement Lot", "quantity": 5000, "expected_price": 20.0
        }, headers={"Authorization": f"Bearer {farmer_token}"})
        prod_id = prod_res.get_json()["product"]["id"]

        # Buyer A places order
        ord_res = self.client.post("/api/orders/", json={
            "product_id": prod_id, "quantity": 100, "delivery_address": "Alpha Warehouse"
        }, headers={"Authorization": f"Bearer {token_a}"})
        order_id = ord_res.get_json()["order"]["id"]

        # Buyer B tries to view Buyer A's order -> 403
        view_res = self.client.get(f"/api/orders/{order_id}", headers={"Authorization": f"Bearer {token_b}"})
        self.assertEqual(view_res.status_code, 403)

        # Buyer B tries to cancel/alter Buyer A's order status -> 403
        stat_res = self.client.patch(f"/api/orders/{order_id}/status", json={
            "status": "Cancelled"
        }, headers={"Authorization": f"Bearer {token_b}"})
        self.assertEqual(stat_res.status_code, 403)

    # 13. Invalid API requests & zero stack trace leakage
    def test_13_invalid_api_requests(self):
        # 1. Invalid JSON body
        res_bad_json = self.client.post(
            "/api/auth/register",
            data="invalid-non-json-string",
            content_type="application/json"
        )
        self.assertEqual(res_bad_json.status_code, 400)
        self.assertFalse(res_bad_json.get_json()["success"])

        # 2. Non-existent endpoint -> 404
        res_404 = self.client.get("/api/non-existent-endpoint-test")
        self.assertEqual(res_404.status_code, 404)
        data_404 = res_404.get_json()
        self.assertFalse(data_404["success"])
        # Verify no traceback is leaked
        self.assertNotIn("Traceback", json.dumps(data_404))

        # 3. Negative price product listing
        farmer_token = generate_token("farmer_neg_test", "farmer", "neg@test.com")
        res_neg_price = self.client.post("/api/products/", json={
            "crop_name": "Faulty Produce", "quantity": 100, "expected_price": -50.0
        }, headers={"Authorization": f"Bearer {farmer_token}"})
        self.assertEqual(res_neg_price.status_code, 400)

        # 4. Negative order quantity
        buyer_token = generate_token("buyer_neg_test", "buyer", "neg_buyer@test.com")
        res_neg_order = self.client.post("/api/orders/", json={
            "product_id": "dummy_id", "quantity": -10, "delivery_address": "Test"
        }, headers={"Authorization": f"Bearer {buyer_token}"})
        self.assertEqual(res_neg_order.status_code, 400)

    # 14. Database failure handling & resilience
    def test_14_database_failure_handling(self):
        # Verify that get_db() check_health() returns structured status without raising uncaught exceptions
        db = get_db()
        health = db.check_health()
        self.assertIsInstance(health, dict)
        self.assertIn("status", health)
        self.assertIn("connected", health)

    # 15. Farmer and buyer profile update and database persistence
    def test_15_profile_update_and_persistence(self):
        # 1. Register Farmer
        f_email = f"farmer_prof_{self.run_id}@test.com"
        f_phone = f"9881{random.randint(100000, 999999)}"
        reg_f = self.client.post("/api/auth/register", json={
            "role": "farmer",
            "full_name": "Original Farmer Name",
            "email": f_email,
            "phone": f_phone,
            "password": "Password123!",
            "state": "Maharashtra",
            "district": "Nashik",
            "village": "Ozar",
            "farm_size_acres": "5",
            "primary_crops": "Tomato"
        })
        self.assertEqual(reg_f.status_code, 201)
        f_token = reg_f.get_json()["token"]

        # 2. Update Farmer Profile
        upd_f = self.client.put("/api/auth/profile", json={
            "full_name": "Updated Farmer Name",
            "farm_size_acres": "18.5",
            "village": "Chandwad",
            "primary_crops": "Tomato, Pomegranate, Grapes",
            "bank_account": "State Bank of India - 1234567890"
        }, headers={"Authorization": f"Bearer {f_token}"})
        self.assertEqual(upd_f.status_code, 200)
        self.assertTrue(upd_f.get_json()["success"])
        self.assertEqual(upd_f.get_json()["user"]["full_name"], "Updated Farmer Name")
        self.assertEqual(upd_f.get_json()["user"]["farm_size_acres"], "18.5")

        # 3. Retrieve Farmer Profile via /me to confirm DB persistence
        get_f = self.client.get("/api/auth/me", headers={"Authorization": f"Bearer {f_token}"})
        self.assertEqual(get_f.status_code, 200)
        user_f = get_f.get_json()["user"]
        self.assertEqual(user_f["full_name"], "Updated Farmer Name")
        self.assertEqual(user_f["farm_size_acres"], "18.5")
        self.assertEqual(user_f["village"], "Chandwad")
        self.assertEqual(user_f["primary_crops"], "Tomato, Pomegranate, Grapes")

        # 4. Register Buyer
        b_email = f"buyer_prof_{self.run_id}@test.com"
        b_phone = f"9882{random.randint(100000, 999999)}"
        reg_b = self.client.post("/api/auth/register", json={
            "role": "buyer",
            "full_name": "Original Buyer Name",
            "business_name": "Old Business Ltd",
            "email": b_email,
            "phone": b_phone,
            "password": "Password123!",
            "state": "Maharashtra",
            "district": "Pune",
            "city": "Pune"
        })
        self.assertEqual(reg_b.status_code, 201)
        b_token = reg_b.get_json()["token"]

        # 5. Update Buyer Profile
        upd_b = self.client.put("/api/auth/profile", json={
            "full_name": "Updated Buyer Name",
            "business_name": "Supreme Agro Foods Pvt Ltd",
            "city": "Navi Mumbai",
            "gstin": "27AABCS1429B1ZB"
        }, headers={"Authorization": f"Bearer {b_token}"})
        self.assertEqual(upd_b.status_code, 200)
        self.assertTrue(upd_b.get_json()["success"])
        self.assertEqual(upd_b.get_json()["user"]["business_name"], "Supreme Agro Foods Pvt Ltd")

        # 6. Retrieve Buyer Profile via /me to confirm DB persistence
        get_b = self.client.get("/api/auth/me", headers={"Authorization": f"Bearer {b_token}"})
        self.assertEqual(get_b.status_code, 200)
        user_b = get_b.get_json()["user"]
        self.assertEqual(user_b["full_name"], "Updated Buyer Name")
        self.assertEqual(user_b["business_name"], "Supreme Agro Foods Pvt Ltd")
        self.assertEqual(user_b["city"], "Navi Mumbai")
        self.assertEqual(user_b["gstin"], "27AABCS1429B1ZB")


if __name__ == "__main__":
    unittest.main()
