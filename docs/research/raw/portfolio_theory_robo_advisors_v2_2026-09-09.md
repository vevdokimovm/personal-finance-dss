# Портфельная теория и робо-эдвайзеры: что переносится на FINPILOT, а что нет (v2)

**Дата:** 09.09.2026
**Тема очереди:** №12
**Заход:** второй. Первый (`portfolio_theory_robo_advisors_2026-09-08.md`) забракован —
отработал при исчерпанном WebSearch и выдал реконструкцию по памяти модели.

## Шапка о качестве материала

- WebSearch на момент работы **живой** (проверено первыми двумя запросами, вернули результаты).
- Основной первоисточник (DGU) получен **живьём как PDF полного текста рабочей версии**
  и распарсен локально — цитаты ниже сняты дословно из текста, не из аннотации.
- Раздел «НЕ ПРОВЕРЕНО» в конце содержит всё, что не удалось подтвердить открытым URL.
- Английские цитаты не переводятся (требование задания).

---

## 1. Первоисточник DGU 2009

### 1.1 Что именно получено живьём

- Журнальная версия (paywall, аннотация открыта):
  https://academic.oup.com/rfs/article-abstract/22/5/1915/1592901
  — *Review of Financial Studies*, Vol. 22, Issue 5, May 2009, pp. 1915–1953.
- **Полный текст рабочей версии (June 2006 draft, заголовок «1/N»)**, скачан HTTP 200,
  409 581 байт, распарсен `pdftotext` (5153 строки текста):
  https://users.nber.org/~confer/2006/si2006/ap/uppal.pdf
  Это версия, циркулировавшая под названием «How Inefficient is the 1/N Asset-Allocation
  Strategy?»; численные результаты и аналитика §5 совпадают с опубликованными.
- Не получено: https://www.bauer.uh.edu/rsusmel/phd/DeMiguel-Garlappi-Uppal-RFS.pdf — **HTTP 403**.
- Не получено: https://mfs.rutgers.edu/MFS/mfs_i/MFSpapers/1_N.pdf — **соединение не установлено (curl код 000)**.
- https://faculty.london.edu/avmiguel/DeMiguel-Garlappi-Uppal-RFS.pdf — отдал HTTP 200,
  но телом был **HTML-документ, а не PDF** (лендинг/редирект). Как источник не засчитан.

### 1.2 Постановка и результат — дословно

> «In this paper, we evaluate the out-of-sample performance of the portfolio policy from the
> sample-based mean-variance portfolio model and the various extensions of this model, designed
> to reduce the impact of estimation error relative to the benchmark strategy of investing a
> fraction 1/N of wealth in each of the N assets available. Of the fourteen models of optimal
> portfolio choice that we evaluate across seven empirical datasets, we find that none is
> consistently better than the 1/N rule in terms of Sharpe ratio, certainty-equivalent return,
> or turnover. This finding indicates that, out of sample, the gain from optimal diversification
> is more than offset by estimation error.»
> — Abstract, https://users.nber.org/~confer/2006/si2006/ap/uppal.pdf

**Выписка.** Метрик ровно три и они названы явно: out-of-sample Sharpe ratio,
certainty-equivalent (CEQ) return, turnover. Формулировка «none is **consistently** better»
— не «1/N выигрывает всегда», а «ни одна из 14 не выигрывает устойчиво по всем датасетам».

### 1.3 Критическая длина окна оценки — дословно

> «To gauge the severity of estimation error, we derive analytically the length of the estimation
> window needed for the sample-based mean-variance strategy to outperform the 1/N benchmark;
> for parameters calibrated to U.S. stock market data, we find that, for a portfolio with only
> 25 assets, the estimation window needed is more than 3,000 months, and for a portfolio with
> 50 assets, it is more than 6,000 months, although in practice these parameters are estimated
> using 120 months of data.»
> — Abstract, там же

И в теле статьи, с указанием условий:

> «This critical estimation-window length is a function of the number of assets, the ex-ante
> Sharpe ratio of the mean-variance portfolio, and the Sharpe ratio of the 1/N policy. Based on
> parameters calibrated to U.S. stock-market data, we find that the critical length of the
> estimation window is 3,000 months for a portfolio with only 25 assets, and more than 6,000
> months for a portfolio with 50 assets. The severity of estimation error is startling if we
> consider that, in practice, these portfolio models are typically estimated using only 60 or
> 120 months of data.»
> — §1 Introduction, там же

**Выписка.** Число 3 000 месяцев (=250 лет) для 25 активов **подтверждено дословно**, условие —
калибровка на данные фондового рынка США. Критическое окно — **не константа**, а функция трёх
величин: N, ex-ante Sharpe оптимального портфеля, Sharpe у 1/N. Это прямо означает, что цифра
переносится только вместе с постановкой, где эти три величины определены.

### 1.4 Причина: ожидаемые доходности или ковариации — дословно

> «Our analytical results suggest that the error in estimating expected returns contributes much
> more to the poor performance of the sample-based mean-variance strategy than the error in
> estimating covariances.»
> — §1 Introduction, там же

Подтверждается эмпирикой из §4:

> «From the row for the minimum-variance strategy titled “min”, we see that ignoring the estimates
> of expected returns altogether but exploiting the information about correlations does lead to
> better performance relative to the out-of-sample mean-variance strategy.»
> — §4, там же

> «…by ignoring expected returns (which are difficult to estimate) but still taking into account
> the [covariance structure]…»
> — §2, там же

> «…because expected returns are more difficult to estimate [than covariances]…»
> — §3, там же

**Выписка — это центральный факт для нашего вопроса.** Авторы называют причиной провала
**ошибку оценки ОЖИДАЕМЫХ ДОХОДНОСТЕЙ**, а не ковариаций. Стратегия minimum-variance, которая
вообще выбрасывает оценку доходностей и оставляет только ковариации, работает **лучше** полной
mean-variance. То есть удар приходится именно по тому параметру, который в задаче
**прогнозируемый и стохастический**.

### 1.5 Механизм провала — дословно

