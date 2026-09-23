# Г45 — Валидность графика прогноза (Монте-Карло) и его практическая польза

**Дата:** 17.09.2026 · **Тема очереди:** Г45 · **Агент:** `base-kit:researcher`
**Вопрос владельца (дословно):** «меня крайне сильно волнует график, который строится в продукте
по Монте-Карло… верифицировать одно дело, но валидировать как-то… то, что он верифицирован
и делает то, что запрограммирован, — это да. но как соотносится с реальностью и практической
полезностью — большие вопросы».

**Что это за файл:** сырьё исследования (raw). Решения по правкам ядра здесь не принимаются.
Канон `docs/math_model.md` и код продукта не изменялись.

---

## 0. Состояние каналов добычи (замер 17.09.2026)

Команда: `curl -skL --max-time 25 -o /dev/null -w "%{http_code}"`.

| Канал | HTTP | Комментарий |
|---|---|---|
| OpenAlex (`api.openalex.org/works?search=...`) | 200 | рабочий, основной поиск реквизитов |
| Crossref (`api.crossref.org/works?query=...`) | 200 | рабочий |
| EuropePMC (`ebi.ac.uk/europepmc/webservices/rest/search`) | 200 | рабочий |
| Semantic Scholar (`api.semanticscholar.org/graph/v1`) | **429** | rate limit без ключа — не гейтится осознанно, не использовался |
| `r.jina.ai` (без браузерного UA) | 200 | рабочий, основной обход антибота |
| Unpaywall (`api.unpaywall.org/v2/<DOI>?email=research@example.org`) | 404 на пробном DOI | 404 = «такого DOI нет», сервис жив; на реальных DOI ниже отвечал 200 |
| arXiv (`arxiv.org/abs/...`) | 200 | рабочий |
| Bank of England (`bankofengland.co.uk`) | 200 | рабочий |
| ЦБ РФ (`cbr.ru`) | 200 | рабочий (с `-k`, сертификат НУЦ не ставился) |
| Exa (`mcp__exa__web_search_exa`) | ok | пробный вызов вернул 5 результатов с полными highlight-ами |

Не сработал только Semantic Scholar (429). Он не понадобился: всё добыто через OpenAlex/Crossref/
arXiv/`r.jina.ai`/Exa.

---
## Как устроен график сейчас (прочитано в коде 17.09.2026, чтобы все пункты ссылались на одно)

`app/services/forecasting.py::forecast_indicators` → `app/core/forecast.py`. Цепочка:

1. `build_monthly_history` — помесячные ряды дохода/расхода из реальных транзакций (скользящие 30-дневные корзины).
2. Если истории < 2 точек — `build_history_from_current(value, periods=6, noise=0.05, seed=1/2/3)`: **выдуманные
   6 точек** вокруг `value·0,96` с детерминированным дрейфом +4 % и гауссовым шумом 5 %.
3. `choose_point_forecast` — демпфированный Holt (α 0,4, β 0,3, φ 0,9 — константы, не подбираются) при ≥ 3 точках,
   иначе SES α 0,3.
4. Баланс копится: `Bt(h) = Bt(h−1)·(1+r_m) + (CF−P)`; показатель `Rt(h) = Bt(h) + CF(h) − P(h)`.
5. `monte_carlo_intervals(point_rt, …)` — **1000 нормальных выборок вокруг точки Rt(h)** с
   `σ(h) = |Rt(h)|·0,05·√(1+0,5h)`, `seed=42`; из них p10/p50/p90. Это и есть «коридор 80 %» на графике.

🔴 Ключевое, что надо удержать: **разброс не берётся из данных человека вообще.** Он берётся как 5 % **от величины
самого показателя Rt**. Это не симуляция денежной траектории (никакие доходы/расходы не разыгрываются) — это
декоративная лента вокруг одной линии.

---

## Пункт 1. На какой вопрос график должен отвечать и отвечает ли

**Аналогия.** Человек спрашивает у врача «я доживу до операции?», а в ответ получает график температуры тела
с «коридором ±5 %». График красивый, вопрос — другой.

**Три вопроса, которые реально задаёт пользователь СППР по личным финансам** (формулировки из Г31/Г41, задачи продукта):
- **«Хватит ли мне денег?»** — то есть: в каком месяце баланс уйдёт ниже нуля (или ниже подушки), если ничего не менять.
  Ответ — **дата и вероятность**, не линия.
- **«Когда закроется долг?»** — ответ **дата** (и разница дат между двумя стратегиями погашения).
- **«Достигну ли цели?»** — ответ **шанс в процентах** к сроку и сколько надо добавлять в месяц, чтобы шанс стал
  приемлемым.

**Что показывает текущий график.** Траекторию `Rt(h)` — величину, которая по Г40 **дважды считает месячный поток**
(`Rt = Bt + CF − P`, при том что `Bt` уже включает `CF − P` за тот же месяц). То есть по вертикальной оси отложена
не «сколько у меня будет денег», а гибрид запаса и потока. Пользователь читает её как «сколько будет на счету» —
а это не она. Ни одного из трёх вопросов график прямо не отвечает: дату пересечения нуля он даёт косвенно
(`deficit_alert` считается отдельно, по Rt, не по балансу), долг в нём не виден, шанс достижения цели — не показан.

🔴 **Вывод пункта 1:** график отвечает на вопрос «как выглядит экстраполяция служебного показателя Rt», а не на вопрос
пользователя. Даже если починить коридор (п. 2), он останется ответом не на тот вопрос, пока по оси Y стоит `Rt`,
а не баланс/долг/цель.

---

## Пункт 2. 🔴 Валиден ли коридор: покрытие, PIT, CRPS — числа

**Аналогия.** Коридор «80 %» — это обещание: «из десяти раз восемь правда окажется внутри». Проверка простая:
сделать тысячу прогнозов, посмотреть, сколько раз попали. Если попали 2 раза из 10, обещание — ложь, независимо
от того, насколько красиво нарисована лента.

**Что уже установлено в Г43** (`statistical_forecasting_methods_2026-09-17.md`, п. 2, не переоткрываю):
покрытие коридора продукта **7–47 % вместо 80 %**; interval score в 3–5 раз хуже альтернатив; замена —
ширина от собственного разброса потока человека, рост как √h, квантиль Стьюдента (74–86 % на первом месяце),
конформный множитель (≈ 80 % на всех горизонтах).

**Что добавляет Г45:** то, чего Г43 не считал — **PIT-гистограмма, CRPS и покрытие по каждому горизонту 1…6**,
плюс две механические патологии, видные без всякой статистики.

### 2.1. Стенд: покрытие по горизонтам + PIT + CRPS

Стенд `g45/p_valid.py` (400 портретов на каждый T, шесть типов рядов из генератора Г43 `gen43.py`, реальные данные
не используются — 152-ФЗ). CANON — **сама функция продукта**; NORM — нормальный/стьюдентов коридор по собственному
разбросу чистого потока; CONF — конформный множитель, откалиброванный на отдельных 400 портретах.
CRPS и interval score нормированы на средний месячный доход человека (меньше — лучше).

