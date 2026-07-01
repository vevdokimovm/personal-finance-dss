"""In-app уведомления (P2.3) — лента в интерфейсе («колокольчик»).

Отличие от P2.5 (email-рассылка + NotificationLog как дедуп-журнал ОТПРАВЛЕННЫХ
писем): здесь — сами уведомления, которые пользователь видит в приложении. Модель
Notification хранит title/body/type/link/is_read/created_at и читается лентой.

Контракт этих тестов:
1. Новый пользователь — пустая лента, ноль непрочитанных.
2. Лента отдаёт уведомления пользователя (новые сверху) + счётчик непрочитанных.
3. Отметка «прочитано» (одного / всех) уменьшает счётчик; фильтр unread_only работает.
4. Изоляция по пользователю: чужие уведомления не видны и не отмечаются (404).
5. Лента требует аутентификации.
6. Хук: когда email-рассылка реально шлёт письмо — рядом создаётся in-app уведомление
   (чтобы то же событие было видно и в колокольчике, не только письмом).

Лента/отметки идут через публичный API (TestClient, Bearer-токен — он приоритетнее
cookie, удобно держать несколько пользователей). Сами уведомления создаются системой,
поэтому в setup мы пишем их напрямую через CRUD (своя сессия SessionLocal), как и
проверки на уровне БД.
"""
from __future__ import annotations

from datetime import timedelta

from app.database import crud
from app.database.db import SessionLocal
from app.database.models import Notification, User
from app.utils.time import utcnow


# ─────────────────────────── helpers ───────────────────────────

def _register(client, email: str) -> str:
    r = client.post(
        "/api/auth/register",
        json={"email": email, "password": "password123", "consent": True},
    )
    assert r.status_code == 201, r.text
    return r.json()["access_token"]


