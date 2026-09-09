# Тема 13 — Математика goal-based investing (GBI) и life-cycle подхода

**Дата:** 09.09.2026
**Статус файла:** ⏳ пишется по ходу работы (правило «сырьё в файл ДО ответа»)
**Метод:** lead-agent + один подагент, живые источники. Реконструкция по памяти модели
в этот файл не попадает; где источник не открылся — явная пометка «канал мёртв».

> 🔴 **Ограничение инструментария этого прогона, честно.** У ведущего агента в этой
> сессии НЕТ тула `Bash`, то есть нет ни `curl`, ни `pdftotext`. Обход «PDF нечитаем»
> сработал по другому каналу: `WebFetch` на PDF сохраняет бинарник на диск и печатает
> путь, а тул `Read` умеет читать PDF постранично (параметр `pages`) — включая PDF,
> собранные из картинок, где `pdftotext` вернул бы пустоту. Этим способом в прогоне
> взяты ЧЕТЫРЕ полнотекстовых первоисточника. Канал рабочий, записать в приёмы.

---

## 0. СОСТОЯНИЕ КАНАЛОВ (ведущий агент)

| Источник | URL | Результат |
|---|---|---|
| Das, Ostrov, Radhakrishnan, Srivastav (2018), JOIM | https://srdas.github.io/Papers/GBWM.pdf | 🟢 **открыт полностью** (3.5 МБ, прочитаны с. 1–12) |
| Deaton, «Franco Modigliani and the Life Cycle Theory of Consumption» (2005) | https://www.princeton.edu/~deaton/downloads/romelecture.pdf | 🟢 **открыт полностью** (58 КБ, прочитаны с. 1–6 и 12–17) |
| UBS, «Liquidity. Longevity. Legacy. A purpose-driven approach to wealth management» | https://www.ubs.com/content/dam/assets/wm/global/doc/liquidity-longevity-legacy.pdf | 🟢 **открыт** (1.6 МБ, PDF из картинок; прочитаны с. 2–7 через `Read`) |
| Vanguard, «Vanguard's Life-Cycle Investing Model (VLCM)», май 2025 | https://corporate.vanguard.com/content/dam/corp/research/pdf/vanguard_life_cycle_investing_model_vlcm_a_general_portfolio_framework_for_goals_based_investing.pdf | 🟢 **открыт** (776 КБ, прочитаны с. 3–8) |
| Betterment, «Goal Projection and Advice Disclosure» | https://www.betterment.com/resources/projection-methodology | 🟢 **открыт полностью** (HTML) |
| NBER w3954, Bodie–Merton–Samuelson (1992) | https://www.nber.org/papers/w3954 | 🟢 открыт, абстракт дословно; полного PDF в свободном доступе нет |
| SSRN, Das–Markowitz–Scheid–Statman (2010) | https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1166899 | 🔴 **403 Forbidden** |
| EDHEC, «Comprehensive Investment Framework For Goals-Based Wealth Management» | https://climateinstitute.edhec.edu/publications/introducing-comprehensive-investment-framework-goals-based-wealth-management | 🔴 **403 Forbidden** |
| HBR, Merton (2014), «The Crisis in Retirement Planning» | https://hbr.org/2014/07/the-crisis-in-retirement-planning | 🟡 **пейволл**: только заголовок, биография, первый абзац. Содержательных цитат НЕ взято |
| Нобелевская лекция Модильяни (1985) | https://www.nobelprize.org/uploads/2018/06/modigliani-lecture.pdf | 🔴 **403 Forbidden** |
| MIT DSpace, Merton (1971) | https://dspace.mit.edu/bitstream/handle/1721.1/63980/optimumconsumpti00mert.pdf?sequence=1 | 🔴 **405 Method Not Allowed** |
| Schwab Intelligent Portfolios, Goal Tracker | https://intelligent.schwab.com/page/goal | 🟡 **301** на https://www.schwab.com/intelligent-portfolios, редирект не пройден (бюджет) |
| srdas.github.io (корень) | https://srdas.github.io/ | 🟡 открыт, списка статей нет |

