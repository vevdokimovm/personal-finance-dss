"""Экспорт финансового отчёта (P3.1)."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.database.crud import get_goals, get_obligations, get_transactions
from app.dependencies import get_current_user_id, get_db
from app.services.report_pdf import build_financial_report_pdf

router = APIRouter(tags=["Экспорт"])


def _rate_pct(obligation) -> float:
    """Ставка хранится как доля (0.085) — приводим к процентам для отчёта."""
    rate = float(obligation.interest_rate)
    return rate * 100 if rate < 1 else rate


@router.get("/export/report.pdf", summary="Финансовый отчёт в PDF (скачивание)")
def export_report_pdf(
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
) -> Response:
    transactions = get_transactions(db, user_id=user_id)
    income = sum(float(t.amount) for t in transactions if t.type == "income")
    expense = sum(float(t.amount) for t in transactions if t.type == "expense")
    obligations = get_obligations(db, active_only=True, user_id=user_id)
    obligations_payment = sum(float(o.monthly_payment) for o in obligations)
    goals = get_goals(db, active_only=True, user_id=user_id)

    report = {
        "generated_at": datetime.utcnow().strftime("%d.%m.%Y %H:%M"),
        "income": income,
        "expense": expense,
        "obligations_payment": obligations_payment,
        "free_resource": income - expense - obligations_payment,
        "obligations": [
            {"name": o.name, "amount": float(o.amount), "rate": _rate_pct(o),
             "payment": float(o.monthly_payment)}
            for o in obligations
        ],
        "goals": [
            {"name": g.name, "current": float(g.current_amount), "target": float(g.target_amount)}
            for g in goals
        ],
    }

    pdf_bytes = build_financial_report_pdf(report)
    filename = f"finpilot-report-{datetime.utcnow():%Y-%m-%d}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
