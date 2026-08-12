import uuid
from sqlalchemy import String, Float, Integer, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False)
    fleet_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    make: Mapped[str] = mapped_column(String, nullable=False)
    model: Mapped[str] = mapped_column(String, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    vin: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    battery_capacity: Mapped[float] = mapped_column(Float, nullable=False)
    max_range: Mapped[float] = mapped_column(Float, nullable=False)
    assigned_driver: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(
        SAEnum("available", "in-use", "service", name="vehicle_status"),
        nullable=False, default="available"
    )
    battery_percent: Mapped[float] = mapped_column(Float, nullable=False)
    photo_url: Mapped[str] = mapped_column(String, nullable=False, default="")
    temperature: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    voltage: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    range: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
