import asyncio
from datetime import datetime, timedelta
import bcrypt
from sqlalchemy import text
from app.core.database import AsyncSessionLocal
from app.models.entities import (
    User,
    UserRole,
    Donor,
    NGO,
    Listing,
    ListingStatus,
    FoodType,
)


def hash_pwd(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


async def seed():
    print("🌱 Seeding realistic test data for ReServe...")
    async with AsyncSessionLocal() as session:
        
        existing = await session.execute(text("SELECT id FROM users LIMIT 1"))
        if existing.scalar() is not None:
            print("Data already seeded. Skipping.")
            return

        # 1. Create Users & Donors
        donor_users_data = [
            {
                "email": "greenbistro@reserve.local",
                "role": UserRole.DONOR,
                "name": "Green Fork Bistro & Cafe",
                "type": "restaurant",
                "address": "42 Market Street, Sector 18",
                "lat": 28.5700,
                "lon": 77.3200,
                "phone": "+91-9876543210",
            },
            {
                "email": "campusmess@reserve.local",
                "role": UserRole.DONOR,
                "name": "Central Campus Mega Mess",
                "type": "hostel",
                "address": "Block C, University Campus North",
                "lat": 28.5850,
                "lon": 77.3100,
                "phone": "+91-9876543211",
            },
            {
                "email": "artisanbakery@reserve.local",
                "role": UserRole.DONOR,
                "name": "Golden Crust Bakery",
                "type": "bakery",
                "address": "12 High Street Arcade",
                "lat": 28.5600,
                "lon": 77.3350,
                "phone": "+91-9876543212",
            },
        ]

        created_donors = []
        for d in donor_users_data:
            user = User(
                email=d["email"],
                hashed_password=hash_pwd("ReservePass123!"),
                role=d["role"],
                is_active=True,
            )
            session.add(user)
            await session.flush()

            donor = Donor(
                user_id=user.id,
                name=d["name"],
                donor_type=d["type"],
                address=d["address"],
                latitude=d["lat"],
                longitude=d["lon"],
                contact_phone=d["phone"],
                verified=True,
            )
            session.add(donor)
            await session.flush()
            created_donors.append(donor)

        # 2. Create NGOs
        ngo_users_data = [
            {
                "email": "hopehaven@reserve.local",
                "name": "Hope Haven Shelter & Kitchen",
                "reg": "NGO-2022-8812",
                "address": "10 Railway Colony Road",
                "lat": 28.5750,
                "lon": 77.3250,
                "phone": "+91-9123456780",
                "capacity": 150,
            },
            {
                "email": "annaseva@reserve.local",
                "name": "Anna Seva Foundation",
                "reg": "NGO-2021-4491",
                "address": "5 Community Center, Sector 12",
                "lat": 28.5900,
                "lon": 77.3050,
                "phone": "+91-9123456781",
                "capacity": 80,
            },
            {
                "email": "citybread@reserve.local",
                "name": "City Bread Relief Network",
                "reg": "NGO-2023-1029",
                "address": "88 Industrial Area Phase 1",
                "lat": 28.5500,
                "lon": 77.3400,
                "phone": "+91-9123456782",
                "capacity": 200,
            },
        ]

        created_ngos = []
        for n in ngo_users_data:
            user = User(
                email=n["email"],
                hashed_password=hash_pwd("ReservePass123!"),
                role=UserRole.NGO,
                is_active=True,
            )
            session.add(user)
            await session.flush()

            ngo = NGO(
                user_id=user.id,
                name=n["name"],
                registration_number=n["reg"],
                address=n["address"],
                latitude=n["lat"],
                longitude=n["lon"],
                contact_phone=n["phone"],
                total_capacity_meals=n["capacity"],
                current_capacity_meals=n["capacity"],
                verified=True,
            )
            session.add(ngo)
            await session.flush()
            created_ngos.append(ngo)

        # 3. Create Sample Listings with various shelf-life horizons
        now = datetime.utcnow()
        sample_listings = [
            {
                "donor": created_donors[0],  # Green Fork Bistro
                "title": "Fresh Dal Tadka, Jeera Rice & Phulkas",
                "type": FoodType.COOKED_MEALS,
                "qty": 45,
                "desc": "Surplus lunch buffet prepared today. Packed in clean stainless catering pans. Keep warm or reheat.",
                "prep_delta_hrs": -2,
                "expiry_delta_hrs": 3.5,  # Urgent! ~3.5 hours left
                "flags": ["vegetarian", "lunch_buffet"],
                "status": ListingStatus.OPEN,
            },
            {
                "donor": created_donors[1],  # Campus Mess
                "title": "Rajma Curry & Steamed Basmati Rice",
                "type": FoodType.COOKED_MEALS,
                "qty": 90,
                "desc": "Wholesome hostel dinner excess. Hygienically stored in insulated containers.",
                "prep_delta_hrs": -1,
                "expiry_delta_hrs": 5.0,  # ~5 hours left
                "flags": ["vegetarian", "high_protein"],
                "status": ListingStatus.OPEN,
            },
            {
                "donor": created_donors[2],  # Golden Crust Bakery
                "title": "Artisan Sourdough Loaves & Croissants",
                "type": FoodType.BAKERY,
                "qty": 35,
                "desc": "Baked early morning. Crisp crusts and butter croissants in individually sealed bakery packs.",
                "prep_delta_hrs": -6,
                "expiry_delta_hrs": 14.0,  # 14 hours left
                "flags": ["vegetarian", "dairy"],
                "status": ListingStatus.OPEN,
            },
            {
                "donor": created_donors[0],
                "title": "Paneer Butter Masala & Tandoori Roti",
                "type": FoodType.COOKED_MEALS,
                "qty": 25,
                "desc": "Evening catering overflow. Allocated to Hope Haven earlier.",
                "prep_delta_hrs": -4,
                "expiry_delta_hrs": 2.0,
                "flags": ["vegetarian"],
                "status": ListingStatus.ALLOCATED,
            },
        ]

        for item in sample_listings:
            listing = Listing(
                donor_id=item["donor"].id,
                title=item["title"],
                food_type=item["type"],
                quantity_meals=item["qty"],
                description=item["desc"],
                pickup_address=item["donor"].address,
                latitude=item["donor"].latitude,
                longitude=item["donor"].longitude,
                prep_time=now + timedelta(hours=item["prep_delta_hrs"]),
                expiry_time=now + timedelta(hours=item["expiry_delta_hrs"]),
                status=item["status"],
                dietary_flags=item["flags"],
            )
            session.add(listing)

        await session.commit()
        print("✅ Seeding completed successfully with Donors, NGOs, and Urgent Listings!")


if __name__ == "__main__":
    asyncio.run(seed())