def _h(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _user_id(email: str) -> str:
    db = SessionLocal()
    try:
        u = db.query(User).filter(User.email == email).first()
        assert u is not None
        return u.id
    finally:
        db.close()


def _make_notification(user_id: str, title: str = "Цель близко", ntype: str = "goal_deadline",
                       body: str = "До дедлайна 3 дня", link: str | None = "/goals") -> int:
    """Создать in-app уведомление напрямую (имитируем системную генерацию)."""
    db = SessionLocal()
    try:
        n = crud.create_notification(db, user_id=user_id, type=ntype,
                                     title=title, body=body, link=link)
        db.commit()
        return n.id
    finally:
        db.close()


# ─────────────────────────── лента ───────────────────────────

class TestFeed:
    def test_empty_for_new_user(self, client) -> None:
        token = _register(client, "feed_empty@test.io")
        r = client.get("/api/notifications/feed", headers=_h(token))
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["unread_count"] == 0
        assert data["items"] == []

    def test_shows_created(self, client) -> None:
        token = _register(client, "feed_show@test.io")
        uid = _user_id("feed_show@test.io")
        _make_notification(uid, title="Первое")
        _make_notification(uid, title="Второе")

        r = client.get("/api/notifications/feed", headers=_h(token))
        assert r.status_code == 200, r.text
        data = r.json()
        assert len(data["items"]) == 2
        assert data["unread_count"] == 2
        titles = {item["title"] for item in data["items"]}
        assert titles == {"Первое", "Второе"}

    def test_newest_first(self, client) -> None:
        token = _register(client, "feed_order@test.io")
        uid = _user_id("feed_order@test.io")
        # Явно разнесём created_at, чтобы порядок был детерминированным.
        db = SessionLocal()
        try:
            old = Notification(user_id=uid, type="system", title="Старое", body="x",
                               created_at=utcnow() - timedelta(hours=2))
            new = Notification(user_id=uid, type="system", title="Новое", body="y",
                               created_at=utcnow())
            db.add_all([old, new])
            db.commit()
        finally:
            db.close()

        r = client.get("/api/notifications/feed", headers=_h(token))
        items = r.json()["items"]
        assert items[0]["title"] == "Новое"
        assert items[1]["title"] == "Старое"

    def test_requires_auth(self, client) -> None:
        r = client.get("/api/notifications/feed")
        assert r.status_code == 401

    def test_isolation_between_users(self, client) -> None:
        token_a = _register(client, "feed_a@test.io")
        _register(client, "feed_b@test.io")
        uid_a = _user_id("feed_a@test.io")
        _make_notification(uid_a, title="Только для A")

        # B не видит уведомления A.
        token_b_fresh = _register(client, "feed_b2@test.io")
        r = client.get("/api/notifications/feed", headers=_h(token_b_fresh))
        assert r.json()["items"] == []
        assert r.json()["unread_count"] == 0

        # A видит своё.
        r2 = client.get("/api/notifications/feed", headers=_h(token_a))
        assert len(r2.json()["items"]) == 1


class TestUnreadCount:
    def test_count_endpoint(self, client) -> None:
        token = _register(client, "count@test.io")
        uid = _user_id("count@test.io")
        for i in range(3):
            _make_notification(uid, title=f"N{i}")
        r = client.get("/api/notifications/unread-count", headers=_h(token))
        assert r.status_code == 200, r.text
        assert r.json()["unread_count"] == 3

    def test_unread_only_filter(self, client) -> None:
        token = _register(client, "filter@test.io")
        uid = _user_id("filter@test.io")
        first = _make_notification(uid, title="Прочту")
        _make_notification(uid, title="Оставлю")

        client.post(f"/api/notifications/{first}/read", headers=_h(token))

        r_all = client.get("/api/notifications/feed", headers=_h(token))
        assert len(r_all.json()["items"]) == 2

        r_unread = client.get("/api/notifications/feed?unread_only=true", headers=_h(token))
        items = r_unread.json()["items"]
        assert len(items) == 1
        assert items[0]["title"] == "Оставлю"


class TestMarkRead:
    def test_mark_one(self, client) -> None:
        token = _register(client, "mark1@test.io")
        uid = _user_id("mark1@test.io")
        nid = _make_notification(uid, title="Отметить")
        _make_notification(uid, title="Не трогать")

        r = client.post(f"/api/notifications/{nid}/read", headers=_h(token))
        assert r.status_code == 200, r.text

        cnt = client.get("/api/notifications/unread-count",
                         headers=_h(token)).json()["unread_count"]
        assert cnt == 1

        # is_read отражается в ленте.
        feed = client.get("/api/notifications/feed", headers=_h(token)).json()
        by_title = {i["title"]: i["is_read"] for i in feed["items"]}
        assert by_title["Отметить"] is True
        assert by_title["Не трогать"] is False

    def test_mark_all(self, client) -> None:
        token = _register(client, "markall@test.io")
        uid = _user_id("markall@test.io")
        for i in range(3):
            _make_notification(uid, title=f"M{i}")

        r = client.post("/api/notifications/read-all", headers=_h(token))
        assert r.status_code == 200, r.text
        assert r.json()["marked"] == 3

        cnt = client.get("/api/notifications/unread-count",
                         headers=_h(token)).json()["unread_count"]
        assert cnt == 0

    def test_mark_nonexistent_404(self, client) -> None:
        token = _register(client, "mark404@test.io")
        r = client.post("/api/notifications/999999/read", headers=_h(token))
        assert r.status_code == 404

    def test_mark_others_notification_404(self, client) -> None:
        _register(client, "owner@test.io")
        uid_owner = _user_id("owner@test.io")
        nid = _make_notification(uid_owner, title="Чужое")

        token_other = _register(client, "intruder@test.io")
        r = client.post(f"/api/notifications/{nid}/read", headers=_h(token_other))
        assert r.status_code == 404  # не виден → как будто не существует

        # И у владельца оно по-прежнему непрочитано.
        db = SessionLocal()
        try:
            n = db.query(Notification).filter(Notification.id == nid).first()
            assert n.is_read is False
        finally:
            db.close()

    def test_mark_read_requires_auth(self, client) -> None:
        r = client.post("/api/notifications/1/read")
        assert r.status_code == 401


# ─────────────────────────── хук в email-рассылку ───────────────────────────

class TestEmailHookCreatesInApp:
    """Когда рассылка реально отправляет письмо — то же событие должно появиться
    in-app (в колокольчике). Иначе пользователь без открытой почты пропустит его."""

    def _user(self, db, email="hook@test.io"):
        return crud.create_user(db, email=email, password_hash="hashed")

    def test_goal_deadline_creates_inapp(self, db_session) -> None:
        from app.services.notifications import run_user_notifications

        db = db_session
        user = self._user(db, email="hook_goal@test.io")
        crud.create_goal(
            db, name="Отпуск", target_amount=100000, current_amount=10000,
            deadline=utcnow() + timedelta(days=4), user_id=user.id,
        )

        sent = run_user_notifications(db, user)
        assert sent["goal_deadline"] == 1

        # In-app уведомление того же типа создано для пользователя.
        notes = crud.get_notifications(db, user_id=user.id)
        assert any(n.type == "goal_deadline" for n in notes)

    def test_inapp_deduped_like_email(self, db_session) -> None:
        """Повторный прогон в том же месяце не плодит дубль in-app (та же дедупликация)."""
        from app.services.notifications import run_user_notifications

        db = db_session
        user = self._user(db, email="hook_dedup@test.io")
        crud.create_goal(
            db, name="Подушка", target_amount=50000, current_amount=5000,
            deadline=utcnow() + timedelta(days=3), user_id=user.id,
        )

        run_user_notifications(db, user)
        run_user_notifications(db, user)  # второй прогон — дедуп

        notes = crud.get_notifications(db, user_id=user.id)
        goal_notes = [n for n in notes if n.type == "goal_deadline"]
        assert len(goal_notes) == 1
