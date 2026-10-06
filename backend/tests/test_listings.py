import pytest
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timedelta
from app.main import app
from app.models.entities import ListingStatus, FoodType


@pytest.mark.asyncio
async def test_get_listings():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/listings/")
        assert response.status_code == 200
        listings = response.json()
        assert isinstance(listings, list)
        assert len(listings) >= 1
        first = listings[0]
        assert "minutes_to_expiry" in first
        assert "status" in first
        assert "food_type" in first


@pytest.mark.asyncio
async def test_create_and_lifecycle_listing():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Create a fresh listing
        now = datetime.utcnow()
        payload = {
            "title": "Fresh Tomato Soup and Baguettes",
            "food_type": "cooked_meals",
            "quantity_meals": 30,
            "description": "Prepared today for charity test run",
            "pickup_address": "Test Hub, 100 Civic Center",
            "latitude": 28.5800,
            "longitude": 77.3150,
            "prep_time": now.isoformat(),
            "expiry_time": (now + timedelta(hours=4)).isoformat(),
            "dietary_flags": ["vegetarian"]
        }
        res = await client.post("/api/v1/listings/", json=payload)
        assert res.status_code == 201
        created = res.json()
        listing_id = created["id"]
        assert created["status"] == "open"
        assert created["quantity_meals"] == 30
        assert created["minutes_to_expiry"] > 0

        # 2. Transition: Open -> Allocated
        res_alloc = await client.patch(
            f"/api/v1/listings/{listing_id}/status",
            json={"status": "allocated"}
        )
        assert res_alloc.status_code == 200
        assert res_alloc.json()["status"] == "allocated"

        # 3. Transition: Allocated -> Picked Up
        res_picked = await client.patch(
            f"/api/v1/listings/{listing_id}/status",
            json={"status": "picked_up"}
        )
        assert res_picked.status_code == 200
        assert res_picked.json()["status"] == "picked_up"

        # 4. Attempt invalid transition on picked up terminal state
        res_invalid = await client.patch(
            f"/api/v1/listings/{listing_id}/status",
            json={"status": "open"}
        )
        assert res_invalid.status_code == 400
