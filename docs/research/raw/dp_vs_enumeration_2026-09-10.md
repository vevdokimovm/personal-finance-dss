# Тема 38. Оптимальное управление и динамическое программирование: почему не DP, а перебор

**Дата:** 2026-09-10
**Статус:** закрыта
**Задача:** готовый ответ с числами на вопрос защиты «почему не DP, а перебор 66 альтернатив».

---

## Участок 1. Аппарат DP для нашей задачи

### 1.1 Уравнение Беллмана — каноническая постановка

**Источник (добыт целиком, `pdftotext -layout`, 3016 строк):** Christopher D. Carroll,
*Solution Methods for Microeconomic Dynamic Stochastic Optimization Problems* (SolvingMicroDSOPs),
версия 2022-04-07, Johns Hopkins University.
URL: `https://www.econ2.jhu.edu/people/ccarroll/SolvingMicroDSOPs.pdf` (HTTP 200, 2 081 230 байт).
🔴 Зеркало `llorracc.github.io/SolvingMicroDSOPs/SolvingMicroDSOPs.pdf` даёт **404** (9,4 КБ HTML) —
рабочий адрес именно econ2.jhu.edu.

**Задача (SolvingMicroDSOPs, §2 «The Problem», с. 4), дословно:**

> We are interested in the behavior a consumer whose goal in period t is to maximize
> expected discounted utility from consumption over the remainder of a lifetime that ends
> in period T:

$$\max\ \mathbb{E}_t\left[\sum_{n=0}^{T-t}\beta^{n}u(c_{t+n})\right]\qquad(1)$$

Уравнения перехода (там же, формула (2), с. 4):

```
a_t     = m_t - c_t
b_{t+1} = a_t R_{t+1}
y_{t+1} = p_{t+1} θ_{t+1}
m_{t+1} = b_{t+1} + y_{t+1}
```

Обозначения дословно из таблицы на с. 4:

| Символ | Значение (оригинал) |
|---|---|
| β | pure time discount factor |
| a_t | assets after all actions have been accomplished in period t |
| b_{t+1} | 'bank balances' (nonhuman wealth) at the beginning of t+1 |
| c_t | consumption in period t |
| m_t | 'market resources' available for consumption ('cash-on-hand') |
| p_{t+1} | 'permanent labor income' in period t+1 |
| R_{t+1} | interest factor (1 + r_{t+1}) from period t to t+1 |
| y_{t+1} | noncapital income in period t+1 |

**Рекурсивная (беллмановская) форма — SolvingMicroDSOPs, формула (3), с. 5, дословно:**

> As is well known, this problem can be rewritten in recursive (Bellman equation) form
>
> **v_t(m_t, p_t) = max_{c_t} u(c_t) + E_t[β v_{t+1}(m_{t+1}, p_{t+1})]**
>
> subject to the Dynamic Budget Constraint (DBC) (2) given above, where v_t measures
> total expected discounted utility from behaving optimally now and henceforth.

Полезность CRRA: `u(•) = •^{1-ρ}/(1-ρ)` (с. 4). В последнем периоде `v_{T+1}=0`, поэтому
`v_T(m_T,p_T) = m_T^{1-ρ}/(1-ρ)` (формула (4), с. 5).

**Разбор в наших терминах:**
- **переменные состояния** — `m_t` (кэш-он-хэнд) и `p_t` (перманентный доход); у нас к ним
  добавляются остатки долгов и накопленный резерв (см. §1.3);
- **управление** — `c_t`, потребление; всё, что не потреблено, идёт в `a_t`. В нашей задаче
  управление векторное: доля свободного потока на резерв / на долги / на цели (это ровно
  постановка Alaluf et al., тема 13);
- **функция ценности** — `v_t`, «total expected discounted utility from behaving optimally
  now and henceforth».

🔴 **Ключевой приём Carroll, прямо относящийся к нашему спору (§3 «Normalization», с. 5):**

> The single most powerful method for speeding the solution of such models is to redefine
> the problem in a way that reduces the number of state variables (if possible).

и итог нормализации (с. 6):

> if we solve the problem (5) which has only a single state variable m_t, we can obtain the
> levels of the value function, consumption, and all other variables of interest simply by
> multiplying the results by the appropriate function of p_t <...> We have thus reduced the
> problem from two continuous state variables to one (and thereby enormously simplified its
> solution).

То есть даже в каноне DP главная работа — **сократить размерность состояния до одной
переменной**. Это делается делением на перманентный доход и работает благодаря
однородности CRRA (`u(xy) = x^{1-ρ}u(y)`, с. 5). Для задачи с N разнородными долгами
(у каждого свои ставка и остаток) такой нормализующей переменной **нет** — см. §1.3.

**Второй приём Carroll, релевантный нам (§7.2, с. 41–42):** при нескольких управлениях он
НЕ решает многомерную задачу максимизации, а разбивает её на последовательность одномерных:

> multidimensional constrained maximization problems are difficult and sometimes quite
> slow to solve. There is a better way. Define the problem ṽ_t(a_t) = max_{ς_t} v_t(a_t, ς_t)
> <...> Thus we have transformed the multidimensional optimization problem into a sequence
> of two simple optimization problems for which solutions are much easier and more reliable.

**Третье, и это прямая поддержка нашей позиции по методу.** Аннотация SolvingMicroDSOPs,
с. 1, дословно:

> I present a specific set of methods that have proven useful in my own work (and explain
> why other popular methods, **such as value function iteration, are a bad idea**).

И развёрнуто на с. 11 (§5.3):

> the fact that the v̀_{T-1} function is a set of line segments is very evident. This figure
> provides the beginning of the intuition for why trying to approximate the value function
> directly is a bad idea (in this context).

Со сноской 14 (с. 11), которая касается ровно нашего случая:

> For some problems, especially ones **with discrete choices**, value function approximation
> is unavoidable; nevertheless, even in such problems, the techniques sketched below can be
> very useful across much of the range over which the problem is defined.

🔴 **Что это значит для нас.** Наша задача — с дискретным выбором (какой долг гасить первым,
класть ли в резерв), а по Carroll именно в задачах с дискретным выбором аппроксимация
функции ценности **неизбежна** и при этом плоха. Изящные методы Carroll (endogenous
gridpoints, method of moderation) опираются на гладкость и внутреннее решение по FOC —
дискретный выбор их ломает. Это первый технический аргумент против «просто возьмите DP».

### 1.2 Консумпционно-сберегательные модели (Carroll, Deaton, Zeldes)

**Carroll, buffer-stock.** Механика — в §1.1 выше (SolvingMicroDSOPs целиком добыт).
Теоретическая часть: Christopher D. Carroll, *Theoretical Foundations of Buffer Stock Saving*,
`https://llorracc.github.io/BufferStockTheory/BufferStockTheory.pdf` (HTTP 200, 1,8 МБ,
`pdftotext` дал 4626 строк — добыт целиком). Суть для нас: у нетерпеливого потребителя
с риском дохода возникает **целевой уровень буфера** (target wealth-to-income ratio), к которому
он тянет активы; выше цели — тратит, ниже — копит. Это ровно логика «подушки безопасности»
в FINPILOT, но выведенная из DP, а не постулированная.

**Deaton (1991), «Saving and Liquidity Constraints», Econometrica 59(5), 1221–1248.**
Авторская копия с личной страницы Принстона:
`https://www.princeton.edu/~deaton/downloads/Saving_and_Liquidity_Constraints.pdf`
(HTTP 200, 510 251 байт, добыт целиком). Постановка — та же беллмановская, плюс жёсткое
ограничение на заимствование (`x_{t+1} = (1+r)[x_t − f(x_t)] + y_{t+1}`, формула (14), с. 1229).

🔴 **Главное для нас — методический пассаж Deaton, с. 1229–1230, дословно:**

> Further results require a more intimate knowledge of the consumption function f(x), and
> since there is little hope of recovering closed form solutions, it is necessary to use the
> contraction mapping apparatus to compute the functions over some suitable grid. <...>
> Using Simpson's rule to evaluate the integral, and with a grid of **100 points**, the
> computations were easily done on a 386-series PC, **taking 5–20 minutes per calculation**
> depending on the values of the parameters.

и, ещё важнее, с. 1230:

> there are a number of computational disadvantages to using the value function approach.
> Firstly, in order to maximize over s for different values of x, it is necessary to have grids
> for both magnitudes, so that, to get adequate precision, **very large matrices are required**.
> Secondly, the utility function is typically not defined for all possible combinations of x and
> s <...> Finally, **the use of grids generates a policy function at the final stage that is a
> step function, which has to be "smoothed" once convergence is obtained**.

🔴 Два вывода, прямо бьющих в наш вопрос защиты:
1. **Одна** переменная состояния, сетка **100 точек** — и 5–20 минут счёта (на железе 1991 г.,
   но пропорция «одна переменная = уже заметный счёт» сохраняется, когда переменных 7–9);
2. **DP на сетке сам выдаёт кусочно-постоянную (ступенчатую) политику.** То есть «точный
   оптимум DP» на практике всё равно дискретизован — это тот же перебор, только по сетке
   состояний, а не по сетке действий. Наш перебор 66 альтернатив шагом 10 % **того же класса
   объекта**, а не принципиально более грубый. Это ключевой довод для §4.

**Zeldes (1989)** — «Optimal Consumption with Stochastic Income: Deviations from Certainty
Equivalence» (QJE 104(2), 275–298): численное решение DP с мультипликативным шоком дохода,
показавшее величину предупредительного мотива. 🔴 **Не добыт**: авторская копия на сайте
Wharton/личной странице не найдена, QJE — пейволл Oxford Academic. Использую как
контекстную ссылку, не как источник цитаты.

---

### 1.3 Проклятие размерности

**Источник (добыт целиком, `pdftotext`, 1610 строк):** John Rust, *Using Randomization to Break
the Curse of Dimensionality*, Econometrica 65(3), 1997, 487–516.
URL: `https://editorialexpress.com/jrust/crest_lectures/randomization.pdf` (HTTP 200, 637 606 байт).

**Определение, с. 489, дословно:**

> There is an important practical limitation to one's ability to solve continuous MDPs
> arbitrarily accurately, Bellman's curse of dimensionality. This is the well-known
> **exponential rise in the time and space required to compute an approximate solution to an
> MDP problem as the dimension (i.e. the number of state and control variables) increases.**
> Although one typically thinks of the curse of dimensionality as arising from the discretization
> of continuous MDPs, **it also occurs in discrete MDPs that have many state and control
> variables.**

