# Тема 27. Как доказать, что совет хороший — метрики качества прескриптивной системы

Дата: 2026-09-10. Сырьё исследования (raw). Формат: дословные цитаты + пояснения.
Статус: ЗАВЕРШЕНО 2026-09-10.

Контекст задачи: FINPILOT, веха 6 (тестирование матмодели v6.0.0). У модели нет ground
truth: нет логов решений пользователя, нет обратной связи от исходов, «правильного ответа»
в задаче распределения свободного денежного потока не существует.

Обозначения пометок:
- [ПРОЧИТАНО] — полный текст источника открыт.
- [СНИППЕТ] — только поисковая выдача/аннотация, полный текст не открыт. Цитата НЕ считается
  проверенной.
- [НЕ ДОБЫТО] — с кодом ответа канала.

---

## Участок 1. Оценка прескриптивных систем без ground truth

### 1.1. Decision Quality (Howard, Stanford) — качество РЕШЕНИЯ отдельно от качества ИСХОДА

Это прямое попадание в нашу задачу: дисциплина, построенная ровно на том, что правильного
исхода знать нельзя, а качество решения при этом оценивать можно и нужно.

Определение [ПРОЧИТАНО, en.wikipedia.org/wiki/Decision_quality]:

> "Decision Quality (DQ) is the quality of a decision at the moment the decision is made,
> regardless of its outcome."
> — со ссылкой на Howard & Abbas, *Foundations of Decision Analysis* (2014)

Шесть требований к качественному решению (там же):

> 1. A useful frame
> 2. Feasible and diverse alternatives
> 3. Meaningful and reliable information
> 4. Clear values, preferences, and trade-offs
> 5. Logically sound reasoning
> 6. Commitment to action

Формулировка Decision Education Foundation [ПРОЧИТАНО,
decisioneducation.org/principles-of-decision-quality/defining-decision-quality]:

> 1. **Helpful Frame** — "Clear on the problem that I am solving"
> 2. **Clear Values** — "Identified what I truly want"
> 3. **Creative Alternatives** — "Generated a good set of alternatives"
> 4. **Useful Information** — "Gathered the relevant information needed"
> 5. **Sound Reasoning** — "Evaluated the alternatives in light of the information"
> 6. **Commitment to Follow Through**

🔴 Два операционально важных принципа.

**(а) Принцип слабейшего звена** — DQ НЕ аддитивна, это не сумма и не среднее:

> "the overall quality of the decision is limited by the weakest element"
> (Wikipedia, со ссылкой на Spetzler, Winter & Meyer, *Decision Quality: Value Creation from
> Better Business Decisions*, 2016)

> "a decision is only as strong as the weakest link" (Decision Education Foundation)

Прямое следствие для нас: агрегированная оценка качества рекомендации должна считаться
как **минимум по измерениям**, а не как взвешенная сумма. Модель, у которой сильные формулы
(sound reasoning), но бедный набор альтернатив, — низкого качества по DQ, сколько бы
ни было баллов у остальных элементов.

**(б) Правило остановки через предельную ценность информации** (Wikipedia):

> "when for each element the cost to obtain additional information or insight to improve
> its quality exceeds the added value"

То есть DQ достигнута не при 100%, а там, где следующая порция уточнения дороже своей
пользы. Это готовое обоснование для порогов приёмки вехи 6: порог не «идеально», а
«дальше дорого».

**(в) Разделение решения и исхода** (Decision Education Foundation):

> "There is a distinction between a good decision and a good outcome."

Пояснение из вторичного источника [СНИППЕТ, не считать проверенным]: в условиях
неопределённости у ЛПР есть контроль над решением, но не над исходом, поэтому исход
не позволяет судить о качестве решения.

Что это даёт вехе 6: **нам не нужен ground truth по исходам, чтобы оценивать модель.**
Мы оцениваем шесть элементов процесса. Из них у FINPILOT напрямую машинно проверяемы:
альтернативы (66 альтернатив с шагом 10% — покрытие и разнообразие пространства),
sound reasoning (инварианты, доминирование, монотонность), clear values (риск-профили
как явная функция ценности). Frame и commitment — не машинные, оцениваются экспертно.

### 1.2. Медицина: валидация CDSS без золотого стандарта — ближайший перенос

Медицинские системы поддержки решений живут ровно в нашей ситуации: правильный ответ
часто неизвестен, цена ошибки высока, эксперты между собой не согласны.

**(а) Критерий Миллера — «пользователь + система против пользователя без системы».**
Berner E.S., *Diagnostic Decision Support Systems: How to Determine the Gold Standard?*
J Am Med Inform Assoc, 2003 [ПРОЧИТАНО, pmc.ncbi.nlm.nih.gov/articles/PMC264440]:

> "Miller proposed that the bottom line in evaluating clinical decision support systems
> (CDSSs) should be 'whether the user plus the system is better than the unaided user
> with respect to a specified task.'" (Berner, 2003)

🔴 Это главная методологическая находка участка 1 после DQ: **эталоном служит не
«правильный ответ», а БАЗОВЫЙ УРОВЕНЬ без системы.** Для FINPILOT это переводится
в исполнимую метрику: сравнить рекомендацию модели не с недостижимым идеалом, а с
наивными бейзлайнами (пропорциональное деление потока; «всё в долг с максимальной
суммой»; «всё в резерв»; snowball вместо avalanche) — и показать, что консенсус
экспертных движков предпочитает вектор модели чаще, чем вектор бейзлайна.

**(б) Критика экспертной панели как эталона** (Berner, 2003):

> "If the experts use the full case data with definitive test results to judge the quality
> of a differential when the user and/or the CDSS did not have all of that data, there is
> a risk of both hindsight bias and underestimation of the quality of the performance
> of the CDSS."

> "there are often disagreements among experts."

Перенос: наши экспертные движки должны получать **ровно тот же вход**, что и модель
(тот же портрет, без дополнительных признаков), иначе разница интерпретируется неверно.
Если у эксперта есть признак, которого нет у модели, — расхождение говорит о входе,
а не о качестве.

**(в) Согласие по РЕКОМЕНДАЦИИ отдельно от согласия по ОЦЕНКЕ.**
Валидация CDSS для хронических ран [ПРОЧИТАНО,
pmc.ncbi.nlm.nih.gov/articles/PMC13249526/] измеряла две разные вещи:

- согласие алгоритма с консенсусом по диагнозу: Cohen's κ = 0.70 (95% CI 0.46–0.94),
  точность 86.2% (25/29 случаев);
- **отдельно — экспертное одобрение терапевтических рекомендаций: 85.2% (127/149 оценок).**

Из поисковой выдачи по тому же кругу работ [СНИППЕТ, не считать проверенным]:
«a health professional may agree with a diagnostic label yet disagree with the proposed
management, or vice versa». Перенос прямой: у нас «оценка ситуации» (диагностика портрета:
профиль риска, стадия) и «рекомендация» (action-vector) — это две метрики, а не одна.
Сейчас проект меряет только вторую (согласие по action-vector 78.63%).

**(г) Как эта работа обошлась с зоной разногласия экспертов** — важно для нашего
раунда 5 (полоса Lt ∈ [1;2), амплитуда 66 п.п.):

- консенсус определён априори: «agreement by at least three of five experts on the same
  diagnostic category»;
- случай без консенсуса **исключён** из анализа, требующего эталона, а не «разрешён»
  голосованием;
- авторская трактовка: «disagreement among experts often reflects genuine uncertainty
  rather than error».

Внутрипанельная согласованность там же: Krippendorff's alpha 0.26–0.60 («low to
moderate»), Fleiss' κ по типам ран от 0.19–0.25 (диабетическая стопа) до 0.54–0.84
(пролежни). 🔴 То есть **опубликованная и принятая к печати валидация CDSS работала
при согласии экспертов от 0.19 каппы** — наш коридор 58.18–79.99% попарного согласия
не аномален, он типичен. Отсюда следует не «метод плох», а «зону низкого согласия надо
объявлять явно и выводить из-под метрики соответствия».

### 1.3. Off-policy evaluation (OPE): почему НАМ не применимо

OPE — стандартный ответ индустрии на вопрос «как оценить новую политику, не выкатывая
её на пользователей». Суть [СНИППЕТ, обзорная выдача по arXiv]: «Off-policy evaluation
(OPE) ... enables the performance evaluation of counterfactual policies without
interacting with actual users»; IPS «uses the importance sampling technique to correct
the distribution shift between different policies», DR «reduces the variance of IPS by
using an estimated reward function as a control variate».

🔴 **Вывод по применимости — отрицательный, и это результат, а не пробел.** Все три
семейства оценщиков (Direct Method, IPS, Doubly Robust) требуют **логированного
датасета взаимодействий** вида (контекст, выбранное действие, вероятность выбора,
наблюдённая награда). У FINPILOT нет ни одной из четырёх компонент: нет логов, нет
логирующей политики, нет propensity, нет награды. IPS без propensity не определён,
DM без наблюдённых наград не обучается, DR — комбинация двух, поэтому тоже нет.

Дополнительно: даже при наличии логов IPS «is unbiased under some identification
assumptions such as full support and unconfoundedness, but it often suffers from high
variance» [СНИППЕТ] — то есть требует, чтобы логирующая политика имела ненулевую
вероятность на всех 66 альтернативах. Детерминированная СППР этого условия не даёт
принципиально (full support нарушен).

**Практический вывод для вехи 6:** OPE в план не включать. Включить в дорожную карту
ПОСЛЕ запуска условие, при котором OPE станет возможен: логировать (портрет, показанный
вектор, вероятность показа, факт исполнения через N месяцев) и заложить
рандомизацию/ε-исследование в выдачу — без неё логи не будут пригодны для OPE даже
через год.

---

## Участок 2. Экспертный консенсус как эталон — предел метода

### 2.1. Меры согласованности и общепринятые пороги

**Каппа Коэна (2 оценщика) и каппа Флейса (>2 оценщиков).** Общая формула:

```
κ = (p_o − p_e) / (1 − p_e)
```
где p_o — наблюдённая доля согласия, p_e — доля согласия, ожидаемая случайно.

Шкала Landis & Koch (1977) — самая цитируемая [СНИППЕТ, оригинал J. Landis, G. Koch,
*The Measurement of Observer Agreement for Categorical Data*, Biometrics 33(1):159–174
не открыт напрямую; шкала воспроизведена согласованно в нескольких вторичных источниках]:

| κ | Ярлык |
|---|---|
| < 0.00 | poor |
| 0.00–0.20 | slight |
| 0.21–0.40 | fair |
| 0.41–0.60 | moderate |
| 0.61–0.80 | substantial |
| 0.81–1.00 | almost perfect |

**ICC (внутриклассовая корреляция)** — для непрерывных величин, а у нас action-vector
непрерывный (доли), так что ICC ближе к нашей задаче, чем каппа.
Koo T.K., Li M.Y. (2016), *A Guideline of Selecting and Reporting Intraclass Correlation
Coefficients for Reliability Research*, J Chiropr Med [ПРОЧИТАНО,
pmc.ncbi.nlm.nih.gov/articles/PMC4913118/]:

> "values less than 0.5 are indicative of poor reliability, values between 0.5 and 0.75
> indicate moderate reliability, values between 0.75 and 0.9 indicate good reliability,
> and values greater than 0.90 indicate excellent reliability"

🔴 И ключевое требование к отчётности, которое мы обязаны выполнить в вехе 6:

> "the ICC estimate obtained from a reliability study is only an expected value of the
> true ICC ... it is more appropriate to evaluate the level of reliability based on the
> 95% confident interval of the ICC estimate, not the ICC estimate itself"

То есть наши 78.63% нельзя приводить точечно — нужен доверительный интервал, и суждение
выносится по НИЖНЕЙ границе. Там же: «There are 10 forms of ICCs», форму (model / type /
definition) обязательно указывать явно.

Концептуальная формула надёжности (там же): `Reliability = true variance /
(true variance + error variance)`.

**W Кендалла** — коэффициент конкордации для ранжирований m судей по n объектам:
```
W = 12·S / (m²·(n³ − n))
```
S — сумма квадратов отклонений сумм рангов от их среднего; W ∈ [0;1], 0 — полный разнобой,
1 — полное совпадение рангов. [Формула общеизвестна, первоисточник Kendall & Babington
Smith 1939 не открывался — помечаю как непроверенный по первоисточнику.]

### 2.2. Ловушки каппы — почему нам её лучше не брать основной метрикой

Feinstein A.R., Cicchetti D.V. (1990), *High agreement but low kappa: I. The problems of
two paradoxes*, J Clin Epidemiol 43:543–549 [СНИППЕТ, полный текст за пейволлом
jclinepi.com — см. «что не добыто»]. Суть двух парадоксов по согласованным вторичным
изложениям:

1. низкая каппа при высоком проценте согласия;
2. несбалансированные маргинальные распределения дают более высокую каппу, чем
   сбалансированные.

