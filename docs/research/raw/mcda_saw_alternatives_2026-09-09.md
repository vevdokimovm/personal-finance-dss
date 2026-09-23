# Тема 15 — слабости метода SAW и альтернативы (TOPSIS, PROMETHEE, MAUT)

Дата: 2026-09-09. Сырьё исследования, дословные цитаты источников.
Разметка: 🟢 прочитано в полном тексте · 🟡 источник второго уровня (сниппет/реферат) ·
🔴 мой вывод, а не прочитанное.

---

## ПРОВЕРКА BASH

🔴 **Bash НЕДОСТУПЕН.** Первым действием сессии выполнена предписанная команда
`which curl && curl -sS -o /dev/null -w "%{http_code}" -A "Mozilla/5.0" https://www.ssrn.com/index.cfm/en/`.
Ответ харнесса дословно:

```
Error: No such tool available: Bash. Bash is disabled for this session, in subagents as well as here.
```

Добавление `Bash` в определение агента **фактом не подтвердилось**. Важное уточнение по
диагностике: это отказ на уровне **списка доступных инструментов**, а не permissions.
Правила `allow` в `settings.json` регулируют, что можно делать уже выданным инструментом,
и не добавляют инструмент в набор. Смотреть надо `tools:` во frontmatter определения агента
и флаги запуска сессии (`--disallowedTools`), а не список разрешений.

Последствие для результата, честно: обход 403 через `curl` с браузерным User-Agent
в этой сессии невозможен, и это **реально стоило источников** — ScienceDirect, Springer,
MDPI, Wiley, ResearchGate закрылись наглухо (см. «СОСТОЯНИЕ КАНАЛОВ»). В частности,
не открыт первоисточник теоремы RAFSI и не открыт O'Shea et al. (2025).

### 🟢 Найден рабочий обход для PDF, не требующий Bash

`WebFetch` на PDF отвечает «не могу разобрать бинарный файл» — **и в том же ответе печатает
путь, куда он этот PDF сохранил**:

```
[Binary content (application/pdf, 469.9KB) also saved to
 /Users/vasyaevdokimov/.claude/projects/.../tool-results/webfetch-1788963069845-pr87iu.pdf]
```

Дальше файл читается штатным `Read` с параметром `pages` — страницы приходят изображениями
и читаются полностью. Так добиты **три** источника, которые иначе были бы записаны
непрочитанными: Bisht & Pal (2024), Jiménez-Martín et al. (2015), Wang & Rangaiah (2025).
Приём работает без Bash и без `pdftotext`. **Это следует занести в постоянные правила
исследований** — «PDF нечитаем» и здесь оказалось неправдой.

---

## СОСТОЯНИЕ КАНАЛОВ