*(состояние каналов подагента — в его собственном разделе)*

---

## 1. Каноническая формулировка GBI — ПРОЧИТАНО В ИСТОЧНИКЕ

### 1.1. Das, Ostrov, Radhakrishnan, Srivastav (2018), «A New Approach to Goals-Based Wealth Management», *Journal of Investment Management*, Vol. 16, No. 3, pp. 1–27

URL полного текста: https://srdas.github.io/Papers/GBWM.pdf

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
- Thaler (1985, 1999) — mental accounting theory: «people treat money with different
  risk–return preferences, depending on what use the money is to be put to».
- Shefrin & Statman (1985) — disposition effect; (2000) — behavioral portfolio theory,
  **BPT-MA** (multiple accounts) против **BPT-SA** (single account). Дословно: «investors
  behave as if they have multiple mental accounts… Each mental account portfolio has
  varying levels of aspiration, depending on the goals for the mental account.»
- Roy (1952) — safety-first: «Rather than trade-off risk versus return, investors
  trade-off goals versus safety, see Roy (1952). This leads to normatively different
  statements of the portfolio problem than in the mean–variance theory of Markowitz (1952).»
- **Das et al. (2010)** — «showed that, under specific technical assumptions, there is
  a mathematical linkage between mental accounting theory (MAT) and mean–variance theory
  (MVT), arguing that there is a mapping from a goals-based portfolio to a portfolio on
  the mean–variance Efficient Frontier. This mathematical reconcilement showed that GBWM
  is supported by MVT».
- **Nevins (2004)** — «contended that traditional investment planning fails to recognize
  investor's behavioral preferences and biases, resulting in suboptimal portfolio
  performance… traditional risk measures do not fully capture market behavior and are
  of limited relevance to investors.»
- **Zwecher (2010)** — bucketing (mental accounting) подход к пенсионному портфелю.
- **Brunel (2015)** — «discussed the equal importance of two goals for an investor: being
  able to avoid nightmares while realizing dreams. Brunel's work focussed on demonstrating
  how goals-based wealth management can be achieved across multiple time horizons for
  multiple life goals. He also suggested how to map the language investors use in
  describing the importance of dreams or the severity of nightmares into acceptable
  probabilities that the investor will realize such dreams or avoid such nightmares.»
- Lopes (1987) — aspiration; Kahneman & Tversky (1979) — prospect theory.

### 1.2. Девять свойств GBWM (с. 4, 7, 8) — дословно

> **Property 1: Clarity.** The financial goals of the investor should be clear.
> **Property 2: Customization.** The advice given to the investors should be individualized
> to cater to their specific goals.
> **Property 3: Risk Specificity.** The probability of the investors attaining (or not
> attaining) their goals should always be clear.
> **Property 4: Risk Compliance.** The advice given to the investor should take into
> account these probabilities.
> **Property 5: Client-centered Communication.** Clients should be asked for information
> about their goals in terms that are clear to them, such as investment time frames,
> desired dollar amounts at the end of these time frames, and desired probabilities of
> attaining these dollar amounts.
> **Property 6: Goal/State Specificity.** Advice discussed with the investors should be
> based on information regarding the investor's goals and the overall state of their
> portfolio, not, in general, the portfolio's individual investment components.
> **Property 7: Portfolio Efficiency.** Investors should always be advised to invest in
> a portfolio that is on the Efficient Frontier.
> **Property 8: State Dependency.** The advice given to investors (i.e., the specific
> location on the Efficient Frontier) should be affected by market changes and easy to
> understand investor preferences, both in bull and bear markets.
> **Property 9: Rules for Rebalancing.** The investor's portfolio should be able to be
> updated automatically at regular intervals… and manually, whenever the investor wishes.

### 1.3. Восемь входных величин от клиента (с. 8, дословно)

