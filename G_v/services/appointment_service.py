"""
Appointment Service - Handles appointment scheduling and management
"""
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, date, time, timedelta

from models import (
    Appointment, AppointmentStatus, Patient, Doctor, User, Room, 
    RoomType, MedicalHistory, Severity
)
from schemas.appointment import (
    AppointmentCreate, AppointmentUpdate, AppointmentReschedule, DoctorNotesUpdate
)
from utils.exceptions import NotFoundError, ConflictError, ValidationError, ForbiddenError
from utils.audit import audit_logger


class AppointmentService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_appointment_by_id(self, appointment_id: int) -> Optional[Appointment]:
        return self.db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    def check_doctor_availability(
        self, 
        doctor_id: int, 
        appointment_date: date, 
        appointment_time: time
    ) -> bool:
        """Check if doctor is available at the given time"""
        existing = self.db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == appointment_date,
            Appointment.appointment_time == appointment_time,
            Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.ACCEPTED])
        ).first()
        return existing is None
    
    def find_available_room(self, branch_id: int, room_type: RoomType = RoomType.CONSULTATION) -> Optional[Room]:
        """Find an available room"""
        return self.db.query(Room).filter(
            Room.branch_id == branch_id,
            Room.room_type == room_type,
            Room.is_available == True
        ).first()
    
    def auto_assign_doctor(self, branch_id: int, appointment_date: date, appointment_time: time) -> Optional[Doctor]:
        """Auto-assign a doctor based on availability"""
        doctors = self.db.query(Doctor).join(User).filter(
            User.branch_id == branch_id,
            User.is_active == True
        ).all()
        
        for doctor in doctors:
            if self.check_doctor_availability(doctor.id, appointment_date, appointment_time):
                return doctor
        
        return None
    
    def create_appointment(
        self, 
        data: AppointmentCreate, 
        branch_id: int,
        created_by: int
    ) -> Appointment:
        """Create a new appointment"""
        # Validate patient
        patient = self.db.query(Patient).filter(Patient.id == data.patient_id).first()
        if not patient:
            raise NotFoundError("Patient", str(data.patient_id))
        
        # Handle doctor assignment
        if data.doctor_id:
            doctor = self.db.query(Doctor).filter(Doctor.id == data.doctor_id).first()
            if not doctor:
                raise NotFoundError("Doctor", str(data.doctor_id))
            
            if not self.check_doctor_availability(data.doctor_id, data.appointment_date, data.appointment_time):
                raise ConflictError("Doctor is not available at this time")
        else:
            # Auto-assign doctor
            doctor = self.auto_assign_doctor(branch_id, data.appointment_date, data.appointment_time)
            if not doctor:
                raise ConflictError("No doctors available at this time")
        
        # Find available room
        room = self.find_available_room(branch_id)
        
        appointment = Appointment(
            patient_id=data.patient_id,
            doctor_id=doctor.id,
            room_id=room.id if room else None,
            appointment_date=data.appointment_date,
            appointment_time=data.appointment_time,
            status=AppointmentStatus.SCHEDULED,
            chief_complaint=data.chief_complaint,
            created_by=created_by
        )
        self.db.add(appointment)
        
        audit_logger.log_action(
            self.db, created_by, "APPOINTMENT_CREATED", "Appointment", appointment.id,
            after_state={
                "patient_id": data.patient_id,
                "doctor_id": doctor.id,
                "date": str(data.appointment_date)
            }
        )
        
        self.db.commit()
        return appointment
    
    def book_appointment_by_patient(
        self, 
        patient_user_id: int,
        doctor_id: Optional[int],
        appointment_date: date,
        appointment_time: time,
        chief_complaint: Optional[str]
    ) -> Appointment:
        """Book appointment through patient portal"""
        patient = self.db.query(Patient).filter(Patient.user_id == patient_user_id).first()
        if not patient:
            raise NotFoundError("Patient record not found")
        
        data = AppointmentCreate(
            patient_id=patient.id,
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            chief_complaint=chief_complaint
        )
        
        return self.create_appointment(data, patient.branch_id, patient.user_id)
    
    def accept_appointment(self, appointment_id: int, doctor_user_id: int) -> Appointment:
        """Doctor accepts an appointment"""
        appointment = self.get_appointment_by_id(appointment_id)
        if not appointment:
            raise NotFoundError("Appointment", str(appointment_id))
        
        doctor = self.db.query(Doctor).filter(Doctor.user_id == doctor_user_id).first()
        if appointment.doctor_id != doctor.id:
            raise ForbiddenError("This appointment is not assigned to you")
        
        if appointment.status != AppointmentStatus.SCHEDULED:
            raise ValidationError(f"Cannot accept appointment with status: {appointment.status.value}")
        
        appointment.status = AppointmentStatus.ACCEPTED
        
        audit_logger.log_action(
            self.db, doctor_user_id, "APPOINTMENT_ACCEPTED", "Appointment", appointment_id
        )
        
        self.db.commit()
        return appointment
    
    def add_doctor_notes(
        self, 
        appointment_id: int, 
        doctor_user_id: int,
        data: DoctorNotesUpdate
    ) -> Appointment:
        """Doctor adds clinical notes, diagnosis, prescription, and verdict"""
        appointment = self.get_appointment_by_id(appointment_id)
        if not appointment:
            raise NotFoundError("Appointment", str(appointment_id))
        
        doctor = self.db.query(Doctor).filter(Doctor.user_id == doctor_user_id).first()
        if appointment.doctor_id != doctor.id:
            raise ForbiddenError("This appointment is not assigned to you")
        
        appointment.notes = data.notes
        appointment.diagnosis = data.diagnosis
        appointment.prescription = data.prescription
        appointment.verdict = data.verdict
        appointment.status = AppointmentStatus.COMPLETED
        
        # Create medical history record
        medical_history = MedicalHistory(
            patient_id=appointment.patient_id,
            appointment_id=appointment.id,
            visit_date=datetime.combine(appointment.appointment_date, appointment.appointment_time),
            diagnosis=data.diagnosis,
            symptoms=appointment.chief_complaint,
            severity=Severity.MEDIUM,
            treatment_given=data.prescription,
            medications={"prescription": data.prescription},
            doctor_notes=data.notes
        )
        self.db.add(medical_history)
        
        audit_logger.log_action(
            self.db, doctor_user_id, "DOCTOR_NOTES_ADDED", "Appointment", appointment_id,
            after_state={"diagnosis": data.diagnosis}
        )
        
        self.db.commit()
        return appointment
    
    def reschedule_appointment(
        self, 
        appointment_id: int, 
        data: AppointmentReschedule,
        rescheduled_by: int
    ) -> Appointment:
        """Receptionist reschedules an appointment"""
        appointment = self.get_appointment_by_id(appointment_id)
        if not appointment:
            raise NotFoundError("Appointment", str(appointment_id))
        
        if appointment.status == AppointmentStatus.COMPLETED:
            raise ValidationError("Cannot reschedule completed appointment")
        
        new_doctor_id = data.new_doctor_id or appointment.doctor_id
        
        # Check availability
        if not self.check_doctor_availability(new_doctor_id, data.new_date, data.new_time):
            raise ConflictError("Doctor is not available at the new time")
        
        before_state = {
            "date": str(appointment.appointment_date),
            "time": str(appointment.appointment_time),
            "doctor_id": appointment.doctor_id
        }
        
        appointment.appointment_date = data.new_date
        appointment.appointment_time = data.new_time
        if data.new_doctor_id:
            appointment.doctor_id = data.new_doctor_id
        appointment.status = AppointmentStatus.SCHEDULED
        
        audit_logger.log_action(
            self.db, rescheduled_by, "APPOINTMENT_RESCHEDULED", "Appointment", appointment_id,
            before_state=before_state,
            after_state={
                "date": str(data.new_date),
                "time": str(data.new_time),
                "doctor_id": new_doctor_id
            }
        )
        
        self.db.commit()
        return appointment
    def confirm_appointment(self, appointment_id: int, staff_user_id: int) -> Appointment:
        """Receptionist confirms an appointment (accepts it)"""
        appointment = self.get_appointment_by_id(appointment_id)
        if not appointment:
            raise NotFoundError("Appointment", str(appointment_id))
        
        if appointment.status != AppointmentStatus.SCHEDULED:
            raise ValidationError(f"Cannot confirm appointment with status: {appointment.status.value}")
        
        appointment.status = AppointmentStatus.ACCEPTED
        
        audit_logger.log_action(
            self.db, staff_user_id, "APPOINTMENT_CONFIRMED", "Appointment", appointment_id
        )
        
        self.db.commit()
        return appointment

    def admit_patient(self, appointment_id: int, room_type: str, doctor_user_id: int) -> Appointment:
        """Admit a patient to a room"""
        appointment = self.get_appointment_by_id(appointment_id)
        if not appointment:
            raise NotFoundError("Appointment", str(appointment_id))
        
        doctor = self.db.query(Doctor).filter(Doctor.user_id == doctor_user_id).first()
        if appointment.doctor_id != doctor.id:
            raise ForbiddenError("This appointment is not assigned to you")
            
        # Find available room
        from models import Branch  # Local import to avoid circular dependency if any
        room = self.db.query(Room).join(Branch).join(User).filter(
            User.id == doctor_user_id,
            Room.branch_id == User.branch_id,
            Room.room_type == getattr(RoomType, room_type.upper(), RoomType.GENERAL_WARD),
            Room.is_available == True
        ).first()
        
        
        if not room:
            raise ConflictError(f"No available {room_type} rooms found in this branch")
            
        appointment.status = AppointmentStatus.ADMITTED
        appointment.room_id = room.id
        room.is_available = False

        # Create Admission record
        from models import Admission, AdmissionStatus # Local import
        admission = Admission(
            patient_id=appointment.patient_id,
            doctor_id=appointment.doctor_id,
            appointment_id=appointment.id,
            room_id=room.id,
            admitted_by=doctor_user_id,
            status=AdmissionStatus.ADMITTED,
            admission_date=datetime.utcnow()
        )
        self.db.add(admission)
        
        audit_logger.log_action(
            self.db, doctor_user_id, "PATIENT_ADMITTED", "Appointment", appointment_id,
            after_state={"room_id": room.id, "room_type": room_type, "admission_id": admission.id}
        )
        
        self.db.commit()
        return appointment

    def get_doctor_appointments(self, doctor_user_id: int) -> Tuple[List[Appointment], int]:
        """Get all appointments for a doctor"""
        doctor = self.db.query(Doctor).filter(Doctor.user_id == doctor_user_id).first()
        if not doctor:
            raise NotFoundError("Doctor profile not found")
            
        query = self.db.query(Appointment).filter(Appointment.doctor_id == doctor.id)
        return query.order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc()).all(), query.count()

    def get_doctor_schedule(self, doctor_user_id: int, schedule_date: date) -> List[Appointment]:
        """Get doctor's schedule for a specific date"""
        doctor = self.db.query(Doctor).filter(Doctor.user_id == doctor_user_id).first()
        if not doctor:
            raise NotFoundError("Doctor profile not found")
            
        return self.db.query(Appointment).filter(
            Appointment.doctor_id == doctor.id,
            Appointment.appointment_date == schedule_date
        ).order_by(Appointment.appointment_time).all()

    def get_branch_appointments(self, branch_id: int) -> Tuple[List[Appointment], int]:
        """Get all appointments for a branch"""
        query = self.db.query(Appointment).join(Patient).filter(Patient.branch_id == branch_id)
        return query.order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc()).all(), query.count()

    def get_patient_appointments(self, patient_id: int) -> Tuple[List[Appointment], int]:
        """Get all appointments for a patient"""
        query = self.db.query(Appointment).filter(Appointment.patient_id == patient_id)
        return query.order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc()).all(), query.count()
