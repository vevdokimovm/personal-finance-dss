from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.dependencies import get_current_user_id, get_db, require_admin
from app.services.analytics import experiment_results
from app.services.experiments import (
    create_experiment,
    delete_experiment,
    get_experiment,
    get_or_assign_variant,
    list_experiments,
    update_experiment,
)

router = APIRouter(tags=["A/B-эксперименты"])
admin_router = APIRouter(
    prefix="/admin/experiments",
    tags=["A/B-эксперименты (админ)"],
    dependencies=[Depends(require_admin)],
)


# ── Публичный: получить вариант (для приложения) ─────────────────────────
@router.get("/experiments/{key}/variant", summary="Получить вариант A/B-эксперимента")
def get_variant_endpoint(
    key: str,
    sid: str | None = None,
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> dict:
    """Вариант subject в эксперименте. subject = user_id (аутентифицирован) либо `sid`
    (стабильный клиентский id анонима). `variant=null` — control / нет участия."""
    variant = get_or_assign_variant(db, key, user_id=user_id, session_id=sid)
    return {"experiment": key, "variant": variant}


# ── Админ: управление и результаты ───────────────────────────────────────
class VariantIn(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    weight: int = Field(gt=0)


class ExperimentCreate(BaseModel):
    key: str = Field(min_length=1, max_length=64)
    name: str = ""
    description: str | None = None
    variants: list[VariantIn] = Field(min_length=1)
    conversion_event: str | None = None
    status: str = "draft"


class ExperimentUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    variants: list[VariantIn] | None = None
    conversion_event: str | None = None
    status: str | None = None


class ExperimentResponse(BaseModel):
    key: str
    name: str
    description: str | None = None
    status: str
    variants: list[dict]
    conversion_event: str | None = None

    model_config = {"from_attributes": True}


@admin_router.post("", response_model=ExperimentResponse, status_code=status.HTTP_201_CREATED)
def create_experiment_endpoint(payload: ExperimentCreate, db: Session = Depends(get_db)):
    if get_experiment(db, payload.key) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Эксперимент с таким key уже есть.")
    try:
        return create_experiment(
            db,
            payload.key,
            name=payload.name,
            description=payload.description,
            variants=[v.model_dump() for v in payload.variants],
            conversion_event=payload.conversion_event,
            status=payload.status,
        )
    except ValueError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc))


@admin_router.get("", response_model=list[ExperimentResponse])
def list_experiments_endpoint(db: Session = Depends(get_db)):
    return list_experiments(db)


@admin_router.patch("/{key}", response_model=ExperimentResponse)
def update_experiment_endpoint(key: str, payload: ExperimentUpdate, db: Session = Depends(get_db)):
    try:
        experiment = update_experiment(
            db,
            key,
            name=payload.name,
            description=payload.description,
            variants=([v.model_dump() for v in payload.variants] if payload.variants else None),
            conversion_event=payload.conversion_event,
            status=payload.status,
        )
    except ValueError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc))
    if experiment is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Эксперимент не найден.")
    return experiment


@admin_router.delete("/{key}")
def delete_experiment_endpoint(key: str, db: Session = Depends(get_db)):
    if not delete_experiment(db, key):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Эксперимент не найден.")
    from fastapi import Response

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@admin_router.get("/{key}/results", summary="Результаты эксперимента: assigned/converted/rate")
def experiment_results_endpoint(key: str, db: Session = Depends(get_db)) -> dict:
    results = experiment_results(db, key)
    if results is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Эксперимент не найден.")
    return results
