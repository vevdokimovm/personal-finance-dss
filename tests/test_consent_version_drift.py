"""Согласие на устаревшую редакцию документа видно как устаревшее.

## Что закрывает

По 152-ФЗ согласие даётся на **конкретную редакцию** документа — это сказано и в самом
проекте (`app/api/routes_consents.py`). Но `has_consent` и `_active` искали запись
без `withdrawn_at` и **не сравнивали** `doc_version` с текущей, а `grant_consent`
при существующем активном согласии возвращал старую запись, не заводя новую.

🔴 **Следствие:** после публикации новой редакции политики обработка продолжалась
по согласию на прежнюю, интерфейс показывал «выдано, версия 1.0» рядом с действующей 1.1,
и никто ни о чём не спрашивал. Cookie-баннер в том же продукте ведёт себя правильно —
сравнивает сохранённую версию с текущей и спрашивает заново.

## Что здесь сделано, а что НЕТ

Состояние согласия теперь несёт `is_current` и `current_version` — расхождение видно
и API, и интерфейсу.

🔴 **Доступ при расхождении НЕ отзывается автоматически, и это осознанно.** Автоотзыв
запер бы человека вне его собственных финансовых данных в момент, когда компания
поменяла редакцию документа, — то есть наказал бы пользователя за действие компании.
Что показывать и когда требовать переподтверждения — продуктовое и юридическое решение
владельца; код обязан дать факт, а не выбрать за него.
"""
from __future__ import annotations

import pytest

from app.services.consent import consent_state, grant_consent


@pytest.fixture()
def user(client, db_session):
    """Зарегистрированный пользователь без записанных согласий.

    Регистрация пишет согласие сама (требование L1), поэтому для тестов сервиса
    записи чистятся — иначе проверки считали бы регистрационную.
    Та же фикстура, что в `test_consents.py`: она там локальная, а не в conftest.
    """
    from app.database.models import User, UserConsent

    client.post(
        "/api/auth/register",
        json={"email": "drift-user@example.com", "password": "verysecret1", "consent": True},
    )
    created = db_session.query(User).filter(User.email == "drift-user@example.com").one()
    db_session.query(UserConsent).filter(UserConsent.user_id == created.id).delete()
    db_session.commit()
    return created


class TestStateExposesVersionDrift:
    """Расхождение редакций видно в состоянии согласия."""

    def test_fresh_consent_is_current(self, db_session, user) -> None:
        grant_consent(db_session, user.id, "personal_data")
        state = consent_state(db_session, user.id)["personal_data"]
        assert state["granted"] is True
        assert state["is_current"] is True, "свежее согласие объявлено устаревшим"

    def test_state_reports_the_current_version_alongside_the_granted_one(
        self, db_session, user
    ) -> None:
        """🔴 Обе версии в ответе, иначе расхождение не с чем сравнить.

        Поле `version` показывает, на что человек соглашался; `current_version` —
        что действует сейчас. Одно без другого не отвечает на вопрос «надо ли
        спрашивать заново».
        """
        grant_consent(db_session, user.id, "personal_data")
        state = consent_state(db_session, user.id)["personal_data"]
        assert "current_version" in state
        assert state["current_version"], "текущая редакция не названа"

    def test_outdated_consent_is_marked_not_current(
        self, db_session, user, monkeypatch
    ) -> None:
        """Редакция документа уехала вперёд — согласие помечено устаревшим."""
        grant_consent(db_session, user.id, "personal_data")

        import app.services.consent as consent_module

        monkeypatch.setattr(
            consent_module, "current_version", lambda consent_type: "99.0", raising=True
        )
        state = consent_state(db_session, user.id)["personal_data"]
        assert state["granted"] is True, "согласие не должно исчезать само"
        assert state["is_current"] is False, (
            "согласие на прежнюю редакцию считается действующим для новой — "
            "обработка идёт по основанию, которого человек не давал"
        )

    def test_missing_consent_is_not_current_either(self, db_session, user) -> None:
        """Невыданное согласие не притворяется актуальным."""
        state = consent_state(db_session, user.id)["financial_data"]
        assert state["granted"] is False
        assert state["is_current"] is False
