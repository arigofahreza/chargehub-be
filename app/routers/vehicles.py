import os
import uuid as _uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.activity import ActivityLog
from app.models.vehicle_battery_state import VehicleBatteryState
from app.models.battery_drain_rate import BatteryDrainRate
from app.models.category import ActivityCategory
from app.schemas.vehicle import VehicleCreate, VehiclePatch, VehicleOut
from app.services.storage import upload_vehicle_photo
from app.utils.tz import WIB

_CHARGING_RATE_PCT_PER_MIN = 1.2
_CHARGING_TYPES = {"charging"}

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

router = APIRouter(prefix="/api/v1/vehicles", tags=["vehicles"], dependencies=[Depends(get_current_user)])


def compute_operating_time(vehicle_id: str, db: Session) -> float:
    result = db.query(func.sum(ActivityLog.duration_minutes)).filter(
        ActivityLog.vehicle_id == vehicle_id,
        ActivityLog.status == "completed",
        ActivityLog.duration_minutes.isnot(None),
    ).scalar()
    return round((result or 0.0) / 60.0, 2)


def compute_vehicle_status(vehicle_id: str, db: Session) -> str:
    active = db.query(ActivityLog).filter(
        ActivityLog.vehicle_id == vehicle_id,
        ActivityLog.status == "in-progress",
    ).first()
    if not active:
        return "idle"
    return "charging" if active.service_type == "Charging" else "working"


