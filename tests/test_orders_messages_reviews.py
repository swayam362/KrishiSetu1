import os
import sys
import unittest
import json

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app import create_app
from backend.database import get_db

class TestKrushiSetuOrdersMessagesReviews(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

        # Clean collections for deterministic testing
        for col_name in ["users", "products", "orders", "messages", "reviews"]:
            col = get_db().get_collection(col_name)
            if hasattr(col, 'drop'): col.drop()

        # 1. Register Farmer A
        res_fa = self.client.post("/api/auth/register", json={
            "role": "farmer", "full_name": "Farmer Arjun", "email": "arjun.farmer@test.com",
            "phone": "9811111111", "password": "password123", "state": "Maharashtra",
            "district": "Nashik", "village": "Ozar"
        })
        self.farmer_a_token = res_fa.get_json()["token"]
        self.farmer_a_id = res_fa.get_json()["user"]["id"]

        # 2. Register Farmer B (Unrelated)
        res_fb = self.client.post("/api/auth/register", json={
            "role": "farmer", "full_name": "Farmer Balaram", "email": "balaram.farmer@test.com",
            "phone": "9822222222", "password": "password123", "state": "Maharashtra",
            "district": "Nagpur", "village": "Katol"
        })
        self.farmer_b_token = res_fb.get_json()["token"]
        self.farmer_b_id = res_fb.get_json()["user"]["id"]

        # 3. Register Buyer A
        res_ba = self.client.post("/api/auth/register", json={
            "role": "buyer", "full_name": "Buyer Rajesh", "business_name": "Rajesh Agro Corp",
            "email": "rajesh.buyer@test.com", "phone": "9833333333", "password": "password123",
            "state": "Maharashtra", "district": "Pune", "city": "Pune City"
        })
        self.buyer_a_token = res_ba.get_json()["token"]
        self.buyer_a_id = res_ba.get_json()["user"]["id"]

        # 4. Register Buyer B (Unrelated)
        res_bb = self.client.post("/api/auth/register", json={
            "role": "buyer", "full_name": "Buyer Dinesh", "business_name": "Dinesh Mart",
            "email": "dinesh.buyer@test.com", "phone": "9844444444", "password": "password123",
            "state": "Maharashtra", "district": "Mumbai", "city": "Navi Mumbai"
        })
        self.buyer_b_token = res_bb.get_json()["token"]
        self.buyer_b_id = res_bb.get_json()["user"]["id"]

        # 5. Farmer A lists a product (Wheat: 5000 kg @ ₹40.0/kg)
        prod_res = self.client.post("/api/products/", json={
            "crop_name": "Golden Harvest Wheat", "category": "Grains", "quantity": 5000,
            "unit": "kg", "expected_price": 40.0, "grade": "Grade A+"
        }, headers={"Authorization": f"Bearer {self.farmer_a_token}"})
        self.product_id = prod_res.get_json()["product"]["id"]

    def test_place_order_server_side_price_calculation(self):
        """Test server calculates total amount strictly from database price, ignoring frontend tampering."""
        # Frontend sends malicious price ₹1.0, backend MUST ignore and use actual ₹40.0
        payload = {
            "product_id": self.product_id,
            "quantity": 1000,
            "price": 1.0,           # Tampered
            "total_amount": 1000.0,  # Tampered
            "delivery_address": "Pune Wholesale Hub, Warehouse 4B"
        }
        res = self.client.post("/api/orders/", json=payload, headers={"Authorization": f"Bearer {self.buyer_a_token}"})
        self.assertEqual(res.status_code, 201)
        order = res.get_json()["order"]
        # Expected: 1000 kg * 40.0 = 40,000.0
        self.assertEqual(order["price_per_unit"], 40.0)
        self.assertEqual(order["total_amount"], 40000.0)
        self.assertEqual(order["status"], "Pending")

        # Verify product stock deducted: 5000 - 1000 = 4000
        p_check = self.client.get(f"/api/products/{self.product_id}")
        self.assertEqual(p_check.get_json()["product"]["quantity"], 4000)

    def test_order_negative_or_excess_quantity_rejected(self):
        """Test order is rejected on invalid or excess quantity."""
        # 1. Negative quantity
        res_neg = self.client.post("/api/orders/", json={
            "product_id": self.product_id, "quantity": -50, "delivery_address": "Pune"
        }, headers={"Authorization": f"Bearer {self.buyer_a_token}"})
        self.assertEqual(res_neg.status_code, 400)

        # 2. Excess quantity (Available is 5000 kg, requested is 8000 kg)
        res_excess = self.client.post("/api/orders/", json={
            "product_id": self.product_id, "quantity": 8000, "delivery_address": "Pune"
        }, headers={"Authorization": f"Bearer {self.buyer_a_token}"})
        self.assertEqual(res_excess.status_code, 400)
        self.assertIn("exceeds available stock", res_excess.get_json()["error"])

    def test_unauthorized_order_access_isolation(self):
        """Test Buyer B cannot view Buyer A's order, and Farmer B cannot view Farmer A's order."""
        # Buyer A places order
        res = self.client.post("/api/orders/", json={
            "product_id": self.product_id, "quantity": 500, "delivery_address": "Pune"
        }, headers={"Authorization": f"Bearer {self.buyer_a_token}"})
        order_id = res.get_json()["order"]["id"]

        # Buyer B tries to view Buyer A's order -> 403 Forbidden!
        res_bb = self.client.get(f"/api/orders/{order_id}", headers={"Authorization": f"Bearer {self.buyer_b_token}"})
        self.assertEqual(res_bb.status_code, 403)

        # Farmer B tries to view Farmer A's order -> 403 Forbidden!
        res_fb = self.client.get(f"/api/orders/{order_id}", headers={"Authorization": f"Bearer {self.farmer_b_token}"})
        self.assertEqual(res_fb.status_code, 403)

        # Buyer A and Farmer A CAN view order -> 200 OK
        self.assertEqual(self.client.get(f"/api/orders/{order_id}", headers={"Authorization": f"Bearer {self.buyer_a_token}"}).status_code, 200)
        self.assertEqual(self.client.get(f"/api/orders/{order_id}", headers={"Authorization": f"Bearer {self.farmer_a_token}"}).status_code, 200)

    def test_order_lifecycle_and_status_transitions(self):
        """Test complete valid status progression: Pending -> Accepted -> Processing -> Shipped -> Delivered -> Completed."""
        res = self.client.post("/api/orders/", json={
            "product_id": self.product_id, "quantity": 1000, "delivery_address": "Pune"
        }, headers={"Authorization": f"Bearer {self.buyer_a_token}"})
        order_id = res.get_json()["order"]["id"]

        # 1. Farmer A accepts order
        res_acc = self.client.patch(f"/api/orders/{order_id}/status", json={"status": "Accepted"},
                                   headers={"Authorization": f"Bearer {self.farmer_a_token}"})
        self.assertEqual(res_acc.status_code, 200)
        self.assertEqual(res_acc.get_json()["order"]["status"], "Accepted")

        # 2. Farmer A marks processing
        res_proc = self.client.patch(f"/api/orders/{order_id}/status", json={"status": "Processing"},
                                    headers={"Authorization": f"Bearer {self.farmer_a_token}"})
        self.assertEqual(res_proc.status_code, 200)

        # 3. Farmer A ships order
        res_ship = self.client.patch(f"/api/orders/{order_id}/status", json={"status": "Shipped"},
                                    headers={"Authorization": f"Bearer {self.farmer_a_token}"})
        self.assertEqual(res_ship.status_code, 200)

        # 4. Buyer A confirms delivery on receipt
        res_del = self.client.patch(f"/api/orders/{order_id}/status", json={"status": "Delivered"},
                                   headers={"Authorization": f"Bearer {self.buyer_a_token}"})
        self.assertEqual(res_del.status_code, 200)
        self.assertEqual(res_del.get_json()["order"]["status"], "Delivered")
        self.assertIn("Released to Farmer", res_del.get_json()["order"]["escrow_status"])

    def test_unauthorized_status_update_rejected(self):
        """Test Buyer cannot mark an order Accepted or Shipped (Farmer actions)."""
        res = self.client.post("/api/orders/", json={
            "product_id": self.product_id, "quantity": 500, "delivery_address": "Pune"
        }, headers={"Authorization": f"Bearer {self.buyer_a_token}"})
        order_id = res.get_json()["order"]["id"]

        # Buyer attempts to Accept order -> 403 Forbidden
        bad_res = self.client.patch(f"/api/orders/{order_id}/status", json={"status": "Accepted"},
                                   headers={"Authorization": f"Bearer {self.buyer_a_token}"})
        self.assertEqual(bad_res.status_code, 403)

    def test_private_messaging_between_participants(self):
        """Test private messaging and thread isolation."""
        # 1. Buyer A sends message to Farmer A
        send_res = self.client.post("/api/messages/send", json={
            "recipient_id": self.farmer_a_id,
            "content": "Hello Farmer Arjun, is this wheat batch moisture-tested below 11%?",
            "product_id": self.product_id
        }, headers={"Authorization": f"Bearer {self.buyer_a_token}"})
        self.assertEqual(send_res.status_code, 201)

        # 2. Farmer A replies to Buyer A
        reply_res = self.client.post("/api/messages/send", json={
            "recipient_id": self.buyer_a_id,
            "content": "Yes Rajeshji, tested at 10.4% moisture yesterday."
        }, headers={"Authorization": f"Bearer {self.farmer_a_token}"})
        self.assertEqual(reply_res.status_code, 201)

        # 3. Buyer A views thread with Farmer A -> 2 messages
        thread_a = self.client.get(f"/api/messages/thread/{self.farmer_a_id}", headers={"Authorization": f"Bearer {self.buyer_a_token}"})
        self.assertEqual(thread_a.status_code, 200)
        self.assertEqual(thread_a.get_json()["count"], 2)

        # 4. Third-party Buyer B queries thread between Buyer A and Farmer A -> 0 messages (Isolated!)
        thread_b = self.client.get(f"/api/messages/thread/{self.farmer_a_id}", headers={"Authorization": f"Bearer {self.buyer_b_token}"})
        self.assertEqual(thread_b.status_code, 200)
        self.assertEqual(thread_b.get_json()["count"], 0)

    def test_verified_reviews_lifecycle(self):
        """Test that only buyers with completed/delivered orders can submit reviews."""
        # 1. Buyer A places order and completes it
        res = self.client.post("/api/orders/", json={
            "product_id": self.product_id, "quantity": 1000, "delivery_address": "Pune"
        }, headers={"Authorization": f"Bearer {self.buyer_a_token}"})
        order_id = res.get_json()["order"]["id"]

        # Order is still 'Pending' -> Review attempt MUST fail!
        early_rev = self.client.post("/api/reviews/", json={
            "order_id": order_id, "rating": 5, "comment": "Great wheat!"
        }, headers={"Authorization": f"Bearer {self.buyer_a_token}"})
        self.assertEqual(early_rev.status_code, 400)
        self.assertIn("only permitted for delivered or completed orders", early_rev.get_json()["error"])

        # Progress order to Delivered
        self.client.patch(f"/api/orders/{order_id}/status", json={"status": "Accepted"}, headers={"Authorization": f"Bearer {self.farmer_a_token}"})
        self.client.patch(f"/api/orders/{order_id}/status", json={"status": "Shipped"}, headers={"Authorization": f"Bearer {self.farmer_a_token}"})
        self.client.patch(f"/api/orders/{order_id}/status", json={"status": "Delivered"}, headers={"Authorization": f"Bearer {self.buyer_a_token}"})

        # 2. Buyer B (did not buy this order) attempts to review -> 403 Forbidden!
        fake_rev = self.client.post("/api/reviews/", json={
            "order_id": order_id, "rating": 1, "comment": "Fake bad review"
        }, headers={"Authorization": f"Bearer {self.buyer_b_token}"})
        self.assertEqual(fake_rev.status_code, 403)

        # 3. Legitimate Buyer A submits verified review -> 201 Created!
        legit_rev = self.client.post("/api/reviews/", json={
            "order_id": order_id, "rating": 5, "comment": "Outstanding quality Sharbati wheat, arrived clean with prompt logistics."
        }, headers={"Authorization": f"Bearer {self.buyer_a_token}"})
        self.assertEqual(legit_rev.status_code, 201)
        self.assertTrue(legit_rev.get_json()["review"]["is_verified_purchase"])

        # 4. Duplicate review on same order -> 409 Conflict
        dup_rev = self.client.post("/api/reviews/", json={
            "order_id": order_id, "rating": 5, "comment": "Trying again"
        }, headers={"Authorization": f"Bearer {self.buyer_a_token}"})
        self.assertEqual(dup_rev.status_code, 409)

        # 5. Check product reviews endpoint reflects rating 5.0
        p_revs = self.client.get(f"/api/reviews/product/{self.product_id}")
        self.assertEqual(p_revs.status_code, 200)
        self.assertEqual(p_revs.get_json()["count"], 1)
        self.assertEqual(p_revs.get_json()["average_rating"], 5.0)

if __name__ == "__main__":
    unittest.main()
