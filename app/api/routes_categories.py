from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.crud import get_categories
from app.dependencies import get_db
from app.schemas.category import CategoryResponse

router = APIRouter(prefix="/categories", tags=["Категории"])


@router.get("", response_model=list[CategoryResponse], summary="Справочник категорий")
def list_categories(
    type: Optional[str] = None,
    db: Session = Depends(get_db),
) -> list[CategoryResponse]:
    return get_categories(db, type=type)
