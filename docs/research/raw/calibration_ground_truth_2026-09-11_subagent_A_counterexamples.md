# Subagent A — контрпримеры к калибровке весов SAW по наблюдаемому поведению

Дата: 2026-09-11. Инструменты: Bash+curl (OpenAlex, Crossref, Unpaywall, Semantic Scholar), WebFetch, pdftotext.
WebSearch исчерпан — не использовался ни разу.

## Блок 1. Improper linear models / flat maximum — равные веса не хуже подогнанных

### 1.0 Общий статус блока: первоисточники ЗАКРЫТЫ, все до одного

Вся классика про improper linear models и равные веса — закрытая по Unpaywall, ни одного
открытого зеркала через доступные каналы не нашлось. Реквизиты и вердикты Unpaywall дословно:

| Работа | Реквизиты | Unpaywall |
|---|---|---|
| Dawes R. M. «The robust beauty of improper linear models in decision making» | *American Psychologist*, 1979, 34(7), 571–582. DOI 10.1037/0003-066X.34.7.571 | `is_oa: false`, `oa_status: "closed"`, `best_oa_location: null` |
| Dawes R. M., Corrigan B. «Linear models in decision making» | *Psychological Bulletin*, 1974, 81(2), 95–106. DOI 10.1037/h0037613 | `is_oa: false`, `oa_status: "closed"` (Semantic Scholar: `openAccessPdf.status: "CLOSED"`) |
| Einhorn H. J., Hogarth R. M. «Unit weighting schemes for decision making» | *Organizational Behavior and Human Performance*, 1975, 13(2), 171–192. DOI 10.1016/0030-5073(75)90044-6 | `is_oa: false`, `oa_status: "closed"` |
| Wainer H. «Estimating coefficients in linear models: It don't make no nevermind» | *Psychological Bulletin*, 1976, 83(2), 213–217. DOI 10.1037/0033-2909.83.2.213 | `is_oa: false`, `oa_status: "closed"` |
| Grove W. M., Zald D. H., Lebow B. S., Snitz B. E., Nelson C. «Clinical versus mechanical prediction: A meta-analysis» | *Psychological Assessment*, 2000, 12(1), 19–30. DOI 10.1037/1040-3590.12.1.19 | `is_oa: false`, `oa_status: "closed"` |
| Dana J., Dawes R. M. «The superiority of simple alternatives to regression for social science predictions» | *Journal of Educational and Behavioral Statistics*, 2004, 29(3), 317–331. DOI 10.3102/10769986029003317 | `is_oa: false`, `oa_status: "closed"` |
| Hogarth R. M., Karelaia N. «Heuristic and linear models of judgment: Matching rules and environments» | *Psychological Review*, 2007, 114(3), 733–758. DOI 10.1037/0033-295X.114.3.733 | `is_oa: false`, `oa_status: "closed"` |

🔴 **Дословных цитат по этому блоку я НЕ привожу — я их не видел.** Реквизиты выше проверены по
Crossref/OpenAlex/Unpaywall и годны для библиографии; содержательные утверждения про «равные
веса не хуже подогнанных» здесь НЕ подтверждены первоисточником и в отчёт как факт идти
не должны. Что перепробовано: `WebFetch`-канал не использовался для платных PsycNET-страниц
(смысла нет — `oa_status: closed`), `curl` с браузерным UA по четырём известным зеркалам
Dawes 1979 (gwern.net, www2.psych.ubc.ca, pages.ucsd.edu, web.archive.org, CiteSeerX) вернул
HTML-заглушки 196–165 667 байт, ни одного PDF. `r.jina.ai` в этой сессии отдаёт 401,
Exa недоступна, `WebSearch` исчерпан — то есть поисковый канал, которым такие зеркала обычно
и находятся, был закрыт целиком. Это ограничение инструментов, а не вывод об отсутствии работ.

**Про «flat maximum»:** поиск по OpenAlex (`search` и `title_and_abstract.search:"flat maximum"`)
релевантных работ по весам в многокритериальном выборе не дал — выдача заполнена посторонним
(Bayesian model averaging, AHP, гидрология). Термин, судя по всему, ищется только полнотекстовым
поиском, которого у меня в этой сессии нет. Записываю как ОТРИЦАТЕЛЬНЫЙ РЕЗУЛЬТАТ ПОИСКА,
а не как «работ нет».

## Блок 2. Домохозяйства гасят долги неоптимально

### 2.1 Gathergood, Mahoney, Stewart, Weber — Balance-Matching Heuristic (ГЛАВНЫЙ контрпример)

**Реквизиты.** John Gathergood, Neale Mahoney, Neil Stewart, Joerg Weber. "How Do Individuals
Repay Their Debt? The Balance-Matching Heuristic." *American Economic Review*, 2019, 109(3),
pp. 844–875. DOI 10.1257/aer.20180288.

**Статус доступа.** ПРОЧИТАН ПОЛНЫЙ ТЕКСТ — по препринту NBER Working Paper No. 24161
(December 2017, Revised August 2018), https://www.nber.org/system/files/working_papers/w24161/w24161.pdf
(993 745 байт, 3467 строк текста после `pdftotext -layout`). Плюс версия Warwick WRAP
(WRAP-how-do-Americans-repay-debt-heuristic-Stewart-2019.pdf, 10 стр.).
Unpaywall по DOI журнальной версии дословно: `is_oa: True`, `oa_status: "bronze"`,
`best_oa_location.url_for_pdf: https://www.aeaweb.org/articles/pdf/doi/10.1257/aer.20180288`
— но сам aeaweb.org на `curl` с браузерным UA отдал HTML-заглушку 5.8 КБ, не PDF; поэтому
читался идентичный по содержанию NBER-препринт.