```

######## T=6  conformal q(h): 1:1.46 2:1.91 3:2.42 4:2.59 5:2.77 6:3.10
method   h    cov80      IS    CRPS  width/inc
CANON    1    25.2%    7.41   0.810       0.50
CANON    2    20.5%   10.67   1.158       0.62
CANON    3    18.0%   14.27   1.553       0.82
CANON    4    19.0%   18.28   1.979       0.96
CANON    5    14.0%   22.53   2.442       1.17
CANON    6    15.2%   26.55   2.871       1.33
NORM     1    81.0%    1.78   0.246       1.04
NORM     2    74.5%    2.52   0.378       1.57
NORM     3    68.8%    3.70   0.545       2.04
NORM     4    68.2%    4.92   0.705       2.49
NORM     5    65.5%    5.79   0.835       2.92
NORM     6    64.2%    6.83   0.998       3.34
CONF     1    80.0%    1.76   0.246       0.95
CONF     2    78.5%    2.55   0.378       1.76
CONF     3    77.2%    3.73   0.546       2.74
CONF     4    78.0%    4.88   0.703       3.38
CONF     5    77.2%    5.74   0.832       4.04
CONF     6    77.8%    6.84   0.992       4.96
PIT over all horizons pooled (10 bins, each ideal 0.10):
  PIT CANON : [0.40 0.04 0.03 0.03 0.01 0.02 0.01 0.02 0.02 0.42]  mean 0.503 (ideal .500)  var 0.2111 (ideal .0833)  KS 0.369 p=8.2e-293
  PIT NORM  : [0.16 0.07 0.07 0.08 0.07 0.09 0.10 0.11 0.11 0.14]  mean 0.518 (ideal .500)  var 0.1029 (ideal .0833)  KS 0.065 p=3.1e-09
  PIT CONF  : [0.12 0.07 0.07 0.10 0.10 0.12 0.11 0.12 0.09 0.10]  mean 0.513 (ideal .500)  var 0.0843 (ideal .0833)  KS 0.050 p=9.3e-06
PIT at h=1 only:
  PIT CANON : [0.36 0.04 0.03 0.04 0.02 0.02 0.03 0.03 0.03 0.40]  mean 0.516 (ideal .500)  var 0.1984 (ideal .0833)  KS 0.343 p=1.8e-42
  PIT NORM  : [0.11 0.06 0.07 0.10 0.10 0.08 0.13 0.15 0.12 0.08]  mean 0.533 (ideal .500)  var 0.0810 (ideal .0833)  KS 0.089 p=3.3e-03
  PIT CONF  : [0.11 0.06 0.07 0.10 0.10 0.08 0.13 0.14 0.12 0.09]  mean 0.534 (ideal .500)  var 0.0856 (ideal .0833)  KS 0.089 p=3.4e-03

######## T=12  conformal q(h): 1:1.34 2:1.60 3:1.82 4:1.94 5:2.10 6:2.21
method   h    cov80      IS    CRPS  width/inc
CANON    1    33.0%    5.28   0.587       0.52
CANON    2    28.2%    7.11   0.788       0.63
CANON    3    27.0%    9.36   1.048       0.83
CANON    4    24.8%   11.83   1.318       0.96
CANON    5    24.2%   14.68   1.637       1.16
CANON    6    23.0%   17.47   1.943       1.31
NORM     1    84.5%    1.55   0.221       1.05
NORM     2    76.0%    2.25   0.340       1.54
NORM     3    73.5%    2.99   0.458       1.95
NORM     4    69.5%    3.91   0.591       2.32
NORM     5    66.2%    4.69   0.716       2.68
NORM     6    65.5%    5.42   0.819       3.02
CONF     1    82.5%    1.53   0.221       0.99
CONF     2    80.0%    2.27   0.342       1.67
CONF     3    79.5%    3.04   0.461       2.33
CONF     4    76.5%    3.89   0.591       2.86
CONF     5    77.5%    4.65   0.713       3.46
CONF     6    77.5%    5.37   0.816       4.00
PIT over all horizons pooled (10 bins, each ideal 0.10):
  PIT CANON : [0.34 0.05 0.04 0.04 0.03 0.03 0.03 0.03 0.03 0.39]  mean 0.517 (ideal .500)  var 0.1919 (ideal .0833)  KS 0.326 p=1.1e-227
  PIT NORM  : [0.11 0.08 0.07 0.08 0.09 0.11 0.08 0.10 0.12 0.16]  mean 0.550 (ideal .500)  var 0.0953 (ideal .0833)  KS 0.091 p=7.7e-18
  PIT CONF  : [0.09 0.06 0.08 0.09 0.11 0.13 0.09 0.12 0.11 0.12]  mean 0.546 (ideal .500)  var 0.0814 (ideal .0833)  KS 0.088 p=1.9e-16
PIT at h=1 only:
  PIT CANON : [0.28 0.05 0.03 0.05 0.04 0.06 0.05 0.03 0.03 0.39]  mean 0.545 (ideal .500)  var 0.1761 (ideal .0833)  KS 0.310 p=1.0e-34
  PIT NORM  : [0.07 0.06 0.06 0.10 0.12 0.13 0.12 0.13 0.13 0.08]  mean 0.552 (ideal .500)  var 0.0723 (ideal .0833)  KS 0.125 p=6.9e-06
  PIT CONF  : [0.08 0.06 0.07 0.08 0.12 0.13 0.11 0.12 0.14 0.09]  mean 0.553 (ideal .500)  var 0.0760 (ideal .0833)  KS 0.123 p=9.4e-06
```

**Как читать PIT.** Для каждого прогноза считаем, в какой процентиль прогнозного распределения попал факт. У честного
прогноза эти числа равномерны: в каждой из 10 корзин по 0,10. У продукта в крайних корзинах **0,40 и 0,42** — то есть
**82 % фактов вываливаются за пределы крайних децилей прогноза**. Это классическая U-образная форма — «прогноз слишком
узкий, модель самоуверенна» (Gneiting & Katzfuss 2014; Diebold, Gunther & Tay 1998 — реквизиты в п. 2.4).
Дисперсия PIT у продукта **0,21 при идеале 0,083** — в 2,5 раза больше равномерной; KS-статистика 0,37, p ≈ 10⁻²⁹³.

**Числа по делу:**
- покрытие 80 %-коридора продукта по горизонтам: **25,2 % → 15,2 %** (T=6) и **33,0 % → 23,0 %** (T=12).
  Ни на одном горизонте даже близко к 80 %.
- 🔴 покрытие **падает** с горизонтом, хотя коридор расширяется: неопределённость суммы потоков растёт быстрее,
  чем `√(1+0,5h)`.
- CRPS продукта **0,81–2,87** среднемесячного дохода против **0,22–1,00** у NORM/CONF — хуже в **3–4 раза**.
  CRPS — «правильное» (proper) правило: его нельзя улучшить ни самоуверенностью, ни искусственным расширением,
  поэтому сравнение методов ведётся по нему, а не по покрытию.
- ширина коридора продукта на первом месяце — **0,50 месячного дохода**, у честного — **1,0**: продукт **вдвое уже**
  того, что оправдано данными; к шестому месяцу 1,33 против 3,3–5,0, то есть **уже в 2,5–3,7 раза**.

### 2.2. 🔴 Две механические патологии — видны без статистики

Стенд `g45/p_patho.py`, вывод дословно:

