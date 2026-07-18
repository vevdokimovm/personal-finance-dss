# Эталон независимой экспертизы мат-модели — 12 000 портретов

## Что здесь

`joined.csv.gz` — сопоставление **12 000 синтетических портретов** по пяти
источникам: выход модели FINPILOT v3.0.0 + рекомендации четырёх независимых
экспертных движков (V, M, J, S). Первичный материал независимой экспертизы
июля 2026 (`docs/reports/testing/independent_expert_review_2026_07.md`),
по которой откалибрована модель v3.1.0.

## Воспроизводимость

Входные портреты в файле НЕ хранятся — они детерминированно регенерируются:

```
PortraitGenerator(seed=20260702, version=1)   # строго v1!
```

Совпадение доказано сверкой rt/kind/risk до копейки (self-check стенда:
статус 12000/12000, доминанта 11998/12000 — два тай-брейка argmax).
Генератор v1 сохранён в `tools/portrait_testing/generator.py` бит-в-бит
именно ради этого файла; для новых прогонов используется v2.

## Как измерить согласие модели с экспертами

```
python -m tools.model_validation.expert_agreement \
    --joined knowledge/model_validation/joined.csv.gz \
    --report docs/reports/testing/expert_agreement_v3_1_0.md \
    --title "модель v3.1.0 (после G1/G2/G3/G5/G6)"
```

Метрика: доминирующее направление плана (debt / reserve / goals+, где goals+
объединяет цели и инвестиции) против консенсуса >= 3 из 4 экспертов на
платёжеспособных портретах. История: v3.0.0 — 51.9%; v3.1.0 — **87.4%**
(коридор согласия самих экспертов между собой: 85.6–95.6%).

## Схема колонок joined.csv.gz

`id, kind, risk` — портрет; `model_*` — статус/показатели/сплит/доминанта
модели v3.0.0; `{v,m,j,s}_{status,dom,res,debt,goal,inv,lump}` — статус,
доминанта и распределение каждого эксперта (res/debt/goal/inv — месячный
поток по бакетам, lump — разовые ходы из запаса).

## Материализованные датасеты (v6.1.0)

| Файл | Схема |
|---|---|
| `portraits_v1_seed20260702.jsonl.gz` | Портреты эталона (вход): 1 JSON/строка — id (SP-XXXXX), kind, income_total, expense_total, obligations[], goals[] (даты ISO), bliq, r_bench, risk_tolerance, l_min |
| `portraits_v2_seed20260702.jsonl.gz` | То же для калиброванного генератора v2 — датасет второй сертификации |
| `model_outcomes_v3_1_0_on_v1.csv.gz` | Ответ модели v3.1.0 на портретах v1: id, kind, risk, status, rt, lt, dt, xo, xr, xg, invest, dom, dt_alert, crisis_severity, crisis_actions. Колонки xg и invest независимы (goals+ = xg + invest) |
| `model_outcomes_v3_1_0_on_v2.csv.gz` | То же на портретах v2 — исторический снимок (модель на момент v6.1.0) |
| `model_outcomes_v3_3_0_on_v2.csv.gz` | Ответ модели v3.3.0 (as certified, floor 1.0) на портретах v2 (код v6.12.3) — модельная половина второй сертификации; согласие 78.9%. Дельта против снимка v3.1.0: 0 смен статуса, 4 смены доминанты, 12 сплит-дрейфов > 6 коп. на 12 000 (G7-каскад остатка); разбор — `docs/reports/testing/model_outcomes_v3_3_0_on_v2.md` |
| `model_outcomes_v3_4_0_on_v2.csv.gz` | Ответ ТЕКУЩЕЙ модели v3.4.0 (floor 2.0, ADR-006 update) на портретах v2 (код v6.13.0); согласие 88.0% — `docs/reports/testing/expert_certification_round2.md` |
| `joined_v2.csv.gz` | Joined второй сертификации: модельная половина v3.4.0 + 4 свежих эксперта (v/m/j/s). Сборка — `tools/model_validation/build_joined.py`; сырые CSV и ревью экспертов — `docs/model/expert_certification/iterations/2/` |
| `portraits_v3_seed20260716.jsonl.gz` | КАНОНИЧЕСКИЙ размеченный датасет v3 (12 000; слои A–E, meta первой строкой): генератор `tools/portrait_testing/generator_v3.py`, приёмка `tests/test_generator_v3.py`, ТЗ — `docs/model/expert_certification/iterations/2/expert_feedback_aggregate.md` §6 |
| `expert_portraits_v3_part1..4.jsonl.gz` | СЛЕПОЙ пакет v3 для раунда 3 (проекция без меток; дубли id и битые записи слоя D доживают до эксперта намеренно). Бриф — `docs/model/expert_brief_v3.md` (status=invalid, run_metadata обязателен) |
| `portraits_v3_coordinator_key.csv.gz` | Ключ координатора v3: id → layer/kind/pair_id/pair_relation/expected_error/id_override — слепота экспертов сохраняется, приёмка и стенд размечают по нему |
| `model_outcomes_v3_4_0_on_v3.csv.gz` | Модельная половина раунда 3: v3.4.0 + FLOW_EPS на 12 000 портретов v3 (слой D — `status=invalid`, колонки `invalid_reason` и `model_lump`; срез 2026-07-16). Анализ — `round3_model_half_analysis.py`, отчёты — `round3_model_half.md`, `expert_certification_round3.md` |
| `joined_v3.csv.gz` | Joined третьей сертификации: модель + 4 эксперта, сопоставление ПО ПОРЯДКУ строк (`build_joined_v3.py`, fail-loud id-сверка); согласие 67.5% (action-adjusted 76.3%) при коридоре 64.8–88.0. Сырые артефакты — `docs/model/expert_certification/iterations/3/` |

Регенерация любого файла: `tools/model_validation/dataset_export.py`
(portraits / outcomes / expert-pack / markdown, детерминировано по seed+version).
Экспертный пакет (сухие чанки без подсказок + бриф `docs/model/expert_brief_v2.md`)
и полный markdown-каталог — регенерируемые артефакты, в архиве не хранятся. История версий модели
и генератора — `docs/model/README.md`.
