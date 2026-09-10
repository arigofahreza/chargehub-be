from collections import defaultdict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.category import EmployeeCategory

router = APIRouter(prefix="/api/v1/job-titles", tags=["job-titles"])


@router.get("")
def list_job_titles(db: Session = Depends(get_db)):
    cats = db.query(EmployeeCategory).order_by(EmployeeCategory.name).all()
    return [c.name for c in cats]


@router.get("/role-map")
def get_role_jabatan_map(db: Session = Depends(get_db)):
    cats = db.query(EmployeeCategory).filter(EmployeeCategory.role.isnot(None)).all()
    result: dict[str, list[str]] = defaultdict(list)
    for cat in cats:
        result[cat.role].append(cat.name)
    return dict(result)
