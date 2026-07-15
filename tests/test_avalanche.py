"""Тесты Avalanche-распределения досрочки с фильтром по ставке (формула ВКР §41)."""
from app.core.avalanche import allocate_obligations_avalanche


def _obligations():
    return [
        {"id": 1, "amount": 100000, "monthly_payment": 5000, "interest_rate": 0.25},
        {"id": 2, "amount": 50000, "monthly_payment": 3000, "interest_rate": 0.08},
    ]


class TestAvalanche:
    def test_no_money(self):
        eff, _, unused = allocate_obligations_avalanche(0, _obligations(), 0.14)
        assert eff == 0.0 and unused == 0

    def test_no_obligations(self):
        eff, _, unused = allocate_obligations_avalanche(10000, [], 0.14)
        assert eff == 0.0 and unused == 10000

    def test_all_below_benchmark_skipped(self):
        # ставка ниже бенчмарка → досрочка невыгодна (NPV), деньги возвращаются
        obls = [{"id": 1, "amount": 100000, "monthly_payment": 5000, "interest_rate": 0.08}]
        eff, _, unused = allocate_obligations_avalanche(10000, obls, 0.14)
        assert eff == 0.0 and unused == 10000

    def test_high_rate_targeted_first(self):
        eff, new, _ = allocate_obligations_avalanche(10000, _obligations(), 0.14)
        assert eff == 10000.0
        by_id = {o["id"]: o for o in new}
        assert by_id[1]["amount"] == 90000     # дорогой кредит гасится
        assert by_id[2]["amount"] == 50000     # дешёвый (ниже бенчмарка) не тронут

    def test_payment_reduced_proportionally(self):
        eff, new, _ = allocate_obligations_avalanche(10000, _obligations(), 0.14)
        by_id = {o["id"]: o for o in new}
        # 90000/100000 * 5000 = 4500
        assert by_id[1]["monthly_payment"] == 4500.0
