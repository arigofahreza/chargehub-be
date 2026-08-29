STRONG_PW = "Secret@123"


def test_register_user(client):
    r = client.post("/api/v1/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": STRONG_PW,
        "firstName": "Test",
        "lastName": "User",
    })
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == "test@example.com"
    assert data["fullName"] == "Test User"
    assert "id" in data


def test_register_weak_password(client):
    r = client.post("/api/v1/auth/register", json={
        "username": "weakuser",
        "email": "weak@example.com",
        "password": "password",
        "firstName": "Weak",
    })
    assert r.status_code == 422


def test_register_duplicate_email(client):
    payload = {
        "username": "dupuser",
        "email": "dup@example.com",
        "password": STRONG_PW,
        "firstName": "Dup",
    }
    client.post("/api/v1/auth/register", json=payload)
    payload["username"] = "dupuser2"
    r = client.post("/api/v1/auth/register", json=payload)
    assert r.status_code == 400


def test_login_success(client):
    client.post("/api/v1/auth/register", json={
        "username": "loginuser",
        "email": "login@example.com",
        "password": STRONG_PW,
        "firstName": "Login",
    })
    r = client.post("/api/v1/auth/login", json={
        "username": "loginuser",
        "password": STRONG_PW,
    })
    assert r.status_code == 200
    data = r.json()
    assert "accessToken" in data
    assert data["tokenType"] == "bearer"
    assert data["user"]["email"] == "login@example.com"


def test_login_wrong_password(client):
    client.post("/api/v1/auth/register", json={
        "username": "wronguser",
        "email": "wrong@example.com",
        "password": STRONG_PW,
        "firstName": "Wrong",
    })
    r = client.post("/api/v1/auth/login", json={
        "username": "wronguser",
        "password": "incorrect",
    })
    assert r.status_code == 401
