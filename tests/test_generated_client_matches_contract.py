"""Сгенерированный TS-клиент не отстаёт от снимка контракта.

## Что закрывает

Клиент (`frontend/src/shared/api/generated/`) лежит в репозитории и собирается из
`docs/api/openapi.json`. CI прогоняет `npm run generate:client` **перед** typecheck,
но не сверяет результат с закоммиченным — то есть шаг, подписанный «контроль дрейфа
от openapi.json», дрейф закоммиченного файла не ловил вовсе.

🔴 **Поймано на живом случае, 08.09.2026.** Поля `is_current` и `current_version` были
добавлены в `ConsentState`, снимок контракта перегенерирован, а TS-клиент — нет.
CHANGELOG при этом утверждал «контракт перегенерирован», и утверждение было верным
ровно наполовину. Фронт не увидел бы новых полей, даже собираясь тянуть их.

Класс тот же, что `test_readme_status_is_current.py`: рядом стоял зелёный гейт,
и потому соседнюю строку никто не читал.

## Что гейт проверяет

Каждое свойство каждой схемы снимка присутствует в сгенерированных типах. Это не
полная сверка форм (типы, обязательность, вложенность) — она потребовала бы своего
генератора. Но пропажу поля, а это и есть наблюдавшийся дрейф, ловит механически.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = REPO_ROOT / "docs" / "api" / "openapi.json"
TYPES = REPO_ROOT / "frontend" / "src" / "shared" / "api" / "generated" / "types.gen.ts"


def _declares(types: str, prop: str) -> bool:
    """Объявлено ли свойство в типах — с любыми модификаторами перед именем."""
    return re.search(rf"(?m)^\s*(?:readonly\s+)?{re.escape(prop)}\??\s*:", types) is not None


def _snapshot_properties() -> dict[str, set[str]]:
    schemas = json.loads(SNAPSHOT.read_text(encoding="utf-8"))["components"]["schemas"]
    return {
        name: set(body.get("properties", {}))
        for name, body in schemas.items()
        if body.get("properties")
    }


class TestEveryContractFieldReachedTheClient:
    """Ни одно поле снимка не потерялось по дороге в типы."""

    def test_no_property_is_missing(self) -> None:
        """🔴 Мутация «откатить types.gen.ts» роняет тест здесь.

        Сообщение называет схему и поле: общее «клиент устарел» не даёт
        следующего шага, а `npm run generate:client` даёт.
        """
        types = TYPES.read_text(encoding="utf-8")
        missing: list[str] = []
        for schema, props in _snapshot_properties().items():
            for prop in sorted(props):
                # 🔴 Ключ печатается с модификаторами: `readonly foo: number`,
                # `foo?: string`, `'foo-bar': …`. Первая редакция сетки искала
                # подстроку `    foo:` и объявила пропавшими два поля, которые
                # на месте, — только с префиксом `readonly`. Гейт, кричащий зря,
                # обесценивает себя быстрее, чем молчащий.
                if _declares(types, prop):
                    continue
                missing.append(f"{schema}.{prop}")
        assert not missing, (
            "поля снимка контракта не доехали до сгенерированного клиента: "
            + ", ".join(missing[:15])
            + (f" и ещё {len(missing) - 15}" if len(missing) > 15 else "")
            + " — выполните `npm run generate:client` во `frontend/`"
        )


class TestGateItselfWorks:
    """Сетка смотрит на реальные файлы, а не молчит на пустом месте."""

    def test_snapshot_has_schemas(self) -> None:
        props = _snapshot_properties()
        assert len(props) > 50, f"в снимке подозрительно мало схем: {len(props)}"

    def test_types_file_is_substantial(self) -> None:
        assert TYPES.exists(), "сгенерированные типы отсутствуют"
        assert len(TYPES.read_text(encoding="utf-8")) > 10_000
