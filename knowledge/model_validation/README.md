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
| `model_outcomes_v3_1_0_on_v2.csv.gz` | То же на портретах v2 — половина будущего joined второй сертификации |

Регенерация любого файла: `tools/model_validation/dataset_export.py`
(portraits / outcomes, детерминировано по seed+version). История версий модели
и генератора — `docs/model/README.md`.
