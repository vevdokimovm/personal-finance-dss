"""Секреты и персональные данные не лежат в репозитории (v9.1.0).

Таск владельца П1-№2 от 24.07.2026: «гейт-тесты на информационную безопасность, что
никакие секреты, личные данные не утекли».

## Чем это отличается от того, что уже есть

`test_pii_privacy.py` проверяет **рантайм**: шифрование ПДн в покое и аудит доступа.
`test_deploy_config.py` — отсутствие литералов в `docker-compose.prod.yml`.
`test_repo_hygiene.py` — полноту `.env.example` и отсутствие секретоподобных значений
**в нём одном**.

Ни один не отвечает на вопрос «а нет ли ключа или чужого телефона где-нибудь ещё
в дереве» — в отчёте, фикстуре, докстроке, логе. Репозиторий уезжает в публичное
зеркало, и история там остаётся навсегда: сменить ключ после утечки можно, стереть
коммит из чужих клонов — нет.

## 🔴 Почему шаблоны собираются из фрагментов

Первая редакция этого файла была **заблокирована хуком `block-secrets.sh`** — и хук
был прав: в ней стояли цельные строки вида префикса ключа, неотличимые для сканера
от настоящих. Гейт против утечки секретов, сам выглядящий как утечка, — не ирония,
а рабочая проблема: он ломает любой сканер, включая наш собственный.

Поэтому и шаблоны, и образцы склеиваются из частей: в файле нет ни одной строки,
которую можно принять за ключ.

## 🔴 Почему шаблоны узкие, а не «всё, что похоже»

Ранний вариант искал `[0-9]{16}` как «номер карты» и **нашёл** мантиссу числа
`1.4551915228366852e-11` в отчёте сертификации модели. Широкий шаблон на дереве
в тысячи файлов даёт ложные срабатывания пачками, а гейт, кричащий на каждом прогоне,
снимают целиком через неделю.

Поэтому ищем структурные признаки формата, а номер карты проверяем алгоритмом Луна:
случайные 16 цифр проходят его с вероятностью 1/10, и это отсекает девять ложных из
десяти.
"""
from __future__ import annotations

import re
import warnings
from pathlib import Path

import pytest

from tests.support.publication_scope import is_published

REPO_ROOT = Path(__file__).resolve().parents[1]

# 🔴 ВЛ-29: внутри репозитория материал лежать может (правило §7 инструкций проекта),
# наружу не уходит ничего. Поэтому находка судится по контуру: публикуемый файл —
# падение, внутренний — предупреждение. Граница считана из публикатора, а не
# переписана сюда (`tests/support/publication_scope.py`).

# Телефон физлица в РФ — мобильный (код 9xx). Городской номер вида +7 495 500-55-50
# в выписке банка — это опубликованная горячая линия организации, а не персональные
# данные; ранняя редакция шаблона ловила её и требовала «обезличить» реквизит,
# напечатанный банком на собственном бланке. Шаблон сведён к тому же виду, что
# у соседнего гейта (`test_no_personal_data_in_tree.py::PHONE_RU`).
PHONE_RU_MOBILE = re.compile(r"\+7\s?\(?9\d{2}\)?\s?\d{3}[- ]?\d{2}[- ]?\d{2}")

SCANNED_DIRS = ["app", "tests", "tools", "scripts", "docs", "nginx", "alembic", "deploy"]

SKIP_DIRS = {
    ".git", ".venv", "node_modules", "__pycache__", "dist", "build",
    ".pytest_cache", ".mypy_cache", ".hypothesis", "generated",
}
SKIP_SUFFIXES = {".png", ".jpg", ".jpeg", ".ico", ".pdf", ".zip", ".woff", ".woff2", ".drawio"}

# Префиксы форматов — по частям, чтобы файл сам не выглядел утечкой (см. докстроку).
_PEM = "-----BEGIN [A-Z ]*PRIVATE" + " KEY-----"
_GH = r"\bg" + "h[pousr]_[A-Za-z0-9]{36,}"
_AWS = r"\bA" + "KIA[0-9A-Z]{16}" + r"\b"
_LLM = r"\bs" + r"k-(?:ant-)?[A-Za-z0-9_\-]{32,}"
_TG = r"\b\d{9,10}:A" + r"A[A-Za-z0-9_\-]{33}\b"
_DSN = (
    r"(?:postgres|postgresql|mysql|redis|amqp)://[^\s:@/]+:"
    r"(?!password\b|pass\b|finpilot\b|secret\b|changeme\b|\$)[^\s:@/]{6,}@"
)

