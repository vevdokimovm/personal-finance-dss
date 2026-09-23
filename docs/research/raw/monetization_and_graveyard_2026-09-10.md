# Тема 24. Бизнес-модели и монетизация в PFM + кладбище закрывшихся продуктов

**Дата:** 2026-09-10
**Статус:** ЗАВЕРШЕНО. Четыре участка закрыты, приложения с дословными текстами норм добавлены.
**Исполнение:** лид (участки 1–3, синтез, все прямые ответы) + 1 субагент (участок 4,
добыча текстов норм РФ). Синтез субагенту не делегировался.
**Проект:** FINPILOT — СППР по личным финансам, рынок РФ, запуск осень 2026, модель — подписка

## Легенда классов доказательств

- 🟩 **РАСКРЫТОЕ** — цифра из отчётности эмитента (10-K, 20-F, S-1, 8-K), официального пресс-релиза
  компании, прямого заявления основателя/CEO с датой.
- 🟨 **ОЦЕНОЧНОЕ** — блог аналитика, отраслевой обзор, вторичная пресса со ссылкой на «источники».
- 🟥 **НЕ ДОБЫТО** — с указанием канала и кода ответа.
- ⬜ **ПАМЯТЬ МОДЕЛИ, НЕ ПРОВЕРЕНО** — помечается явно, в финмодель не идёт.

---

## Участок 1. Модели монетизации

### 1.1. Чистая подписка (YNAB, Copilot, Monarch, Simplifi)

#### 1.1.1. 🔴 Rocket Money — единственный PFM-подписочник с ПОЛНОЙ раскрытой отчётностью

Это самая ценная находка темы. Rocket Money (бывш. Truebill, куплен Rocket Companies в 2021)
входит в публичную Rocket Companies, Inc. (NYSE: RKT), и та **раскрывает и выручку, и число
платящих подписчиков, и отдельно подписочную выручку** — то есть по нему можно посчитать
ARPU и динамику приростов, чего нет ни по одному другому PFM.

**Источники (оба сняты полным текстом через `curl` с заголовком User-Agent, требуемым SEC):** 🟩
- Rocket Companies, Inc., **Form 10-K за FY2024** (год до 31.12.2024):
  https://www.sec.gov/Archives/edgar/data/1805284/000180528425000010/rkt-20241231.htm
- Rocket Companies, Inc., **Form 10-K за FY2025** (год до 31.12.2025):
  https://www.sec.gov/Archives/edgar/data/1805284/000162828026013283/rkt-20251231.htm

**Что за продукт — дословно, Item 1 Business:** 🟩
> "**Rocket Money.** Our personal finance app that helps clients manage their financial lives.
> Rocket Money offers clients a suite of financial wellness services including **subscription
> cancellation, budget management and credit score improvement** that save them time and money."

**Как зарабатывает — дословно, Item 1 (FY2024):** 🟩
> "Rocket Money earns revenue from **premium members, or paying subscribers**, as well as other
> service-based fees from members."

**Учётная политика подписки — дословно, Notes to Consolidated Financial Statements, ASC 606:** 🟩
> "**Rocket Money subscription revenue** — The Company recognizes subscription revenue ratably over
> the contract term beginning on the commencement date of each contract. We have determined that
> subscriptions represent a **stand-ready obligation** to perform over the subscription term. These
> performance obligations are satisfied over time as the customer simultaneously receives and
> consumes the benefits. **Contracts are one month to one year in length.**"

**🟩 РАСКРЫТЫЕ ЧИСЛА (сведены из обоих 10-K):**

| Показатель | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|
| Rocket Money revenue, $ млн (Other income table) | 141.6 | 198.7 / 199 | 297.2 / 297 | **390** |
| В т.ч. **subscription revenue**, $ млн (ASC 606 note) | 118.344 | 178.769 | 266.938 | **351** |
| Rocket Money **gross** revenue, $ тыс. (Select Other, FY2024 10-K) | 145 381 | 209 826 | 321 180 | н/д в FY2025 10-K |
| **Paying subscribers, at period end**, тыс. | 2 263.5 | 3 017.5 | 4 116.5 | **4 583** |

Дословная строка FY2025 10-K, таблица Select Other Rocket Companies:
> "Rocket Money paying subscribers, at period end **4,583 4,117 3,017**" (тыс., 2025 / 2024 / 2023)

Дословно о драйвере роста, MD&A FY2025:
> "**Rocket Money increased $93 million, primarily due to growth in paying subscribers.**"
Дословно, MD&A FY2024:
> "...a **$98.5 million, or 50%, increase in Rocket Money revenue** associated with growth
> in paying subscribers..."

**🔵 Наши расчёты из раскрытых чисел (арифметика, не источник):**
- **Доля чистой подписки в выручке продукта: ~90 %.** 2025: 351/390 = **90.0 %**;
  2024: 266.9/297.2 = **89.8 %**. Остальные ~10 % — «other service-based fees».
  То есть **подписочный PFM промышленного масштаба реально существует и не нуждается
  в лидогенерации как основном источнике** — это прямой контраргумент к тезису
  «PFM живёт только на комиссиях».
- **ARPU (subscription revenue / средние подписчики за год):**
  2024 = 266.938 / ((3017.5+4116.5)/2 = 3567) ≈ **$74.8 в год**;
  2025 = 351 / ((4116.5+4583)/2 = 4350) ≈ **$80.7 в год**.
  Порядок — **$6–7 в месяц на платящего**, при том что базовый тариф Rocket Money Premium —
  «pay what you want» в диапазоне (цены см. тему 23).
- **🔴 Резкое замедление чистых приростов подписчиков:**
  2023 → +754 тыс. · 2024 → **+1 099 тыс.** · 2025 → **+466.5 тыс.**
  Прирост 2025 упал в **2.36 раза** к 2024. Всплеск 2024 совпадает с отключением Mint
  (23.03.2024) — то есть значительная часть роста лидера подписочного PFM была **разовым
  подбором осиротевшей базы конкурента**, а не органикой. Для FINPILOT это предупреждение:
  органический рост подписочного PFM на зрелом рынке измеряется сотнями тысяч в год
  при базе в миллионы, а не кратностями.
- 🟥 **Rocket Companies НЕ раскрывает по Rocket Money:** CAC, LTV, отток (churn),
  конверсию free→paid. Проверено grep-ом по полным текстам обоих 10-K.
  Маркетинговые расходы даются только на всю группу (2025: $1 088 млн; 2024: $824 млн)
  и на Rocket Money не разбиваются.
- Оговорка: Rocket Money **сидит внутри ипотечной группы**, то есть часть его CAC оплачена
  общегрупповым маркетингом и кросс-каналом Rocket Mortgage. Автономный подписочный PFM
  такой субсидии не имеет. Это существенно для переноса цифр на FINPILOT.
- 🟩 Гудвилл от покупки Rocket Money — «approximately $1.1 billion of goodwill» на группу,
  «primarily attributable to the acquisition of Rocket Money in 2021»; тест на обесценение
  на 01.10.2024 индикаторов обесценения не выявил (FY2024 10-K, Note 9).

#### 1.1.2. Monarch Money — подписка, поднявшаяся на смерти Mint

- 🟩 **$75 млн Series B, май 2025**, со-лидеры **FPV Ventures и Forerunner Ventures**;
  участвовали Accel, SignalFire, Clocktower Ventures, Menlo Ventures. Оценка post-money —
  **$850 млн** (🟨 «reported», не подтверждена компанией).
  Источник: CNBC, 23.05.2025,
  https://www.cnbc.com/2025/05/23/personal-finance-app-monarch-raises-75-million.html
- 🟨 **ARR ≈ $12.6 млн (2025)** — источник getlatka.com, это **агрегатор оценок, не раскрытие**.
  ⚠️ Цифра плохо стыкуется с оценкой $850 млн (мультипликатор ~67×) и с заявленным ростом;
  **в финмодель не брать**. Помечено как ОЦЕНОЧНОЕ низкого качества.
- 🟨 «20-кратный рост платящих подписчиков с момента закрытия Mint в начале 2024»;
  «рост платных подписчиков ~9 % в неделю» — формулировки из вторичной прессы,
  без базы отсчёта, то есть непроверяемы.
- 🔴 **Позиционное заявление, важное для FINPILOT** (пересказ CNBC): в отличие от Mint,
  который был бесплатным, Monarch опирается на платящих подписчиков, **чтобы не зависеть
  от рекламы эмитентов кредитных карт и не продавать данные пользователей**.
  Это ровно наша рамка «нет продавца в контуре», уже отработанная конкурентом
  как маркетинговый аргумент.

#### 1.1.3. YNAB, Copilot, Simplifi

🟥 **Не раскрывают ничего.** YNAB (You Need A Budget) — частная компания, отчётности нет;
Copilot Money — частная; Simplifi входит в Quicken (частная, владелец — Aquiline Capital
Partners), отдельных метрик по Simplifi нет. Ни конверсии free→paid, ни оттока, ни LTV
по этим трём продуктам в открытых источниках первого класса не существует.
Всё, что публикуется по ним — оценки агрегаторов (getlatka, Sacra, CB Insights),
класс 🟨, методика не раскрыта.

### 1.2. Freemium — где проходит граница платного

**🔴 ГИПОТЕЗА ЗАДАНИЯ ОПРОВЕРГНУТА.** Предполагалось, что в платный контур чаще всего
попадают **синхронизация счетов и «продвинутая аналитика»**. У лидера рынка это не так —
ровно наоборот.

#### Rocket Money — прямая раскладка free / premium с сайта продукта

Источник: официальный сайт https://www.rocketmoney.com/ , снят **10.09.2026** через текстовый
прокси `r.jina.ai` (прямой `WebFetch` на `/premium` дал **302 → app.rocketmoney.com/premium → 404**).
🟩 (первоисточник — сам вендор), дословно:

> **without Premium** (то есть БЕСПЛАТНО):
> — **Account Linking.** "Link your checking, savings, credit cards, and investments accounts
>   to see everything in one place."
> — **Balance Alerts.** "Get alerted when your checking account falls below a safe balance or
>   when your credit spend is too high."
> — **Subscription Management.** "Our algorithm works its magic to find all of your recurring
>   subscriptions and bills."
> — **Spend Tracking.** "With all of your accounts in one place, see and understand your
>   spending trends."
>
> **with Premium:** "You get everything on the free plan, **plus these additional services**:"
> — **Subscription Cancellation Assistant.** "**Let us cancel your subscriptions for you.**"
> — **Automated Savings Plan.** "Reach your financial goals with ease."
> — "...and more! Turbocharge your finances with **net worth tracking, shared accounts,
>   unlimited budgets**, and more."

И рамочная фраза, которая объясняет всю модель, дословно:
> "**Premium is more than just software features!** You'll also get **real access to humans**
> who can help you cancel subscriptions, lower your bills or help with questions about your
> personal finances."

**🔴 Вывод участка 1.2 — граница платного проходит не там, где предполагалось.**
Бесплатны: агрегация счетов (Plaid-синхронизация), базовая аналитика трат, оповещения,
обнаружение подписок. Платно: (а) **действие, выполненное ЗА пользователя** (отмена подписки,
переговоры о снижении счетов — «concierge», то есть живой человек в контуре);
(б) **автоматизация денежных потоков** (Automated Savings Plan);
(в) **снятие количественных ограничений** (unlimited budgets, shared accounts);
(г) **производные аналитические сущности** (net worth tracking).

Механизм понятен: **синхронизация счетов больше не дефицит** — Plaid/агрегаторы
коммодитизировали её, и запирать за плату то, что конкурент отдаёт даром, нельзя.
Дефицитом остаётся **исполненное действие и результат в деньгах**.

🔴 **Что это значит для FINPILOT.** Наш продукт — СППР, то есть по построению производит
**рекомендацию, а не действие**. По логике рынка рекомендация — это тот класс ценности,
который у Rocket Money раздаётся бесплатно («see and understand your spending trends»).
Значит, платный контур FINPILOT надо строить не на «мы покажем аналитику», а на
**количественном результате расчёта, которого пользователь сам не получит**: план
распределения свободного денежного потока, Avalanche-очередь долгов, симуляция достижения
цели. Это ближе к «Automated Savings Plan» и «net worth tracking», чем к «Spend Tracking».
Это гипотеза о позиционировании, выведенная из раскладки конкурента, а не из его слов.

#### Продукты БЕЗ бесплатного тарифа

По данным темы 23 (цены не переснимались): **YNAB, Copilot, Monarch** бесплатного тарифа
не имеют вовсе — только пробный период с последующей обязательной оплатой. То есть
на рынке сосуществуют две разные конструкции:
- **freemium с широким бесплатным ядром** (Rocket Money, Credit Karma, Empower) — где
  бесплатное ядро является воронкой либо к премиуму, либо к кредитному офферу;
- **paywall-first, без free-тарифа** (YNAB, Monarch, Copilot) — где вообще нет конверсии
  free→paid как метрики, есть конверсия trial→paid.

🟥 **Конверсия free→paid не раскрывается никем из перечисленных.** Ни Rocket Companies
по Rocket Money (проверено grep-ом по двум 10-K), ни YNAB/Monarch/Copilot (частные).
🔵 **Единственная косвенная оценка, которую можно построить:** на главной Rocket Money
заявлено «**Join 10 million+ members**» (🟩 сайт вендора, 10.09.2026), при раскрытых
**4 583 тыс. платящих подписчиков** на 31.12.2025 (🟩 10-K). Отношение ≈ **46 %**.
⚠️ **В финмодель не брать.** «10 million+» — маркетинговая формулировка без определения,
что считается членом и за какой период; знаменатель почти наверняка кумулятивный
(все когда-либо зарегистрировавшиеся), а числитель — срез на дату. Реальная конверсия
почти наверняка существенно ниже. Пометка: ОЦЕНОЧНОЕ низкого качества.

### 1.3. Комиссии и лидогенерация (Credit Karma, NerdWallet)

#### 1.3.1. Credit Karma (сегмент Intuit) — эталон модели

Полные цифры и дословные формулировки — см. §2.2 выше (они там же, где разбор смерти Mint).
Кратко для этого раздела: 🟩 FY2025 выручка сегмента **$2 263 млн, 100 % — service revenue**,
операционная прибыль **$835 млн (37 % маржи)**. Механика дословно из 10-K:
**cost-per-action** (выдача карты, фондирование займа) + **cost-per-click / cost-per-lead**
(ипотека, страхование) + Credit Karma Money.

#### 1.3.2. 🔴 NerdWallet — вторая полная раскрывающаяся лидогенерация, и с плохими новостями

**Источник:** NerdWallet, Inc. (NASDAQ: NRDS), CIK 0001625278, **Form 10-K за FY2025**
(год до 31.12.2025), подан **25.02.2026**:
https://www.sec.gov/Archives/edgar/data/1625278/000162527826000014/nrds-20251231.htm
Снят полным текстом через `curl` с UA, требуемым SEC. 🟩

**Модель — дословно, Note 2 «Revenue» / MD&A:**
> "We generate **substantially all of our revenue through fees paid by our financial services
> partners** in the form of either **revenue per action, revenue per click, revenue per lead,
> and revenue per funded loan** arrangements. For these revenue arrangements, in which a partner
> pays only when a consumer or SMB satisfies the criteria set forth within the arrangement,
> revenue is recognized generally **when we match the consumer or SMB with the financial services
> partner**."

Дословно, Item 1 Business:
> "These marketplaces generate revenue primarily through **referral fees, partner marketing
> arrangements, and lead-generation compensation structures**."
> "We maintain **editorial standards intended to ensure accuracy, clarity, and impartiality**."

**🟩 Выручка по продуктовым категориям (in millions), Note 2, disaggregation:**

| Категория | FY2025 | FY2024 | FY2023 |
|---|---|---|---|
| Insurance | $280.8 | $191.6 | $45.0 |
| Credit cards | **$133.4** | **$176.4** | **$209.7** |
| SMB products | $100.0 | $109.8 | $101.2 |
| Loans | $133.4 | $84.5 | $101.6 |
| Emerging verticals | $189.0 | $125.3 | $141.9 |
| **Total revenue** | **$836.6** | **$687.6** | **$599.4** |

**🔴 Структура расходов в % от выручки (MD&A, «as a percentage of revenue»):** 🟩

| Статья | 2025 | 2024 | 2023 |
|---|---|---|---|
| Research and development | 8 % | 12 % | 13 % |
| **Sales and marketing** | **70 %** | **69 %** | **67 %** |
| General and administrative | 7 % | 9 % | 10 % |
| Total costs and expenses | 92 % | 99 % | 99 % |
| Income from Operations | 8 % | 1 % | 1 % |
| Net Income (Loss) | 6 % | 4 % | (2 %) |

🔴 **Это главное число участка 1.3: в модели лидогенерации 67–70 % выручки уходит обратно
в маркетинг**, и так три года подряд. Операционная маржа при этом 1 % в 2023–2024 и 8 % в 2025.
То есть лидогенерация — это **бизнес по перепродаже трафика**, а не по удержанию пользователя;
LTV в нём равен нескольким комиссиям, а CAC съедает две трети выручки.
Дословный комментарий о причине скачка расходов 2025:
> "...primarily due to a **$114.1 million increase in sales and marketing expenses**..."

**🔴 Второе важное — обвал кредитно-карточной вертикали и его причина, названная дословно:** 🟩
> "**Credit cards revenue decreased $43.0 million, or 24%,** for 2025 compared to 2024,
> **primarily due to continued pressures in organic search traffic.**"
> "SMB products revenue decreased $9.8 million, or 9%... primarily due to **continued pressures
> in organic search traffic**."

Кредитно-карточная выручка NerdWallet падает третий год подряд: $209.7 → $176.4 → $133.4 млн,
то есть **−36 % за два года**. Причина, названная самим эмитентом — деградация органического
поискового трафика. Компания компенсировала это страхованием ($45.0 → $280.8 млн за два года),
то есть **сменила вертикаль, а не починила канал**.
🔴 Для FINPILOT: модель «контент + SEO + партнёрская комиссия» на глазах ломается под
AI-поиском. Строить монетизацию на ней в 2026 — строить на осыпающемся фундаменте.

**🔴 Третье — лидогенерация в масштабе ЗАСТАВЛЯЕТ получить регулируемый статус.** Дословно,
Item 1 Business, раздел «Financial Services»: 🟩
> "**Next Door Lending, LLC (NDL)** provides **mortgage brokerage and origination services**
> to consumers. NDL does not service mortgage loans or hold mortgage loans for more than 30 days."
> "**NerdWallet Advisory LLC** is an **SEC-registered investment** adviser..."

То есть американский лидер «независимого» сравнения финпродуктов на определённом масштабе
завёл внутри себя **ипотечного брокера и зарегистрированного инвестсоветника**. Это прямая
эмпирическая иллюстрация к участку 4: партнёрское вознаграждение при углублении в воронку
неизбежно упирается в лицензируемую деятельность.

**🟥 Не раскрывает:** NerdWallet в FY2025 10-K **не публикует MUU (Monthly Unique Users)** —
проверено grep-ом, 0 вхождений «MUU»/«Monthly Unique Users» в полном тексте, хотя в ранних
годах после IPO эта метрика раскрывалась. CAC, LTV, отток — не раскрываются вовсе
(в лидогенерации понятия «подписчик» нет, удержания как метрики нет).

### 1.4. B2B-лицензирование движка банкам

Вендоры PFM-движков (Personetics, Meniga, Strands, Moneythor, MX, Tink) — **частные компании,
цен и метрик не раскрывают**; их целевая функция названа ими же дословно (LTV, ARPU, кросс-сейл)
в теме 19 (`raw/pfm_engine_vendors_v2_2026-09-09.md`) и здесь не переснимается.
🟥 Прайс-листов и длины цикла продажи по ним в открытом доступе нет.

**🔴 Обходной путь, который сработал: взять публичного вендора того же класса.**
**Q2 Holdings, Inc. (NYSE: QTWO)**, CIK 0001410384 — SaaS-платформа цифрового банкинга
для финансовых организаций США. Она **обязана раскрывать модель ценообразования, длину
контракта и отток**, и делает это в 10-K. Это единственный доступный количественный
ориентир по B2B-контуру PFM.

**Источник:** Q2 Holdings, **Form 10-K за FY2025** (год до 31.12.2025), подан **11.02.2026**:
https://www.sec.gov/Archives/edgar/data/1410384/000141038426000006/qtwo-20251231.htm
Снят полным текстом через `curl` с UA SEC. 🟩

**За что берут деньги — дословно (ответ на вопрос «за клиента? за банк? revenue share?»):** 🟩
> "We offer our solutions to most of our customers using a **SaaS model under which our customers
> pay subscription fees** for the use of our solutions."
> "**We generally price our digital banking platform solutions based on the number of solutions
> purchased by our customers and the number of Registered Users**, as defined in 'Key Operating
> Measures' below, **or commercial account holders utilizing our solutions.**"
> "We generally earn **additional revenues** from our digital banking platform customers **based on
> the number of End Users on our solutions, the number of transactions that End Users perform
> on our solutions and the excess number of users and transactions above what is included in our
> standard subscription fee.**"

🔴 **Ответ прямой: не revenue share и не фикс за банк, а двухкоординатная подписка —
(число купленных модулей) × (число зарегистрированных пользователей), плюс overage
за превышение включённого объёма пользователей и транзакций.** Это классический
per-seat SaaS с пакетом и переплатой сверх пакета.

**Длина контракта — дословно:** 🟩
> "**The initial term of our digital banking platform agreements averages over five years.**"
> "A substantial majority of our revenue is generated from subscription-based arrangements with
> multi-year terms, and the initial term of our digital banking platform agreements averages
> over five years."

**🟩 Раскрытые метрики Q2 Holdings (все — из 10-K FY2025, «Key Operating Measures»):**

| Метрика | FY2025 | FY2024 | FY2023 |
|---|---|---|---|
| Registered Users (клиентов банков-заказчиков), млн | 27.3 | 24.7 | 22.0 |
| Subscription ARR, $ млн | 780.1 | 681.9 | 593.9 |
| Total ARR, $ млн | 921.4 | 824.2 | 734.8 |
| **Net revenue retention rate** | **113 %** | 109 % | 108 % |
| **Subscription net revenue retention rate** | **115 %** | 114 % | 112 % |
| **Annual revenue churn** | **5.2 %** | 4.4 % | 6.1 % |

Определение оттока — дословно (важно, это МЕТОДИКА, а не «принято считать»): 🟩
> "We define **revenue churn** as the amount of any monthly recurring revenue losses due to
> **customer cancellations and downgrades, net of upgrades and replacements** of existing
> solutions, during a year, **divided by our monthly recurring revenue at the end of the prior
> year.** Cancellations refer to customers that have either stopped using our services completely
> or remained a customer but terminated a particular service. Downgrades are a result of customers
> taking less of a particular service or renewing their contract for identical services
> at a lower price."
> "We had **annual revenue churn of 5.2%, 4.4% and 6.1%** for the years ended December 31, 2025,
> 2024 and 2023, respectively."

**🔵 Что это даёт FINPILOT (наш вывод):**
- B2B-контур — это **годовой отток 4–6 % ВЫРУЧКИ при пятилетних контрактах и NRR 113–115 %**,
  то есть база не только не тает, а растёт сама. По устойчивости это на порядок лучше
  потребительской подписки. **Цена входа** — цикл продажи, который Q2 сама называет
  риском: "the **length, cost and unpredictability of our sales cycle**" (Item 1A Risk Factors,
  дословно) 🟩. Конкретной длины в месяцах компания не публикует. 🟥
- Модель «за модуль × за пользователя + overage» — готовый шаблон прайсинга, если FINPILOT
  когда-нибудь будет продаваться банку как движок. Но это **прямо противоречит
  позиционированию «нет продавца в контуре»**: банк покупает движок ровно ради кросс-сейла,
  что вендоры и называют своей целевой функцией.
- 🟥 **Envestnet/Yodlee не добыт:** Envestnet, Inc. в 2024 году выкуплена Bain Capital и
  **делистингована**, публичной отчётности за FY2025 не подаёт. Отдельных раскрытий
  по Yodlee нет.
- 🟥 **MoneyLion не добыт как отдельный эмитент:** компания приобретена Gen Digital
  (сделка объявлена 12.2024, закрыта 2025), самостоятельные 10-K после этого не подаются.
  Сегментного раскрытия по MoneyLion внутри Gen Digital в рамках бюджета темы не найдено.
- 🟥 **Acorns** — частная компания; SPAC-сделка (с Pioneer Merger Corp) **была расторгнута
  в 2022 году**, то есть публичных раскрытий по итогам SPAC не появилось. Проспекта S-1
  в EDGAR по действующей Acorns нет.

### 1.5. Реклама

**Короткий ответ: чистой рекламной модели в PFM практически не существует — она везде
вырождается в лидогенерацию.**

Обоснование из добытого:
- Credit Karma формально имеет рекламный компонент, но **сам эмитент классифицирует его как
  cost-per-click / cost-per-lead, то есть плату за приведённого клиента, а не за показ**
  (10-K INTU FY2025, дословная цитата в §2.2). Плата за показ (CPM) в структуре выручки
  не упоминается вовсе.
- NerdWallet: "**substantially all of our revenue** through fees paid by our financial services
  partners in the form of either **revenue per action, revenue per click, revenue per lead,
  and revenue per funded loan**" (10-K NRDS FY2025). Опять — ни одной строки за показ.
- Mint в своё время был ближе всех к рекламной модели (баннеры и офферы поверх бесплатного
  трекера) — и был закрыт владельцем в пользу актива с чистой моделью cost-per-action (§2.2).

**Причина, почему CPM не работает в PFM (наш вывод из чисел, не цитата):** аудитория PFM мала
по меркам рекламного рынка (Rocket Money — «10 million+ members», Q2 — 27 млн, тогда как
рекламные площадки оперируют сотнями миллионов), но **уникально квалифицирована**:
про пользователя известны доход, долги, платёжное поведение. Рекламодателю выгоднее платить
за результат (выданная карта, профондированный заём), а площадке выгоднее продавать результат,
чем показы. Поэтому равновесие рынка — cost-per-action, а не CPM.

🔴 **Для FINPILOT это означает, что «мы поставим рекламу, зато не будем продавать продукты»
не является отдельной, более мягкой опцией.** На практике рекламодателем в этой нише
выступает тот же банк/МФО с тем же оффером, и модель схлопывается в лидогенерацию,
то есть в ровно тот конфликт интересов, который обозначил ЦБ РФ. Правовая сторона —
участок 4.

---

## Участок 2. КЛАДБИЩЕ

### 2.1. Tally (приоритет №1)

**Реквизиты компании.** Tally Technologies, Inc., Сан-Франциско. Основана 2015. Основатель и CEO —
Jason Brown. Продукт: автоматизированный менеджер погашения долга по кредитным картам — пользователь
привязывает карты, Tally выдаёт кредитную линию под более низкий процент и сама платит по картам
в оптимальном порядке.

**Дата закрытия:** объявлено 12.08.2024, штат уволен целиком. 183 сотрудника на момент закрытия.
🟩 (TechCrunch 12.08.2024; Banking Dive)

**Привлечено и от кого.**
- 🟩 TechCrunch: **$172 млн** всего. Последний раунд — **Series D, октябрь 2022, $80 млн, лидер
  Sway Ventures**. Series C (2019) — **$50 млн, лидер Andreessen Horowitz**, с участием
  Kleiner Perkins, Shasta Ventures, Cowboy Ventures, Sway Ventures.
- 🟩 Оценка **$855 млн** (по данным PitchBook — то есть сама цифра оценки 🟨 вторична, PitchBook,
  а не раскрытие компании).
- ⚠️ **Расхождение источников:** Banking Dive пишет «raised over $200 million», TechCrunch — $172 млн.
  В задании фигурировал $172 млн. Вероятно, разница — учёт долгового финансирования кредитного
  портфеля против только equity. Ни один из двух источников не разбивает.

**Дословное заявление о закрытии (Jason Brown).** 🟩
> "we have made the difficult and sad decision to shut down Tally"
> "This was not the outcome we had hoped for, but after exploring all options, **we were unable to
> secure the necessary funding to continue our operations**"
> "Tally was designed to be more than just a tool; it was a financial coach working quietly in the
> background"
> "We started the company going straight to the people who needed it most... **our overall impact
> can be much greater if we enable partners to leverage our technology**"
> "While this is the end for Tally, our expectation is that it is not the end of our mission"

