from typing import Literal, Optional
from datetime import datetime
from pydantic import BaseModel, Field

ActivityStatus = Literal["completed", "in-progress", "pending"]


class ActivityLogBase(BaseModel):
    date_time: datetime = Field(alias="dateTime")
    vehicle_id: str = Field(alias="vehicleId")
    vehicle_name: str = Field(alias="vehicleName")
    unit_id: str = Field(alias="unitId")
    service_type: str = Field(alias="serviceType")
    supervisor: str
    driver: str
    status: ActivityStatus
    created_by: str = Field(alias="createdBy")
    duration_minutes: Optional[float] = Field(None, alias="durationMinutes")
    energy_kwh: Optional[float] = Field(None, alias="energyKwh")

    model_config = {"populate_by_name": True}


class ActivityLogCreate(ActivityLogBase):
    pass


class ActivityLogPatch(BaseModel):
    date_time: Optional[datetime] = Field(None, alias="dateTime")
    vehicle_id: Optional[str] = Field(None, alias="vehicleId")
    vehicle_name: Optional[str] = Field(None, alias="vehicleName")
    unit_id: Optional[str] = Field(None, alias="unitId")
    service_type: Optional[str] = Field(None, alias="serviceType")
    supervisor: Optional[str] = None
    driver: Optional[str] = None
    status: Optional[ActivityStatus] = None
    created_by: Optional[str] = Field(None, alias="createdBy")
    duration_minutes: Optional[float] = Field(None, alias="durationMinutes")
    energy_kwh: Optional[float] = Field(None, alias="energyKwh")

    model_config = {"populate_by_name": True}


class ActivityLogOut(BaseModel):
    id: str
    date_time: str = Field(serialization_alias="dateTime")
    vehicle_id: str = Field(serialization_alias="vehicleId")
    vehicle_name: str = Field(serialization_alias="vehicleName")
    unit_id: str = Field(serialization_alias="unitId")
    service_type: str = Field(serialization_alias="serviceType")
    supervisor: Optional[str] = None
    driver: str
    status: ActivityStatus
    created_by: str = Field(serialization_alias="createdBy")
    duration_minutes: Optional[float] = Field(None, serialization_alias="durationMinutes")
    energy_kwh: Optional[float] = Field(None, serialization_alias="energyKwh")

    model_config = {"populate_by_name": True}

    @classmethod
    def from_orm_model(cls, a) -> "ActivityLogOut":
        dt = a.date_time
        if hasattr(dt, 'isoformat'):
            dt_str = dt.isoformat() + ("Z" if dt.tzinfo is None else "")
        else:
            dt_str = str(dt) + "Z"
        return cls(
            id=a.id, date_time=dt_str,
            vehicle_id=a.vehicle_id, vehicle_name=a.vehicle_name,
            unit_id=a.unit_id, service_type=a.service_type,
            supervisor=getattr(a, "supervisor", None),
            driver=a.driver, status=a.status, created_by=a.created_by,
            duration_minutes=getattr(a, "duration_minutes", None),
            energy_kwh=getattr(a, "energy_kwh", None),
        )

    def model_dump_camel(self) -> dict:
        return self.model_dump(by_alias=True)