**Дословные цитаты (NBER WP 24161, revised Aug 2018).**

1. Abstract (стр. 2 PDF): «We study how individuals repay their debt using linked data on
   multiple credit cards. Repayments are not allocated to the higher interest rate card, which
   would minimize the cost of borrowing. Moreover, the degree of misallocation is invariant to
   the economic stakes, which is inconsistent with optimization frictions. Instead, we show that
   repayments are consistent with a balance-matching heuristic under which the share of
   repayments on each card is matched to the share of balances on each card. Balance matching
   captures more than half of the predictable variation in repayments and is highly persistent
   within individuals over time.»

2. Introduction (раздел 1): «To minimize interest charges, we calculate that individuals should
   allocate 97.1% of the payments in excess of the minimum to the high APR card. We show that
   individuals allocate only 51.5% of their excess payments to the high APR card, behavior that
   is virtually indistinguishable from the completely non-responsive baseline. In other words,
   85% of individuals should put 100% of their excess payments on the high interest rate card
   but only 10% do so.»

3. Раздел 3.1 «Costs of Misallocation»: «Average interest savings are increasing across the
   number of cards, rising from £65 in the two-card sample to £248 in the five-card sample.
   Because the degree of misallocation is not declining in the economic stakes of the decision,
   individuals with larger balances and larger differences in interest rates have a substantial
   cost of misallocation, with the 90th percentile rising from £167 in the two-card sample to
   £927 in the five-card sample.»

4. Раздел 1 (про ML-бенчмарк): «Consistent with the poor fit of the optimal repayment rule, we
   find that interest rates have low variable importance (i.e., proportional increase in R²) in
   our machine learning models. Consistent with the balance matching results, we find that
   balances have the highest variable importance...»

5. Раздел 1 (кросс-культурная устойчивость ошибки): «the share of payments in excess of the
   minimum misallocated to the high APR card is 50% among Mexican credit card holders and 46%
   among U.K. credit card holders... The results in our paper show, to the contrary, the same
   degree of non-optimal repayments even in the U.K., providing a striking example of uniformity
   of a behavioral bias across very different cultures and financial settings.»

**Что это значит для калибровки весов по поведению.** Прямое опровержение идеи. На том самом
классе решений, который решает наш продукт (как распределить свободный платёж между долгами),
наблюдаемое поведение почти ортогонально оптимуму: 51.5% против нормативных 97.1%, то есть
статистически неотличимо от «людям всё равно». Модель, обученная на этих данных, воспроизвела
бы balance matching — и вес ставки по кредиту вышел бы близким к нулю («interest rates have low
variable importance»). Это ровно та ошибка, которую Avalanche-фильтр призван исправлять.
Важнее всего пункт «degree of misallocation is invariant to the economic stakes»: ошибка не
исчезает там, где цена ошибки высока (90-й процентиль £927/год), значит её нельзя списать на
рациональную экономию внимания и оправдать как «скрытое предпочтение».


### 2.2 Snowball vs Avalanche и 1/N — из того же полного текста (NBER WP 24161)

**Дословно, раздел 5.1–5.4 и сноски.**

1. Раздел 5.3, Heuristic 4: «Repay the card with the lowest balance ("debt snowball method").
   Allocate payments to the lowest balance card, subject to paying the minimum on the other
   card... This heuristic is sometimes referred to as the debt snowball method by financial
   advisors. Proponents argue that paying off a card with a low balance generates a "win" that
   motivates further repayment behavior. If an individual fully pays off a card, this heuristic
   has the additional benefit of "simplifying" the individual's debt portfolio. See also Amar et
   al. (2011) and Brown and Lahey (2015) for laboratory evidence on this approach to debt
   repayment.»

2. Сноска 36 (цитата Дэйва Рэмси, приведённая авторами дословно): «But when you ditch the small
   debt first, you see progress. That one debt is out of your life forever. Soon the second debt
   will follow, and then the next. These little wins will give you a confidence boost, you'll see
   that the plan is working, and you'll stick to it.»

3. Раздел 5.4 «Interest Payments Under Different Heuristics»: «All the heuristics have median
   savings close to zero, but have wide dispersion in savings or losses...» (сравнение идёт
   против первой строки — «the interest saving from optimal payment on the first row as a
   benchmark»).

4. Раздел 5.2 / сноска 9 про 1/N: «The one exception is the 1/N heuristic, which captures some
   behavior exactly, and has a comparable goodness-of-fit with the root mean square error
   metric», и «If we think 1/N is something that individuals implement exactly, then the 1/N
   rule [captures] 11.7% [of individuals]... Under the 1/N heuristic, payments are equal across
   cards, and the steady state balances are unchanged relative to the status quo.»

**Что это значит для калибровки весов по поведению.** Два следствия.
(а) Snowball авторы описывают как правило, продвигаемое **финансовыми советниками**, с
мотивационным, а не денежным обоснованием; денежно оно у них — одна из эвристик с медианной
экономией около нуля против оптимума. То есть «выигрыш по доведению до конца» в этой работе
не измерен, он взят как заявление сторонников — ссылки на измерение идут к Amar et al. (2011)
и Brown & Lahey (2015), которых я не открыл (см. «НЕ ДОБЫТО»).
(б) 1/N — прямое предупреждение конкретно для нашей SAW-свёртки: равное размазывание платежа
между долгами наблюдается у заметной доли людей и при этом **не меняет стационарные балансы
вообще**, экономия ровно ноль. Модель, выучившая веса из поведения, унаследует и это.

