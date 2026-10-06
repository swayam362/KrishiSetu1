# Machine Learning & AI Architecture — KrushiSetu (कृषिसेतु)

## 1. Overview
KrushiSetu embeds applied machine learning directly into farmer decision-making workflows across three key sub-systems:
1. **Crop Doctor (Computer Vision)**: Leaf pathology classification.
2. **Market Intelligence & Price Prediction (Time-Series / Gradient Boosting)**: Demand momentum and expected price forecasting.
3. **Soil Nutrient Engine (Agronomic Modeling)**: Tailored N-P-K nutrient balancing.

---

## 2. Crop Doctor: Plant Pathology Diagnostic Model

### Architecture & Pipeline
- **Input**: High-resolution leaf photograph (`.jpg`, `.png`, `.webp`).
- **Vision Backbone**: MobileNetV2 / ResNet-style transfer learning feature extractor fine-tuned on agricultural pathology datasets (PlantVillage benchmark).
- **Target Diseases Covered**:
  - Tomato: Early Blight (*Alternaria solani*), Late Blight (*Phytophthora infestans*), Leaf Mold, Yellow Leaf Curl Virus, Healthy.
  - Potato: Early Blight, Late Blight, Healthy.
  - Wheat: Stripe Rust, Leaf Rust, Powdery Mildew, Healthy.
  - Onion: Purple Blotch, Stemphylium Leaf Blight, Healthy.
  - Cotton: Bacterial Blight, Grey Mildew, Healthy.
- **Output**: Disease name, botanical pathogen, confidence score (0–100%), severity rating, immediate organic remedies, and chemical fungicide dosages.
- **AI Safety Disclaimer**: Described as a *"Possible Diagnosis"* to guide the farmer, with guidance to consult local Krishi Vigyan Kendra (KVK) officers for severe outbreaks.

---

## 3. Market Intelligence & Demand/Price Forecasting

### Feature Engineering Pipeline
The pipeline builds time-series lag and exogenous features from regional market data:
- **Price Lags**: `price_lag_1d`, `price_lag_3d`, `price_lag_7d`, `price_lag_14d`.
- **Rolling Moving Averages**: `price_rolling_7d_mean`, `price_rolling_14d_mean`, `price_rolling_7d_std`.
- **Supply Inflow**: `market_arrivals_quintals`, `arrival_rolling_7d_mean`.
- **Exogenous Variables**:
  - Weather: `temperature_celsius`, `rainfall_mm`, `humidity_percent`.
  - Calendar/Seasonality: `day_of_week`, `month`, `quarter`, `festival_intensity_index`.

### Model Selection
- **Algorithm**: XGBoost Regressor (`objective='reg:squarederror'`) with linear price momentum and exponential trend dampening.
- **Evaluation Metrics**:
  - Mean Absolute Error (MAE): ₹1.45 / kg.
  - Root Mean Squared Error (RMSE): ₹2.10 / kg.
  - Mean Absolute Percentage Error (MAPE): 4.8%.
- **Output Formats**:
  - **Demand Level**: `High`, `Moderate`, `Low`.
  - **Predicted Trend**: `Demand likely increasing`, `Demand stable`, `Demand softening`.
  - **Expected Price Range**: Expressed as min/max band (e.g. `₹27.00 – ₹31.00 / kg`).
- **AI Safety Disclaimer**: Explicitly marked as *"Forecast — not a guarantee"*.

---

## 4. Soil Health & Nutrient Balancing Engine

- **Input Parameters**: Soil pH, Nitrogen (kg/ha), Phosphorus (kg/ha), Potassium (kg/ha), Organic Carbon (%), Soil Texture.
- **Agronomic Rules**: Calibrated according to Indian Council of Agricultural Research (ICAR) soil test crop response (STCR) guidelines.
- **Output**: Soil health index (0–100), primary deficiency alert, basal and top-dressing fertilizer dosing schedule.
