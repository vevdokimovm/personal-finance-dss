"""Гейт: локальный прогон идёт в окружении, собранном СТРОГО по requirements.

🔴 Корень всей истории 24–25.09.2026, и он один. Локальный прогон повторял КОМАНДЫ
воркфлоу, но не его ОКРУЖЕНИЕ: он шёл в рабочем венве, где накоплены пакеты, которых
в `requirements.txt` нет. Раннер ставит ровно объявленное — и расхождение всегда
в одну сторону: у разработчика пакетов больше.

Чем оплачено: `defusedxml` использовался в проде (`cbr_fx`, `cbr_rate`) с v9.13.14
и не был объявлен. Локально стоял в венве — прогон зелёный; на раннере `conftest`
не импортировался вовсе, четыре джобы из девяти падали до первого теста. Дословно
владелец: «СДЕЛАЙ ОКРУЖЕНИЕ ОДНО ПРАВИЛЬНОЕ И ТУТ И ТАМ И УВИДИШЬ ОШИБКИ ЛОКАЛЬНО».

Чего этот гейт НЕ обещает: одинаковой ОС. Раннер — ubuntu, станция — macOS, и часть
различий (apt, пути, браузеры) остаётся. Он закрывает ровно тот источник расхождения,
который измерен и стоил дня работы: состав пакетов.
"""
from __future__ import annotations

from pathlib import Path

from tools import ci_local

REPO = Path(__file__).resolve().parents[1]


class TestCleanVenvIsPreferred:
    """PATH прогона ведёт в чистое окружение, когда оно собрано."""

    def test_clean_venv_wins_when_present(self, tmp_path: Path) -> None:
        clean = tmp_path / ci_local.CLEAN_VENV / "bin"
        clean.mkdir(parents=True)
        path = ci_local._env(tmp_path)["PATH"]
        assert path.split(":")[0] == str(clean), (
            "прогон обязан идти в окружении по requirements, а не в рабочем венве"
        )

    def test_falls_back_to_working_venv(self, tmp_path: Path) -> None:
        """Чистого нет — работаем в обычном, но это НЕ равно прогону CI."""
        working = tmp_path / ".venv" / "bin"
        working.mkdir(parents=True)
        assert ci_local._env(tmp_path)["PATH"].split(":")[0] == str(working)

    def test_marker_names_the_environment(self, tmp_path: Path) -> None:
        """Прогон обязан записать в след, в каком окружении он шёл.

        Иначе зелёный след из рабочего венва неотличим от зелёного следа
        из чистого — и гейт снова начнёт покрывать собой «работает у меня».
        """
        (tmp_path / ci_local.CLEAN_VENV / "bin").mkdir(parents=True)
        assert ci_local.environment_name(tmp_path) == "clean"
        other = tmp_path / "other"
        other.mkdir()
        assert ci_local.environment_name(other) == "working"


class TestStampRecordsEnvironment:
    """След прогона несёт имя окружения."""

    def test_stamp_has_environment_field(self, tmp_path: Path, monkeypatch) -> None:
        import json

        stamp = tmp_path / "stamp.json"
        monkeypatch.setattr(ci_local, "STAMP", stamp)
        ci_local.write_stamp(["lint"], [], REPO)
        data = json.loads(stamp.read_text(encoding="utf-8"))
        assert data["environment"] in {"clean", "working"}
