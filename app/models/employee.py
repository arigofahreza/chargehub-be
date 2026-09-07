import uuid
from typing import Optional
from sqlalchemy import String, Boolean, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False)
    job_title: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(
        SAEnum("active", "on-leave", "inactive", name="employee_status"),
        nullable=False, default="active"
    )
    avatar_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    initials: Mapped[str] = mapped_column(String, nullable=False)
    chat_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    subscribed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if "subscribed" not in kwargs:
            self.subscribed = False
