"""
Migration: create vehicle_battery_states table.
Run once: python migrate_vehicle_battery_state.py
"""
from app.database import engine, Base
from app.models.vehicle_battery_state import VehicleBatteryState  # noqa: F401 — registers with Base

from sqlalchemy import inspect as sa_inspect

insp = sa_inspect(engine)
if "vehicle_battery_states" in insp.get_table_names():
    print("Table already exists — nothing to do.")
else:
    Base.metadata.create_all(bind=engine, tables=[Base.metadata.tables["vehicle_battery_states"]])
    print("Done: vehicle_battery_states created.")
