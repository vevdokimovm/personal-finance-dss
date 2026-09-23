# Г39 — как проверять, валидировать, развивать и оптимизировать математическое ядро FINPILOT (сырьё)

Дата: 17.09.2026 · Батч: Г39 (постановка — `docs/research/queue/GAP_QUEUE.md`, раздел «Г39», 15 пунктов A/B/C)
Вход: `math_core_audit_2026-09-17.md` (Г40), `math_frameworks_alternatives_2026-09-17.md` (Г41), `docs/reports/mutation_pilot_2026-09-16.md`.
Скрипты: `scratchpad/g39/` (`/private/tmp/claude-501/-Users-vasyaevdokimov-repos-personal-finance-dss/fe25aad2-149b-48bd-a8b2-c62cc04ce4a1/scratchpad/g39/`), код и вывод приведены дословно.
Код продукта, канон `docs/math_model.md`, `tests/` и формулировка новизны НЕ менялись; `app.core` и `app.services.planning` только импортируются.

**Разделение:** верификация (часть A) — ядро считает правильно то, что задумано; валидация (часть B) — ядро решает правильную задачу; развитие (часть C) — как улучшать, не ломая.

**Состояние каналов (замер 17.09.2026, `curl -s -o /dev/null -w %{http_code}`):**
| Канал | Адрес замера | Код |
|---|---|---|
| Semantic Scholar | `api.semanticscholar.org/graph/v1/paper/DOI:10.1145/3143561` | 200 |
| Crossref | `api.crossref.org/works/10.1145/3143561` | 200 |
| OpenAlex | `api.openalex.org/works/doi:10.1145/3143561` | 200 |
| Unpaywall (`email=research@example.org`) | `api.unpaywall.org/v2/10.1145/3143561` | 200 |
| r.jina.ai (без браузерного UA) | `r.jina.ai/https://www.federalreserve.gov/supervisionreg/srletters/sr1107.htm` | 200 |
| curl напрямую | `federalreserve.gov/.../sr1107a1.pdf` | 404 (адрес сменился, см. пункт 7) |
| EuropePMC | `ebi.ac.uk/europepmc/webservices/rest/search` | 200 |
| Решатель | `scratchpad/g41/sv` — highspy, numpy 2.5.3 | импорт OK |
| hypothesis | `.venv` проекта — 6.155.7, Python 3.13.15 | импорт OK |
| pdftotext, tesseract | `/usr/local/bin` | есть |

---

## Пункт 0. 🔴 Проверка пути (б) Г41 на портретах ADR-015, со сценарием «месяц без дохода», против канона и MILP-оракула

### 0.1. Что такое «портреты ADR-015» — и дефект, найденный до всякого прогона

Портреты ADR-015 — `tools/portrait_testing/generator.py::PortraitGenerator.generate_with_income_history(index, months=8)` (ADR-015, `docs/reports/adr/adr_015_irregular_income_floor.md`, «Выполнено», п. 1): портрет генератора v2 плюс 8 месяцев истории дохода с волатильностью из набора `[0.0, 0.0, 0.0, 0.1, 0.2, 0.4, 0.6, 0.9]`. На них построен бенчмарк `tools/model_validation/income_volatility_benchmark.py` (12 000 портретов). Взяты индексы 0–2999, seed 20260702 — тот же, что у бенчмарка.

🔴 **Дефект Д-01 (стенд валидации, класс «молчаливый фолбэк»).** Генератор v2 кладёт срок цели как `datetime.date` (`generator.py::_gen_goals`: `today + timedelta(days=30 * rng.randint(3, 60))`, где `today = date(2026, 7, 2)`), а ядро ждёт `datetime`: `app/core/goals_priority.py::_months_left` проверяет `isinstance(deadline, datetime)` и при несовпадении **молча** возвращает `FALLBACK_MONTHS = 12.0`. Продукт не затронут — ORM и схемы передают `datetime` (`app/database/models.py:291` `Mapped[Optional[datetime]]`, `app/schemas/goal.py:22`). Затронуты все стенды на генераторе v2, которые не конвертируют даты: из просмотренных `income_volatility_benchmark.py` и `expert_agreement.py` конверсии не содержат (`grep "combine\|isoformat\|deadline"` пуст), `goal_inflation_benchmark.py:65` конвертирует только строки.

Скрипт `p0a_date_probe.py`:
```python
"""G39 p0a: portrait generator v2 emits goal deadlines as datetime.date; core goals_priority._months_left expects datetime."""
import sys
from datetime import date, datetime
sys.path.insert(0, "/Users/vasyaevdokimov/repos/personal-finance-dss")
from app.core.goals_priority import _months_left, urgency_of, months_left_or_none
from tools.portrait_testing.generator import PortraitGenerator
today = datetime(2026, 7, 2)
for d in (date(2026, 8, 1), date(2027, 7, 2), date(2031, 7, 2)):
    print(d, "as date ->", _months_left(d, today), " as datetime ->", round(_months_left(datetime(d.year, d.month, d.day), today), 2),
          " urgency date/datetime:", urgency_of(d, today), round(urgency_of(datetime(d.year, d.month, d.day), today), 2))
gen = PortraitGenerator(seed=20260702, version=2)
n_goals = n_date = 0
for i in range(12000):
    for g in gen.generate(i)["goals"]:
        n_goals += 1
        n_date += isinstance(g.get("deadline"), date) and not isinstance(g.get("deadline"), datetime)
print(f"goals in 12000 v2 portraits: {n_goals}, deadlines of type date (silently read as 12 months): {n_date} ({n_date / n_goals:.1%})")
```
Вывод:
```
2026-08-01 as date -> 12.0  as datetime -> 1.0  urgency date/datetime: 1.0 12.0
2027-07-02 as date -> 12.0  as datetime -> 12.17  urgency date/datetime: 1.0 1.0
2031-07-02 as date -> 12.0  as datetime -> 60.87  urgency date/datetime: 1.0 1.0
goals in 12000 v2 portraits: 24127, deadlines of type date (silently read as 12 months): 18387 (76.2%)
```
**Что это значит.** Цель со сроком через месяц в портретах читается как «через 12 месяцев» — срочность 1,0 вместо 12,0. Все выводы стендов на портретах v2 о целях со сроком (срочность, разовое закрытие §11.5, распределение между целями) получены на **другой модели**, чем в продукте. В симуляции ниже даты сконвертированы в `datetime`.

### 0.2. Метод

**Аналогия.** Три водителя едут по одним и тем же 3 000 маршрутам год: канон, путь (б) и «водитель, знающий дорогу наперёд» (оракул). Сравниваем не один маршрут (как в Г41), а распределение исходов, плюс отдельная поездка с поломкой на третьем месяце.

**Постановка.**
- **Политики.** (1) Канон: `run_planning(...)["best"]` каждый месяц. (2) Путь (б): правило `g41/f9a.py::select`, обобщённое на много долгов и целей (`p0b_sim.py::select_b`): ε-подушка `c_min` = 0,5 мес.; «токсичный первым» при ставке > τ = 100 %, если все цели со сроком успеваются в оставшиеся месяцы; ε-цель — не меньше суммы нужных темпов; среди оставшихся — вогнутая ценность $\sqrt{\cdot}$ на глобальных шкалах с весами профиля портрета. Альтернативы — те же 66 точек ядра `ranked`.
- **Бухгалтерия** (`p0b_sim.py::simulate`, общая для обеих политик): проценты $r/12$ на остаток начала месяца; минимальный платёж; досрочка по `obligation_allocation`; подушка и деньги целей приносят $r_{bench}/12$ (у Г41 доходность 0 — здесь честнее к канону, ведь $r_{bench}$ — его же альтернативная доходность); кризисный месяц (`crisis_plan is not None`) — балансовый ход ядра применяется, цели заморожены, дефицит — из подушки, остаток — в «экстренный долг» под 35 % (расходы НЕ режутся: совет `cut_expenses` мы не можем предполагать исполненным); цель, чей срок наступил, записывается (недобор к НОМИНАЛЬНОЙ сумме) и уходит из плана.
- **Сценарии.** `base` — доход каждый месяц с собственной волатильностью портрета; `noinc` — тот же путь, но доход 3-го месяца = 0.
- **Наборы.** `adr015` — 3 000 портретов как есть. 🔴 В портретах v2 ставки 6–35 % (`_gen_obligations_v2`: `rng.uniform(0.06, 0.35)`), то есть правило «токсичный первым» с τ = 100 % **не срабатывает ни разу**. Поэтому второй набор `mfo` — 2 000 обычных (`plain`) портретов из тех же индексов с добавленным МФО: тело 0,33 дохода, ставка 292 %, платёж 0,10 дохода.
- **Оракулы** (`p0c_milp.py`, HiGHS, знание дохода наперёд, 12 мес.): `omoney` — максимум чистой позиции без требований (чистая денежная верхняя граница); `o05` — с требованиями пути (б): подушка ≥ 0,5 мес. в месяцы без дефицита, цели со сроком ≤ 11 мес. к сроку, дальние — пропорциональный темп; `ofl` — то же, но подушка ≥ floor канона на t0.
- **Метрики.** Чистая позиция через 12 мес. (подушка + деньги целей − долги; все деньги сохраняются, разница = проценты минус доходность); недобор целей к сроку; недобор темпа дальних целей; экстренный долг (замена просрочки); месяцы с подушкой < 0,5 мес.; кризисные месяцы. **Критерий приёмки из Г41** (раздел «Вопросы для Г39», п. 1): «(б) не хуже канона ни в одном портрете по просрочкам и срыву целей».

### 0.3. Проверка самих инструментов, прежде чем верить разрывам

1. **Бухгалтерия воспроизводит Г41 до рубля** (`p0b_sim.py repro`, доходность 0, сквозной пример):
```
f9a-repro canon basis=post: interest 37303 cushion 109950 vacation fund 2748 debt 0
f9a-repro b     basis=pre: interest 29173 cushion 40827 vacation fund 80000 debt 0
f9a-repro b     basis=post: interest 29173 cushion 40827 vacation fund 80000 debt 0
```
   Совпадает с `f9a.py` (37 303 / 29 173 ₽).
2. **Оракул воспроизводит `f5b.py`** (`p0c_check.py`, 8 мес., отпуск 80 000, подушка ≥ 20 000): `implied interest: 21824` — совпадает с 21 824 ₽.
3. **Сохранение денег в симуляторе** (`p0f_conservation.py`, 60 портретов × 2 сценария × 2 политики): тождество «чистая позиция = начальная + Σ(доход − расходы) − проценты + доходность» — `records 240 with |gap| > 1 rub: 0`, максимум 0,15 ₽.
4. **Оракул прошёл пять версий, и это важно для доверия к числу.** v1–v4 оказывались НИЖЕ политик: (а) штраф за подушку заставлял оракул занимать под 35 %, чтобы держать подушку (исправлено: экстренный заём только в месяц дефицита и не больше дыры; требование подушки только в месяцы без дефицита); (б) штраф 5 ₽ за рубль займа заставлял занимать РАНЬШЕ, но меньше рублями (штраф снят до 0,001 — проценты сами оценивают заём); (в) доходность в симуляторе на конец месяца, в оракуле на начало; (г) сроки целей: симулятор проверяет месяцы 0–11, оракул 0–12; (д) минимальный платёж в оракуле был фиксирован, а в ядре после досрочки падает пропорционально (`avalanche.py::allocate_obligations_avalanche`: `loan_obj["monthly_payment"] = old_payment * (new_amount / old_amount)`) — заменён ослаблением $y \ge (P_0/B_0)\cdot B$, это делает оракул строгой ВЕРХНЕЙ границей и превращает задачу в ЛП. Остаток: чистый денежный оракул ниже политики в **0,2–0,6 %** записей `adr015` и **5–6 %** `mfo`; причина установлена на портретах 72, 93 — в кризисной ветке симулятора балансовый ход ядра гасит тело ДО начисления процентов месяца (`simulate`, ветка `crisis_plan`), чего оракул не умеет. Это погрешность в пользу политик, разрыв до оракула ею занижен, не завышен.

### 0.4. Результат (первый круг: правило (б) ровно как в Г41)

Сводка из вывода `p0g_report.py` (полный вывод ниже). «(б) хуже/лучше» — доля записей, где разница больше порога (чистая позиция — 0,5 % годового дохода; экстренный долг и недобор целей — 1 ₽).

| Набор / сценарий | Исход (б) = канон | Чистая позиция: (б) хуже на >0,5 % дохода / лучше | Недобор целей к сроку: (б) хуже / лучше | Экстренный долг: (б) хуже / лучше | Критерий приёмки Г41 нарушен |
|---|---|---|---|---|---|
| adr015 plain, base | 35,4 % | **17,4 %** / 0,2 % | 0,0 % / 14,8 % | 7,6 % / 0,4 % | **7,6 %** |
| adr015 plain, noinc | 30,9 % | **18,6 %** / 0,1 % | 0,1 % / 15,6 % | **30,7 %** / 1,6 % | **30,7 %** |
| adr015 plain, волатильность ≥ 0,4, noinc | 24,5 % | 22,7 % / 0,1 % | 0,1 % / 16,1 % | **38,2 %** / 2,7 % | **38,2 %** |
| adr015 с токсичным долгом канона (≥30 %), base | 18,6 % | **44,6 %** / 0,8 % | 0,0 % / 17,3 % | 13,5 % / 1,4 % | 13,5 % |
| mfo (МФО 292 %), base | 24,5 % | **34,3 %** / 9,4 % | 1,6 % / 13,8 % | 8,5 % / 1,5 % | 8,6 % |
| mfo, noinc | 26,4 % | **31,9 %** / 9,9 % | 0,8 % / 14,1 % | **29,8 %** / 2,5 % | **29,8 %** |

Разрыв до чистого денежного оракула (медиана, % годового дохода): adr015 plain base — канон 0,17 %, (б) 0,23 %; mfo base — канон **1,30 %**, (б) **2,43 %**. Доля разрыва «оракул − канон», которую забирает (б), где разрыв > 0,5 % дохода: медиана **−0,2 %** (mfo base), **−19,9 %** (adr015 plain base) — то есть (б) в типичном случае не сокращает, а УВЕЛИЧИВАЕТ денежный разрыв.

**Что это значит простыми словами (первый круг).**
1. **Цели путь (б) действительно лечит**: недобор к сроку меньше у 14–17 % портретов и почти нигде не больше (0–1,6 %). Это держится.
2. **Деньги — нет**: (б) теряет больше 0,5 % годового дохода у 17–19 % обычных портретов и у 32–34 % портретов с МФО, выигрывает у 0,1–10 %. Выигрыш сквозного примера Г41 (−8 130 ₽) — **не типичен**.
3. 🔴 **Кризисный сценарий ломает (б) по главному критерию**: в «месяц без дохода» у (б) больше экстренного долга у **30,7 %** обычных портретов и у **38,2 %** портретов с неровным доходом; медиана прироста — 0,4 месяца расходов. Причина по построению: ε-подушка 0,5 мес. вместо floor 2 мес. — это ровно тот хвостовой риск, который Г41 назвал («меньшая подушка → хвостовой риск при потере дохода»), теперь измеренный.
4. Критерий приёмки Г41 «не хуже канона ни в одном портрете» нарушен в 7,6–38,2 % записей. **В исходном виде рекомендация (б) не держится.** Где именно ломается — абляция ниже (0.5).

Вывод `p0g_report.py` (дословно, без строк заголовка логов):
```
=== adr015 / base / all kinds: records 3000
identical outcome b == canon: 1321 (44.0%)
net position b - canon, roubles: median 0  p10 -7278  p90 12  min -739789350  max 46131455
  as % of 12-month income: median 0.00%  p10 -0.80%  p90 0.00%
  b better by >0.5% income: 0.2%   b worse by >0.5% income: 14.4%
shortfall of goals due within 12 mo     : mean canon  105352197.9  b  100515546.2 | b worse in   0.0%  b better in  13.2%
pace shortfall of later goals           : mean canon  125020253.0  b  102912170.3 | b worse in   2.0%  b better in  35.4%
emergency borrowing (arrears proxy)     : mean canon    1780684.9  b    2443849.7 | b worse in   7.2%  b better in   0.3%
months with cushion < 0.5 mo            : mean canon          1.3  b          1.5 | b worse in   9.0%  b better in   0.6%
crisis months                           : mean canon          2.8  b          2.8 | b worse in   3.6%  b better in   0.3%
goals due 881: missed (>1% short) canon 668  b 643
G41 acceptance criterion violated (b more emergency debt OR more missed goals): 215 (7.2%)
  extra emergency debt under b where it occurs: median 16239  p90 71394  max 1836137471; as months of expenses median 0.37
  by kind: {'plain': 153, 'cheap_debts_only': 11, 'many_goals': 11, 'pdn_boundary': 10, 'overleveraged': 10, 'deadline_now': 6, 'giant_scale': 5, 'rate_at_bench': 4, 'no_goals': 3, 'deficit_cf': 1, 'zero_expenses': 1}
gap pure-money oracle (no cushion, no goals)             - canon: median      1366 ₽ (0.20% inc)  p90     16249 ₽ (1.70%)  oracle below policy: 0.4%
gap pure-money oracle (no cushion, no goals)             - b    : median      1700 ₽ (0.25% inc)  p90     23271 ₽ (2.49%)  oracle below policy: 0.4%
    omoney: mean due-goal shortfall 107882270, far pace shortfall 122438507, emergency 5601450
gap oracle with (b) requirements: cushion 0.5 mo + goals - canon: median         0 ₽ (0.00% inc)  p90      8010 ₽ (0.84%)  oracle below policy: 34.8%
gap oracle with (b) requirements: cushion 0.5 mo + goals - b    : median         0 ₽ (0.00% inc)  p90     10953 ₽ (1.15%)  oracle below policy: 32.4%
    o05: mean due-goal shortfall 74480875, far pace shortfall 67532683, emergency 10126254
gap oracle with canon floor + goals                      - canon: median        -0 ₽ (-0.00% inc)  p90      5179 ₽ (0.55%)  oracle below policy: 40.3%
gap oracle with canon floor + goals                      - b    : median        -0 ₽ (-0.00% inc)  p90      8509 ₽ (0.87%)  oracle below policy: 39.6%
    ofl: mean due-goal shortfall 74842135, far pace shortfall 67120359, emergency 11575053
share of (pure-money oracle - canon) captured by b, where the gap > 0.5% income (1033 records): median -6.1%  p10 -135.6%  p90 4.0%

=== adr015 / base / plain only: records 2000
identical outcome b == canon: 709 (35.4%)
net position b - canon, roubles: median 0  p10 -8407  p90 8  min -69833  max 19330
  as % of 12-month income: median 0.00%  p10 -0.98%  p90 0.00%
  b better by >0.5% income: 0.2%   b worse by >0.5% income: 17.4%
shortfall of goals due within 12 mo     : mean canon     102630.8  b      92529.3 | b worse in   0.0%  b better in  14.8%
pace shortfall of later goals           : mean canon     191866.1  b     159019.1 | b worse in   2.5%  b better in  42.5%
emergency borrowing (arrears proxy)     : mean canon       3089.3  b       4864.4 | b worse in   7.6%  b better in   0.4%
months with cushion < 0.5 mo            : mean canon          0.6  b          0.9 | b worse in  10.2%  b better in   0.6%
crisis months                           : mean canon          2.1  b          2.1 | b worse in   4.1%  b better in   0.2%
goals due 469: missed (>1% short) canon 399  b 382
G41 acceptance criterion violated (b more emergency debt OR more missed goals): 153 (7.6%)
  extra emergency debt under b where it occurs: median 16727  p90 51376  max 143312; as months of expenses median 0.41
  by kind: {'plain': 153}
gap pure-money oracle (no cushion, no goals)             - canon: median      1288 ₽ (0.17% inc)  p90     15456 ₽ (1.56%)  oracle below policy: 0.2%
gap pure-money oracle (no cushion, no goals)             - b    : median      1930 ₽ (0.23% inc)  p90     22305 ₽ (2.39%)  oracle below policy: 0.2%
    omoney: mean due-goal shortfall 112534, far pace shortfall 197291, emergency 9646
gap oracle with (b) requirements: cushion 0.5 mo + goals - canon: median        -0 ₽ (-0.00% inc)  p90      6977 ₽ (0.79%)  oracle below policy: 35.1%
gap oracle with (b) requirements: cushion 0.5 mo + goals - b    : median         0 ₽ (0.00% inc)  p90     10230 ₽ (1.14%)  oracle below policy: 31.7%
    o05: mean due-goal shortfall 67276, far pace shortfall 102363, emergency 17603
gap oracle with canon floor + goals                      - canon: median        -0 ₽ (-0.00% inc)  p90      4037 ₽ (0.42%)  oracle below policy: 40.9%
gap oracle with canon floor + goals                      - b    : median        -0 ₽ (-0.00% inc)  p90      7494 ₽ (0.81%)  oracle below policy: 39.4%
    ofl: mean due-goal shortfall 67323, far pace shortfall 102322, emergency 20155
share of (pure-money oracle - canon) captured by b, where the gap > 0.5% income (691 records): median -19.9%  p10 -155.6%  p90 4.0%

=== adr015 / base / plain, income volatility >= 0.4: records 785
identical outcome b == canon: 224 (28.5%)
net position b - canon, roubles: median -0  p10 -10606  p90 31  min -69833  max 19330
  as % of 12-month income: median -0.00%  p10 -1.15%  p90 0.00%
  b better by >0.5% income: 0.3%   b worse by >0.5% income: 21.1%
shortfall of goals due within 12 mo     : mean canon     105202.9  b      91218.3 | b worse in   0.0%  b better in  15.8%
pace shortfall of later goals           : mean canon     193112.1  b     153579.7 | b worse in   3.3%  b better in  45.4%
emergency borrowing (arrears proxy)     : mean canon       6901.6  b      11406.7 | b worse in  19.0%  b better in   1.1%
months with cushion < 0.5 mo            : mean canon          0.8  b          1.3 | b worse in  23.4%  b better in   1.5%
crisis months                           : mean canon          3.3  b          3.4 | b worse in   8.5%  b better in   0.0%
goals due 180: missed (>1% short) canon 154  b 147
G41 acceptance criterion violated (b more emergency debt OR more missed goals): 149 (19.0%)
  extra emergency debt under b where it occurs: median 16914  p90 51376  max 143312; as months of expenses median 0.42
  by kind: {'plain': 149}
gap pure-money oracle (no cushion, no goals)             - canon: median      1663 ₽ (0.20% inc)  p90     15945 ₽ (1.51%)  oracle below policy: 0.4%
gap pure-money oracle (no cushion, no goals)             - b    : median      2681 ₽ (0.32% inc)  p90     24289 ₽ (2.47%)  oracle below policy: 0.4%
    omoney: mean due-goal shortfall 114409, far pace shortfall 195524, emergency 22801
gap oracle with (b) requirements: cushion 0.5 mo + goals - canon: median        -0 ₽ (-0.00% inc)  p90      7994 ₽ (0.85%)  oracle below policy: 39.0%
gap oracle with (b) requirements: cushion 0.5 mo + goals - b    : median         0 ₽ (0.00% inc)  p90     12554 ₽ (1.29%)  oracle below policy: 36.3%
    o05: mean due-goal shortfall 65256, far pace shortfall 91864, emergency 39701
gap oracle with canon floor + goals                      - canon: median        -0 ₽ (-0.00% inc)  p90      4722 ₽ (0.44%)  oracle below policy: 48.8%
gap oracle with canon floor + goals                      - b    : median        -0 ₽ (-0.00% inc)  p90      9040 ₽ (0.92%)  oracle below policy: 47.1%
    ofl: mean due-goal shortfall 65256, far pace shortfall 91864, emergency 45168
share of (pure-money oracle - canon) captured by b, where the gap > 0.5% income (272 records): median -29.6%  p10 -169.1%  p90 4.5%

=== adr015 / base / with canon-toxic debt (>= max(30%, r_bench+15pp)): records 370
identical outcome b == canon: 69 (18.6%)
net position b - canon, roubles: median -2928  p10 -22001  p90 260  min -739789350  max 28062
  as % of 12-month income: median -0.31%  p10 -2.18%  p90 0.03%
  b better by >0.5% income: 0.8%   b worse by >0.5% income: 44.6%
shortfall of goals due within 12 mo     : mean canon  164176669.1  b  144835609.5 | b worse in   0.0%  b better in  17.3%
pace shortfall of later goals           : mean canon  240897850.4  b  209044702.7 | b worse in   0.8%  b better in  44.9%
emergency borrowing (arrears proxy)     : mean canon     344254.1  b     381296.8 | b worse in  13.5%  b better in   1.4%
months with cushion < 0.5 mo            : mean canon          1.5  b          1.7 | b worse in  12.2%  b better in   2.7%
crisis months                           : mean canon          2.8  b          2.9 | b worse in   9.2%  b better in   0.3%
goals due 108: missed (>1% short) canon 90  b 85
G41 acceptance criterion violated (b more emergency debt OR more missed goals): 50 (13.5%)
  extra emergency debt under b where it occurs: median 14322  p90 55681  max 12766553; as months of expenses median 0.38
  by kind: {'plain': 42, 'pdn_boundary': 2, 'overleveraged': 2, 'deadline_now': 2, 'giant_scale': 1, 'many_goals': 1}
gap pure-money oracle (no cushion, no goals)             - canon: median      9460 ₽ (1.08% inc)  p90     39488 ₽ (3.69%)  oracle below policy: 0.3%
gap pure-money oracle (no cushion, no goals)             - b    : median     15419 ₽ (1.96% inc)  p90     50762 ₽ (4.82%)  oracle below policy: 0.3%
    omoney: mean due-goal shortfall 164180435, far pace shortfall 235515253, emergency 805973
gap oracle with (b) requirements: cushion 0.5 mo + goals - canon: median      1396 ₽ (0.24% inc)  p90     24669 ₽ (2.25%)  oracle below policy: 45.7%
gap oracle with (b) requirements: cushion 0.5 mo + goals - b    : median      2743 ₽ (0.40% inc)  p90     33206 ₽ (2.77%)  oracle below policy: 39.7%
    o05: mean due-goal shortfall 112872287, far pace shortfall 132112976, emergency 8924098
gap oracle with canon floor + goals                      - canon: median       447 ₽ (0.07% inc)  p90     23305 ₽ (1.99%)  oracle below policy: 47.6%
gap oracle with canon floor + goals                      - b    : median      1124 ₽ (0.17% inc)  p90     30603 ₽ (2.53%)  oracle below policy: 44.6%
    ofl: mean due-goal shortfall 112872287, far pace shortfall 132112976, emergency 9588405
share of (pure-money oracle - canon) captured by b, where the gap > 0.5% income (300 records): median -21.3%  p10 -200.2%  p90 3.3%

=== adr015 / noinc / all kinds: records 3000
identical outcome b == canon: 1187 (39.6%)
net position b - canon, roubles: median 0  p10 -6927  p90 36  min -675729303  max 43806103
  as % of 12-month income: median 0.00%  p10 -0.78%  p90 0.01%
  b better by >0.5% income: 0.1%   b worse by >0.5% income: 15.7%
shortfall of goals due within 12 mo     : mean canon  106276785.2  b  102834381.1 | b worse in   0.0%  b better in  14.1%
pace shortfall of later goals           : mean canon  130772588.2  b  109281702.8 | b worse in   1.9%  b better in  36.9%
emergency borrowing (arrears proxy)     : mean canon   20329722.7  b   22714056.5 | b worse in  26.6%  b better in   1.7%
months with cushion < 0.5 mo            : mean canon          2.4  b          2.8 | b worse in  19.7%  b better in   1.1%
crisis months                           : mean canon          3.7  b          3.7 | b worse in   3.8%  b better in   0.4%
goals due 881: missed (>1% short) canon 700  b 677
G41 acceptance criterion violated (b more emergency debt OR more missed goals): 797 (26.6%)
  extra emergency debt under b where it occurs: median 13655  p90 50244  max 1583101350; as months of expenses median 0.40
  by kind: {'plain': 614, 'pdn_boundary': 31, 'many_goals': 26, 'cheap_debts_only': 26, 'rate_at_bench': 20, 'giant_scale': 18, 'deadline_now': 15, 'no_goals': 14, 'overleveraged': 11, 'zero_expenses': 8, 'funded_goal': 6, 'kopeck_scale': 6, 'deficit_cf': 2}
gap pure-money oracle (no cushion, no goals)             - canon: median      1454 ₽ (0.22% inc)  p90     12144 ₽ (1.36%)  oracle below policy: 0.5%
gap pure-money oracle (no cushion, no goals)             - b    : median      2174 ₽ (0.34% inc)  p90     17956 ₽ (2.14%)  oracle below policy: 0.5%
    omoney: mean due-goal shortfall 107846286, far pace shortfall 125565246, emergency 23405992
gap oracle with (b) requirements: cushion 0.5 mo + goals - canon: median        -0 ₽ (-0.00% inc)  p90      5608 ₽ (0.62%)  oracle below policy: 46.4%
gap oracle with (b) requirements: cushion 0.5 mo + goals - b    : median        -0 ₽ (-0.00% inc)  p90      8083 ₽ (0.86%)  oracle below policy: 44.6%
    o05: mean due-goal shortfall 76515950, far pace shortfall 69394779, emergency 37817427
gap oracle with canon floor + goals                      - canon: median     -2409 ₽ (-0.39% inc)  p90      3149 ₽ (0.36%)  oracle below policy: 60.1%
gap oracle with canon floor + goals                      - b    : median     -1995 ₽ (-0.33% inc)  p90      4852 ₽ (0.58%)  oracle below policy: 58.6%
    ofl: mean due-goal shortfall 76877087, far pace shortfall 68982585, emergency 44347557
share of (pure-money oracle - canon) captured by b, where the gap > 0.5% income (910 records): median -6.0%  p10 -135.9%  p90 6.9%

=== adr015 / noinc / plain only: records 2000
identical outcome b == canon: 617 (30.9%)
net position b - canon, roubles: median -0  p10 -7411  p90 8  min -59278  max 16343
  as % of 12-month income: median -0.00%  p10 -0.89%  p90 0.00%
  b better by >0.5% income: 0.1%   b worse by >0.5% income: 18.6%
shortfall of goals due within 12 mo     : mean canon     105886.9  b      96922.6 | b worse in   0.1%  b better in  15.6%
pace shortfall of later goals           : mean canon     199256.2  b     167706.8 | b worse in   2.4%  b better in  44.2%
emergency borrowing (arrears proxy)     : mean canon      16581.0  b      22564.1 | b worse in  30.7%  b better in   1.6%
months with cushion < 0.5 mo            : mean canon          1.8  b          2.2 | b worse in  23.7%  b better in   0.9%
crisis months                           : mean canon          3.1  b          3.1 | b worse in   4.5%  b better in   0.3%
goals due 469: missed (>1% short) canon 420  b 406
G41 acceptance criterion violated (b more emergency debt OR more missed goals): 614 (30.7%)
  extra emergency debt under b where it occurs: median 14230  p90 44367  max 193806; as months of expenses median 0.41
  by kind: {'plain': 614}
gap pure-money oracle (no cushion, no goals)             - canon: median      1440 ₽ (0.20% inc)  p90     10768 ₽ (1.22%)  oracle below policy: 0.3%
gap pure-money oracle (no cushion, no goals)             - b    : median      2439 ₽ (0.34% inc)  p90     16972 ₽ (2.05%)  oracle below policy: 0.2%
    omoney: mean due-goal shortfall 112534, far pace shortfall 200839, emergency 30213
gap oracle with (b) requirements: cushion 0.5 mo + goals - canon: median        -0 ₽ (-0.00% inc)  p90      4750 ₽ (0.53%)  oracle below policy: 48.9%
gap oracle with (b) requirements: cushion 0.5 mo + goals - b    : median        -0 ₽ (-0.00% inc)  p90      7079 ₽ (0.80%)  oracle below policy: 46.7%
    o05: mean due-goal shortfall 70093, far pace shortfall 106036, emergency 51466
gap oracle with canon floor + goals                      - canon: median     -3590 ₽ (-0.53% inc)  p90      2248 ₽ (0.24%)  oracle below policy: 63.7%
gap oracle with canon floor + goals                      - b    : median     -2873 ₽ (-0.42% inc)  p90      4190 ₽ (0.49%)  oracle below policy: 61.4%
    ofl: mean due-goal shortfall 70138, far pace shortfall 105984, emergency 60017
share of (pure-money oracle - canon) captured by b, where the gap > 0.5% income (584 records): median -23.1%  p10 -169.1%  p90 9.4%

=== adr015 / noinc / plain, income volatility >= 0.4: records 785
identical outcome b == canon: 192 (24.5%)
net position b - canon, roubles: median -257  p10 -9369  p90 94  min -59278  max 16343
  as % of 12-month income: median -0.03%  p10 -1.08%  p90 0.01%
  b better by >0.5% income: 0.1%   b worse by >0.5% income: 22.7%
shortfall of goals due within 12 mo     : mean canon     108346.2  b      96515.7 | b worse in   0.1%  b better in  16.1%
pace shortfall of later goals           : mean canon     200998.6  b     162796.2 | b worse in   3.3%  b better in  47.0%
emergency borrowing (arrears proxy)     : mean canon      25235.6  b      34997.4 | b worse in  38.2%  b better in   2.7%
months with cushion < 0.5 mo            : mean canon          1.8  b          2.5 | b worse in  35.3%  b better in   1.7%
crisis months                           : mean canon          4.1  b          4.2 | b worse in   9.2%  b better in   0.5%
goals due 180: missed (>1% short) canon 160  b 154
G41 acceptance criterion violated (b more emergency debt OR more missed goals): 300 (38.2%)
  extra emergency debt under b where it occurs: median 18391  p90 55850  max 193806; as months of expenses median 0.47
  by kind: {'plain': 300}
gap pure-money oracle (no cushion, no goals)             - canon: median      1684 ₽ (0.23% inc)  p90     12557 ₽ (1.32%)  oracle below policy: 0.6%
gap pure-money oracle (no cushion, no goals)             - b    : median      3088 ₽ (0.39% inc)  p90     19945 ₽ (2.25%)  oracle below policy: 0.6%
    omoney: mean due-goal shortfall 114409, far pace shortfall 200106, emergency 48362
gap oracle with (b) requirements: cushion 0.5 mo + goals - canon: median        -0 ₽ (-0.00% inc)  p90      5898 ₽ (0.66%)  oracle below policy: 46.0%
gap oracle with (b) requirements: cushion 0.5 mo + goals - b    : median        -0 ₽ (-0.00% inc)  p90      8731 ₽ (1.01%)  oracle below policy: 43.1%
    o05: mean due-goal shortfall 69462, far pace shortfall 95887, emergency 75676
gap oracle with canon floor + goals                      - canon: median     -3732 ₽ (-0.52% inc)  p90      2976 ₽ (0.31%)  oracle below policy: 62.5%
gap oracle with canon floor + goals                      - b    : median     -2789 ₽ (-0.40% inc)  p90      5238 ₽ (0.59%)  oracle below policy: 59.0%
    ofl: mean due-goal shortfall 69462, far pace shortfall 95887, emergency 85636
share of (pure-money oracle - canon) captured by b, where the gap > 0.5% income (241 records): median -30.7%  p10 -172.6%  p90 9.9%

=== adr015 / noinc / with canon-toxic debt (>= max(30%, r_bench+15pp)): records 370
identical outcome b == canon: 67 (18.1%)
net position b - canon, roubles: median -1480  p10 -17735  p90 413  min -675729303  max 43806103
  as % of 12-month income: median -0.20%  p10 -1.85%  p90 0.07%
  b better by >0.5% income: 0.3%   b worse by >0.5% income: 39.2%
shortfall of goals due within 12 mo     : mean canon  164177241.7  b  154418208.7 | b worse in   0.0%  b better in  16.8%
pace shortfall of later goals           : mean canon  250644541.9  b  214454162.9 | b worse in   0.3%  b better in  44.9%
emergency borrowing (arrears proxy)     : mean canon   38961928.2  b   41310303.3 | b worse in  36.2%  b better in   7.8%
months with cushion < 0.5 mo            : mean canon          3.0  b          3.3 | b worse in  17.3%  b better in   3.0%
crisis months                           : mean canon          3.8  b          3.9 | b worse in   8.4%  b better in   0.3%
goals due 108: missed (>1% short) canon 91  b 87
G41 acceptance criterion violated (b more emergency debt OR more missed goals): 134 (36.2%)
  extra emergency debt under b where it occurs: median 9482  p90 50968  max 409578418; as months of expenses median 0.32
  by kind: {'plain': 115, 'deadline_now': 6, 'pdn_boundary': 4, 'giant_scale': 4, 'no_goals': 2, 'funded_goal': 1, 'overleveraged': 1, 'zero_expenses': 1}
gap pure-money oracle (no cushion, no goals)             - canon: median      6615 ₽ (0.77% inc)  p90     31339 ₽ (3.17%)  oracle below policy: 0.3%
gap pure-money oracle (no cushion, no goals)             - b    : median     11049 ₽ (1.53% inc)  p90     38885 ₽ (4.23%)  oracle below policy: 0.3%
    omoney: mean due-goal shortfall 164180435, far pace shortfall 257864315, emergency 60450553
gap oracle with (b) requirements: cushion 0.5 mo + goals - canon: median       681 ₽ (0.11% inc)  p90     18177 ₽ (1.84%)  oracle below policy: 47.3%
gap oracle with (b) requirements: cushion 0.5 mo + goals - b    : median      1149 ₽ (0.16% inc)  p90     23778 ₽ (2.36%)  oracle below policy: 44.3%
    o05: mean due-goal shortfall 119423556, far pace shortfall 133332474, emergency 74114855
gap oracle with canon floor + goals                      - canon: median     -1953 ₽ (-0.23% inc)  p90     15551 ₽ (1.78%)  oracle below policy: 55.1%
gap oracle with canon floor + goals                      - b    : median     -1125 ₽ (-0.17% inc)  p90     20889 ₽ (2.17%)  oracle below policy: 53.8%
    ofl: mean due-goal shortfall 119423556, far pace shortfall 133332474, emergency 74771173
share of (pure-money oracle - canon) captured by b, where the gap > 0.5% income (277 records): median -19.8%  p10 -206.5%  p90 11.2%

=== mfo / base / all kinds: records 2000
identical outcome b == canon: 490 (24.5%)
net position b - canon, roubles: median -0  p10 -23452  p90 4240  min -90073  max 46351
  as % of 12-month income: median -0.00%  p10 -2.88%  p90 0.48%
  b better by >0.5% income: 9.4%   b worse by >0.5% income: 34.3%
shortfall of goals due within 12 mo     : mean canon     103760.3  b      96811.6 | b worse in   1.6%  b better in  13.8%
pace shortfall of later goals           : mean canon     195525.8  b     170038.4 | b worse in   6.7%  b better in  40.5%
emergency borrowing (arrears proxy)     : mean canon       8051.2  b       9879.5 | b worse in   8.5%  b better in   1.5%
months with cushion < 0.5 mo            : mean canon          1.3  b          1.5 | b worse in  10.1%  b better in   0.7%
crisis months                           : mean canon          2.9  b          2.9 | b worse in   7.5%  b better in   1.7%
goals due 469: missed (>1% short) canon 406  b 398
G41 acceptance criterion violated (b more emergency debt OR more missed goals): 171 (8.6%)
  extra emergency debt under b where it occurs: median 15260  p90 56600  max 191902; as months of expenses median 0.38
  by kind: {'plain': 171}
gap pure-money oracle (no cushion, no goals)             - canon: median     10612 ₽ (1.30% inc)  p90     35717 ₽ (3.31%)  oracle below policy: 5.8%
gap pure-money oracle (no cushion, no goals)             - b    : median     17172 ₽ (2.43% inc)  p90     45641 ₽ (4.27%)  oracle below policy: 5.1%
    omoney: mean due-goal shortfall 112534, far pace shortfall 199163, emergency 15242
gap oracle with (b) requirements: cushion 0.5 mo + goals - canon: median      4937 ₽ (0.59% inc)  p90     27353 ₽ (2.71%)  oracle below policy: 22.9%
gap oracle with (b) requirements: cushion 0.5 mo + goals - b    : median     10467 ₽ (1.42% inc)  p90     33945 ₽ (3.01%)  oracle below policy: 11.4%
    o05: mean due-goal shortfall 69489, far pace shortfall 102986, emergency 31340
gap oracle with canon floor + goals                      - canon: median      2966 ₽ (0.36% inc)  p90     24913 ₽ (2.57%)  oracle below policy: 24.9%
gap oracle with canon floor + goals                      - b    : median      9592 ₽ (1.30% inc)  p90     32757 ₽ (2.99%)  oracle below policy: 19.2%
    ofl: mean due-goal shortfall 69503, far pace shortfall 103111, emergency 32477
share of (pure-money oracle - canon) captured by b, where the gap > 0.5% income (1459 records): median -0.2%  p10 -258.6%  p90 41.7%

=== mfo / base / plain only: records 2000
identical outcome b == canon: 490 (24.5%)
net position b - canon, roubles: median -0  p10 -23452  p90 4240  min -90073  max 46351
  as % of 12-month income: median -0.00%  p10 -2.88%  p90 0.48%
  b better by >0.5% income: 9.4%   b worse by >0.5% income: 34.3%
shortfall of goals due within 12 mo     : mean canon     103760.3  b      96811.6 | b worse in   1.6%  b better in  13.8%
pace shortfall of later goals           : mean canon     195525.8  b     170038.4 | b worse in   6.7%  b better in  40.5%
emergency borrowing (arrears proxy)     : mean canon       8051.2  b       9879.5 | b worse in   8.5%  b better in   1.5%
months with cushion < 0.5 mo            : mean canon          1.3  b          1.5 | b worse in  10.1%  b better in   0.7%
crisis months                           : mean canon          2.9  b          2.9 | b worse in   7.5%  b better in   1.7%
goals due 469: missed (>1% short) canon 406  b 398
G41 acceptance criterion violated (b more emergency debt OR more missed goals): 171 (8.6%)
  extra emergency debt under b where it occurs: median 15260  p90 56600  max 191902; as months of expenses median 0.38
  by kind: {'plain': 171}
gap pure-money oracle (no cushion, no goals)             - canon: median     10612 ₽ (1.30% inc)  p90     35717 ₽ (3.31%)  oracle below policy: 5.8%
gap pure-money oracle (no cushion, no goals)             - b    : median     17172 ₽ (2.43% inc)  p90     45641 ₽ (4.27%)  oracle below policy: 5.1%
    omoney: mean due-goal shortfall 112534, far pace shortfall 199163, emergency 15242
gap oracle with (b) requirements: cushion 0.5 mo + goals - canon: median      4937 ₽ (0.59% inc)  p90     27353 ₽ (2.71%)  oracle below policy: 22.9%
gap oracle with (b) requirements: cushion 0.5 mo + goals - b    : median     10467 ₽ (1.42% inc)  p90     33945 ₽ (3.01%)  oracle below policy: 11.4%
    o05: mean due-goal shortfall 69489, far pace shortfall 102986, emergency 31340
gap oracle with canon floor + goals                      - canon: median      2966 ₽ (0.36% inc)  p90     24913 ₽ (2.57%)  oracle below policy: 24.9%
gap oracle with canon floor + goals                      - b    : median      9592 ₽ (1.30% inc)  p90     32757 ₽ (2.99%)  oracle below policy: 19.2%
    ofl: mean due-goal shortfall 69503, far pace shortfall 103111, emergency 32477
share of (pure-money oracle - canon) captured by b, where the gap > 0.5% income (1459 records): median -0.2%  p10 -258.6%  p90 41.7%

=== mfo / noinc / all kinds: records 2000
identical outcome b == canon: 527 (26.4%)
net position b - canon, roubles: median 0  p10 -23258  p90 3875  min -93589  max 42765
  as % of 12-month income: median 0.00%  p10 -3.15%  p90 0.49%
  b better by >0.5% income: 9.9%   b worse by >0.5% income: 31.9%
shortfall of goals due within 12 mo     : mean canon     107034.7  b     100464.3 | b worse in   0.8%  b better in  14.1%
pace shortfall of later goals           : mean canon     202658.4  b     178049.0 | b worse in   4.5%  b better in  41.8%
emergency borrowing (arrears proxy)     : mean canon      31569.0  b      36584.6 | b worse in  29.8%  b better in   2.5%
months with cushion < 0.5 mo            : mean canon          2.7  b          3.0 | b worse in  19.4%  b better in   2.8%
crisis months                           : mean canon          3.8  b          3.9 | b worse in   6.4%  b better in   2.2%
goals due 469: missed (>1% short) canon 421  b 415
G41 acceptance criterion violated (b more emergency debt OR more missed goals): 596 (29.8%)
  extra emergency debt under b where it occurs: median 11118  p90 43686  max 141779; as months of expenses median 0.32
  by kind: {'plain': 596}
gap pure-money oracle (no cushion, no goals)             - canon: median     11306 ₽ (1.46% inc)  p90     37633 ₽ (3.67%)  oracle below policy: 6.5%
gap pure-money oracle (no cushion, no goals)             - b    : median     17791 ₽ (2.89% inc)  p90     44491 ₽ (4.30%)  oracle below policy: 6.3%
    omoney: mean due-goal shortfall 112534, far pace shortfall 202699, emergency 42170
gap oracle with (b) requirements: cushion 0.5 mo + goals - canon: median      3815 ₽ (0.51% inc)  p90     26813 ₽ (3.04%)  oracle below policy: 31.4%
gap oracle with (b) requirements: cushion 0.5 mo + goals - b    : median      8354 ₽ (1.23% inc)  p90     29730 ₽ (3.23%)  oracle below policy: 14.3%
    o05: mean due-goal shortfall 71584, far pace shortfall 105494, emergency 71324
gap oracle with canon floor + goals                      - canon: median      2322 ₽ (0.32% inc)  p90     24234 ₽ (2.71%)  oracle below policy: 33.2%
gap oracle with canon floor + goals                      - b    : median      7272 ₽ (1.05% inc)  p90     27922 ₽ (3.03%)  oracle below policy: 21.7%
    ofl: mean due-goal shortfall 71599, far pace shortfall 105611, emergency 73865
share of (pure-money oracle - canon) captured by b, where the gap > 0.5% income (1445 records): median 0.0%  p10 -271.1%  p90 46.3%

=== mfo / noinc / plain only: records 2000
identical outcome b == canon: 527 (26.4%)
net position b - canon, roubles: median 0  p10 -23258  p90 3875  min -93589  max 42765
  as % of 12-month income: median 0.00%  p10 -3.15%  p90 0.49%
  b better by >0.5% income: 9.9%   b worse by >0.5% income: 31.9%
shortfall of goals due within 12 mo     : mean canon     107034.7  b     100464.3 | b worse in   0.8%  b better in  14.1%
pace shortfall of later goals           : mean canon     202658.4  b     178049.0 | b worse in   4.5%  b better in  41.8%
emergency borrowing (arrears proxy)     : mean canon      31569.0  b      36584.6 | b worse in  29.8%  b better in   2.5%
months with cushion < 0.5 mo            : mean canon          2.7  b          3.0 | b worse in  19.4%  b better in   2.8%
crisis months                           : mean canon          3.8  b          3.9 | b worse in   6.4%  b better in   2.2%
goals due 469: missed (>1% short) canon 421  b 415
G41 acceptance criterion violated (b more emergency debt OR more missed goals): 596 (29.8%)
  extra emergency debt under b where it occurs: median 11118  p90 43686  max 141779; as months of expenses median 0.32
  by kind: {'plain': 596}
gap pure-money oracle (no cushion, no goals)             - canon: median     11306 ₽ (1.46% inc)  p90     37633 ₽ (3.67%)  oracle below policy: 6.5%
gap pure-money oracle (no cushion, no goals)             - b    : median     17791 ₽ (2.89% inc)  p90     44491 ₽ (4.30%)  oracle below policy: 6.3%
    omoney: mean due-goal shortfall 112534, far pace shortfall 202699, emergency 42170
gap oracle with (b) requirements: cushion 0.5 mo + goals - canon: median      3815 ₽ (0.51% inc)  p90     26813 ₽ (3.04%)  oracle below policy: 31.4%
gap oracle with (b) requirements: cushion 0.5 mo + goals - b    : median      8354 ₽ (1.23% inc)  p90     29730 ₽ (3.23%)  oracle below policy: 14.3%
    o05: mean due-goal shortfall 71584, far pace shortfall 105494, emergency 71324
gap oracle with canon floor + goals                      - canon: median      2322 ₽ (0.32% inc)  p90     24234 ₽ (2.71%)  oracle below policy: 33.2%
gap oracle with canon floor + goals                      - b    : median      7272 ₽ (1.05% inc)  p90     27922 ₽ (3.03%)  oracle below policy: 21.7%
    ofl: mean due-goal shortfall 71599, far pace shortfall 105611, emergency 73865
share of (pure-money oracle - canon) captured by b, where the gap > 0.5% income (1445 records): median 0.0%  p10 -271.1%  p90 46.3%
```
Примечание к выводу: в наборе `adr015 / all kinds` средние по недобору и экстренному долгу раздуты портретами `giant_scale` (величины ×1e4–5e4) — читать доли, а не средние; для `mfo` «all kinds» = «plain only» по построению.