```
=== (A) width of the 80 % band vs the level of Rt ===
One person: income 100 000, expense 85 000, payments 0, so net flow +15 000/mo.
Only the starting balance B0 differs. The real uncertainty of the future is IDENTICAL.
        B0  h           Rt          p10          p90      width  width/Rt
         0  1        30000        27540        32396       4857     0.162
         0  6       105000        91618       117992      26375     0.251
     15000  1        45000        41309        48595       7285     0.162
     15000  6       120000       104706       134849      30143     0.251
    100000  1       130000       119338       140384      21046     0.162
    100000  6       205000       178872       230366      51494     0.251
    600000  1       630000       578330       680325     101994     0.162
    600000  6       705000       615147       792235     177089     0.251

Exact zero crossing: a person whose flow is exactly zero (income == expense), B0 = 0.
  h=1 Rt=0.00 p10=0.00 p90=0.00 width=0.00
  h=2 Rt=0.00 p10=0.00 p90=0.00 width=0.00
  h=3 Rt=0.00 p10=0.00 p90=0.00 width=0.00
  h=4 Rt=0.00 p10=0.00 p90=0.00 width=0.00
  h=5 Rt=0.00 p10=0.00 p90=0.00 width=0.00
  h=6 Rt=0.00 p10=0.00 p90=0.00 width=0.00

=== (B) synthetic history invented when there is no real history ===
current value 100000 -> history [102183.29, 103597.34, 97598.41, 94250.19, 93317.57, 99350.41]
  fitted trend of that history (OLS slope per month): -1381.5
  point forecast h=1..6: [96366, 95884, 95451, 95061, 94710, 94394]
  forecast month 6 vs the value the user actually entered: -5.6%
current value 50000 -> history [51091.64, 51798.67, 48799.21, 47125.1, 46658.78, 49675.2]
  fitted trend of that history (OLS slope per month): -690.7
  point forecast h=1..6: [48183, 47942, 47725, 47530, 47355, 47197]
  forecast month 6 vs the value the user actually entered: -5.6%

Same synthetic history run 3 times with the product's fixed seeds 1/2/3 (income/expense/payments):
  seed=1: [102183.29, 103597.34, 97598.41, 94250.19, 93317.57, 99350.41]
  seed=2: [107223.2, 93458.3, 99175.33, 98623.3, 102568.71, 92469.87]
  seed=3: [96454.6, 102640.12, 92809.38, 102683.41, 97316.06, 97944.75]

What the user sees if he enters income 100 000 and expense 85 000 with NO history at all:
  h=1 income=96366 expense=74291 Bt=22075 Rt=44150 [40529 .. 47677]
  h=2 income=95884 expense=72680 Bt=45279 Rt=68484 [62463 .. 74556]
  h=3 income=95451 expense=71230 Bt=69500 Rt=93721 [84002 .. 103600]
  h=4 income=95061 expense=69925 Bt=94636 Rt=119772 [106386 .. 132681]
  h=5 income=94710 expense=68751 Bt=120595 Rt=146554 [129097 .. 164688]
  h=6 income=94394 expense=67694 Bt=147295 Rt=173996 [151820 .. 195525]
  For comparison, the honest arithmetic 'nothing changes': Bt(h) = 15 000*h -> [15000, 30000, 45000, 60000, 75000, 90000]

=== (C) how much noise 1000 Monte-Carlo draws add over the exact formula ===
  h=1 MC width mean   15602.7 sd over seeds   224.8 | exact normal formula   15696.3
  h=2 MC width mean   18207.2 sd over seeds   508.3 | exact normal formula   18124.6
  h=3 MC width mean   20128.4 sd over seeds   390.5 | exact normal formula   20263.9
  h=4 MC width mean   22340.9 sd over seeds   486.9 | exact normal formula   22198.0
  h=5 MC width mean   23778.7 sd over seeds   547.1 | exact normal formula   23976.5
  h=6 MC width mean   25366.0 sd over seeds   635.9 | exact normal formula   25632.0
```

**(A) Ширина коридора = 5 % от величины Rt, а не от неопределённости.** Отсюда два абсурда:

1. **Богатый получает широкий коридор, бедный — узкий, хотя будущее у них одинаково непредсказуемо.** Один и тот же
   человек (доход 100 000 ₽, траты 85 000 ₽), только стартовый остаток разный: при B0 = 0 коридор на первом месяце
   **4 857 ₽**, при B0 = 600 000 ₽ — **101 994 ₽**. В 21 раз шире при ровно той же неопределённости дохода и трат.
   Неопределённость приписана **размеру счёта**, а не жизни человека.
2. 🔴 **У человека, у которого Rt = 0, коридор схлопывается ровно в ноль.** Доход = расходу, остаток 0 → продукт
   рисует p10 = p50 = p90 = 0,00 на всех шести месяцах: «я абсолютно уверен, что у вас будет ровно ноль».
   Это **самый опасный пользователь** (живёт в ноль, любой сбой — в минус), и именно ему график обещает
   определённость. Обратная сторона той же формулы: чем ближе к границе дефицита, тем «увереннее» продукт.

**(B) Синтетическая история выдумывает не только шум, но и тренд — и он уезжает в прогноз.**
У человека нет истории, он ввёл доход 100 000 ₽ и расход 85 000 ₽. Честная арифметика «ничего не меняется»:
через 6 месяцев накоплено **90 000 ₽**. Продукт показывает **147 295 ₽** — на **64 % больше**.
Механика: `build_history_from_current` придумывает шесть точек, демпфированный Holt (он включается от 3 точек —
а синтетика всегда даёт 6) находит в этом **шуме** тренд и экстраполирует его. С фиксированным сидом 2 «расход»
получает нисходящий тренд и падает со введённых 85 000 ₽ до **67 694 ₽** к шестому месяцу — расходы человека
«сами собой» упали на 20 %, хотя он не делал ничего. Сид фиксирован (1/2/3), значит **ошибка одинаковая
и систематическая у всех пользователей без истории**, а не случайная.

**(C) Монте-Карло здесь не нужен вообще.** 1000 выборок воспроизводят точную формулу нормального квантиля с ошибкой
±0,2–0,6 тыс. ₽ на ширине 15–25 тыс. ₽ (разброс по 20 сидам). То есть тысяча прогонов — это способ получить
формулу `2·1,2816·σ` с добавленным шумом. Подтверждает вывод Г39 п. 4.

🔴 **Итог пункта 2.** График **не валиден** по всем трём принятым в литературе критериям сразу: покрытие
(15–33 % против заявленных 80 %), калибровка (PIT U-образный, дисперсия 0,21 против 0,083), острота/точность
(CRPS в 3–4 раза хуже простой альтернативы). Плюс два дефекта, которые не лечатся перекалибровкой: ноль ширины
в точке дефицита и выдуманный тренд из выдуманной истории.

### 2.3. Реквизиты: чем в науке принято мерить честность прогноза

- **Gneiting T., Raftery A. E., «Strictly Proper Scoring Rules, Prediction, and Estimation»**, JASA 102(477):359–378, 2007,
  DOI 10.1198/016214506000001437. Crossref по этому запросу отдал препринты (DOI 10.21236/ada454828, 2005;
  10.21236/ada459827, 2004) — они и есть технические отчёты того же текста. Суть, которая нам нужна: *правильное*
  (proper) правило нельзя «обыграть» ни самоуверенностью, ни перестраховкой — минимум достигается только при истинном
  распределении. CRPS — правильное правило; **покрытие само по себе — нет** (широкий коридор всегда покрывает).
- **Gneiting T., Katzfuss M., «Probabilistic Forecasting»**, Annual Review of Statistics and Its Application 1:125–151,
  2014, DOI 10.1146/annurev-statistics-062713-085831 (Crossref 200). Отсюда формула цели:
  «maximizing the sharpness of the predictive distributions subject to calibration» — сначала честность, потом узость.
- **Diebold F. X., Gunther T. A., Tay A. S., «Evaluating Density Forecasts with Applications to Financial Risk
  Management»**, International Economic Review 39(4):863, 1998, DOI 10.2307/2527342 (Crossref 200) — работа, откуда
  в практику пришёл PIT: если прогноз честен, `u_t = F_t(y_t)` равномерны на [0,1].
