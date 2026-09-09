# Первичный материал: вендоры PFM-движков (B2B) — ДОБОР v2, 09.09.2026

> Правило проекта §9/§11 — дословный первичный материал ДО выжимки.
> Тема №11 очереди `docs/research/queue/RESEARCH_QUEUE.md` + её добор №22.
> Перезапуск прогона от 08.09.2026 (`pfm_engine_vendors_2026-09-08.md`), который работал
> при исчерпанном WebSearch и брал только угаданные URL.

## Шапка о качестве прогона

- **WebSearch ЖИВ.** Это принципиальное отличие от версии 08.09: слепая зона «источник,
  чей адрес не угадан, не найден в принципе» закрывается.
- Прогон: один агент, **без субагентов**.
- Файл пишется инкрементально по ходу, до итогового ответа.
- Каналы и их состояние фиксируются по месту, с кодами ответа.

🔴 **ГЛАВНЫЙ РЕЗУЛЬТАТ УЖЕ НА ПЕРВОМ ЗАПРОСЕ: вывод версии 08.09 «ни один вендор не считает
размен долг/накопления с учётом процентных ставок» — ОПРОВЕРГНУТ.** Существует семейство
выданных (не заброшенных) патентов Personetics «Guidance engine», где ставки, стратегии
avalanche/snowball и норма распределения присутствуют явно. Разбор ниже.

---

## 1. 🔴 Capital One «Guidance engine» — US11023967B1 (ВЫДАН, ACTIVE)

Найден **живым поиском** (запрос `Personetics patent "debt paydown" allocation model interest rate`).
Поисковая выдача приписала его Personetics — **это ошибка агрегатора**; открытие первоисточника
показало другого правообладателя. Фиксирую как есть.

URL (открыт): https://patents.google.com/patent/US11023967B1/en
URL (открыт, полный текст): https://www.freepatentsonline.com/11023967.html

| Атрибут | Значение (дословно со страницы) |
|---|---|
| Название | Guidance engine: an automated system and method for providing financial guidance |
| Правообладатель | "Capital One Services LLC" |
| Изобретатели | "Katharine Schlesinger, John Rush, Zheyu Yang, Matthew Davis" |
| Приоритет / подача | "2019-11-12" |
| Публикация | "2021-06-01" |
| Статус | **"Active"** (в отличие от заброшенной заявки Sosna) |

Семейство (из той же выдачи, не открыты поштучно): **US11669897**, **US12008644** — то же
название «Guidance engine…», то есть продолжения. Уровень раскрытия у семьи выше, чем у всего,
что нашла версия 08.09.

### Дословные цитаты — ставки и долг

> "HID is defined as any loan with an interest rate above a threshold rate, for example. 7% and higher."

> "High Interest Debt (HID): In addition to Emergency Fund, the guidance engine may also provide
> advice to customers on how to tackle their High Interest Debt."

> "Discretionary Income=Net Monthly Income−CME"

> "Debt Pay Rate—the percentage of a customer's discretionary income the FBP Standard recommends
> they allocate towards paying down High Interest Debt."

> "Emergency Fund—the number of Months of CME saved as Liquid Assets. EF = Liquid Assets / CME"

> "Debt Pay Rate is a percentage of discretionary income between 0 and 10% depending on the FBP
> Standard recommendation."

### 🔴 Avalanche и Snowball — присутствуют явно

> "tackling debt with the highest interest rate first or by paying down debt with the smallest
> revolving balance first."

> "Avalanche/Snowball/ Minimum" [перечислены как paydown strategies]

Это **прямое опровержение** тезиса версии 08.09 «avalanche/snowball не встречаются ни в одном
первичном источнике класса». Они не встречались в заброшенной заявке Sosna; в выданном патенте
Capital One они названы поимённо.

### Размен «долг vs резерв» — дословно

> "Customer should allocate funds to either Emergency Fund, Debt Paydown, or both."

Критерий размена реализован **деревом решений по сегментам**, не оптимизацией. Claim 1 дословно:

> "a decision tree engine comprising: ... determine, based on the first output data, the second
> output data, and the third output data, a financial action for the user, wherein determining the
> financial action **determines results for each branch of a decision tree** that associates the
> financial action with combinations of values of the estimated committed monthly expenses, the
> estimated monthly income, the estimated emergency fund level, and the estimated high interest
> debt level"

Сегментация — «emergency fund levels and debt load (None/Moderate/High)» с действием на каждую
комбинацию. То есть: **таблица правил над дискретными уровнями, а не перебор 66 альтернатив
с SAW-свёрткой.** Норма распределения — фиксированный процент от discretionary income,
подобранный по сегменту, а не результат ранжирования.

### Что у Capital One есть, чего нет у остальных — оценка неопределённости входа

Claim 1 содержит явный слой доверия к оценкам, чего нет ни в одном источнике версии 08.09:

> "third output data associated with a confidence score, wherein the third output data comprises:
> data indicating a **variability score** for each of the estimated committed monthly expenses, the
> estimated monthly income, the estimated emergency fund level, and the estimated high interest debt
> level, wherein the variability score is based on **a ratio of an interquartile range (IQR) or
> standard deviation to a value**... and data indicating a **reasonableness score** for each..."

Это разброс оценки входных величин (IQR/σ к значению), а НЕ квантильный прогноз результата
(p10–p90 по Монте-Карло). Граница с моделью FINPILOT сохраняется, но она тоньше, чем считалось.

---

## 2. 🔴 AIG / Corebridge Financial — US11138577B2 (ВЫДАН, ACTIVE)

URL (открыт): https://patents.google.com/patent/US11138577B2/en

| Атрибут | Значение |
|---|---|
| Название | System, method, and computer program product for automatically managing periodic debt payments and savings contributions |
| Правообладатель | "Corebridge Financial Inc (current); American International Group Inc (original)" |
| Изобретатель | "Joseph F. Duronio" |
| Приоритет | "2016-09-19" |
| Статус | **"Active, expires 2039-02-10"** |

### 🔴 Явный критерий размена по ставке против доходности накоплений — дословно

> "The payment allocation module includes a computer executable allocation code segment configured
> to **apportion the payment election into a debt portion and a savings portion**."

> "if the interest rates of the loans are high, for example, the automatic allocation can weigh in
> favor of the debt portion of the payment election being applied to such loans. When the interest
> rates (which may be variable) of the outstanding loans is low, dollars in excess of the minimum
> loan payment(s) can be allocated to the savings account."

> "the allocation module of a payment management program constructed according to principles of the
> present disclosure is configured to allocate the portion of the payment election in excess of any
> required minimum loan payments to **the highest interest loan(s) or the savings account based on
> one or more metrics, such as, the expected return of the funds in the savings account**"

**Это ровно тот размен, который версия 08.09 объявила нераскрытым ни у кого:** ставка по долгу
против ожидаемой доходности резерва, с приоритетом highest-interest loan (avalanche по смыслу).
Раскрыт качественно (направление размена), не количественно — конкретной формулы порога,
весов и точки безразличия в процитированных фрагментах нет.

Оговорка о классе: AIG/Corebridge — страховщик/пенсионный провайдер, а НЕ вендор PFM-движка
банкам. Для темы №11 (вендоры B2B) это соседний класс, но для главного вопроса («считает ли
хоть кто-нибудь размен с учётом ставок») источник засчитывается.

---
## 3. Strands — ЖИВ. Прошлый заход стучался не в тот домен

🔴 Версия 08.09 записала: «`getstrands.com` недоступен и через WebFetch, и через `curl`
(TLS handshake failure). Ни одной страницы получить не удалось.» **Причина — устаревший домен,
а не смерть компании.** Живой домен — `strands.com`.

Что установил живой поиск:

- **Strands поглощена CRIF** (глобальное кредитное бюро). Объявлено 30.03.2020, сделка закрыта
  02.04.2020. Бренд сейчас — «Strands by CRIF».
  Источники в выдаче: https://strands.com/news/crif-to-acquire-strands/ ,
  https://www.finextra.com/newsarticle/35536/crif-acquires-pfm-firm-strands ,
  https://www.crif.ie/news-resources/news/crif-signs-agreement-for-the-acquisition-of-100-of-strands-inc-to-create-a-worldwide-digital-solutions-provider-for-open-banking-business/
- Основана 2004; по выдаче — «more than 700 implementations to date globally»,
  «over 70,000,000 users worldwide».

### Продуктовая страница Lighthouse (открыта живьём)

URL: https://www.strands.com/ai-finance-suite/lighthouse/

Дословно о механике:

> "Lighthouse combines **rule‑based logic and machine learning** to classify transactions, identify
> merchants and detect recurring patterns"

> "Activate insights and personalized communications in real time based on behavioural triggers and
> financial events" — через "**event‑driven logic**"

> "automated saving tools, real-time progress tracking, and personalized recommendations"

Названные модули: Transaction Data Enrichment · Financial Intelligence and Segmentation ·
Proactive, Real-time Engagement Engine · Smart Saving & Money Management Box.

**Вывод по Strands:** та же архитектура, что у всех в версии 08.09 —
обогащение + сегментация + триггерные инсайты. Прогноза, долговой приоритизации по ставке
и перебора альтернатив на публичной странице нет. Пробел версии 08.09 закрыт: Strands
**не является** контрпримером, но теперь это установлено по прочитанной странице, а не по
недоступности домена.

Упомянут (не открыт) developer portal с «full API Catalog and tutorials» — кандидат
на добор, точный URL из выдачи не получен.

---

## 4. Meniga — найден долговой виджет с планом погашения

Из живой выдачи (страница https://www.meniga.com/products/smart-savings/ в выдаче;
дословная цитата со страницы НЕ получена — засчитываю как непроверенное утверждение выдачи):

> Meniga offers a **Debts widget** that enables customers to see all their debts in one place and
> create a **payoff plan**.

🟡 Это указатель, а не факт: формулировка принадлежит агрегатору выдачи, не открытой странице.
Требует прямого открытия. Патента Meniga по запросу «debt savings recommendation engine»
в выдаче **не найдено** — выдача вернула чужие патенты (Opera Solutions US9792653B2 «Recommender
engine for collections treatment selection», IBM, Hartford Fire Insurance). То есть отрицательный
результат версии 08.09 по патентам Meniga **подтверждается живым поиском**, а не только
недоступностью Google Patents.

---

## 🔴 СОСТОЯНИЕ КАНАЛОВ

- **WebSearch: исчерпан после 7 запросов** (хук проекта: «WebSearch исчерпан (израсходовано
  7 из 400)»). Дальше — `curl html.duckduckgo.com` и прямой WebFetch.
- Google Patents через WebFetch — **работает** (в отличие от 08.09, когда отдавал 503).
- freepatentsonline — работает.

---
## 5. Yodlee — пробел версии 08.09 закрыт, developer-портал открыт

Версия 08.09: «`www.envestnet.com/yodlee/products` — 404… документация "Cashflow Analysis" /
"FinCheck" **не подтверждена**. Требует отдельного прохода.»

Живой URL найден через `curl html.duckduckgo.com` (HTTP 202, работает) и открыт:
https://developer.yodlee.com/products/yodlee/core-apis/docs/api-reference

Полный список разделов API (дословно из портала):

> Accounts · Auth · Cobrand · Configs · Consents · DataExtracts · **Derived** · Documents ·
> Holdings · ProviderAccounts · Providers · Risk Analytics · Statements · Transactions · User ·
> User Documents · Verification

Раздел **Derived** — три эндпоинта, дословно:

> "Get Networth Summary" · "Get Transaction Summary" · "Get Holding Summary"

🔴 **Продуктов «Cashflow Analysis» и «FinCheck» в текущем API-референсе НЕТ.** Аналитический
слой Yodlee сводится к трём сводкам (нетто-стоимость, свод транзакций, свод активов) плюс
Risk Analytics (андеррайтинг). Ни прогноза баланса, ни рекомендаций, ни долговой приоритизации
в списке эндпоинтов не значится.

