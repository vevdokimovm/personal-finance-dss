# Хвосты темы 13 (goal-based investing): найденные, но не прочитанные источники

Дата: 2026-09-10. Статус: В РАБОТЕ (файл дописывается по ходу).
Правило: цитата из сниппета поисковой выдачи НЕ считается прочитанной и помечается явно.

## Участок 1. arXiv:2605.02300 — Meta RL для goals-based wealth management

**Статус: ЗАКРЫТ ПЕРВОИСТОЧНИКОМ, прочитан полностью (HTML-версия, 156 336 символов текста).**

Канал: `curl` с браузерным UA → `https://arxiv.org/html/2605.02300v1` → HTTP 200, 839 609 байт.
(Приём с PDF не понадобился — arXiv отдал HTML v1 целиком.)

Выходные данные: Sanjiv R. Das, Harshad Khadilkar, Sukrit Mittal, Daniel Ostrov, Deep Srivastav,
Hungjen Wang. «A Meta Reinforcement Learning Approach to Goals-Based Wealth Management».
arXiv:2605.02300v1 [cs.LG], submitted 4 May 2026. Лицензия CC BY-NC-ND 4.0.
🔴 **Это не препринт «в воздухе» — он уже опубликован:** journal reference на странице abs:
*«The Journal of Finance and Data Science, Volume 12, 2026, 100186, ISSN 2405-9188»*,
DOI `10.1016/j.jfds.2026.100186`. То есть рецензированная публикация, а не рабочая версия.
Ключевые слова авторов: *«Wealth management, Portfolio selection, Multi-goal problems»*.

### 1.1 Постановка задачи (дословно)

§2.1, определение задачи:

> «An investor using goals-based wealth management (GBWM) wishes to attain as many of their
> financial goals, weighted by their importance to the investor, as possible over the time horizon
> of their portfolio, which may mean throughout their projected lifetime. To weight the importance
> of each goal to an investor, a utility (reward) is assigned to each goal.»

Две решаемые переменные, §2.1:

> «To optimize the expected attained utility, there are two decisions that must be optimized at each
> time step within the time horizon: (1) Goal-taking: whether or not to pay the cost needed to fulfill
> a currently available goal and attain the utility assigned to that goal, and (2) Portfolio choice:
> determining which investment portfolio (level of expected return and its corresponding volatility)
> to hold for the next time step.»

🔴 Прямо назван механизм «отказаться от текущей цели ради будущей» — то есть выбор подмножества:

> «Fulfilling a goal requires there to be sufficient wealth available, but even when there is, the
> investor may be better off forgoing the current goal to increase their probability of fulfilling more
> important future goals. We note that goals cannot be deferred to later time steps in our model.
> They are either fulfilled or not at the times when they are scheduled to occur.» (§2.1)

Из §1 (Introduction) — та же мысль как определение парадигмы:

> «(1) they must determine which goals to pursue and which to abandon to preserve the capital
> required for high-priority future aspirations, and (2) they must dynamically adjust their investment
> portfolio…»

🔴 Отдельно зафиксировать: **отложить цель нельзя** («goals cannot be deferred»). Это ограничение
их модели; в списке будущих работ §7 они его прямо называют дырой — «goal postponement
(Bae et al., 2024)».

### 1.2 Целевая функция и ограничение (формула, дословно)

§2.3, уравнение (1):

> «max_{g(t), p(t), for t={0,...,T−1}} E[ Σ_t g(t)·U(t) ]»

при динамике богатства, уравнение (2):

> «W(t+1) = [W(t) + I(t) − g(t)·C(t)] · exp[(μ_{p(t)} − ½σ²_{p(t)})h + σ_{p(t)}√h · Z],
> where Z ∼ N(0,1) is a standard normal random variable.»

С оговоркой, что GBM не обязателен:

> «While using geometric Brownian motion is a standard assumption for a wealth evolution model in
> the finance literature, it is not a requirement for our RL formulation, which can accommodate any
> simulatable stochastic wealth evolution model.» (§2.3)

Аддитивность полезностей заявлена явно (§2.2, п.3):

> «Note that an investor would be just as happy attaining one goal with a utility of 4 and another
> goal with a utility of 7 as they would be attaining just one goal with a utility of 11.»

**Ограничения:** единственное жёсткое ограничение — неотрицательность/достаточность богатства
(«g = 0 means the investor decides not to take the goal (or can’t afford it)», §2.3 п.1). Никаких
ограничений типа долговой нагрузки, лимита платежа, обязательного резерва в модели НЕТ.

### 1.3 Параметры одной задачи (§2.2)

1. Горизонт: T (число шагов) и h (шаг), h = 1 год во всех экспериментах.
2. Начальное богатство W(0) и вливания I(t) (T-вектор **I**).
3. Цели: C(t) — стоимость цели года t, U(t) — её полезность (T-векторы **C**, **U**).
   Базовая модель — не более одной all-or-nothing цели в год.
4. Инвестиции: P портфелей с (μ_p, σ_p), p ∈ {0,…,P−1}. В экспериментах **P = 15** портфелей
   на эффективной границе, от самого консервативного (1) до самого агрессивного (15).

### 1.4 🔴 Как формализована «выполнить цель частично или не выполнить» — ГЛАВНОЕ

В базовой модели (§2.3): `g(t) ∈ {0,1}` — бинарно. Частичность вводится в §5.1 и Приложении E.

§5.1, дословно:

> «Up to this point, we have restricted ourselves to at most one all-or-nothing goal each year.
> In Appendix E, we show how the MetaRL model can be extended to more than one concurrent goal
> and to allowing some or all goals to be partially filled. In this case of “partial goals” the investor
> may ideally want the full goal, like a luxury trip to Paris for a month, but may also be open to
> partial goals like only having two weeks in Paris or having a month in New Jersey instead.
> Each partial goal has a reduced cost from the full goal, but also has a reduced utility if it is chosen.»

🔴 **Механика перебора комбинаций — Приложение E, дословно (это прямой аналог нашего множества
альтернатив):**

> «In the concurrent/partial goals case, at each time t, there can be a number of possible costs and
> corresponding utilities corresponding to each possible combination of forgoing, partially fulfilling
> (in each available way), or fully fulfilling each of the concurrent goals. **We form a pareto front of
> these possibilities by removing combinations that are dominated by any other combination;** for
> example, we would remove a combination that generates a utility of 50 at a cost of $40,000 if there
> is another combination that generates a utility of 52 at the same cost. In the pareto front of
> combinations that remain, the utility must increase as the cost increases. We will call the remaining
> goal combinations **G(t)**, which contains the cost and corresponding utilities of these combinations
> in increasing order. See Das et al. (2022b) for more details.»

То есть: множество альтернатив года t = все комбинации {отказ / частичное k-го уровня / полное}
по всем одновременным целям, **очищенные по Парето**. В базовом случае |G| = 2
(«Note that our approach here conforms to Appendix A, for which |G| = 2, corresponding to not taking
or taking the single all-or-nothing goal»).

Размер множества комбинаций — пример дословно (§5.1, случай CP1):

> «one all-or-nothing goal (so there are two possibilities…), one goal with one partial goal (so three
> possibilities: take the full goal, take the partial goal, or do not take the goal), and one goal with
> three partial goals (so five possibilities), and at time 10 there is one goal that has one partial goal.
> We note that this gives 2×3×5×3 = **90** different goal-taking combinations to choose from over time.»

Случай CP2: «over **301 full goals and 138 partial goals** to choose from over the course of T = 60 years».

### 1.5 Метод решения

Двухагентный PPO (dual actor-critic): GoalAgent + PortfolioAgent.

> «we decouple investment portfolio selection and goal-taking decisions into two distinct actor
> networks» (§1).

Пространство состояний — **26 переменных** (27 с инфляцией), нормированных и безразмерных (§3.1):
t/T; богатство, нормированное на дисконтированную стоимость текущих и будущих целей по
пессимистичному и оптимистичному прогнозу доходности (2 переменные); 7 переменных полезностей по
временным блокам (0, 1, 2, 3, 4–5, 6–9, 10+ лет), нормированных на сумму полезностей; 2×7 = 14
переменных стоимостей (пессимистично/оптимистично дисконтированных); 2 «indicator states»,
считаемых детерминированной Монте-Карло-симуляцией.