**Формальное определение, с. 490:**

> we say that a discrete MDP problem is subject to a curse of dimensionality if
> comp(d) = Ω(2^d) <...> Similarly a continuous MDP problem is subject to the curse of
> dimensionality if comp(ε, d) = Ω(1/ε^d). In the computer science literature a problem which is
> subject to the curse of dimensionality is said to be **intractable**.

**Сноска 10, с. 490 — точно про нашу ситуацию:**

> There is a curse of dimensionality if we index the size of the MDP problem by (d_s, d_a)
> where d_s is the number of state variables and d_a is the number of control variables, since
> in that case the total size of the MDP problem is indexed by (|S|^{d_s}, |A|^{d_a}) which
> increases exponentially fast in d_s and d_a.

**Рабочая оценка стоимости обратной индукции, с. 490, дословно:**

> The upper bound on the complexity of solving a discrete finite horizon MDP problem with
> |S| states and |A| decisions is **c·T·|A|·|S|²** where c is the time cost per arithmetic
> operation.

**Нижняя граница дискретизации (Chow & Tsitsiklis 1989/1991), с. 491, дословно:**

> In order to guarantee that any deterministic discretization procedure yields this accuracy
> requires a minimum of **|A| = Ω(1/((1−β)²ε)^{d_a})** discretized decisions and
> **|S| = Ω(1/((1−β)²ε)^{d_s})** discretized states. Since backward induction on the resulting
> discrete MDP problem requires O(T|A||S|²) operations, it follows that complexity bound for
> solution of continuous MDPs is given by the expression in equation (1.1).

То есть суммарно `comp ~ T · (1/((1−β)²ε))^{2·d_s + d_a}`. Показатель — **2·d_s + d_a**.
🔴 В формуле (1.1) OCR PDF смазал степень; показатель `2d_s + d_a` восстановлен **выводом
из процитированных дословно кусков** (|S|² даёт 2·d_s, |A| даёт d_a), а не взят из смазанной
строки. Помечаю как реконструкцию, не как цитату.

#### Наша задача: сколько получается состояний

**Постановка FINPILOT в терминах MDP.** Переменные состояния на месяц t:
- остаток по каждому из N долгов — N непрерывных переменных (ставка каждого долга — **параметр**,
  а не состояние: она не меняется во времени, поэтому в d_s не входит, но входит в размер
  задачи как индивидуальная калибровка);
- накопленный резерв — 1;
- накопления по каждой из G целей — G;
- состояние дохода (перманентный доход / кэш-он-хэнд) — 1.

`d_s = N + G + 2`. Управление — вектор долей свободного потока, `d_a = N + G + 1`.

**Арифметика (моя, не из источника; сетка m точек на непрерывное измерение, G = 2 цели,
горизонт T = 12 мес — наш горизонт):**

| N долгов | d_s | m = 11 (шаг 10 %) | m = 21 (шаг 5 %) | m = 51 (шаг 2 %) |
|---|---|---|---|---|
| 1 | 5 | 1,61·10⁵ | 4,08·10⁶ | 3,45·10⁸ |
| 2 | 6 | 1,77·10⁶ | 8,58·10⁷ | 1,76·10¹⁰ |
| 3 | 7 | 1,95·10⁷ | 1,80·10⁹ | 8,97·10¹¹ |
| 4 | 8 | 2,14·10⁸ | 3,78·10¹⁰ | 4,58·10¹³ |
| 5 | 9 | 2,36·10⁹ | 7,94·10¹¹ | 2,33·10¹⁵ |

🔴 **При реалистичных N = 2–5 долгов число состояний — от 1,8 млн до 2,4 млрд даже на самой
грубой сетке (11 точек, шаг 10 %).** Это только |S|; счёт — это |S| × |A| × T × (узлы квадратуры).

**Стоимость обратной индукции.** Число действий |A| — число композиций 10 единиц по (N+3)
корзинам (шаг 10 %, как у нас): N = 2 → 1001, N = 3 → 3003, N = 5 → 19 448.

*(a) Верхняя граница Rust `T·|A|·|S|²` (плотные переходы):*

| N | \|S\| (m=11) | \|A\| | T·\|A\|·\|S\|² |
|---|---|---|---|
| 2 | 1,77·10⁶ | 1 001 | **3,77·10¹⁶** |
| 3 | 1,95·10⁷ | 3 003 | **1,37·10¹⁹** |
| 5 | 2,36·10⁹ | 19 448 | **1,30·10²⁴** |

*(b) Реалистичная разреженная оценка `T·|S|·|A|·K`, где K = 7 узлов квадратуры по шоку дохода
(переход детерминирован при заданном шоке — это наш случай):*

| N | операций | при 10⁸ оп/с | при 10⁹ оп/с (C/векторизация) |
|---|---|---|---|
| 2 | 1,49·10¹¹ | 25 мин | 2,5 мин |
| 3 | 4,92·10¹² | **13,7 ч** | 1,4 ч |
| 5 | 3,85·10¹⁵ | 10 700 ч (446 суток) | 1 070 ч (45 суток) |

**Наш перебор для сравнения:** 12 мес × 66 альтернатив × 1000 траекторий Монте-Карло
≈ **7,9·10⁵ операций-эквивалентов** — то есть на **6–10 порядков** дешевле DP даже в самой
щадящей разреженной оценке. Это и есть числовой ответ на вопрос защиты.

🔴 **Честная оговорка против самих себя.** Разрыв в 6–10 порядков — это сравнение **разных
объектов**: DP считает политику для ВСЕХ состояний сразу (один раз, потом любой пользователь
читает готовую таблицу), а наш перебор считает решение для ОДНОГО текущего состояния.
Если бы состояние было низкоразмерным и параметры общими для всех пользователей, DP можно
было бы посчитать офлайн один раз. Почему у нас так не выйдет — §2 (у каждого пользователя
свой набор долгов со своими ставками и сроками, то есть своя модель мира, а не своя точка
в общем пространстве состояний).

---

### 1.4 Аппроксимативное DP (ADP)

**Powell, W. B., «Approximate Dynamic Programming: Solving the Curses of Dimensionality»,
Wiley, 1-е изд. 2007, 2-е изд. 2011.** Ключевая рамка: **три проклятия размерности** —
пространство состояний, пространство исходов (случайности), пространство действий.
🔴 **Книга — пейволл Wiley; полный текст не добыт.** Слайд-тьюториал
`castle.princeton.edu/Presentations/Powell_ADP_tutorialOctober2008.pdf` дал **404**
(115 КБ HTML вместо PDF). Формулировку «three curses of dimensionality: the state space,
the outcome space and the action space» беру из аннотаций издателя и вторичных источников —
**как контекст, а не как проверенную цитату по странице**.

**Rust (1997) — что реально доказано про обход проклятия.** Рандомизированный алгоритм
ломает проклятие размерности **только для подкласса** — discrete decision processes (DDP).
Ограничение существенно: требуется, чтобы почти все переменные состояния вели себя как
i.i.d. равномерные. Остатки долгов у нас, наоборот, **детерминированно убывают** по
графику — прямая противоположность требуемой структуре, так что этот результат к нам
не применяется.

**Что из ADP применимо у нас реально:** не аппроксимация функции ценности (нужны обучающие
данные, которых нет — тема 37), а **policy-search в узком параметрическом классе**: задать
семейство простых правил (напр. «доля x на резерв до достижения k месячных расходов, остаток
по Avalanche»), и перебрать параметры x, k симуляцией. Это ровно то, что мы уже делаем, только
названное по-другому. См. §4 «третий путь».

---

## Участок 2. DP против перебора — по пунктам

### 2.0 🔴 Главная находка участка: точный оптимум задачи о долгах — NP-трудный

**Источник (добыт целиком через `curl` + очистка HTML, 37 109 знаков):**
Yasmín A. Ríos-Solís, Gabriel A. Caballero-Robledo, M. Sánchez-Espinoza (?),
**«Repayment policy for multiple loans», PLoS ONE, 2017**, PMCID: PMC5400254, PMID: 28430786.
URL: `https://pmc.ncbi.nlm.nih.gov/articles/PMC5400254/` (HTTP 200, 175 832 байта).
Open access (CC-BY), получено 2016-12-01 / принято 2017-04-01.

**Постановка совпадает с нашей почти дословно (аннотация):**

> The Repayment Policy for Multiple Loans is about a given set of loans and a monthly incoming
> cash flow: **what is the best way to allocate the monthly income to repay such loans?**

**Результат о сложности (раздел Materials and methods, дословно):**

> we close the almost 20 year old open question about the complexity of the RPML which, we
> find, **belongs to the NP-hard complexity class** <...> the RPML problem inherits its
> complexity from the **multiple knapsack problem**. <...> While the RPML problem is an NP-hard
> problem that may take an exponential time to be solved, this simplified version belongs to
> the polynomial complexity class.

**Результат об эвристиках (аннотация + Table 2), дословно:**

> We prove that the most employed repayment strategies, such as the highest interest debt and
> the debt snowball methods, **are not optimal**. Experimental results on simulated cases based
> on real data show that our methodology obtains **on average more than 4% of savings** <...>
> In certain cases, the debtor can save up to **40%**.

**Table 2 полностью (относительная экономия точного решения против эвристик, %):**

| Кол-во займов L | Горизонт T, мес | Gap | Время, с | против HInterest (Avalanche) | против Snowball | против Average |
|---|---|---|---|---|---|---|
| 4 | 120 | 0,00017 | 27 | **5,84** | 7,19 | 6,64 |
| 8 | 120 | 0,01129 | 581 | **4,62** | 5,99 | 5,27 |
| 8 | 240 | 0,02324 | 619,6 | **4,56** | 7,42 | 5,58 |
| 12 | 300 | 0,20677 | 1057,7 | **3,43** | 5,67 | 4,06 |
| **Среднее** | | **0,06** | **571,37** | **4,61** | **6,57** | **5,39** |

Решено MILP в Gurobi 6.04 на Mac Pro 3.5 ГГц 6-Core Xeon E5 / 32 ГБ, лимит времени 30 минут.
550 инстансов.

🔴 **Это результат ПРОТИВ нашего Avalanche-фильтра, и его надо назвать прямо: наш
Avalanche-фильтр в среднем на ~4,6 % (по сумме выплат) хуже точного оптимума, а в худшем
найденном случае — на 40 %.**