Гипотеза версии 08.09 о существовании FinCheck/Cashflow Analysis — **не подтверждена по живой
документации**. Возможно, это снятые с продажи продукты; исторические страницы не искал.

---

## 6. 🇷🇺 Российский контур — первый заход (версия 08.09 не смотрела вовсе)

### 6.1. РСХБ — PFM собственной разработки, май 2026 (первичный источник, открыт)

URL (открыт через `curl -k`, HTTP 200): https://www.rshb.ru/news/29052026-000002
Дата: **29 мая 2026**.

Дословно:

> «В мобильном приложении РСХБ появился новый сервис персонального финансового анализа (PFM),
> который помогает клиентам контролировать расходы, планировать бюджет и достигать финансовых
> целей. **Решение разработано командой банка** и основано на применении инструментов
> искусственного интеллекта.»

> «Пользователям доступны функции анализа финансового состояния, включая отображение структуры
> баланса по валютам, динамику изменения средств на счетах, а также визуализацию расходов
> и поступлений по категориям.»

> «Отдельное внимание уделено постановке финансовых целей. Клиенты могут формировать персональные
> стратегии накоплений, а встроенные инструменты искусственного интеллекта помогут подобрать
> рекомендации для более эффективного достижения поставленных задач.»

> «В сервис также интегрирован персональный финансовый календарь. Он позволяет отслеживать
> ключевые финансовые события: поступление заработной платы, выплаты процентов по вкладам,
> **платежи по кредитам**, коммунальные услуги, налоги и штрафы. Пользователи будут заранее
> получать уведомления о предстоящих операциях.»

Зампред правления Елена Батурова, дословно:

> «Благодаря функциональности нового сервиса Банк получает аналитику поведенческих паттернов
> клиентов, что позволяет предлагать только релевантные продукты и таргетированные предложения.
> При этом клиенты получают удобные инструменты для автоматизированного контроля денежных средств,
> **моделирования финансового состояния** и формирования персональной стратегии достижения
> финансовых целей».

**Что это даёт для FINPILOT:**
- 🔴 Свежайший (май 2026) образец того, что считается PFM-планкой у крупного банка РФ:
  категоризация + структура баланса + цели + календарь событий + уведомления.
- Кредиты фигурируют **только как календарные платежи**, не как объект оптимизации.
  Размена «гасить или копить» нет.
- **Разработано внутри банка, не куплено у вендора** — прямое указание на устройство рынка РФ.
- Целевая функция банка названа честно: «предлагать только релевантные продукты и таргетированные
  предложения», то есть PFM — канал кросс-сейла. Это ровно тот конфликт интересов, от которого
  FINPILOT свободен как независимый продукт.

### 6.2. Прочие российские кандидаты (найдены, не разобраны)

- **Abanking** (группа Artsofte), https://abanking.ru/ — вендор фронт-офиса ДБО для банков РФ,
  в выдаче фигурирует с модулем «Интернет-банк для физ.лиц» и презентацией
  https://about.abanking.ru/sites/default/files/presentations/Abanking%20-%20Welcome%20презентация.pdf
  (не открыты). Класс — **фронт-офис ДБО**, не движок рекомендаций; PFM у такого вендора
  обычно виджет, а не математика. Требует проверки.
- Поиск по «ЦФТ / BSS / EasyFinance / Дзен-мани как B2B-PFM» **выполнить не удалось**:
  `html.duckduckgo.com` начал отдавать пустую страницу-заглушку (HTTP 202, 14 КБ, ноль
  результатов) — троттлинг после ~6 запросов. `lite.duckduckgo.com/lite/` работал дольше
  (HTTP 200, 24 КБ, результаты есть), но тоже начал возвращать пустые выдачи.
- `arb.ru` (перепечатка пресс-релиза РСХБ) — **гео-блок**: "Sorry, the page you are looking for
  is currently unavailable for your region." Обойдено чтением оригинала на `rshb.ru`.

**Статус российского контура: заход сделан, тема НЕ закрыта.** Один первичный источник (РСХБ),
один кандидат-вендор (Abanking) не проверен, крупные вендоры банковского ПО РФ (ЦФТ, Диасофт,
BSS, R-Style) не проверены вовсе.

---

## 7. 🔴 Capital One — семейство «Guidance engine» разобрано ПОШТУЧНО

Продолжение прогона после обрыва по лимиту. Разобраны оба продолжения US11023967B1.
Каналы: `patents.google.com` через WebFetch (HTTP 200, но малая модель не отдаёт claims
дословно) → **freepatentsonline через `curl -L`** (HTTP 200, 188 КБ и 189 КБ соответственно) —
именно оттуда взяты дословные тексты формулы изобретения ниже.

### 7.1. US11669897B2

URL (открыт): https://patents.google.com/patent/US11669897B2/en
URL (открыт, полный текст claims): https://www.freepatentsonline.com/11669897.html

| Атрибут | Значение (дословно) |
|---|---|
| Название | "Guidance engine: an automated system and method for providing financial guidance" |
| Правообладатель | "Capital One Services LLC" |
| Изобретатели | "Katharine Schlesinger, John Rush, Zheyu Yang, Matthew Davis" |
| Приоритет | "November 12, 2019" |
| Статус | **"Active, expires 2040-01-10"** |

**Независимый пункт 1 — дословно и целиком** (система из двух движков):

> "1. A system comprising:
> a data integration engine comprising: one or more first processors; and first memory storing
> first instructions that, when executed by the one or more first processors, cause the data
> integration engine to:
> receive, via a guidance user interface, first input data associated with a user, wherein the
> first input data associated with the user comprises data corresponding to a user's monthly
> expenses, monthly income, emergency fund level, or high interest debt level;
> receive, from one or more data servers, second input data associated with the user, wherein the
> second input data associated with the user comprises data corresponding to a user's monthly
> expenses, monthly income, emergency fund level, or high interest debt level;
> optimize the second input data by integrating the first input data into the second input data;
> generate, based on the optimized second input data, first output data associated with an
> estimated committed monthly expenses of the user and an estimated monthly income of the user,
> wherein the estimated committed monthly expenses are associated with a total monthly fixed
> expense incurred by the user to cover essential needs, and the estimated monthly income
> comprises a gross income or a net income; and
> generate, based on the optimized second input data, second output data associated with an
> estimated emergency fund level of the user and an estimated high interest debt level of the
> user, wherein the estimated emergency fund level is based on an amount of liquid assets
> available to cover the estimated committed monthly expenses, and wherein the estimated high
> interest debt level is associated with one or more loans with interest rates above a pre-set
> threshold; and
> a decision tree engine comprising: one or more second processors; and second memory storing
> second instructions that, when executed by the one or more second processors, cause the decision
> tree engine to:
> receive, from the data integration engine, the first output data ... and the second output data ...;
> determine, based on the first output data and the second output data, a financial action for the
> user, wherein determining the financial action **determines results for each branch of a decision
> tree** that associates the financial action with combinations of values of the estimated committed
> monthly expenses, the estimated monthly income, the estimated emergency fund level, and the
> estimated high interest debt level; and
> cause, via the guidance user interface, an output of the financial action, the estimated committed
> monthly expenses, the estimated monthly income, the estimated emergency fund level, and the
> estimated high interest debt level."

🔴 **Ключ ко всему семейству — зависимый пункт 6. Пространство решений явно конечно и мало:**

> "6. ... generate a **twelve-cell matrix** based on an estimated high interest debt load of
> (1) none, (2) moderate, and (3) high, and an estimated emergency fund level of (1) less than one
> month of the estimated committed monthly expenses, (2) less than three months ..., (3) less than
> six months ..., and (4) greater than six months of the estimated committed monthly expenses."

То есть 3 уровня долга × 4 уровня резерва = **12 клеток, по одному предписанному действию
в каждой**. Не перебор распределений, не оптимизация — таблица.

Пункт 5 (что именно считается по резерву) — дословно:

> "5. ... an emergency fund savings goal based on a monetary value of one, three, or six months of
> committed monthly expenses; an emergency fund shortfall based on an amount the user needs to save
> to reach the emergency fund savings goal; an **emergency fund save rate based on as a percentage
> of a discretionary income** the user allocates to the emergency fund level; or an emergency fund
> timescale based on a number of months to achieve the emergency fund savings goal."

Пункт 7 — слой доверия к входу (variability + reasonableness), формулировка совпадает с
US11023967B1, цитата уже приведена в §1.

Пункт 4 / 11 — источники входных данных, дословно:

> "user augmented data; merchant category code; **credit bureau data**; geographic benchmark
> estimates; a cost of living estimate; or a housing cost estimate."

### 7.2. US12008644B2

URL (открыт): https://patents.google.com/patent/US12008644B2/en
URL (открыт, полный текст claims): https://www.freepatentsonline.com/12008644.html

Название, правообладатель, изобретатели, приоритет — идентичны. Статус: **Active**.

Независимый пункт 1 — дословно (заметно ШИРЕ, чем у 11669897: интеграция внешних данных
уехала в зависимый пункт 3, а в независимом остался только конвертер формата + дерево):

> "1. A system comprising:
> a data integration engine comprising: one or more first processors; and first memory storing
> first instructions that, when executed by the one or more first processors, cause the data
> integration engine to: determine user data associated with an estimated monthly expenses of a
> user, an estimated monthly income of the user, an estimated emergency fund level of the user, and
> an estimated high interest debt level of the user, wherein at least a portion of the user data is
> in a non-compliant format; and convert the portion of the user data in the non-compliant format
> into a compliant format;
> a decision tree engine comprising: one or more second processors; and second memory storing
> second instructions that, when executed by the one or more second processors, cause the decision
> tree engine to: receive, from the data integration engine, the user data having the converted
> portion; determine, based on the user data having the converted portion, a financial action for
> the user, wherein determining the financial action comprises **determining results for each branch
> of a decision tree** that associates the financial action with combinations of values of the
> estimated monthly expenses, the estimated monthly income, the estimated emergency fund level, and
> the estimated high interest debt level; and cause, via a guidance user interface, an output of the
> financial action."

Пункт 2 — порог по ставке вынесен в зависимый пункт:

> "2. ... the estimated high interest debt level is associated with a loan with **an interest rate
> above a pre-set threshold**."

Пункт 10 — та же двенадцатиклеточная матрица, дословно тот же текст, что в 11669897 п.6.
Пункт 4 — variability/reasonableness score, дословно та же формулировка (IQR или σ к значению).

### 7.3. 🔴 Описание (общее для семьи): формула нормы и стратегии погашения

Дословно из описания (freepatentsonline, оба патента):

> "Monthly Payments—the sum of a customer's current total minimum payments and the amount associated
> with their debt paydown rate that may be calculated as: **Minimum Payment+(Debt Pay Rate\*Discretionary
> Income)**"

> "Cost and Time to paydown debt based on one of many various paydown strategies—the guidance engine
> may calculate values based on different priorities. For example, tackling debt with the highest
> interest rate first or by paying down debt with the smallest revolving balance first."

Таблица параметров модели содержит строки (дословно, из описания обоих патентов):

> "Strategy Paydown Strategy used ... **Avalanche/Snowball/Minimum**"

> "APR Paydown calculations done ... **0 or 7 Cutoff for either HID (>7% APR) or All debts (>=0% APR)**"

> "Debt Accts Dictionary of each of the associated debt accounts, **their paydown timescales, cost,
> interest cost, etc.**"

> "Lump Payment (for Minimum/Snowball/Avalanche Debt Paydown Strategies) ... 2. If they have less
> than <3 CME saved up or <3 months Liquid assets of payable debt, then it is set to 0. ... 4. If
> they have >3 CME and >3 months of payable debt, the value is set to **Liquid Assets−3\*CME**.
> (Bringing them down to 3 CME of savings)."

🔴 Последняя цитата — **точка размена «долг vs резерв» в явном численном виде**: единовременный
взнос в погашение равен ликвидным активам сверх трёхмесячного резерва, и он равен нулю, пока
резерв меньше трёх CME. Это правило-порог, а не оптимизация, но численно определённое.

