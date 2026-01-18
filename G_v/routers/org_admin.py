"""
Organization Admin Router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import User, UserRole, Branch
from schemas.user import UserCreate, UserResponse, DoctorCreate, NurseCreate
from schemas.organization import BranchCreate, BranchResponse
from schemas.analytics import OrganizationAnalytics
from services.user_service import UserService
from services.analytics_service import AnalyticsService
from auth.dependencies import get_org_admin

router = APIRouter(prefix="/org-admin", tags=["Organization Admin"])

@router.post("/branches", response_model=BranchResponse)
async def create_branch(
    data: BranchCreate, 
    db: Session = Depends(get_db),
    admin: User = Depends(get_org_admin)
):
    branch = Branch(
        organization_id=admin.organization_id,
        name=data.name,
        address=data.address,
        phone=data.phone,
        city=data.city,
        state=data.state,
        pincode=data.pincode
    )
    db.add(branch)
    db.commit()
    db.refresh(branch)
    return branch

@router.get("/branches", response_model=List[BranchResponse])
async def list_branches(
    db: Session = Depends(get_db),
    admin: User = Depends(get_org_admin)
):
    return db.query(Branch).filter(Branch.organization_id == admin.organization_id).all()

@router.get("/staff")
async def list_staff(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    admin: User = Depends(get_org_admin)
):
    query = db.query(User).filter(
        User.organization_id == admin.organization_id,
        User.role != UserRole.PATIENT
    )
    total = query.count()
    users = query.offset((page - 1) * page_size).limit(page_size).all()
    return {"items": users, "total": total}

@router.post("/deans", response_model=UserResponse)
async def add_dean(
    data: UserCreate, 
    branch_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_org_admin)
):
    service = UserService(db)
    return service.create_branch_admin(data, admin.organization_id, branch_id, admin.id)

@router.get("/analytics", response_model=OrganizationAnalytics)
async def get_org_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(get_org_admin)
):
    service = AnalyticsService(db)
    return service.get_organization_analytics(admin.organization_id)

@router.post("/staff/{user_id}/reset-password")
async def reset_staff_password(
    user_id: int, 
    db: Session = Depends(get_db),
    admin: User = Depends(get_org_admin)
):
    service = UserService(db)
    user = service.get_user_by_id(user_id)
    if user.organization_id != admin.organization_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    service.reset_password_to_default(user_id, admin.id)
    return {"status": "success"}

@router.post("/staff/{user_id}/toggle")
async def toggle_staff_access(
    user_id: int, 
    db: Session = Depends(get_db),
    admin: User = Depends(get_org_admin)
):
    service = UserService(db)
    user = service.get_user_by_id(user_id)
    if user.organization_id != admin.organization_id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    if user.is_active:
        service.disable_user(user_id, admin.id)
    else:
        service.enable_user(user_id, admin.id)
    return {"status": "success", "is_active": not user.is_active}
