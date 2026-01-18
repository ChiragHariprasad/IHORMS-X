"""
Helper Functions
"""
import hashlib
from typing import Optional, List, Any
from datetime import datetime, date, time


def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return hash_password(plain_password) == hashed_password


def generate_user_id(org_code: str, branch_code: str, entity_type: str, sequence: int) -> str:
    """Generate standardized user/entity ID"""
    return f"{org_code}-{branch_code}-{entity_type}{sequence:05d}"


def paginate(query, page: int = 1, page_size: int = 20):
    """Apply pagination to a query"""
    return query.offset((page - 1) * page_size).limit(page_size)


def serialize_datetime(dt: Optional[datetime]) -> Optional[str]:
    """Serialize datetime to ISO format"""
    return dt.isoformat() if dt else None


def serialize_date(d: Optional[date]) -> Optional[str]:
    """Serialize date to ISO format"""
    return d.isoformat() if d else None


def serialize_time(t: Optional[time]) -> Optional[str]:
    """Serialize time to string"""
    return t.strftime("%H:%M") if t else None
