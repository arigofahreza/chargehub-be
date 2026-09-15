from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.limiter import limiter
from app.models.user import User
from app.models.employee import Employee
from app.models.category import EmployeeCategory
from app.schemas.user import UserRegister, UserLogin, UserOut, UserUpdate, TokenOut, AdminUserOut
from app.auth import hash_password, verify_password, create_access_token, get_current_user, require_admin

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def _user_out(user: User) -> UserOut:
    return UserOut(
        id=user.id,
        username=user.username,
        phone=getattr(user, "phone", None),
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active,
        role=user.role,
    )


@router.post("/register", status_code=201)
def register(
    body: UserRegister,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(status_code=400, detail="Username sudah digunakan")
    cat = db.query(EmployeeCategory).filter(EmployeeCategory.name == body.jabatan).first() if body.jabatan else None
    user = User(
        username=body.username,
        phone=body.phone,
        hashed_password=hash_password(body.password),
        first_name=body.first_name,
        last_name=body.last_name,
        role_category_id=cat.id if cat else None,
    )
    db.add(user)

    full_name = f"{body.first_name} {body.last_name}".strip()
    initials = "".join(p[0].upper() for p in full_name.split() if p)[:2]
    employee = Employee(
        name=full_name,
        job_title=body.jabatan or "",
        phone=body.phone or "",
        initials=initials,
        status="active",
    )
    db.add(employee)

    db.commit()
    db.refresh(user)
    return AdminUserOut.from_user(user).model_dump_camel()


_DUMMY_HASH = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"


@router.post("/login")
@limiter.limit("10/minute")
def login(request: Request, body: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == body.username).first()
    # Always run bcrypt — prevents username enumeration via timing side-channel
    password_ok = verify_password(body.password, user.hashed_password if user else _DUMMY_HASH)
    if not user or not password_ok or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Username atau password salah")
    token = create_access_token({"sub": user.id})
    result = TokenOut(access_token=token, token_type="bearer", user=_user_out(user).model_dump_camel())
    return result.model_dump_camel()


users_router = APIRouter(prefix="/api/v1/users", tags=["users"])


@users_router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return _user_out(current_user).model_dump_camel()


@users_router.patch("/me")
def update_me(
    body: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if body.first_name is not None:
        current_user.first_name = body.first_name.strip()
    if body.last_name is not None:
        current_user.last_name = body.last_name.strip()
    if body.phone is not None:
        current_user.phone = body.phone.strip()
    db.commit()
    db.refresh(current_user)
    return _user_out(current_user).model_dump_camel()