> «The intuition for the poor performance of optimizing models relative to 1/N is that even small
> errors in estimating the moments of asset returns can lead to large differences in the portfolio
> weights. As a result, “allocation mistakes” caused by using the 1/N weights can turn out to be
> smaller than mistakes caused by using the weights from an optimizing model»
> — §1 Introduction, там же

**Выписка.** Формулировка механизма: **усиление шума входа в выходном решении**
(малая ошибка входа → большое смещение весов). Это свойство ОПТИМИЗАТОРА,
а не свойство рынка. Ниже (раздел «Что это значит для FINPILOT») это критично: наш перебор
66 альтернатив с шагом 10% усиление шума в весах **структурно ограничивает** — но только
по тем входам, которые дискретизированы, а не по прогнозным.

### 1.6 Условия, при которых оптимизация ВЫИГРЫВАЕТ — дословно

> «From our simulation results we conclude that portfolio strategies from the optimizing models
> are expected to outperform the 1/N benchmark if: (i) the estimation window is long, (ii) the
> ex-ante (true) Sharpe ratio of the mean-variance efficient portfolio is substantially higher
> than that of the 1/N portfolio, and (iii) the number of assets is small. The first two
> conditions are intuitive. The reason for the last condition is that a smaller number of assets
> implies fewer parameters to be estimated, and therefore, less room for estimation error; and,
> all else being equal, a smaller number of assets makes naive diversification less effective
> relative to optimal diversification.»
> — §1 Introduction, там же

**Выписка.** Это ключ к переносимости: **три условия победы оптимизации** — длинное окно
(= малая ошибка оценки), большой разрыв в истинном качестве оптимума над наивным,
малое число параметров. Задача с детерминированными параметрами — вырожденный случай
условия (i): окно бесконечно, ошибка нулевая.

### 1.7 Перечень 14 моделей (Table 1) — дословно

```
Naive
0. 1/N with rebalancing (benchmark strategy)                              ew or 1/N
Classical approach that ignores estimation error
1. Sample-based mean-variance                                              mv
Bayesian approach to estimation error
2. Bayesian diffuse-prior                                                  Not reported
3. Bayes-Stein                                                             bs
4. Bayesian Data-and-Model                                                 dm
Moment restrictions
5. Minimum-variance                                                        min
6. Value-weighted market portfolio                                         vw
7. MacKinlay and Pastor's (2000) missing-factor model                      mp
Portfolio constraints
8. Sample-based mean-variance with shortsale constraints                   mv-c
9. Bayes-Stein with shortsale constraints                                  bs-c
10. Minimum-variance with shortsale constraints                            min-c
11. Minimum-variance with generalized constraints                          g-min-c
Optimal combinations of portfolios
12. Kan and Zhou's (2005) "three-fund" model                               mv-min
13. Mixture of minimum-variance and 1/N                                    ew-min
14. Garlappi, Uppal, and Wang's (2006) multi-prior model                   Not reported
```
— Table 1, там же

**Выписка.** Все 14 — вариации **одной задачи**: mean-variance с оценёнными по выборке
моментами. Ни одна не является задачей с известными детерминированными параметрами.
Это уже само по себе ограничивает область применимости вывода.

### 1.8 Выборка, горизонт, методология — дословно

Семь датасетов (Table 2), все — месячные избыточные доходности над 90-дневным US T-bill:

| # | Датасет | N | Период |
|---|---------|---|--------|
| 1 | Ten sector portfolios of the S&P500 + US equity market (S&PSectors) | 10+1 | 01/1981–12/2002 |
| 2 | Ten industry portfolios + US equity market (Industry) | 10+1 | 07/1963–11/2004 |
| 3 | Eight country indexes + World Index (International) | 8+1 | 01/1970–07/2001 |
| 4 | SMB and HML + US equity market (MKT/SMB/HML) | 2+1 | 07/1963–11/2004 |
| 5 | Twenty Size and B/M portfolios + US equity market (FF-1-factor) | 20+1 | 07/1963–11/2004 |
| 6 | Twenty Size and B/M portfolios + MKT, SMB, HML (FF-3-factor) | 20+3 | 07/1963–11/2004 |
| 7 | Twenty Size and B/M portfolios + MKT, SMB, HML, MOM (FF-4-factor) | 20+4 | 07/1963–11/2004 |

— Table 2, там же

Базовая конфигурация (§7.1, «robustness» перечень базовых допущений):

> «(1) the estimation window is M = 120 months; (2) the estimation window is rolling, rather
> than increasing with time; (3) the holding period is one month; (4) the portfolios evaluated
> are those consisting of only-risky assets; (5) one can invest in also the factor portfolios;
> (6) the performance is measured relative to the 1/N-with-rebalancing strategy, rather than
> the 1/N buy-and-hold strategy; (7) the investor has a risk aversion of γ = 1…»
> — §7.1, там же

> «…we choose an estimation window of length M = 60 or M = 120 [months]»
> — §3, там же

**Выписка.** Горизонт удержания — **один месяц**, окно скользящее, перебалансировка ежемесячная.
Задача **повторяющаяся с высокой частотой**, где turnover — реальная статья издержек.
Наша задача (распределение свободного потока раз в месяц с горизонтом плана в годы)
совпадает по частоте, но НЕ по природе входных параметров.

### 1.9 Аналитическая рамка §5 — дословно

> «As in Kan and Zhou (2005), we treat the portfolio weights as an estimator, that is, as a
> function of the data. […] we derive a measure of the expected loss incurred in using a
> particular portfolio strategy that is based on estimated rather than true moments.»
> — §5, там же

Формально:

> «U(x) = xᵀµ − (γ/2) xᵀΣx. The optimal weight is x* = (1/γ)Σ⁻¹µ … Because µ and Σ are not known,
> the optimal portfolio weight is also unknown, and is estimated as a function of the available
> data: x̂ = f(R₁, R₂, …, R_M). We define the expected loss from using a particular estimator of
> the weight x̂ as L(x*, x̂) = U(x*) − E[U(x̂)]»
> — §5, уравнения (14)–(17), там же

