import pytest
from app.services.allocation_engine import (
    haversine_km,
    ListingSnapshot,
    NGOSnapshot,
    allocate_single,
    allocate_batch,
    reproduce_from_evidence,
    SPEED_KMH,
    BUFFER_MINUTES
)

def test_haversine_sanity():
    # Roughly Delhi to Gurugram is ~30km
    lat1, lon1 = 28.6139, 77.2090
    lat2, lon2 = 28.4595, 77.0266
    dist = haversine_km(lat1, lon1, lat2, lon2)
    assert 20 < dist < 40

def test_feasibility_rejection():
    listing = ListingSnapshot("l1", 100, 30, 28.6, 77.2)
    ngo = NGOSnapshot("n1", 200, 200, 28.0, 77.0, True) # far away
    # travel time will be large
    decision = allocate_single(listing, [ngo])
    assert decision.winner_ngo_id is None
    cand = decision.evidence["candidates"][0]
    assert not cand["is_eligible"]
    assert "Infeasible transit time" in cand["rejection_reason"]

def test_unverified_rejection():
    listing = ListingSnapshot("l1", 100, 120, 28.6, 77.2)
    ngo = NGOSnapshot("n1", 200, 200, 28.6, 77.2, False)
    decision = allocate_single(listing, [ngo])
    assert decision.winner_ngo_id is None
    assert decision.evidence["candidates"][0]["rejection_reason"] == "NGO is not verified"

def test_zero_capacity_rejection():
    listing = ListingSnapshot("l1", 100, 120, 28.6, 77.2)
    ngo = NGOSnapshot("n1", 200, 50, 28.6, 77.2, True)
    decision = allocate_single(listing, [ngo])
    assert decision.winner_ngo_id is None
    assert "Insufficient capacity" in decision.evidence["candidates"][0]["rejection_reason"]

def test_closer_wins_when_equal():
    listing = ListingSnapshot("l1", 100, 120, 28.6, 77.2)
    ngo_close = NGOSnapshot("n1", 200, 200, 28.6, 77.21, True) # very close
    ngo_far = NGOSnapshot("n2", 200, 200, 28.6, 77.3, True) # further
    decision = allocate_single(listing, [ngo_close, ngo_far])
    assert decision.winner_ngo_id == "n1"

def test_capacity_matters():
    listing = ListingSnapshot("l1", 100, 120, 28.6, 77.2)
    # Both same location. n1 has exactly 100 capacity. n2 has 1000 capacity.
    # n1 should have better capacity fit score.
    ngo1 = NGOSnapshot("n1", 100, 100, 28.6, 77.2, True)
    ngo2 = NGOSnapshot("n2", 1000, 1000, 28.6, 77.2, True)
    decision = allocate_single(listing, [ngo1, ngo2])
    assert decision.winner_ngo_id == "n2"

def test_batch_processing_and_capacity_decrement():
    listings = [
        ListingSnapshot("l1", 50, 100, 28.6, 77.2), # more urgent
        ListingSnapshot("l2", 80, 200, 28.6, 77.2)
    ]
    ngos = [
        NGOSnapshot("n1", 100, 100, 28.6, 77.2, True) # only capacity for 100
    ]
    decisions = allocate_batch(listings, ngos)
    assert len(decisions) == 2
    
    l1_dec = next(d for d in decisions if d.listing_id == "l1")
    l2_dec = next(d for d in decisions if d.listing_id == "l2")
    
    assert l1_dec.winner_ngo_id == "n1"
    assert l2_dec.winner_ngo_id is None # No capacity left

def test_reproduce_from_evidence():
    listing = ListingSnapshot("l1", 100, 120, 28.6, 77.2)
    ngo1 = NGOSnapshot("n1", 200, 200, 28.6, 77.21, True)
    ngo2 = NGOSnapshot("n2", 200, 200, 28.6, 77.3, True)
    decision = allocate_single(listing, [ngo1, ngo2])
    
    assert reproduce_from_evidence(decision.evidence) is True
    
    # Tamper with it
    decision.evidence["candidates"][0]["total_score"] = 999.0
    assert reproduce_from_evidence(decision.evidence) is False