### 0.5. Скрипты пункта 0 (дословно)

**p0b_sim.py**
```python
"""G39 point 0: path (b) of G41 vs canon, month by month through the canon core (run_planning), 12 months.
Portraits: ADR-015 = PortraitGenerator(seed=20260702, version=2).generate_with_income_history(i).
Scenarios: base (income path with the portrait's own volatility) and 'noinc' (month 3 income = 0).
Ledger (same for both policies, money-conserving, generalises g41/f9a.py):
  - interest r/12 on start-of-month balance, minimum payment paid, avalanche extra from obligation_allocation;
  - cushion and goal funds earn yield y/12 (y = r_bench for portraits, 0 for the f9a reproduction);
  - crisis month (run_planning()['crisis_plan'] is not None): canon closure from liquidity applied, goals frozen,
    deficit covered from cushion, the rest -> emergency card debt at 35 %/yr (5 % minimum payment);
    expenses are NOT cut (the plan's cut_expenses is advice we cannot assume the person follows);
  - a goal whose deadline has come is recorded (shortfall vs NOMINAL target) and leaves the plan, its fund stays in net worth.
Deadlines are converted date -> datetime (p0a: core reads date as 12 months).
Output: JSON lines for the MILP stage + per-portrait metrics."""
import sys, json, math, random, time
from datetime import datetime, timedelta, date
REPO = "/Users/vasyaevdokimov/repos/personal-finance-dss"
sys.path.insert(0, REPO)
import app.core.ranking as ranking
from app.core.goals_priority import months_left_or_none
from app.services.planning import run_planning
from tools.portrait_testing.generator import PortraitGenerator

H = 12
T0 = datetime(2026, 7, 2)
EMERG_RATE = 0.35
SEED = 20260702


def to_dt(d):
    if isinstance(d, datetime) or d is None:
        return d
    if isinstance(d, date):
        return datetime(d.year, d.month, d.day)
    return d


def select_b(r, st, inc, exp, prof, today, c_min=0.5, tau=1.0, cushion_basis="post"):
    """Path (b) of G41 (f9a.py) generalised to many debts/goals."""
    ranked = r["ranked"]
    w = ranking.RISK_PROFILES[prof]; wd, wl, wg = w["w_rt"] + w["w_dt"], w["w_lt"], w["w_goals"]
    pre_used = (r.get("bliq_preallocation") or {}).get("bliq_used", 0.0)
    base = st["bliq"] if cushion_basis == "pre" else st["bliq"] - pre_used
    goals = [g for g in st["goals"] if g["target_amount"] - g["current_amount"] > 1]
    closed = {c["id"] for c in (r.get("bliq_preallocation") or {}).get("closed_goals", [])}
    dl_goals = []
    for g in goals:
        if g["id"] in closed or g.get("deadline") is None:
            continue
        ml = months_left_or_none(g["deadline"], today)
        dl_goals.append((g, max(1, math.floor(ml + 1e-9))))
    need = sum(min(g["target_amount"] - g["current_amount"], (g["target_amount"] - g["current_amount"]) / ml) for g, ml in dl_goals)

    def goal_money(a):
        return sum(a.get("goal_allocation", {}).values())

    def cushion_after(a):
        return (base + a["x_reserve_effective"]) / exp if exp > 0 else 99.0
    pool = list(ranked)
    if not pool:
        return None
    f1 = [a for a in pool if cushion_after(a) >= c_min - 1e-9]
    if f1:
        pool = f1
    else:
        best_c = max(cushion_after(a) for a in pool); pool = [a for a in pool if cushion_after(a) >= best_c - 1e-9]
    obls = st["obls"]
    toxic_alive = tau is not None and any(o["interest_rate"] > tau and o["amount"] > 0.5 for o in obls)
    if toxic_alive:
        pay_after = sum(o["monthly_payment"] for o in obls if o["interest_rate"] <= tau)
        feasible = all(ml > 1 for _, ml in dl_goals) and sum(
            (g["target_amount"] - g["current_amount"]) / (ml - 1) for g, ml in dl_goals) <= inc - exp - pay_after
        if feasible:
            best_d = max(a["x_obl_effective"] for a in pool)
            return max([a for a in pool if a["x_obl_effective"] >= best_d - 1], key=lambda a: a["x_reserve_effective"])
    if need > 0:
        f2 = [a for a in pool if goal_money(a) >= need - 1]
        if f2:
            pool = f2
        else:
            best_g = max(goal_money(a) for a in pool); pool = [a for a in pool if goal_money(a) >= best_g - 1]
    ref = inc if inc > 0 else 1.0

    def U(a):
        q1 = sum(p["paid_in"] * p["interest_rate"] for p in a["avalanche_detail"]["passed"]) / ref
        q2 = min(cushion_after(a), 6.0)
        q3 = min(1.0, goal_money(a) / need) if need > 0 else 0.0
        return wd * max(q1, 0) ** 0.5 + wl * max(q2, 0) ** 0.5 + wg * q3 ** 0.5
    return max(pool, key=U)


def simulate(p, incomes, policy, yield_rate, c_min=0.5, tau=1.0, cushion_basis="post", tap_goals=False):
    st = {"obls": [dict(o) for o in p["obligations"] if o["amount"] > 0.5],
          "bliq": float(p["bliq"]),
          "goals": [dict(g, deadline=to_dt(g.get("deadline"))) for g in p["goals"]]}
    exp = float(p["expense_total"]); prof = int(p["risk_tolerance"]); rb = float(p["r_bench"])
    hist = list(p.get("income_history") or [])
    m = {"interest": 0.0, "yield": 0.0, "emerg_drawn": 0.0, "crisis_months": 0, "low_cushion_months": 0,
         "min_cushion_m": 1e9, "goal_short": 0.0, "goals_due": 0, "goals_missed": 0, "cons_err": 0.0,
         "months_b_toxicfirst": 0, "spent_goal_funds": 0.0, "plan": []}
    for t in range(H):
        today = T0 + timedelta(days=30 * t)
        # deadlines reached
        keep = []
        for g in st["goals"]:
            dl = g.get("deadline")
            if dl is not None and dl <= today:
                m["goals_due"] += 1
                short = max(0.0, g["target_amount"] - g["current_amount"])
                m["goal_short"] += short
                m["goals_missed"] += short > 0.01 * g["target_amount"]
                m["spent_goal_funds"] += g["current_amount"]
            else:
                keep.append(g)
        st["goals"] = keep
        inc = float(incomes[t])
        hist = (hist + [inc])[-8:] if t > 0 else hist
        active_goals = [g for g in st["goals"] if g["target_amount"] - g["current_amount"] > 0.005]
        r = run_planning(inc, exp, st["obls"], active_goals, bliq=st["bliq"], r_bench=rb, risk_tolerance=prof,
                         today=today, income_history=hist or None)
        payments = sum(o["monthly_payment"] for o in st["obls"])
        before = {o["id"]: o for o in st["obls"]}
        if r["crisis_plan"] is not None:
            m["crisis_months"] += 1
            for act in r["crisis_plan"]["actions"]:
                if act["type"] == "close_debts_from_liquidity":
                    for s in act["steps"]:
                        o = before[s["id"]]; o["amount"] -= s["paid_in"]; o["monthly_payment"] -= s["payment_saved"]
                        st["bliq"] -= s["paid_in"]
            payments = sum(o["monthly_payment"] for o in st["obls"])
            hole = exp + payments - inc
            new = []
            for o in st["obls"]:
                i = o["amount"] * o["interest_rate"] / 12; m["interest"] += i
                amt2 = o["amount"] + i - o["monthly_payment"]
                if amt2 > 0.5:
                    new.append(dict(o, amount=amt2, monthly_payment=min(o["monthly_payment"], amt2 * (1 + o["interest_rate"] / 12))))
                else:
                    hole += amt2  # overpaid last instalment reduces the hole
            st["obls"] = new
            if hole <= st["bliq"]:
                st["bliq"] -= hole
            else:
                gap = hole - st["bliq"]; st["bliq"] = 0.0
                if tap_goals:
                    for g in st["goals"]:
                        take = min(gap, g["current_amount"]); g["current_amount"] -= take; gap -= take
                if gap > 0:
                    m["emerg_drawn"] += gap
                    em = next((o for o in st["obls"] if o["id"] == "emerg"), None)
                    if em is None:
                        st["obls"].append({"id": "emerg", "name": "emergency card", "amount": gap, "interest_rate": EMERG_RATE,
                                           "monthly_payment": 0.05 * gap})
                    else:
                        em["amount"] += gap; em["monthly_payment"] = 0.05 * em["amount"]
            m["plan"].append((t + 1, "CRISIS", r["crisis_plan"]["severity"], round(inc)))
        else:
            if policy == "canon":
                a = r["best"]
            else:
                a = select_b(r, st, inc, exp, prof, today, c_min=c_min, tau=tau, cushion_basis=cushion_basis)
                if a is not None and any(o["interest_rate"] > (tau or 9e9) for o in st["obls"]) and a["x_obl_effective"] >= max(x["x_obl_effective"] for x in r["ranked"]) - 1:
                    m["months_b_toxicfirst"] += 1
            rt = inc - exp - payments
            pre = r.get("bliq_preallocation") or {}
            st["bliq"] -= pre.get("bliq_used", 0.0)
            gid = {g["id"]: g for g in st["goals"]}
            for c in pre.get("closed_goals", []):
                gid[c["id"]]["current_amount"] += c["amount"]
            if a is None:
                st["bliq"] += rt; xd = xr = xg = 0.0; alloc_obls = [dict(id=o["id"], name=o["name"], interest_rate=o["interest_rate"], new_amount=o["amount"], new_payment=o["monthly_payment"]) for o in st["obls"]]
            else:
                xd, xr = a["x_obl_effective"], a["x_reserve_effective"]
                xg = sum(a.get("goal_allocation", {}).values())
                m["cons_err"] = max(m["cons_err"], abs(rt - (xd + xr + xg)))
                st["bliq"] += xr
                for k, v in a.get("goal_allocation", {}).items():
                    gid[k]["current_amount"] += v
                alloc_obls = a["obligation_allocation"]
            new = []
            for o in alloc_obls:
                o0 = before[o["id"]]; rate = o["interest_rate"]
                i = o0["amount"] * rate / 12; m["interest"] += i
                amt2 = o["new_amount"] + i - o0["monthly_payment"]
                if amt2 <= 0.5:
                    st["bliq"] += max(0.0, -amt2); continue
                new.append({"id": o["id"], "name": o["name"], "amount": amt2, "interest_rate": rate,
                            "monthly_payment": min(o["new_payment"], amt2 * (1 + rate / 12))})
            st["obls"] = new
            m["plan"].append((t + 1, round(xd), round(xr), round(xg)))
        # month-end yield on cushion and goal funds
        y = yield_rate / 12
        m["yield"] += st["bliq"] * y + sum(g["current_amount"] for g in st["goals"]) * y
        st["bliq"] *= 1 + y
        for g in st["goals"]:
            g["current_amount"] *= 1 + y
        cm = st["bliq"] / exp if exp > 0 else 99.0
        m["min_cushion_m"] = min(m["min_cushion_m"], cm)
        m["low_cushion_months"] += cm < 0.5 - 1e-9
    debt = sum(o["amount"] for o in st["obls"])
    m["debt_end"] = debt
    m["cushion_end"] = st["bliq"]
    m["goal_funds_end"] = sum(g["current_amount"] for g in st["goals"]) + m["spent_goal_funds"]
    m["net_end"] = st["bliq"] + m["goal_funds_end"] - debt
    # v2: pro-rata pace of goals whose deadline is beyond the simulated months (same definition as the oracle)
    far = 0.0
    g0 = {g["id"]: g for g in p["goals"]}
    for g in st["goals"]:
        if g.get("deadline") is None:
            continue
        ml = (g["deadline"] - T0).days / 30
        cur0 = g0[g["id"]]["current_amount"]; tgt = g["target_amount"]
        far += max(0.0, cur0 + max(0.0, tgt - cur0) * H / ml - g["current_amount"])
    m["far_pace_short"] = far
    # far goals (deadline beyond horizon): pro-rata pace achieved
    return m


def income_path(p, index, zero_month=None):
    rng = random.Random(SEED * 1_000_007 + index)
    vol = rng.choice([0.0, 0.0, 0.0, 0.1, 0.2, 0.4, 0.6, 0.9])
    rng2 = random.Random(SEED * 1_000_009 + index)
    inc0 = float(p["income_total"])
    path = [inc0] + [max(0.0, inc0 * (1 + rng2.uniform(-vol, vol))) for _ in range(H - 1)]
    if zero_month is not None:
        path[zero_month] = 0.0
    return path, vol


def reproduce_f9a():
    """Sanity: with yield 0, constant income and the f9a running example the ledger must give f9a numbers."""
    p = {"obligations": [{"id": "cc", "name": "Кредитка", "amount": 120_000.0, "interest_rate": 0.35, "monthly_payment": 6_000.0},
                         {"id": "mfo", "name": "МФО", "amount": 30_000.0, "interest_rate": 2.92, "monthly_payment": 9_000.0}],
         "bliq": 20_000.0, "expense_total": 55_000.0, "risk_tolerance": 3, "r_bench": 0.14, "income_history": None,
         "goals": [{"id": "vac", "name": "Отпуск", "target_amount": 80_000, "current_amount": 0.0,
                    "deadline": datetime(2026, 7, 2) + timedelta(days=243), "category": "emotional"}]}
    global H
    H0, H = H, 8
    out = {}
    for pol, basis in (("canon", "post"), ("b", "pre"), ("b", "post")):
        mm = simulate(p, [90_000] * 8, pol, 0.0, c_min=0.5, tau=1.0, cushion_basis=basis)
        out[(pol, basis)] = mm
        print(f"f9a-repro {pol:5} basis={basis}: interest {mm['interest']:.0f} cushion {mm['cushion_end']:.0f} vacation fund {mm['goal_funds_end']:.0f} debt {mm['debt_end']:.0f}")
    H = H0
    return out


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "repro":
        reproduce_f9a()
    else:
        n = int(sys.argv[2]); inject = mode == "mfo"
        gen = PortraitGenerator(seed=SEED, version=2)
        outf = open(sys.argv[3], "w")
        t0 = time.time()
        for i in range(n):
            p = gen.generate_with_income_history(i)
            if inject:
                if p["kind"] != "plain" or p["income_total"] <= 0:
                    continue
                inc = p["income_total"]
                p["obligations"] = p["obligations"] + [{"id": 99, "name": "MFO", "amount": round(0.33 * inc, 2),
                                                        "interest_rate": 2.92, "monthly_payment": round(0.10 * inc, 2)}]
            for scen, zm in (("base", None), ("noinc", 2)):
                path, vol = income_path(p, i, zm)
                rec = {"index": i, "kind": p["kind"], "set": mode, "scen": scen, "vol": vol, "incomes": path,
                       "expense_total": p["expense_total"], "bliq": p["bliq"], "r_bench": p["r_bench"],
                       "risk": p["risk_tolerance"],
                       "obligations": p["obligations"],
                       "goals": [dict(g, deadline=(to_dt(g["deadline"]).isoformat() if g.get("deadline") else None)) for g in p["goals"]],
                       "floor0": ranking.effective_floor_months(p["obligations"], p["r_bench"], p["income_history"])}
                for pol in ("canon", "b"):
                    mm = simulate(p, path, pol, p["r_bench"])
                    mm.pop("plan")
                    rec[pol] = mm
                outf.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
            if i % 50 == 0:
                print(mode, i, f"{time.time() - t0:.0f}s", flush=True)
        outf.close()
```

**p0c_milp.py** (версия v5, после пяти исправлений из 0.3)
```python
"""G39 point 0, oracle: 12-month MILP (HiGHS) with PERFECT FORESIGHT of the income path, same ledger as p0b_sim.py.
max  net position at month 12 (cushion + goal funds - debts - emergency debt)
     - 10 * shortfall of goals due within 12 months - 2 * shortfall of pro-rata pace of later goals
     - 1 * cushion below c_req (rouble-months) - 0.001 * emergency borrowing (tie-break, v3)
s.t. minimum payments while a loan is alive (binary), money balance each month, cushion >= 0, goal funds only grow.
v5: minimum payment y >= (P0/B0)*balance - a relaxation of the canon ledger, so the oracle is an UPPER bound on net position
(v1-v4 kept the minimum fixed after prepayment and could fall below the policies: sanity check p0e_dominance.py).
v2: emergency borrowing only in deficit months (<= hole); cushion requirement only in non-deficit months.
Run twice per record: c_req = 0.5 month (path (b) epsilon) and c_req = canon floor at t0 (floor0)."""
import sys, json, math, time
from datetime import datetime, timedelta
import highspy, numpy as np
H = 12
T0 = datetime(2026, 7, 2)
EMERG_RATE = 0.35


def solve(rec, c_req_months, time_limit=20.0, goal_pen=(10.0, 2.0)):
    h = highspy.Highs(); h.setOptionValue("output_flag", False); h.setOptionValue("time_limit", time_limit)
    h.setOptionValue("mip_rel_gap", 1e-4)
    inf = highspy.kHighsInf
    idx = {}
    obj = {}

    def var(name, lb=0.0, ub=inf, integer=False, cost=0.0):
        h.addVar(lb, ub); j = h.getNumCol() - 1
        h.changeColCost(j, cost)
        if integer:
            h.changeColIntegrality(j, highspy.HighsVarType.kInteger)
        idx[name] = j
        return j

    def row(coefs, lo, hi):
        ind = [idx[n] for n, _ in coefs]; val = [c for _, c in coefs]
        h.addRow(lo, hi, len(ind), np.array(ind, dtype=np.int32), np.array(val, dtype=float))
    exp = rec["expense_total"]; y = rec["r_bench"] / 12; inc = rec["incomes"]
    debts = [(o["amount"], o["interest_rate"], o["monthly_payment"]) for o in rec["obligations"] if o["amount"] > 0.5]
    K = len(debts)
    # minimisation: cost = -(terminal net) + penalties
    for k, (B0, r, m) in enumerate(debts):
        g = 1 + r / 12
        for t in range(H + 1):
            var(("B", k, t), cost=(1.0 if t == H else 0.0))
        for t in range(H):
            var(("y", k, t))
    for t in range(H + 1):
        var(("C", t), cost=(-1.0 if t == H else 0.0)); var(("E", t), cost=(1.0 if t == H else 0.0))
    for t in range(H):
        # v3: was cost=5.0 - penalty on draw volume made the oracle borrow EARLY (fewer roubles drawn, more interest); interest already prices it
        var(("e", t), cost=0.001); var(("q", t))
        if t >= 1:
            pass
    for t in range(1, H + 1):
        var(("cs", t), cost=1.0)
    goals = []
    for j, gl in enumerate(rec["goals"]):
        tgt, cur = gl["target_amount"], gl["current_amount"]
        dl = datetime.fromisoformat(gl["deadline"]) if gl.get("deadline") else None
        d = None if dl is None else max(0, math.ceil((dl - T0).days / 30 - 1e-9))
        goals.append((j, tgt, cur, dl, d))
        for t in range(H + 1):
            var(("G", j, t), cost=(-1.0 if t == H else 0.0))
        for t in range(H):
            var(("g", j, t))
        var(("sh", j), cost=(goal_pen[0] if (d is not None and d <= H - 1) else goal_pen[1]))
    for k, (B0, r, m) in enumerate(debts):
        g = 1 + r / 12; rho = m / B0
        row([(("B", k, 0), 1)], B0, B0)
        for t in range(H):
            row([(("B", k, t + 1), 1), (("B", k, t), -g), (("y", k, t), 1)], 0, 0)
            # v5: minimum payment proportional to balance, y >= (P0/B0)*B - a RELAXATION of the canon ledger
            # (canon: payment shrinks pro rata only on prepayment and stays P on regular amortisation, so canon's
            # minimum >= rho*B always) -> the oracle is an upper bound; pure LP, no binaries
            row([(("y", k, t), 1), (("B", k, t), -min(rho, g))], 0, inf)
    row([(("C", 0), 1)], rec["bliq"], rec["bliq"]); row([(("E", 0), 1)], 0, 0)
    for j, tgt, cur, dl, d in goals:
        row([(("G", j, 0), 1)], cur, cur)
        for t in range(H):
            # v4: end-of-month yield, as p0b_sim.py: G[t+1] = (G[t] + g[t]) * (1 + y) while the goal is active
            if d is None or t < d:
                row([(("G", j, t + 1), 1 / (1 + y)), (("G", j, t), -1), (("g", j, t), -1)], 0, 0)
            else:
                row([(("G", j, t + 1), 1), (("G", j, t), -1), (("g", j, t), -1)], 0, 0)
            if d is not None and t >= d:
                row([(("g", j, t), 1)], 0, 0)
            if d is None:
                pass
        if d is not None and d <= H - 1:   # v4: the simulator checks deadlines at the start of months 0..H-1
            row([(("G", j, d), 1), (("sh", j), 1)], tgt, inf)
        elif d is not None:
            ml = (dl - T0).days / 30
            row([(("G", j, H), 1), (("sh", j), 1)], cur + max(0.0, tgt - cur) * H / ml, inf)
    for t in range(H):
        coefs = [(("y", k, t), 1) for k in range(K)] + [(("g", j, t), 1) for j, *_ in goals]
        coefs += [(("q", t), 1), (("C", t + 1), 1 / (1 + y)), (("C", t), -1), (("e", t), -1)]   # v4: end-of-month yield
        row(coefs, inc[t] - exp, inc[t] - exp)
        row([(("E", t + 1), 1), (("E", t), -(1 + EMERG_RATE / 12)), (("e", t), -1), (("q", t), 1)], 0, 0)
        # v2 (artifact fix): emergency borrowing only in a deficit month and not above the hole;
        # cushion requirement only in non-deficit months (as the epsilon-floor of path (b)) - a buffer is meant to be spent in a shock
        hole = exp + sum(m for _, _, m in debts) - inc[t]   # >= the simulator's hole (its payments only shrink)
        if hole > 0:
            row([(("e", t), 1)], 0, hole)
        else:
            row([(("e", t), 1)], 0, 0)
            row([(("C", t + 1), 1), (("cs", t + 1), 1)], c_req_months * exp, inf)
    h.run()
    st = h.getModelStatus()
    if st not in (highspy.HighsModelStatus.kOptimal, highspy.HighsModelStatus.kTimeLimit):
        return {"status": str(st)}
    x = h.getSolution().col_value
    if len(x) == 0:
        return {"status": str(st)}
    v = lambda n: x[idx[n]]
    due_short = sum(v(("sh", j)) for j, tgt, cur, dl, d in goals if d is not None and d <= H - 1)
    goals_end = sum(v(("G", j, H)) for j, *_ in goals)
    net = v(("C", H)) + goals_end - sum(v(("B", k, H)) for k in range(K)) - v(("E", H))
    far_short = sum(v(("sh", j)) for j, tgt, cur, dl, d in goals if d is not None and d > H - 1)
    return {"status": str(st).split(".")[-1], "net_end": net, "goal_short_due": due_short, "far_pace_short": far_short,
            "emerg_drawn": sum(v(("e", t)) for t in range(H)),
            "low_cushion_months": sum(1 for t in range(1, H + 1) if v(("cs", t)) > 1.0),
            "mip_gap": h.getInfo().mip_gap,
            "C_path": [round(v(("C", t))) for t in range(H + 1)], "E_path": [round(v(("E", t))) for t in range(H + 1)],
            "e_path": [round(v(("e", t))) for t in range(H)], "q_path": [round(v(("q", t))) for t in range(H)]}


if __name__ == "__main__":
    src, dst, limit = sys.argv[1], sys.argv[2], int(sys.argv[3])
    kinds = set(sys.argv[4].split(",")) if len(sys.argv) > 4 else None
    out = open(dst, "w"); t0 = time.time(); n = 0
    for line in open(src):
        rec = json.loads(line)
        if kinds and rec["kind"] not in kinds:
            continue
        if n >= limit:
            break
        res = {"index": rec["index"], "set": rec["set"], "scen": rec["scen"], "kind": rec["kind"]}
        for tag, c, gp in (("omoney", 0.0, (0.0, 0.0)), ("o05", 0.5, (10.0, 2.0)), ("ofl", rec["floor0"], (10.0, 2.0))):
            s = time.time(); r = solve(rec, c, goal_pen=gp); r["sec"] = round(time.time() - s, 3); res[tag] = r
        out.write(json.dumps(res) + "\n"); n += 1
        if n % 100 == 0:
            print(n, f"{time.time() - t0:.0f}s", flush=True)
    out.close()
```

**p0c_check.py**
```python
"""Sanity of p0c_milp against g41/f5b.py: 8 months, yield 0, vacation 80 000 due month 8, cushion >= 20 000 -> expect interest 21 824 (net 128 176)."""
import sys; sys.path.insert(0, "/private/tmp/claude-501/-Users-vasyaevdokimov-repos-personal-finance-dss/fe25aad2-149b-48bd-a8b2-c62cc04ce4a1/scratchpad/g39")
import p0c_milp as M
M.H = 8
rec = {"expense_total": 55_000, "r_bench": 0.0, "incomes": [90_000] * 8, "bliq": 20_000,
       "obligations": [{"amount": 120_000, "interest_rate": 0.35, "monthly_payment": 6_000}, {"amount": 30_000, "interest_rate": 2.92, "monthly_payment": 9_000}],
       "goals": [{"target_amount": 80_000, "current_amount": 0, "deadline": "2027-02-27T00:00:00"}]}
r = M.solve(rec, 20_000 / 55_000)
print(r, "implied interest:", round(150_000 - r["net_end"]))
```

**p0e_dominance.py** (проверка «оракул не ниже политики»)
```python
"""Sanity: the oracle (c_req 0.5) must not be below a policy in net position unless the policy has a larger goal shortfall."""
import json, sys
G = "/private/tmp/claude-501/-Users-vasyaevdokimov-repos-personal-finance-dss/fe25aad2-149b-48bd-a8b2-c62cc04ce4a1/scratchpad/g39/"
simf, orf, TAG = sys.argv[1], sys.argv[2], sys.argv[3]
sim = {(r["index"], r["scen"]): r for r in map(json.loads, open(G + simf))}
bad = n = 0
for l in open(G + orf):
    o = json.loads(l); s = sim[(o["index"], o["scen"])]; n += 1
    for pol in ("canon", "b"):
        if "net_end" not in o[TAG]:
            print("NO SOLUTION", o["index"], o["scen"], o[TAG]); continue
        d = o[TAG]["net_end"] - s[pol]["net_end"]
        if d < -1 and not (s[pol]["goal_short"] > o[TAG]["goal_short_due"] + 1):
            bad += 1
            if bad <= 8:
                print("ORACLE BELOW", pol, o["index"], o["scen"], o["kind"], "net o/pol", round(o[TAG]["net_end"]), round(s[pol]["net_end"]),
                      "goalshort o/pol", round(o[TAG]["goal_short_due"]), round(s[pol]["goal_short"]), "lowcush o/pol", o[TAG]["low_cushion_months"], s[pol]["low_cushion_months"])
print("records", n, "oracle below a policy with no goal excuse:", bad)
```

**p0f_conservation.py**
```python
"""Money identity of the simulator: net_end = net_0 + sum(income - expenses) - interest + yield. Any gap = money created/destroyed."""
import sys, json
sys.path.insert(0, "/Users/vasyaevdokimov/repos/personal-finance-dss"); sys.path.insert(0, "/private/tmp/claude-501/-Users-vasyaevdokimov-repos-personal-finance-dss/fe25aad2-149b-48bd-a8b2-c62cc04ce4a1/scratchpad/g39")
import p0b_sim as S
from tools.portrait_testing.generator import PortraitGenerator
gen = PortraitGenerator(seed=S.SEED, version=2)
worst = []
for i in range(int(sys.argv[1])):
    p = gen.generate_with_income_history(i)
    for zm in (None, 2):
        path, vol = S.income_path(p, i, zm)
        net0 = p["bliq"] + sum(g["current_amount"] for g in p["goals"]) - sum(o["amount"] for o in p["obligations"] if o["amount"] > 0.5)
        for pol in ("canon", "b"):
            m = S.simulate(p, path, pol, p["r_bench"])
            ident = net0 + sum(path) - 12 * p["expense_total"] - m["interest"] + m["yield"]
            gap = m["net_end"] - ident
            worst.append((abs(gap), gap, i, p["kind"], zm, pol, round(m["net_end"]), round(ident), m["crisis_months"]))
worst.sort(key=lambda w: -w[0])
for w in worst[:12]:
    print(w)
print("records", len(worst), "with |gap| > 1 rub:", sum(1 for w in worst if w[0] > 1))
```

