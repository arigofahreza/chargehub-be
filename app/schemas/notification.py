import json
from typing import Literal, Optional, List
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
    recipient_ids: List[str] = Field(default_factory=list, alias="recipientIds")

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
    recipient_ids: Optional[List[str]] = Field(None, alias="recipientIds")

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
    recipient_ids: List[str] = Field(default_factory=list, serialization_alias="recipientIds")

    model_config = {"populate_by_name": True}

    @classmethod
    def from_orm_model(cls, t) -> "NotificationTemplateOut":
        dt = t.last_sent
        dt_str = dt.isoformat() + ("Z" if dt.tzinfo is None else "")
        raw = getattr(t, "recipient_ids", None)
        if isinstance(raw, str):
            try:
                rids = json.loads(raw)
            except (ValueError, TypeError):
                rids = []
        elif isinstance(raw, list):
            rids = raw
        else:
            rids = []
        return cls(
            id=t.id, name=t.name, message=t.message, status=t.status,
            employee_count=len(rids), phone_count=t.phone_count,
            last_sent=dt_str, category=getattr(t, "category", "General") or "General",
            recipient_ids=rids,
        )

    def model_dump_camel(self) -> dict:
        return self.model_dump(by_alias=True)
