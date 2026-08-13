"""Тесты подсистемы согласий (юрблок L1-L4, L9, L10).

Почему подсистема существует. Юридический пакет обещает пользователю три
РАЗДЕЛЬНЫХ согласия, каждое с датой, временем и редакцией текста, на которую он
согласился. До этой версии в модели было одно поле `consent_at` и один булев
флаг: при споре невозможно показать, на что именно и в какой редакции человек
согласился, а обязательное согласие на обработку ПДн было склеено с
необязательной рекламной рассылкой — конструкция, которую надзор читает как
навязанное согласие.

Что проверяется здесь:
  * три независимых типа согласия, каждое со своей версией текста и моментом;
  * отзыв не стирает историю, а закрывает запись `withdrawn_at` (доказательство
    должно переживать отзыв, иначе нечем подтвердить период обработки);
  * повторная выдача после отзыва создаёт НОВУЮ запись, а не воскрешает старую;
  * согласие на обработку ПДн нельзя отозвать, не удалив аккаунт: отзыв
    основания обработки при сохранении данных — это и есть нарушение;
  * регистрация требует ЯВНОГО согласия (никаких `default=True` — это
    предотмеченная галочка на уровне контракта API);
  * удаление аккаунта уносит и согласия (152-ФЗ, право на удаление);
  * в логах нет e-mail и денежных сумм.
"""
from __future__ import annotations

import json
import logging
import pytest

from app.core.legal import (
    CONSENT_MARKETING,
    CONSENT_PERSONAL_DATA,
    CONSENT_TYPES,
    LEGAL_DOCUMENTS,
    REQUIRED_AT_REGISTRATION,
    current_version,
)
from app.database.crud import delete_user
from app.database.models import UserConsent
from app.logging_config import JsonFormatter, scrub
from app.services.consent import (
    ConsentWithdrawalNotAllowed,
    active_consents,
    grant_consent,
    has_consent,
    withdraw_consent,
)


class TestLegalRegistry:
    def test_three_consent_types_exist(self):
        assert set(CONSENT_TYPES) == {"personal_data", "financial_data", "marketing"}

    def test_only_personal_data_is_required_at_registration(self):
        assert REQUIRED_AT_REGISTRATION == (CONSENT_PERSONAL_DATA,)

    def test_every_consent_type_has_a_versioned_document(self):
        for consent_type in CONSENT_TYPES:
            assert consent_type in LEGAL_DOCUMENTS
            assert current_version(consent_type)

    def test_documents_declare_effective_date(self):
        for doc in LEGAL_DOCUMENTS.values():
            assert doc["effective_from"]


class TestConsentService:
    def test_grant_records_version_and_moment(self, db_session, user):
        record = grant_consent(db_session, user.id, CONSENT_PERSONAL_DATA)
        assert record.consent_type == CONSENT_PERSONAL_DATA
        assert record.doc_version == current_version(CONSENT_PERSONAL_DATA)
        assert record.granted_at is not None
        assert record.withdrawn_at is None

    def test_types_are_independent(self, db_session, user):
        grant_consent(db_session, user.id, CONSENT_PERSONAL_DATA)
        assert has_consent(db_session, user.id, CONSENT_PERSONAL_DATA)
        assert not has_consent(db_session, user.id, CONSENT_MARKETING)

    def test_withdraw_keeps_the_record_as_evidence(self, db_session, user):
        grant_consent(db_session, user.id, CONSENT_MARKETING)
        withdraw_consent(db_session, user.id, CONSENT_MARKETING)
        rows = db_session.query(UserConsent).filter(
            UserConsent.user_id == user.id,
            UserConsent.consent_type == CONSENT_MARKETING).all()
        assert len(rows) == 1
        assert rows[0].withdrawn_at is not None
        assert not has_consent(db_session, user.id, CONSENT_MARKETING)

    def test_regrant_creates_new_row_not_resurrect(self, db_session, user):
        grant_consent(db_session, user.id, CONSENT_MARKETING)
        withdraw_consent(db_session, user.id, CONSENT_MARKETING)
        grant_consent(db_session, user.id, CONSENT_MARKETING)
        rows = db_session.query(UserConsent).filter(
            UserConsent.user_id == user.id,
            UserConsent.consent_type == CONSENT_MARKETING).all()
        assert len(rows) == 2
        assert has_consent(db_session, user.id, CONSENT_MARKETING)

    def test_personal_data_cannot_be_withdrawn_without_deleting_account(
            self, db_session, user):
        grant_consent(db_session, user.id, CONSENT_PERSONAL_DATA)
        with pytest.raises(ConsentWithdrawalNotAllowed):
            withdraw_consent(db_session, user.id, CONSENT_PERSONAL_DATA)

    def test_unknown_type_is_rejected(self, db_session, user):
        with pytest.raises(ValueError):
            grant_consent(db_session, user.id, "sell_my_soul")

    def test_active_consents_reports_state_per_type(self, db_session, user):
        grant_consent(db_session, user.id, CONSENT_PERSONAL_DATA)
        state = active_consents(db_session, user.id)
        assert state[CONSENT_PERSONAL_DATA].withdrawn_at is None
        assert CONSENT_MARKETING not in state

    def test_source_is_stored_when_provided(self, db_session, user):
        record = grant_consent(db_session, user.id, CONSENT_PERSONAL_DATA,
                               source_ip="203.0.113.9", user_agent="pytest/1.0")
        assert record.source_ip == "203.0.113.9"
        assert record.user_agent == "pytest/1.0"