### 7.4. Чего в семействе Capital One НЕТ (проверено поиском по полному тексту обоих патентов)

Поиск по полному тексту (freepatentsonline, оба документа) по ключам:

| Ключ | Вхождений |
|---|---|
| `Monte` | **0** |
| `simulat` | **0** |
| `scenario` | **0** |
| `risk profile` | **0** |
| `rank` | 1 — и относится **к пользователю, а не к альтернативам** |

Единственное вхождение `rank`, дословно:

> "the decision tree system may perform an intermediate calculation based on the user's emergency
> fund level and high interest debt level, and then **ranks the user** based on the initial
> calculation and the intermediate calculation using a financial best practices standard to
> determine a suggested next financial action step."

**Это ранжирование ПОЛЬЗОВАТЕЛЯ по сегментам, а не ранжирование вариантов распределения.**
Различение критично для новизны FINPILOT: у Capital One один выход на клетку матрицы;
множества альтернатив, по которому идёт свёртка, в патентах нет вовсе.

`weight` встречается только в одном контексте — веса при агрегации оценок разброса входных
данных, дословно:

> "When multiple components are combined for certain calculations (e.g., CME is a combination of
> Food, Medical, Housing costs, etc.), their variability scores are weighted to determine the
> variability score for the final value."

Это веса в оценке качества ВХОДА, а не веса критериев в свёртке решений.

### 7.5. Итог по Capital One

| Признак ядра FINPILOT | Есть у Capital One? |
|---|---|
| Учёт процентных ставок по долгу | **Да**, порог 7% APR, avalanche/snowball названы |
| Численный критерий «гасить или копить» | **Да**, но как правило-порог: Lump = Liquid Assets − 3×CME |
| Норма распределения свободного потока | **Да**, но фиксированный % (0–10%) от discretionary income по сегменту |
| Множество альтернатив распределения (шаг 10%) | **Нет** |
| Ранжирование альтернатив (SAW/свёртка) | **Нет** — ранжируется пользователь, не варианты |
| Веса критериев / профиль риска | **Нет** (`risk profile` — 0 вхождений) |
| Вероятностный прогноз (Монте-Карло, квантили) | **Нет** (`Monte`/`simulat`/`scenario` — 0 вхождений) |
| Оценка неопределённости ВХОДА | **Да** (IQR/σ, reasonableness) — у FINPILOT этого нет |

---

## 8. 🔴 Патентные портфели вендоров — сплошная проверка по правообладателю

Канал: **XHR API Google Patents**, `https://patents.google.com/xhr/query?url=q%3Dassignee%3D"<имя>"`
(HTTP 200, машинночитаемый JSON). Это принципиально надёжнее выдачи поисковика: возвращает
`total_num_results` по правообладателю, то есть отрицательный результат становится **измеренным**,
а не «не нашлось».

Запросы без кавычек вокруг имени вырождаются в полнотекстовый поиск (`assignee=MX Technologies`
вернул 41 824 результата вида «Mobileye», «Intel»); ниже приведены только результаты
запросов **с кавычками**, то есть настоящий фильтр по правообладателю.

| Правообладатель | `total_num_results` | Что в портфеле |
|---|---|---|
| **"Personetics"** (без кавычек — точный матч) | **1** | единственный патент, и тот не про финансы |
| **"Moneythor"** | **0** | патентов нет вовсе |
| **"Tink AB"** | **0** | патентов нет вовсе |
| **"Meniga"** | **1** — и он чужой (Prodotti Antibiotici, 1966, лизоцим при раке) | фактически **0** |
| **"Envestnet Inc"** | **0** | патентов нет вовсе |
| **"MX Technologies"** | 14 | агрегация, маршрутизация, шифрование |
| **"Plaid Inc"** | 12 | парсинг данных, fingerprint, антифрод |
| **"Yodlee Inc"** | 30 | оплата счетов, синхронизация портфелей, маскирование |
| **"Strands Inc"** | 6 | музыкальные рекомендации + один финансовый (см. §9) |

### 8.1. 🔴 Personetics: единственный выданный патент — НЕ про финансовые рекомендации

Дословно из ответа API:

> `"publication_number":"US9495962B2"`, `"assignee":"Personetics Technologies Ltd."`,
> `"grant_date":"2016-11-15"`, `"priority_date":"2011-09-19"`,
> `"inventor":"David D. Govrin"`,
> title: `"System and method for evaluating intent of a human partner to a dialogue"`,
> snippet: `"A system and method for assigning relative scores to various possible intents on the
> part of a user approaching a virtual agent, the method comprising predicting priority topics,
> including gathering first data and employing the first data to discern and seek user confirmation
> of at least one ..."`

**Вывод, важный для новизны FINPILOT:** у Personetics — признанного лидера рынка «умных
финансовых инсайтов» для банков — **ноль выданных патентов на финансовый движок**. Единственный
патент 2016 года описывает распознавание намерения в диалоге с виртуальным ассистентом, то есть
чат-бот. Заявка Sosna US20220253817A1 (единственная финансовая) — заброшена, это зафиксировано
версией 08.09. Ответ на вопрос задания «есть ли у Personetics выданные патенты помимо
заброшенной заявки» — **есть ровно один, и он к предмету не относится**.

### 8.2. Meniga, Tink, Moneythor, Envestnet — патентов нет

Гипотеза версии 08.09 «Meniga патентов не имеет» — **подтверждена измерением**, а не отсутствием
доступа. То же для Tink (куплен Visa), Moneythor и Envestnet как юрлица.

Практический смысл: **ядро PFM-рынка патентно пусто.** Вендоры не патентуют математику
рекомендаций — либо потому что её нет (правила и триггеры непатентоспособны как тривиальные),
либо потому что держат как коммерческую тайну. Единственные содержательные патенты класса
принадлежат **банкам и страховщикам** (Capital One, AIG/Corebridge), а не вендорам движков.

### 8.3. MX / Plaid / Yodlee — портфель инфраструктурный, не аналитический

Заголовки патентов MX (дословно): "Aggregation based credit decision" · "Payment processing" ·
"Secure data handling and storage" · "Optimizing aggregation routing over a network" ·
"Long string pattern matching of aggregated account data" · "Automated data supplementation and
verification" · "Securing data based on randomization".

Plaid (дословно): "System and method of filtering internet traffic via a client fingerprint" ·
"System and method for assessing a digital interaction with a digital third party" ·
"Systems and methods for data parsing" · "System and method for maintaining internet anonymity
via client fingerprint".

Yodlee (дословно): "Layered masking of content" · "System and method for syndicated transactions" ·
"Interactive bill payment center" · "Interactive transaction center interface" · "Portfolio
synchronizing between different interfaces" · "Method and system for increasing client
participation in a network-based bill payment system" · "Host exchange in bill paying services".

**Ни одного патента на движок рекомендаций, распределение средств или долговую приоритизацию
ни у одного из трёх.** Это согласуется с §5 (в живом API-референсе Yodlee аналитика сведена
к трём сводкам).

### 8.4. Strands — единственный финансовый патент, и тот заброшен

URL (открыт, HTTP 200, 323 КБ): https://patents.google.com/patent/US20120059751A1/en

| Атрибут | Значение (дословно) |
|---|---|
| Название | "Systems and methods for managing and allocating funds" |
| Правообладатель | "Strands Inc" |
| Изобретатели | "Rick Hangartner, Philip Jenkins" |
| Приоритет | "2010-09-08" |
| Статус | **"Abandoned"** |

Реферат дословно:

> "The application discloses a systems and methods for automatically managing and allocating funds
> deposited in one or more financial accounts owned by the user. The system allows the user to
> specify and dynamically modify multiple savings goals and to associate each goal with a savings
> account..."

Это **распределение свободных средств между несколькими целями с приоритетами** — ближайшее к
FINPILOT из всего, что нашлось у вендоров. Приоритет задаётся пользователем, дословно:

> "the user may assign a categorical priority that indicates how important achieving the goal is to
> the user. Typical categorical priorities in an embodiment may be H(igh), M(edium), or L(ow). Other
> embodiments may allow the user to explicitly **rank-order goals**."

Есть даже формула распределения избытка по «профилю предпочтений» PP, выведенному из истории:

> "excess funds above these three categories of allocations are distributed to all goals as
> PA_i ← MA_i + PP_i·TA ... a preliminary allocation PA is derived across the goals in G with
> minimum inferences on the available history data. the preference profile PP is derived by only
> looking at the period in time in which the user had explicitly ranked the goals in G>0 by making
> allocations to them."

🔴 **Но ключевого нет.** Поиск по полному тексту документа:

| Ключ | Вхождений |
|---|---|
| `interest rate` | **0** |
| `optimiz` | **0** |
| `utility` | **0** |

Долг фигурирует только как разновидность цели накопления, дословно:

> "These goals can be for a future purchase, or for **paying off a small debt** they have collected."

То есть: распределение по целям — да, приоритеты — да (заданные вручную), **ставки — нет,
оптимизация — нет, перебор вариантов — нет**. Плюс документ заброшен: юридически ничего не
блокирует.

---

## 9. 🔴 ГЛАВНЫЙ ВОПРОС — измерение по всему мировому патентному массиву

Канал: XHR API Google Patents, полнотекстовый поиск по всем юрисдикциям. Ценность именно
в числе `total_num_results`: это **измеренный ноль**, а не «не нашлось».

| Запрос (дословно как отправлен) | `total_num_results` | Что вернулось |
|---|---|---|
| `"plurality of candidate allocations" "interest rate"` | **0** | — |
| `"simple additive weighting" finance debt` | **0** | — |
| `"avalanche" "snowball" "emergency fund" allocation interest` | **1** | **только** US11023967B1 Capital One |
| `"Monte Carlo" "debt repayment" "emergency fund" allocation` | 3 | Intuit US20190378207A1 (abandoned) + два китайских промышленных |
| `"ranking" "allocation" "debt repayment" "savings goal" "interest rate"` | 2 | Wallupt WO2017205463A1, Wells Fargo US20260087556A1 |
| `"multi-criteria" "personal finance" "debt" "savings" recommendation` | 1 | US20070011071A1 (частное лицо, 2007) |
| `"plurality of allocation scenarios"` | 634 | всё вне финансов (планировщики задач, облако, СХД) |

### 9.1. Ответ на главный вопрос

**Считает ли кто-нибудь размен «гасить долг или копить» с учётом ставок — ДА.** Три источника,
все выданные и активные:
1. Capital One (семейство из трёх патентов) — порог 7% APR, avalanche/snowball, Lump = Liquid
   Assets − 3×CME.
2. AIG/Corebridge US11138577B2 — ставка по кредиту против ожидаемой доходности накоплений.
3. (косвенно) — больше никого; выше — исчерпывающий список по результатам полнотекстового поиска.

**Раскрывает ли кто-нибудь ПЕРЕБОР вариантов распределения с РАНЖИРОВАНИЕМ — НЕТ, ни один
источник.** Измерено тремя независимыми способами:
- `"plurality of candidate allocations" "interest rate"` → 0 документов в мире;
- `"simple additive weighting" finance debt` → 0 документов в мире;
- в семействе Capital One `rank` встречается ровно один раз и относится к ранжированию
  **пользователя** по сегменту, а не вариантов (§7.4).

### 9.2. Intuit US20190378207A1 «Financial health tool» — почему он НЕ контрпример

URL (открыт, HTTP 200, 405 КБ): https://patents.google.com/patent/US20190378207A1/en
Правообладатель — Intuit Inc., приоритет 2018-06-07, статус **"Abandoned"**.

Монте-Карло там есть, но применён к другому, дословно:

> "financial health service 122 may use a time-series model (e.g., ARIMA, exponential smoothing,
> recurrent neural networks, deep-learning time series, etc.) or a simulation (e.g., **a Monte Carlo
> simulation**) to **predict an expected value for the amount of a cash payment and an expected value
> for the date when the cash payment might occur** and might also provide a measure of uncertainty
> associated with the predicted expected values (e.g., a confidence interval, a range, a standard
> deviation, etc.)."