> (1) Their time frame (Investment Horizon).
> (2) The size of their initial investment (Initial Wealth).
> (3) Their goal wealth (Target Wealth).
> (4) The probability they would like to maintain of reaching their goal wealth (Target Probability).
> (5) The wealth they would not want to end below (Loss Threshold Wealth).
> (6) The probability they would like to maintain of ending above the loss threshold (Loss Threshold Probability).
> (7) Their investment preferences in good states, and
> (8) Their investment preferences in bad states.

**Мой вывод:** целевая конструкция — **не одна метрика, а пара «цель + порог потерь»,
каждая со своей вероятностью**. Две границы, а не одна: «instead of one reference point,
we have two: (i) a Target Wealth on the spectrum of upside outcomes and (ii) a Threshold
Wealth for losses on the downside» (с. 7).

### 1.4. Математика (с. 9, 12) — дословно

> W̃(t) = W(0)·e^((μ − σ²/2)t + σ√t·Z),  (1) — where Z is a standard normal random variable.

> μ = ½σ² + (z₀/√t)·σ + (1/t)·ln(W(t)/W(0)),  (2)
> where z₀ is defined so that the Target Probability equals Φ(z₀), with Φ(z) being the
> cumulative distribution function (CDF) for a standard normal random variable. Note that
> Equation (2) defines an upward curving (i.e., convex) parabolic relationship between the
> expected return μ and the volatility σ.

> «Any portfolio lying on or above this parabola in the (σ, μ) (i.e., risk–return) plane
> will satisfy the investor's stated goals, therefore, the region on or above this parabola
> is called the **Goal Region**… If we replace z₀ with a generic value z in the above
> equation, we call the resulting parabola a **Goal Probability Level Curve** (GPLC)…»

При σ = 0:  μ = (1/t)·ln(W(t)/W(0)),  (3) — regardless of the value of z.

Три строительных блока (с. 9): Goal Region + GPLC, Loss Threshold Curve, Efficient Frontier.
Эффективная граница: σ = √(aμ² + bμ + c),  (4) — гипербола.
**Loss Threshold Curve** строится той же формулой (2) с подстановкой Loss Threshold Wealth.
Итог задачи (с. 12, дословно):

> «we would like to have a portfolio in the (σ, μ) plane that lies in the intersection of
> the Goal Region and the region on or above the Loss Threshold Curve.»

🔴 **Практическое ограничение метрики, названное самими авторами (с. 11, дословно):**

> «The Loss Threshold Probability is always higher than the Target Probability, however,
> as a rule of thumb, values exceeding 99% may be problematic, because tail events above
> this level are hard to model accurately.»

### 1.5. «Меньше волатильность = безопаснее» — опровергнуто (с. 9, дословно)

> «We will show, for example, that the traditional notion of gravitating toward the least
> volatile portfolio in this interval generally does not correspond to the safest choice
> for the investor. Again, this is because the notion of "safest" is defined by the
> probability of attaining their goal, whereas traditionally it has been defined without
> this goals-based perspective.»

### 1.6. Таблица Брюнеля «цель → вероятность» (Table 1, с. 6, дословно)

| Realize | Avoid | Success probability (%) |
|---|---|---|
| Dreams | Concerns | 50, 55, 60 |
| Wishes | Worries | 65, 70, 75 |
| Wants | Fears | 80, 85 |
| Needs | Nightmares | 90, 95 |

Подпись: «Brunel's Goal-Probability table can be used to classify investor goals into
different probability values, which can then be used in our GBWM framework.»

🔴 **Прямой ответ на вопрос о приоритизации: в практической ветке GBI важность цели
кодируется НЕ весом в свёртке, а требуемой вероятностью достижения.** Needs → 90–95 %,
Dreams → 50–60 %. Порядковая шкала важности отображается в кардинальную шкалу вероятностей.

### 1.7. Критика текущей практики советников (с. 7, дословно, выборочно)

> «(4) Underfunded portfolios are often ignored, resonating with an often heard criticism
> in the wealth and asset management industry that financial advisors are "doctors who
> treat only healthy patients."
> (5) Critical goals are often over-funded, consuming too much of the investor's principal.
> (6) Periodically, portfolios are adjusted to bring them back to a target asset allocation,
> regardless of market conditions.
> (7) While advisors understand the concept and intuitions of goals-based wealth management,
> they do not have a framework to analyze its implications for portfolio construction.»