**Выписка — это и есть граница переносимости, выраженная формально.** Вся аналитика DGU
построена на функции потерь `L(x*, x̂) = U(x*) − E[U(x̂)]`, где `x̂` — **оценка**, функция
конечной выборки данных. Если параметры задачи известны точно (не оцениваются из выборки),
то `x̂ = x*` и `L ≡ 0` **по построению**. Утверждение DGU в этом случае не то чтобы «не
подтверждается» — оно **не определено**: у него нет аргумента.

---

## 5. Робо-эдвайзеры — фактура из регуляторных документов

### 5.1 Vanguard — Form ADV Part 2A / Form CRS (ГЛАВНАЯ НАХОДКА, ПОДТВЕРЖДЕНО ДОСЛОВНО)

**Источник получен живьём:** https://personal1.vanguard.com/pdf/vanguard-digital-advice-brochure.pdf
HTTP 200, 1 534 448 байт, PDF 1.7, распарсен `pdftotext` (9 921 строка).
Документ: «Advisor Client Relationship Summary (Form CRS)», **дата на титуле — August 20, 2026**,
Vanguard Advisers, Inc. (VAI), registered with the SEC as an Investment Adviser. Внутри одного
файла — CRS + брошюры программ (Digital Advisor / Personal Advisor), то есть Part 2A по существу.

**Дословно, целевая фраза и — главное — предложение сразу после неё:**

> «Each Service provides access to calculators and interactive tools to help educate Clients about
> how to save for emergencies, where to direct extra or idle cash and how to optimize debt
> repayment options. **These interactive tools are not integrated with the discretionary investment
> advisory and related online financial planning services offered through the Services and do not
> impact your recommended investment strategy.**»
> — Vanguard, ADV brochure (August 20, 2026), раздел «Advisory business», стр. 6

**Выписка — ранее установленное по рынку ПОДТВЕРЖДЕНО дословно и усилено.** Фраза про
«where to direct extra or idle cash and how to optimize debt repayment» не просто «юридически
отвязана» — Vanguard прямым текстом пишет два отдельных отрицания:
(1) инструменты **не интегрированы** с дискреционным инвестиционным контуром и
онлайн-планированием; (2) они **не влияют на рекомендуемую инвестиционную стратегию**.
Это не оговорка об ответственности, это описание архитектуры: калькулятор долга у Vanguard —
**образовательный виджет сбоку**, а не вход в модель распределения.

Подтверждается вторым независимым местом того же документа:

> «Personalizing your enrollment will also give you access to plan additional goals and use digital
> tools like the debt payoff calculator.»
> — там же, стр. 10

**Выписка.** «Debt payoff calculator» перечислен через запятую с прочими «digital tools» —
опять не часть движка аллокации.

**Дословно — размен «гасить долг или инвестировать» у Vanguard ЕСТЬ, но как преддверие сервиса,
не как расчёт внутри него:**

> «Before enrolling in a Service, Clients should consider paying off high-interest debt. If potential
> returns on your investments are lower than your debt's interest rate, it may be best to prioritize
> debt payments first. See “Methods of analysis, investment strategies, and risk of loss - Goals
> forecasting” for the investment returns we assume for the asset classes in each Service's
> portfolios.»
> — там же, стр. 12

**Выписка — это самая содержательная строка во всём разделе.** Vanguard формулирует
**ровно то сравнение, которое является ядром FINPILOT**: ожидаемая доходность инвестиций
против ставки по долгу, и если доходность ниже ставки — гасить долг первым. И тут же
адресует читателя к разделу с **предполагаемыми** доходностями по классам активов.
То есть Vanguard:
- признаёт правило разменом ставок как верное;
- **выносит его ЗА периметр алгоритма** — в текст «before enrolling», в обязанность клиента;
- причина видна из самой формулировки: сторона «инвестиции» у них — **assumed returns**
  (оценка), сторона «долг» — договорная ставка (факт). Сводить факт с оценкой в одном
  дискреционном рекомендательном контуре они не берутся, и вместо этого отдают решение человеку.

Дополнительно, «next dollar guidance» — самое близкое к нашей задаче, что у них есть:

> «Emergency savings and next dollar guidance: The Services provide guidance on how to set emergency
> savings goals, as well as a tool that helps define target thresholds for cash or cash equivalent
> holdings that could be liquidated at no cost … Furthermore, the Services also provide guidance on
> how to balance competing financial objectives, such as wanting to contribute more money to your
> retirement accounts, pay down debt, or save for an emergency.»
> — там же, «Methods of analysis», стр. ~40

**Выписка.** Формулировка «guidance on how to balance competing financial objectives» — это
**наша задача словами Vanguard**: резерв vs долг vs накопление на цель. Но и здесь глагол —
«provide guidance», а не «compute allocation». Ни ставок, ни оптимизации, ни весов.

**Вывод по Vanguard.** Крупнейший робо-эдвайзер мира в своём регуляторном документе
(а) явно называет размен «долг против инвестиций через ставку» правильным,
(б) явно выносит его из алгоритма и
(в) явно пишет, что долговые инструменты на рекомендацию не влияют.
Ниша, в которую целится FINPILOT, на этом уровне рынка **не занята алгоритмически**.

### 5.2 Wealthfront — Classic Portfolio Investment Methodology White Paper

**Источник получен живьём:** https://research.wealthfront.com/whitepapers/investment-methodology/
HTTP 200, 102 272 байта HTML, текст извлечён локально.

> «Wealthfront determines the optimal mix of our chosen asset classes by using Mean-Variance
> Optimization (Markowitz, 1952), the foundation of Modern Portfolio Theory.»

> «Mean-variance optimization (MVO) requires, as inputs, estimates of each asset class's expected
> return, volatility (standard deviation), and the pairwise correlations between asset classes.
> **MVO is sensitive to input parameters and tends to produce concentrated and unintuitive
> portfolios if the parameters are naively specified.** To overcome the difficulty of applying MVO
> in practice, Fischer Black and Robert Litterman proposed the Black-Litterman model while working
> at Goldman Sachs (Black & Litterman, 1992). Their model applies a technique that derives expected
> return parameters from market equilibrium allocations and manager “views” … **It largely mitigates
> the optimizer's sensitivity problem** and enables it to produce diversified and intuitive
> portfolios.»
> — Wealthfront whitepaper, раздел «Mean-Variance Optimization»

