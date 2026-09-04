"""Юридический блок (P1.1): содержание опубликованных документов и связка согласия.

🔴 Переписан в v8.45.0. Раньше проверял SSR-рендер Jinja-страниц `/legal/*` — их больше
нет: тексты отдаёт `GET /api/legal/documents/{slug}`, а показывает React.

**Проверка стала строже, а не слабее.** Jinja рендерила СВОЮ копию документа, разошедшуюся
с официальным пакетом (разбор — `docs/reports/decisions/2026-09-04_legal_texts_single_
source.md`): оператор, срок хранения и адрес обращений отличались. Теперь те же требования
предъявляются к тому единственному тексту, который реально публикуется и из которого
печатаются `docx`.

Формулировки берутся из требований закона (152-ФЗ, 39-ФЗ), а не из вёрстки, поэтому
переезд ничего не потерял: проверялось содержание, оно и проверяется.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.config import settings

# Ключи реестра (`app/core/legal.py`), а не URL: адреса — дело фронта, содержание — нет.
PUBLIC_DOCUMENTS = [
    "privacy_policy",
    "terms_of_service",
    "cookie_policy",
    "personal_data",
    "financial_data",
    "marketing",
]


def _text(client: TestClient, slug: str) -> str:
    response = client.get(f"/api/legal/documents/{slug}")
    assert response.status_code == 200, f"{slug} -> {response.status_code}"
    return response.json()["content"]


@pytest.mark.parametrize("slug", PUBLIC_DOCUMENTS)
def test_document_is_published_and_not_empty(client: TestClient, slug: str) -> None:
    """Документ отдаётся и содержит текст.

    Пустой документ хуже отсутствующего: ссылка есть, требование формально закрыто,
    а человек ничего не прочитал.
    """
    assert len(_text(client, slug)) > 500, f"{slug}: подозрительно короткий текст"


def test_privacy_has_152fz_and_operator(client: TestClient) -> None:
    text = _text(client, "privacy_policy")
    assert "152-ФЗ" in text
    assert "персональных данных" in text.lower()
    # Оператор в тексте и в коде — один и тот же (гейт единого источника, v8.44.0).
    assert settings.LEGAL_OPERATOR_NAME in text


def test_terms_has_investment_disclaimer_39fz(client: TestClient) -> None:
    """Ключевой финтех-дисклеймер: сервис не инвестсоветник (39-ФЗ).

    Проверяется в оферте — там он и обязан быть как условие договора. Отдельно он же
    показывается на самом экране рекомендаций (L5, `DISCLAIMER_39FZ`): требование
    закона в том, чтобы человек видел его в момент решения, а не только в оферте.
    """
    text = _text(client, "terms_of_service")
    assert "39-ФЗ" in text
    assert "инвестиционной рекомендацией" in text


def test_consent_has_withdrawal(client: TestClient) -> None:
    """Право отозвать согласие названо в самом согласии — иначе оно не реализуемо."""
    assert "отзыв" in _text(client, "personal_data").lower()


def test_financial_consent_mentions_import_paths(client: TestClient) -> None:
    """Согласие на финданные называет ОБА пути их появления.

    Импорт выписки и ручной ввод — разные способы, и умолчать про любой значит собирать
    данные способом, на который человек не соглашался.
    """
    text = _text(client, "financial_data").lower()
    assert "выписк" in text
    assert "ручн" in text


def test_contact_email_reachable_in_documents(client: TestClient) -> None:
    """Адрес обращений напечатан в документах: по нему отзывают согласие и требуют
    удаления данных. Адреса, которого нет в тексте, для человека не существует."""
    assert settings.LEGAL_CONTACT_EMAIL in _text(client, "privacy_policy")


def test_registry_lists_documents_for_the_footer(client: TestClient) -> None:
    """Реестр отдаёт адреса — по ним футер (L7) строит ссылки на каждой странице.

    Раньше здесь проверялись сырые `href` в HTML; теперь ссылки строит React из этого
    ответа, и проверять надо источник, а не разметку одного шаблона.
    """
    documents = client.get("/api/legal/documents").json()["documents"]
    urls = {doc["url"] for doc in documents.values()}
    for required in ("/legal/privacy", "/legal/terms", "/legal/cookies"):
        assert required in urls, f"{required} нет в реестре — ссылка футера вела бы в пустоту"


def test_disclaimer_is_served_for_the_recommendation_screen(client: TestClient) -> None:
    """Дисклеймер 39-ФЗ приходит ПОЛЕМ ответа, а не перепечатывается фронтом (L5)."""
    body = client.get("/api/legal/documents").json()
    assert "39-ФЗ" in body["disclaimer_39fz"] or "инвестиционн" in body["disclaimer_39fz"]


# 🔴 `TestDraftBanner` снят вместе с Jinja-страницами.
#
# Баннер «документ в стадии оформления» показывался, пока `LEGAL_DETAILS_CONFIRMED` не
# выставлен и ИНН с адресом пусты. Он предупреждал о пустых полях ШАБЛОНА — механизме,
# которого в пакете `docs/legal/` нет по построению: пакет сознательно называет оператором
# «сервис FINPILOT» без реквизитов юрлица (решение этапа MVP, `docs/legal/README.md` §1).
#
# Показывать «в стадии оформления» поверх текста, объявленного окончательным, значило бы
# подрывать его же силу. Решение и два открытых вопроса владельцу (достаточно ли оператора
# без реквизитов для запуска в РФ; нужен ли баннер до проверки живым юристом) —
# `docs/reports/decisions/2026-09-04_legal_texts_single_source.md`.
#
# Флаг и поля в `app/config.py` оставлены: понадобятся, когда появится юрлицо. Если
# владелец решит вернуть баннер — он вернётся явным состоянием React-экрана, а не
# побочным эффектом пустого поля конфигурации, и тест заводится тогда же.
