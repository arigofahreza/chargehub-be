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
    driver: str
    status: ActivityStatus
    created_by: str = Field(alias="createdBy")

    model_config = {"populate_by_name": True}


class ActivityLogCreate(ActivityLogBase):
    pass


class ActivityLogPatch(BaseModel):
    date_time: Optional[datetime] = Field(None, alias="dateTime")
    vehicle_id: Optional[str] = Field(None, alias="vehicleId")
    vehicle_name: Optional[str] = Field(None, alias="vehicleName")
    unit_id: Optional[str] = Field(None, alias="unitId")
    service_type: Optional[str] = Field(None, alias="serviceType")
    driver: Optional[str] = None
    status: Optional[ActivityStatus] = None
    created_by: Optional[str] = Field(None, alias="createdBy")

    model_config = {"populate_by_name": True}


class ActivityLogOut(BaseModel):
    id: str
    date_time: str = Field(serialization_alias="dateTime")
    vehicle_id: str = Field(serialization_alias="vehicleId")
    vehicle_name: str = Field(serialization_alias="vehicleName")
    unit_id: str = Field(serialization_alias="unitId")
    service_type: str = Field(serialization_alias="serviceType")
    driver: str
    status: ActivityStatus
    created_by: str = Field(serialization_alias="createdBy")

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
            driver=a.driver, status=a.status, created_by=a.created_by,
        )

    def model_dump_camel(self) -> dict:
        return self.model_dump(by_alias=True)
