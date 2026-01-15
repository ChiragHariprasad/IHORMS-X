from models import User, UserRole


def test_health_check(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_login_success_real_db(client, db):
    doctor = db.query(User).filter(User.role == UserRole.DOCTOR).first()
    assert doctor, "No doctor found in seeded DB"

    res = client.post("/api/auth/login", json={
        "email": doctor.email,
        "password": "doctor123"
    })

    assert res.status_code == 200, res.text
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == doctor.email
    assert data["user"]["role"] == "doctor"


def test_login_invalid_password(client, db):
    doctor = db.query(User).filter(User.role == UserRole.DOCTOR).first()
    assert doctor

    res = client.post("/api/auth/login", json={
        "email": doctor.email,
        "password": "wrongpassword"
    })
    assert res.status_code == 401
    assert res.json()["detail"] == "Invalid credentials"


def test_me_requires_token(client):
    res = client.get("/api/auth/me")
    assert res.status_code in (401, 403)


def test_logout_requires_token(client):
    res = client.post("/api/auth/logout")
    assert res.status_code in (401, 403)
