# Тема 13 — Математика goal-based investing (GBI) и life-cycle подхода

**Дата:** 09.09.2026
**Статус файла:** ⏳ пишется по ходу работы (правило «сырьё в файл ДО ответа»)
**Метод:** lead-agent + два подагента (потолок соблюдён), только живые источники.
Реконструкция по памяти модели в этот файл не попадает; где источник не открылся —
явная пометка «канал мёртв».

> 🔴 **Ограничение инструментария, честно.** У ведущего агента в этой сессии НЕТ тула
> `Bash` — ни `curl`, ни `pdftotext`. Обход «PDF нечитаем» сработал по другому каналу:
> `WebFetch` на PDF сохраняет бинарник на диск и печатает путь, а тул `Read` умеет читать
> PDF постранично (`pages=`) — включая PDF, собранные из картинок, где `pdftotext` вернул
> бы пустоту (так взят UBS). Этим способом добыты четыре полнотекстовых первоисточника.
> У подагентов Bash был, и `curl` с браузерным UA открыл зеркало Cambridge там, где SSRN
> отдавал 403. **Записать оба приёма.**

---

## 0. СОСТОЯНИЕ КАНАЛОВ (ведущий агент)

| Источник | URL | Результат |
|---|---|---|
| Das, Ostrov, Radhakrishnan, Srivastav (2018), JOIM | https://srdas.github.io/Papers/GBWM.pdf | 🟢 **открыт полностью** (3.5 МБ, с. 1–12) |
| Deaton, «Franco Modigliani and the Life Cycle Theory of Consumption» (2005) | https://www.princeton.edu/~deaton/downloads/romelecture.pdf | 🟢 **открыт полностью** (58 КБ, с. 1–6 и 12–17) |
| UBS, «Liquidity. Longevity. Legacy.» | https://www.ubs.com/content/dam/assets/wm/global/doc/liquidity-longevity-legacy.pdf | 🟢 **открыт** (1.6 МБ, PDF из картинок, с. 2–7) |
| Vanguard, «Vanguard's Life-Cycle Investing Model (VLCM)», май 2025 | https://corporate.vanguard.com/content/dam/corp/research/pdf/vanguard_life_cycle_investing_model_vlcm_a_general_portfolio_framework_for_goals_based_investing.pdf | 🟢 **открыт** (776 КБ, с. 3–8) |
| Betterment, «Goal Projection and Advice Disclosure» | https://www.betterment.com/resources/projection-methodology | 🟢 **открыт полностью** (HTML) |
| NBER w3954, Bodie–Merton–Samuelson (1992) | https://www.nber.org/papers/w3954 | 🟢 абстракт дословно; полного PDF в открытом доступе нет |
| SSRN, Das–Markowitz–Scheid–Statman (2010) | https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1166899 | 🔴 **403** (но открыто зеркало Cambridge — см. §5) |
| EDHEC | https://climateinstitute.edhec.edu/publications/introducing-comprehensive-investment-framework-goals-based-wealth-management | 🔴 **403** |
| HBR, Merton (2014), «The Crisis in Retirement Planning» | https://hbr.org/2014/07/the-crisis-in-retirement-planning | 🟡 **пейволл**: заголовок, биография, первый абзац. Содержательных цитат НЕ взято |
| Нобелевская лекция Модильяни (1985) | https://www.nobelprize.org/uploads/2018/06/modigliani-lecture.pdf | 🔴 **403** |
| MIT DSpace, Merton (1971) | https://dspace.mit.edu/bitstream/handle/1721.1/63980/optimumconsumpti00mert.pdf?sequence=1 | 🔴 **405 Method Not Allowed** |
| Schwab Intelligent Portfolios, Goal Tracker | https://intelligent.schwab.com/page/goal | 🟡 **301**, редирект не пройден (бюджет) |

---

## 1. Каноническая формулировка GBI — ПРОЧИТАНО В ИСТОЧНИКЕ

### 1.1. Das, Ostrov, Radhakrishnan, Srivastav (2018), «A New Approach to Goals-Based Wealth Management», *Journal of Investment Management*, Vol. 16, No. 3, pp. 1–27

https://srdas.github.io/Papers/GBWM.pdf

**Определение риска (абстракт, дословно):**

> «We introduce a novel framework for goals-based wealth management (GBWM), where risk
> is understood as the probability of investors not attaining their goals, not just the
> standard deviation of investor's portfolios.»

**Ключевая мысль введения, дословно:**

> «Traditionally, the financial industry, financial advisors, and academics in finance
> have associated the notion of "risk" with the standard deviation of an investor's
> portfolio. Investors, on the other hand, typically associate "risk" with the likelihood
> of not attaining their goals. This distinction is important: for example, decreasing
> standard deviation risk in an underfunded investor's portfolio increases, as opposed
> to decreases, the risk of not attaining their goals.»

**Определение GBWM (с. 3, дословно):**

> «In its simplest form, goals-based wealth management can be defined as a process that
> focuses on helping investors realize their goals, both short-term and long-term, through
> a portfolio management method primarily focused on reaching well-defined financial goals.»

**Родословная, как её излагают сами авторы (с. 2–3):**
- Thaler (1985, 1999) — mental accounting: «people treat money with different risk–return
  preferences, depending on what use the money is to be put to».
- Shefrin & Statman (1985) — disposition effect; (2000) — behavioral portfolio theory,
  **BPT-MA** против **BPT-SA**: «investors behave as if they have multiple mental accounts…
  Each mental account portfolio has varying levels of aspiration, depending on the goals
  for the mental account.»
- Roy (1952) — safety-first: «Rather than trade-off risk versus return, investors trade-off
  goals versus safety, see Roy (1952). This leads to normatively different statements of
  the portfolio problem than in the mean–variance theory of Markowitz (1952).»
- **Das et al. (2010)** — «showed that, under specific technical assumptions, there is a
  mathematical linkage between mental accounting theory (MAT) and mean–variance theory
  (MVT), arguing that there is a mapping from a goals-based portfolio to a portfolio on the
  mean–variance Efficient Frontier. This mathematical reconcilement showed that GBWM is
  supported by MVT».
- **Nevins (2004)** — «contended that traditional investment planning fails to recognize
  investor's behavioral preferences and biases, resulting in suboptimal portfolio
  performance… traditional risk measures do not fully capture market behavior and are of
  limited relevance to investors.»
- **Zwecher (2010)** — bucketing (mental accounting) для пенсионного портфеля.
- **Brunel (2015)** — «discussed the equal importance of two goals for an investor: being
  able to avoid nightmares while realizing dreams. Brunel's work focussed on demonstrating
  how goals-based wealth management can be achieved across multiple time horizons for
  multiple life goals. He also suggested how to map the language investors use in describing
  the importance of dreams or the severity of nightmares into acceptable probabilities that
  the investor will realize such dreams or avoid such nightmares.»
- Lopes (1987) — aspiration; Kahneman & Tversky (1979) — prospect theory.

### 1.2. Девять свойств GBWM (с. 4, 7, 8) — дословно

> **Property 1: Clarity.** The financial goals of the investor should be clear.
> **Property 2: Customization.** The advice given to the investors should be individualized
> to cater to their specific goals.
> **Property 3: Risk Specificity.** The probability of the investors attaining (or not
> attaining) their goals should always be clear.
> **Property 4: Risk Compliance.** The advice given to the investor should take into account
> these probabilities.
> **Property 5: Client-centered Communication.** Clients should be asked for information
> about their goals in terms that are clear to them, such as investment time frames, desired
> dollar amounts at the end of these time frames, and desired probabilities of attaining
> these dollar amounts.
> **Property 6: Goal/State Specificity.** Advice discussed with the investors should be based
> on information regarding the investor's goals and the overall state of their portfolio,
> not, in general, the portfolio's individual investment components.
> **Property 7: Portfolio Efficiency.** Investors should always be advised to invest in a
> portfolio that is on the Efficient Frontier.
> **Property 8: State Dependency.** The advice given to investors (i.e., the specific location
> on the Efficient Frontier) should be affected by market changes and easy to understand
> investor preferences, both in bull and bear markets.
> **Property 9: Rules for Rebalancing.** The investor's portfolio should be able to be updated
> automatically at regular intervals… and manually, whenever the investor wishes.

