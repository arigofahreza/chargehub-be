import json
import uuid
from typing import Optional
from sqlalchemy import String, DateTime as _DTCol, Float, Text, Enum as SAEnum, Index
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.database import Base


class ActivityLog(Base):
    __tablename__ = "activity_logs"
    __table_args__ = (
        Index("ix_activity_logs_vehicle_status", "vehicle_id", "status"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    date_time: Mapped[datetime] = mapped_column(_DTCol(timezone=True), nullable=False, index=True)
    vehicle_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    vehicle_name: Mapped[str] = mapped_column(String, nullable=False)
    unit_id: Mapped[str] = mapped_column(String, nullable=False)
    service_type: Mapped[str] = mapped_column(String, nullable=False)
    supervisors: Mapped[str] = mapped_column(Text, nullable=True, default="[]")
    driver: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(
        SAEnum("completed", "in-progress", "pending", name="activity_status"),
        nullable=False, default="pending", index=True
    )
    created_by: Mapped[str] = mapped_column(String, nullable=False)
    km_driven: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=0.0)
    energy_kwh: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=0.0)
    duration_minutes: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=0.0)
    cost_rupiah: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    def get_supervisor_list(self) -> list[str]:
        try:
            return json.loads(self.supervisors or "[]")
        except (json.JSONDecodeError, TypeError):
            return []

    def set_supervisor_list(self, names: list[str]) -> None:
        self.supervisors = json.dumps(names, ensure_ascii=False)
