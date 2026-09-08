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


class TestReconsentIsPossible:
    """🔴 Согласиться на НОВУЮ редакцию можно — иначе расхождение неустранимо.

    Прошлый батч научил систему ВИДЕТЬ, что человек соглашался на прежнюю редакцию
    (`is_current`), и на этом остановился. Выхода из этого состояния не было:
    `grant_consent` при существующем действующем согласии возвращал старую запись,
    **не сверяя `doc_version`**, то есть повторная выдача была no-op.

    🔴 **Для обязательного согласия это тупик без обходного пути.** `personal_data`
    входит в `UNWITHDRAWABLE`: отозвать и выдать заново нельзя, `withdraw_consent`
    отвечает 409. Значит поднятие версии политики обработки ПДн — самого частого
    к пересмотру документа — переводило бы **100 % пользователей** в состояние
    «согласие на устаревшую редакцию» без единого способа выйти, кроме удаления
    аккаунта.

    Механизм, заведённый чтобы заметить расхождение, обязан давать и способ его снять.
    """

    def test_granting_again_after_version_bump_records_the_new_edition(
        self, db_session, user, monkeypatch
    ) -> None:
        """Повторная выдача при новой редакции заводит НОВУЮ запись."""
        import app.services.consent as consent_module

        grant_consent(db_session, user.id, "personal_data")
        monkeypatch.setattr(
            consent_module, "current_version", lambda consent_type: "2.0", raising=True
        )

        grant_consent(db_session, user.id, "personal_data")
        state = consent_state(db_session, user.id)["personal_data"]
        assert state["version"] == "2.0", (
            "повторная выдача вернула прежнюю запись — согласиться на новую редакцию "
            "невозможно, а для personal_data ещё и нечем обойти: отзыв запрещён"
        )
        assert state["is_current"] is True

    def test_previous_record_is_kept_as_evidence(
        self, db_session, user, monkeypatch
    ) -> None:
        """🔴 Прежнее согласие не стирается: оно доказательство основания обработки.

        В период между двумя редакциями данные обрабатывались по прежнему согласию,
        и запись об этом обязана сохраниться.
        """
        import app.services.consent as consent_module
        from app.database.models import UserConsent

        grant_consent(db_session, user.id, "personal_data")
        monkeypatch.setattr(
            consent_module, "current_version", lambda consent_type: "2.0", raising=True
        )
        grant_consent(db_session, user.id, "personal_data")

        rows = (
            db_session.query(UserConsent)
            .filter(UserConsent.user_id == user.id,
                    UserConsent.consent_type == "personal_data")
            .all()
        )
        assert len(rows) == 2, "прежняя запись исчезла — потеряно доказательство основания"
        versions = sorted(r.doc_version for r in rows)
        assert versions == ["1.0", "2.0"]

    def test_granting_same_version_twice_is_idempotent(
        self, db_session, user
    ) -> None:
        """Та же редакция дважды — по-прежнему одна запись.

        Иначе каждый заход на экран согласий плодил бы строки, и «повторная выдача
        создаёт новую строку» перестало бы означать смену редакции.
        """
        from app.database.models import UserConsent

        grant_consent(db_session, user.id, "personal_data")
        grant_consent(db_session, user.id, "personal_data")
        rows = (
            db_session.query(UserConsent)
            .filter(UserConsent.user_id == user.id,
                    UserConsent.consent_type == "personal_data")
            .count()
        )
        assert rows == 1


class TestWithdrawalSurvivesReconsent:
    """🔴 Отзыв гасит ВСЕ действующие записи типа, а не только последнюю.

    Дефект, внесённый той же правкой, что разрешила переподтверждение редакции.
    После подтверждения новой редакции у типа становится ДВЕ записи без `withdrawn_at`.
    `withdraw_consent` брал `_active` — то есть новейшую — и гасил только её; прежняя
    оставалась действующей, `has_consent` продолжал отвечать `True`, и отзыв
    не срабатывал вовсе.

    Для отзываемых типов это прямое нарушение 152-ФЗ: право реализовано в интерфейсе,
    кнопка нажата, ответ успешный, обработка продолжается.

    Найдено при разборе собственной правки, до сдачи батча.
    """

    def test_withdrawal_after_reconsent_really_revokes(
        self, db_session, user, monkeypatch
    ) -> None:
        import app.services.consent as consent_module
        from app.services.consent import has_consent, withdraw_consent

        grant_consent(db_session, user.id, "marketing")
        monkeypatch.setattr(
            consent_module, "current_version", lambda consent_type: "2.0", raising=True
        )
        grant_consent(db_session, user.id, "marketing")

        assert withdraw_consent(db_session, user.id, "marketing") is True
        assert has_consent(db_session, user.id, "marketing") is False, (
            "после переподтверждения редакции отзыв погасил только новую запись — "
            "прежняя осталась действующей, и обработка продолжается"
        )

    def test_every_record_is_marked_withdrawn(
        self, db_session, user, monkeypatch
    ) -> None:
        """Ни одна запись не остаётся без отметки: иначе журнал согласий врёт."""
        import app.services.consent as consent_module
        from app.database.models import UserConsent
        from app.services.consent import withdraw_consent

        grant_consent(db_session, user.id, "marketing")
        monkeypatch.setattr(
            consent_module, "current_version", lambda consent_type: "2.0", raising=True
        )
        grant_consent(db_session, user.id, "marketing")
        withdraw_consent(db_session, user.id, "marketing")

        rows = (
            db_session.query(UserConsent)
            .filter(UserConsent.user_id == user.id,
                    UserConsent.consent_type == "marketing")
            .all()
        )
        assert len(rows) == 2
        assert all(r.withdrawn_at is not None for r in rows)

    def test_state_shows_not_granted_after_withdrawal(
        self, db_session, user, monkeypatch
    ) -> None:
        """И экран согласий показывает «не выдано», а не прежнюю редакцию."""
        import app.services.consent as consent_module
        from app.services.consent import withdraw_consent

        grant_consent(db_session, user.id, "marketing")
        monkeypatch.setattr(
            consent_module, "current_version", lambda consent_type: "2.0", raising=True
        )
        grant_consent(db_session, user.id, "marketing")
        withdraw_consent(db_session, user.id, "marketing")

        state = consent_state(db_session, user.id)["marketing"]
        assert state["granted"] is False


