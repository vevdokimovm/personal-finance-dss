# Тема 39. Верен ли подход по существу — валидация ЗАМЫСЛА

Дата: 2026-09-10. Агент: base-kit:researcher (лид, подагентов — ноль).
Статус: ЗАВЕРШЕНО. Субагентов — ноль. WebSearch — 22 вызова, отказов нет.

Вопрос темы: не «правильно ли мы считаем», а **правильную ли вещь мы считаем**,
и по каким критериям такие продукты судит отрасль.

---

## 0. Короткий ответ владельцу

**Подход верен наполовину, и надо знать, какой именно половиной.**

🟢 **Держится:** инварианты платёжеспособности, Avalanche-арифметика (входы известны точно,
не оцениваются) и — самое сильное, что нашлось, — **отсутствие «советнического стиля»**.
Foerster et al. (JF 2017) показали на канадских данных: фикс-эффект советника объясняет
вдвое больше вариации портфеля клиента, чем весь набор характеристик самого клиента, и
собственное распределение советника предсказывает то, что он назначит клиенту. Алгоритм
такого эффекта не имеет по конструкции. Mullainathan/Noeth/Schoar (NBER 2012, аудит):
советники «fail to de-bias their clients and often reinforce biases that are in their
interests». **Планка, против которой нас разумно судить, низкая — и это работает на нас.**

🔴 **Не держится три вещи.**
1. **Утверждение «повышаем финансовое благополучие» — пустое**, потому что неопровержимо:
   конечная точка спорна в самой отрасли (CFPB строит субъективную шкалу — CRR на данных
   FINRA заключает, что субъективная оценка «has become a poor measure of financial
   well-being»), контрфактический исход того же человека ненаблюдаем, а потолок связи
   «деньги → благополучие» задан извне: ρ(доход, FWB) = 0,38.
2. **SAW-свёртка попадает во все три условия less-is-more Гигеренцера** (низкая
   предсказуемость критерия R² ≤ 0,5 · мало наблюдений на число критериев · критерии
   коррелированы) — то есть находится ровно в той зоне, где равные веса и простые правила
   исторически бьют оптимизацию. Это не значит, что мы проиграем; это значит, что **мы
   обязаны это проверить, а не предполагать**.
3. **Пять раундов калибровки против четырёх экспертных движков — не валидация**, а
   developmental evidence: нет отделения критики от разработки, которого требует
   «effective challenge» SR 11-7. Согласие 78,63 % не даёт права ни на какое утверждение
   о верности подхода.

**Что делать:** заменить формулировку продукта на проверяемую («снижает переплату при
исполнении плана, не нарушая инвариантов платёжеспособности») и провести три проверки
из разд. 5 — они исполнимы на синтетике, без пользователей, и любая из них может
опровергнуть метод (разд. 6). Планировать эффект пилота надо как **1/6** от литературного
(DellaVigna & Linos: 8,7 п.п. в журналах против 1,4 п.п. в полевых юнитах, 70 % разрыва —
публикационный отбор).

## 0.1 Метод поиска
См. разд. 8 в конце файла (каналы, замеры, что не добыто).

## 1. Участок 1. Теория изменений — где рвётся цепочка

### 1.1 Методология: логическая модель ≠ теория изменений
Первоисточник добыт: Clark H., Anderson A. «Theories of Change and Logic Models: Telling
Them Apart», доклад на American Evaluation Association, Атланта, ноябрь 2004
(`theoryofchange.org/wp-content/uploads/toco_library/pdf/TOCs_and_Logic_Models_forAEA.pdf`,
PDF 1.5, 24 стр., HTTP 200; текст 7 486 байт — презентация, слайды).

Дословно из презентации:
> **Logic model:** "Inputs → Activities → Outputs → Intermediate Outcomes → Long-term
> Outcomes" (Basic United Way format, 1996).

> **Theory of Change:** "Popularized in 1990s to capture complex initiatives · Outcomes-based
> · Causal model · Articulate underlying assumptions."

Три различия, названные авторами дословно:
> "(1) Logic Models usually start with a program and illustrate its components. Theories of
> Change may start with a program, but are best when **starting with a goal, before deciding
> what programmatic approaches are needed**."

> "(2) Logic Models require identifying program components, so you can see at a glance if
> outcomes are out of sync with inputs and activities, **but they don't show WHY activities
> are expected to produce outcomes**. Theories of Change also require justifications at each
> step – **you have to articulate the hypothesis about why something will cause something
> else** (it's a causal model, remember!)"

> "(3) Logic Models don't always identify indicators… **Theories of Change require
> identifying indicators**… Because, you need to know **HOW WELL a precondition needs to be
> met** in order to get to the next goal."

🔴 **Критерий корректно сформулированной цепочки, снятый отсюда:** (а) начинать с цели,
а не с программы; (б) на КАЖДОМ переходе — явная гипотеза «почему A вызовет B»;
(в) на каждом переходе — индикатор И **порог**: насколько сильно предусловие должно быть
выполнено, чтобы следующее звено сработало.

🔴 **Приговор нашей нынешней цепочке по этому критерию.** Наша цепочка «посчитали →
показали → человек исполнил → переплата снизилась → благополучие выросло» — это
**логическая модель, а не теория изменений**: она перечисляет звенья, но ни на одном
переходе у нас нет ни записанной гипотезы, ни порога. Мы не знаем и нигде не зафиксировали,
**какая доля исполнения плана** нужна, чтобы переплата упала, и **какое снижение переплаты**
нужно, чтобы сдвинулось благополучие. По Кларк это ровно тот случай, ради которого
различие и вводилось.

### 1.2 Где цепочка рвётся — звено за звеном, по имеющимся данным

| # | Переход | Что известно | Статус |
|---|---|---|---|
| 1 | расчёт → рекомендация показана | техническое, под нашим контролем | 🟢 держится |
| 2 | показали → человек исполнил | алгоритм-аверсия: только 19 % доверяют робо-советнику принимать решения (HSBC, по обзору FPA — 🔴 сниппет); тема 36: совет «погаси долг из накоплений» будет отвергнут, т.к. подушка — устройство самоконтроля | 🔴 **рвётся** |
| 3 | исполнил → переплата снизилась | арифметика Avalanche, при условии исполнения | 🟡 держится условно |
| 4 | переплата снизилась → благополучие выросло | ρ(доход, FWB) = 0,38; ρ(подушка 3 мес., FWB) = 0,54 (CFPB, разд. 2.1) | 🔴 **слабое** |
| 5 | эффект в пилоте → эффект в поле | DellaVigna & Linos: 8,7 п.п. в журналах против 1,4 п.п. в полевых юнитах | 🔴 **рвётся** |

### 1.3 🔴 Прямой вопрос: не оптимизируем ли мы величину, которая не влияет на конечный исход
Честный ответ по добытому: **частично да, и это самая серьёзная угроза замыслу.**

Три независимых свидетельства:

**(а) Субъективное благополучие отражает не то, что мы оптимизируем.**
Munnell, Hou et al., Center for Retirement Research at Boston College, WP 2015-3
«What Do Subjective Assessments of Financial Well-Being Reflect?» (данные FINRA National
Financial Capability Study 2012). Добыто полностью: `crr.bc.edu/wp-content/uploads/2015/03/
wp_2015-3.pdf`, PDF 1.5, HTTP 200, текст 73 692 байта. Дословные выводы авторов:
> "• Subjective financial assessments primarily reflect day-to-day conditions.
> • This remains the case even if the household's day-to-day finances are in reasonably
> good shape.
> • Financial literacy enhances sensitivity to the lack of a retirement plan and having a
> mortgage greater than the value of one's house, but it has no noticeable effect on
> sensitivity to life and medical insurance deficits, having an inactive retirement plan,
> not saving for college, or student debt burdens."

Вывод авторов дословно:
> "Subjective financial assessments have become a **poor** measure of financial well-being."

И рамка, ради которой это стоит прочитать целиком:
> "Peace of mind is one of the great benefits that comes from having one's financial house
> in order. Financial satisfaction is also often used as a measure of financial well-being.
> **But bliss could be the fruit of ignorance.** If so, subjective financial assessments
> would be imperfect measures of well-being and **peace of mind hazardous to financial
> health.**"

🔴 **Это конфликт с 2.1 и его надо назвать прямо.** CFPB строит шкалу субъективного
благополучия и предъявляет её как измеритель исхода. CRR на данных FINRA утверждает,
что субъективная оценка — **плохой** измеритель благополучия, потому что систематически
слепа к отдалённым дефицитам. Два уважаемых источника, противоположные выводы. Для нас
это значит: **выбор конечной точки — не техническая деталь, а спорный вопрос отрасли.**
Если мы возьмём субъективную шкалу — будем ловить сегодняшний комфорт (и рискуем показать
«улучшение» у человека, который просто перестал смотреть). Если возьмём объективные
коэффициенты — будем мерить то, что человек не чувствует и за что не заплатит.

**(б) Больше знания о своих финансах может СНИЖАТЬ удовлетворённость.**
🔴 Только сниппет поисковой выдачи, первоисточник не открыт: в литературе есть результат,
что «financial literacy reduces satisfaction» с объяснением, что финансово грамотные
«не имеют более слабых финансов, но лучше видят дефициты». Это ровно механизм темы 26
(Commonwealth Bank показал 124 251 клиенту цену их ошибки, эффект на погашение
p = 0,162). 🔴 Для нас: показ «вы переплачиваете N рублей» может улучшить объективный
исход и **одновременно ухудшить субъективный**. Наш продукт может быть одновременно
успешным и вредным — по разным конечным точкам.

**(в) Настоящий разрыв — не в оптимальности, а в персонализации, и он бьёт в другую
сторону.** Foerster, Linnainmaa, Melzer, Previtero, «Retail Financial Advice: Does One Size
Fit All?», *Journal of Finance* 72(4), 2017, стр. 1441–1482. Добыто полностью с авторской
страницы `aleprevitero.com/wp-content/uploads/2020/06/024_Previtero_JF_2017.pdf`
(HTTP 200, PDF 1.4, текст 137 900 байт). Дословно:
> "clients' observable characteristics jointly explain only 12% of the [cross-sectional
> variation in risky share] … a remarkable amount of variation in portfolio risk remains
> unexplained. Advisor fixed effects, by contrast, have substantially more explanatory power.
> On their own, advisor effects explain 22% of the variation in risky share. When [added to
> client characteristics they] double the adjusted-R2 from 12% to 30%, meaning that advisor
> fixed effects explain **one and a half times as much of the variation in risky share as
> that explained by the full set of client characteristics.**"
> "…client characteristics explain only 4% of the variation [in home bias], [while] advisor
> fixed effects explain an additional 24% of the variation."
> "An advisor's own asset allocation strongly predicts the allocations chosen on clients'
> behalf."

🔴 **Это аргумент ЗА нас, и единственный сильный, найденный в этой теме.** Живой советник
навязывает клиенту свой собственный стиль: его фикс-эффект объясняет вдвое больше вариации,
чем все характеристики клиента вместе. Алгоритм, детерминированно считающий от анкеты,
такого фикс-эффекта не имеет **по конструкции**. То есть ценность нашего продукта надо
формулировать не как «мы считаем оптимальнее человека», а как **«мы не подмешиваем
советнический стиль в рекомендацию»** — это проверяемо и подтверждено данными.

### 1.4 Внешняя валидность: множитель разрыва подтверждён первоисточником
DellaVigna S., Linos E. «RCTs to Scale: Comprehensive Evidence from Two Nudge Units»,
*Econometrica* 90(1), 2022, стр. 81–116. Добыто полностью — рабочая версия автора
`eml.berkeley.edu/~sdellavi/wp/NudgeToScale2021-04-19.pdf` (HTTP 200, PDF 1.6, текст
261 137 байт). 🔴 Числа сверены по тексту PDF, не по сниппету:
> "In the 26 papers in the Academic Journals sample… a nudge intervention increases take up
> by **8.7 (s.e.=2.5) percentage points (pp.), a 33.4 percent increase** over the average
> control group take up of 26.0 percent."
> "Turning to the **126 trials by Nudge Units**, we estimate an unweighted impact of
> **1.4 pp. (s.e.=0.3), an 8.0 percent increase** over an average control group take-up of
> 17.3 percent. While this impact is highly statistically significantly different from 0 and
> sizable, it is **about one sixth the size** of the estimate in academic papers, and we can
> reject the hypothesis of equal effect sizes in the two samples."
> "For the Academic Journal trials, **selective publication accounts for about 70 percent**
> of the larger effect size relative to the Nudge Unit trials."

Выборка: "126 RCTs covering 23 million individuals" против 26 статей / 74 воздействия /
505 337 участников.

🔴 **Практическое правило для FINPILOT, выводимое отсюда прямо:** любой опубликованный
эффект вмешательства, на который мы ссылаемся при обосновании продукта (включая шаблон
Levi, JFQA 2025, −15 % дискреционных расходов из темы 37), при переносе в наше поле
надо **делить примерно на шесть**, и 70 % этого разрыва — не «наше поле другое»,
а публикационный отбор. Ожидаемый эффект нашего продукта на переплату следует
планировать как ~1/6 от литературного, и **закладывать это в размер выборки пилота
заранее** — иначе пилот будет недомощным по конструкции и вернёт p = 0,162, как
у Commonwealth Bank (тема 26).

## 2. Участок 2. Конструктная валидность

### 2.1 Что вообще измеряет «финансовое благополучие» — шкала CFPB и её валидаторы
Добыто полностью: `sjdm.org/dmidi/files/CFPB_Financial_Well-Being_Scale_Technical_Report.pdf`
(HTTP 200, PDF 1.5; `pdftotext -layout` → 106 364 байта текста). Числа ниже сняты
**из таблиц самого отчёта**, не из сниппета.

Определение валидности в самом отчёте (дословно, сноска о типах валидности):
> "…related validity, construct validity, and internal consistency. Content validity pertains
> to the adequacy with which a [measure covers the domain] … Construct validity is concerned
> with the relationship of the [measure of interest and another independent measure]…"

**Таблица 7 отчёта — корреляции Спирмена шкалы FWB с внешними валидаторами:**

| Валидатор | N | ρ |
|---|---|---|
| Самооценка кредитной истории (1–5) | 6 854 | **0,53** |
| Уверенность, что найдёт $2 000 при неожиданной нужде за месяц | 7 030 | **0,64** |
| Отложены ли средства на 3 месяца расходов (да/нет) | 7 310 | **0,54** |
| Самооценка текущей финансовой ситуации (1–7) | 7 222 | **0,63** |
| «Был случай за год, когда нужна еда, но не мог купить» | 10 166 | **−0,43** |
| «Нужен был врач, но не пошёл — не мог позволить» | 10 166 | **−0,35** |
| Долг в коллекторах | 1 218 | **−0,30** |
| Число негативных финансовых шоков за 12 мес. | 10 166 | **−0,31** |

Все p < 0,0001.

**Таблица 8 — связь с объективным СЭС:** годовой доход домохозяйства (среднее $62 948,
SD $48 013, N = 9 378) — **ρ = 0,38**.

🔴 **Это ядро проблемы конструктной валидности для нас.** Доход — самый объективный
денежный показатель — объясняет **менее 15 % дисперсии** субъективного благополучия
(0,38² ≈ 0,144). Даже наличие подушки на 3 месяца — ρ = 0,54, то есть ~29 % дисперсии.
Наша SAW-полезность считается **из денежных величин** (остатки, ставки, ПДН, горизонт).
Значит, потолок её корреляции с тем, что называется «финансовым благополучием»,
задан сверху этими же 0,3–0,6, и это **при идеально работающей модели**.

Побочное, но важное: сама шкала CFPB **не строится на финансовых данных**: у респондента
не спрашивают доход, активы, обязательства и норму сбережения. То есть отраслевой
эталон «конечного исхода» в этой области — **опросная субъективная величина**,
а не бухгалтерия.

### 2.2 Два раздельных конструкта, а не один (Netemeyer et al., JCR 2018)
🔴 **Добыто только из сниппета WebSearch — полный текст за пейволлом Oxford Academic,
дословность не подтверждена.** Ключевая рамка: воспринимаемое финансовое благополучие —
это **два связанных, но раздельных конструкта**: (1) *current money management stress* —
стресс от управления деньгами сегодня; (2) *expected future financial security* —
ощущение защищённости будущего. У них **разные антецеденты**, а относительная важность
первого для общего благополучия меняется по доходным группам.

🔴 Для нас это прямая угроза дискриминантной валидности: наша целевая функция
(минимизация переплаты + рост резерва + достижение целей) бьёт преимущественно
во **второй** конструкт (будущая защищённость), а поведенческий отказ от рекомендации
(тема 36: подушка как устройство самоконтроля) идёт из **первого**. Одна свёртка SAW
не может быть суррогатом двух конструктов с разными антецедентами — либо надо
показывать, что она нагружается на оба, либо признать, что мы оптимизируем один.

### 2.3 Кэмпбелл–Фиске: что именно надо показать
🔴 **Первоисточник (Campbell & Fiske, Psychological Bulletin 1959, «Convergent and
discriminant validation by the multitrait-multimethod matrix») в этой сессии НЕ добывался —
формулировка ниже даётся по общему знанию канона и должна быть подтверждена перед
цитированием в докладе.** Требование MTMM в применении к нам:
- **конвергентная**: наша SAW-полезность должна значимо коррелировать с *другой методикой
  измерения того же* — например, с экспертной оценкой того же плана и с CFPB-баллом
  пользователя. Один метод ≠ валидация;
- **дискриминантная**: она должна коррелировать с «благополучием» **сильнее**, чем
  с посторонними чертами, измеренными тем же методом (доход, возраст, размер долга).
  🔴 Наш риск: SAW-полезность может оказаться просто линейной функцией дохода и остатка
  долга — тогда дискриминантной валидности нет, и «полезность» — переименованный доход;
- **матрица**: нужно ≥2 черты × ≥2 метода. У нас сейчас одна черта и один метод
  (сам движок). Формально это **ноль** доказательств конструктной валидности.

### 2.4 Суррогатные конечные точки — Fleming & DeMets
Библиография подтверждена: Fleming T.R., DeMets D.L. «Surrogate end points in clinical
trials: are we being misled?» *Annals of Internal Medicine*, 1996; **125(7): 605–613**
(PMID 8815760).

🔴 **Полный текст НЕ добыт.** Замеры каналов: `WebFetch` на `acpjournals.org/doi/...` —
антибот; `curl` с браузерным UA на PDF-версию — **HTTP 403, тело 5 785 байт HTML**;
`r.jina.ai` на страницу статьи — **HTTP 200, но 514 байт с текстом «Just a moment… /
Performing security verification»**, то есть прокси вернул страницу капчи, а не статью.
Препринта 1996 года в открытых архивах не существует (до-arXiv эпоха для медицины).

Содержание по сниппету поисковой выдачи (🔴 **сниппет, не первоисточник**): требование
к суррогату — эффект вмешательства на суррогат должен надёжно предсказывать эффект
на клинический исход; *«in practice, this requirement frequently fails»*. Названные
режимы отказа: суррогат не предсказывает целевой исход; суррогат не улавливает эффект
вмешательства; использование суррогата не даёт информации о профиле безопасности
и может привести к одобрению вредного вмешательства — из-за побочных путей воздействия,
не лежащих на известном причинном пути болезни.

🔴 **Прямая аналогия, ради которой это искалось.** Наша SAW-полезность — суррогат
финансового благополучия. Все три режима отказа переносятся дословно:
1. полезность может не предсказывать благополучие (см. 2.1 — потолок 0,3–0,6);
2. полезность может не улавливать эффект самого продукта (человек не исполнил план —
   тема 26, эффект p = 0,162);
3. 🔴 **самый недооценённый**: оптимизация по суррогату может **навредить** по побочному
   пути, не лежащему на нашей причинной схеме — например, план «перекинь резерв в долг»
   математически повышает полезность и одновременно снимает устройство самоконтроля
   (тема 36), что бьёт по «current money management stress» (2.2). Модель этого пути
   не видит вовсе, потому что его нет в целевой функции.

## 3. Участок 3. Как отрасль судит такие продукты

### 3.1 SR 11-7 / OCC 2011-12 — де-факто стандарт валидации финансовых моделей
Добыто полностью: `federalreserve.gov/boarddocs/srletters/2011/sr1107.pdf` (сопроводительное
письмо, 5 стр., HTTP 200, 66 481 байт) + текст самой методички через рескинженную копию OCC
`occ.gov/static/rescinded-bulletins/bulletin-2011-12.pdf` (PDF 1.7, `pdftotext -layout` →
72 581 байт текста). Ссылка `federalreserve.gov/supervisionreg/srletters/sr1107a1.pdf`
отдала **HTML-страницу вместо PDF** (81 КБ HTML) — приложение через неё не берётся,
поэтому канон читался по копии OCC (текст идентичен, это совместный документ ФРС+OCC).

**Определение модели (дословно, OCC 2011-12 Attachment, разд. III):**
> "the term model refers to a quantitative method, system, or approach that applies
> statistical, economic, financial, or mathematical theories, techniques, and assumptions
> to process input data into quantitative estimates. A model consists of three components:
> an information input component, which delivers assumptions and data to the model;
> a processing component, which transforms inputs into estimates; and a reporting
> component, which translates the estimates into useful business information."

> "The definition of model also covers quantitative approaches whose inputs are partially
> or wholly qualitative or based on expert judgment, provided that the output is
> quantitative in nature."

🔴 Для нас: **наш SAW-движок подпадает под это определение целиком** — вход (анкета,
остатки, ставки), обработка (перебор 66 альтернатив + свёртка + SES/Монте-Карло), отчёт
(рекомендация пользователю). И оговорка про «вход частично экспертный» закрывает попытку
сказать «у нас же веса от экспертов, это не модель».

**Две причины модельного риска (дословно):**
> "Model risk occurs primarily for two reasons: The model may have fundamental errors and
> may produce inaccurate outputs when viewed against the design objective and intended
> business uses. […] The model may be used incorrectly or inappropriately. Even a
> fundamentally sound model producing accurate outputs consistent with the design objective
> of the model may exhibit high model risk if it is misapplied or misused."

🔴 Вторая причина — это ровно тема 39. Модель может считать правильно и при этом быть
применена не к тому. Регулятор США явно выделяет это как **отдельный** источник риска,
не сводимый к точности расчёта.

**Guiding principle — «effective challenge» (дословно):**
> "A guiding principle for managing model risk is 'effective challenge' of models, that is,
> critical analysis by objective, informed parties who can identify model limitations and
> assumptions and produce appropriate changes. Effective challenge depends on a combination
> of incentives, competence, and influence. Incentives to provide effective challenge to
> models are stronger when there is greater separation of that challenge from the model
> development process…"

🔴 Прямое следствие для нас: **пять раундов калибровки против четырёх экспертных движков —
это НЕ effective challenge**, потому что нет разделения: движки подбирались и настраивались
той же стороной, что и модель. Согласие 78,63 % — это показатель схождения, а не
независимой критики. По SR 11-7 это относится к «developmental evidence», а не к валидации.

**Три ядра валидации (дословно):**
> "An effective validation framework should include three core elements:
> • Evaluation of conceptual soundness, including developmental evidence
> • Ongoing monitoring, including process verification and benchmarking
> • Outcomes analysis, including back-testing"

Про conceptual soundness — что именно требуется:
> "Validation should ensure that judgment exercised in model design and construction is well
> informed, carefully considered, and consistent with published research and with sound
> industry practice. […] **Comparison to alternative theories and approaches should be
> included.** Key assumptions and the choice of variables should be assessed, with analysis
> of their impact on model outputs and particular focus on any potential limitations."

🔴 «Comparison to alternative theories and approaches should be included» — это регуляторное
требование сравнить нашу оптимизацию с наивным правилом (см. участок 4). Не пожелание.

Про чувствительность:
> "banks should employ sensitivity analysis in model development and validation to check the
> impact of small changes in inputs and parameter values on model outputs to make sure they
> fall within an expected range. Unexpectedly large changes in outputs in response to small
> changes in inputs can indicate an unstable model."

Про периодичность и порог отказа:
> "Banks should conduct a periodic review—at least annually but more frequently if
> warranted—of each model to determine whether it is working as intended…"
> "Validation also can reveal deterioration in model performance over time and can set
> thresholds for acceptable levels of error, through analysis of the distribution of
> outcomes around expected or predicted values. **If outcomes fall consistently outside
> this acceptable range, then the models should be redeveloped.**"

Про соблазн судить по исходам (важно, перекликается с FCA из темы 37):
> (стр. с ongoing monitoring) "…that model risk is low simply because outcomes from
> model-based decisions appear favorable" — прямо назван как ошибочный вывод.

### 3.2 🔴 SR 11-7 в 2026 году УЖЕ НЕ ДЕЙСТВУЕТ в редакции OCC — заменена OCC 2026-13
Найдено попутно и это меняет формулировку «де-факто стандарт». OCC выпустил **Bulletin
2026-13 «Model Risk Management: Revised Guidance»**, которая **рескиндит** OCC 2011-12
и ряд связанных выпусков (в т.ч. буклет Comptroller's Handbook «Model Risk Management»,
OCC 1997-24 по кредитному скорингу, OCC 2021-19 по BSA/AML).

Источник: `occ.gov/news-issuances/bulletins/2026/bulletin-2026-13.html` (добыто `WebFetch`
+ `curl`, HTTP 200, 65 057 байт HTML). Дословные фрагменты, полученные через `WebFetch`
(🔴 **пересказ модели, не сверенный построчно по HTML** — помечаю; текстовая выжимка
через python-стриппер подтвердила только рамку и список рескиндов):
- новое определение модели: *"a **complex** quantitative method, system, or approach that
  applies statistical, economic, or financial theories to process input data into
  quantitative estimates"* — и явное исключение: *"simple arithmetic calculations, such as
  those found within spreadsheets, as well as deterministic rule-based processes"*;
- *"Generative AI and agentic AI models are novel and rapidly evolving. As such, they are
  not within the scope of this guidance."*;
- порог применимости — банки свыше **$30 млрд** активов;
- *"does not set forth enforceable standards or prescriptive requirements; accordingly,
  non-compliance with this guidance will not result in supervisory criticism."*

🔴 Два вывода для нас. (1) Ссылаться в документации на «SR 11-7» как на действующий
стандарт в 2026 — уже неточность на стороне OCC; корректная формулировка: «валидация
построена по трём ядрам SR 11-7 (2011), с учётом пересмотра OCC 2026-13». (2) Новое
определение с оговоркой про «deterministic rule-based processes» **не спасает нас** —
у нас Монте-Карло и SES, это не детерминированное правило.

### 3.3 TRIPOD+AI и PROBAST — стандарты отчётности и оценки смещения
🔴 **Только по сниппетам поисковой выдачи и аннотациям PMC; полные тексты в этой сессии
не открывались — дословность не подтверждена.**
- **TRIPOD** (Transparent Reporting of a multivariable prediction model for Individual
  Prognosis Or Diagnosis) — впервые опубликован **2015**, минимальные требования к отчёту
  о разработке или оценке прогностической модели. **TRIPOD+AI (2024)** заменяет чеклист
  2015 года; редакция 2015 «should no longer be used».
- Явная граница применимости, важная для нас: *«The recommendations in TRIPOD+AI are for
  transparently reporting how prediction model research was conducted; **it does not
  prescribe how to develop or evaluate a prediction model. The checklist is not a quality
  appraisal tool.**»* То есть TRIPOD **не даёт права утверждать, что подход верен** — он
  даёт только право утверждать, что мы честно описали, что сделали.
- **PROBAST** (+ разрабатываемый PROBAST+AI) — инструмент **оценки риска смещения**
  и качества прогностических моделей; именно он, а не TRIPOD, отвечает на вопрос «модель
  хорошая или нет».

🔴 Оговорка о переносимости: TRIPOD/PROBAST заточены под модели, **предсказывающие исход**
(диагноз, прогноз), где есть наблюдаемая эталонная метка. Наша модель — **прескриптивная**
(рекомендует действие), эталонной метки у неё нет по конструкции. Значит, TRIPOD переносится
в части отчётности (данные, выборка, обработка пропусков, калибровка, ограничения), но
центральные пункты про «predictive performance» у нас **пустые**, и это надо писать честно,
а не имитировать метриками, которые не про то (см. тему 27).

### 3.4 CONSORT-AI / SPIRIT-AI
🔴 **Не добывалось в этой сессии** — на этот участок бюджет не хватило, поисковых вызовов
по CONSORT-AI/SPIRIT-AI не делалось. Известное из общего канона (**подтвердить перед
использованием**): SPIRIT-AI — расширение для **протоколов** клинических испытаний
с участием ИИ, CONSORT-AI — для **отчётов** о результатах; оба опубликованы в 2020 году
одновременно в Nature Medicine / BMJ / Lancet Digital Health. Практическая ценность для нас
— в требовании заранее описать версию алгоритма, вход, процедуру обработки некорректного
входа и роль человека в контуре.

### 3.5 EU AI Act — попадаем ли мы в высокий риск
Первоисточник по Приложению III добыт (`artificialintelligenceact.eu/annex/3/`, `WebFetch`,
HTTP 200). Пункт **5(b)** дословно:
> "AI systems intended to be used to evaluate the creditworthiness of natural persons or
> establish their credit score, **with the exception of AI systems used for the purpose of
> detecting financial fraud**"

🔴 **Прямой ответ: FINPILOT в 5(b) НЕ попадает** — мы не оцениваем кредитоспособность
и не присваиваем скоринговый балл; мы распределяем уже имеющийся денежный поток
пользователя по его собственным обязательствам и целям. Кредитного решения о человеке
не принимается ни нами, ни третьей стороной на нашем выходе.

🔴 **Но это тонкая грань, и её надо охранять продуктовым решением, а не надеждой.**
По разбору отраслевых комментаторов (🔴 **сниппет, не первоисточник Регламента**),
5(b) толкуется расширительно через Recital 58: модель не обязана быть единственным
решающим звеном — если она выдаёт признак, балл или рекомендацию, на которую затем
действует человек-андеррайтер, система всё равно попадает в 5(b). Отсюда красная линия
для нас: **как только ПДН-оценка или «рекомендованный лимит долга» из FINPILOT начнёт
передаваться кредитору или использоваться в решении о выдаче — мы попадаем в высокий
риск целиком**, со всем контуром (система управления рисками, качество данных,
техдокументация, логирование, человеческий надзор, оценка соответствия). Партнёрская
интеграция с банком — это не бизнес-решение, а смена регуляторного класса.

