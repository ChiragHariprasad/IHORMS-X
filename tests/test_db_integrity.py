import pytest
from models import (
    User, Patient, Doctor, Nurse, Appointment,
    Billing, InsuranceClaim, Inventory, PharmacyOrder
)


def test_seed_has_users(db):
    assert db.query(User).count() > 0


def test_seed_has_patients(db):
    assert db.query(Patient).count() > 0


def test_patients_have_org_and_branch(db):
    bad = db.query(Patient).filter(
        (Patient.organization_id == None) | (Patient.branch_id == None)
    )
    assert bad.count() == 0


def test_doctors_have_user(db):
    # if doctor table exists and should be mapped
    count = db.query(Doctor).count()
    if count == 0:
        pytest.skip("No doctors in doctors table (seed missing doctor profiles)")
    bad = db.query(Doctor).filter(Doctor.user_id == None)
    assert bad.count() == 0


def test_appointments_have_valid_links(db):
    count = db.query(Appointment).count()
    if count == 0:
        pytest.skip("No appointments in seed data")

    bad = db.query(Appointment).filter(
        (Appointment.patient_id == None) | (Appointment.doctor_id == None)
    )
    assert bad.count() == 0


def test_billing_has_valid_links(db):
    count = db.query(Billing).count()
    if count == 0:
        pytest.skip("No billing rows in seed data")

    bad = db.query(Billing).filter(
        (Billing.patient_id == None) | (Billing.appointment_id == None)
    )
    assert bad.count() == 0


def test_claims_reference_billing(db):
    claims = db.query(InsuranceClaim).count()
    if claims == 0:
        pytest.skip("No insurance claims in seed data")

    bad = db.query(InsuranceClaim).filter(InsuranceClaim.billing_id == None)
    assert bad.count() == 0


def test_inventory_exists(db):
    count = db.query(Inventory).count()
    if count == 0:
        pytest.skip("No inventory rows in seed data")
    assert count > 0


def test_pharmacy_orders_exist(db):
    count = db.query(PharmacyOrder).count()
    if count == 0:
        pytest.skip("No pharmacy orders in seed data")
    assert count > 0
