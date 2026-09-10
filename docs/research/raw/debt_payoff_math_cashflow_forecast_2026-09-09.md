# Тема 14. Математика погашения долгов (avalanche vs snowball) и прогнозирование денежных потоков

Дата: 2026-09-09. Первичный материал, сохранён по правилу §9 CLAUDE.md.

**Бюджет.** На старте оставалось ~6 запросов WebSearch (израсходовано в сессии 23 из потолка
~29-30). Потрачено ровно 5. Дальше поиск не использовался. Все прочие источники взяты
**прямым WebFetch по URL**, что бюджет не тратит.

**Формат.** Дословные выдержки помечены «Прочитано», интерпретация вахты — «Мой вывод».
Реконструкция по памяти модели в файл не допускалась ни в одном месте; там, где источник
не открылся, стоит «не открыто».

---

## СОСТОЯНИЕ КАНАЛОВ

| Канал / URL | Итог |
|---|---|
| WebSearch «optimal debt repayment highest interest rate first proof» | открылось; выдача почти целиком популярная (Experian, Ramsey, Capital One, Fidelity, Equifax) плюс патенты USPTO. Единственная академическая ссылка — arXiv 2207.03438 |
| WebSearch «Brown Lahey "Small Victories" debt repayment NBER working paper» | открылось; дало точный номер **NBER w20125** и DOI журнальной версии |
| WebSearch «credit card debt puzzle Telyukova liquidity demand» | открылось; дало прямые URL на SSRN, MPRA, eScholarship, RES |
| WebSearch «simple exponential smoothing short time series optimal alpha forecast accuracy» | открылось; из полезного — только otexts.com (Hyndman & Athanasopoulos), остальное блоги и посторонние arXiv |
| WebSearch «статья 11 353-ФЗ досрочный возврат потребительского кредита текст» | открылось; дало прямой URL статьи на consultant.ru |
| https://arxiv.org/pdf/2207.03438 | WebFetch отказал («raw PDF binary stream»), **но сохранил файл на диск**; прочитан через Read, страницы 1-12 |
| https://www.nber.org/system/files/working_papers/w20125/w20125.pdf | то же: WebFetch отказал, файл сохранён, прочитан через Read — страницы 1-10 и 17-31 (весь текст, Tables 1-5, Figures 3-4) |
| https://escholarship.org/content/qt4c67r71r/qt4c67r71r.pdf | то же: WebFetch отказал, файл сохранён, прочитан через Read, страницы 1-6 |
| https://escholarship.org/uc/item/4c67r71r (HTML) | вернул пустую страницу; сработал только PDF по прямому адресу `/content/qt…/qt….pdf` |
| https://cepr.org/system/files/2023-02/Untangling%20the%20credit%20card%20debt%20puzzle.pdf | **HTTP 403 Forbidden**, не открыто |
| https://www.nber.org/papers/w21449 | открылось, но это Getmansky/Lee/Lo «Hedge Funds: A Dynamic Industry In Transition» — номер угадан неверно |
| https://www.nber.org/papers/w20028 | открылось, Hermalin & Weisbach по корпоративному управлению — номер угадан неверно |
| https://otexts.com/fpp2/ses.html | открылось, прочитано |
| https://www.zakonrf.info/zakon-o-potrebitelskom-kredite/11/ | **HTTP 404**, не открыто |
| https://www.consultant.ru/document/cons_doc_LAW_155986/e91b…/ | открылось, но это оглавление закона без текста статьи |
| https://www.consultant.ru/document/cons_doc_LAW_155986/10dd842d4f87b9fe0ae3a8de9f32e91ae070817d/ | открылось, текст статьи 11 получен (пересказ, см. оговорку в разделе 5) |
| Gal & McShane (2012), полный текст JMR | **не открыто** — прямого URL не было, поиск тратить не стал |
| Amar et al. (2011), полный текст JMR | **не открыто** |

**Урок процесса (мой вывод).** Два хода потрачены впустую на угадывание номеров NBER — обе
догадки вернули посторонние статьи. Номер working paper по памяти не восстанавливается,
только поиском. Зато правило «PDF нечитаем — почти всегда неправда» сработало **трижды
подряд**: три ключевых первоисточника спасены через сохранённый на диск файл и Read
с параметром `pages`. Без этого обхода вся тема осталась бы на уровне блогов Experian и Ramsey.

---

## ВОПРОС 1. Формальная оптимальность avalanche и границы этой оптимальности

### Источник 1.1 — Guasoni & Huang, «Minimizing the Repayment Cost of Federal Student Loans»

- https://arxiv.org/pdf/2207.03438 (arXiv:2207.03438v1, 7 Jul 2022). MSC 91G20, 91G80.
- Paolo Guasoni (Dublin City University; Università di Bologna), Yu-Jui Huang (Univ. of Colorado).
- Прочитаны стр. 1-12: постановка, Theorem 2.1, Lemma 3.1, Corollary 3.2, Lemma 3.3,
  Lemma 4.2, Proposition 4.3.

**Прочитано. Приоритет дорогого долга объявлен тривиальным (сноска 8, стр. 5):**

> «The case of a household with debt that carries a higher interest than student loans, such as
> credit card debt, is somewhat trivial, as the borrower's optimal policy is to pay off such debt
> first. Thus, we focus on the case of a positive spread β.»