Практический смысл для рынка РФ: AI Act напрямую на нас не распространяется, но
он — де-факто шаблон, по которому будут писать требования и здесь, и он же — условие
выхода на ЕС (что прямо совпадает с миграционным вектором владельца).

### 3.6 🔴 Аналог в РФ — что есть и распространяется ли на нас
**Прямой ответ: обязательных требований к валидации моделей, распространяющихся на
FINPILOT, в РФ НЕТ — потому что мы не кредитная и не некредитная финансовая организация.**
Всё найденное адресовано поднадзорным ЦБ субъектам.

Что найдено (🔴 по поисковым выдачам и правовым агрегаторам; полные тексты положений
в этой сессии не читались — дословность не подтверждена):
- **Положение Банка России № 716-П от 08.04.2020** «О требованиях к системе управления
  операционным риском в кредитной организации и банковской группе» — модельный риск
  трактуется как **вид операционного риска**, требования в подразделе 4.3.2. Адресат —
  кредитные организации и банковские группы;
- **Указание № 3624-У**, приложение 1, п. 4.2 — определение модельного риска;
- **Положение № 483-П от 06.08.2015** «О порядке расчёта величины кредитного риска
  на основе внутренних рейтингов» — глава 14: банк отражает во внутренних документах
  методологию внутренней валидации и проводит её **не реже одного раза в год**. Это
  ближайший российский аналог SR 11-7 по духу, но он про ПВР-банки и достаточность
  капитала, к нам отношения не имеет;
- 🔴 **Самое релевантное и самое свежее: Методические рекомендации Банка России
  от 16 июня 2026 г. № 3-МР** «По обеспечению информационной безопасности при разработке
  и применении искусственного интеллекта на финансовом рынке». Добыто: карточка ГАРАНТ
  + пресс-релиз ЦБ (`cbr.ru/press/event/?id=32627`) + разбор на Хабре. Адресаты — кредитные
  организации, филиалы иностранных банков, **некредитные финансовые организации**,
  профучастники и субъекты НПС. Это **первый российский документ, систематизирующий риски
  применения ИИ на финрынке**; более 20 мер. По разбору (🔴 пересказ, не дословно):
  требуется контролировать точность и актуальность входных данных при обучении, целостность
  модели, **прозрачность и предсказуемость её работы**, точность выходных данных; для
  операций в автоматическом режиме в критически важных процессах при высоких рисках —
  предусмотреть **«валидацию результатов человеком с возможностью их изменения»**; принцип:
  чем выше риск и цена ошибки, тем меньше автономии у модели.

🔴 Замер каналов по ЦБ: две ссылки `cbr.ru/Crosscut/LawActs/File/7712` и `/9945` скачались
как PDF (244 171 и 357 791 байт, 5 и 21 стр.) и оказались **другими документами** —
методрекомендации по ИБ/операционной надёжности и по тестированию на проникновение
соответственно. Файл самого 3-МР по прямой ссылке в этой сессии не найден.

**Вывод по участку 3 для РФ:** обязательного к исполнению у нас нет ничего. Но 3-МР
задаёт **тон, который будет применён к нам, как только мы станем партнёром поднадзорного
лица**, и его требование «прозрачность и предсказуемость работы модели + человек может
изменить результат» мы можем выполнить дёшево и заранее — это дословно совпадает с нашим
собственным принципом (пользователь редактирует распределение).

## 4. Участок 4. Фундаментальная критика самой идеи

### 4.1 Работает ли финансовое консультирование вообще
Единого мета-анализа «эффект советника на благосостояние клиента» с чистой причинностью
в этой сессии **не найдено**; то, что находится, — набор разнородных оценок, часть из них
отраслевого происхождения (Blanchett & Kaplan «gamma» 1,59 % альфы; ILC-UK «+39 % ликвидных
активов у консультировавшихся»). 🔴 Все эти числа — **сниппеты, наблюдательные корреляции
и отраслевой маркетинг**, к причинности отношения не имеют (самоотбор: к советнику идут
те, кто и так сберегает). В качестве доказательства их использовать нельзя.

Что действительно добыто и является причинным:
**Mullainathan S., Noeth M., Schoar A. «The Market for Financial Advice: An Audit Study»,
NBER WP 17929, март 2012.** Полный текст добыт (`nber.org/system/files/working_papers/
w17929/w17929.pdf`, HTTP 200, PDF 1.6, текст 118 470 байт). Дословно из абстракта:
> "Do financial advisers undo or reinforce the behavioral biases and misconceptions of their
> clients? We use an audit methodology where trained auditors meet with financial advisers
> and present different types of portfolios… **We document that advisers fail to de-bias
> their clients and often reinforce biases that are in their interests.** Advisers encourage
> returns-chasing behavior and push for actively managed funds that have higher fees, even
> if the client starts with a well-diversified, low-fee portfolio."

🔴 Вместе с Foerster et al. (1.3в) это даёт согласованную картину: **эталон, против которого
нас разумно сравнивать, — плохой.** Это критерий Миллера из темы 27 в чистом виде: наивный
бейзлайн здесь не «идеальный советник», а живой советник, который усиливает смещения
клиента и не персонализирует. Планка ниже, чем кажется, и это работает на нас.

### 4.2 🔴 Главная угроза: простое правило может быть не хуже нашего перебора
Gigerenzer G., Brighton H. «Homo Heuristicus: Why Biased Minds Make Better Inferences»,
*Topics in Cognitive Science* 1 (2009), 107–143. **Добыто полностью** (свободная копия
`constable.blog/.../2009-gigerenzer-brighton-homo-heuristicus.pdf`, HTTP 200, PDF 1.3,
37 стр., текст 123 657 байт). Все цитаты ниже — из текста PDF, не из сниппета.

Определение эффекта, дословно:
> "**Less-is-more effects:** More information or computation can decrease accuracy;
> therefore, minds rely on simple heuristics in order to be more accurate than strategies
> that use more information and time."

> "A less-is-more effect… means that minds would not gain anything from relying on complex
> strategies, **even if direct costs and opportunity costs were zero**."

> "Note that the term less-is-more does not mean that the less information one uses, the
> better the performance. Rather, it refers to **the existence of a point at which more
> information or computation becomes detrimental, independent of costs**."

🔴 **Самое опасное для нас место — про взвешивание.** Наш SAW — это в точности «взвесить
и сложить критерии». Гигеренцер бьёт именно туда:
> "In the 1970s, researchers discovered that **equal (or random) weights can predict almost
> as accurately as, and sometimes better than, multiple linear regression** (Dawes, 1979;
> Dawes & Corrigan, 1974; Einhorn & Hogarth, 1975; Schmidt, 1971). Weighting equally is also
> termed **tallying**…"

> "Czerlinski, Gigerenzer, and Goldstein (1999) conducted **20 studies** in which both
> tallying and multiple regression were tested by cross-validation… **Averaged across all
> data sets, tallying achieved a higher predictive accuracy than multiple regression**
> (Fig. 1). Regression tended to overfit the data, as can be seen by the cross-over of
> lines: **it had a higher fit than tallying but a lower predictive accuracy.**"

Из подписи к Fig. 1 (дословно): "Take-the-best is the most frugal, that is, it looks up,
on average, **only 2.4 cues** when making inferences. In contrast, both multiple regression
and tallying look up **7.7 cues** on average… averaged across 20 studies… **the 95%
confidence intervals were ≤ .4 percentage points.**"

🔴 **И самое важное — условия, при которых простое бьёт сложное (дословно):**
> "Early attempts to answer this question indicated that tallying succeeded when **linear
> predictability of the criterion was moderate or small (R² ≤ .5)**, the **ratio of objects
> to cues was 10 or smaller**, and the **cues were correlated** (Einhorn & Hogarth, 1975)."

🔴 **Проверьте нашу задачу по этим трём условиям — она попадает во все три.**
(1) предсказуемость критерия у нас низкая: связь «денежное решение → благополучие»
даёт R² порядка 0,15–0,30 (разд. 2.1), то есть заведомо ≤ 0,5;
(2) число «объектов» (наблюдений на пользователя) к числу критериев у нас мало —
одна анкета на человека против 5+ взвешенных критериев;
(3) критерии у нас **коррелированы между собой** (переплата, срок закрытия долга,
ПДН и остаток резерва — это в значительной мере одна и та же величина в разных проекциях).

Механизм, объясняющий это (дословно, дилемма смещения-дисперсии):
> "achieving a good fit to observations does not necessarily mean we have found a good model,
> and **choosing the model with the best fit is likely to result in poor predictions**."
> "The more flexible the model, the more likely it is to capture not only the underlying
> pattern but unsystematic patterns such as noise."
> "This is an example of how **a biased model can lead to more accurate predictions than an
> unbiased model.**"

### 4.3 1/N против оптимизации — тот же результат в финансах
DeMiguel V., Garlappi L., Uppal R. «Optimal Versus Naive Diversification: How Inefficient
Is the 1/N Portfolio Strategy?», *Review of Financial Studies* 22(5), май 2009, 1915–1953.

🔴 **Полный текст НЕ добыт.** Замеры: `academic.oup.com` — пейволл; SSRN delivery-ссылка
и три зеркала (`gsb.columbia.edu`, `faculty.washington.edu`, dropbox) — вернули **HTML
вместо PDF, коды 404/404/200-HTML**; `r.jina.ai` на Semantic Scholar — 25 407 байт HTML
карточки без полного текста. Числа ниже — **из аннотации и сниппетов поисковой выдачи,
дословность по тексту статьи не подтверждена**:
- оценивались **14 моделей** на **7 эмпирических наборах данных**; ни одна не оказалась
  устойчиво лучше правила 1/N по коэффициенту Шарпа, эквиваленту определённости и обороту;
- «out of sample, **the gain from optimal diversification is more than offset by estimation
  error**»;
- чтобы sample-based mean-variance обошла 1/N на калиброванных к рынку акций США
  параметрах, нужно окно оценки **~3 000 месяцев для 25 активов и ~6 000 месяцев для 50**
  (то есть 250 и 500 лет).

🔴 **Перенос на нашу задачу — и он не механический.** Тема 12 ставила этот вопрос про
портфель; здесь вопрос про **наш перебор 66 альтернатив**. Логика 1/N применима, потому
что источник её силы — **ошибка оценки входов**, а у нас входы оцениваются ничуть не лучше,
чем ожидаемые доходности: горизонт планирования пользователя (тема 34-v2: у 70 % россиян
он «до нескольких месяцев», у нас в модели 12), будущий денежный поток, вероятность
исполнения плана, веса критериев по риск-профилю. Перебор с шагом 10 % по 66 альтернативам
даёт разрешение в тысячные доли рекомендации при входе, известном с точностью в разы.
**Это ровно та ситуация, в которой 1/N выигрывает.**

Честная оговорка в нашу пользу: у нас есть то, чего нет в портфельной задаче, —
**жёсткие инварианты** (остаток ≥ 0, ПДН ≤ 0,40) и **детерминированная арифметика долга**
(Avalanche — не прогноз, а расчёт при известных ставках). Ставки по действующим кредитам
известны точно, а не оцениваются. Значит, часть нашего выигрыша над наивным правилом
не подвержена estimation error вовсе. Но это ровно **та часть, которую даёт Avalanche-фильтр,
а не SAW-свёртка**. И это проверяемо (см. разд. 6).

### 4.4 Почему банки этого не делают — есть ли содержательная причина, кроме конфликта интересов
Тема 10 нашла конфликт интересов. Содержательная причина, найденная здесь, **есть, и она
двойная**:
1. **Модельный риск ложится на банк.** По SR 11-7 (разд. 3.1) любая такая модель
   потребовала бы полного цикла валидации: conceptual soundness + ongoing monitoring +
   outcomes analysis, ежегодный пересмотр, независимая проверка, инвентарь моделей,
   документация «so that parties unfamiliar with a model can understand how the model
   operates». Стоимость этого контура на продукт, который не приносит процентного дохода,
   не окупается.
2. 🔴 **Конечная точка не определена, а значит outcomes analysis невозможен.** SR 11-7
   требует сравнивать выходы модели с фактическими исходами и устанавливать порог:
   «If outcomes fall consistently outside this acceptable range, then the models should be
   redeveloped». Для «оптимального распределения свободного потока» **фактический исход
   не наблюдаем**: нельзя увидеть контрфактическую переплату того же человека без
   рекомендации. Банк, взявший такую модель, получает модель, которую **нельзя валидировать
   по исходам** — то есть постоянный незакрываемый пункт в отчёте валидации. Это
   содержательный, а не корыстный мотив не делать.

🔴 И это же — самая неприятная новость темы 39: **та же проблема есть и у нас.**
Разница только в том, что нас никто не заставляет её признавать.

## 5. ПРЯМОЙ ОТВЕТ: три проверки, дающие право утверждать, что подход верен

Оговорка, без которой список бессмыслен: **ни одна из трёх не доказывает, что мы повышаем
благополучие.** Такое утверждение нам недоступно — конечная точка спорна в самой отрасли
(разд. 1.3а: CFPB против CRR). Три проверки ниже дают право на **более узкое и честное
утверждение**: «наша рекомендация лучше наивной альтернативы по проверяемому промежуточному
исходу, устойчива ко входной неопределённости и не подмешивает произвол разработчика».
Все три исполнимы на наших данных, без пользователей.

### Проверка 1. Турнир против наивных правил (критерий Миллера + требование SR 11-7)
Прогнать на синтетических профилях (нужны сотни, покрывающие сетку: доход × число долгов ×
ставки × размер резерва × риск-профиль) **наш движок против четырёх наивных правил**:
- **N1 — пропорционально остаткам** долга;
- **N2 — равномерно** (1/N по числу назначений: долги, резерв, цели);
- **N3 — «сначала подушка 3 месяца, потом всё в самый дорогой долг»** (правило из
  народных финсоветов, tallying-аналог);
- **N4 — только Avalanche** без SAW-свёртки (весь свободный поток в самый дорогой долг).

Метрика — суммарная переплата и месяц закрытия долгов на горизонте, при **соблюдении
инвариантов** (Rt ≥ 0, ПДН ≤ 0,40).
🔴 **Право утверждать даёт не победа, а её РАЗМЕР и его источник.** Обязательно
разложить преимущество на две части: сколько дал Avalanche-фильтр (детерминированная
арифметика, входы известны точно) и сколько добавила SAW-свёртка **сверх** него, то есть
против N4. Если SAW сверх Avalanche даёт меньше, чем разброс от неопределённости входов
(проверка 2), — верна не наша модель, а её долговое ядро, и продукт надо переформулировать.
Обоснование требования: SR 11-7, «Comparison to alternative theories and approaches should
be included» (разд. 3.1); Gigerenzer, условия less-is-more, в которые мы попадаем по всем
трём пунктам (разд. 4.2); DeMiguel (разд. 4.3).

### Проверка 2. Устойчивость к неопределённости входа (sensitivity analysis по SR 11-7)
Возмутить входы в диапазонах, которые мы **реально** знаем плохо, и посмотреть, меняется ли
рекомендация:
- горизонт планирования: 3 / 6 / 12 месяцев (тема 34-v2: у 70 % россиян — «до нескольких
  месяцев», а у нас в модели 12);
- будущий денежный поток: ±20 % и обрыв дохода на 1 месяц;
- веса критериев риск-профиля: ±25 % от калиброванных;
- ставки по будущим/переменным обязательствам.

🔴 **Порог, объявленный ЗАРАНЕЕ** (иначе это не проверка, а иллюстрация): доля профилей,
где рекомендация переходит в другую «крупную» ячейку (сдвиг распределения ≥ 20 п.п. или
смена приоритетного назначения), должна быть **ниже X %**. X надо назначить до прогона.
Обоснование дословно: «Unexpectedly large changes in outputs in response to small changes
in inputs can indicate an unstable model» (SR 11-7, разд. 3.1).
🔴 Ожидание по имеющимся данным — **нестабильность будет**, особенно по горизонту.
Это и есть вероятный главный результат проверки.

### Проверка 3. Дискриминантная валидность полезности (Кэмпбелл–Фиске, урезанный вариант)
Показать, что SAW-полезность — **не переименованная линейная функция входов**. Регрессия
итоговой полезности на «скучные» предикторы: доход, суммарный остаток долга, средневзвешенная
ставка, размер резерва. Если R² близок к 1 — конструкта нет, есть арифметика, и «свёртка
по взвешенным критериям» ничего не добавляет к трём числам, которые пользователь видит и без
нас. Плюс конвергентная половина: корреляция нашего ранжирования альтернатив с ранжированием
**независимого** (не участвовавшего в калибровке) внешнего движка/эксперта.
🔴 Наши пять раундов калибровки против четырёх движков **этой проверкой не являются**:
там нет разделения между разработкой и критикой, а по SR 11-7 «Incentives to provide
effective challenge… are stronger when there is greater separation of that challenge from
the model development process» (разд. 3.1). 78,63 % согласия — это developmental evidence.

---

## 6. 🔴 Какая проверка ОПРОВЕРГНЕТ подход

Утверждение не пустое: опровергающие исходы существуют, они конкретны и мы можем их
получить на своих данных уже сейчас.

**Опровержение №1 (сильнейшее и самое вероятное).** Если в проверке 1 наивное правило **N4
(чистый Avalanche без SAW)** даёт суммарную переплату, отличающуюся от нашей менее чем
на порог существенности (предлагаю: **< 1 % суммарной переплаты И < 1 месяца** по сроку
закрытия), — то **перебор 66 альтернатив с SAW-свёрткой не оправдан**. Продукт тогда —
не СППР, а хорошо оформленный калькулятор Avalanche с проверкой инвариантов. Это
не катастрофа для бизнеса, но это **опровержение заявленного метода**, и канон v3.0.0
пришлось бы переписывать.

**Опровержение №2.** Если в проверке 2 доля профилей с качественной сменой рекомендации
при возмущении горизонта с 12 на 3 месяца окажется высокой (скажем, > 30 %), — модель
оптимизирует под горизонт, которого у пользователя нет (тема 34-v2). Тогда наш «оптимум»
— артефакт допущения, а не свойство ситуации пользователя.

**Опровержение №3.** Если в проверке 3 R² регрессии полезности на четыре скучных
предиктора > 0,95 — конструкта «полезность распределения» не существует, дискриминантной
валидности нет.

**Опровержение №4 (требует пользователей, поэтому — после запуска).** Если доля исполнения
рекомендации окажется настолько низкой, что ожидаемый эффект на переплату не отличим
от нуля при нашем размере выборки, — рвётся звено 2 цепочки, и всё качество расчёта
не имеет значения. 🔴 Считать размер выборки надо **сразу под эффект в 1/6 литературного**
(DellaVigna & Linos, разд. 1.4), иначе повторим p = 0,162 Commonwealth Bank.

**Чего опровергнуть НЕЛЬЗЯ, и это надо признать.** Утверждение «FINPILOT повышает
финансовое благополучие пользователя» в текущем виде **непроверяемо и потому пустое**:
конечная точка не определена (CFPB против CRR), контрфактический исход того же человека
не наблюдаем (разд. 4.4), а потолок связи «деньги → благополучие» задан извне
на уровне ρ ≈ 0,4–0,6. 🔴 **Рекомендация: убрать это утверждение из формулировок продукта
и заменить проверяемым** — «снижает переплату по долгам при исполнении плана и не нарушает
инварианты платёжеспособности». Первое звучит лучше, второе можно доказать.

---

## 7. Что из отраслевых стандартов выполнить ДО запуска — по приоритету

| # | Что | Откуда требование | Стоимость | Приоритет |
|---|---|---|---|---|
| 1 | **Documentation пакет модели**: назначение, ограничения, ключевые допущения, происхождение весов, описание входов — «so that parties unfamiliar with a model can understand how the model operates, its limitations, and its key assumptions» | SR 11-7 | низкая, текст | 🔴 до запуска |
| 2 | **Явные границы применимости** (для каких профилей модель НЕ даёт рекомендации) + отказ в этих случаях | SR 11-7, «limitations… restrict the scope to a limited set of specific circumstances» | низкая | 🔴 до запуска |
| 3 | **Sensitivity analysis** с заранее объявленным порогом (проверка 2) | SR 11-7 | средняя, наши данные | 🔴 до запуска |
| 4 | **Сравнение с альтернативными подходами** (проверка 1, турнир против наивных) | SR 11-7 «Comparison to alternative theories and approaches should be included» | средняя | 🔴 до запуска |
| 5 | **Теория изменений вместо логической модели**: на каждом переходе — гипотеза «почему» + индикатор + порог | Clark & Anderson 2004 | низкая, но требует решений | 🔴 до запуска |
| 6 | **Человек в контуре с возможностью изменить результат** + прозрачность и предсказуемость выхода | ЦБ РФ 3-МР от 16.06.2026 | у нас уже есть, надо задокументировать | 🟡 до запуска |
| 7 | **Отчёт по TRIPOD+AI (2024)** в применимой части, с честно пустыми пунктами про predictive performance | TRIPOD+AI | средняя | 🟡 к вехе тестирования модели |
| 8 | **Инвентарь моделей + версионирование + план ежегодного пересмотра** | SR 11-7 / 483-П гл. 14 | низкая (у нас SemVer уже есть) | 🟡 до запуска |
| 9 | **Ongoing monitoring / outcomes analysis** с порогом «если исходы устойчиво вне диапазона — модель переразрабатывается» | SR 11-7 | высокая, требует пользователей | 🟢 после запуска |
| 10 | **Независимая проверка (effective challenge) стороной, не участвовавшей в разработке** | SR 11-7 | высокая (нужен человек извне) | 🟢 после запуска, но признать разрыв сейчас |
| 11 | **Красная линия по AI Act 5(b)**: не передавать ПДН-оценку/рекомендованный лимит кредитору | EU AI Act Annex III 5(b) | политика | 🔴 зафиксировать сейчас |

---

## 8. Что не добыто, метод и замеры каналов

### Не добыто
1. **Fleming & DeMets 1996 (Ann Intern Med 125(7):605–613)** — полный текст. `WebFetch`
   на acpjournals.org — антибот; `curl` браузерный UA на PDF — **HTTP 403, 5 785 байт HTML**;
   `r.jina.ai` — **HTTP 200, но 514 байт** со страницей «Performing security verification».
   Препринта 1996 г. не существует. Содержание — по сниппету выдачи, помечено в 2.4.
2. **DeMiguel, Garlappi & Uppal 2009 (RFS 22(5):1915–1953)** — полный текст. Пейволл
   Oxford Academic; три зеркала вернули HTML/404; SSRN delivery-ссылка — HTML;
   `r.jina.ai` на Semantic Scholar — 25 407 байт карточки без текста. Числа (14 моделей,
   7 наборов, 3 000/6 000 месяцев) — из аннотации/сниппетов, помечено в 4.3.
3. **Khashadourian 2024, Financial Planning Review, «Perceptions or behavior? An evaluation
   of CFPB's financial well-being scale using household financial ratios»** — прямо по теме
   участка 2. `WebFetch` Wiley — **HTTP 403**; `r.jina.ai` — **HTTP 200, 514 байт**, капча.
   Exa как независимый канал **недоступен в этой сессии**: вызов
   `mcp__claude_ai_Exa__web_search_exa` вернул «No such tool available» (права правились
   09.09.2026, но список тулов харнесс читает на старте сессии — PIT-035; здесь Exa
   не подключился).
4. **Netemeyer et al. 2018 (JCR 45(1):68–89)** — полный текст, пейволл Oxford Academic.
   Двухконструктная рамка изложена по сниппету, помечено в 2.2.
5. **Campbell & Fiske 1959** — не добывался вовсе, изложен по общему знанию, помечено в 2.3.
6. **CONSORT-AI / SPIRIT-AI** — участок не отработан, поисковых вызовов не делалось (3.4).
7. **Полные тексты 716-П (подраздел 4.3.2), 3624-У прил. 1 п. 4.2, 483-П гл. 14, 3-МР** —
   читались только карточки правовых агрегаторов и пресс-релиз ЦБ. Файл 3-МР по прямой
   ссылке на cbr.ru не найден: `/Crosscut/LawActs/File/7712` и `/9945` — другие документы
   (проверено, 244 171 и 357 791 байт PDF).
8. **Мета-анализ причинного эффекта финсоветника на благосостояние клиента** — не найден;
   есть только наблюдательные и отраслевые оценки, к причинности отношения не имеющие (4.1).

### 🔴 Противоречие между источниками, которое НЕ сглаживается
**CFPB** (Technical Report, 2017) строит и предъявляет субъективную шкалу как измеритель
финансового благополучия, показывая ρ = 0,53…0,64 с валидаторами.
**CRR at Boston College** (WP 2015-3, данные FINRA NFCS 2012) на прямом тесте заключает:
«Subjective financial assessments have become a poor measure of financial well-being»,
потому что субъективная оценка отражает day-to-day и слепа к отдалённым дефицитам,
и «bliss could be the fruit of ignorance».
Оба добыты полными текстами. Разрешить противоречие внутри этой темы не удалось; для нас
следствие практическое — **выбор конечной точки надо делать явно и обосновывать, а не брать
«общепринятую шкалу»**, потому что общепринятой нет.

### Работал ли WebSearch и сколько вызовов
🟢 **WebSearch работал всю сессию без единого отказа.** Сделано **22 вызова** WebSearch.
Пустых выдач на широких запросах не было; признаков исчерпания не наблюдалось.

### Метод поиска
- Классификация запроса: **depth-first** (один вопрос — «верен ли замысел» — с четырёх
  разных ракурсов: программная оценка, психометрика, регуляторика, критика оптимизации).
- **Субагентов — ноль**, по прямому указанию задачи. Вся работа выполнена вахтой
  последовательно; параллелились только независимые вызовы инструментов внутри хода.
- Порядок каналов добычи, применявшийся по каждому источнику: `WebFetch` → `curl`
  с браузерным UA → `r.jina.ai` → (Exa — недоступна) → для PDF `pdftotext -layout`.
- 🔴 **Что реально сработало и стоит запомнить.** Пейволльные статьи брались **не через
  прокси, а через авторские копии**: DellaVigna & Linos — с личной страницы в Berkeley
  (`eml.berkeley.edu/~sdellavi/wp/`), Foerster et al. (JF 2017) — с личной страницы
  Previtero. Оба раза — HTTP 200 и полный PDF там, где издатель отдавал бы пейволл.
  Рескиндованный документ OCC (`occ.gov/static/rescinded-bulletins/`) оказался рабочим
  способом достать текст приложения SR 11-7, когда официальная ссылка ФРС на приложение
  отдала HTML вместо PDF.
- 🔴 **Что НЕ сработало ни разу:** `r.jina.ai` против Cloudflare-капчи издателей
  (acpjournals, Wiley) — оба раза HTTP 200 с телом **514 байт** и текстом «Performing
  security verification». Подтверждает известное: прокси обходит простой антибот,
  но не challenge-страницу и не пейволл. Размер тела — надёжный признак: 514 байт = капча.
- Все числа в разделах 1.4, 2.1, 3.1, 4.1, 4.2 сняты **из текста PDF** (`pdftotext -layout`),
  не из пересказов. Всё, что осталось на уровне сниппета, помечено 🔴 по месту.

---

# ДОБОР 10.09.2026

Повод: при первом прогоне темы 39 агенту **запретили подагентов**, часть работы осталась
недобытой (разд. 8 «Не добыто»). Владелец велел довести до полноты.

Статус добора: **ЗАВЕРШЁН 10.09.2026.** Подагентов — два (последовательно, не веером):
Д.3/Д.4 и Д.6. Разделы Д.0–Д.2 и Д.5 — вахта. Синтез подагенту не поручался.
🔴 WebSearch в сессии недоступен: харнесс вернул «400 of 400 WebSearch calls» на первом
же ходе. Весь поиск шёл через научные API без ключа (OpenAlex / Crossref / Unpaywall /
Semantic Scholar / EuropePMC) — см. Д.5.6.
Порядок чтения: Д.5 (изменения выводов) → Д.1–Д.4, Д.6 (материал).

## Д.0 План добора

Классификация запроса: **depth-first с одной breadth-вставкой**. Один вопрос («верен ли
замысел») углубляется по трём ракурсам (Гигеренцер-первоисточник, фальсифицируемость +
доказательные финансовые интервенции, критика SAW), плюс одна breadth-часть — обзор класса
альтернативных методов (outranking / TOPSIS / satisficing / goal programming).

Подагентов: потолок два (правило 11 проекта). Запускаются **последовательно, по одному**,
не веером — правило 11 требует именно этого; «не более двух» из задания трактуется как
потолок, а не как разрешение на параллель.

Четыре участка добора:
- **Д.1** Гигеренцер: три условия less-is-more по ПЕРВОИСТОЧНИКУ (Einhorn & Hogarth 1975,
  на который Gigerenzer & Brighton только ссылаются) + проверка, попадает ли SAW во все три.
- **Д.2** Фальсифицируемость «повышаем благополучие» + как меряют пользу финсоветов те,
  кто делает это всерьёз (RCT, Campbell Collaboration, What Works); психометрика
  CFPB Financial Well-Being Scale.
- **Д.3** 🔴 Прямые контраргументы против нашего подхода: критика SAW/линейной свёртки
  по существу (компенсаторность, произвол весов, нарушение независимости предпочтений),
  неустойчивость порядка альтернатив (rank reversal).
- **Д.4** Не пропущен ли класс методов лучше нашего: ELECTRE, PROMETHEE, TOPSIS,
  satisficing/aspiration-based, goal programming — чем каждый лучше и хуже SAW именно
  для нашей задачи и для требования объяснимости.
- **Д.5** ИЗМЕНЕНИЯ ВЫВОДОВ: подтвердилось / уточнилось / опровергнуто / осталось
  недобытым + что именно вернул отказ.

Каналы: `WebFetch` → `curl` с браузерным UA → PDF через `pdftotext -layout`.
`r.jina.ai` с нашей сети отдаёт 401 — не пробуется. Exa недоступна (сервер 404).
Российские корневые сертификаты не ставятся (прямой запрет владельца).


---

## Д.3 Прямые контраргументы против SAW/линейной свёртки

Канал добычи по каждому источнику назван по месту. WebSearch в этой сессии недоступен
(бюджет исчерпан), поэтому поиск шёл через OpenAlex API + Crossref + прямые `curl`.

### Д.3.1 Rank reversal: добыто ДОСЛОВНО, и оно бьёт по SAW напрямую

**Источник (добыт полностью, OA, `curl` → HTTP 200, 539 163 байта, 32 страницы, разобран
`pdftotext -layout`):**

> Aires R.F.F., Ferreira L. **«The rank reversal problem in multi-criteria decision making:
> a literature review»**. *Pesquisa Operacional*, 38(2), 2018, pp. 331–362.
> DOI: 10.1590/0101-7438.2018.038.02.0331. PDF: `http://www.scielo.br/pdf/pope/v38n2/1678-5142-pope-38-02-331.pdf`

