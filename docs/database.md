# Database Architecture — KrushiSetu (कृषिसेतु)

## 1. Overview
KrushiSetu utilizes MongoDB as its primary document store, taking advantage of flexible schemas for diverse agricultural produce, variable quality attributes, ML diagnostic payloads, and multi-variable price history.

---

## 2. Collections Schema Reference

### 1. `users`
Stores user identities, credentials, roles, and profile information.
```json
{
  "_id": "user_uuid",
  "id": "user_uuid",
  "full_name": "Ramesh Patil",
  "email": "ramesh@patil.com",
  "phone": "9876543210",
  "password_hash": "$2b$12$...",
  "role": "farmer", // 'farmer' | 'buyer' | 'admin'
  "state": "Maharashtra",
  "district": "Nashik",
  "village": "Pimpalgaon Baswant",
  "farm_size_acres": 12.5,
  "created_at": "2026-09-25T10:00:00Z"
}
```

### 2. `products`
Harvest lots listed by farmers.
```json
{
  "_id": "prod_uuid",
  "id": "prod_uuid",
  "farmer_id": "user_uuid",
  "farmer_name": "Ramesh Patil",
  "crop_name": "Tomato (Hybrid Red)",
  "category": "Vegetables",
  "quantity": 500.0,
  "unit": "kg",
  "price_per_unit": 28.5,
  "grade": "Grade A",
  "organic": true,
  "location": "Nashik, Maharashtra",
  "availability": "Available", // 'Available' | 'Sold Out' | 'Reserved'
  "images": ["/uploads/crops/crop_abc123.jpg"],
  "harvest_date": "2026-09-20",
  "created_at": "2026-09-25T10:00:00Z"
}
```

### 3. `orders`
Escrow-backed transactions between buyers and farmers.
```json
{
  "_id": "ORD-A1B2C3D4",
  "id": "ORD-A1B2C3D4",
  "buyer_id": "buyer_uuid",
  "buyer_name": "AgroFresh Mart",
  "farmer_id": "farmer_uuid",
  "farmer_name": "Ramesh Patil",
  "product_id": "prod_uuid",
  "product_name": "Tomato (Hybrid Red)",
  "quantity": 500.0,
  "price_per_unit": 28.5,
  "total_amount": 14250.0,
  "status": "Pending", // 'Pending' | 'Accepted' | 'Processing' | 'Shipped' | 'Delivered' | 'Completed' | 'Cancelled'
  "escrow_status": "Escrow Funds Locked (RBI Compliant)",
  "delivery_address": "Mumbai Logistics Terminal",
  "created_at": "2026-09-25T10:00:00Z"
}
```

### 4. `disease_results`
Private leaf diagnosis scan records for authenticated farmers.
```json
{
  "_id": "SCAN-9F8E7D",
  "farmer_id": "farmer_uuid",
  "crop": "Tomato",
  "image_url": "/uploads/disease_scans/scan_123.jpg",
  "diagnosis": {
    "status": "Disease Detected",
    "disease_name": "Tomato Early Blight",
    "pathogen": "Alternaria solani",
    "confidence_percent": 91.5,
    "severity": "Moderate",
    "immediate_action": "Spray Copper Oxychloride 50% WP (3g/L water)"
  },
  "created_at": "2026-09-25T10:00:00Z"
}
```

### 5. `soil_data`
Soil nutrient status and fertility recommendations.
```json
{
  "_id": "SOIL-5A4B3C",
  "farmer_id": "farmer_uuid",
  "crop": "Tomato",
  "analysis": {
    "soil_health_score": 82,
    "ph_status": "Neutral (6.8)",
    "nitrogen_status": "Low (210 kg/ha)",
    "phosphorus_status": "Medium (18 kg/ha)",
    "potassium_status": "High (290 kg/ha)",
    "fertilizer_recommendation": {
      "key_priority": "Nitrogen replenishment",
      "schedule": [
        { "stage": "Basal Application", "fertilizer": "DAP 50 kg + FYM 2 Tonnes" },
        { "stage": "Vegetative Growth", "fertilizer": "Urea 25 kg/acre" }
      ]
    }
  },
  "created_at": "2026-09-25T10:00:00Z"
}
```

### 6. Additional Collections
- `messages`: Private bidirectional messaging between transaction participants.
- `reviews`: Buyer-farmer counterparty ratings and feedback.
- `bids`: Smart Selling commercial offers.
- `price_history`: Historical mandi arrivals and modal price time-series.
- `demand_forecasts`: Cached regional AI demand predictions.
- `notifications`: User notification delivery log.

---

## 3. Data Isolation & Privacy Rules
- **Resource Ownership**: Endpoints query strictly with `{"farmer_id": current_user.id}` or `{"buyer_id": current_user.id}`.
- **Location Anonymization**: The database holds full profile details, but public API serializers pass locations through `mask_location_for_public()`.
