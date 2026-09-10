from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import require_permission
from app.models.user import User
from app.models.employee import Employee
from app.schemas.user import AdminUserOut, UserRolePatch

router = APIRouter(prefix="/api/v1/users", tags=["users-admin"])


@router.get("/for-employee")
def list_users_for_employee(
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("employees", "write")),
):
    users = db.query(User).filter(User.is_active == True).order_by(User.first_name).all()
    return [
        {
            "id": u.id,
            "fullName": f"{u.first_name} {u.last_name}".strip(),
            "phone": getattr(u, "phone", "") or "",
            "role": u.role,
        }
        for u in users
    ]


@router.get("")
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("users", "read")),
):
    users = db.query(User).order_by(User.username).all()
    return [AdminUserOut.from_user(u).model_dump_camel() for u in users]


@router.patch("/{user_id}/role")
def update_user_role(
    user_id: str,
    body: UserRolePatch,
    db: Session = Depends(get_db),
    current: User = Depends(require_permission("users", "write")),
):
    if user_id == current.id:
        raise HTTPException(status_code=400, detail="Tidak dapat mengubah role akun sendiri")
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    u.role_category_id = body.role_category_id
    db.commit()
    db.refresh(u)
    return AdminUserOut.from_user(u).model_dump_camel()


@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(require_permission("users", "write")),
):
    if user_id == current.id:
        raise HTTPException(status_code=400, detail="Tidak dapat menghapus akun sendiri")
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    if u.phone:
        emp = db.query(Employee).filter(Employee.phone == u.phone).first()
        if emp:
            db.delete(emp)
    db.delete(u)
    db.commit()
