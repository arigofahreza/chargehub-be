"""add_vehicle_type

Revision ID: h7c8d9e0f1g2
Revises: g6b7c8d9e0f1
Create Date: 2026-08-18 14:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'h7c8d9e0f1g2'
down_revision: Union[str, None] = 'g6b7c8d9e0f1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('vehicles', sa.Column('vehicle_type', sa.String(), nullable=True))
    op.execute("UPDATE vehicles SET vehicle_type = '' WHERE vehicle_type IS NULL")
    with op.batch_alter_table('vehicles') as batch_op:
        batch_op.alter_column('vehicle_type', existing_type=sa.String(), nullable=False)


def downgrade() -> None:
    with op.batch_alter_table('vehicles') as batch_op:
        batch_op.drop_column('vehicle_type')