**Мой вывод.** Это самое близкое к «формальному подтверждению avalanche», что удалось найти
в рецензируемой литературе, и это **не доказательство**. Авторы уровня Guasoni считают
порядок по ставке настолько очевидным, что выносят его за скобки задачи. Отдельной теоремы
о жадном алгоритме на множестве кредитов не найдено.

**Прочитано. Формальная рамка (стр. 5-6), структурно совпадающая с нашей.**

Динамика баланса:
> «(2.1) db_t^α = (r + β) b_t^α dt − α_t dt,  b_0 = x > 0»

Ставка дисконтирования `r` определена ровно как наш `r_bench`:
> «discounted at some rate r > 0, which represents the opportunity cost of money, i.e., the
> alternative safe return that could be obtained on any dollar used to pay off the loan. […]
> For a household without other debt, the discount rate represents the return on a safe investment.»

Допустимые стратегии зажаты минимальным и максимальным платежом:
> «A := {α : t ↦ α_t is Lebesgue measurable with m(t) ≤ α_t ≤ M(t) for 0 ≤ t ≤ T}»

где
> «m(t) reflecting the minimum payment due under income-driven repayments, and M(t) the maximum
> payment that accommodates other living expenses without incurring debt, such as credit card
> balances, which carry a higher rate than that of student loans»

**Прочитано. Структурный результат: оптимум имеет форму «максимум, затем минимум»
(Lemma 4.2, стр. 11):**

> «Lemma 4.2. For any x > 0, v(x) = inf_{α∈B} J(x, α), where
> B := {α ∈ A : ∃ t_0 ≥ 0 s.t. α_t = M(t)1_[0,t_0](t) + m(t)1_(t_0,T](t) for a.e. t ∈ [0,T]}»

И комментарий к Lemma 3.3 (стр. 10) — прямой запрет на равномерную досрочку:
> «when an optimal strategy is in positive amortization (i.e., it is repaying principal), then
> payments should be first maximal and then minimal. […] In particular, repaying a loan through
> a constant repayment rate cannot be optimal, unless such constant happens to be the maximum
> payment that a borrower can afford. As constant repayments are the default for student-loans,
> this observation indicates that inaction is unlikely to be optimal for any borrower.»

**Прочитано. Что ломает «плати максимум» — три механизма, все институциональные:**

1. Прощение остатка с налогом на прощённую сумму:
   > «If the loan is so large (or the income so low) that even maximum payments cannot erode the
   > principal, the optimal strategy is to make minimal payments indefinitely, thereby taking
   > advantage of negative amortization, because simple interest is tantamount to a separate,
   > interest-free loan on all accrued interest, which will also be forgiven.»
2. Простые (некапитализируемые) проценты — накопленный процент сам процентов не порождает.
3. Критический горизонт и критический баланс:
   > «(2.5) t_c := (T + log ω / β)^+ ∈ [0, T)» (ω — ставка налога на прощённый остаток)
   > «the cheapest repayment strategy mandates maximum payments when the initial balance is
   > sufficiently low (x < x*, "max" strategy). Otherwise (x > x*, "max-min" strategy), maximum
   > payments are in order before the critical horizon t_c»

**Прочитано. Вынесено за рамки модели (стр. 4) — это и есть список наших границ:**

> «we do not model certain actions that may be available to borrowers, such as deferment,
> forbearance, consolidation, delinquency, death, or refinancing through a private loan. […]
> delinquency […] adds collection fees to the loan's balance and significantly reduces access
> to credit by impairing the debtor's credit score.»

Налоговый вычет по процентам — почему проигнорирован (стр. 5):
> «for each taxpayer with a minimal loan amount such benefit is virtually constant across
> strategies, and therefore has no marginal effect in the choice of the optimal strategy»

Кредитный скоринг смоделирован **не отдельным ограничением, а через ставку дисконтирования**
(стр. 8):
> «the right panel of figure 1 plots the cost-to-balance ratio for PLUS loans for discount rates
> 3% and 6%, representative of borrowers with different credit scores»

Цитируемая ими эмпирика неоптимального поведения (стр. 4):
> «"the majority of distressed student loan borrowers have their loans in disadvantageous
> repayment plans even when eligible for more advantageous options". In particular, [9] find that
> over 30% of student loans of $5,000 or less are in default, even though they would be paid in
> full in ten years with monthly payments below $100»

**Мой вывод по вопросу 1.** Формальный результат найден, но он про **один** кредит с коридором
`m ≤ α ≤ M`. Из него следует наша механика «минимум по всем, весь остаток свободного потока —
в один приоритетный кредит» и, что важнее, следует **запрет на равномерное размазывание
досрочки**. Многокредитный жадный алгоритм по ставке формального доказательства
в найденной литературе не имеет — он принимается как очевидность. Про налоговый вычет ответ
получен: он не влияет на выбор стратегии, поскольку почти постоянен по стратегиям. Про
кредитный скоринг ответ получен частично: он входит не как ограничение, а как сдвиг
альтернативной доходности `r`.

---

## ВОПРОС 2. Snowball: эмпирика и точка безубыточности