- Учебное изложение (вспомогательное, для формулировок): `mlmetrics.org/evaluating_distributions.html` (Exa, полный
  текст): «If the forecast distributions are consistently too narrow, the realized outcomes will frequently fall in
  the tails. This leads to PIT values clustering near 0 and 1, creating a U-shaped histogram. The model is
  "overconfident" and surprised too often.» — **дословное описание нашей гистограммы**.
- Оговорка оттуда же, которую надо уважать при приёмке: «with enough observations the test rejects uniformity for
  miscalibration too small to matter; the effect size is what should drive a decision», и «overlapping multi-horizon
  forecasts are strongly autocorrelated — so treat the p-value as a rough flag and the histogram shape as the real
  evidence». Поэтому порог приёмки надо ставить по **величине отклонения**, а не по p-значению (см. ИТОГ).

### 2.4. Разброс доходов и расходов домохозяйств РФ и оценка по короткой истории

Что известно из уже сделанных тем (не переоткрываю):
- **Г44** — доступ к микроданным: RLMS-HSE (годовая периодичность, не помесячная), ОДПФ (Обследование домохозяйств
  по потребительским финансам ЦБ), ВНДН Росстата. 🔴 Ограничение, важное именно здесь: **все три — годовые или
  разовые обследования, помесячной истории доходов одного домохозяйства в открытом доступе нет.** Поэтому бэктест
  «на реальных рядах» для нашей задачи (месяц к месяцу у одного человека) **сделать не на чем** — это ограничение
  метода, а не лень: в открытых российских данных нужного объекта не существует.
- **Г17.8 / Мишура А. В. и др. (2025), «The impact of consumer lending on consumption volume and volatility»**,
  Вопросы экономики № 5, DOI 10.32609/0042-8736-2025-5-111-129: «consumer bank lending in Russia is **not a smoothing
  factor, but a factor of additional volatility of consumption**». То есть у закредитованного россиянина месячный
  разброс потребления **выше**, а не ниже — коридор в 5 % для него заведомо фантастика.
- **ADR-015 продукта** (закон шума генератора портретов, `tools/portrait_testing/generator.py`): волатильность дохода
  берётся из набора {0; 0; 0; 0,1; 0,2; 0,4; 0,6; 0,9}, то есть до ±90 % месяц к месяцу. Сам продукт в своём
  генераторе признаёт разброс до 90 %, а на графике рисует 5 %. Это внутреннее противоречие проекта.

🔴 **Как оценивать разброс по короткой истории — ответ, который выдержал проверку числом (стенд п. 2.1):**
берём **собственный чистый поток человека** `net = доход − расход − платежи` за T месяцев, считаем его выборочное
стандартное отклонение `s`, и коридор баланса на h месяцев вперёд строим как
`B0 + m·h ± t_{0,9}(T−1) · s · √h · √(1+h/T)`, где `m` — среднее потока. Множитель `√(1+h/T)` — поправка на то, что
`m` и `s` сами оценены по T точкам (у нас T = 6, это не мелочь). Это даёт 81–84,5 % на первом месяце (стенд).
Дальше, если нужны честные 80 % на всех горизонтах, ширина домножается на **конформный множитель** `q(h)`,
откалиброванный офлайн: стенд Г45 получил q = 1,46 / 1,91 / 2,42 / 2,59 / 2,77 / 3,10 при T = 6 и
1,34 / 1,60 / 1,82 / 1,94 / 2,10 / 2,21 при T = 12 (нормальный z был бы 1,28). Результат — 77–80 % на всех шести
горизонтах против 15–33 % сейчас.

---

## Пункт 3. Веерные диаграммы в центральных банках: как строят и как проверяют

**Аналогия.** Банк Англии — единственная организация, которая двадцать лет подряд публично отвечает на вопрос
«а мой веер не врал?» и **меняет веер, когда он наврал**. Это готовый образец процедуры, которую нам надо завести
у себя, а не только образец картинки.

### 3.1. Как строит Банк Англии

Источник: **«The Inflation Report projections: understanding the fan chart»**, Bank of England Quarterly Bulletin,
1998 Q1, автор Erik Britton, Paul Fisher, John Whitley. Канал: landing-страница через `r.jina.ai` HTTP 200 (только
меню), полный текст — `curl` с браузерным UA на PDF
`https://www.bankofengland.co.uk/-/media/boe/files/quarterly-bulletin/1998/the-inflation-report-projections-understanding-the-fan-chart.pdf`,
**HTTP 200**, далее `pdftotext` (5 355 слов). Дословно:

> «The uncertainty in the subjective assessment of inflation relates to how likely it is that the future events will
> differ from the central view. It is therefore a forward-looking view of the risks to the forecast, not a mechanical
> extrapolation of past uncertainty. Nevertheless, **the initial calibration of uncertainty is based on the experience
> of forecast errors from the previous ten years**.»

> «The degree of uncertainty (the degree of dispersion in the distribution) can be measured by a variety of statistics
> such as variance, mean absolute error or inter-quartile range. The Bank uses a variance measure.»

> «It is always tempting when forecasting to assume that the current degree of uncertainty is greater than usual…
> In practice, it has been shown that, though forecasting is indeed notoriously uncertain in an absolute sense,
> the track record of forecasts is rather better than one would suppose from simply evaluating the uncertainty
> inherent in statistical models.»

🔴 **Ключевое для нас:** ширина веера у БА калибруется по **фактическим ошибкам прошлых прогнозов за 10 лет**
(и лишь затем корректируется суждением комитета). Это ровно тот принцип, которого в нашем коде нет: у нас ширина
взята из константы `MC_SIGMA_BASE = 0.05`, не выведенной ни из чьих ошибок.

### 3.2. Как Банк Англии проверяет веер задним числом

Источник: **Elder R., Kapetanios G., Taylor T., Yates T., «Assessing the MPC's fan charts»**, Bank of England
Quarterly Bulletin, 2005 Q3, с. 326–348. Канал: `curl` с браузерным UA на
`https://www.bankofengland.co.uk/-/media/boe/files/quarterly-bulletin/2005/assessing-the-mpcs-fan-charts.pdf`,
**HTTP 200**, `pdftotext`, 14 343 слова. (Crossref по названию ничего релевантного не отдал — это Quarterly Bulletin,
не журнальная статья с DOI.) Дословно:

> «With only six years of fan chart projections that can be compared with outturns, the sample is too small to draw
> strong conclusions. But to date, at most forecast horizons, inflation and output growth outcomes have been dispersed
> broadly in line with the MPC's fan chart bands.»

> «If the sample were large enough, and the fan charts accurately depicted the likely dispersion of outturns, then we
> would expect half of the outturns to lie in the central 50% bands, and 30% to lie in the central 30% bands.»
> — это **проверка покрытия**, наш п. 2.1.

> «the dots appear clustered towards the centre for forecasts seven, eight and nine quarters ahead. That means outturns
> were less dispersed than the fan chart bands implied at long horizons. Furthermore, for GDP growth at short horizons,
> a large proportion of outturns were well above the median and clustered above the 90th percentile. That indicates…
> that the fan charts **may have been too narrow**.»
> — это **PIT-диаграмма** (положение точки = процентиль прогноза, в который попал факт), нарисованная в виде точек.

> «The first test is a Kolmogorov-Smirnov (KS) test. One problem with the KS test is that it is not very powerful in
> small samples… The second test we use is an extension of a test first suggested by Berkowitz (2001). It is thought
> to be more powerful if the sample size is small, and it allows for dependence of forecast distributions over time.»

