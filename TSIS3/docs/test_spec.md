# CFO Bot — Test Specification
## TSIS 3 | SDD Artifact

---

## 1. Overview

This document defines the test cases that verify the mathematical correctness of the CFO Bot cost calculation engine (`app.js`). Tests are organized by cloud component.

---

## 2. Baseline Inputs (Reference Set)

| Parameter | Value |
|---|---|
| MAU | 1,000 users |
| Messages/User/Day | 10 |
| Storage | 50 GB |
| Model | Gemini Flash |

**Derived:**
- `requests_per_month = 1000 × 10 × 30 = 300,000`

---

## 3. Unit Tests — Per Component

### 3.1 Compute (Cloud Run)

**Formula:** `requests × 2s × $0.000024`

| Test ID | MAU | Msgs/Day | Expected Requests | Expected Cost |
|---|---|---|---|---|
| TC-C01 | 1,000 | 10 | 300,000 | $14.40 |
| TC-C02 | 0 | 10 | 0 | $0.00 |
| TC-C03 | 100,000 | 100 | 300,000,000 | $14,400.00 |
| TC-C04 | 500 | 5 | 75,000 | $3.60 |

**Verification:** `300000 × 2 × 0.000024 = 14.40` ✓

---

### 3.2 Storage (Cloud Storage)

**Formula:** `storage_GB × $0.020`

| Test ID | Storage (GB) | Expected Cost |
|---|---|---|
| TC-S01 | 50 | $1.00 |
| TC-S02 | 1 | $0.02 |
| TC-S03 | 5,000 | $100.00 |
| TC-S04 | 0 | $0.00 |

**Verification:** `50 × 0.020 = 1.00` ✓

---

### 3.3 Bandwidth (Network Egress)

**Formula:** `(requests × 8KB) / (1024×1024) × $0.12`

| Test ID | Requests | Egress (GB) | Expected Cost |
|---|---|---|---|
| TC-B01 | 300,000 | 0.002289 | $0.000275 |
| TC-B02 | 0 | 0 | $0.00 |
| TC-B03 | 300,000,000 | 2,288.82 | $274.66 |

**Verification:** `(300000 × 8) / (1024×1024) × 0.12 ≈ $0.000275` ✓

---

### 3.4 Database (Firestore)

**Formula:**
- reads = requests × 3
- writes = requests × 2
- cost = (reads/100000 × $0.06) + (writes/100000 × $0.18)

| Test ID | Requests | Reads | Writes | Expected Cost |
|---|---|---|---|---|
| TC-D01 | 300,000 | 900,000 | 600,000 | $1.62 |
| TC-D02 | 0 | 0 | 0 | $0.00 |
| TC-D03 | 1,000,000 | 3,000,000 | 2,000,000 | $5.40 |

**Verification:** `(900000/100000×0.06) + (600000/100000×0.18) = 0.54 + 1.08 = 1.62` ✓

---

### 3.5 AI Model (Gemini API)

**Formula:** `requests × 500 tokens × (pricePerMToken / 1,000,000)`

| Test ID | Requests | Model | Tokens | Expected Cost |
|---|---|---|---|---|
| TC-AI01 | 300,000 | Flash ($0.075/M) | 150,000,000 | $11.25 |
| TC-AI02 | 300,000 | Pro ($3.50/M) | 150,000,000 | $525.00 |
| TC-AI03 | 300,000 | Ultra ($30.00/M) | 150,000,000 | $4,500.00 |
| TC-AI04 | 0 | Flash | 0 | $0.00 |

**Verification (AI01):** `300000 × 500 × (0.075/1000000) = 11.25` ✓

---

## 4. Integration Test — Total Cost (Baseline)

| Component | Cost |
|---|---|
| Compute | $14.40 |
| Storage | $1.00 |
| Bandwidth | ~$0.00 |
| Database | $1.62 |
| AI (Flash) | $11.25 |
| **Total** | **~$28.27** |

---

## 5. Edge Case Tests

| Test ID | Scenario | Expected Behavior |
|---|---|---|
| TC-E01 | MAU = 0 | All costs = $0.00, gauge shows 0% |
| TC-E02 | MAU = 100,000, msgs = 100, Ultra model | No NaN, no overflow, tier badge = Enterprise |
| TC-E03 | Storage = 1 GB | Storage cost = $0.02 |
| TC-E04 | Model switch Flash→Ultra | AI cost jumps 400×, total updates instantly |
| TC-E05 | Slider dragged rapidly | No lag, no race conditions, final value correct |

---

## 6. How to Run Tests

1. Open `index.html` in a Chrome browser
2. Set each slider input to the values in the table above
3. Compare displayed cost against expected values
4. Tolerance: ±$0.01 (rounding to 2 decimal places)
