import uuid
from sqlalchemy import String, Integer, DateTime, Enum as SAEnum, Text
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from datetime import datetime
from app.database import Base


class NotificationTemplate(Base):
    __tablename__ = "notification_templates"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False)
    message: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(
        SAEnum("active", "inactive", name="template_status"),
        nullable=False, default="active"
    )
    employee_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    phone_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_sent: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False, default="General")
    recipient_ids: Mapped[Optional[str]] = mapped_column(Text, nullable=True, default="[]")
