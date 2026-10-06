"""
Automated Test Suite for KrushiSetu Market Intelligence & Demand Prediction System
Tests Data Pipeline, XGBoost Inference, External Service Security, Resilience,
Privacy Governance, and Backend API Endpoints.
"""

import os
import sys
import json
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app import create_app
from ml.demand.data_pipeline import MarketDataPipeline, SUPPORTED_CROPS, SUPPORTED_LOCATIONS
from ml.demand.predict import DemandPredictor, get_demand_predictor
from ml.demand.external.external_services import ExternalServiceManager, get_external_service_manager

class TestMarketIntelligenceSystem(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.pipeline = MarketDataPipeline()
        self.predictor = get_demand_predictor()
        self.service_mgr = get_external_service_manager()

    def test_supported_crops_and_locations(self):
        """Test baseline agricultural entities are registered and structured."""
        self.assertGreaterEqual(len(SUPPORTED_CROPS), 10)
        self.assertIn("Tomato", SUPPORTED_CROPS)
        self.assertIn("Wheat", SUPPORTED_CROPS)
        self.assertIn("Onion", SUPPORTED_CROPS)
        self.assertIn("Cotton", SUPPORTED_CROPS)

        cities = [loc["city"] for loc in SUPPORTED_LOCATIONS]
        self.assertIn("Pune", cities)
        self.assertIn("Nashik", cities)
        self.assertIn("Lasalgaon", cities)
        self.assertIn("Indore", cities)

    def test_data_pipeline_feature_engineering(self):
        """Test pipeline generates groundtruth, imputes missing values, and engineers lag features."""
        raw_df = self.pipeline.generate_groundtruth_dataset(num_days=60)
        self.assertGreater(len(raw_df), 1000)
        self.assertIn("modal_price_per_kg", raw_df.columns)
        self.assertIn("market_arrivals_quintals", raw_df.columns)
        self.assertIn("festival_intensity", raw_df.columns)

        clean_df = self.pipeline.clean_and_impute_missing_values(raw_df)
        self.assertEqual(clean_df.isnull().sum().sum(), 0)

        feat_df = self.pipeline.engineer_features(clean_df)
        for col in self.pipeline.feature_columns:
            self.assertIn(col, feat_df.columns)

        X_train, X_test, y_train, y_test = self.pipeline.prepare_train_test_split(feat_df, test_ratio=0.2)
        self.assertEqual(len(X_train) + len(X_test), len(feat_df))
        self.assertEqual(X_train.shape[1], len(self.pipeline.feature_columns))

    def test_external_services_resilience_and_benchmarks(self):
        """Test external weather, market, and distance services operate with robust fallbacks."""
        # 1. Weather fallback
        weather = self.service_mgr.get_weather("Pune")
        self.assertIn("temperature", weather)
        self.assertIn("rainfall", weather)
        self.assertIn("humidity", weather)
        self.assertGreaterEqual(weather["temperature"], 10.0)

        # 2. Market APMC benchmark
        market_data = self.service_mgr.get_market_data("Tomato", "Pune")
        self.assertIn("modal_price_per_kg", market_data)
        self.assertIn("arrivals_quintals", market_data)
        self.assertGreater(market_data["modal_price_per_kg"], 0)

        # 3. Distance & Transit calculation
        dist_info = self.service_mgr.calculate_distance_and_transit("Nashik", "Mumbai")
        self.assertIn("distance_km", dist_info)
        self.assertIn("transit_hours", dist_info)
        self.assertGreater(dist_info["distance_km"], 50.0)

    def test_demand_predictor_inference_tomato_pune(self):
        """Test demand predictor returns expected outputs for Tomato in Pune over Next 7 days."""
        result = self.predictor.predict_demand(
            crop="Tomato",
            location="Pune",
            forecast_period="Next 7 days"
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["crop"], "Tomato")
        self.assertIn("Pune", result["location"])
        self.assertEqual(result["forecast_period"], "Next 7 days")
        self.assertIn("current_demand_level", result)
        self.assertIn("predicted_trend", result)
        self.assertIn("confidence_percent", result)
        self.assertIn("uncertainty", result)
        self.assertIn("important_factors", result)
        self.assertTrue(len(result["important_factors"]) > 0)
        self.assertIn("Forecast — not a guarantee.", result["disclaimer"])
        self.assertIn("chart_data", result)
        self.assertTrue(len(result["chart_data"]["history"]) > 20)
        self.assertTrue(len(result["chart_data"]["forecast"]) >= 7)

    def test_api_endpoint_crops(self):
        """Test GET /api/ai/market-intelligence/crops."""
        res = self.client.get("/api/ai/market-intelligence/crops")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertTrue(len(data["crops"]) >= 10)
        self.assertTrue(len(data["locations"]) >= 10)

    def test_api_endpoint_forecast_get_and_post(self):
        """Test GET and POST /api/ai/market-intelligence/forecast."""
        # GET request
        res_get = self.client.get("/api/ai/market-intelligence/forecast?crop=Onion&location=Nashik&period=Next 15 days")
        self.assertEqual(res_get.status_code, 200)
        data_get = res_get.get_json()
        self.assertTrue(data_get["success"])
        self.assertEqual(data_get["crop"], "Onion")
        self.assertIn("Nashik", data_get["location"])
        self.assertEqual(data_get["forecast_period"], "Next 15 days")
        self.assertIn("disclaimer", data_get)

        # POST request
        payload = {
            "crop": "Wheat",
            "location": "Indore",
            "period": "Next 30 days"
        }
        res_post = self.client.post("/api/ai/market-intelligence/forecast", json=payload)
        self.assertEqual(res_post.status_code, 200)
        data_post = res_post.get_json()
        self.assertTrue(data_post["success"])
        self.assertEqual(data_post["crop"], "Wheat")
        self.assertIn("Indore", data_post["location"])

    def test_api_endpoint_model_info_and_privacy_governance(self):
        """Test GET /api/ai/market-intelligence/model-info for transparency and privacy guarantees."""
        res = self.client.get("/api/ai/market-intelligence/model-info")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("model_type", data)
        self.assertIn("metrics", data)
        self.assertIn("privacy_governance", data)
        self.assertIn("pii_isolation", data["privacy_governance"])
        self.assertIn("database_separation", data["privacy_governance"])
        self.assertIn("disclaimer", data)

    def test_backward_compatibility_market_forecast(self):
        """Test backward-compatible /api/ai/market-forecast endpoint."""
        res = self.client.get("/api/ai/market-forecast?commodity=soybean")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("current_avg_mandi_price", data)
        self.assertIn("predicted_15_days", data)
        self.assertIn("demand_trend", data)
        self.assertIn("Forecast — not a guarantee.", data["disclaimer"])

if __name__ == "__main__":
    unittest.main()
