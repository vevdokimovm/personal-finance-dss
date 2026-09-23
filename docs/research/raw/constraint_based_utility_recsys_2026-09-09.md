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

---

# ДОБОР Г4 (11.09.2026) — первоисточники под repair при пустом множестве альтернатив

Метод: первоисточники добывались полными текстами, не пересказами. Канал, HTTP-код и размер
указаны у каждого источника. Цитаты дословные, с номером страницы по колонтитулу самого PDF.

## ДОБОР Г4 — Junker U., QUICKXPLAIN (AAAI-04), ПОЛНЫЙ ТЕКСТ ДОБЫТ

**Реквизиты (подтверждены по самому PDF):** Ulrich Junker, ILOG, 1681 route des Dolines,
06560 Valbonne, France, ujunker@ilog.fr. «QUICKXPLAIN: Preferred Explanations and Relaxations
for Over-Constrained Problems». Proceedings of AAAI-04, секция CONSTRAINT SATISFACTION &
SATISFIABILITY, **страницы 167–172** (колонтитулы страниц в PDF: 167, 168, 169, 170, 171, 172).
Copyright © 2004, American Association for Artificial Intelligence.

**Канал добычи:**
1. `curl -sk --http1.1` с браузерным UA → `https://cdn.aaai.org/AAAI/2004/AAAI04-000.pdf`
   (оглавление тома) — **HTTP 200, 651 085 байт**, 12 страниц. В оглавлении строка
   «QUICKXPLAIN: Preferred Explanations and Relaxations for Over-Constrained Problems / 167,
   Ulrich Junker». Номер статьи в томе вычислен подсчётом позиции в оглавлении (27-я
   техническая статья).
2. `curl -sk --http1.1` → `https://cdn.aaai.org/AAAI/2004/AAAI04-027.pdf` — **HTTP 200,
   115 902 байта**. Проверено: первая строка текста — «QUICKXPLAIN: Preferred Explanations
   and Relaxations for Over-Constrained Problems, Ulrich Junker, ILOG». Совпадение
   подтверждено; соседние номера 026 (Fang & Ruml) и 028 (Mastrolilli & Gambardella)
   совпали с оглавлением, то есть нумерация проверена с двух сторон.
3. Текст извлечён `pdftotext -layout` — 44 258 байт. **ACM DL / ResearchGate не
   понадобились вовсе.**

🔴 **Опровержение вторичных источников по реквизитам:** страницы **167–172** подтверждены
первоисточником; том AAAI-04, издатель AAAI Press. Никакого «AAAI/IAAI 2004, pp. 167–172,
Vol. 3» в самом PDF нет — в колонтитулах только имя секции и сквозная нумерация тома.

### Постановка задачи (дословно, с. 167)

> «Over-constrained problems can have an exponential number of conflicts, which explain
> the failure, and an exponential number of relaxations, which restore the consistency.
> A user of an interactive application, however, desires explanations and relaxations
> containing the most important constraints. To address this need, we define preferred
> explanations and relaxations based on user preferences between constraints and we compute
> them by a generic method which works for arbitrary CP, SAT, or DL solvers. We significantly
> accelerate the basic method by a divide-and-conquer strategy and thus provide the
> technological basis for the explanation facility of a principal industrial constraint
> programming tool, which is, for example, used in numerous configuration applications.»
> (Abstract, с. 167)

**Ведущий пример (с. 167) — прямая аналогия нашему случаю.** Покупатель хочет универсал
с опциями при бюджете 3000:

| № | Опция | Требование ρi | Стоимость |
|---|---|---|---|
| 1 | roof racks | x1 = 1 | k1 = 500 |
| 2 | CD-player | x2 = 1 | k2 = 500 |
| 3 | one additional seat | x3 = 1 | k3 = 800 |
| 4 | metal color | x4 = 1 | k4 = 500 |
| 5 | special luxury version | x5 = 1 | k5 = 2600 |

«where the boolean variable xi ∈ {0,1} indicates whether the i-th option is chosen and the
costs y = Σ ki·xi are smaller than the total budget of 3000» (с. 167). Наивное распространение
границ даёт конфликт {ρ1..ρ5} — весь набор; минимальный конфликт — {ρ4, ρ5} (таблица 2);
**предпочтительный** конфликт при порядке ρ3 ≺ ρ1 ≺ ρ2 ≺ ρ5 ≺ ρ4 — {ρ3, ρ5} (таблица 3).

Ключевая формулировка проблемы (с. 167, правая колонка):

> «Hence, the essential issue in explaining a failure of a constraint solver is not the
> capability of recording a proof, but selecting a proof among a potentially huge number
> that does not contain unnecessary constraints and that involves the most preferred
> constraints.»

Принцип алгоритма одним абзацем (с. 168, левая колонка):

> «We address this issue by a preference-controlled algorithm that successively adds most
> preferred constraints until they fail. It then backtracks and removes least preferred
> constraints if this preserves the failure. Relaxations can be computed dually, first
> removing least preferred constraints from an inconsistent set until it is consistent.
> The number of consistency checks can drastically be reduced by a divide-and-conquer
> strategy that successively decomposes the overall problem. In the good case, a single
> consistency check can remove all the constraints of a subproblem.»

### Условия применимости (дословно, с. 168)

> «Although the discussion of this paper focuses on constraint satisfaction problems (CSP),
> its results and algorithms apply to any satisfiability problem such as propositional
> satisfiability (SAT) or the satisfiability of concepts in description logic (DL). We
> completely abstract from the underlying constraint language and simply assume that there
> is a monotonic satisfiability property: if S is a solution of a set C1 of constraints
> then it is also a solution of all subsets C2 of C1.»

🔴 **Единственное требование к предметной области — МОНОТОННОСТЬ выполнимости.** Для
FINPILOT это проверяемо напрямую: инварианты Rt ≥ 0 и ПДН ≤ 0,40 монотонны по удалению
пользовательских требований (сняли требование — множество решений не сужается), значит
QuickXplain применим без адаптации.

**Разделение на фон и требования (с. 168):**

> «If a set of constraints has no solution, some constraints must be relaxed to restore
> consistency. It is convenient to distinguish a background B containing the constraints
> that cannot be relaxed. Typically, unary constraints x ∈ D between a variable x and a
> domain D will belong to the background. In interactive problems, only user requirements
> can be relaxed, leaving all other constraints in the background.»

### Определения (дословно, с. 168)

- **Definition 1** (с. 168): «A subset R of C is a relaxation of a problem P := (B, C) iff
  B ∪ R has a solution.» — «A relaxation exists iff B is consistent.»
- **Definition 2** (с. 168): «A subset C of C is a conflict of a problem P := (B, C) iff
  B ∪ C has no solution.» — «A conflict exists iff B ∪ C is inconsistent.»
- **Definition 3** (лексикографическое расширение, с. 168): «Given a total order < on C,
  we enumerate the elements of C in increasing <-order c1, …, cn starting with the most
  important constraints (i.e. ci < cj implies i < j) and compare two subsets X, Y of C
  lexicographically:
  X <lex Y **iff** ∃k : ck ∈ X − Y and X ∩ {c1, …, ck−1} = Y ∩ {c1, …, ck−1}»   (формула (1))
- **Definition 4** (с. 168): «Let P := (B, C, <) be a totally ordered problem. A relaxation R
  of P is a preferred relaxation of P iff there is no other relaxation R* of P s.t. R* <lex R.»
- **Definition 5** (с. 168): «Let P := (B, C, ≺) be a partially ordered problem. A relaxation R
  of P is a preferred relaxation of P iff there is a linearization < of ≺ s.t. R is a preferred
  relaxation of (B, C, <).»
- **Definition 6** (антилексикографический порядок, с. 169): «…compare X and Y lexicographically
  in the reverse order: X <antilex Y **iff** ∃k : ck ∈ Y − X and X ∩ {ck+1, …, cn} =
  Y ∩ {ck+1, …, cn}»   (формула (2))
- 🔴 **Definition 7 — PREFERRED CONFLICT, дословно (с. 169):** «Let P := (B, C, <) be a totally
  ordered problem. A conflict C of P is a **preferred conflict** of P iff there is no other
  conflict C* of P s.t. C* <antilex C.»
- **Definition 8** (с. 169): «Let P := (B, C, ≺) be a partially ordered problem. A conflict C
  of P is a preferred conflict of P iff there is a linearization < of ≺ s.t. C is a preferred
  conflict of (B, C, <).»

**Свойства предпочтительного конфликта (с. 169, дословно):**

> «A preferred conflict C is minimal (irreducible) meaning that each proper subset of C has
> a solution. If no preferences are given (≺ is empty), then the minimal conflicts and the
> preferred conflicts coincide. If ≺ is a strict total order and B ∪ C is inconsistent, then
> P has a unique preferred conflict.»

И симметрично для релаксации (с. 168): «A preferred relaxation R is maximal (non-extensible)
meaning that each proper superset of R has no solution. If no preferences are given, i.e. ≺ is
the empty relation, then the maximal relaxations and the preferred relaxations coincide. If ≺
is a strict total order and B is consistent, then P has a unique preferred relaxation.»

🔴 **Это прямо отвечает на вопрос бэклога.** «Предложить, что ослабить» = вычислить
**preferred relaxation**; «объяснить, какие требования конфликтуют» = вычислить
**preferred conflict**. При СТРОГОМ ТОТАЛЬНОМ порядке требований и то и другое **единственно** —
то есть продукт не обязан показывать пользователю выбор из множества объяснений, если
приоритеты требований заданы линейно. Это снимает ложную развилку UX.

