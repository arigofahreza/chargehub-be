from typing import Literal, Optional
from pydantic import BaseModel, Field

VehicleStatus = Literal["available", "in-use", "service"]


class VehicleBase(BaseModel):
    name: str
    fleet_id: str = Field(alias="fleetId")
    make: str
    model: str
    year: int
    vin: str
    battery_capacity: float = Field(alias="batteryCapacity")
    max_range: float = Field(alias="maxRange")
    assigned_driver: str = Field(alias="assignedDriver")
    status: VehicleStatus
    battery_percent: float = Field(alias="batteryPercent")
    photo_url: str = Field(alias="photoUrl")
    temperature: float
    voltage: float
    range: float

    model_config = {"populate_by_name": True}


class VehicleCreate(VehicleBase):
    pass


class VehiclePatch(BaseModel):
    name: Optional[str] = None
    fleet_id: Optional[str] = Field(None, alias="fleetId")
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    vin: Optional[str] = None
    battery_capacity: Optional[float] = Field(None, alias="batteryCapacity")
    max_range: Optional[float] = Field(None, alias="maxRange")
    assigned_driver: Optional[str] = Field(None, alias="assignedDriver")
    status: Optional[VehicleStatus] = None
    battery_percent: Optional[float] = Field(None, alias="batteryPercent")
    photo_url: Optional[str] = Field(None, alias="photoUrl")
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
    year: int
    vin: str
    battery_capacity: float = Field(serialization_alias="batteryCapacity")
    max_range: float = Field(serialization_alias="maxRange")
    assigned_driver: str = Field(serialization_alias="assignedDriver")
    status: VehicleStatus
    battery_percent: float = Field(serialization_alias="batteryPercent")
    photo_url: str = Field(serialization_alias="photoUrl")
    temperature: float
    voltage: float
    range: float

    model_config = {"populate_by_name": True, "from_attributes": True}

    @classmethod
    def from_orm_model(cls, v) -> "VehicleOut":
        return cls(
            id=v.id, name=v.name, fleet_id=v.fleet_id, make=v.make,
            model=v.model, year=v.year, vin=v.vin,
            battery_capacity=v.battery_capacity, max_range=v.max_range,
            assigned_driver=v.assigned_driver, status=v.status,
            battery_percent=v.battery_percent, photo_url=v.photo_url,
            temperature=v.temperature, voltage=v.voltage, range=v.range,
        )

    def model_dump_camel(self) -> dict:
        return self.model_dump(by_alias=True)