Обзор 130 статей 1980–2015. Дословно, аннотация, с. 331:

> «Despite the importance of multicriteria decision-making (MCDM) techniques for constructing
> effective decision models, there are many criticisms due to the occurrence of a problem called
> rank reversal.»

Определение явления, с. 331:

> «RR refers to a change in the ordering among alternatives previously defined, after the addition
> or removal of an alternative from the group previously ordered (Lootsma, 1993; Buede & Maxwell,
> 1995; Saaty & Sagir, 2009; Wang & Luo, 2009).»

🔴 **Ключевое для нас — Wang & Luo (2009) распространяют RR на SAW, и обзор это фиксирует
дословно, с. 343:**

> «Wang & Luo (2009) explained (and exemplified) that the RRP occurs not only in the AHP but also
> in many other decision-making methods, such as Borda-Kendall (Kendall, 1962), SAW, TOPSIS,
> and in DEA.»

То же в сводной таблице обзора (с. 361, строка «Wang & Luo (2009)»): «Demonstration of the RRP
in four different [methods]».

**Типология RR (с. 334, дословно, полный список пяти типов):**

> «1. Type #1: the final rank order of the alternatives changes if an irrelevant alternative is
> added to (or removed from) the problem.
> 2. Type #2: the indication of the best alternative changes if a non-optimal alternative is
> replaced by another worse one.
> 3. Type #3: the transitivity property is violated if an irrelevant alternative is added to
> (or removed from) the problem.
> 4. Type #4: the transitivity property is violated if the initial decision-problem is decomposed
> into sub-problems, i. e., for the same decision problem and when the same MCDM method is used,
> the rankings of the smaller problems are in conflict with the overall ranking of the alternatives.
> 5. Type #5: the final rank order of the alternatives changes if a non-discriminating criterion
> is removed from the problem.»

И (с. 334):

> «ordering between two alternatives has changed when an alternative is added or removed and this
> clearly contradicts the principle of the independence of irrelevant alternatives.»

**Контр-свидетельство, которое надо привести честно (с. 342, дословно):**

> «In a similar study, Zanakis et al. (1998) tested the RRP in eight methods: ELECTRE, TOPSIS,
> MEW (Multiplicative Exponential Weighting), SAW (Simple Additive Weighting), and four different
> AHP versions. The results concerning the addition of a new alternative in the problem showed that
> MEW and SAW methods have not produced any rank reversals. This was followed by TOPSIS, the four
> AHP versions and, finally, ELECTRE.»

То есть в эмпирическом симуляционном сравнении восьми методов **SAW оказался среди самых
устойчивых к RR, а ELECTRE — самым неустойчивым.** Обзор тут же оговаривается (с. 342):
«However, given the controversy in the MCDM field about comparing rankings from different methods,
the results of Buede & Maxwell (1995), Zanakis et al. (1998) and others should be interpreted
with caution.»

Ещё одна находка того же исследования, прямо про нас (с. 342, дословно):

> «(i) more rank reversals occurred in problems with more alternatives; (ii) the number of rank
> reversals was influenced less by the number of criteria than by the number of alternatives,
> (iii) more rank reversals were observed under constant weights, and fewer under uniformly
> distributed weights.»

**Что это значит для FINPILOT.**
1. Утверждение «SAW тоже страдает rank reversal» — **подтверждено первоисточником через обзор**,
   это не домысел. Но в отличие от AHP это не системный дефект метода, а следствие **нормировки**:
   если нормировка зависит от состава множества альтернатив (max-нормировка, sum-нормировка,
   векторная), добавление/удаление альтернативы меняет знаменатель и может перевернуть порядок.
2. 🟢 **У нас есть техническая защита, которой нет у типового SAW-приложения.** Наши 66 альтернатив
   — это **фиксированная сетка** (шаг 10 %), а не открытый список кандидатов, который заказчик
   пополняет. Альтернативы не добавляются и не удаляются между прогонами. Rank reversal типа #1
   (добавление/удаление альтернативы) для нас структурно **неприменим**, пока сетка фиксирована.
   Это надо записать в доках модели как явное обоснование, а не оставлять счастливой случайностью.
3. 🔴 **Но применимы типы #2 и #5.** Тип #5 (удаление недискриминирующего критерия меняет порядок)
   для нас реален: если у пользователя нет долгов, критерии «переплата» и «срок закрытия долга»
   становятся недискриминирующими — и их выкидывание, по этой литературе, способно поменять
   порядок оставшихся альтернатив. Проверить тестом: сценарий «нет долгов» с критериями долга
   и без них — совпадает ли рекомендация.
4. Пункт (iii) Zanakis — «больше RR при константных весах, меньше при равномерно распределённых» —
   ложится ровно на наш случай: у нас веса **фиксированы экспертно на риск-профиль**, то есть
   константны. Это указывает не на «поменяйте метод», а на **тест чувствительности**: прогнать
   66 альтернатив при возмущении весов ±10 % и посмотреть, сохраняется ли топ-1.
5. Пункт (i) — «больше альтернатив → больше RR» — против нашей сетки из 66. Аргумент за то, чтобы
   не увеличивать плотность сетки (шаг 5 % дал бы 231 альтернативу) без замера устойчивости.
## Д.1 Гигеренцер: три условия less-is-more — сверка по первоисточнику

### Д.1.1 Канал и что именно добыто
Прежняя ссылка (`constable.blog/...`) **умерла: HTTP 404, тело 60 436 байт HTML**.
Рабочий канал найден заново — репозиторий Института Макса Планка:
`https://library.mpib-berlin.mpg.de/ft/gg/GG_Homo_2009.pdf` → **HTTP 200, 608 639 байт,
PDF 1.3, 37 стр.**; `pdftotext -layout` → 123 657 байт текста (побайтно совпало с прогоном
первой сессии — то есть это тот же файл, добытый другим путём).
Реквизиты со стр. 107 самого PDF: Gigerenzer G., Brighton H. «Homo Heuristicus: Why Biased
Minds Make Better Inferences», *Topics in Cognitive Science* **1 (2009) 107–143**,
DOI 10.1111/j.1756-8765.2008.01006.x.

### Д.1.2 🔴 Три условия — цитата с номером страницы (было требование задания)
**Стр. 112**, абзац сразу под подписью к Fig. 1, дословно:

> "Early attempts to answer this question indicated that tallying succeeded when linear
> predictability of the criterion was moderate or small (R2 £ .5), the ratio of objects to
> cues was 10 or smaller, and the cues were correlated (Einhorn & Hogarth, 1975)."
> — Gigerenzer & Brighton 2009, **с. 112**

Тут же, **на той же стр. 112**, авторы переформулируют те же три условия своими словами —
эта редакция для нас удобнее, потому что называет механизм, а не только пороги:

> "Note that the conditions under which tallying succeeds––low predictability of a criterion,
> small sample sizes relative to the number of available cues, and dependency between
> cues––are not infrequent in natural environments."
> — там же, **с. 112**

Механизм, объясняющий, ПОЧЕМУ это работает (**стр. 125**):

> "The more uncertain the criterion is, or the smaller the sample size available, the more a
> cognitive system needs to protect itself from one kind of error (variance) over the other
> (bias). A biased mind that operates with simple heuristics can thus be not only more
> efficient in the sense of less effort but also more accurate than a mind that bets only on
> avoiding bias. **The specific source of bias we identified lies in ignoring the dependencies
> between cues. The specific environmental structures that this bias can exploit are noisy
> observations and small sample sizes.**"
> — там же, **с. 125**

Числовая рамка результата (подпись к Fig. 1, **стр. 112**), сверено по PDF:
> "Take-the-best is the most frugal, that is, it looks up, on average, only 2.4 cues when
> making inferences. In contrast, both multiple regression and tallying look up 7.7 cues on
> average. The results shown are averaged across 20 studies… For each of the 20 studies and
> each of the three strategies, the 95% confidence intervals were £.4 percentage points."

### Д.1.3 🔴 ПЕРВАЯ ПОПРАВКА: три условия — это НЕ первоисточник Гигеренцера
Гигеренцер и Брайтон **не выводят** эти три условия, а ссылаются на **Einhorn H. J., Hogarth
R. M. «Unit weighting schemes for decision making», *Organizational Behavior and Human
Performance* 13(2), апрель 1975, с. 171–192**, DOI 10.1016/0030-5073(75)90044-6
(реквизиты подтверждены через Crossref API, не по памяти). И формулируют осторожно:
**«Early attempts to answer this question indicated…»** — «первые попытки указывали», а не
«установлено».

🔴 **Полный текст Einhorn & Hogarth 1975 НЕ ДОБЫТ.** Замеры каналов:
- Unpaywall по DOI: `"is_oa": false`, список OA-локаций **пуст** — статья не в открытом
  доступе вовсе, а не «мы не нашли»;
- ScienceDirect прямая PDF-ссылка с браузерным UA — **HTTP 403, тело 1 208 323 байта HTML**
  (антибот-страница, не статья);
- `lamsade.dauphine.fr/mcda/biblio/PDF/EINHORN1975.pdf` — **HTTP 404, 326 байт**;
- CiteSeerX по двум идентификаторам — **HTTP 404, 4 661 и 4 664 байта**;
- препринта 1975 года не существует (до-arXiv эпоха).

**Следствие, которое надо признать:** самый сильный вывод темы 39 в первой редакции стоял
на **цитате из вторичного пересказа**, причём пересказа с оговоркой «первые попытки».
Теперь он стоит на дословной цитате с номером страницы (Д.1.2) — но это цитата
из Гигеренцера **о** Эйнхорне, а не из Эйнхорна. Формулировать надо именно так.

### Д.1.4 🔴 ВТОРАЯ ПОПРАВКА, важнее первой: SAW попадает НЕ во все три условия
Первая редакция (разд. 4.2) утверждала: «Проверьте нашу задачу по этим трём условиям —
она попадает во все три». При сверке с текстом первоисточника это утверждение
**не выдерживает — и разбирается по условиям неодинаково.**

**Что вообще меряет вся эта литература.** Все 20 исследований Czerlinski/Gigerenzer/Goldstein
— это задачи **вывода (inference)**: есть наблюдаемый критерий (доля отсева в школе,
численность города), есть признаки (cues), стратегии сравниваются **по точности предсказания
на отложенной выборке (cross-validation)**. Слова «preference» в содержательном смысле
в статье нет вовсе: `grep` по всему тексту даёт два вхождения, оба посторонние (стр. 130,
134). **Наша SAW — задача не вывода, а агрегирования предпочтений (prescriptive), и
наблюдаемого критерия у неё нет по конструкции** (это же и сказано в разд. 4.4 и 3.3).
Значит, перенос — это **аналогия, а не подстановка в условия**, и так его и надо называть.

Разбор по условиям:

| Условие (с. 112) | Что оно на самом деле требует | Наш случай | Вердикт |
|---|---|---|---|
| (1) `R² ≤ .5` линейной предсказуемости **критерия** | должен существовать наблюдаемый критерий, и его линейная предсказуемость должна быть низкой | наблюдаемого критерия нет; в первой редакции вместо него подставлен ρ(деньги, FWB) ≈ 0,38–0,54 из разд. 2.1 | 🟡 **держится только как аналогия**, не как подстановка |
| (2) отношение «объектов к признакам» ≤ 10 | это про **размер выборки, на которой ОЦЕНИВАЮТСЯ веса**: мало наблюдений → большая ошибка оценки → регрессия переобучается | 🔴 мы **вообще не оцениваем веса из выборки** — они назначены экспертно. Формально условие к нам **неприменимо** | 🔴 **НЕ выполняется в том смысле, в каком сформулировано** |
| (3) признаки коррелированы | между cues есть зависимость, которую tallying игнорирует, и это игнорирование оказывается полезным смещением | наши критерии (переплата, срок закрытия, ПДН, остаток резерва) действительно сильно взаимозависимы | 🟢 **держится** |

🔴 **И вот главное: поправка по условию (2) делает нашу позицию ХУЖЕ, а не лучше.**
Механизм less-is-more (стр. 125) — защита от **дисперсии, порождённой ошибкой оценки весов
по малой выборке**. У нас ошибки оценки нет, потому что оценки нет: веса не выведены
из данных ни по какой выборке вообще. В классификации Дауэса (Dawes R. M., «The robust
beauty of improper linear models in decision making», *American Psychologist* 34(7), 1979,
571–582 — 🔴 **реквизиты по списку литературы Гигеренцера, с. 138; сам текст Дауэса
в этой сессии не добывался**) это **improper linear model** — модель с весами, полученными
неоптимальным способом. Про такие модели известно ровно то, что они бьют клиническую
интуицию; **не известно, что экспертно назначенные веса бьют единичные (равные).**

**Практический перевод.** Вопрос к нам — не «попадаем ли мы в условия Гигеренцера»
(частично не попадаем), а **более узкий, более жёсткий и полностью проверяемый на наших
данных**: даёт ли SAW с пятью откалиброванными наборами весов рекомендацию, отличную
от SAW с **равными весами (tallying)**? Пять раундов калибровки и согласие 78,63 %
(разд. 3.1, 5) обосновывают веса **только** если равные веса дают заметно другой результат.

🔴 **Отсюда конкретная правка проверки 1 (разд. 5): добавить пятое наивное правило.**
**N5 — SAW с равными весами (tallying)**: та же нормировка, тот же перебор 66 альтернатив,
те же инварианты, но все веса равны, риск-профиль игнорируется.
Порог опровержения объявить заранее: если рекомендация N5 совпадает с рекомендацией
откалиброванного SAW более чем на **90 % синтетических профилей** (совпадение = та же
приоритетная статья назначения и расхождение долей < 10 п.п.), то **вся конструкция
риск-профилей и калибровки весов не оправдана** — есть tallying, который проще, устойчивее
и объяснимее. Это дешевле всех трёх проверок разд. 5 и опровергает больше.

Заметить: N5 бьёт по **другому** месту, чем N4 (чистый Avalanche) из разд. 6. N4 проверяет,
нужна ли свёртка вообще; N5 проверяет, нужны ли **веса**. Можно провалить N5 и пройти N4 —
тогда свёртка нужна, а калибровка нет.


### Д.3.2 Произвол весов и нормировки: добыто ДОСЛОВНО, самый сильный удар по нашему методу

**Источник (добыт полностью, OA-препринт из репозитория университета, `curl` → HTTP 200,
484 566 байт, 28 страниц, разобран `pdftotext -layout`):**

> Tofallis C. **«Add or multiply? A tutorial on ranking and choosing with multiple criteria»**.
> *INFORMS Transactions on Education*, 14(3), 2014, pp. 109–119. DOI: 10.1287/ited.2013.0124.
> Добытая копия — авторский working paper Hertfordshire Business School (2014), титул: «Accepted
> for publication in INFORMS Transactions on Education».
> PDF: `https://uhra.herts.ac.uk/id/eprint/11986/1/s153.pdf`
> ⚠️ Номера страниц ниже — по **working paper**, не по журнальной пагинации (в журнале 109–119).

Аннотация, дословно (с. 2 working paper):

> «Simple additive weighting is a well-known method for scoring and ranking alternative options
> based on multiple attributes. However the pitfalls associated with this approach are not widely
> appreciated. For example, the apparently innocuous step of normalizing the various attribute data
> in order to obtain comparable figures leads to markedly different rankings depending on which
> normalization is chosen. When the criteria are aggregated using multiplication such difficulties
> are avoided because normalization is no longer required. This removes an important source of
> subjectivity in the analysis because the analyst no longer has to make a choice of normalization
> type. Moreover, it also permits the modelling of more realistic preference behaviour, such as
> diminishing marginal utility, which simple additive weighting does not provide.»

**(1) Четыре стандартные нормировки дают четыре разных ранжирования одних и тех же данных**
(с. 5, дословно; пример — данные Yoon & Hwang 1995, шесть кандидатов, пять критериев):

> «The key point is that the four normalizations do not agree with each other. Candidate B’s rank
> ranges from third down to last. Whilst candidate E’s rank ranges from last up to second!
> Further examples can be found in Pavlicic (2000), including one case where a candidate comes
> first for one normalization but comes last according to two others!
> There is something clearly unsatisfactory about a method when one of its key steps can be
> arbitrarily chosen and yet leads to different outcomes.»

Тофаллис цитирует Pomerol & Barba-Romero (2000, p. 80), с. 5, дословно:

> «Why then is a method which is so demanding in theoretical assumptions, and so prone to
> influence by arbitrary choices at the time of application, so widely (and sometimes badly) used?»

**(2) Вес НЕ инвариантен: та же цифра веса означает разный обменный курс при разной нормировке**
(с. 7, дословно, с арифметикой автора):

> «If we normalize using ‘divide by the maximum’ and use the given weights of 2/5 and 3/5 we
> obtain: Additive score = 2/5 (X/9) + 3/5 (Y/8) = 0.044X + 0.075Y which implies that 1 year of
> experience is worth about $1.7k, (since 0.075/0.044 = 1.7).
> Using the ‘divide by total’ normalization we get: Additive score = 2/5 (X/10) + 3/5 (Y/11) =
> 0.04X + 0.0545Y which means that 1 year of experience is now worth $0.0545/0.04 = $1.36k!»

И вывод (с. 7, дословно):

> «It is likely that compilers of rankings in popular publications are not aware of the important
> point that different normalizations require different weights. It is not sufficient to ask people
> for weights in isolation; the elicitation procedure needs to take account of how they will
> subsequently be applied.»

**(3) Rank reversal внутри ОДНОЙ нормировки — от удаления заведомо плохих альтернатив** (с. 8,
дословно; пример из Pavlicic 2000, 5 кандидатов, 4 критерия, равные веса):

> «Now suppose that in producing the short-list, candidates D and E were rejected because of their
> very poor scores on attributes 1 and 2 respectively. If the same normalization (divide by the
> maximum) is then carried out on the reduced table (Table 7) we find that the ranking is completely
> reversed, with C coming top, B second and A last!»

Причина названа механически (с. 8, дословно):

> «In this case this effect is explained by noticing that the form of the normalization is
> data-dependent. Each of the four normalizations described above involves dividing the data by
> a number which itself is derived from the data. Hence when some of the data are removed this
> number is altered and leads to different results.»

**Что это значит для FINPILOT.**
🔴 Это **прямое попадание в нашу конструкцию, и опаснее, чем rank reversal из Д.3.1.** Наши веса
«откалиброваны экспертно» — но эксперт называл число, не зная (или не фиксируя), при какой
нормировке оно будет применено. По Тофаллису вес без указания нормировки **не имеет
однозначного смысла**: тот же «0,3 на переплату» задаёт разный обменный курс «рубль переплаты
↔ месяц резерва» в зависимости от того, делим мы на max, на sum, на range или на норму вектора.
Практические следствия, обязательные к исполнению:
1. В `docs/math_model.md` должно быть **явно записано, какая нормировка канон**, и что веса
   привязаны именно к ней. Смена нормировки = перекалибровка весов, а не косметика.
2. Экспертная калибровка весов должна быть **переформулирована в терминах обменного курса**
   («сколько рублей переплаты вы готовы отдать за один месяц резерва»), а не в терминах
   абстрактной «важности от 0 до 1». Это ровно то, чего требует цитата про elicitation procedure.
3. 🟢 Пункт (3) нас **не задевает**: наша сетка из 66 альтернатив фиксирована, короткого списка
   мы не делаем, альтернативы из перебора не выкидываем. Но задевает, если появится
   пред-фильтрация («отбросим заведомо нереалистичные распределения») — такую фильтрацию нельзя
   делать ДО нормировки. Если фильтруем — нормируем по исходным 66, а не по остатку.
4. 🔴 **Диапазонная зависимость.** Если нормируем по max/min наблюдаемых значений внутри
   конкретного пользователя, то у пользователя с одним дешёвым долгом и у пользователя с пятью
   дорогими одинаковый вес даёт разный смысл. Это делает рекомендации несопоставимыми между
   пользователями и ломает возможность сказать «профиль „консервативный“ работает так-то».
   Альтернатива — нормировка по **абсолютной шкале** (фиксированные якоря: ПДН 0…0,40,
   резерв 0…6 месяцев), не по выборке. Это управляемая правка, и она снимает и (1), и (3), и (4).

### Д.3.3 Компенсаторность: добыто ДОСЛОВНО, «linearity trap» и парадокс Корхонена

Тот же Тофаллис, раздел 3.3 «All-rounders overlooked in favour of unbalanced candidates»
(с. 9–10 working paper). Геометрическое доказательство, дословно (с. 9–10):

> «Now the important point is that whatever weights are attached the intermediate point will never
> be chosen! Forcing the line to pass through that point would mean that at least one of the extreme
> points would lie above the line (which therefore does not qualify as a frontier), indicating that
> the extreme point had a higher score. Technically, the intermediate point is said to be
> ‘convex-dominated’ by the other two, but is not strictly dominated by either one of them.
> What this teaches us is that is that a simple additive value function can dismiss candidates which
> may be described as ‘reasonable all-rounders’, even if these may be what the decision maker would
> have preferred. Zeleny (1982) calls this the ‘linearity trap’.»

Далее — Вежбицкий, цитируемый Тофаллисом дословно (с. 10):

> «Wierzbicki (2006) refers to this effect as the Korhonen paradox, due to an example given by
> Pekka Korhonen involving the (hypothetical) choice of a life-partner. He uses this to show that
> a weighted sum ‘tends to promote decisions with unbalanced criteria; in order to obtain a balanced
> solution, we have either to use additional constraints or a nonlinear aggregation scheme’. He
> argues that ‘human preferences have essentially nonlinear character, including a preference for
> balanced solutions, and that any linear approximation of preferences e.g. by a weighted sum,
> distorts them...This is in opposition to the methods taught in most management schools’.»

И эмпирическое подтверждение из практики госзакупок (с. 10, дословно):

> «Wierzbicki (2006) goes on to describe the real life introduction of a public tender law in Poland
> requiring greater transparency in regard to the weights used in aggregating criteria: ‘Organizers
> of the tenders soon discovered that they were forced to select the offer that is cheapest and worst
> in quality, or the best in quality but most expensive’.»

Отдельно — про фиксированный обменный курс (с. 10, дословно):

> «Simple additive weighting implies that there is a fixed trade-off rate between each pair of
> criteria. Moreover this trade-off, or ‘exchange rate’, is assumed to remain the same irrespective
> of the level of the attributes. […] This illustrates the fact that human preference (score)
> functions cannot be assumed to be linear.»

**Что это значит для FINPILOT — это самый серьёзный содержательный контраргумент из найденных.**
🔴 Наша задача — **буквально задача о сбалансированном решении.** 66 альтернатив с шагом 10 % —
это симплекс распределения между тремя назначениями, и его вершины (100 % в долги / 100 %
в резерв / 100 % в цели) — как раз «extreme points» Тофаллиса. Промежуточные «all-rounder»-
распределения вроде 40/30/30 находятся **внутри** выпуклой оболочки. Из геометрии линейной
свёртки следует: **точка, выпукло доминируемая другими, не будет выбрана ни при каких весах.**
Если критериальные оценки на симплексе близки к линейным по долям, наш SAW будет систематически
выдавать **угловые решения** — «всё в долги» или «всё в резерв», — а сбалансированные
распределения не выиграют никогда.

Это **проверяемое эмпирическое утверждение о нашем коде, и его надо проверить прямо**:
прогнать все 66 альтернатив на репрезентативной выборке синтетических профилей и посчитать
**долю случаев, где победитель — вершина или ребро симплекса** (одна или две доли = 0).
- Если доля высокая (скажем, >60 %) — «linearity trap» у нас реализовался, и 66 альтернатив
  делают вид работы: содержательно выбор идёт из 3–6 углов. Тогда SAW нужно менять или чинить.
- Если доля низкая — значит наши критерии **нелинейны по долям** (что правдоподобно: переплата
  по Avalanche убывает нелинейно, а полезность резерва имеет насыщение на 3–6 месяцах),
  и выпуклая доминируемость не срабатывает. Тогда контраргумент нас не задевает, но это надо
  **показать числами**, а не предположить.
🟡 Второе следствие: жёсткие инварианты (Rt ≥ 0, ПДН ≤ 0,40) у нас уже работают как то самое
«additional constraints» из цитаты Вежбицкого — то есть частичная защита от угловых решений
в конструкции уже есть. Но она отсекает недопустимое, а не поощряет сбалансированное.
🟡 Дешёвая штатная починка, не меняющая метод: ввести **вогнутое преобразование** нормированных
оценок перед взвешенной суммой (например, извлечение корня или логарифм). Это ровно
«nonlinear aggregation scheme» Вежбицкого и «мультипликативная свёртка» Тофаллиса —
взвешенное среднее геометрическое есть взвешенная сумма логарифмов. Оно (а) убирает выбор
нормировки как источник произвола, (б) убирает угловое смещение, (в) вводит убывающую предельную
полезность, что для финансов содержательно верно (первый месяц резерва ценнее шестого).
🔴 **Цена — объяснимость.** «Мы сложили баллы с весами» непрофессионал понимает; «мы перемножили
оценки в степенях весов» — нет. Это реальный trade-off, и решать его надо явно: считать
геометрически, а **объяснять** через попарные обменные курсы («вам предложено гасить долг,
потому что рубль сюда сейчас стоит дороже рубля в резерв»), которые из мультипликативной
свёртки извлекаются так же честно, как из аддитивной.
## Д.2 «Повышаем благополучие» — фальсифицируемость и как это меряют всерьёз

### Д.2.1 🔴 Прямой ответ: ЕДИНОЙ принятой операционализации «financial well-being» НЕТ
Это был центральный вопрос добора, и ответ отрицательный — причём подтверждён
рецензируемой сводкой, а не нашим впечатлением.

Первоисточник добыт полностью: Aubrey M., Morin A. J. S., Fernet C., Carbonneau N.
«Financial well-being: Capturing an elusive construct with an optimized measure»,
*Frontiers in Psychology* **13:935284**, опубликовано 12.08.2022, DOI 10.3389/fpsyg.2022.935284.
Канал: `https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2022.935284/pdf`
→ **HTTP 200, 1 025 747 байт PDF**; `pdftotext -layout` → 144 182 байта текста.
Журнал полностью открытый (CC BY), пейволла нет.

**Таблица 1 статьи (стр. 3)** сводит ШЕСТЬ конкурирующих определений FWB — CFPB (2015),
Kempson & Poppe (2017), Muir et al. (2017), Brüggen et al. (2017), Netemeyer et al. (2018),
Sorgente & Lanz (2017, 2019) — и показывает, что они **расходятся по составу измерений**
(income adequacy · life enjoyment · temporal present/future · relativity vs. others ·
control/financial management · cognitive evaluation · emotional evaluation). Ни одно
из шести не покрывает все семь; про Netemeyer прямо сказано: *"No original definition was
proposed by the authors, who relied on definitions provided by others."*

🔴 **Ключевая строка для нас (стр. 3, дословно):**
> "None of these operationalizations considered individuals' **objective** financial situation
> (e.g., income level, net worth, etc.) as the sole, or even as a core, component of FWB.
> Rather, they all emphasized the **multidimensional and subjective** nature of FWB as a state
> encompassing cognitive and affective components."
> — Aubrey et al. 2022, **с. 3**

И там же — прямое признание, что сравнивать результаты между исследованиями нельзя:
> "With the ambiguity surrounding the operationalization of FWB, it is not surprising that FWB
> has been measured in many different ways across studies, **making it hard to compare
> results.**"
> — там же, **с. 3**

И прицельная критика самой шкалы CFPB — она **одномерная**, а поле сошлось на том,
что конструкт многомерен:
> "Among the measures forming the third category (for which psychometric properties are
> reported), **two rely on a one-dimensional structure of FWB (Prawitz et al., 2006; CFPB,
> 2017), which represents a major shortcoming** given the emerging consensus outlined in the
> previous section regarding the multidimensional nature of FWB."
> — там же, **с. 3**

Собственный результат авторов (абстракт, стр. 1) — что даже у более продвинутой
многомерной шкалы MSFWBS факторная структура «acceptable at best», а
> "factor correlations high enough to **question the discriminant validity of the factors**"
— то есть проблема дискриминантной валидности, которую разд. 2.3 ставил как риск ДЛЯ НАС,
в этом поле не решена **и для самих эталонных шкал**. Выборка авторов: n = 454
франкоканадских взрослых; методы — ESEM и bifactor-ESEM.

🔴 **Что это меняет в наших выводах.** Первая редакция (разд. 1.3а, 8) называла противоречие
«CFPB против CRR» и оставляла его нерешённым. Теперь картина точнее и **хуже для идеи
измерять благополучие вообще**: это не спор двух источников, а **отсутствие консенсуса
в поле как таковое** — шесть определений, четыре класса измерителей, эталонная шкала CFPB
критикуется за одномерность, а объективные деньги **никто** не кладёт в ядро конструкта.
Вывод разд. 6 («утверждение „повышаем благополучие“ пустое») от этого **не ослабевает,
а усиливается и меняет основание**: оно пустое не потому, что мы не сумели измерить,
а потому, что **измеряемой величины с согласованным определением не существует**, и любая
наша цифра будет цифрой по одной из шести несогласованных шкал.

### Д.2.2 Как меряют пользу финансовых вмешательств те, кто делает это всерьёз
Ответ: **RCT с заранее заданными ПОВЕДЕНЧЕСКИМИ исходами, эффект в единицах стандартного
отклонения, плюс отношение «стоимость на 1 SD».** Не «благополучие».

Первоисточник добыт полностью: Kaiser T., Lusardi A., Menkhoff L., Urban C. J. «Financial
Education Affects Financial Knowledge and Downstream Behaviors», **NBER Working Paper 27057,
апрель 2020** (журнальная версия — *Journal of Financial Economics* 145(2), 2022,
DOI 10.1016/j.jfineco.2021.09.022, за пейволлом Elsevier).
Канал: `https://www.nber.org/system/files/working_papers/w27057/w27057.pdf` → **HTTP 200,
1 150 808 байт PDF**; `pdftotext -layout` → 91 920 байт текста. Все числа ниже сняты
из текста PDF.

Абстракт, дословно:
> "We study the rapidly growing literature on the causal effects of financial education
> programs in a meta-analysis of **76 randomized experiments with a total sample size of over
> 160,000 individuals**. The evidence shows that financial education programs have, on
> average, positive causal treatment effects on financial knowledge and downstream financial
> behaviors. Treatment effects are economically meaningful in size, similar to those realized
> by educational interventions in other domains, and are **at least three times as large as
> the average effect documented in earlier work**."

