# Г43 — Статистические, вероятностные и прогнозные методы для ядра FINPILOT (17.09.2026)

> Постановка: `docs/research/queue/GAP_QUEUE.md`, раздел «Г43» (9 пунктов + карта аппарата).
> Вход (не переоткрывается): Г40 `math_core_audit_2026-09-17.md` п.5; Г41 `math_frameworks_alternatives_2026-09-17.md` рамки 3, 6;
> Г39 `math_core_verification_plan_2026-09-17.md` п.4–5; темы 32/Г6 `key_rate_history_forecastability_2026-09-10.md`,
> `macro_in_forecast_2026-09-10.md`; Г31.5 (ING Kijk Vooruit: дата по 4 последним списаниям, сумма по 5, горизонт 35 дней).
> Код, к которому относятся выводы: `app/core/forecast.py` (`ses_forecast`, `holt_forecast`, `choose_point_forecast`,
> `monte_carlo_intervals`, `build_history_from_current`, `detect_trend`), `app/services/forecasting.py`
> (`build_monthly_history`, `forecast_indicators`). Код продукта, `tests/`, канон — не правились.
> Скрипты и выводы — `scratchpad/g43/`, дословно ниже. Венв стенда: `scratchpad/g43/venv` (numpy, scipy, statsmodels,
> pandas, ruptures, mapie, lifelines) + `sys.path` проекта через `g39/sav_boot.py`.

**Состояние каналов (17.09.2026, `curl -skL`, код HTTP):** Semantic Scholar `search/bulk` 200 · OpenAlex 200 · Crossref 200 ·
EuropePMC 200 · `r.jina.ai` (без UA) 200 · otexts.com/fpp3 200 · Unpaywall (`email=research@example.org`) 200 ·
ЦБ `DailyInfo.asmx` 200 · arXiv API 200 · Exa (`mcp__exa__web_search_exa`) — работает (выдача по M4).

**Процесс.** Классификация — breadth-first (9 независимых пунктов), но ответ по каждому держится на одном и том же стенде
(короткие ряды одного человека), поэтому стенд строится один раз вахтой. Подагентов — см. ИТОГ.

**Как устроен прогноз сейчас (прочитано в коде, чтобы все пункты ссылались на одно).**
`forecast_indicators` берёт помесячные истории дохода/расхода/платежей из `build_monthly_history`; при < 2 точках
подставляет `build_history_from_current` (6 синтетических точек с шумом 5 %, фиксированные сиды 1/2/3);
`choose_point_forecast` → демпфированный Holt (α 0,4, β 0,3, φ 0,9 — константы) при ≥ 3 точках, иначе SES α 0,3;
баланс копится `Bt = Bt−1·(1+r_m) + (CF − P)`, `Rt = Bt + CF − P` (поток второй раз — Г40); коридор —
`monte_carlo_intervals`: нормальный шум вокруг точки с σ = 5 %·√(1+0,5h), **одинаковый для всех людей и не зависящий
от истории**, p10/p90 из 1000 выборок с `seed=42`. `detect_trend` — порог ±5 % от текущего Rt.

---

## Пункт 1. Прогноз денежного потока одного человека: чем предсказывать на 3–12 месяцах

**Аналогия.** Прогноз по короткой истории — как угадывать завтрашнюю температуру по трём дням наблюдений. Сложная модель
«видит» в трёх числах тренд и сезон, которых там нет; простое среднее ничего не выдумывает и поэтому ошибается меньше.

**Что предсказываем у нас.** Четыре разных вещи, и методы для них разные:
(а) **регулярный доход** (зарплата) — ровный ряд + календарные всплески (13-я зарплата, квартальная премия);
(б) **нерегулярный доход** (фриланс) — ряд с нулевыми месяцами, т. е. **прерывистый** (intermittent) ряд;
(в) **обязательные траты и платежи** — почти детерминированы, их лучше не прогнозировать, а **брать из графиков**
(кредитный график, подписки), как делает ING Kijk Vooruit (Г31.5);
(г) **переменные траты** — шум + редкие крупные покупки (тоже частично прерывистый ряд).

**Литература (дословно).**
- Hyndman & Athanasopoulos, *Forecasting: Principles and Practice* (3 ed.), §13.7 «Very long and very short time series»,
  https://otexts.com/fpp3/long-short-ts.html — `curl -skL` **HTTP 200**, 44 751 байт, 17.09.2026 (через `r.jina.ai` страница
  вернулась пустой, 332 байта — взят прямой канал):
  > «The only theoretical limit is that we need more observations than there are parameters in our forecasting model.
  > However, in practice, we usually need substantially more observations than that.»
  > «What tends to happen with short series is that the AICc suggests simple models because anything with more than one
  > or two parameters will produce poor forecasts due to the estimation error.»
- Там же, §13.2 (Croston), https://otexts.com/fpp3/counts.html — `r.jina.ai` **HTTP 200**, 6 724 байта:
  > «There are no algebraic results allowing us to compute prediction intervals for this method, because the method does
  > not correspond to any statistical model (Shenstone & Hyndman, 2005). Forecasts obtained from Croston's method are also
  > known to be biased (Syntetos & Boylan, 2001).»
  > «He would simply use α_a = α_q = 0.1, and set a_0 and q_0 to be equal to the first observation in each of the series.»
