import uuid
from sqlalchemy import String, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False)
    fleet_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    make: Mapped[str] = mapped_column(String, nullable=False)
    model: Mapped[str] = mapped_column(String, nullable=False)
    vin: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    battery_capacity: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="idle")
    battery_percent: Mapped[float] = mapped_column(Float, nullable=False)
    photo_url: Mapped[str] = mapped_column(String, nullable=False, default="")
    temperature: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    voltage: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    range: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    operating_time: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    degradation_rate_pct: Mapped[float] = mapped_column(Float, nullable=False, default=2.0)
    vehicle_type: Mapped[str] = mapped_column(String, nullable=False, default="")
