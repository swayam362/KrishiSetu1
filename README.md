# KrushiSetu (कृषिसेतु)
> **"Smart Farming • Better Markets • Better Decisions"**

An AI-powered agricultural marketplace and decision-support ecosystem connecting farmers directly with bulk buyers, food processing firms, retailers, and exporters while equipping them with predictive intelligence for crop health, soil nutrients, demand trends, price forecasting, transportation economics, and net profit optimization.

---

## 📋 Table of Contents
1. [Project Overview](#1-project-overview)
2. [Problem Statement](#2-problem-statement)
3. [Proposed Solution](#3-proposed-solution)
4. [Unique Selling Proposition (USP)](#4-unique-selling-proposition-usp)
5. [Key Features](#5-key-features)
6. [User Roles](#6-user-roles)
7. [Technology Stack](#7-technology-stack)
8. [System Architecture](#8-system-architecture)
9. [Database Architecture](#9-database-architecture)
10. [AI/ML Architecture](#10-aiml-architecture)
11. [Demand Prediction](#11-demand-prediction)
12. [Price Prediction](#12-price-prediction)
13. [Crop Doctor (Disease Diagnosis)](#13-crop-doctor-disease-diagnosis)
14. [Soil & Nutrient Recommendation](#14-soil--nutrient-recommendation)
15. [Smart Selling Decision Support](#15-smart-selling-decision-support)
16. [Transportation & Logistics Engine](#16-transportation--logistics-engine)
17. [Security Architecture](#17-security-architecture)
18. [Data Privacy Governance](#18-data-privacy-governance)
19. [Installation & Setup](#19-installation--setup)
20. [Environment Variables](#20-environment-variables)
21. [Running Locally](#21-running-locally)
22. [Automated Testing](#22-automated-testing)
23. [Production Deployment](#23-production-deployment)
24. [GitHub Quick Start](#24-github-quick-start)
25. [Demonstration Workflow](#25-demonstration-workflow)
26. [Future Improvements](#26-future-improvements)
27. [Honest Technical Limitations](#27-honest-technical-limitations)

---

## 1. Project Overview
**KrushiSetu (कृषिसेतु)** bridges the critical economic gap between Indian farmers and the modern supply chain. By merging a verified B2B trading floor with applied AI models (Plant Pathology Vision, Time-Series Price Forecasting, and Freight Tariff Optimization), KrushiSetu equips agricultural producers with transparent data to maximize their realized income.

---

## 2. Problem Statement
1. **Information Asymmetry**: Smallholder farmers rely on local middlemen who exploit price opacity and charge arbitrary commissions (typically 6.5%–10%).
2. **Deceptive Nominal Pricing**: High bid prices in distant city markets mislead farmers into expensive haulage trips where transportation costs, handling fees, and transit spoilage wipe out their profit margins.
3. **Late Disease Detection**: Crop diseases are often diagnosed only after visible blight destroys crop yield, costing farmers up to 40% of their seasonal harvest.
4. **Soil Degradation**: Blind application of synthetic fertilizers degrades soil quality and inflates input costs without improving yield quality.

---

## 3. Proposed Solution
KrushiSetu delivers an end-to-end web platform providing:
- **Direct Trading Floor**: Direct farmer-to-buyer transactions eliminating commission intermediaries.
- **Smart Selling Optimizer**: Net Realization decision support accounting for distance, road tariffs, and crop perishability.
- **Crop Doctor Vision**: Immediate leaf pathology diagnosis and actionable treatment steps.
- **Soil Fertility Calculator**: Tailored N-P-K nutrient schedules based on soil test parameters.
- **Market Intelligence**: 15-day regional price trends and demand forecasting.

---

## 4. Unique Selling Proposition (USP)
### Smart Selling Decision Support & Net Realization Optimizer
Unlike generic marketplaces that simply sort bids by highest price, KrushiSetu computes **Actual In-Pocket Profit**:

$$\text{Expected Net Realization} = \text{Expected Revenue} - \text{Transportation Cost} - \text{Other Selling Costs}$$

#### The Flagship Demonstration:
| Metric | Buyer A (Distant Urban Hub) | Buyer B (Local Processing Plant) |
| :--- | :--- | :--- |
| **Nominal Bid Price** | ₹30.00 / kg *(Looks higher)* | ₹28.00 / kg |
| **Harvest Quantity** | 500 kg | 500 kg |
| **Distance** | 110 km (Mumbai Hub) | 25 km (Nashik Hub) |
| **Transportation Freight** | **₹2,000** | **₹500** |
| **Other Costs / Handling** | ₹300 | ₹200 |
| **Gross Expected Revenue** | ₹15,000 | ₹14,000 |
| **Expected Net Realization** | **₹12,700** | **₹13,300 (+₹600 higher net in-pocket!)** |

> **Advisory Principle**: KrushiSetu never makes automated or irreversible trade decisions. The system provides transparent calculations; **the farmer retains 100% final authority**.

---

## 5. Key Features
- **Farmer Command Center**: Unified overview of listed lots, leaf scan alerts, soil status, price forecasts, and matched buyer offers.
- **Buyer Procurement Floor**: Instant produce filtering by commodity, grade, organic certification, and max price.
- **Escrow & Order Tracking**: Order state machine (`Pending` → `Accepted` → `Processing` → `Shipped` → `Delivered` → `Completed`).
- **Crop Doctor**: Fast image upload with instant plant disease diagnosis.
- **Soil & Nutrient Engine**: N-P-K deficiency analysis with ICAR-aligned organic and inorganic fertilization dosing.
- **Freight Sizing & Logistics**: Vehicle recommendation (Mini Truck, Pickup, 6-Tonne, Reefer) with calibrated per-km rates.

---

## 6. User Roles
1. **👨‍🌾 Farmer**: Lists crops, manages harvest lots, scans diseased leaves, calculates net realization, accepts buyer bids.
2. **🏢 Buyer**: Discovers produce, verifies grade specifications, locks escrow funds, places bulk orders, tracks shipments.
3. **🛡️ Admin**: Oversees platform health, monitors transactions, manages dispute resolution.

---

## 7. Technology Stack
- **Frontend**: HTML5, Vanilla CSS3 (Custom Design System), Modular JavaScript (ES6+), Font Awesome Icons, Chart.js.
- **Backend API**: Python 3.9+, Flask, Blueprint Routing, Gunicorn.
- **Database**: MongoDB (Atlas Cloud & Local) with resilient in-memory fallback.
- **Security**: JWT Authentication (HS256), Salted bcrypt password hashing, Location Privacy Masking Engine.
- **AI / ML**: MobileNetV2 (Computer Vision for Disease Diagnosis), XGBoost (Time-series Market Demand & Price Forecasting), Scikit-Learn, NumPy, Pandas.

---

## 8. System Architecture
```
[ Frontend: HTML5 / CSS3 / Vanilla JS ]
                   │
                   ▼ (HTTPS / REST JSON API)
[ Flask Backend Routers & Middleware ]
  ├── /api/auth (JWT & Role Guards)
  ├── /api/products (Produce Inventory)
  ├── /api/orders (Escrow & Order State Machine)
  ├── /api/smart-selling (Net Realization Optimizer)
  └── /api/ai (Crop Doctor, Soil Engine, Market Intelligence)
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
[ MongoDB Database ]   [ AI / ML Pipelines ]
```

---

## 9. Database Architecture
KrushiSetu utilizes 11 collections: `users`, `products`, `orders`, `disease_results`, `soil_data`, `messages`, `reviews`, `bids`, `price_history`, `demand_forecasts`, `notifications`. Refer to [`docs/database.md`](file:///c:/Users/SAINATH/OneDrive/Desktop/agri_finalmarket/docs/database.md) for full JSON schemas.

---

## 10. AI/ML Architecture
The platform integrates machine learning into operational workflows:
- **Vision Pipeline**: Real-time leaf pathology classification.
- **Forecasting Pipeline**: Autoregressive time-series feature engineering with rolling moving averages and weather/mandi arrival indicators.

---

## 11. Demand Prediction
- **Input Variables**: 7-day/14-day rolling price averages, market arrival volume trends, seasonal rainfall, regional festival intensity index.
- **Outputs**: Demand momentum (`High`, `Moderate`, `Low`) and 15-day trend outlook.
- **Safety Standard**: Explicitly labeled as *"Demand Forecast — not a guarantee"*.

---

## 12. Price Prediction
- **Engine**: Gradient boosted regression estimating modal market price intervals.
- **Output**: Expected price range (e.g. `₹27.00 – ₹31.00 / kg`).

---

## 13. Crop Doctor (Disease Diagnosis)
- **Crops Supported**: Tomato, Potato, Wheat, Onion, Cotton.
- **Outputs**: Disease name, botanical pathogen, confidence score (%), immediate organic remedies, and chemical fungicide dosages.
- **Safety Standard**: Labeled as *"Possible Diagnosis"* with advice to consult local KVK agronomists.

---

## 14. Soil & Nutrient Recommendation
- **Parameters**: Soil pH, Nitrogen, Phosphorus, Potassium, Organic Carbon.
- **Outputs**: Soil health score (0–100), primary deficiency alert, basal and vegetative fertilization schedule.

---

## 15. Smart Selling Decision Support
- Evaluates candidate buyer bids side-by-side.
- Computes vehicle freight, toll charges, packaging, mandi cess, and perishability allowance.
- Highlights the highest net profit opportunity while preserving the farmer's full autonomy to select any buyer.

---

## 16. Transportation & Logistics Engine
Includes vehicle fleet specifications:
- **Mini Truck (Tata Ace)**: 1,000 kg capacity • ₹22/km
- **Pickup Truck (Bolero)**: 2,500 kg capacity • ₹32/km
- **Medium Truck (Eicher 6-Tonne)**: 6,000 kg capacity • ₹48/km
- **Heavy Multi-Axle (16-Tonne)**: 16,000 kg capacity • ₹72/km
- **Reefer Cold-Chain**: 5,000 kg capacity • ₹60/km (+15% cooling surcharge)

---

## 17. Security Architecture
- **Passwords**: Salted bcrypt hashing (work factor 12).
- **Tokens**: Signed HMAC-SHA256 JWT tokens with 24-hour expiration.
- **Role Permissions**: Role-based access control (`@roles_required`) on all protected endpoints.
- **Resource Ownership**: Strict checks preventing users from modifying other users' listings or orders.
- **Headers**: `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`, `X-XSS-Protection`, `Referrer-Policy`.
- **Error Handling**: Global JSON error handlers with zero stack trace leakage.

---

## 18. Data Privacy Governance
- **Location Masking**: Exact survey numbers, street names, and postal PIN codes are withheld from public view; only District and State (e.g. *Nashik, Maharashtra*) are displayed.
- **Data Minimization**: Collects only information strictly needed for transaction fulfillment.
- **Confidentiality**: Private messages, leaf scan histories, and trade negotiations are isolated to authorized parties.

---

## 19. Installation & Setup

### Prerequisites
- Python 3.9 or higher
- Git

```bash
# Clone the repository
git clone https://github.com/your-username/KrushiSetu.git
cd KrushiSetu

# Create and activate virtual environment (optional but recommended)
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 20. Environment Variables
Copy the template to create your `.env` file:
```bash
cp .env.example .env
```
Configure:
- `SECRET_KEY`: Flask session security key
- `JWT_SECRET`: JWT token signature key
- `MONGODB_URI`: MongoDB connection string (local or Atlas)

*(Never commit your `.env` file to git)*

---

## 21. Running Locally
Start the backend server:
```bash
python backend/app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 22. Automated Testing
Run the complete 65-test automated test suite:
```bash
python -m unittest discover -s tests -v
```

---

## 23. Production Deployment
Refer to [`docs/deployment.md`](file:///c:/Users/SAINATH/OneDrive/Desktop/agri_finalmarket/docs/deployment.md) for Gunicorn, Docker, and NGINX SSL configuration templates.

---

## 24. GitHub Quick Start
```bash
# 1. Initialize Git repository
git init

# 2. Stage all files (respecting .gitignore)
git add .

# 3. Create initial commit
git commit -m "Initial KrushiSetu project"

# 4. Set main branch
git branch -M main

# 5. Add remote repository URL
git remote add origin https://github.com/your-username/KrushiSetu.git

# 6. Push to GitHub
git push -u origin main
```

---

## 25. Demonstration Workflow (19-Step Flow)
1. **Landing Page (`index.html`)**: View value proposition, features, and navigation.
2. **Farmer Registration (`register.html`)**: Register with location and farm details.
3. **Farmer Login (`login.html`)**: Authenticate and receive JWT token.
4. **Farmer Dashboard (`farmer-dashboard.html`)**: View KPI metrics and intelligence strip.
5. **Add Crop**: List a new lot (e.g. Tomato — 500 kg @ ₹28.5/kg).
6. **Marketplace (`marketplace.html`)**: View listed produce on public trading floor.
7. **Buyer Registration**: Register as an urban buyer / food processing company.
8. **Buyer Search**: Filter by commodity, grade, and max price.
9. **Buyer Order**: Place an escrow-backed order for 500 kg of Tomato.
10. **Farmer Acceptance (`orders.html`)**: Farmer reviews and accepts incoming order.
11. **Crop Doctor (`crop-doctor.html`)**: Upload leaf image and view disease diagnosis.
12. **Soil Analysis**: Enter N-P-K values and review soil health index.
13. **Nutrient Recommendation**: View personalized basal and top-dressing dosage schedule.
14. **Demand Forecast (`market-ai.html`)**: Inspect 15-day regional demand trends.
15. **Price Forecast**: View expected price range bands.
16. **Transportation Calculation**: Select vehicle and compute road freight cost.
17. **Smart Selling (`smart-selling.html`)**: Compare multiple buyer bids side-by-side.
18. **Net Realization**: Inspect step-by-step breakdown (Buyer B nets ₹13,300 vs Buyer A nets ₹12,700).
19. **Order Completion**: Track fulfillment status to final delivery and escrow release.

---

## 26. Future Improvements
- **Multilingual Voice Interface**: Regional voice prompts in Hindi, Marathi, Telugu, and Kannada for low-literacy farmers.
- **Satellite Soil Moisture Integration**: Automated Sentinel-2 NDVI vegetative index ingestion.
- **WhatsApp/SMS Dispatch Alerts**: Webhook notification integration for farmers without continuous internet access.

---

## 27. Honest Technical Limitations
- **Security Boundaries**: Local testing uses HTTP; production environments require reverse-proxy SSL termination (NGINX/Let's Encrypt).
- **ML Model Maturity**: The Crop Doctor vision model and XGBoost price forecaster are calibrated on benchmark datasets (PlantVillage & AGMARKNET); regional calibration with local field datasets is recommended before commercial deployment.
- **External Data Fallbacks**: When third-party weather or government APMC APIs are unreachable, the system uses regional historical benchmarks to maintain uptime.

---

*KrushiSetu (कृषिसेतु) — Built for resilient, transparent, and profitable Indian agriculture.*
