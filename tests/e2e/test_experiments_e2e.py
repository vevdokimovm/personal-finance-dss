"""E2E A/B-экспериментов (P3.5) через реальный HTTP в браузерном контексте.

Полный прод-цикл: админ создаёт эксперимент и запускает → клиент получает вариант (назначение
фиксируется, exposure логируется) → вариант стабилен → результаты показывают назначенного subject.
Браузер для прогона ставится отдельно (`playwright install chromium`); в песочнице CDN браузеров
заблокирован, поэтому спека гоняется на Mac/GitHub CI.
"""
from __future__ import annotations

import time

import pytest

pytestmark = pytest.mark.e2e


def test_ab_experiment_full_cycle(page, base_url) -> None:
    key = f"e2e_exp_{int(time.time() * 1000)}"
    sid = f"e2e-subject-{int(time.time() * 1000)}"

    # админ создаёт эксперимент (в dev ADMIN_API_KEY пуст → доступ открыт) и запускает
    created = page.request.post(f"{base_url}/api/admin/experiments", data={
        "key": key, "name": key, "status": "running",
        "conversion_event": "goal_created",
        "variants": [{"name": "control", "weight": 50}, {"name": "treatment", "weight": 50}],
    })
    assert created.ok, created.text()

    # клиент получает вариант
    first = page.request.get(f"{base_url}/api/experiments/{key}/variant?sid={sid}")
    assert first.ok
    variant = first.json()["variant"]
    assert variant in {"control", "treatment"}

    # назначение зафиксировано: повторный запрос — тот же вариант
    again = page.request.get(f"{base_url}/api/experiments/{key}/variant?sid={sid}")
    assert again.json()["variant"] == variant

    # результаты: subject учтён в своём варианте
    results = page.request.get(f"{base_url}/api/admin/experiments/{key}/results")
    assert results.ok
    body = results.json()
    assigned = {v["variant"]: v["assigned"] for v in body["variants"]}
    assert assigned.get(variant, 0) >= 1