> «Additionally, we enforce minimum and maximum allocation constraints for each asset class …
> The minimum allocation constraints are set at zero in order to ensure that the optimized
> portfolios are long-only … **We selected 35% as the maximum allocation for most asset classes
> to help ensure sufficient diversification.**»
> — там же, раздел «Portfolio Optimization»

**Выписка.** Wealthfront признаёт болезнь DGU **своими словами и в собственном продакшене**
(«MVO is sensitive to input parameters», «concentrated and unintuitive portfolios»), и лечит её
двумя средствами: (1) Black-Litterman — то есть **замена оценки ожидаемых доходностей
на равновесно-байесовскую конструкцию**, и (2) **жёсткие box-ограничения на веса** (0%…35%,
US stocks до 45%). Второе — не эконометрика, а прямая **ампутация степеней свободы оптимизатора**,
ровно тот механизм, который у DGU в списке 14 моделей проходит как «portfolio constraints»
(mv-c, min-c, g-min-c) и оказался самым результативным из всех лекарств.

Ни одного упоминания долга как объекта решения в методологии: слово «debt» встречается
исключительно в описаниях классов активов (US bonds, corporate bonds, municipal bonds — «debt
issued by…»). **Размена «гасить долг или инвестировать» в инвестиционном контуре Wealthfront нет.**

### 5.3 Betterment — Portfolio construction methodology

**Источник получен живьём:** https://www.betterment.com/resources/betterment-portfolio-strategy
HTTP 200, 398 912 байт HTML. Титул: «Betterment's portfolio construction methodology»,
«Updated June 15, 2026».

> «Modern Portfolio Theory requires estimating variables such as expected-returns, covariances,
> and volatilities to optimize for portfolios that sit along an efficient frontier. We refer to
> these variables as capital market assumptions (CMAs) … **While we could use historical averages
> to estimate future returns, this is inherently unreliable because historical returns do not
> necessarily represent future expectations.** A better way is to utilize the Capital Asset Pricing
> Model (CAPM) along with a utility function…»
> — Betterment, §III «Portfolio optimization»

**Самое важное — как именно они гасят шум (это ресэмплинг Мишо в продакшене):**

> «To robustly estimate the weights that best balance risk and return, **we first generate several
> thousand random samples of 15 years of expected returns for the selected asset classes based on
> our latest CMAs, assuming a multivariate normal distribution. For each sample of 15 years of
> simulated expected return data, we find a set of allocation weights subject to constraints that
> provide the best risk-return trade-off, expressed as the portfolio's Sharpe ratio … Averaging the
> allocation weights across the thousands of return samples gives a single set of allocation
> weights optimized to perform in the face of a wide range of market scenarios (a “target
> allocation”).**»
> — там же, «Constrained optimization for stock-heavy portfolios»

> «…we then solve for target portfolio allocation weights … **with the range of possible solutions
> constrained by limiting the deviation from the composition of the custom benchmark.**»
> — там же

**Выписка — крупная находка.** Betterment в проде делает ровно **Michaud resampled efficiency**:
Монте-Карло по входным параметрам → оптимизация на каждом розыгрыше → **усреднение ВЕСОВ**,
а не усреднение входов. Плюс второй слой — ограничение отклонения от бенчмарка. То есть
крупнейший робо-эдвайзер отвечает на болезнь DGU не «отказом от оптимизации», а
**усреднением решения по распределению входа**. Это прямой прототип метрики устойчивости
для нашего перебора 66 альтернатив (см. §6).

Слово «debt» в методологии Betterment встречается **ноль раз** в смысле обязательств клиента.
**Размена «долг vs инвестиции» нет.**

### 5.4 Schwab Intelligent Portfolios

Документ не получен: https://www.schwab.com/legal/intelligent-portfolios-disclosure-brochure —
**HTTP 404** (359 872 байта тела — страница-ошибка, не брошюра). Альтернативный URL в этом
заходе не найден. **Схема Schwab остаётся непроверенной.**

### 5.5 Betterment Form ADV Part 2A

Не получен: https://www.betterment.com/legal/form-adv-part-2a — **HTTP 404**.
Первичная методология Betterment взята из их собственного published whitepaper (§5.3),
регуляторный документ остаётся непроверенным.

### 5.6 Ответ на вопрос §5 задания

**Считает ли хоть один из четырёх размен «гасить долг или инвестировать» с учётом ставок,
внутри алгоритма?**

**Нет — по всему, что получено живьём.**
- Vanguard: правило сформулировано **дословно и верно**, но явно вынесено за периметр
  («Before enrolling…», «do not impact your recommended investment strategy»).
- Wealthfront: долга нет в модели вообще.
- Betterment: долга нет в модели вообще.
- Schwab: **не проверено** (404).

Ниша алгоритмического размена «свободный поток → долг / резерв / цель» на уровне
регуляторно описанного движка у трёх из четырёх крупнейших **пуста**.

---

## 2. Контраргументы и опровержения DGU

### 2.1 Kritzman, Page, Turkington (2010) — «In Defense of Optimization: The Fallacy of 1/N»

**Получено живьём:** официальная страница издателя (CFA Institute Research and Policy Center)
с полным текстом аннотации — https://rpc.cfainstitute.org/research/financial-analysts-journal/2010/in-defense-of-optimization-the-fallacy-of-1n
HTTP 200. Выходные данные со страницы: *Financial Analysts Journal*, Volume 66, Issue 2,
1 March 2010, 9 pages, doi 10.2469/faj.v66.n2.6, ISSN 0015-198X.
Авторы: Mark P. Kritzman, CFA; Sébastien Page, CFA; David Turkington, CFA.

**Полный текст статьи НЕ получен** (paywall CFA Institute Member Content).
Проверены и провалились: SSRN abstract 1591171 — **HTTP 403**;
windhamlabs.com PDF — **HTTP 404**; cfainstitute.org media PDF — **HTTP 404**;
edisciplinas.usp.br PDF — **HTTP 404**. Поиск через DuckDuckGo HTML свободного PDF не дал
(только rpc.cfainstitute.org, JSTOR 27809177, statestreet, scispace).

