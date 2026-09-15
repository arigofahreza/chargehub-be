from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.auth import get_current_user, require_permission
from app.models.app_config import AppConfig
from app.models.user import User
from app.utils.tz import WIB

router = APIRouter(prefix="/api/v1/config", tags=["config"])


class AppConfigOut(BaseModel):
    key: str
    value: str
    description: Optional[str]
    updated_at: str

    @classmethod
    def from_orm(cls, c) -> "AppConfigOut":
        dt = c.updated_at
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=WIB)
        return cls(key=c.key, value=c.value, description=c.description, updated_at=dt.isoformat())

    def model_dump_camel(self) -> dict:
        return {
            "key": self.key,
            "value": self.value,
            "description": self.description,
            "updatedAt": self.updated_at,
        }


class AppConfigUpdate(BaseModel):
    value: str


@router.get("")
def list_config(
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("management", "read")),
):
    configs = db.query(AppConfig).all()
    return [AppConfigOut.from_orm(c).model_dump_camel() for c in configs]


@router.get("/{key}")
def get_config(
    key: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    c = db.query(AppConfig).filter(AppConfig.key == key).first()
    if not c:
        raise HTTPException(status_code=404, detail="Config not found")
    return AppConfigOut.from_orm(c).model_dump_camel()


@router.put("/{key}")
def update_config(
    key: str,
    body: AppConfigUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("management", "write")),
):
    c = db.query(AppConfig).filter(AppConfig.key == key).first()
    if not c:
        raise HTTPException(status_code=404, detail="Config not found")
    c.value = body.value
    c.updated_at = datetime.now(WIB)
    db.commit()
    db.refresh(c)
    return AppConfigOut.from_orm(c).model_dump_camel()
