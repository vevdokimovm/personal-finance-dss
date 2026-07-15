"""Реферальные награды / каркас геймификации (P3.4, MVP).

Базовый /referral/me (P3.2) отдавал код + счётчик. Этот батч добавляет каркас под
будущую страницу рефералки на фронте (веха 6):

1. invite_url — готовая ссылка-приглашение с реферальным кодом (для «поделиться»).
2. milestones — вехи-достижения по числу приглашений (1, 3, 5, 10, 25): какие достигнуты,
   какая следующая и сколько до неё. Детерминированы из счётчика приглашений — без новых
   таблиц. Поле reward зарезервировано под реальные награды (привяжем при монетизации) —
   сейчас каркас, без выдуманной механики начисления (YAGNI).

Чистая функция milestones тестируется изолированно; интеграция — через /referral/me.
"""
from __future__ import annotations

from app.database import crud
from app.services.referral import (
    REFERRAL_THRESHOLDS,
    next_milestone,
    referral_milestones,
)


# ─────────────────────── чистая логика milestones ───────────────────────

class TestMilestones:
    def test_zero_invites_none_reached(self) -> None:
        ms = referral_milestones(0)
        assert len(ms) == len(REFERRAL_THRESHOLDS)
        assert all(m["reached"] is False for m in ms)

    def test_thresholds_below_count_reached(self) -> None:
        ms = referral_milestones(3)
        by_threshold = {m["threshold"]: m["reached"] for m in ms}
        assert by_threshold[1] is True
        assert by_threshold[3] is True
        assert by_threshold[5] is False

    def test_all_reached_at_max(self) -> None:
        ms = referral_milestones(max(REFERRAL_THRESHOLDS) + 100)
        assert all(m["reached"] is True for m in ms)

    def test_each_milestone_has_shape(self) -> None:
        for m in referral_milestones(2):
            assert set(m.keys()) == {"threshold", "title", "reward", "reached"}
            assert isinstance(m["threshold"], int)
            assert isinstance(m["title"], str) and m["title"]


class TestNextMilestone:
    def test_next_from_zero_is_first_threshold(self) -> None:
        nxt = next_milestone(0)
        assert nxt is not None
        assert nxt["threshold"] == REFERRAL_THRESHOLDS[0]
        assert nxt["remaining"] == REFERRAL_THRESHOLDS[0]

    def test_next_remaining_counts_down(self) -> None:
        # При 3 приглашениях следующая веха — 5, осталось 2.
        nxt = next_milestone(3)
        assert nxt["threshold"] == 5
        assert nxt["remaining"] == 2

    def test_next_none_when_all_reached(self) -> None:
        assert next_milestone(max(REFERRAL_THRESHOLDS)) is None


# ─────────────────────── интеграция через /referral/me ───────────────────────

class TestReferralMeEndpoint:
    def _register(self, client, email: str) -> tuple[str, str]:
        r = client.post("/api/auth/register",
                        json={"email": email, "password": "password123", "consent": True})
        assert r.status_code == 201, r.text
        return r.json()["access_token"], email

    def test_me_returns_invite_url_with_code(self, client) -> None:
        token, _ = self._register(client, "rw_url@test.io")
        r = client.get("/api/referral/me", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200, r.text
        data = r.json()
        code = data["referral_code"]
        assert "invite_url" in data
        assert code in data["invite_url"]
        assert "ref=" in data["invite_url"]

    def test_me_returns_milestones_and_next(self, client) -> None:
        token, _ = self._register(client, "rw_ms@test.io")
        r = client.get("/api/referral/me", headers={"Authorization": f"Bearer {token}"})
        data = r.json()
        assert "milestones" in data
        assert len(data["milestones"]) == len(REFERRAL_THRESHOLDS)
        # Новый пользователь без приглашений: ничего не достигнуто, next — первая веха.
        assert all(m["reached"] is False for m in data["milestones"])
        assert data["next_milestone"]["threshold"] == REFERRAL_THRESHOLDS[0]

    def test_me_milestones_reflect_invites(self, client) -> None:
        # Пригласивший + один пришедший по его коду → invited_count = 1, первая веха достигнута.
        token, _ = self._register(client, "rw_inviter@test.io")
        me = client.get("/api/referral/me", headers={"Authorization": f"Bearer {token}"}).json()
        code = me["referral_code"]

        r2 = client.post("/api/auth/register",
                         json={"email": "rw_invited@test.io", "password": "password123",
                               "consent": True, "referral_code": code})
        assert r2.status_code == 201, r2.text

        me2 = client.get("/api/referral/me", headers={"Authorization": f"Bearer {token}"}).json()
        assert me2["invited_count"] == 1
        by_threshold = {m["threshold"]: m["reached"] for m in me2["milestones"]}
        assert by_threshold[1] is True
        assert by_threshold[3] is False
        assert me2["next_milestone"]["threshold"] == 3
        assert me2["next_milestone"]["remaining"] == 2

    def test_me_requires_auth(self, client) -> None:
        r = client.get("/api/referral/me")
        assert r.status_code == 401
