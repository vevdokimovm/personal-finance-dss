# Г40 — Независимый математический аудит канона FINPILOT (сырьё, 17.09.2026)

> Объект: `docs/math_model.md` v3.9.0 (934 строки, прочитан целиком) + `app/core/*` + `docs/model/model_history.md`.
> Постановка: `docs/research/queue/GAP_QUEUE.md`, раздел «Г40–Г41», часть Г40, пункты 1–9.
> Режим: аудит. Канон, формулировка новизны и код продукта НЕ правятся. Скрипты — только в скрэтчпаде
> `/private/tmp/claude-501/-Users-vasyaevdokimov-repos-personal-finance-dss/fe25aad2-149b-48bd-a8b2-c62cc04ce4a1/scratchpad/g40/`.
> Подача для владельца: аналогия → суть → что значит для продукта → насколько серьёзно.
> Файл дописывается по одному пункту (`cat >>`), чтобы пережить обрыв.

**Состояние каналов, 17.09.2026 (замер curl, коды HTTP):** Crossref `api.crossref.org/works/DOI` — 200;
Unpaywall — 422 на адресе с `test@example.com` (сервис отвергает этот e-mail как невалидный, не отказ канала);
Semantic Scholar `/paper/DOI:` — 200; OpenAlex — 200; EuropePMC — 200; `r.jina.ai` (без браузерного UA) — 200;
Exa `mcp__exa__web_search_exa` — работает (выдача по Hwang & Masud 1979 получена); `pdftotext` — есть;
`.venv/bin/python` (CPython 3.13) — есть.

---

## Карта канона (шаг 1 метода)

Порядок вычисления, как он реально идёт в коде (`app/services/planning.py::run_planning`), со ссылками на канон:

| Шаг | Что считается | Канон | Код |
|---|---|---|---|
| 0 | $R_t = I_t - E_t - \sum P$ (поток месяца) | §3.2, стр. 154–157 | `planning.py:82`, `metrics.calculate_rt` |
| 1 | Если $R_t < -0{,}005$ → кризисный план, решётки нет | §12, стр. 488–501 | `planning.py:86,98`, `crisis.build_crisis_plan` |
| 2 | Разовое закрытие близких целей из $B^{liq}$ | §11.5, стр. 483–484 | `goals_priority.preallocate_from_bliq` |
| 3 | Слой разовых ходов из излишка | §14, стр. 556–583 | `surplus.build_surplus_plan` |
| 4 | Решётка долей $(\alpha_d,\alpha_r,\alpha_g)$ с шагом 0,1 → ≤66 точек | §4.3, стр. 194–199 | `alternatives.generate_alternatives` |
| 5 | Для каждой точки: Avalanche-разлив $x_d$ → $\delta P$; цели с кэпом → остаток в резерв; $R_t(a), L_t(a), D_t(a), S_n(a)$ | §5, §10.3–10.4, §11.3–11.4 | `alternatives.evaluate_alternative` |
| 6 | Фильтр $R_t(a)\ge0$, $D_t(a)\le\max(0{,}4;D_t)$, $L_t(a)\ge L_{min}$ | §6, стр. 238–257 | `filtering.filter_alternatives` |
| 7 | min-max по множеству, насыщение $L$ на $L^*$, SAW, лексикографический выбор (floor, U) | §7–9, стр. 261–322 | `ranking.rank_alternatives` |
| 8 | Разметка инвест-транша, вычет ИИС, график лавины | §13, §10.5 | `investment.py`, `amortization.py` |
| — | Прогноз Holt/SES + Монте-Карло | §15, «Обновление прогнозирования» | `services/forecasting.py` — **отдельный эндпоинт, в выбор плана не входит** |

Переменные решения: три доли $\alpha_d,\alpha_r,\alpha_g$ (сколько процентов свободных денег — на долг, в резерв, в цели).
Критерии — функции этих долей. Ограничения — §6. Выбор — лексикографический максимум.

---

## Пункт 1. Корректность постановки

### 1.1. Два критерия из четырёх — на самом деле один и тот же критерий 🔴

**Аналогия.** Судья на конкурсе ставит оценки по «красоте» и по «привлекательности», и это одно и то же, только
записанное двумя словами. Участник, сильный в этом, получает двойной балл.

**Суть.** Критерий ресурса после плана $R_t(a) = I - E - P_{new}(a)$ (§5.1, стр. 206) и критерий долговой
нагрузки $D_t(a) = P_{new}(a)/I$ (§5.3, стр. 216) оба зависят от одного и того же числа — нового суммарного
платежа $P_{new}$ ($I$ — доход, $E$ — расходы, постоянны для всех альтернатив). После min-max нормализации (§7, стр. 264):

$\hat R(a) = \dfrac{P_{max} - P_{new}(a)}{P_{max} - P_{min}}$ и $1-\hat D(a) = \dfrac{P_{max} - P_{new}(a)}{P_{max}-P_{min}}$ — **буква в букву одно и то же**.

Канон это видит, но называет мягко: «Естественная связь $R_t$–$D_t$ (досрочка улучшает обе) приемлема» (§5.4, стр. 221),
и в том же разделе (стр. 223–229) сам квалифицирует ровно такую ситуацию для пары $R$–$L$ как нарушение
non-redundancy по Roy (1996) с double counting весов. Пара $R$–$D$ — тот же дефект в чистом виде (корреляция 1,0, а не 0,9998).

**Число.** Скрипт `p1.py` (ниже), 3000 синтетических портретов, seed 20260917, `r_bench`=0,14: из 1410 портретов с
$R_t>0$ в 888 нормированные $\hat R$ и $1-\hat D$ совпали на всех альтернативах с точностью 0,0015; в остальных 549
расхождение — медиана 0,008, p90 0,033 — и происходит **только от округления** `Dt_new` до 4 знаков
(`alternatives.py:237`): диапазон $D$ между альтернативами в медиане всего 79 квантов по 0,0001.

**Что это значит для продукта.** Фактический вес «досрочки» в свёртке — $w_R + w_D$: консервативный 0,45,
умеренно-консервативный 0,45, сбалансированный 0,50, умеренно-агрессивный 0,50, агрессивный 0,50 (§9, стр. 314–318).
То есть «профиль риска» почти не меняет отношение к долгу, а заявленная монотонность весов (стр. 322,
«долг убывает к агрессивным 0.25→0.15») — артефакт записи: эффективный вес долга у агрессивного профиля
**не меньше**, чем у сбалансированного. Критериев в свёртке реально три, не четыре.

**Насколько серьёзно.** Средне. Сертификация экспертами проходила уже с этим дублем, то есть веса откалиброваны
«вместе с ним», и совет от этого не стал вредным. Но это ошибка постановки, которую рецензент магистерской
найдёт первой, потому что канон сам даёт для неё термин.

### 1.2. Жёсткие инварианты §6 никогда не срабатывают — фильтр пустой 🟡

**Аналогия.** Турникет на выходе из метро, который проверяет, что человек не вошёл обратно. Он «работает», но
отсечь в этом месте некого.

**Суть.** Досрочка может только уменьшить платёж: $P_{new}(a) \le P$. Значит $R_t(a) = I-E-P_{new} \ge R_t > 0$ и
$D_t(a) \le D_t$ для **любой** точки решётки. Оба «жёстких инварианта» (§6, стр. 245–246) выполняются автоматически;
третье ограничение выключено по умолчанию ($L_{min}=0$, стр. 247).

**Число.** `p1.py`: 1410 портретов с $R_t>0$, **0** портретов, где фильтр отклонил хоть одну альтернативу.

**Что это значит.** (а) Допустимое множество = вся решётка; вопрос «что при пустом допустимом множестве» в рабочем
режиме не возникает вовсе. (б) Заявка канона (§0, стр. 80–86), что конструкция — это «additive multi-attribute value
model accounting for veto» (Jiménez-Martín et al. 2015) и что некомпенсаторность «уже есть», **по коду не подтверждается**:
вето-интервалы пусты, реальная некомпенсаторность в модели есть только одна — лексикографический floor (§8).
(в) Инварианты полезны как страховка от будущих правок (например, если появится «взять кредит под цель»),
но это инварианты-тесты, а не ограничения задачи.

**Насколько серьёзно.** Для пользователя — никак. Для формулировки научной новизны и защиты — существенно:
утверждение «жёсткие ограничения + компенсаторная свёртка» надо переписать честно.

### 1.3. Одна величина — три разных определения ликвидности $L_t$ 🔴

Канон жёстко вводит $L_t = B^{liq}/\sum e$ — «запас», и отдельно запрещает прежнюю потоковую формулу v2.x (§3.3, стр. 159–163; §19, стр. 819; `CLAUDE.md`: «v2.x запрещена»). В продукте живут три версии:

| Где | Формула | Соответствие канону |
|---|---|---|
| План (`metrics.calculate_lt`, `alternatives.py:216`) | $(B^{liq}+x_r^{eff})/E$ | ✅ канон §3.3/§5.2 |
| Эндпоинт прогноза, поле `current.Lt` (`app/api/routes_planning.py:726`) | $R_t/(E+\sum P)$ | ❌ **формула v2.x**, запрещённая каноном |
| Эндпоинт прогноза, горизонт `forecast[h].Lt` (`services/forecasting.py:128`) | $B_{t+h}/E_{t+h}$, где $B$ — **накопления на целях** $\sum C_s$ (`routes_planning.py:722`) | ❌ канон прямо отделяет цели от подушки (§3.5, стр. 174–176) |
| Демо-витрина (`routes_demo.py:584`) | $B^{liq}/E$ | ✅ |

**Числовой пример** (`p1b.py`, блок A): доход 100 000 ₽, расходы 60 000 ₽, платежи 10 000 ₽, накопления на целях 100 000 ₽,
подушки нет. План скажет «ликвидность 0 месяцев». Эндпоинт прогноза покажет `current.Lt` = 30 000/70 000 = 0,43, а через
месяц `Lt` = 2,16 месяца — за счёт денег, лежащих на цели «машина».

**Насколько серьёзно.** Высоко для доверия: два экрана одного продукта называют разным числом одно и то же, и одно из
чисел — запрещённая каноном формула. Решение не портит (прогноз в выбор не входит), но пользователь видит противоречие.

### 1.4. В прогнозе «ресурс» — это запас плюс поток: двойной счёт 🔴

**Аналогия.** «Сколько у тебя свободных денег в месяц?» — «Зарплата минус траты, плюс всё, что на счету, плюс ещё раз зарплата минус траты».

**Суть.** Канон: «$R_t$ — поток периода, а не запас — баланс $B_t$ в ресурс НЕ входит (иначе двойной учёт уже накопленного)» (§3.2, стр. 156).
Код прогноза: `bt_running = bt_running*(1+r_m) + (cf_h - p_h)`, затем `rt_h = bt_running + cf_h - p_h` (`services/forecasting.py:124–125`)
— баланс, в который поток месяца уже вошёл, плюс тот же поток ещё раз.

**Число** (`p1b.py`, блок A, история дохода/расхода постоянна, `r_bench`=0): истинный поток ≈ 30 000 ₽/мес. Прогноз «Rt»:
159 586 → 189 290 → 218 957 ₽ на месяцах 1–3, т.е. в 5–7 раз больше и растёт на каждом шаге.
Блок C: при реальном потоке 10 ₽ в месяц прогноз «Rt» = 58 574 / 115 181 / 176 719 ₽. Сигнал о грядущем дефиците
(`deficit_alert`, `forecasting.py:156–167`) строится на этом же поле и при положительном балансе **почти никогда не сработает**.

**Насколько серьёзно.** Высоко для функции прогноза (FR-08 «первый месяц дефицита» практически выключен у всех, у кого есть
хоть какие-то накопления на целях). На выбор плана не влияет.

### 1.5. Канон и код по-разному определяют обеспеченность целей $S_n$ и распределение по целям 🔴

(а) **Формула.** Канон §11.3 (стр. 463): $S_n(a) = \dfrac{\sum_s (C_s+\Delta C_s)\,w_s u_s}{\sum_s T^{fut}_s\,w_s u_s}$ (накоплено плюс взнос, делённое на цель).
Код `goals_priority.calculate_goals_si` (стр. 157–162): $\dfrac{\sum_s \Delta C_s\,w_s u_s}{\sum_s (T^{fut}_s - C_s)\,w_s u_s}$ (только взнос, делённый на остаток).
Докстрока функции (стр. 116) приводит третий вариант с опечаткой «(Ss − ws)». Для ранжирования это не важно:
при фиксированном наборе целей обе формы — сдвиг и растяжение одной и той же суммы $\sum \Delta C_s w_s u_s$, и min-max их выравнивает.
Для показа пользователю числа разные: `p1b.py` блок D — код 0,073, канон 0,248 при одном и том же плане.

(б) **Перераспределение избытка — существенно.** Канон §11.4 (стр. 480): «Избыток сверх потребности цели перераспределяется на остальные».
Код: `x_goa_s = min(x_goals*share, remaining)` (стр. 157) — **не перераспределяет**; недолитое уходит в резерв через каскад ADR-009
(`alternatives.py:207–212`). Канон сам себе противоречит: §10.4 стр. 398 и раздел «Ре-роутинг» стр. 914–924 описывают как раз уход в резерв.

**Числовой пример** (`p1b.py`, блок D). Две цели: «курс» (рост дохода, 10 000 ₽, срок 6 мес.) и «машина» (материальная, осталось 800 000 ₽, срок 12 мес.).
Приоритеты: курс $3{,}0\cdot2 = 6$, машина $1{,}0\cdot1 = 1$ → доли 6/7 и 1/7.
- В цели направлено 20 000 ₽ → курс 10 000 (закрыт), машина 2 871 ₽, **7 129 ₽ ушли в подушку**, хотя машине нужно ещё 797 тыс.
- Направлено 60 000 ₽ → курс 10 000, машина 8 612 ₽, **41 388 ₽ (69 %) ушли в подушку**.

Человек видит план «60 000 ₽ на цели», а на цели реально идёт 18 612 ₽. Сама модель при этом «знает» это: $S_n$ почти не растёт
с $x_g$ после насыщения маленькой цели, поэтому варианты «в цели» теряют полезность — **систематический уклон против целей**
у всех, у кого есть одна маленькая срочная цель рядом с большой.

**Насколько серьёзно.** Высоко: денежный смысл плана расходится с подписью, и это тот же класс, что закрывал ADR-009 («план молча теряет деньги»), только теперь деньги не теряются, а молча меняют направление.

### 1.6. Кризисный режим использует другой floor, чем основной 🔴

Канон §8 (стр. 291–295): floor $F=1{,}0$ месяц при токсичном долге. Канон §12 (стр. 494) и код `crisis.py:36,54`: балансовый ход
считает floor = `RESERVE_FLOOR_MONTHS` = **2,0** всегда, без G8 и без волатильности.

**Числовой пример** (`p1c.py`). Доход 50 000 ₽, расходы 45 000 ₽, МФО: остаток 50 000 ₽ под 150 % годовых, платёж 10 000 ₽ → дефицит 5 000 ₽/мес.
Подушка 100 000 ₽ (2,2 месяца расходов).
- Основной режим для того же долга считает floor 1,0 месяц (`effective_floor_months` = 1.0).
- Кризисный режим: доступно сверх floor 2 мес. только 10 000 ₽ → закрыть МФО «нельзя» → совет **«сократите расходы на 5 000 ₽, реструктурируйте»** (`cut_required`).
- С floor 1,0 доступно 55 000 ₽ ≥ 50 000 → МФО закрывается целиком, платёж 10 000 ₽ исчезает, дефицит становится профицитом +5 000 ₽.
Модель советует человеку резать еду при 100 000 ₽ на счету под ~14 % и долге под 150 %. Эксперты в трёх раундах подряд в этой зоне
выбирали долг (§20, стр. 835–837) — правило G8 существует ровно против этого, но в кризисную ветку не протянуто.

**Насколько серьёзно.** Высоко, и бьёт по самой уязвимой группе.

### 1.7. Существование и единственность решения; мелкие несогласованности 🟢/🟡

- **Существование.** При $R_t > 0,005$ решётка непуста (минимум одна точка «всё в резерв»: `generate_alternatives` не отсекает $r$), фильтр пуст (1.2) → решение есть всегда. При $-0{,}005 \le R_t \le 0$ (`p1c.py`: $R_t$=0 и $-0{,}003$) возвращается одна альтернатива `deficit`, кризисный план не строится — формально корректно, по смыслу «распределять нечего».
- **Единственность.** Не гарантирована: `utility` округляется до 4 знаков **до** сортировки (`ranking.py:180`), ничьи разрешаются порядком генерации (устойчивая сортировка → меньшая доля долга, затем меньшая доля резерва). `p1c.py`: 58 из 1793 портретов (3,2 %) имеют точную ничью на первом месте между разными номинальными сплитами (часть из них — одинаковый эффективный план после дедупликации). Правило тай-брейка в каноне не записано.
- **$D_t$ при нулевом доходе.** Канон §3.4 и `metrics.calculate_dt`: 1,0 при живых платежах (G7). `alternatives.py:217`, `forecasting.py:129`, `routes_planning.py:727`: 0. В плане эта ветка недостижима ($I=0$ ⇒ $R_t\le0$ ⇒ кризис), в прогнозе — достижима.
- **Нумерация канона.** Ссылки внутри документа разъехались с заголовками: «профиль риска (§10)» (стр. 140) — профили в §9; «$r_{bench}$ … (§11)» (стр. 141, 207, 257, 572) — это §10; «категория … (§15)» (стр. 133, 181, 219) — это §11; «Floor … см. §21 п. 9» (стр. 635) — это §18 п. 9; в §15 подразделы названы 12.1/12.2 (стр. 589, 594). Символ $N$ означает и 1000 прогонов МК (стр. 103), и 10 «звёздочек» (стр. 197). Прогнозный раздел §15 описывает SES α=0,3, а код с v3.3.0 — Holt α=0,4 β=0,3 φ=0,9 (стр. 897–910 — дописка в конце файла, не в §15); сам канон на стр. 933 говорит «файл модели предполагается переименовать в math_model_v3_3_0.md», что противоречит шапке (стр. 3–7).
- **Прогноз не участвует в решении.** §0 (стр. 77) делает прогноз этапом 3 алгоритма, §16 считает его в сложности пайплайна. В коде `run_planning` прогноз не вызывается вовсе: он живёт на отдельном эндпоинте `/forecast`. Это нормально для продукта, но канон описывает иначе.

**Итог пункта 1.** Постановка разрешима всегда, но (i) из четырёх критериев независимых три, (ii) жёсткие ограничения декоративны,
(iii) в продукте три определения ликвидности и поток, смешанный с запасом, в прогнозе, (iv) распределение по целям в коде
не совпадает с каноном и незаметно уводит деньги целей в подушку, (v) кризисная ветка не знает про G8.

### Скрипты пункта 1 (дословно)

`p1.py`, `p1b.py`, `p1c.py` — в `/private/tmp/claude-501/-Users-vasyaevdokimov-repos-personal-finance-dss/fe25aad2-149b-48bd-a8b2-c62cc04ce4a1/scratchpad/g40/`. Запуск: `.venv/bin/python <путь>` из корня репозитория.


**p1.py**