(источник: Banking Dive, «Tally sunsets over failure to raise capital»,
https://www.bankingdive.com/news/fintech-tally-closes-over-failure-to-raise-capital/724263/ ;
TechCrunch 12.08.2024,
https://techcrunch.com/2024/08/12/a16z-backed-fintech-tally-which-raised-172m-in-funding-is-shutting-down-after-running-out-of-cash/ )

**🔴 Разбор причины — ключевое для FINPILOT.**
Официальная причина, названная основателем: **не смогли привлечь финансирование**. Но это следствие,
а не механизм. Механизм виден в хронологии:

1. Tally зарабатывала **не на подписке за аналитику, а на процентной марже кредитной линии**
   (спред между стоимостью фондирования и ставкой по своей линии) плюс исторически — членский взнос.
   То есть это был **балансовый бизнес** (lender), а не SaaS. Такому бизнесу нужен постоянный
   приток капитала под портфель.
2. 🟩 **Апрель 2024 — Tally свернула прямой потребительский кредитный портфель (D2C)** и объявила
   пивот в **B2B: white-label ПО управления долгом через партнёров**. То есть компания сама
   признала, что D2C-экономика не сходится (Banking Dive).
3. 🟩 Пивот был подкреплён заявлением о партнёре — «**large publicly-traded consumer company with
   more than 50 million users**», запуск планировался на **июль 2024**. Формального анонса
   не последовало (TechCrunch).
4. 🟩 **Менее чем через 6 месяцев после объявления пивота — закрытие.** То есть B2B-канал
   не успел дать выручку в темпе, покрывающем расходы 183 сотрудников.
5. 🟩 Заявленный полезный результат: пользователи погасили **более $2 млрд долга** (Banking Dive).
   Продуктовая ценность была; сходимости юнит-экономики при этом не было.

**Вывод для FINPILOT (наш, не из источника).** Смерть Tally — **не аргумент против подписочной
СППР по долгу**. Tally умерла как **кредитор**, зависимый от рынка капитала 2022–2024 (рост ставок
ФРС → удорожание фондирования → спред схлопывается → нужен новый капитал → его не дают).
FINPILOT не выдаёт денег и не держит баланса; у него нет ни стоимости фондирования, ни кредитного
риска, ни потребности в капитале под портфель. Правильная формулировка защиты: **«Tally проиграла
на процентной марже, а не на рекомендации»**.
🟥 **Не добыто:** прямого числа CAC/LTV/оттока Tally нет ни в одном из просмотренных источников —
компания была частной и отчётности не публиковала.

### 2.2. Mint / Intuit (приоритет №2)

**Хронология.** Mint куплен Intuit в 2009 за **$170 млн** (🟨 вторичный источник: Tech Startups,
06.11.2023 — сама сделка 2009 общеизвестна, но цифру беру как вторичную). Объявление о закрытии —
**31.10.2023**; официально «Mint больше не будет доступен с 01.01.2024»; фактическое отключение
произошло **23.03.2024** (🟨 вторичные: PYMNTS 2023; Spendify).

**Дословное заявление Intuit** (цитируется PYMNTS и Bloomberg, 01.11.2023): 🟩 (первоисточник —
заявление Intuit, добыт через вторичную публикацию)
> "Last year, the Intuit Mint team joined Intuit Credit Karma to help build one of our newest
> experiences that will help millions of members know, grow and protect their net worth."
> "...marks the next evolution of Credit Karma, one that combines the money management product
> expertise and momentum of Mint with Credit Karma's scale, technology and vast product ecosystem."

Пользователям предложили выгрузить данные и завести аккаунт Credit Karma.
Источники: https://www.pymnts.com/financial-apps/2023/intuit-to-shut-down-mint-invite-users-to-credit-karma/ ,
https://www.bloomberg.com/news/articles/2023-11-01/intuit-winds-down-personal-finance-app-mint-shifts-users-to-credit-karma

**🔴 Что реально произошло — доказательство из отчётности, а не из пресс-релиза.**

Intuit Inc., **Form 10-K за FY2025 (год закончился 31.07.2025), поданный 03.09.2025**
(https://investors.intuit.com/sec-filings/all-sec-filings/content/0000896878-25-000035/intu-20250731.htm ),
раздел Item 7, «Segment Results → Credit Karma», с. 42–43. 🟩 **РАСКРЫТОЕ, дословно:**

> "Credit Karma segment revenue is primarily derived from **cost-per-action transactions**, which
> include the delivery of qualified links that result in completed actions such as credit card
> issuances and personal loan funding; **cost-per-click and cost-per-lead transactions**, which
> include user clicks on advertisements or advertisements that allow for the generation of leads,
> and primarily relate to mortgage and insurance businesses; and Credit Karma Money."

Финансы сегмента Credit Karma (Dollars in millions), там же: 🟩

| Показатель | FY2025 | FY2024 | FY2023 |
|---|---|---|---|
| Service revenue | $2,263 | $1,708 | $1,634 |
| Product and other revenue | — | — | — |
| **Total segment revenue** | **$2,263** | **$1,708** | **$1,634** |
| Δ г/г | 32 % | 5 % | — |
| % of total Intuit revenue | 12 % | 10 % | 11 % |
| **Segment operating income** | **$835** | **$414** | **$428** |
| % of related revenue (опер. маржа) | **37 %** | 24 % | 26 % |

Дословно о драйверах роста: 🟩
> "Revenue for our Credit Karma segment increased $555 million, or 32%, in fiscal 2025 compared with
> fiscal 2024 due to increases in revenue from our **personal loan vertical of $221 million**, our
> **credit card vertical of $213 million**, and our **auto insurance vertical of $99 million**.
> Credit Karma segment operating income increased $421 million, or 102%... partially offset by an
> increase in **marketing expenses of $120 million**."

Описание платформы, Item 1 Business: 🟩
> "...access to their credit scores and reports, credit and identity monitoring, credit building,
> credit report dispute, **tools to help understand net worth and make financial progress**,
> **personalized recommendations of credit card, loan, and insurance products**..."
> "Credit Karma leverages **Lightbox**, a first-of-its-kind enterprise platform which allows
> **lenders** to leverage thousands of de-identified data points from Credit Karma members to help
> provide our members with greater certainty that they will be approved if they apply for a
> financial product."

**🔴 Наблюдение, добытое механически:** в тексте 10-K за FY2025 слово **«Mint» не встречается
ни разу** (проверено grep по полному тексту документа, 2,8 МБ; 58 вхождений «Credit Karma»,
0 вхождений «Mint»). Бренд, куплённый за $170 млн и проживший 15 лет, полностью исчез
из отчётности через полтора года после отключения.

**Причина закрытия Mint — вывод, подтверждаемый цифрами.**
Mint монетизировался слабо (рекламные врезки и партнёрские предложения поверх бесплатного
трекера) и **дублировал воронку** Credit Karma. Credit Karma при этом — **чистая машина
лидогенерации**: 100 % выручки — service revenue от cost-per-action / cost-per-click /
cost-per-lead, **$2,263 млн выручки при операционной марже 37 %** и трёх верталях-драйверах
(потребкредит, кредитные карты, автострахование).
То есть Intuit закрыл PFM-продукт **не потому, что PFM не нужен, а потому что PFM внутри
экосистемы — это КАНАЛ к кредитному офферу, а не продукт**; двух каналов к одному офферу
держать нет смысла, а побеждает тот, что ближе к моменту выдачи кредита.
🔴 **Прямое следствие для FINPILOT:** кейс Mint показывает, что бесплатный PFM без собственной
монетизации выживает только как надстройка над продажей финансовых продуктов. Поскольку
FINPILOT сознательно отказывается от продавца в контуре (позиция ЦБ РФ о независимости сервисов
финансового здоровья), **у него остаётся ровно один источник выручки — прямая плата пользователя**.
Это не ограничение архитектуры, это следствие позиционирования.

### 2.3. Прочие могилы

#### Playbook (США) — единственная, где сохранилось дословное объявление о закрытии

- Продукт: подписочное приложение персональных финансов/инвестиций для high-income tech-работников
  (налогово-оптимизированное инвестирование), с функцией инвестсоветника.
- 🟩 Привлечено: **$7 млн Series A, март 2023** (fintech.global, 30.03.2023,
  https://fintech.global/2023/03/30/personal-finance-app-playbook-snares-7m-in-series-a/ ).
- 🟩 **Объявление о сворачивании — 01.10.2024**, платформа доступна до **31.10.2024**.
  Страница объявления (жива, снята напрямую): https://helloplaybook.webflow.io/
  Дословно:
  > "After much consideration, we've made the tough decision to wind down Playbook."
  > "We're proud of the financial progress you've made, and we're excited to see where your
  > financial journey takes you next." — подписано "The Playbook Team".
- Механика сворачивания (полезно как образец процедуры для нашей оферты): обновление балансов
  по внешним счетам прекращается немедленно; списания прекращаются немедленно; **подписчикам,
  списанным за период после 31.10.2024, возвращаются деньги за неиспользованную часть**;
  30 дней на выгрузку данных; налоговые формы за 2025 выдаёт кастодиан Apex Clearing.
- 🔴 **Причина не названа вообще.** Ни в объявлении, ни в найденных вторичных источниках.
  Это честный отрицательный результат: заявление есть, объяснения нет.
  ⬜ Реконструкция (НЕ ПРОВЕРЕНО): $7 млн Series A + подписочная модель + очень узкий сегмент
  (tech-работники с высоким доходом) → низкий потолок рынка при высоком CAC. Как гипотеза,
  не как факт.

#### Charlie (США)

- 🟨 **Август 2021 — приложение закрыто, команда перешла в Chime** (вторичный источник,
  CB Insights / Dealroom). Это **acqui-hire**, то есть выход через покупку команды,
  а не смерть от экономики.
- 🟥 Дословного заявления основателя не добыто.

#### Simple (США) — образец «смерти через поглощение банком»

- 🟩 Куплена BBVA в **2014 за $117 млн**; **закрыта в 2021**; клиенты переведены в BBVA USA,
  затем в PNC (BBVA продала розницу США за **$11.6 млрд**).
- 🔴 **Причина названа прямо и по имени** — American Banker, «Is BBVA's shutdown of Simple
  a bad sign for bank-fintech mergers?»,
  https://www.americanbanker.com/news/is-bbvas-shutdown-of-simple-a-bad-sign-for-bank-fintech-mergers
  🟩 (цитаты именованных экспертов):
  > **Todd Baker** (Richman Center, Columbia University): "The politics inevitably end up crushing
  > the innovation. When I did bank acquisitions, I used to call this **'destroying the village
  > in order to save it.'**"
  > Baker: "**When BBVA bought Simple, it cut the main source of its freestanding revenues in half.**"
  > **Brian Hamilton** (CEO, One): "**Simple essentially died the day BBVA bought it.** BBVA forced
  > Simple to use its core system." · "**Being bought by a mainstream bank is the equivalent of death.**"
  > **Stephen Greer** (Celent): "You're moving customer accounts from one legacy bank to another
  > legacy bank. These tend to be long and arduous and can take years."
- 🔴 **Механизм смерти назван точно и он ЭКОНОМИЧЕСКИЙ, а не продуктовый:** Simple жила
  на интерчейндже через партнёрский The Bancorp Bank ($7.7 млрд активов, вне потолка
  поправки Дурбина). После перехода под BBVA ($103 млрд активов) интерчейндж попал под
  потолок **21 цент + 0.05 %** — **основной источник выручки уполовинился одним фактом смены
  владельца**. Это редкий случай, когда причина смерти PFM-продукта названа с точностью
  до нормы регулирования.

#### Clarity Money (США)

- 🟩 Куплен **Goldman Sachs в 2018**; **закрыт в феврале 2024**, технология влита
  в **Marcus Insights** (American Banker, там же).
- Тот же класс, что Mint: PFM внутри финансовой экосистемы существует как канал; когда
  экосистема меняет стратегию (Goldman сворачивал розницу Marcus), канал закрывают.

#### Level Money (США)

- 🟨 Куплен Capital One, затем закрыт (American Banker перечисляет в одном ряду с Simple
  и Mint). Реквизитов сделки и дословного заявления не добыто. 🟥

#### Guiabolso (Бразилия)

- Крупнейший PFM Латинской Америки. 🟩 Привлекал **$39 млн** (раунд октябрь 2017, TechCrunch).
- 🟩 Куплен **PicPay** (август 2021; сумма сделки не раскрыта, сделка закрыта примерно
  за три дня). На момент продажи — **более 6 млн пользователей**.
- 🟩 **Закрыт в ноябре 2022**; весь функционал перенесён в PicPay, где запущен раздел
  **«Minhas finanças»** — по формулировке источника, «своего рода мини-Guiabolso».
  Источник: Finsiders Brasil,
  https://finsidersbrasil.com.br/noticias-sobre-fintechs/guiabolso-comprado-pelo-picpay-sera-encerrado-em-novembro/
- 🟩 **Отдельная, специфическая причина боли — стоимость и легальность доступа к банковским
  данным:** «на всём протяжении своей траектории Guiabolso сталкивался с вопросами к своей
  модели доступа к банковским данным, при этом **Bradesco в 2016 году подал против компании
  иск**, ссылаясь, среди прочего, на недостаток безопасности» (Finsiders).
  🔴 Это единственный кейс в подборке, где смерть напрямую связана с **агрегацией данных**:
  скрейпинг банковских данных был юридически атакован банком-держателем данных.
  Развязка — Open Finance: как только агрегация стала регулируемой и общедоступной,
  отдельная ценность агрегатора обнулилась, и он был поглощён платёжной экосистемой.
  **Прямая аналогия для РФ:** открытые API/Открытые финансы Банка России двигаются туда же —
  агрегация перестаёт быть барьером входа и не может быть основой ценности продукта.

#### Digit → Oportun (США) — не смерть, но поучительная цена

- 🟩 Куплен **Oportun Financial Corp (NASDAQ: OPRT)**, сделка объявлена ноябрь 2021,
  **закрыта 22.12.2021**. Цена — **$212.9 млн** ($98.5 млн акциями + $114.4 млн деньгами).
  На момент сделки у Digit было **600 000 платящих участников** (🟨 American Banker/Finextra;
  дата закрытия сделки 🟩 из 10-K Oportun).
- 🔵 **Наш расчёт:** $212.9 млн / 600 тыс. платящих = **≈ $355 за платящего подписчика**.
  Это единственная в подборке рыночная оценка «сколько стоит один платящий подписчик PFM»,
  полученная из реальной сделки. При ARPU Rocket Money ~$75–81/год это соответствует примерно
  **4.5–4.7 годам выручки на подписчика** — то есть покупатель закладывал очень длинную жизнь
  подписчика (или синергию с кредитованием).
- 🟩 Oportun, Form 10-K FY2024
  (https://www.sec.gov/Archives/edgar/data/1538716/000153871625000013/oprt-20241231.htm ):
  сберегательный продукт Digit выжил как фича под именем **Set & Save**, дословно:
  > "**Set & Save Savings** – Our Set & Save product is designed to understand a member's cash
  > flows and save the right amount on a regular basis... Since 2015, our savings product has
  > helped members save more than **$11.4 billion** and helped our members save an average of
  > more than **$1,800 annually**."
  Но: 🟩
  > "In the annual period ended December 31, 2023, the Company recognized a **non-cash pre-tax
  > impairment charge of $5.6 million related to the write-off of embedded finance, investing
  > and retirement products.**"
  То есть **инвестиционная и пенсионная части Digit были списаны в ноль**, выжила только
  сберегательная автоматика. Приобретённая технология Digit числится как $48.5 млн
  «acquired developed technology», амортизируется 7 лет.
- 🔴 Вывод: даже успешный по продукту PFM внутри кредитора выживает **той частью, что
  кормит кредитный бизнес**, а остальное списывается. Тот же закон, что у Mint.

#### 🔴 Moneyhub (Великобритания) — уточнение: умер D2C, компания жива

Первоначальная формулировка задания («Moneyhub» в списке кладбища) **уточнена добытым
источником**: закрылась не компания, а её **потребительское направление**. И это, возможно,
самый релевантный для FINPILOT кейс во всей подборке, потому что закрытие произошло
**на фоне роста компании**, а не на фоне провала.

**Источник:** FinTech Futures, эксклюзив, **опубликован 14.02.2025**, автор Tyler Pathe:
https://www.fintechfutures.com/job-cuts-new-hires/exclusive-moneyhub-shutters-d2c-business-lays-off-around-30-of-uk-workforce
🟩 (прямой `WebFetch` дал **403**; снято через текстовый прокси `r.jina.ai`, полный текст).

Дословно, факты:
> "Open finance and data platform Moneyhub is set to shutter its direct-to-consumer (D2C) app
> business, a move that will also see the company **reduce its UK workforce by 'around 30%'**."
> "...which has led to the elimination of '**approximately 36 positions**'..."
> "The company's D2C proposition, which is spearheaded by the Moneyhub app, will be closed down
> gradually '**over the next 18 months**', **coinciding with the expiration of existing paid
> subscriptions**."
> "Moneyhub has **stopped accepting new customers for its app with immediate effect**."

**🔴 Дословное заявление самой компании** (statement to FinTech Futures): 🟩
> "Our business performance remains strong and we are expecting to report that we're sustaining
> a **revenue CAGR exceeding 35%**."
> "**Our growth has been driven from the B2B sectors we serve; Banking, Lending and Collections,
> Consumer Finance, Pensions and Insurance. To better focus on these growing B2B markets we have
> decided to withdraw from our direct-to-consumer app business.**"

Смена CEO: Samantha Seaton → **Alastair McGill** (экс-GM Broadridge), вступил в должность
в конце января 2025. То есть решение принято практически сразу после смены руководства.
🟨 Дата фактического отключения потребительского сервиса — **14.08.2026** (вторичные обзоры),
что согласуется с заявленными «18 месяцев» от февраля 2025.

**🔴 Почему это важнее прочих могил.** Здесь причина названа компанией прямо и она
**не «мы не смогли»**, а **«B2B растёт быстрее, D2C отвлекает»**. Компания с CAGR >35 %
осознанно вышла из потребительской подписки. Это тот же манёвр, что у Tally (апрель 2024,
сворачивание D2C ради B2B) — только Tally сделала его слишком поздно и без денег, а Moneyhub
вовремя и из позиции силы. **Два независимых случая из десяти — уход из потребительской
подписки в B2B — это уже закономерность, а не совпадение**, и FINPILOT должен назвать
для себя, чем он от них отличается.
Отличие, если формулировать честно: у Moneyhub и Tally D2C-приложение было надстройкой
над технологией (агрегация данных / кредитная линия), которую можно продать банку дороже.
У FINPILOT продаваемая ценность — сама методика распределения денежного потока
(SAW + Avalanche + SES/Монте-Карло), и при продаже её банку она немедленно попадает
под целевую функцию банка (кросс-сейл), то есть перестаёт быть тем, что мы обещаем.
Это делает уход в B2B для нас не запасным аэродромом, а сменой продукта.

**Также отмечу процедурную деталь, полезную для нашей оферты:** Moneyhub сворачивал D2C
**«по мере истечения уже оплаченных подписок»** — то есть не прерывал оплаченный период,
а дорабатывал его. Playbook пошёл другим путём — вернул деньги за неиспользованную часть
(§ Playbook выше). Обе процедуры законны и обе стоит предусмотреть в оферте FINPILOT
на случай прекращения сервиса (см. участок 4.3, ЗоЗПП).

#### Prism

- 🟥 Не добыто. Целевых источников о закрытии не найдено; вероятно, речь о Prism Bill Pay
  (PayNearMe/Prism Money). Реквизитов нет.

---

## Участок 3. Сводная таблица экономики

### 3.1. Всё раскрытое, в одной таблице

Пустая клетка = **«не раскрывает»**. Интерполяций нет. Класс доказательства — в последней колонке.

| Компания / продукт | Модель | Выручка (последний год) | Платящие | CAC | LTV | Конверсия free→paid | Отток | Выручка на пользователя | Источник | Класс |
|---|---|---|---|---|---|---|---|---|---|---|
| **Rocket Money** (Rocket Companies, RKT) | Freemium-подписка (~90 % выручки) | $390 млн (FY2025), в т.ч. подписка $351 млн | **4 583 тыс.** (31.12.2025) | не раскрывает | не раскрывает | не раскрывает | **не раскрывает** | ≈ **$80.7/год** (наш расчёт) | 10-K RKT FY2025, «Select Other», Note ASC 606 | 🟩 / 🔵 расчёт |
| **Credit Karma** (сегмент Intuit, INTU) | Лидогенерация (CPA/CPC/CPL) | **$2 263 млн** (FY2025), опер. прибыль $835 млн (37 %) | н/п (бесплатно) | не раскрывает | не раскрывает | н/п | н/п | не раскрывает | 10-K INTU FY2025, Item 7, Segment Results, с. 42–43 | 🟩 |
| **NerdWallet** (NRDS) | Лидогенерация (RPA/RPC/RPL/RPFL) | **$836.6 млн** (FY2025) | н/п | не раскрывает; **S&M = 70 % выручки** | не раскрывает | н/п | н/п | не раскрывает; MUU больше не публикует | 10-K NRDS FY2025, Note 2, MD&A | 🟩 |
| **Q2 Holdings** (QTWO) — B2B-прокси | SaaS: (модули) × (Registered Users) + overage | Subscription ARR **$780.1 млн**; Total ARR $921.4 млн (FY2025) | 27.3 млн Registered Users у банков-заказчиков | не раскрывает | не раскрывает | н/п | **revenue churn 5.2 %/год**; **NRR 113 %**, subscription NRR 115 % | не раскрывает | 10-K QTWO FY2025, Key Operating Measures | 🟩 |
| **Monarch Money** | Подписка, без free-тарифа | ARR ≈ $12.6 млн (2025) | не раскрывает | не раскрывает | не раскрывает | н/п (нет free) | не раскрывает | не раскрывает | getlatka (агрегатор); раунд — CNBC 23.05.2025 | 🟨 низкого качества |
| **Digit** (на момент продажи Oportun, 2021) | Подписка | не раскрывает | **600 тыс. платящих** | не раскрывает | **цена сделки $212.9 млн ⇒ ≈ $355 за платящего** (наш расчёт) | не раскрывает | не раскрывает | не раскрывает | 10-K OPRT FY2024; American Banker/Finextra | 🟩 сделка / 🟨 число платящих / 🔵 расчёт |
| **Tally** | Процентная маржа кредитной линии + членский взнос | не раскрывает (частная) | не раскрывает | не раскрывает | не раскрывает | не раскрывает | не раскрывает | не раскрывает | — | 🟥 |
| **YNAB · Copilot · Simplifi** | Подписка | не раскрывает | не раскрывает | не раскрывает | не раскрывает | не раскрывает | не раскрывает | не раскрывает | частные компании | 🟥 |

**🔴 Главное наблюдение по таблице: CAC, LTV и отток в потребительском PFM не раскрывает
НИКТО.** Ни один эмитент из четырёх публичных. Раскрываются: выручка, число платящих
(только Rocket Money) и — в B2B — отток выручки и NRR (только Q2). Любая цифра CAC/LTV
по потребительскому PFM, встреченная в интернете, является оценкой третьей стороны,
и её методику надо требовать отдельно.

### 3.2. Отраслевые бенчмарки оттока в потребительской подписке — с методикой

Единственный найденный источник, который **измеряет, а не рассуждает** — **Recurly Research**
(Recurly — биллинговый провайдер, считает по собственной сети клиентов, то есть по реальным
транзакциям, а не по опросу). 🟨 **Класс: ОЦЕНОЧНОЕ, но с раскрытой методикой** — это
не отчётность эмитента, но и не «принято считать».

**Методика — дословно с https://recurly.com/research/churn-rate-benchmarks/ (снято 10.09.2026):**
> "(subscribers lost in month / subscribers at start of month) × 100" — для месячного оттока;
> годовой считается через компаундирование.
> Источник данных: "Recurly's network of subscription businesses", "All figures are updated
> with **July 2026** data".
> Размер выборки и доверительные интервалы **не раскрыты**.
> В смежной публикации Recurly сеть описана как «**more than 2000 businesses over the last year**».

**Числа (Recurly, срез июль 2026):** 🟨

| Отрасль | Total | Voluntary | Involuntary |
|---|---|---|---|
| SaaS | 3.22 % | 2.16 % | 1.06 % |
| Ecommerce (DTC) | 4.25 % | 2.87 % | 1.38 % |
| Digital Media & Entertainment | 4.14 % | 2.55 % | 1.59 % |
| Education | 4.99 % | 3.30 % | 1.69 % |
| Business & Professional Services | 3.44 % | 2.27 % | 1.18 % |
| **Среднее по всем отраслям** | **3.60 %** | 2.34 % | 1.25 % |

Отток в разрезе средней выручки на клиента (ARPC): 🟨
- $10–$25: Total 4.29 % · Voluntary 2.99 % · Involuntary 1.30 %
- $250+: Total 3.07 % · Voluntary 2.90 % · **Involuntary 0.18 %**

⚠️ **Расхождение внутри самого источника, называю прямо:** в поисковой выдаче по материалам
Recurly фигурируют «средний отток 5.6 %, voluntary 4.0 %, involuntary 1.4 %», тогда как
на странице бенчмарков — 3.60 / 2.34 / 1.25 %. Разные страницы Recurly дают разные цифры
(вероятно, разные срезы и разные даты обновления). **Пока расхождение не устранено, брать
диапазон 3.6–5.6 % месячного оттока, а не точку.** Устранить расхождение в рамках бюджета
темы не удалось.

**🔵 Что из этого следует для FINPILOT (арифметика, не источник):**
- Месячный отток **4 %** → средняя жизнь подписчика 1/0.04 = **25 месяцев**.
- Месячный отток **5.6 %** → **≈ 18 месяцев**.
- Два наблюдения из данных Recurly, полезные при выборе тарифа:
  (1) **involuntary churn** (сбой платежа, а не решение уйти) даёт **от четверти до трети
  всего оттока** — это чинится техникой (ретраи, напоминание об истечении карты),
  а не продуктом; для РФ с рекуррентными платежами через эквайринг это отдельная
  инженерная задача, не маркетинговая;
  (2) в дорогом сегменте ($250+) involuntary падает почти до нуля (0.18 %), то есть
  **годовая оплата вместо месячной сама по себе убирает большую часть технического оттока**.
- Ориентир, который можно нести в финмодель, с явной пометкой класса: месячный отток
  **4–5.6 % (🟨 Recurly, методика раскрыта, выборка нет)**; жизнь подписчика **18–25 мес.**;
  ARPU подписочного PFM **$75–81/год (🟩 расчёт из 10-K Rocket Companies)**.
  🔴 Соотносить с РФ напрямую нельзя: и платёжеспособность, и платёжная инфраструктура,
  и привычка платить за ПО отличаются. Это ориентир порядка величины, а не прогноз.

---

## Участок 4. Правовой фильтр РФ

### 4.0. Позиция ЦБ РФ — реквизиты цитаты, на которой держится наше позиционирование

Цитата фигурирует в брифе темы без реквизитов; здесь она добыта с атрибуцией. 🟩

**Источник:** материал «Известий» «Доходы ИИ расходы: банки запускают сервисы по улучшению
"финансового здоровья" россиян», **опубликован 15.08.2024**, перепечатка на finance.mail.ru:
https://finance.mail.ru/article/dohody-ii-rashody-banki-zapuskayut-servisy-po-uluchsheniyu-finansovogo-zdorovya-rossiyan-62370058/
Цитируется **пресс-служба Банка России**, дословно:

> «при этом важно, чтобы сервисы были **независимыми**, то есть в них **не было скрытой
> рекламы и продажи финансовых продуктов**»

Контекст — раздел «Зачем отслеживать кредитную нагрузку и доходы»: инструменты должны помогать
гражданам оценить доходы, расходы и долговую нагрузку, сохраняя независимость от коммерческих
интересов.

**🔴 Класс доказательства — важное уточнение.** Это **комментарий пресс-службы СМИ**,
а не нормативный акт, не информационное письмо и не указание Банка России. Юридической
силы он не имеет; это **сигнал регуляторного ожидания**. Строить на нём позиционирование
можно и нужно, но нельзя ссылаться на него как на норму.

**🔴 И сразу — противоречие, которое надо назвать прямо.** В той же публикации перечислены
те, кто запускает сервисы финансового здоровья в РФ: **Т-Банк** (сервис «Финздоровье»),
**Сбер** (в тестовом режиме), **Зенит** (рассматривал запуск в 2025). То есть регулятор
говорит «сервис должен быть независимым и не продавать финансовые продукты», а фактические
операторы таких сервисов на российском рынке — **сами банки, для которых продажа финансовых
продуктов является основной деятельностью**. Это не наша интерпретация, это прямое
сопоставление двух частей одной статьи.

Для FINPILOT это одновременно риск и главный аргумент: **ниша «независимого финздоровья»
на российском рынке декларирована регулятором, но структурно не может быть занята банками** —
и потому остаётся свободной ровно для независимого подписочного продукта.
Обратная сторона: это же лишает нас лидогенерации как источника выручки (см. ответ (в)).

### 4.1. Ст. 28 ФЗ «О рекламе» (38-ФЗ) — дословно

Статья добыта **полностью**, все 15 частей. В теме 18 она оставалась не снятой дословно —
пробел закрыт. Источник: `https://www.zakonrf.info/zoreklame/28/`, канал `curl`
с браузерным UA, **HTTP 200**. Признак актуальности: в снятом тексте присутствует **ч.15,
введённая ФЗ от 04.08.2023 № 417-ФЗ** (партнёрское финансирование) — последнее по времени
изменение статьи.
⬜ **Точные реквизиты редакции (номер и дата закона-редактора) на странице не публикуются —
НЕ ДОБЫТО**, требуется сверка с `pravo.gov.ru` перед использованием в юридическом документе.

**Полный текст — в приложении А в конце файла** (чтобы не разрывать логику раздела).
Здесь — разбор того, что применимо к FINPILOT.

#### 4.1.1. Части, применимые к нам, если в продукте появится реклама финуслуг

**ч.1 — обязательная идентификация поставщика услуги:**
> «Реклама банковских, страховых и иных финансовых услуг и финансовой деятельности должна
> содержать наименование или имя лица, оказывающего эти услуги или осуществляющего данную
> деятельность (для юридического лица - наименование, для индивидуального предпринимателя -
> фамилию, имя и (если имеется) отчество).»

**ч.2 п.1 — запрет обещаний доходности:**
> «Реклама... не должна: 1) содержать гарантии или обещания в будущем эффективности
> деятельности (доходности вложений), в том числе основанные на реальных показателях
> в прошлом, если такая эффективность деятельности (доходность вложений) не может быть
> определена на момент заключения соответствующего договора»

**🔴 ч.2 п.2 — правило «сказал одно условие — не умалчивай об остальных»:**
> «2) умалчивать об иных условиях оказания соответствующих услуг, влияющих на сумму доходов,
> которые получат воспользовавшиеся услугами лица, или на сумму расходов, которую понесут
> воспользовавшиеся услугами лица, **если в рекламе сообщается хотя бы одно из таких условий**.
> Положения настоящего пункта **не распространяются на рекламу услуг, связанных
> с предоставлением потребительского кредита (займа)**, пользованием им и погашением
> указанного кредита (займа).»

Это ключевая для нас норма общего режима: **триггер — упоминание хотя бы одного условия**.
Стоит показать ставку, срок или сумму — обязан раскрыть всё остальное, что влияет
на доходы/расходы. Для потребкредита этот пункт заменён специальным режимом ч.2.1 и ч.3.

**ч.2.1 — специальный режим потребкредита, предупреждение и ПСК:**
> «Если реклама услуг, связанных с предоставлением потребительского кредита (займа)...
> содержит хотя бы одно условие, влияющее на полную стоимость потребительского кредита
> (займа)... такая реклама должна соответствовать одному из следующих требований:
> 1) содержать предупреждение: **"Изучите все условия кредита (займа)"** с указанием на раздел
> официального сайта кредитора... В рекламе, распространяемой... другими способами, - **не менее
> чем пять процентов рекламной площади (рекламного пространства)**;
> 2) содержать все условия, влияющие на полную стоимость потребительского кредита (займа)...»

**ч.3 — приоритет ПСК над ставкой:**
> «Если реклама... содержит информацию о процентных ставках, в дополнение к требованиям
> части 2.1... должна содержать информацию о диапазонах значений **полной стоимости
> потребительского кредита (займа)**... с использованием слов "полная стоимость кредита
> (займа)". Указанная информация должна предоставляться **до** предоставления информации
> о процентных ставках и указываться шрифтом, размер которого **не менее** чем шрифт,
> которым отображается информация о процентных ставках.»

**ч.3.1 — безусловное предупреждение:**
> «Реклама услуг, связанных с предоставлением потребительского кредита (займа)... **должна
> содержать предупреждение: "Оценивайте свои финансовые возможности и риски"**... в рекламе,
> распространяемой другими способами, - не менее чем пять процентов рекламной площади».

Обратить внимание: ч.3.1 срабатывает **безусловно**, а не при упоминании условий.
ч.3.2 распространяет ч.2.1, 3 и 3.1 на ипотеку.

**🔴 ч.13 и ч.14 — запреты, которые касаются нас напрямую как площадки:**
> «13. Реклама услуг по предоставлению потребительских займов лицами, **не осуществляющими
> профессиональную деятельность по предоставлению потребительских займов** в соответствии
> с Федеральным законом от 21 декабря 2013 года N 353-ФЗ... **не допускается**.»
> «14. Если оказание банковских, страховых и иных финансовых услуг... может осуществляться
> только лицами, имеющими соответствующие лицензии, разрешения, аккредитации либо включенными
> в соответствующий реестр... **реклама указанных услуг или деятельности, оказываемых либо
> осуществляемой лицами, не соответствующими таким требованиям, не допускается**.»

То есть площадка обязана проверять статус рекламируемого кредитора. Разместил оффер
«серого» займодавца — нарушение.

#### 4.1.2. 🔴 Ст. 38 — кто отвечает. Самая практичная находка блока

Источник: `https://www.zakonrf.info/zoreklame/38/`, `curl`, **HTTP 200**.

> «**6. Рекламодатель** несет ответственность за нарушение требований, установленных... **статьями
> 28 - 30.2** настоящего Федерального закона.»
> «**7. Рекламораспространитель** несет ответственность за нарушение требований, установленных...
> **частями 1, 2.1, 3.1, 4, 7, 8, 11 и 13 статьи 28**... настоящего Федерального закона.»

**🔴 Разбор, который надо запомнить.** Рекламодатель отвечает за **всю** ст. 28.
Рекламораспространитель — только за перечисленный список. **Частей 2, 3, 5 и 14 в списке
рекламораспространителя НЕТ.**

Практический смысл для FINPILOT, если он когда-либо станет площадкой (наш вывод, не норма):
- за содержательные умолчания об условиях (ч.2), за неверный показ ПСК против ставки (ч.3)
  и за рекламу услуг лица без лицензии (ч.14) **отвечает банк-рекламодатель, не мы**;
- но **на нас лично** ложатся: ч.1 (назвать поставщика), **ч.2.1 (предупреждение «Изучите все
  условия кредита (займа)» и 5 % площади)**, **ч.3.1 (предупреждение «Оценивайте свои
  финансовые возможности и риски»)**, ч.13 (не размещать рекламу займов непрофессиональных
  займодавцев). Это требования к **вёрстке и к проверке контрагента**, то есть инженерная
  и комплаенс-работа, которую нельзя переложить на партнёра договором.
- Ответственность: ст. 38 ч.4 — «...влечет за собой ответственность в соответствии
  с законодательством Российской Федерации об административных правонарушениях».
  ч.8: рекламопроизводитель отвечает, «если будет доказано, что нарушение произошло по его вине».

#### 4.1.3. Ст. 5 ч.7 и ч.7.1 — общий режим существенной информации

