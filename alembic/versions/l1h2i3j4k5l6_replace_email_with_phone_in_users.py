"""replace_email_with_phone_in_users

Revision ID: l1h2i3j4k5l6
Revises: k0f1g2h3i4j5
Create Date: 2026-09-02 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "l1h2i3j4k5l6"
down_revision: Union[str, None] = "k0f1g2h3i4j5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("phone", sa.String(), nullable=True, server_default=""))
    op.drop_index("ix_users_email", table_name="users")
    op.drop_column("users", "email")


def downgrade() -> None:
    op.add_column("users", sa.Column("email", sa.String(), nullable=True, server_default=""))
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.drop_column("users", "phone")
