import os
import csv
import json
import uuid
import pytest
import pandas as pd

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from models import User, UserRole

# =========================
# IST TIMEZONE CONFIG
# =========================
IST = ZoneInfo("Asia/Kolkata")


def ist_now_iso():
    return datetime.now(IST).isoformat(timespec="seconds")


# =========================
# REPORT PATHS
# =========================
REPORT_DIR = os.path.join(os.getcwd(), "test_reports")
os.makedirs(REPORT_DIR, exist_ok=True)

TEST_CASES_CSV = os.path.join(REPORT_DIR, "test_cases.csv")
TEST_RUNS_CSV = os.path.join(REPORT_DIR, "test_runs.csv")
TEST_WARNINGS_CSV = os.path.join(REPORT_DIR, "test_warnings.csv")
TEST_CASES_JSONL = os.path.join(REPORT_DIR, "test_cases.jsonl")


# =========================
# HELPERS: APPEND WITH NEW COLUMNS
# =========================
def append_row_csv(file_path: str, row: dict):
    if not os.path.exists(file_path):
        with open(file_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(row.keys()))
            writer.writeheader()
            writer.writerow(row)
        return

    df_existing = pd.read_csv(file_path)

    # expand columns if new keys appear
    for col in row.keys():
        if col not in df_existing.columns:
            df_existing[col] = None

    # ensure row has all existing columns
    for col in df_existing.columns:
        if col not in row:
            row[col] = None

    df_new = pd.DataFrame([row], columns=df_existing.columns)
    df_out = pd.concat([df_existing, df_new], ignore_index=True)
    df_out.to_csv(file_path, index=False)


def append_row_jsonl(file_path: str, row: dict):
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


# =========================
# PYTEST HOOKS (REPORTING)
# =========================
_GLOBAL_WARNING_BUFFER = []


def pytest_configure(config):
    config._ihorms_run_id = str(uuid.uuid4())
    config._ihorms_run_start_ist = ist_now_iso()
    config._ihorms_case_rows = []


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call":
        return

    run_id = item.config._ihorms_run_id

    # Try to capture endpoint metadata from param matrix tests
    endpoint = None
    method = None
    allowed_roles = None

    try:
        if hasattr(item, "callspec"):
            params = item.callspec.params
            method = params.get("method")
            endpoint = params.get("url")
            allowed_roles = params.get("allowed_roles")
    except Exception:
        pass

    row = {
        "run_id": run_id,
        "timestamp_ist": ist_now_iso(),
        "nodeid": report.nodeid,
        "test_name": item.name,
        "status": report.outcome,
        "duration_sec": round(report.duration, 6),
        "http_method": method,
        "endpoint": endpoint,
        "allowed_roles": json.dumps(allowed_roles) if allowed_roles is not None else None,
    }

    if report.failed:
        row["error_message"] = str(report.longrepr)

    item.config._ihorms_case_rows.append(row)


def pytest_warning_recorded(warning_message, when, nodeid, location):
    try:
        row = {
            "timestamp_ist": ist_now_iso(),
            "nodeid": nodeid,
            "when": when,
            "category": warning_message.category.__name__,
            "message": str(warning_message.message),
            "filename": location[0] if location else None,
            "lineno": location[1] if location else None,
        }
    except Exception:
        row = {
            "timestamp_ist": ist_now_iso(),
            "nodeid": nodeid,
            "when": when,
            "category": None,
            "message": str(warning_message),
            "filename": None,
            "lineno": None,
        }

    _GLOBAL_WARNING_BUFFER.append(row)


def pytest_sessionfinish(session, exitstatus):
    config = session.config
    run_id = config._ihorms_run_id
    end_time = ist_now_iso()

    for row in config._ihorms_case_rows:
        append_row_csv(TEST_CASES_CSV, row)
        append_row_jsonl(TEST_CASES_JSONL, row)

    for w in _GLOBAL_WARNING_BUFFER:
        w["run_id"] = run_id
        append_row_csv(TEST_WARNINGS_CSV, w)

    total = len(config._ihorms_case_rows)
    passed = sum(1 for r in config._ihorms_case_rows if r["status"] == "passed")
    failed = sum(1 for r in config._ihorms_case_rows if r["status"] == "failed")
    skipped = sum(1 for r in config._ihorms_case_rows if r["status"] == "skipped")

    summary = {
        "run_id": run_id,
        "started_at_ist": config._ihorms_run_start_ist,
        "finished_at_ist": end_time,
        "exit_status": exitstatus,
        "total_tests": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "warnings_count": len(_GLOBAL_WARNING_BUFFER),
    }

    append_row_csv(TEST_RUNS_CSV, summary)


# =========================
# DB + CLIENT FIXTURES
# =========================
DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    os.getenv("DATABASE_URL", "postgresql://postgres:chiragh@localhost:5432/ihorms_db")
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)


@pytest.fixture(scope="session")
def client():
    return TestClient(app)


@pytest.fixture()
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def login_as(client: TestClient, email: str, password: str) -> str:
    r = client.post("/api/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


@pytest.fixture()
def token_factory(client, db):
    """
    Creates real token by logging into DB user table.
    Uses default passwords per role (customize here).
    """
    DEFAULT_PASSWORDS = {
        UserRole.SUPER_ADMIN: "superadmin1",
        UserRole.ORG_ADMIN: "orgadmin1",
        UserRole.BRANCH_ADMIN: "dean1",
        UserRole.DOCTOR: "doctor123",
        UserRole.NURSE: "nurse123",
        UserRole.RECEPTIONIST: "receptionist123",
        UserRole.PHARMACY_STAFF: "pharmacy123",
        UserRole.PATIENT: "patient123",
    }

    def _make(role: UserRole, password: str | None = None) -> str:
        user = db.query(User).filter(User.role == role, User.is_active == True).first()
        assert user, f"No seeded active user found for role={role}"

        pwd = password or DEFAULT_PASSWORDS.get(role)
        assert pwd, f"No default password configured for role={role}"

        return login_as(client, user.email, pwd)

    return _make


@pytest.fixture()
def doctor_token(token_factory):
    return token_factory(UserRole.DOCTOR)


@pytest.fixture()
def other_org_doctor_token(client, db):
    """
    Requires at least 2 doctors across 2 orgs in seed data.
    """
    doc1 = db.query(User).filter(User.role == UserRole.DOCTOR).first()
    assert doc1

    doc2 = db.query(User).filter(
        User.role == UserRole.DOCTOR,
        User.organization_id != doc1.organization_id
    ).first()

    if not doc2:
        pytest.skip("No cross-org doctor exists in seed data")

    return login_as(client, doc2.email, "doctor123")
from models import UserRole

ROLE_MAP = {
    "super_admin": UserRole.SUPER_ADMIN,
    "org_admin": UserRole.ORG_ADMIN,
    "branch_admin": UserRole.BRANCH_ADMIN,
    "doctor": UserRole.DOCTOR,
    "nurse": UserRole.NURSE,
    "receptionist": UserRole.RECEPTIONIST,
    "pharmacy_staff": UserRole.PHARMACY_STAFF,
    "patient": UserRole.PATIENT,
}

@pytest.fixture()
def auth_header_factory(token_factory):
    """
    Returns Authorization header using REAL login from DB users table.
    """
    def _factory(role: str):
        enum_role = ROLE_MAP.get(role)
        assert enum_role, f"Unknown role string: {role}"

        token = token_factory(enum_role)
        return {"Authorization": f"Bearer {token}"}

    return _factory
