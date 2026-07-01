"""ExpenseRecord несёт точную дату операции, не только период «YYYY-MM».

Контекст (техдолг 4.3). Раньше ExpenseRecord хранил лишь ``period`` — это блокировало
будущий слой внутримесячных паттернов и паттернов по дням недели (нельзя восстановить
день операции из «2026-01»). Добавляем опциональное поле ``date`` (точный момент
операции). Когда дата задана — она источник истины: ``period`` выводится из неё, что
исключает рассинхрон period↔date. Поле опционально (дефолт ``None``) — существующие
конструкторы (в т.ч. позиционные) не ломаются.

Написано до реализации (TDD): пока поля ``date`` нет — конструктор с ``date=...`` падает
(TypeError) и обращение к ``.date`` даёт AttributeError (red). После добавления — зелёные.
"""
from __future__ import annotations

from datetime import datetime

from app.core.spending_advice import ExpenseRecord, SpendingAdvisor
from app.database.crud import create_transaction
from app.services.spending import get_spending_advice


def test_expense_record_accepts_exact_date() -> None:
    d = datetime(2026, 1, 17, 14, 30)
    rec = ExpenseRecord(category="Еда", amount=500.0, period="2026-01", date=d)
    assert rec.date == d


def test_expense_record_date_is_optional() -> None:
    # Обратная совместимость: позиционный конструктор без date продолжает работать,
    # date по умолчанию None.
    rec = ExpenseRecord("Покупки", 100.0, "2026-02")
    assert rec.date is None


def test_period_is_derived_from_date_when_present() -> None:
    # Дата — источник истины: period приводится к месяцу даты, даже если передан иной.
    rec = ExpenseRecord(category="Транспорт", amount=80.0, period="1999-12",
                        date=datetime(2026, 3, 4))
    assert rec.period == "2026-03"


def test_period_kept_when_no_date() -> None:
    # Без даты period остаётся как передан (не перезаписывается).
    rec = ExpenseRecord(category="Связь", amount=30.0, period="2026-05")
    assert rec.period == "2026-05"
    assert rec.date is None


class _SpyAdvisor(SpendingAdvisor):
    """Перехватывает records, переданные в analyze, для проверки проброса date."""

    def __init__(self) -> None:
        super().__init__()
        self.seen_records: list[ExpenseRecord] | None = None

    def analyze(self, records, current_period):  # type: ignore[override]
        self.seen_records = list(records)
        return super().analyze(records, current_period)


def test_spending_advice_populates_exact_date_from_transaction(db_session) -> None:
    d = datetime(2026, 1, 10, 9, 0)
    create_transaction(
        db_session, amount=250.0, type="expense",
        date=d, category="Еда", description="завтрак",
    )
    spy = _SpyAdvisor()
    get_spending_advice(db_session, advisor=spy)
    assert spy.seen_records, "advisor должен получить хотя бы одну запись"
    rec = spy.seen_records[0]
    assert rec.date == d
    assert rec.period == "2026-01"