### Источник 2.1 — Brown & Lahey, «Small Victories»

- NBER Working Paper **No. 20125**, май 2014. JEL C91, D03, D14.
- Alexander L. Brown (Dept. of Economics, Texas A&M), Joanna N. Lahey (The Bush School, TAMU; NBER).
- Журнальная версия: *Journal of Marketing Research*, 2015, «Small Victories: Creating Intrinsic
  Motivation in Task Completion and Debt Repayment», DOI 10.1509/jmr.14.0281 —
  https://journals.sagepub.com/doi/10.1509/jmr.14.0281
- Рабочая версия: https://www.nber.org/system/files/working_papers/w20125/w20125.pdf
- SSRN: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2438546
- Прочитаны стр. 1-10 (аннотация, введение, теория, Propositions 1-4) и 17-31 (результаты,
  Section VI, выводы, Tables 1-5, Figures 3-4).

**Прочитано. Дизайн — лабораторный и намеренно НЕ про долг:**

> «In 30 minutes, subjects attempt to retype 150 ten-character strings in a Microsoft Excel
> workbook. The strings are divided over 5 columns where the length of the columns is ascending,
> descending or even throughout as subjects progress. The completion of each column is framed as
> a distinct event for each subject.»

> «we abstract away from the debt repayment scenario in order to make sure that our subjects are
> uncontaminated with popular suggestions on how to repay debt»

**Прочитано. Теоретическая часть — Proposition 1 (стр. 6):**

> «Proposition 1. For any i, for a given class of subtask partitions, β⊂A(X). Define an ascending
> ordering, α' where |α'_1| ≤ … ≤ |α'_k| ≤ … ≤ |α'_m|, and a descending ordering where
> |α''_1| ≥ … ≥ |α''_k| ≥ … ≥ |α''_m|. Then for any α ∈ β, T_i(α') ≤ T_i(α) ≤ T_i(α'').
> If v is non-constant and α'≠α'', T_i(α')<T_i(α'').»

> «Proposition 1 shows that all that is required for the small victories approach to be effective
> in our framework is that the assumptions of social cognitive theory hold.»

Важная оговорка авторов: при доминировании конкурирующей «goal-gradient»-теории оптимален
**равномерный** порядок, которого Ramsey не предлагает:
> «if the effects of a competing, goal-gradient theory […] dominate, then dividing the task into
> equal lengths will produce optimal performance, an approach that Ramsey does not advocate»

**Прочитано. Размеры эффекта (Table 1, Panel I; N = 91):**

| Порядок | Среднее время на ячейку, сек | N | Разница с ascending | p (two-sided) |
|---|---|---|---|---|
| Ascending | 11.08 | 31 | — | — |
| Not ascending | 12.31 | 60 | 1.23 | 0.019 |
| Even | 12.13 | 31 | 1.05 | 0.078 |
| Descending | 12.50 | 29 | 1.42 | 0.015 |

Kruskal-Wallis p = 0.084. Panel II (probit на факт завершения всех 150 ячеек, опущенная
категория — even): ascending +0.13248 (s.e. 0.1222), descending −0.0963 (s.e. 0.1280), N = 91,
asc-desc chi-squared p = 0.08.

Table 3 (регрессия на среднее время ячейки, robust s.e., опущенный порядок — equal):
ascending −1.0522 (0.5862); с контролем на practice average −0.9640 (0.5518), сам practice
average 0.1266 (0.0439, p<0.01). F-тест asc-desc: p = 0.01 и 0.05.

Table 2/4 (проверка goal-gradient): последние пять ячеек столбца выполняются быстрее первых
пяти на 1.11 сек для ascending (p = 0.0000 в Table 2; p = 0.0011 при collapse to first/last,
p = 0.0699 при collapse to person). Для descending разница −1.31/−1.33 незначима (p = 0.23),
для equal −0.41/−0.39 незначима (p = 0.13/0.27).

Конвертация в производительность (стр. 17):
> «In the initial study, subjects in the ascending ordering, on average, complete a cell in 11.08
> seconds compared to 12.50 seconds in the descending ordering […] Converted to rates, these values
> are 325 and 288 cells/hour […] Thus, in terms of total performance, our results suggest subjects
> in the ascending ordering are about **13% more productive** than descending.»

**Прочитано. Choice study — snowball выбирают реже всего:**

> «In a second study, 70 subjects were given the opportunity to choose their ordering. […] Of the
> 70 subjects, 16 chose ascending, 31 chose even and 23 chose descending. A Pearson's chi-square
> test reveals these results are different from a random distribution at the 10% level. Strikingly,
> the ascending ordering […] is the least preferred. Less than one fourth of all subjects (22%)
> choose that method.»

Гетерогенность эффекта — неприятный для snowball результат:
> «Participants with higher measures of self-control benefit more from ascending than from equal
> with a one point increase in the self-control scale leading to a 0.139 second decrease in average
> cell time […] a one-point increase in critical reasoning skills leads to a one second decrease in
> average cell time […] a one-point increase in risk aversion leads to a drop of 0.71 seconds»

> «We argue a plausible extension of this result suggests the people least in need of this
> intervention are the ones most likely to benefit from it.»

