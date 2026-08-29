from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.auth import get_current_user
from app.models.activity import ActivityLog
from app.schemas.activity import ActivityLogCreate, ActivityLogPatch, ActivityLogOut

router = APIRouter(prefix="/api/v1/activities", tags=["activities"], dependencies=[Depends(get_current_user)])


@router.get("/avg-duration")
def get_avg_duration(
    vehicle_id: str = Query(..., alias="vehicleId"),
    service_type: str = Query(..., alias="serviceType"),
    db: Session = Depends(get_db),
):
    result = db.query(func.avg(ActivityLog.duration_minutes)).filter(
        ActivityLog.vehicle_id == vehicle_id,
        ActivityLog.service_type == service_type,
        ActivityLog.status == "completed",
        ActivityLog.duration_minutes.isnot(None),
        ActivityLog.duration_minutes > 0,
    ).scalar()
    return {"avgDurationMinutes": round(result, 2) if result is not None else None}


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
    # Auto-complete any in-progress activity for the same vehicle
    prev = (
        db.query(ActivityLog)
        .filter(ActivityLog.vehicle_id == body.vehicle_id, ActivityLog.status == "in-progress")
        .first()
    )
    if prev:
        prev.status = "completed"
        new_dt = body.date_time.replace(tzinfo=None)
        prev_dt = prev.date_time.replace(tzinfo=None) if prev.date_time.tzinfo else prev.date_time
        if new_dt > prev_dt:
            delta = new_dt - prev_dt
            prev.duration_minutes = round(delta.total_seconds() / 60, 1)

    a = ActivityLog(
        date_time=body.date_time, vehicle_id=body.vehicle_id,
        vehicle_name=body.vehicle_name, unit_id=body.unit_id,
        service_type=body.service_type, driver=body.driver,
        status="in-progress",
        created_by=body.created_by,
        duration_minutes=body.duration_minutes,
        energy_kwh=body.energy_kwh,
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


@router.delete("/{activity_id}", status_code=204)
def delete_activity(activity_id: str, db: Session = Depends(get_db)):
    a = db.query(ActivityLog).filter(ActivityLog.id == activity_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Activity not found")
    db.delete(a)
    db.commit()