## Блок 3. Circularity: нормативное против дескриптивного в decision support

### 3.1 Ядро проблемы circularity — прямо из Gathergood et al. (единственный полный текст, который я открыл)

Отдельных работ по «circularity» (нормативная модель, откалиброванная по поведению, которое
она же должна исправлять) я в доступных каналах **не добыл** — см. «НЕ ДОБЫТО». Но у
Gathergood et al. есть методологически тот же аргумент в явном виде, и он сильнее, чем
абстрактное рассуждение, потому что подкреплён данными.

**Дословно (раздел 1, NBER WP 24161).** «To provide an upper benchmark, we use machine learning
techniques to find the repayment model that maximizes out-of-sample fit using a rich set of
explanatory variables... We find that balance matching captures more than half of the
"predictable variation" in repayment behavior.»

И дальше: «Consistent with the poor fit of the optimal repayment rule, we find that interest
rates have low variable importance (i.e., proportional increase in R²) in our machine learning
models.»

**Что это значит для калибровки весов по поведению.** Это и есть эксперимент, который мы бы
поставили, если бы стали учить веса у данных: авторы уже обучили ML-модель максимального
качества на реальных данных о погашении. Результат — модель с максимальным фитом воспроизводит
эвристику, а нормативно ключевой признак (процентная ставка) получает низкую важность.
Обученные по поведению веса — это описание ошибки, а не предпочтений. Продукт, который
советует то, что люди и так делают, не имеет причин существовать.

Отдельно: у авторов есть прямой довод против оправдания «это скрытые предпочтения / рациональная
невнимательность» — «the degree of misallocation is invariant to the economic stakes, which is
inconsistent with optimization frictions» (Abstract). Если бы поведение было рациональной
экономией внимания, ошибка убывала бы там, где ставки высоки. Она не убывает.

## ПРЯМОЙ ОТВЕТ

**Кратко: ДА, вредно — в той форме, в какой идея сформулирована («учиться весам у данных о том,
как домохозяйства реально распределяют деньги»). Полезной она становится только при жёстком
разделении ролей, см. условия ниже.**

**На чём это стоит.** Один источник, но прочитанный полностью и бьющий ровно в наш класс задач:
Gathergood, Mahoney, Stewart & Weber, *AER* 2019 (читан по NBER WP 24161, rev. Aug 2018).
Три его факта решают вопрос:

1. Наблюдаемое распределение платежей между долгами почти ортогонально оптимуму: 51.5% избыточного
   платежа на дорогую карту против нормативных 97.1%; «85% of individuals should put 100% of their
   excess payments on the high interest rate card but only 10% do so».
2. Ошибка **не убывает с ростом ставок** («invariant to the economic stakes, which is inconsistent
   with optimization frictions») — значит её нельзя переименовать в «скрытые предпочтения» или
   «рациональную невнимательность» и тем самым легализовать как обучающий сигнал.
3. Эксперимент «а что если выучить модель у данных» **уже поставлен авторами**: ML-модель с
   максимальным out-of-sample фитом даёт ставке низкую variable importance, а балансам —
   наивысшую. Выученные веса = balance matching, то есть ровно та ошибка, которую Avalanche-фильтр
   должен исправлять. Обучение по поведению здесь не улучшает СППР, а отключает её.

Плюс 1/N: равное размазывание платежа наблюдается у заметной доли людей и «the steady state
balances are unchanged relative to the status quo» — экономия ноль. Для SAW это буквальный
сценарий вырождения весов в равные.

**При каких условиях калибровка по поведению всё же допустима.** Три роли, и только они:
- **приёмистость, а не оптимальность.** Поведенческие данные годятся для калибровки того,
  ЧТО человек согласится исполнить (какую долю FCF реально направит, доведёт ли до конца),
  и не годятся для калибровки того, что оптимально. Это два разных объекта; смешивать их
  в одной SAW-свёртке нельзя.
- **только там, где нормативного оптимума нет.** Аллокация между «резерв» и «цели» (горизонт,
  склонность к риску, ценность целей) нормативно недоопределена — тут поведение информативно.
  Аллокация между долгами по ставке определена однозначно — тут не информативно вообще.
- **никогда как единственный критерий фита.** Если веса подбираются по максимизации соответствия
  наблюдаемому поведению, целевая функция буквально награждает воспроизведение balance matching.
  Нужна внешняя нормативная метрика (переплата, срок выхода из долга) как обязательный гейт.

**Чего я НЕ могу утверждать по итогам этой сессии.** Что «равные веса не хуже экспертных»
(Dawes/Wainer/Einhorn–Hogarth) — реквизиты собраны, тексты закрыты, дословных цитат нет.
Что snowball выигрывает по доведению до конца — у Gathergood et al. это пересказ позиции
финансовых советников, а первичные эксперименты (Amar et al. 2011; Kettle et al. 2016;
Brown & Lahey 2015) закрыты.

## НЕ ДОБЫТО