> «This last finding may suggest a flaw with the debt-snowball approach: the people who would
> benefit most from small victories may be the ones least likely to be in debt.»

### 🔴 Точка безубыточности «snowball vs avalanche» — численно (Section VI, стр. 18)

Это ровно та величина, которую ставил вопрос 2 («арифметический проигрыш против выигрыша
в доведении до конца»). **Она посчитана.** Прочитано:

> «Suppose an individual has two $10,000 outstanding loans. The first loan is at 10%, and the second
> has a rate between 10% and 20%. She may make monthly repayments of $300 on either loan. Suppose
> repaying the first loan first triggers the psychological motivations of small victories, and this
> individual is able to come up with 13% more on each payment, for a total payment of $369.»

По **сроку** (Figure 3):
> «In this example for all interest rates 16% and below, this individual would pay back both loans
> faster following the small victories method than the conventional economic method. But for rates
> 17% and higher, the conventional economic method of paying down debts with a higher rate of
> interest still produces faster debt repayment even though one is paying less per month.»

По **суммарным деньгам** (Figure 4):
> «For rates 12% and lower, the additional psychological boost of the small victories and subsequent
> increase in debt repayment leads to a lower amount spent on loans than under the standard economic
> strategy. For rates between 13% and 16% inclusive, more is spent in total using the small victory
> method, but that is only when one includes the assumed $69 boost each month from following that
> method. […] For values 17% and above, it is clear the individual is spending more on loans
> following the small victories method than the conventional method.»

Обобщение авторов:
> «Even if the small victories approach can give individuals the ability to save x% more on average,
> there is a limited range around x% in which the difference between interest rates is overcome by
> the motivational boost. In general, this method works best when individuals have debts with
> similar interest rates.»

> «this increase in motivation may not offset the additional interest accrued by not paying off the
> highest-interest-rate debts first if there are relatively different interest rates across debts.»

Оговорка самих авторов о переносимости числа 13%:
> «The 13% figure is for illustrative purposes in order to show that there will be limits to the
> small victories approach. The actual number used is unimportant; for any number, there exists
> a difference in interest rates in which the small victory approach will not be beneficial.»

**Сводка (мой вывод, арифметика авторов).** Два долга по $10 000, платёж $300, надбавка 13%:

| Разрыв ставок Δ | По сроку | По суммарной сумме |
|---|---|---|
| 0-2 п.п. | snowball | snowball |
| 3-6 п.п. | snowball | спорно (зависит, считать ли $69/мес спасёнными деньгами) |
| ≥7 п.п. | avalanche | avalanche |

**Мой вывод по вопросу 2.** Величина существует: **порог примерно 6-7 процентных пунктов
разрыва ставок при мотивационной надбавке 13%.** Ниже порога snowball выигрывает даже
арифметически — не потому, что дешевле, а потому, что **увеличивает сам платёж**. Выше порога
проигрывает по обоим критериям. Ключевая слабость: 13% измерены на наборе текста в Excel,
не на долге; полевого эксперимента с рандомизацией стратегии погашения в найденной
литературе нет.

### Источник 2.2 — цитируемая линия работ (библиография сверена по списку литературы w20125)

- **Gal, David G. and Blakeley B. McShane (2012), «Can Fighting Small Battles Help Win the War?
  Evidence from Consumer Debt Management», *Journal of Marketing Research*, 49(4): 487-501.**
  🔴 Точное название — «Can **Fighting Small Battles** Help Win the War?», а не «Can Small
  Victories Help Win the War?», как значилось в постановке задачи. Полный текст **не открыт**.
  Что о нём известно из w20125 (стр. 2), прочитано:
  > «Gal and McShane (2012) provide suggestive evidence on the efficacy of this method. Using data
  > on 6000 debtors from a leading debt settlement company, they find that people who use the debt
  > snowball were more likely to eliminate their debt balance controlling for debt size in
  > comparison to other methods. Although they cannot control for selection effects (e.g. who
  > chooses this method) or omitted variables bias (e.g. taking a financial class that encourages
  > debt snowball use), their findings suggest that further study of this method is merited.»

  **Мой вывод:** наблюдательное исследование на 6000 должников, без рандомизации; сами
  Brown & Lahey называют его «suggestive» и перечисляют угрозы валидности. Как основание
  для продуктового решения оно слабее эксперимента w20125.

- **Amar, Moty, Dan Ariely, Shahar Ayal, Cynthia E. Cryder and Scott I. Rick (2011), «Winning the
  Battle but Losing the War: The Psychology of Debt Management», *Journal of Marketing Research*,
  48(SPL): S38-S50.** Полный текст **не открыт**. Из w20125 (стр. 2), прочитано:
  > «Amar et al. (2011) suggest that, when given a choice, individuals reject this economically
  > optimal method in favor of the economically sub-optimal debt snowball approach, paying off their
  > small debts first regardless of interest rate […] Because their experimental set-up does not
  > allow for motivational boosts, their participants lose money by choosing the snowball approach
  > over the economically optimal approach.»

**Противоречие между источниками — называю прямо.** Amar et al. (2011): люди **предпочитают**
snowball. Brown & Lahey, choice study: ascending выбирают **реже всего** (22%). Объяснение
самих авторов, прочитано:
> «This general trend is in contrast to Amar et al. (2011) […] albeit in a very different choice
> problem. Their environment, unlike ours, transparently resembles debt-repayment. This difference
> may cause subjects familiar with the debt-snowball strategies to follow the advice directly.»

