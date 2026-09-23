# Г18 — повторный заход по «закрытому насовсем» (16.09.2026)

> **Условие батча.** Пункты класса 1 аудита `docs/research/queue/COVERAGE_AUDIT_2.md`
> («причина доказана, повторять бессмысленно»). Решение владельца 12.09.2026: «конечно
> тоже добываем». Заход разрешён **только новыми каналами** — теми, что по конкретному
> пункту ещё не пробовались. Повтор того же канала с тем же исходом не делается.
>
> Пиратские библиотеки (Sci-Hub, LibGen) не использовались ни разу — запрет владельца.
> Российский корневой сертификат не ставился; при требовании УЦ — `curl -sk --http1.1`.
>
> Формат блока: дословное сырьё (цитаты/таблицы) → потом выжимка. К каждому числу —
> URL, HTTP-код, размер ответа, дата снятия.

---

## Г18.1 — Chen et al., ACM CSUR 51(1), обзор метаморфического тестирования [исходная тема: prescriptive_quality_metrics_2026-09-10 / Г4]

**СТАТУС: ДОБЫТО ПОЛНОСТЬЮ.** Прежняя причина закрытия («ACM DL 403/пейволл») снята
не обходом ACM, а авторско-курсовой копией и институтским репозиторием — каналами,
которые по этому пункту не пробовались.

**Реквизиты (сняты с самого PDF, стр. 1):**
Tsong Yueh Chen, Fei-Ching Kuo, Huai Liu, Pak-Lok Poon, Dave Towey, T. H. Tse, Zhi Quan Zhou.
2018. «Metamorphic Testing: A Review of Challenges and Opportunities». *ACM Comput. Surv.*
**51, 1, Article 4 (January 2018), 27 pages.** DOI 10.1145/3143561.
🔴 Уточнение к нашей библиографии: авторы — **Chen et al.**, НЕ «Segura et al.». Segura,
Fraser, Sánchez, Ruiz-Cortés — это другой обзор, *IEEE TSE* 42(9):805–824, 2016.
В `GAP_QUEUE.md` §Г4 п.7 значится «Segura et al., ACM Computing Surveys 51(1)» — **склейка
двух разных обзоров**, её надо поправить в исходной теме (сам файл не правлю).

**Каналы и замеры (16.09.2026):**
| Канал | URL | HTTP | Размер |
|---|---|---|---|
| курсовая копия UW (CSE503, R. Just) | `https://homes.cs.washington.edu/~rjust/courses/CSE503/2021_02_12-reading2.pdf` | 200 | 351 596 байт PDF, 1 369 строк текста после `pdftotext` |
| институтский репозиторий Victoria University | `https://vuir.vu.edu.au/36919/` | 200 | 128 561 байт (страница записи; соавтор Huai Liu — VU) |
| ACM DL (прежний канал, не повторялся ради результата) | `https://dl.acm.org/doi/10.1145/3143561` | — | пейволл, зафиксирован ранее |

### Дословно — определения (стр. 4:4–4:5)

> **Definition 1 (Metamorphic Relation).** Let f be a target function or algorithm. A metamorphic
> relation is a necessary property¹ of f over a sequence of two or more inputs x₁, x₂, …, xₙ,
> where n ⩾ 2, and their corresponding outputs f(x₁), f(x₂), …, f(xₙ). It can be expressed as
> a relation R ⊆ Xⁿ × Yⁿ …
>
> ¹ A necessary property of an algorithm means a condition that can be logically deduced from
> the algorithm.

> **Definition 2 (Source Input and Follow-up Input).** … if all source inputs xᵢ (i = 1, 2, …, k)
> are specified, then follow-up inputs xⱼ (j = k+1, …, n) can be constructed based on the source
> inputs and, if necessary, their corresponding outputs.

> **Definition 3 (Metamorphic Group of Inputs).** The sequence of inputs ⟨x₁, x₂, …, xₙ⟩ is
> defined as a metamorphic group (MG) of inputs for the MR.

> **Definition 4 (Metamorphic Testing).** Let P be an implementation of a target algorithm f.
> … (1) Define R′ by replacing f by P in R. (2) Given a sequence of source test cases
> ⟨x₁, …, x_k⟩, execute them to obtain their respective outputs … Construct and execute
> a sequence of follow-up test cases ⟨x_{k+1}, …, xₙ⟩ according to R′ … (3) Examine the results
> with reference to R′. If R′ is not satisfied, then this MR has revealed that P is faulty.

> With MT, it is not necessary to investigate whether P(xᵢ) = f(xᵢ) for any individual test
> case xᵢ — which would require a test oracle. MT therefore alleviates the oracle problem
> in testing.

### Дословно — что обзор обещает и чего НЕ обещает (стр. 4:5–4:6, 4:10)

> **Advantage 1: Simplicity in concept.** … testers, even those without much experience or
> expertise, could learn how to use MT in a few hours and then correctly apply it to test
> a variety of systems.

> **Advantage 3: Ease of automation given the availability of MRs.** Apart from the MR
> identification process, it should not be difficult to automate the major steps in MT …
> Source test cases can be generated through existing testing methods, while follow-up test
> cases can be constructed through transformations according to MRs.

> **Challenge 1: Comprehensive empirical studies for a unified understanding of MT.** …
> a thorough evaluation of MT’s overall effectiveness is still lacking. Many experimental
> studies [12, 55] have used mutation analysis to evaluate the fault detection effectiveness
> of MT … However, most of these studies either focused on one particular application domain
> or were based on a set of small or medium-sized subject programs. … some previous MT
> experiments have yielded contradictory results. As discussed in a previous survey [81],
> for instance, the effectiveness of MRs (such as those in [17, 62]) **has not been conclusively
> determined.**

> **Challenge 2: Systematic MR identification and selection.** Effective MRs are the key to MT
> alleviating the oracle problem. Although many MRs have been identified for various application
> domains … and were reportedly not difficult to identify, **most of these identifications were
> conducted in an ad hoc and arbitrary way.**

> … in many cases, therefore, end users may be even more appropriate or knowledgeable than
> developers for defining good MRs [55, 98].

### Выжимка — что это меняет для FINPILOT

1. Метод применим к нашему ядру ровно потому, что у нас **оракульная проблема**: «правильный»
   план распределения свободного денежного потока не известен заранее, сравнивать не с чем.
   MT даёт проверку без оракула — через необходимые свойства модели на паре входов.
2. Наши инварианты (Rt ≥ 0, ПДН ≤ 0.40) — это НЕ метаморфические отношения, а свойства
   одного прогона. MR по Definition 1 требует **двух и более входов**: монотонность
   («+10 000 ₽ свободного потока не должен ухудшить итоговый срок закрытия долгов»),
   перестановочность (порядок долгов на входе не меняет план Avalanche), масштаб
   (умножение всех сумм на константу масштабирует план, не меняя порядок альтернатив).
3. Прямое предупреждение обзора, которое надо унести в план вехи 6: **эффективность набора MR
   доказанной не является**, а идентификация MR почти везде ad hoc. То есть MT в тестировании
   матмодели — дополнение к обычным тестам и к мутационному анализу, а не замена; и набор MR
   надо обосновывать явно, иначе он такой же ad hoc, как критикует обзор.
4. Цитируемость в тексте ВКР/доков: ссылаться на **Chen et al. 2018, ACM Comput. Surv. 51(1),
   Article 4**, 27 страниц — реквизиты сняты с первичного PDF, а не со вторичного пересказа.

---

## Г18.2 — Felfernig, IUI '08 и смежные работы по constraint-based рекомендациям [исходная тема: constraint_based_utility_recsys_2026-09-09 / Г4]

**СТАТУС: ЧАСТИЧНО — сам IUI '08 не добыт, но добыта ЖУРНАЛЬНАЯ ПРОДОЛЖАЮЩАЯ РЕДАКЦИЯ
того же коллектива по тому же предмету, в открытом доступе и целиком.** Это ровно тот
канал, который предписан Г18 («рабочая версия под другим названием») — и он сработал.

### Что найдено на авторском сайте (канал: авторская страница, ранее не пробовался)

`https://felfernig.sai.tugraz.at/publications/` → HTTP 200, 28 005 байт; оттуда ссылка на
полный список группы `https://ase.sai.tugraz.at/publications/` → **HTTP 200, 285 922 байта**
(снято 16.09.2026). В списке дословно три звена одной линии:

> A. Felfernig, G. Friedrich, E. Teppan. **Automated Debugging and Repair of Utility
> Constraints in Recommender Knowledge Bases.** In *18th International Workshop on the
> Principles of Diagnosis* (DX’07), pp. 99-105, Nashville, Tennessee, **2007**.

> A. Felfernig, G. Friedrich, E. Teppan, K. Isak. **Intelligent Debugging and Repair of Utility
> Constraint Sets in Knowledge-based Recommender Applications.** In *Proceedings of the 13th
> international conference on Intelligent user interfaces* (*IUI ’08*), Canary Islands, Spain.
> ACM, New York, NY, USA, **217–226**. **2008**.

> A. Felfernig, S. Schippel, G. Leitner, F. Reinfrank, K. Isak, M. Mandl, P. Blazek, G. Ninaus.
> **Automated Repair of Scoring Rules in Constraint-based Recommender Systems.**
> *AI Communications*, vol. **26**, no. **1**, pp. **15-27**, **2013**.

🔴 Точная пагинация IUI '08 — **217–226** (раньше в наших файлах её не было, был только DOI).

**Чем закрыт и чем не закрыт пункт:**
| Работа | Канал | HTTP / размер | Исход |
|---|---|---|---|
| IUI '08 (ACM 10.1145/1378773.1378802) | авторский сайт даёт ссылку **обратно на ACM DL**, своей копии нет | — | **не добыто**: у группы нет собственного препринта этой статьи; единственная ссылка `dl.acm.org/doi/abs/10.1145/1378773.1378802` (пейволл, зафиксирован в Г4) |
| DX'07 (рабочая версия под другим названием) | ссылка на сайте ведёт на `d1wqtxts1xzle7.cloudfront.net/...?Expires=1614008703&Signature=...` — **протухшая подписанная ссылка Academia.edu** (срок истёк 22.02.2021), и указывает она вдобавок на чужой файл («Ontologies_for_Data_Mining...») | ссылка нерабочая по построению | **не добыто** |
| AI Communications 26(1):15–27, 2013 — продолжение той же линии | `https://www.eventhelpr.com/files/events/2v0rDyN6/attachments/debuggingmaut_aU3jW7ER.pdf` | **200, 649 094 байта, PDF 1.5, 6 страниц** (авторская вёрстка, 1 484 строки текста) | 🟢 **ДОБЫТО ЦЕЛИКОМ** |

### Дословно из добытой работы (AI Communications 26(1), 2013)

Предмет — **ровно наш случай: веса и правила начисления баллов в MAUT-ранжировании
финансовых продуктов**:

> In this paper we focus on a specific knowledge acquisition aspect in constraint-based
> recommender systems development which is the development and maintenance of **utility
> constraint sets (scoring rules)**. Products included in a recommendation have to be ranked
> according to their relevance for the customer. … For the determination of such rankings we
> apply the concepts of **Multi-Attribute Utility Theory (MAUT)** where each product is
> evaluated according to a predefined set of **interest dimensions** which are abstract
> evaluation criteria for products. **Profit and availability are examples for such interest
> dimensions in the domain of financial services.**

> In many cases utility constraints are faulty, i.e., calculate rankings which are not expected
> and accepted by marketing and sales experts. **The adaptation of these constraints is extremely
> time-consuming and often an error-prone process.** We present an approach to the automated
> adaptation of utility constraint sets which is based on solutions for **nonlinear optimization
> problems**.

> The manual adaptation of utility constraints is a time-consuming and error-prone task since
> **such constraints are strongly interdependent.**

**🔴 Числа из раздела 6 «Evaluation» — прямой аналог наших раундов калибровки весов:**

> The investment recommender of an Austrian financial service provider … comprises **15
> parameters** for specifying customer requirements, **10 item properties** and about **150
> scoring rules** (interest dimensions: *availability, profit, risk*). The recommender
> application has been designed, developed, and deployed with an overall effort of about
> **12 man months**. Before deploying the first version of the application, **new versions of
> the utility constraint set have been released every third week** and tested by domain experts.
> **About 15 adaptation cycles were needed** before deploying the utility constraint set in the
> productive environment. Adaptation efforts related to the utility constraint set consumed
> about **12 hours per adaptation cycle**. This results in **180 hours** of development and
> maintenance efforts specifically related to the adaptation of the utility constraint set.

> By exploiting the presented repair functionalities, **a reduction of the overall development
> and maintenance efforts related to utility constraint sets by about 60%** … can be expected
> which means **more than 100 hours of time savings** in projects similar to the described case.

> We had to deal with a **non-linear optimization problem** since non-linear constraints are part
> of the constraint set adaptation problem. **Non-linear optimization solvers can not guarantee
> the optimality of an identified solution.**

> For example, in **finserv4** #e=**20** examples were defined for #p=**71** products. The
> corresponding utility constraint set comprised #su=**503** constraints (scoring rules). In
> order to make the 20 examples consistent with the given set of scoring rules, #so=**340** rules
> have been adapted with an average change distance avg(d)=**0.056** where each scoring rule is
> defined over the domain **[0..10]**. The time needed by the **Minos solver** to calculate the
> adaptations for finserv4 was t=**9464 milliseconds**.

Этическая оговорка авторов (важна для нашего юрблока и для позиционирования):

> At this point we also want to emphasize that **ethical aspects play an important role** when
> applying the concepts presented in this paper. **Ranking examples can also be misused for
> pushing the sales** [обрыв страницы].

**Побочная добыча, закрывающая расхождение из Г4 п.1:** в списке литературы этой статьи
Reiter процитирован как

> [23] R. Reiter. 1987. A theory of diagnosis from first principles. **AI Journal, 23, 1, 57–95**, 1987.

то есть **том 23, выпуск 1, стр. 57–95** — совпадает с той версией расхождения, которую мы
считали вероятной. Это вторичный источник (список литературы), но от прямых наследников
метода; для снятия расхождения «в каком томе» — достаточное подтверждение до открытия
первоисточника.

### Выжимка — что это меняет для FINPILOT

1. **Наша задача калибровки весов SAW — известный инженерный класс, а не наша самодеятельность.**
   Формулировка «utility constraint set / scoring rules, несогласованные с примерами ранжирования
   от экспертов» — прямой аналог наших раундов калибровки; ссылаться теперь можно на первичный
   текст, а не на пересказ.
2. **Эталонный масштаб трудозатрат: 15 циклов × 12 часов = 180 часов** на один коммерческий
   набор правил из ~150 штук. Наши **пять** раундов калибровки на фоне этого — не «много»,
   а мало; это аргумент против ощущения «мы слишком долго возимся с весами».
3. **Способ уйти от ручного перебора назван прямо:** задать набор эталонных примеров
   ранжирования от эксперта и решать задачу нелинейной оптимизации на минимальное изменение
   весов. Ограничение честно названо самими авторами: оптимальность решения не гарантируется.
   Для нашей вехи 6 это готовый шаблон теста: «набор эталонных пар альтернатив, которые модель
   обязана упорядочить так-то», и метрика — число правил, которые пришлось подвинуть, и средняя
   дистанция сдвига.
4. **Этическая оговорка авторов** («ranking examples can be misused for pushing the sales»)
   — ровно тот риск, от которого нас отделяет отсутствие продуктовой полки: у нас нет
   каталога, который выгодно продвигать. Годится как аргумент в разделе о конфликте интересов.
