ACTIVITY_PAYLOAD = {
    "dateTime": "2024-01-15T10:30:00",
    "vehicleId": "veh-001",
    "vehicleName": "Tesla Model 3",
    "unitId": "unit-001",
    "serviceType": "Charging",
    "driver": "John Doe",
    "status": "pending",
    "createdBy": "admin",
}


def test_list_activities_empty(client, operator_headers):
    r = client.get("/api/v1/activities", headers=operator_headers)
    assert r.status_code == 200
    assert r.json() == []


def test_create_activity(client, operator_headers):
    r = client.post("/api/v1/activities", json=ACTIVITY_PAYLOAD, headers=operator_headers)
    assert r.status_code == 201
    data = r.json()
    assert data["vehicleName"] == "Tesla Model 3"
    # BE always starts new activity as in-progress
    assert data["status"] == "in-progress"
    assert "id" in data


def test_get_activity_by_id(client, operator_headers):
    create = client.post("/api/v1/activities", json=ACTIVITY_PAYLOAD, headers=operator_headers)
    act_id = create.json()["id"]
    r = client.get(f"/api/v1/activities/{act_id}", headers=operator_headers)
    assert r.status_code == 200
    assert r.json()["driver"] == "John Doe"


def test_patch_activity_status(client, operator_headers):
    create = client.post("/api/v1/activities", json=ACTIVITY_PAYLOAD, headers=operator_headers)
    act_id = create.json()["id"]
    r = client.patch(
        f"/api/v1/activities/{act_id}",
        json={"status": "completed"},
        headers=operator_headers,
    )
    assert r.status_code == 200
    assert r.json()["status"] == "completed"


def test_delete_activity(client, operator_headers):
    create = client.post("/api/v1/activities", json=ACTIVITY_PAYLOAD, headers=operator_headers)
    act_id = create.json()["id"]
    r = client.delete(f"/api/v1/activities/{act_id}", headers=operator_headers)
    assert r.status_code == 204
    r2 = client.get(f"/api/v1/activities/{act_id}", headers=operator_headers)
    assert r2.status_code == 404


def test_filter_activities_by_status(client, operator_headers):
    # Create in-progress (default), then patch one to completed
    r1 = client.post("/api/v1/activities", json=ACTIVITY_PAYLOAD, headers=operator_headers)
    act1_id = r1.json()["id"]
    # Use different vehicleId to avoid auto-complete triggering
    r2 = client.post("/api/v1/activities", json={
        **ACTIVITY_PAYLOAD, "vehicleId": "veh-002",
    }, headers=operator_headers)
    act2_id = r2.json()["id"]

    client.patch(f"/api/v1/activities/{act1_id}", json={"status": "completed"}, headers=operator_headers)

    resp = client.get("/api/v1/activities?status=completed", headers=operator_headers)
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) == 1
    assert results[0]["id"] == act1_id


def test_avg_duration_endpoint(client, operator_headers):
    # Create + complete an activity with duration
    r = client.post("/api/v1/activities", json=ACTIVITY_PAYLOAD, headers=operator_headers)
    act_id = r.json()["id"]
    client.patch(f"/api/v1/activities/{act_id}", json={
        "status": "completed", "durationMinutes": 45.0,
    }, headers=operator_headers)

    resp = client.get(
        "/api/v1/activities/avg-duration?vehicleId=veh-001&serviceType=Charging",
        headers=operator_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["avgDurationMinutes"] == 45.0
