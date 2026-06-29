"""Тесты v3.0.0: мультивалюта, ingestion-слой, шифрование, B2B (FR-18/19/23, INFRA-15/17)."""
from __future__ import annotations

from datetime import timedelta
from app.utils.time import utcnow
from decimal import Decimal


# ── FR-19: мультивалюта ──────────────────────────────────────────────────
def test_currency_converter_via_usd_pivot():
    from app.services.currency import CurrencyConverter

    conv = CurrencyConverter({"USD": Decimal("1"), "RUB": Decimal("0.0107"), "EUR": Decimal("1.09")})
    # 1000 USD → RUB: 1000 * 1 / 0.0107
    assert conv.convert(1000, "USD", "RUB") == Decimal("93457.94")
    # Идемпотентность
    assert conv.convert(500, "RUB", "RUB") == Decimal("500")
    # Неизвестная валюта — сумма не искажается
    assert conv.convert(100, "XXX", "RUB") == Decimal("100")


def test_fx_rates_seeded_and_convert_endpoint(client):
    rates = client.get("/api/fx/rates").json()
    assert len(rates) >= 8
    codes = {r["currency"] for r in rates}
    assert {"USD", "RUB", "EUR"}.issubset(codes)

    r = client.post(
        "/api/fx/convert", json={"amount": 1000, "from_currency": "USD", "to_currency": "RUB"}
    )
    assert r.status_code == 200
    assert r.json()["result"] > 0


def test_fx_upsert_rate(client):
    r = client.put("/api/fx/rates", json={"currency": "jpy", "rate_to_usd": 0.0067})
    assert r.status_code == 200
    assert r.json()["currency"] == "JPY"


# ── INFRA-15 / REFACTOR-04: адаптер ядра под FinanceEngine ───────────────
def test_core_engine_satisfies_protocol():
    from app.ingestion.contracts import FinanceEngine
    from app.ingestion.engine import CoreFinanceEngine

    assert isinstance(CoreFinanceEngine(), FinanceEngine)


def test_core_engine_avalanche_filters_cheap_debt():
    """Дорогой долг (>r_bench) → досрочка; KEEP-01 сохранён через адаптер."""
    from app.ingestion.engine import CoreFinanceEngine
    from app.ingestion.models import (
        Debt,
        FinancialSnapshot,
        RiskProfile,
        Transaction,
        TransactionType,
    )

    snap = FinancialSnapshot(
        base_currency="RUB",
        transactions=[
            Transaction("t1", Decimal("180000"), TransactionType.INCOME, utcnow()),
            Transaction("t2", Decimal("78000"), TransactionType.EXPENSE, utcnow()),
        ],
        debts=[Debt("d1", "Кредитка", Decimal("200000"), Decimal("25000"), Decimal("0.249"), 24)],
        r_bench=Decimal("0.14"),
    )
    rec = CoreFinanceEngine().analyze(snap, RiskProfile.BALANCED)
    assert rec.rt > 0
    # Дорогой долг 24.9% > 14% → ресурс уходит на долг (KEEP-01)
    assert rec.allocation.to_debt > 0
    # Без целей число альтернатив меньше максимума (21 — только при наличии всех трёх направлений)
    assert rec.alternatives_total > 0


def test_core_engine_multicurrency_conversion():
    from app.ingestion.engine import CoreFinanceEngine
    from app.ingestion.models import FinancialSnapshot, RiskProfile, Transaction, TransactionType
    from app.services.currency import CurrencyConverter

    conv = CurrencyConverter({"USD": Decimal("1"), "RUB": Decimal("0.0107")})
    snap = FinancialSnapshot(
        base_currency="RUB",
        transactions=[Transaction("t1", Decimal("2000"), TransactionType.INCOME, utcnow(), "USD")],
    )
    rec = CoreFinanceEngine(converter=conv).analyze(snap, RiskProfile.BALANCED)
    # 2000 USD ≈ 186916 RUB
    assert rec.rt > Decimal("180000")