**Propositions (с. 169, дословно):**
- **Proposition 1:** «Let C be a conflict for a CSP P := (∅, C, ≺). If C is a minimal conflict
  of P, then the constraint graph of C consists of a single strongly connected component.»
- **Proposition 2:** «X <antilex Y iff Y (<⁻¹)lex X.»
- **Proposition 3:** «Let ¬cj ≺' ¬ci iff ci ≺ cj. R is a preferred relaxation (conflict) of
  (B, C, ≺) iff {¬c | c ∈ C − C} is a preferred conflict (relaxation) of (¬B, {¬c | c ∈ C}, ≺').»
- **Proposition 4:** «If C is a preferred conflict of P := (B, C, <) and R is a preferred
  relaxation of P, then the <-minimal element of C − R is equal to the <-maximal element of C.»
- **Proposition 5** (с. 170): «Let P := (B, C, ≺). If B is inconsistent then the empty set is
  the only preferred conflict of P and P has no relaxation. If B ∪ C is consistent then C is
  the only preferred relaxation of P and P has no conflict.»
- **Proposition 6** (с. 170): «Suppose C1 and C2 are disjoint and that no constraint of C2 is
  preferred to a constraint of C1: **1.** If ∆1 is a preferred relaxation of (B, C1, ≺) and ∆2
  is a preferred relaxation of (B ∪ ∆1, C2, ≺), then ∆1 ∪ ∆2 is a preferred relaxation of
  (B, C1 ∪ C2, ≺). **2.** If ∆2 is a preferred conflict of (B ∪ C1, C2, ≺) and ∆1 is a preferred
  conflict of (B ∪ ∆2, C1, ≺), then ∆1 ∪ ∆2 is a preferred conflict of (B, C1 ∪ C2, ≺).»

### Конструктивные определения (с. 169, дословно)

Предпочтительная релаксация, R0 := ∅ и
```
Ri := Ri−1 ∪ {ci}   if B ∪ Ri−1 ∪ {ci} has a solution
      Ri−1          otherwise
```
Предпочтительный конфликт строится в обратном порядке, Cn := C и
```
Ci := Ci+1 − {ci}   if B ∪ Ci+1 − {ci} has no solution
      Ci+1          otherwise
```

### 🔴 ПСЕВДОКОД АЛГОРИТМА ДОСЛОВНО (Figure 1, с. 170)

```
Algorithm QUICKXPLAIN(B, C, ≺)
  1.  if isConsistent(B ∪ C) return 'no conflict';
  2.  else if C = ∅ then return ∅;
  3.  else return QUICKXPLAIN'(B, B, C, ≺);

Algorithm QUICKXPLAIN'(B, ∆, C, ≺)
  4.  if ∆ ≠ ∅ and not isConsistent(B) then return ∅;
  5.  if C = {α} then return {α};
  6.  let α1, …, αn be an enumeration of C that respects ≺;
  7.  let k be split(n) where 1 ≤ k < n;
  8.  C1 := {α1, …, αk} and C2 := {αk+1, …, αn};
  9.  ∆2 := QUICKXPLAIN'(B ∪ C1, C1, C2, ≺);
 10.  ∆1 := QUICKXPLAIN'(B ∪ ∆2, ∆2, C1, ≺);
 11.  return ∆1 ∪ ∆2;
```
(Figure 1: Divide-and-Conquer for Explanations, с. 170)

**Theorem 1 (с. 170, дословно):** «The algorithm QUICKXPLAIN(B, C, ≺) always terminates.
If B ∪ C has a solution then it returns 'no conflict'. Otherwise, it returns a preferred
conflict of (B, C, ≺).»

### 🔴 СЛОЖНОСТЬ — Table 4, с. 171, ДОСЛОВНО

Единица измерения — **число проверок консистентности** (не операций). n — число ограничений,
k — размер предпочтительного конфликта.

| Method | Split | Best Case | Worst Case |
|---|---|---|---|
| 1. | split(n) = n/2 | log (n/k) + 2k | 2k · log (n/k) + 2k |
| 2. | split(n) = n − 1 | 2k | 2n |
| 3. | split(n) = 1 | k | n + k |

(Table 4: Number of Consistency Checks, с. 171)

🔴 **Числовой ориентир из самого текста (с. 170, дословно):** «For problems with one million
of constraints, QUICKXPLAIN thus needs between 33 and 270 checks if the conflict contains
8 elements.» Проверено арифметикой при n = 10⁶, k = 8: log₂(n/k) = log₂(125000) ≈ 16,93;
16,93 + 16 ≈ 33 (лучший случай); 16 · 16,93 + 16 ≈ 287, в тексте 270 — порядок совпадает,
автор округлял. **Число 33 и 270 брать из первоисточника как есть.**

Пояснение структуры вызовов (с. 170, дословно): «If no pruning (line 4) occurs, then the call
graph is a binary tree containing a leaf for each of the n constraints. This tree has 2n − 1
nodes.» И про выбор split: «If we choose split(n) := n/2 then subproblems are divided into
smaller subproblems of same size and a path from the root to a leaf contains log n nodes.
If the preferred conflict has k elements, then the non-pruned tree is formed of the k paths
from the root node to the k leaves of those elements. In the best case, all k elements belong
to a single subproblem that has 2k − 1 nodes… This path has the length log n − log k = log n/k.
In the worst case, the paths join in the top in a subtree of depth log k.»

Для строк 2 и 3 таблицы (с. 170): «For lines 2 and 3, the shortest path has length 1, but the
longest one has length n.»

**Бенчмарк-пример 2 (с. 170, дословно):** «As a simple benchmark problem, we consider n boolean
variables, a background constraint Σ ki·xi < 3n (with ki = n for i = 9, 10, 12 and ki = 1
otherwise) and n constraints xi = 1. The algorithm introduces the constraints for i = 1, …, 12,
then switches over to a removal phase.»

### Практические оговорки самого автора (с. 171, дословно) — важнее всего для продукта

**1. Неполный проверяльщик даёт НЕминимальный конфликт:**
> «Secondly, a correct, but incomplete method can be used for consistency checking. An arc
> consistency based solver has these properties. Another example is tree search that is
> interrupted after a limited amount of time. If such a method reports false, QUICKXPLAIN
> knows that there is a failure and proceeds as usual. Otherwise, QUICKXPLAIN has no precise
> information about the consistency of the problem and does not remove constraints. As a
> consequence, **it always returns a conflict, but not necessarily a minimal one.** Hence,
> there is a trade-off between optimality of the results and the response time.»

Там же ранее (с. 169): «Incomplete checkers can provide non-minimal conflicts».

**2. Ранняя остановка допустима:**
> «Firstly, QUICKXPLAIN can be stopped when it has found the k worst elements of a preferred
> conflict, which is sometimes sufficient.»

**3. Время ответа полиномиально только для полиномиальных CSP (Conclusion, с. 172):**
> «QUICKXPLAIN has a polynomial response time for polynomial CSPs. For other problems,
> multiple searches through similar search spaces are needed. Search overhead can be avoided
> by maintaining witnesses for the success and failure of previous consistency checks.»

**4. Свидетели успеха и провала** (с. 171): «This analysis shows that QUICKXPLAIN does not
need to start a search from scratch for each consistency check, but can profit from witnesses
for failure and success. The witness of success guides a least-commitment strategy that tries
to prove consistency, whereas a first-fail strategy is guided by a witness of failure and
tries to prove inconsistency.»

**5. Полная проверка консистентности для CSP (с. 169, дословно):**
> «• arc consistency AC is sufficient for tree-like CSPs. • systematic tree search maintaining
> AC is needed for arbitrary CSPs.»

**6. Множественные объяснения (с. 171):** «We use preference-based search (Junker 2002) to
determine multiple preferred relaxations. It sets up a choice point each time a constraint ci
is consistent w.r.t. a partial relaxation Ri−1.»

### Что автор говорит о новизне и о родственных работах (с. 171–172, дословно)

> «Whereas the notion of preferred relaxations found a lot of interest, e.g. in the form of
> extensions of prioritized default theories (Brewka 1989), **the concept of a preferred
> explanation appears to be new.**»

> «Iterative approaches successively remove elements (Bakker et al. 1993) or add elements
> (de Siqueira N. & Puget 1988) and test conflict membership. QUICKXPLAIN unifies and improves
> these two methods by successively decomposing the complete explanation problem into
> subproblems of the same size. (Mauss & Tatar 2002) follow a similar approach, but do not
> take preferences into account. (de la Banda, Stuckey, & Wazny 2003) determine all conflicts
> by exploring a conflict-set tree. These checking-based methods for computing explanations
> **work for any solver and do not require that the solver identifies its precise inferences.**»

> «Moreover, subset checking can also be used to find explanations for linear programming as
> shown in (Chinneck 1997).» — Chinneck, J. W. 1997. «Finding a useful subset of constraints
> for analysis in an infeasible linear program». INFORMS Journal on Computing 9:164–174.

**Промышленное применение (Conclusion, с. 172, дословно):** «…provides the technological basis
for the explanation facility of a principal industrial constraint programming tool (ILOG 2003b)
and a CP-based configurator (ILOG 2003a), which is used in various B2B and B2C configuration
applications.»

### Полный список литературы Junker 2004 (с. 172, дословно — реквизиты для дальнейших доборов)

- Bakker, R. R.; Dikker, F.; Tempelman, F.; and Wognum, P. M. 1993. Diagnosing and solving
  over-determined constraint satisfaction problems. In IJCAI-93, 276–281.
- Brewka, G. 1989. Preferred subtheories: An extended logical framework for default reasoning.
  In IJCAI-89, 1043–1048.
- Chinneck, J. W. 1997. Finding a useful subset of constraints for analysis in an infeasible
  linear porgram [так в оригинале — опечатка в слове «program»]. INFORMS Journal on
  Computing 9:164–174.
- de Kleer, J. 1986. An assumption–based truth maintenance system. Artificial Intelligence
  28:127–162.
- de la Banda, M. G.; Stuckey, P. J.; and Wazny, J. 2003. Finding all minimal unsatisfiable
  subsets. In PPDP 2003, 32–43.
- de Siqueira N., J. L., and Puget, J.-F. 1988. Explanation-based generalisation of failures.
  In ECAI-88, 339–344.
- Dechter, R., and Pearl, J. 1989. Tree clustering for constraint networks. Artificial
  Intelligence 38:353–366.
- Doyle, J. 1979. A truth maintenance system. Artificial Intelligence 12:231–272.
- Ginsberg, M., and McAllester, D. 1994. GSAT and dynamic backtracking. In KR'94, 226–237.
- ILOG. 2003a. ILOG JConfigurator V2.1. Engine programming guide, ILOG S.A., Gentilly, France.
- ILOG. 2003b. ILOG Solver 6.0. User manual, ILOG S.A., Gentilly, France.
- Junker, U., and Mailharro, D. 2003. Preference programming: Advanced problem solving for
  configuration. AI-EDAM 17(1):13–29.
- Junker, U. 2002. Preference-based search and multi-criteria optimization. In AAAI-02, 34–40.
- Jussien, N.; Debruyne, R.; and Boizumault, P. 2000. Maintaining arc-consistency within
  dynamic backtracking. In CP'2000, 249–261.
- Mauss, J., and Tatar, M. 2002. Computing minimal conflicts for rich constraint languages.
  In ECAI-02, 151–155.
- Prosser, P. 1993. Hybrid algorithms for the constraint satisfaction problem. Computational
  Intelligence 9:268–299.
- Sqalli, M. H., and Freuder, E. C. 1996. Inference-based constraint satisfaction supports
  explanation. In AAAI-96, 318–325.

🔴 **Отрицательный факт, важный для нас:** в списке литературы Junker 2004 **НЕТ ссылки на
Reiter 1987**. То есть QuickXplain не построен на теории диагностики Райтера и не ссылается
на неё — связка «Reiter → QuickXplain», встречающаяся во вторичных пересказах, автором
первоисточника не заявлена. Общий предок у них — работы по TMS (de Kleer 1986, Doyle 1979),
которые в списке есть.

## ДОБОР Г4 — Reiter R. (1987) «A theory of diagnosis from first principles», ПОЛНЫЙ ТЕКСТ ДОБЫТ

### 🔴 РЕКВИЗИТЫ — расхождение вторичных источников по тому РАЗРЕШЕНО

**Reiter, R. «A theory of diagnosis from first principles». Artificial Intelligence,
том 32, выпуск 1, апрель 1987, страницы 57–95. DOI 10.1016/0004-3702(87)90062-2.**

Канал: Crossref API (`https://api.crossref.org/works?query.bibliographic=…`) — HTTP 200,
поля `volume: "32"`, `issue: "1"`, `page: "57-95"`, `published: [1987, 4]`,
`container-title: "Artificial Intelligence"`. Подтверждено НЕЗАВИСИМО колонтитулами самого
PDF: страница 57 — «ARTIFICIAL INTELLIGENCE 57 / A Theory of Diagnosis from First Principles»,
далее нечётные страницы несут колонтитул «A THEORY OF DIAGNOSIS FROM FIRST PRINCIPLES» с
номерами 67, 69, 71, 73…, чётные — «R. REITER» с номерами 68, 70, 72, 74.

🔴 **Том 32, а не 33 и не 34.** Semantic Scholar при этом отдаёт `"year": 1986` (запись
`DBLP: journals/ai/Reiter87`, `citationCount: 3556`) — это артефакт их базы, не альтернативная
редакция; ставить год 1986 нельзя.

**Канал полного текста:** Unpaywall для DOI 10.1016/0004-3702(87)90062-2 → `is_oa: False`,
`oa_status: "closed"`, `best_oa_location: None` — **легального OA нет, Elsevier закрыт**.
Semantic Scholar указал `openAccessPdf.status: "CLOSED"` с мёртвым URL cs.kun.nl.
Текст добыт с учебного зеркала: `curl -sk --http1.1` с браузерным UA →
`https://cse.sc.edu/~mgv/csce580f11/gradPres/reiter-diagnosis.pdf` — **HTTP 200,
1 751 213 байт, `application/pdf`**; `pdftotext -layout` → 88 927 байт текста (скан с OCR,
местами искажает символы: «Δ» распознаётся как «A», «zl», «~1»; формулы читаются, но
литерные обозначения требуют осторожности).

Провалившиеся каналы (для протокола): `www.cs.ubc.ca/~poole/cs322/2005/Reiter87.pdf` —
HTTP 404; `www.cs.toronto.edu/~sheila/384/w11/Readings/reiter87.pdf` — HTTP 403;
`webdocs.cs.ualberta.ca/~greiner/PAPERS/…` — HTTP 404; Wayback CDX по `*.pdf` с фильтром —
HTTP 403 «This type of CDX query requires authorization»; `archive.org/wayback/available` —
HTTP 429. Точечный CDX по конкретному URL сработал (снимок 20170921234913, 1 616 087 байт),
но не понадобился.

### Определения (дословно, §4, с. 67–68)

**Definition 4.1 (conflict set), с. 67:**
> «A conflict set for (SD, COMPONENTS, OBS) is a set {c1, …, ck} ⊆ COMPONENTS such that
> SD ∪ OBS ∪ {¬AB(c1), …, ¬AB(ck)} is inconsistent. A conflict set for (SD, COMPONENTS, OBS)
> is minimal iff no proper subset of it is a conflict set for (SD, COMPONENTS, OBS).»

Там же отмечено происхождение понятия: «a concept due originally to de Kleer [5]» (с. 67).

**Proposition 4.2, с. 67:**
> «Δ ⊆ COMPONENTS is a diagnosis for (SD, COMPONENTS, OBS) iff Δ is a minimal set such that
> COMPONENTS − Δ is not a conflict set for (SD, COMPONENTS, OBS).»

🔴 **Definition 4.3 — HITTING SET, ДОСЛОВНО (с. 67):**
> «Suppose C is a collection of sets. A **hitting set** for C is a set H ⊆ ∪(S∈C) S such that
> H ∩ S ≠ { } for each S ∈ C. A hitting set for C is **minimal** iff no proper subset of it
> is a hitting set for C.»

То есть: hitting set — множество, пересекающееся с КАЖДЫМ множеством коллекции хотя бы по
одному элементу; минимальный — неснижаемый по включению (не по мощности!).

🔴 **Theorem 4.4 — ГЛАВНАЯ ТЕОРЕМА, ДОСЛОВНО (с. 67):**
> «Δ ⊆ COMPONENTS is a diagnosis for (SD, COMPONENTS, OBS) iff Δ is a minimal hitting set for
> the collection of conflict sets for (SD, COMPONENTS, OBS).»

Вводная фраза автора перед ней (с. 67): «The following is our principal characterization of
diagnoses, and will provide the basis for computing diagnoses». Доказательство занимает
с. 67–68, приведено в PDF полностью (обе импликации).

**Corollary 4.5, с. 68:**
> «Δ ⊆ COMPONENTS is a diagnosis for (SD, COMPONENTS, OBS) iff Δ is a minimal hitting set for
> the collection of **minimal** conflict sets for (SD, COMPONENTS, OBS).»

Основание (с. 68, дословно): «Notice that every superset of a conflict set for (SD, COMPONENTS,
OBS) is also a conflict set. Because of this, we can easily prove the following: H is a minimal
hitting set for the collection of all conflict sets for (SD, COMPONENTS, OBS) iff H is a minimal
hitting set for the collection of all minimal conflict sets for (SD, COMPONENTS, OBS).»

**Пример из статьи (полный сумматор, с. 68, дословно):** «The full adder has two minimal
conflict sets {X1, X2} and {X1, A2, O1} … There are three diagnoses, given by the minimal
hitting sets for {X1, X2} and {X1, A2, O1}: {X1}, {X2, A2}, {X2, O1}.»

**Приоритет по отношению к de Kleer & Williams (с. 69, дословно):**
> «De Kleer and Williams [6] have independently proposed a characterization of diagnoses which
> corresponds to our Corollary 4.5. However, the major difference between their result and ours
> is that, while theirs derives from sound intuitions, it is based upon an unformalized approach
> to diagnosis, while our results have been derived from initial formal definitions.»

### Definition 4.6 — HS-TREE, ДОСЛОВНО (с. 69)

> «Suppose F is a collection of sets. An edge-labeled and node-labeled tree T is an **HS-tree**
> for F iff it is a smallest tree with the following properties:
> (1) Its root is labeled by "√" if F is empty. Otherwise, its root is labeled by a set of F.
> (2) If n is a node of T, define H(n) to be the set of edge labels on the path in T from the
> root node to n. If n is labeled by √, it has no successor nodes in T. If n is labeled by a
> set Σ of F, then for each σ ∈ Σ, n has a successor node n_σ joined to n by an edge labeled
> by σ. The label for n_σ is a set S ∈ F such that S ∩ H(n_σ) = { } if such a set S exists.
> Otherwise, n_σ is labeled by √.»

**Пример 4.7 (с. 69):** F = {{2,4,5}, {1,2,3}, {1,3,5}, {2,4,6}, {2,4}, {2,3,5}, {1,6}}.

**Два свойства HS-дерева (с. 69, дословно):** «(1) If n is a node of the tree labeled by √,
then H(n) is a hitting set for F. (2) Each minimal hitting set for F is H(n) for some node n
of the tree labeled by √.» И далее: «Notice that the sets of the form H(n) for nodes labeled
by √ do not include all hitting sets for F. The important point for our purpose is that they
do include all minimal hitting sets for F.»

🔴 **Почему Райтер считает не операции, а ОБРАЩЕНИЯ к F (с. 69–71, дословно) — прямая аналогия
нашей задаче:**
> «In addition, we wish to minimize the number of accesses to F required to generate this
> subtree, where by an access to F we mean the computation required to determine the label of
> a node in this subtree. … For our purposes, this computation requiring an access to F must be
> treated as **extremely expensive**. This is so because for us, F will be the set of all conflict
> sets for (SD, COMPONENTS, OBS). Moreover, F **will not be explicitly available, but will
> instead be implicitly defined**. An access to F will be the computation of a conflict set, and
> this will require a call to a theorem prover.»

### Алгоритм построения ОБРЕЗАННОГО HS-дерева, ДОСЛОВНО (с. 72)

> «We summarize our method for generating a pruned HS-tree for F as follows:
> (1) Generate the HS-tree **breadth-first**, generating nodes at any fixed level in the tree
> in left-to-right order.
> (2) **Reusing node labels:** If node n is labeled by the set S ∈ F, and if n' is a node such
> that H(n') ∩ S = { }, label n' by S. (We indicate that the label of n' is a reused label by
> underlining it in the tree.) Such a node n' requires no access to F.
> (3) **Tree pruning:**
> (i) If node n is labeled by √ and node n' is such that H(n) ⊆ H(n'), close n', i.e. do not
> compute a label for n'; do not generate any successors of n'.
> (ii) If node n has been generated and node n' is such that H(n') = H(n), then close n'.
> (We indicate a closed node in the tree by marking it with "×".)
> (iii) If nodes n and n' have been respectively labeled by sets S and S' of F, and if S' is a
> proper subset of S, then for each α ∈ S − S' mark as redundant the edge from node n labeled
> by α. A redundant edge, together with the subtree beneath it, may be removed from the HS-tree
> while preserving the property that the resulting pruned HS-tree will yield all minimal
> hitting sets for F.»

