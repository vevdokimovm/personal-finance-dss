# Г55 — подагент: риск без скоринга, пороги, подписки, шаблонный NLG

Дата: 2026-09-17. Сырьё дописывается по ходу.

---

## УЗЕЛ 1 — риск срыва платежа без скоринга

### 1а. Простые индикаторы и «fast-and-frugal trees» против регрессий — Банк Англии

[РЕЦ] Aikman, D., Galesic, M., Gigerenzer, G., Kapadia, S., Katsikopoulos, K., Kothiyal, A.,
Murphy, E., Neumann, T. «Taking uncertainty seriously: simplicity versus complexity in
financial regulation».
- Первичная версия: **Bank of England Financial Stability Paper No. 28, май 2014, 26 страниц.**
  URL PDF: https://www.bankofengland.co.uk/-/media/boe/files/financial-stability-paper/2014/taking-uncertainty-seriously-simplicity-versus-complexity-in-financial-regulation.pdf
  SSRN: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2432137 · RePEc `boe/finsta/0028`
  · MPRA Paper 59908.
- Журнальная версия: **Industrial and Corporate Change, 2021, vol. 30, no. 2, pp. 317–345**,
  DOI **10.1093/icc/dtaa024** (онлайн 2020-06-29). RePEc `oup/indcch/v30y2021i2p317-345`.
- Канал: Exa `web_search_exa` — отдал большие фрагменты текста PDF. Прямая загрузка PDF
  `curl` дала **HTTP 200, 553 467 байт**, но файл **не разбирается**: `pdftotext` — «Syntax Error:
  Unknown compression method in flate stream / Invalid XRef entry 0 / Top-level pages object is
  wrong type (null)». Числовые таблицы AUROC из PDF поэтому НЕ извлечены — см. «Недобытое».

**Три вывода статьи дословно (версия BoE FSP 28, аннотация):**
> «(i) simple methods can sometimes dominate more complex modelling approaches for calculating
> banks' capital requirements, especially if limited data are available for estimating models or
> the underlying risks are characterised by fat-tailed distributions; (ii) **simple indicators,
> such as leverage or loan to deposit ratios, often outperformed more complex metrics in
> predicting individual bank failure** during the global financial crisis; and (iii) when
> combining information from different indicators to predict bank failure, '**fast-and-frugal**'
> decision trees **can perform comparably to standard, but more information-intensive, regression
> techniques**, while being simpler and easier to communicate.»

🔴 Точная сила утверждения (важно для лидера): по индивидуальным индикаторам — «often
**outperformed**» (простое ЛУЧШЕ сложного); по деревьям против регрессий — «can perform
**comparably**» (простое НЕ ЛУЧШЕ, а не хуже). Это разные утверждения, и статья их не смешивает.

**Дословная методика порога — то, как они выбирают cut-off (это и есть «правило вместо модели»):**
> «To do this, we identify the best cut-off that splits observations of each indicator into zones
> which give a signal of failure on one side of the threshold and survival on the other.
> Specifically, a threshold is found for each indicator between its minimum and maximum value in
> the sample which **minimises the loss function 0.5 × [Pr(false alarm) – Pr(hit)]**, where
> Pr(hit), or the 'hit rate', captures the number of banks that are correctly signalled as
> subsequently failing given the cut-off threshold, relative to the total number of banks that
> actually failed, and Pr(false alarm), or the 'false alarm rate', captures the number of banks
> that are incorrectly picked out as subsequently failing given the cut-off threshold, relative to
> [the total number of surviving banks]»

**Четыре причины, по которым FFT предпочтительны — дословно (прямо переносимы на объяснимость
СППР):**
> «First, as the bias-variance trade-off discussed in Section 3 illustrates, **predictions using
> less information can sometimes be more robust**. Second, since FFTs only assign binary,
> threshold rules to exploit the information in indicators, they are **less sensitive to
> outliers**. Third, FFTs have the advantage that they are able to **handle missing data more
> easily** than regression-based approaches and, because they do not weight together different
> sources of data, they are also more robust to concerns over the reliability or validity of a
> particular data source. Finally, and perhaps most importantly, while their construction follows
> an algorithm, the final trees themselves are **highly transparent** as they provide a clear,
> simple mapping to the generation of 'red' or 'green' flags. While such flags would always need
> to be supplemented by judgement, **a tree representation is easier to understand and communicate
> than the outputs of a regression, whose estimated coefficients give marginal effects**.»

