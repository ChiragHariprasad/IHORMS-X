"""
Organization Schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class OrganizationBase(BaseModel):
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None


class OrganizationCreate(OrganizationBase):
    admin_email: EmailStr
    admin_first_name: str
    admin_last_name: str


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None


class OrganizationResponse(OrganizationBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class OrganizationDetailResponse(OrganizationResponse):
    branch_count: int
    user_count: int
    patient_count: int


class BranchBase(BaseModel):
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    city: str
    state: Optional[str] = None
    pincode: Optional[str] = None


class BranchCreate(BranchBase):
    pass


class BranchResponse(BranchBase):
    id: int
    organization_id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class BranchDetailResponse(BranchResponse):
    doctor_count: int
    nurse_count: int
    patient_count: int
    room_count: int
