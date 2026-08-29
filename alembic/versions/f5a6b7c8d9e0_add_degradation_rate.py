"""add_degradation_rate_to_vehicles

Revision ID: f5a6b7c8d9e0
Revises: e4f5a6b7c8d9
Create Date: 2026-08-18 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'f5a6b7c8d9e0'
down_revision: Union[str, None] = 'e4f5a6b7c8d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('vehicles', sa.Column('degradation_rate_pct', sa.Float(), nullable=True))
    op.execute("UPDATE vehicles SET degradation_rate_pct = 2.0 WHERE degradation_rate_pct IS NULL")
    with op.batch_alter_table('vehicles') as batch_op:
        batch_op.alter_column('degradation_rate_pct', existing_type=sa.Float(), nullable=False)


def downgrade() -> None:
    with op.batch_alter_table('vehicles') as batch_op:
        batch_op.drop_column('degradation_rate_pct')
