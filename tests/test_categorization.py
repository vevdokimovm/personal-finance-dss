"""Тесты rules-engine категоризации (FR-13)."""
import pytest

from app.core.categorization import classify_transaction


class TestAcceptanceCriteria:
    """Критерий приёмки FR-13."""

    def test_cafe_by_keyword(self):
        assert classify_transaction("Кофейня Surf Coffee", None, "expense") == "Кафе и рестораны"

    def test_salary(self):
        assert classify_transaction("Зарплата за май", None, "income") == "Зарплата"

    def test_groceries_by_mcc(self):
        assert classify_transaction("покупка", "5411", "expense") == "Продукты"


class TestRulePriority:
    @pytest.mark.parametrize("desc,mcc,ttype,expected", [
        ("Ozon оплата", None, "expense", "Покупки"),
        ("Яндекс.Такси поездка", None, "expense", "Транспорт"),
        ("аптека", "5912", "expense", "Здоровье"),
        ("Перекрёсток", None, "expense", "Продукты"),
        ("Netflix подписка", None, "expense", "Подписки и сервисы"),
        ("Перевод по СБП", None, "expense", "Переводы"),
        ("Кэшбэк за покупки", None, "income", "Кэшбэк"),
    ])
    def test_classification(self, desc, mcc, ttype, expected):
        assert classify_transaction(desc, mcc, ttype) == expected


class TestDefaults:
    def test_unknown_expense_is_other(self):
        assert classify_transaction("Какой-то магазин XYZ", None, "expense") == "Прочее"

    def test_unknown_income_is_other_income(self):
        assert classify_transaction("Непонятное поступление", None, "income") == "Прочий доход"

    def test_income_rule_not_applied_to_expense(self):
        # правило "зарплата" с applies_to=income не должно срабатывать на расходе
        assert classify_transaction("зарплата", None, "expense") == "Прочее"

    def test_empty_description(self):
        assert classify_transaction(None, None, "expense") == "Прочее"
        assert classify_transaction("", None, "income") == "Прочий доход"
