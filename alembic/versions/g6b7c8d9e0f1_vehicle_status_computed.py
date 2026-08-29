"""vehicle_status_computed

Revision ID: g6b7c8d9e0f1
Revises: f5a6b7c8d9e0
Create Date: 2026-08-18 13:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'g6b7c8d9e0f1'
down_revision: Union[str, None] = 'f5a6b7c8d9e0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Convert status column from ENUM to VARCHAR so computed values can be stored
    op.execute("ALTER TABLE vehicles ALTER COLUMN status TYPE VARCHAR USING status::VARCHAR")
    op.execute("DROP TYPE IF EXISTS vehicle_status")
    # Reset all existing statuses to 'idle' (will be overridden by computed value on read)
    op.execute("UPDATE vehicles SET status = 'idle'")


def downgrade() -> None:
    op.execute("CREATE TYPE vehicle_status AS ENUM ('available', 'in-use', 'service')")
    op.execute("UPDATE vehicles SET status = 'available'")
    op.execute(
        "ALTER TABLE vehicles ALTER COLUMN status TYPE vehicle_status "
        "USING status::vehicle_status"
    )