### 1.3. Восемь входных величин от клиента (с. 8, дословно)

> (1) Their time frame (Investment Horizon). (2) The size of their initial investment (Initial
> Wealth). (3) Their goal wealth (Target Wealth). (4) The probability they would like to
> maintain of reaching their goal wealth (Target Probability). (5) The wealth they would not
> want to end below (Loss Threshold Wealth). (6) The probability they would like to maintain
> of ending above the loss threshold (Loss Threshold Probability). (7) Their investment
> preferences in good states, and (8) Their investment preferences in bad states.

**Мой вывод:** целевая конструкция — **пара «цель + порог потерь», каждая со своей
вероятностью**, а не одна метрика: «instead of one reference point, we have two: (i) a Target
Wealth on the spectrum of upside outcomes and (ii) a Threshold Wealth for losses on the
downside» (с. 7).

### 1.4. Математика (с. 9, 12) — дословно

> W̃(t) = W(0)·e^((μ − σ²/2)t + σ√t·Z),  (1) — where Z is a standard normal random variable.

> μ = ½σ² + (z₀/√t)·σ + (1/t)·ln(W(t)/W(0)),  (2)
> where z₀ is defined so that the Target Probability equals Φ(z₀)… Note that Equation (2)
> defines an upward curving (i.e., convex) parabolic relationship between the expected return
> μ and the volatility σ.

> «Any portfolio lying on or above this parabola in the (σ, μ) … plane will satisfy the
> investor's stated goals, therefore, the region on or above this parabola is called the
> **Goal Region**… If we replace z₀ with a generic value z…, we call the resulting parabola
> a **Goal Probability Level Curve** (GPLC)…»

При σ = 0: μ = (1/t)·ln(W(t)/W(0)),  (3). Эффективная граница: σ = √(aμ² + bμ + c),  (4).
**Loss Threshold Curve** — та же формула (2) с подстановкой Loss Threshold Wealth.
Итог задачи (с. 12): «we would like to have a portfolio in the (σ, μ) plane that lies in the
intersection of the Goal Region and the region on or above the Loss Threshold Curve.»

🔴 **Ограничение метрики, названное самими авторами (с. 11, дословно):**

> «The Loss Threshold Probability is always higher than the Target Probability, however, as
> a rule of thumb, values exceeding 99% may be problematic, because tail events above this
> level are hard to model accurately.»

### 1.5. «Меньше волатильность = безопаснее» — опровергнуто (с. 9, дословно)

> «We will show, for example, that the traditional notion of gravitating toward the least
> volatile portfolio in this interval generally does not correspond to the safest choice for
> the investor. Again, this is because the notion of "safest" is defined by the probability
> of attaining their goal, whereas traditionally it has been defined without this goals-based
> perspective.»

### 1.6. Таблица Брюнеля «цель → вероятность» (Table 1, с. 6, дословно)

| Realize | Avoid | Success probability (%) |
|---|---|---|
| Dreams | Concerns | 50, 55, 60 |
| Wishes | Worries | 65, 70, 75 |
| Wants | Fears | 80, 85 |
| Needs | Nightmares | 90, 95 |

Подпись: «Brunel's Goal-Probability table can be used to classify investor goals into different
probability values, which can then be used in our GBWM framework.»

🔴 **Ответ на вопрос о приоритизации: в практической ветке GBI важность цели кодируется НЕ
весом в свёртке, а требуемой вероятностью достижения.**

### 1.7. Критика текущей практики советников (с. 7, дословно, выборочно)

> «(4) Underfunded portfolios are often ignored, resonating with an often heard criticism in
> the wealth and asset management industry that financial advisors are "doctors who treat only
> healthy patients." (5) Critical goals are often over-funded, consuming too much of the
> investor's principal. (6) Periodically, portfolios are adjusted to bring them back to a
> target asset allocation, regardless of market conditions. (7) While advisors understand the
> concept and intuitions of goals-based wealth management, they do not have a framework to
> analyze its implications for portfolio construction.»

Подход (4) советников — expense management («advise investors on how to cut back expenses or
streamline monthly budgets, incorporating present and future cash flows, so that investor can
achieve certain savings goals») — выведен авторами за рамки GBWM:

> «the objective of expense management is different from the objective of goals-based wealth
> management, so it is unsurprising that this approach meets only the first two properties,
> but not the third or fourth.»

🔴 **Неприятно для нас:** FINPILOT по этой классификации попадает в подход (4), который авторы
НЕ считают goal-based, потому что он не оперирует вероятностями достижения. Разбор — §7.

### 1.8. Цифры опроса (с. 5–6, дословно)

> «72% of clients view success based on the overall performance of their portfolio, not the
> performance of individual investments, whereas only 51% of advisors believe that their
> clients view success primarily based on overall portfolio performance…»
> «Talking with a client in goals-based probability language such as "Based on your current
> strategy, there is a 90% chance that you will achieve your investment goal." is very clear
> to 49% of clients and either very clear or quite clear to 92% of clients, whereas individual
> investment-oriented language like "Your U.S. equity investment has been outperforming its
> benchmark index." is only very clear to 29% of clients and either very clear or quite clear
> to 71% of clients.»

---

## 2. Метрика достижения цели и её ДЕФЕКТЫ

### 2.1. ПРОЧИТАНО — Estrada (2018): вероятность провала и его ГЛУБИНА

Javier Estrada (IESE), «The Bucket Approach for Retirement: A Suboptimal Behavioral Trick?»
https://blog.iese.edu/jestrada/files/2019/01/BucketApproach.pdf (PDF 251 КБ, открыт полностью)

Четыре метрики, две из них — прямые аналоги «риска как недостижения цели»:
- **failure rate F** — «the failure rate is a proxy for the probability of failure, which
  implies that a strategy fails with probability F and succeeds with probability 1–F».
- **years sustained**: `E(YS) = F·(L–SY) + (1–F)·(L+BY)`, где L — длина периода, SY — средний
  недобор лет в провальных сценариях, BY — средний остаток в успешных.
- **RAS = E(YS)/SD(YS)**; **D-RAS = E(YS)/SSD_L(YS)**, где `SSD_L(YS) = {F·(–SY)²}^½ = F^½·SY`.

🔴 Дословно, про дефект «одной только вероятности» и способ его лечения:

> «The key difference between RAS and D-RAS is that the former penalizes very large bequests
> (large departures above the mean) whereas the latter does not; in fact, D-RAS only penalizes
> strategies in those retirement periods in which they fail, **and it does so according to the
> size of the shortfall**. Put differently, the difference between RAS and D-RAS is somewhat
> similar to the difference between a Sharpe ratio, which penalizes volatility regardless of
> whether fluctuations are above or below the mean, and a Sortino ratio, which penalizes only
> fluctuations below a chosen benchmark.»

**Вывод подагента:** `SSD_L(YS) = F^½·SY` — готовый двумерный дескриптор «вероятность провала ×
глубина провала». Вероятность и глубина входят мультипликативно: план с малым F, но огромным SY
штрафуется — чего чистая `P(W_T ≥ G)` не делает вовсе.

### 2.2. 🔴 Почему максимизация вероятности достижения ведёт к неограниченному риску на хвосте

Browne (1999), «Reaching Goals by a Deadline: Digital Options and Continuous-Time Active
Portfolio Management», *Advances in Applied Probability* 31, 551–577; https://doi.org/10.2139/ssrn.703

⚠️ **Статус:** первоисточник НЕ открывался (SSRN 403 в этом прогоне). Существо результата
взято из поисковой выдачи: «for the case of a single stock with constant coefficients, the
optimal policy to maximize the probability of reaching a given value of wealth by a predetermined
time is equivalent to simply buying a European digital option with a particular strike price
and payoff».

