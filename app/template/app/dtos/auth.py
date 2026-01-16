from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, ConfigDict, EmailStr, SecretStr, StringConstraints

from app.dtos.utils.utils import DBStr, IDStr


class UserBase(BaseModel):
    name: DBStr
    email: EmailStr
    phone_number: DBStr | None = None


PasswordStr = Annotated[SecretStr, StringConstraints(min_length=8, max_length=255)]


class UserCreateRequest(UserBase):
    password: PasswordStr


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: PasswordStr


class UserResponse(UserBase):
    id: IDStr
    email: EmailStr
    phone_number: DBStr | None = None
    is_email_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserCreateResponse(BaseModel):
    user: UserResponse


CodeStr = Annotated[
    str, StringConstraints(min_length=6, max_length=6, pattern=r"^[A-Za-z0-9]{6}$")
]


class EmailVerificationRequest(BaseModel):
    code: CodeStr


class ResendEmailVerificationRequest(BaseModel):
    email: EmailStr


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    code: CodeStr
    new_password: PasswordStr