Действия непрерывные `a_g(t) ∈ [0,1]`, `a_p(t) ∈ [0,1]` → монотонные отображения в дискретные
`g(t)`, `p(t)`. 🔴 Третья причина непрерывности прямо про объяснимость:

> «(3) If a_g(t) were a discrete action, we would be unable to infer the confidence with which the
> action was being chosen, which would affect the interpretability of the model.» (§3.2)

Обучение: 5 random seeds × 1000 случайно сгенерированных задач; горизонты обучения 5–50 лет;
одна эффективная граница. Инференс — прогон всех пяти моделей и статистика (медиана) по пяти
действиям (§3.4).

### 1.6 С чем сравнивались и численные результаты

Эталон — **точное динамическое программирование** (backward pass, 2 переменные состояния: t и W(t)).

Тестовый набор — 🔴 **66 задач** (совпадение числа с нашими 66 альтернативами случайно, у них это
число ТЕСТОВЫХ СЦЕНАРИЕВ, а не альтернатив):

> «We designed a suite of 66 new investor problems… These test problems have time horizons that
> range from 3 to 100 years (with a mean of 38 years), and a range of 1 to 60 goals (with a mean of
> 16 goals).» (§4.1)

**Время (Таблица 1, мс, среднее по 66 кейсам):**

| Измерение | # кейсов | mean | std | min | 25% | 50% | 75% | max |
|---|---|---|---|---|---|---|---|---|
| RL-инференс, только портфель | 66 | 9.277 | 2.76 | 3.80 | 8.95 | 9.76 | 10.49 | 18.40 |
| RL-инференс, портфель + цель | 48 | 20.94 | 1.34 | 16.5 | 20.2 | 21.1 | 21.6 | 23.9 |
| DP backward pass | 66 | 2198 | 2255 | 83 | 579 | 1248 | 3720 | 8012 |

Отношения: 2198/20.94 = **105.0×**, 2198/9.277 = **236.9×**.

**Точность (Таблица 2, RL-Efficiency по 66 кейсам):**
mean **0.978**, std 0.016, min **0.917**, 25% 0.975, 50% 0.983, 75% 0.987, max 0.999.
Стабильность: 30 прогонов по 10 000 траекторий Монте-Карло дали mean 0.978293 при std 0.000380.

**Робастность к смене эффективной границы (Таблица 3):** baseline 0.978; 2022–2023 — 0.986;
2012–2013 — 0.995; 2020–2023 — 0.990; 1988–2023 — 0.984; 1997–2023 — 0.987. Границы строились
марковицевской mean-variance оптимизацией по VTSMX / VTBIX / VGTSX, январь 1998 — декабрь 2017.
Начальное богатство масштабировалось так, чтобы отношение оптимальной ожидаемой полезности к
полезности всех целей оставалось в 0.63–0.64 (baseline = **0.636**) — чтобы не завысить эффективность
искусственно.

**Concurrent/partial goals (Таблица 4):** CP1 — DP 0.276 c / RL 0.271 c / ratio 1.02 / eff 0.990;
CP2 — 14.6 / 4.50 / 3.24 / 0.985; CP3 — 2.94 / 1.48 / 1.98 / 0.986; CP4 — 3.36 / 1.54 / 2.18 / 0.972.

**Инфляция (§5.2):** модель Vasicek (1977), `dI_infl = −κ(I_infl − θ)dt + σ dW`; 27 переменных
состояния; DP при 4 переменных состояния вычислительно неосуществим.

Пример-кейс 20 (§4.3): T = 20 лет, W(0) = 100 тыс. долл., цель стоимостью 75 тыс. и полезностью 1
в каждый чётный год, вливаний нет. DP-значение функции 4.10, RL даёт 4.02.

### 1.7 🔴 Роль долга — ЕГО НЕТ

Механический прогон по всему тексту: слова `debt`, `loan`, `mortgage`, `liabilit*` встречаются
**только** в контексте «asset-liability management» как названия смежной литературы (§6, три
упоминания: «These problems are related to asset-liability management and stochastic programming»;
перечень Mulvey/Dempster/Consigli/Infanger/Topaloglou; названия двух работ в списке литературы).
**Ни одной строки о долге заёмщика, платежах по кредиту, долговой нагрузке в модели нет.**
Отрицательный денежный поток моделируется исключительно как «цель» (стоимость C(t)); заимствование
как источник средств отсутствует; W(t) ≥ 0 по построению (цель просто не берётся, если не хватает).

### 1.8 Прямой ответ: чем конструкция FINPILOT отличается от их конструкции

| Признак | Das et al. 2026 (MetaRL) | FINPILOT |
|---|---|---|
| Объект решения | (какие цели взять/частично взять) × (какой портфель держать) | распределение свободного денежного потока между долгами, резервом, целями |
| Множество альтернатив | комбинации целей G(t), очищенные по Парето; 90 комбинаций в CP1, до 301+138 целей в CP2; портфелей P = 15 | 66 альтернатив, шаг 10% |
| Свёртка | ожидаемая аддитивная полезность E[Σ g(t)·U(t)], веса = полезности целей | SAW по взвешенным критериям |
| Метод | dual-PPO мета-RL, эталон — точное DP | детерминированный перебор + SAW + Avalanche + SES/Монте-Карло |
| Ограничения | только достаточность богатства | жёсткие инварианты Rt ≥ 0 и ПДН ≤ 0.40 |
| Долг | отсутствует полностью (см. §1.7) | первоклассный объект: Avalanche-фильтр, ПДН |
| Горизонт | 3–100 лет, шаг год | короткий горизонт, месячный шаг |
| Отложить цель | 🔴 запрещено («goals cannot be deferred»), в планах на будущее | — |
| Аудитория | wealth management, инвестируемый капитал | распределение потока при наличии долгов |

**По существу отличий три, и только два из них выдерживают проверку.**

1. 🔴 **Отличия по «выбору подмножества целей под ресурсным ограничением» НЕТ ВООБЩЕ.** Их
   формулировка сильнее нашей: у них не только «взять/не взять», но и частичное выполнение
   с уменьшенной стоимостью и уменьшенной полезностью, и всё это очищается по Парето до
   множества G(t). Наш перебор 66 альтернатив с шагом 10% — это, по сути, дискретизация
   того же множества «сколько ресурса на какую цель», просто без Парето-фильтра и без
   динамики по годам.
2. **Отличие по SAW-свёртке — слабое.** Их E[Σ g(t)·U(t)] — линейная аддитивная свёртка полезностей,
   то есть та же семья, что SAW; отличие в том, что у них веса приходят из полезностей целей и
   свёртка берётся под матожиданием по стохастической динамике, а у нас — детерминированная свёртка
   по критериям. Это разница в аргументах свёртки, не в классе метода.
3. **Отличия, которые ДЕРЖАТСЯ:** (а) наличие долга как объекта оптимизации и жёсткого ограничения
   ПДН ≤ 0.40 — у них нет ни того, ни другого; (б) жёсткий инвариант Rt ≥ 0 (обязательный резерв)
   как ограничение, а не как ещё одна «цель» с полезностью. У них резерв неотличим от любой другой
   цели, у нас — не подлежит размену.

## Участок 2. Прочие источники §3.2
### 2.1 arXiv:2105.07915 Hedging Goals — ЗАКРЫТ ПЕРВОИСТОЧНИКОМ

Канал: `curl` → `https://arxiv.org/html/2105.07915v2` → HTTP 200, 424 715 байт. Прочитан.

Thomas Krabichler, Marcus Wunsch. «Hedging Goals». arXiv:2105.07915v2 [q-fin.MF],
submitted 17 May 2021, last revised 29 Oct 2021. MSC: 65K99, 91G60, 91G20.

**Постановка.** Не наша задача: один денежный goal к фиксированному сроку, задача сводится
к хеджированию опциона. Аннотация:

