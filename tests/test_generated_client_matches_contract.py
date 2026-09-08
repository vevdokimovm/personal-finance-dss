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


def _type_bodies(types: str) -> dict[str, str]:
    """Тело каждого объявленного типа — от `export type X = {` до закрывающей скобки.

    🔴 Нужно, потому что первая редакция искала свойство по ВСЕМУ файлу и не знала,
    в какой оно схеме. Практический эффект: поле `amount`, добавленное в новую схему,
    находилось в десятке уже существующих типов, и гейт оставался зелёным. Инцидент
    08.09.2026 он поймал только потому, что имя `is_current` оказалось уникальным;
    для `id`, `name`, `status`, `amount` — то есть для большинства новых полей —
    он был слеп. Найдено третьим проходом независимого аудита.
    """
    bodies: dict[str, str] = {}
    for match in re.finditer(r"(?m)^export type (\w+) = \{", types):
        # 🔴 Скобки внутри строковых литералов пропускаются: `literal: "{";` уводил
        # конец тела за настоящую `};`, и тип забирал поля СЛЕДУЮЩЕГО за собой.
        # Найдено собственным зондом на искусственном образце.
        depth, i, quote = 0, match.end() - 1, ""
        while i < len(types):
            ch = types[i]
            if quote:
                if ch == quote and types[i - 1] != "\\":
                    quote = ""
            elif ch in "'\"":
                quote = ch
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        body = types[match.end():i]
        # 🔴 Ключ — имя ИЗ КОНТРАКТА, а не имя типа в TypeScript. Генератор
        # нормализует регистр (`AccountDTO` → `AccountDto`), и сверка по имени типа
        # объявила бы «типа нет в клиенте» для трети схем. Исходное имя генератор
        # сохраняет в doc-комментарии прямо над объявлением — по нему и связываем.
        # 🔴 Имя берётся из СВОЕГО doc-блока и ПЕРВОЙ его строки. Прежняя редакция
        # смотрела на 300 предшествующих символов и брала последнюю однословную
        # строку: у типа без своего комментария окно захватывало хвост предыдущего
        # блока, где однословные подписи свойств (`* Utility`, `* Granted`) есть.
        # Окно ограничено: срез «весь файл до совпадения» на каждом из сотен типов
        # давал квадратичное копирование, и прогон переставал завершаться вовсе.
        # Окно ограничено: срез «весь файл до совпадения» на каждом из сотен типов
        # давал квадратичное копирование, и прогон переставал завершаться вовсе.
        head = types[max(0, match.start() - 400):match.start()]
        # 🔴 Берётся ПОСЛЕДНИЙ doc-блок окна. Поиск регуляркой с ленивым `.*?` находит
        # самый ЛЕВЫЙ `/**` и растягивается до последнего `*/`, склеивая два соседних
        # комментария в один: имя тогда бралось от предыдущего типа, и телу
        # `Alternative` доставался ключ `AllocationDTO`. Проверено запуском —
        # ошибка была невидима глазами и мгновенна в прогоне.
        opened = head.rfind("/**")
        closed = head.rfind("*/")
        # 🔴 Комментарий засчитывается, только если он ПРИЛЕГАЕТ к объявлению: между
        # его `*/` и `export type` не должно быть ничего, кроме пробелов. Иначе у типа
        # без своего doc-блока именем становилась подпись последнего свойства
        # ПРЕДЫДУЩЕГО типа (` * Pattern`), и `bodies["Pattern"]` держал бы чужое тело —
        # ровно тот класс, что уже дал `Alternative` под именем `AllocationDTO`.
        # Проверено собственным зондом на искусственном образце, а не рассуждением.
        adjacent = (
            opened != -1
            and closed > opened
            and head[closed + 2:].strip() == ""
        )
        block = head[opened:] if adjacent else ""
        declared = re.findall(r"^\s*\* (\w+)\s*$", block, re.MULTILINE)
        schema_name = declared[0] if declared else match.group(1)
        ts_name = match.group(1)
        # 🔴 Одно имя в комментарии могут нести ДВА типа: `ObligationResponse`
        # и `ObligationResponseWritable` (вариант для записи, без readonly-полей).
        # Побеждает тот, чьё имя типа совпадает со схемой, иначе «Writable» затирал бы
        # основной и гейт объявлял бы пропавшими вычисляемые поля, которые на месте.
        if schema_name not in bodies or ts_name == schema_name:
            bodies[schema_name] = body
        bodies.setdefault(ts_name, body)
    return bodies