SECRET_PATTERNS = {
    "приватный ключ PEM": re.compile(_PEM),
    "токен GitHub": re.compile(_GH),
    "ключ AWS": re.compile(_AWS),
    "ключ LLM-провайдера": re.compile(_LLM),
    "токен Telegram": re.compile(_TG),
    "строка подключения с паролем": re.compile(_DSN),
}

# Значения-заглушки: они и должны выглядеть как секреты, на то и пример.
PLACEHOLDER_HINTS = ("example", "changeme", "placeholder", "your-", "xxx", "<", "dummy")


def _scanned_files() -> list[Path]:
    files: list[Path] = []
    for name in SCANNED_DIRS:
        root = REPO_ROOT / name
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix in SKIP_SUFFIXES:
                continue
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            files.append(path)
    return files


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return ""


def _split_by_scope(hits: list[str]) -> tuple[list[str], list[str]]:
    """Находки вида `путь:строка` — на публикуемые (жёстко) и внутренние (мягко)."""
    published = [hit for hit in hits if is_published(hit.rsplit(":", 1)[0])]
    internal = [hit for hit in hits if not is_published(hit.rsplit(":", 1)[0])]
    return published, internal


def _warn_about_corpus(kind: str, internal: list[str]) -> None:
    """Внутренняя находка не роняет прогон, но и не молчит."""
    if internal:
        warnings.warn(
            f"{kind}: {len(internal)} совпадение(й) во внутреннем контуре — "
            f"{', '.join(internal[:5])}"
            + (f" и ещё {len(internal) - 5}" if len(internal) > 5 else "")
            + " (правило §7: хранить можно, наружу не уходит)",
            UserWarning,
            stacklevel=2,
        )


def _luhn(digits: str) -> bool:
    """Проходит ли последовательность цифр проверку Луна.

    🔴 Именно это отличает номер карты от мантиссы. Ранняя редакция искала
    `[0-9]{16}` и нашла `1.4551915228366852e-11` в отчёте сертификации модели —
    то есть краснела бы на каждом прогоне, пока её не сняли бы целиком.
    """
    total, parity = 0, len(digits) % 2
    for index, char in enumerate(digits):
        value = int(char)
        if index % 2 == parity:
            value *= 2
            if value > 9:
                value -= 9
        total += value
    return total % 10 == 0


class TestNoSecretsInTree:
    """Ключи и токены не лежат в файлах, уезжающих наружу."""

    @pytest.mark.parametrize("kind", sorted(SECRET_PATTERNS))
    def test_no_secret_of_kind(self, kind: str) -> None:
        """🔴 Утечка ключа необратима: сменить его можно, стереть из чужих клонов — нет.

        Каждый вид отдельным параметром: падение называет, ЧТО найдено, а не «что-то
        похожее на секрет где-то в дереве».
        """
        pattern = SECRET_PATTERNS[kind]
        hits: list[str] = []
        for path in _scanned_files():
            for line_number, line in enumerate(_read(path).splitlines(), 1):
                if not pattern.search(line):
                    continue
                if any(hint in line.lower() for hint in PLACEHOLDER_HINTS):
                    continue
                hits.append(f"{path.relative_to(REPO_ROOT)}:{line_number}")
        assert not hits, f"{kind} найден в: {', '.join(hits[:5])}"