То есть симуляция — для прогноза **отдельного платежа**, не для оценки последствий распределения.

Слово `rank` там относится к **анкете о поведенческих склонностях**, дословно:

> "user device 150 may ask how the user would approach paying off debt. User device 150 may provide
> a series of options which may be **selected and/or ranked by the user**. For example, user device
> 150 may suggest some or all of the following non-limiting possible responses: automatically move
> $5/week towards debt, automatically transfer tax refund or bonus to debt payment, set aside
> leftover money at the end of the month to pay debt, get a second job or side hustle to put towards
> debt..."

Ранжирует **пользователь вручную**, и ранжирует не суммы, а поведенческие приёмы. Поиск по
полному тексту: `interest rate` — **0 вхождений**. Долг без ставки — значит, размена нет
в принципе.

🟢 **Это ближайший найденный аналог по набору слов (Монте-Карло + долг + резерв + ранжирование)
и одновременно доказательство, что совпадение поверхностное.**

---

## 10. 🔴 Guidance engine в ЖИВОМ продукте Capital One — следов НЕТ

Задание: «одно дело формулировка в патенте, другое — работающий продукт». Проверено по трём
каналам, все страницы открыты.

### 10.1. Страница цифровых инструментов Capital One (открыта)

URL: https://www.capitalone.com/learn-grow/money-management/digital-tools-manage-money/

Полный перечень названных в приложении инструментов (дословно со страницы):
**Eno** — "chat or text with Eno and get insights into payment due dates or unusual account
activity"; **CreditWise** — "shows recently reported account balances in your credit report and
helps you track your credit utilization"; **Virtual Cards** — "shop securely online without needing
your physical card on hand"; **Card Lock** — "lock a lost or stolen card to help prevent fraudulent
purchases"; **Subscription Management** — "view a snapshot of upcoming bills, manage subscriptions
paid with your Capital One card"; **Fraud Alerts** — "proactive fraud alerts... instant purchase
notifications that let you monitor transactions in real time".

🔴 **Ни одного инструмента, распределяющего деньги между погашением долга и накоплением.**
Ближе всего CreditWise, и он про кредитный рейтинг и утилизацию лимита, а не про размен.

### 10.2. «Financial Game Plan» (открыта) — это редакционный контент, не фича

URL: https://www.capitalone.com/about/newsroom/financial-game-plan/ , дата **03.09.2026**.

Дословно:

> "The Financial Game Plan is my checklist for working through your financial goals and figuring out
> your next steps."

> "do you have an emergency fund, and how much is in it?"

По долгу рекомендуется метод лавины, дословно: **"list them in order of the highest interest rate
first."** Порядок действий тот же, что в патенте: сначала резерв 3–6 месяцев, потом дорогой долг,
потом инвестиции.

🔴 **Но это статья в ньюсруме, а не описание функции приложения.** Логика Guidance engine
существует у Capital One как **редакционная методичка и как патентная формулировка**;
подтверждения, что она работает внутри продукта как автоматический движок, публично нет.

### 10.3. Что это значит

Разрыв «патент ≠ продукт» для Capital One **зафиксирован фактически**: патент выдан и активен
(семейство из трёх), в публично описанном продукте соответствующей функции нет. Возможные
объяснения (не проверены, гипотезы): фича свёрнута; фича существует только для части клиентов;
патент подан оборонительно. Для FINPILOT практический вывод: **в живых продуктах крупных банков
США размен «долг vs резерв» как автоматический расчёт по-прежнему не наблюдается** — он
существует как совет в статье и как формула в патенте.

---

## 11. Moneythor — техническая страница движка (открыта)

URL (открыт, HTTP 200, 348 КБ, редирект `/platform/` → `/engine/`):
https://www.moneythor.com/engine/

Дословно об устройстве движка:

> "At the core of the Moneythor solution is a high-performance scalable **event-processing and
> orchestration engine** processing real-time and batch data from any assets and liabilities, such
> as accounts, cards, digital wallets, and Open Banking sources."

> "The categorisation process uses several methods including **text analysis, multivariate rules
> based on regular expressions and priority levels, machine learning, external services** where
> applicable."

Публичный портал документации недоступен: `docs.moneythor.com` и `developer.moneythor.com` —
**HTTP 000** (соединение не устанавливается, домены не отвечают), см. «СОСТОЯНИЕ КАНАЛОВ».

**Вывод:** заявленная механика — обработка событий + категоризация правилами и ML. Ни ставок,
ни долговой приоритизации, ни распределения свободного потока на публичной технической странице
нет. Совпадает с патентным результатом (§8: у Moneythor **0 патентов**).

---

## 12. 🇷🇺 Российский контур — продолжение

### 12.1. ОФМ (`opfm.ru`) — не PFM, а маркетплейс. Кандидат отброшен

URL (открыт): https://opfm.ru/

Дословно о продукте: **«Онлайн-сервис, где взаимодействуют финансовые организации и клиенты для
заключения сделок»**. Заявленные функции — единая идентификация по 115-ФЗ, электронные договоры
24/7, хранение документов, снижение затрат front/back office.

Рекомендаций по погашению кредитов, ставкам и распределению средств на сайте нет.
🔴 Аббревиатура вводит в заблуждение: ОФМ = «Открытый Финансовый Маркетплейс», а не PFM.
**Класс — оператор финансовой платформы (маркетплейс), к теме №11 не относится.**

### 12.2. Отраслевые обзоры рынка РФ — оба доступных оказались устаревшими

**«Банковское обозрение», «Как банковские PFM-сервисы участвуют в борьбе за внимание клиента»**
URL (открыт): https://bosfera.ru/bo/kak-bankovskie-pfm-servisy-uchastvuyut-v-borbe-za-vnimanie-klienta
Автор и дата дословно: **«01.06.2015» / «Данил Поминов, Обозреватель "Б.О"»**.
Дословно из доступной части: системы «включают возможности PFM (personal finance management —
управление личными финансами) и (или) PFP (personal financial planning — планирование личных
финансов)». Назван УБРиР как один из внедривших.
🟡 Полный текст закрыт: **«Полная версия доступна только подписчикам»**. Плюс 2015 год —
как срез рынка 2026 непригоден.

**Frank Media, «Личный бухгалтер: что предлагают банки и финтех для управления финансами»**
URL (открыт): https://frankmedia.ru/56644 , дата дословно **«13.12.2021, 16:14»**.
Названы банки: Сбербанк, ВТБ, Тинькофф, МТС банк, Альфа-банк, Почта банк, Русский стандарт.
Названы независимые сервисы: **Easy Finance, Toshl, Drebedengi, CoinKeeper, ZenMoney, Moneylover,
Monefy**.
Функции по банкам: Сбербанк — виртуальный ассистент «Салют», пять механик автонакоплений, цели,
инвестрекомендации; ВТБ — виджет «Единый баланс», рекомендации по налоговым вычетам, заявленная
«Упущенная выгода»; Тинькофф — ассистент Олег (лимиты трат, автоплатежи); МТС банк — расходы
по картам других банков.
🔴 Дословный итог обзора: **«специальных функций по управлению кредитами, расчёту со ставками
и рекомендациями погашения не описано»**.

**Значение для FINPILOT:** на протяжении 2015 → 2021 → 2026 (РСХБ, §6.1) российский PFM
описывается одним и тем же набором: категоризация, цели, автонакопления, календарь, инсайты.
Кредит присутствует как объект учёта и календарного платежа. **Размена «гасить или копить»
со ставками в описаниях российских банковских продуктов не встречается ни в одном году.**

---

## 13. Wells Fargo US20260087556A1 — самый свежий претендент, и он мимо

Найден полнотекстовым поиском (§9). Открыт: https://patents.google.com/patent/US20260087556A1/en
(HTTP 200, 367 КБ).

| Атрибут | Значение (дословно) |
|---|---|
| Название | "Multimodal interactive personal advisor system" |
| Правообладатель | "Wells Fargo Bank NA" |
| Приоритет | "2024-09-24" |
| Статус | **"Pending"** (не выдан) |

**Независимый пункт 1 — дословно:**

> "1. A multimodal interactive personal advisor (MIPA) system comprising: user data circuitry
> configured to retrieve first user data associated with a user, wherein the user is associated with
> a first living location; external data circuitry configured to retrieve **living location data**
> associated with a set of living locations; MIPA management circuitry configured to: facilitate a
> first interaction between the user and an MIPA model; and the MIPA model, wherein the MIPA model
> is configured to: extract, based on the first interaction, a set of data features associated with
> the user; determine, based on the set of data features, second user data; determine, based on the
> first user data and the second user data, a financial status of the user; and determine, based on
> the living location data associated with the set of living locations and the financial status of
> the user, **a second living location for the user**..."

🔴 **Ранжирование там есть — но ранжируются места жительства, а не варианты распределения денег.**
Пункт 6 дословно:

> "6. ... **rank each living location** of the set of living locations based on a set of living
> location attributes associated with the living location data; and determine the second living
> location based on determining the second living location is associated with a **highest rank**
> out of each living location."

> "7. ... the set of living location attributes comprises one or more of transit score data, safety
> data, walkability data, work commute distance, population density data, resident income data, or
> property cost data..."

Это **многокритериальный выбор с ранжированием — но по предмету «куда переехать»**. Ближайшая
формальная конструкция к SAW из найденного, и применена не к деньгам.

Долг и профиль риска — только в описании, не в формуле изобретения. Дословно:

> "the MIPA model 210 may determine that a respective user repeatedly chooses and/or acts upon
> debt-averse goals ... when multiple choices (e.g., multiple opportunities) are presented to the
> user. In such examples, the MIPA model 210 may **heavily weight debt-averse options** when
> presenting choices to the user in the future."

> "the MIPA model 210 may be configured to generate and/or update a **risk tolerance profile**
> associated with the user that defines a user's appetite for risk ... the user prioritizes living
> within modest means, **paying down high interest debts**, and/or paying extra principal on loans
> ... with any 'excess' funds or additional funds they may have outside their usual budget"

> "opportunities (e.g., feasible/actionable plans to achieve goals or subgoals based on
> current/developing financial status, '**pay off high interest debt in six months**'), scenarios
> ... **tradeoffs** (e.g., potential impacts of acting on a particular goal, subgoal, opportunity,
> or action item)"

🟡 Веса здесь — **поведенческие, выученные из истории выборов пользователя** (склонность к
безрисковому/бездолговому), а не веса критериев, заданные профилем риска в модели. И применяются
они к подбору формулировок-подсказок, а не к свёртке численных альтернатив.

**Вывод:** самый близкий по духу документ (2024–2026, «советник», ранжирование, профиль риска,
дорогой долг, tradeoffs) — и всё же не перебор распределений. Плюс он **не выдан**.

### 12.3. 🔴 EasyFinance Platform — единственный найденный НАСТОЯЩИЙ B2B-вендор PFM в РФ

Прямой заход на `easyfinance.ru` — **HTTP 000** (соединение не устанавливается даже с `-k`).
Обойдено через архив, страница получена целиком:
URL (открыт, HTTP 200, 37 КБ): https://web.archive.org/web/2024/https://easyfinance.ru/my/wikiwrapper/bankam

Дословно, что вендор продаёт банку:

> «Внедрение **PFM EasyFinance Platform** приближает Банк к клиенту, укрепляет лояльность
> и создает возможности для новых продаж.»

> «PFM EasyFinance Platform встраивается в существующую систему Интернет-банкинга и работает
> в двух вариантах: **по технологии SaaS** ... или может быть **установлена на серверах Банка**.»

Заявленная выгода банка — дословно:

> «- **Снижение просроченной задолженности по кредитам.** - Снижение нагрузки на call-центр.
> - Снижение издержек на инкассацию, рост безналичных оборотов по картам. - Рост клиентской
> лояльности ... - Повышение благонадежности клиентов — клиенты получают советы и оповещения
> о финансовом состоянии, размере лимитов семейного бюджета, начинают использовать регулярные
> платежи.»

