# Тема 16 — Constraint-based и utility-based рекомендательные системы (школа Felfernig / Burke, MAUT-ранжирование) и их применение в финансовых консультационных сервисах

**Статус файла:** ЗАКРЫТ по всем семи вопросам. Вопрос 5 закрыт совместно с подагентом,
его полное сырьё — `docs/research/raw/_sub16_utility_based_rs.md` (702 строки, 44 КБ).
Прерывание: 09.09.2026 работа была оборвана лимитом аккаунта на середине; файл уцелел и продолжен.
**Оригинал Felfernig & Burke (ICEC '08) прочитать не удалось — ACM DL отдаёт 403 на оба канала.**
Всё, что о нём в файле, снято с канонических пересказов тех же авторов. См. «Что не добыто».

**Прежний статус:** В РАБОТЕ. Файл создаётся рано и дополняется по ходу добычи (правило §11 CLAUDE.md).
Если работа оборвалась — всё, что ниже строки последнего раздела, не добыто.
**Дата:** 2026-09-09. **Исполнитель:** research lead agent (FINPILOT, очередь тем, тема 16).

## Оговорка о полноте
На момент последнего сохранения файл может быть неполон. Разделы, помеченные `[НЕ ДОБЫТО]`,
не подтверждены первоисточником. Реконструкции по памяти модели вынесены в отдельный
раздел и НИКОГДА не смешиваются с дословными выписками.

---

## Классификация запроса и процесс (прозрачность метода)

**Тип запроса:** depth-first по одной научной школе (Felfernig / Burke, constraint- и
utility-based RS) с breadth-элементом по семи под-вопросам. Основной объём добычи выполнен
самим lead-агентом; потолок подагентов (2) соблюдён, запуск — по одному, не веером.

**Каналы добычи, которые сработали:** `WebFetch` на PDF → файл кладётся на диск → `pdftotext`;
`curl` с браузерным UA + питоновский стриппер тегов для HTML, который `WebFetch` подрезает.
**Каналы, которые не сработали:** ACM DL (`dl.acm.org`) отдаёт HTTP 403 и на `WebFetch`,
и на `curl` с браузерным UA — антибот. Зафиксировано в разделе «Что не добыто».

---

# 2. Финансовые применения школы — FSAdvisor (ГЛАВНАЯ НАХОДКА, ДОБЫТО ДОСЛОВНО)

> Раздел идёт первым в файле не по важности вопроса, а по порядку добычи: это первый
> первоисточник, вскрытый целиком, и именно он содержит формулу, совпадающую с ядром FINPILOT.

**Источник (полный текст извлечён, 558 строк):**
Felfernig, A. (ConfigWorks GmbH / University Klagenfurt) & Kiener, A. (Bausparkasse Wüstenrot AG).
**«Knowledge-based Interactive Selling of Financial Services with FSAdvisor».**
Proceedings of the 17th Innovative Applications of Artificial Intelligence Conference (IAAI-05),
AAAI, 2005, pp. 1475–1482.
URL (открыт, PDF разобран через pdftotext): https://cdn.aaai.org/AAAI/2005/IAAI05-004.pdf

## 2.1. Что за система и что рекомендуется

Дословно, Abstract (с. 1475):

> «In this paper we describe the knowledge-based recommender application FSAdvisor (Financial
> Services Advisor) which assists sales representatives in determining personalized financial
> service portfolios for their customers. Commercially introduced in 2003, FSAdvisor is licensed
> to a number of major financial service providers in Austria. It supports the dialog between
> a sales representative and a customer by guaranteeing the consistency and appropriateness of
> proposed solutions, identifying additional selling opportunities and by providing intelligent
> explanations for solutions. […] In FSAdvisor we integrate model-based diagnosis, constraint
> satisfaction and personalization thus supporting customer-oriented sales dialogs.»

Домен и масштаб знаний, дословно (Task Description, с. 1476):

> «Financial service providers currently applying FSAdvisor dispose of a product assortment of
> about 100 (partly configurable) products which cover different areas of interest (e.g.
> investment decisions, financing, pension, life insurance or business and property insurance).»

> «Financial service advisory is a complex task with a large number of constraints and possible
> solutions. In an integrated recommender application there exist about **1-2 million solution
> alternatives and about 300-400 constraints**.»

🔴 Прямое обоснование ОТКАЗА от ML-подходов в финансовом домене, дословно (с. 1476):

> «A customer's taste is not of primary concern in the financial services domain.
> **Recommendations must be correct and explainable**, i.e. Collaborative Filtering (Herlocker
> et al. 2004) or Content-based Filtering (Burke 2002) approaches are not the best choices.»

> «Intelligent explanation, debugging, and repair mechanisms as well as automated test case
> generation are based on model-based knowledge representations, i.e. deep knowledge about the
> application domain must be available (which is not the case when applying Collaborative
> Filtering or Content-based Filtering approaches).»

## 2.2. Формализация задачи (CSP) — дословно (раздел «Constraint Satisfaction», с. 1479)

> «FSAdvisor is based on constraint satisfaction problem solving (Tsang 1993). A Constraint
> Satisfaction Problem (CSP) (C,V,D) (Tsang 1993) is defined by a set V of variables xi, a set C
> of constraints cj and a set D of domains di which defines for each variable the set of possible
> values. A CSP is solved if there exists a set of instantiations of the variables x1, x2, ..., xn
> s.t. all constraints contained in C are satisfied. **A recommendation task can be defined as a
> CSP (C, VSRS, VPROD, DSRS, DPROD), where V is additionally divided into VSRS (set of variables
> describing customer requirements) and VPROD (set of variables describing product properties).**»

Механика при пустом результате, дословно, там же:

> «The constraint solver tries to find a solution for a given recommendation task. **If no solution
> can be found, constraints with a priority > 0 (0 is the highest priority) are relaxed starting
> with constraints with lowest priority. If nothing but non-relaxable constraints (priority = 0)
> remain, a repair mechanism is activated.**»

Отдельный класс «мягких» правил — `tips` (не отсекают, а подсказывают), дословно (с. 1479–1480):

> «In addition to constraints, FSAdvisor supports **tips**, i.e. constraints representing e.g.
> cross-selling opportunities which are shown to the customer without interrupting the recommender
> process (in contrast to constraints, where an additional constraint violation handling dialog is
> started). If a customer is risk-averse and interested in long-term investments, a tip could be:
> long-term investments reduce risks, i.e. allow higher return rates than short-term investments
> without taking high risks.»

## 2.3. 🔴 ФОРМУЛА РАНЖИРОВАНИЯ — совпадает с SAW-ядром FINPILOT

Дословно, раздел «Personalized Ordering of Solutions» (с. 1480):

> «A solution for a given recommendation task is a set (portfolio) of financial services. The order
> of solutions should strictly correspond to the degree a solution contributes to the wishes of a
> customer. **FSAdvisor supports multi-attribute object rating (Ardissono et al. 2003), where each
> solution is evaluated w.r.t. to a pre-defined set of abstract dimensions. Profit, availability and
> risk are examples for such abstract dimensions. Depending on the weighting of the dimensions for
> a specific customer (e.g. a customer is strongly interested in products with a high return rate)
> the set of solutions is ordered using the formula g(x) = Σ(i=1..n) ei·si(x), where n denotes the
> number of dimensions, g(x) represents the utility of one solution x, ei represents the customer's
> interest in dimension i, and si is the contribution of solution x to dimension i.**»

**Устоявшееся имя приёма, дословно из текста: «multi-attribute object rating»**, со ссылкой на
Ardissono et al. 2003 (AI Magazine 24(3):93–108).

**Соответствие с FINPILOT — покомпонентно:**

| FSAdvisor (2005) | FINPILOT (2026) | Совпадение |
|---|---|---|
| `g(x) = Σ ei·si(x)` | `U(a) = Σ w_k · x_k^norm(a)` | структурно тождественно |
| `ei` — интерес клиента к измерению i | `w_k` — вес критерия из риск-профиля | тождественно по роли; у нас 5 фиксированных профилей вместо непрерывной анкеты |
| `si(x)` — вклад решения x в измерение i | `x_k^norm` — min-max нормированный критерий | у нас нормировка внутри текущего множества; у них — не оговорена |
| измерения `profit, availability, risk` | критерии `ресурс, ликвидность, долг, продвижение целей` | разные наборы, одна конструкция |
| ~1–2 млн альтернатив, 300–400 ограничений | 66 альтернатив, 2 жёстких инварианта | масштаб на 4 порядка меньше |
| CSP-решатель, поиск | полный перебор решётки | у нас перебор возможен из-за малости множества |

## 2.4. Диагностика и repair при пустом результате — дословно (с. 1480)

> «**Diagnosis and Repair of Requirements.** If the result set is empty, conventional recommender
> applications tell the user that no solution was found. FSAdvisor supports the calculation of
> repair actions for customer requirements (a minimal set of changes allowing the calculation of
> a solution). If Σ = {x1 = a1, x2 = a2, ..., xn = an} is a set of customer requirements (Σ ∪ C has
> no solution), **a repair is a minimal set of changes to Σ (resulting in Σ') s.t. Σ' ∪ C has a
> solution. The computation of repair actions is based on the Hitting Set algorithm (Reiter 1987)**
> […]. Model-based diagnosis of customer requirements has been introduced in (Felfernig et al.
> 2004), state-of-the-art constraint reasoners (Junker 2004) provide conflict detection but do not
> support the calculation of minimal repair actions.»

Персонализация repair (приоритеты переменных), дословно (с. 1480):

> «**Personalized Repair Proposals.** If no solution can be found for a given set of customer
> requirements, FSAdvisor proposes a minimal set of possible repair actions which allow the
> calculation of a solution. **Different customer properties (variables) have an assigned priority
> which indicates the importance of the variable for the customer. The lower the priority of the
> variable the higher the probability is that the variable is considered as focus of repair
> actions**, e.g. if the type of returns on investment (reinvestment, dividend output) is
> unimportant for a customer, this property is primarily considered as a potential candidate for
> repair actions, i.e. repair actions are adapted to the customer's preferences.»

Тот же аппарат применяется и к отладке самой базы знаний, дословно (с. 1480):

> «Similar to the diagnosis and repair of customer requirements, we apply model-based diagnosis
> techniques in order to identify a minimal set of constraints ∈ C which — when deleted from the
> recommender knowledge base — allow consistency restoration.»

## 2.5. Объяснения — дословно (с. 1480–1481)

> «**Personalized Solution Presentation.** For each solution a corresponding set of explanations is
> calculated. The generation of explanations is based on the concepts presented in (Friedrich 2004).
> Furthermore solution-specific explanations are supported, e.g. **if the customer is strongly
> interested in high return rates and a solution shows a remarkable return rate, this fact is
> explicitly mentioned when the solution is presented to the customer.**»

🔴 То есть объяснение «этот вариант выбран, потому что по важному для вас измерению он даёт много»
— **уже опубликовано в 2005 году** и построено ровно на том же `ei·si(x)`.

Регуляторная мотивация объяснимости (европейская, но по смыслу совпадает с российской практикой
раскрытия), дословно (с. 1476):

> «**Documentation.** Due to regulations of the European Union, financial service providers are
> forced to improve the documentation of advisory sessions. **Intelligent reporting is required which
> includes explanations as to why certain products were offered to a customer.**»

## 2.6. Внедрение и ЗАМЕРЕННЫЕ результаты — дословно (раздел «Application Use and Payoff», с. 1481)

> «FSAdvisor is installed for **150 sales representatives of the Hypo-Alpe-Adria bank since July
> 2003** and for **1400 sales representatives of the Wüstenrot building and loan association since
> June 2004**.»

> «The sales volume of Wüstenrot in 2004 was about **345.000 products** (185.000 building loan
> contracts, 50.000 personal insurances, 100.000 property insurances, and 10.000 other products).»

> «On the average a sales representative sells about **60 − 70 products per year** (highly performing
> sales experts sell up to 500 products per year). The advisors implemented for ADAP have been
> evaluated by sales representatives (experts as well as less experienced representatives) from
> different sales organizations in Austria. **The interviewees were agreeing on the quality of the
> calculated solutions and the design of the advisory dialogs.** Automated generation of intelligent
> summaries of advisory sessions, error-free solutions and cross-selling support are the major
> motivations for applying FSAdvisor […]»

> «**Time Savings.** Time savings related to the application of the advisors can amount up to
> **30 − 50% per advisory session**. This reduction is achieved by generating advisory summaries and
> using customer answers and results from the advisory process to automatically generate offers.»

> «**Quality of Solutions.** FSAdvisor knowledge bases are developed and tested by marketing and
> sales experts. Sales representatives can rely on the solutions calculated by the financial advisor
> and can provide the customer with qualified explanations. **100% error-free offers are provided to
> the customer.**»

Смежная система той же школы с измеренным эффектом на удовлетворённость (не финансы, фотокамеры),
дословно (с. 1481):

> «the digital camera advisor **PIXLA** which was implemented for the largest Austrian online product
> platform (www.geizhals.at). PIXLA is deployed since November 2003 and exhibits about **10.000
> successful advisory sessions per month**. Users of www.geizhals.at were interviewed before and after
> the introduction of PIXLA. The major result of the study was a **statistically significant increase
> of customer satisfaction** (related to dimensions such as easiness to find products etc.).»

🔴 **Важная оговорка о характере замеров.** Ни один из приведённых авторами показателей
(30–50% времени, «100% error-free», согласие интервьюируемых) не является контролируемым
сравнением с baseline. Это отчёт о внедрении (IAAI — трек «инновационных применений», не
исследовательский трек), а не эксперимент. Единственный статистически проверенный результат в
статье — рост удовлетворённости у PIXLA, и он вне финансового домена.

## 2.7. Признанные авторами ограничения — дословно

Стоимость проекта (раздел «Application Development and Deployment», с. 1481–1482):

> «the overall efforts related to a customer project are between **1.5 man months (single advisor)
> and 15 man months** (complete integration of an advisor suite into the customer's CRM system […])»

Комбинаторный взрыв тестирования, дословно (с. 1479):

> «The complete set of possible test cases for a recommender knowledge base with 20 customer
> properties (variables) with a domain of cardinality 5 would comprise about **5^20 test cases which
> is definitely infeasible** for a domain expert. Reducing the input space to 20 possible paths each
> path defined by 7 variables and 5 possible values per variable reduces the number of potential test
> cases to 1.5 mio which is still unfeasible. By applying additional restrictions (equivalence
> partitioning, certified constraints etc.) we can reduce the number of test cases from 1.5 mio to
> about 500.»

Главный признанный барьер, дословно (раздел «Learnings», с. 1482):

> «On the technical level a crucial success factor for advisor projects is that non-programmers are
> enabled to implement and maintain knowledge bases, i.e. **the knowledge acquisition bottleneck must
> be reduced as much as possible** by a development environment supporting graphical design and
> debugging of knowledge bases.»

> «**The correctness of solutions plays a vital role for the acceptance of the system** by sales
> representatives applying the system while communicating with the customer. Therefore, automated
> test case generation mechanisms are needed which support the effective validation of knowledge
> bases.»


---

# 1. Каноническая формализация constraint-based recommenders (ДОБЫТО ДОСЛОВНО)

**Основной вскрытый источник — свежайший обзор той же школы, написанный самим Фельферниг
с соавторами, и он служит канонической сводкой формализации:**

Uta, M.; **Felfernig, A.**; Le, V.-M.; Tran, T. N. T.; Garber, D.; Lubos, S.; Burgstaller, T.
**«Knowledge-based recommender systems: overview and research directions».**
*Frontiers in Big Data*, 7:1304439, 2024. DOI: 10.3389/fdata.2024.1304439.
URL (открыт, HTML снят через curl+UA): https://www.frontiersin.org/journals/big-data/articles/10.3389/fdata.2024.1304439/full

## 1.1. Место constraint-based в таксономии

Дословно (Section 1, Introduction):

> «Third, **knowledge-based recommender (KBR) systems** can be considered as complementary to CF-
> and CBF-based approaches in terms of avoiding the related cold-start difficulties (Burke, 2000;
> Towle and Quinn, 2000; Lorenzi and Ricci, 2005). KBR systems are based on the idea of collecting
> the preferences of a user (preference elicitation) within the scope of a dialog and then to
> recommend items either (1) on the basis of a predefined set of recommendation rules (constraints)
> or (2) using similarity metrics that help to identify items which are similar to the preferences
> of the user. **The first approach is denoted as constraint-based recommendation (Felfernig and
> Burke, 2008), whereas the second one is referred to as case-based recommendation (Lorenzi and
> Ricci, 2005) — these two can be regarded as major types of knowledge-based recommender systems
> (Aggarwal, 2016).**»

🔴 Прямое попадание домена, дословно (там же):

> «KBR systems support the determination of recommendations specifically in **complex and
> high-involvement item domains** [domains where suboptimal decisions can have significant negative
> consequences, for example, when investing in high-risk financial services (Felfernig et al., 2006)]
> where items are not bought on a regular basis (Aggarwal, 2016). **Example item domains are financial
> services** (Felfernig et al., 2007; Musto et al., 2015), software services (Felfernig et al., 2021),
> apartment or house purchasing (Fano and Kurth, 2003), and digital cameras (Felfernig et al., 2006).
> These systems are able to take into account constraints (e.g., high-risk financial services must not
> be recommended to users with a low preparedness to take risks) and **provide explanations of
> recommendations also in situations where no solution could be identified.**»

Слабость школы, признанная в том же абзаце, дословно:

> «**Serendipity effects in knowledge-based recommendation are limited by the static encoding in terms
> of constraints (rules) and similarity metrics.**»

> «Due to an often time-intensive knowledge exchange between domain experts and knowledge engineers,
> **the definition of recommendation knowledge can trigger high setup costs** (Ulz et al., 2017).»

## 1.2. Формальные определения — дословно (Section 3.3)

> «3.3 Constraint-based recommendation. The concept of constraint-based recommendation (Felfernig and
> Burke, 2008) is based on the idea that recommendation knowledge is represented in terms of a set of
> variables and a corresponding set of constraints.»

> «**Definition 1.** A constraint-based recommendation task (**CB-REC Task**) can be defined as a
> constraint satisfaction problem (CSP) (V, C, R) where V = {v1..vn} is a set of finite domain
> variables with associated variable domain definitions dom(vi), C = {c1..cm} is a set of constraints,
> and R = {r1..rk} is a set of user requirements.»

> «**Definition 2.** A constraint-based recommendation (**CB-REC**) for a defined CB-REC Task is a set
> of tuples REC = ⋃(iα ∈ I) {(rank_iα, iα)} where rank_iα represents the recommendation rank assigned
> to item iα ∈ I **defined by a recommendation function rf** and ∀(rank_iα, iα) ∈ REC:
> **consistent(C ∪ R ∪ a(iα))** where a(iα) denotes the variable value assignments associated with
> item iα.»

🔴 **Это и есть каноническое разделение «фильтрующие vs ранжирующие»:** предикат
`consistent(C ∪ R ∪ a(iα))` из Definition 2 — фильтр (жёсткие ограничения, бинарный допуск),
а функция `rf`, задающая `rank_iα`, — ранжирование выживших. У Фельферниг они **разнесены по
определению**, а не по реализации.

## 1.3. Экстенсиональное vs интенсиональное представление — дословно (Section 3.1)

> «Knowledge representations of knowledge-based recommender systems can be (1) **table-based** which
> is used in scenarios where items are represented in terms of product table entries or (2)
> **constraint-based** which is used in scenarios where items are defined on the basis of a set of
> restrictions (also denoted as rules or constraints). In the first case (**extensional
> representation**), each item that could be recommended is explicitly defined in a corresponding item
> (product) table. In the second case, there is no need to enumerate all items since items are
> specified in a constraint-based fashion (**intensional representation**).»

🔴 Прямая релевантность нашей решётке из 66 альтернатив, дословно (Section 3.1.1):

> «**Table-based representations can be applied if the set of offered items is limited, i.e., the item
> space is rather small — which is often the case, for example, in digital camera or financial service
> recommendation** (Felfernig et al., 2006, 2007). Using a table-based knowledge representation,
> corresponding database queries can be performed to identify a set of recommendation candidates that
> support the preferences defined by the user (Felfernig et al., 2006, 2023a).»

Обратная сторона (когда решётка перечислима, интенсиональное представление не требуется),
дословно (Section 3.1.2):

> «Such knowledge representations [интенсиональные] are specifically useful **if the solution (item)
> space becomes intractable**, i.e., defining and maintaining all alternatives is extremely inefficient
> and error-prone (or even impossible) and related search queries become inefficient and at least
> impractical for interactive settings (Falkner et al., 2011).»

## 1.4. Где сидит utility/MAUT-ранжирование — дословно (Section 3.3.1 «Ranking items»)

> «**3.3.1 Ranking items.** Up to now, we did not specify a function rf for the ranking of the items in
> REC. A simple ranking function could just count the number of supported features (see Equation 1)…»

> «**An alternative to our simplified ranking function (Equation 1) is to introduce a utility function
> which evaluates utility of individual items on the basis of a pre-defined set of interest dimensions**
> (Felfernig et al., 2006, 2018a). In our software service recommendation scenario, examples of
> relevant interest dimensions are economy and quality.»

> «Such utility-based evaluation schemes can then be used by a utility function to determine the
> overall utility of individual items — see, for example, **Equation (2)** — where **D represents a set
> of interest dimensions** […] and **eval(iα, d) represents the evaluation scheme** as presented in
> Table 10. **Assuming equal importance of the two example interest dimensions [e.g.,
> importance(economy) = 0.5 and importance(quality) = 0.5], utility(i3) = 0.0 + 10.0 = 10.0 and
> utility(i5) = 0.0 + 15 = 15.0**, i.e., item i5 has a higher utility compared with item i3. Depending
> on the user-specific importance of individual interest dimensions, the resulting utility values can
> differ.»

Equation (2) в нотации статьи: **utility(iα) = Σ(d ∈ D) importance(d) × eval(iα, d)**.

## 1.5. 🔴 ОТВЕТ НА ВОПРОС «ЕСТЬ ЛИ У НАШЕЙ КОНСТРУКЦИИ УСТОЯВШЕЕСЯ ИМЯ»

**Да. Полностью.** Конструкция «жёсткие ограничения → конечное множество кандидатов → аддитивная
взвешенная свёртка по измерениям интереса → выдача с объяснением вклада» — это:

- **по классу системы**: *constraint-based recommender system* на *table-based / extensional
  representation* (Uta et al. 2024, Def. 1–2 и §3.1.1; Felfernig & Burke 2008);
- **по шагу отсечения**: предикат `consistent(C ∪ R ∪ a(iα))` (Uta et al. 2024, Definition 2);
- **по шагу ранжирования**: *utility-based ranking function* / **multi-attribute utility scheme**
  (Uta et al. 2024, §3.3.1, Eq. 2), он же **«multi-attribute object rating»** в терминологии
  FSAdvisor (Felfernig & Kiener 2005, с. 1480) и Ardissono et al. 2003.

**Ни одного слова о новизне самой конструкции сказать нельзя** — она названа, формализована и
опубликована. Наш лексикографический floor-приоритет — единственный элемент, для которого точное
имя в этой школе пока не найдено (см. §7).

---

# 3. Объяснения в constraint-based RS (ДОБЫТО ДОСЛОВНО)

Uta et al. 2024, **Section 4.5.5 «Explanations in knowledge-based recommendation»** — каноническая
трёхчастная типология, дословно:

> «(1) **why explanations** help a user to understand the reasons why a specific item has been
> recommended. In the context of single-shot recommendation approaches such as collaborative filtering
> and content-based filtering, explanations are directly related to the used algorithmic approach. For
> example, *this item is recommended, since similar users also liked it* […]. **Answering such why
> questions in the context of knowledge-based recommendation means to relate recommendations to user
> preferences**, for example, *this camera is recommended since it includes a high frame rate per second
> which corresponds to your requirement to be able to perform sports photography on a professional
> level*.»

> «(2) **Why not explanations** help users to understand in more detail why no solution could be found
> for their requirements. In this context, **conflicts (Junker, 2004) help to understand, for example,
> individual incompatibilities between user requirements, whereas diagnoses (Reiter, 1987; Felfernig
> et al., 2012) are a general proposal (explanation) for resolving an inconsistency.**»

🔴 **Пункт (3) — это ДОСЛОВНО наша «объяснимость через вклад критерия»:**

> «(3) **How explanations** are more related to specific aspects of a recommendation process, for
> example, **when using a utility-based approach for item ranking (Felfernig et al., 2006),
> explanations can take into account corresponding weights to explain how a recommendation has been
> determined**, for example, *since you have ranked the priority of the feature fps (frame rate per
> second) very high, item X is the one which is ranked highest since it received the highest utility
> value on the basis of our evaluation function*.»

**Вывод по вопросу 3.** Приём «показать вклад `w_k · x_k^norm` каждого критерия в итоговую
полезность» называется в этой школе **HOW-explanation при utility-based ranking**, восходит к
Felfernig et al. 2006 и с 2005 года работает в проде в FSAdvisor (см. §2.5). Он **не нов**.
Репутация подхода как «объяснимого по построению» подтверждена первоисточником: у FSAdvisor
объяснимость названа причиной отказа от CF/CBF (§2.1), а в обзоре 2024 — как способность
«provide explanations of recommendations also in situations where no solution could be identified»
(§1.1).

---

# 4. Пустой результат и repair (ДОБЫТО ДОСЛОВНО)

Это самый разработанный участок школы, и здесь есть **готовые канонические рецепты** для нашей
ситуации «жёсткие инварианты Rt≥0 и ПДН≤0.40 отсекли ВСЁ».

## 4.1. Конфликты и диагнозы — определения (Uta et al. 2024, §3.3.2), дословно

> «**In constraint-based recommendation, it can be the case that individual user requirements do not
> allow the determination of a recommendation.**»

> «**Definition 3.** A conflict (set) CS ⊆ R is a set of constraints with inconsistent(CS ∪ C), i.e.,
> no solution can be found for CS ∪ C. A conflict set CS is minimal if ¬∃CS′: CS′ ⊂ CS (subset
> minimality). **Conflict set minimality is important due to the fact that just one requirement needs
> to be deleted (i.e., relaxed) from CS in order to resolve the conflict.**»

> «**Definition 4.** A diagnosis Δ ⊆ R is a set of constraints with consistent(R − Δ ∪ C), i.e., at
> least one solution can be found for R − Δ ∪ C. A diagnosis Δ is minimal if ¬∃Δ′: Δ′ ⊂ Δ (subset
> minimality).»

Когда что применять, дословно:

> «Both concepts, i.e., conflict sets and corresponding diagnoses can be used to support users in
> inconsistent situations. **Conflict sets are helpful in the context of repeated conflict resolution**
> […], and **diagnoses can be used when users are interested in quick repairs** […].»

## 4.2. Персонализированная диагностика через ту же аддитивную полезность (§4.2), дословно

> «**4.2 Dealing with "no solution could be found" situations.** As discussed in Section 3, users of
> knowledge-based recommenders in some situations need support to get out of the **no solution could be
> found dilemma**. Approaches that can proactively support users in such contexts are **conflict
> detection (Junker, 2004) and model-based diagnosis (Reiter, 1987; Felfernig et al., 2012; Walter et
> al., 2017). Such algorithms help users to understand trade-offs in the current situation and propose
> different options to resolve inconsistencies.**»

> «Having user preference weights available, for example, in terms of explicitly defined preference
> weights, algorithms can be applied in different ways to **determine preferred (personalized)
> diagnoses**.»

🔴 Дословно про механику выбора диагноза (тот же аддитивный аппарат, что и в ранжировании):

> «**Following a simple additive utility-based scheme (Felfernig et al., 2013c)** using the orderings
> depicted in Table 14 (the lower the ordering position, the higher the importance of the related user
> requirement), the conflicts CS1 and CS2 would be resolved (in a personalized fashion) as follows: for
> the user in Session s1 (user 1), we would keep the exclusion of license as-is and exclude both,
> ABtesting and multiplechoice (**1 < 3+4**). Vice-versa, in the case of session s2 (user 2), we would
> keep the preferences regarding ABtesting and multiplechoice as-is and accept the inclusion of a
> license fee (**1+2 < 4**).»

## 4.3. Что делает промышленная система (FSAdvisor) — дословно, см. §2.4 выше

Двухступенчатая схема, которой у нас нет:
1. **релаксация по приоритетам:** «constraints with a priority > 0 (0 is the highest priority) are
   relaxed starting with constraints with lowest priority»;
2. **если остались только нерелаксируемые (priority = 0) — включается repair** через Hitting Set
   (Reiter 1987), причём фокус repair смещается на переменные с низким приоритетом ДЛЯ КЛИЕНТА.

## 4.4. Алгоритмический аппарат — точные ссылки

- **Reiter, R. «A theory of diagnosis from first principles». Artificial Intelligence 32(1):57–95,
  1987.** (В библиографии FSAdvisor указано «23(1):57–95» — это опечатка авторов FSAdvisor; см.
  раздел «Что не добыто» — оригинал Reiter я не открывал, точный том не сверен.) Hitting-set
  алгоритм вычисления минимальных диагнозов из минимальных конфликтов.
- **Junker, U. «QUICKXPLAIN: Preferred Explanations and Relaxations for Over-Constrained Problems».
  AAAI-04, 19th National Conference on AI, 2004, pp. 167–172.** Быстрое вычисление **предпочтительного
  минимального конфликта** (не диагноза). Ограничение зафиксировано дословно в FSAdvisor (с. 1480):
  «state-of-the-art constraint reasoners (Junker 2004) **provide conflict detection but do not support
  the calculation of minimal repair actions**».
- **Felfernig, A.; Friedrich, G.; Jannach, D.; Stumptner, M. «Consistency-based Diagnosis of
  Configuration Knowledge Bases». Artificial Intelligence 152(2):213–234, 2004.** Диагностика самой
  базы знаний, а не требований пользователя.
- Более поздние: Felfernig et al. 2012, Walter et al. 2017, Le et al. 2021/2023 («Analysis operations
  for constraint-based recommender systems», RecSys '23) — по ссылкам из Uta et al. 2024.

## 4.5. 🔴 Ключевое различие нашего случая и канонического

В каноне отсечение производят **пользовательские требования R** (их и релаксируют — это переговорный
предмет). У FINPILOT отсекают **инварианты предметной области C** (Rt≥0 — арифметическое тождество,
ПДН≤0.40 — регуляторный/риск-порог). По Definition 4 диагноз ищется **только внутри R** (Δ ⊆ R),
а C неприкосновенно. Следовательно:

- прямой перенос «релаксировать ограничение» **невозможен** для Rt≥0 (это не предпочтение, а
  бухгалтерия) и **сомнителен** для ПДН≤0.40;
- каноническим остаётся другое: если пусто, надо диагностировать, **какая часть ВХОДА** (цели,
  сроки, суммы взносов — то, что у нас играет роль R) конфликтует, и предложить минимальное
  изменение именно её. Это ровно «Personalized Repair Proposals» FSAdvisor.

---

# 1-БИС. Каноническая формализация — версия из Recommender Systems Handbook (ДОБЫТО ДОСЛОВНО)

**Источник (PDF скачан curl-ом с авторского зеркала, разобран pdftotext):**
Felfernig, A.; Friedrich, G.; Jannach, D.; Zanker, M. **«Constraint-Based Recommender Systems».**
In: Ricci, F.; Rokach, L.; Shapira, B. (eds.) *Recommender Systems Handbook*, 2nd ed., Springer,
2015, Chapter 5, pp. 161–190. DOI: 10.1007/978-1-4899-7637-6_5.
Открытая авторская копия: https://web-ainf.aau.at/pub/jannach/files/BookChapter_Constraint-BasedRS_2015.pdf
(Есть и версия 1-го издания 2011 г.: «Developing Constraint-based Recommenders»,
https://web-ainf.aau.at/pub/jannach/files/BookChapter_RS-Handbook-2010.pdf — тоже скачана.)

🔴 **Это самая точная формализация под наш вопрос: она сделана НА ПРИМЕРЕ ФИНАНСОВЫХ УСЛУГ.**

## 1б.1. Пять компонент базы знаний — дословно (с. 162–163)

> «Technically, a recommender knowledge base of a constraint-based recommender system (see [22])
> can be defined through **two sets of variables (VC, VPROD) and three different sets of constraints
> (CR, CF, CPROD)**. These variables and constraints are the major ingredients of a constraint
> satisfaction problem [72].»

> «**Customer Properties VC** describe possible requirements of customers, i.e., requirements are
> instantiations of customer properties. **In the domain of financial services *willingness to take
> risks* is an example of a customer property** and *willingness to take risks = low* represents a
> concrete customer requirement.»

> «**Product Properties VPROD** describe the properties of a given product assortment. Examples of
> product properties are recommended investment period, product type, product name, or expected
> return on investment.»

> «**Constraints CR** are systematically restricting the possible instantiations of customer
> properties, for example, *short investment periods are incompatible with high risk investments*.»

> «**Filter Conditions CF** define the relationship between potential customer requirements and the
> given product assortment. An example of a filter condition is the following: *customers without
> experiences in the financial services domain should not receive recommendations which include
> high-risk products*.»

> «**Products.** Finally, the allowed instantiations of product properties are represented by CPROD.
> **CPROD represents one constraint in disjunctive normal form** that defines elementary restrictions
> on the possible instantiations of variables in VPROD.»

🔴 **Вот прямой ответ на «фильтрующие vs ранжирующие правила»: в каноне разделены не два, а ТРИ
класса ограничений** — CR (совместимость требований между собой), CF (связь требований с
продуктами; собственно «filter conditions»), CPROD (сам каталог как DNF-ограничение). Ранжирующие
правила в этот список **не входят вовсе** — они отдельный слой (utility/MAUT), см. §1б.3.

## 1б.2. Определения задачи и решения — дословно (Definitions 5.1, 5.2, с. 165)

> «**Definition 5.1.** A **recommendation task** can be defined as a constraint satisfaction problem
> (VC, VPROD, CC ∪ CF ∪ CR ∪ CPROD) where VC is a set of variables representing possible customer
> requirements and VPROD is a set of variables describing product properties. CPROD is a constraint in
> disjunctive normal form that describes product instances, CR is a set of constraints describing
> possible combinations of customer requirements, and CF (filter conditions) is a set of constraints
> describing the relationship between customer requirements and product properties. Finally,
> **CC is a set of unary constraints representing concrete customer requirements.**»

> «**Definition 5.2.** An assignment of the variables in VC and VPROD is denoted as **consistent
> recommendation** for a recommendation task (VC, VPROD, CC ∪ CF ∪ CR ∪ CPROD) **iff it does not
> violate any of the constraints** in CC ∪ CF ∪ CR ∪ CPROD.»

Пример базы знаний в статье — буквально инвестиционный советник (Example 5.1, с. 163–164):
`VC = {klc: [expert, average, beginner], wrc: [low, medium, high] (willingness to take risks),
idc: [shortterm, mediumterm, longterm] (duration of investment), …}`;
`CR = {CR1: wrc = high → idc ≠ shortterm; CR2: klc = beginner → wrc ≠ high}`;
`CF = {CF1: idc = shortterm → mnivp < 3; … CF4: wrc = low → rip = low; CF7: klc = beginner → rip ≠ high; …}`.

## 1б.3. 🔴 Ранжирование выживших = MAUT, названо ПРЯМО (с. 180, «Ranking Items»)

> «**Ranking Items.** Given a recommendation task, both constraint solvers and database engines try
> to identify a set of items that fulfill the given customer requirements. Typically, we have to deal
> with situations where more than one item is part of a recommendation result. **In such situations
> the items (products) in the result set have to be ranked. In both cases (constraint solvers and
> database engines), we can apply the concepts of multi-attribute utility theory (MAUT) [74] that
> helps to determine a ranking for each of the items in the result set.** Examples for the application
> of MAUT can be found in [19, 27].»

Где ссылка **[74] = Winterfeldt, D.; Edwards, W. «Decision Analysis and Behavioral Research».
Cambridge University Press** (это база MAUT, на которую опирается сама школа; **не** Keeney & Raiffa
— в списке литературы главы 2015 г. Keeney & Raiffa отсутствуют, что зафиксировано как факт).

Альтернативы MAUT, названные там же:

> «An alternative to the application of MAUT in combination with conjunctive queries are
> **probabilistic databases** [48] which allow a direct specification of ranking criteria within a
> query. […] Finally, instead of combining the mentioned standard constraint solvers with MAUT, we
> can represent a recommendation task in the form of **soft constraints** where the importance
> (preference) for each combination of variable values is determined on the basis of a corresponding
> utility operation (for details see, for example, [2] = Bistarelli, Montanari, Rossi,
> «Semiring-based Constraint Satisfaction and Optimization», JACM 44:201–236, 1997).»

🔴 **Итог по вопросу 1, в одну строку:** наша конструкция называется
**«constraint-based recommender cascaded with a MAUT-based utility ranking scheme»**.
Точная фраза той же школы (см. §6.2 ниже): *«a constraint-based recommender is cascaded with a
utility-based item ranking scheme like the CWAdvisor system»* (Felfernig et al. 2015, с. 181).

---

# 2-БИС. VITA — второе финансовое внедрение, с ИЗМЕРЕННЫМИ результатами и t-тестами

**Источник (PDF скачан curl-ом, разобран pdftotext):**
Felfernig, A.; Isak, K.; Szabo, K.; Zachar, P. **«The VITA Financial Services Sales Support
Environment».** Proceedings of the 19th Conference on Innovative Applications of Artificial
Intelligence (IAAI-07) / AAAI-07, 2007, pp. 1692–1699.
URL: https://cdn.aaai.org/AAAI/2007/AAAI07-274.pdf

## 2б.1. Что рекомендуется и где внедрено — дословно (с. 1697)

> «The VITA financial services recommenders have been deployed in the 4th quarter of 2005 and are
> applied by about **800 sales representatives of the Fundamenta building and loan association**
> primarily for the **recommendation of loans**. In 2006, about **125.000 products have been sold**
> by the Fundamenta building and loan association. **About 10% of those products have been sold on
> the basis of VITA.** Since savings (about 90% of the sold products) are basic products without the
> need of an advisory support, no VITA processes have been implemented for this product type.»

## 2б.2. Целевая функция — MAUT, применённая ТРИЖДЫ — дословно (с. 1695)

> «**Multi-Attribute Utility Theory (MAUT)** (Schmitt et al. 2003): this personalization approach is
> well known in knowledge-based recommender systems research. **(Burke 2000) classifies this
> technology under the concept of utility-based recommendation which is a specific type of
> content-based recommendation.** We apply MAUT for the following purposes:»

> «(1) **Ordering a recommendation set** determined by the recommender application. Each product part
> of a recommendation is evaluated w.r.t. to a given set of product dimensions. Conform to theories of
> cognitive psychology (Gershberg and Shimamura 1994), the most interesting products are presented
> first.»

> «(2) **Ordering of repair actions.** In this case, a set of alternative repair actions is evaluated
> w.r.t. to a defined set of abstract product dimensions. Those **repair actions with the highest
> probability of being accepted by the customer (highest utility) are presented first.**»

> «(3) **Ordering of explanations.** When presenting recommendation results, each of those results has
> an attached list of explanations (argumentations) why this result (product) fits to the wishes and
> needs of a customer. Depending on the given set of abstract product dimensions, **explanations can
> be ordered (most important explanations are presented first)**. […] Each filter constraint has an
> assigned explanation. Customer requirements such as *accessibility_of_investment = flexible* are
> evaluated w.r.t. their impact on different MAUT dimensions (e.g., dimension Accessibility).
> **The higher the impact of certain requirements, the higher is the importance of the MAUT dimension
> for the customer and the higher is importance of the corresponding explanation.**»

🔴 **Пункт (3) — это ровно наша идея «объяснение по вкладу критерия», но развёрнутая дальше нашей:
у них MAUT-веса управляют не только выбором альтернативы, но и ПОРЯДКОМ ОБЪЯСНЕНИЙ.**
Пример из Figure 6 (с. 1698), дословная таблица:
`F1: preparedness_to_take_risks = low → product_risk_level = none ∨ low` → объяснение E1
«The risk rate of this product corresponds to your requirements (a very low level of risk)», вес 9,
измерение MAUT «Preparedness to take risks»; `F2: duration_of_investment = 1-3years → …` → E2, вес 1,
измерение «Profit»; `F3: accessibility_of_investment = flexible → producttype ≠ insurance` → E3,
вес 10, измерение «Accessibility of investment».

## 2б.3. 🔴 ЗАМЕРЕННЫЕ РЕЗУЛЬТАТЫ — дословно (с. 1697–1698). Самые сильные цифры во всей теме

Выборка:

> «we have interviewed sales representatives (**n=205**) of Fundamenta in Dec. 2006. […] On an
> average, interviewees were working for Fundamenta since 3.0 years (std. dev. 2.8 years), the average
> age of the participants was 37.7 years (std.dev. 11.0 years). 38.6% were female participants and
> 61.4% were male participants.»
> Экспертиза (Table 1): beginner 53 чел. (26%), average 31 (15%), expert 121 (59%).

Оценка важности:

> «Results of the study show that VITA is of high importance for improving business processes related
> to the selling of financial services (**91.2% of the participants agreed** on that aspect).»

Экономия времени, **с t-тестом**:

> «On an average a sales dialog with the customer takes about **59.1 minutes** (std. dev. 22.9
> minutes) […]. Regarding the average duration of an advisory session, interviewees specified **time
> savings directly related to the VITA application with about 9.0 minutes per advisory session (std.
> dev. 8.6 minutes), which means time savings of about 13.3%** compared to the duration of advisory
> sessions without a corresponding VITA support. **The significance of these time savings is confirmed
> by a corresponding t-test (t-score = 11.84, p < 0.0001).** If we assume that an average sales
> representative conducts about 70 advisory sessions per year, this results in time savings of about
> 10.5 hours per representative per year. For high performers conducting about 500 sessions per year
> this means time savings of about 75.0 hours (!) per representative per year.»

Окупаемость:

> «Assuming a low margin of 1% and an average loan amount of €30.000, **the investment of about
> €100.000 for the implementation of the VITA environment has been amortized within the same year.**»

Ошибки и удовлетворённость:

> «The VITA application is of high importance for the reduction of errors in the offer generation phase
> (**90.0% of the representatives agreed** on that aspect). Furthermore, the majority of sales
> representatives (**89.2%**) articulated a high value of satisfaction with the recommender
> application. The reasons where time savings in the conduction of sales dialogs and more intuitive
> reporting and explanations for customers.»

🔴 **Рост продаж, с t-тестом** (с. 1698):

> «When comparing the sales rates of 2005 with the sales rates of 2006, **the overall sales rate of
> VITA supported products has been increased by about 50% (!)**. On an average, sales representatives
> specified the increase of sold loans with **3.25 products per year (std. dev. 3.65 products)**. The
> significance of this increase is confirmed by a corresponding **t-test (t-score = 9.59, p < 0.0001)**.»

**Оговорка о качестве замера (моя, не авторов):** «+50% продаж» — это сравнение год-к-году без
контрольной группы, а «13.3% экономии времени» — САМООЦЕНКА представителей в анкете, а не хронометраж;
t-тест здесь проверяет, что средняя самооценка значимо отлична от нуля, а не что эффект вызван
системой. Это по-прежнему сильнее, чем у FSAdvisor, но это не RCT.

Стоимость внедрения — дословно (с. 1698):

> «The investment for the development and deployment of the VITA system was **about 1.5 man-years**
> which includes the development of recommender knowledge bases, the translation of German recommender
> versions into Hungarian […]. On an average, **three developers were involved** in the VITA project.»

---

# 6. Критика и эмпирика (ДОБЫТО ДОСЛОВНО — часть; см. также отчёт субагента)

## 6.1. Почему школа редка в проде — прямые формулировки

Uta et al. 2024, Section 5 «Research directions», дословно:

> «A major strength of knowledge-based (specifically constraint-based) recommenders is their ability
> to **enforce domain-specific constraints**. These systems are useful when recommending and
> explaining **high-involvement items such as cars and financial services**. **A major disadvantage is
> "setup" efforts that are needed to predefine the recommendation knowledge in terms of product
> properties, product catalogs, similarity metrics, and constraints.**»

Uta et al. 2024, Section 4.5.3, дословно:

> «The related phenomenon of the **knowledge acquisition bottleneck**, i.e., significant communication
> overheads between domain experts and knowledge engineers, **is still omnipresent** when applying such
> knowledge-based systems.»

Felfernig et al. 2015 (Handbook ch. 5), с. 161–162, дословно:

> «knowledge-based recommenders suffer from the so-called **knowledge acquisition bottleneck** meaning
> that the work of knowledge engineers is required to explicitly encode the knowledge of domain experts
> into a formal and executable representation.»

Felfernig et al. 2015, §5.6 «Future Research Issues», дословно:

> «**A constraint-based recommender is only as good as its knowledge base.** Consequently, the
> knowledge base has to be correct, complete, and up-to-date in order to guarantee high quality
> recommendations. **This implies significant maintenance tasks**, especially in those domains where
> data and recommendation knowledge changes frequently […]»

## 6.2. 🔴 ЕСТЬ ЛИ ОФФЛАЙН-СРАВНЕНИЕ С BASELINE — ДА, И ОНО НЕ В ПОЛЬЗУ ШКОЛЫ

Felfernig et al. 2015, §5.5 «Practical Experience from Fielded Applications», дословно (с. 181):

> «While the collaborative and the content-based recommendation paradigm have been extensively
> evaluated in the literature, **comparing knowledge-based recommendation algorithms with other
> recommendation paradigms received only limited attention in the past. One reason is that they are
> hard to compare, because they require different types of algorithm input:** collaborative filtering
> typically exploits user ratings while constraint-based recommender systems require explicit user
> requirements, catalog data, and domain knowledge. **Consequently, datasets that contain all these
> types of input data — like the Entree dataset provided by Burke [6] — would allow such comparisons,
> they are however very rare.**»

Единственное найденное прямое сравнение, дословно (там же; датасет — ритейлер премиальных сигар):

> «offline experiments could be made in which knowledge-based algorithm variants that exploited user
> requirements were compared with content-based and collaborative algorithms working on ratings. One of
> the interesting results were that **knowledge-based recommenders did not perform worse in terms of
> serendipity measured by the catalog coverage metric than collaborative filtering. This is especially
> true if a constraint-based recommender is cascaded with a utility-based item ranking scheme like the
> CWAdvisor system. However, collaborative filtering does better in terms of accuracy, if there are 10
> and more ratings known from users.**»

🔴 Ещё жёстче — про слабость самого ранжирования, дословно (с. 182):

> «The retrieval results of knowledge-based recommenders turn out to be **very precise, if users
> formulated some specific requirements. However, when only few constraints apply and the result sets
> are large, the ranking function is not always able to identify the best matching items.** In contrast,
> collaborative filtering learns the relationships between requirements and actually purchased items.
> Therefore, the study showed that **a cascading strategy in which the knowledge-based recommender
> removes candidates based on hard criteria and a collaborative algorithm does the ranking works
> best.**»

И — прямое эмпирическое поражение экспертной базы знаний, дословно (с. 182):

> «in [76] a meta-level hybridization approach between knowledge-based and collaborative filtering was
> proposed and validated. There collaborative filtering learns constraints that map users' requirements
> onto catalog properties of purchased items and feeds them as input into a knowledge-based recommender
> that acts as the principal component. **Offline experiments on historical data provided initial
> evidence that such an approach is able to outperform the knowledge base elicited from the domain
> experts with respect to algorithm's accuracy.**»

Фундаментальная методологическая оговорка школы о самой себе, дословно (с. 182):

> «**Nevertheless, an evaluation of a knowledge-based recommender always measures the quality of the
> encoded knowledge base and the inferencing mechanism itself.**»

## 6.3. Положительная эмпирика (для честного баланса) — дословно, Felfernig et al. 2015, §5.5

> «a conversational recommender for digital cameras has been fielded that was utilized by more than
> **200,000 online shoppers** at a large Austrian price comparison platform. […] **A significantly
> higher share of users successfully completed their product search when using the conversational
> recommender compared to those that did not use it.**»

> «another evaluation of a knowledge-based recommender in the tourism domain was conducted to compare
> conversion rates, i.e., the share of users that turned into bookers, between users and non-users of
> the interactive sales guide [78]. This study strongly empirically confirms that **the probability of
> users issuing a booking request is more than twice as high for those having interacted with the
> interactive travel advisor** than for the other non-interacting users.»

> «**Installations of knowledge-based recommenders in the financial services domain follow a different
> business model as they support sales agents while interacting with their prospective clients.
> Empirical surveys among sales representatives showed that the time savings when interacting with
> clients were considered to be a big advantage** which in turn allows sales staff to focus on sales
> opportunities [19, 23].»

## 6.4. 🔴 Известное «слабое место», которое прямо про нашу свёртку

Найдена работа школы, посвящённая тому, что **веса utility-функции на практике оказываются
НЕВЕРНЫМИ и их приходится чинить автоматически**:

Felfernig, A.; Schippel, S.; Leitner, G.; Reinfrank, F.; Isak, K.; Mandl, M.; Blazek, P.; Ninaus, G.
**«Automated repair of scoring rules in constraint-based recommender systems».**
*AI Communications* 26(1):15–27, 2013. DOI: 10.3233/AIC-120543.
(Полный текст НЕ открыт — SAGE/IOS Press за пейволом. Из аннотации, доступной в выдаче:
utility constraints / scoring rules «determine the order in which items are presented to customers»,
и «in many cases these constraints are faulty and calculate rankings which are not expected and
accepted by marketing and sales experts»; предложен подход автоматической адаптации набора
utility-ограничений через решение задачи нелинейной оптимизации.)
🔴 Формулировка снята с поисковой выдачи, а не с первоисточника — считать её ПЕРЕСКАЗОМ, не цитатой.

---

# 5. Utility-based recommendation отдельно от constraint-based

## 5.1. Что уже установлено дословно в добытых источниках

**Utility-based — самостоятельный класс в таксономии Burke, и школа Фельферниг это признаёт.**
Felfernig et al. 2015 (Handbook ch. 5), сноска 1 на с. 162, дословно:

> «**Utility-based recommenders are often categorized as being knowledge-based, too [5].** For a
> detailed discussion of utility-based approaches, see [5, 19].»
> ([5] = Burke, R. «Knowledge-Based Recommender Systems». *Encyclopedia of Library and Information
> Science* 69(32):180–200, 2000.)

Та же сноска в 1-м издании (Felfernig et al. 2011, «Developing Constraint-based Recommenders»,
с. 4): «Utility-based recommenders are often as well categorized as knowledge-based, see for example
[4]. For a detailed discussion on utility-based approaches we refer the interested reader to [4, 13].»

VITA (Felfernig et al. 2007, с. 1695) даёт прямую классификационную привязку, дословно:

> «Multi-Attribute Utility Theory (MAUT) […]: this personalization approach is well known in
> knowledge-based recommender systems research. **(Burke 2000) classifies this technology under the
> concept of utility-based recommendation which is a specific type of content-based recommendation.**»

🔴 Обратите внимание на расхождение внутри самой школы: в 2007 г. Фельферниг пишет, что Burke относит
utility-based к **content-based**, а в 2011/2015 гг. — что «часто относят к **knowledge-based**».
Это противоречие в первоисточниках, а не моя ошибка; фиксирую как есть.

## 5.2. 🔴 Основание MAUT в этой школе — НЕ Keeney & Raiffa

Ссылка [74] в Felfernig et al. 2015 (и [54] в изд. 2011), на которую опирается фраза «we can apply the
concepts of multi-attribute utility theory (MAUT) [74]»:

> «74. **Winterfeldt, D., Edwards, W.: Decision Analysis and Behavioral Research. Cambridge
> University Press**» (в изд. 2011: «54. Winterfeldt, D., Edwards, W.: Decision analysis and
> behavioral research. Cambridge University Press (1986)»).

**Keeney & Raiffa в списке литературы главы «Constraint-Based Recommender Systems» (Handbook, 2015)
ОТСУТСТВУЮТ** — проверено по полному тексту библиографии главы. Это существенно: школа берёт MAUT
в прикладной, поведенческой редакции von Winterfeldt & Edwards, а **не** в аксиоматической редакции
Keeney & Raiffa, где сформулированы условия законности аддитивной формы. Условия аддитивной
декомпозиции (preferential / utility / additive independence) в текстах школы **не обсуждаются
вообще** — ни в главе Handbook, ни в обзоре Uta et al. 2024, ни в FSAdvisor, ни в VITA.

🔴 **Это самый значимый методологический зазор, найденный в теме:** промышленная школа применяет
аддитивную свёртку без проверки условий, при которых она законна. Наша SAW-свёртка наследует ровно
ту же непроверенную предпосылку.

## 5.3. Известная альтернатива фиксированным весам внутри самой школы

Felfernig et al. 2015, с. 181, дословно (про оффлайн-эксперименты на исторических данных):

> «the training set is exploited to learn a model or **tune an algorithm's parameters (e.g.,
> importance values for MAUT-based interest dimensions [74])** in order to enable the recommender to
> predict the historic outcomes of the user sessions contained in the testing set.»

То есть **обучение весов MAUT из исторических данных названо в каноне как штатный приём** — наши
пять фиксированных риск-профилей это не новизна, а сознательный отказ от обучения.

Далее, в той же школе есть отдельная линия работ ровно про «веса неверны и их надо чинить»:
- Felfernig, A.; Teppan, E.; Friedrich, G.; Isak, K. **«Intelligent debugging and repair of utility
  constraint sets in knowledge-based recommender applications».** IUI '08 (13th Int. Conf. on
  Intelligent User Interfaces), ACM, 2008, pp. 217–226. DOI: 10.1145/1378773.1378802.
  **Полный текст НЕ открыт (ACM DL, HTTP 403).**
- Felfernig, A.; Schippel, S.; Leitner, G.; Reinfrank, F.; Isak, K.; Mandl, M.; Blazek, P.; Ninaus, G.
  **«Automated repair of scoring rules in constraint-based recommender systems».** *AI Communications*
  26(1):15–27, 2013. DOI: 10.3233/AIC-120543. **Полный текст НЕ открыт (пейвол).**
- Felfernig, A.; Mairitsch, M.; Mandl, M.; Schubert, M.; Teppan, E. **«Utility-Based Repair of
  Inconsistent Requirements».** IEA/AIE 2009, LNCS 5579, Springer, 2009.
  DOI: 10.1007/978-3-642-02568-6_17. **Полный текст НЕ открыт (Springer, пейвол).**
- Teppan, E.; Felfernig, A. **«Minimization of Product Utility Estimation Errors in Recommender
  Result Set Evaluations»** (ссылка [70] в Handbook ch. 5). **Не открыт.**

## 5.4. Дополнительная добыча по вопросу 5

Отдельный подагент отправлен на закрытие вопроса 5 по подпунктам: определение utility-based у Burke
(2002, UMUAI 12(4):331–370), условия аддитивной декомпозиции у Keeney & Raiffa, MAUT-based RS
(Manouselis & Costopoulou 2007, Adomavicius & Kwon 2007, Huang), обучение весов (UTA/UTASTAR
Jacquet-Lagrèze & Siskos 1982, conjoint analysis, Bayesian preference elicitation), критика
аддитивной полезности в RS.
**Его выписки — в отдельном файле:**
`/Users/vasyaevdokimov/repos/personal-finance-dss/docs/research/raw/_sub16_utility_based_rs.md`
Если файл отсутствует или помечен как неполный — подагент был оборван, и вопрос 5 закрыт только
в объёме §5.1–5.3 выше.

---

# 7. 🔴 ЧТО ЭТО ЗНАЧИТ ДЛЯ НАШЕГО УТВЕРЖДЕНИЯ О НОВИЗНЕ

**Короткий ответ: утверждение о новизне ПО МЕТОДУ и ПО ОБЪЯСНИМОСТИ в текущей формулировке
несостоятельно. Оба покрыты опубликованным, причём первоисточниками 2005–2008 годов из финансового
домена, а не отдалёнными аналогами.**

## 7.1. Поэлементная таблица покрытия

| № | Элемент конструкции FINPILOT | Покрыт? | Чем именно (точная ссылка) |
|---|---|---|---|
| 1 | Задача = CSP: переменные клиента + переменные продукта + ограничения | ✅ полностью | Felfernig, Friedrich, Jannach, Zanker, *Recommender Systems Handbook* 2nd ed., ch. 5, **Definition 5.1**, с. 165. Пример базы знаний — **инвестиционный советник** (Example 5.1, с. 163–164) |
| 2 | Конечное перечислимое множество альтернатив (наша решётка 66) | ✅ полностью | Uta et al., *Frontiers in Big Data* 7:1304439, 2024, **§3.1.1**: «Table-based representations can be applied if the set of offered items is limited … which is often the case, for example, in digital camera or **financial service recommendation**» |
| 3 | Отсечение жёсткими ограничениями до ранжирования | ✅ полностью | Uta et al. 2024, **Definition 2**: `consistent(C ∪ R ∪ a(iα))`; Handbook ch. 5, **Definition 5.2** («consistent recommendation … iff it does not violate any of the constraints») |
| 4 | Разделение «фильтрующие vs ранжирующие» правила | ✅ полностью, и у них ТОНЬШЕ | Handbook ch. 5, с. 162–163: три класса ограничений **CR / CF / CPROD**; ранжирование — отдельный слой (§«Ranking Items», с. 180) |
| 5 | **Аддитивная взвешенная свёртка выживших (наш SAW)** | ✅ **дословно та же формула** | Felfernig & Kiener, IAAI-05, с. 1480: «**g(x) = Σ(i=1..n) ei·si(x)**, where g(x) represents the utility of one solution x, ei represents the customer's interest in dimension i, and si is the contribution of solution x to dimension i». Плюс Uta et al. 2024 Eq. (2): `utility(iα) = Σ(d∈D) importance(d) × eval(iα, d)` |
| 6 | Имя приёма | ✅ есть устоявшееся | **«multi-attribute object rating»** (Felfernig & Kiener 2005, с. 1480); **«MAUT-based ranking»** (Handbook ch. 5, с. 180); в целом — **«constraint-based recommender cascaded with a utility-based item ranking scheme»** (Handbook ch. 5, с. 181) |
| 7 | Веса из дискретных риск-профилей | ✅ покрыто, и признано УПРОЩЕНИЕМ | В каноне `ei` — индивидуальные значения важности, извлекаемые в диалоге (Handbook ch. 5, с. 180; Uta et al. 2024 §3.3.1). Обучение весов из истории названо штатным приёмом (Handbook ch. 5, с. 181) |
| 8 | **Объяснение через вклад `w_k · x_k^norm`** | ✅ **опубликовано, есть имя** | Uta et al. 2024, **§4.5.5**, тип **«HOW explanation»**: «when using a utility-based approach for item ranking, explanations can take into account corresponding weights to explain how a recommendation has been determined». В проде с 2005 (FSAdvisor, с. 1480–1481) и 2007 (VITA, с. 1695, где MAUT-веса ещё и УПОРЯДОЧИВАЮТ объяснения) |
| 9 | Объяснимость как причина отказа от ML | ✅ ровно наш аргумент, опубликован в 2005 | Felfernig & Kiener 2005, с. 1476: «A customer's taste is not of primary concern in the financial services domain. **Recommendations must be correct and explainable**, i.e. Collaborative Filtering or Content-based Filtering approaches are not the best choices» |
| 10 | Регуляторная мотивация объяснимости | ✅ | Felfernig & Kiener 2005, с. 1476 (директивы ЕС о документировании консультаций) |
| 11 | min-max нормировка ВНУТРИ текущего множества альтернатив | ⚠️ **в этой школе не найдена** | В школе `eval(iα, d)` / `si(x)` — предзаданные оценочные таблицы (Uta et al. 2024, Table 10), нормировка относительно текущего множества нигде не описана. **Но это не новизна:** приём — стандарт MCDA (тема 15) |
| 12 | Лексикографический приоритет заполнения floor-резерва поверх свёртки | ⚠️ **в этой школе не найдено имени** | Ближайшее — приоритеты ограничений при релаксации в FSAdvisor (с. 1479: «constraints with a priority > 0 … are relaxed starting with constraints with lowest priority»), но это лексикография в направлении ПОСЛАБЛЕНИЯ, а не РАНЖИРОВАНИЯ. Лексикографическое предпочтение как таковое — учебник MCDA, не новое |
| 13 | Repair при пустом множестве | ❌ **у нас НЕТ**, у них ЕСТЬ с 1987 г. | Reiter 1987 (hitting sets), Junker 2004 (QuickXPlain), Uta et al. 2024 Def. 3–4, FSAdvisor с. 1480. **Это наш пробел, а не наша новизна** |

## 7.2. Что из этого следует прямо

**Умерло полностью:**
- «Новизна в методе: жёсткие инварианты + SAW-свёртка + профили весов». Это **constraint-based
  recommender с MAUT-ранжированием**, описанный и внедрённый в финансовых услугах в 2003–2007 гг.
  (FSAdvisor, VITA), формализованный в 2008 (Felfernig & Burke) и канонизированный в Handbook (2011,
  2015) и в обзоре 2024. Формула совпадает буквально.
- «Новизна в объяснимости через вклад критерия». Это **HOW-explanation при utility-based ranking**,
  опубликована в 2005–2007 и включена в типологию объяснений обзора 2024 (§4.5.5).

**Живо, но слабо (заявлять с осторожностью и без слова "впервые"):**
- **Объект рекомендации.** Во всех найденных финансовых применениях школы рекомендуется **продукт из
  ассортимента продавца** (кредиты, вклады, страховки, пенсионные), система обслуживает **агента по
  продажам**, а целевая функция завязана на конверсию. У FINPILOT объект — **распределение
  собственного свободного денежного потока клиента** между погашением, резервом и целями; продавца и
  ассортимента нет вовсе, конфликт интересов отсутствует по построению. Работы этой школы, где
  рекомендуемый объект — аллокация собственных средств пользователя, **в добытом массиве не найдены**.
- **Self-service против agent-assist.** FSAdvisor и VITA — инструменты для сотрудника, а не для
  конечного пользователя (VITA: «800 sales representatives»; FSAdvisor: «1400 sales representatives»).
- **Комбинация трёх слоёв одновременно** (лексикографический floor → SAW → объяснение вклада) —
  каждый слой известен по отдельности; их совмещение именем в этой школе не названо. Это тянет на
  «инженерное решение», а не на научную новизну.

**Ничего не осталось от формулировки «новизна по методу и объяснимости». Её надо переписать.**

## 7.3. Как честно переформулировать (варианты, не решение)

1. **По объекту оптимизации:** «перенос constraint-based + MAUT-конструкции с рекомендации продуктов
   финансового ассортимента на рекомендацию распределения собственного денежного потока
   домохозяйства». Слабое, но проверяемое.
2. **По инвариантам:** у школы ограничения — это предпочтения клиента (релаксируемые, Δ ⊆ R).
   У нас — **арифметическое тождество Rt≥0 и нормативный порог ПДН≤0.40**, которые нерелаксируемы
   в принципе. В школе такой случай (когда пусто из-за C, а не из-за R) канонических рецептов
   не имеет — см. §4.5. **Это единственный найденный настоящий методический зазор.**
3. **По аксиоматике:** школа применяет аддитивную свёртку, ни разу не проверив условия её законности
   (§5.2). Если FINPILOT такую проверку введёт явно — это заявляемый вклад, но вклад **методической
   строгости**, не новой конструкции.

---

# Что не добыто и почему (список закрытых источников)

| Источник | Канал | Результат |
|---|---|---|
| **Felfernig, A. & Burke, R. «Constraint-based recommender systems: technologies and research issues». ICEC '08, ACM, Innsbruck, 19.08.2008, pp. 17–26. DOI 10.1145/1409540.1409544** | `WebFetch` на `dl.acm.org/doi/pdf/…` | **HTTP 403 Forbidden** |
| То же | `curl` с браузерным UA | **HTTP 403**, отдана HTML-заглушка 5750 байт вместо PDF (антибот ACM) |
| 🔴 **Следствие:** первоисточник, вокруг которого построена вся тема, **не прочитан в оригинале**. Всё, что о нём сказано в файле, снято с его канонических пересказов теми же авторами (Handbook ch. 5, 2015; Uta et al. 2024) — они полны и внутренне согласованы, но это **не** оригинал ICEC '08 | | |
| Felfernig et al. «Intelligent debugging and repair of utility constraint sets…», IUI '08, ACM | ACM DL | **403** (не пробовал повторно — тот же домен) |
| Felfernig et al. «Automated repair of scoring rules in constraint-based recommender systems», *AI Communications* 26(1):15–27, 2013 | поисковая выдача | **Пейвол** (SAGE/IOS Press). В файле — только пересказ аннотации, помечен как пересказ |
| Felfernig et al. «Utility-Based Repair of Inconsistent Requirements», IEA/AIE 2009, LNCS 5579 | Springer Link | **Пейвол** |
| Felfernig, Schubert «FastDiag: A Diagnosis Algorithm for Inconsistent Constraint Sets» | `curl` на `felfernig.sai.tugraz.at/wp-content/uploads/2021/03/fastdiag.pdf` | **HTTP 200, но файл пустой** (`inode/x-empty`, 0 байт); `ke.tuwien.ac.at` — код **000** (домен не резолвится) |
| Reiter, R. «A theory of diagnosis from first principles», *Artificial Intelligence*, 1987 | не открывался | Цитируется только через вторичные источники. **Расхождение в томе:** FSAdvisor даёт «23(1):57–95», общепринятая ссылка — «32(1):57–95». Не сверено |
| Junker, U. «QUICKXPLAIN», AAAI-04, pp. 167–172 | не открывался | Цитируется через вторичные источники |
| Keeney & Raiffa (1976/1993) | вынесено подагенту | См. `_sub16_utility_based_rs.md` |
| Semantic Scholar API | `curl` | **HTTP 429 Too Many Requests** (без API-ключа) |

**Каналы, которые сработали (для будущих тем):**
`WebFetch` на PDF → файл кладётся в `~/.claude/projects/**/tool-results/*.pdf`, путь печатается →
`pdftotext <путь> <выход>` (сработало на `cdn.aaai.org`).
`curl -sL -A "<браузерный UA>" -o <файл> <URL>` + `pdftotext` — сработало на `cdn.aaai.org` и
`web-ainf.aau.at` (авторское зеркало Яннаха: там лежат ОБА издания главы Handbook, 2011 и 2015).
`curl` + питоновский стриппер HTML-тегов — сработало на `frontiersin.org`, где `WebFetch`
возвращал только пересказ вместо полного текста.

---

# Прямые следствия для FINPILOT

## Подтверждено (можно опираться, есть ссылка)

1. **Выбор класса системы правильный и обоснован в литературе для нашего домена.**
   Uta et al. 2024, §1: KBR-системы применимы именно в «high-involvement item domains … for example,
   when investing in high-risk financial services»; финансовые услуги названы первым примером.
2. **Отказ от CF/ML в пользу explainable-подхода — не наша прихоть, а опубликованный довод школы**
   (Felfernig & Kiener 2005, с. 1476). Это готовый абзац в обоснование архитектуры.
3. **Экономический эффект такого класса систем в финансах измерен и положителен:** VITA — экономия
   13.3% времени консультации (t = 11.84, p < 0.0001), рост продаж поддержанных продуктов ~50%
   (t = 9.59, p < 0.0001), окупаемость €100 000 за год (Felfernig et al. 2007, с. 1697–1698).
4. **Малое перечислимое множество альтернатив — законный инженерный выбор**, а не слабость:
   «Table-based representations can be applied if the set of offered items is limited» (Uta et al.
   2024, §3.1.1).

## Опровергнуто (надо снять из формулировок)

1. **«Новизна в методе».** Конструкция названа, формализована, внедрена и измерена задолго до нас.
2. **«Новизна в объяснимости через вклад критерия».** Это HOW-explanation, канон с 2005–2007.
3. **«Аддитивная свёртка — очевидно корректный способ ранжирования».** Школа сама показала, что
   при малом числе ограничений и больших результирующих множествах «**the ranking function is not
   always able to identify the best matching items**», и что лучше всего работает каскад
   «knowledge-based отсекает — обучаемый алгоритм ранжирует» (Handbook ch. 5, с. 182).
4. **«Фиксированные веса профиля — норма».** В каноне веса индивидуальны и могут обучаться из
   истории (Handbook ch. 5, с. 181); наш вариант — упрощение, которое надо защищать, а не выдавать
   за особенность.

## Порождённые задачи (конкретные, по убыванию важности)

1. 🔴 **Спроектировать поведение при пустом множестве альтернатив.** Сейчас Rt≥0 и ПДН≤0.40 могут
   отсечь всё, и продукт молчит. Каноническая схема — двухступенчатая (FSAdvisor, с. 1479):
   (а) релаксация по приоритетам того, что релаксируемо; (б) если остались только нерелаксируемые —
   вычисление **минимального repair входных данных** (Reiter hitting sets), с сортировкой вариантов
   по нашей же полезности («repair actions with the highest probability of being accepted … are
   presented first», VITA с. 1695). У нас релаксировать инварианты нельзя — значит, работать надо
   с входом (цели, сроки, суммы взносов), и это ровно «Personalized Repair Proposals».
2. 🔴 **Ввести WHY-NOT объяснение.** Uta et al. 2024, §4.5.5: диагноз — это и есть объяснение
   отсутствия решения. Пользователю говорится не «нет вариантов», а «конфликтуют вот эти два ваших
   входных условия, ослабьте одно из двух».
3. 🟡 **Переписать заявление о новизне** по §7.3 — сдвинуть его с метода на объект оптимизации и на
   нерелаксируемость инвариантов; слово «впервые» убрать.
4. 🟡 **Проверить условия аддитивной декомпозиции** для наших четырёх критериев (§5.2). Школа этого
   не делает — если сделаем мы, это добавляет строгости и закрывает очевидный вопрос рецензента
   «почему сумма, а не что-то другое».
5. 🟡 **Признать и задокументировать риск «faulty scoring rules».** У школы есть целая линия работ
   о том, что веса utility-функции на практике неверны и требуют починки (§5.3). Наши пять профилей
   — ровно такой набор весов, никем не откалиброванный. Нужен план калибровки или явная оговорка.
6. 🟢 **Ввести MAUT-упорядочивание объяснений** (VITA, с. 1695): показывать первым то объяснение,
   которое относится к самому важному для профиля критерию. Дёшево, даёт заметный эффект восприятия.
7. 🟢 **Добавить «tips»** — мягкий класс правил, который не отсекает и не ранжирует, а подсказывает
   (FSAdvisor, с. 1479–1480). У нас аналог: «резерв на 3 месяца снижает риск срыва плана сильнее,
   чем досрочное погашение по низкой ставке».

---

# 5-БИС. Utility-based RS — сводка добычи подагента (полное сырьё в отдельном файле)

**Полные дословные выписки:**
`/Users/vasyaevdokimov/repos/personal-finance-dss/docs/research/raw/_sub16_utility_based_rs.md`
(553 строки, 41 КБ). Ниже — только то, что меняет выводы по теме 16; остальное не дублирую.

## 5б.1. Burke: utility-based — ЧАСТНЫЙ СЛУЧАЙ knowledge-based

Burke, R. **«Hybrid Recommender Systems: Survey and Experiments»**, *User Modeling and
User-Adapted Interaction* 12(4), 2002, 331–370 (добыт авторский препринт), дословно, §1.1:

> «**Utility-based recommenders make suggestions based on a computation of the utility of each
> object for the user. Of course, the central problem is how to create a utility function for each
> user.** […] **The user profile therefore is the utility function that the system has derived for
> the user, and the system employs constraint satisfaction techniques to locate the best match.**»

🔴 Обратите внимание: **уже в определении Burke 2002 сшиты обе половины нашей конструкции** —
utility-функция как профиль пользователя ПЛЮС constraint satisfaction для поиска допустимого.

Дословно, §3 (перед Table IV):

> «For the sake of simplicity, the table combines knowledge-based and utility-based techniques
> (**since utility-based recommendation is a special case of knowledge-based**).»

Это снимает расхождение, зафиксированное в §5.1 выше: VITA (2007) приписала Burke отнесение MAUT
к content-based — по первоисточнику 2002 г. это неверно, у Burke utility-based подчинён
knowledge-based.

## 5б.2. Burke о цене фиксированных весов — прямо про наши пять риск-профилей

Дословно (препринт, с. 4):

> «**The flexibility of utility-based systems is also to some degree a failing. The user must
> construct a complete preference function, and must therefore weigh the significance of each
> possible feature. Often this creates a significant burden of interaction.** Tête-à-Tête **uses a
> small number of "stereotype" preference functions to get the user started**, but ultimately the
> user needs to look at, weigh, and select a preference function for each feature […]»

🔴 **«Небольшое число стереотипных функций предпочтения, чтобы стартовать» — это буквально описание
наших пяти риск-профилей, опубликованное в 2002 году как известный приём (Tête-à-Tête).**
И там же — почему этого мало: пользователь всё равно должен потом взвешивать сам.

Дословно (с. 5):

> «Utility- and knowledge-based systems have fewer problems in this regard because they do not rely
> on having historical data about a user's preferences. **Utility-based systems may present
> difficulties for casual users who might be unwilling to tailor a utility function simply to browse
> a catalog.**»

## 5б.3. 🔴 УСЛОВИЕ ЗАКОННОСТИ АДДИТИВНОЙ СВЁРТКИ — теорема, и она бьёт по SAW

Из добытого учебного изложения MAUT (см. `_sub16_utility_based_rs.md` §2.5 с точной локализацией
источника), дословно:

> «**Definition (Additive Independence (AI)).** Attributes X₁, X₂, …, Xₙ are additive independent if
> preferences over lotteries on X₁, X₂, …, Xₙ depend only on their **marginal** probability
> distributions and not on their **joint** probability distribution.»

> «The n-attribute additive utility function u(x) = Σᵢ kᵢ·uᵢ(xᵢ) **is appropriate if and only if the
> additive independence condition holds** among attributes X₁, X₂, …, Xₙ»

Смысл параметра взаимодействия, дословно:

> «**Interpretation of Parameter k.** … k > 0: Y and Z are complements; k = 0: no interaction of
> preference; k < 0: Y and Z are substitutes.»

🔴 **Прямое следствие для FINPILOT.** Наша SAW-свёртка по четырём критериям (ресурс, ликвидность,
долг, продвижение целей) законна **тогда и только тогда**, когда между этими критериями нет
взаимодействия предпочтений. Но предметная область говорит об обратном: ценность «продвижения
целей» для человека **зависит** от того, набран ли резерв ликвидности (именно поэтому у нас и стоит
лексикографический floor-приоритет!). То есть **мы сами, вводя лексикографический floor, признали,
что additive independence нарушена** — и при этом всё равно ранжируем аддитивно внутри.

Важно, что **школа Фельферниг эту проверку не делает вообще** (§5.2 выше: Keeney & Raiffa в
библиографии главы Handbook отсутствуют, условия независимости не упоминаются ни в одной из
добытых работ школы). Порядок работ по каноническому MAUT, дословно:

> «Assessment Procedure for Multiattribute Utility Functions: 1. Introducing the terminology and
> ideas. **2. Identifying relevant independence assumptions.** 3. Assessing conditional utility
> functions or isopreference curves. 4. Assessing the scaling constants. 5. Checking for consistency
> and reiterating.»

Шаг 2 идёт ДО оценивания весов — и в типовом инженерном применении SAW пропускается.

## 5б.4. Обучение весов вместо фиксированных профилей — канонический ответ найден

Дословно (Adomavicius, Manouselis, Kwon, глава о multi-criteria RS; локализация — с. 28,
см. под-файл §4.1):

> «**Preference disaggregation methods could support the implicit formulation of a preference model
> based on a series of previous decisions. A characteristic example is the UTA (i.e., UTilités
> Additive) method, which can be used to extract the utility function from a user-provided ranking
> of known items** (Lakiotaki et al. 2008).»

Первоисточник UTA: Jacquet-Lagrèze, E. & Siskos, J. «Assessing a set of additive utility functions
for multicriteria decision-making: the UTA method», *EJOR* 10(2), 1982, 151–164.
**Дословно не добыт** (Elsevier, платно).

🔴 **Практический выход:** есть готовый канонический механизм заменить наши фиксированные веса —
попросить пользователя **проранжировать несколько знакомых сценариев** и восстановить веса
ordinal-регрессией (UTA), а не спрашивать веса напрямую. Это снимает возражение Burke о «burden of
interaction» и одновременно даёт персонализацию.

## 5б.5. Что подагент НЕ закрыл

- **§5 «Критика аддитивной полезности в RS»** — остался пустым (`в работе`), бюджет ушёл на
  подпункты 1–3. Частично закрыто из моих источников: §6.2 главного файла (ранжирующая функция
  knowledge-based уступает CF по точности) и §5.3 (линия работ Фельферниг о «faulty scoring rules»).
- **Conjoint analysis, Bayesian preference elicitation (Boutilier)** — не добыто.
- **Детерминированный случай** (аддитивная *value* function, Debreu 1960 / Keeney & Raiffa гл. 3:
  аддитивность ⟺ взаимная преференциальная независимость при n ≥ 3) — дословно из первоисточника
  не добыт, только косвенно.
- **Jacquet-Lagrèze & Siskos 1982** — пейвол Elsevier.

## 5б.6. Дополнение к §7 (новизна) по итогам этой добычи

Строка 7 таблицы §7.1 («веса из дискретных риск-профилей») усиливается:
приём **назван и опубликован в 2002 году** — Burke описывает «a small number of *stereotype*
preference functions» у Tête-à-Tête (Burke 2002, препринт с. 4). Наши пять риск-профилей —
это стереотипные функции предпочтения, ровно в этом смысле.

Появляется **новый пункт покрытия**, которого не было в таблице:

| № | Элемент | Покрыт? | Чем |
|---|---|---|---|
| 14 | Связка «utility-функция как профиль пользователя + constraint satisfaction для поиска допустимого» | ✅ **это определение класса** | Burke 2002, §1.1: «The user profile therefore is the utility function … and the system employs constraint satisfaction techniques to locate the best match» |
| 15 | Стереотипные наборы весов вместо индивидуальной настройки | ✅ | Burke 2002, с. 4 (Tête-à-Tête, «a small number of stereotype preference functions») |

И **новый пункт в «порождённые задачи»**, по важности сразу за repair:

> 🔴 **Проверить additive independence для наших четырёх критериев — или честно отказаться от
> чистой аддитивности.** Мы сами де-факто признали её нарушение, введя лексикографический
> floor-приоритет резерва. Варианты: (а) документировать floor как явную поправку на нарушение AI;
> (б) перейти к мультипликативной форме при mutual utility independence; (в) оставить SAW,
> но записать нарушение AI в раздел ограничений модели. Молчать об этом — самый слабый вариант:
> это первый вопрос, который задаст рецензент, знакомый с Keeney & Raiffa.

## 5б.7. Дополнение: подагент дописал §5 (критика) и §2 (иерархия условий). Существенное

Подагент завершил работу; его файл вырос до 702 строк / 44 КБ. Локализация всех цитат ниже —
в `_sub16_utility_based_rs.md`, §2.4–2.8, §3, §5.

**(а) 🔴 Mutual utility independence даёт МУЛЬТИЛИНЕЙНУЮ, а не аддитивную форму.**
Аддитивная — частный случай при `k = 0`. Эквивалентность «аддитивная свёртка ⟺ условие»
держится **только** на additive independence, а не на более слабой преференциальной или
взаимной utility-независимости. Иерархия: **UI ⇒ PI**, обратное неверно.

**(б) Детерминированный случай (аддитивная *value* function, без лотерей) имеет ОТДЕЛЬНУЮ ловушку.**
Требуется взаимная преференциальная независимость **и n ≥ 3 существенных атрибутов** (Debreu 1960).
**При n = 2 этого недостаточно — нужно условие Томсена.** У FINPILOT четыре критерия, так что
n ≥ 3 выполняется; но проверять взаимную преференциальную независимость всё равно надо.
(Добыто через вторичные источники, дословно из Debreu/Keeney & Raiffa — не добыто.)

**(в) 🔴 Каноническая иллюстрация компенсаторности — дословно**
(Adomavicius, Manouselis, Kwon, «Multi-Criteria Recommender Systems», *Recommender Systems
Handbook*, авторская копия https://ise.bgu.ac.il/faculty/liorr/recsyshb/chmulticriteria.pdf,
с. 24–25):

> «**However, without an overall rating the recommendation process becomes more complex, because it
> is less apparent how to establish the total order of the items.** For example, suppose that we
> have a two-criterion movie recommender system, where users judge movies based on their story
> (i.e., plot) and visual effects. Further, suppose that one movie needs to be chosen for
> recommendation among the following two alternatives: (i) movie X, predicted as 8 in story and 2
> in visuals, and (ii) movie Y, predicted as 5 in story and 5 in visuals. **Since there is no
> overall criterion to rank the movies, it is not easy to judge which movie is better, unless some
> other modeling approach is adopted** […] Several approaches have been proposed […]: some try to
> design a total order on items and obtain a single global optimal solution for each user, whereas
> others take the existing partial order of the items and **find multiple (Pareto optimal)
> solutions**.»

**Прямой аналог у нас:** распределение с сильным перекосом в одну цель и сбалансированное могут
получить одинаковый SAW-балл. Аддитивная свёртка эту разницу стирает по построению.

**(г) Готовые НЕКОМПЕНСАТОРНЫЕ заменители в том же классе моделей — дословно** (там же, с. 17):

> «• Average similarity: sim_avg(u, u′) = (1/(k+1)) Σ sim_c(u, u′)
> • Aggregate similarity: sim_aggregate(u, u′) = Σ w_c · sim_c(u, u′)
> • **Worst-case (smallest) similarity: sim_min(u, u′) = min_{c=0..k} sim_c(u, u′)**»
> «• Manhattan distance … • Euclidean distance … • **Chebyshev (or maximal value) distance:
> max_{c=0..k} |R_c(u,i) − R_c(u′,i)|**»

То есть **min-агрегация и метрика Чебышёва — штатные некомпенсаторные альтернативы линейной
свёртке внутри той же школы**, а не экзотика из MCDA.

**(д) 🔴 КАЛИБР ЭФФЕКТА мультикритериальности — единицы процентов, не разы.**
По той же главе: мультикритериальные схемы бьют однокритериальный CF-baseline на
**0.3–6.3% precision-in-top-N**. Это ориентир, на который стоит рассчитывать, планируя
доказательство ценности нашей четырёхкритериальной свёртки.

**(е) Требование к семейству критериев, которым в RS-литературе пренебрегают** (дословно, с. 5):
семейство критериев должно быть **consistent family**: *monotonic*, *exhaustive*, *non-redundant*.
Авторы главы прямо признают, что в RS этим пренебрегают. Для нас это конкретная проверка:
не избыточны ли «ресурс» и «ликвидность» относительно друг друга, исчерпывающи ли четыре критерия.

**(ж) Табличная характеристика utility-based у Burke 2002 (Table I / Table II), дословные пункты:**
вход метода — **сама функция полезности** («User must input utility function», минус O), и
«**Suggestion ability static (does not learn)**» (минус P). Второе — прямое описание нашей
конструкции с пятью фиксированными профилями: она не учится, и это зафиксированный в каноне
недостаток класса, а не наша особенность.

## 5б.8. Дополнение к «порождённым задачам»

> 🟡 **Проверить consistent family of criteria** (monotonic / exhaustive / non-redundant) для
> наших четырёх критериев — дешёвая проверка, прямо названная в каноне как пропускаемая всеми.

> 🟡 **Рассмотреть некомпенсаторный режим ранжирования** (min-агрегация или Чебышёв) хотя бы как
> опциональный «консервативный» профиль. Это не изобретение: обе схемы перечислены в каноне
> мультикритериальных RS наравне со взвешенной суммой.

> 🟡 **Заложить реалистичный калибр эффекта.** Ожидать от мультикритериальности единицы процентов
> прироста качества против однокритериального baseline, а не кратный выигрыш.

---

**Конец файла. Тема 16 закрыта по вопросам 1, 2, 3, 4, 5, 6, 7.**
Непрочитанным остался ОРИГИНАЛ Felfernig & Burke (ICEC '08) — ACM 403 на оба канала;
компенсировано каноническими пересказами тех же авторов (Handbook ch. 5; Uta et al. 2024).
Остальные закрытые источники перечислены в разделе «Что не добыто и почему».
