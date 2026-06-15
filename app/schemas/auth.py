from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: Optional[str] = Field(default=None, max_length=255)
    consent: bool = Field(default=True, description="Согласие на обработку ПДн (152-ФЗ). Веб-форма требует явную галочку; явный false → отказ.")
    newsletter_opt_in: bool = Field(default=False, description="Согласие на новости/рассылку (необязательно).")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    display_name: Optional[str] = None
    created_at: Optional[datetime] = None
    email_verified: bool = False


class UpdateProfileRequest(BaseModel):
    display_name: Optional[str] = Field(default=None, max_length=255)


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1)
    new_password: str = Field(min_length=8, max_length=128)


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    verification_url: Optional[str] = None
