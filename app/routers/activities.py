import logging
from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.auth import get_current_user, require_permission
from app.models.activity import ActivityLog
from app.models.app_config import AppConfig
from app.models.battery_drain_rate import BatteryDrainRate
from app.models.category import ActivityCategory
from app.models.employee import Employee
from app.models.notification import NotificationTemplate
from app.models.notification_schedule import NotificationSchedule
from app.models.vehicle import Vehicle
from app.models.user import User
from app.schemas.activity import ActivityLogCreate, ActivityLogPatch, ActivityLogOut
from app.services.ml_client import normalize_activity, get_shift, predict_battery_after

logger = logging.getLogger("chargehub.activities")

router = APIRouter(prefix="/api/v1/activities", tags=["activities"])

STACKING_TYPES = {"heavy stacking", "light stacking"}
CHARGING_TYPES = {"charging"}

# Charging offsets (battery_before always 30%, rate 1.2%/min, ceiling 90%, +15min to 100%)
_MINUTES_TO_90 = int((90 - 30) / 1.2)   # 50 minutes
_MINUTES_TO_100 = _MINUTES_TO_90 + 15   # 65 minutes

_DEFAULT_TARIFF_KWH = 1114.0


def _get_tariff(db: Session) -> float:
    cfg = db.query(AppConfig).filter(AppConfig.key == "tariff_kwh_rupiah").first()
    try:
        return float(cfg.value) if cfg else _DEFAULT_TARIFF_KWH
    except (ValueError, TypeError):
        return _DEFAULT_TARIFF_KWH


def _auto_schedule_charging(db: Session, activity: ActivityLog, supervisors: list[str], driver: str) -> None:
    try:
        tmpl_90 = db.query(NotificationTemplate).filter(NotificationTemplate.name == "Baterai Hampir Penuh").first()
        tmpl_100 = db.query(NotificationTemplate).filter(NotificationTemplate.name == "Baterai Penuh").first()

        if not tmpl_90 or not tmpl_100:
            logger.warning("Charging notification templates not found, skipping schedules for activity %s", activity.id)
            return

        names = [n for n in list(supervisors) + ([driver] if driver else []) if n]
        employees = db.query(Employee).filter(Employee.name.in_(names)).all()
        targets = list({e.chat_id for e in employees if e.chat_id})

        act_dt = activity.date_time

        for template, offset_minutes in [
            (tmpl_90, _MINUTES_TO_90),
            (tmpl_100, _MINUTES_TO_100),
        ]:
            s = NotificationSchedule(
                template_id=template.id,
                activity_id=activity.id,
                send_at=act_dt + timedelta(minutes=offset_minutes),
            )
            s.set_target_list(targets)
            db.add(s)

        db.commit()
        logger.info(
            "Charging schedules created for activity %s — targets: %d, send_at_90=%s, send_at_100=%s",
            activity.id, len(targets),
            act_dt + timedelta(minutes=_MINUTES_TO_90),
            act_dt + timedelta(minutes=_MINUTES_TO_100),
        )
    except Exception as exc:
        logger.error("Failed to create charging schedules for activity %s: %s", activity.id, exc)
        db.rollback()


def _auto_schedule_non_charging(db: Session, activity: ActivityLog, supervisors: list[str], driver: str) -> None:
    try:
        cat = db.query(ActivityCategory).filter(ActivityCategory.name == activity.service_type).first()
        if not cat:
            logger.warning("ActivityCategory not found for service_type '%s', skip schedule", activity.service_type)
            return

        drain_row = db.query(BatteryDrainRate).filter(BatteryDrainRate.activity_id == cat.id).first()
        if not drain_row or drain_row.persen_penurunan <= 0:
            logger.warning("No drain rate for activity '%s', skip schedule", activity.service_type)
            return

        drain_rate = drain_row.persen_penurunan
        minutes_to_30 = 70.0 / drain_rate

        act_dt = activity.date_time

        shift = get_shift(act_dt.hour)
        ml_activity = normalize_activity(activity.service_type)
        if ml_activity:
            predicted = predict_battery_after(
                truck_id=activity.unit_id,
                activity=ml_activity,
                duration_minutes=minutes_to_30,
                battery_before_pct=100.0,
                shift=shift,
            )
            if predicted is not None:
                logger.info(
                    "ML predicted battery_after=%.2f%% at %.1fmin for activity %s",
                    predicted, minutes_to_30, activity.id,
                )
        else:
            logger.info("service_type '%s' not in ML ValidActivity, ML call skipped", activity.service_type)

        tmpl = db.query(NotificationTemplate).filter(NotificationTemplate.name == "Peringatan Baterai 30%").first()
        if not tmpl:
            logger.warning("Template 'Peringatan Baterai 30%%' not found, skip schedule")
            return

        names = [n for n in list(supervisors) + ([driver] if driver else []) if n]
        employees = db.query(Employee).filter(Employee.name.in_(names)).all()
        targets = list({e.chat_id for e in employees if e.chat_id})

        s = NotificationSchedule(
            template_id=tmpl.id,
            activity_id=activity.id,
            send_at=act_dt + timedelta(minutes=minutes_to_30),
        )
        s.set_target_list(targets)
        db.add(s)
        db.commit()

        logger.info(
            "Non-charging schedule created for activity %s — drain=%.2f%%/min, minutes_to_30=%.1f, send_at=%s",
            activity.id, drain_rate, minutes_to_30, act_dt + timedelta(minutes=minutes_to_30),
        )
    except Exception as exc:
        logger.error("Failed to create non-charging schedule for activity %s: %s", activity.id, exc)
        db.rollback()