@router.get("")
def list_vehicles(
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(Vehicle)
    if search:
        term = f"%{search.lower()}%"
        q = q.filter(
            Vehicle.name.ilike(term) | Vehicle.fleet_id.ilike(term)
        )
    vehicles = q.all()
    result = []
    for v in vehicles:
        computed_status = compute_vehicle_status(v.id, db)
        if status and status != "all" and computed_status != status:
            continue
        result.append(
            VehicleOut.from_orm_model(
                v, compute_operating_time(v.id, db), computed_status,
            ).model_dump_camel()
        )
    return result


@router.get("/{vehicle_id}")
def get_vehicle(vehicle_id: str, db: Session = Depends(get_db)):
    v = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return VehicleOut.from_orm_model(
        v, compute_operating_time(v.id, db), compute_vehicle_status(v.id, db)
    ).model_dump_camel()


@router.post("", status_code=201)
def create_vehicle(payload: VehicleCreate, db: Session = Depends(get_db)):
    fleet_id = payload.fleet_id.strip() if payload.fleet_id else ""
    if not fleet_id:
        fleet_id = f"FLT-{_uuid.uuid4().hex[:6].upper()}"
    v = Vehicle(
        name=payload.name, fleet_id=fleet_id, make=payload.make,
        model=payload.model, vin=payload.vin,
        battery_capacity=payload.battery_capacity, status=payload.status,
        battery_percent=payload.battery_percent, photo_url=payload.photo_url,
        operating_time=payload.operating_time,
        degradation_rate_pct=getattr(payload, 'degradation_rate_pct', 2.0),
        vehicle_type=getattr(payload, 'vehicle_type', ''),
    )
    db.add(v)
    db.commit()
    db.refresh(v)
    return VehicleOut.from_orm_model(v, 0.0, "idle").model_dump_camel()


@router.post("/{vehicle_id}/photo")
async def upload_photo(
    vehicle_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    v = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="File must be JPEG, PNG, WebP, or GIF")

    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File exceeds 5 MB limit")

    ext = os.path.splitext(file.filename or "")[1] or ".jpg"
    url = upload_vehicle_photo(file_bytes, file.content_type, ext)

    v.photo_url = url
    db.commit()
    db.refresh(v)
    return VehicleOut.from_orm_model(
        v, compute_operating_time(v.id, db), compute_vehicle_status(v.id, db)
    ).model_dump_camel()


@router.delete("/{vehicle_id}", status_code=204)
def delete_vehicle(vehicle_id: str, db: Session = Depends(get_db)):
    v = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    db.delete(v)
    db.commit()


@router.patch("/{vehicle_id}")
def patch_vehicle(vehicle_id: str, payload: VehiclePatch, db: Session = Depends(get_db)):
    v = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    updated_fields = payload.model_dump(exclude_unset=True, by_alias=False)
    for field, value in updated_fields.items():
        if hasattr(v, field):
            setattr(v, field, value)
    if "make" in updated_fields or "model" in updated_fields:
        v.name = f"{v.make} {v.model}".strip()
    db.commit()
    db.refresh(v)
    return VehicleOut.from_orm_model(
        v, compute_operating_time(v.id, db), compute_vehicle_status(v.id, db)
    ).model_dump_camel()


# ── Battery state ─────────────────────────────────────────────────────────────

class BatteryStateCalibrate(BaseModel):
    battery_pct: float


@router.get("/{vehicle_id}/battery-state")
def get_battery_state(vehicle_id: str, db: Session = Depends(get_db)):
    state = db.query(VehicleBatteryState).filter(VehicleBatteryState.vehicle_id == vehicle_id).first()
    stored_pct = state.battery_pct if state else 100.0
    calculated_at = state.calculated_at.isoformat() if state else None
    source_activity_id = state.source_activity_id if state else None

    # If manual calibration exists, return it directly — it represents current state
    if state and state.source_activity_id is None:
        return {
            "batteryPct": stored_pct,
            "calculatedAt": calculated_at,
            "sourceActivityId": None,
        }

    # Project battery on-the-fly if there is an in-progress activity
    in_progress = (
        db.query(ActivityLog)
        .filter(ActivityLog.vehicle_id == vehicle_id, ActivityLog.status == "in-progress")
        .order_by(ActivityLog.date_time.desc())
        .first()
    )
    if in_progress:
        now = datetime.now(WIB)
        # Use calibration time as projection base if state was set after activity started
        state_dt = state.calculated_at if state else None
        if state_dt and state_dt.tzinfo is None:
            state_dt = state_dt.replace(tzinfo=WIB)
        act_dt = in_progress.date_time
        if act_dt.tzinfo is None:
            act_dt = act_dt.replace(tzinfo=WIB)
        base_dt = state_dt if (state_dt and state_dt > act_dt) else act_dt
        elapsed_minutes = max(0.0, (now - base_dt).total_seconds() / 60)
        stype = in_progress.service_type.lower()
        if stype in _CHARGING_TYPES:
            live_pct = round(min(100.0, stored_pct + elapsed_minutes * _CHARGING_RATE_PCT_PER_MIN), 2)
        else:
            cat = db.query(ActivityCategory).filter(ActivityCategory.name == in_progress.service_type).first()
            drain = db.query(BatteryDrainRate).filter(BatteryDrainRate.activity_id == cat.id).first() if cat else None
            if drain and drain.persen_penurunan > 0:
                live_pct = round(max(0.0, stored_pct - elapsed_minutes * drain.persen_penurunan), 2)
            else:
                live_pct = stored_pct
        return {
            "batteryPct": live_pct,
            "calculatedAt": now.isoformat(),
            "sourceActivityId": source_activity_id,
        }

    return {
        "batteryPct": stored_pct,
        "calculatedAt": calculated_at,
        "sourceActivityId": source_activity_id,
    }


@router.patch("/{vehicle_id}/battery-state")
def calibrate_battery_state(
    vehicle_id: str,
    body: BatteryStateCalibrate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    v = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    if body.battery_pct < 0 or body.battery_pct > 100:
        raise HTTPException(status_code=400, detail="battery_pct harus 0–100")
    state = db.query(VehicleBatteryState).filter(VehicleBatteryState.vehicle_id == vehicle_id).first()
    now = datetime.now(WIB)
    if state:
        state.battery_pct = body.battery_pct
        state.calculated_at = now
        state.source_activity_id = None
    else:
        db.add(VehicleBatteryState(
            vehicle_id=vehicle_id,
            battery_pct=body.battery_pct,
            calculated_at=now,
            source_activity_id=None,
        ))
    db.commit()
    return {"batteryPct": body.battery_pct, "calculatedAt": now.isoformat(), "sourceActivityId": None}