**Определение FFT и медицинский прототип (Green & Mehr 1997), дословно:**
> «The tree is said to be 'fast and frugal' because it uses just a few pieces of information, not
> all of which are always used (Martignon, Katsikopoulos and Woike (2008)). **It can outperform
> logistic regression, which exploits all of the information, in assigning patients correctly.**»
Дерево описано пошагово: ST-сегмент → главный симптом боль в груди → короткий список прочих
симптомов; максимум три бинарных вопроса, выход возможен на каждом.

**Цепочка более ранних замеров, на которые статья опирается (все — «простое ≥ сложного»), дословно:**
> «In a similar vein, lexicographic models such as '**take-the-best**' (a heuristic that chooses
> one of two options based on a single cue…) have often been found to be superior in predictive
> accuracy, compared to both regression (**Czerlinski, Gigerenzer and Goldstein (1999)**) and
> Bayesian models (**Martignon and Hoffrage (2002)**). This is particularly so **when datasets
> available to fit models are small** (Katsikopoulos, Schooler and Hertwig (2010)). And the
> '**hiatus heuristic**', which predicts the likelihood that a customer will make a purchase based
> upon how recent their last purchase was, has been found to outperform more complex models in
> prediction (**Wübben and Wangenheim (2008)**).»

[ОЦЕНКА] Теоретическая база FFT для поиска AUC-чисел (ссылка из библиографии статьи):
**Luan, S., Schooler, L. J., Gigerenzer, G. «A signal-detection analysis of fast-and-frugal
trees». Psychological Review, 2011, 118(2), pp. 316–338, DOI 10.1037/a0022684** — это работа,
в которой FFT разобраны именно в терминах ROC/обнаружения сигнала. Сама она в этот заход
не добывалась.

#### 1а-1. ЧИСЛА добыты через текстовый прокси

[ЗАМЕР] Канал: `curl -s "https://r.jina.ai/<URL PDF>"` **без** браузерного UA →
**HTTP 200, 114 224 байта** текста. (Прямой `curl` тот же PDF отдал, но он не разбирался
`pdftotext` — прокси спас источник.) Снято 2026-09-17.

**Функция потерь и абсолютная шкала — дословно:**
> «This loss function reflects an equal weighting of 'false alarms' and 'hits'. The lower the loss,
> the better the indicator is — **a perfect signal would spot every failure (Pr(hit) = 1) and yield
> no false alarms, thus giving a loss of −0.5**.»

**Пример подбора порога по одному индикатору — дословно (это буквальный образец «правила вместо
модели»):**
> «As an example, consider the balance-sheet leverage ratio (LR). The minimum and maximum LR
> across banks in the sample are **1.4% and 9.3%** respectively. For any x between these, we have
> a rule which signals the bank as failing if LR < x and surviving otherwise. **For x = 4.15%, the
> loss of this rule is minimised at −0.20**; hence the cut-off threshold for LR is 4.15%.»

**Простое против сложного по отдельным индикаторам — дословно:**
> «On the whole, **the simpler measures tend to perform better**. For example, the three
> best-performing discriminators, the two leverage ratios and the level of wholesale funding, are
> three of the simplest metrics considered. In terms of capital adequacy, **the balance-sheet
> leverage ratio performs considerably better than the Basel I risk-based capital ratio**,
> consistent with the findings of IMF (2009). **Ignoring the Basel I risk weightings that were
> supposed to improve measurement increases predictive power** in relation to the failure of
> a typical large bank in the global financial crisis»

🔴 **Числа качества «интуитивного» дерева из 4 признаков (in-sample), дословно:**
> «More generally, we can calculate the overall in-sample performance of this tree across the
> entire dataset of banks. Doing this, we find that it **correctly calls 82% of the banks that
> failed during the crisis (a hit rate of 0.82)**, while, of the total number of banks that
> survived, **50% of those were incorrectly called as failing (a false alarm rate of 0.50)**.
> **Excluding the wholesale funding level indicator from the tree increases the hit rate to 0.87
> but the false alarm rate goes up to 0.63.**»

