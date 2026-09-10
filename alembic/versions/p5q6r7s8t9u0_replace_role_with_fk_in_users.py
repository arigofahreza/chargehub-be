"""replace_role_with_fk_in_users

Revision ID: p5q6r7s8t9u0
Revises: o4p5q6r7s8t9
Create Date: 2026-09-03 01:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "p5q6r7s8t9u0"
down_revision: Union[str, None] = "o4p5q6r7s8t9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("role_category_id", sa.String(), nullable=True))
    op.create_foreign_key(
        "fk_users_role_category_id",
        "users", "employee_categories",
        ["role_category_id"], ["id"],
        ondelete="SET NULL",
    )
    conn = op.get_bind()
    conn.execute(sa.text("""
        UPDATE users
        SET role_category_id = (
            SELECT id FROM employee_categories
            WHERE employee_categories.role = users.role
            ORDER BY employee_categories.name
            LIMIT 1
        )
    """))
    op.drop_column("users", "role")


def downgrade() -> None:
    op.add_column("users", sa.Column("role", sa.String(), nullable=False, server_default="operator"))
    conn = op.get_bind()
    conn.execute(sa.text("""
        UPDATE users
        SET role = COALESCE(
            (SELECT ec.role FROM employee_categories ec WHERE ec.id = users.role_category_id),
            'operator'
        )
    """))
    op.drop_constraint("fk_users_role_category_id", "users", type_="foreignkey")
    op.drop_column("users", "role_category_id")
