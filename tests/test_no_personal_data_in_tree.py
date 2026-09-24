"""Персональные данные не лежат в дереве репозитория — сквозной гейт.

## Чем отличается от `test_no_secrets_in_repo.py`

Тот гейт (v9.1.0) закрывает **секреты** — токены, ключи, строки подключения — и смотрит
на восемь каталогов кода: `app`, `tests`, `tools`, `scripts`, `docs`, `nginx`, `alembic`,
`deploy`. Задача владельца П1 требовала другого: «личные данные не утекают», **сквозным**
проходом по дереву, включая материалы, логи и фикстуры.

🔴 **Разница в охвате оказалась не формальной.** Первый же сквозной проход нашёл
в `knowledge/survey_auditory/raw/` **27 живых почтовых адресов** респондентов опроса —
gmail, mail.ru, yandex. Прежний гейт этого не видел **по построению**: `knowledge/`
не входил в список каталогов. Отсутствие красного означало отсутствие проверки,
а не отсутствие данных — тот же класс, что `PIT-032`.

## 🔴 Почему эти адреса всё-таки остаются в репозитории

**Решение владельца 06.09.2026, дословно:** «опрос только не трогай, эти данные нужны
потом первых пользователей зазывать».

Респонденты — будущая первая аудитория продукта, и адрес здесь не побочный след,
а рабочий актив: 385 человек, уже ответивших на 62 вопроса о личных финансах, — это
готовый список для запуска. Обезличить его значит уничтожить то, ради чего опрос
и проводился.

Поэтому файл занесён в `PERSONAL_DATA_EXCEPTIONS` — **названным исключением с причиной**,
а не молчаливым пропуском. Разница существенная: исключение видно в коде, ограничено
одним путём и разбирается при следующей ревизии; расширение списка пропусков без причины
превращает гейт в украшение.

**Что из этого следует для деплоя (не закрыто здесь):** к моменту запуска у этих адресов
должно быть правовое основание обработки по 152-ФЗ — согласие респондента на связь,
а не только на участие в опросе. Пункт для юридического блока вехи 9.

## 🔴 Что изменилось в v9.13.3 (ВЛ-29)

Гейт судил всё дерево одинаково и потому требовал чистить **первичный материал
исследований**, который правило §9 велит хранить дословно, а правило §7 разрешает
хранить прямо в репозитории. Решение владельца 24.09.2026 — разделить по контуру:
публикуемый файл роняет прогон, внутренний даёт предупреждение. Граница берётся
из публикатора (`tests/support/publication_scope.py`), а не переписана сюда.

## Почему гейт нужен, хотя публикатор данные не пропускает

`tools/publish/finpilot_publish_public.sh` собирает зеркало по **белому списку**
(`ALLOW_DIRS`), и `knowledge/` в нём нет. Белый список — правильная конструкция,
и он держит границу наружу. Но не единственную:

- **чекпоинт-архив** пакует рабочее дерево целиком и лежит в `~/Developer`, откуда
  переезжает между аккаунтами владельца;
- **белый список расширяется одной строкой**, и тогда данные уедут молча.

Гейт стережёт появление **новых** персональных данных где угодно в дереве — там,
где никакого белого списка нет.

## Что считается персональными данными здесь

Почта на живом почтовом сервисе, российский телефон, СНИЛС, номер паспорта. Каждый
паттерн проверяет сам себя на своих же примерах (`TestGateItselfWorks`): гейт, который
ничего не находит, неотличим от сломанного, пока не потребовать от него находить заведомое.
"""
from __future__ import annotations

import re
import warnings
from pathlib import Path

import pytest

from tests.support.publication_scope import is_published

REPO_ROOT = Path(__file__).resolve().parents[1]

# 🔴 ВЛ-29, решение владельца 24.09.2026 («сделай зелёными», вариант 3).
# Одинаковая строгость ко всему дереву противоречила правилу §7 `CLAUDE.md`:
# опубликованные в интернете материалы разрешено хранить и анализировать ВНУТРИ
# репозитория, и единственный инвариант — наружу ничего не уходит. Поэтому:
#
#   - файл уезжает в зеркало  → находка ВАЛИТ прогон (как и было);
#   - файл остаётся внутри    → находка печатается предупреждением.
#
# Граница не выписана здесь константой, а считана из публикатора
# (`tests/support/publication_scope.py`) — копия белого списка разошлась бы молча.
# Чистка самого корпуса запрещена правилом §9: первичный материал хранится дословно.