**Theorem 4.8, с. 72, дословно:**
> «Let F be a collection of sets, and T a pruned HS-tree for F, as previously described. Then
> {H(n) | n is a node of T labeled by √} is the collection of minimal hitting sets for F.»

**Числа примера (с. 72):** для F из Fig. 3 минимальные hitting sets — {1,2}, {2,3,6}, {2,5,6},
{4,1,3}, {4,1,5}, {4,3,6}; «The computation of these hitting sets required **13 accesses to F**».

Отдельно (с. 72, дословно) — почему нельзя просто предочистить F от надмножеств:
> «Why not simply prescan F, remove from F all supersets of sets in F, and use the resulting
> trimmed F to generate an HS-tree? … The reason we did not do this is … for our purposes F
> will be implicitly defined as the set of all conflict sets … Since we will not have available
> an explicit enumeration of these conflict sets, we cannot perform a preliminary subset test
> on them.»

**Вычисление всех диагнозов (§4.3, с. 74, дословно):** «First compute the collection F of all
conflict sets for (SD, COMPONENTS, OBS), then use the method of pruned HS-trees to compute the
minimal hitting sets for F. These minimal hitting sets will be the diagnoses.»

---

## ДОБОР Г4 — Greiner, Smith & Wilkerson (1989): 🔴 ПОПРАВКА ПОДТВЕРЖДЕНА, В ЧЁМ ИМЕННО ОШИБКА