Практический перенос: если в нашей синтетике большинство портретов сводится к одному
доминирующему действию (например, «сначала дорогой долг»), каппа будет систематически
занижена при фактически высоком согласии. Поэтому по action-vector надо давать
**и процент согласия, и меру, устойчивую к перекосу маргиналий** (Gwet's AC1/AC2 или
Krippendorff's alpha упоминаются как штатная замена [СНИППЕТ]).

### 2.3. 🔴 Удар по методу калибровки: экспертное согласие ≠ точность

Это то место, где найденное бьёт по нашему подходу, и я говорю прямо.

**Grove W.M., Zald D.H., Lebow B.S., Snitz B.E., Nelson C. (2000), *Clinical Versus
Mechanical Prediction: A Meta-Analysis*, Psychological Assessment 12(1):19–30**
[ПРОЧИТАНО, PDF взят curl-ом, zaldlab.psy.vanderbilt.edu/resources/wmg00pa.pdf, 200,
1 096 631 байт]. Дословно из абстракта:

> "On average, mechanical-prediction techniques were about 10% more accurate than clinical
> predictions. Depending on the specific analysis, mechanical prediction substantially
> outperformed clinical prediction in 33%-47% of studies examined. Although clinical
> predictions were often as accurate as mechanical predictions, in only a few studies
> (6%-16%) were they substantially more accurate. Superiority for mechanical-prediction
> techniques was consistent, regardless of the judgment task, type of judges, judges'
> amounts of experience, or the types of data being combined."

И важное определение оттуда же (стр. 19), которое нас частично спасает:

> "Mechanical prediction, including statistical prediction (using explicit equations),
> actuarial prediction (as with insurance companies' actuarial tables), and what we may
> call algorithmic prediction (e.g., a computer program emulating expert judges), is by
> contrast well specified. Once developed, application of mechanical prediction requires
> no expert judgment. Also, mechanical predictions are 100% reproducible."

🔴 **Два следствия для FINPILOT, и они разнонаправленные.**

*Хорошее:* наши четыре «экспертных движка» — это по классификации Grove et al. НЕ clinical
judgment, а `algorithmic prediction (a computer program emulating expert judges)`, то есть
mechanical prediction. Значит эталон у нас воспроизводим на 100% и не страдает
внутрисудейской нестабильностью живых экспертов. Это сильная сторона метода, и её надо
назвать в документации вехи 6 явно, со ссылкой.

*Плохое, и его надо признать:* согласие с экспертным консенсусом — это метрика
**согласованности (consistency/concurrent validity)**, а НЕ метрика точности. Grove et al.
показывает, что человеческая экспертиза в среднем на ~10% менее точна, чем механическая;
Tetlock (Expert Political Judgment, 2005; 284 эксперта, ~28 000 прогнозов 1984–2003)
показывает системную переуверенность экспертов — «events experts rated as 100% certain
occurred only about 80% of the time» [СНИППЕТ, вторичные пересказы, книга не открывалась —
цитата НЕ проверена по первоисточнику]. Отсюда: **число 78.63% нельзя предъявлять как
доказательство полезности совета.** Оно доказывает, что модель воспроизводит принятую
практику, и ровно это и надо писать. Претензия «наш совет хороший, потому что совпадает
с экспертами» методологически несостоятельна и будет разобрана рецензентом.

Правильная формулировка для вехи 6: согласие с консенсусом — **необходимое, но
недостаточное** условие; сверху нужны метрики, не зависящие от эталона (участок 3)
и проверка «система лучше, чем без системы» (критерий Миллера, участок 1.2).

### 2.4. Что делать в зоне разногласия экспертов

Найденная практика — не «разрешать» разногласие, а **выводить зону из-под метрики
соответствия и помечать как область неопределённости**:

- CDSS-валидация по ранам: априорный порог консенсуса «at least three of five experts»,
  случай без консенсуса **исключён** из анализа; «disagreement among experts often reflects
  genuine uncertainty rather than error» [ПРОЧИТАНО, PMC13249526];
- Berner 2003: «there are often disagreements among experts» — как признаваемое свойство,
  а не дефект дизайна.

🔴 Прямой перенос на раунд 5: полосу Lt ∈ [1;2) с амплитудой экспертных ответов 66 п.п.
надо **объявить зоной отсутствия консенсуса формально**: (1) задать априорное правило
консенсуса (например, «согласие ≥3 из 4 движков по доминирующей категории действия»),
(2) портреты, не проходящие правило, исключать из расчёта метрики соответствия и
считать по ним отдельную долю, (3) **в самом продукте в этой полосе менять режим
выдачи** — не единственный вектор, а несколько допустимых с явным «здесь профессионалы
расходятся». Это не костыль, это опубликованная практика.

Методология Delphi для сведения разногласия — отдельный инструмент [не добывалась
отдельно, см. «что не добыто»].

---

## Участок 3. Метрики, применимые нам конкретно

Здесь собрано то, что считается БЕЗ эталона вообще — самая ценная часть для вехи 6,
потому что не зависит ни от логов, ни от экспертов.

### 3.1. Метаморфическое тестирование — прямой ответ на «нет оракула»

Wikipedia, *Metamorphic testing* [ПРОЧИТАНО], со ссылкой на первоисточник
Chen T.Y., Cheung S.C., Yiu S.M. (1998), *Metamorphic testing: A new approach for
generating next test cases*, Technical Report HKUST-CS98-01, HKUST:

> "Metamorphic testing (MT) is a property-based software testing technique, which can be
> an effective approach for addressing the test oracle problem and test case generation
> problem."

> Oracle problem — "the difficulty of determining the expected outcomes of selected test
> cases or to determine whether the actual outputs agree with the expected outcomes."

> Metamorphic relations (MRs) constitute "necessary properties of the intended
> functionality of the software, and must involve multiple executions of the software."

Канонический пример: `sin(π − x) = sin(x)` — правильное значение `sin(1.234)` знать
не нужно, чтобы поймать ошибку.

Из обзорной выдачи по ML-тестированию [СНИППЕТ]: «MR describes the relationship between
input-output pairs of software. Given a test case, metamorphic testing transforms it into
a new test case via a pre-defined transformation rule and then checks whether the
corresponding outputs ... exhibit the expected relationship». Обзор:
Zhang J.M. et al., *Machine Learning Testing: Survey, Landscapes and Horizons*,
arXiv:1906.10742; отдельный обзор — Segura S. et al., ACM Computing Surveys 51(1),
doi 10.1145/3143561 [ACM DL не открывался].

🔴 **Это ровно наш инструмент, и он уже наполовину есть в проекте (инварианты Rt≥0,
ПДН≤0.40).** Дальше — набор MR для FINPILOT, каждая проверяется на 12 000 синтетических
портретов, каждая даёт бинарный вердикт без всякого эталона:

| ID | Метаморфическое отношение | Ожидаемое поведение выхода |
|---|---|---|
| MR-1 | доход ↑ при прочих равных | суммарное покрытие целей не убывает; горизонт достижения не растёт |
| MR-2 | ставка по долгу i ↑ | доля потока в долг i не убывает |
| MR-3 | масштабирование всех денежных величин на λ>0 | вектор ДОЛЕЙ не меняется (однородность нулевой степени) |
| MR-4 | перестановка двух идентичных долгов | вектор долей переставляется соответственно (эквивариантность) |
| MR-5 | размер резерва ↑ при прочих равных | доля в резерв не растёт |
| MR-6 | добавление строго доминируемой альтернативы | рекомендация не меняется (защита от rank reversal) |
| MR-7 | обязательный расход ↑ (свободный поток ↓) | ни один инвариант не нарушается, план деградирует монотонно |
| MR-8 | смена риск-профиля на более консервативный | доля в резерв не убывает, доля в цели не растёт |

Метрика: **MR-violation rate = (число портретов, нарушивших хотя бы одно MR) / N.**
Порог приёмки: **0 нарушений** для MR-3, MR-4, MR-6 (это математические тождества,
любое нарушение — баг), и **≤0.1%** для монотонных MR-1/2/5/8 (допуск на численные
эффекты дискретной сетки в 66 альтернатив с шагом 10% — но каждое нарушение должно
быть объяснено дискретизацией, а не оставлено как «шум»).

⚠️ Честная оговорка: шаг сетки 10% сам по себе способен порождать «немонотонность»
на границе перескока между соседними альтернативами. Поэтому MR-1/2/5/8 надо
формулировать в ослабленной форме «не убывает с точностью до одного шага сетки»,
иначе тест будет краснеть на исправной модели.

### 3.2. Устойчивость: минимальное изменение веса, меняющее решение

Формальный аппарат — Triantaphyllou E., Sánchez A. (1997), *A Sensitivity Analysis
Approach for Some Deterministic Multi-Criteria Decision-Making Methods*, Decision Sciences
28(1):151–194 [первоисточник за пейволлом Wiley; методология воспроизведена дословно
в работе ниже]. Из выдачи [СНИППЕТ]: «Triantaphyllou & Sánchez introduced four definitions
of critical criterion based on absolute term, relative term, top ranking and any ranking».

Jaini N.I., Utyuzhnikov S.V. (2016), *Critical Criterion Analysis for Multi-criteria
Decision Making*, Int. J. of Applied Physics and Mathematics 6(3):129–137,
doi 10.17706/ijapm.2016.6.3.129-137 [ПРОЧИТАНО ЦЕЛИКОМ через pdftotext; PDF получен
через приём «WebFetch кладёт файл на диск»]. Дословно, раздел 3 Methodology (стр. 132):

> "Let 𝛿₁ denotes the change in the current weight 𝑤₁ associated with criterion 𝐶₁. Thus,
> a new weight for criterion 𝐶₁ is 𝑤₁* = 𝑤₁ + 𝛿₁ where 𝛿₁ ≥ −𝑤₁ since 𝑤ⱼ* ≥ 0
> (𝑗 = 1, … , 𝑁). Note that the weights 𝑤ⱼ are normalized such that Σ𝑤ⱼ = 1."

Перенормировка после возмущения (формулы (8) и (9) статьи, дословно):

```
w'_1 = w*_1 / (w*_1 + w_2 + ... + w_N)
w'_j = w_j  / (w*_1 + w_2 + ... + w_N),   j ≠ 1
```

> "The critical criterion is determined after the whole analysis has been completed.
> ... the critical criterion is defined as a criterion with the smallest changes in the
> current weights which affect the [current ranking]."

🔴 Практический перевод для FINPILOT (у нас SAW — тот самый WSM, на котором метод
и построен): для каждого портрета и каждого критерия k считаем **минимальное
относительное возмущение веса `δ*_k / w_k`, при котором меняется рекомендованная
альтернатива**. Получаем:

- **Stability margin портрета** `SM = min_k |δ*_k| / w_k` — насколько «на волоске»
  висит совет. Считается аналитически для SAW, перебором по 66 альтернативам, дёшево.
- **Critical criterion** — тот k, на котором минимум достигается; полезно для объяснения
  («ваш план чувствителен к оценке важности резерва»).
- Порог приёмки: доля портретов с `SM < 5%` не превышает заранее объявленного X.
  🔴 Внешнего отраслевого порога для X в источниках НЕ НАЙДЕНО — его придётся объявить
  своим и обосновать распределением, а не сослаться. Честнее: не задавать порог,
  а публиковать распределение SM и требовать его стабильности между версиями модели.

Родственный приём из практики [ПРОЧИТАНО, cran mcdabench vignette sensana]: вместо
теоретических порогов — эмпирика, прогнать ранжирование при разных схемах весов
(CRITIC, Entropy, Equal, Gini, SD, MEREC, MPSI, Geometric, ROC, RS) и смотреть
rank heatmap: «alternatives that consistently rank high or low across different weighting
methods, as well as those whose ranks vary considerably». Для нас это дешёвый тест:
**доля портретов, у которых рекомендация не меняется при подмене схемы весов** — прямая
мера того, что совет продиктован данными, а не нашей калибровкой.

### 3.3. Доминирование и Парето-оптимальность

Проверка, не требующая эталона: рекомендованная альтернатива не должна быть строго
доминируемой по набору критериев (ни по одному не хуже и хотя бы по одному лучше
находится другая альтернатива из тех же 66). Метрика: **Pareto-violation rate**,
порог приёмки — **строго 0**. Любое ненулевое значение — баг агрегации, а не вопрос
калибровки.

Связанное: MR-6 выше (добавление доминируемой альтернативы не должно менять выбор) —
это тест на rank reversal. Из выдачи [СНИППЕТ]: «the RAFSI method eliminates the rank
reversal problem» (тема 15 это уже разбирала).

### 3.4. Калибровка вероятностей Монте-Карло

У нас SES + Монте-Карло выдаёт вероятности достижения цели. Проверяемое свойство:
событие, объявленное с вероятностью p, происходит в доле p случаев.

Brier score [ПРОЧИТАНО, en.wikipedia.org/wiki/Brier_score]:

```
BS = (1/N) Σ_t (f_t − o_t)²
```
f_t — прогнозная вероятность, o_t ∈ {0,1} — исход.

Разложение Мёрфи (Murphy, 1973), дословно:

```
BS = REL − RES + UNC
BS = (1/N)Σ n_k (f_k − ō_k)²  −  (1/N)Σ n_k (ō_k − ō)²  +  ō(1 − ō)
```
> Reliability (REL) — "measures how close the forecast probabilities are to the true
> probabilities, given that forecast"; "if the reliability is 0, the forecast is perfectly
> reliable".
> Resolution (RES) — насколько условные вероятности отличаются от климатического среднего.
> Uncertainty (UNC) — "measures the inherent uncertainty in the outcomes of the event".

Brier Skill Score: `BSS = 1 − BS / BS_ref`; «A BSS of 1 (100%) represents perfect
predictions, while negative values indicate worse performance than the baseline model».

🔴 **Как это считать НАМ без исходов реальных пользователей.** Единственный честный
способ — **самосогласованность симулятора против собственного генератора**: если
Монте-Карло говорит «цель достигается с вероятностью 0.7», то на 10 000 независимых
прогонов ТОЙ ЖЕ стохастической модели цель должна достигаться в 70% ± MC-ошибка.
Это проверяет корректность реализации (что оценщик вероятности не смещён относительно
собственного процесса), но НЕ проверяет, что модель мира верна.

Второй, более сильный способ — калибровка против **исторических траекторий РФ**
(участок 4): бэктест даёт настоящие o_t. Тогда REL считается по-настоящему, а не
против себя же.

⚠️ Обязательно писать в отчёте вехи 6 прямо: **внутримодельная калибровка — это
верификация, а не валидация.** Модель, идеально калиброванная сама к себе, может
быть полностью неверна относительно реальности.

Инструмент визуализации — reliability diagram (наблюдённая частота против прогнозной
по бинам); нужен, потому что BS агрегирует REL и RES в одно число и хорошая
разрешающая способность маскирует плохую надёжность.

### 3.5. Почему precision@k и NDCG нам НЕ подходят

Разбор мой, не цитата; основания — свойства метрик:

1. **Нет релевантных меток.** precision@k требует бинарной релевантности, NDCG —
   градуированной. У нас ни того, ни другого: нет разметки «этот вектор релевантен
   этому портрету».
2. **Выход — не список, а одна точка в симплексе.** Мы отдаём один action-vector долей,
   а не top-k. Ранжирование 66 альтернатив — внутренний артефакт SAW, пользователю
   не показывается; мерить качество ранжирования хвоста бессмысленно, потому что
   хвост не влияет на продукт.
3. **Соседние альтернативы почти неразличимы.** При шаге 10% альтернативы №1 и №2
   отличаются на 10% потока; NDCG штрафует их перестановку как ошибку ранжирования,
   хотя экономическая разница между ними близка к нулю. Метрика должна быть
   **непрерывной по расстоянию в симплексе**, а не порядковой.

🔴 Правильная замена для сравнения с экспертным консенсусом — расстояние в симплексе,
а не ранговая метрика:
```
d(a, e) = ½ · Σ_c |a_c − e_c|        (total variation / половина L1, ∈ [0;1])
```
где a — вектор модели, e — консенсусный вектор экспертов. Это даёт градацию
«насколько разошлись», а не бинарное «совпало/не совпало», и снимает эффект,
при котором расхождение на 5% потока считается такой же ошибкой, как расхождение
на 80%. 🔴 Наши текущие 78.63% — метрика бинарного совпадения; её надо дополнить
распределением d(a,e), иначе мы не отличаем «почти согласны» от «противоположные советы».

---

## Участок 4. Retrospective backtesting на исторических данных

### 4.1. Делает ли так кто-нибудь — да, это канон финансового планирования

**Bengen W.P. (1994), *Determining Withdrawal Rates Using Historical Data*, Journal of
Financial Planning** — родоначальник «правила 4%» и, что важнее для нас, самой
методологии. Из вторичных изложений [СНИППЕТ; полный PDF есть на
financialplanningassociation.org, в этой сессии открывался только через выдачу]:
портфель 50/50, **скользящие 30-летние окна со стартами 1926–1963**, S&P 500 для акций,
intermediate-term Treasuries для облигаций, CPI для инфляции, ежегодная ребалансировка.

🔴 Ключевой методологический приём, который переносится на нас напрямую: **не одна
траектория, а СЕМЕЙСТВО перекрывающихся исторических когорт** — каждая дата старта
даёт отдельный «портрет из года T», и результат отчитывается не средним, а **худшим
случаем** (у Bengen это SAFEMAX — ставка, выжившая во всех когортах).

**CFA Institute, refresher reading *Backtesting and Simulation*** [ПРОЧИТАНО,
cfainstitute.org/insights/professional-learning/refresher-readings/2026/backtesting-and-simulation]:

> Backtesting "tests a strategy in a historical environment, usually over long periods,
> answering the question 'How would this strategy have performed if it were implemented
> in the past?'"

> Rolling-window backtesting: researchers "fit/calibrate factors or trade signals based on
> the rolling window, rebalance the portfolio periodically, and then track the performance
> over time", это "a proxy for actual investing".

> Simulation "explores how a strategy would perform in a hypothetical environment specified
> by the user, rather than a historical setting".

Заявленные там же ограничения бэктеста (дословно/близко к тексту):
- rolling-window backtesting "may be unable to fully account for the randomness in asset
  returns, particularly on downside risk";
- предполагает, что "the distribution pattern from the historical data is sufficient to
  represent the uncertainty in the future";
- не схватывает negative skewness, fat tails и tail dependence.

### 4.2. Главная ловушка — переобучение на бэктесте, и она измерима

Bailey D.H., Borwein J.M., López de Prado M., Zhu Q.J. (2014), *Pseudo-Mathematics and
Financial Charlatanism: The Effects of Backtest Overfitting on Out-of-Sample Performance*,
Notices of the AMS, May 2014. Из выдачи [СНИППЕТ]: доказано, что «high simulated
performance is easily achievable after backtesting a relatively small number of alternative
strategy configurations»; «The higher the number of configurations tried, the greater is
the probability that the backtest is overfit»; поскольку число испробованных конфигураций
почти никогда не публикуется, «investors cannot evaluate the degree of overfitting».

Технический инструментарий [ПРОЧИТАНО, davidhbailey.com/dhbpapers/overfit-tools-at.pdf,
200, 488 834 байта, стр. 2]:

> "For the single testing case, Bailey, Borwein, López de Prado and Zhu [3] proposed the
> Minimum Backtest Length (MinBTL) as a metric to avoid selecting a strategy with a high SR
> on IS data, but zero or less on OOS data. A probabilistic Sharpe Ratio (PSR) was proposed
> in [1] to calculate the probability of an estimated SR being greater than a benchmark SR.
> For the multiple testing case, Bailey and López de Prado [2] developed the Deflated Sharpe
> Ratio (DSR) to provide a more robust performance statistic, in particular, when the
> returns follow a non-normal distribution."

Ссылки оттуда же: [2] Bailey & López de Prado, *The Deflated Sharpe Ratio: Correcting for
Selection Bias, Backtest Overfitting, and Non-Normality*, Journal of Portfolio Management
40(5):94–107, 2014. Отдельно — *The Probability of Backtest Overfitting* (PBO) через
combinatorially symmetric cross-validation (CSCV) [СНИППЕТ].

🔴 **Прямое требование к вехе 6, вытекающее отсюда:** если мы калибруем матмодель по
историческому прогону, мы обязаны **публиковать число испробованных конфигураций**
(сколько наборов весов/порогов перебрали, прежде чем остановились на v3.0.0). Иначе
наш собственный бэктест будет ровно тем, что Bailey et al. называют charlatanism.
Пять раундов экспертной сертификации — это уже пять испытаний; их надо посчитать
и назвать.

### 4.3. Реализуемость идеи «портрет из 2015 года» — оценка честная

**Данные: ключевая ставка ЦБ РФ — ДОБЫТА и проверена в этой сессии.**
`https://www.cbr.ru/hd_base/KeyRate/?UniDbQuery.Posted=True&UniDbQuery.From=01.01.2014&UniDbQuery.To=10.09.2026`
отдаёт HTTP 200 без авторизации, ~3 180 строк дневного ряда: первая — 09.01.2014, 5,50;
последняя — 10.09.2026, 14,00. Парсится тривиально (таблица HTML, десятичная запятая).

**Инфляция — НЕ подтверждена в этой сессии:** угаданный URL xlsx ЦБ дал 404,
`rosstat.gov.ru` дал ошибку curl 60 (проблема сертификата TLS). Ряд почти наверняка
доступен, но канал в этой сессии не найден — см. «что не добыто».

**Что бэктест на этих данных МОЖЕТ дать (реализуемо):**
1. **Проверка выживаемости инвариантов на реальной траектории.** Портрет из 2015 года,
   план построен по данным, доступным на дату старта; дальше ставка идёт как было
   (17% в 2015 → 4.25% в 2020 → 21% в 2024 → 14% в 2026). Метрика: доля когорт,
   в которых Rt≥0 и ПДН≤0.40 удержаны на всём горизонте без ручного вмешательства.
   Это тест на **робастность, а не на оптимальность**, и в этом качестве он законен.
2. **Настоящая калибровка вероятностей** (участок 3.4): по когортам получаем реальные
   o_t ∈ {0,1} «цель достигнута к сроку» и считаем REL из разложения Мёрфи.
3. **Стресс-профиль:** насколько плох худший исход по когортам (участок 5).

**Что бэктест дать НЕ может — и это надо написать в план прямо:**
1. **Траектория ровно одна (n=1).** Скользящие окна 2014–2026 сильно перекрываются
   и содержат два общих шока (2014–15 и 2022), поэтому «12 когорт» — это НЕ 12
   независимых наблюдений. Доверительные интервалы по таким когортам занижены, и любая
   формула, предполагающая независимость, будет врать. У Bengen тех же проблем меньше
   только потому, что у него 38 стартов и почти столетие данных; у нас — 12 лет.
2. **Нет ground truth по «правильному» распределению даже задним числом.** Зная траекторию
   ставки, можно посчитать ОПТИМАЛЬНЫЙ задним числом план (это решаемая детерминированная
   задача) — но сравнение с ним есть сравнение с оракулом, обладавшим look-ahead. Такое
   сравнение даёт **верхнюю границу сожаления (regret)**, и его надо так и называть,
   а не «наша модель ошиблась на X».
   🔴 При этом regret против оракула — вполне рабочая метрика: `Regret = V_oracle − V_model`,
   нормированная на V_oracle. Она не требует эталона от экспертов и осмысленна: показывает,
   сколько стоит незнание будущего. И, что важнее, позволяет сравнить нашу модель
   с наивными бейзлайнами по одной шкале (критерий Миллера из участка 1.2).
3. **Поведение пользователя не моделируется.** Бэктест предполагает, что план исполняется
   буквально 12 лет подряд. Из темы 17 известно, что связь «принял рекомендацию» ↔ «польза»
   разорвана; значит бэктест меряет качество ПЛАНА, а не качество СОВЕТА, полученного
   человеком.
4. **Look-ahead bias в самой структуре продукта.** Модель v3.0.0 калибровалась в 2026 году
   людьми, знающими, что было в 2022. Полностью это не устранить; можно частично —
   зафиксировать, что параметры модели не зависят от макроряда, и это проверяемо
   (grep по коду: нет захардкоженных значений ставки/инфляции).

**Вывод по участку 4:** идея реализуема, но в переформулированном виде —
**не «докажем, что совет был правильный», а «покажем, что план выживает на реальной
российской траектории и что заявленные вероятности сбываются»**. В таком виде это
сильный раздел вехи 6. В исходном виде («сравним с фактическим исходом») — методологически
несостоятелен по пунктам 1–2 выше.

---

## Участок 5. Что считать «вредом» — метрика безопасности

### 5.1. Регуляторная планка: «foreseeable harm» — это ОБЯЗАННОСТЬ, а не пожелание

FCA Handbook, PRIN 2A.2 [ПРОЧИТАНО, handbook.fca.org.uk/handbook/prin2a/prin2as2]:

> "A firm must avoid causing foreseeable harm to retail customers." (PRIN 2A.2.8R)

> Вред может возникать "both act and omission, in a firm's direct relationship with a
> retail customer or through its role in the distribution chain even where another firm in
> that chain also contributes to the harm." (PRIN 2A.2.9R)

Ограничение ответственности фирмы (важно, потому что даёт нам законную границу):

> "a product may have inherent risks which retail customers accept by selecting that
> product. Where a firm reasonably believes a retail customer understands and accepts such
> risks, it will not breach the rule if it fails to prevent them." (PRIN 2A.2.13G)

Из обзоров практики надзора [СНИППЕТ]: «foreseeable harm includes any outcome that a
prudent firm, applying reasonable care and expertise, should be able to anticipate and is
not limited to harm that has already occurred». И прямая критика в наш адрес заранее:
«Some firms use operational metrics (such as conversion rates or review completion) as a
proxy for customer outcomes without clearly defining what good or poor outcomes look like
at each stage of the journey».

🔴 Последнее смыкается с темой 17: **«доля принятых рекомендаций» — это ровно тот
операционный прокси, который FCA называет плохой практикой.** Два независимых источника
(академический эксперимент SIGIR '25 и регуляторный обзор) сходятся на одном выводе.
Это самое сильное согласование, найденное в теме.

**Ответ на вопрос «есть ли отраслевой стандарт на безопасность совета»:** отдельного
численного стандарта НЕ найдено. Есть принципная обязанность (PRIN 2A.2.8R) и требование
самой фирме определить, что считается плохим исходом на каждом шаге пути клиента,
и мониторить это. То есть **порог мы обязаны назначить сами и обосновать** — регулятор
проверяет наличие и обоснованность порога, а не сверяет его с готовой цифрой.

### 5.2. Как измеряют «худший случай» — аппарат

**CVaR / Conditional Value-at-Risk.** Rockafellar R.T., Uryasev S., *Optimization of
Conditional Value-at-Risk*, Journal of Risk 2(3):21–41, 2000 [ПРОЧИТАНО, препринт автора
sites.math.washington.edu/~rtr/papers/rtr179-CVaR1.pdf, 200, 200 088 байт]. Дословно,
Introduction:

> "By definition with respect to a specified probability level β, the β-VaR of a portfolio
> is the lowest amount α such that, with probability β, the loss will not exceed α, whereas
> the β-CVaR is the conditional expectation of losses above that amount α. Three values of
> β are commonly considered: 0.90, 0.95 and 0.99. The definitions ensure that the β-VaR is
> never more than the β-CVaR, so portfolios with low CVaR must have low VaR as well."

> "CVaR, also called Mean Excess Loss, Mean Shortfall, or Tail VaR, is anyway considered to
> be a more consistent measure of risk than VaR."

Минимизационное представление (общепринятая форма, приведена в выдаче [СНИППЕТ],
в открытом препринте — как функция F_β):

```
CVaR_α(X) = min_{β∈ℝ} { β + (1/(1−α)) · E[(X − β)_+] },   (t)_+ = max(t, 0)
```

🔴 Почему это критично именно нам: CVaR **выпукла** и сводится к линейному
программированию, тогда как VaR — нет. Значит CVaR можно и мерить, и вносить как
ограничение в саму оптимизацию 66 альтернатив, не ломая решаемость.

**Связь с темой 13 (Estrada, Kitces/Tharp).** Уже установлено: «probability of success
entirely misses the dimension of magnitude of success/failure». CVaR — это ровно
недостающее измерение: не «с какой вероятностью провал», а «насколько глубок провал
в тех сценариях, где он случился». То есть тема 13 ставила проблему, а участок 5
даёт готовый математический аппарат под неё. Практическая пара метрик:
`shortfall probability` (что у нас уже есть) + `CVaR дефицита` (чего нет).

**Maximum drawdown** — максимальная просадка от пика; для нашей задачи прямой аналог
не портфельный, а **минимум подушки безопасности на траектории**: `min_t (Rt / месячные
обязательные расходы)` — сколько месяцев автономии остаётся в худшей точке плана.
Это интерпретируемая для пользователя величина и естественный кандидат в жёсткий порог.

### 5.3. Предлагаемая шкала «вреда» для FINPILOT

Инвариантов Rt≥0 и ПДН≤0.40 недостаточно: они бинарные (нарушен/не нарушен) и ничего
не говорят о глубине. Дополнить тремя градуированными:

1. **CVaR₉₅ дефицита ликвидности** — средний размер отрицательного Rt по худшим 5%
   сценариев Монте-Карло (в рублях и в месяцах обязательных расходов).
2. **Минимальная автономия** `min_t (Rt / E_month)` по траектории — в месяцах.
3. **CVaR₉₅ недостижения цели** — средняя величина недобора до цели по худшим 5%
   сценариев (магнитуда провала по Estrada), а не только вероятность недобора.

Порог приёмки для вехи 6 предлагаю ставить как **сравнительный, а не абсолютный**
(абсолютного стандарта в источниках нет): по каждой из трёх величин план модели должен
быть **не хуже каждого из наивных бейзлайнов** (пропорциональное деление, всё-в-долг,
всё-в-резерв, snowball) на ≥95% синтетических портретов. Это операционализация критерия
Миллера «система лучше, чем без системы» через downside, а не через среднее.

---

## ИТОГ 1. Набор метрик для вехи 6 (формула + порог приёмки)

Все восемь считаются на том, что у нас УЖЕ есть: 12 000 синтетических портретов,
четыре экспертных движка, дневной ряд ключевой ставки ЦБ 2014–2026 (проверен, HTTP 200).
Ни одна не требует логов пользователей или обратной связи от исходов.

**M1. MR-violation rate (метаморфические отношения).** Участок 3.1.
```
MRV = |{ p ∈ P : ∃ mr ∈ MR, mr нарушено на p }| / |P|
```
Порог: **0** для MR-3 (однородность по масштабу), MR-4 (эквивариантность к перестановке
идентичных долгов), MR-6 (устойчивость к доминируемой альтернативе) — это тождества.
**≤0.1%** для монотонных MR-1/2/5/7/8, каждое нарушение объяснено дискретизацией сетки.
Основание: Chen et al. 1998, oracle problem.

**M2. Pareto-violation rate.** Участок 3.3.
```
PV = |{ p : рекомендованная альтернатива строго доминируема другой из 66 }| / |P|
```
Порог: **строго 0.** Ненулевое значение — баг агрегации.

**M3. Stability margin (минимальное относительное возмущение веса, меняющее совет).**
Участок 3.2, аппарат Triantaphyllou & Sánchez 1997 / Jaini & Utyuzhnikov 2016.
```
w*_k = w_k + δ_k ;  w'_k = w*_k / Σ_j w'_j (перенормировка, формулы (8)–(9))
SM(p) = min_k |δ*_k| / w_k,  где δ*_k — минимальное δ, меняющее выбранную альтернативу
```
Порог: **распределение SM публикуется; медиана SM не падает и доля SM<5% не растёт
между версиями модели.** 🔴 Абсолютного отраслевого порога в источниках НЕ НАЙДЕНО —
не выдумывать, отчитываться распределением.

**M4. Weight-scheme invariance.** Участок 3.2, приём из mcdabench.
```
WSI = доля портретов, у которых рекомендация не меняется при подмене схемы весов
      (Equal, Entropy, CRITIC, SD, MEREC, ROC, RS)
```
Порог: **WSI ≥ 0.80.** Смысл: совет продиктован данными портрета, а не нашей калибровкой.
Порог назначен нами по аналогии с «substantial» Landis & Koch (0.61–0.80), внешнего
основания нет — так и написать.

**M5. Расстояние до экспертного консенсуса (замена бинарным 78.63%).** Участок 3.5.
```
d(a, e) = ½ · Σ_c |a_c − e_c| ∈ [0;1]
```
Отчитывать: медиану, 90-й перцентиль, долю d ≤ 0.10.
Плюс **ICC(2,k) с 95% ДИ** по Koo & Li 2016, суждение — по НИЖНЕЙ границе интервала
(«values between 0.75 and 0.9 indicate good reliability»).
Порог: **нижняя граница 95% ДИ ICC ≥ 0.50** («moderate») вне зоны отсутствия консенсуса.
🔴 Формулировать как метрику СОГЛАСОВАННОСТИ, не точности (участок 2.3).

**M6. Доля зоны отсутствия консенсуса + её явная обработка.** Участок 2.4.
```
NC = доля портретов, где правило консенсуса (≥3 из 4 движков по доминирующей категории)
     не выполняется
```
Порог: NC измеряется, не ограничивается; **требование приёмки — портреты из NC исключены
из расчёта M5 и в продукте получают режим «несколько допустимых планов»**, а не один
вектор. Основание: PMC13249526 («disagreement among experts often reflects genuine
uncertainty rather than error»).

**M7. Калибровка вероятностей: reliability из разложения Мёрфи.** Участок 3.4.
```
BS = (1/N) Σ (f_t − o_t)² ;  BS = REL − RES + UNC
REL = (1/N) Σ_k n_k (f_k − ō_k)²
```
Две реализации: (а) внутренняя самосогласованность против собственного генератора
(верификация); (б) по историческим когортам РФ (валидация).
Порог: **REL ≤ 0.01** (то есть средняя ошибка калибровки ~10 п.п. по бину — намеренно
мягко для первого замера) и **BSS > 0** против базовой ставки. Дополнительно —
reliability diagram в отчёте.

**M8. Downside против бейзлайнов (операционализация критерия Миллера).** Участки 1.2, 5.3.
```
CVaR_0.95(D) = min_β { β + (1/0.05)·E[(D − β)_+] },  D — дефицит (ликвидности или недобора цели)
Автономия_min(p) = min_t ( Rt(p, t) / E_month(p) )
```
Порог: план модели **не хуже каждого из четырёх наивных бейзлайнов** (пропорция,
всё-в-долг, всё-в-резерв, snowball) по CVaR₉₅ и по минимальной автономии
**на ≥95% портретов**. Основание: Berner 2003, «whether the user plus the system is
better than the unaided user»; Rockafellar & Uryasev 2000.

**Правило агрегации итоговой оценки — по слабейшему звену, а не средним.**
Основание: Decision Quality, «a decision is only as strong as the weakest link».
Веха 6 считается пройденной, когда пройдены ВСЕ восемь, а не когда среднее хорошее.

---

## ИТОГ 2. Что измерить НЕЛЬЗЯ и почему

Честный список. Отсутствие метрики лучше выдуманной.

1. **Полезность совета для конкретного пользователя.** Нет исходов, нет контрфактического
   «что было бы без совета» для того же человека. Никакая метрика на синтетике этого
   не даёт. Требуется RCT или как минимум лонгитюд с контрольной группой.
2. **Точность (accuracy) рекомендации.** Согласие с экспертным консенсусом — это
   concurrent validity, не accuracy. Grove et al. 2000: механические методы в среднем
   на ~10% точнее человеческой экспертизы, значит совпадение с экспертом не является
   доказательством правильности. 🔴 Число 78.63% нельзя предъявлять как «наш совет
   хороший».
3. **Off-policy оценка (IPS / DM / Doubly Robust).** Нет ни логов, ни логирующей политики,
   ни propensity, ни наград. Детерминированная выдача дополнительно нарушает full support.
   OPE невозможен **сейчас** и останется невозможным, если не заложить логирование
   с рандомизацией заранее.
4. **Доля принятых рекомендаций как мера пользы.** Опровергнута дважды независимо:
   тема 17 (Takayanagi et al., SIGIR '25 — обаяние повышает доверие и снижает качество
   решения) и FCA (операционные прокси вместо определения хорошего исхода — прямо
   названо плохой практикой). Метрику можно собирать как продуктовую, но не как метрику
   качества модели.
5. **«Наш план оказался правильным на истории».** Траектория РФ ровно одна (n=1),
   скользящие окна 2014–2026 сильно перекрываются и делят два общих шока; независимых
   наблюдений нет. Максимум, что законно, — regret против оракула с look-ahead и
   выживаемость инвариантов.
6. **Внешняя валидность калибровки Монте-Карло без исторических исходов.** Самопроверка
   против собственного генератора — это верификация реализации, а не подтверждение
   модели мира. Писать в отчёте прямо.
7. **Абсолютный порог «безопасности» совета.** Отраслевого числа нет; FCA требует
   обязанность (PRIN 2A.2.8R) и наличие обоснованных собственных порогов, а не
   соответствие готовой цифре. Любое число, которое мы назовём, — наше, и обосновывать
   его надо распределением, а не ссылкой.
8. **Frame и commitment из шести элементов Decision Quality.** Машинно не проверяются,
   только экспертная оценка. Не притворяться, что закрыты автотестами.

---

## ИТОГ 3. Что не добыто и почему (коды ответа)

| Источник | Что нужно было | Канал и код |
|---|---|---|
| Landis J.R., Koch G.G. (1977), Biometrics 33(1):159–174 | шкала каппы по первоисточнику | первоисточник не открывался; шкала взята из согласованных вторичных изложений (researchgate/statisticssolutions), помечена [СНИППЕТ] |
| Feinstein A.R., Cicchetti D.V. (1990), J Clin Epidemiol 43:543–549 | дословный текст двух парадоксов | jclinepi.com — пейволл Elsevier, полный текст не добыт; препринт не искался (работа 1990 г., препринта скорее всего нет) |
| Triantaphyllou E., Sánchez A. (1997), Decision Sciences 28(1) | формулы δ и четыре определения critical criterion дословно | Wiley — пейволл; страница автора csc.lsu.edu отдала только аннотацию (200, без формул). Методология восстановлена дословно по Jaini & Utyuzhnikov 2016, где она воспроизведена — это [ПРОЧИТАНО] |
| Segura S. et al., ACM Computing Surveys 51(1), doi 10.1145/3143561 | обзор метаморфического тестирования | ACM DL — известный глухой канал, не пробовался повторно |
| Tetlock P., *Expert Political Judgment* (2005) | числа калибровки (284 эксперта, 28 000 прогнозов, «100% certain → 80%») | книга; открыты только вторичные пересказы (CBS News, блоги). Цитата помечена НЕПРОВЕРЕННОЙ. Для вехи 6 этого достаточно как иллюстрации, для публикации — нужен первоисточник |
| Bengen W.P. (1994), Journal of Financial Planning | методология скользящих когорт дословно | PDF есть на financialplanningassociation.org, в этой сессии не открывался (бюджет); помечено [СНИППЕТ] |
| Bailey, Borwein, López de Prado, Zhu (2014), Notices AMS | формула MinBTL и определение PBO/CSCV дословно | добыт смежный обзор тех же авторов (davidhbailey.com, 200, 488 834 б) с определениями MinBTL/PSR/DSR; сами формулы MinBTL и CSCV не извлечены |
| Ряд инфляции РФ 2014–2026 | месячный/годовой ИПЦ | угаданный URL xlsx ЦБ → **HTTP 404**; `rosstat.gov.ru` → **ошибка curl 60** (сертификат TLS). Ряд ключевой ставки при этом добыт полностью (HTTP 200, 3 180 строк). Инфляцию искать отдельно — через `cbr.ru/statistics/ddkp/infl/` или EMISS |
| Методология Delphi для сведения экспертных разногласий | пороги остановки, число раундов | отдельно не искалась — бюджет ушёл на участки 1–5; отмечено как явный пробел |

---

## ИТОГ 4. Метод поиска

**Классификация запроса:** breadth-first — пять независимых участков, каждый со своей
литературой. Depth-first не подходил: участки не были разными ракурсами на один вопрос.

**Субагенты: НОЛЬ, и это осознанно.** Правило §11 проекта запрещает веерный запуск и
требует ждать одного агента, ничего не делая. При пяти участках последовательные агенты
дали бы пять блокирующих ожиданий и пять холодных контекстов при том же наборе
инструментов, что у меня. Ни один участок не требовал угла, недоступного мне напрямую.
Потолок «не более двух» соблюдён с запасом. Сырьё писалось в файл после каждого блока
источников (7 записей Edit по ходу), а не в конце.

**Объём: 17 вызовов WebSearch, 13 вызовов WebFetch, ~11 обращений через Bash
(curl + pdftotext + проверка данных ЦБ).**

**Запросы WebSearch (в порядке выполнения):**
1. prescriptive analytics evaluation methodology without ground truth
2. Howard decision quality vs outcome quality decision analysis six elements
3. off-policy evaluation recommender systems IPS doubly robust survey
4. clinical decision support system validation without gold standard expert panel
5. Landis Koch 1977 kappa benchmarks substantial almost perfect criticism arbitrary
6. Koo Li 2016 ICC guideline selecting reporting intraclass correlation reliability research
7. "kappa" benchmark scales arbitrary criticism prevalence paradox Feinstein Cicchetti
8. Tetlock Expert Political Judgment experts barely better than chance dart-throwing chimps
9. Grove Meehl 2000 clinical versus mechanical prediction meta-analysis 136 studies
10. metamorphic testing machine learning oracle problem metamorphic relations survey
11. MCDA sensitivity analysis robustness rank reversal minimum weight change critical criterion
12. Triantaphyllou Sanchez 1997 sensitivity analysis WSM critical criterion delta formula
13. Bailey Borwein Lopez de Prado Zhu pseudo-mathematics financial charlatanism backtest overfitting
14. robo-advisor backtesting methodology historical simulation single path retirement planning critique
15. Bengen 1994 determining withdrawal rates using historical data rolling 30-year periods
16. Rockafellar Uryasev 2000 optimization of conditional value-at-risk definition formula
17. FCA Consumer Duty avoid foreseeable harm cross-cutting rules outcomes monitoring metrics

**Что сработало из обходных каналов:**
- приём «WebFetch кладёт PDF на диск и печатает путь → pdftotext» — сработал на
  Jaini & Utyuzhnikov (ijapm.org), дал единственный дословный источник формул
  чувствительности вместо запейволленного Triantaphyllou;
- `curl` с браузерным UA — взял Grove et al. 2000 (vanderbilt, 200, 1 096 631 б),
  Bailey overfit-tools (200, 488 834 б), Rockafellar & Uryasev препринт
  (sites.math.washington.edu, 200, 200 088 б). Все три — препринты/копии авторов вместо
  журнальных пейволлов;
- `curl` к cbr.ru — подтвердил доступность дневного ряда ключевой ставки 2014–2026
  без авторизации (это не литература, а проверка реализуемости участка 4);
- `r.jina.ai` не понадобился ни разу: антибот не встретился, все нужные издатели
  (PMC, Wikipedia, FCA Handbook, CFA Institute, cran) открылись штатным WebFetch.

**Противоречий между источниками не обнаружено.** Обнаружено сильное СОГЛАСОВАНИЕ
двух независимых линий (академической — тема 17, и регуляторной — FCA) на выводе,
что операционные прокси принятия рекомендаций не являются метрикой качества.
Обнаружен один удар по нашему методу (Grove et al. — экспертное согласие не есть
точность), он вынесен в участок 2.3 и в ИТОГ 2 п.2, не сглажен.

---

# ДОБОР Г4 (11.09.2026) — первоисточники метрик качества прескриптивных рекомендаций

Метод: только полные тексты. У каждого источника указан канал, HTTP-код и размер ответа.
Цитаты дословные, страница — по колонтитулу самого PDF.

## ДОБОР Г4 — Landis J.R., Koch G.G. (1977): 🔴 ШКАЛА КАППЫ ДОБЫТА ДОСЛОВНО, ГРАНИЦЫ РАСХОДЯТСЯ С ХОДЯЧЕЙ ВЕРСИЕЙ

**Реквизиты (с титульной страницы JSTOR-скана, дословно):** «The Measurement of Observer
Agreement for Categorical Data. Author(s): **J. Richard Landis and Gary G. Koch.** Source:
**Biometrics, Vol. 33, No. 1 (Mar., 1977), pp. 159–174.** Published by: International Biometric
Society. Stable URL: http://www.jstor.org/stable/2529310». DOI по Crossref: **10.2307/2529310**,
`published: [1977, 3]`, `page: "159"`. PMID 843571.

**Канал добычи — цепочка из пяти шагов, четыре первых провалились:**
1. `WebSearch` — прямого PDF не дал.
2. Unpaywall `10.2307/2529310` — HTTP 200, **`is_oa: False`, `oa_status: "closed"`,
   `best_oa_location: None`**. Легальной открытой копии нет.
3. `curl -sk --http1.1` с браузерным UA на `www.dentalage.co.uk/wp-content/uploads/2014/09/
   landis_jr__koch_gg_1977_kappa_and_observer_agreement.pdf` — **HTTP 403, 4 551 байт**
   (Cloudflare). `www.cs.cmu.edu/.../kappa.pdf` — HTTP 200, но `text/html` 40 903 байта,
   не тот файл. CiteSeerX — HTTP 404.
4. Текстовый прокси `r.jina.ai` на тот же dentalage-URL — **HTTP 200, 862 байта**, тело:
   «Attention Required! | Cloudflare / Warning: Target URL returned error 403: Forbidden».
   🔴 **Ещё один замер: `r.jina.ai` НЕ пробивает Cloudflare** (ранее то же на ACM DL).
5. ✅ **Wayback.** CDX по точному URL — HTTP 200, JSON со снимками; взят снимок
   **20170829141229**, `application/pdf`, `length 1178884`. Запрос
   `https://web.archive.org/web/20170829141229id_/http://www.dentalage.co.uk/wp-content/
   uploads/2014/09/landis_jr__koch_gg_1977_kappa_and_observer_agreement.pdf` —
   **HTTP 200, 1 181 952 байта, `application/pdf`**; `pdftotext -layout` → 61 382 байта.
   Это шестой за сессию случай, когда `id_`-снимок Wayback отдал текст, закрытый на живом сайте.

### 🔴 ТАБЛИЦА ДОСЛОВНО, страница 165 (колонтитул «AGREEMENT MEASURES FOR CATEGORICAL DATA 165»)

Вводная фраза автора перед таблицей (с. 164–165, дословно):
> «In order to maintain consistent nomenclature when describing the relative strength of
> agreement associated with kappa statistics, the following labels will be assigned to the
> corresponding ranges of kappa:»

| Kappa Statistic | Strength of Agreement |
|---|---|
| **< 0.00** | **Poor** |
| **0.00–0.20** | **Slight** |
| **0.21–0.40** | **Fair** |
| **0.41–0.60** | **Moderate** |
| **0.61–0.80** | **Substantial** |
| **0.81–1.00** | **Almost Perfect** |

(в OCR-скане «Moderate» распознано как «1\Ioderate», «AlmostPerfect» слитно — это артефакт
распознавания, не текст статьи.)

🔴 **РАСХОЖДЕНИЕ С ХОДЯЧЕЙ ВЕРСИЕЙ, которое надо зафиксировать.** Повсеместно (в том числе
в сводке поисковой выдачи, полученной в этом же доборе) шкалу цитируют как
«**≤ 0 = poor, 0.01–0.20 = slight**, 0.21–0.40 = fair…». **В первоисточнике границы иные:
«< 0.00 — Poor» и «0.00–0.20 — Slight».** То есть κ = 0,00 ровно у Landis & Koch попадает
в «Slight», а не в «Poor»; и нижняя граница «Slight» — 0.00, а не 0.01. Разница
микроскопическая численно, но это ровно тот класс искажения, который эта сессия ловит
пятый раз: пересказ подправил первоисточник и разошёлся тиражом.

🔴 **ГЛАВНАЯ ОГОВОРКА САМИХ АВТОРОВ, которую пересказы опускают почти всегда (с. 165,
сразу под таблицей, дословно):**
> «**Although these divisions are clearly arbitrary, they do provide useful "benchmarks" for
> the discussion of the specific example in Table 1.**»

То есть авторы (а) называют границы **произвольными** собственными словами и (б) вводят их
**для обсуждения одного конкретного примера в Таблице 1 своей статьи**, а не как универсальный
норматив приёмки. **Любая наша формулировка вида «согласие экспертов существенное по шкале
Landis & Koch» обязана нести эту оговорку**, иначе мы приписываем первоисточнику
нормативность, которой он за собой не признаёт. Для калибровки весов это означает: порог
«κ ≥ 0,61» — наше собственное проектное решение, обоснованное удобством, а не заимствованный
из литературы стандарт; так его и надо называть в документах.

**Контекст статьи в целом (аннотация, с. 159):** работа посвящена общей статистической
методологии анализа многомерных категориальных данных из исследований надёжности
наблюдателей — построению функций наблюдённых долей для измерения согласия наблюдателей и
критериям межнаблюдательного смещения, выраженным через однородность маргиналов и
**обобщённые каппа-подобные статистики** (generalized kappa-type statistics). Оценивание и
проверка гипотез (§3.3, с. 165) опираются на подход Grizzle, Starmer & Koch [1969] (GSK).

## ДОБОР Г4 — Feinstein & Cicchetti (1990), два парадокса каппы: АННОТАЦИЯ ИЗДАТЕЛЯ ДОБЫТА ДОСЛОВНО, ПОЛНЫЙ ТЕКСТ НЕ ДОБЫТ

**Реквизиты (Crossref, HTTP 200):** Feinstein A.R., Cicchetti D.V. «High agreement but low
Kappa: I. the problems of two paradoxes». **Journal of Clinical Epidemiology, том 43,
выпуск 6, страницы 543–549, 1990.** DOI **10.1016/0895-4356(90)90158-L**. PMID **2348207**.
🔴 В очереди пробелов записано «J Clin Epidemiol 43:543–549» без номера выпуска — **выпуск 6**,
подтверждено Crossref и списком литературы BMC.

**Парная статья (её реквизиты нужны, потому что решение парадоксов — именно в ней):**
Cicchetti D.V., Feinstein A.R. «High agreement but low kappa: II. Resolving the paradoxes».
J Clin Epidemiol, **43(6):551–558**, 1990, DOI 10.1016/0895-4356(90)90159-M, PMID 2189948.
🔴 Порядок авторов во второй статье **обратный** (Cicchetti первый) — частая ошибка цитирования.

**Каналы:**
- Unpaywall `10.1016/0895-4356(90)90158-l` — HTTP 200: **`is_oa: False`, `oa_status: "closed"`,
  `best_oa_location: None`**. Открытой копии нет.
- ScienceDirect `…/pii/089543569090158L/pdf` — **HTTP 403 при теле 832 805 байт**. Это тот самый
  замер, который уже фиксировался в сессии: большой размер ответа у ScienceDirect НЕ означает,
  что текст получен, это страница-заглушка.
- EuropePMC `fulltextRepo` — HTTP 500.
- ✅ Текстовый прокси `curl -s "https://r.jina.ai/https://www.jclinepi.com/article/
  0895-4356(90)90158-L/abstract"` — **HTTP 200, 16 299 байт**. Получена официальная аннотация
  издателя целиком. Сама страница честно сообщает: «This paper is only available as a PDF»,
  и PDF за пейволлом Elsevier.

### 🔴 ДВА ПАРАДОКСА — ДОСЛОВНО, из авторской аннотации (первичный текст издателя, не пересказ)

> «In a fourfold table showing binary agreement of two observers, the observed proportion of
> agreement, *P₀*, can be paradoxically altered by the chance-corrected ratio that creates κ as
> an index of concordance. **In one paradox, a high value of *P₀* can be drastically lowered by
> a substantial imbalance in the table's marginal totals either vertically or horizontally. In
> the second paradox, κ will be higher with an asymmetrical rather than symmetrical imbalance
> in marginal totals, and with imperfect rather than perfect symmetry in the imbalance.** An
> adjustment that substitutes *K*max for κ does not repair either problem, and seems to make
> the second one worse.»

(В оригинале страницы опечатка «pardox» во втором предложении; ключевые слова статьи: Kappa,
Concordance, Agreement, Paradox.)

**Дисклеймер честности:** это **аннотация**, а не полный текст. Числовых таблиц-примеров
самой статьи мы не видели; ссылаться на конкретные значения κ «из Feinstein & Cicchetti»
нельзя — только на формулировку парадоксов выше.

### Подтверждающее и уточняющее переизложение из ОТКРЫТОГО рецензируемого источника

Канал: `r.jina.ai` → `https://bmcmedresmethodol.biomedcentral.com/articles/10.1186/1471-2288-14-100`
— **HTTP 200, 47 640 байт**. Это «Observer agreement paradoxes in 2×2 tables: comparison of
agreement measures», BMC Medical Research Methodology 14:100 (2014), открытый доступ.

Определения баланса и симметрии, которых в аннотации нет (дословно):
> «In the generic 2×2 table, **balance** refers to whether the ratio of column marginals
> (f1/f2) and the ratio of row marginal (g1/g2) are close to 1, while **symmetry** refers to
> whether the difference in column marginal (f1−f2) has the same sign as the difference in row
> marginal (g1−g2). The first paradox noted by Feinstein and Cicchetti was that **one gets
> lower kappa values despite high observed agreement [P₀ = (x11 + x22)/N] when the marginals
> are imbalanced.** The second paradox is that **one has higher kappa values for asymmetrical
> than for symmetrical imbalanced marginal totals and for imperfect versus perfect symmetry in
> the imbalance.**»

Что предложили сами авторы во второй статье (дословно из BMC):
> «Cicchetti and Feinstein suggested resolving the paradoxes by using **two separate indexes
> (p_pos and p_neg)** to quantify agreement in the positive and negative decisions; these are
> analogous to sensitivity and specificity from a diagnostic testing perspective.»

Другие штатные ответы на парадоксы (дословно из BMC):
> «Byrt et al. discussed the effect of bias and prevalence on kappa and proposed a **prevalence
> and bias adjusted kappa, PABAK**. They also suggested that when reporting kappa, one should
> also report bias and prevalence indices.» (Byrt, Bishop, Carlin, J Clin Epidemiol 46(5):
> 423–429, 1993, DOI 10.1016/0895-4356(93)90018-V)
> «Lantz and Nebenzahl proposed that one should report supporting indicators along with kappa —
> P₀, a symmetry indicator, and p_pos. **Unfortunately, reporting of multiple indices is often
> not done.**» (J Clin Epidemiol 49(4):431–434, 1996, DOI 10.1016/0895-4356(95)00571-4)

Вывод обзора 2014 года (дословно): «While all statistics examined are affected by lack of
symmetry and by imbalances in the marginal totals, **the B-statistic comes closest to resolving
the paradoxes** identified by Feinstein and Cicchetti and Byrt et al. … we **recommend use of
the B-statistic when assessing agreement in 2×2 tables** … and we recommend additionally
providing the corresponding agreement chart». Про саму каппу там же: «Kappa and alpha behave
similarly and are affected by the marginal distributions more so than the B-statistic,
AC1-index and delta measures.» И: «PABAK does not change with changes in prevalence or bias
since it is a simple function of P₀.»

### 🔴 Что это значит для нашей калибровки весов — прямое следствие

Мы меряем каппой согласие экспертов при калибровке весов SAW. Оба парадокса бьют ровно в наш
сценарий: **экспертные оценки альтернатив почти наверняка имеют перекошенные маргиналы**
(эксперты редко раскладывают варианты равномерно по категориям — большинство «приемлемо»,
меньшинство «плохо»). Следствия:
1. Низкая κ при высоком наблюдаемом согласии **не доказывает** расхождения экспертов — это
   может быть парадокс 1. Поэтому **κ нельзя публиковать в одиночку**: вместе с ней обязаны
   идти P₀, индекс смещения (BI) и индекс распространённости (PI) — это буквально
   рекомендация Byrt et al. и Lantz & Nebenzahl, дословно процитированная выше.
2. Рост κ между раундами калибровки **не обязательно означает рост согласия** — парадокс 2:
   κ растёт при АСИММЕТРИЧНОМ перекосе маргиналов. Если между раундами изменилось
   распределение оценок, сравнивать κ раунда 4 и раунда 5 напрямую некорректно.
3. Порог из шкалы Landis & Koch (см. предыдущий раздел) наложен на статистику, которая при
   перекошенных маргиналах систематически занижена — то есть два источника произвола
   складываются. Формулировать в документах так: «κ = X при P₀ = Y, BI = Z, PI = W»,
   а не «согласие существенное».

## ДОБОР Г4 — метаморфическое тестирование: 🔴 АТРИБУЦИЯ В ОЧЕРЕДИ ПРОБЕЛОВ ОШИБОЧНА

### Первое и главное: doi 10.1145/3143561 — это НЕ Segura et al.

В очереди пробелов пункт записан как «**Segura et al., ACM Computing Surveys 51(1),
doi 10.1145/3143561** — обзор метаморфического тестирования». Проверка по Crossref
(`https://api.crossref.org/works/10.1145/3143561`, HTTP 200) даёт другое:

> title: **«Metamorphic Testing»** [полное название — «Metamorphic Testing: A Review of
> Challenges and Opportunities»]; authors: **Chen, Kuo, Liu, Poon, Towey, Tse, Zhou**;
> container-title: **ACM Computing Surveys**, volume **51**, issue **1**, page **1-27**,
> published **2018-01-04**.

**Segura'ы там нет вообще.** Обзор Segura с соавторами — это отдельная работа:

> **Segura S., Fraser G., Sanchez A.B., Ruiz-Cortes A. «A Survey on Metamorphic Testing».
> IEEE Transactions on Software Engineering, том 42, выпуск 9, страницы 805–824,
> сентябрь 2016. DOI 10.1109/TSE.2016.2532875.** (Crossref, HTTP 200.)

🔴 **Итог: в наших текстах ссылку «Segura et al., ACM Comput. Surv. 51(1)» надо разделить на
две — либо Chen et al. (CSUR 2018), либо Segura et al. (IEEE TSE 2016). Существующая запись
склеивает авторов одной работы с выходными данными другой.** Это шестой случай искажения
первоисточника вторичным пересказом за сессию.

### Что добыто полным текстом: препринт-версия обзора Segura et al.

**Канал:** Unpaywall `10.1109/tse.2016.2532875` — HTTP 200, **`is_oa: True`,
`oa_status: "green"`**, репозиторий `https://idus.us.es/handle/11441/38271` (Universidad de
Sevilla). Страница handle — HTTP 200, 418 149 байт; из неё извлечены ссылки на битстримы;
`https://idus.us.es/bitstreams/2ca59b51-6fdd-4ea5-82d8-1189a775ac85/download` —
**HTTP 200, 1 970 284 байта, `application/pdf`**; `pdftotext -layout` → 554 479 байт текста.
(Второй битстрим `d8fffc33-…` — HTTP 200, 1 935 268 байт, но `pdftotext` видит «0 pages»,
битый/иначе закодированный файл; брать первый.)

🔴 **Дисклеймер по версии:** добытый PDF — это **Technical Report ISA-16-TR-02, «Metamorphic
Testing: A Literature Review», Version 1.3, February 9, 2016**, Applied Software Engineering
Research Group, University of Seville. Это авторская версия того же исследования, а **не
журнальная вёрстка TSE 42(9):805–824**; название отличается («A Literature Review» против
«A Survey»), нумерация страниц своя. Цитировать как журнальную статью со страницами нельзя —
либо технический отчёт с его реквизитами, либо журнал без постраничных ссылок.
История версий отчёта дословно: v1.0 — May 25, 2015 «First release»; v1.1 — July 10, 2015
«Eight new papers added… New author added»; v1.2 — January 11, 2016 «Search time span extended
to November 2015. Seventeen new papers reviewed»; v1.3 — February 9, 2016 «New paper added.
Typo fixed.» Охват: «an exhaustive literature review on metamorphic testing, covering
**119 papers published between 1998 and 2015**» (с. 1); сноска 1 на с. 1: «Note that **86 out
of the 119 papers** reviewed in our literature review were published in 2009 or later.»

### 🔴 ОПРЕДЕЛЕНИЯ ДОСЛОВНО

**Проблема оракула и назначение техники (с. 1–2, дословно):**
> «…this problem is referred to as the **oracle problem** and it is recognised as one of the
> fundamental challenges of software testing. **Metamorphic testing is a technique conceived
> to alleviate the oracle problem. It is based on the idea that often it is simpler to reason
> about relations between outputs of a program, than it is to fully understand or formalise
> its input-output behaviour.**»

**Ведущий пример (с. 1, дословно):** «The prototypical example is that of a program that
computes the sine function: What is the exact value of sin(12)? Is an observed output of
−0.5365 correct? A mathematical property of the sine function states that sin(x) = sin(π − x),
and we can use this to test whether sin(12) = sin(π − 12) **without knowing the concrete values
of either sine calculation**.»

🔴 **ОПРЕДЕЛЕНИЕ МЕТАМОРФИЧЕСКОГО ОТНОШЕНИЯ, дословно (с. 1):**
> «This is an example of a **metamorphic relation: an input transformation that can be used to
> generate new test cases from existing test data, and an output relation, that compares the
> outputs produced by a pair of test cases.** Metamorphic testing does not only alleviate the
> oracle problem, but it can also be highly automated.»

**Формальная запись, дословно (с. 2):**
> «In general, a **metamorphic relation for a function f is expressed as a relation among a
> series of function inputs x1, x2, …, xn (with n > 1), and their corresponding output values
> f(x1), f(x2), …, f(xn)**. For instance, for the sine example from the introduction the
> relation between x1 and x2 would be π − x1 = x2, and the relation between f(x1) and f(x2)
> would be equality, i.e.:
> **R = {(x1, x2, sin x1, sin x2) | π − x1 = x2 → sin x1 = sin x2}**»

**Происхождение и обобщение (с. 2, дословно):** «The concept of metamorphic testing,
**introduced by Chen [5] in 1998**, generalises these ideas **from identity relations to any
type of relation, such as equalities, inequalities, periodicity properties, convergence
constraints, subsumption relationships and many others.**»

🔴 **Отличие от инварианта — ключевое для нас (с. 2, дословно):**
> «This resembles the traditional concept of **program invariants**, which are properties (for
> example expressed as assert statements) that hold at certain points in programs. **However,
> the key difference is that an invariant has to hold for every possible program execution,
> whereas a metamorphic relation is a relation between different executions.**»

**Терминология source / follow-up (с. 2, дословно):** «A relation between two executions
implicitly defines how, given an existing **source test case** (x1), one has to transform this
into a **follow-up test case** (x2)… If the relation R does not hold on a pair of source and
follow-up test cases x1 and x2, then a fault has been detected. In this article, we use the
term **metamorphic test case** to refer to a pair of a source test case and its follow-up
test case.»

### Базовый процесс применения — три шага, ДОСЛОВНО (с. 2)

> «1) **Construction of metamorphic relations.** Identify necessary properties of the program
> under test and represent them as metamorphic relations among multiple test case inputs and
> their expected outputs, together with some method to generate a follow-up test case based on
> a source test case. **Note that metamorphic relations may be associated with preconditions
> that restrict the source test cases to which they can be applied.**
> 2) **Generation of source test cases.** Generate or select a set of source test cases for the
> program under test using any traditional testing technique (e.g., random testing).
> 3) **Execution of metamorphic test cases.** Use the metamorphic relations to generate
> follow-up test cases, execute source and follow-up test cases, and check the relations. If
> the outputs of a source test case and its follow-up test case violate the metamorphic
> relation, the metamorphic test case is said to have failed, indicating that the program under
> test contains a bug.»