| Источник | URL | Результат | Чем добито |
|---|---|---|---|
| Informatica VU (Shyur & Shih 2024) | https://www.informatica.vu.lt/journal/INFORMATICA/article/1356/text | 200, полный текст | WebFetch |
| Informatica SI (Bisht & Pal 2024) | https://www.informatica.si/index.php/informatica/article/download/4144/2743 | PDF, WebFetch не разобрал | 🟢 `Read pages 1-4` по сохранённому файлу |
| SciTePress (Jiménez-Martín et al. 2015) | https://www.scitepress.org/Papers/2015/51801/51801.pdf | PDF, WebFetch не разобрал | 🟢 `Read pages 1-3` по сохранённому файлу |
| arXiv (Wang & Rangaiah 2025, гл. 8) | https://arxiv.org/pdf/2509.06388 | PDF, WebFetch не разобрал | 🟢 `Read pages 1-6` по сохранённому файлу |
| ZERO Jurnal (Murti et al. 2025) | https://jurnal.uinsu.ac.id/index.php/zero/article/view/25707/0 | 200, полный текст | WebFetch |
| UK Gov Analysis Function, MCDA guide | https://analysisfunction.civilservice.gov.uk/policy-store/an-introductory-guide-to-mcda/ | 200, полный текст | WebFetch |
| UCC repository (O'Shea et al. 2026) | https://research.ucc.ie/en/publications/weight-stability-intervals-for-multi-criteria-decision-analysis-u/ | 200, реферат | WebFetch |
| ScienceDirect (Vafaei 2022, Procedia CS) | https://www.sciencedirect.com/science/article/pii/S1877050922001570 | **403** | не открыто |
| ScienceDirect, прямой PDF того же | .../S1877050922001570/pdf?md5=… | **403** | не открыто |
| Springer (Vafaei, норм. для weighted average) | https://link.springer.com/chapter/10.1007/978-3-319-78574-5_4 | **303 → idp.springer.com (авторизация)** | не открыто |
| Springer (сравнение TOPSIS и SAW, AOR 2023) | https://link.springer.com/article/10.1007/s10479-023-05339-w | **303 → авторизация** | не открыто |
| MDPI (RAFSI, Žižović et al. 2020) | https://www.mdpi.com/2227-7390/8/6/1015 | **403** | 🟡 добит косвенно — метод изложен целиком в Bisht & Pal 2024 |
| Wiley (Li 2026, trend analysis rank reversal) | https://onlinelibrary.wiley.com/doi/10.1002/mcda.70027 | **403** | не открыто |
| O'Shea et al. 2025, полный PDF | https://peterdeeney.com/wp-content/uploads/2025/07/OShea-et-al-2025-MCDA-L1.pdf | **403** (вопреки ожиданию задания) | 🟡 добит рефератом через UCC |
| Semantic Scholar (страница RAFSI) | https://www.semanticscholar.org/paper/…9cb06371… | пустое тело ответа | не открыто |
| metrology-journal (RAFSI vs PIV) | https://www.metrology-journal.org/…/ijmqe220020.html | **403** | не открыто |
| aegean.gr, step6 выбор метода MCDA | http://www1.aegean.gr/environment/energy/mcda/step6.html | **certificate has expired** | не открыто |

**Процесс.** Классификация запроса: **depth-first** — один предмет (аддитивная свёртка
в нашей задаче), рассматриваемый с шести ракурсов. Субагентов запущено: **0**.
Обоснование: правило §11 `CLAUDE.md` FINPILOT («по одному агенту за раз, экономия лимита»),
а главное — все шесть вопросов упёрлись в одно и то же узкое множество доступных
первоисточников, и делить его между агентами значило бы платить контекстом за дублирование.
WebSearch-вызовов сделано **9**, WebFetch — **13**, `Read` по сохранённым PDF — **3**.

---

## 1. Нормализация как ПРИЧИНА rank reversal (вопросы 1 и 2)

🟢 **Bisht, G., & Pal, A. K. (2024). A Novel Fuzzy Modified RAFSI Method and its Applications in
Multi-Criteria Decision-Making Problems. *Informatica* (Slovenia), 48(1), 21–30.**
https://doi.org/10.31449/inf.v48i1.4144 — прочитаны стр. 21–24.

Центральная цитата, дословно (стр. 21, Introduction):

> «The key explanation for rank reversal is the use of normalization, which changes with the
> addition or deletion of alternatives. This distorts the initial data and violates the
> 'Principle of Independence from Irrelevant Alternatives' (PIIA). This is often true for any
> normalization [2]. Since differences in dimensional units of attributes can only be eliminated
> by normalization in most of the MADM approaches it becomes a vital part.»

> «Rank reversal is the most significant problem that can't be ignored in multi-criteria
> decision-making (MCDM) methods.»

> «MCDM methods are also prone to rank reversal when a problem is decomposed into multiple
> smaller problems keeping the standard weight and alternative scores unaltered.»

История вопроса, дословно оттуда же:

> «During the utilization of the Analytic Hierarchy Process (AHP), the matter of rank reversal
> was initially observed by Belton and Gear [3]. The identical was also noticed by Triantaphyllou
> and Mann [4] in AHP during the substitution of the worst alternative with an anti-ideal
> alternative. Saaty and Varga [5] presented that the matter of rank reversal can happen because
> of the occurrence of almost identical copies within the set of alternatives. They also opined
> that the addition of a new alternative can practically modify the previous preference order.»

> «Fedrizzi et al., [6] presented that the possibility of rank reversal rests on the distribution
> of criteria weights i.e., the entropy of the weight distribution. They established that the
> projected possibility of rank reversal rises with the weight's entropy.»

> «Further many authors noticed this problem in several MCDM methods because of the mutual
> correlations between the relevant and irrelevant alternatives, as a consequence of
> normalization [7].»

**Полный перечень операций, порождающих rank reversal** (сводно по этому тексту): добавление
новой альтернативы; удаление существующей; появление **почти точной копии** (Saaty & Varga);
замена худшей альтернативы на анти-идеальную (Triantaphyllou & Mann); декомпозиция задачи
на подзадачи при неизменных весах и оценках.

🟢 **Wang, Z., & Rangaiah, G. P. (2025). Multi-Criteria Decision-Making: Aggregation-Type Methods
(Chapter 8, preliminary draft).** arXiv:2509.06388 — прочитаны стр. 8-1…8-6.
Ограничения SAW сформулированы прямым текстом (стр. 8-5):

> «The limitations of SAW are as follows. (1) Similar to other MCDM methods, rank reversal can
> occur if new alternatives are added or existing ones are removed, potentially affecting the
> stability of the ranking results (2) It treats all performance values additively; high
> performance on one criterion is possible to completely compensate for low performance on
> another, which might be undesirable in certain decision-making scenarios.»

🟡 Из поисковой выдачи (полный текст не открыт):

> «Interestingly, Barzilai and Golany have proved that no normalization can prevent rank
> reversal.»

🔴 **Противоречие между источниками, называю прямо, не сглаживаю.** Barzilai & Golany —
«никакая нормализация не предотвращает rank reversal»; Žižović et al. (RAFSI, 2020) заявляют,
что их математическая формулировка rank reversal **устраняет**, и Bisht & Pal это
подтверждают независимо. Моё разрешение: результат Barzilai–Golany относится к нормализациям,
вычисляемым **по самой матрице решений** — все такие зависят от состава множества. RAFSI
выносит опорные точки **наружу**: их задаёт ЛПР, а не выборка. Это не опровержение теоремы,
а выход из области её условий. 🟡 Полный текст Barzilai & Golany не открыт, разрешение
противоречия — **мой вывод**.

🟡 Формулировка теоремы о сохранении ранга (из сниппета, доказательство не прочитано):

> «The rank of alternatives from a set remains the same in the case that the starting set of
> alternatives is expanded by a new alternative. This is achieved through a normalization process
> that depends only on the treated alternative and a hypothetical ideal/nadir solution given by
> the decision maker.»

Первоисточник: Žižović, Pamučar, Albijanić, Chatterjee, Pribićević (2020), *Mathematics*
8(6), 1015, https://doi.org/10.3390/math8061015 — **403, не открыто**.

---

## 2. RAFSI: наша нормативная нормализация уже описана в литературе (вопрос 1)

🟢 Алгоритм RAFSI дословно (Bisht & Pal 2024, стр. 23, раздел 2):

> «1) The DM describes ideal (a_Ij) and anti-ideal (a_Nj) values for individual criteria.»

> «2) Mapping of elements of the decision matrix into criteria intervals.
> C_j ∈ [a_Nj, a_Ij], where C_j belongs to max type criteria.
> C_j ∈ [a_Ij, a_Nj], where C_j belongs to min type criteria.»

Отображение подынтервалов критерия в общий интервал [n₁, n_2k]:

> «f_s(x) = (n₁ − n_2k)/(a_Ij − a_Nj) · x + (a_Ij·n₁ − a_Nj·n_2k)/(a_Ij − a_Nj)»

> «It is supposed that the optimal value is six times improved than the non-optimal value i.e.,
> n₁ = 1 and n_2k = 6. In this way, a standardized decision matrix is obtained.»

Нормализация через среднее арифметическое A и гармоническое H границ:

> «for max type criteria ŝ_ij = s_ij / 2A;  for min type criteria ŝ_ij = H / 2s_ij»

И сама свёртка:

> «5) Calculate criteria functions of alternatives V(A_i).
> V(A_i) = ω₁ŝ_i1 + ω₂ŝ_i2 + ….. + ω_n ŝ_in»
> «Finally, alternatives are ranked in descending order of V(A_i).»

🔴 **Главный вывод отчёта для FINPILOT.** RAFSI по агрегации — **это аддитивная взвешенная
свёртка, то есть SAW**. Отличается ровно одним: нормализация ведётся не по min/max выборки,
а по **заданным извне ЛПР идеалу и анти-идеалу каждого критерия**. То, что в литературе
2020–2024 подаётся как «новый метод MADM, устраняющий rank reversal», по конструкции совпадает
с тем, к чему мы пришли своим вычислительным экспериментом: SAW + нормативная нормализация.
Наш переход — не самодеятельная заплатка, а независимо переоткрытая RAFSI-конструкция,
у которой есть публикация в Q1 и подтверждение в последующей литературе. **Это аргумент
для статьи КИМ и для защиты, причём готовый к цитированию.**

🟢 **Ограничения RAFSI — дословно (стр. 23, раздел 2.1). Это ровно наши риски:**

> «1) In this method the DM's set the interval for each criterion by assumption without the use
> of any standard formula.»

> «2) In this method for forming a standardized decision matrix, it is supposed that the optimal
> value is at least six times better than the non-optimal value, but it is not always true.»

> «3) This method assumes that for max type criteria if a_xj > a_Ij, then f(a_xj) = f(a_Ij);
> for min type criteria if a_xj < a_Ij, then f(a_xj) = f(a_Ij) — but this may lead to the same
> ranking of two different alternatives.»

Их же табличная формулировка претензий (Table 1, стр. 23):