| Работа | Реквизиты | Вердикт Unpaywall дословно | Что пробовал |
|---|---|---|---|
| Dawes 1979, *Am. Psychologist* 34(7):571–582 | DOI 10.1037/0003-066X.34.7.571 | `is_oa: false`, `oa_status: "closed"`, `best_oa_location: null`; Semantic Scholar: `not found` | 5 зеркал через `curl` с браузерным UA — все HTML-заглушки |
| Dawes & Corrigan 1974, *Psych. Bulletin* 81(2):95–106 | DOI 10.1037/h0037613 | `is_oa: false`, `oa_status: "closed"`; S2 `openAccessPdf.status: "CLOSED"` | Unpaywall + S2 |
| Einhorn & Hogarth 1975, *OBHP* 13(2):171–192 | DOI 10.1016/0030-5073(75)90044-6 | `is_oa: false`, `oa_status: "closed"`; S2 `"CLOSED"` | Unpaywall + S2 |
| Wainer 1976, *Psych. Bulletin* 83(2):213–217 | DOI 10.1037/0033-2909.83.2.213 | `is_oa: false`, `oa_status: "closed"`; S2 `"CLOSED"` | Unpaywall + S2 |
| Grove et al. 2000, *Psych. Assessment* 12(1):19–30 | DOI 10.1037/1040-3590.12.1.19 | `is_oa: false`, `oa_status: "closed"` | Unpaywall |
| Dana & Dawes 2004, *JEBS* 29(3):317–331 | DOI 10.3102/10769986029003317 | `is_oa: false`, `oa_status: "closed"` | Crossref + Unpaywall |
| Hogarth & Karelaia 2007, *Psych. Review* 114(3):733–758 | DOI 10.1037/0033-295X.114.3.733 | `is_oa: false`, `oa_status: "closed"` | Crossref + Unpaywall; есть смежный SSRN-препринт DOI 10.2139/ssrn.1002514 (не открывал) |
| Amar, Ariely, Ayal, Cryder, Rick 2011, *JMR* 48(SPL):S38–S50 | DOI 10.1509/jmkr.48.SPL.S38 | `is_oa: false`, `oa_status: "closed"`, единственная локация — сам DOI | Unpaywall + OpenAlex `locations` (ни одного репозитория); `people.duke.edu` — 196 байт HTML |
| Kettle, Trudel, Blanchard, Häubl 2016, *JCR* 43(3):460–477 | DOI 10.1093/jcr/ucw037 | `is_oa: false`, `oa_status: "closed"` | OpenAlex `locations`: 5 записей, все `is_oa: false` (UniSG Alexandria ×2, HighWire, RePEc) |
| Besharat, Carrillat, Ladik 2014, *J. Public Policy & Marketing* 33(2):143–158 | DOI 10.1509/jppm.13.007 | `is_oa: true`, `oa_status: "green"`, локация `https://hdl.handle.net/10072/436844` | Разрешил handle через DSpace 7 API Griffith (item uuid `eabfcf0b-42c8-4cdb-88f4-efe885580d9b`), запросил bundles — **есть только два бандла LICENSE, бандла ORIGINAL с файлом нет**. То есть green-запись без файла: Unpaywall говорит «OA», а полного текста по этой локации физически нет |
| Gathergood & Weber 2014, *JEBO* 107(B):455–469 (co-holding) | DOI 10.1016/j.jebo.2014.04.018 | `is_oa: true`, `oa_status: "hybrid"`, `url_for_pdf: https://www.sciencedirect.com/science/article/pii/S0167268114001231/pdf` | Не скачивал — бюджет действий кончился. **Это самая дешёвая дыра для добора: гибрид, PDF-ссылка известна.** |
| Telyukova 2013, *Review of Economic Studies* (credit card debt puzzle) | DOI 10.1093/restud/rds050 | Unpaywall вернул не-JSON (пустой ответ) — статус НЕ установлен, DOI требует перепроверки | — |
| Brown & Lahey 2015 (лабораторные эксперименты по snowball) | реквизиты не установлены | — | Упоминается у Gathergood et al.; отдельно не искал |
| «Circularity» / normative-vs-descriptive в prescriptive analytics | — | — | Поиск по OpenAlex без полнотекстового канала не дал релевантного; `WebSearch` исчерпан, Exa 404, `r.jina.ai` 401. Записано как отрицательный результат поиска, а не как отсутствие литературы |

**Честно про инструменты.** В этой сессии были закрыты сразу три канала обнаружения
(`WebSearch`, Exa, `r.jina.ai`), остались только API метаданных и прямой `curl`. API метаданных
находят работу по известному названию, но не находят её зеркала — поэтому блок 1 остался без
полных текстов, хотя зеркала Dawes 1979 в вебе почти наверняка есть. Это ограничение прогона,
и оно повлияло на результат: блок 1 держится на реквизитах, блок 2 — на прочитанном тексте.

---

## ДОБОР Г31.2 — прокси (16.09.2026)

**Каналы на начало работы:** `r.jina.ai` **без UA** — 🟢 (контроль `monarchmoney.com/pricing`:
**200, 5 509 б**; тот же адрес с браузерным UA — **403, 5 743 б**, капча самого прокси).
Exa — 🟢. Crossref, Unpaywall, NBER — 🟢. **В исходной сессии этого файла были мертвы три канала
обнаружения из четырёх** (`WebSearch` 400/400, Exa 404, `r.jina.ai` 401) — именно поэтому блок 1
остался без полных текстов, о чём агент честно написал сам.

### Г31.2-15. 🔴 Brown & Lahey — РАБОТА ОПОЗНАНА И ДОБЫТА ЦЕЛИКОМ (было «реквизиты не установлены, отдельно не искал»)

