"""Интернационализация (P3.5) — фундамент мультиязычности.

Не переводит весь UI (это поэтапная работа по сотням строк), а даёт механизм: каталог
переводов, определение языка из Accept-Language, функцию translate с graceful-fallback.
Используется для выхода за пределы РФ, когда понадобится английская локаль.
"""
from __future__ import annotations

SUPPORTED_LANGUAGES = ("ru", "en")
DEFAULT_LANGUAGE = "ru"

# Каталог переводов: ключ -> {язык: строка}. Расширяется по мере локализации UI.
TRANSLATIONS: dict[str, dict[str, str]] = {
    "auth.email_taken": {
        "ru": "Пользователь с таким email уже зарегистрирован.",
        "en": "A user with this email is already registered.",
    },
    "auth.consent_required": {
        "ru": "Необходимо согласие на обработку персональных данных.",
        "en": "Consent to personal data processing is required.",
    },
    "auth.invalid_credentials": {
        "ru": "Неверный email или пароль.",
        "en": "Invalid email or password.",
    },
    "common.not_found": {"ru": "Не найдено.", "en": "Not found."},
    "common.unauthorized": {"ru": "Требуется аутентификация.", "en": "Authentication required."},
    "nav.dashboard": {"ru": "Дашборд", "en": "Dashboard"},
    "nav.transactions": {"ru": "Операции", "en": "Transactions"},
    "nav.obligations": {"ru": "Обязательства", "en": "Obligations"},
    "nav.goals": {"ru": "Цели", "en": "Goals"},
    "nav.planning": {"ru": "Прогнозирование", "en": "Planning"},
    "action.add": {"ru": "Добавить", "en": "Add"},
    "action.delete": {"ru": "Удалить", "en": "Delete"},
    "action.save": {"ru": "Сохранить", "en": "Save"},
    "action.cancel": {"ru": "Отмена", "en": "Cancel"},
}


def normalize_language(lang: str | None) -> str:
    """Приводит код языка к поддерживаемому; неизвестный/пустой → язык по умолчанию."""
    if not lang:
        return DEFAULT_LANGUAGE
    code = lang.strip().lower()[:2]
    return code if code in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE


def parse_accept_language(header: str | None) -> str:
    """Первый поддерживаемый язык из HTTP-заголовка Accept-Language."""
    if not header:
        return DEFAULT_LANGUAGE
    for part in header.split(","):
        code = part.split(";")[0].strip().lower()[:2]
        if code in SUPPORTED_LANGUAGES:
            return code
    return DEFAULT_LANGUAGE


def translate(key: str, lang: str = DEFAULT_LANGUAGE) -> str:
    """Перевод по ключу. Неизвестный ключ возвращается как есть (graceful)."""
    lang = normalize_language(lang)
    entry = TRANSLATIONS.get(key)
    if entry is None:
        return key
    return entry.get(lang) or entry.get(DEFAULT_LANGUAGE) or key


def catalog(lang: str) -> dict[str, str]:
    """Весь словарь переводов для языка — для потребления фронтендом."""
    lang = normalize_language(lang)
    return {key: (entry.get(lang) or entry.get(DEFAULT_LANGUAGE) or key)
            for key, entry in TRANSLATIONS.items()}