🔴 **Самый неожиданный результат — ОДИН индикатор бьёт оба дерева, дословно (сноска 1 к Figure 4):**
> «Note that if hits and false alarms are weighted equally in the loss function, **the
> balance-sheet leverage ratio indicator taken individually has a slightly lower loss than both of
> these trees**, primarily because its lower hit rate (**0.74**) is more than outweighed by
> a lower false alarm rate (**0.35**). This would seem to argue for using individual indicators
> rather than the trees. There are, however, two reasons opposing this argument. First, **if higher
> weight were placed on the hit rate than the false alarm rate in the loss function, then the trees
> would start to perform better.** Second, there are strong economic arguments as to why a narrow
> focus on a single indicator might be undesirable — one may miss obvious risks that might be
> building in other areas not captured by the indicator in question or it may create significant
> arbitrage opportunities.»
То есть «one-reason decision making» здесь оказалось **не хуже, а слегка лучше** дерева из
четырёх признаков при равных весах ошибок — с оговоркой, что при асимметричных весах порядок
меняется.

**Пороги «интуитивного» дерева (дословные значения, 4 бинарных правила по порядку):**
1. balance-sheet leverage ratio **< 4,1 %** → сразу красный флаг («the exit instead automatically
   gives a red flag to all banks with a leverage ratio of less than 4.1%»);
2. market-based capital ratio (порог **16,8 %**) → красный, если сигнализирует уязвимость;
3. уровень оптового финансирования → зелёный, если ниже порога;
4. loan to deposit ratio **< 1,4** → зелёный, иначе красный.
Проверка на кейсах, дословно: UBS — «leverage ratio of 1.7% at end-2006 … automatically given
a red flag at the first cue … **the FFT completely ignores** [market-based capital ratio >16.8%
and low loan to deposit ratio]»; Wachovia — ложно-зелёный: «With a leverage ratio of 5.6% and
a market-based capital ratio of 20.4% … its loan-to-deposit ratio of 1.21 gives it a green flag
at the final cue».

**Протокол сравнения — как именно считали out-of-sample (методологический образец), дословно:**
> «To avoid overfitting, we do not estimate the thresholds of the indicators, and associated losses
> and ordering, or the sequence of exits based on the entire sample, but instead use **a training
> set containing 70% of the banks in the sample, randomly chosen**. The performance of the
> resulting tree is evaluated against the **remaining 30%** of banks. **This process of estimating
> and evaluating is repeated 1,000 times** using different training sets to average out random
> variation and is an important feature of the approach. The result is a sequence of points, each
> corresponding to a different w, which give the average hit rate and false alarm rate over all
> trees constructed with that w. Such sequences of hit and false alarm rates are commonly known as
> '**receiver operating characteristic**' (ROC) curves.»
Обобщённая функция потерь: `w × Pr(false alarm) − (1 − w) × Pr(hit)`, базовый случай w = 0,5.
Структура дерева подбирается полным перебором: «The algorithm classifies the exits by
**exhaustively enumerating all possibilities**».

🔴 **Итог сравнения FFT против логистической регрессии — дословно, с обеими сторонами:**
> «Plotting the regression results in Figure 4, we find that **the logistic regression performs
> comparably to the statistical FFT**. When the wholesale funding level indicator is included,
> **it outperforms the statistical FFT (though not the intuitive FFT)** but when that indicator is
> excluded, **the statistical FFT tends to do better**. The difference across the two exercises
> highlights the importance of considering a range of other tests … **before reaching firm
> conclusions on the relative predictive performance of each method in this context**.»
И отдельно: «The figures also include the out-of-sample performance of intuitive trees …
**Interestingly, they perform slightly better than the corresponding trees generated by the
algorithm**» — то есть дерево, построенное по экономическому смыслу вручную, обошло дерево,
подобранное алгоритмом.

