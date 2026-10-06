"""
KrushiSetu Demand Prediction ML Training Pipeline
Trains an XGBoost Tabular baseline regression model on engineered agro-economic features,
evaluates test holdout performance, ranks feature importances, and serializes the model.
"""

import os
import json
import datetime
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False
    from sklearn.ensemble import GradientBoostingRegressor

from ml.demand.data_pipeline import MarketDataPipeline

def train_demand_model(num_days: int = 730, output_dir: str = None) -> dict:
    """
    Executes the end-to-end ML training workflow:
    1. Ingestion / Groundtruth assembly
    2. Data cleaning & Missing value imputation
    3. Feature engineering (lags, seasonality, weather stress, arrivals)
    4. Chronological Train/Test split
    5. XGBoost model fitting
    6. Holdout Evaluation (MAE, RMSE, R²)
    7. Feature importance extraction
    8. Model persistence and metadata generation
    """
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), "models")
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 60)
    print("Starting KrushiSetu Demand Prediction ML Training...")
    print("=" * 60)

    # 1. Pipeline Execution
    pipeline = MarketDataPipeline()
    print("--> 1. Generating & Ingesting multi-source agricultural dataset...")
    raw_df = pipeline.generate_groundtruth_dataset(num_days=num_days)
    print(f"    Dataset loaded: {len(raw_df):,} total rows across {len(raw_df['crop'].unique())} commodities.")

    print("--> 2. Performing data cleaning & missing value imputation...")
    clean_df = pipeline.clean_and_impute_missing_values(raw_df)

    print("--> 3. Engineering predictive features (Lags, Seasonality, Volatility, Imbalance)...")
    feat_df = pipeline.engineer_features(clean_df)

    print("--> 4. Splitting chronologically (80% Train, 20% Test)...")
    X_train, X_test, y_train, y_test = pipeline.prepare_train_test_split(feat_df, test_ratio=0.2)
    print(f"    Train shape: {X_train.shape}, Test shape: {X_test.shape}")

    # 5. Model Initialization & Training
    print("--> 5. Fitting XGBoost Tabular Baseline...")
    if HAS_XGBOOST:
        model = xgb.XGBRegressor(
            n_estimators=180,
            learning_rate=0.06,
            max_depth=5,
            subsample=0.85,
            colsample_bytree=0.85,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train, y_train)
        model_type = "XGBoost Regressor (Gradient Boosted Trees)"
        
        # Extract feature importances
        raw_importances = model.feature_importances_
    else:
        model = GradientBoostingRegressor(
            n_estimators=150,
            learning_rate=0.06,
            max_depth=5,
            random_state=42
        )
        model.fit(X_train, y_train)
        model_type = "Scikit-Learn GradientBoostingRegressor"
        raw_importances = model.feature_importances_

    # 6. Evaluation
    print("--> 6. Evaluating model performance on test holdout...")
    y_pred = model.predict(X_test)
    mae = float(mean_absolute_error(y_test, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
    r2 = float(r2_score(y_test, y_pred))

    # Directional Trend Accuracy (Accuracy in classifying whether demand is increasing/decreasing vs median)
    median_demand = float(y_train.median())
    true_direction = (y_test >= median_demand).astype(int)
    pred_direction = (y_pred >= median_demand).astype(int)
    directional_accuracy = float(np.mean(true_direction == pred_direction) * 100.0)

    print(f"    MAE:  {mae:.3f}")
    print(f"    RMSE: {rmse:.3f}")
    print(f"    R² Score: {r2:.3f}")
    print(f"    Directional Trend Accuracy: {directional_accuracy:.1f}%")

    # Feature Importance Mapping
    feature_names = pipeline.feature_columns
    feature_importance_dict = {}
    for name, imp in zip(feature_names, raw_importances):
        feature_importance_dict[name] = round(float(imp) * 100.0, 2)
    
    # Sort descending
    sorted_factors = sorted(feature_importance_dict.items(), key=lambda x: x[1], reverse=True)
    top_factors = [{"feature": k, "importance_percent": v} for k, v in sorted_factors[:8]]

    # 7. Model Serialization
    model_filename = "demand_xgboost_model.joblib"
    model_path = os.path.join(output_dir, model_filename)
    joblib.dump(model, model_path)
    print(f"--> 7. Model binary saved to: {model_path}")

    metadata = {
        "model_name": "KrushiSetu Demand & Price Trend Predictor",
        "model_type": model_type,
        "version": "1.0.0",
        "trained_at": datetime.datetime.utcnow().isoformat() + "Z",
        "training_samples": len(X_train),
        "test_samples": len(X_test),
        "metrics": {
            "mae": round(mae, 3),
            "rmse": round(rmse, 3),
            "r2_score": round(r2, 3),
            "directional_trend_accuracy_percent": round(directional_accuracy, 1)
        },
        "feature_columns": feature_names,
        "top_influencing_factors": top_factors,
        "disclaimer": "Forecast — not a guarantee. Agricultural market conditions depend on dynamic weather events, transport logistics, and sudden government policy changes."
    }

    metadata_path = os.path.join(output_dir, "model_metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"--> 8. Model metadata saved to: {metadata_path}")
    print("=" * 60)
    print("[SUCCESS] Demand Prediction ML Pipeline training complete successfully!")
    print("=" * 60)

    return metadata

if __name__ == "__main__":
    train_demand_model()
