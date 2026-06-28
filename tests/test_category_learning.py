"""Тесты обучения категоризации на правках пользователя (P2.7).

Детерминированно, без ML: ручное переназначение категории операции запоминается как правило
(match_token -> category) и применяется к будущим импортам и ретроактивно к прошлым операциям.
Покрытие: ядро classify_with_rules, CRUD правил, set/apply, импорт уважает правила,
изоляция per-user, эндпоинты.
"""
from __future__ import annotations

from datetime import datetime

from fastapi.testclient import TestClient

from app.core.categorization import (
    MIN_MATCH_TOKEN_LEN,
    classify_with_rules,
    normalize_match_key,
)
from app.database import crud
from app.database.models import User

EXPENSE = "expense"
INCOME = "income"


def _user(db, uid: str) -> str:
    db.add(User(id=uid, email=f"{uid}@test.io", password_hash="x"))
    db.commit()
    return uid


def _txn(db, *, description, category=None, ttype=EXPENSE, user_id=None, amount=1000):
    return crud.create_transaction(
        db,
        amount=amount,
        type=ttype,
        date=datetime(2026, 6, 1),
        category=category,
        description=description,
        user_id=user_id,
    )


# ── Ядро: classify_with_rules (чистая функция) ───────────────────────────
class TestClassifyWithRules:
    def test_rule_hit_overrides_default(self):
        # без правила "Какой-то магазин XYZ" → Прочее; правило с токеном переопределяет
        rules = [("xyz", "Покупки")]
        assert classify_with_rules("Какой-то магазин XYZ", None, EXPENSE, rules) == "Покупки"

    def test_no_rules_falls_back_to_default(self):
        assert classify_with_rules("Какой-то магазин XYZ", None, EXPENSE, []) == "Прочее"

    def test_rule_does_not_shadow_when_token_absent(self):
        rules = [("starbucks", "Кафе и рестораны")]
        assert classify_with_rules("Какой-то магазин XYZ", None, EXPENSE, rules) == "Прочее"

    def test_guard_short_token_ignored(self):
        # токен короче MIN_MATCH_TOKEN_LEN отсекается → fallback на дефолт
        assert MIN_MATCH_TOKEN_LEN == 3
        rules = [("xy", "Покупки")]
        assert classify_with_rules("Какой-то магазин XYZ", None, EXPENSE, rules) == "Прочее"

    def test_match_is_case_and_space_insensitive(self):
        rules = [("  PYÁTEROCHKA  ".replace("Á", "A"), "Продукты")]
        assert classify_with_rules("оплата pyaterochka 12", None, EXPENSE, rules) == "Продукты"

    def test_first_matching_rule_wins(self):
        rules = [("shop", "Покупки"), ("xyz", "Развлечения")]
        assert classify_with_rules("xyz shop", None, EXPENSE, rules) == "Покупки"

    def test_empty_description_falls_back(self):
        assert classify_with_rules("", None, INCOME, [("anything", "Покупки")]) == "Прочий доход"


def test_normalize_match_key():
    assert normalize_match_key("  STARBUCKS  Москва ") == "starbucks москва"
    assert normalize_match_key(None) == ""
    assert normalize_match_key("") == ""


# ── CRUD правил ──────────────────────────────────────────────────────────
class TestRuleCrud:
    def test_upsert_creates_then_updates(self, db_session):
        uid = _user(db_session, "u-up")
        r1 = crud.upsert_category_rule(db_session, uid, "Pyaterochka", "Продукты", EXPENSE)
        assert r1.match_token == "pyaterochka"  # хранится нормализованным
        assert r1.category == "Продукты"
        # тот же ключ (разный регистр) → апдейт, не новая строка
        r2 = crud.upsert_category_rule(db_session, uid, "PYATEROCHKA", "Кафе и рестораны", EXPENSE)
        assert r2.id == r1.id
        assert r2.category == "Кафе и рестораны"
        assert len(crud.get_category_rules(db_session, uid)) == 1

    def test_get_user_category_rules_filters_by_type(self, db_session):
        uid = _user(db_session, "u-flt")
        crud.upsert_category_rule(db_session, uid, "salary corp", "Зарплата", INCOME)
        crud.upsert_category_rule(db_session, uid, "ozon", "Покупки", EXPENSE)
        exp = crud.get_user_category_rules(db_session, uid, EXPENSE)
        inc = crud.get_user_category_rules(db_session, uid, INCOME)
        assert exp == [("ozon", "Покупки")]
        assert inc == [("salary corp", "Зарплата")]

    def test_delete_rule(self, db_session):
        uid = _user(db_session, "u-del")
        rule = crud.upsert_category_rule(db_session, uid, "netflix", "Подписки и сервисы", EXPENSE)
        assert crud.delete_category_rule(db_session, rule.id, user_id=uid) is True
        assert crud.get_category_rules(db_session, uid) == []
        assert crud.delete_category_rule(db_session, rule.id, user_id=uid) is False

    def test_rules_isolated_per_user(self, db_session):
        a = _user(db_session, "u-a")
        b = _user(db_session, "u-b")
        crud.upsert_category_rule(db_session, a, "ozon", "Покупки", EXPENSE)
        assert crud.get_user_category_rules(db_session, b, EXPENSE) == []
        # B не может удалить правило A
        rule_a = crud.get_category_rules(db_session, a)[0]
        assert crud.delete_category_rule(db_session, rule_a.id, user_id=b) is False


