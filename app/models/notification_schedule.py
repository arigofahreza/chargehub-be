import uuid
import json
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, DateTime, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from app.utils.tz import WIB


class NotificationSchedule(Base):
    __tablename__ = "notification_schedules"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    template_id: Mapped[Optional[str]] = mapped_column(
        String, ForeignKey("notification_templates.id", ondelete="SET NULL"), nullable=True
    )
    activity_id: Mapped[Optional[str]] = mapped_column(
        String, ForeignKey("activity_logs.id", ondelete="SET NULL"), nullable=True
    )
    target: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(WIB)
    )
    send_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
    status: Mapped[str] = mapped_column(
        SAEnum("pending", "sent", "failed", name="schedule_status"),
        nullable=False, default="pending"
    )

    def __init__(self, **kwargs):
        if "status" not in kwargs:
            kwargs["status"] = "pending"
        if "target" not in kwargs:
            kwargs["target"] = "[]"
        if "created_at" not in kwargs:
            kwargs["created_at"] = datetime.now(WIB)
        if "send_at" not in kwargs:
            kwargs["send_at"] = None
        super().__init__(**kwargs)

    def get_target_list(self) -> list[str]:
        try:
            return json.loads(self.target)
        except (json.JSONDecodeError, TypeError):
            return []

    def set_target_list(self, targets: list[str]) -> None:
        self.target = json.dumps(targets)