Итоговые величины (разд. «findings», дословно):
> "Financial education interventions have sizable effects on both financial knowledge
> (**+0.2 SD units**) and financial behaviors (**+0.1 SD units**)."

Операционализация исхода — пять поведенческих доменов, дословно:
> "These behaviors can be further disaggregated into the following categories: Borrowing,
> (retirement) saving, budgeting and planning, insurance, and remittances."

Объём материала по доменам (дословно):
> "23 studies report 115 treatment effect estimates on **credit behaviors**, and 23 studies
> report 55 treatment effect estimates on **budgeting behavior**. The largest number of
> estimates is on saving behavior, with 54 studies reporting a total of 253 treatment effect
> estimates."

Экономика вмешательства (дословно):
> "Overall, our **cost-effectiveness ratio is $60.40 per person for one-fifth of a standard
> deviation improvement in outcomes**."

### Д.2.3 🔴 Противоречие двух мета-анализов — и оно РАЗРЕШЕНО, в отличие от CFPB/CRR
Fernandes D., Lynch J. G., Netemeyer R. G. «Financial Literacy, Financial Education, and
Downstream Financial Behaviors», *Management Science* **60(8), 2014, 1861–1883**,
DOI 10.1287/mnsc.2013.1849 (🔴 **полный текст НЕ добыт**: Unpaywall/OpenAlex дают
`oa_pdf: None`, OA-локаций нет). Их результат воспроизведён и опровергнут внутри
добытого NBER WP 27057, **дословно оттуда**:

> "Compared to the estimate reported in Fernandes et al. (2014) of **0.018 SD units** (with a
> 95% confidence interval (CI95) from **−0.004 to 0.022**), the weighted average effect in this
> larger sample of recent RCTs is about **3.6 times higher**. The new estimate of the effect
> size, even with the identical assumption of a common true effect, clearly rules out a null
> effect of financial education (**0.065 SD units** with CI95 from 0.043 to 0.089). Thus,
> **one of the main findings of Fernandes et al. (2014) is not confirmed** in this larger
> sample of RCTs."

Причина расхождения названа там же: у Фернандеса было **13 RCT**, у Кайзера — **76**
(«the number of RCTs has grown from just 13 in the Fernandes et al. (2014) review to 76
as of 2019»), и первые 13 были именно теми, где эффекты слабейшие.

🔴 **Урок для нас, и он методологический, а не про финграмотность.** Спор «работает ли
вмешательство» в этой области **разрешается накоплением RCT с поведенческими исходами**,
а не уточнением определений благополучия. Это ровно тот путь, который делает утверждение
опровержимым. Разница между «CFPB против CRR» (не разрешено, разд. 8) и «Fernandes против
Kaiser» (разрешено за 6 лет) — это разница между спором **об определении конструкта**
и спором **о величине эффекта на измеримом поведении**. Мы обязаны переехать из первого
типа спора во второй; в этом и состоит смысл рекомендации разд. 6.

### Д.2.4 🔴 Отрезвляющая деталь, бьющая прямо в наш домен
Наш продукт нацелен на **долговое поведение**. У Кайзера и соавторов именно этот домен —
самый ненадёжный, дословно:
> "the results on **saving behavior and budgeting behavior are the most robust**, while the
> effects on other categories of financial behaviors are less certain due to either fewer
> studies including these outcomes (insurance and remittances) or **high heterogeneity in the
> estimated treatment effects (credit behaviors)**."

То есть по кредитному поведению — 115 оценок из 23 исследований, и всё равно разброс
слишком велик, чтобы говорить о надёжном среднем эффекте. Планировать эффект нашего
продукта на переплату по литературному среднему **нельзя вообще**: в нашем домене
литературного среднего с приемлемой гетерогенностью нет. Это добавляется к правилу
«делить на шесть» из разд. 1.4 (DellaVigna & Linos) — и, в отличие от него, не даёт
даже точки отсчёта.

### Д.2.5 Что даёт право на утверждение — операционализация, пригодная нам
Из добытого выводится конкретная замена «повышаем благополучие», и она **трёхчастная**:
1. **Исход — поведенческий и наблюдаемый у нас в системе**, не опросный: фактическая
   переплата по долгам за горизонт, месяц закрытия долга, доля месяцев с соблюдением
   инвариантов, доля исполнения плана. Домены Кайзера — borrowing и budgeting — это ровно
   наши две статьи.
2. **Эффект в единицах SD и с заранее объявленным порогом**, а не «стало лучше». Ориентир
   величины из литературы: +0,1 SD на поведение — это **весь** средний эффект целой отрасли
   финансового образования; всё, что мы наобещаем сверх, требует отдельного объяснения.
3. **Стоимость на единицу эффекта** ($60,40 за 0,2 SD у Кайзера) — метрика, которую наши
   потенциальные партнёры-банки понимают и которая делает утверждение сравнимым.

🔴 **Чего НЕ добыто по фальсифицируемости.** Первоисточники философии науки в прикладном
приложении (Meehl P. E. «Theoretical risks and tabular asterisks: Sir Karl, Sir Ronald, and
the slow progress of soft psychology», *Journal of Consulting and Clinical Psychology* 46(4),
1978, 806–834, DOI 10.1037/0022-006x.46.4.806) — **не добыт**: OpenAlex даёт `oa_pdf: None`
для всех четырёх записей; `meehl.umn.edu` — **HTTP 403, 5 872 байта**;
`meehl.dl.umn.edu` — **соединение не установлено (код 000)**; два университетских зеркала —
**HTTP 404 (1 231 и 279 байт)**. Поппер в оригинале не искался сознательно: его тезис
общеизвестен и не требует цитаты, а прикладную часть (пороги, заранее объявленные
критерии отказа) мы уже держим на добытом первоисточнике SR 11-7 (разд. 3.1) —
там требование сформулировано операционально: *"If outcomes fall consistently outside this
acceptable range, then the models should be redeveloped."* Для наших целей это сильнее
философской ссылки.

🔴 **Campbell Collaboration / What Works-центры:** отдельных систематических обзоров
по нашей задаче (алгоритмическая помощь в распределении денежного потока домохозяйства)
**не найдено**. Ближайшее и по сути замещающее — мета-анализ Кайзера и соавторов (Д.2.2),
который сам ссылается на три предшествующих мета-анализа: Miller et al. (2015),
Kaiser & Menkhoff (2017), Kaiser & Menkhoff (2020) — 🔴 реквизиты сняты из списка
NBER WP 27057, сами работы не открывались.


### Д.3.4 Независимость предпочтений (Keeney & Raiffa) — НЕ добыто

🔴 **По памяти, не сверено.** Условие, при котором аддитивная функция ценности вообще
законна — *mutual preferential independence* (для детерминированного случая) и *additive
independence* (для лотерей), формулируется в Keeney R.L., Raiffa H. «Decisions with Multiple
Objectives: Preferences and Value Tradeoffs», Wiley, 1976 (переизд. Cambridge UP, 1993).
Дословную формулировку добыть не удалось: книга не OA, а через OpenAlex/Unpaywall
полнотекстовой копии нет. Формулировку **не цитировать как проверенную**, пока не добыта.

Косвенное подтверждение того же в добытом Тофаллисе (с. 10, дословно, приведено выше):
«Simple additive weighting implies that there is a fixed trade-off rate between each pair of
criteria. Moreover this trade-off, or ‘exchange rate’, is assumed to remain the same irrespective
of the level of the attributes.» — это и есть операционная формулировка условия независимости.

**Что это значит для FINPILOT.** Наши критерии взаимозависимы **по построению**, и это видно
без всякой литературы: переплата, срок закрытия долга и ПДН — три проекции одного и того же
графика погашения; резерв и ПДН связаны через денежный поток. Обменный курс «рубль переплаты
↔ месяц резерва» у нас **заведомо не постоянен по уровню**: при нулевом резерве первый рубль
в подушку стоит несопоставимо дороже, чем шестой месяц резерва. То есть предпосылка аддитивности
у нас нарушена не «теоретически», а в самом определении критериев. Это второй, независимый
аргумент за вогнутое преобразование оценок перед свёрткой (см. Д.3.3): оно как раз моделирует
непостоянный обменный курс.

### Д.3.5 «Метод определяет ответ больше, чем данные» — добыто частично

Прямого дословного источника с эмпирикой «N методов на одних данных дают N ранжирований» добыть
в бюджете не удалось. Косвенно это уже покрыто добытым:
- Тофаллис (с. 5): четыре нормировки ОДНОГО метода дают четыре разных ранжирования одних данных
  («Candidate B’s rank ranges from third down to last»). Это сильнее исходного тезиса: расходятся
  не разные методы, а один и тот же метод с разной технической деталью.
- Aires & Ferreira (с. 342): «given the controversy in the MCDM field about comparing rankings
  from different methods, the results […] should be interpreted with caution» — то есть сама
  сопоставимость ранжирований разных методов в литературе считается спорной.

Найденные, но НЕ добытые кандидаты по этой теме (все за Elsevier-пейволлом, см. «не добыто»):
Mohammadi M., Rezaei J. «Ensemble ranking: Aggregation of rankings produced by different
multi-criteria decision-making methods», *Omega* 96 (2020) 102254; Cinelli M. et al.
«Generalised framework for multi-criteria method selection», *Omega* (2018).
🔴 Обе — аннотация/метаданные из OpenAlex, дословность не подтверждена.

---

## Д.4 Пропущенные классы методов: outranking, TOPSIS, satisficing, goal programming

### Д.4.0 Итог раздела вперёд текста

Из четырёх классов **два для нашей задачи проходят мимо** (TOPSIS, ELECTRE/PROMETHEE
в ранжирующих версиях) и **два содержательно сильнее SAW** — reference point / satisficing
и goal programming, — но не как замена, а как **другая постановка задачи**. И ровно эти два
теряют меньше всего в объяснимости, что для нас критерий №1.

### Д.4.1 Outranking: ELECTRE и PROMETHEE

**Что это.** Вместо построения единой шкалы полезности строится **отношение превосходства**
(outranking) попарно между альтернативами: a превосходит b, если достаточно критериев за a
(condorcet-подобное «согласие») и ни по одному критерию b не лучше a настолько, чтобы наложить
**вето** (порог дискордантности). Вводятся три порога: безразличия (q), предпочтения (p) и вето (v).
Ключевое отличие от SAW — допускается **несравнимость** (incomparability): метод имеет право
сказать «эти две альтернативы я не упорядочиваю», вместо того чтобы выдавать полный порядок.

🔴 Первоисточник **НЕ добыт**: Roy B. «The outranking approach and the foundations of ELECTRE
methods», *Theory and Decision*, 31(1), 1991, pp. 49–73, DOI 10.1007/bf00134132 — OpenAlex
сообщает `is_oa: false`, OA-локаций нет; Springer-версия за пейволлом. Описание выше —
🔴 **по памяти, дословность не подтверждена.**
Аналогично не добыт Figueira, Greco, Roy, Słowiński «ELECTRE Methods: Main Features and Recent
Developments» (2010), DOI 10.1007/978-3-540-92828-7_3 — OpenAlex: OA-локаций нет.

**Чем лучше SAW для нашей задачи.**
1. 🟢 **Порог вето — это то, чего у нас нет и чего нам не хватает.** У SAW плохое значение всегда
   компенсируемо. У ELECTRE можно сказать: «какой бы ни была экономия на переплате, вариант,
   оставляющий резерв ниже одного месяца, не может превзойти ни один вариант». Сейчас у нас эту
   роль частично играют жёсткие инварианты (Rt ≥ 0, ПДН ≤ 0,40) — но это **бинарные допуски**,
   а вето — градуированное правило внутри допустимой области.
2. 🟢 **Пороги безразличия.** Разница в 200 ₽ переплаты за 12 месяцев для пользователя не значима,
   а SAW честно её учитывает и может на ней перевернуть выбор между двумя соседними ячейками
   сетки 10 %. Порог q формализует «эти два варианта для меня одно и то же» — и это ровно то,
   что нужно, когда альтернативы отличаются на один шаг сетки.
3. 🟢 **ELECTRE TRI — сортировка по категориям, а не ранжирование.** Для нас это может быть
   **правильнее по постановке**, чем выбор одной альтернативы из 66: вместо «вот единственный
   верный ответ 40/30/30» система говорит «эти 9 распределений — рекомендуемые, эти 20 —
   допустимые, эти 37 — не советуем», и пользователь выбирает внутри рекомендуемой категории.
   Это одновременно и честнее (мы не претендуем на различение неразличимого), и лучше по UX
   (пользователь сохраняет агентность, а это в требованиях продукта прямо записано).

**Чем хуже.**
1. 🔴 **Параметров становится БОЛЬШЕ, а не меньше.** Вместо одного веса на критерий — вес плюс
   q, p, v. Для 4–5 критериев × 5 риск-профилей это 60–100 экспертно калибруемых чисел вместо
   20–25. Наша экспертная калибровка и одни веса-то обосновывает с натяжкой.
2. 🔴 **Эмпирически ELECTRE — худший по устойчивости к rank reversal** из восьми методов
   в добытом Zanakis et al. (1998), см. дословную цитату в Д.3.1 (Aires & Ferreira, с. 342).
   Заменять SAW на ELECTRE ради устойчивости порядка — движение в неверную сторону.
3. 🔴 **Несравнимость — плохой ответ пользователю.** «Мы не можем сказать, что лучше» —
   допустимый вывод для аналитика в инвестиционном комитете и провальный для приложения личных
   финансов, где человек пришёл за одним следующим действием.

**Объяснимость.** 🟡 Смешанная. Правило вето объясняется непрофессионалу **лучше** веса
(«вариант отклонён, потому что оставляет вас без подушки — это не обсуждается»). А процедура
дистилляции ELECTRE III (нисходящая/восходящая, итоговое предпорядковое пересечение) —
объясняется **хуже** всего в этом обзоре. PROMETHEE II чуть лучше: поток предпочтений
φ = φ⁺ − φ⁻ подаётся как «сколько альтернатив этот вариант обыгрывает минус сколько обыгрывают
его», и это человек понимает.

🟢 **Практический вывод для FINPILOT: не менять метод, а заимствовать два элемента.**
(а) градуированное **вето** по резерву и ПДН поверх текущих инвариантов;
(б) **порог безразличия** q — если разрыв SAW-баллов между топ-1 и топ-2 ниже q, показывать
их как равноценные, а не назначать победителя. Оба изменения локальны, сохраняют SAW и чинят
ровно те дефекты, что найдены в Д.3.

### Д.4.2 TOPSIS

**Что это.** Нормировка (обычно векторная), взвешивание, построение идеальной (по всем критериям
лучшие значения) и антиидеальной точки, расчёт евклидовых расстояний d⁺ и d⁻ до них, ранжирование
по относительной близости Rᵢ = d⁻/(d⁺ + d⁻).

🔴 Первоисточник Hwang & Yoon (1981) не добывался (монография, не OA). Упоминание в добытом
обзоре Aires & Ferreira (с. 339, дословно): «by Hwang & Yoon (1981), but a new index called
relative proximity [Rᵢ] is calculated for each […]».

**Чем отличается от SAW по существу — и правда ли даёт новое.**
🔴 **Для нашей задачи — почти ничего нового, и это надо сказать прямо.** Формально TOPSIS
нелинеен (евклидово расстояние), поэтому частично лечит «linearity trap» из Д.3.3: точка,
сбалансированная по критериям, ближе к идеалу, чем крайняя, и может выиграть там, где SAW её
никогда не выберет. Это плюс, и для нас содержательный. Но:
1. 🔴 TOPSIS **не снимает** ни одной из проблем Д.3.2: он тоже требует нормировки, тоже требует
   весов, и его веса так же не инвариантны к выбору нормировки.
2. 🔴 Идеал и антиидеал строятся **по множеству альтернатив**, то есть данные-зависимы — ровно
   механизм rank reversal, описанный Тофаллисом (с. 8, дословно приведено в Д.3.2). У TOPSIS RR
   документирован обильно: Aires & Ferreira отводят ему отдельный раздел, и (с. 348) обсуждают
   «main reasons of RR in TOPSIS». В симуляции Zanakis et al. (1998) TOPSIS дал rank reversal,
   а SAW — нет (дословно, с. 342, см. Д.3.1). **По устойчивости TOPSIS для нас ХУЖЕ SAW.**
3. Есть добытый по метаданным (🔴 аннотация, дословность не подтверждена) специальный разбор:
   Zavadskas E.K. et al. / авторский коллектив, «A comparison between TOPSIS and SAW methods»,
   *Annals of Operations Research*, 2023, DOI 10.1007/s10479-023-05339-w — открыть не удалось,
   см. «не добыто».

**Объяснимость.** 🔴 **Хуже SAW.** «Ваш вариант на 0,73 близок к идеальному по евклидову
расстоянию в нормированном пятимерном пространстве» — не объяснение для пользователя-
непрофессионала. Взвешенная сумма хотя бы разлагается на понятные вклады критериев.

🔴 **Вывод: TOPSIS для FINPILOT не является улучшением. Не переходить.**

### Д.4.3 Satisficing / aspiration-based — 🟢 добыто ДОСЛОВНО, и это лучший кандидат

**Источник (добыт полностью, OA из репозитория IIASA, `curl` → HTTP 200, 7 079 622 байта,
разобран `pdftotext -layout`):**

> Lewandowski A., Wierzbicki A.P. (Eds.) **«Aspiration Based Decision Support Systems: Theory,
> Software and Applications»**. Lecture Notes in Economics and Mathematical Systems, vol. 331.
> Springer-Verlag, Berlin/Heidelberg/New York, 1989. ISBN 3-540-51213-6.
> PDF: `http://pure.iiasa.ac.at/id/eprint/3217/1/XB-89-402.pdf`
> Цитаты ниже — из вводной главы «Theory and Methodology», раздел 3 «The principle of reference
> point optimization in decision support systems (DSS)», сс. 10–12.
> 🔴 Точное авторство главы (редакторы против отдельного автора) по титульным листам не сверено.

Определение satisficing и его связи с aspiration levels (с. 10, дословно):

> «Another rationality framework, called satisficing decision making, was formulated by Simon
> (1969) and further extended by many researchers […] Originally, this approach assumed that human
> decision makers do not optimize, because of the difficulty of optimization operations, because of
> uncertainty of typical decision environment, and because of complexity of the decision situations
> in large organizations. Therefore, this approach was sometimes termed bounded rationality […]»

И (с. 10, дословно) — то, что для нас важнее всего:

> «A very important contribution of the satisficing framework is the observation that decision
> makers often use aspiration levels for various outcomes of decisions; in classical interpretations
> of the satisficing framework, these aspiration levels indicate when to stop optimizing. While more
> modern interpretations might prefer other rules for stopping optimization, the concept of
> aspiration levels is extremely useful for aggregating the results of learning by the decision
> maker: aspiration levels represent values of decision outcomes that can be accepted as reasonable
> or satisfactory by the decision maker and thus are aggregated, adaptable parameters that are
> sufficient for a simple representation of his accumulated experience.»

Механика «квазисатисфисинга» — три типа исходов, дословно (с. 11):

> «One of the basic means of communication of the user with the decision support system is his
> specification of aspiration levels for each objective outcome; these aspiration levels are
> interpreted as reasonable values of objective outcomes. In more complex situations, the user can
> specify two levels for each objective outcome — an aspiration level interpreted as above and
> a reservation level interpreted as the lowest acceptable level for the given objective outcome.»

И (с. 11, дословно) — принцип, который прямо описывает то, чем должна быть наша СППР:

> «the decision support system following the quasisatisficing principle should use this guiding
> information, together with other information contained in the system, in order to propose to the
> user one or several alternative decisions that are best attuned to this guiding information.
> When preparing (generating or selecting) such alternative decisions, the decision support system
> should not impose on the user the optimizing or the satisficing or any other behaviour, but should
> follow the behaviour that is indicated by the types of objective outcomes.»

Три случая ответа системы (сс. 11–12, дословно, сокращённо по началам):

> «Case 1: the user has overestimated the possibilities implied by admissible decisions […] and
> there is no admissible decision such that the values of all objective outcomes are exactly equal
> to their aspiration levels. In this case, however, it is possible to propose a decision for which
> the values of objective outcomes are as close as possible […] to their aspiration levels […]
> Case [2]: the user underestimated the possibilities implied by admissible decisions and there
> exist a decision which results in the values of objective outcomes exactly equal to the specified
> aspiration levels. In this case, it is possible to propose a decision which improves all objective
> outcomes uniformly as much as possible […]
> Case [3]: the user, by a chance or as a result of a learning process, has specified aspiration
> levels there are uniquely attainable by an admissible decision.»

И (с. 12, дословно):

> «In the process of quasisatisficing decision support, all aspiration levels and the corresponding
> decisions proposed by the system have tentative character. If a decision proposed by the system
> is not satisfactory to the user, he can modify the aspiration [levels]»

Отдельно — прямая критика классической утилитаристской постановки, к которой относится и SAW
(с. 9–10, дословно):

> «Therefore, if any approximation of an utility function is used in a decision support system,
> it should be nonstationary in time in order to account for the learning and adaptive nature of
> the decision making process. Such an approximation cannot be very detailed, it must have
> a reasonably simple form characterized by some adaptive parameters that can aggregate the effects
> of learning.»

И претензия к «чёрному ящику» из той же главы (с. 8, дословно):

> «your best decision is as follows". This often helps the user, but not sufficiently: he does not
> know which of his answers is responsible for this particular choice, nor how to change general
> instructions to the system in order to influence the final decision if he does not like it for
> some reason.»

**🔴 Что это значит для FINPILOT — это самый важный вывод всего Д.4.**
Цитата с. 8 — **буквальное описание нашего текущего дефекта**: SAW выдаёт «вот лучшее
распределение», пользователь не знает, какой его ответ (какой вес какого профиля) за это отвечает,
и не знает, как повлиять на итог. Наше собственное продуктовое требование — «человек должен
понять, почему ему предложили именно это, и иметь возможность изменить» — 40 лет назад
сформулировано как **аргумент против** метода нашего класса и **в пользу** aspiration-based.

Далее, наш пользователь **уже мыслит уровнями притязаний**, а не весами. «Хочу подушку
на 3 месяца», «хочу закрыть карту за год», «не хочу платить по долгам больше 25 % дохода» —
это готовые aspiration levels; а наши инварианты (ПДН ≤ 0,40, Rt ≥ 0) — это готовые
**reservation levels** в терминологии Вежбицкого, причём ровно с тем смыслом, который он даёт:
«the lowest acceptable level». То есть **половина конструкции reference point у нас уже
реализована, просто названа иначе.**

🟢 **Реалистичный путь, не выбрасывающий SAW.** Reference point и SAW не взаимоисключающи:
достижение уровня притязаний по каждому критерию считается **частной achievement-функцией**
(растёт до 1 при достижении aspiration, ниже — падает, ниже reservation — резко штрафуется),
а затем эти частные достижения сворачиваются. Наша SAW-свёртка остаётся **механизмом свёртки**,
а меняется **что именно сворачивается**: не «нормированная оценка критерия», а «насколько
достигнута ваша собственная цель». Это одним ходом:
- убирает произвол нормировки (Д.3.2) — шкала задаётся не выборкой, а парой
  (reservation, aspiration) пользователя;
- вводит нелинейность и лечит «linearity trap» (Д.3.3) — achievement-функция кусочно-линейна
  с изломом в точке притязания, вогнута сверху;
- радикально улучшает объяснимость: «мы предложили гасить долг, потому что ваша цель
  „закрыть карту за год“ при этом достигается на 100 %, а подушка — на 80 % от вашей же цели
  в 3 месяца»;
- 🔴 и требует спросить у пользователя цели по каждому критерию. Это цена: новый экран,
  новые обязательные поля. Но у нас продукт **и так** про цели — они уже третье назначение
  денежного потока.

**Объяснимость.** 🟢 **Лучшая из всех рассмотренных классов.** Объяснение формулируется
целиком в словах пользователя, без слова «вес», «нормировка» и «баллы».

### Д.4.4 Goal programming (Charnes & Cooper), включая лексикографический вариант

**Что это.** Задача формулируется не как максимизация свёртки, а как **минимизация отклонений**
от заданных целей: для каждой цели вводятся переменные недо- и перевыполнения (d⁻, d⁺), жёсткие
требования остаются ограничениями, а целевая функция минимизирует взвешенную сумму отклонений
(weighted GP) либо оптимизирует отклонения **по приоритетным уровням** — сначала полностью
цель первого приоритета, и только среди её оптимумов цель второго (lexicographic / preemptive GP).

🔴 Первоисточник **НЕ добыт** (Charnes A., Cooper W.W. «Management Models and Industrial
Applications of Linear Programming», Wiley, 1961; и Charnes & Cooper 1977 «Goal programming
and multiple objective optimizations», *EJOR* 1(1), 39–54). Обзор Jones D., Tamiz M. «Goal
Programming: realistic targets for the near future», *Journal of Multi-Criteria Decision Analysis*
16(5–6), 2009 — Wiley отдал **HTTP 403, 5 802 байта** и `WebFetch`-у, и `curl` с браузерным UA.

🟢 **Но добыто дословное свидетельство о GP из первоисточника смежной школы** — в том же томе
IIASA, и это ценнее общего обзора, потому что там сразу назван **дефект** GP (с. 21, дословно):

> «This constitutes a drawback of many decision support systems based on goal programming
> techniques (Charnes and Cooper, 1975, Ignizio, 1978) that impose on the user the unmodified
> satisficing rationality and stop optimization upon reaching given aspirations, called goals
> in this case.»

И (с. 11, дословно) — точная граница между GP и reference point:

> «This means that the decision support system should optimize when at least one objective outcome
> is specified as minimized or maximized and should satisfice (stop optimizing upon reaching
> aspiration levels) when all objective outcomes are specified as stabilized. The later case
> corresponds actually to the technique of goal programming, see e.g. Ignizio (1978), hence the
> quasisatisficing decision support can be also considered as a generalization of this technique.»

**Чем лучше SAW для нашей задачи.**
1. 🟢 **Структура задачи совпадает буквально.** У нас есть жёсткие ограничения (Rt ≥ 0,
   ПДН ≤ 0,40) и мягкие цели (переплата, срок, резерв). GP — единственный из рассмотренных
   классов, который **изначально построен на этом разделении**, а не приделывает ограничения
   сбоку к скоринговой процедуре.
2. 🟢 **Лексикографический вариант снимает произвол весов вообще.** Вместо «резерв весит 0,3»
   — «сначала выйти из зоны ПДН > 0,40, потом набрать месяц подушки, потом гасить дорогой долг,
   потом копить на цель». Это **приоритеты, а не веса**, и они не зависят ни от нормировки,
   ни от диапазонов шкал — то есть вся критика Д.3.2 к ним не применима.
3. 🟢 **Это ровно то, как звучит реальный финансовый совет.** «Сначала подушка на месяц, потом
   гасите карту, потом инвестируйте» — общепринятая последовательность в популярных финансовых
   методиках; лексикографический GP — её точная математическая форма.
4. 🟢 Не нужен перебор 66 альтернатив: это оптимизационная задача, решаемая напрямую (для
   линейных критериев — LP). Побочно снимает и пункт (i) Zanakis «больше альтернатив → больше RR».

**Чем хуже.**
1. 🔴 Дефект, названный Вежбицким дословно выше: GP **останавливается на достижении цели**.
   Если пользователь поставил «подушка 3 месяца» и она достижима с запасом, GP не станет
   набирать 4 месяца, даже когда это бесплатно. Для финансов это реальный вред, а не педантизм.
   Лечится ровно тем, что предлагает Вежбицкий — reference point вместо чистого GP, где после
   достижения aspiration функция продолжает расти (Case 2 выше). То есть **Д.4.3 доминирует
   Д.4.4**: reference point есть обобщение GP, снимающее его главный дефект. Это сказано
   в добытом тексте прямым текстом («can be also considered as a generalization of this technique»).
2. 🔴 Лексикографика **безжалостна к почти-равенству**: приоритет 1 удовлетворяется полностью,
   даже если стоит катастрофически дорого по приоритету 2. Нужны пороги «достаточно близко»,
   а это возвращает калибровку параметров.
3. 🟡 Переход на GP означает отказ от сетки 66 альтернатив, а с ней — от возможности показать
   пользователю **соседние варианты** («а если бы 50/30/20?»). Для объяснимости это потеря.

**Объяснимость.** 🟢 **Очень высокая — у лексикографического варианта, вероятно, наивысшая
из всех.** «Сначала это, потом это, потом это» — понятная человеку форма, требующая нуля
математической подготовки, и она же прозрачно редактируема (переставь приоритеты).
🔴 У weighted GP объяснимость такая же, как у SAW, и все те же проблемы с весами.

### Д.4.5 Применения к личным финансам — 🔴 ОТРИЦАТЕЛЬНЫЙ РЕЗУЛЬТАТ

Поиск в OpenAlex (`multi-criteria decision personal finance household debt repayment strategy`,
фильтр `is_oa:true`, 6 верхних результатов) не дал **ни одной** работы, применяющей MCDM
(SAW, ELECTRE, PROMETHEE, TOPSIS, GP, reference point) к распределению денежного потока
домохозяйства или к выбору стратегии погашения долга. Выдача целиком ушла в **экономику
домохозяйств без MCDM**: «Financial literacy and over-indebtedness in low-income households»
(IRFA 2016), «Debt as a source of financial stress in Australian households» (2005),
«Household Finance» (Campbell, NBER w12149, 2006), «The economics of small business finance»
(JBF 1998). Ни одна не про метод принятия решения.

Единственное найденное пересечение MCDM с финансами — **портфельные задачи**:
«A PROMETHEE-based approach to portfolio selection problems», *Computers & Operations Research*,
2011 (🔴 аннотация, дословность не подтверждена; SD отдал 403). Это институциональные инвестиции,
не личный денежный поток.

**Что это значит для FINPILOT.**
🟢 **Это важный положительный сигнал по новизне и его надо зафиксировать в формулировке новизны
продукта/ВКР-наследия:** MCDM-подход к активному распределению свободного денежного потока
домохозяйства (долги / резерв / цели) в найденной OA-литературе **не описан**. Мы не переизобретаем
чужое решение.
🔴 **И одновременно это предупреждение:** отсутствие применений означает и отсутствие
**внешнего бенчмарка**. Проверить нашу модель «против опубликованного эталона» не получится —
эталона нет. Значит, единственный доступный способ валидации — сравнение с **экспертными
решениями** (что и делается в независимом-исследователе-режиме, ритуал §12) и внутренняя
проверка инвариантов и устойчивости. Это надо записать как принятое ограничение, а не как
недоделку.
🔴 Оговорка о добросовестности: отсутствие результатов в OpenAlex по одному набору запросов —
**не доказательство отсутствия работ**. WebSearch в этой сессии недоступен, Google Scholar
не опрашивался, русскоязычная литература (eLibrary, КиберЛенинка) не проверялась вовсе.
Вывод «не описано» имеет силу «не найдено доступными каналами», не более.