**Реквизиты (Crossref, HTTP 200):** Brown A. L., Lahey J. N. «**Small Victories: Creating Intrinsic
Motivation in Task Completion and Debt Repayment**», *Journal of Marketing Research*, **2015**,
**DOI 10.1509/jmr.14.0281**. Рабочая версия — **NBER Working Paper № 20125, май 2014**,
«Small Victories: Creating Intrinsic Motivation in **Savings and** Debt Reduction»,
**DOI 10.3386/w20125**, JEL C91, D03, D14.

**Канал:** `curl` с браузерным UA по `nber.org/system/files/working_papers/w20125/w20125.pdf` →
**HTTP 200, 769 726 байт PDF** → `pdftotext -layout` → **110 658 знаков**. Прокси и Exa
не понадобились. 🔴 Пункт был не «закрыт», а **не искался**.

#### Первичный материал — ДОСЛОВНО (NBER WP 20125)

**Абстракт:**
> «One popular approach contradicts traditional economic theory by suggesting that people in debt
> should **pay off their debts from smallest size to largest regardless of interest rate**, to realize
> quick motivational gains from eliminating debts. We more broadly define this idea as "**small
> victories**"… Consistent with the idea of small victories, we find that when a mildly unpleasant
> task is broken down into parts of unequal size, subjects complete these parts **faster when they
> are arranged in ascending order** (i.e., from smallest to largest) rather than descending order…
> **Yet when subjects are given the choice over three different orderings, subjects choose the
> ascending ordering least often.**»

**Результат эксперимента 1 (дословно):**
> «…subjects performed in the ascending ordering **1.42 seconds per cell faster** on average than in
> the descending ordering (**significant at the 5% level**)… when ascending is compared to the pooled
> results of both descending and even orders (**1.23 seconds per cell faster**, two-sided
> **p = 0.019**). …A Kruskal-Wallis test indicates the differences for all three orders are
> significant at the 10% level (**p = 0.084**). Both the Cuzick trend test and the Jonckheere-Terpstra
> test… find the ascending-even-descending ordering to be significant, with **p-values of 0.0260
> and 0.0265**.»
> «A higher percentage of subjects (**71%, 22 of 31**) complete the task in ascending than
> **descending (48%, 14 of 29)** or **even (58%, 18 of 31)**. A Pearson's chi-square test reveals
> this difference is meaningful at the **10% level**.»

**Результат эксперимента 2 и гетерогенность (дословно):**
> «In a second study we find when subjects are given the opportunity to choose among all three orders
> they **choose the ascending ordering, the one that provides the most motivational benefit, least
> often**. Additionally, regression results suggest there is **subject heterogeneity** in the benefits
> of the small victories approach. Those with **higher self-control, better critical reasoning skills,
> and higher risk aversion**… **benefit more** from having chosen ascending. We argue a plausible
> extension of this result suggests **the people least in need of this intervention are the ones most
> likely to benefit from it**.»

🔴 **Границы применимости, названные самими авторами (дословно):**
> «…we show in Section VI that it will **only be useful to borrowers in specific cases of debt-reduction
> where interest rates between loans do not differ greatly. In the event of large differences in
> interest rates**…» (далее авторы разбирают, что мотивационный выигрыш перекрывается процентными
> потерями).
> Механизм признан **социально-когнитивным**, а не goal-gradient: «suggesting **social-cognitive
> factors dominate** in this environment» — ускорение идёт от накопления завершённых подзадач,
> а не от приближения к концу текущей.

#### Выжимка — что это значит для нашего долгового контура

1. 🔴 **Это лабораторное подтверждение snowball с точно очерченной границей, и граница — наша.**
   Эффект «малых побед» существует и измерен (ascending быстрее descending, 71 % против 48 %
   доведённых до конца), **но авторы сами ограничивают его случаем, когда ставки по долгам
   различаются несильно**. Наш Avalanche-фильтр оптимизирует ровно по ставке — то есть спор
   «snowball против avalanche» в первоисточнике решается **не в пользу одного из методов, а через
   разброс ставок в конкретном портфеле долгов**.
2. 🔴 **Самый неудобный для продукта результат:** при свободном выборе люди выбирают ascending
   **реже всего**, а выигрывают от него сильнее те, у кого и так выше самоконтроль. То есть
   «дать пользователю выбрать стратегию» — не нейтральная опция: она систематически уводит от
   порядка, дающего мотивационный выигрыш, и работает лучше всего на тех, кому помощь нужна меньше.
   Это довод за **рекомендацию по умолчанию с объяснением**, а не за меню стратегий.
3. 🟡 **Перенос ограничен**: лаборатория, задача копирования ячеек за 30 минут, n порядка 30 на
   ячейку дизайна, значимости на уровне 5–10 %. Числа брать как направление эффекта, не как
   величину для нашей модели.
4. ⚪ **Канон не меняется.** Avalanche остаётся; появляется обоснованное место для оговорки
   в пользовательском объяснении: при близких ставках порядок «от меньшего долга» стоит
   мотивационно дороже, чем проигрывает по процентам.

### Г31.2-16. 🟡 Gathergood & Weber 2014 («самая дешёвая дыра для добора») — числа добыты, полный текст нет

**Каналы 16.09.2026:**

