"""create_notification_logs

Revision ID: q6r7s8t9u0v1
Revises: p5q6r7s8t9u0
Create Date: 2026-09-03 02:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "q6r7s8t9u0v1"
down_revision: Union[str, None] = "p5q6r7s8t9u0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE notif_log_status AS ENUM ('sent', 'failed');
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;
    """)
    op.create_table(
        "notification_logs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("to_phone", sa.String(), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("template_id", sa.String(), nullable=True),
        sa.Column("template_name", sa.String(), nullable=True),
        sa.Column("status", sa.Enum("sent", "failed", name="notif_log_status", create_type=False), nullable=False),
        sa.Column("sent_at", sa.DateTime(), nullable=False),
        sa.Column("sent_by_id", sa.String(), nullable=True),
        sa.Column("note", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["template_id"], ["notification_templates.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["sent_by_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_notification_logs_sent_at", "notification_logs", ["sent_at"])


def downgrade() -> None:
    op.drop_index("ix_notification_logs_sent_at", "notification_logs")
    op.drop_table("notification_logs")
    op.execute("DROP TYPE IF EXISTS notif_log_status")
