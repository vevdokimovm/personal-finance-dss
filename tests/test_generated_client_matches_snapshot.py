"""Сгенерированный клиент собран из текущего снимка контракта (v9.1.0).

## 🔴 Почему CI падал, а локально было зелено

`tsc` в CI: `Property 'household_id' does not exist on type 'BudgetStatus'`. Локально
та же команда проходила.

Причина — **три артефакта вместо одного источника**:

1. `app/schemas/*.py` — схемы, живут в коде;
2. `docs/api/openapi.json` — снимок, обновляется командой руками;
3. `frontend/src/shared/api/generated/` — клиент, генерируется из снимка.

Правка схемы, не доехавшая до снимка, ломает CI на чистом клоне; правка снимка,
не доехавшая до клиента, ломает его **у следующего разработчика**. Локально
расхождение невидимо: у того, кто правил, все три состояния свежие по очереди,
и он не проходит путь «клонировал → собрал» целиком (тот же класс, что PIT-020).

## Что проверяется

Снимок пересобирается из живого приложения в памяти и сравнивается с файлом на диске.
Расходятся — значит кто-то поменял схему и не обновил снимок; тогда сгенерированный
клиент описывает контракт, которого больше нет.

Сверка идёт по **множеству путей и имён схем**, а не побайтово: порядок ключей в JSON
незначим, и побайтовое сравнение краснело бы на перестановке, ничего не сообщая.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = REPO_ROOT / "docs" / "api" / "openapi.json"
GENERATED_TYPES = REPO_ROOT / "frontend" / "src" / "shared" / "api" / "generated" / "types.gen.ts"


def _normalise(name: str) -> str:
    """Имя схемы в сопоставимом виде.

    🔴 Генератор переименовывает: `AccountDTO` → `AccountDto`, `HTTPValidationError` →
    `HttpValidationError`, `Body_upload_statement_...` → `BodyUploadStatement...`.
    Сравнение буквальных имён давало бы вечно красный гейт на правильном клиенте —
    то есть ровно тот шум, из-за которого проверки снимают целиком.
    """
    return re.sub(r"[^a-z0-9]", "", name.lower())


def _live_spec() -> dict:
    from app.main import app

    return app.openapi()


def _snapshot() -> dict:
    return json.loads(SNAPSHOT.read_text(encoding="utf-8"))


class TestSnapshotMatchesApp:
    """Снимок контракта не отстаёт от кода."""

    def test_paths_match(self) -> None:
        """🔴 Новый или удалённый эндпоинт доехал до снимка.

        Мутация: добавить роут и не пересобрать снимок — падает здесь, а не в CI
        на чужой машине.
        """
        live = set(_live_spec()["paths"])
        stored = set(_snapshot()["paths"])
        assert live == stored, (
            f"снимок отстал от кода. Только в приложении: {sorted(live - stored)}; "
            f"только в снимке: {sorted(stored - live)}. "
            "Пересоберите: python -m tools.api_snapshot.dump_openapi"
        )

    def test_schema_names_match(self) -> None:
        """Список моделей совпадает: новая схема без снимка ломает генерацию клиента."""
        live = set(_live_spec()["components"]["schemas"])
        stored = set(_snapshot()["components"]["schemas"])
        assert live == stored, (
            f"схемы разошлись. Только в приложении: {sorted(live - stored)}; "
            f"только в снимке: {sorted(stored - live)}"
        )

    def test_schema_fields_match(self) -> None:
        """🔴 Поля внутри схем — то, на чём и упал CI.

        Совпадения имён схем мало: `BudgetStatus` существовал в обоих местах,
        а поля `household_id` в снимке не было. `tsc` у того, кто правил, молчал,
        потому что его клиент был собран из свежего снимка; в CI клиент собирается
        из снимка в репозитории.
        """
        live = _live_spec()["components"]["schemas"]
        stored = _snapshot()["components"]["schemas"]
        mismatched: list[str] = []
        for name in sorted(set(live) & set(stored)):
            live_fields = set(live[name].get("properties", {}))
            stored_fields = set(stored[name].get("properties", {}))
            if live_fields != stored_fields:
                missing = sorted(live_fields - stored_fields)
                extra = sorted(stored_fields - live_fields)
                mismatched.append(f"{name}: нет в снимке {missing}, лишнее в снимке {extra}")
        assert not mismatched, "поля схем разошлись со снимком:\n  " + "\n  ".join(mismatched)


class TestGeneratedClientMatchesSnapshot:
    """Клиент собран из того снимка, что лежит в репозитории."""

    def test_every_schema_has_a_generated_type(self) -> None:
        """🔴 Клиент знает все модели снимка.

        Клиент в репозитории — не артефакт сборки, а исходник: `tsc` в CI проверяет
        именно его. Отставший клиент означает, что фронт компилируется против
        контракта, которого больше нет.
        """
        if not GENERATED_TYPES.exists():
            return  # клиент не сгенерирован в этом окружении — проверит CI
        source = GENERATED_TYPES.read_text(encoding="utf-8")
        declared = {
            _normalise(name)
            for name in re.findall(r"^export type ([A-Za-z0-9_]+) =", source, re.MULTILINE)
        }
        missing = [
            name for name in _snapshot()["components"]["schemas"]
            if _normalise(name) not in declared
        ]
        assert not missing, (
            f"в сгенерированном клиенте нет типов: {missing}. "
            "Пересоберите: cd frontend && npm run generate:client"
        )