**Аннотация дословно (с официальной страницы издателя):**

> «Previous research has shown that equally weighted portfolios outperform optimized portfolios,
> which suggests that optimization adds no value in the absence of informed inputs. This article
> argues the opposite. With naive inputs, optimized portfolios usually outperform equally weighted
> portfolios. **The ostensible superiority of the 1/N approach arises not from limitations in
> optimization but, rather, from reliance on rolling short-term samples for estimating expected
> returns. This approach often yields implausible expectations.** By relying on longer-term samples
> for estimating expected returns or even naively contrived yet plausible assumptions, optimized
> portfolios outperform equally weighted portfolios out of sample.»
> — CFA Institute RPC, страница статьи

**Выписка — и это ровно наш вопрос.** KPT не спорят с математикой DGU. Они меняют **одну вещь
в постановке: способ получения ожидаемых доходностей.** DGU кормили оптимизатор скользящим
5–10-летним историческим средним; KPT заменяют этот вход на долгосрочную выборку или даже
на «наивно сконструированные, но правдоподобные» допущения — и оптимизация выигрывает.
То есть **обе стороны спора согласны в диагнозе: болен ВХОД «ожидаемая доходность»,
а не оптимизатор.** Спор идёт только о том, лечится ли вход. Это максимально благоприятная
для нас конфигурация литературы: если у задачи вход не «ожидаемая доходность», спор к ней
не относится ни одной из сторон.

### 2.2 Вторичный конспект статьи KPT (не первоисточник, помечено)

**Источник:** https://reasonabledeviations.com/notes/papers/defense_optimisation/ HTTP 200.
Это **конспект стороннего автора** (Robert Andrew Martin), не первоисточник. Приводится
отдельно и только как указание на методологию, которую нужно будет подтвердить по полному
тексту, если он понадобится.

> «The study used 13 datasets representing different asset classes, some going back to 1926. …
> Rather than using econometrics, three different models for expected returns were used:
> Constant expected returns, i.e only generating the minimum variance portfolio. Estimating a risk
> premium for each asset. Rolling mean using all available data. The covariance matrix was estimated
> with a monthly rolling 5/10/20-year sample covariance matrix.»

> «Optimisation of the covariance matrix alone adds value. Any reasonable set of expected returns,
> even chosen based only on arbitrary judgment, outperforms 1/N after optimisation. It doesn't
> matter how sophisticated the optimisation is if the return model is based on a small rolling
> sample.»

> «Markowitz 1952 is about optimisation given a set of beliefs, not about how to generate those
> beliefs.»

**Выписка (со статусом «вторичное, требует сверки с полным текстом»).** Ключевая мысль —
разделение «оптимизация при данных убеждениях» vs «порождение убеждений». Это то самое
разделение, которое переносит спор с оптимизатора на источник входных чисел.

---

## 3. Граница переносимости: оцениваемые стохастические параметры vs известные детерминированные

### 3.1 Michaud & Michaud — прямая формулировка границы

**Источник получен живьём:** https://newfrontieradvisors.com/media/rxbld4hq/estimation-error-and-portfolio-optimization-12-05.pdf
HTTP 200, 927 901 байт, PDF 25 страниц, распарсен `pdftotext`.
«Estimation Error and Portfolio Optimization: A Resampling Solution», Richard Michaud & Robert
Michaud, New Frontier Advisors, «Publication forthcoming in the Journal of Investment Management»,
© 2007.

**Самая важная цитата всего исследования по вопросу переносимости:**

> «MV Optimization Limitations. **The problem that limits the investment value of MV optimized
> portfolios is not Markowitz' theory. Markowitz gives the right way to invest given that you know
> that you have exactly the correct inputs. The most serious problem is estimation error, or
> parameter uncertainty, in optimization inputs.** Risk-return estimates are highly uncertain in
> investment practice and sensitivity to changes in optimization inputs leads to portfolio
> optimality ambiguity.»
> — Michaud & Michaud, «MV Optimization Limitations», стр. 6

**Выписка — искомое разделение найдено и сформулировано автором явно.** Michaud проводит
границу ровно там, где её ищет задание: **дефект локализован не в акте оптимизации,
а в неопределённости входных параметров** («estimation error, or parameter uncertainty,
in optimization inputs»). При известных верных входах Марковиц «даёт правильный способ»
(«the right way to invest given that you know that you have exactly the correct inputs»).
Это ровно тот тезис, который нужен для проверки нашей гипотезы, и он у первоисточника,
а не в пересказе.

Далее — техническая мотивация RE-оптимизации (усреднение весов, не входов):

> «Every simulated MV efficient frontier … is the right way to invest given a set of inputs.
> **But the inputs are highly uncertain. How should an investor deal with portfolio optimality
> uncertainty?** … the RE optimal minimum variance portfolio is defined as **the average of the
> portfolio weights** of all the simulated minimum variance portfolios.»
> — там же, стр. 16

> «The Resampled Efficiency™ (RE) techniques presented in Michaud (1998) introduce **Monte Carlo
> methods to properly represent investment information uncertainty** in computing MV portfolio
> optimality and in defining trading and monitoring rules. … we show RE optimization to be a
> Bayesian-based generalization and enhancement of Markowitz's solution.»
> — Abstract, там же

> «Tests demonstrate that **unbounded** MV optimized portfolios are dominated by equal weighting
> and have essentially no practical investment value. In practice MV optimization is used primarily
> as a convenient framework for imposing ad hoc constraints…»
> — там же, стр. 5

**Выписка — важная оговорка.** Слово **unbounded** несёт всю нагрузку: равновзвешенность бьёт
**неограниченную** MV-оптимизацию. Ограниченная (box-constraints, как у Wealthfront; отклонение
от бенчмарка, как у Betterment) — уже другой объект. Наш перебор с шагом 10% при
Rt≥0 и ПДН≤0.40 — **ограниченная и дискретная** задача по построению.

### 3.2 Черта, которую источники позволяют провести

Сводя §1.4, §1.9, §2.1 и §3.1: во всей найденной литературе механизм провала описывается
через **одну и ту же цепочку** —

