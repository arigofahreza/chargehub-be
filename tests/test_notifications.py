TEMPLATE_PAYLOAD = {
    "name": "Low Battery Alert",
    "message": "Vehicle battery below 20%. Please schedule charging.",
    "status": "active",
    "lastSent": "2024-01-10T09:00:00",
    "category": "Alert",
}


def test_list_templates_empty(client, admin_headers):
    r = client.get("/api/v1/notifications", headers=admin_headers)
    assert r.status_code == 200
    assert r.json() == []


def test_create_template(client, admin_headers):
    r = client.post("/api/v1/notifications", json=TEMPLATE_PAYLOAD, headers=admin_headers)
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Low Battery Alert"
    assert data["category"] == "Alert"
    # employeeCount/phoneCount computed from recipientIds (none sent → 0)
    assert data["employeeCount"] == 0
    assert "id" in data


def test_create_template_with_recipients(client, admin_headers):
    payload = {**TEMPLATE_PAYLOAD, "name": "With Recipients", "recipientIds": ["id-1", "id-2"]}
    r = client.post("/api/v1/notifications", json=payload, headers=admin_headers)
    assert r.status_code == 201
    data = r.json()
    assert data["employeeCount"] == 2
    assert data["recipientIds"] == ["id-1", "id-2"]


def test_get_template_by_id(client, admin_headers):
    create = client.post("/api/v1/notifications", json=TEMPLATE_PAYLOAD, headers=admin_headers)
    tmpl_id = create.json()["id"]
    r = client.get(f"/api/v1/notifications/{tmpl_id}", headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["name"] == "Low Battery Alert"


def test_patch_template_status(client, admin_headers):
    create = client.post("/api/v1/notifications", json=TEMPLATE_PAYLOAD, headers=admin_headers)
    tmpl_id = create.json()["id"]
    r = client.patch(
        f"/api/v1/notifications/{tmpl_id}",
        json={"status": "inactive"},
        headers=admin_headers,
    )
    assert r.status_code == 200
    assert r.json()["status"] == "inactive"


def test_filter_templates_by_status(client, admin_headers):
    client.post("/api/v1/notifications", json={**TEMPLATE_PAYLOAD, "status": "active"}, headers=admin_headers)
    client.post("/api/v1/notifications", json={**TEMPLATE_PAYLOAD, "name": "T2", "status": "inactive"}, headers=admin_headers)
    r = client.get("/api/v1/notifications?status=inactive", headers=admin_headers)
    assert r.status_code == 200
    results = r.json()
    assert len(results) == 1
    assert results[0]["status"] == "inactive"
