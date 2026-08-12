"""add category to notification_templates

Revision ID: a3f9b2c1d4e5
Revises: 51aa1be783af
Create Date: 2026-08-07 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'a3f9b2c1d4e5'
down_revision = '51aa1be783af'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'notification_templates',
        sa.Column('category', sa.String(), nullable=False, server_default='General')
    )


def downgrade() -> None:
    op.drop_column('notification_templates', 'category')
