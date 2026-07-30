"""Юридические документы: объявленный URL обязан открываться.

Причина существования файла. Реестр `LEGAL_DOCUMENTS` объявлял шесть адресов,
и **ни один из них не соответствовал реальному маршруту**: заявлено
`/legal/consent-personal-data`, `/privacy`, `/cookies`, а приложение отдаёт
`/legal/consent`, `/legal/privacy`, `/legal/cookies`. На эти же адреса ссылается
машиночитаемый отказ гейта согласий — то есть фронт получал ссылку в никуда
вместе с требованием дать согласие.

Тест закрывает класс целиком: любой документ, добавленный в реестр без
работающего маршрута, роняет прогон.
"""
from __future__ import annotations

import pytest

from app.core.legal import LEGAL_DOCUMENTS

DOCUMENT_IDS = sorted(LEGAL_DOCUMENTS)


@pytest.mark.parametrize("doc_id", DOCUMENT_IDS)
def test_declared_url_opens(client, doc_id):
    url = LEGAL_DOCUMENTS[doc_id]["url"]
    assert client.get(url).status_code == 200, f"{doc_id} → {url}"


@pytest.mark.parametrize("doc_id", DOCUMENT_IDS)
def test_document_declares_version_and_effective_date(doc_id):
    document = LEGAL_DOCUMENTS[doc_id]
    assert document["version"]
    assert document["effective_from"]
    assert document["title"]


@pytest.mark.parametrize("doc_id", DOCUMENT_IDS)
def test_source_file_exists_in_repository(doc_id):
    from pathlib import Path
    repo = Path(__file__).resolve().parents[1]
    assert (repo / LEGAL_DOCUMENTS[doc_id]["path"]).exists()


def test_registry_endpoint_lists_every_document(client):
    payload = client.get("/api/legal/documents").json()
    listed = payload.get("documents", payload)
    assert len(listed) == len(LEGAL_DOCUMENTS)


def test_registry_endpoint_carries_the_disclaimer(client):
    """Дисклеймер 39-ФЗ обязан быть доступен фронту программно.

    Иначе его наличие на экране рекомендаций зависит от того, вспомнит ли
    верстальщик про требование оферты.
    """
    payload = client.get("/api/legal/documents").json()
    text = payload["disclaimer_39fz"]
    # Проверяется термин из 39-ФЗ, а не номер закона: юридически значима
    # именно формулировка «индивидуальная инвестиционная рекомендация»,
    # называть закон по номеру на экране не требуется.
    assert "индивидуальной инвестиционной рекомендацией" in text
    assert "инвестиционным советником" in text