> «Subjective criterion interval setting, reliance on an arbitrary superiority threshold, and
> the potential for identical rankings among different alternatives due to its assumptions on
> criteria types.»

Иллюстрация из статьи: при интервалах C₁ ∈ [2, 10] и оценках 12 и 10 у альтернатив A₁ и A₂
RAFSI даёт **f(12) = f(10)**, то есть A₁ и A₂ получают одинаковый ранг, хотя по критерию
максимизации A₁ строго лучше.

🔴 **Перенос на нас.** Это цена нормативной нормализации, и она наша тоже: нормы задаются
экспертно (методика ПДН, floor-резерв, горизонт целей), а всё, что выходит за норму,
**срезается в одну точку** — клиппинг. На решётке из 66 альтернатив с шагом 10% это реальный
сценарий: при высоком свободном денежном потоке верхние 10–20 распределений могут упереться
в потолок нормы сразу по нескольким критериям и стать **неразличимыми по свёртке**.
Проверяемое следствие: доля «связанных» (tied) альтернатив в топе как функция уровня дохода.
Если она растёт с доходом — патология подтверждена, и лечится расширением норм вверх
либо мягким (не жёстким) насыщением вместо клиппинга.

---

## 3. Компенсаторность и вето (вопрос 3) — самый сильный результат

🟢 **Jiménez-Martín, A., Sabio, P., & Mateos, A. (2015). Veto Values in Group Decision Making
within MAUT: Aggregating Complete Rankings Derived from Dominance Intensity Measures.
Proceedings of ICORES 2015, pp. 99–106.** DOI: 10.5220/0005180100990106 ·
https://www.scitepress.org/Papers/2015/51801/51801.pdf — прочитаны стр. 99–101.

Аддитивная модель и её статус, дословно (стр. 99):

> «The additive model is considered a valid approach in many practical situations for the reasons
> described in (Raiffa, 1982) and (Stewart, 1996). Its functional form is
> u(A_i) = Σ_{j=1..n} w_j u_j(x_ij)»

> «The additive model is a compensatory model in the sense that poor performance for an attribute
> can be compensated by good performances for other attributes.»

> «For some multicriteria decision analysis (MCDA) problems and certain attributes, however, DMs
> may find it convenient to provide a veto value that identifies attribute performances that rule
> out the alternative regardless of the value taken in the other attributes.»

Как вето встроено формально (стр. 101):

> «v(A_i) is the veto function that checks if the performances for a given A_i are within the
> respective veto intervals: v(A_i) = Π_{j} v_j(A_i), with v_j(A_i) = 1 if x_ij > v_j^U;
> 0 if x_ij ≤ v_j^U.»
> «Note that v(A_i) = 0 if at least one performance is within the veto interval for the
> corresponding attribute.»

Итоговая функция:

> «u^l(A_i) = [ Σ_{j=1..n} u_j(x_ij) w_j^l d_j(A_i) ] × v(A_i).»

🔴 **Это буквально архитектура FINPILOT.** Наши жёсткие инварианты Rt ≥ 0 и ПДН ≤ 0.40 —
это мультипликативная бинарная вето-функция v(A_i) ∈ {0, 1}, применяемая **до/поверх**
аддитивной свёртки. То есть «SAW с фильтром допустимости», который мы построили из
инженерных соображений, есть опубликованная и названная конструкция:
**additive multi-attribute value model accounting for veto**. Ответ на прямой вопрос задания
(«что уместно, когда часть ограничений вынесена в фильтр допустимости, а не в свёртку»):
эта гибридная схема — **признанный в MAUT способ ввести некомпенсаторность, не отказываясь
от аддитивной свёртки**. Переходить на PROMETHEE/ELECTRE ради некомпенсаторности нам
**не требуется** — мы уже в правильной ветке, и её можно назвать её собственным именем.

Обзор способов ввести некомпенсаторность — дословно (стр. 100):

> «In outranking methods the use of veto usually represents the intensity of preference of the
> minority (Roy and Slowinski, 2008). Nowak used ELECTRE-III to build a multi-attribute ranking
> using preference thresholds to distinguish situations of strict and weak preference in
> stochastic dominance approaches (Nowak, 2004). Later, Munda (2009) implemented a veto-based
> threshold using fuzzy set theory to represent qualitative information.»

> «Moreover, additive compensatory methods have also incorporated the concept of veto. An example
> is the technique for order preference by similarity to ideal solution (TOPSIS) method (Yoon,
> 1980). … Both alternatives behave like veto thresholds, but not in the strict sense of rejection
> of alternatives but as reference points for solving the decision-making problem.»

Про Choquet (стр. 100):

> «In connection with research based on the power of veto, (Marichal, 2004) proposes to
> axiomatize individual indices to valuate when each criterion behaves as a veto or for an
> aggregation by means of the Choquet integral. These indices make it possible to identify and
> measure the impact or trend of each criterion within the overall evaluation of the
> alternatives.»

🟡 Из выдачи, о разграничении семейств:

> «Non-compensatory methods include ELECTRE and PROMETHEE families. ELECTRE-III employs a
> non-compensatory model, such that poor performance on one criterion cannot be compensated
> by strong performance on another.»
> «ELECTRE uses the veto threshold as a parameter to express a strong opposition to an
> alternative being outranked by another.»

**Мультипликативная альтернатива как «мягкая» некомпенсаторность.** 🟢 Wang & Rangaiah 2025
(стр. 8-6) о MEW/WPM, P_i = Π F_ij^{w_j}:

> «As it uses a multiplicative aggregation, an alternative must perform reasonably well in each
> criterion to achieve a high overall performance score; this property helps avoid the possible
> excessive compensation (i.e., very high performance in one criterion fully offsets poor
> performance in another, as can occur in SAW).»

> «Due to its multiplicative structure, MEW is sensitive to extreme degradation in a particular
> criterion, as a low value can substantially reduce the overall product. This characteristic
> makes it well-suited for risk-averse applications.»

> «If the performance on a single criterion is zero (or extremely small) for a particular
> alternative, the product becomes zero (or very close to zero), effectively disqualifying that
> alternative regardless of its performance on other criteria.»

🔴 Для нас MEW интересен ровно тем, что задание называет опасным: «нельзя гасить провал по
ликвидности успехом по долгу». Но у MEW есть цена — обнуление при нулевом критерии, что на
нашей решётке встречается регулярно (доля 0% в резерв даёт L_t на нижней границе).
И вторая цена — потеря аддитивной объяснимости: вклад критерия перестаёт быть слагаемым.
🔴 **Мой вывод: MEW нам не подходит, а вето-конструкция подходит и уже применена.**

---

## 4. SAW против TOPSIS: устойчивость и объяснимость (вопрос 4)

🟢 **Murti, A. C., Ghozali, M. I., Puta, I. L., & Ikhwan, A. (2025). Analyzing criteria count
impact on SAW and TOPSIS stability in decision support systems. *ZERO: Jurnal Sains, Matematika
dan Terapan*, 9(2).** http://dx.doi.org/10.30829/zero.v9i2.25707