# Сквозной проход: не список каталогов, а всё дерево минус заведомо чужое.
# 🔴 Именно поэтому гейт находит то, чего не находил прежний: список каталогов
# нельзя забыть расширить, если списка нет.
SKIP_DIRS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__", "dist", "build",
    ".pytest_cache", ".mypy_cache", ".hypothesis", ".ruff_cache", ".tanstack",
    "generated", "coverage", "playwright-report", "test-results", "blob-report",
    "__screenshots__", "site-packages",
    "_base",  # зеркало base-repo: чужая репа со своими гейтами
}
SKIP_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".pdf", ".zip", ".gz",
    ".woff", ".woff2", ".ttf", ".drawio", ".xlsx", ".docx", ".pptx",
    ".lock", ".map",
}
# Файлы, которым положено содержать разметку персональных данных: сам этот гейт
# и его сосед по секретам. Иначе проверка находит собственные примеры.
SKIP_FILES = {"test_no_personal_data_in_tree.py", "test_no_secrets_in_repo.py"}

# 🔴 Журнал хука `audit-log.sh`: он записывает КАЖДУЮ команду агента дословно,
# включая примеры адресов из этого самого гейта. Нашлось мутационной проверкой —
# сразу после того, как гейт был написан, он покраснел бы на собственных примерах.
# Файл закрыт `.gitignore` и в репозиторий не уезжает; здесь он исключён из прохода,
# потому что его содержимое не редактируется — оно накапливается само.
SKIP_PATHS = {"logs/agent-audit.jsonl"}

# 🔴 Названные исключения — по одному пути, каждое с причиной в этой же строке.
# Список ведётся руками намеренно: молчаливый пропуск по маске превратил бы гейт
# в украшение, а строка с причиной разбирается при следующей ревизии.
PERSONAL_DATA_EXCEPTIONS = {
    "knowledge/survey_auditory/raw/survey_responses_385.xlsx.md":
        "решение владельца 06.09.2026: адреса респондентов — список первой аудитории "
        "для запуска, обезличивание уничтожает смысл опроса. К деплою нужно правовое "
        "основание связи по 152-ФЗ (пункт юридического блока вехи 9)",
}

# Домены, на которых адрес заведомо выдуман: RFC 2606 плюс наши тестовые.
FAKE_DOMAINS = frozenset({
    "example.com", "example.org", "example.net", "example.ru",
    "test.io", "fp.io", "pwd.io", "invalid", "localhost",
    "finpilot.app", "finpilot.ru", "test.com", "mail.test",
    "redacted.invalid",
})
# Живые почтовые сервисы: адрес на таком домене принадлежит человеку.
LIVE_MAIL_DOMAINS = frozenset({
    "gmail.com", "mail.ru", "yandex.ru", "yandex.com", "list.ru",
    "inbox.ru", "bk.ru", "rambler.ru", "icloud.com", "outlook.com",
    "hotmail.com", "yahoo.com",
})

EMAIL = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
PHONE_RU = re.compile(r"(?:\+7|\b8)[ \-]?\(?9\d{2}\)?[ \-]?\d{3}[ \-]?\d{2}[ \-]?\d{2}\b")
SNILS = re.compile(r"\b\d{3}-\d{3}-\d{3} \d{2}\b")
PASSPORT_RU = re.compile(r"\b\d{2} \d{2} \d{6}\b")


def _scanned_files() -> list[Path]:
    files: list[Path] = []
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file() or path.name in SKIP_FILES:
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix in SKIP_SUFFIXES:
            continue
        relative = str(path.relative_to(REPO_ROOT))
        if relative in PERSONAL_DATA_EXCEPTIONS or relative in SKIP_PATHS:
            continue
        files.append(path)
    return files


def _split_by_scope(offenders: list[str]) -> tuple[list[str], list[str]]:
    """Разложить находки на публикуемые (жёстко) и внутренние (мягко)."""
    published = sorted(name for name in offenders if is_published(name))
    internal = sorted(name for name in offenders if not is_published(name))
    return published, internal


