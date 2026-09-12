"""Ревизионный гейт против правила §9: первичный материал хранится дословно.

**Зачем этот файл.** `preflight` был красным 119 провалами на четырёх файлах
`docs/research/raw/` — и ни один из них не дефект. Две проверки ловили ровно то,
что правило §9 обязывает хранить неприкосновенным:

- **CJK-канарейка** — на дословных корейских цитатах KakaoBank/Toss (названия продуктов,
  тексты дисклеймеров с сайта банка). Канарейка заведена против токен-глюка генерации
  (иероглиф вместо кириллицы), а не против иностранной цитаты.
- **Legacy мат-модели** — на «95% CI» в цитатах научных статей. Паттерн заведён против
  утечки параметра модели v2.x в живые доки; в цитате чужой работы это описание её
  методики, а не наш параметр.

Правка сырья для прохождения гейта запрещена правилом §9 напрямую, поэтому лечение —
аллоулист с обоснованием, тот же механизм, что уже применён к
`competitors_recommendation_engines_2026-09-08.md` и к `dist/` в `SKIP_DIRS`.

**Что держат тесты.** (1) Гейт зелёный на всём дереве — иначе следующая вахта снова
сдаёт батч с красным preflight, как это произошло с батчем 10.09. (2) Аллоулист не
протухает: каждая запись обязана указывать на существующий файл, иначе он копит мёртвые
исключения и однажды прикроет настоящий глюк. (3) 🔴 Канарейка **не ослаблена**: на файле
вне аллоулиста иероглиф по-прежнему провал. Без третьего теста первые два означали бы
«гейт отключили», а не «гейт уточнили».
"""
from __future__ import annotations

from pathlib import Path

from tools.revision.revision_check import (
    CJK_ALLOWLIST,
    LEGACY_ALLOWLIST_FILES,
    CjkCanaryChecker,
    LegacyModelChecker,
)

ROOT = Path(__file__).resolve().parents[1]

# 🔴 Символы задаются escape-последовательностями, а не буквально: иначе этот файл
# сам становится провалом канарейки — о чём её собственный комментарий
# в `revision_check.py` и предупреждает. Поймано на первом же прогоне.
GLITCH = "\u6040"   # тот самый иероглиф из реального глюка в слове «Авторизация»
HANGUL = "\uac00"   # хангыль: диапазон канарейки, не только CJK Unified


class TestGateIsGreenOnTheTree:
    """Обе проверки зелёные — предмет провала preflight 11.09.2026."""

    def test_cjk_canary_has_no_failures(self):
        result = CjkCanaryChecker(ROOT).run()
        assert result.failures == [], [f"{f.location}: {f.detail}" for f in result.failures[:5]]

    def test_legacy_model_check_has_no_failures(self):
        result = LegacyModelChecker(ROOT).run()
        assert result.failures == [], [f"{f.location}: {f.detail}" for f in result.failures[:5]]


class TestAllowlistsDoNotRot:
    """Мёртвая запись аллоулиста однажды прикроет настоящий дефект."""

    def test_every_cjk_entry_points_at_an_existing_file(self):
        missing = [rel for rel in CJK_ALLOWLIST if not (ROOT / rel).is_file()]
        assert missing == []

    def test_every_cjk_entry_carries_a_justification(self):
        blank = [rel for rel, why in CJK_ALLOWLIST.items() if len(why.strip()) < 20]
        assert blank == []

    def test_every_legacy_entry_points_at_an_existing_file(self):
        missing = [rel for rel in LEGACY_ALLOWLIST_FILES if not (ROOT / rel).is_file()]
        assert missing == []


class TestCanaryStillCatchesRealGlitches:
    """🔴 Гейт уточнён, а не выключен."""

    def test_cjk_outside_allowlist_is_still_a_failure(self, tmp_path):
        (tmp_path / "docs").mkdir()
        # Тот самый класс дефекта: иероглиф внутри русского слова.
        (tmp_path / "docs" / "leak.md").write_text(
            f"Авториза{GLITCH}ция пользователя\n", encoding="utf-8")
        result = CjkCanaryChecker(tmp_path).run()
        assert len(result.failures) == 1
        assert "docs/leak.md:1" == result.failures[0].location

    def test_allowlisted_path_is_skipped_only_for_its_own_path(self, tmp_path):
        """Исключение действует на один путь, а не на каталог целиком."""
        raw = tmp_path / "docs" / "research" / "raw"
        raw.mkdir(parents=True)
        allowed = next(iter(CJK_ALLOWLIST))
        target = tmp_path / allowed
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(f"{HANGUL}\n", encoding="utf-8")
        (raw / "other_file.md").write_text(f"{HANGUL}\n", encoding="utf-8")
        result = CjkCanaryChecker(tmp_path).run()
        locations = [f.location for f in result.failures]
        assert locations == ["docs/research/raw/other_file.md:1"]

    def test_legacy_pattern_outside_allowlist_is_still_a_failure(self, tmp_path):
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "leak.md").write_text(
            "Модель перебирает 21 альтернатив по портфелю\n", encoding="utf-8")
        result = LegacyModelChecker(tmp_path).run()
        assert [f.location for f in result.failures] == ["docs/leak.md:1"]