class TestRegistrationContract:
    def test_consent_has_no_default_true(self):
        """Предотмеченная галочка на уровне контракта — это нарушение L2."""
        from app.schemas.auth import RegisterRequest

        field = RegisterRequest.model_fields["consent"]
        assert field.is_required(), "согласие обязано быть явным, без default"

    def test_registration_without_consent_is_rejected(self, client):
        response = client.post("/api/auth/register", json={
            "email": "no-consent@example.com", "password": "verysecret1",
            "consent": False})
        assert response.status_code in (400, 422)

    def test_registration_writes_personal_data_consent(self, client, db_session):
        response = client.post("/api/auth/register", json={
            "email": "consent-ok@example.com", "password": "verysecret1",
            "consent": True})
        assert response.status_code in (200, 201)
        rows = db_session.query(UserConsent).filter(
            UserConsent.consent_type == CONSENT_PERSONAL_DATA).all()
        assert any(r.doc_version == current_version(CONSENT_PERSONAL_DATA)
                   for r in rows)

    def test_marketing_opt_in_is_recorded_separately(self, client, db_session):
        client.post("/api/auth/register", json={
            "email": "marketing@example.com", "password": "verysecret1",
            "consent": True, "newsletter_opt_in": True})
        rows = db_session.query(UserConsent).filter(
            UserConsent.consent_type == CONSENT_MARKETING).all()
        assert rows, "рассылка обязана попасть отдельной записью"

    def test_marketing_is_not_granted_by_default(self, client, db_session):
        client.post("/api/auth/register", json={
            "email": "no-marketing@example.com", "password": "verysecret1",
            "consent": True})
        rows = db_session.query(UserConsent).filter(
            UserConsent.consent_type == CONSENT_MARKETING).all()
        assert not rows


class TestConsentApi:
    def test_state_endpoint_lists_all_types(self, client, auth_headers):
        response = client.get("/api/consents", headers=auth_headers)
        assert response.status_code == 200
        body = response.json()
        assert set(body["consents"]) == set(CONSENT_TYPES)

    def test_grant_and_withdraw_financial_consent(self, client, auth_headers):
        granted = client.post("/api/consents/financial_data",
                              headers=auth_headers)
        assert granted.status_code == 200
        assert granted.json()["granted"] is True

        withdrawn = client.delete("/api/consents/financial_data",
                                  headers=auth_headers)
        assert withdrawn.status_code == 204

        state = client.get("/api/consents", headers=auth_headers).json()
        assert state["consents"]["financial_data"]["granted"] is False

    def test_withdrawing_personal_data_is_conflict(self, client, auth_headers):
        response = client.delete("/api/consents/personal_data",
                                 headers=auth_headers)
        assert response.status_code == 409
        assert "account" in response.json()["detail"].lower() or \
               "аккаунт" in response.json()["detail"].lower()

    def test_unknown_type_is_404(self, client, auth_headers):
        assert client.post("/api/consents/whatever",
                           headers=auth_headers).status_code == 404

    def test_documents_endpoint_is_public_and_versioned(self, client):
        response = client.get("/api/legal/documents")
        assert response.status_code == 200
        docs = response.json()["documents"]
        assert docs
        for doc in docs.values():
            assert doc["version"] and doc["effective_from"]

    def test_state_requires_authentication(self, client):
        assert client.get("/api/consents").status_code in (401, 403)


class TestDeletionAndLogs:
    def test_account_deletion_removes_consents(self, db_session, user):
        grant_consent(db_session, user.id, CONSENT_PERSONAL_DATA)
        delete_user(db_session, user_id=user.id)
        rows = db_session.query(UserConsent).filter(
            UserConsent.user_id == user.id).all()
        assert rows == []

    def test_scrub_masks_email(self):
        assert "ivan@example.com" not in scrub("письмо ivan@example.com ушло")

    def test_scrub_masks_amounts(self):
        assert "147500.55" not in scrub("списано 147500.55 ₽")

    def test_formatter_scrubs_message(self):
        record = logging.LogRecord("t", logging.INFO, __file__, 1,
                                   "user a@b.com paid 99999.00", None, None)
        payload = json.loads(JsonFormatter().format(record))
        assert "a@b.com" not in payload["message"]

    def test_scrub_keeps_short_numbers(self):
        """Идентификаторы, коды и статусы маскировать не нужно."""
        assert "404" in scrub("status 404")


@pytest.fixture()
def user(client, db_session):
    """Зарегистрированный пользователь без единого записанного согласия.

    Регистрация пишет согласие сама (это и есть требование L1), поэтому для
    тестов сервиса записи чистятся: иначе проверка «повторная выдача создаёт
    новую строку» считала бы регистрационную.
    """
    from app.database.models import User, UserConsent

    client.post("/api/auth/register", json={
        "email": "fixture-user@example.com", "password": "verysecret1",
        "consent": True})
    created = db_session.query(User).filter(
        User.email == "fixture-user@example.com").one()
    db_session.query(UserConsent).filter(
        UserConsent.user_id == created.id).delete()
    db_session.commit()
    return created


@pytest.fixture()
def auth_headers(client):
    response = client.post("/api/auth/register", json={
        "email": "fixture-auth@example.com", "password": "verysecret1",
        "consent": True})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}
