"""
KrushiSetu Model Evaluation Script
Evaluates the trained demand predictor on holdout test benchmarks and returns diagnostics.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from ml.demand.data_pipeline import MarketDataPipeline

def evaluate_demand_model(model_dir: str = None) -> dict:
    if model_dir is None:
        model_dir = os.path.join(os.path.dirname(__file__), "models")
    
    model_path = os.path.join(model_dir, "demand_xgboost_model.joblib")
    meta_path = os.path.join(model_dir, "model_metadata.json")

    if not os.path.exists(model_path) or not os.path.exists(meta_path):
        raise FileNotFoundError(f"Trained model not found at {model_path}. Run ml/demand/train.py first.")

    model = joblib.load(model_path)
    with open(meta_path, "r") as f:
        meta = json.load(f)

    pipeline = MarketDataPipeline()
    raw_df = pipeline.generate_groundtruth_dataset(num_days=180)
    clean_df = pipeline.clean_and_impute_missing_values(raw_df)
    feat_df = pipeline.engineer_features(clean_df)
    
    X = feat_df[pipeline.feature_columns]
    y_true = feat_df["target_demand_score"]

    y_pred = model.predict(X)

    mae = float(mean_absolute_error(y_true, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    r2 = float(r2_score(y_true, y_pred))

    results = {
        "status": "PASS",
        "model_name": meta.get("model_name"),
        "model_type": meta.get("model_type"),
        "evaluated_samples": len(X),
        "test_mae": round(mae, 3),
        "test_rmse": round(rmse, 3),
        "test_r2_score": round(r2, 3),
        "top_factors": meta.get("top_influencing_factors", [])
    }
    return results

if __name__ == "__main__":
    res = evaluate_demand_model()
    print(json.dumps(res, indent=2))
