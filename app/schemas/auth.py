from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: Optional[str] = Field(default=None, max_length=255)
    consent: bool = Field(
        description="Согласие на обработку ПДн (152-ФЗ). ОБЯЗАТЕЛЬНОЕ поле без "
                    "значения по умолчанию: default=True на уровне контракта — "
                    "это предотмеченная галочка, надзор читает её как навязанное "
                    "согласие (юрблок L2). Явный false → отказ в регистрации.")
    newsletter_opt_in: bool = Field(
        default=False,
        description="Согласие на рекламную рассылку. Независимо от согласия на "
                    "обработку ПДн: склеивать обязательное с необязательным нельзя.")
    referral_code: Optional[str] = Field(
        default=None, max_length=12, description="Реферальный код пригласившего (необязательно).")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=10)
    new_password: str = Field(min_length=8, max_length=128)


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
    # MFA (раздел 4.4): при включённом втором факторе login возвращает mfa_required=True
    # и краткоживущий mfa_token (для /auth/mfa/verify) вместо полной сессии; access_token
    # тогда пуст.
    mfa_required: bool = False
    mfa_token: Optional[str] = None


class MfaEnrollResponse(BaseModel):
    secret: str
    provisioning_uri: str


class MfaConfirmRequest(BaseModel):
    code: str = Field(min_length=4, max_length=10)


class MfaConfirmResponse(BaseModel):
    recovery_codes: list[str]


class MfaVerifyRequest(BaseModel):
    mfa_token: str = Field(min_length=1)
    code: str = Field(min_length=4, max_length=16)


class MfaDisableRequest(BaseModel):
    code: str = Field(min_length=4, max_length=16)


class MfaStatusResponse(BaseModel):
    enabled: bool
