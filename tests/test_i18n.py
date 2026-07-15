"""Интернационализация (P3.5)."""
from __future__ import annotations

from app.i18n import (
    DEFAULT_LANGUAGE,
    catalog,
    normalize_language,
    parse_accept_language,
    translate,
)


class TestTranslate:
    def test_russian(self) -> None:
        assert translate("action.add", "ru") == "Добавить"

    def test_english(self) -> None:
        assert translate("action.add", "en") == "Add"

    def test_unknown_key_returns_key(self) -> None:
        assert translate("does.not.exist", "en") == "does.not.exist"

    def test_default_language_fallback(self) -> None:
        # неподдерживаемый язык падает на default (ru)
        assert translate("action.save", "de") == "Сохранить"


class TestNormalizeLanguage:
    def test_supported(self) -> None:
        assert normalize_language("en") == "en"

    def test_unknown_falls_back(self) -> None:
        assert normalize_language("fr") == DEFAULT_LANGUAGE

    def test_none_falls_back(self) -> None:
        assert normalize_language(None) == DEFAULT_LANGUAGE

    def test_locale_with_region(self) -> None:
        assert normalize_language("en-US") == "en"


class TestParseAcceptLanguage:
    def test_picks_supported(self) -> None:
        assert parse_accept_language("en-US,en;q=0.9,fr;q=0.8") == "en"

    def test_skips_unsupported(self) -> None:
        assert parse_accept_language("fr-FR,de;q=0.9,ru;q=0.8") == "ru"

    def test_empty_default(self) -> None:
        assert parse_accept_language(None) == DEFAULT_LANGUAGE


class TestCatalog:
    def test_full_catalog_en(self) -> None:
        cat = catalog("en")
        assert cat["nav.dashboard"] == "Dashboard"
        assert len(cat) > 5


class TestI18nEndpoint:
    def test_translations_endpoint_explicit_lang(self, client) -> None:
        r = client.get("/api/i18n/translations?lang=en")
        assert r.status_code == 200
        body = r.json()
        assert body["language"] == "en"
        assert body["translations"]["action.add"] == "Add"

    def test_translations_endpoint_accept_header(self, client) -> None:
        r = client.get("/api/i18n/translations", headers={"Accept-Language": "en-US,en;q=0.9"})
        assert r.status_code == 200
        assert r.json()["language"] == "en"