**Вывод подагента (МОЙ ВЫВОД, не цитата).** Эквивалентность «максимизация P(W_T ≥ G)» ⇔
«покупка digital/binary option» и есть строгое выражение дефекта. Payoff бинарного опциона равен
нулю во ВСЕХ сценариях недостижения, независимо от того, W_T = G−ε или W_T = 0. Функционал
`E[1{W_T ≥ G}]` имеет нулевую чувствительность к глубине провала: «промахнуться на рубль» и
«потерять всё» для него неразличимы. Оптимальная политика поэтому берёт сколь угодно большой
риск там, где цель ещё достижима, и «сдаётся» там, где недостижима. Формально тот же объект,
что **quantile hedging** Föllmer–Leukert (решение вида индикатора на множестве Неймана–Пирсона).
⚠️ Связь с Föllmer–Leukert — вывод подагента, первоисточник не открывался.

### 2.3. ⚠️ Kitces о «probability of success» — НЕ ПОДТВЕРЖДЕНО ЧТЕНИЕМ

kitces.com отдал **403** и на `WebFetch`, и на `curl` с браузерным UA (тело 1486 байт,
страница-заглушка), обе страницы. Цитаты ниже пришли **в сниппете поисковой выдачи** и
на экране страницы НЕ читались:

> «'Probability of success' – the primary metric used for conveying preparedness for retirement
> within most modern planning software – is known to have a number of issues. In particular,
> 'probability of success/failure' entirely misses the dimension of 'magnitude of
> success/failure'…»
> «A plan with a high probability of failure and a low magnitude of failure is qualitatively
> different than a plan with a high probability of failure and a high magnitude of failure, but
> in a world where only 'probability of success' is reported, then these two plans will look
> identical.»

Статус: **вероятно верно, требует верификации через другой канал.** Тезис по существу
независимо подтверждён Estrada (§2.1), поэтому содержательно раздел не висит на Kitces.

---

## 3. Приоритизация нескольких целей — и 🔴 ГЛАВНЫЙ ВОПРОС НОВИЗНЫ

### 3.1. 🔴 Конкурируют ли цели с ПОГАШЕНИЕМ ДОЛГА в одной оптимизации? — ДА, ТАКАЯ РАБОТА ЕСТЬ

**Alaluf, Crippa, Geng, Jing, Kulkarni, Krishnan, Navarro, Sircar, Tang (2024),
«Reinforcement Learning Paycheck Optimization for Multivariate Financial Goals»,
arXiv:2403.06011 (Princeton ORFE).** https://arxiv.org/pdf/2403.06011 — открыт полностью.

ПРОЧИТАНО В ИСТОЧНИКЕ:

> «We study paycheck optimization, which examines how to allocate income in order to achieve
> several competing financial goals. For paycheck optimization, a quantitative methodology is
> missing, due to a lack of a suitable problem formulation.»

> «one aims to allocate monthly income in order to achieve goals like paying out loans,
> purchasing a mortgage, saving for retirement, etc.»

> «To the best of our knowledge, a quantitative solution for paycheck optimization is missing.
> Existing results on paycheck optimization are mainly analytical without an implementable
> methodology (Swart, 2004; Archuleta & Grable, 2011; Hershey et al., 2013).»

**Формализация (формулы дословно).** `X_t^i` — доля цели i, ещё не закрытая. Две разные динамики:

- долговые цели: `X_{t+1}^i = (1 + r_t^i)·X_t^i − S_t·π_t^i / G^i`, i ∈ {Credit Card Debt, Student Loans}
- сберегательные: `X_{t+1}^i = 1 − (1 + r_t^i)(1 − X_t^i) − S_t·π_t^i / G^i`, i ∈ {Home Down Payment, Emergency Funds}
- пенсия отдельно, с 401K/IRA и работодательским матчингом `m_t`.

`S_t` — месячный доход, `π_t^i` — **ДОЛЯ дохода, направленная на цель i**, `G^i` — сумма цели.
То есть распределение свободного денежного потока по целям — в точности вектор `π_t`.

**Приоритет цели** — через кусочно-линейную полезность от выполненной доли `x̄ = 1 − X_t^i`:

```
w1(x; p)        = −p · max(0, 1 − x̄)
w2(x; p, q, h)  = −q · max(0, 1 − x̄) − (p − q) · max(0, 1 − x̄ − h)
```

> «a larger p^i (or q^i) corresponds to a greater urgency to complete goal i»; h ∈ [0,1]
> «to specify the crossover point between when a user pays off the first segment of the goal
> and moves onto the second one».

Целевая функция — максимум суммы полезностей всех целей по времени; решение — policy gradient
(model-free RL).

**🔴 Доказанная неоптимальность «водопада» (лексикографического порядка) — прямой удар по
Avalanche/Snowball как по принципу:**

> «Some existing paycheck optimization solutions rely on a simple waterfall method. Specifically,
> the user needs to prioritize different goals in an absolute order to finish the goals one by
> one. In other words, all incomes will be allocated to a specific goal and only when one is met
> will the next one be considered. As a result, the method is incapable of targeting multiple
> goals simultaneously and thus is generally sub-optimal.»

Контрпример (Appendix A, прочитан дословно): доход $1000/мес, две долговые цели.
Goal 1: $1000, ставка 0, приоритет p1 = 1000. Goal 2: $1 000 000/(1+r), ставка r = 0.001, p2 = 1.

> «First, we would pay off Goal 1, since p1 > p2. … For each subsequent time t > 1, notice that
> the increase in X² due to interest will be equal to 1000. Hence, at each time step t, the debt
> for Goal 2 will increase by 1000, resulting in the user needing to allocate all her paycheck to
> pay down this increase. Thus, X_t² = 1,000,000 for t > 0, and the user will never be able to
> pay down Goal 2.»

> «On the other hand, let us consider a strategy where we recognize the threat of future
> compounding interest. The user would optimally split her paycheck evenly among the two goals.
> … From this point onward, the user would allocate all her paycheck, equal to $1000 towards
> Goal 2, which will be gradually paid down.»

Три типажа в экспериментах: «the home buyer», «the saver/retirement planner», «the debtor, who
prefers to pay off debt first» (для debtor: `p_credit card = p_student loan = 20.0`). Snowball
признан там предпочтением, а не оптимумом:

> «different users may have different priorities for each goal … or they may prioritize the
> confidence boost that comes from zeroing out debt and choose to pay out small debts first.»

**🔴 ВЫВОД ПО НОВИЗНЕ (важно для текстов проекта).** Ниша НЕ пуста. Формулировка «мы первые
объединяем долг и цели в одной оптимизации» **больше не проходит** — Princeton-группа поставила
и решила ровно эту задачу. Проверяемые зазоры (по прочитанному тексту, не по догадке):
(а) нет рискового портфеля/распределения активов внутри целей — только доли дохода, ставки
экзогенны; (б) **нет ограничения платёжеспособности типа ПДН и нет резерва как жёсткого
инварианта** — emergency fund просто одна из целей; (в) нет вероятностной метрики достижения
(всё сведено к ожидаемой полезности); (г) налоговый контур американский (401K/IRA).
Рабочая замена формулировки: «долг + цели + жёсткие регуляторные и ликвидностные инварианты,
детерминированно и объяснимо, а не чёрным ящиком RL».

### 3.2. Найдено, но НЕ прочитано (честный статус)

- **Das, Khadilkar, Mittal, Ostrov, Srivastav, Wang (2026), «A Meta Reinforcement Learning
  Approach to Goals-Based Wealth Management»**, arXiv:2605.02300. Из сниппета: «Each GBWM
  problem involves a multiple year scenario over which the investor looks to optimally choose an
  investment portfolio each year and choose to fulfill all, some, or none of the different
  financial goals that arise each year, seeking to maximize the expected total investor utility
  obtained from the fulfilled financial goals»; MetaRL даёт «97.8% of the optimal expected
  utilities determined via Dynamic Programming». ⚠️ Не открыто, цитата из сниппета.
- **«Dynamic optimization for multi-goals wealth management»**, *Journal of Banking & Finance*,
  2021 — https://www.sciencedirect.com/science/article/abs/pii/S0378426621001515 — paywall.
