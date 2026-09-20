"""
Migration: add performance indexes.
Run once: python migrate_indexes.py
All statements use IF NOT EXISTS — safe to re-run.
"""
from app.database import engine
from sqlalchemy import text

INDEXES = [
    # activity_logs — hottest table
    "CREATE INDEX IF NOT EXISTS ix_activity_logs_vehicle_id ON activity_logs (vehicle_id)",
    "CREATE INDEX IF NOT EXISTS ix_activity_logs_status ON activity_logs (status)",
    "CREATE INDEX IF NOT EXISTS ix_activity_logs_date_time ON activity_logs (date_time DESC)",
    "CREATE INDEX IF NOT EXISTS ix_activity_logs_vehicle_status ON activity_logs (vehicle_id, status)",

    # notification_schedules — scheduler polls every ~30s
    "CREATE INDEX IF NOT EXISTS ix_notif_sched_activity_id ON notification_schedules (activity_id)",
    "CREATE INDEX IF NOT EXISTS ix_notif_sched_status_send_at ON notification_schedules (status, send_at)",

    # battery_drain_rates — lookup per activity create/complete
    "CREATE INDEX IF NOT EXISTS ix_battery_drain_rates_activity_id ON battery_drain_rates (activity_id)",

    # employees — name.in_() lookup per activity create
    "CREATE INDEX IF NOT EXISTS ix_employees_name ON employees (name)",

    # notification_logs — pagination by sent_at
    "CREATE INDEX IF NOT EXISTS ix_notification_logs_sent_at ON notification_logs (sent_at DESC)",
]

with engine.connect() as conn:
    for stmt in INDEXES:
        conn.execute(text(stmt))
        name = stmt.split("IF NOT EXISTS ")[1].split(" ON")[0]
        print(f"OK: {name}")
    conn.commit()

print("Done: all indexes applied.")