🔴 **Числового AUC/Gini в статье нет**: качество выражено парами (hit rate, false alarm rate) и
ROC-кривыми на Figure 4, площадь под кривой авторы не приводят. Значения самих кривых — только
в графике, в текст прокси они не попали (ось: «False alarm rate / Hit rate», легенда
«Logit · Statistical fast-and-frugal tree · Intuitive fast-and-frugal tree», шкала 0.0–1.0).
Предостережение авторов против переусложнения — дословно: «such computationally intensive
approaches run the danger of **over-fitting the data** (Gigerenzer and Brighton (2009))».

🔴 **Оговорка по применимости, которую лидеру нельзя терять:** объект предсказания у Aikman et al.
— **банкротство БАНКА** (кросс-страновая выборка крупных банков, глобальный кризис), а не срыв
платежа физлицом. Перенос вывода на домохозяйства — экстраполяция, а не результат этой статьи.

---

## УЗЕЛ 3 — подписки, регулярные платежи, аномалии без ML

### 3а. Лицензии открытых PFM-проектов (критично для закрытого продукта)

[ЗАМЕР] Канал: `gh api -X GET https://api.github.com/repos/<owner>/<repo>`, HTTP 200, поле
`.license.spdx_id`. Снято 2026-09-17.

| Проект | Репозиторий | Лицензия SPDX | Звёзд | Годно для закрытого кода |
|---|---|---|---|---|
| Firefly III | `firefly-iii/firefly-iii` | **AGPL-3.0** | 24 648 | 🔴 НЕТ |
| Actual Budget | `actualbudget/actual` | **MIT** | 29 016 | 🟢 ДА |
| Maybe Finance | `maybe-finance/maybe` | **AGPL-3.0** | 54 282 | 🔴 НЕТ |
| Ghostfolio | `ghostfolio/ghostfolio` | **AGPL-3.0** | 9 310 | 🔴 НЕТ |

🔴 Вывод по лицензиям (факт, не мнение): три из четырёх крупнейших открытых PFM — **AGPL-3.0**,
то есть их код нельзя ни копировать, ни переписывать «по мотивам» в закрытый продукт
(AGPL распространяется и на сетевое использование). **Единственный источник, из которого
алгоритм можно заимствовать дословно — Actual Budget (MIT).**

### 3а-1. Actual Budget (MIT) — алгоритм `findSchedules` дословно по исходнику

[ЗАМЕР] Файл: `packages/loot-core/src/server/schedules/find-schedules.ts`, ветка `master`.
Канал: `curl` raw.githubusercontent.com, **HTTP 200, 10 495 байт**, снято 2026-09-17.
URL: https://github.com/actualbudget/actual/blob/master/packages/loot-core/src/server/schedules/find-schedules.ts

Механизм — **не обучение, а перебор фиксированного набора шаблонов периодичности**
с двумя допусками. Дословно из комментария в `findSchedules()` (стр. ~319-328):

> «Patterns to look for:
> * Weekly
> * Every two weeks
> * Monthly on day X
> * Monthly on every 1st or 3rd day
> * Monthly on every 2nd or 4th day
>
> Search for them approx (+- 2 days) but track which transactions
> and find the best one...»

**Допуск по дате — ±2 дня, жёстко в SQL-фильтре** (функция `getTransactions`, стр. 24-40):
```
$and: [
  { date: { $gte: d.subDays(date, 2) } },
  { date: { $lte: d.addDays(date, 2) } },
]
```

**Допуск по сумме — ±7,5 % от абсолютной величины суммы.** Определение
(`packages/loot-core/src/shared/rules.ts`, стр. 234-236; канал `curl`, HTTP 200, 5 607 байт):
```js
export function getApproxNumberThreshold(number) {
  return Math.round(Math.abs(number) * 0.075);
}
```
Применение (`find-schedules.ts`, стр. 61-70):
```js
const threshold = getApproxNumberThreshold(trans.amount);
...
t.amount >= trans.amount - threshold &&
t.amount <= trans.amount + threshold,
```
плюс **обязательное точное совпадение контрагента**: `matched.payee === payee`
(стр. 69). Переводы исключаются заранее: `'payee.transfer_acct': null`.

