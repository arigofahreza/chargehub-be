"""
Seed management data into the database.
Run once on first deploy, or to reset seed data.

Usage (from api/ directory):
    python seed_mgmt.py
    python seed_mgmt.py --force   # re-seed even if data exists
"""
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.database import engine, SessionLocal, Base
from app.models import VehicleCategory, EmployeeCategory, ActivityCategory  # noqa: F401 — registers models
from app.models import Vehicle, Employee, ActivityLog, NotificationTemplate, User  # noqa: F401


VEHICLE_CATEGORIES = ["Dump Truck", "Ekskavator", "Wheel Loader", "Motor Grader"]
EMPLOYEE_CATEGORIES = [
    {"name": "Pengawas", "role": "pengawas"},
    {"name": "Operator Loader", "role": "operator"},
    {"name": "Operator Eksavator", "role": "operator"},
    {"name": "Admin", "role": "admin"},
    {"name": "Checker", "role": "operator"},
    {"name": "Engineering", "role": "operator"},
]
ACTIVITY_CATEGORIES = [
    "Heavy Stacking", "Light Stacking", "Maintenance Access",
    "Charging", "General Activity", "Loading",
]

POLICY_RULES = [
    # pengawas
    ["pengawas", "dashboard", "read"],
    ["pengawas", "vehicles", "read"],
    ["pengawas", "vehicles", "write"],
    ["pengawas", "employees", "read"],
    ["pengawas", "employees", "write"],
    ["pengawas", "notifications", "read"],
    ["pengawas", "notifications", "write"],
    ["pengawas", "activities", "read"],
    ["pengawas", "activities", "write"],
    ["pengawas", "activities:charging", "write"],
    ["pengawas", "activities:stacking", "write"],
    ["pengawas", "categories", "read"],
    # admin (inherits pengawas via grouping policy)
    ["admin", "management", "read"],
    ["admin", "management", "write"],
    ["admin", "users", "read"],
    ["admin", "users", "write"],
    ["admin", "categories", "write"],
    # operator
    ["operator", "dashboard", "read"],
    ["operator", "vehicles", "read"],
    ["operator", "employees", "read"],
    ["operator", "notifications", "read"],
    ["operator", "activities", "read"],
    ["operator", "activities:charging", "write"],
    ["operator", "categories", "read"],
    # spotter
    ["spotter", "dashboard", "read"],
    ["spotter", "vehicles", "read"],
    ["spotter", "employees", "read"],
    ["spotter", "notifications", "read"],
    ["spotter", "activities", "read"],
    ["spotter", "activities:stacking", "write"],
    ["spotter", "categories", "read"],
]


def seed_categories(force: bool = False):
    db = SessionLocal()
    try:
        if force:
            db.query(VehicleCategory).delete()
            db.query(EmployeeCategory).delete()
            db.query(ActivityCategory).delete()
            db.commit()

        if db.query(VehicleCategory).count() == 0:
            for name in VEHICLE_CATEGORIES:
                db.add(VehicleCategory(name=name))
            print(f"  Seeded {len(VEHICLE_CATEGORIES)} vehicle categories")
        else:
            print("  Vehicle categories: already seeded, skip")

        if db.query(EmployeeCategory).count() == 0:
            for item in EMPLOYEE_CATEGORIES:
                db.add(EmployeeCategory(name=item["name"], role=item["role"]))
            print(f"  Seeded {len(EMPLOYEE_CATEGORIES)} employee categories")
        else:
            print("  Employee categories: already seeded, skip")

        if db.query(ActivityCategory).count() == 0:
            for name in ACTIVITY_CATEGORIES:
                db.add(ActivityCategory(name=name, icon_url=None))
            print(f"  Seeded {len(ACTIVITY_CATEGORIES)} activity categories (no icons — upload via management UI)")
        else:
            print("  Activity categories: already seeded, skip")

        db.commit()
    finally:
        db.close()


def seed_policy(force: bool = False):
    from app.rbac.enforcer import get_enforcer
    e = get_enforcer()

    if force:
        e.delete_all_policy()
        print("  Cleared existing policy rules")

    if e.get_policy():
        print("  Casbin policy: already seeded, skip")
        return

    e.add_policies(POLICY_RULES)
    e.add_grouping_policy("admin", "pengawas")
    print(f"  Seeded {len(POLICY_RULES)} policy rules + 1 grouping rule")


def main():
    parser = argparse.ArgumentParser(description="Seed management data")
    parser.add_argument("--force", action="store_true", help="Re-seed even if data exists")
    args = parser.parse_args()

    print("Creating tables...")
    Base.metadata.create_all(bind=engine)

    # casbin adapter creates casbin_rule table
    from app.rbac.enforcer import get_enforcer
    get_enforcer()

    print("Seeding categories...")
    seed_categories(force=args.force)

    print("Seeding Casbin policy...")
    seed_policy(force=args.force)

    print("Done.")


if __name__ == "__main__":
    main()
