from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, UserOut, UserUpdate, TokenOut
from app.auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def _user_out(user: User) -> UserOut:
    return UserOut(
        id=user.id,
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active,
        role=user.role,
    )


@router.post("/register", status_code=201)
def register(body: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(status_code=400, detail="Username sudah digunakan")
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email sudah terdaftar")
    user = User(
        username=body.username,
        email=body.email,
        hashed_password=hash_password(body.password),
        first_name=body.first_name,
        last_name=body.last_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _user_out(user).model_dump_camel()


@router.post("/login")
def login(body: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == body.username).first()
    if not user or not verify_password(body.password, user.hashed_password):
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
    if body.email is not None:
        existing = db.query(User).filter(User.email == body.email, User.id != current_user.id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email sudah digunakan akun lain")
        current_user.email = body.email.strip()
    db.commit()
    db.refresh(current_user)
    return _user_out(current_user).model_dump_camel()
