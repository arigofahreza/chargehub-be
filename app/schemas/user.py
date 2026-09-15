import re
from pydantic import BaseModel, Field, field_validator


class UserRegister(BaseModel):
    username: str
    phone: str
    password: str
    first_name: str = Field(alias="firstName")
    last_name: str = Field(default="", alias="lastName")
    jabatan: str | None = None

    model_config = {"populate_by_name": True}

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        stripped = re.sub(r"[\s\-\(\)]", "", v.strip())
        if not re.match(r"^\+?[\d]{8,15}$", stripped):
            raise ValueError("Nomor telepon tidak valid")
        return stripped

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        errors = []
        if len(v) < 8:
            errors.append("minimal 8 karakter")
        if not re.search(r"[A-Z]", v):
            errors.append("huruf kapital (A-Z)")
        if not re.search(r"[a-z]", v):
            errors.append("huruf kecil (a-z)")
        if not re.search(r"\d", v):
            errors.append("angka (0-9)")
        if not re.search(r"[^A-Za-z0-9]", v):
            errors.append("simbol (!@#$...)")
        if errors:
            raise ValueError(f"Password harus mengandung: {', '.join(errors)}")
        return v


class UserLogin(BaseModel):
    username: str = Field(max_length=64)
    password: str = Field(max_length=128)


class UserUpdate(BaseModel):
    first_name: str | None = Field(None, alias="firstName")
    last_name: str | None = Field(None, alias="lastName")
    phone: str | None = None

    model_config = {"populate_by_name": True}


class UserOut(BaseModel):
    id: str
    username: str
    phone: str | None = None
    first_name: str = Field(serialization_alias="firstName")
    last_name: str = Field(serialization_alias="lastName")
    is_active: bool = Field(serialization_alias="isActive")
    role: str = "operator"

    model_config = {"populate_by_name": True}

    def model_dump_camel(self) -> dict:
        d = self.model_dump(by_alias=True)
        d["fullName"] = f"{self.first_name} {self.last_name}".strip()
        return d


class TokenOut(BaseModel):
    access_token: str = Field(serialization_alias="accessToken")
    token_type: str = Field(default="bearer", serialization_alias="tokenType")
    user: dict

    model_config = {"populate_by_name": True}

    def model_dump_camel(self) -> dict:
        return self.model_dump(by_alias=True)


class UserRolePatch(BaseModel):
    role_category_id: str = Field(alias="roleCategoryId")

    model_config = {"populate_by_name": True}


class AdminUserOut(BaseModel):
    id: str
    username: str
    phone: str | None = None
    first_name: str = Field(serialization_alias="firstName")
    last_name: str = Field(serialization_alias="lastName")
    full_name: str = Field(serialization_alias="fullName")
    is_active: bool = Field(serialization_alias="isActive")
    role: str
    role_category_id: str | None = Field(None, serialization_alias="roleCategoryId")

    model_config = {"populate_by_name": True}

    def model_dump_camel(self) -> dict:
        return self.model_dump(by_alias=True)

    @classmethod
    def from_user(cls, u) -> "AdminUserOut":
        return cls(
            id=u.id,
            username=u.username,
            phone=getattr(u, "phone", None),
            first_name=u.first_name,
            last_name=u.last_name,
            full_name=f"{u.first_name} {u.last_name}".strip(),
            is_active=u.is_active,
            role=u.role,
            role_category_id=getattr(u, "role_category_id", None),
        )
