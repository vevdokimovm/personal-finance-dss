# Г44 — Оценка эффекта советов на длинной дистанции до накопления исходов

> Дата: 2026-09-17. Батч Г44 (GAP_QUEUE). Статус: ЗАВЕРШЁН (пункты 1–6 закрыты; недобор — в «Что осталось неизвестным»).
> Сырьё пишется по ходу; итог — блок «ИТОГ Г44» в конце.

**Состояние каналов (17.09.2026, `curl -skL --max-time 25`, код HTTP):** OpenAlex 200 · Crossref 200 · EuropePMC 200 ·
Semantic Scholar `search/bulk` 200 · `r.jina.ai` (без UA) 200 · Unpaywall (`email=research@example.org`) 200 · arXiv API 200 ·
`www.hse.ru/rlms/` 200 · `www.cpc.unc.edu/projects/rlms-hse` 200 (редирект на `rlms-hse.cpc.unc.edu`) ·
`rlms-hse.ru` — **000** (нет соединения; `curl -sk --http1.1` тоже 000; через `r.jina.ai` — 422) — домен не отвечает, сайт проекта живёт
на `hse.ru/rlms` · Exa (`mcp__exa__web_search_exa`) — **работает** (выдача по Athey et al., 5 результатов).

> Постановка: `docs/research/queue/GAP_QUEUE.md`, раздел «Г44» (6 пунктов). Вход (не переоткрывается): тема 37
> `causal_effect_measurement_2026-09-10.md`; тема 27 `prescriptive_quality_metrics_2026-09-10.md` (OPE не определён без логов
> и propensity); Г30.1 `approach_validity_2026-09-10.md` §2.4 и стр. ~2685, ~3566 (Прентис, Fleming & DeMets 1996 — дословно добыты);
> Г39 `math_core_verification_plan_2026-09-17.md` (симулятор `p0b_sim.py`, кризисный сценарий, журнал исходов, 30,7 %);
> `rf_household_finance_stats_v2_2026-09-10.md` Д9.3 (условия RLMS — дословно добыты), `debt_data_sources_rf_2026-09-10.md` п. 17–18.
> Код продукта, канон, tests — не правились. Скрипты — `scratchpad/g44/`, вывод дословно ниже.

**Процесс.** Шаг 0: вопрос — «как узнать длинный эффект до длинных данных»; форма ответа — таблица методов по силе
доказательства + сырьё по 6 пунктам. Три способа ответа рассматривались: (а) обзор литературы по каждому пункту;
(б) только численный стенд; (в) литература по ключевым узлам (surrogate index, OPE, панели, шкалы благополучия) + один малый
стенд, показывающий и пользу, и замкнутую петлю симуляции. Выбран (в): (а) без стенда не отвечает «что это даст нам»,
(б) без литературы повторяет ошибку Г31.4 (проверка моделью самой себя). Классификация — breadth-first (6 независимых пунктов).
**Подагентов — 0** (правило проекта «лучше без подагентов»; пункты короткие, вход уже собран).

---

## Источник-опора: surrogate index (Athey, Chetty, Imbens, Kang)

Реквизиты: Athey S., Chetty R., Imbens G. W., Kang H. «The Surrogate Index: Combining Short-Term Proxies to Estimate Long-Term
Treatment Effects More Rapidly and Precisely». NBER WP 26463 (2019, rev. Aug 2024), DOI 10.3386/w26463; опубликовано:
**Review of Economic Studies 93(4):2284–2312, 2026** (реквизит со страницы NBER). Канал: **Exa** (`web_search_exa`, выдача содержит
текст nber.org, doi.org, opportunityinsights.org PDF 03.2024). Данные и код: Zenodo doi 10.5281/zenodo.13732512.

Дословно:
> «Under the Prentice surrogacy assumption, which requires that the primary outcome is independent of the treatment conditional
> on the surrogates, we show that the average treatment effect on the surrogate index equals the treatment effect on the
> long-term outcome.»
> «We show that the difference in the mean surrogate index identifies the ATE on the primary (long-term) outcome when three
> assumptions hold: unconfoundedness, surrogacy, and comparability.»
> «Comparability requires that the conditional distribution of the primary outcome given the surrogates is the same in the
> observational and experimental samples.»
> «Under these three assumptions, the ATE on the primary outcome is just identified and hence the assumptions jointly do not
> have any testable implications.»
> «Rather than waiting a full nine years to directly observe the long-term impact, we show that it is possible to use short-term
> (the first six quarters) outcomes as surrogates. One could have estimated the program's long-term impacts on mean employment
> rates using the employment rates observed in the first six quarters, with a 35% reduction in standard errors.»
> «We recognize that the credibility of the Surrogacy assumption may be questioned in any given application, especially when
> viewed in isolation. Therefore, we view the best path forward as building a "library" of surrogate indices…»
> «Following an approach popularized by LaLonde (1986), we put aside part of the data and investigate whether we could have
> estimated the long-term effects without having long-term experimental data.»

**Что это значит для нас (материал, не решение).** Метод требует ТРЁХ вещей: (1) рандомизированного (или неискажённого)
сравнения «с советом / без» на коротком окне; (2) **второй, наблюдательной выборки**, где видны и ранние сигналы, и длинный
исход — чтобы выучить «ранние сигналы → исход через 1–3 года»; (3) допущения, что связь одинакова в обеих выборках.
Для п. (2) у РФ-продукта кандидат — панель RLMS (см. п. 2 ниже). Шесть кварталов у авторов = 1,5 года — это не «3 месяца»:
в их задаче короткое окно было длиннее, чем хочет владелец.

---

## Пункт 1. Симуляция на синтетических когортах (сырьё литературы)

**Аналогия.** Авиатренажёр: пилота можно «уронить» в грозу тысячу раз, не дожидаясь настоящей грозы. Но тренажёр учит только
тем грозам, которые в него заложил конструктор: если конструктор ошибся в физике, пилот научится летать в неправильной грозе.

### 1.1 ЕЦБ: стресс-тест балансов домохозяйств на микроданных (образец «шоки на реальных людях»)
Реквизиты: Ampudia M., van Vlokhoven H., Żochowski D. «Financial fragility of euro area households». ECB WP 1737 (2014);
J. Financial Stability 27:250–262 (2016). Канал: WebSearch (реквизиты) → WebFetch на
https://www.ecb.europa.eu/pub/pdf/scpwps/ecbwp1737.en.pdf отказался разбирать PDF, **сохранил файл** → `pdftotext` (112 593 байта).
Дословно:
> «We propose a novel framework to identify distressed households by taking account of both the solvency and the liquidity
> situation of an individual household. Using the data from the Household Finance and Consumption Survey and the country‐level
> data on non‐performing loans we calibrate our metric of distress and estimate stress‐test elasticities in response to an
> interest rate shock, an income shock and a house price shock.»
> «It states that a household is considered to be in distress if the household's negative financial margin for a determined
> number of months, M, is greater than the household's liquid assets.»
> «We do not take into account any possible changes in future income…»
> «We assume that the unemployment rate increases by 5 percentage points. The distribution of the shock is based on personal
> characteristics such as age, gender, education, marital status and the presence of dependent children in the household.
> Their labour income is replaced by unemployment benefits.»
> «the interest rate shock is a 300 basis points increase in the interest rate. … The house price shock is a decline of 20% of
> the value of real estate.»
> «In section 3.3 we will calibrate our metric using the observed non‐performing loans ratios by country.»
> «we cannot consider households that are able but unwilling to service their debt. Issues such as strategic defaults are beyond
> the scope…»

**Что взять.** (1) Определение беды «финансовая маржа < 0 И ликвидности не хватает на M месяцев» — почти буквально наша
метрика кризисного хвоста Г39; (2) **якорь вне модели**: порог M и вероятность дефолта калибруются по *наблюдаемой* доле
просроченных кредитов (NPL) — это и есть способ разорвать замкнутую петлю: симулятор обязан воспроизвести внешнее число,
которое в него не закладывали. Для РФ аналог — доля кредитов с просрочкой 90+ из статистики ЦБ / НБКИ (в этом батче не добывалось).
(3) Шоки задаются не «всем одинаково», а по вероятности, зависящей от характеристик человека.