Источник: `https://www.zakonrf.info/zoreklame/5/`, `curl`, **HTTP 200**.
> «7. Не допускается реклама, в которой **отсутствует часть существенной информации**
> о рекламируемом товаре, об условиях его приобретения или использования, **если при этом
> искажается смысл информации и вводятся в заблуждение потребители рекламы**.»
> «7.1. В рекламе товаров и иных объектов рекламирования **стоимостные показатели должны быть
> указаны в рублях**, а в случае необходимости дополнительно могут быть указаны в иностранной
> валюте.»

И норма, прямо релевантная теме «реклама рядом с рекомендацией»:
> «9. Не допускаются... распространение **скрытой рекламы**, то есть рекламы, которая оказывает
> **не осознаваемое потребителями рекламы воздействие на их сознание**, в том числе такое
> воздействие путем использования специальных видеовставок (двойной звукозаписи)
> и иными способами.»

⚠️ **Важное ограничение, которое надо назвать честно:** легальное определение «скрытой рекламы»
в ч.9 **узкое** — оно про неосознаваемое воздействие (25-й кадр и подобное), а **не** про
«рекламу, замаскированную под аналитику». То есть цитата ЦБ РФ про «скрытую рекламу»
в сервисах финздоровья (§4.0) использует это словосочетание **в бытовом, а не в легальном
смысле**. Ссылаться на ст. 5 ч.9 как на запрет партнёрских офферов внутри PFM **нельзя** —
это была бы натяжка. Реальный правовой инструмент здесь — ст. 18.1 ч.16 (пометка «реклама»),
см. §4.4.

**ч.7.1 — прямое требование к нашему интерфейсу** независимо от рекламы: если в продукте
показывается цена, она в рублях. Согласуется с правилом 6 CLAUDE.md проекта (знак рубля
после числа через неразрывный пробел).

### 4.2. Статус для лидогенерации

**Прямой ответ: обязательного статуса для получения вознаграждения от банка за приведённого
клиента в российском праве НЕ ОБНАРУЖЕНО, при условии что сделка не заключается внутри
продукта. Граница, установленная темой 21, подтверждена и уточнена.**

#### 4.2.1. 211-ФЗ — статус возникает по факту включения в реестр, а не по признакам

Источник: ФЗ от 20.07.2020 № 211-ФЗ, `https://legalacts.ru/doc/federalnyi-zakon-ot-20072020-n-211-fz-o-sovershenii-finansovykh/`,
`curl`, **HTTP 200**, шапка документа: **«(ред. от 27.10.2025)»**. 🟩
(`consultant.ru` дал HTTP 200, но вместо текста — заглушку «доступен по расписанию»
некоммерческой версии; текст снят с legalacts.)

> **Статья 11. Статус оператора финансовой платформы**
> «1. Юридическое лицо **приобретает статус оператора финансовой платформы со дня включения
> Банком России сведений о нем в реестр операторов финансовых платформ.**»

> **Статья 1, ч.2:**
> «Требования настоящего Федерального закона **не распространяются** на деятельность
> по оказанию услуг, связанных с обеспечением возможности совершения сделок, осуществляемую
> лицами, **которые не были включены Банком России в реестр операторов финансовых платформ**.»

> **Статья 2, п.1:** «финансовая платформа - информационная система, которая обеспечивает
> взаимодействие финансовых организаций или эмитентов с получателями финансовых услуг...
> **в целях обеспечения возможности совершения финансовых сделок** и доступ к которой
> предоставляется оператором финансовой платформы»
> **п.7:** «финансовые сделки - совершаемые между финансовыми организациями или эмитентами
> и получателями финансовых услуг **с использованием финансовой платформы** сделки...»

**🔴 Разбор.** Конструкция закона **разрешительная, а не признаковая**: статус не «наступает»
от того, что ты делаешь нечто похожее — он **приобретается** со дня включения в реестр,
а на не включённых требования закона прямо не распространяются (ст. 1 ч.2). Ключевой признак
самой платформы — сделка совершается **с использованием финансовой платформы**, то есть
внутри неё. **Вознаграждение без заключения сделки внутри продукта этот признак не образует.**
Это и есть ответ на вопрос задания: **получение вознаграждения БЕЗ заключения сделки внутри
продукта статус оператора финплатформы не создаёт.**

Порог входа в этот статус, для понимания масштаба (ст. 8): 🟩
> «1. Минимальный размер собственных средств оператора финансовой платформы должен составлять
> **100 миллионов рублей**.»
> «2. Оператор финансовой платформы **не вправе совмещать свою деятельность с деятельностью
> кредитной организации и бюро кредитных историй**...»
Плюс организационно-правовая форма — **только акционерное общество** (ст. 2 п.2).
То есть это тяжёлый регулируемый статус, а не формальность; попасть в него случайно нельзя,
но и получить «на всякий случай» невозможно.

#### 4.2.2. 🔴 Кредитный брокер — понятия в российском праве НЕТ

Источник: ФЗ от 21.12.2013 № 353-ФЗ «О потребительском кредите (займе)»,
`https://legalacts.ru/doc/federalnyi-zakon-ot-21122013-n-353-fz-o/`, `curl`, **HTTP 200**,
шапка **«(ред. от 04.08.2026)»**. 🟩

**Полнотекстовый поиск по всему закону (386 КБ) по строке «брокер» даёт ЕДИНСТВЕННОЕ
вхождение, и оно не о кредитном брокере** — это исключение из определения профессиональной
деятельности по предоставлению потребительских займов:
> «...займов, предоставляемых **брокером клиенту для совершения сделок купли-продажи ценных
> бумаг**...» (ст. 3, п.5)

**Вывод (воспроизводимый механически):** понятия «кредитный брокер», требований к нему,
лицензирования или реестра **в тексте 353-ФЗ действующей редакции нет**.

Смежное, дословно:
> **Статья 4.** «Профессиональная деятельность по предоставлению потребительских займов
> осуществляется **кредитными организациями, а также некредитными финансовыми организациями**
> в случаях, определенных федеральными законами об их деятельности.»

То есть регулируется **выдача** займа, а не приведение клиента к тому, кто выдаёт.
🔴 Это подтверждает: **лидогенерация как таковая в РФ не лицензируется**. Ограничения
на неё приходят не из банковского права, а из **рекламного** (ст. 28 и ст. 18.1
ФЗ «О рекламе», §4.1 и §4.4) и из **налогового** (§4.3.3, потеря льготы по НДС).

#### 4.2.3. Поправка к брифу: ст. 13.1 ФЗ № 395-1 утратила силу

Задание отсылало к ст. 13.1 ФЗ «О банках и банковской деятельности» (банковский платёжный
агент). Источник `https://www.zakonrf.info/zakon-o-bankah/13.1/`, `curl`, **HTTP 200**,
текст статьи целиком: 🟩
> «**Статья 13.1. Утратила силу. - Федеральный закон от 27.06.2011 N 162-ФЗ**»

Институт банковского платёжного агента с 2011 года живёт в **ФЗ от 27.06.2011 № 161-ФЗ
«О национальной платёжной системе»**. Косвенное подтверждение из добытого в этой же теме
текста 54-ФЗ (ст. 4.7): там банковский платёжный агент упоминается «при осуществлении
деятельности в соответствии с Федеральным законом от 27 июня 2011 года N 161-ФЗ».
🟥 **Текст ст. 14 ФЗ № 161-ФЗ не добыт** (legalacts по угаданному URL → **404**).
Впрочем, к нашей задаче он и не относится: платёжный агент — про приём платежей
в пользу банка, а не про рекомендацию продукта.

#### 4.2.4. Позиция ЦБ: разъяснения именно про лидогенерацию не найдено, но найдено смежное и очень близкое

🟥 Информационного письма Банка России ровно про лидогенерацию / партнёрское вознаграждение /
«сервисы финансового здоровья» **не обнаружено** (поиск по `cbr.ru` результатов по предмету
не дал).

Зато добыт **действующий регуляторный сигнал по механически близкому предмету** — подталкивание
пользователя к конкретному продукту внутри дистанционного канала:

**Банк России. «О геймификации, наджинге и иных практиках вовлечения потребителей на рынке
инвестиционных услуг». Доклад для общественных консультаций, 2026.**
https://cbr.ru/Content/Document/File/194058/Consultation_Paper_14072026_59.pdf
Канал `curl`, **HTTP 200**, 759 721 байт, текст извлечён `pdftotext`.
🔴 **Статус: доклад для консультаций, НЕ нормативный акт и НЕ разъяснение.** Цитируется
как позиция регулятора, не как норма. Дословно:

> «Когда организация использует подталкивания, чтобы повлиять на поведение клиентов, например,
> с помощью **всплывающих окон в приложении**, возникает вопрос, может ли такой тип
> подталкивания к сделке с конкретным инструментом восприниматься как персонализированное
> общение или **персонализированная рекомендация** клиенту.»
> «**ESMA считает, что когда клиент получает всплывающее сообщение, электронное письмо
> или другой тип сообщения, которое подталкивает его к совершению сделки с конкретным
> финансовым инструментом, то это сообщение стоит рассматривать как индивидуальную
> инвестиционную рекомендацию.** Поэтому организация должна проводить оценку соответствия
> инструмента профилю клиента.»
> «В настоящее время регулирование "темных паттернов" и геймификации при предоставлении
> потребителям финансовых продуктов (дополнительных услуг) в дистанционных каналах находится
> **в плоскости рекомендаций** (Методических рекомендаций № 22-МР и Методических
> рекомендаций № 1-МР).»

Реквизиты упомянутых рекомендаций (сноски доклада, дословно): 🟩
> «Методические рекомендации Банка России **от 27.12.2024 № 22-МР** по предоставлению
> потребителям финансовых продуктов (дополнительных услуг) в дистанционных каналах»
> «Методические рекомендации Банка России **от 20.01.2025 № 1-МР** по применению основных
> принципов добросовестного поведения на финансовом рынке»
🟥 Тексты 22-МР и 1-МР не добыты (бюджет). **Это первая цель следующего захода по теме.**

**🔴 Почему это важнее, чем кажется, и как стыкуется с темами 18–19.**
Регуляторный вывод тем 18–19 был: FINPILOT под лицензирование инвестсоветника не попадает,
и защита **предметная** — мы не называем финансовый инструмент. Доклад ЦБ **подтверждает
именно этот механизм с противоположной стороны**: линию проводят по признаку «подталкивание
к сделке **с конкретным финансовым инструментом**». То есть наш щит — не дисклеймер и не
формулировка, а **отсутствие названного инструмента в выдаче**. Как только в продукте
появляется партнёрский оффер конкретного банка рядом с расчётом, этот щит исчезает
не по нашему решению, а по признаку, который регулятор уже описал.
Это самый сильный правовой аргумент против лидогенерации внутри FINPILOT — сильнее,
чем цитата про независимость из §4.0, потому что он опирается на описанный механизм,
а не на пожелание.

### 4.3. Подписка на ПО для физлиц (оферта, 54-ФЗ, НДС, реестр ПО, ЗоЗПП)

#### 4.3.1. Оферта: правильная конструкция — не «договор оказания услуг», а лицензионный договор в упрощённом порядке

Источники — `zakonrf.info/gk/435|437|438|1286`, `curl`, все **HTTP 200**,
пометка «(действующая редакция)». 🟩

> **Ст. 437 ГК РФ, п.2:** «Содержащее **все существенные условия договора** предложение,
> из которого усматривается воля лица, делающего предложение, заключить договор на указанных
> в предложении условиях **с любым, кто отзовется**, признается офертой (публичная оферта).»
> **п.1:** «Реклама и иные предложения, адресованные неопределенному кругу лиц, рассматриваются
> как **приглашение делать оферты**, если иное прямо не указано в предложении.»

> **Ст. 438 ГК РФ, п.3:** «Совершение лицом, получившим оферту, в срок, установленный для ее
> акцепта, **действий по выполнению указанных в ней условий договора** (отгрузка товаров,
> предоставление услуг, выполнение работ, **уплата соответствующей суммы** и т.п.) считается
> акцептом...»
> **п.2:** «**Молчание не является акцептом**, если иное не вытекает из закона, соглашения
> сторон, обычая или из прежних деловых отношений сторон.»

**🔴 Ст. 1286 ГК РФ, п.5 — ключевая для нас конструкция:**
> «Лицензионный договор с пользователем о предоставлении ему простой (неисключительной)
> лицензии на использование программы для ЭВМ или базы данных **может быть заключен
> в упрощенном порядке**.
> Лицензионный договор, заключаемый в упрощенном порядке, является **договором присоединения**,
> условия которого... могут быть изложены... **в электронном виде** (пункт 2 статьи 434).
> **Начало использования программы для ЭВМ... пользователем, как оно определяется указанными
> условиями, означает его согласие на заключение договора. В этом случае письменная форма
> договора считается соблюденной.**
> Лицензионный договор, заключаемый в упрощенном порядке, **является безвозмездным, если
> договором не предусмотрено иное**.»

**Три практических следствия (наш разбор, не норма):**
1. Для FINPILOT правильная рамка — **лицензионный договор в упрощённом порядке**, а не договор
   возмездного оказания услуг. Это и даёт основание для льготы по НДС (§4.3.3), и упрощает
   форму заключения.
2. 🔴 **Последний абзац п.5 — ловушка:** упрощённая лицензия **по умолчанию безвозмездна**.
   Возмездность и размер вознаграждения должны быть в тексте прописаны прямо, иначе
   договор считается безвозмездным. Это ошибка, которую легко допустить, копируя чужой EULA.
3. Формулировка «начало использования означает согласие» требует, чтобы в оферте **было
   определено, что считается началом использования** (регистрация? первый вход? нажатие
   кнопки?) — иначе момент заключения договора неопределён. Ст. 438 п.2 прямо говорит,
   что молчание акцептом не является.

#### 4.3.2. 54-ФЗ: чек обязателен, но для подписки есть облегчающая норма

Источники — `zakonrf.info/zakon-o-kkt/1.2` и `/4.7`, `curl`, **HTTP 200**. 🟩

> **Ст. 1.2, п.1:** «Контрольно-кассовая техника... применяется на территории Российской
> Федерации **в обязательном порядке всеми организациями и индивидуальными предпринимателями
> при осуществлении ими расчетов**, за исключением случаев, установленных настоящим
> Федеральным законом.»

> **🔴 Ст. 1.2, п.5** (это наш случай — интернет-эквайринг без личного взаимодействия):
> «Пользователи при осуществлении расчетов в безналичном порядке, исключающих возможность
> непосредственного взаимодействия покупателя (клиента) с пользователем... с применением
> устройств, подключенных к сети "Интернет"... **обязаны обеспечить передачу покупателю
> (клиенту) кассового чека или бланка строгой отчетности в электронной форме на абонентский
> номер либо адрес электронной почты, указанные покупателем (клиентом) до совершения
> расчетов. При этом кассовый чек... на бумажном носителе пользователем может не печататься.**»

> **п.5.3** (для расчётов вне п.5 и 5.1): «...обязаны **сформировать кассовый чек... не позднее
> рабочего дня, следующего за днем осуществления расчета**...»

> **п.2.2:** «Действие положений... об обязанности пользователя применять контрольно-кассовую
> технику при осуществлении расчетов в безналичном порядке с предъявлением электронного
> средства платежа распространяется в том числе на расчеты путем перевода денежных средств
> **с использованием сервиса быстрых платежей платежной системы Банка России**...»

**🔴 Ст. 1.2, п.2.1 — норма, которая прямо облегчает жизнь подписочному сервису:**
> «При осуществлении расчетов в виде зачета или возврата предварительной оплаты и (или)
> авансов, ранее внесенных физическими лицами за... **услуги в электронной форме,
> определенные статьей 174.2 Налогового кодекса Российской Федерации**... пользователем
> **может быть сформирован ОДИН кассовый чек... содержащий сведения о всех таких расчетах,
> совершенных за расчетный период, не превышающий календарного месяца**... (но не позднее
> десяти календарных дней, следующих за днем окончания расчетного периода), **без выдачи
> (направления) кассового чека... клиенту**.»

То есть при подписочной модели с авансами возможен **сводный месячный чек** вместо чека
на каждое списание — при условии квалификации как «услуги в электронной форме» по ст. 174.2 НК.
🟥 Соотношение этой квалификации с лицензионной конструкцией §4.3.1 в рамках темы **не
проработано** — это вопрос к налоговому консультанту, а не к исследованию.

**Ст. 4.7 — обязательные реквизиты чека** приведены в приложении Б. Из специфичного для нас:
> «...**при расчете в сети "Интернет" - адрес сайта пользователя**»
> «...наименование товаров, работ, услуг **(если объем и список услуг возможно определить
> в момент оплаты)**, платежа, выплаты, их количество, цена (в валюте Российской Федерации)
> за единицу... **с указанием ставки налога на добавленную стоимость** (за исключением случаев
> осуществления расчетов пользователями, не являющимися налогоплательщиками налога
> на добавленную стоимость или освобожденными от исполнения обязанностей налогоплательщика...,
> а также осуществления расчетов за товары, работы, услуги, **не подлежащие налогообложению
> (освобождаемые от налогообложения)** налогом на добавленную стоимость)»

#### 4.3.3. 🔴 НДС и реестр отечественного ПО — САМАЯ ВАЖНАЯ НАХОДКА ВСЕГО УЧАСТКА 4

Источник: НК РФ, ст. 149 п.2 пп.26, `https://www.zakonrf.info/nk/149/`, `curl`, **HTTP 200**,
«действующая редакция». 🟩 Дословно:

> «26) **исключительных прав на программы для электронных вычислительных машин и базы данных,
> включенные в единый реестр российских программ для электронных вычислительных машин и баз
> данных**... **прав на использование таких программ и баз данных (включая обновления к ним
> и дополнительные функциональные возможности), в том числе путем предоставления удаленного
> доступа к ним через информационно-телекоммуникационную сеть, в том числе через
> информационно-телекоммуникационную сеть "Интернет"**.
>
> **Положения настоящего подпункта НЕ ПРИМЕНЯЮТСЯ, если передаваемые права состоят
> в получении возможности распространять рекламную информацию в информационно-
> телекоммуникационной сети, в том числе в информационно-телекоммуникационной сети "Интернет",
> и (или) получать доступ к такой информации, размещать предложения (объявления)
> о приобретении (реализации) товаров (работ, услуг), имущественных прав в информационно-
> телекоммуникационной сети... ОСУЩЕСТВЛЯТЬ ПОИСК ИНФОРМАЦИИ О ПОТЕНЦИАЛЬНЫХ ПОКУПАТЕЛЯХ
> (ПРОДАВЦАХ) И (ИЛИ) ЗАКЛЮЧАТЬ СДЕЛКИ;**»

**🔴 Это делает выбор модели монетизации ИЗМЕРИМЫМ В ДЕНЬГАХ, а не только этическим.**

Разбор (наш вывод из дословной нормы):
- **Чистая подписка на ПО из реестра → освобождение от НДС.** Первый абзац покрывает ровно
  нашу конструкцию: право использования, предоставляемое удалённым доступом через Интернет,
  включая обновления и дополнительные функциональные возможности (то есть платные тарифы).
- **Добавление рекламы или лидогенерации → льгота ТЕРЯЕТСЯ.** Второй абзац исключает
  из-под льготы права, состоящие в возможности «распространять рекламную информацию»
  и «**осуществлять поиск информации о потенциальных покупателях (продавцах)**» —
  последнее является буквальным описанием лидогенерации.
- 🔵 **Цена вопроса, арифметика:** ставка НДС в РФ — 20 %. Отказ от лидогенерации в пользу
  чистой подписки **не только снимает конфликт с позицией ЦБ (§4.0) и с признаком
  «подталкивание к конкретному инструменту» (§4.2.4), но и сохраняет ~20 % выручки**.
  То есть модель, которая казалась «отказом от денег ради принципа», при попадании в реестр
  оказывается ещё и налогово выгоднее. **Это главный практический вывод правового участка.**
- ⚠️ Оговорка, которую нельзя пропустить: льгота **обусловлена включением в реестр**.
  Без реестра — НДС на общих основаниях. Требования к включению — ниже.

**Постановление Правительства РФ от 16.11.2015 № 1236.**
Источник: `https://legalacts.ru/doc/postanovlenie-pravitelstva-rf-ot-16112015-n-1236/`,
`curl`, **HTTP 200**, шапка **«(ред. от 13.08.2026)»**. 🟩
Требования п.5, применимые к нам (сокращённо; полный текст — приложение В):
> «а) исключительное право на программное обеспечение на территории всего мира и на весь срок
> действия исключительного права принадлежит одному либо нескольким из следующих лиц
> (правообладателей): ... российской коммерческой организации, которая... находится под
> контролем Российской Федерации... и (или) **гражданина Российской Федерации**...;
> **гражданину Российской Федерации**;»
> «б) программное обеспечение **правомерно введено в гражданский оборот** на территории
> Российской Федерации, экземпляры... либо права использования... свободно реализуются
> на всей территории Российской Федерации...»
> «в) общая сумма выплат по лицензионным и иным договорам... в пользу иностранных
> юридических лиц и (или) физических лиц... составляет **менее 30 процентов выручки**,
> полученной правообладателем... за истекший календарный год...»
> «ж) программное обеспечение **не имеет принудительного обновления и управления из-за рубежа**;»
> «з) гарантийное обслуживание, техническая поддержка и модернизация... осуществляются
> российской коммерческой или некоммерческой организацией без преобладающего иностранного
> участия **либо гражданином Российской Федерации**;»
> «и) технические средства хранения исходного текста и объектного кода... а также технические
> средства компиляции... **находятся на территории Российской Федерации**;»
> «к) технические средства, необходимые для активации, выпуска, распространения, управления
> лицензионными ключами... находятся на территории Российской Федерации...;»
> «л) **графический пользовательский интерфейс программного обеспечения реализован
> на русском языке**;»
> «м) программное обеспечение **совместимо не менее чем с 2 операционными системами,
> соответствующими требованиям к доверенному программному обеспечению**...»

🔵 **Оценка выполнимости для FINPILOT (наша, требует проверки юристом):** пп. «а», «б», «в»,
«ж», «з», «и», «к», «л» — выполнимы силами владельца-гражданина РФ без изменения архитектуры.
🔴 **Пункт «м» — единственное реальное препятствие**: требуется совместимость не менее чем
с двумя доверенными ОС. Для веб-приложения его толкование неочевидно (совместимость
серверной части? браузера?), и это **вопрос, который надо задать до подачи заявления,
а не после**. Пункт «в» (менее 30 % выручки в пользу иностранных лиц) отдельно стоит
проверить против расходов на иностранные облачные сервисы и библиотеки.

#### 4.3.4. Возвраты по ЗоЗПП

Источники — `zakonrf.info/zozpp/32` и `/26.1`, `curl`, **HTTP 200**. 🟩

> **Ст. 32. Право потребителя на отказ от исполнения договора о выполнении работ (оказании
> услуг).** «Потребитель вправе отказаться от исполнения договора о выполнении работ (оказании
> услуг) **в любое время при условии оплаты исполнителю фактически понесенных им расходов**,
> связанных с исполнением обязательств по данному договору.»

> **Ст. 26.1 «Дистанционный способ продажи ТОВАРА», п.4:** «Потребитель вправе отказаться
> от **товара** в любое время до его передачи, а после передачи товара - **в течение семи
> дней**. В случае, если информация о порядке и сроках возврата товара надлежащего качества
> не была предоставлена в письменной форме в момент доставки товара, потребитель вправе
> отказаться от товара **в течение трех месяцев**...»

**🔴 Разбор — здесь важно, чего в нормах НЕТ.**
- **Ст. 26.1 говорит о ТОВАРЕ**, а не об услуге и не о лицензии. К подписке на ПО она
  напрямую не применяется. Правило «семь дней на возврат» к нашей модели **не переносится
  автоматически** — распространённое заблуждение.
- **Ст. 32 применяется к работам/услугам** и даёт потребителю право отказаться **в любое
  время**, возместив исполнителю **фактически понесённые расходы**. Для SaaS с почти нулевой
  предельной себестоимостью это означает: **при отказе в середине оплаченного периода
  «фактически понесённые расходы» стремятся к нулю, и деньги за неиспользованный период,
  скорее всего, придётся вернуть**. Оферта не может это право отменить.
- 🔵 **Отсюда — практическое проектное следствие**, стыкующееся с кладбищем: Playbook при
  закрытии **вернул деньги за неиспользованную часть**, Moneyhub — **доработал оплаченные
  подписки до истечения** (§2.3). Обе процедуры совместимы со ст. 32; вторая дешевле
  и мягче. В оферте FINPILOT стоит предусмотреть обе и назвать порядок возврата явно.
- ⚠️ Если конструкция договора — **лицензионная** (ст. 1286 п.5), а не «оказание услуг»,
  применимость ст. 32 напрямую становится спорной. **Это противоречие между налоговой
  оптимальностью (лицензия → льгота по НДС) и потребительской квалификацией** надо разрешать
  с юристом; исследование его фиксирует, но не решает.
- 🟥 **Позиция Роспотребнадзора и судебная практика конкретно по возврату за неиспользованный
  период подписки на ПО — НЕ ДОБЫТЫ** (бюджет темы исчерпан на текстах норм).

### 4.4. Реклама внутри продукта

#### 4.4.1. Что вообще считается рекламой — ст. 3 ФЗ «О рекламе»

Источник: `https://www.zakonrf.info/zoreklame/3/`, `curl`, **HTTP 200**. 🟩
> «1) **реклама** - информация, распространенная любым способом, в любой форме и с использованием
> любых средств, **адресованная неопределенному кругу лиц** и направленная на привлечение
> внимания к объекту рекламирования, формирование или поддержание интереса к нему
> и его продвижение на рынке;»
> «2) **объект рекламирования** - товар, средства индивидуализации юридического лица и (или)
> товара, изготовитель или продавец товара, результаты интеллектуальной деятельности либо
> мероприятие..., на привлечение внимания к которым направлена реклама;»
> «5) **рекламодатель** - изготовитель или продавец товара либо иное определившее объект
> рекламирования и (или) содержание рекламы лицо;»
> «7) **рекламораспространитель** - лицо, осуществляющее распространение рекламы любым
> способом, в любой форме и с использованием любых средств;»

**🔴 Признак «адресованная неопределённому кругу лиц» — и почему он нас НЕ спасает.**
Возникает соблазн рассуждать так: наш оффер персонализирован под конкретного пользователя,
значит круг лиц определён, значит это не реклама. Так рассуждать нельзя, и вот почему:
если персонализация выводит сообщение из-под режима рекламы, оно **попадает под режим
индивидуальной рекомендации** — ровно по механизму, который ЦБ описал в докладе о наджинге
(§4.2.4, позиция ESMA про всплывающее сообщение о конкретном инструменте). **Обе двери ведут
в регулируемое помещение**: либо реклама с маркировкой и требованиями ст. 28, либо
персональная рекомендация с оценкой соответствия профилю клиента. Третьего варианта
для партнёрского оффера внутри финансового приложения из добытых источников не просматривается.

#### 4.4.2. Маркировка интернет-рекламы — ст. 18.1 и erid

Источник: `https://www.zakonrf.info/zoreklame/18.1/`, `curl`, **HTTP 200**.
Заголовок статьи: «Реклама и социальная реклама в информационно-телекоммуникационной сети
"Интернет"». 🟩

> «**16. Реклама, распространяемая в информационно-телекоммуникационной сети "Интернет"**,
> за исключением рекламы, размещенной в телепрограммах и телепередачах, радиопрограммах
> и радиопередачах..., **должна содержать пометку "реклама", а также указание на рекламодателя
> такой рекламы и (или) сайт, страницу сайта... содержащие информацию о рекламодателе такой
> рекламы.**»

> «**17. Распространение рекламы... допускается при условии присвоения оператором рекламных
> данных соответствующей рекламе идентификатора рекламы**..., которые представляют собой
> уникальное цифровое обозначение, предназначенное для обеспечения **прослеживаемости**
> распространенных... рекламы... и учета информации о таких рекламе...»

> «3. Рекламодатели, рекламораспространители, операторы рекламных систем... разместившие
> в информационно-телекоммуникационной сети "Интернет" рекламу..., направленные на привлечение
> внимания потребителей рекламы..., находящихся на территории Российской Федерации,
> и соответствующие критериям, определенным Правительством Российской Федерации, **обязаны
> предоставлять информацию... в федеральный орган исполнительной власти, осуществляющий
> функции по контролю и надзору в сфере средств массовой информации**...»
> «5. ...обязаны предоставлять информацию... **через... оператора рекламных данных**.»
> «13. Информация... подлежит хранению... **не менее пяти лет** со дня ее получения...»

**Санкции — КоАП РФ ст. 14.3** (`https://www.zakonrf.info/koap/14.3/`, `curl`, **HTTP 200**,
«действующая редакция»): 🟩
> «**15.** Неисполнение рекламодателем, рекламораспространителем, оператором рекламной системы
> обязанности по предоставлению информации... о распространенной... рекламе... либо нарушение
> установленных сроков..., либо предоставление... неполной, недостоверной, неактуальной
> информации - влечет наложение административного штрафа на граждан в размере
> **от десяти тысяч до тридцати тысяч рублей**; на должностных лиц - **от тридцати тысяч
> до ста тысяч рублей**; на юридических лиц - **от двухсот тысяч до пятисот тысяч рублей**.»
> «**16.** Распространение рекламы... **без присвоенного оператором рекламных данных...
> идентификатора рекламы** либо нарушение требований к его размещению - влечет наложение
> административного штрафа на граждан... **от тридцати тысяч до ста тысяч рублей**;
> на должностных лиц - **от ста тысяч до двухсот тысяч рублей**; на юридических лиц -
> **от двухсот тысяч до пятисот тысяч рублей**.»
> «**17.** [для операторов рекламных данных] ...на должностных лиц - от ста тысяч
> до двухсот тысяч рублей; на юридических лиц - **от трехсот тысяч до семисот тысяч рублей**.»

🟥 **Не добыты:** постановление Правительства РФ с критериями интернет-рекламы, подлежащей
учёту (к ст. 18.1 ч.3), и приказ Роскомнадзора с требованиями к идентификатору erid.
Без них нельзя точно сказать, под какие именно размещения подпадает наш случай.

#### 4.4.3. Отделение рекламы от аналитического контента — прямой нормы НЕТ

🔴 **Честный отрицательный результат.** Прямой нормы, требующей отделять рекламу
от редакционного/аналитического контента **в цифровых сервисах**, в добытых текстах
**не обнаружено**. Есть только:
- **ст. 18.1 ч.16** — пометка «реклама» и указание на рекламодателя (это и есть фактический
  механизм отделения в интернете);
- **ст. 5 ч.9** — запрет скрытой рекламы, но с **узким легальным определением**
  (неосознаваемое воздействие), которое к «рекламе, замаскированной под аналитику»
  напрямую не применяется (см. оговорку в §4.1.3);
- аналог правила «на правах рекламы» из ст. 16 существует **для периодических печатных
  изданий**, а не для цифровых сервисов.

**Вывод:** запрета ставить партнёрский оффер рядом с финансовой рекомендацией в российском
праве прямо нет. Есть обязанность его **пометить** («реклама» + erid + рекламодатель)
и есть требования ст. 28 к содержанию. **То есть это законно, но видно пользователю** —
что и является настоящим ограничением для продукта, обещающего независимость.
Запрет здесь не правовой, а **позиционный**: см. §4.0 (позиция ЦБ) и §4.2.4 (признак
подталкивания к конкретному инструменту).

---

### 4.5. 🔴 Сводка участка 4: что можно, чего нельзя и что это стоит

