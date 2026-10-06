# REST API Documentation — KrushiSetu (कृषिसेतु)

## 1. Authentication & Security Headers

All protected endpoints require the standard JWT Bearer token format in the HTTP request headers:
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

---

## 2. API Endpoints Reference

### 🔐 Authentication (`/api/auth`)

| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/register` | Public | Register new Farmer or Buyer account with salted bcrypt password. |
| `POST` | `/api/auth/login` | Public | Authenticate credentials and receive signed 24h JWT token. |
| `GET` | `/api/auth/profile` | Authenticated | Retrieve authenticated user profile (excludes password hashes). |

---

### 🌱 Product Catalog & Marketplace (`/api/products`)

| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/products/` | Public | List active produce lots with optional filters (`crop`, `category`, `district`, `organic`, `max_price`). |
| `GET` | `/api/products/<id>` | Public | Get produce lot details with masked regional location. |
| `POST` | `/api/products/` | Farmer | Create new crop lot listing. |
| `PUT` | `/api/products/<id>` | Farmer (Owner) | Update existing crop lot listing. |
| `DELETE` | `/api/products/<id>` | Farmer (Owner) | Delete crop lot listing. |
| `GET` | `/api/products/my-products` | Farmer | List all harvest lots owned by the authenticated farmer. |

---

### 📦 Orders & Escrow (`/api/orders`)

| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/orders/` | Buyer | Place order for produce lot (verifies available stock server-side). |
| `GET` | `/api/orders/` | Authenticated | List orders associated with the caller (Farmers see incoming, Buyers see purchases). |
| `GET` | `/api/orders/<id>` | Participant | Retrieve single order details. |
| `PATCH` | `/api/orders/<id>/status` | Participant | Update order status (`Accepted`, `Shipped`, `Delivered`, `Cancelled`). |

---

### ⚡ Smart Selling Decision Support (`/api/smart-selling`)

| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/smart-selling/calculate` | Public/Demo | Multi-buyer Net Realization calculation with transparent step-by-step breakdown. |
| `GET` | `/api/smart-selling/farmer-summary` | Farmer | Consolidated AI summary (My Crops + Disease + Soil + Demand + Price + Opportunities). |
| `POST` | `/api/smart-selling/transport-estimate` | Public | Dedicated vehicle tariff and road freight calculator. |
| `GET` | `/api/smart-selling/vehicles` | Public | List supported vehicle fleet specifications and capacities. |

---

### 🔬 AI & Market Intelligence (`/api/ai`)

| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/ai/crop-doctor/diagnose` | Farmer | Upload leaf photo for plant disease diagnosis and treatment plan. |
| `GET` | `/api/ai/crop-doctor/history` | Farmer | Retrieve private historical leaf diagnosis scans. |
| `POST` | `/api/ai/soil/recommend` | Farmer | Calculate customized N-P-K fertilizer schedules based on soil test parameters. |
| `GET` | `/api/ai/market-intelligence/crops` | Public | List supported commodities and APMC market centers. |
| `GET` | `/api/ai/market-intelligence/forecast` | Public | Retrieve 7, 15, or 30-day demand and price predictions. |
| `GET` | `/api/ai/market-intelligence/model-info` | Public | Model transparency, evaluation metrics (MAE, RMSE), and privacy governance notes. |
