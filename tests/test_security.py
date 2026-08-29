"""
Security tests: verify auth enforcement on every protected route.
"""
import pytest

STRONG_PW = "Secret@123"

# Routes requiring any valid user (operator or admin)
AUTH_REQUIRED_ROUTES = [
    ("GET",    "/api/v1/vehicles"),
    ("GET",    "/api/v1/activities"),
    ("GET",    "/api/v1/dashboard/fleet-status"),
    ("GET",    "/api/v1/dashboard/stats"),
    ("GET",    "/api/v1/dashboard/usage-trend"),
    ("GET",    "/api/v1/dashboard/top-energy"),
    ("GET",    "/api/v1/dashboard/avg-kwh-per-vehicle"),
    ("GET",    "/api/v1/dashboard/battery-hourly"),
    ("GET",    "/api/v1/job-titles"),
]

# Routes requiring admin role
ADMIN_ONLY_ROUTES = [
    ("GET",    "/api/v1/employees"),
    ("GET",    "/api/v1/notifications"),
]

ALL_PROTECTED = AUTH_REQUIRED_ROUTES + ADMIN_ONLY_ROUTES


# ── No token ─────────────────────────────────────────────────────────────────

def test_no_token_returns_401(client):
    for method, path in ALL_PROTECTED:
        r = client.request(method, path)
        assert r.status_code == 401, f"Expected 401 for {method} {path}, got {r.status_code}"


# ── Invalid / malformed tokens ────────────────────────────────────────────────

@pytest.mark.parametrize("bad_auth", [
    "Bearer invalid.token.here",
    "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.bad.sig",
    "Basic dXNlcjpwYXNz",
    "Bearer",
    "token-without-bearer-prefix",
])
def test_invalid_token_returns_401(client, bad_auth):
    headers = {"Authorization": bad_auth}
    r = client.get("/api/v1/vehicles", headers=headers)
    assert r.status_code == 401, f"Bad token '{bad_auth}' should return 401, got {r.status_code}"


def test_nonexistent_user_in_token_returns_401(client):
    from app.auth import create_access_token
    fake_token = create_access_token({"sub": "00000000-0000-0000-0000-000000000000"})
    headers = {"Authorization": f"Bearer {fake_token}"}
    r = client.get("/api/v1/vehicles", headers=headers)
    assert r.status_code == 401


# ── Operator: can access user-level, blocked from admin-only ──────────────────

def test_operator_allowed_on_auth_required_routes(client, operator_headers):
    for method, path in AUTH_REQUIRED_ROUTES:
        r = client.request(method, path, headers=operator_headers)
        assert r.status_code == 200, f"Operator should access {method} {path}, got {r.status_code}"


def test_operator_blocked_from_admin_routes(client, operator_headers):
    for method, path in ADMIN_ONLY_ROUTES:
        r = client.request(method, path, headers=operator_headers)
        assert r.status_code == 403, f"Operator should be 403 on {method} {path}, got {r.status_code}"


# ── Admin: can access everything ──────────────────────────────────────────────

def test_admin_allowed_on_all_routes(client, admin_headers):
    for method, path in ALL_PROTECTED:
        r = client.request(method, path, headers=admin_headers)
        assert r.status_code == 200, f"Admin should access {method} {path}, got {r.status_code}"


# ── Write operations: operator blocked from admin-only writes ─────────────────

def test_operator_cannot_create_employee(client, operator_headers):
    r = client.post("/api/v1/employees", json={
        "name": "Test", "jobTitle": "Driver", "phone": "+62000",
        "status": "active", "initials": "T",
    }, headers=operator_headers)
    assert r.status_code == 403


def test_operator_cannot_create_notification(client, operator_headers):
    r = client.post("/api/v1/notifications", json={
        "name": "Test", "message": "msg", "status": "active",
        "lastSent": "2024-01-01T00:00:00",
    }, headers=operator_headers)
    assert r.status_code == 403


def test_operator_cannot_delete_employee(client, admin_headers, operator_headers):
    create = client.post("/api/v1/employees", json={
        "name": "ToDelete", "jobTitle": "Driver", "phone": "+62000",
        "status": "active", "initials": "TD",
    }, headers=admin_headers)
    emp_id = create.json()["id"]
    r = client.delete(f"/api/v1/employees/{emp_id}", headers=operator_headers)
    assert r.status_code == 403


# ── Auth endpoints: public (no token required) ────────────────────────────────

def test_register_and_login_are_public(client):
    r = client.post("/api/v1/auth/register", json={
        "username": "pubuser", "email": "pub@test.com",
        "password": STRONG_PW, "firstName": "Pub",
    })
    assert r.status_code == 201

    r = client.post("/api/v1/auth/login", json={
        "username": "pubuser", "password": STRONG_PW,
    })
    assert r.status_code == 200
    assert "accessToken" in r.json()


# ── /users/me: authenticated user only ───────────────────────────────────────

def test_get_me_requires_auth(client):
    r = client.get("/api/v1/users/me")
    assert r.status_code == 401


def test_get_me_returns_current_user(client, operator_headers):
    r = client.get("/api/v1/users/me", headers=operator_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["username"] == "opertest"
    assert data["role"] == "operator"


def test_get_me_admin_role(client, admin_headers):
    r = client.get("/api/v1/users/me", headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["role"] == "admin"
