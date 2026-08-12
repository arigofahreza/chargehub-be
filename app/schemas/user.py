from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str = Field(alias="fullName")

    model_config = {"populate_by_name": True}


class UserLogin(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: str
    email: str
    full_name: str = Field(serialization_alias="fullName")
    is_active: bool = Field(serialization_alias="isActive")
    role: str = "operator"

    model_config = {"populate_by_name": True}

    def model_dump_camel(self) -> dict:
        return self.model_dump(by_alias=True)


class TokenOut(BaseModel):
    access_token: str = Field(serialization_alias="accessToken")
    token_type: str = Field(default="bearer", serialization_alias="tokenType")
    user: dict

    model_config = {"populate_by_name": True}

    def model_dump_camel(self) -> dict:
        return self.model_dump(by_alias=True)