> 🔴 «As a result of this analysis, which was summarised in a box in the August 2005 Inflation Report, **the GDP fan
> charts have been widened at short horizons**, which should mitigate this problem.»

**Что отсюда берём буквально:** (1) проверка = покрытие по каждому горизонту + PIT + KS/Berkowitz с поправкой на
зависимость соседних прогнозов; (2) результат проверки **обязан менять картинку** — БА расширил веер, обнаружив
недопокрытие. Мы можем сделать то же дешевле: у нас есть синтетический стенд, где проверка стоит минуты, а не годы.

### 3.3. ЦБ РФ

Из темы 32 (`key_rate_history_forecastability_2026-09-10.md`, п. 3.1.c, расчёт агента; не переоткрываю):
диапазон средней ключевой ставки на **следующий** год ЦБ попадал **2 раза из 16 (12 %)**, через год — **0 из 12**,
и на этих горизонтах ЦБ **хуже наивного** «ставка останется как сейчас» (средняя ошибка 5,04 п.п. против 4,76).
Почти все промахи — занижение.

🔴 **Урок, который стоит дороже картинки:** организация с сотней экономистов и полным доступом к данным
промахивается своим интервалом в 88 % случаев на горизонте год. Мы строим коридор на 6 месяцев вперёд по 6 точкам
истории одного человека. Обещать ему «80 %» и рисовать ленту шириной в половину месячного дохода —
это не оптимизм, это обещание, которое нечем обеспечить.

---

## Пункт 4. 🔴 Понимают ли люди такие графики

**Аналогия.** Коридор на графике — это как надпись «глубина здесь от 1 до 3 метров». Человек читает её как
«глубина 1 или 3», а не «скорее всего около 2, но бывает и 4». Граница ленты на картинке превращается в голове
в забор: внутри — «может быть», снаружи — «не бывает». Это измерено, а не предположено.

### 4.1. Люди читают интервал как две конкретные величины, а не как неопределённость

**Padilla L., Kay M., Hullman J., «Uncertainty Visualization»**, в Wiley StatsRef: Statistics Reference Online, 2021,
DOI 10.1002/9781118445112.stat08296. Полный препринт добыт через Exa:
`space.ucmerced.edu/Downloads/publications/Uncertainty_Visualization_Padilla_Kay_Hullman_2022.pdf`. Дословно:

> «The deterministic construal error is when individuals attempt to substitute visual uncertainty information for
> deterministic information. For example, Joslyn and LeClerc found that when participants viewed mean temperature
> forecasts that included 95% confidence intervals depicted as bars with end caps, they **incorrectly believed that
> the error bars represented high and low temperatures**. The participants maintained this belief **even when Joslyn
> and LeClerc tested a condition where the correct way to interpret the forecast was shown prominently in a key**.»

> «Visualizations of intervals are generally hard for both experts and novices to use, and **errors persist even with
> extensive instructions**.»

> «Padilla et al. proposed the data visualization theory that when visual boundaries, such as isocontours and error
> bars, are used for continuous data, **the boundaries lead people to conceptualize the data as categorical**.»

> Рекомендация авторов дословно: «There is no single visualization technique we endorse, but there are some that
> should be critically considered before employing them. **Intervals, such as error bars and the Cone of Uncertainty,
> can be particularly challenging for viewers.** If a designer needs to show an interval, we also recommend displaying
> information that is more representative, such as a scatterplot, violin plot, gradient plot, ensemble plot,
> **quantile dotplot**, or HOP. **Just showing an interval alone could lead people to conceptualize the data as
> categorical.**»

**Padilla L., Castro S. C., Hosseinpour H., «A review of uncertainty visualization errors: Working memory as an
explanatory theory»**, Psychology of Learning and Motivation, vol. 74, 2021, Ch. 7 (Elsevier;
`sciencedirect.com/science/article/abs/pii/S0079742121000074`, полный PDF — `space.ucmerced.edu`, через Exa). Дословно:

> «Savelli and Joslyn found that **36% of participants believed that the confidence intervals represented high- and
> low-temperature forecasts rather than uncertainty around the mean**. Savelli and Joslyn then tested alternative
> visualization techniques, including dotted lines and blurry boundaries, and found that the participants still
> assumed that the intervals around the means were high- and low-temperature forecasts.»

> «People tend to believe that error bars contain the distribution of values… If the two bars are far apart, the
> boundaries lead people to believe that these boundaries contain all the relevant values.»

Реквизиты первоисточника этого 36 %: **Savelli S., Joslyn S., «The Advantages of Predictive Interval Forecasts for
Non-Expert Users and the Impact of Visualizations»**, Applied Cognitive Psychology 27(4):527–541, 2013,
DOI 10.1002/acp.2932 (Crossref 200). Смежное: **Joslyn S., LeClerc J., «Decisions With Uncertainty: The Glass Half
Full»**, Current Directions in Psychological Science 22(4):308–315, 2013, DOI 10.1177/0963721413481473 (Crossref 200);
**Joslyn, Nemec, Savelli**, Weather, Climate, and Society 5(2):133–147, 2013, DOI 10.1175/WCAS-D-12-00007.1.

🔴 **Перенос на наш экран.** «Коридор p10…p90» пользователь прочитает как «в худшем случае у меня будет столько,
в лучшем — столько». Не «в 20 % случаев будет хуже нижней границы». Это значит: наш **и без того вдвое узкий**
коридор (п. 2) ещё и читается как **жёсткая граница снизу** — то есть пользователь получает ложную гарантию
«хуже, чем p10, не будет», тогда как на деле хуже p10 происходит в **40 %** случаев (нижняя корзина PIT = 0,40, стенд п. 2.1).

### 4.2. Что вместо интервала работает лучше: квантильные точечные диаграммы

**Kay M., Kola T., Hullman J. R., Munson S. A., «When (ish) is My Bus? User-centered Visualizations of Uncertainty in
Everyday, Mobile Predictive Systems»**, CHI '16, с. 5092–5103, DOI 10.1145/2858036.2858558. Полный PDF:
`mjskay.com/papers/chi_2016_uncertain_bus.pdf` (Exa, полный текст). Дословно:

> «we propose a novel discrete representation of continuous outcomes designed for small screens, **quantile dotplots**.
> In a controlled experiment we find that quantile dotplots **reduce the variance of probabilistic estimates by
> ~1.15 times compared to density plots** and facilitate more confident estimation by end-users.»

> «By using quantiles we facilitate interval estimation from frequencies: e.g., knowing there are 50 dots here,
> **if we are willing to miss our bus 3/50 times, we can count 3 dots from the left** to get a one-sided 94% (1 − 3/50)
> prediction interval corresponding to that risk tolerance.»

> «error bars and probability densities **require prior experience with statistical models to correctly interpret**.
> People can better understand probabilistic information when it is **framed in terms of discrete events**.»

**Fernandes M., Walls L., Munson S., Hullman J., Kay M., «Uncertainty Displays Using Quantile Dotplots or CDFs Improve
Transit Decision-Making»**, CHI '18, DOI 10.1145/3173574.3173718 (страница ACM DL добыта через Exa — прямой `WebFetch`
на ACM традиционно 403; авторский PDF `mjskay.com/papers/chi_2018_uncertain_bus_decisions.pdf` через Exa вернул
`CRAWL_NOT_FOUND`, полный текст не открывался, реферат — дословно с ACM). Дословно:

