"""Вердикт о CI: зелёный ли прогон по ПОСЛЕДНЕМУ ТЕГУ, целиком.

Запуск:

    python -m tools.ci_verdict            # последний тег
    python -m tools.ci_verdict v9.13.11   # конкретный тег

Выход ненулевой, если хоть одна джоба не `success` (кроме `skipped`) или прогон
ещё идёт. Печатает все джобы, а не только упавшие — чтобы вердикт можно было
прочитать целиком, а не поверить на слово.

🔴 **Зачем инструмент.** За сутки вахта трижды объявила CI зелёным, и трижды
ошиблась: сначала смотрела локальный прогон вместо раннера, потом прогон
по **ветке** вместо прогона по **тегу**. Джоба «Полный (мультибраузер + визуал +
a11y + security)» на ветке **пропускается** и запускается только на теге — то есть
ровно там, где вахта не смотрела, красное и жило, почти два месяца.
Разбор — `docs/reports/incidents/ci_red_on_tags_for_a_month.md`.

Правило вердикта, и оно узкое намеренно:
- `success` — зелено;
- `skipped` — зелено (тиры `full`/`deep` пропускаются по условию запуска);
- `cancelled`, `failure`, `timed_out`, всё прочее — НЕ зелено;
- незавершённая джоба — НЕ зелено: вердикта по ней ещё нет.
"""
from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass

REPO = "vevdokimovm/personal-finance-dss"


@dataclass(frozen=True)
class Job:
    """Джоба прогона: имя, состояние и вердикт."""

    name: str
    status: str
    conclusion: str | None


def verdict(jobs: list[Job]) -> tuple[bool, list[str]]:
    """Зелёный ли прогон целиком.

    Args:
        jobs: джобы прогона.

    Returns:
        Пара «зелено ли» и список проблем в виде «имя: причина».
    """
    if not jobs:
        return False, ["в прогоне нет ни одной джобы — проверять нечего"]
    problems: list[str] = []
    for item in jobs:
        if item.status != "completed":
            problems.append(f"{item.name}: {item.status} (не завершена)")
        elif item.conclusion not in ("success", "skipped"):
            problems.append(f"{item.name}: {item.conclusion}")
    return not problems, problems


def _gh(*args: str) -> str:
    result = subprocess.run(
        ["gh", *args], capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args)}: {result.stderr.strip()}")
    return result.stdout


def latest_tag() -> str:
    """Последний тег репозитория по версии, а не по дате создания."""
    out = _gh("api", f"repos/{REPO}/tags", "--jq", ".[0].name")
    return out.strip()


def commit_of(ref: str) -> str:
    """SHA коммита, на который указывает ссылка (тег, ветка или сам SHA).

    `HEAD` разрешается ЛОКАЛЬНО: у GitHub API такой ссылки нет, а спрашивать сеть
    о том, что лежит в рабочем дереве, незачем — и это единственный случай, когда
    вердикт можно запросить без интернета вовсе.
    """
    if ref == "HEAD":
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=False
        )
        if result.returncode == 0:
            return result.stdout.strip()
    return _gh("api", f"repos/{REPO}/commits/{ref}", "--jq", ".sha").strip()


def fetch_jobs(sha: str) -> tuple[str, list[Job]]:
    """Джобы последнего прогона, запущенного по ЭТОМУ КОММИТУ.

    🔴 Раньше искали прогон по имени тега. Решение владельца 25.09.2026, дословно:
    «снимай вердикт по КОММИТУ!». Причина: из триггеров воркфлоу убраны теги, потому
    что все три тира (`fast`, `full`, `deep`) гоняются на каждый push — прогон по тегу
    дублировал прогон по коммиту один в один, два полных набора джоб на один и тот же
    код при нуле новой информации. Коммит — то, что реально проверено; тег лишь имя,
    которое на него указывает.
    """
    runs = json.loads(
        _gh(
            "run", "list", "--limit", "50",
            "--json", "databaseId,headSha,status",
        )
    )
    for run in runs:
        if run["headSha"].startswith(sha) or sha.startswith(run["headSha"]):
            raw = json.loads(
                _gh("run", "view", str(run["databaseId"]), "--json", "jobs")
            )
            jobs = [
                Job(name=j["name"], status=j["status"], conclusion=j["conclusion"])
                for j in raw["jobs"]
            ]
            return str(run["databaseId"]), jobs
    return "", []


def main() -> int:
    ref = sys.argv[1] if len(sys.argv) > 1 else "HEAD"
    sha = commit_of(ref)
    run_id, jobs = fetch_jobs(sha)
    if not run_id:
        print(f"прогона по коммиту {sha[:12]} ({ref}) не найдено")
        return 1
    print(f"=== ВЕРДИКТ CI по коммиту {sha[:12]} ({ref}, прогон {run_id}) ===")
    for item in jobs:
        mark = "🟢" if item.conclusion == "success" else (
            "⚪️" if item.conclusion == "skipped" else "🔴"
        )
        print(f"  {mark} {item.conclusion or item.status}\t{item.name}")
    ok, problems = verdict(jobs)
    if ok:
        print("\nЗЕЛЕНО ЦЕЛИКОМ.")
        return 0
    print("\nНЕ ЗЕЛЕНО:")
    for line in problems:
        print(f"  - {line}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
