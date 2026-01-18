"""
User Schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal


class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None


class UserCreate(UserBase):
    password: Optional[str] = None  # Will use default if not provided


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None


class UserResponse(UserBase):
    id: int
    role: str
    organization_id: Optional[int]
    branch_id: Optional[int]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class DoctorCreate(UserCreate):
    specialization: str
    qualification: str
    experience_years: int
    consultation_fee: Decimal


class DoctorResponse(UserResponse):
    specialization: Optional[str]
    qualification: Optional[str]
    experience_years: Optional[int]
    license_number: Optional[str]
    consultation_fee: Optional[Decimal]
    
    class Config:
        from_attributes = True


class NurseCreate(UserCreate):
    qualification: str


class NurseResponse(UserResponse):
    qualification: Optional[str]
    license_number: Optional[str]
    
    class Config:
        from_attributes = True


class StaffListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[UserResponse]


class DoctorListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[DoctorResponse]
