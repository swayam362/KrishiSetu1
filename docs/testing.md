# Testing Guide — KrushiSetu (कृषिसेतु)

## 1. Automated Test Suite Overview

KrushiSetu includes a 65-test automated test suite across 7 modules covering unit, integration, security, privacy, and adversarial cases.

| Test Module | Coverage Area | Test Count |
| :--- | :--- | :---: |
| [test_auth.py](file:///c:/Users/SAINATH/OneDrive/Desktop/agri_finalmarket/tests/test_auth.py) | User registration, bcrypt password hashing, JWT login, profile sanitization | 8 tests |
| [test_products.py](file:///c:/Users/SAINATH/OneDrive/Desktop/agri_finalmarket/tests/test_products.py) | Product creation, updates, deletes, ownership checks, marketplace filters | 8 tests |
| [test_orders_messages_reviews.py](file:///c:/Users/SAINATH/OneDrive/Desktop/agri_finalmarket/tests/test_orders_messages_reviews.py) | Order placement, stock deduction, state transitions, direct messages, ratings | 10 tests |
| [test_ai_modules.py](file:///c:/Users/SAINATH/OneDrive/Desktop/agri_finalmarket/tests/test_ai_modules.py) | Leaf image diagnostics, confidence metrics, soil nutrient schedules | 7 tests |
| [test_market_intelligence.py](file:///c:/Users/SAINATH/OneDrive/Desktop/agri_finalmarket/tests/test_market_intelligence.py) | Time-series features, XGBoost inference, weather/APMC fallbacks | 8 tests |
| [test_price_prediction_and_transport.py](file:///c:/Users/SAINATH/OneDrive/Desktop/agri_finalmarket/tests/test_price_prediction_and_transport.py) | Vehicle fleet tariffs, distance calculations, Smart Selling ranking | 12 tests |
| [test_security_privacy_negative.py](file:///c:/Users/SAINATH/OneDrive/Desktop/agri_finalmarket/tests/test_security_privacy_negative.py) | Adversarial payloads, NoSQL injection, role violations, location privacy, negative tests | 12 tests |

**Total Tests**: **65 / 65 Passing**

---

## 2. Running Automated Tests

Run the full test suite from the root directory:
```bash
python -m unittest discover -s tests -v
```

Run specific test files:
```bash
# Run security & negative tests
python -m unittest tests/test_security_privacy_negative.py

# Run market intelligence & demand forecasting tests
python -m unittest tests/test_market_intelligence.py

# Run smart selling & transport tests
python -m unittest tests/test_price_prediction_and_transport.py
```

---

## 3. Negative & Edge-Case Testing Scope
The test suite explicitly verifies that:
- Unauthorized requests without tokens receive `401 Unauthorized`.
- Wrong user roles (e.g. Buyer attempting to list a harvest) receive `403 Forbidden`.
- Negative prices, zero quantities, or excess order amounts receive `400 Bad Request`.
- Disallowed file types (e.g. `.php`, `.sh`) are rejected during leaf upload.
- Location strings with 6-digit postal PIN codes have numbers stripped to preserve privacy.
- AI predictions include required probabilistic disclaimers and do not claim 100% certainty.