**Реквизиты (Crossref, HTTP 200):** Russell Greiner, Barbara A. Smith, Ralph W. Wilkerson.
«A correction to the algorithm in Reiter's theory of diagnosis». **Artificial Intelligence,
том 41, выпуск 1, страницы 79–88, 1989.** Подтверждено самим PDF: колонтитул первой страницы
«ARTIFICIAL INTELLIGENCE 79», подпись внизу — «Artificial Intelligence 41 (1989/90) 79–88,
0004-3702/89/$3.50 © 1989, Elsevier Science Publishers B.V. (North-Holland)». Жанр —
**RESEARCH NOTE**. Аффилиации: Greiner — University of Toronto, 10 King's College Road;
Smith и Wilkerson — University of Missouri at Rolla.

**Канал:** `curl -sk --http1.1` с браузерным UA →
`http://www.cs.ru.nl/~peterl/teaching/KeR/Theorist/greibers-correctiontoreiter.pdf` —
**HTTP 200, 463 965 байт, `application/pdf`**, 10 страниц; `pdftotext -layout` → 23 141 байт.

### ✅ ДА, ОШИБКА В ОРИГИНАЛЕ РАЙТЕРА БЫЛА. Формулировка авторов дословно (Abstract, с. 79):

> «Reiter [3] has developed a general theory of diagnosis based on first principles. His
> algorithm computes all diagnoses which explain the differences between the predicted and
> observed behavior of a given system. **Unfortunately, Reiter's description of the algorithm
> is incorrect in that some diagnoses can be missed under certain conditions.** This note
> presents a revised algorithm and a proof of its correctness.»

### 🔴 В ЧЁМ ИМЕННО ОШИБКА (с. 80 и с. 82, дословно)

Источник бага назван прямо (с. 79–80): «However, it is the application of a technique for
handling the nonminimal conflict sets that introduces a bug into Reiter's algorithm.»

Механизм (с. 82, дословно):
> «It should be clear that pruning by removing redundant edges (pruning rule (3iii)) is
> applicable only when there is at least one set in the collection which is a strict superset
> of some other set in the collection. … **However, this type of pruning can result in an
> incomplete diagnostician, as it is possible to lose minimal hitting sets, and therefore,
> diagnoses.**»

> «The problem arises from **the interaction of the pruning rule which removes redundant edges
> (rule (3iii)) and the closing rules (rules (3i) and (3ii))**. A closing rule will close the
> node n when it finds another node n' which will lead to the same minimal hitting set(s).
> This, of course, assumes that the node n' will remain in the HS-tree. The pruning rule,
> however, may remove the node n', meaning that the path to any potential hitting sets will be
> totally lost — lost from the node n path when node n was closed and lost from the node n'
> path when node n' was pruned.» (с. 83)

**Контрпример целиком (с. 82, дословно):**
> «Consider the collection of sets: {{a,b}, {b,c}, {a,c}, {b,d}, {b}}. Without pruning by
> removing redundant edges, the HS-tree shown in Fig. 1 would be generated. … Note that nodes
> n5, n7, and n9 have been closed by the subset rule (pruning rule (3i)) since n3 is labeled √,
> H(n3) ⊆ H(n5), H(n3) ⊆ H(n7), and H(n3) ⊆ H(n9). The set labeling node n8, {a}, is a proper
> subset of the set, {a,b}, labeling nodes n0, n1, and n4. If the redundant branches from n0,
> namely the branch labeled "a", is pruned, the remaining tree contains only the nodes n0, n2,
> n5, and n6. **The minimal hitting set {a,b} is no longer represented in the tree.**»

**Вторая, отдельная неточность — пропущенная перемаркировка родителя (с. 83, дословно):**
> «Before presenting the solution to this problem, we first clarify one other point in Reiter's
> original algorithm. **Pruning by the removal of redundant edges also requires that the parent
> node be relabeled.** Consider the collection of sets {{a,b}, {a}, {b}}. Without pruning, the
> HS-tree in Fig. 2 would be generated. As {b} ⊂ {a,b}, the "a" branch under n0 would be pruned.
> However, if n0 is not relabeled by the set {b}, then the "b" branch under n0 would be pruned
> as {a} ⊂ {a,b}. The surviving HS-tree would contain the single node n0 which is not labeled
> by √.»

И важная оговорка авторов в пользу Райтера (с. 83, дословно):
> «**Reiter's description (in the text) of the process for computing the minimal hitting sets
> is basically correct. However, the algorithm did not accurately follow his text.** … In the
> text of the paper, Reiter discusses relabeling the node, but this point is not stated in the
> algorithm.»

🔴 **Это уточнение обязано попасть в любой наш текст.** Правильная формулировка — не «теория
Райтера ошибочна» (теорема 4.4 и теорема 4.8 не тронуты), а **«формулировка обрезающего
алгоритма в статье 1987 неполна: она теряет часть минимальных hitting sets при неминимальных
конфликтах; текст статьи описывал процесс верно, псевдокод — нет»**. Любой вторичный пересказ
вида «Reiter's algorithm is wrong» — огрубление.

### Исправленный алгоритм HS-DAG, ДОСЛОВНО (с. 83–84)

Идея (с. 83): «The HS-DAG algorithm, shown below, is more faithful to that description. It
involves using a **directed acyclic graph, dag,** to compute the minimal hitting sets rather
than a tree. To simplify the description, we assume that the collection of sets is ordered.
This allows us to specify the algorithm deterministically, as we can now select a member of
this collection rather than assume that a member is chosen arbitrarily.»

**Базовое построение HS-dag для упорядоченной коллекции F (с. 84, дословно):**
> «(1) Let D represent the growing dag. Generate a node which will be the root of the dag.
> This node will be processed in (2).
> (2) Process the nodes in D in a breadth-first order. To process a node n:
>  (i) Define H(n) to be the set of edge labels on the path in D from the root down to node n.
>  (ii) If for all x ∈ F, x ∩ H(n) ≠ { } then label n by √. Otherwise, label n by Σ where Σ is
>  the first member of F for which Σ ∩ H(n) = { }.
>  (iii) If n is labeled by a set Σ ∈ F, for each σ ∈ Σ, generate a new downward arc labeled by
>  σ. This arc leads to a new node m with H(m) = H(n) ∪ {σ}. The new node m will be processed
>  (labeled and expanded) after all nodes in the same generation as n have been processed.
> (3) Return the resulting dag, D.»

