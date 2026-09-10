from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

ScheduleStatus = str  # "pending" | "sent" | "failed"


class NotificationScheduleCreate(BaseModel):
    template_id: str = Field(alias="templateId")
    activity_id: str = Field(alias="activityId")
    target: list[str]
    send_at: Optional[datetime] = Field(None, alias="sendAt")

    model_config = {"populate_by_name": True}


class NotificationScheduleOut(BaseModel):
    id: str
    template_id: Optional[str] = Field(None, serialization_alias="templateId")
    activity_id: Optional[str] = Field(None, serialization_alias="activityId")
    target: list[str]
    created_at: str = Field(serialization_alias="createdAt")
    send_at: str = Field(serialization_alias="sendAt")
    status: str

    model_config = {"populate_by_name": True}

    @classmethod
    def from_orm_model(cls, s) -> "NotificationScheduleOut":
        def fmt(dt: datetime) -> str:
            if dt is None:
                dt = datetime.now(timezone.utc)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.isoformat()

        return cls(
            id=s.id,
            template_id=s.template_id,
            activity_id=s.activity_id,
            target=s.get_target_list(),
            created_at=fmt(s.created_at),
            send_at=fmt(s.send_at),
            status=s.status,
        )

    def model_dump_camel(self) -> dict:
        return self.model_dump(by_alias=True)
