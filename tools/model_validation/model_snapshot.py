"""
Снимок модели на момент запуска (волна 0, п. 0.7, `docs/model/telemetry_spec.md`).

Зачем: без снимка через год не с чем сравнить поведение модели на живых
данных — неизвестно, какая именно версия канона/кода/констант эти советы
давала. Снимок читает константы ПРЯМО ИЗ КОДА (не переписан вручную), чтобы
не расходиться с реальностью — та же дисциплина, что у «живых указателей»
канона (session-context.sh).

Обычный (не пред-релизный) прогон делает снимок ТЕКУЩЕГО состояния — полезен
и до фактического запуска как baseline; при реальном запуске в проде команду
нужно перезапустить, чтобы зафиксировать финальную конфигурацию.

Запуск: python -m tools.model_validation.model_snapshot
"""
from __future__ import annotations

import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from app.config import Settings
from app.core import filtering, goals_priority, investment, ranking
from app.core.amortization import MAX_HORIZON_MONTHS

REPO_ROOT = Path(__file__).resolve().parents[2]
CANON_PATH = REPO_ROOT / "docs" / "math_model.md"
OUT_DIR = REPO_ROOT / "knowledge" / "model_validation"


def _git_commit() -> str:
    try:
        out = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True,
        )
        return out.stdout.strip()
    except Exception:  # noqa: BLE001 — снимок не должен падать из-за git
        return "неизвестен (git недоступен)"


def _canon_version() -> str:
    text = CANON_PATH.read_text(encoding="utf-8")
    m = re.search(r"версия\s+(\d+\.\d+\.\d+)", text.splitlines()[0])
    return m.group(1) if m else "не найдена"


def build_snapshot() -> str:
    app_version = Settings().APP_VERSION
    canon_version = _canon_version()
    commit = _git_commit()
    when = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    risk_rows = "\n".join(
        f"| {k} | {v['label']} | {v['w_rt']}/{v['w_lt']}/{v['w_dt']}/{v['w_goals']} | "
        f"{v['lt_target']} |"
        for k, v in sorted(ranking.RISK_PROFILES.items())
    )
    equity_rows = "\n".join(
        f"| {k} | {v} |" for k, v in sorted(investment.EQUITY_SHARE_BY_PROFILE.items())
    )

    return f"""# Снимок модели — v{app_version}

**Снято:** {when} · **Команда:** `python -m tools.model_validation.model_snapshot`
(константы читаются прямо из кода на момент запуска, не переписаны вручную)

> Волна 0, п. 0.7 (`docs/model/telemetry_spec.md`) — без этого снимка через год
> поведение модели на живых данных не с чем сравнить: неизвестно, какая именно
> версия канона/кода/констант эти советы давала. Если это прогон ДО фактического
> запуска в проде — при реальном запуске команду нужно перезапустить, чтобы
> зафиксировать финальную конфигурацию (этот файл — baseline, не финал).

## Версии

| Что | Значение |
|---|---|
| Версия кода (`APP_VERSION`) | {app_version} |
| Версия канона (`docs/math_model.md`) | {canon_version} |
| Git-коммит | `{commit}` |

## Ключевые константы (`app/core/`)

| Константа | Значение | Модуль |
|---|---|---|
| `DT_MAX` (потолок ПДН) | {filtering.DT_MAX} | `filtering.py` |
| `L_MIN` (мин. автономии, отсев) | {filtering.L_MIN} | `filtering.py` |
| `B_MIN` (мин. остаточный ресурс) | {filtering.B_MIN} | `filtering.py` |
| `RESERVE_FLOOR_MONTHS` (floor резерва) | {ranking.RESERVE_FLOOR_MONTHS} | `ranking.py` |
| `TOXIC_FLOOR_MONTHS` (floor при токсичном долге, G8) | \
{ranking.TOXIC_FLOOR_MONTHS} | `ranking.py` |
| `INCOME_VOLATILITY_THRESHOLD` (ADR-015) | {ranking.INCOME_VOLATILITY_THRESHOLD} | `ranking.py` |
| `INCOME_VOLATILITY_MIN_MONTHS` (ADR-015) | {ranking.INCOME_VOLATILITY_MIN_MONTHS} | `ranking.py` |
| `INCOME_VOLATILITY_FLOOR_BOOST_CAP` (ADR-015) | \
{ranking.INCOME_VOLATILITY_FLOOR_BOOST_CAP} | `ranking.py` |
| `GOAL_INFLATION_RATE` (ADR-013) | {goals_priority.GOAL_INFLATION_RATE} | `goals_priority.py` |
| `GOAL_INFLATION_HORIZON_MONTHS` (ADR-013) | \
{goals_priority.GOAL_INFLATION_HORIZON_MONTHS} | `goals_priority.py` |
| `MAX_HORIZON_MONTHS` (график погашения, ADR-016) | {MAX_HORIZON_MONTHS} | `amortization.py` |
| `HORIZON_SHORT_MONTHS` / `HORIZON_MID_MONTHS` (инвест-транш) | \
{investment.HORIZON_SHORT_MONTHS} / {investment.HORIZON_MID_MONTHS} | `investment.py` |

## Профили риска (`RISK_PROFILES`)

| # | Профиль | Веса Rt/Lt/Dt/Goals | Lt* (целевая подушка) |
|---|---|---|---|
{risk_rows}

## Доля акций в инвест-транше по профилю (`EQUITY_SHARE_BY_PROFILE`)

| Профиль | Доля акций |
|---|---:|
{equity_rows}

## Как использовать

Сравнить поведение модели на живых данных с этим снимком — значит взять
`model_version`/`app_version` из события телеметрии (волна 0, п. 0.6,
`docs/model/telemetry_spec.md`) и найти соответствующий снимок в
`knowledge/model_validation/model_snapshot_v*.md`. Если снимка для нужной
версии нет — перезапустить эту команду на нужном коммите (снимок
детерминирован по коду, не по времени запуска).
"""


def main() -> None:
    app_version = Settings().APP_VERSION
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"model_snapshot_v{app_version.replace('.', '_')}.md"
    out_path.write_text(build_snapshot(), encoding="utf-8")
    print(f"Снимок модели: {out_path}")


if __name__ == "__main__":
    main()