> «Goal-based investing is concerned with reaching a monetary investment goal by a given finite
> deadline, which differs from mean-variance optimization in modern portfolio theory… we show that
> maximizing the probability of reaching the goal (quantile hedging, cf. [FL99]) and minimizing the
> expected shortfall (efficient hedging, cf. [FL00]) yield, in fact, the same optimal investment policy.»

Две возможные математические постановки (§1.1):

> «Either, one attempts to maximize the probability of reaching an investment goal by a given maturity,
> or one tries to minimize the expected shortfall (or a function thereof).»

🔴 **Главная находка этого источника — не по нашей постановке, а по участку 4 (Kitces).**
Дословно §1.2 (Literature review):

> «While highly appealing theoretically, the probability-maximizing paradigm suffers from the binary
> nature of its optimum: **a goal missed by a hair’s breadth is still a goal missed,** and any such
> strategy will be discarded. Rather, more and more leverage will be applied to attain the goal — even
> as the maturity draws closer —, resulting in either success or bankruptcy. **This indifference for the
> size of the shortfall constitutes a major drawback of probability-maximizing strategies for practical
> purposes.**»

И там же:

> «In practice, measuring and minimizing downward risk is arguably more significant than maximizing
> the probability of attaining a goal (in analogy with the dichotomy of Expected Shortfall versus
> Value-at-Risk…). Downward risk can be quantified by the shortfall, i.e., the positive part of the
> distance between the profit a strategy has earned at maturity and the goal.»

§6.1, о практической непригодности бинарного критерия:

> «Despite all, and much more crucially, the «all-or-nothing» feature of the proposed optimal strategy
> is not feasible in many real-world applications such as traditional pension funds. **For obvious
> reasons, retirement savings are not supposed to be a Bernoulli experiment.**»

Пример 6.1 показывает механику деформации: если цель — доходность ровно r, а безрисковая ставка
даёт r−ε, то P[R(0) ≥ r] = 0, и максимизация вероятности заставляет держать долю риска
ξ ≥ (e^ε − 1)/(e^{1+ε} − 1) > 0, то есть **принимать риск ради нулевого прироста цели**. Вывод авторов:

> «This example shows that the probability-maximizing paradigm might be too rigid in the context of
> goal-based investing as it does not take into consideration the investor’s risk appetite.»

**Риск-аверсия формализована** как минимизация нижнего частного момента `E[((H − V_T)_+)^p]`,
p > 1 (Proposition 7.1), то есть глубина недобора возводится в степень — прямой аналог тезиса Estrada
(2018) о глубине провала, только в непрерывном времени.

**Долг:** отсутствует как объект. Упомянут только как «unlimited credit line at the bank» —
техническое требование к репликации дигитального опциона (§6.1), то есть кредитное плечо
хеджера, а не долг домохозяйства.

**Вклад авторов (§2):** адаптация теории хеджирования условных требований к goal-based investing,
интеграция риск-предпочтений через lower partial moments, и — заявлено как первое —
учёт транзакционных издержек через Deep Hedging:

> «To the best of our knowledge, this is the first instance that transaction costs are incorporated
> into the optimization problems arising in goal-based investing.»

**Отношение к FINPILOT:** ортогонален. Одна цель, никакого выбора подмножества целей, нет долга,
нет ограничений типа ПДН. Ценность — исключительно как рецензируемая опора для тезиса
«вероятность успеха слепа к величине недобора» (см. участок 4).
### 2.2 arXiv:2510.21650 Goal-based portfolio selection with fixed transaction costs — ЗАКРЫТ ПЕРВОИСТОЧНИКОМ

Канал: `curl` → `https://arxiv.org/html/2510.21650v1` → HTTP 200, 1 701 170 байт. Прочитан
(§1 Introduction, §2 Formulation, §3 QVI, §8 Numerical analysis; доказательства §4–7 и приложения
A–D пролистаны — это техника вязкостных решений, к нашей задаче отношения не имеет).

Erhan Bayraktar (Michigan), Bingyan Han (HKUST-GZ), Jingjie Zhang (UIBE).
arXiv:2510.21650v1 [math.OC], submitted 24 Oct 2025. Лицензия CC BY-SA 4.0.
MSC 49L20, 91G10, 49L25, 60H30.

**Постановка (§2), дословно:**

> «Assume that an investor has K goals. Each goal k ∈ {1,…,K} requires a target amount G_k by a
> predetermined deadline T_k… The investor constructs a single portfolio to meet each target G_k.»

Управления два: последовательность сделок `Λ = {(τ_n, Δ_n)}` (моменты и объёмы) и

> «the investor also needs to determine the dollar amounts allocated to each goal. Let θ_k ≥ 0 denote
> the F_{T_k}-measurable random variable representing the amount withdrawn from the money account
> to finance goal k.»

🔴 **Целевая функция — взвешенная сумма недоборов (2.15), дословно:**

> «The investor seeks to minimize the shortfalls between the target levels G_k and the funding amounts
> θ_k, weighted by the importance parameters w_k > 0:
> inf_{(θ_{1:K}, Λ) ∈ A(0,x;1)} E[ Σ_{k=1}^{K} w_k (G_k − θ_k)^+ ].»

Функция ценности (2.16): `V_k(t,x) := inf E[ Σ_{i=k}^K w_i (G_i − θ_i)^+ | … ]`.

**Это принципиально важно для нашей новизны:** здесь распределение ресурса по целям
**непрерывное** (θ_k — любая неотрицательная сумма), а не бинарное, и агрегация — **линейная
взвешенная свёртка** по целям с весами важности w_k. То есть «SAW-подобная свёртка + распределение
ресурса между несколькими целями» существует в рецензируемой математической литературе
(препринт октября 2025) в чистом виде.

**Ограничения.** Короткие продажи запрещены в обоих активах: `S̄ := [0,∞)²`. Издержки
`C(Δ)` строго положительны, `C_min := C(0) > 0`; допустимое множество сделок
`D(x) = [−x₁, χ(x₀)]`. Ликвидационная стоимость `L(x) := x₀ + (x₁ − C(−x₁))^+` (2.14).
🔴 Ограничение `x ∈ [0,∞)²` — это фактически «Rt ≥ 0» их модели: запрет на отрицательные
позиции = запрет на заимствование. Формулируется как невозможность short, а не как долговая политика.

**Долг:** отсутствует. Запрет коротких позиций — единственное соприкосновение с темой.

**Метод решения:** стохастический метод Перрона; доказано, что функция ценности — единственное
вязкостное решение системы квазивариационных неравенств (QVI); доказано существование
оптимальной стратегии торговли и схемы финансирования целей. Численно — конечные разности
с penalty-схемой (Azimzadeh, 2017) на треугольной сетке.

**Численные параметры (§8):** две цели `G₁ = 3` (дедлайн `T₁ = 1`) и `G₂ = 6` (`T₂ = 2`);
веса `w₁ = 1`, `w₂ = 0.2`; `r = 0`, `μ = 0.3`, `σ = 0.4`; `C_min = 0.02`; сетка по богатству
`Δx = (9 + C_min)/200 = 0.0451`, шаг времени `Δt = 0.01`; область `x₀ + x₁ ≤ 9 + C_min`.

**Главный содержательный результат:**

> «Numerical results reveal complex optimal trading regions and show that the optimal investment
> strategy differs substantially from the V-shaped strategy observed in the frictionless case.» (аннотация)

V-образность в безфрикционном случае (воспроизведён Capponi & Zhang, 2024): доля в акции
снижается при подходе богатства к G₁ и растёт после его превышения —

> «This V-shaped adjustment reflects an investor’s tendency to reduce risk near the target level
> to avoid missing the primary goal.» (§8.1)

При равных весах `w₁ = w₂` и без издержек: цель 1 не финансируется вовсе при богатстве ниже 3.6;
при богатстве от 3.6 до 6.6 около 3.6 остаётся в акции, остаток идёт на цель 1 (§8.2.3).
При `w₁ = 5w₂` агент отдаёт все доступные средства на первую цель.

