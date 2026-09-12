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