```python
"""G40 p.1: definitional consistency checks on synthetic portraits (read-only use of app.core)."""
import random, sys
from datetime import datetime
sys.path.insert(0, "/Users/vasyaevdokimov/repos/personal-finance-dss")
from app.services.planning import run_planning
from app.services.forecasting import forecast_indicators
from app.core.goals_priority import calculate_goals_si

TODAY = datetime(2026, 9, 17)

def portrait(rng):
    inc = rng.choice([40_000, 60_000, 90_000, 150_000, 250_000])
    exp = inc * rng.uniform(0.35, 0.8)
    obls = []
    for k in range(rng.randint(0, 3)):
        amt = rng.uniform(20_000, 1_500_000)
        rate = rng.choice([0.09, 0.15, 0.22, 0.29, 0.35, 0.8, 1.5])
        n = rng.choice([12, 24, 60, 180])
        rm = rate / 12
        pay = amt * rm / (1 - (1 + rm) ** -n)
        obls.append({"id": f"o{k}", "name": f"L{k}", "amount": amt, "interest_rate": rate, "monthly_payment": pay})
    goals = []
    for s in range(rng.randint(0, 3)):
        m = rng.choice([2, 6, 12, 30, 48, 120, None])
        dl = None if m is None else datetime(2026 + (9 + m) // 12, (9 + m) % 12 + 1, 17)
        goals.append({"id": f"g{s}", "name": f"G{s}", "target_amount": rng.uniform(50_000, 3_000_000),
                      "current_amount": rng.uniform(0, 30_000), "deadline": dl,
                      "category": rng.choice(["income_growth", "safety", "material", "emotional"])})
    bliq = exp * rng.choice([0, 0.5, 1.5, 3, 8])
    return inc, exp, obls, goals, bliq

rng = random.Random(20260917)
n_pos = n_rej = n_rd_identical = n_rd_cases = 0
max_dev = 0.0
for _ in range(3000):
    inc, exp, obls, goals, bliq = portrait(rng)
    res = run_planning(inc, exp, obls, goals, bliq=bliq, r_bench=0.14, risk_tolerance=rng.randint(1, 5), today=TODAY)
    if res.get("admissible_count") is None:
        continue
    if res["indicators"]["Rt"] <= 0:
        continue
    n_pos += 1
    if res["admissible_count"] != res["alternatives_total"]:
        n_rej += 1
    # R-norm vs (1 - D-norm) on ALL admissible alternatives
    alts = res.get("ranked") or []
    if alts:
        n_rd_cases += 1
        dev = max(abs(a["scores"]["Rt_norm"] - a["scores"]["Dt_norm"]) for a in alts)
        max_dev = max(max_dev, dev)
        if dev <= 0.0015:
            n_rd_identical += 1
print("portraits with Rt>0:", n_pos)
print("portraits where filter rejected >=1 alternative:", n_rej)
print("portraits with alternatives list:", n_rd_cases, " where Rt_norm == Dt_norm(inverted) on every alt (|diff|<=0.0015):", n_rd_identical, " max |diff|:", round(max_dev, 4))

# --- inspect worst R/D divergence ---
rng = random.Random(20260917)
worst = None
for _ in range(3000):
    inc, exp, obls, goals, bliq = portrait(rng)
    res = run_planning(inc, exp, obls, goals, bliq=bliq, r_bench=0.14, risk_tolerance=3, today=TODAY)
    if res["indicators"]["Rt"] <= 0 or not res.get("ranked"):
        continue
    alts = res["ranked"]
    dev = max(abs(a["scores"]["Rt_norm"] - a["scores"]["Dt_norm"]) for a in alts)
    if worst is None or dev > worst[0]:
        worst = (dev, inc, exp, obls, alts)
dev, inc, exp, obls, alts = worst
print("\nWORST dev", dev, "income", inc, "exp", round(exp), "obls", [(round(o['amount']), o['interest_rate'], round(o['monthly_payment'],2)) for o in obls])
rts = sorted(set(a["Rt_new"] for a in alts)); dts = sorted(set(a["Dt_new"] for a in alts))
print(" distinct Rt_new:", len(rts), rts[:3], rts[-2:], " distinct Dt_new:", len(dts), dts)

# --- classify divergences ---
rng = random.Random(20260917)
cls = {"identical": 0, "div_due_to_rounding_collapse": 0, "div_other": 0}
for _ in range(3000):
    inc, exp, obls, goals, bliq = portrait(rng)
    res = run_planning(inc, exp, obls, goals, bliq=bliq, r_bench=0.14, risk_tolerance=3, today=TODAY)
    if res["indicators"]["Rt"] <= 0 or not res.get("ranked"):
        continue
    alts = res["ranked"]
    dev = max(abs(a["scores"]["Rt_norm"] - a["scores"]["Dt_norm"]) for a in alts)
    if dev <= 0.0015:
        cls["identical"] += 1
    elif len(set(a["Dt_new"] for a in alts)) <= 3 or len(set(a["Rt_new"] for a in alts)) <= 3:
        cls["div_due_to_rounding_collapse"] += 1
    else:
        cls["div_other"] += 1
print("\nR/D classification:", cls)

# --- magnitude of R/D divergence and its origin (Dt_new quantised to 4 decimals) ---
rng = random.Random(20260917)
devs = []; quanta = []
for _ in range(3000):
    inc, exp, obls, goals, bliq = portrait(rng)
    res = run_planning(inc, exp, obls, goals, bliq=bliq, r_bench=0.14, risk_tolerance=3, today=TODAY)
    if res["indicators"]["Rt"] <= 0 or not res.get("ranked"):
        continue
    alts = res["ranked"]
    dev = max(abs(a["scores"]["Rt_norm"] - a["scores"]["Dt_norm"]) for a in alts)
    if dev > 0.0015:
        devs.append(dev)
        rng_d = max(a["Dt_new"] for a in alts) - min(a["Dt_new"] for a in alts)
        quanta.append(round(rng_d / 0.0001))
devs.sort(); quanta.sort()
q = lambda xs, p: xs[int(p * (len(xs) - 1))]
print("\ndivergent n=", len(devs), " dev p50/p90/max:", round(q(devs,.5),4), round(q(devs,.9),4), round(devs[-1],4),
      " D-range in 1e-4 quanta p10/p50:", q(quanta,.1), q(quanta,.5))
```

**p1b.py**

```python
"""G40 p.1b: forecast stock/flow, synthetic-history trend, Si canon-vs-code, goal cap redistribution."""
import sys
from datetime import datetime
sys.path.insert(0, "/Users/vasyaevdokimov/repos/personal-finance-dss")
from app.services.forecasting import forecast_indicators
from app.core.forecast import build_history_from_current, choose_point_forecast
from app.core.goals_priority import calculate_goals_si

# (A) forecast: constant real history, zero r_bench
f = forecast_indicators(balance=100_000, rt=30_000, lt=0, dt=0.1, income_total=100_000, expense_total=60_000,
                        obligation_payments=10_000, horizon=3,
                        income_history=[100_000]*6, expense_history=[60_000]*6, r_bench=0.0)
for row in f["forecast"]:
    print("A h=%d Bt=%.0f Rt=%.0f Lt=%.3f p10=%.0f p90=%.0f" % (row["period"], row["Bt"], row["Rt"], row["Lt"], row["Rt_p10"], row["Rt_p90"]))

# (B) no history: synthetic history -> Holt trend invented?
f2 = forecast_indicators(balance=0, rt=30_000, lt=0, dt=0.1, income_total=100_000, expense_total=60_000,
                         obligation_payments=10_000, horizon=6, r_bench=0.0)
print("B synthetic income history:", build_history_from_current(100_000, seed=1))
print("B income forecast h1..h6:", [row["income"] for row in f2["forecast"]])
print("B expense forecast h1..h6:", [row["expense"] for row in f2["forecast"]])

# (C) Rt close to zero -> MC interval width
f3 = forecast_indicators(balance=-29_990, rt=10, lt=0, dt=0.1, income_total=100_000, expense_total=89_990,
                         obligation_payments=10_000, horizon=3,
                         income_history=[70_000, 130_000, 60_000, 140_000, 100_000, 100_000],
                         expense_history=[89_990]*6, r_bench=0.0)
for row in f3["forecast"]:
    print("C h=%d Rt=%.0f p10=%.0f p90=%.0f" % (row["period"], row["Rt"], row["Rt_p10"], row["Rt_p90"]))

# (D) Si: canon formula vs code formula, and redistribution of capped excess
today = datetime(2026, 9, 17)
goals = [
    {"id": "g1", "name": "small", "target_amount": 10_000, "current_amount": 0, "deadline": datetime(2027, 3, 17), "category": "income_growth"},
    {"id": "g2", "name": "big", "target_amount": 1_000_000, "current_amount": 200_000, "deadline": datetime(2027, 9, 17), "category": "material"},
]
for xg in (20_000, 60_000):
    si, alloc = calculate_goals_si(xg, goals, today)
    # canon §11.3: sum (C+dC) w u / sum T w u
    from app.core.goals_priority import urgency_of, CATEGORY_WEIGHTS
    num = den = 0.0
    for g in goals:
        p = CATEGORY_WEIGHTS[g["category"]] * urgency_of(g["deadline"], today)
        num += (g["current_amount"] + alloc.get(g["id"], 0)) * p
        den += g["target_amount"] * p
    print("D x_g=%d code Si=%.4f canon Si=%.4f alloc=%s deployed=%.0f unused->reserve=%.0f" % (xg, si, num/den, alloc, sum(alloc.values()), xg - sum(alloc.values())))
```

**p1c.py**

```python
"""G40 p.1c: edge of feasible set (Rt=0, Rt=-0.003), ties at the top, crisis floor vs ranking floor."""
import sys, random
from datetime import datetime
sys.path.insert(0, "/Users/vasyaevdokimov/repos/personal-finance-dss")
from app.services.planning import run_planning
from app.core.ranking import effective_floor_months
TODAY = datetime(2026, 9, 17)
loan = {"id": "o1", "name": "MFO", "amount": 50_000, "interest_rate": 1.5, "monthly_payment": 10_000}
for exp in (40_000, 40_000.003):
    r = run_planning(50_000, exp, [loan], [], bliq=0, r_bench=0.14, today=TODAY)
    b = r["best"]
    print("Rt=%.3f crisis=%s best=%s admissible=%s" % (50_000 - exp - 10_000, r["crisis_plan"] is not None, b and b["id"], r["admissible_count"]))

# crisis branch floor vs ranking floor for a toxic-debt user
print("ranking floor with toxic loan:", effective_floor_months([loan], 0.14))
r = run_planning(50_000, 45_000, [loan], [], bliq=100_000, r_bench=0.14, today=TODAY)
print("crisis (Rt=-5000, bliq=100k = 2.22 mo of expenses, toxic MFO 50k):", [a["type"] for a in r["crisis_plan"]["actions"]], r["crisis_plan"]["severity"])
r = run_planning(50_000, 45_000, [loan], [], bliq=140_000, r_bench=0.14, today=TODAY)
print("crisis (bliq=140k = 3.11 mo):", [a["type"] for a in r["crisis_plan"]["actions"]], r["crisis_plan"]["severity"])

# ties at the top of the ranking
rng = random.Random(7); ties = tot = 0
for _ in range(2000):
    inc = rng.choice([60_000, 100_000, 200_000]); exp = inc * rng.uniform(0.3, 0.7)
    obls = [{"id": "o", "name": "c", "amount": rng.uniform(1e4, 1e6), "interest_rate": rng.choice([0.2, 0.3, 0.6]), "monthly_payment": rng.uniform(2e3, 3e4)}] if rng.random() < .7 else []
    goals = [{"id": "g", "name": "g", "target_amount": rng.uniform(5e4, 2e6), "current_amount": 0, "deadline": None, "category": "material"}] if rng.random() < .7 else []
    r = run_planning(inc, exp, obls, goals, bliq=exp * rng.choice([0, 1, 3, 7]), r_bench=0.14, risk_tolerance=rng.randint(1, 5), today=TODAY)
    rk = r["ranked"]
    if r["indicators"]["Rt"] <= 0 or len(rk) < 2: continue
    tot += 1
    if (rk[0]["floor_level"], rk[0]["utility"]) == (rk[1]["floor_level"], rk[1]["utility"]) and (rk[0]["x_obligations"], rk[0]["x_reserve"], rk[0]["x_goals"]) != (rk[1]["x_obligations"], rk[1]["x_reserve"], rk[1]["x_goals"]):
        ties += 1
print("top-1 exact ties on (floor_level, utility) between different nominal splits: %d of %d" % (ties, tot))
```

**Вывод `p1.py`:**
```
portraits with Rt>0: 1410
portraits where filter rejected >=1 alternative: 0
portraits with alternatives list: 1410  where Rt_norm == Dt_norm(inverted) on every alt (|diff|<=0.0015): 863  max |diff|: 0.702
WORST dev 1.0 income 150000 exp 89931 obls [(369735, 0.35, 21636.39), (1391406, 0.22, 38429.11)]
 distinct Rt_new: 11 [3.42, 3.44, 3.46] [3.6, 3.62]  distinct Dt_new: 1 [0.4004]
R/D classification: {'identical': 888, 'div_due_to_rounding_collapse': 8, 'div_other': 541}
divergent n= 549  dev p50/p90/max: 0.008 0.033 1.0  D-range in 1e-4 quanta p10/p50: 18 79
```
(первая строка — один профиль риска на портрет, случайный; блоки 2–4 — профиль 3; отсюда 863 против 888.)

**Вывод `p1b.py`:**
```
A h=1 Bt=129793 Rt=159586 Lt=2.163 p10=146498 p90=172334
A h=2 Bt=159541 Rt=189290 Lt=2.659 p10=172648 p90=206073
A h=3 Bt=189249 Rt=218957 Lt=3.154 p10=196250 p90=242036
B synthetic income history: [102183.29, 103597.34, 97598.41, 94250.19, 93317.57, 99350.41]
B income forecast h1..h6: [96366.08, 95884.43, 95450.96, 95060.83, 94709.71, 94393.71]
B expense forecast h1..h6: [52440.75, 51303.52, 50280.02, 49358.87, 48529.83, 47783.69]
C h=1 Rt=58574 p10=53770 p90=63253
C h=2 Rt=115181 p10=105055 p90=125394
C h=3 Rt=176719 p10=158393 p90=195347
D x_g=20000 code Si=0.0727 canon Si=0.2478 alloc={'g1': 10000.0, 'g2': 2870.74} deployed=12871 unused->reserve=7129
D x_g=60000 code Si=0.0794 canon Si=0.2532 alloc={'g1': 10000.0, 'g2': 8612.21} deployed=18612 unused->reserve=41388
```

**Вывод `p1c.py`:**
```
Rt=0.000 crisis=False best=deficit admissible=1
Rt=-0.003 crisis=False best=deficit admissible=1
ranking floor with toxic loan: 1.0
crisis (Rt=-5000, bliq=100k = 2.22 mo of expenses, toxic MFO 50k): ['cut_expenses', 'restructure_debt'] cut_required
crisis (bliq=140k = 3.11 mo): ['close_debts_from_liquidity'] recoverable_from_liquidity
top-1 exact ties on (floor_level, utility) between different nominal splits: 58 of 1793
```

---

## Пункт 2. Устойчивость рекомендации: скачки и монотонность

### 2.1. Главная находка: модель почти всегда кладёт ВСЁ в одно направление 🔴

**Аналогия.** Представь весы с тремя чашами, но каждая гиря подписана не «сколько грамм», а «на каком месте по тяжести».
Тогда неважно, сколько весит каждая вещь — побеждает та чаша, у которой ярлык «первое место». Весы перестают взвешивать.

**Суть в трёх шагах.**
1. min-max нормализация (§7, стр. 264) растягивает каждый критерий так, что худшая альтернатива получает 0, лучшая — 1,
   **независимо от того, насколько велика разница в рублях**: сэкономить 100 ₽ платежа в месяц или 10 000 ₽ — после нормировки одно и то же «1».
2. Каждый критерий почти линейно зависит от «своей» доли: платёж падает пропорционально досрочке (`avalanche.py:79`),
   подушка растёт пропорционально резерву (`alternatives.py:216`), $S_n$ растёт пропорционально взносу (`goals_priority.py:157–162`).
   Значит $U(a) \approx W_d\,\alpha_d + W_r\,\alpha_r + W_g\,\alpha_g$ + константа, где $\alpha$ — доли, а $W$ — веса профиля
   ($W_d = w_R + w_D$ из-за дубля 1.1, $W_r = w_L$, $W_g = w_S$).
3. Линейная функция на треугольнике долей $\alpha_d+\alpha_r+\alpha_g=1$ достигает максимума **в вершине** — это основная теорема
   линейного программирования. Вершина = «100 % в одно направление». В ребро или внутрь решение попадает только там, где
   линейность ломается: насыщение подушки на $L^*$, кэп цели, полностью погашенный кредит, floor.

**Число** (`p2b.py`, блок A: 4000 случайных портретов, seed 11, из них 2720 с положительным потоком). Где лежит эффективное
распределение победителя:

| | вершина (всё в одно) | ребро (два направления) | внутри (все три) |
|---|---:|---:|---:|
| все профили | **2475 (91,0 %)** | 240 (8,8 %) | 5 (0,2 %) |
| консервативный | 398 | 119 | 1 |
| сбалансированный | 536 | 22 | 1 |
| агрессивный | 486 | 38 | 1 |

**Что это значит для продукта.** Обоснование шага 10 % — «заметно более тонкие рекомендации» (§4.3, стр. 199; §18 п. 5, стр. 667) —
на данных не подтверждается: 66 точек перебираются, а выигрывает почти всегда угол. Сама решётка при этом не вредна —
она просто почти не используется.

### 2.2. Решение слепо к ставке и к важности цели 🔴

**Число** (`p2b.py`, блок B). Человек: доход 100 000 ₽, расходы 50 000 ₽, один кредит 300 000 ₽ с платежом 12 000 ₽ (4 % остатка),
подушка 200 000 ₽ (4 месяца, floor выполнен), цель «Учёба» (категория «рост дохода», вес 3,0 — высший), 400 000 ₽ через 18 месяцев.
Свободно 38 000 ₽/мес. Меняем **только ставку кредита**:

| Ставка | 15 % | 20 % | 29 % | 30 % | 60 % | 90 % |
|---|---|---|---|---|---|---|
| Консервативный | 11 400 долг / 26 600 резерв / 0 цели | то же | то же | то же | то же | то же |
| Сбалансированный | 38 000 долг / 0 / 0 | то же | то же | то же | то же | то же |
| Агрессивный | 38 000 долг / 0 / 0 | то же | то же | то же | то же | то же |

Кредит под 15 % (на 1 п.п. выше `r_bench` 14 %) и под 90 % дают **одинаковый** совет. Цель с наивысшим категориальным весом
не получает ни рубля ни в одном профиле, включая агрессивный ($w_S = 0{,}40$), потому что $W_d = 0{,}50 > 0{,}40$.
Ставка влияет на решение только через два порога: $r_{bench}$ (гасить ли вообще, §10.3) и токсичность ≥30 % (floor, §8).
Категории и срочность целей (§11.1–11.2) влияют только на то, **как делить деньги между целями**, но не на то, **идут ли деньги в цели**.

**Насколько серьёзно.** Высоко с точки зрения адекватности: экономически совет «гасить 15 % вместо того, чтобы копить на
учёбу, которая поднимет доход» спорен, а «гасить 15 % так же приоритетно, как 90 %» — просто потеря информации.
Эксперты этого не поймали, потому что сертификация сравнивает **доминанту** (направление), а доминанта «в долг» у экспертов чаще всего тоже.
S6 из `p2.py`: для «Анны» (ниже) все пять профилей дают один и тот же план — 100 % в долг.

### 2.3. Карта разрывов: где ничтожное изменение входа меняет совет целиком

Базовый человек «Анна» (`p2.py`): доход 90 000 ₽, расходы 55 000 ₽, кредитка 120 000 ₽ (платёж 5 %), потребкредит 400 000 ₽ под 18 %
(платёж 14 500 ₽), цель «Ремонт» 300 000 ₽ через 2 года, `r_bench` 14 %. Свободно 14 500 ₽/мес.

| Порог | Изменение входа | Совет до | Совет после | Величина скачка |
|---|---|---|---|---|
| **Токсичность долга 30 %** (§8/§20) | ставка кредитки 29,5 % → 30,0 %, подушка 80 000 ₽ | 14 500 ₽ в резерв | 14 500 ₽ в долг | **100 % потока**, от 0,5 п.п. ставки |
| **Floor 2 мес.** (§8) | подушка 96 500 → 97 000 ₽ (+500 ₽) | 14 500 в резерв | 1 450 долг / 13 050 резерв | 1 450 ₽ = 10 % потока; «пила» с шагом решётки, 10 переключений на 40 000 ₽ подушки |
| **Знак потока $R_t$** (§3.2/§12) | расходы 69 250 → 69 500 → 69 750 ₽ | +250 ₽ в долг | «Дефицитный бюджет», действий нет | кризис: «погасить кредитку из подушки» (5 000 ₽ из 150 000) |
| там же | расходы 70 000 → 70 250 ₽ | кризис: погасить из подушки | кризис: «сократите расходы, реструктурируйте» | смена типа совета от 250 ₽ расходов |
| **Инфляция цели 36 мес.** (§11.3) | срок цели 1080 → 1081 день | $T^{fut}$ = 2 000 000 ₽ | $T^{fut}$ = 2 249 973 ₽ | +12,5 % к цели за один день; в опытах `p2b.py` блок D на победителя не повлияло (решение — угол «всё в цели», доли между целями от $T^{fut}$ не зависят) |
| **ПДН 0,40** (§6) | — | — | — | **разрыва нет**: гейт пуст (1.2), 0,40 влияет только на флаг `Dt_alert` |
| **Кромка ПСК 300 %** | — | — | — | **в ядре продукта нет**: схема `app/schemas/obligation.py:14` — `interest_rate ≥ 0` без верхней границы; 300 % — порог валидатора экспертных датасетов (канон стр. 61), не пользовательский |
| **Шаг решётки 10 %** (§4.3) | — | — | — | ошибка ≤ 10 % потока; видна только там, где решение не в вершине (≈9 % случаев, 2.1) |

**Замечает ли пользователь.** Да — в двух местах. (1) Порог 30 %: два человека с кредитками под 29,9 % и 30 % получают
противоположные советы, и объяснение (`recommendation.py`) не называет порог. (2) Граница $R_t = 0$: при +250 ₽ — план,
при 0 ₽ — «распределять нечего» без действий, при −250 ₽ — кризисный план с погашением из подушки. Человек, у которого
поток колеблется около нуля от месяца к месяцу, увидит три разных типа совета подряд.

### 2.4. Монотонность по доходу 🟢

`p2.py` S1: доход от 70 000 до 160 000 ₽ шагом 250 ₽. Нарушений «больший доход → какое-то направление получает меньше рублей» — **2**,
оба в узкой зоне сразу после выхода из дефицита (доход 75 750 → 76 000 и 76 250 → 76 500 ₽, свободно 250–1000 ₽), величина
75–125 ₽. Выше — строго монотонно: всё в долг, сумма растёт с доходом. Наибольшее перераспределение на +250 ₽ дохода — 200 ₽.
**Вывод:** по доходу модель монотонна практически везде; немонотонность — в зоне копеечного потока, где решётка 10 % грубее самих сумм.
Но обратная сторона того же: при доходе 160 000 ₽ (свободно 84 500 ₽/мес.) цель «Ремонт» через 2 года по-прежнему получает 0 ₽ —
монотонность достигнута ценой того, что решение — всегда один угол.

### 2.5. Итог пункта 2

- **Надёжно:** монотонность по доходу; отсутствие разрыва на ПДН 0,40; floor — «пила» с амплитудой не больше шага решётки.
- **Неустойчиво:** порог токсичности 30 % (полный разворот потока от 0,5 п.п. ставки); граница $R_t=0$ (три типа совета на ±250 ₽).
- **Неадекватно по существу:** решение в 91 % случаев — угол симплекса, определённый только весами; ставка (выше $r_{bench}$) и важность цели в выбор направления не входят. Это следствие связки «min-max + линейные критерии + взвешенная сумма», и к нему вернёмся в пунктах 3 и 9.

### Скрипты пункта 2 (дословно)

**p2.py**