**Отношение к FINPILOT.** 🔴 Бьёт по новизне сильнее, чем Das et al. 2026: у Das целевая функция
— полезность выполненных целей (по сути бинарно/по Парето-комбинациям), а здесь ровно
«минимизировать взвешенную сумму недоборов при непрерывном распределении денег по целям» —
это функционально то же, что делает наш SAW по целям. Отличия, которые держатся: нет долга,
нет ПДН, нет обязательного резерва как отдельного неразменного ограничения, горизонт —
инвестиционный, а не помесячный поток.
### 2.3 JBF 2021/2022 «Dynamic optimization for multi-goals wealth management» — 🔴 ЗАКРЫТ ПРЕПРИНТОМ АВТОРА, ПРОЧИТАН

Пейволл ScienceDirect обойдён: **препринт лежит открыто на личной странице Sanjiv Das**.
Канал: `WebSearch` → `curl` → `https://srdas.github.io/Papers/MultWealthGoals.pdf` →
HTTP 200, 1 100 479 байт, `application/pdf` → `pdftotext` → 3741 строки текста.

Sanjiv R. Das (Santa Clara), Daniel Ostrov (Santa Clara), Anand Radhakrishnan (Franklin Templeton),
Deep Srivastav (Franklin Templeton). «Dynamic Optimization for Multi-Goals Wealth Management».
Версия препринта датирована **May 25, 2021** — совпадает с `S0378426621001515` (available online 2021);
журнальная версия — Journal of Banking & Finance, vol. 140, 2022, art. 106192.
JEL: G11, G40, G50. Keywords: «Goals-based investing, dynamic programming, retirement planning».
Это тот самый «Das et al. (2022b)», на который опирается MetaRL-статья участка 1.

**Аннотация, дословно:**

> «We develop a dynamic programming methodology that seeks to maximize investor outcomes over
> multiple, potentially competing goals (such as upgrading a home, paying college tuition, or
> maintaining an income stream in retirement), **even when financial resources are limited.** Unlike
> Monte Carlo approaches currently in wide use in the wealth management industry, our approach uses
> investor preferences to dynamically make the optimal determination for fulfilling or not fulfilling
> each goal and for selecting the investor’s investment portfolio. This can be computed quickly, even
> for numerous investor goals spread over different or concurrent time periods, where **each goal may
> be all-or-nothing or may allow for partial fulfillment.** The probabilities of attaining each (full or
> partial) goal under the optimal scenario are also computed… This approach vastly outperforms buy
> and hold strategies and target-date funds.»

**Новое определение риска (§1), дословно:**

> «Traditionally, risk is defined as the volatility of the investments in an investor’s portfolio.
> In contrast, for GBWM with a single goal, risk is defined as the probability that an investor does
> not meet that financial goal… For multiple goals in well-funded portfolios… It becomes the
> probability that the investor will not be able to attain all their goals.»

**Переменные модели (§2.1):** периоды t = 0…T с шагом h лет; вливания I(t) > 0; l_max портфелей
на эффективной границе с упорядочением μ₁ < … < μ_lmax и σ₁ < … < σ_lmax; векторы стоимостей
c(t) и полезностей u(t) с компонентами k = 1…k_max(t); начальное богатство W(0); сетка богатства
из i_max значений с равномерным логарифмическим шагом, W_min — небольшая положительная величина
(«a dollar or five dollars, which essentially corresponds to being bankrupt»).

🔴 **Построение множества альтернатив года — дословный первоисточник Парето-фильтра**
(на него ссылается MetaRL-статья, §2.3 препринта). Пример: три одновременные цели,
цель 1 — all-or-nothing (2 варианта), цель 2 — с одним частичным уровнем (3 варианта),
цель 3 — с тремя частичными (5 вариантов):

> «Since there are two possibilities for Goal 1 (fulfill the goal or forgo it), three possibilities for
> Goal 2, and five possibilities for Goal 3, we have a total of 2 × 3 × 5 = 30 possibilities for combined
> goal fulfillment at this time period.»

Затем комбинации сортируются по стоимости и прореживаются:

> «Finally, starting with the second column, we remove any column where the preceding column has a
> higher (or equal) utility. We remove these columns because it never makes sense to obtain them,
> given that the previous column attains a higher (or equal) total utility at a lower cost.
> **This reduces the 24 cases to 13.** These 13 cases comprise the final cost and utility vectors.»

То есть 30 сырых комбинаций → 24 после отсева → **k_max(t) = 13** недоминируемых альтернатив года.
Программа хранит соответствие каждой комбинации исходным целям («the k = 8 entry, which has a cost
of $40 and a utility of 550, corresponds to not taking Goal 1, total fulfillment of the Goal 2, and
partial fulfillment of the Goal 3 at a cost of $20»).

**Уравнение Беллмана (4), дословно:**

> «V(W_i(t)) = max_{k,l} [ u_k(t) + Σ_{J=1}^{i_max} V(W_J(t+1)) · q(W_J(t+1) | W_i(t), c_k(t), μ_l) ]»

Сложность: `O(i_max (k_max(t) + l_max))` за счёт разделения оптимизации на две (сначала по l_max
портфелям, потом по k_max(t) целям) вместо `k_max(t) × l_max`. Реализация — NumPy + JIT в Python.

🔴🔴 **САМОЕ ВАЖНОЕ ДЛЯ НОВИЗНЫ FINPILOT: в реалистическом примере §4.5 ДОЛГ ПРИСУТСТВУЕТ.**
Пара «mid-thirties», горизонт 60 лет, W(0) = $100 тыс., i_max = 1221, время счёта 17 секунд.
Доходы (infusions): зарплата $75 тыс., +4% в год до пенсии в 69 лет; Social Security $120 тыс. с 70 лет.
Цели разбиты на четыре тира, и **Tier 1 (highest priority) начинается с ипотеки:**

> «1. Tier 1 (highest priority) goals
> (a) **Mortgage:** Assume the couple needs to pay a fixed annual rate of $10 for the next 25 years
> (t = 1 through t = 25) to pay off what remains from a 30 year fixed mortgage.
> (b) Property tax… (c) Long term care insurance… (d) Medical expenses… (e) Everyday expenses:
> Assume these start at $60 per year and go up at a 3% rate of inflation. Further, if necessary,
> these can be trimmed to $50 per year by cutting costs that are not as crucial.»

Всего: «in total over the 60 year timeframe, the couple is considering **301 full goals and 138 partial
goals**» (те самые цифры, которые MetaRL-статья цитирует как случай CP2).

Результат (Таблица 9): «Each Tier 1 goal has a greater than 99% chance of being fulfilled and a greater
than 97% chance of being fully fulfilled… the probability of attaining the Tier 4 goals varies from
0 to 98%». В строках таблицы полезностей по целям первой идёт «Mortgage payments».

По траекториям (§4.5.1): при плохой доходности алгоритм жертвует Tier 3–4 — «philanthropy… in years
7–37», «High School… years 10–12», «Trips… year 10 and year 20», «college goal could only be partially
met in years 14–16», «the wedding could not be funded in the poor case», — и вывод авторов:

> «It is precisely because the algorithm is taking the future into account, that it passes on some
> goals in the early years in order to enable taking later goals.»

Полезности: good path 576 485 из максимально возможных 577 055; poor path 574 540.

**🔴 Что именно это делает с новизной FINPILOT — точная граница.**
Ипотека здесь входит в ту же оптимизацию, что и цели, **но как экзогенный аннуитетный платёж
с высшим приоритетом**, то есть как «цель с большой полезностью», а не как объект стратегии
погашения. В работе НЕТ: (а) выбора, какой долг гасить быстрее (нет ставок по долгам, нет
Avalanche/Snowball), (б) досрочного погашения как альтернативы, (в) ограничения долговой нагрузки
(ПДН), (г) обязательного неснижаемого резерва. Единственное «жёсткое» ограничение — банкротство
как нижняя граница сетки богатства.
### 2.4 Deguest, Martellini, Milhau — 🔴 ТЕЗИС ПОДТВЕРЖДЁН ПО АВТОРСКОМУ ТЕКСТУ (не по аннотации магазина)

