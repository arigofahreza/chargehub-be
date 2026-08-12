TEMPLATE_PAYLOAD = {
    "name": "Low Battery Alert",
    "message": "Vehicle battery below 20%. Please schedule charging.",
    "status": "active",
    "employeeCount": 5,
    "phoneCount": 3,
    "lastSent": "2024-01-10T09:00:00",
}


def test_list_templates_empty(client):
    r = client.get("/api/v1/notifications")
    assert r.status_code == 200
    assert r.json() == []


def test_create_template(client):
    r = client.post("/api/v1/notifications", json=TEMPLATE_PAYLOAD)
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Low Battery Alert"
    assert data["employeeCount"] == 5
    assert "id" in data


def test_get_template_by_id(client):
    create = client.post("/api/v1/notifications", json=TEMPLATE_PAYLOAD)
    tmpl_id = create.json()["id"]
    r = client.get(f"/api/v1/notifications/{tmpl_id}")
    assert r.status_code == 200
    assert r.json()["phoneCount"] == 3


def test_patch_template_status(client):
    create = client.post("/api/v1/notifications", json=TEMPLATE_PAYLOAD)
    tmpl_id = create.json()["id"]
    r = client.patch(f"/api/v1/notifications/{tmpl_id}", json={"status": "inactive"})
    assert r.status_code == 200
    assert r.json()["status"] == "inactive"


def test_filter_templates_by_status(client):
    client.post("/api/v1/notifications", json={**TEMPLATE_PAYLOAD, "status": "active"})
    client.post("/api/v1/notifications", json={**TEMPLATE_PAYLOAD, "name": "T2", "status": "inactive"})
    r = client.get("/api/v1/notifications?status=inactive")
    assert r.status_code == 200
    results = r.json()
    assert len(results) == 1
    assert results[0]["status"] == "inactive"
