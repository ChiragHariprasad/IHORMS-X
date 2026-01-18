"""
User Service - Handles user management operations
"""
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func

from models import User, UserRole, Doctor, Nurse, Patient, Organization, Branch
from schemas.user import UserCreate, UserUpdate, DoctorCreate, NurseCreate
from utils.helpers import hash_password, generate_user_id
from utils.exceptions import NotFoundError, ConflictError
from utils.audit import audit_logger


class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = self.get_user_by_email(email)
        if user and user.password_hash == hash_password(password) and user.is_active:
            return user
        return None
    
    def create_staff(
        self, 
        data: UserCreate, 
        role: UserRole, 
        organization_id: int, 
        branch_id: Optional[int],
        created_by: int,
        default_password: str
    ) -> User:
        """Create a staff user (Doctor, Nurse, Receptionist, etc.)"""
        if self.get_user_by_email(data.email):
            raise ConflictError(f"User with email {data.email} already exists")
        
        user = User(
            organization_id=organization_id,
            branch_id=branch_id,
            role=role,
            email=data.email,
            password_hash=hash_password(data.password or default_password),
            first_name=data.first_name,
            last_name=data.last_name,
            phone=data.phone,
            date_of_birth=data.date_of_birth,
            gender=data.gender,
            is_active=True
        )
        self.db.add(user)
        self.db.flush()
        
        audit_logger.log_action(
            self.db, created_by, "USER_CREATED", "User", user.id,
            after_state={"email": user.email, "role": role.value}
        )
        
        return user
    
    def create_doctor(
        self, 
        data: DoctorCreate, 
        organization_id: int, 
        branch_id: int,
        created_by: int
    ) -> Tuple[User, Doctor]:
        """Create a doctor with profile"""
        user = self.create_staff(
            UserCreate(**data.model_dump(exclude={'specialization', 'qualification', 'experience_years', 'consultation_fee'})),
            UserRole.DOCTOR,
            organization_id,
            branch_id,
            created_by,
            "doctor123"
        )
        
        # Generate license number
        org = self.db.query(Organization).filter(Organization.id == organization_id).first()
        branch = self.db.query(Branch).filter(Branch.id == branch_id).first()
        
        doctor_count = self.db.query(Doctor).join(User).filter(User.branch_id == branch_id).count()
        
        # Simple code generation
        org_code = org.name[:3].upper()
        branch_code = (branch.city or "BCH")[:3].upper()
        license_number = generate_user_id(org_code, branch_code, 'D', doctor_count + 1)
        
        doctor = Doctor(
            user_id=user.id,
            specialization=data.specialization,
            qualification=data.qualification,
            experience_years=data.experience_years,
            consultation_fee=data.consultation_fee,
            license_number=license_number
        )
        self.db.add(doctor)
        self.db.commit()
        
        return user, doctor
    
    def create_nurse(
        self, 
        data: NurseCreate, 
        organization_id: int, 
        branch_id: int,
        created_by: int
    ) -> Tuple[User, Nurse]:
        """Create a nurse with profile"""
        user = self.create_staff(
            UserCreate(**data.model_dump(exclude={'qualification'})),
            UserRole.NURSE,
            organization_id,
            branch_id,
            created_by,
            "nurse123"
        )
        
        org = self.db.query(Organization).filter(Organization.id == organization_id).first()
        branch = self.db.query(Branch).filter(Branch.id == branch_id).first()
        
        nurse_count = self.db.query(Nurse).join(User).filter(User.branch_id == branch_id).count()
        
        org_code = org.name[:3].upper()
        branch_code = (branch.city or "BCH")[:3].upper()
        license_number = generate_user_id(org_code, branch_code, 'N', nurse_count + 1)
        
        nurse = Nurse(
            user_id=user.id,
            qualification=data.qualification,
            license_number=license_number
        )
        self.db.add(nurse)
        self.db.commit()
        
        return user, nurse
    
    def create_receptionist(
        self, 
        data: UserCreate, 
        organization_id: int, 
        branch_id: int,
        created_by: int
    ) -> User:
        """Create a receptionist"""
        user = self.create_staff(
            data, UserRole.RECEPTIONIST, organization_id, branch_id, created_by, "reception123"
        )
        self.db.commit()
        return user
    
    def create_pharmacy_staff(
        self, 
        data: UserCreate, 
        organization_id: int, 
        branch_id: int,
        created_by: int
    ) -> User:
        """Create pharmacy staff"""
        user = self.create_staff(
            data, UserRole.PHARMACY_STAFF, organization_id, branch_id, created_by, "pharma123"
        )
        self.db.commit()
        return user
    
    def create_branch_admin(
        self, 
        data: UserCreate, 
        organization_id: int, 
        branch_id: int,
        created_by: int
    ) -> User:
        """Create a branch admin (dean)"""
        # Check dean count
        dean_count = self.db.query(User).filter(
            User.branch_id == branch_id,
            User.role == UserRole.BRANCH_ADMIN,
            User.is_active == True
        ).count()
        
        if dean_count >= 2:
            raise ConflictError("Maximum 2 deans allowed per branch")
        
        default_password = f"dean{dean_count + 1}"
        user = self.create_staff(
            data, UserRole.BRANCH_ADMIN, organization_id, branch_id, created_by, default_password
        )
        self.db.commit()
        return user
    
    def disable_user(self, user_id: int, disabled_by: int) -> User:
        """Disable a user's login (soft disable)"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise NotFoundError("User", str(user_id))
        
        user.is_active = False
        
        audit_logger.log_action(
            self.db, disabled_by, "USER_DISABLED", "User", user.id,
            before_state={"is_active": True},
            after_state={"is_active": False}
        )
        
        self.db.commit()
        return user
    
    def enable_user(self, user_id: int, enabled_by: int) -> User:
        """Re-enable a user's login"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise NotFoundError("User", str(user_id))
        
        user.is_active = True
        
        audit_logger.log_action(
            self.db, enabled_by, "USER_ENABLED", "User", user.id,
            before_state={"is_active": False},
            after_state={"is_active": True}
        )
        
        self.db.commit()
        return user
    
    def reset_password_to_default(self, user_id: int, reset_by: int) -> User:
        """Reset user password to role default"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise NotFoundError("User", str(user_id))
        
        default_passwords = {
            UserRole.ORG_ADMIN: "orgadmin1",
            UserRole.BRANCH_ADMIN: "dean1",
            UserRole.DOCTOR: "doctor123",
            UserRole.NURSE: "nurse123",
            UserRole.RECEPTIONIST: "reception123",
            UserRole.PHARMACY_STAFF: "pharma123",
            UserRole.PATIENT: "patient123"
        }
        
        default_pwd = default_passwords.get(user.role, "password123")
        user.password_hash = hash_password(default_pwd)
        
        audit_logger.log_action(
            self.db, reset_by, "PASSWORD_RESET", "User", user.id
        )
        
        self.db.commit()
        return user
    
    def update_user(self, user_id: int, data: UserUpdate, updated_by: int) -> User:
        """Update user information"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise NotFoundError("User", str(user_id))
        
        before_state = {"first_name": user.first_name, "last_name": user.last_name}
        
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        
        audit_logger.log_action(
            self.db, updated_by, "USER_UPDATED", "User", user.id,
            before_state=before_state,
            after_state=data.model_dump(exclude_unset=True)
        )
        
        self.db.commit()
        return user
    
    def get_staff_by_branch(
        self, 
        branch_id: int, 
        role: Optional[UserRole] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[User], int]:
        """Get staff list for a branch"""
        query = self.db.query(User).filter(
            User.branch_id == branch_id,
            User.is_deleted == False
        )
        
        if role:
            query = query.filter(User.role == role)
        
        total = query.count()
        users = query.offset((page - 1) * page_size).limit(page_size).all()
        
        return users, total
