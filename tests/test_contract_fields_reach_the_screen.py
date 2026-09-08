"""Поле контракта, которое считается, но никому не показывается, — заметно сразу.

## Зачем

Класс `CONSENT-GATE-NO-UI` повторился в продукте **пять раз**: гейт согласия,
правила категорий, кризисный план, spending-advice и — самый крупный — половина ответа
`/planning/calculate`. Каждый раз одинаково: бэкенд считает, поле лежит в контракте,
фронта нет, и никто не замечает, пока не пройдёт путь целиком.

🔴 **Общая причина у всех пяти — отсутствие механической сверки.** Экраны проверялись
по отдельности, а вопрос «у этого поля вообще есть потребитель» не задавал никто.

## Как устроено

Для схемы альтернативы плана (самый нагруженный объект ответа) сверяется: каждое поле
либо встречается во `frontend/src` вне сгенерированного клиента, либо стоит
в `WITHOUT_CONSUMER` с причиной.

**Список может только сокращаться:** его длина зафиксирована, и добавление нового поля
без экрана валит гейт. Это не запрет заводить поля впрок — это требование назвать
такое поле вслух, а не обнаружить его через полтора десятка версий.

Замер на момент заведения (08.09.2026): **15 полей** кластера совета без потребителя;
по всей поверхности контракта — 122 из 767, но там много служебного.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = REPO_ROOT / "docs" / "api" / "openapi.json"
FRONTEND_SRC = REPO_ROOT / "frontend" / "src"

# 🔴 Проверяется КЛАСТЕР СОВЕТА, а не весь контракт. Замер по всей поверхности:
# 122 поля из 767 (16 %) не имеют потребителя во фронте — но значительная часть
# служебная по назначению (телеметрия, аудит: `input_snapshot_hash`, `model_version`),
# и список из 122 исключений превратил бы гейт в украшение. Здесь — объекты, содержание
# которых канон обещает ПОЛЬЗОВАТЕЛЮ: сама альтернатива и показатели плана.
SCHEMAS = ("Alternative", "PlanningIndicators")

# Поля без экрана на 08.09.2026. Каждое — задача в ROADMAP.md (пятый случай класса),
# а не «так задумано»: канон §10–13 описывает их как часть совета, а не как служебные.
WITHOUT_CONSUMER: dict[str, str] = {
    "avalanche_detail": "помесячный график погашения (ADR-016, §10.5, канон v3.8.0)",
    "obligation_allocation": "какому кредиту сколько уходит — ядро Avalanche-совета (§10)",
    "goal_allocation": "разбор распределения по целям (§11)",
    "goal_breakdown": "детализация целей (§11)",
    "investment_tranche": "инвестиционный транш: полка по профилю, нота АСВ (§13)",
    "x_obl_unused": "нераспределённый остаток по долгам (§9)",
    "x_goals_unused": "нераспределённый остаток по целям (§9)",
    "x_obl_effective": "фактически ушедшее в долги после подрезки (§9)",
    "x_reserve_effective": "фактически ушедшее в резерв после подрезки (§9)",
    "x_remain": "остаток, не ушедший никуда (§9)",
    # PlanningIndicators — показатели плана, тот же кластер совета.
    "Dt_alert": "флаг «ПДН выше 0.40» — канон §7 обещает его вместе с советом о рефинансировании",
    "debt_schedule": "график погашения: сколько месяцев и процентов экономит план",
    "CFt": "денежный поток периода",
    "income_cv": "волатильность дохода — от неё зависит надбавка к floor резерва (ADR-015)",
    "BLR_status": "статус базового уровня ликвидности",
}


def _schema_properties() -> list[str]:
    schemas = json.loads(SNAPSHOT.read_text(encoding="utf-8"))["components"]["schemas"]
    props: set[str] = set()
    for name in SCHEMAS:
        assert name in schemas, f"в снимке контракта нет схемы {name}"
        props |= set(schemas[name].get("properties", {}))
    return sorted(props)


def _frontend_text() -> str:
    parts: list[str] = []
    for path in FRONTEND_SRC.rglob("*"):
        if not path.is_file() or path.suffix not in {".ts", ".tsx"}:
            continue
        if "generated" in path.parts or "node_modules" in path.parts:
            continue
        parts.append(path.read_text(encoding="utf-8", errors="ignore"))
    return "\n".join(parts)


class TestEveryFieldEitherShowsUpOrIsDeclared:
    """Поле либо доехало до экрана, либо названо в списке с причиной."""

    def test_no_silent_field_without_a_screen(self) -> None:
        """🔴 Мутация «завести новое поле в схеме» роняет тест здесь.

        Именно так и накапливались пять прошлых случаев: поле появлялось,
        экран не появлялся, и заметить это было нечем.
        """
        blob = _frontend_text()
        silent = [
            field
            for field in _schema_properties()
            if field not in blob and field not in WITHOUT_CONSUMER
        ]
        assert not silent, (
            f"поля кластера совета {SCHEMAS} считаются и не показываются никому: {silent} — "
            "либо выведите на экран, либо назовите в WITHOUT_CONSUMER с причиной"
        )

    def test_declared_list_does_not_grow(self) -> None:
        """Список — долг, а не свалка: он может только сокращаться."""
        assert len(WITHOUT_CONSUMER) <= 15, (
            f"полей без экрана стало {len(WITHOUT_CONSUMER)} — список задуман убывающим"
        )

    def test_every_declared_field_still_exists(self) -> None:
        """Поле убрали из контракта — убирается и из списка.

        Иначе список хранит долг по несуществующему полю и выглядит длиннее правды.
        """
        props = set(_schema_properties())
        stale = sorted(set(WITHOUT_CONSUMER) - props)
        assert not stale, f"в списке поля, которых больше нет в контракте: {stale}"

    def test_every_declared_field_states_a_reason(self) -> None:
        empty = [f for f, why in WITHOUT_CONSUMER.items() if len(why.strip()) < 15]
        assert not empty, f"поле без внятной причины: {empty}"


class TestGateItselfWorks:
    """Обход действительно читает фронт, а не пустоту."""

    def test_frontend_text_is_substantial(self) -> None:
        assert len(_frontend_text()) > 200_000

    def test_schema_has_expected_shape(self) -> None:
        props = _schema_properties()
        assert len(props) > 25, f"в кластере совета подозрительно мало полей: {len(props)}"
        assert "utility" in props and "Rt_new" in props
