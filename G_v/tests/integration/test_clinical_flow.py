"""
Integration test for appointment workflow
"""
import pytest
from models import User, UserRole, Organization, Branch, Patient, Doctor
from utils.helpers import hash_password
from auth.jwt_handler import jwt_handler
from datetime import date, time

def test_full_clinical_workflow(client, db):
    # 1. Setup Environment (Org, Branch, Staff)
    org = Organization(name="Apollo Integration")
    db.add(org)
    db.flush()
    branch = Branch(organization_id=org.id, name="Main Branch", city="Mumbai")
    db.add(branch)
    db.flush()
    
    # Staff Users
    rec_user = User(id=10, email="rec@ap.com", role=UserRole.RECEPTIONIST, organization_id=org.id, branch_id=branch.id, password_hash="x", is_active=True, first_name="R", last_name="S")
    doc_user = User(id=11, email="doc@ap.com", role=UserRole.DOCTOR, organization_id=org.id, branch_id=branch.id, password_hash="x", is_active=True, first_name="D", last_name="M")
    db.add_all([rec_user, doc_user])
    db.flush()
    
    doctor = Doctor(user_id=11, specialization="General", qualification="MD", license_number="DOC001")
    db.add(doctor)
    db.commit()
    
    rec_token = jwt_handler.create_access_token({"sub": "10", "role": "receptionist"})
    doc_token = jwt_handler.create_access_token({"sub": "11", "role": "doctor"})
    
    # 2. Receptionist registers patient
    reg_response = client.post(
        "/receptionist/patients",
        json={
            "email": "p1@gmail.com",
            "first_name": "Patient",
            "last_name": "One",
            "phone": "9999999999",
            "blood_group": "A+",
            "address": "Mumbai Street"
        },
        headers={"Authorization": f"Bearer {rec_token}"}
    )
    assert reg_response.status_code == 200
    patient_id = reg_response.json()["id"]
    
    # 3. Receptionist books appointment
    app_response = client.post(
        "/receptionist/appointments",
        json={
            "patient_id": patient_id,
            "doctor_id": doctor.id,
            "appointment_date": str(date.today()),
            "appointment_time": "10:30",
            "chief_complaint": "Persistent Headache"
        },
        headers={"Authorization": f"Bearer {rec_token}"}
    )
    assert app_response.status_code == 200
    app_id = app_response.json()["id"]
    
    # 4. Doctor accepts appointment
    accept_response = client.post(
        f"/doctor/appointments/{app_id}/accept",
        headers={"Authorization": f"Bearer {doc_token}"}
    )
    assert accept_response.status_code == 200
    
    # 5. Doctor adds notes and completes visit
    notes_response = client.post(
        f"/doctor/appointments/{app_id}/notes",
        json={
            "notes": "Patient is stressed.",
            "diagnosis": "Tension Headache",
            "prescription": "Rest and Paracetamol 500mg",
            "verdict": "Return if pain persists"
        },
        headers={"Authorization": f"Bearer {doc_token}"}
    )
    assert notes_response.status_code == 200
    assert notes_response.json()["status"] == "completed"
    
    # 6. Verify medical history entry
    history_response = client.get(
        f"/doctor/patients/{patient_id}/history",
        headers={"Authorization": f"Bearer {doc_token}"}
    )
    assert history_response.status_code == 200
    assert len(history_response.json()) > 0
    assert history_response.json()[0]["diagnosis"] == "Tension Headache"
