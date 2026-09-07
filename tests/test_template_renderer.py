from unittest.mock import MagicMock
from datetime import datetime
from app.services.template_renderer import render_notification

def make_activity(**kwargs):
    activity = MagicMock()
    activity.vehicle_name = kwargs.get("vehicle_name", "Tesla Model 3")
    activity.vehicle_id = kwargs.get("vehicle_id", "VH-001")
    activity.driver = kwargs.get("driver", "Budi")
    activity.supervisor = kwargs.get("supervisor", "Andi")
    activity.service_type = kwargs.get("service_type", "Charging")
    activity.status = kwargs.get("status", "completed")
    activity.date_time = kwargs.get("date_time", datetime(2026, 9, 7, 10, 0))
    activity.km_driven = kwargs.get("km_driven", 150.5)
    activity.energy_kwh = kwargs.get("energy_kwh", 42.0)
    activity.duration_minutes = kwargs.get("duration_minutes", 60.0)
    return activity

def test_render_basic_template():
    template = "Kendaraan {{ vehicle_name }} telah {{ status }}."
    activity = make_activity()
    result = render_notification(template, activity)
    assert result == "Kendaraan Tesla Model 3 telah completed."

def test_render_driver_field():
    template = "Driver: {{ driver }}, Supervisor: {{ supervisor }}"
    activity = make_activity()
    result = render_notification(template, activity)
    assert result == "Driver: Budi, Supervisor: Andi"

def test_render_numeric_fields():
    template = "{{ km_driven }} km, {{ energy_kwh }} kWh"
    activity = make_activity()
    result = render_notification(template, activity)
    assert result == "150.5 km, 42.0 kWh"
