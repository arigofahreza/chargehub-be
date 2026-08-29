from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import require_admin
from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeePatch, EmployeeOut

router = APIRouter(prefix="/api/v1/employees", tags=["employees"], dependencies=[Depends(require_admin)])


@router.get("")
def list_employees(
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(Employee)
    if status:
        q = q.filter(Employee.status == status)
    if search:
        term = f"%{search}%"
        q = q.filter(Employee.name.ilike(term) | Employee.email.ilike(term))
    employees = q.all()
    return [EmployeeOut.from_orm_model(e).model_dump_camel() for e in employees]


@router.get("/{employee_id}")
def get_employee(employee_id: str, db: Session = Depends(get_db)):
    e = db.query(Employee).filter(Employee.id == employee_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Employee not found")
    return EmployeeOut.from_orm_model(e).model_dump_camel()


@router.post("", status_code=201)
def create_employee(body: EmployeeCreate, db: Session = Depends(get_db)):
    e = Employee(
        name=body.name, email=body.email, job_title=body.job_title,
        phone=body.phone, status=body.status,
        avatar_url=body.avatar_url, initials=body.initials,
    )
    db.add(e)
    db.commit()
    db.refresh(e)
    return EmployeeOut.from_orm_model(e).model_dump_camel()


@router.delete("/{employee_id}", status_code=204)
def delete_employee(employee_id: str, db: Session = Depends(get_db)):
    e = db.query(Employee).filter(Employee.id == employee_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(e)
    db.commit()


@router.patch("/{employee_id}")
def patch_employee(employee_id: str, body: EmployeePatch, db: Session = Depends(get_db)):
    e = db.query(Employee).filter(Employee.id == employee_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Employee not found")
    data = body.model_dump(exclude_unset=True, by_alias=False)
    for key, value in data.items():
        setattr(e, key, value)
    db.commit()
    db.refresh(e)
    return EmployeeOut.from_orm_model(e).model_dump_camel()
