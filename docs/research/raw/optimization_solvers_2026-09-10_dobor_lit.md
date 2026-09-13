# Добор первоисточников: оптимизационные солверы vs перебор (10.09.2026)

Сырьё подагента. Пункты:
- A. Fox (1966) — маржинальный анализ, условия точности жадного
- B. Federgruen & Groenevelt (1986) — необходимые и достаточные условия жадного; доп. ограничения
- C. Michaud (1989) — «estimation-error maximizers»
- D. DeMiguel, Garlappi, Uppal (2009) — 1/N, число моделей, окно оценки
- E. Gurobi / IBM и Россия
- F. Отечественные LP/MILP-солверы в реестре ПО
- G1. Двойственность для MIP; G2. Цена робастности; G3. Объяснимость оптимизации

Статус пунктов фиксируется ниже по мере добычи.

---

## E. IBM и Россия (ДОБЫТО, первоисточник IBM, полный текст)

**E1. IBM Newsroom.** Krishna A. «Update on IBM's Business Operations in Russia». IBM Newsroom, опубликовано June 07, 2022 (письмо сотрудникам от May 30, 2022).
URL: https://newsroom.ibm.com/Update-on-IBMs-Business-Operations-in-Russia — канал: curl (HTTP 200), текст извлечён из HTML.
Дословно:
> «On March 7th, I shared with you our decision to suspend IBM's business operations in Russia due to the war in Ukraine.»
> «As the consequences of the war continue to mount and uncertainty about its long-term ramifications grows, we have now made the decision to carry out an orderly wind-down of IBM's business in Russia. We see this move as both right and necessary, and a natural next step following our business suspension. This process will commence today and result in the separation of our local workforce.»
Примечание: само письмо от 07.03.2022 на newsroom в выдачу не попало; факт и дата 07.03 подтверждены этим первоисточником IBM (ссылкой автора на собственное решение).

**E2. IBM PSIRT News.** «PSIRT NEWS: IBM suspends business in Russia», запись «June 14, 2022: An update on the war in Ukraine».
URL: https://www.ibm.com/support/pages/psirt-news-ibm-suspends-business-russia (он же node/6610609) — канал: curl (HTTP 200).
Дословно:
> «IBM has suspended business in Russia, including engagement with Russian clients, business partners, suppliers, vendors, resellers, developers and OEMs and is conducting an orderly wind-down of all business there.»

Что значит для нас: IBM (правообладатель CPLEX) официально прекратил работу с российскими клиентами и партнёрами, включая реселлеров и разработчиков, и свернул бизнес. Легальная покупка/продление коммерческой лицензии CPLEX российским юрлицом через IBM закрыта; это аргумент против CPLEX в продакшене FINPILOT, независимо от технических достоинств.

## D. DeMiguel, Garlappi, Uppal (ДОБЫТО, полный текст РАБОЧЕЙ версии, не журнальной)

DeMiguel V., Garlappi L., Uppal R. (2009) «Optimal Versus Naive Diversification: How Inefficient is the 1/N Portfolio Strategy?» Review of Financial Studies 22(5):1915–1953. DOI 10.1093/rfs/hhm075.
Прочитан полный текст рабочей версии «1/N», draft June 2006, NBER Summer Institute 2006: https://users.nber.org/~confer/2006/si2006/ap/uppal.pdf — канал curl + pdftotext (HTTP 200, 409 581 байт).
Недобыто: журнальная версия. LBS `faculty.london.edu/avmiguel/DeMiguel-Garlappi-Uppal-RFS.pdf` вернул HTTP 200, но HTML-страницу, не PDF; SSRN Delivery.cfm (1376199) — HTTP 403. Поэтому номера страниц ниже — страницы РАБОЧЕЙ версии (по счёту листов PDF), не RFS 1915–1953. Числа 14 моделей / 7 датасетов / 3000 / 6000 совпадают с аннотацией RFS (Oxford Academic, SSRN 1376199 — аннотация).

Дословно (абстракт, стр. 2 PDF):
> «Of the fourteen models of optimal portfolio choice that we evaluate across seven empirical datasets, we find that none is consistently better than the 1/N rule in terms of Sharpe ratio, certainty-equivalent return, or turnover. This finding indicates that, out of sample, the gain from optimal diversification is more than offset by estimation error.»
> «for parameters calibrated to U.S. stock market data, we find that, for a portfolio with only 25 assets, the estimation window needed is more than 3,000 months, and for a portfolio with 50 assets, it is more than 6,000 months, although in practice these parameters are estimated using 120 months of data.»

Введение (стр. 6 PDF, в тексте формулировка чуть иная — «is 3,000 months», без «more than»):
> «Based on parameters calibrated to U.S. stock-market data, we find that the critical length of the estimation window is 3,000 months for a portfolio with only 25 assets, and more than 6,000 months for a portfolio with 50 assets. The severity of estimation error is startling if we consider that, in practice, these portfolio models are typically estimated using only 60 or 120 months of data.»
> «Our analytical results suggest that the error in estimating expected returns contributes much more to the poor performance of the sample-based mean-variance strategy than the error in estimating covariances.»

Раздел с симуляциями (стр. 25 PDF): «for a portfolio with 25 assets, the estimation window needed … is more than 3,000 months, and for a portfolio with 50 assets it is more than 6,000 months. In Panel E, in which the Sharpe ratio for the 1/N portfolio is only 0.08, … more than 1,600 months, and … 50 assets … more than 3,200 months.» (в оригинале вторая «Panel E» — видимо опечатка, по контексту Panel F).

Какие модели иногда обгоняли 1/N (дословно):
> «Of all the models we study, the minimum-variance portfolio with constraints studied in Jagannathan and Ma (2003) performs best in terms of Sharpe ratio. But even this model cannot deliver a Sharpe ratio or CEQ return that is statistically superior to that delivered by the 1/N strategy in any of the seven empirical datasets, and its turnover is typically higher than that of the 1/N policy.» (стр. 6)
> «The second mixture portfolio, "ew-min", outperforms the 1/N strategy for the "Industry," "International," "MKT/SMB/HML," and "FF-1-factor" datasets, but the difference is statistically significant only for the "FF-1-factor" dataset.»
> «"mv-min" strategy has a higher Sharpe ratio than the benchmark 1/N strategy only for the "MKT/SMB/HML" dataset, but even here the P-value is 0.22.»
Предостережение авторов: «the purpose of this study is not to advocate the use of the 1/N heuristic as an asset allocation strategy, but merely to use it as a benchmark».

Что значит для нас: числа 14 / 7 / 3000 (25 активов) / 6000 (50 активов) подтверждены по полному тексту (с нюансом «3,000» vs «more than 3,000» между абстрактом и введением). Главная причина — ошибка оценки СРЕДНИХ доходностей, а не ковариаций: это прямо бьёт по любой оптимизации, чья цель зависит от прогнозов доходности (у нас — прогноз SES+МК). Честная оговорка: единичные модели (ew-min, g-min-c) иногда обгоняли 1/N, но статистически значимо — в единичных датасетах.

