"""
IHORMS-X Database Models
Multi-tenant Hospital Management System
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, 
    Numeric, Text, Date, Time, JSON, Enum as SQLEnum, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()

# ==================== ENUMS ====================

class UserRole(enum.Enum):
    SUPER_ADMIN = "super_admin"
    ORG_ADMIN = "org_admin"
    BRANCH_ADMIN = "branch_admin"
    DOCTOR = "doctor"
    NURSE = "nurse"
    RECEPTIONIST = "receptionist"
    PHARMACY_STAFF = "pharmacy_staff"
    PATIENT = "patient"

class AppointmentStatus(enum.Enum):
    SCHEDULED = "scheduled"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class OrderStatus(enum.Enum):
    PENDING = "pending"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"

class ClaimStatus(enum.Enum):
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"

class RoomType(enum.Enum):
    CONSULTATION = "consultation"
    ICU = "icu"
    GENERAL_WARD = "general_ward"
    EMERGENCY = "emergency"
    OPERATION_THEATER = "operation_theater"

class Severity(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# ==================== CORE MODELS ====================

class Organization(Base):
    __tablename__ = 'organizations'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    address = Column(Text)
    phone = Column(String(20))
    email = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    branches = relationship("Branch", back_populates="organization")
    users = relationship("User", back_populates="organization")

class Branch(Base):
    __tablename__ = 'branches'
    
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    name = Column(String(200), nullable=False)
    address = Column(Text)
    phone = Column(String(20))
    city = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(10))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    organization = relationship("Organization", back_populates="branches")
    users = relationship("User", back_populates="branch")
    rooms = relationship("Room", back_populates="branch")

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'))
    branch_id = Column(Integer, ForeignKey('branches.id'))
    role = Column(SQLEnum(UserRole), nullable=False)
    
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20))
    date_of_birth = Column(Date)
    gender = Column(String(10))
    
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    last_login = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    organization = relationship("Organization", back_populates="users")
    branch = relationship("Branch", back_populates="users")
    
    __table_args__ = (
        Index('idx_user_email', 'email'),
        Index('idx_user_role_branch', 'role', 'branch_id'),
    )

class Patient(Base):
    __tablename__ = 'patients'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    branch_id = Column(Integer, ForeignKey('branches.id'), nullable=False)
    
    patient_uid = Column(String(50), unique=True, nullable=False)
    blood_group = Column(String(5))
    emergency_contact = Column(String(20))
    emergency_contact_name = Column(String(100))
    address = Column(Text)
    
    insurance_provider = Column(String(100))
    insurance_policy_number = Column(String(50))
    insurance_expiry = Column(Date)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    appointments = relationship("Appointment", back_populates="patient")
    medical_history = relationship("MedicalHistory", back_populates="patient")
    access_logs = relationship("PatientAccessLog", back_populates="patient")
    
    __table_args__ = (
        Index('idx_patient_uid', 'patient_uid'),
    )

class Doctor(Base):
    __tablename__ = 'doctors'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    specialization = Column(String(100))
    qualification = Column(String(200))
    experience_years = Column(Integer)
    license_number = Column(String(50), unique=True)
    consultation_fee = Column(Numeric(10, 2))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    appointments = relationship("Appointment", back_populates="doctor")

class Nurse(Base):
    __tablename__ = 'nurses'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    qualification = Column(String(200))
    license_number = Column(String(50), unique=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    telemetry_records = relationship("TelemetryData", back_populates="nurse")

class Room(Base):
    __tablename__ = 'rooms'
    
    id = Column(Integer, primary_key=True)
    branch_id = Column(Integer, ForeignKey('branches.id'), nullable=False)
    room_number = Column(String(20), nullable=False)
    room_type = Column(SQLEnum(RoomType), nullable=False)
    floor = Column(Integer)
    capacity = Column(Integer, default=1)
    is_available = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    branch = relationship("Branch", back_populates="rooms")
    appointments = relationship("Appointment", back_populates="room")

class Equipment(Base):
    __tablename__ = 'equipment'
    
    id = Column(Integer, primary_key=True)
    branch_id = Column(Integer, ForeignKey('branches.id'), nullable=False)
    name = Column(String(200), nullable=False)
    equipment_type = Column(String(100))
    serial_number = Column(String(100), unique=True)
    purchase_date = Column(Date)
    last_maintenance = Column(Date)
    is_operational = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

# ==================== APPOINTMENT & CLINICAL ====================

class Appointment(Base):
    __tablename__ = 'appointments'
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    doctor_id = Column(Integer, ForeignKey('doctors.id'), nullable=False)
    room_id = Column(Integer, ForeignKey('rooms.id'))
    
    appointment_date = Column(Date, nullable=False)
    appointment_time = Column(Time, nullable=False)
    status = Column(SQLEnum(AppointmentStatus), default=AppointmentStatus.SCHEDULED)
    
    chief_complaint = Column(Text)
    notes = Column(Text)
    diagnosis = Column(Text)
    prescription = Column(Text)
    verdict = Column(Text)
    
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    room = relationship("Room", back_populates="appointments")
    medical_history = relationship("MedicalHistory", back_populates="appointment", uselist=False)
    telemetry = relationship("TelemetryData", back_populates="appointment")
    billing = relationship("Billing", back_populates="appointment", uselist=False)
    
    __table_args__ = (
        Index('idx_appointment_date_doctor', 'appointment_date', 'doctor_id'),
        Index('idx_appointment_patient', 'patient_id'),
    )

class MedicalHistory(Base):
    __tablename__ = 'medical_history'
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    appointment_id = Column(Integer, ForeignKey('appointments.id'))
    
    visit_date = Column(DateTime, nullable=False)
    diagnosis = Column(Text, nullable=False)
    symptoms = Column(Text)
    severity = Column(SQLEnum(Severity))
    treatment_given = Column(Text)
    medications = Column(JSON)
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(Date)
    
    doctor_notes = Column(Text)
    lab_results = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    patient = relationship("Patient", back_populates="medical_history")
    appointment = relationship("Appointment", back_populates="medical_history")
    
    __table_args__ = (
        Index('idx_medical_history_patient_date', 'patient_id', 'visit_date'),
    )

class TelemetryData(Base):
    __tablename__ = 'telemetry_data'
    
    id = Column(Integer, primary_key=True)
    appointment_id = Column(Integer, ForeignKey('appointments.id'), nullable=False)
    nurse_id = Column(Integer, ForeignKey('nurses.id'), nullable=False)
    equipment_id = Column(Integer, ForeignKey('equipment.id'))
    
    heart_rate = Column(Integer)
    blood_pressure_systolic = Column(Integer)
    blood_pressure_diastolic = Column(Integer)
    temperature = Column(Numeric(4, 1))
    oxygen_saturation = Column(Integer)
    respiratory_rate = Column(Integer)
    
    is_icu_patient = Column(Boolean, default=False)
    alert_triggered = Column(Boolean, default=False)
    alert_message = Column(Text)
    
    recorded_at = Column(DateTime, default=datetime.utcnow)
    
    appointment = relationship("Appointment", back_populates="telemetry")
    nurse = relationship("Nurse", back_populates="telemetry_records")

# ==================== BILLING & INSURANCE ====================

class Billing(Base):
    __tablename__ = 'billing'
    
    id = Column(Integer, primary_key=True)
    appointment_id = Column(Integer, ForeignKey('appointments.id'), nullable=False)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    
    bill_number = Column(String(50), unique=True, nullable=False)
    bill_date = Column(DateTime, default=datetime.utcnow)
    
    consultation_fee = Column(Numeric(10, 2), default=0)
    medication_cost = Column(Numeric(10, 2), default=0)
    room_charges = Column(Numeric(10, 2), default=0)
    test_charges = Column(Numeric(10, 2), default=0)
    other_charges = Column(Numeric(10, 2), default=0)
    
    subtotal = Column(Numeric(10, 2), nullable=False)
    tax = Column(Numeric(10, 2), default=0)
    discount = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(10, 2), nullable=False)
    
    amount_paid = Column(Numeric(10, 2), default=0)
    payment_status = Column(String(20), default='pending')
    payment_method = Column(String(50))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    appointment = relationship("Appointment", back_populates="billing")
    insurance_claims = relationship("InsuranceClaim", back_populates="billing")

class InsuranceClaim(Base):
    __tablename__ = 'insurance_claims'
    
    id = Column(Integer, primary_key=True)
    billing_id = Column(Integer, ForeignKey('billing.id'), nullable=False)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    
    claim_number = Column(String(50), unique=True, nullable=False)
    insurance_provider = Column(String(100), nullable=False)
    policy_number = Column(String(50), nullable=False)
    
    claimed_amount = Column(Numeric(10, 2), nullable=False)
    approved_amount = Column(Numeric(10, 2))
    status = Column(SQLEnum(ClaimStatus), default=ClaimStatus.SUBMITTED)
    
    submitted_date = Column(DateTime, default=datetime.utcnow)
    processed_date = Column(DateTime)
    rejection_reason = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    billing = relationship("Billing", back_populates="insurance_claims")

# ==================== PHARMACY ====================

class Supplier(Base):
    __tablename__ = 'suppliers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    contact_person = Column(String(100))
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class Inventory(Base):
    __tablename__ = 'inventory'
    
    id = Column(Integer, primary_key=True)
    branch_id = Column(Integer, ForeignKey('branches.id'), nullable=False)
    
    medicine_name = Column(String(200), nullable=False)
    generic_name = Column(String(200))
    manufacturer = Column(String(200))
    batch_number = Column(String(50))
    
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2))
    expiry_date = Column(Date)
    
    reorder_level = Column(Integer, default=50)
    last_restocked = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PharmacyOrder(Base):
    __tablename__ = 'pharmacy_orders'
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    appointment_id = Column(Integer, ForeignKey('appointments.id'))
    pharmacy_staff_id = Column(Integer, ForeignKey('users.id'))
    
    order_number = Column(String(50), unique=True, nullable=False)
    order_date = Column(DateTime, default=datetime.utcnow)
    
    items = Column(JSON, nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING)
    fulfilled_date = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)

# ==================== AUDIT & LOGS ====================

class PatientAccessLog(Base):
    __tablename__ = 'patient_access_logs'
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    accessed_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    access_type = Column(String(50))
    access_reason = Column(Text)
    ip_address = Column(String(50))
    
    accessed_at = Column(DateTime, default=datetime.utcnow)
    
    patient = relationship("Patient", back_populates="access_logs")

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50))
    entity_id = Column(Integer)
    
    before_state = Column(JSON)
    after_state = Column(JSON)
    
    ip_address = Column(String(50))
    user_agent = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_audit_user_created', 'user_id', 'created_at'),
    )

class SystemEvent(Base):
    __tablename__ = 'system_events'
    
    id = Column(Integer, primary_key=True)
    event_type = Column(String(100), nullable=False)
    severity = Column(String(20))
    message = Column(Text)
    event_metadata = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_event_type_created', 'event_type', 'created_at'),
    )