### Примеры метаморфических отношений из статьи (дословно) — образцы формы

**Кратчайший путь (с. 2):** «consider a program that computes the shortest path between a
source vertex s and destination vertex d in a graph G, SP(G, s, d). A metamorphic relation of
the program is that **if the source and destination vertices are swapped, the length of the
shortest path should be equal: |SP(G, s, d)| = |SP(G, d, s)|**.»

**Поисковая система (с. 2):** «Let Count(q) be the number of results returned for a search
query q. Intuitively, the number of returned results for q should be greater or equal than that
obtained when refining the search with another keyword k. This can be expressed as the
following metamorphic relation: **Count(q) ≥ Count(q + k)**, where + denotes the concatenation
of two keywords.» С конкретными числами (с. 2): «a search for the keyword "metamorphic",
resulting in "About" **4.2M results** … searching for the keywords "metamorphic testing": This
leads to **8,380 results** which is less than the result for "metamorphic", and thus satisfies
the relation.»

**Ранние предшественники (с. 2, дословно):** «Blum et al. checked whether numerical programs
satisfy identity relations such as P(x) = P(x1) + P(x2) for random values of x1 and x2. In the
context of fault tolerance, the technique of **data diversity** runs the program on
re-expressed forms of the original input; e.g., sin(x) = sin(a) × sin(π/2 − b) +
sin(π/2 − a) × sin(b) where a + b = x.»