## G1 (часть). Документация Gurobi про двойственные для MIP (ДОБЫТО, полный текст)

Gurobi Help Center, Butera G. «How do I retrieve the (dual) Pi values for a MIP problem?» Updated February 23, 2026.
URL: https://support.gurobi.com/hc/en-us/articles/360034305272-How-do-I-retrieve-the-dual-Pi-values-for-a-MIP-problem — канал curl (HTTP 200).
(Страница справочника атрибутов `docs.gurobi.com/.../constraint_linear.html` — HTTP 404, URL сменился.)
Дословно:
> «As mentioned in the documentation for Pi, this attribute is only available for convex continuous models. Shadow prices are not well-defined in mixed-integer programs, so we do not provide dual values for a model with integer variables. Note that Gurobi 9 introduced MIP scenario analysis, which can help with sensitivity analysis for MIP problems.»
> «You can, however, obtain dual information from the so-called fixed model by solving the MIP, calling method fixed() that creates a continuous model by fixing all integer variables to the values of the best solution found, solving the fixed model, and then querying the dual values for that model. However, this approach is problematic: … For integer models, continuous rates of change are not valid because some variables move in discrete steps. Reduced costs on the fixed version of an integer model reveal very little (if anything) about what happens if the integer variables change value. In fact, the dual values are not useful and meaningful for the continuous variables: There are examples where a variable has a very large reduced cost in the fixed model even though you can easily move that variable in the MIP without degrading the objective function value.»
Что значит для нас: вендор сам пишет «not well-defined», но предлагает два суррогата — fixed-model duals (с оговоркой, что они мало что говорят) и MIP scenario analysis. Значит формулировку «теневых цен для MIP не существует» надо смягчить до «в стандартном LP-смысле не определены; есть суррогаты с ограниченной интерпретацией». Литература (Gomory–Baumol, Wolsey, O'Neill) — ниже.

## F (часть). ArhiPlex (ДОБЫТО, карточка каталога АРПП)

«Программное обеспечение для решения задач линейного целочисленного программирования ArhiPlex». Правообладатель по карточке — «ЛАБОРАТОРИЯ КОРПОРАТИВНОГО СОПРОВОЖДЕНИЯ» (сайт https://arhitexlab.ru/support). Номер в Едином реестре российского ПО: **17164**, дата решения 03.04.2023 («Поручение Минцифры России от 03.04.2023 б/н»).
URL: https://catalog.arppsoft.ru/product/6240150 — канал curl (HTTP 200). Запрос: «отечественный решатель задач линейного и целочисленного программирования реестр российского ПО».
Лицензия/цена/Python API — на карточке не указаны (проверка ниже, если хватит бюджета).

## G1 (часть 2). O'Neill et al. (2005) — цены для MIP через фиксацию целочисленных (ДОБЫТО, полный текст препринта)

O'Neill R.P., Sotkiewicz P.M., Hobbs B.F., Rothkopf M.H., Stewart W.R. Jr. (2005) «Efficient market-clearing prices in markets with nonconvexities». European Journal of Operational Research 164(1):269–285.
Прочитан препринт «December, 2000; Revised November, 2003»: https://bear.warrington.ufl.edu/centers/purc/docs//papers/0541_sotkiewicz_efficient_market-clearing_prices.pdf — канал curl + pdftotext (HTTP 200). Номера страниц журнала не сверены.
Дословно (абстракт):
> «This paper addresses the existence of market clearing prices and the economic interpretation of strong duality for integer programs in the economic analysis of markets with nonconvexities (indivisibilities).»
> «We show that the optimal solution to a linear program that solves the mixed integer program has dual variables that: (1) have the traditional economic interpretation as prices; (2) explicitly price integral activities; and (3) clear the market in the presence of nonconvexities.»
Процедура (дословно):
> «1. Formulate the problem as a mixed integer program and solve. 2. Find a LP that solves the MIP by adding cuts that set the integer variables to their optimal values. 3. Use the dual variables and primal quantities from the linear program to form an efficient contract.»
Сами авторы цитируют противоположный тезис как «belief» литературы: Geoffrion & Nauss (1977): «(integer programming) models have no shadow prices or dual variables with an interpretation comparable to that in linear programming.» и далее «The economic literature continues to reflect this belief.»
Что значит для нас: это прямой контрпример к формулировке «двойственных для MIP не существует». Корректно: у MIP нет двойственных в LP-смысле «без дополнительных построений», но (а) цены получаются из LP с фиксированными целочисленными (как Gurobi fixed()), причём у O'Neill они ещё и явно «цены» целочисленных решений (платёж за бинарную активность); (б) существуют субаддитивная двойственность и ценовые функции (Gomory–Baumol 1960, Wolsey 1981 — не добыты, см. ниже). Ограничение для нас: такие «цены» локальны для выбранной целочисленной конфигурации и не говорят, что будет при переключении бинарных — это совпадает с оговоркой Gurobi.

## B (часть). Federgruen & Groenevelt (1986) — вторичный пересказ (полный текст НЕ добыт)

Оригинал: Operations Research 34(6):909–918, DOI 10.1287/opre.34.6.909. Semantic Scholar API: openAccessPdf status «CLOSED», абстракт «elided by the publisher». Сайт INFORMS не пробовался (пейволл).
Добыт пересказ в: Frank A., Murota K. «Discrete Decreasing Minimization, Part II: Views from Discrete Convex Analysis», arXiv:1808.08477 — канал curl + pdftotext, раздел литобзора (полный текст статьи Frank–Murota):
> «Federgruen–Groenevelt (1986) [7] This paper deals with base-polyhedra in Case Z. Main concern of this paper is to offer a general framework in which a greedy procedure called the marginal allocation algorithm (MAA) works. The concept of concave order is introduced as a class of admissible objective functions for which the greedy procedure works. The main result (Corollary 1 in Sec.3) states, roughly, that the MAA gives an optimal solution for every weakly concave order on polymatroids.»
> «Ibaraki–Katoh (1988) [20] … Chapter 9, entitled "Resource allocation problems under submodular constrains" presents the fundamental and up-to-date results at that time, including those by Fujishige [11], Groenevelt [15], and Federgruen–Groenevelt [7]. … The contents of Chapter 9 of this book are updated in a handbook chapter by Ibaraki–Katoh [23] in 1998. Its revised version by Katoh–Shioura–Ibaraki [24] in 2013 incorporates the views from discrete convex analysis.»
(Katoh–Shioura–Ibaraki 2013: Handbook of Combinatorial Optimization 2nd ed., pp. 2897–2988, DOI 10.1007/978-1-4419-7997-1_44 — пейволл Springer, не добыт.)

## B (вывод). Когда жадный = перебор 66 точек (вывод подагента, опирается на пересказ F–G выше, не на полный текст F–G)

Известное (по Frank–Murota о F–G 1986 и классике Fox 1966): жадный маржинальный алгоритм (MAA) точен, если (1) цель — сепарабельная вогнутая (у F–G шире: «weakly concave order»), (2) допустимое множество — целочисленные точки полиматроида (частный случай — одно ограничение суммы Σx_i ≤ B, в т.ч. с верхними границами на группы), (3) шаг дискретный и одинаковый.
- Нижняя граница floor на одну переменную: сдвиг переменной x_i' = x_i − floor_i переводит задачу обратно в полиматроид с уменьшенным бюджетом. Жадный остаётся точен (это box-ограничение; верхние границы — тоже полиматроидные). Вывод «floor = да» — логическое следствие, дословного подтверждения из F–G нет.
- ПДН ≤ 0.40 как ограничение на СУММУ долговых платежей относительно дохода: если это линейное ограничение на подмножество переменных (сумма по группе «долги» ≤ const), это ограничение полиматроидного типа (граница на группу) — жадный остаётся точен ТОЛЬКО если такие группы образуют ламинарное семейство/субмодулярную функцию. Если ПДН зависит от x нелинейно или связывает переменные с разными знаками, полиматроидность теряется и гарантии F–G нет.
- Несепарабельная цель (SAW с нормировкой по всему вектору, штрафы за взаимодействие, МК-метрики риска, зависящие от комбинации) — гарантии нет. Тогда жадный ≠ оптимум в общем случае, и перебор 66 точек остаётся единственным точным методом на этой сетке.
Итого: перебор 66 точек и жадный дают одно и то же, если функция SAW после агрегации сепарабельна и вогнута по каждой доле, а ограничения — сумма = 100% + box/групповые верхние границы. Проверка на нашей модели — эмпирическая (сравнить на тестах), это дешевле, чем доказательство.

## A. Fox (1966) (НЕ ДОБЫТ полный текст)

Fox B. (1966) «Discrete Optimization Via Marginal Analysis». Management Science 13(3):210–216, DOI 10.1287/mnsc.13.3.210. Также RAND Paper P-3288-1 (1966), DTIC AD0626604.
Каналы и что вернули:
- DTIC https://apps.dtic.mil/sti/tr/pdf/AD0626604.pdf — HTTP 200, но HTML «Under Maintenance» (1408 байт), PDF не отдан.
- RAND https://www.rand.org/pubs/papers/P3288-1.html — HTTP 200, ссылки на PDF в HTML не найдено; угаданный путь content/dam/rand/pubs/papers/2008/P3288-1.pdf — HTTP 404.
- ProQuest openview — только превью без текста. Semantic Scholar API — «CLOSED», абстракт «elided by the publisher».
- Exa — MCP-сервер не подключился (404 Server not found), канал недоступен в этой сессии.
Вторичное (аннотация по выдаче поиска, не полный текст): «discrete optimization subject to one constraint using Lagrangian analysis … generates the complete family of undominated allocations»; «incremental method … allocation of a linear and discrete resource to activities with concave return functions». Дословную формулировку теоремы добыть НЕ удалось. Рекомендация: повторить DTIC позже (maintenance временный).

## C. Michaud (1989) (полный текст НЕ добыт; цитата — вторичная, со страницей)

Michaud R.O. (1989) «The Markowitz Optimization Enigma: Is 'Optimized' Optimal?» Financial Analysts Journal 45(1):31–42, DOI 10.2469/faj.v45.n1.31.
Каналы: SSRN 2387669 (страница и Delivery.cfm) — HTTP 403; JSTOR 4479185, CFA rpc — пейволл, не пробовались глубже; Semantic Scholar — «CLOSED».
Вторичная цитата со страницей (Journal of Financial Planning / FPA, статья «End the Charade: Replacing the Efficient Frontier with the Efficient Range», https://www.financialplanningassociation.org/article/end-charade-replacing-efficient-frontier-efficient-range, curl HTTP 200):
> «Michaud (1989, 33) argued that mean-variance optimizers are, in effect, "estimation-error maximizers," allocating too much to assets that, because of imprecise estimates, show high returns, low standard deviations, or low correlations with other assets.»
Та же статья сразу даёт контраргумент: «Green and Hollifield (1992), however, found that the extreme allocations in optimized mean-variance portfolios are, in fact, inherent in mean-variance efficient portfolios constructed with precise estimates.»
Дополнительно из полного текста Michaud & Michaud «Estimation Error and Portfolio Optimization: A Resampling Solution» (New Frontier Advisors, 2005/2007; https://newfrontieradvisors.com/media/rxbld4hq/estimation-error-and-portfolio-optimization-12-05.pdf, curl + pdftotext): «RE optimization does not maximize in-sample parameters, rather it accounts for the possibility these parameters are wrong.» — само выражение «estimation-error maximizers» там по grep не найдено.
Что значит: стр. 33 и формулировка подтверждены только через вторичный источник, где цитата стоит в кавычках со страницей. Для нашего текста — ставить «(Michaud 1989, p. 33, цит. по …)» или добыть оригинал через библиотеку.

## E (часть 2). Gurobi и Россия (ДОБЫТО: EULA; публичного заявления о РФ НЕ найдено)

Gurobi Optimization, LLC «End-User License Agreement» (Standard EULA, Nov 2022): https://cdn.gurobi.com/wp-content/uploads/Gurobi_Standard_EULA_Nov2022.pdf — curl + pdftotext.
Дословно, §10.1 «Export Restrictions»:
> «You agree that You will not export, re-export, or transfer the Product or documentation, in whole or in part, to any country, person, or entity subject to U.S. export restrictions. You will not use the Product to benefit, or provide services to, any country, person, or entity subject to U.S. export restrictions. You will not permit any third party to access or use the Product (whether via delivery of on-premise software or provision of the functionality of the Product via hosting services) in violation of any U.S. export restrictions.»
Россия в EULA поимённо не названа. Статус РФ даёт BIS (вторично по выдаче поиска): «The U.S. government has imposed export licensing requirements for almost all items and technology being exported or re-exported to Russia or Belarus» (https://www.bis.gov/licensing/country-guidance/russia-belarus — не открывал, взято из сниппета).
Поиск «Gurobi Russia license sales stopped 2022» — отдельного заявления Gurobi о России не нашёл (выдача: EULA, newsroom без упоминания РФ). Страница https://www.gurobi.com/legal/export-compliance/ — HTTP 404. Страница академической программы (gurobi.com/academia/academic-program-and-licenses/) скачана, по grep «russia|embargo|export|restricted|sanction» — совпадений нет.
Что значит: для Gurobi нет «пресс-релиза об уходе», но EULA прямо запрещает использование в пользу лиц/стран под экспортными ограничениями США, включая хостинг (т.е. SaaS FINPILOT для пользователей РФ). Юридически это тот же барьер, что и у CPLEX.

## F (часть 2). ArhiPlex — детали; другие отечественные солверы

ArhiPlex (Лаборатория корпоративного сопровождения / ARHITEX), реестр №17164 (см. выше):
- Python API ЕСТЬ: пакет `arhiplexpy`. Документация «Быстрый старт» ArhiCloud (https://arhicloud.arhitex.com/documentation/quick-start/, curl HTTP 200): «Установка пакета arhiplexpy для Python»; требования «Python версий 3.8/3.11 и пакетный менеджер pip»; установка `pip install .` из каталога клиента «ArhiPlex Remote Client». В оглавлении есть разделы «Python API, C++ API, C# API, REST API, Python Matrix API», и отдельно «Двойственные решения». Есть облачный режим ArhiCloud с «Маппинг наименований и анонимизация» (важно для 152-ФЗ: задача уходит в облако вендора).
- Отдельно в реестре/каталогах: «Библиотека ArhiOMO языка python для формализации и решения задач линейного и целочисленного программирования с использованием солвера ArhiPlex», артикул ARPP-22479 (k-integration.ru, curl HTTP 200).
- Цена: публично НЕТ. platforms.su/platform/18473 (curl HTTP 200): «Цена и условия По запросу»; редакции «Стандарт — Базовая лицензия», «Профи — Расширенная лицензия», «Корпоративный — Неограниченная лицензия», все «По запросу». k-integration: «Цена: по запросу, Последнее обновление цены: 21.12.2024». Цифра «10000 руб.» из пересказа поиска первоисточником НЕ подтверждена.
- Заявление о производительности (MIPLIB2017, «первое место по методике Ганса Миттельмана») — только из сниппета поиска про сайт arhiplex.com; сам сайт curl не открыл (код 000, соединение не установлено, и с -k --http1.1 тоже). Независимой проверки на plato.asu.edu не делал — НЕ использовать как факт.
- Упоминание в сниппете vc.ru «Как решать задачи оптимизации без зарубежных солверов» и Хабр/Цифра (zyfra) «Как мы в 2 раза ускорили решение MILP» — там SCIP 8.0.3 (открытый, не отечественный). Не открывал.
Другие кандидаты: поиски «отечественный решатель задач линейного и целочисленного программирования реестр российского ПО» и «российский MILP солвер реестр ПО Python API» вернули только ArhiPlex. Солверы ИВМ РАН / ВЦ РАН, «Логос», Т-Банк в выдаче НЕ появились; отдельно не искал (бюджет). reestr.digital.gov.ru напрямую не запрашивал.

## G2. Цена робастности (ДОБЫТО: Bertsimas & Thiele 2006 полный текст; Goldfarb & Iyengar — только аннотация)

Bertsimas D., Thiele A. (2006) «A Robust Optimization Approach to Inventory Theory». Operations Research 54(1):150–168, DOI 10.1287/opre.1050.0238. Полный текст: http://web.mit.edu/dbertsim/www/papers/melvyn/A-Robust-Optimization-Approach-to-Inventory-Theory-OR54.pdf — curl + pdftotext.
Дословно (раздел численных экспериментов, R = 100·(E_DP − E_ROB)/E_DP в процентах):
> «When the assumed distribution is binomial, the ratio R increases as the standard deviation increases and the robust policy outperforms dynamic programming by up to 10% to 13%, depending on the realized distribution. When the assumed distribution is Gaussian, the two methods are equivalent because the robust policy outperforms dynamic programming by at most 0.4%.»
Из абстракта: «the robust problem is of the same difficulty as the nominal problem, that is, a linear programming problem when there are no fixed costs, and a mixed-integer programming problem when fixed costs are present.»
Там же есть и обратный случай: по grep «then DP outperforms ROB, while if h > h0, ROB outperforms DP» — выигрыш зависит от соотношения издержек.
Что значит: контрпример к «цене робастности, всегда превышающей выигрыш». Когда реальное распределение отличается от предполагаемого (ошибка модели), робастная политика дала на 10–13% меньше издержек, чем «оптимальная» DP; при верной модели разница ≤0.4%. То есть робастность почти бесплатна при правильной модели и выигрывает при ошибке. Оговорка: это инвентаризация, а не финансы домохозяйства.
Goldfarb D., Iyengar G. (2003) «Robust Portfolio Selection Problems». Mathematics of Operations Research 28(1):1–38, DOI 10.1287/moor.28.1.1.14260 — только аннотация по выдаче: робастные формулировки «combat the sensitivity of the optimal portfolio to statistical and modeling errors», сводятся к SOCP «comparable to … convex quadratic programs». Out-of-sample числа не добыты.
Дополнительно (D выше): «robust» портфель Garlappi, Uppal, Wang (2006) в DeMiguel et al. «do not outperform the naive 1/N benchmark» — робастность в портфелях сама по себе 1/N не бьёт.

## G3. Альтернативы по объяснимости (ДОБЫТО, полные тексты arXiv/авторские)

1. Aigner K.-M., Goerigk M., Hartisch M., Liers F., Miehlich A. (2024) «A Framework for Data-Driven Explainability in Mathematical Optimization». AAAI 38(19):20912–20920. Полный текст arXiv:2308.08309 (curl).
Что объясняет: объяснимость как второй критерий — сходство решения с решениями, реализованными в похожих ситуациях в прошлом. Цена: «we prove that already in simple cases the explainable model is NP-hard, we characterize relevant polynomially solvable cases such as the explainable shortest path problem». Ключевое: «It turns out that the cost of enforcing explainability can be very small.»
2. Forel A., Parmentier A., Vidal T. (2023) «Explainable Data-Driven Optimization: From Context to Decision and Back Again». ICML 2023, PMLR 202:10170–10187. Полный текст arXiv:2301.10074 (curl).
Что объясняет: контрфактуальные объяснения для конвейера «прогноз → оптимизация»: «In what alternative context would the previous expert-based solution be better than the …» [рекомендованного]. Два класса: «relative and absolute explanations» (Definition 2.1). Методы — для random forest и nearest-neighbor предикторов. Ключевое: «This lack of interpretability can block the adoption of data-driven solutions as practitioners may not understand or trust the recommended decisions.»
3. Korikov A., Shleyfman A., Beck J.C. (2021) «Counterfactual Explanations for Optimization-Based Decisions in the Context of the GDPR». IJCAI 2021. Полный текст https://tidel.mie.utoronto.ca/pubs/Korikov_ijcai21.pdf (curl).
Что объясняет: «Почему не X?» через обратную оптимизацию — минимальное изменение коэффициентов цели, при котором X стало бы оптимальным. Цена (дословно): «Our solution techniques demonstrate that the computational effort to produce an explanation is equivalent to that of the original optimization problem in the former case» [сумма взвешенных бинарных]; «Theorem 1 shows that the computational effort required to form an explanation arises solely from re-solving the original problem with the added constraint xj = 1.» Мотивация — GDPR.
Продолжения (только ссылки из выдачи, не открывал): Korikov & Beck CPAIOR 2023 «Objective-Based Counterfactual Explanations for Linear Discrete Optimization» (https://tidel.mie.utoronto.ca/pubs/inverse_cpaior2023.pdf); Kurtz, Birbil, den Hertog «Counterfactual Explanations for Linear Optimization» (arXiv:2405.15431; EJOR 2025, S0377221725004886).
4. Čyras K., Letsios D., Misener R., Toni F. (2019) «Argumentation for Explainable Scheduling». AAAI 33(01):2752–2759, DOI 10.1609/aaai.v33i01.33012752. Полный текст ojs.aaai.org (curl).
Что объясняет: почему расписание (не) допустимо, (не) эффективно, (не) удовлетворяет зафиксированным решениям пользователя, в том числе для what-if. Дословно: «optimization solvers are often unexplainable black boxes whose solutions are inaccessible to users and which users cannot interact with. We define a novel paradigm using argumentation … supported by tractable explanations which certify or refute solutions.» Узко: задача makespan scheduling.
5. Вендорские конфликт-рефайнеры (Gurobi IIS / CPLEX conflict refiner) — не добывал (бюджет); они объясняют НЕДОПУСТИМОСТЬ, а не выбор оптимума.
Что значит для вывода «X-MILP лучшее по объяснимости»: как минимум три независимые линии (контрфактуалы через обратную оптимизацию, data-driven сходство с прошлыми решениями, аргументация) дают объяснения поверх ЛЮБОГО оптимизатора, и контрфактуал Korikov стоит одного повторного решения задачи. У перебора 66 точек контрфактуал ещё дешевле: все альтернативы уже посчитаны, «почему не X» = разница оценок X и выбранной. Вывод «MILP лучший по объяснимости» надо переформулировать или снять.

## G1 (часть 3). Классика двойственности для MIP — только вторично

Guzelsoy M., Ralphs T.K. (2010) «Integer Programming Duality», статья для Wiley Encyclopedia of OR and MS. Полный текст: https://coral.ise.lehigh.edu/~ted/files/papers/Duality-EOR10.pdf (curl + pdftotext).
Дословно: «It is perhaps surprising that many of the results familiar from linear programming (LP) duality do extend to integer programming. However, this generalization requires adoption of a more general point of view on duality than is apparent from studying the linear programming case.» «In the linear programming case, the value function is piecewise linear and convex (assuming minimization), which is the reason for the tractability of the linear programming dual problem. In the integer programming case, the value function has a more complex structure». Далее: value function PILP — функция Гомори (Blair & Jeroslow 1982), двойственные функции субаддитивны.
Wolsey L.A. (1981) «Integer programming duality: Price functions and sensitivity analysis». Mathematical Programming 20:173–195, DOI 10.1007/BF01589344 — только аннотация по выдаче: «the necessity of using price functions in place of prices». Springer HTML — curl вернул страницу без абстракта. Gomory & Baumol (1960) — не добывал; упомянуты у O'Neill et al. (пример с постоянными издержками, pp. 538–540).
Итог по G1: правильная формулировка — «у MIP нет теневых ЦЕН в LP-смысле (скаляров); есть ценовые ФУНКЦИИ (субаддитивная двойственность) и цены при фиксированных целочисленных (O'Neill; Gurobi fixed())». Тезис «не существует» — неверен как стоит.

---

## Сводка статусов
- A Fox — НЕ добыт (DTIC maintenance, RAND 404). Нужен повтор.
- B F–G — полный текст НЕ добыт, есть точный вторичный пересказ + вывод о применимости.
- C Michaud — полный текст НЕ добыт; цитата с p. 33 — вторичная.
- D DeMiguel — ДОБЫТ (рабочая версия 2006, числа сверены).
- E IBM — ДОБЫТ (newsroom + PSIRT); Gurobi — EULA §10.1, заявления о РФ нет.
- F — ArhiPlex (реестр 17164, Python API arhiplexpy, цена по запросу); других не найдено.
- G1 — ДОБЫТО (Gurobi, O'Neill, Guzelsoy–Ralphs); Wolsey/Gomory–Baumol — аннотация.
- G2 — Bertsimas–Thiele ДОБЫТ; Goldfarb–Iyengar — аннотация.
- G3 — Aigner, Forel, Korikov, Čyras — ДОБЫТЫ.

## Счётчик вызовов
- WebSearch: 21
- WebFetch: 0
- curl (URL-запросов, в пакетах): 36 (из них отказов: SSRN 403 ×3, DTIC maintenance, RAND 404, Gurobi docs 404 ×2, LBS отдал HTML вместо PDF, arhiplex.com — код 000)
- Exa: недоступна (MCP-сервер 404 при подключении)

---

## ДОБОР-2 10.09.2026 (Fox / Federgruen–Groenevelt / Michaud)

Три первоисточника, не открытые предыдущим заходом:
1. Fox B. (1966) «Discrete optimization via marginal analysis», Management Science 13(3):210-216 — условия точности жадного маржинального алгоритма.
2. Federgruen A., Groenevelt H. (1986) «The greedy procedure for resource allocation problems: necessary and sufficient conditions for optimality», Operations Research 34(6):909-918.
3. Michaud R. (1989) «The Markowitz Optimization Enigma: Is "Optimized" Optimal?», Financial Analysts Journal 45(1):31-42 — «estimation-error maximizers».

Статус каждого — ниже.

### 2. Federgruen & Groenevelt (1986) — ВТОРИЧНО (первоисточник за пейволлом INFORMS)

**Библиография.** Federgruen A., Groenevelt H. «The greedy procedure for resource allocation problems: necessary and sufficient conditions for optimality». Operations Research, 1986, 34(6):909-918.
**Каналы по первоисточнику:** pubsonline.informs.org — пейволл (в выдаче есть только landing); semanticscholar — только карточка без PDF; DTIC — весь сайт отдаёт заглушку «Our Site is Getting an Upgrade» (HTTP 200, HTML вместо PDF); Springer `link.springer.com/content/pdf/10.1007/978-1-4614-6624-6_44-1.pdf` (глава Katoh–Shioura–Ibaraki «Resource Allocation Problems») — HTTP 200, но 3 КБ HTML-заглушки, не PDF.

**Добытый вторичный источник — ПОЛНЫЙ ТЕКСТ:**
Patil K., Jagannathan K., Sundaresan R. «A Survey of Algorithms for Separable Convex Optimization with Linear Ascending Constraints». arXiv:1608.08000, 42 с.
URL: https://arxiv.org/pdf/1608.08000 — канал: curl с браузерным UA, HTTP 200, 394 955 байт, `pdftotext -layout`.

Дословно (в обзоре Federgruen–Groenevelt — ссылка [4], Groenevelt 1991 — [10], Hochbaum 1994 — [12]):

Постановка (с. 15-16 PDF, раздел 4):
> «Problem Π2 : Minimize Σ_{e∈E} w_e(x(e)) subject to x ∈ B(g), x ∈ Z^E_+.
> The set of vectors satisfying the constraint set of problem Π2 form the bases of the polymatroid (E, g) defined over integers. Problem Π2 can be solved by the greedy algorithm (Federgruen and Groenevelt [4]). Starting with an initial allocation x = 0, this algorithm increases the value of a variable by one unit if the corresponding decrease in the objective function is largest among all possible feasible increments. The complexity of the greedy algorithm is O(B(log n + F )), where F is the number of operations required to check the feasibility of a given increment in a single variable.»

Ключевая оговорка о сложности там же:
> «Therefore, the complexity of the greedy algorithm is exponential in the number of input bits to the algorithm.»
(то есть жадный псевдополиномиален: линеен по ЧИСЛУ единиц B, а не по длине входа; полиномиальность даёт масштабирование Хохбаум — «Hochbaum [12] proposed a variant of the greedy algorithm that uses a scaling technique to reduce the complexity to O(n · (log n + F ) · log(B/(nǫ)))», с. 4)

Условие оптимальности (Theorem 1, с. 10 PDF; авторство приписано Groenevelt):
> «Theorem 1. A base x ∈ B(g) is an optimal solution to problem Π1 if and only if for each exchangeable pair (u, e) associated with base x (i.e., u ∈ dep(x, e, g) − {e}), we have w_e^+(x(e)) ≥ w_u^-(x(u)).»
> «The result is due to Groenevelt [10]. See Fujishige [7, Th. 8.1] for a proof of the more general result on submodular systems.»

Определение полиматроида, которое и есть «условие, при котором жадный точен» (с. 9 PDF, формулы 7-9):
> «f (∅) = 0, f (A) ≤ f (B) (A ⊆ B ⊆ E), f (A) + f (B) ≥ f (A ∪ B) + f (A ∩ B) (A, B ⊆ E). The pair (E, f ) is called a polymatroid with ground set E.»
> «B(f ) := {x ∈ P (f ) : x(E) = f (E)}»

**Что это значит для темы 40.** Жадное маржинальное распределение доказуемо оптимально ровно тогда, когда (а) целевая сепарабельна и выпукла/вогнута по каждой переменной и (б) допустимое множество — базы полиматроида (монотонная субмодулярная функция ранга). Ограничения FINPILOT — ПДН ≤ 0.40, Rt ≥ 0, целевые сроки — полиматроидную структуру не образуют: это разнородные линейные и нелинейные связи по нескольким ресурсам сразу, а не одна субмодулярная функция ранга. Значит жадный алгоритм в нашей задаче не имеет гарантии оптимальности, и ссылаться на классику Federgruen–Groenevelt как на оправдание жадного нельзя — она работает против такого выбора. Перебор 66 фиксированных точек, наоборот, даёт точный оптимум по построению на своей сетке; MILP нужен только если сетку убрать.

### 3. Michaud (1989) — ЧАСТИЧНО: дословные цитаты добыты, но ВТОРИЧНО и без номеров страниц

**Библиография.** Michaud R. O. «The Markowitz Optimization Enigma: Is "Optimized" Optimal?». Financial Analysts Journal, 1989, 45(1):31-42. DOI 10.2469/faj.v45.n1.31.

**Каналы по первоисточнику — все отказали:**
- tandfonline.com/doi/abs/10.2469/faj.v45.n1.31 — пейволл (только abs).
- jstor.org/stable/pdf/4479185.pdf — curl HTTP 200, но 3038 байт HTML-заглушки вместо PDF.
- researchgate.net (прямая ссылка на PDF в профиле автора) — HTTP 403 и через `curl` с браузерным UA, и через `WebFetch`.
- newfrontieradvisors.com (сайт самого Мишо) — HTTP 200, поиск по «enigma» PDF статьи не отдаёт: в `/media/` лежат только privacy policy, Form ADV/CRS и пресс-релиз.
- api.semanticscholar.org (paper 073b8705f28cbb8500d789e05c8ec1c45b49440c) — HTTP 429 Too Many Requests.
- html.duckduckgo.com — HTTP 202 (антибот-челлендж).
- r.jina.ai не трогали по указанию (401).

**Добытый вторичный источник — ПОЛНЫЙ ТЕКСТ:**
Palomar D. P. «Portfolio Optimization: Theory and Application», §7.5 «Drawbacks of the MVP».
URL: https://portfoliooptimizationbook.com/book/7.5-MVP-drawbacks.html — канал: WebFetch (bookdown.org отдал 301 на этот домен), HTTP 200.

Дословные цитаты из Michaud (1989), приведённые там (страница в источнике НЕ указана):
> «… it remains one of the outstanding puzzles of modern finance that MV optimization has yet to meet with widespread acceptance by the investment community …»
> «The major problem with MV optimization is its tendency to maximize the effects of errors in the input assumptions. Unconstrained MV optimization can yield results that are inferior to those of simple equal-weighting schemes.»

🔴 **Чего добыть НЕ удалось.** Точной фразы «estimation-error maximizers» в добытом вторичном источнике нет — там дословно только «tendency to maximize the effects of errors in the input assumptions». Атрибуция «estimation-error maximizers, Michaud 1989, p. 33» гуляет по литературе, но ни одним открытым первоисточником в этом заходе не подтверждена. **В тексте темы 40 эту формулировку в кавычках с номером страницы ставить нельзя**, пока PDF статьи не добыт (нужен доступ к JSTOR 4479185 или к FAJ через библиотеку). Допустимо: пересказ без кавычек либо цитата двух фраз выше со ссылкой на вторичный источник.
**Количественной оценки эффекта** в добытом фрагменте нет — есть только качественное утверждение «inferior to those of simple equal-weighting schemes» (числовая оценка того же эффекта берётся из DeMiguel–Garlappi–Uppal 2009, пункт D выше).

**Что это значит для темы 40.** Довод Мишо направлен не против оптимизации как таковой, а против оптимизации по шумным оценкам входов: чем тоньше сетка и чем свободнее оптимизатор, тем полнее он вытаскивает ошибку оценки в решение. Для FINPILOT это прямой аргумент В ПОЛЬЗУ грубой сетки из 66 точек с шагом 10%: дискретизация работает как регуляризация и физически ограничивает, насколько сильно решение может отреагировать на погрешность прогноза денежного потока. Переход на MILP/непрерывный оптимум даст более точный оптимум ФУНКЦИИ, но не более точный оптимум РЕАЛЬНОСТИ.

### 1. Fox (1966) — ВТОРИЧНО (первоисточник не открыт: DTIC на техобслуживании)

**Библиография.** Fox B. «Discrete optimization via marginal analysis». Management Science, 1966, 13(3):210-216. Он же — RAND Paper P-3288-1.

**Каналы по первоисточнику — все отказали:**
- apps.dtic.mil/sti/tr/pdf/AD0626604.pdf — HTTP 200, но вместо PDF отдана HTML-страница «Our Site is Getting an Upgrade / Under Maintenance» (1408 байт). Весь DTIC сейчас недоступен, ссылка при этом верная — её же вернул поиск с корректным заголовком статьи.
- rand.org/pubs/papers/P3288-1.html — `WebFetch` HTTP 403; `curl` с браузерным UA HTTP 200, но на странице ни одной ссылки на PDF (`href="*.pdf"` — пусто), полного текста RAND не выкладывает.
- rand.org/content/dam/rand/pubs/papers/2008/P3288-1.pdf — HTTP 404.
- pubsonline.informs.org/doi/10.1287/mnsc.13.3.210 — пейволл.
- api.semanticscholar.org (paper 47a13e55f302d78b728741b51d906573d828817f) — HTTP 429.
- link.springer.com (глава Katoh–Shioura–Ibaraki) — HTTP 200 с 3 КБ HTML-заглушки вместо PDF.

**Добытый вторичный источник — ПОЛНЫЙ ТЕКСТ:**
Zhang et al. «Discrete Effort Distribution via Regret-enabled Greedy Algorithm». arXiv:2503.11107.
URL: https://arxiv.org/pdf/2503.11107 — канал: curl с браузерным UA, HTTP 200, 542 101 байт, `pdftotext -layout`. Fox — ссылка [7] в библиографии (л. 842-843), Federgruen–Groenevelt — [9], Katoh–Ibaraki 1998 — [6].

Дословно (с. 3 PDF, введение):
> «A fundamental variant known as the simple resource allocation problem [6] involves minimizing separable convex objective functions (or maximizing separable concave objective functions) with a single linear constraint, solvable via classical greedy algorithms [7, 8]. Subsequent research has extended this framework along two directions: generalizing objective functions and complex constraints. For instance, Federgruen and Groenevelt [9] developed greedy algorithms for weakly concave objectives … Nonlinear constraints were addressed by Bretthauder and Shetty [12], who proposed a branch-and-bound algorithm for separable concave objectives.»

Здесь [7] = Fox 1966, [8] = Shih 1974. То есть три условия точности жадного маржинального алгоритма подтверждены вторичным источником с полным текстом: **(а) сепарабельная целевая, (б) вогнутая (при максимизации) / выпуклая (при минимизации), (в) ровно ОДНО линейное ограничение ресурса**, шаги целочисленные. Четвёртая деталь — что при нелинейных ограничениях жадный уже не годится и нужен branch-and-bound — сказана там же прямым текстом.

🔴 **Дословной формулировки самой теоремы Fox со страницей первоисточника (Management Science 13(3), с. 210-216) в этом заходе НЕТ.** Ставить кавычки с указанием страницы Fox нельзя. Канал, который стоит повторить, когда DTIC поднимется: `https://apps.dtic.mil/sti/tr/pdf/AD0626604.pdf` (документ AD0626604 «DISCRETE OPTIMIZATION VIA MARGINAL ANALYSIS, Bennett Fox, January 1966» — публичный, без пейволла).

**Что это значит для темы 40.** Классический результат Fox применим к задаче вида «распределить один делимый ресурс между n статьями при сепарабельной вогнутой полезности». У FINPILOT ресурс формально один (свободный денежный поток), но ограничений больше одного (ПДН ≤ 0.40, Rt ≥ 0, минимальные платежи по долгам), а целевая — SAW-свёртка нескольких критериев, вогнутость которой по каждой доле не доказана. Оба условия Fox нарушены, поэтому гарантия точности жадного не переносится. Перебор 66 точек сетки остаётся единственным способом получить точный оптимум на заявленной сетке без доказательства структурных свойств целевой; MILP имел бы смысл только вместе с переходом к непрерывным долям и линеаризацией SAW.

---

**Счётчик заходa ДОБОР-2:** ~26 действий (WebSearch ×5, WebFetch ×3, Bash/curl ×11, дозаписи в файл ×4).

**Перечень отказов с кодами:**
| Ресурс | Код | Комментарий |
|---|---|---|
| apps.dtic.mil/sti/tr/pdf/AD0626604.pdf | 200 (HTML) | заглушка «Under Maintenance», весь DTIC лежит |
| rand.org/pubs/papers/P3288-1.html | 403 (WebFetch) / 200 (curl, без PDF) | полного текста нет |
| rand.org/content/dam/.../P3288-1.pdf | 404 | пути не существует |
| link.springer.com/content/pdf/10.1007/978-1-4614-6624-6_44-1.pdf | 200 (3 КБ HTML) | антибот вместо PDF |
| jstor.org/stable/pdf/4479185.pdf | 200 (3 КБ HTML) | антибот вместо PDF |
| researchgate.net (PDF Мишо) | 403 (curl и WebFetch) | антибот |
| api.semanticscholar.org ×3 | 429 | rate limit без ключа |
| html.duckduckgo.com | 202 | антибот-челлендж |
| newfrontieradvisors.com | 200 | PDF статьи на сайте нет |
| pubsonline.informs.org (обе статьи) | пейволл | INFORMS |
| tandfonline.com (Michaud) | пейволл | Taylor & Francis |

**Итог по трём пунктам:** ни один первоисточник полным текстом не добыт; по всем трём есть вторичные источники с полным текстом и дословными цитатами (Fox — arXiv:2503.11107; Federgruen–Groenevelt — arXiv:1608.08000; Michaud — Palomar §7.5). Номеров страниц первоисточников нет ни у одного, включая знаменитое «estimation-error maximizers, p. 33» — эту атрибуцию подтвердить не удалось.

---

# ДОБОР Г4 (11.09.2026) — Fox / Federgruen–Groenevelt / Michaud, повторный заход

## Г4 — реквизиты: что подтвердилось, что было перепутано В САМОМ ЗАДАНИИ

Задание на добор Г4 содержало строку «**Fox (1966), Operations Research 34(6):909–918**».
🔴 **Это склейка двух разных работ, и файл `optimization_solvers_2026-09-10_dobor_lit.md`
уже содержал правильный вариант** — то есть исправлять надо не файл, а задание. Проверка
по Crossref (`query.bibliographic`, HTTP 200) даёт:

| Что | Правильные реквизиты | DOI |
|---|---|---|
| **Fox B.** «Discrete Optimization Via Marginal Analysis» | **Management Science, том 13, выпуск 3, страницы 210–216, ноябрь 1966** | 10.1287/mnsc.13.3.210 |
| **Federgruen A., Groenevelt H.** «The Greedy Procedure for Resource Allocation Problems: Necessary and Sufficient Conditions for Optimality» | **Operations Research, том 34, выпуск 6, страницы 909–918, декабрь 1986** | 10.1287/opre.34.6.909 |

Пагинация **34(6):909–918 принадлежит Federgruen & Groenevelt (1986)**, а не Fox. Записывать
в любых наших текстах строго раздельно.

**Полные тексты обоих — НЕ ДОБЫТЫ, причина измерена:** Unpaywall (HTTP 200) даёт для
`10.1287/mnsc.13.3.210` — **`is_oa: False`, `oa_status: "closed"`**, и для
`10.1287/opre.34.6.909` — **`is_oa: False`, `oa_status: "closed"`**. То есть **легальной
открытой копии не существует ни для одной**; это не неудача поиска, а состояние прав.
INFORMS-пейволл подтверждён на уровне метаданных, зеркала искать бессмысленно без
библиотечного доступа. Содержательные выводы по обеим работам в этом файле выше опираются на
обзор Frank–Murota и обзорные пересказы — это остаётся вторичным материалом и так и должно
цитироваться.

## 🔴 Г4 — Michaud (1989): цитата «estimation-error maximizers, p. 33» ПЕРВОИСТОЧНИКОМ НЕ ПОДТВЕРЖДЕНА. ВЕРДИКТ: НЕ ЦИТИРОВАТЬ В ТАКОМ ВИДЕ

### Реквизиты подтверждены полностью (три независимых источника)

- **Crossref:** Michaud R. «The Markowitz Optimization Enigma: Is 'Optimized' Optimal?»
  **Financial Analysts Journal, том 45, выпуск 1, страницы 31–42, январь 1989**,
  DOI **10.2469/faj.v45.n1.31**.
- **CFA Institute Research Portal** (страница издателя, добыта через `r.jina.ai`, **HTTP 200,
  1 880 байт**): «1 January 1989 **Financial Analysts Journal Volume 45, Issue 1** …
  Publisher Information: Association for Investment Management and Research, **12 pages**,
  doi.org/10.2469/faj.v45.n1.31, **ISSN/ISBN: 0015-198X**.» 12 страниц согласуется с 31–42.
- **JSTOR** `stable/4479185` (через `r.jina.ai`, HTTP 200, 10 861 байт): «Published Time:
  1989-01-01T00:00:00Z», далее только экран регистрации («Read 10 articles per month free»).

Существует также **вторая, отдельная публикация того же текста**: «The Markowitz Optimization
Enigma: Is Optimized Optimal?», **ICFA Continuing Education Series, 1989, выпуск 4,
страницы 43–54**, DOI 10.2469/cp.v1989.n4.6 (Crossref). 🔴 **У неё ДРУГАЯ пагинация (43–54).**
Это само по себе объясняет, почему ссылки «p. 33» могут не сходиться: существуют два издания
с разной нумерацией, и вторичные источники могли брать страницу из любого. Плюс SSRN-запись
того же названия с датой **2014** (DOI 10.2139/ssrn.2387669) — третья точка расхождения
по году.

### Все испробованные каналы полного текста и их отказы

| Канал | Результат |
|---|---|
| Unpaywall `10.2469/faj.v45.n1.31` | HTTP 200, **`is_oa: False`, `oa_status: "closed"`** — открытой копии нет |
| Semantic Scholar по DOI | HTTP 200, `openAccessPdf: {"url": "", "status": "CLOSED"}`, `citationCount: 1502` |
| SSRN `sol3/Delivery.cfm/SSRN_ID2387669…` | **HTTP 403 при теле 896 437 байт** — заглушка, не текст |
| SSRN `sol3/papers.cfm?abstract_id=2387669` | **HTTP 403, 896 437 байт** |
| JSTOR через `r.jina.ai` | HTTP 200, 10 861 байт — экран доступа, текста нет |
| CFA Institute через `r.jina.ai` | HTTP 200, 1 880 байт — аннотация есть, текст «CFA Institute Premium Member Content» |
| `newfrontieradvisors.com/media/1136/…pdf` (сайт автора) | **HTTP 404, 0 байт** |
| ResearchGate (две записи) | Cloudflare, закрыт (замер сессии) |
| Michaud & Michaud «Estimation Error and Portfolio Optimization: A Resampling Solution» (сайт автора, HTTP 200, 927 901 байт, `pdftotext` успешно) | **`grep` по «estimation-error maximiz» — НОЛЬ совпадений.** Единственное упоминание: «…providing a scientific veneer for marketing purposes (Michaud 1989)» |
| Centaur Reading «Why estimation alone causes Markowitz portfolio selection to fail» (HTTP 200, 250 192 байта, текст извлечён, 86 551 байт) | **`grep` по «maximiz» — НОЛЬ совпадений.** Michaud цитируется 6 раз, но только как «'Markowitz optimisation enigma' (Michaud, 1989)» и по работам 2007 года |

### 🔴 Что можно утверждать, а что нельзя

**МОЖНО — дословно из аннотации самого издателя (CFA Institute, страница статьи):**
> «The indifference of many investment practitioners to mean-variance optimization technology,
> despite its theoretical appeal, is understandable in many cases. **The major problem with MV
> optimization is its tendency to maximize the effects of errors in the input assumptions.
> Unconstrained MV optimization can yield results that are inferior to those of simple equal
> weighting schemes.** Nevertheless, MV optimization is superior to many ad hoc techniques in
> terms of integration of portfolio objectives with client constraints and efficient use of
> information. Its practical value may be enhanced by the sophisticated adjustment of inputs and
> the imposition of constraints based on fundamental investment considerations and the
> importance of priors. The operating principle should be that, **to the extent that reliable
> information is available, it should be included as part of the definition of the optimization
> procedure.**»

Это **авторская аннотация от издателя**, а не пересказ. Тезис «MV-оптимизация максимизирует
влияние ошибок входных оценок» ей подтверждён полностью. Подтверждён и второй тезис —
«безусловная MV-оптимизация может уступать простому равновзвешиванию».

🔴 **НЕЛЬЗЯ:**
1. **Ставить кавычки вокруг «estimation-error maximizers» со ссылкой на Michaud 1989** —
   выражение в добытых первичных материалах (аннотация издателя, два авторских текста самого
   Michaud) **не встречается ни разу**. Оно есть только во вторичных пересказах.
2. **Указывать страницу 33.** Она не проверена, а существование издания ICFA с пагинацией
   43–54 делает её сомнительной даже как заимствование.
3. Любая формулировка вида «Michaud (1989, p. 33) назвал оптимизаторы "estimation-error
   maximizers"» — **снять из всех наших текстов**.

### Как писать вместо этого (готовая формулировка)

> Майкл Майкод показал, что главная проблема средне-дисперсионной оптимизации — «its tendency
> to maximize the effects of errors in the input assumptions», и что безусловная MV-оптимизация
> способна давать результат хуже простого равновзвешивания (Michaud R.O. «The Markowitz
> Optimization Enigma: Is 'Optimized' Optimal?», Financial Analysts Journal, 1989, 45(1):31–42,
> DOI 10.2469/faj.v45.n1.31; цитируется по авторской аннотации издателя — полный текст закрыт,
> `oa_status: closed`).

Так утверждение остаётся истинным и проверяемым, а кавычки стоят вокруг фразы, которая
действительно есть в первичном материале. Если оригинал понадобится дословно — единственный
оставшийся путь **библиотечный доступ к FAJ или членство CFA Institute**; открытых каналов
не существует, и повторять добор без такого доступа бессмысленно.

### Почему это важно для нас по существу, а не только по цитированию

Тезис Michaud — аргумент **в пользу** нашей архитектуры: чем сложнее оптимизатор, тем сильнее
он усиливает ошибки во входных оценках. У нас входы (ожидаемые доходности, ставки, инфляция)
оцениваются с большой погрешностью, а перебор 66 фиксированных точек с шагом 10 % —
намеренно грубая сетка, которая **не даёт оптимизатору места, где разгуляться на шуме**.
Это ровно в духе последней фразы аннотации: включать в процедуру ровно столько информации,
сколько её надёжно есть. 🔴 Но сформулировать это в наших документах надо **своими словами со
ссылкой на реквизиты**, а не поддельной цитатой.