> «Продвижение банковских продуктов на основании анализа данных Клиента ... - Рост кросс-продаж
> и выручки на Клиента. - **Рост продаж продуктов Банка (кредитные карты, депозиты, ипотека)
> через таргетированную рекламу**...»

Что получает конечный клиент — полный список дословно:

> «- Создание финансовых целей и мониторинг их достижения. - **Рекомендации по финансовому
> состоянию** и sms, e-mail оповещения - Информеры, интерактивная система оценки финансового
> состояния. - Версия для iPhone, Android, Windows Phone»

🔴 **Ключевое наблюдение.** Долг фигурирует дважды, и оба раза **как интерес банка, а не клиента**:
«снижение просроченной задолженности» и «рост продаж кредитных карт, депозитов, ипотеки». Функции
«помочь клиенту дешевле выйти из долга» нет вовсе. Клиентская часть — цели, оповещения, информеры.

Это второе — после РСХБ (§6.1) — прямое подтверждение устройства рынка РФ: **российский PFM
продаётся банку как канал кросс-сейла и снижения просрочки, и целевая функция движка —
интерес банка.** Независимая СППР, оптимизирующая выгоду пользователя (в том числе советуя
не брать кредит), в этой бизнес-модели не может появиться в принципе — не потому что сложно,
а потому что не оплачивается.

### 12.4. Вакансия команды PFM Сбербанка — состав функций изнутри

🟡 Источник получен **через выдачу поиска, страница вакансии `careerist.ru` не открылась**
(отдала главную страницу каталога, не карточку). Засчитываю как непроверенное утверждение выдачи,
не как дословную цитату первоисточника.

По выдаче: вакансия «Java (PFM)», Сбербанк, Новосибирск, опубликована **13.05.2026**. Описание
команды по выдаче: «Молодая команда PFM внутри Сбербанка занимается разработкой и внедрением
сервисов по управлению своими финансами в Сбербанк Онлайн, включая **анализ финансов, бюджет,
цели, конверты, копилки, инвестиционное профилирование и автоконсультирование**».

Даже в этом (непроверенном) перечне обращает на себя внимание состав: анализ, бюджет, цели,
конверты, копилки — то есть **накопительный контур**. Кредитного контура в перечне нет вовсе;
«инвестиционное профилирование» относится к инвестициям, а не к разменy долг/резерв.
Требует дооткрытия карточки вакансии, см. «СОСТОЯНИЕ КАНАЛОВ».

---

## 14. 🔴 Техдокументация вендоров — схемы ответов эндпоинтов (задание §6)

Вопрос задания: «чем оперирует движок — суммой, подсказкой из библиотеки или ранжированным
списком». По MX получен **прямой ответ из схемы полей**.

### 14.1. MX — эндпоинты Insights: движок оперирует ТЕКСТОМ ИЗ ШАБЛОНА

URL (открыт, HTTP 200, 445 КБ): https://docs.mx.com/api-reference/platform-api/reference/insights

Перечень эндпоинтов дословно:

> GET "List insights by account" · GET "List all insights for a user" · GET "List all categories
> associated with an insight" · GET "List all accounts associated with an insight" · GET "List all
> merchants associated with an insight" · GET "List all scheduled payments associated with an
> insight" · GET "List all transactions associated with an insight" · GET "Read insight" ·
> PUT "Update insight" · GET "List insights by transaction"

Полная схема объекта `insight` (дословно, значимые поля):

> `description` String — "The human-readable information being delivered to the end user."
> `title` String — "The title for the specific insight, for example, Price Increase or Paycheck Deposit."
> `template` String — "A short label for the type of insight being delivered, for example,
> **SubscriptionPriceIncrease**, **MonthlyCategoryTotal**, and more."
> `micro_call_to_action` String — "Returns a micro CTA if the insight template supports micro copy."
> `micro_description` String — "A shorter version (300 characters or less) of description."
> `cta_clicked_at`, `has_been_displayed`, `is_dismissed` — телеметрия показа и клика.

🔴 **В схеме инсайта НЕТ ни одного числового поля результата**: ни суммы, ни ставки, ни оценки,
ни ранга, ни уверенности. Есть заголовок, текст, метка шаблона, микро-CTA и счётчики показов.
**Ответ на вопрос задания по MX однозначен: движок отдаёт подсказку из библиотеки шаблонов,
а не сумму и не ранжированный список.** Остальные поля — про то, показали ли её и кликнули ли.

### 14.2. MX — эндпоинты Goals: долг и накопление в одном перечне, приоритет задаётся вручную

URL (открыт, HTTP 200, 444 КБ): https://docs.mx.com/api-reference/platform-api/reference/goals

Дословно:

> "Use these endpoints to create and manage goals for a user. You can also **reposition goals to
> adjust their priority levels**."

> "Every goal has a **track type** and a **meta type**. The track type is the overall classification
> of the goal (**debt, savings, retirement, or emergency fund**) while the meta type is the specific
> classification (like college, house, vacation, and so on)."

Полный перечень track type дословно:

> "DEBT_TRACK · SAVINGS_TRACK · RETIREMENT_TRACK · EMERGENCY_FUND_TRACK"

Поля цели (дословно):

> `amount` Decimal — "The amount of the goal."
> `current_amount` Decimal — "The current amount of the goal."
> `goal_type_name` String — "The type of goal. Can be **SAVE_AMOUNT or PAYOFF**."
> `position` Integer — "**The priority of the goal in relation to multiple goals.**"
> `projected_to_complete_at` String — "Date and time the goal is **projected** to be completed..."
> `targeted_to_complete_at` String — "...**Intended for users to set their own goal completion dates.**"

🔴 **Разбор — это и есть та граница, которую ищет задание.** У MX в одной модели сосуществуют
погашение долга (`PAYOFF`, `DEBT_TRACK`) и накопление (`SAVE_AMOUNT`, `EMERGENCY_FUND_TRACK`) —
то есть **предмет размена присутствует**. Но:
- поля **процентной ставки в модели цели нет вовсе**;
- приоритет — целое число `position`, которое **выставляется вручную** через "Reposition goals",
  а не вычисляется;
- прогноз есть (`projected_to_complete_at`), но это одна дата, а не квантили и не сравнение
  сценариев;
- эндпоинта, принимающего свободную сумму и возвращающего её разбиение по целям, в перечне нет.

**То есть MX даёт банку контейнеры для целей и порядок, заданный человеком, но не считает,
куда деньги выгоднее направить.** Это ровно тот зазор, в который целится FINPILOT.

### 14.3. Meniga и Personetics — документация закрыта

- `docs.meniga.com` → **HTTP 401** (редирект на `/latest`, требуется авторизация партнёра).
- `developers.personetics.com` → **HTTP 000** (домен не отвечает).
- `docs.moneythor.com`, `developer.moneythor.com` → **HTTP 000**.

По этим трём вендорам ответ на вопрос «чем оперирует движок» **из первичной техдокументации
получить не удалось**. Косвенно: у всех троих 0 патентов (§8), у Moneythor публичная страница
движка описывает событийную обработку и категоризацию (§11).

---

## 15. 🇷🇺 Российский контур — ЗАКРЫТИЕ: кто продаёт банкам РФ PFM-движки

Третий заход (прогон 3). **WebSearch на старте этого прогона снова ЖИВ** — квота
восстановилась после обрыва предыдущего агента. Это позволило найти вендоров, чьи адреса
не угадываются.

### 15.1. StandFore PFM (Qulix Systems) — B2B-вендор, продающий PFM банкам

Прямой домен `qulix.ru` — **HTTP 000** (не отвечает, страница снята). Взято через архив.
URL (открыт, HTTP 200, 30,7 КБ):
https://web.archive.org/web/2023/http://www.qulix.ru/solutions/banking/personal-finance-management

Дословно:

> «StandFore PFM – это современная система по управлению личными финансами и финансовому
> планированию. Решение может быть тесно интегрировано в каналы дистанционного обслуживания
> банка, предоставляя, таким образом, широкие возможности по **целевому взаимодействию
> с клиентами**.»

Полный перечень функций дословно:

> «Основные функции системы: Анализ персональных расходов · Цели и планирование накоплений (PFP)
> · **Финансовый советник - сценарии достижения целей** · Управление личным бюджетом ·
> Горизонт возможностей»

Компания — Qulix Systems (Москва / Минск / Ливерпуль), копирайт на архивной странице
«© 2005-2020 Qulix Systems».

🟡 «Финансовый советник — сценарии достижения целей» — единственная формулировка у российского
вендора, приближающаяся к сценарному расчёту. Раскрытия механики нет: подстраниц с описанием
советника в архиве **не существует** — проверено по CDX-индексу Wayback
(`http://web.archive.org/cdx/search/cdx?url=qulix.ru/solutions/banking*`), который вернул
ровно шесть URL и ни одного вложенного в `personal-finance-management`:

> `http://www.qulix.ru/solutions/banking` · `.../integration-gateway` · `.../online-loan-services`
> · `.../personal-finance-management` · `.../standfore-fs` · `.../virtual-office`

Кредитный контур у вендора вынесен в **отдельный** продукт `online-loan-services` — то есть
в самой архитектуре продуктовой линейки долг и PFM разведены по разным системам. Это косвенно,
но согласуется с общим выводом: размен «гасить или копить» в российском PFM не живёт.

### 15.2. 🔴 Отраслевой указатель CNews по тегу PFM — карта рынка РФ целиком

URL (открыт, HTTP 200, 410 КБ):
https://www.cnews.ru/book/PFM_-_Personal_Finance_Management_-_Системы_управления_личными_финансами

Это индексная книга CNews: все публикации издания, размеченные тегом PFM, плюс частотный
список организаций. Ценность — в том, что это **внешняя, не вендорская разметка рынка**.

Объём тега дословно: **«Публикаций - 37, упоминаний - 47»** — за период с 2013 по 2025 год.

**Вендоры ПО (не банки) в списке по числу упоминаний, дословно из таблицы:**

> «BSS - Banks Soft Systems - Банк Софт Системс - БСС — 11» · «1С — 5» ·
> «R-Style - Эр-Стайл ГК — 4» · «R-Style Softlab - Эр-Стайл Софтлаб — 4» ·
> «ЦФТ - Центр Финансовых Технологий — 3» · «Cashoff LAB - Cashoff Laboratory - Кэшофф Лаб — 3» ·
> «Cinimex - Синимекс — 2» · «Инверсия - Инверсия НПФ — 2» · «Бифит - Bifit — 2» ·
> «CoinKeeper - Dizrapp — 2» · «ПрограмБанк — 1» · «Temenos AG — 1»

🔴 **Это и есть ответ на вопрос задания «кто вообще продаёт банкам РФ PFM-движки».**
Список короткий и он состоит из **вендоров ДБО** (систем дистанционного банковского
обслуживания), а не из вендоров аналитических движков. BSS, R-Style Softlab, ЦФТ, Бифит,
Инверсия, ПрограмБанк — это поставщики интернет-банка и АБС. PFM у них — **модуль внутри
системы ДБО**, что прямо видно по заголовкам новостей тега, дословно:

> «20.05.2015 — В системе "ДБО BS-Client. Частный Клиент" 2.7 **появился сервис управления
> личными финансами**»
> «03.06.2015 — R-Style Softlab **расширила функциональность системы ДБО InterBank v.5.2**»
> «27.02.2015 — BSS расширяет географию внедрений "ДБО BS-Client. Частный Клиент"»
> «14.11.2016 — BSS представила новый функционал и перспективы развития систем ДБО для юрлиц»

Единственный чистый PFM-вендор в списке — **Cashoff**, дословно из заголовков:

> «05.10.2015 — Сервис управления личными финансами от Cashoff **запущен ещё в двух российских
> банках**»
> «24.06.2016 — Клиентам ВБРР станет доступен **сервис Cashoff** для iOS и Android»

