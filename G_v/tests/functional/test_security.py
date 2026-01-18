"""
Security and Role Restriction Tests (System Testing)
"""
import pytest
from models import User, UserRole, Organization, Branch, Patient
from auth.jwt_handler import jwt_handler

def test_unauthorized_access_to_patient_data(client, db):
    # Setup branch and patient
    org = Organization(name="Sec Org")
    db.add(org)
    db.flush()
    branch = Branch(organization_id=org.id, name="B1")
    db.add(branch)
    db.flush()
    
    patient_user = User(id=100, email="p@s.com", role=UserRole.PATIENT, branch_id=branch.id, password_hash="x", first_name="P", last_name="S")
    db.add(patient_user)
    db.flush()
    patient = Patient(user_id=100, organization_id=org.id, branch_id=branch.id, patient_uid="PSEC")
    db.add(patient)
    db.commit()
    
    # Try to access patient list as a Patient (should fail)
    patient_token = jwt_handler.create_access_token({"sub": "100", "role": "patient"})
    
    response = client.get(
        "/receptionist/patients/search",
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]

def test_org_admin_cannot_view_clinical_data(client, db):
    # Setup Org Admin
    org_admin_user = User(id=101, email="oa@s.com", role=UserRole.ORG_ADMIN, password_hash="x", is_active=True, first_name="O", last_name="A")
    db.add(org_admin_user)
    db.commit()
    
    oa_token = jwt_handler.create_access_token({"sub": "101", "role": "org_admin"})
    
    # Org admin tries to access clinical records (should fail/403)
    # The routers for doctors/nurses are restricted to doctor/nurse roles
    response = client.get(
        "/doctor/appointments",
        headers={"Authorization": f"Bearer {oa_token}"}
    )
    
    assert response.status_code == 403

def test_super_admin_unauthorized_for_clinical(client, db):
    # Setup Super Admin
    sa_user = User(id=1, email="sa@ihorms.com", role=UserRole.SUPER_ADMIN, password_hash="x", is_active=True, first_name="S", last_name="A")
    db.add(sa_user)
    db.commit()
    
    sa_token = jwt_handler.create_access_token({"sub": "1", "role": "super_admin"})
    
    # Super admin tries to search patients
    response = client.get(
        "/receptionist/patients/search",
        headers={"Authorization": f"Bearer {sa_token}"}
    )
    
    assert response.status_code == 403