**Мой вывод:** предпочтение snowball — не врождённая склонность, а **выученная реакция
на популярный совет** (Ramsey). Когда контекст долга снят, предпочтение исчезает.
Для FINPILOT это значит: спрос на snowball у российского пользователя может быть заметно
ниже американского, поскольку культурного слоя «Dave Ramsey» в РФ нет.

---

## ВОПРОС 3. Порог «гасить или копить» и credit card debt puzzle

### Источник 3.1 — Telyukova, «Household Need for Liquidity and the Credit Card Debt Puzzle»

- Irina A. Telyukova, University of California, San Diego. Первая версия 01.04.2005,
  прочитанная версия — 05.05.2009. eScholarship (UC San Diego, Recent Work), permalink
  https://escholarship.org/uc/item/4c67r71r, PDF
  https://escholarship.org/content/qt4c67r71r/qt4c67r71r.pdf
- Журнальная версия: *The Review of Economic Studies*, 2013, 80(3): 1148-1177 —
  https://academic.oup.com/restud/article-abstract/80/3/1148/1571542 (не открывалась)
- Прочитаны стр. 1-6 (аннотация, введение, постановка, результат калибровки).

**Прочитано. Масштаб явления (аннотация и стр. 2):**

> «In the 2001 U.S. Survey of Consumer Finances (SCF), 27% of households report simultaneously
> revolving significant credit card debt and holding sizeable amounts of liquid assets. These
> consumers report paying, on average, a 14% interest rate on their debt, while earning only 1 or 2%
> on their liquid deposit accounts. This phenomenon is known as the "credit card debt puzzle",
> as it appears to violate the standard no-arbitrage condition.»

> «In the 2001 U.S. Survey of Consumer Finances, 27% of households reported revolving an average
> of $5,766 in credit card debt, with an APR of 14%, and simultaneously, holding an average of
> $7,338 in liquid assets, with a return rate of around 1%. In fact, 84% of households who revolved
> credit card debt had some liquid assets that could be, but were not, used for credit card debt
> repayment.»

**Прочитано. Ответ на вопрос «иррациональность или рациональный спрос на ликвидность»:**

> «I offer a rigorous examination of an alternative hypothesis of why a household may choose
> rationally to hold liquid assets and revolve credit card debt simultaneously»

> «The premise is that there are large parts of household monthly expenditures that cannot be paid
> for by credit card, so they must be paid by liquid instruments. Such payments often are
> substantial in size, and include predicted expenses (such as mortgage and rent payments, utilities,
> babysitting and daycare services), as well as significant unpredictable ones (such as major
> household repairs, auto repairs and other types of emergencies).»

> «Thus, even for a household that has accumulated credit card debt, drawing down its liquid assets
> below some threshold is not an optimal choice, and the household may prioritize building its
> liquid asset holdings over debt repayment in the short to medium run.»

**Прочитано. Насколько объясняет — численно (стр. 5):**

> «The calibrated model accounts for between 85 and 104% of the households who choose to revolve
> debt while holding money in the bank, and for a median such household, for 56-62 cents of every
> dollar it holds in liquid accounts. The ranges are given for two alternative calibrations,
> depending on the choice of the risk aversion parameter.»

🔴 **Расхождение между версиями работы, называю прямо.** Прочитанная рабочая версия 2009 года
даёт **85-104%** домохозяйств и **56-62 цента** с доллара. Аннотация опубликованной версии
(по сниппету поисковой выдачи, сам текст RES 2013 не открывался) сообщает другие числа:
«between 44% and 56% of the households […] and for 100% of the liquidity held by a median
household». Числа не сходятся ни по одному из двух показателей. Какая версия окончательная —
**не установлено**; в документацию FINPILOT ни один из этих диапазонов брать нельзя, пока
не прочитана журнальная версия.

**Прочитано. Альтернативные объяснения и почему автор их отвергает:**

- Стратегическое накопление перед банкротством (Lehnert & Maki 2001): «upon examination of the
  total portfolios of the puzzle households, it appears that most of them would be unlikely to file
  for bankruptcy, as they hold significant and positive financial and nonfinancial wealth».
- Самоконтроль/контроль супруга (Bertaut & Haliassos 2002; Haliassos & Reiter 2003): «is unlikely
  to account for many of the households in the puzzle category, since it is a costly way of
  performing this kind of control. A household in the puzzle group loses, on average, **$734 per
  year**, largely from the costs of debt revolving, which amounts to **1.5% of their total annual
  after-tax income**».
- Гиперболическое дисконтирование (Laibson et al. 2001) — про пенсионные активы, не переносится:
  «retirement assets, such as IRA accounts, are nonliquid and involve a significant penalty for
  early withdrawal […] The explanation cannot apply to the credit card debt puzzle, however,
  because the tradeoff here is between two short-run decisions, and because liquid asset withdrawal
  does not incur a penalty».
- Gross & Souleles (2002) — первые задокументировали явление; идею транзакционного спроса
  на ликвидность упоминали, но «dismiss it as insufficient for the purposes of explaining
  the puzzle». Telyukova показывает обратное.