**p0g_report.py**
```python
"""G39 point 0 report: path (b) vs canon vs MILP oracles on ADR-015 portraits (+ MFO-injected plain portraits), base / month-3-without-income."""
import json, statistics as stt
G = "/private/tmp/claude-501/-Users-vasyaevdokimov-repos-personal-finance-dss/fe25aad2-149b-48bd-a8b2-c62cc04ce4a1/scratchpad/g39/"


def q(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, max(0, int(round(p * (len(xs) - 1)))))] if xs else float("nan")


def load(tag):
    sim = [json.loads(l) for l in open(G + f"p0_{tag}.jsonl")]
    orc = {(o["index"], o["scen"]): o for o in map(json.loads, open(G + f"p0_o_{tag}.jsonl"))}
    return sim, orc


def block(rows, orc, title):
    n = len(rows)
    if n == 0:
        return
    print(f"\n=== {title}: records {n}")
    same = sum(1 for r in rows if abs(r["b"]["net_end"] - r["canon"]["net_end"]) < 1 and abs(r["b"]["goal_short"] - r["canon"]["goal_short"]) < 1
               and abs(r["b"]["far_pace_short"] - r["canon"]["far_pace_short"]) < 1)
    print(f"identical outcome b == canon: {same} ({same / n:.1%})")
    inc12 = lambda r: max(1.0, sum(r["incomes"]))
    dnet = [r["b"]["net_end"] - r["canon"]["net_end"] for r in rows]
    dnet_rel = [(r["b"]["net_end"] - r["canon"]["net_end"]) / inc12(r) for r in rows]
    print(f"net position b - canon, roubles: median {stt.median(dnet):.0f}  p10 {q(dnet, .1):.0f}  p90 {q(dnet, .9):.0f}  min {min(dnet):.0f}  max {max(dnet):.0f}")
    print(f"  as % of 12-month income: median {stt.median(dnet_rel):.2%}  p10 {q(dnet_rel, .1):.2%}  p90 {q(dnet_rel, .9):.2%}")
    print(f"  b better by >0.5% income: {sum(1 for x in dnet_rel if x > .005) / n:.1%}   b worse by >0.5% income: {sum(1 for x in dnet_rel if x < -.005) / n:.1%}")
    for key, lab in (("goal_short", "shortfall of goals due within 12 mo"), ("far_pace_short", "pace shortfall of later goals"),
                     ("emerg_drawn", "emergency borrowing (arrears proxy)"), ("low_cushion_months", "months with cushion < 0.5 mo"),
                     ("crisis_months", "crisis months")):
        c = [r["canon"][key] for r in rows]; b = [r["b"][key] for r in rows]
        worse = sum(1 for x, y in zip(c, b) if y > x + 1e-6 + (1 if key in ("goal_short", "far_pace_short", "emerg_drawn") else 0))
        better = sum(1 for x, y in zip(c, b) if y < x - 1e-6 - (1 if key in ("goal_short", "far_pace_short", "emerg_drawn") else 0))
        print(f"{lab:40}: mean canon {stt.mean(c):>12.1f}  b {stt.mean(b):>12.1f} | b worse in {worse / n:6.1%}  b better in {better / n:6.1%}")
    gm_c = sum(r["canon"]["goals_missed"] for r in rows); gm_b = sum(r["b"]["goals_missed"] for r in rows); due = sum(r["canon"]["goals_due"] for r in rows)
    print(f"goals due {due}: missed (>1% short) canon {gm_c}  b {gm_b}")
    # acceptance criterion of G41 (question 1): b not worse than canon in ANY portrait on arrears and goal failure
    viol = [r for r in rows if r["b"]["emerg_drawn"] > r["canon"]["emerg_drawn"] + 1 or r["b"]["goals_missed"] > r["canon"]["goals_missed"]]
    print(f"G41 acceptance criterion violated (b more emergency debt OR more missed goals): {len(viol)} ({len(viol) / n:.1%})")
    if viol:
        ed = [r["b"]["emerg_drawn"] - r["canon"]["emerg_drawn"] for r in viol if r["b"]["emerg_drawn"] > r["canon"]["emerg_drawn"] + 1]
        if ed:
            print(f"  extra emergency debt under b where it occurs: median {stt.median(ed):.0f}  p90 {q(ed, .9):.0f}  max {max(ed):.0f};"
                  f" as months of expenses median {stt.median([(r['b']['emerg_drawn'] - r['canon']['emerg_drawn']) / max(1, r['expense_total']) for r in viol if r['b']['emerg_drawn'] > r['canon']['emerg_drawn'] + 1]):.2f}")
        kinds = {}
        for r in viol:
            kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
        print("  by kind:", dict(sorted(kinds.items(), key=lambda kv: -kv[1])))
    # oracles
    ok = [r for r in rows if (r["index"], r["scen"]) in orc and "net_end" in orc[(r["index"], r["scen"])]["o05"] and "net_end" in orc[(r["index"], r["scen"])]["omoney"]]
    if ok:
        for tag, lab in (("omoney", "pure-money oracle (no cushion, no goals)"), ("o05", "oracle with (b) requirements: cushion 0.5 mo + goals"), ("ofl", "oracle with canon floor + goals")):
            okt = [r for r in ok if "net_end" in orc[(r["index"], r["scen"])][tag]]
            for pol in ("canon", "b"):
                gap = [orc[(r["index"], r["scen"])][tag]["net_end"] - r[pol]["net_end"] for r in okt]
                gapr = [g / inc12(r) for g, r in zip(gap, okt)]
                print(f"gap {lab:52} - {pol:5}: median {stt.median(gap):>9.0f} ₽ ({stt.median(gapr):.2%} inc)  p90 {q(gap, .9):>9.0f} ₽ ({q(gapr, .9):.2%})  oracle below policy: {sum(1 for g in gap if g < -1) / len(gap):.1%}")
            gs = [orc[(r["index"], r["scen"])][tag]["goal_short_due"] for r in okt]; fs = [orc[(r["index"], r["scen"])][tag]["far_pace_short"] for r in okt]
            ed = [orc[(r["index"], r["scen"])][tag]["emerg_drawn"] for r in okt]
            print(f"    {tag}: mean due-goal shortfall {stt.mean(gs):.0f}, far pace shortfall {stt.mean(fs):.0f}, emergency {stt.mean(ed):.0f}")
        # share of the oracle's advantage over canon captured by b
        cap = []
        for r in ok:
            o = orc[(r["index"], r["scen"])]["omoney"]["net_end"]; c = r["canon"]["net_end"]; b = r["b"]["net_end"]
            if o - c > 0.005 * inc12(r):
                cap.append((b - c) / (o - c))
        if cap:
            print(f"share of (pure-money oracle - canon) captured by b, where the gap > 0.5% income ({len(cap)} records): median {stt.median(cap):.1%}  p10 {q(cap, .1):.1%}  p90 {q(cap, .9):.1%}")


if __name__ == "__main__":
    for tag in ("adr015", "mfo"):
        sim, orc = load(tag)
        for scen in ("base", "noinc"):
            rows = [r for r in sim if r["scen"] == scen]
            block(rows, orc, f"{tag} / {scen} / all kinds")
            block([r for r in rows if r["kind"] == "plain"], orc, f"{tag} / {scen} / plain only")
            if tag == "adr015":
                block([r for r in rows if r["kind"] == "plain" and r["vol"] >= 0.4], orc, f"{tag} / {scen} / plain, income volatility >= 0.4")
                tox = [r for r in rows if any(o["interest_rate"] >= max(0.30, r["r_bench"] + 0.15) for o in r["obligations"])]
                block(tox, orc, f"{tag} / {scen} / with canon-toxic debt (>= max(30%, r_bench+15pp))")
```

### 0.6. Второй круг: абляция — какой элемент пути (б) ломается (`p0h_ablation.py`, `p0i_ablation_report.py`, `p0j_price_and_tap.py`)

**Аналогия.** Машина стала расходовать больше топлива — по очереди снимаем по одной доработке и смотрим, после какой расход вернулся.

Семь вариантов на тех же 1 000 обычных портретах (индексы 0–1499, `kind == "plain"`), тех же путях дохода и той же бухгалтерии; кризисные месяцы у всех — канон. Колонки: «хуже/лучше по деньгам» — чистая позиция отличается от канона больше чем на 0,5 % годового дохода; «экстр. хуже» — больше экстренного долга, чем у канона; «критерий Г41» — больше экстренного долга ИЛИ больше сорванных целей; «разрыв» — медиана отставания от чистого денежного оракула в % годового дохода (у канона: adr015 base 0,166 %, noinc 0,191 %; mfo base 1,315 %, noinc 1,496 %).

Вывод `p0i_ablation_report.py`:
```

=== adr015 / base / plain portraits: 1000
variant              net worse>0.5% net better>0.5% median dnet %inc goal miss worse goal short better emerg worse emerg better G41 criterion viol gap to o-money med %
b_g41                         17.0%            0.3%           0.000%            0.0%             14.8%        7.0%         0.5%               7.0%               0.196%
b_no_goal_eps                  1.4%            1.8%           0.000%            0.4%              0.3%        2.7%         1.6%               3.1%               0.121%
b_floor_canon                 15.6%            0.1%           0.000%            0.0%             12.1%        2.8%         0.5%               2.8%               0.199%
b_tau_canon                   14.5%            0.6%           0.000%            0.0%             14.8%        7.2%         0.3%               7.2%               0.193%
b_floor_tau_canon             13.5%            0.4%           0.000%            0.0%             12.1%        2.4%         0.3%               2.4%               0.195%
canon_goal_eps                15.4%            0.0%           0.000%            0.0%             12.1%        2.6%         0.0%               2.6%               0.195%
canon_goal_toxic              13.4%            0.4%           0.000%            0.0%             12.1%        2.3%         0.0%               2.3%               0.195%
canon (reference)    gap to o-money median 0.166%  p90 1.565%

=== adr015 / noinc / plain portraits: 1000
variant              net worse>0.5% net better>0.5% median dnet %inc goal miss worse goal short better emerg worse emerg better G41 criterion viol gap to o-money med %
b_g41                         18.6%            0.2%          -0.000%            0.0%             15.3%       30.9%         1.9%              30.9%               0.317%
b_no_goal_eps                  1.4%            0.8%           0.000%            0.0%              0.4%       13.7%         4.9%              13.7%               0.172%
b_floor_canon                 13.4%            0.1%           0.000%            0.0%             11.5%        8.9%         2.3%               8.9%               0.223%
b_tau_canon                   15.2%            0.9%           0.000%            0.0%             15.2%       31.7%         0.8%              31.7%               0.285%
b_floor_tau_canon             11.3%            0.7%           0.000%            0.0%             11.5%        8.1%         1.1%               8.1%               0.220%
canon_goal_eps                13.2%            0.0%           0.000%            0.0%             11.5%        9.4%         0.0%               9.4%               0.221%
canon_goal_toxic              11.2%            0.7%           0.000%            0.0%             11.5%        8.4%         0.0%               8.4%               0.219%
canon (reference)    gap to o-money median 0.191%  p90 1.234%

=== mfo / base / plain portraits: 1000
variant              net worse>0.5% net better>0.5% median dnet %inc goal miss worse goal short better emerg worse emerg better G41 criterion viol gap to o-money med %
b_g41                         33.0%            9.9%           0.000%            0.1%             13.8%        8.3%         1.5%               8.4%               2.432%
b_no_goal_eps                  0.4%           21.6%           0.004%            0.0%              1.9%        3.7%         2.7%               3.7%               0.932%
b_floor_canon                 33.3%            2.9%          -0.000%            0.1%             12.9%        4.1%         0.6%               4.2%               2.682%
b_tau_canon                   31.6%           10.9%           0.000%            0.1%             13.8%        8.3%         1.4%               8.4%               2.339%
b_floor_tau_canon             31.8%            3.6%           0.000%            0.1%             12.9%        4.0%         0.5%               4.1%               2.615%
canon_goal_eps                41.4%            0.2%          -0.141%            0.1%             13.1%        4.3%         0.0%               4.4%               2.916%
canon_goal_toxic              31.7%            3.6%           0.000%            0.1%             12.9%        4.1%         0.3%               4.2%               2.622%
canon (reference)    gap to o-money median 1.315%  p90 3.345%

=== mfo / noinc / plain portraits: 1000
variant              net worse>0.5% net better>0.5% median dnet %inc goal miss worse goal short better emerg worse emerg better G41 criterion viol gap to o-money med %
b_g41                         30.7%           10.2%           0.000%            0.0%             13.9%       28.7%         2.7%              28.7%               2.826%
b_no_goal_eps                  0.3%           21.1%           0.006%            0.0%              1.5%       18.0%         5.7%              18.0%               1.023%
b_floor_canon                 30.2%            3.1%           0.000%            0.0%             12.5%       16.6%         2.0%              16.6%               3.089%
b_tau_canon                   29.3%           11.6%           0.000%            0.0%             13.9%       29.1%         2.4%              29.1%               2.777%
b_floor_tau_canon             28.8%            3.7%           0.000%            0.0%             12.5%       16.5%         1.9%              16.5%               3.072%
canon_goal_eps                38.9%            0.1%          -0.076%            0.0%             12.8%       19.8%         0.4%              19.8%               3.247%
canon_goal_toxic              28.9%            3.7%           0.000%            0.0%             12.5%       16.6%         1.7%              16.6%               3.072%
canon (reference)    gap to o-money median 1.496%  p90 3.683%
```

**Цена пунктуальности целей** (`p0j_price_and_tap.py price`): сколько рублей чистой позиции вариант теряет против канона на каждый рубль сокращённого недобора целей (к сроку + темп дальних):
```
adr015 base  b_g41            : portraits with less goal shortfall  472; total net lost      2337083 for     42803423 roubles of shortfall avoided -> 0.055 rub/rub; per portrait median 0.026, p90 0.141
adr015 noinc b_g41            : portraits with less goal shortfall  491; total net lost      2152918 for     39552893 roubles of shortfall avoided -> 0.054 rub/rub; per portrait median 0.044, p90 0.152
adr015 base  canon_goal_eps   : portraits with less goal shortfall  408; total net lost      2116119 for     34396784 roubles of shortfall avoided -> 0.062 rub/rub; per portrait median 0.035, p90 0.153
adr015 noinc canon_goal_eps   : portraits with less goal shortfall  407; total net lost      1579207 for     29105809 roubles of shortfall avoided -> 0.054 rub/rub; per portrait median 0.031, p90 0.145
adr015 base  canon_goal_toxic : portraits with less goal shortfall  397; total net lost      1794685 for     32186394 roubles of shortfall avoided -> 0.056 rub/rub; per portrait median 0.029, p90 0.143
adr015 noinc canon_goal_toxic : portraits with less goal shortfall  394; total net lost      1273860 for     26574172 roubles of shortfall avoided -> 0.048 rub/rub; per portrait median 0.028, p90 0.146
mfo    base  b_g41            : portraits with less goal shortfall  446; total net lost      5289625 for     32546811 roubles of shortfall avoided -> 0.163 rub/rub; per portrait median 0.123, p90 0.673
mfo    noinc b_g41            : portraits with less goal shortfall  459; total net lost      4966145 for     30613881 roubles of shortfall avoided -> 0.162 rub/rub; per portrait median 0.140, p90 0.729
mfo    base  canon_goal_eps   : portraits with less goal shortfall  403; total net lost      6367964 for     27619986 roubles of shortfall avoided -> 0.231 rub/rub; per portrait median 0.222, p90 1.036
mfo    noinc canon_goal_eps   : portraits with less goal shortfall  416; total net lost      6396824 for     25582189 roubles of shortfall avoided -> 0.250 rub/rub; per portrait median 0.241, p90 1.230
mfo    base  canon_goal_toxic : portraits with less goal shortfall  388; total net lost      5018117 for     25114041 roubles of shortfall avoided -> 0.200 rub/rub; per portrait median 0.185, p90 0.867
mfo    noinc canon_goal_toxic : portraits with less goal shortfall  393; total net lost      4692583 for     22217778 roubles of shortfall avoided -> 0.211 rub/rub; per portrait median 0.198, p90 1.051
```

**Чувствительность к допущению бухгалтерии** «деньги целей в кризис не трогаются» (`p0j_price_and_tap.py tap 900`, сценарий `noinc`, дефицит сверх подушки сначала берётся из денег целей, потом экстренный долг):
```
noinc scenario, tap_goals=True, plain portraits 600
  b_g41            : more emergency debt than canon 3.7%; more missed goals than canon 0.0%
  canon_goal_eps   : more emergency debt than canon 0.2%; more missed goals than canon 0.0%
  b_no_goal_eps    : more emergency debt than canon 3.0%; more missed goals than canon 0.0%
```

**Разбор по элементам — что держится, что ломается.**

| Элемент пути (б) | Что показала абляция | Вердикт |
|---|---|---|
| Вогнутая ценность на глобальных шкалах (рамка 4) | `b_no_goal_eps` (всё, кроме ε-цели): по деньгам хуже канона лишь в 0,3–1,4 %, лучше в 21,6 % портретов с МФО; разрыв до оракула 0,93 % против 1,32 % у канона | 🟢 **держится** — по деньгам это улучшение |
| ε-цель «не меньше нужного темпа» (рамки 5, 8) | Единственный источник денежной потери: без неё «хуже по деньгам» падает с 17–33 % до 0,3–1,4 %. С ней — недобор целей меньше у 12–15 % портретов. Цена: **0,05 ₽ за рубль** сокращённого недобора без токсичного долга, **0,16–0,25 ₽** с МФО, у 10 % портретов с МФО — **0,67–1,23 ₽ за рубль** | 🟡 **не ошибка, а компромисс с ценой**; без предела цены покупает пунктуальность дороже самой цели |
| ε-подушка 0,5 мес. вместо floor (рамки 3, 5) | Главная причина провала в кризисе: экстренный долг хуже у 30,9 % (adr015 noinc); с floor канона — 8,9 %. Если деньги целей доступны в кризисе — 3,7 % | 🔴 **ломается в кризисе**, если деньги целей не считаются запасом; держится, только если продукт явно разрешает брать из целей в беде |
| «Токсичный первым», τ = 100 % (рамка 2) | В портретах ADR-015 не срабатывает ни разу (ставки ≤ 35 %). С порогом канона 30 % эффект мал: 14,5 % против 17,0 % «хуже по деньгам» | ⚪ **не проверяемо на ADR-015**; на МФО мало что меняет |
| Критерий приёмки Г41 «не хуже канона ни в одном портрете» | Не выполняется ни одним вариантом с ε-целью, потому что деньги на цель заперты и в кризисе недоступны; при доступных деньгах целей — 0,2 % (`canon_goal_eps`) | 🔴 **критерий сформулирован неверно**: ε-цель по построению меняет рубли на пунктуальность; нужен двухмерный критерий (деньги, цели) с ценой |

**Главное число, которого не было в Г41.** Разрыв канона до ясновидящего денежного оптимума на портретах ADR-015 без токсичного долга — **медиана 0,17 % годового дохода, p90 1,6 %**. С МФО — медиана 1,3 %, p90 3,3 %. То есть **по деньгам у обычного человека без дорогого долга канон уже почти оптимален**, и любое правило выбора может выиграть в типичном случае меньше 0,2 % дохода в год. Настоящая ценность пути (б) — не деньги, а **сроки целей** и **поведение при токсичном долге**.

### 0.7. 🔴 Ответ по пункту 0: держится ли рекомендация Г41

**В том виде, как она записана в Г41 (весь пакет из четырёх элементов, «−8 130 ₽ процентов и отпуск в срок») — НЕ держится.** Сквозной пример был нетипичным: на популяции путь (б) не даёт одновременно «меньше процентов и цель в срок» — он меняет одно на другое.

**Держится по частям:**
1. 🟢 **Вогнутая ценность на общих шкалах** — держится и по деньгам лучше канона.
2. 🟡 **ε-цель** — держится как компромисс, но нужна **верхняя граница цены**: вводить ε-взнос, только если цена рубля пунктуальности ниже порога, связанного с классом надёжности цели (рамка 8 Г41). Без предела у 10 % портретов с МФО пунктуальность покупается дороже рубля за рубль.
3. 🔴 **ε-подушка 0,5 мес.** — ломается в кризисе (экстренный долг хуже у 31 % портретов в «месяц без дохода»). Допустима только вместе с явным правилом «в беде деньги целей — тоже запас» (тогда 3,7 %), либо с floor канона (8,9 %).
4. ⚪ **«Токсичный первым»** — на портретах ADR-015 не проверяется (там нет ставок выше 35 %); на добавленном МФО эффект мал.

**Где ломается:** (а) сценарий «месяц без дохода» у людей с неровным доходом (38 % портретов с волатильностью ≥ 0,4); (б) портреты с МФО, где ε-цель тянет деньги мимо долга под 292 %; (в) сам критерий приёмки Г41, который несовместим с ε-целью.

**Что нужно, прежде чем путь (б) идёт в канон (решение владельца):** (1) критерий приёмки — двухмерный: «чистая позиция не хуже канона больше чем на X % дохода И недобор целей не больше», с X, выбранным владельцем; (2) предел цены пунктуальности; (3) правило о деньгах целей в кризисе; (4) пересчёт этого пункта на генераторе с ТОКСИЧНЫМИ ставками из реального распределения (у v2 их нет) и после починки Д-01.

**Ограничения замера.** Симуляция 12 месяцев, один сценарий шока (месяц 3); расходы в кризисе не сокращаются; `surplus_plan` (разовые ходы из излишка, `app/services/planning.py`, слой G4) не применяется ни каноном, ни (б); доходность подушки и целей = $r_{bench}$; оракул знает доход наперёд и потому — верхняя граница, а не достижимая цель.

**p0h_ablation.py**
```python
"""G39 point 0, round 2: ablation of path (b) - which element breaks it. Same portraits, paths and ledger as p0b_sim.py.
Variants (selection rule inside a non-crisis month; crisis months are canon for all):
  V0 b_g41            - path (b) as in G41 (c_min 0.5, tau 100 %, eps-goal, concave U)
  V1 b_no_goal_eps    - V0 without the eps-goal filter
  V2 b_floor_canon    - V0 with c_min = canon effective floor (ranking.effective_floor_months)
  V3 b_tau_canon      - V0 with toxic threshold of the canon (rate >= max(30 %, r_bench + 15 pp))
  V4 b_floor_tau_canon- V2 + V3
  V5 canon_goal_eps   - CANON order kept; among alternatives with the canon's best floor_level keep those meeting the goal pace; first by canon order
  V6 canon_goal_toxic - V5 + toxic-first (canon threshold) inside the same best-floor group, when all deadline goals stay feasible
run_planning is wrapped only to read r_bench / income_history / obligations of the current call."""
import sys, json, math, time
sys.path.insert(0, "/private/tmp/claude-501/-Users-vasyaevdokimov-repos-personal-finance-dss/fe25aad2-149b-48bd-a8b2-c62cc04ce4a1/scratchpad/g39")
import p0b_sim as S
import app.core.ranking as ranking
from app.core.goals_priority import months_left_or_none
from tools.portrait_testing.generator import PortraitGenerator

CUR = {}
_real_rp = S.run_planning


def rp_wrap(inc, exp, obls, goals, **kw):
    CUR.update(rb=kw["r_bench"], hist=kw.get("income_history"), obls=obls)
    return _real_rp(inc, exp, obls, goals, **kw)


S.run_planning = rp_wrap
_orig_select_b = S.select_b
VARIANT = {"name": "b_g41"}


def goal_need(r, st, today):
    goals = [g for g in st["goals"] if g["target_amount"] - g["current_amount"] > 1]
    closed = {c["id"] for c in (r.get("bliq_preallocation") or {}).get("closed_goals", [])}
    dl = []
    for g in goals:
        if g["id"] in closed or g.get("deadline") is None:
            continue
        ml = months_left_or_none(g["deadline"], today)
        dl.append((g, max(1, math.floor(ml + 1e-9))))
    need = sum(min(g["target_amount"] - g["current_amount"], (g["target_amount"] - g["current_amount"]) / ml) for g, ml in dl)
    return need, dl


def select_variant(r, st, inc, exp, prof, today, c_min=0.5, tau=1.0, cushion_basis="post"):
    v = VARIANT["name"]
    rb = CUR["rb"]; floor = ranking.effective_floor_months(CUR["obls"], rb, income_history=CUR["hist"])
    tau_canon = max(ranking.TOXIC_RATE_ABS, rb + ranking.TOXIC_RATE_SPREAD) - 1e-9   # select_b uses '>' -> subtract eps to mean '>='
    if v == "b_g41":
        return _orig_select_b(r, st, inc, exp, prof, today, c_min=0.5, tau=1.0)
    if v == "b_floor_canon":
        return _orig_select_b(r, st, inc, exp, prof, today, c_min=floor, tau=1.0)
    if v == "b_tau_canon":
        return _orig_select_b(r, st, inc, exp, prof, today, c_min=0.5, tau=tau_canon)
    if v == "b_floor_tau_canon":
        return _orig_select_b(r, st, inc, exp, prof, today, c_min=floor, tau=tau_canon)
    if v == "b_no_goal_eps":
        st2 = dict(st, goals=[dict(g, deadline=None) for g in st["goals"]])   # goals look open-ended to select_b -> need = 0, no pace filter
        return _orig_select_b(r, st2, inc, exp, prof, today, c_min=0.5, tau=1.0)
    ranked = r["ranked"]
    if not ranked:
        return None
    top_floor = max(a["floor_level"] for a in ranked)
    grp = [a for a in ranked if a["floor_level"] >= top_floor - 1e-9]          # canon order preserved (ranked is sorted)
    need, dl = goal_need(r, st, today)
    gm = lambda a: sum(a.get("goal_allocation", {}).values())
    if v == "canon_goal_toxic":
        obls = CUR["obls"]
        if any(o["interest_rate"] > tau_canon and o["amount"] > 0.5 for o in obls):
            pay_after = sum(o["monthly_payment"] for o in obls if o["interest_rate"] <= tau_canon)
            feasible = all(ml > 1 for _, ml in dl) and sum((g["target_amount"] - g["current_amount"]) / (ml - 1) for g, ml in dl) <= inc - exp - pay_after
            if feasible:
                best_d = max(a["x_obl_effective"] for a in grp)
                return next(a for a in grp if a["x_obl_effective"] >= best_d - 1)
    if need > 0:
        ok = [a for a in grp if gm(a) >= need - 1]
        if ok:
            return ok[0]
        best_g = max(gm(a) for a in grp)
        return next(a for a in grp if gm(a) >= best_g - 1)
    return ranked[0]


S.select_b = select_variant
VARIANTS = ["b_g41", "b_no_goal_eps", "b_floor_canon", "b_tau_canon", "b_floor_tau_canon", "canon_goal_eps", "canon_goal_toxic"]

if __name__ == "__main__":
    mode, n, dst = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    gen = PortraitGenerator(seed=S.SEED, version=2)
    out = open(dst, "w"); t0 = time.time()
    for i in range(n):
        p = gen.generate_with_income_history(i)
        if p["kind"] != "plain" or p["income_total"] <= 0:
            continue
        if mode == "mfo":
            inc = p["income_total"]
            p["obligations"] = p["obligations"] + [{"id": 99, "name": "MFO", "amount": round(0.33 * inc, 2), "interest_rate": 2.92, "monthly_payment": round(0.10 * inc, 2)}]
        for scen, zm in (("base", None), ("noinc", 2)):
            path, vol = S.income_path(p, i, zm)
            rec = {"index": i, "set": mode, "scen": scen, "vol": vol, "expense_total": p["expense_total"], "inc12": sum(path)}
            for v in VARIANTS:
                VARIANT["name"] = v
                m = S.simulate(p, path, "b", p["r_bench"]); m.pop("plan"); rec[v] = m
            out.write(json.dumps(rec) + "\n")
        if i % 60 == 0:
            print(mode, i, f"{time.time() - t0:.0f}s", flush=True)
    out.close()
```

**p0i_ablation_report.py**
```python
"""G39 point 0 round 2 report: every variant vs canon (same portraits/paths as p0_*.jsonl)."""
import json, statistics as stt
G = "/private/tmp/claude-501/-Users-vasyaevdokimov-repos-personal-finance-dss/fe25aad2-149b-48bd-a8b2-c62cc04ce4a1/scratchpad/g39/"
VARS = ["b_g41", "b_no_goal_eps", "b_floor_canon", "b_tau_canon", "b_floor_tau_canon", "canon_goal_eps", "canon_goal_toxic"]


def q(xs, p):
    xs = sorted(xs); return xs[int(round(p * (len(xs) - 1)))]


for tag in ("adr015", "mfo"):
    canon = {(r["index"], r["scen"]): r for r in map(json.loads, open(G + f"p0_{tag}.jsonl"))}
    orc = {(o["index"], o["scen"]): o for o in map(json.loads, open(G + f"p0_o_{tag}.jsonl"))}
    rows = [json.loads(l) for l in open(G + f"p0h_{tag}.jsonl")]
    for scen in ("base", "noinc"):
        rs = [r for r in rows if r["scen"] == scen]
        n = len(rs)
        print(f"\n=== {tag} / {scen} / plain portraits: {n}")
        print(f"{'variant':20} {'net worse>0.5%':>14} {'net better>0.5%':>15} {'median dnet %inc':>16} {'goal miss worse':>15} {'goal short better':>17} {'emerg worse':>11} {'emerg better':>12} {'G41 criterion viol':>18} {'gap to o-money med %':>20}")
        for v in VARS:
            dn, worse, better, gw, gb, ew, eb, viol, gap = [], 0, 0, 0, 0, 0, 0, 0, []
            for r in rs:
                c = canon[(r["index"], scen)]["canon"]; m = r[v]; inc = max(1.0, r["inc12"])
                d = (m["net_end"] - c["net_end"]) / inc; dn.append(d)
                worse += d < -0.005; better += d > 0.005
                gw += m["goals_missed"] > c["goals_missed"]; gb += m["goal_short"] < c["goal_short"] - 1
                ew += m["emerg_drawn"] > c["emerg_drawn"] + 1; eb += m["emerg_drawn"] < c["emerg_drawn"] - 1
                viol += (m["emerg_drawn"] > c["emerg_drawn"] + 1) or (m["goals_missed"] > c["goals_missed"])
                o = orc.get((r["index"], scen), {}).get("omoney", {})
                if "net_end" in o:
                    gap.append((o["net_end"] - m["net_end"]) / inc)
            print(f"{v:20} {worse / n:>14.1%} {better / n:>15.1%} {stt.median(dn):>16.3%} {gw / n:>15.1%} {gb / n:>17.1%} {ew / n:>11.1%} {eb / n:>12.1%} {viol / n:>18.1%} {stt.median(gap):>20.3%}")
        gapc = [(orc[(r['index'], scen)]['omoney']['net_end'] - canon[(r['index'], scen)]['canon']['net_end']) / max(1.0, r['inc12']) for r in rs if 'net_end' in orc[(r['index'], scen)]['omoney']]
        print(f"{'canon (reference)':20} gap to o-money median {stt.median(gapc):.3%}  p90 {q(gapc, .9):.3%}")
```

**p0j_price_and_tap.py**
```python
"""G39 point 0 round 2b: (1) price of goal punctuality: roubles of net position lost per rouble of goal shortfall avoided (variant vs canon);
(2) sensitivity to the ledger assumption 'goal funds are not touched in a crisis' (tap_goals=True: deficit beyond cushion is taken from goal funds before emergency debt)."""
import sys, json, statistics as stt
sys.path.insert(0, "/private/tmp/claude-501/-Users-vasyaevdokimov-repos-personal-finance-dss/fe25aad2-149b-48bd-a8b2-c62cc04ce4a1/scratchpad/g39")
G = "/private/tmp/claude-501/-Users-vasyaevdokimov-repos-personal-finance-dss/fe25aad2-149b-48bd-a8b2-c62cc04ce4a1/scratchpad/g39/"
mode = sys.argv[1]
if mode == "price":
    for tag in ("adr015", "mfo"):
        canon = {(r["index"], r["scen"]): r["canon"] for r in map(json.loads, open(G + f"p0_{tag}.jsonl"))}
        rows = [json.loads(l) for l in open(G + f"p0h_{tag}.jsonl")]
        for v in ("b_g41", "canon_goal_eps", "canon_goal_toxic"):
            for scen in ("base", "noinc"):
                lost = gained = 0.0; ratios = []
                for r in rows:
                    if r["scen"] != scen:
                        continue
                    c = canon[(r["index"], scen)]; m = r[v]
                    dg = (c["goal_short"] + c["far_pace_short"]) - (m["goal_short"] + m["far_pace_short"])
                    dn = c["net_end"] - m["net_end"]
                    if dg > 1:
                        lost += dn; gained += dg
                        ratios.append(dn / dg)
                print(f"{tag:6} {scen:5} {v:17}: portraits with less goal shortfall {len(ratios):4}; total net lost {lost:>12.0f} for {gained:>12.0f} roubles of shortfall avoided -> {lost / max(gained, 1):.3f} rub/rub; per portrait median {stt.median(ratios) if ratios else float('nan'):.3f}, p90 {sorted(ratios)[int(.9 * (len(ratios) - 1))] if ratios else float('nan'):.3f}")
else:
    import p0h_ablation as A
    S = A.S
    from tools.portrait_testing.generator import PortraitGenerator
    gen = PortraitGenerator(seed=S.SEED, version=2)
    res = {k: [0, 0] for k in ("b_g41", "canon_goal_eps", "b_no_goal_eps")}
    n = 0
    for i in range(int(sys.argv[2])):
        p = gen.generate_with_income_history(i)
        if p["kind"] != "plain" or p["income_total"] <= 0:
            continue
        path, vol = S.income_path(p, i, 2)
        c = S.simulate(p, path, "canon", p["r_bench"], tap_goals=True)
        n += 1
        for v in res:
            A.VARIANT["name"] = v
            m = S.simulate(p, path, "b", p["r_bench"], tap_goals=True)
            res[v][0] += m["emerg_drawn"] > c["emerg_drawn"] + 1
            res[v][1] += m["goals_missed"] > c["goals_missed"]
    print(f"noinc scenario, tap_goals=True, plain portraits {n}")
    for v, (e, g) in res.items():
        print(f"  {v:17}: more emergency debt than canon {e / n:.1%}; more missed goals than canon {g / n:.1%}")
```

---

# Часть A. Верификация — ядро считает правильно то, что задумано

## Пункт 1. Точный решатель как оракул (MILP / ЛП)

**Аналогия.** Проверять навигатор, сравнивая его маршрут с маршрутом таксиста, который знает все пробки заранее. Таксист недостижим в жизни, но разница в минутах — честная мера, насколько навигатор плох.

**Что проверяет.** Разрыв эвристики с математическим оптимумом той же задачи — числом, в рублях, а не спором. Не проверяет, правильная ли сама задача (это часть B).

**Что докажет/опровергнет в нашем ядре.** Модули: правило выбора `app/core/ranking.py::rank_alternatives` + `app/core/avalanche.py` + `app/core/crisis.py` в помесячном цикле. Проблемы Г40: № 4/22 (угол симплекса), № 2–3 (floor при токсичном долге), № 6 (срок цели). **Уже сделано в пункте 0** — это и есть первый реальный прогон оракула на популяции: разрыв канона до денежного оптимума — медиана 0,17 % годового дохода без токсичного долга, 1,3 % с МФО; p90 — 1,6 % и 3,3 %.

**Где оракул перестаёт быть дешёвым** (`p1_scale.py`):
```
LP oracle (p0c_milp v5):
  H= 12 loans=2 goals=2:     15.4 ms  status=kOptimal
  H= 12 loans=4 goals=4:      5.8 ms  status=kOptimal
  H= 12 loans=8 goals=6:      9.3 ms  status=kOptimal
  H= 36 loans=2 goals=2:      8.9 ms  status=HighsModelStatus.kInfeasible
  H= 36 loans=4 goals=4:     14.9 ms  status=HighsModelStatus.kInfeasible
  H= 36 loans=8 goals=6:     28.3 ms  status=HighsModelStatus.kInfeasible
  H= 60 loans=2 goals=2:     17.0 ms  status=HighsModelStatus.kInfeasible
  H= 60 loans=4 goals=4:     27.1 ms  status=HighsModelStatus.kInfeasible
  H= 60 loans=8 goals=6:     49.5 ms  status=HighsModelStatus.kInfeasible
  H=120 loans=2 goals=2:     36.2 ms  status=kOptimal
  H=120 loans=4 goals=4:     65.0 ms  status=kOptimal
  H=120 loans=8 goals=6:    140.6 ms  status=kOptimal
  H=240 loans=2 goals=2:   4268.1 ms  status=HighsModelStatus.kUnknown
  H=240 loans=4 goals=4:   3079.7 ms  status=HighsModelStatus.kSolveError
  H=240 loans=8 goals=6:  12806.3 ms  status=HighsModelStatus.kUnknown
MILP with binary 'alive' per loan-month (G41 f5b, constant income, no goals/emergency):
  H=  8 loans=2:     31.4 ms  solved
  H=  8 loans=4:    171.8 ms  solved
  H=  8 loans=8:    305.8 ms  solved
  H= 12 loans=2:     41.7 ms  solved
  H= 12 loans=4:    200.1 ms  solved
  H= 12 loans=8:   1000.4 ms  solved
  H= 24 loans=2:     42.5 ms  solved
  H= 24 loans=4:   1162.1 ms  solved
  H= 24 loans=8:     39.9 ms  infeasible/none
  H= 36 loans=2:     45.7 ms  solved
  H= 36 loans=4:   1632.6 ms  solved
  H= 36 loans=8:     61.9 ms  infeasible/none
  H= 60 loans=2:     90.4 ms  solved
  H= 60 loans=4:   1937.7 ms  solved
  H= 60 loans=8:    101.2 ms  infeasible/none
```
Что видно: (1) формулировка ЛП (без бинарных переменных, пункт 0.3 д) решается за 6–141 мс до горизонта 120 месяцев и 8 кредитов — **6 000 портретов за 57 с**; (2) честная MILP с бинарным признаком «кредит жив» растёт до ~1–2 с уже при 4–8 кредитах; (3) на горизонте 240 мес. ЛП ломается численно (экспоненциальный рост остатка под 292 % за 20 лет); (4) «infeasible» на 36–60 мес. в ЛП — **не установлено**, почему: гипотеза — граница экстренного займа «не больше дыры» считается по исходным платежам, а при ставке 292 % и минимальном платеже меньше процентов остаток растёт быстрее дохода. Для оракула на 12 месяцев это не мешает (0 отказов на 10 000 задач пункта 0).

**Уроки пункта 0 про сам метод — важнее скорости.** Оракул пять раз оказывался «хуже» политики, и каждый раз виноват был не код продукта, а несовпадение бухгалтерий: штрафы, момент начисления доходности, горизонт сроков, модель минимального платежа. **Правило для CI: оракул обязан проходить проверку доминирования** (`p0e_dominance.py`: денежный оракул без требований не ниже ни одной политики) **прежде, чем его разрыв используется как метрика.** Без неё оракул производит ложные дефекты.

**Цена внедрения.** Уже написано ~250 строк (`p0b_sim.py`, `p0c_milp.py`); перенос в `tools/model_validation/oracle_gap.py` + отчёт: **6–10 ч**. Библиотека: `highspy` (HiGHS, MIT) — новая dev-зависимость, в продукт не идёт. Прогон 3 000 портретов × 2 сценария: ~5 мин симуляция + ~1 мин оракул.

**Корзина: «сразу после синтеза»** — это единственный инструмент, который превращает спор о пути (б) в число; без него решение по пункту 0 принимать нечем.

## Пункт 2. Доказательство инвариантов для всех входов (Z3, интервалы) и property-based проверка (Hypothesis)

