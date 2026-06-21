"""Локализация — отдача словаря переводов фронтенду (P3.5)."""
from __future__ import annotations

from fastapi import APIRouter, Header, Query

from app.i18n import SUPPORTED_LANGUAGES, catalog, normalize_language, parse_accept_language

router = APIRouter(prefix="/i18n", tags=["Локализация"])


@router.get("/translations", summary="Словарь переводов для языка (для фронтенда)")
def translations(
    lang: str | None = Query(None, description="Код языка (ru/en). По умолчанию — из Accept-Language."),
    accept_language: str | None = Header(None),
) -> dict:
    resolved = normalize_language(lang) if lang else parse_accept_language(accept_language)
    return {
        "language": resolved,
        "supported": list(SUPPORTED_LANGUAGES),
        "translations": catalog(resolved),
    }