# ── set_transaction_category / apply_category_rule ───────────────────────
class TestSetAndApply:
    def test_set_category_changes_transaction(self, db_session):
        uid = _user(db_session, "u-set")
        txn = _txn(db_session, description="OZON 123", category="Прочее", user_id=uid)
        updated = crud.set_transaction_category(db_session, txn.id, "Покупки", user_id=uid)
        assert updated is not None
        assert updated.category == "Покупки"

    def test_set_category_resolves_category_id_when_system_exists(self, db_session):
        uid = _user(db_session, "u-cid")
        crud.create_category(db_session, name="Покупки", type=EXPENSE, is_system=True)
        txn = _txn(db_session, description="OZON", category="Прочее", user_id=uid)
        updated = crud.set_transaction_category(db_session, txn.id, "Покупки", user_id=uid)
        assert updated.category_id is not None

    def test_set_category_returns_none_for_foreign_or_missing(self, db_session):
        a = _user(db_session, "u-s1")
        b = _user(db_session, "u-s2")
        txn = _txn(db_session, description="OZON", user_id=a)
        # чужой пользователь не может переназначить
        assert crud.set_transaction_category(db_session, txn.id, "Покупки", user_id=b) is None
        assert crud.set_transaction_category(db_session, 999999, "Покупки", user_id=a) is None

    def test_apply_rule_retroactively_with_count(self, db_session):
        uid = _user(db_session, "u-apply")
        t1 = _txn(db_session, description="OZON 1", category="Прочее", user_id=uid)
        _txn(db_session, description="ozon 2", category="Прочее", user_id=uid)
        _txn(db_session, description="OZON store 3", category="Прочее", user_id=uid)
        _txn(db_session, description="Пятёрочка", category="Прочее", user_id=uid)
        # применяем правило ozon -> Покупки, исключая исходную t1
        count = crud.apply_category_rule(
            db_session, uid, "ozon", "Покупки", EXPENSE, exclude_id=t1.id
        )
        assert count == 2  # два совпадающих ozon (t1 исключён, Пятёрочка не матчит)
        cats = {t.description: t.category for t in crud.get_transactions(db_session, user_id=uid)}
        assert cats["ozon 2"] == "Покупки"
        assert cats["OZON store 3"] == "Покупки"
        assert cats["Пятёрочка"] == "Прочее"

    def test_apply_rule_respects_type(self, db_session):
        uid = _user(db_session, "u-type")
        exp = _txn(db_session, description="ACME", category="Прочее", ttype=EXPENSE, user_id=uid)
        inc = _txn(db_session, description="ACME", category="Прочий доход", ttype=INCOME, user_id=uid)
        crud.apply_category_rule(db_session, uid, "acme", "Покупки", EXPENSE)
        db_session.refresh(exp)
        db_session.refresh(inc)
        assert exp.category == "Покупки"
        assert inc.category == "Прочий доход"  # доход не тронут

    def test_apply_rule_short_token_noop(self, db_session):
        uid = _user(db_session, "u-short")
        _txn(db_session, description="AB store", category="Прочее", user_id=uid)
        assert crud.apply_category_rule(db_session, uid, "ab", "Покупки", EXPENSE) == 0

    def test_apply_rule_isolated_per_user(self, db_session):
        a = _user(db_session, "u-ia")
        b = _user(db_session, "u-ib")
        ta = _txn(db_session, description="OZON", category="Прочее", user_id=a)
        tb = _txn(db_session, description="OZON", category="Прочее", user_id=b)
        crud.apply_category_rule(db_session, a, "ozon", "Покупки", EXPENSE)
        db_session.refresh(ta)
        db_session.refresh(tb)
        assert ta.category == "Покупки"
        assert tb.category == "Прочее"  # операция другого пользователя не затронута