**Хронология тега целиком (дословно, значимые пункты):**

> «29.12.2025 — 3,5 млн россиян поставили цели в "Сбербанк Онлайн" в 2025 году»
> «04.07.2025 — ИИ в приложении Сбербанка выявил главные "финансовые дыры" россиян — и предложил,
> как их закрыть»
> «08.07.2024 — Бесплатными сервисами по управлению личными финансами в "Сбербанк Онлайн"
> ежедневно пользуются 26 млн человек»
> «21.12.2020 — МТС трансформирует мобильное приложение МТС Банка в смартбанк»
> «16.03.2021 — Москвичи откладывают в "онлайн-конверты" "Сбера" в среднем 13,4 тыс. рублей»
> «25.06.2021 — "Сбер" изучил, на что тратит и копит молодежь»
> «11.10.2013 — Русскоязычные сервисы управления личными финансами протестировали
> на эффективность»

🔴 **Наблюдение, важное для новизны:** за 12 лет тега (2013→2025) в 37 публикациях
крупнейшего ИТ-издания страны **ни один заголовок не касается расчёта погашения долга,
процентных ставок или выбора между погашением и накоплением.** Предметный ряд тега:
категоризация расходов, цели, конверты/копилки, инсайты, ДБО. Это независимое (не наше)
подтверждение вывода §12.2, полученное на другом корпусе и с другой стороны — не по
описаниям продуктов, а по тому, о чём вообще пишет отраслевая пресса.

### 15.3. 🔴 Сбербанк — самый крупный PFM в РФ, описан изнутри (первичный источник, открыт)

URL (открыт, HTTP 200): https://www.cnews.ru/news/line/2025-07-04_ii_v_prilozhenii_sberbanka
Дата: **04.07.2025**. Источник материала — сам банк («Об этом CNews сообщили представители
Сбербанка»), заявлено на Финансовом конгрессе Банка России.

Масштаб дословно:

> «Сегодня свыше **10 млн клиентов** Сбербанка регулярно пользуются PFM со встроенным
> искусственным интеллектом. **15% из них ежемесячно выполняют хотя бы одну персональную
> рекомендацию**: переходят на более выгодный накопительный продукт, пересматривают структуру
> расходов, оформляют налоговые вычеты.»

Полный перечень сервисов дословно:

> «С виртуальным ассистентом «Салют» можно обсудить свое финансовое поведение, расходы, получить
> неочевидные инсайты о привычках и советы по оптимизации бюджета и максимизации выгоды. ...
> пользователи могут перейти к детальной качественной аналитике, в такие сервисы как —
> **«Портфельная аналитика», «Финансовое здоровье», «Анализ финансов», «Календари платежей
> и выплат»** ... Помимо этого, PFM взаимодействует с людьми через **контекстные персональные
> рекомендации по накоплениям, инвестициям и экономии**, которые появляются в приложении
> в зависимости от жизненной ситуации пользователя.»

Что именно движок диагностирует, дословно:

> «Среди самых частых — платные подписки, которыми никто не пользуется, импульсивные траты
> и отсутствие накоплений, даже при стабильном доходе.»

> «в среднем клиенты теряют около тысячи руб. в месяц на забытых подписках»

> «Более **40% клиентов с регулярными доходами не создают финансовых целей** в приложении
> и не используют накопительные счета. У этой группы характерны хаотичные переводы между счетами
> и отсутствие стратегии накоплений — в результате даже при стабильном доходе не формируется
> подушка безопасности.»

Руслан Вестеровский, старший вице-президент, руководитель блока «Управление благосостоянием»
Сбербанка, дословно о природе выдачи движка:

> «Он **предлагает подсказки**, основанные на целях и привычках самого пользователя. ... Для нас
> важно не просто предлагать продукт, а помогать клиенту осознанно подойти к своим решениям».

🔴 **Три вывода, все по дословному тексту:**
1. Триада рекомендаций названа явно и исчерпывающе: **«накопления, инвестиции, экономия»**.
   Погашения долга в триаде нет. Кредит в материале не упомянут ни разу — ни как объект
   рекомендации, ни как параметр.
2. Единица выдачи — **«подсказка»** (слова самого руководителя направления), то же самое, что
   поле `description` у MX (§14.1). Не сумма, не распределение, не ранжированный список.
3. Метрика успеха — **«переходят на более выгодный накопительный продукт»**, то есть кросс-сейл
   продукта банка. Третье подряд подтверждение целевой функции российского PFM (после РСХБ §6.1
   и EasyFinance §12.3): движок оптимизирует не выгоду клиента, а конверсию.

Отдельно отмечу цифру, полезную как рыночный контекст: **15% выполняют хотя бы одну
рекомендацию в месяц** при 10 млн пользователей — это верхняя планка отклика для лидера рынка
при рекомендациях-подсказках.

---

## 16. 🔴 Независимые описания (задание §7): вакансии вендоров — какие методы реально применяются

Логика приёма: в требованиях вакансии видно, какие компетенции вендор реально покупает.
Если движок считает оптимизацию, в R&D нужен человек с оптимизацией/исследованием операций;
если движок раскладывает шаблоны по триггерам — нужен бэкендер и дата-инженер.

### 16.1. Personetics — полный состав открытых позиций (страница открыта)

URL (открыт, HTTP 200): https://personetics.com/careers/

Масштаб компании со страницы, дословно:

> "Over **150 million users** rely on our financial wellness tech every month."

**Полный список всех открытых вакансий на 09.09.2026 (дословно, департамент — должность —
локация):**

> Customer Success — "AI Customer Success Partner (North America)" — New York / United State ·
> G&A — "Business Applications Manager" — Tel Aviv · G&A — "Head of AI" — Tel Aviv ·
> **R&D — "Data Architect"** — Tel Aviv · **R&D — "Data Engineer"** — Tel Aviv ·
> **R&D — "DevOps Engineer"** — Tel Aviv · **R&D — "Senior Backend Engineer"** — Tel Aviv ·
> **R&D — "Software Architect"** — Tel Aviv · **R&D — "Squad Lead"** — Tel Aviv ·
> Product — "Product Manager - Engage" — Tel Aviv ·
> Sales — "Senior Account Executive, ASEAN & North Asia" — Singapore / Hong Kong

🔴 **В R&D лидера рынка — шесть позиций, и среди них НЕТ ни Data Scientist, ни Research
Scientist, ни ML Engineer, ни кого-либо с количественным моделированием.** Весь R&D — data
engineering, backend, DevOps, архитектура. Это независимое подтверждение патентного результата
(§8.1: у Personetics ноль патентов на финансовый движок) на совершенно другом канале.

### 16.2. Personetics «Head of AI» — должность про ВНУТРЕННЮЮ автоматизацию, не про продукт

URL (открыт, HTTP 200): https://personetics.com/us/careers/co/tel-aviv-israel/E5.075/head-of-ai/all

Дословно о предмете должности:

> "We are seeking a visionary who reports to the CEO, to serve as the focal point of our
> **internal AI strategy** and lay the groundwork for an AI-enabled future across our organization."

> "Authoring, shaping, and continuously updating the company's **AI Transformation Strategy for
> internal operations, engineering enablement, knowledge management, and workforce productivity**"

> "**Process Optimization & Internal Efficiency:** Mapping existing workflows across various
> departments (Marketing, Sales, HR, Delivery, R&D, Product, etc.) to identify bottlenecks."

Требования, дословно:

> "modern AI paradigms (**LLMs, RAG, API integrations**)"
> "Significant experience in technological leadership, Internal Product Management, Platform
> Engineering, or digital transformation."

🔴 **У компании, продающей банкам «AI-powered financial guidance», единственная позиция со словом
AI в названии — про автоматизацию собственных отделов маркетинга и HR.** Слова `optimization`,
`operations research`, `recommender`, `bandit`, `reinforcement learning` в требованиях
отсутствуют; единственное вхождение «optimization» — «Process Optimization & Internal
Efficiency» и «optimize compute costs».

### 16.3. Personetics «Senior Backend Engineer» — стек продукта без единого следа математики

URL (открыт, HTTP 200):
https://personetics.com/us/careers/co/tel-aviv-israel/54.96A/senior-backend-engineer/all

Требования целиком, дословно:

> "5+ years of hands-on experience in backend and platform engineering roles"
> "5+ years of experience designing and building large-scale backend systems using **Java**"
> "2+ years of experience working with **Python** (Advantage)"
> "3+ years of hands-on experience with **Kubernetes** and modern cloud-native architectures"
> "Solid experience working with **relational databases and SQL**"
> "Practical experience with AI development tools such as **Cursor** or similar tools"

Ни статистики, ни оптимизации, ни ML в требованиях к ядру платформы. «AI» в требованиях —
это Cursor, то есть инструмент написания кода.

### 16.4. Personetics «Data Engineer» — аналитика для BI, а не для движка

URL (открыт, HTTP 200):
https://personetics.com/us/careers/co/tel-aviv-israel/DC.D64/data-engineer/all

Предмет должности дословно:

> "to help design, build, and scale our **BI platform** ... to support internal dashboards and
> future-facing operational analytics."

> "Integrate modern tools and frameworks such as **Airflow, Databricks, Power BI**, and streaming
> platforms."

🟡 В «Nice to have» есть единственная строка, указывающая на связь аналитики с продуктом,
дословно:

> "Background in building operational analytics pipelines, in which **analytical data feeds
> real-time product business logic**."

То есть аналитика **питает бизнес-логику**, а не заменяет её. Формулировка «business logic»
(а не «model», не «optimizer») — ровно то, что видно в схеме MX (§14.1): шаблоны и правила,
подпитанные данными.

**Итог по вакансиям:** три открытые R&D-вакансии крупнейшего вендора класса, прочитанные
целиком, не содержат ни одного требования, которое понадобилось бы для расчёта размена
«долг vs накопление» со ставками. Покупаются Java, Kubernetes, Airflow, SQL. Метод,
который реально применяется, читается из вакансий однозначно: **правила и шаблоны поверх
потока событий.**

---

## 17. 🔴 Независимые описания (задание §7): как вендор САМ описывает изготовление рекомендации

Наиболее ценный класс источников: не маркетинговое «AI-powered», а страницы про **инструмент
создания инсайтов**. Там вендор вынужден сказать, из чего инсайт собран.

### 17.1. Personetics Engagement Builder — инсайт собирается человеком в конструкторе из шаблона

URL (открыт, HTTP 200): https://personetics.com/products/engagement-builder/

Дословно:

> "Create custom insights in a **low-code, management tool** to quickly develop and deploy new
> content across all bank channels."

> "Bring innovation in house – **design custom insights without custom development**."

> "The Engagement Builder **Wizard is a guide to creating new insights using a library of
> templates** or creating one from scratch"

> "Building — **Define logic, behavior and user experience** on new and out of the box insights"

> "Managing — Control experience with **groups, priorities and dependencies**"

> "The Engagement Builder low-code environment combines the accessibility of point and click
> editing with **editing queries and related code** to accommodate a full stack team"

> "Choose from a variety of insight types including **trivia, questionnaires and articles**"

🔴 **Это исчерпывающий ответ на вопрос задания «чем оперирует движок».** У лидера рынка
рекомендация — это **единица КОНТЕНТА**, которую сотрудник банка собирает мышкой из библиотеки
шаблонов, задавая условия выборки («editing queries») и приоритет показа. Слово, которым сам
вендор называет продукт движка, — **«content»**. Типы инсайта включают викторину и статью.
Ни оптимизации, ни расчёта суммы, ни ранжирования вариантов распределения здесь нет и быть
не может: приоритет — это порядок показа карточек, задаваемый вручную («groups, priorities and
dependencies»), ровно как `position` у MX (§14.2).

Отдельно отмечу строку про безопасность, дословно: **"No access to customer data"** — то есть
конструктор работает с условиями и текстами, а не с данными клиента.

### 17.2. Meniga Smart Money Rules — накопительная автоматика, долга нет вовсе