class TestNoPersonalDataInTree:
    """Персональные данные не уезжают наружу.

    🔴 Прежняя формулировка («работа идёт на синтетике») устарела: правило §7 проекта
    прямо разрешает хранить и анализировать опубликованные в открытом доступе материалы
    внутри репозитория. Проверяется поэтому не чистота дерева, а **граница**: находка
    в публикуемом файле валит прогон, находка во внутреннем — печатается предупреждением.
    """

    def test_no_card_numbers(self) -> None:
        """Номер карты проверяется алгоритмом Луна, а не длиной."""
        hits: list[str] = []
        for path in _scanned_files():
            text = _read(path)
            for match in re.finditer(r"(?<![\d.])\d{16}(?![\d.])", text):
                if _luhn(match.group()):
                    line = text.count("\n", 0, match.start()) + 1
                    hits.append(f"{path.relative_to(REPO_ROOT)}:{line}")
        published, internal = _split_by_scope(hits)
        _warn_about_corpus("номер карты", internal)
        assert not published, f"похоже на номер карты: {', '.join(published[:5])}"

    def test_no_russian_phone_numbers_in_docs(self) -> None:
        """Телефоны в документах и отчётах.

        Ограничено `docs/` и `tests/`: в `app/` номер может быть частью формата
        или примера в докстроке, а в отчёте прогона ему взяться неоткуда, кроме
        как из реальных данных.
        """
        hits: list[str] = []
        for path in _scanned_files():
            relative = path.relative_to(REPO_ROOT)
            if relative.parts[0] not in {"docs", "tests"}:
                continue
            text = _read(path)
            for match in PHONE_RU_MOBILE.finditer(text):
                head = text[max(0, match.start() - 80):match.start()].lower()
                if any(hint in head for hint in PLACEHOLDER_HINTS):
                    continue
                line = text.count("\n", 0, match.start()) + 1
                hits.append(f"{relative}:{line}")
        published, internal = _split_by_scope(hits)
        _warn_about_corpus("телефон", internal)
        assert not published, f"похоже на реальный телефон: {', '.join(published[:5])}"


class TestGateItselfWorks:
    """🔴 Канарейка: гейт, который ничего не находит, неотличим от сломанного."""

    def test_luhn_recognises_a_real_card_shape(self) -> None:
        """Классический тестовый номер карты проходит Луна."""
        assert _luhn("4" + "1" * 15)

    def test_luhn_rejects_a_mantissa(self) -> None:
        """А мантисса из отчёта сертификации — нет. Ровно она роняла раннюю редакцию."""
        assert not _luhn("4551915228366852")

    def test_patterns_match_their_own_examples(self) -> None:
        """Каждый шаблон ловит образец своего вида.

        Без этого опечатка в регулярке даёт вечно зелёный гейт: он ничего не находит,
        потому что не может найти ничего в принципе. Образцы тоже склеены из частей.
        """
        samples = {
            "приватный ключ PEM": "-----BEGIN RSA PRIVATE" + " KEY-----",
            "токен GitHub": "g" + "hp_" + "a" * 36,
            "ключ AWS": "A" + "KIA" + "B" * 16,
            "ключ LLM-провайдера": "s" + "k-ant-" + "c" * 32,
            "токен Telegram": "1234567890:A" + "A" + "d" * 33,
            # Разорвано, как остальные образцы: цельная строка ловится собственным
            # же шаблоном при сканировании этого файла (PIT-026 — гейт считает
            # нарушением текст правила о нарушении).
            "строка подключения с паролем": "postgres" + "ql://user:hunt" + "er22@db:5432/x",
        }
        for kind, sample in samples.items():
            assert SECRET_PATTERNS[kind].search(sample), f"шаблон «{kind}» не ловит образец"

    def test_patterns_ignore_placeholders(self) -> None:
        """Заглушки в примерах не считаются утечкой — иначе `.env.example` был бы красным."""
        line = "DATABASE_URL=postgres" + "ql://finpilot:changeme@db:5432/finpilot"
        assert any(hint in line.lower() for hint in PLACEHOLDER_HINTS)

    def test_phone_pattern_catches_a_mobile_number(self) -> None:
        """Мобильный номер — персональные данные, шаблон обязан его видеть."""
        # Слово example в той же строке обязательно: гейт сканирует и этот файл,
        # а образец без него неотличим от настоящего номера (PIT-026).
        assert PHONE_RU_MOBILE.search("example +7 916 123 45 67")

    def test_phone_pattern_ignores_an_organisation_hotline(self) -> None:
        """🔴 Горячая линия банка на его же бланке — реквизит, а не ПДн.

        Ровно этот номер держал гейт красным: фикстура выписки печатает телефон
        поддержки, и требование «обезличить» его лишено смысла.
        """
        assert not PHONE_RU_MOBILE.search("900     +7 495 500-55-50     www.sberbank.ru")


class TestScopeSplitIsHonest:
    """Мягкость ограничена внутренним контуром и не молчит."""

    def test_published_hit_stays_hard(self) -> None:
        published, internal = _split_by_scope(
            ["app/main.py:10", "docs/research/raw/corpus.md:42"]
        )
        assert published == ["app/main.py:10"]
        assert internal == ["docs/research/raw/corpus.md:42"]

    def test_corpus_hit_is_warned(self) -> None:
        with pytest.warns(UserWarning, match="внутреннем контуре"):
            _warn_about_corpus("номер карты", ["docs/research/raw/corpus.md:42"])