1. параметр задачи неизвестен и оценивается по конечной выборке
   (DGU §5: `x̂ = f(R₁ … R_M)`; Michaud: «parameter uncertainty in optimization inputs»);
2. оценка шумная, причём **сильнее всего шумит средняя доходность**
   (DGU: «the error in estimating expected returns contributes much more … than the error in
   estimating covariances»; KPT: «reliance on rolling short-term samples for estimating expected
   returns … often yields implausible expectations»);
3. оптимизатор **усиливает** шум в весах
   (DGU: «even small errors in estimating the moments … can lead to large differences in the
   portfolio weights»).

**Убери звено 1 — и звенья 2, 3 не запускаются.** Ни один из найденных источников не утверждает,
что оптимизация вредна при известных детерминированных параметрах; Michaud прямо утверждает
обратное. **Прямой статьи «deterministic parameters ⇒ optimization is safe» в этом заходе
не найдено** — вывод собран из явных формулировок трёх независимых первоисточников,
а не взят из одной работы. Это надо держать в голове как ограничение.

---

## 4. Где у НАС есть оценка, а не факт: ошибка прогноза потока

### 4.1 Честный статус поиска

**Прямой литературы «household cash flow forecasting error → качество решения о распределении
свободного потока» в этом заходе НЕ НАЙДЕНО.** Запросы по терминам задания
(cash flow forecasting error, sensitivity of optimal policy to forecast error, plan stability)
вывели на корпоративный треженери-маркетинг (arya.ai, hyperbots, numeric, dryrun и т.п.) —
это не источники. Ниже — **смежная, но методологически прямая** литература из stochastic
programming, где вопрос «насколько ошибка прогноза портит оптимальное решение» ставится
формально и измеряется. Перенос на нашу задачу — по аналогии, не по прямой ссылке;
это ограничение помечено здесь и в итоговом разделе.

### 4.2 Ошибка прогноза деградирует целевую функцию — измерено

**Источник получен живьём:** https://arxiv.org/abs/1812.00773 HTTP 200.
«Effects of forecast errors on optimal utilisation in aggregate production planning with
stochastic customer demand».

> «One problem that occurs is that **deterministic mixed integer decision problems are often used
> for long-term planning, but the real production system faces a set of stochastic influences.**
> Therefore, a planned utilisation factor has to be included into this deterministic aggregate
> planning problem. In practice, this decision is often based on past data and not consciously
> taken. In this paper, the effect of long-term forecast error on the optimal planned utilisation
> factor is evaluated … The results show that the **planned utilisation factor used in the
> aggregate planning problem has a high influence on optimal costs.** Additionally, the negative
> effect of forecast errors is evaluated and discussed in detail…»
> — Abstract, arXiv:1812.00773

**Выписка — это точный структурный аналог нашей конструкции.** У них: детерминированная
оптимизационная задача, в которую стохастика заходит **через один буферный параметр**
(planned utilisation factor), калиброванный по прошлым данным. У нас: детерминированный перебор
66 альтернатив, в который стохастика заходит **через прогноз потока (SES + Монте-Карло)
и через размер резерва**. Вывод их работы: сам буферный параметр «has a high influence on
optimal costs» — то есть **вся чувствительность к прогнозу концентрируется в этом параметре,
а не размазана по оптимизатору**. Для нас это указание, где искать нашу уязвимость: не в SAW
и не в переборе, а в том, как прогноз потока превращается в один-два числа на входе.

### 4.3 Асимметрия ошибки прогноза — измерено

**Источник получен живьём:** https://arxiv.org/abs/2405.19997 HTTP 200.
«Analyzing the impact of forecast errors in the planning of wine grape harvesting operations
using a multi-stage stochastic model approach».

> «Results indicate that **the effect of the errors in yield determination is not symmetrical;
> underestimations of the yields have a more significant negative effect on the objective
> function, while overestimation does not.** Flexibility to revise hiring decisions does not make
> a significant difference if the yields are overestimated.»
> — Abstract, arXiv:2405.19997

**Выписка.** Прямой и переносимый результат: **ошибка прогноза бьёт асимметрично**, и одна
сторона ошибки дороже другой. Для FINPILOT это значит, что проверять устойчивость к прогнозу
потока надо **раздельно вверх и вниз**: занижение прогноза дохода и завышение прогноза расхода
почти наверняка не эквивалентны по цене. Симметричный доверительный интервал вокруг SES —
неверная форма проверки.

---

## 6. Метрики устойчивости решения

### 6.1 Turnover — определение из первоисточника DGU

> «Three, to get a sense of the amount of trading required to implement each portfolio strategy,
> we compute the portfolio turnover, defined as **the average sum of the absolute value of the
> trades across the N available assets**: Turnover = 1/(T−M) · Σ_t Σ_j | ŵ_{k,j,t+1} − ŵ_{k,j,t⁺} |»
> — DGU, §3, уравнение (13), https://users.nber.org/~confer/2006/si2006/ap/uppal.pdf

**Выписка.** Turnover у DGU — **L1-норма изменения вектора весов между соседними периодами**.
Это чисто геометрическая мера нестабильности решения; издержки — лишь одна из её интерпретаций.
Перенос на нас прямой: между двумя соседними ежемесячными прогонами L1-расстояние между
выбранными долями (долг / резерв / цель) — готовая метрика «план не дёргается».

### 6.2 Turnover как регуляризатор, а не только как издержка

**Источник получен живьём:** https://arxiv.org/abs/1709.06296 HTTP 200.
«Large-Scale Portfolio Allocation Under Transaction Costs and Model Uncertainty».

> «We theoretically and empirically study portfolio optimization under transaction costs and
> **establish a link between turnover penalization and covariance shrinkage** with the penalization
> governed by transaction costs. **We show how the ex ante incorporation of transaction costs shifts
> optimal portfolios towards regularized versions of efficient allocations.** … we illustrate that
> **turnover penalization is more effective than commonly employed shrinkage methods** and is crucial
> in order to construct empirically well-performing portfolios.»
> — Abstract, arXiv:1709.06296

