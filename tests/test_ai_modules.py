import os
import sys
import unittest
import io
import json

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app import create_app
from backend.database import get_db

class TestKrushiSetuAIModules(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

        # Clean collections
        for col in ["users", "disease_results", "soil_data"]:
            c = get_db().get_collection(col)
            if hasattr(c, 'drop'): c.drop()

        # 1. Register Farmer A
        res_a = self.client.post("/api/auth/register", json={
            "role": "farmer", "full_name": "Farmer Ramesh", "email": "ramesh.ai@test.com",
            "phone": "9812300001", "password": "password123", "state": "Maharashtra",
            "district": "Nashik", "village": "Ozar"
        })
        self.farmer_a_token = res_a.get_json()["token"]
        self.farmer_a_id = res_a.get_json()["user"]["id"]

        # 2. Register Farmer B
        res_b = self.client.post("/api/auth/register", json={
            "role": "farmer", "full_name": "Farmer Suresh", "email": "suresh.ai@test.com",
            "phone": "9812300002", "password": "password123", "state": "Maharashtra",
            "district": "Lasalgaon", "village": "Lasalgaon"
        })
        self.farmer_b_token = res_b.get_json()["token"]
        self.farmer_b_id = res_b.get_json()["user"]["id"]

        # 3. Register Buyer (Should not access farmer agronomy diagnosis)
        res_buyer = self.client.post("/api/auth/register", json={
            "role": "buyer", "full_name": "Buyer Vikas", "business_name": "Vikas Foods",
            "email": "vikas.buyer@test.com", "phone": "9812300003", "password": "password123",
            "state": "Maharashtra", "district": "Pune", "city": "Pune"
        })
        self.buyer_token = res_buyer.get_json()["token"]

    def test_crop_doctor_valid_diagnosis(self):
        """Test leaf photo diagnosis returns pathology data, confidence, remedies, and AI disclaimer."""
        fake_leaf_image = (io.BytesIO(b"dummy leaf pixel data"), "tomato_leaf.jpg")
        res = self.client.post("/api/ai/crop-doctor/diagnose", data={
            "crop": "Tomato",
            "image": fake_leaf_image
        }, content_type="multipart/form-data", headers={"Authorization": f"Bearer {self.farmer_a_token}"})

        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("Early Blight", data["diagnosis"]["disease_name"])
        self.assertIn("Possible disease detected", data["diagnosis"]["status"])
        self.assertGreaterEqual(data["diagnosis"]["confidence"], 0.85)
        self.assertIn("disclaimer", data["diagnosis"])
        self.assertTrue(len(data["diagnosis"]["organic_remedies"]) > 0)
        self.assertTrue(len(data["diagnosis"]["chemical_management"]) > 0)

    def test_crop_doctor_invalid_file_rejected(self):
        """Test executable or non-image uploads are strictly rejected."""
        fake_executable = (io.BytesIO(b"malicious script"), "payload.exe")
        res = self.client.post("/api/ai/crop-doctor/diagnose", data={
            "crop": "Wheat",
            "image": fake_executable
        }, content_type="multipart/form-data", headers={"Authorization": f"Bearer {self.farmer_a_token}"})

        self.assertEqual(res.status_code, 400)
        self.assertFalse(res.get_json()["success"])

    def test_soil_analysis_valid_recommendations(self):
        """Test soil analysis generates tailored N-P-K fertilizer schedules and growth stage tips."""
        payload = {
            "crop": "Wheat",
            "nitrogen": 85.0,        # Deficient (<120)
            "phosphorus": 16.0,      # Deficient (<20)
            "potassium": 22.0,       # Deficient (<30)
            "ph": 6.2,               # Ideal/Slightly acidic
            "organic_carbon": 0.45,  # Low (<0.5%)
            "growth_stage": "Sowing/Basal",
            "location": "Nashik, MH"
        }
        res = self.client.post("/api/ai/soil-analysis", json=payload, headers={"Authorization": f"Bearer {self.farmer_a_token}"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        analysis = data["data"]
        self.assertEqual(analysis["parameters"]["nitrogen"]["status"], "Deficient / Low")
        self.assertEqual(analysis["parameters"]["phosphorus"]["status"], "Deficient / Low")
        self.assertEqual(analysis["parameters"]["potassium"]["status"], "Deficient / Low")
        self.assertTrue(len(analysis["fertilizer_options"]) >= 2)
        self.assertIn("Sowing", analysis["stage_advisory"])
        self.assertIn("disclaimer", analysis)

    def test_soil_analysis_invalid_inputs_rejected(self):
        """Test invalid soil nutrient values (negative numbers, pH out of bounds) are rejected."""
        # 1. Negative nutrient
        res_neg = self.client.post("/api/ai/soil-analysis", json={
            "crop": "Onion", "nitrogen": -40.0, "phosphorus": 20.0, "potassium": 30.0, "ph": 6.5
        }, headers={"Authorization": f"Bearer {self.farmer_a_token}"})
        self.assertEqual(res_neg.status_code, 400)

        # 2. Impossible pH value (>14.0)
        res_ph = self.client.post("/api/ai/soil-analysis", json={
            "crop": "Onion", "nitrogen": 140.0, "phosphorus": 20.0, "potassium": 30.0, "ph": 16.5
        }, headers={"Authorization": f"Bearer {self.farmer_a_token}"})
        self.assertEqual(res_ph.status_code, 400)

    def test_private_agronomy_history_isolation(self):
        """Test Farmer A's scan and soil records are isolated from Farmer B."""
        # Farmer A runs diagnosis
        img = (io.BytesIO(b"leaf image data"), "leaf.jpg")
        self.client.post("/api/ai/crop-doctor/diagnose", data={"crop": "Tomato", "image": img},
                         content_type="multipart/form-data", headers={"Authorization": f"Bearer {self.farmer_a_token}"})

        # Farmer A runs soil test
        self.client.post("/api/ai/soil-analysis", json={
            "crop": "Tomato", "nitrogen": 100, "phosphorus": 25, "potassium": 35, "ph": 6.8
        }, headers={"Authorization": f"Bearer {self.farmer_a_token}"})

        # Farmer A checks history -> 1 scan, 1 soil record
        hist_a_scans = self.client.get("/api/ai/crop-doctor/history", headers={"Authorization": f"Bearer {self.farmer_a_token}"})
        self.assertEqual(hist_a_scans.get_json()["count"], 1)

        hist_a_soil = self.client.get("/api/ai/soil-analysis/history", headers={"Authorization": f"Bearer {self.farmer_a_token}"})
        self.assertEqual(hist_a_soil.get_json()["count"], 1)

        # Farmer B checks history -> 0 scans, 0 soil records (Private Isolation!)
        hist_b_scans = self.client.get("/api/ai/crop-doctor/history", headers={"Authorization": f"Bearer {self.farmer_b_token}"})
        self.assertEqual(hist_b_scans.get_json()["count"], 0)

        hist_b_soil = self.client.get("/api/ai/soil-analysis/history", headers={"Authorization": f"Bearer {self.farmer_b_token}"})
        self.assertEqual(hist_b_soil.get_json()["count"], 0)

if __name__ == "__main__":
    unittest.main()