Четыре типовых «псевдо-goal-based» подхода советников разобраны на с. 4–5, и для каждого
указано, каким свойствам он НЕ удовлетворяет. Подход (4) — expense management («advise
investors on how to cut back expenses or streamline monthly budgets, incorporating present
and future cash flows, so that investor can achieve certain savings goals») — выведен
за рамки GBWM:

> «the objective of expense management is different from the objective of goals-based
> wealth management, so it is unsurprising that this approach meets only the first two
> properties, but not the third or fourth.»

🔴 **Неприятно для нас:** FINPILOT по этой классификации попадает в подход (4), который
авторы НЕ считают goal-based, потому что он не оперирует вероятностями достижения. §7.

### 1.8. Цифры опроса (с. 5–6, дословно)

> «72% of clients view success based on the overall performance of their portfolio, not
> the performance of individual investments, whereas only 51% of advisors believe that
> their clients view success primarily based on overall portfolio performance…»
> «Talking with a client in goals-based probability language such as "Based on your current
> strategy, there is a 90% chance that you will achieve your investment goal." is very clear
> to 49% of clients and either very clear or quite clear to 92% of clients, whereas
> individual investment-oriented language like "Your U.S. equity investment has been
> outperforming its benchmark index." is only very clear to 29% of clients and either very
> clear or quite clear to 71% of clients.»

---

## 4. Life-cycle / consumption smoothing — ПРОЧИТАНО В ИСТОЧНИКЕ

Источник: Angus Deaton, «Franco Modigliani and the Life Cycle Theory of Consumption»,
Convegno Internazionale Franco Modigliani, Accademia Nazionale dei Lincei, Рим, 17–18.02.2005.
https://www.princeton.edu/~deaton/downloads/romelecture.pdf
(Дейтон — нобелевский лауреат по экономике потребления; авторитетное изложение Модильяни,
но не сам Модильяни. Первоисточники Modigliani–Brumberg 1954/1980 в прогоне не открывались.)

### 4.1. Формулировка гипотезы жизненного цикла (SUMMARY, дословно)

> «In the early 1950s, Franco Modigliani and his student Richard Brumberg worked out a
> theory of spending based on the idea that people make intelligent choices about how much
> they want to spend at each age, limited only by the resources available over their lives.
> By building up and running down assets, working people can make provision for their
> retirement, and more generally, tailor their consumption patterns to their needs at
> different ages, **independently of their incomes at each age**.»

Происхождение (с. 4): «Life-cycle theory makes its first appearance in two papers that
Modigliani wrote in the early 1950s with a graduate student, Richard Brumberg, Modigliani
and Brumberg (1954) and Modigliani and Brumberg (1980).»

### 4.2. Merton (1969) внутри этой рамки (с. 14, дословно)

> «Theoretical results by Robert Merton (1969) provided further support; Merton showed that
> if risk is confined to financial assets, the basic rule for life-cycle consumers of
> setting consumption proportional to assets, remains true when utility maximization was
> replaced by expected utility maximization. **Of course, that leaves a hole in the
> argument — earnings themselves are uncertain — and that hole turns out to be important,
> at least in some cases.**»

🔴 Это ровно наш случай: доход домохозяйства неопределён, и SES+Монте-Карло — попытка
закрыть именно эту дыру.

### 4.3. 🔴 Carroll (1997), buffer-stock: почему long-horizon рамка НЕ переносится на короткий горизонт (с. 14–15, дословно)