| Модель монетизации | Законна в РФ? | Чем регулируется | Цена и последствия |
|---|---|---|---|
| **Подписка на ПО (лицензия)** | ✅ Да | ГК ст. 1286 п.5 (упрощённая лицензия), 54-ФЗ ст. 1.2 п.5 (электронный чек), ЗоЗПП ст. 32 (отказ в любое время) | Требует: оферта с явной возмездностью; электронный чек на e-mail/телефон; порядок возврата. **При включении в реестр ПО — освобождение от НДС (НК ст. 149 п.2 пп.26)** |
| **Партнёрское вознаграждение от банка (лидогенерация), сделка вне продукта** | ⚠️ Да, статус не требуется, **но дорого** | Статус оператора финплатформы **не возникает** (211-ФЗ ст. 1 ч.2, ст. 11 ч.1); «кредитный брокер» в 353-ФЗ **отсутствует** | 🔴 **Теряется льгота по НДС** — НК ст. 149 п.2 пп.26, второй абзац прямо исключает «поиск информации о потенциальных покупателях». Плюс требования ст. 28 и маркировка ст. 18.1. Плюс конфликт с §4.0 и §4.2.4 |
| **Реклама внутри продукта** | ⚠️ Да, но с обязательствами | ФЗ «О рекламе» ст. 28 (содержание), ст. 18.1 ч.16–17 (пометка «реклама» + erid), ст. 38 ч.7 (наша ответственность как распространителя) | Штрафы КоАП ст. 14.3 ч.15–16: **до 500 тыс. руб. на юрлицо** за отсутствие erid или непередачу данных. 🔴 **Та же потеря льготы по НДС.** На нас лично — ч.1, 2.1, 3.1, 13 ст. 28 |
| **Сделка внутри продукта (маркетплейс)** | ❌ Требует статуса | 211-ФЗ | **Собственные средства ≥ 100 млн руб., только АО, реестр ЦБ** (ст. 8, ст. 2 п.2). Для FINPILOT недостижимо и не нужно |
| **Выдача денег (модель Tally)** | ❌ Другой бизнес | 353-ФЗ ст. 4 — только кредитные и некредитные финорганизации | Лицензия, капитал, кредитный риск. Именно на этом умер ближайший аналог (§2.1) |

**🔴 Главный вывод участка 4, в одну строку.**
Лидогенерация в РФ **не запрещена и не лицензируется** — вопреки ожиданию, юридического
барьера тут нет. Барьер оказался **налоговым и позиционным**: партнёрская модель стоит
FINPILOT **освобождения от НДС по НК ст. 149 п.2 пп.26** (~20 % выручки), плюс маркировки
и ответственности по ст. 28/18.1, плюс прямого противоречия с позицией ЦБ (§4.0) и с уже
описанным регулятором признаком «подталкивание к сделке с конкретным инструментом» (§4.2.4),
который в темах 18–19 был опознан как наш единственный щит от статуса инвестсоветника.
**Чистая подписка — единственная модель, которая не платит ни одну из этих цен, и при этом
она же налогово выгоднее.** Отказ от продавца в контуре перестаёт быть жертвой ради принципа
и становится расчётом.

---

## Прямые ответы

### (а) На чём реально живут PFM-продукты и какая модель выживает дольше

**Живут на двух моделях, и они принципиально разные по устройству.**

**1. Лидогенерация — модель большой выручки и плохой экономики удержания.**
Credit Karma: **$2 263 млн выручки, 37 % операционной маржи** (🟩 10-K INTU FY2025).
NerdWallet: **$836.6 млн** (🟩 10-K NRDS FY2025). Обе — 100 % плата партнёров за действие,
клик или лид; ни одна не берёт денег с пользователя. Но:
- у NerdWallet **67–70 % выручки три года подряд уходит в sales & marketing**, операционная
  маржа была **1 % в 2023 и 2024**, стала 8 % только в 2025 (🟩 10-K, «as a percentage of
  revenue»). Это бизнес перепродажи трафика, а не удержания;
- канал разрушается на глазах: кредитно-карточная выручка NerdWallet **$209.7 → $176.4 →
  $133.4 млн** за три года, −36 %, и эмитент называет причину дословно: "**continued pressures
  in organic search traffic**" (🟩 10-K NRDS FY2025);
- модель тянет за собой регулируемый статус: NerdWallet держит внутри **ипотечного брокера
  (Next Door Lending, LLC)** и **зарегистрированного инвестсоветника (NerdWallet Advisory LLC)**
  (🟩 10-K, Item 1).

**2. Подписка — модель меньшей выручки и лучшей устойчивости, и она РЕАЛЬНО РАБОТАЕТ
в масштабе.** Главное опровержение расхожего «PFM невозможен без комиссий»:
**Rocket Money — $390 млн выручки за FY2025, из которых $351 млн (90 %) — чистая абонентская
плата, при 4 583 тыс. платящих подписчиков** (🟩 10-K RKT FY2025). ARPU ≈ **$80.7/год**
(🔵 наш расчёт). То есть подписочный PFM промышленного размера существует и измерим.
Оговорки, без которых цифру нельзя переносить: (1) Rocket Money живёт внутри ипотечной
группы и часть CAC оплачена общегрупповым маркетингом; (2) **чистые приросты подписчиков
упали в 2.36 раза** — +1 099 тыс. в 2024 против +466 тыс. в 2025, и всплеск 2024 совпадает
с отключением Mint 23.03.2024, то есть был разовым подбором чужой базы (🔵 расчёт из 🟩 данных).

**3. Что выживает дольше — B2B.** Единственный измеримый контур с раскрытым удержанием:
Q2 Holdings, **контракты в среднем свыше пяти лет, годовой отток выручки 5.2 %,
NRR 113 %** (🟩 10-K QTWO FY2025). Но это подписка банка, а не пользователя, и покупается
она банком ровно ради кросс-сейла.

**Вывод одной строкой:** дольше всех живёт B2B-подписка, из потребительских моделей —
подписка (устойчивее, но меньше), лидогенерация даёт больший оборот при марже 1–8 %
и на глазах теряет свой единственный канал привлечения (органический поиск).

### (б) На чём умерло кладбище — по каждому причина с источником

| Продукт | Дата | Причина, названная источником | Класс |
|---|---|---|---|
| **Tally** | 12.08.2024 | Основатель Jason Brown: "we were unable to secure the necessary funding to continue our operations". Механизм: **балансовый кредитный бизнес** (маржа на кредитной линии), в апреле 2024 сам свернул D2C-портфель и объявил пивот в B2B, до выручки от пивота не дожил <6 мес. Умер как **кредитор**, зависимый от рынка капитала, а не как рекомендательный сервис | 🟩 заявление / 🔵 механизм наш |
| **Mint** | объявлено 31.10.2023, отключён 23.03.2024 | Intuit: команда Mint «joined Intuit Credit Karma». Механизм доказан отчётностью: Credit Karma — чистый **cost-per-action** на $2 263 млн с маржой 37 %; два канала к одному кредитному офферу не нужны. **PFM внутри экосистемы — канал, а не продукт** | 🟩 заявление + 🟩 10-K |
| **Simple** | куплена 2014 за $117 млн, закрыта 2021 | Todd Baker (Columbia): "**When BBVA bought Simple, it cut the main source of its freestanding revenues in half**" — интерчейндж попал под потолок поправки Дурбина (21¢ + 0.05 %) при переходе из партнёрского банка $7.7 млрд в BBVA $103 млрд. Brian Hamilton: "Simple essentially died the day BBVA bought it" | 🟩 именованные эксперты |
| **Clarity Money** | куплен Goldman Sachs 2018, закрыт февраль 2024 | Влит в Marcus Insights при сворачивании розничной стратегии Goldman. Тот же класс, что Mint | 🟨 |
| **Level Money** | куплен Capital One, затем закрыт | Тот же класс. Реквизитов и заявления не добыто | 🟨 / 🟥 |
| **Guiabolso** | куплен PicPay 08.2021 (>6 млн польз.), закрыт 11.2022 | Функционал перенесён в PicPay («Minhas finanças»). Отдельно: **атака на модель агрегации данных — иск Bradesco 2016**. Единственный кейс, где смерть связана со стоимостью/легальностью доступа к банковским данным; развязка — Open Finance обнулил барьер агрегации | 🟩 |
| **Playbook** | объявлено 01.10.2024, закрыт 31.10.2024 | "After much consideration, we've made the tough decision to wind down Playbook." **Причина не названа вообще** — ни в объявлении, ни во вторичке | 🟩 заявление / 🟥 причина |
| **Charlie** | 08.2021 | Команда перешла в Chime — **acqui-hire**, не смерть от экономики | 🟨 |
| **Digit** | куплен Oportun 22.12.2021 за $212.9 млн | Не смерть: продукт выжил как фича Set & Save. Но **инвестиционная и пенсионная части списаны**: "non-cash pre-tax impairment charge of $5.6 million related to the write-off of embedded finance, investing and retirement products" (FY2023) | 🟩 10-K OPRT |
| **Moneyhub** (только D2C-направление) | объявлено 14.02.2025, сворачивание 18 мес., отключение 14.08.2026 | Компания дословно: "Our business performance remains strong... **revenue CAGR exceeding 35%**... To better focus on these growing B2B markets **we have decided to withdraw from our direct-to-consumer app business**". Уход из D2C **из позиции силы**, −36 позиций (~30 % штата UK) | 🟩 заявление компании |
| **Prism** | — | Не добыто | 🟥 |

**🔴 Сквозная закономерность, которую видно только на всей подборке.**
Из десяти позиций **ни одна не умерла от того, что «пользователям не нужно управление
финансами»**. Причины делятся на три класса, и ни один не относится к рекомендательной
логике продукта:
1. **Смерть балансового бизнеса** (Tally, отчасти Simple) — умерла процентная/интерчейндж-маржа,
   не рекомендация.
2. **Поглощение экосистемой** (Mint, Clarity Money, Level Money, Guiabolso, Simple, Digit,
   Charlie) — семь из десяти. Продукт закрывают не за убыточность, а потому что внутри
   владельца он является дублирующим каналом. **Это самый частый способ смерти PFM.**
3. **Причина не раскрыта** (Playbook).

Для FINPILOT это переворачивает предъявляемый аргумент: «кладбище PFM» — это в основном
**кладбище поглощённых, а не кладбище неработающих продуктов**. Независимый подписочный
продукт без владельца-банка в эту схему смерти структурно не попадает.

### (в) Какая модель законна и непротиворечива для FINPILOT в РФ

**Прямой ответ: чистая подписка на ПО, и она же — единственная, которая не платит
ни одной из четырёх цен.** Полный разбор с дословными нормами — участок 4, сводная
таблица — §4.5. Здесь — сжатый ответ.

**Неожиданный результат правового участка: юридического запрета на лидогенерацию в РФ НЕТ.**
Статус оператора финансовой платформы по 211-ФЗ **приобретается со дня включения в реестр**
(ст. 11 ч.1), а на не включённых требования закона прямо не распространяются (ст. 1 ч.2) —
то есть вознаграждение без заключения сделки внутри продукта статуса не создаёт (§4.2.1).
Понятия «кредитный брокер» в 353-ФЗ **нет вовсе** — проверено полнотекстово по 386 КБ
действующей редакции (§4.2.2). Ожидание, что лидогенерация упрётся в лицензирование,
**не подтвердилось**.

**Барьер оказался в другом месте — он налоговый и позиционный, и он считается в деньгах:**
1. 🔴 **НДС.** НК РФ ст. 149 п.2 пп.26 освобождает от НДС права на ПО из реестра российских
   программ, «в том числе путем предоставления удаленного доступа... через... сеть "Интернет"».
   Но второй абзац подпункта **прямо исключает** из-под льготы права, состоящие в возможности
   «распространять рекламную информацию» и «**осуществлять поиск информации о потенциальных
   покупателях (продавцах)**». Лидогенерация и реклама **стоят FINPILOT освобождения от НДС**,
   то есть порядка **20 % выручки**.
2. **Признак «подталкивание к конкретному инструменту».** Доклад ЦБ о наджинге (2026)
   воспроизводит позицию ESMA: сообщение, подталкивающее к сделке с конкретным финансовым
   инструментом, следует рассматривать как индивидуальную рекомендацию. Наш щит из тем 18–19 —
   предметный (инструмент не назван) — исчезает в тот момент, когда рядом с расчётом появляется
   партнёрский оффер конкретного банка. Не по нашему решению, а по описанному регулятором
   признаку (§4.2.4).
3. **Обязательства площадки.** Реклама финуслуг внутри продукта законна, но на нас лично
   ложатся ч.1, 2.1, 3.1 и 13 ст. 28 ФЗ «О рекламе» (ст. 38 ч.7) — включая обязательные
   предупреждения «Изучите все условия кредита (займа)» и «Оценивайте свои финансовые
   возможности и риски» с занятием **не менее 5 % рекламной площади**, — плюс маркировка
   «реклама» и идентификатор erid (ст. 18.1 ч.16–17) под штрафом **до 500 тыс. руб.**
   на юрлицо (КоАП ст. 14.3 ч.15–16).
4. **Позиция ЦБ.** §4.0: сервисы финздоровья «важно, чтобы… были независимыми, то есть
   в них не было скрытой рекламы и продажи финансовых продуктов» (пресс-служба ЦБ,
   «Известия», 15.08.2024). Юридической силы не имеет, но это заявленное ожидание регулятора
   ровно по нашей нише.

**Что требуется от подписочной модели, чтобы она была законной (§4.3):** оферта как
**лицензионный договор в упрощённом порядке** (ГК ст. 1286 п.5) — с обязательной **явной
оговоркой о возмездности**, иначе договор по умолчанию безвозмездный; электронный чек
на e-mail/телефон до совершения расчёта (54-ФЗ ст. 1.2 п.5), с возможностью сводного
месячного чека при авансах (п. 2.1); порядок возврата с учётом ЗоЗПП ст. 32 (отказ в любое
время с возмещением фактически понесённых расходов — для SaaS они близки к нулю).
Единственное реальное препятствие для попадания в реестр ПО — **пп. «м» ПП РФ № 1236**
(совместимость не менее чем с двумя доверенными ОС), его толкование для веб-приложения
надо выяснить **до** подачи заявления.

Экономическая часть ответа, следующая из добытого:

**Совместима с позиционированием «у нас нет продавца в контуре» ровно одна модель —
прямая подписка пользователя.** Это не выбор из нескольких, а единственный остаток
после вычёркивания:
- **лидогенерация вычёркивается позиционированием**, а не законом: публичная позиция ЦБ РФ —
  сервисы финансового здоровья «важно, чтобы… были **независимыми, то есть в них не было
  скрытой рекламы и продажи финансовых продуктов**». Партнёрское вознаграждение от банка
  за приведённого клиента — ровно то, против чего это сказано;
- **реклама вычёркивается тем, что не является отдельной опцией**: в PFM рекламодателем
  выступает тот же банк с тем же оффером, и CPM-модель схлопывается в cost-per-action
  (§1.5) — то есть в тот же конфликт интересов, только неявный;
- **B2B-лицензирование движка банку вычёркивается той же логикой**: банк покупает движок
  ради кросс-сейла, вендоры сами называют целевой функцией LTV/ARPU/кросс-сейл (тема 19).
  Как отдельная бизнес-линия в будущем — возможно, но не под тем же брендом и не с тем же
  обещанием независимости;
- **балансовые модели (выдача денег, как у Tally) не рассматриваются** — это другой бизнес
  с лицензией, капиталом и кредитным риском, и именно на нём умер ближайший к нам аналог.

**Практический вывод для конструкции тарифа**, опирающийся на §1.2:
граница платного у лидера рынка проходит **не по синхронизации счетов и не по аналитике**
(они бесплатны у Rocket Money), а по **выполненному за пользователя действию и по снятию
количественных ограничений**. Для FINPILOT, который по построению выдаёт рекомендацию,
а не совершает действие, это значит: платить будут не за «показать аналитику», а за
**вычисленный план распределения свободного денежного потока** — то есть за результат
расчёта, который пользователь сам не получит. Это гипотеза о ценообразовании,
подлежащая проверке, а не установленный факт.

---

## Что не добыто и почему

| Что | Канал и код ответа |
|---|---|
| CAC, LTV, конверсия free→paid, отток **Rocket Money** | Проверено `grep` по полным текстам 10-K RKT FY2024 и FY2025 (3.2 и 3.6 МБ) — **эмитент не раскрывает**. Не «не нашёл», а «не публикуется» |
| MUU (Monthly Unique Users) **NerdWallet** | 0 вхождений «MUU»/«Monthly Unique Users» в полном тексте 10-K NRDS FY2025. Метрика снята с публикации |
| Юнит-экономика **Tally** (CAC/LTV/отток) | Компания частная, отчётности не подавала. В TechCrunch, Banking Dive, PYMNTS, Crowdfund Insider цифр нет |
| **Причина закрытия Playbook** | Объявление о сворачивании добыто дословно (helloplaybook.webflow.io), но причины в нём нет. Вторичных источников с причиной не найдено |
| Дословное заявление о закрытии **Charlie**, **Level Money** | Не найдено; доступны только упоминания в обзорных статьях (🟨) |
| ~~Подтверждение закрытия **Moneyhub**~~ | **ДОБЫТО во втором заходе.** `WebFetch` на fintechfutures.com → **403**; `r.jina.ai` → полный текст с заявлением компании. Уточнение к заданию: закрылось D2C-направление, компания жива |
| **Prism** | Целевых источников не найдено; неоднозначность самого названия |
| **Envestnet/Yodlee** | Envestnet выкуплена Bain Capital (2024) и делистингована — публичной отчётности за FY2025 не существует |
| **MoneyLion** | Приобретена Gen Digital (закрыто 2025), самостоятельных 10-K не подаёт; сегментного раскрытия внутри Gen Digital не найдено |
| **Acorns** | SPAC-сделка с Pioneer Merger Corp расторгнута в 2022 → публичных раскрытий не появилось; S-1 действующей компании в EDGAR нет |
| Прайс-листы **Personetics, Meniga, Moneythor, Tink, MX** | Частные компании, цены под NDA. Обойдено через публичный аналог Q2 Holdings |
| Длина цикла продажи B2B в месяцах | Q2 Holdings называет его риском ("length, cost and unpredictability of our sales cycle"), но **числа не публикует** |
| Размер выборки бенчмарков **Recurly** | Сама Recurly не раскрывает; указано только "Recurly's network" и, в смежном материале, «more than 2000 businesses» |
| Устранение расхождения Recurly (3.60 % против 5.6 %) | Разные страницы того же вендора дают разные числа; в бюджете темы не разрешено. Записано диапазоном |
| `www.rocketmoney.com/premium` | `WebFetch` → **302** на `app.rocketmoney.com/premium` → **404**. Обойдено через `r.jina.ai` по главной странице |
| `help.rocketmoney.com` статья о Premium | `r.jina.ai` → целевой URL вернул **404** |
| **Правовой контур (участок 4), добыто субагентом:** | |
| Точные реквизиты редакции ст. 28 ФЗ «О рекламе» (номер и дата закона-редактора) | `zakonrf.info` → **200**, но реквизит на странице не публикуется; `pravo.gov.ru` не открывался. Актуальность подтверждена косвенно (наличие ч.15 от 417-ФЗ). **Перед юридическим использованием сверить** |
| Полный текст 211-ФЗ на `consultant.ru` | `consultant.ru` → **200**, но текст закрыт заглушкой «доступен по расписанию» некоммерческой версии; через `r.jina.ai` → **200**, та же заглушка. Обойдено через `legalacts.ru` → **200** |
| ФЗ № 161-ФЗ ст. 14 (банковский платёжный агент) | `legalacts.ru` по угаданному URL → **404**. К задаче не относится (платёжный агент ≠ рекомендация) |
| Информационное письмо ЦБ ровно про лидогенерацию / партнёрское вознаграждение / «сервисы финздоровья» | `WebSearch` по `cbr.ru` → результатов по предмету **нет**. Найдено смежное и более ценное — доклад о наджинге (§4.2.4) |
| **Тексты Методических рекомендаций ЦБ № 22-МР (27.12.2024) и № 1-МР (20.01.2025)** | Не запрашивались — бюджет субагента исчерпан. **Реквизиты установлены точно. Первая цель следующего захода** |
| Позиция Роспотребнадзора и судебная практика по возврату за неиспользованный период подписки на ПО | Не запрашивались — бюджет. На `zakonrf.info/zozpp/32/` есть блок судебной практики 2025 г., но это карточки-аннотации, не тексты по подписке на ПО — как первоисточник не засчитано |
| ПП РФ с критериями интернет-рекламы к ст. 18.1 ч.3 и приказ РКН о требованиях к erid | Не запрашивались — бюджет |
| `docs.cntd.ru` | код **000**, соединение не установлено |
| `r.jina.ai` на `zakonrf.info/zoreklame/28/` | **200**, но вернул **пересказ вместо дословного текста** — важное ограничение канала: для дословности нужен сырой HTML со своим стриппером, а не текстовый прокси |
| SEC EDGAR прямым `curl` без контактного UA | **HTTP-заглушка «Your Request Originates from an Undeclared Automated Tool»** (файл 4.8 КБ вместо документа). Лечится заголовком `User-Agent` с контактом — после этого все 10-K снялись с первого раза |

## Метод поиска

**Объём (по контуру лида, без учёта работы субагента).** 8 вызовов `WebSearch`, 8 вызовов
`WebFetch`, 14 вызовов `Bash`
(`curl` + разбор HTML в текст на Python + `grep`/`regex` по полным текстам), 1 субагент
(участок 4, правовой блок РФ). Скачано и разобрано в plain text **шесть документов SEC**
общим объёмом ~14 МБ HTML: INTU 10-K FY2025 (2.8 МБ), RKT 10-K FY2024 (3.2 МБ) и FY2025
(3.6 МБ), NRDS 10-K FY2025, QTWO 10-K FY2025, OPRT 10-K FY2024.

**Поисковые запросы (дословно):**
1. `Tally credit card debt app shut down 2024 Jason Brown`
2. `Intuit shutting down Mint official statement Credit Karma`
3. `Intuit 10-K Credit Karma revenue fiscal 2025 segment`
4. `Rocket Companies 10-K Rocket Money premium members subscription revenue`
5. `Monarch Money ARR paying subscribers funding round 2025`
6. `Digit app shut down Simple bank BBVA closed Clarity Money Marcus discontinued personal finance app`
7. `Guiabolso PicPay acquisition shutdown Brazil PFM`
8. `Playbook app shut down wealth 2024 Charlie fintech app shut down Digit Oportun`
9. `Oportun Digit acquisition $213 million wind down savings business 2024`
10. `Recurly subscription churn benchmark report consumer average monthly churn rate methodology`
11. `Moneyhub consumer app closed personal finance UK discontinued D2C`
12. `Банк России сервисы финансового здоровья независимыми скрытой рекламы продажи финансовых продуктов`

**Приёмы, которые сработали и стоит запомнить:**
- 🔴 **SEC EDGAR требует `User-Agent` с контактными данными.** Обычный браузерный UA получает
  заглушку «Undeclared Automated Tool» (тело 4.8 КБ). С `-H "User-Agent: <название> <email>"`
  все документы отдаются с первого раза. Это не антибот, а формальное требование SEC.
- 🔴 **Индекс подач вместо угадывания URL:** `https://data.sec.gov/submissions/CIK<10 цифр>.json`
  отдаёт полный список форм с accession number и primary document — из него собирается
  прямая ссылка на любой 10-K за любой год. Так найдены свежие подачи NRDS (25.02.2026),
  QTWO (11.02.2026), OPRT (27.02.2026), которые поиском не находились.
- 🔴 **Разбор 10-K локально, а не через модель.** `curl` → снятие тегов регуляркой →
  поиск по подстрокам с контекстом ±600 символов. Так вытащены точные таблицы сегментов
  и, что важнее, **доказан отрицательный результат**: 0 вхождений «Mint» в 10-K Intuit
  FY2025, 0 вхождений «MUU» у NerdWallet, отсутствие CAC/LTV у Rocket Companies.
  Отрицательный результат такого рода нельзя получить, читая документ глазами.
- `r.jina.ai` пробил `rocketmoney.com` там, где `WebFetch` ушёл в 302 → 404.

**Контур субагента (участок 4, правовой блок РФ).** Один субагент, ~30 вызовов инструментов,
2 `WebSearch`, 2 `WebFetch`, остальное — `curl` с браузерным UA + локальный стриппер HTML.
Открыто и снято дословно: **`zakonrf.info` — 15 страниц, все HTTP 200** (ФЗ «О рекламе» ст. 3,
5, 18.1, 28, 38; ГК ст. 435, 437, 438, 1286; НК ст. 149; ЗоЗПП ст. 26.1, 32; 54-ФЗ ст. 1.2,
4.7; Закон о банках ст. 13.1; КоАП ст. 14.3); **`legalacts.ru` — 3 документа** (211-ФЗ ред.
27.10.2025, 353-ФЗ ред. 04.08.2026, ПП РФ № 1236 ред. 13.08.2026), 161-ФЗ → 404;
**`cbr.ru`** — PDF доклада о наджинге (200, 759 721 байт), разобран `pdftotext -layout`.
Запросы: «211-ФЗ … статья 2 оператор финансовой платформы текст»; «Банк России информационное
письмо маркетплейс лидогенерация вознаграждение за привлечение клиента» (с ограничением
по домену `cbr.ru`).
🔴 **Приём субагента, который стоит запомнить:** `r.jina.ai` на страницу с текстом закона
вернул **пересказ, а не дословный текст**. Для дословности пришлось брать сырой HTML
и стриппить локально. Текстовый прокси хорош против антибота, но **не годится там, где нужна
дословность нормы**.

**Что осталось за рамками бюджета:** российские аналоги (ЮMoney/Тинькофф-аналитика,
«Дзен-мани», CoinKeeper) не разбирались — задание касалось мирового кладбища и моделей;
российский контур покрыт участком 4 в правовой части.

---

# ПРИЛОЖЕНИЯ — дословные тексты норм

> Правило §9 CLAUDE.md проекта: первичный материал сохраняется дословно ДО выжимки.
> Ниже — полные тексты, на которые ссылается участок 4.
> Все сняты каналом `curl` с браузерным User-Agent, HTTP 200, 10.09.2026.

## Приложение А. ФЗ от 13.03.2006 № 38-ФЗ «О рекламе», статья 28 — полностью

Источник: `https://www.zakonrf.info/zoreklame/28/`
Актуальность: в тексте присутствует ч.15, введённая ФЗ от 04.08.2023 № 417-ФЗ.
⬜ Точные реквизиты редакции на странице не публикуются — НЕ ДОБЫТО.

> **Статья 28. Реклама финансовых услуг и финансовой деятельности**
>
> 1. Реклама банковских, страховых и иных финансовых услуг и финансовой деятельности должна содержать наименование или имя лица, оказывающего эти услуги или осуществляющего данную деятельность (для юридического лица - наименование, для индивидуального предпринимателя - фамилию, имя и (если имеется) отчество).
>
> 2. Реклама банковских, страховых и иных финансовых услуг и финансовой деятельности не должна:
> 1) содержать гарантии или обещания в будущем эффективности деятельности (доходности вложений), в том числе основанные на реальных показателях в прошлом, если такая эффективность деятельности (доходность вложений) не может быть определена на момент заключения соответствующего договора;
> 2) умалчивать об иных условиях оказания соответствующих услуг, влияющих на сумму доходов, которые получат воспользовавшиеся услугами лица, или на сумму расходов, которую понесут воспользовавшиеся услугами лица, если в рекламе сообщается хотя бы одно из таких условий. Положения настоящего пункта не распространяются на рекламу услуг, связанных с предоставлением потребительского кредита (займа), пользованием им и погашением указанного кредита (займа).
>
> 2.1. Если реклама услуг, связанных с предоставлением потребительского кредита (займа), пользованием им и погашением указанного кредита (займа), содержит хотя бы одно условие, влияющее на полную стоимость потребительского кредита (займа), определяемую в соответствии с Федеральным законом от 21 декабря 2013 года N 353-ФЗ "О потребительском кредите (займе)", такая реклама должна соответствовать одному из следующих требований:
> 1) содержать предупреждение: "Изучите все условия кредита (займа)" с указанием на раздел официального сайта кредитора, который обеспечивает потребителю рекламы возможность ознакомления с подробными условиями оказания соответствующих услуг, влияющими на полную стоимость потребительского кредита (займа), определяемую в соответствии с Федеральным законом от 21 декабря 2013 года N 353-ФЗ "О потребительском кредите (займе)". В рекламе, распространяемой в радиопрограммах, продолжительность такого предупреждения должна составлять не менее чем три секунды, в рекламе, распространяемой в телепрограммах и при кино- и видеообслуживании, - не менее чем три секунды и должно быть отведено не менее чем пять процентов площади кадра, а в рекламе, распространяемой другими способами, - не менее чем пять процентов рекламной площади (рекламного пространства);
> 2) содержать все условия, влияющие на полную стоимость потребительского кредита (займа), определяемую в соответствии с Федеральным законом от 21 декабря 2013 года N 353-ФЗ "О потребительском кредите (займе)", в случае невозможности указания на раздел официального сайта, указанный в пункте 1 настоящей части. В рекламе, распространяемой в радиопрограммах, продолжительность упоминания таких условий должна составлять не менее чем три секунды, в рекламе, распространяемой в телепрограммах и при кино- и видеообслуживании, продолжительность упоминания (демонстрации) таких условий должна составлять не менее чем три секунды и упоминанию (демонстрации) таких условий должно быть отведено не менее чем пять процентов площади кадра, а в рекламе, распространяемой другими способами, - не менее чем пять процентов рекламной площади (рекламного пространства).
>
> 3. Если реклама услуг, связанных с предоставлением потребительского кредита (займа), пользованием им и погашением указанного кредита (займа), содержит информацию о процентных ставках, в дополнение к требованиям части 2.1 настоящей статьи такая реклама должна содержать информацию о диапазонах значений полной стоимости потребительского кредита (займа), определенных с учетом требований Федерального закона от 21 декабря 2013 года N 353-ФЗ "О потребительском кредите (займе)" по видам потребительского кредита (займа), с использованием слов "полная стоимость кредита (займа)". Указанная информация должна предоставляться до предоставления информации о процентных ставках и указываться шрифтом, размер которого не менее чем шрифт, которым отображается информация о процентных ставках.
>
> 3.1. Реклама услуг, связанных с предоставлением потребительского кредита (займа), пользованием им и погашением указанного кредита (займа), должна содержать предупреждение: "Оценивайте свои финансовые возможности и риски". В рекламе, распространяемой в радиопрограммах, продолжительность такого предупреждения должна составлять не менее чем три секунды, в рекламе, распространяемой в телепрограммах и при кино- и видеообслуживании, - не менее чем три секунды и должно быть отведено не менее чем пять процентов площади кадра, а в рекламе, распространяемой другими способами, - не менее чем пять процентов рекламной площади (рекламного пространства).
>
> 3.2. Правила, предусмотренные частями 2.1, 3 и 3.1 настоящей статьи, также применяются к рекламе услуг, связанных с предоставлением кредита (займа) физическим лицам в целях, не связанных с осуществлением ими предпринимательской деятельности, и обязательства заемщика по которому обеспечены ипотекой.
>
> 4. Реклама услуг, связанных с осуществлением управления, включая доверительное управление, активами (в том числе ценными бумагами, инвестиционными резервами акционерных инвестиционных фондов, паевыми инвестиционными фондами, пенсионными резервами негосударственных пенсионных фондов, средствами пенсионных накоплений, ипотечным покрытием, накоплениями для жилищного обеспечения военнослужащих), должна содержать:
> 1) источник информации, подлежащей раскрытию в соответствии с федеральным законом;
> 2) сведения о месте или об адресе (номер телефона), где до заключения соответствующего договора заинтересованные лица могут ознакомиться с условиями управления активами, получить сведения о лице, осуществляющем управление активами, и иную информацию, которая должна быть предоставлена в соответствии с федеральным законом и иными нормативными правовыми актами Российской Федерации.
>
> 5. Реклама услуг, связанных с осуществлением управления, включая доверительное управление, активами, не должна содержать:
> 1) документально не подтвержденную информацию, если она непосредственно относится к управлению активами;
> 2) информацию о результатах управления активами, в том числе об их изменении или о сравнении в прошлом и (или) в текущий момент, не основанную на расчетах доходности, определяемых в соответствии с нормативными актами Центрального банка Российской Федерации;
> 3) информацию о гарантиях надежности возможных инвестиций и стабильности размеров возможных доходов или издержек, связанных с указанными инвестициями;
> 4) информацию о возможных выгодах, связанных с методами управления активами и (или) осуществлением иной деятельности;
> 5) заявления о возможности достижения в будущем результатов управления активами, аналогичных достигнутым результатам.
>
> 5.1. Реклама, побуждающая к заключению сделок с форекс-дилерами, должна содержать следующее указание: "Предлагаемые к заключению договоры или финансовые инструменты являются высокорискованными и могут привести к потере внесенных денежных средств в полном объеме. До совершения сделок следует ознакомиться с рисками, с которыми они связаны.". Публичное объявление цен (порядка определения цен), а также иных существенных условий договора не является рекламой, побуждающей к заключению сделок с форекс-дилерами.
>
> 5.2. Реклама услуг по содействию в инвестировании с использованием инвестиционной платформы должна содержать:
> 1) адрес сайта в информационно-телекоммуникационной сети "Интернет", на котором осуществляется раскрытие информации оператором инвестиционной платформы;
> 2) указание на то, что заключение с использованием инвестиционной платформы договоров, по которым привлекаются инвестиции, является высокорискованным и может привести к потере инвестированных денежных средств в полном объеме.
>
> 5.3. Не допускается реклама, связанная с привлечением инвестиций с использованием инвестиционной платформы следующими способами:
> 1) предоставление займов;
> 2) приобретение размещаемых акций непубличного акционерного общества и эмиссионных ценных бумаг, конвертируемых в акции непубличного акционерного общества;
> 3) приобретение утилитарных цифровых прав.
>
> 6. Не допускается реклама, связанная с привлечением денежных средств физических лиц для строительства жилья, за исключением рекламы, связанной с привлечением денежных средств на основании договора участия в долевом строительстве, рекламы жилищных и жилищно-строительных кооперативов, рекламы, связанной с привлечением и использованием жилищными накопительными кооперативами денежных средств физических лиц на приобретение жилых помещений.
>
> 7. Реклама, связанная с привлечением денежных средств участников долевого строительства для строительства (создания) многоквартирных домов и (или) иных объектов недвижимости, должна содержать адрес сайта единой информационной системы жилищного строительства в информационно-телекоммуникационной сети "Интернет", на котором осуществляется размещение проектной декларации, предусмотренной федеральным законом, фирменное наименование (наименование) застройщика либо указанное в проектной декларации индивидуализирующее застройщика коммерческое обозначение. Реклама, связанная с привлечением денежных средств участников долевого строительства для строительства (создания) многоквартирных домов и (или) иных объектов недвижимости, может содержать коммерческое обозначение, индивидуализирующее объект (группу объектов) капитального строительства (в случае строительства многоквартирных домов - наименование жилого комплекса), если такое коммерческое обозначение (наименование жилого комплекса) указано в проектной декларации.
>
> 8. Реклама, связанная с привлечением денежных средств участников долевого строительства для строительства (создания) многоквартирных домов и (или) иных объектов недвижимости, не допускается до выдачи в установленном порядке разрешения на строительство многоквартирного дома и (или) иного объекта недвижимости, государственной регистрации права собственности или права аренды, субаренды на земельный участок, на котором осуществляется строительство (создание) многоквартирного дома и (или) иного объекта недвижимости, в составе которых будут находиться объекты долевого строительства, получения заключения уполномоченного на осуществление регионального государственного контроля (надзора) в области долевого строительства многоквартирных домов и (или) иных объектов недвижимости органа исполнительной власти субъекта Российской Федерации, на территории которого осуществляется строительство (создание) соответствующих многоквартирного дома и (или) иного объекта недвижимости, о соответствии застройщика и проектной декларации требованиям, установленным Федеральным законом от 30 декабря 2004 года N 214-ФЗ "Об участии в долевом строительстве многоквартирных домов и иных объектов недвижимости и о внесении изменений в некоторые законодательные акты Российской Федерации", если получение такого заключения предусмотрено указанным Федеральным законом.
>
> 9. Реклама, связанная с привлечением денежных средств участников долевого строительства для строительства (создания) многоквартирного дома и (или) иного объекта недвижимости, не допускается в период приостановления в соответствии с федеральным законом деятельности застройщика, связанной с привлечением денежных средств участников долевого строительства для строительства (создания) многоквартирного дома и (или) иного объекта недвижимости.
>
> 10. Требования частей 7 - 9 настоящей статьи распространяются также на рекламу, связанную с уступкой прав требований по договору участия в долевом строительстве.
>
> 11. Реклама, связанная с привлечением и использованием жилищным накопительным кооперативом денежных средств физических лиц на приобретение жилых помещений, должна содержать:
> 1) информацию о порядке покрытия членами жилищного накопительного кооператива понесенных им убытков;
> 2) сведения о включении жилищного накопительного кооператива в реестр жилищных накопительных кооперативов;
> 3) адрес сайта в информационно-телекоммуникационной сети общего пользования (в том числе в сети "Интернет"), на котором осуществляется раскрытие информации жилищным накопительным кооперативом.
>
> 12. В рекламе, связанной с привлечением и использованием жилищным накопительным кооперативом денежных средств физических лиц на приобретение жилых помещений, не допускается гарантировать сроки приобретения или строительства таким кооперативом жилых помещений.
>
> 13. Реклама услуг по предоставлению потребительских займов лицами, не осуществляющими профессиональную деятельность по предоставлению потребительских займов в соответствии с Федеральным законом от 21 декабря 2013 года N 353-ФЗ "О потребительском кредите (займе)", не допускается.
>
> 14. Если оказание банковских, страховых и иных финансовых услуг или осуществление финансовой деятельности может осуществляться только лицами, имеющими соответствующие лицензии, разрешения, аккредитации либо включенными в соответствующий реестр или являющимися членами соответствующих саморегулируемых организаций, реклама указанных услуг или деятельности, оказываемых либо осуществляемой лицами, не соответствующими таким требованиям, не допускается.
>
> 15. Если лицо, не являющееся кредитной или некредитной финансовой организацией, осуществляет один или несколько видов деятельности, указанных в части 1 статьи 2 Федерального закона от 4 августа 2023 года N 417-ФЗ "О проведении эксперимента по установлению специального регулирования в целях создания необходимых условий для осуществления деятельности по партнерскому финансированию в отдельных субъектах Российской Федерации и о внесении изменений в отдельные законодательные акты Российской Федерации", признаваемых для целей указанного Федерального закона деятельностью по партнерскому финансированию, реклама такой деятельности должна содержать информацию о включении этого лица в реестр участников эксперимента, предусмотренный статьей 4 указанного Федерального закона. Требования, предусмотренные настоящей частью, применяются до окончания срока проводимого в соответствии с указанным Федеральным законом эксперимента.

