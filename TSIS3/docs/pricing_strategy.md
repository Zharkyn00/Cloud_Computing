# CFO Bot — Pricing Strategy Document
## TSIS 3 | Phase 4 Business Justification

---

## Executive Summary

This document justifies the cloud architecture decisions made for the **ChatBot application** based on cost modeling outputs from the CFO Bot calculator. The selected GCP stack is optimized for **cost-efficiency at scale** while maintaining **enterprise-grade reliability**.

---

## 1. Architecture Decisions & Justification

### 1.1 Compute: Cloud Run (Serverless)

**Decision:** Use Cloud Run instead of GCE (virtual machines) or GKE (Kubernetes).

| Option | Monthly Cost (1k MAU) | Monthly Cost (50k MAU) |
|---|---|---|
| Cloud Run (serverless) | ~$14 | ~$720 |
| GCE e2-medium (always-on) | ~$25 flat | ~$25 flat |
| GKE (2-node cluster) | ~$150 flat | ~$150 flat |

**Justification:**
- At **< 5,000 MAU**, Cloud Run costs less than any always-on VM
- At **> 5,000 MAU**, Cloud Run scales automatically — no manual capacity planning
- Zero cost when idle (no requests = no charges)
- **ChatBots are bursty by nature** — serverless is the ideal billing model

> **Conclusion:** Cloud Run is the optimal choice for all growth stages of a ChatBot.

---

### 1.2 AI Model: Tier Selection Strategy

**The AI model cost dominates at scale.** Model selection is the most critical financial decision.

| MAU | Flash Cost | Pro Cost | Ultra Cost | Recommended |
|---|---|---|---|---|
| 1,000 | $11.25 | $525 | $4,500 | Flash |
| 10,000 | $112.50 | $5,250 | $45,000 | Flash / Pro |
| 50,000 | $562.50 | $26,250 | $225,000 | Flash |
| 100,000 | $1,125 | $52,500 | $450,000 | Flash |

**Recommended strategy:**
1. **Launch phase (0–10k MAU):** Gemini Flash exclusively — high quality at minimal cost
2. **Growth phase (10k–50k MAU):** Flash for 90% of traffic, Pro only for complex queries (hybrid routing)
3. **Enterprise phase (50k+ MAU):** Negotiate committed-use discount with Google; explore fine-tuned Flash

> **Switching from Flash to Pro at 50k MAU increases AI costs by 46.7× ($562 → $26,250).**

---

### 1.3 Database: Firestore vs. Cloud SQL

**Decision:** Cloud Firestore (NoSQL) over Cloud SQL (PostgreSQL/MySQL).

| Criterion | Firestore | Cloud SQL |
|---|---|---|
| Cost at 1k MAU | ~$1.62/mo | ~$25/mo (min instance) |
| Cost at 100k MAU | ~$162/mo | ~$250–500/mo |
| Scaling | Auto | Manual |
| Chat data fit | ✅ Document model perfect | ⚠️ Requires schema design |

**Justification:**
- Chat history is naturally document-structured (user → session → messages)
- Firestore has **no minimum instance cost** — ideal for startups
- Real-time listeners built-in — useful for live chat UI

---

### 1.4 Storage: Cloud Storage Standard

**Decision:** GCS Standard class for all user/media storage.

- $0.020/GB/month is the lowest-cost option for hot data
- Coldline ($0.004/GB) not suitable — chat media needs immediate access
- At 50 GB: only **$1.00/month** — effectively negligible

---

## 2. Cost Scenarios Summary

| Scenario | MAU | Messages/Day | Model | Est. Monthly Cost |
|---|---|---|---|---|
| MVP / Pilot | 100 | 5 | Flash | ~$3 |
| Startup Launch | 1,000 | 10 | Flash | ~$28 |
| Early Growth | 10,000 | 15 | Flash | ~$140 |
| Scaling | 50,000 | 20 | Flash | ~$560 |
| Enterprise | 100,000 | 30 | Flash | ~$1,700 |
| Enterprise (Pro) | 100,000 | 30 | Pro | ~$53,000 |

---

## 3. Break-Even & Pricing Recommendation

**SaaS Pricing Model:**

| Tier | Price/User/Month | MAU Needed to Break Even |
|---|---|---|
| Free | $0 | — (loss-leader) |
| Basic ($5/mo) | $5 | 6 users (at 1k MAU scale) |
| Pro ($15/mo) | $15 | 2 users |
| Enterprise | Custom | Immediate profit |

**Recommendation:** Launch at **$9.99/user/month**. At 1,000 MAU, this generates **$9,990/month** revenue against **~$28/month** cloud cost — a **>350× gross margin on infrastructure**.

> The primary cost driver is not infrastructure — it is AI model tokens. A hybrid Flash/Pro routing strategy (using Flash for 90% of queries) can reduce AI costs by up to 40% with minimal quality loss.

---

## 4. Conclusion

The selected GCP architecture (Cloud Run + Firestore + GCS + Gemini Flash) is:
- ✅ **Cost-optimal** for a ChatBot at all growth stages
- ✅ **Fully serverless** — no DevOps overhead
- ✅ **Scalable** from 100 to 1,000,000 users without re-architecture
- ✅ **Firebase-deployable** in minutes

The CFO Bot calculator validates that our ChatBot can achieve a **>95% gross margin** on cloud infrastructure at any scale when using Gemini Flash, making it an extremely defensible SaaS business.
