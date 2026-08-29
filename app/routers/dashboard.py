from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, cast, Integer
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models.vehicle import Vehicle
from app.models.activity import ActivityLog

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"], dependencies=[Depends(get_current_user)])


def parse_dt(s: Optional[str]) -> Optional[datetime]:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


@router.get("/fleet-status")
def fleet_status(
    vehicle_id: Optional[str] = Query(None, alias="vehicleId"),
    db: Session = Depends(get_db),
):
    q = db.query(Vehicle)
    if vehicle_id and vehicle_id != "all":
        q = q.filter(Vehicle.id == vehicle_id)
    vehicles = q.all()
    counts = {"available": 0, "in-use": 0, "service": 0}
    for v in vehicles:
        if v.status in counts:
            counts[v.status] += 1
    total = sum(counts.values())
    return {
        "available": counts["available"],
        "inUse": counts["in-use"],
        "service": counts["service"],
        "total": total,
    }


@router.get("/usage-trend")
def usage_trend(
    vehicle_id: Optional[str] = Query(None, alias="vehicleId"),
    date_from: Optional[str] = Query(None, alias="dateFrom"),
    date_to: Optional[str] = Query(None, alias="dateTo"),
    db: Session = Depends(get_db),
):
    q = db.query(
        func.date(ActivityLog.date_time).label("date"),
        func.coalesce(func.sum(ActivityLog.km_driven), 0).label("km"),
    )
    if vehicle_id and vehicle_id != "all":
        q = q.filter(ActivityLog.vehicle_id == vehicle_id)
    dt_from = parse_dt(date_from)
    dt_to = parse_dt(date_to)
    if dt_from:
        q = q.filter(ActivityLog.date_time >= dt_from)
    if dt_to:
        q = q.filter(ActivityLog.date_time <= dt_to)
    q = q.group_by(func.date(ActivityLog.date_time)).order_by(func.date(ActivityLog.date_time))
    rows = q.all()
    return [{"date": str(r.date), "km": float(r.km)} for r in rows]


@router.get("/top-energy")
def top_energy(
    vehicle_id: Optional[str] = Query(None, alias="vehicleId"),
    date_from: Optional[str] = Query(None, alias="dateFrom"),
    date_to: Optional[str] = Query(None, alias="dateTo"),
    limit: int = Query(5),
    db: Session = Depends(get_db),
):
    q = db.query(
        ActivityLog.vehicle_id,
        ActivityLog.vehicle_name,
        func.coalesce(func.sum(ActivityLog.energy_kwh), 0).label("total_kwh"),
    )
    if vehicle_id and vehicle_id != "all":
        q = q.filter(ActivityLog.vehicle_id == vehicle_id)
    dt_from = parse_dt(date_from)
    dt_to = parse_dt(date_to)
    if dt_from:
        q = q.filter(ActivityLog.date_time >= dt_from)
    if dt_to:
        q = q.filter(ActivityLog.date_time <= dt_to)
    q = (
        q.group_by(ActivityLog.vehicle_id, ActivityLog.vehicle_name)
        .order_by(func.sum(ActivityLog.energy_kwh).desc())
        .limit(limit)
    )
    rows = q.all()
    max_kwh = float(rows[0].total_kwh) if rows else 1.0
    return [
        {
            "vehicleId": r.vehicle_id,
            "vehicleName": r.vehicle_name,
            "totalKwh": round(float(r.total_kwh), 1),
            "pct": round(float(r.total_kwh) / max_kwh * 100, 1) if max_kwh > 0 else 0,
        }
        for r in rows
    ]