**НО — механизм этих 4,6 % разобран в статье, и он у нас отключён по построению.** Разбор
инстанса с экономией 40 % (Fig 2, дословно):

> in the first months, the RPML model **proposes to save money even if the debtor generates
> default penalties** that might be even greater than the amount of the installments (as in
> month 4). However, these savings will palliate the lack of cash that the debtor will face
> during months 3, 4 and 5 <...> **The cyclic behavior of the savings proposed by the RPML plan
> is the powerful arm that allows reducing the total amount of repayments by diminishing the
> default penalties.**

То есть выигрыш оптимума над Avalanche берётся из **умышленной просрочки и последующего
покрытия штрафов**: оптимум играет на кассовых разрывах. В FINPILOT сценарий, где заёмщик
не покрывает обязательный платёж, **запрещён жёсткими инвариантами** `R_t ≥ 0` и `ПДН ≤ 0,40`.
Оптимизация, у которой отобрана возможность допускать просрочку, теряет главный источник
своего преимущества. Плюс прямое подтверждение из той же статьи:

> the benefit of using the RPML methodology with instances with more credit-card debts is
> reduced with respect to the other alternatives. Indeed, **the benefit is around 0.5% with
> respect to the highest interest rule.**

**Отсюда рабочая оценка нашей потери:** для краткосрочных долгов без сценария просрочки
разрыв Avalanche против оптимума **порядка 0,5 %, а не 4,6 %**. 🔴 Это **интерполяция с моей
стороны** (статья даёт 0,5 % для инстансов с преобладанием кредитных карт, а не для инстансов
с запретом просрочки) — на защите это надо подавать как порядок величины, а не как замер.

### 2.1 Чувствительность решения к ошибке в параметрах

**Источник (добыт целиком, `pdftotext`, 2343 строки):** David A. Love, *Optimal Rules of Thumb
for Consumption and Portfolio Choice*, 21.11.2011, Williams College.
URL: `https://web.williams.edu/Economics/seminars/loveOptimalRules.pdf` (HTTP 200, 505 379 байт).
Авторская/семинарская копия — пейволла нет.

**Определение «оптимальной эвристики» — это ровно наша конструкция (с. 8, формулы (3)–(4)):**

> Define a rule of thumb to be a policy h̃_t(θ) in which the decision rules are constrained to
> take a specific functional form, d_t = f(s_t; θ), where θ is a vector of parameters.
> <...> Define an **optimal rule of thumb** to be a parameterization θ* that maximizes the value
> of adopting a particular rule of thumb: **θ* = arg max_θ v_t(h̃_t(θ), s_t)**   (4)

🔴 **Наши 66 альтернатив — это в точности сетка по θ в формуле (4) Love.** Перебор 66 сплитов
с оценкой каждого через SES + Монте-Карло = численный `arg max_θ` в ограниченном классе правил.
У метода есть имя в литературе (optimal rule of thumb / policy search в ограниченном классе),
и он опубликован как самостоятельный подход, а не как упрощение по незнанию. Это опорный
аргумент §4.

**Величина потери против DP (аннотация, с. 1, дословно):**

> In the case of portfolio choice, I find that **optimal linear age rules lead to modest welfare
> losses relative to the dynamic programming solution** and that a linear rule based on the ratio
> of financial wealth to total lifetime resources performs even better. **Consumption rules
> generate larger welfare losses—from 1–8% of annual consumption**—but an effective rule is to
> consume 70–80% of annuitized lifetime wealth.

Детализация (с. 3–4):
- оптимальное линейное возрастное правило по портфелю: **потери < 0,5 % годового потребления**;
- с обновлением правила в 40 и 65 лет: **< 0,06 % годового потребления, около $32 в год**;
- правило потребления «доля дохода + фиксированная ставка изъятия»: **4–8 % в год**;
- правило «доля аннуитизированного богатства»: **1–4 %**, местами ниже 1 % при обновлении.

🔴 **И ключевое различение, работающее на нас (с. 6):**

> the differences in the welfare losses associated with an arbitrary rule of thumb advocated in
> popular finance and an optimized one often turn out to be substantial.

То есть **разрыв между произвольной эвристикой и оптимизированной эвристикой больше, чем между
оптимизированной эвристикой и DP.** Мы находимся на «оптимизированной» стороне: правило
«Avalanche + резерв + цели» не взято из популярной литературы, а параметризовано и оптимизировано
по сетке 66 точек.

🔴 **А это — против нас, и это надо озвучить на защите первым, не дожидаясь вопроса (с. 4):**

> the welfare losses rise by as much as **2% of annual consumption** when the model incorporates
> uncertainty in risk aversion or the discount factor. Thus, while parameter uncertainty does not
> lead to large changes in the optimal rules themselves, **it can make the rules less attractive
> relative to the dynamic programming solution.**

🔴 **Это ПРЯМОЕ ОПРОВЕРЖЕНИЕ ожидаемого нами эффекта.** Мы рассчитывали на симметрию с
DeMiguel (тема 39): «входы оценены плохо → выигрыш оптимизации съедается». Love проверил ровно
эту гипотезу для DP-задачи потребления и получил **обратный знак**: при неопределённости
параметров предпочтений эвристика проигрывает DP **сильнее**, а не слабее. Аналог «1/N бьёт
Марковица» в консумпционно-сберегательной задаче **не воспроизводится в этой работе**.

**Почему это не убивает нашу позицию (но и не спасает её целиком).** У Love неопределённость —
в **параметрах предпочтений** (ρ, β), а не в **уравнении движения** (будущий поток дохода,
горизонт, вероятность шока). DeMiguel-эффект в портфельной задаче возникает из ошибки в
**ожидаемых доходностях**, то есть в модели мира, а не в предпочтениях. Наши слабые входы
(темы 32–34) — это модель мира, а не предпочтения. 🔴 **Работа, которая мерила бы потерю DP
именно от ошибки в модели дохода для потребительской задачи, мною НЕ найдена** — см. «что
не добыто». Это дыра в аргументации, и на защите честнее сказать «прямого замера нет»,
чем притянуть Love в свою сторону.

### 2.2 Робастное DP / robust MDP — какой ценой

**Источник (добыт целиком, `pdftotext`, 3634 строки):** Wolfram Wiesemann, Daniel Kuhn,
Berç Rustem, *Robust Markov Decision Processes*.
URL: `https://optimization-online.org/wp-content/uploads/2010/05/2610.pdf` (HTTP 200, 751 303 байта).

Идея: транзитная матрица неизвестна точно, известно лишь **множество неопределённости**
(ambiguity set) `P`; политика максимизирует худший случай на `P`.

**Результат о сложности (с. 3, п. 2 вклада, дословно):**

> It is stated in [18] that the robust policy evaluation and improvement problems "seem to be
> hard to solve" for non-rectangular ambiguity sets. **We prove that these problems cannot be
> approximated to any constant factor in polynomial time unless P = NP.**

**И — прямо про наш случай (с. 7, дословно):**

> In Section 5, we will construct ambiguity sets **from observation histories**. The resulting
> ambiguity sets **turn out to be non-rectangular** <...> Unfortunately, the robust policy
> evaluation and improvement problems over non-rectangular ambiguity sets are **intractable**
> <...> and we will only be able to obtain approximate solutions via semidefinite programming.
> This is in stark contrast to the robust policy evaluation and improvement problems over
> s-rectangular and (s,a)-rectangular ambiguity sets, which can be solved efficiently through a
> sequence of second-order cone programs.

**Что это значит для FINPILOT.** «Робастное DP» как ответ на «наши входы плохо оценены» —
не бесплатный: (1) множества неопределённости, построенные **по наблюдённым историям** (а другого
источника у нас нет), выходят **не-прямоугольными**, и точная робастная задача становится
NP-трудной без константного приближения; (2) прямоугольные множества, где всё считается
полиномиально, **консервативны** — статья прямо пишет, что «rectangularization unduly increase
the level of conservatism» и создаёт нежелательные эффекты. То есть выбор: либо неразрешимо,
либо чрезмерно осторожный совет.

🔴 **Плюс к этому — у нас нет наблюдённых историй вообще (тема 37, нет логов).** Строить
ambiguity set не из чего. Робастное DP у нас не отвергнуто по вкусу — оно **не имеет входа**.

### 2.3 Сводная таблица по шести критериям

См. итоговый раздел «Таблица DP против перебора».

---

## Участок 3. Что применяют в продуктах

### 3.1 Betterment — первичный документ

**Источник:** Betterment, «Goal Projection and Advice Disclosure»,
`https://www.betterment.com/legal/goal-projection` (получено `WebFetch`, HTTP 200).
Это официальное юридическое раскрытие методики, а не маркетинг.

Что там реально написано (цитаты, добытые из документа):
- «The recommended monthly contributions estimate is based on a **50% likelihood** of the
  portfolio value reaching the goal target at the end of the investment term»;
- «Betterment considers volatility in its returns estimates and displays a client's **likelihood
  of success** in reaching their investing goals depending on market performance»;
- статус «On Track» — «the total projected portfolio value exceeds the goal target assuming
  average market performance. This is equivalent to a likelihood of 50% and above»;
- «The lighter, shaded region indicates the range within which there is **80% likelihood** of
  obtaining the projected portfolio value».

🔴 **Чего в документе НЕТ:** ни динамического программирования, ни оптимального управления,
ни явного слова «оптимизация». Метод — **проекция распределения + процентильные полосы +
подбор взноса под 50-й процентиль**. Это форвардная симуляция и обратное решение по одному
скаляру (размер взноса), а не решение задачи оптимального управления.

**Как это ложится на нас:** Betterment решает более простую задачу (один портфель, одна цель,
одна ручка — взнос) и всё равно останавливается на симуляции + процентиль. У нас задача сложнее
(долги + резерв + цели), и симуляционный подход (SES + Монте-Карло по 66 сплитам) — это тот же
класс метода, применённый к более широкому пространству действий.

### 3.2 Vanguard — что делают их же исследователи

**Источник (добыт целиком, `pdftotext`, 2603 строки):** Victor Duarte (Illinois), Julia Fonseca
(Illinois), **Aaron Goodman (Vanguard, Investment Strategy Group)**, Jonathan A. Parker (MIT & NBER),
«Simple Allocation Rules and Optimal Portfolio Choice Over the Lifecycle», NBER WP 29559,
версия 16.05.2024. URL: `https://mitsloan.mit.edu/shared/ods/documents?PublicationDocumentID=10586`
(HTTP 200, 472 455 байт).