URL (открыт, HTTP 200): https://www.meniga.com/resources/smart-money-rules/ , дата «23.10.2024»

Дословно:

> "Meniga Smart Money Rules helps your banking customers save money. **Automated rules** seamlessly
> set money aside and enable customers to leverage their savings in many ways meaningful to them."

> "Banks employ this **flexible automation engine** to drive loyalty and engagement"

> "For Banks — Help customers accumulate their savings and to make a habit of it. **Cross-sell
> products** and drive engagement by nudging them to leverage their savings."

> "Standalone product implementable **on top of any PFM solution**"

🔴 Название продукта содержит слово «Rules», и вендор называет его «automation engine» —
это правило-триггер («если пришла зарплата — отложи N»), а не расчёт. Долг на странице
**не упомянут ни разу**. Целевая функция снова названа прямо: cross-sell.

### 17.3. Meniga Cashflow Assistant — прогноз баланса есть, вероятностного описания нет

URL (открыт, HTTP 200): https://www.meniga.com/resources/cashflow-assistant/ , дата «23.10.2024»

Дословно:

> "Meniga's AI-powered Cashflow Assistant helps banking customers understand where they are
> financially and provides **future cashflow predictions**."

> "For Customers — Relieve stress of liquidity problems with a **projected future balance
> of accounts** · Reduce fees associated with overdrafts · Efficiently balance monthly cashflow"

> "For Banks — ... **Recommend the right products at the right time** based on your customers'
> financial needs such as **investment products or credit lines**"

🟡 **Это единственный найденный у вендоров прогноз будущего баланса — то есть прямой сосед
прогнозного блока FINPILOT (SES + Монте-Карло).** Но:
- выдача описана в единственном числе — «a projected future balance», одна траектория,
  а не интервал и не квантили; слов `probability`, `confidence`, `scenario`, `Monte Carlo`
  на странице нет;
- назначение прогноза — предупредить об овердрафте, а не оценить последствия распределения;
- 🔴 применение прогноза со стороны банка названо дословно: рекомендовать **«credit lines»**.
  То есть прогноз дефицита ликвидности у вендора конвертируется в предложение кредита.
  У FINPILOT тот же прогноз конвертируется в план, снижающий долговую нагрузку. Это не разница
  в математике — это **противоположная целевая функция**, и она зафиксирована дословной цитатой
  вендора.

---

## 18. 🇷🇺 CASHOFF — единственный чистый PFM-вендор РФ, разобран

По указателю CNews (§15.2) Cashoff — единственная компания в теге PFM, для которой PFM является
собственным продуктом, а не модулем ДБО. Разобран отдельно.

### 18.1. Витрина продуктов (страница открыта)

URL (открыт, HTTP 200, 263 КБ): https://cashoff.ru/

Полная продуктовая линейка дословно, с разбивкой по покупателю:

> «#банкам — #01 **Импорт данных** "Мы знаем все о ваших клиентах" · #02 **Персональный
> банкинг** "Найдём выгоду для каждого" · #03 **Технологии лояльности** "Кешбэк за товары
> в чеках"»
> «#брендам — #04 **Реклама в каналах банка** · #05 **Аналитика покупок** "Портрет покупателя"
> · #06 **Банковские карты лояльности** "Доступ к потребителям"»
> «#казначеям — #07 Импорт данных корпораций из банков»

🔴 Из семи продуктов **три продаются брендам, а не банку и не пользователю**: реклама в каналах
банка, аналитика покупок, карты лояльности. Это тот же вывод, что по EasyFinance (§12.3),
но в более сильной форме: у российского PFM-вендора **покупатель аналитики — рекламодатель**.

Отзыв клиента, дословно (Новикомбанк, Евгений Гладилин, руководитель направления Департамента
розничного бизнеса):

> «Используемые коллегами из CASHOFF технологии – консолидация и обогащение данных вплоть
> до электронных чеков, а также искусственный интеллект сближают банк с каждым клиентом.
> **«Умные советы» – создают уникальный клиентский опыт**, а PFM сервис обеспечивает комфорт
> каждому из них».

Отзыв SBI банка (Юлия Фомина, директор по маркетингу), дословно — единственное место на сайте,
где описан предмет совета:

> «Мы предлагаем клиентам сервис, который **«подсвечивает» закономерности в их тратах** и помогает
> выявить потребности. ... Мы **подсказываем ему, как правильно сэкономить на комиссиях и как
> больше накопить**, подключив своих близких к семейному счету.»

Предмет советов: комиссии и накопления. Долг — нет.

### 18.2. Как вендор сам описывает механику (страница открыта)

URL (открыт, HTTP 200): https://ru.cashoff.global/cashoff-perezapustil-personalnyj-czifrovoj-banking/
Дата: **18 февраля 2022**. Теги статьи дословно: «pfm · Аналитика данных · семейный банк ·
**умные советы** · **Финансовый советник**».

Дословно:

> «За счёт технологий **интеллектуального анализа не только транзакций, но и чеков**, сервис
> персонального цифрового банкинга позволяет банкам точно профилировать пользователей
> и предоставлять персональные рекомендации и индивидуальные советы.»

> «Новые инструменты, или как мы их называем **«умные подсказки» в режиме push-уведомлений
> и email-рассылки** в подходящий момент дают индивидуальные рекомендации для каждого клиента
> благодаря анализу транзакций и чеков.»

> «С помощью персонализации и геймификации наши обновленные сервисы планирования финансов (PFM),
> историй (Stories) и уведомлений (Push/Email) **увеличивают пожизненную ценность клиента, влияя
> на ключевые метрики Unit-экономики (время жизни и выручка с клиента)**»

> «Через истории банк напрямую коммуницирует с клиентом, ненавязчиво **показывает и продаёт
> персонализированные предложения**»

> «Такой подход позволяет банкам качественно и количественно увеличивать финансовые показатели
> такие как **LTV, ARPU и Lifetime**.»

🔴 **Российский вендор говорит то же самое, что западные, только без эвфемизмов.** Единица
выдачи — «умная подсказка» в пуше (то же, что `description` у MX и «content» у Personetics).
Метрика успеха названа прямым текстом: LTV, ARPU, Lifetime. Целевая функция движка —
выручка банка с клиента.

Показательно и самоописание проблемы, которую вендор решает, дословно:

> «В погоне за трендами в приложениях появляются **кладбища предложений банка и партнёров.
> Пользователи теряются и не понимают свою личную выгоду.** Процесс доведения информации
> до пользователя больше становится похож на **информационный шум или спам**.»

То есть вендор сам признаёт, что рынок производит поток нерелевантных предложений, и предлагает
как лекарство — **лучший таргетинг тех же предложений**, а не расчёт выгоды пользователя.

---

## 🔴 СОСТОЯНИЕ КАНАЛОВ — дополнение прогона 3 (финализация)

| Канал | Код / результат | Комментарий |
|---|---|---|
| **WebSearch** | **ЖИВ** | квота восстановилась после обрыва прогона 2; израсходовано 6 запросов |
| `lite.duckduckgo.com` | HTTP 202, 14 240 байт, **0 результатов** | троттлинг с прошлого прогона не снялся; заменён на WebSearch |
| `www.qulix.ru` | **HTTP 000** | домен снят; обойдено через `web.archive.org` |
| `web.archive.org` + CDX API | HTTP 200 | работает, использован дважды (страница + индекс URL) |
| `www.cnews.ru` | HTTP 200 (410 КБ и 190 КБ) | работает без ограничений |
| `personetics.com` | HTTP 200 | careers и продуктовые страницы открываются целиком |
| `personetics.com/us/careers/co/tel-aviv/21.21B/data-scientist/all/` | HTTP 200, но **вакансия снята** | дословно: "The position may have been closed or the link is incorrect" |
| `builtin.com/job/data-scientist/4256389` | **HTTP 404** | агрегатор вакансий, объявление истекло |
| `www.meniga.com/resources/*` | HTTP 200 | product profiles открываются; `/products/cashflow-assistant/` → **404**, живой адрес `/resources/cashflow-assistant/` |
| `cashoff.ru` | HTTP 200 (263 КБ) | SPA, внутренние ссылки в HTML отсутствуют; подстраницы вида `/bankam/...` → **404** |
| `ru.cashoff.global` | HTTP 200 | блог вендора, открывается |

**Незакрытые каналы (перечислены честно, работа не выполнена):**
- `abanking.ru` и презентация `about.abanking.ru/.../Abanking - Welcome презентация.pdf` — не открывались.
- Карточка вакансии Сбербанка «Java (PFM)» на `careerist.ru` — не открылась (§12.4), статус
  «утверждение выдачи» не повышен.
- Продуктовые страницы PFM у BSS, R-Style Softlab, ЦФТ, Бифит, Инверсии, ПрограмБанка — найдены
  по указателю CNews как факт присутствия на рынке, но сами не открывались.
- `docs.meniga.com` (401), `developers.personetics.com` (000), `docs.moneythor.com` (000) —
  остались закрыты, как и в прогоне 2.

---

## 19. 🔴 ЧТО ИЗМЕНИЛОСЬ ПРОТИВ ВЕРСИИ ОТ 08.09.2026

### 19.1. ОПРОВЕРГНУТО (три вывода версии 08.09 неверны)

| Вывод 08.09 | Что установлено | Где |
|---|---|---|
| «Ни один источник класса не считает размен долг/накопления с учётом процентных ставок» | **Неверно.** Считают двое: Capital One (порог 7% APR, Lump = Liquid Assets − 3×CME) и AIG/Corebridge (ставка по кредиту против ожидаемой доходности накоплений). Оба патента ВЫДАНЫ и АКТИВНЫ | §1, §2, §7.3 |
| «Avalanche/snowball не встречаются ни в одном первичном источнике класса» | **Неверно.** Названы поимённо в описании семейства Capital One: "Avalanche/Snowball/Minimum" | §1, §7.3 |
| «Strands мёртв — домен не отвечает» | **Неверно.** Компания жива, поглощена CRIF в 2020; версия 08.09 стучалась в устаревший домен `getstrands.com` вместо `strands.com` | §3 |

### 19.2. ПОДТВЕРЖДЕНО, но теперь ИЗМЕРЕНИЕМ, а не отсутствием доступа

Это качественное повышение статуса выводов: «не нашлось» заменено на «ноль по запросу
к правообладателю» / «ноль по полнотекстовому поиску по мировому массиву».

- **Перебора вариантов распределения с ранжированием не раскрывает НИКТО в мире.** Три
  независимых измерения: `"plurality of candidate allocations" "interest rate"` → **0**;
  `"simple additive weighting" finance debt` → **0**; в семействе Capital One `rank`
  относится к пользователю, не к вариантам (§7.4, §9).
- **Ядро PFM-рынка патентно пусто:** Moneythor 0, Tink 0, Envestnet 0, Meniga 0 (фактически),
  Personetics 1 и тот про распознавание намерения в диалоге (§8).
- **Монте-Карло у вендоров нет вообще**; единственный документ класса с Монте-Карло (Intuit)
  применяет его к прогнозу отдельного платежа, заброшен, и `interest rate` в нём 0 вхождений (§9.2).
- **Российский PFM = категоризация + цели + календарь + подсказки, без долгового контура** —
  подтверждено теперь на пяти независимых корпусах: РСХБ 2026 (§6.1), обзоры 2015 и 2021 (§12.2),
  EasyFinance (§12.3), указатель CNews за 2013–2025 (§15.2), Сбербанк 2025 (§15.3).

### 19.3. НАЙДЕНО НОВОГО (чего в версии 08.09 не было вовсе)

1. **Семейство Capital One из трёх патентов** с полными текстами формулы изобретения (§1, §7).
2. **AIG/Corebridge US11138577B2** — второй источник размена по ставке (§2).
3. **Разрыв «патент ≠ продукт» у Capital One зафиксирован фактически** (§10): в публично
   описанном продукте функции нет, логика существует как статья в ньюсруме от 03.09.2026.