```python
"""G40 p.2: discontinuities and monotonicity of the recommendation (read-only use of app.services.planning)."""
import sys, random
from datetime import datetime, timedelta
sys.path.insert(0, "/Users/vasyaevdokimov/repos/personal-finance-dss")
from app.services.planning import run_planning
TODAY = datetime(2026, 9, 17)

def eff(res):
    b = res["best"]
    if res["crisis_plan"] is not None:
        return ("CRISIS", tuple(a["type"] for a in res["crisis_plan"]["actions"]))
    if b is None or b["id"] == "deficit":
        return ("DEFICIT",)
    goals = sum(b.get("goal_allocation", {}).values())
    return (round(b["x_obl_effective"]), round(b["x_reserve_effective"]), round(goals), b["id"])

def base(income=90_000, expenses=55_000, card_rate=0.25, bliq=150_000, goal_days=730, profile=3, card_amt=120_000):
    obls = [
        {"id": "card", "name": "Кредитка", "amount": card_amt, "interest_rate": card_rate, "monthly_payment": card_amt * 0.05},
        {"id": "cash", "name": "Потребкредит", "amount": 400_000, "interest_rate": 0.18, "monthly_payment": 14_500},
    ]
    goals = [{"id": "g", "name": "Ремонт", "target_amount": 300_000, "current_amount": 20_000,
              "deadline": TODAY + timedelta(days=goal_days), "category": "material"}]
    return run_planning(income, expenses, obls, goals, bliq=bliq, r_bench=0.14, risk_tolerance=profile, today=TODAY)

def sweep(name, xs, f):
    prev = None; changes = []
    for x in xs:
        e = eff(f(x))
        if prev is not None and e != prev[1]:
            changes.append((prev[0], prev[1], x, e))
        prev = (x, e)
    print(f"\n== {name}: {len(changes)} switches")
    for c in changes[:14]:
        print("  ", c)
    return changes

# S1: income sweep, step 250 RUB
ch = sweep("S1 income 70k..160k step 250 (exp 55k, bliq 150k, card 25%)", range(70_000, 160_001, 250), lambda x: base(income=x))
# monotonicity: RUB to each bucket vs income
rows = []
for x in range(70_000, 160_001, 250):
    e = eff(base(income=x))
    if isinstance(e[0], int):
        rows.append((x, e[0], e[1], e[2]))
viol = [(a, b) for a, b in zip(rows, rows[1:]) if b[1] < a[1] - 1 or b[2] < a[2] - 1 or b[3] < a[3] - 1]
print("  monotonicity violations (some bucket gets FEWER roubles when income +250):", len(viol))
for a, b in viol[:6]:
    print("    ", a, "->", b)
big = sorted(((abs(b[1]-a[1]) + abs(b[2]-a[2]) + abs(b[3]-a[3])) / 2, a, b) for a, b in zip(rows, rows[1:]))[-3:]
print("  largest re-allocation per +250 RUB income (RUB moved between buckets):", big)

# S2: liquid cushion sweep around floor (2 * 55k = 110k)
sweep("S2 bliq 90k..130k step 500 (income 90k)", range(90_000, 130_001, 500), lambda x: base(bliq=x))

# S3: card rate sweep through toxic threshold 0.30 and r_bench 0.14
sweep("S3 card rate 0.10..0.60 step 0.005 (bliq 80k, 1.45 mo)", [round(0.10 + 0.005 * i, 3) for i in range(101)], lambda r: base(card_rate=r, bliq=80_000))

# S4: goal deadline around 36 months (inflation step)
sweep("S4 goal deadline 1070..1095 days (income 90k, bliq 400k)", range(1070, 1096), lambda d: base(goal_days=d, bliq=400_000))

# S5: expenses sweep across Rt = 0
sweep("S5 expenses 67k..71k step 250 (Rt crosses 0 at 69 500)", range(67_000, 71_001, 250), lambda x: base(expenses=x, bliq=150_000))

# S6: profile sweep on the same person
for p in range(1, 6):
    print("S6 profile", p, eff(base(profile=p, bliq=400_000)))
```

**Вывод p2.py:**
```

== S1 income 70k..160k step 250 (exp 55k, bliq 150k, card 25%): 340 switches
   (73250, ('CRISIS', ('cut_expenses', 'freeze_goals', 'restructure_debt')), 73500, ('CRISIS', ('close_debts_from_liquidity', 'freeze_goals')))
   (75250, ('CRISIS', ('close_debts_from_liquidity', 'freeze_goals')), 75500, ('DEFICIT',))
   (75500, ('DEFICIT',), 75750, (125, 125, 0, 'a550'))
   (75750, (125, 125, 0, 'a550'), 76000, (450, 50, 0, 'a910'))
   (76000, (450, 50, 0, 'a910'), 76250, (675, 75, 0, 'a910'))
   (76250, (675, 75, 0, 'a910'), 76500, (1000, 0, 0, 'a1000'))
   (76500, (1000, 0, 0, 'a1000'), 76750, (1250, 0, 0, 'a1000'))
   (76750, (1250, 0, 0, 'a1000'), 77000, (1500, 0, 0, 'a1000'))
   (77000, (1500, 0, 0, 'a1000'), 77250, (1750, 0, 0, 'a1000'))
   (77250, (1750, 0, 0, 'a1000'), 77500, (2000, 0, 0, 'a1000'))
   (77500, (2000, 0, 0, 'a1000'), 77750, (2250, 0, 0, 'a1000'))
   (77750, (2250, 0, 0, 'a1000'), 78000, (2500, 0, 0, 'a1000'))
   (78000, (2500, 0, 0, 'a1000'), 78250, (2750, 0, 0, 'a1000'))
   (78250, (2750, 0, 0, 'a1000'), 78500, (3000, 0, 0, 'a1000'))
  monotonicity violations (some bucket gets FEWER roubles when income +250): 2
     (75750, 125, 125, 0) -> (76000, 450, 50, 0)
     (76250, 675, 75, 0) -> (76500, 1000, 0, 0)
  largest re-allocation per +250 RUB income (RUB moved between buckets): [(125.0, (159750, 84250, 0, 0), (160000, 84500, 0, 0)), (200.0, (75750, 125, 125, 0), (76000, 450, 50, 0)), (200.0, (76250, 675, 75, 0), (76500, 1000, 0, 0))]

== S2 bliq 90k..130k step 500 (income 90k): 10 switches
   (96500, (0, 14500, 0, 'a0100'), 97000, (1450, 13050, 0, 'a190'))
   (98000, (1450, 13050, 0, 'a190'), 98500, (2900, 11600, 0, 'a280'))
   (99500, (2900, 11600, 0, 'a280'), 100000, (4350, 10150, 0, 'a370'))
   (101000, (4350, 10150, 0, 'a370'), 101500, (5800, 8700, 0, 'a460'))
   (102500, (5800, 8700, 0, 'a460'), 103000, (7250, 7250, 0, 'a550'))
   (104000, (7250, 7250, 0, 'a550'), 104500, (8700, 5800, 0, 'a640'))
   (105500, (8700, 5800, 0, 'a640'), 106000, (10150, 4350, 0, 'a730'))
   (107000, (10150, 4350, 0, 'a730'), 107500, (11600, 2900, 0, 'a820'))
   (108500, (11600, 2900, 0, 'a820'), 109000, (13050, 1450, 0, 'a910'))
   (109500, (13050, 1450, 0, 'a910'), 110000, (14500, 0, 0, 'a1000'))

== S3 card rate 0.10..0.60 step 0.005 (bliq 80k, 1.45 mo): 1 switches
   (0.295, (0, 14500, 0, 'a0100'), 0.3, (14500, 0, 0, 'a1000'))

== S4 goal deadline 1070..1095 days (income 90k, bliq 400k): 0 switches

== S5 expenses 67k..71k step 250 (Rt crosses 0 at 69 500): 12 switches
   (67000, (2500, 0, 0, 'a1000'), 67250, (2250, 0, 0, 'a1000'))
   (67250, (2250, 0, 0, 'a1000'), 67500, (2000, 0, 0, 'a1000'))
   (67500, (2000, 0, 0, 'a1000'), 67750, (1750, 0, 0, 'a1000'))
   (67750, (1750, 0, 0, 'a1000'), 68000, (1500, 0, 0, 'a1000'))
   (68000, (1500, 0, 0, 'a1000'), 68250, (1250, 0, 0, 'a1000'))
   (68250, (1250, 0, 0, 'a1000'), 68500, (1000, 0, 0, 'a1000'))
   (68500, (1000, 0, 0, 'a1000'), 68750, (600, 150, 0, 'a820'))
   (68750, (600, 150, 0, 'a820'), 69000, (450, 50, 0, 'a910'))
   (69000, (450, 50, 0, 'a910'), 69250, (250, 0, 0, 'a1000'))
   (69250, (250, 0, 0, 'a1000'), 69500, ('DEFICIT',))
   (69500, ('DEFICIT',), 69750, ('CRISIS', ('close_debts_from_liquidity', 'freeze_goals')))
   (70000, ('CRISIS', ('close_debts_from_liquidity', 'freeze_goals')), 70250, ('CRISIS', ('cut_expenses', 'freeze_goals', 'restructure_debt')))
S6 profile 1 (14500, 0, 0, 'a1000')
S6 profile 2 (14500, 0, 0, 'a1000')
S6 profile 3 (14500, 0, 0, 'a1000')
S6 profile 4 (14500, 0, 0, 'a1000')
S6 profile 5 (14500, 0, 0, 'a1000')
```

**p2b.py**

```python
"""G40 p.2b: corner solutions, weight-only decisions, rate blindness, inflation step for a debt-free person."""
import sys, random
from collections import Counter
from datetime import datetime, timedelta
sys.path.insert(0, "/Users/vasyaevdokimov/repos/personal-finance-dss")
from app.services.planning import run_planning
TODAY = datetime(2026, 9, 17)

def shares(b):
    return (int(b["id"][1]) if len(b["id"]) == 4 else None) if False else b["id"]

# (A) where do winners lie on the simplex? vertex (one direction 100%), edge (two), interior (three)
rng = random.Random(11); kinds = Counter(); by_profile = {p: Counter() for p in range(1, 6)}
for _ in range(4000):
    inc = rng.choice([50_000, 80_000, 120_000, 200_000, 350_000]); exp = inc * rng.uniform(0.3, 0.75)
    obls = []
    for k in range(rng.randint(0, 2)):
        amt = rng.uniform(1e4, 2e6); rate = rng.choice([0.08, 0.16, 0.22, 0.35, 0.9]); n = rng.choice([12, 36, 120, 240]); rm = rate / 12
        obls.append({"id": f"o{k}", "name": "l", "amount": amt, "interest_rate": rate, "monthly_payment": amt * rm / (1 - (1 + rm) ** -n)})
    goals = [{"id": f"g{s}", "name": "g", "target_amount": rng.uniform(3e4, 5e6), "current_amount": 0,
              "deadline": rng.choice([None, TODAY + timedelta(days=rng.randint(60, 4000))]),
              "category": rng.choice(["income_growth", "safety", "material", "emotional"])} for s in range(rng.randint(0, 3))]
    p = rng.randint(1, 5)
    r = run_planning(inc, exp, obls, goals, bliq=exp * rng.choice([0, 1, 2.5, 5, 10]), r_bench=0.14, risk_tolerance=p, today=TODAY)
    b = r["best"]
    if r["crisis_plan"] is not None or b is None or b["id"] == "deficit":
        continue
    x = [b["x_obl_effective"], b["x_reserve_effective"], sum(b.get("goal_allocation", {}).values())]
    nz = sum(1 for v in x if v > 0.5)
    k = {1: "vertex", 2: "edge", 3: "interior"}.get(nz, "empty")
    kinds[k] += 1; by_profile[p][k] += 1
print("A effective-split location of the winner:", dict(kinds))
for p in range(1, 6):
    print("   profile", p, dict(by_profile[p]))

# (B) rate blindness: one loan, fixed payment/amount ratio, cushion above floor, rate 15%..90%
def one(rate, profile, amt=300_000, ratio=0.04, goal=True):
    obls = [{"id": "o", "name": "Кредит", "amount": amt, "interest_rate": rate, "monthly_payment": amt * ratio}]
    goals = [{"id": "g", "name": "Учёба", "target_amount": 400_000, "current_amount": 0, "deadline": TODAY + timedelta(days=540), "category": "income_growth"}] if goal else []
    r = run_planning(100_000, 50_000, obls, goals, bliq=200_000, r_bench=0.14, risk_tolerance=profile, today=TODAY)
    b = r["best"]
    return (round(b["x_obl_effective"]), round(b["x_reserve_effective"]), round(sum(b.get("goal_allocation", {}).values())))
for p in (1, 3, 5):
    print("B profile", p, {rate: one(rate, p) for rate in (0.15, 0.20, 0.29, 0.30, 0.60, 0.90)})

# (C) same person, loan balance 30k vs 3M (magnitude blindness), rate 20%
for p in (1, 3, 5):
    print("C profile", p, {amt: one(0.20, p, amt=amt) for amt in (30_000, 300_000, 900_000)})

# (D) inflation step at 36 months for a debt-free person with two goals
def goals_person(days, profile=5):
    goals = [{"id": "far", "name": "Квартира", "target_amount": 2_000_000, "current_amount": 0, "deadline": TODAY + timedelta(days=days), "category": "material"},
             {"id": "near", "name": "Отпуск", "target_amount": 150_000, "current_amount": 0, "deadline": TODAY + timedelta(days=400), "category": "emotional"}]
    r = run_planning(120_000, 60_000, [], goals, bliq=400_000, r_bench=0.14, risk_tolerance=profile, today=TODAY)
    b = r["best"]
    return b["id"], {k: round(v) for k, v in b["goal_allocation"].items()}, round(b["x_reserve_effective"])
for d in (1079, 1080, 1081, 1085):
    print("D deadline days", d, goals_person(d))
```

**Вывод p2b.py:**
```
A effective-split location of the winner: {'vertex': 2475, 'edge': 240, 'interior': 5}
   profile 1 {'vertex': 398, 'edge': 119, 'interior': 1}
   profile 2 {'vertex': 533, 'edge': 17, 'interior': 1}
   profile 3 {'vertex': 536, 'edge': 22, 'interior': 1}
   profile 4 {'vertex': 522, 'edge': 44, 'interior': 1}
   profile 5 {'vertex': 486, 'edge': 38, 'interior': 1}
B profile 1 {0.15: (11400, 26600, 0), 0.2: (11400, 26600, 0), 0.29: (11400, 26600, 0), 0.3: (11400, 26600, 0), 0.6: (11400, 26600, 0), 0.9: (11400, 26600, 0)}
B profile 3 {0.15: (38000, 0, 0), 0.2: (38000, 0, 0), 0.29: (38000, 0, 0), 0.3: (38000, 0, 0), 0.6: (38000, 0, 0), 0.9: (38000, 0, 0)}
B profile 5 {0.15: (38000, 0, 0), 0.2: (38000, 0, 0), 0.29: (38000, 0, 0), 0.3: (38000, 0, 0), 0.6: (38000, 0, 0), 0.9: (38000, 0, 0)}
C profile 1 {30000: (29280, 19520, 0), 300000: (11400, 26600, 0), 900000: (1400, 12600, 0)}
C profile 3 {30000: (29280, 19520, 0), 300000: (38000, 0, 0), 900000: (14000, 0, 0)}
C profile 5 {30000: (30000, 0, 18800), 300000: (38000, 0, 0), 900000: (14000, 0, 0)}
D deadline days 1079 ('a0010', {'far': 40000, 'near': 20000}, 0)
D deadline days 1080 ('a0010', {'far': 40000, 'near': 20000}, 0)
D deadline days 1081 ('a0010', {'far': 40000, 'near': 20000}, 0)
D deadline days 1085 ('a0010', {'far': 40000, 'near': 20000}, 0)
```
---

## Пункт 3. Нормализация и SAW: rank reversal, «вес без диапазона», компенсаторность

Вход (не переоткрывается): тема 15, `docs/research/raw/mcda_saw_alternatives_2026-09-09.md` — нормализация как причина rank reversal
(стр. 79–116), компенсаторность SAW (стр. 125–128, 239–240), max-нормализация устойчивее min-max (Shyur & Shih 2024, стр. 345–359),
у RAFSI нет теоремы о rank reversal (стр. 615), O'Shea et al. 2026 — интервалы устойчивости весов (стр. 466–487).

### 3.1. Rank reversal от добавления/удаления альтернатив — у нас структурно почти невозможен 🟢

**Аналогия.** Оценки «по кривой» в классе меняются, если в класс пришёл отличник. Но если отличник и двоечник в классе всегда одни и те же — кривая не сдвигается.

**Суть.** min-max по множеству $A$ (§7, стр. 264) зависит только от крайних значений. У нас крайние значения каждого критерия достигаются
в **вершинах** решётки («всё в долг», «всё в резерв», «всё в цели»), а вершины присутствуют при любом шаге (10 %, 5 %) и отсекаются
только вместе с целым направлением (`alternatives.py:91–94`: нет целей — нет $g>0$, нет долгов — нет $d>0$), когда критерий и так константа.
Фильтр пуст (1.2). Значит классический сценарий rank reversal «добавили/убрали альтернативу — поменялся порядок остальных» в продукте
не возникает. Это совпадает с выводом темы 15 (стр. 529–532: «фиксированная решётка» как заслон). **Надёжно.**

### 3.2. Главный дефект нормализации — не rank reversal, а «вес без диапазона» 🔴

**Аналогия.** Спрашиваем: «что важнее — цена или расход бензина?» — «цена, вес 0,6». Но если все машины на выбор стоят от 1 000 000 до
1 000 500 ₽, а расход — от 5 до 15 литров, то «важная» цена на деле ничего не решает. Правильный вопрос: «что важнее — сэкономить 500 ₽
или 10 литров на сотню?». Вес имеет смысл только вместе с размахом.

**Литература.**
- Fischer, G. W. (1995). Range Sensitivity of Attribute Weights in Multiattribute Value Models. *Organizational Behavior and Human Decision Processes*, 62(3), 252–266. DOI 10.1006/obhd.1995.1048. Полный текст закрыт (Semantic Scholar `/paper/DOI:` → `openAccessPdf.status: CLOSED`, 17.09.2026). Реферат — `https://scholars.duke.edu/publication/771230`, HTTP 200 (curl и `r.jina.ai`), 17.09.2026, дословно:
  > «In decision analysis, multiattribute value functions are normalized relative to the best and worst outcomes in the local decision context. With this normalization, attribute weights (scaling constants) should vary as a function of the range of outcomes on each attribute in the local context. Other things being equal, the greater the range of outcomes for attribute X, the greater the weight for attribute X should be. […] Weights elicited using the direct importance weight method were range-insensitive, contrary to the standard normative model.»
- Monat, J. P. (2009). The benefits of global scaling in multi-criteria decision analysis. *Judgment and Decision Making*, 4(6). DOI 10.1017/s1930297500004034, `https://doi.org/10.1017/s1930297500004034` — HTTP 200, текст через `r.jina.ai` (88 990 байт), 17.09.2026, дословно:
  > «when local scales are used, differences in objective attribute values are typically transformed to use the full range of the attribute scale (typically 0–1, 0–10, or 0–100). Thus the poorest choice among the local option choices available, not among the entire universe of choices, would get a score of 0 and the best, 100. This forced transformation may over-emphasize the importance of small differences in attribute values and consequently lead to wrong conclusions.»
  > «There is substantial literature showing that the use of local scales precludes the use of importance weights in MCDA (see for example Goodwin & Wright, 2004) because importance weights will assign inappropriate weights to specific criteria when the range of values for that criterion is small, and vice-versa.»
- Morton, A. (2017). Multiattribute Value Elicitation. In *Elicitation* (Springer), DOI 10.1007/978-3-319-65052-4_12 (HTTP 200 на DOI, фрагмент через Exa, 17.09.2026), дословно:
  > «In ad hoc approaches, people often set weights by asking questions such as "how important is this criterion relative to that criterion?". Although people can answer such questions, the questions themselves are meaningless (Morton and Fasolo, 2009). In MAVT, the weighting questions are phrased in terms of increments on different scales.»
- Keeney, R. L. (2002). Common Mistakes in Making Value Trade-Offs. *Operations Research* 50(6):935–945, DOI 10.1287/opre.50.6.935.357 — **не открыт**: Semantic Scholar `CLOSED`, Unpaywall `is_oa: false`. Упомянут в выдаче Exa как источник того же тезиса; дословной цитаты нет.

**Как это у нас.** Нормализация — локальная min-max (§7), веса профилей (§9, стр. 312–318) заданы как «важность» один раз для всех
людей, без привязки к диапазонам. Размах каждого критерия у каждого человека свой: у одного 100 % в долг снижают платёж на 300 ₽, у другого на
30 000 ₽; у одного 100 % в резерв добавляют 0,1 месяца подушки, у другого 2 месяца. После min-max оба размаха превращаются в «от 0 до 1»,
а веса остаются теми же. Это ровно то, что Fischer называет range-insensitive direct importance weights и Monat — «importance weights with local scales». Канон ссылается на Jain et al. (2005) как на источник min-max (§7, стр. 273) — это источник из биометрии (нормализация оценок в fusion), к весам ЛПР он не относится.

**Число 1 — выбор нормализации решает судьбу плана** (`p3.py`, блок B). 1500 случайных портретов (seed 3), в 1092 с положительным потоком
заменяем только формулу нормализации: min-max (канон) → max-нормализация ($x/\max$; для долга $\min/x$), всё остальное как есть.
Эффективный план победителя изменился в **452 из 1092 (41,4 %)**; в 428 из них сменилось **доминирующее направление** (долг ↔ резерв ↔ цели).
Эксперимент подтверждает вывод Monat количественно: почти в половине случаев ответ — артефакт того, как растянуты шкалы, а не предпочтений.

**Число 2 — критический вес и «нож»** (`p3.py`, блок A; человек из 2.2: кредит 300 000 ₽ под 20 %, цель «Учёба» 400 000 ₽ через 18 мес., свободно 38 000 ₽).
Агрессивный профиль: $w_S$ = 0,40 → весь поток в долг. Поднимаем $w_S$, пропорционально уменьшая остальные: при $w_S$ = **0,46**
($w_R + w_D$ = 0,45) план **целиком** переключается: 38 000 ₽ в цели, 0 в долг. Никакого промежуточного плана нет — это видно и из 2.1:
решение — вершина, пока $W_d > W_g$, и другая вершина, как только $W_g > W_d$. Интервал устойчивости весов в духе O'Shea et al. здесь
считается в уме: «запас» агрессивного профиля до смены решения — 0,06 по весу цели, у сбалансированного ($W_d$ = 0,50, $W_S$ = 0,20) — 0,30.

**Что это значит для продукта.** Веса профилей — единственный реальный рычаг выбора направления (2.1), и они же — наименее обоснованная
часть (не зависят от диапазонов, калиброваны по согласию с экспертами, петля Г31.4). Модель выглядит многокритериальной, но работает как
правило «направление с максимальным весом профиля, с поправкой на насыщение и floor».

