"""split_full_name_to_first_last_name

Revision ID: i8d9e0f1g2h3
Revises: h7c8d9e0f1g2
Create Date: 2026-08-20 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'i8d9e0f1g2h3'
down_revision: Union[str, None] = 'h7c8d9e0f1g2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('first_name', sa.String(), nullable=True))
    op.add_column('users', sa.Column('last_name', sa.String(), nullable=True))
    # Migrate existing data: split full_name by first space (PostgreSQL)
    op.execute("""
        UPDATE users
        SET first_name = SPLIT_PART(full_name, ' ', 1),
            last_name = CASE
                WHEN POSITION(' ' IN full_name) > 0
                THEN SUBSTRING(full_name FROM POSITION(' ' IN full_name) + 1)
                ELSE ''
            END
    """)
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('first_name', existing_type=sa.String(), nullable=False)
        batch_op.alter_column('last_name', existing_type=sa.String(), nullable=False)
        batch_op.drop_column('full_name')


def downgrade() -> None:
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('full_name', sa.String(), nullable=True))
    op.execute("UPDATE users SET full_name = first_name || ' ' || last_name")
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('full_name', existing_type=sa.String(), nullable=False)
        batch_op.drop_column('first_name')
        batch_op.drop_column('last_name')
