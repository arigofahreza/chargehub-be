EMPLOYEE_PAYLOAD = {
    "name": "John Doe",
    "email": "john@example.com",
    "jobTitle": "Driver",
    "phone": "+1-555-0100",
    "status": "active",
    "initials": "JD",
}


def test_list_employees_empty(client, admin_headers):
    r = client.get("/api/v1/employees", headers=admin_headers)
    assert r.status_code == 200
    assert r.json() == []


def test_create_employee(client, admin_headers):
    r = client.post("/api/v1/employees", json=EMPLOYEE_PAYLOAD, headers=admin_headers)
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "John Doe"
    assert data["jobTitle"] == "Driver"
    assert "id" in data


def test_get_employee_by_id(client, admin_headers):
    create = client.post("/api/v1/employees", json={
        **EMPLOYEE_PAYLOAD, "email": "jane@example.com", "name": "Jane Smith", "initials": "JS",
    }, headers=admin_headers)
    emp_id = create.json()["id"]
    r = client.get(f"/api/v1/employees/{emp_id}", headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["email"] == "jane@example.com"


def test_patch_employee_status(client, admin_headers):
    create = client.post("/api/v1/employees", json={
        **EMPLOYEE_PAYLOAD, "email": "bob@example.com", "name": "Bob Brown", "initials": "BB",
    }, headers=admin_headers)
    emp_id = create.json()["id"]
    r = client.patch(f"/api/v1/employees/{emp_id}", json={"status": "on-leave"}, headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["status"] == "on-leave"


def test_delete_employee(client, admin_headers):
    create = client.post("/api/v1/employees", json={
        **EMPLOYEE_PAYLOAD, "email": "del@example.com", "name": "Del User", "initials": "DU",
    }, headers=admin_headers)
    emp_id = create.json()["id"]
    r = client.delete(f"/api/v1/employees/{emp_id}", headers=admin_headers)
    assert r.status_code == 204
    r2 = client.get(f"/api/v1/employees/{emp_id}", headers=admin_headers)
    assert r2.status_code == 404


def test_filter_employees_by_status(client, admin_headers):
    client.post("/api/v1/employees", json={
        **EMPLOYEE_PAYLOAD, "email": "a@ex.com", "initials": "AO", "status": "active",
    }, headers=admin_headers)
    client.post("/api/v1/employees", json={
        **EMPLOYEE_PAYLOAD, "email": "b@ex.com", "name": "Inactive One", "initials": "IO", "status": "inactive",
    }, headers=admin_headers)
    r = client.get("/api/v1/employees?status=inactive", headers=admin_headers)
    assert r.status_code == 200
    results = r.json()
    assert len(results) == 1
    assert results[0]["status"] == "inactive"
