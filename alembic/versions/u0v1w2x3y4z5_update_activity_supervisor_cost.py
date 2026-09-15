"""update_activity_supervisor_cost

Revision ID: u0v1w2x3y4z5
Revises: t9u0v1w2x3y4
Create Date: 2026-09-12 00:01:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "u0v1w2x3y4z5"
down_revision: Union[str, None] = "t9u0v1w2x3y4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add supervisors JSON column
    op.add_column("activity_logs", sa.Column("supervisors", sa.Text(), nullable=True))
    # Migrate existing single supervisor → JSON array
    op.execute(
        "UPDATE activity_logs SET supervisors = '[\"' || supervisor || '\"]' "
        "WHERE supervisor IS NOT NULL AND supervisor != ''"
    )
    op.execute(
        "UPDATE activity_logs SET supervisors = '[]' "
        "WHERE supervisors IS NULL OR supervisors = ''"
    )
    # Drop old column
    op.drop_column("activity_logs", "supervisor")
    # Add cost column
    op.add_column("activity_logs", sa.Column("cost_rupiah", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("activity_logs", "cost_rupiah")
    op.add_column("activity_logs", sa.Column("supervisor", sa.String(), nullable=True))
    op.drop_column("activity_logs", "supervisors")