# ── Импорт/создание уважают правила ──────────────────────────────────────
class TestImportRespectsRules:
    def test_single_create_uses_rule(self, db_session):
        uid = _user(db_session, "u-cr")
        crud.upsert_category_rule(db_session, uid, "xyzmart", "Покупки", EXPENSE)
        txn = _txn(db_session, description="оплата XYZMART 99", user_id=uid)  # без явной категории
        assert txn.category == "Покупки"

    def test_explicit_category_beats_rule(self, db_session):
        uid = _user(db_session, "u-exp")
        crud.upsert_category_rule(db_session, uid, "xyzmart", "Покупки", EXPENSE)
        txn = _txn(db_session, description="XYZMART", category="Развлечения", user_id=uid)
        assert txn.category == "Развлечения"  # явный ввод важнее правила

    def test_bulk_import_applies_rules(self, db_session):
        uid = _user(db_session, "u-bulk")
        crud.upsert_category_rule(db_session, uid, "xyzmart", "Покупки", EXPENSE)
        rows = [
            {"amount": 100, "type": EXPENSE, "date": datetime(2026, 6, 2), "description": "XYZMART 1"},
            {"amount": 200, "type": EXPENSE, "date": datetime(2026, 6, 3), "description": "оплата xyzmart 2"},
            {"amount": 300, "type": EXPENSE, "date": datetime(2026, 6, 4), "description": "Неизвестно ZZZ"},
        ]
        assert crud.bulk_create_transactions(db_session, rows, user_id=uid) == 3
        cats = {t.description: t.category for t in crud.get_transactions(db_session, user_id=uid)}
        assert cats["XYZMART 1"] == "Покупки"
        assert cats["оплата xyzmart 2"] == "Покупки"
        assert cats["Неизвестно ZZZ"] == "Прочее"


# ── Эндпоинты ────────────────────────────────────────────────────────────
class TestEndpoints:
    def _create_txn(self, client: TestClient, *, description, category="Прочее", ttype=EXPENSE):
        r = client.post("/api/transactions", json={
            "amount": 1000, "category": category, "type": ttype,
            "date": "2026-06-01T00:00:00", "description": description,
        })
        assert r.status_code in (200, 201)
        return r.json()["id"]

    def test_recategorize_learns_and_applies(self, client: TestClient):
        t1 = self._create_txn(client, description="OZON 1")
        self._create_txn(client, description="ozon 2")
        resp = client.post(f"/api/transactions/{t1}/category", json={
            "category": "Покупки", "match_token": "ozon", "apply_to_matching": True,
        })
        assert resp.status_code == 200
        body = resp.json()
        assert body["transaction"]["category"] == "Покупки"
        assert body["rule"]["match_token"] == "ozon"
        assert body["updated_count"] == 1  # вторая ozon-операция

    def test_recategorize_without_learning(self, client: TestClient):
        tid = self._create_txn(client, description="OZON")
        resp = client.post(f"/api/transactions/{tid}/category", json={
            "category": "Покупки", "learn": False,
        })
        assert resp.status_code == 200
        assert resp.json()["rule"] is None
        assert client.get("/api/category-rules").json() == []

    def test_recategorize_404_for_missing(self, client: TestClient):
        resp = client.post("/api/transactions/999999/category", json={"category": "Покупки"})
        assert resp.status_code == 404

    def test_list_and_delete_rules(self, client: TestClient):
        tid = self._create_txn(client, description="NETFLIXPAY")
        client.post(f"/api/transactions/{tid}/category", json={
            "category": "Подписки и сервисы", "match_token": "netflixpay",
        })
        rules = client.get("/api/category-rules").json()
        assert len(rules) == 1
        rule_id = rules[0]["id"]
        deleted = client.delete(f"/api/category-rules/{rule_id}")
        assert deleted.status_code == 204
        assert client.get("/api/category-rules").json() == []

    def test_delete_rule_404(self, client: TestClient):
        assert client.delete("/api/category-rules/999999").status_code == 404
