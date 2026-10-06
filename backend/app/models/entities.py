import enum
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Enum as SAEnum,
    JSON,
    Text,
)
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserRole(str, enum.Enum):
    DONOR = "donor"
    NGO = "ngo"
    ADMIN = "admin"


class ListingStatus(str, enum.Enum):
    OPEN = "open"
    ALLOCATED = "allocated"
    PICKED_UP = "picked_up"
    EXPIRED = "expired"


class FoodType(str, enum.Enum):
    COOKED_MEALS = "cooked_meals"
    BAKERY = "bakery"
    PRODUCE = "produce"
    DAIRY = "dairy"
    PACKAGED = "packaged"
    BEVERAGES = "beverages"


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SAEnum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    donor = relationship("Donor", back_populates="user", uselist=False, cascade="all, delete-orphan")
    ngo = relationship("NGO", back_populates="user", uselist=False, cascade="all, delete-orphan")


class Donor(Base):
    __tablename__ = "donors"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    name = Column(String, nullable=False, index=True)
    donor_type = Column(String, nullable=False)  # restaurant, hostel, bakery, event_organizer, corporate_cafeteria
    address = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    contact_phone = Column(String, nullable=True)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="donor")
    listings = relationship("Listing", back_populates="donor", cascade="all, delete-orphan")
    forecasts = relationship("Forecast", back_populates="donor", cascade="all, delete-orphan")


class NGO(Base):
    __tablename__ = "ngos"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    name = Column(String, nullable=False, index=True)
    registration_number = Column(String, nullable=True)
    address = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    contact_phone = Column(String, nullable=True)
    total_capacity_meals = Column(Integer, nullable=False, default=100)
    current_capacity_meals = Column(Integer, nullable=False, default=100)  # Remaining capacity
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="ngo")
    allocations = relationship("Allocation", back_populates="ngo")


class Listing(Base):
    __tablename__ = "listings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    donor_id = Column(String, ForeignKey("donors.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, nullable=False)
    food_type = Column(SAEnum(FoodType), nullable=False)
    quantity_meals = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    pickup_address = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    prep_time = Column(DateTime, nullable=False)
    expiry_time = Column(DateTime, nullable=False, index=True)
    status = Column(SAEnum(ListingStatus), default=ListingStatus.OPEN, index=True, nullable=False)
    photo_url = Column(String, nullable=True)
    dietary_flags = Column(JSON, default=list)  # ["vegetarian", "halal", "contains_dairy"]
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    donor = relationship("Donor", back_populates="listings")
    allocations = relationship("Allocation", back_populates="listing", cascade="all, delete-orphan")


class Allocation(Base):
    __tablename__ = "allocations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    listing_id = Column(String, ForeignKey("listings.id", ondelete="CASCADE"), nullable=False, index=True)
    ngo_id = Column(String, ForeignKey("ngos.id", ondelete="CASCADE"), nullable=False, index=True)
    allocated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    picked_up_at = Column(DateTime, nullable=True)
    status = Column(String, default="pending_pickup")  # pending_pickup, completed, cancelled
    evidence_json = Column(JSON, nullable=False)  # Full auditable candidate list, weights, winning factors
    explanation_text = Column(Text, nullable=False)  # Plain-English generated justification
    model_version = Column(String, default="heuristic_v1")

    listing = relationship("Listing", back_populates="allocations")
    ngo = relationship("NGO", back_populates="allocations")


class Forecast(Base):
    __tablename__ = "forecasts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    donor_id = Column(String, ForeignKey("donors.id", ondelete="CASCADE"), nullable=False, index=True)
    forecast_for_date = Column(DateTime, nullable=False, index=True)
    predicted_quantity_meals = Column(Float, nullable=False)
    confidence_lower = Column(Float, nullable=True)
    confidence_upper = Column(Float, nullable=True)
    features_used = Column(JSON, nullable=True)
    model_version = Column(String, default="xgboost_v1")
    generated_at = Column(DateTime, default=datetime.utcnow)

    donor = relationship("Donor", back_populates="forecasts")
