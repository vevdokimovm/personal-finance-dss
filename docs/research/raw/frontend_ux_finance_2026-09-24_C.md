# Тема 42 — СЫРЬЁ, ДОБОР ОСТАТКА (файл C)

Снято: 24.09.2026. Исполнитель: агент-добор (lead) + 1 подагент.
Предмет ровно три вещи: **угол 4** (показ неопределённости прогноза),
**угол 6** (доступность: WCAG 2.1 AA + ГОСТ Р 52872-2019), **хвост угла 3**
(отрицательные суммы, округление денег, выравнивание чисел).
Углы 1, 2, 5, 7 и §3.1–3.4 закрыты ранее (`_A.md`, `_B.md`, `_L.md`) и здесь НЕ трогаются.

Формат: дословные цитаты с URL и датой снятия; пересказ помечен словом «Пересказ».

## СТАТУС ЭТОГО ФАЙЛА
- [x] §4 неопределённость — §4.1–4.8 готовы
- [x] §6 доступность — вынесен в отдельный файл `frontend_ux_finance_2026-09-24_C_a11y.md` (986 строк), краткая карта — §6 ниже
- [x] §3.5–3.7 хвост чисел — готовы
- [x] не добыто — по частям лида ниже; по углу 6 — в конце файла `_C_a11y.md`

---

## Угол 4. Показ неопределённости прогноза (коридор p10–p90)

### 4.1. Correll & Gleicher, «Error Bars Considered Harmful» (IEEE TVCG, дек. 2014) — измеренная ошибка восприятия интервала

Источник: препринт авторов, University of Wisconsin-Madison.
URL: https://graphics.cs.wisc.edu/Papers/2014/CG14/Preprint.pdf — снято 24.09.2026,
канал: WebFetch отказался разбирать PDF, но сохранил файл на диск; текст извлечён `pdftotext`.

Аннотация, дословно:

> «When making an inference or comparison with uncertain, noisy, or incomplete data, measurement error and confidence intervals can be as important for judgment as the actual mean values of different groups. These often misunderstood statistical quantities are frequently represented by bar charts with error bars. This paper investigates drawbacks with this standard encoding, and considers a set of alternatives designed to more effectively communicate the implications of mean and error data to a general audience... We suggest the use of gradient plots (which use transparency to encode uncertainty) and violin plots (which use width) as better alternatives for inferential tasks than bar charts with error bars.»

🔴 Ключевой механизм ошибки — «within-the-bar bias» и «all or nothing», дословно:

> «graphically salient objects that present the visual metaphor of “containing” values, values visually within the bar are perceived as likelier data points than values outside of the bar [24]. Lastly, by presenting error bars as discrete visual objects, designers emphasize an “all or nothing” approach to interpretation — values are either within the bar or they are not. By only showing information about one kind of statistical inference, viewers are unable to draw their own conclusions for their own standards of proof...»

Проектные требования, которые авторы вывели ДО эксперимента (дословно):

> «The encoding should avoid “all or nothing” binary encodings — the encodings should permit different standards of proof other than (for instance) an α of 0.05. This will likely require encodings which display confidence continuously, rather than as discrete levels.»
> «The encoding should mitigate known biases in the interpretation of error bars (such as within the bar bias, and mis-estimation of error bars due to the presence of central glyphs). This will likely require encodings which are visually symmetric about the mean.»

**Числа эксперимента 1 (one-sample judgments), дословно:**

> «We recruited 96 participants, 8 for each combination of problem frame and graph type.»
> «Our results support H2: We observed a significant interaction between the position of the dot (above or below the mean) and encoding (F(2,2)=21.3, p < 0.0001) on the perceived likelihood of the dot as an outcome. A Tukey’s test of Honest Significant Difference (HSD) confirmed that participants in the bar chart condition considered red dots below the mean (and so within the visual area of the bar) significantly more likely than those above the bar. This effect was not significant for any of the remaining, symmetric encodings.»
> «A Tukey’s HSD confirmed that participants more consistently followed the expected strategy for question 1 (following the sample mean) with symmetric encodings (violin: 89.2% of trials, gradient: 88.5%, box: 87.4%) than with bar charts (83.2%). Graph type was also a significant main effect on confidence (F(3,2982)=7.46, p < 0.0001). A Tukey’s HSD confirmed that participants were significantly more confident with the alternate encoding types which provided more detail about the probability distribution (gradient: M = 5.12, violin: M = 5.06) than with the bar charts and box plots (M = 4.86 for both encodings).»

> «this study shows that within the bar bias ... is present even for inferential tasks, and can be severe enough to not just impact the perceived likelihood of different outcomes, but even the direction of inference.»

Также измерено, что участники в целом читают неопределённость правильно, если кодировка это позволяет:

> «Participant’s average reported confidence was positively correlated with the relevant value of the cdf (R2 = 0.805, β = 6.78).»
> «Participant’s average judgments about the likelihood of outcomes was positively correlated with the pdf values of the stimuli presented (R2 = 0.842, β = 5.70).»

**Что это значит для FINPILOT (пересказ, вывод вахты, не цитата):** сплошная заливка коридора p10–p90 с резкой границей — это ровно та «all or nothing» кодировка: граница p90 читается как «дальше не бывает», а площадь внутри — как «здесь всё одинаково вероятно». Лечится непрерывным затуханием (градиент по плотности) вместо сплошного цвета и симметрией относительно медианы.