**Насколько серьёзно.** Высоко для научной корректности; средне для пользователя, потому что направление «в долг при ставке выше
$r_{bench}$» чаще всего и есть разумный совет. Опасность — в краях (3.3).

### 3.3. Компенсаторность: срочная цель безопасности «покупается» снижением платежа 🔴

**Аналогия.** Экзамен, где высокий балл по физкультуре засчитывается вместо сданной математики — даже если без математики не выдают диплом.

**Суть.** Канон признаёт компенсаторность SAW и ставит одну некомпенсаторную защиту — floor ликвидности (§8, §18 п. 9). Для целей такой защиты нет:
срок цели входит только в срочность $u_s$ (§11.2), а срочность — только в деление $x_g$ **между** целями (§11.4) и в $S_n$, который min-max делает
безразмерным. Разовое закрытие из подушки (§11.5) срабатывает только при сроке ≤ 3 мес. **и** сумме ≤ 50 % подушки.

**Числовой пример** (`p3.py`, блок C). Доход 110 000 ₽, расходы 55 000 ₽, потребкредит 500 000 ₽ под 19 % (платёж 18 000 ₽, не токсичный),
подушка 150 000 ₽ (2,7 мес., floor выполнен). Цель «Операция» (категория `safety`, вес 2,0), 120 000 ₽ через 4 месяца. Свободно 37 000 ₽/мес.
— ровно столько, чтобы успеть за 3,2 месяца.

| Профиль | Долг | Резерв | Операция |
|---|---:|---:|---:|
| Консервативный | 29 600 | 7 400 | **0** |
| Сбалансированный | 37 000 | 0 | **0** |
| Агрессивный | 37 000 | 0 | **0** |

Через месяц срок станет 3 мес., но 120 000 > 50 % × 150 000 = 75 000 — разовое закрытие не сработает. **Модель ведёт человека к сорванному
сроку операции, экономя ему ~1 100 ₽/мес. платежа по кредиту под 19 %.** Сертификация этого не ловит: сравнивается доминанта, а доминанта «в долг» —
частый ответ и у экспертов.

**Насколько серьёзно.** Высоко: это ровно тот случай, где литература требует вето (тема 15, стр. 276: «additive compensatory methods have also
incorporated the concept of veto»), а вето у нас пустое (1.2).

### 3.4. Итог пункта 3

- **Надёжно:** rank reversal от изменения набора альтернатив у нас структурно не возникает (крайние точки — всегда вершины решётки).
- **Ошибка постановки:** веса «важности» при локальной min-max нормализации — нарушение range-sensitivity principle (Fischer 1995; Monat 2009); замена нормализации на соседнюю стандартную меняет план в 41 % портретов.
- **Опасная компенсаторность:** срок цели (включая `safety`) не является ограничением и проигрывает снижению платежа по обычному кредиту.

### Скрипт пункта 3 (дословно)

**p3.py**

```python
"""G40 p.3: weight stability, normalization choice, compensation of a missed deadline (in-memory patches only)."""
import sys, random, copy
from collections import Counter
from datetime import datetime, timedelta
sys.path.insert(0, "/Users/vasyaevdokimov/repos/personal-finance-dss")
import app.core.ranking as ranking
from app.services.planning import run_planning
TODAY = datetime(2026, 9, 17)
ORIG_PROFILES = copy.deepcopy(ranking.RISK_PROFILES)
ORIG_NORM = ranking.normalize_value

def split(r):
    b = r["best"]
    if r["crisis_plan"] is not None or b is None or b["id"] == "deficit":
        return None
    return (round(b["x_obl_effective"]), round(b["x_reserve_effective"]), round(sum(b.get("goal_allocation", {}).values())))

def study_person(profile):
    obls = [{"id": "o", "name": "Кредит", "amount": 300_000, "interest_rate": 0.20, "monthly_payment": 12_000}]
    goals = [{"id": "g", "name": "Учёба", "target_amount": 400_000, "current_amount": 0, "deadline": TODAY + timedelta(days=540), "category": "income_growth"}]
    return run_planning(100_000, 50_000, obls, goals, bliq=200_000, r_bench=0.14, risk_tolerance=profile, today=TODAY)

# (A) weight stability: raise w_goals of profile 5, scale the other three proportionally, find the switch
base = ORIG_PROFILES[5]; prev = None
for i in range(0, 31):
    wg = round(0.40 + 0.01 * i, 2)
    k = (1 - wg) / (1 - base["w_goals"])
    ranking.RISK_PROFILES[5] = {**base, "w_goals": wg, "w_rt": base["w_rt"] * k, "w_lt": base["w_lt"] * k, "w_dt": base["w_dt"] * k}
    s = split(study_person(5))
    if s != prev:
        print("A w_goals=%.2f  (w_rt+w_dt=%.3f, w_lt=%.3f) -> split debt/reserve/goals = %s" % (wg, (base["w_rt"] + base["w_dt"]) * k, base["w_lt"] * k, s))
    prev = s
ranking.RISK_PROFILES[5] = ORIG_PROFILES[5]

# (B) normalization choice: min-max (canon) vs max-normalisation (x/max; for D: min/x) vs sum-normalisation
def max_norm(value, v_min, v_max, minimize=False):
    if v_max == v_min:
        return 1.0
    if minimize:
        return (v_min / value) if value > 0 else 1.0
    return value / v_max if v_max > 0 else 0.0

rng = random.Random(3); diff = tot = 0; kinds = Counter()
portraits = []
for _ in range(1500):
    inc = rng.choice([60_000, 100_000, 180_000]); exp = inc * rng.uniform(0.3, 0.7)
    obls = []
    for k in range(rng.randint(0, 2)):
        amt = rng.uniform(2e4, 1.5e6); rate = rng.choice([0.16, 0.22, 0.35]); n = rng.choice([12, 60, 240]); rm = rate / 12
        obls.append({"id": f"o{k}", "name": "l", "amount": amt, "interest_rate": rate, "monthly_payment": amt * rm / (1 - (1 + rm) ** -n)})
    goals = [{"id": "g", "name": "g", "target_amount": rng.uniform(5e4, 3e6), "current_amount": 0, "deadline": TODAY + timedelta(days=rng.randint(120, 3000)), "category": rng.choice(["income_growth", "safety", "material", "emotional"])}] if rng.random() < .8 else []
    portraits.append((inc, exp, obls, goals, exp * rng.choice([0, 2.5, 5, 9]), rng.randint(1, 5)))
for inc, exp, obls, goals, bliq, p in portraits:
    ranking.normalize_value = ORIG_NORM
    a = split(run_planning(inc, exp, obls, goals, bliq=bliq, r_bench=0.14, risk_tolerance=p, today=TODAY))
    ranking.normalize_value = max_norm
    b = split(run_planning(inc, exp, obls, goals, bliq=bliq, r_bench=0.14, risk_tolerance=p, today=TODAY))
    ranking.normalize_value = ORIG_NORM
    if a is None:
        continue
    tot += 1
    if a != b:
        diff += 1
        dom = lambda s: max(range(3), key=lambda i: s[i])
        kinds["dominant changed" if dom(a) != dom(b) else "same dominant, amounts changed"] += 1
print("B min-max vs max-normalisation: winner split differs in %d of %d portraits (%.1f%%): %s" % (diff, tot, 100 * diff / tot, dict(kinds)))

# (C) compensation: urgent safety goal (4 months) vs non-toxic debt, cushion above floor
obls = [{"id": "o", "name": "Потребкредит", "amount": 500_000, "interest_rate": 0.19, "monthly_payment": 18_000}]
goals = [{"id": "med", "name": "Операция", "target_amount": 120_000, "current_amount": 0, "deadline": TODAY + timedelta(days=120), "category": "safety"}]
for p in (1, 3, 5):
    r = run_planning(110_000, 55_000, obls, goals, bliq=150_000, r_bench=0.14, risk_tolerance=p, today=TODAY)
    print("C profile", p, "split debt/reserve/goals:", split(r), " months to deadline 4, need 120 000, free flow", round(r["indicators"]["Rt"]))
```

**Вывод p3.py:**
```
A w_goals=0.40  (w_rt+w_dt=0.500, w_lt=0.100) -> split debt/reserve/goals = (38000, 0, 0)
A w_goals=0.46  (w_rt+w_dt=0.450, w_lt=0.090) -> split debt/reserve/goals = (0, 0, 38000)
B min-max vs max-normalisation: winner split differs in 452 of 1092 portraits (41.4%): {'dominant changed': 428, 'same dominant, amounts changed': 24}
C profile 1 split debt/reserve/goals: (29600, 7400, 0)  months to deadline 4, need 120 000, free flow 37000
C profile 3 split debt/reserve/goals: (37000, 0, 0)  months to deadline 4, need 120 000, free flow 37000
C profile 5 split debt/reserve/goals: (37000, 0, 0)  months to deadline 4, need 120 000, free flow 37000
```
---

## Пункт 4. Avalanche и $r_{bench}$: насколько велик разрыв на НАШИХ ограничениях

Вход: Rios-Solis et al. 2017 (`optimization_solvers_2026-09-10.md`, Г30.1-20) — MILP, NP-трудность, разрыв >4 % в среднем, до 40 %;
Fox 1966 Теорема 2 (`closed_forever_retry_2026-09-16.md`, стр. 1768).

### 4.1. Откуда берётся разрыв Rios-Solis — и есть ли эти причины у нас 🟢 (уточнение входа)

Перечитан первоисточник (текст в скрэтчпаде `repay.txt`, 63 297 байт, добыт ранее: `https://pdfs.semanticscholar.org/5c18/d886f09b66d0bd8dc0a324b2963073f34a98.pdf`, HTTP 200). Дословно:
> «debtor disposes of a maximum amount of money $f_t$ in a month t to pay the loans. We let this amount to differ for each period to account for an extra or lesser income, such as a Christmas bonus.»
> «The debtor can choose to pay less than this minimum at the expense of obtaining a default interest rate $h_{tj} > i_{tj}$ […] certain debt instruments impose a penalty $pc_j$ when the debtor repays more than the initially established installment»
> (о 40 %-м примере) «the RPML model proposes to save money even if the debtor generates default penalties […] these savings will palliate the lack of cash that the debtor will face during months 3, 4 and 5 […] The cyclic behavior of the savings proposed by the RPML plan is the powerful arm that allows reducing the total amount of repayments by diminishing the default penalties.»

То есть разрыв порождают **три вещи**: меняющийся по месяцам бюджет, штрафы за недоплату минимума, штрафы за переплату — и возможность копить.

**Число** (`p4.py`, блок A). Собственная денежно-сохраняющая симуляция в постановке нашего §10.5: фиксированные минимальные платежи,
**постоянный** бюджет (сумма минимумов + доплата), освободившийся платёж закрытого долга навсегда уходит в пул, штрафов нет.
3000 случайных портфелей из 2–4 долгов (ставки 15–60 %, сроки 6–120 мес., доплата 2–40 тыс. ₽), seed 4040. Сравнение Avalanche со **всеми**
перестановками порядка приоритета: Avalanche был лучшим **в 3000 из 3000**, разрыв 0,00 % на всех квантилях.

**Что это значит.** На наших текущих допущениях (детерминированный постоянный поток, нет штрафов — ст. 11 ФЗ-353 запрещает комиссию за досрочку,
канон §10.1.1 стр. 350–351) Avalanche не проигрывает ни одному порядку. Разрыв Rios-Solis — это цена **того, чего в модели нет**: колебаний дохода
по месяцам и просрочек. Он станет реальным ровно для тех, у кого доход нерегулярный (ADR-015) или кто в кризисе (§12) — и там модель одномесячная
и помочь не может. Оговорка: сравнивались приоритетные правила, а не глобальный оптимум (MILP не запускался) — см. ЗАДОЛЖЕННОСТЬ.

### 4.2. Внутреннее противоречие: SAW меряет снижение ПЛАТЕЖА, а Avalanche гасит по СТАВКЕ 🟡

**Аналогия.** Тренер оценивает бегуна по скорости, а на старт ставит того, у кого лучше выносливость.

**Суть.** Критерии $R_t(a)$ и $D_t(a)$ (§5.1, §5.3) — это снижение ежемесячного платежа $\delta P$. Разлив $x_d$ внутри долгов — по убыванию ставки (§10.4).
Для максимизации $\delta P$ оптимален жадный шаг по «отдаче платежа на рубль» $P_k/A_k$ ($P$ — платёж, $A$ — остаток): функция $\delta P$ кусочно-линейная,
вогнутая и неубывающая по каждому кредиту — ровно условия Теоремы 2 Fox 1966, только маржинальная отдача — $P/A$, а не ставка. Кризисный модуль так и делает
(`crisis.py:59–69`, сортировка по $P/A$). **В одном ядре два разных правила** для одного и того же разлива денег по кредитам.

**Пример** (арифметика по аннуитетной формуле): 100 000 ₽ досрочки. Ипотека 20 % на 25 лет → платёж падает на **1 678 ₽**. Потребкредит 16 % на 2 года → на **4 896 ₽**.
Avalanche выберет ипотеку (выше ставка → меньше переплата — это верно), но критерий SAW при этом оценит досрочку на треть от возможного, и в споре
«долг против целей» долговое направление будет недооценено ровно у тех, у кого самый дорогой долг — длинный.

**Насколько серьёзно.** Средне. Экономически прав Avalanche; неправ критерий. Это аргумент в пользу замены критерия «снижение платежа» на «сэкономленные проценты» (или «чистая выгода против $r_{bench}$») — решение за владельцем.

### 4.3. Дефект в графике погашения (§10.5): освободившийся платёж «каскадится» один месяц, потом пропадает 🔴

**Суть.** Канон §10.5 (стр. 406–416): в накопительном сценарии освободившийся платёж закрытого долга «каскадом переходит в пул» — то есть навсегда.
Код `amortization._simulate`: `freed += pay` только **в месяц закрытия** (строки цикла `if principal >= balances[i]: freed += pay`), в следующие месяцы закрытый долг
пропускается (`if balances[i] <= 0: continue`) и ничего не освобождает. Плюс в месяц закрытия в пул добавляется **весь** платёж, хотя часть его ушла на погашение остатка.

**Число** (`p4.py` блок B и `p4b.py`).
- Синтетика: займ 1 000 ₽ с платежом 5 000 ₽ под 0 % + кредит 100 000 ₽ под 20 % с платежом 2 000 ₽. Продукт: **95 месяцев, 95 060 ₽ процентов**. Денежно-сохраняющая лавина: **17 месяцев, 15 476 ₽**.
- «Кредитка 60 000 ₽ под 30 % (платёж 3 000) + потребкредит 500 000 ₽ под 20 % на 5 лет», доплата 5 000 ₽/мес.: продукт показывает экономию **106 809 ₽** и срок 41 мес.; правильный каскад — **131 220 ₽** и 36 мес.
- «МФО 30 000 ₽ под 90 % + кредитка 150 000 ₽ под 35 % + автокредит 900 000 ₽ под 17 %», доплата 5 000 ₽: продукт — **107 674 ₽** и 50 мес.; правильно — **214 271 ₽** и 35 мес. **Экономия занижена вдвое, срок завышен на 15 месяцев.**

**Что это значит для пользователя.** Экран «сколько вы сэкономите, если будете гасить досрочно» систематически занижает выгоду у всех, у кого больше одного долга,
— как раз у тех, кого лавина мотивирует. В выбор плана не входит (красная линия ADR-016), поэтому это дефект подачи, а не решения. Канон говорит «занижение, не завышение» только про обрез $H_{max}$ (стр. 423–425); этот источник занижения в каноне не описан.

Попутно: §10.4 (стр. 396) — после досрочки **сохраняется срок** и падает платёж (так в `avalanche.py:79`), §10.5 — платёж **фиксирован** и сокращается срок. Две разные модели кредита в одном каноне; ст. 11 ФЗ-353 даёт заёмщику оба варианта, модель выбор не спрашивает.

### 4.4. $r_{bench} = r_{key}\cdot(1-0{,}13)$: математически и экономически 🟡

1. **Налог посчитан не так, как в законе.** НК РФ ст. 214.2 п. 1 (`https://www.consultant.ru/document/cons_doc_LAW_28165/deeb3189e859806a5eda495b89553a10d0f9b393/`, HTTP 200, текст через `r.jina.ai`, 17.09.2026), дословно:
   > «налоговая база определяется налоговым органом как превышение суммы доходов в виде процентов, полученных налогоплательщиком в течение налогового периода по всем вкладам (остаткам на счетах) в указанных банках, над суммой процентов, рассчитанной как произведение одного миллиона рублей и максимального значения ключевой ставки Центрального банка Российской Федерации из действовавших по состоянию на 1-е число каждого месяца в указанном налоговом периоде»
   Для типичного домохозяйства с подушкой меньше примерно миллиона рублей проценты по вкладу **не облагаются вовсе**, и посленалоговая доходность = полная ставка, а не 87 % от неё.
   **Пример:** ключевая 16 %. Канон: $r_{bench}$ = 13,9 %. Для человека с подушкой 300 000 ₽ реальная альтернатива ≈ 16 %. Кредит под 15 % канон объявит «гасить» (15 ≥ 13,9),
   хотя деньги на вкладе приносят больше, чем стоит кредит. Ошибка направлена в сторону досрочки — туда же, куда и отсутствие ликвидностной премии (канон §10.2, стр. 371–377).
   (Прогрессивная шкала НДФЛ с 2025 г. в этом батче не проверялась.)
2. **Ипотечный вычет процентов не учтён.** НК РФ ст. 220 п. 4 (`https://www.consultant.ru/document/cons_doc_LAW_28165/62f621e5835790398a88f80270fe2cf0b3710b3c/`, HTTP 200, 17.09.2026), дословно:
   > «Имущественный налоговый вычет, предусмотренный подпунктом 4 пункта 1 настоящей статьи, предоставляется в сумме фактически произведенных налогоплательщиком расходов по уплате процентов в соответствии с договором займа (кредита), но не более 3 000 000 рублей»
   Для ипотеки, по которой человек получает вычет, реальная стоимость долга ≈ $r\cdot(1-0{,}13)$ до исчерпания лимита. Модель сравнивает **после**налоговую доходность вклада с **до**налоговой ставкой ипотеки — асимметрия в сторону досрочки.
3. **Номинал против номинала — корректно.** Ставка кредита и ставка вклада обе номинальные, инфляция в сравнении сокращается (эффект Фишера, канон §10, стр. 400). Здесь ошибки нет.
4. **Спот против горизонта.** Решение «гасить кредит на 5 лет» сравнивает ставку кредита на весь срок с ключевой **на сегодня**. Прогнозируемость ключевой ставки — отдельное сырьё `key_rate_history_forecastability_2026-09-10.md`; здесь фиксируется только то, что порог — моментальный снимок, а решение — многолетнее.
5. **Мелкое.** Ставка кредита в модели — номинальная годовая с помесячным начислением (`amortization.py`: `rate/12`), ключевая — годовая; при 20 % номинальных эффективная годовая 21,9 %. Разница порядка 1–2 п.п. на высоких ставках, в пользу недооценки дорогого долга.

**Итог пункта 4.** Avalanche на текущих допущениях модели не проигрывает (0 из 3000); разрыв Rios-Solis появится вместе с нерегулярным доходом и просрочками, которых модель не видит. Реальные дефекты — в окружении: критерий SAW меряет не то, что оптимизирует Avalanche; график §10.5 теряет освободившиеся платежи (экономия занижена до 2 раз); порог $r_{bench}$ ошибочно облагает налогом необлагаемые проценты и не учитывает ипотечный вычет — оба смещения толкают к досрочке.

### Скрипты пункта 4 (дословно)

**p4.py**

```python
"""G40 p.4: avalanche vs best priority order under fixed minimum payments and fixed monthly budget;
plus a conservation check of app.core.amortization._simulate (freed payment cascade)."""
import sys, random, itertools
from decimal import Decimal
sys.path.insert(0, "/Users/vasyaevdokimov/repos/personal-finance-dss")
from app.core.amortization import _simulate

def sim(loans, order, extra, cap=600):
    """Money-conserving simulation: constant budget = sum of min payments + extra; freed payments cascade."""
    bal = [l[0] for l in loans]; r = [l[1] / 12 for l in loans]; P = [l[2] for l in loans]
    budget = sum(P) + extra; interest = 0.0; m = 0
    while any(b > 1e-6 for b in bal) and m < cap:
        m += 1; spent = 0.0
        for i in range(len(loans)):
            if bal[i] <= 1e-6: continue
            it = bal[i] * r[i]; interest += it; bal[i] += it
            pay = min(P[i], bal[i]); bal[i] -= pay; spent += pay
        pool = budget - spent
        for i in order:
            if pool <= 1e-9: break
            if bal[i] <= 1e-6: continue
            a = min(pool, bal[i]); bal[i] -= a; pool -= a
    return interest, m

rng = random.Random(4040); gaps = []; worst = None; n = 0
for _ in range(3000):
    k = rng.randint(2, 4); loans = []
    for _ in range(k):
        bal = rng.uniform(10_000, 800_000); rate = rng.uniform(0.15, 0.60)
        term = rng.choice([6, 12, 24, 60, 120]); rm = rate / 12
        pay = bal * rm / (1 - (1 + rm) ** -term)
        loans.append((bal, rate, pay))
    extra = rng.uniform(2_000, 40_000)
    aval = sorted(range(k), key=lambda i: -loans[i][1])
    ia, ma = sim(loans, aval, extra)
    if ma >= 600: continue
    best = min((sim(loans, list(p), extra) + (list(p),) for p in itertools.permutations(range(k))), key=lambda t: t[0])
    n += 1
    gap = (ia - best[0]) / best[0] if best[0] > 0 else 0.0
    gaps.append(gap)
    if worst is None or gap > worst[0]:
        worst = (gap, loans, extra, ia, best)
gaps.sort(); q = lambda p: gaps[int(p * (len(gaps) - 1))]
nz = sum(1 for g in gaps if g > 1e-6)
print("A instances:", n, " avalanche not best among priority orders:", nz, "(%.1f%%)" % (100 * nz / n))
print("A interest gap vs best order: p50=%.4f%% p90=%.3f%% p99=%.2f%% max=%.2f%%" % (100 * q(.5), 100 * q(.9), 100 * q(.99), 100 * gaps[-1]))
g, loans, extra, ia, best = worst
print("A worst instance: loans (balance, rate, min payment):", [(round(b), round(r, 3), round(p)) for b, r, p in loans], "extra", round(extra))
print("   avalanche interest %.0f; best order %s interest %.0f" % (ia, best[2], best[0]))

# (B) conservation check of the product simulator: loan closes by its own min payment -> is the whole payment 'freed'?
obls = [{"id": "small", "amount": 1_000, "interest_rate": 0.0, "monthly_payment": 5_000},
        {"id": "big", "amount": 100_000, "interest_rate": 0.20, "monthly_payment": 2_000}]
m_prod, i_prod, _, _ = _simulate(obls, ["big", "small"], extra_monthly=1.0, cascade_freed=True, horizon_months=360)
i_ok, m_ok = sim([(1_000, 0.0, 5_000), (100_000, 0.20, 2_000)], [1, 0], 1.0)
print("B product _simulate: months=%d interest=%.2f | money-conserving sim: months=%d interest=%.2f" % (m_prod, float(i_prod), m_ok, i_ok))
```

