"""add_username_to_users

Revision ID: e4f5a6b7c8d9
Revises: d3e4f5a6b7c8
Create Date: 2026-08-18 00:02:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e4f5a6b7c8d9'
down_revision: Union[str, None] = 'd3e4f5a6b7c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('username', sa.String(), nullable=True))
    op.execute("UPDATE users SET username = email WHERE username IS NULL")
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('username', existing_type=sa.String(), nullable=False)
        batch_op.create_unique_constraint('uq_users_username', ['username'])


def downgrade() -> None:
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_constraint('uq_users_username', type_='unique')
    op.drop_column('users', 'username')
