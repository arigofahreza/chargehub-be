from typing import Literal
from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str


class CategoryPatch(BaseModel):
    name: str


class CategoryOut(BaseModel):
    id: str
    name: str

    model_config = {"from_attributes": True}


class EmployeeCategoryOut(BaseModel):
    id: str
    name: str
    role: str | None = None

    model_config = {"from_attributes": True}


class ActivityCategoryOut(BaseModel):
    id: str
    name: str
    icon_url: str | None = None

    model_config = {"from_attributes": True}


class BatteryDrainRateCreate(BaseModel):
    activity_id: str = Field(alias="activityId")
    persen_penurunan: float = Field(alias="persenPenurunan")
    category: Literal["kenaikan", "penurunan"] = "penurunan"

    model_config = {"populate_by_name": True}


class BatteryDrainRatePatch(BaseModel):
    persen_penurunan: float = Field(alias="persenPenurunan")
    category: Literal["kenaikan", "penurunan"] | None = None

    model_config = {"populate_by_name": True}


class BatteryDrainRateOut(BaseModel):
    id: str
    activity_id: str = Field(serialization_alias="activityId")
    activity_name: str = Field(serialization_alias="activityName")
    persen_penurunan: float = Field(serialization_alias="persenPenurunan")
    category: str = "penurunan"

    model_config = {"populate_by_name": True}

    def model_dump_camel(self) -> dict:
        return self.model_dump(by_alias=True)
