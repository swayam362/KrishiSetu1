import os
import sys
import unittest
import json

# Add project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app import create_app
from backend.database import get_db

class TestKrushiSetuAuth(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        # Clean users collection before each test
        users_col = get_db().get_collection("users")
        if hasattr(users_col, 'drop'):
            users_col.drop()

    def test_database_collections_initialized(self):
        """Verify all 11 required collections exist in database architecture."""
        db = get_db()
        for col_name in db.COLLECTIONS:
            col = db.get_collection(col_name)
            self.assertIsNotNone(col)

    def test_farmer_registration_success(self):
        """Test successful registration of a Farmer with all required fields."""
        payload = {
            "role": "farmer",
            "full_name": "Ramesh Patil",
            "email": "ramesh.patil@testkrushi.com",
            "phone": "9876543210",
            "password": "secureFarmerPassword123",
            "state": "Maharashtra",
            "district": "Nashik",
            "village": "Ozar",
            "farm_size_acres": "12.5",
            "primary_crops": "Wheat, Onion"
        }
        res = self.client.post("/api/auth/register", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("token", data)
        self.assertEqual(data["user"]["role"], "farmer")
        self.assertEqual(data["user"]["email"], "ramesh.patil@testkrushi.com")
        self.assertNotIn("password", data["user"])
        self.assertNotIn("password_hash", data["user"])

    def test_buyer_registration_success(self):
        """Test successful registration of a Buyer with business name and location."""
        payload = {
            "role": "buyer",
            "full_name": "Vikram Sethi",
            "business_name": "AgroFresh Foods Pvt Ltd",
            "email": "vikram@agrofresh.com",
            "phone": "9812345678",
            "password": "secureBuyerPassword123",
            "state": "Maharashtra",
            "district": "Pune",
            "city": "Pune City",
            "gstin": "27AAAAA0000A1Z5"
        }
        res = self.client.post("/api/auth/register", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["user"]["role"], "buyer")
        self.assertEqual(data["user"]["business_name"], "AgroFresh Foods Pvt Ltd")
        self.assertNotIn("password", data["user"])
        self.assertNotIn("password_hash", data["user"])

    def test_login_success(self):
        """Test user login with valid email and password."""
        # 1. Register first
        self.client.post("/api/auth/register", json={
            "role": "farmer",
            "full_name": "Suresh Deshmukh",
            "email": "suresh@krushitest.com",
            "phone": "9822334455",
            "password": "mypassword123",
            "state": "Maharashtra",
            "district": "Nashik",
            "village": "Lasalgaon"
        })

        # 2. Login with email
        login_res = self.client.post("/api/auth/login", json={
            "email": "suresh@krushitest.com",
            "password": "mypassword123"
        })
        self.assertEqual(login_res.status_code, 200)
        data = login_res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("token", data)
        self.assertNotIn("password", data["user"])

    def test_login_wrong_password(self):
        """Test login fails when password is incorrect."""
        self.client.post("/api/auth/register", json={
            "role": "farmer",
            "full_name": "Ganpat Yadav",
            "email": "ganpat@krushitest.com",
            "phone": "9833445566",
            "password": "correctPassword",
            "state": "Karnataka",
            "district": "Gulbarga",
            "village": "Afzalpur"
        })

        res = self.client.post("/api/auth/login", json={
            "email": "ganpat@krushitest.com",
            "password": "wrongPassword123"
        })
        self.assertEqual(res.status_code, 401)
        data = res.get_json()
        self.assertFalse(data["success"])
        self.assertIn("Invalid email/phone or password", data["error"])

    def test_duplicate_email_rejection(self):
        """Test duplicate email is rejected with 409 Conflict."""
        payload = {
            "role": "farmer",
            "full_name": "Amol Shinde",
            "email": "duplicate@krushitest.com",
            "phone": "9844556677",
            "password": "testPassword123",
            "state": "Maharashtra",
            "district": "Nagpur",
            "village": "Katol"
        }
        res1 = self.client.post("/api/auth/register", json=payload)
        self.assertEqual(res1.status_code, 201)

        payload2 = dict(payload)
        payload2["phone"] = "9899887766" # Different phone, same email
        res2 = self.client.post("/api/auth/register", json=payload2)
        self.assertEqual(res2.status_code, 409)
        data = res2.get_json()
        self.assertFalse(data["success"])
        self.assertIn("already exists", data["error"])

    def test_invalid_email_format(self):
        """Test registration rejection on invalid email syntax."""
        payload = {
            "role": "farmer",
            "full_name": "Invalid Email User",
            "email": "not-an-email",
            "phone": "9855667788",
            "password": "testPassword123",
            "state": "Maharashtra",
            "district": "Nashik",
            "village": "Ozar"
        }
        res = self.client.post("/api/auth/register", json=payload)
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertFalse(data["success"])
        self.assertIn("valid email", data["error"])

    def test_missing_required_fields(self):
        """Test validation error when required fields are missing."""
        # Missing state and district
        payload = {
            "role": "farmer",
            "full_name": "Incomplete User",
            "email": "incomplete@krushitest.com",
            "phone": "9866778899",
            "password": "testPassword123"
        }
        res = self.client.post("/api/auth/register", json=payload)
        self.assertEqual(res.status_code, 400)

    def test_unauthorized_dashboard_access_without_token(self):
        """Test protected endpoint rejects request without Authorization header."""
        res = self.client.get("/api/auth/me")
        self.assertEqual(res.status_code, 401)
        data = res.get_json()
        self.assertFalse(data["success"])
        self.assertIn("missing", data["error"])

    def test_role_based_authorization_isolation(self):
        """Test Farmer cannot access Buyer-only route and vice versa."""
        # 1. Register Farmer
        reg_farmer = self.client.post("/api/auth/register", json={
            "role": "farmer",
            "full_name": "Farmer Ram",
            "email": "farmer.ram@test.com",
            "phone": "9877112233",
            "password": "password123",
            "state": "Maharashtra",
            "district": "Nashik",
            "village": "Panchavati"
        })
        farmer_token = reg_farmer.get_json()["token"]

        # 2. Register Buyer
        reg_buyer = self.client.post("/api/auth/register", json={
            "role": "buyer",
            "full_name": "Buyer Shyam",
            "business_name": "Shyam Trading Co",
            "email": "buyer.shyam@test.com",
            "phone": "9877223344",
            "password": "password123",
            "state": "Maharashtra",
            "district": "Mumbai",
            "city": "Vashi"
        })
        buyer_token = reg_buyer.get_json()["token"]

        # 3. Farmer accesses Farmer-only route -> 200 OK
        res_f_ok = self.client.get("/api/auth/farmer-only-action", headers={"Authorization": f"Bearer {farmer_token}"})
        self.assertEqual(res_f_ok.status_code, 200)

        # 4. Farmer tries to access Buyer-only route -> 403 Forbidden!
        res_f_forbidden = self.client.get("/api/auth/buyer-only-action", headers={"Authorization": f"Bearer {farmer_token}"})
        self.assertEqual(res_f_forbidden.status_code, 403)
        self.assertFalse(res_f_forbidden.get_json()["success"])

        # 5. Buyer accesses Buyer-only route -> 200 OK
        res_b_ok = self.client.get("/api/auth/buyer-only-action", headers={"Authorization": f"Bearer {buyer_token}"})
        self.assertEqual(res_b_ok.status_code, 200)

        # 6. Buyer tries to access Farmer-only route -> 403 Forbidden!
        res_b_forbidden = self.client.get("/api/auth/farmer-only-action", headers={"Authorization": f"Bearer {buyer_token}"})
        self.assertEqual(res_b_forbidden.status_code, 403)

if __name__ == "__main__":
    unittest.main()
