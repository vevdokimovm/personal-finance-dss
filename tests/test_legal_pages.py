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


class TestDisclaimerTravelsWithTheAdvice:
    """L5: предупреждение обязано быть на экране решения, а не рядом с ним.

    Раньше текст жил только в `/api/legal/documents`. Формально он был доступен
    программно — фактически его наличие на экране рекомендаций зависело от того,
    вспомнит ли фронт сходить за ним отдельным вызовом. Теперь он приезжает
    вместе с самой рекомендацией, и забыть его нельзя.
    """

    def test_response_model_carries_disclaimer_by_default(self):
        from app.core.legal import DISCLAIMER_39FZ
        from app.schemas.recommendation import RecommendationResponse

        fields = RecommendationResponse.model_fields
        assert "disclaimer" in fields
        assert fields["disclaimer"].default == DISCLAIMER_39FZ


class TestRequiredConsentsAreEnforcedNotDocumented:
    """Константа обязана исполняться, а не описывать намерение.

    `REQUIRED_AT_REGISTRATION` до этого только утверждалась в тесте: добавление
    второго обязательного согласия в реестр не изменило бы поведение кода.
    """

    def test_registration_grants_every_required_consent(self, client, db_session):
        from app.core.legal import REQUIRED_AT_REGISTRATION
        from app.database.models import User, UserConsent

        client.post("/api/auth/register", json={
            "email": "req@fp.io", "password": "strongpass1", "consent": True})
        user = db_session.query(User).filter_by(email="req@fp.io").one()
        granted = {
            row.consent_type
            for row in db_session.query(UserConsent).filter_by(user_id=user.id)
        }
        assert set(REQUIRED_AT_REGISTRATION) <= granted

    def test_source_of_truth_is_iterated_not_hardcoded(self):
        source = (
            __import__("pathlib").Path("app/api/routes_auth.py")
            .read_text(encoding="utf-8")
        )
        assert "for _required in REQUIRED_AT_REGISTRATION" in source
