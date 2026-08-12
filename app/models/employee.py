import uuid
from typing import Optional
from sqlalchemy import String, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    job_title: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(
        SAEnum("active", "on-leave", "inactive", name="employee_status"),
        nullable=False, default="active"
    )
    avatar_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    initials: Mapped[str] = mapped_column(String, nullable=False)
