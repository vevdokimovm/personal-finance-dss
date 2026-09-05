"""Контракт `/admin/experiments/{key}/results`: схема вместо `dict` (v8.49.0).

Правило проекта, ни одного исключения за веху 8: эндпоинт, размеченный `-> dict`,
не попадает в `openapi.json` полями, генератор клиента выдаёт `unknown`, и фронт
дописывает тип руками. Ровно так родился `ForecastResult`, знавший 5 полей из 12
(v8.48.0). Схема заводится ДО экрана.

Здесь же проверяется, что в ответе есть **вывод**, а не только счётчики: какой
вариант выигрывает и можно ли верить разнице.
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from app.services.experiments import create_experiment, get_or_assign_variant


def _make_experiment(db_session, key: str = "exp-contract") -> None:
    create_experiment(
        db_session,
        key,
        name="Проверка контракта",
        variants=[{"name": "control", "weight": 1}, {"name": "test", "weight": 1}],
        conversion_event="plan_calculated",
        status="running",
    )
    db_session.commit()


class TestResultsSchema:
    """Ответ описан схемой и несёт вывод, а не только сырые счётчики."""

    def test_response_has_declared_fields(self, client: TestClient, db_session) -> None:
        """Поля ответа на месте — их читает фронт и генератор клиента."""
        _make_experiment(db_session)
        body = client.get("/api/admin/experiments/exp-contract/results").json()

        assert body["key"] == "exp-contract"
        assert body["status"] == "running"
        assert body["conversion_event"] == "plan_calculated"
        assert isinstance(body["variants"], list)

    def test_variant_rows_carry_significance(self, client: TestClient, db_session) -> None:
        """🔴 Каждый вариант несёт сравнение с контролем, а не голый процент.

        Без этих полей экран показывает два числа рядом, и человек читает большее
        как победу — независимо от того, различимы они статистически или нет.
        """
        _make_experiment(db_session, "exp-sig")
        for i in range(4):
            get_or_assign_variant(db_session, "exp-sig", user_id=f"u{i}", session_id=None)
        db_session.commit()

        variants = client.get("/api/admin/experiments/exp-sig/results").json()["variants"]
        assert variants, "варианты обязаны быть в ответе"
        for row in variants:
            assert "variant" in row and "assigned" in row and "converted" in row
            assert "conversion_rate" in row
            assert "is_control" in row, "фронт обязан знать, с чем сравнивают"
            assert "uplift_pct" in row
            assert "p_value" in row
            assert "significant" in row

    def test_control_row_is_marked_and_not_compared_to_itself(
        self, client: TestClient, db_session
    ) -> None:
        """Контроль помечен и не сравнивается сам с собой.

        «Подъём контроля над контролем» — ноль по определению; показывать его как
        результат значит заводить строку, которая ничего не значит.
        """
        _make_experiment(db_session, "exp-control")
        variants = client.get("/api/admin/experiments/exp-control/results").json()["variants"]

        control_rows = [v for v in variants if v["is_control"]]
        assert len(control_rows) == 1, "контроль ровно один — первый вариант"
        assert control_rows[0]["uplift_pct"] is None
        assert control_rows[0]["p_value"] is None
        assert control_rows[0]["significant"] is False

    def test_openapi_declares_schema_not_bare_dict(self, client: TestClient) -> None:
        """🔴 Гейт против возврата к `-> dict`.

        Проверяется снимок OpenAPI: у ответа обязан быть `$ref` на схему. Мутация
        «вернуть dict» роняет именно этот тест, а не разметку экрана.
        """
        schema = client.get("/openapi.json").json()
        path = schema["paths"]["/api/admin/experiments/{key}/results"]["get"]
        content = path["responses"]["200"]["content"]["application/json"]["schema"]
        assert "$ref" in content or content.get("type") == "object" and "properties" in content, (
            "ответ результатов эксперимента не описан схемой — фронт получит unknown"
        )