**Что было под сомнением.** В теме 13 формула «secure essential goals with the highest confidence
level and maximize the chances to reach aspirational goals» была взята из аннотации магазина.
Сама книга (World Scientific, 2021, ISBN 9789811240942, DOI 10.1142/12386) — платная, полного текста
в открытом доступе нет.

**Что добыто.**

**(а) Авторская библиографическая запись, а не магазин.** RePEc/HAL Post-Print `hal-03710225`
(`https://ideas.repec.org/p/hal/journl/hal-03710225.html`, HTTP 200, канал `curl`). Аффилиации
указаны полностью: Deguest — LEM UMR 9221, Martellini и Milhau — EDHEC Business School. Текст записи:

> «Grounded in the principles of asset pricing and portfolio optimisation, the goal-based investing
> approach leads to the design of investment solutions that truly respond to investors’ problems,
> which can most often be summarized as follows: **secure essential goals with the highest confidence
> level and maximize the chances to reach aspirational goals.** A series of case studies guides the
> reader through the implementation of goal-based investing… and explains how one can accommodate
> a variety of implementation features such as taxes, short-sales constraints, parameter estimation
> risk, as well as limited customisation.»

🔴 Оговорка честная: это по-прежнему **аннотация**, просто депонированная авторами/институтом,
а не текст книги. Сама по себе она тезис не «поднимает» до первоисточника.

**(б) 🔴 Тезис подтверждён в ТЕЛЕ авторской статьи, открытой полностью.**
Lionel Martellini, Vincent Milhau, John Mulvey. «Applying Goal-Based Investing to the Retirement
Issue», EDHEC-Risk Industry Analysis. Канал: `WebFetch` дал 403 → **`r.jina.ai` дал HTTP 200,
26 634 байта полного текста** (`https://climateimpact.edhec.edu/applying-goal-based-investing-retirement-issue`).
Дословно:

> «In most cases, however, individuals and households are under-funded; their replacement income
> needs in retirement exceed what can be financed via savings alone. In other words, the desired
> replacement income level is not affordable and therefore represents an **aspirational goal**
> (in the terminology of Chhabra et al. (2015)), the presence of which justifies the need for upside
> performance. In this context, a well-designed retirement solution should simultaneously generate
> a high probability for individuals to achieve their aspirational/target levels of replacement income,
> but it should also **secure some essential/minimum levels of replacement income in order to ensure
> that basic needs in retirement will be satisfied regardless of market performance.**»

И следом:

> «The recognition that investors aspire to secure both essential and aspirational goals with high
> probabilities is leading to the new GBI investment paradigm in individual money management, where
> investors’ problems can be fully characterized in terms of their goals. Goal-based investing is the
> counterpart of liability-driven investing (LDI), which has become the relevant paradigm in
> institutional money management.»

**Вывод: тезис ПОДТВЕРЖДЁН**, авторство Martellini/Milhau корректно, а терминология
«essential / aspirational» самими авторами атрибутирована **Chhabra et al. (2015)** — то есть
первоисточник термина ещё глубже, это не изобретение книги 2021 года.

**Механика «essential goal» из той же статьи (полезно как образец жёсткого ограничения):**
годовая цель — ограничить падение покупательной способности замещающего дохода на 20% за
календарный год; это задаёт **пол (floor)**, который стратегия обязана соблюдать всегда,
и он пересчитывается каждый год как 80% текущих сбережений. Численно: 10 000 сценариев;
стандартный target-date fund даёт **16.1% вероятности** хотя бы одного годового убытка выше порога
и худший сценарий свыше **35%**, тогда как GBI-стратегия удерживает 20% во всех сценариях;
при улучшенном PSP рост покупательной способности на 200% достигается с вероятностью **78.1%**
против примерно 50% у target-date fund.

🔴 **Это прямая аналогия нашим жёстким инвариантам:** «essential goal» у них реализован именно как
floor-ограничение, не подлежащее размену на полезность, — ровно та роль, которую у нас играют
Rt ≥ 0 и ПДН ≤ 0.40. То есть архитектурный приём «часть целей — ограничение, а не слагаемое
в свёртке» в GBI-литературе уже канонизирован.

**Долг:** в статье слова `debt`/`loan`/`mortgage` не встречаются ни разу (механическая проверка).

## Участок 3. Schwab Intelligent Portfolios — Goal Tracker — 🔴 ЗАКРЫТ, ПОРОГИ ДОБЫТЫ ЧИСЛАМИ

**Редирект пройден и оказался ложным следом.** `https://www.schwab.com/intelligent-portfolios`
взят целиком (`curl`, HTTP 200, 583 029 байт; и через `r.jina.ai`, 55 364 байта) — **механики
Goal Tracker на нём нет вовсе**, это продуктовая витрина (6 риск-профилей, «more than 80 variations»
портфелей). Нужная страница — другая: `https://www.schwab.com/automated-investing/goal-tracker`
(канал `r.jina.ai`, HTTP 200, 20 254 байта, прочитана целиком).

### 3.1 Механика

> «Goal Tracker saves your goal and monitors **daily** whether your portfolio is "on target," "at risk,"
> or "off target." These graphics are dynamic, and you can make adjustments to variables, such as your
> contributions, and see how those changes impact your potential to reach your goal.»

Два типа целей: **savings goal** (накопить сумму) и **income goal** (не обнулить счёт до заданной даты).

### 3.2 Что за «long-term expected return estimates and simulations» — ответ

> «Instead, the Goal Tracker uses **Monte Carlo simulation** to provide probability analysis on the
> likelihood that your assets will reach your savings goal or that your income will last until
> a selected end date.»

Сколько сценариев — 🔴 **в тексте противоречие, привожу как есть, обе формулировки дословно:**

> «We do this for every month until the end of your stated time horizon to calculate a hypothetical or
> projected ending balance. **We repeat this series of draws 999 times,** to give us a range of
> possible outcomes.»

и тут же ниже, при описании перцентилей: «the 750th best out of **1,000** ending balances»,
«the 500th best out of 1,000 ending results», «the 250th best of 1,000», «the 100th best of 1,000».
То есть 999 повторов + исходный прогон = 1000 исходов, но прямо это не сказано.

Шаг симуляции — **месячный**. Источник параметров:

> «Goal Tracker uses long-term return estimates provided by **Charles Schwab Investment Management Inc.
> (CSIM)**… To create these long-term return estimates, CSIM uses a set of factors including interest
> rates, earnings, dividends and others to estimate future returns and risk on a wide range of asset
> classes including equities, bonds, and commodities, etc.»

🔴 Важная оговорка о том, чего в модели НЕТ:

> «The performance projections assume monthly rebalancing and reinvestment of interest and dividends.
> **They do not include inflation, fees or taxes.**»

Четыре сценарных среза: «better» — 75-й перцентиль (превзойдёте в 25% симуляций), «average» —
50-й, «worse» — 25-й (достигнете в 75% симуляций), «very poor» — 10-й (достигнете в 90%).
Иллюстративный пример: старт $100 000, без довзносов, 10 лет → не менее $140 000 в «worse»,
$172 000 в «average», $212 000 в «better».

### 3.3 🔴 ПОРОГИ ТРЁХ СОСТОЯНИЙ — ЧИСЛА (Exhibit 4, savings goal)

| Статус | Определение (дословно) |
|---|---|
| **«On Target»** | «Better than 50% chance of reaching your goal» |
| **«At Risk»** | «Between a 25% and 50% chance of reaching your goal» |
| **«Off Target»** | «Less than a 25% chance of reaching your goal» |

Пояснение к «off target», дословно:

> «We don’t believe that you should anticipate or rely on a market performing well above average to
> achieve your goal. You should increase your contributions or change your goal.»

Числовые примеры со страницы: цель $155 795 за 18 лет при медианной проекции $332 831 — «on target»;
цель $450 000 при той же проекции ~$332 000 — «at risk»; цель $500 000 — «off target».

