"""drop_jabatan_from_users

Revision ID: n3o4p5q6r7s8
Revises: m2i3j4k5l6m7
Create Date: 2026-09-02 01:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "n3o4p5q6r7s8"
down_revision: Union[str, None] = "m2i3j4k5l6m7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("users", "jabatan")


def downgrade() -> None:
    op.add_column("users", sa.Column("jabatan", sa.String(), nullable=True, server_default=""))