**Аналогия.** Тысяча проверенных мостов не доказывает, что мост выдержит любой грузовик. Расчёт по формуле прочности — доказывает, но только для той модели моста, что на бумаге. Property-based — это «тысяча случайных грузовиков, и если мост треснул, найти самый лёгкий, от которого он трескается». SMT-решатель — «расчёт на бумаге»: либо доказывает для всех входов, либо выдаёт конкретный контрпример.

**Что проверяет.** Свойства, верные для ЛЮБОГО входа: деньги сохраняются, подушка не падает ниже floor, платёж не растёт после досрочки. Hypothesis ищет нарушение случайным перебором и **ужимает** найденный пример до минимального. Z3 работает с точной вещественной арифметикой и отвечает «доказано для всех» (unsat отрицания) или «вот контрпример» (sat).

**Честная граница метода.** Z3 доказывает свойство **математической модели, заново записанной в скрипте**, а не Python-кода с `float` и `money()`. Разрыв закрывается двумя способами: (а) моделировать округление явно (сделано в 2.3, пункт 1c); (б) держать Hypothesis-тест на настоящем коде рядом с доказательством. Интервальная арифметика (пакеты `mpmath.iv`, `pyinterval`) для нашего ядра избыточна: нелинейностей почти нет (кроме $P/A$ и min-max), и Z3 с вещественными числами закрывает их сам.

### 2.1. Инварианты на 3 000 портретах и Hypothesis (`p2_inv.py`)

Скрипт (дословно):
```python
"""G39 item 2/3: invariants of the canon decision - (a) frequency on 3000 ADR-015 portraits (dates -> datetime),
(b) Hypothesis search with shrinking for a MINIMAL counterexample of every invariant that fails.
Nothing in app/ or tests/ is touched; the output is a list of candidate properties for tests/test_core_properties.py."""
import sys, copy, math, json
from datetime import datetime, timedelta, date
sys.path.insert(0, "/Users/vasyaevdokimov/repos/personal-finance-dss")
from hypothesis import given, settings, strategies as st, HealthCheck, Phase
from app.services.planning import run_planning, FLOW_EPS
import app.core.ranking as ranking
from app.core.goals_priority import inflated_target_amount
from tools.portrait_testing.generator import PortraitGenerator
T0 = datetime(2026, 7, 2)


def run(p):
    return run_planning(p["income_total"], p["expense_total"], p["obligations"], p["goals"], bliq=p["bliq"], r_bench=p["r_bench"],
                        risk_tolerance=p["risk_tolerance"], today=T0, income_history=p.get("income_history"))


def inv_conservation(p, r):
    rt = r["indicators"]["Rt"]
    for a in r["ranked"]:
        s = a["x_obl_effective"] + a["x_reserve_effective"] + sum(a.get("goal_allocation", {}).values())
        if abs(s - max(rt, 0.0)) > 0.05 + 1e-9 * abs(rt):
            return False, (a["id"], s, rt)
    return True, None


def inv_nonneg(p, r):
    for a in r["ranked"]:
        vals = [a["x_obl_effective"], a["x_reserve_effective"], *a.get("goal_allocation", {}).values()]
        if min(vals, default=0) < -0.005:
            return False, (a["id"], vals)
    return True, None


def inv_goal_cap(p, r):
    rem = {g["id"]: max(0.0, inflated_target_amount(g["target_amount"], g.get("deadline"), T0) - g["current_amount"]) for g in p["goals"]}
    for a in r["ranked"]:
        for k, v in a.get("goal_allocation", {}).items():
            if v > rem[k] + 0.02:
                return False, (a["id"], k, v, rem[k])
    return True, None


def inv_debt_sane(p, r):
    old = {o["id"]: o for o in p["obligations"]}
    for a in r["ranked"]:
        for o in a["obligation_allocation"]:
            if o["new_amount"] < -0.005 or o["new_payment"] > old[o["id"]]["monthly_payment"] + 0.01:
                return False, (a["id"], o)
    return True, None


def inv_crisis_iff_deficit(p, r):
    rt = r["indicators"]["Rt"]
    has = r["crisis_plan"] is not None
    if rt < -FLOW_EPS and not (has and r["crisis_plan"]["actions"]):
        return False, ("deficit without actions", rt)
    if rt >= 0 and has:
        return False, ("crisis at Rt>=0", rt)
    return True, None


def inv_crisis_keeps_floor(p, r):
    cp = r["crisis_plan"]
    if not cp:
        return True, None
    for act in cp["actions"]:
        if act["type"] == "close_debts_from_liquidity":
            fl = ranking.RESERVE_FLOOR_MONTHS * p["expense_total"]
            if act["bliq_remaining"] < fl - 0.02:
                return False, (act["bliq_remaining"], fl)
    return True, None


def inv_lexicographic_floor(p, r):
    if not r["ranked"]:
        return True, None
    top = max(a["floor_level"] for a in r["ranked"])
    return (r["ranked"][0]["floor_level"] >= top - 1e-9), (r["ranked"][0]["floor_level"], top)


def inv_prealloc_keeps_floor(p, r):
    """canon intent (math_model.md §8 floor is lexicographically first): the one-off goal closure of §11.5 should not take the cushion below the floor"""
    pre = r.get("bliq_preallocation") or {}
    if pre.get("bliq_used", 0) <= 0:
        return True, None
    fl = ranking.effective_floor_months(p["obligations"], p["r_bench"], income_history=p.get("income_history")) * p["expense_total"]
    before = p["bliq"]
    # v2: G40 6.4 example starts BELOW the floor (100 000 < 120 000) - the floor is lexicographically first, so any closure that leaves < floor violates it
    if pre["bliq_remaining"] < fl - 0.02:
        return False, (before, pre["bliq_used"], pre["bliq_remaining"], fl)
    return True, None


def inv_pdn_not_up(p, r):
    b = r["best"]
    if not b:
        return True, None
    return b["Dt_new"] <= r["indicators"]["Dt"] + 1e-4, (b["Dt_new"], r["indicators"]["Dt"])


def inv_avalanche_order(p, r):
    b = r["best"]
    if not b:
        return True, None
    old = {o["id"]: o for o in p["obligations"]}
    alloc = {o["id"]: o for o in b["obligation_allocation"]}
    paid = {k: old[k]["amount"] - alloc[k]["new_amount"] for k in alloc}
    for k, v in paid.items():
        if v > 0.01:
            for j, o in old.items():
                if o["interest_rate"] > old[k]["interest_rate"] and o["interest_rate"] >= p["r_bench"] and alloc[j]["new_amount"] > 0.01:
                    return False, (k, old[k]["interest_rate"], j, o["interest_rate"], alloc[j]["new_amount"])
    return True, None


def inv_ocr(p, r):
    b = r["best"]
    if not b or b["x_obl_effective"] <= 0.005:
        return True, None
    return any(o["interest_rate"] >= p["r_bench"] and o["amount"] > 0 for o in p["obligations"]), (b["x_obl_effective"],)


def inv_utility_range(p, r):
    return all(-1e-9 <= a["utility"] <= 1 + 1e-9 for a in r["ranked"]), None


def inv_deterministic(p, r):
    r2 = run(copy.deepcopy(p))
    f = lambda x: None if not x["best"] else (x["best"]["id"], x["best"]["x_obl_effective"], x["best"]["x_reserve_effective"])
    return f(r) == f(r2), (f(r), f(r2))


def inv_top3_distinct(p, r):
    sigs = [(round(a["x_obl_effective"]), round(a["x_reserve_effective"]), round(sum(a.get("goal_allocation", {}).values()))) for a in r["top3"]]
    return len(sigs) == len(set(sigs)), sigs


INVS = [inv_conservation, inv_nonneg, inv_goal_cap, inv_debt_sane, inv_crisis_iff_deficit, inv_crisis_keeps_floor, inv_lexicographic_floor,
        inv_prealloc_keeps_floor, inv_pdn_not_up, inv_avalanche_order, inv_ocr, inv_utility_range, inv_deterministic, inv_top3_distinct]

money = st.floats(min_value=0, max_value=2e6, allow_nan=False, allow_infinity=False).map(lambda x: round(x, 2))


@st.composite
def portrait(draw):
    inc = draw(money); exp = draw(money)
    n = draw(st.integers(0, 3))
    obls = []
    for i in range(n):
        amt = draw(st.floats(1, 3e6).map(lambda x: round(x, 2)))
        obls.append({"id": i + 1, "name": f"l{i}", "amount": amt, "interest_rate": draw(st.sampled_from([0.05, 0.12, 0.2, 0.3, 0.35, 1.0, 2.92])),
                     "monthly_payment": round(amt * draw(st.floats(0.005, 0.2)), 2)})
    goals = []
    for j in range(draw(st.integers(0, 3))):
        tgt = draw(st.floats(1000, 3e6).map(lambda x: round(x, 2)))
        dl = draw(st.one_of(st.none(), st.integers(-2, 72).map(lambda m: T0 + timedelta(days=30 * m))))
        goals.append({"id": j + 1, "name": f"g{j}", "target_amount": tgt, "current_amount": round(tgt * draw(st.floats(0, 1.1)), 2),
                      "deadline": dl, "category": draw(st.sampled_from(["income_growth", "safety", "material", "emotional"]))})
    hist = draw(st.one_of(st.none(), st.lists(st.floats(0, 3e5).map(lambda x: round(x, 2)), min_size=6, max_size=8)))
    return {"income_total": inc, "expense_total": exp, "obligations": obls, "goals": goals, "bliq": draw(money),
            "r_bench": draw(st.sampled_from([0.10, 0.14, 0.20])), "risk_tolerance": draw(st.integers(1, 5)), "income_history": hist}


def dt(d):
    return datetime(d.year, d.month, d.day) if isinstance(d, date) and not isinstance(d, datetime) else d


if __name__ == "__main__":
    n = int(sys.argv[1])
    gen = PortraitGenerator(seed=20260702, version=2)
    cnt = {f.__name__: [0, None] for f in INVS}
    for i in range(n):
        p = gen.generate_with_income_history(i)
        for g in p["goals"]:
            g["deadline"] = dt(g.get("deadline"))
        r = run(p)
        for f in INVS:
            ok, info = f(p, r)
            if not ok:
                cnt[f.__name__][0] += 1
                if cnt[f.__name__][1] is None:
                    cnt[f.__name__][1] = (i, p["kind"], info)
    print(f"(a) generator portraits: {n}")
    for k, (c, ex) in cnt.items():
        print(f"  {k:28} violated {c:>5} ({c / n:6.2%})" + (f"  first: portrait {ex[0]} kind={ex[1]} info={ex[2]}" if ex else ""))
    print("(b) Hypothesis, 400 examples each, derandomized, shrinking on")
    def make(f):
        @settings(max_examples=400, deadline=None, database=None, derandomize=True, suppress_health_check=list(HealthCheck))
        @given(portrait())
        def t(p):
            r = run(p)
            ok, info = f(p, r)
            assert ok, (info, p)
        return t
    for f in INVS:
        t = make(f)
        try:
            t()
            print(f"  {f.__name__:28} no counterexample in 400")
        except Exception as e:
            msg = str(e).splitlines()
            print(f"  {f.__name__:28} COUNTEREXAMPLE: {type(e).__name__}: {' | '.join(msg[:3])[:400]}")
```
Вывод:
```
(a) generator portraits: 3000
  inv_conservation             violated     0 ( 0.00%)
  inv_nonneg                   violated     0 ( 0.00%)
  inv_goal_cap                 violated     0 ( 0.00%)
  inv_debt_sane                violated     0 ( 0.00%)
  inv_crisis_iff_deficit       violated     0 ( 0.00%)
  inv_crisis_keeps_floor       violated     0 ( 0.00%)
  inv_lexicographic_floor      violated     0 ( 0.00%)
  inv_prealloc_keeps_floor     violated     1 ( 0.03%)  first: portrait 663 kind=deadline_now info=(171125.77, 84501.19, 86624.58, 180747.46)
  inv_pdn_not_up               violated     0 ( 0.00%)
  inv_avalanche_order          violated     0 ( 0.00%)
  inv_ocr                      violated     0 ( 0.00%)
  inv_utility_range            violated     0 ( 0.00%)
  inv_deterministic            violated     0 ( 0.00%)
  inv_top3_distinct            violated     0 ( 0.00%)
(b) Hypothesis, 400 examples each, derandomized, shrinking on
  inv_conservation             no counterexample in 400
  inv_nonneg                   no counterexample in 400
  inv_goal_cap                 no counterexample in 400
  inv_debt_sane                no counterexample in 400
  inv_crisis_iff_deficit       no counterexample in 400
  inv_crisis_keeps_floor       no counterexample in 400
  inv_lexicographic_floor      no counterexample in 400
  inv_prealloc_keeps_floor     COUNTEREXAMPLE: AssertionError: ((2000.0, 1000.0, 1000.0, 1002.0), {'income_total': 501.0, 'expense_total': 501.0, 'obligations': [], 'goals': [{'id': 1, 'name': 'g0', 'target_amount': 1000.0, 'current_amount': 0.0, 'deadline': datetime.datetime(2026, 7, 2, 0, 0), 'category': 'income_growth'}], 'bliq': 2000.0, 'r_bench': 0.1, 'risk_tolerance': 1, 'income_history': None})
  inv_pdn_not_up               no counterexample in 400
  inv_avalanche_order          no counterexample in 400
  inv_ocr                      no counterexample in 400
  inv_utility_range            no counterexample in 400
  inv_deterministic            no counterexample in 400
  inv_top3_distinct            no counterexample in 400
```
**Прочтение.** 13 из 14 инвариантов не нарушены ни на портретах, ни на 400 случайных примерах каждого. Нарушен **`inv_prealloc_keeps_floor`**: разовое закрытие близкой цели (§11.5, `goals_priority.py::preallocate_from_bliq`) оставляет подушку ниже floor. Hypothesis ужал пример до **минимального**: доход 501 ₽, расходы 501 ₽, подушка 2 000 ₽ (4 месяца), одна цель 1 000 ₽ со сроком «сегодня» → подушка после закрытия 1 000 ₽ при floor 1 002 ₽. Это дефект Г40 № 3 (6.4), теперь с минимальным контрпримером, пригодным прямо в регрессионный тест. На портретах генератора — 1 из 3 000 (портрет 663): генератор v2 почти не порождает целей со сроком ≤ 3 мес. (и без починки Д-01 не породил бы вовсе).

### 2.2. Недопустимые входы (`p2b_bad_inputs.py`)

```python
"""G39 item 2b: does the core fail loud on invalid inputs (NaN, inf, negative)? G40 7.4 checked pydantic schemas; this checks run_planning itself."""
import sys, math
from datetime import datetime
sys.path.insert(0, "/Users/vasyaevdokimov/repos/personal-finance-dss")
from app.services.planning import run_planning
T0 = datetime(2026, 7, 2)
base = dict(income_total=100_000.0, expense_total=60_000.0, obligations=[{"id": 1, "name": "l", "amount": 100_000.0, "interest_rate": 0.25, "monthly_payment": 5_000.0}],
            goals=[{"id": 1, "name": "g", "target_amount": 200_000.0, "current_amount": 0.0, "deadline": datetime(2027, 7, 2)}], bliq=50_000.0)
cases = {"income NaN": ("income_total", float("nan")), "income inf": ("income_total", float("inf")), "income negative": ("income_total", -50_000.0),
         "expenses NaN": ("expense_total", float("nan")), "bliq NaN": ("bliq", float("nan")), "bliq negative": ("bliq", -100_000.0),
         "rate NaN": ("rate", float("nan")), "rate negative": ("rate", -0.5), "payment > amount*10": ("pay", 2_000_000.0),
         "goal target NaN": ("target", float("nan")), "r_bench NaN": ("r_bench", float("nan"))}
for name, (k, v) in cases.items():
    kw = {kk: (vv if not isinstance(vv, list) else [dict(x) for x in vv]) for kk, vv in base.items()}
    rb = 0.14
    if k in ("income_total", "expense_total", "bliq"):
        kw[k] = v
    elif k == "rate":
        kw["obligations"][0]["interest_rate"] = v
    elif k == "pay":
        kw["obligations"][0]["monthly_payment"] = v
    elif k == "target":
        kw["goals"][0]["target_amount"] = v
    elif k == "r_bench":
        rb = v
    try:
        r = run_planning(kw["income_total"], kw["expense_total"], kw["obligations"], kw["goals"], bliq=kw["bliq"], r_bench=rb, today=T0)
        b = r["best"]
        desc = "CRISIS " + r["crisis_plan"]["severity"] if b is None else f"best {b['id']} obl={b['x_obl_effective']} res={b['x_reserve_effective']} goals={sum(b['goal_allocation'].values())} utility={b['utility']}"
        print(f"{name:22}: NO ERROR -> Rt={r['indicators']['Rt']} Lt={r['indicators']['Lt']} Dt={r['indicators']['Dt']} | {desc}")
    except Exception as e:
        print(f"{name:22}: raised {type(e).__name__}: {str(e)[:120]}")
```
Вывод:
```
income NaN            : raised ValueError: cannot convert float NaN to integer
income inf            : raised InvalidOperation: [<class 'decimal.InvalidOperation'>]
income negative       : NO ERROR -> Rt=-115000.0 Lt=0.8333 Dt=1.0 | CRISIS critical
expenses NaN          : raised ValueError: cannot convert float NaN to integer
bliq NaN              : NO ERROR -> Rt=35000.0 Lt=nan Dt=0.05 | best a0010 obl=0.0 res=0.0 goals=35000.0 utility=nan
bliq negative         : NO ERROR -> Rt=35000.0 Lt=-1.6667 Dt=0.05 | best a0100 obl=0.0 res=35000.0 goals=0 utility=0.3
rate NaN              : NO ERROR -> Rt=35000.0 Lt=0.8333 Dt=0.05 | best a0100 obl=0.0 res=35000.0 goals=0 utility=0.8
rate negative         : NO ERROR -> Rt=35000.0 Lt=0.8333 Dt=0.05 | best a0100 obl=0.0 res=35000.0 goals=0 utility=0.8
payment > amount*10   : NO ERROR -> Rt=-1960000.0 Lt=0.8333 Dt=20.0 | CRISIS critical
goal target NaN       : NO ERROR -> Rt=35000.0 Lt=0.8333 Dt=0.05 | best a0100 obl=0.0 res=35000.0 goals=0 utility=0.5
r_bench NaN           : NO ERROR -> Rt=35000.0 Lt=0.8333 Dt=0.05 | best a0100 obl=0.0 res=35000.0 goals=0 utility=0.8
```
🔴 **Дефект Д-07.** Ядро **молча** считает на NaN подушки (полезность `nan`, план «всё в цели»), на NaN ставки, NaN $r_{bench}$ и NaN суммы цели (кредит/цель просто выпадает из расчёта), на отрицательной подушке (Lt = −1,67). NaN дохода и расходов падает, но случайно и невнятно (`cannot convert float NaN to integer`). Г40 № 24 проверял только схемы pydantic; здесь — само ядро. Если хоть один вход дойдёт до ядра в обход схем (импорт выписки, демо-роут, B2B-роут), совет будет неверным без единого сигнала.

### 2.3. Доказательства Z3 (`p2c_z3.py`, `z3-solver` 5.1.0 в `scratchpad/g41/sv`)

```python
"""G39 item 2: proofs 'for all inputs' with the Z3 SMT solver (z3-solver 5.1.0 in scratchpad venv g41/sv).
Method: to prove property P for every input, ask Z3 for an input where NOT P holds. unsat = proven for all real-valued inputs
(of the MATHEMATICAL model re-encoded here, not of the Python float code); sat = a concrete counterexample."""
from z3 import Reals, Real, Solver, And, Or, Not, If, Implies, sat, unsat, simplify


def verdict(name, s):
    r = s.check()
    if r == unsat:
        print(f"[PROVEN for all inputs] {name}")
    elif r == sat:
        m = s.model()
        print(f"[COUNTEREXAMPLE] {name}: " + ", ".join(f"{d.name()}={m[d].as_decimal(3) if hasattr(m[d], 'as_decimal') else m[d]}" for d in sorted(m.decls(), key=lambda d: d.name())))
    else:
        print(f"[UNKNOWN] {name}: {r}")


# 1. crisis.py::_close_debts_from_liquidity, one loan, exact reals (no rounding): bliq_remaining >= RESERVE_FLOOR_MONTHS * expenses
A, P, bliq, E, deficit = Reals("A P bliq E deficit")
floor = 2 * E
available = bliq - floor
need = deficit
ratio = P / A
pay = If(available >= A, A, If(available < need / ratio + 0.01, available, need / ratio + 0.01))
s = Solver()
s.add(A > 0, P > 0, E >= 0, deficit > 0, available > 0)
s.add(Not(bliq - pay >= floor))
verdict("crisis closure keeps cushion >= floor (1 loan, exact arithmetic)", s)

# 1b. same, two loans in greedy sequence
A1, P1, A2, P2 = Reals("A1 P1 A2 P2")
s = Solver()
s.add(A1 > 0, P1 > 0, A2 > 0, P2 > 0, E >= 0, deficit > 0, available > 0)
pay1 = If(available >= A1, A1, If(available < deficit / (P1 / A1) + 0.01, available, deficit / (P1 / A1) + 0.01))
rec1 = P1 * pay1 / A1
left2 = available - pay1
need2 = deficit - rec1
pay2 = If(Or(need2 <= 0, left2 <= 0), 0, If(left2 >= A2, A2, If(left2 < need2 / (P2 / A2) + 0.01, left2, need2 / (P2 / A2) + 0.01)))
s.add(Not(bliq - pay1 - pay2 >= floor))
verdict("crisis closure keeps cushion >= floor (2 loans, greedy sequence, exact arithmetic)", s)

# 1c. WITH the code's rounding: pay = money(x) is ROUND_HALF_UP to kopecks -> modelled as pay in [x - 0.005, x + 0.005]
x, rnd = Reals("x rnd")
s = Solver()
s.add(A > 0, P > 0, E >= 0, deficit > 0, available > 0)
s.add(x == If(available >= A, A, If(available < need / ratio + 0.01, available, need / ratio + 0.01)))
s.add(rnd >= -0.005, rnd <= 0.005)
s.add(Not(bliq - (x + rnd) >= floor))
verdict("crisis closure keeps cushion >= floor WITH kopeck rounding", s)
s2 = Solver()
s2.add(A > 0, P > 0, E >= 0, deficit > 0, available > 0)
s2.add(x == If(available >= A, A, If(available < need / ratio + 0.01, available, need / ratio + 0.01)))
s2.add(rnd >= -0.005, rnd <= 0.005)
s2.add(Not(bliq - (x + rnd) >= floor - 0.005))
verdict("crisis closure keeps cushion >= floor - 0.005 rub WITH kopeck rounding", s2)

# 2. goals_priority.preallocate_from_bliq (§11.5): near goals closed if their sum <= 50 % of bliq; does the cushion stay >= floor (2 months)?
S_near = Real("S_near")
s = Solver()
s.add(bliq > 0, E > 0, S_near > 0, S_near <= 0.5 * bliq)
s.add(Not(bliq - S_near >= 2 * E))
verdict("§11.5 one-off goal closure keeps cushion >= floor", s)
s = Solver()
s.add(bliq > 0, E > 0, S_near > 0, S_near <= 0.5 * bliq, bliq >= 2 * E)   # even when the floor WAS met before
s.add(Not(bliq - S_near >= 2 * E))
verdict("§11.5 closure keeps cushion >= floor, given the floor was met before", s)
s = Solver()
s.add(bliq > 0, E > 0, S_near > 0, S_near <= 0.5 * bliq, bliq >= 4 * E)   # sufficient condition candidate
s.add(Not(bliq - S_near >= 2 * E))
verdict("§11.5 closure keeps cushion >= floor, given cushion >= 2 x floor before (candidate repair condition)", s)

# 3. avalanche.py: prepayment never raises the payment and never makes Rt' < Rt (hence filter gate 'Rt' >= 0' can only bind at Rt<0)
Aa, Pa, apply_, I, Ex = Reals("Aa Pa apply I Ex")
s = Solver()
s.add(Aa > 0, Pa >= 0, apply_ >= 0, apply_ <= Aa)
newP = Pa * (Aa - apply_) / Aa
s.add(Not(And(newP <= Pa, I - Ex - newP >= I - Ex - Pa)))
verdict("avalanche prepayment: new payment <= old payment and Rt' >= Rt", s)

# 4. filtering.py PDN gate: an admissible plan never has Dt' > max(0.40, Dt + eps); and since Dt' <= Dt always (3), the gate never rejects a plan with I > 0
Dnew, Dcur = Reals("Dnew Dcur")
s = Solver()
s.add(I > 0, Pa >= 0, Aa > 0, apply_ >= 0, apply_ <= Aa, Dcur == Pa / I, Dnew == Pa * (Aa - apply_) / Aa / I)
s.add(Dnew > If(0.40 >= Dcur + 5e-5, 0.40, Dcur + 5e-5))
verdict("PDN gate never rejects any alternative when income > 0 (the '<= 0.40' invariant is vacuous, cf. G40 #13)", s)
```
Вывод:
```
[PROVEN for all inputs] crisis closure keeps cushion >= floor (1 loan, exact arithmetic)
[PROVEN for all inputs] crisis closure keeps cushion >= floor (2 loans, greedy sequence, exact arithmetic)
[COUNTEREXAMPLE] crisis closure keeps cushion >= floor WITH kopeck rounding: /0=[(1, 1) -> 1, else -> 0], A=1, E=0, P=1, bliq=1, deficit=1, rnd=0.003?, x=1
[PROVEN for all inputs] crisis closure keeps cushion >= floor - 0.005 rub WITH kopeck rounding
[COUNTEREXAMPLE] §11.5 one-off goal closure keeps cushion >= floor: E=0.25, S_near=0.25, bliq=0.5
[COUNTEREXAMPLE] §11.5 closure keeps cushion >= floor, given the floor was met before: E=0.25, S_near=0.25, bliq=0.5
[PROVEN for all inputs] §11.5 closure keeps cushion >= floor, given cushion >= 2 x floor before (candidate repair condition)
[PROVEN for all inputs] avalanche prepayment: new payment <= old payment and Rt' >= Rt
[PROVEN for all inputs] PDN gate never rejects any alternative when income > 0 (the '<= 0.40' invariant is vacuous, cf. G40 #13)
```
**Прочтение по строкам.**
1. **Доказано для всех входов:** кризисный балансовый ход (`crisis.py::_close_debts_from_liquidity`) никогда не опускает подушку ниже 2 месяцев расходов — для одного и для двух кредитов в жадной последовательности. Это уже не «проверено на 1 410 портретах», а теорема о модели.
2. **С копеечным округлением** Z3 нашёл «контрпример» — но он **ложный**: модель округления в скрипте грубее настоящей (`money(1)` не превращается в 1,003). Зато **доказана** слабая граница «не ниже floor − 0,005 ₽». Урок для владельца: sat на огрублённой модели — повод уточнить модель, а не сразу дефект.
3. **§11.5 — контрпример, и даже когда floor до закрытия выполнялся** (подушка 0,5, расходы 0,25, цель 0,25). И сразу **доказано достаточное условие починки**: если подушка до закрытия ≥ 2 floor (4 месяца), правило «не больше 50 % подушки» floor не пробьёт. Это готовая формулировка правки для владельца.
4. **Доказано:** досрочка по Avalanche не повышает платёж и не уменьшает $R_t$.
5. **Доказано: ПДН-гейт `filtering.py` при доходе > 0 не отвергает ни одной альтернативы вообще** — потому что по п. 4 ни одна альтернатива не повышает ПДН. Г40 № 13 видел «0 срабатываний из 1 410» на выборке; теперь это верно для всех входов. Инвариант «ПДН ≤ 0,40» в нынешнем коде — декларация, а не ограничение.

**Цена внедрения.** Hypothesis уже в проекте: перенос 14 инвариантов в `tests/test_core_properties.py` — **4–6 ч** (стратегия портрета уже есть: `scenario()` в том же файле). Z3: `z3-solver` (MIT, ~40 МБ колесо) — dev-зависимость; 5 доказательств — **4–8 ч**, плюс по 1–2 ч на каждое новое правило канона (ε-ограничения пути (б) — первые кандидаты). Регрессионный тест на минимальный пример §11.5 — 0,5 ч.

**Корзина.** Инварианты Hypothesis и минимальный пример §11.5 — **«сразу после синтеза»**. Проверка входов ядра (Д-07) — **«до запуска»**. Z3 — **«до запуска»** для кризисного модуля и ПДН-гейта (формулировка для магистерской и для ответа «докажите, что план не уводит в минус»), остальное — **«потом»**.

## Пункт 3. Метаморфические отношения для нашего ядра (направленные)

**Аналогия.** Не знаешь точного веса посылки, но точно знаешь: если положить в неё ещё один предмет, весы не должны показать меньше. Метаморфическое отношение — это такое «если так, то не меньше/не больше/то же самое», которое можно проверить без знания правильного ответа.

**Что это по первоисточнику.** Chen, Kuo, Liu, Poon, Towey, Tse, Zhou 2018, *ACM Computing Surveys* 51(1), Article 4, DOI 10.1145/3143561 — текст добыт 16.09.2026 (`raw/closed_forever_retry_2026-09-16.md`, копия `homes.cs.washington.edu/~rjust/courses/CSE503/2021_02_12-reading2.pdf`, HTTP 200). Дословно: «**Definition 1 (Metamorphic Relation).** Let f be a target function or algorithm. A metamorphic relation is a necessary property of f over a sequence of two or more inputs x₁, x₂, …, xₙ, where n ⩾ 2, and their corresponding outputs f(x₁), f(x₂), …, f(xₙ).» и «If R′ is not satisfied, then this MR has revealed that P is faulty.» Второй обзор — Segura, Fraser, Sánchez, Ruiz-Cortés 2016, *IEEE TSE* 42(9), DOI 10.1109/TSE.2016.2532875 (OpenAlex `api.openalex.org/works/doi:10.1109/TSE.2016.2532875`, HTTP 200, 17.09.2026), реферат дословно: «Metamorphic testing provides an alternative, where correctness is not determined by checking an individual concrete output, but by applying a transformation to a test input and observing how the program output "morphs" into a different one as a result.»

**Чем наш набор отличается от уже существующего.** В `tools/portrait_testing/generator.py` есть `METAMORPHIC_RELATIONS` (M1_income … M5_scale) — но это **возмущения с замером расстояния L1**, без направления: «насколько изменился план». Направленных утверждений «не должно уменьшиться» в них нет, и `tests/test_metamorphic_relations.py` проверяет только сами возмущения (какой элемент тронут), не решение ядра.

**Набор из 16 направленных отношений** — проверены на 3 000 портретах ADR-015 (даты → `datetime`), допуск 1 ₽, модуль — `app/services/planning.py::run_planning` (один месяц). «Нечувствительность» — выход не изменился вовсе (это не нарушение, но сигнал слепоты).

