"""
Super Admin Router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import Organization, User, UserRole
from schemas.organization import OrganizationCreate, OrganizationResponse
from schemas.analytics import PlatformAnalytics
from services.analytics_service import AnalyticsService
from auth.dependencies import get_super_admin
from utils.helpers import hash_password

router = APIRouter(prefix="/super-admin", tags=["Super Admin"])

@router.post("/organizations", response_model=OrganizationResponse)
def create_organization(
    data: OrganizationCreate, 
    db: Session = Depends(get_db),
    admin: User = Depends(get_super_admin)
):
    # Check if exists
    if db.query(Organization).filter(Organization.name == data.name).first():
        raise HTTPException(status_code=400, detail="Organization already exists")
    
    org = Organization(
        name=data.name,
        address=data.address,
        phone=data.phone,
        email=data.email
    )
    db.add(org)
    db.flush()
    
    # Create Org Admin
    admin_user = User(
        organization_id=org.id,
        role=UserRole.ORG_ADMIN,
        email=data.admin_email,
        password_hash=hash_password("orgadmin1"),
        first_name=data.admin_first_name,
        last_name=data.admin_last_name,
        is_active=True
    )
    db.add(admin_user)
    db.commit()
    db.refresh(org)
    return org

@router.get("/organizations", response_model=List[OrganizationResponse])
def list_organizations(
    db: Session = Depends(get_db),
    admin: User = Depends(get_super_admin)
):
    return db.query(Organization).all()

@router.get("/analytics", response_model=PlatformAnalytics)
def get_platform_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(get_super_admin)
):
    service = AnalyticsService(db)
    return service.get_platform_analytics()

@router.post("/organizations/{org_id}/toggle")
def toggle_organization(
    org_id: int, 
    db: Session = Depends(get_db),
    admin: User = Depends(get_super_admin)
):
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    org.is_active = not org.is_active
    db.commit()
    return {"status": "success", "is_active": org.is_active}
