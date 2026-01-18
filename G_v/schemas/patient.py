"""
Patient Schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime


class PatientBase(BaseModel):
    blood_group: Optional[str] = None
    emergency_contact: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    address: Optional[str] = None
    insurance_provider: Optional[str] = None
    insurance_policy_number: Optional[str] = None
    insurance_expiry: Optional[date] = None


class PatientCreate(PatientBase):
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None


class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    blood_group: Optional[str] = None
    emergency_contact: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    insurance_provider: Optional[str] = None
    insurance_policy_number: Optional[str] = None
    insurance_expiry: Optional[date] = None


class PatientResponse(BaseModel):
    id: int
    user_id: int
    patient_uid: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str]
    date_of_birth: Optional[date]
    gender: Optional[str]
    blood_group: Optional[str]
    emergency_contact: Optional[str]
    emergency_contact_name: Optional[str]
    address: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class PatientDetailResponse(PatientResponse):
    insurance_provider: Optional[str]
    insurance_policy_number: Optional[str]
    insurance_expiry: Optional[date]
    total_visits: int
    last_visit: Optional[datetime]


class PatientSearchResult(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[PatientResponse]