### 1.2 Валидация агентных моделей: Windrum, Fagiolo, Moneta (2007)
Реквизиты: Windrum P., Fagiolo G., Moneta A. «Empirical Validation of Agent-Based Models: Alternatives and Prospects».
JASSS 10(2):8, 2007. https://www.jasss.org/10/2/8.html — **WebFetch 200** (выжимка малой модели, цитаты короткие):
> «the indirect calibration approach first performs validation, and then indirectly calibrates the model by focusing on the
> parameters that are consistent with output validation.» (§4.4)
> «The main difference with the Indirect Calibration approach is that here one tries to pick empirical parameters directly to
> calibrate the model.» (§4.10, подход Werker–Brenner)
> «AB models with realistic assumptions and agent descriptions invariably contain many degrees of freedom.» (§5.1)
**Что взять.** Правило «откалибровал на одних данных — проверяй на других» (калибровка ≠ валидация); чем больше свободных
параметров, тем легче симулятору «подогнаться» и тем меньше стоит его совпадение с реальностью.

### 1.3 Как разорвать замкнутую петлю (синтез по 1.1–1.2 и Г31.4, материал)
Симулятор, построенный на допущениях модели (доход по тому же генератору, человек выполняет совет на 100 %, расходы не меняются),
проверяет только арифметику, не пользу. Три развязки: (а) **входы — из реальных данных**, не из генератора (ОДПФ/RLMS
распределения дохода, долгов, частоты потери работы); (б) **поведение — не из модели**: доля выполнения советов, «откат» к
тратам — из литературы исполнения (тема `behavioral_execution_gap`) и варьируется как неизвестный параметр; (в) **внешний якорь**:
симулятор без совета обязан воспроизвести наблюдаемые доли беды в РФ (доля с автономией 0–1 мес. 65,0 % по ОДПФ — тема 35;
доля с просрочками — КОУЖ/ВНДН вопрос 10), прежде чем ему можно верить на сравнении «с советом».

---

## Пункт 3. Суррогатные конечные точки в финансовом благополучии (сырьё)

**Аналогия.** Врач не ждёт 10 лет инфаркта — он меряет давление. Но таблетка может снижать давление и не спасать от инфаркта
(ровно предупреждение Fleming & DeMets 1996, добыто в Г30.1: «A correlate does not a surrogate make»).

### 3.1 Подушка как ранний сигнал беды через 3 года — Sabat & Gallagher (2020, AARP PRI)
Страница: https://www.aarp.org/pri/topics/work-finances-retirement/financial-security-retirement/short-term-emergency-savings/ —
**WebFetch 200** (выжимка малой модели). Авторы: Jorge Sabat, Emily A. Gallagher, ноябрь 2020; панель 4 года + 3 года наблюдения.
> «achieving this savings buffer at any point in a four-year period is associated with a 9.5 percentage point decrease in the
> likelihood that a household will experience extreme hardship three years later» (буфер — $2 452 ликвидных сбережений)
> «It is important to note that this analysis speaks to correlation and not causation. It is possible that improvements in
> financial well-being…is the underlying factor that permits a household to both accumulate a savings buffer and also experience
> less hardship over time.»
Беда определена через: нехватку еды, неуплату коммуналки, неуплату аренды/ипотеки, отказ от медпомощи.
**Вывод:** подушка — **коррелят** беды через 3 года с измеренной силой (−9,5 п.п.), но авторы прямо отказываются от причинности.
По Прентису это условие (1) из двух; условие (2) «эффект совета на подушку передаёт весь эффект на беду» не проверено никем.

### 3.2 Gjertson (2016) — сбережения на экстренный случай и последующие лишения
Реквизиты: Gjertson L. «Emergency Saving and Household Hardship». J. Family and Economic Issues 37:1–17 (2016),
DOI 10.1007/s10834-014-9434-z. Канал: WebSearch (сниппет Springer, первоисточник не открывался в этом прогоне):
> «households who saved for emergencies experienced slightly less overall hardship and were less likely to report several specific
> hardships, such as food insecurity and having a phone disconnected.» (продольная выборка Making Connections, Annie E. Casey)

### 3.3 Шкала CFPB Financial Well-Being
- CFPB, «Financial Well-Being Scale: Scale development technical report», май 2017,
  https://www.consumerfinance.gov/data-research/research-reports/financial-well-being-technical-report/ (сниппет WebSearch):
  баллы «positively correlated with self-assessed credit quality and negatively correlated with debt in collections and economic
  hardships». 10 и 5 вопросов. **Продольной проверки «шкала сейчас → беда через годы» в технорепорте по сниппету не видно.**
- Khashadourian et al. 2024, Financial Planning Review, DOI 10.1002/cfp2.1194 — «Perceptions or behavior? An evaluation of CFPB's
  financial well‐being scale using household financial ratios». WebFetch — **403**; `r.jina.ai` — страница без текста статьи
  (grep по «well-being|ratio|find» пусто, exit 1). Exa — см. ниже, если добран.

### 3.4 Затухание эффекта — Fernandes, Lynch, Netemeyer (2014)
Реквизиты: Management Science 60(8):1861–1883, DOI 10.1287/mnsc.2013.1849. Канал: WebSearch (сниппеты SSRN/RePEc; ACM DL — известный
403). Сниппет:
> «even large interventions with many hours of instruction have negligible effects on behavior 20 months or more from the time of
> intervention»; интервенции объясняют «only 0.1% of the variance in financial behaviors studied, with weaker effects in low-income samples».
🔴 **Главное для Г44:** короткий эффект финансового вмешательства **не переносится** на 20+ месяцев сам собой — эффект затухает.
Значит, любой суррогат «через 3 месяца» без поправки на затухание завысит длинный эффект. Это прямой аргумент против наивного
«через 3 месяца стало лучше → через 2 года тоже».

### 3.5 Реальный пример длинного замера — Urban Institute (Theodos et al., 2015)
https://www.urban.org/research/publication/evaluation-impacts-and-implementation-approaches-financial-coaching-programs —
WebFetch **403**; `r.jina.ai` **200** (текст аннотации):
> «This report presents findings from a randomized controlled trial of two financial coaching programs that serve low- and
> moderate-income people. … Study findings suggest that a well-implemented coaching program with engaged clients can produce
> important improvements in certain financial outcomes.»
Сниппет WebSearch: на одном сайте рост сбережений и кредитного рейтинга, на другом — снижение совокупного и просроченного долга.
Длительность наблюдения на странице не указана (в этом прогоне не добыта).

---

## Пункт 5. Стресс-траектории и худшие случаи (сырьё)
Опора — ЕЦБ (1.1): метрика — **доля домохозяйств в беде** до и после шока, а не среднее. Дословно из обзора там же:
> «adverse scenario which combines shocks to house prices, unemployment rates and interest rates the percentage of households in
> distress increases from 13.9 to 20.9 percent» (ссылка на предшествующую работу, стр. ~255 текста WP 1737).
Для нас: метрика кризисного хвоста Г39 («доля портретов, у которых совет дал больше экстренного долга в месяце без дохода»,
30,7 % у пути (б)) — та же форма. Стенд ниже считает её на 24 месяцах.

---

## Пункт 2. Исторический бэктест на панельных данных (сырьё)

**Аналогия.** Проверить навигатор на записях прошлых поездок: берём реальный маршрут человека и спрашиваем, куда бы он приехал,
если бы слушал навигатор. Сложность: мы видим только ту дорогу, которую человек реально выбрал, — «что было бы» не записано.

### 2.1 RLMS-HSE (РМЭЗ НИУ ВШЭ): доступ
- Условия (дословно добыты ранее, Д9.3 `rf_household_finance_stats_v2`): Household & Individual 1994–2024 — **DUA No, IRB No**,
  «available to download without any application process»; ограничение — «only for analysis purposes», запрет идентификации;
  обязательная ссылка в публикациях. Запрета коммерческого использования в тексте нет, но и явного разрешения нет → письменный
  запрос в НИУ ВШЭ и CPC до коммерческого применения (там же). На `hse.ru/rlms/data` — «Добавлены данные 34-й волны 2025 года».
- Сейчас (17.09.2026): `hse.ru/rlms/` 200; на странице — разделы «Условия доступа к данным», «Лонгитюдное обследование домохозяйств
  РМЭЗ НИУ ВШЭ представляет собой серию ежегодных общенациональных репрезентативных опросов на базе вероятностной
  стратифицированной многоступенчатой территориальной выборки», «Вопросники 34-й волны» (новость 28.08.2026),
  «Как правильно приклеить к домохозяйственному файлу данные предыдущей волны» (скан `curl -skL`, текст страниц).