## Приложение Б. ФЗ от 22.05.2003 № 54-ФЗ, ст. 4.7 ч.1 — обязательные реквизиты чека

Источник: `https://www.zakonrf.info/zakon-o-kkt/4.7/`

> **Статья 4.7. Требования к кассовому чеку и бланку строгой отчетности**
> 1. Кассовый чек и бланк строгой отчетности, за исключением случаев, установленных настоящим Федеральным законом, содержат с учетом положений пунктов 1.1 и 1.2 настоящей статьи следующие обязательные реквизиты:
> наименование документа;
> порядковый номер за смену;
> дата, время и место (адрес) осуществления расчета (при расчете в зданиях и помещениях - адрес здания и помещения с почтовым индексом, при расчете в транспортных средствах - наименование и номер транспортного средства, адрес организации либо адрес регистрации индивидуального предпринимателя, при расчете в сети "Интернет" - адрес сайта пользователя);
> наименование организации-пользователя или фамилия, имя, отчество (при наличии) индивидуального предпринимателя - пользователя;
> идентификационный номер налогоплательщика пользователя;
> применяемая при расчете система налогообложения;
> признак расчета (получение средств от покупателя (клиента) - приход, возврат покупателю (клиенту) средств, полученных от него, - возврат прихода, выдача средств покупателю (клиенту) - расход, получение средств от покупателя (клиента), выданных ему, - возврат расхода);
> наименование товаров, работ, услуг (если объем и список услуг возможно определить в момент оплаты), платежа, выплаты, их количество, цена (в валюте Российской Федерации) за единицу с учетом скидок и наценок, стоимость с учетом скидок и наценок, с указанием ставки налога на добавленную стоимость (за исключением случаев осуществления расчетов пользователями, не являющимися налогоплательщиками налога на добавленную стоимость или освобожденными от исполнения обязанностей налогоплательщика налога на добавленную стоимость, а также осуществления расчетов за товары, работы, услуги, не подлежащие налогообложению (освобождаемые от налогообложения) налогом на добавленную стоимость);
> сумма расчета с отдельным указанием ставок и сумм налога на добавленную стоимость по этим ставкам (за исключением тех же случаев);
> форма расчета (оплата наличными деньгами и (или) в безналичном порядке), а также сумма оплаты наличными деньгами и (или) в безналичном порядке;
> должность и фамилия лица, осуществившего расчет с покупателем (клиентом), оформившего кассовый чек или бланк строгой отчетности и выдавшего (передавшего) его покупателю (клиенту) (за исключением расчетов, осуществленных с использованием автоматических устройств для расчетов, применяемых в том числе при осуществлении расчетов в безналичном порядке в сети "Интернет");
> регистрационный номер контрольно-кассовой техники;
> заводской номер экземпляра модели фискального накопителя;
> фискальный признак документа;
> адрес сайта уполномоченного органа в сети "Интернет", на котором может быть осуществлена проверка факта записи этого расчета и подлинности фискального признака;
> абонентский номер либо адрес электронной почты покупателя (клиента) в случае передачи ему кассового чека или бланка строгой отчетности в электронной форме или идентифицирующих такие кассовый чек или бланк строгой отчетности признаков и информации об адресе информационного ресурса в сети "Интернет", на котором такой документ может быть получен;
> адрес электронной почты отправителя кассового чека или бланка строгой отчетности в электронной форме в случае передачи покупателю (клиенту) кассового чека или бланка строгой отчетности в электронной форме;
> порядковый номер фискального документа;
> номер смены;
> фискальный признак сообщения (для кассового чека или бланка строгой отчетности, хранимых в фискальном накопителе или передаваемых оператору фискальных данных);
> QR-код.

## Приложение В. ПП РФ от 16.11.2015 № 1236, п.5 — требования к ПО для включения в реестр

Источник: `https://legalacts.ru/doc/postanovlenie-pravitelstva-rf-ot-16112015-n-1236/`, ред. от 13.08.2026.
Наименование акта в действующей редакции: «Об утверждении Правил формирования и ведения
единого реестра российских программ для электронных вычислительных машин и баз данных
и единого реестра программ для электронных вычислительных машин и баз данных из государств -
членов Евразийского экономического союза, за исключением Российской Федерации».

> **5. В реестр российского программного обеспечения включаются сведения о программном обеспечении, которое соответствует следующим требованиям:**
> а) исключительное право на программное обеспечение на территории всего мира и на весь срок действия исключительного права принадлежит одному либо нескольким из следующих лиц (правообладателей): Российской Федерации; субъекту Российской Федерации; муниципальному образованию; российской некоммерческой организации, высший орган управления которой формируется прямо и (или) косвенно Российской Федерацией, субъектами Российской Федерации, муниципальными образованиями и (или) гражданами Российской Федерации и решения которой иностранное лицо не имеет возможности определять ...; российской коммерческой организации, которая ... находится под контролем Российской Федерации, и (или) субъекта Российской Федерации, и (или) муниципального образования, и (или) гражданина Российской Федерации, и (или) контролируемых ими совместно или по отдельности лиц. При этом под контролем понимается возможность определять решения ... в силу наличия права прямо или косвенно распоряжаться более чем 50 процентами общего количества голосов ...; гражданину Российской Федерации;
> б) программное обеспечение правомерно введено в гражданский оборот на территории Российской Федерации, экземпляры программного обеспечения либо права использования программного обеспечения, услуги по предоставлению доступа к программному обеспечению свободно реализуются на всей территории Российской Федерации, отсутствуют ограничения, установленные в том числе иностранными государствами и препятствующие распространению или иному использованию ...;
> в) общая сумма выплат по лицензионным и иным договорам ... в пользу иностранных юридических лиц и (или) физических лиц, контролируемых ими российских коммерческих и (или) некоммерческих организаций, агентов, представителей иностранных лиц ... составляет менее 30 процентов выручки, полученной правообладателем (правообладателями) за истекший календарный год ...;
> г) сведения о программном обеспечении не составляют государственную тайну и программное обеспечение не содержит сведений, составляющих государственную тайну;
> д) соответствие программного обеспечения требованиям безопасности информации подтверждено сертификатом ... (только для программного обеспечения, основной функцией которого является защита конфиденциальной информации);
> ж) программное обеспечение не имеет принудительного обновления и управления из-за рубежа;
> з) гарантийное обслуживание, техническая поддержка и модернизация программного обеспечения, в том числе модификация исходного текста программного обеспечения, осуществляются российской коммерческой или некоммерческой организацией без преобладающего иностранного участия либо гражданином Российской Федерации;
> и) технические средства хранения исходного текста и объектного кода программного обеспечения, а также технические средства компиляции исходного текста в объектный код программного обеспечения находятся на территории Российской Федерации;
> к) технические средства, необходимые для активации, выпуска, распространения, управления лицензионными ключами программного обеспечения находятся на территории Российской Федерации, контролируются российскими организациями либо гражданами Российской Федерации;
> л) графический пользовательский интерфейс программного обеспечения реализован на русском языке;
> м) программное обеспечение совместимо не менее чем с 2 операционными системами, соответствующими требованиям к доверенному программному обеспечению. Программное обеспечение может быть совместимо с одной операционной системой ... в случаях если: правообладатель такого программного обеспечения и правообладатель операционной системы входят в одну группу лиц; такое программное обеспечение используется исключительно в составе программно-аппаратного комплекса;
> н) доля выручки, полученной правообладателем в качестве вознаграждения от реализации программного обеспечения ... организациям, входящим в одну группу лиц с правообладателем, не должна превышать 30 процентов общей выручки ... (только для программного обеспечения, правообладателем которого является государственная корпорация, государственная компания, публично-правовая компания и иная организация, в уставном капитале которой доля прямого и (или) косвенного участия Российской Федерации ... превышает 50 процентов ...).

---

**Конец файла.** Тема 24 закрыта; открытые хвосты перечислены в разделе
«Что не добыто и почему». Первая цель следующего захода — тексты Методических рекомендаций
Банка России **№ 22-МР от 27.12.2024** и **№ 1-МР от 20.01.2025**.


---

## ДОБОР Г1 — Возврат за неиспользованный период подписки: позиция ВС РФ, Роспотребнадзора, практика 🔴

> Добыто 11.09.2026.

### 1. Информационное сообщение органа системы Роспотребнадзора со ссылкой на п. 10 Обзора ВС РФ за 2023 г.

> `https://volchansk-adm.ru/govinfo/rospotrebnadzor/media/2025/8/20/vozvrat-denezhnyih-sredstv-za-platnyie-podpiski/` — `curl -skL --http1.1`, HTTP 200, 40 937 байт. Автор — Североуральский филиал ФБУЗ «Центр гигиены и эпидемиологии в Свердловской области» (учреждение Роспотребнадзора), дата публикации по URL 20.08.2025. Это не письмо центрального аппарата, а консультационная публикация; сам Обзор ВС открыт ниже отдельно (или помечен как не добытый).

Дословно:

```
Центр гигиены и эпидемиологии в СО
    Если Вы заметили ошибку в тексте, выделите необходимый фрагмент и нажмите Ctrl Enter. Заранее благодарны!
        Возврат денежных средств за платные подписки
Североуральский филиал ФБУЗ «Центр гигиены и эпидемиологии в Свердловской области» информирует о том, что у потребителей есть право вернуть часть уплаченной абонентской платы при отказе от договора, если он не воспользовался услугами в полном объеме.
Многие потребители оформляют подписку (абонемент) в онлайн-кинотеатры, пользуясь возможностью просматривать фильмы, сериалы и иной медиаконтент.
В случае, если по тем или иным причинам потребитель передумал использовать подписку, возникает вопрос, можно ли вернуть деньги?
Положения ст. 429.4 ГК РФ регулирующие условия заключения абонентского договора, не предусматривают возврата уплаченных потребителем денежных средств при одностороннем отказе от договора.
Предприниматели, предоставляющие услуги и сервисы по подписке, чаще всего включают в оферту положения о том, что подключение подписки является самостоятельной, отдельной и неделимой услугой, которая считается предоставленной клиенту в момент ее оплаты и предоставления доступа к товарам, услугам или контенту. Соответственно, по часто высказываемому ими мнению, в том числе в суде, даже в случае одностороннего отказа клиента от договора они не обязаны возвращать ему часть полученной платы.
Однако с данной позицией не согласился Верховный суд Российской Федерации (п. 10 Обзора ВС РФ судебной практики по делам о защите прав потребителей 2023 года) и пояснил следующее:
Согласно п. 1 ст. 429.4 ГК РФ договором с исполнением по требованию (абонентским договором) признается договор, предусматривающий внесение одной из сторон (абонентом) определенных, в том числе периодических, платежей или иного предоставления за право требовать от другой стороны (исполнителя) предоставления предусмотренного договором исполнения в затребованных количестве или объеме либо на иных условиях, определяемых абонентом.
В соответствии с п. 1 ст. 779 ГК РФ по договору возмездного оказания услуг исполнитель обязуется по заданию заказчика оказать услуги (совершить определенные действия или осуществить определенную деятельность), а заказчик обязуется оплатить эти услуги.
На отношения, связанные с заключением договоров об оказании услуг, стороной которых является гражданин, использующий услугу в личных целях, распространяются положения законодательства о защите прав потребителей.
В силу ст. 32 Закона о защите прав потребителей и п. 1 ст. 782 ГК РФ потребитель вправе отказаться от исполнения договора о выполнении работ (оказании услуг) в любое время при условии оплаты исполнителю фактически понесенных им расходов, связанных с исполнением обязательств по данному договору.
Из приведенных положений закона следует, что потребитель в любое время вправе отказаться от исполнения договора об оказании услуг и потребовать возврата уплаченных по договору сумм за вычетом фактически понесенных исполнителем расходов.
```

### 2. Определение ВС РФ по онлайн-курсам (ООО «ГикБрейнс»), новость РАПСИ 14.11.2024

> `https://rapsinews.ru/judicial_news/20241114/310406440.html` — `curl`, HTTP 200, 46 491 байт. Номер определения в новости не указан (в тексте — «в изученном РАПСИ определении»); первоисточник не открыт.

Дословно ключевое:

```
Если Вы согласны и дальше использовать файлы cookie, пожалуйста, нажмите кнопку «Подтвердить». Если не согласны - Вы можете изменить настройки своего браузера.
ВС защитил право вернуть оплату доступных, но непройденных уроков онлайн-курсов
С такими выводами согласились суд апелляционной инстанции и кассационный суд общей юрисдикции.
Потребитель вправе отказаться от исполнения договора об услуге, если им обнаружены существенные недостатки выполненной работы или иные существенные отступления от условий договора, напоминает ВС.
«При этом Закон о защите прав потребителей (ЗОЗПП) не предусматривает возможности определения цены, возвращаемой потребителю при отказе от исполнения договора в связи с существенными недостатками услуг, за вычетом стоимости фактически оказанных услуг», - разъясняет ВС.
```

**Раскладка для оферты FINPILOT (фактическая):** (а) при отказе без претензий к качеству — ст. 32 ЗоЗПП + п. 1 ст. 782 ГК: возврат уплаченного за вычетом фактически понесённых расходов, бремя доказывания расходов на исполнителе; для абонентского договора (ст. 429.4 ГК) — возврат за период, на который договор досрочно прекращён (п. 10 Обзора ВС за 2023 г., по пересказу). (б) Условие оферты «подписка — неделимая услуга, считается оказанной в момент оплаты/предоставления доступа» ВС отверг. (в) При существенных недостатках — возврат без вычета стоимости оказанного (ВС по делу ГикБрейнс; иная норма, не ст. 32). (г) Включение в оферту условия о невозврате — состав ч. 2 ст. 14.8 КоАП (юрлицу 10–20 тыс. руб.) и ничтожность условия по ст. 16 ЗоЗПП (норма ст. 16 в этом доборе не открывалась). Вывод «можно прописать пропорциональный возврат за оставшиеся дни и удержание документально подтверждённых расходов; нельзя — невозврат, неделимость, «замораживание» вместо возврата» — производный от текстов выше, юристом не сверен.

Другие публикации выдачи (сниппеты, не открывались): Управление Роспотребнадзора по Воронежской обл. `36.rospotrebnadzor.ru/news/29453` (HTTP 200, 59 577 байт, но в очищенном тексте только меню — тело новости рендерится иначе, НЕ ДОБЫТО); `zpp.rospotrebnadzor.ru/Forum/appeals/Details/57114`, `.../59162`, `.../59590` — ответы виртуальной приёмной, не открывались.


## ДОБОР Г1 — НК РФ ст. 149 п. 2 пп. 26: льгота по НДС на ПО и SaaS-подписка

> `https://legalacts.ru/kodeks/NK-RF-chast-2/razdel-viii/glava-21/statja-149/` — `curl -skL --http1.1`, HTTP 200, 205 933 байт (83 782 символа текста). На странице: «(ред. от 04.08.2026) (с изм. и доп., вступ. в силу с 01.09.2026)». Сверка с КонсультантПлюс не проводилась (окно 20–24 ч). Реквизиты законов-редакторов подпункта на legalacts вырезаны; по сниппету выдачи: упоминание лицензионного договора исключено с 01.01.2021 Федеральным законом от 31.07.2020 № 265-ФЗ (сниппет, закон не открыт).

Дословно (п. 2 ст. 149 — «Не подлежит налогообложению (освобождается от налогообложения) реализация (а также передача, выполнение, оказание для собственных нужд) на территории РФ…» — вводная фраза п. 2 по общеизвестному тексту, в этом доборе не выписана):

```
26) исключительных прав на программы для электронных вычислительных машин и базы данных, включенные в единый реестр российских программ для электронных вычислительных машин и баз данных и (или) единый реестр результатов научно-исследовательских, опытно-конструкторских и технологических работ военного, специального или двойного назначения, прав на использование таких программ и баз данных (включая обновления к ним и дополнительные функциональные возможности), в том числе путем предоставления удаленного доступа к ним через информационно-телекоммуникационную сеть, в том числе через информационно-телекоммуникационную сеть "Интернет".
Положения настоящего подпункта не применяются, если передаваемые права состоят в получении возможности распространять рекламную информацию в информационно-телекоммуникационной сети, в том числе в информационно-телекоммуникационной сети "Интернет", и (или) получать доступ к такой информации, размещать предложения (объявления) о приобретении (реализации) товаров (работ, услуг), имущественных прав в информационно-телекоммуникационной сети, в том числе в информационно-телекоммуникационной сети "Интернет", осуществлять поиск информации о потенциальных покупателях (продавцах) и (или) заключать сделки;
```

**Раскладка для FINPILOT (фактическая):** (1) условие — ПО включено в единый реестр российских программ (Минцифры); без реестра льготы нет; (2) лицензионный договор как условие в тексте подпункта больше не назван (сниппет: исключён с 2021); (3) **удалённый доступ через Интернет прямо охвачен** — «в том числе путем предоставления удаленного доступа к ним через… сеть „Интернет“», т.е. SaaS-подписка по тексту подпадает; (4) исключение второго абзаца (реклама, объявления, поиск покупателей/продавцов, заключение сделок) к СППР по личным финансам по буквальному тексту не относится — если в продукте не появится маркетплейс/витрина офферов; (5) сниппеты выдачи (rnk.ru «отмена льготы», pro-ability.ru о письме Минфина о доработке ПО, 06.05.2026) говорят о сужении практики применения в 2026 г. — не открывались, первоисточник Минфина не добыт. Вопрос, является ли подписка «правом на использование» (ст. 1235–1286 ГК) или услугой — толкованием не проверялся; условие реестра делает вопрос актуальным только после включения FINPILOT в реестр.


## ДОБОР Г1 — ПП РФ от 24.07.2025 № 1087: критерии отнесения к рекламе информации в Интернете

> Официальный текст: `http://publication.pravo.gov.ru/file/pdf?eoNumber=0001202507250057` (карточка `publication.pravo.gov.ru/document/0001202507250057`, опубликовано 25.07.2025), `curl -sk --http1.1`, HTTP 200, 1 051 800 байт, PDF без текстового слоя (pdftotext → 5 байт); 5 страниц прочитаны через `Read` постранично и расшифрованы вручную — дословно, но переписано со скана (опечатки переписки возможны). Подпись М. Мишустин, ЭП.
>
> 🔴 **Поправка к формулировке очереди:** постановление издано «в соответствии со статьей 18**²** Федерального закона "О рекламе"», а НЕ к ч. 3 ст. 18.1. Вступает в силу **со дня официального опубликования** (т.е. 25.07.2025). Отдельного ПП с критериями «к ч. 3 ст. 18.1» в выдаче не найдено; ПП от 25.05.2022 № 948 (сниппет) — критерии отнесения лиц к обязанным предоставлять информацию о рекламе в РКН, это другой предмет, текст не открывался.

Дословно:

```
1. Утвердить прилагаемые критерии отнесения к рекламе информации, распространяемой на отдельных информационных ресурсах в информационно-телекоммуникационной сети "Интернет".
2. Настоящее постановление вступает в силу со дня его официального опубликования.

КРИТЕРИИ отнесения к рекламе информации, распространяемой на отдельных информационных ресурсах в информационно-телекоммуникационной сети "Интернет"

1. Настоящий документ устанавливает критерии отнесения к рекламе информации, распространяемой на следующих информационных ресурсах (сайтах, и (или) страницах сайта в информационно-телекоммуникационной сети "Интернет", и (или) информационных системах, и (или) программах для электронных вычислительных машин в информационно-телекоммуникационной сети "Интернет" (далее - сеть "Интернет"):
информационные ресурсы, которые предоставляют потребителю в отношении определенного товара (услуги) возможность одновременно ознакомиться с предложением продавца (исполнителя) о заключении договора купли-продажи товара (договора возмездного оказания услуг), заключить с продавцом (исполнителем) договор купли-продажи (договор возмездного оказания услуг), а также произвести предварительную оплату указанного товара (услуги) путем наличных расчетов либо перевода денежных средств такому владельцу в рамках применяемых форм безналичных расчетов;
информационные ресурсы, которые предназначены и (или) используются для организации взаимодействия их пользователей между собой в целях купли-продажи, мены и (или) передачи в пользование движимого и (или) недвижимого имущества, выполнения работ, оказания услуг, поиска подходящей работы и (или) подбора необходимых работников за счет предоставления их пользователям возможности самостоятельно размещать объявления на государственном языке Российской Федерации, государственных языках республик в составе Российской Федерации или иных языках народов Российской Федерации о купле-продаже, мене и (или) передаче в пользование движимого и (или) недвижимого имущества, выполнении работ, об оказании услуг, о поиске подходящей работы и (или) подборе необходимых сотрудников, тематически сгруппированные в зависимости от содержания таких объявлений, а также за счет предоставления их пользователям возможности самостоятельно обращаться по таким объявлениям и доступ к которым в течение суток составляет в том числе более ста тысяч пользователей сети "Интернет", находящихся на территории Российской Федерации;
информационные ресурсы, которые предназначены и (или) используются их пользователями для предоставления и (или) распространения посредством созданных ими персональных страниц информации на государственном языке Российской Федерации, государственных языках республик в составе Российской Федерации или иных языках народов Российской Федерации, на которых может распространяться реклама, направленная на привлечение внимания потребителей, находящихся на территории Российской Федерации, и доступ к которым в течение суток составляет в том числе более пятисот тысяч пользователей сети "Интернет", находящихся на территории Российской Федерации;
информационные системы, осуществляющие по запросу пользователя поиск в сети "Интернет" информации определенного содержания и предоставляющие пользователю сведения об указателе страницы сайта в сети "Интернет" для доступа к запрашиваемой информации, расположенной на сайтах в сети "Интернет", принадлежащих иным лицам, за исключением информационных систем, используемых для осуществления государственных и муниципальных функций, оказания государственных и муниципальных услуг, а также для осуществления иных публичных полномочий, установленных федеральными законами.
2. Информация, распространяемая на информационных ресурсах (сайтах, и (или) страницах сайта в сети "Интернет", и (или) информационных системах, и (или) программах для электронных вычислительных машин), указанных в пункте 1 настоящего документа, относится к рекламе, если соответствует понятию "реклама", предусмотренному в пункте 1 статьи 3 Федерального закона "О рекламе", и отвечает в совокупности следующим критериям:
а) направлена на привлечение внимания к товару (работе, услуге), средству индивидуализации юридического лица и (или) товара, изготовителю или продавцу товара, результатам интеллектуальной деятельности либо мероприятию и формирование или поддержание интереса к ним и их продвижение на рынке;
б) не носит характер справочно-информационных или аналитических материалов. К справочно-информационным или аналитическим материалам относятся:
результаты поисковой выдачи, предоставляемые по запросу пользователя информационных ресурсов, указанных в абзацах первом - пятом пункта 1 настоящего документа, независимо от способа и формы предоставления таких результатов, а также признаков, указанных в абзаце третьем настоящего подпункта;
информация, включенная в каталог товаров (работ, услуг), то есть сгруппированная по определенным рубрикам без нарушения визуального единообразия и единого стиля представления информации в соответствующей рубрике, представляющая собой однотипный набор кратких информационных сведений о лицах и производимых или реализуемых ими товарах (выполняемых работах, оказываемых услугах);
информация о производимых товарах (выполняемых работах, оказываемых услугах), организуемых выставках и подобных мероприятиях, размещенная на информационном ресурсе производителя таких товаров (лица, выполняющего работы, оказывающего услуги), организатора таких мероприятий;
справочно-информационные материалы о товарах (работах, услугах) и (или) продавцах, производителях таких товаров (лицах, выполняющих работы, оказывающих услуги), которые предоставляются пользователю информационных ресурсов, указанных в абзацах первом - пятом пункта 1 настоящего документа, с учетом особенностей, предусмотренных статьей 10.2-2 Федерального закона "Об информации, информационных технологиях и о защите информации";
информация, представляющая собой личное мнение или отношение к какому-либо товару (работе, услуге) пользователей информационных ресурсов, указанных в абзаце четвертом пункта 1 настоящего документа, распространяемая такими пользователями посредством созданных ими персональных страниц на указанных информационных ресурсах, при условии, что данная информация не формирует интерес к какому-либо товару (работе, услуге), в том числе за счет чрезмерного описания товара (работы, услуги) и его достоинств, призывов к покупке;
в) не является объявлениями физических лиц или юридических лиц, не связанными с осуществлением предпринимательской деятельности. К объявлениям физических лиц или юридических лиц, не связанным с осуществлением предпринимательской деятельности, относятся размещенные на информационных ресурсах, указанных в абзацах первом - пятом пункта 1 настоящего документа:
сообщения о передаче вещей, животных безвозмездно;
сообщения о продаже физическими лицами принадлежащих им вещей, предназначенных для личного потребления;
отзывы (суждения, мнения), содержащие оценку товара (работы, услуги) и (или) продавца, производителя таких товаров (лица, выполняющего работы, оказывающего услуги), размещенные в соответствующих разделах информационного ресурса;
объявления работодателей о приеме на работу без размещения сведений, привлекающих внимание к конкретному товару (работе, услуге), лицу.
```

**Раскладка для FINPILOT (фактическая):** критерии применяются только к четырём видам ресурсов (маркетплейсы с оплатой, доски объявлений >100 тыс./сутки, соцсети с персональными страницами >500 тыс./сутки, поисковики). Сам FINPILOT ни к одному не относится → ПП 1087 к собственному сайту продукта напрямую не применяется; применяется к размещениям FINPILOT на чужих ресурсах этих видов (например, посевы в соцсетях). Любопытная связка: абзац о справочно-информационных материалах прямо отсылает к ст. 10.2-2 149-ФЗ (рекомендательные технологии).


## ДОБОР Г1 — Реквизиты действующей редакции ст. 28 38-ФЗ «Реклама финансовых услуг и финансовой деятельности»

> `https://www.consultant.ru/document/cons_doc_LAW_58968/0021818db8b93ae5fbd38076074a7182e157186c/` — `curl -skL --http1.1`, HTTP 200, 118 430 байт (18 020 символов текста; вопреки замеру сессии, в 16 ч по Москве статья отдана целиком, с редакционными пометками). Заголовок: «Федеральный закон от 13.03.2006 N 38-ФЗ (ред. от 04.08.2026)». Сверка: legalacts.ru, та же статья — HTTP 200, 71 247 байт, «(ред. от 04.08.2026)», без пометок.

