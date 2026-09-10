"""add_jabatan_to_users

Revision ID: m2i3j4k5l6m7
Revises: l1h2i3j4k5l6
Create Date: 2026-09-02 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "m2i3j4k5l6m7"
down_revision: Union[str, None] = "l1h2i3j4k5l6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("jabatan", sa.String(), nullable=True, server_default=""))


def downgrade() -> None:
    op.drop_column("users", "jabatan")
