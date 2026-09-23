"""Пороговая ставка Avalanche берётся из одного места и динамически (ДК-36, WORK_QUEUE P0 §4).

Канон §10.2 задаёт r_bench = r_key · (1 − НДФЛ) и называет 0.14 ФОЛБЭКОМ на случай
недоступности источника ключевой ставки, с прямой оговоркой: «прежняя жёстко зашитая
константа 0.14 устаревала бы при движении ключевой и давала бы неверные советы
"гасить / не гасить"». Механизм в коде есть (`app.services.cbr_rate.get_opportunity_cost_rate`,
каскад сеть → память → кэш БД → фолбэк) и используется основным и демонстрационным контурами.

Два дефекта, которые фиксируют тесты:
1. B2B-маршрут не звал этот каскад вовсе — партнёр без явного `r_bench` получал расчёт
   по статике, тогда как тот же снимок в основном контуре считался бы по динамике;
2. литерал 0.14 был рассыпан по модулям, поэтому «поправить в одном месте» было физически
   невозможно: правка одного места создавала расхождение вместо исправления.
"""
import pathlib
import re

APP = pathlib.Path(__file__).resolve().parents[1] / "app"
LITERAL = re.compile(r"(?<![\d.])0\.14(?![\d])")
DOC_MARKERS = ('"""', "'''", "*", ">")


def _literal_hits():
    """Литерал 0.14 в ИСПОЛНЯЕМОМ коде вне единственного места — настроек.

    Упоминания в комментариях и докстроках не считаются: объяснять, откуда взялось число,
    нужно рядом с кодом, и запрет на это превратил бы тест в запрет писать пояснения.
    Само значение живёт в `app/core/avalanche.py` рядом с фильтром, которому оно нужно,
    и этот файл исключён как его законный дом. В окружение число не выносится: это параметр
    канона, а не настройка развёртывания.
    """
    hits = []
    for path in APP.rglob("*.py"):
        if path.name == "avalanche.py":
            continue  # законный дом константы канона
        for num, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            code = line.split("#", 1)[0]
            stripped = code.lstrip()
            if not stripped or stripped.startswith(DOC_MARKERS):
                continue
            if LITERAL.search(code) and "R_BENCH_FALLBACK" not in code:
                hits.append(f"{path.relative_to(APP.parent)}:{num}: {line.strip()}")
    return hits


class TestFallbackLivesInOnePlace:
    def test_no_scattered_literals(self):
        """0.14 существует ровно в одном месте — в настройках, а не россыпью по модулям."""
        hits = _literal_hits()
        assert hits == [], "литерал фолбэка вне конфигурации:\n" + "\n".join(hits)

    def test_core_exposes_the_fallback(self):
        from app.core.avalanche import R_BENCH_FALLBACK

        assert 0 < float(R_BENCH_FALLBACK) < 1


class TestB2BUsesTheSameSourceAsTheMainContour:
    def test_b2b_route_calls_the_dynamic_rate(self):
        """B2B-маршрут обязан ходить за динамической ставкой, как основной контур."""
        source = (APP / "api" / "routes_b2b.py").read_text(encoding="utf-8")
        assert "get_opportunity_cost_rate" in source, \
            "B2B считает по статике, мимо каскада ключевой ставки"

    def test_partner_without_rate_gets_the_dynamic_one(self):
        """Снимок без явного r_bench считается по тому же значению, что и основной контур."""
        from app.api.routes_b2b import SnapshotDTO, _to_snapshot
        from app.services.cbr_rate import get_opportunity_cost_rate

        expected = float(str(get_opportunity_cost_rate()["r_bench"]))
        snapshot = _to_snapshot(SnapshotDTO())
        assert abs(float(snapshot.r_bench) - expected) < 1e-9, \
            f"B2B взял {snapshot.r_bench}, основной контур считает по {expected}"

    def test_partner_rate_still_wins_when_given(self):
        """Явно присланная партнёром ставка не подменяется динамической."""
        from app.api.routes_b2b import SnapshotDTO, _to_snapshot

        snapshot = _to_snapshot(SnapshotDTO(r_bench=0.31))
        assert abs(float(snapshot.r_bench) - 0.31) < 1e-9