| Канал | Адрес | Результат |
|---|---|---|
| `curl`+UA | `nottingham-repository.worktribe.com/726053/1/1-s2.0-S0167268114001231-main.pdf` | **HTTP 403, 5 808 б** HTML |
| `r.jina.ai` **без UA** | тот же PDF | **200 у прокси, 578 б**, «Performing security verification… This website uses a security service to protect against malicious bots» — 🔴 **и без UA антибот держит** |
| `mcp__exa__web_search_exa` | — | 🟢 нашла репозиторную копию (CC BY 4.0, 419 Кб) и SSRN `abstract_id=2005031` |
| `mcp__exa__web_fetch_exa` | тот же PDF | 200, но отдана **карточка репозитория**, не тело PDF |

**Добыто дословно (абстракт авторов, совпадает в трёх независимых копиях — репозиторий Ноттингема,
SSRN, издательская карточка):**
> «We use UK survey data to analyze the puzzling co-existence of high cost revolving consumer credit
> alongside low yield liquid savings in household balance sheets, which we name the '**co-holding
> puzzle**'. **Approximately 12% of households in our sample co-hold, on average, £3800 of revolving
> consumer credit** on which they incur interest charges, **even though they could immediately pay
> down all this debt using their liquid assets**. Co-holders are typically **more financially
> literate, with above average income and education**. In most estimates co-holding is also associated
> with **impulsive spending behavior**… Our results provide empirical support to theoretical models
> in which households **co-hold as a means of managing self-control problems**.»
Лицензия репозиторной копии — **CC BY 4.0**; депонирована 07.09.2015; том 107, JEBO.

**Что это меняет:** 🔴 **прямой контрпример нашему инварианту «свободный поток сначала на долг
по максимальной ставке».** 12 % британских домохозяйств осознанно держат дорогой револьверный
долг (£3 800 в среднем) при достаточной ликвидности — и это **не безграмотность**: со-держатели
**более** финансово грамотны и обеспечены, а механизм — управление самоконтролем. Для продукта это
означает: рекомендация «погасить карту из резерва» будет отвергаться частью пользователей
рационально, и это не дефект расчёта. Полный текст (регрессии, спецификации) **не добыт** —
остаётся задолженностью.

### Г31.2-17. Перепроверенные реквизиты и оставшееся закрытым

| Пункт | Замер 16.09.2026 | Итог |
|---|---|---|
| **Telyukova 2013** | 🔴 **DOI в нашей таблице НЕВЕРЕН.** `10.1093/restud/rds050` → Unpaywall **404 Not Found** (не «пустой ответ» — такого DOI нет). Crossref: правильный — **`10.1093/restud/rdt001`**, «Household Need for Liquidity and the Credit Card Debt Puzzle», *The Review of Economic Studies*, **09.01.2013** | реквизиты исправлены; полный текст не запрашивался — задолженность |
| Dawes 1979; Dawes & Corrigan 1974; Einhorn & Hogarth 1975; Wainer 1976; Grove et al. 2000; Hogarth & Karelaia 2007; Amar et al. 2011; Kettle et al. 2016 | не переоткрывались в этом подбатче | по части из них Г30.1 уже дал абстракты (Einhorn & Hogarth, Dana & Dawes) — см. `approach_validity`; остальные — `closed` по Unpaywall, не класс антибота |
| Besharat, Carrillat & Ladik 2014 | не переоткрывался | установлено ранее: green-запись без файла в бандле — дефект репозитория, не канал |
| «Circularity» / normative-vs-descriptive | не переоткрывался — бюджет | 🔴 **ЗАДОЛЖЕННОСТЬ**: именно этот пункт был закрыт при трёх мёртвых каналах и остаётся самым непроверенным в файле |

## ИТОГ Г31.2 (в этом файле)

- Закрыт **1 пункт полностью** (Brown & Lahey: опознан, добыт целиком, 110 658 знаков),
  **1 частично** (Gathergood & Weber: ключевые числа дословно, полный текст нет),
  **1 исправлен по реквизитам** (Telyukova: DOI в нашей таблице не существует).
- 🔴 **Нашей ошибкой вызова прокси не оказался ни один пункт** — репозиторий Ноттингема держит
  антибот и без UA.
- 🔴 **Ошибка «отказ инструмента = отсутствие источника» — 2 раза:** Brown & Lahey **не искались
  вовсе** при мёртвых каналах обнаружения, а лежат в открытом NBER; Gathergood & Weber записаны
  как «не скачивал — бюджет», хотя открытая копия под CC BY существует.
- 🔴 **Содержательно это самый важный блок подбатча:** добыт первоисточник, который одновременно
  **подтверждает** мотивационный эффект snowball и **ограничивает** его случаем близких ставок,
  плюс показывает, что свободный выбор стратегии уводит людей от полезного порядка. Канон
  (Avalanche-фильтр) **не опровергнут**; появляется материал для формулировки объяснения
  пользователю и довод против «меню стратегий».

### ЗАДОЛЖЕННОСТЬ Г31.2 (по этому файлу)

1. Полный текст **Gathergood & Weber 2014** — репозиторий Ноттингема за антиботом; непробованное:
   SSRN `Delivery.cfm` по `abstract_id=2005031`, CORE, OpenAIRE.
2. **Telyukova 2013** по исправленному DOI `10.1093/restud/rdt001` — Unpaywall/репозитории UCSD.
3. Участок «**circularity / normative-vs-descriptive в prescriptive analytics**» — поисковый заход
   на живых каналах не делался ни разу.

---

# 🔴 СВОДНЫЙ ИТОГ ПОДБАТЧА Г31.2 (16.09.2026) — по всем семи тронутым файлам

