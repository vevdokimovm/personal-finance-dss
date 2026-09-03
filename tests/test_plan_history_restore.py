"""Восстановление удалённого снимка плана (v8.38.0).

🔴 Продукт говорил на двух языках удаления. У целей, активов, обязательств, операций и
бюджетов удаление мягкое И обратимое: есть `restore`-эндпоинт и отмена в интерфейсе.
У снимков плана мягкое удаление БЫЛО (`is_deleted`/`deleted_at` заполняются), а
восстановления не было — то есть данные лежали в базе, но вернуть их пользователь не мог
никак. Это худший из трёх возможных вариантов: не «удалили насовсем» и не «можно
вернуть», а «сказали, что удалили, а на деле спрятали».

Схема при этом менять не понадобилось: колонки уже есть. Первая оценка задачи в ROADMAP
называла её «изменением схемы с матрицей SQLite+PostgreSQL» — сверка с диском показала,
что это неверно, оценка исправлена.
"""
from __future__ import annotations

import pytest


def _register(client, email: str = "restore@test.io") -> None:
    client.post(
        "/api/auth/register",
        json={"email": email, "password": "password123", "consent": True},
    )
    client.post("/api/consents/financial_data")


def _save_snapshot(client) -> int:
    response = client.post(
        "/api/planning/history",
        json={
            "risk_profile": "balanced",
            "indicators": {"Rt": 1000.0, "Lt": 5000.0, "Dt": 0.2, "BLR": 3.0},
            "best": {
                "name": "A-40-30-30",
                "x_obligations": 0.4,
                "x_reserve": 0.3,
                "x_goals": 0.3,
                "utility": 0.8,
            },
            "top3": [],
            "note": "проверка восстановления",
        },
    )
    assert response.status_code == 200, response.text
    return response.json()["id"]


class TestRestore:
    def test_deleted_snapshot_can_be_restored(self, client) -> None:
        _register(client)
        snapshot_id = _save_snapshot(client)

        client.delete(f"/api/planning/history/{snapshot_id}")
        listed = client.get("/api/planning/history").json()["items"]
        assert snapshot_id not in [s["id"] for s in listed]

        restored = client.post(f"/api/planning/history/{snapshot_id}/restore")
        assert restored.status_code == 200, restored.text
        assert restored.json()["id"] == snapshot_id
        listed = client.get("/api/planning/history").json()["items"]
        assert snapshot_id in [s["id"] for s in listed]

    def test_restored_snapshot_keeps_its_content(self, client) -> None:
        """Восстановление возвращает ТОТ ЖЕ снимок, а не пустую заготовку с тем же id.

        Сверяем с тем, что снимок отдавал ДО удаления, а не с телом запроса на
        сохранение: бэкенд заполняет часть полей сам (`best` считается по портрету,
        а не берётся из запроса), и тест, сверяющий с запросом, проверял бы не
        восстановление, а собственное представление вахты о сохранении.
        """
        _register(client, "restore2@test.io")
        snapshot_id = _save_snapshot(client)
        before = client.get(f"/api/planning/history/{snapshot_id}").json()

        client.delete(f"/api/planning/history/{snapshot_id}")
        restored = client.post(f"/api/planning/history/{snapshot_id}/restore").json()

        assert restored == before
        assert restored["note"] == "проверка восстановления"
        assert restored["indicators"]["Rt"] == pytest.approx(before["indicators"]["Rt"])

    def test_restore_is_idempotent_for_a_live_snapshot(self, client) -> None:
        """Живой снимок восстанавливать нечего — 404, а не молчаливый успех.

        Молчаливый успех на неудалённом объекте прячет ошибку вызывающего: интерфейс
        показал бы «восстановлено» там, где ничего не происходило.
        """
        _register(client, "restore3@test.io")
        snapshot_id = _save_snapshot(client)
        assert client.post(f"/api/planning/history/{snapshot_id}/restore").status_code == 404

    def test_missing_snapshot_is_404(self, client) -> None:
        _register(client, "restore4@test.io")
        assert client.post("/api/planning/history/999999/restore").status_code == 404

    def test_foreign_snapshot_is_not_restorable(self, client) -> None:
        """Чужой снимок не восстанавливается — иначе id становится ключом к чужим данным."""
        _register(client, "owner@test.io")
        snapshot_id = _save_snapshot(client)
        client.delete(f"/api/planning/history/{snapshot_id}")
        client.post("/api/auth/logout")

        _register(client, "stranger@test.io")
        assert client.post(f"/api/planning/history/{snapshot_id}/restore").status_code == 404