**Выписка — сильный и практичный результат.** Штраф за turnover математически эквивалентен
регуляризации (shrinkage) — то есть **наказание за перескок решения между периодами и есть
лекарство от шума на входе**, причём авторы утверждают, что оно эффективнее классического
shrinkage. Для нас это готовый механизм: штраф за изменение рекомендации относительно
прошлого месяца — не косметика для UX, а математически обоснованный способ погасить
чувствительность к шуму прогноза потока.

### 6.3 Ресэмплинг весов как гейт (из §3.1 и §5.3)

Механизм, подтверждённый и в академии (Michaud), и в проде (Betterment):
розыгрыш входов → полная оптимизация на каждом розыгрыше → **усреднение решения**.
Применительно к перебору 66 альтернатив это даёт **готовый гейт качества**, который у нас
сейчас, судя по канону, не реализован: разыграть прогноз потока Монте-Карло, прогнать перебор
на каждом розыгрыше, посмотреть **распределение выбранной альтернативы**. Если победитель
устойчив (одна и та же альтернатива или соседняя по шагу 10% выигрывает в подавляющем
большинстве розыгрышей) — решение не чувствительно к шуму прогноза. Если победитель прыгает
по всей сетке — это и есть тот самый провал DGU, но пришедший к нам не через доходности,
а через прогноз потока.

### 6.4 Метрики, применимые к нашему перебору 66 альтернатив — сводка

| Метрика | Откуда | Как считать у нас |
|---|---|---|
| Turnover (L1 между решениями) | DGU ур. (13) | Σ\|доля_t+1 − доля_t\| по трём назначениям |
| Стабильность весов при ресэмплинге | Michaud RE; Betterment | доля розыгрышей Монте-Карло, где побеждает та же альтернатива |
| Разброс победителя по сетке | Michaud RE | стандартное отклонение индекса победившей альтернативы (шаг 10%) |
| Turnover-penalty как регуляризатор | arXiv:1709.06296 | штраф в SAW за отклонение от прошлого плана |
| Асимметричный стресс прогноза | arXiv:2405.19997 | отдельно занижение дохода и завышение расхода, не симметричный интервал |
| Worst-case regret | упомянут в литературе, первоисточник не открыт | **не проверено**, см. ниже |

---

## Что это значит для FINPILOT

### Прямой ответ на главный вопрос

**Гипотеза владельца подтверждается — но НЕ полностью, и уточнение важнее подтверждения.**

**Аргумент 1/N к ядру FINPILOT не переносится.** Держится это на трёх независимо
подтверждённых опорах, каждая — дословная цитата из первоисточника:

1. **DGU называют виновником оценку ожидаемых доходностей, а не оптимизацию как таковую**
   («the error in estimating expected returns contributes much more … than the error in
   estimating covariances»; minimum-variance, выбрасывающая оценку доходностей, работает лучше
   полной MV). У нас на стороне долга — договорная ставка, факт, а не оценка. Параметра,
   который у DGU ломает всё, в этом месте нашей модели нет.
2. **Michaud проводит границу явно:** «Markowitz gives the right way to invest **given that you
   know that you have exactly the correct inputs**. The most serious problem is estimation error,
   or parameter uncertainty, in optimization inputs.» Оптимизация не порочна — порочна
   оптимизация по шумной оценке.
3. **Аналитика DGU §5 построена на `L(x*, x̂) = U(x*) − E[U(x̂)]`, где `x̂ = f(R₁…R_M)`** —
   функция конечной выборки. При известных параметрах `x̂ = x*` и потеря нулевая **по построению**.
   Число «3 000 месяцев» — не универсальная константа, а функция (N, ex-ante Sharpe, Sharpe 1/N),
   калиброванная на рынок акций США. К задаче без оцениваемых моментов оно неприменимо.

Плюс две структурные защиты, которых у DGU не было: наш перебор **дискретен** (шаг 10%,
66 альтернатив) и **жёстко ограничен** (Rt≥0, ПДН≤0.40). Michaud подчёркивает, что 1/N бьёт
именно **unbounded** MV-оптимизацию; Wealthfront и Betterment лечат ту же болезнь ровно
box-ограничениями и ограничением отклонения от бенчмарка. Дискретная сетка физически не даёт
оптимизатору «взорвать» веса от малого шума на входе — механизм провала DGU
(«small errors … can lead to large differences in the portfolio weights») у нас структурно
ослаблен.

**Но дыра есть, и она не там, где искали.** Она в п.4 задания и подтверждается собственной
логикой DGU: **эффект estimation error не исчезает, он перемещается в единственный вход,
который у нас действительно оценивается — прогноз потока (SES + Монте-Карло).**
Ставки известны точно; **свободный денежный поток на горизонте плана — нет**. И DGU, и Michaud,
и KPT говорят одно: удар приходится по **той компоненте входа, что оценивается по короткой
истории**. У нас SES строится ровно по короткой истории транзакций пользователя — методологически
это тот же самый «rolling short-term sample», который KPT называют настоящей причиной
превосходства 1/N.

**Итог одной строкой:** провал Марковица к нам не переносится **по долговой стороне** (там факт),
но переносится **по потоковой стороне** (там оценка), и именно там надо ставить гейт.

### Что делать (следует прямо из найденного)

1. **Гейт устойчивости на ресэмплинге** — Монте-Карло уже есть в модели, но используется для
   прогноза, а не для проверки решения. Нужно: разыграть прогноз потока N раз → прогнать перебор
   66 альтернатив на каждом розыгрыше → измерить, насколько устойчив победитель. Это ровно
   Michaud RE и ровно то, что Betterment делает в проде («averaging the allocation weights across
   the thousands of return samples»). Инвариант-кандидат: победитель не должен смещаться более
   чем на один шаг сетки (10%) в X% розыгрышей.
2. **Turnover-инвариант между прогонами** — L1-расстояние между рекомендациями соседних месяцев
   (DGU ур. 13). Штраф за него, по arXiv:1709.06296, работает как регуляризация и **эффективнее
   классического shrinkage**. Это лечит одновременно две вещи: чувствительность к шуму прогноза
   и доверие пользователя к плану, который не дёргается.
