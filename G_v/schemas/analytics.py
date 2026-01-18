"""
Analytics Schemas
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal


class PlatformAnalytics(BaseModel):
    """Super Admin - Platform level analytics"""
    total_organizations: int
    active_organizations: int
    total_branches: int
    total_users: int
    total_patients: int
    total_appointments: int
    organizations: List[Dict[str, Any]]


class OrganizationAnalytics(BaseModel):
    """Org Admin - Organization level analytics"""
    organization_id: int
    organization_name: str
    total_branches: int
    total_staff: int
    total_patients: int
    total_appointments: int
    billing_summary: Dict[str, Any]
    staff_distribution: Dict[str, int]


class BranchAnalytics(BaseModel):
    """Branch Admin - Branch level analytics"""
    branch_id: int
    branch_name: str
    total_doctors: int
    total_nurses: int
    total_receptionists: int
    total_pharmacy_staff: int
    total_patients: int
    appointments_today: int
    appointments_this_week: int
    room_occupancy: Dict[str, Any]
    equipment_status: Dict[str, Any]


class PatientAccessLogResponse(BaseModel):
    id: int
    patient_id: int
    patient_name: str
    accessed_by: int
    accessed_by_name: str
    access_type: str
    access_reason: Optional[str]
    ip_address: Optional[str]
    accessed_at: datetime
    
    class Config:
        from_attributes = True