- `rlms-hse.cpc.unc.edu` (через Exa): «Demoscope and the HSE have prepared longitudinal files containing all years of data from 1994,
  both for the individual data (adults and children) and the household data. … Individual and household identifiers are available
  on each observation so that researchers can examine changes over time.»
- `hse.ru/en/rlms/construct` (через Exa): готовый набор «Constructed Variables Dataset 1994-2024» (SPSS 29,2 МБ / Stata 30,2 МБ):
  Household Assets, Expenditures, Income, Poverty Line; «only families with complete economic information were included».
- Профиль данных: Popkin B., Kozyreva P., Kosolapov M. и др. «Data Resource Profile: RLMS-HSE Phase II … 1994–2013».
  Int. J. Epidemiology 45(2):395–401 (2016). PDF `rlms-hse.cpc.unc.edu/wp-content/uploads/index-178.pdf` — `curl` с UA **200**,
  882 632 байта → `pdftotext`. Дословно: «The target sample size was set at 4 000 households. A multistage probability sample of
  households was…»; ядро домохозяйственного блока (через Exa): «in-depth food, clothes and consumer durables during 3 months,
  savings, transfer payments … income from all wage and non-wage sources … and drawing down savings».

### 2.2 RLMS: какие переменные про долги и сбережения — по анкете домохозяйства 23-й волны (2014)
Файл `rlms-hse.cpc.unc.edu/wp-content/uploads/R23_hh_eng_rus.pdf` — `curl` с UA **200**, 352 441 байт → `pdftotext`
(анкета взрослого `R23_adult_eng_rus.pdf` — **404**). Дословно найденные вопросы:
> «F14.6. Tell me, please: Did any member of your family take a line of credit in the last 12 months?» (HWTAKCRE)
> «14.7. For what purpose did you take a line of credit?» — «Mortgage credit for purchasing house, real estate … 1 / For purchasing a
> car … 2 / … Consumer credit in a bank for any purposes … 6»
> «F14.8. Tell me, please: Does your family have any credit debts today?» (HWCREDD)
> «F14.9. How much money does your family owe in credit today?»
> «F14.10. … Does your family have any money debts to private persons today?»
> «13. … In the last 30 days, did your family … 1.1 Take money on credit … How much in rubles?» (HWTCRED, HWTCREDV)
> «7.2. For payment of credit, repayment of loans … Yes» (блок расходов за 30 дней)
> «12_A. Imagine an unpleasant situation in which all members of your family lost their sources of income. How long do you think your
> family would be able to live at your present level--in other words, without decreasing your expenditures--without any income?
> Consider only your savings, not selling any of your possessions.» — «Half a year or longer / A few months / Not longer than a month /
> … two weeks / … a week / Not even one day» (HWSAVTYM)
> «13. … 2. Spend savings, sell jewelry, foreign currency savings»
> «E12.1. Name your total debts.» (долг за жильё и ЖКУ, HWUNPAID)

**Чего в анкете нет (по grep «credit|loan|debt|owe|savings|borrow»): ставки кредита, срока, помесячного графика, суммы
сбережений в рублях** (только интервал «сколько продержитесь»). Периодичность — **раз в год**.

### 2.3 Годится ли RLMS для бэктеста ИМЕННО нашего совета — оценка (материал)
- 🔴 **Прямой бэктест совета — нет.** Совет ядра помесячный и требует ставок, платежей, остатков по каждому долгу и суммы подушки;
  в RLMS — годовые снимки, долг одной суммой, без ставки, подушка интервалом. «Прогнать совет по реальной траектории» нельзя:
  нельзя ни построить вход ядра, ни пересчитать траекторию при другом распределении денег (контрфакт не наблюдается никогда —
  это не свойство RLMS, а свойство любого бэктеста решения, в отличие от бэктеста прогноза).
- **Годится для трёх косвенных задач:** (а) **внешний якорь симулятора** (п. 1.3): частоты потери дохода, переходы «нет долга →
  долг», «подушка несколько месяцев → не больше месяца» год к году — то, что симулятор без совета обязан воспроизвести;
  (б) **обучающая выборка для суррогатного индекса** (Athey et al., условие comparability): «сигналы года t (есть ли кредит,
  расходы на выплаты / доход, подушка по HWSAVTYM, брали ли в долг за 30 дней) → беда в t+1…t+3 (долг частным лицам, долг по ЖКУ,
  продажа вещей, подушка "not even one day")»; (в) распределения портретов для генератора.
- Годовой шаг против помесячного продукта — главное несоответствие: суррогат «3 месяца» по RLMS не строится; строится «1 год → 2–3 года».
- ОДПФ ЦБ (Г23): микроданные открыты и **есть ставки по кредитам**, но это не панель (повторные срезы 2013–2024) → годится для
  входов и якорей, не для «сигнал → исход у того же человека». ВНДН Росстата (Д9.4): покредитный блок со ставкой и платежом, ежегодно
  2012–2025, CC BY 4.0 через tochno.st — **тоже срезы**, не панель (панельность ВНДН в этом прогоне не проверялась).

### 2.4 Зарубежные панели для сравнения
- **PSID (США).** WebSearch-сниппеты psidonline.isr.umich.edu: «Public Use Data are available free of cost to all researchers who
  register, and agree to the Conditions of Use»; модуль богатства «first included in 1984 and was included again in 1989, 1994, 1999,
  and every wave since then»; «conducted annually from 1968 through 1997 and has been conducted biennially since 1997»; в 2015 —
  блок финансовых трудностей (проблемы с выплатами, ипотека, изъятие жилья). Шаг — 2 года.
- **Understanding Society (UKHLS, Великобритания).** Сниппеты understandingsociety.ac.uk: три уровня доступа (End User Licence,
  Special Licence, Secure); «Commercial organisations can apply for access… For some data the terms of consent may prohibit commercial
  access. Commercial organisations are required to demonstrate the public benefits». Шаг — год.
- **SHARE** — в этом прогоне не добывалось (WebSearch/Exa не запускались по SHARE: бюджет пункта отдан RLMS; известно лишь, что
  панель охватывает 50+, т. е. не наш сегмент — это утверждение не подтверждено источником в этом файле).
- **Вывод:** ни одна панель не даёт помесячных транзакций; помесячные панели существуют только у банков и агрегаторов
  (тема 37 / Г30.1: ВТБ). Это переносит «настоящий» бэктест в данные самого продукта после запуска (п. 6).

---

## Пункт 4. Оценка политики по нерандомизированным данным (off-policy evaluation) — сырьё

**Аналогия.** Оценить нового повара по отзывам на блюда старого повара: можно, только если старый иногда готовил то же, что
приготовил бы новый (перекрытие), и мы знаем, как часто он это делал (вероятность выбора).

- Тема 27 (дословно ранее): IPS «uses the importance sampling technique to correct the distribution shift», DR «reduces the variance
  of IPS»; у нас «нет логов, нет логирующей политики, нет propensity» → **сейчас OPE не определён**.
- Kallus N., Uehara M. «Efficiently Breaking the Curse of Horizon in Off-Policy Evaluation with Double Reinforcement Learning».
  arXiv:1909.05850 (Operations Research, 2022). Канал: arXiv API **200** (4 864 байта). Дословно:
  > «Off-policy evaluation (OPE) in reinforcement learning is notoriously difficult in long- and infinite-horizon settings due to
  > diminishing overlap between behavior and target policies.»
  > «in time-variant processes, OPE is only feasible in the near-on-policy setting, where behavior and target policies are
  > sufficiently similar. But, in time-invariant Markov decision processes … truly-off-policy evaluation is feasible»
- Обзор: Uehara, Shi, Kallus «A Review of Off-Policy Evaluation in Reinforcement Learning», arXiv:2212.06355 (arXiv API 200) —
  аннотация общего характера, цитат по условиям не даёт.
- Сниппет WebSearch по arXiv:2402.08201: DR-оценки «relies on a strong distributional overlap assumption»; предложены усечённые
  DR-оценки при слабом перекрытии.