**Три обрезающих правила HS-DAG (с. 84, дословно) — сравнивать с правилами Райтера построчно:**
> «(1) **Reusing nodes:** This algorithm will not always generate a new node m as a descendant
> of node n. There are two cases to consider: (i) If there is a node n' in D such that
> H(n') = H(n) ∪ {σ}, then let the σ-arc under n point to this existing node n'. Hence, n' will
> have more than one parent. (ii) Otherwise, generate a new node, m, at the end of this σ-arc
> as described in the basic HS-DAG algorithm.
> (2) **Closing:** If there is a node n' which is labeled by √ and H(n') ⊆ H(n) then close node
> n. A label is not computed for n nor are any successor nodes generated.
> (3) **Pruning:** If the set Σ is to label a node and it has not been used previously, then
> attempt to prune D as described in the following. (i) If there is a node n' which has been
> labeled by the set S' of F where Σ ⊂ S', then **relabel n' with Σ**. For any α in S' − Σ, the
> α-edge under n' is no longer allowed. The node connected by this edge and all of its
> descendants are removed, **except for those nodes with another ancestor which is not being
> removed**. Note that this step may eliminate the node which is currently being processed.
> (ii) Interchange the sets S' and Σ in the collection. (Note that this has the same effect as
> eliminating S' from F.)»

🔴 **Суть починки в одной фразе (наша формулировка, основанная на с. 85):** переход от ДЕРЕВА
к ОРИЕНТИРОВАННОМУ АЦИКЛИЧЕСКОМУ ГРАФУ даёт узлу несколько родителей, поэтому обрезка одной
ветви больше не отрезает узел от графа. Авторы прямо на том же примере (с. 85, дословно):
«Figure 3 shows a partial HS-dag for the collection of sets used earlier, namely,
{{a,b}, {b,c}, {a,c}, {b,d}, {b}}. When the set {b} is first used as a label, the dag is
pruned as shown in Fig. 4. **Note that node n3 still has a parent and so remains in the dag.
Thus, the minimal hitting set {a,b} is not lost, as was the case with the HS-tree.**»

**Theorem 4.1 (Correctness of HS-DAG algorithm), с. 85, дословно:**
> «Given the ordered collection F, the HS-DAG algorithm returns a particular labeled dag.
> (1) For all nodes n labeled by √, H(n) is a minimal hitting set.
> (2) Every minimal hitting set for F is H(n) for some node n whose label is √.»

Структура доказательства (с. 85, дословно): «It is sufficient to prove the following three
points: (a) the basic HS-DAG algorithm (without the pruning rules) will find all of the minimal
hitting sets, (b) the pruning rules will not eliminate any of the minimal hitting sets and
(c) the pruning rules will eliminate all of the nonminimal hitting sets.»

🔴 **Отдельно ценно (с. 85):** «(a) The claim is stated, **without proof** on [3, p. 72].»
То есть ключевое свойство полноты в статье 1987 было заявлено БЕЗ ДОКАЗАТЕЛЬСТВА (ср. слова
самого Райтера на с. 69: «The following results are obvious for any HS-tree»), и доказано
только в поправке 1989 (Lemma 4.2). Это ещё один аргумент цитировать пару Reiter 1987 +
Greiner et al. 1989 всегда вместе, а не по отдельности.

**Зависимость результата от порядка (с. 85, дословно):** «Note that the particular HS-dag which
is returned by the algorithm depends on how F is ordered. Using Π(F) to refer to the
Π-rearrangement of F, HS-DAG(F) and HS-DAG(Π(F)) will lead to different HS-dags. We prove below
that these two graphs will produce the same minimal hitting sets.»

**Разница подходов Райтера и de Kleer–Williams по Greiner (с. 79, дословно):** «While Reiter's
algorithm **can make use of conflict sets which are not minimal**, de Kleer and Williams'
algorithm **requires that minimal conflict sets be determined** by the underlying inference
mechanism.»

### Что из этого прямо применимо к FINPILOT

1. Если считать «компонентами» пользовательские требования (сумма досрочного погашения, срок
   цели, размер резерва), а «конфликтными множествами» — наборы требований, при которых
   инварианты Rt ≥ 0 и ПДН ≤ 0,40 несовместны, то **набор требований, который надо ослабить,
   есть минимальный hitting set коллекции конфликтов** (Theorem 4.4 дословно выше).
2. 🔴 **Если реализовывать HS-подход — реализовывать HS-DAG (Greiner 1989), а не HS-tree
   (Reiter 1987).** Наши конфликты будут получаться НЕминимальными (проверка инвариантов
   даёт «этот набор не проходит», не «вот неснижаемое ядро»), а именно на неминимальных
   конфликтах баг Райтера и проявляется — это буквально условие срабатывания правила (3iii).
3. У Junker (QuickXplain) и Reiter разные выходы: Junker даёт ОДИН предпочтительный конфликт
   и одну предпочтительную релаксацию (единственные при тотальном порядке), Reiter/Greiner —
   ВСЕ минимальные диагнозы. Для UX «объясни и предложи одно» дешевле Junker; для «покажи все
   способы разрешить» нужен HS-DAG. Это не конкурирующие, а дополняющие алгоритмы; в списке
   литературы Junker 2004 Reiter 1987 отсутствует (проверено по полному списку выше).

## ДОБОР Г4 — Felfernig et al., IUI '08: ⛔ ПЕРВОИСТОЧНИК НЕ ДОБЫТ (точная причина)

