"""Уведомления: запуск email-рассылки (P2.5) + лента in-app уведомлений (P2.3)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import crud
from app.database.db import get_db
from app.database.models import User
from app.api._consent_guard import require_financial_consent
from app.dependencies import require_admin, require_user
from app.schemas.notification import NotificationFeed, NotificationOut

router = APIRouter(prefix="/notifications", tags=["Уведомления"])

# Гейт согласия на финданные — ПОЭНДПОИНТНО, а не на роутер целиком.
#
# Уведомления несут суммы: `app/services/notifications.py` кладёт в тело строку вида
# «Сводка за {месяц}: доход …, расход …, чистыми …», та же сводка уходит письмом и в
# Telegram. Значит лента отдаёт финансовый портрет и обязана требовать согласия — иначе
# ручное добавление одной операции защищено строже, чем регулярная выдача всей сводки
# (гипотеза H3c independent-expert, подтверждена чтением кода в v8.30.2).
#
# 🔴 Почему НЕ `include_router(..., dependencies=_FIN)`, как у остальных десяти роутеров:
# `POST /notifications/run` — cron-рассылка под `require_admin`. Она ходит от служебного
# администратора и обслуживает ВСЕХ пользователей сразу. Роутерный гейт потребовал бы
# согласия от админа на чужие данные, рассылка молча перестала бы работать, и узнали бы
# об этом по жалобе пользователя, а не по красному тесту. Поэтому список ниже точечный,
# а на `/run` стоит регрессионный тест, что гейта там нет.
_FIN = [Depends(require_financial_consent)]


@router.post("/run", summary="Запустить рассылку уведомлений (для cron)",
             dependencies=[Depends(require_admin)])
def run_notifications(db: Session = Depends(get_db)) -> dict:
    """Проверяет дедлайны целей и превышения бюджета по всем пользователям и шлёт
    недостающие уведомления. Идемпотентно (дедуп по месяцу) — безопасно дёргать по cron."""
    from app.services.notifications import run_all_notifications

    return run_all_notifications(db)


@router.get("/feed", summary="Лента моих уведомлений (колокольчик)",
            response_model=NotificationFeed, dependencies=_FIN)
def notifications_feed(
    unread_only: bool = Query(False, description="Только непрочитанные"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
) -> NotificationFeed:
    items = crud.get_notifications(db, user_id=user.id, unread_only=unread_only, limit=limit)
    return NotificationFeed(
        items=[NotificationOut.model_validate(n) for n in items],
        unread_count=crud.count_unread_notifications(db, user_id=user.id),
    )


@router.get("/unread-count", summary="Число непрочитанных уведомлений",
            dependencies=_FIN)
def notifications_unread_count(
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
) -> dict:
    return {"unread_count": crud.count_unread_notifications(db, user_id=user.id)}


@router.post("/{notification_id}/read", summary="Отметить уведомление прочитанным",
             dependencies=_FIN)
def notification_mark_read(
    notification_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
) -> dict:
    ok = crud.mark_notification_read(db, user_id=user.id, notification_id=notification_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Уведомление не найдено")
    return {"status": "ok"}


@router.post("/read-all", summary="Отметить все уведомления прочитанными",
             dependencies=_FIN)
def notifications_mark_all_read(
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
) -> dict:
    marked = crud.mark_all_notifications_read(db, user_id=user.id)
    return {"marked": marked}