- **Deguest, Martellini, Milhau, «Goal-Based Investing: Theory and Practice»** (World Scientific,
  2021) — полного текста в открытом доступе не найдено; формула «secure essential goals with the
  highest confidence level and maximize the chances to reach aspirational goals» взята
  **из аннотации магазина, не из книги**. Пересказ содержания по аннотации в этот файл не вносится.
- arXiv 2105.07915 «Hedging Goals», arXiv 2510.21650 «Goal-based portfolio selection with fixed
  transaction costs» — найдены, не открыты.

---

## 4. Life-cycle / consumption smoothing — ПРОЧИТАНО В ИСТОЧНИКЕ

Источник: Angus Deaton, «Franco Modigliani and the Life Cycle Theory of Consumption», Рим,
17–18.02.2005. https://www.princeton.edu/~deaton/downloads/romelecture.pdf
(Дейтон — нобелевский лауреат по экономике потребления; авторитетное изложение, но не сам
Модильяни. Первоисточники Modigliani–Brumberg 1954/1980 не открывались.)

### 4.1. Формулировка гипотезы (SUMMARY, дословно)

> «In the early 1950s, Franco Modigliani and his student Richard Brumberg worked out a theory of
> spending based on the idea that people make intelligent choices about how much they want to
> spend at each age, limited only by the resources available over their lives. By building up and
> running down assets, working people can make provision for their retirement, and more generally,
> tailor their consumption patterns to their needs at different ages, **independently of their
> incomes at each age**.»

### 4.2. Merton (1969) внутри этой рамки (с. 14, дословно)

> «Theoretical results by Robert Merton (1969) provided further support; Merton showed that if
> risk is confined to financial assets, the basic rule for life-cycle consumers of setting
> consumption proportional to assets, remains true when utility maximization was replaced by
> expected utility maximization. **Of course, that leaves a hole in the argument — earnings
> themselves are uncertain — and that hole turns out to be important, at least in some cases.**»

🔴 Это ровно наш случай: доход домохозяйства неопределён, SES+Монте-Карло закрывает эту дыру.

### 4.3. 🔴 Carroll (1997), buffer-stock: почему long-horizon рамка НЕ переносится на короткий горизонт (с. 14–15, дословно)

> «Work on precautionary saving, particularly by Carroll (1997), has shown that people with
> uncertain future earnings who are sufficiently prudent **will never borrow**, if there is the
> possibility, however remote, that they will not earn enough to be able to repay their debts.
> If such people expect their earnings to grow over time, they will nevertheless keep their
> consumption within their current incomes, thus inducing a close articulation, or "tracking,"
> between consumption and income. In this case, although people are maximizing their expected
> lifetime utility, as postulated by the life-cycle theory under uncertainty, **their consumption
> is effectively constrained by their current incomes**. Such behavior is directly contrary to one
> of the central insights of the Modigliani model, that the profile of consumption can be detached
> from the profile of income…»

> «In these extreme precautionary or "liquidity constrained" accounts of saving, consumption is
> smoothed, **not over the whole life-cycle, but over much shorted periods of a few years at a
> time**, see again Carroll (1997) and Deaton (1991). In the literature, this is often referred to
> as **"high-frequency" smoothing of income**, as opposed to the "low frequency" or "life-cycle
> frequency" smoothing that was postulated by Modigliani and Brumberg.»

> «it is the youngest families who are likely to want to borrow, but either cannot or are too
> prudent to do so, and are therefore more or less constrained by their current earnings, while
> those in middle-age behave in the traditional life-cycle way. That such a formulation is
> consistent both with expected utility maximization and with the survey data has been shown in an
> important paper by Pierre-Olivier Gourinchas and Jonathan Parker (2002).»

🔴 **Мой вывод — самый важный результат §4.** Литература сама разделяет два режима:
«life-cycle frequency» (десятилетия, Модильяни–Мертон) и **«high-frequency» смягчение потока на
горизонте нескольких лет при ликвидностном ограничении** (Carroll, Deaton, Gourinchas–Parker).
Наше ядро — распределение свободного потока при Rt≥0 и ПДН≤0.40, горизонты от месяцев — живёт
во ВТОРОМ режиме. Ссылаться в текстах проекта на Модильяни–Мертона как на теоретическую опору
для горизонта 1–5 лет **некорректно**; корректная опора — buffer-stock ветка.

### 4.4. Bodie, Merton, Samuelson (1992) — абстракт дословно

https://www.nber.org/papers/w3954 (*Journal of Economic Dynamics and Control*, 16, 427–449, 1992)

> «This paper examines the effect of the labor-leisure choice on portfolio and consumption
> decisions over an individual's life cycle… **The ability to vary labor supply ex post induces
> the individual to assume greater risks in his investment portfolio ex ante.** The model explains
> why the young (enjoying greater labor flexibility over their working lives) may take greater
> investment risks than the old. It also offers an explanation as to why consumption spending is
> relatively "smooth" despite volatility in asset prices. Finally, the paper provides a compact
> method for valuing the risky cash flows associated with future wage income.»

**Мой вывод:** логика «гибкость дохода ex post → допустимость большего риска ex ante» обосновывает,
почему риск-профиль должен зависеть от устойчивости дохода, а не только от самоописания
пользователя. В модели v3.0.0 такой связи нет. Кандидат в гипотезы, не в требования.

### 4.5. Критика life-cycle рамки, названная самим Дейтоном (с. 15–17, дословно)

> «Perhaps the most fundamental challenge to the life-cycle model has been directed at its basic
> underlying assumption, that people make rational, consistent, intertemporal plans…»

> «Even commercial financial planners advise their clients about retirement planning according to
> rules and recommendations, such as target wealth to income ratios that, under some circumstances,
> are wildly inconsistent with life-cycle theory. **These commercial plans are not better than
> life-cycle plans, and can lead to disaster under some circumstances**, but they attest to the
> implausibility that individuals, who lack the resources and computer facilities of financial
> planners, do better in following life-cycle rules.»

> «Under hyperbolic discounting, people wait too long to get started on saving for retirement…
> More generally, default options in saving plans matter, because people procrastinate on changing
> the default; Richard Thaler and Shlomo Benartzi (2004) have analyzed (and trade-marked) a plan
> called "Save more tomorrow™"…»

> «life-cycle theory captures some of the truth, even if it is clear that the details are wrong.»

**Мой вывод:** «commercial plans… can lead to disaster» бьёт по классу продуктов с эвристическими
константами («3 оклада резерва», «порог 7 % APR» из патента Capital One), но НЕ бьёт по
конструкции с явной целевой функцией и ограничениями.

---

## 5. Критика GBI — и её ИЗМЕРЕННАЯ цена

### 5.1. 🔴 Сколько стоит разбиение по ментальным счетам: 12 базисных пунктов

**Das, Markowitz, Scheid, Statman (2010), «Portfolio Optimization with Mental Accounts»,
*Journal of Financial and Quantitative Analysis* 45(2), 311–334.**
SSRN отдал 403; открыто **зеркало Cambridge** (PDF 24 стр., 462 КБ, прочитано целиком):
https://www.cambridge.org/core/services/aop-cambridge-core/content/view/4B23CFB326982C52014A1BA447FA9244/S0022109010000141a.pdf/portfolio_optimization_with_mental_accounts.pdf

ПРОЧИТАНО В ИСТОЧНИКЕ:

> «We demonstrate a mathematical equivalence between MVT, MA, and risk management using value at
> risk (VaR). The aggregate allocation across MA subportfolios is mean-variance efficient with
> short selling. Short-selling constraints on mental accounts impose very minor reductions in
> certainty equivalents, only if binding for the aggregate portfolio, offsetting utility losses
> from errors in specifying risk-aversion coefficients in MVT applications.»

> «The MA framework results in no loss in MVT efficiency when short selling is permitted. … Since
> MA portfolios are mathematically equivalent to MVT portfolios, combining optimal MA subportfolios
> also results in an aggregate portfolio that is on the MVT frontier.»

🔴 **Случай БЕЗ коротких продаж — искомое число:**

