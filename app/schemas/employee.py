from typing import Literal, Optional
from pydantic import BaseModel, Field

EmployeeStatus = Literal["active", "on-leave", "inactive"]


class EmployeeBase(BaseModel):
    name: str
    email: Optional[str] = None
    job_title: str = Field(alias="jobTitle")
    phone: str
    status: EmployeeStatus
    avatar_url: Optional[str] = Field(None, alias="avatarUrl")
    initials: str
    chat_id: Optional[str] = Field(None, alias="chatId")
    subscribed: bool = False

    model_config = {"populate_by_name": True}


class EmployeeCreate(EmployeeBase):
    pass


class EmployeePatch(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    job_title: Optional[str] = Field(None, alias="jobTitle")
    phone: Optional[str] = None
    status: Optional[EmployeeStatus] = None
    avatar_url: Optional[str] = Field(None, alias="avatarUrl")
    initials: Optional[str] = None
    chat_id: Optional[str] = Field(None, alias="chatId")
    subscribed: Optional[bool] = None

    model_config = {"populate_by_name": True}


class EmployeeOut(BaseModel):
    id: str
    name: str
    email: Optional[str] = None
    job_title: str = Field(serialization_alias="jobTitle")
    phone: str
    status: EmployeeStatus
    avatar_url: Optional[str] = Field(None, serialization_alias="avatarUrl")
    initials: str
    chat_id: Optional[str] = Field(None, serialization_alias="chatId")
    subscribed: bool = False

    model_config = {"populate_by_name": True, "from_attributes": True}

    @classmethod
    def from_orm_model(cls, e) -> "EmployeeOut":
        return cls(
            id=e.id, name=e.name,
            job_title=e.job_title, phone=e.phone, status=e.status,
            avatar_url=e.avatar_url, initials=e.initials,
            chat_id=getattr(e, "chat_id", None),
            subscribed=getattr(e, "subscribed", False) or False,
        )

    def model_dump_camel(self) -> dict:
        return self.model_dump(by_alias=True)