**Что они сделали (аннотация, с. 1, дословно):**

> We study the accuracy of such simple quantitative guidance in an area where it has been widely
> adopted — lifecycle portfolio choice among stocks, bonds, and liquid accounts — by developing a
> **machine-learning algorithm** to solve for optimal portfolio choice in a calibrated lifecycle
> model <...> the average fully-optimal portfolio at each age **conforms well to current simple
> age-dependent prescriptive rules** until shortly before retirement, **validating existing
> analyses**. We further show that the **consumption-equivalent losses from conditioning
> portfolio shares on age alone are substantial, around 2 to 3 percent of consumption.**

**Почему НЕ DP (с. 4, дословно):**

> We are able to evaluate the simple rule in a model with **more than 20 state variables and
> shocks** by using new tools from the field of **deep reinforcement learning** <...> The main
> advantage of our method over **traditional numerical dynamic programming (NDP)** is the
> massive increase in speed that makes it tractable to solve **previously infeasible problems**.
> The traditional NDP approach would first characterize the solution <...> then construct grids
> on which choices can be characterized by matrices <...> In contrast, our method maximizes
> expected utility using simulated sample paths **which avoids computationally-slow numerical
> integration**.

и (с. 5):

> Our method is far easier to use and program (and so less prone to error) than traditional
> numerical dynamic programming methods. For example, **there is no need to specify the density
> and scale of grids** over which policy functions can then be defined as matrices.

и (с. 29):

> these three solution strategies <...> make it feasible to solve our lifecycle model – and
> presumably similar models – that were **previously computationally infeasible to solve**.

🔴 **Три вывода, каждый прямо про наш вопрос:**
1. **Численное DP на 20+ переменных состояния объявлено «previously computationally infeasible»
   исследователями MIT/NBER с соавтором из Vanguard в 2024 году.** Это ровно наш §1.3 — только
   не моя арифметика, а их формулировка. У нас при N=5 долгах d_s = 9 плюс параметры ставок —
   тот же порядок задачи.
2. Их замена DP — **не аналитика, а симуляция по траекториям с policy gradient**. Наш подход
   (перебор 66 политик × Монте-Карло траектории) — тот же принцип «оценивать политику
   симуляцией, а не сеткой состояний», только с перебором вместо градиента, потому что
   пространство политик у нас 66 точек, а не миллионы весов сети.
3. **Простые правила проигрывают полному оптимуму 2–3 % consumption-equivalent** — и это
   в портфельной задаче с 20+ состояниями. Это верхняя планка порядка нашей потери.

### 3.3 Общая картина по индустрии

**Источник:** обзор 2025 г., arXiv:2509.09922, «Robo-Advisors Beyond Automation: Principles and
Roadmap for AI-Driven Financial Planning» (добыт целиком, `pdftotext`, 1697 строк, HTTP 200,
656 939 байт).

Что делают платформы (с. ~5, дословно):

> In practice, most platforms follow a broadly similar structure. Clients are first onboarded
> through questionnaires that capture financial goals, investment horizons, and risk tolerance.
> **Portfolios are then constructed using frameworks such as Modern Portfolio Theory (MPT)
> (Black and Litterman, 1990, 1992; Elton and Gruber, 1997; Markowitz, 1952) or its extensions.**
> The system subsequently monitors market conditions, rebalances portfolios, and applies features
> such as tax-loss harvesting or dividend reinvestment.

Их же «уровень 1 зрелости» (с. 23):

> The first maturity level consists of **deterministic, rule-based financial tools**—essentially
> digital calculators that replicate spreadsheet functions <...> These systems process
> user-provided inputs (loan amount, interest rate, time horizon) through fixed formulas.

🔴 **Ответ на вопрос «почему никто не применяет DP в потребительских продуктах»:** обзор
описывает индустрию как «MPT/однопериодная оптимизация + мониторинг + правила», а нижний
уровень — как детерминированные калькуляторы. **DP в перечне методов индустрии не появляется
вовсе.** Причины, собираемые из трёх источников выше:
- вычислительная неподъёмность при реалистичном числе состояний (§1.3, §3.2);
- необходимость задать модель мира (доходы, шоки, предпочтения) в виде, которого у продукта нет;
- ступенчатая, необъяснимая политика на выходе (Deaton, §1.2);
- регуляторное требование объяснимой рекомендации (§4.2).

### 3.4 RL как замена DP — применим ли у нас

Тема-хвост 13 дала MetaRL с **97,8 % от оптимума DP** (Das et al., arXiv:2605.02300), §3.2 даёт
deep RL с 20+ состояниями. Оба работают.

🔴 **Но оба обучаются на СИМУЛЯЦИЯХ из откалиброванной модели, а не на логах.** Duarte et al.:
«maximizes expected utility using **simulated sample paths**». То есть отсутствие логов (тема 37)
**не является препятствием для RL** — препятствием было бы отсутствие модели мира. Модель мира
у нас есть (SES + Монте-Карло по потоку).

**Настоящее препятствие другое, и оно решающее:** RL-политика — это веса нейросети. Она не
объясняется пользователю и не проходит требование обоснованной рекомендации (§4.2). Кроме того,
её нужно обучать **под каждый набор долгов пользователя** (у каждого свои ставки/сроки — своя
модель мира), либо подавать конфигурацию долгов на вход сети, что снова упирается в переменную
размерность входа. Duarte et al. решали ОДНУ откалиброванную модель месяцами GPU-времени —
у нас же на каждого пользователя своя.

🔴 **Вывод по RL: технически применим, продуктово — нет.** И причина не «нет логов», как мы
думали, а «нет объяснимости + модель мира индивидуальна». Это поправка к теме 37.

---

## Участок 4. Ответ на защите

### 4.1 Что мы теряем количественно, отказавшись от DP

Собрано из четырёх независимо добытых работ. Все числа — из первоисточников, прочитанных целиком.

| Что сравнивается | Потеря эвристики против оптимума | Источник |
|---|---|---|
| Avalanche против точного оптимума погашения (MILP), средн. по 550 инстансам | **4,61 %** суммы выплат | Ríos-Solís et al., PLoS ONE 2017, Table 2 |
| То же, худший найденный инстанс | **40 %** | там же, Fig 2 |
| То же, инстансы с преобладанием краткосрочных долгов (кредитки) | **≈ 0,5 %** | там же, Table 4 |
| Snowball против точного оптимума | 6,57 % | там же, Table 2 |
| Оптимизированное линейное правило по портфелю против DP | **< 0,5 %** годового потребления | Love 2011, с. 3 |
| То же, с обновлением правила | **< 0,06 %** (≈ $32/год) | Love 2011, с. 3 |
| Правила потребления против DP | 1–8 % годового потребления | Love 2011, аннотация |
| Простые возрастные правила (TDF) против полного оптимума, 20+ состояний | **2–3 %** consumption-equivalent | Duarte, Fonseca, Goodman, Parker 2024, аннотация |
| MetaRL против DP-эталона (GBWM) | достигает **97,8 %** оптимума (потеря 2,2 %) | Das et al., arXiv:2605.02300 (тема 13, хвосты) |

🔴 **Рабочая оценка потери FINPILOT: единицы процентов — порядка 0,5–5 % в терминах суммы
выплат/эквивалента потребления, скорее ближе к нижней границе.** Обоснование нижней границы:
(а) наш горизонт 12 месяцев, а не жизненный цикл — большая часть выигрыша DP набирается на
длинном горизонте; (б) инварианты `R_t ≥ 0` и `ПДН ≤ 0,40` запрещают просрочку, а именно на
просрочке точный оптимум RPML отыгрывает свои 4,6 % (§2.0); (в) мы не берём произвольное
правило, а оптимизируем параметризованное — а разрыв «произвольная эвристика vs
оптимизированная» больше, чем «оптимизированная vs DP» (Love 2011, с. 6).

### 4.2 Что мы выигрываем

**1. Вычислительная осуществимость — 6–10 порядков (§1.3).** Перебор: ~7,9·10⁵
операций-эквивалентов. DP при N=3 долгах на грубейшей сетке (шаг 10 %): 4,92·10¹² операций
даже в разреженной оценке — 13,7 ч на 10⁸ оп/с. При N=5: 3,85·10¹⁵ — 45 суток на 10⁹ оп/с.
🔴 И это не «мы плохо считаем»: DP на 20+ состояниях названо «previously computationally
infeasible» в NBER WP 29559 (2024).

**2. Объяснимость.** Ответ перебора — «60 % на долги, 30 % в резерв, 10 % на цель, потому что
такой сплит дал лучшую свёртку по вашему профилю; вот 65 других вариантов и их оценки».
Ответ DP — значение функции ценности в узле сетки, восстановленное интерполяцией. Deaton 1991
(с. 1230) прямо: «the use of grids generates a policy function at the final stage that is a
**step function**, which has to be "smoothed"». Объяснить ступеньку интерполированной
функции ценности пользователю нельзя.

**3. Регуляторное соответствие.** Методические рекомендации Банка России от 27.12.2024 № 22-МР
«По предоставлению потребителям финансовых продуктов (дополнительных услуг) в дистанционных
каналах» — заявленная цель включает «прозрачный и осознанный выбор потребителем финансовых
продуктов в дистанционных каналах», внедрение рекомендовано не позднее IV квартала 2025 г.
🔴 **Первичный текст 22-МР НЕ ДОБЫТ** (garant.ru и pifconsulting.ru вернули HTTP 200, но без
текста документа — см. «что не добыто»). Формулировка цели взята из аннотаций правовых баз,
номера пунктов не проверены. **На защите ссылаться на 22-МР только на уровне «цель документа»,
без номеров пунктов, пока текст не добыт с cbr.ru.**

**4. Устойчивость пересчёта.** Изменились входные данные (появился долг, изменился доход) —
перебор пересчитывается за миллисекунды на актуальном состоянии. DP требует пересчёта всей
таблицы политики, потому что **у каждого пользователя своя модель мира**: свой набор долгов
со своими ставками, сроками и минимальными платежами. Это не разные точки в общем пространстве
состояний — это разные MDP. Офлайн-предподсчёт одной таблицы на всех невозможен, а именно на
нём держится вся экономическая привлекательность DP.

