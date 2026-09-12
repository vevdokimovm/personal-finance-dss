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