### Д.3–Д.4: не добыто

| Источник | Канал | Что вернул инструмент |
|---|---|---|
| Wang Y.-M., Luo Y. «On rank reversal in decision analysis», *Mathematical and Computer Modelling* 49(5–6), 2009, 1221–1229 | `curl` UA → ScienceDirect PDF (OpenAlex дал его как OA) | **HTTP 403**, тело 1 207 967 байт — это HTML-страница блокировки, не PDF (`file`: HTML document). Содержание известно только пересказом Aires & Ferreira (добыт дословно) |
| Roy B. «The outranking approach and the foundations of ELECTRE methods», *Theory and Decision* 31(1), 1991, 49–73 | OpenAlex → Unpaywall | `is_oa: false`, OA-локаций нет вовсе. Пейволл Springer, авторской копии не найдено |
| Figueira, Greco, Roy, Słowiński «ELECTRE Methods: Main Features and Recent Developments» (2010), DOI 10.1007/978-3-540-92828-7_3 | OpenAlex | `best_oa_location: null` |
| Keeney R.L., Raiffa H. «Decisions with Multiple Objectives», 1976 — формулировка mutual preferential independence | OpenAlex, Unpaywall | Монография, полнотекстовых OA-копий нет. Условие изложено 🔴 по памяти |
| Jones D., Tamiz M. «Goal Programming: realistic targets for the near future», *JMCDA* 16(5–6), 2009 | `curl` UA → Wiley `pdfdirect` | **HTTP 403**, тело 5 802 байта (HTML-заглушка) |
| Wierzbicki A.P. «A mathematical basis for satisficing decision making», *Mathematical Modelling* 3(5), 1982, 391–405 | `curl` UA → ScienceDirect (OpenAlex: OA) | **HTTP 403**, тело 1 207 962 байта, HTML-заглушка. Идеи покрыты добытым томом IIASA 1989 |
| «A comparison between TOPSIS and SAW methods», *Annals of Operations Research*, 2023, DOI 10.1007/s10479-023-05339-w | `curl` UA → `link.springer.com/content/pdf/...` | **HTTP 200, но 3 038 байт HTML**, не PDF — редирект на страницу проверки |
| Mohammadi M., Rezaei J. «Ensemble ranking», *Omega* 96 (2020) 102254 | OpenAlex → Unpaywall | OA-локации: ScienceDirect (403-класс) и `resolver.tudelft.nl` (не пробовался, бюджет исчерпан) — 🔴 остаётся добываемым, TU Delft обычно отдаёт |
| Cinelli et al. «Generalised framework for multi-criteria method selection», *Omega*, 2018 | OpenAlex | pdf-ссылка ведёт на ScienceDirect (403-класс), не пробовалась |
| Tofallis, журнальная пагинация *ITE* 14(3), 109–119 | — | Добыт **working paper**, не вёрстка журнала. Номера страниц в цитатах — по working paper, и это помечено по месту |
| CORE API поиск | `api.core.ac.uk/v3/search/works` | **HTTP 500**, `"abstract is not a searchable field"` — API-ошибка, не отказ доступа |
| CORE веб-поиск | `curl` UA → `core.ac.uk/search` | **HTTP 403**, 5 735 байт |


## Д.6 Добор источников из раздела «НЕ ДОБЫТО»

Прогон 10.09.2026, отдельный агент. Задача — дословный текст, а не пересказ. WebSearch недоступен
(бюджет сессии исчерпан), добыча через OpenAlex / Crossref / Unpaywall / EuropePMC / Semantic Scholar
API и прямой `curl`. Каждый отказ фиксируется с URL, кодом HTTP и размером тела.

### Д.6.1 CONSORT-AI и SPIRIT-AI (2020) — ДОБЫТО ДОСЛОВНО

**Реквизиты (подтверждены через OpenAlex, DOI резолвится):**

- Liu X., Cruz Rivera S., Moher D., Calvert M. J., Denniston A. K. and The SPIRIT-AI and CONSORT-AI
  Working Group. «Reporting guidelines for clinical trial reports for interventions involving artificial
  intelligence: the CONSORT-AI extension». *Nature Medicine*, vol. 26, September 2020, pp. 1364–1374.
  DOI 10.1038/s41591-020-1034-x. PMID 32908283.
  Одновременная публикация в *BMJ* 2020;370:m3164 (DOI 10.1136/bmj.m3164) и *The Lancet Digital Health*
  (DOI 10.1016/S2589-7500(20)30218-1) — три журнала, один текст.
- Cruz Rivera S., Liu X., Chan A.-W., Denniston A. K., Calvert M. J. and The SPIRIT-AI and CONSORT-AI
  Working Group. «Guidelines for clinical trial protocols for interventions involving artificial
  intelligence: the SPIRIT-AI extension». *Nature Medicine*, vol. 26, September 2020, pp. 1351–1363.
  DOI 10.1038/s41591-020-1037-7. PMID 32908284.
  Одновременно в *BMJ* 2020;370:m3210 и *The Lancet Digital Health* (DOI 10.1016/S2589-7500(20)30219-3).

**Канал добычи (успех):** `curl -sL` с браузерным UA →
`https://www.nature.com/articles/s41591-020-1034-x.pdf` → HTTP 200, 1 101 432 байта, `application/pdf`,
`file`: PDF version 1.4, 46 страниц. То же для SPIRIT: `.../s41591-020-1037-7.pdf` → HTTP 200,
1 099 791 байт, PDF 1.4, 48 страниц. Разбор — `pdftotext -layout`. Открытый доступ, пейволла нет.
Зеркала-дубли (тоже HTTP 200): `https://pure-oai.bham.ac.uk/ws/files/108551837/s41591_020_1034_x.pdf`
(1 075 301 байт) и `.../305723447/RiveraSC2020Guidelines.pdf` (661 301 байт).

**Назначение расширений — дословно, аннотация CONSORT-AI, с. 1364:**

> «The CONSORT-AI (Consolidated Standards of Reporting Trials–Artificial Intelligence) extension
> is a new reporting guideline for clinical trials evaluating interventions with an AI component.
> It was developed in parallel with its companion statement for clinical trial protocols: SPIRIT-AI
> (Standard Protocol Items: Recommendations for Interventional Trials–Artificial Intelligence).
> Both guidelines were developed through a staged consensus process involving literature review
> and expert consultation to generate 29 candidate items, which were assessed by an international
> multi-stakeholder group in a two-stage Delphi survey (103 stakeholders), agreed upon in a two-day
> consensus meeting (31 stakeholders) and refined through a checklist pilot (34 participants).
> The CONSORT-AI extension includes 14 new items that were considered sufficiently important for AI
> interventions that they should be routinely reported in addition to the core CONSORT 2010 items.
> CONSORT-AI recommends that investigators provide clear descriptions of the AI intervention,
> including instructions and skills required for use, the setting in which the AI intervention is
> integrated, the handling of inputs and outputs of the AI intervention, the human–AI interaction
> and provision of an analysis of error cases.»

**Аннотация SPIRIT-AI, с. 1351 (дословно, ключевое отличие — протокол, не отчёт):**

> «The SPIRIT-AI (Standard Protocol Items: Recommendations for Interventional Trials–Artificial
> Intelligence) extension is a new reporting guideline for clinical trial protocols evaluating
> interventions with an AI component. … Both guidelines were developed through a staged consensus
> process involving literature review and expert consultation to generate 26 candidate items, which
> were consulted upon by an international multi-stakeholder group in a two-stage Delphi survey
> (103 stakeholders), agreed upon in a consensus meeting (31 stakeholders) and refined through a
> checklist pilot (34 participants). The SPIRIT-AI extension includes 15 new items that were
> considered sufficiently important for clinical trial protocols of AI interventions.»

Числа, которые стоит держать точными: **CONSORT-AI — 14 новых пунктов, SPIRIT-AI — 15**; кандидатных
пунктов 29 и 26 соответственно; один и тот же консенсусный процесс (Delphi 103 → встреча 31 → пилот 34).

**Пункты чеклиста, релевантные FINPILOT — дословно, CONSORT-AI, Table 1, с. 1367
(раздел Interventions, ядро CONSORT item 5), и параллельные SPIRIT-AI, Table 1, с. 1353 (item 11a):**

| CONSORT-AI (отчёт) | SPIRIT-AI (протокол) |
|---|---|
| «CONSORT-AI 5 (i) Extension — State which version of the AI algorithm was used.» | «SPIRIT-AI 11a (i) Extension — State which version of the AI algorithm will be used.» |
| «CONSORT-AI 5 (ii) Extension — Describe how the input data were acquired and selected for the AI intervention.» | «SPIRIT-AI 11a (ii) Extension — Specify the procedure for acquiring and selecting the input data for the AI intervention.» |
| «CONSORT-AI 5 (iii) Extension — Describe how poor quality or unavailable input data were assessed and handled.» | «SPIRIT-AI 11a (iii) Extension — Specify the procedure for assessing and handling poor-quality or unavailable input data.» |
| «CONSORT-AI 5 (iv) Extension — Specify whether there was human–AI interaction in the handling of the input data, and what level of expertise was required of users.» | «SPIRIT-AI 11a (iv) Extension — Specify whether there is human–AI interaction in the handling of the input data, and what level of expertise is required for users.» |
| «CONSORT-AI 5 (v) Extension — Specify the output of the AI intervention» | «SPIRIT-AI 11a (v) Extension — Specify the output of the AI intervention.» |
| «CONSORT-AI 5 (vi) Extension — Explain how the AI intervention’s outputs contributed to decision-making or other elements of clinical practice.» | «SPIRIT-AI 11a (vi) Extension — Explain the procedure for how the AI intervention’s output will contribute to decision-making or other elements of clinical practice.» |

Плюс два пункта уровня отбора и площадки (CONSORT-AI, Table 1, с. 1367):

> «CONSORT-AI 4a (ii) Extension — State the inclusion and exclusion criteria at the level of the
> input data.»
> «CONSORT-AI 4b Extension — Describe how the AI intervention was integrated into the trial setting,
> including any onsite or offsite requirements.»

И пункт про ошибки (CONSORT-AI, Table 1, продолжение, раздел Results / item 19, с. 1368; в аннотации
он назван «provision of an analysis of error cases»):

> «… performance errors and how errors were identified, where no such analysis was planned or done,
> explain why not.»

Диаграмма потока участников (CONSORT-AI Fig. 1, с. 1369) добавляет отдельную ветку отсева, дословно:
«Assessed for eligibility at input data level» и «Missing or inadequate input data (n = )».

Явно **исключённое** решение группы, с. 1372 (дословно, важно для нас — снимает соблазн ссылаться на
CONSORT-AI как на норму для самообучающихся систем):

> «… as ‘continuously adapting’ or ‘continuously learning’ AI systems) … agreed that this be excluded
> from CONSORT-AI. These are AI [systems that] may cause changes in performance over time. The group
> noted [that this was] … without tangible examples in healthcare applications, and [may be
> revis]ited in future iterations of CONSORT-AI.»

*(последняя цитата собрана из двухколоночного PDF, склейка колонок обозначена скобками; смысл —
непрерывно обучающиеся системы намеренно вынесены за рамки CONSORT-AI 2020.)*

**Что это меняет для FINPILOT.** CONSORT-AI/SPIRIT-AI — готовый, отраслевой и уже консенсусный
скелет протокола валидации нашей СППР, и он ложится на неё почти пункт-в-пункт: 5(i) → версия
матмодели (`docs/math_model.md`, v3.x) фиксируется в протоколе и в каждом отчёте о прогоне;
5(ii)/4a(ii) → критерии отбора **входных данных** (анкета доходов/расходов/долгов) отдельно от
критериев отбора **пользователей**; 5(iii) → поведение при неполном или недостоверном вводе — это
прямое требование, а не наша перестраховка; 5(iv) → мы обязаны заявить уровень человека в контуре
(пользователь без финансового образования) как параметр исследования; 5(v)/5(vi) → выход SAW-свёртки
(распределение свободного потока) и то, как именно он влияет на решение пользователя; item 19 →
заранее спланированный **анализ случаев ошибки** (нарушение инвариантов «остаток ≥ 0» и «ПДН ≤ 0,40»,
расхождение прогноза SES+Монте-Карло с фактом на горизонте 12 мес.). Отдельно: расширения намеренно
**не покрывают** непрерывно обучающиеся системы — значит ссылаться на них можно только пока модель
детерминирована и версионирована, что для нашей v3.x верно.

### Д.6.2 Campbell & Fiske 1959 — ДОБЫТО ДОСЛОВНО (полный текст статьи)

Campbell D. T., Fiske D. W. «Convergent and discriminant validation by the multitrait-multimethod
matrix». *Psychological Bulletin*, 56(2), 1959, pp. 81–105. DOI 10.1037/h0046016.

**Канал добычи (успех):** `curl -sL` с браузерным UA →
`https://www2.psych.ubc.ca/~schaller/528Readings/CampbellFiske1959.pdf` → HTTP 200, **1 654 879 байт**,
`application/pdf`, 26 страниц. Разбор `pdftotext -layout`, сверено построчно по извлечённому тексту.
Отказы до этого: `https://www.uv.es/friasnav/CampbellFiske.pdf` → код `000`, 0 байт (соединение не
установлено, таймаут).

**Четыре правила чтения MTMM-матрицы — дословно, с. 82–83:**

> «In terms of this diagram, four aspects bear upon the question of validity. **In the first place,
> the entries in the validity diagonal should be significantly different from zero and sufficiently
> large to encourage further examination of validity. This requirement is evidence of convergent
> validity.** Second, a validity diagonal value should be higher than the values lying in its column
> and row in the heterotrait-heteromethod triangles. That is, a validity value for a variable should
> be higher than the correlations obtained between that variable and any other variable having neither
> trait nor method in common. This requirement may seem so minimal and so obvious as to not need
> stating, yet an inspection of the literature shows that it is frequently not met, and may not be met
> even when the validity coefficients are of substantial size.» (с. 82–83)

> «A third common-sense desideratum is that a variable correlate higher with an independent effort to
> measure the same trait than with measures designed to get at different traits which happen to employ
> the same method. For a given variable, this involves comparing its values in the validity diagonals
> with its values in the heterotrait-monomethod triangles.» (с. 83)

> «A fourth desideratum is that the same pattern of trait interrelationship be shown in all of the
> heterotrait triangles of both the monomethod and heteromethod blocks.» (с. 83)

> «**The last three criteria provide evidence for discriminant validity.**» (с. 83)

Определение независимости методов, отделяющее валидность от надёжности — дословно, с. 83:

> «Reliability is the agreement between two efforts to measure the same trait through maximally similar
> methods. Validity is represented in the agreement between two attempts to measure the same trait
> through maximally different methods.» (с. 83)

И почему дискриминантная половина обязательна, дословно, с. 84:

> «When a dimension of personality is hypothesized, when a construct is proposed, the proponent
> invariably has in mind distinctions between the new dimension and other constructs already in use.
> One cannot define without implying distinctions, and the verification of these distinctions is an
> important part of the validational process.» (с. 84)

Отдельно — эмпирическое наблюдение авторов, что третье требование в реальных данных обычно не
выполняется (это важно для калибровки наших ожиданий), дословно, с. 83:

> «For variables Ai, Bi, and Ci, this requirement is met to some degree. For the other variables,
> A2, A3 etc., it is not met and this is probably typical of the usual case in individual differences
> research…» (с. 83)

**Что это меняет для FINPILOT.** Требование к валидации нашей рекомендации становится
двусторонним и проверяемым числами, а не «эксперты согласились». Конвергентная половина: оценка
одного и того же профиля пользователя двумя **максимально разными** методами (наш SAW-рейтинг
альтернатив против независимого экспертного распределения того же свободного потока) должна давать
корреляцию значимо выше нуля. Дискриминантная половина — три оставшихся правила, и она у нас пока
нигде не заявлена: (а) согласие «SAW против эксперта по одному профилю» обязано быть выше, чем
согласие «SAW по профилю X против эксперта по профилю Y»; (б) оно обязано быть выше, чем согласие
двух наших **собственных** метрик по разным профилям — иначе мы меряем метод (сам SAW и его веса),
а не финансовое положение пользователя; (в) картина различий между риск-профилями должна
воспроизводиться и в экспертной разметке, и в нашей. Третье правило Кэмпбелла–Фиске — прямой тест
на «method variance»: если наши 5 риск-профилей коррелируют между собой сильнее, чем каждый с
внешней оценкой, профили не различают то, что заявлено. Сами авторы предупреждают, что именно это
требование в реальных данных чаще всего проваливается — то есть закладывать его в план валидации
надо заранее, а не как формальность.

### Д.6.3 DeMiguel, Garlappi & Uppal 2009 — ОТКАЗ, ПОЛНЫЙ ТЕКСТ НЕ ДОБЫТ

DeMiguel V., Garlappi L., Uppal R. «Optimal Versus Naive Diversification: How Inefficient Is the 1/N
Portfolio Strategy?». *Review of Financial Studies*, 22(5), 2009, pp. 1915–1953. DOI 10.1093/rfs/hhm075.

**Библиография подтверждена по первоисточникам-метаданным** (OpenAlex по DOI, Semantic Scholar
Graph API по DOI: `paperId 5056fa2683e15c4c84d13c3dbfb949dc133850a3`, `CorpusId 1073674`,
`MAG 2163969674`, год 2009).

**Статус открытого доступа — закрыт, подтверждено двумя независимыми API:**
- Unpaywall `https://api.unpaywall.org/v2/10.1093/rfs/hhm075` → HTTP 200, `is_oa: False`,
  `best_oa_location: None`, список `oa_locations` пуст.
- Semantic Scholar → `openAccessPdf: {"url": "", "status": "CLOSED"}`; поле `abstract` изъято
  издателем (`"The following paper fields have been elided by the publisher: {'abstract'}"`).
- OpenAlex `locations[]` — обе записи `is_oa: False`, `pdf_url: None` (Review of Financial Studies
  и RePEc).

**Одиннадцать попыток добычи, все отбиты (URL → HTTP → байты → тип):**

| URL | HTTP | Байт | Тип |
|---|---|---|---|
| `http(s)://faculty.london.edu/avmiguel/DeMiguel-Garlappi-Uppal-RFS.pdf` | 200 | 499 294 | `text/html` — это профиль LBS, не PDF (200+HTML = отказ) |
| `https://www.london.edu/-/media/files/faculty-and-research/DeMiguel-Garlappi-Uppal-RFS.pdf` | 404 | 415 061 | text/html |
| `http://docentes.fe.unl.pt/~psc/OptimalVersusNaiveDiversification.pdf` | 000 | 0 | соединение не установлено |
| `https://personal.lse.ac.uk/vayanos/Cases/DeMiguelGarlappiUppal.pdf` | 404 | 214 | text/html |
| `https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID911512_code16678.pdf?abstractid=911512&mirid=1` | **403** | 5 948 | text/html |
| `https://papers.ssrn.com/sol3/Delivery.cfm?abstractid=911512` | **403** | 5 782 | text/html |
| `https://docs.edhec-risk.com/EDHEC-Publications/documents/DeMiguel.pdf` | 000 | 0 | соединение не установлено |
| `https://www.bauer.uh.edu/rsusmel/phd/DeMiguel-Garlappi-Uppal.pdf` | 403 | 0 | — |
| `https://faculty.washington.edu/ezivot/econ509/DeMiguelGarlappiUppal2009.pdf` | 404 | 162 | text/html |
| `https://www2.bc.edu/~taillard/DeMiguel_Garlappi_Uppal_RFS_2009.pdf` | 000 | 0 | — |
| ещё 4 guess-URL (sfu.ca, ocw.mit.edu, mays.tamu.edu, anderson.ucla.edu) | 404 | 162–3 431 | text/html |

Репозиторий LBS Research Online обыскан: `https://lbsresearch.london.edu/cgi/search?q=Optimal+Versus+Naive+Diversification`
→ HTTP 200, 58 060 байт; в выдаче эта статья **отсутствует** (первый хит
`id/eprint/1755/1/OptimalPortfolioDiversific.pdf` → HTTP 200, 1 195 761 байт, PDF — но это
**другая** работа: Lassance, DeMiguel & Vrins, «Optimal portfolio diversification via independent
component analysis», *Operations Research* 70(1), 2022, DOI 10.1287/opre.2021.2140). CORE API без
ключа → HTTP 200 с ошибкой поиска (`abstract is not a searchable field`). archive.org advancedsearch
по точной фразе → HTTP 200, `numFound: 0`.

🔴 **Практический вывод для темы.** Три числа, которые в прошлой сессии стояли на аннотации —
(а) сколько моделей и наборов данных сравнивалось, (б) формулировка про перекрытие выигрыша ошибкой
оценки, (в) требуемая длина окна оценки для 25 и для 50 активов, — **дословно не подтверждены и в
выводы темы в таком виде идти не должны**. Ссылаться на DeMiguel–Garlappi–Uppal сейчас допустимо
только как на факт существования результата, без цитируемых цифр. Канал, который остался
неопробованным: печатный/библиотечный доступ и e-library по подписке вуза — это не веб-задача.

### Д.6.4 Fleming & DeMets 1996 — ОТКАЗ; абстракта не существует в индексах

Fleming T. R., DeMets D. L. «Surrogate end points in clinical trials: are we being misled?».
*Annals of Internal Medicine*, 1996 Oct 1; 125(7): 605–613. DOI 10.7326/0003-4819-125-7-199610010-00011.
PMID 8815760. Аффилиация первого автора — Department of Biostatistics, University of Washington,
Seattle 98195-7232, USA.

**Что добыто:** полные библиографические реквизиты дословно из PubMed E-utilities —
`https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=8815760&rettype=abstract&retmode=text`
→ HTTP 200, **471 байт**, `text/plain`. Ответ содержит выходные данные и указание
`Comment in Ann Intern Med. 1997 Apr 15;126(8):667` — **и не содержит текста абстракта вовсе**.

**EuropePMC REST** `https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:8815760&resultType=core&format=json`
→ HTTP 200, запись найдена, но `"abstractText": null`, `"isOpenAccess": "N"`,
`fullTextUrlList` содержит единственную ссылку с `"availability": "Subscription required"`.

То есть у этой статьи **абстракт не депонирован ни в MEDLINE, ни в EuropePMC** — добыть «хотя бы
дословный абстракт» технически невозможно, это не наш промах в каналах. Прошлый прогон:
acpjournals.org отбивал `curl` с браузерным UA HTTP 403 (5 785 байт); препринта у статьи 1996 года
нет по природе.

🔴 **Практический вывод.** Требования Fleming–DeMets к суррогатной конечной точке и перечень режимов
отказа **в теме процитировать нечем**. Ни одна формулировка из этого источника не должна попасть в
выжимку как цитата. Если тезис «суррогатная метрика может ввести в заблуждение» нужен теме — его
надо взять из другого, открытого источника, а Fleming–DeMets оставить как библиографическую ссылку
без цитат.

### Д.6.5 Netemeyer, Warmath, Fernandes & Lynch 2018 — ОТКАЗ

Netemeyer R. G., Warmath D., Fernandes D., Lynch J. G. «How Am I Doing? Perceived Financial
Well-Being, Its Potential Antecedents, and Its Relation to Overall Well-Being». *Journal of Consumer
Research*, 45(1), 2018, pp. 68–89. DOI 10.1093/jcr/ucx109.
Метаданные подтверждены Semantic Scholar (`paperId 19e2b4297008bc4c1cfe266aeae4b9c2a99ec904`,
`CorpusId 148692628`, `MAG 2767423872`).

**Ключевая находка канала:** Semantic Scholar отдаёт `openAccessPdf.status: "GREEN"` с
`url: https://doi.org/10.2139/ssrn.3485990` — то есть **зелёная копия существует на SSRN,
abstract_id 3485990**. Но забрать её не удалось:
`https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID3485990_code17371.pdf?abstractid=3485990&mirid=1`
→ HTTP 200, но `file` на скачанном даёт «HTML document text, ASCII text, 5 954 байта» — то есть
антибот-заглушка под видом успеха, а не PDF. Поле `abstract` у S2 изъято издателем
(`elided by the publisher`).

Авторские копии — отказ:
`https://leeds-faculty.colorado.edu/lynchj/PDF/NetemeyerWarmathFernandesLynchJCR2018.pdf` → HTTP 404,
1 245 байт, text/html; тот же путь с пробелами в имени → HTTP 404, 1 245 байт;
`https://spot.colorado.edu/~lynchj/PDF/Netemeyer2018.pdf` → **HTTP 403**, 199 байт,
`text/html; charset=iso-8859-1` (каталог существует, доступ закрыт).

🔴 **Практический вывод.** Дословные формулировки двух конструктов (current money management stress /
expected future financial security) и их различающихся антецедентов **не добыты** и цитироваться не
должны. 🟢 Но канал найден и он рабочий при следующем заходе: **SSRN abstract_id 3485990** — это
именно эта статья; её надо брать через страницу `papers.ssrn.com/sol3/papers.cfm?abstract_id=3485990`
с сессионной кукой, а не прямым Delivery.cfm. Это первая конкретная зацепка по источнику, до сих пор
считавшемуся наглухо пейвольным.

### Д.6.6 Методические рекомендации Банка России № 3-МР от 16.06.2026 — ОТКАЗ

Поиск на cbr.ru: `https://www.cbr.ru/search/?text=3-МР искусственный интеллект` (через
`curl -sk --http1.1` с браузерным UA, как требует правило для госсайтов РФ) → HTTP 200,
**67 380 байт**, `text/html; charset=utf-8`. В выдаче — единственная файловая ссылка
`/Crosscut/LawActs/File/4117`, и это **не** искомый документ (номер из другого диапазона, как и
проверенные прошлым прогоном `/7712` и `/9945`, скачанные ранее в эту же папку: `cbr_7712.pdf` —
PDF 5 страниц, `cbr_9945.pdf` — PDF 21 страница, оба другие акты).

Российский корневой сертификат по прямому запрету владельца не скачивался и не устанавливался;
обход шёл только через `curl -sk --http1.1`.

🔴 **Практический вывод.** Сам текст 3-МР по-прежнему не добыт; дословных формулировок требований
у нас нет. В теме этот документ может фигурировать только как факт («ЦБ выпустил методические
рекомендации по ИБ при разработке и применении ИИ на финрынке, 16.06.2026, № 3-МР»), без цитат и
без перечня требований. Непройденный канал — `garant.ru` / `consultant.ru` (не пробовались в этом
прогоне: бюджет действий закончился на cbr.ru) и рассылка ЦБ по подписке.

---

## Д.5 ИЗМЕНЕНИЯ ВЫВОДОВ по итогам добора

Пишется вахтой (лидом), не подагентом. Разделы Д.3/Д.4 и Д.6 писали два подагента
(потолок правила 11 — два, запущены последовательно, не веером). Разделы Д.0–Д.2 и Д.5 —
вахта. Раздел физически идёт после Д.6, потому что файл только дописывается.

### Д.5.1 🔴 ОПРОВЕРГНУТО (четыре утверждения первой редакции)

**1. «SAW попадает во все три условия less-is-more Гигеренцера» (разд. 0, п. 2 и разд. 4.2)
— НЕВЕРНО.** Разбор по добытому первоисточнику (Д.1.4): условие (3) «критерии коррелированы»
держится; условие (1) «R² критерия ≤ 0,5» держится **только как аналогия**, потому что
наблюдаемого критерия у прескриптивной задачи нет по конструкции; условие (2) «объектов
к признакам ≤ 10» **к нам неприменимо буквально** — оно про ошибку оценки весов по выборке,
а мы веса из выборки не оцениваем вовсе. Правильная формулировка: **два условия из трёх
переносятся, и то одно из них по аналогии.**
🔴 Но поправка **не смягчает** вывод, а переводит его в более жёсткий и более проверяемый:
раз веса не оценены из данных, нет никаких оснований считать, что они бьют равные.
Отсюда новая проверка N5 (Д.5.4).

**2. «Утверждение „повышаем благополучие“ неопровержимо, потому что конечная точка спорна
(CFPB против CRR)» — основание НЕВЕРНОЕ, вывод верный и усилился.** Это не спор двух
источников. Aubrey et al. 2022, табл. 1, с. 3 (Д.2.1) показывает **шесть конкурирующих
определений FWB** с несовпадающими наборами измерений, четыре класса измерителей, критику
шкалы CFPB за одномерность — и главное: *«None of these operationalizations considered
individuals' objective financial situation … as the sole, or even as a core, component of
FWB.»* Утверждение пустое не потому, что мы не сумели измерить, а потому, что **величины
с согласованным определением не существует**, и ни одно из шести определений не кладёт
объективные деньги — то есть ровно то, что считает наша SAW, — в ядро конструкта.
🔴 Разд. 8 («Противоречие между источниками, которое не сглаживается») подлежит переписыванию:
там зафиксирован спор двух работ, а на деле это отсутствие консенсуса в поле.

**3. Три числа из DeMiguel, Garlappi & Uppal 2009 (разд. 4.3) — ЦИТИРОВАТЬ НЕЛЬЗЯ.**
Подтверждено тремя независимыми API (Unpaywall `is_oa: false`, Semantic Scholar `CLOSED`,
OpenAlex — обе локации не-OA), 15 попыток добычи, включая репозиторий LBS Research Online
(статьи там нет) и archive.org (`numFound: 0`). Подробности отказов — Д.6.3. «14 моделей /
7 наборов данных», формулировка про перекрытие выигрыша ошибкой оценки и окна 3 000/6 000
месяцев остаются **непроверенной аннотацией**. Ссылаться на факт существования результата
можно; приводить эти числа в доках модели или во внешних текстах — нет.

**4. Раздел 2.4 (Fleming & DeMets 1996, суррогатные конечные точки) — ЛИШИЛСЯ ОСНОВАНИЯ.**
Это не промах каналов: PubMed efetch (HTTP 200, 471 байт) и EuropePMC (`abstractText: null`,
`isOpenAccess: N`) показывают, что **абстракт не депонирован ни в MEDLINE, ни в EuropePMC**,
то есть у статьи нет открытого текста вообще, даже краткого (Д.6.4). Всё, что стояло
в разд. 2.4, — пересказ сниппета поисковой выдачи неизвестного происхождения. 🔴 **Аналогия
«SAW-полезность = суррогатная конечная точка» содержательно верна и остаётся, но должна быть
переставлена на открытый источник** либо изложена без ссылки, как наше собственное
рассуждение. В нынешнем виде — риск того же класса, что и в теме 40, где знаменитая цитата
не подтвердилась ни одним источником.

