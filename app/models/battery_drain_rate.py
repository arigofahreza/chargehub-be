import uuid
from sqlalchemy import String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class BatteryDrainRate(Base):
    __tablename__ = "battery_drain_rates"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    activity_id: Mapped[str] = mapped_column(String, ForeignKey("activity_categories.id", ondelete="CASCADE"), nullable=False, index=True)
    persen_penurunan: Mapped[float] = mapped_column(Float, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False, default="penurunan")