> «Evaluations of uncertainty displays for transit prediction have assessed people's ability to extract probabilities,
> **but not the quality of their decisions**. In a controlled, incentivized experiment, we had subjects decide when to
> catch a bus… **Frequency-based visualizations previously shown to allow people to better extract probabilities
> (quantile dotplots) yielded better decisions.** Decisions with quantile dotplots with 50 outcomes were (1) better on
> average, having **expected payoffs 97% of optimal** (95% CI: [95%,98%]), **5 percentage points more than control**
> (95% CI: [2,8]); and (2) more consistent, having within-subject standard deviation of 3 percentage points…
> **Cumulative distribution function plots performed nearly as well, and both outperformed textual uncertainty,
> which was sensitive to the probability interval communicated.**»

🔴 **Три вывода, прямо применимые к нашему экрану:**
1. Оценивать надо **качество решения**, а не «понял ли человек картинку». Это единственная работа, которая мерила
   именно решение, и разница между лучшей и худшей подачей — **5 процентных пунктов выигрыша** при прочих равных.
2. **Квантильная точечная диаграмма и CDF победили и текст, и интервал.** «Сколько-то точек из 50» — это счёт,
   а не чтение шкалы.
3. **Текстовая подача неопределённости чувствительна к тому, какой интервал назван** — то есть «80 %-коридор»
   словами работает хуже и нестабильно.

### 4.3. Интервал вокруг среднего преувеличивает уверенность

**Hofman J. M., Goldstein D. G., Hullman J., «How Visualizing Inferential Uncertainty Can Mislead Readers About
Treatment Effects in Scientific Results»**, CHI '20, с. 1–12, DOI 10.1145/3313831.3376454 (Crossref 200; полный PDF
`dangoldstein.com/papers/Hofman_Goldstein_Hullman_Visualizing_Uncertainty_Mislead_Scientific.pdf`, Exa). Дословно:

> «responses closest to the normatively correct answers across all measures were attained by people presented with
> visualizations that encoded information about **variation in individual outcomes (95% PIs or HOPs)**. These results
> are important because scientists often display their results using **95% CIs, the least accurate format we tested**.»

Смежно: **Correll M., Gleicher M., «Error Bars Considered Harmful: Exploring Alternate Encodings for Mean and Error»**,
IEEE TVCG 20(12):2142–2151, 2014, DOI 10.1109/TVCG.2014.2346298 (Crossref 200) — градиентные и violin-подачи дают
более верную оценку правдоподобия значения, чем «усы».

**Перенос:** наш коридор — это интервал вокруг **точечного прогноза**, то есть ближе к «inferential uncertainty».
Пользователю нужна **outcome uncertainty**: «в каких месяцах и как часто я уйду в минус», а не «где проходит
средняя траектория ± сколько-то».

---

## Пункт 5. Нужен ли график вообще — или дата, сценарии и шанс

**Аналогия.** Прогноз погоды на телефоне не рисует веер температуры. Он говорит «дождь, 70 %, возьми зонт».
Веер нужен тому, кто принимает решение о **распределении**, а не о действии. Наш пользователь принимает решение
о действии: платить долг или копить, урезать траты или нет.

### 5.1. Стенд: можно ли сделать честным одно число «шанс уйти в минус»

Стенд `g45/p_alt.py`, 600 портретов, история 6 месяцев, горизонт 6 месяцев. Проверяется **надёжность (reliability)**
вероятности «баланс уйдёт ниже нуля в ближайшие 6 месяцев»: если продукт говорит «30 %», должно случаться примерно
в 30 % случаев. Вывод дословно:

```
N=600 portraits, T=6 months of history, horizon 6 months. Actually went below zero within 6 months: 12.2%

  reliability of 'product noise model' (forecast probability vs observed frequency):
    forecast 0.00-0.05: n= 517  mean forecast 0.00  actual frequency 0.09
    forecast 0.95-1.00: n=  83  mean forecast 1.00  actual frequency 0.30
    Brier score 0.177  (lower is better; always-say-base-rate = 0.107)

  reliability of 'own-spread model' (forecast probability vs observed frequency):
    forecast 0.00-0.05: n= 415  mean forecast 0.00  actual frequency 0.06
    forecast 0.05-0.20: n=  85  mean forecast 0.11  actual frequency 0.18
    forecast 0.20-0.40: n=  66  mean forecast 0.30  actual frequency 0.27
    forecast 0.40-0.60: n=  31  mean forecast 0.48  actual frequency 0.45
    forecast 0.60-0.80: n=   3  mean forecast 0.63  actual frequency 1.00
    Brier score 0.093  (lower is better; always-say-base-rate = 0.107)

  mean forecast probability: product 0.138, own-spread 0.079, truth 0.122
```

🔴 **Что это значит человеческими словами.**
- Шумовая модель продукта **не умеет производить промежуточные вероятности вообще**: из 600 человек она 517 раз
  сказала «0 %» и 83 раза «100 %». Ничего между. Это прямое следствие того, что коридор узкий: ноль либо далеко
  за границей, либо далеко внутри.
- Когда продукт говорит **«100 %, вы уйдёте в минус», это случается в 30 %** случаев. Когда говорит «0 %» —
  случается в **9 %**.
- Оценка качества (Brier score, меньше — лучше): **0,177 у продукта против 0,107** у тупейшего правила «всем говорить
  среднюю частоту 12 %». 🔴 **Модель продукта хуже, чем вообще не считать.**
- Модель по собственному разбросу человека: **0,093**, то есть лучше базовой ставки, и по корзинам ложится честно
  (сказала 30 % — случилось 27 %; сказала 48 % — случилось 45 %).

**Вывод:** заменять график одним числом **можно и нужно**, но только если под ним стоит разброс самого человека.
На текущем движке любая производная от него величина — дата, шанс, сценарий — унаследует ту же ложь.

### 5.2. Что говорит практика финансового планирования (практикующие источники, не рецензируемые)

🟡 **Статус источников: отраслевые блоги и вендорские материалы, не рецензируемая наука.** Маркетинговый язык
в них присутствует, числа без публикации метода. Беру только то, что согласуется с рецензируемой частью (п. 4).

- **Kitces M., «It's Time For The Next Generation Of Monte Carlo Analysis Software»** (kitces.com, 24.07.2012; домен
  отдаёт 403 и `WebFetch`, и `curl` с браузерным UA — **текст добыт через Exa**). Дословно: «use of Monte Carlo
  analysis has begun to focus excessively on a singular probability of success, **that itself can be almost as
  misleading as straight-line projections when not viewed in proper context**… what's ultimately needed is software
  that shows not just the probability of success, but also **the magnitude and consequences of failure**, and a
  **sensitivity analysis** that helps clients understand the impact of the trade-off decisions they have available.»
  И ключевой пример-иллюстрация: «Would you rather have scenario A, an 85% probability of success, or scenario B,
  a 90% probability?… what if the 15% failure scenario A only required a 5% spending cut… and the latter 10% failure
  scenario B would require a 50% spending cut, including selling your house?»
- **Tharp D., «How Advisors Can Communicate Monte Carlo Results To Clients»** (kitces.com, 29.06.2022, через Exa):
  «maintaining a 70% probability of success level – implying only a 30% probability of adjustment – **would in reality
  have required downward spending adjustments in nearly 100% of all historical scenarios**»; вывод автора:
  «communicating results from a guardrails-based plan **in terms of dollars** to clients is likely far more effective
  … than reporting a probability of adjustment metric».
- **«Making Monte Carlo results more relevant with the right level of abstraction»** (Financial Planning, 21.04.2021,
  через Exa): «probability of success alone does not convey enough information… **this unidimensional presentation…
  entirely ignores magnitude of failure**».
