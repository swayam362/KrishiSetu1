# System Architecture — KrushiSetu (कृषिसेतु)

## 1. High-Level Architecture Overview

KrushiSetu is an intelligent, privacy-first agricultural marketplace and decision-support ecosystem. It is structured as a decoupled three-tier architecture:

```
┌─────────────────────────────────────────────────────────────┐
│             Frontend Layer (Vanilla HTML5 / CSS3 / JS)       │
│  - Landing Page (index.html)                                │
│  - Farmer AI Dashboard (farmer-dashboard.html)              │
│  - Buyer Procurement Console (buyer-dashboard.html)         │
│  - Marketplace Trading Floor (marketplace.html)             │
│  - Smart Selling Decision Support Engine (smart-selling.html)│
│  - Crop Doctor Plant Pathology (crop-doctor.html)           │
│  - Market Intelligence & Trends (market-ai.html)            │
│  - Orders & Escrow Management (orders.html)                 │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTPS / REST JSON API
                               ▼
┌─────────────────────────────────────────────────────────────┐
│            Backend Application Layer (Python / Flask)       │
│  - Blueprint Routers (/api/auth, /api/products, /api/orders,│
│                       /api/ai, /api/smart-selling, etc.)    │
│  - Security & Privacy Middleware (JWT, RBAC, Masking)       │
│  - Transportation & Haulage Engine (Vehicle sizing, Tariffs)│
│  - Production Security Headers & Error Normalization        │
└───────────────┬─────────────────────────────┬───────────────┘
                │                             │
                ▼                             ▼
┌───────────────────────────────┐ ┌───────────────────────────┐
│     Database Layer (MongoDB)  │ │      AI / ML Layer        │
│  - MongoDB Atlas / Local      │ │  - Crop Doctor CNN Vision │
│  - 11 Data Collections        │ │  - XGBoost Demand Pipeline│
│  - Resilient In-Memory Driver │ │  - Price Forecasting Regr │
└───────────────────────────────┘ └───────────────────────────┘
```

---

## 2. Core Architectural Principles

1. **Clean Separation of Concerns**:
   - The frontend remains lightweight, responsive, and framework-free with vanilla JavaScript.
   - The backend exposes RESTful endpoints with standard JSON responses (`{ success: true, ... }`).
2. **Flagship USP — Smart Selling Decision Support**:
   - Rather than simply directing farmers to the highest nominal bidder, the system computes:
     $$\text{Expected Net Realization} = \text{Expected Revenue} - \text{Transportation Cost} - \text{Other Selling Costs}$$
   - Demonstrates why nearby buyers with lower nominal prices often yield higher actual profits in the farmer's bank account.
3. **Advisory Decision Support (Zero Automated Actions)**:
   - The platform never makes automated or irreversible trade commitments. The farmer retains 100% decision-making authority.
4. **Data Privacy & Minimization**:
   - Geographic coordinates and exact farm plot addresses are anonymized to regional/district boundaries on public trading floors.
5. **Resilient Dual-Mode Operation**:
   - Automatically connects to MongoDB Atlas or local MongoDB when available.
   - Falls back gracefully to an in-memory document database for self-contained demonstrations and automated testing.
