"""Маршруты household — совместные/семейные бюджеты (P3.7).

Все эндпоинты требуют аутентификации. Видимость и управление разграничены ролью:
не-член household получает 404 на приватные ресурсы (существование не палится),
член-не-owner — 403 на управляющие действия. Запись общих данных (через
household_id в обычных create-эндпоинтах) проверяется отдельно — там, где она
происходит (см. can_write_household).
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.database.crud import (
    accept_invite,
    create_household,
    create_invite,
    delete_household,
    get_household,
    get_household_invites,
    get_household_members,
    get_household_role,
    get_invite_by_id,
    get_membership,
    get_user_by_id,
    get_user_households,
    household_member_count,
    leave_household,
    remove_member,
    rename_household,
    revoke_invite,
)
from app.database.models import User
from app.dependencies import get_db, require_user
from app.schemas.household import (
    HouseholdCreate,
    HouseholdInviteCreate,
    HouseholdInviteResponse,
    HouseholdMemberResponse,
    HouseholdResponse,
    HouseholdUpdate,
    InviteAcceptResponse,
)
from app.services.event_logger import log_event

router = APIRouter(prefix="/households", tags=["Совместные бюджеты"])


# ─────────────────────────── helpers ───────────────────────────

def _household_response(db: Session, household, user_id: str) -> HouseholdResponse:
    return HouseholdResponse(
        id=household.id,
        name=household.name,
        owner_id=household.owner_id,
        role=get_household_role(db, household.id, user_id) or "",
        member_count=household_member_count(db, household.id),
        created_at=household.created_at,
    )


def _require_member(db: Session, household_id: int, user: User):
    """Член household или 404 (существование household не раскрываем не-членам)."""
    membership = get_membership(db, household_id, user.id)
    if membership is None:
        raise HTTPException(status_code=404, detail="Household не найден")
    return membership


def _require_owner(db: Session, household_id: int, user: User) -> None:
    role = get_household_role(db, household_id, user.id)
    if role is None:
        raise HTTPException(status_code=404, detail="Household не найден")
    if role != "owner":
        raise HTTPException(
            status_code=403, detail="Только владелец может выполнить это действие"
        )


def _invite_url(request: Request, token: str) -> str:
    return str(request.base_url).rstrip("/") + f"/join?token={token}"


# ─────────────────────────── household CRUD ───────────────────────────

@router.post(
    "",
    response_model=HouseholdResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать household (стать владельцем)",
)
def create_household_endpoint(
    payload: HouseholdCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
) -> HouseholdResponse:
    household = create_household(db, user_id=user.id, name=payload.name)
    log_event("household_created", {"household_id": household.id}, user_id=user.id)
    return _household_response(db, household, user.id)


@router.get("", response_model=list[HouseholdResponse], summary="Мои households")
def list_households_endpoint(
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
) -> list[HouseholdResponse]:
    return [_household_response(db, h, user.id) for h in get_user_households(db, user.id)]


@router.get("/{household_id}", response_model=HouseholdResponse, summary="Детали household")
def get_household_endpoint(
    household_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
) -> HouseholdResponse:
    _require_member(db, household_id, user)
    household = get_household(db, household_id)
    if household is None:
        raise HTTPException(status_code=404, detail="Household не найден")
    return _household_response(db, household, user.id)


@router.patch(
    "/{household_id}", response_model=HouseholdResponse, summary="Переименовать household"
)
def rename_household_endpoint(
    household_id: int,
    payload: HouseholdUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
) -> HouseholdResponse:
    _require_owner(db, household_id, user)
    household = rename_household(db, household_id, payload.name)
    if household is None:
        raise HTTPException(status_code=404, detail="Household не найден")
    return _household_response(db, household, user.id)


@router.delete("/{household_id}", summary="Распустить household")
def delete_household_endpoint(
    household_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
):
    _require_owner(db, household_id, user)
    delete_household(db, household_id)
    log_event("household_deleted", {"household_id": household_id}, user_id=user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ─────────────────────────── члены ───────────────────────────

@router.get(
    "/{household_id}/members",
    response_model=list[HouseholdMemberResponse],
    summary="Члены household",
)
def list_members_endpoint(
    household_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
) -> list[HouseholdMemberResponse]:
    _require_member(db, household_id, user)
    result: list[HouseholdMemberResponse] = []
    for m in get_household_members(db, household_id):
        member_user = get_user_by_id(db, m.user_id)
        result.append(
            HouseholdMemberResponse(
                user_id=m.user_id,
                email=member_user.email if member_user else None,
                role=m.role,
                joined_at=m.joined_at,
            )
        )
    return result


@router.delete(
    "/{household_id}/members/{member_user_id}", summary="Удалить члена household"
)
def remove_member_endpoint(
    household_id: int,
    member_user_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
):
    _require_owner(db, household_id, user)
    if not remove_member(db, household_id, member_user_id):
        raise HTTPException(
            status_code=400, detail="Нельзя удалить владельца или пользователь не состоит в household"
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{household_id}/leave", summary="Покинуть household")
def leave_household_endpoint(
    household_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
):
    _require_member(db, household_id, user)
    if not leave_household(db, household_id, user.id):
        raise HTTPException(
            status_code=400,
            detail="Владелец не может покинуть household — распустите его или передайте владение",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ─────────────────────────── приглашения ───────────────────────────

@router.post(
    "/invites/{token}/accept",
    response_model=InviteAcceptResponse,
    summary="Принять приглашение по токену",
)
def accept_invite_endpoint(
    token: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
) -> InviteAcceptResponse:
    membership, error = accept_invite(db, token, user.id)
    if error == "expired":
        raise HTTPException(status_code=410, detail="Срок приглашения истёк")
    if error is not None or membership is None:
        raise HTTPException(status_code=400, detail="Приглашение недействительно")
    log_event(
        "household_member_joined",
        {"household_id": membership.household_id, "role": membership.role},
        user_id=user.id,
    )
    return InviteAcceptResponse(household_id=membership.household_id, role=membership.role)


@router.post(
    "/{household_id}/invites",
    response_model=HouseholdInviteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать приглашение",
)
def create_invite_endpoint(
    household_id: int,
    payload: HouseholdInviteCreate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
) -> HouseholdInviteResponse:
    _require_owner(db, household_id, user)
    invite = create_invite(
        db,
        household_id=household_id,
        created_by=user.id,
        role=payload.role.value,
        email=payload.email,
    )
    log_event("household_invite_created", {"household_id": household_id}, user_id=user.id)
    response = HouseholdInviteResponse.model_validate(invite)
    response.token = invite.token
    response.invite_url = _invite_url(request, invite.token)
    return response


@router.get(
    "/{household_id}/invites",
    response_model=list[HouseholdInviteResponse],
    summary="Приглашения household",
)
def list_invites_endpoint(
    household_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
) -> list[HouseholdInviteResponse]:
    _require_owner(db, household_id, user)
    # token из списка намеренно не отдаём — только в ответе на создание
    return [HouseholdInviteResponse.model_validate(inv) for inv in get_household_invites(db, household_id)]


@router.post("/{household_id}/invites/{invite_id}/revoke", summary="Отозвать приглашение")
def revoke_invite_endpoint(
    household_id: int,
    invite_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
):
    _require_owner(db, household_id, user)
    invite = get_invite_by_id(db, invite_id)
    if invite is None or invite.household_id != household_id:
        raise HTTPException(status_code=404, detail="Приглашение не найдено")
    revoke_invite(db, invite_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
