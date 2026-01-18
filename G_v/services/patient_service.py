"""
Patient Service - Handles patient management operations
"""
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from datetime import datetime

from models import User, UserRole, Patient, Organization, Branch, MedicalHistory, Appointment
from schemas.patient import PatientCreate, PatientUpdate
from utils.helpers import hash_password, generate_user_id
from utils.exceptions import NotFoundError, ConflictError
from utils.audit import audit_logger


class PatientService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_patient_by_id(self, patient_id: int) -> Optional[Patient]:
        return self.db.query(Patient).filter(Patient.id == patient_id).first()
    
    def get_patient_by_uid(self, patient_uid: str) -> Optional[Patient]:
        return self.db.query(Patient).filter(Patient.patient_uid == patient_uid).first()
    
    def get_patient_by_user_id(self, user_id: int) -> Optional[Patient]:
        return self.db.query(Patient).filter(Patient.user_id == user_id).first()
    
    def create_patient(
        self, 
        data: PatientCreate, 
        organization_id: int, 
        branch_id: int,
        created_by: int
    ) -> Patient:
        """Create a new patient record (Receptionist only)"""
        # Check if email already exists
        existing = self.db.query(User).filter(User.email == data.email).first()
        if existing:
            raise ConflictError(f"User with email {data.email} already exists")
        
        # Create user
        user = User(
            organization_id=organization_id,
            branch_id=branch_id,
            role=UserRole.PATIENT,
            email=data.email,
            password_hash=hash_password("patient123"),
            first_name=data.first_name,
            last_name=data.last_name,
            phone=data.phone,
            date_of_birth=data.date_of_birth,
            gender=data.gender,
            is_active=True
        )
        self.db.add(user)
        self.db.flush()
        
        # Generate patient UID
        org = self.db.query(Organization).filter(Organization.id == organization_id).first()
        branch = self.db.query(Branch).filter(Branch.id == branch_id).first()
        
        patient_count = self.db.query(Patient).filter(Patient.branch_id == branch_id).count()
        
        org_code = org.name[:3].upper()
        branch_code = (branch.city or "BCH")[:3].upper()
        patient_uid = generate_user_id(org_code, branch_code, 'P', patient_count + 1)
        
        # Create patient record
        patient = Patient(
            user_id=user.id,
            organization_id=organization_id,
            branch_id=branch_id,
            patient_uid=patient_uid,
            blood_group=data.blood_group,
            emergency_contact=data.emergency_contact,
            emergency_contact_name=data.emergency_contact_name,
            address=data.address,
            insurance_provider=data.insurance_provider,
            insurance_policy_number=data.insurance_policy_number,
            insurance_expiry=data.insurance_expiry
        )
        self.db.add(patient)
        
        audit_logger.log_action(
            self.db, created_by, "PATIENT_CREATED", "Patient", patient.id,
            after_state={"patient_uid": patient_uid, "email": data.email}
        )
        
        self.db.commit()
        return patient
    
    def update_patient(
        self, 
        patient_id: int, 
        data: PatientUpdate, 
        updated_by: int
    ) -> Patient:
        """Update patient demographic details"""
        patient = self.get_patient_by_id(patient_id)
        if not patient:
            raise NotFoundError("Patient", str(patient_id))
        
        user = self.db.query(User).filter(User.id == patient.user_id).first()
        
        # Update user fields
        user_fields = ['first_name', 'last_name', 'phone']
        for field in user_fields:
            value = getattr(data, field, None)
            if value is not None:
                setattr(user, field, value)
        
        # Update patient fields
        patient_fields = ['address', 'blood_group', 'emergency_contact', 
                         'emergency_contact_name', 'insurance_provider',
                         'insurance_policy_number', 'insurance_expiry']
        for field in patient_fields:
            value = getattr(data, field, None)
            if value is not None:
                setattr(patient, field, value)
        
        audit_logger.log_action(
            self.db, updated_by, "PATIENT_UPDATED", "Patient", patient.id,
            after_state=data.model_dump(exclude_unset=True)
        )
        
        self.db.commit()
        return patient
    
    def search_patients(
        self, 
        branch_id: int,
        query: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Patient], int]:
        """Search patients by name, UID, or phone"""
        base_query = self.db.query(Patient).join(User).filter(
            Patient.branch_id == branch_id
        )
        
        if query:
            search = f"%{query}%"
            base_query = base_query.filter(
                or_(
                    Patient.patient_uid.ilike(search),
                    User.first_name.ilike(search),
                    User.last_name.ilike(search),
                    User.phone.ilike(search),
                    User.email.ilike(search)
                )
            )
        
        total = base_query.count()
        patients = base_query.offset((page - 1) * page_size).limit(page_size).all()
        
        return patients, total
    
    def get_patient_medical_history(
        self, 
        patient_id: int, 
        accessed_by: int,
        access_reason: str = "Clinical review"
    ) -> List[MedicalHistory]:
        """Get patient's medical history (logs access)"""
        patient = self.get_patient_by_id(patient_id)
        if not patient:
            raise NotFoundError("Patient", str(patient_id))
        
        # Log access
        audit_logger.log_patient_access(
            self.db, patient_id, accessed_by, 
            "Medical History View", access_reason
        )
        
        return self.db.query(MedicalHistory).filter(
            MedicalHistory.patient_id == patient_id
        ).order_by(MedicalHistory.visit_date.desc()).all()