> «If no short sales are allowed, subportfolio optimization results in a few basis points (bp) loss
> in efficiency relative to optimizing a single aggregate portfolio (see also Brunel (2006)).
> However, this loss is small compared to the loss that occurs from investors inaccurately
> specifying their risk aversions. … We show that the efficiency loss declines as investors become
> increasingly risk averse.»

> «In the presence of short-selling constraints, the aggregate portfolio is not necessarily on the
> constrained portfolio frontier. … The aggregate portfolio has a mean return of 13.31% with a
> standard deviation of 19.89% and lies just below the frontier. If the same portfolio were to lie
> on the constrained frontier at the same standard deviation, it would return 13.43%. The loss of
> mean-variance efficiency because of the short-selling constraint is **12 bp**.»

> «When constraints are placed on short selling, aggregates of subportfolios are inefficient in
> comparison to a single optimal portfolio by only a few basis points. Portfolio inefficiency that
> arises from investors' inability to specify accurate mean-variance trade-offs in the aggregate
> portfolio level could be much larger.»

Практический рецепт (дословно): «At a practical level, we need only impose the short-selling
constraint at the aggregate portfolio level. Often the aggregate portfolio does not entail short
selling even when some subportfolios do.»

**Мост «вероятностная цель → дисперсия» (дословно):** риск определён как «a definition of risk as
the probability of failing to reach the threshold level in each mental account, and attitudes
toward risk that vary by account», и при этом «Once the investor specifies her subportfolio
threshold levels and probabilities, the problem may be translated into a standard mean-variance
problem with an implied risk-aversion coefficient.» То есть (H, α) → γ.

**Вывод подагента:** это ключевой контраргумент против тезиса «GBI строго хуже единой
оптимизации». Цена разбиения по счетам без коротких продаж измерена: **12 б.п.** доходности на
конкретном примере, тогда как ошибка задания коэффициента риск-аверсии в единой MVT стоит
существенно дороже. Спор не «строго хуже», а «хуже на величину, меньшую, чем ошибка измерения
предпочтений» — а предпочтения в рознице измеряются плохо всегда.

### 5.2. ПРОЧИТАНО — Estrada (2018): bucketing проигрывает, и вот механизм

Тот же источник, что §2.1.

> «Third, it is consistent with the well-known behavioral bias of mental accounting; a retiree is
> likely to find the separation between the withdrawal account and the investment account
> appealing.»

> «However, a plausible strategy is not necessarily an optimal one. In fact, Kitces (2014) suggests
> that simple static allocations yield better results than bucket strategies, unless the latter
> involve rebalancing. More precisely, based on U.S. evidence beginning in 1966, he shows that
> bucketing with rebalancing yields the same performance as static strategies, and bucketing
> without rebalancing underperforms static strategies.»

> «the comprehensive evidence discussed here, from 21 countries over a 115-year period, questions
> its effectiveness. In fact, simple static strategies, which by definition involve periodic
> rebalancing, clearly outperform bucket strategies, and they do so based not just on one but on
> four different ways of assessing performance.»

Дизайн: база Dimson–Marsh–Staunton, 21 страна, 1900–2014, портфель $1000, IWR 4 %, горизонт
30 лет, 11 статических стратегий против 3 вариантов bucket; в bucket-стратегиях ребалансировки
нет по построению.

🔴 Структурное возражение, применимое к любому «ведру»:

> «Importantly, note that largely by definition, a bucket approach and periodic rebalancing are
> inconsistent with each other.»

**Вывод подагента:** самый сильный аргумент против наивного GBI-разбиения: раздельные счета
механически запрещают ребалансировку между ними, а именно она и даёт основной прирост.
Потеря не абстрактная «неэффективность агрегата», а конкретный отключённый механизм.

---

## 6. Практика — ПРОЧИТАНО В ИСТОЧНИКЕ

### 6.1. 🔴 UBS Wealth Way (Liquidity. Longevity. Legacy.) — самая ценная находка прогона

https://www.ubs.com/content/dam/assets/wm/global/doc/liquidity-longevity-legacy.pdf
(PDF из картинок, прочитан постранично через `Read`.)

**Определение подхода (с. 2, дословно):**

> «Every family's financial plan is unique, but most investment strategies are organized quite
> similarly. **Instead of using "risk tolerance" as the primary guiding factor**, our approach is
> built on the foundation of your financial objectives. The Liquidity. Longevity. Legacy. approach
> allocates family wealth into three strategies that we have designated the 3Ls…»

> «**Liquidity**: Assets in the Liquidity strategy are allocated to match expenditures in order to
> provide an automatic (or nearly automatic) and steady cash flows for the next 2 to 5 years…»
> «**Longevity**: … designed and sized to include all of the assets and resources the family plans
> to utilize for the remainder of their lifetimes…»
> «**Legacy**: … includes assets that are in excess of what the family members need to meet their
> own lifetime objectives…»

**Fig. 3 (с. 5) — теоретические опоры и метрики, дословно из таблицы:**

| | Liquidity | Longevity | Legacy |
|---|---|---|---|
| Purpose | Provide liquidity for near-term spending | Provide asset growth and appropriate risk hedging to meet lifetime goals | Growth of legacy assets |
| Investment approach | Asset-liability matching | Total wealth LDI | Taxable endowment |
| **Sizing** | **Next three years of cash flow** | Based on objectives, age | Surplus |
| **Risk assessment** | **Probability of success, funding ratio, surplus risk** | (то же) | Long-term risk-adjusted return |
| Intellectual Framework | Merton, Samuelson, Kahneman, Thaler, Waring, Sharpe 2.0 | (то же) | Markowitz, Sharpe 1.0, Swensen |

**Liability-driven investing — переопределение риска (с. 5, дословно):**

> «Instead of focusing on day-to-day volatility as the primary measure of risk, a liability-driven
> approach builds a portfolio optimized to help meet the investor's future liabilities. **Risk is
> redefined as not meeting those liabilities.**»

> «From a technical standpoint, what really matters in these situations is the surplus or deficit
> of the strategy — the assets minus the liabilities — and not the absolute level of assets or
> variance in the portfolio. Accordingly, **the objective function should shift from maximizing
> assets relative to portfolio volatility to a strategy that maximizes the surplus in context of
> the volatility of the surplus.**»

**UBS сам ссылается на аргумент 1/N (с. 5, дословно) — стык с закрытой темой 12:**

> «recent research indicates that a simple equal weighted approach outperforms as frequently as
> much more sophisticated MPT-based approaches. It turns out that the narrow focus on "optimizing
> portfolios" has not led to max outcomes for investors.»

**Горизонт как определяющий фактор (с. 6, дословно):**

> «No matter the "risk tolerance" of the individual, investing funds earmarked for a grandchild's
> college tuition in a moderate portfolio makes very little sense if the check is due at the
> bursar's office in six months but might be perfectly rational if college is still seven years
> away.»
> «Probability of loss in any asset or portfolio is dependent on time horizon, which means time
> horizon should have an impact on the appropriate investment portfolio.»

🔴 **ГЛАВНАЯ ЦИТАТА ПРОГОНА (с. 7, дословно). UBS называет НАШУ задачу как известный дефект
ментального учёта — и сознательно принимает сегментацию:**

> «mental accounting describes a tendency that leads people to segment their assets and spending
> goals into distinct parts and treat those parts differently without thinking of the whole. This
> proclivity can lead to suboptimal decision-making, **such as holding a credit card balance at a
> 15% interest rate when this could be paid off by an investment that yields 2%**. The 3L framework
> **takes advantage of this segmenting inclination** by separating assets to help meet specific
> spending objectives. The result is an intuitive investment strategy that creates a clear
> connection between assets and the objectives for those assets.»