- Makridakis, Spiliotis, Assimakopoulos, «The M4 Competition: Results, findings, conclusion and way forward» / итоговая статья
  IJF 36(1):54–74, 2020, DOI 10.1016/j.ijforecast.2019.04.014 (Crossref 200). Постпринт Бата
  https://purehost.bath.ac.uk/ws/portalfiles/portal/192035784/IJF_2019_M4_Conclusions_post_print_.pdf (через Exa, 17.09.2026):
  > «this study found that the Mean Absolute Percentage Error (MAPE) of Naïve 2 was, on average, 1.4% more accurate than
  > that of the Box Jenkins methodology to ARIMA models, while Single Exponential Smoothing (SES) was correspondingly 2.61%
  > more accurate.» (о Makridakis & Hibon 1979)
  > «Out Of the 17 most accurate methods, 12 were "combinations" of mostly statistical approaches.» · «The six pure ML
  > methods performed poorly, with none of them being more accurate than the combination benchmark and only one being more
  > accurate than Naïve2.» (аннотация, https://pure.unic.ac.cy/en/publications/the-m4-competition-results-findings-conclusion-and-way-forward/)
  **Оговорка применимости:** ряды M4 — десятки и сотни точек (годовые ≥ 13, месячные ≥ 42); «весна» сложных методов M4 к
  нашим 3–12 точкам не переносится. Переносится только вывод «комбинации и простые методы — сильный ориентир».
- M5: Makridakis et al., «M5 accuracy competition: Results, findings, and conclusions», IJF 38(4):1346–1364, 2022,
  DOI 10.1016/j.ijforecast.2021.11.013 (Crossref 200). Выигрыш ML в M5 держится на **тысячах связанных рядов** (обучение
  «поперёк» товаров) — у нас это аналог «поперёк людей», т. е. профилирование (см. п. 6). Полный текст не открывался — в
  ЗАДОЛЖЕННОСТЬ.
- Croston (1972), Operational Research Quarterly 23(3):289, DOI 10.2307/3007885; Syntetos & Boylan (2005), IJF 21(2):303–314,
  DOI 10.1016/j.ijforecast.2004.10.001 (поправка SBA ×(1−α/2)); Teunter, Syntetos & Babai (2011), EJOR 214(3):606–615,
  DOI 10.1016/j.ejor.2011.05.018 (TSB — сглаживает вероятность «месяц непустой») — все реквизиты Crossref **HTTP 200**.

**Стенд (`g43/gen43.py`, `g43/p1_point.py`).** Шесть типов рядов (зарплата с премиями; закон шума ADR-015 из
`tools/portrait_testing/generator.py::generate_with_income_history`; фриланс с 5–30 % пустых месяцев; тренд +2 %/мес;
сдвиг уровня ×0,6 или ×1,3 в случайный месяц; траты с крупными покупками и декабрём), по 300 портретов на тип, история
T = 3, 6, 12 месяцев, прогноз на 6 месяцев вперёд из одной точки (как в продукте). Ошибка в долях среднего дохода истории.
`e1` — ошибка первого месяца; `e6` — ошибка **суммы за 6 месяцев**, делённая на 6 (именно сумма двигает баланс).
`CANON_holt` — это **сама функция продукта** `app/core/forecast.py::choose_point_forecast`. Дефект Д-01 генератора
(срок цели как `date`) стенд не затрагивает: цели здесь не используются, ряды строятся своим генератором.

```python
"""G43 synthetic monthly series of one person + forecasting methods. Kinds mirror what the product meets:
salary (3 % noise + December/quarterly bonus), adr015 (the project's PortraitGenerator.generate_with_income_history
volatility law: uniform +-v, v from {0,0,0,.1,.2,.4,.6,.9}), freelance (zero months + lognormal), trend (+2 %/month),
shift (level x0.6 or x1.3 at a random month, possibly inside the forecast window), expense (10 % noise + lumpy
purchases p=.15 + December +25 %). Real user data is not used (152-FZ)."""
import sav_boot  # noqa
import math, warnings
import numpy as np
from app.core.forecast import choose_point_forecast, ses_forecast

warnings.filterwarnings("ignore")
KINDS = ("salary", "adr015", "freelance", "trend", "shift", "expense")
H = 6


def gen(kind, rng, n):
    base = rng.uniform(40e3, 250e3)
    m0 = rng.integers(0, 12)
    t = np.arange(n)
    dec = ((m0 + t) % 12) == 11
    if kind == "salary":
        y = base * (1 + rng.normal(0, .03, n))
        y = y + dec * base * rng.uniform(.5, 1.5)
        if rng.random() < .3:
            y = y + (((m0 + t) % 3) == 2) * base * .3
    elif kind == "adr015":
        v = rng.choice([0, 0, 0, .1, .2, .4, .6, .9])
        y = np.maximum(0, base * (1 + rng.uniform(-v, v, n)))
    elif kind == "freelance":
        p0 = rng.uniform(.05, .3)
        y = np.where(rng.random(n) < p0, 0.0, base * rng.lognormal(-.08, .4, n))
    elif kind == "trend":
        y = base * 1.02 ** t * (1 + rng.normal(0, .05, n))
    elif kind == "shift":
        cp = rng.integers(2, n)
        f = rng.choice([.6, 1.3])
        y = base * (1 + rng.normal(0, .04, n)) * np.where(t >= cp, f, 1.0)
    elif kind == "expense":
        y = base * (1 + rng.normal(0, .10, n)) + (rng.random(n) < .15) * base * rng.uniform(.5, 2, n)
        y = y * np.where(dec, 1.25, 1.0)
    return np.maximum(y, 0.0)


# ---------- point methods: hist (np.array) -> np.array(H) ----------
def m_naive(h): return np.repeat(h[-1], H)
def m_mean(h): return np.repeat(h.mean(), H)
def m_median(h): return np.repeat(np.median(h), H)
def m_ses03(h): return np.array(ses_forecast(list(h), horizon=H))
def m_canon(h): return np.array(choose_point_forecast(list(h), horizon=H))
def m_ing(h): return np.repeat(np.median(h[-5:]), H)  # ING Kijk Vooruit style: last 5 occurrences


def m_ses_fit(h):
    from statsmodels.tsa.holtwinters import SimpleExpSmoothing
    if len(h) < 3 or np.ptp(h) == 0:
        return m_mean(h)
    return np.asarray(SimpleExpSmoothing(h, initialization_method="estimated").fit().forecast(H))


def m_damped_fit(h):
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    if len(h) < 5 or np.ptp(h) == 0:
        return m_ses_fit(h)
    r = ExponentialSmoothing(h, trend="add", damped_trend=True, initialization_method="estimated").fit()
    return np.maximum(np.asarray(r.forecast(H)), 0)


def m_theta(h):
    from statsmodels.tsa.forecasting.theta import ThetaModel
    if len(h) < 4 or np.ptp(h) == 0:
        return m_mean(h)
    return np.maximum(np.asarray(ThetaModel(h, period=1, deseasonalize=False).fit().forecast(H)), 0)


def m_arima(h):
    from statsmodels.tsa.arima.model import ARIMA
    if len(h) < 5 or np.ptp(h) == 0:
        return m_mean(h)
    best, bf = None, None
    for order, tr in (((0, 0, 0), "c"), ((1, 0, 0), "c"), ((0, 1, 1), "n")):
        try:
            r = ARIMA(h, order=order, trend=tr).fit()
            k = r.df_model + 1; n = len(h)
            aicc = r.aic + (2 * k * (k + 1) / (n - k - 1) if n - k - 1 > 0 else 1e9)
            if best is None or aicc < best:
                best, bf = aicc, np.asarray(r.forecast(H))
        except Exception:
            pass
    return np.maximum(bf, 0) if bf is not None else m_mean(h)


def m_comb(h):  # M4 "Comb" benchmark idea: SES + Holt + damped, equal weights (here: fitted SES, damped, naive-free)
    return (m_ses_fit(h) + m_damped_fit(h) + m_mean(h)) / 3


def _croston(h, a=.1, mode="croston"):
    nz = np.flatnonzero(h > 0)
    if len(nz) == 0:
        return np.zeros(H)
    if mode == "tsb":
        p = (h > 0).mean(); z = h[nz].mean()
        for x in h:
            p = p + a * ((x > 0) - p)
            if x > 0:
                z = z + a * (x - z)
        return np.repeat(p * z, H)
    z = h[nz[0]]; q = nz[0] + 1.0; last = nz[0]
    for i in nz[1:]:
        z = z + a * (h[i] - z); q = q + a * ((i - last) - q); last = i
    f = z / q
    if mode == "sba":
        f *= (1 - a / 2)
    return np.repeat(f, H)


def m_croston(h): return _croston(h)
def m_sba(h): return _croston(h, mode="sba")
def m_tsb(h): return _croston(h, mode="tsb")


METHODS = {"naive": m_naive, "mean": m_mean, "median": m_median, "ing_med5": m_ing, "ses0.3": m_ses03,
           "CANON_holt": m_canon, "ses_fit": m_ses_fit, "damped_fit": m_damped_fit, "theta": m_theta,
           "arima_aicc": m_arima, "comb": m_comb, "croston": m_croston, "sba": m_sba, "tsb": m_tsb}
```

```python
"""G43 p.1: which point forecast wins on 3-12 months of one person's history. Single forecast origin per portrait
(as in the product: the person has T months now, we forecast the next 6). Errors scaled by the history mean.
e1 = |error of month 1|; e6 = |error of the 6-month SUM| / 6 (what drives the balance path)."""
import sys, time
import numpy as np
from gen43 import gen, KINDS, METHODS, H

N = int(sys.argv[1]) if len(sys.argv) > 1 else 300
rng = np.random.default_rng(43)
t0 = time.time()
for T in (3, 6, 12):
    print(f"\n######## history T={T} months, N={N} portraits per kind")
    print(f"{'kind':10}" + "".join(f"{k:>11}" for k in METHODS))
    agg = {k: [[], []] for k in METHODS}
    for kind in KINDS:
        e1 = {k: [] for k in METHODS}; e6 = {k: [] for k in METHODS}
        for _ in range(N):
            y = gen(kind, rng, T + H)
            h, fut = y[:T], y[T:]
            sc = h.mean() if h.mean() > 0 else 1.0
            for k, f in METHODS.items():
                p = f(h)
                e1[k].append(abs(p[0] - fut[0]) / sc)
                e6[k].append(abs(p.sum() - fut.sum()) / 6 / sc)
        for k in METHODS:
            agg[k][0] += e1[k]; agg[k][1] += e6[k]
        print(f"{kind+' e1':10}" + "".join(f"{np.mean(e1[k]):11.3f}" for k in METHODS))
        print(f"{kind+' e6':10}" + "".join(f"{np.mean(e6[k]):11.3f}" for k in METHODS))
    print(f"{'ALL e1':10}" + "".join(f"{np.mean(agg[k][0]):11.3f}" for k in METHODS))
    print(f"{'ALL e6':10}" + "".join(f"{np.mean(agg[k][1]):11.3f}" for k in METHODS))
    best = min(METHODS, key=lambda k: np.mean(agg[k][1]))
    c = np.mean(agg["CANON_holt"][1]); b = np.mean(agg[best][1])
    print(f"best on e6: {best} {b:.3f}; canon {c:.3f}; canon excess {100*(c/b-1):.0f} %")
print(f"\nelapsed {time.time()-t0:.0f}s")
```

Вывод (дословно; предупреждения statsmodels о сходимости вычищены `grep`, сырой вывод — `g43/p1_point.out`):

```
######## history T=3 months, N=300 portraits per kind
kind            naive       mean     median   ing_med5     ses0.3 CANON_holt    ses_fit damped_fit      theta arima_aicc       comb    croston        sba        tsb
salary e1       0.231      0.192      0.132      0.132      0.184      0.417      0.232      0.232      0.192      0.192      0.217      0.170      0.173      0.193
salary e6       0.184      0.151      0.105      0.105      0.151      0.507      0.180      0.180      0.151      0.151      0.167      0.153      0.170      0.151
adr015 e1       0.235      0.184      0.202      0.202      0.181      0.330      0.205      0.205      0.184      0.184      0.195      0.185      0.196      0.184
adr015 e6       0.165      0.109      0.140      0.140      0.114      0.467      0.130      0.130      0.109      0.109      0.118      0.146      0.158      0.109
freelance e1      0.819      0.667      0.691      0.691      0.693      1.044      0.746      0.746      0.667      0.667      0.711      0.718      0.709      0.667
freelance e6      0.676      0.453      0.506      0.506      0.470      1.522      0.576      0.576      0.453      0.453      0.526      0.468      0.455      0.454
trend e1        0.059      0.056      0.057      0.057      0.059      0.091      0.055      0.055      0.056      0.056      0.054      0.069      0.108      0.056
trend e6        0.082      0.096      0.095      0.095      0.100      0.153      0.087      0.087      0.096      0.096      0.088      0.111      0.160      0.095
shift e1        0.079      0.096      0.110      0.110      0.098      0.117      0.090      0.090      0.096      0.096      0.090      0.109      0.116      0.096
shift e6        0.185      0.207      0.220      0.220      0.208      0.218      0.197      0.197      0.207      0.207      0.200      0.216      0.212      0.207
expense e1      0.322      0.288      0.254      0.254      0.294      0.542      0.316      0.316      0.288      0.288      0.302      0.316      0.309      0.288
expense e6      0.280      0.211      0.206      0.206      0.212      0.766      0.250      0.250      0.211      0.211      0.231      0.240      0.249      0.211
ALL e1          0.291      0.247      0.241      0.241      0.252      0.423      0.274      0.274      0.247      0.247      0.261      0.261      0.268      0.247
ALL e6          0.262      0.205      0.212      0.212      0.209      0.606      0.237      0.237      0.205      0.205      0.222      0.222      0.234      0.205
best on e6: mean 0.205; canon 0.606; canon excess 196 %
######## history T=6 months, N=300 portraits per kind
kind            naive       mean     median   ing_med5     ses0.3 CANON_holt    ses_fit damped_fit      theta arima_aicc       comb    croston        sba        tsb
salary e1       0.234      0.179      0.126      0.129      0.184      0.335      0.197      0.295      0.221      0.257      0.218      0.162      0.151      0.181
salary e6       0.189      0.145      0.101      0.103      0.149      0.314      0.163      0.318      0.234      0.211      0.198      0.141      0.147      0.146
adr015 e1       0.175      0.137      0.146      0.157      0.139      0.189      0.146      0.167      0.156      0.160      0.144      0.144      0.168      0.137
adr015 e6       0.144      0.080      0.095      0.103      0.084      0.186      0.096      0.167      0.144      0.125      0.101      0.101      0.123      0.080
freelance e1      0.755      0.583      0.607      0.637      0.592      0.795      0.619      0.730      0.679      0.651      0.618      0.611      0.602      0.584
freelance e6      0.599      0.356      0.374      0.423      0.360      0.764      0.407      0.698      0.579      0.470      0.441      0.382      0.375      0.356
trend e1        0.062      0.079      0.080      0.074      0.072      0.065      0.071      0.061      0.060      0.070      0.065      0.098      0.144      0.077
trend e6        0.082      0.129      0.129      0.121      0.118      0.077      0.104      0.073      0.069      0.092      0.094      0.150      0.199      0.126
shift e1        0.078      0.135      0.140      0.127      0.117      0.101      0.092      0.103      0.092      0.085      0.093      0.163      0.172      0.131
shift e6        0.141      0.207      0.211      0.196      0.188      0.169      0.157      0.216      0.183      0.149      0.153      0.233      0.232      0.202
expense e1      0.375      0.304      0.250      0.252      0.311      0.454      0.327      0.439      0.370      0.369      0.342      0.323      0.312      0.305
expense e6      0.284      0.185      0.172      0.173      0.196      0.406      0.210      0.444      0.333      0.262      0.251      0.233      0.236      0.185
ALL e1          0.280      0.236      0.225      0.229      0.236      0.323      0.242      0.299      0.263      0.265      0.247      0.250      0.258      0.236
ALL e6          0.240      0.184      0.180      0.186      0.182      0.319      0.189      0.319      0.257      0.218      0.206      0.207      0.219      0.183
best on e6: median 0.180; canon 0.319; canon excess 77 %
######## history T=12 months, N=300 portraits per kind
kind            naive       mean     median   ing_med5     ses0.3 CANON_holt    ses_fit damped_fit      theta arima_aicc       comb    croston        sba        tsb
salary e1       0.272      0.184      0.155      0.159      0.209      0.238      0.203      0.276      0.226      0.259      0.216      0.139      0.125      0.191
salary e6       0.201      0.074      0.105      0.108      0.136      0.223      0.093      0.296      0.214      0.190      0.154      0.097      0.090      0.091
adr015 e1       0.194      0.144      0.151      0.162      0.149      0.163      0.150      0.161      0.159      0.162      0.149      0.141      0.159      0.144
adr015 e6       0.146      0.068      0.081      0.105      0.077      0.131      0.078      0.103      0.102      0.106      0.075      0.075      0.098      0.068
freelance e1      0.773      0.613      0.592      0.642      0.629      0.675      0.619      0.664      0.664      0.646      0.620      0.625      0.624      0.613
freelance e6      0.585      0.282      0.284      0.356      0.327      0.511      0.314      0.409      0.413      0.344      0.316      0.313      0.309      0.283
trend e1        0.063      0.136      0.139      0.074      0.077      0.053      0.062      0.054      0.057      0.064      0.071      0.149      0.198      0.119
trend e6        0.080      0.192      0.195      0.123      0.127      0.056      0.091      0.052      0.060      0.082      0.105      0.204      0.254      0.174
shift e1        0.063      0.160      0.166      0.093      0.090      0.077      0.070      0.083      0.073      0.065      0.078      0.169      0.178      0.140
shift e6        0.099      0.207      0.211      0.132      0.132      0.138      0.112      0.173      0.134      0.102      0.111      0.216      0.221      0.187
expense e1      0.366      0.308      0.269      0.287      0.315      0.350      0.308      0.347      0.323      0.327      0.313      0.308      0.295      0.308
expense e6      0.284      0.169      0.179      0.190      0.194      0.301      0.177      0.274      0.245      0.215      0.195      0.173      0.179      0.174
ALL e1          0.288      0.258      0.245      0.236      0.245      0.259      0.236      0.264      0.250      0.254      0.241      0.255      0.263      0.253
ALL e6          0.233      0.165      0.176      0.169      0.165      0.227      0.144      0.218      0.194      0.173      0.159      0.180      0.192      0.163
best on e6: ses_fit 0.144; canon 0.227; canon excess 57 %
elapsed 415s
```

**Что показывает число.**
1. 🔴 **Продуктовый прогноз (демпфированный Holt с константами) — худший из 14 методов на всех трёх длинах истории.**
   Ошибка суммы за полгода: T=3 — **0,606** против 0,205 у среднего (**в 3 раза хуже**); T=6 — 0,319 против 0,180 у медианы
   (+77 %); T=12 — 0,227 против 0,144 у SES с подобранным α (+57 %). На T=3 Holt инициализирует тренд разностью первых двух
   точек (`holt_forecast`: `trend = history[1] - history[0]`) — одна случайная разница становится «трендом» на полгода.
   Выигрывает Holt только там, где тренд есть по построению (тип `trend`, T=12: 0,056 против 0,192 у среднего) — но это
   один тип из шести, и там же простое SES α=0,3 даёт 0,127, а подобранный демпфированный — 0,052.
2. **Канон §15 описывает SES α=0,3 — и он почти лучший**: 0,209 / 0,182 / 0,165 (в пределах 2–15 % от лучшего на каждой
   длине). То есть код ушёл от канона в худшую сторону (Г40 № 27 — расхождение уже известно; здесь — его цена).
3. **Подбор параметров по данным (ETS/ARIMA по AICc, Theta) на 3–6 точках не помогает**, на 12 точках SES с подобранным α —
   лучший в среднем (0,144). Демпфированный Holt с подбором — плох везде, кроме рядов с настоящим трендом.
4. **Медиана** выигрывает на зарплате с премиями (0,101–0,105): премия — выброс, медиана его не тянет. Но медиана
   **недооценивает сумму за год**, если премия регулярна — премию надо моделировать **календарём** (известное событие), а
   не статистикой: при 12 месяцах истории декабрьский всплеск виден ровно один раз, сезонность оценить нельзя (Г40 п. 5.2).
5. **Кростон/SBA/TSB на фрилансе не выигрывают у простого среднего** (e6 0,356–0,382 против 0,356 при T=6; 0,283–0,313
   против 0,282 при T=12). Причина: для суммы за полгода среднее по всем месяцам, **включая нули**, уже несмещённая оценка;
   Кростон нужен, когда важен вопрос «когда придёт следующий платёж», а не «сколько за полгода». Для нас полезна не точка,
   а **доля пустых месяцев как отдельный параметр** — это Г41 (рамка 6) и п. 2 ниже (интервал).
6. **Сдвиг уровня (потеря/смена работы)** — единственный тип, где «последнее значение» (naive) лучше среднего
   (0,099 против 0,207 при T=12): среднее смешивает «до» и «после». Это вход п. 3 (обнаружение изменений).

**Цена и корзина.**
| Что | Корзина | Почему |
|---|---|---|
| Заменить Holt на SES α=0,3 (как в каноне) или на среднее/медиану по истории, без тренда | **сразу** | выигрыш 27–66 % ошибки суммы за 6 мес. (0,227→0,165; 0,319→0,182; 0,606→0,209); правка одной функции, канон уже так написан |
| Тренд — только если он «доказан» (п. 8: значимость наклона при ≥ 9–12 точках) | до запуска | единственный тип, где тренд помогает; без проверки значимости тренд выдумывается |
| Обязательные траты/платежи — из графиков, не из статистики | до запуска | то же у ING; прогнозировать известное — ошибка класса |
| Календарные события (13-я, отпуск, декабрь) — как известные разовые, а не как сезонность | до запуска | 12 точек не дают сезонность; человек знает про свою премию |
| Подбор параметров ETS/ARIMA/Theta по AICc | потом (от 12+ мес.) | на 3–6 точках не выигрывает (fpp3 §13.7 — то же) |
| Кростон/SBA/TSB | не нужно для суммы; **доля пустых месяцев** — нужно (п. 2) | среднее с нулями уже несмещённое |
| Иерархический прогноз «категория → итог» | не нужно | на 3–12 точках на категорию данных ещё меньше; итог прогнозируется лучше суммы шумных частей; согласование иерархии (MinT) требует оценки ковариаций, что на таких длинах невозможно — вывод вахты, отдельным числом не проверялся (ЗАДОЛЖЕННОСТЬ) |
| Байесовские структурные ряды (BSTS) | потом | ценны только с априором «похожих людей» (п. 6) |

---

## Пункт 2. Вероятностный прогноз вместо точки: интервалы, конформное предсказание, калибровка, правильные оценочные правила

**Аналогия.** Прогноз погоды «70 % дождя» честен, если из всех дней, когда синоптик говорил «70 %», дождь был примерно в
семи из десяти. Это и есть **калибровка**. Наш коридор «80 %» честен, если реальный баланс попадает в него в 8 случаях из 10.
Второе требование — **резкость** (sharpness): коридор «от минус миллиона до плюс миллиона» всегда калиброван и бесполезен.

**Термины одной строкой.**
- *Квантиль 10 %* — число, ниже которого окажется 10 % исходов. Коридор p10–p90 — «80 % интервал».
- *Покрытие (coverage)* — доля случаев, когда правда попала в коридор. Должно быть ≈ заявленному.
- *Interval score* (Gneiting & Raftery 2007, формула 43) — «штраф» интервала: `ширина + (2/α)·недолёт + (2/α)·перелёт`,
  α = 0,2 для 80 %-коридора. Меньше — лучше. Одновременно наказывает и за ширину, и за промах; честнее, чем одно покрытие.
- *Pinball loss* — то же для одного квантиля; *CRPS* — то же для всего распределения сразу (усреднение pinball по всем квантилям).
- *Конформное предсказание* — берём пачку прошлых случаев, меряем, насколько сильно прогноз промахивался, и ставим ширину
  коридора ровно такой, чтобы 80 % промахов в неё влезали. Никаких допущений о нормальности.

**Литература (дословно).**
- Gneiting & Raftery, «Strictly Proper Scoring Rules, Prediction, and Estimation», JASA 102(477):359–378, 2007,
  DOI 10.1198/016214506000001437. OpenAlex: закрыт (`oa_status: closed`), Unpaywall (`email=research@example.org`) — `is_oa: False`;
  **авторская копия** https://sites.stat.washington.edu/raftery/Research/PDF/Gneiting2007jasa.pdf — `curl -skL` **HTTP 200**, 556 804 байта,
  `pdftotext`, 17.09.2026:
  > «we contended that the goal of probabilistic forecasting is to maximize the sharpness of the predictive distributions
  > subject to calibration.»
  > «propose the intuitively appealing interval score as a utility function in interval estimation that addresses width as
  > well as coverage»
  > §6.2: `S_int(l,u;x) = (u − l) + (2/α)(l − x)1{x < l} + (2/α)(x − u)1{x > u}` (формула 43, «negatively oriented interval score»).
- Angelopoulos & Bates, «A Gentle Introduction to Conformal Prediction and Distribution-Free Uncertainty Quantification»,
  arXiv:2107.07511v6 — https://arxiv.org/pdf/2107.07511v6 **HTTP 200**, 5 360 733 байта, `pdftotext`:
  > «we call this property marginal coverage, since the probability is marginal (averaged) over the randomness in the
  > calibration and test points.»
  > «This is a stronger property than the marginal coverage property in (1) that conformal prediction is guaranteed to
  > achieve—indeed, in the most general case, conditional coverage is impossible to achieve [14].»
  > (о временных рядах) «Note that these data points are not exchangeable or i.i.d.; adjacent data points …» — для рядов
  > авторы отсылают к взвешенному/адаптивному варианту (§4.6; Gibbs & Candès, arXiv:2106.00170).

**Стенд (`g43/p2_interval.py`).** Проверяется **сама функция продукта** `app/services/forecasting.py::forecast_indicators`:
её коридор `Rt_p10…Rt_p90` против «правды», посчитанной по той же формуле канона (`Rt = Bt + CF − P`, r_bench = 0), так что
проверяется только интервал, а не дефект «поток дважды». Альтернативы строят коридор для баланса `B_h`:
NORM (своё среднее и разброс чистого потока, квантиль Стьюдента, поправка на неточность оценки `√(1+h/n)`),
BOOT (перетасовка собственных месяцев, 2000 путей — сохраняет нули и крупные покупки),
CONF (конформное: множитель ширины откалиброван на **других** 400 портретах смешанных типов, промах нормирован на
собственный разброс человека — т. е. «насколько широк коридор» знают из популяции, «в каких единицах» — из человека).

```python
"""G43 p.2: does the product's 80 % corridor (app/services/forecasting.py::forecast_indicators -> Rt_p10..Rt_p90) cover
the truth 80 % of the time? Alternatives for the balance path B_h = B0 + sum of net flows (income - expense - P):
 NORM  : own mean and sd of net flow, t-quantile, sd*sqrt(h)*sqrt(1+h/n) (parameter uncertainty)
 BOOT  : resample own months iid (keeps zero months and lumpy purchases), 2000 paths
 CONF  : split-conformal on a population of calibration portraits, score normalised by own sd*sqrt(h) (scale-free),
         applied to NORM's centre. Calibration and test portraits are different draws.
Truth for canon uses the canon's own formula (Rt = Bt + CF - P, r_bench = 0), so only the interval is tested.
Interval score (Gneiting & Raftery 2007, eq. 43): width + (2/a)(l-y)+ + (2/a)(y-u)+, a = 0.2; scaled by mean income."""
import sys
import numpy as np
from scipy import stats
from gen43 import gen
from app.services.forecasting import forecast_indicators

H = 6; A = 0.2
N = int(sys.argv[1]) if len(sys.argv) > 1 else 400
KINDS = ("salary", "adr015", "freelance", "trend", "shift")
rng = np.random.default_rng(4302)


def person(kind, T):
    inc = gen(kind, rng, T + H)
    exp_ = gen("expense", rng, T + H)
    exp_ = exp_ / exp_[:T].mean() * inc[:T].mean() * rng.uniform(.4, .7)
    P = inc[:T].mean() * rng.uniform(0, .25)
    B0 = inc[:T].mean() * rng.choice([0.0, 1.0, 6.0])
    return inc, exp_, P, B0


def centre_sd(net):
    return net.mean(), max(net.std(ddof=1), 1e-9)


def iscore(l, u, y, sc):
    return ((u - l) + 2 / A * max(l - y, 0) + 2 / A * max(y - u, 0)) / sc


def run(T):
    # calibration of CONF on separate portraits (mixed kinds, like a real user base)
    scores = {h: [] for h in range(1, H + 1)}
    for _ in range(N):
        kind = KINDS[rng.integers(len(KINDS))]
        inc, exp_, P, B0 = person(kind, T)
        net = inc - exp_ - P
        m, s = centre_sd(net[:T])
        cum = np.cumsum(net[T:])
        for h in range(1, H + 1):
            scores[h].append(abs(cum[h - 1] - m * h) / (s * np.sqrt(h)))
    qh = {h: np.quantile(scores[h], min(1, (1 - A) * (1 + 1 / N))) for h in scores}
    print(f"\n######## T={T}  conformal multipliers q(h): " + " ".join(f"{h}:{qh[h]:.2f}" for h in qh)
          + f"  (normal z would be {stats.norm.ppf(1-A/2):.2f})")
    print(f"{'kind':10}{'h':>3} | {'CANON cov':>9} {'IS':>6} | {'NORM cov':>8} {'IS':>6} | {'BOOT cov':>8} {'IS':>6} | {'CONF cov':>8} {'IS':>6}")
    for kind in KINDS + ("B0=0 only",):
        acc = {k: {h: [[], []] for h in (1, 6)} for k in ("canon", "norm", "boot", "conf")}
        for _ in range(N):
            kk = kind if kind in KINDS else KINDS[rng.integers(len(KINDS))]
            inc, exp_, P, B0 = person(kk, T)
            if kind not in KINDS:
                B0 = 0.0
            net = inc - exp_ - P
            sc = inc[:T].mean()
            fc = forecast_indicators(balance=B0, rt=B0, lt=0, dt=0, income_total=inc[T - 1], expense_total=exp_[T - 1],
                                     obligation_payments=P, horizon=H, income_history=list(inc[:T]),
                                     expense_history=list(exp_[:T]), obligation_history=[P] * T, r_bench=0.0)
            B = B0 + np.cumsum(net[T:])
            Rt_true = B + net[T:]
            m, s = centre_sd(net[:T])
            boot = B0 + np.cumsum(rng.choice(net[:T], size=(2000, H)), axis=1)
            for h in (1, 6):
                f = fc["forecast"][h - 1]
                l, u = f["Rt_p10"], f["Rt_p90"]; y = Rt_true[h - 1]
                acc["canon"][h][0].append(l <= y <= u); acc["canon"][h][1].append(iscore(l, u, y, sc))
                y = B[h - 1]
                half = stats.t.ppf(1 - A / 2, T - 1) * s * np.sqrt(h) * np.sqrt(1 + h / T)
                l, u = B0 + m * h - half, B0 + m * h + half
                acc["norm"][h][0].append(l <= y <= u); acc["norm"][h][1].append(iscore(l, u, y, sc))
                l, u = np.quantile(boot[:, h - 1], [A / 2, 1 - A / 2])
                acc["boot"][h][0].append(l <= y <= u); acc["boot"][h][1].append(iscore(l, u, y, sc))
                half = qh[h] * s * np.sqrt(h)
                l, u = B0 + m * h - half, B0 + m * h + half
                acc["conf"][h][0].append(l <= y <= u); acc["conf"][h][1].append(iscore(l, u, y, sc))
        for h in (1, 6):
            row = " | ".join(f"{np.mean(acc[k][h][0]):9.1%} {np.mean(acc[k][h][1]):6.2f}" for k in ("canon", "norm", "boot", "conf"))
            print(f"{kind:10}{h:>3} | {row}")


for T in (6, 12):
    run(T)
```

Вывод (дословно, `g43/p2_interval.out`):

```

######## T=6  conformal multipliers q(h): 1:1.58 2:2.20 3:2.52 4:2.59 5:3.00 6:3.15  (normal z would be 1.28)
kind        h | CANON cov     IS | NORM cov     IS | BOOT cov     IS | CONF cov     IS
salary      1 |     14.5%   8.53 |     77.8%   2.06 |     69.0%   2.24 |     77.8%   2.06
salary      6 |     13.2%  27.20 |     67.5%   5.15 |     39.5%   6.14 |     82.0%   5.68
adr015      1 |     23.8%   5.65 |     82.2%   1.38 |     72.2%   1.33 |     82.0%   1.37
adr015      6 |     16.5%  19.04 |     74.5%   4.81 |     49.8%   5.33 |     84.8%   5.36
freelance   1 |      7.8%  16.14 |     76.5%   3.25 |     70.8%   3.30 |     76.2%   3.25
freelance   6 |      8.8%  51.62 |     78.5%  10.69 |     54.2%  12.49 |     89.8%  12.06
trend       1 |     29.8%   3.66 |     75.8%   0.99 |     53.2%   1.05 |     75.8%   0.99
trend       6 |     25.8%  12.96 |     51.0%   3.93 |     23.2%   5.58 |     77.5%   3.76
shift       1 |     25.2%   4.40 |     74.2%   1.32 |     64.2%   1.28 |     74.0%   1.32
shift       6 |     17.0%  17.21 |     43.2%   7.66 |     20.0%   9.70 |     62.5%   6.85
B0=0 only   1 |      6.8%   8.34 |     83.5%   1.88 |     67.0%   1.90 |     83.2%   1.88
B0=0 only   6 |      8.5%  27.11 |     60.5%   6.22 |     35.2%   7.80 |     81.2%   6.45

######## T=12  conformal multipliers q(h): 1:1.36 2:1.69 3:1.86 4:1.98 5:2.20 6:2.57  (normal z would be 1.28)
kind        h | CANON cov     IS | NORM cov     IS | BOOT cov     IS | CONF cov     IS
salary      1 |     31.2%   5.01 |     84.8%   1.57 |     69.5%   1.64 |     84.0%   1.56
salary      6 |     18.8%  16.10 |     89.0%   3.40 |     77.0%   3.09 |     96.5%   4.61
adr015      1 |     29.0%   4.47 |     86.2%   1.20 |     69.2%   1.21 |     85.0%   1.18
adr015      6 |     23.0%  14.66 |     78.8%   3.48 |     61.3%   3.61 |     91.2%   4.19
freelance   1 |     10.2%  12.03 |     77.2%   2.81 |     67.2%   2.87 |     75.5%   2.81
freelance   6 |      8.8%  35.34 |     83.2%   7.94 |     68.2%   7.97 |     93.5%   9.49
trend       1 |     46.5%   3.08 |     73.8%   1.02 |     34.5%   1.29 |     69.5%   1.02
trend       6 |     43.5%   9.06 |     33.0%   5.68 |     19.0%   7.21 |     61.8%   4.24
shift       1 |     42.2%   2.96 |     80.0%   1.14 |     63.2%   1.19 |     78.2%   1.13
shift       6 |     23.2%  11.20 |     44.5%   6.86 |     30.0%   7.97 |     65.8%   5.87
B0=0 only   1 |     12.5%   6.70 |     76.2%   1.70 |     60.2%   1.81 |     74.5%   1.70
B0=0 only   6 |     14.8%  18.06 |     68.2%   5.10 |     53.5%   5.55 |     83.2%   5.51
```

**Что показывает число.**
1. 🔴 **Коридор продукта врёт в разы: заявлено 80 %, фактически 7–47 %** (T=6: 7,8–29,8 % на первом месяце, 8,5–25,8 % на
   шестом; T=12: 10–47 %). Штраф interval score в 3–5 раз выше любой альтернативы (например, фриланс T=6, h=6: **51,6** против
   10,7 у NORM). Причины видны прямо в коде `app/core/forecast.py::monte_carlo_intervals`:
   (а) ширина = **5 % от величины Rt**, а не от разброса дохода: у человека с нулевым балансом коридор почти нулевой
   (строка `B0=0 only`: покрытие **6,8 %** и 8,5 %), у человека с запасом 6 доходов — широкий, хотя будущее у них одинаково
   неопределённо; (б) 5 % одинаковы для зарплатника и фрилансера (у фрилансера реальный разброс месяца 40–60 %);
   (в) ширина растёт как `√(1+0,5h)` — медленнее, чем растёт неопределённость **суммы** потоков (`√h` и больше);
   (г) центр — смещённый Holt (п. 1). Monte-Carlo здесь не нужен вовсе: у нормального шума вокруг точки квантиль считается
   формулой (Г39 п. 4 — то же), и 1000 прогонов лишь добавляют шум ±0,054 σ.
2. **Простой нормальный коридор по собственному разбросу (NORM) на первом месяце уже почти честен** (74–86 %), но к шестому
   месяцу **сужается сильнее правды** там, где ряд не стационарен: тренд 33–51 %, сдвиг уровня 43–45 %.
3. **Бутстрэп собственных месяцев (BOOT) хуже нормального** (20–77 %) — на 6–12 точках он не видит хвостов (из шести чисел
   нельзя вытянуть месяц хуже худшего) и не знает о неточности своего среднего. На коротких рядах — **не нужен**.
4. **Конформный множитель (CONF) даёт честные 80 % «в среднем по людям» и при B0=0** (81,2 % при T=6, 83,2 % при T=12)
   и лучший или близкий к лучшему штраф на трендах и сдвигах. Но **по отдельным типам** покрытие гуляет 62–97 % — ровно то,
   что предупреждают Angelopoulos & Bates: гарантия **маргинальная** (в среднем по популяции), не для каждого человека.
   Числа множителя поучительны сами: на T=6 нужен множитель **3,15** на шестом месяце вместо нормальных 1,28·√6 ≈ 3,14 —
   совпадение случайное: он «доплачивает» за нестационарность и неточность оценки разброса по 6 точкам.
5. **Где взять калибровочную выборку в продукте.** До запуска — только синтетика (152-ФЗ, реальных данных нет). После
   запуска — собственная история человека «задним числом» (прогноз, сделанный 6 месяцев назад, против факта) и
   обезличенная популяционная статистика промахов (агрегат, без профилей) — граница с п. 6.

**Как проверять, что коридор не врёт (процедура, а не пожелание).**
1. Бэктест с «катящимся началом»: на каждой истории делаем прогноз из прошлого и сверяем с фактом.
2. Считаем **покрытие** по каждому горизонту 1…6 и **по типам людей** (зарплата/фриланс/сдвиг) — не только общее.
   Допуск: для 80 % при 400 портретах стандартная ошибка ≈ 2 п. п., поэтому «честно» = 76–84 %.
3. Считаем **interval score** (или pinball на p10/p50/p90, или CRPS) — сравнение методов только по нему, не по покрытию
   (широкий коридор всегда «покрывает»).
4. Строим **PIT-гистограмму** (в какой квантиль прогноза попал факт): у честного прогноза она ровная. U-образная — коридор
   узкий (наш случай), горб — слишком широкий.
5. Всё это — метаморфическая/свойственная проверка ядра в духе Г39 (там же место для теста).

**Цена и корзина.**
| Что | Корзина | Почему |
|---|---|---|
| Ширина коридора от **собственного разброса потока**, а не от величины Rt; рост как √h; квантиль Стьюдента | **сразу** | покрытие 7–47 % → 74–86 % на первом месяце; правка одной функции; MC не нужен |
| Конформный множитель по горизонту, откалиброванный на синтетике до запуска и на агрегатах после | до запуска | даёт 80 % «в среднем» на всех горизонтах, включая B0=0; нужна калибровочная выборка |
| Метрики: покрытие по горизонтам и типам + interval score / pinball + PIT — в стенд Г39 | до запуска | без них «диапазон» не проверяем |
| Адаптивное конформное (Gibbs & Candès) — поправка ширины по собственным промахам человека онлайн | потом | нужны 6+ собственных прогнозов с фактом |
| Бутстрэп собственных месяцев | не нужно | на 6–12 точках хуже нормального (20–77 %) |
| Библиотека `mapie` | не нужно | конформный множитель — десять строк; зависимость ради этого не оправдана (установлена в стенд, не использовалась) |

---

## Пункт 3. Обнаружение изменений (смена работы, потеря дохода, ребёнок): BOCPD, PELT, простое правило

**Аналогия.** Среднее по году у человека, который полгода назад потерял работу, — это «средняя температура по больнице».
Детектор смены режима отвечает на вопрос «с какого месяца началась нынешняя жизнь?», и прогноз строится только по ней.

**Методы одной строкой.**
- **BOCPD** (Adams & MacKay 2007) — после каждого месяца пересчитывает вероятность «сколько месяцев длится текущий режим»
  (run length). Параметр — *hazard*: априорная частота смен (1/24 — «раз в два года»).
- **PELT** (библиотека `ruptures`, Truong, Oudre & Vayatis, Signal Processing 167, 2020, DOI 10.1016/j.sigpro.2019.107299 —
  Crossref 200) — задним числом режет ряд на куски с разными средними; штраф за каждый разрез.
- **Правило** — «среднее последних 3 месяцев отличается от прежнего больше чем на 3 разброса».

**Литература (дословно).** Adams & MacKay, «Bayesian Online Changepoint Detection», arXiv:0710.3742v1 —
https://arxiv.org/pdf/0710.3742v1 **HTTP 200**, 255 274 байта, `pdftotext`, 17.09.2026:
> «Here we examine the case where the model parameters before and after the changepoint are independent and we derive an
> online algorithm for exact inference of the most recent changepoint. We compute the probability distribution of the
> length of the current "run," or time since the last changepoint, using a simple message-passing algorithm.»
> «process is memoryless and the hazard function is constant at H(τ) = 1/λ.»

**Стенд (`g43/p3_changepoint.py`, `g43/p3b_tune.py`).** 12 месяцев истории, прогноз суммы на 6. `shift_hist` — ряды, где
сдвиг ×0,6/×1,3 **гарантированно** внутри истории (месяцы 3–10); остальные типы — **без смены** (ложные тревоги).
Прогноз после тревоги — среднее с месяца смены. BOCPD — своя реализация с нормально-гамма априором (прогнозное
распределение Стьюдента).

```python
"""G43 p.3: changepoint detection on 12 months of one person. Question: does 'forecast = mean since the detected change'
beat plain mean / naive, and how often does a detector cry wolf on series WITHOUT a change (salary with bonuses,
ADR-015 noise, freelance with zero months)?
Detectors: BOCPD (Adams & MacKay 2007) with Normal-Gamma prior -> Student-t predictive, constant hazard 1/24;
PELT (ruptures, l2 cost, BIC-like penalty); RULE: mean of last 3 months differs from the earlier mean by > 3 pooled sd."""
import numpy as np
from scipy import stats
import ruptures as rpt
from gen43 import gen

T, H, N = 12, 6, 500
rng = np.random.default_rng(4303)


def bocpd_last_cp(x, hazard=1 / 24, mu0=1.0, k0=1.0, a0=2.0, b0=.02):
    """Return MAP start index of the current regime (0 = no change detected). x is scaled by the first-3 mean."""
    R = np.array([1.0]); mu = np.array([mu0]); k = np.array([k0]); a = np.array([a0]); b = np.array([b0])
    for t, xt in enumerate(x):
        scale = np.sqrt(b * (k + 1) / (a * k))
        pred = stats.t.pdf(xt, 2 * a, mu, scale)
        grow = R * pred * (1 - hazard)
        cp = (R * pred * hazard).sum()
        R = np.append(cp, grow); R /= R.sum()
        mu_n = (k * mu + xt) / (k + 1); b_n = b + k * (xt - mu) ** 2 / (2 * (k + 1))
        mu = np.append(mu0, mu_n); k = np.append(k0, k + 1); a = np.append(a0, a + .5); b = np.append(b0, b_n)
    rl = int(np.argmax(R))  # MAP run length after the last point
    return len(x) - rl if rl < len(x) else 0


def pelt_last_cp(x):
    s = x.std() if x.std() > 0 else 1.0
    bk = rpt.Pelt(model="l2", min_size=2).fit(x / s).predict(pen=2 * np.log(len(x)) * 2)
    return bk[-2] if len(bk) > 1 else 0


def rule_last_cp(x):
    a, b = x[:-3], x[-3:]
    sd = np.sqrt((a.var(ddof=1) * (len(a) - 1) + b.var(ddof=1) * 2) / (len(x) - 2)) + 1e-9
    return len(x) - 3 if abs(b.mean() - a.mean()) > 3 * sd else 0


DET = {"bocpd": bocpd_last_cp, "pelt": pelt_last_cp, "rule3": rule_last_cp}
print(f"T={T}, N={N} per kind. alarm = detector says the current regime started after month 0.")
print(f"{'kind':12}{'true cp in hist':>16} | " + " | ".join(f"{d:>5} alarm  e6" for d in DET) + " | mean e6 | naive e6")
for kind in ("shift_hist", "salary", "adr015", "freelance", "trend"):
    alarms = {d: 0 for d in DET}; err = {d: [] for d in DET}; em, en = [], []; hits = 0
    for _ in range(N):
        if kind == "shift_hist":  # force the change inside the history (months 3..10) to measure detection power
            while True:
                y = gen("shift", rng, T + H)
                r = y / np.median(y)
                cps = np.flatnonzero(np.abs(np.diff(np.log(np.maximum(r, 1e-9)))) > .2)
                if len(cps) and 3 <= cps[0] + 1 <= T - 2:
                    break
            hits += 1
        else:
            y = gen(kind, rng, T + H)
        h, fut = y[:T], y[T:]
        sc = h[:3].mean() if h[:3].mean() > 0 else max(h.mean(), 1.0)
        x = h / sc
        em.append(abs(h.mean() * 6 - fut.sum()) / 6 / sc); en.append(abs(h[-1] * 6 - fut.sum()) / 6 / sc)
        for d, f in DET.items():
            c = f(x)
            if c > 0:
                alarms[d] += 1
            seg = h[c:] if c > 0 else h
            err[d].append(abs(seg.mean() * 6 - fut.sum()) / 6 / sc)
    print(f"{kind:12}{hits:>16} | " + " | ".join(f"{alarms[d]/N:10.1%} {np.mean(err[d]):.3f}" for d in DET)
          + f" | {np.mean(em):7.3f} | {np.mean(en):8.3f}")
```

```python
"""G43 p.3b: BOCPD / PELT settings grid. Guard 'G': accept a change only if the new regime has >= 2 months and its
median differs from the old median by > 15 % (robust to one-off bonuses)."""
import numpy as np
import ruptures as rpt
from gen43 import gen
from p3_changepoint import bocpd_last_cp, T, H

N = 400


def guard(h, c):
    if c <= 0 or c > len(h) - 2:
        return 0
    a, b = np.median(h[:c]), np.median(h[c:])
    return c if abs(b - a) > .15 * max(a, 1e-9) else 0


def pelt(x, k):
    s = x.std() if x.std() > 0 else 1.0
    bk = rpt.Pelt(model="l2", min_size=2).fit(x / s).predict(pen=k * np.log(len(x)))
    return bk[-2] if len(bk) > 1 else 0


VAR = {
    "bocpd b0=.02": lambda x, h: bocpd_last_cp(x),
    "bocpd b0=.02+G": lambda x, h: guard(h, bocpd_last_cp(x)),
    "bocpd b0=.1 +G": lambda x, h: guard(h, bocpd_last_cp(x, b0=.1)),
    "bocpd b0=.1 hz1/60+G": lambda x, h: guard(h, bocpd_last_cp(x, b0=.1, hazard=1 / 60)),
    "pelt k=1": lambda x, h: pelt(x, 1),
    "pelt k=1+G": lambda x, h: guard(h, pelt(x, 1)),
    "pelt k=.5+G": lambda x, h: guard(h, pelt(x, .5)),
}
rng = np.random.default_rng(4304)
data = {}
for kind in ("shift_hist", "salary", "adr015", "freelance", "trend"):
    L = []
    while len(L) < N:
        if kind == "shift_hist":
            y = gen("shift", rng, T + H); r = np.log(np.maximum(y / np.median(y), 1e-9))
            cps = np.flatnonzero(np.abs(np.diff(r)) > .2)
            if not (len(cps) and 3 <= cps[0] + 1 <= T - 2):
                continue
        else:
            y = gen(kind, rng, T + H)
        L.append(y)
    data[kind] = L
print(f"{'variant':22}" + "".join(f"{k:>22}" for k in data))
for name, f in VAR.items():
    cells = []
    for kind, L in data.items():
        al, e = 0, []
        for y in L:
            h, fut = y[:T], y[T:]
            sc = h[:3].mean() if h[:3].mean() > 0 else max(h.mean(), 1.0)
            c = f(h / sc, h)
            al += c > 0
            seg = h[c:] if c > 0 else h
            e.append(abs(seg.mean() * 6 - fut.sum()) / 6 / sc)
        cells.append(f"{al / N:9.1%} e6={np.mean(e):.3f}")
    print(f"{name:22}" + "".join(f"{c:>22}" for c in cells))
```

Вывод `p3_changepoint.py` (дословно):
```
T=12, N=500 per kind. alarm = detector says the current regime started after month 0.
kind         true cp in hist | bocpd alarm  e6 |  pelt alarm  e6 | rule3 alarm  e6 | mean e6 | naive e6
shift_hist               500 |      99.6% 0.018 |      22.2% 0.141 |      15.8% 0.148 |   0.186 |    0.031
salary                     0 |      92.4% 0.233 |       0.0% 0.076 |       0.0% 0.076 |   0.076 |    0.203
adr015                     0 |       3.6% 0.060 |       0.0% 0.059 |       0.0% 0.059 |   0.059 |    0.135
freelance                  0 |      12.6% 0.312 |       0.2% 0.303 |       0.0% 0.301 |   0.301 |    0.602
trend                      0 |      29.0% 0.187 |       1.4% 0.212 |       6.8% 0.204 |   0.213 |    0.092
```

Вывод `p3b_tune.py` (дословно; первые 7 строк — повтор p3 из-за импорта модуля без `__main__`-защиты, числа совпадают):
```
T=12, N=500 per kind. alarm = detector says the current regime started after month 0.
kind         true cp in hist | bocpd alarm  e6 |  pelt alarm  e6 | rule3 alarm  e6 | mean e6 | naive e6
shift_hist               500 |      99.6% 0.018 |      22.2% 0.141 |      15.8% 0.148 |   0.186 |    0.031
salary                     0 |      92.4% 0.233 |       0.0% 0.076 |       0.0% 0.076 |   0.076 |    0.203
adr015                     0 |       3.6% 0.060 |       0.0% 0.059 |       0.0% 0.059 |   0.059 |    0.135
freelance                  0 |      12.6% 0.312 |       0.2% 0.303 |       0.0% 0.301 |   0.301 |    0.602
trend                      0 |      29.0% 0.187 |       1.4% 0.212 |       6.8% 0.204 |   0.213 |    0.092
variant                           shift_hist                salary                adr015             freelance                 trend
bocpd b0=.02                  99.8% e6=0.019        93.2% e6=0.198         2.8% e6=0.064        11.2% e6=0.306        23.2% e6=0.189
bocpd b0=.02+G                99.8% e6=0.019        28.7% e6=0.127         2.2% e6=0.064         9.0% e6=0.301        19.5% e6=0.193
bocpd b0=.1 +G                62.5% e6=0.070        26.0% e6=0.126         2.2% e6=0.068        11.2% e6=0.314         0.0% e6=0.211
bocpd b0=.1 hz1/60+G          33.8% e6=0.115        21.0% e6=0.120         0.5% e6=0.065         2.5% e6=0.301         0.0% e6=0.211
pelt k=1                      99.5% e6=0.037        16.0% e6=0.142        15.5% e6=0.088        23.2% e6=0.378        98.8% e6=0.138
pelt k=1+G                    99.5% e6=0.037        16.0% e6=0.142        11.0% e6=0.086        22.2% e6=0.376        35.2% e6=0.176
pelt k=.5+G                   99.5% e6=0.033        16.0% e6=0.142        22.8% e6=0.104        46.8% e6=0.444        37.8% e6=0.165
```

**Что показывает число.**
1. **Когда смена есть, BOCPD находит её почти всегда и почти идеально чинит прогноз**: тревога в 99,6–99,8 % случаев,
   ошибка суммы за полгода **0,019 против 0,186** у среднего по истории (**в 10 раз меньше**). Это самый большой выигрыш в
   Г43 — но только на людях, у которых жизнь действительно изменилась.
2. **Цена — ложные тревоги.** Чувствительный BOCPD принимает декабрьскую премию за «новую жизнь» у **92–93 %**
   зарплатников и портит им прогноз (0,198–0,233 против 0,076). Защита «новый режим ≥ 2 месяцев и медиана сдвинулась
   > 15 %» снижает это до 29 %; огрубление априора и hazard 1/60 — до 21 %, но тогда падает и чувствительность (34 %).
   **Одной настройки, хорошей для всех, на 12 точках нет** — это компромисс «пропуск ↔ ложная тревога», и он решается не
   статистикой.
3. **Наивный прогноз «как в прошлом месяце»** на сдвинутых рядах уже даёт 0,031 — почти как BOCPD, — но на зарплате с
   премией (0,203) и фрилансе (0,602) он ужасен. Значит, ценность детектора — не в точности, а в **выборе**, когда
   переключиться с «среднего» на «последнее».
4. **Фриланс** — главный источник ложных тревог у PELT (22–47 %), и прогноз от них хуже (0,376–0,444 против 0,301).
5. **Тренд** детекторы режут на куски (PELT без защиты — 98,8 %), это не страшно (ошибка даже падает: 0,138 против 0,213).

**Вывод для продукта.** Детектор — **триггер вопроса человеку**, а не автоматическое переключение: «С марта доход ниже на
40 %. Это новая работа / потеря дохода / разовое?» Ответ человека — точнее любой настройки hazard, и он же закрывает
ложную тревогу от премии. Известные разовые события (премия, 13-я зарплата) надо вычитать **до** детектора — это та же
«календарная» правка из п. 1. Рождение ребёнка/переезд видны в **тратах**, а не в доходе — тот же детектор на ряду
расходов (не проверялось отдельным числом — ЗАДОЛЖЕННОСТЬ).

**Цена и корзина.**
| Что | Корзина | Почему |
|---|---|---|
| BOCPD (≈40 строк) + защита + **вопрос человеку** при тревоге; прогноз по текущему режиму после подтверждения | **до запуска** | ×10 точнее при реальной смене; без подтверждения ложные тревоги 21–93 % у зарплатников |
| Простое правило «3 последних месяца против прежних» | не нужно | ловит 16 % реальных сдвигов |
| PELT/`ruptures` в продукте | не нужно | задним числом, а решение нужно сейчас; ложные тревоги на фрилансе до 47 % |
| Детектор на тратах (ребёнок, переезд) | потом | тот же код; нужен ряд трат по категориям |

---

## Пункт 4. Анализ выживаемости и «шанс достичь цели»

**Аналогия.** Анализ выживаемости — это медицинская статистика «сколько пациентов ещё не выписаны через N дней», перенесённая
на «сколько людей ещё не закрыли долг / не достигли цели / не ушли в просрочку через N месяцев». Кривая выживаемости —
доля «ещё не случилось» по месяцам.

**Два разных смысла, и путать их нельзя.**
1. **Когортный** анализ (Каплан–Мейер, модель Кокса) — оценивается **по тысячам людей**: «у заёмщиков с такими признаками
   вероятность досрочного погашения к 12-му месяцу — X». Это ровно кредитный скоринг банков.
2. **Персональная кривая** — «через сколько месяцев **этот** человек достигнет цели» — строится **симуляцией его собственных
   потоков** (время первого достижения, first-passage time). Популяции не нужно.

**Литература (реквизиты — Crossref 200, аннотации — OpenAlex 200, 17.09.2026).**
- Stepanova & Thomas, «Survival Analysis Methods for Personal Loan Data», Operations Research 50(2):277–289, 2002,
  DOI 10.1287/opre.50.2.277.426 (272 цитирования):
  > «This paper shows how using survival-analysis tools from reliability and maintenance modeling allows one to build
  > credit-scoring models that assess aspects of profit as well as default. … The paper looks at three extensions of Cox's
  > proportional hazards model applied to personal loan data.»
- Banasik, Crook & Thomas, «Not if but when will borrowers default», JORS 50(12):1185–1190, 1999,
  DOI 10.1057/palgrave.jors.2600851:
  > «This study looks at the question when will borrowers default not if they will default.»
  Полные тексты не открывались (закрыты, не требовались для вывода «когортный анализ = данные банка») — ЗАДОЛЖЕННОСТЬ.

**Стенд (`g43/p4_goal_chance.py`, вариант априора `g43/p4b_prior.py`).** Цель — накопить G за 12 месяцев; история 12
месяцев; 3000 людей пяти типов. Три способа сказать «шанс»:
DET — как сейчас по сути делает ядро (достижимо / нет по среднему), NORM — вероятность по нормальному закону с
собственным разбросом и поправкой на неточность оценки, NORMz — плюс явный риск пустого месяца дохода (рамка 6 Г41)
с априором Beta. Качество — **оценка Брайера** (средний квадрат «сказанная вероятность − что случилось», 0 — идеал,
0,25 — «монетка 50 %») и таблица надёжности (сказали 30 % — сбылось ли в 30 %).

```python
"""G43 p.4: 'chance to reach the goal' from ONE person's history, and is that chance honest (calibrated)?
Goal: save G within 12 months from net flow. History T=12 months. Methods for p = P(sum of next 12 net flows >= G):
 DET   : canon-like yes/no (mean*12 >= G) -> p in {0,1}
 NORM  : Student-t with own mean/sd, sd*sqrt(12)*sqrt(1+12/T)
 NORMz : NORM + explicit zero-income-month risk (Г41 frame 6): income month empty with Beta(1+zeros, 1+T-zeros) mean
Score: Brier (lower = better) and a reliability table (predicted bin -> realised frequency).
Also: first-passage-time curve (months to goal) for one freelancer - this is the per-person 'survival curve'."""
import numpy as np
from scipy import stats
from gen43 import gen

T, HZ, N = 12, 12, 3000
rng = np.random.default_rng(4305)
KINDS = ("salary", "adr015", "freelance", "trend", "shift")
P = {"DET": [], "NORM": [], "NORMz": []}; Y = []; K = []
for i in range(N):
    kind = KINDS[i % len(KINDS)]
    inc = gen(kind, rng, T + HZ)
    ex = gen("expense", rng, T + HZ); ex = ex / ex[:T].mean() * inc[:T].mean() * rng.uniform(.5, .8)
    net = inc - ex
    m, s = net[:T].mean(), net[:T].std(ddof=1)
    G = max(m * HZ, inc[:T].mean()) * rng.uniform(.6, 1.4)  # goals around what the history suggests
    Y.append(net[T:].sum() >= G); K.append(kind)
    P["DET"].append(float(m * HZ >= G))
    sd = s * np.sqrt(HZ) * np.sqrt(1 + HZ / T)
    P["NORM"].append(stats.t.sf((G - m * HZ) / sd, T - 1))
    z = int((inc[:T] == 0).sum()); pz = (1 + z) / (2 + T)
    nz = inc[:T][inc[:T] > 0]; mi = nz.mean() if len(nz) else 0.0
    sims = []
    em, es = ex[:T].mean(), ex[:T].std(ddof=1)
    si = nz.std(ddof=1) if len(nz) > 1 else .3 * mi
    draws = (rng.random((2000, HZ)) >= pz) * rng.normal(mi, si, (2000, HZ)) - rng.normal(em, es, (2000, HZ))
    P["NORMz"].append(float((draws.sum(1) >= G).mean()))
Y = np.array(Y, float); K = np.array(K)
print(f"N={N}, realised share of goals reached {Y.mean():.1%}")
for k, p in P.items():
    p = np.array(p)
    print(f"\n{k}: Brier {np.mean((p - Y) ** 2):.3f}   by kind: " +
          ", ".join(f"{kk} {np.mean((p[K == kk] - Y[K == kk]) ** 2):.3f}" for kk in KINDS))
    for lo, hi in ((0, .2), (.2, .4), (.4, .6), (.6, .8), (.8, 1.01)):
        sel = (p >= lo) & (p < hi)
        if sel.sum():
            print(f"   predicted {lo:.1f}-{min(hi,1):.1f}: n={sel.sum():5d}  mean predicted {p[sel].mean():.2f}  realised {Y[sel].mean():.2f}")
# per-person survival curve: months until goal
inc = gen("freelance", np.random.default_rng(7), T); ex = np.full(T, inc.mean() * .6)
net = inc - ex; G = 3 * inc.mean()
paths = np.cumsum(rng.choice(net, size=(5000, 36)), axis=1)
first = np.where((paths >= G).any(1), (paths >= G).argmax(1) + 1, 99)
surv = [(first > t).mean() for t in (6, 12, 18, 24, 36)]
print(f"\nfreelancer, goal = 3 months of income, history {np.round(inc/1e3).astype(int).tolist()} k RUB")
print("P(goal NOT yet reached) after 6/12/18/24/36 months: " + " / ".join(f"{x:.0%}" for x in surv))
print(f"median months to goal {np.median(first):.0f}, 80 % range {np.quantile(first, .1):.0f}-{np.quantile(first, .9):.0f}; "
      f"deterministic canon-like answer: {G / net.mean():.1f} months")
```

Вывод (дословно):
```
N=3000, realised share of goals reached 58.9%

DET: Brier 0.368   by kind: salary 0.288, adr015 0.260, freelance 0.405, trend 0.482, shift 0.407
   predicted 0.0-0.2: n= 1512  mean predicted 0.00  realised 0.46
   predicted 0.8-1.0: n= 1488  mean predicted 1.00  realised 0.72

NORM: Brier 0.239   by kind: salary 0.194, adr015 0.196, freelance 0.235, trend 0.309, shift 0.260
   predicted 0.0-0.2: n=  316  mean predicted 0.10  realised 0.38
   predicted 0.2-0.4: n=  743  mean predicted 0.32  realised 0.42
   predicted 0.4-0.6: n=  932  mean predicted 0.50  realised 0.62
   predicted 0.6-0.8: n=  657  mean predicted 0.69  realised 0.73
   predicted 0.8-1.0: n=  352  mean predicted 0.89  realised 0.79

NORMz: Brier 0.293   by kind: salary 0.219, adr015 0.209, freelance 0.241, trend 0.509, shift 0.287
   predicted 0.0-0.2: n= 1012  mean predicted 0.09  realised 0.42
   predicted 0.2-0.4: n=  837  mean predicted 0.30  realised 0.59
   predicted 0.4-0.6: n=  757  mean predicted 0.49  realised 0.70
   predicted 0.6-0.8: n=  356  mean predicted 0.68  realised 0.81
   predicted 0.8-1.0: n=   38  mean predicted 0.83  realised 0.82

freelancer, goal = 3 months of income, history [0, 92, 132, 0, 94, 76, 144, 95, 176, 168, 147, 58] k RUB
P(goal NOT yet reached) after 6/12/18/24/36 months: 64% / 15% / 3% / 1% / 0%
median months to goal 8, 80 % range 4-14; deterministic canon-like answer: 7.5 months
```

Вариант `p4b_prior.py` = `p4` с априором пустого месяца Beta(A0, B0) из аргументов (строка `pz = (A0 + z) / (A0 + B0 + T)`); вывод блока NORMz (дословно):
```
== prior Beta(1 1)
NORMz: Brier 0.293   by kind: salary 0.219, adr015 0.209, freelance 0.241, trend 0.509, shift 0.287
   predicted 0.0-0.2: n= 1012  mean predicted 0.09  realised 0.42
   predicted 0.2-0.4: n=  837  mean predicted 0.30  realised 0.59
   predicted 0.4-0.6: n=  757  mean predicted 0.49  realised 0.70
   predicted 0.6-0.8: n=  356  mean predicted 0.68  realised 0.81
   predicted 0.8-1.0: n=   38  mean predicted 0.83  realised 0.82
== prior Beta(0.2 10)
NORMz: Brier 0.251   by kind: salary 0.190, adr015 0.194, freelance 0.237, trend 0.360, shift 0.273
   predicted 0.0-0.2: n=  556  mean predicted 0.09  realised 0.40
   predicted 0.2-0.4: n=  584  mean predicted 0.30  realised 0.46
   predicted 0.4-0.6: n=  569  mean predicted 0.50  realised 0.59
   predicted 0.6-0.8: n=  683  mean predicted 0.70  realised 0.68
   predicted 0.8-1.0: n=  608  mean predicted 0.89  realised 0.78
== prior Beta(0.5 30)
NORMz: Brier 0.258   by kind: salary 0.190, adr015 0.193, freelance 0.267, trend 0.367, shift 0.273
   predicted 0.0-0.2: n=  576  mean predicted 0.09  realised 0.40
   predicted 0.2-0.4: n=  552  mean predicted 0.29  realised 0.47
   predicted 0.4-0.6: n=  539  mean predicted 0.50  realised 0.62
   predicted 0.6-0.8: n=  637  mean predicted 0.70  realised 0.66
   predicted 0.8-1.0: n=  696  mean predicted 0.90  realised 0.75
```

**Что показывает число.**
1. **Ответ «да/нет» хуже монетки**: Брайер DET **0,368** (монетка — 0,25). Из тех, кому «нет», цель достигли **46 %**; из
   тех, кому «да», не достигли **28 %**. Вероятность по собственному разбросу (NORM) — **0,239**, на треть лучше.
2. **Вероятность у NORM откалибрована лишь в середине** (сказали 0,50 → сбылось 0,62; 0,69 → 0,73), по краям
   самоуверенна (0,10 → 0,38; 0,89 → 0,79). Нижний край портят ряды с настоящим трендом (растущий доход — цель достигается
   чаще, чем обещает среднее). Значит, показывать сырую вероятность нельзя — нужна **перекалибровка** по бэктесту
   (изотоническая/Платт; метод не проверялся — ЗАДОЛЖЕННОСТЬ) и **округление в словесные корзины** («скорее да / 50 на 50 /
   скорее нет»), тогда ошибка края не видна как «10 %».
3. 🔴 **Риск пустого месяца с равномерным априором Beta(1,1) делает хуже, не лучше** (Брайер 0,293): он приписывает
   зарплатнику с 12 полными месяцами 1/14 ≈ 7 % риска пустого месяца. С информативным априором Beta(0,2; 10)
   (≈ 2 % по умолчанию) — 0,251, почти как NORM, а на фрилансе — паритет (0,237 против 0,235). **Поправка к Г41,
   рамка 6:** выигрыш байесовского «пустого месяца» целиком зависит от априора; априор должен приходить из
   популяционной статистики (доля людей с пустыми месяцами), а не из «равномерного незнания». На синтетике выигрыша над
   простым NORM **нет**; он появится только там, где пустые месяцы в истории редки, а в будущем — нет (этого на стенде нет).
4. **Персональная «кривая выживаемости» без когорты считается и полезна**: фрилансер с историей [0, 92, 132, 0, …] тыс. ₽,
   цель — 3 дохода. Детерминированный ответ ядра — «7,5 месяца». Честный ответ — «**скорее всего 8 месяцев, в 8 из 10
   случаев от 4 до 14**; через год цель ещё не достигнута с шансом 15 %».

**Цена и корзина.**
| Что | Корзина | Почему |
|---|---|---|
| «Шанс достичь цели» по собственному разбросу (NORM) + словесные корзины | **до запуска** | Брайер 0,368 → 0,239; одна формула |
| Срок цели как диапазон «медиана, 80 % от–до» (симуляция собственных потоков) | **до запуска** | тот же стенд МК, который уже есть, но с разбросом человека |
| Перекалибровка вероятности по бэктесту | до запуска | края самоуверенны (0,10 → 0,38) |
| Когортный анализ выживаемости (Кокс) для досрочки/просрочки | **не нужно** до своих данных | нужны тысячи историй займов; у банка они есть, у нас нет; при появлении — это профилирование (п. 6) |
| Байесовский риск пустого месяца | потом, с популяционным априором | с «пустым» априором вредит (0,293 против 0,239) |

---

## Пункт 5. Долгий горизонт: сценарии ставки, бутстрэп по блокам, режимы — где длинный прогноз имеет смысл

**Аналогия.** Прогноз на год вперёд — не «какой будет ставка», а «в каком коридоре она, скорее всего, окажется и насколько
плохо может быть». Сценарный генератор — это машина, которая рисует тысячи правдоподобных будущих, чтобы план проверили
на всех, а не на одном.

**Что уже установлено (не переоткрывается).** Тема 32 / Г6: на горизонте года точечный прогноз ставки — «текущий уровень»
(Полбин–Шумилов, Дибольд—Мариано), вилки ЦБ попадают 2 из 16; режимная модель даёт выигрыш **в форме распределения, а не
в точке** (Г6.5.в), количественного сравнения на российской ставке нет. **Здесь это сравнение сделано** — для
модели Васичека, CIR и бутстрэпа (режимная модель Маркова не повторялась — Г6.5 закрыл её качественно; численно — ЗАДОЛЖЕННОСТЬ).

**Методы одной строкой** (формулы — в п. 9).
- **RW-emp** — «ставка останется», а разброс берём из всех прошлых изменений за такой же срок.
- **BOOT6** — бутстрэп по блокам: будущее склеивается из **кусков по 6 месяцев** реальной истории, чтобы сохранить
  серийность (циклы повышений/снижений). Politis & Romano, «The Stationary Bootstrap», JASA 89:1303–1313, 1994,
  DOI 10.1080/01621459.1994.10476870 (Crossref 200).
- **VAS** — модель Васичека: ставка тянется к долгосрочному среднему со скоростью `a` и получает случайные толчки.
  **VAS-ps** — то же, но с учётом того, что сами `a`, среднее и разброс оценены неточно.
- **CIR** — Кокс–Ингерсолл–Росс: то же, но толчки тем сильнее, чем выше ставка (и ставка не уходит ниже нуля).

**Данные.** SOAP ЦБ `DailyInfo.asmx`, метод `KeyRate` (скрипт `g43/fetch_kr.py`, тело `g43/kr.xml`): **HTTP 200,
332 819 байт, 3 260 записей, 2013-09-17 (5,50) … 2026-09-17 (14,00)**; значения на конец месяца — 157 точек.
TLS проверка отключена в скрипте (`ssl._create_unverified_context`) — российский корневой сертификат не ставился по правилу
владельца. Бэктест: каждый месяц с 2016-01, калибровка **только по данным до этой даты** (растущее окно).

```python
"""Fetch CBR key rate (SOAP DailyInfo.KeyRate) -> keyrate.csv (date, rate)."""
import ssl, urllib.request, re, pathlib
G = pathlib.Path(__file__).parent
body = (G / "kr.xml").read_bytes()
ctx = ssl._create_unverified_context()  # no Russian root CA installed by owner's rule
req = urllib.request.Request("https://www.cbr.ru/DailyInfoWebServ/DailyInfo.asmx", data=body,
                             headers={"Content-Type": "application/soap+xml; charset=utf-8"})
r = urllib.request.urlopen(req, context=ctx, timeout=60)
x = r.read().decode()
rows = re.findall(r"<DT>([0-9-]+)T[^<]*</DT>\s*<Rate>([0-9.]+)</Rate>", x)
rows.sort()
(G / "keyrate.csv").write_text("date,rate\n" + "\n".join(f"{d},{v}" for d, v in rows))
print("HTTP", r.status, "bytes", len(x), "records", len(rows), rows[0], rows[-1])
```

```python
"""G43 p.5/p.9: do continuous-time short-rate models (Vasicek 1977, CIR 1985) calibrated on the CBR key rate give better
3/6/12-month scenarios than 'the rate stays where it is'? Data: keyrate.csv (SOAP DailyInfo.KeyRate), month-end values.
Rolling origins every month 2016-01 .. (last - h); calibration uses ONLY data up to the origin (expanding window).
Methods (each gives 4000 scenario draws of r(t+h)):
 RW-emp : r_t + empirical h-month changes seen before the origin (overlapping)
 BOOT6  : r_t + sum of resampled 6-month blocks of monthly changes (stationary-ish block bootstrap)
 VAS    : dr = a(b - r)dt + s dW, exact AR(1) discretisation fitted by OLS; exact Gaussian conditional law
 VAS-ps : VAS with parameter uncertainty (OLS coefficients drawn from their sampling distribution)
 CIR    : dr = a(b - r)dt + s sqrt(r) dW, OLS on r_{t+1}-r_t = a b - a r + e sqrt(r); full-truncation Euler, monthly steps
Point = median of draws. Scores: MAE of point (p.p.), 80 % coverage, CRPS (sample estimator), all in percentage points."""
import pathlib
import numpy as np
import pandas as pd

G = pathlib.Path(__file__).parent
d = pd.read_csv(G / "keyrate.csv", parse_dates=["date"]).set_index("date")["rate"]
m = d.resample("ME").last().dropna()
r = m.values; idx = m.index
rng = np.random.default_rng(4309)
S = 4000


def crps(x, y):
    x = np.sort(x); n = len(x)
    return np.mean(np.abs(x - y)) - np.sum((2 * np.arange(1, n + 1) - n - 1) * x) / n ** 2


def fit_ar1(h):
    X = np.column_stack([np.ones(len(h) - 1), h[:-1]]); Y = h[1:]
    beta, *_ = np.linalg.lstsq(X, Y, rcond=None)
    res = Y - X @ beta; s2 = res.var(ddof=2)
    cov = s2 * np.linalg.inv(X.T @ X)
    return beta, s2, cov


def vas(h, hz, ps=False):
    beta, s2, cov = fit_ar1(h)
    betas = rng.multivariate_normal(beta, cov, size=S) if ps else np.tile(beta, (S, 1))
    c, phi = betas[:, 0], np.clip(betas[:, 1], -0.999, 0.9999)
    x = np.full(S, h[-1])
    for _ in range(hz):
        x = c + phi * x + rng.normal(0, np.sqrt(s2), S)
    return x


def cir(h, hz):
    rr = np.maximum(h, 0.25)
    sq = np.sqrt(rr[:-1])
    Y = (rr[1:] - rr[:-1]) / sq
    X = np.column_stack([1 / sq, sq])
    (ab, ma), *_ = np.linalg.lstsq(X, Y, rcond=None)
    s = (Y - X @ np.array([ab, ma])).std(ddof=2)
    x = np.full(S, h[-1])
    for _ in range(hz):
        xp = np.maximum(x, 0)
        x = x + ab + ma * xp + s * np.sqrt(xp) * rng.normal(size=S)
    return np.maximum(x, 0)


def rw_emp(h, hz):
    ch = h[hz:] - h[:-hz]
    return h[-1] + rng.choice(ch, S)


def boot6(h, hz):
    dch = np.diff(h); B = 6
    starts = rng.integers(0, len(dch) - B + 1, size=(S, -(-hz // B)))
    paths = dch[starts[..., None] + np.arange(B)].reshape(S, -1)[:, :hz]
    return h[-1] + paths.sum(1)


METH = {"RW-emp": rw_emp, "BOOT6": boot6, "VAS": lambda h, z: vas(h, z), "VAS-ps": lambda h, z: vas(h, z, True), "CIR": cir}
if __name__ == "__main__":
    print(f"month-end key rate {idx[0]:%Y-%m}..{idx[-1]:%Y-%m}, n={len(r)}; last {r[-1]}")
    b, s2, _ = fit_ar1(r)
    a = -np.log(b[1]); print(f"full-sample Vasicek (monthly): phi={b[1]:.4f} -> a={a:.4f}/month (half-life {np.log(2)/a:.0f} months), "
                            f"long-run b={b[0]/(1-b[1]):.2f} %, sigma={np.sqrt(s2):.2f} p.p./month")
    start = list(idx).index(idx[idx >= "2016-01-01"][0])
    for hz in (3, 6, 12):
        res = {k: [[], [], []] for k in METH}; res["NAIVE point"] = [[], [], []]
        origins = range(start, len(r) - hz)
        for o in origins:
            h = r[: o + 1]; y = r[o + hz]
            res["NAIVE point"][0].append(abs(h[-1] - y))
            for k, f in METH.items():
                x = f(h, hz)
                lo, hi = np.quantile(x, [.1, .9])
                res[k][0].append(abs(np.median(x) - y)); res[k][1].append(lo <= y <= hi); res[k][2].append(crps(x, y))
        print(f"\n== horizon {hz} months, origins {len(origins)} ({idx[start]:%Y-%m}..{idx[len(r)-hz-1]:%Y-%m})")
        print(f"{'method':12}{'MAE p.p.':>10}{'cov80':>8}{'CRPS':>8}")
        for k, v in res.items():
            if v[1]:
                print(f"{k:12}{np.mean(v[0]):10.2f}{np.mean(v[1]):8.1%}{np.mean(v[2]):8.2f}")
            else:
                print(f"{k:12}{np.mean(v[0]):10.2f}{'':>8}{'':>8}")
        # calm vs turbulent origins: split by whether a >2 p.p. move happened within the window
        turb = np.array([np.max(np.abs(r[o + 1:o + hz + 1] - r[o])) > 2 for o in origins])
        for k in ("RW-emp", "VAS", "CIR"):
            c = np.array(res[k][2]); cv = np.array(res[k][1])
            print(f"   {k:8} calm windows ({(~turb).sum()}): CRPS {c[~turb].mean():.2f} cov {cv[~turb].mean():.0%} | "
                  f"turbulent ({turb.sum()}): CRPS {c[turb].mean():.2f} cov {cv[turb].mean():.0%}")
    # what VAS says today
    x = vas(r, 12, True)
    print(f"\nVAS-ps from {idx[-1]:%Y-%m} ({r[-1]} %), 12 months: median {np.median(x):.2f}, 80 % {np.quantile(x,.1):.2f}..{np.quantile(x,.9):.2f}")
    x = rw_emp(r, 12)
    print(f"RW-emp  from {idx[-1]:%Y-%m}, 12 months: median {np.median(x):.2f}, 80 % {np.quantile(x,.1):.2f}..{np.quantile(x,.9):.2f}")
```

Вывод (дословно, `g43/p9_vasicek.out`; повторный прогон после оборачивания в `__main__` дал побайтно тот же вывод — `diff` пуст):
```
month-end key rate 2013-09..2026-09, n=157; last 14.0
full-sample Vasicek (monthly): phi=0.9554 -> a=0.0456/month (half-life 15 months), long-run b=11.66 %, sigma=1.36 p.p./month

== horizon 3 months, origins 126 (2016-01..2026-06)
method        MAE p.p.   cov80    CRPS
RW-emp            1.32   74.6%    1.14
BOOT6             1.33   73.0%    1.15
VAS               1.60   85.7%    1.25
VAS-ps            1.59   86.5%    1.25
CIR               1.48   90.5%    1.22
NAIVE point       1.30                
   RW-emp   calm windows (108): CRPS 0.47 cov 87% | turbulent (18): CRPS 5.15 cov 0%
   VAS      calm windows (108): CRPS 0.69 cov 96% | turbulent (18): CRPS 4.62 cov 22%
   CIR      calm windows (108): CRPS 0.66 cov 97% | turbulent (18): CRPS 4.55 cov 50%

== horizon 6 months, origins 123 (2016-01..2026-03)
method        MAE p.p.   cov80    CRPS
RW-emp            2.30   73.2%    1.84
BOOT6             2.31   73.2%    1.84
VAS               2.57   74.8%    1.90
VAS-ps            2.55   78.0%    1.87
CIR               2.45   79.7%    1.82
NAIVE point       2.19                
   RW-emp   calm windows (86): CRPS 0.80 cov 93% | turbulent (37): CRPS 4.25 cov 27%
   VAS      calm windows (86): CRPS 1.09 cov 88% | turbulent (37): CRPS 3.77 cov 43%
   CIR      calm windows (86): CRPS 0.99 cov 93% | turbulent (37): CRPS 3.76 cov 49%

== horizon 12 months, origins 117 (2016-01..2025-09)
method        MAE p.p.   cov80    CRPS
RW-emp            4.00   65.0%    2.98
BOOT6             3.96   75.2%    2.89
VAS               3.83   62.4%    2.83
VAS-ps            3.79   66.7%    2.76
CIR               3.90   61.5%    2.76
NAIVE point       3.54                
   RW-emp   calm windows (44): CRPS 1.35 cov 100% | turbulent (73): CRPS 3.97 cov 44%
   VAS      calm windows (44): CRPS 1.43 cov 86% | turbulent (73): CRPS 3.68 cov 48%
   CIR      calm windows (44): CRPS 1.32 cov 86% | turbulent (73): CRPS 3.63 cov 47%

VAS-ps from 2026-09 (14.0 %), 12 months: median 13.02, 80 % 7.99..18.36
RW-emp  from 2026-09, 12 months: median 13.25, 80 % 10.00..21.50
```

Значимость разниц — стенд п. 8, блок (A) (код и вывод там): **CRPS Васичека минус RW-emp на 12 месяцах = −0,22 п. п.,
DM с поправкой Ньюи–Уэста p = 0,65, 95 % блочный бутстрэп [−0,82; +0,82]**; эффективно независимых годовых окон
за 2016–2025 — около **девяти**. На 3 месяцах точка «как сейчас» значимо лучше медианы Васичека (+0,28 п. п., p = 0,007).

**Что показывает число.**
1. **Точка: «ставка останется» лучше всех на всех горизонтах** (MAE 1,30 / 2,19 / 3,54 п. п. против 1,59 / 2,55 / 3,79 у
   Васичека). Возврат к среднему тянет прогноз к 11,7 % — а ставка РФ 2016–2026 не возвращалась, а прыгала. Это
   подтверждает тему 32 на новом классе моделей.
2. **Распределение: на 3 месяцах Васичек/CIR хуже** (CRPS 1,25/1,22 против 1,14), **на 12 месяцах — чуть лучше**
   (2,76 против 2,98, −7 %), **но разница статистически неотличима от нуля** (p = 0,65). Честный вывод: **выигрыша не
   доказано**; 13 лет истории — это ~9 независимых лет, этого не хватает, чтобы различить модели.
3. **Все методы на 12 месяцах самоуверенны**: покрытие 80 %-коридора — 62–75 %. В «бурные» окна (движение > 2 п. п.:
   73 из 117 годовых окон!) покрытие 44–48 % у всех. Ни одна гладкая модель не ловит скачки 2014 и 2022 годов —
   CIR на 3 месяцах в бурных окнах держит 50 % против 0 % у RW-emp, но ценой более широкого коридора в спокойные.
4. **Что модели говорят сегодня** (от 14,00 %, 2026-09): Васичек — медиана 13,0 %, 80 % коридор **8,0–18,4 %**;
   RW-emp — 13,25 %, **10,0–21,5 %**. Разница — в хвостах: Васичек симметричен, эмпирика помнит, что вверх ставка
   прыгала сильнее, чем опускалась. Для человека с плавающей ставкой по кредиту важен именно **верхний хвост**, и его
   честнее даёт эмпирика.
5. **Бутстрэп по блокам (BOOT6)** — лучшее покрытие на 12 месяцах (75,2 %) при CRPS 2,89 — середина. Он
   единственный «помнит» серии повышений.
6. **Где длинный прогноз вообще имеет смысл.** Точечный — нигде дальше «текущего уровня». Сценарный — да, но как
   **стресс-набор «если»**, а не как распределение с вероятностями: «ставка резко вверх» (худший исторический полугодовой скачок **+13,5 п. п.**, 2021-08 → 2022-02; максимум за год — +15,75 п. п. от 2021-02), «ставка плавно вниз» (**21,00 → 14,50 %** за 2025-05 → 2026-05), «без изменений» (проверка по ряду — g43/p5_episodes.out, в конце пункта). Вероятности у этих сценариев на 9 независимых годах
   оценить нельзя — это и есть честная граница. Федоров, Магжанов, Картаев (Деньги и кредит, т. 84, № 2, 2025,
   https://ideas.repec.org/a/bkr/journl/v84y2025i2p36-64.html, через Exa 17.09.2026, аннотация):
   > «for horizons of a year or more, the application of the proposed combination improves the accuracy of forecasts
   > compared to market forecasts, while for shorter horizons, market expectations are more accurate.»
   — то есть на коротком горизонте рыночная кривая (ROISfix) лучше моделей; полный текст не открывался — ЗАДОЛЖЕННОСТЬ
   (это продолжение Г30.2-6, где «работ не существует» уже опровергнуто).

**Цена и корзина.**
| Что | Корзина | Почему |
|---|---|---|
| Три стресс-сценария ставки «резко вверх / без изменений / плавно вниз» по историческим эпизодам РФ, без вероятностей | **до запуска** | честно, дёшево, отвечает на «что если» для плавающих ставок и вкладов |
| Эмпирический коридор изменений ставки (RW-emp) или блочный бутстрэп для Монте-Карло решения | потом | лучше покрытие верхнего хвоста; нужен, только если ставка войдёт в МК решения |
| Васичек / CIR как генератор сценариев | **не нужно** | точка хуже «как сейчас» (значимо на 3 мес.), распределение неотличимо (p = 0,65); тянет к среднему, которого у ставки РФ нет |
| Режимная (марковская) модель | потом | Г6.5: выигрыш в форме распределения; матрица переходов по 3 эпизодам не оценивается — только экспертно |
| Длинный (3–5 лет) прогноз доходов/трат человека | не нужно | на 3–12 точках нет данных; показывать сценарии «если доход −30 %», «если +1 ребёнок» |

Проверка эпизодов (`g43/p5_episodes.out`, дословно; однострочный скрипт: месячные значения, изменения за 6 и 12 месяцев):
```
max +6m 13.5 2021-08-31 | min 6m -12.5 2022-03-31
max +12m 15.75 2021-02-28 | min 12m -12.5 2022-02-28
date
2025-01-31    21.00
2025-02-28    21.00
2025-03-31    21.00
2025-04-30    21.00
2025-05-31    21.00
2025-06-30    20.00
2025-07-31    18.00
2025-08-31    18.00
2025-09-30    17.00
2025-10-31    16.50
2025-11-30    16.50
2025-12-31    16.00
2026-01-31    16.00
2026-02-28    15.50
2026-03-31    15.00
2026-04-30    14.50
2026-05-31    14.50
2026-06-30    14.25
2026-07-31    14.00
2026-08-31    14.00
2026-09-30    14.00
Freq: ME
```

---

## Пункт 6. Прогноз поведения человека: склонность следовать совету, «похожие люди» как априор, граница с 152-ФЗ

**Аналогия.** Новый врач про нового пациента знает мало, но знает, «как обычно бывает у людей такого возраста». Он
начинает с этого знания и поправляет его по анализам пациента. Это и есть **частичное объединение** (partial pooling,
иерархическая байесовская модель): чем меньше данных о человеке, тем больше вес «как у всех»; чем больше — тем больше
вес его собственных.

**Формула одна, и она простая.** Оценка = `w · (своё) + (1 − w) · (как у всех)`, где `w = разброс_между_людьми /
(разброс_между_людьми + неточность_своей_оценки)`. Для доли «следовал совету» — это формула `(k + a) / (n + a + b)`:
`k` — сколько раз из `n` человек последовал, `a` и `b` — «как у всех» (априор Бета-распределения).

**Стенд (`g43/p6_pooling.py`).** (а) разброс дохода человека по 3/6/12 месяцам: своя оценка против объединённой;
(б) шанс, что человек последует следующему совету, после 1/3/6/12 советов: своя доля, поправка Лапласа
`(k+1)/(n+2)`, объединённая. Популяция задана известной — проверяется только выигрыш от объединения.

```python
"""G43 p.6: 'similar people as prior knowledge' without ML. Two quantities a recommender needs about ONE person:
(a) income volatility sigma (drives the cushion and the corridor) from T months;
(b) probability that the person follows advice, from k of n past advices.
Own-only estimate vs partial pooling (empirical Bayes): the population distribution is estimated from OTHER people
(aggregate, no profile of this person is needed at prediction time)."""
import numpy as np
from scipy import stats

rng = np.random.default_rng(4306)
P = 5000
# (a) true log-sigma across people ~ N(log .12, .8)  (CV from ~3 % to ~60 %)
mu_pop, sd_pop = np.log(.12), .8
true_ls = rng.normal(mu_pop, sd_pop, P)
print("(a) income volatility: error of log-sigma estimate (RMSE), and share of people whose cushion multiplier is off by >x1.5")
for T in (3, 6, 12):
    x = rng.normal(0, np.exp(true_ls)[:, None], (P, T))
    own = np.log(x.std(1, ddof=1))
    # sampling var of log sd ~ 1/(2(T-1)); pooled prior estimated from a separate population (here: moments of own estimates)
    v_s = 1 / (2 * (T - 1))
    pri_m = own.mean() + 0.5 * v_s  # small-sample bias of log sd, rough
    pri_v = max(own.var() - v_s, 1e-3)
    w = pri_v / (pri_v + v_s)
    pooled = w * own + (1 - w) * pri_m
    for name, est in (("own", own), ("pooled", pooled)):
        e = est - true_ls
        print(f"   T={T:2d} {name:6} RMSE {np.sqrt(np.mean(e**2)):.3f}  off by >x1.5: {np.mean(np.abs(e) > np.log(1.5)):.1%}  (weight on own data {w:.2f})")
# (b) adherence p_i ~ Beta(3, 5) (population mean 37.5 %)
a0, b0 = 3.0, 5.0
p = rng.beta(a0, b0, P)
print("\n(b) chance to follow the next advice after n advices: Brier score of the prediction")
for n in (1, 3, 6, 12):
    k = rng.binomial(n, p)
    nxt = rng.random(P) < p
    own = np.where(n > 0, k / n, .5)
    lap = (k + 1) / (n + 2)
    eb = (k + a0) / (n + a0 + b0)
    for name, est in (("own k/n", own), ("Laplace", lap), ("pooled", eb)):
        print(f"   n={n:2d} {name:8} Brier {np.mean((est - nxt) ** 2):.4f}")
print(f"   floor (knowing true p): {np.mean(p * (1 - p)):.4f}")
```

Вывод (дословно):
```
(a) income volatility: error of log-sigma estimate (RMSE), and share of people whose cushion multiplier is off by >x1.5
   T= 3 own    RMSE 0.691  off by >x1.5: 46.2%  (weight on own data 0.76)
   T= 3 pooled RMSE 0.578  off by >x1.5: 40.8%  (weight on own data 0.76)
   T= 6 own    RMSE 0.367  off by >x1.5: 23.6%  (weight on own data 0.87)
   T= 6 pooled RMSE 0.337  off by >x1.5: 20.4%  (weight on own data 0.87)
   T=12 own    RMSE 0.225  off by >x1.5: 7.2%  (weight on own data 0.94)
   T=12 pooled RMSE 0.217  off by >x1.5: 6.2%  (weight on own data 0.94)

(b) chance to follow the next advice after n advices: Brier score of the prediction
   n= 1 own k/n  Brier 0.4208
   n= 1 Laplace  Brier 0.2514
   n= 1 pooled   Brier 0.2317
   n= 3 own k/n  Brier 0.2764
   n= 3 Laplace  Brier 0.2392
   n= 3 pooled   Brier 0.2251
   n= 6 own k/n  Brier 0.2403
   n= 6 Laplace  Brier 0.2283
   n= 6 pooled   Brier 0.2215
   n=12 own k/n  Brier 0.2241
   n=12 Laplace  Brier 0.2205
   n=12 pooled   Brier 0.2171
   floor (knowing true p): 0.2081
```

**Что показывает число.**
1. **Разброс дохода:** объединение полезно на 3 месяцах (ошибка 0,69 → 0,58 по логарифму; доля людей, у которых оценка
   промахнулась больше чем в 1,5 раза, 46 % → 41 %), к 12 месяцам выигрыш исчезает (7,2 % → 6,2 %). Даже с объединением
   на 3 месяцах **у 4 из 10 людей разброс ошибочен в полтора раза** — поэтому подушку и коридор на коротких историях
   надо строить с запасом (конформный множитель п. 2), а не с «точной» оценкой.
2. **Склонность следовать совету почти не прогнозируется по одному человеку.** Нижний предел (если знать истинную
   склонность) — Брайер 0,208; «как у всех» без данных — ≈ 0,234; после **12 советов (год!)** объединённая оценка —
   0,217. Своя доля `k/n` после 1 совета — **0,421, хуже монетки**. При одном совете в месяц персонализация по
   поведению даёт мало и поздно; её место — не в выборе плана, а в **формулировке** (тема 36 / Г41 рамка 4).
3. **Где заканчивается «статистика» и начинается «профилирование».** Априор «как у всех» — это **агрегат** (одно среднее
   и один разброс по популяции), он не описывает конкретного человека. «Похожие люди» по признакам (возраст, регион,
   доход, категория трат) — это уже **сегментация по персональным данным**, т. е. профилирование.

**152-ФЗ, ст. 16 (дословно).** КонсультантПлюс,
https://www.consultant.ru/document/cons_doc_LAW_61801/22e884a41450dcb5cb62d956583ad32abe2bbbe9/ — через `r.jina.ai`
**HTTP 200**, 4 309 байт, 17.09.2026:
> «1. Запрещается принятие на основании исключительно автоматизированной обработки персональных данных решений,
> порождающих юридические последствия в отношении субъекта персональных данных или иным образом затрагивающих его права
> и законные интересы, за исключением случаев, предусмотренных частью 2 настоящей статьи.»
> «2. … может быть принято … только при наличии согласия в письменной форме субъекта персональных данных или в случаях,
> предусмотренных федеральными законами …»
> «3. Оператор обязан разъяснить субъекту персональных данных порядок принятия решения на основании исключительно
> автоматизированной обработки его персональных данных и возможные юридические последствия такого решения,
> предоставить возможность заявить возражение против такого решения …»

**Вывод вахты (не юридическое заключение).** Совет FINPILOT решение за человека не принимает (он сам решает, платить ли
досрочно), поэтому ч. 1 прямо не срабатывает — но «иным образом затрагивающих его … законные интересы» толкуется широко.
Безопасная конструкция: (а) априор — только популяционный агрегат, без сегментов; (б) если сегменты появятся —
письменное согласие (ч. 2), объяснение порядка и кнопка «не согласен» (ч. 3), что продукту и так нужно для доверия
(тема 17). Как это соотносится с AI Act и его дерогацией для профилирования — уже разобрано в
`causal_effect_measurement_2026-09-10.md` (стр. ~3050, 3650); здесь не повторяется.

**Цена и корзина.**
| Что | Корзина | Почему |
|---|---|---|
| Априор «как у всех» (одно среднее + разброс) для разброса дохода и доли пустых месяцев | до запуска (из синтетики/открытой статистики), после — из агрегатов | выигрыш на 3 мес. истории (46 % → 41 % грубых промахов); не профилирование |
| Прогноз склонности следовать совету | потом | Брайер 0,234 → 0,217 за год советов; толку мало |
| «Похожие люди» по признакам (иерархическая модель по сегментам) | не нужно до согласия и данных | профилирование по 152-ФЗ ст. 16; выигрыш на нашей частоте совета не доказан |

---

## Пункт 7. Рекомендательные системы сверх тем 9, 16, 17: что применимо к одному совету в месяц

**Не переоткрывается.** Тема 9/31.5 (`recsys_finance_domain_specifics_2026-09-09.md`, ИТОГ Г31.5): холодный старт в финансах
(«individual transactional data are often missing, which causes user cold-start problem»), отсутствие валидированного
офлайн-протокола оценки финансового совета (§3), «пользователь не отличает хороший совет от плохого» (§3-бис);
тема 16 — школа constraint/utility-based (новизна по методу опровергнута); тема 17 — доверие и вред;
Г41 рамка 7 — бандиты и обучение с подкреплением (где уместно и где опасно).

**Что добавляет Г43 (прогнозный угол).**
1. **Контекстные и сессионные рекомендации** (что показать в этой сессии по её контексту) решают задачу «много
   объектов × много показов». У нас **один совет в месяц** и объект не каталог, а план из 66 альтернатив, выбираемый
   моделью. Сессионный подход применим только к **порядку и формулировке** подсказок внутри экрана, не к самому плану.
2. **Холодный старт у нас — это п. 1–2 и п. 6 этого файла**, а не проблема рекомендаций: на 0–3 месяцах истории нужно
   (а) SES/среднее вместо Holt, (б) широкий конформный коридор, (в) популяционный априор разброса и пустых месяцев,
   (г) вопрос человеку при подозрении на смену режима (п. 3). Синтетическая история `build_history_from_current` —
   не холодный старт, а **выдумка тренда** (Г40 п. 5.2: −20 % за полгода из генератора случайных чисел).
3. **Офлайн против онлайн.** Офлайн (на прошлых данных) можно проверить только **прогноз** (п. 2 — покрытие, interval
   score) и **инварианты** плана (Г39). Эффект совета на поведение офлайн не проверяется вовсе (контрфактического «что
   было бы без совета» в логе нет) — только онлайн-экспериментом. Размер такого эксперимента (п. 8, блок D):
   **356 человек на группу**, чтобы различить долю «последовал совету» 30 % против 40 %, и **1 377** — для 30 % против 35 %.
   До запуска этого нет, значит в «до запуска» у рекомендаций — только офлайн-проверки прогноза и инвариантов.
4. **Объяснимость прогноза** — дешевле всего через **сценарии и корзины** («скорее да / 50 на 50»), а не через
   объяснение модели: п. 4 показал, что сырые вероятности по краям врут (0,10 → 0,38), значит показывать их цифрой —
   объяснять неправду.

**Корзина.** Контекстные/сессионные модели — **не нужно** (объект не каталог, частота 1/мес.). Офлайн-протокол
прогноза (покрытие + interval score + PIT) — **до запуска** (п. 2). Онлайн-эксперимент на эффект совета — **потом**
(≥ 356 человек на группу). Внешняя литература в этом пункте не добиралась сверх базы — пункт закрыт ссылкой на темы 9,
16, 17 и Г41, как требует постановка («сверх тем»); новые числа — из стендов п. 2, 4, 8.

---

## Пункт 8. Статистика для проверки самой модели: бутстрэп-интервалы, Дибольд—Мариано, множественные сравнения, размер пилота

**Аналогия.** Два прогноза отличаются на 7 % — это как два бегуна с разницей в полсекунды на одном забеге: без
повторов нельзя сказать, кто быстрее. Статистика здесь отвечает на один вопрос: **разница реальна или это везение
выборки?**

**Инструменты одной строкой.**
- **Бутстрэп-интервал** — пересобираем выборку из неё же тысячи раз и смотрим, как гуляет среднее. Для рядов —
  **блочный** (куски подряд), иначе недооценим неопределённость.
- **Тест Дибольда—Мариано** (Diebold & Mariano 1995, JBES 13(3):253, DOI 10.1080/07350015.1995.10524599; поправка
  Harvey, Leybourne & Newbold 1997, IJF 13(2):281, DOI 10.1016/S0169-2070(96)00719-4 — оба Crossref 200) — «значимо ли
  различаются ошибки двух прогнозов». Для перекрывающихся окон (прогноз на 12 месяцев, сделанный каждый месяц) дисперсию
  считают с поправкой Ньюи–Уэста — иначе соседние окна, почти одинаковые, засчитываются как независимые.
- **Поправка Холма** (Holm 1979, Scandinavian Journal of Statistics 6(2):65–70; реквизиты — по памяти вахты, Crossref
  поиском вернул не ту запись — сверить, ЗАДОЛЖЕННОСТЬ) — если сравниваем с 13 методами сразу, порог значимости делим,
  чтобы «случайный победитель» не проскочил.
- **Размер выборки пилота** — сколько людей нужно, чтобы разница 30 % → 40 % не утонула в шуме.

**Стенд (`g43/p8_stats.py`).**

```python
"""G43 p.8: statistics for checking the model itself.
(A) Is the 12-month CRPS advantage of Vasicek over 'rate stays + empirical changes' real? Overlapping windows ->
    Diebold-Mariano with Newey-West (Bartlett, lag h-1) variance + HLN correction; also moving-block bootstrap CI.
(B) Point 1: paired bootstrap CI (resampling portraits) for 'canon Holt minus SES 0.3' 6-month-sum error, T=6.
(C) Holm correction: canon Holt against 13 alternatives, T=6 (paired t-tests over portraits).
(D) Pilot sample size: people needed to detect a change in 'followed the advice' share, and to verify 80 % coverage."""
import numpy as np
from scipy import stats
from p9_vasicek import r, idx, METH, crps
import p9_vasicek as P9
from gen43 import gen, KINDS, METHODS

rng = np.random.default_rng(4308)
P9.rng = np.random.default_rng(4309)


def dm_hac(d, h):
    d = np.asarray(d); T = len(d); dbar = d.mean(); u = d - dbar
    lrv = u @ u / T
    for k in range(1, h):
        lrv += 2 * (1 - k / h) * (u[k:] @ u[:-k]) / T
    stat = dbar / np.sqrt(lrv / T)
    stat *= np.sqrt((T + 1 - 2 * h + h * (h - 1) / T) / T)
    return dbar, stat, 2 * stats.t.sf(abs(stat), T - 1)


print("(A) key rate, rolling origins from 2016-01")
start = list(idx).index(idx[idx >= "2016-01-01"][0])
for hz in (3, 6, 12):
    sc = {k: [] for k in ("RW-emp", "VAS-ps", "CIR")}; ae = {"naive": [], "VAS-ps": []}
    for o in range(start, len(r) - hz):
        h = r[: o + 1]; y = r[o + hz]
        for k in sc:
            x = METH[k](h, hz); sc[k].append(crps(x, y))
            if k == "VAS-ps":
                ae["VAS-ps"].append(abs(np.median(x) - y))
        ae["naive"].append(abs(h[-1] - y))
    for k in ("VAS-ps", "CIR"):
        d = np.array(sc[k]) - np.array(sc["RW-emp"])
        m, s, p = dm_hac(d, hz)
        B = []; L = max(hz, 3); n = len(d)
        for _ in range(4000):
            st = rng.integers(0, n - L + 1, size=-(-n // L))
            B.append(np.concatenate([d[i:i + L] for i in st])[:n].mean())
        lo, hi = np.quantile(B, [.025, .975])
        print(f"  h={hz:2d} CRPS {k} - RW-emp = {m:+.3f} p.p.  DM-HAC {s:+.2f} p={p:.2f}  block-bootstrap 95 % CI [{lo:+.3f}, {hi:+.3f}]  (n={n}, effective ~{n // hz})")
    d = np.array(ae["VAS-ps"]) - np.array(ae["naive"]); m, s, p = dm_hac(d, hz)
    print(f"  h={hz:2d} MAE VAS-ps - naive = {m:+.3f} p.p.  DM-HAC {s:+.2f} p={p:.3f}")

print("\n(B)+(C) point forecasts, T=6, N=600 portraits (100 per kind)")
T, H = 6, 6
E = {k: [] for k in METHODS}
for i in range(600):
    y = gen(KINDS[i % 6], rng, T + H); hh, fut = y[:T], y[T:]; s = hh.mean() if hh.mean() > 0 else 1.0
    for k, f in METHODS.items():
        E[k].append(abs(f(hh).sum() - fut.sum()) / 6 / s)
E = {k: np.array(v) for k, v in E.items()}
d = E["CANON_holt"] - E["ses0.3"]
bs = [d[rng.integers(0, len(d), len(d))].mean() for _ in range(4000)]
print(f"  canon - ses0.3: mean {d.mean():+.3f} (share of mean income), 95 % bootstrap CI [{np.quantile(bs,.025):+.3f}, {np.quantile(bs,.975):+.3f}]; "
      f"relative {100 * d.mean() / E['CANON_holt'].mean():.0f} % of canon error")
pv = {k: stats.ttest_rel(E["CANON_holt"], E[k]).pvalue for k in METHODS if k != "CANON_holt"}
order = sorted(pv, key=pv.get); m = len(order); rej = True
for j, k in enumerate(order):
    thr = .05 / (m - j); rej = rej and pv[k] < thr
    print(f"  Holm {j+1:2d}. canon vs {k:11} diff {np.mean(E['CANON_holt'] - E[k]):+.3f}  p={pv[k]:.1e}  threshold {thr:.4f}  {'REJECT (canon worse)' if rej and np.mean(E['CANON_holt'] - E[k]) > 0 else ('reject' if rej else 'keep')}")

print("\n(D) pilot sample sizes (two-sided alpha .05, power .8)")
za, zb = stats.norm.ppf(.975), stats.norm.ppf(.8)
for p1, p2 in ((.30, .40), (.30, .35), (.50, .60)):
    pb = (p1 + p2) / 2
    n = (za * np.sqrt(2 * pb * (1 - pb)) + zb * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2 / (p1 - p2) ** 2
    print(f"  follow-the-advice share {p1:.0%} -> {p2:.0%}: {int(np.ceil(n))} people per arm")
for tol in (.05, .03, .02):
    n = za ** 2 * .8 * .2 / tol ** 2
    print(f"  verify 80 % coverage within +-{tol:.0%}: {int(np.ceil(n))} independent forecast-outcome pairs")
```

Вывод (дословно; предупреждения statsmodels в `p8.err`):
```
(A) key rate, rolling origins from 2016-01
  h= 3 CRPS VAS-ps - RW-emp = +0.109 p.p.  DM-HAC +1.31 p=0.19  block-bootstrap 95 % CI [-0.056, +0.261]  (n=126, effective ~42)
  h= 3 CRPS CIR - RW-emp = +0.076 p.p.  DM-HAC +1.23 p=0.22  block-bootstrap 95 % CI [-0.051, +0.184]  (n=126, effective ~42)
  h= 3 MAE VAS-ps - naive = +0.280 p.p.  DM-HAC +2.75 p=0.007
  h= 6 CRPS VAS-ps - RW-emp = +0.021 p.p.  DM-HAC +0.10 p=0.92  block-bootstrap 95 % CI [-0.347, +0.436]  (n=123, effective ~20)
  h= 6 CRPS CIR - RW-emp = -0.027 p.p.  DM-HAC -0.20 p=0.84  block-bootstrap 95 % CI [-0.270, +0.227]  (n=123, effective ~20)
  h= 6 MAE VAS-ps - naive = +0.342 p.p.  DM-HAC +1.33 p=0.185
  h=12 CRPS VAS-ps - RW-emp = -0.220 p.p.  DM-HAC -0.46 p=0.65  block-bootstrap 95 % CI [-0.819, +0.816]  (n=117, effective ~9)
  h=12 CRPS CIR - RW-emp = -0.212 p.p.  DM-HAC -0.62 p=0.54  block-bootstrap 95 % CI [-0.613, +0.515]  (n=117, effective ~9)
  h=12 MAE VAS-ps - naive = +0.262 p.p.  DM-HAC +0.48 p=0.633

(B)+(C) point forecasts, T=6, N=600 portraits (100 per kind)
  canon - ses0.3: mean +0.135 (share of mean income), 95 % bootstrap CI [+0.106, +0.165]; relative 43 % of canon error
  Holm  1. canon vs tsb         diff +0.135  p=2.9e-19  threshold 0.0038  REJECT (canon worse)
  Holm  2. canon vs ses0.3      diff +0.135  p=5.3e-19  threshold 0.0042  REJECT (canon worse)
  Holm  3. canon vs mean        diff +0.134  p=7.7e-19  threshold 0.0045  REJECT (canon worse)
  Holm  4. canon vs ses_fit     diff +0.129  p=1.7e-18  threshold 0.0050  REJECT (canon worse)
  Holm  5. canon vs ing_med5    diff +0.129  p=2.8e-18  threshold 0.0056  REJECT (canon worse)
  Holm  6. canon vs median      diff +0.130  p=1.3e-16  threshold 0.0063  REJECT (canon worse)
  Holm  7. canon vs comb        diff +0.105  p=1.2e-15  threshold 0.0071  REJECT (canon worse)
  Holm  8. canon vs croston     diff +0.110  p=3.6e-13  threshold 0.0083  REJECT (canon worse)
  Holm  9. canon vs arima_aicc  diff +0.101  p=1.1e-10  threshold 0.0100  REJECT (canon worse)
  Holm 10. canon vs sba         diff +0.096  p=4.5e-10  threshold 0.0125  REJECT (canon worse)
  Holm 11. canon vs naive       diff +0.073  p=5.1e-07  threshold 0.0167  REJECT (canon worse)
  Holm 12. canon vs theta       diff +0.060  p=2.0e-06  threshold 0.0250  REJECT (canon worse)
  Holm 13. canon vs damped_fit  diff -0.017  p=3.0e-01  threshold 0.0500  keep

(D) pilot sample sizes (two-sided alpha .05, power .8)
  follow-the-advice share 30% -> 40%: 356 people per arm
  follow-the-advice share 30% -> 35%: 1377 people per arm
  follow-the-advice share 50% -> 60%: 388 people per arm
  verify 80 % coverage within +-5%: 246 independent forecast-outcome pairs
  verify 80 % coverage within +-3%: 683 independent forecast-outcome pairs
  verify 80 % coverage within +-2%: 1537 independent forecast-outcome pairs
```

**Что показывает число.**
1. **Главный вывод п. 1 значим**: продуктовый Holt хуже SES α=0,3 на **0,135** доли дохода (95 % бутстрэп
   [+0,106; +0,165]) — это **43 % его ошибки**; с поправкой Холма Holt значимо хуже **12 из 13** альтернатив;
   неотличим только от подобранного демпфированного Holt (такого же класса). Поправка на множественность вывод не
   меняет — разница огромна.
2. **Выигрыш Васичека/CIR в распределении (п. 5) не значим ни на одном горизонте** (p = 0,19–0,92). На 12 месяцах за
   117 «прогнозов» стоит лишь ~9 независимых лет — интервал разницы [−0,82; +0,82] п. п. шире самой разницы в 4 раза.
   **Это общий урок для всех утверждений «модель X лучше на ставке РФ»:** 13 лет истории не различают модели на
   годовом горизонте. Любое такое утверждение без HAC-поправки — самообман.
3. **Пилот.** Чтобы увидеть рост доли «последовал совету» с 30 % до 40 % — **356 человек на группу**; до 35 % —
   **1 377**. Чтобы проверить, что коридор «80 %» честен с точностью ±5 п. п. — **246 независимых пар «прогноз–факт»**
   (±3 п. п. — 683). Для синтетики это бесплатно; для живых людей — это полгода на 250 пользователях.
4. **Бутстрэп для наших чисел.** Числа Г39–Г43 на синтетике (доли, средние ошибки) должны идти с интервалом; при 300–600
   портретах интервал ±2–3 п. п. — выводы «в разы» устойчивы, выводы «на 5 %» — нет (см. п. 1: ses0,3 против mean —
   разница в третьем знаке, **не различимы**).

**Корзина.** DM с HAC + блочный бутстрэп + Холм в стенд проверки ядра (Г39) — **до запуска** (≈ 60 строк, уже
написаны здесь). Расчёт размера пилота — **до запуска** (план эксперимента). Всё остальное (последовательные тесты,
байесовские A/B) — потом.

---

## Пункт 9. Непрерывные модели: СДУ для ставки, оптимальное управление (ГЯБ, Мертон), численные методы — нужно ли нам

**Аналогия.** Непрерывная модель — как описывать движение машины уравнением скорости в каждое мгновение. Это красиво и
точно, если машина едет плавно. Наш человек «едет» рывками раз в месяц (зарплата, платёж, решение), а ставка ЦБ меняется
ступеньками по решениям совета директоров. Для ступенек уравнение мгновенной скорости — лишний посредник.

### 9.1. Стохастические дифференциальные уравнения (СДУ) для ставки: Васичек и CIR

**Что это (с расшифровкой каждого символа).**
- Васичек: `dr = a(b − r)dt + σ dW`. `r` — ставка; `dr` — её изменение за бесконечно малое время `dt`; `b` — долгосрочный
  уровень, к которому ставку «тянет»; `a` — сила притяжения (чем больше, тем быстрее возврат); `σ dW` — случайный толчок,
  `W` — «броуновское движение» (накопленный нормальный шум), `σ` — его размер.
- CIR: `dr = a(b − r)dt + σ√r dW` — то же, но толчок пропорционален `√r`: при высокой ставке шум больше, ноль недостижим.
- Реквизиты: Vasicek, «An equilibrium characterization of the term structure», JFE 5(2):177–188, 1977,
  DOI 10.1016/0304-405X(77)90016-2; Cox, Ingersoll & Ross, «A Theory of the Term Structure of Interest Rates»,
  Econometrica 53(2):385, 1985, DOI 10.2307/1911242; эмпирическое сравнение однофакторных моделей — Chan, Karolyi,
  Longstaff & Sanders, J. Finance 47(3):1209, 1992, DOI 10.2307/2328983 (все — Crossref 200; тексты CIR и CKLS не
  открывались — ЗАДОЛЖЕННОСТЬ).
- Vasicek (1977), текст — копия на ресурсном сайте актуарного института ISFA,
  https://www.ressources-actuarielles.net/EXT/ISFA/1226.nsf/0/e11e4bc52747d1ddc125772400459afe/$FILE/Vasicek77.pdf
  (адрес найден через Exa; `curl -skL` **HTTP 200**, 643 885 байт, 12 страниц, `pdftotext`, 17.09.2026), с. 185:
  > «the spot rate r(t) follows the so-called Ornstein-Uhlenbeck process, dr = α(γ − r)dt + ρdz, with α > 0 …
  > This description of the spot rate process has been proposed by Merton (1971).»
  > «The instantaneous drift α(γ − r) represents a force that keeps pulling the process towards its long-term mean γ with
  > magnitude proportional to the deviation of the process from the mean. The stochastic element, which has a constant
  > instantaneous variance ρ², causes the process to fluctuate around the level γ in an erratic, but continuous, fashion.»
  🔴 Ключевое слово — **«continuous»**: модель предполагает **непрерывные** пути. Ключевая ставка РФ — ступеньки, и
  самые важные для человека события — скачки (+6,5 п. п. за день в декабре 2014, +10,5 п. п. в феврале 2022; тема 32).
- Arxiv-обзор (Orlando, Mininni, Bufalo, arXiv:1901.02246, через Exa, аннотация) прямо называет те же слабости и лечит их
  разбиением выборки: «to overcome both the usual challenges imposed by regime switching, volatility clustering, skewed
  tails, etc.» — т. е. без доработки однофакторная модель этих свойств не воспроизводит.

**Число на нашей задаче** — п. 5 (стенд `p9_vasicek.py`) и п. 8 (A):
| Горизонт | Точка: MAE «как сейчас» / Васичек | Распределение: CRPS RW-emp / Васичек (с неточностью параметров) / CIR | Значимость разницы CRPS |
|---|---|---|---|
| 3 мес. | **1,30** / 1,59 п. п. (Васичек хуже, p = 0,007) | **1,14** / 1,25 / 1,22 | p = 0,19–0,22 |
| 6 мес. | **2,19** / 2,55 | 1,84 / 1,87 / **1,82** | p = 0,84–0,92 |
| 12 мес. | **3,54** / 3,79 | 2,98 / **2,76** / **2,76** | p = 0,54–0,65 |
Полная калибровка на всей истории: `a` = 0,046 в месяц (**период полувозврата 15 месяцев**), `b` = 11,7 %,
`σ` = 1,36 п. п. в месяц. Полувозврат в 15 месяцев на горизонте решений в 3–12 месяцев означает, что «тяга к
среднему» почти не успевает сработать, а то, что успевает, — тянет не туда (2016–2026 ставка не возвращалась к 11,7 %,
а прыгала между 4,25 и 21).

**Вердикт по 9.1.** Васичек/CIR **не дают выигрыша**: точка значимо хуже «как сейчас» на 3 месяцах, распределение
неотличимо на всех горизонтах. Непрерывность путей противоречит природе ставки (решения совета директоров, скачки).
Если сценарии ставки понадобятся — дискретные: стресс-эпизоды РФ (п. 5) или эмпирика изменений.

### 9.2. Оптимальное управление: уравнение Гамильтона—Якоби—Беллмана (ГЯБ) и задача Мертона

**Что это.** ГЯБ — непрерывный родственник уравнения Беллмана из Г41 (рамка 2): «ценность состояния сейчас = лучшее из
(выгода за мгновение + ожидаемая ценность через мгновение)». Если `dt` сделать месяцем, ГЯБ **превращается** в
дискретное уравнение Беллмана, которое у нас уже разобрано и сравнено с перебором (`dp_vs_enumeration_2026-09-10.md`,
Г41 рамка 2). Задача Мертона (Merton 1969, REStat 51(3):247, DOI 10.2307/1926560; Merton 1971, JET 3(4):373–413,
DOI 10.1016/0022-0531(71)90038-X — Crossref 200) — частный случай ГЯБ с явным ответом: доля рискованных активов
постоянна и равна `(μ − r) / (γσ²)` (`μ` — ожидаемая доходность рискованного актива, `r` — безрисковая ставка, `γ` —
неприятие риска, `σ` — волатильность актива).

**Почему не даёт выигрыша у нас (по пунктам, каждый проверяем).**
1. **Объекта нет.** Мертон выбирает долю акций; у нас инвестиционных рекомендаций нет по закону (тема 18; Г41 рамка 3:
   «рамка неприменима к ядру»). Сам Мертон, по Дейтону (Г41 рамка 3, дословно): «Merton showed that if risk is confined to
   financial assets […] Of course, that leaves a hole in the argument — earnings themselves are uncertain». У нашего
   человека риск — именно в заработке.
2. **Ответ на долговую часть уже известен и дискретен.** В детерминированной задаче «платить долги из потока» с линейными
   процентами оптимальное управление (принцип максимума Понтрягина — непрерывный аналог) — «всё свободное в самый дорогой
   долг», т. е. Avalanche. Г40 п. 4 проверил это против точного решателя: **Avalanche не проигрывает в 0 из 3000
   случаев**. Непрерывный аппарат дал бы тот же ответ дороже. (Вывод «бэнг-бэнг = Avalanche» — рассуждение вахты по
   линейности задачи; отдельным непрерывным решателем не проверялся — ЗАДОЛЖЕННОСТЬ низкого приоритета.)
3. **Там, где неопределённость дохода важна, правильная модель — дискретная** (буферный запас Кэрролла, решается методом
   эндогенной сетки помесячно; Г41 рамка 3, таблица подушки 0,8–4 месяца). Её непрерывная версия существует, но требует
   тех же параметров (`β`, `ρ`) человека и не добавляет ничего, кроме формы записи.
4. **Ограничения ядра не ложатся в ГЯБ.** Жёсткие инварианты `Rt ≥ 0`, `ПДН ≤ 0,40`, 66 дискретных альтернатив,
   сроки целей — это ограничения на **состояние** и дискретное **управление**; в ГЯБ они превращаются в граничные условия
   и вязкостные решения — математически тяжело, практически — та же сетка, что и дискретный Беллман.

### 9.3. Численные методы: что из них у нас уже есть и что нужно

| Метод | Где у нас | Нужно ли |
|---|---|---|
| Монте-Карло (случайные сценарии) | `app/core/forecast.py::monte_carlo_intervals` | **в нынешнем виде — нет**: вокруг нормального шума квантиль считается формулой (Г39 п. 4, ±0,054 σ шума от 1000 прогонов); нужен только когда сценарии не нормальны (пустые месяцы, стресс ставки) |
| Точная дискретизация / схема Эйлера—Маруямы для СДУ | стенд `p9_vasicek.py` (AR(1) — точная дискретизация Васичека; Эйлер с усечением — CIR) | нет, раз не нужны СДУ |
| Конечные разности для ГЯБ | нет | нет |
| Итерация по ценности / метод эндогенной сетки (дискретный Беллман) | нет в ядре; стенды Г41 (`f3a.py`), тема `dp_vs_enumeration` | **до запуска — как офлайн-таблица** подушки Кэрролла (Г41), не как онлайн-решатель |
| Перебор 66 альтернатив + точный MILP как оракул | ядро + стенд Г39 п. 1 | есть |
| Оценка параметров (МНК, AICc, максимальное правдоподобие) | нет (константы α/β/φ зашиты, `forecast.py:26–28`) | SES с подбором α — **потом** (выигрыш появляется от 12 месяцев, п. 1) |

### 9.4. 🔴 Прямой ответ владельцу

**Непрерывные модели (СДУ, ГЯБ, Мертон) на нашей задаче выигрыша не дают, и это проверено числом там, где проверяемо.**
- Васичек/CIR на ключевой ставке РФ 2013–2026: точечный прогноз **хуже** «ставка останется» (значимо на 3 месяцах),
  разброс сценариев **не лучше** эмпирического (p = 0,19–0,92). Причина по существу: модель описывает плавное
  блуждание вокруг среднего, а ставка ЦБ — ступеньки и скачки без возврата к среднему на нашем горизонте.
- ГЯБ/Мертон: у нас нет объекта Мертона (инвестиций), долговая часть решается дискретным правилом без потерь (0 из 3000),
  а неопределённость дохода корректно ложится в **дискретную** модель буферного запаса, которая уже выбрана в Г41.
- Что из «непрерывного мира» **стоит взять** — не модели, а **две идеи**: (1) неопределённость растёт с горизонтом по
  закону, который можно посчитать, а не угадывать константой `√(1+0,5h)` (п. 2); (2) вероятность «дойти до цели»
  считается как время первого достижения (п. 4) — это понятие теории случайных процессов, но считается простой
  симуляцией помесячно.
- Где непрерывный аппарат **стал бы нужен**: продукт с инвестиционными рекомендациями (выбор доли активов — Мертон и его
  развития с доходом от труда), оценка облигаций/ипотеки с плавающей ставкой по рыночной кривой (модели срочной
  структуры — именно для этого Васичек и создан: «derives a general form of the term structure of interest rates»). Ни
  того, ни другого в ядре нет.

---

## ИТОГ Г43

**Процесс, честно.** Классификация — breadth-first (9 пунктов), но все пункты держатся на одном стенде «короткий ряд
одного человека», поэтому стенд строила вахта сама. **Подагентов — 0** (правило «не более двух» соблюдено; шаг
делегирования не прошёл проверку «строго ли необходим»: литература по каждому пункту — 1–3 первоисточника, добытые
прямыми каналами). `WebSearch` — **0 вызовов**; Exa — 3 поиска; прямые каналы — Crossref, OpenAlex, Unpaywall (с
`email=research@example.org`), arXiv, `r.jina.ai` без UA, `curl -skL`, SOAP ЦБ. Кругов — один; второй не понадобился:
противоречий между пунктами нет, есть одна поправка к Г41 (ниже, п. 4 таблицы).
**Главная оговорка ко всем числам:** данные синтетические (152-ФЗ), генератор написан вахтой (`g43/gen43.py`) — шум вокруг
уровня, тренд, сдвиг, нули, крупные покупки. Методы, «угадывающие» устройство генератора, получают фору; поэтому в
выборку специально включены типы, где простые методы должны проигрывать (тренд, сдвиг). Проверка на реальных
помесячных рядах — ЗАДОЛЖЕННОСТЬ № 1.

### 1. Таблица методов

| Метод | Что предсказывает у нас | Данных нужно | Качество на коротких рядах (число) | Цена | Корзина |
|---|---|---|---|---|---|
| **Демпфированный Holt с константами (сейчас в коде)** | доход/расход/платежи | ≥ 3 точки (включается) | **худший из 14**: ошибка суммы за 6 мес. 0,606 / 0,319 / 0,227 при T = 3/6/12; значимо хуже 12 из 13 (Холм) | — | **убрать** |
| SES α = 0,3 (как в каноне §15) / среднее / медиана | уровень дохода и трат | 3+ | 0,209 / 0,182 / 0,165; от лучшего на 0–15 % | одна функция | **сразу** |
| SES с подбором α, ETS/ARIMA по AICc, Theta | то же | 12+ | на 3–6 точках не лучше среднего; на 12 — SES-подбор лучший (0,144) | библиотека/код оценки | потом |
| Тренд (Holt) только при значимом наклоне | растущий доход | 9–12+ | помогает только типу «тренд» (0,052 против 0,192) | проверка значимости | до запуска |
| Обязательные платежи из графиков, премии — календарём | платежи, 13-я зарплата | график / ответ человека | медиана бьёт среднее на зарплате с премиями (0,101 против 0,145) — премия портит статистику | данные уже есть | до запуска |
| Кростон / SBA / TSB | нерегулярный доход, крупные покупки | 6+ с нулями | для суммы за полгода не лучше среднего (0,356–0,382 против 0,356) | мал | не нужно для суммы |
| Иерархический прогноз категорий (MinT) | итог из категорий | ковариации категорий | не проверялся числом; на 3–12 точках ковариацию не оценить | средняя | не нужно |
| **Коридор от собственного разброса (Стьюдент, √h)** | диапазон баланса | 3+ | покрытие 80 %-коридора на 1-м месяце **74–86 %** против **7–47 %** у продукта | одна функция | **сразу** |
| **Конформный множитель по горизонту** | честный диапазон на 1–6 мес. | калибровочная выборка (синтетика → агрегаты) | 81–83 % при нулевом балансе, по типам 62–97 %; лучший interval score на трендах/сдвигах | десять строк + выборка | до запуска |
| Бутстрэп собственных месяцев | диапазон | 12+ | 20–77 % — хуже нормального | мал | не нужно |
| BOCPD + защита + **вопрос человеку** | смена работы / потеря дохода | 6–12 | при реальном сдвиге ошибка **0,019 против 0,186** (×10); ложные тревоги 21–93 % у зарплатников без подтверждения | ~40 строк + экран вопроса | до запуска |
| PELT / простое правило | то же | 12 | PELT: ложные тревоги на фрилансе до 47 %; правило ловит 16 % сдвигов | мал | не нужно |
| «Шанс достичь цели» по собственному разбросу + словесные корзины | цель к сроку | 6+ | Брайер **0,239** против **0,368** у «да/нет» (монетка 0,25) | формула | до запуска |
| Срок цели диапазоном (время первого достижения) | «когда дойду» | 6+ | фрилансер: «8 мес., в 8 из 10 случаев 4–14» вместо «7,5» | уже есть МК | до запуска |
| Когортный анализ выживаемости (Кокс) | досрочка, просрочка | тысячи историй займов | данных нет | высокая + профилирование | не нужно до своих данных |
| Байесовский риск пустого месяца | нулевые месяцы | популяционный априор | с равномерным априором **вредит** (0,293 против 0,239); с информативным — паритет (0,251) | мал | потом, с популяционным априором |
| Частичное объединение «как у всех» (агрегат) | разброс дохода | 3 мес. + агрегат | грубые промахи разброса 46 % → 41 % при T = 3; при T = 12 выигрыша почти нет | мал | до запуска |
| Прогноз склонности следовать совету | реакция на совет | 12+ советов | Брайер 0,234 → 0,217 за год — почти не прогнозируется | средняя | потом |
| Сегменты «похожих людей» | всё | согласие + данные | не проверялось; профилирование по 152-ФЗ ст. 16 | высокая + юр. | не нужно |
| Три стресс-сценария ставки по эпизодам РФ | плавающие ставки, вклады | ряд ЦБ | — (сценарии без вероятностей) | мал | до запуска |
| Эмпирика изменений ставки / блочный бутстрэп | распределение ставки | 10+ лет | покрытие на 12 мес. 65 % / 75 %; CRPS 2,98 / 2,89 | мал | потом |
| **Васичек / CIR (СДУ)** | ставка на 3–12 мес. | 10+ лет | точка хуже «как сейчас» (1,59 против 1,30, p = 0,007); CRPS на 12 мес. 2,76 против 2,98, **p = 0,65** | средняя | **не нужно** |
| ГЯБ / Мертон | потребление, доля активов, долг | параметры предпочтений | объекта нет; долговая часть = Avalanche (0 из 3000 проигрышей, Г40) | высокая | **не нужно** |
| DM с HAC + блочный бутстрэп + Холм | проверка любых «X лучше Y» | бэктест | показал: выигрыш Васичека не значим; проигрыш Holt значим (CI [+0,106; +0,165]) | ~60 строк | до запуска (в стенд Г39) |
| Расчёт размера пилота | план эксперимента | — | 356 чел./группу (30 → 40 %); 246 пар для покрытия ±5 п. п. | формула | до запуска |

### 2. 🔴 Что заменить в нашем SES+МК сразу (с числом выигрыша на синтетике)

1. **`app/core/forecast.py::choose_point_forecast` — вернуть к SES α = 0,3 (как написано в каноне §15) или к среднему
   по истории, без тренда.** Ошибка суммы за 6 месяцев: **0,606 → 0,209 (−66 %) при 3 месяцах истории; 0,319 → 0,182
   (−43 %) при 6; 0,227 → 0,165 (−27 %) при 12.** На 6 месяцах разница значима: +0,135 доли дохода, 95 % CI
   [+0,106; +0,165] (`p8_stats.py`, блок B). Проигрыш — только у людей с настоящим устойчивым ростом дохода (их тренд
   вернуть после проверки значимости, корзина «до запуска»).
2. **`monte_carlo_intervals` — ширина от собственного разброса чистого потока человека, а не 5 % от Rt; рост как √h
   с поправкой на неточность оценки; квантиль Стьюдента; Монте-Карло для нормального случая не нужен (формула).**
   Покрытие заявленных 80 %: **7–47 % → 74–86 % на первом месяце**; при нулевом балансе **6,8 % → 83,5 %**. Для 6-го
   месяца нормальный коридор ещё узок на нестационарных рядах (43–51 %) — это закрывает конформный множитель
   (до запуска): **81 % при T = 6 и 83 % при T = 12 на нулевом балансе**.
3. **`build_history_from_current` — не подавать в Holt** (после п. 1 это решается само: у SES нет тренда, выдумывать
   нечего; Г40: −20 % расходов за полгода из генератора случайных чисел).
4. Дефекты Г40 (окно «30 суток», CV без нулевых месяцев, поток дважды в Rt) — **не заменяются методом**, чинятся в своих
   местах; Г43 их не переоткрывал. Поправка к **Г41 рамка 6**: байесовский «пустой месяц» с равномерным априором
   ухудшает шанс цели (Брайер 0,239 → 0,293) — априор должен быть информативным и популяционным.

### 3. Что показывать пользователю вместо одного числа — и как проверить, что интервал не врёт

**Показывать.**
- **Баланс через N месяцев — диапазоном**: «скорее всего около X; в 8 случаях из 10 от A до B». Для нулевого запаса
  диапазон должен быть **не нулевым** (сейчас — почти нулевой).
- **Шанс достичь цели — словами по корзинам** («почти наверняка / скорее да / 50 на 50 / скорее нет»), а не процентом:
  сырые вероятности по краям врут (сказали 10 % — сбылось 38 %). Срок цели — «около 8 месяцев, обычно от 4 до 14».
- **Ставка — тремя сценариями «если»** (резкий рост как 2021-08 → 2022-02 на +13,5 п. п.; без изменений; плавное
  снижение как 21 → 14,5 % за 2025-05 → 2026-05), без вероятностей.
- **При подозрении на смену режима — вопрос**, а не молчаливая перестройка прогноза.

**Проверять (процедура для стенда Г39).** Бэктест с катящимся началом → покрытие по каждому горизонту 1…6 **и по типам
людей** (допуск ±4 п. п. при 400 портретах) → interval score / pinball (сравнение методов только по ним) → PIT-гистограмма
(ровная = честно, U-образная = коридор узкий) → для вероятностей — Брайер и таблица надёжности. Для живых данных:
≥ 246 пар «прогноз–факт» на проверку покрытия с точностью ±5 п. п. Разницы между методами — DM с HAC-поправкой и
Холмом, иначе перекрывающиеся окна дают ложную значимость.

### 4. 🔴 Прямой ответ по непрерывным моделям

**Не нужны.** Васичек и CIR, откалиброванные на ключевой ставке ЦБ 2013–2026 (SOAP `KeyRate`, 3 260 записей), дают
точечный прогноз **хуже** «ставка останется» (значимо на 3 месяцах, p = 0,007) и распределение сценариев, **неотличимое**
от эмпирики изменений (p = 0,19–0,92; на 12 месяцах за 13 лет есть лишь ~9 независимых окон). Причина по существу:
модель Васичека описывает, по словам самого Васичека, колебания «in an erratic, but continuous, fashion» вокруг
долгосрочного среднего, а ставка ЦБ — ступеньки и скачки (+6,5 п. п. за день в 2014, +10,5 в 2022) без возврата к
среднему на горизонте 3–12 месяцев (полувозврат по калибровке — 15 месяцев). ГЯБ и задача Мертона не нужны: объекта
Мертона (инвестиций) в ядре нет, долговая часть решается дискретным правилом без потерь (Г40: 0 из 3000), неопределённость
дохода уже правильно ложится в дискретную модель буферного запаса (Г41). Из непрерывного мира стоит взять две **идеи** —
закон роста неопределённости с горизонтом и «время первого достижения цели», — обе считаются помесячно без СДУ.
Непрерывный аппарат понадобится только при появлении инвестиционных рекомендаций или оценки инструментов по рыночной
кривой ставок.

### 5. Карта аппарата

| Уровень | Что это по-человечески | Где уже есть в ядре | Где его нет и нужен |
|---|---|---|---|
| **Теория вероятностей** | как описать «может быть так, а может иначе» | нормальный шум в `monte_carlo_intervals`; профили риска как веса | распределение с **нулевыми месяцами** и крупными покупками (не нормальное) — п. 2, 4 |
| **Математическая статистика** | как по данным оценить число и его точность | CV дохода (ADR-015, с дефектом Г40); константы α/β/φ **не оценены** | интервалы с поправкой на неточность оценки; калибровка коридора; DM/бутстрэп/Холм для проверки — п. 2, 8 |
| **Анализ временных рядов** | как предсказать следующее значение ряда | Holt/SES (`forecast.py`) — **выбран худший вариант** | SES/среднее вместо Holt; тренд только при значимости; календарные события; обнаружение смены режима — п. 1, 3 |
| **Байесовские методы** | как обновлять знание по мере новых данных | нет | априор «как у всех» (агрегат) для разброса и пустых месяцев; BOCPD — п. 3, 6 |
| **Стохастические процессы и СДУ** | как описать случайность, растущую со временем | нет | как **модели** — не нужны (п. 9); как **понятия** — время первого достижения цели (п. 4) и закон роста неопределённости √h (п. 2) |
| **Оптимизация и оптимальное управление** | как выбрать лучшее действие | перебор 66 альтернатив + SAW + Avalanche; MILP-оракул в стенде Г39 | дискретный Беллман/буферный запас — офлайн-таблицей подушки (Г41); ГЯБ/Мертон — не нужны (п. 9) |
| **Численные методы** | как это посчитать на компьютере | Монте-Карло 1000 прогонов (для нормального случая лишний); капитализация по месяцам | формульные квантили вместо МК; МК — только для ненормальных сценариев; конечные разности для ГЯБ — не нужны |

### 6. ЗАДОЛЖЕННОСТЬ

1. **Проверка на реальных помесячных рядах.** Все числа — синтетика генератора вахты. Кандидат без персональных данных
   РФ: открытый чешский банковский набор PKDD'99 (Berka, помесячные операции счетов) — не добывался, лицензия и доступ
   не проверены.
2. Иерархический прогноз категорий (MinT) — вывод «не нужно» дан рассуждением, числом не проверен.
3. Детектор смены режима на **ряду трат** (ребёнок, переезд) — не проверен.
4. Перекалибровка вероятности цели (изотоническая/Платт) по бэктесту — не проверена; вывод «края самоуверенны» есть.
5. Адаптивное конформное (Gibbs & Candès, arXiv:2106.00170) — не проверено; требует собственной истории прогнозов человека.
6. Календарное моделирование премий / 13-й зарплаты — вывод «медиана бьёт среднее из-за премий» есть, альтернатива
   «премия как известное событие» числом не проверена.
7. Марковская режимная модель на ставке РФ — числом не проверялась (Г6.5 закрыл качественно).
8. Полные тексты не открывались: M5 (IJF 38(4), 2022); Stepanova & Thomas 2002; Banasik, Crook & Thomas 1999;
   Cox–Ingersoll–Ross 1985; Chan–Karolyi–Longstaff–Sanders 1992; Федоров–Магжанов–Картаев 2025 («Деньги и кредит»).
   Для выводов Г43 их аннотаций/реквизитов достаточно, но цитаты из тел статей не взяты.
9. Реквизиты Holm (1979) не подтверждены Crossref (поиск вернул запись-поправку другой статьи) — сверить.
10. Утверждение «оптимальное управление в линейной долговой задаче = Avalanche» — рассуждение вахты; опирается на
    дискретную проверку Г40 (0 из 3000), непрерывным решателем не проверялось.
11. Дефект Д-01 генератора проекта (срок цели как `date`) стенды Г43 **обошли**, не используя генератор для целей;
    связь стендов с портретами ADR-015 — только через закон шума `adr015`.
12. Библиотеки `mapie` и `lifelines` установлены в венв стенда, но не использовались (конформный множитель и кривая
    достижения цели написаны напрямую) — если понадобится сверка с эталонной реализацией, это следующий шаг.

**Файлы стенда:** `scratchpad/g43/` — `gen43.py`, `p1_point.py` (+ `.out`, `.clean`), `p2_interval.py`,
`p3_changepoint.py`, `p3b_tune.py`, `p4_goal_chance.py`, `p4b_prior.py`, `p5_episodes.out`, `p6_pooling.py`,
`p8_stats.py`, `p9_vasicek.py`, `fetch_kr.py`, `kr.xml`, `keyrate.csv`; первоисточники: `ab.pdf`/`ab.txt`
(Angelopoulos & Bates), `gr.pdf`/`gr.txt` (Gneiting & Raftery), `bocpd.pdf`/`bocpd.txt` (Adams & MacKay),
`vas77.pdf`/`vas77.txt` (Vasicek), `fpp3_ls.html`, `fpp3_croston.md`, `fz152_16b.md`.
