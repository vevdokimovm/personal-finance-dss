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
    if version == 3:
        gen3 = PortraitGeneratorV3(seed, n=n)
        with gzip.open(out, "wt", encoding="utf-8") as fh:
            fh.write(json.dumps(_jsonable(gen3.meta()), ensure_ascii=False) + "\n")
            for i in range(n):
                portrait = _jsonable(gen3.generate(i))
                portrait["id"] = f"SP3-{i:05d}"
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


def export_coordinator_key(out: Path, n: int, seed: int) -> int:
    """Ключ координатора v3: id -> метки (слепота экспертов сохраняется)."""
    gen3 = PortraitGeneratorV3(seed, n=n)
    out.parent.mkdir(parents=True, exist_ok=True)
    fields = ("id", "layer", "kind", "pair_id", "pair_role",
              "pair_relation", "expected_error", "id_override")
    written = 0
    with gzip.open(out, "wt", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for i in range(n):
            row = gen3.coordinator_key(i)
            writer.writerow({k: ("" if row.get(k) is None else row[k])
                             for k in fields})
            written += 1
    return written


OUTCOME_FIELDS = (
    "id", "kind", "risk", "status", "rt", "lt", "dt",
    "xo", "xr", "xg", "invest", "dom",
    "dt_alert", "crisis_severity", "crisis_actions", "invalid_reason",
)


def _export_outcomes_v3(out: Path, n: int, seed: int) -> int:
    """Outcomes для датасета v3: слой D уходит в status=invalid БЕЗ запуска модели.

    Правило invalid зеркально экспертному брифу v3 (`portrait_validation`).
    id — канонические SP3-{i:05d} (уникальные, стыкуются с ключом координатора);
    дубли id слоя D — дефект уровня выгрузки, сборщик joined раунда 3
    сопоставляет ответы экспертов по порядку строк, не по id.
    """
    gen3 = PortraitGeneratorV3(seed, n=n)
    today = datetime.combine(gen3.frozen_today, time(12, 0))
    out.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with gzip.open(out, "wt", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=OUTCOME_FIELDS)
        writer.writeheader()
        for i in range(n):
            portrait = gen3.generate(i)
            reason = invalid_reason(portrait)
            if reason is not None:
                writer.writerow({
                    "id": f"SP3-{i:05d}",
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
                "id": f"SP3-{i:05d}",
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
            })
            written += 1
    return written


def export_model_outcomes(out: Path, n: int, seed: int, version: int) -> int:
    """Прогоняет n портретов через run_planning и пишет выход модели в csv.gz.

    xo/xr/xg — эффективный сплит лучшего плана; invest — инвестиционный транш
    (в xg НЕ включён: колонки независимы, семантику goals+inv собирает
    потребитель). Кризисные поля — охват G2.
    """
    if version == 3:
        return _export_outcomes_v3(out, n=n, seed=seed)
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
    gen3 = PortraitGeneratorV3(seed, n=n) if version == 3 else None
    gen = None if version == 3 else PortraitGenerator(seed, version=version)
    try:
        for i in range(n):
            if i % chunk_size == 0:
                if fh is not None:
                    fh.close()
                part = i // chunk_size + 1
                path = out_dir / f"expert_portraits_v{version}_part{part}.jsonl.gz"
                fh = gzip.open(path, "wt", encoding="utf-8")
                files.append(path)
                if version == 3:
                    part_meta = {
                        "__meta__": True, "dataset_version": 3, "part": part,
                        "rows": min(chunk_size, n - i),
                        "frozen_today": gen3.frozen_today.isoformat(),
                    }
                    fh.write(json.dumps(part_meta, ensure_ascii=False) + "\n")
            if version == 3:
                row = _jsonable(gen3.expert_row(i))
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
    if version == 3:
        gen3 = PortraitGeneratorV3(seed, n=n)

        def rows():
            for i in range(n):
                yield gen3.expert_row(i)

        header_extra = (
            f"> Срез дат (все дедлайны относительно него): "
            f"{gen3.frozen_today.isoformat()}. Небольшая доля записей намеренно "
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Экспорт датасетов валидации")
    parser.add_argument(
        "what",
        choices=("portraits", "outcomes", "expert-pack", "markdown",
                 "coordinator-key")
    )
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--n", type=int, default=12000)
    parser.add_argument("--seed", type=int, default=20260702)
    parser.add_argument("--version", type=int, default=2, choices=(1, 2, 3))
    parser.add_argument("--chunk-size", type=int, default=3000)
    args = parser.parse_args(argv)

    if args.what == "coordinator-key":
        written = export_coordinator_key(args.out, n=args.n, seed=args.seed)
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
