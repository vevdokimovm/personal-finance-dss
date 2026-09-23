Каналы 17.09.2026: r.jina.ai 200 · OpenAlex 200 · Crossref 200 · EuropePMC 200 · Semantic Scholar 429 (лежит) · pdftotext есть · Exa (mcp__exa) — работает (поиск Bacchelli & Bird вернул 5 результатов) · context7 — проба ниже.

# Г34 — Устойчивость к изменениям: что каждый вид проверки доказывает и что из нашего набора работает (17.09.2026)

Батч Г34 из `docs/research/queue/GAP_QUEUE.md`. Вход: Г33 (`engineering_standards_benchmark_2026-09-17.md`), Г32, Г47, Chen et al. из Г18. Сырьё пишется по ходу.

## Сырьё: код-ревью в Microsoft (Exa, 17.09.2026)

- Bacchelli & Bird, ICSE 2013, doi:10.1109/icse.2013.6606617, аннотация дословно: «Our study reveals that while finding defects remains the main motivation for review, reviews are less about defects than expected and instead provide additional benefits such as knowledge transfer, increased team awareness, and creation of alternative solutions to problems.»
- Czerwonka, Greiler, Tilford, «Code reviews do not find bugs», ICSE 2015 SEIP, аннотация дословно: «we posit (1) that code reviews often do not find functionality issues that should block a code submission; (2) that effective code reviews should be performed by people with specific set of skills».
- Bosu, Greiler, Bird, «Characteristics of Useful Code Reviews», MSR 2015 (https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/bosu2015useful.pdf), дословно: «The interviewees rated almost 69% comments as either useful or somewhat useful.» и «most of the review comments are unrelated to any types of functional defects.» и «These four all belong to the class termed “evolvability defects” as classified by Mantyla et al.»
- Greiler, MSR-TR-2016-27: причины ревью — «Code improvement 2835 (1) · Find defects 2749 (2) · Increase knowledge transfer 1528 (3)».

## Сырьё: что уже есть на входе (чтение репозитория, 17.09.2026)

- Г33 (`engineering_standards_benchmark_2026-09-17.md`): покрытие 90 % = Google «exemplary»; гейт по новому коду (diff-cover); мутации 68,7 % на 3 модулях ядра, `|| true`; Stryker 60/80; Google TSE 2021 — «85% of reported mutants as unproductive» → фильтрация «from 15% to 89%»; Inozemtseva & Holmes 2014; Papadakis 2018; import-linter нет; pre-commit гоняет весь pytest; три линтера; `alembic check` нет; `random.seed` глобальный. Здесь НЕ повторяется, только используется.
- Г18/Г4 (`prescriptive_quality_metrics_2026-09-10.md` стр. 332–380, 1112–1250): определение MR по Segura et al. TR ISA-16-TR-02 и Chen 1998; 8 кандидатов MR для FINPILOT (MR-1…MR-8).
- 🔴 **Г39 (`math_core_verification_plan_2026-09-17.md`, ИТОГ стр. 3168–3300) — самое сильное свидетельство для Г34, добытое на НАШЕМ коде.** При гейте покрытия ядра ≥95 % и обязательном TDD метаморфические отношения, инварианты Hypothesis, Z3 и стенды нашли **9 дефектов (Д-01…Д-09) и 4 подтверждённых наблюдения**, в т.ч.: Д-03 «масштаб ×10 меняет план 30/70 → 0/100» (MR09/MR03/MR14); Д-04 «победитель сменился в 13 из 28» (MR03/07/15); Д-07 «ядро молча считает на NaN» (проба входов); Д-09 «решающий критерий в объяснении неверен в 67,9 % советов» (тест верности); «ПДН-гейт не отвергает ни одной альтернативы при доходе > 0 — доказано Z3». Эти строки были **исполнены** тестами (покрытие ядра ≥95 %) — и ни один тест не знал, что ответ неверный. Это и есть проблема оракула на нашем материале.
- Г32 (`product_security_2026-09-17.md`) — фаззинг парсера и дыры `routes_banks.py` (не повторяю).
- Г47 (`bank_statement_corpus_2026-09-17.md`) — корпус выписок с эталонами, 6 негативных кейсов «Точки» — готовый материал для golden-тестов и посевного корпуса фаззинга.

## Сырьё П9/П3-а: инспекции, чек-листы, сравнительная результативность (OpenAlex + arXiv, 17.09.2026)

**Канал:** OpenAlex `works?search=` (HTTP 200, аннотации восстановлены из `abstract_inverted_index`), PDF Wagner — `curl` arXiv 200, 318 707 байт → `pdftotext`.

1. **Fagan M.E., «Design and code inspections to reduce errors in program development», IBM Systems Journal 15(3), 1976**, doi:10.1147/sj.153.0182 (1503 цитирования; полный текст закрыт, `oa_url: None`). Аннотация дословно: «Separate the objectives of the inspection process operations to keep the inspection team focused on one objective at a time: Operation Overview Preparation Inspection Rework Follow-up … 3. Classify errors by type, and rank frequency of occurrence of types. Identify which types to spend most time looking for in the inspection. 4. Describe how to look for presence of error types. 5. Analyze inspection results and use for constant process improvement». Процентов обнаружения в аннотации нет; числа по инспекциям — из обзоров ниже.
   Что важно для нас: суть Fagan — не «прочитать внимательно», а **(а) классифицировать ошибки по типам и частоте, (б) искать приоритетно самые частые типы, (в) измерять результат инспекции и управлять процессом по числам**. Наш `PIT-*` — это пункт (а), но без (в).

2. 🔴 **Porter, Votta, Basili, «Comparing detection methods for software requirements inspections: a replicated experiment», IEEE TSE 21(6), 1995**, doi:10.1109/32.391380 (441 цит.). Дословно: «(1) the Scenario method had a higher fault detection rate than either Ad Hoc or Checklist methods, (2) Scenario reviewers were more effective at detecting the faults their scenarios are designed to uncover, and were no less effective at detecting other faults than both Ad Hoc or Checklist reviewers, (3) **Checklist reviewers were no more effective than Ad Hoc reviewers**, and (4) **Collection meetings produced no net improvement in the fault detection rate**-meeting gains were offset by meeting losses.» Выборка: «Forty eight graduate students… sixteen, three-person teams» (требования, не код).

3. 🔴 **Hatton L., «Testing the Value of Checklists in Code Inspections», IEEE Software 25(4), 2008**, doi:10.1109/ms.2008.100. Дословно: «using data from 308 inspections by industrial engineers over a three-year period. **The results showed no evidence that checklists significantly improved these inspections.** Further analysis revealed that individual inspection performance varied by a factor of 10 in terms of faults found per unit time, and **individuals found on average about 53 percent of the faults. Two-person teams found on average 76 percent of the faults.**»
   → 🔴 **Посылка постановки «по данным — чек-лист находит больше» ОПРОВЕРГНУТА** двумя независимыми работами (эксперимент 1995 и промышленные данные 2008). Больше находит **сценарий/перспектива** — чтение с конкретной задачей «ищи класс X так-то», и **второй человек** (53 % → 76 %).

4. **Runeson, Andersson, Thelin, Andrews, Berling, «What do we know about defect detection methods?», IEEE Software 23(3), 2006**, doi:10.1109/ms.2006.89. Дословно: «A survey of defect detection studies comparing inspection and testing techniques yields practical recommendations: **use inspections for requirements and design defects, and use testing for code.**»

5. 🔴 **Wagner S., «A literature survey of the quality economics of defect-detection techniques», ISESE 2006**, doi:10.1145/1159733.1159763, arXiv:1612.04590 (PDF 200). Сводные таблицы дословно:
   - Табл. 1, результативность тестовых техник (% найденных дефектов): «Functional 33 / 53.26 / 48.85 / 88 · Structural 17 / 54.78 / 56.85 / 89 · All 7.2 / 49.85 / 47 / 89» (мин/среднее/медиана/макс); «When comparing functional and structural testing, **there is no significant difference visible**.»
   - Табл. 2, производительность тестов (дефектов на человеко-час): «Functional 1.22 / 1.72 / 1.71 / 2.47 · Structural 0.22 / 1.5 / 2.07 / 2.2 · All 0.04 / 1.26 / 1.5 / 2.47».
   - Табл. 7, результативность инспекций (%): «8.5 / 34.14 / 30 / 92.7»; «We observe a quite stable mean value that is close to the median with about 30%. However, the range of values is huge. This suggests that an inspection is dependent on other factors to be effective.»
   - Табл. 8, производительность инспекций (дефектов/чел.-ч): «0.16 / 1.87 / 1.18 / 6».
   - Статанализ: «the average ratio of false positives over three tools for Java was 66% ranging from 31% up to 96%»; «After eliminating the false positives, the tools were able to find 81% of the known defects… However, the defects had mainly a low severity. **For the severest defects the effectiveness reduced to 22%**, for the second severest defects even to 20%.» Вывод: статанализ «seem to be better in total but much worse considering severe defects».
   - Стоимость устранения (чел.-ч на дефект): инспекции кода «Coding 0.17 / 2.71 / 1.95 / 6.3»; юнит-тесты ≈3,5; системный тест ≈8; **дефекты из эксплуатации «3.9 / 57.42 / 27.6 / 250»** — «The field defects are then more than three times as expensive with 27 staff-hours.»
   - Со ссылкой на Jones: «A series of well-planned tests by a professionally staffed testing group can exceed 35 percent per stage, and 80 percent in overall cumulative testing efficiency.»