**Мой вывод (важный для новизны):** размен «дорогой долг против низкодоходного актива» назван
прямым текстом, с числами 15 % против 2 % — но как **иллюстрация ошибки клиента**, а не как
задача, которую фреймворк решает. UBS фиксирует дефект и строит продукт НА нём («takes
advantage»), потому что сегментация даёт поведенческую дисциплину. То есть в GBI-практике
верхнего сегмента конфликт «цель против долга» **осознан и намеренно оставлен нерешённым**.
Это сильнее, чем «никто не считает»: индустрия знает про размен и отказалась его считать
в пользу удобства. Формулировка новизны FINPILOT должна опираться на это.

### 6.2. Betterment — ПРОЧИТАНО В ИСТОЧНИКЕ

https://www.betterment.com/resources/projection-methodology

> «The recommended monthly contributions estimate is based on **a 50% likelihood** of the portfolio
> value reaching the goal target at the end of the investment term for all investing goals, other
> than PRP goals.»

График: «one line shows the projected portfolio value under average market conditions» (50-й
перцентиль) и «The lighter, shaded region indicates the range within which there is 80%
likelihood» (10-й–90-й перцентили).

Измеренные нули по этому документу: метод расчёта (Монте-Карло или замкнутая форма) **не
раскрыт**; взаимодействие нескольких целей **не описано вовсе**; **долг и обязательства
не упоминаются нигде**.

🔴 **Мой вывод:** рекомендация взносов при вероятности достижения **50 %** — подбрасывание монеты,
поданное как совет. По шкале Брюнеля (§1.6) 50 % — нижняя граница категории «Dreams», а не
«Needs». Массовый робо-адвайзер де-факто ставит все цели пользователя в разряд мечты.

### 6.3. Vanguard VLCM — ПРОЧИТАНО В ИСТОЧНИКЕ

«Vanguard's Life-Cycle Investing Model (VLCM): A general portfolio framework for goals-based
investing», Vanguard research, май 2025.

**Конструкция целевой функции (с. 5, дословно):**

> «One of the main advantages of a utility theory is that it explicitly accounts for an investor's
> risk preference or risk aversion. The VLCM ranks different glide-path options by applying the
> risk-tolerance criteria embedded in the utility function. **This function works as a scoring
> system that ranks all possible portfolio options based on their risk and return characteristics.
> Each potential glide path that is evaluated is given a utility score, and the glide path with the
> highest score** (the one that strikes the optimal balance between expected return and risk) **is
> the best solution for the investor's preferences, circumstances, and goal.**»

**Цель модели (с. 4, дословно):**

> «The main objective behind life-cycle investing and the VLCM is to maximize the expected lifetime
> utility of spending and wealth.»
> «the VLCM generates optimal glide paths by assessing the trade-offs between the expected (median)
> lifetime spending that can be funded from a portfolio and uncertainty about that spending due to
> market risk. The model uses an optimization algorithm to evaluate this trade-off among potential
> glide paths and selects the glide path that offers the best balance between level and volatility
> of lifetime spending.»

**Четыре набора входов (с. 5, дословно):** (1) Investor goal and investment horizon; (2) Asset
class return projections from VCMM; (3) Investor circumstances such as savings rate, length of
accumulation period, additional sources of income or assets for funding the goal, and consumption
horizons; (4) Investor preferences such as risk aversion, shortfall risk aversion, loss aversion,
and preference for timing of spending.

**Выходные метрики (Fig. 1, с. 6, дословно):** «Simulated wealth distributions through time ·
Simulated consumption distributions through time · Risk metrics such as portfolio return
volatility, consumption volatility, and wealth volatility · **Probability of success, given a
goal** · Potential benefit of customization (certainty fee equivalent)…»
Симуляции: «Distribution of return outcomes from VCMM are derived from **10,000 simulations** for
each modeled asset class. Simulations as of December 31, 2024.»

**Горизонт нерейтайрмент-целей (с. 7, дословно):** «nonretirement goals, which tend to have an
intermediate horizon, **such as 5 to 30 years**.»

🔴 **Измеренный ноль:** в полном перечне входов VLCM (Fig. 1, с. 6 — 15 позиций для retirement,
4 для nonretirement, 2 поведенческих и 2 рациональных предпочтения, 9 классов активов) **долга,
кредитов и обязательств домохозяйства нет ни одной строкой**. Ближайшее — «External cash flows».

**Мой вывод:** VLCM — прямой структурный аналог нашего ядра в инвестиционном домене: перебор
допустимых альтернатив (glide paths вместо 66 сплитов), скоринг каждой одной свёрткой, выбор
максимума, риск-предпочтения как параметры функции. Лучший из найденных аргументов, что
конструкция «перебор + свёртка + профиль весов» методологически законна. Разница: у них
утилитарная функция с теоретическим обоснованием (expected lifetime utility), у нас SAW —
линейная свёртка нормированных критериев, которой этот статус не даётся автоматически.

### 6.4. Schwab Intelligent Portfolios — НЕ ЗАКРЫТО

`https://intelligent.schwab.com/page/goal` вернул **301** на `https://www.schwab.com/intelligent-portfolios`;
редирект не пройден (бюджет). По сниппетам Goal Tracker раскрывает три состояния («on target»,
«at risk», «off target») и «long-term expected return estimates and simulations», но **пороги
состояний не проверены по первоисточнику** и потому как факт не заносятся.

---

## 7. СЛЕДСТВИЯ ДЛЯ FINPILOT

> Раздел дописан ведущей вахтой 09.09.2026 после обрыва агента по лимиту аккаунта.
> Опирается ТОЛЬКО на разделы 1-6 этого файла. Где вывод мой, а не источника, — сказано прямо.

### 7.1. 🔴 Опровергнуто: постановка задачи «долг + цели в одной оптимизации» НЕ нова

**Прочитано (§3.1).** Alaluf et al. (2024), arXiv:2403.06011, Princeton ORFE: «how to allocate
income in order to achieve several competing financial goals», где среди целей прямо названы
«paying out loans», а вектор `π_t` — доли дохода по целям. Это наша задача, поставленная
и решённая.

**Что это ломает.** Формулировка канона `docs/novelty_statement.md` (§20.3 первичного файла
темы 11) утверждала, что постановка задачи распределения свободного потока как выбора
на множестве альтернатив «не раскрыта ни в одном публично доступном источнике». В части
**постановки** это теперь неверно, и правится в каноне немедленно.

**Что устояло — зазоры, названные по прочитанному тексту, а не по догадке:**

| Элемент | Princeton 2403.06011 | FINPILOT |
|---|---|---|
| Метод | policy gradient, model-free RL | детерминированный перебор 66 альтернатив + SAW |
| Объяснимость | политика нейросети, вклад цели невосстановим | вклад каждого критерия виден явно |
| Ограничение платёжеспособности | нет | ПДН ≤ 0.40, регуляторный порог ЦБ |
| Резерв | одна из целей наравне с прочими | жёсткий инвариант допустимости |
| Метрика | ожидаемая полезность | + вероятностный прогноз последствий |
| Юрисдикция | 401K/IRA, налоговый контур США | РФ |

🔴 **Честная новая формулировка:** новизна не в постановке и не в том, что мы «первые
объединяем долг и цели», а в **детерминированном объяснимом решении задачи, которую
решают чёрным ящиком, с жёсткими регуляторными и ликвидностными инвариантами**.

### 7.2. 🟢 Контрпример против «водопада» бьёт мимо нас — но это надо доказать тестом

**Прочитано (§3.1).** Princeton доказывает субоптимальность waterfall: доход $1000/мес,
Goal 1 — $1000 под 0% с приоритетом p₁ = 1000, Goal 2 — $1 000 000/(1+r) под r = 0.001
с p₂ = 1. Водопад гасит Goal 1 первым, долг Goal 2 растёт на 1000 в месяц, и «the user will
never be able to pay down Goal 2».

🔴 **Мой вывод, требующий проверки.** Их водопад упорядочен по **приоритету пользователя**
(`p^i`, «urgency»). Наш Avalanche (§10.3-10.4 `docs/math_model.md`) упорядочен **по ставке**:
`O^target` ранжируется по убыванию `r_k`. В их же контрпримере наш порядок дал бы Goal 2
(r = 0.001) приоритет над Goal 1 (r = 0) — то есть верный ответ. Плюс верхний уровень у нас
вообще не водопад: доли `(x_d, x_g, x_r)` берутся перебором 66 альтернатив, а не
последовательным насыщением.

