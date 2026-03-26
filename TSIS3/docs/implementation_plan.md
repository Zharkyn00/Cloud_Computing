# CFO Bot — Implementation Plan (SDD Artifact)
## TSIS 3 | Phase 2 Deliverable

---

## 1. Goal

Build and deploy a **CFO Bot** web application that estimates monthly GCP cloud costs for a ChatBot. The system uses a **Spec-Driven Development** approach where `SSOT.md` drives all calculation logic in `app.js`.

---

## 2. System Architecture

```
SSOT.md (specification)
    │
    ▼
app.js (cost engine)          ← implements all formulas from SSOT
    │
    ├── calcComputeCost()     Cloud Run billing model
    ├── calcStorageCost()     GCS Standard billing model
    ├── calcBandwidthCost()   Network Egress billing model
    ├── calcDatabaseCost()    Firestore reads/writes billing model
    ├── calcAICost()          Gemini token billing model
    └── calculateAll()        Aggregator → returns breakdown object
    │
    ▼
index.html + style.css        Single-page UI
    │
    ▼
Firebase Hosting              Public URL
```

---

## 3. Component Breakdown

### 3.1 SSOT.md
- Defines all supported cloud components
- Contains exact pricing constants (GCP list prices, 2024)
- UI/UX requirements and all mathematical formulas
- Serves as the contract between specification and implementation

### 3.2 app.js — Cost Engine
- All pricing constants are defined in a single `PRICING` object at the top
- Each cloud component has its own isolated pure function
- `calculateAll()` composes all functions and returns a single result object
- `updateDisplay()` reads DOM inputs, calls `calculateAll()`, and updates all DOM elements reactively
- Live slider gradient updates use CSS custom properties (`--pct`)

### 3.3 style.css — Design System
- CSS custom properties (tokens) for all colors, radii, shadows
- Google Fonts (Inter + JetBrains Mono)
- Glassmorphism cards with backdrop-filter
- Animated background grid
- Custom styled range sliders
- SVG gauge with animated stroke-dashoffset
- Responsive 2-column grid (collapses to 1 column on mobile)
- Print stylesheet for PDF export

### 3.4 index.html — Interface
- Semantic HTML5 structure
- ARIA labels on all interactive elements
- Three slider controls (MAU, Messages/Day, Storage)
- One model tier dropdown (Flash / Pro / Ultra)
- Cost breakdown table with animated bar fills per component
- SVG gauge (fills as cost approaches $50k/month)
- Tier badge (Startup / Growth / Scale / Enterprise)
- Export/Print button

### 3.5 Firebase Hosting
- `firebase.json` — points public directory to `.` (project root)
- `.firebaserc` — project alias (`tsis3-cfo-bot`)
- Markdown/docs files excluded from deployment
- Cache headers for JS/CSS assets (1 year)

---

## 4. Key Design Decisions

| Decision | Rationale |
|---|---|
| Pure JS (no framework) | No build step required — works offline, easy to audit |
| All formulas in PRICING constant | Single place to update prices, matches SSOT exactly |
| SVG gauge | Visually communicates scale without chart library |
| Tier badges | Makes costs interpretable for non-technical stakeholders |
| Print CSS | Enables real PDF export without third-party library |

---

## 5. Verification Checklist

- [ ] Open `index.html` — app loads with no console errors
- [ ] MAU slider 0 → all costs = $0.00
- [ ] MAU 1000, Msgs 10 → Total ≈ $28.27
- [ ] Model change Flash→Ultra → AI cost jumps 400×
- [ ] Gauge fills proportionally as MAU increases
- [ ] Print button opens browser print dialog
- [ ] All formulas match `test_spec.md` expected values
