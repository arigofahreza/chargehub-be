def test_register_user(client):
    r = client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "secret123",
        "fullName": "Test User",
    })
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == "test@example.com"
    assert data["fullName"] == "Test User"
    assert "id" in data


def test_register_duplicate_email(client):
    payload = {"email": "dup@example.com", "password": "pass", "fullName": "User"}
    client.post("/api/v1/auth/register", json=payload)
    r = client.post("/api/v1/auth/register", json=payload)
    assert r.status_code == 400


def test_login_success(client):
    client.post("/api/v1/auth/register", json={
        "email": "login@example.com",
        "password": "mypass",
        "fullName": "Login User",
    })
    r = client.post("/api/v1/auth/login", json={
        "email": "login@example.com",
        "password": "mypass",
    })
    assert r.status_code == 200
    data = r.json()
    assert "accessToken" in data
    assert data["tokenType"] == "bearer"
    assert data["user"]["email"] == "login@example.com"


def test_login_wrong_password(client):
    client.post("/api/v1/auth/register", json={
        "email": "wrong@example.com",
        "password": "correct",
        "fullName": "Wrong User",
    })
    r = client.post("/api/v1/auth/login", json={
        "email": "wrong@example.com",
        "password": "incorrect",
    })
    assert r.status_code == 401