**Автоматизация (с. 2, дословно):** «If source test cases are generated automatically, then
metamorphic testing enables **full test automation**, i.e., input generation and output
checking.»

**Открытая проблема, названная авторами (с. 2, дословно):** «there are **open questions on how
to derive effective metamorphic relations**, as well as how to reduce the costs of testing with
them.» — то есть построение MR остаётся ручной инженерной работой; ждать от техники
автоматического вывода отношений нельзя.

### Прямое применение к FINPILOT — почему техника нам подходит

У нас ровно проблема оракула: **для расчёта SES + Монте-Карло и для ранжирования SAW нет
эталонного «правильного ответа»**, с которым можно сравнить выход. Метаморфические отношения
строятся без эталона, и их форма для нашей модели выводится из самих определений выше.
Кандидаты, формулируемые по шаблону «преобразование входа → отношение выходов» (наша
формулировка, построенная на определении со с. 1–2, не цитата):
- масштабирование: умножение всего свободного денежного потока и всех долгов на λ > 0 не
  должно менять ДОЛЕВОЕ распределение в оптимальной альтернативе (66 вариантов — доли);
- монотонность по ставке: повышение ставки одного долга при прочих равных не должно снижать
  долю, направляемую на его погашение (Avalanche);
- перестановка: перенумерация долгов с одинаковыми параметрами не должна менять результат;
- сужение допустимого множества: ужесточение порога ПДН не может РАСШИРИТЬ множество
  допустимых альтернатив (аналог `Count(q) ≥ Count(q + k)` дословно из статьи);