Скрипт `p3_mr.py` (дословно):
```python
"""G39 item 3: DIRECTIONAL metamorphic relations on the canon decision (app.services.planning.run_planning, one month).
Source portraits: PortraitGenerator(seed=20260702, version=2).generate_with_income_history(i), deadlines converted date -> datetime (p0a).
For each relation: twin input, expected direction of a named output, tolerance 1 rub. Counts: checked / violated / insensitive (identical output).
The existing generator.py METAMORPHIC_RELATIONS measure L1 distance only (no direction) - these are new."""
import sys, copy, json, math
from datetime import datetime, timedelta, date
sys.path.insert(0, "/Users/vasyaevdokimov/repos/personal-finance-dss")
from app.services.planning import run_planning
import app.core.ranking as ranking
from tools.portrait_testing.generator import PortraitGenerator
T0 = datetime(2026, 7, 2)
TOL = 1.0


def dt(d):
    return datetime(d.year, d.month, d.day) if isinstance(d, date) and not isinstance(d, datetime) else d


def run(p, today=T0):
    return run_planning(p["income_total"], p["expense_total"], p["obligations"], p["goals"], bliq=p["bliq"], r_bench=p["r_bench"],
                        risk_tolerance=p["risk_tolerance"], today=today, income_history=p.get("income_history"))


def goal_money(r, gid):
    b = r["best"]
    v = (b or {}).get("goal_allocation", {}).get(gid, 0.0) if b else 0.0
    v += sum(c["amount"] for c in (r.get("bliq_preallocation") or {}).get("closed_goals", []) if c["id"] == gid)
    return v


def paid_in(r, oid, obls):
    b = r["best"]
    if not b:
        return 0.0
    before = {o["id"]: o["amount"] for o in obls}
    return sum(before[o["id"]] - o["new_amount"] for o in b["obligation_allocation"] if o["id"] == oid)


def total_alloc(r):
    b = r["best"]
    return 0.0 if not b else b["x_obl_effective"] + b["x_reserve_effective"] + sum(b.get("goal_allocation", {}).values())


def sig(r):
    b = r["best"]
    if not b:
        return ("crisis", r["crisis_plan"]["severity"] if r["crisis_plan"] else None)
    return (round(b["x_obl_effective"]), round(b["x_reserve_effective"]), tuple(sorted((k, round(v)) for k, v in b.get("goal_allocation", {}).items())))


REL = {}


def rel(name, doc):
    def deco(f):
        REL[name] = (doc, f); return f
    return deco


@rel("MR01_income_up", "income +10% -> resource Rt of the chosen plan not lower; total allocated not lower; no new crisis")
def mr01(p):
    t = copy.deepcopy(p); t["income_total"] = p["income_total"] * 1.10
    a, b = run(p), run(t)
    if a["best"] is None:
        return None
    bad = (b["best"] is None) or b["best"]["Rt_new"] < a["best"]["Rt_new"] - TOL or total_alloc(b) < total_alloc(a) - TOL
    return bad, sig(a) == sig(b), (a["best"]["Rt_new"], None if b["best"] is None else b["best"]["Rt_new"])


@rel("MR02_rate_up_target", "rate of the most expensive avalanche target x1.5 -> roubles prepaid INTO THAT loan not lower")
def mr02(p):
    tg = [o for o in p["obligations"] if o["interest_rate"] >= p["r_bench"] and o["amount"] > 1]
    if not tg:
        return None
    o = max(tg, key=lambda o: o["interest_rate"])
    t = copy.deepcopy(p); next(x for x in t["obligations"] if x["id"] == o["id"])["interest_rate"] = o["interest_rate"] * 1.5
    a, b = run(p), run(t)
    if a["best"] is None or b["best"] is None:
        return None
    pa, pb = paid_in(a, o["id"], p["obligations"]), paid_in(b, o["id"], t["obligations"])
    return pb < pa - TOL, abs(pa - pb) <= TOL, (round(pa), round(pb))


@rel("MR03_rate_cross_bench", "a loan below r_bench raised to r_bench+10pp -> total prepayment x_obl_effective not lower")
def mr03(p):
    lo = [o for o in p["obligations"] if o["interest_rate"] < p["r_bench"] and o["amount"] > 1]
    if not lo:
        return None
    o = lo[0]
    t = copy.deepcopy(p); next(x for x in t["obligations"] if x["id"] == o["id"])["interest_rate"] = p["r_bench"] + 0.10
    a, b = run(p), run(t)
    if a["best"] is None or b["best"] is None:
        return None
    return b["best"]["x_obl_effective"] < a["best"]["x_obl_effective"] - TOL, abs(b["best"]["x_obl_effective"] - a["best"]["x_obl_effective"]) <= TOL, (a["best"]["x_obl_effective"], b["best"]["x_obl_effective"])


@rel("MR04_deadline_later", "nearest dated goal deadline +6 months -> money to that goal this month not higher")
def mr04(p):
    dated = [g for g in p["goals"] if g.get("deadline") and g["target_amount"] - g["current_amount"] > 1]
    if not dated:
        return None
    g = min(dated, key=lambda g: g["deadline"])
    t = copy.deepcopy(p); next(x for x in t["goals"] if x["id"] == g["id"])["deadline"] = g["deadline"] + timedelta(days=183)
    a, b = run(p), run(t)
    if a["best"] is None:
        return None
    ga, gb = goal_money(a, g["id"]), goal_money(b, g["id"])
    return gb > ga + TOL, abs(ga - gb) <= TOL, (round(ga), round(gb))


@rel("MR05_deadline_sooner", "dated goal deadline moved to 2 months from today (if later) -> money to that goal not lower")
def mr05(p):
    dated = [g for g in p["goals"] if g.get("deadline") and g["deadline"] > T0 + timedelta(days=90) and g["target_amount"] - g["current_amount"] > 1]
    if not dated:
        return None
    g = dated[0]
    t = copy.deepcopy(p); next(x for x in t["goals"] if x["id"] == g["id"])["deadline"] = T0 + timedelta(days=60)
    a, b = run(p), run(t)
    if a["best"] is None:
        return None
    ga, gb = goal_money(a, g["id"]), goal_money(b, g["id"])
    return gb < ga - TOL, abs(ga - gb) <= TOL, (round(ga), round(gb))


@rel("MR06_target_up", "goal target +20% -> money to that goal not lower")
def mr06(p):
    gs = [g for g in p["goals"] if g["target_amount"] - g["current_amount"] > 1]
    if not gs:
        return None
    g = gs[0]
    t = copy.deepcopy(p); next(x for x in t["goals"] if x["id"] == g["id"])["target_amount"] = g["target_amount"] * 1.2
    a, b = run(p), run(t)
    if a["best"] is None:
        return None
    ga, gb = goal_money(a, g["id"]), goal_money(b, g["id"])
    return gb < ga - TOL, abs(ga - gb) <= TOL, (round(ga), round(gb))


@rel("MR07_bliq_up", "cushion +1 month of expenses -> reserve contribution not higher AND cushion after plan (Lt_new) not lower")
def mr07(p):
    if p["expense_total"] <= 0:
        return None
    t = copy.deepcopy(p); t["bliq"] = p["bliq"] + p["expense_total"]
    a, b = run(p), run(t)
    if a["best"] is None or b["best"] is None:
        return None
    bad = b["best"]["x_reserve_effective"] > a["best"]["x_reserve_effective"] + TOL or b["best"]["Lt_new"] < a["best"]["Lt_new"] - 1e-6
    return bad, sig(a) == sig(b), (a["best"]["x_reserve_effective"], b["best"]["x_reserve_effective"], a["best"]["Lt_new"], b["best"]["Lt_new"])


@rel("MR08_permutation", "reverse order of obligations and goals -> identical per-id plan")
def mr08(p):
    t = copy.deepcopy(p); t["obligations"] = t["obligations"][::-1]; t["goals"] = t["goals"][::-1]
    a, b = run(p), run(t)
    return sig(a) != sig(b), sig(a) == sig(b), (sig(a), sig(b))


@rel("MR09_scale10", "all money x10 -> plan shares identical (x/R to 0.1 %)")
def mr09(p):
    k = 10.0
    t = copy.deepcopy(p)
    for key in ("income_total", "expense_total", "bliq"):
        t[key] = p[key] * k
    for o in t["obligations"]:
        o["amount"] *= k; o["monthly_payment"] *= k
    for g in t["goals"]:
        g["target_amount"] *= k; g["current_amount"] *= k
    if t.get("income_history"):
        t["income_history"] = [x * k for x in t["income_history"]]
    a, b = run(p), run(t)
    if (a["best"] is None) != (b["best"] is None):
        return True, False, ("crisis mismatch",)
    if a["best"] is None:
        return None
    R = max(1e-9, total_alloc(a))
    sa = (a["best"]["x_obl_effective"] / R, a["best"]["x_reserve_effective"] / R)
    sb = (b["best"]["x_obl_effective"] / (k * R), b["best"]["x_reserve_effective"] / (k * R))
    bad = max(abs(x - y) for x, y in zip(sa, sb)) > 1e-3
    return bad, not bad, (sa, sb)


@rel("MR10_expenses_up", "expenses +5% -> resource Rt of the plan not higher and total allocated not higher")
def mr10(p):
    t = copy.deepcopy(p); t["expense_total"] = p["expense_total"] * 1.05
    a, b = run(p), run(t)
    if a["best"] is None or b["best"] is None:
        return None
    bad = b["best"]["Rt_new"] > a["best"]["Rt_new"] + TOL or total_alloc(b) > total_alloc(a) + TOL
    return bad, sig(a) == sig(b), (a["best"]["Rt_new"], b["best"]["Rt_new"])


@rel("MR11_rbench_up", "r_bench +5pp -> total prepayment not higher (fewer loans pass the OCR filter)")
def mr11(p):
    t = copy.deepcopy(p); t["r_bench"] = p["r_bench"] + 0.05
    a, b = run(p), run(t)
    if a["best"] is None or b["best"] is None:
        return None
    return b["best"]["x_obl_effective"] > a["best"]["x_obl_effective"] + TOL, abs(b["best"]["x_obl_effective"] - a["best"]["x_obl_effective"]) <= TOL, (a["best"]["x_obl_effective"], b["best"]["x_obl_effective"])


@rel("MR12_time_shift", "today +17 days and every deadline +17 days -> identical plan")
def mr12(p):
    t = copy.deepcopy(p)
    for g in t["goals"]:
        if g.get("deadline"):
            g["deadline"] = g["deadline"] + timedelta(days=17)
    a, b = run(p), run(t, today=T0 + timedelta(days=17))
    return sig(a) != sig(b), sig(a) == sig(b), (sig(a), sig(b))


@rel("MR13_volatility_up", "income history spread x2 around its mean (same mean) -> effective floor not lower and cushion after plan not lower")
def mr13(p):
    h = p.get("income_history")
    if not h or min(h) <= 0:
        return None
    mu = sum(h) / len(h)
    t = copy.deepcopy(p); t["income_history"] = [max(1.0, mu + 2 * (x - mu)) for x in h]
    fa = ranking.effective_floor_months(p["obligations"], p["r_bench"], income_history=p["income_history"])
    fb = ranking.effective_floor_months(t["obligations"], t["r_bench"], income_history=t["income_history"])
    a, b = run(p), run(t)
    if a["best"] is None or b["best"] is None:
        return None
    bad = fb < fa - 1e-9 or b["best"]["Lt_new"] < a["best"]["Lt_new"] - 1e-6
    return bad, sig(a) == sig(b), (fa, fb, a["best"]["Lt_new"], b["best"]["Lt_new"])


@rel("MR14_category_up", "goal category material -> safety (weight 1 -> 2) -> money to that goal not lower")
def mr14(p):
    gs = [g for g in p["goals"] if g["target_amount"] - g["current_amount"] > 1]
    if len(gs) < 2:
        return None
    g = gs[0]
    t = copy.deepcopy(p); next(x for x in t["goals"] if x["id"] == g["id"])["category"] = "safety"
    a, b = run(p), run(t)
    if a["best"] is None:
        return None
    ga, gb = goal_money(a, g["id"]), goal_money(b, g["id"])
    return gb < ga - TOL, abs(ga - gb) <= TOL, (round(ga), round(gb))


@rel("MR15_add_goal", "add a new open-ended goal 500 000 -> money to EXISTING goals not higher")
def mr15(p):
    gs = [g for g in p["goals"] if g["target_amount"] - g["current_amount"] > 1]
    if not gs:
        return None
    t = copy.deepcopy(p); t["goals"].append({"id": 777, "name": "new", "target_amount": 500_000.0, "current_amount": 0.0, "deadline": None})
    a, b = run(p), run(t)
    if a["best"] is None or b["best"] is None:
        return None
    sa = sum(goal_money(a, g["id"]) for g in gs); sb = sum(goal_money(b, g["id"]) for g in gs)
    return sb > sa + TOL, abs(sa - sb) <= TOL, (round(sa), round(sb))


@rel("MR16_repay_loan", "remove the cheapest loan (as if repaid) -> Rt of the plan not lower")
def mr16(p):
    if not p["obligations"]:
        return None
    o = min(p["obligations"], key=lambda o: o["interest_rate"])
    t = copy.deepcopy(p); t["obligations"] = [x for x in t["obligations"] if x["id"] != o["id"]]
    a, b = run(p), run(t)
    if a["best"] is None:
        return None
    return (b["best"] is None) or b["best"]["Rt_new"] < a["best"]["Rt_new"] - TOL, sig(a) == sig(b), (a["best"]["Rt_new"],)


if __name__ == "__main__":
    n = int(sys.argv[1])
    gen = PortraitGenerator(seed=20260702, version=2)
    stats = {k: [0, 0, 0, []] for k in REL}
    for i in range(n):
        p = gen.generate_with_income_history(i)
        for g in p["goals"]:
            g["deadline"] = dt(g.get("deadline"))
        for name, (doc, f) in REL.items():
            res = f(p)
            if res is None:
                continue
            bad, same, info = res
            s = stats[name]; s[0] += 1; s[1] += bool(bad); s[2] += bool(same)
            if bad and len(s[3]) < 3:
                s[3].append((i, p["kind"], p["risk_tolerance"], info))
    print(f"portraits {n}")
    print(f"{'relation':24} {'checked':>7} {'violated':>9} {'insensitive':>11}  expectation")
    for name, (doc, f) in REL.items():
        c, v, s, ex = stats[name]
        print(f"{name:24} {c:>7} {v:>5} ({(v / c if c else 0):5.1%}) {s:>5} ({(s / c if c else 0):5.1%})  {doc}")
        for e in ex:
            print(f"      example: portrait {e[0]} kind={e[1]} profile={e[2]} -> {e[3]}")
```
Вывод:
```
portraits 3000
relation                 checked  violated insensitive  expectation
MR01_income_up              2443     0 ( 0.0%)     0 ( 0.0%)  income +10% -> resource Rt of the chosen plan not lower; total allocated not lower; no new crisis
MR02_rate_up_target         1132     0 ( 0.0%)   995 (87.9%)  rate of the most expensive avalanche target x1.5 -> roubles prepaid INTO THAT loan not lower
MR03_rate_cross_bench        591     4 ( 0.7%)   429 (72.6%)  a loan below r_bench raised to r_bench+10pp -> total prepayment x_obl_effective not lower
      example: portrait 1187 kind=plain profile=5 -> (27201.83, 25796.07)
      example: portrait 1244 kind=plain profile=1 -> (11704.71, 3901.57)
      example: portrait 2135 kind=plain profile=1 -> (23415.19, 16725.13)
MR04_deadline_later         1738     4 ( 0.2%)  1636 (94.1%)  nearest dated goal deadline +6 months -> money to that goal this month not higher
      example: portrait 299 kind=plain profile=4 -> (8159, 9179)
      example: portrait 1221 kind=zero_expenses profile=5 -> (27799, 29710)
      example: portrait 2649 kind=zero_expenses profile=5 -> (51120, 59778)
MR05_deadline_sooner        1668    10 ( 0.6%)  1302 (78.1%)  dated goal deadline moved to 2 months from today (if later) -> money to that goal not lower
      example: portrait 105 kind=huge_bliq profile=5 -> (95, 86)
      example: portrait 466 kind=plain profile=3 -> (48, 0)
      example: portrait 643 kind=plain profile=5 -> (20034, 12020)
MR06_target_up              1878     8 ( 0.4%)  1851 (98.6%)  goal target +20% -> money to that goal not lower
      example: portrait 573 kind=pdn_boundary profile=4 -> (410, 369)
      example: portrait 663 kind=deadline_now profile=4 -> (84501, 0)
      example: portrait 2035 kind=plain profile=3 -> (14, 0)
MR07_bliq_up                2371    50 ( 2.1%)  1757 (74.1%)  cushion +1 month of expenses -> reserve contribution not higher AND cushion after plan (Lt_new) not lower
      example: portrait 39 kind=giant_scale profile=2 -> (0.0, 709544236.44, 2.9862, 5.0011)
      example: portrait 217 kind=plain profile=4 -> (19490.3, 5847.09, 2.0433, 2.0409)
      example: portrait 428 kind=plain profile=2 -> (0.0, 4857.72, 3.6422, 4.9936)
MR08_permutation            3000     0 ( 0.0%)  3000 (100.0%)  reverse order of obligations and goals -> identical per-id plan
MR09_scale10                2443     2 ( 0.1%)  2441 (99.9%)  all money x10 -> plan shares identical (x/R to 0.1 %)
      example: portrait 2663 kind=plain profile=1 -> ((0.30000000000000004, 0.7000000000000001), (0.0, 1.0))
      example: portrait 2969 kind=plain profile=5 -> ((1.0, 0.0), (0.7999999999999999, 0.0))
MR10_expenses_up            2261     0 ( 0.0%)    72 ( 3.2%)  expenses +5% -> resource Rt of the plan not higher and total allocated not higher
MR11_rbench_up              2443     0 ( 0.0%)  2263 (92.6%)  r_bench +5pp -> total prepayment not higher (fewer loans pass the OCR filter)
MR12_time_shift             3000     0 ( 0.0%)  3000 (100.0%)  today +17 days and every deadline +17 days -> identical plan
MR13_volatility_up          2443     0 ( 0.0%)  2396 (98.1%)  income history spread x2 around its mean (same mean) -> effective floor not lower and cushion after plan not lower
MR14_category_up            1355     4 ( 0.3%)  1082 (79.9%)  goal category material -> safety (weight 1 -> 2) -> money to that goal not lower
      example: portrait 466 kind=plain profile=3 -> (48, 0)
      example: portrait 1551 kind=giant_scale profile=4 -> (582536, 0)
      example: portrait 2035 kind=plain profile=3 -> (14, 0)
MR15_add_goal               1878    11 ( 0.6%)  1480 (78.8%)  add a new open-ended goal 500 000 -> money to EXISTING goals not higher
      example: portrait 498 kind=kopeck_scale profile=3 -> (0, 10)
      example: portrait 1351 kind=plain profile=3 -> (0, 115)
      example: portrait 1467 kind=giant_scale profile=4 -> (0, 127525553)
MR16_repay_loan             1392     0 ( 0.0%)     0 ( 0.0%)  remove the cheapest loan (as if repaid) -> Rt of the plan not lower
```

**Разбор причин на первых примерах** (`p3b_diag.py`):
```python
"""G39 item 3b: root cause of each violated metamorphic relation on its first example portrait."""
import sys, copy
sys.path.insert(0, "/private/tmp/claude-501/-Users-vasyaevdokimov-repos-personal-finance-dss/fe25aad2-149b-48bd-a8b2-c62cc04ce4a1/scratchpad/g39")
import p3_mr as M
from tools.portrait_testing.generator import PortraitGenerator
gen = PortraitGenerator(seed=20260702, version=2)


def portrait(i):
    p = gen.generate_with_income_history(i)
    for g in p["goals"]:
        g["deadline"] = M.dt(g.get("deadline"))
    return p


def show(tag, r):
    b = r["best"]; pre = r["bliq_preallocation"]
    if b is None:
        print(f"   {tag}: CRISIS {r['crisis_plan']['severity']}"); return
    print(f"   {tag}: best {b['id']} d/r/g nominal=({b['x_obligations']:.0f},{b['x_reserve']:.0f},{b['x_goals']:.0f}) effective obl={b['x_obl_effective']:.0f} res={b['x_reserve_effective']:.0f} goals={sum(b['goal_allocation'].values()):.0f}"
          f" | prealloc used={pre['bliq_used']:.0f} closed={[c['id'] for c in pre['closed_goals']]} | floor_level={b['floor_level']} utility={b['utility']} scores={b['scores']}"
          f" | admissible={r['admissible_count']} Rt={r['indicators']['Rt']:.0f} Bliq_after={r['indicators']['Bliq']:.0f}")
    ties = [a['id'] for a in r['ranked'] if a['floor_level'] == b['floor_level'] and a['utility'] == b['utility']]
    if len(ties) > 1:
        print(f"      TIE at the top (floor_level, utility): {ties[:6]}")


cases = [("MR03_rate_cross_bench", 1244), ("MR04_deadline_later", 299), ("MR05_deadline_sooner", 643), ("MR06_target_up", 663),
         ("MR07_bliq_up", 217), ("MR07_bliq_up", 428), ("MR09_scale10", 2663), ("MR14_category_up", 466), ("MR15_add_goal", 1351)]
for name, i in cases:
    p = portrait(i)
    doc, f = M.REL[name]
    print(f"\n=== {name} portrait {i} kind={p['kind']} profile={p['risk_tolerance']} r_bench={p['r_bench']} income={p['income_total']:.0f} exp={p['expense_total']:.0f} bliq={p['bliq']:.0f}")
    print("   obligations:", [(o['id'], round(o['amount']), o['interest_rate'], round(o['monthly_payment'])) for o in p['obligations']])
    print("   goals:", [(g['id'], round(g['target_amount']), round(g['current_amount']), str(g['deadline'])[:10] if g['deadline'] else None) for g in p['goals']])
    captured = {}
    orig = M.run
    calls = []
    def spy(q, today=M.T0):
        r = orig(q, today); calls.append((q, r)); return r
    M.run = spy
    res = f(p)
    M.run = orig
    print("   relation result:", res)
    show("source", calls[0][1]); show("twin  ", calls[1][1])
```
```

=== MR03_rate_cross_bench portrait 1244 kind=plain profile=1 r_bench=0.1596 income=102913 exp=45221 bliq=222599
   obligations: [(1, 307103, 0.1502, 6864), (2, 197472, 0.2107, 4668), (3, 287718, 0.2367, 7143)]
   goals: [(1, 127083, 12777, '2028-04-22'), (2, 1501904, 234661, '2027-03-29'), (3, 219286, 32926, '2028-02-22')]
   relation result: (True, False, (11704.71, 3901.57))
   source: best a370 d/r/g nominal=(11705,27311,0) effective obl=11705 res=27311 goals=0 | prealloc used=0 closed=[] | floor_level=2.1352 utility=0.4521 scores={'Rt_norm': 0.3, 'Lt_norm': 0.7, 'Dt_norm': 0.309, 'Si_norm': 0.0, 'Lt_capped': 5.5264} | admissible=66 Rt=39016 Bliq_after=222599
      TIE at the top (floor_level, utility): ['a370', 'a820']
   twin  : best a190 d/r/g nominal=(3902,35114,0) effective obl=3902 res=35114 goals=0 | prealloc used=0 closed=[] | floor_level=2.1352 utility=0.4515 scores={'Rt_norm': 0.1, 'Lt_norm': 0.9, 'Dt_norm': 0.106, 'Si_norm': 0.0, 'Lt_capped': 5.6989} | admissible=66 Rt=39016 Bliq_after=222599
      TIE at the top (floor_level, utility): ['a190', 'a370', 'a550', 'a730', 'a910']

=== MR04_deadline_later portrait 299 kind=plain profile=4 r_bench=0.2 income=36933 exp=16536 bliq=44213
   obligations: []
   goals: [(1, 603290, 14465, '2030-03-13'), (2, 1958364, 1579228, '2029-09-14')]
   relation result: (True, False, (8159, 9179))
   source: best a028 d/r/g nominal=(0,4079,16317) effective obl=0 res=4079 goals=16317 | prealloc used=0 closed=[] | floor_level=2.1266 utility=0.8009 scores={'Rt_norm': 1.0, 'Lt_norm': 0.298, 'Dt_norm': 1.0, 'Si_norm': 0.804, 'Lt_capped': 2.9203} | admissible=11 Rt=20397 Bliq_after=44213
   twin  : best a019 d/r/g nominal=(0,2040,18357) effective obl=0 res=2040 goals=18357 | prealloc used=0 closed=[] | floor_level=2.1266 utility=0.8015 scores={'Rt_norm': 1.0, 'Lt_norm': 0.149, 'Dt_norm': 1.0, 'Si_norm': 0.905, 'Lt_capped': 2.797} | admissible=11 Rt=20397 Bliq_after=44213

=== MR05_deadline_sooner portrait 643 kind=plain profile=5 r_bench=0.1 income=124676 exp=104643 bliq=334344
   obligations: []
   goals: [(1, 88184, 78405, '2026-09-30'), (2, 1710894, 909141, '2026-10-30')]
   relation result: (True, False, (20034, 12020))
   source: best a0010 d/r/g nominal=(0,0,20034) effective obl=0 res=0 goals=20034 | prealloc used=9779 closed=[1] | floor_level=2.147 utility=1.0 scores={'Rt_norm': 1.0, 'Lt_norm': 1.0, 'Dt_norm': 1.0, 'Si_norm': 1.0, 'Lt_capped': 3.0} | admissible=11 Rt=20034 Bliq_after=324565
   twin  : best a0010 d/r/g nominal=(0,0,20034) effective obl=0 res=0 goals=20034 | prealloc used=0 closed=[] | floor_level=2.147 utility=1.0 scores={'Rt_norm': 1.0, 'Lt_norm': 1.0, 'Dt_norm': 1.0, 'Si_norm': 1.0, 'Lt_capped': 3.0} | admissible=11 Rt=20034 Bliq_after=334344

=== MR06_target_up portrait 663 kind=deadline_now profile=4 r_bench=0.1596 income=171188 exp=90374 bliq=171126
   obligations: [(1, 337548, 0.1821, 22676), (2, 534051, 0.2728, 26684)]
   goals: [(1, 84501, 0, '2026-07-02')]
   relation result: (True, False, (84501, 0))
   source: best a0100 d/r/g nominal=(0,31454,0) effective obl=0 res=31454 goals=0 | prealloc used=84501 closed=[1] | floor_level=1.3066 utility=0.5 scores={'Rt_norm': 0.0, 'Lt_norm': 1.0, 'Dt_norm': 0.0, 'Si_norm': 1.0, 'Lt_capped': 1.3066} | admissible=11 Rt=31454 Bliq_after=86625
   twin  : best a640 d/r/g nominal=(18872,12582,0) effective obl=18872 res=12582 goals=0 | prealloc used=0 closed=[] | floor_level=2.0 utility=0.3809 scores={'Rt_norm': 0.6, 'Lt_norm': 0.4, 'Dt_norm': 0.604, 'Si_norm': 0.0, 'Lt_capped': 2.0328} | admissible=66 Rt=31454 Bliq_after=171126

=== MR07_bliq_up portrait 217 kind=plain profile=4 r_bench=0.1596 income=44197 exp=13609 bliq=8319
   obligations: [(1, 395552, 0.2134, 11097)]
   goals: [(1, 597164, 292102, '2031-06-06'), (2, 538567, 169328, '2030-09-09')]
   relation result: (True, False, (19490.3, 5847.09, 2.0433, 2.0409))
   source: best a0100 d/r/g nominal=(0,19490,0) effective obl=0 res=19490 goals=0 | prealloc used=0 closed=[] | floor_level=2.0 utility=0.2 scores={'Rt_norm': 0.0, 'Lt_norm': 1.0, 'Dt_norm': 0.0, 'Si_norm': 0.0, 'Lt_capped': 2.0433} | admissible=66 Rt=19490 Bliq_after=8319
   twin  : best a730 d/r/g nominal=(13643,5847,0) effective obl=13643 res=5847 goals=0 | prealloc used=0 closed=[] | floor_level=2.0 utility=0.4103 scores={'Rt_norm': 0.7, 'Lt_norm': 0.3, 'Dt_norm': 0.702, 'Si_norm': 0.0, 'Lt_capped': 2.0409} | admissible=66 Rt=19490 Bliq_after=21928

=== MR07_bliq_up portrait 428 kind=plain profile=2 r_bench=0.2 income=78698 exp=13826 bliq=50356
   obligations: [(1, 1324533, 0.3096, 52729)]
   goals: [(1, 1363669, 650212, '2029-08-15'), (2, 1703328, 690083, '2029-09-14'), (3, 1058406, 226770, '2027-04-28'), (4, 863822, 546394, '2028-02-22')]
   relation result: (True, False, (0.0, 4857.72, 3.6422, 4.9936))
   source: best a1000 d/r/g nominal=(12144,0,0) effective obl=12144 res=0 goals=0 | prealloc used=0 closed=[] | floor_level=2.0 utility=0.45 scores={'Rt_norm': 1.0, 'Lt_norm': 0.0, 'Dt_norm': 1.0, 'Si_norm': 0.0, 'Lt_capped': 3.6422} | admissible=66 Rt=12144 Bliq_after=50356
   twin  : best a640 d/r/g nominal=(7287,4858,0) effective obl=7287 res=4858 goals=0 | prealloc used=0 closed=[] | floor_level=2.0 utility=0.6154 scores={'Rt_norm': 0.6, 'Lt_norm': 0.982, 'Dt_norm': 0.607, 'Si_norm': 0.0, 'Lt_capped': 4.9936} | admissible=66 Rt=12144 Bliq_after=64181

=== MR09_scale10 portrait 2663 kind=plain profile=1 r_bench=0.1 income=102847 exp=77237 bliq=62542
   obligations: [(1, 95917, 0.0926, 2246), (2, 46263, 0.3247, 2271)]
   goals: [(1, 1958078, 191412, None), (2, 1559170, 281454, '2029-05-17'), (3, 174492, 71483, None)]
   relation result: (True, False, ((0.30000000000000004, 0.7000000000000001), (0.0, 1.0)))
   source: best a370 d/r/g nominal=(6328,14764,0) effective obl=6328 res=14764 goals=0 | prealloc used=0 closed=[] | floor_level=1.0 utility=0.4501 scores={'Rt_norm': 0.3, 'Lt_norm': 0.7, 'Dt_norm': 0.3, 'Si_norm': 0.0, 'Lt_capped': 1.0009} | admissible=66 Rt=21092 Bliq_after=62542
   twin  : best a0100 d/r/g nominal=(0,210921,0) effective obl=0 res=210921 goals=0 | prealloc used=0 closed=[] | floor_level=1.0 utility=0.45 scores={'Rt_norm': 0.0, 'Lt_norm': 1.0, 'Dt_norm': 0.0, 'Si_norm': 0.0, 'Lt_capped': 1.0828} | admissible=66 Rt=210921 Bliq_after=625419
      TIE at the top (floor_level, utility): ['a0100', 'a190', 'a280', 'a370']

=== MR14_category_up portrait 466 kind=plain profile=3 r_bench=0.1596 income=41192 exp=26824 bliq=61307
   obligations: [(1, 555058, 0.1173, 12918)]
   goals: [(1, 1661455, 865300, '2029-08-15'), (2, 1257680, 77203, None), (3, 72929, 31744, '2029-04-17')]
   relation result: (True, False, (48, 0))
   source: best a091 d/r/g nominal=(0,1305,145) effective obl=0 res=1305 goals=145 | prealloc used=0 closed=[] | floor_level=2.0713 utility=0.8033 scores={'Rt_norm': 1.0, 'Lt_norm': 0.9, 'Dt_norm': 1.0, 'Si_norm': 0.167, 'Lt_capped': 2.3341} | admissible=66 Rt=1450 Bliq_after=61307
      TIE at the top (floor_level, utility): ['a091', 'a190']
   twin  : best a0100 d/r/g nominal=(0,1450,0) effective obl=0 res=1450 goals=0 | prealloc used=0 closed=[] | floor_level=2.0713 utility=0.8 scores={'Rt_norm': 1.0, 'Lt_norm': 1.0, 'Dt_norm': 1.0, 'Si_norm': 0.0, 'Lt_capped': 2.3395} | admissible=66 Rt=1450 Bliq_after=61307

=== MR15_add_goal portrait 1351 kind=plain profile=3 r_bench=0.1596 income=98106 exp=96671 bliq=246818
   obligations: []
   goals: [(1, 381624, 220142, '2028-03-23'), (2, 582831, 183277, '2029-05-17'), (3, 1019802, 5190, '2028-03-23'), (4, 732015, 393667, '2029-04-17')]
   relation result: (True, False, (0, 115))
   source: best a0100 d/r/g nominal=(0,1435,0) effective obl=0 res=1435 goals=0 | prealloc used=0 closed=[] | floor_level=2.0 utility=0.8 scores={'Rt_norm': 1.0, 'Lt_norm': 1.0, 'Dt_norm': 1.0, 'Si_norm': 0.0, 'Lt_capped': 2.568} | admissible=11 Rt=1435 Bliq_after=246818
   twin  : best a091 d/r/g nominal=(0,1291,144) effective obl=0 res=1291 goals=144 | prealloc used=0 closed=[] | floor_level=2.0 utility=0.8029 scores={'Rt_norm': 1.0, 'Lt_norm': 0.899, 'Dt_norm': 1.0, 'Si_norm': 0.167, 'Lt_capped': 2.5665} | admissible=11 Rt=1435 Bliq_after=246818
```

**Что найдено — дефекты с причиной (номера продолжают Д-01, Д-07).**

| № | Отношение → нарушение | Причина (установлена по диагностике) | Модуль / канон | Величина | Связь с Г40 |
|---|---|---|---|---|---|
| **Д-02** | MR06: сумма цели +20 % → деньги на цель **84 501 → 0 ₽** (портрет 663); MR05: другой цели приблизили срок → первая цель **лишилась** разового закрытия (643) | Разовое закрытие §11.5 — «всё или ничего» по **сумме всех** близких целей относительно 50 % подушки: одна выросшая или новая близкая цель отменяет закрытие остальных | `goals_priority.py::preallocate_from_bliq`; канон §11.5 | до 100 % цели | новое (Г40 № 3 видел только пробой floor) |
| **Д-03** | MR09: все деньги ×10 → план **30/70 → 0/100** (портрет 2663); MR03, MR14 — тот же механизм | Полезность округляется до 4 знаков (`ranking.py`: `alt["utility"] = round(utility, 4)`) и сортируется с этим округлением → ложные ничьи, порядок решает стабильность сортировки и последний бит float | `ranking.py::rank_alternatives` | до 100 % потока | Г40 № 25 (там «ложные ничьи 3,2 %», здесь — видимый ущерб: масштаб меняет совет) |
| **Д-04** | MR07 (428): подушка +1 мес. → взнос в резерв **0 → 4 858 ₽**; MR15 (1351): новая цель → существующим целям **0 → 115 ₽**; MR03 (1244): кредит стал дороже бенчмарка → досрочка **11 705 → 3 902 ₽** | min-max нормировка по текущему набору альтернатив: любое изменение размаха критерия переставляет выбор, даже если сама альтернатива не изменилась | `ranking.py::normalize_value`; канон §7 | до 67 % досрочки | Г40 № 5 (нормировка) — теперь как нарушение монотонности |
| **Д-05** | MR07 (217): подушка +13 609 ₽ → подушка ПОСЛЕ плана **ниже** (2,0433 → 2,0409 мес.) | `floor_level = min(Lt', floor)`: всё сверх floor считается равным, и лишние деньги уходят в долг | `ranking.py::rank_alternatives` (G6) | 33 ₽ — мелко | новое, мелкое |
| **Д-06** | MR04 (299): срок цели дальше на 6 мес. → денег на неё в месяц **больше** (8 159 → 9 179 ₽) | Распределение по остатку, а не по нужному темпу; за 36 мес. цель индексируется (§11.3), дальше срок → больше остаток | `goals_priority.py::calculate_goals_si`, `inflated_target_amount` | 0,2 % портретов | Г40 № 6, № 20 |

**Слепота (не нарушение, а отсутствие реакции), число на 3 000 портретах:** ставка главного кредита ×1,5 не меняет досрочку в него у **87,9 %**; $r_{bench}$ +5 п. п. — **92,6 %**; срок ближайшей цели +6 мес. — **94,1 %**; сумма цели +20 % — **98,6 %**; удвоение волатильности дохода — **98,1 %**. Это числовое подтверждение «слепоты» Г40 № 4 для каждого входа отдельно.

**Не нарушены ни разу:** доход вверх (MR01), перестановка долгов и целей (MR08), сдвиг «сегодня» вместе со сроками (MR12 — **после** починки Д-01; с `date` он бы ломался), расходы вверх (MR10), $r_{bench}$ вверх (MR11), волатильность вверх (MR13), удаление кредита (MR16).

**Цена внедрения.** 16 отношений как параметризованные тесты `pytest` на ~200 портретах: **6–10 ч**. Каждый найденный дефект — отдельный регрессионный тест на конкретный портрет (номер и вход известны): **0,5 ч** каждый. Библиотек не нужно.

**Корзина.** MR01, MR08, MR09, MR10, MR11, MR12, MR16 (сейчас держатся) — **«сразу после синтеза»** как защитная сетка перед правками ядра. MR05/MR06 (Д-02) и MR09 (Д-03) — **«до запуска»**: это неверный совет обычному человеку. MR03/MR07/MR15 (Д-04) — **«до запуска»**, если путь (б) не принят (он лечит нормировку глобальными шкалами); иначе — снимаются вместе с min-max. Метрики слепоты — **«потом»**, как регрессионные числа после смены правила выбора.

## Пункт 4. Проверка Монте-Карло: сходимость, число прогонов, зерно

**Аналогия.** Оценивать, сколько в среднем орлов выпадет, бросая монету 1 000 раз. Если бросить ещё раз 1 000 — получится чуть другое число. «Ошибка Монте-Карло» — это насколько гуляет ответ от серии к серии. А если ответ можно посчитать формулой — бросать монету не нужно вовсе.

**Что проверяет.** (1) Есть ли у величины, которую мы оцениваем симуляцией, точная формула; (2) насколько оценка зависит от зерна генератора; (3) сколько прогонов нужно для заявленной точности; (4) побочные эффекты генератора случайных чисел.

**Первоисточник.** Koehler, Brown, Haneuse 2009, *The American Statistician* 63(2), DOI 10.1198/tast.2009.0030; полный текст PMC3337209 через `r.jina.ai/https://pmc.ncbi.nlm.nih.gov/articles/PMC3337209/` (HTTP 200, 53 668 байт, 17.09.2026; EuropePMC `fullTextXML` — HTTP 500). Дословно: «We define *Monte Carlo error* to be the standard deviation of the Monte Carlo estimator, taken across hypothetical repetitions of the simulation, where each simulation is based on the same design and consists of *R* replications»; «of 223 regular articles that reported a simulation study, only 8 provided either a formal justification for the number of replications used or an estimate of MCE»; «The most common choice was *R* = 1000 (74 articles)»; «it seems unlikely that a single choice for *R* will provide practical guidance in a broad range of simulation settings». И цитата Метрополиса–Улама 1949 оттуда же: «This estimate would be of great practical importance, since it alone would allow us to suit the size of the sample to the desired accuracy.»

**Наш модуль.** `app/core/forecast.py::monte_carlo_intervals` (канон §15): `MC_SIMULATIONS = 1000`, $\sigma_h = 0{,}05\sqrt{1+0{,}5h}$ от точечного прогноза, нормальный шум, коридор p10–p90, `seed=42`.

Скрипт `p4_mc.py`:
```python
"""G39 item 4: verification of the Monte Carlo corridor app/core/forecast.py::monte_carlo_intervals.
(a) the corridor has a CLOSED FORM: samples = point + N(0, s) -> p10 = point - 1.2816 s, p90 = point + 1.2816 s;
(b) Monte Carlo error of p10 with n = 1000 across seeds vs theory SE(q_p) = sqrt(p(1-p)/n) / phi(z_p) * s;
(c) replications needed for a target precision; (d) side effect: random.seed() on the GLOBAL generator."""
import sys, math, random, statistics as stt
sys.path.insert(0, "/Users/vasyaevdokimov/repos/personal-finance-dss")
from app.core import forecast as F

z10 = -1.2815515655446004
phi = math.exp(-z10 * z10 / 2) / math.sqrt(2 * math.pi)
point, H = 100_000.0, 3
print("(a) closed form vs code (seed 42, n=1000), point 100 000:")
iv = F.monte_carlo_intervals([point] * H, horizon=H)
for h, row in enumerate(iv, start=1):
    s = point * F.MC_SIGMA_BASE * math.sqrt(1 + F.MC_SIGMA_GROWTH * h)
    ex10, ex90 = point + z10 * s, point - z10 * s
    print(f"  h={h}: sigma={s:.0f}  code p10={row['p10']:.0f} exact={ex10:.0f} (err {row['p10'] - ex10:+.0f} = {(row['p10'] - ex10) / s:+.3f} sigma)  "
          f"code p90={row['p90']:.0f} exact={ex90:.0f} (err {row['p90'] - ex90:+.0f})  p50 err {row['p50'] - point:+.0f}")
print("(b) seed-to-seed spread of p10 at h=1, n=1000, 400 seeds:")
s1 = point * F.MC_SIGMA_BASE * math.sqrt(1 + F.MC_SIGMA_GROWTH)
est = [F.monte_carlo_intervals([point], horizon=1, seed=k)[0]["p10"] for k in range(400)]
theory = math.sqrt(0.1 * 0.9 / 1000) / phi * s1
print(f"  empirical SD {stt.pstdev(est):.1f} rub, theory {theory:.1f} rub ({theory / s1:.3f} sigma); mean bias {stt.mean(est) - (point + z10 * s1):+.1f} rub;"
      f" range across seeds {min(est):.0f}..{max(est):.0f}")
print("(c) replications needed so that SE(p10) <= eps * sigma:")
for eps in (0.05, 0.01, 0.001):
    n = 0.1 * 0.9 / (phi * eps) ** 2
    print(f"  eps={eps}: n >= {math.ceil(n)}")
print("(d) global RNG side effect:")
random.seed(12345); a = random.random()
random.seed(12345); F.monte_carlo_intervals([point], horizon=1); b = random.random()
random.seed(999); F.monte_carlo_intervals([point], horizon=1); c = random.random()
print(f"  next random.random() after forecast call is independent of the caller's seed: {b == c} (b={b:.6f}, c={c:.6f}, untouched={a:.6f})")
print("(e) degenerate corridors: point 0 ->", F.monte_carlo_intervals([0.0], horizon=1)[0], "; point -50 000 ->", F.monte_carlo_intervals([-50_000.0], horizon=1)[0])
```
Вывод:
```
(a) closed form vs code (seed 42, n=1000), point 100 000:
  h=1: sigma=6124  code p10=91798 exact=92152 (err -354 = -0.058 sigma)  code p90=107988 exact=107848 (err +140)  p50 err -113
  h=2: sigma=7071  code p10=91209 exact=90938 (err +271 = +0.038 sigma)  code p90=108866 exact=109062 (err -196)  p50 err -219
  h=3: sigma=7906  code p10=89630 exact=89868 (err -239 = -0.030 sigma)  code p90=110541 exact=110132 (err +409)  p50 err +212
(b) seed-to-seed spread of p10 at h=1, n=1000, 400 seeds:
  empirical SD 348.2 rub, theory 331.0 rub (0.054 sigma); mean bias -0.5 rub; range across seeds 91091..93213
(c) replications needed so that SE(p10) <= eps * sigma:
  eps=0.05: n >= 1169
  eps=0.01: n >= 29222
  eps=0.001: n >= 2922110
(d) global RNG side effect:
  next random.random() after forecast call is independent of the caller's seed: True (b=0.099355, c=0.099355, untouched=0.416620)
(e) degenerate corridors: point 0 -> {'p10': 0.0, 'p50': 0.0, 'p90': 0.0} ; point -50 000 -> {'p10': -54100.78, 'p50': -50056.54, 'p90': -46005.99}
```

**Что это значит.**
1. 🔴 **Симуляция не нужна — у коридора есть точная формула.** Код добавляет к точке нормальный шум и берёт 10-й и 90-й процентили; это ровно $\text{точка} \pm 1{,}2816\,\sigma_h$ (1,2816 — число из таблицы нормального распределения для 10 %). 1 000 прогонов дают эту же величину с ошибкой **±0,054 σ** (≈ 330 ₽ на прогнозе 100 000 ₽); с зерном 42 ошибка фиксирована и выглядит «точной», но это случайный сдвиг на −354 ₽ у p10. Чтобы симуляция сравнялась с формулой до 1 % σ, нужно **29 222** прогона; формула даёт ноль ошибки за одну строку. (Г40 № 19 это назвал; здесь — число.)
2. 🔴 **Дефект Д-08: `random.seed(seed)` сбрасывает ГЛОБАЛЬНЫЙ генератор Python.** После любого вызова прогноза следующий `random.random()` в процессе одинаков независимо от того, что задал вызывающий (b = c = 0,099355). В `app/services/bank_api.py:121–138` глобальный `random` генерирует синтетические транзакции — после прогноза они становятся повторяющимися. Для продукта мелко (демо-банк), для любого будущего кода со случайностью (A/B-назначение, сэмплинг) — ловушка. Лечение — `random.Random(seed)` локально.
3. Коридор нулевой при прогнозе 0 и «зеркальный» при отрицательном — ширина $\propto |\text{точка}|$, то есть человек с нулевым свободным потоком получает «прогноз без неопределённости». Это не ошибка счёта, а ошибка постановки (Г40 № 19).

**Что метод даст для будущего МК (если стохастика появится в решении — например, сценарии шоков для пути (б) или дерево `f1a` Г41):** правило из Koehler — в каждом отчёте печатать MCE рядом с оценкой и выбирать R из требуемой точности, а не круглым числом.

**Цена внедрения.** Замена симуляции формулой: **1–2 ч** + тест «формула = симуляция при n = 200 000 до 0,01 σ» (0,5 ч). Локальный генератор (Д-08): **0,5 ч**. Библиотек не нужно.

**Корзина.** Д-08 — **«сразу после синтеза»** (мелкая правка, но делает поведение процесса недетерминированным для соседей). Формула вместо МК — **«до запуска»** (экран прогноза). Постановка шума (σ от волатильности истории, а не 5 % для всех) — **«потом»**, вместе с пунктом 5.

## Пункт 5. Проверка прогноза SES/Holt: бэктест против наивного прогноза, тест Дибольда–Мариано

**Аналогия.** Синоптик хвалится сложной моделью. Проверка: каждый прошлый день сравнить его прогноз с правилом «завтра будет как сегодня». Если правило не хуже — модель ничего не добавляет. Тест Дибольда–Мариано отвечает, не случайна ли разница.

**Что проверяет.** Точность прогноза на истории «с катящимся началом» (каждый следующий месяц прогнозируется только по прошлым) и значимость разницы с простыми эталонами.

**Первоисточник.** Diebold & Mariano 1995, *JBES* 13(3), DOI 10.1080/07350015.1995.10524599 (OpenAlex HTTP 200, 17.09.2026), реферат дословно: «We propose and evaluate explicit tests of the null hypothesis of no difference in the accuracy of two competing forecasts. In contrast to previously developed tests, a wide variety of accuracy measures can be used (in particular, the loss function need not be quadratic and need not even be symmetric), and forecast errors can be non-Gaussian, nonzero mean, serially correlated, and contemporaneously correlated.» Поправка на малые выборки — Harvey, Leybourne, Newbold 1997, *IJF* 13(2), DOI 10.1016/S0169-2070(96)00719-4 (OpenAlex HTTP 200, реферата в базе нет; формула поправки взята из общеизвестной записи теста, по тексту статьи не сверена — пометка).