Дизайн: «five fixed alternatives with multiple random seeds», число критериев от 5 до 30,
синтетические данные.

> «SAW is more prone to ranking fluctuations, while TOPSIS demonstrates greater stability.»

> SAW: «quasi-linear growth in processing time (≈0.002-0.008 s)»; TOPSIS: «remains efficient
> (≈0.002-0.004 s) with minimal variance».

> «Kendall's Tau reveals variability across scenarios, and sensitivity tests confirm that
> agreement depends on data generation.»

🟡 **Оговорка, которая почти обнуляет применимость к нам.** Эксперимент варьирует **число
критериев (5→30) при пяти альтернативах**. У FINPILOT конфигурация обратная — **4 критерия
и 66 альтернатив**. Работа двигает ровно ту ось, по которой мы стоим, и держит фиксированной
ту, по которой мы растянуты. Переносить вывод «TOPSIS устойчивее» на нашу задачу нельзя.
🔴 **Работ, сравнивающих SAW и TOPSIS именно при малом числе критериев и большом числе
альтернатив, найти не удалось — это остаётся неизвестным.**

🟢 **Shyur, H.-J., & Shih, H.-S. (2024). Resolving rank reversal in TOPSIS: A comprehensive
analysis of distance metrics and normalization methods. *Informatica* (Vilnius), 35(4), 837–858.**
https://doi.org/10.15388/24-INFOR576 ·
https://www.informatica.vu.lt/journal/INFORMATICA/article/1356/text

> «If the primary concern is to avoid RR, then opting for Chebyshev distance can be the best
> solution.»

> «employing max normalization appears to yield a more resilient ranking result compared to
> using max-min normalization.»

Численно: rank reversal при манхэттенском расстоянии наступал при Δ_X₂ = 2.0, при евклидовом —
при Δ_X₂ = 2.6, то есть позже. SAW и WSM в статье **не упоминаются вовсе**.

🔴 **Прямое попадание в нашу находку.** Max-нормализация устойчивее min-max — независимое
подтверждение того, что патология минимаксной нормализации, которую мы поймали в
вычислительном эксперименте, **не артефакт нашей задачи, а известный дефект процедуры**.
Причём подтверждение получено **на другом методе (TOPSIS)** — значит дефект принадлежит
нормализации, а не свёртке. Для статьи это ценнее, чем подтверждение на том же SAW.

**Объяснимость.** 🟢 Wang & Rangaiah 2025 (стр. 8-5), достоинства SAW дословно:

> «(1) It is one of the simplest MCDM methods, requiring only the sum of the normalized weighted
> criteria values, which makes it very straightforward to understand and implement (Wang et al.,
> 2022). (2) Its computational procedure is relatively transparent, allowing decision-makers to
> easily observe how each criterion and weight contributes to the overall score. (3) Due to its
> simplicity, it can be readily applied in many fields, such as engineering, project selection,
> and resource allocation, where a quick ranking of alternatives is needed.»

🔴 Вот прямая цитируемая опора для нашего тезиса об объяснимости: «allowing decision-makers to
easily observe **how each criterion and weight contributes** to the overall score». В SAW
итоговый балл раскладывается на слагаемые w_j·F_ij, и каждое слагаемое — готовая строка
объяснения пользователю («резерв дал +0.18, долговая нагрузка −0.07»). У TOPSIS балл — это
C_i = d⁻/(d⁺+d⁻), отношение двух евклидовых расстояний; оно **не раскладывается в сумму
вкладов критериев**, и любое объяснение пользователю становится пересказом геометрии.
🟡 Прямой работы, измеряющей «плату за TOPSIS в объяснимости», найти не удалось —
аргумент строится из свойств формул, а не из измерения. Так и надо писать в статье.

---

## 5. MAUT: когда аддитивная свёртка теоретически обоснована (вопрос 5)

🟢 **UK Government Analysis Function. An Introductory Guide to MCDA.**
https://analysisfunction.civilservice.gov.uk/policy-store/an-introductory-guide-to-mcda/

> «The strict definition of Mutual Preferential Independence is that the trade-off between any
> two criteria is independent of a particular level of performance on any third criterion.»

> «It is important to understand that a linear additive model is not the only form of overall
> value function, but it is the standard form for MCDA. It is only valid when there is Mutual
> Preferential Independence between the criteria.»

Практический тест на нарушение — дословно:

> «Do not ignore a stakeholder's reluctance to offer a preference judgement, especially if they
> say 'it depends' on another criterion.»

Что делать при нарушении:

> «it may be possible to review the selection of objectives and criteria to eliminate it. This
> will usually be simpler than adopting alternative forms of overall value function.»

🟡 Из выдачи, определение и пример нарушения:

> «Preferential Independence occurs when a set of attributes Y is preferentially independent of
> its complement X-Y when the preference order over outcomes with varying values of attributes
> in Y does not change when the attributes of X-Y are fixed to any value.»

> «In real situations, preferential independence could be easily violated, because of the possible
> interaction between objective/criteria. … When preferential independence conditions are
> violated, the simple additive model cannot be applied, and more complex utility/value functions
> must be developed to capture the interactions between criteria.»

### 🔴 Ответ на прямой вопрос: наша коллинеарность — это НЕ нарушение preferential independence

Называю точно, потому что задание просило точности, и здесь легко ошибиться.

**Preferential independence (Keeney & Raiffa)** — свойство **предпочтений ЛПР**:
готовность обменять единицу критерия A на единицу критерия B не зависит от уровня критерия C.
Нарушается, когда критерии **взаимодействуют в голове у пользователя**. Тест — вербальный
(«это зависит от…»), лечение — пересмотр состава критериев либо Choquet/GAI-модель.

**Коллинеарность критериев ресурса и ликвидности, которую мы обнаружили** — свойство
**матрицы решений**, а не предпочтений: два столбца ACM статистически почти дублируют друг
друга на нашем множестве альтернатив. Это нарушение **не preferential independence, а
non-redundancy** — третьего требования к «coherent family of criteria» по Бернару Руа.
🟡 Из выдачи:

> «According to Bernard Roy, a family of criteria is said to be coherent when it is exhaustive/
> complete, cohesive and non-redundant.»
> «Non-redundancy: The criteria should cover all that is to be measured, with as little
> overlapping/redundancy as possible.»

Первоисточник: Roy, B. (1996). *Multicriteria Methodology for Decision Aiding* — 🔴 не открыт,
термин известен по вторичной выдаче.

Практическое следствие редундантности в аддитивной свёртке названо в литературе HTA
как **double counting** (🟡 сниппет):

> «Double-counting can occur when trial design is already taken into account through the Quality
> of Evidence criterion or weight-factor, so it needs to be carefully avoided if the criterion is
> considered separately.»