**5. Метод имеет имя в литературе.** Love (2011), формула (4): `θ* = arg max_θ v_t(h̃_t(θ), s_t)` —
«optimal rule of thumb». Наши 66 альтернатив — сетка по θ. Это опубликованный подход, а не
самодеятельность.

### 4.3 🔴 Третий путь — что реально доступно

**Вариант A. DP на грубой сетке — НЕ РАБОТАЕТ, и это считано.** Наша сетка уже грубейшая
из возможных (шаг 10 %, 11 точек на измерение). При ней N=3 → 1,95·10⁷ состояний, N=5 →
2,36·10⁹. Грубее — только шаг 20 % (6 точек), что даёт при N=3 ≈ 2,8·10⁵ состояний, но
рекомендация «40 % или 60 %, промежуточного нет» хуже нашей же текущей точности. Тупик.

**Вариант B. 🟢 DP/точная оптимизация ДЛЯ ПОДЗАДАЧИ (только долги) — РЕАЛЬНЫЙ, и он уже
формализован за нас.** Ríos-Solís et al. (2017) дали готовую MILP-формулировку RPML, решаемую
Gurobi за 27–1058 с при 4–12 займах с гэпом 0,06 в среднем. Плюсы: (1) при N ≤ 4 займах —
27 секунд и гэп 0,00017, то есть практически точный оптимум; (2) это **линейное
программирование**, а не DP — двойственные переменные дают объяснение «почему именно так»;
(3) даёт нам **измеримую верхнюю границу** качества Avalanche на синтетике. Минус: время
27–1058 с несовместимо с интерактивным ответом, но совместимо с оффлайн-валидацией.
🔴 **Это самый ценный практический результат темы.**

**Вариант C. Эвристика с гарантией близости (approximation ratio) — НЕ НАЙДЕНА.** Поскольку
RPML NP-труден по сведению к multiple knapsack, ожидать FPTAS в общем случае нельзя; работ
с доказанным approximation ratio для Avalanche/Snowball мною **не найдено**. Заявлять «наш
перебор в X раз от оптимума» без такой работы нельзя — только эмпирический замер (вариант B).

**Вариант D. 🟢 Расширение сетки θ вместо перехода к DP.** Love (2011, §3.1 «Updating the rule»)
показывает, что **обновление параметров правила во времени** снижает потерю с 0,5 % до 0,06 %,
то есть на порядок — дешевле, чем менять класс метода. У нас аналог — пересчитывать сплит
каждый месяц по фактическому состоянию (мы это уже делаем) и, возможно, разрешить разные
сплиты для разных месяцев горизонта, а не один на все 12.

**Вариант E. Перебор с более мелким шагом.** 66 альтернатив = композиции 10 по 3 корзинам
(шаг 10 %). Шаг 5 % даёт 231 альтернативу, шаг 2 % — 1326. При стоимости 12 × 66 × 1000 ≈
7,9·10⁵ операций рост в 20 раз всё ещё оставляет нас на 5–8 порядков ниже DP. То есть **если
кто-то на защите скажет «66 — это мало», ответ не «зато дёшево», а «мы можем взять 1326 и
остаться в тысячу раз дешевле DP; вопрос в том, различима ли разница при нашей точности
входов»** — и вот тут работает аргумент темы 39 про less-is-more.

---

## Итоги

### 1. 🔴 Прямой ответ на вопрос защиты

Динамическое программирование даёт оптимум для *заданной* модели мира, но нашу задачу оно
не решает вычислительно: состояние FINPILOT — это остаток по каждому из N долгов, резерв,
накопления по целям и состояние дохода, то есть d_s = N + G + 2; при N = 3 долгах и 2 целях
на грубейшей сетке шагом 10 % это 1,95·10⁷ состояний, а при N = 5 — 2,36·10⁹, и обратная
индукция стоит 4,92·10¹² и 3,85·10¹⁵ операций соответственно (13,7 часа и 446 суток при
10⁸ оп/с) против ≈ 7,9·10⁵ операций у нашего перебора — разрыв 6–10 порядков; это не наша
оценка снизу, а прямая арифметика по границе Rust (Econometrica 1997, с. 490: «The upper
bound on the complexity of solving a discrete finite horizon MDP problem with |S| states and
|A| decisions is c·T·|A|·|S|²»), и авторы NBER WP 29559 (2024, среди них исследователь
Vanguard) называют численное DP на 20+ переменных состояния «previously computationally
infeasible». Цена отказа при этом измерена и мала: оптимизированные правила теряют против
DP менее 0,5 % годового потребления, а с обновлением параметров — менее 0,06 % (Love 2011,
с. 3); простые возрастные правила против полного оптимума — 2–3 % (Duarte et al. 2024);
точный MILP-оптимум погашения нескольких займов выигрывает у Avalanche в среднем 4,61 %,
но лишь 0,5 % на краткосрочных долгах, и выигрыш этот берётся из умышленной просрочки
с последующим покрытием штрафов (Ríos-Solís et al., PLoS ONE 2017, Table 2 и Fig 2) —
сценария, который у нас запрещён инвариантами R_t ≥ 0 и ПДН ≤ 0,40. Сама задача о погашении
нескольких займов доказанно NP-трудна (сведение к multiple knapsack, там же), поэтому
«просто посчитать оптимум» невозможно не только у нас, но и в принципе. Наш перебор 66
альтернатив — это не упрощение, а численный `arg max_θ v_t(h̃_t(θ), s_t)` в ограниченном
классе правил: у метода есть имя и формула в литературе (Love 2011, формула (4), с. 8,
«optimal rule of thumb»), и по тому же источнику разрыв между *произвольной* эвристикой
и *оптимизированной* больше, чем между оптимизированной и DP. 🔴 Одно возражение мы обязаны
озвучить сами: Love (2011, с. 4) нашёл, что при неопределённости параметров предпочтений
потери эвристики против DP **растут** на величину до 2 % годового потребления, то есть
ожидаемая нами симметрия с DeMiguel (тема 39) в этой работе **не подтверждается**, а
исследование, замеряющее потерю DP именно от ошибки в модели дохода, нами не найдено.

### 2. Таблица DP против перебора

| Критерий | Точное DP (value/policy iteration на сетке) | Наш перебор 66 альтернатив + Монте-Карло |
|---|---|---|
| **Сложность** | `c·T·\|A\|·\|S\|²`; \|S\| = m^(N+G+2). При N=3, m=11: 1,95·10⁷ состояний, 4,92·10¹² оп (разреж.), 13,7 ч. При N=5: 3,85·10¹⁵ оп, 446 сут. Rust 1997, с. 490 | 12 × 66 × 1000 ≈ 7,9·10⁵ оп-эквивалентов, миллисекунды. Расширяемо до 1326 альтернатив (шаг 2 %) с ростом ×20 |
| **Оптимальность** | Оптимум **для заданной модели мира**; на практике всё равно дискретизован сеткой. Точный оптимум подзадачи долгов NP-труден (RPML, PLoS ONE 2017) | Оптимум **в классе правил**. Замеренная потеря: <0,5 % (Love), 2–3 % (Duarte et al.), 4,61 %/0,5 % против MILP (Ríos-Solís) |
| **Интерпретируемость** | Низкая. Политика — ступенчатая функция на сетке, требующая сглаживания (Deaton 1991, с. 1230) | Высокая. 66 явных сплитов с числовой оценкой каждого; решение = «этот лучше вот этих 65» |
| **Устойчивость к ошибке входов** | 🔴 Спорно. Love 2011, с. 4: при неопределённости параметров предпочтений DP выигрывает **больше**. Робастное DP: NP-трудно на неprямоугольных множествах, консервативно на прямоугольных (Wiesemann et al.) | Меньше «ручек», чувствительных к оценке; условия less-is-more (тема 39) выполнены, но прямого замера в нашей задаче нет |
| **Объяснимость пользователю** | Практически невозможна: значение функции ценности в узле интерполяции | Прямая: сплит + сравнительная таблица альтернатив. Соответствует духу 22-МР (текст не добыт) |
| **Пересчёт при изменении данных** | Полный пересчёт таблицы политики. 🔴 Офлайн-предподсчёт «раз на всех» невозможен: у каждого пользователя свой набор долгов = свой MDP, а не своя точка в общем состоянии | Полный пересчёт = один прогон перебора, миллисекунды |

### 3. Что стоит попробовать — конкретно, на синтетике

1. 🟢 **Измерить наш собственный gap MILP-ом (вариант B §4.3).** Взять формулировку RPML
   (Ríos-Solís et al. 2017: минимизация суммарной выплаченной наличности, ограничения
   Eqs (3)–(6), бинарные Z_jt для просрочек), реализовать на PuLP/Gurobi-free, прогнать
   на 200–500 синтетических профилях с N = 2–5 долгов и нашим горизонтом 12 мес **при
   отключённом сценарии просрочки** (наши инварианты) и сравнить с выдачей Avalanche-фильтра.
   Ожидаемый результат — число вида «наш фильтр в среднем на X % хуже точного оптимума
   при запрете просрочки». 🔴 Это превращает главный аргумент защиты из литературного
   в **собственный замер**. Ожидаемое время: 27 с на инстанс при N ≤ 4 (их замер).
2. **Посчитать честную кривую «шаг сетки → качество».** Прогнать перебор с шагом 20 / 10 / 5 / 2 %
   (16 / 66 / 231 / 1326 альтернатив) на тех же профилях. Если разница между 66 и 1326
   меньше разброса от ошибки входов (темы 32–34) — это прямое эмпирическое подтверждение
   less-is-more темы 39 **на наших данных**, а не по аналогии.
3. **Проверить вариант D (обновление правила).** Сравнить «один сплит на 12 месяцев» против
   «пересчёт сплита каждый месяц по факту». По Love (2011) обновление даёт выигрыш на порядок
   (0,5 % → 0,06 %). Если у нас так же — это дешёвое улучшение без смены класса метода.
4. **DP как эталон для одного долга.** При N = 1, G = 0 состояние двумерно (остаток + резерв),
   |S| при m = 51 ≈ 2,6·10³ — DP считается за секунды. Дать точный оптимум на этой вырожденной
   задаче и измерить, насколько от него отстаёт перебор. Даёт нижнюю границу разрыва
   и защищает от возражения «вы вообще DP не пробовали».

### 4. Что не добыто. Метод поиска

**Не добыто:**
- **Zeldes (1989), QJE 104(2)** — авторской копии не найдено, Oxford Academic пейволл.
  Канал не пробивался (пейволл, а не антибот). Использован как контекстная ссылка без цитаты.