**Но это рассуждение, а не измерение.** Контрпример конкретен и воспроизводим — он обязан
стать тестом. Задача заведена в ROADMAP: прогнать портрет из Appendix A через наше ядро
и зафиксировать результат. Если ядро ведёт себя верно — это сильный аргумент в защиту метода,
подтверждённый чужим контрпримером. Если нет — это дефект, найденный до запуска.

### 7.3. 🔴 Метрика обеспеченности целей St — проверить на дефект бинарного опциона

**Прочитано (§2.2).** Максимизация `P(W_T ≥ G)` эквивалентна покупке digital option
(Browne, 1999): функционал `E[1{W_T ≥ G}]` имеет **нулевую чувствительность к глубине
провала** — «промахнуться на рубль» и «потерять всё» неразличимы. Независимо подтверждено
Estrada (§2.1) и, по сниппету, Kitces (§2.3, чтением не подтверждено).

🔴 **Прямой вопрос к нашей модели, ответа на который в этом файле нет:** критерий `St`
(обеспеченность целей) — это доля покрытия или порог достижения? Если где-то в ядре
решение принимается по признаку «цель достигнута / не достигнута», мы наследуем ровно этот
дефект. Проверяется чтением §11.4 и формулы (8) канона; заведено в ROADMAP.

**Готовый ответ литературы, если дефект найдётся:** Брюнель (§1.6) кодирует важность цели
**не весом в свёртке, а требуемой вероятностью достижения** (Needs 90-95%, Dreams 50-60%).
Это альтернатива нашему `w_S`, а не дополнение к нему — принимать её надо осознанно.

### 7.4. 🟢 Наша теоретическая опора названа неверно — и в файле есть верная

**Прочитано (§4.3).** Дейтон о Carroll (1997): ликвидностно ограниченные домохозяйства
сглаживают потребление «not over the whole life-cycle, but over much shorter periods of a few
years at a time» — «high-frequency» smoothing против «life-cycle frequency» Модильяни.

**Следствие для текстов.** Ссылаться на Модильяни-Мертона как на опору для горизонта 1-5 лет
некорректно: их рамка — про десятилетия и про детачмент потребления от дохода, а наше ядро
работает ровно там, где этот детачмент не выполняется. Корректная опора — **buffer-stock
ветка (Carroll 1997, Deaton 1991, Gourinchas-Parker 2002)**. Это усиление, а не уступка:
ветка описывает именно нашего пользователя.

### 7.5. 🟢 Ответ критикам «GBI хуже единой оптимизации» — измеренный

**Прочитано (§5.1).** Das, Markowitz, Scheid, Statman (2010): при запрете коротких продаж
потеря эффективности от разбиения по ментальным счетам — **12 базисных пунктов** на их
примере, и «this loss is small compared to the loss that occurs from investors inaccurately
specifying their risk aversions».

**Следствие.** Возражение «разбиение по счетам теряет диверсификацию» отвечается числом,
а не риторикой: цена разбиения меньше цены ошибки измерения риск-аверсии, а в рознице
предпочтения измеряются плохо всегда. Пригодно для защиты и для инвесторских вопросов.

### 7.6. Что НЕ подтвердилось и остаётся открытым

- Kitces (§2.3) — 403 по обоим каналам, цитаты только из сниппета. Содержательно раздел
  на нём не висит (Estrada подтверждает независимо), но как ссылку использовать нельзя.
- Browne (1999) и Föllmer-Leukert — первоисточники не открывались, связь помечена как вывод.
- Deguest-Martellini-Milhau: utility для essential/aspirational НЕ добыта, книга закрыта.
- Schwab (§6.4) не закрыт; §3.2 — четыре работы найдены и не прочитаны, включая MetaRL
  (arXiv:2605.02300) и JBF 2021 за пейволлом.

🔴 **Первым делом при возобновлении темы: arXiv:2605.02300 и GBWM_RL2.pdf** — это ближайшие
соседи находки §3.1, и именно они могут сузить зазоры из таблицы §7.1.

---

## 8. ЧТО ОСТАЛОСЬ НЕДОСТУПНЫМ (промежуточно)

- SSRN (403), EDHEC (403), nobelprize.org (403), MIT DSpace (405), HBR (пейволл),
  **kitces.com (403 и на WebFetch, и на curl с браузерным UA — обе страницы)**.
- Schwab Goal Tracker — редирект не пройден.
- Не открыты первоисточники Browne (1999) и Föllmer–Leukert; связанные утверждения помечены.
- Deguest–Martellini–Milhau: полного текста книги нет в открытом доступе, utility для
  essential/aspirational НЕ добыта.
- Найдены, но не прочитаны: `GBWM_RL2.pdf` (Das & Ostrov, multi-goal RL), arXiv 2105.07915,
  arXiv 2510.21650, arXiv 2605.02300 (MetaRL), JBF 2021 (paywall).
- Нулевые результаты подагента: запрос «goals-based wealth management debt repayment
  optimization» — выдача целиком консультантская (EP Wealth, US Bank, Ameriprise), академического
  ноль; «optimal allocation between debt repayment and saving household model» — по существу
  почти ноль.

---

## ДОБОР Г31.5 — отказ адреса (17.09.2026)

**Каналы (замер 17.09.2026):** `nobelprize.org` прямой `curl -skL` с UA **200** · `r.jina.ai` без UA **200** · NBER прямой **200** · MIT DSpace 7 REST `discover/search/objects` **200** → `items/…/bundles` **200** → `bundles/…/bitstreams` **200** → `bitstreams/…/content` **200** · `pdftoppm` + `tesseract` (`eng`) в системе.

В файле нет доборов после §8 «ЧТО ОСТАЛОСЬ НЕДОСТУПНЫМ» (стр. 837–846); последние упоминания трёх пунктов — стр. 28, 32–33, 839 («nobelprize.org (403), MIT DSpace (405)»). В `gbi_tails_closed_2026-09-10.md` эти пункты не перепроверялись (`grep` на Merton/nobelprize/63980 — ноль). Все три — класс Г31.5.

### Г31.5-G1. 🟢 Нобелевская лекция Модильяни (1985) — ПОЛНЫЙ ТЕКСТ ДОБЫТ по тому же адресу

- `https://www.nobelprize.org/uploads/2018/06/modigliani-lecture.pdf` прямым `curl -skL` с браузерным UA — **HTTP 200, 251 201 б, `application/pdf`**, 21 стр., sha256 `20dfc67237b8d413ff51e623a6610dfcf123868a32941ff6387cf2d6a3e68f05`, `pdftotext` → 1 081 строка. Контрольно `r.jina.ai` без UA — **200, 68 659 б**. Отказ «403» был отказом одного захода (`WebFetch`), не адреса.
- Заголовок: **«Life Cycle, Individual Thrift and the Wealth of Nations»**, Franco Modigliani, Sloan School of Management, MIT.

**ДОСЛОВНО (разд. «(1) Utility maximization and the role of Life Resources»):**

> «The hypothesis of utility maximization (and perfect markets) has, all by itself, one very powerful implication - the resources that a representative consumer allocates to consumption at any age, it, will depend only on his life resources (the present value of labor income plus bequests received, if any) and not at all on income accruing currently. When combined with the self evident proposition that the representative consumer will choose to consume at a reasonably stable rate, close to his anticipated average life consumption, we can reach one conclusion fundamental for an understanding of individual saving behavior, namely that the size of saving over short periods of time, like a year, will be swayed by the extent to which current income departs from average life resources.»

> «In MB-C and in the first two parts of the MB-A, we made a number of simplifying, stylized, assumptions … These were: (1) opportunities: income constant until retirement, zero thereafter; zero interest rate; and (2) preferences: constant consumption over life, no bequests. … Because the retirement span follows the earning span, consumption smoothing leads to a humped-shaped age path of wealth holding…»

