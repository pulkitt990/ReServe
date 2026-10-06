import pytest
from httpx import AsyncClient, ASGITransport
import asyncio
from datetime import datetime, timedelta
import time
import uuid
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.entities import NGO, ListingStatus, Listing, User, UserRole, Donor, Allocation
from app.core.database import AsyncSessionLocal
from app.main import app

@pytest.mark.asyncio
async def test_allocation_api_flow():
    unique_id = str(uuid.uuid4())[:8]
    async with AsyncSessionLocal() as db_session:
        # Create user + NGO
        u_ngo = User(email=f"tngo_{unique_id}@example.com", hashed_password="h", role=UserRole.NGO)
        db_session.add(u_ngo)
        await db_session.commit()
        await db_session.refresh(u_ngo)

        ngo = NGO(
            user_id=u_ngo.id, name=f"Test NGO {unique_id}", address="Addr", latitude=28.551, longitude=77.301,
            total_capacity_meals=5000, current_capacity_meals=5000, verified=True
        )
        db_session.add(ngo)
        await db_session.commit()
        
        # Create user + Donor
        u_donor = User(email=f"tdonor_{unique_id}@example.com", hashed_password="h", role=UserRole.DONOR)
        db_session.add(u_donor)
        await db_session.commit()
        await db_session.refresh(u_donor)
        
        donor = Donor(
            user_id=u_donor.id, name=f"Test Donor {unique_id}", donor_type="restaurant", address="Addr",
            latitude=28.551, longitude=77.301, verified=True
        )
        db_session.add(donor)
        await db_session.commit()
        await db_session.refresh(donor)
        
        donor_id = donor.id
        ngo_id = ngo.id
        u_ngo_id = u_ngo.id
        u_donor_id = u_donor.id

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            expiry = datetime.utcnow() + timedelta(hours=2)
            prep = datetime.utcnow() + timedelta(minutes=10)
            
            resp = await client.post("/api/v1/listings/", json={
                "title": "API Test Food",
                "food_type": "cooked_meals",
                "quantity_meals": 100,
                "pickup_address": "Some place",
                "latitude": 28.551,
                "longitude": 77.301,
                "prep_time": prep.isoformat(),
                "expiry_time": expiry.isoformat(),
                "donor_id": donor_id
            })
            assert resp.status_code in (200, 201)
            listing_id = resp.json()["id"]
            
            resp = await client.get(f"/api/v1/allocation/preview/{listing_id}")
            assert resp.status_code == 200
            
            resp = await client.post(f"/api/v1/allocation/allocate/{listing_id}")
            assert resp.status_code == 200
            alloc = resp.json()["allocation"]
            alloc_id = alloc["id"]
            
            resp = await client.post(f"/api/v1/allocation/allocate/{listing_id}")
            assert resp.status_code == 409
            
            resp = await client.get(f"/api/v1/explanation/allocation/{alloc_id}")
            assert resp.status_code == 200
            assert "explanation" in resp.json()
            
            resp = await client.get(f"/api/v1/explanation/allocation/{alloc_id}/verify")
            assert resp.status_code == 200
            assert resp.json()["reproducible"] is True
            
    finally:
        async with AsyncSessionLocal() as db_session:
            # Clean up
            stmt_a = select(Allocation).filter(Allocation.ngo_id == ngo_id)
            res_a = await db_session.execute(stmt_a)
            for a in res_a.scalars().all():
                await db_session.delete(a)
                
            stmt_l = select(Listing).filter(Listing.donor_id == donor_id)
            res_l = await db_session.execute(stmt_l)
            for l in res_l.scalars().all():
                await db_session.delete(l)
                
            db_ngo = await db_session.get(NGO, ngo_id)
            if db_ngo: await db_session.delete(db_ngo)
            db_donor = await db_session.get(Donor, donor_id)
            if db_donor: await db_session.delete(db_donor)
            
            db_u_ngo = await db_session.get(User, u_ngo_id)
            if db_u_ngo: await db_session.delete(db_u_ngo)
            db_u_donor = await db_session.get(User, u_donor_id)
            if db_u_donor: await db_session.delete(db_u_donor)
            
            await db_session.commit()

@pytest.mark.asyncio
async def test_batch_allocation_benchmark():
    from app.services.allocation_engine import allocate_batch, ListingSnapshot, NGOSnapshot
    
    listings = [ListingSnapshot(f"l_{i}", 50, 120 - i*0.1, 28.5, 77.2) for i in range(500)]
    ngos = [NGOSnapshot(f"n_{j}", 5000, 5000, 28.5, 77.2, True) for j in range(200)]
    
    start_time = time.time()
    decisions = allocate_batch(listings, ngos)
    duration = time.time() - start_time
    assert len(decisions) == 500
    assert duration < 5.0
    print(f"\nBatch allocated 500 listings x 200 NGOs in {duration:.3f} seconds.")

