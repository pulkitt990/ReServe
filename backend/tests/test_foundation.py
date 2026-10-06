import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data


@pytest.mark.asyncio
async def test_router_endpoints_mounted():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r_auth = await ac.get("/api/v1/auth/me")
        assert r_auth.status_code == 200
        
        r_listings = await ac.get("/api/v1/listings/")
        assert r_listings.status_code == 200
        
        r_forecast = await ac.get("/api/v1/forecasting/donor/1")
        assert r_forecast.status_code == 200
        
        r_allocate = await ac.post("/api/v1/allocation/allocate/1")
        assert r_allocate.status_code in (200, 404)
        
        r_explain = await ac.get("/api/v1/explanation/allocation/1")
        assert r_explain.status_code in (200, 404)