**Мой вывод по вопросу 3.** Ответ на прямой вопрос задачи: **это в основном рациональный спрос
на ликвидность, а не иррациональность.** Ключевой механизм — часть расходов физически нельзя
оплатить кредитом, и по ним есть непредсказуемая компонента, порождающая
**предосторожностный** спрос на ликвидные средства. Из этого следует, что чисто арифметическое
сравнение «ставка кредита против доходности вклада» **неполно**: у резерва есть ликвидностная
премия, не входящая в номинальную доходность. Величина премии в цитируемых цифрах: домохозяйство
«головоломки» сознательно платит $734 в год (1.5% посленалогового дохода) за право держать
ликвидность. Это и есть цена, которую люди готовы платить за резерв.

---

## ВОПРОС 4. SES на короткой истории — закрыт частично

### Источник 4.1 — Hyndman & Athanasopoulos, «Forecasting: Principles and Practice» (2nd ed.), §7.1

- https://otexts.com/fpp2/ses.html — открыто, прочитано.

**Прочитано:**

- Область применимости: SES подходит для данных «no clear trend or seasonal pattern»; прогноз
  «flat» — все будущие значения равны оценённому уровню.
- Форма взвешенного среднего: «ŷ_{T+1|T} = αy_T + (1−α)ŷ_{T|T−1}», α ∈ [0,1]; большие α
  сильнее весят свежие наблюдения, малые — историю.
- Выбор α: «the unknown parameters and the initial values for any exponential smoothing method
  can be estimated by minimising the SSE»; это «a non-linear minimisation problem», решается
  численно, замкнутой формулы нет. То есть **α и начальный уровень ℓ₀ оцениваются совместно**,
  а не задаются вручную.
- Пример: добыча нефти в Саудовской Аравии 1996-2013 → α̂ = 0.83, ℓ̂₀ = 446.6; пятилетний
  прогноз — плоская линия 542.68.
- Отличие от наивного прогноза: наивный равен последнему наблюдению, SES — экспоненциально
  взвешенное среднее всей истории.

**Мой вывод по вопросу 4 — что реально получено и чего нет.** Получено: канонический способ
выбора α (совместная минимизация SSE по α и ℓ₀), условия применимости (нет тренда и сезонности),
природа прогноза (плоский). **Не получено ничего из того, ради чего вопрос ставился:** свойств
SES именно на 3-12 наблюдениях, метрик устойчивости оценки α на коротких рядах, сравнения
с наивным прогнозом и с робастной медианной оценкой на этом горизонте. Поиск по теме дал почти
исключительно блоги и посторонние arXiv-препринты; бюджет закончился раньше, чем удалось
дотянуться до методической литературы.

🔴 **Существенное замечание вахты, следующее из прочитанного.** Пример из учебника — 18 годовых
наблюдений и α̂ = 0.83. При α = 0.83 эффективная память ряда — примерно 1/α ≈ 1.2 наблюдения,
то есть модель почти вырождается в наивный прогноз. На нашей истории в 3-12 месяцев совместная
оценка двух параметров (α и ℓ₀) по 3-12 точкам — это оценка двух параметров по выборке,
сопоставимой с их числом. Это прямо тот самый estimation error, на который указала тема 12.
**Утверждение непроверенное**, требует отдельного захода с источниками.

---

## ВОПРОС 5. Российская специфика — ст. 11 ФЗ-353

### Источник 5.1 — Федеральный закон от 21.12.2013 № 353-ФЗ, статья 11

- https://www.consultant.ru/document/cons_doc_LAW_155986/10dd842d4f87b9fe0ae3a8de9f32e91ae070817d/
- Статья: «Право заемщика на отказ от получения потребительского кредита (займа) и досрочный
  возврат потребительского кредита (займа)».

🔴 **Оговорка о качестве этого источника.** Инструмент вернул **пересказ частей 1-8, а не
дословный текст** (сработало ограничение на длину цитаты). Ниже — пересказ, не цитата.
Перед использованием в юридически значимых материалах текст статьи надо перечитать дословно.

Содержание частей 1-8 в пересказе:

1. Заёмщик вправе отказаться от кредита полностью или частично, уведомив кредитора до истечения
   срока предоставления средств.
2. **14 календарных дней** после получения кредита — досрочный возврат всей суммы или части
   **без предварительного уведомления**, с уплатой процентов за фактический срок кредитования.
3. Для **целевого** кредита — **30 календарных дней**, те же условия, без предварительного
   уведомления.
4. В остальных случаях — уведомление кредитора **не менее чем за тридцать календарных дней
   до дня возврата**, если договором не установлен более короткий срок.
5. Договором может быть предусмотрено, что частичный досрочный возврат совершается только
   в дату очередного платежа, но не позднее 30 дней после уведомления.
6. Проценты уплачиваются **включительно до дня фактического возврата** соответствующей суммы.
7. Кредитор обязан **в течение 5 календарных дней** рассчитать сумму основного долга и процентов
   на дату уведомления и предоставить эту информацию заёмщику.
8. При частичном досрочном возврате кредитор **пересчитывает полную стоимость кредита
   и уточняет график платежей**.

