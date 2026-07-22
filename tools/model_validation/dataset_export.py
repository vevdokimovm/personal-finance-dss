"""Экспорт датасетов валидации: портреты и выход модели (веха 6).

Назначение — материализовать в репо сжатые датасеты, чтобы принцип
«один zip = полный контекст» работал и для данных:

  * `portraits_*.jsonl.gz` — сами портреты (вход): один JSON-объект на строку,
    id формата SP-XXXXX, даты в ISO. Эксперту для независимой оценки не нужен
    ни код, ни генератор — только этот файл.
  * `model_outcomes_*.csv.gz` — ответ ТЕКУЩЕЙ модели по каждому портрету
    (версию модели фиксировать в имени файла, напр. `model_outcomes_v3_3_0_on_v2`):
    статус, показатели, эффективный сплит, доминанта, инвест-транш, кризис.
    Это половина будущего joined-файла второй сертификации (вторую половину —
    колонки экспертов — добавляют внешние экспертные движки).

Запуск из корня репо:
    python -m tools.model_validation.dataset_export portraits \
        --out knowledge/model_validation/portraits_v2_seed20260702.jsonl.gz \
        --n 12000 --seed 20260702 --version 2
    python -m tools.model_validation.dataset_export outcomes \
        --out knowledge/model_validation/model_outcomes_v3_1_0_on_v2.csv.gz \
        --n 12000 --seed 20260702 --version 2
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import sys
from datetime import date, datetime, time
from pathlib import Path
from typing import Any

from tools.model_validation.expert_agreement import FROZEN_TODAY, model_outcome
from tools.portrait_testing.generator import PortraitGenerator
from tools.portrait_testing.generator_v3 import PortraitGeneratorV3
from tools.portrait_testing.generator_v4 import PortraitGeneratorV4
from tools.model_validation.portrait_validation import invalid_reason


def _jsonable(node: Any) -> Any:
    if isinstance(node, (datetime, date)):
        return node.isoformat()
    if isinstance(node, dict):
        return {k: _jsonable(v) for k, v in node.items()}
    if isinstance(node, list):
        return [_jsonable(x) for x in node]
    return node


def export_portraits(out: Path, n: int, seed: int, version: int) -> int:
    """Пишет n портретов в jsonl.gz; возвращает число записанных строк.

    Для version=3 первой строкой уходит meta-объект генератора (D3 раунда 2),
    записи размечены (layer/kind/pair_*/expected_error) — это КАНОНИЧЕСКИЙ
    файл; слепой экспертный пакет — производный (`export_expert_pack`).
    """
    out.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    if version in LAYERED_GENERATORS:
        gen_l = layered_generator(version, seed, n)
        prefix = ID_PREFIX[version]
        with gzip.open(out, "wt", encoding="utf-8") as fh:
            fh.write(json.dumps(_jsonable(gen_l.meta()), ensure_ascii=False) + "\n")
            for i in range(n):
                portrait = _jsonable(gen_l.generate(i))
                portrait["id"] = f"{prefix}-{i:05d}"
                fh.write(json.dumps(portrait, ensure_ascii=False) + "\n")
                written += 1
        return written
    gen = PortraitGenerator(seed, version=version)
    with gzip.open(out, "wt", encoding="utf-8") as fh:
        for i in range(n):
            portrait = _jsonable(gen.generate(i))
            portrait["id"] = f"SP-{i:05d}"
            fh.write(json.dumps(portrait, ensure_ascii=False) + "\n")
            written += 1
    return written


def export_coordinator_key(out: Path, n: int, seed: int,
                           version: int = 3) -> int:
    """Ключ координатора (v3+): id -> метки; слепота экспертов сохраняется."""
    gen_l = layered_generator(version, seed, n)
    out.parent.mkdir(parents=True, exist_ok=True)
    fields = ("id", "layer", "kind", "pair_id", "pair_role",
              "pair_relation", "expected_error", "id_override")
    if version >= 4:
        fields = fields[:3] + ("family",) + fields[3:]
    written = 0
    with gzip.open(out, "wt", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for i in range(n):
            row = gen_l.coordinator_key(i)
            writer.writerow({k: ("" if row.get(k) is None else row[k])
                             for k in fields})
            written += 1
    return written


LAYERED_GENERATORS = {3: PortraitGeneratorV3, 4: PortraitGeneratorV4}
ID_PREFIX = {3: "SP3", 4: "SP4"}


def layered_generator(version: int, seed: int, n: int):
    """Слоистые генераторы (v3+): единый фасад generate/expert_row/meta."""
    return LAYERED_GENERATORS[version](seed, n=n)


OUTCOME_FIELDS = (
    "id", "kind", "risk", "status", "rt", "lt", "dt",
    "xo", "xr", "xg", "invest", "dom",
    "dt_alert", "crisis_severity", "crisis_actions", "invalid_reason",
    "model_lump", "model_lump_debt", "model_lump_reserve", "model_lump_goal",
)


def _export_outcomes_layered(out: Path, n: int, seed: int,
                             version: int = 3) -> int:
    """Outcomes для слоистых датасетов (v3+): слой D — status=invalid без модели.

    Правило invalid зеркально экспертному брифу v3 (`portrait_validation`).
    id — канонические SP3-{i:05d} (уникальные, стыкуются с ключом координатора);
    дубли id слоя D — дефект уровня выгрузки, сборщик joined раунда 3
    сопоставляет ответы экспертов по порядку строк, не по id.
    """
    gen_l = layered_generator(version, seed, n)
    prefix = ID_PREFIX[version]
    today = datetime.combine(gen_l.frozen_today, time(12, 0))
    out.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with gzip.open(out, "wt", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=OUTCOME_FIELDS)
        writer.writeheader()
        for i in range(n):
            portrait = gen_l.generate(i)
            reason = invalid_reason(portrait)
            if reason is not None:
                writer.writerow({
                    "id": f"{prefix}-{i:05d}",
                    "kind": portrait.get("kind", ""),
                    "risk": portrait.get("risk_tolerance", ""),
                    "status": "invalid",
                    "rt": "", "lt": "", "dt": "",
                    "xo": 0.0, "xr": 0.0, "xg": 0.0, "invest": 0.0,
                    "dom": "none",
                    "dt_alert": "",
                    "crisis_severity": "",
                    "crisis_actions": "",
                    "invalid_reason": reason,
                })
                written += 1
                continue
            o = model_outcome(portrait, today=today)
            writer.writerow({
                "id": f"{prefix}-{i:05d}",
                "kind": portrait["kind"],
                "risk": portrait["risk_tolerance"],
                "status": o["status"],
                "rt": round(o["rt"], 2),
                "lt": round(o["lt"], 4),
                "dt": round(o["dt"], 4),
                "xo": round(o["xo"], 2),
                "xr": round(o["xr"], 2),
                "xg": round(o["xg"] - o["invest"], 2),
                "invest": round(o["invest"], 2),
                "dom": o["dom"],
                "dt_alert": int(o["dt_alert"]),
                "crisis_severity": o["crisis_severity"] or "",
                "crisis_actions": o["crisis_actions"],
                "invalid_reason": "",
                "model_lump": o["model_lump"],
                "model_lump_debt": o["model_lump_debt"],
                "model_lump_reserve": o["model_lump_reserve"],
                "model_lump_goal": o["model_lump_goal"],
            })
            written += 1
    return written


def export_model_outcomes(out: Path, n: int, seed: int, version: int) -> int:
    """Прогоняет n портретов через run_planning и пишет выход модели в csv.gz.

    xo/xr/xg — эффективный сплит лучшего плана; invest — инвестиционный транш
    (в xg НЕ включён: колонки независимы, семантику goals+inv собирает
    потребитель). Кризисные поля — охват G2.
    """
    if version in LAYERED_GENERATORS:
        return _export_outcomes_layered(out, n=n, seed=seed, version=version)
    gen = PortraitGenerator(seed, version=version)
    out.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with gzip.open(out, "wt", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=OUTCOME_FIELDS)
        writer.writeheader()
        for i in range(n):
            portrait = gen.generate(i)
            o = model_outcome(portrait)
            writer.writerow({
                "id": f"SP-{i:05d}",
                "kind": portrait["kind"],
                "risk": portrait["risk_tolerance"],
                "status": o["status"],
                "rt": round(o["rt"], 2),
                "lt": round(o["lt"], 4),
                "dt": round(o["dt"], 4),
                "xo": round(o["xo"], 2),
                "xr": round(o["xr"], 2),
                "xg": round(o["xg"] - o["invest"], 2),
                "invest": round(o["invest"], 2),
                "dom": o["dom"],
                "dt_alert": int(o["dt_alert"]),
                "crisis_severity": o["crisis_severity"] or "",
                "crisis_actions": o["crisis_actions"],
                "model_lump": o["model_lump"],
                "model_lump_debt": o["model_lump_debt"],
                "model_lump_reserve": o["model_lump_reserve"],
                "model_lump_goal": o["model_lump_goal"],
            })
            written += 1
    return written


EXPERT_FIELDS = (
    "id", "income_total", "expense_total", "obligations", "goals",
    "bliq", "r_bench", "risk_tolerance",
)


def export_expert_pack(
    out_dir: Path,
    n: int,
    seed: int,
    version: int,
    chunk_size: int = 3000,
) -> list[Path]:
    """Пакет для внешних экспертных движков: СУХИЕ входы, чанками.

    Правило чистоты (портретный протокол вехи 6): никаких подсказок —
    ни типа портрета (kind), ни вычисленных метрик, ни внутренних параметров
    модели (l_min). Только то, что знал бы живой консультант со слов клиента.
    Чанки по chunk_size строк — чтобы раздавать экспертам порциями.

    version=3: проекция `PortraitGeneratorV3.expert_row` — дубли id (слой D)
    честно доживают до эксперта; каждая часть открывается минимальной
    meta-строкой (версия/срез/число строк) БЕЗ конфига слоёв — дизайн не течёт.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    files: list[Path] = []
    fh = None
    layered = version in LAYERED_GENERATORS
    gen_l = layered_generator(version, seed, n) if layered else None
    gen = None if layered else PortraitGenerator(seed, version=version)
    try:
        for i in range(n):
            if i % chunk_size == 0:
                if fh is not None:
                    fh.close()
                part = i // chunk_size + 1
                path = out_dir / f"expert_portraits_v{version}_part{part}.jsonl.gz"
                fh = gzip.open(path, "wt", encoding="utf-8")
                files.append(path)
                if layered:
                    part_meta = {
                        "__meta__": True, "dataset_version": version,
                        "part": part, "rows": min(chunk_size, n - i),
                        "frozen_today": gen_l.frozen_today.isoformat(),
                    }
                    fh.write(json.dumps(part_meta, ensure_ascii=False) + "\n")
            if layered:
                row = _jsonable(gen_l.expert_row(i))
            else:
                portrait = _jsonable(gen.generate(i))
                portrait["id"] = f"SP-{i:05d}"
                row = {k: portrait[k] for k in EXPERT_FIELDS}
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    finally:
        if fh is not None:
            fh.close()
    return files


