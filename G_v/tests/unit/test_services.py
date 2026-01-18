"""
Unit tests for core services
"""
import pytest
from services.user_service import UserService
from services.patient_service import PatientService
from models import UserRole, Organization, Branch
from schemas.user import UserCreate, DoctorCreate
from schemas.patient import PatientCreate
from decimal import Decimal

def test_user_authentication(db, create_test_user):
    user_service = UserService(db)
    email = "test@example.com"
    password = "password123"
    create_test_user(email, UserRole.DOCTOR)
    
    authenticated_user = user_service.authenticate_user(email, password)
    assert authenticated_user is not None
    assert authenticated_user.email == email

def test_create_doctor(db, create_test_user):
    user_service = UserService(db)
    
    # Setup dependencies
    org = Organization(name="Test Org")
    db.add(org)
    db.flush()
    branch = Branch(organization_id=org.id, name="Test Branch", city="Mumbai")
    db.add(branch)
    db.flush()
    
    super_admin = create_test_user("admin@test.com", UserRole.SUPER_ADMIN)
    
    doctor_data = DoctorCreate(
        email="doctor@test.com",
        first_name="John",
        last_name="Doe",
        specialization="Cardiology",
        qualification="MBBS",
        experience_years=10,
        consultation_fee=Decimal("1000.00")
    )
    
    user, doctor = user_service.create_doctor(doctor_data, org.id, branch.id, super_admin.id)
    
    assert user.email == "doctor@test.com"
    assert doctor.specialization == "Cardiology"
    assert doctor.license_number.startswith("TES-MUM-D")

def test_patient_registration(db, create_test_user):
    patient_service = PatientService(db)
    
    # Setup dependencies
    org = Organization(name="Test Org 2")
    db.add(org)
    db.flush()
    branch = Branch(organization_id=org.id, name="Test Branch 2", city="Delhi")
    db.add(branch)
    db.flush()
    
    receptionist = create_test_user("rec@test.com", UserRole.RECEPTIONIST)
    
    patient_data = PatientCreate(
        email="patient@test.com",
        first_name="Jane",
        last_name="Doe",
        phone="1234567890",
        blood_group="O+"
    )
    
    patient = patient_service.create_patient(patient_data, org.id, branch.id, receptionist.id)
    
    assert patient.patient_uid.startswith("TES-DEL-P")
    assert patient.blood_group == "O+"
