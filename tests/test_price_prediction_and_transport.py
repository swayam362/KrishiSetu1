"""
Automated Test Suite for KrushiSetu Prompt 7/10
Tests:
1. Valid price prediction (Current price, Expected price range, Uncertainty/confidence, Factors affecting prediction, Wording check)
2. Missing values handling
3. Invalid values & code injection rejection
4. Transportation estimation & vehicle sizing
5. Unauthorized access protection on private prediction history
6. External API failure resilience & fallback
7. Location privacy masking
"""

import os
import sys
import json
import unittest
from unittest.mock import patch

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app import create_app
from backend.utils.transportation_service import get_transportation_engine, SUPPORTED_VEHICLES
from backend.utils.location_privacy import mask_location_for_public, format_public_region
from ml.demand.predict import get_demand_predictor

class TestPricePredictionAndTransportation(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.predictor = get_demand_predictor()
        self.transport_engine = get_transportation_engine()

        # Clean collections for deterministic testing
        for col_name in ["users", "price_predictions"]:
            col = self.app.config.get("DB", None)
            from backend.database import get_db
            c = get_db().get_collection(col_name)
            if hasattr(c, 'drop'):
                c.drop()

        # Register Farmer P7
        res_f = self.client.post("/api/auth/register", json={
            "role": "farmer",
            "full_name": "Farmer Ramesh P7",
            "email": "farmer_p7@krushisetu.in",
            "phone": "9823001111",
            "password": "Password123!",
            "state": "Maharashtra",
            "district": "Nashik",
            "village": "Pimpalgaon",
            "farm_size_acres": "8"
        })
        f_data = res_f.get_json() or {}
        self.farmer_token = f_data.get("token") or f_data.get("access_token")
        self.farmer_id = f_data.get("user", {}).get("id")

        # Register Buyer P7
        res_b = self.client.post("/api/auth/register", json={
            "role": "buyer",
            "full_name": "Buyer Vikram P7",
            "email": "buyer_p7@krushisetu.in",
            "phone": "9823002222",
            "password": "Password123!",
            "state": "Maharashtra",
            "district": "Mumbai",
            "city": "Mumbai",
            "business_name": "Vikram Agro Trade"
        })
        b_data = res_b.get_json() or {}
        self.buyer_token = b_data.get("token") or b_data.get("access_token")
        self.buyer_id = b_data.get("user", {}).get("id")

    # =========================================================================
    # 1. PRICE PREDICTION TESTS
    # =========================================================================
    def test_valid_price_prediction_structure_and_wording(self):
        """
        Verify valid price prediction contains:
        - Current price
        - Expected price range (e.g. ₹27–₹31/kg)
        - Uncertainty / confidence
        - Factors affecting prediction
        - Strict check: Never say 'Guaranteed future price', must use 'Expected price range'
        """
        res = self.client.post("/api/ai/price-prediction", json={
            "crop": "Tomato",
            "location": "Pune",
            "period": "Next 7 days"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])

        # Check current price
        self.assertIn("current_price", data)
        self.assertIn("current_price_display", data)
        self.assertGreater(data["current_price"], 0)

        # Check expected price range
        self.assertIn("expected_price_range", data)
        self.assertIn("expected_price_display", data)
        self.assertIn("min_price", data["expected_price_range"])
        self.assertIn("max_price", data["expected_price_range"])
        self.assertLessEqual(data["expected_price_range"]["min_price"], data["expected_price_range"]["max_price"])

        # Check confidence & uncertainty
        self.assertIn("confidence_percent", data)
        self.assertIn("uncertainty", data)
        self.assertIn("bound_amount", data["uncertainty"])
        self.assertGreaterEqual(data["confidence_percent"], 70.0)

        # Check factors affecting prediction
        self.assertIn("factors_affecting_prediction", data)
        self.assertTrue(len(data["factors_affecting_prediction"]) > 0)

        # Strict wording compliance verification
        raw_json_str = json.dumps(data)
        self.assertNotIn("Guaranteed future price", raw_json_str)
        self.assertNotIn("guaranteed future price", raw_json_str.lower())
        self.assertIn("Expected price range", raw_json_str)
        self.assertIn("Forecast — not a guarantee.", data["disclaimer"])

    def test_price_prediction_missing_values(self):
        """Test missing fields default safely to standard benchmarks."""
        res = self.client.post("/api/ai/price-prediction", json={})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("Tomato", data["crop"])  # Default fallback crop

    def test_price_prediction_invalid_and_injection_inputs(self):
        """Test rejection of dangerous injection attempts and invalid payloads."""
        # 1. Code injection attempt
        res_inj = self.client.post("/api/ai/price-prediction", json={
            "crop": "Tomato; import os; os.system('rm -rf')",
            "location": "Pune",
            "period": "Next 7 days"
        })
        self.assertEqual(res_inj.status_code, 400)
        data_inj = res_inj.get_json()
        self.assertFalse(data_inj["success"])

        # 2. Dangerous script tags
        res_script = self.client.post("/api/ai/price-prediction", json={
            "crop": "<script>alert(1)</script>",
            "location": "Pune"
        })
        self.assertEqual(res_script.status_code, 400)

        # 3. Absurdly long string overflow
        res_long = self.client.post("/api/ai/price-prediction", json={
            "crop": "A" * 500,
            "location": "Pune"
        })
        self.assertEqual(res_long.status_code, 400)

    # =========================================================================
    # 2. TRANSPORTATION ESTIMATION TESTS
    # =========================================================================
    def test_transportation_estimation_valid_route(self):
        """Test transportation estimation between Pune and Mumbai for 5,000 kg."""
        res = self.client.post("/api/smart-selling/transport-estimate", json={
            "farmer_location": "Pune",
            "buyer_location": "Mumbai",
            "quantity_kg": 5000.0,
            "vehicle_type": "medium_truck"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])

        self.assertGreater(data["distance_km"], 100.0)
        self.assertGreater(data["transit_hours"], 2.0)
        self.assertEqual(data["trips_required"], 1)

        # Cost breakdown
        costs = data["cost_breakdown"]
        self.assertIn("base_freight", costs)
        self.assertIn("handling_and_loading", costs)
        self.assertIn("toll_and_permits", costs)
        self.assertIn("total_estimated_transport_cost", costs)
        self.assertIn("effective_cost_per_kg", costs)
        self.assertGreater(costs["total_estimated_transport_cost"], 1000.0)

    def test_transportation_vehicle_auto_sizing_and_multi_trip(self):
        """Test vehicle auto-recommendation when payload exceeds small vehicle capacity."""
        # 8,000 kg with mini_truck requested should require 8 trips
        res = self.client.post("/api/smart-selling/transport-estimate", json={
            "farmer_location": "Nashik",
            "buyer_location": "Mumbai",
            "quantity_kg": 8000.0,
            "vehicle_type": "mini_truck"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["trips_required"], 8)

        # Auto-recommend without specified vehicle for 8,000 kg should select heavy_truck (1 trip)
        res_auto = self.client.post("/api/smart-selling/transport-estimate", json={
            "farmer_location": "Nashik",
            "buyer_location": "Mumbai",
            "quantity_kg": 8000.0
        })
        self.assertEqual(res_auto.status_code, 200)
        data_auto = res_auto.get_json()
        self.assertEqual(data_auto["vehicle_type"]["id"], "heavy_truck")
        self.assertEqual(data_auto["trips_required"], 1)

    def test_transportation_cold_chain_reefer(self):
        """Test cold-chain temperature-controlled transport surcharge."""
        res_standard = self.client.post("/api/smart-selling/transport-estimate", json={
            "farmer_location": "Nashik",
            "buyer_location": "Mumbai",
            "quantity_kg": 3000.0,
            "requires_cold_storage": False
        })
        res_reefer = self.client.post("/api/smart-selling/transport-estimate", json={
            "farmer_location": "Nashik",
            "buyer_location": "Mumbai",
            "quantity_kg": 3000.0,
            "requires_cold_storage": True
        })
        cost_std = res_standard.get_json()["cost_breakdown"]["total_estimated_transport_cost"]
        cost_reefer = res_reefer.get_json()["cost_breakdown"]["total_estimated_transport_cost"]
        self.assertGreater(cost_reefer, cost_std)
        self.assertGreater(res_reefer.get_json()["cost_breakdown"]["cold_storage_surcharge"], 0)

    def test_transportation_invalid_and_missing_values(self):
        """Test negative quantity, zero quantity, and non-numeric inputs are rejected."""
        # Negative quantity
        res_neg = self.client.post("/api/smart-selling/transport-estimate", json={"quantity_kg": -500})
        self.assertEqual(res_neg.status_code, 400)

        # Zero quantity
        res_zero = self.client.post("/api/smart-selling/transport-estimate", json={"quantity_kg": 0})
        self.assertEqual(res_zero.status_code, 400)

        # Non-numeric quantity
        res_str = self.client.post("/api/smart-selling/transport-estimate", json={"quantity_kg": "five thousand"})
        self.assertEqual(res_str.status_code, 400)

        # Quantity over max allowable limit (100,000 kg)
        res_over = self.client.post("/api/smart-selling/transport-estimate", json={"quantity_kg": 500000})
        self.assertEqual(res_over.status_code, 400)

    def test_vehicles_list_api(self):
        """Test GET /api/smart-selling/vehicles returns calibrated vehicle list."""
        res = self.client.get("/api/smart-selling/vehicles")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertGreaterEqual(len(data["vehicles"]), 5)
        veh_ids = [v["id"] for v in data["vehicles"]]
        self.assertIn("mini_truck", veh_ids)
        self.assertIn("pickup", veh_ids)
        self.assertIn("medium_truck", veh_ids)
        self.assertIn("heavy_truck", veh_ids)
        self.assertIn("reefer", veh_ids)

    # =========================================================================
    # 3. SECURITY & UNAUTHORIZED ACCESS TESTS
    # =========================================================================
    def test_unauthorized_access_to_private_prediction_history(self):
        """
        Verify that accessing or saving private prediction history
        WITHOUT authentication returns 401 Unauthorized.
        """
        # GET private history without token -> 401
        res_unauth = self.client.get("/api/ai/price-prediction/history")
        self.assertEqual(res_unauth.status_code, 401)

        # POST save private prediction without token -> 401
        res_save_unauth = self.client.post("/api/ai/price-prediction/save", json={
            "crop": "Wheat",
            "location": "Indore"
        })
        self.assertEqual(res_save_unauth.status_code, 401)

    def test_authorized_private_prediction_save_and_isolation(self):
        """
        Verify authenticated user can save and retrieve their private predictions,
        and predictions are isolated between users.
        """
        # 1. Farmer saves private prediction
        res_save = self.client.post("/api/ai/price-prediction/save", json={
            "crop": "Wheat",
            "location": "Indore",
            "period": "Next 15 days"
        }, headers={"Authorization": f"Bearer {self.farmer_token}"})
        self.assertEqual(res_save.status_code, 201)
        save_data = res_save.get_json()
        self.assertTrue(save_data["success"])
        pred_id = save_data["prediction_id"]

        # 2. Farmer retrieves private history
        res_hist = self.client.get("/api/ai/price-prediction/history", headers={"Authorization": f"Bearer {self.farmer_token}"})
        self.assertEqual(res_hist.status_code, 200)
        hist_data = res_hist.get_json()
        self.assertTrue(hist_data["success"])
        farmer_pred_ids = [item["id"] for item in hist_data["history"]]
        self.assertIn(pred_id, farmer_pred_ids)

        # 3. Buyer retrieves history -> Farmer's prediction should NOT be in Buyer's list (User Isolation)
        res_buyer_hist = self.client.get("/api/ai/price-prediction/history", headers={"Authorization": f"Bearer {self.buyer_token}"})
        self.assertEqual(res_buyer_hist.status_code, 200)
        buyer_hist_data = res_buyer_hist.get_json()
        buyer_pred_ids = [item["id"] for item in buyer_hist_data["history"]]
        self.assertNotIn(pred_id, buyer_pred_ids)

    # =========================================================================
    # 4. EXTERNAL API FAILURE RESILIENCE
    # =========================================================================
    def test_external_maps_and_weather_api_failure_resilience(self):
        """
        Test that external API timeouts, connection errors, or rate limits
        fall back smoothly to internal models without 500 crashes.
        """
        with patch("requests.get", side_effect=Exception("External Maps API Timeout")):
            # Transport distance calculation should gracefully fall back to internal haversine matrix
            estimate = self.transport_engine.estimate_transportation_cost(
                farmer_location="Nashik",
                buyer_location="Mumbai",
                quantity_kg=4000.0
            )
            self.assertTrue(estimate["success"])
            self.assertGreater(estimate["distance_km"], 50.0)
            self.assertGreater(estimate["cost_breakdown"]["total_estimated_transport_cost"], 0)

        with patch("requests.get", side_effect=Exception("External Weather API 503 Service Unavailable")):
            # Price prediction should gracefully fall back to agro-climatological benchmark
            prediction = self.predictor.predict_demand(
                crop="Tomato",
                location="Pune",
                forecast_period="Next 7 days"
            )
            self.assertTrue(prediction["success"])
            self.assertIn("weather_summary", prediction)
            self.assertIn("current_price", prediction)

    # =========================================================================
    # 5. LOCATION PRIVACY TESTS
    # =========================================================================
    def test_location_privacy_masking(self):
        """
        Verify that exact home addresses/coordinates are masked to administrative regions.
        """
        # Exact address dictionary
        exact_location_dict = {
            "survey_number": "Plot 42/B",
            "street": "Near Hanuman Temple, Pimpalgaon Village",
            "village": "Pimpalgaon Baswant",
            "district": "Nashik",
            "state": "Maharashtra",
            "gps_lat": 20.1654,
            "gps_lon": 73.9876
        }
        masked = mask_location_for_public(exact_location_dict)
        self.assertEqual(masked["district"], "Nashik")
        self.assertEqual(masked["state"], "Maharashtra")
        self.assertIn("Nashik", masked["display_location"])
        self.assertNotIn("Plot 42/B", masked["display_location"])
        self.assertNotIn("20.1654", masked["display_location"])

        # String location sanitization
        masked_str = mask_location_for_public("Survey 19, Gat No 5, Dindori, Nashik, Maharashtra")
        self.assertEqual(masked_str["district"], "Nashik")
        self.assertEqual(masked_str["state"], "Maharashtra")
        self.assertNotIn("Survey 19", masked_str["display_location"])

if __name__ == "__main__":
    unittest.main()