- **«The Dangers of Monte Carlo Simulations»** (Advisor Perspectives, 10.01.2023, через Exa): «**The results from Monte
  Carlo are entirely determined by the CMAs used**… unless advisors are confident that they are using highly accurate
  CMAs, **probability of success metrics will mislead clients into a false sense of security**». Их числовой пример:
  смена предположения о доходности с 7,11 % на 8,52 % двигает «вероятность успеха» с 78 % до 87 %.
- **Income Lab, «Why Probability of Success Is Wrong for Retirement Planning»** (31.03.2026, через Exa) — 🟡 **явно
  вендорский материал конкурента-методологии, числа непроверяемы**, привожу только как иллюстрацию отраслевого спора:
  «68% of advisors report that clients struggle to interpret probability-based outputs».

🔴 **Общий знаменатель всех пяти и совпадение с наукой п. 4:** одна цифра/одна лента без **величины провала**
и без **рычагов** («что изменится, если урезать траты на 10 %») решение не поддерживает. Это ровно то, что мерили
Fernandes et al.: побеждает подача, из которой **прямо вычитается действие**.

### 5.3. Что предлагается вместо графика (материал для синтеза, не решение)

| Что показать | Отвечает на вопрос | Чем обеспечено | Проверяется |
|---|---|---|---|
| **Дата**: «при нынешнем темпе подушки хватает до марта» + «при потере дохода — до ноября» | «хватит ли денег» | арифметика без прогноза + один сценарий | точность даты (MAE в месяцах) на бэктесте |
| **Шанс**: «вероятность уйти в минус за 6 месяцев — 27 %» | «насколько я на грани» | разброс собственного потока человека | reliability-диаграмма + Brier (п. 5.1: 0,093 против 0,177) |
| **2–3 названных сценария** («как сейчас» / «минус 20 % дохода» / «крупная покупка 80 тыс.») | «что будет, если» | детерминированный пересчёт, без вероятностей | не требует калибровки — это не прогноз, а арифметика «если» |
| **Квантильная точечная диаграмма** на 20–50 точек вместо ленты, если картинка нужна | «насколько это точно» | те же квантили, но считаемые | Kay 2016 / Fernandes 2018 (п. 4.2) |
| **Рычаги**: «урезать траты на 10 % → шанс минуса 27 % → 9 %» | «что мне делать» | пересчёт того же числа при изменении входа | сравнение решений, а не картинок |

**Против самой идеи веера на 6 месяцев по 6 точкам** играет и п. 3.3: ЦБ РФ со всей своей аналитикой попадает
в свой годовой интервал **12 % раз**. Веер — инструмент организации, которая **публично отчитывается за свои
промахи**. Продукт, который не ведёт учёта своих промахов, веер рисовать не заработал.

---

## Пункт 6. Правило для случая «истории нет»

**Аналогия.** Врач, у которого нет анализов, не рисует график динамики гемоглобина по выдуманным точкам.
Он пишет «данных нет» и назначает анализ.

**Что делает продукт сейчас** (стенд п. 2.2, блок B): выдумывает 6 точек, находит в них тренд, экстраполирует его
и рисует вокруг коридор. У человека, который ввёл доход 100 000 ₽ и расход 85 000 ₽, через 6 месяцев показывается
**147 295 ₽ вместо честных 90 000 ₽** (+64 %), потому что «расход» в выдуманной истории сам собой упал до 67 694 ₽.
Сид фиксирован → **ошибка одинаковая у всех** пользователей без истории. Это не шум, это систематическое враньё
в пользу оптимизма — самый опасный знак ошибки для финансового советчика.

**Правило, которое следует из материала (три уровня, по количеству точек):**

| Сколько реальных месяцев | Что можно показывать | Чего показывать нельзя |
|---|---|---|
| **0–1** | только арифметику «если ничего не изменится»: `Bt(h) = B0 + (доход − расход − платежи)·h`, одной линией, с подписью «это не прогноз, а расчёт при неизменных суммах»; плюс сценарии «минус 20 % дохода» | любой коридор, любую вероятность, любой тренд |
| **2–5** | ту же линию + **популяционный** коридор по типу человека (зарплатник/нерегулярный доход), явно помеченный как «по данным похожих людей, не по вашим» | собственный тренд (Holt на 3 точках ловит шум — Г39/Г43) |
| **6+** | коридор по собственному разбросу с конформной поправкой (п. 2.4) + шанс ухода в минус (п. 5.1) | обещание «80 %» без замера покрытия |

🔴 **Отдельно: синтетическую историю нельзя подавать на вход прогнозной функции ни при каких условиях.**
Если данных нет — источник неопределённости не «шум 5 %», а **полное отсутствие информации**, и правильная
реакция интерфейса — не картинка, а просьба ввести данные (или подключить выписку). Три месяца реальной истории
дороже любой модели: покрытие NORM на T=12 против T=6 (стенд п. 2.1) отличается на 3,5 п.п. на первом месяце,
а вот **выдуманная история портит точечный прогноз на 64 %** — на порядок больше, чем любая тонкая настройка модели.

---

## ИТОГ Г45

### 🔴 Прямой ответ

**График не валиден и в текущем виде вреден.** Не «спорен», не «требует доработки» — он даёт пользователю
систематически ложное обещание. Проверено четырьмя независимыми критериями, каждый — число, не мнение:

| Критерий | Что должно быть | Что есть | Источник числа |
|---|---|---|---|
| **Покрытие** коридора «80 %» | 76–84 % | **15–33 %** (T=6: 25,2 % → 15,2 % по горизонтам 1→6) | стенд `g45/p_valid.py`, 400 портретов |
| **Калибровка** (PIT) | ровная гистограмма, дисперсия 0,083 | **U-образная: 0,40 и 0,42 в крайних корзинах**, дисперсия 0,21, KS 0,37 | там же |
| **Точность распределения** (CRPS) | не хуже простой альтернативы | **в 3–4 раза хуже** (0,81–2,87 против 0,22–1,00 в долях месячного дохода) | там же |
| **Надёжность производного решения** (Brier для «уйду ли в минус») | лучше базовой ставки 0,107 | **0,177 — хуже, чем не считать вовсе** | стенд `g45/p_alt.py`, 600 портретов |

Плюс три дефекта, которые **не лечатся перекалибровкой**, потому что это дефекты замысла, а не настройки:
1. 🔴 **Ширина коридора = 5 % от величины Rt.** У человека, живущего в ноль, коридор схлопывается **ровно в ноль**
   (замер: p10 = p50 = p90 = 0,00 на всех шести месяцах). Самому уязвимому пользователю продукт обещает абсолютную
   определённость. У человека с запасом 600 тыс. ₽ при том же доходе коридор **в 21 раз шире**, хотя будущее у них
   одинаково неопределённо.
2. 🔴 **Когда истории нет, прогноз строится по выдуманной истории** и завышает накопления на **64 %** (147 295 ₽
   вместо 90 000 ₽ на шестом месяце) с **фиксированным сидом**, то есть одинаково у всех.
3. **По оси Y стоит `Rt`** — служебная величина, дважды считающая месячный поток (Г40), которую пользователь
   читает как «сколько будет на счету». Даже честный коридор вокруг неё отвечал бы не на тот вопрос.

**Полезен ли он?** Нет. По п. 4 (рецензируемые эксперименты) пользователь читает границы ленты как «худший и лучший
случай» (deterministic construal error, 36 % участников у Savelli & Joslyn 2013, и ошибка **не исчезает даже с
пояснением в легенде**). То есть узкий коридор не просто неточен — он читается как **гарантия**, что хуже нижней
границы не будет, тогда как хуже неё оказывается 40 % исходов.