**Ранжирование кандидатов — обратная функция от расхождения в днях**, дословно (стр. 43-52):
```js
function getRank(day1, day2) {
  const dayDiff = Math.abs(d.differenceInDays(parseDate(day1), parseDate(day2)));
  // The amount of days off determines the rank: exact same day
  // is highest rank 1, 1 day off is .5, etc. This will find the
  // best start date that matches all the dates the closest
  return 1 / (dayDiff + 1);
}
```
Итог: расписания группируются по контрагенту, внутри группы сортируются по `rank`
по убыванию, побеждает первое (`schedules.sort((s1, s2) => s2.rank - s1.rank)`).

**Минимальное число повторов:** явной константы «N повторов» в коде НЕТ. Требование строже
и бинарное: кандидат отбрасывается, если совпадение не найдено **хотя бы в одном** из
проверяемых интервалов — `if (found.indexOf(null) !== -1) { continue; }` (стр. 76-78).
То есть периодичность должна подтвердиться на ВСЕХ сгенерированных датах шаблона.

[ОЦЕНКА] Отдельное ограничение реализации: комментарий стр. 167-170 —
«28 is the max number of days that all months are guaranteed [to have] … we'll end up
skipping months that don't have that day» — то есть дни 29-31 обрабатываются отдельной
ветвью `monthlyLastDay`, а не общим правилом.

### 3б. Статистические детекторы выбросов — первоисточники и пороги

#### MAD — Leys et al. 2013 (полный текст добыт)

