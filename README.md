# ReServe — Predictive, Perishability-Aware Food Rescue Platform

## Overview
Existing food-donation platforms (e.g. Feeding India) are reactive: a donor posts surplus food, and it goes to whichever NGO claims it first. **ReServe** is different:
1. **Predicts surplus** before it happens using historical listing patterns.
2. **Optimally allocates surplus** under real time pressure (factoring in expiry window, NGO travel time, and remaining storage capacity) instead of first-come-first-served.
3. **Explains every allocation decision** in plain language with reproducible, stored evidence JSON so NGOs understand why they did or didn't receive a listing.

---

## Architecture: Modular Monolith
To preserve team velocity and zero operational complexity, ReServe is intentionally built as a **modular monolith** with clean internal boundaries:
- **`app/api/endpoints/auth.py`**: Authentication & persona session management.
- **`app/api/endpoints/listings.py`**: Listing creation, live expiry tracking, and status lifecycle.
- **`app/api/endpoints/forecasting.py`**: ML-driven surplus forecasting.
- **`app/api/endpoints/allocation.py`**: Multi-factor perishability-aware greedy allocator.
- **`app/api/endpoints/explanation.py`**: Audit evidence & plain-English explanation engine.

---

## Allocation Formula & Academic Defense Rationale

The matching engine computes a deterministic multi-criteria score $\in [0, 1]$ for every candidate NGO:

$$\text{Score}(L, N) = w_1 \cdot \text{Urgency}(t_{\text{expiry}}) + w_2 \cdot \text{Proximity}(d_{\text{km}}) + w_3 \cdot \text{CapacityFit}(c_{\text{rem}}, q)$$

Subject to hard feasibility constraints:
1. **Perishability Feasibility Guard**: $\text{Estimated Transit Time} + \tau_{\text{buffer}} \le t_{\text{expiry}}$. If transit $+ 20\text{ min inspection buffer} > \text{time remaining}$, the score is zeroed out (infeasible match).
2. **Capacity Feasibility Guard**: The candidate NGO must have remaining storage/distribution capacity $\ge q$ (or a minimum configurable partial fulfillment threshold).

### Academic Justification of Weights ($w_1 = 0.45, w_2 = 0.30, w_3 = 0.25$):
- **Why Urgency has Highest Weight ($w_1 = 0.45$)**: 
  Food waste in rescue logistics is an **irreversible, time-decaying perishable asset**. If an NGO is 5 minutes closer but receives food with 8 hours of remaining shelf life while another batch expires in 45 minutes, prioritizing proximity over perishability leads to catastrophic waste at the source. Thus, the temporal decay factor is granted primary weighting ($45\%$).
- **Why Proximity has Secondary Weight ($w_2 = 0.30$)**: 
  NGOs operate with volunteer labor and limited fuel budgets. Minimizing dispatch distance reduces volunteer burnout, operational costs, and vehicular carbon emissions, while maximizing the probability of on-time arrival before the decay window closes.
- **Why Capacity has Tertiary Weight ($w_3 = 0.25$)**: 
  Capacity fit ensures that food is routed to shelters capable of immediate refrigerated storage or prompt redistribution. A shelter that cannot store or distribute 100 meals will cause downstream secondary spoilage. It receives $25\%$ because it is also guarded as a hard filter (ineligible if capacity is zero).

### Distance Calculation Caveat & Academic Disclosure:
> **Explicit Engineering Disclosure for Viva/Defense**: 
> Proximity is computed using the spherical **Haversine formula** (great-circle distance) with an assumed urban congestion speed factor ($25\text{ km/h}$). This is a **zero-cost algorithmic approximation** of transit distance and time. It does **not** query commercial paid routing APIs (e.g. Google Maps Distance Matrix API) in order to maintain zero external financial dependencies and zero rate-limiting during load testing. In production deployment, a real road-network routing matrix (e.g. OSRM or OpenRouteService) can replace this component seamlessly.

### Algorithmic Optimization Roadmap:
The baseline engine executes as a **stateless greedy heuristic** ($O(N \log N)$ sorting over $N$ verified NGOs) designed for sub-millisecond dispatch under high request concurrency. In the codebase, clear extension points are marked where a multi-listing global assignment solver using **Mixed-Integer Linear Programming (MILP / PuLP)** can batch-optimize globally across concurrent simultaneous listings.

---

## Data Provenance Disclosure
> **Honest Disclosure**: Real-world commercial restaurant food waste logs are not publicly published due to proprietary liability. All historical listing datasets used for training the forecasting model in this repository are **synthetically generated** with realistic seasonalities (day-of-week surges, weather variations, holiday spikes). No synthetic data is represented as genuine donor logs.

---

## Local Development Quickstart

```bash
# 1. Clone repository & navigate to reserve
cd reserve

# 2. Launch complete stack via Docker Compose
docker compose up --build

# 3. Access interfaces:
# - Frontend: http://localhost:5173
# - FastAPI Swagger Docs: http://localhost:8000/docs
# - System Health Check: http://localhost:8000/health
```

---

---

### Implementation Notes for Milestone 2
- **Urgency (0.45)**: Implemented as arrival safety margin `min(1.0, (expiry - (travel_time + 20)) / 120.0)`. High score = safe margin.
- **Proximity (0.30)**: Linear decay `max(0, 1.0 - distance_km / 15.0)`.
- **Capacity (0.25)**: `min(1.0, (available_capacity - quantity) / quantity)`. More remaining capacity = higher score.