**Позиции ВС РФ по этой статье — не искались**, бюджет закончился. Это отдельная задача.

**Мой вывод по вопросу 5.** Для нашей механики значимы четыре факта: (а) проценты считаются
за фактический срок, до дня возврата включительно — значит модель не должна закладывать
никаких штрафов или «недополученных процентов» при досрочке; (б) законом не предусмотрена
комиссия за досрочное погашение — то есть барьер, ломающий avalanche у Guasoni & Huang
(«comisiones»), в российском потребкредите отсутствует, и это **усиливает** применимость
avalanche; (в) существует **лаг до 30 дней** между решением и фактическим списанием — наш
помесячный шаг это скрывает, а в реальности решение «в этом месяце гасим кредит X» может
исполниться только в следующем; (г) после частичной досрочки график пересчитывается кредитором,
и есть развилка «сократить срок или сократить платёж» — из текста статьи она не следует,
регулируется договором.

---

## 🔴 СЛЕДСТВИЯ ДЛЯ FINPILOT

### Вопрос 1 — наш avalanche: **подтверждает частично**

Guasoni & Huang дают формальное основание двум нашим решениям:
(а) сверх минимальных платежей весь свободный поток идёт в один кредит, а не размазывается —
«repaying a loan through a constant repayment rate cannot be optimal»;
(б) наш `r_bench` концептуально тождественен их ставке дисконтирования `r` — «alternative safe
return that could be obtained on any dollar used to pay off the loan». Формула
`r_bench = ключевая × (1 − НДФЛ)` — конкретизация их `r` под российское налогообложение вклада,
и в их рамку она ложится без натяжки.

**Ставит под вопрос одно.** Приоритет по ставке между несколькими кредитами формально
не доказан ни в одном найденном источнике. Значит, ссылаться в документации на «доказанную
оптимальность avalanche» **нельзя**. Корректная формулировка для `docs/math_model.md`:
«минимизирует суммарные проценты при допущениях: детерминированный поток, отсутствие комиссий
за досрочное погашение, отсутствие влияния на доступ к будущему кредиту, единая ставка
альтернативной доходности».

### Где наш avalanche-по-ставке даёт неоптимум — воспроизводимо

Найдены **два** класса входных данных.

**Кейс А — поведенческий (арифметика Brown & Lahey, Section VI).**
- Кредит 1: остаток 10 000, ставка 10% годовых.
- Кредит 2: остаток 10 000, ставка 12% годовых (разрыв 2 п.п.).
- Плановый ежемесячный платёж: 300.
- Поведенческая надбавка при snowball: +13% → фактический платёж 369.
- Ожидаемое: **snowball даёт и меньший срок, и меньшую суммарную выплату**.
- Граница переключения: при ставке второго кредита **17% и выше** (разрыв ≥7 п.п.) avalanche
  выигрывает по обоим критериям даже с учётом надбавки. Промежуточная зона 13-16% (разрыв
  3-6 п.п.): snowball быстрее по сроку, но дороже по деньгам.
- 🔴 Оговорка: у нас поведенческий множитель к платежу **не смоделирован вообще**. Внутри нашей
  текущей арифметики этот неоптимум **не воспроизводится** — он появляется только если ввести
  зависимость размера платежа от выбранной стратегии. Это самостоятельное продуктовое решение,
  а не техническая правка. Как тест-кейс он ставится только вместе с таким множителем.

**Кейс Б — институциональный (следует из Guasoni & Huang).** Оптимальность ломается там, где
есть механизм, обесценивающий будущий остаток: прощение долга с налогом, простые проценты,
комиссия за досрочку, субсидированная ставка, теряемая при досрочном погашении. В российском
потребкредите по ст. 11 ФЗ-353 комиссии за досрочку нет, проценты считаются за фактический
срок — то есть **основной институциональный ломатель avalanche у нас отсутствует**. Но
ипотека с господдержкой и кредитные каникулы структурно эквивалентны и в модели не учтены.

**Отдельно — контрпример к avalanche по ставке в чистом виде.** Такого контрпримера
**не найдено**. Все найденные — либо поведенческие (кейс А), либо институциональные (кейс Б).
При допущениях «нет комиссий, нет поведенческих эффектов, детерминированный поток» ни один
источник не показал входных данных, где порядок по ставке проигрывает. Это **отрицательный
результат**, и записывать его надо именно так, а не как «доказано».

### Вопрос 2 — обязаны ли мы давать snowball опцией: **ставит под вопрос текущее решение**

- «За»: при разрыве ставок ≤2 п.п. snowball выигрывает **арифметически**, не только
  психологически. У российского заёмщика с двумя-тремя потребкредитами ставки часто близки —
  случай не экзотический.
- «Против»: эффект измерен на наборе текста в Excel, не на долге; полевой проверки нет;
  выигрывают от snowball те, у кого выше самоконтроль и критическое мышление, то есть **не**
  целевая группа вмешательства; наблюдательное подтверждение (Gal & McShane) сами Brown & Lahey
  называют «suggestive».