### 3.4 🔴 Для income goal пороги ДРУГИЕ и выше (Exhibit 8) — этого в теме 13 не было

> «Goal Tracker has a **higher threshold for "on target" in the income goal** because the stakes are
> likely higher if your account runs out of money than it is if you miss a savings goal.»

| Статус | Определение (дословно) |
|---|---|
| **«On Target»** | «Between a 90% and 75% chance of your money lasting» |
| **«At Risk»** | «Less than a 75% chance but better than a 50% chance or your money lasting» *(опечатка «or» вместо «of» — в оригинале)* |
| **«Off Target»** | «Less than a 50% chance of your money lasting» |

> «We believe that you should be able to sustain spending with between 90% and 75% confidence.»
> «Your income goal is "off target" if you have money left over only in the "average" market or better
> (i.e., success less than 50% of the time). **The chance of having money left is a 50/50 coin flip
> or worse.**»

**Содержательный вывод для нас:** Schwab различает целевую надёжность по ТИПУ цели — накопительная
цель считается благополучной уже при 50%, а «не остаться без денег» требует 75–90%. Это ровно та же
дихотомия essential/aspirational, что у Martellini (участок 2.4), но выраженная порогами вероятности
в живом продукте.

### 3.5 Работа с долгом

**Нет.** Механическая проверка `debt|loan|mortgage|liabilit` по обеим страницам: на странице Goal
Tracker — ноль совпадений; на витрине Intelligent Portfolios совпадения только про ипотечные
продукты банка Schwab в навигации и про класс активов «Bank Loans / floating-rate notes» в составе
портфелей. **Долг клиента в постановку цели не входит.**

## Участок 4. Kitces — «probability of success» — 🔴 ЗАКРЫТ ПЕРВОИСТОЧНИКОМ, ЦИТАТА ПОДТВЕРЖДЕНА ДОСЛОВНО

### 4.1 🔴 Канал: kitces.com БЕРЁТСЯ через `r.jina.ai`

Замер 10.09.2026: `curl -s "https://r.jina.ai/https://www.kitces.com/blog/..."` → **HTTP 200,
40 354 байта** полного текста. То есть прежний вывод «kitces.com глухой» был выводом о двух
каналах (`WebFetch` 403, `curl` с UA 403), а не о доступности сайта. Текстовый прокси его пробивает.
Это надо занести в реестр каналов: **kitces.com следует из списка «глухих» ИСКЛЮЧИТЬ.**

### 4.2 Первоисточник и точная цитата

Derek Tharp, Ph.D., CFP, CLU, RICP (Lead Researcher at Kitces.com, Head of Innovation at Income Lab,
Assistant Professor of Finance, University of Southern Maine). «Making Monte Carlo Results More
Relevant By Finding The Right Level Of Abstraction», Nerd’s Eye View, **опубликовано 2021-04-07**.
URL: `https://www.kitces.com/blog/multidimensional-abstraction-to-communicate-monte-carlo-simulation-probability-and-magnitude-of-success/`

🔴 **Формулировка из темы 13 подтверждена ДОСЛОВНО** (Executive Summary):

> «For instance, ‘probability of success’ – the primary metric used for conveying preparedness for
> retirement within most modern planning software – is known to have a number of issues. In particular,
> **‘probability of success/failure’ entirely misses the dimension of ‘magnitude of success/failure’,**
> which is highly important for developing a rich qualitative understanding of a retiree’s plan
> dynamics. For instance, a plan with a high probability of failure and a low magnitude of failure is
> qualitatively different than a plan with a high probability of failure and a high magnitude of
> failure, but in a world where only ‘probability of success’ is reported, then these two plans will
> look identical.»

Уточнение авторства: это текст **Тарпа на площадке Kitces.com**, а не лично Майкла Китсеса.
В теме 13 приписывать тезис «Kitces» допустимо только как площадке/школе.

### 4.3 Что ещё даёт статья — сверх подтверждения

**(а) Тезис о «probability of adjustment».** Дословно:

> «‘probability of success’ also does not convey to clients that they can adjust their spending to
> avoid failure, which further paints a distorted picture of reality. While this abstraction can
> perhaps be improved by framing around ‘probability of adjustment’ … it is nonetheless woefully
> incomplete without addressing the dimension of *magnitude*.»

И математическая оговорка:

> «it is not just scenarios that “fail” that would trigger spending adjustments. Instead, scenarios
> that start toward a path of failure would also trigger adjustment… consequently, **the mathematical
> probability that an adjustment would occur is actually higher than the probability of failure itself.**»

**(б) 🔴 Готовая однопараметрическая метрика — Fullmer’s Shortfall Risk.** Дословно:

> «Richard Fullmer proposed Shortfall Risk, a single metric that would capture both the probability of
> failure *and* magnitude of failure:
> **Shortfall Risk = Probability of Shortfall × Magnitude of Shortfall**»
> «Magnitude of Shortfall is the amount of money one wanted to spend but could not because they ran
> out of money (expressed as a percentage of the initial portfolio value).» (ссылка: DOI 10.1002/9781119200826.ch13)

И сразу критика этой свёртки, которая нам полезна как аргумент против одной агрегированной цифры:

> «Scenario A: 50% probability of shortfall; 10% magnitude of shortfall… Scenario B: 10% probability
> of shortfall; 50% magnitude of shortfall… Representing both as the same shortfall risk (.05 in this
> case) is not a very useful level of abstraction.»
> «Arguably, Fullmer’s model is most insightful when the Probability of Shortfall and Magnitude of
> Shortfall remain as two distinct concepts.»

Предлагаемые автором две «правильные» размерности: **(a) likelihood of adjustment и (b) magnitude
of adjustment** — не вероятность и глубина провала, а вероятность и величина ПОПРАВКИ.

### 4.4 Независимое подтверждение по существу — David Blanchett, CFA Institute

Дополнительно взят независимый источник (канал `r.jina.ai`, HTTP 200, 8 933 байта):
David Blanchett, «Rethinking Retirement Planning Outcome Metrics», CFA Institute Enterprising
Investor, 2023-04-10, основан на его статье в **Financial Analysts Journal** «Redefining the Optimal
Retirement Income Strategy» (DOI 10.1080/0015198X.2022.2129947). Дословно:

> «Success-related metrics treat the outcome as binary, however, and don’t describe the magnitude of
> failure or how far the individual came from accomplishing the goal. According to such metrics,
> **it doesn’t matter whether the retiree fails in the 10th or 30th year or by $1 or $1 million dollars.
> All failure is treated the same.**»

Численный пример: цель $100/год на 10 лет; в пяти прогонах цель выполнена частично —
«Using the average goal completion, **90% of the goal is covered, on average, while success rates
indicate a 50% chance of success.** Though based on identical data, these two metrics give very
different perspectives about the safety of the target level spending.»

Практический вывод Бланшетта, важный для калибровки порогов:

> «Those financial advisers who continue to rely on success rates should dial their targets down a bit.
> According to my research, **80% is probably the right target.** This may seem low: Who wants a 20%
> chance of failure? But the lower value reflects the fact that “failure” in these situations is rarely
> as cataclysmic as the metric implies.»

И развитие темы в сторону неравноценности целей — прямая опора для нашего разделения
обязательных и необязательных статей:

> «not funding essential expenses like housing or health care will likely lead to more dissatisfaction
> than cutting back on travel or other flexible items… Goal-completion percentages can be further
> modified to incorporate diminishing marginal utility… based on prospect theory.»

### 4.5 Третье независимое подтверждение — Krabichler & Wunsch (участок 2.1)

Рецензируемая математическая формулировка того же: «a goal missed by a hair’s breadth is still
a goal missed… This indifference for the size of the shortfall constitutes a major drawback of
probability-maximizing strategies for practical purposes» (arXiv:2105.07915v2, §1.2).

**Итого по участку 4:** тезис держится тремя независимыми источниками (Tharp/Kitces 2021;
Blanchett/FAJ+CFA 2022–2023; Krabichler & Wunsch 2021) плюс уже прочитанный в теме 13 Estrada (2018).
Пометку «НЕ ПОДТВЕРЖДЕНО» в §2.3 темы 13 снимать.