### Д.5.2 🟡 УТОЧНИЛОСЬ

**1. Три условия Гигеренцера — теперь на дословной цитате со страницей.** Gigerenzer &
Brighton, *Topics in Cognitive Science* 1 (2009) 107–143, **с. 112** (Д.1.2). Добыто заново:
прежняя ссылка умерла (HTTP 404), рабочий канал — репозиторий MPI
`library.mpib-berlin.mpg.de/ft/gg/GG_Homo_2009.pdf`, HTTP 200, 608 639 байт, текст побайтно
совпал с прогоном первой сессии.
🔴 При этом выяснилось, что **сам Гигеренцер это не выводит, а пересказывает** Einhorn &
Hogarth 1975 с оговоркой «Early attempts to answer this question indicated…», а
первоисточник **не в открытом доступе вовсе** (Unpaywall: `is_oa: false`, OA-локаций ноль;
ScienceDirect — HTTP 403, 1 208 323 байта HTML). Требование задания «цитата с номером
страницы» выполнено, но честная формулировка звучит так: **цитата из Гигеренцера о Эйнхорне,
а не из Эйнхорна.**

**2. Rank reversal у SAW — подтверждён дословно, но задевает нас слабее ожидаемого.**
Aires & Ferreira, *Pesquisa Operacional* 38(2), 2018, 331–362, с. 343: Wang & Luo (2009)
показали RR не только у AHP, но и у SAW, TOPSIS, Borda-Kendall и DEA. Однако **тип #1
(добавление/удаление альтернативы) к нам структурно неприменим**: наши 66 альтернатив —
фиксированная сетка с шагом 10 %, а не пополняемый список кандидатов. Применимы типы #2 и #5;
тип #5 (удаление недискриминирующего критерия) реален в сценарии «у пользователя нет долгов».
🟢 И контр-факт, который обязателен к упоминанию: у Zanakis et al. (1998), 8 методов,
**SAW не дал ни одного rank reversal, а ELECTRE оказался худшим** (Д.3.1, с. 342). Аргумент
«сменить SAW на outranking ради устойчивости» — движение в неверную сторону.

**3. Как отрасль меряет пользу финансовых вмешательств всерьёз — ответ получен и он узкий.**
RCT с заранее заданными **поведенческими** исходами (borrowing, saving, budgeting, insurance,
remittances), эффект в единицах SD, плюс стоимость на единицу эффекта. Kaiser, Lusardi,
Menkhoff, Urban, NBER WP 27057 (2020): 76 RCT, >160 000 человек, **+0,2 SD на знание и
+0,1 SD на поведение**, **$60,40 на 0,2 SD** (Д.2.2). Слова «financial well-being» в качестве
конечной точки там нет.

**4. Спор о пользе разрешается накоплением RCT, а не уточнением определений.** Fernandes,
Lynch & Netemeyer 2014 давали 0,018 SD с CI −0,004…0,022 (то есть ноль) на 13 RCT; на 76 RCT
получается 0,065 SD с CI 0,043…0,089 при тех же допущениях, и авторы пишут дословно:
*«one of the main findings of Fernandes et al. (2014) is not confirmed»* (Д.2.3). 🔴 Это
модель того, как наше утверждение должно быть устроено, чтобы вообще быть утверждением.

**5. Планка эффекта в нашем домене хуже, чем «делить на шесть».** Разд. 1.4 предлагал делить
литературный эффект на 6 (DellaVigna & Linos). Уточнение: в нашем домене **литературного
среднего с приемлемой гетерогенностью просто нет** — у Кайзера credit behaviors названы
наименее надёжной категорией из-за «high heterogeneity», при 115 оценках из 23 исследований
(Д.2.4). Делить не от чего.

**6. Требования MTMM теперь на первоисточнике.** Campbell & Fiske 1959 добыт полностью
(Д.6.2, UBC, HTTP 200, 1 654 879 байт, 26 стр.), четыре правила выписаны со страницами 82–84.
Разд. 2.3, где они излагались «по общему знанию», можно переписать на дословные формулировки.

**7. CONSORT-AI / SPIRIT-AI (разд. 3.4, «участок не отработан») — закрыт.** Оба добыты
дословно из Nature Medicine (Д.6.1): 14 новых пунктов у CONSORT-AI, 15 у SPIRIT-AI,
Delphi 103 → 31 → пилот 34. 🔴 Существенное ограничение переносимости: **непрерывно
обучающиеся системы намеренно вынесены за рамки обоих расширений** — ссылаться на них можно,
пока наша модель детерминирована и версионирована, что у нас так и есть (SemVer, канон v3.0.0).

### Д.5.3 🔴 НОВОЕ — чего в первой редакции не было вовсе, и это меняет приоритеты

**1. Произвол нормировки — самый сильный контраргумент против нашего метода, сильнее
Гигеренцера.** Tofallis C. «Add or multiply? A tutorial on ranking and choosing with multiple
criteria», *INFORMS Transactions on Education* 14(3), 2014, 109–119 (добыт авторский working
paper, HTTP 200, 484 566 байт, 28 стр.). Четыре стандартные нормировки одних и тех же данных
дают **четыре разных ранжирования**; кандидат B съезжает с третьего места на последнее,
кандидат E — с последнего на второе (Д.3.2, с. 5 WP). И вторая половина, ещё хуже: **одна
и та же цифра веса задаёт разный обменный курс между критериями при разной нормировке** —
у Тофаллиса тот же вес даёт то $1,7 тыс., то $1,36 тыс. за год опыта (с. 7 WP).
🔴 **Следствие для нас, прямое и дешёвое в исправлении:** наши экспертно откалиброванные веса
**не имеют однозначного смысла без указания нормировки**. Пять раундов калибровки и согласие
78,63 % калибровали не «важность критерия», а «важность критерия при данной нормировке».
Если нормировка в `docs/math_model.md` не зафиксирована как часть канона — это дефект
документации уровня инварианта.

**2. Linearity trap / парадокс Корхонена — систематическое смещение к угловым решениям.**
Тот же Тофаллис, с. 9–10 WP, геометрически: *«whatever weights are attached the intermediate
point will never be chosen»* — выпукло-доминируемая точка не выигрывает **ни при каких
весах**; Zeleny (1982) называет это «linearity trap», Вежбицкий — парадоксом Корхонена:
взвешенная сумма *«tends to promote decisions with unbalanced criteria»*.
🔴 **Наша задача — буквально задача о сбалансированном решении.** 66 альтернатив с шагом 10 %
образуют симплекс распределения между тремя назначениями; его вершины — «всё в долги»,
«всё в резерв», «всё в цели». Если критериальные оценки на симплексе близки к линейным
по долям, SAW будет систематически выдавать **угловые решения**, а сбалансированные
распределения вроде 40/30/30 не выиграют никогда. Это **проверяемая гипотеза о нашем
собственном коде**, и проверка стоит один прогон (Д.5.4, проверка 4).

**3. Единственный класс методов, объективно лучший для нашей задачи — reference point /
aspiration-based (Вежбицкий).** Не TOPSIS (по устойчивости к RR **хуже** SAW, ни одной
проблемы Д.3.2 не снимает), не outranking (параметров вдвое больше: вместо веса — вес плюс
q, p, v; ELECTRE худший по RR; несравнимость — провальный ответ пользователю личных
финансов), не чистый goal programming (останавливается на достижении цели). Источник добыт
дословно: Lewandowski & Wierzbicki (Eds.), «Aspiration Based Decision Support Systems»,
LNEMS 331, Springer 1989 (репозиторий IIASA, HTTP 200, 7 079 622 байта), сс. 10–12.
🟢 **И половина конструкции у нас уже реализована, просто названа иначе:** инварианты
Rt ≥ 0 и ПДН ≤ 0,40 — это *reservation levels* по Вежбицкому, а цели пользователя
(«подушка на 3 месяца», «закрыть карту за год») — готовые *aspiration levels*.
Переход не требует выбрасывать SAW: свёртка остаётся, меняется **что сворачивается** —
не нормированная оценка критерия, а достижение собственной цели пользователя. Одним ходом
снимается произвол нормировки, вводится нелинейность против linearity trap и радикально
улучшается объяснимость («ваша цель закрыть карту достигается на 100 %, подушка — на 80 %
от вашей же цели» вместо «взвешенный балл 0,72»).
🔴 Цена честно: нужен новый экран с целями по каждому критерию.

**4. Два элемента outranking стоит заимствовать, не меняя метод** (Д.4.1): градуированное
**вето** по резерву/ПДН поверх нынешних бинарных допусков и **порог безразличия q** — если
разрыв SAW-баллов между топ-1 и топ-2 ниже q, показывать их как равноценные, а не назначать
победителя. Оба локальны и чинят ровно найденные дефекты.

**5. 🟢 Отрицательный результат по литературе — в нашу пользу и против нас одновременно.**
Ни одной работы, применяющей MCDM (SAW, ELECTRE, PROMETHEE, TOPSIS, GP, reference point)
к распределению денежного потока домохозяйства или к выбору стратегии погашения долга,
не найдено (Д.4.5). Плюс — новизна продукта подтверждается. Минус — **внешнего бенчмарка
не существует**, валидация возможна только против экспертных решений и внутренних проверок;
это надо записать как принятое ограничение, а не как недоделку.
🔴 Оговорка о добросовестности: WebSearch в этой сессии был недоступен, Google Scholar
и русскоязычные базы (eLibrary, КиберЛенинка) не опрашивались. Вывод имеет силу
«не найдено доступными каналами», не «не существует».

**6. Тест на method variance по Кэмпбеллу–Фиске, которого в теме не было** (Д.6.2): если наши
пять риск-профилей коррелируют между собой сильнее, чем каждый из них — с внешней экспертной
оценкой, то мы меряем **SAW и его веса, а не финансовое положение пользователя**. Сами авторы
пишут (с. 83), что именно это требование в реальных данных проваливается чаще прочих.

### Д.5.4 Обновлённый список проверок (замещает разд. 5 в части полноты)

К трём проверкам разд. 5 добавляются четыре; все исполнимы на синтетике, без пользователей,
и каждая может опровергнуть метод.

| # | Проверка | Что опровергает | Порог, объявляемый ЗАРАНЕЕ | Откуда требование |
|---|---|---|---|---|
| 1 | Турнир против наивных N1–N4 (разд. 5) | нужна ли свёртка вообще | преимущество над N4 < 1 % переплаты И < 1 мес. → метод не оправдан | SR 11-7; Д.4.5 (бенчмарка нет — только наивные) |
| 2 | Sensitivity по входам (разд. 5) | устойчивость к неопределённости | доля качественной смены рекомендации > X % | SR 11-7 |
| 3 | Дискриминантная валидность полезности (разд. 5) | есть ли конструкт | R² на 4 скучных предиктора > 0,95 → конструкта нет | Campbell & Fiske 1959, Д.6.2 |
| **4** | 🔴 **N5 — SAW с РАВНЫМИ весами (tallying)** | нужны ли веса и калибровка | совпадение рекомендации > 90 % профилей → калибровка и риск-профили не оправданы | Д.1.4 (Гигеренцер, Дауэс) |
| **5** | 🔴 **Доля угловых решений на симплексе** | даёт ли перебор 66 содержательный выбор | высокая доля победителей на вершинах/рёбрах симплекса → linearity trap, 66 альтернатив имитируют работу | Д.3.3 (Тофаллис, Zeleny, Корхонен) |
| **6** | 🔴 **Инвариантность к нормировке** | имеют ли веса однозначный смысл | смена нормировки (max / sum / vector) меняет топ-1 более чем на Y % профилей → веса без канонизированной нормировки бессмысленны | Д.3.2 (Тофаллис, с. 5 и 7 WP) |
| **7** | 🔴 **RR типа #5: сценарий «нет долгов»** | устойчивость к выпадению критерия | рекомендация с долговыми критериями и без них расходится | Д.3.1 (Aires & Ferreira, с. 334) |
| **8** | Method variance по 5 риск-профилям | меряем ли мы положение пользователя или свой же движок | взаимные корреляции профилей > корреляции с внешней экспертной оценкой | Д.6.2 (Campbell & Fiske, с. 83) |

🔴 **Приоритет изменился.** Самая дешёвая и самая опровергающая — теперь **проверка 6**
(инвариантность к нормировке): она не требует ни синтетических профилей сотнями, ни
экспертов, а её провал обесценивает всю калибровку весов. Следом — **проверка 4** (равные
веса) и **проверка 5** (угловые решения). Все три бьют в SAW-свёртку, то есть в ту часть,
которая в разд. 4.3 уже была названа наиболее уязвимой.

### Д.5.5 Что осталось неизвестным и что именно вернул отказ

| Источник | Канал и попытки | Что вернул инструмент | Статус |
|---|---|---|---|
| Einhorn & Hogarth 1975, OBHP 13(2), 171–192 | Unpaywall; ScienceDirect PDF (`curl` UA); LAMSADE; CiteSeerX ×2 | `is_oa: false`, OA-локаций ноль; **HTTP 403, 1 208 323 байта HTML**; HTTP 404, 326 байт; HTTP 404, 4 661 и 4 664 байта | 🔴 не добыт; три условия стоят на пересказе Гигеренцера |
| DeMiguel, Garlappi & Uppal 2009, RFS 22(5) | 15 попыток: Unpaywall, S2, OpenAlex, SSRN ×2, LBS-профиль, LBS Research Online, archive.org, CORE | `is_oa: false` / `CLOSED` / обе локации не-OA; SSRN **403 (5 948 и 5 782 байта)**; LBS **200 + HTML вместо PDF**; archive.org `numFound: 0`; абстракт изъят издателем | 🔴 не добыт; три числа цитировать нельзя |
| Fleming & DeMets 1996, Ann Intern Med 125(7) | PubMed efetch; EuropePMC core; acpjournals (прошлая сессия) | efetch **HTTP 200, 471 байт**; EuropePMC `abstractText: null`, `isOpenAccess: N` | 🔴 **текста не существует в открытых индексах вообще, даже абстракта**; разд. 2.4 без основания |
| Netemeyer et al. 2018, JCR 45(1), 68–89 | авторские копии (Leeds, Darden); SSRN Delivery.cfm | 404/403; SSRN **200 + HTML 5 954 байта** (антибот под видом успеха) | 🔴 не добыт, **но канал найден**: S2 даёт `openAccessPdf.status: GREEN`, SSRN `abstract_id=3485990` — брать через `papers.cfm`, не `Delivery.cfm`. Кандидат на следующий заход |
| ЦБ РФ, Методрекомендации № 3-МР от 16.06.2026 | `curl -sk --http1.1` по cbr.ru | HTTP 200, 67 380 байт; единственная файловая ссылка `/Crosscut/LawActs/File/4117` — **другой документ** | 🔴 не добыт. Российский корневой сертификат не ставился (прямой запрет владельца) |
| Roy B. 1991, Theory and Decision 31(1) | OpenAlex → Unpaywall | `is_oa: false`, OA-локаций нет | 🔴 ELECTRE изложен по памяти, помечено по месту |
| Wang & Luo 2009, Math. and Computer Modelling 49 | `curl` UA → ScienceDirect (OpenAlex указал как OA) | **HTTP 403, 1 207 967 байт HTML** | 🔴 известен только через дословный пересказ в добытом обзоре Aires & Ferreira |
| Wierzbicki 1982, Mathematical Modelling 3(5) | `curl` UA → ScienceDirect | **HTTP 403, 1 207 962 байта HTML** | 🟡 идеи покрыты добытым томом IIASA 1989 |
| Keeney & Raiffa 1976 (preferential independence) | OpenAlex, Unpaywall | монография, OA-копий нет | 🔴 условие изложено по памяти, помечено |
| Jones & Tamiz 2009, JMCDA 16(5–6) | `curl` UA → Wiley pdfdirect | **HTTP 403, 5 802 байта** | 🔴 не добыт |
| «A comparison between TOPSIS and SAW», Annals of OR 2023 | `curl` UA → Springer content/pdf | **HTTP 200, но 3 038 байт HTML** (страница проверки) | 🔴 не добыт |
| Fernandes, Lynch & Netemeyer 2014, Management Science 60(8) | OpenAlex, Unpaywall | `oa_pdf: None`, OA-локаций нет | 🟡 результат воспроизведён дословно **внутри** добытого NBER WP 27057 |
| Meehl 1978, JCCP 46(4) | OpenAlex ×4 записи; meehl.umn.edu; meehl.dl.umn.edu; 2 зеркала | все `oa_pdf: None`; **403 (5 872 байта)**; **код 000** (соединение не установлено); **404 (1 231 и 279 байт)** | 🟡 не добыт; фальсифицируемость держится на добытом SR 11-7 («If outcomes fall consistently outside this acceptable range…») |
| Mohammadi & Rezaei, Omega 96 (2020) 102254 | OpenAlex → Unpaywall | OA-локации: ScienceDirect (403-класс) и `resolver.tudelft.nl` — **не пробовалась, бюджет исчерпан** | 🟡 добываема, кандидат на следующий заход |

### Д.5.6 Метод и замеры добора

- Классификация запроса: **depth-first с одной breadth-вставкой** (см. Д.0).
- Подагентов — **два**, запущены **последовательно, не веером** (правило 11 проекта):
  первый — Д.3/Д.4, второй — Д.6. Синтез (Д.5) писала вахта, подагенту не поручался.
- 🔴 **WebSearch в этой сессии оказался недоступен полностью**: на первом же ходе добора
  харнесс вернул «this session has used its web search budget (**400 of 400** WebSearch
  calls)». Это лимит окружения, а не наш внутренний счётчик, и он **исчерпан ещё до старта
  добора**. Ни вахта, ни подагенты поиском не пользовались вовсе.
- 🟢 **Найденная замена WebSearch, которая сработала на всех участках и которую стоит
  запомнить: научные API без ключа.**
  - `https://api.openalex.org/works?search=<q>&per_page=8&mailto=<e>` — основной поиск,
    отдаёт `best_oa_location.pdf_url` и полный массив `locations[]`;
  - `https://api.crossref.org/works?query.bibliographic=<q>&rows=5` — точные реквизиты
    (том, номер, страницы, год, DOI) вместо памяти;
  - `https://api.unpaywall.org/v2/<DOI>?email=<e>` — **отличает «мы не нашли» от «OA нет
    вовсе»**, что и позволило честно закрыть Einhorn & Hogarth и DeMiguel;
  - `https://api.semanticscholar.org/graph/v1/paper/...` — статус OA и цвет (GREEN/CLOSED);
  - EuropePMC REST и PubMed efetch — доказали **отсутствие абстракта** Fleming & DeMets.
- 🔴 **Что не сработало как замена поиску:** DuckDuckGo (`html.` и `lite.`) — **HTTP 202**
  с телом ~14 КБ (челлендж-страница); Bing через `curl` — HTTP 200, но геолокализует и
  игнорирует кавычки, выдача уходит не по теме; Brave — HTTP 200, но JS-рендер.
- 🟢 **Что сработало на добыче:** репозитории институтов и университетов там, где издатель
  закрыт: MPI (`library.mpib-berlin.mpg.de`) — Гигеренцер; NBER — Кайзер; Frontiers (CC BY) —
  Aubrey; SciELO — Aires & Ferreira; UHRA Hertfordshire — Тофаллис; IIASA — Вежбицкий;
  UBC — Campbell & Fiske. **Семь первоисточников из семи, где издатель отдал бы пейволл.**
- 🔴 **Что не сработало ни разу:** ScienceDirect/Elsevier (403 с телом ~1,2 МБ HTML — важный
  признак: большой размер тела не означает успех), Wiley pdfdirect (403, ~5,8 КБ),
  SSRN `Delivery.cfm` (403 и 200+HTML), Springer `content/pdf` (200 + 3 КБ HTML),
  ResearchGate, ACM DL, CORE (`/v3/search/works` — HTTP 500 `"abstract is not a searchable
  field"`, то есть ошибка API, а не отказ доступа; веб-поиск — 403).
- 🔴 `r.jina.ai` не пробовался (401 с нашей сети), Exa не пробовалась (сервер 404) —
  по прямому указанию задания.
- Российские корневые сертификаты **не скачивались и не устанавливались**.

### Д.5.7 Короткий ответ владельцу по итогам добора

**Подход по-прежнему верен наполовину, но половина сместилась.** В первой редакции главной
угрозой числился Гигеренцер («простое правило может быть не хуже нашего перебора»). После
сверки по первоисточнику эта угроза **ослабла как формальный аргумент** (мы попадаем не во
все три условия) и **усилилась как практическое требование** (веса не оценены из данных —
докажи, что они бьют равные).

🔴 **Реальная главная угроза оказалась другой и в первой редакции отсутствовала: произвол
нормировки и linearity trap.** Первое означает, что наши веса не имеют однозначного смысла
без канонизированной нормировки. Второе означает, что линейная свёртка на симплексе
систематически тянет к угловым решениям — то есть перебор 66 альтернатив может выдавать
«всё в долги» или «всё в резерв» не потому, что так лучше пользователю, а потому, что так
устроена арифметика метода. Обе проверяются на синтетике за один прогон каждая, и обе
опровергают больше, чем три проверки первой редакции.

🟢 **И появился конструктивный выход, которого не было: reference point / aspiration-based.**
Он не требует выбрасывать SAW — меняется то, что сворачивается: не нормированная оценка
критерия, а достижение собственной цели пользователя. Половина конструкции у нас уже есть
(инварианты = reservation levels, цели = aspiration levels). Это единственный найденный класс
методов, который одновременно лечит оба новых дефекта и **улучшает** объяснимость, а не
ухудшает её, — в отличие от TOPSIS и outranking, которые по нашим критериям хуже SAW.

**Что делать первым:** проверка 6 (инвариантность к нормировке). Дешевле всех, опровергает
больше всех, и её провал обесценивает пять раундов калибровки и согласие 78,63 %.


---

# ПЕРЕПРОВЕРКА Д3 С ПОИСКОМ — 11.09.2026

Прогон с работающим WebSearch (лимит в `~/.claude/settings.json` поднят). Вахта-лид работает
сама, подагентов по ходу не запускала. Файл только дописывается; каждый источник пишется сразу
после добычи.

## ПЕРЕПРОВЕРКА Д3 С ПОИСКОМ — П2 DeMiguel, Garlappi & Uppal (1/N)

🔴 **Д.6.3 и Д.5.1 п. 3 («цитировать нельзя, текст закрыт») — ОПРОВЕРГНУТЫ в части чисел.
Прав добор темы 40 (Д2), но с оговоркой о версии.**

**Канал:** `curl -skL --http1.1` с браузерным UA →
`https://users.nber.org/~confer/2006/si2006/ap/uppal.pdf` → **HTTP 200, 409 581 байт,
`application/pdf`**, `pdfinfo`: 54 страницы. Разбор `pdftotext -layout`, постранично.
Это **рабочая версия** («1/N», First draft: March 2005, This draft: June 2006, NBER Summer
Institute 2006, AP 7/13/06; сноска: «This paper was earlier circulated under the title,
"How Inefficient is the 1/N Asset-Allocation Strategy?"»). **Журнальная версия RFS 22(5)
1915–1953 по-прежнему не открыта**, номера страниц ниже — листы PDF рабочей версии.

Поиск (WebSearch «DeMiguel Garlappi Uppal Optimal Versus Naive Diversification pdf») дополнительно
выдал: scribd.com/document/85831670 (журнальная версия RFS 2009 — зеркало, Scribd требует
входа, не открывалось), SSRN `abstract_id=1376199` (карточка журнальной версии), EFMA 2013
(`efmaefm.org/.../EFMA2013_0360_fullpaper.pdf` — **другая** работа, критика DGU).
SSRN `papers.cfm?abstract_id=1376199` через `curl` → **HTTP 403, 5 782 байта, `<title>Just
a moment...`** (Cloudflare). Вывод: SSRN теперь закрыт и на `papers.cfm`, не только на
`Delivery.cfm`.

**Три числа, дословно, по `pdftotext` (не по пересказу):**

(а) Число моделей и наборов — абстракт, **л. 2**:
> «Of the fourteen models of optimal portfolio choice that we evaluate across seven empirical
> datasets, we find that none is consistently better than the 1/N rule in terms of Sharpe ratio,
> certainty-equivalent return, or turnover.»

(б) Перекрытие выигрыша ошибкой оценки — абстракт, **л. 2**:
> «This finding indicates that, out of sample, the gain from optimal diversification is more
> than offset by estimation error.»

(в) Окно оценки — абстракт, **л. 2**:
> «…for a portfolio with only 25 assets, the estimation window needed is more than 3,000 months,
> and for a portfolio with 50 assets, it is more than 6,000 months, although in practice these
> parameters are estimated using 120 months of data.»
Введение, **л. 6** — формулировка другая: «is 3,000 months for a portfolio with only 25 assets,
and more than 6,000 months for a portfolio with 50 assets». Симуляции, **л. 25** и выводы
**л. 35** — снова «more than 3,000 … more than 6,000». **л. 28**: «…6,000 months for the case
with 25 assets to outperform the 1/N policy, and when there are 50 risky assets even 6,000
months of data is not enough» (это про другую, более сильную модель внутри симуляций).

**Сверка с Д2 темы 40** (`optimization_solvers_2026-09-10_dobor_lit.md`, раздел D): совпадает
побайтно по всем трём цитатам и по номерам листов (2, 6, 25). Д2 записал версию честно
(«полный текст РАБОЧЕЙ версии, не журнальной»); ошибка — у Д.6.3 этого файла, который искал
только журнальную версию и не видел препринт на NBER.

**Совпадение с аннотацией журнальной версии:** WebSearch-сниппет аннотации RFS/SSRN 1376199
даёт те же 14 / seven / «around 3000 months … about 6000 months» — сниппет, первоисточник
журнала не открыт. Итог: числа 14 / 7 / 3 000 / 6 000 **цитировать можно** со ссылкой на
рабочую версию 2006 и пометкой, что в журнальной версии аннотация говорит «around/about».
Оговорка по существу (л. 25, 28): 3 000 и 6 000 — не константы, а результат калибровки
к рынку США при конкретных коэффициентах Шарпа; при Sharpe 1/N = 0,08 — «more than 1,600»
и «more than 3,200» (л. 25).

## ПЕРЕПРОВЕРКА Д3 С ПОИСКОМ — П1 Dawes & Corrigan 1974 (ДОБЫТО, полный текст журнала)

Dawes R. M., Corrigan B. «Linear models in decision making». *Psychological Bulletin* 81(2),
February 1974, 95–106. **Новый источник, в первом доборе его не было.**
Канал: WebSearch («Dawes Corrigan 1974 "Linear models in decision making" Psychological Bulletin
pdf») → `https://gwern.net/doc/statistics/decision/1974-dawes.pdf` → `curl -skL --http1.1`
с UA → **HTTP 200, 505 970 байт, `application/pdf`**, 12 страниц (скан журнала, OCR-слой).
Разбор `pdftotext`. Страницы журнала = лист PDF + 94. Угаданные соседние пути у gwern
(`1979-dawes`, `1975-einhorn`, `1976-wainer`, `1978-meehl`, `2000-grove`) → все **HTTP 404,
165 667 байт HTML**.

**Абстракт, с. 95, дословно:**
> «A review of these contexts indicates that they have common structural characteristics:
> (a) Each input variable has a conditionally monotone relationship with the output; (b) there
> is error of measurement; and (c) deviations from optimal weighting do not make much practical
> difference. These characteristics ensure the success of linear models. In fact linear models
> are so appropriate in such contexts that random linear models (i.e., models whose weights are
> randomly chosen except for sign) may perform quite well. […] In all four, random linear models
> yield predictions that are superior to those of human judges.»

**Табл. 1, с. 102 — корреляции предсказаний с критерием** (OCR снимает таблицу по столбцам;
раскладка ниже восстановлена по порядку столбцов «judge / judge's model / random model /
equal weighting / cross-validated regression / optimal linear»; 🟡 привязку чисел к строкам
проверить глазами по скану, OCR таблицы ненадёжен):

| Пример | Судья | Модель судьи | Случайные веса | **Равные веса** | Регрессия, кросс-вал. | Оптимальная (на обучающей) |
|---|---|---|---|---|---|---|
| Невроз vs психоз | .28 | .31 | .30 | **.34** | .46 | .46 |
| GPA, Illinois | .33 | .50 | .51 | **.60** | .57 | .69 |
| GPA, Oregon | .37 | .43 | .51 | **.60** | .57 | .69 |
| Оценки факультета, Oregon | .19 | .25 | .39 | **.70** | — | .92 |
| Yntema & Torgerson | .87 | 1.00 | — | … | … | … |

🔴 Последняя строка OCR-ом собрана неполно — цитировать только первые четыре, и то с оговоркой.

**Ключевое место для нашей темы, с. 102–103 дословно:**
> «…equal weighting scheme had a higher correlation with the criterion than did the
> cross-validated optimal weighting scheme. This anomalous result is explained by the fact that
> the ratio of observations of variables was too low to obtain stable beta weights…»
> «…linear models are robust not only in the three ways described earlier in this article, but
> they are robust over deviations from optimal weighting as well. […] the solution to the problem
> of obtaining optimal weights is one that — in terms of von Winterfeldt and Edwards — has a
> "flat maximum." Weights that are near to optimal lead to almost the same output as do optimal
> beta weights.»
> «(But note that in all cases equal weighting is superior to the models based on judges'
> behavior.)»

**Условие соотношения «наблюдений к предикторам» — с. 104, дословно (пересказ Schmidt 1971
и Marks 1966):**
> «Schmidt found that in the presence of suppressor variables the ratio of observations to
> predictors should be approximately 15 to 1 before optimally derived weights are superior to
> unit weights in cross-validation and, in the absence of suppressors, this ratio should be
> 25 to 1. In a similar study, Marks found that a ratio of approximately 20 to 1 was necessary.»

**Вывод статьи, с. 105, дословно:**
> «In short, given the fact that in many contexts equal weights yield predictions very highly
> correlated with those obtained from optimal weights, equal weights may be superior. In contrast
> (Meehl, personal communication, 1972), beta coefficients are extremely unstable and most
> extrapolations are to samples from populations that differ somewhat from those on which the
> betas are estimated.»
> «The whole trick is to decide what variables to look at and then to know how to add.»