# ── INFRA-17 / NFR-06: шифрование токенов ────────────────────────────────
def test_token_cipher_roundtrip():
    from app.services.security import TokenCipher

    cipher = TokenCipher()
    secret = "access-sandbox-abc123"
    encrypted = cipher.encrypt(secret)
    assert encrypted != secret
    assert cipher.decrypt(encrypted) == secret
    assert cipher.decrypt("garbage") is None


def test_password_hasher_verify():
    from app.services.security import PasswordHasher

    hasher = PasswordHasher()
    h = hasher.hash("mypassword")
    assert h != "mypassword"
    assert hasher.verify("mypassword", h)
    assert not hasher.verify("wrong", h)


def test_jwt_issue_and_decode():
    from app.services.security import TokenService

    svc = TokenService()
    token = svc.issue("uid-123", "x@y.io")
    payload = svc.decode(token)
    assert payload is not None
    assert payload["sub"] == "uid-123"
    assert svc.decode("not-a-token") is None


# ── INFRA-18: персистентность ManualProvider ─────────────────────────────
def test_manual_snapshot_persistence(client):
    from app.database.db import SessionLocal
    from app.ingestion.models import (
        Account,
        FinancialSnapshot,
        Goal,
        RiskProfile,
    )
    from app.ingestion.providers.manual import (
        ManualProvider,
        ManualSnapshotRepository,
    )

    db = SessionLocal()
    try:
        repo = ManualSnapshotRepository(db)
        snap = FinancialSnapshot(
            base_currency="RUB",
            risk_profile=RiskProfile.AGGRESSIVE,
            accounts=[Account("a1", "Депозит", Decimal("150000"), "RUB", is_liquid=True)],
            goals=[Goal("g1", "Цель", Decimal("300000"), Decimal("50000"), utcnow() + timedelta(days=180))],
            r_bench=Decimal("0.16"),
        )
        repo.save("user-x", snap)

        provider = ManualProvider(repo)
        loaded = provider.fetch_snapshot("user-x")
        assert loaded.base_currency == "RUB"
        assert loaded.risk_profile == RiskProfile.AGGRESSIVE
        assert len(loaded.accounts) == 1
        assert loaded.accounts[0].balance == Decimal("150000")
        assert loaded.r_bench == Decimal("0.16")
    finally:
        db.close()


# ── FR-23: B2B /v1/analyze ───────────────────────────────────────────────
def test_b2b_disabled_without_api_keys(client):
    r = client.post("/v1/analyze", json={"base_currency": "RUB", "transactions": []})
    assert r.status_code == 404


def test_b2b_analyze_with_api_key(client, monkeypatch):
    from app.config import settings

    monkeypatch.setattr(settings, "B2B_API_KEYS", "partner-secret-key")

    payload = {
        "base_currency": "RUB",
        "risk_profile": 3,
        "transactions": [
            {"transaction_id": "t1", "amount": 180000, "type": 1, "date": "2026-06-01T00:00:00"},
            {"transaction_id": "t2", "amount": 78000, "type": 2, "date": "2026-06-02T00:00:00"},
        ],
        "debts": [
            {"debt_id": "d1", "name": "Кредитка", "balance": 200000,
             "monthly_payment": 25000, "interest_rate": 0.249, "term_months": 24}
        ],
        "r_bench": 0.14,
    }
    # Без ключа → 401
    assert client.post("/v1/analyze", json=payload).status_code == 401
    # С ключом → 200
    r = client.post("/v1/analyze", json=payload, headers={"X-API-Key": "partner-secret-key"})
    assert r.status_code == 200
    body = r.json()
    assert body["rt"] > 0
    assert body["alternatives_total"] > 0
    assert "allocation" in body


# ── FR-18: Plaid отключён без конфига ────────────────────────────────────
def test_plaid_disabled_without_config(client):
    header = {"Authorization": f"Bearer {_token(client)}"}
    r = client.post("/api/plaid/sync", headers=header)
    assert r.status_code == 404


def _token(client) -> str:
    r = client.post("/api/auth/register", json={"email": "plaid@fp.io", "password": "strongpass1"})
    return r.json()["access_token"]