**Когда OPE честен (материал):** (1) продукт **логирует** показанную альтернативу и вероятность её показа (propensity) — для
детерминированного ядра вероятность 0/1, и перекрытия нет вовсе → нужна **намеренная случайность** (показывать с малой
вероятностью соседнюю из 66 альтернатив или спрашивать выбор между двумя); (2) новая политика близка к старой
(«near-on-policy» — Kallus & Uehara): оценивать можно **правки ядра**, а не «совет против ничего»; (3) горизонт: на 24 месяцах
веса IPS перемножаются по месяцам и взрываются — поэтому помесячное OPE на длинном горизонте без марковской структуры
нечестно. Пересекается с Г30.1: ВТБ выбрал симулятор вместо IPS/DR ровно из-за этого.

---

## Пункт 6. Дизайн наблюдения после запуска (сырьё)

**Аналогия.** Дневник наблюдений за садом: если не записывать с первого дня, когда полил и сколько вырос, через год
останется только ощущение «вроде растёт».

### 6.1 Источники
- Duflo E., Glennerster R., Kremer M. «Using Randomization in Development Economics Research: A Toolkit». NBER Technical WP 333
  (2006), DOI 10.3386/t0333; CEPR DP 6059 (2007). Канал: **Exa** (текст doi.org / NBER). Дословно:
  > «The minimum detectable effect size for a given power (κ), significance level (α), sample size (N), and portion of subjects
  > allocated to treatment group (P) is therefore given by MDE = (t(1−κ) + tα)·sqrt(1/(P(1−P)))·sqrt(σ²/N)» (формула 7)
  > «Partial compliance thus strongly affects the power of a design, since the MDE increases linearly with the compliance rate, while it
  > increases proportionally to the square root of the number of observations. Thus, if there is only an 80% difference in take up
  > between the treatment and control group, the sample size would have to be 56% larger to achieve the same minimum detectable effect.»
  > «when administrative data on the outcome is available for both the treatment and the comparison group, the optimal sample size
  > will have a larger comparison group.»
- AEA RCT Registry (сниппеты WebSearch, docs.socialscienceregistry.org, aeaweb.org): реестр «only for Randomized Controlled Trials (RCTs)
  in the fields of economics, political science, and other social sciences»; «Registration is free and requires a minimal amount of
  information»; pre-analysis plan — по желанию, прикрепляется позже; регистрация — **до начала вмешательства** (J-PAL, «Pre-analysis plans»).
- CFPB «Measuring financial well-being» (дек. 2015), files.consumerfinance.gov/f/201512_cfpb_financial-well-being-user-guide-scale.pdf —
  сниппет: короткая версия шкалы — вопросы **3, 5, 6, 8, 10** из 10. Формулировки вопросов в этом прогоне не добыты (PDF не открывался).

### 6.2 Размер выборки — расчёт стенда (`scratchpad/g44/power.py`, дословный вывод)
Исход — доля «в беде» (бинарный), две равные группы, α = 0,05 двусторонний, мощность 80 %, поправка на выполнение 1/c²:
```
base 10% effect -2 pp: n per arm (compliance 100/80/50 %):     3210     5016    12841
base 10% effect -5 pp: n per arm (compliance 100/80/50 %):      432      675     1727
base 20% effect -2 pp: n per arm (compliance 100/80/50 %):     6036     9431    24143
base 20% effect -5 pp: n per arm (compliance 100/80/50 %):      903     1410     3610
base 30% effect -2 pp: n per arm (compliance 100/80/50 %):     8076    12620    32306
base 30% effect -5 pp: n per arm (compliance 100/80/50 %):     1248     1950     4992
```
**Смысл:** чтобы увидеть снижение доли людей в беде с 20 % до 15 % при том, что советы выполняет половина, нужно ~3,6 тыс. человек
**в каждой группе**; эффект в 2 п.п. — десятки тысяч. До такого числа пользователей продукт дорастёт не сразу.

### 6.3 Что логировать с первого дня (материал для синтеза)
1. **Вход совета** (снимок: доход, расходы, долги со ставками/платежами/остатками, подушка, цели) — хэшированно, без ПДн наружу (152-ФЗ).
2. **Показанный совет, версия ядра и вся ранжированная выдача** (66 альтернатив и их баллы) + **вероятность показа** (для будущего OPE;
   при детерминированном ядре — 1, поэтому см. п. 4 про намеренную случайность).
3. **Что человек сделал** (факт перевода/погашения против совета) — доля выполнения; без этого нельзя отделить «совет плохой» от «не выполнен».
4. **Помесячные исходы**: остатки долгов, просрочки (флаг и дни), новые займы (особенно МФО и кредитки), подушка в месяцах расходов,
   ПДН, события шока (потеря дохода — флаг).
5. **Ранние сигналы-кандидаты в суррогаты** (фиксированный набор, чтобы потом строить surrogate index): подушка через 3 мес., ПДН, новые
   займы за 3 мес., 5 вопросов шкалы CFPB (или аналог) на входе и через 3/6/12 мес.
6. **Отток** (ушёл из продукта — это не «всё хорошо»; ушедшие теряются для исхода — главный источник смещения).
7. **Предрегистрация до запуска**: главная метрика (доля в беде через 12 мес.), суррогаты, порог, размер выборки, правило остановки.
8. **Отложенная контрольная группа** (часть новых пользователей видит только учёт без совета 3–6 мес.) — единственный способ получить
   первое условие Athey et al. (unconfoundedness); этическая оговорка — кризисные предупреждения показываются всем.

---

## Прототип (пункты 1 и 5): когорта из 400 синтетических домохозяйств, 24 месяца

🔴 **Оговорка прежде чисел: это проверка ТОЙ ЖЕ моделью.** Портреты — генератор проекта (`PortraitGenerator(seed=20260702,
version=2)`, только `plain` с доходом и расходами > 0), путь дохода — тот же приём, что в Г39, бухгалтерия — обобщение
`g39/p0b_sim.py`, человек выполняет совет на 100 % (кроме варианта `canon60`). Стенд отвечает на вопрос «что арифметически
следует из совета при наших допущениях», а **не** «помогает ли совет в жизни». Что стенд НЕ проверяет: реальные частоты потери
работы в РФ, реальное выполнение советов, реакцию расходов на шок, новые займы по собственной инициативе человека.

**Устройство.** Скрипт `scratchpad/g44/cohort.py` (прогон 117 с при load average ~3,7; ошибок 0; максимальное расхождение
тождества сохранения денег «итог = начало + Σ(доход − расход) − проценты − потреблённое» — **0,70 ₽** на 400 × 4 × 6 прогонах).
Политики: `canon` — `run_planning(...)["best"]` каждый месяц, кризис — как в Г39; `canon60` — совет выполняется с вероятностью
0,6 в месяц, иначе свободный остаток месяца проедается; `avalanche` / `snowball` — весь остаток в самый дорогой / самый маленький
долг; `nothing` — минимальные платежи, остаток копится деньгами; `rfavg` — минимальные платежи, 10 % остатка откладывается,
остальное тратится (**10 % — условный параметр, не проверенная статистика РФ**). Сценарии: `base`; `jobloss` — доход 0 в
месяцах 3–5; `infl` — расходы +0,8 %/мес., доход +0,3 %/мес.; `combo` — оба. «Беда» (по ЕЦБ, п. 1.1) — месяц, когда дыру не
закрыла подушка и пришлось занять под 35 %.

