import uuid
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class VehicleCategory(Base):
    __tablename__ = "vehicle_categories"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)


class EmployeeCategory(Base):
    __tablename__ = "employee_categories"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    role: Mapped[str | None] = mapped_column(String, nullable=True)


class ActivityCategory(Base):
    __tablename__ = "activity_categories"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    icon_url: Mapped[str | None] = mapped_column(String, nullable=True)