> «Work on precautionary saving, particularly by Carroll (1997), has shown that people with
> uncertain future earnings who are sufficiently prudent **will never borrow**, if there is
> the possibility, however remote, that they will not earn enough to be able to repay their
> debts. If such people expect their earnings to grow over time, they will nevertheless keep
> their consumption within their current incomes, thus inducing a close articulation, or
> "tracking," between consumption and income. In this case, although people are maximizing
> their expected lifetime utility, as postulated by the life-cycle theory under uncertainty,
> **their consumption is effectively constrained by their current incomes**. Such behavior is
> directly contrary to one of the central insights of the Modigliani model, that the profile
> of consumption can be detached from the profile of income…»

И прямо про горизонт (с. 15, дословно):

> «In these extreme precautionary or "liquidity constrained" accounts of saving, consumption
> is smoothed, **not over the whole life-cycle, but over much shorted periods of a few years
> at a time**, see again Carroll (1997) and Deaton (1991). In the literature, this is often
> referred to as **"high-frequency" smoothing of income**, as opposed to the "low frequency"
> or "life-cycle frequency" smoothing that was postulated by Modigliani and Brumberg.»

Примирение двух картин (с. 15, дословно):

> «it is the youngest families who are likely to want to borrow, but either cannot or are
> too prudent to do so, and are therefore more or less constrained by their current earnings,
> while those in middle-age behave in the traditional life-cycle way. That such a formulation
> is consistent both with expected utility maximization and with the survey data has been
> shown in an important paper by Pierre-Olivier Gourinchas and Jonathan Parker (2002).»

🔴 **Мой вывод — самый важный результат §4 для FINPILOT.** Литература сама разделяет два
режима: «life-cycle frequency» (десятилетия, Модильяни–Мертон) и **«high-frequency»
смягчение потока на горизонте нескольких лет при ликвидностном ограничении** (Carroll,
Deaton, Gourinchas–Parker). Наше ядро — распределение свободного потока при Rt≥0 и
ПДН≤0.40, горизонты от месяцев — живёт во ВТОРОМ режиме. Ссылаться в текстах проекта
на Модильяни–Мертона как на теоретическую опору для горизонта 1–5 лет **некорректно**;
корректная опора — buffer-stock / liquidity-constrained ветка.

### 4.4. Bodie, Merton, Samuelson (1992) — абстракт дословно

https://www.nber.org/papers/w3954 (NBER WP 3954; *Journal of Economic Dynamics and Control*,
16, 427–449, 1992)

> «This paper examines the effect of the labor-leisure choice on portfolio and consumption
> decisions over an individual's life cycle… **The ability to vary labor supply ex post
> induces the individual to assume greater risks in his investment portfolio ex ante.**
> The model explains why the young (enjoying greater labor flexibility over their working
> lives) may take greater investment risks than the old. It also offers an explanation as
> to why consumption spending is relatively "smooth" despite volatility in asset prices.
> Finally, the paper provides a compact method for valuing the risky cash flows associated
> with future wage income.»

**Мой вывод:** human capital как обоснование риск-профиля переносится лишь частично.
У нас риск-профиль — набор весов SAW, а не доля в рисковом активе; но логика «гибкость
дохода ex post → допустимость большего риска ex ante» обосновывает, почему риск-профиль
должен зависеть от устойчивости дохода, а не только от самоописания пользователя.
В модели v3.0.0 такой связи нет. Кандидат в гипотезы, не в требования.

### 4.5. Критика life-cycle рамки, названная самим Дейтоном (с. 15–17, дословно)

> «Perhaps the most fundamental challenge to the life-cycle model has been directed at its
> basic underlying assumption, that people make rational, consistent, intertemporal plans…»

> «Even commercial financial planners advise their clients about retirement planning
> according to rules and recommendations, such as target wealth to income ratios that, under
> some circumstances, are wildly inconsistent with life-cycle theory. **These commercial
> plans are not better than life-cycle plans, and can lead to disaster under some
> circumstances**, but they attest to the implausibility that individuals, who lack the
> resources and computer facilities of financial planners, do better in following life-cycle
> rules.»

> «One strand formalizes procrastination using the concept of "hyperbolic discounting,"
> David Laibson (1997) and Laibson and Christopher Harris (2001)… **Under hyperbolic
> discounting, people wait too long to get started on saving for retirement**… More
> generally, default options in saving plans matter, because people procrastinate on
> changing the default; Richard Thaler and Shlomo Benartzi (2004) have analyzed (and
> trade-marked) a plan called "Save more tomorrow™"…»