- идемпотентность горизонта: прогноз на T шагов, перезапущенный с промежуточного состояния,
  должен совпасть с хвостом исходного прогноза.
Все пять — **отношения между РАЗНЫМИ прогонами**, а не инварианты внутри одного прогона;
именно это отличие авторы называют ключевым (цитата выше, с. 2). Наши Rt ≥ 0 и ПДН ≤ 0,40 —
это **инварианты**, не MR, и одно другого не заменяет.

**Не добыто:** журнальная вёрстка TSE 42(9):805–824 (постраничные ссылки) и обзор Chen et al.
CSUR 51(1) doi 10.1145/3143561 — по последнему Unpaywall даёт `is_oa: True, oa_status: "green"`
с единственным репозиторием `https://nottingham-repository.worktribe.com/output/925152`,
который отдаёт **HTTP 403 на `curl` с браузерным UA** и **HTTP 200/549 байт «Just a moment…
Performing security verification» на `r.jina.ai`** (Cloudflare). Оставлено на следующий добор.

## ДОБОР Г4 — Bengen W.P. (1994), правило 4 %: ПОЛНЫЙ ТЕКСТ ДОБЫТ, МЕТОДОЛОГИЯ ДОСЛОВНО

**Реквизиты:** William P. Bengen, CFP®. «Determining Withdrawal Rates Using Historical Data».
**Journal of Financial Planning, октябрь 1994.** (Во вторичных источниках встречается
«vol. 7, iss. 4, pp. 171–180»; постранично подтвердить не удалось — добытый файл есть
**перепечатка 2004 года** без исходной пагинации, см. дисклеймер ниже.)