### Что должно заменить или дополнить

1. **Ширина — от собственного разброса человека, не от величины показателя.**
   `B0 + m·h ± t_{0,9}(T−1)·s·√h·√(1+h/T)`, где `m`, `s` — среднее и СКО собственного чистого потока за T месяцев.
   Даёт 81–84,5 % на первом месяце вместо 25 %. **Монте-Карло не нужен** — 1000 прогонов воспроизводят ту же формулу
   с добавленным шумом (замер: разброс ширины по сидам ±0,2–0,6 тыс. ₽; подтверждает Г39 п. 4).
2. **Конформный множитель по горизонту**, откалиброванный офлайн на синтетике: q(h) = 1,46 / 1,91 / 2,42 / 2,59 /
   2,77 / 3,10 при T=6. Даёт 77–80 % на всех шести горизонтах.
3. **Сменить главный вывод экрана** с ленты на то, из чего вычитается действие (п. 5.3): **дата** «подушки хватает
   до …», **шанс** «уйти в минус за 6 мес. — N %» (он честен при правильном разбросе: Brier 0,093 против 0,177),
   **2–3 названных сценария**, **рычаги** («урезать траты на 10 % → шанс 27 % → 9 %»).
4. **Если картинка всё-таки нужна** — квантильная точечная диаграмма или CDF вместо ленты (Kay 2016: оценки
   устойчивее в ~1,15 раза; Fernandes 2018: решения на 5 п.п. ближе к оптимальным, чем без неопределённости,
   и лучше, чем текст и чем интервал).
5. **По оси Y — баланс, а не Rt.** Дефект двойного счёта потока — тема Г40, здесь только фиксирую, что он
   попадает прямо на график.

### Как проверять валидность после изменения (метрики и порог приёмки)

Процедура — копия того, что делает Банк Англии (п. 3.2), но на синтетическом стенде, где она стоит минуты:
бэктест с катящимся началом, затем четыре проверки. Пороги при 400 портретах (стандартная ошибка покрытия ≈ 2 п.п.):

| Метрика | Как считать | 🔴 Порог приёмки |
|---|---|---|
| **Покрытие**, отдельно по каждому горизонту 1…6 **и по каждому типу человека** | доля фактов внутри p10…p90 | **76–84 %** на каждом горизонте; ни один тип не ниже **70 %** |
| **PIT-гистограмма**, 10 корзин, по горизонтам и пулом | `u = F(y)` | ни одна корзина не выходит за **0,07–0,13**; дисперсия PIT в **0,075–0,095** |
| **CRPS / interval score** | нормировать на средний месячный доход | **не хуже базового** «собственный разброс + √h» ни на одном горизонте |
| **Brier + reliability** для «шанс уйти в минус» | по корзинам прогнозной вероятности | Brier **ниже базовой ставки**; в каждой корзине разрыв прогноз/факт ≤ **0,10** |

Две оговорки, обе из литературы, обе обязательны, иначе проверка сама себя обманет:
- p-значение KS — только флаг, не критерий: соседние горизонты одного прогноза сильно зависимы, и на большой выборке
  тест отвергает равномерность при отклонении, не имеющем практического значения. Решение принимается **по величине
  отклонения**, а не по p (Gneiting & Katzfuss 2014; учебное изложение `mlmetrics.org`).
- Покрытие **само по себе — неправильное (improper) правило**: коридор «от минус бесконечности до плюс бесконечности»
  покрывает 100 %. Поэтому покрытие всегда в паре с CRPS/interval score (Gneiting & Raftery 2007).

### Правило для случая «истории нет»

🔴 **Синтетическая история на вход прогнозной функции не подаётся никогда.** Градация:
- **0–1 месяц реальных данных:** одна линия «при неизменных суммах» (`B0 + поток·h`) с явной подписью, что это
  арифметика, а не прогноз; никакого коридора, никакой вероятности, никакого тренда. Плюс 1–2 сценария «а если».
- **2–5 месяцев:** линия + коридор **по популяции похожих людей**, помеченный как чужой, не свой. Собственный тренд
  не считать (Holt на 3 точках ловит шум — Г39, Г43).
- **6+ месяцев:** собственный разброс + конформная поправка + шанс минуса.

Обоснование одним числом: выдуманная история портит точечный прогноз на **64 %**, тогда как разница между историей
в 6 и 12 месяцев стоит **3,5 п.п.** покрытия. Первое — катастрофа, второе — тонкая настройка.

### Что осталось неизвестным (честно)

1. 🔴 **Бэктест на реальных российских помесячных рядах не сделан — не на чем.** RLMS-HSE, ОДПФ, ВНДН (условия
   доступа — Г44, не переоткрывал) дают **годовую или разовую** периодичность; открытых помесячных рядов дохода
   и расхода одного домохозяйства в РФ нет. Все числа Г45 получены на синтетических портретах генератора Г43
   (закон шума ADR-015 самого продукта). Это **ограничение данных, а не метода**: как только появятся собственные
   обезличенные данные после запуска, тот же стенд считается на них без изменений.
2. **Полный текст Fernandes et al. 2018 не открыт** — авторский PDF `mjskay.com/papers/chi_2018_uncertain_bus_decisions.pdf`
   вернул через Exa `CRAWL_NOT_FOUND`; ACM DL (`dl.acm.org/doi/10.1145/3173574.3173718`) традиционно отдаёт 403
   прямым каналам, страница добыта через Exa. Использован **дословный реферат с числами** (97 % оптимума, +5 п.п.),
   методических деталей эксперимента не видел.
3. **Semantic Scholar не использовался** — 429 без ключа (см. таблицу каналов); не понадобился.
4. **Эксперимента на живых пользователях продукта нет и быть не может до запуска** — все выводы п. 4 перенесены
   из транспортной и метеорологической областей. Перенос обоснован (те же когнитивные механизмы, тот же тип решения
   «действовать сейчас или подождать»), но это перенос, а не замер на нашей аудитории.
5. **Оптимальная форма замены не выбрана** — п. 5.3 даёт пять кандидатов с проверяемыми критериями, но выбор
   и приоритет — решение владельца в синтезе, не моё.

### Стенды и файлы

- `g45/p_valid.py` → `p_valid.out` — покрытие по горизонтам, PIT, CRPS, ширина; CANON/NORM/CONF, T=6 и T=12.
- `g45/p_patho.py` → `p_patho.out` — схлопывание коридора в нуле, зависимость ширины от B0, выдуманная история,
  избыточность Монте-Карло.
- `g45/p_alt.py` → `p_alt.out` — надёжность вероятности «уйти в минус», Brier, reliability по корзинам.
- Генератор портретов — `g45/gen43.py` (копия стенда Г43), загрузчик путей — `g45/sav_boot.py`.
- PDF Банка Англии: `g45/the-inflation-report-projections-understanding-the-fan-chart.pdf` (+ `.txt`),
  `g45/assessing-the-mpcs-fan-charts.pdf` (+ `.txt`).
- Каталог стенда: `/private/tmp/claude-501/-Users-vasyaevdokimov-repos-personal-finance-dss/f953390f-3de4-47af-96f5-3b071a88d028/scratchpad/g45/`.

Код продукта, канон `docs/math_model.md`, тесты, CHANGELOG, VERSION, WATCHLOG и GAP_QUEUE в ходе Г45 **не изменялись**.
