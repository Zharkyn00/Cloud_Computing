/**
 * CFO Bot — Cloud Economics Calculator
 * TSIS 3 | Cost Engine (app.js)
 *
 * All formulas are defined in SSOT.md
 */

// ─── PRICING CONSTANTS (from SSOT) ───────────────────────────────────────────

const PRICING = {
  compute: {
    pricePerVCPUSec: 0.000024,   // Cloud Run gen2 per vCPU-second
    avgDurationSec: 2,            // average request duration (seconds)
  },
  storage: {
    pricePerGB: 0.020,            // GCS Standard, per GB/month
  },
  bandwidth: {
    pricePerGB: 0.12,             // Egress to internet, per GB
    avgResponseKB: 8,             // avg response size per request
  },
  database: {
    readPricePer100k: 0.06,       // Firestore reads
    writePricePer100k: 0.18,      // Firestore writes
    readsPerRequest: 3,
    writesPerRequest: 2,
  },
  models: {
    flash: {
      label: "Gemini Flash",
      pricePerMToken: 0.075,
      tokensPerRequest: 500,
    },
    pro: {
      label: "Gemini Pro",
      pricePerMToken: 3.50,
      tokensPerRequest: 500,
    },
    ultra: {
      label: "Gemini Ultra",
      pricePerMToken: 30.00,
      tokensPerRequest: 500,
    },
  },
};

// ─── COST CALCULATION FUNCTIONS ───────────────────────────────────────────────

/**
 * Calculate total monthly requests
 * @param {number} mau - Monthly Active Users
 * @param {number} messagesPerDay - Messages per user per day
 * @returns {number} Total monthly requests
 */
function calcRequestsPerMonth(mau, messagesPerDay) {
  return mau * messagesPerDay * 30;
}

/**
 * Compute cost (Cloud Run)
 * Formula: requests × avg_duration_sec × pricePerVCPUSec
 */
function calcComputeCost(requestsPerMonth) {
  const { pricePerVCPUSec, avgDurationSec } = PRICING.compute;
  return requestsPerMonth * avgDurationSec * pricePerVCPUSec;
}

/**
 * Storage cost (Cloud Storage)
 * Formula: storage_GB × pricePerGB
 */
function calcStorageCost(storageGB) {
  return storageGB * PRICING.storage.pricePerGB;
}

/**
 * Bandwidth cost (Network Egress)
 * Formula: (requests × avgResponseKB / 1024 / 1024) × pricePerGB
 */
function calcBandwidthCost(requestsPerMonth) {
  const { pricePerGB, avgResponseKB } = PRICING.bandwidth;
  const egressGB = (requestsPerMonth * avgResponseKB) / (1024 * 1024);
  return egressGB * pricePerGB;
}

/**
 * Database cost (Firestore)
 * Formula: (reads/100k × readRate) + (writes/100k × writeRate)
 */
function calcDatabaseCost(requestsPerMonth) {
  const { readPricePer100k, writePricePer100k, readsPerRequest, writesPerRequest } = PRICING.database;
  const reads = requestsPerMonth * readsPerRequest;
  const writes = requestsPerMonth * writesPerRequest;
  return (reads / 100000 * readPricePer100k) + (writes / 100000 * writePricePer100k);
}

/**
 * AI Model cost (Gemini API)
 * Formula: requests × tokensPerRequest × (pricePerMToken / 1,000,000)
 */
function calcAICost(requestsPerMonth, modelKey) {
  const model = PRICING.models[modelKey];
  const tokensPerMonth = requestsPerMonth * model.tokensPerRequest;
  return tokensPerMonth * (model.pricePerMToken / 1_000_000);
}

/**
 * Main calculation — returns full cost breakdown
 */
