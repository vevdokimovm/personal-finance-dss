"""Реестр юридических документов и типов согласий (юрблок L1, L4).

Единственный источник правды о том, какие согласия существуют, какая редакция
текста действует сейчас и с какой даты. Версия хранится вместе с каждым
согласием пользователя: при изменении текста надо знать, на какую редакцию
согласился конкретный человек, иначе доказать согласие невозможно.

Правило изменения: НЕ править версию задним числом. Новая редакция текста —
новая версия здесь и новая дата вступления; старые записи согласий продолжают
ссылаться на прежнюю редакцию, и это правильно.
"""
from __future__ import annotations

from typing import Final

CONSENT_PERSONAL_DATA: Final = "personal_data"
CONSENT_FINANCIAL_DATA: Final = "financial_data"
CONSENT_MARKETING: Final = "marketing"

CONSENT_TYPES: Final[tuple[str, ...]] = (
    CONSENT_PERSONAL_DATA,
    CONSENT_FINANCIAL_DATA,
    CONSENT_MARKETING,
)

# Обязательное при регистрации — только обработка ПДн. Финансовые данные
# запрашиваются в момент их ввода, рассылка не запрашивается вовсе: склеивать
# обязательное с необязательным нельзя (навязанное согласие).
REQUIRED_AT_REGISTRATION: Final[tuple[str, ...]] = (CONSENT_PERSONAL_DATA,)

# Согласие, отзыв которого невозможен без удаления аккаунта: оно и есть
# основание обработки. Отзыв основания при сохранении данных — нарушение.
UNWITHDRAWABLE: Final[tuple[str, ...]] = (CONSENT_PERSONAL_DATA,)

_EFFECTIVE_FROM: Final = "2026-07-29"

LEGAL_DOCUMENTS: Final[dict[str, dict[str, str]]] = {
    CONSENT_PERSONAL_DATA: {
        "title": "Согласие на обработку персональных данных",
        "version": "1.0",
        "effective_from": _EFFECTIVE_FROM,
        "path": "docs/legal/consent-personal-data.md",
        "url": "/legal/consent",
    },
    CONSENT_FINANCIAL_DATA: {
        "title": "Согласие на обработку финансовых данных",
        "version": "1.0",
        "effective_from": _EFFECTIVE_FROM,
        "path": "docs/legal/consent-financial-data.md",
        "url": "/legal/financial-consent",
    },
    CONSENT_MARKETING: {
        "title": "Согласие на рекламную рассылку",
        "version": "1.0",
        "effective_from": _EFFECTIVE_FROM,
        "path": "docs/legal/consent-marketing.md",
        "url": "/legal/marketing-consent",
    },
    "privacy_policy": {
        "title": "Политика обработки персональных данных",
        "version": "1.0",
        "effective_from": _EFFECTIVE_FROM,
        "path": "docs/legal/privacy-policy.md",
        "url": "/legal/privacy",
    },
    "terms_of_service": {
        "title": "Пользовательское соглашение",
        "version": "1.0",
        "effective_from": _EFFECTIVE_FROM,
        "path": "docs/legal/terms-of-service.md",
        "url": "/legal/terms",
    },
    "cookie_policy": {
        "title": "Политика использования файлов cookie",
        "version": "1.0",
        "effective_from": _EFFECTIVE_FROM,
        "path": "docs/legal/cookie-policy.md",
        "url": "/legal/cookies",
    },
}

# Дисклеймер 39-ФЗ. Обязан выводиться НА САМОЙ странице рекомендаций, а не
# только в оферте (требование L5): пользователь принимает решение о деньгах на
# этом экране, здесь же должно стоять предупреждение.
DISCLAIMER_39FZ: Final = (
    "FINPILOT не является инвестиционным советником и не оказывает услуг по "
    "инвестиционному консультированию. Расчёты носят информационный характер и "
    "не являются индивидуальной инвестиционной рекомендацией. Решение и "
    "ответственность за него остаются за вами."
)


def is_known(consent_type: str) -> bool:
    return consent_type in CONSENT_TYPES


def current_version(consent_type: str) -> str:
    """Действующая редакция текста согласия."""
    if consent_type not in LEGAL_DOCUMENTS:
        raise ValueError(f"неизвестный документ: {consent_type}")
    return LEGAL_DOCUMENTS[consent_type]["version"]