Законы-редакторы, упомянутые в тексте ст. 28 (число упоминаний в пометках, по возрастанию даты):

```
   1 от 13.03.2006 N 38-ФЗ
   1 от 23.07.2013 N 251-ФЗ
   1 от 21.12.2013 N 375-ФЗ
   5 от 29.12.2014 N 460-ФЗ
   2 от 02.08.2019 N 259-ФЗ
   7 от 26.12.2024 N 479-ФЗ
   1 от 31.07.2025 N 337-ФЗ
```

Дословная пометка КонсультантПлюс: «…в соответствие с требованиями ст. 28 (в ред. ФЗ от 26.12.2024 N 479-ФЗ) до 01.09.2025» (договоры на распространение рекламы финуслуг, заключённые до 01.03.2025).

**Итог по реквизитам:** последний закон-редактор ст. 28 в пометках КонсультантПлюс — **Федеральный закон от 31.07.2025 № 337-ФЗ** (одна пометка); основной массив действующей редакции — **от 26.12.2024 № 479-ФЗ** (семь пометок, в силе с 01.03.2025 по той же пометке). Редакция всего закона — от 04.08.2026 (изменения 2026 г. в ст. 28, по пометкам, не вносились). Какую часть ст. 28 правил 337-ФЗ — по очищенному тексту не установлено.

## ДОБОР Г1 — Приказ РКН о требованиях к идентификатору рекламы (erid) и передаче в ОРД

> 🔴 **Смена акта:** Приказ РКН от 30.11.2022 № 191 (рег. Минюст 28.12.2022 № 71862) **утратил силу**; действующий — **Приказ Роскомнадзора от 25.03.2025 № 68** «Об утверждении Требований к идентификатору рекламы, идентификатору социальной рекламы, его содержанию, порядка и сроков его присвоения, размещения при распространении рекламы и (или) социальной рекламы в сети „Интернет“, хранения и предоставления в РКН», **рег. Минюст 14.04.2025 № 81842, в силе с 25.04.2025**, издан во исполнение ФЗ от 26.12.2024 № 479-ФЗ. Источник реквизитов — `https://ppt.ru/obzory/vstupaet-v-silu/prikaz-roskomnadzora-25-03-2025-68` (`curl`, HTTP 200, 294 095 байт) и совпадающие сниппеты выдачи WebSearch (КонсультантПлюс `cons_doc_LAW_503134`, garant.ru/hotlaw/federal/1809500/, Контур documentId=492969). Там же сниппет: одновременно издан **Приказ РКН от 25.03.2025 № 67** — требования к программам для учёта рекламы (не открывался).

Суть по обзору ppt.ru (вторичный источник, дословно):

```
Приказ Роскомнадзора от 25.03.2025 № 68 об утверждении Требований к идентификатору рекламы в интернете
Обновлены требования к идентификатору рекламы, порядку его присвоения, размещения и предоставления в Роскомнадзор при распространении рекламы в сети «Интернет». Приказ вступает в силу 25 апреля 2025 года.
Роскомнадзор утвердил новую систему цифровой идентификации рекламных материалов в сети «Интернет». Приказ определяет принципы маркировки всей рекламы, размещаемой в сети.
Документ устанавливает единую технологию присвоения уникальных цифровых кодов для каждого рекламного сообщения. Эта технология обеспечивает контроль за рекламными материалами и сбор статистической информации.
параметры и структуру цифровых идентификаторов;
сроки и порядок получения маркировки для рекламы;
правила размещения идентификационных данных в рекламных материалах;
процедуры хранения и передачи сведений об идентификаторах в контролирующие органы.
Документ разработан во исполнение Федерального закона от 26 декабря 2024 года № 479-ФЗ и заменяет приказ Роскомнадзора от 30 ноября 2022 года № 191.
Дата вступления в силу: 25 апреля 2025 года
```

Суть прежнего приказа № 191 по разбору INTELLECT (`intellectpro.ru/press/works/prikaz_rkn_ob_identifikatorah_reklamy/`, HTTP 200, 56 470 байт; вторичный, для преемственности — действующий № 68 мог изменить детали):

```
Что такое идентификатор рекламы и как его получить: инструкция для компаний.
Вся реклама в Интернете должна в обязательном порядке иметь идентификатор. В Приказе разъясняется порядок его получения и размещения.
    Задать вопрос                               
Роскомнадзор опубликовал последний из нормативно-правовых актов, необходимых для полноценного функционирования Единого реестра интернет-рекламы (далее — ЕРИР): требования к идентификатору рекламы, его содержанию, порядку и срокам его присвоения, размещению при распространении рекламы в Интернете (Приказ Роскомнадзора от 30.11.2022 №191, далее — Приказ).
Согласно документу, идентификатор рекламы — уникальное цифровое обозначение для отслеживания распространенной в Интернете рекламы и учета информации о ней. Этот идентификатор часто называют токеном. Выдаются такие токены операторами рекламных данных (ОРД).
Вся реклама в Интернете должна в обязательном порядке иметь такой идентификатор. И в Приказе Роскомнадзор раскрывает детали его получения и порядок размещения в рекламе.
Когда и как получать идентификатор
Получить идентификатор нужно до размещения рекламы. Это очень важный момент.
Исключение — реклама в стримах (то есть в прямых эфирах) или рекламная интеграция в аудиовизуальных произведениях — например, у блогеров. В таких случаях получение идентификатора возможно в течение месяца после распространения рекламы в составе видеоролика.
Технически процедура очень простая: в личном кабинете оператора рекламных данных вы загружаете креатив своей рекламы и моментально получаете этот самый уникальный буквенно-цифровой код. То есть буквально в пару кликов.
Где и как размещается идентификатор
Приказ предусматривает правила размещения токена в зависимости от формата рекламы.
По общему правилу рекламный идентификатор добавляется в конец кликовой ссылки и выглядит так: https://site.ru/?erid=base58(protobuf). В этом примере наименованием сайта в сети «Интернет» является «site.ru», а идентификатором рекламы — буквы и цифры 
Однако бывают ситуации, когда кликовой ссылки нет или по каким-то невозможно присовокупить к ней ERID, — например, в текстово-графических блоках или видеороликах. В этом случае идентификатор размещается в виде пометки «ERID: ххх»:
поверх текстово-графического блока,
```

**Раскладка для FINPILOT (фактическая):** порядок «креатив → ОРД → erid до распространения → размещение erid в ссылке или пометкой» касается любой платной рекламы FINPILOT в Интернете (посевы, таргет, интеграции у блогеров). Для блогерских интеграций по старому приказу — токен в течение месяца после выхода; сохранилось ли это в № 68 — не проверено.


## ДОБОР Г16 — Ж. Приказ Роскомнадзора от 25.03.2025 № 68 — Требования к идентификатору рекламы (дословно)

Акт: Приказ Роскомнадзора от 25.03.2025 № 68 «Об утверждении Требований к идентификатору рекламы, идентификатору социальной рекламы, его содержанию, порядка и сроков его присвоения, размещения при распространении рекламы и (или) социальной рекламы в сети „Интернет“, хранения и предоставления в Роскомнадзор» (cons_doc_LAW_503134; оглавление HTTP 200, 32 770 байт). По справке consultant/ppt.ru вступил в силу 25.04.2025, заменил приказ РКН от 30.11.2022 № 191, издан во исполнение 479-ФЗ от 26.12.2024 — это пересказ поисковой выдачи, текст приказной части ниже не снимался.


### Требования к идентификатору рекламы (утв. приказом РКН № 68) — полный текст

- Источник: https://www.consultant.ru/document/cons_doc_LAW_503134/015fd7066153336d870556327e00f8177ef5b5f2/
- Канал: curl -sk --http1.1 + браузерный UA, разбор HTML скриптом; HTTP/размер HTML: 200 / 47 259 байт; снято 12.09.2026 ~21:40 МСК
- Объём: полный текст статьи в действующей редакции (как отдал consultant.ru)

```text
Утверждены
приказом Федеральной службы
по надзору в сфере связи,
информационных технологий
и массовых коммуникаций
от 25 марта 2025 г. N 68
ТРЕБОВАНИЯ
К ИДЕНТИФИКАТОРУ РЕКЛАМЫ, ИДЕНТИФИКАТОРУ СОЦИАЛЬНОЙ
РЕКЛАМЫ, ЕГО СОДЕРЖАНИЮ, ПОРЯДОК И СРОКИ ЕГО ПРИСВОЕНИЯ,
РАЗМЕЩЕНИЯ ПРИ РАСПРОСТРАНЕНИИ РЕКЛАМЫ И (ИЛИ) СОЦИАЛЬНОЙ
РЕКЛАМЫ В ИНФОРМАЦИОННО-ТЕЛЕКОММУНИКАЦИОННОЙ СЕТИ
"ИНТЕРНЕТ", ХРАНЕНИЯ И ПРЕДОСТАВЛЕНИЯ В ФЕДЕРАЛЬНУЮ
СЛУЖБУ ПО НАДЗОРУ В СФЕРЕ СВЯЗИ, ИНФОРМАЦИОННЫХ
ТЕХНОЛОГИЙ И МАССОВЫХ КОММУНИКАЦИЙ
1. Идентификатор рекламы и (или) идентификатор социальной рекламы представляют собой уникальное цифровое обозначение, предназначенное для обеспечения прослеживаемости распространенной в информационно-телекоммуникационной сети "Интернет" <1> рекламы и (или) социальной рекламы и учета информации о таких рекламе и (или) социальной рекламе <2>.
--------------------------------
<1> Далее - сеть "Интернет".
<2> Часть 17 статьи 18.1 Федерального закона от 13 марта 2006 г. N 38-ФЗ "О рекламе" (далее - Федеральный закон "О рекламе"). Далее - идентификатор.
2. Идентификатор формируется с применением программ для электронных вычислительных машин, используемых операторами рекламных данных для установления факта распространения рекламы и (или) социальной рекламы в сети "Интернет" <3>.
--------------------------------
<3> Далее - программа.
3. Присвоение идентификатора осуществляется оператором рекламных данных незамедлительно до распространения рекламы и (или) социальной рекламы в сети "Интернет" рекламодателем, рекламораспространителем, лицами, указанными в части 3.13 статьи 10 Федерального закона "О рекламе", или оператором рекламной системы после передачи рекламы и (или) социальной рекламы в программу.
4. Оператор рекламных данных должен предоставить присвоенный идентификатор в Федеральную службу по надзору в сфере связи, информационных технологий и массовых коммуникаций <4> в соответствии с протоколом об информационном взаимодействии, предусмотренным пунктом 6 Правил взаимодействия Федеральной службы по надзору в сфере связи, информационных технологий и массовых коммуникаций с операторами рекламных данных, включая порядок, формат и сроки предоставления в Федеральную службу по надзору в сфере связи, информационных технологий и массовых коммуникаций информации о распространенной в информационно-телекоммуникационной сети "Интернет" рекламе, утвержденных постановлением Правительства Российской Федерации от 28 мая 2022 г. N 974 <5>.
--------------------------------
<4> Далее - уполномоченный орган.
<5> Далее соответственно - протокол, Правила. В соответствии с пунктом 2 постановления Правительства Российской Федерации от 28 мая 2022 г. N 974 данный акт действует до 1 сентября 2028 г.
5. Идентификатор предоставляется оператором рекламных данных в информационную систему радиочастотной службы, обеспечивающую осуществление организационных и технических мер, необходимых для реализации уполномоченным органом полномочий по учету, хранению и обработке информации о рекламе в соответствии с частью 2 статьи 18.1 Федерального закона "О рекламе" <6>.
--------------------------------
<6> Далее - информационная система. Часть 9 статьи 18.1 Федерального закона "О рекламе", подпункт "е" пункта 4, подпункты "я", "я(3)" пункта 5 Положения о радиочастотной службе, утвержденного постановлением Правительства Российской Федерации от 14 мая 2014 г. N 434, пункт 3 Правил. Далее - информационная система.
6. Идентификатор передается в информационную систему вместе с кодом оператора рекламных данных, который присваивается оператору рекламных данных при регистрации в информационной системе.
7. Идентификатор должен включать произвольный набор цифр, состоящий из совокупности цифровых обозначений.
8. Оператор рекламных данных может дополнять идентификатор буквенными обозначениями.
9. Рекламодатель, рекламораспространитель, оператор рекламной системы, лица, указанные в части 3.13 статьи 10 Федерального закона "О рекламе", должны осуществлять размещение идентификатора, переданного от оператора рекламных данных и кодированного им в протокол сериализации (передачи) структурированных данных в форме буквенно-цифрового текста на основе букв латинского языка.
10. Идентификатор рекламы должен представлять собой набор байтов или буквенно-цифрового текста на основе букв латинского языка, присоединяемых к указателю страницы сайта в сети "Интернет" в виде: https://site.ru/?erid=base58(protobuf), где "site.ru" - наименование сайта в сети "Интернет", а "erid" - наименование идентификатора рекламы, который передается серверу посредством ссылки <7>.
--------------------------------
<7> Далее - техническая ссылка.
11. Допускается размещение идентификатора в начале или в конце текстового блока, поверх текстово-графического блока, в начале и (или) поверх видеоролика в виде пометки "erid: xxx", где "erid" включает наименование идентификатора, а "xxx" - набор буквенно-цифрового текста на основе букв латинского языка.
12. Идентификатор, содержащийся в контрастной текстовому блоку, текстово-графическому блоку или видеоролику пометке "erid: xxx", должен быть доступен для визуализации, в том числе посредством использования программных средств.
13. В целях обеспечения размещения идентификатора при распространении рекламы и (или) социальной рекламы в сети "Интернет" оператором рекламных данных в протокол могут включаться иные технические характеристики идентификатора, разрабатываемые исходя из формы распространения рекламы и (или) социальной рекламы.
14. Оператор рекламных данных должен хранить идентификаторы, присвоенные распространенным в сети "Интернет" рекламе и (или) социальной рекламе, в течение года со дня их присвоения.
15. В целях хранения идентификаторов оператор рекламной системы, оператор рекламных данных (в случае использования ими в указателе страницы сайта в сети "Интернет" кодированной технической ссылки) должны предоставлять в информационную систему коды декодирования технической ссылки.
```


## ДОБОР Г16 — З. Обзор судебной практики ВС РФ по делам о защите прав потребителей (утв. Президиумом ВС РФ 18.10.2023), пп. 10 и 11 (дословно)

- Источник: https://base.garant.ru/407853829/ (ГАРАНТ, публичная страница документа)
- Канал: curl -sk --http1.1 + браузерный UA, HTML в cp1251, разбор скриптом; HTTP 200, 191 103 байт; снято 12.09.2026 ~21:50 МСК
- consultant.ru: номер документа поиском в окне не найден, см. ниже
- Объём: пп. 10 и 11 целиком (п. 11 — до начала п. 12). Переносы строк внутри ссылок на статьи склеены; надстрочные индексы статей ГК (429⁴, 429³) Гарант отдаёт отдельной строкой — видны как «429 4».
- Определение СК по гражданским делам ВС РФ от 23.08.2022 № 41-КГ22-23-К4 цитируется в п. 10 как основание. Отдельный текст определения: garant.ru/products/ipo/prime/doc/405296547/ — HTTP 403 (902 байта), не добыт этим каналом.

```text
10. Потребитель в случае отказа от исполнения абонентского договора вправе требовать возврата денежных сумм, уплаченных за период действия договора, на который он досрочно прекращен.
П. обратился в суд с иском к обществу (исполнителю) о защите прав потребителя, указав, что в процессе оформления кредита на приобретение автомобиля ему была навязана дополнительная услуга "Техническая помощь на дороге", исполнителем которой является ответчик. Денежные средства в размере 255 000 руб. за указанную услугу списаны банком с кредитного счета истца.
Заявление потребителя о расторжении договора и возврате уплаченных денежных средств общество оставило без удовлетворения.
Решением суда иск П. удовлетворен частично.
Суд апелляционной инстанции, отменяя решение суда и принимая по делу новое решение об отказе в иске, сослался на то, что истец вступил в отношения с обществом (ответчиком по делу) только относительно услуг по оказанию технической помощи на дороге, при этом денежные средства в размере 255 000 руб. уплачены П. автосалону (продавцу), а следовательно, оснований для их взыскания с общества не имеется.
С данными выводами суда апелляционной инстанции согласился кассационный суд общей юрисдикции.
Судебная коллегия по гражданским делам Верховного Суда отменила состоявшиеся по делу постановления судов апелляционной и кассационной инстанций в связи со следующим. Согласно  пункту 1 статьи 429  4
 ГК РФ договором с исполнением по требованию (абонентским договором) признается договор, предусматривающий внесение одной из сторон (абонентом) определенных, в том числе периодических, платежей или иного предоставления за право требовать от другой стороны (исполнителя) предоставления предусмотренного договором исполнения в затребованных количестве или объеме либо на иных условиях, определяемых абонентом. В соответствии с  пунктом 1 статьи 779
 ГК РФ по договору возмездного оказания услуг исполнитель обязуется по заданию заказчика оказать услуги (совершить определенные действия или осуществить определенную деятельность), а заказчик обязуется оплатить эти услуги.
На отношения, связанные с заключением договоров об оказании услуг, стороной которых является гражданин, использующий услугу в личных целях, распространяются положения о защите прав потребителей. В силу  статьи 32  Закона о защите прав потребителей и  пункта 1 статьи 782
 ГК РФ потребитель вправе отказаться от исполнения договора о выполнении работ (оказании услуг) в любое время при условии оплаты исполнителю фактически понесенных им расходов, связанных с исполнением обязательств по данному договору.
Из приведенных положений закона следует, что потребитель в любое время вправе отказаться от исполнения договора об оказании услуг и потребовать возврата уплаченных по договору сумм за вычетом фактически понесенных исполнителем расходов.
Обязанность доказать наличие таких расходов и их размер в данном случае возлагается на исполнителя.
Если имеет место абонентский договор на оказание услуг, то потребитель имеет право требовать возврата денежных сумм, уплаченных за тот период действия договора, на который он досрочно прекращен.
По данному делу суд апелляционной инстанции, отказав потребителю в возврате уплаченных по договору денежных сумм, названные положения закона не учел.
Кроме того, Судебная коллегия по гражданским делам Верховного Суда указала, что суд апелляционной инстанции, ссылаясь на уплату денежных средств за услугу не ответчику, а автосалону, в нарушение положений  части 2 статьи 56  и  статьи 196
 ГПК РФ не определил все имеющие значение для правильного разрешения спора обстоятельства и правоотношения сторон, в частности не определил, от чьего имени и за чей счет заключался договор на оказание услуг со стороны исполнителя. Определение
 Судебной коллегии по гражданским делам Верховного Суда от 23 августа 2022 г. N 41-КГ22-23-К4.
11. Условие договора, согласно которому у потребителя при отказе от исполнения договора отсутствует или ограничивается право на возврат уплаченных денежных средств, является недействительным, как ущемляющее права потребителя.
К. обратился в суд с иском к обществу-1 (исполнителю) о взыскании уплаченных по договору денежных средств и штрафа за несоблюдение в добровольном порядке удовлетворения требований потребителя.
Судом по делу установлено, что 9 октября 2021 г. К. (покупатель) заключил с обществом-2 (продавец) договор купли-продажи автомобиля и дополнительное соглашение к нему.
11 октября 2021 г. между К. (заказчик) и обществом-1 (исполнитель, ответчик по делу) подписан договор, в рамках которого между сторонами заключен абонентский договор на обслуживание автомобиля и опционный договор на право требования денежных платежей в соответствии со  статьями 429  3  и  429  4  ГК РФ.
По абонентскому договору исполнителем заказчику за плату предоставляется абонентское обслуживание - право получения в порядке и на условиях, указанных в приложении к договору, следующих услуг: "аварийный комиссар, получение справок из МВД, получение справки из Гидрометцентра, независимая экспертиза недвижимого имущества и автотранспорта, доставка документов, круглосуточная эвакуация автомобиля, техническая помощь, юридическая консультация по недвижимости и по транспорту, трезвый водитель, трансферт, поиск автомобиля, персональный менеджер".
По опционному договору заказчик получает право требования от исполнителя денежных платежей в адрес любой из указанных в нем станций технического обслуживания автомобилей (бенефициара).
Исполнитель выдает заказчику независимую гарантию, в соответствии с которой станция технического обслуживания автомобилей, указанная как бенефициар в независимой гарантии, где заказчик будет осуществлять техническое обслуживание транспортного средства, получает право требования от исполнителя денежных средств на оплату технического обслуживания автомобиля заказчика в сумме и на условиях, изложенных в независимой гарантии.
В договоре от 11 октября 2021 г. указано, что общая цена договора составляет 150 000 руб. и складывается из цены абонентского обслуживания в размере 45 000 руб. и цены опционного договора - 105 000 руб. Договор действует с 11 октября 2021 г. по 10 октября 2026 г.
11 октября 2021 г. ответчик выдал истцу независимую гарантию на срок с 11 октября 2021 г. по 10 октября 2026 г. с суммой гарантии 367 500 руб., по условиям которой она обеспечивает исполнение принципалом основного обязательства перед бенефициаром по договору о плановом техническом обслуживании транспортного средства.
13 октября 2021 г. К. направил в адрес общества-1 претензию об отказе от исполнения договора и о возврате уплаченных по нему денежных средств.
18 ноября 2021 г. ответчик возвратил истцу часть платы за абонентское обслуживание за неиспользованный период в размере 44 827,45 руб., в удовлетворении остальных изложенных в претензии требований отказал.
Удовлетворяя иск, суд первой инстанции исходил из того, что истец как потребитель вправе отказаться от договора и потребовать возврата уплаченных по нему денежных средств в полном объеме, поскольку ответчик в части, касающейся опционного договора, каких-либо расходов по его исполнению не понес.
Отменяя решение суда и принимая новое решение об отказе в иске, суд апелляционной инстанции указал, что условиями договора, с которыми истец был ознакомлен и согласен, не предусмотрен возврат платежа при прекращении опционного договора. При этом суд апелляционной инстанции исходил из того, что условие опционного договора о невозврате платежа не ущемляет права потребителя, поскольку это прямо предусмотрено законом.
Кассационный суд общей юрисдикции оставил  апелляционное определение  без изменения.
Судебная коллегия по гражданским делам Верховного Суда с выводами судов апелляционной и кассационной инстанций не согласилась в связи со следующим.
Договор должен соответствовать обязательным для сторон правилам, установленным законом и иными правовыми актами (императивным нормам), действующим в момент его заключения ( пункт 1 статьи 422  ГК РФ). В  пункте 1 статьи 168
 ГК РФ закреплено, что, за исключением случаев, предусмотренных  пунктом 2
 этой статьи или иным законом, сделка, нарушающая требования закона или иного правового акта, является оспоримой, если из закона не следует, что должны применяться другие последствия нарушения, не связанные с недействительностью сделки. Сделка, нарушающая требования закона или иного правового акта и при этом посягающая на публичные интересы либо права и охраняемые законом интересы третьих лиц, ничтожна, если из закона не следует, что такая сделка оспорима или должны применяться другие последствия нарушения, не связанные с недействительностью сделки (пункт 2). В силу  пункта 1 статьи 16
 Закона о защите прав потребителей недопустимыми условиями договора, ущемляющими права потребителя, являются условия, которые нарушают правила, установленные международными договорами Российской Федерации, данным законом, законами и принимаемыми в соответствии с ними иными нормативными правовыми актами Российской Федерации, регулирующими отношения в области защиты прав потребителей. Недопустимые условия договора, ущемляющие права потребителя, ничтожны.
Если включение в договор условий, ущемляющих права потребителя, повлекло причинение убытков потребителю, они подлежат возмещению продавцом (изготовителем, исполнителем, импортером, владельцем агрегатора) в полном объеме в соответствии со  статьей 13  данного закона. Согласно  пункту 2
 названной статьи к недопустимым условиям договора, ущемляющим права потребителя, в том числе относятся:
условия, которые устанавливают для потребителя штрафные санкции или иные обязанности, препятствующие свободной реализации права, установленного  статьей 32  этого закона ( подпункт 3 );
иные условия, нарушающие правила, установленные международными договорами Российской Федерации, данным законом, законами и принимаемыми в соответствии с ними иными нормативными правовыми актами Российской Федерации, регулирующими отношения в области защиты прав потребителей ( подпункт 15 ). Пунктом 76
 постановления Пленума Верховного Суда от 23 июня 2015 г. N 25 "О применении судами некоторых положений раздела I части первой Гражданского кодекса Российской Федерации" 8
 разъяснено, что ничтожными являются условия сделки, заключенной с потребителем, не соответствующие актам, содержащим нормы гражданского права, обязательные для сторон при заключении и исполнении публичных договоров ( статья 3 ,  пункты 4  и  5 статьи 426
 ГК РФ), а также условия сделки, при совершении которой был нарушен явно выраженный законодательный запрет ограничения прав потребителей (например,  пункт 2 статьи 16  Закона о защите прав потребителей,  статья 29
 Федерального закона от 2 декабря 1990 г. N 395-I "О банках и банковской деятельности").
Названные требования закона и разъяснения Пленума Верховного Суда судом апелляционной инстанции при рассмотрении спора не применены, в связи с чем условие договора об отсутствии у заказчика права требовать возврата платежа при отказе от исполнения договора надлежащей оценки не получило. Определение
 Судебной коллегии по гражданским делам Верховного Суда от 11 июля 2023 г. N 5-КГ23-57-К2.
```


## ДОБОР Г16 — Л (часть 1). 149-ФЗ ст. 10.2-2 — норма, на которой стоят «правила применения рекомендательных технологий» (дословно)

Акт: Федеральный закон от 27.07.2006 № 149-ФЗ «Об информации, информационных технологиях и о защите информации», последняя редакция по consultant.ru на 12.09.2026 (cons_doc_LAW_61798).


### 149-ФЗ, ст. 10.2-2 «Особенности предоставления информации с применением рекомендательных технологий»

- Источник: https://www.consultant.ru/document/cons_doc_LAW_61798/2a69c627d62738291fe0a0fd4c1253385e730784/
- Канал: curl -sk --http1.1 + браузерный UA, разбор HTML скриптом; HTTP/размер HTML: 200 / 67 085 байт; снято 12.09.2026 ~21:40 МСК
- Объём: полный текст статьи в действующей редакции (как отдал consultant.ru)

```text
Статья 10.2-2. Особенности предоставления информации с применением рекомендательных технологий
(введена Федеральным законом от 31.07.2023 N 408-ФЗ)
1. Владелец сайта и (или) страницы сайта в сети "Интернет", и (или) информационной системы, и (или) программы для электронных вычислительных машин, на которых применяются информационные технологии предоставления информации на основе сбора, систематизации и анализа сведений, относящихся к предпочтениям пользователей сети "Интернет", находящихся на территории Российской Федерации (далее - владелец информационного ресурса, на котором применяются рекомендательные технологии), обязан соблюдать требования законодательства Российской Федерации, в частности:
1) не допускать применение информационных технологий предоставления информации на основе сбора, систематизации и анализа сведений, относящихся к предпочтениям пользователей сети "Интернет", находящихся на территории Российской Федерации (далее - рекомендательные технологии), которые нарушают права и законные интересы граждан и организаций, а также не допускать применение рекомендательных технологий в целях предоставления информации с нарушением законодательства Российской Федерации;
2) не допускать предоставление информации с применением рекомендательных технологий без информирования пользователей сети "Интернет" о применении на данном сайте и (или) странице сайта в сети "Интернет", и (или) в информационной системе, и (или) в программе для электронных вычислительных машин рекомендательных технологий. Требования к содержанию информации о применении рекомендательных технологий и размещению такой информации на информационном ресурсе устанавливаются федеральным органом исполнительной власти, осуществляющим функции по контролю и надзору в сфере средств массовой информации, массовых коммуникаций, информационных технологий и связи;
3) разместить на информационном ресурсе, на котором применяются рекомендательные технологии, документ, устанавливающий правила применения рекомендательных технологий;
4) разместить на информационном ресурсе, на котором применяются рекомендательные технологии, адрес электронной почты для направления ему юридически значимых сообщений, свои фамилию и инициалы (для физического лица) или наименование (для юридического лица).
2. Правила применения рекомендательных технологий должны содержать:
1) описание процессов и методов сбора, систематизации, анализа сведений, относящихся к предпочтениям пользователей сети "Интернет", предоставления информации на основе этих сведений, а также способов осуществления таких процессов и методов;
2) виды сведений, относящихся к предпочтениям пользователей сети "Интернет", которые используются для предоставления информации с применением рекомендательных технологий, источники получения таких сведений.
3. Правила применения рекомендательных технологий должны быть размещены на информационном ресурсе, на котором применяются рекомендательные технологии, на русском языке. Владелец информационного ресурса, на котором применяются рекомендательные технологии, должен обеспечить беспрепятственный и безвозмездный доступ пользователей сети "Интернет" к правилам применения рекомендательных технологий.
4. В случае обнаружения в сети "Интернет" информационного ресурса, на котором рекомендательные технологии применяются с признаками нарушения требований, предусмотренных пунктами 1 и 2 части 1 настоящей статьи, федеральный орган исполнительной власти, осуществляющий функции по контролю и надзору в сфере средств массовой информации, массовых коммуникаций, информационных технологий и связи, вправе запрашивать у владельца информационного ресурса, на котором применяются рекомендательные технологии, информацию, связанную с применением рекомендательных технологий, а также доступ к программно-техническим средствам рекомендательных технологий для проведения оценки соответствия применения рекомендательных технологий требованиям настоящей статьи. Указанное лицо обязано предоставлять запрашиваемую информацию и доступ к программно-техническим средствам не позднее чем в течение десяти дней со дня получения запроса федерального органа исполнительной власти, осуществляющего функции по контролю и надзору в сфере средств массовой информации, массовых коммуникаций, информационных технологий и связи.
5. В случае установления факта неисполнения владельцем информационного ресурса, на котором применяются рекомендательные технологии, обязанностей, предусмотренных настоящей статьей, федеральный орган исполнительной власти, осуществляющий функции по контролю и надзору в сфере средств массовой информации, массовых коммуникаций, информационных технологий и связи, направляет указанному лицу уведомление, содержащее требование принять меры по устранению выявленного нарушения. Владелец информационного ресурса, на котором применяются рекомендательные технологии, обязан принять меры по устранению указанного в уведомлении нарушения не позднее чем через десять дней со дня получения уведомления или в иной, установленный в уведомлении срок.
6. В случае непринятия владельцем информационного ресурса, на котором применяются рекомендательные технологии, мер, указанных в части 5 настоящей статьи, федеральный орган исполнительной власти, осуществляющий функции по контролю и надзору в сфере средств массовой информации, массовых коммуникаций, информационных технологий и связи, незамедлительно направляет указанному лицу требование о прекращении предоставления информации с применением рекомендательных технологий.
7. В течение суток с момента получения требования, указанного в части 6 настоящей статьи, владелец информационного ресурса, на котором применяются рекомендательные технологии, обязан прекратить предоставление информации с применением рекомендательных технологий.
8. В случае неисполнения владельцем информационного ресурса, на котором применяются рекомендательные технологии, требования о прекращении предоставления информации с применением рекомендательных технологий федеральный орган исполнительной власти, осуществляющий функции по контролю и надзору в сфере средств массовой информации, массовых коммуникаций, информационных технологий и связи, незамедлительно направляет по системе взаимодействия операторам связи требование о принятии мер по ограничению доступа к информационному ресурсу, на котором применяются рекомендательные технологии. Данное требование должно содержать доменное имя сайта в сети "Интернет", сетевой адрес, указатели страниц сайта в сети "Интернет", позволяющие идентифицировать такой информационный ресурс.
9. После получения по системе взаимодействия требования федерального органа исполнительной власти, осуществляющего функции по контролю и надзору в сфере средств массовой информации, массовых коммуникаций, информационных технологий и связи, о принятии мер по ограничению доступа оператор связи, оказывающий услуги по предоставлению доступа к информационно-телекоммуникационной сети "Интернет", обязан незамедлительно ограничить доступ к информационному ресурсу, указанному в части 8 настоящей статьи, за исключением случая, предусмотренного абзацем третьим пункта 5.1 статьи 46 Федерального закона от 7 июля 2003 года N 126-ФЗ "О связи".
10. В случае, если владелец информационного ресурса, на котором применяются рекомендательные технологии, принял меры, указанные в части 5 настоящей статьи, он направляет уведомление об этом в федеральный орган исполнительной власти, осуществляющий функции по контролю и надзору в сфере средств массовой информации, массовых коммуникаций, информационных технологий и связи. Такое уведомление может быть направлено также в электронном виде.
11. После получения уведомления, указанного в части 10 настоящей статьи, и проверки его достоверности федеральный орган исполнительной власти, осуществляющий функции по контролю и надзору в сфере средств массовой информации, массовых коммуникаций, информационных технологий и связи, обязан незамедлительно уведомить по системе взаимодействия оператора связи, оказывающего услуги по предоставлению доступа к информационно-телекоммуникационной сети "Интернет", о возобновлении доступа к информационному ресурсу, на котором применяются рекомендательные технологии.
12. После получения уведомления, указанного в части 11 настоящей статьи, оператор связи незамедлительно возобновляет доступ к информационному ресурсу, на котором применяются рекомендательные технологии, за исключением случая, предусмотренного частью 13 настоящей статьи.
13. В случае, если доступ к информационному ресурсу, на котором применяются рекомендательные технологии, был ограничен федеральным органом исполнительной власти, осуществляющим функции по контролю и надзору в сфере средств массовой информации, массовых коммуникаций, информационных технологий и связи, в соответствии с абзацем третьим пункта 5.1 статьи 46 Федерального закона от 7 июля 2003 года N 126-ФЗ "О связи", возобновление доступа к информационному ресурсу, на котором применяются рекомендательные технологии, осуществляется данным органом после получения уведомления, указанного в части 10 настоящей статьи, и проверки его достоверности.
14. Порядок взаимодействия федерального органа исполнительной власти, осуществляющего функции по контролю и надзору в сфере средств массовой информации, массовых коммуникаций, информационных технологий и связи, с владельцами информационных ресурсов, на которых применяются рекомендательные технологии, устанавливается указанным федеральным органом исполнительной власти.
15. Положения настоящей статьи не распространяются на операторов государственных информационных систем, государственные органы и органы местного самоуправления.
16. Нарушение владельцем информационного ресурса, на котором применяются рекомендательные технологии, требований настоящей статьи влечет за собой уголовную, административную и иную ответственность в соответствии с законодательством Российской Федерации.
```