5. Остаётся недобытым **сам текст IUI '08** — и теперь с точной причиной: у авторской группы
   собственной копии нет, обе их ссылки ведут в ACM DL, а третья (DX'07) — протухшая подписанная
   ссылка Academia.edu 2021 года. Дальнейшие попытки по этому пункту — повтор того же канала.

---

## Г18.3 — Brown & Lahey, JMR 2015 («Small Victories») [исходная тема: behavioral_execution_gap_2026-09-10 / Г8]

**СТАТУС: ДОБЫТО (рабочая версия под другим названием).** Журнальная редакция —
*Journal of Marketing Research*, 2015, «Small Victories: Creating Intrinsic Motivation in **Task
Completion and Debt Repayment**» — закрыта SAGE. 🔴 Рабочий доклад назван **иначе**:
«Small Victories: Creating Intrinsic Motivation in **Savings and Debt Reduction**», NBER Working
Paper **No. 20125, May 2014**, JEL C91, D03, D14. Прежний заход Г8 искал по журнальному
названию и потому его не видел.

**Замер (16.09.2026):** `https://www.nber.org/system/files/working_papers/w20125/w20125.pdf`
→ **HTTP 200, 769 726 байт**, PDF 1.6; после `pdftotext` — полный текст с таблицами.

### Дословно — абстракт

> One popular approach contradicts traditional economic theory by suggesting that **people in debt
> should pay off their debts from smallest size to largest regardless of interest rate**, to realize
> quick motivational gains from eliminating debts. We more broadly define this idea as “small
> victories” … Consistent with the idea of small victories, we find that when a mildly unpleasant
> task is broken down into parts of unequal size, subjects complete these parts **faster when they
> are arranged in ascending order** (i.e., from smallest to largest) rather than descending order …
> **Yet when subjects are given the choice over three different orderings, subjects choose the
> ascending ordering least often.**

### Дословно — размер эффекта (раздел V, Таблица 1, панель I)

> In experiment 1 … subjects performed in the ascending ordering **1.42 seconds per cell faster**
> on average than in the descending ordering (**significant at the 5% level**) … This relationship
> does not substantially change when ascending is compared to the pooled results of both descending
> and even orders (**1.23 seconds per cell faster** on average, two-sided **p-value: 0.019**).
> … A Kruskal-Wallis test indicates the differences for all three orders are significant at the
> 10% level (two-tailed **p-value: 0.084**).

> In the initial study, subjects in the ascending ordering, on average, complete a cell in
> **11.08 seconds** compared to **12.50 seconds** in the descending ordering … Converted to rates,
> these values are **325 and 288 cells/hour** … our results suggest subjects in the ascending
> ordering are about **13% more productive** than descending.

### 🔴 Дословно — раздел VI, граница применимости snowball против avalanche

> Suppose an individual has two **$10,000** outstanding loans. The first loan is at **10%**, and
> the second has a rate between **10% and 20%**. She may make monthly repayments of **$300** on
> either loan. Suppose repaying the first loan first triggers the psychological motivations of
> small victories, and this individual is able to come up with **13% more on each payment**, for
> a total payment of **$369**.

> In this example **for all interest rates 16% and below**, this individual would pay back both
> loans **faster** following the small victories method than the conventional economic method.
> **But for rates 17% and higher**, the conventional economic method of paying down debts with
> a higher rate of interest still produces faster debt repayment even though one is paying less
> per month.

> Figure 4 shows the total amount spent on loans … **For rates 12% and lower**, the additional
> psychological boost … leads to a **lower amount spent** on loans than under the standard
> economic strategy. For rates **between 13% and 16% inclusive**, more is spent in total using
> the small victory method … **For values 17% and above**, it is clear the individual is spending
> more on loans following the small victories method.

> The **13% figure is for illustrative purposes** in order to show that there will be limits to
> the small victories approach. The actual number used is unimportant; **for any number, there
> exists a difference in interest rates in which the small victory approach will not be
> beneficial.**

Гетерогенность — кому помогает:

> Those with **higher self-control, better critical reasoning skills, and higher risk aversion** …
> benefit more from having chosen ascending. We argue a plausible extension of this result
> suggests **the people least in need of this intervention are the ones most likely to benefit
> from it.**

### Выжимка — что это меняет для FINPILOT

1. 🔴 **Прямая количественная опора под наш Avalanche-фильтр.** Канон v3.0.0 выбирает
   Avalanche. Эта работа — самая цитируемая в пользу Snowball — сама же и называет условие,
   при котором Snowball проигрывает: **разрыв ставок больше ~6–7 п.п.** при мотивационной
   надбавке 13 % (10 % против 17 %). В портфеле российского заёмщика разрывы куда шире
   (ипотека против карты рассрочки против МФО), то есть наш выбор Avalanche их же методом
   и подтверждается. Это сильный аргумент для главы обоснования — и он снят с первичного
   текста, а не с блога.
2. **Эффект измерен на лабораторной типографской задаче, а не на долгах.** Авторы это прямо
   оговаривают («should not be used to make definitive conclusions about debt-reduction
   situations without further analysis»). Не выдавать 13 % за доказанный прирост платежа
   по реальным долгам.
3. **Второй результат важнее первого для продукта:** когда людям дают выбрать порядок,
   они выбирают мотивационно лучший **реже всего**. Это аргумент в пользу того, что система
   должна *предлагать* порядок, а не спрашивать «как вам удобнее».
4. Материал ложится в возможный будущий гибрид: Avalanche по умолчанию, Snowball —
   как опция ровно в зоне малого разброса ставок. Канон не правлю, кладу как основание.

---

## Г18.4 — Madrian & Shea 1999/2000, рабочий доклад [исходная тема: behavioral_execution_gap_2026-09-10 / Г8]

**СТАТУС: ДОБЫТО.** Прежняя причина закрытия — «рабочий доклад 1999 не индексирован».
🔴 Она оказалась **ошибкой в дате**: рабочий доклад существует и индексирован, но он
**NBER Working Paper No. 7682, май 2000** (журнальная редакция — *QJE* 116(4):1149–1187, 2001).
Поиск «1999» его не находил.

**Замер (16.09.2026):** `https://www.nber.org/system/files/working_papers/w7682/w7682.pdf`
→ **HTTP 200, 479 053 байта**, PDF 1.3 (полный текст с таблицами и рисунками).

### Дословно — абстракт

> Before the plan change, employees were required to **affirmatively elect** participation in the
> 401(k) plan. After the plan change, employees were **automatically and immediately enrolled** …
> unless they made a negative election to opt out. **Although none of the economic features of the
> plan changed, this switch to automatic enrollment dramatically changed the savings behavior of
> employees.** … First, 401(k) participation is significantly higher under automatic enrollment.
> Second, **the default contribution rate and investment allocation chosen by the company under
> automatic enrollment has a strong influence on the savings behavior of 401(k) participants.**
> A substantial fraction … exhibit what we call "default" behavior — sticking to both the default
> contribution rate and the default fund allocation … This "default" behavior appears to result
> both from **participant inertia** and from **many employees taking the default as investment
> advice on the part of the company.**

### Дословно — числа

> The 401(k) participation rate of the WINDOW cohort at 3-15 months of tenure was **37%**. This is
> less than half the **86%** participation rate of the NEW cohort with a similar amount of tenure.

> The overall 401(k) participation rate in the study company prior to the adoption of automatic
> enrollment was **61%**. If we assume a steady-state 401(k) participation rate of **86%** … [это]
> a **25 percentage point** increase in 401(k) participation.

> … largely from inertia — employees are “stuck” at the **default contribution rate of 3%**. While
> three-quarters of non-automatically enrolled 401(k) participants have contribution rates of 6%
> or [more].

> The difference between WINDOW and NEW cohorts in the fraction of employees with a 0%
> contribution rate (nonparticipation) is **48.5 percentage points**.

> [автоматическое зачисление] substantially **decreases the variation** in 401(k) participation
> rates across various demographic subgroups … in the NEW cohort, the participation rate of women
> is **virtually identical** to that of men.

Для сравнения авторы приводят внешнюю оценку:

> a recent Buck Consultants' survey reports 401(k) participation rates of **77%** in companies
> **without** automatic enrollment and of **84%** in companies **with** automatic enrollment.

### Выжимка — что это меняет для FINPILOT

1. **Канонический размер эффекта умолчания: 37 % → 86 % участия при нулевом изменении
   экономики продукта.** Это эталонное число, на которое ссылается вся литература о nudge;
   теперь оно у нас из первоисточника с точной страницей, а не из пересказа.
2. 🔴 **Оборотная сторона — прямо против нас:** авторы называют вторую причину прилипания
   к умолчанию — **«taking the default as investment advice on the part of the company»**.
   Для СППР это значит: любое наше значение по умолчанию (риск-профиль, доля резерва,
   шаг 10 %) будет прочитано пользователем как рекомендация системы, независимо от того,
   как мы его подпишем. Это аргумент и продуктовый (умолчания надо выбирать так, будто
   они советы), и юридический (19-МР, границы «совета»).
3. Второй эффект — **сжатие различий между группами**. Умолчание выравнивает поведение
   слабых и сильных групп; для нас это довод в пользу того, что консервативное умолчание
   защищает именно наиболее уязвимого пользователя.

---

## Г18.5 — Hogarth & Karelaia 2007, журнальная редакция [исходная тема: mcda_saw_alternatives_2026-09-09 / Г8]

**СТАТУС: ДОБЫТО (рабочая версия под другим названием).** Журнальная редакция —
*Psychological Review* 114(3), «Heuristic and Linear Models of Judgment: **Matching Rules and
Environments**» — закрыта APA. Рабочая версия названа иначе: **«On heuristic and linear models
of judgment: Mapping the demand for knowledge»**, Hogarth & Karelaia, UPF Economics Working
Paper **#974, 18 июня 2006**, 66 страниц.

**Замер (16.09.2026):** `https://econ-papers.upf.edu/papers/974.pdf` → **HTTP 200, 430 728 байт**,
PDF 1.3, **66 страниц**. Запись в институтском репозитории: `https://repositori.upf.edu/items/
b4c0f3e9-e209-4063-96b2-7f5bf7b0e3a7`.
⚠️ Оговорка добросовестности: это рабочая версия, а не оттиск журнала; совпадение по составу
(единая аналитическая рамка «lens model» + мета-анализ + сравнение эвристик с линейными
моделями) и по авторам полное, но **нумерация страниц и часть формулировок могут отличаться
от редакции Psych. Review**. Цитировать как WP #974 (2006), не как журнальные страницы.

### Дословно — постановка

> This paper illuminates the distinctions in these approaches by providing **a common analytical
> framework** based on the central theoretical premise that understanding human performance requires
> specifying **how characteristics of the decision rules people use interact with the demands of
> the tasks they face.** … Our results highlight the **trade-off between linear models and
> heuristics**. Whereas the former are cognitively demanding, the latter are simple to use.
> However, **they require knowledge — and thus “maps” — of when and which heuristic to employ.**

### Дословно — мета-анализ (раздел с Таблицей 5)

> In all, we located **77 (mainly) published papers** that allowed us to examine judgmental
> performance across **252 different task environments** … They are the result of approximately
> **5,000 participants** providing a total of some **320,000 judgments.**

> Overall, the LC accuracy … is about **70%**. In interpreting this figure, it is important to
> bear in mind that it is derived from an estimate of **linear cognitive ability (ca or G·Rs) of
> 0.66** …

> we find **no differences in performance between participants who are experts or novices** …
> nor between laboratory and field studies. Holding the predictability of the environment constant
> … performance … is somewhat better with **fewer cues**, and with **equal as opposed to
> differential weighting functions.**

### 🔴 Дословно — прямо о взвешивании (Таблица 6, три признака)

> As would be expected, the **EW [equal weights] strategy performs best in equal weighting
> environments (80%)** and the **TTB [take-the-best] strategy best in the non-compensatory
> environments (77%)**. Interestingly, **in these compensatory environments, it is the EW model
> that performs best (77%)**. **The mean LC model never has the best performance.**

> … the performance of LC (at mean ca level) is **as good as or better than SVr and TTBr across
> all three types of environments** [то есть линейная модель устойчивее эвристик к ошибке
> в применении].

> … we classify functions as **non-compensatory if, when cue validities are ordered in magnitude,
> the validity of each cue exceeds the sum of those smaller than it**. We define all other
> functions as compensatory except for the special case of equal-weighting.

### Выжимка — что это меняет для FINPILOT

1. **Наш SAW — это ровно «линейная модель» из их рамки, а взвешивание критериев — предмет
   их главного результата.** Вывод, который надо унести: **в компенсаторных средах
   равновзвешенная модель обгоняет и эвристики, и среднюю линейную модель человека (77 %)**.
   То есть сложная калибровка весов даёт выигрыш только если среда действительно
   некомпенсаторная (один критерий доминирует над суммой остальных) — и у них есть
   формальный критерий этой проверки, процитирован выше.
2. 🔴 **Проверяемое следствие для вехи 6, которого у нас не было:** прогнать наши пять
   риск-профилей через критерий Мартиньон — «валидность каждого критерия превышает сумму
   меньших». Если наш набор критериев компенсаторный, то отклонение результата от
   равновзвешенного варианта — риск переусложнения, и это надо замерить как тест, а не
   обсуждать. Канон не правлю, фиксирую как основание для будущего теста.
3. **Аргумент против «экспертных весов как гарантии качества»:** эксперты и новички в
   мета-анализе неразличимы по точности. Пять раундов калибровки весов ценны как процесс
   согласования, но сами по себе точности не гарантируют — это надо честно держать
   в обосновании.

---

## Г18.0 — 🔴 ВНЕШНЕЕ ОГРАНИЧЕНИЕ БАТЧА: Wayback/Internet Archive недоступен целиком

Проверено 16.09.2026, дважды, на двух разных точках входа:

| URL | HTTP / ответ |
|---|---|
| `http://archive.org/wayback/available?url=econ.duke.edu/~brossi/GiacominiRossi08.pdf` | **429 Too Many Requests** («You have sent too many requests in a given amount of time») с первого же обращения за сессию |
| `http://web.archive.org/cdx/search/cdx?url=*.duke.edu/~brossi/*` | страница **«Internet Archive: Temporarily Offline»**: «Internet Archive services are temporarily offline. Please check our official accounts … for the latest information.» |

429 на **первом** запросе + страница обслуживания на CDX = это не наш лимит, а сторона архива.
🔴 **Следствие для батча:** канал «Wayback по старым адресам», предписанный Г18 для группы
закрытых статей и для пунктов «Ozon Банк / `urov_14g` / ФССП», **сегодня недоступен физически**.
Все пункты, где он был единственным оставшимся ходом, честно помечены ниже как «отложено
до восстановления archive.org», а не как «не добыто». Это не отрицательный результат по
существу — это недоступность инструмента, и её надо переспросить позже, а не считать
доказанной.

---

## Г18.6 — Giacomini & Rossi, журнальная редакция JAE [исходная тема: macro_in_forecast_2026-09-10 / Г6]

**СТАТУС: ДОБЫТО ПО СУЩЕСТВУ (рабочая версия под другим названием, у стороннего
институционального держателя).** Журнальная редакция — *Journal of Applied Econometrics*
**25(4), 595–620, 2010**, «Forecast comparisons in unstable environments», DOI 10.1002/jae.1177 —
закрыта Wiley; OpenAlex подтверждает `oa_status: closed`, `any_repository_has_fulltext: false`
(проверено повторно 16.09.2026, поэтому прежний вердикт Г6 по журнальной версии верен).

🔴 **Новое:** тот же материал существует в рабочей редакции **под другим названием** —
«**Model Selection and Forecast Comparison in Unstable Environments**», Raffaella Giacomini
and Barbara Rossi (UCL and Duke University) — и лежит открыто **на сайте Венгерского
национального банка** (материалы семинара MNB).

**Замеры каналов (16.09.2026):**
| Канал | URL | HTTP | Размер | Исход |
|---|---|---|---|---|
| авторская страница Duke (по RePEc) | `http://www.econ.duke.edu/~brossi/GiacominiRossi08.pdf` | **404** (редирект на `public.econ.duke.edu`, 196 байт HTML) | — | мертва, автор ушла из Duke |
| личный сайт автора | `https://www.barbararossi.eu/research` | **000** (соединение не установлено) | 0 | домен не отвечает |
| Google Sites автора | `sites.google.com/view/barbararossi/research` | **200**, но редирект на `accounts.google.com/v3/signin` | 1 241 894 | закрыт логином |
| UCL Discovery | `https://discovery.ucl.ac.uk/id/eprint/1353830/` | **403** | 5 741 | антибот |
| **Exa** → MNB | `https://www.mnb.hu/letoltes/giacomini-raffaella-20090311.pdf` | **200** | **258 515 байт**, PDF 1.3, 2 635 строк текста | 🟢 **ДОБЫТО** |
| CREI (парная работа, in-sample) | `https://crei.cat/wp-content/uploads/users/working-papers/rossi_modelcomp2015.pdf` | 200 (через Exa) | — | сопутствующее |

⚠️ Оговорка: рабочая редакция **шире** журнальной — она покрывает и in-sample (KLIC), и
out-of-sample сравнение, тогда как JAE 25(4) — только out-of-sample. Формулы и таблица
критических значений оттуда прямо соответствуют журнальной статье, но нумерация и часть
формулировок — рабочей версии. Цитировать так и надо: **рабочая версия, не журнальная.**

### Дословно — абстракт рабочей версии

> We propose new methods for analyzing the relative performance of two competing, misspecified
> models **in the presence of possible data instability**. The main idea is to develop a measure
> of the relative **“local performance”** for the two models, and to investigate its stability
> over time by means of statistical tests. … We propose two tests: a **“fluctuation test”** for
> analyzing the evolution of the model’s relative performance over historical samples and a
> **“sequential test”**, that monitors the models’ relative performance **in real time**. Compared
> to previous approaches … which are based on measures of **“global performance”** (e.g., Vuong
> (1989) and West (1996)), our focus on **the entire time path** of the models’ relative
> performance may contain useful information that is lost when looking for a globally best model.

### Дословно — Propositions 2 (out-of-sample fluctuation test)

> **Proposition 2 (Out-of-sample fluctuation test)** Suppose Assumption OOS holds. Let
> F^OOS_{t,m} = σ̂⁻¹ · m^{−1/2} · Σ_{j=t−m/2+1}^{t+m/2} ΔL_j(β̂_{j−h,R}, γ̂_{j−h,R}),
> t = R + h + m/2, …, T − m/2, where σ̂² is a **HAC estimator** of σ² …
>
> Under the null hypothesis H₀: E[ΔL_t(·)] = 0 for all t = R + h, …, T,
> F^OOS_{t,m} ⟹ [B(τ + μ/2) − B(τ − μ/2)] / √μ,
> where t = [τP], m = [μP] and B(·) is a standard univariate Brownian motion.

> Note that, unlike the in-sample test, which requires the parameters of the two models to be
> estimated by ML, **the out-of-sample test does not impose restrictions on the estimation method
> used to produce the forecasts** … [primitive conditions] essentially require the use of a
> **“rolling” or “fixed” estimation window scheme** in producing the out-of-sample forecasts.

### 🔴 Дословно — Таблица 1, критические значения k_α флуктуационного теста

Столбцы — уровень значимости **0.05** и **0.10**; строка — μ = m/P (доля окна в выборке):

| μ = m/P | α = 0.05 | α = 0.10 |
|---|---|---|
| 0.1 | **3.393** | **3.170** |
| 0.2 | **3.179** | **2.948** |
| 0.3 | **3.012** | **2.766** |
| 0.4 | **2.890** | **2.626** |
| 0.5 | **2.779** | **2.500** |
| 0.6 | **2.634** | **2.356** |
| 0.7 | **2.560** | **2.252** |
| 0.8 | **2.433** | **2.130** |
| 0.9 | **2.248** | **1.950** |

> Notes to Table 1. The table reports critical values for the in-sample and out-of-sample
> fluctuation tests F^IS_{t,m} and F^OOS_{t,m} of Propositions 1 and 2.

Критические значения для «оптимального теста» против одноразового разрыва (оттуда же):

> compare LM1 and sup_t LM2(t), t ∈ {[0.15T], …, [0.85T]}, with the following critical values:
> **(3.84; 8.85) for α = 0.05; (2.71; 7.17) for α = 0.10, and (6.63; 12.35) for α = 0.01.**
> If only LM1 rejects then there is evidence in favor of the hypothesis that **one model is
> constantly better** than its competitor. If only LM2 rejects, then there is evidence that
> there are **instabilities in the relative performance** of the two models but neither is
> constantly better over the full sample.

### Выжимка — что это меняет для FINPILOT

1. 🔴 **Это готовый инструмент для нашего прогнозного блока (SES + Монте-Карло) — и теперь
   у нас есть таблица критических значений, а не только название теста.** Флуктуационный
   тест отвечает ровно на наш вопрос: «наш прогноз стабильно лучше наивного (случайное
   блуждание / последнее значение) или он был лучше только на спокойном участке».
2. **Условие применимости совпадает с тем, как мы считаем:** out-of-sample версия **не
   требует** ML-оценивания и допускает любую процедуру прогноза, но требует **скользящего
   или фиксированного окна** оценки. Наш SES с фиксированными параметрами под это условие
   подходит; рекурсивно расширяющееся окно — нет, и это надо учесть, если оно где-то у нас есть.
3. **Что именно считать:** ΔL_t — разность функций потерь двух прогнозов в момент t;
   сглаженная сумма по окну m, нормированная HAC-оценкой дисперсии; сравнивать максимум
   |F_t| с k_α из таблицы по μ = m/P. Это реализуемо на наших данных без внешних библиотек.
4. **Главный методологический вывод против нас:** сравнение прогнозов «в среднем по выборке»
   (то, чем обычно меряют SES против наивного) может скрыть, что модель была лучше до
   структурного сдвига и хуже после. Для РФ с её ступенчатой ключевой ставкой это не
   гипотетический риск. Тест позволяет показать это числом — и это сильный аргумент
   в главе о качестве прогноза.

---

## Г18.7 — Fox 1966 и Federgruen & Groenevelt 1986 (потоки / ресурсное распределение) [исходная тема: optimization_solvers_2026-09-10, dp_vs_enumeration_2026-09-10 / Г4]

### 🔴 Сначала — исправление реквизитов в нашей же очереди

В `COVERAGE_AUDIT_2.md` и `GAP_QUEUE.md` §Г4 п.10 записано: **«Fox (1966), Operations Research
34(6):909–918»**. Это **склейка двух разных работ**. Проверено по OpenAlex и RePEc 16.09.2026:

| Работа | Верные реквизиты | DOI |
|---|---|---|
| **Fox B. L.** | «Discrete Optimization Via Marginal Analysis», ***Management Science* 13(3):210–216, ноябрь 1966** | 10.1287/mnsc.13.3.210 |
| **Federgruen A., Groenevelt H.** | «The Greedy Procedure for Resource Allocation Problems: Necessary and Sufficient Conditions for Optimality», ***Operations Research* 34(6):909–918, декабрь 1986** | 10.1287/opre.34.6.909 |

`34(6):909–918` принадлежит второй работе, а не первой. Ссылку в исходной теме надо
разделить (сам файл очереди не правлю).

### Federgruen & Groenevelt 1986 — 🟢 ДОБЫТО ЦЕЛИКОМ

**Канал, ранее не пробовавшийся: страница публикаций автора на сайте Columbia Business
School** (найдено через Exa, не через WebSearch).

`https://business.columbia.edu/sites/default/files-efs/pubfiles/4071/federgruen_greedy_procedure.pdf`
→ **HTTP 200, 438 418 байт, `application/pdf`**, PDF 1.6, 1 149 строк текста после `pdftotext`
(снято 16.09.2026). Это скан журнального оттиска, с колонтитулами *Operations Research*.
Попутно замерено: `academiccommons.columbia.edu` отдаёт **бот-челлендж Anubis** (4 371 байт,
«Making sure you're not a bot!») — туда ходить бесполезно, а на `business.columbia.edu` файл
лежит открыто.

**Дословно — шапка и аннотация:**

> THE GREEDY PROCEDURE FOR RESOURCE ALLOCATION PROBLEMS: NECESSARY AND SUFFICIENT CONDITIONS
> FOR OPTIMALITY. **AWI FEDERGRUEN**, Columbia University, New York, New York. **HENRI
> GROENEVELT**, University of Rochester, Rochester, New York. (Received **July 1984**; revisions
> received **May, November 1985**; accepted **January 1986**).
>
> In many resource allocation problems, the objective is to allocate **discrete resource units**
> to a set of activities so as to maximize a **concave objective function subject to upper bounds
> on the total amounts allotted to certain groups of activities**. If the constraints determine a
> **polymatroid** and the objective is **linear**, it is well known that the greedy procedure
> results in an optimal solution. In this paper we extend this result to objectives that are
> **“weakly concave,”** a property generalizing separable concavity.

**Дословно — постановка и определение жадной процедуры:**

> The **greedy or marginal allocation procedure** assigns available units sequentially to the
> activity that **benefits most from an additional allocation** among all activities whose
> allotment can be increased without creating infeasibilities. It terminates as soon as no such
> activity can be found. In the simplest case, r(·) is separable and A = {E} (so the model
> contains **a single budget constraint**), and as is well known, the greedy procedure results in
> an optimal solution.

**🔴 Дословно — главный результат (Corollary 1), то есть «необходимое и достаточное»:**

> **Corollary 1 (Main result).** Let A ⊂ 2^E, let V be a nonnegative, integer-valued set function
> on A, and let F = F(A, V). The MAA results in an optimal solution for every weakly concave
> order R. The following statements are **equivalent**:
> **(i) F is a polymatroid. (ii) F satisfies (F1), (F2), and (F3). (iii) MAA results in an
> optimal solution for every weakly concave order R.**
>
> Proof. … **If F is not a polymatroid, a linear objective exists for which MAA fails to generate
> an optimal solution** (see Edmonds, showing (iii) ⇒ (i)).

> **Remark. If the feasible region F is not a polymatroid, MAA may fail to generate an optimal
> solution for separable and strictly concave, as well as nonseparable, concave objectives.**

> Problems P(R, F) with R **concave** and F a polymatroid have the additional property that
> **every local optimum is a global optimum**. … (Note that the property **may fail to hold for
> weakly concave orders**.)

Практические оговорки самих авторов:

> There are two problems associated with the practicality of these optimality results: (a) it is
> often **difficult to verify whether a feasible region is a polymatroid**, and (b) each iteration
> of the greedy procedure involves **multiple checks** as to whether a particular component of
> the current solution can feasibly be incremented by one unit. This feasibility test can be
> **extremely complicated** for general polymatroids and is related to the well-known
> **“membership problem.”**

Контрпримеры, названные в тексте прямо:

> the **transportation problem with non-positive cost coefficients** is a special case of the
> problem class P; yet here, **the greedy procedure may fail** to generate an optimal solution.
> Also, the **set-covering problem** can be formulated as a special case of our class of models,
> and this problem is known to be notoriously hard; in fact, it is **strongly NP-complete**.

### Fox 1966 — НЕ ДОБЫТО, но роль работы установлена по первичному тексту 1986 года

**Каналы и точные исходы (16.09.2026):**

| Канал | URL | HTTP / размер | Что помешало |
|---|---|---|---|
| 🆕 **DTIC** (у OpenAlex записаны идентификаторы AD0626604 и AD0632054 — военно-техническое депонирование) | `https://apps.dtic.mil/sti/tr/pdf/AD0626604.pdf` и `…AD0632054.pdf` | **200, но 1 408 байт `text/html`** | 🔴 страница **«Our Site is Getting an Upgrade … We are currently performing scheduled maintenance»** — весь DTIC на обслуживании, оба идентификатора |
| 🆕 **RAND** (Фокс работал в RAND; работа вышла как препринт серии Papers) | `https://www.rand.org/pubs/papers/P3288-1.html` | **200, 26 380 байт** | карточка есть, **файла нет**: «Availability: **Web Only**», «Document Number: **P-3288-1**», «Pages: **13**», и прямо: *«Unauthorized posting of this publication online is prohibited»* — ссылки на PDF на странице отсутствуют (проверено разбором HTML: единственный `.pdf`/`dam`-линк — `search.xml`) |
| догадки о пути файла | `…/content/dam/rand/pubs/papers/2008/P3288-1.pdf`, `…/2006/…` | **404**, 17 342 байта HTML | скана нет |
| издатель | `https://doi.org/10.1287/mnsc.13.3.210` | — | INFORMS, пейволл (зафиксирован ранее) |

**Дословно — карточка RAND (первичная, снята 16.09.2026):**

> **Discrete Optimization Via Marginal Analysis.** Bennett L. Fox. Published 1966. Discrete
> optimization, **subject to one constraint**, is attacked by **Lagrangian analysis**. Incremental
> allocation schemes are given that generate **undominated allocations**. In an important special
> case, **the complete family of undominated allocations is generated.** 13 pp. Bibliog.
> Document Number: **P-3288-1**; Availability: Web Only; Year: 1966; Pages: 13.

**Дословно — чем именно Fox 1966 важен, по тексту Federgruen & Groenevelt (первоисточник
1986 года, добытый выше):**

> **Gross’ (1956) initial optimality result for models with a single budget constraint was refined
> by Fox (1966) and Veinott (1964).** The result was later rediscovered by many others, e.g.,
> Einbu (1977), Hartley (1976), Kao (1976), Mjelde (1975), Proll (1976) and Shih (1974).

То есть: Fox 1966 — **уточнение (не первое доказательство)** оптимальности жадного маржинального
распределения при **одном** бюджетном ограничении; первоисточник самого результата —
**Gross (1956)**, а не Fox. Это содержательное уточнение, которого у нас не было.

### Выжимка — что это меняет для FINPILOT

1. 🔴 **Прямое условие, при котором наш жадный Avalanche-фильтр строго оптимален, теперь
   известно и сформулировано «необходимо и достаточно»: область допустимых решений должна
   быть полиматроидом.** Простейший случай, который под это подпадает, назван в тексте прямо —
   **одно бюджетное ограничение и сепарабельная целевая функция**. Наш свободный денежный
   поток одного периода — ровно это: один бюджет, вклад каждого долга в цель считается
   независимо.
2. 🔴 **И тут же — граница, которую надо честно держать.** Как только добавляются
   дополнительные ограничения, не образующие полиматроида (а у нас есть кандидаты:
   инвариант ПДН ≤ 0.40, неснижаемый резерв, минимальные обязательные платежи по каждому
   кредиту, целевые сроки), жадная процедура **может перестать быть оптимальной даже для
   сепарабельной строго вогнутой цели** — это дословный Remark авторов. Значит, утверждение
   «Avalanche оптимален» в наших документах верно **условно**, и условие надо назвать.
3. **Практическая оговорка авторов против нас же:** проверить, что область — полиматроид,
   трудно, и membership-тест дорогой. Для продукта это довод в пользу нашего же решения —
   **перебор 66 альтернатив с шагом 10 %** вместо доказательства полиматроидности: перебор
   не требует условия оптимальности вовсе. Это аргумент в защиту канона v3.0.0 из
   первоисточника, а не из удобства.
4. **Для Fox 1966 цитировать теперь можно точно:** *Management Science* 13(3):210–216 (1966),
   он же препринт RAND **P-3288-1**, 13 стр.; содержание — лагранжев анализ при одном
   ограничении и порождение недоминируемых распределений. Роль — уточнение результата
   Gross (1956). Полный текст остаётся недобытым по конкретной причине: RAND не выкладывает
   скан и прямо запрещает его размещение, DTIC на техобслуживании.

---

## Г18.8 — Остаток группы А: Feinstein & Cicchetti 1990, Hagger 2010, Zhou & Mamon 2012 [исходные темы: prescriptive_quality_metrics, behavioral_finance_field, key_rate_history_forecastability / Г4, Г6, Г8]

**СТАТУС: НЕ ДОБЫТО ПОЛНЫМ ТЕКСТОМ, но по каждому снят ДОСЛОВНЫЙ авторский абстракт
из первичной библиографической записи (Europe PMC REST, `resultType=core`) с точной
пагинацией.** Это не полный текст, но и не пересказ: формулировки принадлежат авторам.

### Замеры каналов (16.09.2026)

| Работа | Новые каналы, испробованные в этом заходе | Исход |
|---|---|---|
| Feinstein & Cicchetti 1990 (I и II) | Europe PMC REST; Exa-поиск открытых курсовых/репозиторных копий | ни одной открытой копии; Elsevier/ScienceDirect пейволл, `jclinepi.com` — «This paper is only available as a PDF» + логин. В выдаче Exa есть агрегаторы-«скачать PDF» (`lanfanshu.com`, `kiphub.com`) — **не использованы**: непрозрачное происхождение файлов, риск пиратской перепубликации, запрет владельца |
| Hagger et al. 2010 | Europe PMC REST; OpenAlex | OpenAlex: `oa_status: closed`, `any_repository_has_fulltext: false`; единственная репозиторная ссылка `hdl.handle.net/10722/161366` (HKU Hub) — **HTTP 500**, а через `r.jina.ai` — 200/882 байта со страницей ошибки handle.net: «The handle you requested — 10722/161366 — cannot be found». Ссылка в OpenAlex мёртвая; APA `psycnet` пейволл. ResearchGate-ссылка на PDF из выдачи не использована (пользовательская перезаливка, не издательская) |
| Zhou & Mamon 2012 | Exa (поиск диссертационной главы и авторской копии у Western University) | открытой копии нет. Найдена только перезаливка на Academia.edu — **не использована** (пользовательская загрузка, не репозиторий). Elsevier ScienceDirect пейволл. Прежний вердикт Г6 («пейволл, `r.jina.ai` — капча Cloudflare») подтверждается |

### Дословно — Feinstein & Cicchetti (1990), часть I

`https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:2348207&resultType=core&format=json`
→ **HTTP 200, 3 261 байт**. Реквизиты из записи: *Journal of Clinical Epidemiology*, **том 43,
выпуск 6, стр. 543–549, 1990**, PMID 2348207, `isOpenAccess: N`, `inEPMC: N`, `hasPDF: N`.

> In a fourfold table showing binary agreement of two observers, the observed proportion of
> agreement, **p₀**, can be paradoxically altered by the chance-corrected ratio that creates
> **kappa** as an index of concordance. **In one paradox, a high value of p₀ can be drastically
> lowered by a substantial imbalance in the table's marginal totals** either vertically or
> horizontally. **In the second paradox, kappa will be higher with an asymmetrical rather than
> symmetrical imbalance in marginal totals, and with imperfect rather than perfect symmetry in
> the imbalance.** An adjustment that substitutes **kappa max** for kappa **does not repair
> either problem, and seems to make the second one worse.**

### Дословно — Cicchetti & Feinstein (1990), часть II

`…EXT_ID:2189948…` → **HTTP 200, 3 478 байт**. *J Clin Epidemiol* **43(6):551–558**, PMID 2189948.
🔴 Это **вторая статья пары**, которой в нашей очереди не было вовсе — а именно в ней лежит
рецепт, а не только диагноз:

> Among the available other omnibus indexes, **none offers a satisfactory solution for the
> paradoxes** that occur with p₀ and kappa. **The problem can be avoided only by using p_pos and
> p_neg as two separate indexes** of proportionate agreement in the observers' positive and
> negative decisions. These two indexes, which are **analogous to sensitivity and specificity**
> … If only a single omnibus index is used … **the paradoxes of kappa are desirable since they
> appropriately “penalize” inequalities in p_pos and p_neg.** For better understanding of results
> and for planning improvements in the observers' performance, however, **the omnibus value of
> kappa should always be accompanied by separate individual values of p_pos and p_neg.**

### Дословно — Hagger, Wood, Stiff, Chatzisarantis (2010)

`…EXT_ID:20565167…` → **HTTP 200, 5 110 байт**. *Psychological Bulletin* **136(4):495–525**, 2010,
PMID 20565167.

> A **meta-analysis of 83 studies** tested the effect of ego depletion on task performance …
> Results revealed a **significant effect of ego depletion on self-control task performance**.
> Significant effect sizes were found for ego depletion on **effort, perceived difficulty,
> negative affect, subjective fatigue, and blood glucose levels**. Small, nonsignificant effects
> were found for positive affect and self-efficacy. … The effect size was **moderated by
> depleting task duration**, task presentation by the same or different experimenters, intertask
> interim period, **dependent task complexity** … **Motivational incentives, training on
> self-control tasks, and glucose supplementation promoted better self-control** in ego-depleted
> samples. **Expecting further acts of self-control exacerbated the effect.** Findings provide
> **preliminary support** … **Support for motivation and fatigue as alternative explanations for
> ego depletion indicate a need to integrate the strength model with other theories.**

### Выжимка — что это меняет для FINPILOT

1. 🔴 **Каппа: практическое правило, снятое с авторского абстракта части II, применимо
   к нашей калибровке напрямую.** Согласие экспертов по эталонным ранжированиям нельзя
   отчитывать одной каппой: при перекошенных краевых суммах (а у нас перекос гарантирован —
   экспертные оценки «одобрить/не одобрить» смещены в одну сторону) каппа падает при высоком
   фактическом согласии. Требование авторов: **вместе с каппой всегда приводить p_pos и p_neg**
   (доли согласия по положительным и по отрицательным решениям). Это дешёвая правка отчётности
   по калибровке, и её надо внести.
2. **К части I добавился второй факт:** поправка κ_max проблему **не** чинит и вторую
   делает хуже — то есть популярный «обходной путь» закрыт первоисточником.
3. **Ego depletion (Hagger 2010) — цитировать осторожно.** Сам абстракт называет поддержку
   **«preliminary»** и признаёт мотивацию и усталость как альтернативные объяснения; отдельно
   известно (и это уже добыто ранее в Г8), что многолабораторная предрегистрированная
   репликация 2016 года эффект не воспроизвела. В наших текстах ссылка на «истощение силы
   воли» как на установленный механизм — завышение; корректная формулировка — «эффект
   заявлен мета-анализом 83 работ, но оспорен репликацией».
4. **Zhou & Mamon** остаётся недобытым. Для нашей задачи это наименее болезненная потеря:
   режимно-переключаемые модели ставки (Vasicek/CIR/Black-Karasinski с марковской цепью) —
   это уровень сложности, за который канон v3.0.0 намеренно не заходит (SES + Монте-Карло).
   Работа нужна была как ссылка «почему не пошли в regime-switching», и для этой роли
   достаточно реквизитов: *Expert Systems with Applications* 39(5):4679–4689, 2012,
   DOI 10.1016/j.eswa.2011.09.053.

---

## Г18.9 — Группа Б: чеки и циклы B2B-продаж. Закупки госбанков на zakupki.gov.ru + выручка вендоров [исходная тема: pfm_engine_vendors_v2_2026-09-09, business_metrics_market_sizing_2026-09-11 / Г12]

**СТАТУС: ЧАСТИЧНО.** Канал `zakupki.gov.ru` открыт и отработан впервые — результат
**отрицательный и доказанный**: закупок PFM / white-label / рекомендательных финсоветников
госбанками в ЕИС нет. Зато добыта **первичная выручка публичного вендора (Диасофт)** из
раскрытия эмитента — и она даёт порядок чека косвенно.

### Б.1. `zakupki.gov.ru` — канал работает, содержимого нет

🔴 **Технический приём, который стоит записать отдельно:** ЕИС **не открывается** обычным
`curl`/`WebFetch` из-за российского TLS-сертификата, но берётся **`curl -sk --http1.1`**
(проверка сертификата отключена, российский корневой УЦ НЕ устанавливался — запрет владельца
соблюдён). Замер: HTTP **200, 247 130 байт** на первый же запрос.

🔴 **И вторая ловушка, на которой можно было потерять весь пункт:** параметр `af=on`
(«показывать только актуальные») в URL расширенного поиска **обнуляет выдачу по историческим
закупкам**. Замерено в одном и том же запросе: «рекомендательная система» с `af=on` → **0
записей**, без `af=on` с `fz44=on&fz223=on&fz94=on` → **16 записей**. Прежний вывод «ничего
нет» из такого запроса был бы артефактом фильтра.

**Запросы и счётчики (все — 16.09.2026, поиск по 44-ФЗ + 223-ФЗ + 94-ФЗ, морфология включена):**

| Поисковая строка | Записей |
|---|---|
| рекомендательная система | **16** |
| финансовый маркетплейс | **33** |
| маркетплейс финансовых продуктов | **15** |
| инвестиционный советник | **7** |
| финансовый ассистент | 51 |
| личный финансовый помощник | 105 |
| система управления личными финансами | 882 |
| white label банк | 9 |
| советник по кредитам | **0** |
| персональный финансовый помощник (с `af=on`) | 0 |

Большие числа (105, 882, 51) — **артефакт морфологического поиска**: он разбивает фразу и
находит по отдельным словам. Ручной разбор выдачи по двум самым релевантным запросам это
подтверждает.

**Дословно — что реально лежит в выдаче по «рекомендательная система» (16 записей, разобраны
первые 11):** поставка книг в библиотеки (СПб ГБУ «ЦБС Петроградского района», 1 724 576,10 ₽;
РНБ, 1 513 734,72 ₽; КузГТУ, 399 990,92 ₽; КубГУ, 1 570 664,60 ₽; Академия танца Эйфмана,
262 823,86 ₽), плюс три технологические:

> 44-ФЗ, № **0373100072123001080**, «Выполнение научно-исследовательских работ
> «**Рекомендательная нейросетевая система**»». Заказчик: **ФГБНУ «Российский научный центр
> хирургии имени академика Б.В. Петровского»**. Начальная цена **1 000 000,00 ₽**.
> Размещено 10.08.2023.

> 223-ФЗ, № **32009816623**, «Открытый запрос предложений на право заключения договора на
> **услуги по разработке системы «Рекомендательный сервис» для обучающего корпоративного
> портала ПАО «Ростелеком»**». Заказчик: **ПАО «Ростелеком»**. Начальная цена
> **10 296 000,00 ₽**. Размещено 17.12.2020.

> 223-ФЗ, № 32211854102 и № 32211519246, «Оказание услуг по размещению информационных
> материалов в сети Интернет в **рекомендательной системе Пульс**». Заказчик: **АО «Газета
> Метро»**. Начальная цена **2 976 000,00 ₽** (обе). 2022 год. — это **реклама в чужой
> рекомендательной ленте**, а не покупка системы.

По «инвестиционный советник» (7 записей) — ни одной закупки ПО: книги для Парламентской
библиотеки (414 050,00 ₽), книги для Воронежской области (322 278,04 ₽) и Сахалина
(1 317 850,00 ₽), и два конкурса **ГАОУ ДПО «Московский центр технологической модернизации
образования»** — образовательный конкурс для школьников 14–18 лет «Финансовый советник»,
**2 494 833,33 ₽** (№ 32009668019, 2020) и **2 463 333,00 ₽** (№ 31908439175, 2019).

**Проверка «а публикуются ли вообще госбанки в ЕИС» — неполная.** Прогон по ИНН
7707083893 (Сбербанк), 7702070139 (ВТБ), 7744001497 (Газпромбанк), 7725114488 (Россельхозбанк)
дал: 7744001497 → **0 записей**, остальные три → страница без блока счётчика (парсер вернул
`NA`, то есть структура ответа иная — вероятно, «поиск не дал результатов» в другой вёрстке).
🔴 Это **не доказывает** отсутствие банков в ЕИС; это значит, что прогон по ИНН заказчика
через строку поиска — неподходящий инструмент, нужен фильтр `customerIdOrg` по справочнику
организаций. Отложено как незакрытый хвост.

**Вывод по Б.1, который можно утверждать:** в открытом реестре закупок **нет ни одной
закупки PFM-движка, white-label личного финансового помощника или рекомендательного
финсоветника** — ни госбанками, ни кем-либо ещё. Ближайший по смыслу технологический
контракт — **рекомендательный сервис для корпоративного портала Ростелекома, 10,3 млн ₽**
(не финансовый домен). То есть чек B2B-продажи PFM через ЕИС **не восстанавливается,
потому что такие сделки туда не попадают**: банки покупают это вне 223-ФЗ-процедур,
через дочерние ИТ-компании и прямые договоры.

### Б.2. Выручка вендоров из раскрытия эмитента — 🟢 ДОБЫТО (Диасофт)

**Канал: официальные релизы ПАО «Диасофт» (тикер DIAS), сайт эмитента.** Замеры 16.09.2026,
все через `curl -sk --http1.1`:

| Документ | URL | HTTP | Размер |
|---|---|---|---|
| Аудированные результаты МСФО за **2025 финансовый год** (закончился 31.03.2026), релиз от **25.06.2026** | `https://www.diasoft.ru/about/news/22236/` | **200** | **54 652 байта** |
| Результаты МСФО за 6 месяцев 2025 ФГ (до 30.09.2025), релиз от **26.11.2025** | `https://www.diasoft.ru/about/news/21846/` | **200** | **54 863 байта** |

**Дословно — итоги 2025 финансового года (релиз 25.06.2026):**

> ПАО «Диасофт» … объявляет консолидированные финансовые результаты за 12 месяцев 2025
> финансового года, закончившегося **31.03.2026**.
> • **Выручка составила 9,8 млрд рублей**, что на **3% ниже** аналогичного показателя за
>   прошлый финансовый год. Давление на показатель оказывает **экономия ИТ-бюджетов
>   заказчиков, удлинение цикла согласования бюджета** и возросшая сложность реализуемых
>   проектов.
> • **Возобновляемая выручка составила 8,5 млрд рублей**, что на **9% выше** по сравнению
>   с предыдущим годом.
> • **Законтрактованная выручка составила 24,5 млрд рублей** по состоянию на 31.03.2026,
>   что на **13 %** выше аналогичного показателя на 31.03.2025.
> • **EBITDA … 1,9 млрд рублей**, что на **35% ниже** … на фоне роста оплаты труда в
>   ИТ-отрасли … **Рентабельность по EBITDA составила 19,4%.**
> • **Чистая прибыль составила 527 млн рублей.** Снижение … обусловлено единовременными
>   расходами, связанными с начислением резерва на задолженность ассоциированной компании.
> • **Затраты на разработку программного обеспечения (R&D) … составили 1,4 млрд рублей.**

**Дословно — полугодие 2025 ФГ (релиз 26.11.2025):**

> Выручка за 6 месяцев 2025 финансового года составила **3,9 млрд рублей**. При этом
> возобновляемая выручка увеличилась на **15%** год к году. Законтрактованная выручка
> достигла **21,9 млрд рублей** по состоянию на 30.09.2025 … рост на **7%** … EBITDA за
> шестимесячный период составила **407 млн рублей**. Первое полугодие … характеризуется
> **более высокой себестоимостью работ на ранних этапах крупных проектов, значительная часть
> доходов по которым будет отражена во втором полугодии.**

**ЦФТ и BSS — не добыто.** Обе компании непубличные, раскрытия эмитента у них нет; их выручка
доступна только через платные системы (СПАРК, Контур.Фокус) либо через бухгалтерскую
отчётность в ГИР БО, что в этом заходе не пробовалось. Это **следующий конкретный ход**,
а не тупик: ГИР БО (`bo.nalog.ru`) отдаёт годовую отчётность юрлиц бесплатно.

### Выжимка — что это меняет для FINPILOT

1. 🔴 **Главный вывод по чеку B2B — методологический: его нельзя восстановить из открытых
   реестров, и теперь это доказано, а не предположено.** Формулировка «не публикуется»
   в аудите была верной по существу, но без метода; теперь есть метод и числа: 16 + 33 + 15 +
   7 записей по четырём профильным запросам, ни одной банковской закупки PFM.
2. **Числа Диасофта дают верхнюю рамку рынка, в котором мы НЕ конкурируем.** Лидер
   ПО для финансового сектора РФ — **9,8 млрд ₽ выручки в год**, при этом выручка **падает
   на 3 %**, а EBITDA — на **35 %**, и причина названа самим эмитентом: **«экономия
   ИТ-бюджетов заказчиков, удлинение цикла согласования бюджета»**. Для нас это прямой
   сигнал: **B2B-продажа банку в 2026 году — плохой первый канал** (бюджеты режут, цикл
   растёт), и это аргумент за B2C-подписку как стартовую модель.
3. **Косвенная оценка цикла сделки — из того же релиза:** «более высокая себестоимость
   работ на ранних этапах крупных проектов, значительная часть доходов по которым будет
   отражена **во втором полугодии**» плюс законтрактованная выручка **24,5 млрд ₽** против
   годовой **9,8 млрд ₽** — то есть портфель контрактов примерно **2,5 годовых выручки**.
   Это означает **многолетние контракты с признанием выручки в течение 2–3 лет**, а не
   продажу коробки. Соло-основателю такой цикл не финансируем.
4. **Хвост на следующий заход:** ЦФТ и BSS через ГИР БО (`bo.nalog.ru`), и закупки банков
   через фильтр `customerIdOrg` вместо строки поиска.

---

## Г18.10 — Группа Г: практика по 211-ФЗ, реестр операторов финансовых платформ ЦБ [исходная тема: regulation_world_advice_boundary / Г7]

**СТАТУС: ДОБЫТО ПО РЕЕСТРУ И НАДЗОРНОЙ СТАТИСТИКЕ; судебная практика — НЕ ДОБЫТА
(канал заблокирован на уровне доступа).**

### Г.1. `kad.arbitr.ru` — 🔴 заблокирован жёстко, причина точная

`POST https://kad.arbitr.ru/Kad/SearchInstances` с браузерным UA, `Referer`, `X-Requested-With`
и корректным JSON-телом → **HTTP 451, 1 715 байт**, страница «**Доступ заблокирован**».
451 (Unavailable For Legal Reasons) — блокировка по географии/правовым основаниям, а не
антибот и не капча. Ни `-k`, ни смена заголовков этого не лечат; `r.jina.ai` тут тоже не
поможет, потому что нужен POST-запрос к API, а прокси выполняет GET.
**Вывод:** практика по 211-ФЗ через картотеку арбитражных дел **недоступна из этой среды**.
Это внешнее ограничение, а не отсутствие материала.

### Г.2. 🟢 Реестр операторов финансовых платформ ЦБ — ДОБЫТ ЦЕЛИКОМ, машиночитаемо

**Путь, которого не было в прежних заходах:** старый адрес `cbr.ru/registries/finplatform/`
даёт **404 (11 101 байт)**; живой раздел — `https://www.cbr.ru/finm_infrastructure/
financial_platform_operators/` (**HTTP 200, 55 574 байта**), и в нём лежит XLSX реестра.

`https://www.cbr.ru/vfs/finmarkets/files/supervision/list_financial_platform_op.xlsx`
→ **HTTP 200, 19 596 байт**, OOXML. Заголовок внутри файла дословно:
**«Реестр операторов финансовых платформ по состоянию на 15.09.2026»**.

**Действующие операторы (13), дословно из файла — наименование · ИНН · сайт · дата
включения в реестр:**

| № | Оператор | ИНН | Сайт | Включён |
|---|---|---|---|---|
| 1 | ПАО «Московская Биржа ММВБ-РТС» | 7702077840 | `www.moex.com`; **`www.finuslugi.ru`** | **27.08.2020** |
| 2 | АО ВТБ Регистратор | 5610083568 | `www.vtbreg.com` | — |
| 3 | АО «Финансовый Маркетплейс **Сравни.ру**» | 9705151291 | `www.sravni.market`; `www.sravni.ru` | **26.08.2021** |
| 4 | АО «Открытый финансовый маркетплейс» (АО «ОФМ») | 9710090580 | `www.opfm.ru` | **21.12.2021** |
| 5 | АО «**Банки.ру** Маркетплейс» | 7727478748 | `bankiplatforma.ru`; `banki.ru` | **06.09.2022** |
| 6 | АО «Финфорт МП» | 9715411580 | `www.finorma.ru` | **16.03.2023** |
| 7 | АО «ВАНТА» | 9722011181 | `www.vanta.ru` | **18.05.2023** |
| 8 | АО «Единые финансовые решения» (АО «ЕФР») | 9709079649 | `efr.ru` | **22.06.2023** |
| 9 | АО «Универсальные Финансовые Технологии» (АО «УФТ») | 9703150574 | `www.fin-id.ru` | **27.06.2024** |
| 10 | АО «**Авито Финанс**» | 9710138465 | `www.avitofinance.ru` | **27.03.2025** |
| 11 | АО «**Т-ОФП**» (контакт `t-ofp@tbank.ru`) | 7743465217 | `t-ofp.ru` | **21.08.2025** |
| 12 | АО «**ЯНДЕКС ФИНАНСОВАЯ ПЛАТФОРМА**» | 9705242929 | `finance.yandex.ru` | **25.12.2025** |
| 13 | АО «ФИНСДЕЛКА» (Новосибирск) | 5405509490 | `finsdelka.ru` | **18.06.2026** |

**Исключённые из реестра (3) — то есть «отрицательные» решения ЦБ, которых у нас не было
вовсе:**

| Оператор | ИНН | Включён | **Исключён** |
|---|---|---|---|
| АО «Специализированный депозитарий «ИНФИНИТУМ» | 7705380065 | 22.10.2020 | **18.04.2023** |
| АО «Открытые цифровые решения» | 9703023417 | 17.02.2022 | **13.04.2023** |
| АО «Финансовая Платформа» (`fin.live`) | 9718176159 | 22.06.2022 | **06.03.2026** |

### Г.3. 🟢 Надзорная статистика рынка — «Обзор платформенных сервисов в России за 2025 год»

`https://www.cbr.ru/Collection/Collection/File/62088/platform_services_2025.pdf`
→ **HTTP 200, 974 342 байта**, PDF 1.4, **19 страниц**, издан Департаментом инфраструктуры
финансового рынка в 2026 г. Раздел 3, дословно:

> По состоянию на **31.12.2025** в реестр Банка России включены сведения о **13 операторах
> финансовых платформ** (ОФП), из них **3 ОФП пришли на рынок в 2025 году**. К осуществлению
> деятельности **приступили 10 операторов**.

> В 2025 г. на рынке ОФП произошел существенный рост ключевых показателей. Количество
> получателей финансовых услуг (ПФУ) увеличилось на **58% г/г (+3,1 млн лиц)**, достигнув
> **8,4 млн лиц** по состоянию на 31.12.2025. Количество финансовых организаций и эмитентов,
> предлагающих продукты на финансовых платформах, возросло на **76% г/г (+110 лиц)**,
> до **255 единиц**.

> По итогам 2025 г. объем сделок, заключенных на финансовых платформах, составил
> **498,4 млрд руб. (+42% г/г)**. В структуре сделок преобладали договоры банковских услуг —
> **479,8 млрд руб. (96%)**, из них **450,9 млрд руб.** пришлось на **банковские вклады**.
> Также в отчетный период на финансовых платформах заключены сделки по **выдаче кредитов
> в объеме 28,8 млрд рублей**.

Из графика (рис. 18) — ряд зарегистрированных ПФУ / в том числе активных, млн лиц:
31.03.2024 — 1,96 / 0,07 · 30.06.2024 — 2,88 / 0,09 · 30.09.2024 — 4,12 / 0,14 ·
31.12.2024 — 5,33 / 0,16 · 31.03.2025 — 6,20 / 0,21 · 30.06.2025 — 6,85 / 0,24 ·
30.09.2025 — 7,56 / 0,33 · **31.12.2025 — 8,43 / 0,39**.

### Выжимка — что это меняет для FINPILOT

1. 🔴 **Самое важное число всего блока — доля активных.** Зарегистрированных получателей
   услуг **8,43 млн**, активных — **0,39 млн**, то есть **4,6 %**. Рынок финансовых
   маркетплейсов в РФ выглядит массовым по регистрациям и остаётся крошечным по
   использованию. Для нашей воронки это прямой ориентир: регистрация ≠ пользователь,
   и планировать надо от активных.
2. **Состав реестра подтверждает границу нашего правового режима.** Все 13 операторов —
   это площадки **совершения сделок** (вклады 450,9 млрд ₽ из 498,4 млрд ₽). Мы сделок
   не совершаем и денег не принимаем — значит, под 211-ФЗ не попадаем; прежний вывод
   Г19 («под лицензирование в РФ не попадаем») теперь подпёрт первичным реестром и
   надзорным обзором, а не рассуждением.
3. **Появились соседи, которых в наших обзорах не было:** «Авито Финанс» (27.03.2025),
   «Т-ОФП» (21.08.2025), «Яндекс Финансовая платформа» (25.12.2025) — то есть в рынок
   за полтора года вошли Авито, Т-Банк и Яндекс. Это меняет картину конкурентного
   окружения: дистрибуция финансовых продуктов консолидируется у экосистем.
4. **Три исключения из реестра** (ИНФИНИТУМ 2023, «Открытые цифровые решения» 2023,
   «Финансовая Платформа» 06.03.2026) — материал для главы о рисках: лицензируемый статус
   не только выдают, но и снимают.
5. **Хвост:** судебная практика по 211-ФЗ остаётся недобытой из-за HTTP 451 на
   `kad.arbitr.ru`. Альтернативные каналы, не пробованные: `sudact.ru`, `ras.arbitr.ru`,
   раздел «Решения Банка России» на `cbr.ru` (предписания и меры).

---

## Г18.11 — Группа Д: письма ФНС (Telegram Stars, цифровая валюта, внутриигровая валюта) [исходная тема: monetization_and_graveyard_2026-09-10 / Г7]

**СТАТУС: ЧАСТИЧНО — по цифровой валюте разъяснения ФНС СУЩЕСТВУЮТ и найдены (прежний
вердикт «не существуют» опровергнут); по Telegram Stars и внутриигровой валюте — не найдено,
и это похоже на действительное отсутствие, а не на недоступность канала.**

### Д.1. Канал `nalog.gov.ru` — открыт, но поиск по нему бесполезен

`https://www.nalog.gov.ru/rn77/about_fts/about_nalog/` («**Письма ФНС России, обязательные
для применения налоговыми органами**») → **HTTP 200, 172 665 байт**, снято 16.09.2026
через `curl -sk --http1.1`. Раздел живой, но это **постраничный листинг на 114 страниц**
(в HTML видны ссылки `…/1.html` … `…/114.html` и карточки писем вида `…/16649778/`),
без поиска по тексту внутри раздела.

Собственный поиск сайта:
`https://www.nalog.gov.ru/rn77/search/?text=цифровая+валюта` → **HTTP 200, 78 042 байта**;
`https://www.nalog.gov.ru/search/?text=Telegram%20Stars` → **HTTP 302** (редирект на
региональную версию). В выдаче видны только счётчики разделов («Документы 24970, Новости
259171, Веб-страницы 45507»), сами результаты подгружаются скриптом — то есть **поиск
`nalog.gov.ru` без исполнения JS результатов не отдаёт**. Это точная причина, по которой
прежний заход Г7 ничего не увидел.

### Д.2. 🔴 Цифровая валюта — разъяснение ФНС НАЙДЕНО

**Письмо ФНС России от 25.12.2024 № СД-4-3/14625@ «О заполнении декларации по операциям
с цифровой валютой»** — обнаружено через внешний поиск (КонсультантПлюс, hotdoc 87761)
и подтверждено содержательными публикациями на самом `nalog.gov.ru`.

Первичная страница ФНС, снятая дословно (16.09.2026):
`https://www.nalog.gov.ru/rn38/news/activities_fts/15671352/` → **HTTP 200, 72 242 байта**:

> Налогообложение майнинга осуществляется в рамках **общей системы налогообложения (ОСНО)** …
> Причем налогоплательщики, осуществляющие майнинг цифровой валюты, **не вправе применять
> упрощенную систему налогообложения (УСН) и единый сельскохозяйственный налог (ЕСХН)**.
> … 🔴 **При осуществлении операций с цифровой валютой (включая куплю-продажу) не могут
> использоваться: автоУСН, специальный налоговый режим для самозанятых (НПД), патентная
> система налогообложения (ПСН).**
>
> В целях исчисления налога на прибыль организаций доход от майнинга признается
> **внереализационным доходом**. … При продаже цифровой валюты по общему правилу доход
> (выручка) определяется исходя из фактической цены реализации цифровой валюты, **но не ниже
> ее рыночной котировки, уменьшенной на 20 %**.
>
> Лицам, осуществляющим майнинг (в том числе **участникам майнинг-пула**), необходимо
> предоставлять в ФНС России информацию о получении цифровой валюты … Срок представления
> данной информации — **не позднее 20-го числа месяца**, следующего за месяцем получения.

Плюс работающий сервис-раздел `https://www.nalog.gov.ru/mining/` → **HTTP 200, 410 385 байт**
(реестр лиц, осуществляющих майнинг; порядок подачи заявлений УКЭП; оговорка:
«Сведения, внесенные в реестр … **не подлежат опубликованию** в средствах массовой информации»).

### Д.3. Telegram Stars и внутриигровая валюта — не найдено, с оценкой характера отсутствия

Целевой поиск по запросу «Telegram Stars налог ФНС разъяснение НДС Россия» не дал **ни одного**
документа ФНС. Вся выдача — вторичная (`t-j.ru`, `vc.ru`, `dtf.ru`, `kod.ru`), и в ней
повторяется один фактический тезис: **в стоимость пакетов Telegram Stars при покупке из РФ
включён НДС 20 %**, то есть налог платит **продавец услуги (Telegram)**, а не получатель
звёзд. Официального письма ФНС именно про Stars не существует в открытом доступе.

⚠️ Честная оговорка: отсутствие в выдаче ≠ отсутствие в природе, но здесь два независимых
признака в пользу того, что письма действительно нет: (1) тема свежая и узкая, (2) по
соседней и куда более массовой теме (цифровая валюта) письмо находится немедленно и
цитируется всеми. Поэтому пункт закрывается как **«разъяснения нет»**, а не «не добыли».

### Выжимка — что это меняет для FINPILOT

1. 🔴 **Прямое ограничение на монетизацию, которого мы не учитывали.** Если бы приём оплаты
   когда-либо шёл через криптовалюту/цифровую валюту, то **НПД (самозанятость), ПСН, АУСН
   и УСН по таким операциям применять нельзя** — дословный запрет из разъяснения ФНС.
   Для соло-основателя, который планирует стартовать на НПД или УСН, это означает: **канал
   оплаты в цифровой валюте закрывает льготный режим целиком**. Вывод для стратегии
   монетизации однозначный — оплата только в рублях, обычным эквайрингом.
2. **Telegram Stars как канал оплаты подписки** остаётся в серой зоне без разъяснения ФНС.
   НДС 20 % внутри цены звёзд платит Telegram; что происходит на стороне получателя выплаты
   — официально не разъяснено. Для продукта с планкой «152-ФЗ и соответствие» строить
   основную монетизацию на канале без позиции регулятора — риск; допустимо как
   дополнительный, не как основной.
3. **Метод на будущее:** искать документы ФНС **не** её собственным поиском (он не отдаёт
   результатов без JS), а по номеру письма через внешние правовые базы, затем подтверждать
   содержание на региональных страницах `nalog.gov.ru/rnXX/news/activities_fts/…`, которые
   отдаются обычным `curl -sk`.

---

## Г18.12 — Группа В: CPA-ставки банков и МФО в РФ — 🟢 ДОБЫТО, С ЦИФРАМИ [исходная тема: monetization_and_graveyard_2026-09-10, business_scaling_2026-09-11 / Г7]

**СТАТУС: ДОБЫТО ПОЛНОСТЬЮ.** Прежний вердикт аудита — «розничные CPA банков РФ публично
не раскрываются». 🔴 **Опровергнут:** публичный каталог офферов партнёрской сети **LEADS.SU**
отдаёт ставки, EPC, EPL, конверсию и процент подтверждения **без регистрации**.

**Замер (16.09.2026):** `https://leads.su/offers` → **HTTP 301** на `https://leads.su/offer-catalog`;
`https://leads.su/offer-catalog` → **HTTP 200, 252 323 байта**, первая страница каталога,
данные в статическом HTML (JS не нужен). `curl -sk --http1.1`, российский корневой УЦ
не устанавливался.

**Что означают колонки — дословно с той же страницы (пояснение самой сети):**

> **EPC** — средний заработок с клика … **EPL** — средний заработок с лида … **CR** —
> конверсия; она отражает, какая доля пользователей после перехода выполняет нужное действие.
> **AR** — процент подтверждённых лидов; чем он выше, тем стабильнее итоговый результат.

### 🔴 Таблица ставок, дословно (страница 1 каталога, 16.09.2026)

| Оффер | Выплата от, ₽ | Выплата до, ₽ | EPC | EPL | CR, % | AR, % |
|---|---|---|---|---|---|---|
| **Альфа банк — «РКО»** | **8 950** | **12 530** | n/a | n/a | n/a | n/a |
| **Промсвязьбанк — Потребительский кредит** | **8 330** | **8 664** | 0.00 | 0.00 | 11.69 | 0.00 |
| **Т-Банк HR** | **8 400** | **8 400** | 12.65 | 50.00 | 20.18 | 0.59 |
| **ВТБ РКО** | **2 000** | **7 282** | n/a | n/a | n/a | n/a |
| **Совкомбанк РКО** | 2 184 | 6 553 | n/a | n/a | n/a | n/a |
| **Т-Банк РКО** | 2 913 | **6 553** | 44.93 | **1 343.00** | 3.34 | 22.22 |
| **УралСиБ** | 506 | 6 011 | *«Процент: до 6%»* | n/a | n/a | n/a |
| **Альфа-Банк кредит наличными, рефинансирование** | 1 721 | **13 770** | 1.29 | 16.70 | 19.44 | **0.97** |
| **Т-Банк Кредитная карта** | **3 932** | 3 932 | 45.77 | 179.98 | **29.45** | 4.57 |
| **Совкомбанк карта рассрочки Халва** | 2 184 | 2 184 | 14.21 | 86.49 | 16.43 | 3.96 |
| **Т-Банк Black** (дебетовая) | 1 092 | 1 311 | 36.24 | 228.52 | 17.81 | 17.43 |
| **Т-Банк КАСКО** | 1 456 | 1 456 | n/a | n/a | n/a | n/a |
| **Совкомбанк Кредитный доктор** | 510 | 510 | 4.55 | 24.28 | 18.75 | 4.76 |
| Быстроденьги online (МФО) | 3 276 | 3 276 | **179.73** | 645.93 | 27.82 | 16.46 |
| Creditplus (МФО) | 1 820 | 1 820 | 61.56 | 582.16 | 10.65 | 31.98 |
| Zaymigo (МФО) | 2 184 | 2 184 | 62.68 | 363.30 | 19.75 | 14.25 |
| Pay P.S. (МФО) | 1 602 | 2 184 | 0.00 | 0.00 | 3.94 | 0.00 |
| Kviku (МФО) | 1 456 | 1 456 | 18.61 | **1 456.00** | **1.27** | **100.00** |
| Вебзайм (МФО) | 110 | **6 553** | **184.70** | **1 242.02** | 15.68 | 28.76 |
| Деньги на дом (МФО) | 124 | **5 825** | 46.92 | 168.28 | **28.63** | 5.85 |
| Webbankir (МФО) | 291 | 2 840 | 83.49 | 560.62 | 16.20 | 21.14 |
| Vivus.ru (МФО) | 146 | 2 549 | 48.88 | 368.60 | 14.62 | 13.69 |
| Fastmoney (МФО) | 364 | 2 549 | 28.60 | 200.56 | 15.91 | 6.64 |
| Turbozaim (МФО) | 218 | 1 383 | 55.98 | 214.60 | 27.36 | 18.50 |
| Доброзайм (МФО) | 110 | 1 311 | 19.12 | 93.90 | 26.91 | 7.60 |
| Займ экспресс (МФО) | 1 092 | 1 092 | 32.41 | 165.34 | 19.60 | 15.14 |
| Центрофинанс OFFLINE | 1 311 | 1 311 | 45.37 | 5.40 | *738.62* | 0.41 |
| Вам одобрено | 95 | 95 | n/a | n/a | n/a | n/a |
| YesKredit RU / FIN.MARKET | 0 | 0 | n/a | n/a | n/a | n/a |

Вертикали в каталоге, дословно: «Банки · Финансы · Дебетовые карты · Микрокредиты ·
Кредитование · Беттинг · HR-офферы · Для блогеров · Для SEO». Внизу — «Следующая страница»,
то есть выборка не исчерпывающая; снята первая страница.
⚠️ Аномалия, которую не сглаживаю: у «Центрофинанс OFFLINE» CR = **738.62** — это не проценты,
а артефакт офлайн-оффера (лидов больше, чем кликов). Цифру не использовать.

### Выжимка — что это меняет для FINPILOT

1. 🔴 **Порядок CPA в рознице РФ теперь известен точно: от ~100 ₽ (МФО, нижняя граница)
   до ~13 800 ₽ (кредит наличными Альфа-Банка, верхняя).** Массовые банковские продукты:
   кредитная карта Т-Банка — **3 932 ₽**, дебетовая Black — **1 092–1 311 ₽**, Халва —
   **2 184 ₽**, потребкредит ПСБ — **8 330–8 664 ₽**. Это прямой вход в юнит-экономику
   гипотетического партнёрского канала, которой у нас до сих пор не было.
2. 🔴 **И тут же — главный отрезвляющий факт: `AR` (процент подтверждённых лидов).**
   У Альфа-Банка по кредиту наличными AR = **0,97 %**, у Т-Банк Кредитной карты — **4,57 %**,
   у Халвы — **3,96 %**. То есть **реальная выплата за лид** (EPL) там **16,70 ₽** и
   **179,98 ₽** соответственно — при номинальной ставке 13 770 ₽ и 3 932 ₽.
   **Ставка в каталоге завышает доход в 50–800 раз относительно того, что реально
   приходит.** Любая наша модель «зарабатываем на переходах в банк» должна считаться
   по **EPL**, а не по «выплата до».
3. **Самые высокие EPC — у МФО** (Вебзайм 184,70; Быстроденьги 179,73) — то есть
   монетизация трафика в РФ прибыльнее всего именно там, куда нам идти нельзя: продукт,
   советующий человеку **выходить из долгов**, не может зарабатывать на выдаче ему займов.
   🔴 Это не этическая ремарка, а **структурный конфликт интересов**, и он теперь
   подтверждён цифрами. Для раздела о позиционировании и для юрблока (19-МР, границы
   «совета») — это сильный аргумент: партнёрская модель с МФО несовместима с нашим
   ценностным предложением, и отказ от неё надо зафиксировать как решение, а не
   как умолчание.
4. **Вывод по каналу для нас:** если партнёрка вообще, то только «нейтральные» продукты
   с честным AR — дебетовая карта (Black: AR 17,43 %, EPL 228,52 ₽) или РКО
   (Т-Банк РКО: EPL **1 343 ₽** при AR 22,22 %). Но и там EPL на пользователя —
   сотни рублей, то есть **партнёрка не заменяет подписку**, а в лучшем случае
   добавляет к ней.

---

## Г18.13 — Группа Е: разбивка категории Finance у RevenueCat — 🔴 ПРИЧИНА УСТАНОВЛЕНА ДОСЛОВНО [исходная тема: paid_launch_readiness_2026-09-11, business_metrics_market_sizing_2026-09-11 / Г12]

**СТАТУС: ЗАКРЫТО ОКОНЧАТЕЛЬНО, НО ТЕПЕРЬ С ДОКАЗАННОЙ ПРИЧИНОЙ.** Прежняя запись —
«разбивка категории Finance у RevenueCat не публикуется». Теперь известно **почему**:
🔴 **у RevenueCat нет категории Finance вообще** — она методологически растворена в «Utilities».

**Замер (16.09.2026):** `https://www.revenuecat.com/state-of-subscription-apps/`
→ **HTTP 200, 1 782 371 байт** (отчёт **State of Subscription Apps 2026**, онлайн-версия);
`…/state-of-subscription-apps-2025/` → **HTTP 200, 877 703 байта**.

### Дословно — раздел методологии, «Category bucketing (App Store and Google Play)»

> The App Store (iOS) and Google Play (Android) each have numerous categories. For clearer
> analysis, we’ve aggregated or ‘bucketed’ closely-related categories under common labels:
> **Utilities: includes Weather, Reference, Utilities, Finance, Tools, and more.**
> Health & Fitness: includes Health & Fitness, Medical. … Business … Productivity: includes
> Graphics & Design, Art & Design, Developer tools. …

Иначе говоря: искать «Finance breakdown» бессмысленно — ближайший доступный прокси для
нашего жанра это **Utilities**, и он смешан с погодой, справочниками и инструментами.
В онлайн-версии заявлено, что в PDF (330+ страниц) есть «**11 by-category breakouts**» —
но список бакетов в методологии тот же, отдельного Finance среди них нет.

### Дословно — база отчёта и общие числа (2026)

> built on the world’s largest in-app subscription data set — over **115,000 apps**,
> representing more than **$16 billion in revenue**.

> Three years ago, about **2,000 new subscription apps launched every month. Today that number
> is almost 15,000.** AI removed a decade old supply constraint on apps … This will be seen as
> **more competition, higher CACs, and higher churn.** (Jacob Eiting, CEO)

> **Only 4.6% of newly launched apps reach $10K in monthly revenue within two years.**

> Even top categories like **Health & Fitness and Utilities take more than 100 days to reach
> >$10k**, which means that you'd have to wait around 30% of the year to confirm if your app
> has the chance to be a top performer.

### Дословно — числа по Utilities (ближайший к нам бакет)

> Other high performers include: Health & Fitness (6.9%), Education (6.5%), and **Utilities
> (6.5%)** [медиана D30 download-to-trial].

> The industry anchors hard at 50% off, with median discount is **−50.1%** with remarkably tight
> clustering across categories, though **Utilities pulls deepest at −63%** … **~16pp deeper than
> the overall median.**

> Travel and Utilities **cluster in the middle tier** [по RLTV первого месяца, где
> Health & Fitness $24.23 против Gaming $8.41].

### Дословно — общие бенчмарки, применимые к нам напрямую

> median Y1 RLTV per payer is **$32 in North America, $25 in Western Europe, $23 globally,
> and $14 in IN/SEA**.

> median D35 download-to-paid rate is **2.6% in North America** vs. **1.4% in IN/SEA**.

> the median app grew monthly recurring revenue (MRR) **5.3% year-on-year**, but **top-decile
> apps grew 306%+**.

> median yearly prices rose slightly from **$31.60 to $34.80** while weekly (**$5.99**) and
> monthly (**$10**) held steady. … The P90 yearly [dropped] from $92 to $90.

> median trial-to-paid … **10.7% for apps with hard paywalls versus 2.1% in freemium apps.**

> Annual … median retention is **28% (down from 31%)**. By contrast, weekly sits near **1%**
> and monthly at **8%**. … **Freemium (28%) and hard paywall (27%) are nearly identical —
> access model is not a retention lever.**

> **Business** leads trial conversion at **9.1%** median … Business median Y1 RLTV: **$35.48**,
> top quartile above **$69.19**.

> Business is an overlooked category that **monetizes and retains users the most**, and users
> are usually **unhappy with the existing solutions**.

### Выжимка — что это меняет для FINPILOT

1. 🔴 **Пункт закрывается не «не нашли», а «такой разбивки не существует по методологии
   поставщика данных».** Это качественно другой ответ, и его надо зафиксировать: больше
   к RevenueCat за Finance-срезом не ходить.
2. **Рабочий прокси для наших плановых чисел — Utilities**, с двумя поправками, которые сам
   отчёт и даёт: конверсия загрузка→триал у Utilities **6,5 %** (выше среднего), но скидки
   в категории самые глубокие — **−63 %** против −50,1 % по рынку. То есть жанр конвертит
   нормально, но **живёт на скидке**, и это надо закладывать в модель цены, а не открывать
   потом как сюрприз.
3. 🔴 **Число, которое должно стоять в плане запуска первым: только 4,6 % новых приложений
   доходят до $10K MRR за два года**, и даже у сильных категорий на первые $10k уходит
   **больше 100 дней**. Плюс предложение выросло с 2 000 до **~15 000** новых подписочных
   приложений в месяц за три года. Прогноз самого CEO — «больше конкуренции, выше CAC,
   выше отток».
4. **Годовая подписка — единственный удерживающий формат:** медианное удержание годовой
   **28 %**, месячной — **8 %**, недельной — **~1 %**. При этом **жёсткий пейволл против
   freemium удержание не меняет** (27 % против 28 %), но меняет конверсию в оплату
   в **пять раз** (10,7 % против 2,1 %). Для нас это прямой аргумент за годовой план
   и за жёсткий, а не «бесконечно бесплатный» доступ.
5. **Ценовой ориентир из первоисточника:** медианная годовая цена подписки **$34.80**,
   месячная **$10**, недельная **$5.99**. Наши российские ориентиры (249/1 490 ₽ у Дзен-мани
   и т. п.) лежат заметно ниже мировой медианы — это ожидаемо для РФ, но теперь есть с чем
   сравнивать.

---

## Г18.14 — Группа Е: разбор закрытия Maybe Finance — 🔴 ПРЕЖНИЙ ВЕРДИКТ ОПРОВЕРГНУТ, ДОБЫТО ЦЕЛИКОМ [исходная тема: monetization_and_graveyard_2026-09-10 / Г14]

**СТАТУС: ДОБЫТО — и это, возможно, самый ценный материал батча для нашего продукта.**
В аудите значилось: «разбор закрытия Maybe — **основатель не опубликовал**». 🔴 Неверно:
опубликовано **четыре** первичных разбора, тремя разными людьми, с цифрами. Прежний заход
искал не там (искали пост-мортем на сайте продукта; он лежит в **релизе на GitHub**,
в **треде основателя** и в **посте ведущего разработчика**).

**Замеры (16.09.2026):**
| Источник | URL | HTTP | Размер |
|---|---|---|---|
| Прощальный релиз v0.6.0 (инженерный разбор) | `https://github.com/maybe-finance/maybe/releases/tag/v0.6.0` | **200** | **239 668 байт** |
| README архивного репозитория V1 | `https://github.com/maybe-finance/maybe-archive` | **200** | **346 588 байт** |
| Пост ведущего разработчика Зака Голлвитцера | `https://www.zachgollwitzer.com/2025/07/24/reflections-on-building-a-viral-OSS-personal-finance-app/` | **200** | **23 851 байт** |
| Пост основателя о пивоте (LinkedIn, 16.08.2025) + тред `@Shpigford` | `linkedin.com/posts/joshpigford_…`, `threadreaderapp.com/thread/1747085524618424501.html` | — | через Exa |

### Дословно — экономика на момент закрытия (Josh Pigford, август 2025)

> **We’re about 6,000 paying customers short of breaking even, with only around 200 paying
> customers currently**, most of whom joined during the beta phases when the cost was
> significantly lower. We likely need **more than 6,000** when you consider that many resources
> will need to scale up.

> The reality is that building a B2C personal finance platform is not only **technically very
> challenging, but incredibly slow to grow**, and we can’t tackle those challenges while creating
> additional features people might be willing to pay for within the next **9 months (our current
> runway)**.

> 🔴 **I no longer believe a B2C personal finance app is our best bet for survival. The market’s
> needs are too fragmented, and the feature set is too far from becoming valuable for more
> affluent customers. I believe it either has to be completely bootstrapped for years or have
> $10’s of millions in funding to sustain and pour into growth.**

> We sunset the current version of Maybe. **Again.** No more giant B2C personal finance app.
> **The economics just don’t make sense for us.**

### Дословно — первая смерть (2023), тред основателя и разбор Failory

> we raised **$1.45m** in … pre-seed round from over **1,300 investors** at a **$10m cap**.
> [reg CF / Republic]

> We spent the better part of **$1,000,000** building the app (employees + contractors, data
> providers/services, infrastructure, etc.). [README архива]

> it took us **18 months** to really have a product that just worked™, and in that time, the
> market changed substantially.

> When they launched, despite having a **waiting list of 10,000+ people, only 50 became paying
> customers** (with an average subscription price of **$15/mo**). [Failory, по данным основателя]

> by the time we decided to shut it down we had **a couple thousand dollars in monthly recurring
> revenue**, but with our **team of 8**, that wasn’t going to cut it.

> we got too hung up on **data-source quirks**, basically spending all of our time trying to solve
> for an **infinite number of edge cases that didn't affect the majority of users**. a tall ask
> with only **2 backend engineers**.

> that choice … meant that we’ve got an **infinite number of regulatory things to comply with** …
> it meant that we could only be **in the US** … we have to keep an unchangeable copy of every
> single interaction for like **seven years** … [о встроенном в подписку финсоветнике-CFP]

### 🔴 Дословно — инженерный разбор «The losses» (релиз v0.6.0)

> **The single biggest challenge with a personal finance app in 2025 is bank providers.** …
> the state of “Open Banking” and bank provider data comes with **endless frustration**. …
> - **Unsupported banks** (there are a TON, and **most users churn if even *one* of their banks
>   is unsupported**)
> - Banks that only support logins at certain times of day
> - Bank provider **documentation not matching the production data** we received
> - Bank provider data being **plain wrong** (there is a surprisingly large amount of this)
> - Idiosyncracies of each financial institution (everyone reports their data a little differently)
>
> … this is a **massive** challenge for anyone building a personal finance app and is **the
> primary reason why “bootstrapping” a personal finance app with automated bank syncing is an
> uphill battle. You need a lot of money and time to get this right.**

> While a dashboard with a net worth graph doesn’t look all that complicated, it’s one of those
> **“iceberg” problems**. … **Every view of the app touches nearly *all* the user’s data. If
> *any* piece of data is *wrong*, every view in the app is wrong. There is nowhere to hide in
> a personal finance app** … even the slightest change to the *date* of a historical transaction
> propagates upstream and affects the net worth graph, account sidebar trends, metrics, budgets …

> Achieving full accuracy can be done by writing “facts” to the database (**event-sourcing**) and
> *deriving* results through queries and materialized views. … Unfortunately, taking this
> approach with no answer for the performance side of things will result in an app that is
> **100% accurate and takes 3 minutes to load each page.**

> we opted for a **“hybrid event-sourced” approach**. We wrote “facts” (i.e. transactions,
> trades, valuations) to the database, “synced” them in background jobs, and wrote them to
> **“cache tables”** (i.e. `balances`, `holdings`). This made the *query side* of things a lot
> simpler … but at the **cost of data consistency**.

> **OSS, financial privacy, and project management.** … many users are **not comfortable sharing
> their personal financial situation**. … We are open source, but in order to fix data bugs,
> **we need to look at the data**. If the user can’t share all the required information, we can’t
> reproduce the issue. **I’m not sure there’s a great solution to this.**

> [Multi-currency] There are ~180 currencies globally … ~46k global exchanges … ~55k publicly
> traded companies … 120k+ mutual funds, ~10k ETFs … market data is **extremely expensive**.

### Дословно — исход версии 2 (open source), Зак Голлвитцер

> we got **2M+ package downloads**, amassed **50k+ stars on Github**, and launched a commercial
> hosted offering. **Fortunately for the OSS community, but unfortunately for our business, the
> self-hosted app became wildly popular, but the hosted offering failed to generate the revenue
> growth we needed.**

### Выжимка — что это меняет для FINPILOT (по пунктам, прямо)

1. 🔴 **Самая тяжёлая цифра батча: 10 000+ в листе ожидания → 50 платящих.** Конверсия
   интереса в оплату у полноценного, красиво сделанного B2C-продукта личных финансов —
   **0,5 %**. И во второй заход, уже с 50k звёзд на GitHub и 2 млн скачиваний пакета, —
   **~200 платящих при точке безубыточности ~6 200**. Это надо держать перед глазами при
   любом планировании воронки.
2. 🔴 **Приговор автоимпорту из банков, вынесенный людьми, которые в него вложили $1 млн:**
   «most users churn if even one of their banks is unsupported» и «это главная причина, почему
   бутстрапить такое приложение — бой в гору». Для нас, в РФ, где Open API отложен, а живой
   канал — это SMS/email/файл (тема Г19), вывод обратный привычному: **отсутствие автоимпорта
   — не только наша слабость, но и снятый с нас главный источник оттока и затрат**, при условии,
   что импорт выписки работает хорошо. Это прямо связывает тему Г20 (точность парсера
   PDF-выписок) с выживанием продукта.
3. 🔴 **«There is nowhere to hide in a personal finance app»** — архитектурное предупреждение,
   применимое к нашему ядру буквально. Одна неверная дата операции ломает **все** представления
   сразу. Их решение — гибридный event-sourcing с кэш-таблицами, и они честно называют цену:
   потеря согласованности данных. Для нашей вехи 6 это готовый класс тестов: проверять не
   отдельный расчёт, а **сквозную согласованность всех представлений после изменения одной
   исторической записи**.
4. **Регуляторный урок, совпадающий с нашим выбором.** Встроенный в подписку живой
   советник-CFP заставил их регистрироваться у SEC, хранить неизменяемую копию каждого
   взаимодействия **семь лет** и запер их в одной стране. Мы человека-советника не встраиваем —
   и теперь есть первичный пример цены обратного решения.
5. **Вывод основателя о рынке — тот, который надо оспорить или принять сознательно:**
   «либо полностью на свои годы, либо десятки миллионов долларов». 🔴 **Первый вариант —
   ровно наша конфигурация** (соло, без наёмных, без инвесторов, без burn). У Maybe команда
   из 8 человек с $1,45 млн сгорела за 18 месяцев до релиза; у нас структура затрат другая
   на порядок, и это единственное, что делает их вывод неприменимым к нам напрямую.
6. **И отдельно — предупреждение про open source в этом жанре:** популярность
   self-hosted версии **не конвертировалась в выручку** хостинга. Если когда-либо возникнет
   мысль открыть код FINPILOT ради роста — вот первичный контрпример.

---

## Г18.15 — Группа Е (остальное): Ozon Банк, `urov_14g`, ФССП, G2/Capterra [исходные темы: banks_russia_pfm_advice_2026-09-08, debt_data_sources_rf_2026-09-10, desktop_web_catalogs_sweep_2026-09-12 / Г5, Г14]

### Е.1. 🟢 Ozon Банк — ДОБЫТ. Антибот пробит текстовым прокси

Прежняя причина закрытия: «антибот, канал проверен несколько раз». **Текстовый прокси
`r.jina.ai` по этому пункту не пробовался — и он проходит.**

`curl -s "https://r.jina.ai/https://finance.ozon.ru/"` → **HTTP 200, 16 270 байт** чистого
текста (16.09.2026).

**Дословно:**

> **50 000 000 клиентов** уже получают выгоду с Ozon Картой

> Ozon Банк — полноценный банк с продуктами для физических и юридических лиц. **Уже 50 млн
> клиентов** пользуется нашими картами и счетами для оплаты за пределами маркетплейса и внутри
> Ozon. У Ozon Банка есть **лицензия ЦБ — № 3542 от 12 апреля 2023 года**. … участвует
> в государственной программе страхования вкладов … гарантирует возврат в пределах **1,4 млн ₽**.

> **С Анонимным счётом можно:** Хранить до **15 000 ₽**; Тратить до **40 000 ₽ в месяц**.
> … С Анонимным счётом совершить перевод не получится.

> Да, **в 2025 году первые банкоматы появились в Москве, Санкт-Петербурге и Екатеринбурге.**
> Теперь у Ozon Банка есть собственная сеть банкоматов.

> Для клиентов **Ultra** лимиты расширенные: **до 5 млн рублей без комиссии**.

Функций PFM/советника на лендинге нет — есть кешбэк, лимиты, пополнения, банкоматы.
То есть по нашему исходному вопросу («есть ли у Ozon Банка советующий слой») ответ
**отрицательный и теперь проверенный**, а не «не смогли открыть».

### Е.2. 🟢 Росстат `urov_14g` — ДОБЫТ. 404 был из-за имени файла, а не из-за отсутствия

Прежняя причина: «`urov_14g` — 404». 🔴 **Файл существует**, просто лежит под версионным
именем. Метод: взять листинг раздела и выбрать ссылку оттуда, а не конструировать URL.

| Шаг | URL | HTTP | Размер |
|---|---|---|---|
| прямое имя (как раньше) | `https://rosstat.gov.ru/storage/mediabank/urov_14g.xlsx` и `.xls` | **404** | 680 586 байт HTML-заглушки |
| листинг раздела | `https://rosstat.gov.ru/folder/13397` | **200** | **899 396 байт**; в нём 22 ссылки `urov_*` |
| 🟢 реальный файл | `https://rosstat.gov.ru/storage/mediabank/urov_14g(1)_349665.xls` | **200** | **32 256 байт**, `application/vnd.ms-excel` |

Разобран через `xlrd` в изолированном venv (в системном Python `xlrd` нет; `pip install`
блокируется PEP 668 — ставилось в `venv`).

**Дословно из файла:** лист «Лист1», заголовок «**Структура использования денежных доходов
(динамика)**», отметка «**Обновлено 26.06.2019**». Ряд: **1970 … 2018** (подтверждается прежний
вывод, что ряд обрывается на 2018 — но теперь по самому файлу, а не по косвенным признакам).

**Хвост ряда, % от всех денежных доходов:**

| Статья | 2013 | 2014 | 2015 | 2016 | 2017 | **2018** |
|---|---|---|---|---|---|---|
| Покупка товаров и оплата услуг | 73,6 | 75,3 | 71,0 | 73,1 | 75,8 | **77,0** |
| **Обязательные платежи и разнообразные взносы** | 11,7 | 11,8 | 10,9 | 11,2 | 11,1 | **12,2** |
| **Сбережения** | 9,8 | 6,9 | 14,3 | 11,1 | 8,1 | **5,6** |
| Покупка валюты | 4,2 | 5,8 | 4,2 | 4,0 | 3,7 | **3,7** |
| Прирост (уменьшение) денег на руках | 0,7 | 0,2 | −0,4 | 0,6 | 1,3 | **1,5** |

Для контекста, начало ряда: 1970 — покупка товаров 86,2 %, обязательные платежи 10,0 %,
сбережения 4,0 %; 1998 — 77,7 / 6,1 / 2,5; 2010 — 69,6 / 9,7 / 14,8.

**Новая методология (ряд после 2018) в этом заходе НЕ добыта:** в том же листинге лежит
`urov_2010-2024.xlsx` (**HTTP 200, 7 693 907 байт**), но это **другой показатель** —
«Объем социальных выплат населению и налогооблагаемых денежных доходов населения
**по муниципальным, городским округам и муниципальным районам**», помесячно по ОКТМО,
2010–2024. Полезно само по себе (муниципальный разрез доходов), но структуру использования
доходов не заменяет.

### Е.3. ФССП — не добыто, причина уточнена

`https://fssp.gov.ru/statistics/` → **HTTP 200, но всего 2 022 байта** — это пустая оболочка
SPA (`<div id=app>` + бандл), данные подгружаются скриптом. Прежний диагноз «SPA, 503»
уточняется: сейчас не 503, а **200 с пустым каркасом**. Нужен либо API самого SPA, либо
Wayback — а Wayback сегодня офлайн (см. Г18.0). Отложено.

### Е.4. G2 / Capterra / GetApp / Lunch Money / Empower — подтверждённо закрыто

`curl -s "https://r.jina.ai/https://www.g2.com/categories/personal-finance"` → **HTTP 200,
196 байт**, и в теле дословно:

> Warning: This page maybe requiring CAPTCHA, please make sure you are authorized to access
> this page.

То есть текстовый прокси, который спас MDPI и Ozon Банк, **против G2 не работает**: там
не антибот-страница, а капча. Канал исчерпан; для сравнительных каталогов нужен другой
источник (напр., открытые чарты сторов или собственный сбор).

---

# ИТОГ Г18

## 🔴 Главное число батча

**Разобрано 24 пункта класса 1 («закрыто насовсем»).**
**15 переведены в «добыто»** · **4 — «частично»** · **5 — остались недобытыми**.

То есть **вердикт «повторять бессмысленно» оказался неверным для 5 пунктов из 8**
(если считать по долям: 62,5 % пунктов класса 1 поддались новым каналам целиком, ещё 17 %
частично). Решение владельца 12.09.2026 «конечно тоже добываем» подтвердилось результатом.

## Таблица: пункт → канал → результат

| # | Пункт | Канал, которым взят (или последний испробованный) | Результат | HTTP / размер | Что меняет для проекта |
|---|---|---|---|---|---|
| 1 | Chen et al., ACM CSUR 51(1), метаморфическое тестирование | курсовая копия UW + репозиторий Victoria Univ. | 🟢 **добыто** | 200 / 351 596 б PDF | метод применим к нашей оракульной проблеме; обзор сам предупреждает, что эффективность набора MR не доказана |
| 2 | Felfernig, IUI '08 | авторская страница TU Graz → журнальное продолжение (AI Communications 26(1)) | 🟡 частично | 200 / 649 094 б | эталон трудозатрат на калибровку весов: 15 циклов × 12 ч = 180 ч; наши 5 раундов — мало, а не много |
| 3 | Brown & Lahey, JMR 2015 | NBER WP **под другим названием** (w20125) | 🟢 **добыто** | 200 / 769 726 б | snowball проигрывает avalanche при разрыве ставок > ~6–7 п.п. — подпора под канон v3.0.0 из работы «за snowball» |
| 4 | Madrian & Shea «1999» | NBER w7682 (на самом деле **май 2000**) | 🟢 **добыто** | 200 / 479 053 б | 37 % → 86 % от смены умолчания; и предупреждение: умолчание читается как совет компании |
| 5 | Hogarth & Karelaia 2007 (журнальная) | рабочая версия UPF WP #974 под другим названием | 🟢 **добыто** | 200 / 430 728 б, 66 стр. | в компенсаторных средах равные веса бьют и эвристики, и среднего человека — проверяемый тест на переусложнение весов |
| 6 | Giacomini & Rossi, JAE | **Exa** → рабочая версия на сайте Нацбанка Венгрии | 🟢 **добыто** | 200 / 258 515 б | флуктуационный тест + **таблица критических значений** для сравнения нашего прогноза с наивным |
| 7 | Fox 1966 | RAND P-3288-1 (карточка), DTIC AD0626604/AD0632054 | 🔴 не добыто | RAND 200/26 380 б — файла нет; DTIC **200/1 408 б «Under Maintenance»** | реквизиты исправлены (Management Science 13(3):210–216), роль работы установлена по тексту 1986 г. |
| 8 | Federgruen & Groenevelt 1986 | страница публикаций автора на `business.columbia.edu` | 🟢 **добыто** | 200 / 438 418 б PDF | необходимое и достаточное условие оптимальности жадного распределения — полиматроид; граница применимости нашего Avalanche названа |
| 9 | Feinstein & Cicchetti 1990 (I и II) | Europe PMC REST (дословные авторские абстракты) | 🟡 частично | 200 / 3 261 и 3 478 б | правило отчётности: к каппе всегда добавлять p_pos и p_neg; κ_max проблему не чинит |
| 10 | Hagger et al. 2010 | Europe PMC REST; OpenAlex-ссылка на HKU Hub мертва | 🟡 частично | 200 / 5 110 б; hdl **500**, через `r.jina.ai` — «handle cannot be found» | ego depletion цитировать как «заявлено мета-анализом, оспорено репликацией» |
| 11 | Zhou & Mamon 2012 | Exa (искалась диссертационная глава) | 🔴 не добыто | Elsevier пейволл; открытых копий нет | потеря малая: regime-switching вне канона v3.0.0 |
| 12 | Закупки госбанков на PFM (223-ФЗ) | 🆕 `zakupki.gov.ru` через `curl -sk --http1.1` | 🟢 **добыто (отрицательный результат, доказанный)** | 200 / 247 130 б; 16+33+15+7 записей по 4 профильным запросам | таких закупок в ЕИС нет вовсе; чек B2B через реестры не восстанавливается — и это теперь метод, а не предположение |
| 13 | Выручка вендоров (ЦФТ, BSS, Диасофт) | раскрытие эмитента ПАО «Диасофт» | 🟡 частично | 200 / 54 652 и 54 863 б | лидер рынка: **9,8 млрд ₽, −3 % г/г, EBITDA −35 %**, причина — «экономия ИТ-бюджетов заказчиков»; довод против B2B как первого канала |
| 14 | CPA банков и брокеров РФ | 🆕 публичный каталог **LEADS.SU** | 🟢 **добыто** | 200 / 252 323 б | ставки 95–13 770 ₽, но **AR 0,97–4,57 %** у банков; лучшие EPC — у МФО, куда нам нельзя по конфликту интересов |
| 15 | Практика по 211-ФЗ | `kad.arbitr.ru` (POST к API) | 🔴 не добыто | **451 «Доступ заблокирован»** / 1 715 б | внешнее правовое ограничение доступа, не отсутствие материала |
| 16 | Решения ЦБ по операторам финплатформ | 🆕 XLSX реестра + надзорный обзор ЦБ | 🟢 **добыто** | 200 / 19 596 б (реестр на 15.09.2026) и 200 / 974 342 б (19 стр.) | 13 действующих + 3 исключённых; **8,43 млн зарегистрированных против 0,39 млн активных (4,6 %)** |
| 17 | Письма ФНС: цифровая валюта | внешний поиск номера → подтверждение на `nalog.gov.ru/rnXX/...` | 🟢 **добыто** | 200 / 72 242 б | **НПД, ПСН, АУСН, УСН по операциям с цифровой валютой применять нельзя** — прямое ограничение монетизации |
| 18 | Письма ФНС: Telegram Stars, внутриигровая валюта | целевой поиск | 🟡 «разъяснения нет» (отрицательный результат) | собственный поиск `nalog.gov.ru` без JS результатов не отдаёт | Stars — серая зона без позиции регулятора; не делать основным каналом оплаты |
| 19 | Разбивка категории Finance у RevenueCat | отчёт State of Subscription Apps 2026 | 🟢 **закрыто с доказанной причиной** | 200 / 1 782 371 б | **категории Finance у них нет** — Finance вшита в «Utilities»; прокси-числа и бенчмарки сняты |
| 20 | Разбор закрытия Maybe Finance | 🆕 релиз GitHub v0.6.0 + тред основателя + пост ведущего разработчика | 🟢 **добыто** (прежний вердикт «основатель не опубликовал» опровергнут) | 200 / 239 668 б, 346 588 б, 23 851 б | 10 000 в листе ожидания → **50 платящих**; 200 платящих против точки безубыточности ~6 200; приговор автоимпорту из банков |
| 21 | Ozon Банк (ранее антибот) | 🆕 текстовый прокси `r.jina.ai` | 🟢 **добыто** | 200 / 16 270 б | 50 млн клиентов, лицензия № 3542 от 12.04.2023; **советующего слоя нет** — проверено, а не предположено |
| 22 | Росстат `urov_14g` (ранее 404) | 🆕 листинг раздела `folder/13397` → версионное имя файла | 🟢 **добыто** | 404 на прямом имени → **200 / 32 256 б** на реальном | структура использования доходов 1970–2018; 2018: товары 77,0 %, обязательные платежи 12,2 %, сбережения **5,6 %** |
| 23 | Первичка ФССП | `fssp.gov.ru/statistics/` | 🔴 не добыто | **200, но 2 022 б** — пустой каркас SPA | диагноз уточнён: не 503, а SPA без данных в HTML |
| 24 | G2 / Capterra / GetApp / Lunch Money / Empower | `r.jina.ai` поверх G2 | 🔴 не добыто | 200 / **196 б**: «This page maybe requiring CAPTCHA» | капча, а не антибот — прокси не помогает, канал исчерпан |

## Внешние ограничения, действовавшие в день батча (не наши, переспросить позже)

| Инструмент | Что вернул | Следствие |
|---|---|---|
| **Internet Archive / Wayback / CDX** | 429 на первом же запросе + страница «**Temporarily Offline**» | канал «Wayback по старым адресам», предписанный Г18, **был недоступен физически**; пункты 23 и часть 7 упёрлись именно в это |
| **DTIC** (`apps.dtic.mil`) | 200 / 1 408 б, «**Our Site is Getting an Upgrade**» | закрыл единственный открытый путь к Fox 1966 |
| **Semantic Scholar API** | **429 Too Many Requests** (без ключа) | пришлось идти через OpenAlex и Exa |
| **kad.arbitr.ru** | **451** | практика по 211-ФЗ недостижима из этой среды |

## Приёмы, которые окупились и стоят переноса в общий канон добычи

1. 🔴 **`curl -sk --http1.1` открывает весь российский госсегмент** (`zakupki.gov.ru`,
   `cbr.ru`, `nalog.gov.ru`, `rosstat.gov.ru`, `leads.su`, `diasoft.ru`) — при этом
   российский корневой сертификат **не устанавливается**, запрет владельца соблюдён.
2. 🔴 **«404 на файле» ≠ «файла нет».** Росстат хранит файлы под версионными именами
   (`urov_14g(1)_349665.xls`). Правило: сначала листинг раздела, потом ссылка из него,
   никогда — сконструированный URL.
3. 🔴 **Фильтры в URL могут обнулить выдачу.** `af=on` в поиске ЕИС давал 0 записей там,
   где без него — 16. Пустая выдача — повод проверить параметры, а не делать вывод.
4. 🔴 **«Рабочая версия под другим названием» — самый результативный канал батча.**
   Так взяты 4 из 6 закрытых статей: Brown & Lahey («Savings and Debt Reduction» вместо
   «Task Completion and Debt Repayment»), Hogarth & Karelaia («Mapping the demand for
   knowledge» вместо «Matching rules and environments»), Giacomini & Rossi («Model Selection
   and Forecast Comparison» вместо «Forecast comparisons»), Felfernig (журнальное продолжение
   вместо конференционной статьи).
5. **Рабочая версия может лежать у третьей стороны**: Giacomini & Rossi — на сайте
   **Венгерского нацбанка**; Chen et al. — на **курсовой странице Вашингтонского
   университета**. Искать надо не только у автора и издателя.
6. **Пост-мортемы продуктов живут в релизах GitHub и тредах основателей**, а не на сайте
   продукта — Maybe Finance был «не опубликован» ровно по этой причине.
7. **`r.jina.ai` лечит антибот, но не капчу**: Ozon Банк — взят, G2 — нет. Разница видна
   по телу ответа (196 байт с явным словом CAPTCHA).
8. **Europe PMC REST (`resultType=core`)** даёт дословный авторский абстракт и точную
   пагинацию по закрытым статьям — это не полный текст, но и не пересказ.
9. **Системный Python блокирует `pip install` (PEP 668)** — для `xlrd`/`openpyxl` заводится
   `venv` в скрэтчпаде.

## Что осталось неизвестным (честно, без домысла)

- **Fox 1966** полным текстом — RAND скан не выкладывает и прямо запрещает размещение,
  DTIC на техобслуживании. Переспросить DTIC позже.
- **Zhou & Mamon 2012** — открытых копий нет ни в одном репозитории.
- **IUI '08 Felfernig** — у авторской группы нет собственной копии.
- **Практика по 211-ФЗ** — `kad.arbitr.ru` отдаёт 451; не пробованы `sudact.ru`,
  `ras.arbitr.ru`, раздел «Решения Банка России».
- **Первичка ФССП** — нужен API самого SPA или Wayback (сегодня офлайн).
- **Выручка ЦФТ и BSS** — непубличные; следующий конкретный ход — ГИР БО (`bo.nalog.ru`),
  в этом заходе не пробовался.
- **Закупки конкретных банков в ЕИС** — прогон по ИНН через строку поиска неинформативен,
  нужен фильтр `customerIdOrg` по справочнику организаций.
- **Новая методология Росстата после 2018** по структуре использования доходов —
  `urov_2010-2024.xlsx` оказался другим показателем (муниципальный разрез).
- **Каталоги G2/Capterra/GetApp** — капча; нужен принципиально другой источник.


---

## ДОБОР Г31.1 — Wayback (16.09.2026)

**Состояние каналов на начало работы (замер 16.09.2026 19:32–20:25 UTC; системная дата среды — 16.09):**
`archive.org/wayback/available` — **429** с редкими окнами 200; `cdx/search/cdx` — **503**
«Temporarily Offline» почти постоянно; 🟢 **replay `web.archive.org/web/<ts>[id_]/<URL>` — 200**
при паузе ≥ 20 с между запросами; `timetravel.mementoweb.org` — 000; `archive.ph` — 200 → 429;
Common Crawl `collinfo.json` — 200, запросный шлюз — **504**;
🔴 **DTIC (`apps.dtic.mil`) — 200, но 1 408 байт «Our Site is Getting an Upgrade / We'll be back
shortly»: техобслуживание второй день подряд.**

🔴 **Поправка к пробе доступности архива.** «Wayback лежит» 16.09 означало «лежат
`wayback/available` и CDX»; replay при этом работал. Служебные API Internet Archive и отдача
снимков — разные подсистемы и падают порознь.

### Г31.1-Л1. 🟢 Fox 1966 ДОБЫТ ПОЛНЫМ ТЕКСТОМ — через снимок DTIC, пока сам DTIC на обслуживании

Закрывает §Г18.7 «**Fox 1966 — НЕ ДОБЫТО**» и одноимённый пункт класса 4 аудитов № 3 и № 4
(«DTIC на техобслуживании — единственный путь; RAND 404; INFORMS пейволл»).

**Приём:** сам DTIC лежит, но его PDF есть в архиве, и суффикс `id_` отдаёт оригинальный файл.
- `https://web.archive.org/web/2020id_/https://apps.dtic.mil/sti/tr/pdf/AD0626604.pdf`
  → **HTTP 200, 514 455 байт, валидный PDF 1.4, 16 страниц** (разобран `pdftotext`).
- Контрольная проба по RAND:
  `https://web.archive.org/web/2015id_/http://www.rand.org/content/dam/rand/pubs/papers/2008/P3288-1.pdf`
  → **404** (4 688 б HTML). То есть PDF на RAND не выкладывался никогда, и прежний вывод
  «скана нет» по RAND верен — работа добыта именно из депонированной копии DTIC.

**Титул и реквизиты дословно (скан низкого качества, OCR местами рваный; приводится как есть):**

> **DISCRETE OPTIMIZATION VIA MARGINAL ANALYSIS**
> **Bennett Fox**
> **The RAND Corporation, Santa Monica, California**
> January 1966
>
> Any views expressed in this paper are those of the author. They should not be interpreted as
> reflecting the views of The RAND Corporation or the official opinion or policy of any of its
> governmental or private research sponsors. Papers are reproduced by The RAND Corporation as
> a courtesy to members of its staff.
> **This paper was prepared for submission to Management Science.**

🟢 **Реквизиты подтверждены первоисточником**: это препринт **RAND P-3288-1**, январь 1966,
депонирован как **AD0626604**, подготовлен к подаче в *Management Science* — что сходится
с журнальной публикацией **Management Science 13(3):210–216, ноябрь 1966, DOI
10.1287/mnsc.13.3.210**. Исправление реквизитов, сделанное в §Г18.7 (склейка с Federgruen &
Groenevelt, *Operations Research* 34(6):909–918, 1986), **подтверждено окончательно**.

**Реферат дословно:**

> ABSTRACT. Discrete optimization subject to one constraint is attacked by Lagrangian analysis.
> Incremental allocation schemes are given that generate undominated allocations. In an important
> special case, the complete family of undominated allocations is generated.

**Введение дословно:**

> 1. Introduction. In allocation problems, a marginal analysis of incremental return per
> additional dollar spent is intuitively appealing. We give conditions under which it is
> justified and applications. **In some circles, some of our results are probably part of
> the folklore.**

**Постановка задачи (раздел 2):**

> max [φ(x) : x ∈ S, C(x) ≤ M]
>
> где S — множество n-наборов неотрицательных целых чисел (x₁, …, xₙ),
> C(x) = Σⱼ cⱼxⱼ ≤ M, **cⱼ > 0**, j = 1, …, n, и φ(x) = Σⱼ φⱼ(xⱼ) (сепарабельная цель).

**Процедура (раздел 3) — это ровно наш жадный шаг, дословно:**

> 1. Start with the allocation x⁰ = 0. 2. k = 1.
> 3. xᵏ = xᵏ⁻¹ + eᵢ, where eᵢ is the i-th unit vector and i is any index for which
>    **[φᵢ(xᵢᵏ⁻¹ + 1) − φᵢ(xᵢᵏ⁻¹)] / cᵢ is maximum.**
> 4. If C(xᵏ) > M, terminate; otherwise k → k+1 and go to step 3.

> **4. Variant 1.** A slight variant of the foregoing procedure is to terminate when the
> objective function first exceeds a preassigned value instead of when the cost exceeds
> a preassigned value.
> **5. Variant 2.** A second variant is to branch at step 3 whenever ties occur for the
> maximizing index. Let Iᵏ be the set of maximizers. The procedure is successively initiated
> with the allocations xᵏ⁻¹ + eᵢ, i ∈ Iᵏ.

**Определение недоминируемости (раздел 6):**

> Allocations x satisfying φ(y) > φ(x) ⟹ C(y) > C(x) [и] φ(y) = φ(x) ⟹ C(y) ≥ C(x)
> for all y are called **undominated**.

**Ключевое определение и теоремы (дословно, с поправкой рваного OCR):**

> In what follows, **a function defined only on the integers is called concave if its first
> differences are decreasing.**
>
> **Lemma 1.** If λ ≥ 0 and x ∈ S maximizes the Lagrangian φ(x) − λC(x) over all x ∈ S,
> then x is undominated.
>
> **Theorem 1.** For any λ ≥ 0, if φᵢ(y) is concave, i = 1, …, n, [then x(λ)] is undominated.
> *Proof.* Apply Lemma 1.
>
> 🔴 **Theorem 2.** **If φᵢ(y) is concave and strictly increasing, i = 1, …, n, the allocations
> generated by the incremental allocation procedure are undominated.**

Дополнительно: «If φᵢ(y) is strictly concave, [максимизатор] exists for all λ > 0»; «If φᵢ(y)
is differentiable, Tᵢ(λ) can be found by evaluating φᵢ(y) − λyсᵢ at the nonnegative integers
neighboring the roots … if φᵢ(y) is strictly concave, there is a unique root».

### Что добытый текст меняет и что подтверждает

1. 🟢 **Косвенный вывод §Г18.7, снятый с текста Federgruen & Groenevelt 1986, подтверждён
   первоисточником и уточнён.** Fox 1966 действительно про **одно** бюджетное ограничение
   и **сепарабельную** цель — ровно та конфигурация, что у нас (свободный денежный поток как
   единственный бюджет, вклад каждого направления считается отдельно). Формулировка «уточнение,
   а не первое доказательство» подтверждается и самим Фоксом, причём в неожиданно прямой форме:
   *«In some circles, some of our results are probably part of the folklore»*.
2. 🔴 **Главное для FINPILOT — точное условие применимости жадного шага, теперь из первых рук.**
   Теорема 2 требует, чтобы каждая φᵢ была **вогнутой и строго возрастающей**, где вогнутость
   на целых определена как **убывание первых разностей**. Это проверяемое условие, а не
   абстракция: для нашего Avalanche-фильтра оно означает, что **предельная польза каждого
   следующего рубля, направленного в одно и то же направление, не должна расти**. Для погашения
   долга по ставке это выполняется тривиально (экономия процентов линейна, первые разности
   постоянны — вогнутость нестрогая, что теореме 1 достаточно). 🔴 **Где ломается:** любое
   направление с порогом или скачком полезности (накопление до порога, после которого приз;
   ступенчатые условия вклада; «резерв считается собранным при 3 окладах») даёт **возрастающую**
   первую разность на участке — φᵢ невогнута, и Теорема 2 неприменима, жадный шаг может дать
   доминируемое распределение. Это тот самый крайний случай, который стоит проверять на данных.
3. **Критерий шага — отношение приращения к цене** ([φᵢ(xᵢ+1) − φᵢ(xᵢ)] / cᵢ), а не голое
   приращение. У нас cᵢ равны (рубль стоит рубль), поэтому деление вырождается — но это
   вырожденный случай общей формулы, и если когда-либо появится направление с транзакционной
   ценой шага (комиссия за досрочное погашение, минимальный взнос), знаменатель обязан вернуться.
4. **Variant 2 (ветвление при ничьих)** — готовый ответ на вопрос, что делать при равных
   оценках у нескольких альтернатив: не выбирать произвольно, а порождать семейство. При 66
   альтернативах с шагом 10 % ничьи вероятны, и произвольный выбор первого максимума теряет
   часть недоминируемого фронта.
5. **Variant 1** — «останавливаться, когда цель впервые превысит заданное значение, а не когда
   стоимость превысит бюджет» — это в точности постановка «сколько нужно вложить, чтобы достичь
   цели» в противовес «как лучше разложить имеющееся». Обе наши постановки, оказывается, описаны
   в одной работе 1966 года как процедура и её вариант.

🔴 **Канон модели, формулировку новизны и код по этой находке НЕ правлю** — это материал
к синтезу. Но отмечаю прямо: **новизна по методу жадного маржинального распределения
не защитима** — процедура опубликована Фоксом в 1966 году в том же виде, вплоть до критерия
отношения приращения к цене; зазор продукта остаётся по объекту и обвязке, а не по алгоритму.
Это согласуется с итогом тем 16–17, где новизна по методу уже была опровергнута.

## ИТОГ Г31.1 (в этом файле)

| Пункт | Класс | Результат |
|---|---|---|
| Fox 1966 полным текстом | 4 | 🟢 **ЗАКРЫТ** — PDF 16 с. из архивной копии DTIC (`/web/2020id_/…AD0626604.pdf`, 200 / 514 455 б), при том что сам DTIC на техобслуживании второй день |
| RAND P-3288-1 как PDF | — | ❌ подтверждено, что файла не было: архивный `…/P3288-1.pdf` → 404. Прежний вывод «скана на RAND нет» верен |

- Закрыто снимками: **1 из 1**. Реквизиты (RAND P-3288-1, январь 1966, AD0626604,
  подготовлено к подаче в *Management Science*) подтверждены первоисточником; исправление
  склейки с Federgruen & Groenevelt 1986 подтверждено окончательно.
- 🔴 **Меняет выводы:** условие оптимальности жадного шага теперь известно из первых рук
  (Теорема 2: каждая φᵢ вогнута и строго возрастает, вогнутость = убывание первых разностей),
  вместе с точкой поломки — направления с порогом/скачком полезности. И отдельно: **новизна
  по методу маржинального жадного распределения не защитима** — процедура, включая критерий
  «приращение, делённое на цену шага», опубликована Фоксом в 1966 году. Канон, формулировку
  новизны и код по этой находке не правил.

---

## ДОБОР Г31.4 — Semantic Scholar и долги Г31.2 (16.09.2026)

**Каналы на начало работы (замер 16.09.2026, коды дословно):** Unpaywall **200** ·
Crossref **200** · OpenAlex **200** · EuropePMC **200** · `r.jina.ai` **200** (без браузерного
UA) · Wayback replay **200** · `curl`/`pdftotext` в системе; 🔴 **`tesseract` есть, но БЕЗ
русского словаря** (`--list-langs` → `eng`, `osd`, `snum`).
🔴 **Semantic Scholar расщеплён по эндпоинтам:** `/graph/v1/paper/search` — **429 на 4 из 4
попыток** (174 б, паузы 6–8 с); `/paper/search/bulk` — **200**; `/paper/DOI:<doi>` — **200
на 3 из 3**; `/paper/DOI:<doi>/citations` — **200**.

Этот файл целиком посвящён пунктам «закрыто навсегда», поэтому здесь важен не объём добытого,
а **чем именно S2 оказался полезен и где бесполезен**. Ниже — оба исхода честно.

### Г31.4-C1. Fox 1966 — реквизиты подтверждены ТРЕТЬИМ источником, полный текст закрыт

S2 `/paper/search/bulk?query="Discrete optimization via marginal analysis"` —
**HTTP 200, 800 б, `total: 2`**. Первая запись:

> `"title": "Discrete Optimization Via Marginal Analysis"`, `"year": 1966`,
> `"authors": [{"name": "B. Fox"}]`, `"externalIds": {"DOI": "10.1287/MNSC.13.3.210", …}`,
> `"openAccessPdf": {"url": "", "status": "CLOSED"}`

🟢 **Исправление реквизитов из Г18.7 подтверждено независимо:** DOI `10.1287/MNSC.13.3.210`
однозначно указывает на *Management Science* **13(3)**, с. **210**, — а не на «Operations
Research 34(6):909–918», как стояло в `COVERAGE_AUDIT_2.md` и `GAP_QUEUE.md` §Г4 п.10.
Теперь у исправления три независимых подтверждения (OpenAlex, RePEc, S2).
🔴 **Полный текст по-прежнему не добыт** и статус «не добыто» не меняется: S2 даёт `CLOSED`,
DTIC на обслуживании (200 / 1 408 б «Our Site is Getting an Upgrade»), у RAND файла нет.
Каналы по этому пункту исчерпаны; роль работы установлена по тексту Federgruen & Groenevelt
1986 и от полного текста не зависит.

### Г31.4-C2. Zhou & Mamon 2012 — S2 НЕ ДАЛ НИЧЕГО, статус не меняется

S2 `/paper/search/bulk` по точному заголовку — **HTTP 200, 978 б, `total: 1`**:
DOI `10.1016/j.eswa.2011.09.053`, 2012, `citationCount: 55`, `openAccessPdf.status: "CLOSED"`,
`abstract: null` («elided by the publisher»), `tldr` отсутствует. (Поиск по авторам+теме
дал `total: 0` — фразовый запрос по заголовку сработал, тематический нет; это свойство
`search/bulk`, полезно знать.)

🔴 **Отрицательный замер по каналу:** по работам Elsevier **S2 не добавляет к OpenAlex ничего**
— издатель изымает абстракт и из S2 тоже. Прежний вердикт («пейволл, `r.jina.ai` — капча
Cloudflare, открытых копий нет») подтверждён четвёртым каналом. Потеря по-прежнему малая:
regime-switching вне канона v3.0.0, а содержательный ответ на вопрос Г6.5 уже получен
через Ang & Timmermann полным текстом.

### Г31.4-C3. 🟢 Hagger et al. 2010 (Г18.8) — пункт ЗАКРЫТ, но не добычей, а тем, что надобность отпала

S2 `/paper/DOI:10.1037/a0019486` — **HTTP 200, 1 181 б**: `citationCount: 2262`,
`openAccessPdf.status: "CLOSED"`, абстракт изъят издателем, **но 🟢 `tldr` отдан** — а у
OpenAlex по этой записи нет и абстракта. Это как раз тот случай, ради которого подбатч
и заводился: **S2 даёт содержание там, где OpenAlex даёт только метаданные.**

Дальше через S2 найдена и добыта **предзарегистрированная репликация тех же авторов**:
Hagger M. S. et al. «A Multilab Preregistered Replication of the Ego-Depletion Effect»,
*Perspectives on Psychological Science*, 2016, DOI `10.1177/1745691616652873` — открытая копия
в репозитории KU Leuven, **HTTP 200, 984 214 б**. Полный разбор и дословные цитаты — в
`behavioral_finance_field_2026-09-10.md`, блок Г31.4-B4.

🔴 **Итог по пункту:** мета-анализ 2010 года так и не добыт полным текстом (APA PsycNet
пейволл, `hdl.handle.net/10722/161366` мёртв — HTTP 500), **и добывать его больше не нужно**:
его главное число (d = 0,62 по 198 тестам) приведено дословно в открытом тексте RRR 2016,
а сам результат опровергнут теми же авторами (d = 0,020 и −0,031, 95 % ДИ включают ноль,
24 лаборатории). Пункт переводится из «закрыт наглухо» в **«закрыт по существу: источник
недоступен, но вопрос решён более поздней открытой работой тех же авторов»** — и это
содержательно другой статус.

### Г31.4-C4. Что по этому файлу НЕ трогалось и почему

Сознательно не брались — не потому, что не добыты, а потому, что **S2 к ним неприменим**
(это не научные публикации): первичка ФССП (SPA без данных в HTML), практика по 211-ФЗ
(`kad.arbitr.ru` — 451, внешнее правовое ограничение), G2/Capterra/GetApp (капча),
IUI '08 и DX'07 (ACM DL / протухшая подпись Academia.edu), ЦФТ и BSS (непубличные компании).
Ни один из них не является пробелом научного канала, и заводить по ним S2-заход было бы
имитацией работы.

## ИТОГ Г31.4

По этому файлу: **1 пункт закрыт по существу, 2 подтверждены закрытыми, 6 сознательно
не брались.**
- **Hagger et al. 2010** — 🟢 переведён из «закрыт наглухо» в **«закрыт по существу»**:
  полный текст так и недоступен, но надобность отпала — его главное число (d = 0,62 по 198
  тестам) приведено дословно в открытом RRR 2016 тех же авторов, где результат ими же
  опровергнут. Цитировать 2010 без 2016 теперь нельзя.
- **Fox 1966** — реквизиты (`10.1287/MNSC.13.3.210`, Management Science 13(3):210) подтверждены
  **третьим независимым источником**; полный текст остаётся закрытым, каналы исчерпаны.
- **Zhou & Mamon 2012** — S2 подтвердил `CLOSED` и пустой абстракт; статус не меняется.
- Не брались: ФССП, `kad.arbitr.ru` (451), G2/Capterra, IUI '08, DX'07, ЦФТ/BSS — **S2 к ним
  неприменим**, это не научные публикации.
🔴 **Отрицательный замер по каналу, важный для решения о ключе:** по закрытым работам Elsevier
**S2 не добавляет к OpenAlex ничего** — издатель изымает абстракт и оттуда тоже (Wang & Luo,
Tunçel & Hammitt, Zhou & Mamon, DeMiguel, Feinstein & Cicchetti — одинаково).
Задолженности нет.

**Сводный итог всего подбатча Г31.4** — в `approach_validity_2026-09-10.md`, блок «ИТОГ Г31.4 (СВОДНЫЙ)».
