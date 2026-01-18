"""
Branch Admin Router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import User, UserRole
from schemas.user import UserCreate, UserResponse, DoctorCreate, NurseCreate
from schemas.analytics import BranchAnalytics
from services.user_service import UserService
from services.analytics_service import AnalyticsService
from auth.dependencies import get_branch_admin

router = APIRouter(prefix="/branch-admin", tags=["Branch Admin"])

@router.post("/doctors", response_model=UserResponse)
async def add_doctor(
    data: DoctorCreate, 
    db: Session = Depends(get_db),
    admin: User = Depends(get_branch_admin)
):
    service = UserService(db)
    user, doctor = service.create_doctor(data, admin.organization_id, admin.branch_id, admin.id)
    return user

@router.post("/nurses", response_model=UserResponse)
async def add_nurse(
    data: NurseCreate, 
    db: Session = Depends(get_db),
    admin: User = Depends(get_branch_admin)
):
    service = UserService(db)
    user, nurse = service.create_nurse(data, admin.organization_id, admin.branch_id, admin.id)
    return user

@router.post("/receptionists", response_model=UserResponse)
async def add_receptionist(
    data: UserCreate, 
    db: Session = Depends(get_db),
    admin: User = Depends(get_branch_admin)
):
    service = UserService(db)
    return service.create_receptionist(data, admin.organization_id, admin.branch_id, admin.id)

@router.get("/staff")
async def list_branch_staff(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    admin: User = Depends(get_branch_admin)
):
    service = UserService(db)
    users, total = service.get_staff_by_branch(admin.branch_id, page=page, page_size=page_size)
    return {"items": users, "total": total}

@router.get("/analytics", response_model=BranchAnalytics)
async def get_branch_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(get_branch_admin)
):
    service = AnalyticsService(db)
    return service.get_branch_analytics(admin.branch_id)

@router.post("/staff/{user_id}/disable")
async def disable_staff(
    user_id: int, 
    db: Session = Depends(get_db),
    admin: User = Depends(get_branch_admin)
):
    service = UserService(db)
    user = service.get_user_by_id(user_id)
    if user.branch_id != admin.branch_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    service.disable_user(user_id, admin.id)
    return {"status": "success"}