def _top_level_keys(body: str) -> set[str]:
    """Ключи ВЕРХНЕГО уровня типа — без свойств вложенных объектов.

    🔴 Иначе поле, объявленное внутри инлайнового вложенного объекта (`advice: {`,
    `input_summary: {`, `metrics: {` — таких в клиенте полтора десятка), засчитывалось
    бы как свойство самой схемы. Это остаток того же дефекта, что правился уровнем
    выше: было «ищем по всему файлу», стало «по всему телу типа», должно быть
    «по верхнему уровню тела». Замер 08.09.2026: сегодня таких совпадений ноль —
    правка заводится до того, как они появятся.

    Модификаторы учитываются: ключ печатается как `readonly foo: number` или
    `foo?: string`.
    """
    keys: set[str] = set()
    depth = 0
    for raw in body.splitlines():
        # Скобки внутри строковых литералов не считаются: `literal: "{"` сдвинул бы
        # глубину и спрятал бы все последующие поля типа.
        line = re.sub(r"'[^']*'|\"[^\"]*\"", "", raw)
        if depth == 0:
            match = re.match(r"(?:readonly\s+)?([A-Za-z0-9_]+)\??\s*:", line.strip())
            if match:
                keys.add(match.group(1))
        depth += line.count("{") - line.count("}")
    return keys


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
        bodies = _type_bodies(types)
        missing: list[str] = []
        for schema, props in _snapshot_properties().items():
            # Схемы, которых в клиенте нет вовсе, — отдельная поломка: называем её так.
            body = bodies.get(schema)
            if body is None:
                missing.append(f"{schema} (типа нет в клиенте)")
                continue
            keys = _top_level_keys(body)
            for prop in sorted(props):
                # 🔴 Ключ печатается с модификаторами: `readonly foo: number`,
                # `foo?: string`, `'foo-bar': …`. Первая редакция сетки искала
                # подстроку `    foo:` и объявила пропавшими два поля, которые
                # на месте, — только с префиксом `readonly`. Гейт, кричащий зря,
                # обесценивает себя быстрее, чем молчащий.
                if prop in keys:
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


class TestParserHandlesEdgeCases:
    """🔴 Разбор типов проверен на искусственных образцах, а не только на живом файле.

    Файл переписывался трижды за час, и обе ошибки нашлись **запуском зонда**,
    а не чтением: тип без своего doc-блока получал имя от подписи последнего свойства
    предыдущего типа, а скобка внутри строкового литерала уводила конец тела
    за настоящую `};` — и тип забирал поля следующего за собой.

    На живом `types.gen.ts` ни то, ни другое сегодня не проявляется, поэтому проверка
    на нём молчала бы. Искусственный образец показывает поведение прямо.
    """

    SAMPLE = '''
/**
 * WithString
 */
export type WithString = {
    /**
     * Pattern
     */
    pattern: string;
    literal: "{";
    nested: {
        inner: number;
    };
    after: number;
};

export type NoDoc = {
    plain: number;
};
'''

    def test_body_stops_at_its_own_closing_brace(self) -> None:
        keys = _top_level_keys(_type_bodies(self.SAMPLE)["WithString"])
        assert "plain" not in keys, "тело уехало за свою `};` — забраны поля соседа"
        assert {"pattern", "literal", "after"} <= keys

    def test_nested_object_fields_are_not_top_level(self) -> None:
        keys = _top_level_keys(_type_bodies(self.SAMPLE)["WithString"])
        assert "nested" in keys
        assert "inner" not in keys, "поле вложенного объекта засчитано как своё"

    def test_type_without_doc_block_keeps_its_own_name(self) -> None:
        bodies = _type_bodies(self.SAMPLE)
        assert "NoDoc" in bodies
        assert "Pattern" not in bodies, (
            "именем типа стала подпись свойства предыдущего блока"
        )

    def test_doc_name_wins_when_block_is_adjacent(self) -> None:
        """А прилегающий комментарий по-прежнему даёт имя из контракта."""
        assert "WithString" in _type_bodies(self.SAMPLE)