**Что это значит для П1.** Условия ЕСТЬ, и они другие, чем у Гигеренцера: не «≤ 10 объектов
на признак», а **«от 15–25 наблюдений на предиктор оптимальные веса начинают выигрывать»**
(Schmidt по пересказу Dawes & Corrigan). Плюс три структурных условия успеха линейной модели
вообще: условная монотонность каждого входа, ошибка измерения, **плоский максимум** — отклонение
от оптимальных весов почти не меняет выход. 🔴 Всё это — задачи **предсказания наблюдаемого
критерия** (GPA, диагноз, оценки), как и у Гигеренцера; вывод Д.1.4 («к прескриптивной SAW
переносится только по аналогии») подтверждается и этим первоисточником.

## ПЕРЕПРОВЕРКА Д3 С ПОИСКОМ — П1 Grove et al. 2000 (ДОБЫТО, полный текст журнала)

Grove W. M., Zald D. H., Lebow B. S., Snitz B. E., Nelson C. «Clinical versus mechanical
prediction: A meta-analysis». *Psychological Assessment* 12(1), 2000, 19–30.
DOI 10.1037//1040-3590.12.1.19. **Новый источник, в первом доборе не пробовался.**
Канал: WebSearch → `http://zaldlab.psy.vanderbilt.edu/resources/wmg00pa.pdf` (лаборатория
второго автора) → `curl` → **HTTP 200, 1 096 631 байт, `application/pdf`**, 12 страниц, скан
журнала. Разбор `pdftotext -layout`.

**Абстракт, с. 19, дословно:**
> «On average, mechanical-prediction techniques were about 10% more accurate than clinical
> predictions. Depending on the specific analysis, mechanical prediction substantially
> outperformed clinical prediction in 33%–47% of studies examined. Although clinical predictions
> were often as accurate as mechanical predictions, in only a few studies (6%–16%) were they
> substantially more accurate.»
С. 20: «Of the 163 studies, 136 qualified for inclusion». С. 21: «only eight studies (6%)
notably favor clinical prediction». С. 25: «in the entire set of 136 studies, no such factor
produced a sizable influence on study outcomes».

🔴 **Для П1 Grove — не аргумент «равные веса не хуже подогнанных».** Он сравнивает **механику
вообще** (регрессия, актуарные таблицы, алгоритмы) с **клиническим суждением**, а не равные
веса с оптимальными. Его место в теме — довод, что формализованная свёртка бьёт интуитивное
экспертное решение, то есть аргумент **за** наличие у нас формального правила, и против
«пусть решает человек/эксперт». Про наш выбор между откалиброванными и равными весами он
не говорит ничего.

## ПЕРЕПРОВЕРКА Д3 С ПОИСКОМ — П3 Netemeyer et al. 2018 (ЧАСТИЧНО: дословный абстракт; полный текст НЕ добыт)

**Полный текст: не добыт. Канал из Д.6.5 («брать через `papers.cfm`») больше не рабочий.**
- SSRN `https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3485990` через `curl -skL --http1.1`
  с UA → **HTTP 403, 5 782 байта, `<title>Just a moment...`** (Cloudflare). То же для 1376199.
- То же через `r.jina.ai` → **HTTP 200, 491 байт**: «Title: Just a moment… Performing security
  verification» — пустышка.
- OUP `academic.oup.com/jcr/article-pdf/45/1/68/29010715/ucx109.pdf` (адрес из выдачи
  WebSearch) → **HTTP 403, 5 813 байт HTML**.
- Wayback `web/2022id_/…Delivery.cfm/SSRN_ID3485990_code17371.pdf…` → **HTTP 404, 4 700 байт**;
  CDX `papers.ssrn.com/sol3/Delivery.cfm*3485990*` → **HTTP 200, 0 байт** (снимков PDF нет).
- Репозиторий UCP (Fernandes), `ciencia.ucp.pt/en/publications/how-am-i-doing-…` →
  HTTP 200, 58 164 байта — карточка без файла (только DOI и PlumX).
- ResearchGate 337543922 — в выдаче есть, но ResearchGate отдаёт Cloudflare и через `r.jina.ai`
  (проверено на соседней записи: HTTP 200, 514 байт, «Security check required»).

**Что добыто — абстракт SSRN-версии дословно.** Канал: Wayback
`https://web.archive.org/web/2022id_/https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3485990`
→ **HTTP 200, 71 509 байт**, `text/html` (карточка SSRN со встроенным абстрактом). Абстракт
у S2 изъят издателем, а у SSRN — нет:
> «Though perceived financial well-being is viewed as an important topic of consumer research,
> the literature contains no accepted definition of this construct. […] perceived financial
> well-being is conceptualized as two related, but separate constructs: 1) stress related to the
> management of money today (current money management stress); and 2) a sense of security in
> one's financial future (expected future financial security). We develop and validate measures
> of these constructs (web appendix A) and then demonstrate their relationship to overall
> well-being, controlling for other life domains and objective measures of the financial domain.
> Our findings demonstrate that perceived financial well-being is a key predictor of overall
> well-being and comparable in magnitude to the combined effect of other life domains (job
> satisfaction, physical health assessment, and relationship support satisfaction). Further, the
> relative importance of current money management stress to overall well-being varies by income
> groups and that current money management stress and expected future financial security have
> differing antecedents.»

**Что это даёт разд. 2.2.** Дословно подтверждены: (1) два раздельных конструкта с их точными
названиями; (2) **«the literature contains no accepted definition of this construct»** — это
тот же вывод, что Д.5.1 п. 2 вывел из Aubrey et al. 2022, теперь из второго, независимого
источника; (3) разные антецеденты у двух конструктов; (4) модели контролировали
**объективные финансовые меры** — то есть субъективное благополучие несёт объяснительную
силу сверх денег. Не добыто: списки антецедентов, коэффициенты, пункты шкал (web appendix A).
Цитировать можно только абстракт.

## ПЕРЕПРОВЕРКА Д3 С ПОИСКОМ — П6 Meehl 1978 (ДОБЫТО, полный текст)

