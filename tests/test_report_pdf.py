"""Экспорт финансового отчёта в PDF (P3.1)."""
from __future__ import annotations

from datetime import datetime

from app.database import crud
from app.services.report_pdf import build_financial_report_pdf

_SAMPLE = {
    "generated_at": "21.06.2026 10:00",
    "income": 150000.0,
    "expense": 90000.0,
    "obligations_payment": 25000.0,
    "free_resource": 35000.0,
    "obligations": [
        {"name": "Ипотека", "amount": 3000000.0, "rate": 8.5, "payment": 25000.0},
    ],
    "goals": [
        {"name": "Подушка безопасности", "current": 100000.0, "target": 300000.0},
    ],
}


class TestBuildPdf:
    def test_returns_pdf_bytes(self) -> None:
        data = build_financial_report_pdf(_SAMPLE)
        assert isinstance(data, bytes)
        assert data[:5] == b"%PDF-"
        assert len(data) > 1000  # непустой документ

    def test_empty_sections_do_not_crash(self) -> None:
        empty = {**_SAMPLE, "obligations": [], "goals": []}
        data = build_financial_report_pdf(empty)
        assert data[:5] == b"%PDF-"

    def test_zero_target_goal_no_division_error(self) -> None:
        edge = {**_SAMPLE, "goals": [{"name": "X", "current": 0.0, "target": 0.0}]}
        data = build_financial_report_pdf(edge)
        assert data[:5] == b"%PDF-"


class TestPdfEndpoint:
    def test_endpoint_returns_pdf(self, client) -> None:
        r = client.get("/api/export/report.pdf")
        assert r.status_code == 200
        assert r.headers["content-type"] == "application/pdf"
        assert r.content[:5] == b"%PDF-"
        assert "attachment" in r.headers.get("content-disposition", "")

    def test_endpoint_with_data(self, client, db_session) -> None:
        db = db_session
        crud.create_transaction(db, amount=100000, type="income", date=datetime(2026, 6, 1))
        crud.create_obligation(db, name="Кредит", amount=500000, interest_rate=0.15,
                               term=24, monthly_payment=20000, payment_day=10)
        crud.create_goal(db, name="Отпуск", target_amount=150000, current_amount=50000,
                         deadline=datetime(2027, 1, 1))
        r = client.get("/api/export/report.pdf")
        assert r.status_code == 200
        assert r.content[:5] == b"%PDF-"
