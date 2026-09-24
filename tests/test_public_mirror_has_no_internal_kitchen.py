"""Внутренняя кухня разработки не уезжает в публичное зеркало.

## Что закрывает

`tools/publish/finpilot_publish_public.sh` собирает зеркало по белому списку, и в нём
есть `app`, `tests`, `frontend`, `scripts`, `.github` — целиком. Три сетки на выходе
ловят имена файлов (`DENY_NAME_PATTERNS`), секреты (`SECRET_PATTERNS`) и имя владельца
с названием приватного репозитория (`NAME_RE`).

🔴 **Четвёртой сетки не было, и мимо трёх существующих проходит внутренняя кухня.**
Замер 08.09.2026: **35 файлов** в публикуемых каталогах несут дословные решения
владельца, ссылки на вахтенный журнал и разборы инцидентов — и ни один из них не
содержит имени владельца, поэтому `NAME_RE` их не видит.

Худший случай нашёлся сразу: `tests/test_no_personal_data_in_tree.py` **публично
называет каталог, где лежат 27 живых почтовых адресов респондентов**, и цитирует
решение владельца их сохранить. Публикация этого файла — не утечка самих адресов,
а указатель на них: она сообщает всем, что персональные данные в приватном
репозитории есть, где именно и почему их не удалили.

## Почему это не педантизм

Тот же стандарт **уже принят** в самом публикаторе — для текста релиза:
`NOTES_RE` объявляет `WATCHLOG|вахт|аккаунт|Claude|клод` неуместным в публичном
описании и валит сборку. Здесь ровно та же лексика применяется к дереву, куда она
попадает гораздо чаще: в релизных заметках десяток строк, а в коде — тысячи.

## Проверено на живом зеркале, а не выведено

`tests/test_dataset_export.py` **уже опубликован** со словом «вахта» (проверено через
GitHub API 08.09.2026). Тяжёлый случай пока латентен: зеркало отставало от репозитория,
и файл про 27 адресов туда ещё не доехал — то есть гейт заводится ДО происшествия,
а не после.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from tests.support.publication_scope import is_published

REPO_ROOT = Path(__file__).resolve().parents[1]

# Каталоги, которые публикатор копирует в зеркало целиком (`ALLOW_DIRS`).
PUBLISHED_DIRS = ("app", "tests", "frontend/src", "scripts", ".github")

SKIP_PARTS = {"node_modules", "__pycache__", "dist", "build", ".pytest_cache", "generated"}
TEXT_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".yml", ".yaml", ".sh", ".css", ".sql"}

# 🔴 Лексика внутренней кухни. Первые две группы — приватный разговор и внутренний
# процесс; они не имеют публичного смысла вовсе. Третья — указатели на реестры,
# которых в зеркале нет: ссылка в никуда плюс каталог прошлых дефектов.
INTERNAL_PATTERNS: dict[str, re.Pattern[str]] = {
    # 🔴 Сетка ловит ЦИТАТУ, а не сам факт решения. «Решение владельца» без кавычек —
    # обычная продуктовая лексика (product owner decided X) и публичному читателю
    # ничего лишнего не сообщает. Опасна дословная выдержка из приватного разговора:
    # она публикует чужую речь, а не проектное решение. Первая редакция сетки ловила
    # оба случая разом и требовала править 21 файл, из которых 20 были в порядке.
    "дословная цитата приватного разговора": re.compile(
        r"дословно[:,]?\s*[«\"]|владельц[аеу][^\n]{0,40}дословно", re.IGNORECASE
    ),
    "вахтенный журнал и вахта": re.compile(r"WATCHLOG|вахт[аеуойы]", re.IGNORECASE),
    "имя ассистента": re.compile(r"\bClaude\b|клод", re.IGNORECASE),
}

# Файлы, которым лексика нужна по существу: они САМИ про эту границу.
# Исключение названо и ограничено путём — как в `test_no_personal_data_in_tree.py`.
EXCEPTIONS: dict[str, str] = {
    "tests/test_public_mirror_has_no_internal_kitchen.py": (
        "сам гейт: перечисляет запрещённую лексику, иначе не может её искать"
    ),
    "tests/test_no_personal_data_in_tree.py": (
        "не публикуется вовсе: занесён в DENY_NAME_PATTERNS публикатора — по построению "
        "называет каталог с живыми ПДн, и это его рабочие данные, а не оплошность"
    ),
    "scripts/setup_claude_code_plugins.sh": (
        "не публикуется вовсе: rsync-исключение плюс DENY_NAME_PATTERNS — "
        "внутренний тулинг рабочей станции, к продукту отношения не имеет"
    ),
}

PUBLISHER = REPO_ROOT / "tools/publish/finpilot_publish_public.sh"

# Исключения, оправданные тем, что файл не публикуется: утверждение проверяемое,
# и оно проверяется — иначе «не публикуется» становится обещанием на словах.
DENIED_BY_PUBLISHER = (
    "tests/test_no_personal_data_in_tree.py",
    "scripts/setup_claude_code_plugins.sh",
)


# Граница «уедет / не уедет» считается ОДНИМ модулем на все гейты:
# `tests/support/publication_scope.py` разбирает белые списки публикатора и применяет
# два механических правила отсева внутри `tests/` — тест внутреннего инструмента
# (ссылка на `tools.`) и тест хука рабочей станции (ссылка на `.claude`). Оба предмета
# в зеркале отсутствуют, значит тест на них — ссылка в никуда. Прежде правило жило
# копией регулярки здесь и списком имён в `EXCEPTIONS`; копия расходилась молча.


def _published_files() -> list[Path]:
    found: list[Path] = []
    for rel in PUBLISHED_DIRS:
        root = REPO_ROOT / rel
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
                continue
            if SKIP_PARTS & set(path.relative_to(REPO_ROOT).parts):
                continue
            # 🔴 Один источник границы на все гейты: белые списки публикатора
            # плюс механический отсев внутри `tests/` (инструменты и хуки).
            if not is_published(str(path.relative_to(REPO_ROOT))):
                continue
            found.append(path)
    return found


def _offenders(pattern: re.Pattern[str]) -> list[str]:
    hits: list[str] = []
    for path in _published_files():
        rel = str(path.relative_to(REPO_ROOT))
        if rel in EXCEPTIONS:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if pattern.search(text):
            hits.append(rel)
    return sorted(hits)


class TestPublishedTreeIsFreeOfInternalKitchen:
    """Публикуемое дерево не рассказывает постороннему про внутреннюю кухню."""

    @pytest.mark.parametrize(("what", "pattern"), sorted(INTERNAL_PATTERNS.items()))
    def test_no_internal_vocabulary(self, what: str, pattern: re.Pattern[str]) -> None:
        """🔴 Мутация «вернуть цитату владельца в докстринг» роняет этот тест.

        Сообщение называет конкретные файлы: общее «в дереве внутрянка» не даёт
        ни одного следующего шага.
        """
        offenders = _offenders(pattern)
        assert not offenders, (
            f"в публикуемых каталогах осталась внутренняя кухня ({what}): "
            f"{', '.join(offenders[:12])}"
            + (f" и ещё {len(offenders) - 12}" if len(offenders) > 12 else "")
            + " — это уедет в публичное зеркало при следующей публикации"
        )

    def test_no_pointer_to_where_personal_data_lives(self) -> None:
        """🔴 Публикуемый файл не называет каталог с живыми персональными данными.

        Указатель опаснее самих данных не потому, что данные менее ценны, а потому,
        что он публичен и адресует их точно: «в приватной репе есть ПДн, вот где».
        """
        pattern = re.compile(r"survey_auditory|живых почтовых адрес|живые адрес")
        offenders = [f for f in _offenders(pattern) if f != Path(__file__).name]
        assert not offenders, (
            "публикуемый файл называет, где лежат живые персональные данные: "
            f"{', '.join(offenders)}"
        )


class TestExceptionsAreDisciplined:
    """Исключения названы, обоснованы и не разрастаются."""

    def test_every_exception_points_at_an_existing_file(self) -> None:
        missing = [rel for rel in EXCEPTIONS if not (REPO_ROOT / rel).exists()]
        assert not missing, f"исключение указывает на несуществующий файл: {missing}"

    def test_every_exception_states_a_reason(self) -> None:
        empty = [rel for rel, why in EXCEPTIONS.items() if len(why.strip()) < 20]
        assert not empty, f"исключение без внятной причины: {empty}"

    def test_files_claimed_unpublished_are_really_denied(self) -> None:
        """🔴 «Не публикуется» — проверяемое утверждение, а не обещание.

        Исключение вида «файл всё равно не уедет» держится на строке в публикаторе.
        Уберут строку — исключение станет дырой, и заметить это будет нечем.
        Мутация «снять имя из DENY_NAME_PATTERNS» роняет тест здесь.
        """
        script = PUBLISHER.read_text(encoding="utf-8")
        for rel in DENIED_BY_PUBLISHER:
            name = Path(rel).name
            assert f"'{name}'" in script, (
                f"{rel} исключён как «не публикуется», но публикатор его не запрещает — "
                "исключение держится на словах"
            )

    def test_publisher_really_drops_tests_of_workstation_hooks(self) -> None:
        """🔴 Тест хука рабочей станции в зеркало не уезжает — и это механизм.

        Хуки живут в `.claude/`: контура рабочей станции в зеркале нет вовсе, значит
        и тестам его там делать нечего. До v9.13.3 это держалось на списке имён
        в `EXCEPTIONS`: каждый новый хук добавлял строку, а забытая строка давала
        красный гейт на ровном месте — ровно так и вышло с тремя тестами гейтов
        поиска (ВЛ-29). Теперь правило считается по факту ссылки, как и для `tools/`.
        """
        script = PUBLISHER.read_text(encoding="utf-8")
        assert ".claude" in script, (
            "публикатор больше не отсекает тесты хуков рабочей станции, "
            "а гейт считает, что отсекает"
        )
        for name in ("test_watch_identity_hook.py", "test_exa_gate_hook.py"):
            assert not is_published(f"tests/{name}"), f"{name} снова считается публикуемым"

    def test_publisher_really_drops_tests_of_internal_tooling(self) -> None:
        """🔴 Правило «предмет не публикуется — тест тоже» держится на публикаторе.

        Гейт пропускает эти файлы **потому, что** публикатор их отсекает. Уберут
        механизм — гейт начнёт молча прощать целую пачку файлов, и заметить будет
        нечем. Поэтому механизм проверяется здесь, а не подразумевается.
        """
        script = PUBLISHER.read_text(encoding="utf-8")
        assert "collect_internal_tool_tests" in script, (
            "публикатор больше не отсекает тесты внутренних инструментов, "
            "а гейт всё ещё считает, что отсекает"
        )
        assert "${extra_excludes[@]}" in script, (
            "функция отбора есть, но её результат не подставляется в rsync — "
            "список считается и не применяется"
        )

    def test_exceptions_stay_few(self) -> None:
        """Список исключений — не способ погасить гейт.

        Порог намеренно низкий: как только исключений станет больше, дешевле
        починить лексику, чем расширять список.
        """
        assert len(EXCEPTIONS) <= 5, (
            f"исключений {len(EXCEPTIONS)} — гейт превращается в украшение"
        )


class TestGateItselfWorks:
    """Сетка ловит то, ради чего заведена (проверка живости гейта)."""

    @pytest.mark.parametrize(
        ("sample", "key"),
        [
            (
                "Решение владельца 04.09.2026, дословно: «...»",
                "дословная цитата приватного разговора",
            ),
            ("владельца, дословно: «...»", "дословная цитата приватного разговора"),
            ("см. docs/WATCHLOG.md §0", "вахтенный журнал и вахта"),
            ("вахта закрывает батч", "вахтенный журнал и вахта"),
            ("сгенерировано Claude", "имя ассистента"),
        ],
    )
    def test_patterns_match_their_examples(self, sample: str, key: str) -> None:
        assert INTERNAL_PATTERNS[key].search(sample), f"сетка не ловит: {sample}"

    def test_walk_reaches_both_backend_and_frontend(self) -> None:
        """Обход добирается до обоих контуров — иначе зелёный ничего не значит."""
        files = {str(p.relative_to(REPO_ROOT)) for p in _published_files()}
        assert any(f.startswith("app/") for f in files), "обход не дошёл до бэкенда"
        assert any(f.startswith("frontend/src/") for f in files), "обход не дошёл до фронта"
        assert len(files) > 300, f"обход нашёл подозрительно мало файлов: {len(files)}"
