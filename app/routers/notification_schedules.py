import json
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user, require_permission
from app.models.notification_schedule import NotificationSchedule
from app.models.user import User
from app.schemas.notification_schedule import NotificationScheduleCreate, NotificationScheduleOut

router = APIRouter(prefix="/api/v1/notification-schedules", tags=["notification-schedules"])


@router.get("")
def list_schedules(
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(NotificationSchedule)
    if status:
        q = q.filter(NotificationSchedule.status == status)
    schedules = q.order_by(NotificationSchedule.send_at.asc()).all()
    return [NotificationScheduleOut.from_orm_model(s).model_dump_camel() for s in schedules]


@router.post("", status_code=201)
def create_schedule(
    body: NotificationScheduleCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("notifications", "write")),
):
    send_at = body.send_at or datetime.now(timezone.utc)
    if send_at.tzinfo is not None:
        send_at = send_at.replace(tzinfo=None)

    s = NotificationSchedule(
        template_id=body.template_id,
        activity_id=body.activity_id,
        send_at=send_at,
    )
    s.set_target_list(body.target)
    db.add(s)
    db.commit()
    db.refresh(s)
    return NotificationScheduleOut.from_orm_model(s).model_dump_camel()


@router.get("/{schedule_id}")
def get_schedule(
    schedule_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    s = db.query(NotificationSchedule).filter(NotificationSchedule.id == schedule_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return NotificationScheduleOut.from_orm_model(s).model_dump_camel()


@router.delete("/{schedule_id}", status_code=204)
def delete_schedule(
    schedule_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("notifications", "write")),
):
    s = db.query(NotificationSchedule).filter(NotificationSchedule.id == schedule_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Schedule not found")
    db.delete(s)
    db.commit()
