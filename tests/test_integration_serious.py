import pytest
from sqlalchemy import desc

from models import Patient, Doctor, Appointment, AuditLog, PatientAccessLog


def test_st01_login_flow_real_db(doctor_token):
    assert isinstance(doctor_token, str)
    assert len(doctor_token) > 50


def test_st02_me_returns_tenant(client, doctor_token):
    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {doctor_token}"})
    assert r.status_code == 200
    data = r.json()

    assert data["role"] == "doctor"
    assert data["organization_id"] is not None
    assert data["branch_id"] is not None


def test_st03_doctor_appointments_returns_200(client, db, doctor_token):
    """
    Must return 200 even if appointments list is empty,
    as long as Doctor profile exists in doctors table.
    """
    r = client.get(
        "/api/doctor/appointments",
        params={"status": "SCHEDULED"},
        headers={"Authorization": f"Bearer {doctor_token}"}
    )

    # If this fails with 404 -> your DB is missing Doctor profile row for that user.
    assert r.status_code == 200, r.text

    payload = r.json()
    assert "appointments" in payload
    assert isinstance(payload["appointments"], list)


def test_st04_patient_search_same_tenant_success(client, db, doctor_token):
    """
    Picks a patient dynamically from the same tenant as doctor.
    """
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {doctor_token}"})
    assert me.status_code == 200
    my_org = me.json()["organization_id"]
    my_branch = me.json()["branch_id"]

    patient = db.query(Patient).filter(
        Patient.organization_id == my_org,
        Patient.branch_id == my_branch
    ).first()

    if not patient:
        pytest.skip("No patient exists in same tenant as doctor in seed data")

    r = client.get(
        "/api/doctor/patients/search",
        params={"patient_uid": patient.patient_uid},
        headers={"Authorization": f"Bearer {doctor_token}"}
    )
    assert r.status_code == 200, r.text
    assert r.json()["patient"]["patient_uid"] == patient.patient_uid


def test_st05_patient_search_cross_tenant_blocked(client, db, doctor_token):
    """
    Finds any patient NOT in doctor's tenant -> must return 403.
    """
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {doctor_token}"})
    assert me.status_code == 200
    my_org = me.json()["organization_id"]
    my_branch = me.json()["branch_id"]

    other_patient = db.query(Patient).filter(
        (Patient.organization_id != my_org) | (Patient.branch_id != my_branch)
    ).first()

    if not other_patient:
        pytest.skip("No cross-tenant patient exists in seed data")

    r = client.get(
        "/api/doctor/patients/search",
        params={"patient_uid": other_patient.patient_uid},
        headers={"Authorization": f"Bearer {doctor_token}"}
    )
    assert r.status_code == 403, r.text
    assert r.json()["detail"] == "Cross-tenant access denied"


def test_st06_medical_history_view_creates_logs(client, db, doctor_token):
    """
    This validates your compliance requirement:
    viewing patient history must create:
      - PatientAccessLog row
      - AuditLog row
    """
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {doctor_token}"})
    assert me.status_code == 200
    my_org = me.json()["organization_id"]
    my_branch = me.json()["branch_id"]
    doctor_user_id = me.json()["user_id"]

    patient = db.query(Patient).filter(
        Patient.organization_id == my_org,
        Patient.branch_id == my_branch
    ).first()

    if not patient:
        pytest.skip("No patient exists in same tenant as doctor")

    before_access_logs = db.query(PatientAccessLog).filter(
        PatientAccessLog.patient_id == patient.id,
        PatientAccessLog.accessed_by == doctor_user_id
    ).count()

    before_audit_logs = db.query(AuditLog).filter(
        AuditLog.entity_type == "Patient",
        AuditLog.entity_id == patient.id,
        AuditLog.user_id == doctor_user_id
    ).count()

    r = client.get(
        f"/api/doctor/patients/{patient.id}/history",
        headers={"Authorization": f"Bearer {doctor_token}"}
    )
    assert r.status_code == 200, r.text

    after_access_logs = db.query(PatientAccessLog).filter(
        PatientAccessLog.patient_id == patient.id,
        PatientAccessLog.accessed_by == doctor_user_id
    ).count()

    after_audit_logs = db.query(AuditLog).filter(
        AuditLog.entity_type == "Patient",
        AuditLog.entity_id == patient.id,
        AuditLog.user_id == doctor_user_id
    ).count()

    assert after_access_logs == before_access_logs + 1
    assert after_audit_logs == before_audit_logs + 1


def test_st07_cross_org_doctor_blocked_from_history(client, db, doctor_token, other_org_doctor_token):
    """
    Cross-org doctor must be blocked (403) for same-tenant patient.
    """
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {doctor_token}"})
    assert me.status_code == 200
    my_org = me.json()["organization_id"]
    my_branch = me.json()["branch_id"]

    patient = db.query(Patient).filter(
        Patient.organization_id == my_org,
        Patient.branch_id == my_branch
    ).first()

    if not patient:
        pytest.skip("No patient exists in doctor tenant")

    r = client.get(
        f"/api/doctor/patients/{patient.id}/history",
        headers={"Authorization": f"Bearer {other_org_doctor_token}"}
    )
    assert r.status_code == 403, r.text