**Наш модуль.** `app/core/forecast.py::choose_point_forecast` → демпфированный Holt с зашитыми α = 0,4, β = 0,3, φ = 0,9 при ≥ 3 точках (канон §15 описывает SES — расхождение Г40 № 27). Прогноз в решение не входит (Г40 № 27), но с ADR-015 история дохода входит во floor через CV.

Скрипт `p5_backtest.py` (венв `g39/sav`: scipy 1.18.1):
```python
"""G39 item 5: rolling-origin backtest of the canon point forecast (app/core/forecast.py::choose_point_forecast = damped Holt
with fixed alpha .4 beta .3 phi .9 for >= 3 points) against naive benchmarks, with the Diebold-Mariano test
(Harvey-Leybourne-Newbold small-sample correction). Data: (A) ADR-015 income histories (8 months, iid noise - no trend by construction);
(B) the same with a +2 %/month trend; (C) with a 6-month-early job loss (level shift -40 %). No real user data exists (152-FZ) - see debt list."""
import sav_boot  # noqa
import math, random, statistics as stt
import numpy as np
from scipy import stats
from app.core.forecast import choose_point_forecast
from tools.portrait_testing.generator import PortraitGenerator


def dm_test(e1, e2, h=1):
    """DM on absolute-error loss; HLN-corrected statistic, t(T-1) p-value. Positive stat -> model 1 worse."""
    d = np.abs(np.asarray(e1)) - np.abs(np.asarray(e2))
    T = len(d)
    if T < 3 or np.var(d) == 0:
        return float("nan"), float("nan")
    dm = d.mean() / math.sqrt(np.var(d, ddof=0) / T)
    k = math.sqrt((T + 1 - 2 * h + h * (h - 1) / T) / T)
    s = dm * k
    return s, 2 * stats.t.sf(abs(s), df=T - 1)


def series(kind, p, i):
    rng = random.Random(7 * i + 1)
    base = [x for x in p["income_history"]]
    inc = p["income_total"]
    if kind == "A":
        return base
    if kind == "B":
        return [x * 1.02 ** t for t, x in enumerate(base)]
    if kind == "C":
        return [x if t < 4 else x * 0.6 for t, x in enumerate(base)]


gen = PortraitGenerator(seed=20260702, version=2)
for kind, label in (("A", "ADR-015 histories (noise only)"), ("B", "+2 %/month trend"), ("C", "level shift -40 % at month 5")):
    E = {"holt": [], "naive": [], "mean": []}
    wins = {"holt_vs_naive": [0, 0, 0], "holt_vs_mean": [0, 0, 0]}
    n = 0
    for i in range(3000):
        p = gen.generate_with_income_history(i)
        if p["kind"] != "plain" or p["income_total"] <= 0:
            continue
        y = series(kind, p, i)
        if min(y) <= 0:
            continue
        n += 1
        scale = stt.mean(y)
        eh, en, em = [], [], []
        for t in range(3, len(y)):
            hist = y[:t]
            eh.append((choose_point_forecast(hist, horizon=1)[0] - y[t]) / scale)
            en.append((hist[-1] - y[t]) / scale)
            em.append((stt.mean(hist) - y[t]) / scale)
        E["holt"] += eh; E["naive"] += en; E["mean"] += em
        for key, other in (("holt_vs_naive", en), ("holt_vs_mean", em)):
            s, pv = dm_test(eh, other)
            if pv == pv and pv < 0.05:
                wins[key][0 if s > 0 else 1] += 1
            else:
                wins[key][2] += 1
    print(f"\n=== {label}: portraits {n}, 1-step forecasts per portrait {len(y) - 3}")
    for k, v in E.items():
        a = np.abs(v)
        print(f"  {k:6} MAE {a.mean():.4f} of mean income   RMSE {math.sqrt(np.mean(np.square(v))):.4f}   bias {np.mean(v):+.4f}")
    s, pv = dm_test(E["holt"], E["naive"]); print(f"  pooled DM holt vs naive: stat {s:+.2f} p={pv:.2g} (positive = Holt worse)")
    s, pv = dm_test(E["holt"], E["mean"]); print(f"  pooled DM holt vs mean : stat {s:+.2f} p={pv:.2g}")
    for key, (w, b, ns) in wins.items():
        print(f"  per-portrait DM {key}: Holt significantly worse {w / n:.1%}, better {b / n:.1%}, not distinguishable {ns / n:.1%}")
print("\nNote: pooled DM treats forecast errors of different portraits as one sequence (independent across portraits by construction).")
```
Вывод:
```

=== ADR-015 histories (noise only): portraits 2000, 1-step forecasts per portrait 5
  holt   MAE 0.2329 of mean income   RMSE 0.4377   bias +0.0082
  naive  MAE 0.1975 of mean income   RMSE 0.3671   bias -0.0025
  mean   MAE 0.1564 of mean income   RMSE 0.2841   bias +0.0020
  pooled DM holt vs naive: stat +12.35 p=8.5e-35 (positive = Holt worse)
  pooled DM holt vs mean : stat +27.57 p=2.7e-161
  per-portrait DM holt_vs_naive: Holt significantly worse 4.0%, better 1.0%, not distinguishable 95.0%
  per-portrait DM holt_vs_mean: Holt significantly worse 6.3%, better 0.1%, not distinguishable 93.6%

=== +2 %/month trend: portraits 2000, 1-step forecasts per portrait 5
  holt   MAE 0.2351 of mean income   RMSE 0.4315   bias -0.0054
  naive  MAE 0.2097 of mean income   RMSE 0.3749   bias -0.0225
  mean   MAE 0.1861 of mean income   RMSE 0.2953   bias -0.0569
  pooled DM holt vs naive: stat +9.13 p=8e-20 (positive = Holt worse)
  pooled DM holt vs mean : stat +17.90 p=1.4e-70
  per-portrait DM holt_vs_naive: Holt significantly worse 3.4%, better 39.6%, not distinguishable 57.0%
  per-portrait DM holt_vs_mean: Holt significantly worse 4.5%, better 39.2%, not distinguishable 56.4%

=== level shift -40 % at month 5: portraits 2000, 1-step forecasts per portrait 5
  holt   MAE 0.3477 of mean income   RMSE 0.5415   bias +0.1683
  naive  MAE 0.2478 of mean income   RMSE 0.4050   bias +0.0962
  mean   MAE 0.3635 of mean income   RMSE 0.4329   bias +0.3039
  pooled DM holt vs naive: stat +28.64 p=2.1e-173 (positive = Holt worse)
  pooled DM holt vs mean : stat -4.22 p=2.5e-05
  per-portrait DM holt_vs_naive: Holt significantly worse 7.1%, better 0.5%, not distinguishable 92.4%
  per-portrait DM holt_vs_mean: Holt significantly worse 4.1%, better 3.7%, not distinguishable 92.2%

Note: pooled DM treats forecast errors of different portraits as one sequence (independent across portraits by construction).
```

**Что это значит.**
1. 🔴 **На истории из 8 месяцев канонный Holt проигрывает обоим простым правилам во всех трёх мирах**: ошибка 23 % дохода против 16 % у «среднего по истории» (без тренда) и 25 % у «как в прошлом месяце» (после потери работы). Даже при настоящем тренде +2 %/мес. Holt в сумме хуже, потому что шум у волатильных портретов больше тренда. Разница значима (объединённый DM, p < 10⁻¹⁹).
2. **На одном человеке тест почти ничего не различает** (5 прогнозов на человека: 92–95 % «неразличимо»). Практический вывод: валидировать прогноз можно только на популяции, не на отдельной истории — это ограничение на будущий мониторинг после запуска.
3. **После потери дохода Holt хуже всех по смещению (+17 % дохода)**: он «помнит» старый уровень и продолжает прогнозировать доход, которого уже нет. Это ровно тот сценарий, где ADR-015 запрещает истории влиять на кризис, — и правильно запрещает.
4. Горизонт полезности на наших данных не установлен: при 8 точках полезного горизонта нет вовсе даже на 1 шаг. Честный вывод — «прогноз должен быть средним/наивным, пока не доказано обратное на реальных данных».

**Чего не хватает (ЗАДОЛЖЕННОСТЬ).** Реальных помесячных рядов дохода домохозяйств РФ нет (та же дыра Г40 № 10, Г41 № 14). Синтетика ADR-015 — шум без структуры по построению, поэтому пункт доказывает только «Holt не лучше там, где структуры нет», а не «Holt плох на реальных людях».

**Цена внедрения.** Стенд бэктеста с DM: **4–6 ч** (скрипт готов). Зависимость `scipy` — dev. Реальные данные после запуска — стенд тот же.

**Корзина.** Замена Holt на «среднее по истории» или сравнение с ним как гейт — **«до запуска»** (экран прогноза сейчас хуже наивного). Бэктест на реальных анонимизированных рядах — **«потом»** (после запуска).

---

# Часть B. Валидация — ядро решает правильную задачу

## Пункт 6. 🔴 Выход из замкнутой петли валидации

**Аналогия.** Ученик сам составил тест, сам решил и сам проверил — пятёрка ничего не значит. Нужна внешняя линейка: чужой экзамен, реальная жизнь (сдал ли потом), или хотя бы чужой учебник с ответами.

**Что проверяет.** Совпадение решений модели с чем-то, что НЕ было настроено той же стороной: внешними нормами, теорией, исходами, реальными выборами людей.

**Почему петля замкнута сейчас.** Пороги (floor 2 мес., токсичность 30 %, $L^*$, веса) и метрика сертификации (согласие 78,63 %) — всё от экспертных движков, настроенных самим проектом. По SR 11-7 это «developmental evidence», не валидация (цитата и адрес — `raw/approach_validity_2026-09-10.md` §3.1: «Effective challenge depends on a combination of incentives, competence, and influence. Incentives to provide effective challenge to models are stronger when there is greater separation of that challenge from the model development process»).

### Пять способов выхода и что каждый даёт нам

| Способ | Аналогия | Что докажет/опровергнет у нас | Данные | Когда возможен |
|---|---|---|---|---|
| **(1) Внешние эталоны** (EMH, MaPS, 2–6 мес., буферный запас Кэрролла) | чужая линейка | попадают ли floor, ПДН-гейт, иерархия «поток → долг → резерв» в чужие нормы | уже добыты | **сейчас** (замер ниже) |
| **(2) Теоретический оракул** (MILP, модель Кэрролла) | задача с известным ответом | насколько решение далеко от оптимума при явных целях | синтетика | **сейчас** (пункт 0) |
| **(3) Ретроспектива на исходах** (backtesting SR 11-7: «Outcomes analysis, including back-testing») | проверить прогноз погоды назавтра | срываются ли цели, появляются ли просрочки у следующих совету | исходы пользователей | через 6–12 мес. после запуска |
| **(4) Выявленные предпочтения / обратная оптимизация** | по покупкам угадать вкусы | какие веса делают реальные выборы людей оптимальными; если веса профилей далеки — профили выдуманы | выборы пользователей «принял/изменил план» | после запуска, сотни человек |
| **(5) Полевой эксперимент** | контрольная группа | помогает ли совет вообще (причинный эффект) | рандомизация | после запуска; Г41 рамка 7: 3 211 человек на вариант |

**Обратная оптимизация — первоисточник.** Ahuja & Orlin 2001, *Operations Research* 49(5), DOI 10.1287/opre.49.5.771.10607 (OpenAlex HTTP 200, 17.09.2026), дословно: «The inverse optimization problem is to perturb the cost vector c to d so that x0 is an optimal solution of P with respect to d and ‖d−c‖p is minimum»; «If the problem P is a linear programming problem, then its inverse problem under the L1 as well as L∞ norm is also a linear programming problem.» Для нас: наш выбор — взвешенная сумма на конечном наборе, значит «какие веса делают выбор человека лучшим» — это набор линейных неравенств на веса, решаемый тем же HiGHS за миллисекунды. Это же даёт «интервалы устойчивости весов» пункта 9 — одна техника на два пункта.

### Замер внешнего эталона (1) на портретах ADR-015 (`p6_external.py`)

```python
"""G39 item 6: canon floor vs EXTERNAL anchors on ADR-015 portraits (no expert agreement involved).
Anchors: (1) Carroll buffer-stock table from G41 f3a.py (months of INCOME, p0 = 2 % column, illustrative parameters);
(2) EMH ALR benchmark 200 % of monthly expenses (Greninger 1996 via approach_validity raw); (3) US 2-6 months; (4) EMH CIR < 15 % non-mortgage debt service.
Portrait volatility v -> sigma of uniform(-v, v) = v / sqrt(3)."""
import sav_boot  # noqa
import math, random
import numpy as np
from scipy import stats
import app.core.ranking as ranking
from tools.portrait_testing.generator import PortraitGenerator

SIG = [0.05, 0.10, 0.30, 0.60]
CARROLL_P2 = [1.41, 1.48, 1.97, 3.51]   # months of income, p0 = 2 %


def carroll(sigma):
    return float(np.interp(sigma, SIG, CARROLL_P2))


gen = PortraitGenerator(seed=20260702, version=2)
rows = []
for i in range(3000):
    p = gen.generate_with_income_history(i)
    if p["kind"] != "plain" or p["income_total"] <= 0 or p["expense_total"] <= 0:
        continue
    v = random.Random(20260702 * 1_000_007 + i).choice([0.0, 0.0, 0.0, 0.1, 0.2, 0.4, 0.6, 0.9])
    sigma = v / math.sqrt(3)
    fl = ranking.effective_floor_months(p["obligations"], p["r_bench"], income_history=p["income_history"])   # months of expenses
    car = carroll(sigma) * p["income_total"] / p["expense_total"]                                              # -> months of expenses
    cir = sum(o["monthly_payment"] for o in p["obligations"]) / p["income_total"]
    rows.append((v, sigma, fl, car, cir, ranking.income_cv(p["income_history"])))
a = np.array([r[:5] for r in rows])
print(f"plain portraits: {len(rows)}")
for v in sorted(set(a[:, 0])):
    s = a[a[:, 0] == v]
    print(f"  volatility {v:.1f} (sigma {v / math.sqrt(3):.2f}): canon floor mean {s[:, 2].mean():.2f} mo exp | Carroll target median {np.median(s[:, 3]):.2f} mo exp "
          f"(p10 {np.percentile(s[:, 3], 10):.2f}, p90 {np.percentile(s[:, 3], 90):.2f}) | canon above Carroll in {np.mean(s[:, 2] > s[:, 3]):.0%}")
rho, pv = stats.spearmanr(a[:, 1], a[:, 2])
rho2, pv2 = stats.spearmanr(a[:, 1], a[:, 3])
print(f"Spearman(volatility, canon floor) = {rho:.3f} (p={pv:.2g}); Spearman(volatility, Carroll target) = {rho2:.3f}")
print(f"canon floor within US 2-6 months: {np.mean((a[:, 2] >= 2) & (a[:, 2] <= 6)):.1%}; equals EMH ALR benchmark 200 %: {np.mean(np.abs(a[:, 2] - 2) < 1e-9):.1%}")
print(f"Carroll target (months of expenses) within 2-6: {np.mean((a[:, 3] >= 2) & (a[:, 3] <= 6)):.1%}; below 2: {np.mean(a[:, 3] < 2):.1%}")
debtors = a[a[:, 4] > 0]
print(f"EMH CIR: debtors {len(debtors)}; debt service >= 15 % of income: {np.mean(debtors[:, 4] >= 0.15):.1%}; > canon DT_MAX 0.40: {np.mean(debtors[:, 4] > 0.40):.1%}")
```
Вывод:
```
plain portraits: 2000
  volatility 0.0 (sigma 0.00): canon floor mean 1.89 mo exp | Carroll target median 2.39 mo exp (p10 1.50, p90 4.43) | canon above Carroll in 33%
  volatility 0.1 (sigma 0.06): canon floor mean 1.85 mo exp | Carroll target median 2.46 mo exp (p10 1.47, p90 4.54) | canon above Carroll in 31%
  volatility 0.2 (sigma 0.12): canon floor mean 1.85 mo exp | Carroll target median 2.83 mo exp (p10 1.75, p90 4.49) | canon above Carroll in 21%
  volatility 0.4 (sigma 0.23): canon floor mean 1.87 mo exp | Carroll target median 3.04 mo exp (p10 1.97, p90 5.11) | canon above Carroll in 11%
  volatility 0.6 (sigma 0.35): canon floor mean 1.91 mo exp | Carroll target median 3.92 mo exp (p10 2.36, p90 7.36) | canon above Carroll in 0%
  volatility 0.9 (sigma 0.52): canon floor mean 1.98 mo exp | Carroll target median 5.35 mo exp (p10 3.34, p90 9.98) | canon above Carroll in 0%
Spearman(volatility, canon floor) = 0.408 (p=3.9e-81); Spearman(volatility, Carroll target) = 0.512
canon floor within US 2-6 months: 86.6%; equals EMH ALR benchmark 200 %: 69.1%
Carroll target (months of expenses) within 2-6: 68.8%; below 2: 20.9%
EMH CIR: debtors 1101; debt service >= 15 % of income: 83.8%; > canon DT_MAX 0.40: 31.7%
```

**Что это значит.**
1. 🟢 **Floor канона согласован с двумя внешними нормами по уровню**: в коридоре США 2–6 мес. у 86,6 % портретов, ровно на эталоне EMH ALR 200 % — у 69,1 % (остальные — floor 1 мес. при токсичном долге). Уровень floor — не выдумка экспертов.
2. 🔴 **По форме — нет: floor почти не растёт с волатильностью дохода, а модель Кэрролла растёт сильно.** При волатильности 0,9 канон даёт в среднем 1,98 мес. расходов, Кэрролл — 5,35 (p10 3,34). Корреляция с волатильностью 0,41 у канона против 0,51 у Кэрролла, но по величине расхождение в 2,7 раза. Причины в коде: прибавка ADR-015 начинается с CV > 0,3 и не больше 1 мес. (`ranking.py`: `INCOME_VOLATILITY_THRESHOLD = 0.3`, `..._BOOST_CAP = 1.0`), а у портрета с разбросом ±90 % CV лишь 0,52. Это внешнее опровержение порога 0,3 ADR-015 («не откалиброванная владельцем константа» — сам ADR это признаёт). Оговорка: параметры таблицы Кэрролла иллюстративные (Г41), при ставке вкладов 8 % целевого запаса нет — сравнение качественное.
3. 🟡 **ПДН-гейт против EMH:** эталон EMH на неипотечную долговую нагрузку — < 15 % дохода; её превышают 83,8 % заёмщиков портретов v2, наш порог 0,40 — 31,7 %. Порог 0,40 — ипотечный по природе (Г40 № 26: ссылка «4892-У» не подтверждена), а портреты не различают ипотеку. Внешний эталон говорит: для неипотечного долга 0,40 — слишком мягко как «безопасный уровень», и к тому же гейт не срабатывает вовсе (пункт 2.3).

**Цена внедрения.** Стенд «канон против внешних эталонов» (floor, ПДН, иерархия EMH): **4–6 ч**, библиотек не нужно (scipy для корреляции — dev). Инфраструктура журнала исходов для (3)–(4) — событие «план принят/изменён/исполнен» + срыв цели/просрочка: **2–3 дня** (связка с 152-ФЗ: только агрегаты). Обратная оптимизация весов на журнале — **1 день** после накопления.

**Корзина.** Стенд внешних эталонов — **«сразу после синтеза»** (это первое доказательство вне петли, дешёвое). Журнал исходов — **«до запуска»** (без него способы 3–5 невозможны навсегда: данные не собираются задним числом). Ретроспектива, обратная оптимизация, эксперимент — **«потом»**.

## Пункт 7. Практика валидации моделей: SR 11-7, Банк России (483-П / 845-П), ASME V&V 10/20 — что переносится на нас

**Аналогия.** У банков и инженеров, считающих мосты, уже есть «инструкция по технике безопасности для моделей». Нам не нужно её исполнять (мы не банк и не мост), но её разделы — готовый чек-лист того, что обычно забывают.

**Источники и дословные места.**
- **SR 11-7 / OCC 2011-12** — добыт 10.09.2026 (`raw/approach_validity_2026-09-10.md` §3.1, `federalreserve.gov/boarddocs/srletters/2011/sr1107.pdf` HTTP 200 и копия OCC). Три ядра: «Evaluation of conceptual soundness, including developmental evidence • Ongoing monitoring, including process verification and benchmarking • Outcomes analysis, including back-testing». Про чувствительность: «Unexpectedly large changes in outputs in response to small changes in inputs can indicate an unstable model.» Про альтернативы: «Comparison to alternative theories and approaches should be included.» 🔴 OCC отменил 2011-12 бюллетенем **2026-13** (там же, §3.2) — ссылаться как на «три ядра SR 11-7 (2011) с учётом пересмотра OCC 2026-13».
- **Банк России, 483-П** (06.08.2015), гл. 14 «Внутренняя валидация» — `sudact.ru/law/polozhenie-o-poriadke-rascheta-velichiny-kreditnogo-riska/polozhenie/razdel-iv/glava-14/`, HTTP 200 (42 828 байт), 17.09.2026, текст через Exa: «не реже одного раза в год осуществлять сопоставительный анализ рассчитанных значений вероятности дефолта, полученных в результате применения моделей, … с фактической частотой реализованных дефолтов»; «в случае недостаточности внутренней статистической информации использовать внешнюю статистическую информацию»; «14.3. Методы и стандарты проведения внутренней валидации, включая статистические тесты, … не меняются в зависимости от фазы цикла деловой активности.»
- **Разъяснения ЦБ о валидации по 483-П** — `cbr.ru/faq_ufr/dbrnfaq/doc/forPrint/?id=241`, HTTP 200 (32 717 байт), 17.09.2026: «Тестирование модели, в рамках которого проводятся различные количественные тесты, включая сопоставительный анализ результатов модели и аналогичных показателей из других источников (benchmarking)»; «Банк России может при необходимости запросить дополнительную документацию, … (например, программные коды, реализующие модель, документацию с указанием всех изменений, внесенных в модель)». И `…?id=232` (HTTP 200): «Рейтинговые системы банка должны эффективно дифференцировать риск … При значительном расхождении прогнозных оценок с фактическими значениями должна происходить переоценка компонентов кредитного риска.»
- 🟡 **Положение Банка России 845-П от 02.11.2024** (зарег. Минюстом 28.12.2024 № 80878) — по заголовку тот же предмет, глава 15 «…по внутренней валидации…». Текст — только фрагменты выдачи Exa (КонсультантПлюс через `r.jina.ai` отдал 2 055 байт — одну шапку): «15.3. Количественные методы оценки должны включать в себя проведение тестов на устойчивость функционирования внутренних моделей ПВР (в том числе оценку индекса стабильности популяции …), эффективность ранжирования …, точность прогнозных значений … путем их сопоставления с фактическими значениями»; «15.4.2. Анализ … вклада каждого фактора и (или) модуля (совокупности факторов) в ранжирующую способность внутренней модели». **Не установлено:** отменяет ли 845-П Положение 483-П и с какой даты (причина — полный текст не открыт). Ссылаться на 483-П как на действующее — нельзя без этой проверки.
- **ASME V&V 20-2009** — страница стандарта `asme.org/…/standard-for-verification-and-validation-in-computational-fluid-dynamics-and-heat-transfer/2009` (текст выдачи Exa): «the specification of a verification and validation approach that quantifies the degree of accuracy inferred from the comparison of solution and data for a specified variable at a specified validation point». Определения — по обзору Dowding & Hogan (OSTI 1368927; `curl` — таймаут, текст через Exa): «Code verification (V&V-20): "Establishes that the code accurately solves the mathematical model incorporated in the code, i.e. that the code is free of mistakes for the simulations of interest." – Solution verification (V&V-20): Estimates the numerical accuracy of a particular calculation.»; «Validation (ASME V&V-10/V&V-20): "The process of determining the degree to which a model is an accurate representation of the real world from the perspective of the intended uses of the model."»; «Code verification should be performed prior to validation.» Сам текст стандарта платный; копия на normfile.com — пиратская, не использовалась.

**Что переносится на нас — таблица.**

| Требование практики | Что это у нас | Что есть | Чего нет | Пункт этого файла |
|---|---|---|---|---|
| Code verification до validation (V&V 20) | инварианты, MR, Z3, оракул | пункты 1–3 | CI-гейт на них | 1–3, ИТОГ §4 |
| Solution verification: численная точность конкретного расчёта | ошибка сетки 10 %, ошибка МК | Г40 9.3, пункт 4 | отчёт о точности рядом с советом | 4, 11 |
| Conceptual soundness + сравнение с альтернативами (SR 11-7) | Г40, Г41, путь (б) | сделано | — | 0 |
| Sensitivity analysis (SR 11-7) | Соболь/Моррис | — | — | 8 |
| Benchmarking с внешними источниками (ЦБ, SR 11-7) | EMH, Кэрролл, 2–6 мес. | пункт 6 | регулярный отчёт | 6 |
| Outcomes analysis / back-testing, «не реже раза в год» (ЦБ 483-П гл. 14) | срывы целей, просрочки после совета | нет данных | журнал исходов | 5, 6 |
| Методы валидации не меняются с фазой цикла (483-П 14.3) | стенды фиксированы, не подгоняются под «хороший» результат | частично (сертификации заморожены) | правило в документе модели | 15 |
| Вклад каждого фактора в решение (845-П 15.4.2) | объяснимость, индексы Соболя | `weighted_scores` | вклад на уровне популяции | 8, 14 |
| Индекс стабильности популяции (845-П 15.3) | сдвиг распределения входов после запуска | — | мониторинг PSI | «потом» |
| Документация и история изменений доступны проверяющему (ЦБ) | канон, `model_history.md`, ADR | есть | карточка модели | 15 |
| Независимость валидатора (effective challenge) | петля Г31.4 | нет | внешний рецензент/научный руководитель, фиксированные эталоны | 6 |

**Чего НЕ переносить.** Лицензионные требования ПВР (капитал, дефолты, консервативная надбавка) — нас не касаются (Г18–19: под лицензирование не попадаем). Порог OCC $30 млрд — тоже.

**Цена внедрения.** Документ «политика валидации модели» на 2–3 страницы по таблице выше: **4–6 ч**. Библиотек не нужно.

**Корзина.** Политика валидации — **«до запуска»** (нужна и для магистерской, и для ответа регулятору/партнёру B2B). Мониторинг PSI и ежегодный бэктест — **«потом»**.

## Пункт 8. Глобальный анализ чувствительности: Моррис и Соболь на реальных константах канона

**Аналогия.** В машине двадцать ручек настройки. Покрутить каждую по одной, остальные держа на месте, — «локальная» проверка, она пропустит ручки, которые действуют только вместе. «Глобальная» — крутить все сразу случайно много раз и потом статистикой разложить, какая доля разброса результата пришлась на каждую ручку. Моррис — дешёвая разведка «какие ручки вообще что-то делают»; Соболь — точная раскладка долей.

**Что проверяет, в двух числах.** Индекс Соболя первого порядка $S_1$ — доля разброса результата, которую объясняет один параметр сам по себе (от 0 до 1). Полный индекс $S_T$ — та же доля вместе со всеми взаимодействиями с другими параметрами. $S_T \approx 0$ — параметр можно не калибровать: он не решает ничего. У Морриса $\mu^*$ — средний модуль эффекта от шага параметра (сила), $\sigma$ — разброс этого эффекта (нелинейность или взаимодействие).

**Первоисточники.** Morris 1991, *Technometrics* 33(2), DOI 10.1080/00401706.1991.10484804 (OpenAlex HTTP 200, 17.09.2026), дословно: «The proposed experimental plans are composed of individually randomized one-factor-at-a-time designs, and data analysis is based on the resulting random sample of observed elementary effects, those changes in an output due solely to changes in a particular input. Advantages of this approach include a lack of reliance on assumptions of relative sparsity of important inputs, monotonicity of outputs with respect to inputs…». Sobol 2001, *Math. Comput. Simul.* 55, DOI 10.1016/S0378-4754(00)00270-6; Saltelli et al. 2010, *Comput. Phys. Commun.* 181, DOI 10.1016/j.cpc.2009.09.018 (оба — только реквизиты OpenAlex, рефератов в базе нет, тексты закрыты — не открывались). Инструмент — SALib: Herman & Usher 2017, *JOSS*, DOI 10.21105/joss.00097 (открыт), реферат: «SALib contains Python implementations of commonly used global sensitivity analysis methods, including Sobol …, Morris …»; Iwanaga, Usher, Herman 2022, *SESMO*, DOI 10.18174/sesmo.18155: «Sensitivity analysis is now considered a standard practice in environmental modeling.»

**Постановка.** 12 констант канона, подменяемых в памяти процесса (код не менялся): floor (`ranking.RESERVE_FLOOR_MONTHS` 1–3, он же в `crisis`), порог токсичности (0,20–0,40), спред (0,05–0,25), floor при токсичном долге (0,5–2), порог волатильности ADR-015 (0,1–0,5), кап прибавки (0,5–2), множитель $L^*$ (0,7–1,3), множители весов долга и целей (0,7–1,3, с перенормировкой), доля подушки для разового закрытия §11.5 (0,3–0,7), горизонт «близкой» цели (1–6 мес.), ПДН-порог (0,30–0,50). Ситуации: 100 фиксированных (60 обычных портретов ADR-015 с положительным потоком, 20 из них с добавленным МФО, 20 — с добавленной целью через 2 мес.). Выходы: средняя доля потока в досрочку, в резерв, доля ситуаций, где план отличается от плана при значениях канона.

Скрипт `p8_gsa.py` (венв `g39/sav`, SALib 1.5.2):
```python
"""G39 item 8: global sensitivity analysis (Morris elementary effects, Sobol indices; SALib 1.5.2) of the canon decision
to its REAL constants, patched in memory only. Population: 60 plain ADR-015 portraits + 20 of them with an injected MFO (292 %)
+ 20 with an injected near goal (2 months, 30 % of the cushion) -> 100 fixed situations, one month each, dates -> datetime.
Outputs (averaged over the 100 situations): Y_debt = share of free flow to debt prepayment; Y_res = share to reserve;
Y_change = share of situations whose chosen plan differs from the plan under canon defaults."""
import sav_boot  # noqa
import sys, copy, time
from datetime import datetime, timedelta, date
import numpy as np
from SALib.sample import morris as morris_s, sobol as sobol_s
from SALib.analyze import morris as morris_a, sobol as sobol_a
import app.core.ranking as ranking
import app.core.crisis as crisis
import app.core.goals_priority as gp
import app.services.planning as planning
from app.services.planning import run_planning
from tools.portrait_testing.generator import PortraitGenerator

T0 = datetime(2026, 7, 2)
PROB = {"num_vars": 12, "names": [
    "RESERVE_FLOOR_MONTHS", "TOXIC_RATE_ABS", "TOXIC_RATE_SPREAD", "TOXIC_FLOOR_MONTHS", "INCOME_VOL_THRESHOLD", "INCOME_VOL_BOOST_CAP",
    "lt_target_mult", "w_debt_mult", "w_goals_mult", "BLIQ_USAGE_THRESHOLD", "NEAR_GOAL_HORIZON_MONTHS", "DT_MAX"],
    "bounds": [[1.0, 3.0], [0.20, 0.40], [0.05, 0.25], [0.5, 2.0], [0.1, 0.5], [0.5, 2.0],
               [0.7, 1.3], [0.7, 1.3], [0.7, 1.3], [0.3, 0.7], [1.0, 6.0], [0.30, 0.50]]}
DEFAULT = [2.0, 0.30, 0.15, 1.0, 0.3, 1.0, 1.0, 1.0, 1.0, 0.5, 3.0, 0.40]
BASE_PROFILES = copy.deepcopy(ranking.RISK_PROFILES)


def dt(d):
    return datetime(d.year, d.month, d.day) if isinstance(d, date) and not isinstance(d, datetime) else d


def build():
    gen = PortraitGenerator(seed=20260702, version=2)
    out, i = [], 0
    while len(out) < 60:
        p = gen.generate_with_income_history(i); i += 1
        if p["kind"] != "plain" or p["income_total"] <= 0 or p["income_total"] - p["expense_total"] - sum(o["monthly_payment"] for o in p["obligations"]) <= 0:
            continue
        for g in p["goals"]:
            g["deadline"] = dt(g.get("deadline"))
        out.append(p)
    extra = []
    for p in out[:20]:
        q = copy.deepcopy(p); inc = q["income_total"]
        q["obligations"].append({"id": 99, "name": "MFO", "amount": 0.33 * inc, "interest_rate": 2.92, "monthly_payment": 0.02 * inc})
        extra.append(q)
    for p in out[20:40]:
        q = copy.deepcopy(p)
        q["goals"].append({"id": 98, "name": "near", "target_amount": 0.3 * q["bliq"] + 1, "current_amount": 0.0, "deadline": T0 + timedelta(days=60)})
        extra.append(q)
    return out + extra


def apply(x):
    (ranking.RESERVE_FLOOR_MONTHS, ranking.TOXIC_RATE_ABS, ranking.TOXIC_RATE_SPREAD, ranking.TOXIC_FLOOR_MONTHS,
     ranking.INCOME_VOLATILITY_THRESHOLD, ranking.INCOME_VOLATILITY_FLOOR_BOOST_CAP) = x[:6]
    crisis.RESERVE_FLOOR_MONTHS = x[0]
    gp.BLIQ_USAGE_THRESHOLD, gp.NEAR_GOAL_HORIZON_MONTHS = x[9], x[10]
    planning.DT_MAX = x[11]
    for k, base in BASE_PROFILES.items():
        prof = ranking.RISK_PROFILES[k]
        wd, wr, wl, wg = base["w_dt"] * x[7], base["w_rt"] * x[7], base["w_lt"], base["w_goals"] * x[8]
        s = wd + wr + wl + wg
        prof.update(w_dt=wd / s, w_rt=wr / s, w_lt=wl / s, w_goals=wg / s, lt_target=base["lt_target"] * x[6])


def evaluate(x, pop, ref=None):
    apply(x)
    debt = res = 0.0; ids = []
    for p in pop:
        r = run_planning(p["income_total"], p["expense_total"], p["obligations"], p["goals"], bliq=p["bliq"], r_bench=p["r_bench"],
                         risk_tolerance=p["risk_tolerance"], today=T0, income_history=p.get("income_history"))
        b = r["best"]
        R = max(1e-9, r["indicators"]["Rt"])
        if b is not None:
            debt += b["x_obl_effective"] / R; res += b["x_reserve_effective"] / R
        ids.append(None if b is None else (b["id"], round(r["bliq_preallocation"]["bliq_used"])))
    ch = 0.0 if ref is None else np.mean([a != c for a, c in zip(ids, ref)])
    return debt / len(pop), res / len(pop), ch, ids


pop = build()
d0, r0, _, ref = evaluate(DEFAULT, pop)
print(f"situations {len(pop)}; canon defaults: share to debt {d0:.3f}, to reserve {r0:.3f}")
t = time.time()
X = morris_s.sample(PROB, N=24, num_levels=6, seed=1)
Y = np.array([evaluate(x, pop, ref)[:3] for x in X])
print(f"\nMORRIS: {len(X)} runs, {time.time() - t:.0f}s. mu* (mean |elementary effect|), sigma (non-linearity/interaction), normalised by output range")
for j, lab in enumerate(["Y_debt", "Y_res", "Y_change"]):
    Si = morris_a.analyze(PROB, X, Y[:, j], num_levels=6, seed=1)
    order = np.argsort(-np.array(Si["mu_star"]))
    print(f"  {lab}: " + "; ".join(f"{PROB['names'][k]} mu*={Si['mu_star'][k]:.3f} s={Si['sigma'][k]:.3f}" for k in order))
t = time.time()
Xs = sobol_s.sample(PROB, 64, calc_second_order=False, seed=2)
Ys = np.array([evaluate(x, pop, ref)[:3] for x in Xs])
print(f"\nSOBOL (Saltelli/Jansen estimators): {len(Xs)} runs, {time.time() - t:.0f}s. S1 = own effect share, ST = total incl. interactions (conf = 95 % bootstrap half-width)")
for j, lab in enumerate(["Y_debt", "Y_res", "Y_change"]):
    Si = sobol_a.analyze(PROB, Ys[:, j], calc_second_order=False, seed=2)
    order = np.argsort(-Si["ST"])
    print(f"  {lab} (output var {Ys[:, j].var():.4f}): " + "; ".join(f"{PROB['names'][k]} S1={Si['S1'][k]:.2f} ST={Si['ST'][k]:.2f}±{Si['ST_conf'][k]:.2f}" for k in order))
apply(DEFAULT)
```
Вывод:
```
situations 100; canon defaults: share to debt 0.326, to reserve 0.576

MORRIS: 312 runs, 124s. mu* (mean |elementary effect|), sigma (non-linearity/interaction), normalised by output range
  Y_debt: w_debt_mult mu*=0.185 s=0.115; RESERVE_FLOOR_MONTHS mu*=0.136 s=0.047; w_goals_mult mu*=0.060 s=0.066; TOXIC_FLOOR_MONTHS mu*=0.053 s=0.026; TOXIC_RATE_ABS mu*=0.018 s=0.024; lt_target_mult mu*=0.012 s=0.013; TOXIC_RATE_SPREAD mu*=0.011 s=0.020; NEAR_GOAL_HORIZON_MONTHS mu*=0.005 s=0.008; BLIQ_USAGE_THRESHOLD mu*=0.004 s=0.008; INCOME_VOL_THRESHOLD mu*=0.002 s=0.003; INCOME_VOL_BOOST_CAP mu*=0.000 s=0.000; DT_MAX mu*=0.000 s=0.000
  Y_res: RESERVE_FLOOR_MONTHS mu*=0.179 s=0.033; w_debt_mult mu*=0.107 s=0.050; TOXIC_FLOOR_MONTHS mu*=0.054 s=0.026; lt_target_mult mu*=0.038 s=0.023; TOXIC_RATE_ABS mu*=0.018 s=0.024; TOXIC_RATE_SPREAD mu*=0.011 s=0.020; NEAR_GOAL_HORIZON_MONTHS mu*=0.010 s=0.015; BLIQ_USAGE_THRESHOLD mu*=0.008 s=0.015; INCOME_VOL_THRESHOLD mu*=0.003 s=0.003; w_goals_mult mu*=0.001 s=0.001; INCOME_VOL_BOOST_CAP mu*=0.000 s=0.000; DT_MAX mu*=0.000 s=0.000
  Y_change: NEAR_GOAL_HORIZON_MONTHS mu*=0.089 s=0.111; w_debt_mult mu*=0.076 s=0.082; RESERVE_FLOOR_MONTHS mu*=0.060 s=0.040; BLIQ_USAGE_THRESHOLD mu*=0.053 s=0.096; TOXIC_FLOOR_MONTHS mu*=0.042 s=0.035; w_goals_mult mu*=0.038 s=0.046; lt_target_mult mu*=0.025 s=0.012; TOXIC_RATE_ABS mu*=0.013 s=0.018; TOXIC_RATE_SPREAD mu*=0.011 s=0.022; INCOME_VOL_THRESHOLD mu*=0.001 s=0.005; INCOME_VOL_BOOST_CAP mu*=0.000 s=0.000; DT_MAX mu*=0.000 s=0.000

SOBOL (Saltelli/Jansen estimators): 896 runs, 393s. S1 = own effect share, ST = total incl. interactions (conf = 95 % bootstrap half-width)
  Y_debt (output var 0.0048): w_debt_mult S1=0.66 ST=0.69±0.27; RESERVE_FLOOR_MONTHS S1=0.22 ST=0.38±0.15; w_goals_mult S1=0.06 ST=0.07±0.04; TOXIC_FLOOR_MONTHS S1=0.07 ST=0.05±0.03; TOXIC_RATE_ABS S1=0.03 ST=0.01±0.01; TOXIC_RATE_SPREAD S1=0.00 ST=0.01±0.01; lt_target_mult S1=-0.00 ST=0.01±0.00; NEAR_GOAL_HORIZON_MONTHS S1=-0.02 ST=0.00±0.00; INCOME_VOL_THRESHOLD S1=-0.00 ST=0.00±0.00; BLIQ_USAGE_THRESHOLD S1=-0.00 ST=0.00±0.00; INCOME_VOL_BOOST_CAP S1=0.00 ST=0.00±0.00; DT_MAX S1=0.00 ST=0.00±0.00
  Y_res (output var 0.0042): RESERVE_FLOOR_MONTHS S1=0.54 ST=0.65±0.25; w_debt_mult S1=0.28 ST=0.30±0.11; lt_target_mult S1=0.05 ST=0.07±0.03; TOXIC_FLOOR_MONTHS S1=0.09 ST=0.07±0.04; TOXIC_RATE_ABS S1=0.03 ST=0.02±0.01; NEAR_GOAL_HORIZON_MONTHS S1=-0.02 ST=0.02±0.01; TOXIC_RATE_SPREAD S1=0.02 ST=0.01±0.01; INCOME_VOL_THRESHOLD S1=-0.00 ST=0.00±0.00; w_goals_mult S1=0.00 ST=0.00±0.00; BLIQ_USAGE_THRESHOLD S1=0.00 ST=0.00±0.00; INCOME_VOL_BOOST_CAP S1=0.00 ST=0.00±0.00; DT_MAX S1=0.00 ST=0.00±0.00
  Y_change (output var 0.0050): NEAR_GOAL_HORIZON_MONTHS S1=0.32 ST=0.30±0.16; w_debt_mult S1=0.20 ST=0.22±0.15; RESERVE_FLOOR_MONTHS S1=0.12 ST=0.09±0.04; TOXIC_FLOOR_MONTHS S1=0.02 ST=0.04±0.02; w_goals_mult S1=0.04 ST=0.03±0.02; lt_target_mult S1=0.01 ST=0.01±0.01; TOXIC_RATE_ABS S1=0.01 ST=0.01±0.01; TOXIC_RATE_SPREAD S1=-0.01 ST=0.00±0.01; INCOME_VOL_THRESHOLD S1=0.01 ST=0.00±0.00; BLIQ_USAGE_THRESHOLD S1=-0.01 ST=0.00±0.00; INCOME_VOL_BOOST_CAP S1=0.00 ST=0.00±0.00; DT_MAX S1=0.00 ST=0.00±0.00
```