*Сводка положена сюда как в последний тронутый файл; блоки `## ИТОГ Г31.2` есть в каждом.*

## 1. Главное число подбатча

🔴 **Нашей ошибкой вызова прокси (браузерный UA) не оказался НИ ОДИН из 12 перепроверенных
отказов — ноль.**

При этом **сама ошибка реальна и замерена в этом же прогоне**:
`https://r.jina.ai/https://www.monarchmoney.com/pricing` **без UA** → **HTTP 200, 5 509 байт
содержимого**; тот же адрес, тот же прокси, **с UA Chrome/127** → **HTTP 403, 5 743 байта**,
`<title>Just a moment...` (Cloudflare **самого прокси**). Гипотеза Г31.3 подтверждена как класс
и **опровергнута как объяснение наших конкретных записей**: все зафиксированные «прокси не пробил
Cloudflare» относятся к защите **целевого сайта**, которая держится и без UA. Проверено на
`maps.org.uk`, `onlinelibrary.wiley.com`, `papers.ssrn.com`, `sciencedirect.com` (двумя адресами),
`help.monarch.com`, `psidonline.isr.umich.edu`, `nottingham-repository.worktribe.com`, `habr.com`.

🔴 **Отдельный вывод по каналу, годный на будущее:** у прокси есть **устойчивая сигнатура отказа
цели** — тело **300–600 байт** с заголовком `Just a moment...` либо `Warning: Target URL returned
error 403`. Тело в сотню килобайт с тем же заголовком (ScienceDirect, 112 999 б) — оболочка
Cloudflare, тоже пустышка. **Прокси пробивает Springer, но не пробивает Wiley, ScienceDirect, SSRN,
Cloudflare-защиту MaPS, Хабра, PSID и Worktribe.**

## 2. Второе число, и оно оказалось важнее

🔴 **Ошибка «отказ инструмента записан как отсутствие источника» — 7 раз за подбатч**
(в Г30.1–Г30.4 — 20 раз, в Г30.4 — 9, в Г31.1 — вскрыт ложный «Wayback лежит»):

| # | Пункт | Что было записано | Что оказалось |
|---|---|---|---|
| 1 | MaPS FFT, опросник | «Wayback лежит» (Г24) | Wayback **replay** отдал PDF с первой попытки |
| 2 | Choupani & Mamdoohi 2016 | «Wayback — HTML вместо PDF» | проверялся только адрес `/pdf`; **страница статьи** в архиве содержит абстракт |
| 3 | Khashadourian 2024 | «Exa недоступна в этой сессии» | Exa по адресу **из Unpaywall** (`pdfdirect`) отдала полный текст |
| 4 | Roy 1991 | «Springer закрыт» | прокси Springer **пробивает** (у статьи 1991 г. просто нет абстракта на странице) |
| 5 | PSID | «сайт 403, данных не добыл» | соседний хост `simba.isr.umich.edu` открыт, документация с кодами переменных находится поиском |
| 6 | Brown & Lahey 2015 | «отдельно не искал» | лежит в **открытом NBER** (WP 20125), 769 726 б PDF |
| 7 | Gathergood & Weber 2014 | «не скачивал — бюджет» | открытая копия **CC BY 4.0** существует; числа добыты |

**Вывод для протокола:** класс, ради которого заводился Г31, реален, но его причина не в UA
и не в прокси. Она в том, что **отказ ОДНОГО адреса записывается как свойство источника**.
Дешёвая профилактика, подтверждённая трижды за этот подбатч: спросить Unpaywall/Crossref точный
адрес OA-локации **до** попытки фетча; пробовать **соседний адрес того же ресурса** (страница
вместо PDF, второй хост, рабочая версия вместо журнальной).

## 3. Что закрыто

| Файл | Пункт | Было | Стало | Канал |
|---|---|---|---|---|
| `causal_effect_measurement` | X5 Tech, «От A/B к Causal Inference» | Хабр 403, «вне приоритета» | 🟢 **полный текст** | Exa |
| `bank_patents_wellness_scoring` + `competitors_2026_refresh` | MaPS Financial Fitness Tool | «9 формулировок и веса не добыты» | 🟢 **все 9 вопросов дословно + 4 принципа взвешивания + методика из 5 шагов** | **Wayback replay** (снимок 23.06.2024) + Exa |
| `approach_validity` | Khashadourian & Harrison 2024 | Wiley 403, Exa не подключена | 🟢 **полный текст**, 4 коэффициента с порогами | Exa по адресу из Unpaywall |
| `calibration_…_subagent_B` | PSID, долговой блок | «не установлено по всем колонкам» | 🟢 **установлен с кодами переменных и оговорками** | Exa (User Guide ISR) + прокси |
| `calibration_…_subagent_A` | Brown & Lahey | «реквизиты не установлены» | 🟢 **опознана и добыта целиком** | `curl` → NBER PDF → `pdftotext` |
| `calibration_ground_truth` | Choupani & Mamdoohi 2016 | «не добыт ничем» | 🟡 **абстракт дословно** | Wayback replay страницы статьи |
| `calibration_…_subagent_A` | Gathergood & Weber 2014 | «не скачивал» | 🟡 **ключевые числа дословно** | Exa |
| `macro_in_forecast` | Gust et al., JEDC | «отказ канала, Exa 503» | ⚪ **переклассифицирован в пейволл** + реквизиты и поправка к аффилиации | Exa |
| `approach_validity` | Roy 1991 | «Springer закрыт» | ⚪ **канал открыт, тела статьи нет** | прокси |