4. **Wells Fargo US20260087556A1** — самый свежий претендент, ранжирование там применено
   к выбору места жительства (§13).
5. **Прямой ответ на вопрос «чем оперирует движок»** из схемы полей MX: текст из шаблона,
   ноль числовых полей результата (§14.1); и из конструктора Personetics: «content»,
   собираемый мышкой (§17.1).
6. **Российский контур целиком:** кто продаёт (вендоры ДБО + Cashoff + StandFore/Qulix +
   EasyFinance), что обещают, какова целевая функция (§6, §12, §15, §18).
7. **Вакансии Personetics прочитаны целиком** — в R&D лидера рынка нет ни одной количественной
   позиции (§16).
8. **Meniga Cashflow Assistant** — единственный найденный прогноз баланса у вендора, и он
   конвертируется банком в предложение кредитной линии (§17.3).

### 19.4. ОСТАЛОСЬ НЕДОСТУПНЫМ

- Партнёрская документация Meniga (401), Personetics (000), Moneythor (000) — механика движков
  этих трёх вендоров из первичной техдокументации так и не получена. Косвенные каналы
  (патенты, вакансии, конструктор, продуктовые страницы) сходятся на одном ответе, но прямого
  подтверждения из API-схемы нет только по MX и Yodlee (там оно есть).
- Продуктовые страницы PFM у BSS / R-Style Softlab / ЦФТ / Бифит / Инверсии / ПрограмБанка.
- `abanking.ru`; карточка вакансии Сбербанка «Java (PFM)».
- Историческая документация Yodlee «Cashflow Analysis» / «FinCheck» — существование продуктов
  так и не подтверждено и не опровергнуто, в живом API-референсе их нет (§5).

---

## 20. 🔴 ЧТО ЭТО ЗНАЧИТ ДЛЯ НОВИЗНЫ FINPILOT

Раздел писан честно, включая неудобное. Ключевой вопрос задания: **патент Capital One
US11023967B1 выдан и активен, формулировки в нём близки к нашей конструкции, но следов
реализации в продукте не найдено — что это значит практически.**

### 20.1. Новое измерение: география патентной семьи (проверено в этом прогоне)

Открыты страницы всех четырёх ключевых патентов, прочитан блок «Also Published As».

| Патент | «Also Published As» дословно | Юрисдикции семьи |
|---|---|---|
| US11023967B1 (Capital One) | "US20210342939A1 · US12008644B2 · US20230252559A1 · US11669897B2 · US20210142402A1" | **только US** |
| US11669897B2 (Capital One) | тот же перечень | **только US** |
| US12008644B2 (Capital One) | тот же перечень | **только US** |
| US11138577B2 (AIG/Corebridge) | "US20180082269A1" | **только US** |

Проверена и последняя публикация семьи US20230252559A1 (URL открыт,
https://patents.google.com/patent/US20230252559A1/en): статус дословно **"Granted"**,
"Application number US18/137,023", "Other versions US12008644B2". То есть **семья закрыта:
три выданных патента, ни одной висящей заявки-продолжения, ни одного члена семьи за пределами
США** — ни EP, ни WO/PCT, ни RU.

🟢 **Практический вывод по риску, самый важный в этом разделе.** Патент действует только
на территории выдачи. У семейства Capital One и у патента AIG/Corebridge **нет российских
и нет европейских членов семьи, и срок подачи PCT/национальных фаз по приоритетам 2016 и 2019
годов давно истёк** — доподать их уже нельзя. Для рынка РФ, который является целевым для
FINPILOT (запуск осенью 2026), **эти патенты не создают запрета на реализацию.**
Это не юридическое заключение и не заменяет патентный поиск в Роспатенте, но это проверяемый
факт с указанием источника, и проверяется он повторно за две минуты.

🟡 **Оборотная сторона, неудобная.** Ровно этот же факт означает, что при выходе FINPILOT
на рынок США семейство Capital One становится предметом FTO-анализа. Раздел 20.3 объясняет,
почему даже там риск ограничен.

### 20.2. Что из ядра FINPILOT перестало быть новым (неудобное, признаётся прямо)

Три элемента, которые до 08.09 считались частью нашей новизны, ею больше **не являются**:

1. **Учёт процентных ставок при работе с долгом** — раскрыт Capital One (порог 7% APR)
   и AIG/Corebridge. Не наше.
2. **Стратегии avalanche / snowball** — названы поимённо в описании Capital One. Не наши
   и никогда не были (это общеизвестные приёмы личных финансов), но теперь это подтверждено
   документом класса.
3. **Численное правило размена «долг vs резерв»** — раскрыто Capital One в явном виде:
   "Lump Payment ... the value is set to **Liquid Assets−3\*CME**". Направление размена
   раскрыто и AIG/Corebridge (ставка по долгу против ожидаемой доходности резерва).

🔴 **Следствие для формулировок ВКР/заявки/README:** утверждения вида «впервые учитывает
процентные ставки при выборе между погашением и накоплением» **использовать нельзя** —
они опровергаются первичным документом. Это надо поправить везде, где такая формулировка
встречается.

### 20.3. Что остаётся новым — и почему это выдерживает проверку

Граница проходит **не по предмету, а по методу**. Capital One решает ту же задачу
**таблицей на 12 клеток**; FINPILOT — перебором и свёрткой. Дословно из зависимого пункта 6
US11669897B2: "generate a **twelve-cell matrix** based on an estimated high interest debt load
of (1) none, (2) moderate, and (3) high, and an estimated emergency fund level of ...".

| Элемент ядра FINPILOT | Найден ли в мировом массиве | Чем измерено |
|---|---|---|
| Множество альтернатив распределения (66 вариантов, шаг 10%) | **Нет** | `"plurality of candidate allocations" "interest rate"` → 0 документов (§9) |
| SAW-свёртка над альтернативами в личных финансах | **Нет** | `"simple additive weighting" finance debt` → 0 документов (§9) |
| Ранжирование ВАРИАНТОВ (а не пользователя) | **Нет** | в семье Capital One `rank` = ранжирование пользователя по сегменту (§7.4); у Wells Fargo ранжируются места жительства (§13); у Intuit ранжирует сам пользователь вручную (§9.2) |
| Профиль риска как веса критериев | **Нет** | `risk profile` в семье Capital One → 0 вхождений (§7.4); у Wells Fargo веса поведенческие, выученные из истории, и применяются к подбору формулировок (§13) |
| Вероятностный прогноз (SES + Монте-Карло, квантили) применительно к последствиям распределения | **Нет** | `Monte`/`simulat`/`scenario` в семье Capital One → 0 (§7.4); у Intuit Монте-Карло применён к прогнозу отдельного платежа, и `interest rate` там 0 (§9.2); у Meniga прогноз — одна траектория баланса (§17.3) |
| Жёсткие инварианты (Rt≥0, ПДН≤0.40) как ограничения допустимости альтернативы | **Нет** | ни в одном прочитанном документе понятия допустимого множества нет; у всех выход — одно предписанное действие |

🟢 **Формулировка новизны, которая выдерживает проверку по собранному материалу:**
не «учитываем ставки» и не «советуем, гасить или копить», а —
**«постановка задачи распределения свободного денежного потока как задачи многокритериального
выбора на конечном множестве допустимых альтернатив, с ранжированием самих альтернатив
и с оценкой последствий каждой вероятностным прогнозом».** Ни один из ~41 прочитанного
источника этого не делает. Все найденные системы выдают **одно предписанное действие**:
клетку матрицы (Capital One), правило-триггер (Meniga Smart Money Rules), карточку из библиотеки
шаблонов (Personetics Engagement Builder, MX Insights), подсказку в пуше (Сбербанк, CASHOFF).

### 20.4. Что значит разрыв «патент выдан, продукта нет» — три трактовки и их цена

Факт (§10): у Capital One три активных патента и **ни одного инструмента размена в публично
описанном продукте**; логика живёт как редакционная статья от 03.09.2026.

| Трактовка | Что означает для нас | Проверяемо? |
|---|---|---|
| **А. Фича свёрнута или не запускалась** — патент оборонительный | Свободная ниша: задача признана крупным банком значимой, но продукта нет. Сильнейший из возможных рыночных сигналов в нашу пользу | Частично: отсутствие подтверждается публичными страницами продукта, наличие — опровергнуть нельзя |
| **Б. Фича есть, но невидима снаружи** (часть клиентов, внутренний скоринг) | Ниша занята тише, чем кажется; наше преимущество — не в идее, а в исполнении и в независимости от банка | Нет. Публичными каналами не проверяется в принципе |
| **В. Считать умеют, но не показывают, потому что совет «гаси долг» противоречит бизнесу банка** | Это структурная причина, а не техническая. Она объясняет, почему у ВСЕХ найденных вендоров целевая функция — кросс-сейл (§6.1 РСХБ, §12.3 EasyFinance, §15.3 Сбербанк, §17.2 Meniga, §17.3 Meniga → «credit lines», §18 CASHOFF → LTV/ARPU) | Косвенно — да, и в этом прогоне подтверждено шестью дословными цитатами |

🔴 **Практический вывод, честный.** Трактовка Б исключить нельзя, и это ограничивает силу
любого утверждения «в мире такого нет» — корректная формулировка звучит как **«не раскрыто
ни в одном публично доступном источнике»**, а не «не существует». Но трактовки А и В обе
работают в пользу FINPILOT, и трактовка В — единственная, у которой есть прямые
подтверждения в собранном материале.

### 20.5. Где остаётся риск

1. **Терминологический, не юридический.** Если в текстах FINPILOT встречается конструкция
   «дерево решений по уровням резерва и долга» или «фиксированный процент от свободного дохода
   по сегменту», она читается как переизложение Capital One. Наша конструкция — перебор
   и свёртка; формулировки должны отражать именно её, иначе мы сами себя ставим внутрь чужой
   формулы изобретения.
2. **Порог 7% APR и правило «резерв 3 месяца»** — раскрыты. Использовать их как «наши
   параметры» нельзя; в модели они и так параметры калибровки, а не изобретение — но это
   должно быть видно из текста.
3. **Рынок США** — при выходе туда семейство Capital One требует FTO-анализа по пункту 1
   каждого из трёх патентов. Ключевой разграничитель на нашей стороне: во всех трёх независимых
   пунктах присутствует **"a decision tree engine"** как обязательный элемент. Система,
   не содержащая дерева решений, под буквальное прочтение пункта не попадает.
4. **Оценка неопределённости ВХОДА (variability / reasonableness score по IQR и σ)** — есть
   у Capital One и **отсутствует у нас**. Это не риск новизны, это пробел качества: они
   умеют говорить, насколько доверяют своим оценкам дохода и расходов, а мы нет. Кандидат
   в бэклог, не в новизну.

### 20.6. Что из этого проверяемо (список для повторной проверки любым другим агентом)

- Отсутствие членов семьи вне США — блок «Also Published As» на страницах трёх патентов.
- `total_num_results` по правообладателям через XHR API Google Patents (§8).
- Нули по трём полнотекстовым запросам мирового массива (§9).
- Отсутствие числовых полей результата в схеме `insight` MX (§14.1) и отсутствие поля ставки
  в модели `goal` MX (§14.2) — открытая документация, без авторизации.
- Состав открытых R&D-вакансий Personetics (§16.1) — меняется со временем, снимок на 09.09.2026.
- Триада рекомендаций Сбербанка «накопления, инвестиции, экономия» без долга (§15.3).

---

## 🔴 ИТОГ ПРОГОНА

Тема №11 очереди и её добор №22 **закрыты**. Живых, реально открытых источников — **41**
(29 из прогонов 1–2 плюс 12 в прогоне 3). Главное изменение картины против версии 08.09:
вывод «размен со ставками не считает никто» опровергнут двумя выданными патентами, но
центральный тезис новизны FINPILOT — **перебор допустимых альтернатив с ранжированием
и вероятностной оценкой последствий** — устоял и теперь подтверждён не отсутствием находок,
а измеренными нулями по мировому патентному массиву.