**Вывод p4.py:**
```
A instances: 3000  avalanche not best among priority orders: 0 (0.0%)
A interest gap vs best order: p50=0.0000% p90=0.000% p99=0.00% max=0.00%
A worst instance: loans (balance, rate, min payment): [(273223, 0.48, 11025), (437089, 0.499, 18323)] extra 15351
   avalanche interest 457164; best order [1, 0] interest 457164
B product _simulate: months=95 interest=95060.21 | money-conserving sim: months=17 interest=15475.91
```

**p4b.py**

```python
"""G40 p.4b: realistic check of the freed-payment cascade in app.core.amortization vs a money-conserving simulation."""
import sys, random
sys.path.insert(0, "/Users/vasyaevdokimov/repos/personal-finance-dss")
from app.core.amortization import build_debt_amortization_schedule
exec(open("/private/tmp/claude-501/-Users-vasyaevdokimov-repos-personal-finance-dss/fe25aad2-149b-48bd-a8b2-c62cc04ce4a1/scratchpad/g40/p4.py").read().split("rng = random.Random(4040)")[0])

def ann(b, r, n):
    rm = r / 12
    return b * rm / (1 - (1 + rm) ** -n)

cases = {
    "card+cash loan": [("card", 60_000, 0.30, 3_000), ("cash", 500_000, 0.20, ann(500_000, 0.20, 60))],
    "three loans": [("mfo", 30_000, 0.90, 6_000), ("card", 150_000, 0.35, 7_500), ("car", 900_000, 0.17, ann(900_000, 0.17, 60))],
}
for name, ls in cases.items():
    obls = [{"id": i, "amount": b, "interest_rate": r, "monthly_payment": p} for i, b, r, p in ls]
    for extra in (5_000, 15_000):
        s = build_debt_amortization_schedule(obls, extra, r_bench=0.14)
        order = sorted(range(len(ls)), key=lambda k: -ls[k][2])
        i_ok, m_ok = sim([(b, r, p) for _, b, r, p in ls], order, extra)
        i_base, m_base = sim([(b, r, p) for _, b, r, p in ls], order, 0.0)
        print("%-15s extra=%6d | product: accel months=%3d interest=%9.0f saved=%9.0f | conserving cascade: months=%3d interest=%9.0f saved vs product-baseline=%9.0f"
              % (name, extra, s.accelerated_months, s.accelerated_total_interest, s.interest_saved, m_ok, i_ok, s.baseline_total_interest - i_ok))
```

**Вывод p4b.py:**
```
card+cash loan  extra=  5000 | product: accel months= 41 interest=   212223 saved=   106809 | conserving cascade: months= 36 interest=   187812 saved vs product-baseline=   131220
card+cash loan  extra= 15000 | product: accel months= 24 interest=   121918 saved=   197114 | conserving cascade: months= 22 interest=   112422 saved vs product-baseline=   206610
three loans     extra=  5000 | product: accel months= 50 interest=   421827 saved=   107674 | conserving cascade: months= 35 interest=   315231 saved vs product-baseline=   214271
three loans     extra= 15000 | product: accel months= 35 interest=   297567 saved=   231935 | conserving cascade: months= 26 interest=   232355 saved vs product-baseline=   297146
```
---

## Пункт 5. Прогноз: SES/Holt + Монте-Карло, окно месяца, номинал и реальные величины

**Сначала о месте прогноза в модели.** Прогноз в выбор плана не входит (1.7): `run_planning` его не вызывает, он живёт на эндпоинте `/forecast`
(`app/api/routes_planning.py:696`) и в демо. Значит его дефекты бьют по экрану прогноза и по сигналу «через N месяцев дефицит», но не по распределению денег.
Исключение — **окно «текущего месяца»** (5.1): оно общее для плана и прогноза.

### 5.1. «Месяц» = последние 30 суток: у человека со стабильной зарплатой раз в месяц может «исчезнуть» доход 🔴🔴

**Аналогия.** Считать, сколько ты зарабатываешь в месяц, заглядывая ровно на 30 суток назад. Если зарплата приходит 5-го, а между 5 августа и 5 сентября 31 день, то вечером 4 сентября в окне нет ни одной зарплаты.

**Суть.** `app/core/preprocessing.py::prepare_data` берёт транзакции за `[now − 30 суток, now]` (стр. 108–112), и из них считаются $I_t$, $E_t$, а значит $R_t$ и режим (кризис или нет).

**Число** (`p5b.out`; зарплата 100 000 ₽ 5-го числа каждого месяца в 00:00, траты 2 000 ₽ в день):

| Момент расчёта | Доход в окне | Расход в окне |
|---|---:|---:|
| 04.09.2026 00:00 | 100 000 | 62 000 (31 день) |
| **04.09.2026 23:00** | **0** | 60 000 |
| 05.09.2026 01:00 | 100 000 | 60 000 |

В 23:00 4 сентября человек со стабильной зарплатой получает $I_t = 0$ → $R_t = -60\,000$ → **кризисный режим, тяжесть `critical` («нулевой доход»)**, совет резать расходы.
Любой месяц из 31 дня даёт такое окно. Расходы при этом «плавают» на 3,3 % в зависимости от часа (31 или 30 дней в окне, границы включены с обеих сторон).

Та же нарезка в истории (`services/forecasting.py::build_monthly_history`, окна по 30 суток): `p5.py` блок A — при расчёте 04.09.2026 последний «месяц» истории = **0** ₽;
при расчёте 03.03.2026 один из прошлых «месяцев» = 0 (февраль короткий). Holt на истории `[100 000 ×7, 0]` прогнозирует **49 200 → 39 480 → 30 732 ₽** — падение дохода, которого нет.

**Насколько серьёзно.** Очень высоко: ложный кризис у самого обычного пользователя. Это не формула канона, а слой данных, но он определяет вход в формулы; канон §2.1 говорит «совокупный месячный приток» и не определяет, что такое месяц.

### 5.2. Holt с зашитыми параметрами на 3–8 точках выдумывает тренд 🟡

**Литература.** Hyndman & Athanasopoulos, *Forecasting: Principles and Practice*, 3rd ed., §8.1, `https://otexts.com/fpp3/ses.html` — HTTP 200 через `curl` (через `r.jina.ai` — капча), 17.09.2026, дословно:
> «This method is suitable for forecasting data with no clear trend or seasonal pattern.»
> «In some cases, the smoothing parameters may be chosen in a subjective manner — the forecaster specifies the value of the smoothing parameters based on previous experience. However, a more reliable and objective way to obtain values for the unknown parameters is to estimate them from the observed data.»

**У нас.** SES α=0,3 (канон §15, стр. 590) и Holt α=0,4, β=0,3, φ=0,9 (стр. 902–903; `core/forecast.py:26–28`) — **константы, не оценённые по данным**; канон называет α=0,3 «типичным для месячных финансовых рядов» (стр. 591) без источника. Holt включается уже при 3 точках (`forecast.py:86`).

**Число** (`p5.py` блок B): 5000 историй из 8 месяцев истинно **плоского** дохода 100 000 ₽ с шумом 5 %. Прогноз Holt на 6 месяцев: 5-й–95-й перцентили ошибки **−9,4 % … +8,9 %**, у **36,9 %** историй ошибка больше 5 %. Простое среднее тех же 8 точек дало бы стандартную ошибку ≈1,8 %. То есть демпфированный тренд на коротком шумном ряду в 4–5 раз хуже «ничего не делать».
**Когда истории нет вовсе** (`p1b.py` блок B): `build_history_from_current` синтезирует 6 точек с шумом 5 % на фиксированных сидах (`forecast.py:123–135`), и Holt по ним предсказывает человеку падение расходов **с 60 000 до 47 784 ₽ за 6 месяцев (−20 %)** — тренд, созданный генератором случайных чисел.

**Сезонность.** Ни SES, ни Holt её не моделируют; 13-я зарплата, отпуск, декабрь, налоговый вычет — всё это для модели «тренд». При 8 месяцах истории сезонную компоненту оценить нельзя в принципе (нужен хотя бы год) — это ограничение данных, его надо назвать, а не лечить.

### 5.3. Монте-Карло: ширина коридора не зависит от человека, распределение нормальное 🔴

**Суть.** `monte_carlo_intervals` (`forecast.py:99–120`): $\sigma = |\hat y|\cdot 0{,}05\cdot\sqrt{1+0{,}5h}$ — **5 % от точечного прогноза для всех**, шум нормальный. В каноне (§15, стр. 595–596) $\sigma_0$ не раскрыт; что это фиксированные 5 %, видно только в коде.

**Число** (`p5.py` блок C). История дохода фрилансера `[70, 130, 60, 140, 100, 100, 55, 145]` тыс. ₽ (CV = 0,34). Честный 80 %-й коридор на следующий месяц — примерно **±43 000 ₽**. Модель даёт **±7,8 % от точки** — у всех, при любой истории. Та же модель в floor резерва (§8) CV уже считает — в прогноз он не протянут.
Плюс: коридор пропорционален $|\hat y|$, поэтому при потоке около нуля (а это самые рискованные люди) коридор **схлопывается в точку**.
**1000 прогонов не нужны:** при нормальном шуме p10/p90 = точка ± 1,2816σ считаются формулой; прогон даёт 45 899 / 53 994 против аналитических 46 076 / 53 924 — МК добавляет только шум выборки.

**Литература о распределении.** Guvenen, Karahan, Ozkan, Song, «What Do Data on Millions of U.S. Workers Reveal about Life-Cycle Earnings Risk?», NBER WP 20913, DOI 10.3386/w20913, `https://www.nber.org/papers/w20913` — HTTP 200, 17.09.2026, дословно:
> «earnings shocks display substantial deviations from lognormality---the standard assumption in the incomplete markets literature. In particular, earnings shocks display strong negative skewness and extremely high kurtosis---as high as 30 compared with 3 for a Gaussian distribution. The high kurtosis implies that in a given year, most individuals experience very small earnings shocks, and a small but non-negligible number experience very large shocks.»
Для совета «сколько держать в подушке» важны как раз редкие большие провалы (потеря работы), а нормальное распределение их занижает. (Данные США, годовые заработки; для месячного потока домохозяйства в РФ прямых данных в этом батче нет.)

**Рост $\sigma$ с горизонтом.** $\sqrt{1+0{,}5h}$ не выводится ни из модели случайного блуждания (там $\sqrt{h}$), ни из независимых месячных шоков (там роста нет для потока и $\sqrt{h}$ для накопленного запаса). В прогнозе при этом поле `Rt` — смесь запаса и потока (1.4), так что «правильный» закон роста определить нельзя, пока не разведены величины.

### 5.4. Волатильность дохода: нулевые месяцы выбрасываются — у самых нестабильных CV занижен 🔴

`ranking.income_cv` (стр. 98): `nonzero = [v for v in income_history if v > 0]`. Докстрока объясняет это как «ведущие нули — отсутствие данных», но фильтр выбрасывает **все** нули, включая месяцы в середине ряда.
**Число** (`p5.py` блок D): фрилансер `[120, 0, 90, 150, 0, 110, 130, 100]` тыс. ₽ — два месяца без дохода из восьми. `income_cv` = **0,169** (ниже порога 0,3 → floor не растёт). CV с нулями = **0,609** (floor вырос бы на полный +1 месяц). Правило ADR-015 существует ради нерегулярного дохода и **не срабатывает у человека с пустыми месяцами** — ровно у того, кому подушка нужнее всего. Ведущие нули уже отрезаются в `build_monthly_history` (стр. 66–69), второй фильтр в `income_cv` лишний и вредный.

### 5.5. Номинал против реальных величин (Г30.2-К)

- **В выборе плана** номинал и реал почти не смешаны: доходы, расходы, платежи, ставки кредитов и $r_{bench}$ — всё номинальное, сравнение ставок корректно (4.4 п. 3).
- **Инфляция целей** вводится только для целей дальше 36 мес. (§11.3). Внутри решения её эффект гасится min-max (3.2): $S_n$ безразмерен, поэтому индексация меняет только кэпы и деление между целями. `p2b.py` блок D: срок цели 1079…1085 дней — победитель и деление не изменились; канон сам фиксирует смену победителя в 0,23 % портретов (стр. 53).
- **Но есть обрыв:** 36 мес. ровно — индекс 1,00; 36 мес. и один день — 1,125 (`p2.py`/инлайн-замер: 2 000 000 → 2 249 973 ₽). Утверждение канона, что до 3 лет «инфляционный снос тонет в шуме прогноза» (стр. 468), при 4 %/год даёт 12,5 % на границе — это не шум. Непрерывная форма $T\cdot1{,}04^{\tau/12}$ для всех сроков обрыв убирает.
- **Накопления на целях не растут.** $C_s$ в $S_n$ и кэпы не получают процента, хотя подушку прогноз капитализирует по $r_{bench}$ (стр. 905–906). Номинальный рубль в цели на 10 лет «стоит» в модели столько же, сколько рубль, положенный завтра; при индексированной цели это завышает требуемый взнос. На выбор направления опять почти не влияет (min-max), на показ «сколько осталось копить» — влияет.
- Graf–Kling–Russ 2024 и Hanna et al. 2017 (вход Г30.2) говорят о разном порядке альтернатив в номинале и реале для долгосрочных накоплений; у нас долгосрочные накопления — инвест-транш (§13), который строится **после** выбора, так что основной канал их находки в ядро не попадает.

**Итог пункта 5.** Самое опасное — не метод прогноза, а определение «месяца» (ложный кризис у стабильного зарплатника) и выбрасывание нулевых месяцев из CV. Прогнозный экран: поток смешан с запасом, тренд выдуман на коротком шумном ряду, коридор одинаковый для всех и нормальный. Номинал/реал в решении почти согласованы, с одним обрывом на 36 месяцах.

### Скрипт пункта 5 (дословно)

**p5.py**

```python
"""G40 p.5: 30-day binning vs calendar salary, Holt on flat noisy history, MC interval vs analytic, CV with zero months."""
import sys, random, statistics
from datetime import datetime, timedelta
from types import SimpleNamespace as T
sys.path.insert(0, "/Users/vasyaevdokimov/repos/personal-finance-dss")
from app.services.forecasting import build_monthly_history
from app.core.forecast import holt_forecast, monte_carlo_intervals
from app.core.ranking import income_cv

# (A) salary 100 000 on the 5th of each month, 12 months back; expenses 2 000/day
for now in (datetime(2026, 9, 17), datetime(2026, 9, 4), datetime(2026, 3, 3)):
    tx = []
    d = now - timedelta(days=400)
    while d <= now:
        if d.day == 5:
            tx.append(T(date=d, amount=100_000, type="income"))
        tx.append(T(date=d, amount=2_000, type="expense"))
        d += timedelta(days=1)
    h = build_monthly_history(tx, months=8, now=now)
    print("A now=%s income bins (old->new): %s  CV(income_cv)=%s" % (now.date(), [int(x) for x in h["income"]], income_cv(h["income"])))

# (B) Holt with fixed alpha/beta/phi on a FLAT true income with 5%% noise, 8 months: how far is h=6 from the truth?
rng = random.Random(5); devs = []
for _ in range(5000):
    hist = [100_000 * (1 + rng.gauss(0, 0.05)) for _ in range(8)]
    devs.append(holt_forecast(hist, horizon=6)[-1] / 100_000 - 1)
devs.sort(); q = lambda p: devs[int(p * (len(devs) - 1))]
print("B Holt h=6 relative error on flat series: p5=%.3f p50=%.3f p95=%.3f  share |err|>5%%: %.1f%%  (SES-mean would have sd ~ %.3f)"
      % (q(.05), q(.5), q(.95), 100 * sum(1 for x in devs if abs(x) > 0.05) / len(devs), 0.05 / 8 ** 0.5))

# (C) MC interval does not depend on history volatility; analytic Normal quantile
iv = monte_carlo_intervals([50_000.0], horizon=1)
print("C MC p10/p90 for point 50 000:", iv[0], " analytic +-1.2816*sigma:", round(50_000 - 1.2816 * 50_000 * 0.05 * 1.5 ** 0.5), round(50_000 + 1.2816 * 50_000 * 0.05 * 1.5 ** 0.5))
hist = [70_000, 130_000, 60_000, 140_000, 100_000, 100_000, 55_000, 145_000]
print("   history CV (population) = %.3f -> an honest 80%% band for next month income ~ +-%.0f RUB; model band width is +-%.1f%% of point regardless"
      % (statistics.pstdev(hist) / statistics.mean(hist), 1.2816 * statistics.pstdev(hist), 100 * 1.2816 * 0.05 * 1.5 ** 0.5))

# (D) CV ignores zero-income months (freelancer with 2 empty months out of 8)
fr = [120_000, 0, 90_000, 150_000, 0, 110_000, 130_000, 100_000]
nz = [x for x in fr if x > 0]
print("D freelancer history", fr, " income_cv =", round(income_cv(fr), 3), " CV incl. zeros =", round(statistics.pstdev(fr) / statistics.mean(fr), 3))
```

**Вывод p5.py:**
```
A now=2026-09-17 income bins (old->new): [100000, 100000, 100000, 100000, 100000, 100000, 100000, 100000]  CV(income_cv)=0.0
A now=2026-09-04 income bins (old->new): [100000, 100000, 100000, 100000, 100000, 100000, 100000, 0]  CV(income_cv)=0.0
A now=2026-03-03 income bins (old->new): [100000, 0, 100000, 100000, 100000, 100000, 100000, 100000]  CV(income_cv)=0.0
B Holt h=6 relative error on flat series: p5=-0.094 p50=-0.000 p95=0.089  share |err|>5%: 36.9%  (SES-mean would have sd ~ 0.018)
C MC p10/p90 for point 50 000: {'p10': 45899.22, 'p50': 49943.46, 'p90': 53994.01}  analytic +-1.2816*sigma: 46076 53924
   history CV (population) = 0.336 -> an honest 80% band for next month income ~ +-43105 RUB; model band width is +-7.8% of point regardless
D freelancer history [120000, 0, 90000, 150000, 0, 110000, 130000, 100000]  income_cv = 0.169  CV incl. zeros = 0.609
```

**Замер окна месяца (инлайн-скрипт, дословно):**

```python
import sys; sys.path.insert(0,'.')
from datetime import datetime, timedelta
from types import SimpleNamespace as T
from app.core.preprocessing import prepare_data
from app.core.metrics import calculate_income_total, calculate_expense_total
for now in (datetime(2026,9,4,0,0), datetime(2026,9,4,23,0), datetime(2026,9,5,1,0)):
    tx=[]; d=datetime(2026,5,1)
    while d<=now:
        if d.day==5: tx.append(T(date=d, amount=100000, type='income', category='salary', description='', is_recurring=True))
        tx.append(T(date=d, amount=2000, type='expense', category='food', description='', is_recurring=False))
        d+=timedelta(days=1)
    p=prepare_data(transactions=tx, obligations=[], goals=[], now=now)
    print(now, 'income', calculate_income_total(p['transactions']), 'expense', calculate_expense_total(p['transactions']))
# Holt on trailing zero: holt_forecast([100000]*7+[0], horizon=3) -> [49200, 39480, 30732]
```

**Вывод:**
```
2026-09-04 00:00:00 income 100000.0 expense 62000.0
2026-09-04 23:00:00 income 0.0 expense 60000.0
2026-09-05 01:00:00 income 100000.0 expense 60000.0
```
---

## Пункт 6. Кризисный режим и цели

### 6.1. Логика переключения режима

- **Порог.** Кризис — при $R_t < -0{,}005$ ₽ (`planning.py:86`), решётка — при $R_t \ge 0$; между ними одна альтернатива «Дефицитный бюджет» без действий (1.7). Гистерезиса нет: человек, чей поток колеблется около нуля, получает три разных типа совета подряд (2.3).
- **Разные floor в двух режимах** — 1.6 (кризис не знает G8 и ADR-015). 🔴
- **Разные правила разлива по кредитам** — кризис по $P/A$, основной режим по ставке (4.2). 🟡
- **Ложный вход в кризис** из-за 30-суточного окна — 5.1. 🔴🔴

### 6.2. Балансовый ход «всё или ничего» 🔴

**Суть.** `crisis._close_debts_from_liquidity` возвращает ход только если дефицит закрывается **полностью** (стр. 108: `if recovered + 1e-9 < deficit: return None`). Частичное погашение, которое **уменьшило бы** дефицит, отбрасывается целиком, и совет «сократите расходы» считается на весь дефицит.

**Пример** (`p6.py` блок A, человек из 1.6): дефицит 5 000 ₽, сверх floor доступно 10 000 ₽; погасив ими МФО (платёж 20 % остатка в месяц), человек снизил бы платёж на 2 000 ₽ и резал бы расходы на 3 000, а не на 5 000. План: `cut_expenses 5000` + `restructure_debt`, погашения нет.

### 6.3. «Жадность по $P/A$ оптимальна» — утверждение канона противоречит политике полного закрытия 🟡

