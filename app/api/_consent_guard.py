"""Гейт согласия на обработку финансовых данных (юрблок L1).

Зачем отдельный модуль. До этого согласие типа `financial_data` записывалось в
`user_consents`, но **не ограничивало ничего**: пользователь мог не давать его
и всё равно вводить доходы, обязательства и цели. Такая конструкция хуже, чем
отсутствие согласия: документ обещает раздельное основание для обработки
финансового портрета, а код обрабатывает его по основанию для ПДн.

Замысел зафиксирован в `app/core/legal.py`: обязательное при регистрации —
только обработка ПДн, **финансовые данные запрашиваются в момент их ввода**.
Здесь этот момент и наступает.

Почему 403, а не 422: данные корректны, отказ по основанию, а не по форме.
Тело ответа машиночитаемо, чтобы фронт показал экран согласия, а не текст
ошибки:

    {"detail": {"code": "consent_required",
                "consent_type": "financial_data",
                "document": {...}, "message": "..."}}
"""
from __future__ import annotations

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.legal import CONSENT_FINANCIAL_DATA, LEGAL_DOCUMENTS
from app.database.models import User
from app.dependencies import get_current_user, get_db
from app.services.consent import has_consent


def _refuse(consent_type: str) -> HTTPException:
    document = LEGAL_DOCUMENTS.get(consent_type, {})
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={
            "code": "consent_required",
            "consent_type": consent_type,
            "document": {
                "title": document.get("title"),
                "version": document.get("version"),
                "url": document.get("url"),
            },
            "message": (
                "Для работы с финансовыми данными нужно отдельное согласие "
                "на их обработку. Его можно дать в настройках профиля."
            ),
        },
    )


def require_financial_consent(
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Гейт для эндпоинтов финансового портрета.

    Анонимный режим проходит без проверки сознательно: демо-данные не
    относятся к определённому субъекту, 152-ФЗ к ним неприменим, и требовать
    согласие там означало бы сломать демо ради формальности.

    Для авторизованного пользователя согласие обязательно: именно с этого
    момента обрабатывается финансовый портрет конкретного человека.
    """
    if user is None:
        return
    if not has_consent(db, user.id, CONSENT_FINANCIAL_DATA):
        raise _refuse(CONSENT_FINANCIAL_DATA)
