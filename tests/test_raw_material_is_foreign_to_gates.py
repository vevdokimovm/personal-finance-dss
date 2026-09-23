"""Гейты не судят первичный материал исследований как СВОЙ текст (правило §9).

**Почему класс, а не список.** `LINK_ALLOWLIST`, `LEGACY_ALLOWLIST_FILES` и
`CJK_ALLOWLIST` вели по одной записи на файл. Корпус `docs/research/raw/` вырос
до 188 файлов, и каждая новая тема снова роняла `preflight` тем же способом:
цитата чужого репозитория читается как битая ссылка на НАШ путь, доверительный интервал
из цитируемой статьи — как утечка параметра нашей модели v2.x, иероглиф
в дословном ответе — как токен-глюк. Правка сырья под гейт запрещена §9
напрямую, поэтому список исключений мог только расти.

Тот же довод уже записан в самом гейте для `GENERATED_PREFIXES`: «свойство пути
не зависит от того, кто на него сослался, — поэтому и проверяется свойство».
Здесь свойство такое же: файл под `docs/research/raw/` — чужой текст, хранимый
дословно, и наши проверки к нему неприменимы **по построению**, а не по списку.

**Что держат тесты.** (1) Класс распознаётся. (2) Три проверки не валят гейт
на сырье. (3) 🔴 Канарейка НЕ выключена: вне `raw/` иероглиф по-прежнему провал,
а внутри `raw/` он остаётся ВИДИМЫМ в информационных строках — иначе это было бы
«гейт сняли», а не «гейт уточнили».
"""
from __future__ import annotations

from pathlib import Path

from tools.revision.revision_check import (
    CjkCanaryChecker,
    LegacyModelChecker,
    LinkChecker,
    _is_raw_material,
)
from tools.preflight import soft_hyphens

ROOT = Path(__file__).resolve().parents[1]

# Символы задаются escape-последовательностями: иначе файл сам ловится канарейкой.
_CJK = chr(0x7D04)  # иероглиф строится кодом: литерал поймала бы сама канарейка
_SOFT_HYPHEN = chr(0x00AD)
# Строка-приманка собирается из частей: целиком она совпала бы с legacy-паттерном
# в этом же файле — ровно то самосовпадение, о котором предупреждает сам гейт.
_LEGACY_QUOTE = "95" + "% доверительный интервал"


def test_raw_material_recognised_by_prefix() -> None:
    assert _is_raw_material("docs/research/raw/anything_2026-01-01.md")
    assert not _is_raw_material("docs/research/synthesis/PASS_JOURNAL.md")
    assert not _is_raw_material("docs/math_model.md")


def _write_raw(tmp_path: Path, name: str, body: str) -> Path:
    raw = tmp_path / "docs" / "research" / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    path = raw / name
    path.write_text(body, encoding="utf-8")
    return path


def test_link_checker_ignores_citations_of_foreign_repositories(tmp_path: Path) -> None:
    _write_raw(tmp_path, "theme.md", "Разбор чужого проекта: app/Factory/Journal.php\n")
    assert LinkChecker(tmp_path).run().ok


def test_link_checker_still_fails_outside_raw(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir(parents=True)
    (tmp_path / "docs" / "live.md").write_text("см. app/core/nonexistent.py\n", encoding="utf-8")
    assert not LinkChecker(tmp_path).run().ok


def test_legacy_checker_ignores_quoted_confidence_intervals(tmp_path: Path) -> None:
    _write_raw(tmp_path, "science.md", f"Авторы приводят {_LEGACY_QUOTE}.\n")
    assert LegacyModelChecker(tmp_path).run().ok


def test_cjk_canary_does_not_fail_on_raw_but_keeps_it_visible(tmp_path: Path) -> None:
    _write_raw(tmp_path, "quote.md", f"охват {_CJK} 12 %\n")
    result = CjkCanaryChecker(tmp_path).run()
    assert result.ok, "сырьё не валит гейт"
    assert any("quote.md" in finding.location for finding in result.infos), (
        "находка обязана остаться видимой в информационных строках"
    )


def test_cjk_canary_still_fails_outside_raw(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir(parents=True)
    (tmp_path / "docs" / "live.md").write_text(f"текст {_CJK} текст\n", encoding="utf-8")
    assert not CjkCanaryChecker(tmp_path).run().ok


def test_soft_hyphen_check_skips_raw_material(tmp_path: Path) -> None:
    _write_raw(tmp_path, "soft.md", f"сло{_SOFT_HYPHEN}во\n")
    assert soft_hyphens(tmp_path) == []


def test_soft_hyphen_check_still_fails_outside_raw(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir(parents=True)
    (tmp_path / "docs" / "live.md").write_text(f"сло{_SOFT_HYPHEN}во\n", encoding="utf-8")
    assert soft_hyphens(tmp_path) != []
