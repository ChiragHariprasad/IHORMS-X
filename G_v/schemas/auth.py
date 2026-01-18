"""
Authentication Schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserBasicInfo(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    role: str
    organization_id: Optional[int]
    branch_id: Optional[int]
    
    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserBasicInfo


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PasswordResetRequest(BaseModel):
    user_id: int


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
