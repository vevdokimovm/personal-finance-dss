"""
Сервис продуктовой аналитики (LOG-01, LOG-02, LOG-03, LOG-08).

Запись отказоустойчива (NFR-13): логирование работает в собственной
изолированной сессии и при любом сбое лишь молча откатывается — основной
пользовательский запрос никогда не ломается из-за аналитики.
"""
from __future__ import annotations

from typing import Any, Optional

from app.database.db import SessionLocal
from app.database.models import Event, Recommendation

try:
    from app.config import settings
    _APP_VERSION: Optional[str] = getattr(settings, "APP_VERSION", None)
except Exception:
    _APP_VERSION = None

_SENSITIVE_KEYS = (
    "password", "passwd", "token", "secret", "api_key", "apikey",
    "authorization", "auth", "access_token", "refresh_token",
    "card_number", "cardnumber", "cvv", "cvc", "pan", "pin",
)
_MASK = "***"


def mask_sensitive(payload: Any) -> Any:
    """LOG-08: рекурсивно маскирует секреты и токены перед записью в лог."""
    if isinstance(payload, dict):
        masked: dict[str, Any] = {}
        for key, value in payload.items():
            if any(token in str(key).lower() for token in _SENSITIVE_KEYS):
                masked[key] = _MASK
            else:
                masked[key] = mask_sensitive(value)
        return masked
    if isinstance(payload, (list, tuple)):
        return [mask_sensitive(item) for item in payload]
    return payload


def log_event(
    event_type: str,
    payload: Optional[dict] = None,
    session_id: Optional[str] = None,
    user_id: Optional[int] = None,
) -> None:
    """LOG-01 / LOG-03: фиксирует продуктовое событие в таблице events."""
    db = SessionLocal()
    try:
        db.add(Event(
            user_id=user_id,
            session_id=session_id,
            event_type=event_type,
            event_payload=mask_sensitive(payload) if payload else None,
            app_version=_APP_VERSION,
        ))
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


def log_recommendation(result: dict, user_id: Optional[int] = None) -> None:
    """LOG-02: сохраняет полный снимок сгенерированной рекомендации."""
    db = SessionLocal()
    try:
        indicators = result.get("indicators", {}) or {}
        best = result.get("best") or {}
        explanation = best.get("explanation", {}) if isinstance(best, dict) else {}

        db.add(Recommendation(
            user_id=user_id,
            income_total=_to_float(indicators.get("It")),
            expense_total=_to_float(indicators.get("Et")),
            obligation_payments_total=_to_float(indicators.get("SigmaP")),
            balance_bt=_to_float(indicators.get("Bt")),
            bliq=_to_float(indicators.get("Bliq")),
            rt=_to_float(indicators.get("Rt")),
            lt=_to_float(indicators.get("Lt")),
            dt=_to_float(indicators.get("Dt")),
            blr=_to_float(indicators.get("BLR")),
            optimal_x_obl=_to_float(best.get("x_obligations")),
            optimal_x_res=_to_float(best.get("x_reserve")),
            optimal_x_goals=_to_float(best.get("x_goals")),
            u_score=_to_float(best.get("utility")),
            alternatives_total=_to_int(result.get("alternatives_total")),
            alternatives_accepted=_to_int(result.get("admissible_count")),
            reasoning_text=_compose_reasoning(explanation),
        ))
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


def _to_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _to_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _compose_reasoning(explanation: Any) -> Optional[str]:
    if not isinstance(explanation, dict):
        return None
    parts: list[str] = []
    insight = explanation.get("insight")
    if insight:
        parts.append(str(insight))
    gains = explanation.get("gains") or []
    if gains:
        parts.append("Выгоды: " + "; ".join(str(g) for g in gains))
    costs = explanation.get("costs") or []
    if costs:
        parts.append("Издержки: " + "; ".join(str(c) for c in costs))
    return " ".join(parts) if parts else None
