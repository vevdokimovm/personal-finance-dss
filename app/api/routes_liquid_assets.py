from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database.crud import (
    create_liquid_asset,
    delete_liquid_asset,
    get_liquid_assets,
)
from app.dependencies import get_db
from app.schemas.liquid_asset import LiquidAssetCreate, LiquidAssetResponse

router = APIRouter(prefix="/liquid-assets", tags=["Ликвидные активы"])


@router.get("", response_model=list[LiquidAssetResponse], summary="Список ликвидных активов (Bliq)")
def list_assets(db: Session = Depends(get_db)) -> list[LiquidAssetResponse]:
    return get_liquid_assets(db)


@router.post(
    "",
    response_model=LiquidAssetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить ликвидный актив (депозит, накопит. счёт, кэш)",
)
def add_asset(payload: LiquidAssetCreate, db: Session = Depends(get_db)) -> LiquidAssetResponse:
    return create_liquid_asset(
        db,
        name=payload.name,
        amount=payload.amount,
        interest_rate=payload.interest_rate,
        type=payload.type,
        comment=payload.comment,
    )


@router.delete("/{asset_id}", summary="Удалить ликвидный актив")
def remove_asset(asset_id: int, db: Session = Depends(get_db)):
    if delete_liquid_asset(db, asset_id) is None:
        raise HTTPException(status_code=404, detail="Актив не найден")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
