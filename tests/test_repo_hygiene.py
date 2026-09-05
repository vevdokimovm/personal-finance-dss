"""Гигиена корня репозитория и полнота `.env.example` (v9.0.0).

## Зачем гейт, а не разовая уборка

Ревизия перед вехой 9 нашла в корне четыре файла, которых там быть не должно, —
и все четыре появились по-разному: копия при правке (`.bak`), артефакт macOS
(`.DS_Store`), рабочая база (`.db`), отчёт разового прогона. Разовая уборка чинит
сегодняшнее состояние и ничего не говорит про завтрашнее: те же четыре способа
работают и после неё.

🔴 **Почему это не косметика перед деплоем.** Каждый файл в корне попадает
в чекпоинт-архив, а `.db` — ещё и в образ, если `.dockerignore` промахнётся.
Рабочая база размером в полмегабайта содержит **данные**, пусть и синтетические;
её место — вне репозитория, и правило «реальные персональные данные не уходят
наружу» держится в том числе на этом.

## `.env.example` — не документация, а контракт

Каждая переменная, которую читает `Settings`, обязана быть в примере: человек,
поднимающий продукт, собирает `.env` по нему, а не по исходникам. Пропущенная
переменная означает дефолт, о котором он не знал, — и именно так появились
два конфига, ломающие прод молча (v8.56.0: `CORS_ORIGINS`, `DATABASE_URL`).

Проверяются **все** поля `Settings`, а не заранее выписанный список: список
разошёлся бы с кодом при первом же новом поле, и заметить это было бы нечем.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from app.config import Settings

REPO_ROOT = Path(__file__).resolve().parents[1]
ENV_EXAMPLE = REPO_ROOT / ".env.example"

# Файлы и расширения, которых в корне быть не должно. Каждый — свой способ появления,
# поэтому список ведётся руками: глоб по «мусору» ловил бы и легитимные файлы.
FORBIDDEN_EXACT = {
    ".DS_Store": "артефакт macOS, попадает в архив и в образ",
    "sppr.db": "рабочая база: данные не место в репозитории, даже синтетические",
    "IMAGE-REVISION-STATUS.md": "отчёт разового прогона — ему место в docs/reports/",
}
FORBIDDEN_SUFFIXES = {
    ".bak": "копия при правке — версии живут в архивах, а не рядом с оригиналом",
    ".orig": "остаток слияния",
    ".rej": "остаток неприменённого патча",
    ".pyc": "байт-код",
}

# Поля, которых в примере нет намеренно: они не конфигурируются человеком.
ENV_EXEMPT = {
    "APP_VERSION",  # ведётся церемонией батча, не руками
    "PROJECT_NAME",
}


def _root_files() -> list[Path]:
    return [p for p in REPO_ROOT.iterdir() if p.is_file()]


class TestRootIsClean:
    """Корень репозитория содержит только то, чему там место."""

    def test_no_forbidden_files(self) -> None:
        """🔴 Найдено ревизией перед вехой 9: четыре файла, четыре разных способа.

        Мутация «вернуть любой из них» роняет этот тест с объяснением, почему
        конкретный файл мешает, — а не общим «в корне мусор».
        """
        found = {
            p.name: FORBIDDEN_EXACT[p.name]
            for p in _root_files()
            if p.name in FORBIDDEN_EXACT
        }
        assert not found, "в корне лежат файлы, которым там не место: " + "; ".join(
            f"{name} ({why})" for name, why in found.items()
        )

    def test_no_backup_suffixes(self) -> None:
        """Копии при правке не остаются рядом с оригиналом.

        `.bak` опаснее прочего мусора: он выглядит как рабочий файл, и правка
        может уехать в него вместо настоящего — тихо и без ошибки.
        """
        found = [
            f"{p.name} ({FORBIDDEN_SUFFIXES[p.suffix]})"
            for p in _root_files()
            if p.suffix in FORBIDDEN_SUFFIXES
        ]
        assert not found, "в корне остались копии/остатки: " + "; ".join(found)

    def test_database_files_are_ignored_by_git(self) -> None:
        """🔴 Запрет держится не только на уборке, но и на `.gitignore`.

        Убрать файл и не закрыть путь — значит починить сегодняшний день:
        следующий запуск создаст базу заново, и она снова окажется в архиве.
        """
        gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
        assert re.search(r"^\*?\.db$|^\*\.db\b", gitignore, re.MULTILINE), (
            "`*.db` не закрыт в .gitignore — рабочая база вернётся в репозиторий сама"
        )


class TestEnvExampleIsComplete:
    """Пример окружения покрывает все настройки, которые читает приложение."""

    def test_every_setting_is_documented(self) -> None:
        """🔴 Пропущенная переменная = дефолт, о котором человек не знал.

        Ровно так появились `CORS_ORIGINS` и `DATABASE_URL`, ломавшие прод молча
        (v8.56.0). Список полей берётся из `Settings`, а не выписывается рядом:
        выписанный разошёлся бы с кодом при первом новом поле.
        """
        text = ENV_EXAMPLE.read_text(encoding="utf-8")
        documented = set(re.findall(r"^#?\s*([A-Z][A-Z0-9_]+)\s*=", text, re.MULTILINE))
        missing = sorted(
            name for name in Settings.model_fields
            if name not in documented and name not in ENV_EXEMPT
        )
        assert not missing, (
            f"настройки читаются приложением, но не описаны в .env.example: {missing}. "
            "Человек соберёт .env по примеру и получит дефолты, о которых не знал"
        )

    @pytest.mark.parametrize(
        "name",
        ["JWT_SECRET", "ADMIN_API_KEY", "TOKEN_ENCRYPTION_KEY", "TRUST_PROXY_HEADERS"],
    )
    def test_production_critical_settings_are_present(self, name: str) -> None:
        """Настройки, без которых прод не поднимется или сломается, названы явно.

        Тест дублирует предыдущий по существу и оставлен намеренно: он падает
        с именем конкретной переменной, а не со списком, и по нему сразу видно,
        что именно забыли перед деплоем.
        """
        assert re.search(rf"^#?\s*{name}\s*=", ENV_EXAMPLE.read_text(encoding="utf-8"),
                         re.MULTILINE), f"{name} не описан в .env.example"

    def test_example_holds_no_real_secrets(self) -> None:
        """🔴 Пример не содержит значений, похожих на настоящие ключи.

        `.env.example` лежит в репозитории и уезжает в публичное зеркало. Fernet-ключ
        или длинная случайная строка здесь означали бы утечку, даже если ключ давно
        сменили: история остаётся.
        """
        for line in ENV_EXAMPLE.read_text(encoding="utf-8").splitlines():
            if "=" not in line or line.strip().startswith("#"):
                continue
            value = line.split("=", 1)[1].strip().strip('"').strip("'")
            assert not re.fullmatch(r"[A-Za-z0-9_\-]{32,}=*", value), (
                f"в .env.example значение похоже на настоящий секрет: {line.split('=')[0]}"
            )