### 4.2. Bank of England, Staff Working Paper No. 1,196 «Anchors aweigh? The effect of communicating forecast uncertainty» (17.07.2026)

URL: https://www.bankofengland.co.uk/working-paper/2026/anchors-aweigh-the-effect-of-communicating-forecast-uncertainty — снято 24.09.2026, канал WebFetch.
Авторы: Michael McMahon, Matthew Naylor, Ryan Rholes, Peter Rickards.

Пересказ страницы (дословные фрагменты аннотации в кавычках):
Часть I — сравнение форматов (fan charts, dot plots, box-and-whisker plots, speedometers, ranges) на массовой и экспертной аудитории: «fan charts are well understood and perform best at jointly conveying both expectations and uncertainty».
Часть II — 1 600 участников из Великобритании в четыре этапа; fan chart «materially mitigate» расшатывание ожиданий при ошибке прогноза и работает как «an ‘insurance policy’ that helps protect central bank reputation».
🔴 Измеренный дефект восприятия: «the public consistently underestimates the degree of uncertainty», и показ неопределённости веером эту недооценку смягчает.

**Противоречие внутри источников по веерным диаграммам** — зафиксировать явно: та же страница/обзор отмечает противоположную рекомендацию из обзора Бернанке (см. §4.3).

### 4.3. Обзор Бернанке (Bank of England, апрель 2024) — официальная рекомендация УБРАТЬ fan chart