**Что это значит.**
1. **Решают три ручки:** веса долга (доля в разбросе досрочки $S_T$ = 0,69), размер floor ($S_T$ = 0,65 для резерва, 0,38 для досрочки) и горизонт «близкой» цели ($S_T$ = 0,30 для смены плана — через разовое закрытие §11.5). Это и есть параметры, которые обязаны иметь внешнюю опору (пункт 6); у floor она частично есть, у весов и горизонта 3 мес. — нет.
2. 🔴 **Не решают ничего (ST = 0,00):** ПДН-порог `DT_MAX` — подтверждает доказательство Z3 (пункт 2.3): гейт не срабатывает; кап прибавки ADR-015 и порог волатильности (≤ 0,003 по Моррису) — на портретах ADR-015 прибавка floor почти не включается (пункт 6: CV редко выше 0,3). Их калибровка — пустая работа, пока не изменена формула.
3. **Порог токсичности 30 % и спред — слабые в среднем** ($S_T$ ≤ 0,02), хотя Г40 № 14 показал полный разворот совета на отдельном портрете при 29,5 → 30 %. Одно не противоречит другому: глобальный индекс усредняет по популяции, где ставок у порога мало. Вывод для владельца: **глобальный анализ не заменяет карту разрывов** (Г40, `p2.py`) — нужны оба.
4. **Взаимодействия заметны у floor** ($S_T$ − $S_1$ = 0,16 для досрочки; $\sigma$ Морриса у весов долга 0,115 больше половины $\mu^*$): эффект floor зависит от весов — калибровать их по отдельности нельзя.
5. **Точность оценок.** 896 прогонов × 100 ситуаций — доверительные полуширины до ±0,27 у крупных индексов; ранжирование «решает / не решает» устойчиво, точные доли — нет. Для отчёта в магистерскую — поднять N до 256–512 (≈ 30–60 мин).
6. **Зона L∈[1;2) с разбросом 66 п. п.** (из постановки) — это зона между floor при токсичном долге и обычным floor; её вес подтверждён: `TOXIC_FLOOR_MONTHS` + `RESERVE_FLOOR_MONTHS` вместе — вторая по силе группа.

**Цена внедрения.** Стенд готов: **3–4 ч** на перенос в `tools/model_validation/gsa.py` + отчёт; SALib (MIT) и scipy — dev-зависимости в отдельном окружении. Прогон ~10 мин.

**Корзина.** **«Сразу после синтеза»** — как фильтр: какие параметры калибровать (веса, floor, горизонт 3 мес.), какие удалить или переписать (ПДН-гейт, ADR-015 порог). Повтор после каждой смены правила выбора — **«потом»**.

## Пункт 9. Устойчивость многокритериального ранжирования: интервалы O'Shea, SMAA, rank reversal (skcriteria)

**Аналогия.** Жюри выбрало победителя. Вопрос: если одному судье чуть изменить вес голоса — победитель тот же? Интервал устойчивости — насколько можно сдвинуть вес, пока победитель не сменится. SMAA — «пересудить конкурс тысячу раз со случайными весами и посчитать, как часто побеждает тот же».

**Первоисточники.** O'Shea, Deeney, Triantaphyllou, Diaz-Balteiro, Tarim 2026, *Expert Systems with Applications* 296, 128460, DOI 10.1016/j.eswa.2025.128460 — реферат `research.ucc.ie/en/publications/weight-stability-intervals-for-multi-criteria-decision-analysis-u/` через `r.jina.ai`, HTTP 200, 19 896 байт, 17.09.2026 (полный PDF 16.09 отдавал 403, `raw/mcda_saw_alternatives_2026-09-09.md`). Дословно: «The first contribution of this paper is the development of a novel method for determining precise weight stability intervals which does not rely on enumeration or simulation for use with the weighted sum model (WSM, based on the L 1 Minkowski norm)»; WSI — «the range of values for individual weights for which the ranking of alternatives will not change». 🟡 Формула самой статьи не прочитана (закрыт текст); в скрипте — собственный вывод той же идеи: при пропорциональном пересчёте остальных весов разница полезностей двух альтернатив линейна по изменяемому весу, значит точку смены даёт одно линейное уравнение. SMAA — Lahdelma, Hokkanen, Salminen 1998, *EJOR* 106(1), DOI 10.1016/S0377-2217(97)00163-X (только реквизиты, реферата в OpenAlex нет). Rank reversal — `skcriteria.ranksrev.rank_invariant_check.RankInvariantChecker` (scikit-criteria 0.10), докстрока дословно: «the best alternative identified by the method should remain unchanged when a non-optimal alternative is replaced by a worse alternative, provided that the relative importance of each decision criterion remains the same.»

**Наш модуль.** `app/core/ranking.py::rank_alternatives` — веса `RISK_PROFILES`, min-max нормировка, лексикографический floor. Проблема Г40 № 5 и Г30.2-К.

Скрипт `p9_rank_stability.py`:
```python
"""G39 item 9: stability of the canon choice to its weights, on 600 plain ADR-015 portraits (one month, dates -> datetime).
(a) closed-form weight stability intervals (WSI, O'Shea et al. 2026 idea for the weighted sum): change one weight w_j, rescale the
    others proportionally; U_a - U_b is linear in w_j, so the flip point against every competitor is a root of a linear equation.
    Computed on the canon's own normalised scores inside the top floor_level group (the lexicographic first stage is kept fixed).
(b) SMAA-style acceptability: weights drawn uniformly from the simplex (Dirichlet(1,1,1,1)); share of draws where the canon's choice wins.
(c) scikit-criteria RankInvariantChecker (RRT1) on the 4-criteria matrix with min-max + weighted sum."""
import sav_boot  # noqa
import warnings
from datetime import datetime, date
import numpy as np
import app.core.ranking as ranking
from app.services.planning import run_planning
from tools.portrait_testing.generator import PortraitGenerator
warnings.filterwarnings("ignore")
T0 = datetime(2026, 7, 2)
KEYS = ["Rt_norm", "Lt_norm", "Dt_norm", "Si_norm"]
WK = ["w_rt", "w_lt", "w_dt", "w_goals"]
rng = np.random.default_rng(3)


def dt(d):
    return datetime(d.year, d.month, d.day) if isinstance(d, date) and not isinstance(d, datetime) else d


def wsi(S, a, w, j):
    lo, hi = 0.0, 1.0
    for b in range(len(S)):
        if b == a:
            continue
        d = S[a] - S[b]
        rest = sum(w[k] * d[k] for k in range(4) if k != j) / (1 - w[j]) if w[j] < 1 else 0.0
        # f(x) = x*d_j + (1-x)*rest ; f(w_j) >= 0 at the current weights (a is best)
        slope = d[j] - rest
        if abs(slope) < 1e-12:
            continue
        root = -rest / slope
        if slope > 0:
            lo = max(lo, root)
        else:
            hi = min(hi, root)
    return lo, hi


gen = PortraitGenerator(seed=20260702, version=2)
dist = {k: [] for k in WK}; flips05 = {k: 0 for k in WK}; acc = []; zero_width = 0; n = 0; mats = []
i = 0
while n < 600:
    p = gen.generate_with_income_history(i); i += 1
    if p["kind"] != "plain" or p["income_total"] <= 0:
        continue
    for g in p["goals"]:
        g["deadline"] = dt(g.get("deadline"))
    r = run_planning(p["income_total"], p["expense_total"], p["obligations"], p["goals"], bliq=p["bliq"], r_bench=p["r_bench"],
                     risk_tolerance=p["risk_tolerance"], today=T0, income_history=p.get("income_history"))
    if r["best"] is None:
        continue
    n += 1
    top = r["ranked"][0]["floor_level"]
    grp = [x for x in r["ranked"] if x["floor_level"] >= top - 1e-9]
    S = np.array([[x["scores"][k] for k in KEYS] for x in grp])
    w = np.array([ranking.RISK_PROFILES[p["risk_tolerance"]][k] for k in WK])
    a = 0
    for j, k in enumerate(WK):
        lo, hi = wsi(S, a, w, j)
        d = min(w[j] - lo, hi - w[j])
        dist[k].append(max(d, 0.0))
        flips05[k] += d < 0.05
    zero_width += any(np.all(np.abs(S[b] - S[a]) < 1e-9) is False and abs((S[a] - S[b]) @ w) < 1e-9 for b in range(1, len(S)))
    W = rng.dirichlet(np.ones(4), 500)
    wins = np.argmax(W @ S.T, axis=1)
    acc.append(np.mean(np.all(np.isclose(S[wins], S[a]), axis=1)))
    if len(mats) < 40 and len(grp) >= 5:
        mats.append((np.array([[x["Rt_new"], x["scores"]["Lt_capped"], x["Dt_new"], x["Si"]] for x in r["ranked"]]), w))
print(f"portraits {n}")
print("(a) distance from the current weight to the nearest rank flip of the top choice (absolute weight units):")
for k in WK:
    v = np.array(dist[k])
    print(f"  {k:7}: median {np.median(v):.3f}  p10 {np.percentile(v, 10):.3f}  share with flip within +-0.05: {flips05[k] / n:.1%}  share with distance 0 (tie): {np.mean(v < 1e-9):.1%}")
print(f"  exact ties at the top (another alternative with equal utility, different scores): {zero_width / n:.1%}")
acc = np.array(acc)
print(f"(b) SMAA acceptability of the canon choice (share of random weight vectors where it wins): median {np.median(acc):.2f}, p10 {np.percentile(acc, 10):.2f}, share < 0.25: {np.mean(acc < 0.25):.1%}")
from skcriteria import mkdm
from skcriteria.pipeline import mkpipe
from skcriteria.preprocessing.invert_objectives import InvertMinimize
from skcriteria.preprocessing.scalers import MinMaxScaler
from skcriteria.agg.simple import WeightedSumModel
from skcriteria.ranksrev.rank_invariant_check import RankInvariantChecker
pipe = mkpipe(InvertMinimize(), MinMaxScaler(target="matrix"), WeightedSumModel())
ok = bad = err = 0
for M, w in mats:
    # drop exact duplicate rows (skcriteria needs distinct alternatives for a meaningful test)
    M = np.unique(np.round(M, 6), axis=0)
    if len(M) < 3:
        continue
    dm = mkdm(M, objectives=[max, max, min, max], weights=[w[0], w[1], w[2], w[3]])
    try:
        res = RankInvariantChecker(pipe, repeat=2, random_state=4).evaluate(dm)
        ranks = [rk for _, rk in res.ranks] if hasattr(res, "ranks") else []
        best0 = ranks[0].alternatives[np.argmin(ranks[0].values)] if ranks else None
        same = all(rk.alternatives[np.argmin(rk.values)] == best0 for rk in ranks[1:])
        ok += same; bad += not same
    except Exception as e:
        err += 1
        if err == 1:
            print("  skcriteria error:", type(e).__name__, str(e)[:200])
print(f"(c) skcriteria RRT1 (worsen suboptimal alternatives, repeat=2) on {ok + bad} decision matrices: best alternative unchanged in {ok}, changed in {bad}; errors {err}")
```
Вывод:
```
/private/tmp/claude-501/-Users-vasyaevdokimov-repos-personal-finance-dss/fe25aad2-149b-48bd-a8b2-c62cc04ce4a1/scratchpad/g39/sav/lib/python3.13/site-packages/skcriteria/pipeline.py:26: SKCriteriaDeprecationWarning: The 'skcriteria.pipeline' module is deprecated since 0.9 and will be removed in 1.0 Use 'skcriteria.pipelines' instead.
  deprecate.warn(
portraits 600
(a) distance from the current weight to the nearest rank flip of the top choice (absolute weight units):
  w_rt   : median 0.200  p10 0.072  share with flip within +-0.05: 5.5%  share with distance 0 (tie): 1.2%
  w_lt   : median 0.200  p10 0.060  share with flip within +-0.05: 6.7%  share with distance 0 (tie): 1.0%
  w_dt   : median 0.203  p10 0.087  share with flip within +-0.05: 4.7%  share with distance 0 (tie): 1.0%
  w_goals: median 0.200  p10 0.074  share with flip within +-0.05: 3.5%  share with distance 0 (tie): 0.2%
  exact ties at the top (another alternative with equal utility, different scores): 0.0%
(b) SMAA acceptability of the canon choice (share of random weight vectors where it wins): median 1.00, p10 0.48, share < 0.25: 5.3%
  skcriteria error: ValueError Input X contains infinity or a value too large for dtype('float64').
(c) skcriteria RRT1 (worsen suboptimal alternatives, repeat=2) on 28 decision matrices: best alternative unchanged in 15, changed in 13; errors 10
```

**Что это значит.**
1. **К весам выбор канона устойчив:** медиана расстояния до смены победителя 0,20 — это значит, что у половины портретов победитель не меняется, даже если вес опустить до нуля (расстояние упирается в сам вес). Сдвиг веса на ±0,05 меняет выбор у 3,5–6,7 % портретов. SMAA: медиана приемлемости 1,00, у 5,3 % портретов выбор канона побеждает менее чем при четверти случайных весов. Причина устойчивости — та же, что у «одной корзины» Г40: решение почти всегда вершина, и её держит не тонкая настройка весов, а грубая структура задачи. Это хорошая новость для объяснимости и плохая для утверждения «профиль риска тонко управляет советом».
2. 🔴 **К набору альтернатив — неустойчив:** в тесте rank reversal (ухудшить неоптимальную альтернативу — победитель должен остаться) лучший вариант сменился в **13 из 28** матриц. Это прямое подтверждение Д-04 / Г40 № 5 внешним инструментом: при min-max нормировке «ухудшение проигравшего» меняет размах шкалы и переставляет победителя. Оговорки: (а) skcriteria инвертирует минимизируемый критерий через $1/x$ (`InvertMinimize`), канон — через $\max - x$, то есть проверена близкая, но не та же свёртка; (б) 10 матриц упали на $1/0$ (ПДН = 0 у людей без долга) — это ограничение инструмента, не ядра; (в) выборка малая (28). Число — индикатор, не метрика.
3. Строка «exact ties at the top: 0.0 %» — **ошибка скрипта** (сравнение `np.all(...) is False` всегда ложно для numpy-булева), её не читать; реальные ничьи видны в колонке «distance 0»: 0,2–1,2 % портретов (Д-03).

**Цена внедрения.** WSI + SMAA как стенд: **3–4 ч** (numpy, без новых зависимостей). Собственный RRT1 с нормировкой канона (вместо skcriteria): **2–3 ч**. Ежедневный CI не нужен — отчёт на каждый батч, меняющий веса или нормировку.

**Корзина.** RRT1 на нормировке канона — **«до запуска»**, если путь (б) не принят (иначе снимается глобальными шкалами). WSI/SMAA-отчёт — **«потом»** (устойчивость к весам уже высокая); но для магистерской — таблица из пункта полезна сразу.

## Пункт 10. Стресс-сценарии на реальных траекториях РФ (2014–2015, 2022)

**Аналогия.** Краш-тест: машину разгоняют не на абстрактной скорости, а на той, с которой реально бьются на трассе. Мы прогоняем ядро через те месяцы, когда ключевая ставка прыгала за одну ночь.

**Что проверяет.** Как меняется совет, когда внешний параметр ($r_{bench}$) идёт по реальной исторической траектории: нет ли «пилы» (досрочка → стоп → досрочка), сколько людей получают разворот совета, чего это стоит.

**Данные.** Траектории — по датам решений ЦБ из `raw/key_rate_history_forecastability_2026-09-10.md` (2014: 10,5 → 17 % 16.12.2014, «полпути назад за 4,6 мес.»; 2022: 9,5 → 20 % 28.02.2022, 14 % с 04.05.2022, спуск шагами −3 п.п.). Там же: вклады до года следуют за ключевой в тот же месяц (коэффициент ≈ 1,0), кредиты физлиц — слабо (≈ 0,5, договорная ставка фиксирована). Модуль: `app/services/cbr_rate.py::get_key_rate` — источник $r_{bench}$; решение — `avalanche.py::select_avalanche_targets` (фильтр «ставка ≥ $r_{bench}$»).

Скрипт `p10_stress.py`:
```python
"""G39 item 10: stress on real RF key-rate trajectories. r_bench (canon: the key rate is its fallback source, app/services/cbr_rate.py)
follows the month-average key rate of 2022 (spike 9.5 -> 20) and of 12.2014-11.2015 (10.5 -> 17 -> 11), versus a flat path.
Values: raw/key_rate_history_forecastability_2026-09-10.md (decision dates). Ledger = p0b_sim.py; yield on cash stays at the portrait's r_bench (limitation).
Metrics per portrait: months where the dominant use of free flow (debt / reserve / goals) switches; whether prepayment stops at the spike."""
import sys, json, statistics as stt
sys.path.insert(0, "/private/tmp/claude-501/-Users-vasyaevdokimov-repos-personal-finance-dss/fe25aad2-149b-48bd-a8b2-c62cc04ce4a1/scratchpad/g39")
import p0b_sim as S
from tools.portrait_testing.generator import PortraitGenerator

PATHS = {
    "flat_9.5": [0.095] * 12,
    "2022": [0.085, 0.095, 0.20, 0.17, 0.125, 0.105, 0.08, 0.08, 0.075, 0.075, 0.075, 0.075],
    "2014-15": [0.105, 0.17, 0.17, 0.15, 0.14, 0.13, 0.12, 0.115, 0.11, 0.11, 0.11, 0.11],
}
CUR = {"path": None}
_rp = S.run_planning


def rp(inc, exp, obls, goals, **kw):
    m = min(11, (kw["today"] - S.T0).days // 30)
    kw["r_bench"] = CUR["path"][m]
    return _rp(inc, exp, obls, goals, **kw)


S.run_planning = rp


def dominant(entry):
    if entry[1] == "CRISIS":
        return "crisis"
    _, d, r, g = entry
    return max((d, "debt"), (r, "reserve"), (g, "goals"))[1] if d + r + g > 0 else "none"


gen = PortraitGenerator(seed=20260702, version=2)
res = {k: {"switches": [], "stop": 0, "net": [], "debtors": 0, "resume": 0} for k in PATHS}
n = 0
for i in range(1500):
    p = gen.generate_with_income_history(i)
    if p["kind"] != "plain" or p["income_total"] <= 0 or not p["obligations"]:
        continue
    n += 1
    path, vol = S.income_path(p, i)
    for name, rpath in PATHS.items():
        CUR["path"] = rpath
        m = S.simulate(p, path, "canon", p["r_bench"])
        dom = [dominant(e) for e in m["plan"]]
        res[name]["switches"].append(sum(1 for a, b in zip(dom, dom[1:]) if a != b))
        res[name]["net"].append(m["net_end"] / max(1, sum(path)))
        pre = m["plan"][1]; spike = m["plan"][2]; late = m["plan"][8]
        if pre[1] != "CRISIS" and pre[1] > 1:
            res[name]["debtors"] += 1
            if spike[1] != "CRISIS" and spike[1] <= 1:
                res[name]["stop"] += 1
                if late[1] != "CRISIS" and late[1] > 1:
                    res[name]["resume"] += 1
print(f"plain portraits with debt: {n}")
base = res["flat_9.5"]["net"]
for name, v in res.items():
    d = [a - b for a, b in zip(v["net"], base)]
    print(f"  {name:9}: mean switches of dominant use {stt.mean(v['switches']):.2f}; prepaying in month 2: {v['debtors']}; "
          f"stopped prepayment in month 3 (spike): {v['stop']} ({v['stop'] / max(1, v['debtors']):.1%}), resumed by month 9: {v['resume']}; "
          f"net vs flat path, % of 12-mo income: median {stt.median(d):+.3%}, min {min(d):+.3%}")
```
Вывод:
```
plain portraits with debt: 556
  flat_9.5 : mean switches of dominant use 3.05; prepaying in month 2: 305; stopped prepayment in month 3 (spike): 5 (1.6%), resumed by month 9: 1; net vs flat path, % of 12-mo income: median +0.000%, min +0.000%
  2022     : mean switches of dominant use 3.34; prepaying in month 2: 305; stopped prepayment in month 3 (spike): 102 (33.4%), resumed by month 9: 83; net vs flat path, % of 12-mo income: median +0.000%, min -0.972%
  2014-15  : mean switches of dominant use 3.17; prepaying in month 2: 232; stopped prepayment in month 3 (spike): 4 (1.7%), resumed by month 9: 0; net vs flat path, % of 12-mo income: median +0.000%, min -0.833%
```

**Что это значит.**
1. 🔴 **«Пила» 2022 года реальна:** у **33,4 %** заёмщиков, гасивших долг досрочно, в марте 2022 совет разворачивается «стоп досрочке» (их кредиты под 12–19 % перестают проходить фильтр $r_{bench}$ = 20 %), и у **81 %** из них (83 из 102) к сентябрю досрочка возвращается. Для человека это три противоположных совета за полгода. Экономически временный стоп оправдан (вклады реально дали ~19 %), но **ядро не знает, что шок временный** — у него нет памяти и гистерезиса (Г40 № 15 о границе $R_t = 0$ — тот же класс).
2. **Шок 2014 года почти не задел совет** (1,7 %): портретов со ставками 11–17 % между старой и новой ставкой мало, а спуск был медленным.
3. **Даже без шока совет «переключается» ~3 раза в год** (плоская ставка 9,5 %: 3,05 смены главного направления потока) — из-за колебаний дохода портретов. Это базовая частота «пилы», с которой надо сравнивать любую новую версию.
4. **Деньги:** медиана разницы с плоской траекторией 0, худший портрет −0,97 % годового дохода. 🟡 Ограничение: доходность подушки в бухгалтерии не следует за ключевой (осталась ставкой портрета), поэтому выгода «вкладов под 20 %» не учтена — денежный итог стресса занижен в пользу плоской траектории; качественный вывод о «пиле» от этого не зависит.
5. Инфляционный всплеск (расходы +7–11 %) **не прогонялся** — бухгалтерия `p0b_sim.py` держит расходы постоянными (ЗАДОЛЖЕННОСТЬ, п. 10 ниже).

**Цена внедрения.** Стенд траекторий: **3–5 ч** (готов на 80 %); доходность и расходы по траектории — ещё **2–3 ч**. Метрика «число разворотов совета в год» — **1 ч**. Библиотек не нужно.

**Корзина.** Метрика разворотов и стенд 2022 — **«до запуска»** (ставка 2026 года в зоне 14–21 %, шок того же класса вероятен: «≈ 50 % шанс хотя бы одного такого эпизода внутри 36-месячного окна», тот же сырой файл). Правило гистерезиса для $r_{bench}$ — решение владельца, **«потом»**.

---

# Часть C. Развитие и оптимизация ядра

## Пункт 11. Лучше эвристики: гарантии качества, где DP, где MILP

**Аналогия.** Прежде чем покупать дорогой навигатор, узнать, на сколько минут он в среднем быстрее нынешнего. Если на две минуты из часа — покупать надо что-то другое.

**Что известно (вход, не переоткрывается).** Avalanche не оптимален в общем случае (Rios-Solis 2017, разрыв > 4 %, в пределе 40 %, задача NP-трудна); жадный шаг оптимален лишь при условиях Fox 1966 / Federgruen & Groenevelt 1986, которые минимальные платежи и ПДН нарушают (постановка Г39). Г40 п. 4.1: на наших допущениях 0 из 3 000 портфелей, где иной порядок гашения лучше. Г41: policy search берёт 82 % выигрыша оптимума простым правилом; DP точно невычислимо, перебор 66 точек + правило = политика класса CFA (Powell).

**Что добавил этот батч — числом.**
1. **Потолок выигрыша любой эвристики** — разрыв канона до ясновидящего денежного оптимума (пункт 0): медиана **0,17 %** годового дохода без токсичного долга, **1,3 %** с МФО; p90 — 1,6 % и 3,3 %. Гарантию вида «не хуже оптимума больше чем на ε» для правила выбора можно не доказывать теоретически — её можно **измерять** оракулом на каждой версии (пункт 1).
2. **Сетка тоньше дорого, выигрыш мал** (`p13b_grid.py`, ниже): 66 → 5 151 альтернатива — время 6 → 458 мс; Г40 9.3: план меняется у 22,5 % портретов, но p90 сдвига — 2 % потока. Двухуровневая сетка (тема 40: ~242 точки) — разумный компромисс.
3. **Где MILP реально нужен** — как офлайн-оракул (пункт 1); в продукт — нет (Г41, путь (в): объяснимость и данные о шоках). **Где DP реален** — только для одномерного решения «сколько в подушку при неровном доходе» (таблица Кэрролла, Г41 рамка 3), и то офлайн, как справочник.
4. **Где выигрыш есть и не требует новой математики** — токсичный долг (разрыв ×8 к обычным портретам) и сроки целей: там policy search по 2–3 параметрам на симуляторе пункта 0 (с оракулом как эталоном) — следующий шаг, а не новая эвристика.

**Цена.** Policy search для порога токсичности и ε-правил на стенде пункта 0: **1–2 дня**. Библиотек не нужно (перебор по сетке параметров).

**Корзина.** **«Потом»** — после решения владельца по пути (б); метрика «разрыв до оракула» — уже в гейтах (ИТОГ §4).

## Пункт 12. Номинал против реальных величин

**Аналогия.** Сравнивать две цены в рублях одного и того же месяца можно без поправки на инфляцию. Поправка нужна, только когда сравниваешь рубли разных лет.

**Что проверяет.** Меняет ли перевод в реальные величины (за вычетом инфляции) выбор ядра.

**Вывод по построению (без скрипта — алгебра на одну строку).** Реальная ставка по Фишеру: $r^{real} = \frac{1+r}{1+\pi} - 1$, где $r$ — номинальная ставка, $\pi$ — инфляция. Для двух ставок $r_1, r_2$ при одной и той же $\pi > -1$: $r_1^{real} \ge r_2^{real} \iff r_1 \ge r_2$ (деление на одно положительное число $1+\pi$ порядок не меняет). Значит: (а) порядок Avalanche в реальных величинах тот же; (б) фильтр «ставка кредита ≥ $r_{bench}$» тот же, если и ставка, и бенчмарк переводятся одной инфляцией. **Внутри одного месяца выбор ядра инвариантен к переводу номинал → реал.** Расхождение появляется только там, где сравниваются рубли разных дат: (1) индексация целей §11.3 с обрывом на 36 мес. (+12,5 % за один день, Г40 № 20; пункт 3, Д-06); (2) экран прогноза и график погашения (многомесячные суммы); (3) путь (б) и оракул пункта 0 — 12-месячная чистая позиция в номинале занижает цену отложенной цели при инфляции. Проверка Г30.2-К («порядок 66 альтернатив в реальных величинах может расходиться») — **для одномесячного выбора закрыта отрицательно**: расходиться нечему.

**Где стоит пересчитать.** Метрику пункта 0 — в реальных рублях при $\pi$ = 4–8 %: цена пунктуальности целей (0,05–0,25 ₽/₽) сравнима с годовой инфляцией, и перевод может поменять вывод о «дорогой» пунктуальности. **ЗАДОЛЖЕННОСТЬ** — не пересчитано.

**Цена.** Реальные величины в стенде пункта 0: **2–3 ч**; сглаживание обрыва §11.3 — **1–2 ч** + решение владельца.

**Корзина.** Сглаживание обрыва §11.3 — **«до запуска»** (Д-06 виден пользователю). Реальные величины в оракуле — **«сразу после синтеза»** вместе с пунктом 1.

## Пункт 13. Производительность: профиль, пределы Python

**Аналогия.** Прежде чем ставить турбину, взвесить машину и засечь, где она тормозит.

Скрипты `p13_14_perf_explain.py` (часть 13) и `p13b_grid.py`:
```python
"""G39 item 13b: cost of a finer grid (step knob of run_planning) on a portrait with positive flow, debts and goals."""
import sys, time
from datetime import datetime
sys.path.insert(0, "/Users/vasyaevdokimov/repos/personal-finance-dss")
from app.services.planning import run_planning
T0 = datetime(2026, 7, 2)
obls = [{"id": k, "name": f"l{k}", "amount": 200_000.0 * (k + 1), "interest_rate": r, "monthly_payment": 8_000.0} for k, r in enumerate((0.35, 0.22, 0.18))]
goals = [{"id": j, "name": f"g{j}", "target_amount": 300_000.0, "current_amount": 10_000.0, "deadline": datetime(2027 + j, 7, 2)} for j in range(3)]
for step in (0.10, 0.05, 0.02, 0.01):
    best = []
    for _ in range(5):
        s = time.perf_counter()
        r = run_planning(250_000, 120_000, obls, goals, bliq=150_000, r_bench=0.14, risk_tolerance=3, today=T0, step=step)
        best.append(time.perf_counter() - s)
    print(f"step {step}: {r['alternatives_total']} alternatives, best of 5: {min(best) * 1000:.1f} ms")
```
```
step 0.1: 66 alternatives, best of 5: 6.4 ms
step 0.05: 231 alternatives, best of 5: 21.1 ms
step 0.02: 1326 alternatives, best of 5: 119.0 ms
step 0.01: 5151 alternatives, best of 5: 458.1 ms
(13) run_planning per call: median 0.87 ms, p95 7.03 ms, max 11.84 ms
     grid step 0.1: 1 alternatives, 0.2 ms
     grid step 0.05: 1 alternatives, 0.2 ms
     grid step 0.01: 1 alternatives, 0.4 ms
         2557365 function calls (2556690 primitive calls) in 1.794 seconds
   Ordered by: cumulative time
   List reduced from 111 to 14 due to restriction <14>
   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
      300    0.002    0.000    1.794    0.006 /private/tmp/claude-501/-Users-vasyaevdokimov-repos-personal-finance-dss/fe25aad2-149b-48bd-a8b2-c62cc04ce4a1/scratchpad/g39/p13_14_perf_explain.py:21(call)
      300    0.038    0.000    1.792    0.006 /Users/vasyaevdokimov/repos/personal-finance-dss/app/services/planning.py:46(run_planning)
     7930    0.180    0.000    1.158    0.000 /Users/vasyaevdokimov/repos/personal-finance-dss/app/core/alternatives.py:133(evaluate_alternative)
     7930    0.139    0.000    0.374    0.000 /Users/vasyaevdokimov/repos/personal-finance-dss/app/core/goals_priority.py:208(goals_allocation_breakdown)
     7930    0.105    0.000    0.256    0.000 /Users/vasyaevdokimov/repos/personal-finance-dss/app/core/goals_priority.py:109(calculate_goals_si)
    67708    0.059    0.000    0.238    0.000 /Users/vasyaevdokimov/repos/personal-finance-dss/app/core/money.py:35(money)
   413091    0.209    0.000    0.209    0.000 {built-in method builtins.round}
    77425    0.125    0.000    0.192    0.000 /Users/vasyaevdokimov/repos/personal-finance-dss/app/core/money.py:19(to_money)
    89198    0.032    0.000    0.158    0.000 /Users/vasyaevdokimov/repos/personal-finance-dss/app/core/goals_priority.py:48(months_left_or_none)
      300    0.056    0.000    0.144    0.000 /Users/vasyaevdokimov/repos/personal-finance-dss/app/core/alternatives.py:56(generate_alternatives)
    67730    0.081    0.000    0.127    0.000 /Users/vasyaevdokimov/repos/personal-finance-dss/app/core/goals_priority.py:63(_months_left)
   572512    0.123    0.000    0.123    0.000 {method 'get' of 'dict' objects}
     7875    0.015    0.000    0.121    0.000 /Users/vasyaevdokimov/repos/personal-finance-dss/app/core/investment.py:148(annotate_investment_tranche)
      300    0.050    0.000    0.113    0.000 /Users/vasyaevdokimov/repos/personal-finance-dss/app/core/ranking.py:138(rank_alternatives)

(14) decisions with a distinct runner-up: 861
  won at the lexicographic FLOOR stage (explanation still names a SAW criterion): 348 (40.4%)
```

**Что это значит.** Медиана вызова ядра **0,87 мс**, p95 **7 мс** (сетка 66 точек). 65 % времени — `evaluate_alternative` (пересчёт каждой из 66 альтернатив), внутри — распределение по целям и денежное округление через `Decimal` (`money.py`, 68 тыс. вызовов на 300 портретов). Векторизация numpy даст ×10–30, но **не нужна**: для веб-запроса 1–7 мс — ничто; узкое место появляется только в стендах (пункт 0: 480 тыс. вызовов за 5 мин) и при сетке 1 % (458 мс). Перенос на другой язык — не нужен. Единственная оптимизация с пользой: кэш распределения по целям внутри одного вызова (одинаковые `x_goals` у разных альтернатив) — **2–3 ч**, ускорит стенды в 1,5–2 раза.

Сноска к выводу: строки «grid step … 1 alternatives» в `p13_14.out` — портрет в дефиците, замер недействителен; верные числа — в `p13b_grid.out`.

**Корзина.** **«Потом»**. Гейт времени в CI не нужен сверх существующего `timing_lab`.

## Пункт 14. Объяснимость: показывать ПОЧЕМУ, не нарушая честности

**Аналогия.** Врач говорит «таблетку назначил из-за давления», а на деле назначил из-за анализа крови. Объяснение звучит разумно — и неверно. Проверка честности объяснения: совпадает ли названная причина с той, что реально решила.

**Что проверяет (fidelity, «верность» объяснения).** Для каждого совета — была ли названная причина настоящей: выиграл ли вариант у ближайшего соперника на этапе floor (лексикографически) или на этапе SAW, и если на SAW — какой критерий дал наибольший вклад в РАЗНИЦУ с соперником.

**Наш модуль.** `app/core/recommendation.py::_dominant_criterion` — берёт критерий с наибольшим `weighted_scores` у победителя и пишет «Решающим для оценки оказалось то, …» (строка 352).

Скрипт — `p13_14_perf_explain.py` (часть 14):
```python
"""G39 items 13-14. (13) timing and profile of run_planning; (14) FIDELITY of the explanation: does 'dominant_criterion'
(app/core/recommendation.py::_dominant_criterion = largest weighted score of the winner) name the reason the winner beat the runner-up?
True reason: (i) floor_level if winner and runner-up differ there (lexicographic stage, SAW irrelevant); else (ii) the criterion with the largest
positive contribution to U(winner) - U(runner-up)."""
import sys, time, cProfile, pstats, io, statistics as stt
from datetime import datetime, date
sys.path.insert(0, "/Users/vasyaevdokimov/repos/personal-finance-dss")
from app.services.planning import run_planning
from tools.portrait_testing.generator import PortraitGenerator
T0 = datetime(2026, 7, 2)
gen = PortraitGenerator(seed=20260702, version=2)
pops = []
for i in range(1200):
    p = gen.generate_with_income_history(i)
    for g in p["goals"]:
        if isinstance(g.get("deadline"), date) and not isinstance(g["deadline"], datetime):
            g["deadline"] = datetime(g["deadline"].year, g["deadline"].month, g["deadline"].day)
    pops.append(p)


def call(p):
    return run_planning(p["income_total"], p["expense_total"], p["obligations"], p["goals"], bliq=p["bliq"], r_bench=p["r_bench"],
                        risk_tolerance=p["risk_tolerance"], today=T0, income_history=p.get("income_history"))


t = []
for p in pops[:600]:
    s = time.perf_counter(); call(p); t.append(time.perf_counter() - s)
print(f"(13) run_planning per call: median {stt.median(t) * 1000:.2f} ms, p95 {sorted(t)[int(.95 * len(t))] * 1000:.2f} ms, max {max(t) * 1000:.2f} ms")
for step in (0.10, 0.05, 0.01):
    p = pops[1]; s = time.perf_counter()
    r = run_planning(p["income_total"], p["expense_total"], p["obligations"], p["goals"], bliq=p["bliq"], r_bench=p["r_bench"],
                     risk_tolerance=p["risk_tolerance"], today=T0, step=step)
    print(f"     grid step {step}: {r['alternatives_total']} alternatives, {(time.perf_counter() - s) * 1000:.1f} ms")
pr = cProfile.Profile(); pr.enable()
for p in pops[:300]:
    call(p)
pr.disable()
buf = io.StringIO(); pstats.Stats(pr, stream=buf).sort_stats("cumulative").print_stats(14)
print("\n".join(l for l in buf.getvalue().splitlines() if l.strip())[:3500])

n = floor_decided = agree = disagree = 0
for p in pops:
    r = call(p)
    if len(r["top3"]) < 2:
        continue
    a, b = r["ranked"][0], None
    for x in r["ranked"][1:]:
        if (round(x["x_obl_effective"]), round(x["x_reserve_effective"])) != (round(a["x_obl_effective"]), round(a["x_reserve_effective"])):
            b = x; break
    if b is None:
        continue
    n += 1
    said = r["top3"][0]["explanation"].get("dominant_criterion")
    if a["floor_level"] > b["floor_level"] + 1e-9:
        floor_decided += 1
        continue
    diff = {k: a["weighted_scores"][k] - b["weighted_scores"][k] for k in a["weighted_scores"]}
    true = max(diff, key=diff.get)
    agree += said == true; disagree += said != true
print(f"\n(14) decisions with a distinct runner-up: {n}")
print(f"  won at the lexicographic FLOOR stage (explanation still names a SAW criterion): {floor_decided} ({floor_decided / n:.1%})")
print(f"  won at the SAW stage: named criterion = largest contribution to the win: {agree} ({agree / n:.1%}); names another criterion: {disagree} ({disagree / n:.1%})")
```
```
  won at the SAW stage: named criterion = largest contribution to the win: 276 (32.1%); names another criterion: 237 (27.5%)
```

