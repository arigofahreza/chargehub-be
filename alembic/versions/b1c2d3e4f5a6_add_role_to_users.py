"""add_role_to_users

Revision ID: b1c2d3e4f5a6
Revises: a3f9b2c1d4e5
Create Date: 2026-08-10 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b1c2d3e4f5a6'
down_revision: Union[str, None] = 'a3f9b2c1d4e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('role', sa.String(), nullable=False, server_default='operator'))


def downgrade() -> None:
    op.drop_column('users', 'role')