Снято 24.09.2026, канал WebSearch + вторичные источники (CNBC 12.04.2024,
https://www.cnbc.com/2024/04/12/bernanke-review-bank-of-england-scraps-fan-charts-in-forecast-overhaul.html;
официальная страница обзора: https://www.bankofengland.co.uk/independent-evaluation-office/forecasting-for-monetary-policy-making-and-communication-at-the-bank-of-england-a-review).

Из изложения обзора (цитаты в кавычках — формулировки обзора, приводимые источниками):
веерные диаграммы «outlived their usefulness» и «should be eliminated»; они
«convey little useful information over and above what could be communicated in other,
more direct ways». Взамен рекомендованы сценарный анализ и прямая словесная
секция о рисках. Всего в обзоре 12 рекомендаций.

🔴 **Прямое противоречие с §4.2** (BoE SWP 1,196, 2026: «fan charts are well understood
and perform best at jointly conveying both expectations and uncertainty»). Расхождение
не сглаживать: экспериментальная психология восприятия говорит, что веер читается
лучше альтернатив; институциональный обзор говорит, что веер не приносит пользы
сверх словесного объяснения и не привлекает внимания публики. Оба утверждения
про РАЗНОЕ: первое — про сравнение форматов в лаборатории, второе — про ценность
формата в реальной коммуникации ЦБ. Для продукта это означает: веер сам по себе
не заменяет текстовое объяснение риска.

### 4.4. Fernandes, Walls, Munson, Hullman, Kay. «Uncertainty Displays Using Quantile Dotplots or CDFs Improve Transit Decision-Making» (CHI '18, DOI 10.1145/3173574.3173718)

URL: https://www.mjskay.com/papers/chi2018-uncertain-bus-decisions.pdf — снято 24.09.2026,
канал: WebFetch сохранил PDF на диск → `pdftotext`.

Аннотация, дословно:

> «Everyday predictive systems typically present point predictions, making it hard for people to account for uncertainty when making decisions... In a controlled, incentivized experiment, we had subjects decide when to catch a bus using displays with textual uncertainty, uncertainty visualizations, or no-uncertainty (control). Frequency-based visualizations previously shown to allow people to better extract probabilities (quantile dotplots) yielded better decisions. Decisions with quantile dotplots with 50 outcomes were (1) better on average, having expected payoffs 97% of optimal (95% CI: [95%,98%]), 5 percentage points more than control (95% CI: [2,8]); and (2) more consistent, having within-subject standard deviation of 3 percentage points (95% CI: [2,4]), 4 percentage points less than control (95% CI: [2,6]). Cumulative distribution function plots performed nearly as well, and both outperformed textual uncertainty, which was sensitive to the probability interval communicated.»

🔴 **Измеренная зависимость от выбранного порога вероятности** (дословно из результатов):

> «Textual uncertainty conditions vary: text99 and text60 reach nearly similar performance, while text85 exhibits very little learning, and appears more comparable to the no uncertainty condition, where neither average performance nor consistency improves much.»
> «many decisions in the final trials are still likely to be of lower quality (lower than 70% of optimal in interval, text85, and none, judging by the 95% PPIs).»

То есть: **условие «interval» (просто показанный интервал) оказалось в одной группе
с условием БЕЗ неопределённости** — интервал сам по себе решений не улучшил.

🔴 **Термин, прямо описывающий риск «интервал прочитали как обещание»** — дословно:

> «Such representations may also be less susceptible to deterministic construal errors, that is, misinterpreting uncertainty as representing some other concept [27]. For example, in weather forecasting, misinterpreting the lower end of a predictive interval for a daily high temperature as the daily low for that day. Reducing an entire distribution to a single one-sided prediction interval (here, the probability a bus arrives at a certain time or later) necessarily reduces the applicability of the prediction.»

**Перенос на FINPILOT (пересказ, вывод вахты):** нижняя граница p10 денежного коридора
будет прочитана как «столько у меня точно будет» — это ровно deterministic construal
error из цитаты выше. Значит p10 нельзя подписывать как «минимум»/«худший случай»:
это 10-й процентиль, и в одном случае из десяти будет хуже.

### 4.5. Kale, Nguyen, Kay, Hullman. «Hypothetical Outcome Plots Help Untrained Observers Judge Trends in Ambiguous Data» (IEEE TVCG / InfoVis 2018)

URL: http://mucollective.northwestern.edu/files/2018-HOPsTrends-InfoVis.pdf — снято 24.09.2026,
канал: WebFetch сохранил PDF на диск → `pdftotext`.

Аннотация, дословно (фрагмент):

> «Animated representations of outcomes drawn from distributions (hypothetical outcome plots, or HOPs) are used in the media and other public venues to communicate uncertainty. HOPs greatly improve multivariate probability estimation over conventional static uncertainty visualizations... By modeling each participant’s accuracy as a function of the level of evidence presented over many repeated judgments, we find that observers are able to correctly infer the underlying trend in samples conveying a lower level of evidence when using HOPs rather than static aggregate uncertainty visualizations as a decision aid.»

Числа, дословно:

> «We found that JNDs were lower in the HOPs condition (Fig. 6, left) than in the error bars condition (Est = -0.68; 95% CI: -1.19 to -0.14; t = -2.49; p = 0.02)... This effect suggested that on average when participants used HOPs rather than error bars they required less evidence about the underlying trend in a noisy time series to achieve mean accuracy (around 75%).»
> «We found that JNDs were lower in the regular HOPs condition (Fig. 8, left) than in the line ensembles condition (Est = -1.22; 95% CI: -2.18 to -0.26; t = -2.52; p = 0.01).»
> «JNDs were also lower for participants who used fast HOPs rather than line ensembles as a decision aid (Est = -0.74; 95% CI: -1.69 to 0.22; t = -1.52; p = 0.13). However, this effect was small and unreliable. When the frame rate of HOPs was faster, gains in performance were attenuated.»

🔴 **Практическая деталь скорости анимации:** «regular HOPs condition (400 ms per sample)»
работает, «fast HOPs (100 ms per sample)» — выигрыш теряется. То есть кадр гипотетического
исхода должен держаться ~400 мс, не быстрее.

Вывод авторов, дословно:

> «This suggests that sampling-oriented presentations of uncertainty lead to better comprehension of uncertainty for the purpose of perceptual decision-making than summary statistical representations of uncertainty.»

### 4.6. 🔴 Нулевой и отрицательный исход внутри интервала — что измерено

Ключевая работа: Joslyn, S. L., & LeClerc, J. E. (2012). «Uncertainty forecasts improve
weather-related decisions and attenuate the effects of forecast error». *Journal of
Experimental Psychology: Applied*, 18(1), 126–140. DOI 10.1037/a0025185.
Открытая копия издателя: https://www.apa.org/pubs/journals/features/xap-18-1-126.pdf —
снято 24.09.2026, канал Exa (`web_search_exa`), текст аннотации и фрагменты результатов
получены из выдачи Exa по этой копии.

Аннотация, дословно:

> «Although uncertainty is inherent in weather forecasts, explicit numeric uncertainty estimates are rarely included in public forecasts for fear that they will be misunderstood. Of particular concern are situations in which precautionary action is required at low probabilities, often the case with severe events... Results suggested that uncertainty information improved decision quality overall and increased trust in the forecast. Participants with uncertainty forecasts took appropriate precautionary action and withheld unnecessary action more often than did participants using deterministic forecasts. When error in the forecast increased, participants with conventional forecasts were reluctant to act. However, this effect was attenuated by uncertainty forecasts. Providing categorical decision advice alone did not improve decisions. However, combining decision advice with uncertainty estimates resulted in the best performance overall.»

**Устройство эксперимента (прямая аналогия с кассовым разрывом):** участник — менеджер
дорожной службы, решает, платить ли за посыпку дорог солью, чтобы избежать штрафа
при гололёде. Порог принятия решения — 17 % вероятности замерзания (PoF).
То есть тестировалась ровно та задача, что у FINPILOT: **вероятность перехода
показателя через КРИТИЧЕСКИЙ ПОРОГ** (ноль/минус), а не ширина интервала вообще.

Числа, дословно (из выдачи по PDF издателя):

> «There was a significant main effect for error type, F(1, 146) 113.41, p .01. Participants made more risk-seeking (M .55, SD .25) than risk-averse errors (M .21, SD .20), d 1.50.»
> «Participants salted more often above the 17% threshold (M .73, SD .15) than below it (M .22, SD .19), d 2.98. There was also a significant interaction, F(1, 245) 26.30, p .01, suggesting greater differentiation in salt decisions among those with uncertainty formats... They salted less below the 17% threshold (M .16, SD .16) than did those with deterministic forecasts (M .25, SD .20), and more above the 17% threshold (M .76, SD .12) than did those with deterministic forecasts (M .72, SD .16).»
> «Tukey’s post hoc analyses indicated significantly better performance among freeze frequency (M $96.42, SD $70.14, p .02, d .67) and freeze frequency consequences participants (M $98.76, SD $54.44, p .02, d .69) than among control participants (M $154.27, SD $100.11).»
> «Trust... significantly greater trust among freeze frequency (M 2.65, SD .70, p .01, d .88) and freeze frequency consequences participants (M 2.79, SD .70, p .01, d 1.09) than among control participants (M 2.05, SD .66).»

🔴 **Три вывода, каждый подтверждён числами выше (пересказ вывода вахты из цитат):**
1. Формат **частоты** («в 17 случаях из 100») дал и лучшую денежную результативность,
   и более высокое доверие, чем контроль без неопределённости — а вот «совет без
   неопределённости» («Providing categorical decision advice alone did not improve
   decisions») не дал ничего. Для продукта: рекомендация «отложите N ₽» без указания
   вероятности провала — по измерению бесполезна.
2. Показ вероятности **порогового события** увеличил разделение решений вокруг порога —
   люди действовали точнее и выше, и ниже порога.
3. Неопределённость **защищает доверие при промахе прогноза**: «this effect was attenuated
   by uncertainty forecasts», и там же измерено, что потерянное доверие возвращается плохо
   («trust once lost is difficult to regain even when the forecast becomes more reliable,
   at least over the 60 trials observed here»).

Смежная работа того же автора: Joslyn, S., & Grounds, M. A. (2015). «The use of uncertainty
forecasts in complex decision tasks and various weather conditions». DOI 10.1037/xap0000064 —
аннотация (Exa, 24.09.2026): «Results suggest that participants with uncertainty estimates
did better overall, and neither the task complexity nor the coldness of the forecasts
reduced that advantage.» То есть выигрыш от показа неопределённости не съедается
усложнением задачи.

**Сводка по углу 4 — что делать с нулём/минусом внутри коридора (вывод вахты, не цитата):**
коридор p10–p90 не отвечает на вопрос пользователя; вопрос звучит как «уйду ли я в минус».
Измеренный ответ — считать и показывать **вероятность порогового события отдельным числом
в частотном формате** («в 17 из 100 сценариев остаток уходит ниже нуля до 20-го числа»),
плюс дату первого возможного пересечения нуля, а не только ширину веера.

## Угол 3, хвост: отрицательные суммы, округление, выравнивание

*(§3.1–3.4 — в `_A.md`, здесь только то, чего там нет.)*

### 3.5. Отрицательные суммы: минус, скобки, цвет

**(а) Unicode CLDR / UTS #35 Part 3 «Numbers» — первоисточник форматов.**
URL: https://www.unicode.org/reports/tr35/tr35-numbers.html — снято 24.09.2026, канал WebFetch.
Дословно:

> «A pattern contains a positive subpattern and may contain a negative subpattern, for example, `#,##0.00;(#,##0.00)`.»
> «if there is no explicit negative subpattern, the implicit negative subpattern is the ASCII minus sign (-) prefixed to the positive subpattern.»
> «That is, `0.00` alone is equivalent to `0.00;-0.00`.»
> «In addition to a standard currency format, in which negative currency amounts might typically be displayed as something like `-$3.27`, locales may provide an `accounting` form, in which for `en_US` the same example would appear as `($3.27)`.»
> «the information in the supplemental data (see Supplemental Currency Data) is used to override the number of decimal places — and the rounding — according to the currency that is being formatted.»

Пересказ (вывод вахты): CLDR различает ДВА стиля — `standard` (минус) и `accounting`
(скобки). Скобки — не украшение и не «так красивее», а отдельный именованный стиль,
и он локалезависим. В JS это `Intl.NumberFormat(locale, {style:'currency', currency:'RUB',
currencySign:'accounting'})`. Для локали `ru` канонический `standard`-паттерн
и разделители зафиксированы в `_A.md` §3.4.

**(б) 🔴 Российская нормативная практика: скобки ВМЕСТО минуса — требование формы.**
Приказ Минфина России от 02.07.2010 № 66н «О формах бухгалтерской отчетности организаций»,
Приложение № 1, сноска <7> к бухгалтерскому балансу. Дословно:

> «<7> Здесь и в других формах отчетов вычитаемый или отрицательный показатель показывается в круглых скобках.»

Источник текста: зеркало документа на сайте Росстата,
https://11.rosstat.gov.ru/storage/mediabank/LAW141042_0_20140322_141409_53398.htm —
снято 24.09.2026. Каналы: `WebFetch` → ошибка TLS «unable to verify the first certificate»
(российский УЦ в цепочке), добыто `curl -sk --http1.1` с браузерным UA, HTTP 200,
549 655 байт; текст извлечён локально регуляркой.

Оттуда же — единицы измерения в шапке формы, дословно:

> «Единица измерения: тыс. руб. (млн. руб.) по ОКЕИ │ 384 (385) │»

Пересказ (вывод вахты): у российского пользователя, видевшего бухгалтерскую или
налоговую форму, скобки = «вычитается/минус» — это привычка, подкреплённая нормативной
формой. Но эта норма про ОТЧЁТНОСТЬ ЮРЛИЦА, а не про личный кабинет: переносить её
на потребительский интерфейс автоматически нельзя, тем более что в банковских выписках
РФ (см. `_A.md` и тему 1С) отрицательные операции показываются знаком «−», а не скобками.

**(в) Цвет для знака суммы — прямой конфликт с WCAG 1.4.1** (см. §6 этого файла):
цвет не может быть единственным носителем смысла, поэтому «красное число = расход»
допустимо только вместе со знаком «−» либо словом/иконкой. Это не мнение, а применение
критерия; дословная формулировка критерия — в §6.

### 3.6. Округление денег в интерфейсе

**(а) Нормативное округление в РФ — только для налога.** НК РФ, ст. 52, п. 6, дословно:

> «6. Сумма налога исчисляется в полных рублях. Сумма налога менее 50 копеек отбрасывается, а сумма налога 50 копеек и более округляется до полного рубля.»

Источник: https://www.nalkod.ru/statia52 (сборник текста НК РФ с комментариями),
снято 24.09.2026, канал `r.jina.ai`. 🟡 **Источник вторичный** — первоисточник
(pravo.gov.ru / consultant) в этом прогоне не открывался; текст пункта совпадает
с общеизвестной редакцией, но для канона его надо сверить по официальной публикации.
Важно: это правило относится к ИСЧИСЛЕНИЮ НАЛОГА, и распространять его на отображение
остатков и платежей в продукте оснований нет.

**(б) Число знаков после запятой задаёт валюта, а не дизайнер** — CLDR
`supplementalData` (цитата в §3.5(а): «is used to override the number of decimal places —
and the rounding — according to the currency»). Для RUB это 2 знака.

**(в) Что НЕ добыто по округлению:** нормативного источника уровня W3C/GOV.UK про
«округлять ли до рубля в интерфейсе» и про рассогласование суммы столбца при
поэлементном округлении в этом прогоне не найдено (запросы и каналы — в разделе
«НЕ ДОБЫТО»). Внутренний канон продукта по арифметике денег уже есть:
`docs/research/raw/08_decimal_core_float_map_2026-08-13.md`,
`11_rounding_convention_verification_2026-08-13.md` — дублировать его поиском не нужно.

### 3.7. Выравнивание чисел в таблицах

**(а) GOV.UK Design System, компонент Table.**
URL: https://design-system.service.gov.uk/components/table/ — снято 24.09.2026, канал WebFetch.
Дословно:

> «When comparing columns of numbers, align the numbers to the right in table cells.»

Реализация: классы `govuk-table__header--numeric` и `govuk-table__cell--numeric`,
в Nunjucks-макросе — `"format": "numeric"`. Там же про доступность: атрибут `scope`
на заголовках нужен, чтобы «help users of assistive technology distinguish between
row and column headers» (`scope="col"` / `scope="row"`).

**(б) Выравнивание по десятичному разделителю — CSS Text Module Level 4, §7.2
«Character-based Alignment in a Table Column».**
URL: https://www.w3.org/TR/css-text-4/#character-alignment — снято 24.09.2026,
канал: WebFetch обрезал документ, добыто через `r.jina.ai`. Дословно:

> «When multiple cells in a column have an alignment character specified, the alignment character of each such cell in the column is centered along a single column-parallel axis and the rest of the text in the column shifted accordingly. (Note that the strings do not have to be the same for each cell, although they usually are.)»

Пример спецификации, дословно: `TD { text-align: "." center }` — «will cause the column
of dollar figures in the following HTML table ... to align along the decimal point».

🔴 В том же месте спецификации висит открытый вопрос редакторов
(«Is this intended to say that it’s the centers of the alignment characters that should
be aligned? It’s not clear that’s what it says...» со ссылкой на минутки 2016-02-02),
то есть фича в CSS Text 4 не устоялась. **Вывод вахты (пересказ):** опираться
на `text-align: "."` нельзя, выравнивание по разделителю делается моноширинными
табличными цифрами (`font-variant-numeric: tabular-nums`, `_A.md` §3.1) плюс
выравниванием вправо и ОДИНАКОВЫМ числом знаков после запятой во всём столбце.

### 4.7. Первоисточник конструкции fan chart — Bank of England Quarterly Bulletin, 1998 Q1, «The Inflation Report projections: understanding the fan chart» (Britton, Fisher, Whitley)

URL: https://www.bankofengland.co.uk/-/media/boe/files/quarterly-bulletin/1998/the-inflation-report-projections-understanding-the-fan-chart.pdf —
снято 24.09.2026; канал: WebFetch сохранил PDF на диск → `pdftotext`.

Дословно про устройство полос:

> «until there is 10% of the distribution in a single central band... That band is coloured the deepest shade of red. The two points are moved outwards again on either side of the first band (still keeping equal probability density) until another 10% of the distribution has been added, this time marking a pair of bands, one on either side of the centre... Pairs of bands continue to be added until 90% of the distribution is covered.»

🔴 Дословно про то, что вне веера исходы ЕСТЬ:

> «The fan chart always has the following features. There is an equal number of red bands on either side of the central band (eight). Each pair of bands covers 10% of the distribution but, if the risks are unbalanced, the same colour bands are not of equal width (representing unequal probability intervals). The distribution is truncated, so that there is an implicit ninth and final pair of bands, occupying the white space outside the 90% covered.»

Дословно про смысл центральной линии:

> «No single projection of inflation at a future date has much chance of matching the subsequent outcome. Policy discussions need to take account of the full range of possibilities... The central projection of inflation is then interpreted as being the ‘mode’ of the statistical distribution—it is the single most likely outcome based on current knowledge and judgment...»
> «The central projection is, by construction, always in the deepest red band since it is associated with the mode. For heavily unbalanced risks, the mean and median may not be in the deepest red band...»

Дословно — подпись к диаграмме, которой Банк Англии сопровождал веер (образец того,
как объясняют коридор словами):

> «The chart shows the relative likelihood of possible outcomes. The central band, coloured deep red, includes the central projection: there is judged to be a 10% chance that inflation will be within that central band at any date. The next deepest shade, on both sides of the central band, takes the distribution out to 20%; and so on, in steps of 10 percentage points. Of course, it is impossible to assess the probabilities with any precision, but this represents the MPC’s best estimate. The more uncertainty there is about the inflation outcome at any particular time horizon, the wider the bands, and the more gradually the colour fades. And if the risks are more on one side than the other, then the remaining bands will be wider on that side of the central band.»

**Прямое следствие для коридора p10–p90 в FINPILOT (вывод вахты, пересказ):**
1. Веер Банка Англии — это НЕ «один интервал 80 %», а **девять пар полос по 10 %
   вероятности каждая**, из которых девятая (внешняя) намеренно не нарисована.
   Наш коридор p10–p90 — это одна полоса с резкой границей, то есть ровно
   «all or nothing» кодировка из §4.1. Ступенчатая заливка по децилям устраняет
   и это, и «within-the-bar bias».
2. Слова «покрытие 80 %» означают, что **в 2 случаях из 10 факт окажется вне
   коридора**, и по §4.6 это надо сказать частотой, а не процентом покрытия.
3. Центральная линия — мода, и при несимметричном риске среднее и медиана в неё
   не попадают; подписывать её «прогноз» без оговорки нельзя.

### 4.8. 🔴🔴 Главная измеренная ошибка ровно НАШЕГО случая: 80 %-й интервал читают как два детерминированных числа

Первоисточники:
- Savelli, S., & Joslyn, S. (2013). «The Advantages of Predictive Interval Forecasts for Non-Expert Users and the Impact of Visualizations». *Applied Cognitive Psychology*. DOI 10.1002/acp.2932.
- Joslyn, S., & Savelli, S. (2021). «Visualizing Uncertainty for Non-Expert End Users: The Challenge of the Deterministic Construal Error». *Frontiers in Computer Science*, 2:590232. DOI 10.3389/fcomp.2020.590232 (открытый доступ, PDF: https://www.frontiersin.org/articles/10.3389/fcomp.2020.590232/pdf).
- Grounds, M. A., Joslyn, S., & Otsuka, K. (2017). «Probabilistic Interval Forecasts: An Individual Differences Approach...». DOI 10.1155/2017/3932565.

Снято 24.09.2026, канал Exa (`mcp__exa__web_search_exa`), выдача по полным текстам.

**Аннотация Savelli & Joslyn 2013, дословно:**

> «Three experiments demonstrated advantages over conventional deterministic forecasts for participants making temperature estimates and precautionary decisions with predictive interval weather forecasts showing the upper and lower boundaries within which the observed value is expected with a specified probability. Participants using predictive intervals were better able to identify unreliable forecasts, expected a narrower range of outcomes, and were more decisive than were participants using deterministic forecasts. Predictive interval format was also manipulated to determine whether adding visualizations enhanced understanding. Some participants using visualizations misinterpreted predictive intervals as expressions of diurnal fluctuations (deterministic forecasts). Almost no misinterpretations occurred when the predictive interval was expressed in text alone. Moreover, no advantages were found for visualizations over text-only formats, demonstrating that visualizations, especially those investigated in these studies, may not be suitable for expressing this concept.»

**Числа (Joslyn & Savelli 2021, обзор собственных экспериментов), дословно:**

> «We first noticed the DCE when testing the bracket visualization of the upper and lower bound of the 80% predictive interval mentioned above (see Figure 1A; Savelli and Joslyn, 2013). Although the visualization was accompanied by a prominent key containing a simple, straightforward definition of each number, **36% of participants misinterpreted the upper bound as the daytime high temperature and the lower bound as the nighttime low**. In other words, they thought that the bracket was depicting a deterministic forecast for diurnal fluctuation.»

> «However, it was a gross misinterpretation of the single-value forecast, much higher (or lower) than what was intended, and it negatively affected the decisions participants made (e.g., to issue a heat or freeze warning) based on the forecast.»

> «So we ran a subsequent study in which we incorporated features recommended by visualization experts to convey uncertainty, such as broken instead of solid lines (Figure 1C) for the bracket (Tufte, 2006) and a bar with blurry, transparent ends (Figure 1D) where the upper and lower bounds were located (MacEachren, 1992). These were also accompanied by the same explicit key. However, again the errors were made at approximately the same rate. In other words, **these classic uncertainty features did not help at all**.»

> «in one final effort, we removed the visualization altogether and presented the information in a text format (See Figure 1B). With this format, the misinterpretation all but disappeared. **Nearly everyone (94%) was able to correctly identify the numbers** intended as the daytime high and nighttime low temperatures. This suggested that the previous errors were at least partially due to the fact that a visualization was used, rather than the particular [design].»

> «As we saw in our own study (Savelli and Joslyn, 2013), omitting the visualization and providing a simple text based numerical representation of the 80% predictive interval instead (Figure 1B) eliminated the error. Moreover, the text format was equally advantageous in terms of forecast understanding, trust in the forecast and decision quality as were the visualizations. In other words, **omitting the visualization reduced DCEs with no costs.** Moreover, participants were able to understand and use the text predictive interval forecast with absolutely no special training.»

**Воспроизведение на широкой (не студенческой) выборке — Grounds, Joslyn & Otsuka 2017, дословно:**

> «Participants who used the predictive interval forecast made significantly more DCEs (M = 2.35, SD = 3.55) than participants who used the point estimate (M = .23, SD = .59), (346.29) = 10.48, < .001, Cohen’s = .83, suggesting that it was not a random error. Moreover, participants with DCEs made significantly different decisions than did those who correctly interpreted the predictive interval...»
> «...the results reported here suggest that text expressions block DCEs and all but eliminate the error... For that reason, we recommend that predictive intervals be communicated using a text format and call for additional research into uncertainty visualizations in general.»

**Смежное измерение по «конусу неопределённости» (тот же обзор), дословно:**

> «A classic example is the cone of uncertainty showing the possible path of a hurricane. Evidence suggests that it is widely misunderstood as the extent of the storm with the central line indicating the main path of the hurricane (Broade et al., 2008; Boone et al., 2018; Bostrom et al., 2018). Indeed, participants tend to indicate that the hurricane will be larger and produce more damage when using the classic cone compared to the same information represented as ensemble or spaghetti plots, showing multiple possible paths (Ruginski et al., 2016; Liu et al., 2017; Padilla et al., 2017).»
> «information instructing participants that the width of the cone of uncertainty “tells you nothing about the size or intensity of the storm” reduced this impression among participants compared to a control condition in which it was not presented (Boone et al., 2018).»

🔴 **Перенос на FINPILOT — это самый жёсткий результат всего угла 4 (вывод вахты, пересказ):**
1. Веер, расширяющийся во времени (конус), сам по себе вызывает «деterministic construal
   error»: люди читают ширину как ВЕЛИЧИНУ явления, а границы — как два конкретных
   прогноза («вот столько будет в лучшем случае и вот столько в худшем»). Ровно
   такую фигуру рисует прогноз денежного потока с расширяющимся коридором.
2. Классические приёмы «мягкой» визуализации неопределённости — пунктир, размытые концы,
   прозрачность — **измеренно не помогли** (частота ошибки та же).
3. Помогло только ОДНО: то же самое числом и словами в тексте — ошибка упала до ~6 %
   (94 % правильных), причём без потери в качестве решений и доверии.
4. Помогает также прямое отрицание неверной трактовки в подписи (эксперимент Boone
   с фразой «ширина ничего не говорит о размере шторма»).
**Следствие для дизайна:** график коридора оставить можно, но решение пользователь должен
принимать по ТЕКСТОВОМУ блоку рядом («в 8 случаях из 10 остаток на 20-е число будет
между X ₽ и Y ₽; в 2 случаях из 10 — вне этого; вероятность уйти в минус — N из 100»),
а не по картинке. И подпись должна прямо отрицать ложную трактовку границ.

---

## НЕ ДОБЫТО (части лида: угол 4 и хвост угла 3). Дата — 24.09.2026

| Источник / вопрос | Каналы и коды | Статус |
|---|---|---|
| Savelli & Joslyn 2013, полный текст (Wiley, DOI 10.1002/acp.2932) | Exa дала аннотацию и пересказ результатов из ОТКРЫТОГО обзора 2021 тех же авторов; сам Wiley не открывался | 🟡 **нужно действие владельца**: пейволл Wiley. Число 36 % и вывод про текст взяты из открытой работы Joslyn & Savelli 2021 (Frontiers), где авторы цитируют собственный эксперимент — это первоисточник на том же уровне достоверности |
| Joslyn & LeClerc 2012, полный PDF издателя (apa.org/pubs/journals/features/xap-18-1-126.pdf) | текст получен через выдачу Exa по этому PDF; отдельного `WebFetch`/`curl` прохода по файлу не делалось (бюджет) | 🟢 **исполнимо, не доделано**: цитаты есть, но со смещёнными знаками статистики (`F(1, 146) 113.41, p .01` — так пришло из извлечения, знаки `=` и `<` потерялись при конвертации PDF). Для канона перепроверить по PDF |
| BIS IFC, «Fan Chart: The Art and Science of Communicating Uncertainty» | WebFetch → **HTTP 404** (ссылка из выдачи WebSearch протухла), другой URL не искался | 🟢 исполнимо, не доделано |
| Обзор Бернанке (BoE, 2024), дословные формулировки из самого отчёта | взяты из изложения CNBC и страницы BoE; PDF самого обзора не открывался | 🟢 исполнимо, не доделано: цитаты «outlived their usefulness», «should be eliminated», «convey little useful information...» приведены по вторичному источнику, для канона нужна сверка по PDF отчёта |
| НК РФ ст. 52 п. 6 — первоисточник | добыто через `r.jina.ai` с `nalkod.ru` (вторичный сборник). `consultant.ru` и `pravo.gov.ru` в этом прогоне не пробовались | 🟢 исполнимо, не доделано |
| «Как округлять деньги в ИНТЕРФЕЙСЕ» и рассогласование итога столбца при поэлементном округлении | запросы: CLDR supplementalData (получено), GOV.UK style guide (в `_A.md` §3.3), поиск нормативного правила уровня W3C/GOV.UK не давал предметного результата | ⚪ **отрицательный результат**: нормы такого уровня, похоже, не существует; внутренний канон продукта уже есть (`08_decimal_core...`, `11_rounding_convention...`) |
| Письмо Минфина России от 18.08.2020 № 07-01-07/72430 (про отрицательные значения в отчётности) | `WebFetch` на `base.garant.ru/74651590/` и `garant.ru/.../74551590/` — страницы открылись (200), но **полного текста письма на них нет**, только аннотация | 🟡 нужен платный доступ Гарант/Консультант либо поиск публикации на minfin.gov.ru. Для продукта не критично: норма про скобки уже добыта дословно из самого приказа 66н |

---

## Угол 6. Доступность — КАРТА (полное сырьё в отдельном файле)

🔴 Дословные цитаты WCAG 2.1, ГОСТ Р 52872-2019, 162-ФЗ и ГОСТ Р 52872-2012 лежат в
`/Users/vasyaevdokimov/repos/personal-finance-dss/docs/research/raw/frontend_ux_finance_2026-09-24_C_a11y.md`
(986 строк, снято 24.09.2026, подагент). Здесь — только карта и то, что меняет решения.

**Структура того файла:** A — WCAG 2.1 (A.0 нормативность, A.1 1.1.1, A.2 1.3.1, A.3 1.4.1,
A.4 1.4.3, A.5 1.4.4, A.6 1.4.10, A.7 1.4.11, A.8 смежные AA, A.9 Understanding 1.4.11 про
графики, A.10 Understanding 1.4.1, A.11 техники H51/H43, A.12 WAI tutorial «Complex Images»);
B — ГОСТ Р 52872-2019 (B.0 дата, B.1 предисловие, B.2 соотношение с WCAG, B.3 область
применения, B.4 критерии дословно, B.5 «версия для слабовидящих», B.6 про таблицы);
C — юридический статус (162-ФЗ ст. 26); D — сравнение с редакцией 2012; НЕ ДОБЫТО.

**Семь фактов из него, которые влияют на продукт:**

1. 🔴 **Дата введения ГОСТ Р 52872-2019 — 01.04.2020, а не 01.06.2020** (приказ Росстандарта
   от 29.08.2019 № 589-ст; сверено по трём источникам). Действует с поправкой ИУС 2020 № 3.
2. 🔴 **Что нормативно:** нормативны только тексты Success Criterion. Understanding и Techniques
   (в т.ч. H43, H51, tutorial «Complex Images») — **информативны**, дословно:
   «Content identified as "informative" or "non-normative" is never required for conformance».
   То есть `scope`/`headers` — не буква нормы, а способ выполнить нормативный 1.3.1.
3. 🔴 **1.4.10 Reflow прямо выводит таблицы данных из-под требования одномерного скролла:**
   «Examples of content which requires two-dimensional layout are ... data tables
   (not individual cells)». Горизонтальный скролл финансовой таблицы на 320 px — законен.
   Оговорка «not individual cells» в русском переводе ГОСТа **утрачена**.
4. 🔴 **1.4.11 (3:1 для графики) не требуется, если то же есть в другой форме** — дословно:
   «The information is available in another form, such as in a table that follows the graph,
   which becomes visible when a "Long Description" button is pressed». Это дешёвый и
   нормативно чистый путь для графика прогноза: таблица значений рядом.
5. **ГОСТ = WCAG 2.1 с той же нумерацией критериев и теми же числами** (4.5:1, 3:1, 200 %,
   320/256 px). Дословно из Введения: «за основу был взят актуальный на этот момент документ
   Web Content Accessibility Guidelines (WCAG) 2.1». Пометки МОД/IDT/NEQ в предисловии НЕТ.
   Своих числовых норм РФ в редакции 2019 не осталось; шире WCAG он тем, что покрывает
   не только веб, но и приложения и «любую информацию в электронно-цифровой форме».
6. 🔴 **Требования «версия для слабовидящих» в редакции 2019 НЕТ** (в редакции 2012 было:
   текстовая версия, «не более 2—3 экранов текста», «не более 15 ссылок»). Осталась общая
   «соответствующая альтернативная версия» из механизма соответствия WCAG.
7. 🔴 **Юридический статус — требование или рекомендация.** 162-ФЗ ст. 26 ч. 1: «Документы
   национальной системы стандартизации применяются на добровольной основе». НО ч. 3:
   «Применение национального стандарта является обязательным для изготовителя и (или)
   исполнителя в случае публичного заявления о соответствии продукции национальному
   стандарту». **Для FINPILOT это означает: пока мы не написали «соответствует
   ГОСТ Р 52872-2019» — это рекомендация; как только написали (сайт, документация,
   карточка в реестре ПО) — обязанность.** Второй путь к обязательности назван самим
   ГОСТом: закупки, техзадания, нормативные акты, коммерческие договоры.

**Пять расхождений перевода ГОСТа против WCAG**, зафиксированных подагентом дословно
(см. конец `_C_a11y.md`): утрачено «(not individual cells)»; «256 пикселей CSS соответствуют
**ширине** ... 1024 пикселя» вместо «height»; ссылка «см. Критерий 1.1.2» вместо 4.1.2;
опечатка «в качество единственного визуального средства» в 1.4.1.
