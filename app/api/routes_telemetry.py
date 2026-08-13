"""Телеметрия принятия совета (волна 0, п. 0.6, `docs/model/telemetry_spec.md`).

ДОРМАНТНО за `settings.TELEMETRY_COLLECTION_ENABLED` (default False, INFRA-13-style
флаг в `app/config.py`) — 404, пока не включён. Правовой контур обезличивания для
использования этих данных в сертификации модели (152-ФЗ, ROADMAP §8.2а) закрывается
юристом отдельно от кода; переключение флага — решение владельца ПОСЛЕ этого, не
автоматика при деплое (тот же принцип, что у Plaid — `_ensure_plaid_enabled`).

Роутер подключён в `app/api/router.py` за гейтом `require_financial_consent`
(тот же, что transactions/obligations/goals/liquid-assets): `advice`/
`input_snapshot_hash` производны от финансового портрета пользователя.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database.crud import create_advice_event, record_advice_decision
from app.database.models import User
from app.dependencies import get_db, require_user
from app.schemas.telemetry import AdviceDecision, AdviceEventCreate, AdviceEventResponse

router = APIRouter(prefix="/telemetry", tags=["Телеметрия принятия совета"])


def _ensure_telemetry_enabled() -> None:
    if not settings.TELEMETRY_COLLECTION_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Телеметрия принятия совета не активирована "
                "(TELEMETRY_COLLECTION_ENABLED=False — ждёт правового контура "
                "обезличивания, ROADMAP §8.2а)."
            ),
        )


@router.post(
    "/advice-events",
    response_model=AdviceEventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Записать показ плана",
)
def create_advice_event_endpoint(
    payload: AdviceEventCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
) -> AdviceEventResponse:
    _ensure_telemetry_enabled()
    event = create_advice_event(
        db=db,
        user_id=user.id,
        model_version=payload.model_version,
        app_version=payload.app_version,
        input_snapshot_hash=payload.input_snapshot_hash,
        advice=payload.advice,
    )
    return AdviceEventResponse.model_validate(event)


@router.patch(
    "/advice-events/{plan_id}/decision",
    response_model=AdviceEventResponse,
    summary="Записать решение пользователя по показанному плану",
)
def record_advice_decision_endpoint(
    plan_id: str,
    payload: AdviceDecision,
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
) -> AdviceEventResponse:
    _ensure_telemetry_enabled()
    event = record_advice_decision(
        db=db,
        plan_id=plan_id,
        user_id=user.id,
        outcome=payload.outcome,
        modified_to=payload.modified_to,
    )
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Событие с таким plan_id не найдено.",
        )
    return AdviceEventResponse.model_validate(event)