Вывод `report.py` (дословно):
```
== subset all: n=400
   errors 0, max |conservation gap| 0.70 rub
   base     canon    : net gain % of annual income median    69.3 p10     8.0 | any distress   6.0% | emergency debt > 1 month expenses at m24   0.8% | median distress months 0
   base     canon60  : net gain % of annual income median    45.5 p10     4.5 | any distress   6.2% | emergency debt > 1 month expenses at m24   2.0% | median distress months 0
   base     avalanche: net gain % of annual income median    70.0 p10     7.7 | any distress   7.8% | emergency debt > 1 month expenses at m24   1.2% | median distress months 0
   base     snowball : net gain % of annual income median    69.2 p10     7.7 | any distress   7.8% | emergency debt > 1 month expenses at m24   1.2% | median distress months 0
   base     nothing  : net gain % of annual income median    64.6 p10     7.7 | any distress   5.2% | emergency debt > 1 month expenses at m24   0.8% | median distress months 0
   base     rfavg    : net gain % of annual income median    13.1 p10    -0.4 | any distress   8.0% | emergency debt > 1 month expenses at m24   3.5% | median distress months 0
   jobloss  canon    : net gain % of annual income median    38.7 p10   -23.2 | any distress  76.8% | emergency debt > 1 month expenses at m24  24.8% | median distress months 2
   jobloss  canon60  : net gain % of annual income median    21.2 p10   -28.6 | any distress  78.8% | emergency debt > 1 month expenses at m24  33.2% | median distress months 2
   jobloss  avalanche: net gain % of annual income median    39.2 p10   -23.2 | any distress  74.5% | emergency debt > 1 month expenses at m24  22.2% | median distress months 2
   jobloss  snowball : net gain % of annual income median    39.2 p10   -23.2 | any distress  74.5% | emergency debt > 1 month expenses at m24  22.5% | median distress months 2
   jobloss  nothing  : net gain % of annual income median    37.3 p10   -23.2 | any distress  69.5% | emergency debt > 1 month expenses at m24  48.5% | median distress months 2
   jobloss  rfavg    : net gain % of annual income median    -2.1 p10   -30.1 | any distress  80.2% | emergency debt > 1 month expenses at m24  65.2% | median distress months 3
   infl     canon    : net gain % of annual income median    64.9 p10    -3.7 | any distress   9.0% | emergency debt > 1 month expenses at m24   5.5% | median distress months 0
   infl     canon60  : net gain % of annual income median    42.7 p10    -5.7 | any distress  11.0% | emergency debt > 1 month expenses at m24   6.5% | median distress months 0
   infl     avalanche: net gain % of annual income median    65.1 p10    -4.0 | any distress  12.2% | emergency debt > 1 month expenses at m24   6.0% | median distress months 0
   infl     snowball : net gain % of annual income median    65.0 p10    -4.0 | any distress  12.2% | emergency debt > 1 month expenses at m24   6.0% | median distress months 0
   infl     nothing  : net gain % of annual income median    60.7 p10    -4.0 | any distress   8.2% | emergency debt > 1 month expenses at m24   5.5% | median distress months 0
   infl     rfavg    : net gain % of annual income median    11.6 p10    -9.0 | any distress  15.0% | emergency debt > 1 month expenses at m24   8.0% | median distress months 0
   combo    canon    : net gain % of annual income median    33.4 p10   -36.2 | any distress  77.8% | emergency debt > 1 month expenses at m24  30.8% | median distress months 2
   combo    canon60  : net gain % of annual income median    18.1 p10   -39.5 | any distress  80.2% | emergency debt > 1 month expenses at m24  39.5% | median distress months 2
   combo    avalanche: net gain % of annual income median    35.5 p10   -35.8 | any distress  76.8% | emergency debt > 1 month expenses at m24  27.8% | median distress months 3
   combo    snowball : net gain % of annual income median    35.4 p10   -35.8 | any distress  76.8% | emergency debt > 1 month expenses at m24  27.8% | median distress months 3
   combo    nothing  : net gain % of annual income median    32.1 p10   -36.2 | any distress  71.8% | emergency debt > 1 month expenses at m24  52.5% | median distress months 2
   combo    rfavg    : net gain % of annual income median    -3.9 p10   -42.0 | any distress  83.2% | emergency debt > 1 month expenses at m24  69.5% | median distress months 3
   -- pairwise canon vs baseline (share of portraits): canon worse net by >0.5% income / better; canon more distress months / fewer
   base     canon vs avalanche: worse  31.5% better   3.8% | more distress   0.0% fewer   4.8%
   base     canon vs snowball : worse  27.3% better   7.0% | more distress   0.0% fewer   4.8%
   base     canon vs nothing  : worse   0.0% better  43.8% | more distress   1.0% fewer   0.0%
   base     canon vs rfavg    : worse   0.0% better  95.5% | more distress   0.0% fewer   5.8%
   base     canon vs canon60  : worse   0.0% better  93.8% | more distress   0.0% fewer   3.5%
   jobloss  canon vs avalanche: worse  48.0% better   1.0% | more distress   3.5% fewer  25.8%
   jobloss  canon vs snowball : worse  44.0% better   3.5% | more distress   4.8% fewer  25.5%
   jobloss  canon vs nothing  : worse   1.8% better  49.5% | more distress  19.0% fewer   0.2%
   jobloss  canon vs rfavg    : worse   0.2% better  90.2% | more distress   2.2% fewer  42.0%
   jobloss  canon vs canon60  : worse   0.0% better  87.2% | more distress   0.2% fewer  22.8%
   infl     canon vs avalanche: worse  33.2% better   3.8% | more distress   0.0% fewer   6.8%
   infl     canon vs snowball : worse  28.2% better   7.0% | more distress   0.0% fewer   6.8%
   infl     canon vs nothing  : worse   0.0% better  42.8% | more distress   0.8% fewer   0.0%
   infl     canon vs rfavg    : worse   0.0% better  93.8% | more distress   0.0% fewer  11.0%
   infl     canon vs canon60  : worse   0.0% better  90.5% | more distress   0.0% fewer   6.0%
   combo    canon vs avalanche: worse  48.5% better   1.8% | more distress   4.8% fewer  26.8%
   combo    canon vs snowball : worse  45.0% better   4.2% | more distress   5.5% fewer  26.2%
   combo    canon vs nothing  : worse   2.0% better  46.0% | more distress  18.5% fewer   0.8%
   combo    canon vs rfavg    : worse   0.8% better  89.2% | more distress   2.5% fewer  41.8%
   combo    canon vs canon60  : worse   0.2% better  85.5% | more distress   0.2% fewer  22.8%
== subset with debt: n=227
   errors 0, max |conservation gap| 0.70 rub
   base     canon    : net gain % of annual income median    80.7 p10    25.6 | any distress   7.0% | emergency debt > 1 month expenses at m24   0.4% | median distress months 0
   base     canon60  : net gain % of annual income median    58.8 p10    21.4 | any distress   7.0% | emergency debt > 1 month expenses at m24   2.2% | median distress months 0
   base     avalanche: net gain % of annual income median    82.2 p10    25.6 | any distress  10.1% | emergency debt > 1 month expenses at m24   1.3% | median distress months 0
   base     snowball : net gain % of annual income median    81.8 p10    25.6 | any distress  10.1% | emergency debt > 1 month expenses at m24   1.3% | median distress months 0
   base     nothing  : net gain % of annual income median    74.1 p10    25.4 | any distress   5.7% | emergency debt > 1 month expenses at m24   0.4% | median distress months 0
   base     rfavg    : net gain % of annual income median    31.4 p10    11.3 | any distress   8.8% | emergency debt > 1 month expenses at m24   4.0% | median distress months 0
   jobloss  canon    : net gain % of annual income median    46.8 p10   -11.5 | any distress  88.5% | emergency debt > 1 month expenses at m24  33.0% | median distress months 3
   jobloss  canon60  : net gain % of annual income median    31.8 p10   -12.1 | any distress  89.4% | emergency debt > 1 month expenses at m24  43.2% | median distress months 3
   jobloss  avalanche: net gain % of annual income median    48.2 p10   -11.9 | any distress  88.5% | emergency debt > 1 month expenses at m24  30.8% | median distress months 3
   jobloss  snowball : net gain % of annual income median    47.7 p10   -11.9 | any distress  88.5% | emergency debt > 1 month expenses at m24  31.3% | median distress months 3
   jobloss  nothing  : net gain % of annual income median    44.8 p10   -11.9 | any distress  79.7% | emergency debt > 1 month expenses at m24  64.8% | median distress months 2
   jobloss  rfavg    : net gain % of annual income median    12.2 p10   -14.3 | any distress  88.1% | emergency debt > 1 month expenses at m24  76.2% | median distress months 3
   infl     canon    : net gain % of annual income median    78.2 p10    16.3 | any distress  10.1% | emergency debt > 1 month expenses at m24   5.3% | median distress months 0
   infl     canon60  : net gain % of annual income median    56.3 p10    13.9 | any distress  12.3% | emergency debt > 1 month expenses at m24   7.0% | median distress months 0
   infl     avalanche: net gain % of annual income median    79.8 p10    17.0 | any distress  15.9% | emergency debt > 1 month expenses at m24   6.2% | median distress months 0
   infl     snowball : net gain % of annual income median    79.3 p10    17.0 | any distress  15.9% | emergency debt > 1 month expenses at m24   6.2% | median distress months 0
   infl     nothing  : net gain % of annual income median    72.4 p10    16.3 | any distress   8.8% | emergency debt > 1 month expenses at m24   5.3% | median distress months 0
   infl     rfavg    : net gain % of annual income median    30.6 p10     7.5 | any distress  15.9% | emergency debt > 1 month expenses at m24   8.8% | median distress months 0
   combo    canon    : net gain % of annual income median    45.2 p10   -21.6 | any distress  88.5% | emergency debt > 1 month expenses at m24  37.9% | median distress months 3
   combo    canon60  : net gain % of annual income median    29.6 p10   -22.7 | any distress  89.4% | emergency debt > 1 month expenses at m24  47.1% | median distress months 3
   combo    avalanche: net gain % of annual income median    45.6 p10   -21.6 | any distress  90.7% | emergency debt > 1 month expenses at m24  35.2% | median distress months 3
   combo    snowball : net gain % of annual income median    45.6 p10   -21.6 | any distress  90.7% | emergency debt > 1 month expenses at m24  35.2% | median distress months 3
   combo    nothing  : net gain % of annual income median    42.3 p10   -21.5 | any distress  81.9% | emergency debt > 1 month expenses at m24  67.4% | median distress months 2
   combo    rfavg    : net gain % of annual income median    10.3 p10   -22.8 | any distress  89.9% | emergency debt > 1 month expenses at m24  79.3% | median distress months 3
   -- pairwise canon vs baseline (share of portraits): canon worse net by >0.5% income / better; canon more distress months / fewer
   base     canon vs avalanche: worse  55.1% better   6.6% | more distress   0.0% fewer   7.5%
   base     canon vs snowball : worse  47.6% better  12.3% | more distress   0.0% fewer   7.5%
   base     canon vs nothing  : worse   0.0% better  77.1% | more distress   1.8% fewer   0.0%
   base     canon vs rfavg    : worse   0.0% better  96.0% | more distress   0.0% fewer   6.2%
   base     canon vs canon60  : worse   0.0% better  93.0% | more distress   0.0% fewer   3.5%
   jobloss  canon vs avalanche: worse  64.8% better   1.8% | more distress   2.2% fewer  38.8%
   jobloss  canon vs snowball : worse  57.7% better   6.2% | more distress   4.4% fewer  38.3%
   jobloss  canon vs nothing  : worse   2.6% better  62.1% | more distress  29.5% fewer   0.4%
   jobloss  canon vs rfavg    : worse   0.4% better  88.1% | more distress   4.0% fewer  35.7%
   jobloss  canon vs canon60  : worse   0.0% better  83.7% | more distress   0.4% fewer  19.8%
   infl     canon vs avalanche: worse  58.1% better   6.6% | more distress   0.0% fewer  11.0%
   infl     canon vs snowball : worse  49.3% better  12.3% | more distress   0.0% fewer  11.0%
   infl     canon vs nothing  : worse   0.0% better  75.3% | more distress   1.3% fewer   0.0%
   infl     canon vs rfavg    : worse   0.0% better  93.8% | more distress   0.0% fewer  11.0%
   infl     canon vs canon60  : worse   0.0% better  90.3% | more distress   0.0% fewer   6.2%
   combo    canon vs avalanche: worse  65.2% better   3.1% | more distress   2.2% fewer  40.1%
   combo    canon vs snowball : worse  59.0% better   7.5% | more distress   3.5% fewer  39.2%
   combo    canon vs nothing  : worse   3.1% better  59.5% | more distress  26.4% fewer   1.3%
   combo    canon vs rfavg    : worse   1.3% better  87.2% | more distress   4.0% fewer  36.1%
   combo    canon vs canon60  : worse   0.4% better  81.9% | more distress   0.4% fewer  21.1%
== subset toxic debt rate>=30%: n=74
   errors 0, max |conservation gap| 0.63 rub
   base     canon    : net gain % of annual income median    82.1 p10    21.1 | any distress   4.1% | emergency debt > 1 month expenses at m24   0.0% | median distress months 0
   base     canon60  : net gain % of annual income median    56.9 p10    18.2 | any distress   4.1% | emergency debt > 1 month expenses at m24   0.0% | median distress months 0
   base     avalanche: net gain % of annual income median    82.9 p10    21.1 | any distress   8.1% | emergency debt > 1 month expenses at m24   0.0% | median distress months 0
   base     snowball : net gain % of annual income median    82.1 p10    21.1 | any distress   8.1% | emergency debt > 1 month expenses at m24   0.0% | median distress months 0
   base     nothing  : net gain % of annual income median    74.1 p10    20.0 | any distress   2.7% | emergency debt > 1 month expenses at m24   0.0% | median distress months 0
   base     rfavg    : net gain % of annual income median    28.6 p10     8.9 | any distress   5.4% | emergency debt > 1 month expenses at m24   1.4% | median distress months 0
   jobloss  canon    : net gain % of annual income median    50.4 p10   -13.7 | any distress  86.5% | emergency debt > 1 month expenses at m24  27.0% | median distress months 3
   jobloss  canon60  : net gain % of annual income median    28.4 p10   -17.1 | any distress  87.8% | emergency debt > 1 month expenses at m24  35.1% | median distress months 3
   jobloss  avalanche: net gain % of annual income median    52.7 p10   -13.7 | any distress  87.8% | emergency debt > 1 month expenses at m24  27.0% | median distress months 3
   jobloss  snowball : net gain % of annual income median    52.2 p10   -13.7 | any distress  87.8% | emergency debt > 1 month expenses at m24  27.0% | median distress months 3
   jobloss  nothing  : net gain % of annual income median    45.7 p10   -13.7 | any distress  78.4% | emergency debt > 1 month expenses at m24  63.5% | median distress months 2
   jobloss  rfavg    : net gain % of annual income median     9.2 p10   -23.8 | any distress  86.5% | emergency debt > 1 month expenses at m24  74.3% | median distress months 3
   infl     canon    : net gain % of annual income median    79.5 p10    13.9 | any distress   9.5% | emergency debt > 1 month expenses at m24   5.4% | median distress months 0
   infl     canon60  : net gain % of annual income median    53.8 p10     7.5 | any distress  13.5% | emergency debt > 1 month expenses at m24   8.1% | median distress months 0
   infl     avalanche: net gain % of annual income median    80.0 p10    13.9 | any distress  14.9% | emergency debt > 1 month expenses at m24   5.4% | median distress months 0
   infl     snowball : net gain % of annual income median    78.7 p10    13.9 | any distress  14.9% | emergency debt > 1 month expenses at m24   5.4% | median distress months 0
   infl     nothing  : net gain % of annual income median    72.2 p10    13.9 | any distress   8.1% | emergency debt > 1 month expenses at m24   5.4% | median distress months 0
   infl     rfavg    : net gain % of annual income median    27.3 p10     3.7 | any distress  17.6% | emergency debt > 1 month expenses at m24   8.1% | median distress months 0
   combo    canon    : net gain % of annual income median    45.8 p10   -23.2 | any distress  86.5% | emergency debt > 1 month expenses at m24  28.4% | median distress months 3
   combo    canon60  : net gain % of annual income median    27.3 p10   -30.8 | any distress  87.8% | emergency debt > 1 month expenses at m24  41.9% | median distress months 3
   combo    avalanche: net gain % of annual income median    48.1 p10   -23.2 | any distress  87.8% | emergency debt > 1 month expenses at m24  28.4% | median distress months 3
   combo    snowball : net gain % of annual income median    47.5 p10   -23.2 | any distress  87.8% | emergency debt > 1 month expenses at m24  28.4% | median distress months 3
   combo    nothing  : net gain % of annual income median    41.3 p10   -23.2 | any distress  79.7% | emergency debt > 1 month expenses at m24  66.2% | median distress months 2
   combo    rfavg    : net gain % of annual income median     7.5 p10   -31.7 | any distress  87.8% | emergency debt > 1 month expenses at m24  75.7% | median distress months 3
   -- pairwise canon vs baseline (share of portraits): canon worse net by >0.5% income / better; canon more distress months / fewer
   base     canon vs avalanche: worse  51.4% better   4.1% | more distress   0.0% fewer   6.8%
   base     canon vs snowball : worse  40.5% better  12.2% | more distress   0.0% fewer   6.8%
   base     canon vs nothing  : worse   0.0% better  87.8% | more distress   2.7% fewer   0.0%
   base     canon vs rfavg    : worse   0.0% better  94.6% | more distress   0.0% fewer   4.1%
   base     canon vs canon60  : worse   0.0% better  91.9% | more distress   0.0% fewer   0.0%
   jobloss  canon vs avalanche: worse  70.3% better   0.0% | more distress   1.4% fewer  27.0%
   jobloss  canon vs snowball : worse  58.1% better   8.1% | more distress   2.7% fewer  25.7%
   jobloss  canon vs nothing  : worse   1.4% better  70.3% | more distress  40.5% fewer   0.0%
   jobloss  canon vs rfavg    : worse   0.0% better  89.2% | more distress   5.4% fewer  25.7%
   jobloss  canon vs canon60  : worse   0.0% better  85.1% | more distress   0.0% fewer  14.9%
   infl     canon vs avalanche: worse  55.4% better   4.1% | more distress   0.0% fewer   8.1%
   infl     canon vs snowball : worse  43.2% better  12.2% | more distress   0.0% fewer   8.1%
   infl     canon vs nothing  : worse   0.0% better  85.1% | more distress   1.4% fewer   0.0%
   infl     canon vs rfavg    : worse   0.0% better  94.6% | more distress   0.0% fewer  12.2%
   infl     canon vs canon60  : worse   0.0% better  90.5% | more distress   0.0% fewer   6.8%
   combo    canon vs avalanche: worse  70.3% better   0.0% | more distress   1.4% fewer  31.1%
   combo    canon vs snowball : worse  60.8% better   8.1% | more distress   2.7% fewer  29.7%
   combo    canon vs nothing  : worse   1.4% better  70.3% | more distress  35.1% fewer   1.4%
   combo    canon vs rfavg    : worse   0.0% better  87.8% | more distress   4.1% fewer  28.4%
   combo    canon vs canon60  : worse   0.0% better  81.1% | more distress   0.0% fewer  18.9%
```

