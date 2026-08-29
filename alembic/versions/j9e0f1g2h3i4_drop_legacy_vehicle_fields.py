"""drop_legacy_vehicle_fields

Revision ID: j9e0f1g2h3i4
Revises: i8d9e0f1g2h3
Create Date: 2026-08-30 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "j9e0f1g2h3i4"
down_revision: Union[str, None] = "i8d9e0f1g2h3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("vehicles") as batch_op:
        batch_op.drop_column("year")
        batch_op.drop_column("max_range")
        batch_op.drop_column("assigned_driver")


def downgrade() -> None:
    with op.batch_alter_table("vehicles") as batch_op:
        batch_op.add_column(sa.Column("assigned_driver", sa.String(), nullable=False, server_default=""))
        batch_op.add_column(sa.Column("max_range", sa.Float(), nullable=False, server_default="0"))
        batch_op.add_column(sa.Column("year", sa.Integer(), nullable=False, server_default="0"))