@router.get("/avg-duration")
def get_avg_duration(
    vehicle_id: str = Query(..., alias="vehicleId"),
    service_type: str = Query(..., alias="serviceType"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
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
    date_from: Optional[str] = Query(None, alias="dateFrom"),
    date_to: Optional[str] = Query(None, alias="dateTo"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(ActivityLog)
    if status:
        q = q.filter(ActivityLog.status == status)
    if vehicle_id:
        q = q.filter(ActivityLog.vehicle_id == vehicle_id)
    if date_from:
        dt_from = datetime.fromisoformat(date_from.replace("Z", "+00:00"))
        q = q.filter(ActivityLog.date_time >= dt_from)
    if date_to:
        dt_to = datetime.fromisoformat(date_to.replace("Z", "+00:00"))
        q = q.filter(ActivityLog.date_time <= dt_to)
    q = q.order_by(ActivityLog.date_time.desc())
    logs = q.all()
    return [ActivityLogOut.from_orm_model(a).model_dump_camel() for a in logs]


@router.get("/{activity_id}")
def get_activity(
    activity_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    a = db.query(ActivityLog).filter(ActivityLog.id == activity_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Activity not found")
    return ActivityLogOut.from_orm_model(a).model_dump_camel()


@router.post("", status_code=201)
def create_activity(
    body: ActivityLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stype_lower = body.service_type.lower()
    role = current_user.role
    if role == "operator" and stype_lower not in CHARGING_TYPES:
        raise HTTPException(
            status_code=403,
            detail="Operator hanya dapat menginput aktivitas Charging",
        )
    if role == "spotter" and stype_lower not in STACKING_TYPES:
        raise HTTPException(
            status_code=403,
            detail="Spotter hanya dapat menginput aktivitas Stacking",
        )

    # Auto-complete any in-progress activity for the same vehicle
    prev = (
        db.query(ActivityLog)
        .filter(ActivityLog.vehicle_id == body.vehicle_id, ActivityLog.status == "in-progress")
        .first()
    )
    if prev:
        prev.status = "completed"
        new_dt = body.date_time
        prev_dt = prev.date_time
        if new_dt > prev_dt:
            delta = new_dt - prev_dt
            prev.duration_minutes = round(delta.total_seconds() / 60, 1)

    # For charging: auto-calc energy_kwh (30%→100% = 70% of capacity) and cost_rupiah
    energy_kwh = body.energy_kwh
    cost_rupiah = None
    if stype_lower == "charging":
        vehicle = db.query(Vehicle).filter(Vehicle.id == body.vehicle_id).first()
        if vehicle and vehicle.battery_capacity:
            energy_kwh = round(0.70 * vehicle.battery_capacity, 2)
            tariff = _get_tariff(db)
            cost_rupiah = round(energy_kwh * tariff, 2)

    a = ActivityLog(
        date_time=body.date_time, vehicle_id=body.vehicle_id,
        vehicle_name=body.vehicle_name, unit_id=body.unit_id,
        service_type=body.service_type,
        driver=body.driver,
        status="in-progress",
        created_by=body.created_by,
        duration_minutes=body.duration_minutes,
        energy_kwh=energy_kwh,
        cost_rupiah=cost_rupiah,
    )
    a.set_supervisor_list(body.supervisors)
    db.add(a)
    db.commit()
    db.refresh(a)

    if stype_lower == "charging":
        _auto_schedule_charging(db, a, body.supervisors, body.driver)
    else:
        _auto_schedule_non_charging(db, a, body.supervisors, body.driver)

    return ActivityLogOut.from_orm_model(a).model_dump_camel()


@router.patch("/{activity_id}")
def patch_activity(
    activity_id: str,
    body: ActivityLogPatch,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    a = db.query(ActivityLog).filter(ActivityLog.id == activity_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Activity not found")
    if body.service_type:
        stype_lower = body.service_type.lower()
        role = current_user.role
        if role == "operator" and stype_lower not in CHARGING_TYPES:
            raise HTTPException(status_code=403, detail="Operator hanya dapat menginput aktivitas Charging")
        if role == "spotter" and stype_lower not in STACKING_TYPES:
            raise HTTPException(status_code=403, detail="Spotter hanya dapat menginput aktivitas Stacking")
    data = body.model_dump(exclude_unset=True, by_alias=False)
    new_supervisors = None
    if "supervisors" in data and data["supervisors"] is not None:
        new_supervisors = data.pop("supervisors")
        a.set_supervisor_list(new_supervisors)
    elif "supervisors" in data:
        data.pop("supervisors")
    for key, value in data.items():
        setattr(a, key, value)
    db.commit()
    db.refresh(a)

    # Reschedule if any schedule-affecting field changed
    _SCHEDULE_FIELDS = {"date_time", "supervisors", "driver"}
    if _SCHEDULE_FIELDS.intersection(body.model_fields_set):
        db.query(NotificationSchedule).filter(
            NotificationSchedule.activity_id == a.id,
            NotificationSchedule.status == "pending",
        ).delete()
        db.commit()
        supervisors = new_supervisors if new_supervisors is not None else a.get_supervisor_list()
        if a.service_type.lower() in CHARGING_TYPES:
            _auto_schedule_charging(db, a, supervisors, a.driver or "")
        else:
            _auto_schedule_non_charging(db, a, supervisors, a.driver or "")

    return ActivityLogOut.from_orm_model(a).model_dump_camel()


@router.delete("/{activity_id}", status_code=204)
def delete_activity(
    activity_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("activities", "write")),
):
    a = db.query(ActivityLog).filter(ActivityLog.id == activity_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Activity not found")
    db.query(NotificationSchedule).filter(NotificationSchedule.activity_id == activity_id).delete()
    db.delete(a)
    db.commit()