function calculateAll(mau, messagesPerDay, storageGB, modelKey) {
  const requests = calcRequestsPerMonth(mau, messagesPerDay);
  const compute   = calcComputeCost(requests);
  const storage   = calcStorageCost(storageGB);
  const bandwidth = calcBandwidthCost(requests);
  const database  = calcDatabaseCost(requests);
  const ai        = calcAICost(requests, modelKey);
  const total     = compute + storage + bandwidth + database + ai;

  return {
    requests,
    compute,
    storage,
    bandwidth,
    database,
    ai,
    total,
    modelLabel: PRICING.models[modelKey].label,
  };
}

// ─── UI HELPERS ───────────────────────────────────────────────────────────────

function fmt(value) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

function fmtNum(value) {
  return new Intl.NumberFormat("en-US").format(Math.round(value));
}

function getEl(id) {
  return document.getElementById(id);
}

// ─── REACTIVE UPDATES ────────────────────────────────────────────────────────

function updateDisplay() {
  const mau            = parseInt(getEl("mau").value, 10);
  const messagesPerDay = parseInt(getEl("msgs").value, 10);
  const storageGB      = parseInt(getEl("storage").value, 10);
  const modelKey       = getEl("model").value;

  // Sync slider value labels
  getEl("mau-val").textContent       = fmtNum(mau);
  getEl("msgs-val").textContent      = messagesPerDay;
  getEl("storage-val").textContent   = fmtNum(storageGB);

  const result = calculateAll(mau, messagesPerDay, storageGB, modelKey);

  // Update summary pills
  getEl("stat-requests").textContent = fmtNum(result.requests) + " req";
  getEl("stat-mau").textContent      = fmtNum(mau) + " MAU";
  getEl("stat-model").textContent    = result.modelLabel;

  // Update breakdown rows
  getEl("cost-compute").textContent   = fmt(result.compute);
  getEl("cost-storage").textContent   = fmt(result.storage);
  getEl("cost-bandwidth").textContent = fmt(result.bandwidth);
  getEl("cost-database").textContent  = fmt(result.database);
  getEl("cost-ai").textContent        = fmt(result.ai);
  getEl("cost-total").textContent     = fmt(result.total);

  // Update bar chart
  const components = [
    { id: "bar-compute",   value: result.compute },
    { id: "bar-storage",   value: result.storage },
    { id: "bar-bandwidth", value: result.bandwidth },
    { id: "bar-database",  value: result.database },
    { id: "bar-ai",        value: result.ai },
  ];

  const max = Math.max(...components.map(c => c.value), 0.01);
  components.forEach(({ id, value }) => {
    const pct = (value / max) * 100;
    getEl(id).style.width = pct + "%";
    getEl(id).setAttribute("title", fmt(value));
  });

  // Progress circle for total
  const maxExpected = 50000; // $50k is "100%" of the gauge
  const pct = Math.min((result.total / maxExpected) * 100, 100);
  const circle = document.querySelector(".gauge-ring");
  const circumference = 2 * Math.PI * 54; // r=54
  circle.style.strokeDashoffset = circumference - (pct / 100) * circumference;

  // Tier badge
  const badge = getEl("tier-badge");
  if (result.total < 500) {
    badge.textContent = "🟢 Startup Tier";
    badge.className = "tier-badge green";
  } else if (result.total < 5000) {
    badge.textContent = "🟡 Growth Tier";
    badge.className = "tier-badge yellow";
  } else if (result.total < 20000) {
    badge.textContent = "🟠 Scale Tier";
    badge.className = "tier-badge orange";
  } else {
    badge.textContent = "🔴 Enterprise Tier";
    badge.className = "tier-badge red";
  }
}

// ─── INIT ────────────────────────────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", () => {
  // Wire all inputs to updateDisplay
  ["mau", "msgs", "storage", "model"].forEach((id) => {
    const el = getEl(id);
    el.addEventListener("input", updateDisplay);
    el.addEventListener("change", updateDisplay);
  });

  // Print / Export button
  getEl("btn-export").addEventListener("click", () => {
    window.print();
  });

  // Initial render
  updateDisplay();
});
