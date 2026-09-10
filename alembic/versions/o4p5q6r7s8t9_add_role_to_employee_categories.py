"""add_role_to_employee_categories

Revision ID: o4p5q6r7s8t9
Revises: n3o4p5q6r7s8
Create Date: 2026-09-03 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "o4p5q6r7s8t9"
down_revision: Union[str, None] = "n3o4p5q6r7s8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_KNOWN_ROLES = {
    "Pengawas": "pengawas",
    "Operator Loader": "operator",
    "Operator Eksavator": "operator",
    "Admin": "admin",
    "Checker": "operator",
    "Engineering": "operator",
}


def upgrade() -> None:
    op.add_column("employee_categories", sa.Column("role", sa.String(), nullable=True))
    conn = op.get_bind()
    for name, role in _KNOWN_ROLES.items():
        conn.execute(
            sa.text("UPDATE employee_categories SET role = :role WHERE name = :name"),
            {"role": role, "name": name},
        )


def downgrade() -> None:
    op.drop_column("employee_categories", "role")