🔴 **Итог по вопросу 5.** Наша находка — двойной счёт из-за редундантности критериев,
а не нарушение аддитивности. Это важное различие для статьи: **из редундантности не следует,
что аддитивная свёртка неприменима**; из неё следует, что эффективные веса искажены
(коллинеарная пара получает суммарный вес w_R + w_L там, где ЛПР назначал w_R). И лечится
это ровно тем, чем мы лечили — **переопределением критериев** (прогнозный ресурс,
ликвидность по запасу), что и есть рекомендация UK Gov: «review the selection of objectives
and criteria to eliminate it». А вот вопрос, независимы ли наши четыре критерия
**предпочтительно**, — отдельный, **эмпирически нами не проверявшийся**, и он проверяется
не корреляциями, а опросом пользователей на предмет «это зависит от…».
🔴 Кандидат на подозрение: обмен «долговая нагрузка ↔ обеспеченность целей», скорее всего,
зависит от уровня ликвидности (при пустом резерве человек не готов менять долг на цели ни
в какой пропорции). Если это так, MPI у нас нарушено, и часть нарушения уже съедена
floor-резервом — что, кстати, **ещё один аргумент в защиту вынесения floor в фильтр**.

---

## 6. Устойчивость к возмущению весов (вопрос 6)

🟡 **O'Shea, R., Deeney, P., Triantaphyllou, E., Diaz-Balteiro, L., & Armagan Tarim, S. (2026).
Weight stability intervals for multi-criteria decision analysis using the weighted sum model.
*Expert Systems with Applications*, 296, 128460.** https://doi.org/10.1016/j.eswa.2025.128460 ·
реферат: https://research.ucc.ie/en/publications/weight-stability-intervals-for-multi-criteria-decision-analysis-u/

🔴 Полный PDF по указанному в задании адресу **отдал 403** — вопреки ожиданию задания, и без
Bash обойти нечем. Ниже — по реферату.

> «Multi-criteria decision analysis (MCDA), or multi-criteria decision making (MCDM) encompasses
> a wide set of mathematical methods to compare alternatives whilst considering multiple criteria
> and the relative importance (weight) of each criterion or the allowable trade-off between
> criteria.»

Два заявленных вклада (по реферату): (1) метод определения **точных** интервалов устойчивости
весов для WSM, **не опирающийся на перебор или симуляцию**; (2) использование этих интервалов
для выявления наиболее чувствительных весов через **подход Парето-доминирования**, с учётом
и допустимого увеличения, и допустимого уменьшения веса. Демонстрация — на альтернативах
производства биогаза.

🔴 **Сопоставление с нами, и оно неутешительное в одну сторону.** Наша проверка устойчивости
к весам, насколько известно из постановки задачи, делается **симуляцией** (варьирование весов
профилей и наблюдение ранга). O'Shea et al. предлагают ровно то, чего у нас нет: **аналитические
интервалы**, вычисляемые в замкнутой форме для WSM — то есть для нашей свёртки один в один.
Метод **не совпадает** с нашим: у нас статистика по прогонам, у них — точные границы.
Это не ошибка в нашей модели, но это **прямая возможность усилить главу об устойчивости**:
заменить «мы прогнали N сценариев и ранг не менялся» на «интервал устойчивости веса
ликвидности составляет [w−a, w+b], пять риск-профилей лежат внутри/вне него».
🟡 Формул нет — статья не открыта.

Для контекста, 🟢 UK Gov про стандартную практику анализа чувствительности:

> «Your review should concentrate most closely on the effect the analysis has had on the option
> rankings.»

---

## 🔴 СЛЕДСТВИЯ ДЛЯ FINPILOT

### A. Подтверждает наш выбор (повод лучше объяснить, а не менять)

1. **SAW + нормативная нормализация = RAFSI.** Наш переход с минимаксной на нормативную
   нормализацию — не заплатка, а независимо переоткрытая опубликованная конструкция
   (Žižović et al. 2020; изложение — Bisht & Pal 2024). Заявленное свойство: устранение
   rank reversal за счёт того, что опорные точки заданы ЛПР, а не выборкой.
   **Действие: цитировать в статье КИМ и в защите, назвать наш метод «SAW с RAFSI-подобной
   нормативной нормализацией».** Модель не менять.

2. **Жёсткие инварианты Rt ≥ 0 и ПДН ≤ 0.40 до свёртки — это «additive model accounting for
   veto»** (Jiménez-Martín et al. 2015, формула u(A) = [Σ w_j u_j d_j] × v(A)).
   Наша гибридная схема — признанный в MAUT способ ввести некомпенсаторность без отказа
   от аддитивности. **Действие: назвать вещь своим именем в docs и в статье.**
   Переход на PROMETHEE/ELECTRE ради некомпенсаторности **не требуется** — это был бы
   отказ от объяснимости ради свойства, которое у нас уже есть.

3. **Патология минимаксной нормализации подтверждена независимо и на другом методе**
   (Shyur & Shih 2024: max устойчивее max-min). Наша находка — не артефакт задачи.
   **Действие: цитировать как внешнее подтверждение раздела о вырожденности.**

4. **Объяснимость SAW — цитируемое преимущество, а не наше самомнение**
   (Wang & Rangaiah 2025: «allowing decision-makers to easily observe how each criterion and
   weight contributes to the overall score»). У TOPSIS балл C_i = d⁻/(d⁺+d⁻) в сумму вкладов
   не раскладывается. **Действие: вставить этот аргумент в раздел «почему не TOPSIS».**

5. **Фиксированность решётки 66 альтернатив.** Rank reversal в литературе всегда привязан
   к **изменению состава множества** (добавление, удаление, копия, замена на анти-идеал,
   декомпозиция). У нас состав фиксирован конструкцией. **Действие: сказать это явно —
   у нас два независимых заслона от rank reversal, а не один: фиксированная решётка
   И нормализация, не зависящая от выборки.**

### B. Ставит под вопрос (требует проверки, возможно — изменения)

6. **🔴 Клиппинг нормативной нормализации может делать альтернативы неразличимыми.**
   Ограничение RAFSI №3, дословно подтверждённое примером в источнике: «f(12) = f(10) …
   this may lead to the same ranking of two different alternatives». На нашей решётке при
   высоком свободном потоке верхние распределения могут упереться в потолок норм по
   нескольким критериям сразу. **Действие: измерить долю tied-альтернатив в топ-5 как
   функцию уровня дохода. Если растёт — рассмотреть мягкое насыщение вместо жёсткого
   среза либо расширение верхних норм.** Это **повод менять модель**, если эффект найдётся.

7. **🔴 Preferential independence наших четырёх критериев не проверялась.**
   Мы проверили коллинеарность (свойство матрицы), а MPI — свойство предпочтений, и оно
   проверяется опросом, а не корреляцией. Подозрительная пара: обмен «долг ↔ цели»
   при разном уровне ликвидности. **Действие: включить в пользовательское тестирование
   вопрос-ловушку по схеме UK Gov («это зависит от…»).** Если MPI нарушено — аддитивная
   свёртка формально неприменима без оговорки, и оговорку надо будет написать честно
   (либо показать, что floor-резерв гасит зависимость).