- Практическая форма, которую это диктует: не равноправная стратегия в настройках,
  а **условная рекомендация**. Считать разрыв `max(ставка) − min(ставка)` по действующим
  кредитам и предлагать snowball только при разрыве ниже порога. По данным w20125 порог —
  порядка 6 п.п. при надбавке 13%; поскольку надбавка для нашей аудитории неизвестна, порог
  задавать консервативно: **2-3 п.п.**
- Из choice study: если snowball вводится, он должен **предлагаться системой**, а не лежать
  в настройках — сами пользователи ascending выбирают реже всего (22%).

### Вопрос 3 — порог «гасить или копить»: **ставит под вопрос чистую арифметику `r_bench`**

Telyukova показывает, что одновременное держание дорогого долга и дешёвой ликвидности —
**в основном рационально**, потому что у резерва есть ликвидностная премия сверх номинальной
доходности. Наш `r_bench = ключевая × 0.87` эту премию **не содержит**: он сравнивает
номинальную посленалоговую доходность вклада со ставкой кредита. Следствие: наш фильтр
систематически **завышает** привлекательность досрочного погашения относительно пополнения
резерва — ровно в тех случаях, когда резерв ещё не сформирован.

Смягчающее обстоятельство: у нас резерв и долг конкурируют не только через `r_bench`,
но и через SAW-критерий ликвидности с весом по риск-профилю. То есть премия за ликвидность
у нас входит не в порог, а в свёртку. **Это надо проверить отдельно:** не оказывается ли
кредит, прошедший фильтр `ставка > r_bench`, приоритетнее резерва раньше, чем следовало бы,
при консервативных профилях. Тест-кейс формулируется так: пустой резерв, кредит со ставкой
чуть выше `r_bench`, консервативный профиль — куда уходят деньги.

Численный ориентир из источника: домохозяйство «головоломки» платит **$734 в год, или 1.5%
посленалогового дохода**, за право держать ликвидность. Это верхняя оценка того, сколько
разумный человек готов переплатить за резерв.

### Вопрос 4 — SES: **не подтверждает и не опровергает**

Подтверждено только то, что α должна оцениваться минимизацией SSE совместно с ℓ₀, а не
задаваться константой, и что SES применим лишь при отсутствии тренда и сезонности —
допущение, для месячных расходов домохозяйства сомнительное (декабрь, отпуска). Свойства
на 3-12 наблюдениях **не установлены**.

### Вопрос 5 — ФЗ-353: **подтверждает, с одной оговоркой**

Отсутствие комиссии за досрочку и расчёт процентов за фактический срок означают, что главный
институциональный ломатель avalanche в РФ не действует. Оговорка — **лаг до 30 дней**
на уведомление: наш помесячный шаг предполагает мгновенное исполнение решения, а по закону
между решением и списанием может пройти месяц. Стоит проверить, не даёт ли это систематического
смещения в горизонте плана.

---

## ЧТО ОСТАЛОСЬ НЕДОСТУПНЫМ И ЧТО ДЕЛАТЬ СЛЕДУЮЩЕМУ ЗАХОДУ

1. **Доказательство оптимальности жадного алгоритма по ставке для N кредитов.** Не найдено.
   Гипотеза вахты: в экономической литературе его нет, потому что результат тривиален
   (обменный аргумент). Искать надо в OR/scheduling, в терминах «exchange argument»,
   «greedy optimality», «weighted scheduling» — **не** в терминах «avalanche» и не в economics.
2. **Gal & McShane (2012), полный текст.** Не открыт. Точная ссылка: *JMR* 49(4): 487-501,
   правильное название «Can Fighting Small Battles Help Win the War? Evidence from Consumer
   Debt Management». Идти по DOI, поиск не тратить.
3. **Amar et al. (2011), полный текст.** Не открыт. *JMR* 48(SPL): S38-S50.
4. **Журнальная версия Telyukova (RES 2013, 80(3): 1148-1177).** Не открыта. Нужна для
   разрешения расхождения чисел «85-104% / 56-62 цента» (WP 2009) против «44-56% / 100%»
   (аннотация опубликованной версии по сниппету). До разрешения — **ни один диапазон
   в документацию не брать**.
5. **Gross & Souleles (2002), «Do Liquidity Constraints and Interest Rates Matter for Consumer
   Behavior?», QJE.** Не открыт, только упоминание у Telyukova.
6. **CEPR «Untangling the credit card debt puzzle» (2023).** Отдал HTTP 403. Свежая работа,
   может пересматривать выводы Telyukova — стоит попробовать через другой хост или DOI.
7. **Вопрос 4 целиком по существу.** Свойства SES на 3-12 наблюдениях, устойчивость оценки α,
   сравнение с наивным прогнозом и робастной медианой на коротком горизонте. Точки входа:
   fpp3 (§8, otexts.com/fpp3/), работы Hyndman по model selection на коротких рядах,
   литература по M-competitions (там прямо измеряется, где наивный прогноз бьёт ES).
8. **Позиции ВС РФ по ст. 11 ФЗ-353.** Не искались.
9. **Дословный текст ст. 11 ФЗ-353.** Получен только пересказ частей 1-8. Перечитать дословно
   перед использованием в юридически значимых материалах.
10. **Страницы 11-16 и 32+ файла w20125** (детали эксперимента, Tables 6-7 по choice study)
    не читались. Файл открывается по прямому URL и читается через Read с параметром `pages`.
