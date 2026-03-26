# SSOT — CFO Bot: Cloud Economics Calculator
## System Specification v1.0 | TSIS 3

---

## 1. Scope

This document is the **Single Source of Truth (SSOT)** for the CFO Bot web application.  
The CFO Bot estimates the **monthly cloud infrastructure cost** of running a **ChatBot application** on **Google Cloud Platform (GCP)**, given user-supplied usage assumptions and AI model selection.

---

## 2. Supported Cloud Components

| # | Component | GCP Service | Billing Unit |
|---|---|---|---|
| 1 | Compute | Cloud Run | per vCPU-second × memory |
| 2 | Storage | Cloud Storage (Standard) | per GB/month |
| 3 | Bandwidth | Network Egress | per GB transferred |
| 4 | Database | Firestore (Native Mode) | per 100k reads/writes |
| 5 | AI Model | Vertex AI / Gemini API | per 1M input tokens |

---

## 3. Exact Cost Models

### 3.1 Compute (Cloud Run)

```
requests_per_month = MAU × messages_per_user_per_day × 30
compute_cost ($) = requests_per_month × avg_duration_sec × 0.000024
```
- avg_duration_sec = 2 (assumed per chat request)
- Price: $0.000024 per vCPU-second (Cloud Run gen2, 1 vCPU)

### 3.2 Storage (Cloud Storage)

```
storage_cost ($) = storage_GB × 0.020
```
- Price: $0.020 per GB/month (Standard class, us-central1)

### 3.3 Bandwidth (Network Egress)

```
egress_GB = requests_per_month × avg_response_kb / 1024 / 1024
bandwidth_cost ($) = egress_GB × 0.12
```
- avg_response_kb = 8 KB per response (assumed)
- Price: $0.12 per GB (internet egress, first 1 TB)

### 3.4 Database (Firestore)

```
reads_per_month  = requests_per_month × 3   (3 doc reads per message)
writes_per_month = requests_per_month × 2   (2 doc writes per message)
db_cost ($) = (reads_per_month / 100000 × 0.06) + (writes_per_month / 100000 × 0.18)
```
- Read price: $0.06 per 100,000 reads
- Write price: $0.18 per 100,000 writes

### 3.5 AI Model (Gemini API)

```
tokens_per_month = requests_per_month × avg_tokens_per_request
ai_cost ($) = tokens_per_month × price_per_token
```

| Model | Price per 1M tokens (input) | avg_tokens_per_request |
|---|---|---|
| Gemini Flash | $0.075 | 500 |
| Gemini Pro | $3.50 | 500 |
| Gemini Ultra | $30.00 | 500 |

### 3.6 Total Monthly Cost

```
total_cost = compute_cost + storage_cost + bandwidth_cost + db_cost + ai_cost
```

---

## 4. Input Parameters (UI Controls)

| Parameter | Type | Min | Max | Default | Unit |
|---|---|---|---|---|---|
| Monthly Active Users (MAU) | Slider | 0 | 100,000 | 1,000 | users |
| Messages per User per Day | Slider | 1 | 100 | 10 | messages |
| Storage | Slider | 1 | 5,000 | 50 | GB |
| AI Model Tier | Dropdown | — | — | Flash | — |

---

## 5. Architectural Constraints

- **Stateless compute**: All requests handled by Cloud Run (no persistent VMs)
- **Per-request billing**: Costs scale linearly with usage
- **No GPU needed**: Gemini API handles inference (managed service)
- **Free tier excluded**: All calculations assume paid tier for accuracy

## 6. UI/UX Requirements

- Single-page application (no page reloads)
- Real-time cost updates as sliders change
- Breakdown table showing cost per component
- Dark-mode premium design
- Mobile-responsive layout
- Export/print capability
