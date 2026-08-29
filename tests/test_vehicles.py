VEHICLE_PAYLOAD = {
    "name": "Tesla Model Y", "fleetId": "EV-001", "make": "Tesla",
    "model": "Model Y", "vin": "5YJYGDEE4MF123456",
    "batteryCapacity": 75.0, "status": "idle",
    "batteryPercent": 87.0, "photoUrl": "/img.jpg",
}


def test_list_vehicles_empty(client, operator_headers):
    resp = client.get("/api/v1/vehicles", headers=operator_headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_vehicle(client, operator_headers):
    resp = client.post("/api/v1/vehicles", json=VEHICLE_PAYLOAD, headers=operator_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Tesla Model Y"
    assert data["fleetId"] == "EV-001"
    assert "id" in data


def test_get_vehicle_by_id(client, operator_headers):
    created = client.post("/api/v1/vehicles", json={
        **VEHICLE_PAYLOAD, "fleetId": "EV-002", "vin": "LGXCE4C09P1234567",
    }, headers=operator_headers).json()
    resp = client.get(f"/api/v1/vehicles/{created['id']}", headers=operator_headers)
    assert resp.status_code == 200
    assert resp.json()["fleetId"] == "EV-002"


def test_patch_vehicle(client, operator_headers):
    created = client.post("/api/v1/vehicles", json={
        **VEHICLE_PAYLOAD, "fleetId": "EV-003", "vin": "NIO0ET5S2022A3456",
    }, headers=operator_headers).json()
    resp = client.patch(
        f"/api/v1/vehicles/{created['id']}",
        json={"batteryPercent": 50.0},
        headers=operator_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["batteryPercent"] == 50.0


def test_delete_vehicle(client, operator_headers):
    created = client.post("/api/v1/vehicles", json={
        **VEHICLE_PAYLOAD, "fleetId": "EV-004", "vin": "DEL0000001234567",
    }, headers=operator_headers).json()
    resp = client.delete(f"/api/v1/vehicles/{created['id']}", headers=operator_headers)
    assert resp.status_code == 204
    get_resp = client.get(f"/api/v1/vehicles/{created['id']}", headers=operator_headers)
    assert get_resp.status_code == 404


def test_get_nonexistent_vehicle(client, operator_headers):
    resp = client.get("/api/v1/vehicles/nonexistent-id", headers=operator_headers)
    assert resp.status_code == 404
