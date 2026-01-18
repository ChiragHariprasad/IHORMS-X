"""
Functional tests for Nurse and Pharmacy operations
"""
import pytest
from models import User, UserRole, Organization, Branch, Appointment, Patient, Doctor, Nurse, Inventory
from auth.jwt_handler import jwt_handler
from datetime import date, time

def test_nurse_telemetry_recording(client, db):
    # Setup branch and nurse
    org = Organization(name="Care Org")
    db.add(org)
    db.flush()
    branch = Branch(organization_id=org.id, name="B1", city="Pune")
    db.add(branch)
    db.flush()
    
    nurse_user = User(id=20, email="nurse@care.com", role=UserRole.NURSE, branch_id=branch.id, password_hash="x", is_active=True, first_name="N", last_name="C")
    db.add(nurse_user)
    db.flush()
    nurse = Nurse(user_id=20, qualification="RN", license_number="L001")
    db.add(nurse)
    db.flush()
    
    # Setup patient and appointment
    pat_user = User(id=21, email="p2@care.com", role=UserRole.PATIENT, branch_id=branch.id, password_hash="x", first_name="P", last_name="T")
    db.add(pat_user)
    db.flush()
    patient = Patient(user_id=21, organization_id=org.id, branch_id=branch.id, patient_uid="P001")
    db.add(patient)
    db.flush()
    
    doc_user = User(id=22, email="d2@care.com", role=UserRole.DOCTOR, branch_id=branch.id, password_hash="x")
    db.add(doc_user)
    db.flush()
    doctor = Doctor(user_id=22, license_number="D002")
    db.add(doctor)
    db.flush()
    
    appointment = Appointment(patient_id=patient.id, doctor_id=doctor.id, appointment_date=date.today(), appointment_time=time(10,0))
    db.add(appointment)
    db.commit()
    
    nurse_token = jwt_handler.create_access_token({"sub": "20", "role": "nurse"})
    
    # Record telemetry
    tele_response = client.post(
        "/nurse/telemetry",
        json={
            "appointment_id": appointment.id,
            "heart_rate": 120,
            "blood_pressure_systolic": 145,
            "temperature": 101.5,
            "oxygen_saturation": 94,
            "is_icu_patient": False
        },
        headers={"Authorization": f"Bearer {nurse_token}"}
    )
    
    assert tele_response.status_code == 200
    data = tele_response.json()
    assert data["alert_triggered"] is True
    assert "High heart rate" in data["alert_message"]

def test_pharmacy_inventory_management(client, db):
    # Setup pharmacist
    org = Organization(name="Pharma Org")
    db.add(org)
    db.flush()
    branch = Branch(organization_id=org.id, name="B2", city="Pune")
    db.add(branch)
    db.flush()
    
    pharma_user = User(id=30, email="pharma@care.com", role=UserRole.PHARMACY_STAFF, branch_id=branch.id, password_hash="x", is_active=True, first_name="P", last_name="S")
    db.add(pharma_user)
    db.commit()
    
    pharma_token = jwt_handler.create_access_token({"sub": "30", "role": "pharmacy_staff"})
    
    # 1. Add Stock
    inv_response = client.post(
        "/pharmacy/inventory",
        json={
            "medicine_name": "Amoxicillin 500mg",
            "quantity": 100,
            "unit_price": 5.50,
            "reorder_level": 20
        },
        headers={"Authorization": f"Bearer {pharma_token}"}
    )
    assert inv_response.status_code == 200
    
    # 2. View Stock
    list_response = client.get(
        "/pharmacy/inventory",
        headers={"Authorization": f"Bearer {pharma_token}"}
    )
    assert list_response.status_code == 200
    assert any(item["medicine_name"] == "Amoxicillin 500mg" for item in list_response.json())
