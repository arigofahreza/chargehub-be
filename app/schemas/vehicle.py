from typing import Literal, Optional
from pydantic import BaseModel, Field

VehicleStatus = Literal["idle", "working", "charging"]


class VehicleBase(BaseModel):
    name: str
    fleet_id: str = Field(default="", alias="fleetId")
    make: str
    model: str
    vin: str
    battery_capacity: float = Field(alias="batteryCapacity")
    status: VehicleStatus
    battery_percent: float = Field(alias="batteryPercent")
    photo_url: str = Field(default="", alias="photoUrl")
    operating_time: float = Field(default=0.0, alias="operatingTime")
    degradation_rate_pct: float = Field(default=2.0, alias="degradationRatePct")
    vehicle_type: str = Field(default="", alias="vehicleType")
    temperature: Optional[float] = Field(default=0.0)
    voltage: Optional[float] = Field(default=0.0)
    range: Optional[float] = Field(default=0.0)

    model_config = {"populate_by_name": True}


class VehicleCreate(VehicleBase):
    pass


class VehiclePatch(BaseModel):
    name: Optional[str] = None
    fleet_id: Optional[str] = Field(None, alias="fleetId")
    make: Optional[str] = None
    model: Optional[str] = None
    vin: Optional[str] = None
    battery_capacity: Optional[float] = Field(None, alias="batteryCapacity")
    status: Optional[VehicleStatus] = None
    battery_percent: Optional[float] = Field(None, alias="batteryPercent")
    photo_url: Optional[str] = Field(None, alias="photoUrl")
    operating_time: Optional[float] = Field(None, alias="operatingTime")
    degradation_rate_pct: Optional[float] = Field(None, alias="degradationRatePct")
    vehicle_type: Optional[str] = Field(None, alias="vehicleType")
    temperature: Optional[float] = None
    voltage: Optional[float] = None
    range: Optional[float] = None

    model_config = {"populate_by_name": True}


class VehicleOut(BaseModel):
    id: str
    name: str
    fleet_id: str = Field(serialization_alias="fleetId")
    make: str
    model: str
    vin: str
    battery_capacity: float = Field(serialization_alias="batteryCapacity")
    status: VehicleStatus
    battery_percent: float = Field(serialization_alias="batteryPercent")
    photo_url: str = Field(serialization_alias="photoUrl")
    operating_time: float = Field(serialization_alias="operatingTime")
    degradation_rate_pct: float = Field(serialization_alias="degradationRatePct")
    vehicle_type: str = Field(serialization_alias="vehicleType")

    model_config = {"populate_by_name": True, "from_attributes": True}

    @classmethod
    def from_orm_model(cls, v, operating_time: float = 0.0, status: str = "idle") -> "VehicleOut":
        return cls(
            id=v.id, name=v.name, fleet_id=v.fleet_id, make=v.make,
            model=v.model, vin=v.vin,
            battery_capacity=v.battery_capacity,
            status=status,
            battery_percent=v.battery_percent,
            photo_url=v.photo_url,
            operating_time=operating_time,
            degradation_rate_pct=getattr(v, 'degradation_rate_pct', 2.0),
            vehicle_type=getattr(v, 'vehicle_type', ''),
        )

    def model_dump_camel(self) -> dict:
        return self.model_dump(by_alias=True)