3. **Асимметричный стресс прогноза, не симметричный** — arXiv:2405.19997: занижение и завышение
   стоят разного. Тестировать отдельно «доход оказался ниже прогноза» и «расход выше прогноза».
4. **Позиционирование продукта.** Vanguard в ADV дословно формулирует наше ядро
   («If potential returns on your investments are lower than your debt's interest rate, it may be
   best to prioritize debt payments first») и **явно выносит его из алгоритма**
   («do not impact your recommended investment strategy»). Wealthfront и Betterment долг
   не моделируют вовсе. Ниша алгоритмического размена «поток → долг / резерв / цель»
   на уровне регуляторно описанных движков крупнейших робо-эдвайзеров **свободна**.
   Это годится и в README, и в защиту научной новизны — со ссылкой на конкретную страницу ADV.

### Что осталось непроверенным

1. **Полный текст Kritzman/Page/Turkington (2010)** — paywall CFA Institute; SSRN 403,
   четыре зеркала 404, DDG свободного PDF не дал. Есть только дословная официальная аннотация.
   Методология (13 датасетов, три модели ожидаемых доходностей) взята из **вторичного конспекта**
   и требует сверки.
2. **Schwab Intelligent Portfolios** — disclosure brochure 404, схема не проверена вовсе.
3. **Betterment Form ADV Part 2A** — 404. Методология взята из их whitepaper, регуляторный
   документ не сверен.
4. **Прямой академической работы «deterministic known parameters ⇒ estimation-error argument
   не применяется» не найдено.** Вывод собран из явных формулировок DGU §5, Michaud и KPT,
   но единой статьи, которая проводит эту черту в лоб, в заходе не обнаружено. Стоит поискать
   отдельно в литературе по stochastic vs deterministic optimization и по VSS
   (value of the stochastic solution) — попытка открыть Maggioni/Wallace через Springer
   упёрлась в редирект на IdP-авторизацию (HTTP 303).
5. **Литературы прицельно по household cash-flow forecasting error → качество решения
   о распределении не найдено.** §4 держится на структурных аналогах из production planning
   (arXiv:1812.00773, arXiv:2405.19997), а не на прямых источниках по личным финансам.
   Это самое слабое место файла.
6. **Worst-case regret** как метрика упомянута в результатах поиска (SARPO, robust optimization
   с regret-ограничениями), но ни одного первоисточника по ней открыть в этом заходе
   не успели — в таблицу §6.4 внесена со статусом «не проверено».
7. **Литература после 2010** по спору DGU vs KPT (кто оказался прав в последующие 15 лет)
   не разобрана. Это отдельная тема для очереди.

---

## НЕ ПРОВЕРЕНО (по памяти обучения)

**Ничего.** Все утверждения выше опираются на источники, открытые в ходе этого захода;
всё, что не удалось подтвердить, вынесено в список «Что осталось непроверенным» и не
подменено реконструкцией по памяти. Раздел оставлен пустым намеренно — это отличие v2 от v1.

---

## Реестр источников (что реально открыто)

| # | URL | Статус | Что дало |
|---|-----|--------|----------|
| 1 | https://users.nber.org/~confer/2006/si2006/ap/uppal.pdf | **200, PDF, полный текст** | DGU: постановка, 3000/6000 мес., причина = expected returns, Table 1/2, ур. (13), §5 |
| 2 | https://academic.oup.com/rfs/article-abstract/22/5/1915/1592901 | 200, аннотация | Выходные данные RFS 22(5):1915–1953 |
| 3 | https://rpc.cfainstitute.org/research/financial-analysts-journal/2010/in-defense-of-optimization-the-fallacy-of-1n | **200** | KPT: дословная аннотация + выходные данные |
| 4 | https://reasonabledeviations.com/notes/papers/defense_optimisation/ | 200 | KPT: методология (ВТОРИЧНЫЙ источник) |
| 5 | https://newfrontieradvisors.com/media/rxbld4hq/estimation-error-and-portfolio-optimization-12-05.pdf | **200, PDF 25 стр.** | Michaud: граница переносимости, RE-оптимизация |
| 6 | https://personal1.vanguard.com/pdf/vanguard-digital-advice-brochure.pdf | **200, PDF, ADV/CRS от 20.08.2026** | Vanguard: дословная фраза + два отрицания + правило про high-interest debt |
| 7 | https://research.wealthfront.com/whitepapers/investment-methodology/ | **200** | Wealthfront: MVO + Black-Litterman + box-constraints, долга нет |
| 8 | https://www.betterment.com/resources/betterment-portfolio-strategy | **200** | Betterment: ресэмплинг весов (Michaud в проде), долга нет |
| 9 | https://arxiv.org/abs/1812.00773 | **200** | Ошибка прогноза → деградация целевой функции через буферный параметр |
| 10 | https://arxiv.org/abs/2405.19997 | **200** | Асимметрия ошибки прогноза |
| 11 | https://arxiv.org/abs/1709.06296 | **200** | Turnover-penalty ≡ регуляризация, эффективнее shrinkage |
| — | https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1591171 | **403** | KPT full text не получен |
| — | https://www.schwab.com/legal/intelligent-portfolios-disclosure-brochure | **404** | Schwab не получен |
| — | https://www.betterment.com/legal/form-adv-part-2a | **404** | Betterment ADV не получен |
| — | https://www.bauer.uh.edu/rsusmel/phd/DeMiguel-Garlappi-Uppal-RFS.pdf | **403** | зеркало DGU не получено |
| — | https://mfs.rutgers.edu/MFS/mfs_i/MFSpapers/1_N.pdf | **curl 000** | зеркало DGU не получено |
| — | https://faculty.london.edu/avmiguel/DeMiguel-Garlappi-Uppal-RFS.pdf | 200, но **тело = HTML, не PDF** | не засчитан |
| — | https://www.windhamlabs.com/.../In-Defense-of-Optimization-The-Fallacy-of-1N.pdf | **404** | KPT PDF не получен |
| — | https://link.springer.com/article/10.1007/s10479-010-0807-x | **303 → IdP auth** | VSS не получен |

**Живых источников, давших содержательный материал: 11.**
Из них полнотекстовых PDF первоисточников: 3 (DGU, Michaud, Vanguard ADV).
