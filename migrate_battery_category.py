"""
Migration: add category column to battery_drain_rates.
Run once: python migrate_battery_category.py
"""
from app.database import engine
from sqlalchemy import text, inspect as sa_inspect

insp = sa_inspect(engine)
if "battery_drain_rates" not in insp.get_table_names():
    print("Table battery_drain_rates not found — skipping.")
else:
    cols = [c["name"] for c in insp.get_columns("battery_drain_rates")]
    if "category" in cols:
        print("Column already exists — nothing to do.")
    else:
        with engine.connect() as conn:
            conn.execute(text(
                "ALTER TABLE battery_drain_rates ADD COLUMN category VARCHAR NOT NULL DEFAULT 'penurunan'"
            ))
            conn.commit()
        print("Done: category column added, existing rows default to 'penurunan'.")