**Итого: 5 пунктов закрыто полностью, 2 частично, 1 переклассифицирован, 1 исправлен по
реквизитам (Telyukova: DOI `10.1093/restud/rds050` не существует, верный — `10.1093/restud/rdt001`),
1 поправка авторства (Khashadourian — авторов двое).**

## 4. 🔴 Меняет ли добытое канон, прогноз, новизну или юрблок

**Канон модели v3.0.0 — НЕТ. Формулировку новизны — НЕТ. Юрблок — НЕТ. Прогноз — НЕТ.**
Изменения касаются **опор и формулировок объяснений**, и это материал для решения владельца,
а не правка:

1. 🔴 **Долговой контур — самое содержательное.** Brown & Lahey (NBER WP 20125): эффект «малых
   побед» измерен (ascending на **1,42 с/ячейку** быстрее descending, p < 0,05; доведших задачу
   до конца **71 % против 48 %**), **но сами авторы ограничивают его случаем, когда ставки
   по долгам различаются несильно**. Avalanche не опровергнут; появляется обоснованное место
   для оговорки в пользовательском объяснении. Второй результат той же работы —
   **при свободном выборе люди выбирают выигрышный порядок реже всего**, а выигрывают от него
   те, у кого выше самоконтроль, — довод **против «меню стратегий»** и за рекомендацию
   по умолчанию с объяснением.
2. 🔴 **Контрпример инварианту «поток сначала на дорогой долг».** Gathergood & Weber: **12 %**
   британских домохозяйств держат в среднем **£3 800** дорогого револьверного долга при достаточной
   ликвидности, и это поведение **более** грамотных и обеспеченных — управление самоконтролем.
   Часть отказов от нашей рекомендации будет рациональной.
3. 🔴 **Участок валидности: шкала CFPB больше не эталон.** Khashadourian & Harrison 2024
   (рецензируемо): соответствие объективной типологии и CFPB есть, но довод CFPB «высокое σ баллов
   ⇒ объективные показатели не работают» назван неточным и, возможно, отражающим **шум в данных**.
   Взамен — внешний набор контуров EMH с числами: свободный поток **> 3 %** расходов, постоянные
   расходы **≤ 65 %**, неипотечная долговая нагрузка **< 15 %** дохода, резерв **≥ 200 %** месячных
   расходов (коридор 200–600 %), и иерархия **поток → бюджет → долг → резерв**, совпадающая
   с нашей по порядку.
4. 🔴 **Резерв: два независимых внешних ориентира сошлись.** MaPS (государственный инструмент UK)
   меряет резерв ступенями до «**6 months or longer**»; американские эталоны — **2–6 месяцев**.
   Наш дефолт попадает в подтверждённый коридор.
5. 🟡 **Калибровка популяции.** Choupani & Mamdoohi: целочисление после IPF («unbiased tabular
   rounding **should be developed**») и **zero-cell** — открытые проблемы, а не детали реализации;
   авторы рекомендуют **симуляционный** синтез. PSID: `credit card debt` **исключает convenience
   use**; компоненты **импутированы hot-deck**; формулировка вопроса меняет ответ радикально
   (**57 %** ответивших «нет» на сложный вопрос отвечали «да» на простой).
6. 🟡 **Причинная оценка.** X5 Tech — второй российский промышленный первоисточник после ВТБ:
   при мягком самоотборе ошибка I рода **12 % вместо 5 %** и «стремится к 100 %» при жёстком;
   снижать дисперсию (CUPED), не сняв смещение, — строить доверительный интервал вокруг ложного
   эффекта.

## 5. ЗАДОЛЖЕННОСТЬ Г31.2 — непройденное, отдельным списком (не выдаётся за результат)

1. **DeMiguel, Garlappi & Uppal 2009** — не переоткрывался (бюджет). Приём: Unpaywall → адрес
   OA-локации → Exa по нему (сработал на Khashadourian).
2. **Wang & Luo 2009** — ScienceDirect закрыт прокси и Exa. Непробованное: Wayback replay
   **страницы статьи** (сработало на Choupani).
3. **Полный текст Gathergood & Weber 2014** — Worktribe за антиботом; непробованное: SSRN
   `Delivery.cfm` (`abstract_id=2005031`), CORE, OpenAIRE.
4. **Telyukova 2013** по исправленному DOI `10.1093/restud/rdt001`.
5. **«Circularity / normative-vs-descriptive в prescriptive analytics»** — поисковый заход
   на живых каналах не делался ни разу.
6. **Смещение прогнозов Минэка в п. п. (график АКРА)** — нужен **OCR** (`tesseract`), канал
   в системе есть, по пункту не применялся.
7. **Economic Record 2022 (Wiley)**, **Choupani 2017 (CEUS)**, **CBA–MI Tech Reports № 2/3/5**
   (за логином Okta), **реестр ФИПС** (блокировка по сети), **WO2026074314A1 / KR102121857B1** —
   действия владельца или платные/институциональные каналы, поиском не решаются.

**Метод подбатча:** один агент, **подагентов 0**; `WebSearch` — **0 вызовов**;
`mcp__exa__web_search_exa` — 2, `mcp__exa__web_fetch_exa` — 5; `curl` через `r.jina.ai` **без UA** —
16 адресов, `curl` прямой — 6, Wayback replay — 4, Crossref — 3, Unpaywall — 3, `pdftotext` — 3 PDF.
Все семь файлов дописаны `cat >>` по ходу работы, до итогового ответа.
