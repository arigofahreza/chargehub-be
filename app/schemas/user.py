import re
from pydantic import BaseModel, Field, field_validator


class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    first_name: str = Field(alias="firstName")
    last_name: str = Field(default="", alias="lastName")

    model_config = {"populate_by_name": True}

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        pattern = r"^[^\s@]+@[^\s@]+\.[^\s@]{2,}$"
        if not re.match(pattern, v.strip()):
            raise ValueError("Format email tidak valid (contoh: nama@domain.com)")
        return v.strip().lower()

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
    username: str
    password: str


class UserUpdate(BaseModel):
    first_name: str | None = Field(None, alias="firstName")
    last_name: str | None = Field(None, alias="lastName")
    email: str | None = None

    model_config = {"populate_by_name": True}


class UserOut(BaseModel):
    id: str
    username: str
    email: str
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
