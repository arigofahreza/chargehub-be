from pathlib import Path
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user, require_permission
from app.models.user import User
from app.models.category import VehicleCategory, EmployeeCategory, ActivityCategory
from app.models.battery_drain_rate import BatteryDrainRate
from app.schemas.category import CategoryCreate, CategoryPatch, CategoryOut, EmployeeCategoryOut, ActivityCategoryOut, BatteryDrainRateCreate, BatteryDrainRatePatch, BatteryDrainRateOut
from app.services.storage import upload_activity_icon

router = APIRouter(prefix="/api/v1/categories", tags=["categories"])


# ── Vehicle categories ──────────────────────────────────────────────

@router.get("/vehicle")
def list_vehicle_categories(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    cats = db.query(VehicleCategory).order_by(VehicleCategory.name).all()
    return [CategoryOut.model_validate(c).model_dump() for c in cats]


@router.post("/vehicle", status_code=201)
def create_vehicle_category(
    body: CategoryCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("categories", "write")),
):
    existing = db.query(VehicleCategory).filter(VehicleCategory.name == body.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Kategori sudah ada")
    cat = VehicleCategory(name=body.name)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return CategoryOut.model_validate(cat).model_dump()


@router.patch("/vehicle/{category_id}")
def update_vehicle_category(
    category_id: str,
    body: CategoryPatch,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("categories", "write")),
):
    cat = db.query(VehicleCategory).filter(VehicleCategory.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Kategori tidak ditemukan")
    cat.name = body.name
    db.commit()
    db.refresh(cat)
    return CategoryOut.model_validate(cat).model_dump()


@router.delete("/vehicle/{category_id}", status_code=204)
def delete_vehicle_category(
    category_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("categories", "write")),
):
    cat = db.query(VehicleCategory).filter(VehicleCategory.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Kategori tidak ditemukan")
    db.delete(cat)
    db.commit()


# ── Employee categories ─────────────────────────────────────────────

@router.get("/employee")
def list_employee_categories(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    cats = db.query(EmployeeCategory).order_by(EmployeeCategory.name).all()
    return [EmployeeCategoryOut.model_validate(c).model_dump() for c in cats]


@router.post("/employee", status_code=201)
def create_employee_category(
    body: CategoryCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("categories", "write")),
):
    existing = db.query(EmployeeCategory).filter(EmployeeCategory.name == body.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Kategori sudah ada")
    cat = EmployeeCategory(name=body.name, role=body.name.lower())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return EmployeeCategoryOut.model_validate(cat).model_dump()


@router.patch("/employee/{category_id}")
def update_employee_category(
    category_id: str,
    body: CategoryPatch,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("categories", "write")),
):
    cat = db.query(EmployeeCategory).filter(EmployeeCategory.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Kategori tidak ditemukan")
    cat.name = body.name
    db.commit()
    db.refresh(cat)
    return EmployeeCategoryOut.model_validate(cat).model_dump()


@router.delete("/employee/{category_id}", status_code=204)
def delete_employee_category(
    category_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("categories", "write")),
):
    cat = db.query(EmployeeCategory).filter(EmployeeCategory.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Kategori tidak ditemukan")
    db.delete(cat)
    db.commit()


# ── Activity categories ─────────────────────────────────────────────

@router.get("/activity")
def list_activity_categories(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    cats = db.query(ActivityCategory).order_by(ActivityCategory.name).all()
    return [ActivityCategoryOut.model_validate(c).model_dump() for c in cats]


@router.post("/activity", status_code=201)
async def create_activity_category(
    name: str = Form(...),
    icon: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("categories", "write")),
):
    existing = db.query(ActivityCategory).filter(ActivityCategory.name == name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Kategori sudah ada")

    contents = await icon.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Icon tidak boleh kosong")

    suffix = Path(icon.filename or "icon.png").suffix.lower() or ".png"
    icon_url = upload_activity_icon(contents, icon.content_type or "image/png", suffix)

    cat = ActivityCategory(name=name, icon_url=icon_url)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return ActivityCategoryOut.model_validate(cat).model_dump()


@router.patch("/activity/{category_id}")
async def update_activity_category(
    category_id: str,
    name: str = Form(...),
    icon: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("categories", "write")),
):
    cat = db.query(ActivityCategory).filter(ActivityCategory.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Kategori tidak ditemukan")
    cat.name = name
    if icon and icon.filename:
        contents = await icon.read()
        if contents:
            suffix = Path(icon.filename).suffix.lower() or ".png"
            cat.icon_url = upload_activity_icon(contents, icon.content_type or "image/png", suffix)
    db.commit()
    db.refresh(cat)
    return ActivityCategoryOut.model_validate(cat).model_dump()


@router.delete("/activity/{category_id}", status_code=204)
def delete_activity_category(
    category_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("categories", "write")),
):
    cat = db.query(ActivityCategory).filter(ActivityCategory.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Kategori tidak ditemukan")
    db.delete(cat)
    db.commit()


# ── Battery drain rates ─────────────────────────────────────────────

def _rate_out(rate: BatteryDrainRate, db: Session) -> BatteryDrainRateOut:
    act = db.query(ActivityCategory).filter(ActivityCategory.id == rate.activity_id).first()
    return BatteryDrainRateOut(
        id=rate.id,
        activity_id=rate.activity_id,
        activity_name=act.name if act else "",
        persen_penurunan=rate.persen_penurunan,
    )


@router.get("/battery-drain-rates")
def list_battery_drain_rates(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    rates = db.query(BatteryDrainRate).all()
    return [_rate_out(r, db).model_dump_camel() for r in rates]


@router.post("/battery-drain-rates", status_code=201)
def create_battery_drain_rate(
    body: BatteryDrainRateCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("categories", "write")),
):
    act = db.query(ActivityCategory).filter(ActivityCategory.id == body.activity_id).first()
    if not act:
        raise HTTPException(status_code=404, detail="Aktivitas tidak ditemukan")
    rate = BatteryDrainRate(activity_id=body.activity_id, persen_penurunan=body.persen_penurunan)
    db.add(rate)
    db.commit()
    db.refresh(rate)
    return _rate_out(rate, db).model_dump_camel()


@router.patch("/battery-drain-rates/{rate_id}")
def update_battery_drain_rate(
    rate_id: str,
    body: BatteryDrainRatePatch,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("categories", "write")),
):
    rate = db.query(BatteryDrainRate).filter(BatteryDrainRate.id == rate_id).first()
    if not rate:
        raise HTTPException(status_code=404, detail="Data tidak ditemukan")
    rate.persen_penurunan = body.persen_penurunan
    db.commit()
    db.refresh(rate)
    return _rate_out(rate, db).model_dump_camel()


@router.delete("/battery-drain-rates/{rate_id}", status_code=204)
def delete_battery_drain_rate(
    rate_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("categories", "write")),
):
    rate = db.query(BatteryDrainRate).filter(BatteryDrainRate.id == rate_id).first()
    if not rate:
        raise HTTPException(status_code=404, detail="Data tidak ditemukan")
    db.delete(rate)
    db.commit()