**Выжимка.** Пересказ Дейтона в §4.1 первоисточником подтверждён. Уточнение, важное для §4.3 («ссылаться на Модильяни–Мертона как на опору для горизонта 1–5 лет некорректно»): сам Модильяни формулирует базовую модель при **нулевой ставке, постоянном доходе до пенсии и полном рынке** — это модель распределения на горизонте жизни, а краткосрочные сбережения в ней — лишь отклонение текущего дохода от «life resources». Вывод §4.3 первоисточником усиливается, не меняется.

### Г31.5-G2. 🟢 Merton «Optimum Consumption and Portfolio Rules in a Continuous-time Model» — ПОЛНЫЙ ТЕКСТ ДОБЫТ через DSpace 7 REST

- Записанный отказ: `dspace.mit.edu/bitstream/handle/1721.1/63980/…pdf?sequence=1` — **405** (старый адрес DSpace 6, после миграции MIT на DSpace 7 не обслуживается).
- Цепочка DSpace 7 (тот же приём, что добыл Abadie 2021):
  1. `GET https://dspace.mit.edu/server/api/discover/search/objects?query=handle:1721.1/63980` — **200, 19 685 б** → item `45b93de3-551e-475d-9d42-4724ecd84484`, «Optimum consumption and portfolio rules in a continuous-time model,»;
  2. `…/core/items/45b93de3-…/bundles` — **200, 5 288 б** → bundle `ORIGINAL` `96a3b10b-01c0-49e9-a3a1-117a211e7016`;
  3. `…/core/bundles/96a3b10b-…/bitstreams` — **200, 2 112 б** → `62450091-e2fd-4838-86e3-b049a0993ae4` `optimumconsumpti00mert.pdf`, 2 302 235 б;
  4. `…/core/bitstreams/62450091-…/content` — **200, 2 302 235 б, `application/pdf`**, 54 стр., sha256 `af55d619bb0b2f2cf87e3c4c847e8541d896ad9c83b903d96a1ad2b531b85c81`; OCR-слой есть, `pdftotext` → 6 254 строки.
- 🔴 **Версия:** MIT Dept. of Economics Working Paper **No. 58, August 1970** (скан Internet Archive 2011) — рабочая версия статьи *Journal of Economic Theory* 3(4), 1971. Цитировать как WP с пометкой.

**ДОСЛОВНО (введение, с. 1–2):**

> «The present paper extends these results for more general utility functions, price behavior assumptions, and for Income generated also from non-capital gains sources. It is shown that if the "geometric Brownian motion" hypothesis is accepted, then a general "Separation" or "mutual fund" theorem can be proved such that, in this model, the classical Tobin mean-variance rules hold without the objectionable assumptions of quadratic utility or of normality of distributions for prices. … If the further assumption is made that the utility function of the individual is a member of the family of utility functions called the "HARA" family, explicit solutions for the optimal consumption and portfolio rules are derived and a number of theorems proved.»

> (разд. о HARA, после (48)–(49)) «The manifest characteristic of (48) and (49) is that the demand functions are linear in wealth. It will be shown that the HARA family is the only class of concave utility functions which imply linear solutions.»

(OCR исправлен в двух очевидных местах: «Brownlan» → «Brownian», «KARA» → «HARA».)

**Выжимка.** Явные решения — только при логнормальных ценах и HARA-полезности; линейность спроса по богатству — **необходимое и достаточное** свойство HARA. Для нас это фиксирует границу переносимости: у нас нет ни стохастических цен активов, ни оптимизации полезности по времени — перенос «правил Мертона» на распределение свободного потока недопустим, что совпадает с выводом §4.3.

### Г31.5-G3. 🟢 Bodie, Merton & Samuelson (1992), NBER w3954 — ПОЛНЫЙ ТЕКСТ ДОБЫТ (скан, OCR)

- Запись стр. 28: «абстракт дословно; полного PDF в открытом доступе нет». Проверялась только страница `nber.org/papers/w3954`.
- `https://www.nber.org/system/files/working_papers/w3954/w3954.pdf` прямым `curl -skL` — **HTTP 200, 1 117 822 б, `application/pdf`**, 41 стр., sha256 `ee65cf593723352ffad55ea042518330c15de6ffb5170dbb83ebddabffd1e37d`. Текстового слоя нет (`pdftotext` → 0 строк), страницы 20–30 распознаны `tesseract -l eng` при 200 dpi. Цитаты ниже — OCR, сверены по смыслу, опечатки распознавания не правились кроме очевидных.

**ДОСЛОВНО (OCR, с. 20–22 рукописи):**

> «The wealth effect suggests that in "normal" circumstances, the individual with flexible labor will invest a greater proportion of his financial wealth in the risky asset than his counterpart whose labor is fixed. However, it is worth making the obvious observation: An individual with flexible labor must actually want to exercise this option ex post…»

> «…the individual borrows at the risk-free rate to finance his investment in the risky asset. The pure wealth effect of the individual's riskless human capital causes a significant rebalancing of his investment portfolio. As the example illustrates, the individual's degree of leverage is greatest early in the life-cycle and when his labor supply is flexible. … The model also predicts that households with greater labor flexibility will tend to have riskier investment portfolios.»

> «For Part b, the proportional increase in wealth is 24%. This is to say that on top of his initial lifetime wealth ($730,000), the individual would need an additional $175,000 to bring him the same level of utility as he enjoys with flexible labor.»

> «Remark 4. Similar dynamic results apply in the broader case of isoelastic utility. … The difference in investment behavior between the fixed and flexible labor cases is greatest early in the life-cycle when the individual's stock of human capital is greatest. Moreover, the welfare advantage of labor flexibility is significant for typical numerical examples. **All of this applies when the wage does not vary stochastically over time.**»

**Выжимка.** 🔴 Уточнение к выводу §4.4 («риск-профиль должен зависеть от устойчивости дохода»): основной результат BMS получен для **детерминированной зарплаты** — «риск» в нём создаёт гибкость предложения труда, а не неустойчивость дохода; человеческий капитал в базовой модели **безрисковый** и потому работает как облигация, позволяющая больше риска. Стохастическая зарплата — отдельный разд. (с. 23 и далее рукописи, распознан начальный фрагмент с уравнением Беллмана). Значит, опираться на BMS для тезиса «нестабильный доход → меньше риска» напрямую нельзя: базовая модель говорит о другом механизме. Гипотеза §4.4 остаётся гипотезой, её обоснование нужно брать из ветки стохастической зарплаты (здесь не разбиралась — см. ЗАДОЛЖЕННОСТЬ).

## ИТОГ Г31.5 — goal_based_investing_lifecycle

3 кандидата, **3 закрыты полным текстом:**

| Пункт | Записанный отказ (один адрес) | Чем закрыт |
|---|---|---|
| Модильяни, Нобелевская лекция | `nobelprize.org` 403 (`WebFetch`) | **прямой `curl -skL` с UA по тому же адресу** (200, 251 201 б); контрольно `r.jina.ai` 200 |
| Merton WP 58 (1970) / JET 1971 | `dspace.mit.edu/bitstream/handle/…` 405 | **DSpace 7 REST**, 4 шага, все 200 |
| Bodie–Merton–Samuelson 1992 | проверялась только страница `nber.org/papers/w3954` | **прямой `curl` по `system/files/working_papers/w3954/w3954.pdf`** (200) + OCR `tesseract` |

🔴 **Что меняет обоснование (канон не трогается):** тезис §4.4 «гибкость дохода → больше риска ex ante» в базовой модели BMS получен при **нестохастической зарплате** и безрисковом человеческом капитале; как опору для связки «устойчивость дохода ↔ риск-профиль» его цитировать без оговорки нельзя. Выводы §4.1 и §4.3 первоисточниками подтверждены.

**ЗАДОЛЖЕННОСТЬ по файлу:** OCR разд. BMS о стохастической зарплате (с. 23+ рукописи, страницы PDF 29–41) не выполнялся — нужен, если §4.4 пойдёт в обоснование. HBR Merton 2014 (пейволл) и EDHEC (регистрационная стена, см. `gbi_tails_closed`) — не класс Г31.5, не брались.