def _warn_about_corpus(kind: str, internal: list[str]) -> None:
    """Внутренняя находка не роняет прогон, но и не молчит.

    Молчание превратило бы гейт в украшение: следующая вахта не отличила бы
    «корпус чист» от «корпус не проверяется».
    """
    if internal:
        warnings.warn(
            f"{kind}: {len(internal)} файл(ов) во внутреннем контуре — "
            f"{', '.join(internal[:5])}"
            + (f" и ещё {len(internal) - 5}" if len(internal) > 5 else "")
            + " (правило §7: хранить можно, наружу не уходит)",
            UserWarning,
            stacklevel=2,
        )


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return ""


def _is_personal_email(address: str) -> bool:
    """Адрес принадлежит живому человеку, а не примеру в документации.

    🔴 Проверка идёт по домену, а не по локальной части: `anna@example.com`
    в тесте безопасен, `anna@gmail.com` в материалах — нет, и отличить их
    по имени невозможно.

    Отдельно разрешён `edu.misis.ru`: это авторский контакт в научных статьях,
    уже опубликованных в журналах. Автор указывает свою почту сам и намеренно —
    это атрибуция, а не утечка.
    """
    domain = address.rsplit("@", 1)[-1].lower()
    if domain in FAKE_DOMAINS or domain == "edu.misis.ru":
        return False
    return domain in LIVE_MAIL_DOMAINS


class TestNoPersonalDataInTree:
    """Сквозной проход по дереву."""

    def test_no_live_email_addresses(self) -> None:
        """🔴 Почта на живом домене = персональные данные конкретного человека.

        Мутация: добавить адрес респондента в любой файл вне исключений — падает
        здесь с именем файла и числом адресов.
        """
        offenders: dict[str, int] = {}
        for path in _scanned_files():
            found = {a for a in EMAIL.findall(_read(path)) if _is_personal_email(a)}
            if found:
                offenders[str(path.relative_to(REPO_ROOT))] = len(found)
        published, internal = _split_by_scope(list(offenders))
        _warn_about_corpus("живые почтовые адреса", internal)
        assert not published, (
            "в ПУБЛИКУЕМЫХ файлах лежат живые почтовые адреса — это уедет наружу:\n  "
            + "\n  ".join(f"{name}: {offenders[name]} шт." for name in published)
            + "\nОбезличить в источнике либо занести путь в PERSONAL_DATA_EXCEPTIONS "
              "С ПРИЧИНОЙ: фильтр публикатора закрывает один путь наружу, "
              "а чекпоинт-архив — другой."
        )

    @pytest.mark.parametrize(
        ("name", "pattern"),
        [("телефон", PHONE_RU), ("СНИЛС", SNILS), ("паспорт", PASSPORT_RU)],
    )
    def test_no_identifier_of_kind(self, name: str, pattern: re.Pattern) -> None:
        """Российские идентификаторы физлица не встречаются нигде в дереве."""
        offenders = [
            str(p.relative_to(REPO_ROOT)) for p in _scanned_files() if pattern.search(_read(p))
        ]
        published, internal = _split_by_scope(offenders)
        _warn_about_corpus(name, internal)
        assert not published, f"{name} найден в публикуемых файлах: {published}"


class TestExceptionsAreDisciplined:
    """🔴 Исключения не расползаются.

    Список пропусков — самая уязвимая часть любого гейта: он растёт молча, каждый
    раз по уважительной причине, и в какой-то момент перестаёт что-либо проверять.
    Проверки ниже требуют, чтобы у каждого исключения был живой путь и внятная причина.
    """

    def test_every_exception_points_at_an_existing_file(self) -> None:
        """Исключение для файла, которого нет, — мёртвая строка, скрывающая соседа."""
        missing = [name for name in PERSONAL_DATA_EXCEPTIONS if not (REPO_ROOT / name).exists()]
        assert not missing, f"исключения ссылаются на несуществующие файлы: {missing}"

    def test_every_exception_states_a_reason(self) -> None:
        """Причина, а не пустая строка: без неё следующая ревизия не сможет судить."""
        thin = [name for name, why in PERSONAL_DATA_EXCEPTIONS.items() if len(why) < 40]
        assert not thin, f"у исключений нет внятной причины: {thin}"

    def test_exceptions_stay_few(self) -> None:
        """Порог намеренно низкий: рост списка — повод для разговора, а не для правки.

        Гейт с длинным списком исключений измеряет длину списка, а не чистоту дерева.
        """
        assert len(PERSONAL_DATA_EXCEPTIONS) <= 3, (
            f"исключений стало {len(PERSONAL_DATA_EXCEPTIONS)} — гейт превращается "
            "в список того, что решили не проверять"
        )