- **Powell, «Approximate Dynamic Programming», Wiley (2007/2011)** — книга за пейволлом.
  Слайд-тьюториал `castle.princeton.edu/Presentations/Powell_ADP_tutorialOctober2008.pdf`
  вернул **HTTP 404** (115 733 байта HTML вместо PDF). Формулировка «three curses of
  dimensionality» взята из аннотации издателя — **не проверенная по странице цитата**.
- **Полный текст 22-МР Банка России** — `garant.ru/products/ipo/prime/doc/411133249/` и
  `pifconsulting.ru/acts/acts_726.html`: обе страницы отдали **HTTP 200, но без текста
  документа** (только карточка и ссылка на cbr.ru). Номера пунктов не проверены.
  🔴 Следующий канал, не испробованный: прямая ссылка на PDF с `cbr.ru`.
- **Работа про чувствительность DP-решения к ошибке в МОДЕЛИ ДОХОДА** (аналог DeMiguel для
  консумпционно-сберегательной задачи) — **не найдена**. Найдена только чувствительность
  к параметрам предпочтений (Love 2011), и там знак эффекта **против нас**. Это реальная
  дыра в аргументации, а не «не искал».
- **Эвристика с доказанным approximation ratio для задачи погашения** — не найдена;
  вероятно, не существует (RPML NP-труден).
- **Формула (1.1) Rust (1997), с. 491** — OCR PDF смазал показатель степени. Показатель
  `2·d_s + d_a` **реконструирован выводом** из процитированных дословно фрагментов
  (|S|² → 2·d_s, |A| → d_a), а не прочитан. Помечено в тексте.
- **Точный состав авторов PLoS ONE 2017** — HTML PMC дал имена частично (Y. Ríos-Solís,
  G. A. Caballero-Robledo, третий соавтор «MSE» по инициалам в разделе вклада).
  Ссылку оформлять по DOI/PMID, а не по моему списку авторов.

**WebSearch работал.** Вызовов WebSearch — **13**, все вернули непустую выдачу, ни одного
отказа и ни одного 429. Отдельно: `WebFetch` — 3 вызова (Betterment — успех; garant и
pifconsulting — 200 без текста). `curl` — 9 загрузок, 6 успешных PDF, 1 успешный HTML,
2 промаха 404 (зеркала llorracc.github.io и castle.princeton.edu). `r.jina.ai` не
понадобился ни разу. `pdftotext -layout` — 7 разборов, все успешные.

**Метод поиска.** Работал один агент, без подагентов (правило §11 CLAUDE.md).
Классификация запроса — **breadth-first** (четыре независимых участка: аппарат DP ·
сравнение · практика индустрии · ответ защиты), но исполнено **последовательно одним
контекстом**, потому что участки 2 и 4 целиком питаются находками участков 1 и 3, и
параллельный веер потребовал бы повторного добывания тех же PDF.

Порядок каналов по каждому источнику: `WebSearch` короткими запросами (3–6 слов) →
проверка, есть ли **авторская/открытая копия** (личные страницы `~deaton` в Принстоне,
`econ2.jhu.edu/people/ccarroll`, `web.williams.edu`, `mitsloan.mit.edu`, `editorialexpress.com`,
`optimization-online.org`, PMC open access) → `curl` с браузерным UA → `pdftotext -layout` →
чтение и цитирование по строкам. 🔴 **Все девять содержательных цитат в этом файле взяты из
файлов, разобранных `pdftotext`-ом целиком, а не из сниппетов поиска.** Ни один пересказ
`WebFetch` не использован как источник числа — единственный `WebFetch`-источник (Betterment)
помечен явно и содержит только текстовые формулировки, не числа из PDF.

🔴 **Приём, сработавший лучше всего:** искать не по названию статьи, а по формулировке
результата («simple heuristic near-optimal lifecycle welfare loss», «optimal debt repayment
NP-hard») — так найдены Love 2011 и Ríos-Solís 2017, две самые ценные работы темы, ни одна
из которых не была известна на входе.

---

## ДОБОР 10.09.2026

**Что добираю (по разделу «Не добыто» и пометкам «реконструкция / интерполяция / из аннотации»):**
1. Love (2011): формула (4), страницы, числа <0,5 %, <0,06 % ($32), 1–8 %, «до 2 %» при
   неопределённости параметров — сверка по PDF построчно.
2. Ríos-Solís et al. (PLoS ONE 2017): полный список авторов, MILP-формулировка (Eqs), Table 2
   (4,61 %), источник 0,5 % (какая таблица, какой контекст), 40 %, утверждение о NP-трудности;
   главное — зависит ли выигрыш оптимума от просрочки (проверка нашего довода «у нас она запрещена»).
3. Rust (1997), формула (1.1): показатель степени — прочитать, а не реконструировать.
4. Powell, ADP — «three curses of dimensionality» по первоисточнику.
5. 22-МР Банка России — первичный текст с cbr.ru.
6. Zeldes (1989) — открытая копия.
7. Das et al. arXiv:2605.02300 — 97,8 % (взято из темы 13, здесь не сверено).
8. Контрпримеры к сильным выводам: (а) DP реально применяется в персональных финансах/продуктах;
   (б) чувствительность DP к ошибке модели дохода; (в) approximation ratio для погашения долгов;
   (г) Avalanche оптимален при отсутствии просрочек (или нет).

### Результаты (дописываются по ходу)

#### Д1. Love (2011) — построчная сверка по PDF
Канал: `curl` → `web.williams.edu/Economics/seminars/loveOptimalRules.pdf`, HTTP 200, 505 379 байт
(совпадает с первым прогоном), `pdftotext -layout`, 2343 строки. Номера страниц сверены
постранично (`pdftotext -f N -l N`); печатный номер = номер страницы PDF − 1 (титул без номера).

| Утверждение в файле | По PDF | Вердикт |
|---|---|---|
| Формула (4) `θ* = arg max_θ v_t(h̃_t(θ), s_t)`, «с. 8» | формула верна дословно; стоит на **печатной с. 9** (PDF-стр. 10); с. 8 кончается сноской 8 | 🟡 **страница исправлена: 9, не 8** |
| <0,5 % годового потребления, линейное возрастное правило по портфелю, с. 3 | печ. с. 3: «If individuals adhere to an optimal linear age rule for the remainder of life, for example, welfare losses generally amount to less than 0.5% of annual consumption» | 🟢 |
| <0,06 %, ≈ $32/год, обновление в 40 и 65 лет, с. 3 | печ. с. 3: «Allowing for updating at ages 40 and 65, the welfare losses for a 20-year-old college graduate fall below 0.06 percent of annual consumption, or about $32 a year» | 🟢; уточнение: это **правило по богатству** (wealth-based) для выпускника колледжа; для возрастного правила с обновлением — **0,12 %** (с. ~24: «fall to 0.12 percent … linear age rule … and 0.06 percent … linear wealth rule») |
| 1–8 % для правил потребления, аннотация | дословно: «Consumption rules generate larger welfare losses—from 1–8% of annual consumption» | 🟢 |
| «рост до 2 %» при неопределённости, с. 4 | печ. с. 4: «welfare losses rise by as much as 2% of annual consumption when the model incorporates uncertainty in risk aversion or the discount factor»; в разделе результатов: «the welfare losses increase by about 0.4–2 percent of annual consumption, with the largest changes arising in the case of an uncertain discount rate» (с. 25–26) | 🟢 число; 🔴 **смысл в файле истолкован неверно — см. ниже** |
| «arbitrary rule … substantial», с. 6 | печ. с. 6 — дословно совпадает | 🟢 |

🔴 **Главная поправка Д1: «опровержение DeMiguel-симметрии» было прочитано не в ту сторону.**
Что именно сравнивает Love при неопределённости параметров — формула (8), с. 10, дословно:

> Suppose, for example, that a financial planner would like to offer the "best" rule of thumb for
> an individual investor of a given age, education, wealth level, and so on. The planner does not
> know the individual's risk aversion with precision, but instead has an idea of the parameter's
> distribution. <...> An optimal robust rule of thumb minimizes the expected loss <...>
> θ*_R = arg max_θ ∫ v_t(h̃_t(θ), s_t, ξ) dG(ξ).   (8)

и постановка таблицы 6 (с. 25–26): «imagine that a financial advisor would like to offer the best
consumption rule of thumb **knowing only the distribution** of risk aversion or impatience».

То есть +0,4–2 % — это цена того, что **одно правило выбирается на всё распределение
людей**, а эталон DP при этом считается **для каждого индивида с его истинными параметрами**.
DP в этом эксперименте ошибкой входов **не наказан вовсе** — ему дали правду. Это не проверка
«кто устойчивее к ошибке оценки», а цена неучтённой неоднородности. Вывод файла «при
неопределённости параметров эвристика проигрывает DP сильнее, знак против нас» —
**некорректное прочтение**: работа не содержит эксперимента, где DP решается на ошибочных
параметрах. Для FINPILOT следствие другое и полезное: у нас сплит выбирается **под каждого
пользователя** (перебор на его профиле), а не одно правило на всех — то есть ровно тот источник
потерь, который мерил Love, у нас по построению не возникает. Дыра «нет замера DP на ошибочной
модели дохода» остаётся открытой (см. Д7).

#### Д2. Ríos-Solís et al. (PLoS ONE 2017) — полный текст JATS XML
Канал: Europe PMC REST `ebi.ac.uk/europepmc/webservices/rest/PMC5400254/fullTextXML`, HTTP 200,
124 104 байта (машиночитаемый XML — числа таблиц взяты из `<table>`, не из пересказа).

- **Авторы (из `<contrib-group>`):** Yasmín Agueda **Ríos-Solís**, **Mario Alberto Saucedo-Espinosa**,
  Gabriel Arturo **Caballero-Robledo**. PLoS ONE **12(4): e0175782**, DOI `10.1371/journal.pone.0175782`.
  🟡 В файле третий автор был «M. Sánchez-Espinoza (?)» — **ошибка, исправлено: Saucedo-Espinosa**.
- **Table 2** — все числа совпали с файлом (5,84/7,19/6,64; 4,62/5,99/5,27; 4,56/7,42/5,58;
  3,43/5,67/4,06; среднее 0,06 / 571,37 с / **4,61 / 6,57 / 5,39**). 🟢
