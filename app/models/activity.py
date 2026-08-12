import uuid
from typing import Optional
from sqlalchemy import String, DateTime, Float, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.database import Base


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    date_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    vehicle_id: Mapped[str] = mapped_column(String, nullable=False)
    vehicle_name: Mapped[str] = mapped_column(String, nullable=False)
    unit_id: Mapped[str] = mapped_column(String, nullable=False)
    service_type: Mapped[str] = mapped_column(String, nullable=False)
    driver: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(
        SAEnum("completed", "in-progress", "pending", name="activity_status"),
        nullable=False, default="pending"
    )
    created_by: Mapped[str] = mapped_column(String, nullable=False)
    km_driven: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=0.0)
    energy_kwh: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=0.0)