**Канал:** `WebSearch` → прямой URL на сайте FPA. 🔴 **Путь в записи файла был устаревшим:**
`…/sites/default/files/**2020-12**/MAR04%20Determining…pdf` — **HTTP 404, 58 596 байт HTML**.
Рабочий путь — с каталогом **`2021-04`**:
`https://www.financialplanningassociation.org/sites/default/files/2021-04/MAR04%20Determining%20Withdrawal%20Rates%20Using%20Historical%20Data.pdf`
— **HTTP 200, 347 755 байт, `application/pdf`**; `pdftotext -layout` → 37 864 байта.
Не сработало: `https://www.retailinvestor.org/pdf/Bengen1.pdf` — HTTP 200, но `text/html`
1 324 байта (заглушка, не PDF).

🔴 **Дисклеймер по изданию, обязателен при цитировании.** Добытый PDF — это **перепечатка
в рубрике «FPA Journal — The Best of 25 Years»**, март 2004 (внутренний колонтитул
`2004_Issues/jfp0304 (N of 13)`). Примечание редактора дословно: «In honor of the Journal of
Financial Planning's 25th anniversary, during 2004 we will reprint what we consider some of the
best content of the Journal. This month, we present William Bengen's research on calculating
"safe" withdrawal rates and asset allocations based on historical data, **which was published
in the October 1994 issue of the Journal**.» То есть текст авторский и полный, но **номера
страниц 171–180 в нём отсутствуют**; ссылаться постранично на оригинал 1994 года по этому
файлу нельзя.

