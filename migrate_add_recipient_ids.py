"""Add recipient_ids column to notification_templates table."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text(
        "ALTER TABLE notification_templates "
        "ADD COLUMN IF NOT EXISTS recipient_ids TEXT DEFAULT '[]'"
    ))
    conn.commit()
    print("Migration complete: recipient_ids column added.")
