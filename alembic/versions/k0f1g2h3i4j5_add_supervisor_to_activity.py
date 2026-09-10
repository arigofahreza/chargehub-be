"""add_supervisor_to_activity

Revision ID: k0f1g2h3i4j5
Revises: j9e0f1g2h3i4
Create Date: 2026-09-02 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "k0f1g2h3i4j5"
down_revision: Union[str, None] = "j9e0f1g2h3i4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("activity_logs", sa.Column("supervisor", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("activity_logs", "supervisor")
