"""
Pytest configuration and fixtures for IHORMS
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import get_db
from models import Base, User, UserRole
from auth.jwt_handler import jwt_handler
from utils.helpers import hash_password

# Use an in-memory SQLite database for faster testing
# Note: For production-grade integration, use a separate Postgres test DB
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db(setup_db):
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def super_admin_token():
    token_data = {"sub": "1", "role": UserRole.SUPER_ADMIN.value}
    return jwt_handler.create_access_token(data=token_data)

@pytest.fixture
def org_admin_token():
    token_data = {"sub": "2", "role": UserRole.ORG_ADMIN.value}
    return jwt_handler.create_access_token(data=token_data)

@pytest.fixture
def branch_admin_token():
    token_data = {"sub": "3", "role": UserRole.BRANCH_ADMIN.value}
    return jwt_handler.create_access_token(data=token_data)

@pytest.fixture
def doctor_token():
    token_data = {"sub": "4", "role": UserRole.DOCTOR.value}
    return jwt_handler.create_access_token(data=token_data)

@pytest.fixture
def nurse_token():
    token_data = {"sub": "5", "role": UserRole.NURSE.value}
    return jwt_handler.create_access_token(data=token_data)

@pytest.fixture
def receptionist_token():
    token_data = {"sub": "6", "role": UserRole.RECEPTIONIST.value}
    return jwt_handler.create_access_token(data=token_data)

@pytest.fixture
def patient_token():
    token_data = {"sub": "7", "role": UserRole.PATIENT.value}
    return jwt_handler.create_access_token(data=token_data)

@pytest.fixture
def create_test_user(db):
    def _create_user(email, role, organization_id=None, branch_id=None):
        user = User(
            email=email,
            password_hash=hash_password("password123"),
            first_name="Test",
            last_name="User",
            role=role,
            organization_id=organization_id,
            branch_id=branch_id,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    return _create_user
