from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.entities import UserRole, ListingStatus, FoodType


class UserBase(BaseModel):
    email: str
    role: UserRole


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class DonorBase(BaseModel):
    name: str
    donor_type: str
    address: str
    latitude: float
    longitude: float
    contact_phone: Optional[str] = None


class DonorCreate(DonorBase):
    pass


class DonorOut(DonorBase):
    id: str
    user_id: str
    verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class NGOBase(BaseModel):
    name: str
    registration_number: Optional[str] = None
    address: str
    latitude: float
    longitude: float
    contact_phone: Optional[str] = None
    total_capacity_meals: int = 100
    current_capacity_meals: int = 100


class NGOCreate(NGOBase):
    pass


class NGOOut(NGOBase):
    id: str
    user_id: str
    verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ListingBase(BaseModel):
    title: str
    food_type: FoodType
    quantity_meals: int = Field(gt=0, description="Quantity in meals must be greater than zero")
    description: Optional[str] = None
    pickup_address: str
    latitude: float
    longitude: float
    prep_time: datetime
    expiry_time: datetime
    photo_url: Optional[str] = None
    dietary_flags: List[str] = []


class ListingCreate(ListingBase):
    donor_id: Optional[str] = None  # If not provided, will default to current donor user


class ListingUpdate(BaseModel):
    title: Optional[str] = None
    food_type: Optional[FoodType] = None
    quantity_meals: Optional[int] = Field(None, gt=0)
    description: Optional[str] = None
    pickup_address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    prep_time: Optional[datetime] = None
    expiry_time: Optional[datetime] = None
    photo_url: Optional[str] = None
    dietary_flags: Optional[List[str]] = None


class ListingStatusUpdate(BaseModel):
    status: ListingStatus


class ListingOut(ListingBase):
    id: str
    donor_id: str
    status: ListingStatus
    created_at: datetime
    updated_at: datetime
    minutes_to_expiry: float
    is_expired: bool
    donor_name: Optional[str] = None

    class Config:
        from_attributes = True


class AllocationOut(BaseModel):
    id: str
    listing_id: str
    ngo_id: str
    allocated_at: datetime
    picked_up_at: Optional[datetime] = None
    status: str
    evidence_json: Dict[str, Any]
    explanation_text: str
    model_version: str
    ngo_name: Optional[str] = None

    class Config:
        from_attributes = True