**Что это значит (предварительно, до сверки с ревью Google/Microsoft).** Аналогия: каждый вид проверки — сито с дырками своей формы; одно сито ловит 30–55 % дефектов, и ловят они **разные** дефекты. Отсюда главный закон всей области: **результативность набирается последовательностью разных сит, а не шлифовкой одного**. По дефектам на час тесты и инспекции близки (1,3–1,9 деф./ч в среднем), статанализ дешёв, но слеп к тяжёлым дефектам (22 %). Дефект, доживший до эксплуатации, стоит в 8–10 раз дороже (27,6 ч медиана против 2–3,5 ч).

## Сырьё П9-б: что реально находит современное ревью и как Google решает, что проверка бесполезна (Exa `web_fetch_exa` + r.jina.ai, 17.09.2026)

**Каналы:** Exa fetch — 3 URL (CACM — обрезан до 30 000 знаков куки-баннером; sback.it PDF Sadowski 2018 — текст; microsoft.com PDF Czerwonka 2015 — текст); r.jina.ai на CACM — HTTP 200, 58 172 байта, полный текст.

1. 🔴 **Czerwonka, Greiler, Tilford, «Code Reviews Do Not Find Bugs: How the Current Code Review Best Practice Slows Us Down», ICSE 2015 SEIP** (https://www.microsoft.com/en-us/research/wp-content/uploads/2015/05/PID3556473.pdf). Дословно:
   - «**Only about 15% of comments provided by reviewers indicate a possible defect, much less a blocking defect.** Rather, it is feedback related to the long-term code maintainability that comprises a much larger portion of comments provided by reviewers; at least 50% of all.»
   - «Without prior exposure to the part of code base being reviewed, on average only 33% of any reviewer's comments are deemed useful by the author of a change. However, reviewers typically learn very fast. When reviewing the same part of code base for the third time, the usefulness ratio increases to about 67% of their comments.»
   - «Code review usefulness is negatively correlated with the size of a code review… The decrease however only starts to be noticeable for reviews with 20 or more changed files.»
   - «The median time from a review being requested to receiving all necessary sign-offs is about 24 hours».

2. **Sadowski, Söderberg, Church, Sipko, Bacchelli, «Modern Code Review: A Case Study at Google», ICSE-SEIP 2018**, doi:10.1145/3183519.3183525 (https://sback.it/publications/icse2018seip.pdf). Аннотация: «12 interviews, a survey with 44 respondents, and the analysis of review logs for 9 million reviewed changes». Дословно: «we identified four key themes for what Google developers expect from code reviews: **education, maintaining norms, gatekeeping, and accident prevention**»; «the main focus at Google, as explained by our participants, is on education as well as code readability and understandability»; из сводки сходящихся практик Rigby & Bird: «CP3 Change sizes are small», «CP4 Two reviewers find an optimal number of defects».

3. 🔴 **Sadowski, Aftandilian, Eagle, Miller-Cushon, Jaspan, «Lessons from Building Static Analysis Tools at Google», CACM 61(4), 2018**, doi:10.1145/3188720. Дословно:
   - Определение: «We consider an issue to be an “**effective false positive**” if developers did not take positive action after seeing the issue… Developers, not tool authors, will determine and act on a tool's perceived false-positive rate.»
   - Провал дашборда: «Although FindBugs found hundreds of bugs in Google's Java codebase, the dashboard saw little use because a bug dashboard was outside the developers' usual workflow»; Fixit-неделя: «They reviewed a total of 3,954 such warnings (42% of 9,473 total), but **only 16% (640) were actually fixed**».
   - Раньше — лучше: «survey participants deemed **74% of the issues flagged at compile time as “real problems,” compared to 21% of those found in checked-in code**… This result is explained by the “survivor effect”».
   - Критерий блокирующей проверки: «A compiler check at Google should be easily understood; actionable and easy to fix…; **produce no effective false positives (the analysis should never stop the build for correct code)**; and report issues affecting only correctness rather than style or best practices.»
   - Критерий предупреждения в ревью: «**Produce less than 10% effective false positives.** Developers should feel the check is pointing out an actual issue at least 90% of the time»; стиль — в ревью, а не в сборке: «reporting them at compile-time is frustrating for developers».
   - 🔴 **Механизм отключения бесполезной проверки:** «The Tricorder team tracks such not-useful clicks, computing the ratio of “Please fix” vs. “Not useful” clicks. **If the ratio for an analyzer goes above 10%, the Tricorder team disables the analyzer until the author(s) improve it.**» Масштаб: «approximately 50,000 code review changes per day… Reviewers clicked “Please Fix” more than 5,000 times per day… “Not useful” clicks 250 times per day.»

4. **Bosu, Greiler, Bird, MSR 2015** (уже выше): «most of the review comments are unrelated to any types of functional defects»; полезные — функциональные дефекты и «validation issues or alternate scenarios (i.e. corner cases)».

**Что это значит.** Аналогия: ревью — это не металлоискатель, а наставник. Человеческое ревью в индустрии **находит в основном сопровождаемость (≥50 % замечаний), дефекты — ~15 %**, а его главная ценность по Google — обучение и нормы. Значит, ставить человеческое/агентное ревью как «главную защиту от поломок» — ошибка по данным; его место — понятность, архитектура, крайние случаи. Для гейтов у Google есть **измеримое правило**: блокирующая проверка — ноль ложных остановок; предупреждение — не больше 10 % «не полезно»; всё, что выше, выключается до починки. Это и есть ответ на вопрос «как понять, что гейт бесполезен».

## Сырьё П2/П3: результативность поведенческих методов, покрытие, типы, флаки (OpenAlex + Exa, 17.09.2026)

### Покрытие как мера (структурные меры)
- **Kochhar, Lo, Lawall, Nagappan, «Code Coverage and Postrelease Defects: A Large-Scale Study on Open Source Projects», IEEE Trans. Reliability 66(4), 2017**, doi:10.1109/tr.2017.2727062. Дословно: «We analyze 100 large open-source Java projects… Our results show that **coverage has an insignificant correlation with the number of bugs that are found after the release of the software at the project level, and no such correlation at the file level**.»
- **Chekam, Papadakis, Le Traon, Harman, «An Empirical Study on Mutation, Statement and Branch Coverage Fault Revelation That Avoids the Unreliable Clean Program Assumption», ICSE 2017**, doi:10.1109/icse.2017.61. Дословно: «our primary finding is that **strong mutation testing has the highest fault revelation of four widely-used criteria**. Our findings also revealed that **fault revelation starts to increase significantly only once relatively high levels of coverage are attained**.»
- **Just, Jalali, Inozemtseva, Ernst, Holmes, Fraser, «Are mutants a valid substitute for real faults in software testing?», FSE 2014**, doi:10.1145/2635868.2635929 (602 цит.). Дословно: «Our experiments used 357 real faults in 5 open-source applications that comprise a total of 321,000 lines of code… The results show **a statistically significant correlation between mutant detection and real fault detection, independently of code coverage**.»
- (MC/DC и DO-178C — первоисточник платный, в этом батче не открывался; см. «Осталось неизвестным».)
- Сводка Wagner 2006 (выше): «When comparing functional and structural testing, there is no significant difference visible» (53 % против 55 % в среднем).

**Вывод по структурным мерам:** покрытие — **необходимое условие** (Chekam: дефекты начинают находиться «only once relatively high levels of coverage are attained»), но **не мера качества** (Kochhar: нет связи с дефектами после релиза на уровне файла; Inozemtseva — в Г33). Мутационный балл связан с реальными дефектами независимо от покрытия (Just 2014), но слабо при контроле размера набора (Papadakis 2018, в Г33).

### Проблема оракула
- **Barr, Harman, McMinn, Shahbaz, Yoo, «The Oracle Problem in Software Testing: A Survey», IEEE TSE 41(5), 2015**, doi:10.1109/tse.2014.2372785 (1096 цит.). Дословно: «Given an input for a system, the challenge of distinguishing the corresponding desired, correct behaviour from potentially incorrect behavior is called the “test oracle problem”… The literature on test oracles has introduced techniques for oracle automation, including **modelling, specifications, contract-driven development and metamorphic testing**. When none of these is completely adequate, **the final source of test oracle information remains the human**».

### Метаморфическое тестирование
- **Liu, Kuo, Towey, Chen, «How Effectively Does Metamorphic Testing Alleviate the Oracle Problem?», IEEE TSE 40(1), 2014**, doi:10.1109/tse.2013.46 (208 цит.). Дословно: «identification of a sufficient number of appropriate metamorphic relations for testing, **even by inexperienced testers, was possible with a very small amount of training**… the empirical studies presented in this paper clearly show that **a small number of diverse metamorphic relations, even those identified in an ad hoc manner, had a similar fault-detection capability to a test oracle**».
- MR для денег и рекомендаций — найдены работы (Exa):
  - **Rahman, Izurieta, «An Approach to Testing Banking Software Using Metamorphic Relations», IEEE IRI 2023**, doi:10.1109/iri58017.2023.00036: «we introduce new metamorphic relations to test banking functions and demonstrate the effectiveness of using these MRs».
  - **Mao, Yi, Chen, «Metamorphic Robustness Testing for Recommender Systems: A Case Study», DSA 2020**, doi:10.1109/dsa51864.2020.00060: «five types of metamorphic relations are proposed… taking a well-known recommender library LibRec as an example… effective in revealing the robustness problem».
  - **Khirbat, Ren, Castells, Sanderson, arXiv:2411.12121 (2024)**: MR «rating multiplication, rating shifting» для рекомендаций; сходство выхода — «Kendall and Ranking Biased Overlap (RBO)».
  - **Ying, Bellotti, Breeden, Towey, «Metamorphic Testing and exploration for Machine Learning credit score models», IST 2025**, doi:10.1016/j.infsof.2025.107903: «all three models often violate MRs… **Traditional metrics fail to capture these violations**».
  - **«Metamorphic Testing and Debugging of Tax Preparation Software», ICSE-SEIS 2023** (doi:10.1109/ICSE-SEIS58686.2023.00019): «specifications… are naturally available as properties on the software requiring **similar inputs provide similar outputs**»; «Our tool uncovered several accountability bugs… from nonrobust behavior in corner-cases (**unreliable behavior when tax returns are close to zero**) to missing eligibility conditions».
  - «Testing multiple linear regression systems with metamorphic testing» (Monash): «propose 11 Metamorphic Relations… effectiveness is examined using mutation analysis».

### Property-based (Hypothesis)
- 🔴 **Ravi, Coblenz, «An Empirical Evaluation of Property-Based Testing in Python», OOPSLA 2025 (PACMPL 9, art. 412)**, doi:10.1145/3764068 (PDF https://cseweb.ucsd.edu/~mcoblenz/assets/pdf/OOPSLA_2025_PBT.pdf через Exa). Дословно: «a corpus study of 426 Python programs that use Hypothesis… evaluated the efficacy of test suites of 40 projects using mutation testing, and found that **on average, each property-based test finds about 50 times as many mutations as the average unit test**… tests that look for exceptions, that test inclusion in collections, and that check types are over 19 times more effective… **76% of mutations found were found within the first 20 inputs**.» Инструмент — «We used the tool mutmut». Оговорки авторов: «The effect size, calculated as Cramér's V, is 0.05… this is a weak association»; в сумме «Unit tests comprised 98.4% of our sample and killed 84.7% of the total mutations found, while PBTs (comprising 1.6%) killed 15.3%»; из артефакта: «55% of mutations were found with a single input… 86% within the first 100 inputs, and 96% within the first 350 inputs».
- **Corgozinho et al., «Property-based testing in Python: empirical insights», EMSE 2026**, doi:10.1007/s10664-026-10953-w: «the main challenges developers face concern **data generation strategies (36.62%)**»; Ghostwriter «only 18.23% were fully automatable».

### Фаззинг HTTP по схеме
- **Hatfield-Dodds, Dygalo, «Deriving semantics-aware fuzzers from web API schemas», ICSE-Companion 2022**, doi:10.1145/3510454.3528637: «We present Schemathesis… Our evaluation, **thirty independent runs of eight tools against sixteen containerized open-source web services, shows that Schemathesis wildly outperforms all previous tools**.» (Авторы — сами авторы инструмента; независимое сравнение ниже.)
- **Kim, Xv, Sinha, Orso, «Automated test generation for REST APIs: no time to rest yet», ISSTA 2022**, doi:10.1145/3533767.3534401: «a set of 10 state-of-the-art REST API testing tools… applied… to a benchmark of 20 real-world open-source RESTful services and analyzed their performance in terms of code coverage achieved and unique failures triggered.» (Рейтинг из тела статьи в этом батче не снят.)

### Дифференциальное тестирование
- **Rigger, Su, «Detecting optimization bugs in database engines via non-optimizing reference engine construction» (NoREC), ESEC/FSE 2020**, doi:10.1145/3368089.3409710: «on four widely-used DBMS, namely PostgreSQL, MariaDB, SQLite, and CockroachDB. We found **159 previously unknown bugs**… 141 of which have been fixed». Это дифференциальное тестирование **самих СУБД**, не кода поверх них: наш прогон «SQLite против PostgreSQL» — родственная, но другая вещь (ловит **расхождение диалектов под нашим ORM-кодом**, а не баги СУБД).

### Статическая типизация
- **Khan, Chen, Nadi, Bailey, «An Empirical Study of Type-Related Defects in Python Projects», IEEE TSE 48(8), 2022**, doi:10.1109/tse.2021.3082068: «we mine… 210 Python projects… **We observe that 15 percent of the defects could have been prevented by mypy**… the redefinition of Python references, dynamic attribute initialization and incorrectly handled Null objects are the most common causes».
- **Gao, Bird, Barr, «To Type or Not to Type», ICSE 2017**, doi:10.1109/icse.2017.75: «both Flow 0.30 and TypeScript 2.0 successfully detect 15%!» (публичные JS-баги, прошедшие тесты и ревью).

### Флаки
- **Micco, Google Testing Blog, 27.05.2016** (https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html): «a continual rate of about **1.5% of all test runs** reporting a "flaky" result»; «**Almost 16% of our tests** have some level of flakiness»; «about **84% of the transitions we observe from pass to fail involve a flaky test**»; «It is human nature to ignore alarms when there is a history of false signals»; карантин: «automatically quarantines the test… could easily mask a real race condition».
- **Listfield, Google Testing Blog, 17.04.2017**: «around 4.2 million tests… around 63 thousand have a flaky run over the course of a week»; «**0.5% of our small tests were flaky, 1.6% of our medium tests were flaky, and 14% of our large tests were flaky**»; «the larger the test… the more likely it is to be flaky».

## Сырьё П5/П8: выбор тестов по изменению и автоматическое ревью (Exa, 17.09.2026)

### Выбор подмножества тестов
- **Machalica, Samylkin, Porth, Chandra, «Predictive Test Selection», ICSE-SEIP 2019**, doi:10.1109/icse-seip.2019.00018 (arXiv:1810.05286). Дословно: «Deployed in production, the strategy reduces the total infrastructure cost of testing code changes by a factor of two, while guaranteeing that **over 95% of individual test failures and over 99.9% of faulty changes** are still reported»; «selects fewer than a third of the tests that would be selected on the basis of **build dependencies**»; «Note that **any faulty change that makes it into the master branch will be detected in the stabilization stage**»; о флаках: «| FlakedTests(d)| is about four times larger than … | FailedTests(d)|».
  → Отраслевая база отбора — **транзитивный граф зависимостей** («all tests that transitively depend on modified code»), а сокращение поверх него обязательно подстраховано **полным прогоном позже**. Наш `_affected_tests.py` берёт только **прямые** вхождения имени модуля в `tests/**` (грep по строке) — это уже, чем граф зависимостей; подстраховка полным прогоном у нас есть (preflight-церемония / CI).

### Автоматическое (LLM) ревью — для процесса на одного
- **«Automated Code Review In Practice», ICSE-SEIP 2025**, arXiv:2412.18531 (Qodo PR Agent, промышленная компания, 4 335 PR): «**73.8% of automated code review comments were labeled as resolved**… the overall average pull request closure duration increased from five hours 52 minutes to eight hours 20 minutes»; «26.2% of the tool comments were not acted upon»; недостатки — «faulty reviews, unnecessary corrections, and irrelevant comments».
- **Atlassian RovoDev, arXiv:2601.01129**: «54,000 generated code review comments over a year… **38.70% of its comments leading to code changes**»; для сравнения у людей «44.45%»; «reducing median pull request cycle time by 30.8%».
- **Olewicki et al., arXiv:2411.07091 (Mozilla, Ubisoft)**: «**8.1% and 7.2%**… of LLM-generated comments were accepted»; «Refactoring-related comments are more likely to be accepted than Functional comments (18.2% and 18.6% compared to 4.8% and 5.2%)».
- **CodeRabbit в дикой природе, arXiv:2607.03316**: «31,073 pairs… **36.4% were accepted**… 56.3% were rejected»; причины отказа — «false positive issues (43.3%)»; «in 43.4% of false-positive cases, the agent fails to understand the specific section of code that is directly under review»; «agentic reviews tend to focus more on functional concerns… yet they were more likely to be invalid».
- **16 AI-ревью-экшенов на GitHub, arXiv:2508.18771**: «22,000 review comments in 178 repositories»; адресовано «0.9%–19.2%» валидных ИИ-замечаний против «60%» человеческих; «Comments that are concise, contain code snippets, and are **manually triggered**… are more likely to result in code changes».
- ⚠️ Исключено как недостоверное: johal.in «Claude Code vs. Human Reviewers… 500 Production Pull Requests» — блог без рецензии, несуществующая версия «Claude Code v20240501», маркетинговые обобщения («By 2026, 70%…»). Не используется.

**Вывод для соло.** Автоматический ревьюер (агент) — реальная замена второй паре глаз **по сопровождаемости и части багов**, но с измеренной долей мусора 26–56 %; принимаются чаще короткие, привязанные к строкам, запущенные вручную замечания; функциональные замечания ИИ — самые ненадёжные. Значит, агент-ревьюер полезен как **сценарный** проверяющий (узкая задача: «ищи класс X») — это совпадает с выводом Porter 1995 о сценарном чтении — и его польза должна **измеряться долей принятых замечаний**, как у Google (правило 10 %).

## Сырьё П1/П2: MC/DC, сетки безопасности (характеризующие тесты, диф OpenAPI, слои), разбор инцидентов (Exa + context7 + r.jina.ai, 17.09.2026)

### MC/DC (авиационный DO-178B/C)
- **Dupuy, Leveson, «An empirical evaluation of the MC/DC coverage criterion on the HETE-2 satellite software», DASC 2000**, doi:10.1109/dasc.2000.886883 (PDF umich.edu через Exa). Дословно: «the test cases generated to satisfy the MC/DC coverage requirement **detected important errors not detectable by functional testing**… although MC/DC coverage testing took a considerable amount of resources (**about 40% of the total testing time**), it was not significantly more difficult than satisfying condition/decision coverage»; непокрытое — «primarily involved error-handling».
- **Heimdahl, Whalen, Rajan, Staats, «On MC/DC and implementation structure», DASC 2008**, doi:10.1109/dasc.2008.4702848: «the effectiveness of the test suites was **highly sensitive to the structure of the implementation**… (The inlined test suites outperformed the non-inlined test suites in the range of 10% to 5940%.)»; «A statement such as “We have completed testing up to Masking MC/DC and revealed no critical faults” **has little meaning unless there is a discussion about the nature of the oracle used**.»
- **Gay et al., ACM TOSEM 2016**, doi:10.1145/2934672: «structural coverage criteria, including MC/DC, can easily be “**cheated**” by restructuring a program».
- **Kapoor, Bowen, ISESE 2003**, doi:10.1109/isese.2003.1237977: «the MC/DC criterion is more reliable and stable in comparison to DC, DC/R and FPC.»
→ Для нас: MC/DC — сильнейшая из структурных мер для **составных логических условий** (у нас: гейты фильтрации, условия кризисного режима, «токсичный первым»), но и она «обманывается» переписыванием кода и ничего не значит без оракула. В Python готового MC/DC-инструмента в `coverage.py` нет (есть только ветви, `--branch`; у нас выключены — Г33 Р1 п. 8). Цена/польза для нас — ниже, чем у мутаций, которые делают то же (порча условия `and`→`or` — стандартный мутант).

### Характеризующие (golden / approval) тесты
- **Feathers, «Characterization Testing», 08.08.2016** (https://michaelfeathers.silvrback.com/characterization-testing): «**The purpose of characterization testing is to document your system's actual behavior, not check for the behavior you wish your system had.**»; «When a system goes into production, in a way, it becomes its own specification.»
- **Feathers, «Working Effectively With Legacy Code»** (objectmentor PDF): «A ''test covering'' is a set of tests used to introduce an invariant on a code base… **correct behavior is defined by what the set of classes did yesterday**, not by any external standard of correctness»; стратегия: «1. Identify change points 2. Find an inflection point 3. Cover the inflection point… 4. Make changes 5. Refactor the covered code.»
- **Wikipedia «Characterization test»**: «also known as Golden Master Testing… In James Bach's and Michael Bolton's classification of test oracles, this kind of testing corresponds to the **historical oracle**»; «Golden Master testing does not imply correctness of the results»; ограничение — «It depends on repeatability. Volatile and non-deterministic values need to be masked».
→ Эталонный файл — это **исторический оракул**: ловит «изменилось», не «неверно». Поэтому он идеален там, где правильный ответ **известен извне** (выписка банка → ожидаемые транзакции из Г47: это уже не исторический, а **внешний** эталон) и для рефакторинга ядра (Д-01…Д-09 будут чиниться — перед правкой нужен снимок поведения на фиксированных портретах, чтобы видеть, что поменялось ВСЁ, что должно, и НИЧЕГО лишнего).

### Машинное обнаружение ломающих изменений API
- **oasdiff, `docs/BREAKING-CHANGES.md`** (GitHub, Exa): «The `oasdiff breaking` command displays the changes that break existing API clients… typically used in the CI to report or prevent breaking changes»; «Oasdiff supports **hundreds of checks**… `ERR` - Errors are definite breaking changes»; «**adding a required request property is breaking**»; «To exit with return code 1 if ERR-level changes are found, add the `--fail-on ERR` flag.» GitHub Action: «`review: false` to keep everything inside your CI».
- У нас: `tests/test_generated_client_matches_snapshot.py` — **обнаружение дрейфа** (снимок ≠ живое приложение) «по множеству путей и имён схем». Это не то же самое: дрейф ловит «забыл обновить снимок», а oasdiff — «обновил снимок, и он ломает клиента». При одном своём фронте, генерируемом из снимка, ломающее изменение ловит ещё `tsc` фронта; oasdiff нужен, когда появятся **внешние** потребители — B2B `/v1` (у нас есть).

### Архитектурные фитнес-функции
- **import-linter, документация (context7 `/seddonym/import-linter`)**: контракт `type = "layers"` с упорядоченным списком слоёв; есть `exhaustive = true` и готовый pre-commit-хук `lint_imports`. Норма и цена — в Г33 (1–2 ч + исправления), не повторяю.

### Разбор инцидентов
- **Google SRE Book, «Postmortem Culture»** (https://sre.google/sre-book/postmortem-culture/, r.jina.ai 200): «The primary goals of writing a postmortem are to ensure that the incident is documented, that all contributing root cause(s) are well understood, and, especially, that **effective preventive actions are put in place**»; «It is important to **define postmortem criteria before an incident occurs**»; «Blameless postmortems are a tenet of SRE culture»; после ревью «the postmortem is added to a team or organization repository of past incidents».
- **ODC** (Chillarege et al. 1992) — первоисточник в батче не открывался; упоминание — через Wagner 2006: «six error types accounted for nearly 80% of the highest severity defects… They used ODC for classification.»

### Мёртвый код
- `vulture` README через r.jina.ai — ответ без искомых строк (grep пуст), дословных цитат нет; нормы для мёртвого кода — в Г33 (Р1 п. 11: «список, без порога»). Отдельно в этом батче не добывалось.

## П9-наш. 🔴 Сверка НАШЕГО порядка ревизии и гейтов с практикой (чтение репозитория, 17.09.2026, без запуска)

Прочитано: `tools/preflight.py` (250 строк), `tools/revision/revision_check.py` (608), `.claude/settings.json` (регистрация хуков), `.claude/hooks/tests-gate.sh`, `_affected_tests.py`, `lint-python.sh`, `.claude/agents/*.md` (4), `docs/pitfalls.md` (912 строк, 35 записей PIT), `docs/reports/recurrence_ledger.md`, `docs/reports/incidents_summary.md`, `docs/reports/audits/independent_expert_cycle_log.md`, `docs/reports/mutation_pilot_2026-09-16.md`, `.pre-commit-config.yaml`, `.flake8`, `.github/workflows/ci.yml`, `git config core.hooksPath`.

### Что у нас на самом деле проверяет каждый контур

| Контур | Что проверяет по коду | Класс по таксономии | Поведение продукта? |
|---|---|---|---|
| `python -m tools.preflight` | совпадение версий в 5 местах, окно WATCHLOG = 10, мягкие переносы, `&& grep` в скриптах, `.repo-id`, префикс `VERSION`, + `revision_check` | согласованность документов и церемонии | **нет** — сам файл пишет: «не подтверждает, что поведение верное. Он ловит ceremony-дрейф и известные грабли» |
| `revision_check` | битые ссылки, упоминания старого канона, CJK-канарейка, счётчики таблиц/миграций/путей OpenAPI, коллизии регистра | статическая проверка документов | нет |
| Stop-хук `tests-gate.sh` | тесты файлов, изменённых в сессии (`_affected_tests.py`: grep имени модуля по `tests/**`), + маркер `property` | выбор тестов по изменению | да, срез |
| `lint-python.sh` | flake8 на записанный файл, **не блокирует** | статанализ стиля | нет |
| хуки `block-*`, `check-design-tokens`, `exa-gate`, `research-channels-gate`, `websearch-budget` | секреты, разрушительные команды, токены дизайна, каналы добычи | защита процесса, не кода | нет |
| CI `core`/`fast`/`full`/`deep` | покрытие ≥95/≥90 %, матрица SQLite+PG, E2E, мутации | тесты | да |
| агенты `design-critic`, `a11y-auditor`, `api-contract-guard` | чтение по узкому чек-листу | ревью-сценарий | частично (интерфейс, контракт) |
| агент `independent-expert` | «разрыв между задуманным и работающим» | **сценарное чтение** (Porter 1995) | да |
| `docs/pitfalls.md` + `recurrence_ledger.md` | ошибки **воркфлоу ассистента** | реестр классов с эскалацией | нет — «продукт не затронут» (шапка файла) |
| `incidents_summary.md` | дефекты продукта | разбор инцидентов | да, постфактум |

### Что соответствует практике (с опорой)

1. **Эскалация «проза → правило → машина» (`recurrence_ledger.md` §1)** — совпадает с Fagan («Classify errors by type, and rank frequency… Identify which types to spend most time looking for») и с Google («Moving as many checks into the compiler as possible is one proven way»; «74%… at compile time… compared to 21%… in checked-in code»). Это самая сильная часть нашей методики.
2. **`independent-expert` — это и есть сценарное чтение**, которое по Porter 1995 находит больше, чем чек-лист и свободное чтение, и он **единственный наш ревью-контур с измеренным выходом**: 9 проходов, **58 гипотез, 11 уровня SEV, «ни один проход не вернул пусто»**; по статусам в журнале — 🟢 33 и 🔴 16 строк (включая 2 строки легенды), ⚪ опровергнутых 1 строка (легенда) — т.е. опровергнутых гипотез практически нет. Нашёл ровно тот класс, который, по Bosu 2015, авторы считают самым полезным («validation issues or alternate scenarios (i.e. corner cases)»), и класс, который тесты не видят в принципе (CONSENT-GATE-NO-UI: гейт работал, экрана не было 26 дней).
3. **«Мутация после каждой починки»** (журнал эксперта, «Приёмы, которые сработали») и `mutation_pilot` — это то, что Google называет правильным употреблением мутаций: выжившие мутанты на изменённом коде как задачи, а не балл.
4. **Подмножество тестов на Stop + полный прогон позже** — та же схема, что у Facebook («any faulty change that makes it into the master branch will be detected in the stabilization stage»).
5. **Разделение INC / INV / PIT и реестр инцидентов** — совпадает с SRE («repository of past incidents»), разборы без поиска виноватых.
6. **Честная самоаттестация** в коде гейтов (preflight пишет, чего НЕ проверяет; PIT-017 «гейт, который заявлен как проверяющий X, но X не проверяет, хуже отсутствующего») — это формулировка той же мысли, что у Google про «effective false positives».

### Что держится на вере (с фактами)

1. 🔴 **Выход гейтов не измеряется вообще.** Ни у одного гейта нет счётчика «сработал → был реальный дефект / был ложным». У Google это главный рычаг: «If the ratio for an analyzer goes above 10%, the Tricorder team disables the analyzer». У нас задокументированы **четыре ложных срабатывания гейтов**, каждое оформлено как грабли, а не как метрика гейта: PIT-021 («ЛОЖНОЕ красное: гейт воспроизвёл чужую семантику приблизительно»), PIT-023 («хук судит по СЛОВУ в команде»), PIT-026 («комментарий, объясняющий запрет, роняет проверку»), PIT-030 («гейт проверял строку рядом с той, что врала»); плюс два ложняка гейта поиска 09.09.2026 (CLAUDE.md, правило 11), и хук PIT-018 блокирует в этом самом батче команду, где путь стоит после `=` (ложное срабатывание, замерено 17.09.2026).
2. 🔴 **Самый дорогой инцидент проекта устроил гейт документов, а не код.** CI-RED-41-DAYS: «`revision_check`/`preflight` падал на КАЖДОМ пуше… Гейт падал ДО запуска `pytest` — весь unit+integration+property набор не выполнялся в CI ни разу за 65 версий». Проверка регистра имени файла глоссария остановила все поведенческие проверки на 41 день. По Google-критерию блокирующей проверки («produce no effective false positives… should never stop the build for correct code») это недопустимо. Сейчас джобы в `ci.yml` без `needs:` — связь снята, но правило «гейт документов не может заслонять тесты» нигде не записано.
3. 🔴 **Правило «понижать уровень нельзя» (`recurrence_ledger.md` §1) противоположно практике.** Google выключает шумную проверку до починки; у нас снять автопроверку можно «только вместе с исчезновением причины». Это механизм накопления налога: гейты только добавляются (в журнале эксперта — «заведено гейтов против рецидива: 14»), выхода у них нет.
4. **Реестр рецидивов считает ошибки ассистента, а не дефекты продукта.** Шапка `pitfalls.md`: «продукт не затронут». Для продуктовых дефектов (INC-*, Д-01…Д-09) нет разметки «каким методом найден / какой метод нашёл бы раньше» (аналог ODC-«триггера»). Поэтому на вопрос владельца «ловят ли наши гейты» у нас нет своих чисел — только эпизоды. Из эпизодов видно: CONSENT-GATE — нашёл независимый эксперт; INC-NULL-DEADLINE и BUG-026 — ревью/чтение; INC-CRUD-DELETE — «сломано несколько версий при зелёных юнит-тестах», поймали E2E; PG-дедлок — матрица PG; BUG-028 — календарь (машина времени); INC-A11Y-DEADTEST — «зелёный за счёт skip»; Д-01…Д-09 — MR/инварианты/Z3/стенды при покрытии ядра ≥95 %. **Ни один продуктовый дефект в реестре не найден preflight или `revision_check`.**
5. **Документ о гейте расходится с гейтом:** `recurrence_ledger.md` §3 перечисляет «`flake8` по `app/ tools/ tests/`» среди проверок preflight — в `tools/preflight.py` flake8 не вызывается (тот же класс, что PIT-017/PIT-030).
6. 🔴 **`.pre-commit-config.yaml` — «чеховское ружьё», а не налог (поправка к Г33).** `git config core.hooksPath` = `_base/.githooks` (там `pre-commit` на секреты/тяжёлые файлы и `commit-msg`), в `.git/hooks/` — только `*.sample`. Значит, конфиг pre-commit с полным pytest **сейчас не исполняется**; Г33 оценил его как «25 мин на каждый коммит» — фактически 0 мин и 0 защиты. Внутри конфига ещё и дубль (`pytest -v` и `coverage run -m pytest` — два полных прогона), `mypy` 1.3.0 и `flake8 --max-line-length=100` против стандарта 88. Файл вводит в заблуждение читающего и выстрелит у того, кто выполнит `pre-commit install` в среде без `hooksPath`.
7. **Проза в гейте.** `preflight` печатает `MANUAL_QUESTIONS` — три вопроса, которые «машина не проверит». Собственный `recurrence_ledger.md` §0: «разбор, который надо вспомнить и открыть, не является мерой». Вопросы на экране — та же проза.
8. **flake8 отключает `F401` (неиспользуемый импорт)** в `.flake8` — один из немногих машинных детекторов «чеховских ружей» выключен глобально.
9. **Выбор тестов в Stop-хуке уже, чем граф зависимостей**: `_affected_tests.py` ищет **прямое** вхождение имени модуля в тестах («Не претендует на полный dependency-граф»). Правка `app/core/x.py`, проверяемая только через тесты `app/services/y.py`, срез не попадает. Подстраховка — полный прогон в CI (как у Facebook), значит это ускоритель, а не гейт; называть его «гейтом» неверно.
10. **Еженедельный мутационный прогон, вероятно, ничего не делает** (гипотеза, проверяется одной строкой лога CI в Р1): в `ci.yml` `pip install -q mutmut` без пина версии и `mutmut run --paths-to-mutate app/core || true`. В mutmut 3.x (пилот шёл на 3.7.0) ключ конфигурации переименован — документация (context7 `/boxed/mutmut`): «The config paths_to_mutate is deprecated. Please rename it to source_paths», а `run` принимает имена мутантов («`mutmut run "my_module*"`»). Если CLI-флаг не распознаётся, ошибку глотает `|| true`, и джоба зелёная без единой мутации. Тот же класс, что INC-A11Y-DEADTEST («зелёный за счёт skip»).
11. **Агенты-ревьюеры (`design-critic`, `a11y-auditor`, `api-contract-guard`) не меряются.** Индустрия: доля принятых замечаний ИИ-ревью 7–74 % в зависимости от инструмента. Без учёта «принято/отклонено» неизвестно, где мы в этом диапазоне.
12. **Существующие метаморфические тесты стоят на генераторе с дефектом Д-01** (`tests/test_metamorphic_relations.py` импортирует `tools.portrait_testing.generator`; Г39: «Генератор v2 даёт срок цели как `date`, ядро молча читает «12 месяцев»… 76,2 % сроков»). Часть отношений проверяет не ту модель — зелёный цвет у них ничего не доказывает про сроки целей.

### Вердикт по методике ревизии
**Не «не то делали», а «делали одну половину».** Мы хорошо умеем **заводить** проверки (эскалация по рецидивам, сценарный эксперт, мутация после починки) — это совпадает с практикой и местами опережает её для соло-проекта. Мы не умеем **снимать** проверки и **мерить** их: нет учёта выхода гейтов, нет правила выключения шумных, реестр классов считает ошибки процесса, а не продукта. Результат виден в числах: самый дорогой инцидент (41 день без тестов в CI) вызван гейтом документов, а все найденные дефекты ядра (9 шт.) найдены поведенческими методами, которых в блокирующем контуре нет.

---

## П2. 🔴 Таксономия видов проверки: что доказывает каждый (синтез по сырью выше)

**Аналогия.** Тест — это вопрос к программе плюс знание правильного ответа. Покрытие меряет, **сколько вопросов задано**; оракул — **откуда мы знаем ответ**. Программа может ответить на все вопросы, и ни один ответ не будет проверен. Главный водораздел всей области — не «юнит или интеграционный», а **какой у проверки оракул** (Barr et al. 2015: «modelling, specifications, contract-driven development and metamorphic testing… the final source… remains the human»).

| Вид проверки | Что доказывает, если зелёный | Оракул | Что НЕ ловит | Результативность (источник) |
|---|---|---|---|---|
| Покрытие строк / ветвей | строка/ветвь **исполнилась** | нет | любой неверный ответ | нет значимой связи с дефектами после релиза на уровне файла (Kochhar 2017); находка дефектов растёт «only once relatively high levels of coverage are attained» (Chekam 2017) |
| MC/DC | каждое условие в решении независимо влияет на исход | нет | неверный ответ; «обманывается» переписыванием (Gay 2016) | нашёл ошибки, невидимые функциональным тестам, ценой ~40 % времени тестирования (Dupuy & Leveson 2000); без оракула «has little meaning» (Heimdahl 2008) |
| Пример-тест (эталонное значение) | на **этом** входе ответ равен посчитанному человеком | эталонное значение | всё, чего нет в примерах | тесты в среднем находят ~50 % дефектов, 1,3–1,7 деф./ч (Wagner 2006, табл. 1–2); один юнит-тест убивает в ~50 раз меньше мутантов, чем один property-тест (Ravi & Coblenz 2025) |
| Свойство-инвариант (`hypothesis`) | свойство верно на **сотнях случайных** входов | частичный: свойство | ошибку, не нарушающую свойство | ×50 мутантов на тест; 76 % находок в первых 20 входах; самые сильные — «ожидается исключение», «входит в коллекцию», «тип» (×19) (Ravi & Coblenz 2025); эффект слабый по Cramér's V = 0,05 |
| Метаморфическое отношение | **два прогона** согласованы (×λ → доли те же) | отношение между прогонами | ошибку, одинаково искажающую оба прогона | «a small number of diverse metamorphic relations… had a similar fault-detection capability to a test oracle» (Liu et al. 2014); **у нас — 9 дефектов ядра за батч Г39** при покрытии ≥95 % |
| Дифференциальное | две реализации дают одно | вторая реализация | ошибку, общую для обеих | NoREC — 159 новых багов в PostgreSQL/SQLite/MariaDB/CockroachDB (Rigger & Su 2020); у нас: SQLite↔PG нашла дедлок фикстур и порядок NULL; ЛП-оракул Г39 измерил разрыв до оптимума |
| Характеризующий / golden | поведение **не изменилось** со вчера | исторический | ошибку, бывшую вчера | «does not imply correctness» (Wikipedia/Feathers); цель — рефакторинг без незаметных изменений |
| Эталонный файл с внешним ответом | разбор совпал с ответом из **внешнего** источника | внешний эталон | форматы вне корпуса | сильнее исторического; у нас корпус Г47 |
| Контракт по схеме | ответ **имеет форму** из OpenAPI | схема | неверные значения в верной форме | Schemathesis «wildly outperforms» 7 других инструментов на 16 сервисах (авторы инструмента, 2022) |
| Фаззинг | программа **не падает / не зависает** | неявный (падение) | тихо неверный ответ | зависит от цели; у нас — Г32 |
| Мутационный анализ | **тесты** замечают порчу кода | мера тестов, не кода | — | связь с реальными дефектами «independently of code coverage» (Just 2014), но слабая при контроле размера (Papadakis 2018); у нас 68,7 % на трёх модулях ядра |
| Статическая типизация (`mypy`) | классы ошибок типов невозможны | система типов | логику | 15 % дефектов Python-проектов предотвратимы mypy (Khan et al. 2022) |
| Линтеры / статанализ | шаблоны ошибок отсутствуют | правило | логику | 81 % известных дефектов, но **22 % тяжёлых**; ложных срабатываний 31–96 % (Wagner 2006) |
| Формальное доказательство (Z3) | свойство верно **для всех** входов модели | спецификация | расхождение модели и кода | у нас доказано: ПДН-гейт не отвергает ни одной альтернативы при доходе > 0 (Г39) |
| Ревью человеком | понятность, нормы, крайние случаи | человек | большинство функциональных дефектов | ~15 % замечаний — дефекты, ≥50 % — сопровождаемость (Czerwonka 2015); инспекции в среднем 34 % дефектов (Wagner); один 53 %, пара 76 % (Hatton 2008) |
| Сценарное чтение | заданный класс дефектов отсутствует | человек + сценарий | классы вне сценария | больше, чем свободное чтение и чек-лист (Porter et al. 1995) |
| Сквозной браузерный | путь пользователя проходит | ожидаемый экран | логику внутри | ловит разрывы UI↔API (у нас INC-CRUD-DELETE); крупные тесты флакуют в 14 % против 0,5 % мелких (Google 2017) |

🔴 **Главный вывод таксономии.** «Тест исполнения строк» (покрытие) и «проверка поведения» различаются **наличием оракула**. Покрытие — необходимое, но не достаточное: оно гарантирует, что вопрос задан, и ничего не говорит об ответе. Мутационный анализ — единственная массовая мера того, **есть ли у тестов оракул**. Наши 68,7 % означают: у трети порч ядра оракула нет.

### Проверка рабочей гипотезы раскладки (подтвердить / опровергнуть / уточнить)

| Слой | Гипотеза | Вердикт | Уточнение с числами |
|---|---|---|---|
| Ядро модели | инварианты `hypothesis` + метаморфические отношения | 🟢 **подтверждено** | + **дифференциальный оракул** (ЛП/MILP из Г39 — единственный способ измерить «насколько хуже оптимума»); + **характеризующий снимок** на фиксированных портретах перед починкой Д-02…Д-09 (Feathers); + свойства класса «невалидный вход → исключение» — самая результативная категория (×19, Ravi) и прямо закрывает Д-07 (NaN); + мутации как мера (69 выживших в `ranking`). 🔴 Существующие MR-тесты сначала отвязать от дефекта Д-01 генератора |
| Парсер выписок | эталонные файлы + фаззинг | 🟡 **уточнено** | эталон Г47 — **внешний** оракул, он и есть главный. Фаззинг даёт только неявный оракул (падение), поэтому к нему нужны **свойства денег**: сумма разобранных операций = обороты из шапки выписки; повторный импорт не меняет итог (идемпотентность, Г33); перестановка строк не меняет суммы. Фаззинг дешевле делать через `hypothesis` (`st.binary()`), он уже установлен (`tests/test_statement_property.py`, 13 тестов) |
| Слой данных | дифференциальный SQLite ↔ PostgreSQL | 🟡 **частично** | это дифференциал **диалектов под нашим кодом**, и он доказанно работал (дедлок PG, порядок NULL, FK не форсятся на SQLite). Но 12-factor требует паритета dev/prod (Г33); пока две СУБД поддерживаются — оставить; к нему нужны `alembic check` (дрейф), тест обратимости (есть), ограничения схемы как отражение домена (PIT-010) |
| HTTP-контур | контрактные тесты против OpenAPI | 🟡 **уточнено** | наш «контракт» = снимок ↔ живое приложение + генерация клиента + `tsc` — ловит **дрейф формы**. Не ловит 500 на неожиданных входах: это генеративный фаззинг по схеме (Schemathesis); прецедент — PIT-024 «контракт заводили ради типов, а нашли пятисотку у каждого нового пользователя». Ломающие изменения (oasdiff) — только для B2B `/v1` |
| Интерфейс | браузерные | 🟢 **подтверждено, с ограничением** | нужны для **путей пользователя** (CRUD, «новый пользователь с нуля» — CONSENT-GATE); но крупные тесты флакуют в 28 раз чаще мелких (14 % против 0,5 %, Google) → минимум сквозных, остальное — компонентные (Vitest) |
| 🔴 Пропущено в гипотезе: **объяснение совета** | — | 🔴 **добавить** | «решающий критерий неверен в 67,9 % советов» (Д-09). Оракул — тот же код выбора; тест верности: «названная причина при её удалении меняет победителя» |
| 🔴 Пропущено: **время и окружение** | — | 🔴 **добавить** | BUG-026 (TZ), BUG-028 (календарная мина), INV-MACHINE-LOAD — метаморфические отношения по окружению: «смена TZ / сдвиг часов на +370 дней не меняет результат» (машина времени `tools/timewarp` уже есть — поднять в регулярный прогон) |

### Метаморфические отношения, которые формулируют для финансов и рекомендаций

Из литературы (формы отношений, не числа):
- **Масштабирование шкалы** — «rating multiplication», «rating shifting» (Mao et al. 2020 для LibRec; Khirbat et al. 2024), совпадение списков меряют «Kendall and Ranking Biased Overlap (RBO)».
- **Похожие входы → похожие выходы** — налоговое ПО (ICSE-SEIS 2023): нашли «unreliable behavior when tax returns are close to zero».
- **Монотонность по бизнес-ожиданию** — кредитный скоринг (Ying et al. 2025): «all three models often violate MRs… Traditional metrics fail to capture these violations».
- **Банковские функции** — Rahman & Izurieta 2023 (перечень отношений в аннотации не раскрыт).
- **Регрессия** — 11 отношений для линейной регрессии (Monash).
- **Перестановка / аддитивность / умножение** для матричных расчётов (Rahman & Kanewala 2018).

Для FINPILOT (сведено с Г18 MR-1…MR-8 и Г39 MR01…MR16; новые помечены ★):
| Отношение | Преобразование входа | Ожидание | Статус |
|---|---|---|---|
| однородность | все суммы × λ | доли плана не меняются | Г39 MR03/MR09 — **нарушено** (Д-03, Д-04) |
| ★ смена единиц | рубли → копейки (×100) | план тот же с точностью до округления | частный случай предыдущего; ловит float/Decimal (Г20) |
| монотонность по доходу | доход ↑ | покрытие целей не убывает | Г39 — держится |
| монотонность по ставке | ставка долга ↑ | доля в этот долг не убывает | Г18 MR-2; Г39 слепота 87,9 % |
| перестановка | перенумеровать одинаковые долги / цели | план переставляется | держится |
| доминируемая альтернатива | добавить заведомо худший вариант | победитель не меняется (rank reversal) | Г39 RRT1 — **нарушено** в 13 из 28 |
| сужение ограничений | ужесточить порог ПДН | допустимых вариантов не больше | Г18; Г39: гейт не срабатывает вовсе |
| сдвиг горизонта | перезапуск с промежуточного месяца | хвост прогноза совпадает | Г18 |
| ★ порядок строк выписки | переставить операции | итоги по категориям те же | новое, для парсера |
| ★ дробление операции | одна покупка → две на ту же сумму | итоги по категориям те же | новое, для категоризации |
| ★ часовой пояс / часы | TZ=MSK вместо UTC; сдвиг на +370 дн. | результат тот же / тот же относительно новой даты | BUG-026, BUG-028 |
| ★ похожие входы | доход ±1 ₽ | план меняется не скачком (кроме объяснимых порогов) | по образцу налогового ПО; ловит «пилу» Г39 п. 10 |

---

## П3. Что даёт больше найденных дефектов на час работы

**Честно о силе данных.** Прямого сравнения «property vs метаморфическое vs фаззинг на одном коде в дефектах на час» в найденной литературе **нет**. Есть: сводка Wagner 2006 (данные в основном 1980–2000-х), отдельные замеры по каждому методу и наш собственный батч Г39.

| Метод | Дефектов на час / доля | Источник |
|---|---|---|
| Функциональные тесты | 1,72 деф./ч (среднее), находят 53 % | Wagner табл. 1–2 |
| Структурные тесты | 1,5 деф./ч, 55 % | Wagner |
| Инспекции | 1,87 деф./ч (медиана 1,18), находят 34 % (разброс 8,5–92,7) | Wagner табл. 7–8 |
| Статанализ | дёшев в запуске, но тяжёлых дефектов 22 %; разбор ложных — «essentially constitutes a review» | Wagner |
| Проверка при сборке против после коммита | 74 % против 21 % «реальных проблем» | Google CACM 2018 |
| Property-тест против юнит-теста | ×50 мутантов на тест | Ravi & Coblenz 2025 |
| Метаморфические отношения | несколько разнородных MR ≈ полноценный оракул; строятся «even by inexperienced testers… with a very small amount of training» | Liu et al. 2014 |
| Дефект из эксплуатации | стоит 27,6 ч (медиана) против 2–3,5 ч на этапе кода и тестов | Wagner табл. 11–12 |
| **Наш замер (Г39)** | 9 дефектов ядра + 4 подтверждения за один батч (27 скриптов стенда) при уже зелёных тестах и покрытии ≥95 % | `math_core_verification_plan_2026-09-17.md` |
| **Наш замер (эксперт)** | 58 гипотез / 9 проходов, 11 уровня SEV | `independent_expert_cycle_log.md` |

**Ответ.** По совокупности: (1) **поведенческие проверки с оракулом без эталона** (свойства и метаморфические отношения) — наибольший выход на час для кода без «правильного ответа», и у нас это подтверждено собственным числом; (2) **сценарное чтение со свежим контекстом** — наибольший выход для дефектов **замысла** (фича без экрана, разрыв канона и кода), которые тесты не видят в принципе; (3) **перенос проверки как можно раньше** (тип, сборка, pre-commit) — дешевле всего на дефект, но ловит только простые классы. Линтеры и ревью «глазами» — наименьший выход по тяжёлым дефектам.

---

## П1. Сетки безопасности при изменении — что есть и чего нет

| Сетка | У нас | Вывод |
|---|---|---|
| Характеризующие тесты перед правкой страшного кода | нет как практики | 🔴 нужны перед починкой Д-02…Д-09 (ядро будут менять в нескольких местах сразу) — снимок плана на ~300 фиксированных портретах |
| Контракт фронт↔бэк | снимок + генерация + `tsc` + `api-contract-guard` | достаточно для одного своего фронта; Pact не нужен (Г33) |
| Машинное обнаружение ломающих изменений API | дрейф снимка — есть; классификация «ломающее» — нет | oasdiff — когда у B2B `/v1` появится внешний клиент (1 ч) |
| Архитектурные фитнес-функции | нет | import-linter, цена в Г33 |

## П4. Спящие дефекты и «чеховские ружья» — что нашлось в этом батче

| Ружьё | Где | Чем ловится машинно |
|---|---|---|
| конфиг pre-commit, который не исполняется (и с двойным pytest внутри) | `.pre-commit-config.yaml` при `core.hooksPath=_base/.githooks` | сверка «конфиг инструмента ↔ реально установленный хук» (одна проверка в preflight) |
| `|| true` в CI, возможно глотающий мёртвую мутационную джобу | `ci.yml` deep | запрет `|| true` в CI без комментария-обоснования — тот же приём, что PIT-001 |
| гейт в продукте, доказанно не срабатывающий | ПДН-гейт `filtering.filter_alternatives` (Г39, Z3) | формальное доказательство / глобальная чувствительность ($S_T$ = 0) |
| константа, почти не влияющая на результат | прибавка floor ADR-015 ($S_T$ = 0, Г39) | индексы Соболя как детектор «мёртвых» параметров |
| выключенный детектор неиспользуемых импортов | `.flake8` `extend-ignore = … F401` | включить F401 (или ruff) |
| тест, зелёный за счёт `skip` | прецедент INC-A11Y-DEADTEST | число пропусков как сигнал (`pytest -rs`, порог) |
| документ о гейте, расходящийся с гейтом | `recurrence_ledger.md` §3 про flake8 в preflight | `revision_check`-проверка «названная в документе команда существует в коде» |
| мёртвый код | не мерено | `vulture` / `knip` — Р1 п. 11 Г33 |

## П5. CI/CD-дисциплина — сверх Г33

- **Выбор тестов по изменению.** Индустриальная база — транзитивный граф зависимостей, сокращение поверх него обязательно подстраховано полным прогоном (Facebook: «over 95% of individual test failures and over 99.9% of faulty changes», «fewer than a third of the tests»). Наш `_affected_tests.py` — прямые вхождения; это ускоритель Stop-хука, а не гейт; подстраховка (полный прогон в CI) есть — **приемлемо**. Улучшение (транзитивный граф импорта или `pytest-testmon` по фактическому покрытию) — малый эффект, 2–4 ч.
- **Флаки.** Google: 1,5 % прогонов, 16 % тестов, **84 % переходов «зелёный → красный» — флаки**; «It is human nature to ignore alarms when there is a history of false signals». У нас класс INV-MACHINE-LOAD — 11 эпизодов (перегрузка хоста), то есть флакующие по таймауту тесты есть. Норма: учитывать перезапуски, карантин только с заведённой задачей («could easily mask a real race condition»).
- **Быстрый отказ.** Сейчас джобы CI параллельны (без `needs:`), это лучше прошлой цепочки, из-за которой 41 день не шли тесты. Правило, которого нет: **гейт документов не имеет права заслонять поведенческие тесты**.

## П6–П7. Схема данных и наблюдаемость
Разобраны в Г33 (expand/contract, `alembic check`, откат, 4 золотых сигнала, аптайм, SLI) — здесь не повторяю. Единственное добавление Г34: канареечная выкладка и авто-откат на одном VPS — избыточны; достаточный минимум — смоук после выкладки + сравнение доли 5xx до/после + откат одной командой (Г33, 2–4 ч).

## П8. Процесс на одного — что заменяет второго ревьюера
1. **Свежий контекст = второй человек.** Hatton: один инспектор находит 53 %, пара — 76 %. Наш `independent-expert` (агент без контекста сессии) — функциональный аналог второго, и у него лучшие измеренные числа в проекте. Оставить, **сделать регулярным по изменённому коду**, а не только «на веху».
2. **Сценарий вместо чек-листа.** Чек-лист не лучше свободного чтения (Porter 1995; Hatton 2008 — 308 инспекций, «no evidence that checklists significantly improved»). Наши агенты-ревьюеры уже устроены как сценарии («ищи класс X») — это правильно; неправильно, что их выход не меряется.
3. **ИИ-ревью — считать принятые замечания.** Доля принятых у промышленных инструментов 7–74 %; ниже порога полезности (Google: не больше 10 % «не полезно» для предупреждения) — отключать или сужать сценарий.
4. **Разбор инцидентов.** SRE: критерии разбора заданы **до** инцидента; цель — «effective preventive actions». У нас INC-разборы есть; не хватает поля «каким методом найден / что поймало бы раньше», без которого нельзя решить, какие гейты работают.
5. **«Остыть и перечитать»** — в найденной литературе чисел нет; не утверждаю.

## П10. Масштабирование кодовой базы
Отдельно в этом батче не добывалось сверх Г33 (B2 «модульный монолит», Shopify, import-linter). Признаки «пора делить» и стоимость раздела — осталось неизвестным (см. ниже).

---

## ИТОГ Г34

### Прямой ответ владельцу
**Мер предосторожности у нас много, но они стоят не там, где ловят.** Блокирующий контур (preflight, `revision_check`, покрытие ≥90/95 %) проверяет документы, церемонию и **исполнение** строк; ни один продуктовый дефект в реестре инцидентов им не найден, а самый дорогой инцидент проекта (41 день без тестов в CI) вызвал именно гейт документов. Все 9 дефектов ядра, найденные 16–17.09.2026, выловлены **поведенческими** методами с оракулом (метаморфические отношения, инварианты, Z3, стенды), которых в блокирующем контуре нет. «Не то делали» — неверно; верно «делали половину»: хорошо заводим проверки, но не меряем и не снимаем их.

**Процесс (прозрачно).** Классификация — depth-first для п. 2 и п. 9 (много ракурсов на один вопрос «что ловит дефекты»), breadth-first для остальных пунктов. Подагентов — **0** (ограничение батча; вход Г33/Г39 уже был в контексте). Внешние вызовы: `WebSearch` — 0, `WebFetch` — 0, браузер — 0 (не понадобился); Exa `web_search_exa` — 10, Exa `web_fetch_exa` — 1 (3 URL); context7 — 2 resolve + 2 query; OpenAlex — 3 пакета, 31 запрос (ошибки: 1×400, 2×429); `r.jina.ai` — 4 (CACM 200/58 172 байта, SRE 200, vulture — без нужных строк, проба); `curl` — arXiv PDF 200/318 707 байт → `pdftotext`, PDF Nottingham — 404. Второго круга не было: противоречие «чек-лист находит больше» (постановка) против Porter 1995 и Hatton 2008 разрешено на месте в пользу двух первоисточников.

### 🔴 Таблица: механизм → что ловит → есть ли у нас → цена → эффект
Отсортировано по отношению эффекта к цене (сначала — большой эффект за малую цену). Цена — часы соло-разработчика с ассистентом, 0 ₽.

| # | Механизм | Что ловит | Есть у нас | Цена | Эффект по исследованиям |
|---|---|---|---|---|---|
| 1 | 🔴 **Сделать мутационный контур настоящим**: проверить, что `deep` реально мутирует (флаг `--paths-to-mutate` против mutmut 3.x, пин версии, убрать `|| true`), выгружать **выживших** мутантов изменённого кода ядра как задачи; храповик ≥68,7 % | тесты без оракула («строка исполнена, ответ не проверен») | пилот есть; еженедельная джоба, вероятно, пустая | 1–3 ч | связь с реальными дефектами «independently of code coverage» (Just 2014); Google — ценность в выживших на изменённом коде, 15 %→89 % продуктивных после фильтра |
| 2 | 🔴 **Учёт выхода гейтов + правило выключения**: у каждого гейта счётчик «сработал / реальный дефект / ложный»; гейт с >10 % ложных — выключается до починки; отменить запрет «понижать уровень нельзя»; блокирующим может быть только гейт без ложных остановок | налог гейтов, ложную уверенность, гейты-декорации | нет (4 ложняка оформлены как PIT, не как метрика) | 2–3 ч | Google Tricorder: «above 10%… disables the analyzer»; блокирующая проверка — «no effective false positives» |
| 3 | 🔴 **Поведенческие проверки ядра в блокирующий `core`**: починить Д-01 в генераторе, поднять держащиеся MR (01, 08, 10, 11, 12, 16) и 13 инвариантов Г39 с порогом 0 нарушений; MR с известными дефектами — храповиком | тихо неверный совет | частично: `test_metamorphic_relations.py` (15), `test_core_properties.py` (24 `@given`), но на генераторе с Д-01 и не все MR | 5–7 ч | Liu 2014 (MR ≈ оракул); Ravi 2025 (×50 на тест); **наши 9 дефектов при покрытии ≥95 %** |
| 4 | Свойства «невалидный вход → исключение» для `run_planning` | NaN/∞/минус → молчаливый план (Д-07) | нет | 2–3 ч | самая результативная категория property-тестов, ×19 (Ravi 2025) |
| 5 | Поле «каким методом найден / что поймало бы раньше» в карточке дефекта и в `incidents_summary` (ODC-триггер) | незнание, какие гейты работают | нет | 1 ч + 5 мин на дефект | ODC — «six error types accounted for nearly 80%» тяжёлых (через Wagner); без этого п. 2 не на чем считать |
| 6 | Удалить или привести в соответствие `.pre-commit-config.yaml` | «ружьё»: двойной полный pytest, mypy 1.3.0, длина строки 100 при стандарте 88 | конфиг есть, **не исполняется** (`hooksPath=_base/.githooks`) | 0,5 ч | убирает ложное представление (поправка к Г33) |
| 7 | Правило «гейт документов не заслоняет тесты» + убрать прозу `MANUAL_QUESTIONS` из preflight (или превратить в проверки) | повтор CI-RED-41-DAYS | джобы уже параллельны, правила нет | 1 ч | Google: блокирующее — только без ложных; свой `recurrence_ledger` §0 — «проза не мера» |
| 8 | Характеризующий снимок ядра на ~300 фиксированных портретах **перед** починкой Д-02…Д-09 | незамеченные побочные изменения при правке ядра | нет | 2–3 ч | Feathers: «correct behavior is defined by what the set of classes did yesterday» — видно, что поменялось ВСЁ нужное и НИЧЕГО лишнего |
| 9 | Включить F401 (неиспользуемые импорты) | мёртвые импорты, «ружья» | выключен в `.flake8` | 0,5–1 ч + чистка | Google держит «unused variable analysis» среди базовых bug-finding проверок (CACM 2018) |
| 10 | Золотые файлы парсера на корпусе Г47 + свойства денег (сумма = обороты, повторный импорт не меняет итог, перестановка строк) + фаззинг `hypothesis` `st.binary()` | неверный разбор, падения, двойной импорт | частично (`test_statement_property.py`, 13 тестов) | 4–6 ч | внешний эталон сильнее исторического; фаззинг без свойств — только падения |
| 11 | Метаморфические отношения окружения (TZ, машина времени +370 дн.) в регулярный прогон | BUG-026/BUG-028-класс | `tools/timewarp` есть, «раз в веху» | 1–2 ч | прецеденты в проекте (2 дефекта) |
| 12 | Тест верности объяснения (Д-09) | «названная причина ≠ настоящая» | нет | 3–6 ч (Г39) | 67,9 % советов с неверной причиной |
| 13 | Генеративный фаззинг API по схеме (Schemathesis) в `full` | 500 на неожиданных входах, несоответствие схеме | нет | 2–4 ч | «wildly outperforms» 7 инструментов (авторы, 2022); прецедент PIT-024 |
| 14 | Сквозной тест «новый пользователь с нуля» | тупики замысла (CONSENT-GATE) | нет (action item инцидента) | 3–4 ч | SEV1 near miss у нас |
| 15 | Учёт принятых/отклонённых замечаний агентов-ревьюеров | шумные ревьюеры | нет | 1 ч | ИИ-ревью: принято 7–74 % по инструментам |
| 16 | `independent-expert` регулярно по изменённому коду, не только «на веху» | дефекты замысла | есть | 0 ч (порядок) | 58 гипотез / 11 SEV / «ни один проход не вернул пусто»; Hatton: пара 76 % против 53 % |
| 17 | Учёт флаков: перезапуски, карантин только с задачей | ложная тревога и привычка игнорировать красное | нет (INV-MACHINE-LOAD, 11 эпизодов) | 2–3 ч | Google: 84 % переходов в красное — флаки |
| 18 | import-linter (слои) | нарушение архитектуры | нет | 1–2 ч + правки | Г33 |
| 19 | oasdiff для B2B `/v1` | ломающие изменения для внешних клиентов | нет | 1 ч | сотни проверок, `--fail-on ERR`; нужен при первом внешнем клиенте |
| 20 | Транзитивный выбор тестов (граф импорта / `pytest-testmon`) | тест, не попавший в срез Stop-хука | прямые вхождения | 2–4 ч | Facebook — граф зависимостей как база; у нас подстраховка полным прогоном уже есть → эффект малый |
| 21 | MC/DC | составные условия | нет | высокая (нет инструмента в `coverage.py`) | ~40 % времени тестирования (Dupuy 2000), «обманывается» (Gay 2016); мутации `and`↔`or` дают близкое дешевле → **не внедрять** |

🔴 **Три механизма, которые стоит внедрить первыми:** (1) **мутационный контур, который реально работает** — выжившие мутанты изменённого кода как задачи (п. 1, 1–3 ч); (2) **учёт выхода гейтов и правило выключения шумных** (п. 2, 2–3 ч) — это прямой ответ на «мб мы не то делали»; (3) **поведенческие проверки ядра в блокирующем контуре** после починки Д-01 (п. 3, 5–7 ч) — единственный механизм, который уже доказал себя на нашем коде девятью дефектами.

### Что из текущего набора избыточно (налог, а не защита)
1. 🔴 **`.pre-commit-config.yaml`** — не исполняется; при установке дал бы два полных pytest на коммит. Удалить или свести к быстрым проверкам.
2. 🔴 **Правило «понижать уровень нельзя»** в `recurrence_ledger.md` — гарантирует, что гейты только копятся. Заменить на «снимается при >10 % ложных или при нуле срабатываний за две вехи — с записью».
3. **preflight как «защита от поломок»** — как проверка церемонии версии он нужен, но из 7 его проверок ни одна не смотрит на поведение продукта, а его ложное красное однажды остановило все тесты на 41 день. Оставить церемонией, не считать сеткой безопасности. `MANUAL_QUESTIONS` — проза, по нашему же реестру не работает.
4. **`pylint` с `continue-on-error`** — гейт, который никогда не блокирует (Г33: три линтера одного класса).
5. **Неблокирующий flake8 на каждую запись (`lint-python.sh`)** — пограничный: дублирует блокирующий `lint` в CI; дёшев, но полезность не замерена. Решать по счётчику из п. 2.
6. **ПДН-гейт в `filtering`** (код продукта) — доказанно не отвергает ни одной альтернативы (Г39, Z3): гейт-декорация, решение — в ROADMAP ядра.
7. **Еженедельная мутационная джоба в текущем виде** — если гипотеза п. 10 раздела «П9-наш» подтвердится, это зелёная пустышка.
8. Честная оговорка: про остальные хуки (`block-secrets`, `block-destructive`, `check-design-tokens`, гейты каналов) **данных о выходе нет** — объявлять их налогом без счётчика нельзя; для `block-relative-read-path.py` зафиксировано ложное срабатывание в этом батче (абсолютный путь после `=`).

### Осталось неизвестным
- Прямого сравнения «property / метаморфическое / фаззинг / ревью в дефектах на час на одном коде» в найденной литературе нет; числа Wagner 2006 — в основном данные 1980–2000-х.
- Liu et al. 2014 — полный текст не добыт (Nottingham ePrints 404 по прямому пути); используется только аннотация, без процентов.
- Kim et al. ISSTA 2022 — рейтинг инструментов из тела статьи не снят; превосходство Schemathesis подтверждено только его авторами.
- Рейтинги перечня MR Rahman & Izurieta 2023 и Mao 2020 — в аннотациях перечней нет, тела не открывались (IEEE, закрыто).
- ODC (Chillarege 1992), DO-178C, Fagan 1976 и 1986 — первоисточники закрыты; Fagan цитируется по аннотации, без процентов обнаружения.
- `vulture` — дословных цитат о точности не добыто.
- Признаки «пора делить модульный монолит» и стоимость раздела (п. 10) — не исследовались сверх Г33.
- Реальный выход наших гейтов (сколько раз сработал каждый и сколько из этого — дефекты) — **данных нет в репозитории**; это не пробел поиска, а пробел учёта (механизм п. 2 таблицы).
- Работает ли еженедельная мутационная джоба — гипотеза, проверяется логом CI в Р1.
- «Остыть и перечитать» — чисел в литературе не найдено.

### Что передаётся в ROADMAP (не делалось в батче — решение владельца)
Этап Р1/внедрения: пункты 1–3 таблицы первыми; затем 4–12 как «до запуска»; 13–20 — «после запуска / по мере появления B2B»; 21 — не делать.