**🔴 Уточнение названия, которое меняет поиск.** В очереди пробелов работа записана как
«Intelligent debugging and repair of utility constraint sets». Полное название по ACM:
**«Intelligent debugging and repair of utility constraint sets in knowledge-based recommender
applications»**. Авторы: **Felfernig A., Teppan E., Friedrich G., Isak K.** Proceedings of the
13th International Conference on Intelligent User Interfaces (IUI '08), **pp. 217–226**,
**doi 10.1145/1378773.1378802**. Аффилиация — Institute for Software Technology, Graz
University of Technology.

**Каналы и их отказы (протокол):**
- `WebSearch` — выдача найдена, полного текста в ней нет.
- `https://api.unpaywall.org/v2/10.1145/1378773.1378802` — HTTP 200, ответ:
  **`is_oa: False`, `oa_status: "closed"`, `best_oa_location: None`.** То есть легальной
  открытой копии не существует вовсе, это не наша неудача поиска.
- Текстовый прокси `curl -s "https://r.jina.ai/https://dl.acm.org/doi/10.1145/1378773.1378802"`
  — **HTTP 200, но всего 463 байта**, тело: «Title: Just a moment… / Performing security
  verification / This website uses a security service to protect against malicious bots… /
  This page maybe requiring CAPTCHA». 🔴 **ACM DL закрыт антиботом и для `r.jina.ai` тоже** —
  замер зафиксирован, повторять этот канал на ACM в следующих доборах бессмысленно.
- ResearchGate (`publication/221608244`) — закрыт Cloudflare (известный замер сессии).

**Что удалось снять достоверно — только из аннотации в выдаче поиска (СНИППЕТ, первоисточник
не открыт):** «constraint-based recommender systems where utility constraints (scoring rules)
determine the order in which items (products and services) are presented to customers. In many
cases utility constraints are faulty and calculate rankings which are not expected and accepted
by marketing and sales experts. The authors present an approach to **automated adaptation of
utility constraint sets based on solutions for nonlinear optimization problems**.»

🔴 **Это меняет ожидание от источника.** Механизм «из конфликта получают предложение по
ослаблению ограничений» у Felfernig et al. 2008 — **НЕ hitting-set и НЕ QuickXplain, а решение
задачи НЕЛИНЕЙНОЙ ОПТИМИЗАЦИИ** по подгонке весов/порогов скоринговых правил к эталонным
ранжированиям экспертов. То есть работа отвечает на вопрос «как починить ВЕСА, чтобы
ранжирование совпало с ожиданием экспертов», а не «что ослабить, когда допустимых альтернатив
ноль». **Для пункта Г4.1 (пустое множество альтернатив) она не является нужным источником;
она относится к задаче калибровки весов SAW.** Записать это как отрицательный результат по
исходной постановке и как положительный указатель для темы калибровки.

**Доступные заместители того же коллектива (реквизиты для следующего добора, полный текст не
брался в этом доборе):**
- Felfernig, Schippel, Leitner, Reinfrank, Isak, Mandl, Blazek, Ninaus. «Automated repair of
  scoring rules in constraint-based recommender systems». AI Communications, 2013,
  doi 10.3233/AIC-120543 (SAGE) — прямое продолжение IUI '08, то же «repair of scoring rules».
- «An efficient diagnosis algorithm for inconsistent constraint sets». AI EDAM (Cambridge) —
  **есть открытая копия на arXiv: `https://arxiv.org/pdf/2102.09005`** (в этом доборе не
  скачивалась, канал проверен как существующий по выдаче).
- «A Diagnosis Algorithm for Inconsistent Constraint Sets» — открытый PDF на
  `https://papers.phmsociety.org/index.php/phmconf/article/download/1948/957`.

---

## ДОБОР Г4 — Rodler P. (2022), формальное доказательство QuickXplain: ПОЛНЫЙ ТЕКСТ ДОБЫТ

**Реквизиты:** Patrick Rodler, University of Klagenfurt, Universitätsstrasse 65-67, 9020
Klagenfurt. «Understanding the QuickXPlain Algorithm: Simple Explanation and Formal Proof» —
препринт arXiv:2001.01835v3 [cs.AI], 4 August 2022. Журнальная версия: «A formal proof and
simple explanation of the QuickXplain algorithm», **Artificial Intelligence Review**,
doi **10.1007/s10462-022-10149-w**; открытый доступ также через PMC (PMC9622537) и
PubMed 36337611.

**Канал:** `curl -sk --http1.1` → `https://arxiv.org/pdf/2001.01835` — **HTTP 200,
875 248 байт, `application/pdf`**; `pdftotext -layout` → 62 547 байт.

### 🔴 Главная практическая оговорка: до 2022 года доказательства корректности QuickXplain НЕ БЫЛО

Дословно (Abstract, с. 1):
> «However, although (we regularly experience) people are having a hard time understanding
> QuickXPlain and seeing why it works correctly, **a proof of correctness of the algorithm has
> never been published.** This is what we account for in this work…»

И в разделе 1 (с. 3, дословно): «people often complain they do not see why it correctly
computes a minimal subset of the universe. **This is not least because no proof of QX has yet
been published.**» В Conclusion (с. 16): «Since QX has in practice turned out to be hardly
understood by many — experienced academics included — and was published without a proof, we
account for that by providing for QX an intelligible proof that explains.»

Практический вывод для нас: **утверждение «QuickXplain доказанно корректен» допустимо
цитировать только со ссылкой на Rodler 2022, не на Junker 2004.** Junker 2004 содержит
Theorem 1 (формулировку корректности), но без доказательства; Junker сам пишет «The following
results are obvious» о свойствах и не доказывает их — ровно та же болезнь, что у Reiter 1987
(см. выше: Greiner et al. 1989, с. 85, «The claim is stated, without proof on [3, p. 72]»).

### Переформулировка задачи в общем виде — MSMP (с. 2, дословно)

> «The task of finding within a given universe an irreducible subset with a specific monotone
> property is referred to as the **MSMP (Minimal Set subject to a Monotone Predicate)**
> problem.»

**Definition 1 (Monotone Property), с. 5, дословно:**
> «Let U be the universe (a set of elements) and p : 2^U → {0,1} be a function where p(X) = 1
> iff property p holds for X ⊆ U. Then, p is a **monotone property** iff p(∅) = 0 and
> ∀X', X'' ⊆ U : X' ⊂ X'' ⟹ p(X') ≤ p(X'').»
> «So, p is monotone iff, given that p holds for some set X', it follows that p also holds for
> any superset X'' of X'. An equivalent definition is: If p does not hold for some set X'',
> p does not hold for any subset X' of X'' either.»

**Definition 2 (p-Problem-Instance), с. 6:** «Let A (analyzed set) and B (background) be
(related) finite sets of elements where **A ∩ B = ∅**, and let p be a monotone predicate.
Then we call the tuple ⟨A, B⟩ a p-problem-instance (p-PI).»

**Definition 3 (Minimal p-Set given some Background), с. 6:** «Let ⟨A, B⟩ be a p-PI. Then, we
call X a p-set wrt. ⟨A, B⟩ iff X ⊆ A and p(X ∪ B) = 1. We call a p-set X wrt. ⟨A, B⟩ minimal
iff there is no p-set X' ⊂ X wrt. ⟨A, B⟩.» Сноска 7 (с. 5): «Throughout this paper,
**minimality always refers to minimality wrt. set-inclusion**» — то есть НЕ по мощности.

**Proposition 1 (Existence of a p-Set), с. 6, дословно:** «(1) A (minimal) p-set exists for
⟨A, B⟩ iff p(A ∪ B) = 1. (2) ∅ is a — and the only — (minimal) p-set wrt. ⟨A, B⟩ iff p(B) = 1.»

### Алгоритм QX в записи Родлера (Algorithm 1, с. 6, дословно) — сверить с псевдокодом Junker

```
Algorithm 1 QX: Computation of a Minimal p-Set
Input: a p-PI ⟨A, B⟩ where A is the analyzed set and B is the background
Output: a minimal p-set wrt. ⟨A, B⟩, if existent; 'no p-set', otherwise
 1: procedure QX(⟨A, B⟩)
 2:   if p(A ∪ B) = 0 then
 3:       return 'no p-set'
 4:   else if A = ∅ then
 5:       return ∅
 6:   else
 7:       return QX'(B, ⟨A, B⟩)

 8: procedure QX'(C, ⟨A, B⟩)
 9:   if C ≠ ∅ ∧ p(B) = 1 then
10:       return ∅
11:   if |A| = 1 then
12:       return A
13:   k ← split(|A|)
14:   A1 ← get(A, 1, k)
15:   A2 ← get(A, k + 1, |A|)
16:   X2 ← QX'(A1, ⟨A2, B ∪ A1⟩)
17:   X1 ← QX'(X2, ⟨A1, B ∪ X2⟩)
18:   return X1 ∪ X2
```

🔴 **Сверка с оригиналом Junker 2004 (Figure 1, с. 170) — расхождений по существу нет**, но
ОБОЗНАЧЕНИЯ инвертированы и это ловушка при чтении вторичных пересказов: у Junker строка 4
проверяет `not isConsistent(B)`, у Rodler строка 9 проверяет `p(B) = 1`, потому что у Junker
предикат — «консистентно», а у Rodler — «свойство выполнено» (то есть НЕконсистентность).
Порядок рекурсивных вызовов совпадает: сначала правая половина с левой в фоне, затем левая
с уже найденным X2 в фоне.

**Theorem 1 (Correctness of QX), с. 16, дословно:**
> «Let ⟨A, B⟩ be a p-PI. Then, QX(⟨A, B⟩) returns a minimal p-PI wrt. ⟨A, B⟩ if a p-set exists
> for ⟨A, B⟩. Otherwise, QX(⟨A, B⟩) returns 'no p-set'.»
(Опечатка «minimal p-PI» вместо «minimal p-set» — в самом препринте.)

**Proposition 2 (Termination), с. 11:** «Let ⟨A, B⟩ be a p-PI. Then QX(⟨A, B⟩) terminates.»

**Стратегия деления и сложность (с. 14, дословно):** «suppose that QX pursues a splitting
strategy where a set is always partitioned into equal-sized subsets in each iteration, i.e.,
split(n) returns ⌈n/2⌉ (note: **this leads to the best worst-case complexity of QX**, cf. [9]).»
Ссылка [9] — это Junker 2004; то есть Rodler подтверждает нашу таблицу 4 из первоисточника,
а не даёт свою.

**Пример Родлера (с. 14):** A = {1,…,8}, B = ∅, два минимальных p-set: X = {3,4,7} и
Y = {4,5,8}. Показывает, что QX возвращает **один** из них, зависящий от порядка/разбиения.

### Условия применимости алгоритма QX как чёрного ящика (с. 2–3, дословно)

> «In general, an algorithm A for a specific manifestation of the MSMP problem can be used to
> solve arbitrary manifestations of the MSMP problem if (i) the procedure used by A to decide
> the monotone predicate is **used as a black-box** (i.e., given a subset of the universe as
> input, the procedure outputs 1 if the predicate is true for the subset and 0 otherwise; no
> more and no less), and (ii) **no assumptions or additional techniques are used in A which
> are specific to one particular manifestation** of the MSMP problem.»

Родлер отдельно перечисляет, какие алгоритмы этому НЕ удовлетворяют (с. 3): опирающиеся на
дополнительный вывод сверх значения предиката (certificate-refinement-based), glass-box
подходы с модификацией процедуры проверки (theorem prover, записывающий аксиомы вывода),
и техника model rotation для MUS, неприменимая к minimal correction subsets.

**Почему QX популярен — оценка Родлера (с. 3, дословно):** «Likely reasons for the widespread
use of QX are its **mild theoretical complexity in terms of the number of (usually expensive)
predicate evaluations** required, as well as its favorable practical performance for important
problems (such as conflict or diagnosis computation for model-based diagnosis).»

**Терминологическая карта (с. 2, дословно) — важна, чтобы не путать литературу:** «minimal
unsatisfiable subsets (also termed **conflicts** or minimal unsatisfiable cores), minimal
correction subsets (also termed **diagnoses**), prime implicants (also termed justifications),
prime implicates, and most concise optimal queries to an oracle».
🔴 То есть «конфликт» Junker'а и «диагноз» Reiter'а — это **разные** объекты (MUS против MCS),
а не синонимы; вторичные пересказы их регулярно смешивают.

---

# ИТОГ ДОБОРА Г4 (11.09.2026)

Один агент, без подагентов. Каналы в порядке: `WebSearch` → `WebFetch` → `curl -sk --http1.1`
с браузерным UA → `r.jina.ai` → API метаданных (Crossref, Unpaywall, Semantic Scholar) →
Wayback с `id_`. Все HTTP-коды и размеры проставлены у каждого источника в его разделе.

## Таблица по пунктам

| Пункт | Источник | Итог | Где раздел |
|---|---|---|---|
| Г4.1 | **Junker, QUICKXPLAIN, AAAI-04, 167–172** | ✅ **ДОБЫТ ПОЛНОСТЬЮ** (cdn.aaai.org, HTTP 200, 115 902 б) | `constraint_based_utility_recsys_2026-09-09.md` |
| Г4.1 | **Reiter 1987, AI 32(1):57–95** | ✅ **ДОБЫТ ПОЛНОСТЬЮ** (зеркало cse.sc.edu, HTTP 200, 1 751 213 б) | там же |
| Г4.1 | **Greiner, Smith & Wilkerson 1989, AI 41(1):79–88** | ✅ **ДОБЫТ ПОЛНОСТЬЮ** (cs.ru.nl, HTTP 200, 463 965 б) | там же |
| Г4.1 | **Felfernig et al., IUI '08, 217–226** | ⛔ **НЕ ДОБЫТ.** Unpaywall: `is_oa: False`, `oa_status: "closed"`. ACM DL: Cloudflare и для `curl`, и для `r.jina.ai` (HTTP 200, 463 б, «Performing security verification»). Есть только аннотация-сниппет | там же |
| Г4.1 | **Rodler 2022, формальное доказательство QX** (сверх задания) | ✅ **ДОБЫТ ПОЛНОСТЬЮ** (arXiv:2001.01835, HTTP 200, 875 248 б) | там же |
| Г4.2 | **Landis & Koch 1977, Biometrics 33(1):159–174** | ✅ **ДОБЫТ ПОЛНОСТЬЮ** (Wayback `id_`, HTTP 200, 1 181 952 б) | `prescriptive_quality_metrics_2026-09-10.md` |
| Г4.2 | **Feinstein & Cicchetti 1990, JCE 43(6):543–549** | 🟡 **ЧАСТИЧНО.** Аннотация издателя дословно (`r.jina.ai`, HTTP 200, 16 299 б). Полный текст: Unpaywall `closed`; ScienceDirect **HTTP 403 при теле 832 805 б** | там же |
| Г4.2 | **Обзор метаморфического тестирования** | 🟡 **ЧАСТИЧНО.** Segura et al. добыт полностью в версии техотчёта ISA-16-TR-02 (idus.us.es, HTTP 200, 1 970 284 б). Chen et al. CSUR 51(1) — НЕ добыт (репозиторий Ноттингема: HTTP 403 `curl`, 549 б Cloudflare через `r.jina.ai`) | там же |
| Г4.2 | **Bengen 1994, правило 4 %** | ✅ **ДОБЫТ ПОЛНОСТЬЮ** (FPA, каталог `2021-04`, HTTP 200, 347 755 б) | там же |
| Г4.2 | **Методология Delphi** | ✅ **ДОБЫТО ДВА ИСТОЧНИКА.** Linstone & Turoff 1975 целиком (Wayback `id_`, HTTP 200, 11 700 935 б) + Diamond et al. 2014 аннотация с числами (`r.jina.ai`, HTTP 200, 23 026 б) | там же |
| Г4.3 | **Рамка выбора метода MCDA, Omega** | ✅ **ДОБЫТ ПОЛНОСТЬЮ** (arXiv:1810.11078, HTTP 200, 2 518 978 б) | `approach_validity_2026-09-10.md` |
| Г4.3 | **Fox 1966** | ⛔ **НЕ ДОБЫТ.** Unpaywall `10.1287/mnsc.13.3.210`: `is_oa: False`, `oa_status: "closed"` | `optimization_solvers_2026-09-10_dobor_lit.md` |
| Г4.3 | **Federgruen & Groenevelt 1986** | ⛔ **НЕ ДОБЫТ.** Unpaywall `10.1287/opre.34.6.909`: `is_oa: False`, `oa_status: "closed"` | там же |
| Г4.3 | **Michaud 1989, цитата «estimation-error maximizers, p. 33»** | ⛔ **НЕ ПОДТВЕРЖДЕНА, ВЕРДИКТ: СНЯТЬ.** Unpaywall `closed`; S2 `openAccessPdf status CLOSED`; SSRN HTTP 403; JSTOR — экран доступа; сайт автора HTTP 404. Добыта авторская аннотация издателя (CFA Institute, HTTP 200, 1 880 б) — **выражения в ней нет** | там же |

## 🔴 Что из добытого ОПРОВЕРГАЕТ или правит уже записанное

1. 🔴 **«Cinelli et al., Omega 2018» — неверная атрибуция.** Авторы рамки выбора метода MCDA —
   **Wątróbski, Jankowski, Ziemba, Karczmarczyk, Zioło**, Omega **86 (2019), 107–124**.
   Фамилии Cinelli среди авторов нет. Подтверждено Crossref и титулом самого PDF.
2. 🔴 **«Segura et al., ACM Computing Surveys 51(1), doi 10.1145/3143561» — склейка двух
   работ.** По этому DOI лежит **Chen, Kuo, Liu, Poon, Towey, Tse, Zhou**, CSUR 51(1):1–27,
   2018. Обзор Segura с соавторами — **IEEE TSE 42(9):805–824, 2016**, doi 10.1109/TSE.2016.2532875.
3. 🔴 **«Fox (1966), Operations Research 34(6):909–918» (формулировка задания) — склейка.**
   Fox 1966 — **Management Science 13(3):210–216**; пагинация 34(6):909–918 принадлежит
   **Federgruen & Groenevelt 1986**. В самом файле `optimization_solvers…dobor_lit.md` это уже
   было записано правильно — ошибка в задании, не в базе.
4. 🔴 **Шкала каппы Landis & Koch цитируется с подправленными границами.** В первоисточнике
   (с. 165) — **«< 0.00 Poor», «0.00–0.20 Slight»**, а не общепринятое «≤ 0 poor,
   0.01–0.20 slight». И там же авторская оговорка, которую опускают почти всегда: «**Although
   these divisions are clearly arbitrary, they do provide useful "benchmarks" for the discussion
   of the specific example in Table 1.**» Шкала введена для ОДНОГО примера их же статьи, а не
   как норматив приёмки.
5. 🔴 **Цитата Michaud «estimation-error maximizers, p. 33» не подтверждается ничем первичным.**
   Выражения нет ни в авторской аннотации издателя, ни в двух собственных текстах Michaud,
   доступных полностью. Плюс существует второе издание статьи с ДРУГОЙ пагинацией
   (ICFA Continuing Education Series 1989(4):43–54), что делает «p. 33» вдвойне ненадёжной.
   **Снять из всех текстов**, заменить на проверенную цитату из аннотации.
6. 🔴 **Число «4 % выдержало 50 лет в 41 из 50 случаев» у Бенгена ОТСУТСТВУЕТ.** В статье:
   **40 сценарных лет из 51** достигают 50-летней живучести при 50/50 и 4 % (это следует из
   сравнения с Figure 3(A): «Fully 47 scenario years… while only 40 scenario years attained
   that pinnacle in the earlier chart»). И сам Бенген даёт два разных минимума для одного и
   того же графика: «about 35 years» в описании Figure 1(B) и «**before 33 years**» в выводах.
7. 🔴 **Итоговая рекомендация Бенгена по активам — не 50/50, а «as close to 75 percent
   [stocks] as possible, and in no cases less than 50 percent».** 50/50 — «an arbitrary asset
   allocation chosen for purposes of illustration», а горизонт 50 лет — «chosen arbitrarily»,
   то есть столбцы «50 лет» на графиках цензурированы справа.
8. 🔴 **Felfernig et al. IUI '08 отвечает не на тот вопрос, под который стоял в очереди.** По
   аннотации — «automated adaptation of utility constraint sets based on solutions for
   **nonlinear optimization problems**», то есть подгонка ВЕСОВ скоринговых правил под
   ожидания экспертов, а **не** алгоритм repair при пустом множестве альтернатив. Пункт надо
   переклассифицировать из Г4.1 (repair) в тему калибровки весов.
9. 🔴 **Reiter 1987 и QuickXplain не связаны так, как утверждают вторичные пересказы.**
   В списке литературы Junker 2004 (снят полностью) **ссылки на Reiter нет**. Общий предок —
   работы по TMS (de Kleer 1986, Doyle 1979). И это разные объекты: QuickXplain ищет
   **минимальный конфликт (MUS)**, Reiter перечисляет **все минимальные диагнозы (MCS)** —
   Rodler 2022 прямо перечисляет их как разные манифестации задачи MSMP.
10. 🔴 **Поправка Greiner et al. 1989 подтверждена, но её обычная формулировка — огрубление.**
    Правильно: **теоремы Райтера (4.4, 4.8) не тронуты; неполон ПСЕВДОКОД обрезки** — он теряет
    минимальные hitting sets при НЕминимальных конфликтах из-за взаимодействия правила (3iii)
    с правилами (3i)/(3ii); плюс в алгоритме не была записана перемаркировка родителя, хотя в
    тексте статьи она обсуждалась. Дословно у Greiner: «Reiter's description (in the text)…
    is basically correct. However, the algorithm did not accurately follow his text.»
    **Следствие для нас: реализовывать HS-DAG, а не HS-tree** — наши конфликты будут
    неминимальными, то есть ровно в условии срабатывания бага.
11. 🔴 **Корректность QuickXplain доказана только в 2022 (Rodler), у Junker 2004 доказательства
    нет.** Утверждение «QuickXplain доказанно корректен» цитировать через Rodler, а не Junker.
    Симметрично: ключевое свойство полноты HS-tree у Reiter 1987 заявлено без доказательства
    («The following results are obvious»), доказано только Greiner et al. 1989 (их слова:
    «The claim is stated, **without proof** on [3, p. 72]»).
12. 🔴 **Пять раундов нашей калибровки весов — сверх методической нормы.** Linstone & Turoff:
    «**three rounds proved sufficient to attain stability**; further rounds tended to show very
    little change and **excessive repetition was unacceptable to participants**». И критерий
    остановки методологически иной, чем принято думать: «**Stability of the distribution…
    is a more significant measure for developing a stopping criterion than degree of
    convergence.**»
13. 🔴 **Каппу нельзя публиковать в одиночку.** Оба парадокса Feinstein & Cicchetti бьют
    в наш сценарий перекошенных экспертных оценок; рост κ между раундами может быть артефактом
    изменения маргиналов, а не ростом согласия. Плюс: после Delphi-процедуры с обратной связью
    оценки экспертов **не независимы**, а каппа определена для независимых наблюдателей —
    это дополнительное, отдельное ограничение на её интерпретацию у нас.
14. 🔴 **Условие применимости QuickXplain к нашей задаче проверяемо и выполняется:**
    единственное требование — **монотонность** предиката (Junker, с. 168: «monotonic
    satisfiability property»; Rodler, Def. 1). Инварианты Rt ≥ 0 и ПДН ≤ 0,40 монотонны по
    снятию пользовательских требований. При СТРОГОМ ТОТАЛЬНОМ порядке требований
    предпочтительные конфликт и релаксация **единственны** — значит UX не обязан показывать
    пользователю выбор из множества объяснений.
15. 🔴 **SAW — частный случай MAVT, а MAVT не учитывает риск** (Omega-статья, §4, дословно).
    Наше разделение «SAW ранжирует — SES+Монте-Карло оценивает риск» методологически
    корректно. И отдельно: нормировка меняет фактический вес, уже заданный экспертами
    (там же, фактор (c)), — значит менять схему нормировки без перекалибровки весов нельзя.
16. 🔴 **Методологический пробел, вскрытый Бенгеном:** правило 4 % построено прогоном политики
    по ВСЕМ историческим стартовым датам с отчётом по ХУДШЕЙ когорте. У нас такого backtest'а
    по скользящим когортам на исторических рядах РФ нет, и он дешевле Монте-Карло.

## Замеры каналов, добавленные этим добором (для протокола)

- **cdn.aaai.org отдаёт труды AAAI напрямую**, шаблон `AAAI04-NNN.pdf`; номер статьи
  вычисляется подсчётом позиции в оглавлении `AAAI04-000.pdf` и проверяется соседями.
- **`r.jina.ai` НЕ пробивает Cloudflare** — подтверждено трижды: ACM DL (463 б),
  dentalage.co.uk (862 б), nottingham-repository (549 б). Он лечит антибот-заглушки
  издательских SPA (jclinepi, biomedcentral, rpc.cfainstitute сработали), но не Cloudflare.
- **Wayback с `id_` сработал дважды в этом доборе** (Landis & Koch; книга Linstone & Turoff),
  оба раза на файлах, недоступных на живом сайте. Точечный CDX по КОНКРЕТНОМУ URL работает;
  CDX с масками и фильтрами — **HTTP 403 «This type of CDX query requires authorization»**,
  а `archive.org/wayback/available` — **HTTP 429**.
- 🔴 **Частично скачанный PDF выглядит валидно по HTTP-коду.** arXiv:1810.11078 при `-m 60`
  дал HTTP 200 и 2 179 072 байта, но `pdftotext` выдал «Invalid XRef entry 0 / Top-level pages
  object is wrong type (null)». Проверять вывод `pdftotext` на ошибки, а не только код ответа
  и размер.
- **ScienceDirect: HTTP 403 при теле 832 805 байт** — подтверждён прежний замер сессии.
- **SSRN: HTTP 403 при теле 896 437 байт** — тот же класс, вопреки записи «SSRN берётся
  `curl`-ом»; на `papers.cfm` и на `Delivery.cfm` одинаково.
- **Unpaywall различает «не нашли» и «открытого доступа нет»** — за добор это дало пять
  твёрдых отрицательных результатов (`oa_status: closed`) вместо бесконечного перебора зеркал:
  Reiter (Elsevier), Felfernig (ACM), Landis & Koch (JSTOR), Feinstein (Elsevier), Fox и
  Federgruen (INFORMS), Michaud (FAJ).

**Конец добора Г4.**

---

## ДОБОР Г31.5 — отказ адреса (17.09.2026)

**Каналы на начало работы (замер 17.09.2026):** Unpaywall **200** · Crossref **200** · OpenAlex **200** · S2 `/paper/DOI:` **200** · S2 `search/bulk` **200** · Exa search **работает** · `r.jina.ai` без UA **200** · Wayback CDX: `josquin.cti.depaul.edu` **200**, `ist.tugraz.at` **200**, 🔴 `facweb.cs.depaul.edu` — **503 два раза подряд** (11 832 б, пауза 20 с) — записано как отказ ОДНОГО запроса CDX, не Wayback.

Кандидат класса по файлу — один: **Felfernig & Burke, ICEC '08** (последнее упоминание — стр. 1278: «ACM 403 на оба канала»; в Г4 этот пункт не перепроверялся — Г4 работал IUI '08, а не ICEC '08). Проверено, что «оба канала» означали ОДИН адрес `dl.acm.org/doi/pdf/…` двумя клиентами.

### Г31.5-C1. Felfernig & Burke ICEC '08 — ⛔ НЕ ДОБЫТ, но теперь по пройденным адресам, а не по одному

| Канал | Адрес | Код / размер | Итог |
|---|---|---|---|
| Unpaywall | `api.unpaywall.org/v2/10.1145/1409540.1409544` | **200** | `is_oa: False`, `oa_status: "closed"` |
| OpenAlex | `api.openalex.org/works/doi:10.1145/1409540.1409544` | **200** | `is_oa: False`, `any_repository_has_fulltext: False`, единственная локация — `doi.org` |
| S2 | `/graph/v1/paper/DOI:10.1145/1409540.1409544` | **200, 1 187 б** | `openAccessPdf.status: "CLOSED"`, `abstract: null` (изъят издателем), `citationCount: 310`, DBLP `conf/ACMicec/FelfernigB08`; 🟢 **`tldr` отдан** (ниже) |
| Exa search | запрос по точному заголовку + «ICEC 2008 pdf» | 10 результатов | только библиографические записи (researchr, Google Scholar, ссылки в чужих статьях); **открытой копии нет** |
| Exa fetch | `dl.acm.org/doi/pdf/10.1145/1409540.1409544` и `dl.acm.org/doi/10.1145/1409540.1409544` | `CRAWL_LIVECRAWL_TIMEOUT` оба | не отдано |
| `r.jina.ai` по ACM DL | — | не повторялся: замер Г4 (11.09.2026) на соседнем DOI того же хоста — 200/463 б, Cloudflare «Performing security verification» | ACM DL закрыт для прокси |
| Wayback CDX, страница автора Burke (старый хост) | `josquin.cti.depaul.edu/~rburke/*` | **200, 312 699 б** | ни одного файла с `felf/icec/constrain` в имени |
| Wayback CDX, страница автора Burke (новый хост) | `facweb.cs.depaul.edu/rburke/*` | **503, 503** | не проверено — ЗАДОЛЖЕННОСТЬ (см. ниже) |
| Wayback CDX, PDF TU Graz | `ist.tugraz.at/*`, `mimetype:application/pdf` | **200, 137 410 б** | ни одного файла `icec/burke/constraint-based` |

**S2 `tldr` ДОСЛОВНО** (машинная аннотация, не авторская — цитировать только с этой пометкой): «A taxonomy of recommendation knowledge sources and algorithmic approaches is introduced and the most prevalent techniques of constraint-based recommendation are discussed, and open research issues are outlined.»

**Выжимка.** Прежний статус «не прочитан в оригинале» остаётся, но основание сменилось с «ACM 403» на «легальной открытой копии не существует ни в одном индексе (Unpaywall, OpenAlex, S2), авторские страницы Burke (josquin) и TU Graz в архиве её не содержат». Уточнение реквизитов по DBLP/researchr: в ACM ICPS vol. 342 статья значится как **Article 3, 10 pages**; «pp. 17–26» встречается во вторичных ссылках (INTELLIREQ, OpenReq) — оба варианта описывают одну работу.

### Г31.5-C2. Felfernig et al. 2013 AI Communications (продолжение IUI '08) — подтверждено закрытым, но S2 дал содержание

Unpaywall `10.3233/AIC-120543` — **200**, `is_oa: False`, `closed`. S2 `/paper/DOI:` — **200, 1 468 б**, абстракт изъят, `citationCount: 20`, **`tldr` ДОСЛОВНО:** «This work presents an approach to the automated adaptation of utility constraint sets which is based on solutions for nonlinear optimization problems and increases the applicability of constraint-based recommendation technologies by allowing the automated reproduction of example item rankings specified by marketing and sales experts.»
Подтверждает вывод Г4 (стр. 1955–1962): работа — о **калибровке весов/скоринговых правил под эталонные ранжирования экспертов** через нелинейную оптимизацию, а не о ремонте пустого множества альтернатив.

## ИТОГ Г31.5 — constraint_based_utility_recsys

1 кандидат класса, **0 закрыто полным текстом, 1 переквалифицирован** из «отказ одного адреса» в «открытой копии нет ни в одном из пройденных индексов и авторских архивов» (+ `tldr` S2 по ICEC '08 и AIC 2013). Канон и новизна не затрагиваются: содержание ICEC '08 в файле уже снято с канонических пересказов тех же авторов (Handbook 2015), и найденный `tldr` им не противоречит.

**ЗАДОЛЖЕННОСТЬ по файлу:** Wayback CDX по `facweb.cs.depaul.edu/rburke/*` — два 503 подряд; повторить в следующей сессии. Arxiv `2102.09005` и `papers.phmsociety.org/…/1948/957` (заместители IUI '08, стр. 1968–1971) не скачивались и в этот заход — сознательно: пункт Г4.1, под который они шли, закрыт Junker/Reiter/Rodler, а IUI '08 признан не относящимся к Г4.1; для вопроса калибровки весов они не нужны (это алгоритмы диагностики, не калибровки).