Вывод `gap.py` (дословно; разница «ядро минус базовая стратегия», чистая позиция — в % годового дохода, экстренный долг — в месяцах расходов):
```
with debt n=227 base     canon-avalanche: net gap p10   -3.9 median   -0.6 p90    0.0 | emergency debt at m24, months of expenses: p10  0.00 median  0.00 p90  0.00
with debt n=227 base     canon-nothing  : net gap p10    0.0 median    4.3 p90   14.3 | emergency debt at m24, months of expenses: p10  0.00 median  0.00 p90  0.00
with debt n=227 base     canon-canon60  : net gap p10    0.9 median   17.9 p90   39.2 | emergency debt at m24, months of expenses: p10  0.00 median  0.00 p90  0.00
with debt n=227 jobloss  canon-avalanche: net gap p10   -3.1 median   -1.1 p90    0.1 | emergency debt at m24, months of expenses: p10 -0.17 median  0.00 p90  0.35
with debt n=227 jobloss  canon-nothing  : net gap p10   -0.0 median    1.7 p90    8.4 | emergency debt at m24, months of expenses: p10 -2.68 median -0.09 p90  0.01
with debt n=227 jobloss  canon-canon60  : net gap p10    0.0 median   11.5 p90   30.1 | emergency debt at m24, months of expenses: p10 -1.52 median  0.00 p90  0.00
with debt n=227 combo    canon-avalanche: net gap p10   -3.5 median   -1.1 p90    0.1 | emergency debt at m24, months of expenses: p10 -0.24 median  0.00 p90  0.52
with debt n=227 combo    canon-nothing  : net gap p10   -0.0 median    1.4 p90    8.6 | emergency debt at m24, months of expenses: p10 -2.72 median -0.00 p90  0.06
with debt n=227 combo    canon-canon60  : net gap p10    0.0 median   10.2 p90   32.8 | emergency debt at m24, months of expenses: p10 -1.35 median  0.00 p90  0.00
```