Канон §12 (стр. 494): жадный порядок по $P/A$ «минимизирует расход ликвидности и потому оптимален»; там же: «Политика суммы: полное закрытие, если доступной ликвидности хватает на весь кредит». Одно исключает другое.
**Пример** (`p6.py` блок B): дефицит 1 000 ₽, кредит 100 000 ₽ с платежом 5 000 ₽, подушка 300 000 ₽. Достаточно погасить **20 000 ₽**; модель тратит **100 000 ₽** и выводит поток в +4 000 ₽. Как продуктовое решение («без огрызка долга») — допустимо, но тогда это не минимизация ликвидности, и слово «оптимален» в каноне неверно. Сама жадность по $P/A$ для задачи «минимум ликвидности при линейной отдаче с потолком» — это дробный рюкзак, и там она действительно оптимальна (тот же класс, что Fox 1966, Теорема 2).

### 6.4. Разовое закрытие близкой цели тратит подушку ниже floor 🔴

**Суть.** Этап 4.0 (§11.5; `goals_priority.preallocate_from_bliq`) закрывает цели со сроком ≤ 3 мес., если их сумма ≤ 50 % $B^{liq}$ — **не глядя на floor**. Floor (§8) — «стартовый запас, который риск-профиль не отменяет» (стр. 304).
**Пример** (`p6.py` блок C): доход 100 000 ₽, расходы 60 000 ₽ (floor = 120 000 ₽), подушка 100 000 ₽ — floor уже не выполнен. Цель «Отпуск» (эмоциональная, вес 0,5) 50 000 ₽ через 2 месяца. Модель **закрывает отпуск из подушки** → подушка 50 000 ₽ (0,83 мес.) → и сразу отправляет **весь** месячный поток в резерв (`a0100`), чтобы её восстанавливать. Два шага одного плана противоречат друг другу, и самый низкий по канону приоритет (эмоциональная цель) обгоняет самый высокий (floor).

### 6.5. Цель «подушка» и критерий ликвидности не видят друг друга 🔴

**Суть.** Канон §11.1 (стр. 448) прямо относит «Подушка, страховой резерв» к категории целей `safety`, а §2.3–2.4 и §3.3 исключают деньги целей из $L_t$. Если пользователь завёл подушку как цель — модель её не видит как подушку.
**Пример** (`p6.py` блок D): агрессивный профиль, доход 100 000 ₽, расходы 60 000 ₽, цель «Подушка безопасности» 360 000 ₽, накоплено 200 000 ₽ (3,3 мес.). $L_t$ = **0**, BLR = 3,33. Модель отправляет **все 40 000 ₽ в резерв** (floor не выполнен при нуле), цели — 0 ₽. Человек копит вторую подушку, не достроив первую.

### 6.6. Веса категорий и срочность: обоснованы ли и не противоречат ли основному критерию

- **Происхождение чисел 3,0 / 2,0 / 1,0 / 0,5** (§11.1, стр. 445–452) — ссылка на Becker (1964). Becker — теория отдачи от инвестиций в человеческий капитал; числовой шкалы приоритетов целей домохозяйства канон из неё не цитирует, первоисточник в этом батче не открывался. Статус — **собственное решение с теоретической мотивацией**, не калибровка и не заимствованная шкала.
- **Срочность $u_s = \max(1, 12/\tau)$** (§11.2) — гипербола без источника; цель через месяц весит в 12 раз больше годовой.
- **Главное: оба множителя почти ничего не решают.** Они делят $x_g$ **между** целями; в выборе направления (долг / резерв / цели) после min-max они исчезают (2.2, 3.3). Срочная цель `safety` на 4 месяца проигрывает обычному кредиту под 19 % во всех профилях (3.3). То есть **противоречия с основным критерием нет — есть его отсутствие**: приоритеты целей декларированы, но в главный выбор не пропущены.
- **Кризис замораживает все цели подряд** (`crisis.py:161–168`), включая `safety` («лечение»). Для категории с весом 2,0 это жёстко, но в дефиците объяснимо; в каноне не оговорено.
- Недолитые деньги целей уходят в резерв, а не на соседние цели — канон противоречит сам себе (1.5 б).

**Итог пункта 6.** Кризисная ветка по конструкции правильная (план всегда есть, инвариант I12), но её числа живут отдельно от основного ядра: другой floor, «всё или ничего» в балансовом ходе, завышенное утверждение об оптимальности. Цели: веса и срочность не участвуют в главном выборе; этап 4.0 нарушает floor; цель-подушка невидима для критерия ликвидности.

### Скрипт пункта 6 (дословно)

**p6.py**

```python
"""G40 p.6: crisis all-or-nothing payoff, full-closure vs minimal liquidity, near-goal preallocation vs floor, 'cushion' goal vs reserve."""
import sys
from datetime import datetime, timedelta
sys.path.insert(0, "/Users/vasyaevdokimov/repos/personal-finance-dss")
from app.services.planning import run_planning
from app.core.crisis import build_crisis_plan
TODAY = datetime(2026, 9, 17)

# (A) partial payoff that would shrink the deficit is rejected entirely
loan = {"id": "o1", "name": "МФО", "amount": 50_000, "interest_rate": 1.5, "monthly_payment": 10_000}
p = build_crisis_plan(50_000, 45_000, [loan], [], bliq=100_000, today=TODAY)
print("A deficit 5000, available over 2-mo floor = 10 000 -> could pay 10 000 and save 2 000/mo; plan:",
      [(a["type"], a.get("amount")) for a in p["actions"]])

# (B) 'optimal = minimal liquidity' vs full-closure policy
loans = [{"id": "big", "name": "Кредит", "amount": 100_000, "interest_rate": 0.25, "monthly_payment": 5_000}]
p = build_crisis_plan(60_000, 20_000 + 40_000 + 0, loans, [], bliq=300_000, today=TODAY)  # deficit = 5 000
p = build_crisis_plan(60_000, 56_000, loans, [], bliq=300_000, today=TODAY)  # deficit = 1 000
c = p["actions"][0]
print("B deficit 1000: liquidity spent %s (minimum sufficient would be %d), flow after %s" % (c["bliq_used"], 1_000 / 0.05, c["new_rt"]))

# (C) near-goal preallocation spends the cushion below the floor on an emotional goal
goals = [{"id": "v", "name": "Отпуск", "target_amount": 50_000, "current_amount": 0, "deadline": TODAY + timedelta(days=60), "category": "emotional"}]
r = run_planning(100_000, 60_000, [], goals, bliq=100_000, r_bench=0.14, today=TODAY)
bp = r["bliq_preallocation"]
print("C floor = 2 mo = 120 000; bliq before 100 000; closed goals:", [g["name"] for g in bp.get("closed_goals", [])],
      "; Bliq after:", r["indicators"]["Bliq"], "; Lt after:", r["indicators"]["Lt"], "; best split:", r["best"]["id"])

# (D) a 'safety' goal named cushion is invisible to the liquidity criterion
goals = [{"id": "c", "name": "Подушка безопасности", "target_amount": 360_000, "current_amount": 200_000, "deadline": None, "category": "safety"}]
r = run_planning(100_000, 60_000, [], goals, bliq=0, r_bench=0.14, risk_tolerance=5, today=TODAY)
print("D goal 'cushion' holds 200 000 (3.3 mo); Lt =", r["indicators"]["Lt"], "BLR =", r["indicators"]["BLR"], "; best:", r["best"]["id"],
      "x_reserve_eff:", r["best"]["x_reserve_effective"], "goals:", r["best"]["goal_allocation"])
```

**Вывод p6.py:**
```
A deficit 5000, available over 2-mo floor = 10 000 -> could pay 10 000 and save 2 000/mo; plan: [('cut_expenses', 5000.0), ('restructure_debt', None)]
B deficit 1000: liquidity spent 100000.0 (minimum sufficient would be 20000), flow after 4000.0
C floor = 2 mo = 120 000; bliq before 100 000; closed goals: ['Отпуск'] ; Bliq after: 50000.0 ; Lt after: 0.8333 ; best split: a0100
D goal 'cushion' holds 200 000 (3.3 mo); Lt = 0.0 BLR = 3.33 ; best: a0100 x_reserve_eff: 40000.0 goals: {}
```
---

## Пункт 7. Численная устойчивость реализации

### 7.1. `float` против `Decimal` в ядре — сохранение денег выдержано 🟢

**Аналогия.** Кассир, который считает на калькуляторе с плавающей точкой: вопрос не «идеальны ли цифры», а «сходится ли касса до копейки».

`app/core/money.py` (стр. 8–9) прямо фиксирует решение: безразмерное ядро выбора — `float`, деньги на границах — `Decimal` с ROUND_HALF_UP; накопительная арифметика графика (§10.5) — `Decimal` (`amortization.py`, докстрока).
**Число** (`p7.py` блок C): 3000 портретов на трёх масштабах (×1, ×1000, ×1 000 000 к рублёвым суммам), 198 000 альтернатив. Проверка инварианта сохранения §10.4 (стр. 398): $x_d^{eff} + \sum_s x_{g,s} + x_r^{eff} = R_t^+$. Расхождений больше 5 копеек — **0**, даже при доходах порядка сотен миллиардов. Двоичная погрешность `float` на реальных суммах несущественна.

### 7.2. Округления ДО сравнения — вот где численный дефект 🟡

- `Dt_new` округляется до 4 знаков **до** min-max (`alternatives.py:237`) → диапазон долгового критерия квантуется, при малом $\delta P$ схлопывается в одно значение (1.1: пример, где $\hat R$ меняется, а $\hat D$ константа; расхождение $\hat R$ и $1-\hat D$ до 0,033 в 10 % портретов).
- `utility` округляется до 4 знаков **до** сортировки (`ranking.py:180`) → искусственные ничьи на первом месте в 3,2 % портретов (1.7), разрешаемые порядком генерации.
- `Lt_new` — 4 знака, `floor_level` — 6 знаков (`ranking.py:182`): при расходах 1 000 000 ₽/мес. шаг 1e-6 месяца = 1 ₽ — терпимо.
Лечится одним правилом: округлять только то, что показывается, а сравнивать неокруглённое.

### 7.3. Деление на ноль и крайние входы

| Вход | Что происходит | Оценка |
|---|---|---|
| $I_t = 0$ | ПДН = 1,0 в `metrics` (G7), 0 в `alternatives`/прогнозе (1.7) | 🟡 несогласованность |
| $E_t = 0$ при подушке 500 000 ₽ (`p7.py` D) | $L_t$ = 0, BLR = 0 → «подушки нет» | 🟡 неверный показ; решение не страдает (без долгов и целей альтернатива одна) |
| $\max=\min$ в нормализации | `normalize_value` возвращает 1,0 всем (`ranking.py:131–132`) | 🟢 ранжирование не меняет; `utility` на экране завышен на вес «мёртвого» критерия — канон (стр. 271) говорит «константа», не «единица» |
| Срок цели в прошлом | $\tau$ = max(1, …) → срочность 12 | 🟢 разумно |
| Цель через 900 лет (`p7.py` D) | $T^{fut}$ = 3,6·10²¹ ₽, без падения; план «всё в цели» | 🟡 нет верхней границы срока |
| $R_t$ = 0,01 ₽ | 66 альтернатив по 0,00 ₽, ничьи | 🟢 безвредно |
| Переполнение | `Decimal` в графике, кап 360 мес.; степени инфляции до ~10²¹ — в пределах `float` | 🟢 |

### 7.4. Входные схемы пропускают NaN, бесконечность и отрицательный доход 🔴

**Число** (`p7.py` блок A, pydantic-схемы `app/schemas/*`):
- `TransactionCreate(amount=nan)` — **принято**; `amount=inf` — **принято**; `amount=-5000, type="income"` — **принято** (`transaction.py:10`: `amount: float` без ограничений).
- `ObligationCreate(amount=inf)` — **принято** (`ge=0` пропускает бесконечность); `interest_rate=nan` — отклонено.
- `GoalCreate(target_amount=inf)` — **принято**.
Что делает ядро, если такое дошло (блок B): ставка NaN → кредит молча исключается из лавины, «всё в резерв», `utility` = 1,0 без ошибки; цель = ∞ → $S_n$ = 0, план 50/50 резерв/цели без ошибки. **Fail-loud нет**: модель выдаёт правдоподобный ответ на бессмысленный вход. Дошло ли это до БД (колонки `Numeric(14,2)`) — в этом батче не проверялось; на уровне схем защита отсутствует.

**Итог пункта 7.** Денежная арифметика ядра держит копейку на любых масштабах — надёжно. Дефекты — в округлении до сравнения (ложные ничьи, схлопывание критерия), в несогласованной обработке $I=0$ и $E=0$, и в том, что схемы ввода пропускают NaN/∞/отрицательный доход, а ядро молча считает на них.

### Скрипт пункта 7 (дословно)

**p7.py**

```python
"""G40 p.7: numerical robustness: NaN/inf through schemas, conservation of roubles, extreme magnitudes, zero expenses, far deadlines."""
import sys, random, math, warnings
from datetime import datetime, timedelta
sys.path.insert(0, "/Users/vasyaevdokimov/repos/personal-finance-dss")
warnings.filterwarnings("ignore")
from app.schemas.transaction import TransactionCreate
from app.schemas.obligation import ObligationCreate
from app.schemas.goal import GoalCreate
from app.services.planning import run_planning
TODAY = datetime(2026, 9, 17)

# (A) do the input schemas let NaN / inf through?
for label, fn in [
    ("Transaction amount=nan", lambda: TransactionCreate(amount=float("nan"), type="income", category="x", date=TODAY, description="")),
    ("Transaction amount=inf", lambda: TransactionCreate(amount=float("inf"), type="income", category="x", date=TODAY, description="")),
    ("Transaction amount=-5000 income", lambda: TransactionCreate(amount=-5000, type="income", category="x", date=TODAY, description="")),
    ("Obligation amount=inf", lambda: ObligationCreate(name="x", amount=float("inf"), interest_rate=0.2, monthly_payment=1000)),
    ("Obligation interest_rate=nan", lambda: ObligationCreate(name="x", amount=1000, interest_rate=float("nan"), monthly_payment=100)),
    ("Goal target=inf", lambda: GoalCreate(name="x", target_amount=float("inf"), category="material")),
]:
    try:
        fn(); print("A ACCEPTED :", label)
    except Exception as e:
        print("A rejected :", label, "->", type(e).__name__)

# (B) what the engine does with a NaN rate / inf target
try:
    r = run_planning(100_000, 50_000, [{"id": "o", "name": "x", "amount": 100_000, "interest_rate": float("nan"), "monthly_payment": 5_000}], [], bliq=200_000, today=TODAY)
    b = r["best"]; print("B nan rate -> best", b["id"], "x_obl_eff", b["x_obl_effective"], "utility", b["utility"])
except Exception as e:
    print("B nan rate -> exception", type(e).__name__, e)
try:
    r = run_planning(100_000, 50_000, [], [{"id": "g", "name": "x", "target_amount": float("inf"), "current_amount": 0, "deadline": None, "category": "material"}], bliq=200_000, today=TODAY)
    b = r["best"]; print("B inf goal -> best", b["id"], "goal_alloc", b["goal_allocation"], "Si", b["Si"])
except Exception as e:
    print("B inf goal -> exception", type(e).__name__, e)

# (C) conservation: x_obl_eff + goals deployed + x_res_eff == R+ (kopeck tolerance), incl. large magnitudes
rng = random.Random(77); worst = 0.0; n = 0; bad = 0
for _ in range(3000):
    scale = rng.choice([1, 1e3, 1e6])
    inc = rng.uniform(3e4, 5e5) * scale; exp = inc * rng.uniform(0.2, 0.8)
    obls = [{"id": "o", "name": "l", "amount": rng.uniform(1e3, 1e6) * scale, "interest_rate": rng.choice([0.1, 0.2, 0.5]), "monthly_payment": inc * rng.uniform(0.01, 0.15)}]
    goals = [{"id": "g", "name": "g", "target_amount": rng.uniform(1e3, 1e6) * scale, "current_amount": 0, "deadline": None, "category": "material"}]
    r = run_planning(inc, exp, obls, goals, bliq=rng.uniform(0, 5) * exp, r_bench=0.14, risk_tolerance=rng.randint(1, 5), today=TODAY)
    rt = inc - exp - obls[0]["monthly_payment"]
    if rt <= 0: continue
    for a in r["ranked"]:
        n += 1
        tot = a["x_obl_effective"] + sum(a["goal_allocation"].values()) + a["x_reserve_effective"]
        err = abs(tot - rt)
        worst = max(worst, err / scale)
        if err > 0.05: bad += 1
print("C alternatives checked:", n, " sum mismatch > 5 kopecks:", bad, " worst mismatch per unit of scale: %.4f RUB" % worst)

# (D) zero expenses and a goal 900 years away
r = run_planning(100_000, 0.0, [], [], bliq=500_000, today=TODAY)
print("D expenses=0: Lt =", r["indicators"]["Lt"], "BLR =", r["indicators"]["BLR"], "best", r["best"]["id"])
far = TODAY.replace(year=2926)
r = run_planning(100_000, 50_000, [], [{"id": "g", "name": "x", "target_amount": 1_000_000, "current_amount": 0, "deadline": far, "category": "material"}], bliq=500_000, today=TODAY)
print("D goal in 2926: best", r["best"]["id"], "goal alloc", r["best"]["goal_allocation"])
from app.core.goals_priority import inflated_target_amount
print("   inflated target for 2926:", "%.3e" % inflated_target_amount(1_000_000, far, TODAY))
```

**Вывод p7.py:**
```
A ACCEPTED : Transaction amount=nan
A ACCEPTED : Transaction amount=inf
A ACCEPTED : Transaction amount=-5000 income
A ACCEPTED : Obligation amount=inf
A rejected : Obligation interest_rate=nan -> ValidationError
A ACCEPTED : Goal target=inf
B nan rate -> best a0100 x_obl_eff 0.0 utility 1.0
B inf goal -> best a055 goal_alloc {'g': 25000.0} Si 0.0
C alternatives checked: 198000  sum mismatch > 5 kopecks: 0  worst mismatch per unit of scale: 0.0150 RUB
D expenses=0: Lt = 0.0 BLR = 0.0 best a0100
D goal in 2926: best a0010 goal alloc {'g': 50000.0}
   inflated target for 2926: 3.575e+21
```
---

> Продолжение после обрыва по лимиту аккаунта (HTTP 429), 17.09.2026. Пункты 1–7 выше не менялись.

## Пункт 8. Сверка каждого блока канона с литературой: первоисточник, пересказ или собственное решение

**Аналогия.** Библиография в дипломе: одно дело — «взял формулу из статьи и проверил», другое — «сослался на статью, в которой этого нет», третье — «придумал сам и честно так и написал». Все три законны; незаконно только выдавать третье за первое.

**Шкала статуса:**
🟢 **первоисточник** — работа открыта, утверждение канона в ней есть;
🟡 **пересказ / неточная ссылка** — ссылка есть, но в первоисточнике утверждение другое, шире или не проверено;
🔴 **собственное решение** — внешней опоры нет, число выбрано командой или калибровано по согласию с экспертами (замкнутая петля Г31.4).