- **MILP:** цель (3) — минимизация суммарной выплаченной суммы; ограничения (4)–(15);
  переменные X_jt (платёж), C_jt (штраф за недоплату), P_jt (штраф за переплату сверх
  установленного взноса), B_jt (остаток), S_t (сбережения); бинарные Z_jt (долг жив) и Y_jt
  (переплата сверх E_jt). Штраф за недоплату, дословно (10): `(Z_jt E_jt − X_jt)(1 + h_jt) ≤ C_jt`.
  NP-трудность — **сведение подстановкой (8) в (11) к ограничениям multiple knapsack** (16),
  дословно: «Since the right-hand side of Eq (16) is a constant and variables Z_jt are binary, these
  equations correspond to the restrictions of the multiple knapsack problem». 🟡 Уточнение: это
  **набросок** («giving the main component needed for a complexity proof by reduction in an intuitive
  manner»), а не полное доказательство — на защите говорить «показано сведением», не «строго доказано».
- **0,5 %** — из текста при **Table 4** (инстансы, упорядоченные по числу кредиток), дословно:
  «the benefit of using the RPML methodology with instances with more credit-card debts is reduced
  with respect to the other alternatives. Indeed, the benefit is around 0.5% with respect to the
  highest interest rule». 🟢 Table 3 (по числу ипотек): против HInterest 4,6 / 4,3 / 4,0 / 4,1 / 3,7 %.
- **40 %** — Fig 2, дословно: «This improvement is the best one obtained from the 550 instances
  that were tested and, remarkably, it has only two bank loans and two credit card loans». 🟢
- 🔴 **Новое, и это главное для нашего довода «выигрыш оптимума — из просрочки».** Генерация
  дохода в инстансах, дословно: «The monthly incomes f_t of the debtors were obtained by adding all
  the installments they should pay monthly and multiply this value by a random number between
  [-0.5,0.5]». То есть доход задан **как сумма обязательных взносов, умноженная на случайный
  множитель** — по буквальному чтению в [−0,5; 0,5] (что дало бы отрицательный доход; вероятно,
  имелось в виду 1 + U[−0,5; 0,5] — это **неясность самой статьи**, не наша). В обоих прочтениях
  в заметной доле месяцев **дохода не хватает на обязательные платежи** — просрочка там не
  «умышленная стратегия», а вынужденная, и оптимум выигрывает тем, что **распределяет неизбежную
  недоплату** дешевле, чем Avalanche. 🟡 Значит, формулировку файла «выигрыш берётся из
  умышленной просрочки» надо смягчить до: **выигрыш берётся в режиме кассового дефицита, когда
  просрочка неизбежна; при доходе, покрывающем все минимальные платежи, эта часть выигрыша
  исчезает**. Наш инвариант `R_t ≥ 0` отсекает именно этот режим — довод держится, но на другом
  основании. Разрыв Avalanche против оптимума **при достаточном доходе** статья отдельно
  **не замеряла** — 0,5 % относится к «много кредиток», а не к «нет дефицита». Интерполяция
  файла остаётся интерполяцией; закрыть её может только наш собственный MILP-замер (Итоги п. 3.1).
- Отдельное признание статьи о пересчёте: «If her income changes or if interest rates are not as
  expected, the debtor has to compute the RPML methodology again to obtain a new plan» — точный
  оптимум так же требует полного пересчёта, как и наш перебор.

#### Д3. Rust (1997), формула (1.1) — прочитана по изображению страницы
Канал: `pdftoppm -f 6 -l 6 -r 130` (PDF-стр. 6 = печ. с. 491) → `Read` картинки. Дословно:

> (1.1)  comp(ε, d_s, d_a, β) = Θ( T / ((1 − β)² ε)^{2d_s + d_a} )

🟢 **Реконструкция показателя `2·d_s + d_a` подтверждена.** Уточнение: `T` стоит в числителе,
а знак — **Θ** (асимптотически точная граница сверху и снизу, сноска 12), не только Ω. Пометку
«реконструкция, не цитата» в §1.3 можно снять.

#### Д4. 22-МР Банка России — первичный текст добыт
Канал: `curl -sk --http1.1` → `https://www.cbr.ru/crosscut/lawacts/file/9937`, HTTP 200,
`application/pdf`, 216 984 байта, `pdftotext` — 1070 строк. 🔴 Ссылка `…/file/7653`, выданная
поиском как «методические рекомендации», оказалась **другим документом** — «Методические
рекомендации Банка России по управлению финансовым продуктом» (435 122 байта, 39 с.); не путать.

Дословно, п. 1.1:
> 1.1. Настоящие Методические рекомендации разработаны в целях обеспечения единства подходов к
> предоставлению финансовых продуктов (дополнительных услуг) в дистанционных каналах, обеспечения
> прозрачного и осознанного выбора потребителями финансовых продуктов (дополнительных услуг) в
> дистанционных каналах, улучшения качества обслуживания потребителей, стимулирования
> добросовестного, клиентоориентированного поведения финансовых организаций, а также обеспечения
> доступности финансовых продуктов.

П. 5.1: «Финансовым организациям рекомендуется внедрить … не позднее IV квартала 2025 года». 🟢
🟡 **Уточнение значимости:** адресаты — финансовые организации, предмет — **продажа продуктов и
допуслуг в дистанционных каналах** (клиентский путь, «простых и понятных формулировок», согласие
на допуслуги). Про алгоритмические рекомендации / объяснимость расчёта в тексте **ничего нет**.
На защите 22-МР годится только как «регулятор декларирует прозрачный и осознанный выбор» (п. 1.1),
а не как требование объяснимости алгоритма — такой нормы в документе нет. Файл-копия в
scratchpad сессии, текст доступен по URL выше.

#### Д5. Powell — «три проклятия размерности» по тексту самого Powell
Книга Wiley по-прежнему за пейволлом; `castle.princeton.edu/adp/` — **HTTP 404** (115 689 байт
HTML), как и тьюториал в первом прогоне. Взамен — статья самого автора: W. B. Powell,
*From Reinforcement Learning to Optimal Control: A unified framework for sequential decisions*,
arXiv:1912.03513v2, 18.12.2019 (`curl`, HTTP 200, 2 170 296 байт, `pdftotext`). Дословно:

> In fact, there are actually three curses of dimensionality: the state space, the action space,
> and the outcome space.

И там же, строкой выше — независимая от нашей арифметики оценка для табличного DP:

> In practice, this typically means that one-dimensional problems can be solved in under a minute;
> two-dimensional problems might take several minutes (but possibly up to an hour, depending on the
> dimensionality and the planning horizon); three dimensional problems easily take a week or a month;
> and four dimensional problems can take up to a year (or more).

🟢 Формулировка подтверждена первоисточником того же автора (не книгой). Оценка «3 измерения —
неделя-месяц, 4 — до года» — **эмпирическое суждение автора, не теорема**, но от признанного
специалиста по ADP; наша задача при N ≥ 1 долге имеет d_s ≥ 5.

#### Д6. 🔴 Контрпример к §3.3: DP В ПРОДУКТЕ ЕСТЬ — Franklin Templeton Goals Optimization Engine
Утверждение файла «DP в перечне методов индустрии не появляется вовсе» — **опровергнуто**.
Das, Ostrov, Radhakrishnan, Srivastav, *Dynamic Optimization for Multi-Goals Wealth Management*,
версия 25.05.2021 (J. Banking & Finance), `srdas.github.io/Papers/MultWealthGoals.pdf`, HTTP 200,
1 100 479 байт, `pdftotext`. Двое из четырёх авторов — сотрудники Franklin Templeton Investments.
Аннотация, дословно:

> We develop a dynamic programming methodology that seeks to maximize investor outcomes over
> multiple, potentially competing goals <...> Unlike Monte Carlo approaches currently in wide use
> in the wealth management industry, our approach uses investor preferences to dynamically make
> the optimal determination for fulfilling or not fulfilling each goal and for selecting the
> investor's investment portfolio.

Скорость (с. 4–5), дословно: «This optimization computation is usually completed in under 2 seconds.
Even in the most complicated case <...> a 60 year portfolio horizon, over 1000 potential wealth
values, 15 investment portfolio choices <...> and 301 competing full goals with 138 partial
alternative goals — the optimal solution is computed in only 17 seconds on a basic desktop computer».
Сложность (с. ~14): `O(i_max · T · l_max + Σ_t k_max(t))`.

Продуктовый статус — пресс-релиз Franklin Templeton от 16.09.2020 (`WebFetch`, текст): «Banks,
advisers, financial professionals and defined contribution plans can leverage the technology».
🟡 Пресс-релиз слов «dynamic programming» не содержит; связь GOE ↔ DP держится на статье с
соавторами из FT и на формулировке поисковой выдачи о премии Markowitz 2018 за «the academic
research behind Franklin Templeton's Goals Optimization Engine» — первоисточник этой фразы
(страница FT/JOIM) **не открывался**.

**Почему это не ломает наш вывод, а уточняет его.** Состояние в GOE — **одна переменная**
(богатство на сетке `i_max`), цели не несут своего остатка (выполнить/не выполнить в момент t),
портфели — 15 точек эффективной границы. Это ровно условие Carroll §1.1: DP подъёмно, когда
состояние сведено к одной переменной. У нас состояние — вектор остатков N долгов со своими ставками
(d_s = N + G + 2). Правильная формулировка для защиты: **«DP в индустрии применяется там, где
состояние одномерно (Franklin Templeton GOE: только богатство, 2–17 с); в задаче с несколькими
долгами состояние многомерно, и тот же метод упирается в §1.3»** — а не «DP никто не применяет».
Заодно та же статья подтверждает, что основная масса индустрии — Monte Carlo с фиксированными
стратегиями («forwards-in-time Monte Carlo methods that are widely used in the wealth management
industry are restricted to 1) use fixed investment portfolio strategies»).

#### Д7. Чувствительность DP к ошибке МОДЕЛИ ДОХОДА — частично закрыто
Прямого замера «DP, решённое на ошибочной модели дохода, оценённое в истинной» по-прежнему нет.
Найдено ближайшее: Gálvez, Paz-Pardo, *Richer earnings dynamics, consumption and portfolio choice
over the life cycle*, ECB WP No 2810 (`curl`, HTTP 200, 3 535 557 байт, `pdftotext`; журнальная
версия — J. Financial Economics 2025, `sciencedirect.com/…/S0304405X25002144`, не открывалась).

