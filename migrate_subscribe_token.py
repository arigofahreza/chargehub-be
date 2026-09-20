"""
Migration: add subscribe_token column to employees.
Run once: python migrate_subscribe_token.py
"""
from app.database import engine
from sqlalchemy import text, inspect as sa_inspect

insp = sa_inspect(engine)
if "employees" not in insp.get_table_names():
    print("Table employees not found — skipping.")
else:
    cols = [c["name"] for c in insp.get_columns("employees")]
    if "subscribe_token" in cols:
        print("Column already exists — nothing to do.")
    else:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE employees ADD COLUMN subscribe_token VARCHAR"))
            conn.commit()
        print("Done: subscribe_token column added.")