### З — сверка по первоисточнику consultant.ru (тот же Обзор, пп. 10–11)

- Источник: https://www.consultant.ru/document/cons_doc_LAW_460140/e0449550c512c26e841f7eb5b84b85c51f388883/ (раздел «Разрешение споров о защите прав потребителей, связанных с реализацией товаров, выполнением работ (оказанием услуг)»; документ cons_doc_LAW_460140, «утв. Президиумом Верховного Суда РФ 18.10.2023»)
- Канал: curl -sk --http1.1 + браузерный UA; HTTP 200, 214 562 байт HTML, 82 776 знаков текста раздела; снято 12.09.2026 ~21:45 МСК
- Сверка с копией ГАРАНТ выше: совпадение 98,5 % по знакам без пробелов; расхождения только редакционные — у consultant сокращения «п.», «ст.», «ГК РФ», у Гаранта полные «пункту», «статьи»; по существу правовой позиции расхождений не найдено. Цитировать — по этой копии.

```text
10. Потребитель в случае отказа от исполнения абонентского договора вправе требовать возврата денежных сумм, уплаченных за период действия договора, на который он досрочно прекращен.
П. обратился в суд с иском к обществу (исполнителю) о защите прав потребителя, указав, что в процессе оформления кредита на приобретение автомобиля ему была навязана дополнительная услуга "Техническая помощь на дороге", исполнителем которой является ответчик. Денежные средства в размере 255 000 руб. за указанную услугу списаны банком с кредитного счета истца.
Заявление потребителя о расторжении договора и возврате уплаченных денежных средств общество оставило без удовлетворения.
Решением суда иск П. удовлетворен частично.
Суд апелляционной инстанции, отменяя решение суда и принимая по делу новое решение об отказе в иске, сослался на то, что истец вступил в отношения с обществом (ответчиком по делу) только относительно услуг по оказанию технической помощи на дороге, при этом денежные средства в размере 255 000 руб. уплачены П. автосалону (продавцу), а следовательно, оснований для их взыскания с общества не имеется.
С данными выводами суда апелляционной инстанции согласился кассационный суд общей юрисдикции.
Судебная коллегия по гражданским делам Верховного Суда РФ отменила состоявшиеся по делу постановления судов апелляционной и кассационной инстанций в связи со следующим.
Согласно п. 1 ст. 429.4 ГК РФ договором с исполнением по требованию (абонентским договором) признается договор, предусматривающий внесение одной из сторон (абонентом) определенных, в том числе периодических, платежей или иного предоставления за право требовать от другой стороны (исполнителя) предоставления предусмотренного договором исполнения в затребованных количестве или объеме либо на иных условиях, определяемых абонентом.
В соответствии с п. 1 ст. 779 ГК РФ по договору возмездного оказания услуг исполнитель обязуется по заданию заказчика оказать услуги (совершить определенные действия или осуществить определенную деятельность), а заказчик обязуется оплатить эти услуги.
На отношения, связанные с заключением договоров об оказании услуг, стороной которых является гражданин, использующий услугу в личных целях, распространяются положения законодательства о защите прав потребителей.
В силу ст. 32 Закона о защите прав потребителей и п. 1 ст. 782 ГК РФ потребитель вправе отказаться от исполнения договора о выполнении работ (оказании услуг) в любое время при условии оплаты исполнителю фактически понесенных им расходов, связанных с исполнением обязательств по данному договору.
Из приведенных положений закона следует, что потребитель в любое время вправе отказаться от исполнения договора об оказании услуг и потребовать возврата уплаченных по договору сумм за вычетом фактически понесенных исполнителем расходов.
Обязанность доказать наличие таких расходов и их размер в данном случае возлагается на исполнителя.
Если имеет место абонентский договор на оказание услуг, то потребитель имеет право требовать возврата денежных сумм, уплаченных за тот период действия договора, на который он досрочно прекращен.
По данному делу суд апелляционной инстанции, отказав потребителю в возврате уплаченных по договору денежных сумм, названные положения закона не учел.
Кроме того, Судебная коллегия по гражданским делам Верховного Суда РФ указала, что суд апелляционной инстанции, ссылаясь на уплату денежных средств за услугу не ответчику, а автосалону, в нарушение положений ч. 2 ст. 56 и ст. 196 ГПК РФ не определил все имеющие значение для правильного разрешения спора обстоятельства и правоотношения сторон, в частности не определил, от чьего имени и за чей счет заключался договор на оказание услуг со стороны исполнителя.
(Определение Судебной коллегии по гражданским делам Верховного Суда РФ от 23 августа 2022 г. N 41-КГ22-23-К4)
11. Условие договора, согласно которому у потребителя при отказе от исполнения договора отсутствует или ограничивается право на возврат уплаченных денежных средств, является недействительным, как ущемляющее права потребителя.
К. обратился в суд с иском к обществу-1 (исполнителю) о взыскании уплаченных по договору денежных средств и штрафа за несоблюдение в добровольном порядке удовлетворения требований потребителя.
Судом по делу установлено следующее.
9 октября 2021 г. К. (покупатель) заключил с обществом-2 (продавец) договор купли-продажи автомобиля и дополнительное соглашение к нему.
11 октября 2021 г. между К. (заказчик) и обществом-1 (исполнитель, ответчик по делу) подписан договор, в рамках которого между сторонами заключены абонентский договор на обслуживание автомобиля и опционный договор на право требования денежных платежей в соответствии со ст. ст. 429.3 и 429.4 ГК РФ.
По абонентскому договору исполнителем заказчику за плату предоставляется абонентское обслуживание - право получения в порядке и на условиях, указанных в приложении к договору, следующих услуг: "аварийный комиссар, получение справок из МВД, получение справки из Гидрометцентра, независимая экспертиза недвижимого имущества и автотранспорта, доставка документов, круглосуточная эвакуация автомобиля, техническая помощь, юридическая консультация по недвижимости и по транспорту, трезвый водитель, трансфер, поиск автомобиля, персональный менеджер".
По опционному договору заказчик получает право требования от исполнителя денежных платежей в адрес любой из указанных в нем станций технического обслуживания автомобилей (бенефициара).
Исполнитель выдает заказчику независимую гарантию, в соответствии с которой станция технического обслуживания автомобилей, указанная как бенефициар в независимой гарантии, где заказчик будет осуществлять техническое обслуживание транспортного средства, получает право требования от исполнителя денежных средств на оплату технического обслуживания автомобиля заказчика в сумме и на условиях, изложенных в независимой гарантии.
В договоре от 11 октября 2021 г. указано, что общая цена договора составляет 150 000 руб. и складывается из цены абонентского обслуживания в размере 45 000 руб. и цены опционного договора - 105 000 руб. Договор действует с 11 октября 2021 г. по 10 октября 2026 г.
11 октября 2021 г. ответчик выдал истцу независимую гарантию на срок с 11 октября 2021 г. по 10 октября 2026 г. с суммой гарантии 367 500 руб., по условиям которой она обеспечивает исполнение принципалом основного обязательства перед бенефициаром по договору о плановом техническом обслуживании транспортного средства.
13 октября 2021 г. К. направил в адрес общества-1 претензию об отказе от исполнения договора и о возврате уплаченных по нему денежных средств.
18 ноября 2021 г. ответчик возвратил истцу часть платы за абонентское обслуживание за неиспользованный период в размере 44 827 руб., в удовлетворении остальных изложенных в претензии требований отказал.
Удовлетворяя иск, суд первой инстанции исходил из того, что истец как потребитель вправе отказаться от договора и потребовать возврата уплаченных по нему денежных средств в полном объеме, поскольку ответчик в части, касающейся опционного договора, каких-либо расходов по его исполнению не понес.
Отменяя решение суда и принимая новое решение об отказе в иске, суд апелляционной инстанции указал, что условиями договора, с которыми истец был ознакомлен и согласен, не предусмотрен возврат платежа при прекращении опционного договора. При этом суд апелляционной инстанции исходил из того, что условие опционного договора о невозврате платежа не ущемляет права потребителя, поскольку это прямо предусмотрено законом.
Кассационный суд общей юрисдикции оставил апелляционное определение без изменения.
Судебная коллегия по гражданским делам Верховного Суда РФ с выводами судов апелляционной и кассационной инстанций не согласилась в связи со следующим.
Согласно п. 1 ст. 422 ГК РФ договор должен соответствовать обязательным для сторон правилам, установленным законом и иными правовыми актами (императивным нормам), действующим в момент его заключения.
В ст. 168 ГК РФ закреплено, что, за исключением случаев, предусмотренных п. 2 этой статьи или иным законом, сделка, нарушающая требования закона или иного правового акта, является оспоримой, если из закона не следует, что должны применяться другие последствия нарушения, не связанные с недействительностью сделки. Сделка, нарушающая требования закона или иного правового акта и при этом посягающая на публичные интересы либо права и охраняемые законом интересы третьих лиц, ничтожна, если из закона не следует, что такая сделка оспорима или должны применяться другие последствия нарушения, не связанные с недействительностью сделки.
В силу п. 1 ст. 16 Закона о защите прав потребителей недопустимыми условиями договора, ущемляющими права потребителя, являются условия, которые нарушают правила, установленные международными договорами Российской Федерации, данным Законом, законами и принимаемыми в соответствии с ними иными нормативными правовыми актами Российской Федерации, регулирующими отношения в области защиты прав потребителей. Недопустимые условия договора, ущемляющие права потребителя, ничтожны.
Если включение в договор условий, ущемляющих права потребителя, повлекло причинение убытков потребителю, они подлежат возмещению продавцом (изготовителем, исполнителем, импортером, владельцем агрегатора) в полном объеме в соответствии со ст. 13 данного Закона.
Согласно п. 2 названной статьи к недопустимым условиям договора, ущемляющим права потребителя, в том числе относятся:
условия, которые устанавливают для потребителя штрафные санкции или иные обязанности, препятствующие свободной реализации права, установленного ст. 32 этого Закона (подп. 3);
иные условия, нарушающие правила, установленные международными договорами Российской Федерации, данным Законом, законами и принимаемыми в соответствии с ними иными нормативными правовыми актами Российской Федерации, регулирующими отношения в области защиты прав потребителей (подп. 15).
Пунктом 76 постановления Пленума Верховного Суда РФ от 23 июня 2015 г. N 25 "О применении судами некоторых положений раздела I части первой Гражданского кодекса Российской Федерации" разъяснено, что ничтожными являются условия сделки, заключенной с потребителем, не соответствующие актам, содержащим нормы гражданского права, обязательные для сторон при заключении и исполнении публичных договоров (ст. 3, пп. 4 и 5 ст. 426 ГК РФ), а также условия сделки, при совершении которой был нарушен явно выраженный законодательный запрет ограничения прав потребителей (например, п. 2 ст. 16 Закона о защите прав потребителей, ст. 29 Федерального закона от 2 декабря 1990 г. N 395-I "О банках и банковской деятельности").
Названные требования закона и разъяснения Пленума Верховного Суда РФ судом апелляционной инстанции при рассмотрении спора не учтены, в связи с чем условие договора об отсутствии у заказчика права требовать возврата платежа при отказе от исполнения договора надлежащей оценки не получило.
(Определение Судебной коллегии по гражданским делам Верховного Суда РФ от 11 июля 2023 г. N 5-КГ23-57-К2)
```


## ДОБОР Г16 — Л (часть 2). Правила применения рекомендательных технологий крупных сервисов — фактическая структура

### Яндекс (единая страница для всех сервисов)

- Источник: https://music.yandex.ru/legal/recommendations/ru/ — curl HTTP 200, 692 512 байт (SPA-разметка); текст взят через r.jina.ai: HTTP 200, 218 582 байт; снято 12.09.2026 ~22:15 МСК.
- Устройство: общая часть «Как работают рекомендации в Яндексе» + «Как управлять рекомендациями», дальше по разделу на каждый сервис с одинаковым набором из пяти подразделов: «Для чего использует» / «Какие данные о пользовательских предпочтениях использует и где получает» / «Как анализирует данные и формирует рекомендации» / «Как пользователь может влиять на рекомендации» / «Адрес почты для запросов». Это ровно перечень, которого требует ч. 1 ст. 10.2-2 149-ФЗ (записана выше).

Оглавление (все заголовки, как отдал прокси):

```text
## Как работают рекомендации в Яндексе
#### Что такое рекомендации
#### Зачем нужны рекомендации
#### Как работают рекомендации
#### На чем основана работа рекомендаций
#### Алгоритмы
#### Безопасность и конфиденциальность
## Как управлять рекомендациями
## **Яндекс Музыка**
#### **Для чего Яндекс Музыка использует рекомендательные технологии**
#### **Какие данные о пользовательских предпочтениях сервис использует и где получает**
#### **Как сервис анализирует данные и как формирует рекомендации**
#### **Как пользователь может влиять на рекомендации**
#### **Адрес почты для запросов**
## Кинопоиск
#### **Для чего Кинопоиск использует рекомендательные технологии**
#### **Какие данные о пользовательских предпочтениях сервис использует и где получает**
#### **Как сервис анализирует данные и как формирует рекомендации**
#### **Как пользователь может влиять на рекомендации**
#### **Адрес для направления запросов**
## **Яндекс Книги**
#### **Для чего Яндекс Книги используют рекомендательные технологии**
#### **Какие данные о пользовательских предпочтениях сервис использует и где получает**
#### **Как сервис анализирует данные и как формирует рекомендации**
#### **Как пользователь может влиять на рекомендации**
#### **Адрес почты для запросов**
## **Яндекс Афиша**
#### **Для чего Афиша использует рекомендательные технологии**
#### **Какие данные о пользовательских предпочтениях сервис использует и где получает**
#### **Как сервис анализирует данные и как формирует рекомендации**
#### **Как пользователь может влиять на рекомендации**
#### **Адрес почты для запросов**
## **Яндекс Плюс**
#### **Для чего Плюс использует рекомендательные технологии**
#### **Какие данные о пользовательских предпочтениях сервис использует и где получает**
#### **Как сервис анализирует данные и как формирует рекомендации**
#### **Как пользователь может влиять на рекомендации**
#### **Адрес почты для запросов**
## **Яндекс Такси**
#### **Для чего Яндекс Такси использует рекомендательные технологии**
#### **Точка посадки**
#### **Точки старта и финиша в поисковой строке**
#### **Коммуникации в приложении**
#### **Опция «Подождать»**
#### **Опция «Чуть пройти»**
#### **Овердрафт для корпоративных клиентов**
#### **Адрес почты для запросов**
## **Яндекс Про**
#### **Для чего Яндекс Про использует рекомендательные технологии**
#### **Заказы**
#### **Предложения в разделе «Выгода с Про»**
#### **Персональные цели для поездок**
#### **Персональные цели Заправок**
#### **Адрес почты для запросов**
## **Яндекс Доставка**
#### **Для чего Яндекс Доставка использует рекомендательные технологии**
#### **Точки отправки и получения посылки в поисковой строке**
#### **Коммуникации в приложении**
#### **Адрес почты для запросов**
## **Яндекс Драйв**
#### **Для чего Драйв использует рекомендательные технологии**
#### **Профиль вождения**
#### **Оптимальное распределение машин**
#### **Точка окончания поездки**
#### **Рекомендации автомобиля**
#### **Коммуникации в приложении**
#### **Адрес почты для запросов**
## **Яндекс Заправки**
#### **Скидки и бонусы различным группам пользователей**
#### **Коммуникации в приложении**
#### **Адрес почты для запросов**
## **Яндекс Еда, Деливери**
#### **Для чего Яндекс Еда и Деливери используют рекомендательные технологии**
#### **Какие данные о пользовательских предпочтениях сервис использует и где получает**
#### **Как сервис анализирует данные и как формирует рекомендации**
#### **Как пользователь может влиять на рекомендации**
#### **Адрес почты для запросов**
## **Яндекс Лавка**
#### **Для чего Лавка использует рекомендательные технологии**
#### **Какие данные о пользовательских предпочтениях сервис использует и где получает**
#### **Как сервис анализирует данные и как формирует рекомендации**
#### **Как пользователь может влиять на рекомендации**
#### **Адрес почты для запросов**
## **Яндекс Маркет**
#### **Для чего Маркет использует рекомендательные технологии**
#### **Какие данные о пользовательских предпочтениях сервис использует и где получает**
#### **Как сервис анализирует данные и как формирует рекомендации**
#### **Как пользователь может влиять на рекомендации**
#### **Адрес почты для запросов**
## **Яндекс Советник**
#### **Для чего Советник использует рекомендательные технологии**
#### **Какие данные о пользовательских предпочтениях сервис использует и где получает**
#### **Как сервис анализирует данные и как формирует рекомендации**
#### **Как пользователь может влиять на рекомендации**
#### **Адрес почты для запросов**
## **Геосервисы (Яндекс Карты, Яндекс Навигатор)**
#### **Для чего Карты и Навигатор используют рекомендательные технологии**
#### **Поиск на карте, подсказки организаций и адресов**
#### **Ранжирование объектов на карте**
#### **Предоставление пользователям рекомендаций в режиме «Идеи»**
#### **Адрес почты для запросов**
## **Алиса**
#### **Для чего Алиса использует рекомендательные технологии**
#### **Какие данные о пользовательских предпочтениях сервис использует и где получает**
#### **Как сервис анализирует данные и как формирует рекомендации**
#### **Как пользователь может влиять на рекомендации**
#### **Адрес почты для запросов**
## **Поиск**
#### **Для чего Поиск использует рекомендательные технологии**
#### **Чем это помогает пользователям**
#### **Какие данные о пользовательских предпочтениях использует Поиск и где их получает**
#### **Как сервис анализирует данные и как формирует рекомендации**
#### **Как пользователь может влиять на рекомендации**
#### **Адрес почты для запросов**
## **Яндекс Ритм**
#### **Для чего «Яндекс Ритм» использует рекомендательные технологии**
#### **Какие данные о пользовательских предпочтениях сервис использует и где получает**
#### **Как сервис анализирует данные и формирует рекомендации**
#### **Как пользователь может влиять на рекомендации**
#### **Адрес почты для запросов**
## **Шедеврум**
#### **Описание для чего используются рекомендательные технологии**
#### **Какие данные о пользовательских предпочтениях сервис использует и где получает**
#### **Как сервис анализирует данные и как формирует рекомендации**
#### **Как пользователь может влиять на рекомендации**
#### **Адрес почты для направления запросов**
## **Яндекс 360: Яндекс Почта**
#### **Для чего Почта использует рекомендательные технологии**
#### **Подсказки в почте**
#### **Защита от спама**
#### **Адрес почты для направления запросов**
## **Яндекс 360: Яндекс Диск**
#### **Для чего Диск использует рекомендательные технологии**
#### **Какие данные о пользовательских предпочтениях сервис использует и где получает**
#### **Как сервис анализирует данные и как формирует рекомендации**
#### **Как пользователь может влиять на рекомендации**
#### **Адрес почты для направления запросов**
## **Едадил**
#### **Для чего Едадил использует рекомендательные технологии**
#### **Какие данные о пользовательских предпочтениях сервис использует и где получает**
#### **Как сервис анализирует данные и как формирует рекомендации**
#### **Как пользователь может влиять на рекомендации**
#### **Адрес почты для запросов**
## **Яндекс Погода**
#### **Для чего Погода использует рекомендательные технологии**
#### **Какие данные о пользовательских предпочтениях сервис использует и где получает**
#### **Как сервис анализирует данные и как формирует рекомендации**
#### **Как пользователь может влиять на рекомендации**
#### **Адрес почты для запросов**
## **Яндекс Директ**
#### **Для чего Директ использует рекомендательные технологии**
#### **Какие данные о пользовательских предпочтениях сервис использует и где получает**
#### **Как сервис анализирует данные и как формирует рекомендации**
#### **Как пользователь может влиять на рекомендации**
## **Яндекс Взгляд**
#### **Для чего Взгляд использует рекомендательные технологии**
#### **Какие данные о пользовательских предпочтениях сервис использует и где получает**
#### **Как сервис анализирует данные и как формирует рекомендации**
#### **Как пользователь может влиять на рекомендации**
#### **Адрес почты для направления запросов**
## **Вебмастер**
#### **Для чего Вебмастер использует рекомендательные технологии**
#### **Какие данные о пользовательских предпочтениях сервис использует и где получает**
#### **Как сервис анализирует данные и как формирует рекомендации**
#### **Как пользователь может влиять на рекомендации**
#### **Адрес почты для запросов**
## **ADFOX**
#### Для чего ADFOX использует рекомендательные технологии
#### Какие данные о пользовательских предпочтениях сервис использует и где получает
#### Как сервис анализирует данные и как формирует рекомендации
#### Как пользователь может влиять на рекомендации
#### Адрес почты для запросов
## **Яндекс Бизнес**
#### **Как сервис анализирует данные и как формирует рекомендации**
#### **Как пользователь может влиять на рекомендации**
#### **Адрес почты для направления запросов**
## **Яндекс Игры**
#### **Для чего Игры используют рекомендательные технологии**
#### Какие данные о пользовательских предпочтениях сервис использует и где получает
#### **Как сервис анализирует данные и как формирует рекомендации**
#### **Как пользователь может влиять на рекомендации**
#### **Адрес почты для запросов**
## **Авто.ру**
#### **Для чего Авто.ру использует рекомендательные технологии**
#### **Какие данные о пользовательских предпочтениях сервис использует и где получает**
#### **Как сервис анализирует данные и как формирует рекомендации**
#### **Как пользователь может влиять на рекомендации**
#### **Адрес почты для запросов**
## **Яндекс Недвижимость**
#### **Для чего Недвижимость использует рекомендательные технологии**
#### **Какие данные о пользовательских предпочтениях сервис использует и где получает**
#### **Как сервис анализирует данные и как формирует рекомендации**
#### **Как пользователь может влиять на рекомендации**
#### **Адрес почты для запросов**
## **Яндекс Путешествия**
#### **Для чего Путешествия используют рекомендательные технологии**
#### **Какие данные о пользовательских предпочтениях сервис использует и где получает**
#### **Как сервис анализирует данные и как формирует рекомендации**
#### **Как пользователь может влиять на рекомендации**
#### **Адрес почты для запросов**
## **Яндекс Услуги**
#### **Описание для чего используются рекомендательные технологии**
#### **Какие данные о пользовательских предпочтениях сервис использует и где получает**
#### **Как сервис анализирует данные и как формирует рекомендации**
#### **Как пользователь может влиять на рекомендации**
#### **Адрес почты для запросов**
## **Яндекс Учебник**
#### **Для чего Учебник использует рекомендательные технологии**
#### **Какие данные о пользовательских предпочтениях сервис использует и где получает**
#### **Как сервис анализирует данные и как формирует рекомендации**
#### **Как пользователь может влиять на рекомендации**
#### **Адрес почты для запросов**
## **Яндекс Практикум**
#### **Для чего Практикум использует рекомендательные технологии**
#### **Какие данные о пользовательских предпочтениях сервис использует и где получает**
#### **Как сервис анализирует данные и как формирует рекомендации**
#### **Как пользователь может влиять на рекомендации**
#### **Адрес почты для направления запросов**
## **Яндекс Пэй**
#### **Для чего Пэй использует рекомендательные технологии**
#### **Какие данные о пользовательских предпочтениях сервис использует и где получает**
#### **Как сервис анализирует данные и как формирует рекомендации**
#### **Как пользователь может влиять на рекомендации**
#### **Адрес почты для запросов**
## **Recommendix**
#### **Для чего Recommendix использует рекомендательные технологии**
#### **Какие данные о пользовательских предпочтениях сервис использует и где получает**
#### **Как пользователь может влиять на рекомендации**
#### **Адрес почты для запросов**
```

Общая часть — дословно:

```text
На информационном ресурсе применяются рекомендательные технологии. На информационном ресурсе при применении информационных технологий предоставления информации осуществляется сбор, систематизация и анализ сведений, относящихся к предпочтениям пользователей сети «Интернет», находящихся на территории Российской Федерации.

## Как работают рекомендации в Яндексе

#### Что такое рекомендации

Рекомендации — это подсказки, которые помогают быстрее и точнее находить нужное и интересное на сервисах Яндекса.

Современный интернет невозможно представить без рекомендаций. Они есть практически во всех сервисах Яндекса: Еде, Лавке, Музыке, Кинопоиске, Маркете, Такси и многих других. Именно рекомендации делают сервисы умными и удобными для пользователей.

Больше подробностей — [тут](https://ya.ru/project/recommend).

#### Зачем нужны рекомендации

Рекомендации помогают:

*   **Экономить время.** Они предлагают контент, товары и услуги, которые, скорее всего, подойдут именно вам. Без необходимости искать их по всему интернету или выбирать из каталога.

*   **Находить новое.** Рекомендательные алгоритмы учитывают предпочтения — не только ваши, но и других пользователей. Они могут предложить что-то необычное: одежду локального бренда, забытый фильм с любимым актёром или группу, которую вы бы иначе никогда не услышали.

*   **Получать выгоду.** Рекомендации могут предложить качественную альтернативу или бюджетный аналог, который будет не хуже привычного бренда.

#### Как работают рекомендации

За все рекомендации на сервисах Яндекса отвечают алгоритмы, которые основываются на информации о действиях пользователей на наших сервисах. Рекомендации постоянно меняются и подстраиваются под поведение пользователей.

Рекомендательные алгоритмы учитывают много факторов. Например, Яндекс Музыка обращает внимание на треки и исполнителей, Кинопоиск — на просмотренные фильмы, а Яндекс Маркет — на регулярные покупки и популярные категории товаров. У одних рекомендаций есть сезонность, на другие влияют оценки «нравится» и «не нравится». Если предпочтения пользователя изменились, алгоритм это учтёт, и со временем рекомендации адаптируются под новые интересы.

Чем активнее пользователь взаимодействует с сервисами (слушает музыку, смотрит фильмы, заказывает еду или товары), тем точнее будут его персональные рекомендации. Однако алгоритмам требуется время, чтобы собрать достаточно информации и сформировать максимально релевантные рекомендации.

#### На чем основана работа рекомендаций

Главный источник информации для рекомендаций — это поведение пользователей на сервисах Яндекса. Например:

*   Лайки и дизлайки, кнопки «Нравится» («Не нравится»), оценки и так далее

*   Заказы, покупки, клики и другие похожие действия

*   Просмотры фильмов, товаров, подборок; прослушивания треков и альбомов

*   Время просмотра, нахождения на странице или в разделе сервиса и схожие данные

*   Информация, которой вы делитесь с Яндексом: например, геолокация, язык или возраст

*   Свойства контента или товаров: например, жанр фильма или спектральные характеристики музыки

*   Контекст. Например, день недели или время суток

На старте работы с сервисом у алгоритмов может быть недостаточно данных для качественных рекомендаций. Поэтому в некоторых случаях сервисы предлагают пользователю рассказать о предпочтениях и интересах, чтобы сразу рекомендовать то, что может ему понравиться.

#### Алгоритмы

Алгоритмы Яндекса используют различные методы машинного обучения (в том числе нейронные сети с миллионами параметров) и виды разметки — например, разметку релевантности контента запросам пользователей.

Яндекс постоянно тестирует и улучшает алгоритмы. При каждом изменении алгоритм проходит приёмку — проверку того, что изменение улучшает качество работы. Приёмка может включать в себя:

*   **Эксперименты на большой аудитории.** В таких экспериментах поведение части пользователей оценивается в течение долгого времени, чтобы убедиться, что изменение алгоритма улучшает работу сервиса.

*   **Обратные эксперименты.** После принятия новой версии алгоритма, старая продолжает работать для небольшой группы пользователей, чтобы подтвердить, что новая версия лучше.

#### Безопасность и конфиденциальность

Яндекс надёжно защищает данные пользователей на своих сервисах. Для этого мы используем, например, шифрование и настройки доступа, проходим независимый аудит в соответствии с AICPA SOC 2 и SOC 3 и другими стандартами безопасности.

Мы обязуемся защищать конфиденциальность пользователей, соблюдая законы о защите данных и не допуская несанкционированного доступа к информации.

## Как управлять рекомендациями

Рекомендации зависят от поведения пользователей на сервисах Яндекса. При этом выбор всегда остаётся за пользователем: он может следовать рекомендациям или игнорировать их.

Также всем пользователям, у которых есть аккаунт на Яндексе, доступен раздел «Управление данными» в Яндекс ID. В нём можно просмотреть, какие данные доступны каждому сервису, изучить эти данные и распорядиться ими по своему усмотрению. Подробнее — в [справке](https://yandex.ru/support/id/data.html).
```

Образец раздела одного сервиса (Яндекс Музыка) — дословно:

```text
## **Яндекс Музыка**

**(ООО «Яндекс Музыка»)**

#### **Для чего Яндекс Музыка использует рекомендательные технологии**

Яндекс Музыка использует рекомендательные технологии для того, чтобы предлагать пользователям музыкальные треки, альбомы, исполнителей или плейлисты в соответствии с их музыкальными предпочтениями.

Рекомендательный алгоритм сервиса используется для формирования «умных» плейлистов, витрин и бесконечного потока музыки «Моя волна». Он анализирует и учитывает множество факторов, таких как история прослушивания (включая отказ от дослушивания, пропуск трека), добавление в коллекцию и другие.

Яндекс Музыка может использовать фильтры для исключения нерелевантного или нежелательного контента. Для фильтрации может использоваться соответствие правилам размещения контента на сервисе, а также пользовательские настройки, например, ограничение доступа к контенту для взрослых.

#### **Какие данные о пользовательских предпочтениях сервис использует и где получает**

Рекомендательные алгоритмы Яндекс Музыки используют следующие сведения о предпочтениях пользователей, полученные от них при использовании сервиса:

*   поисковые запросы на сервисе,

*   историю прослушивания пользователя, включая длительность, повторные прослушивания, отказ от дослушивания, пропуск трека, добавление в коллекцию,

*   просмотры контента, в том числе витрин,

*   реакции с помощью действий «нравится» и «не нравится»,

*   выбор в функции «уточнить музыкальные предпочтения» (жанры и исполнители, которые нравятся пользователю),

*   настройки предпочтений: настроение треков (бодрый, весёлый), степень знакомства (новое, любимое), похожесть на другой контент («Моя волна по…»).

Также используются аналогичные агрегированные данные по другим пользователям сервиса.

#### **Как сервис анализирует данные и как формирует рекомендации**

Стратегия заключается в анализе большого количества факторов, включая жанр, название, текст, длительность, характер аудиотреков, вхождение трека в те или иные плейлисты, историю взаимодействия пользователей с треками, историю прослушивания и так далее, чтобы предложить пользователю максимально интересную для него музыку.

Алгоритм адаптируется к поведению пользователей, анализируя историю прослушивания, просмотры контента, добавление контента в коллекцию, длительность прослушивания и другие метрики. Это помогает системе понять, что именно ценит пользователь, и предоставлять более точные предложения.

Алгоритм обучается различными методами с использованием асессорской разметки как источника знаний.

Алгоритм принимает решение на основе отбора релевантных для пользователя единиц контента и их последующего ранжирования, где каждой единице контента (трек, альбом, плейлист и т.д.) присваивается ранг на основе различных сигналов и данных. Эти данные включают в себя запрос (в случае поиска), разнообразие и объем пользовательских предпочтений в разрезе исполнителей, треков и жанров, поведение пользователя.

Ранжирование работает таким образом, чтобы максимизировать вычисляемую метрику качества рекомендаций, которая показывает, как часто пользователь обращается к музыке и как долго её слушает, поощряя время прослушивания в течение дня и количество дней с прослушиваниями в рамках недели.

Алгоритм расчета и параметры метрики качества рекомендаций подбираются таким образом, чтобы максимально хорошо соответствовать объективной (но сложнее вычисляемой) метрике, показывающей, насколько высоко пользователь оценивает интересность предложенного ему контента.

#### **Как пользователь может влиять на рекомендации**

Ключевую роль в изменении рекомендательного алгоритма играют: пользовательские действия (реакция с помощью действий «нравится», «не нравится», пропуск трека, повторное прослушивание трека), текст запроса (в случае обращения к поисковой выдаче), история прослушивания, история просмотров витрин.

Эти данные помогают системе предложить пользователю наиболее релевантные результаты (состав витрины, плейлиста, потока музыки).

Пользователи Яндекс Музыки могут влиять на рекомендации:

*   через свое поведение в ходе прослушивания (включая дослушивание, добавление в коллекцию, пропуск или недослушивание трека, выбор контента на витрине, отметки «нравится» и «не нравится»);

*   постановкой отметок «нравится» и «не нравится»;

*   настройкой рекомендаций функцией «уточнить музыкальные предпочтения», с помощью которой пользователь выбирает жанры и исполнителей, которые ему нравятся.

Некоторые продукты Яндекс Музыки могут позволять пользователям настраивать предпочтения, чтобы получать более точные и персонализированные рекомендации, например настроить настроение треков (бодрый, весёлый), регулировать степень знакомства (новое, любимое), похожесть на другой контент («Моя волна по…»).

Пользователи могут игнорировать рекомендации и использовать самостоятельно выбранный и сохраненный контент.

#### **Адрес почты для запросов**

[recommendations@support.yandex.ru](mailto:recommendations@support.yandex.ru)
```

### VK Реклама (ООО «ВК»)

- Источник: https://ads.vk.ru/documents/recommendation (r.jina.ai HTTP 200, 6 522 байт) — страница-заглушка от 29.09.2023 со ссылкой на https://help.mail.ru/legal/terms/adsvk/recommendation/ (r.jina.ai HTTP 200, 31 392 байт). У ВК отдельные правила на каждый продукт (ресурс Mail, медиапроекты, Почта, Облако, Юла, Маруся, VK Реклама) — видно по меню справки.
- Текст правил VK Рекламы — дословно (рекламные баннеры справки вырезаны):

```text
# Правила применения рекомендательных технологий рекламной системы « VK Реклама»




С целью предоставления релевантных рекламных материалов, интересных каждому конкретному пользователю, рекламная система «VK Реклама» применяет технологии подбора индивидуального рекламного контента.

Данное технологическое решение позволяет рекламной системе подбирать материалы, подходящие каждому конкретному пользователю среди десятков миллионов рекламных сообщений, загруженных рекламодателями в рекламную систему. Правила описывают механизмы и принципы работы рекомендательных алгоритмов VK Реклама, а также раскрывают, какие сведения о пользователях собираются и используются для формирования рекомендаций.

Технологии подбора индивидуального рекламного контента – это программное обеспечение, использующее механизмы искусственного интеллекта для категоризации интересов пользователей и ранжирования рекламных материалов в зависимости от предполагаемых интересов. Интересы пользователей определяются рекомендательными алгоритмами с учетом сведений о взаимодействии пользователей с проектами ВК и партнеров. Чем больше пользователь использует проекты ВК, тем точнее будет работать система подбора рекламных материалов.

В число сведений, используемых алгоритмами рекламной системой «VK Реклама» для принятия решения о показе индивидуального рекламного сообщения пользователю, входят действия пользователя внутри проектов ВК, реакции на прошедшие рекламные кампании, которые уже видел пользователь. К реакциям относятся клики, скрытия рекламных объявлений, сохранения контента и жалобы. Также учитываются популярность рекламируемого продукта для конкретной аудитории, к которой относится пользователь, его половозрастные характеристики и иные признаки.

Сведения о интересах пользователей обрабатываются следующим образом:

*   Рекомендательные алгоритмы осуществляют сбор и анализ прошедших рекламных кампаний и открытых данных в проектах ВК, в том числе сведений о предпочтениях пользователей, в том числе: логи кликов по рекламным сообщениям, сохранения, отказы от просмотра рекламы, а также тематики материалов, которые чаще выбирал пользователь, включая посты, видео, фото.

*   Применяются математические модели (в том числе для формирования признакового пространства), которые путем многофакторного анализа, классификации, ранжирования признаков контента позволяют оценить вероятность того, что информационный материал будет просмотрен до конца конкретным пользователем.

*   Отобранные релевантные рекламные сообщения попадают в аукцион рекламной системы. Рекламное сообщение - победитель будет показано пользователю.

Рекламная платформа VK Реклама не демонстрируют пользователям материалы, содержащие, среди прочего, недостоверную информацию, информацию с нарушением закона о рекламе. Каждое рекламное сообщение проходит строгую модерацию.

Пользователи могут влиять на факт показа тех или иных рекламных материалов у себя в ленте путем клика на меню в правом верхнем углу и нажатием одного из пунктов меню: «сохранить в закладках», «это не интересно», «пожаловаться».

Юридически значимые сообщения по вопросам применения рекомендательных технологий могут быть направлены на адрес электронной почты ООО «ВК»: [caresupport@vk.company](mailto:caresupport@vk.company).

Служба поддержки Mail

![Image 12: Помощь Mail](https://hmr-assets.cdn-vk.ru/cdn/img/og-sharing.png)

[Предыдущая статья Terms and conditions for publishers](https://help.mail.ru/legal/terms/adsvk/partners-doc-terms-for-nonresidents/)

[Следующая статья Пользовательское соглашение VK Реклама](https://help.mail.ru/legal/terms/adsvk/terms/)
```


### Okko

- Источник: ссылка из подвала https://blog.okko.tv/legal/terms-of-use («На информационном ресурсе применяются рекомендательные технологии в соответствии c Правилами») → https://clients-static.okko.tv/web/docs/recommendations-rules.pdf — curl, HTTP 200, 79 760 байт PDF; pdftotext 4 215 знаков. Снято 12.09.2026 ~22:20 МСК.
- Устройство: одностраничный PDF, «вступили в силу 01.12.2023», неотъемлемая часть пользовательского соглашения; нумерованные пункты: 1 — виды сведений и источники; 2 — как анализируются (ML, глубинное обучение, градиентный бустинг); 3 — как формируются рекомендации; далее — управление и контакты. Текст целиком, дословно:

```text
Правила применения рекомендательных технологий

   Вступили в силу 01.12.2023

На информационном ресурсе при применении информационных технологий
предоставления информации осуществляется сбор, систематизация и анализ
сведений, относящихся к предпочтениям пользователей сети «Интернет»,
находящихся на территории Российской Федерации.

Настоящие правила применения рекомендательных технологий (Правила) определяют
общие условия и правила применения информационных технологий предоставления
информации на основе сбора, систематизации и анализа сведений, относящихся к
предпочтениям Пользователей (далее – «Рекомендательные технологии»).

Правила являются неотъемлемой частью Пользовательского соглашения Сервиса

1. Для функционирования Рекомендательных технологий используются следующие виды
сведений, относящиеся к предпочтениям авторизованных Пользователей и источники их
получения:
1.1 Для работы Рекомендательных технологий используются данные, предоставляемые
авторизованным Пользователем в результате использования браузера или приложения,
запускаемого на устройстве Пользователя и взаимодействующего с Сервисом.
1.2 Каждому авторизованному Пользователю присваивается случайный идентификатор
Пользователя, который представляет собой набор букв, цифр и специальных символов.
1.3 В совокупности с идентификатором авторизованного Пользователя используются
следующие данные о взаимодействиях Пользователя с Сервисом, такие как:
     - данные о факте и длительности просмотра Видеоконтента;
     - данные о пользовательских рейтингах и списке «Запомнено»;
     - данные о показанном Видеоконтенте на витрине Пользователя;
     - данные о поисковых запросах на Сервисе;
     - данные о переходе на карточку Видеоконтента.
2. Данные о взаимодействиях Пользователя с Сервисом, в том числе с Видеоконтентом, а
также контентные метаданные используются для выявления закономерностей и паттернов
предпочтений Пользователя на основе методов машинного обучения, включая модели
глубинного обучения и градиентного бустинга деревьев принятия решений.
3. На основе выявленных закономерностей и паттернов предпочтений Пользователя
происходит ранжирование коллекций Видеоконтента для Пользователя на витрине
Сервиса, а также формируются рекомендации в виде списка дополнительного
Видеоконтента.
```

### Ozon — НЕ добыт

- https://docs.ozon.ru/legal/terms-of-use/site/algorithms/ (адрес найден WebSearch по ozon.ru, заголовок «Алгоритмы | Помощь OZON»): curl с браузерным UA — HTTP 307 на страницу проверки (164 байт); r.jina.ai — «Antibot Challenge Page», исходный ответ 403; Wayback availability API — HTTP 429. Текст не получен.
- Пересказ выдачи (Хабр https://habr.com/ru/news/764976/ , Lenta.ru): у Ozon два алгоритма — поиска и рекомендаций; ~300 характеристик товара, рейтинги, поведение покупателя; учитываются кнопки «Подписаться», «Не интересно», «Скрыть из ленты», «Пожаловаться». Не норма и не текст правил.


## ИТОГ ДОБОРА Г16 (monetization_and_graveyard) — 12.09.2026

| Пункт | Статус | Что именно |
|---|---|---|
| Ж. Приказ РКН от 25.03.2025 № 68 | добыт, consultant.ru в окне | утверждённые Требования к идентификатору рекламы — целиком; приказная часть (реквизиты вступления в силу) — только по поисковой выдаче: с 25.04.2025, взамен приказа № 191 |
| З. Обзор ВС от 18.10.2023, пп. 10–11 | добыт | consultant.ru (cons_doc_LAW_460140) и ГАРАНТ, сверены — расхождения только редакционные |
| З. Определение ВС от 23.08.2022 № 41-КГ22-23-К4 отдельным текстом | НЕ добыт | garant.ru/products/ipo/prime/doc/405296547/ — HTTP 403; vsrf.ru/stor_pdf_ec.php?id=150868 — HTTP 404; позиция определения дословно воспроизведена в п. 10 Обзора как его основание |
| Л. Правила рекомендательных технологий | добыт частично | 149-ФЗ ст. 10.2-2 целиком; Яндекс (структура + общая часть + образец раздела), VK Реклама (текст), Okko (PDF целиком); Ozon — НЕ добыт: антибот (curl 307, r.jina.ai 403, Wayback 429) |

Буквальное содержание:
- Обзор ВС, п. 10: «Если имеет место абонентский договор на оказание услуг, то потребитель имеет право требовать возврата денежных сумм, уплаченных за тот период действия договора, на который он досрочно прекращен»; «Обязанность доказать наличие таких расходов и их размер … возлагается на исполнителя».
- Обзор ВС, п. 11 (заголовок): «Условие договора, согласно которому у потребителя при отказе от исполнения договора отсутствует или ограничивается право на возврат уплаченных денежных средств, является недействительным, как ущемляющее права потребителя».
- Структура правил у крупных сервисов совпадает с перечнем ч. 1 ст. 10.2-2: для чего используются технологии → какие данные о предпочтениях и откуда → как анализируются и формируются рекомендации → как пользователь влияет → адрес для обращений. Яндекс делает одну страницу с разделом на каждый сервис, ВК — отдельный документ на каждый продукт, Okko — PDF на одну страницу как «неотъемлемую часть» пользовательского соглашения (в силе с 01.12.2023).

🔴 Что меняет выводы `legal_final.md`:
1. 🔴 **Возврат за неиспользованный период подписки — позиция ВС, а условие «оплата невозвратна» ничтожно (п. 11 Обзора, ЗоЗПП ст. 16 и 32 — дословно в paid_launch).** В §1.1 и §6 этого нет; в оферте нужен порядок пропорционального возврата, а расходы, которые мы удерживаем, доказываем мы. Оговорка: оба дела Обзора — об абонентских договорах на услуги (автоуслуги). Прямого разбора SaaS-подписки в пп. 10–11 нет.
2. Задача L1 из §6 получает готовый образец структуры: пять подразделов по ч. 1 ст. 10.2-2 (Яндекс и Okko). Сам вывод §1.1 не меняется.

---

## ДОБОР Г30.3 — Exa (16.09.2026)

**Каналы на начало работы (16.09.2026, ~21:30 МСК):** Exa `mcp__exa__web_search_exa` — 🟢 работает; `r.jina.ai` без UA → `sec.gov`
**HTTP 200**, 13 806 б; OpenAlex **200**; Crossref **200**; `cbr.ru` прямой `curl -sk --http1.1` **200**; Wayback **302** (жив). Окно `consultant.ru` открыто.

### Г30.3-Ю3. Приказ РКН от 25.03.2025 № 68 — приказная часть (реквизиты вступления в силу) — ✅ ДОБЫТО ПЕРВОИСТОЧНИКОМ

Хвост из итога Г16: «приказная часть (реквизиты вступления в силу) — только по поисковой выдаче». Закрыт.

Источники:
- Exa `web_search_exa` («Приказ Роскомнадзора от 25.03.2025 № 68 … зарегистрирован в Минюсте вступает в силу») — 8 результатов:
  base.garant.ru, rulaws.ru, consultant.ru (cons_doc_LAW_503134), garant.ru/hotlaw, normativ.kontur.ru, pravo.ppt.ru, minjust.consultant.ru, meganorm.ru;
- **`https://base.garant.ru/411874488/` через `r.jina.ai` — HTTP 200, 14 427 б**, снято 16.09.2026 (приказная часть целиком, ниже дословно);
- normativ.kontur.ru (сниппет Exa): «Редакция от 25.03.2025 — Действует с 25.04.2025»; ГАРАНТ (сниппет Exa): «Вступает в силу с 25 апреля 2025 г.»;
  pravo.ppt.ru (сниппет Exa): «опубликован: 16 апр 2025».

**Приказная часть дословно (ГАРАНТ):**

> В соответствии с частью 17 статьи 18.1 Федерального закона от 13 марта 2006 г. N 38-ФЗ "О рекламе", пунктом 1 Положения о Федеральной службе
> по надзору в сфере связи, информационных технологий и массовых коммуникаций, утвержденного постановлением Правительства Российской Федерации
> от 16 марта 2009 г. N 228, приказываю:
>
> 1. Утвердить прилагаемые Требования к идентификатору рекламы, идентификатору социальной рекламы, его содержанию, порядок и сроки его присвоения,
> размещения при распространении рекламы и (или) социальной рекламы в информационно-телекоммуникационной сети "Интернет", хранения и предоставления
> в Федеральную службу по надзору в сфере связи, информационных технологий и массовых коммуникаций.
>
> 2. Признать утратившим силу приказ Федеральной службы по надзору в сфере связи, информационных технологий и массовых коммуникаций от 30 ноября 2022 г.
> N 191 "Об утверждении Требований к идентификатору рекламы, его содержанию, порядка и сроков его присвоения, размещения при распространении рекламы
> в информационно-телекоммуникационной сети "Интернет", хранения и предоставления в Федеральную службу по надзору в сфере связи, информационных
> технологий и массовых коммуникаций" (зарегистрирован Министерством юстиции Российской Федерации 28 декабря 2022 г., регистрационный 71862).
>
> Руководитель А.Ю.Липов
>
> Зарегистрировано в Минюсте России 14 апреля 2025 г. Регистрационный N 81842

**Реквизиты сводно:** подзаконный акт (приказ федеральной службы), основание — **ч. 17 ст. 18.1 38-ФЗ**; Минюст **14.04.2025 № 81842**;
опубликован 16.04.2025 (по pravo.ppt.ru, номер опубликования на `pravo.gov.ru` не сверялся); **в силу с 25.04.2025** (ГАРАНТ и Контур совпадают);
в приказе **нет отдельного пункта о сроке вступления** — дата 25.04.2025 выводится карточками из общего порядка для ведомственных актов
(10 дней после официального опубликования), а не из текста приказа. Приказ № 191 утратил силу пунктом 2.

**Выжимка.** Для FINPILOT ничего не меняется: требования к erid (текст утверждённых Требований целиком — в блоке Г16-Ж выше) действуют
с 25.04.2025, прежний № 191 применять нельзя. В юрблок — реквизит «Приказ РКН от 25.03.2025 № 68 (рег. Минюст 14.04.2025 № 81842)».

### Г30.3-Ю4. Правила рекомендательных технологий Ozon — ❌ НЕ ДОБЫТО (хвост Г16-Л)

Exa `web_fetch_exa` → «307 Temporary Redirect»; Exa-индекс `docs.ozon.ru` → то же; `r.jina.ai` **без UA** → 200 с телом «Target URL returned error 403» (1 005 б)
и «Antibot Challenge Page» (512 б); Wayback CDX → 503. Причина — JS-челлендж Ozon (класс 2, нужен headless-браузер). Подробности и вторичные описания —
`competitors_2026_refresh_2026-09-12.md`, блок «ДОБОР Г30.3», К1. Для образца документа по ст. 10.2-2 хватает уже добытых Яндекса, VK, Okko.

### ИТОГ Г30.3 (monetization_and_graveyard)

| Пункт | Был статус | Стал | Приём |
|---|---|---|---|
| Приказ РКН от 25.03.2025 № 68 — приказная часть | «только по поисковой выдаче» | **добыто дословно**: основание ч. 17 ст. 18.1 38-ФЗ; п. 2 — № 191 утратил силу; Минюст 14.04.2025 № 81842; в силу 25.04.2025 | Exa search → `r.jina.ai` base.garant.ru (200, 14 427 б) |
| Правила рекомендательных технологий Ozon | не добыто | **не добыто** (класс 2) | Exa fetch/search, `r.jina.ai` без UA, Wayback CDX |
| Определение ВС 41-КГ22-23-К4 отдельным текстом | не добыто | **не пробовалось** в Г30.3 | — |


## ДОБОР Г30.3 — второй заход (16.09.2026)

**Каналы:** Exa — 🟢; `r.jina.ai` без UA — 200; `cbr.ru` — 200; Wayback CDX — **503**; OpenAlex — 429.

### Г30.3-Ю5. Определение ВС РФ от 23.08.2022 № 41-КГ22-23-К4 — ✅ ДОБЫТО ДОСЛОВНО (хвост Г16-З)

Ранее: `garant.ru/products/ipo/prime/doc/405296547/` → **403**, `vsrf.ru/stor_pdf_ec.php?id=150868` → **404**; позиция была известна только по п. 10 Обзора ВС 18.10.2023.
Теперь текст снят через Exa с двух независимых площадок: `gkrfkod.ru/pract/opredelenie-…-41-kg22-23-k4/` и карточка ГАРАНТ `base.garant.ru/405396547/`
(+ `garant.ru/products/ipo/prime/doc/405296547/` — тот же текст в индексе Exa). Дословно:
> «Согласно пункту 1 статьи 429.4 Гражданского кодекса Российской Федерации договором с исполнением по требованию (абонентским договором) признаётся договор,
> предусматривающий внесение одной из сторон (абонентом) определённых, в том числе периодических, платежей … за право требовать от другой стороны (исполнителя)
> предоставления предусмотренного договором исполнения…»
> «В силу статьи 32 Закона о защите прав потребителей и пункта 1 статьи 782 Гражданского кодекса Российской Федерации потребитель вправе отказаться от исполнения
> договора о выполнении работ (оказании услуг) **в любое время** при условии оплаты исполнителю фактически понесённых им расходов…»
> «**Обязанность доказать наличие таких расходов и их размер в данном случае возлагается на исполнителя.**»
> «**Если имеет место абонентский договор на оказание услуг, то потребитель имеет право требовать возврата денежных сумм, уплаченных за тот период действия
> договора, на который он досрочно прекращён.**»
Фабула: покупатель автомобиля возвращал плату за дополнительную услугу; дело направлено на новое рассмотрение, так как суд «не определил, от чьего имени и за чей
счёт заключался договор на оказание услуг со стороны исполнителя».
**Что это меняет.** Позиция Г16 подтверждена первоисточником, а не только Обзором: в оферте FINPILOT нужен порядок **пропорционального возврата** за неиспользованный
период подписки, и бремя доказывания фактических расходов — на нас. 🟠 Полезная оговорка из разбора на zakon.ru (18.12.2023, мнение юриста): при **периодической**
абонентской плате сумма возврата может быть нулевой, если отказ пришёлся на конец оплаченного периода; спорным остаётся возврат за **часть** периода.
Это аргумент в пользу помесячной тарификации вместо предоплаты за год.


---

## ДОБОР Г31.1 — Wayback (16.09.2026)

**Состояние каналов на начало работы (замер 16.09.2026 19:32–20:40 UTC; системная дата среды — 16.09):**
`archive.org/wayback/available` — **429** с редкими окнами 200; `cdx/search/cdx` — **503**
«Temporarily Offline» почти постоянно; 🟢 **replay `web.archive.org/web/<ts>[id_]/<URL>` — 200**
при паузе ≥ 18–20 с между запросами; `timetravel.mementoweb.org` — 000; `archive.ph` — 200,
затем 429, по нужным адресам «No results»; Common Crawl `collinfo.json` — 200, запросный
шлюз — **504**; DTIC — 200/1 408 б «Under Maintenance», второй день.

🔴 **Поправка к пробе доступности архива:** «Wayback лежит» 16.09 означало «лежат
`wayback/available` и CDX»; **replay при этом отдавал снимки**. Это разные подсистемы.

### Г31.1-Г1. ReadyForZero — 🟢 ДОБЫТЫ ОБЕ ТОЧКИ: работающий продукт и страница закрытия

**(а) Работающий продукт.** `https://web.archive.org/web/2014/https://www.readyforzero.com/`
→ **HTTP 200, 28 040 б**, 🔴 **дата снимка 01.01.2015 00:50:49 UTC**. Заголовок
«Pay Off Debt | ReadyForZero».

> «We'll show you **the fastest way to pay off any debt** – and give you the motivation
> to get there.»
> «**A Pay Off Plan That Works.** Take control of your financial life: ReadyForZero has helped
> people **pay down $207 million in debt** – and counting.»
> «**Link all your debts or tell us what you owe**, sit back while we create a personalized plan,
> then prepare to conquer your debt. Include credit card debt, student loan debt, …»
> «**Visualize Your Progress.** … you'll always have access to an easy to read progress graph.»
> «**Automate Your Payments.** … **Upgrade to ReadyForZero PLUS** so you can automate your
> repayment plan.»
> «**Track Your Credit Score.** … signing up for [ReadyForZero] **Credit**. This upgrade allows
> you to make payments and track your **Experian VantageScore 3** credit score.»
> «**Get Better Interest Rates.** Lower your interest rates and consolidate your debts.
> ReadyForZero can show you **what debts should be consolidated** and gives you instant feedback
> on how much you can save. **Preview offers from our trusted partners** without taking …»

**Модель монетизации на пике — трёхслойная:** бесплатный план погашения → платная подписка
**PLUS** (автоплатежи) → платный **Credit** (кредитный скор) → **партнёрские офферы**
рефинансирования/консолидации. То есть подписка и лидогенерация сосуществовали.

**(б) 🔴 Страница закрытия (посмертная).**
`https://web.archive.org/web/2016/https://www.readyforzero.com/` → **HTTP 200, 13 439 б**,
🔴 **дата снимка 07.01.2017 05:14:02 UTC**. Внутренний заголовок — буквально
«**RFZ Sunset Homepage**».

> «**It's time to say goodbye…** We've helped **over 200,000 people** pay down **more than
> $350M in debt**. Thank you for being part of this wonderful journey. We will now be placing
> all our efforts towards our award winn[ing blog] …»
> «ReadyForZero can still help you get the financial help you need.
> **CONSOLIDATE YOUR DEBT** — We've partnered with the best debt consolidation companies …
> **EXPLORE PERSONAL LOAN OPTIONS** … **REBUILD YOUR CREDIT SCORE** — Secured credit cards …»
> «Looking for a loan? **Join over 450,000 people who have received the money they needed
> through Avant.**»
> 🔴 «**© 2016 Avant RFZ LLC**»

**Что это даёт — редкий случай, когда видно и начало, и конец, с числами:**
- Итоговый масштаб продукта за всю жизнь: **200 000+ пользователей, $350 млн погашенного долга**
  (против $207 млн на снимке начала 2015 — то есть примерно $143 млн прироста за два последних
  года жизни).
- 🔴 **Механика смерти названа юридически:** правообладателем страницы закрытия выступает
  **Avant RFZ LLC** — то есть продукт достался кредитору Avant, и от него осталась **воронка
  лидогенерации на займы**: консолидация, персональные займы, secured-карты. Прескриптивная
  часть (план погашения) выключена, партнёрская — оставлена.
- **Вывод для нас, жёсткий:** у прескриптивного советника по долгам, монетизируемого в том числе
  партнёрскими офферами кредитных продуктов, есть устойчивый аттрактор — **выродиться в
  лидогенератор займов**, потому что именно эта часть переживает продукт. Партнёрская
  монетизация и совет по погашению долга **конфликтуют по интересу**: советник заинтересован,
  чтобы долг гасился, партнёр — чтобы брали новый. ReadyForZero — прямое эмпирическое
  подтверждение этого конфликта, а не теоретическое рассуждение.

### Г31.1-Г2. Maybe Finance — 🔴 ДОБЫТА ПОСМЕРТНАЯ СТРАНИЦА: продукт личных финансов БОЛЬШЕ НЕ ПРОДУКТ

`https://web.archive.org/web/2025/https://maybe.co/` → **HTTP 200, 20 497 б**,
🔴 **дата снимка 27.12.2025 17:07:33 UTC**.

> «**Maybe: Know your business, in plain English.**» · «In Early Access Now»
> «No SQL. No spreadsheets. No formulas. No long setup. No learning curve. No four hour tutorials.
> No rows. No bloat. No analysts. No waiting.»
> «**Your business, in plain English.** Start your free trial now. **Just $50/mo after your trial.**»
> «📊 **Connect QuickBooks** — Seamlessly sync your financial data in seconds»
> «🎯 **Play the what-if game** — Model scenarios and see instant projections»
> «✨ No spreadsheets. Ever. — Get insights without formulas or pivot tables»
> 🔴 «**Looking for the personal finance version of Maybe? Find the repository here.**»

**Что это меняет.** По состоянию на **27.12.2025** домен `maybe.co` занят **другим продуктом**:
B2B-аналитикой бизнеса на QuickBooks за **$50/мес**. Продукт личных финансов, который мы
разбирали как конкурента, **низведён до ссылки на открытый репозиторий** — то есть перестал
быть коммерческим продуктом вовсе и живёт как open-source код без компании за ним.

🔴 **Для карты конкурентов это означает:** Maybe в разделе живых конкурентов держать нельзя —
его следует перенести в «кладбище» с пометкой «команда ушла в B2B, персональный продукт отдан
в open source». И отдельно: **сценарное моделирование «what-if» команда сохранила — но продаёт
его бизнесу, а не физлицу.** Это ещё один голос в пользу наблюдения, что за прескриптивную
математику в личных финансах платят плохо, а в B2B — платят ($50/мес против типичных
$5–15/мес в PFM).

### Г31.1-Г3. Bright Money — снимок до смены объекта получен

`https://web.archive.org/web/2022/https://www.brightmoney.co/` → **HTTP 200, 65 905 б**,
🔴 **дата снимка 03.01.2023 13:20:49 UTC**.

- Слоган дословно: «**Bright — Crush card debt. Build credit. Plan for life after debt.**»
- Юрлицо и адрес: **Bright Capital Inc, 50 California St, Floor 15, San Francisco, CA 94111**;
  контакт `hello@brightmoney.co`, +1 877 274 6494.
- Разделы и юридические документы, раскрывающие устройство продукта: «**MoneyScience™**»,
  «School of MoneyScience», «**Credit Builder Credit Agreement**», «**Deposit Agreement**»,
  «**ACH Debit Authorization**», «Electronic Signatures and Communications», «Disclosure»,
  банк-партнёр — **Evolve Bank & Trust**.

**Толкование.** На начало 2023 года Bright — это связка «погашение карточного долга + сборка
кредитной истории», где прескриптивная часть названа собственной торговой маркой
(**MoneyScience™**), а денежный контур держится на **кредитном продукте** (Credit Builder)
и **прямом дебетовании счёта клиента по ACH** через банк-партнёра. То есть монетизация опять
не в совете: совет бесплатен и брендирован, платит клиент за кредитный продукт вокруг него.
🔴 Это **третий случай в одном доборе** (ReadyForZero, Bright, плюс общий вывод по Maybe),
где прескриптивная математика личных финансов сама по себе не является предметом оплаты.
Содержательная выдача HTML этого снимка — навигация и юридический подвал; сами описания
фич подгружались скриптом и в снимок не попали (размер 65 905 б при ~30 строках текста).

## ИТОГ Г31.1 (в этом файле)

| Пункт | Класс | Результат |
|---|---|---|
| ReadyForZero — рабочая и посмертная страницы | 4 | 🟢 **закрыт двумя снимками**: 01.01.2015 и 07.01.2017 («RFZ Sunset Homepage») |
| Maybe Finance — посмертные страницы | 4 | 🟢 **закрыт снимком 27.12.2025** |
| Bright Money — до смены объекта | 4 | 🟡 **частично**: снимок 03.01.2023 получен, но описания фич грузились скриптом; добыты слоган, юрлицо, банк-партнёр и перечень юридических документов |
| Тарифы Дзен-мани и CoinKeeper в прошлых редакциях | 4 | ❌ не пробовано по бюджету — **задолженность** (цена Zenmoney 1 490 ₽ уже добыта ранее из двух первоисточников, приоритет низкий) |

- Закрыто снимками: **2 полностью, 1 частично из 4**.
- 🔴 **Меняет выводы, и существенно:**
  1. **Maybe Finance больше не конкурент** — на 27.12.2025 `maybe.co` занят B2B-аналитикой
     за $50/мес, персональный продукт отдан в open source. Переносить из живых конкурентов
     в «кладбище».
  2. **ReadyForZero даёт полный жизненный цикл с числами** ($207 млн → $350 млн, 200 000+
     пользователей) и юридически зафиксированный финал: **© 2016 Avant RFZ LLC**, продукт
     выродился в лидогенерацию займов. Это эмпирическое подтверждение конфликта интересов
     между советом «гаси долг» и партнёрской монетизацией кредитных продуктов.
  3. Вместе с Bright Money (монетизация через Credit Builder и ACH, а не через совет) —
     **три из трёх** разобранных случая показывают, что за прескриптивную математику личных
     финансов сама по себе не платят.