| Блок канона | Утверждение | Ссылка канона | Статус | Чем подтверждено |
|---|---|---|---|---|
| §3.3 норма $L_t$ ∈ [2,5; 6] | норма автономии | Greninger et al. 1996 | 🟡 | Первоисточник добыт (`calibration_ground_truth_2026-09-10.md` §4.1, FSR 5(1):57–70, HTTP 200): метод — **Delphi-опрос 156 экспертов**, то есть это тоже экспертный консенсус. Плюс внутреннее противоречие канона: §3.3 стр. 165 привязывает норму Greninger к $L_t$, а §18 п. 6 стр. 668 пишет «Ложная привязка $L_t$ к Greninger снята: норма корректно относится к BLR» |
| §3.4, §6, §17 $D_{max}$ = 0,40 | «соответствует Указ. № 4892-У» | ЦБ РФ 4892-У; Fannie Mae DTI 43 % | 🟡 обе ссылки неточны | (а) `rf_household_finance_stats_v2_2026-09-10.md` §4.1: «Нормативного порога 0,40 для гражданина в РФ нет»; 4892-У — методика и надбавки, лимиты ЦБ вокруг 50 % и 80 %; опора 0,40 — эмпирика БКИ (средний ПДН 34,6 %) и Минфин «комфортно 30 %, на грани 50 %». (б) Fannie Mae Selling Guide B3-6-02, `https://selling-guide.fanniemae.com/sel/b3-6-02/debt-income-ratios`, HTTP 200, 17.09.2026, дословно: «For manually underwritten loans, Fannie Mae's maximum total DTI ratio is 36% […] can be exceeded up to 45% […] For loan casefiles underwritten through DU, the maximum allowable DTI ratio is 50%». **Числа 43 % в документе нет** (43 % — порог правила Qualified Mortgage CFPB, в этом батче не открывался). В ядре порог к тому же пуст (1.2) |
| §3.2 $R_t \ge 0$ | не уводить бюджет в минус | — (инвариант) | 🟢 логика | Тавтологичен на решётке (1.2) |
| §4.3 шаг 10 %, 66 точек | «тоньше без потери скорости» | ADR-008 (стенд) | 🔴 | Собственное решение; эмпирически 91 % решений — вершины (2.1) |
| §5.4 non-redundancy, MPI | термины | Roy 1996 | 🟢 термин (тема 15) | Но применён к паре $R$–$L$ и не применён к паре $R$–$D$ (1.1) |
| §0 вето-модель | additive value model with veto | Jiménez-Martín et al. 2015 | 🟡 | Термин верный (тема 15); в коде вето пусто (1.2) |
| §7 min-max | нормализация | Jain et al. 2005 | 🟡 **нерелевантная ссылка** | Crossref: DOI 10.1016/j.patcog.2005.01.012, «Score normalization in multimodal **biometric** systems», *Pattern Recognition* 38(12), 2005. Работа о слиянии оценок биометрических классификаторов, не о весах ЛПР. Нормативная литература MCDA (Fischer 1995; Monat 2009, пункт 3.2) говорит, что min-max с весами «важности» некорректна |
| §7 насыщение $L^*$ | предельная полезность подушки = 0 выше цели | калибровка G1 | 🔴 | Экспертный консенсус (Г31.4) |
| §8 SAW | аддитивная свёртка | Fishburn 1967; Hwang & Yoon 1981 | 🟡 | Crossref: Fishburn P.C., «Methods of Estimating Additive Utilities», *Management Science* 13(7), 1967, DOI 10.1287/mnsc.13.7.435 — обзор способов **оценивать** аддитивную полезность, не «метод SAW»; сам текст в этом батче не открывался. Hwang & Yoon 1981 — каноническая классификация SAW как метода **MADM** (пункт 9) |
| §8 лексикографический floor | некомпенсаторный приоритет | Hwang & Masud 1979 (раздел «Lexicographic Method», по оглавлению) | 🟢 конструкция / 🔴 число | Приём известен (оглавление Hwang & Masud 1979, выдача Exa, пункт 9); значения 2,0 / 1,0 / +CV — калибровка по экспертам |
| §9 веса профилей, $L^*$ 6…3 мес. | | «канон», экспертный коридор | 🔴 | Без внешней опоры; не зависят от диапазонов (3.2) |
| §10 Avalanche | приоритет по ставке | Bach 2003 | 🟡 ссылка / 🟢 результат | В сырье проекта нет ни одного файла с первоисточником Bach 2003 (grep по `docs/research/raw`, 0 совпадений). Оптимальность на наших допущениях подтверждена численно (4.1), границы — Rios-Solis 2017 (🟢), Guasoni & Huang (🟢, тема 14), Brown & Lahey (🟢) |
| §10.2 $r_{bench}$ = ключ × 0,87 | посленалоговая доходность | Brealey–Myers–Allen (NPV) | 🟡 | Принцип альтернативной стоимости — учебник; налоговая часть противоречит НК РФ ст. 214.2 (4.4); ликвидностная премия — Telyukova (🟢, признано каноном) |
| §10.5 график | каскад освободившихся платежей | Bach 2003 | 🟡 | Код каскада расходится с описанием (4.3) |
| §11.1 веса категорий 3/2/1/0,5 | | Becker 1964 | 🔴 с теоретической мотивацией | Числовой шкалы у Becker канон не цитирует (6.6) |
| §11.2 срочность 12/τ | | — | 🔴 | Нет источника |
| §11.3 инфляция 4 %, порог 36 мес. | | цель ЦБ; ступень `instrument_for_horizon` | 🟢 ставка / 🔴 порог | 4 % — официальная цель; обрыв на 36 мес. — собственное (5.5) |
| §12 кризисный план | порядок действий | консенсус экспертизы | 🔴 порядок / 🟢 жадность по $P/A$ | Дробный рюкзак — классический результат; «оптимальность» опровергнута собственной политикой полного закрытия (6.3) |
| §13–14 полка, горизонты 12/36 | | экспертный коридор G5; 177-ФЗ; НК РФ | 🔴 полка / 🟢 АСВ, ИИС | Нормы закона — факт; доли акций — консенсус |
| §15 SES α=0,3; Holt α,β,φ | «типично для финансовых рядов» | Brown 1956; Hyndman 2002; Gardner–McKenzie 1985 | 🟡 | Методы — первоисточники; **значения параметров** — нет; fpp3 §8.1 прямо рекомендует оценивать их по данным (5.2) |
| §15 МК $N(0,\sigma^2)$, σ = 5 %·√(1+0,5h) | | Metropolis & Ulam 1949 | 🔴 | М&У — метод вообще; нормальность противоречит Guvenen et al. (5.3); 5 % не записано в каноне вовсе |
| §15 CI 80 % | | «продуктовая читаемость» | 🔴 честно названо | — |
| §8 CV > 0,3 | | «статистический ориентир фрилансеров» (стр. 640) | 🔴 | Источник не указан; реализация занижает CV (5.4) |
| §20 токсичность max(30 %, r+15 п.п.) | | предрегистрация, раунд 4 | 🔴 | Экспертный консенсус; порождает самый большой разрыв (2.3) |
| §2.1 «месячный доход» | | — | 🔴 не определено | Код — 30 суток; ложный кризис (5.1) |

**Итог пункта 8.** Из ~27 блоков чисто на первоисточниках стоят только юридические факты (АСВ, ИИС, цель по инфляции), классические алгоритмические результаты (жадный шаг для вогнутых задач, аннуитет) и терминология MCDA. Все **числа, которые определяют совет** — веса, floor, $L^*$, токсичность, насыщение, срочность, категории, параметры прогноза — собственные решения или экспертный консенсус, что совпадает с выводом Г31.4. Три ссылки канона **неточны по существу**: ПДН 0,40 не «соответствует 4892-У», у Fannie Mae нет 43 %, Jain et al. 2005 — биометрия. Это правится одной строкой каждая, но на защите их найдут.

---

## Пункт 9. 🔴🔴 Верно ли, что у нас многокритериальный ВЫБОР? MADM или MODM

### 9.0. Прямой ответ

**Гипотеза вахты подтверждена по классификации и уточнена по следствиям.** По определениям первоисточников наша задача — **MODM (задача многокритериального проектирования, design problem)**: альтернативы не выбраны заранее, а порождаются управляющими переменными (три доли) и ограничениями, критерии — функции этих переменных. Решена она **дискретизацией пространства решений (симплекс-решётка с шагом 0,1) и полным перебором со скаляризацией взвешенной суммой** — а скаляризация и нормализация взяты из инструментария MADM (SAW по Hwang & Yoon 1981). Научный руководитель прав, и это не спор о словах: у названия есть три измеримых следствия (9.3). Одно из них — (а) — в формулировке вахты неточно, и число показывает, как именно.

### 9.1. Определения классов — дословно по первоисточникам

**Аналогия.** MADM — выбрать квартиру из пяти объявлений на Циане: варианты уже есть, у каждого известна цена, метраж, район. MODM — спроектировать квартиру самому: варианты не лежат готовыми, их порождают размеры комнат и ограничения бюджета, а цена и метраж **вычисляются** из проекта.

1. **Hwang & Masud (1979)**, *Multiple Objective Decision Making — Methods and Applications*, Springer LNEMS 164, гл. II «Basic Concepts and Terminology», с. 12–13, DOI 10.1007/978-3-642-45511-7_2. Ознакомительные страницы: `https://link.springer.com/chapter/10.1007/978-3-642-45511-7_2`, HTTP 200 (curl), текст через `r.jina.ai`, 17.09.2026. Дословно:
   > «Definition 1: Attributes. Attributes are the characteristics, qualities or performance parameters of alterantives. Multiple attribute decision paroblems involve the selection of the "best" alternative from a pool of preselected alternatives described in terms of their attributes.»
   > «Definition 2: Objectives. Objectives are the directions "to do better" as perceived by the decision maker. […] MODM problems, as a result, involve the design of alternatives which optimize or "best satisfy" the objectives of the DM.»
   (опечатки «alterantives», «paroblems» — в оригинале скана.)
   Там же, гл. I «Introduction», с. 1–2 (`https://link.springer.com/chapter/10.1007/978-3-642-45511-7_1`, HTTP 200), о взвешенной сумме как «традиционном подходе» к векторной задаче максимизации:
   > «The other approach is to optimize a super-objective function created by multiplying each objective function with a suitable weight and then by adding them together. […] Both of the above approaches are ad hoc at best. Often they lead to a solution which may not be the best or most satisfactory. […] For the second approach, the major problem is in determining the proper weight, $w_i$. The $w_i$'s are sensitive to the level of the particular objective as well as the levels of all other objectives.»
   Последняя фраза — ровно дефект 3.2 (вес без диапазона), записанный в 1979 году.

2. **Hwang & Yoon (1981)**, *Multiple Attribute Decision Making — Methods and Applications*, Springer LNEMS 186, гл. I «Introduction», с. 1–2, DOI 10.1007/978-3-642-48318-9_1, `https://link.springer.com/chapter/10.1007/978-3-642-48318-9_1`, HTTP 200, 17.09.2026. Дословно:
   > «Design/selection. Solutions to these problems are either to design the best alternative or to select the best one among previously specified finite alternatives. […] One may notice that there exist two alternative sets due to the different problem settings: one set contains a finite number of elements (alternatives), and the other has an infinite number. For instance a car a customer may purchase (select) is among the available finite models auto companies have produced; but a model which a certain company mass produced is among the infinite number of options which engineers may have designed.»
   По оглавлению (Exa, выдача по DOI 10.1007/978-3-642-45511-7) Simple Additive Weighting, TOPSIS, ELECTRE, лексикографический метод отнесены к **методам MADM** (гл. III «Methods for Multiple Attribute Decision Making»).

3. **Где граница: «конечно/бесконечно» или «явно/неявно»?** У Hwang & Yoon разделение сформулировано через конечность. Более поздняя и точная формулировка — через способ задания множества. Korhonen & Macdonald, «Multiple Objective Programming Support», Springer Reference, DOI 10.1007/springerreference_72509 (фрагмент через Exa, 17.09.2026), дословно:
   > «When Q consists of a finite number of elements which are explicitly known in the beginning of the solution process, we have an important class of problems which may be called e.g. (Multiple Criteria) Evaluation Problems. […] When the number of alternatives in Q is infinite and not countable, the alternatives are usually defined using a mathematical model formulation, and the problem is called continuous. In this case we say that the alternatives are only implicitly known. This kind of problem is referred as a Multiple Criteria Design Problem»
   Обзорная статья MCDA (HandWiki, `https://handwiki.org/wiki/Multiple-criteria_decision_analysis`, по выдаче Exa — вторичный источник, приводится только как уточнение): «Multiple-criteria design problems […] the alternatives are not explicitly known. An alternative (solution) can be found by solving a mathematical model. The number of alternatives is either finite or infinite […] If Q is defined implicitly (by a set of constraints), the resulting problem is called a multiple-criteria design problem.»

4. **Miettinen (1999)**, *Nonlinear Multiobjective Optimization*, Kluwer (Springer), Part II, гл. 3 «A Posteriori Methods», с. 77–78, DOI 10.1007/978-1-4615-5563-6_4, `https://link.springer.com/chapter/10.1007/978-1-4615-5563-6_4`, HTTP 200, 17.09.2026. Дословно:
   > «A posteriori methods could also be called methods for generating Pareto optimal solutions. After the Pareto optimal set (or a part of it) has been generated, it is presented to the decision maker, who selects the most preferred among the alternatives.»
   > «In nonlinear problems, the distinction lies between convex and non convex problems. In other words, some methods can only generate Pareto optimal solutions of convex problems. […] Basic methods are the weighting method and the ε-constraint method.»
   > «3.1. Weighting Method […] the idea is to associate each objective function with a weighting coefficient and minimize the weighted sum of the objectives. In this way, the multiple objective functions are transformed into a single objective function.»
   > «Theorem 3.1.2. The solution of weighting problem (3.1.1) is Pareto optimal if the weighting coefficients are positive»
   То есть взвешенная сумма у Miettinen — **метод многоцелевой оптимизации (скаляризация)**, а не метод выбора. Теорема о выпуклости (3.1.4 по нумерации книги) на ознакомительных страницах не видна — по ней ниже вторичные первоисточники.

5. **Невыпуклый фронт.** Messac & Ismail-Yahaya, «Required relationship between objective function and Pareto frontier orders», AIAA 2001, DOI 10.2514/6.2001-1495 (реферат через Exa): «It is well known that the weighted sum aggregate objective function fails to capture Pareto points that are located on a concave region of the Pareto frontier.» Scott & Antonsson, *J. Mech. Design* 2005, DOI 10.1115/1.1909204 (реферат через Exa): «It has long been known that a weighted sum, when used for multicriteria optimization, may fail to locate all points on a nonconvex Pareto frontier.»

6. **Zeleny (1982)**, *Multiple Criteria Decision Making*, McGraw-Hill — **первоисточник не открыт**: Google Books — только карточка, archive.org `multiplecriteria00zele` — карточка без текста в выдаче, DOI у книги нет. Из вторичного источника (Springer, «De Novo Programing in MCDM», DOI 10.1007/978-3-642-48417-9_159, реферат через Exa): «Instead of "optimizing a given system" M. Zeleny (1982, 1986) suggests a way of "designing an optimal system"». Для классификации MADM/MODM Zeleny в этом аудите **не нужен как опора** — хватает Hwang & Masud, Hwang & Yoon и Miettinen; записан в ЗАДОЛЖЕННОСТЬ.

### 9.2. Куда попадает наша задача — по признакам

| Признак | MADM (Hwang & Masud, опр. 1) | MODM (опр. 2) | FINPILOT |
|---|---|---|---|
| Альтернативы | заранее отобраны («preselected») | проектируются («design of alternatives») | **порождаются** из трёх долей (§4.1–4.3) |
| Задание множества | явный список | неявно, через переменные и ограничения | **неявно**: $x_d+x_r+x_g=R_t^+$, $x\ge0$, §6 |
| Критерии | заданные оценки в матрице | функции переменных | **вычисляются** из долей (§5, `evaluate_alternative`) |
| Число альтернатив | конечно, мало | обычно бесконечно | непрерывный симплекс, **обрезанный до 66 точек сеткой** |
| Метод | SAW, TOPSIS, … | скаляризация, ε-ограничения, фронт Парето | SAW-скаляризация по сетке + лексикографический верхний уровень |

Конечность 66 точек не делает задачу MADM: по Korhonen & Macdonald решающий признак — альтернативы известны **неявно**, через модель. Сам канон в §0 (стр. 71) называет задачу «многокритериальной оптимизацией», а в §21 (стр. 885) опирается на Hwang & Yoon (1981) как на «базу многокритериального **выбора**» — терминология внутри канона уже расходится.

### 9.3. Три следствия — проверены числом

**(а) Выпуклость фронта Парето — гипотеза в формулировке вахты неточна; реальная проблема другая и сильнее.**

*Аналогия.* Если все хорошие компромиссы лежат на ровной доске, наклоняя её (меняя веса), шарик всегда скатится в угол; остановиться посередине он может только при идеально горизонтальной доске.

*Число* (`p9.py`, `p9b.py`; 400 портретов с долгами и целями, seed 909; учитывается верхний лексикографический уровень floor; критерии — нормированные долг, подушка с насыщением, цели).
- Эффективных (неулучшаемых) точек решётки — **7 233** в 232 портретах.
- Из них выбираются **хоть при каких-то** положительных весах (4 000 случайных векторов весов) — **1 075 (15 %)**; остальные **6 158 (85 %)** не выбираются никогда.
- Но почти все «невыбираемые» лежат **на плоской грани** выпуклой оболочки, а не во впадине: отставание от оболочки ≤ 0,01 единицы полезности у **99,2 %**, максимум 0,028 (`p9b.py`, 5 000 векторов весов).
*Что это значит.* Фронт у нас не невыпуклый, а **почти плоский** — следствие линейности критериев по долям (2.1). Классический дефект «взвешенная сумма не видит вогнутых участков» (Messac; Scott & Antonsson) присутствует лишь как малый хвост. Главное: на плоском фронте взвешенная сумма ведёт себя «бах-бах» — при любых весах выдаёт вершину, а **все промежуточные компромиссы (85 % неулучшаемых планов) достижимы только на острие ножа**, когда веса точно уравновешены (3.2: переключение 38 000 ₽ целиком при $w_S$ 0,45 → 0,46). Пять профилей риска — пять наклонов доски — дают пять углов. Если критерии когда-нибудь станут нелинейными (сэкономленные проценты, вогнутая полезность), к этому добавится и классическая невыпуклость.

**(б) Ошибка сетки 10 % — существует, обычно мала, иногда большая.**
*Число* (`p9.py` блок B; 80 портретов, сравнение шага 10 % и 1 %, т.е. 66 против 5 151 точки): эффективный план отличается больше чем на 0,5 % потока в **18 из 80 (22,5 %)**; перенесённая доля потока — медиана **0**, p90 **2 %**, максимум **86 %** (в одном портрете оптимум на мелкой сетке оказался в другом углу — обычно там, где кэп цели или погашение кредита приходится между узлами). ADR-008 проверял шаг 5 % и нашёл смену победителя «в долях процента»; на шаге 1 % эффект заметнее. Поскольку решения в основном угловые (2.1), сетка редко важна, но это **ошибка дискретизации, а не свойство задачи** — гипотеза вахты подтверждена.

**(в) Как правильно называть в магистерской и в публикациях.**
Неверно: «многокритериальный выбор альтернатив методом SAW из 66 вариантов».
Верно (предлагаемая формулировка, решение за владельцем):
> «Двухуровневая (лексикографическая) задача многокритериальной оптимизации распределения свободного денежного потока домохозяйства между погашением долга, резервом ликвидности и финансовыми целями. Верхний уровень — максимизация заполнения минимального резерва; нижний — скаляризация взвешенной суммой min-max-нормированных критериев. Задача решается полным перебором равномерной симплекс-решётки долей с шагом 0,1 (66 точек).»
Дискретизация пространства решений ради объяснимости и мгновенного счёта — **законный приём**, если назван своим именем (Miettinen: генерация множества решений и предъявление его ЛПР — это a posteriori методы). Незаконно только называть результат «выбором из заданных альтернатив» и ссылаться на Hwang & Yoon как на базу метода.

**Что меняется в защите и новизне.** (1) Рецензент из многокритериальной оптимизации спросит про фронт Парето, достижимость компромиссов и ошибку сетки — ответы теперь есть числом (9.3). (2) Новизна «SAW + Avalanche + прогноз» как метод не держится (это уже установлено темами 16–17); держится объект и конструкция «лексикографический floor + скаляризация + доменные критерии». (3) Цитата Hwang & Masud 1979 о чувствительности весов к уровням целей — готовый аргумент, почему веса профилей нужно калибровать по диапазонам (3.2).

**Методы MODM, подходящие без переписывания ядра** (решётка уже перебирает все 66 точек, поэтому всё ниже — надстройка над готовым массивом):
1. **Показ фронта Парето** — из 66 точек отобрать неулучшаемые и показать человеку 3–5 разных компромиссов вместо одного угла. Цена — фильтр доминирования на 66 точках. Прямо соответствует a posteriori методам Miettinen.
2. **ε-ограничения** — превратить часть критериев в ограничения: «цель с дедлайном должна успевать», «подушка не ниже floor», и максимизировать остальное. Лечит 3.3 (операция) и 6.4 (отпуск из подушки) без смены свёртки. Miettinen называет ε-constraint вторым базовым методом.
3. **Точка отсчёта / функция достижения (achievement scalarizing)** — человек говорит «хочу к декабрю 120 000 на операцию и не меньше двух месяцев подушки», модель ищет ближайший неулучшаемый план. Упомянуто Miettinen в том же разделе; сильно объяснимо.
4. **Интерактивные методы** (класс NIMBUS того же автора) — последовательное уточнение «улучши это, можно пожертвовать тем»; дороже в интерфейсе, для Г41.

**Итог пункта 9.** По первоисточникам задача — MODM (проектирование решения), решённая дискретизацией и скаляризацией с инструментом из MADM. Следствия: фронт почти плоский, поэтому взвешенная сумма выдаёт углы и теряет 85 % неулучшаемых компромиссов; сетка 10 % меняет план в ~22 % случаев на мелкой сетке, обычно на 0–2 % потока; формулировку для магистерской надо сменить с «выбора альтернатив» на «многокритериальную оптимизацию со скаляризацией на дискретной сетке».

### Скрипты пункта 9 (дословно)

**p9.py**

```python
"""G40 p.9: (a) supported vs unsupported Pareto-efficient alternatives on the 66-point grid; (b) grid error 10% vs 1%."""
import sys, random
from datetime import datetime, timedelta
sys.path.insert(0, "/Users/vasyaevdokimov/repos/personal-finance-dss")
from app.services.planning import run_planning
TODAY = datetime(2026, 9, 17)

def portrait(rng):
    inc = rng.choice([60_000, 100_000, 180_000]); exp = inc * rng.uniform(0.3, 0.65)
    obls = []
    for k in range(rng.randint(1, 3)):
        amt = rng.uniform(2e4, 1.2e6); rate = rng.choice([0.16, 0.22, 0.35, 0.6]); n = rng.choice([12, 36, 120, 300]); rm = rate / 12
        obls.append({"id": f"o{k}", "name": "l", "amount": amt, "interest_rate": rate, "monthly_payment": amt * rm / (1 - (1 + rm) ** -n)})
    goals = [{"id": f"g{s}", "name": "g", "target_amount": rng.uniform(3e4, 2e6), "current_amount": 0,
              "deadline": TODAY + timedelta(days=rng.randint(90, 3000)), "category": rng.choice(["income_growth", "safety", "material", "emotional"])} for s in range(rng.randint(1, 2))]
    return inc, exp, obls, goals, exp * rng.choice([2.2, 3.5, 6, 9]), rng.randint(1, 5)

def crit(a):  # criteria actually used by the swap: debt (R-norm; D-norm identical up to rounding), capped L, S
    s = a["scores"]; return (s["Rt_norm"], s["Lt_norm"], s["Si_norm"])

def dominates(u, v):
    return all(x >= y for x, y in zip(u, v)) and any(x > y + 1e-9 for x, y in zip(u, v))

rng = random.Random(909); wr = random.Random(1)
W = [tuple(x / sum(t) for x in t) for t in ([wr.random() for _ in range(3)] for _ in range(4000))]
tot_eff = tot_sup = n = 0; portraits_with_unsupported = 0
for _ in range(400):
    inc, exp, obls, goals, bliq, p = portrait(rng)
    r = run_planning(inc, exp, obls, goals, bliq=bliq, r_bench=0.14, risk_tolerance=p, today=TODAY)
    if r["crisis_plan"] is not None or not r["ranked"]:
        continue
    # restrict to floor-optimal alternatives (the lexicographic first level), as the ranking does
    top_floor = max(a["floor_level"] for a in r["ranked"])
    A = [a for a in r["ranked"] if a["floor_level"] >= top_floor - 1e-9]
    pts = {}
    for a in A:
        pts.setdefault(tuple(round(c, 3) for c in crit(a)), a["id"])
    P = list(pts)
    eff = [u for u in P if not any(dominates(v, u) for v in P)]
    if len(eff) < 2:
        continue
    n += 1
    sup = set()
    for w in W:
        sup.add(max(P, key=lambda u: sum(wi * ui for wi, ui in zip(w, u))))
    unsup = [u for u in eff if u not in sup]
    tot_eff += len(eff); tot_sup += len(eff) - len(unsup)
    portraits_with_unsupported += bool(unsup)
print("A portraits with >=2 efficient points:", n, " efficient points:", tot_eff, " reachable by SOME positive weights:", tot_sup,
      " unreachable (unsupported):", tot_eff - tot_sup, " portraits having unsupported points:", portraits_with_unsupported)

# (B) grid error: 10% vs 1% step on the same portraits
rng = random.Random(910); diffs = []; changed = 0; m = 0
for _ in range(150):
    inc, exp, obls, goals, bliq, p = portrait(rng)
    r10 = run_planning(inc, exp, obls, goals, bliq=bliq, r_bench=0.14, risk_tolerance=p, today=TODAY, step=0.10)
    if r10["crisis_plan"] is not None or r10["best"] is None:
        continue
    r1 = run_planning(inc, exp, obls, goals, bliq=bliq, r_bench=0.14, risk_tolerance=p, today=TODAY, step=0.01)
    def eff_split(b):
        return (b["x_obl_effective"], b["x_reserve_effective"], sum(b["goal_allocation"].values()))
    a, b = eff_split(r10["best"]), eff_split(r1["best"])
    rt = inc - exp - sum(o["monthly_payment"] for o in obls)
    d = sum(abs(x - y) for x, y in zip(a, b)) / 2 / rt
    m += 1; diffs.append(d); changed += d > 0.005
diffs.sort(); q = lambda t: diffs[int(t * (len(diffs) - 1))]
print("B portraits:", m, " plan differs (>0.5%% of flow moved):", changed, "(%.1f%%)" % (100 * changed / m),
      " share of flow moved p50=%.3f p90=%.3f max=%.3f" % (q(.5), q(.9), diffs[-1]))
```

