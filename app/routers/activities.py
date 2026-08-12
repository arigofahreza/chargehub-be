from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.activity import ActivityLog
from app.schemas.activity import ActivityLogCreate, ActivityLogPatch, ActivityLogOut

router = APIRouter(prefix="/api/v1/activities", tags=["activities"])


@router.get("")
def list_activities(
    status: Optional[str] = Query(None),
    vehicle_id: Optional[str] = Query(None, alias="vehicleId"),
    db: Session = Depends(get_db),
):
    q = db.query(ActivityLog)
    if status:
        q = q.filter(ActivityLog.status == status)
    if vehicle_id:
        q = q.filter(ActivityLog.vehicle_id == vehicle_id)
    q = q.order_by(ActivityLog.date_time.desc())
    logs = q.all()
    return [ActivityLogOut.from_orm_model(a).model_dump_camel() for a in logs]


@router.get("/{activity_id}")
def get_activity(activity_id: str, db: Session = Depends(get_db)):
    a = db.query(ActivityLog).filter(ActivityLog.id == activity_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Activity not found")
    return ActivityLogOut.from_orm_model(a).model_dump_camel()


@router.post("", status_code=201)
def create_activity(body: ActivityLogCreate, db: Session = Depends(get_db)):
    a = ActivityLog(
        date_time=body.date_time, vehicle_id=body.vehicle_id,
        vehicle_name=body.vehicle_name, unit_id=body.unit_id,
        service_type=body.service_type, driver=body.driver,
        status=body.status, created_by=body.created_by,
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return ActivityLogOut.from_orm_model(a).model_dump_camel()


@router.patch("/{activity_id}")
def patch_activity(activity_id: str, body: ActivityLogPatch, db: Session = Depends(get_db)):
    a = db.query(ActivityLog).filter(ActivityLog.id == activity_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Activity not found")
    data = body.model_dump(exclude_unset=True, by_alias=False)
    for key, value in data.items():
        setattr(a, key, value)
    db.commit()
    db.refresh(a)
    return ActivityLogOut.from_orm_model(a).model_dump_camel()
