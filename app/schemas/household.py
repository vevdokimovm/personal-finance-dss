from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class HouseholdRole(str, Enum):
    owner = "owner"
    member = "member"
    viewer = "viewer"


class InviteRole(str, Enum):
    """Роли, на которые можно пригласить. owner назначить приглашением нельзя —
    владелец один и задаётся созданием household (Pydantic отвергнет owner здесь → 422)."""

    member = "member"
    viewer = "viewer"


class HouseholdCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class HouseholdUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class HouseholdResponse(BaseModel):
    id: int
    name: str
    owner_id: str
    role: str  # роль текущего пользователя в этом household
    member_count: int
    created_at: datetime


class HouseholdMemberResponse(BaseModel):
    user_id: str
    email: Optional[EmailStr] = None
    role: str
    joined_at: datetime


class HouseholdInviteCreate(BaseModel):
    email: Optional[EmailStr] = None
    role: InviteRole = InviteRole.member


class HouseholdInviteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    household_id: int
    email: Optional[EmailStr] = None
    role: str
    status: str
    expires_at: datetime
    created_at: datetime
    # token отдаётся только в ответе на создание (чтобы owner мог передать ссылку),
    # в списках приглашений не светится.
    token: Optional[str] = None
    invite_url: Optional[str] = None


class InviteAcceptResponse(BaseModel):
    household_id: int
    role: str