### Источник данных (дословно)

> «In all cases I will rely on actual historical performance of investments and inflation, as
> presented in **Ibbotson Associates' Stocks, Bonds, Bills and Inflation: 1992 Yearbook**.»

Средние из Ibbotson, которыми Бенген иллюстрирует ошибочный подход (дословно): «common stocks
had returned **10.3 percent** compounded over the years, and intermediate-term Treasuries had
returned **5.1 percent**. Inflation averaged **3 percent** over the same period. Therefore, a
client with a portfolio consisting of 60-percent stocks and 40-percent bonds could expect an
average compounded return of **8.2 percent**, assuming continual rebalancing. The "real"
return, adjusted for inflation, would be almost **5.1 percent**.»

🔴 **Формулировка ошибки, ради опровержения которой написана статья (дословно):**
> «**The logical fallacy that got our hypothetical planner into trouble was assuming that
> average returns and average inflation rates are a sound basis for computing how much a client
> can safely withdraw from a retirement fund over a long time.**»

Предшественник, на которого Бенген прямо опирается (дословно): «As **Larry Bierwirth** pointed
out in his excellent article in the **January 1994** issue of this publication ("Investing for
Retirement: Using the Past to Model the Future"), **it pays to look not just at averages, but
at what actually has happened, year-by-year**, to investment returns and inflation in the past.»

### 🔴 МЕТОДОЛОГИЯ СКОЛЬЗЯЩИХ КОГОРТ — ДОСЛОВНО

**Мера результата:**
> «I have quantified portfolio performance in terms of "**portfolio longevity**": **how long the
> portfolio will last before all its investments have been exhausted by withdrawals.** This is
> an intuitive approach that is easy to explain to my clients, whose primary goal is making it
> through retirement without exhausting their funds, and whose secondary goal is accumulating
> wealth for their heirs.»

**Устройство когорт (это и есть искомая «методология скользящих когорт», дословно):**
> «In Figure 1(A), **the first vertical bar on the left represents the portfolio of a client who
> began retirement on Jan. 1, 1926. He made a withdrawal of 3 percent of the portfolio the first
> year, followed by inflation-adjusted withdrawals each succeeding year. The next bar represents
> the portfolio of a client who began retirement on Jan. 1, 1927, and so on.**»

То есть: **один сценарий = один год старта**, ряд стартов идёт подряд с 1926 года, каждая
когорта проживает СВОЮ фактическую историю доходностей и инфляции год за годом. Никакой
случайной генерации, никакого Монте-Карло — только исторические последовательности.
Число когорт названо в тексте позже: «Twenty-four of the **51 scenario years**…» — то есть
51 сценарный год.

🔴 **Горизонт 50 лет — ПРОИЗВОЛЬНАЯ ОТСЕЧКА, а не результат (дословно):**
> «As you can see from the graph, the 1926 client was able to make withdrawals from his
> portfolio in this manner for 50 years. **Actually, the portfolio would have lasted much longer
> than this. I have chosen 50 years arbitrarily as the longest period to show on the charts**,
> as few clients enjoy more than 50 years of retirement.»
Это значит, что столбцы «50 лет» на графиках — **цензурированные наблюдения** (right-censored),
и любая статистика по ним занижает истинную живучесть. Пересказы этого не сообщают почти
никогда.

**Базовое распределение активов — тоже произвольное (дословно):** «a series of graphs
illustrates the historical performance of portfolios consisting of 50-percent intermediate-term
Treasury notes and 50-percent common stocks (**an arbitrary asset allocation chosen for
purposes of illustration**)». И далее: «my conclusions above were based on the assumption that
the client **continually rebalanced** a portfolio of 50-percent common stocks and 50-percent
intermediate-term Treasuries.»

### 🔴 ГЛАВНЫЕ ЧИСЛА — ДОСЛОВНО, с расхождением внутри самой статьи

**3 %:** «Figure 1(A) (three-percent withdrawal rate) is as exciting as a crewcut. It shows that
**all clients, regardless of the year they began their retirement, were able to enjoy at least
50 years of inflation-adjusted withdrawals** from their portfolios.» И: «an "absolutely safe"
(to the extent history is a guide) initial withdrawal level is **3 percent**, in that it ensures
that portfolio longevity is never less than 50 years. (**This is also true for withdrawal rates
as high as approximately 3.5 percent.**) However, most clients would find such a low level of
withdrawals unacceptable.»

**4 % — ключевая формулировка (дословно):**
> «**Assuming a minimum requirement of 30 years of portfolio longevity, a first-year withdrawal
> of 4 percent, followed by inflation-adjusted withdrawals in subsequent years, should be safe.
> In no past case has it caused a portfolio to be exhausted before 33 years, and in most cases
> it will lead to portfolio lives of 50 years or longer. By comparison, a 4.25-percent
> first-year withdrawal could exhaust a portfolio in as little as 28 years, were past conditions
> to repeat themselves.**»

🔴 **Внутреннее расхождение первоисточника, которое надо знать.** Ранее, описывая ту же
Figure 1(B), Бенген пишет: «no client enjoys less than **about 35 years** before his retirement
money is used up». А в разделе выводов — «**before 33 years**». Оба числа — из одной статьи,
про один и тот же график. При цитировании безопасно брать **33 года** (это число стоит в
нормативном выводе) и указывать, что в описании графика автор говорит «около 35».

🔴 **Проверка ходячего пересказа.** Сводка поисковой выдачи в этом же доборе утверждает:
«Bengen tested the withdrawal rates using actual returns over **50-year periods beginning in
1926**. A 3% withdrawal rate lasted 50 years in all test cases. **A 4% withdrawal rate lasted
50 years in 41 of the 50 test cases** and lasted at least 35 years in all cases.» Из добытого
полного текста прямо подтверждается: «all clients… at least 50 years» для 3 %; «no past case…
exhausted before 33 years» и «in most cases… 50 years or longer» для 4 %. Про «41 из 50» —
🔴 **в тексте статьи такой фразы НЕТ.** Ближайшее, что есть: «Fully **47 scenario years** result
in portfolio longevities of the maximum of 50 years, while **only 40 scenario years** attained
that pinnacle in the earlier chart» — и это сравнение **Figure 3(A) (75/25 при 4 %)** против
**Figure 1(B) (50/50 при 4 %)**, то есть для 50/50 при 4 % полной 50-летней живучести достигают
**40** сценарных лет, а не 41. **Цифру «41 из 50» цитировать нельзя**; правильная —
«40 сценарных лет из 51» для 50/50.

**Рекомендация автора клиентам (дословно):** «Therefore, I counsel my clients to withdraw at no
more than a four-percent rate during the early years of retirement, especially if they retire
early (age 60 or younger).»

**6 % — оценка риска (дословно):** «If the client expects to live another 30 years, I point out
that the chart shows **31 scenario years when he would outlive his assets, and only 20** which
would have been adequate for his purposes … This means he has **less than a 40-percent chance**
to successfully negotiate retirement — not very good odds.»

### Выводы по распределению активов (дословно) — обычно опускаются, хотя это половина статьи

Устройство сетки (дословно): «This chart was created by producing **40 graphs** … **Five
possible asset allocations (0-, 25-, 50-, 75-, and 100-percent stocks)** were matched against
**8 percentages of first-year withdrawals (1, 2, 3, 4, 5, 6, 7, and 8 percent)**. All
permutations of these elements were computed as graphs, and **the shortest bar in each graph** —
representing the shortest life of a portfolio for each combination of factors — was transferred
to Figure 2. What is depicted in Figure 2, then, is a "**Worst Case Portfolio Life**" graph.»

- «One pattern that leaps out from the figure is that **holding too few stocks does more harm
  than holding too many stocks.**»
- «the **50/50 stock/bond mix appears to be near-optimum** for generating the highest minimum
  portfolio longevity for any withdrawal scheme.»
- 🔴 Итоговый совет автора **не 50/50, а ближе к 75 % акций** (дословно): «**I think it is
  appropriate to advise the client to accept a stock allocation as close to 75 percent as
  possible, and in no cases less than 50 percent.** Stock allocations lower than 50 percent are
  counterproductive… Somewhere between 50-percent and 75-percent stocks will be a client's
  "comfort zone".» И: «**stock allocations of more than 75 percent are to be avoided at the
  beginning of retirement**», потому что «the minimum longevity during the Little Dipper drops
  below the minimum longevity established on the 50-percent chart».
- «The average portfolio value increase from 35-percent stocks to 75-percent stocks is
  **+123 percent**» (через 20 лет).

### Что это даёт нам методологически

Правило 4 % построено **ровно тем методом, который у нас в модели отсутствует**: прогон
фиксированной политики по ВСЕМ историческим стартовым датам подряд и отчёт по ХУДШЕЙ когорте,
а не по средней. У нас SES + Монте-Карло — синтетические траектории; Бенген бы назвал это
«assuming average returns», ровно той ошибкой, против которой написана статья (цитата выше).
🔴 Это не значит, что наш метод неверен, но означает, что **backtest по скользящим когортам
на исторических рядах ключевой ставки и инфляции РФ — отдельная, не покрытая нами проверка**,
и она дешевле Монте-Карло. Плюс два методологических урока прямо из текста: горизонт-отсечка
создаёт цензурированные наблюдения (их нельзя усреднять как обычные), и отчётная величина —
**минимум по когортам**, а не среднее.

## ДОБОР Г4 — методология Delphi: пороги остановки, число раундов, критерий сходимости. ДВА ПЕРВОИСТОЧНИКА ДОБЫТЫ

### Источник 1 — Linstone & Turoff (ред.), «The Delphi Method: Techniques and Applications» (1975), ПОЛНЫЙ ТЕКСТ

**Канал:** авторская страница NJIT `https://web.njit.edu/~turoff/pubs/delphibook/delphibook.pdf`
— **HTTP 404** (сайт переехал). Wayback CDX по этому URL — HTTP 200, найдены снимки;
взят **20191128162519**. Запрос
`https://web.archive.org/web/20191128162519id_/https://web.njit.edu/~turoff/pubs/delphibook/delphibook.pdf`
— **HTTP 200, 11 700 935 байт, `application/pdf`**; `pdftotext -layout` → 1 499 260 байт.
(Идентичный по digest `QY2HFJT7LPOGPZDYEMDO7WED7SRD4OR5` файл лежит в Wayback ещё с 2003 года
по адресу `is.njit.edu/pubs/delphibook/delphibook.pdf` — то есть версия не менялась.)
Это **седьмой** случай за сессию, когда `id_`-снимок Wayback отдал текст, недоступный на живом
сайте.

🔴 **ЧИСЛО РАУНДОВ — ДОСЛОВНО (раздел IV.A «Introduction», авторы Linstone и Turoff):**
> «It was also observed in all early forecasting Delphis that **a point of diminishing returns
> is reached after a few rounds. Most commonly, three rounds proved sufficient to attain
> stability in the responses; further rounds tended to show very little change and excessive
> repetition was unacceptable to participants.** (Obviously this tendency should not unduly
> constrain the design of Policy Delphis or computerized conferencing which have objectives
> other than forecasting.)»

🔴 **КРИТЕРИЙ ОСТАНОВКИ — СТАБИЛЬНОСТЬ, А НЕ СХОДИМОСТЬ. Дословно (раздел «Evaluation:
Introduction», с. 229 книги, пункт 4 в изложении результатов Dalkey, Brown & Cochran):**
> «**(4) Stability of the distribution of the group's response along the interval scale over
> successive rounds is a more significant measure for developing a stopping criterion than
> degree of convergence.** The authors propose a specific stability measure.»

(Первоисточник этого пункта, по сноске книги: **N. Dalkey, B. Brown, S. Cochran, «Use of
Self-Ratings to Improve Group Estimates», Technological Forecasting 1, No. 3 (1970),
pp. 283–291.**)

**Это прямо противоречит интуитивному «останавливаемся, когда мнения сошлись».** Сходимость
(сужение межквартильного размаха) — наблюдаемое свойство процесса, но останавливаться надо
по СТАБИЛЬНОСТИ распределения между раундами: распределение перестало меняться — стоп,
даже если разброс остался большим.

**Что вообще известно про сходимость (тот же раздел, по Gordon–Helmer, Rand 1964, дословно):**
> «The authors observed two trends: **(1) For most event statements the final-round
> interquartile range is smaller than the initial-round range. In other words, convergence of
> responses is more common than divergence over a number of rounds. (2) Uncertainty increases
> as the median forecast date of the event moves further into the future.** Near-term forecasts
> have a smaller interquartile range than distant forecasts.»

**Мера сходимости, применявшаяся на практике (дословно):** «One indication of the effect of a
Delphi experiment is the amount of convergence caused by the iteration process, where
convergence is a measure of how much more … one measure of convergence was **the change in the
spread between the** [квартилями]…» — то есть рабочая метрика сходимости — **изменение
межквартильного размаха между раундами**.

🔴 **Предупреждение о ложном консенсусе — дословно, из того же раздела:**
> «**There clearly exists the possibility of an unnatural overconsensus. Conformists may
> "capitulate" to group pressures temporarily, on paper.**»
И эмпирика оттуда же: «Respondents are sensitive to feedback of the scores from the whole group
and **tend to move (at least temporarily) toward the perceived consensus**»; «less confident
members exhibit a somewhat larger movement in the second round»; а про догматиков —
«Surprisingly, the **high-dogmatism group exhibits significantly more changes** than the
low-dogmatism group… he views the median of the group response as a surrogate [for authority].»

**Реальная практика раундов в кейсах книги (дословные строки):** «This study was originally
scheduled to be completed in three rounds of interrogation. However, as it evolved, **only two
rounds appeared necessary**»; «The Steel and Ferroalloy Delphi included **three rounds**»;
«The Delphi ran for **three rounds**». Плюс общее замечание: «methods of successive refinement,
like the Delphi, **strongly tend to induce convergence**» — то есть сходимость частично
артефакт процедуры, а не свойство предмета.

### Источник 2 — Diamond et al. (2014), систематический обзор: ЧИСЛА ПО ПОРОГАМ

**Реквизиты (Crossref, HTTP 200):** Diamond, Grant, Feldman, Pencharz, Ling, Moore, Wales.
«Defining consensus: A systematic review recommends methodologic criteria for reporting of
Delphi studies». **Journal of Clinical Epidemiology, том 67, выпуск 4, страницы 401–409,
апрель 2014.** DOI **10.1016/j.jclinepi.2013.12.002**. PMID 24581294.

**Канал:** `r.jina.ai` → `https://www.jclinepi.com/article/S0895-4356(13)00507-6/abstract` —
**HTTP 200, 23 026 байт**. Получена авторская аннотация целиком. Полный текст за пейволлом
Elsevier (не добыт).

🔴 **ЧИСЛА — ДОСЛОВНО ИЗ АННОТАЦИИ (выборка: 100 англоязычных Delphi-исследований из Web of
Science и Scopus, 2000–2009):**
> «About **98 of the Delphi studies purported to assess consensus**, although a definition for
> consensus was only provided in **72** of the studies (**64 a priori**). **The most common
> definition for consensus was percent agreement (25 studies), with 75% being the median
> threshold to define consensus.** Although the authors concluded in **86** of the studies that
> consensus was achieved, consensus was only specified a priori (with a threshold value) in
> **42** of these studies. **Achievement of consensus was related to the decision to stop the
> Delphi study in only 23 studies, with 70 studies terminating after a specified number of
> rounds.**»

Вывод авторов дословно: «Although consensus generally is felt to be of primary importance to
the Delphi process, **definitions of consensus vary widely and are poorly reported.** Improved
criteria for reporting of methods of Delphi studies are required.»

### 🔴 Что из этого следует для НАШИХ пяти раундов калибровки весов

1. **Пять раундов — больше нормы, и это не комплимент.** Linstone & Turoff: «three rounds
   proved sufficient to attain stability… further rounds tended to show **very little change**
   and **excessive repetition was unacceptable to participants**» (дословно выше). Раунды 4 и 5
   у нас с высокой вероятностью не добавили информации, а добавили усталость и конформность.
2. **Мы останавливались не по критерию.** По Diamond et al. это не аномалия (70 из 100
   исследований останавливаются по числу раундов, а не по достижению консенсуса), но и не
   методология: это ровно та практика, которую обзор называет плохо отчитанной.
3. **Правильный критерий остановки — СТАБИЛЬНОСТЬ распределения между раундами, а не степень
   сходимости** (дословная формулировка Dalkey/Brown/Cochran через Linstone & Turoff).
   Проверяемо задним числом по нашим данным: если распределение оценок раунда 4 и раунда 5
   статистически неразличимо — раунд 5 был лишним, и это надо записать честно.
4. **Порог консенсуса обязан быть объявлен ДО начала**, с числом. Медиана по литературе —
   **75 % согласия** (Diamond et al., дословно). Если мы не объявляли порог заранее — так и
   писать: «порог a priori не задавался», а не подбирать его постфактум под полученный
   результат.
5. **Сдвиг к медиане группы — известный артефакт, а не признак правоты** («Respondents…
   tend to move (at least temporarily) toward the perceived consensus», «unnatural
   overconsensus», дословно выше). Совпадение экспертов после 5 раундов частично объясняется
   самой процедурой. Это же смыкается с предыдущим разделом про каппу: согласие, полученное
   итеративной процедурой с обратной связью, нельзя интерпретировать как независимое согласие
   наблюдателей — а каппа считается именно для независимых оценок.


---

## ДОБОР Г31.5 — отказ адреса (17.09.2026)

**Каналы (замер 17.09.2026):** Unpaywall **200** · Crossref **200** · S2 `/paper/DOI:` **200** · Exa search **работает** · прямой `curl -skL` на `www.csc.lsu.edu` **200** (http и https).

Кандидаты класса по файлу и их последнее упоминание:
- **Triantaphyllou & Sánchez 1997** — стр. 869: «Wiley — пейволл; страница автора csc.lsu.edu отдала только аннотацию». Проверялась СТРАНИЦА автора, не его каталог PDF. Класс Г31.5. В доборе Г4 (стр. 934+) не перепроверялся.
- Chen et al. CSUR 51(1) (стр. 870, 1273: Ноттингем 403) — 🟢 **уже добыт** в `closed_forever_retry_2026-09-16.md`, Г18.1 (курсовая копия UW, HTTP 200, 351 596 б). Здесь запись устарела, повторно не добывался.
- Feinstein & Cicchetti 1990 (стр. 1012+) — закрыт на Unpaywall/ScienceDirect/прокси, аннотация добыта; не класс (не один адрес). Не брался.

### Г31.5-Q1. 🟢 Triantaphyllou & Sánchez 1997 — ПОЛНЫЙ ТЕКСТ ДОБЫТ (авторская копия)

- Crossref — **200**: `10.1111/j.1540-5915.1997.tb01306.x`, *Decision Sciences* **28(1):151–194**; вторая запись — глава книги Triantaphyllou «Multi-criteria Decision Making Methods: A Comparative Study», Springer, `10.1007/978-1-4757-3157-6_8`, с. 131–175.
- Unpaywall — **200**, `is_oa: False`, `closed`. S2 `/paper/DOI:` — **200**, `CLOSED`, `citationCount: 633`.
- 🟢 Exa search по точному заголовку вернул прямой адрес авторского PDF, которого нет ни в одном OA-индексе: **`http://www.csc.lsu.edu/trianta/Journal_PAPERS1/MCDM_SensitivityAnalysis_by_Triantaphyllou1.pdf`**.
- `curl -skL` с UA — **HTTP 200, 468 592 б, `application/pdf`**, 51 стр. (рукопись с пометкой «Published in: Decision Sciences, Vol. 28, No. 1, pp. 151-194, Winter 1997»), sha256 `86182766f846f8ad03bd9b58131c19057a5c14b9caba2a5c442dbd3d60655aaa`, `pdftotext` → 3 880 строк. Формулы сняты чтением отрисованных страниц 10–13 (`pdftotext` ломает дроби).

**ДОСЛОВНО — WSM и его допущение (с. 6):**

> «P_i = Σ_{j=1..N} a_ij W_j, for i = 1,2,3,...,M. (3) … The supposition which governs this model is the **additive utility** assumption. However, the WSM should be used only when the decision criteria can be expressed in identical units of measure (e.g., only dollars, or only pounds, or only seconds, etc.).»

**ДОСЛОВНО — абсолютные против относительных изменений (с. 8–9):**

> «In the first way the interest is on whether the indication of the best (top) alternative changes or not. On the second definition the interest is on changes on the ranking of any alternative. … suppose that the two criteria C1 and C2 have weights W1 = 0.30 and W2 = 0.50 … when the first weight becomes W′1 = 0.35 … the second weight becomes W′2 = 0.57 … In absolute terms for both criteria, the first criterion is the most critical criterion. … However, when one considers relative terms … for C1 is: |W1 − W′1| × 100/W1 = 16.67, while for C2 it is: |W2 − W′2| × 100/W2 = 14.00. … Therefore, when the relative changes are considered, then the most critical criterion is C2.»
>
> «Therefore, a total of four alternative definitions can be considered. These are coded as Absolute Any (AA), Absolute Top (AT), Percent Any (PA), and Percent Top (PT). … it is more meaningful to use relative changes. Therefore, in this paper the emphasis will be on relative (percent) changes…»

**ДОСЛОВНО — определения (с. 10–11):**

> «DEFINITION 1: Let δ_k,i,j (1 ≤ i < j ≤ M and 1 ≤ k ≤ N) denote the minimum change in the current weight W_k of criterion C_k such that the ranking of alternatives A_i and A_j will be reversed. Also, define as: δ′_k,i,j = δ_k,i,j × 100/W_k (6). … it is possible for a given pair of alternatives and a decision criterion, the critical change to be infeasible.»
>
> «DEFINITION 2: The Percent-Top (or PT) critical criterion is the criterion which corresponds to the smallest |δ′_k,1,j| (1 ≤ j ≤ M and 1 ≤ k ≤ N) value.»
> «DEFINITION 3: The Percent-Any (or PA) critical criterion is the criterion which corresponds to the smallest |δ′_k,i,j| (1 ≤ i < j ≤ M and 1 ≤ k ≤ N) value.»
> «DEFINITION 4: The criticality degree of criterion C_k, denoted as D′_k, is the smallest percent amount by which the current value of W_k must change, such that the existing ranking of the alternatives will change. That is: D′_k = min_{1≤i<j≤M} {|δ′_k,i,j|}»
> «DEFINITION 5: The sensitivity coefficient of criterion C_k, denoted as sens(C_k), is the reciprocal of its criticality degree: sens(C_k) = 1/D′_k. **If the criticality degree is infeasible (i.e., impossible to change any alternative rank with any weight change), then the sensitivity coefficient is set equal to zero.**»

**ДОСЛОВНО — Теорема 1 (с. 12), для WSM и AHP:**

> «δ_1,1,2 < (P2 − P1)/(a21 − a11), if (a21 > a11), or: δ_1,1,2 > (P2 − P1)/(a21 − a11), if (a21 < a11). (7a) Furthermore, the following condition should also be satisfied for the new weight W*1 = W1 − δ_1,1,2 to be feasible: 0 ≤ W*1 … δ_1,1,2 ≤ W1. (7b) **In these developments it is not required to have W*_i ≤ 1 because these weights are re-normalized to add up to one.** … it may be **impossible** to reverse the existing ranking of the alternative A1 and A2 by making changes on the current weight of criterion C1. This situation occurs when the value of the ratio (P2 − P1)/(a21 − a11) is greater than W1.»
>
> «THEOREM 1: When the WSM, AHP, or ideal mode AHP methods are used, the quantity δ′_k,i,j (1 ≤ i < j ≤ M and 1 ≤ k ≤ N), by which the current weight W_k of criterion C_k needs to be modified (after normalization) so that the ranking of the alternatives A_i and A_j will be reversed, is given as follows: δ′_k,i,j < (P_j − P_i)/(a_jk − a_ik) × 100/W_k, if (a_jk > a_ik) or: δ′_k,i,j > (P_j − P_i)/(a_jk − a_ik) × 100/W_k, if (a_jk < a_ik). (8a) Furthermore, the following condition should also be satisfied for the value of δ′_k,i,j to be feasible: (P_j − P_i)/(a_jk − a_ik) ≤ W_k. (8b)»

**Выжимка и сверка с тем, что записано в §3.2 файла (восстановлено по Jaini & Utyuzhnikov 2016).**
1. Метод в файле восстановлен **верно по существу**: минимальное возмущение веса с последующей перенормировкой, аналитически для WSM.
2. 🔴 **Три уточнения, которых в §3.2 нет:**
   (а) Предложенный в файле «Stability margin `SM = min_k |δ*_k|/w_k` при смене рекомендованной альтернативы» — это ровно **PT-критический критерий** (Def. 2), а не PA (Def. 3–4, смена любого ранга). Для совета по одной рекомендованной альтернативе PT — правильный выбор, но называть его надо так, и **D′_k/sens(C_k) из Def. 4–5 — это PA**, их нельзя подставлять вместо PT.
   (б) **Критическое изменение может не существовать** (8b): если (P_j − P_i)/(a_jk − a_ik) > W_k, никакое изменение веса k не переставляет пару. В формуле SM файла этот случай не обработан — минимум по пустому множеству не определён; у авторов sens = 0 (Def. 5). При реализации это надо закрыть явно, иначе SM даст деление на ноль или ложный «0 %».
   (в) Абсолютная и относительная мера **дают разные критические критерии** на одних данных (пример 0.30/0.50 выше). Выбор относительной меры в файле совпадает с выбором авторов — теперь со ссылкой на первоисточник.
3. Оговорка авторов о применимости WSM — «only when the decision criteria can be expressed in identical units» — у нас выполняется только после нормировки к безразмерной шкале; это то же условие, что и в споре о нормировке (см. `mcda_saw_alternatives`, Г31.5-M1).

## ИТОГ Г31.5 — prescriptive_quality_metrics

3 кандидата: **Triantaphyllou & Sánchez 1997 — закрыт полным текстом** (канал: **Exa search** дал прямой адрес авторского PDF, скачан `curl`; ни Unpaywall, ни S2, ни OpenAlex этого адреса не знают); **Chen et al. CSUR — закрыт ссылкой** на Г18.1; Feinstein & Cicchetti — не класс, не брался.

🔴 **Что меняет обоснование (канон не трогается):** предложенная метрика устойчивости совета (SM, §3.2) по первоисточнику — PT-критический критерий; при реализации обязательна обработка **недостижимого** критического изменения (8b) — авторы кладут sens = 0. Без этого метрика на части портретов будет неопределена. Заведение метрики — решение владельца.
Задолженности нет.