> «life-cycle theory captures some of the truth, even if it is clear that the details are wrong.»

**Мой вывод:** цитата «commercial plans… can lead to disaster» бьёт по классу продуктов
с эвристическими константами («3 оклада резерва», «порог 7 % APR» из патента Capital One),
но НЕ бьёт по конструкции с явной целевой функцией и ограничениями. Это аргумент в пользу
нашего подхода против рынка калькуляторов; держать под рукой в тексте о новизне.

---

## 6. Практика — ПРОЧИТАНО В ИСТОЧНИКЕ

### 6.1. 🔴 UBS Wealth Way (Liquidity. Longevity. Legacy.) — самая ценная находка прогона

Источник: UBS, «Liquidity. Longevity. Legacy. A purpose-driven approach to wealth
management», https://www.ubs.com/content/dam/assets/wm/global/doc/liquidity-longevity-legacy.pdf
(PDF собран из картинок; прочитан постранично через `Read`.)

**Определение подхода (с. 2, дословно):**

> «Every family's financial plan is unique, but most investment strategies are organized
> quite similarly. **Instead of using "risk tolerance" as the primary guiding factor**,
> our approach is built on the foundation of your financial objectives. The Liquidity.
> Longevity. Legacy. approach allocates family wealth into three strategies that we have
> designated the 3Ls…»

> «**Liquidity**: Assets in the Liquidity strategy are allocated to match expenditures in
> order to provide an automatic (or nearly automatic) and steady cash flows for the next
> 2 to 5 years…»
> «**Longevity**: The Longevity strategy is designed and sized to include all of the assets
> and resources the family plans to utilize for the remainder of their lifetimes…»
> «**Legacy**: … includes assets that are in excess of what the family members need to meet
> their own lifetime objectives…»

**Fig. 3 (с. 5) — теоретические опоры и метрики, дословно из таблицы:**

| | Liquidity | Longevity | Legacy |
|---|---|---|---|
| Purpose | Provide liquidity for near-term spending | Provide asset growth and appropriate risk hedging to meet lifetime goals | Growth of legacy assets |
| Investment approach | Asset-liability matching | Total wealth LDI | Taxable endowment |
| **Sizing** | **Next three years of cash flow** | Based on objectives, age | Surplus |
| **Risk assessment** | **Probability of success, funding ratio, surplus risk** | (то же) | Long-term risk-adjusted return |
| Intellectual Framework | Merton, Samuelson, Kahneman, Thaler, Waring, Sharpe 2.0 | (то же) | Markowitz, Sharpe 1.0, Swensen |

**Liability-driven investing — переопределение риска (с. 5, дословно):**

> «Instead of focusing on day-to-day volatility as the primary measure of risk, a
> liability-driven approach builds a portfolio optimized to help meet the investor's future
> liabilities. **Risk is redefined as not meeting those liabilities.**»

> «From a technical standpoint, what really matters in these situations is the surplus or
> deficit of the strategy — the assets minus the liabilities — and not the absolute level
> of assets or variance in the portfolio. Accordingly, **the objective function should shift
> from maximizing assets relative to portfolio volatility to a strategy that maximizes the
> surplus in context of the volatility of the surplus.**»

**UBS сам ссылается на аргумент 1/N (с. 5, дословно) — стык с закрытой темой 12:**

> «recent research indicates that a simple equal weighted approach outperforms as frequently
> as much more sophisticated MPT-based approaches. It turns out that the narrow focus on
> "optimizing portfolios" has not led to max outcomes for investors.»

**Горизонт как определяющий фактор (с. 6, дословно):**

> «No matter the "risk tolerance" of the individual, investing funds earmarked for a
> grandchild's college tuition in a moderate portfolio makes very little sense if the check
> is due at the bursar's office in six months but might be perfectly rational if college is
> still seven years away.»
> «Probability of loss in any asset or portfolio is dependent on time horizon, which means
> time horizon should have an impact on the appropriate investment portfolio.»