class TestActiveRecordChoiceIsDeterministic:
    """🔴 Действующей считается запись на ТЕКУЩУЮ редакцию, если она есть.

    После разрешения переподтверждения у типа бывает несколько действующих записей,
    и выбор «последняя по `granted_at`» завязан на отметку времени. Две выдачи в одну
    микросекунду (двойной клик, повтор запроса) дают неопределённый порядок — и если
    победит запись на прежнюю редакцию, `is_current` навсегда останется `false`,
    а кнопка «Подтвердить новую редакцию» будет плодить строки, ничего не меняя.

    Выбор по СМЫСЛУ («действует та, что на текущей редакции») от времени не зависит
    вовсе и потому не ломается ни при каком совпадении отметок.
    """

    def test_current_edition_wins_over_older_one(
        self, db_session, user, monkeypatch
    ) -> None:
        import app.services.consent as consent_module
        from app.database.models import UserConsent
        from app.services.consent import _active

        grant_consent(db_session, user.id, "marketing")
        monkeypatch.setattr(
            consent_module, "current_version", lambda consent_type: "2.0", raising=True
        )
        grant_consent(db_session, user.id, "marketing")

        # Отметки времени совпадают — порядок «по свежести» становится неопределённым.
        same_moment = db_session.query(UserConsent).first().granted_at
        for row in db_session.query(UserConsent).filter(
            UserConsent.user_id == user.id, UserConsent.consent_type == "marketing"
        ):
            row.granted_at = same_moment
        db_session.commit()

        assert _active(db_session, user.id, "marketing").doc_version == "2.0", (
            "при совпавших отметках победила запись на прежнюю редакцию — "
            "расхождение стало неустранимым"
        )

    def test_old_edition_still_counts_as_consent(
        self, db_session, user, monkeypatch
    ) -> None:
        """🔴 Согласие на прежнюю редакцию остаётся ДЕЙСТВУЮЩИМ.

        Доступ при расхождении не отзывается — это решение владельца: иначе смена
        редакции документа заперла бы человека вне его собственных данных.
        """
        import app.services.consent as consent_module
        from app.services.consent import has_consent

        grant_consent(db_session, user.id, "marketing")
        monkeypatch.setattr(
            consent_module, "current_version", lambda consent_type: "2.0", raising=True
        )

        assert has_consent(db_session, user.id, "marketing") is True


class TestScreenAndGatesAgreeOnWhichRecordIsActive:
    """🔴 Экран и гейты отвечают на «какая запись действует» ОДИНАКОВО.

    `_active` починили выбирать запись на текущую редакцию, а `active_consents` —
    источник для `consent_state`, то есть для API и экрана — остался с выбором
    «первая по `granted_at` убыв.». В одном модуле оказалось два разных ответа
    на один вопрос: гейты (`has_consent` → `_active`) и экран
    (`consent_state` → `active_consents`).

    🔴 **Тупик воскресал бы по-новому и в худшей форме:** экран показывает
    `is_current=false`, человек жмёт «Подтвердить новую редакцию», `grant_consent`
    спрашивает `_active`, видит запись на текущую редакцию и возвращает её как есть —
    новой строки нет, ответ 200, экран не меняется. Кнопка, которая всегда есть
    и никогда ничего не делает; для `personal_data` — без обходного пути.

    Найдено пятым проходом независимого аудита 08.09.2026: свойство детерминизма
    было доказано на приватном хелпере, а публичный путь его не наследовал.
    """

    def test_state_agrees_with_active_when_timestamps_collide(
        self, db_session, user, monkeypatch
    ) -> None:
        """Тот же сценарий совпавших отметок — но проверяется ПУБЛИЧНЫЙ путь."""
        import app.services.consent as consent_module
        from app.database.models import UserConsent
        from app.services.consent import _active

        grant_consent(db_session, user.id, "marketing")
        monkeypatch.setattr(
            consent_module, "current_version", lambda consent_type: "2.0", raising=True
        )
        grant_consent(db_session, user.id, "marketing")

        same_moment = db_session.query(UserConsent).first().granted_at
        for row in db_session.query(UserConsent).filter(
            UserConsent.user_id == user.id, UserConsent.consent_type == "marketing"
        ):
            row.granted_at = same_moment
        db_session.commit()

        state = consent_state(db_session, user.id)["marketing"]
        assert state["version"] == _active(db_session, user.id, "marketing").doc_version
        assert state["is_current"] is True, (
            "экран считает согласие устаревшим, хотя запись на текущую редакцию есть — "
            "кнопка подтверждения будет всегда на месте и никогда ничего не сделает"
        )

    def test_state_matches_active_for_every_type(self, db_session, user) -> None:
        """Опора: на обычных данных источники тоже не расходятся."""
        from app.services.consent import _active

        for consent_type in ("personal_data", "marketing"):
            grant_consent(db_session, user.id, consent_type)

        state = consent_state(db_session, user.id)
        for consent_type in ("personal_data", "marketing"):
            record = _active(db_session, user.id, consent_type)
            assert state[consent_type]["version"] == record.doc_version
