"""Юридический блок (P1.1): публикация документов, footer, контакты, связка согласия.

Проверяет серверный рендер юр-страниц, наличие ключевых нормативных формулировок
(152-ФЗ, 39-ФЗ), подстановку реквизитов оператора из настроек, правовые ссылки в
footer и информированность согласия при регистрации. Браузерное поведение (клики)
сюда не входит — только SSR.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.config import settings

LEGAL_PAGES = [
    "/legal/privacy",
    "/legal/terms",
    "/legal/consent",
    "/legal/financial-consent",
    "/contacts",
]


@pytest.mark.parametrize("path", LEGAL_PAGES)
def test_legal_page_renders(client: TestClient, path: str) -> None:
    resp = client.get(path)
    assert resp.status_code == 200
    assert "text/html" in resp.headers.get("content-type", "")
    assert len(resp.text) > 500


def test_privacy_has_152fz_and_operator(client: TestClient) -> None:
    html = client.get("/legal/privacy").text
    assert "152-ФЗ" in html
    assert "Политика обработки персональных данных" in html
    assert settings.LEGAL_OPERATOR_NAME in html


def test_terms_has_investment_disclaimer_39fz(client: TestClient) -> None:
    # Ключевой финтех-дисклеймер: сервис не инвестсоветник (39-ФЗ).
    html = client.get("/legal/terms").text
    assert "39-ФЗ" in html
    assert "не является индивидуальной инвестиционной рекомендацией" in html


def test_consent_has_withdrawal(client: TestClient) -> None:
    html = client.get("/legal/consent").text
    assert "отзыв" in html.lower()


def test_financial_consent_mentions_import_paths(client: TestClient) -> None:
    html = client.get("/legal/financial-consent").text
    assert "выписк" in html.lower()
    assert "ручн" in html.lower()


def test_contacts_has_operator_email(client: TestClient) -> None:
    html = client.get("/contacts").text
    assert settings.LEGAL_CONTACT_EMAIL in html


def test_footer_has_legal_links(client: TestClient) -> None:
    # Footer наследуется base.html → присутствует на любой странице.
    html = client.get("/").text
    assert 'href="/legal/privacy"' in html
    assert 'href="/legal/terms"' in html
    assert 'href="/legal/financial-consent"' in html
    assert 'href="/contacts"' in html


def test_registration_consent_links_to_documents(client: TestClient) -> None:
    # Чекбокс согласия 152-ФЗ ведёт на опубликованные документы — согласие информированное.
    html = client.get("/").text
    assert 'id="auth-consent"' in html
    assert 'href="/legal/privacy"' in html
    assert 'href="/legal/consent"' in html


class TestDraftBanner:
    """Страховка: пока реквизиты оператора не подтверждены — на документах виден баннер."""

    def test_banner_visible_by_default(self, client: TestClient) -> None:
        # По умолчанию ИНН/адрес пусты и флаг не выставлен → баннер виден.
        html = client.get("/legal/privacy").text
        assert "legal-draft-banner" in html

    def test_banner_hidden_when_details_confirmed(
        self, client: TestClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(settings, "LEGAL_OPERATOR_INN", "7700000000")
        monkeypatch.setattr(settings, "LEGAL_OPERATOR_ADDRESS", "г. Москва, ул. Пример, д. 1")
        monkeypatch.setattr(settings, "LEGAL_DETAILS_CONFIRMED", True)
        html = client.get("/legal/privacy").text
        assert "legal-draft-banner" not in html