## Итоги

### 1. Прямой ответ по каждому хвосту

| # | Хвост | Вердикт | Чем закрыт |
|---|---|---|---|
| 1 | **arXiv:2605.02300** — Das, Khadilkar, Mittal, Ostrov, Srivastav, Wang (2026), MetaRL GBWM | 🟢 **ЗАКРЫТ ПЕРВОИСТОЧНИКОМ, прочитан целиком** | `curl` → `arxiv.org/html/2605.02300v1`, HTTP 200, 839 609 байт. Плюс выяснено сверх задания: статья не препринт, а публикация — J. of Finance and Data Science, vol. 12, 2026, 100186, DOI 10.1016/j.jfds.2026.100186 |
| 2 | **arXiv:2105.07915** — Krabichler & Wunsch, «Hedging Goals» | 🟢 **ЗАКРЫТ ПЕРВОИСТОЧНИКОМ** | `curl` → `arxiv.org/html/2105.07915v2`, HTTP 200, 424 715 байт. По нашей постановке ортогонален; ценность — рецензируемая опора для участка 4 |
| 3 | **arXiv:2510.21650** — Bayraktar, Han, Zhang, fixed transaction costs | 🟢 **ЗАКРЫТ ПЕРВОИСТОЧНИКОМ** | `curl` → `arxiv.org/html/2510.21650v1`, HTTP 200, 1 701 170 байт |
| 4 | **JBF, `S0378426621001515`** — «Dynamic optimization for multi-goals wealth management» | 🟢 **ЗАКРЫТ ПРЕПРИНТОМ АВТОРА** (пейволл ScienceDirect обойдён, не пробит) | `srdas.github.io/Papers/MultWealthGoals.pdf`, HTTP 200, 1 100 479 байт → `pdftotext`, 3741 строка. Версия от 25.05.2021 = та же работа, что JBF vol. 140 (2022) 106192 |
| 5 | **Deguest, Martellini, Milhau (2021), книга** | 🟡 **ТЕЗИС ПОДТВЕРЖДЁН, но НЕ по тексту книги** | Книга платная, полного текста нет. Формула подтверждена (а) авторской записью HAL/RePEc `hal-03710225`, DOI 10.1142/12386 — это по-прежнему аннотация, но авторская, а не магазинная; (б) 🔴 **телом открытой статьи** Martellini/Milhau/Mulvey «Applying Goal-Based Investing to the Retirement Issue» (`r.jina.ai`, HTTP 200, 26 634 байта), где доктрина essential/aspirational изложена в основном тексте. Пометку «взято из аннотации магазина» **снимать** |
| 6 | **Schwab Intelligent Portfolios, Goal Tracker (§6.4)** | 🟢 **ЗАКРЫТ, ПОРОГИ ДОБЫТЫ ЧИСЛАМИ** | Редирект пройден: `schwab.com/intelligent-portfolios` (HTTP 200, 583 029 байт) оказался **ложным следом** — механики там нет. Нужная страница `schwab.com/automated-investing/goal-tracker` (`r.jina.ai`, HTTP 200, 20 254 байта). Пороги savings: >50% / 25–50% / <25%. Пороги income (в теме 13 их не было вовсе): 90–75% / <75% и >50% / <50%. Монте-Карло, «999 times» при описании перцентилей «out of 1,000», месячный шаг, оценки CSIM, **без инфляции, комиссий и налогов** |
| 7 | **Kitces — «probability of success» (§2.3, «НЕ ПОДТВЕРЖДЕНО»)** | 🟢 **ЗАКРЫТ ПЕРВОИСТОЧНИКОМ, ЦИТАТА ДОСЛОВНАЯ** + уточнено авторство | `r.jina.ai` → kitces.com, HTTP 200, 40 354 байта. Автор — **Derek Tharp**, статья от 2021-04-07, не лично Kitces. Фраза «‘probability of success/failure’ entirely misses the dimension of ‘magnitude of success/failure’» подтверждена буква в букву. Пометку «НЕ ПОДТВЕРЖДЕНО» **снимать** |

**Снятых как неверные — нет.** Единственная существенная поправка: авторство тезиса участка 4
(Tharp, а не Kitces лично) и статус источника участка 2.4 (доктрина подтверждена статьёй, книга
остаётся непрочитанной).

---

### 2. 🔴 Что из добытого меняет формулировку новизны FINPILOT

**Рамка на входе.** Тема 16 сняла новизну по **методу** (SAW дословно совпадает с FSAdvisor,
Felfernig & Kiener IAAI-05) и по **объяснимости** (вклад критерия = HOW-explanation, канон с 2005).
Тема 13 сняла новизну по **постановке** (Princeton arXiv:2403.06011 — «долг + цели в одной
оптимизации»). Устоял **только объект оптимизации**: распределение собственного денежного потока
(продавца нет) и нерелаксируемость инвариантов.

**Прямой ответ: да, новый материал бьёт и по объекту тоже — по двум из трёх его составляющих.**

**(а) 🔴 «Выбор подмножества целей под ограничением ресурса» — не наше. Снято дважды.**
Das et al. (2026), §2.1: *«they must determine which goals to pursue and which to abandon to preserve
the capital required for high-priority future aspirations»*. Более того, их постановка **сильнее
нашей**: помимо «взять/не взять» есть частичное выполнение с уменьшенной стоимостью и уменьшенной
полезностью, а множество альтернатив года строится как все комбинации по всем одновременным целям
с **отсевом по Парето** (Прил. E; первоисточник приёма — Das et al. 2021/2022, где 30 сырых
комбинаций → 24 → **k_max = 13** недоминируемых). Наш перебор 66 альтернатив с шагом 10% —
дискретизация того же множества, **без** Парето-фильтра. Формулировка новизны через «перебор
альтернатив распределения по целям» больше не защитима.

**(б) 🔴 «Линейная свёртка по взвешенным целям» — не наше. Снято третий раз, теперь ещё и в
математической литературе.** Bayraktar, Han, Zhang (2025), (2.15):
`inf E[ Σ_k w_k (G_k − θ_k)^+ ]` — минимизация **взвешенной суммы недоборов** при **непрерывном**
распределении денег θ_k по целям. Это функционально то же, что делает наш SAW по целям, только
записанное как задача стохастического управления. То есть удар темы 16 по методу подтверждён
из независимой ветки литературы (math.OC, а не рекомендательные системы).

**(в) 🔴 «Долг в одной оптимизации с целями» — не наше, и это ВТОРОЕ независимое опровержение
после Princeton.** В Das et al. (JBF, §4.5) реалистический кейс на 60 лет содержит **ипотеку как
цель Tier 1** — «pay a fixed annual rate of $10 for the next 25 years to pay off what remains from
a 30 year fixed mortgage», и в таблице полезностей по целям первой строкой идут «Mortgage payments».
Всего 301 полная и 138 частичных целей. Значит, тезис «мы первые, кто кладёт долг и цели в одну
оптимизацию» опровергнут не только препринтом Princeton 2024, но и рецензируемой статьёй JBF 2022.

**(г) 🔴 «Жёсткие ограничения вместо слагаемых свёртки» — тоже не изобретение.**
Martellini/Milhau/Mulvey: essential goal реализован как **floor**, который «the strategy should
respect at all times» (пол = 80% доступного дохода на начало года, пересчёт ежегодно), тогда как
aspirational goals оптимизируются по вероятности. Архитектурный приём «часть целей — ограничение,
а не слагаемое» в GBI канонизирован. Schwab делает то же продуктово: для income goal порог «on
target» поднят до 75–90% против 50% для savings goal, прямо потому что «the stakes are likely
higher if your account runs out of money».

**Что после всего этого ещё держится — и держится честно (четыре пункта, не больше):**

1. **Долг как объект СТРАТЕГИИ, а не как экзогенный платёж.** У Das долг — фиксированный аннуитет
   с высоким приоритетом; выбора «какой долг гасить быстрее» нет, ставок по долгам нет,
   досрочного погашения как альтернативы нет. Avalanche-фильтр (приоритет по ставке) не имеет
   аналога ни в одном из семи прочитанных источников.
