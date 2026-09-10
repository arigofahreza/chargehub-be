import secrets
import string
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user, require_permission, require_admin
from app.models.employee import Employee
from app.models.user import User
from app.schemas.employee import EmployeeCreate, EmployeePatch, EmployeeOut, EmployeeTokenOut


def _generate_token() -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(8))

router = APIRouter(prefix="/api/v1/employees", tags=["employees"])


@router.get("/telegram-tokens")
def list_telegram_tokens(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    employees = db.query(Employee).order_by(Employee.name).all()
    return [EmployeeTokenOut.from_orm_model(e).model_dump_camel() for e in employees]


@router.post("/{employee_id}/refresh-token")
def refresh_subscribe_token(
    employee_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    e = db.query(Employee).filter(Employee.id == employee_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Employee tidak ditemukan")
    token = _generate_token()
    while db.query(Employee).filter(Employee.subscribe_token == token).first():
        token = _generate_token()
    e.subscribe_token = token
    db.commit()
    db.refresh(e)
    return EmployeeTokenOut.from_orm_model(e).model_dump_camel()


@router.get("")
def list_employees(
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    job_title: Optional[str] = Query(None, alias="jobTitle"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(Employee)
    if status:
        q = q.filter(Employee.status == status)
    if search:
        term = f"%{search}%"
        q = q.filter(Employee.name.ilike(term))
    if job_title:
        q = q.filter(Employee.job_title == job_title)
    return [EmployeeOut.from_orm_model(e).model_dump_camel() for e in q.all()]


@router.get("/{employee_id}")
def get_employee(
    employee_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    e = db.query(Employee).filter(Employee.id == employee_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Employee not found")
    return EmployeeOut.from_orm_model(e).model_dump_camel()


@router.post("", status_code=201)
def create_employee(
    body: EmployeeCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("employees", "write")),
):
    e = Employee(
        name=body.name, job_title=body.job_title,
        phone=body.phone, status=body.status,
        avatar_url=body.avatar_url, initials=body.initials,
    )
    db.add(e)
    db.commit()
    db.refresh(e)
    return EmployeeOut.from_orm_model(e).model_dump_camel()


@router.delete("/{employee_id}", status_code=204)
def delete_employee(
    employee_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("employees", "write")),
):
    e = db.query(Employee).filter(Employee.id == employee_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(e)
    db.commit()


@router.patch("/{employee_id}")
def patch_employee(
    employee_id: str,
    body: EmployeePatch,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("employees", "write")),
):
    e = db.query(Employee).filter(Employee.id == employee_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Employee not found")
    data = body.model_dump(exclude_unset=True, by_alias=False)
    for key, value in data.items():
        setattr(e, key, value)
    db.commit()
    db.refresh(e)
    return EmployeeOut.from_orm_model(e).model_dump_camel()