**Что это значит простыми словами (материал для синтеза, не решение по ядру).**
1. **Ядро против avalanche — не выигрыш, а размен.** По деньгам ядро чаще немного проигрывает (у 55–65 % должников хуже больше
   чем на 0,5 % годового дохода; медиана разрыва −0,6…−1,1 % дохода, худшие 10 % — −3…−4 %). Зато при потере работы у ядра
   **меньше месяцев беды у 38–40 % должников** (больше — у 2–4 %). Ядро держит подушку и платит за это процентами.
   Это та же картина, что Г39 нашёл на 12 месяцах, теперь на 24 и с инфляцией.
2. **Ядро против «ничего не делать» выигрывает деньгами** (медиана +4,3 % дохода в base, до +14 % у верхних 10 %),
   но при потере работы **у 26–30 % должников месяцев беды больше, чем у «ничего»** — потому что «ничего» держит все свободные
   деньги наличными. При этом у «ничего» к концу вдвое чаще висит экстренный долг больше месячных расходов (65 % против 33 %) —
   «ничего» не гасит его сверх 5 % минимума. 🔴 **Какая стратегия «лучше», зависит от выбранной метрики беды** — это и есть
   главный урок: вопрос «помогает ли на дистанции» без заранее зафиксированной метрики не имеет ответа.
3. 🔴 **Самый большой рычаг — не математика ядра, а выполнение.** `canon` против `canon60`: медиана +18 % годового дохода в base,
   +10–12 % при шоках — на порядок больше, чем разница ядро/avalanche (≈1 %). Но это число целиком задано допущением стенда
   («невыполненный месяц = проеденный остаток»). То есть **ответ стенда определяется параметром, которого нет в модели** —
   ровно замкнутая петля, о которой предупреждал Г31.4: без реальных данных о выполнении симуляция не может сказать, помогает ли продукт.
4. **Худшие случаи (п. 5).** При потере работы на 3 месяца «беда» случается у 70–83 % всех портретов и у 80–91 % должников при ЛЮБОЙ стратегии: три месяца без
   дохода при типичной подушке генератора не закрывает ни одна политика распределения остатка. Совет меняет **глубину** беды
   (экстренный долг на 24-м месяце больше месячных расходов: ядро 33 %, avalanche 31 %, ничего 65 %, rfavg 76 % — у должников),
   а не её факт. Метрика «доля, которую совет довёл до беды» должна считаться **против базовой стратегии** (разница пар), а не абсолютно.
5. **Чего стенд не может сказать в принципе:** какая доля реальных людей в РФ потеряет доход, как часто они выполняют советы,
   берут ли МФО при нехватке. Все три — внешние параметры, их источник — RLMS (переходы год к году) и журнал продукта (п. 6).

---

## ИТОГ Г44

### 🔴 Прямой ответ: как ответить «помогает ли продукт на дистанции», не дожидаясь года

Ответить **без данных о реальных людях нельзя совсем** — никакой метод не превращает модель в доказательство её же пользы.
Можно другое: (а) **до запуска** — узнать, где совет арифметически опасен, и подготовить внешние якоря; (б) **после запуска** — получить
обоснованную оценку 1–3-летнего эффекта через 3–6 месяцев, а не через 2 года, если с первого дня логировать нужное и держать
контрольную группу. Методы по силе доказательства, от сильного к слабому:

1. **Отложенная контрольная группа + суррогатный индекс** (Athey, Chetty, Imbens, Kang; RES 2026).
   *Аналогия:* врач меряет давление через 3 месяца вместо инфарктов через 10 лет, но сначала на другой когорте проверил, что давление
   предсказывает инфаркты. *Суть:* часть новых пользователей 3–6 мес. видит только учёт; сравниваем ранние сигналы (подушка, ПДН, новые
   займы, шкала благополучия); связь «ранние сигналы → исход через 1–3 года» учим на панели (RLMS, годовой шаг) или позже на своих же
   старых пользователях. *Пример:* Ольга, зарплата 70 000 ₽, кредитка 120 000 ₽ под 35 %: через 3 месяца у неё в группе с советом
   подушка 1,2 мес. против 0,4 у похожих без совета — индекс переводит это в «ожидаемая доля беды через 2 года −X п.п.».
   *Цена:* тысячи пользователей на группу (при выполнении советов 50 % — ~3,6 тыс. на группу для эффекта −5 п.п. от 20 %),
   3–6 мес., этическое решение про контроль. *Слабость:* допущение surrogacy не проверяемо в одном исследовании (авторы:
   «the assumptions jointly do not have any testable implications»), а финансовые эффекты затухают — Fernandes et al. 2014:
   «negligible effects on behavior 20 months or more» → ранний эффект завышает длинный.
