"""add_operating_time_to_vehicles_nullable_email_employees

Revision ID: c2d3e4f5a6b7
Revises: b1c2d3e4f5a6
Create Date: 2026-08-18 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c2d3e4f5a6b7'
down_revision: Union[str, None] = 'b1c2d3e4f5a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('vehicles', sa.Column('operating_time', sa.Float(), nullable=True, server_default='0.0'))

    with op.batch_alter_table('employees') as batch_op:
        batch_op.alter_column('email', existing_type=sa.String(), nullable=True)


def downgrade() -> None:
    op.drop_column('vehicles', 'operating_time')

    with op.batch_alter_table('employees') as batch_op:
        batch_op.alter_column('email', existing_type=sa.String(), nullable=False)
