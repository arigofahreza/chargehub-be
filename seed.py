"""Seed database with sample data matching frontend mock data."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime, timezone
from app.database import SessionLocal
from app.models.vehicle import Vehicle
from app.models.employee import Employee
from app.models.activity import ActivityLog
from app.models.notification import NotificationTemplate
from app.models.user import User
from app.auth import hash_password


def seed():
    db = SessionLocal()
    try:
        # Admin user
        admin = db.query(User).filter(User.username == "admin").first()
        if admin:
            admin.hashed_password = hash_password("Admin@123")
            admin.role = "admin"
        else:
            db.add(User(
                username="admin",
                email="admin@chargehub.com",
                hashed_password=hash_password("Admin@123"),
                full_name="Admin User",
                role="admin",
            ))

        # Operator user
        operator = db.query(User).filter(User.username == "operator").first()
        if not operator:
            db.add(User(
                username="operator",
                email="operator@chargehub.com",
                hashed_password=hash_password("Operator@123"),
                full_name="Operator User",
                role="operator",
            ))

        # Vehicles
        vehicles = [
            Vehicle(id="veh-001", name="Tesla Model 3", fleet_id="FLT-001", make="Tesla", model="Model 3",
                    year=2022, vin="5YJ3E1EA1NF000001", battery_capacity=82.0, max_range=358.0,
                    assigned_driver="Emily Rodriguez", status="available", battery_percent=78.0,
                    photo_url="", temperature=22.5, voltage=400.0, range=279.0),
            Vehicle(id="veh-002", name="Nissan Leaf", fleet_id="FLT-002", make="Nissan", model="Leaf",
                    year=2021, vin="1N4AZ1CP1MC550002", battery_capacity=40.0, max_range=226.0,
                    assigned_driver="David Kim", status="in-use", battery_percent=45.0,
                    photo_url="", temperature=21.0, voltage=360.0, range=102.0),
            Vehicle(id="veh-003", name="Chevrolet Bolt", fleet_id="FLT-003", make="Chevrolet", model="Bolt",
                    year=2023, vin="1G1FY6S07P4000003", battery_capacity=65.0, max_range=416.0,
                    assigned_driver="Michael Chen", status="service", battery_percent=20.0,
                    photo_url="", temperature=20.0, voltage=350.0, range=83.0),
            Vehicle(id="veh-004", name="Ford F-150 Lightning", fleet_id="FLT-004", make="Ford",
                    model="F-150 Lightning", year=2023, vin="1FTEW1EV5PFC00004",
                    battery_capacity=131.0, max_range=483.0, assigned_driver="Sarah Johnson",
                    status="available", battery_percent=92.0, photo_url="",
                    temperature=23.0, voltage=800.0, range=444.0),
            Vehicle(id="veh-005", name="Rivian R1T", fleet_id="FLT-005", make="Rivian", model="R1T",
                    year=2022, vin="7FCTGAAL0NR000005", battery_capacity=135.0, max_range=505.0,
                    assigned_driver="Unassigned", status="service", battery_percent=5.0,
                    photo_url="", temperature=18.0, voltage=800.0, range=25.0),
        ]
        for v in vehicles:
            if not db.query(Vehicle).filter(Vehicle.id == v.id).first():
                db.add(v)

        # Employees
        employees = [
            Employee(id="emp-001", name="Sarah Johnson", email="sarah@chargehub.com",
                     job_title="Fleet Manager", phone="+1-555-0101", status="active", initials="SJ"),
            Employee(id="emp-002", name="Michael Chen", email="michael@chargehub.com",
                     job_title="EV Technician", phone="+1-555-0102", status="active", initials="MC"),
            Employee(id="emp-003", name="Emily Rodriguez", email="emily@chargehub.com",
                     job_title="Driver", phone="+1-555-0103", status="active", initials="ER"),
            Employee(id="emp-004", name="David Kim", email="david@chargehub.com",
                     job_title="Driver", phone="+1-555-0104", status="on-leave", initials="DK"),
            Employee(id="emp-005", name="Lisa Thompson", email="lisa@chargehub.com",
                     job_title="Operations Coordinator", phone="+1-555-0105", status="inactive", initials="LT"),
        ]
        for e in employees:
            if not db.query(Employee).filter(Employee.id == e.id).first():
                db.add(e)

        # Activity logs
        activities = [
            ActivityLog(id="act-001", date_time=datetime(2024, 1, 15, 10, 30),
                        vehicle_id="veh-001", vehicle_name="Tesla Model 3",
                        unit_id="unit-001", service_type="Charging",
                        driver="Emily Rodriguez", status="completed", created_by="sarah@chargehub.com",
                        km_driven=128.5, energy_kwh=32.4, duration_minutes=90),
            ActivityLog(id="act-002", date_time=datetime(2024, 1, 15, 14, 0),
                        vehicle_id="veh-002", vehicle_name="Nissan Leaf",
                        unit_id="unit-002", service_type="Inspection",
                        driver="David Kim", status="completed", created_by="sarah@chargehub.com",
                        km_driven=45.2, energy_kwh=11.8, duration_minutes=60),
            ActivityLog(id="act-003", date_time=datetime(2024, 1, 16, 9, 0),
                        vehicle_id="veh-003", vehicle_name="Chevrolet Bolt",
                        unit_id="unit-003", service_type="Maintenance",
                        driver="Michael Chen", status="in-progress", created_by="sarah@chargehub.com",
                        km_driven=0.0, energy_kwh=0.0, duration_minutes=120),
            ActivityLog(id="act-004", date_time=datetime(2024, 1, 16, 11, 30),
                        vehicle_id="veh-004", vehicle_name="Ford F-150 Lightning",
                        unit_id="unit-001", service_type="Charging",
                        driver="Emily Rodriguez", status="completed", created_by="sarah@chargehub.com",
                        km_driven=215.0, energy_kwh=55.2, duration_minutes=150),
            ActivityLog(id="act-005", date_time=datetime(2024, 1, 17, 8, 0),
                        vehicle_id="veh-001", vehicle_name="Tesla Model 3",
                        unit_id="unit-004", service_type="Charging",
                        driver="Emily Rodriguez", status="completed", created_by="sarah@chargehub.com",
                        km_driven=98.3, energy_kwh=25.1, duration_minutes=75),
            ActivityLog(id="act-006", date_time=datetime(2024, 1, 17, 13, 0),
                        vehicle_id="veh-005", vehicle_name="Rivian R1T",
                        unit_id="unit-002", service_type="Charging",
                        driver="Sarah Johnson", status="completed", created_by="sarah@chargehub.com",
                        km_driven=178.6, energy_kwh=48.3, duration_minutes=120),
            ActivityLog(id="act-007", date_time=datetime(2024, 1, 18, 9, 30),
                        vehicle_id="veh-002", vehicle_name="Nissan Leaf",
                        unit_id="unit-003", service_type="Charging",
                        driver="David Kim", status="completed", created_by="sarah@chargehub.com",
                        km_driven=62.1, energy_kwh=16.5, duration_minutes=45),
            ActivityLog(id="act-008", date_time=datetime(2024, 1, 18, 15, 0),
                        vehicle_id="veh-004", vehicle_name="Ford F-150 Lightning",
                        unit_id="unit-001", service_type="Charging",
                        driver="Emily Rodriguez", status="completed", created_by="sarah@chargehub.com",
                        km_driven=195.4, energy_kwh=50.1, duration_minutes=135),
        ]
        for a in activities:
            existing = db.query(ActivityLog).filter(ActivityLog.id == a.id).first()
            if existing:
                existing.duration_minutes = a.duration_minutes
                existing.energy_kwh = a.energy_kwh
            else:
                db.add(a)

        # Notification templates
        templates = [
            NotificationTemplate(id="tmpl-001", name="Low Battery Alert",
                                 message="Your assigned vehicle {vehicleName} battery is below 20%. Please schedule charging.",
                                 status="active", employee_count=8, phone_count=5,
                                 last_sent=datetime(2024, 1, 10, 9, 0)),
            NotificationTemplate(id="tmpl-002", name="Maintenance Due",
                                 message="Vehicle {vehicleName} is due for scheduled maintenance. Please contact the service team.",
                                 status="active", employee_count=3, phone_count=2,
                                 last_sent=datetime(2024, 1, 8, 14, 30)),
            NotificationTemplate(id="tmpl-003", name="Charging Complete",
                                 message="Your assigned vehicle {vehicleName} has finished charging and is ready for use.",
                                 status="active", employee_count=12, phone_count=8,
                                 last_sent=datetime(2024, 1, 15, 16, 0)),
            NotificationTemplate(id="tmpl-004", name="Trip Summary",
                                 message="Your trip summary for today: {distance} km driven. Battery remaining: {batteryLevel}%.",
                                 status="inactive", employee_count=0, phone_count=0,
                                 last_sent=datetime(2023, 12, 31, 23, 59)),
        ]
        for t in templates:
            if not db.query(NotificationTemplate).filter(NotificationTemplate.id == t.id).first():
                db.add(t)

        db.commit()
        print("Seed complete.")
        print(f"  {db.query(User).count()} users")
        print(f"  {db.query(Vehicle).count()} vehicles")
        print(f"  {db.query(Employee).count()} employees")
        print(f"  {db.query(ActivityLog).count()} activities")
        print(f"  {db.query(NotificationTemplate).count()} notification templates")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