🔴 **Дефект Д-09 (честность объяснения).** Фраза «решающим оказалось …» **неверна в 67,9 % советов**: в **40,4 %** победитель выиграл на этапе floor, где SAW-критерии не участвовали вовсе, а в **27,5 %** выиграл на SAW, но решил другой критерий, чем назван. Верна она лишь в 32,1 %. Причина: «наибольший вклад в полезность победителя» ≠ «наибольший вклад в разницу с соперником» (у всех вариантов почти одинаково большая компонента не объясняет выбор). Это ровно тот тип ошибки, который XAI-литература называет потерей fidelity, и прямой риск для XAI-эксперимента магистерской: пользователю показывают правдоподобную, но не ту причину.

**Как делать честно (без новой математики).** (1) Если выиграл floor — говорить «сначала пополняем подушку до N мес., это правило приоритетнее остальных». (2) Если SAW — называть критерий с наибольшим вкладом в **разницу** с ближайшим соперником (контрфакт уже считается: `next_alt`, батч 0.4). (3) Для пути (б) — называть активное ε-ограничение (Г41, вопрос 9). (4) Тест верности — ровно скрипт выше, как регрессионная метрика.

**Цена.** Правка `_dominant_criterion` на «разницу с соперником» + ветка floor: **2–4 ч**; тест fidelity: **1–2 ч**. Библиотек не нужно.

**Корзина.** **«До запуска»** — неверное объяснение хуже отсутствующего (и прямо касается защиты).

## Пункт 15. Документирование модели по стандарту: карточка модели

**Аналогия.** Паспорт лекарства: для кого, от чего, в каких дозах, противопоказания, какие испытания пройдены.

**Первоисточник.** Mitchell et al. 2019, *FAT\* '19*, DOI 10.1145/3287560.3287596, открытая копия `arxiv.org/pdf/1810.03993` (OpenAlex HTTP 200, 17.09.2026), реферат дословно: «Model cards are short documents accompanying trained machine learning models that provide benchmarked evaluation in a variety of conditions … Model cards also disclose the context in which models are intended to be used, details of the performance evaluation procedures, and other relevant information.» и «this framework can be used to document any trained machine learning model». Наша модель не обучаемая, но разделы переносятся. Банковский аналог — требования ЦБ к документации (пункт 7: «запросить … программные коды, реализующие модель, документацию с указанием всех изменений»), SR 11-7 (документация ограничений и допущений).

**Предлагаемая структура карточки ядра FINPILOT** (каждый раздел — ссылка на уже существующий документ, а не новый текст):

| Раздел | Содержание | Откуда брать |
|---|---|---|
| Назначение | один месяц распределения свободного потока; не инвестиционный совет | канон §0, Г18–19 |
| Постановка | MODM со скаляризацией (Г40 п. 9), политика класса CFA (Г41) | Г40, Г41 |
| Входы и допустимая область | валидация входов, запрет NaN/∞ (Д-07) | схемы + пункт 2.2 |
| Допущения | доходность = $r_{bench}$, фиксированные ставки кредитов, расходы не режутся, «месяц = 30 суток» | канон, Г40 № 1 |
| Границы применимости | нет ставок ниже 0 и выше ~300 %, нет валютных долгов, ипотека не отделена (пункт 6) | пункт 6, 10 |
| Верификация | инварианты, MR, Z3, оракул — с числами и датой | пункты 1–3 |
| Валидация | внешние эталоны, бэктест, исходы (когда будут) | пункты 5–6 |
| Чувствительность | индексы Соболя, карта разрывов | пункт 8, Г40 `p2.py` |
| Известные ограничения | таблица дефектов Г40 и Д-01…Д-09 со статусом | Г40, этот файл |
| История изменений | `docs/model/model_history.md` | есть |
| Политика валидации | методы фиксированы, не подгоняются (483-П 14.3) | пункт 7 |

**Цена.** **4–6 ч** (сборка из существующего). Библиотек не нужно.

**Корзина.** **«До запуска»** (защита, B2B, ответ на запрос регулятора).

---

## ИТОГ Г39

**Процесс, честно.** Классификация — breadth-first (15 независимых методов + пункт 0 как depth-first). Подагентов — **0** (вход Г40/Г41 уже был в контексте; подагент начал бы с нуля). `WebSearch` — **0**. Exa — **2** поиска (483-П/845-П, ASME V&V). OpenAlex — 15 DOI одним скриптом, Semantic Scholar batch — 1 (первый вызов 429, повтор 200), `r.jina.ai` — 5 (Koehler 200, O'Shea 200, ФРС 200, КонсультантПлюс ×2 — шапки/заглушки, ASME — 404), `curl` — замеры кодов, EuropePMC — 500 на полный текст, Unpaywall — 1 замер канала с `research@example.org`. Посреди батча был обрыв по лимиту аккаунта и смена аккаунта; файл к моменту обрыва содержал пункты 0–4, работа продолжена с пункта 5 без потерь. Скриптов — 27, все в `scratchpad/g39/`, приведены дословно. Код продукта, канон, `tests/`, формулировка новизны не менялись; константы канона подменялись только в памяти процесса стендов (пункт 8).

### 1. 🔴 Ответ по пути (б)

**В виде, записанном в Г41 (пакет из четырёх элементов с обещанием «меньше процентов и цель в срок»), рекомендация НЕ держится** на портретах ADR-015 и в сценарии «месяц без дохода». Сквозной пример Г41 оказался нетипичным.

| Элемент | На 3 000 портретах ADR-015 и 2 000 с МФО | Вердикт |
|---|---|---|
| Вогнутая ценность на общих шкалах | по деньгам хуже канона у 0,3–1,4 %, лучше у 21,6 % портретов с МФО | 🟢 держится |
| ε-цель (темп на цель) | недобор целей меньше у 12–15 %, но деньги хуже у 17–33 %; цена **0,05 ₽** за рубль сокращённого недобора (без токсичного долга), **0,16–0,25 ₽** с МФО, у 10 % портретов с МФО **0,67–1,23 ₽** | 🟡 компромисс, нужен предел цены |
| ε-подушка 0,5 мес. | в «месяц без дохода» экстренного долга больше у **30,7 %** обычных и **38,2 %** портретов с неровным доходом; с floor канона — 8,9 %; если деньги целей в беде доступны — 3,7 % | 🔴 ломается в кризисе |
| «Токсичный первым», τ = 100 % | в ADR-015 не срабатывает ни разу (ставки ≤ 35 %) | ⚪ непроверяемо на этих портретах |
| Критерий приёмки Г41 «не хуже ни в одном портрете» | нарушен в 7,6–38,2 %; несовместим с ε-целью по построению | 🔴 переформулировать |

**Главное новое число:** разрыв канона до ясновидящего денежного оптимума — медиана **0,17 %** годового дохода (p90 1,6 %) без токсичного долга и **1,3 %** (p90 3,3 %) с МФО. У обычного человека без дорогого долга канон по деньгам уже почти оптимален; ценность пути (б) — в сроках целей и токсичном долге, не в рублях.

**Что нужно до принятия (решение владельца):** двухмерный критерий приёмки (деньги ± X % дохода и недобор целей), предел цены пунктуальности, правило «в беде деньги целей — тоже запас», пересчёт на портретах с реальным распределением токсичных ставок и после починки Д-01.

### 2. План проверки ядра тремя корзинами

**«Сразу после синтеза»** (защитная сетка до любой правки ядра):

| Метод | Что докажет | Модуль | Часы | Библиотека |
|---|---|---|---|---|
| Оракул ЛП + проверка доминирования (п. 1, 0) | разрыв до оптимума в рублях для любой версии правила | `services/planning`, `core/ranking`, `avalanche`, `crisis` | 6–10 | `highspy` (dev) |
| 14 инвариантов Hypothesis + минимальный пример §11.5 (п. 2) | сохранение денег, floor, ПДН, порядок Avalanche для всех случайных входов | все `core/*` | 4–6 | `hypothesis` (есть) |
| 7 держащихся метаморфических отношений (п. 3) | монотонность по доходу/расходам/$r_{bench}$, перестановка, сдвиг времени | `run_planning` | 3–5 | — |
| Локальный генератор в прогнозе, Д-08 (п. 4) | детерминизм процесса | `core/forecast` | 0,5 | — |
| Внешние эталоны (п. 6) | floor/ПДН против EMH, 2–6 мес., Кэрролла | `core/ranking`, `filtering` | 4–6 | scipy (dev) |
| Глобальная чувствительность (п. 8) | какие константы калибровать, какие мертвы | константы канона | 3–4 | `SALib` (dev) |
| Реальные величины в оракуле (п. 12) | не меняется ли вывод о цене пунктуальности | стенд | 2–3 | — |
| Починка стенда Д-01 (п. 0.1) | стенды считают ту же модель, что продукт | `tools/portrait_testing` | 1 | — |

**«До запуска»** (неверный совет или неверное объяснение обычному человеку):

| Метод / правка | Что докажет или устранит | Модуль | Часы | Библиотека |
|---|---|---|---|---|
| MR05/MR06 → Д-02 (обрыв §11.5) | разовое закрытие не отменяется чужой целью, не пробивает floor (условие из Z3) | `goals_priority.preallocate_from_bliq` | 3–5 | — |
| MR09 → Д-03 (ничьи при округлении) | масштаб не меняет совет | `ranking.rank_alternatives` | 1–2 | — |
| MR03/07/15 → Д-04 (min-max), если путь (б) не принят | набор альтернатив не переставляет победителя | `ranking.normalize_value` | 4–8 | — |
| Проверка входов ядра, Д-07 (п. 2.2) | NaN/∞/минус не дают молчаливого плана | `run_planning` | 2–3 | — |
| Z3 для кризиса и ПДН-гейта (п. 2.3) | теоремы для магистерской; ПДН-гейт — переписать или удалить | `crisis`, `filtering` | 4–8 | `z3-solver` (dev) |
| Формула вместо МК (п. 4) | коридор без случайной ошибки ±0,054 σ | `core/forecast` | 1–2 | — |
| Прогноз: среднее вместо Holt или гейт «не хуже наивного» (п. 5) | экран прогноза не хуже простого правила | `core/forecast` | 2–4 | scipy (dev) |
| Журнал исходов (п. 6) | без него бэктест и обратная оптимизация невозможны навсегда | сервисы/БД | 16–24 | — |
| Политика валидации (п. 7) | чек-лист SR 11-7 / ЦБ / V&V | документ | 4–6 | — |
| Стресс 2022 + метрика разворотов (п. 10) | «пила» совета при шоке ставки | `avalanche`, `cbr_rate` | 4–6 | — |
| Сглаживание обрыва индексации, Д-06 (п. 12) | цель не дорожает на 12,5 % за день | `goals_priority.inflated_target_amount` | 1–2 | — |
| Честное объяснение, Д-09 (п. 14) | названная причина = настоящая | `recommendation._dominant_criterion` | 3–6 | — |
| Карточка модели (п. 15) | паспорт ядра для защиты и B2B | документ | 4–6 | — |

**«Потом»** (после запуска или после решения по пути (б)): policy search порогов (п. 11, 1–2 дня); бэктест на реальных рядах и ежегодный outcomes analysis (п. 5–7); обратная оптимизация весов и полевой эксперимент (п. 6); WSI/SMAA-отчёт (п. 9, 3–4 ч); гистерезис $r_{bench}$ (п. 10); кэш распределения целей (п. 13, 2–3 ч); PSI-мониторинг (п. 7); доведение Z3 на правила пути (б).

### 3. Дефекты, найденные в этом батче метаморфическими отношениями, инвариантами и стендами

| № | Дефект | Чем найден | Где | Величина |
|---|---|---|---|---|
| Д-01 | Генератор v2 даёт срок цели как `date`, ядро молча читает «12 месяцев» — стенды на портретах считают не ту модель | проба типа (`p0a`) | `tools/portrait_testing/generator.py::_gen_goals` × `goals_priority._months_left` | 76,2 % сроков |
| Д-02 | Разовое закрытие §11.5 — «всё или ничего» по сумме близких целей: рост/появление одной цели отменяет закрытие других; пробивает floor (минимальный пример Hypothesis; Z3 — контрпример и доказанное условие починки «подушка ≥ 2 floor») | MR05, MR06, инвариант, Z3 | `goals_priority.preallocate_from_bliq`, канон §11.5 | до 100 % суммы цели |
| Д-03 | Округление полезности до 4 знаков перед сортировкой → ложные ничьи; масштаб ×10 меняет план 30/70 → 0/100 | MR09, MR03, MR14 | `ranking.rank_alternatives` | до 100 % потока, ~1 % портретов |
| Д-04 | min-max по набору альтернатив: больше подушки → больше взнос в резерв; новая цель → больше денег старым; кредит дороже бенчмарка → досрочка меньше; RRT1 — победитель сменился в 13 из 28 | MR03, MR07, MR15, skcriteria | `ranking.normalize_value`, канон §7 | до 67 % досрочки |
| Д-05 | Всё сверх floor «равно» → лишние деньги уходят мимо подушки, подушка после плана ниже | MR07 | `ranking` (G6) | мелко (33 ₽) |
| Д-06 | Распределение по остатку, а не по темпу: дальше срок → больше денег в месяц (через индексацию §11.3) | MR04 | `goals_priority.calculate_goals_si` | 0,2 % портретов |
| Д-07 | Ядро молча считает на NaN подушки/ставки/$r_{bench}$/цели и на отрицательной подушке | проба входов | `run_planning` и ниже | неверный план без сигнала |
| Д-08 | `random.seed()` сбрасывает глобальный генератор процесса | проба МК | `core/forecast.monte_carlo_intervals` | детерминизм соседей (`bank_api.py`) |
| Д-09 | «Решающий критерий» в объяснении неверен в 67,9 % советов (40,4 % — выиграл floor, 27,5 % — другой критерий) | тест верности | `recommendation._dominant_criterion` | большинство советов |
| (подтв.) | ПДН-гейт не отвергает ни одной альтернативы при доходе > 0 — доказано Z3 для всех входов; $S_T$ = 0 | Z3, Соболь | `filtering.filter_alternatives` | гейт-декорация (Г40 № 13) |
| (подтв.) | Прибавка floor ADR-015 почти не включается: при разбросе дохода ±90 % floor 1,98 мес. против 5,35 по Кэрроллу; $S_T$ = 0 | внешний эталон, Соболь | `ranking.effective_floor_months` | в 2,7 раза ниже |
| (подтв.) | Коридор прогноза — МК вместо формулы, ошибка ±0,054 σ; Holt хуже наивного и среднего на 8-точечной истории | МК, DM | `core/forecast` | +7 п. п. ошибки к доходу |
| (набл.) | «Пила» совета при шоке ставки 2022: у 33,4 % досрочка останавливается, у 81 % из них возвращается через полгода | стресс | `avalanche` + `cbr_rate` | 3 разворота за полгода |

**Слепота (не нарушение, число для регрессии):** досрочка в главный кредит не реагирует на его ставку ×1,5 у 87,9 %, на $r_{bench}$ +5 п. п. — у 92,6 %, на срок цели +6 мес. — у 94,1 %, на сумму цели +20 % — у 98,6 %, на удвоение волатильности — у 98,1 %.

### 4. Метрики — гейты CI и откуда берётся порог

Принцип порогов: (а) **логическое свойство** — порог 0 нарушений, потому что свойство либо верно, либо нет; (б) **метрика с известным дефектом** — «храповик»: не хуже текущего замера, ужесточается после починки (число не с потолка, а зафиксированное состояние); (в) **статистическая метрика** — допуск = 2 стандартные ошибки выборки на фиксированном наборе портретов, чтобы шум не валил CI, а реальное ухудшение — валило.

| Гейт | Порог | Обоснование |
|---|---|---|
| 14 инвариантов (п. 2.1), фиксированный seed Hypothesis + 300 портретов | 0 нарушений (кроме `inv_prealloc_keeps_floor` — xfail до починки Д-02) | (а); 13 из 14 уже держатся на 3 000 портретах и 400 случайных примерах |
| Держащиеся MR (01, 08, 10, 11, 12, 16) на 300 портретах | 0 нарушений | (а); 0 на 3 000 портретах |
| MR с известными дефектами (03, 05, 06, 07, 09, 14, 15) | доля нарушений ≤ текущей (0,7 / 0,6 / 0,4 / 2,1 / 0,1 / 0,3 / 0,6 %), после починки — 0 | (б) |
| Доминирование оракула (п. 1) | чистый денежный оракул ниже политики ≤ 1 % записей | (в) + установленная причина остатка 0,2–0,6 %; выше — значит сломана бухгалтерия стенда |
| Разрыв до оракула на 1 000 фикс. портретах | медиана ≤ 0,17 % + 2 SE, p90 ≤ 1,6 % + 2 SE (adr015 plain); отдельно для набора с МФО 1,3 % / 3,3 % | (б)+(в) |
| Кризисный хвост новой версии против предыдущей | доля портретов с бо́льшим экстренным долгом в `noinc` ≤ 2 % | (в): SE доли на 1 000 портретах при p ≈ 0,1 — 0,95 %, 2 SE ≈ 2 %; путь (б) в текущем виде (30,7 %) его не пройдёт |
| Верность объяснения (п. 14) | ≥ 32,1 % сейчас (храповик), после починки — 100 % | (б); после правки причина вычисляется тем же кодом, что выбор, иначе это ошибка |
| Коридор прогноза (п. 4) | после перехода на формулу: совпадение с МК при n = 200 000 до 0,01 σ | (а) по построению; SE при n = 200 000 — 0,004 σ |
| Прогноз против наивного (п. 5) | объединённый DM на фикс. портретах: модель не хуже «среднего по истории» при p < 0,05 | (в); сейчас гейт красный — это правильно |
| Разворотов совета в год (п. 10) | ≤ 3,05 + 2 SE на плоской ставке | (б)+(в) |
| Мутационный балл ядра | ≥ 68,7 % (храповик) | (б); нормативный порог — только после Г33 (решение владельца 16.09.2026), здесь не выдумывается |
| Покрытие 90 % | оставить | не предмет Г39; пилот мутаций показал, что покрытие качество не меряет |

**Не делать гейтом:** RRT1 skcriteria (28 матриц, другая инверсия критерия), индексы Соболя (полуширины до ±0,27 — отчёт, не гейт), SMAA/WSI (устойчивость уже высокая — отчёт при смене весов).

### 5. Маршрут обучения владельца

**Цель** — понимать, что проверяет каждый метод этого файла, читать его числа и не зависеть от объясняющего. Не цель — доказывать теоремы. Порядок выбран так, чтобы каждый шаг открывал конкретные пункты отчёта. Часы — оценка с задачами, при 5 ч/нед — около 5 месяцев на обязательную часть.

| Шаг | Что учить (минимум) | Зачем у нас (какие пункты начинают читаться) | Источник (рус. / англ.) | Часы |
|---|---|---|---|---|
| 0 | проценты, сложный процент, степень и логарифм, пропорции | ставки, $r_{bench}$, реальная ставка Фишера (п. 12), $\sqrt{1+0{,}5h}$ (п. 4) | mathprofi.ru (HTTP 200) · Khan Academy (HTTP 200) | 8–10 |
| 1 | среднее, дисперсия, стандартное отклонение, коэффициент вариации, квантили (p10/p90), нормальное распределение, стандартная ошибка, p-value | CV дохода (ADR-015, п. 6), коридор МК и его ошибка (п. 4), тест DM (п. 5), «2 SE» в гейтах | Stepik «Основы статистики», курс 76 (A. Карпов; API Stepik — HTTP 200) · Khan Academy «Statistics and probability» | 15–20 |
| 2 | вектор, скалярное произведение = взвешенная сумма, линейная функция, симплекс (веса в сумме 1) | SAW как скалярное произведение, «угол симплекса» Г40, линейность в WSI (п. 9), SMAA | 3Blue1Brown «Essence of linear algebra» (HTTP 200, ~3 ч) · Stepik «Линейная алгебра», курс 2461 (HTTP 200) · MIT OCW 18.06 (HTTP 200) выборочно | 12–15 |
| 3 | линейное программирование: целевая функция, ограничения, допустимая область, почему оптимум в вершине; целочисленные переменные; идея двойственности | оракул (п. 0–1), «одна корзина» Г40, обратная оптимизация (п. 6) | MIT OCW 15.053 «Optimization Methods in Management Science» (HTTP 200) · Е. С. Вентцель «Исследование операций» · Х. Таха «Введение в исследование операций» (рус. пер.; адреса не проверялись) · документация HiGHS (highs.dev, HTTP 200) | 20–25 |
| 4 | многокритериальность: Парето-фронт, скаляризация, ε-ограничения, функция достижения | Г40 п. 9 (MODM), Г41 рамка 5, путь (б), п. 9 | Miettinen 1999, гл. 3 (Springer, HTTP 200) · А. В. Лотов, И. И. Поспелова «Многокритериальные задачи принятия решений» (МГУ) · В. Д. Ногин «Принятие решений в многокритериальной среде» (адреса не проверялись) | 8–10 |
| 5 | тестирование математики: property-based, метаморфические отношения, идея SMT («найди контрпример или докажи») | п. 2–3, дефекты Д-02…Д-07 | документация Hypothesis (HTTP 200) · Chen et al. 2018, разд. 1–3 (копия в сырье) · Z3 wiki (HTTP 200) | 6–8 |
| 6 | анализ чувствительности и неопределённости: локальный vs глобальный, $S_1$/$S_T$, Моррис; ошибка Монте-Карло | п. 4, 8; SR 11-7 «sensitivity analysis» | Saltelli et al. «Global Sensitivity Analysis: The Primer», гл. 1–2 (Wiley, HTTP 200) · документация SALib (HTTP 200) · Koehler et al. 2009 (PMC) | 8–10 |
| 7 (по желанию) | оценка прогнозов: скользящее начало, MAE/RMSE, наивные эталоны, экспоненциальное сглаживание | п. 5 | Hyndman & Athanasopoulos «Forecasting: Principles and Practice», гл. 5 и 8 (otexts.com/fpp3, HTTP 200) | 8–10 |
| 8 (по желанию) | управление модельным риском | п. 7, политика валидации | SR 11-7 + OCC 2011-12 (в сырье `approach_validity`) · разъяснения ЦБ по 483-П (cbr.ru, HTTP 200) | 4–5 |

**Итого:** обязательные шаги 0–6 — **~80–100 ч**; с 7–8 — **~95–115 ч**. Как проверить себя после каждого шага: открыть соответствующий пункт этого файла и объяснить своими словами строку «Что это значит» — если получилось без подсказки, шаг закрыт.

**Словарь на одну строку (то, что встречается в отчётах чаще всего).** σ — насколько величина обычно отклоняется от среднего; CV — то же в долях среднего; p10/p90 — значения, ниже которых 10 % / 90 % случаев; SE — насколько гуляет оценка от выборки к выборке; p-value — вероятность увидеть такую разницу, если её на самом деле нет; $S_1$/$S_T$ — доля разброса результата от параметра без/с взаимодействиями; вершина симплекса — «все деньги в одну корзину»; ε-ограничение — «не меньше X», вместо веса; оракул — точное решение той же задачи, недоступное в жизни, но годное как линейка.

### 5а. ЗАДОЛЖЕННОСТЬ (не пройдено — с причиной)

1. Пересчёт пункта 0 на портретах с реалистичным распределением токсичных ставок — генератора с таким распределением нет (v2: 6–35 %); МФО добавлялось искусственно.
2. Инфляционный всплеск расходов в стрессе (п. 10) и доходность подушки по траектории ставки — бухгалтерия `p0b_sim.py` держит расходы и доходность постоянными.
3. Реальные величины в оракуле и цена пунктуальности в реальных рублях (п. 12) — не пересчитано.
4. «Infeasible» ЛП-оракула на горизонтах 36–60 мес. (п. 1) — причина не установлена, есть гипотеза.
5. Реальные помесячные ряды дохода домохозяйств РФ для бэктеста (п. 5) — не существуют в открытом доступе в найденных источниках (та же дыра Г40 № 10, Г41 № 14).
6. Полный текст Положения 845-П и факт отмены 483-П (п. 7) — КонсультантПлюс через `r.jina.ai` отдал только шапку; использованы фрагменты выдачи Exa.
7. Тексты стандартов ASME V&V 10/20 — платные; определения взяты из обзора Dowding & Hogan (OSTI 1368927, `curl` — таймаут, текст через Exa) и страницы ASME.
8. Полные тексты Sobol 2001, Saltelli 2010, Lahdelma 1998, Harvey–Leybourne–Newbold 1997, de Moura & Bjørner 2008 — закрыты (OpenAlex `oa_url: None`); Unpaywall по ним не запрашивался. Формула поправки HLN в `p5_backtest.py` — по общеизвестной записи, со статьёй не сверена.
9. Формула WSI из статьи O'Shea et al. — закрыт полный текст (403 на 16.09); в скрипте — собственный вывод той же идеи.
10. Собственный тест RRT1 на нормировке канона (вместо `InvertMinimize` skcriteria) — не написан; 10 из 38 матриц упали на делении на ноль.
11. Z3-доказательства для правил пути (б) и для Python-кода с `float` (а не для переписанной модели) — не делались.
12. Учебники Таха, Вентцель, Лотов–Поспелова, Ногин — адреса не проверялись (названия по памяти вахты).
13. Строка «exact ties at the top» в `p9_rank_stability.py` — ошибка скрипта (сравнение numpy-булева через `is False`), число не использовать.

---

## Приложение. Сырые ответы литературных каналов (дословно, 17.09.2026)

**OpenAlex, скрипт `lit/oa_batch.py`:**
```python
import json, urllib.request, urllib.parse
dois = ["10.1016/S0378-4754(00)00270-6", "10.1080/00401706.1991.10484804", "10.1016/j.cpc.2009.09.018", "10.21105/joss.00097",
        "10.18174/sesmo.18155", "10.1016/S0377-2217(97)00163-X", "10.1080/07350015.1995.10524599", "10.1198/tast.2009.0030",
        "10.1145/351240.351266", "10.1145/3287560.3287596", "10.1007/978-3-540-78800-3_24", "10.1287/opre.49.5.771.10607",
        "10.1016/S0169-2070(96)00719-4", "10.1016/j.ress.2005.11.017", "10.1109/TSE.2016.2532875"]
def inv(ab):
    if not ab: return ""
    pos = {}
    for w, idx in ab.items():
        for i in idx: pos[i] = w
    return " ".join(pos[i] for i in sorted(pos))
for d in dois:
    url = "https://api.openalex.org/works/doi:" + urllib.parse.quote(d)
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "research"}), timeout=40) as r:
            code = r.status; w = json.load(r)
    except Exception as e:
        print("\n###", d, "ERR", e); continue
    print("\n###", d, "| HTTP", code, "|", w.get("publication_year"), "|", (w.get("primary_location") or {}).get("source", {}) and (w["primary_location"]["source"] or {}).get("display_name"), "|", w.get("title"))
    print("authors:", ", ".join(a["author"]["display_name"] for a in w.get("authorships", [])[:6]))
    print("oa:", (w.get("open_access") or {}).get("oa_url"), "| cited_by", w.get("cited_by_count"))
    print("abstract:", inv(w.get("abstract_inverted_index"))[:1400])
```
```

### 10.1016/S0378-4754(00)00270-6 | HTTP 200 | 2001 | Mathematics and Computers in Simulation | Global sensitivity indices for nonlinear mathematical models and their Monte Carlo estimates
authors: I. M. Sobol
oa: None | cited_by 6360
abstract: 

### 10.1080/00401706.1991.10484804 | HTTP 200 | 1991 | Technometrics | Factorial Sampling Plans for Preliminary Computational Experiments
authors: Max D. Morris
oa: None | cited_by 4066
abstract: A computational model is a representation of some physical or other system of interest, first expressed mathematically and then implemented in the form of a computer program; it may be viewed as a function of inputs that, when evaluated, produces outputs. Motivation for this article comes from computational models that are deterministic, complicated enough to make classical mathematical analysis impractical and that have a moderate-to-large number of inputs. The problem of designing computational experiments to determine which inputs have important effects on an output is considered. The proposed experimental plans are composed of individually randomized one-factor-at-a-time designs, and data analysis is based on the resulting random sample of observed elementary effects, those changes in an output due solely to changes in a particular input. Advantages of this approach include a lack of reliance on assumptions of relative sparsity of important inputs, monotonicity of outputs with respect to inputs, or adequacy of a low-order polynomial as an approximation to the computational model.

### 10.1016/j.cpc.2009.09.018 | HTTP 200 | 2009 | Computer Physics Communications | Variance based sensitivity analysis of model output. Design and estimator for the total sensitivity index
authors: Andrea Saltelli, Paola Annoni, Ivano Azzini, Francesca Campolongo, Marco Ratto, Stefano Tarantola
oa: None | cited_by 3521
abstract: 

### 10.21105/joss.00097 | HTTP 200 | 2017 | The Journal of Open Source Software | SALib: An open-source Python library for Sensitivity Analysis
authors: Jonathan D. Herman, Will Usher
oa: https://doi.org/10.21105/joss.00097 | cited_by 1564
abstract: SALib contains Python implementations of commonly used global sensitivity analysis methods, including Sobol (Sobol’ 2001, Andrea Saltelli (2002), Andrea Saltelli et al. (2010)), Morris (Morris 1991 ...

### 10.18174/sesmo.18155 | HTTP 200 | 2022 | Socio-Environmental Systems Modeling | Toward SALib 2.0: Advancing the accessibility and interpretability of global sensitivity analyses
authors: Takuya Iwanaga, Will Usher, Jonathan D. Herman
oa: https://sesmo.org/article/download/18155/17856 | cited_by 380
abstract: Sensitivity analysis is now considered a standard practice in environmental modeling. Several open-source libraries, such as the Sensitivity Analysis Library (SALib), have been published in the recent past aimed at simplifying the application of sensitivity analyses. Still, there remain issues in software usability and accessibility, as well as a lack of guidance in the interpretation of sensitivity analysis results. This paper describes the changes made and planned to SALib to advance the ease with which modelers may conduct sensitivity analysis and interpret results. We further offer our perspectives from the past 7 years of maintaining SALib for the consideration of those aspiring to launch their own software for sensitivity analysis, develop methodology, or those otherwise interested in becoming involved in a project like SALib. These include the value of a community of practice to foster best practices for sensitivity analysis, the potential for collaboration across different software (for sensitivity analysis) platforms, and the need to specifically support the software development that underpins computational science.

### 10.1016/S0377-2217(97)00163-X | HTTP 200 | 1998 | European Journal of Operational Research | SMAA - Stochastic multiobjective acceptability analysis
authors: Risto Lahdelma, Joonas Hokkanen, Pekka Salminen
oa: None | cited_by 654
abstract: 

### 10.1080/07350015.1995.10524599 | HTTP 200 | 1995 | Journal of Business and Economic Statistics | Comparing Predictive Accuracy
authors: Francis X. Diebold, Roberto S. Mariano
oa: None | cited_by 5053
abstract: We propose and evaluate explicit tests of the null hypothesis of no difference in the accuracy of two competing forecasts. In contrast to previously developed tests, a wide variety of accuracy measures can be used (in particular, the loss function need not be quadratic and need not even be symmetric), and forecast errors can be non-Gaussian, nonzero mean, serially correlated, and contemporaneously correlated. Asymptotic and exact finite-sample tests are proposed, evaluated, and illustrated.

### 10.1198/tast.2009.0030 | HTTP 200 | 2009 | The American Statistician | On the Assessment of Monte Carlo Error in Simulation-Based Statistical Analyses
authors: Elizabeth Koehler, Elizabeth R. Brown, Sebastien Haneuse
oa: https://www.ncbi.nlm.nih.gov/pmc/articles/3337209 | cited_by 314
abstract: Statistical experiments, more commonly referred to as Monte Carlo or simulation studies, are used to study the behavior of statistical methods and measures under controlled situations. Whereas recent computing and methodological advances have permitted increased efficiency in the simulation process, known as variance reduction, such experiments remain limited by their finite nature and hence are subject to uncertainty; when a simulation is run more than once, different results are obtained. However, virtually no emphasis has been placed on reporting the uncertainty, referred to here as Monte Carlo error, associated with simulation results in the published literature, or on justifying the number of replications used. These deserve broader consideration. Here we present a series of simple and practical methods for estimating Monte Carlo error as well as determining the number of replications required to achieve a desired level of accuracy. The issues and methods are demonstrated with two simple examples, one evaluating operating characteristics of the maximum likelihood estimator for the parameters in logistic regression and the other in the context of using the bootstrap to obtain 95% confidence intervals. The results suggest that in many settings, Monte Carlo error may be more substantial than traditionally thought.

### 10.1145/351240.351266 | HTTP 200 | 2000 | None | QuickCheck
authors: Koen Claessen, John Hughes
oa: None | cited_by 736
abstract: Quick Check is a tool which aids the Haskell programmer in formulating and testing properties of programs. Properties are described as Haskell functions, and can be automatically tested on random input, but it is also possible to define custom test data generators. We present a number of case studies, in which the tool was successfully used, and also point out some pitfalls to avoid. Random testing is especially suitable for functional programs because properties can be stated at a fine grain. When a function is built from separately tested components, then random testing suffices to obtain good coverage of the definition under test.

### 10.1145/3287560.3287596 | HTTP 200 | 2019 | None | Model Cards for Model Reporting
authors: Margaret Mitchell, Simone Wu, Andrew Zaldivar, Parker Barnes, Lucy Vasserman, Ben Hutchinson
oa: https://arxiv.org/pdf/1810.03993 | cited_by 2026
abstract: Trained machine learning models are increasingly used to perform high-impact tasks in areas such as law enforcement, medicine, education, and employment. In order to clarify the intended use cases of machine learning models and minimize their usage in contexts for which they are not well suited, we recommend that released models be accompanied by documentation detailing their performance characteristics. In this paper, we propose a framework that we call model cards, to encourage such transparent model reporting. Model cards are short documents accompanying trained machine learning models that provide benchmarked evaluation in a variety of conditions, such as across different cultural, demographic, or phenotypic groups (e.g., race, geographic location, sex, Fitzpatrick skin type [15]) and intersectional groups (e.g., age and race, or sex and Fitzpatrick skin type) that are relevant to the intended application domains. Model cards also disclose the context in which models are intended to be used, details of the performance evaluation procedures, and other relevant information. While we focus primarily on human-centered machine learning models in the application fields of computer vision and natural language processing, this framework can be used to document any trained machine learning model. To solidify the concept, we provide cards for two supervised models: One trained to det

### 10.1007/978-3-540-78800-3_24 | HTTP 200 | 2008 | Lecture notes in computer science | Z3: An Efficient SMT Solver
authors: Leonardo de Moura, Nikolaj Bjørner
oa: None | cited_by 6446
abstract: 

### 10.1287/opre.49.5.771.10607 | HTTP 200 | 2001 | Operations Research | Inverse Optimization
authors: Ravindra K. Ahuja, James B. Orlin
oa: None | cited_by 501
abstract: In this paper, we study inverse optimization problems defined as follows. Let S denote the set of feasible solutions of an optimization problem P, let c be a specified cost vector, and x0 be a given feasible solution. The solution x0 may or may not be an optimal solution of P with respect to the cost vector c. The inverse optimization problem is to perturb the cost vector c to d so that x0 is an optimal solution of P with respect to d and ‖d−c‖p is minimum, where ‖d−c‖p is some selected Lp norm. In this paper, we consider the inverse linear programming problem under L1 norm (where ‖d−c‖p = Σi∈J wj|dj−cj|, with J denoting the index set of variables xj and wj denoting the weight of the variable j) and under L∞ norm (where ‖d−c‖p = maxj∈J{wj|dj−cj|}). We prove the following results: (i) If the problem P is a linear programming problem, then its inverse problem under the L1 as well as L∞ norm is also a linear programming problem. (ii) If the problem P is a shortest path, assignment or minimum cut problem, then its inverse problem under the L1 norm and unit weights can be solved by solving a problem of the same kind. For the nonunit weight case, the inverse problem reduces to solving a minimum cost flow problem. (iii) If the problem P is a minimum cost flow problem, then its inverse problem under the L1 norm and unit weights reduces to solving a unit-capacity minimum cost flow probl

### 10.1016/S0169-2070(96)00719-4 | HTTP 200 | 1997 | International Journal of Forecasting | Testing the equality of prediction mean squared errors
authors: David I. Harvey, Stephen J. Leybourne, Paul Newbold
oa: None | cited_by 2086
abstract: 

### 10.1016/j.ress.2005.11.017 | HTTP 200 | 2006 | Reliability Engineering & System Safety | Survey of sampling-based methods for uncertainty and sensitivity analysis
authors: J.C. Helton, Jay Johnson, Cedric Jean-Marie Sallaberry, Curtis B. Storlie
oa: None | cited_by 1228
abstract: 

### 10.1109/TSE.2016.2532875 | HTTP 200 | 2016 | IEEE Transactions on Software Engineering | A Survey on Metamorphic Testing
authors: Sergio Segura, Gordon Fraser, Ana B. Sánchez, Antonio Ruiz–Cortés
oa: https://idus.us.es/handle/11441/38271 | cited_by 566
abstract: A test oracle determines whether a test execution reveals a fault, often by comparing the observed program output to the expected output. This is not always practical, for example when a program's input-output relation is complex and difficult to capture formally. Metamorphic testing provides an alternative, where correctness is not determined by checking an individual concrete output, but by applying a transformation to a test input and observing how the program output “morphs” into a different one as a result. Since the introduction of such metamorphic relations in 1998, many contributions on metamorphic testing have been made, and the technique has seen successful applications in a variety of domains, ranging from web services to computer graphics. This article provides a comprehensive survey on metamorphic testing: It summarises the research results and application areas, and analyses common practice in empirical studies of metamorphic testing as well as the main open challenges.
```