**Вывод p9.py:**
```
A portraits with >=2 efficient points: 232  efficient points: 7233  reachable by SOME positive weights: 1075  unreachable (unsupported): 6158  portraits having unsupported points: 230
B portraits: 80  plan differs (>0.5%% of flow moved): 18 (22.5%)  share of flow moved p50=0.000 p90=0.020 max=0.860
```

**p9b.py**

```python
"""G40 p.9b: separate strictly unsupported efficient points (strictly below the convex hull for every weight)
from points lying on a flat face of the hull (reachable only as ties). Gap = min_w [max_v w.v - w.u] over sampled weights."""
import sys, random
exec(open("/private/tmp/claude-501/-Users-vasyaevdokimov-repos-personal-finance-dss/fe25aad2-149b-48bd-a8b2-c62cc04ce4a1/scratchpad/g40/p9.py").read().split("rng = random.Random(909)")[0])
rng = random.Random(909); wr = random.Random(1)
W = [tuple(x / sum(t) for x in t) for t in ([wr.random() for _ in range(3)] for _ in range(5000))]
gaps = []
for _ in range(400):
    inc, exp, obls, goals, bliq, p = portrait(rng)
    r = run_planning(inc, exp, obls, goals, bliq=bliq, r_bench=0.14, risk_tolerance=p, today=TODAY)
    if r["crisis_plan"] is not None or not r["ranked"]:
        continue
    top_floor = max(a["floor_level"] for a in r["ranked"])
    P = list({tuple(round(c, 3) for c in crit(a)) for a in r["ranked"] if a["floor_level"] >= top_floor - 1e-9})
    eff = [u for u in P if not any(dominates(v, u) for v in P)]
    if len(eff) < 2:
        continue
    best = [max(sum(wi * vi for wi, vi in zip(w, v)) for v in P) for w in W]
    for u in eff:
        gaps.append(min(b - sum(wi * ui for wi, ui in zip(w, u)) for w, b in zip(W, best)))
gaps.sort(); n = len(gaps)
for thr in (0.002, 0.01, 0.03, 0.1):
    k = sum(1 for g in gaps if g <= thr)
    print("efficient points with hull gap <= %.3f (on/near a hull face, tie-reachable): %d of %d (%.1f%%)" % (thr, k, n, 100 * k / n))
print("gap p50=%.3f p90=%.3f max=%.3f (gap in units of normalized utility)" % (gaps[n // 2], gaps[int(.9 * (n - 1))], gaps[-1]))
```

**Вывод p9b.py:**
```
efficient points with hull gap <= 0.002 (on/near a hull face, tie-reachable): 4750 of 7233 (65.7%)
efficient points with hull gap <= 0.010 (on/near a hull face, tie-reachable): 7172 of 7233 (99.2%)
efficient points with hull gap <= 0.030 (on/near a hull face, tie-reachable): 7233 of 7233 (100.0%)
efficient points with hull gap <= 0.100 (on/near a hull face, tie-reachable): 7233 of 7233 (100.0%)
gap p50=0.001 p90=0.004 max=0.028 (gap in units of normalized utility)
```
---

## ИТОГ Г40

**Процесс, честно.** Подагентов — **0** (всё сделано в одном контексте, последовательно). `WebSearch` — **0** вызовов. Exa — 6 поисков. Прочие каналы: Crossref, Semantic Scholar, Unpaywall (один запрос по ошибке ушёл с e-mail владельца в параметре — дальше Unpaywall не использовался), `curl`, `r.jina.ai`. Скриптов — 14 (`p1`…`p9b`), все в скрэтчпаде, приведены дословно. Код продукта, канон и тесты не менялись; ранжирование в `p3.py` менялось только подменой в памяти процесса.

### 1. Таблица проблем

Классы: **ОП** — ошибка постановки; **НУ** — неустойчивость; **НД** — необоснованное допущение; **ЧД** — численный дефект / дефект реализации; **ВВ** — вопрос вкуса.
Серьёзность для пользователя: 🔴🔴 ложный совет у обычного человека; 🔴 неверный совет или противоречивые числа у заметной группы; 🟡 редкий случай или только показ; 🟢 не видна пользователю.

| # | Раздел канона / код | Проблема | Класс | Серьёзность | Чем подтверждено |
|---|---|---|---|---|---|
| 1 | §2.1; `preprocessing.prepare_data` | «Месяц» = 30 суток: у зарплатника с выплатой 5-го числа 4-го числа доход = 0 → ложный кризис `critical` | ЧД/ОП | 🔴🔴 | число: 5.1, `p5b.out` |
| 2 | §12; `crisis.py:36,54` | Кризисный режим берёт floor 2 мес. вместо 1 при токсичном долге → «резать расходы» при 100 000 ₽ на счёте и МФО под 150 % | ОП | 🔴 | число: 1.6, `p1c.py` |
| 3 | §6.2, §6.4, §11.5 | Балансовый ход «всё или ничего»; разовое закрытие цели тратит подушку ниже floor | ОП | 🔴 | число: 6.2, 6.4, `p6.py` |
| 4 | §7–9 | Решение в 91 % случаев — угол симплекса, определяется только весами; слепо к ставке (15 % = 90 %) и к важности цели | ОП | 🔴 | число: 2.1–2.2, `p2b.py`; теория: основная теорема ЛП |
| 5 | §7, §9 | Веса «важности» при локальной min-max нормализации (нарушение range sensitivity); смена нормализации меняет план в 41 % портретов | ОП/НД | 🔴 | литература: Fischer 1995, Monat 2009, Hwang & Masud 1979; число: 3.2, `p3.py` |
| 6 | §8, §11 | Нет вето на срок цели: операция через 4 месяца получает 0 ₽ во всех профилях | ОП | 🔴 | число: 3.3, `p3.py` |
| 7 | §11.4; `goals_priority.calculate_goals_si` | Недолитые деньги целей молча уходят в подушку (69 % «целевых» денег в примере); канон противоречит сам себе | ОП/ЧД | 🔴 | число: 1.5, `p1b.py` |
| 8 | §11.1, §3.3 | Цель-«подушка» невидима для критерия ликвидности → вторая подушка | ОП | 🔴 | число: 6.5, `p6.py` |
| 9 | §8 ADR-015; `ranking.income_cv` | Нулевые месяцы выкидываются из CV → floor не растёт у фрилансера с пустыми месяцами (0,17 вместо 0,61) | ЧД | 🔴 | число: 5.4, `p5.py` |
| 10 | §10.5; `amortization._simulate` | Освободившийся платёж каскадится один месяц; экономия занижена до 2 раз, срок завышен на 15 мес. | ЧД | 🔴 (показ) | число: 4.3, `p4b.py` |
| 11 | §15; `services/forecasting.py:124–125`, `routes_planning.py:726` | Прогнозный «ресурс» = запас + поток (двойной счёт); три разных определения $L_t$, одно — запрещённая v2.x | ОП | 🔴 (экран прогноза) | число: 1.3–1.4, `p1b.py` |
| 12 | §5.1/§5.3 | $\hat R \equiv 1-\hat D$: два критерия — один; эффективный вес долга 0,45–0,50 у всех профилей | ОП | 🟡 | алгебра + число: 1.1, `p1.py` |
| 13 | §6 | Жёсткие инварианты никогда не срабатывают (0 из 1410); заявка о вето-модели не подтверждается кодом | ОП | 🟢 (для научной формулировки — существенно) | число: 1.2 |
| 14 | §20, §8 | Порог токсичности 30 %: 29,5 % → 30 % разворачивает 100 % потока | НУ/НД | 🔴 | число: 2.3, `p2.py` |
| 15 | §3.2/§12 | Граница $R_t=0$ без гистерезиса: три типа совета на ±250 ₽ | НУ | 🟡 | число: 2.3 |
| 16 | §10.2 | $r_{bench}$ облагает НДФЛ проценты, которые по ст. 214.2 НК РФ для большинства не облагаются; ипотечный вычет (ст. 220) не учтён; оба смещения — к досрочке | НД | 🟡 | закон: 4.4 |
| 17 | §5, §10.4 vs §12, §10.5 | Критерий SAW меряет снижение платежа, Avalanche гасит по ставке, кризис — по $P/A$; две модели кредита (срок vs платёж) | ОП | 🟡 | арифметика: 4.2; Fox 1966 Т.2 |
| 18 | §15 | Holt с зашитыми α, β, φ на 3–8 точках: ошибка ±9 % на плоском ряду; при отсутствии истории — выдуманный тренд −20 % | НД | 🟡 (показ) | литература: fpp3 §8.1; число: 5.2 |
| 19 | §15 | МК: σ = 5 % от точки для всех, нормальное распределение; 1000 прогонов вместо формулы | НД | 🟡 (показ) | литература: Guvenen et al.; число: 5.3 |
| 20 | §11.3 | Обрыв инфляционной индексации на 36 мес. (+12,5 % за один день) | НУ | 🟡 | число: 5.5 |
| 21 | §4.3 | Ошибка сетки 10 %: план меняется в 22,5 % портретов на шаге 1 %, p90 — 2 % потока, max 86 % | ЧД | 🟡 | число: 9.3 (б), `p9.py` |
| 22 | §8 (лексикографический выбор) | На плоском фронте взвешенная сумма выдаёт углы; 85 % неулучшаемых компромиссов недостижимы | ОП | 🟡 | число + литература: 9.3 (а) |
| 23 | §12 | «Жадность по $P/A$ оптимальна» противоречит политике полного закрытия (100 000 ₽ вместо 20 000) | ОП (формулировка) | 🟡 | число: 6.3 |
| 24 | `app/schemas/*` | Схемы пропускают NaN, ∞, отрицательный доход; ядро молча считает | ЧД | 🟡 | число: 7.4, `p7.py` |
| 25 | `ranking.py:180`, `alternatives.py:237` | Округление до сравнения: ложные ничьи 3,2 %, схлопывание $\hat D$ | ЧД | 🟢 | число: 7.2 |
| 26 | §3.4, §17, §21 | Ссылки: ПДН 0,40 «по 4892-У» (нет), Fannie Mae 43 % (нет), Jain 2005 — биометрия; §3.3 ↔ §18 п. 6 о Greninger | НД (источники) | 🟢 (защита — существенно) | литература: пункт 8 |
| 27 | весь канон | Перекрёстные ссылки на разделы разъехались; §15 описывает SES, код — Holt; прогноз в решение не входит, хотя §0 делает его этапом | ВВ/документ | 🟢 | 1.7 |
| 28 | §9 веса, §11 категории, срочность | Собственные решения без внешней опоры (замкнутая петля Г31.4) | НД | 🟡 | пункт 8 |
| — | `money.py`, сохранение денег | **Не проблема:** инвариант сохранения держится до 5 копеек на любых масштабах | — | 🟢 надёжно | 7.1 |
| — | §10 Avalanche | **Не проблема на текущих допущениях:** 0 из 3000 портфелей, где другой порядок лучше | — | 🟢 надёжно | 4.1 |
| — | §7 rank reversal от набора альтернатив | **Не проблема:** крайние точки — всегда вершины решётки | — | 🟢 надёжно | 3.1 |

### 2. 🔴 Прямой ответ: MADM или MODM

**MODM.** По Hwang & Masud (1979, опр. 1–2) многоатрибутная задача — «selection of the "best" alternative from a pool of preselected alternatives», многоцелевая — «design of alternatives which optimize or "best satisfy" the objectives». У нас альтернативы не отобраны заранее, а порождены тремя долями и ограничениями; критерии вычисляются из долей. Конечность 66 точек класс не меняет: по Korhonen & Macdonald решает то, что множество задано **неявно**, через модель. Инструмент (SAW, min-max) взят из MADM (Hwang & Yoon 1981), и это законный приём **скаляризации** (Miettinen 1999, weighting method), если назван своим именем. Научный руководитель прав.

Три следствия:
- **(а) Выпуклость фронта.** Фронт не невыпуклый, а почти плоский (99,2 % неулучшаемых точек в пределах 0,01 от оболочки). Поэтому взвешенная сумма выдаёт угол и **теряет 85 % неулучшаемых компромиссов**, достижимых лишь при точно уравновешенных весах. Классическая невыпуклость — малый хвост (максимальный разрыв 0,028).
- **(б) Ошибка сетки 10 %.** Реальна: на сетке 1 % план другой в 22,5 % портретов; обычно сдвиг 0–2 % потока, в редких случаях — до 86 %.
- **(в) Формулировка для магистерской:** «двухуровневая (лексикографическая) задача многокритериальной оптимизации распределения денежного потока со скаляризацией взвешенной суммой на равномерной симплекс-решётке», а не «многокритериальный выбор из 66 альтернатив».

### 3. 🔴 Насколько модель адекватна сейчас — оценка владельцу

**Шкала — три уровня, и почему именно так.** Для СППР по деньгам важны не красота формул, а два вопроса: *может ли совет навредить обычному человеку* и *как часто*. Поэтому:
- **Надёжно** — проверено числом или первоисточником, вредных краёв не нашлось.
- **Условно верно** — для типичного человека совет разумный, но основание — экспертный консенсус, а не внешняя норма, или есть известные края, где совет плохой, но редкий.
- **Требует правки до запуска** — у **обычного, не экзотического** пользователя модель выдаёт неверный совет или два противоречащих числа, и это находится коротким примером.

**Надёжно (на это можно опираться):**
- Денежная арифметика: деньги в плане не теряются и не появляются, до копеек.
- Порядок погашения по ставке (Avalanche) — на наших допущениях лучший из возможных порядков.
- Кризисная ветка всегда даёт план действий; запрет «уйти в минус» соблюдается.
- Монотонность по доходу: больше доход — не хуже план.
- Сама идея «сначала минимальная подушка, потом всё остальное» — лексикографический floor — корректный и признанный в литературе приём.

**Условно верно:**
- Направление «досрочка при ставке выше порога» — в типичных случаях разумно, но решается весами, а не ставкой и суммами (91 % решений — «всё в одно»).
- Все пороги и веса (floor 2 мес., токсичность 30 %, $L^*$, веса профилей, категории целей) — согласие с экспертами, не внешняя норма (петля Г31.4). Порог 30 % даёт полный разворот совета от полупроцента ставки.
- $r_{bench}$ — правильная идея, но налог посчитан не по закону и смещает к досрочке.
- Прогноз — экран, не решение; сейчас он скорее декоративный: коридор одинаковый для всех, тренд на коротком ряду случайный.

**Требует правки до запуска** (все — локальные правки, ни одна не требует менять рамку):
1. Определение «месяца» — ложный кризис у зарплатника раз в месяц (1).
2. Кризисный floor без G8 (2) и балансовый ход «всё или ничего» (3).
3. Деньги целей уходят в подушку без ведома человека (7); цель-подушка невидима (8); разовое закрытие цели ломает floor (3).
4. Нет ограничения на срок цели — срыв срочной цели ради снижения платежа (6).
5. CV без нулевых месяцев (9).
6. Экран прогноза: запас плюс поток и три разных $L_t$ (11); экран графика погашения занижает экономию до 2 раз (10).

**Вердикт простыми словами.** Модель **не сломана и не опасна по конструкции**: деньги сходятся, порядок погашения правильный, кризис всегда получает план. Но сейчас она **проще, чем выглядит**: из четырёх критериев независимых три, жёсткие ограничения не работают, и почти всегда совет — «всё в одну корзину» по весу профиля. Это приемлемо как первая версия и объяснимо, но **не** «тонкая многокритериальная оптимизация». Перед запуском надо закрыть шесть групп дефектов выше — именно они дают неверный совет обычному человеку. По шкале: **ядро — условно верно; обвязка ядра (окно месяца, кризис, цели, CV, экраны прогноза и графика) — требует правки до запуска.** Научная формулировка — требует правки до защиты (пункт 9, ссылки пункта 8).

### 4. Вопросы для Г41 и Г39

**Г41 — какие рамки проверять первыми (в порядке пользы):**
1. **Многоцелевая оптимизация a posteriori** (п. 5 постановки Г41): показ фронта Парето из уже перебранных 66 точек; ε-ограничения для сроков целей и floor; функция достижения по точке отсчёта (Wierzbicki/Miettinen). Вопрос: какой из трёх даёт наибольший выигрыш объяснимости при нулевой цене перебора, и как показать 3–5 компромиссов вместо угла.
2. **Критерии в рублях вместо min-max** (глобальные шкалы, Monat 2009; swing-веса): вопрос — можно ли задать критерии как «сэкономленные проценты», «месяцы подушки», «доля цели к сроку» с весами, откалиброванными по диапазонам, и что это даёт для 3.2/2.2.
3. **Стохастическое/многопериодное программирование** (п. 1–2 Г41): вопрос — насколько разрыв Rios-Solis появляется при нерегулярном доходе (ADR-015 портреты), то есть стоит ли многомесячная постановка своей сложности.
4. **Модель буферного запаса** (Carroll; п. 3 Г41): даёт ли размер подушки из распределения дохода вместо экспертных 2/3–6 месяцев — это разорвало бы петлю Г31.4 для floor и $L^*$.
5. **Ожидаемая полезность / вогнутые функции ценности** (п. 4 Г41): уберёт ли вогнутость «бах-бах» углов без интерактивности.

**Г39 — что проверять и чем:**
1. **Свойства решения — метаморфными и property-based тестами** (Hypothesis): монотонность по доходу; непрерывность по ставке вне объявленных порогов; нечувствительность к порядку ввода долгов/целей; «больше ставка → не меньше в долг» (сейчас нарушается как нечувствительность); сохранение денег; floor не нарушается ни одним этапом (ловит 6.4).
2. **Согласованность канона и кода — сверочными тестами**: одна функция $L_t$ для всех эндпоинтов; $S_n$ по формуле канона; каскад §10.5 против денежно-сохраняющей эталонной симуляции (`p4.py` как оракул).
3. **Карта разрывов — параметрическими свипами** (`p2.py` как основа): список объявленных порогов и проверка, что других скачков нет.
4. **Устойчивость к весам и нормализации** — интервалы устойчивости O'Shea et al. на портретах; доля портретов, меняющих план при смене нормализации (сейчас 41 %) как метрика.
5. **Дискретизация** — сетка 1 % как оракул для 10 %; доля и размер расхождений как регрессионная метрика.
6. **Календарь** — тесты на окно месяца на границах 28/30/31 дня и разном часе.
7. **Входы** — фаззинг схем NaN/∞/отрицательные.
8. **Мутационное тестирование** (68,7 % сейчас): добавить убийц мутаций в местах, найденных здесь (ключ сортировки лавины, фильтр нулей в CV, floor в кризисе, кэп целей).
9. **Разрыв петли валидации (Г31.4)** — внешние данные вместо экспертного согласия там, где они есть: распределение шоков дохода (буферный запас), фактические исходы (срывы целей, просрочки).

### 5. ЗАДОЛЖЕННОСТЬ (не пройдено — с причиной)

1. **Глобальный оптимум погашения (MILP)** на наших допущениях не считался — сравнивались только приоритетные порядки (4.1). Причина: наличие решателя в `.venv` не проверено (попытка импорта scipy была остановлена хуком путей), в объём батча не вошло. Проверить: PuLP/CBC или scipy `milp` на тех же 3000 портфелях.
2. **Zeleny 1982** — полный текст не добыт (Google Books — карточка; archive.org — карточка; DOI нет). Для вывода пункта 9 не требуется, но в списке первоисточников постановки.
3. **Miettinen 1999, Теорема 3.1.4 (выпуклость)** — на ознакомительных страницах Springer не видна; вывод опирается на Messac & Ismail-Yahaya 2001 и Scott & Antonsson 2005 (рефераты) и на собственный замер.
4. **Keeney 2002, Fischer 1995 полными текстами** — закрыты (Semantic Scholar `CLOSED`, Unpaywall `is_oa: false`); использованы реферат Fischer и открытый Monat 2009.
5. **Bach 2003** — в сырье проекта нет ни одного файла с первоисточником; что это за работа и что в ней про avalanche — не проверено.
6. **Fishburn 1967** — реквизиты по Crossref, текст не открывался.
7. **Прогрессивная шкала НДФЛ с 2025 г.** для $r_{bench}$ — не проверялась.
8. **Доходят ли NaN/∞ до БД** (`Numeric(14,2)`) — проверены только pydantic-схемы.
9. **Правило Qualified Mortgage CFPB (43 %)** как вероятный настоящий источник числа канона — не открывалось.
10. **Статистика шоков месячного дохода домохозяйств РФ** для распределения МК — в этом батче не искалась (есть только годовые данные США, Guvenen et al.).