class TestGateItselfWorks:
    """🔴 Гейт, который ничего не находит, неотличим от сломанного."""

    @pytest.mark.parametrize(
        "address", ["ivan.petrov@gmail.com", "user@mail.ru", "a.b@yandex.ru"]
    )
    def test_live_addresses_are_recognised(self, address: str) -> None:
        assert EMAIL.fullmatch(address)
        assert _is_personal_email(address)

    @pytest.mark.parametrize(
        "address", ["anna@example.com", "owner@test.io", "x@redacted.invalid"]
    )
    def test_placeholders_are_ignored(self, address: str) -> None:
        assert not _is_personal_email(address)

    def test_author_contact_is_allowed(self) -> None:
        """Авторская почта в научных статьях — атрибуция, а не утечка."""
        assert not _is_personal_email("m2201058@edu.misis.ru")

    # 🔴 Образцы названы `EXAMPLE_*` не для красоты: соседний гейт
    # (`test_no_secrets_in_repo.py`) ищет телефоны в `tests/` и считает
    # заглушкой то, рядом с чем стоит слово example. Без этого два гейта
    # ловят друг друга — и падает тот, кто просто написан вторым.
    EXAMPLE_PHONE = "+7 916 123 45 67"
    EXAMPLE_SNILS = "112-233-445 95"
    EXAMPLE_PASSPORT = "45 08 123456"

    @pytest.mark.parametrize(
        ("pattern", "sample"),
        [
            (PHONE_RU, EXAMPLE_PHONE),
            (SNILS, EXAMPLE_SNILS),
            (PASSPORT_RU, EXAMPLE_PASSPORT),
        ],
    )
    def test_identifier_patterns_match_their_examples(
        self, pattern: re.Pattern, sample: str
    ) -> None:
        assert pattern.search(sample)

    def test_tree_walk_reaches_materials_and_code(self) -> None:
        """🔴 Проход действительно доходит до материалов.

        Прежний гейт был зелёным именно потому, что не смотрел в `knowledge/`.
        Проверка охвата важнее проверки паттернов: паттерн, которому нечего читать,
        зелёный при любом содержимом.
        """
        scanned = {p.relative_to(REPO_ROOT).parts[0] for p in _scanned_files()}
        for expected in ("knowledge", "app", "frontend", "docs"):
            assert expected in scanned, f"сквозной проход не доходит до {expected}/"


class TestScopeSplitIsHonest:
    """🔴 Мягкость ограничена внутренним контуром и не молчит.

    Разделение на жёсткое и мягкое — самый опасный вид послабления: оно выглядит
    как работающий гейт, пока не окажется, что мягкими стали все находки сразу.
    Поэтому проверяется и то, что публикуемое осталось жёстким, и то, что
    внутреннее всё-таки сообщается.
    """

    def test_published_finding_stays_hard(self) -> None:
        published, internal = _split_by_scope(
            ["app/main.py", "docs/research/raw/corpus.md"]
        )
        assert published == ["app/main.py"]
        assert internal == ["docs/research/raw/corpus.md"]

    def test_corpus_finding_is_warned_not_swallowed(self) -> None:
        with pytest.warns(UserWarning, match="внутреннем контуре"):
            _warn_about_corpus("телефон", ["docs/research/raw/corpus.md"])

    def test_clean_corpus_is_silent(self) -> None:
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            _warn_about_corpus("телефон", [])

    def test_corpus_really_is_outside_the_contour(self) -> None:
        """Опора всего послабления: корпус действительно не уезжает наружу.

        Мутация «добавить `docs/research` в белый список публикатора» роняет тест
        здесь — послабление обязано отвалиться вместе с основанием.
        """
        assert not is_published("docs/research/raw/bank_statement_corpus_2026-09-17.md")
