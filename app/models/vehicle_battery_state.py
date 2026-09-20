import uuid
from datetime import datetime
from sqlalchemy import String, Float, DateTime as _DTCol, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class VehicleBatteryState(Base):
    __tablename__ = "vehicle_battery_states"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    vehicle_id: Mapped[str] = mapped_column(String, ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False, unique=True)
    battery_pct: Mapped[float] = mapped_column(Float, nullable=False)
    calculated_at: Mapped[datetime] = mapped_column(_DTCol(timezone=True), nullable=False)
    source_activity_id: Mapped[str | None] = mapped_column(String, ForeignKey("activity_logs.id", ondelete="SET NULL"), nullable=True)
