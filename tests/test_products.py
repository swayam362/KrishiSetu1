
import os
import sys
import unittest
import io
import json
from PIL import Image

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app import create_app
from backend.database import get_db


class TestKrushiSetuProducts(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

        # Clean collections for deterministic testing
        users_col = get_db().get_collection("users")
        products_col = get_db().get_collection("products")

        if hasattr(users_col, "drop"):
            users_col.drop()
        if hasattr(products_col, "drop"):
            products_col.drop()

        # Register Farmer A
        res_a = self.client.post("/api/auth/register", json={
            "role": "farmer",
            "full_name": "Farmer Ramesh",
            "email": "farmer.ramesh@test.com",
            "phone": "9800000001",
            "password": "password123",
            "state": "Maharashtra",
            "district": "Nashik",
            "village": "Ozar"
        })
        self.farmer_a_token = res_a.get_json()["token"]
        self.farmer_a_id = res_a.get_json()["user"]["id"]

        # Register Farmer B
        res_b = self.client.post("/api/auth/register", json={
            "role": "farmer",
            "full_name": "Farmer Suresh",
            "email": "farmer.suresh@test.com",
            "phone": "9800000002",
            "password": "password123",
            "state": "Maharashtra",
            "district": "Lasalgaon",
            "village": "Lasalgaon"
        })
        self.farmer_b_token = res_b.get_json()["token"]

        # Register Buyer
        res_c = self.client.post("/api/auth/register", json={
            "role": "buyer",
            "full_name": "Buyer Sunil",
            "business_name": "Sunil Foods",
            "email": "buyer.sunil@test.com",
            "phone": "9800000003",
            "password": "password123",
            "state": "Maharashtra",
            "district": "Pune",
            "city": "Pune City"
        })
        self.buyer_token = res_c.get_json()["token"]

    def test_farmer_can_create_product(self):
        payload = {
            "crop_name": "Organic Sharbati Wheat",
            "category": "Grains",
            "quantity": 5000,
            "unit": "kg",
            "expected_price": 39.5,
            "grade": "Grade A+",
            "harvest_date": "2026-09-20",
            "description": "Clean organic sharbati wheat."
        }

        res = self.client.post(
            "/api/products/",
            json=payload,
            headers={
                "Authorization": f"Bearer {self.farmer_a_token}"
            }
        )

        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(
            data["product"]["crop_name"], "Organic Sharbati Wheat"
        )
        self.assertEqual(
            data["product"]["farmer_id"], self.farmer_a_id
        )

    def test_buyer_cannot_create_product(self):
        payload = {
            "crop_name": "Buyer Fake Crop",
            "category": "Grains",
            "quantity": 1000,
            "expected_price": 40.0
        }

        res = self.client.post(
            "/api/products/",
            json=payload,
            headers={
                "Authorization": f"Bearer {self.buyer_token}"
            }
        )

        self.assertEqual(res.status_code, 403)
        self.assertFalse(res.get_json()["success"])

    def test_farmer_a_cannot_edit_farmer_b_product(self):
        res = self.client.post(
            "/api/products/",
            json={
                "crop_name": "Farmer B Red Onions",
                "category": "Vegetables",
                "quantity": 8000,
                "expected_price": 25.0
            },
            headers={
                "Authorization": f"Bearer {self.farmer_b_token}"
            }
        )

        product_id = res.get_json()["product"]["id"]

        edit_res = self.client.put(
            f"/api/products/{product_id}",
            json={"expected_price": 10.0},
            headers={
                "Authorization": f"Bearer {self.farmer_a_token}"
            }
        )

        self.assertEqual(edit_res.status_code, 403)
        self.assertFalse(edit_res.get_json()["success"])
        self.assertIn(
            "own produce listings", edit_res.get_json()["error"]
        )

    def test_farmer_can_edit_own_product(self):
        res = self.client.post(
            "/api/products/",
            json={
                "crop_name": "Farmer A Mangoes",
                "category": "Fruits",
                "quantity": 2000,
                "expected_price": 80.0
            },
            headers={
                "Authorization": f"Bearer {self.farmer_a_token}"
            }
        )

        product_id = res.get_json()["product"]["id"]

        edit_res = self.client.put(
            f"/api/products/{product_id}",
            json={
                "expected_price": 75.0,
                "availability": "Sold Out"
            },
            headers={
                "Authorization": f"Bearer {self.farmer_a_token}"
            }
        )

        self.assertEqual(edit_res.status_code, 200)
        updated = edit_res.get_json()["product"]
        self.assertEqual(updated["price_per_unit"], 75.0)
        self.assertEqual(updated["availability"], "Sold Out")

    def test_farmer_can_delete_own_product(self):
        res = self.client.post(
            "/api/products/",
            json={
                "crop_name": "Farmer A Tur Dal",
                "category": "Pulses",
                "quantity": 1500,
                "expected_price": 110.0
            },
            headers={
                "Authorization": f"Bearer {self.farmer_a_token}"
            }
        )

        product_id = res.get_json()["product"]["id"]

        del_b = self.client.delete(
            f"/api/products/{product_id}",
            headers={
                "Authorization": f"Bearer {self.farmer_b_token}"
            }
        )
        self.assertEqual(del_b.status_code, 403)

        del_a = self.client.delete(
            f"/api/products/{product_id}",
            headers={
                "Authorization": f"Bearer {self.farmer_a_token}"
            }
        )
        self.assertEqual(del_a.status_code, 200)

        check = self.client.get(f"/api/products/{product_id}")
        self.assertEqual(check.status_code, 404)

    def test_search_and_filters(self):
        self.client.post(
            "/api/products/",
            json={
                "crop_name": "Super Basmati Rice",
                "category": "Grains",
                "quantity": 10000,
                "expected_price": 55.0,
                "grade": "Export Grade",
                "location": "Karnal, Haryana"
            },
            headers={
                "Authorization": f"Bearer {self.farmer_a_token}"
            }
        )

        self.client.post(
            "/api/products/",
            json={
                "crop_name": "Organic Tomatoes",
                "category": "Vegetables",
                "quantity": 3000,
                "expected_price": 18.0,
                "grade": "Grade A",
                "location": "Nashik, Maharashtra"
            },
            headers={
                "Authorization": f"Bearer {self.farmer_a_token}"
            }
        )

        res_s = self.client.get("/api/products/?search=basmati")
        self.assertEqual(res_s.status_code, 200)
        self.assertEqual(len(res_s.get_json()["products"]), 1)
        self.assertEqual(
            res_s.get_json()["products"][0]["crop_name"],
            "Super Basmati Rice"
        )

        res_c = self.client.get("/api/products/?category=Vegetables")
        self.assertEqual(res_c.status_code, 200)
        self.assertTrue(
            all(
                p["category"] == "Vegetables"
                for p in res_c.get_json()["products"]
            )
        )

        res_p = self.client.get("/api/products/?max_price=20")
        self.assertEqual(res_p.status_code, 200)
        self.assertTrue(
            all(
                p["price_per_unit"] <= 20
                for p in res_p.get_json()["products"]
            )
        )

    def test_image_upload_security(self):
        """Test image upload and rejection of dangerous extensions."""

        # Create a real JPEG image for the upload test
        img_buffer = io.BytesIO()
        Image.new("RGB", (224, 224), color="green").save(
            img_buffer, format="JPEG"
        )
        img_buffer.seek(0)

        valid_img = (img_buffer, "test_crop.jpg")

        res_ok = self.client.post(
            "/api/products/upload-image",
            data={"image": valid_img},
            content_type="multipart/form-data",
            headers={
                "Authorization": f"Bearer {self.farmer_a_token}"
            }
        )

        self.assertEqual(res_ok.status_code, 201)
        self.assertTrue(
            res_ok.get_json()["image_url"].startswith(
                "/uploads/crops/crop_"
            )
        )

        # Reject dangerous executable extension
        malicious = (io.BytesIO(b"print('hack')"), "malware.exe")

        res_bad = self.client.post(
            "/api/products/upload-image",
            data={"image": malicious},
            content_type="multipart/form-data",
            headers={
                "Authorization": f"Bearer {self.farmer_a_token}"
            }
        )

        self.assertEqual(res_bad.status_code, 400)
        self.assertFalse(res_bad.get_json()["success"])


if __name__ == "__main__":
    unittest.main()