@router.get("/stats")
def stats(
    vehicle_id: Optional[str] = Query(None, alias="vehicleId"),
    date_from: Optional[str] = Query(None, alias="dateFrom"),
    date_to: Optional[str] = Query(None, alias="dateTo"),
    db: Session = Depends(get_db),
):
    q = db.query(ActivityLog)
    if vehicle_id and vehicle_id != "all":
        q = q.filter(ActivityLog.vehicle_id == vehicle_id)
    dt_from = parse_dt(date_from)
    dt_to = parse_dt(date_to)
    if dt_from:
        q = q.filter(ActivityLog.date_time >= dt_from)
    if dt_to:
        q = q.filter(ActivityLog.date_time <= dt_to)
    logs = q.all()

    total_km = sum(l.km_driven or 0 for l in logs)
    total_kwh = sum(l.energy_kwh or 0 for l in logs)
    activity_count = len(logs)

    vq = db.query(Vehicle)
    if vehicle_id and vehicle_id != "all":
        vq = vq.filter(Vehicle.id == vehicle_id)
    vehicles = vq.all()
    available_count = sum(1 for v in vehicles if v.status == "available")
    avg_battery = sum(v.battery_percent for v in vehicles) / len(vehicles) if vehicles else 0

    return {
        "totalKm": round(total_km, 1),
        "totalKwh": round(total_kwh, 1),
        "activityCount": activity_count,
        "availableCount": available_count,
        "avgBatteryPct": round(avg_battery, 1),
        "totalVehicles": len(vehicles),
    }


@router.get("/avg-kwh-per-vehicle")
def avg_kwh_per_vehicle(
    vehicle_id: Optional[str] = Query(None, alias="vehicleId"),
    date_from: Optional[str] = Query(None, alias="dateFrom"),
    date_to: Optional[str] = Query(None, alias="dateTo"),
    db: Session = Depends(get_db),
):
    KWH_PRICE = 1114
    q = db.query(
        ActivityLog.vehicle_id,
        ActivityLog.vehicle_name,
        func.avg(ActivityLog.energy_kwh).label("avg_kwh"),
        func.count(ActivityLog.id).label("session_count"),
    )
    if vehicle_id and vehicle_id != "all":
        q = q.filter(ActivityLog.vehicle_id == vehicle_id)
    dt_from = parse_dt(date_from)
    dt_to = parse_dt(date_to)
    if dt_from:
        q = q.filter(ActivityLog.date_time >= dt_from)
    if dt_to:
        q = q.filter(ActivityLog.date_time <= dt_to)
    q = q.filter(ActivityLog.energy_kwh.isnot(None), ActivityLog.energy_kwh > 0)
    q = (
        q.group_by(ActivityLog.vehicle_id, ActivityLog.vehicle_name)
        .order_by(func.avg(ActivityLog.energy_kwh).desc())
    )
    rows = q.all()
    return [
        {
            "vehicleId": r.vehicle_id,
            "vehicleName": r.vehicle_name,
            "avgKwh": round(float(r.avg_kwh or 0), 2),
            "estimatedCost": round(float(r.avg_kwh or 0) * KWH_PRICE),
            "sessionCount": int(r.session_count),
        }
        for r in rows
    ]


@router.get("/battery-hourly")
def battery_hourly(
    vehicle_id: Optional[str] = Query(None, alias="vehicleId"),
    date_from: Optional[str] = Query(None, alias="dateFrom"),
    date_to: Optional[str] = Query(None, alias="dateTo"),
    db: Session = Depends(get_db),
):
    q = db.query(
        cast(func.extract("hour", ActivityLog.date_time), Integer).label("hour"),
        ActivityLog.vehicle_name,
        func.avg(ActivityLog.energy_kwh).label("avg_kwh"),
    )
    if vehicle_id and vehicle_id != "all":
        q = q.filter(ActivityLog.vehicle_id == vehicle_id)
    dt_from = parse_dt(date_from)
    dt_to = parse_dt(date_to)
    if dt_from:
        q = q.filter(ActivityLog.date_time >= dt_from)
    if dt_to:
        q = q.filter(ActivityLog.date_time <= dt_to)
    q = q.filter(ActivityLog.energy_kwh.isnot(None), ActivityLog.energy_kwh > 0)
    q = q.group_by(
        cast(func.extract("hour", ActivityLog.date_time), Integer),
        ActivityLog.vehicle_name,
    ).order_by(cast(func.extract("hour", ActivityLog.date_time), Integer))
    rows = q.all()

    vehicles = sorted({r.vehicle_name for r in rows})
    hour_map: dict[int, dict[str, float]] = {h: {v: 0.0 for v in vehicles} for h in range(24)}
    for r in rows:
        hour_map[int(r.hour)][r.vehicle_name] = round(float(r.avg_kwh or 0), 2)

    data = [{"hour": h, **hour_map[h]} for h in range(24)]
    return {"vehicles": vehicles, "data": data}
