ACTIVITY_PAYLOAD = {
    "dateTime": "2024-01-15T10:30:00",
    "vehicleId": "veh-001",
    "vehicleName": "Tesla Model 3",
    "unitId": "unit-001",
    "serviceType": "Charging",
    "driver": "John Doe",
    "status": "completed",
    "createdBy": "admin",
}


def test_list_activities_empty(client):
    r = client.get("/api/v1/activities")
    assert r.status_code == 200
    assert r.json() == []


def test_create_activity(client):
    r = client.post("/api/v1/activities", json=ACTIVITY_PAYLOAD)
    assert r.status_code == 201
    data = r.json()
    assert data["vehicleName"] == "Tesla Model 3"
    assert data["status"] == "completed"
    assert "id" in data


def test_get_activity_by_id(client):
    create = client.post("/api/v1/activities", json=ACTIVITY_PAYLOAD)
    act_id = create.json()["id"]
    r = client.get(f"/api/v1/activities/{act_id}")
    assert r.status_code == 200
    assert r.json()["driver"] == "John Doe"


def test_patch_activity_status(client):
    create = client.post("/api/v1/activities", json=ACTIVITY_PAYLOAD)
    act_id = create.json()["id"]
    r = client.patch(f"/api/v1/activities/{act_id}", json={"status": "in-progress"})
    assert r.status_code == 200
    assert r.json()["status"] == "in-progress"


def test_filter_activities_by_status(client):
    client.post("/api/v1/activities", json={**ACTIVITY_PAYLOAD, "status": "completed"})
    client.post("/api/v1/activities", json={**ACTIVITY_PAYLOAD, "status": "pending"})
    r = client.get("/api/v1/activities?status=pending")
    assert r.status_code == 200
    results = r.json()
    assert len(results) == 1
    assert results[0]["status"] == "pending"