🔴 **ГЛАВНАЯ ЦИТАТА ПРОГОНА (с. 7, дословно). UBS называет НАШУ задачу как известный
дефект ментального учёта — и всё равно сознательно принимает сегментацию:**

> «mental accounting describes a tendency that leads people to segment their assets and
> spending goals into distinct parts and treat those parts differently without thinking of
> the whole. This proclivity can lead to suboptimal decision-making, **such as holding a
> credit card balance at a 15% interest rate when this could be paid off by an investment
> that yields 2%**. The 3L framework **takes advantage of this segmenting inclination** by
> separating assets to help meet specific spending objectives. The result is an intuitive
> investment strategy that creates a clear connection between assets and the objectives for
> those assets.»

**Мой вывод (важный для новизны):** размен «дорогой долг против низкодоходного актива»
у UBS назван прямым текстом, с числами 15 % против 2 % — но назван как **иллюстрация
ошибки клиента**, а не как задача, которую фреймворк решает. UBS фиксирует дефект и
сознательно строит продукт НА этом дефекте («takes advantage»), потому что сегментация
даёт поведенческую дисциплину. То есть в GBI-практике верхнего сегмента конфликт
«цель против долга» **осознан и намеренно оставлен нерешённым**. Это сильнее, чем «никто
не считает»: индустрия знает про размен и отказалась его считать в пользу удобства.
Формулировка новизны FINPILOT должна опираться именно на это, а не на «никто не додумался».

### 6.2. Betterment — ПРОЧИТАНО В ИСТОЧНИКЕ

https://www.betterment.com/resources/projection-methodology («Goal Projection and Advice Disclosure»)

> «The recommended monthly contributions estimate is based on **a 50% likelihood** of the
> portfolio value reaching the goal target at the end of the investment term for all
> investing goals, other than PRP goals.»

График: «one line shows the projected portfolio value under average market conditions»
(50-й перцентиль) и «The lighter, shaded region indicates the range within which there is
80% likelihood» (10-й–90-й перцентили).

Измеренные нули по этому документу: **метод расчёта (Монте-Карло или замкнутая форма)
не раскрыт**; **взаимодействие нескольких целей не описано вовсе**; **долг и обязательства
не упоминаются нигде** — модель оперирует активами, взносами и изъятиями.

🔴 **Мой вывод:** рекомендация взносов при вероятности достижения **50 %** — это подбрасывание
монеты, поданное как совет. По шкале Брюнеля (Table 1 в §1.6) 50 % — это нижняя граница
категории «Dreams», а не «Needs». Массовый робо-адвайзер де-факто ставит все цели
пользователя в разряд мечты. Это готовый конкурентный аргумент и одновременно
предупреждение: если FINPILOT начнёт показывать вероятности, надо решить, какой уровень
считается допустимым, и не молчать о нём.

### 6.3. Vanguard VLCM — ПРОЧИТАНО В ИСТОЧНИКЕ

Источник: «Vanguard's Life-Cycle Investing Model (VLCM): A general portfolio framework for
goals-based investing», Vanguard research, май 2025.
https://corporate.vanguard.com/content/dam/corp/research/pdf/vanguard_life_cycle_investing_model_vlcm_a_general_portfolio_framework_for_goals_based_investing.pdf

**Конструкция целевой функции (с. 5, дословно):**

> «One of the main advantages of a utility theory is that it explicitly accounts for an
> investor's risk preference or risk aversion. The VLCM ranks different glide-path options
> by applying the risk-tolerance criteria embedded in the utility function. **This function
> works as a scoring system that ranks all possible portfolio options based on their risk
> and return characteristics. Each potential glide path that is evaluated is given a utility
> score, and the glide path with the highest score** (the one that strikes the optimal
> balance between expected return and risk) **is the best solution for the investor's
> preferences, circumstances, and goal.**»

**Цель модели (с. 4, дословно):**

