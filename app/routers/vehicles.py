import os
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate, VehiclePatch, VehicleOut
from app.services.storage import upload_vehicle_photo

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

router = APIRouter(prefix="/api/v1/vehicles", tags=["vehicles"])


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
    if status and status != "all":
        q = q.filter(Vehicle.status == status)
    return [VehicleOut.from_orm_model(v).model_dump_camel() for v in q.all()]


@router.get("/{vehicle_id}")
def get_vehicle(vehicle_id: str, db: Session = Depends(get_db)):
    v = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return VehicleOut.from_orm_model(v).model_dump_camel()


@router.post("", status_code=201)
def create_vehicle(payload: VehicleCreate, db: Session = Depends(get_db)):
    v = Vehicle(
        name=payload.name, fleet_id=payload.fleet_id, make=payload.make,
        model=payload.model, year=payload.year, vin=payload.vin,
        battery_capacity=payload.battery_capacity, max_range=payload.max_range,
        assigned_driver=payload.assigned_driver, status=payload.status,
        battery_percent=payload.battery_percent, photo_url=payload.photo_url,
        temperature=payload.temperature, voltage=payload.voltage, range=payload.range,
    )
    db.add(v)
    db.commit()
    db.refresh(v)
    return VehicleOut.from_orm_model(v).model_dump_camel()


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
    return VehicleOut.from_orm_model(v).model_dump_camel()


@router.patch("/{vehicle_id}")
def patch_vehicle(vehicle_id: str, payload: VehiclePatch, db: Session = Depends(get_db)):
    v = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    field_map = {
        "fleet_id": "fleet_id", "battery_capacity": "battery_capacity",
        "max_range": "max_range", "assigned_driver": "assigned_driver",
        "battery_percent": "battery_percent", "photo_url": "photo_url",
    }
    for field, value in payload.model_dump(exclude_unset=True, by_alias=False).items():
        if hasattr(v, field):
            setattr(v, field, value)
    db.commit()
    db.refresh(v)
    return VehicleOut.from_orm_model(v).model_dump_camel()