2. **Внешне заякоренная симуляция когорт** (ЕЦБ, Ampudia et al. 2014; Windrum et al. 2007).
   *Аналогия:* авиатренажёр, откалиброванный по чёрным ящикам настоящих аварий. *Суть:* входы и частоты шоков — из ОДПФ/ВНДН/RLMS, а не
   из генератора; поведение (выполнение, реакция на шок) — варьируемый неизвестный параметр; симулятор принимается, только если без
   совета воспроизводит наблюдаемые доли беды в РФ (автономия 0–1 мес. 65 % по ОДПФ; просрочки по КОУЖ/ВНДН; NPL ЦБ).
   *Пример:* Игорь, 90 000 ₽, ипотека + МФО: в 1 000 прогонах с частотой потери работы из RLMS считаем, у скольких «игорей» совет дал
   больше экстренного долга, чем avalanche. *Цена:* 2–4 недели работы, данные бесплатные. *Доказывает:* безопасность совета в
   правдоподобных мирах и где он хуже простых правил. *Не доказывает:* пользу в жизни (петля разорвана только наполовину).
3. **Внутренняя симуляция (текущий стенд Г39/Г44).** *Суть:* та же модель, свои допущения. *Цена:* уже сделано, часы.
   *Доказывает:* арифметические размены (ядро ≈ −1 % дохода к avalanche ради меньшего числа месяцев беды у ~40 % должников при
   потере работы) и что главный рычаг — выполнение, а не ядро. *Не доказывает:* ничего о реальной пользе.
4. **Off-policy оценка по логам (IPS/DR).** Сейчас **не определена** (нет логов и propensity). После запуска честна только для
   оценки **близких правок ядра** («near-on-policy», Kallus & Uehara) и только если ядро намеренно вносит случайность в показ;
   для «совет против ничего» на 24 месяцах — нечестна (перекрытие исчезает, веса взрываются).
5. **Бэктест на исторических панелях** — для НАШЕГО помесячного совета **невозможен** (см. п. 2.3): в RLMS нет ставок, платежей по
   долгам и суммы подушки, шаг год; контрфакт решения не наблюдается ни в какой панели. RLMS нужен как якорь (метод 2) и обучающая
   выборка суррогатов (метод 1), не как бэктест.

### Данные РФ, реально доступные
- **RLMS-HSE**: 1994–2025 (34 волны), ежегодно, домохозяйства ~4–5 тыс., идентификаторы для склейки волн; скачивание без заявки (DUA No),
  условие «only for analysis purposes», коммерческое разрешение не прописано → письменный запрос в НИУ ВШЭ/CPC. Переменные про деньги:
  брали ли кредит за 12 мес. и цель (ипотека/авто/потреб), есть ли кредитный долг и его сумма, долги частным лицам, «взяли в долг за
  30 дней» и сумма, расходы на выплату кредитов за 30 дней, «сколько проживёте на сбережения» (6 градаций), трата сбережений,
  долг за ЖКУ, подробные доходы/расходы; готовые сконструированные переменные 1994–2024. Нет: ставки, срока, графика, суммы сбережений.
- **ОДПФ ЦБ** (срезы 2013–2024, микроданные открыты, есть ставки) и **ВНДН Росстата** (срезы 2012–2025, CC BY 4.0, покредитный блок со
  ставкой и платежом) — входы и якоря, не панель.

### Какие суррогаты брать и насколько им верить
| Суррогат (через 3–12 мес.) | Связь с бедой через 1–3 года | Доверие |
|---|---|---|
| Подушка ≥ ~1 мес. расходов / ≥ $2 452 | −9,5 п.п. риска крайних лишений через 3 года (Sabat & Gallagher 2020), меньше лишений (Gjertson 2016) | среднее: коррелят, причинность авторы отрицают |
| Новые займы у МФО / частных лиц, просрочка | прямая часть исхода «беда» (ЕЦБ: маржа < 0 и ликвидности не хватает) | высокое как ранний исход, но это уже почти сама беда |
| ПДН, финансовая маржа | основа стресс-тестов ЕЦБ, калибруется по NPL | среднее |
| Шкала CFPB (5 вопросов) | согласуется с объективными коэффициентами (Khashadourian & Harrison 2024, η² = 0,197, n ≈ 410), но авторы отмечают шум | низко-среднее для продольного прогноза: продольной валидации «шкала → беда через годы» в добытом не найдено |
| Чистая позиция / уплаченные проценты | то, что оптимизирует ядро | низкое как суррогат пользы: это SAW-логика самого продукта (Прентис: суррогат должен ловить ВЕСЬ эффект) |
Правило: брать **набор** (индекс), а не одну метрику; фиксировать его до запуска; делать поправку на затухание.

### Что логировать с первого дня
Снимок входа совета · версия ядра и вся ранжированная выдача с вероятностью показа · фактическое действие (выполнение) · помесячно:
остатки долгов, просрочки, новые займы (МФО/кредитки), подушка в месяцах, ПДН, флаг шока дохода · шкала благополучия на входе и
через 3/6/12 мес. · отток · отложенная контрольная группа · предрегистрация (главная метрика, суррогаты, выборка, правило остановки).
Подробно — п. 6.3.

### Таблица методов
| Метод | Что доказывает | Чего не доказывает | Данные | Цена | Корзина |
|---|---|---|---|---|---|
| Внутренняя симуляция (стенд Г39/Г44) | арифметические размены, опасные зоны совета | пользу в жизни (замкнутая петля) | генератор проекта | часы, сделано | **сейчас** (готово) |
| Заякоренная симуляция (ЕЦБ-подобная) | безопасность совета в правдоподобных для РФ мирах; где хуже простых правил | реальное поведение и пользу | ОДПФ, ВНДН, RLMS, NPL ЦБ | 2–4 недели, бесплатно | **до запуска** |
| Суррогатный индекс на RLMS (обучение связи) | какие годовые сигналы предсказывают беду через 1–3 года в РФ | эффект нашего совета (нужен п. ниже) | RLMS 1994–2025 | 1–2 недели + письмо в ВШЭ | **до запуска** |
| Логирование + предрегистрация | делает возможными все методы после запуска | ничего само по себе | продукт | 16–24 ч (оценка Г39) | **до запуска** |
| Отложенный контроль + суррогатный индекс | причинный эффект на 1–3 года за 3–6 мес. при допущениях | эффект при нарушенной surrogacy; затухание | продукт + RLMS | тысячи пользователей на группу, 3–6 мес. | **после запуска** |
| OPE (IPS/DR) | качество близких правок ядра | «совет против ничего» на 24 мес. | логи с propensity, случайность показа | недели после накопления логов | **после запуска** |
| Бэктест совета на панелях | — | всё: вход ядра не строится, контрфакт не наблюдается | — | — | **не нужно** |
| RCT с ожиданием 1–3 лет | эффект без допущений | — | продукт | годы | **после запуска** (как проверка индекса, не как единственный путь) |

### Что осталось неизвестным
- Длительность наблюдения и точные размеры эффектов в RCT Urban Institute (страница открылась только аннотацией).
- Формулировки 5 вопросов шкалы CFPB (PDF не открывался); продольная валидность шкалы на горизонте лет — не найдена.
- SHARE — не добывался; PSID и Understanding Society — только сниппеты условий доступа.
- Панельность ВНДН; российские данные NPL/просрочек 90+ для якоря — не добывались в этом батче.
- Анкета взрослого RLMS 23-й волны — 404; вопросы про кредиты в индивидуальной анкете не проверены.
- Реальная доля выполнения советов в РФ — главный неизвестный параметр стенда.

### Процесс (прозрачность)
Классификация — breadth-first. Подагентов — **0**. WebSearch — 12 вызовов, Exa — 5, WebFetch — 5 (из них 2 × 403, 1 PDF → диск →
`pdftotext`), `r.jina.ai` — 3, arXiv API — 1, `curl` с UA — 3 PDF RLMS (1 × 404). Стенд: `scratchpad/g44/{cohort.py, report.py,
gap.py, power.py}`, выводы `report.out`, `gap.out`, `cohort400.jsonl`. Канон, код продукта, tests, служебные доки — не трогались.