8. **🟡 Устойчивость к весам можно посчитать точно, а не симуляцией**
   (O'Shea et al. 2026, аналитические weight stability intervals для WSM).
   **Действие: достать полный текст, когда будет доступен Bash или другой канал,
   и заменить симуляционную проверку аналитической.** Повод усилить, не менять.

### C. Терминологические исправления в наших материалах

9. Найденную нами **коллинеарность критериев ресурса и ликвидности** нельзя называть
   нарушением preferential independence или «взаимодействием критериев» — это
   **нарушение non-redundancy** в смысле coherent family of criteria (Roy 1996), приводящее
   к **double counting** эффективных весов. Разные явления, разные лечения.
   🔴 Если в статье КИМ или в `docs/math_model.md` эти термины смешаны — исправить.

---

## ЧТО ОСТАЛОСЬ НЕИЗВЕСТНЫМ

1. **Доказательство теоремы RAFSI о rank reversal** — Žižović et al. (2020), MDPI, 403.
   Известна только формулировка по сниппету. Мы опираемся на пересказ в Bisht & Pal.
2. **Barzilai & Golany** — «никакая нормализация не предотвращает rank reversal»: полный
   текст не открыт, разрешение противоречия с RAFSI (§1) — мой вывод, не прочитанное.
3. **Vafaei et al. полностью** (2018, 2020, 2022) — ScienceDirect и Springer закрыты.
   Заявленный «критерий выбора нормализации» известен только по рефератам, и по ним он
   выглядит **эмпирико-статистической рамкой (топология данных + корреляции Спирмена/Пирсона),
   а не аналитическим критерием**. Аналитического критерия выбора нормализации в найденной
   литературе нет вовсе.
4. **Сравнение SAW vs TOPSIS при 4 критериях и десятках альтернатив** — работ не найдено.
   Единственная найденная (Murti et al. 2025) варьирует ортогональную нам ось.
5. **Полный текст O'Shea et al. (2026)** и его формулы — 403, только реферат.
6. **PROMETHEE** — ни одного открытого первоисточника не добыто; всё, что есть в отчёте
   про PROMETHEE, это классификационные фразы из выдачи. Угол закрыт как пустой.
7. **Измеренная «плата за TOPSIS в объяснимости»** — эмпирических работ не найдено;
   наш аргумент выводится из структуры формул.

---

## ДОБОР Г31.5 — отказ адреса (17.09.2026)

**Каналы на начало работы (замер 17.09.2026, коды дословно):** Unpaywall **200** (1 164 б) · Crossref **200** (16 033 б) · OpenAlex **200** (18 331 б) · EuropePMC **200** (17 910 б) · S2 `/paper/search/bulk` **200** (31 142 б) · S2 `/paper/DOI:` **404** на DOI, отсутствующем в S2 (не отказ канала) · `r.jina.ai` без UA **200** (321 б) · Wayback replay **302** (редирект на снимок, штатно). Сессия один раз упала на лимите АККАУНТА (HTTP 429 харнесса), аккаунт сменён — к каналам добычи отношения не имеет.

Раздел «ЧТО ОСТАЛОСЬ НЕИЗВЕСТНЫМ» этого файла (последнее упоминание — строки 568–583, других доборов в файле нет) числит закрытыми четыре пункта по одному адресу каждый: MDPI 403, ScienceDirect 403, `peterdeeney.com` 403, `metrology-journal.org` 403. Все четыре — класс Г31.5.

### Г31.5-M1. 🟢 Žižović et al. 2020, RAFSI — ПОЛНЫЙ ТЕКСТ ДОБЫТ, доказательство снято

- Unpaywall `10.3390/math8061015` — **200**: `is_oa: true`, `oa_status: "gold"`, локации `mdpi.com/2227-7390/8/6/1015/pdf?version=1592731444` (publisher) и DOAJ.
- Прямой `curl -sL` с UA по этому PDF — **403, 411 б** (тот самый отказ, записанный в файл).
- 🟢 `r.jina.ai` **без UA** по странице `https://www.mdpi.com/2227-7390/8/6/1015` — **HTTP 200, 67 024 б**, полный текст статьи, «Published Time: 2020-06-21». sha256 снятого текста `d349e5604db27a59770505608a6b080343aeee77137d62baa007437fd94f960f`.

**Нормировка и итоговая функция ДОСЛОВНО (разд. 2, шаги 4–5):**

> «Step 4: Form normalized decision matrix … (a) for the criteria C j max type: ŝ_ij = s_ij / (2A) (7); (b) for the criteria C j min type: ŝ_ij = H / (2 s_ij) (8)»
>
> «For max type criteria … 0 < n_1/(2A) ≤ ŝ_ij ≤ n_2k/(2A) < 1 (10)» ; «for min type criteria … 0 < H/(2 n_2k) ≤ ŝ_ij ≤ H/(2 n_1) < 1 (11)»
>
> «Proof of (10): n_2k/(2A) = n_2k / (2·(n_1+n_2k)/2) = n_2k/(n_1+n_2k) < (n_2k+n_1)/(n_1+n_2k) = 1»
>
> «Additionally, for the boundary values of criteria intervals n_1 and n_2k, we have the following equality (12) and (13): n_1/(2A) = H/(2 n_2k) (12); n_2k/(2A) = H/(2 n_1) (13)»
>
> «Step 5: Calculate criteria functions of the alternatives V(A_i) … V(A_i) = w_1 ŝ_i1 + w_2 ŝ_i2 + … + w_n ŝ_in (14)»

Здесь A и H — арифметическое и гармоническое среднее границ n_1 и n_2k ЕДИНОГО интервала, в который отображаются заданные ЛПР идеальная и анти-идеальная точки (шаги 1–3). Ни одна величина нормировки не зависит от состава множества альтернатив.

🔴 **Главное, что даёт первоисточник и чего не было в файле: «теоремы о rank reversal» в статье НЕТ.** Доказываются только (10)–(13) — что нормированные значения лежат в (0;1) и что границы для max- и min-критериев совпадают. Устойчивость к RR показана **экспериментально** (разд. 4.2), не доказана. Запись «Доказательство теоремы RAFSI о rank reversal — не добыто» (п. 1 «ЧТО ОСТАЛОСЬ НЕИЗВЕСТНЫМ») описывала несуществующий объект.

**Эксперименты разд. 4.2 ДОСЛОВНО:**

> «The first experiment: … in each subsequent scenario, the worst-ranked researcher from the set is eliminated. … In all these scenarios, the criteria functions of the alternatives remained unchanged. TOPSIS, VIKOR, and COPRAS methods are used in the same condition. All these methods also showed stability and resistance to rank reversal. However, changes in criteria function values are observed in these methods.»
>
> «The second experiment: … another candidate (A7) is added … (4) RAFSI method: This method showed stability in both sets of alternatives. All the alternatives kept the same f(Ai) values in both sets.» — при этом у TOPSIS «alternative A2 was third in the old set, while, in the new set, it is in the fifth position instead of the fourth», у VIKOR «alternative A3 was in the fifth rank in the old set, but, in the new set, it is ranked last».

И побочный результат разд. 4.1, прямо про нормировку: «data normalization, as suggested in RAFSI method, was also used for TOPSIS, VIKOR, and COPRAS methods. After using the new normalization technique, **identical rankings were obtained by all the methods**.»

**Выжимка.** (14) — это ровно взвешенная сумма, то есть SAW. Всё отличие RAFSI от SAW — в нормировке к фиксированным ЛПР-опорным точкам вместо min/max по текущей выборке. Первоисточник, таким образом, прямо подтверждает тезис §1–2 файла («причина rank reversal — нормировка, а не аддитивная свёртка»), но как **конструктивный довод и численный пример на 6–7 альтернативах**, а не как теорема. Для обоснования нашей нормативной нормировки ссылаться на RAFSI можно в форме «та же конструкция описана и проверена экспериментом», но не «доказана устойчивость».

### Г31.5-M2. 🟢 O'Shea et al., WSM weight stability intervals — ПОЛНЫЙ ТЕКСТ ДОБЫТ по тому же адресу

- Прямой `curl -sL` с браузерным UA по `https://peterdeeney.com/wp-content/uploads/2025/07/OShea-et-al-2025-MCDA-L1.pdf` — **HTTP 200, 1 078 100 б**, PDF 1.7, **14 страниц** (`pdfinfo`), `pdftotext -layout` → 1 072 строки. sha256 `8c713da1d7b2f7ecc61b4e714236f0cdfca431eab3386b1afd66adb54037142e`.
- 🔴 Запись файла «403 (вопреки ожиданию задания)» — отказ ОДНОГО ЗАХОДА: тот же адрес сегодня отдаёт файл целиком. Адрес не менялся, менялся заход.
- Реквизиты из самого файла: O'Shea R., Deeney P., Triantaphyllou E., Diaz-Balteiro L., Tarim S. A. «Weight stability intervals for multi-criteria decision analysis using the weighted sum model». *Expert Systems With Applications* **296 (2026) 128460**. (Файл писал «2025»/«2026» вперемешку — год тома 2026.)

**Абстракт ДОСЛОВНО (с. 1):**

> «A key consideration in any MCDA is the sensitivity of the results obtained to alterations of the criteria weights used. Prior methods to determine the weight stability interval (WSI, the range of values for individual weights for which the ranking of alternatives will not change) include the manual alteration of criteria weights, the use of different sets of criteria weights in a form of scenario analysis, or the process of iteratively searching for the maximum and minimum allowable alterations to individual criteria weights to determine the weight stability interval. The first contribution of this paper is the development of a novel method for determining precise weight stability intervals which does not rely on enumeration or simulation for use with the weighted sum model (WSM, based on the L1 Minkowski norm), one of the most widely used aggregation methods within MCDA. The second contribution of this work is the use of these WSIs to identify the most sensitive weight(s) based on a Pareto dominance approach whilst considering both the allowable increase and decrease in criteria weights.»

**Формулы ДОСЛОВНО (с. 4–5; сверено чтением отрисованных страниц 4–5 PDF, не только `pdftotext` — двухколоночная вёрстка ломает дроби):**

> «Utopia_j = max(p_1j,…,p_nj) if c_j is a benefit criterion … min(p_1j,…,p_nj) if cost; Nadir_j = min(…) if benefit … max(…) if cost» ;
> «x_ij^Nadir = |Nadir_j − p_ij| / |Nadir_j − Utopia_j| (1)» ; «d_i = L1(A_i) = Σ_j w_j x_ij (4). Equation (4) is equivalent to the simple additive weighting (SAW), or weighted sum model (WSM)»
>
> «Theorem 1. If two alternatives A_K and A_L are ranked as A_K > A_L under the WSM method when the Nadir alternative is used for reference, then these two alternatives will be ranked in exactly the same way when the Utopia alternative is considered, and vice-versa.» (доказательство — через D_12^Nadir = −D_12^Utopia, (10)–(11))
>
> «w*_j = (1 + α_j) w_j (12), where, for w*_j to remain non-negative, α_j ≥ −1. In order for the relative weight ratios of the remaining weights to remain unchanged … β_j = (1 − (1 + α_j) w_j) / (1 − w_j) (13); w*_i = β_j w_i (14), where, for w*_i to remain positive α_j < (1 − w_j)/w_j.»
>
> «d_E^Nadir* = ((1 + α_j)(1 − w_j) w_j x_Ej + (1 − w_j + α_j w_j)(d_E^Nadir − w_j x_Ej)) / (1 − w_j) (15)» ;
> «α_j = (1 − w_j)(d_F^Nadir − d_E^Nadir) / ( w_j (x_Ej − x_Fj − d_E^Nadir + d_F^Nadir) ) (16)»
>
> «α_j^− = max(−1, α_j) if α_j ≤ 0; −1 if α_j > 0 (17)» ; «α_j^+ = min((1 − w_j)/w_j, α_j) if α_j ≥ 0; (1 − w_j)/w_j if α_j < 0 (18)» ;
> «This process provides the normalised weight stability interval (wsi) for the normalised weight w_j of criterion c_j, namely wsi_j = [w_j(1 + α_j^−), w_j(1 + α_j^+)] = [w_jL, w_jU]. This ensures that alternative A_E performs better than alternative A_F for an alteration to a single criterion weight, w_j, within [w_jL, w_jU].»

**Выжимка.** (16)–(18) дают интервал устойчивости веса **в замкнутой форме, без перебора и Монте-Карло**, для пары альтернатив при пропорциональной перенормировке остальных весов — ровно та схема весов, что у нас (сумма = 1). Для 66 альтернатив это O(66 · k) вычислений на критерий против лидера. 🔴 Оговорка применимости: Utopia/Nadir у авторов — min/max **по текущей выборке**, т. е. их нормировка зависит от состава альтернатив (класс, подверженный RR по M1); сами формулы (12)–(18) от этого не зависят и переносятся на нормировку к фиксированным опорным точкам без изменений, поскольку используют только x_Ej, x_Fj и d^Nadir.

### Г31.5-M3. 🟢 Vafaei et al. 2022, Procedia CS — ПОЛНЫЙ ТЕКСТ ДОБЫТ через репозиторий, который Unpaywall называл прямо

- Файл записывал: ScienceDirect страница **403**, прямой PDF **403** → «не открыто», «ScienceDirect и Springer закрыты».
- Unpaywall `10.1016/j.procs.2022.01.156` — **200**: `is_oa: True`, `oa_status: "gold"`, вторая локация **`run.unl.pt/bitstreams/48b7fbce-477f-45f7-ac0c-8fa244d26cba/download`** (repository, помечена `submittedVersion`).
- `curl -skL` с UA по этому адресу — **HTTP 200, 662 030 б, `application/pdf`**, 8 страниц, sha256 `4539fd0964ab9f2a4f1d66797708418bda8a38704fdb89672e3c1f1440185cbf`. 🔴 Метка `submittedVersion` **неверна**: в файле журнальная вёрстка с колонтитулом «Nazanin Vafaei et al. / Procedia Computer Science 199 (2022) 1229–1236».
- Попутно: `r.jina.ai` без UA по странице ScienceDirect — **200, 11 827 б**, только абстракт и метка «Open access / Under a Creative Commons license». Статья — gold OA, закрыт был бот-канал, не доступ.

**Абстракт ДОСЛОВНО:** «Using different normalization techniques may result in different rankings of alternatives. … we assess different normalization techniques with the Simple Additive Weighting (SAW) method using metrics from the proposed assessment framework and select the most adequate technique for a small case study that is borrowed from literature.»

**Результат ДОСЛОВНО (Table 4, SAW, кейс Chakraborty & Yeh: 6 альтернатив, 5 критериев):**

| | Max | Max-Min | Sum | Vector |
|---|---|---|---|---|
| Euclidean↑ | 0.2172 | 0.5912 | 0.1790 | 0.1850 |
| STD↑ | 0.0397 | 0.1079 | 0.0327 | 0.0338 |
| RCI↑ | 3 | 2.6667 | 4 | 3.6667 |
| MSE↓ | 1.7778 | 4.7778 | 2.4444 | 2.7778 |
| Mean ks↑ | 0.4640 | 0.1500 | 0.3210 | 0.393 |
| PV (Table 5) | 2 | 2 | 1 | 0 |

> «By implementing PV, we conclude that our framework selects the Max and Max-Min normalization as the best techniques for this case because it has the highest PV, while the approach by Chakraborty and Yeh [11], recommended the Max normalization technique.»

**Выжимка.** Работа про выбор нормировки для SAW по согласованности рангов на ОДНОМ кейсе из 6 альтернатив; rank reversal при добавлении/удалении альтернатив **не тестируется**, фиксированных опорных точек среди кандидатов нет. Для нас это слабый источник: подтверждает лишь, что «разные нормировки — разные ранги» у SAW (тезис §1 файла), и что голосование по метрикам даёт ничью. Числа кейса на наш выбор не переносятся.

### Г31.5-M4. 🟢 Duc Trung et al. 2022, «Comparison of the RAFSI and PIV method» — ПОЛНЫЙ ТЕКСТ ДОБЫТ

- Файл записывал: `metrology-journal.org/…/ijmqe220020.html` — **403** → «не открыто».
- `r.jina.ai` без UA по тому же адресу — **HTTP 200, 52 286 б**, полный текст. Реквизиты: *Int. J. Metrol. Qual. Eng.* **13**, 14 (2022), EDP Sciences, **CC BY 4.0**, Hanoi University of Industry.

**Абстракт ДОСЛОВНО:** «However, rank reversal after adding or removing an alternative can occur in using some of the methods. In this study, two methods RAFSI and PIV were compared for application of making multi-criteria decisions. They are known to be capable of avoiding rank reversal problems. Sixteen 9XC steel turning tests were performed … Four methods including MEREC, ROC, RS and EQUAL were used for determining weights of the criteria. The blend of two multi-criteria decision making methods (RAFSI and PIV) with four weight-determining methods resulted in eight ranking options. … all eight ranking options identified the same best test.»

**Вывод ДОСЛОВНО (разд. 6):** «Under the RAFSI method, the best and worst alternatives do not depend on the weighting methods. The ranking results of the alternatives are the same as the MEREC and EQUAL methods are applied. The ranking order of the alternatives overlaps fourteen out of sixteen as the weights of the criteria are identified by the two methods ROC and RS. … the similarity in ranking order of the alternatives using the PIV method is less than the RAFSI method.»

**Выжимка.** 🔴 Несмотря на заголовок и абстракт, **rank reversal при добавлении/удалении альтернатив в работе не проверяется** — сравнивается устойчивость рангов к смене метода ВЕСОВ. Для вопроса «устойчив ли RAFSI/нормативная нормировка к RR» источник пуст; для вопроса «чувствителен ли ранг к схеме весов» — 14 из 16 совпадений позиций при ROC/RS против MEREC/EQUAL, один кейс. Ценность малая, запись «не открыто» снимается.

## ИТОГ Г31.5 — mcda_saw_alternatives

**4 кандидата класса, 4 закрыты полным текстом.**

| Пункт | Записанный отказ (один адрес) | Чем закрыт |
|---|---|---|
| Žižović 2020 RAFSI (MDPI) | `mdpi.com` 403 | **`r.jina.ai` без UA** по странице (200, 67 024 б) |
| O'Shea et al. 2026 ESWA | `peterdeeney.com` PDF 403 | **прямой `curl -sL` с UA по тому же адресу** (200, 1 078 100 б) — отказ одного захода |
| Vafaei 2022 Procedia CS | ScienceDirect 403 (страница и PDF) | **Unpaywall → репозиторий `run.unl.pt`** (200, 662 030 б) |
| Duc Trung 2022 IJMQE | `metrology-journal.org` 403 | **`r.jina.ai` без UA** (200, 52 286 б) |

🔴 **Что меняет обоснование (канон не трогается):**
1. **«Теоремы RAFSI о rank reversal» не существует** — устойчивость показана экспериментом на 6–7 альтернативах, доказаны лишь границы нормировки (10)–(13). Итоговая функция RAFSI (14) — это SAW. Ссылаться: «конструкция нормировки к фиксированным опорным точкам описана и экспериментально проверена», не «доказана». Пункт 1 «ЧТО ОСТАЛОСЬ НЕИЗВЕСТНЫМ» снимается как описывавший несуществующий объект.
2. **Интервалы устойчивости весов SAW в замкнутой форме** (O'Shea (16)–(18)) — готовый метод для анализа чувствительности пяти риск-профилей без Монте-Карло; прямо смыкается с §6 файла и с Г30.2-К. Заведение проверки — решение владельца.
3. Vafaei 2022 и Duc Trung 2022 **RR при смене состава альтернатив не тестируют** — если где-то в базе на них сослались как на подтверждение устойчивости к RR, ссылка неверна.

Остаётся по файлу: п. 3 Vafaei 2018/2020 (Springer) — в этот заход не брались, см. сводный итог (ЗАДОЛЖЕННОСТЬ); п. 6 PROMETHEE — угол закрыт как пустой содержательно, не отказом адреса, класс Г31.5 к нему неприменим; Li 2026 Wiley `10.1002/mcda.70027` — см. ЗАДОЛЖЕННОСТЬ.
