from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database.crud import (
    create_liquid_asset,
    delete_liquid_asset,
    get_liquid_assets,
    restore_liquid_asset,
    update_liquid_asset,
)
from app.api._guards import ensure_can_share
from app.dependencies import get_current_user_id, get_db
from app.schemas.liquid_asset import LiquidAssetCreate, LiquidAssetResponse, LiquidAssetUpdate
from app.services.event_logger import log_event

router = APIRouter(prefix="/liquid-assets", tags=["Ликвидные активы"])


@router.get("", response_model=list[LiquidAssetResponse], summary="Список ликвидных активов (Bliq)")
def list_assets(
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> list[LiquidAssetResponse]:
    return get_liquid_assets(db, user_id=user_id)


@router.post(
    "",
    response_model=LiquidAssetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить ликвидный актив (депозит, накопит. счёт, кэш)",
)
def add_asset(
    payload: LiquidAssetCreate,
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> LiquidAssetResponse:
    # Общий котёл требует права на него — одна проверка на все сущности
    # (`_guards.ensure_can_share`), четыре копии разошлись бы при первой правке.
    ensure_can_share(db, payload.household_id, user_id)
    return create_liquid_asset(
        db,
        name=payload.name,
        amount=payload.amount,
        interest_rate=payload.interest_rate,
        type=payload.type,
        comment=payload.comment,
        currency=payload.currency,
        user_id=user_id,
        household_id=payload.household_id,
    )


@router.put(
    "/{asset_id}",
    response_model=LiquidAssetResponse,
    summary="Изменить ликвидный актив (частично, только переданные поля)",
)
def update_asset(
    asset_id: int,
    payload: LiquidAssetUpdate,
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> LiquidAssetResponse:
    asset = update_liquid_asset(
        db, asset_id, user_id=user_id, **payload.model_dump(exclude_unset=True)
    )
    if asset is None:
        raise HTTPException(status_code=404, detail="Актив не найден")
    log_event("liquid_asset_updated", {"asset_id": asset_id})
    return asset


@router.delete("/{asset_id}", summary="Удалить ликвидный актив")
def remove_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
):
    if delete_liquid_asset(db, asset_id, user_id=user_id) is None:
        raise HTTPException(status_code=404, detail="Актив не найден")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{asset_id}/restore",
    response_model=LiquidAssetResponse,
    summary="Восстановить удалённый ликвидный актив (undo)",
)
def restore_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> LiquidAssetResponse:
    asset = restore_liquid_asset(db, asset_id, user_id=user_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="Удалённый актив не найден")
    log_event("liquid_asset_restored", {"asset_id": asset_id})
    return asset