def _fmt_money(v: float) -> str:
    return f"{v:,.2f}".replace(",", " ")


def _fmt_cell(value) -> str:
    """Число — как деньги; всё прочее (None/строка/мусор слоя D) — сырьём в !..!."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return f"!{value!r}!"
    return _fmt_money(value)


def _fmt_rate(value) -> str:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return f"!{value!r}!"
    return f"{value * 100:.1f}%"


def _fmt_deadline(goal: dict) -> str:
    if "deadline" not in goal:
        return "!нет поля deadline!"
    value = goal["deadline"]
    if value is None:
        return "без дедлайна"
    if hasattr(value, "isoformat"):
        return f"дедлайн {value.isoformat()}"
    return f"дедлайн !{value!r}!"


def export_markdown(out: Path, n: int, seed: int, version: int) -> int:
    """Человекочитаемые СУХИЕ карточки портретов одним .md (для владельца).

    Те же правила чистоты, что и в экспертном пакете: без типа портрета и без
    вычисленных метрик. Регенерируемый артефакт — в архиве кода не хранится,
    выдаётся по запросу.

    version=3: карточки строятся из слепой проекции `expert_row` — дубли id
    доживают до карточек, битые записи слоя D рендерятся КАК ЕСТЬ (сырое
    значение в `!..!`), рендер данные не чинит и не падает.
    """
    out.parent.mkdir(parents=True, exist_ok=True)
    risk_labels = {1: "консервативный", 2: "умеренно-консервативный",
                   3: "сбалансированный", 4: "умеренно-агрессивный",
                   5: "агрессивный"}
    if version in LAYERED_GENERATORS:
        gen_l = layered_generator(version, seed, n)

        def rows():
            for i in range(n):
                yield gen_l.expert_row(i)

        header_extra = (
            f"> Срез дат (все дедлайны относительно него): "
            f"{gen_l.frozen_today.isoformat()}. Небольшая доля записей намеренно "
            "некорректна — как сырая выгрузка из CRM (битые суммы/даты/поля, "
            "дубли id); такие значения показаны как есть в `!..!`, карточки "
            "их не чинят.\n"
        )
    else:
        gen = PortraitGenerator(seed, version=version)

        def rows():
            for i in range(n):
                portrait = gen.generate(i)
                portrait["id"] = f"SP-{i:05d}"
                yield portrait

        header_extra = ""
    written = 0
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(
            f"# Портреты датасета v{version} — {n} шт. (seed {seed})\n\n"
            "> Сухие входные данные без подсказок: тип портрета и расчётные "
            "показатели намеренно не приводятся. Регенерация: "
            "`python -m tools.model_validation.dataset_export markdown ...`\n"
            + header_extra
        )
        for row in rows():
            risk = row.get("risk_tolerance")
            risk_text = (f"риск {risk} ({risk_labels[risk]})"
                         if risk in risk_labels else f"риск !{risk!r}!")
            fh.write(
                f"\n### {row['id']} · {risk_text} · "
                f"безрисковая ставка {_fmt_rate(row.get('r_bench'))}\n"
            )
            income = row.get("income_total", "!поле отсутствует!")
            fh.write(
                f"Доход {_fmt_cell(income)} ₽/мес · "
                f"Расходы {_fmt_cell(row.get('expense_total'))} ₽/мес · "
                f"Накопления {_fmt_cell(row.get('bliq'))} ₽\n"
            )
            obligations = row.get("obligations") or []
            if obligations:
                items = "; ".join(
                    f"«{o.get('name', '?')}» — остаток {_fmt_cell(o.get('amount'))} ₽, "
                    f"ставка {_fmt_rate(o.get('interest_rate'))}, "
                    f"платёж {_fmt_cell(o.get('monthly_payment'))} ₽/мес"
                    for o in obligations
                )
                fh.write(f"Кредиты: {items}\n")
            else:
                fh.write("Кредиты: нет\n")
            goals = row.get("goals") or []
            if goals:
                items = "; ".join(
                    f"«{g.get('name', '?')}» — {_fmt_cell(g.get('target_amount'))} ₽ "
                    f"(накоплено {_fmt_cell(g.get('current_amount'))}), "
                    + _fmt_deadline(g)
                    for g in goals
                )
                fh.write(f"Цели: {items}\n")
            else:
                fh.write("Цели: нет\n")
            written += 1
    return written


def outcomes_filename(model_version: str, dataset_version: int) -> str:
    """Имя csv-снимка: model_outcomes_<модель>_on_v<датасет>.csv.gz."""
    mv = model_version.replace(".", "_")
    return f"model_outcomes_{mv}_on_v{dataset_version}.csv.gz"


def results_filename(model_version: str, dataset_version: int) -> str:
    """Имя читаемой сводки: model_results_<модель>_on_v<датасет>.md."""
    mv = model_version.replace(".", "_")
    return f"model_results_{mv}_on_v{dataset_version}.md"


def _summarise_outcomes(rows: list[dict], gen) -> dict:
    """Числа для сводки: статусы, слои, вердикт D, доминанты, lump."""
    from collections import Counter
    key = {r["id"]: gen.coordinator_key(int(r["id"].split("-")[1]))
           for r in rows}
    status_counts = dict(Counter(r["status"] for r in rows))
    layers: dict[str, dict] = {}
    for r in rows:
        la = key[r["id"]]["layer"]
        layers.setdefault(la, Counter())[r["status"]] += 1
    d_rows = [r for r in rows if key[r["id"]]["layer"] == "D"]
    d_invalid = sum(1 for r in d_rows if r["status"] == "invalid")
    false_pos = sum(1 for r in rows
                    if key[r["id"]]["layer"] != "D" and r["status"] == "invalid")
    dom = dict(Counter(r["dom"] for r in rows if r["status"] == "ok"))
    lumps = [float(r.get("model_lump") or 0) for r in rows]
    nz = [x for x in lumps if x > 0]
    return {
        "status_counts": status_counts,
        "layers": {la: dict(c) for la, c in layers.items()},
        "d_invalid": d_invalid, "d_total": len(d_rows),
        "false_positives_on_valid": false_pos,
        "dominants_ok": dom,
        "lump_share": round(100 * len(nz) / len(rows), 1) if rows else 0.0,
    }


def _render_summary(model_version: str, dataset_version: int,
                    stats: dict) -> str:
    """Читаемая .md-сводка прогона (нейминг и числа — из stats)."""
    sc = stats["status_counts"]
    total = sum(sc.values())
    lines = [
        f"# Портреты датасета v{dataset_version} через модель "
        f"{model_version.replace('_', '.')} — результаты",
        "",
        f"Прогон {total} портретов через модель "
        f"**{model_version.replace('_', '.')}**. Ответ только модели "
        "(эксперты отдельно).",
        "",
        "## Статусы",
        "",
        f"- ok: {sc.get('ok', 0)} · deficit: {sc.get('deficit', 0)} · "
        f"invalid: {sc.get('invalid', 0)}",
        "",
        "## По слоям",
        "",
    ]
    for la in sorted(stats["layers"]):
        c = stats["layers"][la]
        lines.append(f"- {la}: {c}")
    lines += [
        "",
        "## Робастность",
        "",
        f"- Слой D (битые записи): {stats['d_invalid']}/{stats['d_total']} "
        f"отклонены как invalid, ложных на валидных: "
        f"{stats['false_positives_on_valid']}.",
        "",
        "## Доминанты (ok)",
        "",
        f"- {stats['dominants_ok']}",
        "",
        f"Разовые ходы модели: {stats['lump_share']}% портретов.",
        "",
        "Построчные результаты — "
        f"`knowledge/model_validation/"
        f"{outcomes_filename(model_version, dataset_version)}`.",
    ]
    return "\n".join(lines) + "\n"


def run_model_over_dataset(dataset_version: int, seed: int, model_version: str,
                           out_dir: Path, n: int = 12000) -> dict:
    """Один прогон модели по датасету → оба выходных файла + числа сводки.

    Имена файлов кодируют версию модели и версию датасета (см.
    `docs/model/model_run_output_standard.md`). Ручной набор имени не нужен.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / outcomes_filename(model_version, dataset_version)
    export_model_outcomes(csv_path, n=n, seed=seed, version=dataset_version)
    with gzip.open(csv_path, "rt", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    gen = layered_generator(dataset_version, seed, n)
    stats = _summarise_outcomes(rows, gen)
    md_path = out_dir / results_filename(model_version, dataset_version)
    md_path.write_text(_render_summary(model_version, dataset_version, stats),
                       encoding="utf-8")
    return {"outcomes_path": csv_path, "results_path": md_path, **stats}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Экспорт датасетов валидации")
    parser.add_argument(
        "what",
        choices=("portraits", "outcomes", "expert-pack", "markdown",
                 "coordinator-key", "run")
    )
    parser.add_argument("--out", type=Path)
    parser.add_argument("--n", type=int, default=12000)
    parser.add_argument("--seed", type=int, default=20260702)
    parser.add_argument("--version", type=int, default=2,
                        choices=(1, 2, 3, 4))
    parser.add_argument("--chunk-size", type=int, default=3000)
    parser.add_argument("--dataset-version", type=int, choices=(2, 3, 4))
    parser.add_argument("--model-version", type=str,
                        help="версия матмодели, напр. v3_4_0")
    parser.add_argument("--out-dir", type=Path)
    args = parser.parse_args(argv)
    if args.what != "run" and args.out is None:
        parser.error("--out обязателен")

    if args.what == "run":
        if not args.model_version:
            parser.error("--model-version обязателен: версия МАТМОДЕЛИ "
                         "(напр. v3_4_0) — это НЕ версия кода APP_VERSION")
        res = run_model_over_dataset(
            model_version=args.model_version,
            dataset_version=args.dataset_version, seed=args.seed,
            out_dir=args.out_dir or args.out, n=args.n)
        print(f"run: модель {args.model_version} x датасет v{args.dataset_version}")
        print(f"  outcomes -> {res['outcomes_path']}")
        print(f"  results  -> {res['results_path']}")
        print(f"  статусы: {res['status_counts']}; "
              f"D {res['d_invalid']}/{res['d_total']}, "
              f"ложных {res['false_positives_on_valid']}")
        return 0

    if args.what == "coordinator-key":
        written = export_coordinator_key(args.out, n=args.n, seed=args.seed,
                                         version=args.version)
        print(f"coordinator-key: {written} строк -> {args.out}")
        return 0
    if args.what == "expert-pack":
        files = export_expert_pack(
            args.out, n=args.n, seed=args.seed,
            version=args.version, chunk_size=args.chunk_size,
        )
        print(f"expert-pack: {args.n} строк -> {len(files)} файлов в {args.out}")
        return 0
    fn = {
        "portraits": export_portraits,
        "outcomes": export_model_outcomes,
        "markdown": export_markdown,
    }[args.what]
    written = fn(args.out, n=args.n, seed=args.seed, version=args.version)
    print(f"{args.what}: {written} строк -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
