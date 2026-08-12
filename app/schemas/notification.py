from typing import Literal, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

TemplateStatus = Literal["active", "inactive"]


class NotificationTemplateBase(BaseModel):
    name: str
    message: str
    status: TemplateStatus
    employee_count: int = Field(alias="employeeCount")
    phone_count: int = Field(alias="phoneCount")
    last_sent: str = Field(alias="lastSent")
    category: str = "General"

    model_config = {"populate_by_name": True}


class NotificationTemplateCreate(NotificationTemplateBase):
    pass


class NotificationTemplatePatch(BaseModel):
    name: Optional[str] = None
    message: Optional[str] = None
    status: Optional[TemplateStatus] = None
    employee_count: Optional[int] = Field(None, alias="employeeCount")
    phone_count: Optional[int] = Field(None, alias="phoneCount")
    last_sent: Optional[str] = Field(None, alias="lastSent")
    category: Optional[str] = None

    model_config = {"populate_by_name": True}


class NotificationTemplateOut(BaseModel):
    id: str
    name: str
    message: str
    status: TemplateStatus
    employee_count: int = Field(serialization_alias="employeeCount")
    phone_count: int = Field(serialization_alias="phoneCount")
    last_sent: str = Field(serialization_alias="lastSent")
    category: str = "General"

    model_config = {"populate_by_name": True}

    @classmethod
    def from_orm_model(cls, t) -> "NotificationTemplateOut":
        dt = t.last_sent
        dt_str = dt.isoformat() + ("Z" if dt.tzinfo is None else "")
        return cls(
            id=t.id, name=t.name, message=t.message, status=t.status,
            employee_count=t.employee_count, phone_count=t.phone_count,
            last_sent=dt_str, category=getattr(t, "category", "General") or "General",
        )

    def model_dump_camel(self) -> dict:
        return self.model_dump(by_alias=True)