(а) **Оптимальная DP-политика заметно меняется от спецификации дохода** (с. ~4), дословно:
«looking at a 50-year old worker with relatively low wealth ($150,000) but high earnings ($140,000),
the canonical model recommends a high exposure into stocks, of approximately 80% of the financial
portfolio. The richer non-linear process, instead <...> suggests a more conservative strategy of
60% into stocks». То есть ошибка в модели дохода сдвигает «точный оптимум» на 20 п.п. доли.

(б) **Простое правило оказывается ближе к оптимуму при более реалистичной модели дохода**
(аннотация): «We also find renewed support for rule-of-thumb investment strategies under the model
with the nonlinear earnings process». Table 7 (с. 24–25), потери правила «100 − возраст» в %
потребления: γ = 9,17: NL **0,02** против канонической 0,18; γ = 6,4: NL **0,21** против 0,45.

(в) Про ошибку в γ, дословно: «miss-specifying γ at the level implied by the canonical process also
implies underestimating the costs of households not participating in the stock market between a
factor of 2 <...> and a factor of 7».

🟡 **Что это даёт.** Это не замер «DP на ложной модели против эвристики» — это два DP на двух
моделях. Но оно показывает два нужных нам факта: DP-оптимум **чувствителен к спецификации
дохода** на уровне самой рекомендации (80 % против 60 %), а простое правило при переходе к более
реалистичной модели **становится ближе к оптимуму**, а не дальше. Направление — в нашу пользу,
прямого числа по-прежнему нет. Дыра сужена, не закрыта.

#### Д8. Независимое подтверждение «произвольное правило хуже оптимизированного сильнее, чем оптимизированное хуже DP»
Choi, Liu, Liu, *Practical Finance: An Approximate Solution to Lifecycle Portfolio Choice*, NBER WP
34166, август 2025 (`curl`, HTTP 200, 1 790 117 байт, `pdftotext`). Дословно (аннотация): «Across
5,103 parameter sets, our approximation results in welfare that is on average only 0.06% lower than
that of the optimal solution». И (с. 21–22): «A lifetime of 60% equities reduces welfare by 3.75%,
while investing 100 minus your age percent in stocks reduces welfare by 2.00%»; вечные 100 % акций —
11,85 %, неучастие — 7,86 %. 🟢 Тот же знак, что у Love (с. 6), на **другой** модели и **5 103**
наборах параметров: аппроксимация под параметры человека — 0,06 %, общее правило — 2,00–3,75 %.
Для нас это сильнее Love: подтверждает, что выигрыш даёт **подгонка правила под индивидуальные
параметры**, а не сложность метода. Наш перебор именно это и делает.

#### Д9. Прочее
- **Das et al. arXiv:2605.02300 — 97,8 %** сверено по аннотации arXiv (WebSearch-выдача страницы
  `arxiv.org/abs/2605.02300`): «delivering expected utilities that are, on average, 97.8% of the
  optimal expected utilities (determined via Dynamic Programming)». 🟢 PDF не открывался.
  Попутно: эталон там — DP, то есть в той же GBWM-постановке DP считается и служит мерилом
  (ещё одно указание на Д6).
- **Avalanche оптимален?** Контрпример к «Avalanche ≈ оптимум при достаточном доходе» искался.
  Первоисточников с доказательством оптимальности правила наивысшей ставки при отсутствии штрафов
  **не найдено**; выдача — блоги («mathematically optimal») без доказательства, в работу не взяты.
  Ríos-Solís указывают, что упрощённые постановки Gupta et al. (Omega 1987, 15(4):323–330) и Ng et al.
  (Ann. Oper. Res. 2012, 192(1):141–150) — полиномиальные (LP), но их тексты — Elsevier/Springer
  пейволл, **не открывались**; утверждать, что в них доказана оптимальность Avalanche, нельзя.
- **Zeldes (1989)** — открытой копии не найдено и в этот раз (выдача: Oxford Academic abstract,
  страница Columbia Business School без PDF, EconPapers). Пейволл. Статус без изменений.
- **Lettau & Uhlig (1999), AER 89(1):148–174**, «Rules of Thumb versus Dynamic Programming» —
  найден как потенциальный контрпункт; авторская копия `home.uchicago.edu/~huhlig/papers/uhlig.lettau.aer.1999.pdf`
  вернула **HTTP 404** (145 475 байт HTML). По аннотации (выдача поиска, не первоисточник): правила,
  отбираемые по прошлому опыту, страдают «good state bias», и исправление требует решить DP.
  🟡 Не проверено; к нашей схеме (оценка правил симуляцией вперёд, а не по прошлому опыту) прямо
  не относится, но это тот тип возражения, который стоит знать.

### ИЗМЕНЕНИЯ ВЫВОДОВ

**Подтвердилось (сверено с первоисточником, числа из PDF/XML):**
1. Все числа Table 2 Ríos-Solís (4,61 / 6,57 / 5,39; 40 %; 0,5 % при Table 4) — 🟢.
2. Love: <0,5 %, <0,06 % ($32), 1–8 %, «as much as 2 %» — 🟢 дословно.
3. Rust (1.1): `Θ(T/((1−β)²ε)^{2d_s+d_a})` — прочитано по изображению страницы; пометку
   «реконструкция» в §1.3 можно снять.
4. «Три проклятия размерности» — по тексту самого Powell (arXiv:1912.03513), не по аннотации книги.
5. 22-МР, п. 1.1 «прозрачного и осознанного выбора» и п. 5.1 «не позднее IV квартала 2025 года» — дословно с cbr.ru.
6. Das et al. 2026 — 97,8 % (по аннотации arXiv).
7. «Оптимизированное правило ≪ произвольное правило по потерям» — **усилено независимым
   источником** (Choi–Liu–Liu 2025: 0,06 % против 2,00–3,75 % на 5 103 наборах параметров).

**Уточнилось:**
1. Love, формула (4) — **с. 9**, не с. 8. Для 0,06 % — это правило по богатству; возрастное с обновлением — 0,12 %.
2. Третий автор PLoS ONE — **Mario Alberto Saucedo-Espinosa** (не «Sánchez-Espinoza»); реквизиты: PLoS ONE 12(4): e0175782.
3. NP-трудность RPML — **набросок сведения** к multiple knapsack («in an intuitive manner»), не полное доказательство.
4. Выигрыш MILP над Avalanche берётся не из «умышленной», а из **вынужденной** просрочки: доход в
   инстансах задан как сумма взносов × случайный множитель, то есть в части месяцев его не хватает
   на обязательные платежи. Наш довод «у нас этот режим отсечён `R_t ≥ 0`» держится, но на этом
   основании. Разрыв при достаточном доходе статья **не мерила**; 0,5 % — это «много кредиток», не
   «нет дефицита». Замер — только наш собственный MILP (Итоги п. 3.1), и его ценность выросла.
5. 22-МР — про продажу продуктов/допуслуг в дистанционных каналах; **нормы об объяснимости
   алгоритма в нём нет**. Ссылаться только на п. 1.1 как на декларируемую цель.
6. Powell даёт независимую грубую шкалу для табличного DP: 3 измерения — неделя-месяц, 4 — до года.

**Опровергнуто:**
1. 🔴 **§3.3 «DP в индустрии не появляется вовсе» — неверно.** Franklin Templeton GOE — DP в продукте
   (банки, советники, пенсионные планы), 2–17 с на расчёт. Условие применимости — **одномерное
   состояние** (только богатство). Правильная формулировка: DP применяют там, где состояние
   одномерно; с несколькими долгами оно многомерно. Итог п. 1 и таблицу §2 это не ломает, но
   фразу про индустрию на защите в прежнем виде произносить нельзя — её опровергнут одним примером.
2. 🔴 **«Love: при неопределённости параметров эвристика проигрывает DP сильнее — прямое
   опровержение нашей симметрии с DeMiguel» — неверное прочтение.** Love сравнивает **одно правило
   на всё распределение людей** с DP, решённым **для каждого по его истинным параметрам** (формула
   (8), с. 10; Table 6). DP там ошибкой входов не наказан. Это цена неоднородности, а не
   устойчивости. Для FINPILOT вывод обратный: сплит выбирается на профиле конкретного пользователя,
   и этот источник потерь у нас по построению отсутствует. Абзац «🔴 Одно возражение мы обязаны
   озвучить сами» в Итогах п. 1 и строку «Устойчивость к ошибке входов» таблицы §2 надо переписать:
   «прямого замера DP на ошибочной модели нет; ближайшее (ECB WP 2810) показывает, что DP-оптимум
   сдвигается на 20 п.п. от спецификации дохода, а простое правило при реалистичной модели
   становится ближе к оптимуму».

**Всё ещё не добыто (и что вернул отказ):**
- Zeldes (1989) — открытой копии нет; Oxford Academic — пейволл (выдача без PDF).
- Powell, книга ADP — пейволл Wiley; `castle.princeton.edu/adp/` — **HTTP 404**, 115 689 байт HTML.
- Lettau & Uhlig (1999) — авторская копия `home.uchicago.edu/~huhlig/…` — **HTTP 404**, 145 475 байт HTML.
- Gupta et al. (1987), Ng et al. (2012) — пейволл Elsevier/Springer, не пробовались дальше выдачи.
- Первоисточник фразы «research behind Franklin Templeton's Goals Optimization Engine» (премия
  Markowitz 2018) — не открывался; пресс-релиз FT 2020 слова «dynamic programming» не содержит.
- Прямой замер «DP на ложной модели дохода против эвристики» — не найден (Д7 сужает, не закрывает).
- Работа с доказанным approximation ratio для правил погашения — не найдена (без изменений).

**Метод добора.** Один агент, **подагенты не запускались** (добор уложился в прямые каналы, углы
не требовали параллели). WebSearch — 12 вызовов, все с непустой выдачей, 429 не было. WebFetch — 1
(пресс-релиз FT). `curl` — 13 загрузок: 10 успешных (Love, Rust, Europe PMC XML, cbr 7653 — не тот
документ, cbr 9937, Das 2021, Powell 2019, NBER 34166, ECB 2810), 2 × HTTP 404 (castle.princeton.edu,
home.uchicago.edu). `pdftoppm` + `Read` картинки — 1 раз (формула Rust). `r.jina.ai` не использовался
(по указанию). Все числа добора взяты из разобранных PDF/XML, кроме Д9 (97,8 % — аннотация arXiv,
помечено) и Lettau–Uhlig (аннотация, помечено).
