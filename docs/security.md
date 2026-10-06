# Security & Data Privacy Guide — KrushiSetu (कृषिसेतु)

## 1. Security Architecture & Controls

KrushiSetu implements defense-in-depth principles across the entire application stack:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Network & Transport Security                             │
│    - HTTPS / TLS 1.3 Encryption                             │
│    - Security Headers (HSTS, CSP, nosniff, SAMEORIGIN)      │
│    - CORS Restricted to Authorized API Endpoints            │
├─────────────────────────────────────────────────────────────┤
│ 2. Authentication & Session Management                      │
│    - Passwords Hashed with Salted bcrypt (Work Factor 12)   │
│    - HMAC-SHA256 JWT Access Tokens (24-Hour Expiration)     │
│    - Zero Plaintext Password Storage or Logging             │
├─────────────────────────────────────────────────────────────┤
│ 3. Authorization & Access Control (RBAC)                    │
│    - Role Enforcement (@roles_required for Farmer/Buyer)   │
│    - Strict Resource Ownership Checks (Edit/Delete crops)   │
│    - Private Message & Order Isolation                      │
├─────────────────────────────────────────────────────────────┤
│ 4. Input Validation & Injection Mitigation                  │
│    - Numeric Bounds & Type Coercion                         │
│    - NoSQL Operator Stripping (Removes leading '$')         │
│    - File Upload Verification (MIME, Extension, Safe UUID)  │
│    - Payload Size Ceiling (16 MB MAX_CONTENT_LENGTH)        │
├─────────────────────────────────────────────────────────────┤
│ 5. Data Privacy & Minimization                              │
│    - Location Masking (District/State level for public)     │
│    - Isolation of Farmer AI Diagnostics History             │
│    - Confidentiality of Counterparty Negotiations           │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Secure File Upload Pipeline
1. **Extension & MIME Validation**: Only `.jpg`, `.jpeg`, `.png`, and `.webp` allowed.
2. **File Size Check**: Individual files capped at 5 MB; request payload capped at 16 MB.
3. **Safe Randomized Naming**: User filenames are discarded; unique random UUIDs (`crop_<uuid>.jpg`) are assigned.
4. **Isolated Directory Serving**: Uploads served strictly from `/uploads/` with path traversal normalization (`os.path.normpath`).

---

## 3. Location Privacy Governance
To prevent harassment, theft, and unwarranted commercial solicitation, the public marketplace never exposes:
- Survey numbers, Khasra numbers, or street addresses.
- Exact GPS coordinates or farm plot boundaries.
- Full 6-digit postal PIN codes.

All public endpoints serialize geographic identifiers through `mask_location_for_public()`, displaying solely district and state (e.g. *Nashik, Maharashtra*).

---

## 4. Known Limitations & Production Readiness Roadmap
- **SSL Termination**: Local development runs on HTTP/development Flask. Production requires an NGINX reverse proxy with Let's Encrypt SSL certificates.
- **Distributed Token Invalidation**: In multi-node horizontal deployments, token blocklists should be stored in a centralized Redis cache.
- **WAF Integration**: Cloudflare or AWS WAF should be placed in front of public traffic for DDoS mitigation.