Meehl P. E. «Theoretical Risks and Tabular Asterisks: Sir Karl, Sir Ronald, and the Slow
Progress of Soft Psychology». *JCCP* 46, 1978, 806–834.
Канал: WebSearch («Meehl 1978 "Theoretical risks and tabular asterisks" pdf meehl.umn.edu»)
→ `http://users.cla.umn.edu/~nwaller/prelim/meehtablularasterisks.pdf` (страница N. Waller,
U. Minnesota) → `curl` → **HTTP 200, 831 343 байта, `application/pdf`**, 29 страниц,
текстовый слой 153 863 байта. Это перенабор (метка «#113» из списка трудов Meehl), журнальные
страницы указаны в шапке «1978, Vol. 46, 806-834»; ниже номер листа PDF и расчётная страница
журнала (лист + 805), 🟡 расчётная — не сверена со сканом.

Дословно, лист 12 (≈ с. 817):
> «I believe that the almost universal reliance on merely refuting the null hypothesis as the
> standard method for corroborating substantive theories in the soft areas is a terrible
> mistake, is basically unsound, poor scientific strategy, and one of the worst things that ever
> happened in the history of psychology.»
> «A theory is corroborated to the extent that we have subjected it to such risky tests; the
> more dangerous tests it has survived, the better corroborated it is.»

Лист 14 (≈ с. 819):
> «The situation in which A is merely conjoined to T in setting up our test of T makes it hard
> for us social scientists to fulfill a Popperian falsifiability requirement—to state before the
> fact what would count as a strong falsifier.»

Лист 17 (≈ с. 822):
> «Putting it crudely, if you have enough cases and your measures are not totally unreliable,
> the null hypothesis will always be falsified, regardless of the truth of the substantive
> theory.»

Абстракт (лист 1, с. 806): «Multiple paths to estimating numerical point values ("consistency
tests") are better, even if approximate with rough tolerances; and lacking this, ranges,
orderings, second-order differences, curve peaks and valleys, and function forms should be used.»

**Что это даёт теме.** Требование «объявить порог опровержения заранее» (разд. 5–6, табл.
Д.5.4) теперь стоит на первоисточнике не только SR 11-7, но и Мила: «state before the fact what
would count as a strong falsifier». И второе, прямо в нашу пользу: Мил предлагает вместо
значимости **числовые предсказания с допусками** — наши пороги («совпадение > 90 %», «< 1 %
переплаты») и есть такие «rough tolerances». 🟡 Лист 17 бьёт по любой нашей будущей проверке
на больших синтетических выборках: при сотнях тысяч профилей «статистически значимое» различие
будет всегда — порог обязан быть в единицах практической величины (рубли, месяцы, п. п.),
а не p-value.

## ПЕРЕПРОВЕРКА Д3 С ПОИСКОМ — П1 Einhorn & Hogarth 1975: оригинал НЕ добыт, добыт пересказ соавтора

**Оригинал** (OBHP 13(2), 171–192, DOI 10.1016/0030-5073(75)90044-6) — **не добыт и сейчас**.
Поиск (два запроса, в т.ч. `filetype:pdf`) полного текста не показал: только S2, PhilPapers,
ScienceDirect (абстракт), PsycNET, LAMSADE-библиография. Путь gwern `1975-einhorn.pdf` → HTTP 404.
**Новое против первого добора — абстракт журнала, сниппет WebSearch (первоисточник не открыт):**
«The minimum correlation between the two types of composites is found to be an increasing function
of the intercorrelation of the components and a decreasing function of the number of predictors,
and the minimum is fairly high for most applied situations.»

**Добыт взамен — пересказ одним из двух авторов.** Hogarth R. M. «On ignoring scientific
evidence: The bumpy road to enlightenment». UPF Economics Working Paper 973, May 19, 2006.
Канал: WebSearch («Einhorn Hogarth "unit weighting schemes for decision making" 1975
filetype:pdf») → `https://econ-papers.upf.edu/papers/973.pdf` → `curl` → **HTTP 200, 226 084 байта,
`application/pdf`**, 33 страницы. Благодарность в сноске — Dawes, Makridakis, Armstrong.

Дословно, с. 17–18 WP:
> «Dawes and Corrigan outlined four reasons for the success of their method: (1) in prediction,
> having the appropriate variables in the equation may be more important than the precise form of
> the function; (2) each predictor has a conditionally monotone relationship with the criterion;
> (3) the presence of error of measurement; and (4) deviations from optimal weighting may not make
> much practical difference. Subsequently, Einhorn and I examined the phenomenon analytically
> (Einhorn & Hogarth, 1975). To do so, we first transformed the Dawes and Corrigan model by
> assuming an equal weight model (i.e., all regression coefficients are given equal weight)
> subject only to knowing the correct sign (zero-order correlation) of each variable. […] We then
> went on to show the rather general conditions under which such equal- or unit-weighting models
> correlate highly with so-called optimal weights calculated using least squares. Furthermore, we
> indicated how predictions based on unit weights are not subject to shrinkage on cross-validation
> and that conditions exist under which such simpler models would predict more accurately than
> ordinary least squares.»
> «In addition, Wainer (1976) […] also showed that least-squares regression weights could often be
> replaced by equal weights with little or no loss in accuracy.»
> «Moreover, to show real effects of differential sizes of coefficients, one should put estimated
> models to predictive tests where equal weight models provide a baseline.»
С. 16: «the smaller the ratio n/k the greater the shrinkage».
С. 20: «the equal weighting model correlates perfectly with the arithmetic mean of the x variables
(assuming that they have equal standard deviations)».

**Что это даёт.** (1) Соавтор сам формулирует результат 1975 как **«conditions exist under which»**
— равные веса выигрывают **при условиях**, а не всегда. Это совпадает с осторожным «Early
attempts … indicated» у Гигеренцера (Д.1.3). (2) 🔴 Три числовых условия (R² ≤ .5; ≤ 10 объектов на
признак; коррелированные признаки) у Хогарта **не названы**; первоисточник их не открыт. Они
по-прежнему стоят только на пересказе Гигеренцера. (3) Хогарт прямо формулирует **методическое
требование, совпадающее с нашей проверкой N5**: дифференцированные веса надо проверять против
модели с равными весами как базовой линии. Это первоисточник под N5 лучше, чем аналогия
с Гигеренцером. (4) Важное условие, которое у Гигеренцера не звучит: равные веса работают
**при известном знаке** каждого признака (Einhorn & Hogarth по пересказу соавтора). У нас знаки
критериев известны (переплата — хуже, резерв — лучше), так что это условие мы выполняем.
(5) С. 20: равные веса корректно сравнимы только **при равных стандартных отклонениях**
признаков — то есть смысл «равных весов» сам зависит от нормировки. Это прямая стыковка
с Тофаллисом (Д.3.2): проверка N5 без канонизированной нормировки не определена.

## ПЕРЕПРОВЕРКА Д3 С ПОИСКОМ — П4 Fleming & DeMets 1996: текст НЕ добыт; замена — сам Флеминг, NCBI Bookshelf

**Оригинал — не добыт.** Поиск выдал прямую ссылку издателя
`https://www.acpjournals.org/doi/pdf/10.7326/0003-4819-125-7-199610010-00011`:
- `curl -skL --http1.1` с UA → **HTTP 403, 5 849 байт HTML**;
- `r.jina.ai` → **HTTP 200, 519 байт**, «Just a moment… Performing security verification» — пустышка;
- Wayback `web/2020id_/…` → **HTTP 404, 4 678 байт**.
Авторских PDF, курсовых выкладок с текстом статьи в выдаче нет. Вывод Д.6.4 (абстракта нет
в MEDLINE/EuropePMC) поиском не опровергнут.

**Замена из открытого первоисточника, где Флеминг излагает тот же тезис сам.**
IOM (Institute of Medicine) 2010, «Evaluation of Biomarkers and Surrogate Endpoints in Chronic
Disease», прил. «Presentation by Thomas Fleming: Biomarkers and Surrogate Endpoints in Chronic
Disease», NCBI Bookshelf `https://www.ncbi.nlm.nih.gov/books/NBK209571/` → `curl` → **HTTP 200,
74 512 байт, HTML**. Это **конспект доклада составителями отчёта**, не текст Флеминга; прямые
цитаты в кавычках — его слова.
Дословно:
> «Fleming's work, and in particular, his publication with David DeMets (Fleming and DeMets,
> 1996), was influential to the committee and its recommendations.»
> «The Prentice criteria provide guidance, he said: first, the potential surrogate needs to be
> a correlate; second, the surrogate endpoint must fully capture the net effect of the
> intervention on all mechanisms that influence the clinical outcome.»
> «However, determination of the net effect of an intervention on a surrogate endpoint does not
> exclude the possibility that the intervention produces off-target effects on the clinical
> endpoint, he noted.»
> «"From the clinical perspective, it is key to have a comprehensive understanding of the causal
> pathways of the disease process, and of the off-target as well as the on-target effects of the
> intervention," he said.»

**Что это даёт разд. 2.4.** Аналогию «SAW-полезность = суррогат» можно поставить на этот источник
с честной ссылкой (IOM 2010, конспект доклада Флеминга), а Fleming & DeMets 1996 оставить без
цитат. Два условия переносятся к нам буквально: (1) суррогат должен коррелировать с исходом —
у нас это не показано вовсе (разд. 2); (2) **суррогат должен улавливать ВЕСЬ чистый эффект
вмешательства на исход** — наш SAW-балл заведомо не видит «off-target» эффектов рекомендации
(стресс от агрессивного погашения, срыв плана, отказ от резерва). Корреляция суррогата с исходом
**не достаточна** — это и есть главный тезис, ради которого разд. 2.4 ссылался на Fleming & DeMets.

## ПЕРЕПРОВЕРКА Д3 С ПОИСКОМ — П5 Методрекомендации ЦБ № 3-МР от 16.06.2026 (ДОБЫТО, полный текст)

🔴 **Д.6.6 («на cbr.ru файла нет») — ОПРОВЕРГНУТ.** Файл лежит на cbr.ru; его не было в выдаче
внутреннего поиска ЦБ, но он привязан к пресс-релизу.
Канал: WebSearch («Банк России методические рекомендации 3-МР 16.06.2026 искусственный интеллект»)
→ пресс-релиз `https://www.cbr.ru/press/event/?id=32627` (`curl -sk --http1.1` с UA, **HTTP 200,
31 377 байт**) → единственная файловая ссылка `/Crosscut/LawActs/File/12204` →
**HTTP 200, 200 444 байта, `application/pdf`**, PDF 1.7, **34 страницы**, текстовый слой
116 299 байт. Российский корневой сертификат не ставился. Вместо реквизитов в шапке файла
плейсхолдеры `[REGDATESTAMP] № [REGNUMSTAMP]`; принадлежность к 3-МР подтверждается
(1) привязкой к пресс-релизу ЦБ от той же даты и (2) дословным совпадением п. 1.1 и п. 2.5 с
обзором КонсультантПлюс `consultant.ru/law/hotdocs/94506.html` (HTTP 200, 45 109 байт), где
документ назван «(утв. Банком России 16.06.2026 N 3-МР)». garant.ru → **HTTP 403, 902 байта**;
через `r.jina.ai` → HTTP 200, 368 байт, «Checking your browser» — пустышка.

**Дословно, п. 1.1, стр. 1–2 (адресаты):** «…кредитных организаций, иностранных банков,
осуществляющих деятельность на территории Российской Федерации через свои филиалы, некредитных
финансовых организаций, лиц, оказывающих профессиональные услуги на финансовом рынке, субъектов
национальной платежной системы (далее – организации)…» — в соответствии с Кодексом этики в сфере
ИИ на финрынке (информационное письмо ЦБ от 09.07.2025 № ИН-016-13/91).

**Дословно, п. 2.1.4, стр. 4 (риск, прямо касающийся нас)** — 🟡 OCR двухколоночной таблицы
перемешал слова; восстановленный порядок: «Риски отсутствия достаточной объяснимости и (или)
предсказуемости действий модели ИИ, обусловленные сложностью интерпретации результатов исполнения
модели ИИ, приводящие к некорректным выводам и решениям модели ИИ.» Порядок слов сверить по
PDF глазами.

**Дословно, п. 2.5, стр. 5 (человек в контуре)** — текст восстановлен из того же перемешанного
слоя и совпадает с обзором КонсультантПлюс слово в слово:
> «В случае использования ИИ для выполнения операций в автоматическом режиме в критически важных
> процессах (например, в платежных процессах, процессах учетных систем, которые отражают факты
> основной деятельности организации), когда риски информационной безопасности ИИ оценены
> организацией как высокие, организации рекомендуется реализовать валидацию результатов операций,
> выполненных ИИ в автоматическом режиме, человеком с возможностью изменения таких результатов.»

**Дословно, приложение, п. 1.5, стр. 31 (политика ИБ):**
> «1.5. Достаточная объяснимость и (или) предсказуемость. Рекомендуется закрепить необходимость
> применения механизмов интерпретации поведения модели ИИ в целях обеспечения достаточной
> объяснимости и (или) предсказуемости действий модели ИИ (в релевантных случаях).»
Там же, стр. 31: п. 3 «Минимальные персональные данные» — «использования минимальных
персональных данных, на обработку которых … получено согласие субъекта персональных данных»;
п. 4 «Безопасная разработка» со ссылкой на ГОСТ Р 71539-2024 (ИСО/МЭК 5338:2023) и
ГОСТ Р 70889-2023 (ИСО/МЭК 8183:2023). Стр. 2: термины «объяснимость», «предсказуемость»,
«надёжность» — в значениях национальной стратегии развития ИИ (Указ Президента).

**Что меняется для разд. 3.6 и строки 6 табл. разд. 7.**
1. 🔴 Разд. 3.6 пересказывал Хабр как «контролировать … **прозрачность и предсказуемость её
   работы**» и «**валидацию результатов человеком с возможностью их изменения**» как общий
   принцип. По тексту: (а) человек в контуре рекомендован **только** для операций ИИ
   **в автоматическом режиме** в **критически важных процессах** (платежи, учётные системы)
   **при высоких рисках ИБ** — это узкое условие, а не общий принцип; (б) слова «прозрачность»
   в найденных местах нет — есть «достаточная объяснимость и (или) предсказуемость»,
   **«в релевантных случаях»**. Формулировку разд. 3.6 и строки 6 разд. 7 надо перевести
   на эти слова.
2. Документ — про **информационную безопасность** ИИ, а не про валидацию качества моделей:
   модели угроз (гл. 3, по методике ФСТЭК 05.02.2021), политика ИБ, поставщики и open source.
   Как аналог SR 11-7 он **слабее**, чем выглядел по пересказу.
3. Вывод 3.6 «нас не касается напрямую, пока мы не партнёр поднадзорного лица» — подтверждён
   п. 1.1: FINPILOT ни к одной категории адресатов не относится.
4. Наш принцип «пользователь редактирует распределение» формально **перекрывает** п. 2.5:
   FINPILOT не выполняет операций в автоматическом режиме вообще — рекомендация без исполнения.

## ПЕРЕПРОВЕРКА Д3 С ПОИСКОМ — П1 Dawes 1979 (ДОБЫТО, полный текст журнала)

Dawes R. M. «The robust beauty of improper linear models in decision making». *American
Psychologist* 34(7), July 1979, 571–582. **В первом доборе не пробовался вовсе** (Д.1.4:
«реквизиты по списку литературы Гигеренцера; сам текст Дауэса не добывался»).
Канал: WebSearch («"Dawes" "robust beauty of improper linear models" syllabus reading pdf
571-582»; четыре предыдущих запроса полного текста не дали) →
`https://www.cmu.edu/dietrich/sds/docs/dawes/the-robust-beauty-of-improper-linear-models-in-decision-making.pdf`
(Dept. of Social and Decision Sciences, CMU — кафедра Дауэса) → `curl -skL --http1.1` с UA →
**HTTP 200, 1 205 823 байта, `application/pdf`**, 12 страниц, текстовый слой 71 365 байт.
Страница журнала = лист + 570 (колонтитулы «574 • JULY 1979 • AMERICAN PSYCHOLOGIST» совпадают).
Попутно в выдаче: `scispace.com/pdf/the-robust-beauty-…-gxnq55pw2w.pdf` — не открывался.

**Абстракт, с. 571:**
> «Improper linear models are those in which the weights of the predictor variables are obtained
> by some nonoptimal method; for example, they may be obtained on the basis of intuition, derived
> from simulating a clinical judge's predictions, or set to be equal. This article presents
> evidence that even such improper linear models are superior to clinical intuition when
> predicting a numerical criterion from numerical predictors. In fact, unit (i.e., equal)
> weighting is quite robust for making such predictions.»

**Главное численное условие, с. 574, дословно** (в OCR «IS» = «15»):
> «In multiple regression, for example, b weights are notoriously unstable; the ratio of
> observations to predictors should be as high as 15 or 20 to 1 before b weights, which are the
> optimal weights, do better on cross-validation than do simple unit weights. Schmidt (1971),
> Goldberg (1972), and Claudy (1972) have demonstrated this need empirically through computer
> simulation, and Einhorn and Hogarth (1975) and Srinivisan (Note 3) have attacked the problem
> analytically. The general solution depends on a number of parameters such as the multiple
> correlation in the population and the covariance pattern between predictor variables.»

**Случай без измеримого критерия — прямо про нас, с. 574:**
> «Another situation in which proper linear models cannot be used is that in which there are no
> measurable criterion variables. We might, nevertheless, have some idea about what the important
> predictor variables would be and the direction they would bear to the criterion if we were able
> to measure the criterion.»

**Табл. 1, с. 576 — корреляции с критерием** (OCR снял таблицу столбцами; 29 чисел разложены
по 6 столбцам 5+5+5+5+4+5, пустая ячейка — кросс-валидация у Yntema & Torgerson):

| Пример | Судья | Модель судьи | Случайные веса | **Равные веса** | **Регрессия, кросс-вал.** | Оптимальная |
|---|---|---|---|---|---|---|
| Невроз vs психоз (861 пациент, 11 шкал MMPI) | .28 | .31 | .30 | **.34** | **.46** | .46 |
| GPA, Illinois (90 студентов, 10 признаков) | .33 | .50 | .51 | **.60** | **.57** | .69 |
| GPA, Oregon (те же 90 и 10) | .37 | .43 | .51 | **.60** | **.57** | .69 |
| Оценки факультета, Oregon (111 студентов) | .19 | .25 | .39 | **.48** | **.38** | .54 |
| Yntema & Torgerson (эллипсы) | .84 | .89 | .84 | **.97** | — | .97 |

🔴 **Поправка к моей же записи выше (Dawes & Corrigan 1974, табл. 1):** строка «Оценки факультета»
там собрана OCR неверно (.70 и .92 — числа не из этой строки), строка Yntema & Torgerson —
неполна. Правильные значения — эта таблица 1979 г. (тот же набор пяти исследований, Дауэс
прямо ссылается: «(Dawes & Corrigan, 1974, p. 102)»). Первые три строки 1974 г. совпадают с 1979.

С. 576, дословно: «On the average, these random linear models perform about as well as the
paramorphic models of the judges […]. Equal-weighting models, presented in the fourth column, do
even better. (There is a mathematical reason why equal-weighting models must outperform the
average random model.)» Сноска 5: «Equal or random weighting of incomparable variables — for
example, GRE score and GPA — without prior standardization would be nonsensical.»
С. 577: «The solution to the problem of obtaining optimal weights is one that — in terms of von
Winterfeldt and Edwards — has a "flat maximum." Weights that are near to optimal level produce
almost the same output as do optimal beta weights.» И: «This result seems to hold generally as
long as these intercorrelations are not negative; for example, the correlation between X + 2Y and
2X + Y is .80 when X and Y are uncorrelated.» (в OCR «X + 27» — это «X + 2Y»).

**🔴 Что таблица показывает против тезиса в сильной форме.** «Равные веса не хуже подогнанных»
верно **не всегда даже в собственной таблице Дауэса**: в самом большом исследовании (861 пациент,
11 предикторов, ≈ 78 наблюдений на предиктор) кросс-валидированная регрессия бьёт равные веса
**.46 против .34**. В трёх малых выборках (90–111 объектов на 10 признаков, ≈ 9–11 на признак)
равные веса выигрывают (.60 vs .57, .60 vs .57, .48 vs .38). Это ровно условие с. 574 —
15–20 наблюдений на предиктор. Равные веса **всегда** бьют модель судьи и самого судью — это
и есть устойчивая часть тезиса.

## ПЕРЕПРОВЕРКА Д3 С ПОИСКОМ — П6 Mohammadi & Rezaei 2020 (ДОБЫТО, финальная журнальная версия, CC BY)

Mohammadi M., Rezaei J. «Ensemble ranking: Aggregation of rankings produced by different
multi-criteria decision-making methods». *Omega* 96 (2020) 102254. DOI 10.1016/j.omega.2020.102254.
Канал: Unpaywall API (`api.unpaywall.org/v2/10.1016/j.omega.2020.102254`, HTTP 200, 3 652 байта)
→ OA-локация `http://resolver.tudelft.nl/uuid:592fbf1f-5f2a-4437-9bf1-345ba3d7a6ba` → редирект на
`repository.tudelft.nl/record/…` (HTTP 200, 28 391 байт) → ссылка на файл
`https://repository.tudelft.nl/file/File_6a282e29-e6f3-4252-b1ce-67546c87ae0d` → **HTTP 200,
770 588 байт, `application/pdf`**. Обложка TU Delft: «Document Version: Final published version».
Статья под **CC BY 4.0** («This is an open access article under the CC BY license»). Страницы
ниже — листы PDF (лист 1 — обложка репозитория).

Дословно, лист 2 (Введение):
> «One of the main controversial issues in this area is that different MCDM methods, even when
> they use the same input, produce different and potentially conflicting rankings, which means that
> finding an overall aggregated ranking of alternatives is of the essence. Some studies ignore the
> existence of such a conflict [29], or use a simple ranking statistic, like averages [43], while yet
> other methods attempt to reconcile the difference and work out a compromise [28,42].»
Лист 3: «The MCDM methods may provide different rankings for the same problem because they use
different mechanisms, making it hard to provide sufficient support for the ranking of one MCDM
method compared to the others.»
Метод: веса методов через half-quadratic минимизатор (оценщик Уэлша), плюс **consensus index**
(«the extent to which all MCDM methods agree upon the final ranking», лист 5) и **trust level**.
Примеры — оценка систем ontology alignment OAEI 2018; значения consensus index в примерах
около 0,77–0,91 (листы 8–11; OCR обрезает десятичные — точные числа не выписываю).

**Что это даёт Д.3.5 («метод определяет ответ больше, чем данные» — было «добыто частично»).**
Тезис теперь стоит на дословной формулировке журнала: одни и те же входы — разные методы —
разные, в том числе конфликтующие ранжирования. 🟡 Но Mohammadi & Rezaei это **постулируют
со ссылками**, а не меряют на своей задаче как главный результат; как количественное доказательство
«насколько сильно расходятся» статья не годится. Практический довод для нас: их **consensus
index** — готовая метрика для нашей проверки 6 (инвариантность к нормировке) и N5 (равные
веса): считать согласие топ-1/ранжирования между вариантами SAW, а не только долю совпадений.

## ПЕРЕПРОВЕРКА Д3 С ПОИСКОМ — П6 Keeney & Raiffa 1976, preferential independence (оригинал НЕ добыт; вторичная выкладка)

Монография (Wiley 1976; переиздание CUP 1993) — открытой копии поиск не показал (Google Books,
ResearchGate-обзоры). **Взамен — учебная выкладка:** Panchal J. H., Purdue, «07: Multi-attribute
Utility Theory», слайды курса Decision Making in Engineering Design
(`engineering.purdue.edu/DELP/education/decision_making_slides/Module_07___Multi_attribute_Utility_Theory.pdf`,
`curl` → **HTTP 200, 5 087 134 байта, PDF**, 67 слайдов). 🟡 Вторичный источник.

Дословно, слайд 39:
> «Definition (Preference Independence (PI)) A subset S of attributes is preferentially independent
> of its complement S̄ if the preference order of the consequences involving only changes in levels
> of S does not depend on the levels at which attributes in S̄ are held fixed.»
Слайд 41 — для трёх атрибутов: если X utility-independent от {Y, Z}, а {X, Y} и {X, Z}
preferentially independent от Z и Y соответственно, то u(x, y, z) — **мультилинейная** форма
с членами k·k1·k2·u1·u2 и т. д.; аддитивная — частный случай (k = 0).
Сниппет WebSearch (первоисточник не открыт): «An additive value function … if and only if the
attributes are mutually preferentially independent (Keeney and Raiffa, 1976; Krantz et al., 1971)».

**Что это даёт Д.3.4.** Определение теперь не «по памяти», а по учебной выкладке. Для нас условие
читается так: предпочтение между двумя распределениями, различающимися только долей в долги и
резерв, **не должно зависеть** от того, сколько уходит в цели. 🔴 У нас доли **связаны
симплексом** (сумма = 100 %): изменить две доли при фиксированной третьей нельзя вовсе, так что
условие в классической форме к долям неприменимо — оно применимо к **критериям** (переплата,
срок закрытия, резерв в месяцах, ПДН). А для них взаимозависимость очевидна (Д.1.4, условие 3:
«критерии коррелированы»). Проверка «независимы ли наши критерии по предпочтению» остаётся
открытой и должна быть сформулирована на уровне критериев, не долей.

## ПЕРЕПРОВЕРКА Д3 С ПОИСКОМ — П6 «A comparison between TOPSIS and SAW methods» (ДОБЫТО, журнальная версия, CC BY)

Ciardiello F., Genovese A. «A comparison between TOPSIS and SAW methods». *Annals of Operations
Research* 325 (2023) 967–994. DOI 10.1007/s10479-023-05339-w. **Авторы в первом доборе не были
установлены** (стояло только название).
Канал: WebSearch («"A comparison between TOPSIS and SAW" Annals of Operations Research 2023») →
White Rose Research Online `https://eprints.whiterose.ac.uk/id/eprint/199927/1/s10479-023-05339-w.pdf`
→ `curl` → **HTTP 200, 1 294 821 байт, `application/pdf`**, 29 листов (лист 1 — обложка
репозитория, «Version: Published Version», CC BY). Страницы журнала = лист + 965.

Абстракт, с. 967: «Results show that TOPSIS, when used in combination with a Manhattan distance,
produces rankings which are extremely similar to the ones resulting from SAW. […] Experimental
results confirm that rankings produced by TOPSIS methods are closer to SAW ones when similar formal
properties are satisfied.»
С. 968: «Also, it has been shown that TOPSIS methods suffers from the rank reversal phenomenon,
which does not affect SAW approaches (García-Cascales & Lamata, 2012).»
С. 987 (разд. 6): «TOPSIS methods suffer from rank reversals, while SAW does not.»
С. 988: «TOPSIS with Manhattan distance inherits a nice property of SAW, i.e., the lack of rank
reversals, in this random instance.» (добавление 26-й альтернативы к 25 — табл. 2; с Tchebychev —
«many rank reversals appear», табл. 3).
🔴 **Решающая оговорка, с. 974, дословно:** «Therefore our analysis does not take into account
normalisation techniques occurring before the aggregation processes.» С. 979: «Nevertheless,
similarities might change if different normalisation techniques for ratings and trade-off weights
are chosen.»

**🔴 Противоречие источников, которое НЕ сглаживаю:** Ciardiello & Genovese 2023 (через
García-Cascales & Lamata 2012) — **«SAW не страдает rank reversal»**; Wang & Luo 2009 (через
дословный пересказ Aires & Ferreira 2018, с. 343, Д.3.1) — **RR «occurs … in … SAW»**.
Разрешение по добытому тексту, а не по догадке: Ciardiello & Genovese **явно исключили
нормировку** из анализа (с. 974). Значит их «SAW без RR» — утверждение о **свёртке по
ненормированным (или фиксированно нормированным) оценкам**. Как RR возникает у Wang & Luo, мы
не видели (первоисточник не открыт), поэтому механизм «RR у SAW порождается нормировкой,
зависящей от набора альтернатив (max, sum, vector)» — 🟡 **наша гипотеза**, согласная с
Тофаллисом (Д.3.2), но не цитата. Для нас это одно и то же требование, что и проверка 6:
если нормировка критерия в модели зависит от **набора** 66 альтернатив (деление на максимум по
сетке, сумму по сетке), RR и нестабильность весов приходят через неё; если нормировка задана
**внешними** константами (например, в рублях и месяцах относительно цели пользователя), SAW
от RR типа #1 защищён по результату Ciardiello & Genovese.

## ПЕРЕПРОВЕРКА Д3 С ПОИСКОМ — П6 «Jones & Tamiz 2009»: 🔴 ОШИБКА АВТОРСТВА в файле

Crossref `https://api.crossref.org/works/10.1002/mcda.442` → **HTTP 200, 7 242 байта**:
«Goal Programming: realistic targets for the near future» — авторы **Rafael Caballero, Trinidad
Gómez, Francisco Ruiz**; *JMCDA* **16(3–4)**, **79–110**, май 2009. Выдача WebSearch
(`onlinelibrary.wiley.com/doi/abs/10.1002/mcda.442`, «Caballero - 2009») это подтверждает.
🔴 В файле (Д.4.4, стр. ~1701; таблица «не добыто» ~1795; Д.5.5 ~2311) статья приписана
**Jones D., Tamiz M.** и указан выпуск **16(5–6)** — **оба реквизита неверны**. Jones и Tamiz —
авторы других обзоров GP (напр., «A Review of Goal Programming», Springer ISOR 2016,
DOI 10.1007/978-1-4939-3094-4_21; «Practical Goal Programming», Springer 2010). Полный текст
Caballero et al. не добыт (Wiley 403 в первом доборе; открытых копий поиск не показал).
На выводы Д.4.4 это не влияет: дефект GP там стоит на дословной цитате тома IIASA 1989, с. 21.

## ПЕРЕПРОВЕРКА Д3 С ПОИСКОМ — П6 Roy 1991 и Wang & Luo 2009: НЕ добыты и с поиском

**Roy B.** «The outranking approach and the foundations of ELECTRE methods». *Theory and Decision*
31, 1991, **49–73**, DOI 10.1007/BF00134132 (страницы — из выдачи Springer/WebSearch).
Попытки: WebSearch (карточки Springer, scispace, PhilPapers, S2 — полного текста нет);
Springer `content/pdf/10.1007/BF00134132.pdf` → **HTTP 200, 3 038 байт HTML** (проверочная
страница, как в первом доборе); Wayback `web/2019id_/…` → **HTTP 404, 4 739 байт**; Unpaywall →
`is_oa: False`, OA-локаций нет; scispace карточка → **HTTP 202, 0 байт** (JS-челлендж).
Статус не изменился: ELECTRE в Д.4.1 изложен по памяти.

**Wang Y.-M., Luo Y.** «On rank reversal in decision analysis». *Mathematical and Computer
Modelling* 49(5–6), 2009, **1221–1229**, DOI 10.1016/j.mcm.2008.06.019 (реквизиты — сниппет
WebSearch). Попытки: WebSearch (ScienceDirect, ResearchGate «Request PDF»); Wayback
`web/2015id_/…/pii/S0895717708002860/pdf` → **HTTP 404, 4 719 байт**. Вложение ResearchGate
с García-Cascales & Lamata 2012 (другая работа, «On rank reversal and TOPSIS method», MCM 56
(2012) 123–132) → **HTTP 403, 24 203 байта HTML**. Статус не изменился: известен только через
пересказ Aires & Ferreira.

## ПЕРЕПРОВЕРКА Д3 С ПОИСКОМ — П1 Wainer 1976: оригинал НЕ добыт; добыто свидетельство спора

Wainer H. «Estimating coefficients in linear models: It don't make no nevermind». *Psychological
Bulletin* 83, 1976, 213–217 (реквизиты — сниппеты WebSearch). Четыре запроса полного текста:
S2, ResearchGate (Cloudflare), PsycNET, Springer-соседи. Сниппет выдачи упоминал архивную копию
на `dionysus.psych.wisc.edu` — Wayback CDX по этому хосту (`mimetype:application/pdf`, 2 000
записей, HTTP 200) файла Уэйнера **не содержит**. Путь gwern `1976-wainer.pdf` → HTTP 404.
Блог John D. Cook (WebFetch) Уэйнера по существу не излагает — только комментарий читателя.
Сниппет аннотации (первоисточник не открыт): «under very general circumstances coefficients in
multiple regression models can be replaced with equal weights with almost no loss in accuracy on
the original data sample».

**Добыто — свидетельство, что тезис оспаривался в самой литературе.** de Rooij M. et al.
«The Early Roots of Statistical Learning in the Psychometric Literature: A review and two new
results», arXiv:1911.11463 (Leiden), `curl` → **HTTP 200, 334 561 байт, PDF**, 22 стр.
Дословно, с. 5–6: «Equal weighting obviously does not give an unbiased estimate of the true
regression equation, but because the data are not used for estimation the sample to sample
variance is zero. This may be beneficial in some data analysis situations while harmful in others.
This caused an argument between Wainer (1976) and Pruzek and Frederick (1978): Wainer claimed equal
regression weights are beneficial in almost any circumstance, while Pruzek and Frederick claimed
that only in very limited situations equal weighting is beneficial.»
С. 5: Lawshe & Schucker (1959) — четыре схемы весов (сырые суммы, по SD, по 1/SD, МНК) — «found
NO evidence in favor of one of them over the others».

---

# ИЗМЕНЕНИЯ ВЫВОДОВ ПОСЛЕ ПЕРЕПРОВЕРКИ С ПОИСКОМ (11.09.2026)

Писала вахта-лид сама, подагентов не было. Опровержения помечены 🔴.

## И.1 Держится ли на первоисточниках тезис «равные веса не хуже подогнанных»

**Держится в ограниченной форме; в сильной форме («не хуже всегда») опровергнут собственной
таблицей Дауэса.** Теперь в полном тексте есть три первоисточника блока (Dawes & Corrigan 1974,
Dawes 1979, Grove et al. 2000) и пересказ соавтора Einhorn & Hogarth (Hogarth 2006).
Что устойчиво:
1. **Равные веса лучше модели эксперта и самого эксперта — во всех пяти исследованиях табл. 1
   Dawes 1979, с. 576:** .34/.31, .60/.50, .60/.43, .48/.25, .97/.89 (равные / модель судьи).
   Дословно: «in all cases equal weighting is superior to models based on judges' behavior» (с. 577).
2. Отклонение от оптимальных весов почти не меняет результат: «flat maximum» (с. 577).
Что условно:
3. 🔴 **Против кросс-валидированной регрессии равные веса выигрывают только при малом числе
   наблюдений на признак.** Порог по первоисточнику: **15–20:1** (Dawes 1979, с. 574), а у
   Dawes & Corrigan 1974 (с. 104, пересказ Schmidt 1971) **15:1 с супрессорами и 25:1 без них,
   20:1 по Marks**. В таблице самого Дауэса на выборке 861/11 (≈ 78:1) регрессия бьёт равные
   веса, **.46 против .34**. В трёх выборках с ≈ 9–11 наблюдениями на признак выигрывают равные.
4. Тезис требует известного знака каждого признака, условно-монотонной связи с критерием, ошибки
   измерения, **стандартизации** (Dawes 1979, сноска 5: без неё равные веса «would be
   nonsensical») и неотрицательных интеркорреляций (с. 577).
5. Сам тезис оспаривался: Pruzek & Frederick 1978 против Уэйнера (de Rooij et al. 2019, с. 6).

**Сверка с условиями Гигеренцера и Брайтона (ToCS 2009, с. 112).** Условие «≤ 10 объектов на
признак» с первоисточниками **согласуется**: 10:1 лежит ниже их порога 15–25:1. Условие
«коррелированы признаки» согласуется с Хогартом («rather general conditions … correlate highly»)
и абстрактом Einhorn & Hogarth из сниппета: минимальная корреляция двух композитов растёт
с интеркорреляцией. 🔴 **Условие «R² ≤ .5» не найдено ни в одном добытом первоисточнике**:
оно по-прежнему держится только на пересказе Гигеренцера, а сам Einhorn & Hogarth 1975 не открыт.

**🔴 Главная новая находка для нас — сильнее прежнего вывода Д.1.4.** Д.1.4 писал: «не известно,
что экспертно назначенные веса бьют единичные». Добытый текст говорит больше, и в обратную
сторону: **документировано, что веса, выведенные из поведения экспертов (paramorphic /
bootstrapping), проигрывают равным весам везде, где их сравнивали** (Dawes 1979, табл. 1).
Наши веса откалиброваны по согласию с экспертами (пять раундов, 78,63 %) — по конструкции это
ближе всего именно к «модели судьи». Априорное ожидание для проверки N5, таким образом, —
**не в пользу откалиброванных весов**. Оговорка та же, что в Д.1.4: у Дауэса это задачи
предсказания наблюдаемого критерия. Но Дауэс сам разбирает случай «no measurable criterion
variables» (с. 574) — наш случай — и рекомендует для него improper linear model с известными
направлениями признаков. Это довод **за** формальную свёртку против интуиции и **ничего** —
за экспертные веса против равных. Хогарт (2006, с. 18) формулирует методическое требование
прямо: дифференцированные веса проверять против модели с равными весами как базовой линии.
Это первоисточник под N5 вместо аналогии.

Grove et al. 2000 (+10 % точности у механики, 136 исследований) — довод за формальное правило
против экспертного суждения. **К вопросу «равные или подогнанные» он не относится.**

## И.2 Что меняется для главной угрозы (нормировка, linearity trap) и для выхода (Вежбицкий)

1. **Произвол нормировки усилился: теперь его подтверждают три независимые линии.** (а) Тофаллис —
   смысл весов (Д.3.2). (б) **Дауэс, сноска 5, и Хогарт, с. 20:** сами «равные веса»
   определены только относительно стандартизации, поэтому **проверка N5 без канонизированной
   нормировки не определена**. Порядок проверок из Д.5.4 (сначала 6, потом 4) теперь не
   предпочтение, а логическая зависимость. (в) **Rank reversal у SAW:** Ciardiello & Genovese 2023
   («SAW does not») против Wang & Luo 2009 («occurs … in SAW»). Первые явно исключили нормировку
   (с. 974). 🟡 Гипотеза, не цитата: RR у SAW приходит через нормировку, зависящую от набора
   альтернатив. Практически: если нормировка критериев в модели считается по сетке 66 альтернатив
   (max, sum), угрозу RR типа #1 из Д.5.2 п. 2 нельзя списывать как «структурно неприменимую» —
   сетка фиксирована, но нормирующие константы могут зависеть от входа пользователя. Если
   нормировка задана внешними константами, SAW от RR защищён.
2. **Linearity trap — поиском не опровергнут и не ослаблен.** «Flat maximum» Дауэса (с. 577)
   указывает в ту же сторону: если выход почти не чувствителен к весам, пять риск-профилей
   рискуют давать одни и те же угловые решения. Значит, проверки 4 (N5) и 5 (доля угловых)
   ожидаемо провалятся **вместе**, если провалятся.
3. **Выход через reference point / aspiration-based (Вежбицкий) остаётся лучшим кандидатом;
   поиск против него ничего не дал.** Два новых довода в его пользу: (а) цели пользователя
   задают внешние нормирующие константы, и это прямо закрывает п. 1(в) и сноску 5 Дауэса;
   (б) 3-МР, прил. п. 1.5 (стр. 31): «достаточная объяснимость и (или) предсказуемость» — формат
   «цель достигнута на 80 %» ей отвечает. Готовая метрика для проверок 4 и 6 — consensus index
   Mohammadi & Rezaei 2020.

## И.3 🔴 Что добор Д3 (и я сам в этом прогоне) записал неверно

1. 🔴 **Д.6.3 / Д.5.1 п. 3 — DeMiguel «цитировать нельзя».** Неверно: полный текст рабочей версии
   NBER SI 2006 открыт, числа 14 / 7 / 3 000 / 6 000 сверены по `pdftotext` (л. 2, 6, 25). **Прав
   Д2 темы 40.** Ограничение одно: цитировать как рабочую версию, не как вёрстку RFS.
2. 🔴 **Д.6.6 — «файла 3-МР на cbr.ru нет».** Неверно: `cbr.ru/Crosscut/LawActs/File/12204`,
   34 стр., привязан к пресс-релизу 32627.
3. 🔴 **Разд. 3.6 и стр. 6 разд. 7 — пересказ 3-МР.** Человек в контуре рекомендован только
   для **автоматических операций в критически важных процессах при высоком риске ИБ** (п. 2.5).
   Слова «прозрачность» в найденных местах нет: там «достаточная объяснимость и (или)
   предсказуемость … (в релевантных случаях)». Документ — про ИБ, не про валидацию качества.
4. 🔴 **Авторство «Jones & Tamiz 2009» — неверно.** Правильно: Caballero, Gómez, Ruiz, *JMCDA*
   16(3–4), 79–110 (Crossref).
5. 🔴 **Д.6.5 / Д.5.5 — «канал Netemeyer: брать через `papers.cfm`».** На 11.09.2026 `papers.cfm`
   тоже за Cloudflare (403). Абстракт взят через Wayback, полный текст не добыт.
6. 🔴 **Д.5.5 — Meehl 1978 «не добыт».** Добыт (UMN, 29 стр.).
7. 🔴 **Моя собственная запись в этом прогоне, раздел Dawes & Corrigan 1974:** строки таблицы 1
   «оценки факультета» и Yntema & Torgerson собраны OCR неверно. Правильные значения — в разделе
   Dawes 1979 (исправлено там же).
8. 🔴 **Моя собственная запись в этом прогоне, раздел Keeney & Raiffa:** фраза «для критериев
   взаимозависимость очевидна (Д.1.4, условие 3: „критерии коррелированы“)» **смешивает два
   разных понятия**. Preferential independence — свойство **предпочтений**, а не статистическая
   некоррелированность. Коррелированные критерии могут быть независимыми по предпочтению.
   Вопрос о preferential independence наших критериев остаётся **открытым**, аргументом «они
   коррелированы» он не решается.

## И.4 Что подтвердилось

- Д.1.3: у Гигеренцера — пересказ Einhorn & Hogarth с оговоркой «early attempts»; соавтор сам
  пишет «conditions exist under which» (Hogarth 2006, с. 18).
- Д.1.4: перенос на прескриптивную SAW — аналогия; все добытые первоисточники блока — задачи
  предсказания.
- Д.5.1 п. 2: у FWB нет принятого определения — теперь и дословно у Netemeyer et al. 2018 («the
  literature contains no accepted definition of this construct»).
- Д.6.4: у Fleming & DeMets 1996 открытого текста нет. Замена для разд. 2.4 найдена: IOM 2010,
  конспект доклада Флеминга (NBK209571), с критериями Прентиса и «off-target effects».
- Фальсифицируемость (разд. 5–6): теперь и на Meehl 1978 («state before the fact what would count
  as a strong falsifier»), плюс предостережение: пороги задавать в практических единицах, не
  через p-value.

## И.5 Метод и замеры перепроверки

- Классификация: breadth-first по списку источников П1–П6, лид работал сам, **подагентов 0**
  (потолок два, не понадобились). **WebSearch — 28 вызовов**, отказа по бюджету не было.
  **WebFetch — 1**. Остальное — `curl -skL --http1.1` с браузерным UA, `r.jina.ai`, Wayback
  (`id_` и CDX), Unpaywall и Crossref API, `pdftotext`.
- **Что дал поиск против первого добора** (первый добор этих адресов не видел):
  gwern.net (Dawes & Corrigan 1974); CMU SDS (Dawes 1979); zaldlab Vanderbilt (Grove 2000);
  users.cla.umn.edu/~nwaller (Meehl 1978); econ-papers.upf.edu (Hogarth 2006); NBER SI 2006
  (DeMiguel, адрес был у Д2 темы 40, но не у Д.6.3); пресс-релиз cbr.ru → File/12204 (3-МР);
  consultant.ru (сверка 3-МР); White Rose (Ciardiello & Genovese); NCBI Bookshelf NBK209571
  (Флеминг); arXiv 1911.11463 (спор Уэйнера). TU Delft (Mohammadi & Rezaei) взят **без поиска**,
  по OA-локации Unpaywall, которую первый добор не успел попробовать.
- **Что не открылось и почему:** SSRN (`papers.cfm` и `Delivery.cfm`) — Cloudflare 403, в том
  числе через `r.jina.ai` (пустышка 491 байт); ResearchGate — Cloudflare, в том числе через
  `r.jina.ai` (514 байт) и на вложениях (403, 24 203 байта); acpjournals — 403, `r.jina.ai`
  пустышка 519 байт, Wayback 404; OUP article-pdf — 403; garant.ru — 403, `r.jina.ai` 368 байт;
  Springer `content/pdf` — 200 + 3 038 байт HTML; meehl.umn.edu — 403; Semantic Scholar batch
  API — 429; Wayback availability API — 429.

---

# ДОБОР Г4 (11.09.2026) — MCDM: выбор метода под задачу, первоисточник

## ДОБОР Г4 — «Generalised framework for multi-criteria method selection»: 🔴 АВТОРЫ И ГОД В НАШЕЙ ЗАПИСИ ОШИБОЧНЫ

### Реквизиты — проверены по Crossref и по титулу самого PDF

В очереди пробелов работа записана как «**Cinelli et al.**, "Generalised framework for
multi-criteria method selection", **Omega 2018**». Обе части неточны.

**Правильно (Crossref `query.bibliographic`, HTTP 200, и титул препринта):**
> **Wątróbski J., Jankowski J., Ziemba P., Karczmarczyk A., Zioło M. «Generalised framework
> for multi-criteria method selection». Omega, том 86, страницы 107–124, июль 2019.
> DOI 10.1016/j.omega.2018.07.004.**

Аффилиации по титулу PDF: Wątróbski, Ziemba, Zioło — Faculty of Economics and Management,
University of Szczecin, Mickiewicza 64, 71-101 Szczecin, Poland; Jankowski, Karczmarczyk —
Faculty of Computer Science and Information Systems, West Pomeranian University of Technology,
Żołnierska 49, 71-210 Szczecin, Poland.

🔴 **Фамилии Cinelli среди авторов НЕТ.** Год: статья принята 12 июля 2018 (штамп в PDF:
«Received 10 September 2017, Accepted 12 July 2018, Available online xxx»,
`[m5G;August 3, 2018;19:32]`), но выпуск журнала — **86 (2019), с. 107–124**. Ссылка «Omega
2018» допустима только как год онлайн-публикации; полная ссылка — 2019, том 86.

**Есть парная публикация данных** (тоже не Cinelli): Wątróbski, Jankowski, Ziemba,
Karczmarczyk, Zioło. «Generalised framework for multi-criteria method selection: Rule set
database and exemplary decision support system implementation blueprints». **Data in Brief 22
(февраль 2019), 639–642, DOI 10.1016/j.dib.2018.12.015.** 🔴 Это прямой источник **базы
правил** — если рамку применять, брать её оттуда, а не переписывать из статьи.

**Канал добычи:** Unpaywall `10.1016/j.omega.2018.07.004` — HTTP 200, `is_oa: True`,
**`oa_status: "hybrid"`**, две локации: издатель ScienceDirect и репозиторий
`https://arxiv.org/pdf/1810.11078`. Взят arXiv: `curl -sk --http1.1` —
**HTTP 200, 2 518 978 байт, `application/pdf`**; `pdftotext -layout` → 275 505 байт.
(Первая попытка с `-m 60` дала обрыв на 2 179 072 байтах и битый PDF — `pdftotext` ругался
«Invalid XRef entry 0 / Top-level pages object is wrong type (null)». 🔴 **Замер: частично
скачанный PDF выглядит как файл и имеет HTTP 200 — проверять `pdftotext` на ошибки, а не
только код ответа.** Повтор с `-m 240` дал полный файл.)

### Что рамка делает (аннотация, дословно)

> «Multi-Criteria Decision Analysis (MCDA) methods are widely used in various fields and
> disciplines. While most of the research has been focused on the development and improvement
> of new MCDA methods, **relatively limited attention has been paid to their appropriate
> selection for the given decision problem. Their improper application decreases the quality of
> recommendations, as different MCDA methods deliver inconsistent results.** The current paper
> presents a methodological and practical framework for selecting suitable MCDA methods for a
> particular decision situation. **A set of 56 available MCDA methods was analysed** and, based
> on that, a hierarchical set of methods' characteristics and the rule base were obtained…
> The proposed framework was implemented within a web platform available for public use at
> **www.mcda.it**.»

**Масштаб базы правил (§4, дословно):** «As a result, the original set of **450 thousand rules**
was reduced to **4,536 rules**. Furthermore, after the removal of the rules returning 0 methods,
a **final set of 656 rules** was obtained.»

### 🔴 ЧТО РАМКА ГОВОРИТ ПРО НАШ СЛУЧАЙ — прямые находки

**1. SAW в их классификации — Table 1, строка «Simple Additive Weighting (SAW)», дословные
значения признаков:** доступные бинарные отношения **I = 1, P = 1** (безразличие и
предпочтение; Q = 0, R = 0, S = 0 — то есть **нет слабого предпочтения, несравнимости и
outranking**); «Linear compensation effect»: **No = 0, Total = 1, Partial = 0** — то есть
**ПОЛНАЯ линейная компенсация**; «Type of aggregation»: **Single criterion = 1**, Outranking =
0, Mixed = 0; «Type of preferential information»: **Deterministic = 1, Cardinal = 1**,
Non-deterministic = 0, Ordinal = 0, Fuzzy = 0.

🔴 **Это ровно наш случай и подтверждает выбор:** у нас детерминированные кардинальные оценки
критериев, веса от экспертов числом, полная компенсация между критериями (плохое по одному
критерию можно окупить хорошим по другому — именно это и делает взвешенная сумма), дискретное
множество из 66 альтернатив, задача типа γ (ranking). **Строка SAW в Table 1 совпадает с
профилем нашей задачи по всем пяти группам признаков.** Оговорка честности: это сверка по
таблице признаков, а не прогон их веб-инструмента (www.mcda.it в этом доборе не запускался).

**2. Описание SAW в приложении статьи (дословно):** «[evaluations] with regard to individual
criteria should be **proportionally normalized to the highest evaluation** regarding each of the
criteria. Preference aggregation comes down to determining a **product of weights of a criterion
and the evaluation of a variant regarding this criterion. Next, all such products for a given
variant are added up.**» 🔴 Обратить внимание: у них нормировка — **деление на максимум по
критерию**, а не min-max. Если у нас min-max — это отклонение от их канонического SAW, и его
надо назвать явно.

**3. 🔴 Место SAW в иерархии методов — дословно (§4):**
> «The **SAW method** … **is the simplest case of the MAVT method, where the additive value
> function is normalized to the [0,1] interval.** … It can be, therefore, concluded that
> **the MAVT, SAW, SMART and UTA methods are special cases of the MAUT method.**»

И там же про соседей: «The MAVT method is basically a simplification of the MAUT method, with
the only significant difference being the fact that during the aggregation MAVT uses a **value
function**, and MAUT — a **utility function**. The value function, in contrast to the utility
function, **does not take into account the risk (probability)**.»

🔴 **Это важное следствие для нашей архитектуры.** SAW — частный случай MAVT, а **MAVT (в
отличие от MAUT) не учитывает риск/вероятность**. У нас риск живёт ОТДЕЛЬНО — в блоке
SES + Монте-Карло, — и это методологически корректное разделение, а не пробел: ранжируем
детерминированной ценностной функцией, а неопределённость оцениваем отдельным прогоном.
Если бы мы захотели загнать риск ВНУТРЬ свёртки, правильный ход — переход от SAW/MAVT к MAUT,
а не подкрутка весов SAW.

**4. Правило R14 — почему восемь методов дают почти одно и то же (дословно):** «Based on this
rule, **eight methods are indicated as appropriate** to solve a problem of a specific character:
**EVAMIX, MAUT, MAVT, SAW, SMART, TOPSIS, UTA, VIKOR.** The high number of methods in this rule
results from the **great similarity of the majority of the methods included in it.**»
Дальше авторы делят их на три подмножества похожих. 🔴 **Практический вывод: спор "SAW или
TOPSIS" для нашего профиля задачи — во многом ложный**, обе попадают в одно правило R14;
по этой рамке выбор между ними не детерминирован характером задачи.

**5. Почему вообще выбор метода не безразличен (§2.2, дословно):**
> «**The selection of a proper MCDA method for a given decision situation is salient, since
> various methods can yield different results for the same problem.** The difference in results
> when applying various calculating procedures can be influenced by the following factors:
> **(a) various techniques use weights differently in their calculations; (b) algorithms differ
> in their approach to selecting the "best" solution; (c) many algorithms attempt to scale the
> objectives, which affects the weights already chosen; (d) some algorithms introduce additional
> parameters affecting the final recommendations.**»

🔴 Пункт (c) бьёт прямо в нас: **нормировка критериев меняет фактический вес, уже выбранный
экспертами.** То есть наши откалиброванные веса неотделимы от конкретной схемы нормировки;
менять нормировку без перекалибровки весов — значит молча изменить модель. Это проверяемое
утверждение для наших тестов.

**6. Диагноз практики, который стоит признать про себя (§2.2, дословно):**
> «Decision-makers are often unable to fully justify their choice of the method which was
> applied to solve their decision situation. The selection of a multi-criteria method is
> usually carried out [on the basis of the] software, which they are familiar with. On this
> account, **it is not an MCDA method that is selected for a decision problem, but the decision
> problem is adjusted to a chosen multi-criteria method.**»

**7. Стадии Роя, на которые опирается рамка (§2.1, дословно):** «According to Roy, there are
four stages in the decision-making process: (I) defining an object of the decision and the set
of potential decision variants A as well as the determination of the reference problematics
on A; (II) analysing consequences and developing the consistent set of criteria C;
(III) modelling comprehensive preferences and operationally aggregating performances;
(IV) investigating and developing the recommendation…» и четыре «проблематики» Роя:
«**α - selection, β - sorting, γ - ranking, δ - description**». Наша задача — **γ (ranking)**
плюс α (выбор одной рекомендуемой альтернативы из ранжированного списка).

**8. Честная оценка предшественников, показывающая планку точности (§2.2, дословно):**
«The IDEA approach achieves an accuracy of **63–73%**, depending on the matched MCDA method.»
То есть даже формальные рамки выбора метода ошибаются в трети случаев — на их рекомендацию
нельзя ссылаться как на доказательство правильности нашего выбора, только как на
подтверждающий аргумент.

**9. Ограничение применимости самих рекомендаций (§2.2, дословно):** «The guidelines for the
selection of the MCDA method may be **redundant for some classes of decision problems**.
The degree of criteria compensation is essential for the problems in the field of
sustainability, but for other classes of problems, such a guideline is unnecessary.»

### Ранняя цитата, которую стоит держать под рукой (§2.2, дословно, цитата авторов из [18])

> «the great diversity of MCDA procedures may be seen as a strong point, it can also be a
> weakness. **Up to now, there has been no possibility of deciding whether one method makes
> more sense than another in a specific problem situation.** A systematic axiomatic analysis of
> decision procedures and algorithms is yet to be carried out.»

