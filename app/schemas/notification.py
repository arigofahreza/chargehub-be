from typing import Literal, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

TemplateStatus = Literal["active", "inactive"]


class NotificationTemplateBase(BaseModel):
    name: str
    message: str
    status: TemplateStatus
    phone_count: int = Field(default=0, alias="phoneCount")
    last_sent: str = Field(alias="lastSent")
    category: str = "General"

    model_config = {"populate_by_name": True}


class NotificationTemplateCreate(NotificationTemplateBase):
    pass


class NotificationTemplatePatch(BaseModel):
    name: Optional[str] = None
    message: Optional[str] = None
    status: Optional[TemplateStatus] = None
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
            employee_count=0, phone_count=t.phone_count,
            last_sent=dt_str, category=getattr(t, "category", "General") or "General",
        )

    def model_dump_camel(self) -> dict:
        return self.model_dump(by_alias=True)


LogStatus = Literal["sent", "failed"]


class NotificationLogCreate(BaseModel):
    to_phone: str = Field(alias="toPhone")
    message: str
    template_id: Optional[str] = Field(None, alias="templateId")
    template_name: Optional[str] = Field(None, alias="templateName")
    status: LogStatus = "sent"
    note: Optional[str] = None

    model_config = {"populate_by_name": True}


class NotificationLogOut(BaseModel):
    id: str
    to_phone: str = Field(serialization_alias="toPhone")
    message: str
    template_id: Optional[str] = Field(None, serialization_alias="templateId")
    template_name: Optional[str] = Field(None, serialization_alias="templateName")
    status: LogStatus
    sent_at: str = Field(serialization_alias="sentAt")
    sent_by_id: Optional[str] = Field(None, serialization_alias="sentById")
    note: Optional[str] = None

    model_config = {"populate_by_name": True}

    @classmethod
    def from_orm(cls, log) -> "NotificationLogOut":
        dt = log.sent_at
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return cls(
            id=log.id,
            to_phone=log.to_phone,
            message=log.message,
            template_id=log.template_id,
            template_name=log.template_name,
            status=log.status,
            sent_at=dt.isoformat(),
            sent_by_id=log.sent_by_id,
            note=log.note,
        )

    def model_dump_camel(self) -> dict:
        return self.model_dump(by_alias=True)
