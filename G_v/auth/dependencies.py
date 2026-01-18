"""
Authentication Dependencies for FastAPI
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from auth.jwt_handler import jwt_handler
from models import User, UserRole

security = HTTPBearer()


class TokenData:
    def __init__(self, user_id: int, email: str, role: UserRole, 
                 organization_id: Optional[int], branch_id: Optional[int]):
        self.user_id = user_id
        self.email = email
        self.role = role
        self.organization_id = organization_id
        self.branch_id = branch_id


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Validate JWT and return current user"""
    token = credentials.credentials
    payload = jwt_handler.verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    user = db.query(User).filter(User.id == int(user_id), User.is_active == True).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    return user


def require_roles(allowed_roles: List[UserRole]):
    """Dependency factory for role-based access"""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[r.value for r in allowed_roles]}"
            )
        return current_user
    return role_checker


# Role-specific dependencies
async def get_super_admin(user: User = Depends(require_roles([UserRole.SUPER_ADMIN]))) -> User:
    return user


async def get_org_admin(user: User = Depends(require_roles([UserRole.ORG_ADMIN]))) -> User:
    return user


async def get_branch_admin(user: User = Depends(require_roles([UserRole.BRANCH_ADMIN]))) -> User:
    return user


async def get_doctor(user: User = Depends(require_roles([UserRole.DOCTOR]))) -> User:
    return user


async def get_nurse(user: User = Depends(require_roles([UserRole.NURSE]))) -> User:
    return user


async def get_receptionist(user: User = Depends(require_roles([UserRole.RECEPTIONIST]))) -> User:
    return user


async def get_pharmacy_staff(user: User = Depends(require_roles([UserRole.PHARMACY_STAFF]))) -> User:
    return user


async def get_patient_user(user: User = Depends(require_roles([UserRole.PATIENT]))) -> User:
    return user


async def get_clinical_staff(
    user: User = Depends(require_roles([UserRole.DOCTOR, UserRole.NURSE]))
) -> User:
    return user


async def get_branch_staff(
    user: User = Depends(require_roles([
        UserRole.DOCTOR, UserRole.NURSE, UserRole.RECEPTIONIST, 
        UserRole.PHARMACY_STAFF, UserRole.BRANCH_ADMIN
    ]))
) -> User:
    return user