[РЕЦ] Leys, C., Ley, C., Klein, O., Bernard, P., Licata, L. «Detecting outliers: Do not use
standard deviation around the mean, use absolute deviation around the median».
**Journal of Experimental Social Psychology, 2013, vol. 49, iss. 4, pp. 764–766.**
DOI: 10.1016/j.jesp.2013.03.013. Дата публикации — июль 2013 (онлайн 27.03.2013).
Канал: Exa `web_search_exa`, полный текст отдан в highlights; открытая копия —
институциональные репозитории ULB (https://dipot.ulb.ac.be/dspace/bitstream/2013/139499/1/Leys_MAD_final-libre.pdf)
и Uni.lu ORBilu (https://orbilu.uni.lu/bitstream/10993/59204/1/Leys_MAD_final-libre.pdf),
handle https://orbilu.uni.lu/handle/10993/59204. ScienceDirect — пейволл (отдал только
навигацию каталога, содержимого статьи нет).

**Константа 1,4826 — дословно:**
> «Usually, b = 1.4826, a constant linked to the assumption of normality of the data,
> disregarding the abnormality induced by outliers (Rousseeuw & Croux, 1993). If another
> underlying distribution is assumed (which is seldom the case in the field of psychology),
> this value changes to b = 1/Q(0.75), where Q(0.75) is the 0.75 quantile of that underlying
> distribution. In case of normality, 1/Q(0.75) = 1.4826 (Huber, 1981). This multiplication
> by b is crucial, as otherwise the formula for the MAD would only estimate the scale up to
> a multiplicative constant.»

**Порог — авторы рекомендуют 2,5, а не 3, дословно (рекомендации 1 и 2):**
> «1. In univariate statistics, the Median Absolute Deviation is the most robust
> dispersion/scale measure in presence of outliers, and hence we strongly recommend the
> median plus or minus 2.5 times the MAD method for outlier detection.
> 2. The threshold should be justified and the justification should clearly state that other
> concerns than cherry-picking degrees of freedom guided the selection. By default, we suggest
> a threshold of 2.5 as a reasonable choice.
> 3. We encourage researchers to report information about outliers, namely: the number of
> outliers removed and their value (or at least the distance between outliers and the selected
> threshold).»

Шкала порогов приписана Miller (1991), дословно:
> «Depending on the stringency of the researcher's criteria, which should be defined and
> justified by the researcher, Miller (1991) proposes the values of 3 (very conservative),
> 2.5 (moderately conservative) or even 2 (poorly conservative).»

**Критерий отбрасывания — две эквивалентные формы, вторая даёт «расстояние до порога»:**
`M − 3·MAD < x_i < M + 3·MAD`, либо `|(x_i − M)/MAD| > 3`. Дословно о преимуществе второй:
> «The second expression of our decision criterion leads to the same conclusion as the first
> but offers the advantage of indicating the distance of the value from the decision criterion,
> rather than proceeding by comparison with a specific value of the series.»

**Робастность — числа breakdown point (ключевой аргумент против σ и против IQR):**
- среднее: breakdown point = **0** («when a single observation has an infinite value, the mean
  of all observations becomes infinite; hence the mean's breakdown point is 0»);
- медиана и MAD: breakdown point = **0,5** («the median is the location estimator that has the
  highest breakdown point… Exactly the same can be said about the Median Absolute Deviation»);
- межквартильный размах (IQR): breakdown point = **25 %** — дословно: «It is for example more
  robust than the classical interquartile range (see Rousseeuw & Croux, 1993), which has a
  breakdown point of 25% only».

Дополнительное свойство, важное для коротких рядов, дословно:
> «Moreover, the MAD is totally immune to the sample size.»
и оценка Huber (1981, p. 107): MAD — «single most useful ancillary estimate of scale».

Атрибуция метода: «Absolute deviation from the median was (re-)discovered and popularized by
**Hampel (1974)** who attributes the idea to **Carl Friedrich Gauss** (1777–1855)».

[ЗАМЕР] Числовой пример авторов (воспроизводимый): ряд 1, 3, 3, 6, 8, 10, 10, 1000.
Медиана = 7. Абсолютные отклонения: 6, 4, 4, 1, 1, 3, 3, 993 → отсортированы 1, 1, 3, 3, 4, 4,
6, 993 → медиана отклонений = 3,5 → MAD = 3,5 × 1,4826 = **5,1891**. Границы при пороге 3:
7 ± 3·5,1891 → отбрасывается всё вне [−8,57; 22,57], то есть ровно значение 1000, и его
нормированное расстояние (1000 − 7)/5,19 = **191,36**.

Обзор практики (сам по себе [ЗАМЕР]): авторы просмотрели JPSP и Psychological Science за
2010–2012, **127 релевантных попаданий**, и — дословно — «No article mentioned used the Median
Absolute Deviation described below», при этом большинство либо не указывало метод, либо резало
по 2–3 σ вокруг среднего.

---

## УЗЕЛ 4 — текст объяснения без LLM (шаблонный NLG)

### 4а. Шаблонный NLG против «настоящего» — ключевая работа, полный текст добыт

[РЕЦ] van Deemter, K., Krahmer, E., Theune, M. «Real versus Template-Based Natural Language
Generation: A False Opposition?» — рубрика **«Squibs and Discussions»**,
**Computational Linguistics, 2005, vol. 31, no. 1, pp. 15–24.** Опубликовано 2005-03-01.
DOI: **10.1162/0891201053630291**. Открытый PDF: **https://aclanthology.org/J05-1002.pdf**
(идентификатор ACL Anthology `J05-1002`); зеркало — Tilburg University research portal
https://research.tilburguniversity.edu/en/publications/11916ff5-42fc-4699-b602-92cf2530c40f.
Канал: Exa `web_search_exa` — полный текст статьи отдан в highlights (статья короткая,
10 страниц). Цитируемость по данным Exa — **204 цитирования**.
Порядок авторов расходится между источниками: ACL Anthology и DOI-запись дают
«van Deemter, Krahmer, Theune», PDF-подпись в highlights — «van Deemter, Theune, Krahmer».

**Тезис статьи дословно (аннотация):**
> «This article challenges the received wisdom that template-based approaches to the generation
> of language are necessarily inferior to other approaches as regards their **maintainability,
> linguistic well-foundedness, and quality of output**. Some recent NLG systems that call
> themselves ''template-based'' will illustrate our claims.»

**Определение шаблонного NLG, которое даёт статья (с отсылкой к Reiter & Dale 1997, стр. 83–84):**
> «Template-based systems are natural-language-generating systems that map their nonlinguistic
> input directly (i.e., without intermediate representations) to the linguistic surface structure
> (cf. Reiter and Dale 1997, pages 83–84). Crucially, this linguistic structure may contain gaps;
> well-formed output results when the gaps are filled or, more precisely, when all the gaps have
> been replaced by linguistic structures that do not contain gaps. **(Canned text is the borderline
> case of a template without gaps.)**»

🔴 **Главный формальный аргумент — Тьюринг-эквивалентность, и это НЕ замер, а теоретический
результат, приписываемый Reiter & Dale 1997:**
> «Template-based and standard NLG systems are said to be ''**Turing equivalent**''
> (Reiter and Dale 1997); that is, each of them can generate all recursively enumerable
> languages.»
и следствие про качество вывода, дословно:
> «As for the output quality and variability of the output, if template-based systems have the
> same generative power as standard NLG systems (Reiter and Dale 1997), **there cannot be
> a difference between the types of output that they are able to generate in principle.**»

**Что именно вменялось шаблонам (та «received wisdom», с которой авторы спорят), дословно:**
> «Reiter and Dale (1997) state that template-based systems are more difficult to maintain and
> update (page 61) and that they produce poorer and less varied output (pages 60, 84) than
> standard NLG systems. Busemann and Horacek (1998) go even further by suggesting that
> template-based systems do not embody generic linguistic insights (page 238).»

**Контрдовод по сопровождаемости — ссылка на повторное использование, а не на замер:**
> «It is far from obvious that template-based systems should always score low on maintainability.
> Several template-based systems such as **TG/2, EXEMPLARS, and XTRAGEN** have been reused for
> generation in different languages or in different domains… In the case of **D2S**, the basic
> generation algorithm and such functions as ApplyTemplate and ExpressObject have been used for
> different application domains (**music, soccer games, route descriptions, and public transport**)
> and different languages (**English, Dutch, and German**)… When a template-based system is applied
> to a new domain or language, many of the templates will have to be written anew…, but the
> underlying generation mechanisms generally require little or no modification.»

**Где шаблоны прямо СИЛЬНЕЕ, дословно:**
> «The fact that templates can be specified by hand gives template-based systems an advantage in
> cases in which good linguistic rules are not (yet) available or for constructions which have
> unpredictable meanings or highly specific conditions of use.»
Вариативность достигается без обучения: «Current D2S-based systems rely mainly on random choice
to achieve variation, but more context-sensitive variations (e.g., varying the output depending on
user characteristics) can also be achieved through the use of **parametrized templates** (XTRAGEN)
or **template specialization hierarchies** (EXEMPLARS).»

**Вывод статьи дословно:**
> «We have argued that systems that call themselves template based can, **in principle, perform
> all NLG tasks in a linguistically well-founded way**… Conversely, most standard NLG systems
> perform many NLG tasks in a less than well-founded fashion (e.g., relying heavily on shortcuts,
> and nontransparent ones at that). **We doubt that there is still any important difference between
> the two classes of systems, since the variation within each of them is as great as that between
> them.**»

[ЗАМЕР] Единственное количественное наблюдение в статье — о том, насколько шаблоны игнорировались
литературой: обзор RAGS (Cahill et al. 1999) отбирал полностью реализованные системы, и — дословно —
«although these criteria appear to favor template based systems, **none of the 19 systems
investigated were template-based**». Плюс: «the only current textbook on NLG (Reiter and Dale 2000)
does not pay any attention to template-based generation, except for a passing mention of the ECRAN
system».

🔴 **Важное ограничение для лидера: человеческих оценок (числа рейтингов «шаблон vs настоящий NLG»)
в этой статье НЕТ.** Работа — теоретико-аргументативный «squib» в 10 страниц, её вклад —
Тьюринг-эквивалентность + разбор кейсов (D2S, TG/2, EXEMPLARS, XTRAGEN), а не эксперимент.
Ссылка на неё как на «замеры качества» была бы подменой класса материала.

**Связь с Mellish (2000) — про «срезки углов», дословно:**
> «Mellish argues that shortcuts have a legitimate role in practical NLG when linguistic rules
> are missing, provided the existence of the shortcuts is acknowledged… It is shortcuts of this
> kind that a template-based system is well placed to make, of course. But crucially,
> template-based systems do not have to use shortcuts any more than standard NLG systems.»

### 4б. Реализации и ЛИЦЕНЗИИ (проверено точно, критично для закрытого продукта)

#### SimpleNLG

[ЗАМЕР] Канал: `gh api -X GET https://api.github.com/repos/simplenlg/simplenlg/contents/LICENSE.md`,
HTTP 200, файл **15 857 байт**, снято 2026-09-17. (`curl` на `raw.githubusercontent.com/.../license.txt`
дал **HTTP 000** — файла с таким именем нет, реальное имя `LICENSE.md`.)

Дословно, первая строка файла:
> «SimpleNLG is licensed under the terms and conditions of **Mozilla Public License 2.0**.
> Copyright (C) 2010-11 [The University of Aberdeen](http://www.abdn.ac.uk).»

API репозитория при этом отдаёт `.license.spdx_id = "NOASSERTION"`, `.license.name = "Other"` —
то есть **автоопределению GitHub здесь верить нельзя**, лицензию пришлось читать из файла.

**Версия:** актуальный релиз — **v4.5.0**, опубликован 2020-06-07 (предыдущие: v4.4.8 —
2016-04-10, v4.4.3 — 2014-08-20). Репозиторий не архивирован, последний push 2024-12-06,
832 звезды.

🔴 **Дословное предупреждение о версиях из README** — прямо влияет на коммерческое использование:
> «Please note that earlier versions of SimpleNLG have different licensing, in particular
> **versions before V4.0 cannot be used commercially**.»

Оценка пригодности: **MPL 2.0 — file-level copyleft**, то есть в отличие от AGPL позволяет
линковку из закрытого продукта; обязанность раскрывать исходники распространяется только на
сами изменённые файлы MPL-кода («Larger Work» по п. 1.7 лицензии может быть закрытым).
То есть 🟢 годно при условии (а) версия ≥ 4.0, (б) сам код SimpleNLG не модифицируется, либо
его правки публикуются. **Но:** дословно из README — «The "official" version of SimpleNLG
only produces texts in English», русского языка в официальной версии НЕТ.

Авторство, дословно из README (важно для связи с узлом 4а):
> «It was originally developed by **Ehud Reiter**, Professor at the University of Aberdeen's
> Department of Computing Science and **co-founder of Arria NLG**.»
Заявленный охват: «Lexicon/morphology system: The default lexicon computes inflected forms
(morphological realisation). We believe this has fair coverage» + «Microplanning: Currently
just simple aggregation, hopefully will grow over time.»

#### 4г. Русская морфология — лицензии и статус поддержки

[ЗАМЕР] Каналы: `gh api` по репозиториям (HTTP 200) + `https://pypi.org/pypi/<pkg>/json`
(HTTP 200), снято 2026-09-17.

| Пакет | Репозиторий | Лицензия (PyPI `info.license` + classifier) | Версия на PyPI | GitHub `.license.spdx_id` | Последний push | Звёзд |
|---|---|---|---|---|---|---|
| **pymorphy2** | `pymorphy2/pymorphy2` | MIT (`License :: OSI Approved :: MIT License`) | **0.9.1** | **NONE** (файла лицензии в корне нет) | 2024-06-26 | 1 176 |
| **pymorphy3** | `no-plagiarism/pymorphy3` | MIT | **2.0.6** | **MIT** | **2025-10-09** | 147 |
| **petrovich** (Python) | `damirazo/petrovich` | MIT | **2.0.1** | **MIT** | 2023-06-27 | 54 |

Статус поддержки (факты, не мнение): pymorphy2 **не архивирован**, но последняя активность
2024-06-26 и версия с 0.9.1; **pymorphy3 — активный форк**, push 2025-10-09, версия 2.0.6.
Репозиторий `petrovich-team/petrovich-rb` (Ruby-оригинал) по API — **HTTP 404, "Not Found"**;
Python-порт `damirazo/petrovich` жив, но без активности с июня 2023.

🔴 Не закрыто: лицензия **словарей** (пакеты `pymorphy2-dicts-ru` на базе OpenCorpora) отдельна
от лицензии кода и в этот замер не попала — см. «Недобытое».

