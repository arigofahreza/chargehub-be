def test_list_vehicles_empty(client):
    resp = client.get("/api/v1/vehicles")
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_vehicle(client):
    payload = {
        "name": "Tesla Model Y", "fleetId": "EV-001", "make": "Tesla",
        "model": "Model Y", "year": 2023, "vin": "5YJYGDEE4MF123456",
        "batteryCapacity": 75.0, "maxRange": 533.0, "assignedDriver": "James",
        "status": "available", "batteryPercent": 87.0, "photoUrl": "/img.jpg",
        "temperature": 24.0, "voltage": 394.0, "range": 463.0,
    }
    resp = client.post("/api/v1/vehicles", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Tesla Model Y"
    assert data["fleetId"] == "EV-001"
    assert "id" in data


def test_get_vehicle_by_id(client):
    payload = {
        "name": "BYD Atto 3", "fleetId": "EV-002", "make": "BYD", "model": "Atto 3",
        "year": 2023, "vin": "LGXCE4C09P1234567", "batteryCapacity": 60.0,
        "maxRange": 420.0, "assignedDriver": "Sarah", "status": "in-use",
        "batteryPercent": 62.0, "photoUrl": "/img2.jpg",
        "temperature": 26.0, "voltage": 380.0, "range": 260.0,
    }
    created = client.post("/api/v1/vehicles", json=payload).json()
    resp = client.get(f"/api/v1/vehicles/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["fleetId"] == "EV-002"


def test_patch_vehicle(client):
    payload = {
        "name": "NIO ET5", "fleetId": "EV-003", "make": "NIO", "model": "ET5",
        "year": 2022, "vin": "NIO0ET5S2022A3456", "batteryCapacity": 75.0,
        "maxRange": 560.0, "assignedDriver": "Mike", "status": "available",
        "batteryPercent": 95.0, "photoUrl": "/img3.jpg",
        "temperature": 23.0, "voltage": 396.0, "range": 532.0,
    }
    created = client.post("/api/v1/vehicles", json=payload).json()
    resp = client.patch(f"/api/v1/vehicles/{created['id']}", json={"status": "in-use"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "in-use"


def test_filter_vehicles_by_status(client):
    for i, status in enumerate(["available", "available", "in-use"]):
        client.post("/api/v1/vehicles", json={
            "name": f"V-{i}", "fleetId": f"EV-{i:03d}", "make": "X", "model": "X",
            "year": 2023, "vin": f"VIN{i:010d}", "batteryCapacity": 60.0,
            "maxRange": 400.0, "assignedDriver": "X", "status": status,
            "batteryPercent": 80.0, "photoUrl": "/x.jpg",
            "temperature": 25.0, "voltage": 380.0, "range": 300.0,
        })
    resp = client.get("/api/v1/vehicles?status=available")
    assert len(resp.json()) == 2
