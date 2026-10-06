import math
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime

# Config constants
SPEED_KMH = 25.0
BUFFER_MINUTES = 20.0
MAX_RADIUS_KM = 15.0

WEIGHT_URGENCY = 0.45
WEIGHT_PROXIMITY = 0.30
WEIGHT_CAPACITY_FIT = 0.25

assert math.isclose(WEIGHT_URGENCY + WEIGHT_PROXIMITY + WEIGHT_CAPACITY_FIT, 1.0), "Weights must sum to 1"
ENGINE_VERSION = "greedy_v1"

@dataclass
class ListingSnapshot:
    listing_id: str
    quantity_meals: int
    minutes_to_expiry: float
    latitude: float
    longitude: float

@dataclass
class NGOSnapshot:
    ngo_id: str
    total_capacity_meals: int
    current_capacity_meals: int
    latitude: float
    longitude: float
    verified: bool

@dataclass
class CandidateScore:
    ngo_id: str
    is_eligible: bool
    rejection_reason: Optional[str]
    distance_km: float
    travel_min: float
    margin_min: float
    urgency_score: float
    proximity_score: float
    capacity_score: float
    total_score: float
    weighted_contributions: Dict[str, float]

@dataclass
class AllocationDecision:
    listing_id: str
    winner_ngo_id: Optional[str]
    runner_up_ngo_id: Optional[str]
    winning_factors: List[str]
    evidence: Dict[str, Any]

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def compute_candidate_score(listing: ListingSnapshot, ngo: NGOSnapshot) -> CandidateScore:
    if not ngo.verified:
        return CandidateScore(
            ngo_id=ngo.ngo_id, is_eligible=False, rejection_reason="NGO is not verified",
            distance_km=0.0, travel_min=0.0, margin_min=0.0, urgency_score=0.0, proximity_score=0.0,
            capacity_score=0.0, total_score=0.0, weighted_contributions={}
        )
    
    if ngo.current_capacity_meals < listing.quantity_meals:
        return CandidateScore(
            ngo_id=ngo.ngo_id, is_eligible=False, 
            rejection_reason=f"Insufficient capacity ({ngo.current_capacity_meals} < {listing.quantity_meals})",
            distance_km=0.0, travel_min=0.0, margin_min=0.0, urgency_score=0.0, proximity_score=0.0,
            capacity_score=0.0, total_score=0.0, weighted_contributions={}
        )
    
    if listing.minutes_to_expiry <= 0:
        return CandidateScore(
            ngo_id=ngo.ngo_id, is_eligible=False, rejection_reason="Listing already expired",
            distance_km=0.0, travel_min=0.0, margin_min=0.0, urgency_score=0.0, proximity_score=0.0,
            capacity_score=0.0, total_score=0.0, weighted_contributions={}
        )

    distance_km = haversine_km(listing.latitude, listing.longitude, ngo.latitude, ngo.longitude)
    travel_min = (distance_km / SPEED_KMH) * 60.0

    margin = listing.minutes_to_expiry - (travel_min + BUFFER_MINUTES)
    if margin < 0:
        return CandidateScore(
            ngo_id=ngo.ngo_id, is_eligible=False, 
            rejection_reason=f"Infeasible transit time (travel+buffer={travel_min + BUFFER_MINUTES:.1f}m > expiry={listing.minutes_to_expiry:.1f}m)",
            distance_km=distance_km, travel_min=travel_min, margin_min=margin, urgency_score=0.0, proximity_score=0.0,
            capacity_score=0.0, total_score=0.0, weighted_contributions={}
        )
    
    # 1. Urgency Score: arrival safety margin. Cap at 120 minutes.
    urgency_score = min(1.0, margin / 120.0)

    # 2. Proximity Score: linear decay up to MAX_RADIUS_KM
    proximity_score = max(0.0, 1.0 - (distance_km / MAX_RADIUS_KM))

    # 3. Capacity Fit Score: prefers NGOs with MORE remaining capacity.
    capacity_score = min(1.0, (ngo.current_capacity_meals - listing.quantity_meals) / listing.quantity_meals)

    weighted_urgency = WEIGHT_URGENCY * urgency_score
    weighted_proximity = WEIGHT_PROXIMITY * proximity_score
    weighted_capacity = WEIGHT_CAPACITY_FIT * capacity_score

    total_score = weighted_urgency + weighted_proximity + weighted_capacity

    return CandidateScore(
        ngo_id=ngo.ngo_id,
        is_eligible=True,
        rejection_reason=None,
        distance_km=distance_km,
        travel_min=travel_min,
        margin_min=margin,
        urgency_score=urgency_score,
        proximity_score=proximity_score,
        capacity_score=capacity_score,
        total_score=total_score,
        weighted_contributions={
            "urgency": weighted_urgency,
            "proximity": weighted_proximity,
            "capacity": weighted_capacity
        }
    )

