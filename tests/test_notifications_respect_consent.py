"""Рассылка не шлёт финансовые суммы тому, кто согласия не давал или отозвал его.

## Как обнаружилось

Девятый проход независимого аудита, гипотеза H1. Гейт `require_financial_consent`
стоит на ЧТЕНИИ ленты (`GET /notifications/feed`, `/unread-count`), и обоснование
в `routes_notifications.py` названо дословно:

    «Уведомления несут суммы… кладёт в тело строку вида „Сводка за {месяц}: доход …,
    расход …, чистыми …", **та же сводка уходит письмом и в Telegram**. Значит лента
    отдаёт финансовый портрет и обязана требовать согласия».

Гейт до письма и Telegram не дошёл. `run_all_notifications` берёт
`db.query(User).filter(User.email.isnot(None)).all()` и не спрашивает `has_consent`
ни разу — во всём `app/` эта функция вызывается только из `_consent_guard.py`.

🔴 **Почему это не формальность.** `financial_data` НЕ входит в `REQUIRED_AT_REGISTRATION`
(там только `personal_data`) и отзываемо через интерфейс. Значит человек, который согласия
не давал или **отозвал** его, продолжает получать письмом и в Telegram свой доход, расход
и чистый поток, а `create_notification` копит те же суммы в БД.

Тот же класс, что весь цикл аудита ловит раз за разом: **периметр описан прозой, а не кодом**.
Здесь проза сама называет письмо и Telegram — и всё равно осталась прозой.
"""
from __future__ import annotations

from datetime import timedelta

import pytest

from app.core.legal import CONSENT_FINANCIAL_DATA
from app.database.crud import create_goal, create_user
from app.services.consent import grant_consent, withdraw_consent
from app.services.notifications import (
    goals_near_deadline,
    run_all_notifications,
    run_user_notifications,
)
from app.utils.time import utcnow


def _seed_reason_to_notify(db_session, user):
    """Условие, при котором рассылка ОБЯЗАНА сработать: цель с дедлайном через три дня.

    🔴 Без этого тест зелен по чужой причине — у пустого пользователя рассылать нечего,
    и проверка «ничего не отправлено» выполняется сама собой, что бы ни делал код.
    Ровно та ошибка, которую цикл аудита ловил в этой же сессии на атрибуции событий.
    """
    goal = create_goal(
        db_session,
        name="Резерв",
        target_amount=100000.0,
        current_amount=10000.0,
        deadline=utcnow() + timedelta(days=3),
        user_id=user.id,
    )
    assert goals_near_deadline(db_session, user.id), (
        "фикстура не создала повода для уведомления — тест проверял бы пустоту"
    )
    return goal


@pytest.fixture
def user_without_consent(db_session):
    user = create_user(db_session, email="no-consent@example.com", password_hash="x")
    _seed_reason_to_notify(db_session, user)
    return user


@pytest.fixture
def user_with_consent(db_session):
    user = create_user(db_session, email="with-consent@example.com", password_hash="x")
    grant_consent(db_session, user.id, CONSENT_FINANCIAL_DATA)
    _seed_reason_to_notify(db_session, user)
    return user


def test_fixture_really_triggers_notifications(db_session, user_with_consent, monkeypatch):
    """Контроль живости: с согласия и с поводом рассылка ДОЛЖНА сработать.

    🔴 Этот тест — не проверка продукта, а проверка трёх остальных. Если он краснеет,
    остальные зелены впустую: они утверждают «ничего не отправлено» там, где отправлять
    нечего вовсе.
    """
    monkeypatch.setattr(
        "app.services.notifications.email_service.send_goal_deadline_reminder",
        lambda *a, **kw: True,
    )
    result = run_user_notifications(db_session, user_with_consent)
    assert result["goal_deadline"] == 1, (
        f"повод есть и согласие есть, а уведомление не ушло: {result}"
    )


def _sent_anything(counters: dict) -> bool:
    return any(counters.get(k, 0) for k in ("goal_deadline", "budget_overrun", "digest"))


def test_no_consent_no_notifications(db_session, user_without_consent, monkeypatch):
    """🔴 Без согласия на финданные рассылка молчит целиком.

    Мутация: снять проверку согласия в `run_user_notifications` — тест краснеет.
    """
    calls: list[str] = []
    monkeypatch.setattr(
        "app.services.notifications.email_service.send_goal_deadline_reminder",
        lambda *a, **kw: calls.append("goal_deadline") or True,
    )
    result = run_user_notifications(db_session, user_without_consent)
    assert not _sent_anything(result), (
        "рассылка отправила уведомление человеку без согласия на финансовые данные — "
        f"суммы ушли письмом и в Telegram в обход гейта: {result}"
    )
    assert calls == [], "письмо ушло, хотя согласия нет"


def test_withdrawn_consent_stops_notifications(db_session, user_with_consent, monkeypatch):
    """🔴 Отзыв согласия останавливает рассылку — не только чтение ленты.

    Отзыв, который гасит экран и не гасит письмо, — это отзыв на бумаге:
    человек нажал «отозвать», а суммы продолжают приходить ему на почту.
    """
    monkeypatch.setattr(
        "app.services.notifications.email_service.send_goal_deadline_reminder",
        lambda *a, **kw: True,
    )
    withdraw_consent(db_session, user_with_consent.id, CONSENT_FINANCIAL_DATA)
    result = run_user_notifications(db_session, user_with_consent)
    assert not _sent_anything(result), (
        "согласие отозвано, а рассылка продолжает слать финансовые суммы"
    )


def test_orchestrator_skips_users_without_consent(db_session, user_without_consent, monkeypatch):
    """Оркестратор cron учитывает согласие так же, как индивидуальный проход.

    Проверка отдельная от предыдущих намеренно: `run_all_notifications` мог бы
    обходить `run_user_notifications` собственным циклом — тогда фикс в одном месте
    не закрыл бы второе.
    """
    monkeypatch.setattr(
        "app.services.notifications.email_service.send_goal_deadline_reminder",
        lambda *a, **kw: True,
    )
    totals = run_all_notifications(db_session)
    assert not _sent_anything(totals), (
        f"cron-оркестратор разослал суммы без согласия: {totals}"
    )
