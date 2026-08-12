def test_list_employees_empty(client):
    r = client.get("/api/v1/employees")
    assert r.status_code == 200
    assert r.json() == []


def test_create_employee(client):
    r = client.post("/api/v1/employees", json={
        "name": "John Doe",
        "email": "john@example.com",
        "jobTitle": "Driver",
        "phone": "+1-555-0100",
        "status": "active",
        "initials": "JD",
    })
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "John Doe"
    assert data["jobTitle"] == "Driver"
    assert "id" in data


def test_get_employee_by_id(client):
    create = client.post("/api/v1/employees", json={
        "name": "Jane Smith",
        "email": "jane@example.com",
        "jobTitle": "Manager",
        "phone": "+1-555-0101",
        "status": "active",
        "initials": "JS",
    })
    emp_id = create.json()["id"]
    r = client.get(f"/api/v1/employees/{emp_id}")
    assert r.status_code == 200
    assert r.json()["email"] == "jane@example.com"


def test_patch_employee_status(client):
    create = client.post("/api/v1/employees", json={
        "name": "Bob Brown",
        "email": "bob@example.com",
        "jobTitle": "Technician",
        "phone": "+1-555-0102",
        "status": "active",
        "initials": "BB",
    })
    emp_id = create.json()["id"]
    r = client.patch(f"/api/v1/employees/{emp_id}", json={"status": "on-leave"})
    assert r.status_code == 200
    assert r.json()["status"] == "on-leave"


def test_filter_employees_by_status(client):
    client.post("/api/v1/employees", json={
        "name": "Active One", "email": "a@ex.com", "jobTitle": "Driver",
        "phone": "+1-555-0001", "status": "active", "initials": "AO",
    })
    client.post("/api/v1/employees", json={
        "name": "Inactive One", "email": "b@ex.com", "jobTitle": "Driver",
        "phone": "+1-555-0002", "status": "inactive", "initials": "IO",
    })
    r = client.get("/api/v1/employees?status=inactive")
    assert r.status_code == 200
    results = r.json()
    assert len(results) == 1
    assert results[0]["status"] == "inactive"
