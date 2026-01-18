"""
Functional tests for authentication and super admin endpoints
"""
import pytest
from models import UserRole, User
from utils.helpers import hash_password

def test_login_success(client, db):
    # Setup user
    password = "password123"
    user = User(
        email="login@test.com",
        password_hash=hash_password(password),
        first_name="Login",
        last_name="Test",
        role=UserRole.SUPER_ADMIN,
        is_active=True
    )
    db.add(user)
    db.commit()
    
    response = client.post("/auth/login", json={
        "email": "login@test.com",
        "password": password
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "login@test.com"

def test_create_organization_auth(client, super_admin_token):
    # This token is pre-generated in conftest.py for user with ID 1
    # We need to make sure user 1 exists in DB for proper validation if dependency checks it
    # However, my dependencies mock just returns the user object if they exist.
    # In conftest, I didn't create the user in DB, but JWT payload has ID 1.
    # Let's ensure the user exists for functional tests.
    pass

def test_super_admin_create_org(client, db):
    # Create the super admin user in DB
    admin = User(
        id=1,
        email="super@ihorms.com",
        password_hash=hash_password("admin"),
        first_name="Super",
        last_name="Admin",
        role=UserRole.SUPER_ADMIN,
        is_active=True
    )
    db.add(admin)
    db.commit()
    
    token = "Bearer test_token" 
    # Mocking token validation if needed, but conftest uses real jwt_handler
    from auth.jwt_handler import jwt_handler
    access_token = jwt_handler.create_access_token({"sub": "1", "role": "super_admin"})
    
    response = client.post(
        "/super-admin/organizations",
        json={
            "name": "Global Health",
            "admin_email": "global_admin@health.com",
            "admin_first_name": "Global",
            "admin_last_name": "Admin"
        },
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["name"] == "Global Health"