def allocate_single(listing: ListingSnapshot, ngos: List[NGOSnapshot]) -> AllocationDecision:
    candidates: List[CandidateScore] = []
    ngo_capacity_map = {n.ngo_id: n.current_capacity_meals for n in ngos}
    
    for ngo in ngos:
        candidates.append(compute_candidate_score(listing, ngo))
    
    eligible = [c for c in candidates if c.is_eligible]
    eligible.sort(key=lambda c: (-c.total_score, c.travel_min, c.ngo_id))
    
    winner_id = None
    runner_up_id = None
    winning_factors = []
    
    if eligible:
        winner = eligible[0]
        winner_id = winner.ngo_id
        if len(eligible) > 1:
            runner_up = eligible[1]
            runner_up_id = runner_up.ngo_id
            
            margins = {
                "urgency": winner.weighted_contributions["urgency"] - runner_up.weighted_contributions["urgency"],
                "proximity": winner.weighted_contributions["proximity"] - runner_up.weighted_contributions["proximity"],
                "capacity": winner.weighted_contributions["capacity"] - runner_up.weighted_contributions["capacity"],
            }
            max_margin = max(margins.values())
            if max_margin > 0:
                winning_factors = [k for k, v in margins.items() if math.isclose(v, max_margin, abs_tol=1e-5)]
            else:
                winning_factors = ["tie_breaker_logic"]
        else:
            winning_factors = ["only_eligible_candidate"]

    evidence = {
        "engine_version": ENGINE_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "weights": {
            "urgency": WEIGHT_URGENCY,
            "proximity": WEIGHT_PROXIMITY,
            "capacity_fit": WEIGHT_CAPACITY_FIT
        },
        "constants": {
            "speed_kmh": SPEED_KMH,
            "buffer_minutes": BUFFER_MINUTES,
            "max_radius_km": MAX_RADIUS_KM
        },
        "listing_snapshot": {
            "id": listing.listing_id,
            "quantity_meals": listing.quantity_meals,
            "minutes_to_expiry": listing.minutes_to_expiry,
            "lat": listing.latitude,
            "lon": listing.longitude
        },
        "winner_ngo_id": winner_id,
        "runner_up_ngo_id": runner_up_id,
        "winning_factors": winning_factors,
        "candidates": [
            {
                "ngo_id": c.ngo_id,
                "is_eligible": c.is_eligible,
                "rejection_reason": c.rejection_reason,
                "distance_km": round(c.distance_km, 3),
                "travel_min": round(c.travel_min, 3),
                "margin_min": round(c.margin_min, 3),
                "capacity_meals": ngo_capacity_map.get(c.ngo_id, 0),
                "sub_scores": {
                    "urgency": round(c.urgency_score, 4),
                    "proximity": round(c.proximity_score, 4),
                    "capacity": round(c.capacity_score, 4)
                },
                "weighted_contributions": {k: round(v, 4) for k, v in c.weighted_contributions.items()},
                "total_score": round(c.total_score, 4)
            } for c in candidates
        ]
    }

    return AllocationDecision(
        listing_id=listing.listing_id,
        winner_ngo_id=winner_id,
        runner_up_ngo_id=runner_up_id,
        winning_factors=winning_factors,
        evidence=evidence
    )

def allocate_batch(listings: List[ListingSnapshot], ngos: List[NGOSnapshot]) -> List[AllocationDecision]:
    sorted_listings = sorted(listings, key=lambda l: l.minutes_to_expiry)
    decisions = []
    ngo_map = {n.ngo_id: n for n in ngos}
    
    for listing in sorted_listings:
        decision = allocate_single(listing, list(ngo_map.values()))
        decisions.append(decision)
        if decision.winner_ngo_id:
            ngo_map[decision.winner_ngo_id].current_capacity_meals -= listing.quantity_meals
            
    return decisions

def reproduce_from_evidence(evidence: Dict[str, Any]) -> bool:
    """
    Re-evaluates the hard filters and re-calculates all scores from raw inputs to detect tampering.
    """
    listing_snap = evidence["listing_snapshot"]
    constants = evidence["constants"]
    weights = evidence["weights"]
    
    recomputed_candidates = []
    
    for c_ev in evidence["candidates"]:
        dist = c_ev["distance_km"]
        travel_min = (dist / constants["speed_kmh"]) * 60.0
        margin = listing_snap["minutes_to_expiry"] - (travel_min + constants["buffer_minutes"])
        
        is_eligible = True
        
        if c_ev["rejection_reason"] == "NGO is not verified":
            is_eligible = False
        elif c_ev["capacity_meals"] < listing_snap["quantity_meals"]:
            is_eligible = False
        elif margin < 0:
            is_eligible = False
            
        if not is_eligible:
            recomputed_candidates.append({
                "ngo_id": c_ev["ngo_id"],
                "is_eligible": False,
                "total_score": 0.0,
                "travel_min": travel_min
            })
            continue
            
        urg_score = min(1.0, margin / 120.0)
        prox_score = max(0.0, 1.0 - (dist / constants["max_radius_km"]))
        cap_score = min(1.0, (c_ev["capacity_meals"] - listing_snap["quantity_meals"]) / listing_snap["quantity_meals"])
        
        total = (weights["urgency"] * urg_score) + \
                (weights["proximity"] * prox_score) + \
                (weights["capacity_fit"] * cap_score)
                
        recomputed_candidates.append({
            "ngo_id": c_ev["ngo_id"],
            "is_eligible": True,
            "total_score": total,
            "travel_min": travel_min
        })
        
        # Detect tampering in the stored candidate's total score
        if c_ev["is_eligible"]:
            if not math.isclose(total, c_ev["total_score"], abs_tol=1e-3):
                return False
                
    # Re-rank candidates
    eligible = [c for c in recomputed_candidates if c["is_eligible"]]
    eligible.sort(key=lambda c: (-c["total_score"], c["travel_min"], c["ngo_id"]))
    
    winner_id = eligible[0]["ngo_id"] if eligible else None
    return winner_id == evidence["winner_ngo_id"]