2. **ПДН ≤ 0.40 как жёсткий инвариант.** Ни в одном источнике нет ограничения на долговую нагрузку.
   Ближайший аналог — запрет коротких позиций `x ∈ [0,∞)²` у Bayraktar et al. и «can’t afford it»
   у Das; это ограничения достаточности средств, а не нормативной нагрузки. Регуляторное
   происхождение (РФ) — вне охвата всей прочитанной литературы.
3. **Rt ≥ 0 как неразменный резерв.** У Das резерв неотличим от любой другой цели (был бы просто
   целью с большой полезностью); floor у Martellini ближе всего, но это floor по доходу, а не
   обязательный денежный буфер.
4. **Горизонт и объект потока.** Все семь источников работают с инвестируемым капиталом и годовым
   шагом на горизонте 3–100 лет. Распределение месячного свободного потока домохозяйства с долгами
   — не рассматривается никем из них.

**Вывод, который надо унести:** формулировку новизны следует переписать с «постановка/метод/перебор
альтернатив» на **связку «стратегия погашения долга (ставки, Avalanche) + нормативное ограничение
ПДН + неразменный резерв, на горизонте месячного потока»**. Любая формулировка, начинающаяся со
слов «выбор подмножества целей», «взвешенная свёртка» или «долг и цели вместе», опровергается
первоисточником в один ход.

---

### 3. Что не добыто и почему (коды ответа по каналам)

| Объект | Каналы и коды | Итог |
|---|---|---|
| Полный текст книги Deguest/Martellini/Milhau (World Scientific, 2021) | Открытой версии не существует; проверены RePEc (HTTP 200 — только аннотация), EDHEC (`r.jina.ai` HTTP 200 — «Register to download PDF») | **Недоступен (пейволл).** Тезис при этом подтверждён обходным путём — статьёй тех же авторов |
| EDHEC-Risk Publication «Introducing a Comprehensive Investment Framework for GBWM» (март 2015, Deguest/Martellini/Milhau/Suri/Wang) | Прямая ссылка на PDF `climateimpact.edhec.edu/sites/risk/files/...` → **HTTP 404** (56 118 байт HTML-заглушки). Страница публикации: `WebFetch` → **403**, `r.jina.ai` → **HTTP 200**, но тело = «Register to download PDF» | **Не добыт: регистрационная стена.** `r.jina.ai` пробивает антибот, но не логин — подтверждение известного ограничения канала |
| Журнальная версия JBF `S0378426621001515` на ScienceDirect | Не пробовалась дольше одной итерации по прямому указанию задания | **Не нужна:** препринт автора идентичен по содержанию |
| Приложения A–D arXiv:2510.21650 (доказательства вязкостных решений) | Доступны, HTTP 200 | **Сознательно не читались:** техника доказательства к вопросу не относится |
| Точное число симуляций Schwab Goal Tracker | Страница взята целиком | **Противоречие в самом источнике** («999 times» против «out of 1,000»), зафиксировано дословно, домысливать не стал |

**Ничего не осталось «недоступным по вине канала», кроме двух платных объектов EDHEC/World
Scientific.** Ни одна попытка не завершилась статусом «не смог открыть» без указания кода.

---

### 4. Метод поиска

**Запросы `WebSearch` — 5 штук, все результативные:**
1. `Das Ostrov "Dynamic optimization for multi-goals wealth management" preprint pdf` → дал ссылку
   на `srdas.github.io`, которая и закрыла пейволл ScienceDirect.
2. `Martellini Milhau EDHEC "essential goals" "aspirational goals" goal-based investing framework paper`
3. `"Introducing a Comprehensive Investment Framework for Goals-Based Wealth Management" EDHEC 2015 pdf`
4. `Schwab Intelligent Portfolios "Goal Tracker" "on target" "off target" probability`
5. `Kitces "probability of success" misses "magnitude" of failure retirement Monte Carlo critique`
   (с `blocked_domains: kitces.com`) → вывел на CFA Institute/Blanchett, а оттуда — на точный URL
   статьи Тарпа, который затем взят напрямую.

**Объём просмотренного (только полностью взятые документы):**

| Документ | Канал | Байт |
|---|---|---|
| arXiv:2605.02300v1 (HTML) | `curl` UA | 839 609 (→ 156 336 симв. текста, 1830 строк) |
| arXiv:2510.21650v1 (HTML) | `curl` UA | 1 701 170 (→ 205 671 симв.) |
| arXiv:2105.07915v2 (HTML) | `curl` UA | 424 715 (→ 66 556 симв.) |
| Das et al., препринт JBF (PDF) | `curl` UA + `pdftotext` | 1 100 479 (→ 3741 строка) |
| schwab.com/intelligent-portfolios | `curl` UA / `r.jina.ai` | 583 029 / 55 364 |
| schwab.com/automated-investing/goal-tracker | `r.jina.ai` | 20 254 |
| kitces.com — Tharp, «Right Level Of Abstraction» | `r.jina.ai` | 40 354 |
| kitces.com — «Reframing Monte Carlo Results» | `r.jina.ai` | 29 943 |
| EDHEC — «Applying GBI to the Retirement Issue» | `r.jina.ai` | 26 634 |
| CFA Institute — Blanchett | `r.jina.ai` | 8 933 |
| RePEc/HAL `hal-03710225` | `curl` UA | HTTP 200 |
| arXiv abs-страницы (2 шт.) | `curl` UA | 39 625 + 39 949 |

Итого ~4.9 МБ сырья, из них четыре полных научных текста прочитаны по разделам, а не по аннотациям.
Подагенты **не запускались** (0 из разрешённых 2) — задача решилась последовательно, веерного
запуска не было.

**Приёмы, которые сработали:**
- 🔴 **`WebFetch` на PDF не понадобился вовсе:** arXiv в 2026 отдаёт HTML-версию (`/html/<id>v1`)
  для всех трёх статей, и `curl` берёт её напрямую. Проверка версий перебором `v1/v2/v3`
  (404 на несуществующих) дешевле, чем угадывание.
- Пейволл издателя обходится **личной страницей автора**, а не архивами: один поисковый запрос
  вида `<авторы> "<точное название>" preprint pdf`.

---

### 5. 🔴 Методическая находка о каналах — заносить в реестр

**`kitces.com` из списка «глухих» ИСКЛЮЧИТЬ.** Прежний вывод «сайт глухой, 403 дважды» был выводом
о **двух каналах** (`WebFetch` → 403; `curl` с браузерным UA → 403), а не о доступности сайта.
Замер 10.09.2026: `curl -s "https://r.jina.ai/https://www.kitces.com/blog/..."` → **HTTP 200,
40 354 байта** полного текста статьи; второй файл того же домена — **HTTP 200, 29 943 байта**.
Два из двух.

**Правило на будущее:** «сайт глухой» без проверки текстового прокси — **незавершённый замер**,
а не результат. Формулировать следует «домен не берётся каналами 1–2», и только после
`r.jina.ai` — «не берётся вовсе». Это тот же класс ошибки, что «PDF нечитаем» (PIT: `WebFetch`
кладёт файл на диск), — утверждение о попытке, выданное за утверждение о доступности.

**Граница канала подтверждена в том же прогоне:** `r.jina.ai` обходит **антибот**, но не
**регистрационную стену** — EDHEC отдал HTTP 200 с телом «Register to download PDF».
Антибот и пейволл/логин — разные препятствия, первое прокси снимает, второе нет.

**Побочно:** `schwab.com` берётся и обычным `curl` с UA (HTTP 200, 583 КБ), и прокси —
редирект `intelligent.schwab.com/page/goal` → `www.schwab.com/intelligent-portfolios` пройден,
но целевая страница оказалась не той: механика Goal Tracker живёт по адресу
`/automated-investing/goal-tracker`. **Пройденный редирект не гарантирует, что попал на нужный
документ** — проверять по содержимому, а не по коду 200.