> «The main objective behind life-cycle investing and the VLCM is to maximize the expected
> lifetime utility of spending and wealth.»
> «the VLCM generates optimal glide paths by assessing the trade-offs between the expected
> (median) lifetime spending that can be funded from a portfolio and uncertainty about that
> spending due to market risk. The model uses an optimization algorithm to evaluate this
> trade-off among potential glide paths and selects the glide path that offers the best
> balance between level and volatility of lifetime spending.»

**Четыре набора входов (с. 5, дословно):** (1) Investor goal and investment horizon;
(2) Asset class return projections from VCMM; (3) Investor circumstances such as savings
rate, length of accumulation period, additional sources of income or assets for funding
the goal, and consumption horizons; (4) Investor preferences such as risk aversion,
shortfall risk aversion, loss aversion, and preference for timing of spending.

**Выходные метрики (Fig. 1, с. 6, дословно):** «Simulated wealth distributions through
time · Simulated consumption distributions through time · Risk metrics such as portfolio
return volatility, consumption volatility, and wealth volatility · **Probability of success,
given a goal** · Potential benefit of customization (certainty fee equivalent)…»
Симуляции: «Distribution of return outcomes from VCMM are derived from **10,000 simulations**
for each modeled asset class. Simulations as of December 31, 2024.»

**Горизонт нерейтайрмент-целей (с. 7, дословно):** «nonretirement goals, which tend to have
an intermediate horizon, **such as 5 to 30 years**.»

🔴 **Измеренный ноль:** в полном перечне входов VLCM (Fig. 1, с. 6 — 15 позиций для
retirement, 4 для nonretirement, 2 поведенческих, 2 рациональных предпочтения, 9 классов
активов) **долга, кредитов и обязательств домохозяйства нет ни одной строкой**.
Ближайшее — «External cash flows». То есть у самой методологически развитой публично
раскрытой goals-based модели индустрии долговая сторона отсутствует конструктивно.

**Мой вывод:** VLCM — прямой структурный аналог нашего ядра, только в инвестиционном
домене: перебор допустимых альтернатив (glide paths вместо 66 сплитов), скоринг каждой
одной сверткой, выбор максимума, риск-предпочтения как параметры функции. Это лучший
из найденных аргументов, что наша конструкция «перебор + свёртка + профиль весов»
методологически законна: так устроена модель Vanguard. Разница — у них утилитарная
функция с теоретическим обоснованием (expected lifetime utility), у нас SAW — линейная
свёртка нормированных критериев, теоретического статуса которой это не даёт. §7.

### 6.4. Schwab Intelligent Portfolios — НЕ ЗАКРЫТО

Страница `https://intelligent.schwab.com/page/goal` вернула **301** на
`https://www.schwab.com/intelligent-portfolios`; редирект в этом прогоне не пройден
(экономия бюджета). По поисковым сниппетам Goal Tracker раскрывает три состояния
(«on target», «at risk», «off target») и «long-term expected return estimates and
simulations», но **сами пороги состояний не проверены по первоисточнику** и потому
в этот файл как факт не заносятся. Задача следующему заходу.

---

## 2, 3, 5. В РАБОТЕ (подагент)

Метрика достижения цели и её дефекты · приоритизация нескольких целей и конкуренция
целей с погашением долга · академическая критика GBI. Заполняется по возврату подагента.
Если файл остался в этом состоянии — прогон оборвался здесь; §1, §4, §6 при этом
полностью проверены по первоисточникам.

---

## 8. ЧТО ОСТАЛОСЬ НЕДОСТУПНЫМ (промежуточно)

- SSRN (403), EDHEC (403), nobelprize.org (403), MIT DSpace (405), HBR (пейволл) —
  каналы мёртвые для `WebFetch` в этом прогоне.
- Schwab Goal Tracker — редирект не пройден.
- Следующему заходу: те же URL через `curl -sL -A "Mozilla/5.0"` из Bash (у ведущего
  агента этой сессии Bash не было) и зеркала на personal pages авторов.
