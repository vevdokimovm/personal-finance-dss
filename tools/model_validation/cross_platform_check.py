"""
Кросс-платформенная сверка детерминированных прогонов (волна 0, п. 0.5,
`docs/model/model_completion_plan.md` §4).

Зачем: floating-point арифметика теоретически может разойтись между
платформами (разные libm/BLAS, x86_64 vs arm64) — модель обещает
воспроизводимость по seed (см. `knowledge/model_validation/README.md`:
"совпадение доказано сверкой rt/kind/risk до копейки"), но эта гарантия
никогда не проверялась явно между Intel Mac и Linux (только внутри одной
платформы, между версиями генератора).

Метод: генерируем N портретов детерминированным сидом, прогоняем полный
`run_planning()` на каждом, сериализуем ключевые числовые поля канонически
(отсортированные ключи, фиксированный формат float) и считаем sha256 по
каждому портрету + один агрегатный хеш по всему прогону. Сравнение между
платформами — просто diff двух таких отчётов; расхождение агрегатного хеша
означает реальную проблему воспроизводимости, а не косметику.

Запуск: python -m tools.model_validation.cross_platform_check [N]
Пишет отчёт в knowledge/model_validation/cross_platform_<platform>.json
"""
from __future__ import annotations

import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

from app.services.planning import run_planning
from tools.portrait_testing.generator import PortraitGenerator

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "knowledge" / "model_validation"
DEFAULT_N = 2000


def _canonical(value: float, ndigits: int = 6) -> str:
    """Фиксированный формат: без него `repr(float)` может отличаться между
    платформами при равном значении (напр. экспоненциальная запись у
    экстремумов) — сериализация обязана быть детерминированной сама по себе,
    не только вычисление."""
    return f"{round(float(value), ndigits):.{ndigits}f}"


def _portrait_digest(p: dict, result: dict) -> str:
    ind = result["indicators"]
    best = result.get("best") or {}
    ds = ind.get("debt_schedule") or {}
    fields = [
        p["id"] if "id" in p else "",
        _canonical(ind["Rt"]), _canonical(ind["Lt"]), _canonical(ind["Dt"]),
        _canonical(ind.get("income_cv") or -1),
        str(best.get("id", "")),
        _canonical(best.get("utility", 0) or 0),
        "1" if result.get("crisis_plan") else "0",
        _canonical(ds.get("interest_saved", 0) or 0),
        str(ds.get("months_saved", "")),
    ]
    return hashlib.sha256("|".join(fields).encode("utf-8")).hexdigest()


def run(n: int) -> dict:
    gen = PortraitGenerator(seed=20260813, version=2)
    digests: list[str] = []
    exceptions = 0
    for i in range(n):
        p = gen.generate(i)
        try:
            result = run_planning(
                income_total=p["income_total"], expense_total=p["expense_total"],
                obligations=p["obligations"], goals=p["goals"], bliq=p["bliq"],
                r_bench=p["r_bench"], risk_tolerance=int(p.get("risk_tolerance", 3)),
                l_min=float(p.get("l_min", 0.0)),
                today=datetime(2026, 8, 13, tzinfo=timezone.utc),
            )
        except Exception:  # noqa: BLE001 — сверка воспроизводимости, не полноты
            exceptions += 1
            digests.append("EXCEPTION")
            continue
        digests.append(_portrait_digest(p, result))

    aggregate = hashlib.sha256("".join(digests).encode("utf-8")).hexdigest()
    return {
        "platform": platform.platform(),
        "machine": platform.machine(),
        "python_version": sys.version.split()[0],
        "n": n,
        "seed": 20260813,
        "exceptions": exceptions,
        "aggregate_sha256": aggregate,
        "per_portrait_sha256": digests,
    }


def main() -> None:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_N
    report = run(n)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # ОС + архитектура в имени: x86_64 у Intel Mac и у Linux-контейнера на той
    # же машине совпадают — без ОС в имени один прогон затирал бы другой.
    tag = f"{platform.system()}_{report['machine']}".replace("/", "_")
    out_path = OUT_DIR / f"cross_platform_{tag}.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"платформа: {report['platform']} ({report['machine']}), python "
          f"{report['python_version']}")
    print(f"портретов: {n}, исключений: {report['exceptions']}")
    print(f"агрегатный sha256: {report['aggregate_sha256']}")
    print(f"отчёт: {out_path}")


if __name__ == "__main__":
    main()
