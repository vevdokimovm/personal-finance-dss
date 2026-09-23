# Тема 20 — Патенты банков и финтеха + методики financial wellness scoring

**Дата:** 2026-09-09
**Статус полноты:** ЗАВЕРШЕНО частично — блоки А, Б, В заполнены; недобытые участки перечислены
поимённо с кодами ответа в разделе «Что не добыто и почему». Работа шла 09–10.09.2026
(сессия прервана лимитом и продолжена; файл писался по ходу, потерь нет).
**Исполнитель:** research-агент, канал добычи по порядку WebFetch → curl(UA) → r.jina.ai → PDF-приём через Read(pages)
**Оговорка:** всё, что помечено «реконструкция по памяти» — НЕ проверено источником и не годится
для научного текста. Всё остальное сопровождается URL и кодом ответа канала.

---

## БЛОК А. Патентный массив

> **Метод добычи всего блока А.** Поиск вёлся через **недокументированный JSON-эндпоинт
> Google Patents** `https://patents.google.com/xhr/query?url=<urlencoded query>` с браузерным
> User-Agent (все вызовы вернули HTTP 200; обычный `WebFetch` по patents.google.com не
> использовался, т.к. страница рендерится JS, а серверная HTML-версия доступна через `curl`).
> Реквизиты и claims снимались с `https://patents.google.com/patent/<PUB>/en` (`curl` + UA,
> HTTP 200, 380–405 КБ на документ) разбором микроразметки `itemprop=` (`status`,
> `assigneeCurrent`, `inventor`, `priorityDate`, `filingDate`, `publicationDate`,
> секция `itemprop="claims"`, блок «Also Published As»). Правовой статус берётся из
> `<span itemprop="status">` — это поле Google Patents, отражающее статус в реестре.

### А.1. 🔴 US12047359B2 — BrightPlan LLC, «Systems and methods for components of financial wellness»

**САМАЯ ЗНАЧИМАЯ НАХОДКА БЛОКА.** Это выданный и действующий патент **именно на методику
расчёта агрегированного финансового индекса через иерархическую взвешенную свёртку** —
то есть на то, что в теме 20 предполагалось непатентуемым.

| Поле | Значение |
|---|---|
| Публикационный номер | **US12047359B2** |
| Заявитель (current assignee) | **Brightplan LLC** |
| Изобретатели | Marthin De Beer, Larry Robinson, Krutarth Shah, Harpreet Buttar |
| Дата приоритета | **2017-10-27** |
| Дата подачи | 2022-11-18 (продолжение) |
| Дата публикации/выдачи | **2024-07-23** |
| **Правовой статус** | **Active** |
| Число claims | 20 |
| Also Published As | **US11509634B2** ; US20200366654A1 ; US20230078826A1 ; **US20240372840A1** |

🔴 **Все члены семьи — только US.** Ни одного члена семьи вне США в блоке «Also Published As»
не обнаружено (нет EP/WO/RU). Для рынка РФ этот патент **не является запретом**.

**Claim 1 — дословно:**

> 1. A secure messaging system configured by at least one processor to execute instructions
> stored in memory, the system comprising:
> a user-facing application that performs processing based on user interaction with a goal-based
> planning application, the goal-based planning application configured to execute instructions
> including:
> **determining a pillar score for each of a plurality of pillars, the pillar score being a weighted
> percentage of a financial wellness score, each of the plurality of pillars including a component
> data attribute, the component data attribute being a weighted percentage of the pillar score
> for each of the plurality of pillars; and**
> **calculating the financial wellness score using the pillar score for each of the plurality of pillars.**

**Зависимые claims, раскрывающие состав индекса — дословно:**

> 8. […] the plurality of pillars including a **monthly cash flow pillar, a financial freedom pillar,
> a security pillar, a personal organization pillar, and a decay element pillar**.
> 9. […] the monthly cash flow pillar having the component data attribute of **savings as
> a percentage of gross income or a credit score**.
> 10. […] the financial freedom pillar having the component data attribute of a **retirement goal
> status, 401k savings, 403B savings, IRA savings, an investment strategy, or automated savings**.
> 11. […] the security pillar having the component data attribute of an **emergency goal, a funding
> emergency goal, a saving plan on track, adequate insurance coverage, or an estate plan**.
> 12. […] the personal organization pillar having the component data attribute of a financial
> account linked to a net worth dashboard or record keeping.
> 13. […] the **decay element pillar** having the component data attribute of an amount of
> educational content consumed online, an amount of interaction with a financial advisor or
> a **login frequency to view the financial wellness score**.

**Механизм выдачи советов — дословно:**

> 14. […] each pillar of the plurality of pillars and each component data attribute having
> a corresponding **piece of advice** to advance a user within a pillar.
> 15. […] the corresponding piece of advice having an **advice score**.
> 16. […] the **advice score being inversely related to a financial wellness score for a pillar**.
> 17. […] the corresponding piece of advice being **prioritized based upon the advice score**.
> 18. […] the corresponding piece of advice being based on machine learning and predictive
> analytics, the machine learning and the predictive analytics using user cohort behaviors.

**Раскрыт ли перебор альтернатив с ранжированием? — ЧАСТИЧНО, и не тот.**
Ранжирование здесь есть (claim 17), но ранжируются **советы**, а не **альтернативы распределения
денежного потока**. Приоритет совета вычисляется тривиально: обратно пропорционально
баллу того столпа, к которому совет привязан (claim 16). Нет: дискретного множества долей
распределения, нет скалярной свёртки по критериям на каждой альтернативе, нет жёстких
ограничений-инвариантов, нет вероятностного прогноза. **Конструкция FINPILOT не раскрыта.**
Что действительно перекрыто — **сам приём «иерархический индекс = взвешенные столпы,
столп = взвешенные атрибуты»** (claim 1), в границах США.

### А.2. US8412622B2 — Bank of America, «Systems and methods for determining a financial health indicator»

| Поле | Значение |
|---|---|
| Публикационный номер | **US8412622B2** |
| Заявитель | **Bank of America Corp** (current assignee) |
| Изобретатели | Kazi M. Ariff, Carol A. Smith, Shane A. Johnson, Russell W. Tipper, Yicong Li, Sean M. O'Connor, Thomas D. Kelley, Susan S. Thomas, William F. Borowski, William J. Aheron, Judith M. Anderson, Steven K. Hayes |
| Приоритет / подача | **2009-03-30** / 2009-03-30 |
| Публикация (выдача) | **2013-04-02** |
| **Правовой статус** | **Active** |
| Число claims | 36 |
| Also Published As | US20100250430A1 ; **WO2010114732A1** |

🟡 **Есть международная заявка WO2010114732A1** — то есть заявитель PCT-маршрут открывал.
Национальной фазы RU в блоке «Also Published As» **не обнаружено** (в списке только US-публикации
и WO). Проверка национальных фаз WO2010114732A1 отдельным запросом **не проводилась** —
это остаточный риск, зафиксирован в разделе «Что не добыто».

**Claim 1 — дословно:**

> 1. A method for providing a financial health indicator, the method comprising:
> determining, via a computing device processor, a **target budget allocation** for a user based
> on a current budget allocation of the user and responses to a **budget profile questionnaire**;
> **constantly monitoring**, via a computing device, a **credit report score** associated with a user;
> constantly monitoring, via a computing device, a **budget savings amount** associated with the
> user, wherein the budget savings amount reflects expenditures, as they occur, made by the user
> compared to the target budget allocation;
> determining, via a computing device processor, a **financial health indicator** for the user
> **based on the credit report score and the budget savings amount**, wherein the financial health
> indicator is configured to **fluctuate in real-time** based on at least one of a change in the credit
> report score and a change in the budget savings amount; and
> communicating, via a computing device, the financial health indicator to the user.

Существенные зависимые:

> 4. […] receiving […] user selections for the target budget allocation based on providing the user
> with **peer budget allocation data**.
> 7. […] defines the financial health indicator as a **financial health score**.
> 8. […] defines the financial health indicator as a **color within a financial health color spectrum**.
> 10.–12. […] определение достижения порога индикатора и **автоматическая выдача награды** —
> «a preferred rate of return on a financial institution account, or a preferred price on a financial
> institution product».

**Раскрыт ли перебор альтернатив? — НЕТ.** Индекс — функция ровно двух входов (кредитный скоринг
бюро + отклонение факта от целевого бюджета). Это **двухфакторный индикатор состояния**,
без оптимизации, без критериев, без ранжирования вариантов. К конструкции FINPILOT не близко.

### А.3. US20140372340A1 — Bank of America, «Financial wellness scoring tool»

| Поле | Значение |
|---|---|
| Публикационный номер | US20140372340A1 |
| Заявитель | Bank of America Corp |
| Изобретатель | **William E. Brown, III** (единственный) |
| Приоритет / подача | 2013-06-14 / 2013-06-14 |
| Публикация | 2014-12-18 |
| **Правовой статус** | 🔴 **Abandoned** |
| Число claims | 20 |
| Also Published As | US20160314533A1 |

**Claim 1 — дословно (существенная часть):**

> identify retirement account information for plan participants in a retirement account at an
> institution, wherein the retirement account information is related to […] savings, investing,
> setting and monitoring goals, and account preservation behaviors of the plan participants;
> determine a **wellness score** for the plan participants […] wherein the wellness score is
> determined from the retirement account information related to a measure of the savings,
> investing, setting and monitoring goals, and account preservation behaviors […];
> determine **wellness metrics** for the plan participants […] in one or more aggregate metrics;
> create a **report** illustrating the wellness scores […]; and provide the report to desired parties.

**Область — узкая: пенсионные планы (401k) и отчётность работодателю**, не персональные финансы
домохозяйства. Перебор альтернатив не раскрыт. Формула балла в claims не раскрыта вовсе — есть
только перечень поведенческих факторов (claims 2–5). **Заявка заброшена, правового препятствия нет.**

### А.4. US20190378207A1 — Intuit Inc., «Financial health tool»

| Поле | Значение |
|---|---|
| Публикационный номер | US20190378207A1 |
| Заявитель | Intuit Inc |
| Изобретатели | Aaron Dibner-Dunlap, Kevin Furbish, Kymm Kause, Swathi Nimmagadda, Nirmala Ranganathan |
| Приоритет / подача | 2018-06-07 / 2018-06-07 |
| Публикация | 2019-12-12 |
| **Правовой статус** | 🔴 **Abandoned** |
| Число claims | 30 |
| Also Published As | не обнаружено (только US-публикация) |

**Claim 1 — дословно:**

> 1. A method of identifying and implementing an account change comprising:
> obtaining, at a processor, data indicating a user's financial health, the data including
> **personality data not directly related to finances**; analyzing, by the processor, the data
> to identify a change applicable to a financial account of the user, the change configured
> to improve the user's financial health; and **automatically causing** […] the change to be
> implemented by a network-accessible financial service.

Документ найден по запросу, содержащему одновременно «Monte Carlo», «debt repayment»
и «emergency fund» — то есть эти термины есть в описании, но **в claims их нет**: заявленная
конструкция — «собрать данные, включая данные о личности → определить изменение счёта →
применить его автоматически». Перебор альтернатив с ранжированием **не заявлен**.
Заявка заброшена.



### А.5. 🔴 РОССИЙСКИЙ МАССИВ — измеренный отрицательный результат

#### А.5.1. Доступность национальных реестров: НЕ ДОБЫТО, коды зафиксированы

| Канал | URL | Результат |
|---|---|---|
| `WebFetch` | `https://www1.fips.ru/iiss/` | **HTTP 403 Forbidden**, тело не получено |
| `curl` + браузерный UA | `https://www1.fips.ru/iiss/` | **HTTP 403, 1 606 байт** |
| `curl` + браузерный UA | `https://www.fips.ru/iiss/` | **HTTP 403, 1 606 байт** |
| `curl` + браузерный UA | `https://searchplatf.rospatent.gov.ru/` | **HTTP 000, 0 байт** (соединение не установлено) |
| `curl` + браузерный UA | `https://searchplatf.rospatent.gov.ru/search?q=…` | **HTTP 000, 0 байт** |
| `r.jina.ai` | `https://www1.fips.ru/iiss/` | HTTP 200 у прокси, но тело — **заглушка DDoS-Guard**, см. ниже |
| `r.jina.ai` | `https://new.fips.ru/registers-web/` | то же, заглушка DDoS-Guard |
| `r.jina.ai` | `https://searchplatf.rospatent.gov.ru/` | **HTTP 422**, `"Domain 'searchplatf.rospatent.gov.ru' could not be resolved"` |

Тело заглушки дословно:

> ## www1.fips.ru is not available
> It looks like the website owner has restricted access from your current network
> To protect their website from malicious activity, the owner or administrator may block access
> from specific countries, networks, or IP addresses.

🔴 **Причина не в инструменте, а в геоблокировке DDoS-Guard**: ФИПС закрыт для сети, из которой
идут запросы. Текстовый прокси не помогает — он честно проксирует ту же 403. Домен
`searchplatf.rospatent.gov.ru` **не резолвится вовсе** ни у нас, ни у прокси, то есть либо
переехал, либо доступен только из РФ-сегмента.

**Следствие: реестр свидетельств о госрегистрации программ для ЭВМ (Сбер, Т-Банк, ЦФТ, BSS,
CASHOFF) в этой сессии НЕ ПРОВЕРЕН вообще.** Google Patents свидетельства на ПО для ЭВМ
не индексирует в принципе — это отдельный реестр Роспатента, не патентный. Участок надо
закрывать с машины в российском сегменте, либо через платный сервис (Онлайн Патент,
PatentDB, Роспатент API по договору).

#### А.5.2. Что удалось: RU-массив через Google Patents

Google Patents RU-сегмент **проиндексирован**, но в основном по названию/реферату, а не по
полному тексту: русскоязычные полнотекстовые фразы дают нули там, где фильтр по СПК даёт выдачу.
Замер: `q=("финансового здоровья")&country=RU` → **0**; `q=("персональных финансов")&country=RU` → **1**
(и тот — Microsoft про платформу данных, RU2371757C2, не по теме).
Поэтому дальше искалось **по классам СПК с широким русским словом-якорем**.

**Класс G06Q 40/02 (банковское дело), country=RU** — запрос `q=(способ)&country=RU&cpc=G06Q40/02`,
**TOTAL = 101**, просмотрено 50 верхних. Состав выдачи: платёжные токены и транзакции (Visa,
Mastercard, Alibaba, НСПК), антифрод («Лаборатория Касперского» — 6 документов), банкоматы
и инкассация, кредитные сделки. **Ни одного документа про распределение свободных средств,
персональный финансовый менеджер или индекс финздоровья.**

**Класс G06Q 40/06 (инвестиции/финансовое планирование), country=RU** — запрос
`q=(способ)&country=RU&cpc=G06Q40/06`, **TOTAL = 42**, просмотрено 42. Состав: биржевые рынки,
инвестиционные инструменты, недвижимость, волатильность, ценные бумаги. Ближайшие по духу
документы (но не по конструкции):
- **RU2213369C2**, «Гайдед Чойс.Ком, Инк.», приоритет 1997-07-25, публикация 2003-09-27 —
  «Система предоставления инвестиционного консультирования и управления средствами…».
  🔴 **Приоритет 1997 → 20-летний срок истёк в 2017, документ заведомо в общественном достоянии.**
- **RU2019118128A**, ООО «ОПТИМАЛЬНОЕ УПРАВЛЕНИЕ», приоритет 2017-06-21, публикация 2021-07-21 —
  «Способ и устройство планирования операций с активами предприятия». Это **заявка** (код `A`),
  и предмет — **активы предприятия**, не домохозяйство.

**Класс G06Q 30/0631 (рекомендации по выбору товара), country=RU** — запрос
`q=(способ)&country=RU&cpc=G06Q30/0631`, **TOTAL = 50**, просмотрено 32. Состав: рекомендательные
системы контента и товаров (Яндекс — 5 документов, JD.com, Xiaomi, Microsoft, Samsung).
**Финансовых рекомендательных систем в этом классе по RU нет.**

#### А.5.3. Портфель ПАО «Сбербанк» в G06Q 40/00 — перечислен полностью

Запрос `q=(Сбербанк)&country=RU&cpc=G06Q40/00`, **TOTAL = 10**, просмотрено 10 из 10:

| Номер | Приоритет | Публикация | Название |
|---|---|---|---|
| RU2680760C1 | 2018-04-04 | 2019-02-26 | Компьютеризированный способ разработки и управления моделями скоринга |
| RU2723448C1 | 2019-05-24 | 2020-06-11 | Способ расчёта кредитного рейтинга клиента |
| RU2677384C1 | 2017-12-14 | 2019-01-16 | Способ автоматического расчёта включённых денежных средств при сбоях |
| RU2723452C2 | 2018-08-16 | 2020-06-11 | Компьютерно-реализуемый способ и система централизованного управления… |
| RU2705772C1 | 2019-04-23 | 2019-11-11 | Способ и система исполнения сделки РЕПО в распределённом реестре |
| RU2699577C1 | 2018-12-20 | 2019-09-06 | Способ и система поиска мошеннических транзакций |
| RU2724798C1 | 2019-09-05 | 2020-06-25 | Способ и система оптимизации инкассаторского обслуживания объектов наличного… |
| RU2679231C1 | 2017-12-22 | 2019-02-06 | Способ и система геомоделирования сети устройств самообслуживания |
| RU2723456C2 | 2018-11-15 | 2020-06-11 | Способ и система поиска устройства самообслуживания |
| RU2767285C1 | 2020-12-08 | 2022-03-17 | Способ и система автоматизированного зачисления денежных средств при… |

🔴 **Ни одного патента Сбербанка на индекс финансового здоровья, персональный финансовый
менеджер или распределение свободного денежного потока в классе G06Q 40/00 не обнаружено.**
Два «скоринговых» патента — **кредитный скоринг для банка** (оценка заёмщика банком),
а не индекс здоровья для клиента. Это принципиально другой объект.

#### А.5.4. АО «Тинькофф Банк» / Т-Банк

Запрос `q=(Тинькофф)&country=RU`, **TOTAL = 12**, просмотрено 12 (из них 5 — дубли RU/EN
одних и тех же документов, 4 — шум по совпадению слова). Реальные документы банка — два:
- **RU205388U1**, АО «Тинькофф Банк», приоритет 2021-02-01, публикация 2021-07-13, **полезная
  модель** — «Корпус банкомата» (ATM CASE).
- **RU2779249C1**, АО «Тинькофф Банк», публикация 2022-09-05 — «Система определения
  принадлежности банковской карты пользователю».

**По теме персональных финансов — ничего.**

Отдельно найден **RU2845216C1**, ООО «Сбер Бизнес Софт», публикация 2025-08-15 —
«Способ и система поиска и выделения семантически уникальных популярных фраз…» (NLP, не по теме).

#### А.5.5. Прямой ответ по российскому массиву

**Действующего российского патента, чьи независимые пункты накрывали бы перебор дискретного
множества альтернатив распределения свободного денежного потока со скалярной свёрткой,
ограничениями и ранжированием, в проверенном объёме НЕ ОБНАРУЖЕНО.**
Объём проверки: 3 класса СПК (G06Q 40/02 — 101 док., G06Q 40/06 — 42 док., G06Q 30/0631 — 50 док.),
портфель Сбербанка в G06Q 40/00 целиком (10 док.), портфель Тинькофф (12 док.), плюс
5 полнотекстовых русскоязычных запросов.
🟡 **Ограничение вывода:** реестр программ для ЭВМ Роспатента не проверялся (недоступен),
а полнотекстовый поиск по RU в Google Patents неполон — поэтому это «не найдено в проверенном
объёме», а не «доказано отсутствие».


### А.6. 🔴 US20250315893A1 — Insphire IO Corp., «Data-driven adaptive financial guidance system with reinforcement learning optimization»

**Самый близкий к постановке задачи FINPILOT документ из всего просмотренного массива.**

| Поле | Значение |
|---|---|
| Публикационный номер | US20250315893A1 |
| Заявитель | Insphire IO Corp |
| Изобретатели | Benjamin Levine, Patrick Hendershott, Laurel Taylor |
| Приоритет | **2024-04-09** |
| Подача | 2025-04-08 |
| Публикация | **2025-10-09** |
| **Правовой статус** | 🟡 **Pending** (заявка на рассмотрении, патент НЕ выдан) |
| Число claims | 15 |
| Also Published As | не обнаружено (только US-публикация; членов семьи вне США нет) |

**Claim 1 — дословно, существенные фрагменты:**

> 1. A computer-implemented method for managing an individual's financial portfolio to **optimize
> net wealth**, the method comprising:
> receiving […] financial data […] includes at least information regarding income, expenses,
> **debt obligations**, savings account balances, investment account details, and historical
> financial transactions;
> analyzing […] wherein the analysis includes: calculating a **current balance, interest rate,
> and minimum payment requirement for each identified debt obligation**; determining an account
> balance and interest rate for each identified savings account; […]
> personalizing […] a financial guidance plan based on financial goals of the user, circumstances,
> and **risk tolerance**, wherein the personalization includes: […] **assessing potential financial
> shocks and evaluating the risk tolerance of the user using a Constant Relative Risk Aversion
> (CRRA) utility function**: considering time preferences and financial objectives […];
> generating […] tailored financial guidance […] includes specific recommendations on **debt
> reduction, savings optimization, and investment strategies**;
> implementing […] a **reinforcement learning algorithm** to continuously improve the financial
> guidance based on real-world feedback […];
> **wherein the method results in a net wealth improvement for the individual by optimizing the
> allocation of resources among debt reduction, savings, and investments** based on the individual's
> personalized financial plan.

Claim 2 добавляет пользовательскую цель **как ограничение**:

> receiving […] a user-defined financial target, wherein the financial target comprises a desired
> savings balance by a specified future date; **incorporating […] the user-defined financial target
> into the financial guidance plan as a constraint to be achieved**; […]

**Сопоставление с конструкцией FINPILOT — что совпало и что нет:**

| Элемент FINPILOT | В US20250315893A1 |
|---|---|
| Распределение потока между долгами / резервом / целями | **ДА**, заявлено дословно («optimizing the allocation of resources among debt reduction, savings, and investments») |
| Учёт ставки по каждому долгу | **ДА** («interest rate […] for each identified debt obligation») |
| Риск-профиль пользователя | **ДА**, но через **CRRA-функцию полезности**, а не через фиксированный набор профилей |
| Цель как жёсткое ограничение | **ДА** (claim 2) |
| **Перебор дискретного множества альтернатив (шаг 10 %)** | **НЕТ** — конструкция не переборная |
| **Скалярная свёртка по взвешенным критериям (SAW)** | **НЕТ** — целевая функция одна: CRRA-полезность / net wealth |
| **Ранжирование альтернатив и показ вклада критериев** | **НЕТ** |
| **Инварианты (Rt ≥ 0, ПДН ≤ 0.40)** | **НЕТ** в claims |
| **Монте-Карло** | **НЕТ** в claims (заявлено «assessing potential financial shocks», механизм не назван) |
| Механизм адаптации | **Reinforcement learning** — у нас его нет вовсе |

🔴 **Вывод.** Это ближайший аналог по ЗАДАЧЕ и одновременно **чужой по МЕТОДУ**: там
RL + CRRA-оптимизация (одна скалярная полезность, непрерывное решение), у нас — MCDA-перебор
дискретной сетки с многокритериальной свёрткой и явными инвариантами. Патент **не выдан**
(pending), российских членов семьи нет.

### А.7. US20120059751A1 — Strands, Inc., «Systems and methods for managing and allocating funds»

| Поле | Значение |
|---|---|
| Номер | US20120059751A1 |
| Заявитель | Strands Inc |
| Изобретатели | Rick Hangartner, Philip Jenkins |
| Приоритет / подача | 2010-09-08 / 2011-09-08 |
| Публикация | 2012-03-08 |
| **Правовой статус** | 🔴 **Abandoned** |
| Also Published As | не обнаружено |

**Claim 1 — дословно:**

> 1. An apparatus, comprising: a memory device configured to: store information identifying at least
> one user account; and store **user preferences corresponding to at least one savings goal**;
> a processing device configured to: **detect a deposit of funds** into the at least one user account;
> **automatically allocate the deposit in response to the user preferences**; and cause a display
> of progress towards meeting the at least one savings goal […]

Claim 3 раскрывает состав preferences: «goal category, goal name, goal amount, end date,
contribution amount, or **goal priority**».

🔴 **Распределение здесь делает ПОЛЬЗОВАТЕЛЬ, задав приоритеты целей; система только исполняет.**
Никакой оптимизации, ранжирования вариантов или критериев. Тот же класс, что KeyBank
US20210125274A1 из темы 19 («выбор режима делает пользователь галочкой»). Заявка заброшена.

### А.8. Прочие просмотренные заявители — отрицательный результат, поимённо

Проверены и **не дали релевантной конструкции** (документы либо про другое, либо конструкция
далека):

- **Wells Fargo** — US20250335982A1 «System and method for financial health robo-advisor»
  (изобретатель Cathy Ann Costa, приоритет 2022-11-10, публикация 2025-10-30, статус **Pending**,
  Also Published As **US12361480B1**). Claim 1 — **геолокационное упреждающее уведомление**:
  нейросеть предсказывает вероятность покупки при входе устройства в предопределённую
  географическую зону и выдаёт «preventative alert when the probability exceeds a threshold value».
  К распределению потока отношения не имеет. Также: US11244406B1 (peer-based comparison),
  US20200380596A1, US20200380610A1, US20220101383A1, US20250139697A1, US20250200481A1 —
  мониторинг, алерты, сравнение с пирами.
- **USAA** — US12141861B1 «Financial autopilot» (Nathan Mahoney, Luis Daniel Silva,
  Gunjan C. Vijayvergia, Jason Paul Hendry; приоритет 2018-09-28, публикация 2024-11-12,
  статус **Active**; Also Published As US11127075B1, US11861694B1, US12524803B1 — **всё US**).
  Claim 1 — **обучение нейросети предсказывать расход по истории транзакций** и «determining
  a plan to account for the at least one specified expense». Слова «avalanche»/«snowball»
  присутствуют в описании (документ найден именно по ним), но **в формуле их нет**;
  переборной оптимизации нет. Также US11455681B1 «Adaptive financial advisor».
- **Capital One** — US20230252559A1 «Guidance engine: an automated system and method for providing
  financial guidance» (Katharine Schlesinger, John Rush, Zheyu Yang, Matthew Davis; приоритет
  2019-11-12, публикация 2023-08-10, статус **Granted**). Это **тот же семейный куст**, что уже
  разобран в теме 19: Also Published As — **US11023967B1, US11669897B2, US12008644B2,
  US20210142402A1, US20210342939A1, все US**. Claim 1 подтверждает механизм дословно:
  «determining results for **each branch of a decision tree** that associates the financial action
  with **combinations of values** of the estimated monthly expenses, the estimated monthly income,
  the estimated emergency fund level, and the estimated high interest debt level».
  🔴 **Это дерево решений по четырём величинам, а не перебор альтернатив с ранжированием.**
  Claim 2 подтверждает порог: «the estimated high interest debt level is associated with a loan
  with an interest rate **above a pre-set threshold**».
- **Responsive Capital Management Inc.** — US12229832B2 «Wealth management systems»
  (Davyde Wachell, Chris Sanford, Logan Grosenick; приоритет 2018-11-26, публикация 2025-02-18,
  статус **Active**). 🟡 **Единственный из найденных с широкой международной семьёй:
  Also Published As CA3121012A1, EP3888026A1, EP3888026A4, WO2020107111A1, US20220028001A1** —
  то есть CA + EP + PCT. **Российского члена семьи в блоке нет.** Claim 1 — ML-система
  «next best action» с событийными правилами, обучением с учителем и «binary univariate
  thresholding function»; ранжирование там есть, но ранжируются **уведомления** по релевантности
  на основе обратной связи, не альтернативы распределения.
- **Bank of America** — дополнительно US20140372341A1 «Wellness segmentation tool»,
  US20160267595A1 «Financial wellness system», US20170193604A1, US20100268629A1 «Concrete budgeting».
- **Truist Bank** — большой куст 2022–2025 (US20250156890A1, US20250259195A1, US12307473B2,
  US20240037406A1, US20240045740A1 и др.), но это **ML-предсказание обновлённого балла оценки
  и инфраструктура**, а также несвязанный куст про криптографию/носимые устройства
  (US20250307932A1 … US20250307934A1).
- **Block/Square** — US11657448B2, US10460395B2 (разделение балансов, GUI отслеживания транзакций),
  US11922447B1 (биометрические вознаграждения). Не по теме.
- **Intuit** — US11270375B1 (агрегация данных для предсказания), CA3162417C «Customized credit
  card debt reduction plans» (приоритет 2020-07-23, выдан в **Канаде** 2025-03-25) — найден по
  «avalanche»+«snowball», содержание формулы не снималось (см. «Что не добыто»).
- **LendingClub** — US20260080466A1 «Dynamic Financial Health Predictor» (приоритет 2019-12-27,
  публикация 2026-03-19), US20210201400A1 «Intelligent servicing».
- **Freedom Financial Network** — US12333599B1 «Financial health scoring for direct client-merchant
  transactions» (приоритет 2021-05-04, публикация 2025-06-17).
- **VeraScore Inc.** — US20230128256A1 «Financial health simulation system» (приоритет 2021-10-22).
- **Fidelity (FMR LLC)** — US20200104935A1 «Systems and methods for wealth and health planning».
- **Financial Finesse, Inc.** — US20110225079A1, US20150206452A1 (персонализированное
  финансовое образование), US20200320894A1 «Interactive coaching interface».
- **Acorns Grow** — US12614232B2, US12026779B2, US11176614B1 (округление трат, «excess funds
  from retail transactions and apportioning»).
- **Toronto-Dominion Bank**, **Citizens Financial Group**, **Envel Inc.**, **Ahora Inc.**,
  **Quarter Inc.**, **Movencorp**, **Parabola LLC**, **Edea LLC**, **Rawllin International**,
  **Benovate**, **loanDepot**, **ConnexMarkets**, **Sou Sou**, **Live Give Save** — просмотрены
  по заголовкам в выдачах, релевантной конструкции не содержат.

🔴 **По заявителям из задания, по которым выдача не дала НИ ОДНОГО релевантного документа:**
JPMorgan Chase, Citigroup, PNC (кроме US20250217892A1 про краудсорсинговые инвестиции),
Discover, American Express, Charles Schwab, Vanguard, Credit Karma, NerdWallet, PayPal, Plaid,
MX Technologies, Meniga, Moneythor, Tink, Nubank, Revolut. 🟡 Важная оговорка: попытка искать
через параметр `&assignee=<имя>` эндпоинта Google Patents **систематически возвращала HTTP 503**
(8 запросов подряд), поэтому по этим компаниям поиск шёл **свободным текстом**, а не по полю
заявителя — это менее надёжный метод, и отсутствие результата по ним слабее, чем по тем,
кого нашли через СПК-фильтры.


---

## БЛОК Б. Методики financial wellness / financial health scoring

### Б.1. Financial Health Network — FinHealth Score® Toolkit (2021)

**Реквизиты.** «The Financial Health Network's FinHealth Score® Toolkit», Financial Health Network,
135 S. LaSalle, Suite 2125, Chicago, IL 60603, © 2021, 11 страниц.
URL: https://finhealthnetwork.org/wp-content/uploads/2021/11/FinHealthScoreToolkit-2021.pdf
**Канал добычи:** `WebFetch` не пробовался (PDF), `curl` с браузерным UA → **HTTP 403, 1635 байт**
(антибот Cloudflare). Текстовый прокси `curl -s "https://r.jina.ai/<URL>"` → **HTTP 200, 14 126 байт**,
полный текст всех 11 страниц. Это второй замеренный случай, когда `r.jina.ai` пробивает антибот
там, где `curl` с UA получает 403 (первый — MDPI, 09.09.2026).

**Структура.** 8 вопросов = 8 индикаторов, сгруппированных в 4 домена по 2 вопроса.

> Spend less than income · Pay bills on time · Have manageable debt · Have a prime credit score ·
> Have appropriate insurance · Plan ahead financially · Have sufficient liquid savings ·
> Have sufficient long-term savings

Домены: **SPEND** (вопросы 1–2), **SAVE** (3–4), **BORROW** (5–6), **PLAN** (7–8).

**Формулировки вопросов — дословно.**

> **Q1 (SPEND).** Which of the following statements best describes how your household's total
> spending compared to total income over the last 12 months?
> Spending was much less than income / a little less than income / about equal to income /
> a little more than income / much more than income

> **Q2 (SPEND).** Which of the following statements best describes how your household has paid
> its bills over the last 12 months? My household has been financially able to:
> Pay all our bills on time / nearly all / most / some / very few of our bills on time

> **Q3 (SAVE).** At your current level of spending, how long could you and your household afford
> to cover expenses, if you had to live on only the money you have readily available, without
> withdrawing money from retirement accounts or borrowing?
> 6 months or more / 3-5 months / 1-2 months / 1-3 weeks / Less than 1 week

> **Q4 (SAVE).** Thinking about your household's longer-term financial goals, such as saving for
> a vacation, starting a business, buying or paying off a home, saving up for education, putting
> money away for retirement, or making retirement funds last... How confident are you that your
> household is currently doing what is needed to meet your longer-term goals?
> Very confident / Moderately confident / Somewhat confident / Slightly confident / Not at all confident

> **Q5 (BORROW).** Thinking about all of your household's current debts, including mortgages,
> bank loans, student loans, money owed to people, medical debt, past-due bills, and credit card
> balances that are carried over from prior months... As of today, which of the following statements
> describes how manageable your household debt is?
> Do not have any debt / Have a manageable amount of debt / Have a bit more debt than is manageable /
> Have far more debt than is manageable

> **Q6 (BORROW).** How would you rate your credit score? Your credit score is a number that tells
> lenders how risky or safe you are as a borrower.
> Excellent / Very good / Good / Fair / Poor / I don't know

> **Q7 (PLAN).** Thinking about all of the types of insurance you and others in your household
> currently might have, including health insurance, vehicle insurance, home or rental insurance,
> life insurance, and disability insurance... How confident are you that those insurance policies
> will provide enough support in case of an emergency?
> Very confident / Moderately confident / Somewhat confident / Slightly confident / Not at all
> confident / No one in my household has any insurance

> **Q8 (PLAN).** To what extent do you agree or disagree with the following statement:
> "My household plans ahead financially."
> Agree strongly / Agree somewhat / Neither agree nor disagree / Disagree somewhat / Disagree strongly

**SCORING LOGIC — балльные значения дословно.**

| Вопрос | Вариант → баллы |
|---|---|
| Q1 | 100 much less than income · 75 a little less · 50 about equal · 25 a little more · 0 much more |
| Q2 | 100 all bills on time · 60 nearly all · 40 most · 20 some · 0 very few |
| Q3 | 100 «6 months or more» · 75 «3-5 months» · 50 «1-2 months» · 25 «1-3 weeks» · 0 «Less than 1 week» |
| Q4 | 100 Very · 75 Moderately · 50 Somewhat · 25 Slightly · 0 Not at all confident |
| Q5 | 100 «Do not have any debt» · **85** «manageable amount» · **40** «a bit more than manageable» · 0 «far more than manageable» |
| Q6 | 100 Excellent · 80 Very good · 60 Good · 40 Fair · 0 Poor · **0 «I don't know»** |
| Q7 | 100 Very · 75 Moderately · 50 Somewhat · 25 Slightly · **10 «Not at all confident»** · **0 «No one in my household has any insurance»** |
| Q8 | 100 Agree strongly · 65 Agree somewhat · 35 Neither · 15 Disagree somewhat · 0 Disagree strongly |

🔴 **Важное для нас: шкалы НЕ линейные и НЕ равношаговые.** Q2 (20-балльный шаг вниз от 100 к 60),
Q5 (100/85/40/0), Q6 (100/80/60/40/0), Q7 (…25/10/0), Q8 (100/65/35/15/0) — все с неравными
интервалами. Это единственный элемент «весов» в методике; отдельного вектора весов доменов нет.

**Агрегация — дословно:**

> Average of point values for QUESTIONS 1 - 8 → **FinHealth SCORE**
> Average of point values for QUESTIONS 1 & 2 → SPEND SCORE
> Average of point values for QUESTIONS 3 & 4 → SAVE SCORE
> Average of point values for QUESTIONS 5 & 6 → BORROW SCORE
> Average of point values for QUESTIONS 7 & 8 → PLAN SCORE

То есть агрегат — **невзвешенное среднее арифметическое восьми баллов**, каждый вопрос имеет
эффективный вес 1/8 = 12.5%, каждый домен — 25%. «Веса» спрятаны не в коэффициентах, а
в неравномерности балльных шкал.

**Шкала интерпретации — дословно:**

> **Financially Vulnerable** — Financial health scores between **0 - 39**. Individuals with scores
> in this range report healthy outcomes across few, or none, of the eight financial health indicators.
> **Financially Coping** — Financial health scores between **40 - 79**.
> **Financially Healthy** — Financial health scores between **80 - 100**.

**Бенчмарки (2021 National Averages, источник — U.S. Financial Health Pulse®):**

> FinHealth SCORE **66** · SPEND **75** · SAVE **69** · BORROW **61** · PLAN **61**

(в исходном PDF порядок чисел «66 75 69 61 61» напечатан одной строкой под заголовками
SPEND/SAVE/BORROW/PLAN + FinHealth SCORE; сопоставление домен↔число выше — по позиции,
и это **единственное место раздела, где есть риск смещения**; при использовании в тексте
перепроверить по оригиналу вёрстки.)

**Психометрическая валидация.** В самом Toolkit **не приводится** — ни размера выборки,
ни альфы Кронбаха, ни IRT. Даётся отсылка: «Visit finhealthnetwork.org/score for frequently
asked questions about the toolkit and to learn how we developed it».

**Лицензия.** «© 2021 Financial Health Network. All rights reserved.» — свободной лицензии
в документе **нет**. FinHealth Score® — зарегистрированный товарный знак. Для коммерческого
использования документ отсылает к контакту (hrobb@finhealthnetwork.org, «schedule a demo»),
что указывает на платный/договорной режим для enterprise-измерения.

**Обновление 2026.** По выдаче поиска: Financial Health Network провела многолетнюю переработку
и выпустила обновление Score в начале 2026 («From Insight to Impact: The Next Phase of Financial
Health Measurement», https://finhealthnetwork.org/research/from-insight-to-impact-the-next-phase-of-financial-health-measurement/).
🟡 **Не добыто дословно** — на момент записи открывался только Toolkit 2021.



### Б.2. CFPB Financial Well-Being Scale (США, госорган) — ПОЛНОСТЬЮ ДОБЫТО

**Реквизиты.** «CFPB Financial Well-Being Scale: Scale development technical report»,
Consumer Financial Protection Bureau, **май 2017**, 51 стр.
Официальная страница: https://www.consumerfinance.gov/data-research/research-reports/financial-well-being-technical-report/
**Канал добычи:** `curl` с браузерным UA по зеркалу Society for Judgment and Decision Making
https://sjdm.org/dmidi/files/CFPB_Financial_Well-Being_Scale_Technical_Report.pdf →
**HTTP 200, 794 352 байта**; `pdftotext` → 93 806 символов текста. Таблицы Приложения E —
растровые (`pdfimages -list` показал JPEG 931×134 на стр. 47), поэтому сняты **визуально
через `Read` с `pages: 47-48`** — это тот же приём «PDF на диск → Read(pages)», но применённый
к таблице-картинке внутри уже скачанного PDF.

**Определение конструкта — дословно:**

> Financial well-being is the feeling of having financial security and financial freedom of choice,
> in the present and when considering the future.

**Что это за инструмент — дословно из самоописания (с. 4, п. 3):**

> A free and publicly available survey instrument and measurement scale.

**Метод разработки.** Три раунда опросов, суммарно **свыше 14 000 респондентов**; финальная
аналитическая выборка разработки шкалы — **10 804 человека** (Table 4, Приложение A).
Раунд 1 — 46 кандидатных пунктов на 4 500 респондентов; раунд 2 — 7 899 респондентов;
раунд 3 — mode-testing (онлайн + 1 000 по телефону). Выборка набрана Survey Sampling
International, **не является национально репрезентативной** — прямая оговорка сноски 24:

> IRT scale development methods require a large and diverse sample of respondents, but not one
> that is nationally representative.

Разработка на двух возрастных группах раздельно: **18-61** и **62+** (обнаружены значимые
различия в интерпретации вопросов). IRT-моделирование выполнено в **flexMIRT® 2.0**.

**Демография аналитической выборки (Table 4):** N = 10 804 (100.00%); женщины 5 770 (53.41%),
мужчины 5 034 (46.59%); возраст 18-24 — 1 336 (12.37%), 25-34 — 1 622 (15.01%), 35-44 — 1 725
(15.97%), 45-54 — 1 914 (17.72%), 55-61 — 1 329 (12.30%), 62-69 — 1 415 (13.10%), 70+ — 1 463
(13.54%); раса: не указана 91 (0.84%), White 7 780 (72.01%), Black 1 072 (9.92%), Asian 434 (4.02%).

**Десять пунктов шкалы — дословно (Table 3).**
Блок 1, ответы по шкале «How well does this statement describe you or your situation?»
(Describes me completely / very well / somewhat / very little / Does not describe me at all):

> 1. I could handle a major unexpected expense
> 2. I am securing my financial future
> 3. Because of my money situation, I feel like I will never have the things I want in life* †
> 4. I can enjoy life because of the way I'm managing my money
> 5. I am just getting by financially* †
> 6. I am concerned that the money I have or will save won't last * †

Блок 2, ответы по шкале «How often does this statement apply to you?»
(Always / Often / Sometimes / Rarely / Never):

> 7. Giving a gift for a wedding, birthday or other occasion would put a strain on my finances
>    for the month*
> 8. I have money left over at the end of the month†
> 9. I am behind with my finances*
> 10. My finances control my life* †

> \* Denotes items for which the response options are "reverse coded."
> † Denotes items that are part of the abbreviated (5 item) scale.

Сокращённая **5-пунктовая** версия = пункты 3, 5, 6, 8, 10. Корреляция 10- и 5-пунктовой
версий — **0.94 (p<0.001)**.

**Кодировка ответов (Scoring worksheet, стр. 46 отчёта — снято визуально).**

Часть 1 (Completely / Very well / Somewhat / Very little / Not at all):
- пункты 1, 2, 4 → **4 / 3 / 2 / 1 / 0**
- пункты 3, 5, 6 (reverse) → **0 / 1 / 2 / 3 / 4**

Часть 2 (Always / Often / Sometimes / Rarely / Never):
- пункт 8 → **4 / 3 / 2 / 1 / 0**
- пункты 7, 9, 10 (reverse) → **0 / 1 / 2 / 3 / 4**

Итог: сырой суммарный балл (Total response value) в диапазоне **0–40**.

**Формула перевода в шкалу 0-100 — дословно (раздел 5.2.1):**

```
CFPB Financial Well-Being Scale Score = round ((IRT FWB score*15) + 50).
```

> Typical IRT-based scores are on the standard normal distribution – that is, a "bell-shaped"
> curve that has a mean of zero and a standard deviation value of one. For ease of interpretation
> and communication, the CFPB Financial Well-Being Scale scores are whole numbers between 0
> and 100. To get to the CFPB Financial Well-Being Scale metric from a raw IRT score, the value is
> multiplied by 15, added to 50, and then rounded to the nearest whole number.

**🔴 ПОЛНАЯ ПЕРЕВОДНАЯ ТАБЛИЦА (Appendix E, стр. 47 отчёта; снята визуально `Read pages 47-48`).**
Строка — сырой суммарный балл 0–40; столбцы — четыре группы (возраст × способ администрирования).

| Total response value | Self-adm. 18-61 | Self-adm. 62+ | By someone else 18-61 | By someone else 62+ |
|---|---|---|---|---|
| 0 | 14 | 14 | 16 | 18 |
| 1 | 19 | 20 | 21 | 23 |
| 2 | 22 | 24 | 24 | 26 |
| 3 | 25 | 26 | 27 | 28 |
| 4 | 27 | 29 | 29 | 30 |
| 5 | 29 | 31 | 31 | 32 |
| 6 | 31 | 33 | 33 | 33 |
| 7 | 32 | 35 | 34 | 35 |
| 8 | 34 | 36 | 36 | 36 |
| 9 | 35 | 38 | 38 | 38 |
| 10 | 37 | 39 | 39 | 39 |
| 11 | 38 | 41 | 40 | 40 |
| 12 | 40 | 42 | 42 | 41 |
| 13 | 41 | 44 | 43 | 43 |
| 14 | 42 | 45 | 44 | 44 |
| 15 | 44 | 46 | 45 | 45 |
| 16 | 45 | 48 | 47 | 46 |
| 17 | 46 | 49 | 48 | 47 |
| 18 | 47 | 50 | 49 | 48 |
| 19 | 49 | 52 | 50 | 49 |
| 20 | 50 | 53 | 52 | 50 |
| 21 | 51 | 54 | 53 | 52 |
| 22 | 52 | 56 | 54 | 53 |
| 23 | 54 | 57 | 55 | 54 |
| 24 | 55 | 58 | 57 | 55 |
| 25 | 56 | 60 | 58 | 56 |
| 26 | 58 | 61 | 59 | 57 |
| 27 | 59 | 63 | 60 | 58 |
| 28 | 60 | 64 | 62 | 60 |
| 29 | 62 | 66 | 63 | 61 |
| 30 | 63 | 67 | 65 | 62 |
| 31 | 65 | 69 | 66 | 64 |
| 32 | 66 | 71 | 68 | 65 |
| 33 | 68 | 73 | 70 | 67 |
| 34 | 69 | 75 | 71 | 68 |
| 35 | 71 | 77 | 73 | 70 |
| 36 | 73 | 79 | 76 | 72 |
| 37 | 75 | 82 | 78 | 75 |
| 38 | 78 | 84 | 81 | 77 |
| 39 | 81 | 88 | 85 | 81 |
| 40 | 86 | 95 | 91 | 87 |

Инструкция к таблице дословно: «Because scores vary based on age and how the questionnaire
was administered, you must convert the total response value to a financial well-being score.»
Ограничение дословно: «The table-based method should not be used if a respondent does not
answer all questions in the scale».

**Психометрика — Table 6, marginal reliability:**

| Mode | 10 Item, Age 18-61 | 10 Item, Age 62+ | 5 Item, Age 18-61 | 5 Item, Age 62+ |
|---|---|---|---|---|
| Online | **0.89** | **0.90** | 0.82 | 0.83 |
| Phone | **0.90** | **0.89** | 0.84 | 0.82 |

> Marginal reliability can be interpreted similar to Cronbach's alpha. […] The minimum standard
> for a scale to be considered generally credible is .70, so the CFPB Financial Well-Being Scale,
> at or above .80, can be considered highly reliable for all combinations of respondent age,
> survey mode, and scale version.

**Валидация (Table 7, Spearman-корреляции 10-пунктового IRT-балла с внешними критериями):**

| Внешний критерий | N | ρ |
|---|---|---|
| «How would you rate your current credit record?» (1–5) | 6 854 | **0.53*** |
| Уверенность собрать $2 000 при внезапной нужде (1–4) | 7 030 | **0.64*** |
| Есть ли резерв на 3 месяца расходов (нет/да) | 7 310 | **0.54*** |
| Самооценка текущей фин. ситуации (1–7) | 7 222 | **0.63*** |
| «нужна была еда, но не мог купить» (нет/да) | 10 166 | **−0.43*** |
| Не пошёл к врачу из-за денег (нет/да) | 10 166 | **−0.35*** |
| Был долг в коллекшене (нет/да) | 1 218 | **−0.30*** |
| Число негативных финансовых шоков за 12 мес. (из 10) | 10 166 | **−0.31*** |

`*** = p < .0001`.

**Лицензия / условия использования.** Отчёт прямо называет шкалу «**A free and publicly
available survey instrument and measurement scale**» (с. 4). CFPB — федеральное ведомство США,
его работы не охраняются авторским правом США (17 U.S.C. §105); в самом PDF знака «©» нет
(поиск по тексту дал 0 вхождений). Отдельного текста лицензии в отчёте нет — 🟡 то есть
«public domain» здесь **вывод из статуса органа + самоописания «free and publicly available»**,
а не процитированная лицензионная оговорка. Для юрблока это надо подтвердить отдельно.
Дополнительно CFPB бесплатно раздаёт Stata-пакет `pfwb.ado` (разработан Abt Associates
для CFPB, Приложение F) для прямого IRT-скоринга.

**Что это НЕ измеряет (важно для FINPILOT).** Шкала целиком **субъективная и дескриптивная**:
все 10 пунктов — самоотчёт об ощущении («feel», «concerned», «enjoy»), ни одного объективного
показателя (ни дохода, ни ставки, ни ПДН, ни остатка). Отчёт прямо оговаривает, что отдельных
подшкал нет: «there is no "freedom of choice" score». Она даёт **одно число состояния**, не даёт
ни одной величины, пригодной как критерий в задаче распределения потока.


### Б.3. 🔴 CBA–Melbourne Institute Financial Wellbeing Scales (Австралия) — ПОЛНОСТЬЮ ДОБЫТО

**Самая близкая к нашей задаче методика из всех найденных**, потому что у неё есть
**вторая, ОБЪЕКТИВНАЯ шкала, считаемая из банковских записей без единого вопроса пользователю**.

**Реквизиты первоисточника.** Comerton-Forde C., Ip E., Ribar D.C., Ross J., Salamanca N.,
Tsiaplias S. «Using Survey and Banking Data to Measure Financial Wellbeing»,
CBA–Melbourne Institute Financial Wellbeing Scales **Technical Report No. 1, март 2018**,
Melbourne Institute: Applied Economic & Social Research, University of Melbourne.
Chapters 1–6 (37 стр.): https://melbourneinstitute.unimelb.edu.au/__data/assets/pdf_file/0005/2839433/CBA_MI_Tech_Report_No_1_Chapters_1_to_6.pdf
Журнальная версия: Comerton-Forde et al. «Measuring Financial Wellbeing with Self-Reported
and Bank Record Data», *Economic Record*, 2022, DOI 10.1111/1475-4932.12664 (Wiley,
🟡 пейволл, не открывался).

**Канал добычи (важный замер).** `WebFetch` по домену unimelb.edu.au → **HTTP 403**.
`curl` с браузерным UA → **HTTP 403, 5 933–6 002 байта** (страница Okta/Cloudflare).
Текстовый прокси `r.jina.ai` по «новому» пути (`/0010/4752721/`) вернул **страницу логина
University of Melbourne** — то есть файл там за авторизацией. По «старому» пути
(`/0005/2839433/`) тот же `r.jina.ai` вернул **HTTP 200, 82 945 байт, 37 страниц полного
текста**. 🔴 **Вывод для методики добычи: у одного и того же PDF на сайте могут быть два пути,
и старый может быть открыт, когда новый закрыт — проверять оба.**

**Данные.** Онлайн-опрос **5 682** клиентов Commonwealth Bank of Australia, первая неделя
августа 2017, партнёр FiftyFive5; ответы связаны с банковскими записями тех же клиентов.
После отбраковки (50 не ответили на все вопросы шкалы и др.) аналитическая выборка —
**4 470 клиентов**. Три страты: A — национально репрезентативная (1 611 ответов),
B — sole-MFI, C — «high-visibility» split-MFI (1 172 ответа).

#### Б.3.1. Reported Financial Wellbeing Scale (субъективная, 10 вопросов)

Источники вопросов — дословно: «six from the CFPB (2015), one from Muir et al. (2017),
two from FiftyFive5 (2017), and one that we developed».

**Table 4.1 — вопросы и кодировка, дословно:**

> **1.** In the last 12 months, how difficult was it for you to meet your necessary cost of living
> expenses like housing, electricity, water, health care, food, clothing or transport? (Muir et al. 2017)
> `0 - Very difficult · 1 - Difficult · 2 - Neither difficult nor easy · 3 - Easy · 4 - Very easy`

> *How well do the following statements describe you or your situation?* (CFPB 2015)
> **2.** I can enjoy life because of the way I'm managing my money
> **3.** I could handle a major unexpected expense
> **4.** I am securing my financial future
> `0 - Not at all · 1 - Very little · 2 - Somewhat · 3 - Very well · 4 - Completely`

> *How often do the following statements apply to you?* (CFPB 2015)
> **5.** My finances control my life *
> **6.** I have money left over at the end of the month
> **7.** Giving a gift for a wedding, birthday or other occasion would put a strain on my finances
> for the month *
> `0 - Never · 1 - Rarely · 2 - Sometimes · 3 - Often · 4 - Always`

> *When it comes to how you think and feel about your finances, please indicate the extent to which
> you agree or disagree with the following statements* (FiftyFive5 2017 and Comerton-Forde et al. 2018)
> **8.** I feel on top of my day to day finances
> **9.** I am comfortable with my current levels of spending relative to the funds I have coming in
> **10.** I am on track to have enough money to provide for my financial needs in the future
> `0 - Disagree strongly · 1 - Disagree · 2 - Neither agree nor disagree · 3 - Agree · 4 - Agree strongly`

> \* Negative statement that is reverse-coded in scale.

**Формула — дословно:**

```
Reported Financial Wellbeing Scale = Sum of responses to items 1 to 10 multiplied by 2.5
```

> A person's reported financial wellbeing scale value is formed by adding the responses to all 10
> questions and multiplying the sum by 2.5. This results in a 0-100 scale in which larger values
> indicate higher amounts of reported financial wellbeing.

Сумма 0–40 → шкала 0–100, **41 возможное значение**, все веса равны 1.

**Отображение на домены конструкта — дословно:**

> Item 1 addresses **meeting financial obligations**; items 2 and 6 address **financial freedom**;
> items 5, 8 and 9 address **control over finances**; and items 3, 4, 7 and 10 address **financial
> security**. Similarly, items 1, 2, 8 and 9 address **everyday** situations; 3 and 7 address
> **rainy day** situations; and 4 and 10 address **one day** situations.

#### Б.3.2. 🔴 Observed Financial Wellbeing Scale (ОБЪЕКТИВНАЯ, 5 показателей из банковских записей)

**Это единственная найденная в теме 20 вычислимая шкала финздоровья, которой НЕ нужен опрос.**

**Table 4.2 — дословно:**

> **11.** Number of months in last year with **payment dishonours**
> `0 - 7 or more months · 1 - 1 to 6 months · 2 - None`
> **12.** Any **payday loans** in last year?
> `0 - Yes · 1 - No`
> **13.** Days in last year with **liquid balances below one week's average expenses**
> `0 - 75% or more · 1 - 1% to 75% · 2 - Never`
> **14.** Days in last year during which customer had the **ability to raise one month's expenses
> from savings or available credit**
> `0 - 25% or less · 1 - 25% to 99% · 2 - Always`
> **15.** **Age-normed percentile of customer's median savings balance** over last year
> `0 - Below 35th percentile · 1 - 35th to 90th percentile · 2 - Above 90th percentile`

**Формула — дословно:**

```
Observed Financial Wellbeing Scale = Sum of outcomes from items 11 to 15 multiplied by 100/9
```

Максимум суммы = 2+1+2+2+2 = 9, отсюда множитель 100/9. Веса равны, шкала 0–100.

Соотнесение с конструктом — дословно: «Items 11 and 12 encompass elements of **meeting
financial obligations**; item 13 addresses conditions that give rise to **financial freedom**;
and items 14 and 15 describe outcomes that provide **control and security**».

Корреляция Reported и Observed шкал — **Spearman ρ = 40 %**, то есть они меряют
**существенно разные вещи**, и авторы прямо это заявляют.

#### Б.3.3. 🔴 Ключевой методологический результат — простая сумма ≈ IRT

Прямая цитата, важная как обоснование для нашей SAW-свёртки:

> Both of our scales are formed from **simple summations of categorical responses**. This method
> imposes restrictions on the underlying data. It treats each item as being **equally informative** […]
> We compared our simple scales to more complex scales based on Item Response Theory model
> estimates that allowed for differences among items in terms of their reliability and response
> differences. **Our simple scale of reported financial wellbeing was correlated 99.2 per cent with
> a more flexible IRT scale, and our simple scale of observed financial wellbeing was correlated
> 98.0 per cent with a more flexible IRT scale. Therefore, our simple scales are appropriate and
> capture almost all the information of more flexible but complex scales.**

То есть авторы, имея полную IRT-модель, **сознательно выбрали невзвешенную сумму**, показав,
что усложнение даёт менее 1 % информации. Это прямой аргумент против требования «обосновать
веса психометрически» применительно к прикладному индексу.

#### Б.3.4. 🔴 ЛИЦЕНЗИЯ — прямой запрет коммерческого использования

Дословно со страницы условий (добыто через `r.jina.ai`, HTTP 200):

> By downloading these Scales, you agree that you will **only use them for your organisation's
> internal, non-commercial purposes** (e.g., to monitor the financial wellbeing of your customers).
> **If you want to use the Scales to create a commercial product or service for individuals, industry
> clients and/or practitioners (e.g., to provide individual FWB assessments as part of a bundled
> service, or to create an FWB score or index to sell to the financial services industry), then please
> contact us to discuss licensing options.**

> If you use or reference the Scales, we ask that you refer to them as the "**Melbourne Institute
> Financial Wellbeing Scales**" or "**MI Financial Wellbeing Scales**" and cite the initial report
> (e.g., cite Comerton-Forde et al., 2018) with each use. **If you use the methodology in a different
> scale or modify it, we ask that you give your other / modified scale a different name.**

> Neither the Commonwealth Bank of Australia nor the Melbourne Institute shall be liable for any
> errors or omissions […] All information is provided "as is", without any warranties (express or
> implied) […] and does not constitute financial advice.

🔴 **Для FINPILOT (коммерческий SaaS) прямое использование шкал требует отдельной лицензии.**
Ссылаться и цитировать — можно; встроить в продаваемый продукт — нет без договора.
Исследователи проекта: Ferdi Botha, John P. de New, Carsten Murawski (Melbourne Institute /
Department of Finance, University of Melbourne); контакт по лицензированию —
Melb-Inst@unimelb.edu.au.

**Прочие отчёты серии (URL добыты, содержимое не разбиралось):**
Tech Report No. 2 «Using Survey and Banking Data to Understand Australians' Financial Wellbeing»
(июль 2018); No. 3 «Improving the CBA–MI Observed Financial Wellbeing Scale» (февраль 2019,
описывает версию 2 наблюдаемой шкалы — «twice as many outcomes than the first version»);
No. 5 «Developing a short form version […]» (март 2020, короткая версия из 5 вопросов).


### Б.4. OECD/INFE Toolkit — 🔴 ИЗМЕРЕННЫЙ ОТРИЦАТЕЛЬНЫЙ РЕЗУЛЬТАТ: формулы балла финблагополучия НЕТ

Проверены **две редакции**, обе добыты полностью.

**Редакция 2022.** «OECD/INFE Toolkit for Measuring Financial Literacy and Financial Inclusion 2022»,
© OECD 2022. `curl` + UA → **HTTP 200, 1 881 374 байта**; `pdftotext` → 126 884 символа.
URL: https://www.oecd.org/content/dam/oecd/en/publications/reports/2022/03/oecd-infe-toolkit-for-measuring-financial-literacy-and-financial-inclusion-2022_54dba970/cbc4114f-en.pdf

**Редакция 2026.** «OECD/INFE Toolkit for Measuring Financial Literacy, Inclusion and Well-Being 2026»,
© OECD 2026. `curl` + UA → **HTTP 200, 2 355 961 байт**; `pdftotext` → 160 759 символов.
URL: https://www.oecd.org/content/dam/oecd/en/publications/reports/2026/01/oecd-infe-toolkit-for-measuring-financial-literacy-inclusion-and-well-being-2026_6e8d9566/92f2d439-en.pdf

**Что там есть по финблагополучию (2022) — дословно:**

> **Five financial well-being questions incorporated in the short financial well-being survey developed
> by the Consumer Financial Protection Bureau in the US**, and questions reflecting aspects identified
> through the OECD work on financial well-being.

То есть ОЭСР **не разрабатывала своей шкалы**, а вставила **5-пунктовую короткую шкалу CFPB**
(см. Б.2) внутрь блоков QS1/QS2 своей анкеты. В анкете 2022 эти пункты рассыпаны среди других
утверждений и кодируются `1='Always' … 5='Never'` (QS1) и `1='completely' … 5='not at all'` (QS2) —
🔴 **шкала обратная по направлению к кодировке CFPB (там 4 = лучший исход)**. Комментарий
Приложения A дословно: «Statements 3, 9, 10 and 11 are included in order to explore **subjective
financial well-being**».

**🔴 Чего там НЕТ.** Поиск по всему тексту 2022 (`grep -i "financial well-being score"`) — **0 вхождений**.
Приложение A определяет **только** `Financial literacy score` (behaviour / attitude / knowledge)
и `Digital financial literacy score`, каждый через явное «1 point if …». **Правила агрегации пяти
пунктов благополучия в балл в документе не приводится вовсе.**

Редакция 2026 — то же самое. Поиск `"well-being score"` по всему тексту — **0 вхождений**.
Box 5 «Categories of questions» дословно:

> Category 1 contains core mandatory questions/statements that: […] are used in the calculation of
> **financial literacy and digital financial literacy scores** […]; cover important outcomes
> (**financial well-being**, exposure to frauds and scams) […]
> The OECD/INFE international report based on data collected by the Toolkit 2026 will contain
> a detailed explanation of **how the financial literacy scores are created**. Researchers/institutions
> using the Toolkit 2026 are welcome to **contact the OECD/INFE Secretariat for any enquiries
> related to scoring**.

Определение конструкта в 2026 (в русле G20 Policy Note on Financial Well-being, OECD 2024) —
дословно:

> Questions on financial well-being cover aspects regarding the ability of individuals to smoothly
> manage their financial needs and obligations, to cope with negative shocks, to pursue aspirations,
> goals and capture opportunities and to feel satisfied and confident about their financial lives.

**Вывод по п.4 задания: у ОЭСР вычислимого агрегата финансового благополучия нет.**
Есть скоринг **финансовой грамотности** (что мы и так знали по ЦБ РФ) и заимствованный
опросник CFPB без правил свёртки. Для FINPILOT как источник формулы — **не годится**;
как источник формулировок вопросов на русском языке (переводы Toolkit существуют) — годится.


### Б.5. UK Money and Pensions Service (MaPS) — сегментация есть, вычислимого индекса не добыто

**Что добыто.** «MONEY AND PENSIONS SERVICE (MaPS) FINANCIAL WELLBEING SEGMENTATION»,
приложение к UK Data Archive Study Number 8454 «Financial Capability Survey, 2018».
`curl` + UA → **HTTP 200, 870 419 байт**; `pdftotext -layout` → 2 951 символ (документ на 2 страницы).
URL: https://doc.ukdataservice.ac.uk/doc/8454/mrdoc/pdf/8454_maps_fin_wellbeing_segmentation.pdf

🔴 **Это НЕ индекс, а сегментация.** Дословно:

> MaPS has recently updated its Financial Wellbeing Segmentation model, which was originally
> created by the Money Advice Service in conjunction with **CACI** in 2016. As well as using data
> from the Adult Financial Capability Survey, this 'refreshed' model has introduced additional
> **indebtedness variables** (from the Financial Need survey), and additional **pensions variables**
> (from the FCA Financial Lives Survey).
> As per the original model from 2016, three 'macro' segments remain (i.e. the **'Struggling',
> 'Squeezed' and 'Cushioned'**). The under-pinning **sub-segments (14 in total)** have been updated…

Описания макро-сегментов дословно:

> **Struggling** — Least financially resilient segment: Lowest incomes, benefit dependent · Low
> provision for later life · Little or no savings buffer · Many in social housing · Higher incidence
> of disability and single parents · Lower financial confidence · High over-indebtedness
> **Squeezed** — High risk segment: Average incomes, but living beyond their means · High access
> to and use of credit · Insufficient savings buffers to cope with income shocks (both major and
> minor) · Not prepared for later life
> **Cushioned** — Most financially resilient segment: Highest incomes and savings – most can absorb
> 'bumps in the road' · Comfortable provision for later life · Confident with money · BUT not
> immune to major income shocks

14 микро-сегментов (переменные `maps_seg_macro` и `maps_seg_micro` в датафайлах) дословно:
`1a Struggling Younger Adults · 1b Struggling Credit Dependent · 1c Struggling Making Do ·
1d Struggling Retirees · 2a Younger Squeezed · 2b Squeezed Families · 2c Squeezed Pre-Retired ·
2d Squeezed Retired · 3a Cushioned Still at Home · 3b Cushioned Younger Professionals ·
3c Cushioned Settled Families · 3d Cushioned Confident Older Families · 3e Cushioned Empty
Nesters · 3f Cushioned Retiring`.

**Чего не добыто.** У MaPS есть отдельный **Financial Fitness Tool (FFT) score** — по описанию
поисковой выдачи «an index of several key themes […] key components such as savings, financial
resilience and retirement planning included in the FFT score» и «nine questions». Методический
документ **не открылся**: `WebFetch` по `maps.org.uk` → **HTTP 403**; `r.jina.ai` → HTTP 200,
но тело — **страница антибот-верификации** («Performing security verification … This website uses
a security service to protect against malicious bots»). Формулу и веса FFT считать недобытыми.

🔴 **Методическое отличие MaPS от FinHealth/CFPB, важное для нас:** британцы решают задачу
не баллом, а **классификацией домохозяйства в один из 14 сегментов** — то есть выходом является
не число, а тип. Это третья принципиальная схема (после «взвешенная сумма» и «IRT-латентный
конструкт»), и она ближе к нашим фиксированным риск-профилям, чем к индексу.

### Б.6. Есть ли у регулятора вычислимый индекс финздоровья ДОМОХОЗЯЙСТВА — ответ: НЕТ ни у одного из проверенных

| Регулятор / орган | Что есть | Индекс здоровья ДОМОХОЗЯЙСТВА |
|---|---|---|
| **CFPB (США)** | Financial Well-Being Scale, 10 вопросов, IRT, public-domain (Б.2) | 🟡 **Есть шкала, но чисто субъективная**: 10 самоотчётных пунктов, ни одного объективного показателя |
| **ЦБ РФ** | Опросный индекс финансовой грамотности (54 балла, 2023) | 🔴 **НЕТ** (подтверждено темой 19) |
| **OECD/INFE** | Скоринг финансовой грамотности и цифровой финграмотности; вопросы благополучия без правил свёртки (Б.4) | 🔴 **НЕТ** — формулы агрегата не существует в документе |
| **MaPS (Великобритания)** | Сегментация 3 макро / 14 микро (Б.5) | 🔴 **НЕТ индекса**, есть классификация |
| **Banco de España** | Композитный **индикатор финансовой уязвимости домохозяйств** в Financial Stability Report | 🟡 **Есть, но СЕКТОРАЛЬНЫЙ, а не индивидуальный**: «positive values indicate higher financial vulnerability than the average for the period 2005-2025 Q4, while negative values indicate lower financial vulnerability» — это z-подобная агрегатная величина по сектору домохозяйств для целей макропруденциального надзора, а не оценка конкретной семьи. Состав раскрыт в Box 2 «Report on the Financial Situation of Households and Firms». Дословный разбор состава **не добывался** |

**Прямой вывод:** ни один проверенный регулятор не публикует **вычислимый индекс финансового
здоровья конкретного домохозяйства из объективных данных**. Регуляторы делают либо опросные
шкалы (CFPB, ОЭСР), либо секторальные индикаторы уязвимости (Banco de España), либо сегментацию
(MaPS). **Единственная найденная вычислимая объективная шкала на уровне домохозяйства —
не регуляторная, а банковская: CBA–MI Observed Financial Wellbeing Scale (Б.3.2).**

### Б.7. Российский контур — раскрытие методик отсутствует, зафиксировано измеренно

#### Б.7.1. НАФИ — индекса финансового здоровья НЕТ

Проверена страница реестра индексов: https://nafi.ru/ratings/ (`WebFetch`, HTTP 200).
Полный перечень индексов НАФИ на странице:
`Индекс RSBI · Индекс ИСИАР (сберегательно-инвестиционной активности россиян) · Индекс финансовой
грамотности · Индекс цифровой грамотности · Индекс качества розничного сервиса · Индекс доверия
рекламе · Индекс цифровой финансовой грамотности · NPS на рынке розничных банковских услуг`.

🔴 **«Индекса финансового здоровья россиян» в перечне НЕТ.** Задание исходило из того, что
у НАФИ такая методика есть — **это предположение не подтвердилось**. Ближайшее — индекс
финансовой грамотности, построенный по методологии ОЭСР (то есть по Б.4, где агрегата
благополучия нет).

#### Б.7.2. Сбер и Т-Банк — состав доменов известен, формула не раскрыта

**Первоисточник:** Мария Фрай, «Доходы ИИ расходы: банки запускают сервисы по улучшению
"финансового здоровья" россиян», Известия, **15 августа 2024** (не 14-е, как предполагалось
в задании). URL: https://iz.ru/1742865/mariia-frai/dokhody-ii-raskhody-banki-zapuskaiut-servisy-po-uluchsheniiu-finansovogo-zdorovia-rossiian
Канал: `WebFetch` → HTTP 200.

**Т-Банк, сервис «Финздоровье»** — состав показателей по статье:
общее количество денег пользователя · период, на который хватит накопленных денег ·
кредитный рейтинг · **кредитная нагрузка (доля дохода на погашение долга)** · траты на подписки ·
инвестиции и доходы от них · финансовая защита.
Цитата из статьи: «система показывает кредитный рейтинг клиента: чем он выше, тем больше
вероятность получить выгодные условия по ссуде». Заявленные планы — автоматический прогноз
будущих расходов и помощь в составлении бюджета.

**Сбер, сервис «Финансовое здоровье»** (на момент статьи — тестовый режим, ограниченный доступ) —
**четыре базовые сферы**: расходы · финансовая подушка · инвестиции · защита.

Более детальный состав доменов Сбера (по анонсу запуска, июнь 2023, вторичные источники —
irk.ru, ysia.ru, yakutiamedia.ru):
- регулярные расходы — «сколько месяцев за предыдущие полгода клиент тратил меньше, чем
  поступало на его счета в Сбере»;
- размер финансовой подушки — «как долго она позволит клиенту сохранять привычный образ жизни»;
- уровень защищённости — «насколько застрахованы жизнь, здоровье и имущество клиента»;
- уровень риска и сбалансированность инвестиционного портфеля;
- будущая пенсия — «рассчитывает её размер на данный момент и сравнивает с текущим доходом».
🟡 Это **пересказ пресс-релиза в региональных новостных лентах**, не первоисточник Сбера;
использовать в научном тексте только со ссылкой на новостной характер источника.

🔴 **Итог по РФ: ни у Сбера, ни у Т-Банка формула, веса, шкала и пороги нигде не опубликованы.**
Ни патента, ни свидетельства, ни методической статьи, ни доклада найти не удалось (см.
«Что не добыто»). Состав доменов **совпадает с международной рамкой** Spend / Save / Borrow /
Plan-Protect (FinHealth Network, Б.1) с национальной добавкой «пенсия» и «инвестиции».


---

## БЛОК В. Три прямых вопроса

### В.1. Есть ли патентный блокер для FINPILOT на рынке РФ?

**Ответ: в проверенном объёме — НЕТ. Ни одного действующего документа с российской правовой
силой, чьи независимые пункты накрывали бы конструкцию FINPILOT, не обнаружено.**

Обоснование по трём независимым линиям.

**1. Российский национальный массив — пусто (А.5).** Просмотрены целиком три класса СПК
(G06Q 40/02 — 101 документ, G06Q 40/06 — 42, G06Q 30/0631 — 50), портфель ПАО «Сбербанк»
в G06Q 40/00 (10 из 10 документов перечислены поимённо), портфель АО «Тинькофф Банк»
(12 документов). Тематика российского финансового массива — платёжные транзакции, антифрод,
банкоматы и инкассация, биржевые инструменты, кредитный скоринг для банка. **Персонального
финансового менеджера, индекса финздоровья и распределения свободного потока в нём нет.**

**2. Иностранные патенты не имеют российских членов семьи.** Блок «Also Published As» проверен
у каждого разобранного документа:
- US12047359B2 (BrightPlan, Active) — только US-члены семьи;
- Capital One (US11023967B1 / US11669897B2 / US12008644B2 / US20230252559A1) — только US;
- USAA US12141861B1 — только US; Intuit, Strands, Wells Fargo, Truist — только US;
- BoA US8412622B2 — есть **WO2010114732A1**, но национальной фазы RU в блоке нет;
- Responsive Capital US12229832B2 — CA + EP + WO, **RU нет**.
🔴 **Патент действует только там, где выдан.** US-патент не создаёт запрета в РФ ни при каких
условиях; это ключевой факт для оценки риска.

**3. Даже по существу конструкции совпадений нет.** Ни один из ~330 просмотренных документов
не заявляет в формуле **перебор дискретного множества альтернатив распределения потока
со скалярной свёрткой по взвешенным критериям и ранжированием**. Найденные механизмы делятся
на четыре класса, и все они другие:
- **дерево решений по пороговым правилам** — Capital One (branch of a decision tree по четырём
  величинам, порог ставки);
- **иерархическая взвешенная сумма для ИНДЕКСА (не для выбора альтернативы)** — BrightPlan;
- **ML-предсказание одной величины / next best action** — USAA, Truist, Wells Fargo,
  Responsive Capital, Intuit;
- **исполнение заданных пользователем приоритетов** — Strands, KeyBank (тема 19).
Ближайший по ЗАДАЧЕ документ — **US20250315893A1 (Insphire IO)**: там прямо заявлено
«optimizing the allocation of resources among debt reduction, savings, and investments»,
но метод — **RL + CRRA-функция полезности**, одна скалярная целевая функция, без перебора сетки,
без многокритериальной свёртки, без инвариантов; статус **Pending**, семьи вне США нет.

🟡 **Три оговорки, ограничивающие силу этого вывода:**
(а) **реестр свидетельств о госрегистрации программ для ЭВМ Роспатента не проверялся вообще** —
ФИПС недоступен (403 DDoS-Guard на всех каналах), а Google Patents этот реестр не индексирует;
(б) полнотекстовый поиск по RU в Google Patents неполон (русские фразы дают нули там, где
СПК-фильтр даёт выдачу) — поиск по РФ фактически шёл по классам, а не по тексту;
(в) национальные фазы WO2010114732A1 (BoA) отдельно не проверялись.
Поэтому корректная формулировка — **«блокер не найден в проверенном объёме»**, а не
«блокера не существует». Для патентной чистоты перед подачей нужен платный поиск по ФИПС.

### В.2. Можно ли взять готовую валидированную шкалу финздоровья вместо своей?

**Ответ: можно взять ровно одну — CFPB Financial Well-Being Scale. Но она НЕ решает нашу
задачу и годится только как дополнительный дескриптивный слой.**

**Сравнение четырёх кандидатов по пригодности:**

| Шкала | Валидация | Лицензия для коммерческого SaaS | Вход | Годится нам? |
|---|---|---|---|---|
| **CFPB FWB Scale** | 🟢 сильнейшая: N=10 804, IRT (flexMIRT 2.0), marginal reliability 0.89–0.90, 8 внешних валидаторов | 🟢 «free and publicly available», федеральный орган США (17 U.S.C. §105); знака © в документе нет | 10 вопросов, **только самоотчёт** | 🟡 как отдельный опрос — да; как источник критериев — нет |
| **FinHealth Score (FHN)** | 🟡 в Toolkit не приводится вовсе | 🔴 «All rights reserved», ® — enterprise по договору | 8 вопросов, самоотчёт | 🔴 нет |
| **CBA–MI Reported / Observed** | 🟢 IRT, N=4 470; простая сумма ≈ IRT (99.2 % / 98.0 %) | 🔴 **прямой запрет**: «only […] internal, non-commercial purposes»; продажа индекса — отдельное лицензирование | Reported — 10 вопросов; **Observed — 5 показателей из банковских записей** | 🔴 без лицензии нет; 🟢 **как образец методики Observed — самый ценный источник** |
| **OECD/INFE** | — | 🟢 открыто | — | 🔴 **формулы агрегата не существует** |

**Что эти шкалы измеряют и чего они принципиально НЕ измеряют применительно к нашей задаче:**

🔴 **Разрыв дескриптивного и прескриптивного.** Все найденные шкалы отвечают на вопрос
«**насколько человеку сейчас хорошо/плохо**» и выдают **одно число состояния**.
FINPILOT отвечает на другой вопрос — «**куда направить следующий рубль свободного потока**» —
и выдаёт **вектор долей с обоснованием**. Между этими задачами нет прямого перехода:

- **Шкала не даёт критериев для сравнения альтернатив.** Чтобы ранжировать 66 вариантов
  распределения, нужны величины, **зависящие от выбранного варианта** (стоимость обслуживания
  долга при данном варианте, покрытие резерва при данном варианте, срок достижения цели).
  Все 10 пунктов CFPB и все 8 FinHealth — величины **текущего состояния**, инвариантные
  к нашему решению. Подставить их в SAW нельзя вообще.
- **Шкала не содержит ни одного ограничения.** Наши инварианты (Rt ≥ 0, ПДН ≤ 0.40) — это
  область допустимости, а шкале понятие допустимости чуждо: она размечает состояние, а не
  отсекает недопустимые действия.
- **Субъективность.** У CFPB все 10 пунктов — про ощущение («feel», «concerned», «enjoy»).
  Это по построению не вычисляется из транзакций, а требует опроса, и меняется медленнее
  и иначе, чем финансовое положение.
- **Разные страны.** Q6 CFPB/FinHealth про «prime credit score» и Q7 про страховое покрытие
  (health insurance) прямо привязаны к институтам США. Для РФ Q6 нужно переопределять
  на ПКР/НБКИ, Q7 — на ОМС/ДМС, то есть шкала перестаёт быть той же шкалой,
  а с ней рушится и вся заявленная валидация.

**Практический вывод для продукта.**
1. **Собственную прескриптивную модель (SAW + инварианты) заменить нечем — ни одна найденная
   шкала не является её альтернативой.** Претензия «взяли бы готовую валидированную»
   методологически некорректна: готовые шкалы решают другую задачу.
2. **Если нужен дополнительный ДЕСКРИПТИВНЫЙ показатель состояния** («индекс финздоровья»
   рядом с рекомендацией) — брать **CFPB FWB Scale**: единственная одновременно
   психометрически сильная и юридически свободная. Полная переводная таблица (Б.2) в файле есть,
   реализуется без внешних зависимостей.
3. **Если нужен ОБЪЕКТИВНЫЙ показатель из транзакционных данных** — брать **не саму шкалу**,
   а **её конструкцию** у CBA–MI Observed (Б.3.2): пять категориальных показателей из банковских
   записей, равные веса, нормировка множителем 100/max. Лицензия запрещает использовать
   ИХ шкалу в коммерческом продукте, но условия прямо предусматривают вариант «модифицируете —
   дайте другое имя»; плюс сами авторы доказали, что равновесная сумма даёт 98–99 % информации
   полной IRT-модели, что снимает необходимость воспроизводить их калибровку.
4. 🔴 **Ссылаться в ВКР/статье можно на все четыре, использовать в коде — только на CFPB.**

### В.3. Патентуется ли scoring как таковой?

**Ответ: ДА, и это подтверждено выданным действующим патентом. Причём патентуется именно
ФОРМУЛА агрегации, а не UI и не сбор данных.**

**Главное доказательство — US12047359B2 (BrightPlan LLC, выдан 2024-07-23, статус Active).**
Claim 1 не содержит ни интерфейса, ни источников данных, ни ML — только арифметику агрегации:

> determining a pillar score for each of a plurality of pillars, the pillar score being a **weighted
> percentage of a financial wellness score**, each of the plurality of pillars including a component
> data attribute, the component data attribute being a **weighted percentage of the pillar score**
> for each of the plurality of pillars; and **calculating the financial wellness score using the
> pillar score** for each of the plurality of pillars.

Обёртка «A secure messaging system configured by at least one processor…» — стандартный приём
преодоления *Alice* (привязка к машине); содержательно защищена **двухуровневая взвешенная
свёртка**. Состав столпов вынесен в зависимые claims (8–13), то есть заявитель защитил
и общую схему, и конкретный набор доменов.

**Второе доказательство — US8412622B2 (Bank of America, выдан 2013-04-02, Active).** Claim 1
защищает индекс, определяемый **как функция двух конкретных входов** (кредитный балл бюро +
отклонение факта от целевого бюджета) с требованием обновления в реальном времени. Это тоже
формула, а не интерфейс — визуализация вынесена в зависимые claims (7 — «financial health score»,
8 — «a color within a financial health color spectrum»).

**Границы патентоспособности, видимые по массиву:**
- Патентуется **схема свёртки** (иерархия столпов, набор входов, правило обновления), но
  **числовые веса в claims никто не раскрывает** — ни BrightPlan, ни BoA. Веса остаются
  коммерческой тайной; в формулу выносится структура.
- **Заявки на «wellness score» без конкретного механизма забрасываются**: BoA US20140372340A1
  «Financial wellness scoring tool» (перечень поведенческих факторов, формулы нет) — **Abandoned**;
  Intuit US20190378207A1 — **Abandoned**; Strands US20120059751A1 — **Abandoned**.
  Из четырёх заброшенных — все без раскрытого вычислительного механизма в независимом пункте.
- Практический ориентир для нашей заявки: **выигрывает независимый пункт, в котором есть
  конкретный вычислительный шаг** (у BrightPlan — двухуровневая взвешенная доля; у Capital One —
  ветвление дерева по комбинациям значений четырёх величин; у BoA — функция двух входов
  с реальным временем). Голая формулировка «оцениваем финансовое здоровье и даём совет»
  ведёт к abandonment.


---

## Что не добыто и почему

Каждая строка — с кодом ответа канала. «Не смог открыть» без кода в этот список не попадает.

### Полностью недобытые участки

| Что | Каналы и коды | Последствие |
|---|---|---|
| 🔴 **Реестр свидетельств о госрегистрации программ для ЭВМ Роспатента** (Сбер, Т-Банк, ВТБ, ЦФТ, BSS, CASHOFF) | `WebFetch` www1.fips.ru/iiss → **403**; `curl`+UA www1.fips.ru → **403, 1 606 б**; `curl`+UA www.fips.ru → **403, 1 606 б**; `r.jina.ai` www1.fips.ru → HTTP 200 прокси, тело = заглушка **DDoS-Guard** («restricted access from your current network»); `r.jina.ai` new.fips.ru → та же заглушка; `curl` searchplatf.rospatent.gov.ru → **HTTP 000** (нет соединения); `r.jina.ai` searchplatf → **HTTP 422**, `"Domain … could not be resolved"` | Участок В.1 закрыт не полностью. Нужен доступ из РФ-сегмента или платный сервис (Онлайн Патент / PatentDB / API Роспатента) |
| **MaPS Financial Fitness Tool — формула и 9 вопросов** | `WebFetch` maps.org.uk → **403**; `r.jina.ai` maps.org.uk → HTTP 200, тело = **антибот-верификация** («Performing security verification») | Б.5 остался на уровне сегментации; формулы FFT нет |
| **CBA–MI Tech Reports № 2, 3, 5** (в т.ч. версия 2 Observed-шкалы и короткая 5-вопросная форма) | `WebFetch` melbourneinstitute.unimelb.edu.au → **403**; `curl`+UA → **403, 5 933–6 002 б**; `r.jina.ai` по «новому» пути `/0010/4752721/` → **страница логина Okta University of Melbourne** | Есть версия 1 обеих шкал целиком (Б.3), версии 2 и короткой формы нет |
| **Economic Record 2022, Comerton-Forde et al.** (журнальная версия) | Wiley Online Library — **пейволл**, не пробовался за пределами поисковой выдачи | Первоисточник добыт в виде Technical Report No. 1, что эквивалентно по содержанию |
| **FinHealth Score, редакция 2026** («From Insight to Impact») | не пробовался — бюджет | Б.1 отражает редакцию 2021 |
| **BBVA Health Score — формула глубже известного** | не добывался в этой сессии | Остаётся на уровне темы 19 (0–100, четыре переменные по 25 %, порог 50, рамка 50/20/30, потолок долга 35 %) |
| **Westpac, Discover, Truist, Fidelity Financial Wellness Score, Prudential, Morgan Stanley** — методики индексов | не добывались (бюджет ушёл на РФ-участок и на полные первоисточники CFPB/CBA-MI) | Пробел блока Б, честно назван |
| **Banco de España — состав индикатора уязвимости (Box 2)** | не открывался, известен только по описанию в поисковой выдаче | Б.6 фиксирует факт существования и характер (секторальный), не состав |
| **CA3162417C (Intuit, «Customized credit card debt reduction plans», выдан в Канаде 2025-03-25)** | найден в выдаче, формула не снималась — бюджет | Единственный найденный документ, где avalanche/snowball могут быть в claims; проверить в следующей теме |
| **Национальные фазы WO2010114732A1 (Bank of America)** | не проверялись отдельным запросом | Остаточный риск для В.1, оценён как низкий (в «Also Published As» только US + WO) |

### Технические ограничения инструментов, замеренные в этой сессии

1. 🔴 **Параметр `&assignee=<имя>` эндпоинта Google Patents `xhr/query` систематически возвращает
   HTTP 503** — 8 запросов подряд (Meniga, Moneythor, Personetics, Nu Pagamentos, Revolut, Plaid,
   Yodlee, MX Technologies), затем 503 пришёл и на простой запрос без `assignee` (то есть
   срабатывает ещё и rate-limit). **Рабочая замена: `&cpc=<класс>` + `&country=<код>` — эти
   параметры отдают 200 стабильно.** Поиск по названным компаниям пришлось вести свободным
   текстом, что слабее.
2. 🔴 **Google Patents слабо индексирует ПОЛНЫЙ ТЕКСТ RU-документов.** Замер: `q=("финансового
   здоровья")&country=RU` → **0**; `q=("персональных финансов")&country=RU` → **1** (нерелевантный);
   тот же корпус через `&cpc=G06Q40/02&country=RU` → **101 документ**. Вывод: по РФ искать
   классами, не фразами.
3. 🟢 **Подтверждён приём «два пути к одному PDF»**: файл CBA–MI Tech Report No. 1 по «новому»
   пути закрыт логином, по «старому» (`/0005/2839433/`) отдан прокси целиком (**200, 82 945 б**).
   Прежде чем записывать PDF недобытым — искать альтернативный путь на том же домене.
4. 🟢 **Подтверждён приём для растровых таблиц внутри PDF**: `pdftotext` по Приложению E отчёта
   CFPB дал только заголовки (`pdfimages -list` показал JPEG 931×134), полная переводная таблица
   40 строк × 4 столбца снята **визуально через `Read` с `pages: 47-48`**.
5. 🟢 **`r.jina.ai` пробил антибот Financial Health Network**: `curl`+UA → **403, 1 635 б**,
   прокси → **200, 14 126 б**. Третий подтверждённый случай после MDPI.
   **Но НЕ пробивает**: DDoS-Guard с геоблокировкой (ФИПС), Okta-логин (unimelb),
   антибот с CAPTCHA (maps.org.uk).

### Расхождение с исходным заданием

🔴 **Задание утверждало: «у НАФИ есть методика индекса финансового здоровья россиян, проверь».
Проверено — такого индекса у НАФИ НЕТ.** Полный перечень восьми индексов НАФИ приведён в Б.7.1.
Это не пробел добычи, а опровергнутая посылка.
🟡 Второе, мельче: статья Известий вышла **15 августа 2024**, а не 14-го.

### Оборвавшийся подагент

Первый (и единственный) запущенный подагент — по российскому массиву ФИПС/Роспатент — **завершился
аварийно**: `rate_limit, HTTP 429, "You've hit your session limit"`, успев дойти до фразы
«Now the ФИПС channel — measuring response codes». Его работа результата не дала; весь российский
участок (А.5) добыт вахтой самостоятельно после сброса лимита. Потолок «не более двух подагентов»
соблюдён: запущен один, второй не запускался.

---

## Метод поиска

### Патентный поиск (блок А)

**Инструмент.** Недокументированный JSON-эндпоинт Google Patents
`https://patents.google.com/xhr/query?url=<urlencoded query>` с браузерным User-Agent
(Chrome/120 macOS). Реквизиты и формулы — `https://patents.google.com/patent/<PUB>/en`
через `curl`+UA (HTTP 200, 380–405 КБ/документ), разбор микроразметки `itemprop=`:
`status`, `assigneeCurrent`, `assigneeOriginal`, `inventor`, `priorityDate`, `filingDate`,
`publicationDate`, секция `<section itemprop="claims">`, блок «Also Published As».

**Классы СПК, по которым вёлся поиск:** **G06Q 40/00** (финансы, общее), **G06Q 40/02**
(банковское дело), **G06Q 40/06** (инвестиции, финансовое планирование),
**G06Q 30/0631** (рекомендации по выбору). Класс **G06Q 10/0637** и **G06Q 20/00**
из задания не использовались — первый про стратегическое планирование предприятия,
второй про платёжную архитектуру, оба заведомо мимо предмета.

**Поисковые запросы — дословно, все 27 (формат `q=…`, к каждому шло `&num=25…50`):**

*Конструкция FINPILOT (11 запросов, из них 8 дали ноль):*
```
("allocation of discretionary income")&country=US                              → 0
("surplus funds" "allocation") ("debt repayment") ("savings goal")             → 0
("discretionary income" "debt repayment" "savings goal")                       → 0
("plurality of candidate allocations") ("debt")                                → 0
("allocation scenarios" "ranking") ("savings" "debt")                          → 0
("weighted sum" "candidate allocation") ("financial")                          → 3  (все не по теме)
("Monte Carlo") ("debt repayment" "emergency fund")                            → 3  (1 релевантный: Intuit)
("debt-to-income ratio" "constraint") ("allocation" "savings goal") ("optimization") → 0
("multi-criteria" "personal finance" "recommendation")                         → 0
("utility score" "allocation" "debt" "savings")                                → 0
("simulating" "plurality of scenarios") ("pay down debt")                      → 0
("highest interest rate" "allocate" "surplus" "emergency savings")             → 0
("discretionary cash flow" "allocation") ("recommendation")                    → 0
("recommended allocation" "percentage") ("debt repayment" "savings")           → 0
("plurality of allocation scenarios")                            → 634 (всё телеком/облака)
("candidate allocations") ("score")                              → 24  (всё телеком/производство)
```
*Скоринг и распределение (6 запросов):*
```
("financial health score")&country=US                            → 54,  просмотрено 30
("financial wellness score")                                     → 23,  просмотрено 20
("financial wellness") ("score") ("weight")&country=US           → 39,  просмотрено 30
("avalanche" "snowball") ("debt")                                → 4,   просмотрено 4
("apportioning" "surplus" "debt" "savings")                      → 17,  просмотрено 17
("cash flow" "allocate" "plurality of goals" "rank")             → 9,   просмотрено 2
("debt-to-income" "threshold") ("recommend" "allocation" "savings") → 16, просмотрено 15
("weighted criteria" "rank" "financial goals" "allocation")      → 1
("allocating" "surplus funds") ("debt" "savings goal")           → 1    (Strands)
("emergency fund" "debt" "allocate" "recommendation" "risk profile") → 1 (Insphire IO)
("financial health") ("Personetics" OR "Meniga" OR "Moneythor" OR "Yodlee" OR "MX Technologies") → 15
```
*Российский массив (8 запросов):*
```
("финансового здоровья")&country=RU                              → 0
("долговой нагрузки" "рекомендаци")&country=RU                   → 0
("персональных финансов")&country=RU                             → 1 (нерелевантный)
(рекомендаци финансов)&country=RU                                → 0
(финансовых)&country=RU&cpc=G06Q40/02                            → 49,  просмотрено 40
(способ)&country=RU&cpc=G06Q40/02                                → 101, просмотрено 50
(способ)&country=RU&cpc=G06Q40/06                                → 42,  просмотрено 42
(способ)&country=RU&cpc=G06Q30/0631                              → 50,  просмотрено 32
(Сбербанк)&country=RU&cpc=G06Q40/00                              → 10,  просмотрено 10 из 10
(Тинькофф)&country=RU                                            → 12,  просмотрено 12 из 12
(накоплени)&country=RU                                           → 1013 (шум: механика, металлургия)
```
*Отбитые по 503 (параметр `assignee`, 8 запросов):* Meniga, Moneythor, Personetics,
Nu Pagamentos, Revolut, Plaid, Yodlee, MX Technologies.

**Объём.** Всего результативных выдач — **31**; просмотрено по заголовкам/реквизитам
**около 330 документов**; полные формулы (claims) сняты у **11 документов**:
US12047359B2, US8412622B2, US20140372340A1, US20190378207A1, US20250315893A1,
US20120059751A1, US12141861B1, US20230252559A1, US20250335982A1, US12229832B2,
US8412622B2 (повторно, полный список 36 claims).

### Методики (блок Б)

**WebSearch — 6 запросов:** `CFPB Financial Well-Being Scale scale development technical report` ·
`Financial Health Network FinHealth Score methodology eight questions` ·
`CommBank Melbourne Institute Financial Wellbeing Scales technical report methodology Comerton-Forde` ·
`OECD INFE 2022 toolkit measuring financial literacy financial well-being score calculation` ·
`MaPS Money and Pensions Service financial wellbeing measurement framework indicators` ·
`НАФИ индекс финансового здоровья россиян методика расчета` ·
`Сбер индекс финансового здоровья методика домены расчет баллы` ·
`Известия 14 августа 2024 индексы финансового здоровья банки Сбер ВТБ` ·
`central bank household financial health index Banco de España financial vulnerability indicator households`
(9 суммарно).

**Добытые полнотекстовые первоисточники — 6:**

| Документ | Канал | Код / объём |
|---|---|---|
| CFPB Technical Report 2017 (51 стр.) | `curl`+UA, зеркало sjdm.org | **200, 794 352 б** → 93 806 симв. + визуальный снимок стр. 47–48 |
| FinHealth Score Toolkit 2021 (11 стр.) | `r.jina.ai` (после 403 у `curl`) | **200, 14 126 б** |
| CBA–MI Tech Report No. 1, Chapters 1–6 (37 стр.) | `r.jina.ai`, «старый» путь | **200, 82 945 б** |
| Страница условий MI Financial Wellbeing Scales | `r.jina.ai` | **200, 5 228 б** |
| OECD/INFE Toolkit 2022 | `curl`+UA | **200, 1 881 374 б** → 126 884 симв. |
| OECD/INFE Toolkit 2026 | `curl`+UA | **200, 2 355 961 б** → 160 759 симв. |
| MaPS Financial Wellbeing Segmentation | `curl`+UA (ukdataservice.ac.uk) | **200, 870 419 б** |
| Известия 15.08.2024 | `WebFetch` | **200** |
| nafi.ru/ratings | `WebFetch` | **200** |

**Проверки-опровержения, выполненные явно:** `grep -i "financial well-being score"` по обеим
редакциям OECD → **0 вхождений в обеих**; `grep -i "©"` по отчёту CFPB → **0 вхождений**;
перечень индексов НАФИ → **индекса финздоровья в списке нет**.

### Что осталось за рамками темы и куда это положить

Три пробела блока Б (банковские индексы США/Австралии, редакция FinHealth 2026, состав
индикатора Banco de España) и один блока А (формула CA3162417C) не закрыты по бюджету,
а не по недоступности — все каналы к ним рабочие. Разумно вынести отдельной короткой темой,
а не догонять внутри темы 20.

---

## ДОБОР Г3 — Г3.1: семья Intuit «Customized credit card debt reduction plans» (2026-09-11)

Канал: `curl -sk --http1.1` с браузерным UA → `https://patents.google.com/patent/<номер>/en`, разбор HTML
(itemprop `claims`, `docdbFamily`, `countryStatus`, `legalEvents`). Сырые HTML — `/private/tmp/g3/*.html`.

| Документ | HTTP | Байт | Статус по Google Patents (legalStatusIfi) |
|---|---|---|---|
| US11544780B2 | 200 | 340 650 | **Active**, выдан 2023-01-03, ожидаемое истечение 2040-07-23 |
| CA3162417C | 200 | 170 576 | **Active**, выдан 2025-03-25, ожидаемое истечение 2041-05-24; пошлина за 4-й год уплачена 2025-05-16 |
| CA3162417A | 404 | 1 449 | такой страницы нет; в семье есть **CA3162417A1** (публикация заявки 2022-01-27) |
| EP4049226A1 | 200 | 263 609 | **Withdrawn** — «Application deemed to be withdrawn», effective 2022-12-13 (запись 2023-05-24); патент НЕ выдан |
| AU2021311376A1 | 200 | 156 608 | **Abandoned** — «MK5 Application lapsed section 142(2)(e) — patent request and compl. specification not accepted» (2024-06-13) |
| WO2022020000A1 | 200 | 267 494 | **Ceased** (PCT-стадия завершена, 2023-01-23) |

**Библиография US11544780B2:** заявка US16/937,400, подача и приоритет 2020-07-23; публикация заявки
US20220027983A1 (2022-01-27); выдача 2023-01-03. Правообладатель — Intuit Inc. Изобретатели — Daniel Ben David,
Yehezkel Shraga Resheff, Yair Horesh, Nirmala Ranganathan. Экспертиза: FINAL REJECTION 2022-03-03 → ответ
2022-05-06 → Advisory action 2022-06-01 → Notice of Allowance 2022-08-31 → PATENTED CASE 2022-12-14.
**CA3162417C:** подача 2021-05-24 (нацфаза PCT/US2021/033871), приоритет 2020-07-23, запрос экспертизы 2022-05-19,
выдача 2025-03-25.

### Семья (DOCDB, блок «Family» Google Patents — одинаков на всех пяти страницах)

CA3162417A1 · CA3162417C · EP4049226A1 · US20220027983A1 · US11544780B2 · AU2021311376A1 · WO2022020000A1.
Страны: **US, CA, EP, AU, WO. Российского (RU) и евразийского (EA) члена нет.**

Проверка тремя путями:
1. DOCDB-семья Google Patents (выше) — RU/EA нет.
2. Правовые события WO2022020000A1 (INPADOC, как их показывает Google Patents), дословно:
   «ENP Entry into the national phase … CA» (2022-05-19); «… EP … Effective date: 20220523» (2022-05-27);
   «… AU … 20210524» (2022-06-09); «NENP Non-entry into the national phase Ref country code: DE» (2023-02-24).
   Вход в нацфазу RU не зарегистрирован; 31-месячный срок для RU от приоритета 2020-07-23 истёк 2023-02-23.
3. Обратный поиск в RU-массиве: `POST searchplatform.rospatent.gov.ru/search`, `ru_since_1994`,
   q = `WO2022020000 OR "2022/020000" OR "US2021/033871" OR "PCT/US2021/033871"` → HTTP 200, 181 байт, **total 0**.
   Ранее (тема 30, §4б) `"Интьюит" OR "ИНТУИТ ИНК" OR "Intuit Inc"` → 1 (Mastercard, упоминание).
   Patentscope (`detail.jsf?docId=WO2022020000&tab=NATIONALPHASE`) → HTTP 200, 41 400 байт, но это оболочка
   без карточки (docId в Patentscope не равен номеру публикации) — канал не дал данных, вывод на нём не строится.

**Итог по действию в РФ:** ни одного члена семьи с действием на территории РФ; EP-ветка отозвана до выдачи
(и EP-патент в РФ не действует в любом случае); действуют только **US11544780B2** и **CA3162417C**.

### Формула — независимые пункты ДОСЛОВНО

**US11544780B2, п. 1** (независимые: 1 — способ, 9 — система с тем же набором операций):
> «1. A method performed by one or more processors of a computer-based debt reduction system and comprising: determining a set of financial attributes and a demographic profile of each of a plurality of consumers, each set of financial attributes indicative of credit card debt associated with a respective consumer of the plurality of consumers; identifying a number of the consumers who successfully repaid credit card debt based at least in part on their respective sets of financial attributes; determining a plurality of debt reduction techniques used by the identified consumers to repay their respective credit card debts; identifying correlations, using a correlation engine including at least one classifier, between at least one of financial attributes of a user and the sets of financial attributes or a demographic profile of the user and the demographic profiles; training a machine learning model, using the correlations, to predict, for each of the debt reduction techniques, a likelihood of the user repaying the credit card debt using the debt reduction technique; predicting, using the trained machine learning model, a likelihood, for each of the debt reduction techniques, that, given the user's financial attributes and demographic profile, the user will successfully repay the credit card debt using the debt reduction technique; identifying, based on the predicted likelihoods, the one of the debt reduction techniques that, if used by the user, is most likely to result in the user successfully repaying the credit card debt; retrieving feedback data representative of whether the user is successfully repaying the credit card debt using the identified debt reduction technique; and retraining the trained machine learning model, using the feedback data, to more accurately predict a likelihood that a given debt reduction technique will result in a given user successfully repaying credit card debt.»

**US11544780B2, п. 9** — «A system comprising: one or more processors; a machine learning model communicatively coupled with the one or more processors; a correlation engine including at least one classifier; and a memory … storing instructions that … cause the system to perform operations including:» — далее операции **слово в слово как в п. 1**.

**CA3162417C, п. 1 и п. 9** — тот же текст с ОДНИМ отличием в независимых пунктах: в операции корреляции
«between at least one of financial attributes of a user and the sets of financial attributes **and** a demographic
profile of the user and the demographic profiles» — у US стоит **«or»**. То есть канадская формула **уже**:
требует корреляции И по финансовым атрибутам, И по демографическому профилю. (В зависимых пп. 2, 3, 8, 10, 11
канадская версия тоже заменяет перечисление «or» на «and».)

**Где avalanche/snowball.** 🔴 **В формуле их НЕТ ни в US, ни в CA** (ни в одном из 20 пунктов). Слова стоят
только в описании: «the debt reduction plans can include any one or more of an avalanche technique (which calls
for paying down credit card debt having the highest APR first), a snowball technique (which calls for paying down
credit card debt having the lowest outstanding balances first), and a fireball technique (which may be a hybrid of
the avalanche and snowball techniques)». Прежняя запись (строка 1281 этого файла и Г3.1 очереди: «где
avalanche/snowball в формуле») — **неверна**: они в описании как примеры «debt reduction techniques».
Зависимый п. 19 — предпочтения пользователя (платить минимум/не более максимума в месяц/в заданный срок)
и взвешивание предсказанных вероятностей по ним.

### Сравнение по признакам с методом FINPILOT (признаки — по §5 `fips_patent_clearance_2026-09-10.md`)

| Признак независимого пункта (US п. 1 / CA п. 1) | У FINPILOT |
|---|---|
| (a) финансовые атрибуты и демографический профиль **множества других потребителей** с кредитно-карточным долгом | **нет** — работаем с данными одного домохозяйства, популяции не собираем |
| (b) выявление потребителей, **успешно погасивших** долг | **нет** |
| (c) определение техник погашения, которыми они пользовались | **нет** (техника у нас одна — Avalanche, задана методом, а не выведена из чужой истории) |
| (d) корреляции через correlation engine **с классификатором** | **нет** |
| (e) **обучение ML-модели** предсказывать вероятность успешного погашения по каждой технике | **нет** (SAW с весами профиля; SES + Монте-Карло — прогноз потока, не классификатор успеха) |
| (f) предсказание вероятности по каждой технике для пользователя | **нет** |
| (g) выбор техники с максимальной вероятностью успеха | **частично по форме** (выбираем лучшую альтернативу), но по иному критерию — взвешенная сумма, не вероятность успеха |
| (h) сбор обратной связи, следует ли пользователь технике | **нет** в методе (канон v3.0.0) |
| (i) **переобучение** модели по обратной связи | **нет** |

Вывод исследователя (не заключение о патентной чистоте): формула **уже, а не шире** метода «перебор вариантов
погашения»: все её признаки завязаны на обучаемую по популяции модель вероятности успеха с обратной связью.
У FINPILOT отсутствуют как минимум (a), (b), (d), (e), (i) — признаки, которые по правилу «все признаки
независимого пункта» исключают совпадение. Плюс территориальное: действует только в US и CA, в РФ членов нет.
Граница вывода: пригодно для США/Канады ТОЛЬКО пока в FINPILOT не появится обучаемая на пользователях модель
выбора стратегии погашения с переобучением по факту исполнения — такой модуль на экспортных рынках надо сверять
с этой формулой заново.


### Г3.1, дополнение — «та же семья идей»: поиск по смежным заявителям и формулировкам (2026-09-11)

Канал: `GET https://patents.google.com/xhr/query?url=<urlencoded>` (внутренний JSON-эндпоинт Google Patents),
`curl -sk --http1.1`, браузерный UA. Все запросы HTTP 200; размер ответа указан.

| # | Запрос (как передан в `url=`) | Байт | Всего | Что в выдаче |
|---|---|---|---|---|
| 1 | `q=("debt avalanche" OR "avalanche method" OR "avalanche technique")&q=(snowball)&q=(debt)` | 6 704 | 3 | CA3162417C (Intuit); **US12524803B1** «Financial autopilot», USAA, выдан 2026-01-13; **US20250335982A1** «System and method for financial health robo-advisor», Wells Fargo, публ. 2025-10-30 |
| 2 | `q=("debt payoff plan" OR "debt repayment plan" OR "debt reduction plan")&assignee=Intuit` | 3 298 | 1 | только US20220027983A1 (та же семья) |
| 3 | `q=("debt payoff" OR "debt repayment")&assignee=Credit Karma` | 140 | **0** | — |
| 4 | `q=("debt payoff" OR "debt repayment" OR "pay down debt")&assignee=Capital One` | 24 759 | 10 | US8538880B1 (debt recovery, 2013); US20230252559A1 и US11023967B1 «Guidance engine»; **US12393978B2 «Systems and methods for debt management with spending recommendation», Capital One Services, выдан 2025-08-19**; US20210358027A1 (визуализация процентов по вариантам платежа); прочее — ML-профилирование |
| 5 | `q=("debt payoff" OR "debt repayment")&assignee=SoFi` | 140 | **0** | — |
| 6 | `q=("debt payoff" OR "debt repayment")&assignee=Chime` | 140 | **0** | — |
| 7 | `q=("debt payoff" OR "debt repayment" OR "credit card")&assignee=Tally` | 7 613 | 3 | шум (Texas Instruments, CN-распознавание лиц) — заявителя «Tally» в индексе Google Patents по этим строкам нет |
| 8 | `q=("highest interest rate first" OR "highest APR first")&q=(debt)` | 18 459 | 6 | US10453125B2 (MX Technologies, transaction-based debt management); CA3162417C; US20250335982A1 (Wells Fargo); US11948195B2 (Ajou University, обучающее устройство по управлению долгом); US11023967B1 (Capital One); US20070112668A1 (Celano) |

Замечания: (1) единственные документы, где «avalanche»+«snowball» встречаются вместе, — семья Intuit,
USAA «Financial autopilot» и заявка Wells Fargo «financial health robo-advisor»; **ни в одном из трёх
avalanche/snowball не вынесены в независимый пункт** (у Intuit проверено дословно выше; у USAA и Wells Fargo
формулы в рамках этого добора не снимались — см. НЕ ДОБЫТО). (2) Отсутствие результатов у Credit Karma,
SoFi, Chime — это отрицательный результат ПО СТРОКЕ запроса и полю `assignee` Google Patents, а не
доказательство отсутствия портфеля (Credit Karma с 2020 принадлежит Intuit, и её документы могут быть
записаны на Intuit). (3) Российских членов ни у одного из перечисленных документов в блоке «Also published as»
не отмечено; отдельная проверка по RU-массиву не проводилась для новых номеров — см. НЕ ДОБЫТО.

---

# ДОБОР Г7 (11.09.2026) — индексы финансового здоровья, методики

> Добор по очереди `docs/research/queue/GAP_QUEUE.md`, раздел «Г7 — Конкуренты, индексы
> здоровья, каналы», пункты 1–4 + российский сосед. Каналы и коды ответа указаны у каждого числа.

## ДОБОР Г7 — FinHealth Score, редакция 2026 («From Insight to Impact») — ✅ ДОБЫТО ДОСЛОВНО

**Реквизиты.** «From Insight to Impact: The Next Phase of Financial Health Measurement.
Updates to the FinHealth Score® and Definitions», Financial Health Network, **март 2026**, 28 стр.
Авторы: Taylor C. Nelms, Meghan Greene (+ методологический вклад: Lisa Berdie, Necati Celik,
Kennan Cepa, Wanjira Chege, Angela Fontes, Shira Hammerslough, Amber Jackson, Andrew Warren).
Финансирование — **Citi Foundation**.

**Канал добычи.** Страница `https://finhealthnetwork.org/research/from-insight-to-impact-the-next-phase-of-financial-health-measurement/`:
`curl -sk`+браузерный UA → **HTTP 403, 1 745 байт** (антибот, тот же класс, что замерен ранее);
`r.jina.ai` по той же странице → **HTTP 200, 111 593 байта**, из тела извлечён прямой адрес PDF.
Сам PDF `https://finhealthnetwork.org/wp-content/uploads/2026/03/From-Insight-to-Impact_-The-Next-Phase-of-Financial-Health-Measurement.pdf`
через `r.jina.ai` → **HTTP 200, 61 306 байт** текста (прокси сам разобрал PDF в markdown,
`Published Time: Tue, 10 Mar 2026 15:20:08 GMT`, `Number of Pages: 28`). Четвёртый
подтверждённый случай «`r.jina.ai` пробил антибот Financial Health Network».

### Что изменилось против редакции 2021

**1. Определение конструкта переписано целиком.** Дословно, Приложение A («Prior Definition» →
«Updated Definition»):

> **Prior:** «Financial health is a composite measurement of an individual's financial life that
> assesses whether people are spending, saving, borrowing, and planning in ways that will enable
> them to be resilient and pursue opportunities. Individuals who are Financially Healthy are able
> to manage their day-to-day expenses, absorb financial shocks, and progress toward meeting their
> long-term financial goals.»

> **Updated:** «Financial health is the state of a household's finances. A Financially Healthy
> household is able to meet current financial needs and obligations, is on track to meet future
> financial needs and obligations, and is able to absorb and recover from unexpected expenses or
> drops in income.»

🔴 Три содержательных сдвига: (а) единица наблюдения сменилась с **индивида на домохозяйство**
(«It centers the household as the unit of analysis»); (б) убраны неизмеримые термины
(«resilient», «pursue opportunities») — дословно: «this way we avoid using terms that themselves
require definitions in our definition of financial health» (сноска 25); (в) определение
разбито на три временны́х среза — настоящее, будущее, шок.

**2. Четвёртый столп переименован: «Plan» → «Plan and Protect».** Дословно: «This includes
updating the name of the fourth pillar of our measurement framework from "Plan" to "Plan and
Protect"». Мотив — «to acknowledge the independent importance of protection via adequate
insurance coverage».

**3. Число столпов и число индикаторов НЕ изменилось: 4 столпа, 8 индикаторов.** Дословно:
«The four-pillar framework remains foundational». Состав:

| Столп | Индикатор |
|---|---|
| Spend | 1. Spending relative to income |
| Spend | 2. On-time bill payment |
| Save | 3. Liquid savings levels |
| Save | 4. Progress on long-term savings goals |
| Borrow | 5. Debt manageability |
| Borrow | 6. Credit score |
| Plan and Protect | 7. Adequacy of insurance coverage |
| Plan and Protect | 8. Planning ahead financially |

**4. Изменены формулировки вопросов и шкалы ответов.** Дословный перечень изменений
(Приложение A, «Changes to the eight indicator questions and corresponding response options»):

> ● Standardizing all items to 5-point response scales with balanced midpoint options.
> ● Simplifying language and changing to active voice to improve readability and reduce cognitive load.
> ● Adding clear timeframes ("Thinking about the last 12 months…") and examples to improve recall and reduce interpretation differences.
> ● On item #2 (on-time bill payment), switching from proportion-based ("pay most bills") to frequency-based ("always/most of the time") response options […]
> ● On item #4 (long-term savings), reframing from an estimate of "confidence in meeting long-term goals" to an estimate of current progress toward long-term savings goals. This reduces optimism bias and is less perceptual and more objective.
> ● On item #5 (debt manageability), restructuring the question into two parts—a simple debt screener followed by a graded manageability question—to clarify confusion around "no debt" responses and ensure a true midpoint.
> ● On item #7 (insurance coverage), revising from "confidence" to "adequacy of protection" using a five-point "how well protected" scale to reduce subjectivity and align with how households assess risk coverage.

🔴 **Для нас прямо применимо два из этих решений.** (а) Вопрос №4 переведён с *уверенности*
на *фактический прогресс* именно «to reduce optimism bias» — это внешнее подтверждение
того, что самооценочный вопрос о целях систематически завышен. (б) Вопрос №5 разбит на
скринер «есть ли долг вообще» + градуированную оценку, потому что «no debt» ломал середину
шкалы — тот же класс проблемы, что у любого показателя долговой нагрузки при нулевом долге.

### Полные тексты восьми вопросов редакции 2026 (Table 1, стр. 14–16), дословно

1. **Spending relative to income:** «Thinking about the last 12 months, how did your household's
   total spending compare to total income (after taxes)?» — 1. Spent much less than income /
   2. Spent a little less / 3. Spent about the same / 4. Spent a little more / 5. Spent much more.
2. **On-time bill payment:** «Thinking about the past 12 months, how often was your household able
   to pay all bills on time? Please include all of the bills your household must regularly pay,
   such as rent or mortgage, utilities, car payments, insurance, and other loan payments.» —
   Always / Most of the time / About half of the time / Less than half of the time / Rarely or never.
3. **Liquid savings levels:** «At your current level of spending, how long could your household
   afford to cover expenses if you had to live only off the money you have readily available,
   without borrowing, selling something, or withdrawing from retirement savings?» —
   6 months or more / 3-5 months / 1-2 months / Less than 1 month but more than 1 week / Less than 1 week.
4. **Progress on long-term savings goals:** «Thinking about your household's long-term savings,
   how would you describe your progress toward meeting your savings goals? Long-term savings
   include money set aside for retirement, education, investments, and saving for a home or other
   major purchase. Do NOT include regular checking accounts, everyday savings, or emergency cash
   in your response.» — Ahead of schedule / About on track / A little behind / Moderately behind / Far behind.
5. **Debt manageability (два вопроса):** (a) «Does your household currently have any debt or
   outstanding loans? Please include mortgage or home equity loans, auto loans, student loans,
   personal loans, medical debt, credit card balances carried over from prior months, past-due or
   unpaid bills, and money owed to other people.» — Yes / No. (b) «Thinking about your household's
   current debt or outstanding loans, how manageable is your household's overall debt right now?» —
   Completely manageable / Mostly / Somewhat / Barely / Not at all manageable.
6. **Credit score:** «Your credit score is a number that tells lenders how risky or safe you are
   as a borrower. How would you rate your credit score?» — Excellent / Very good / Good / Fair /
   Poor / **Don't know** (шестой вариант — единственный индикатор, где есть «не знаю»).
7. **Adequacy of insurance coverage:** «Thinking about all the insurance policies you and others
   in your household might have, how well protected do you feel your household is today in case
   of a major expense or loss? […] Please answer the question to the best of your ability even if
   your household has no insurance.» — Very well protected / Mostly / Somewhat / A little / Not at all.
8. **Planning ahead financially:** «To what extent do you agree or disagree with the following
   statement: "My household plans ahead financially."» — Agree strongly / Agree somewhat /
   Neither agree nor disagree / Disagree somewhat / Disagree strongly.

### 🔴 Ключевое ограничение: формула агрегации в редакции 2026 ЕЩЁ НЕ ОПУБЛИКОВАНА

Дословно, раздел «The Next Phase of Financial Health Measurement»:

> «we expect to roll out the revised FinHealth Score survey and scoring methodology in the 2026
> Financial Health Pulse, to be fielded in **spring 2026**» … «we expect to roll out the refreshed
> Score in the Financial Health Pulse 2026 U.S. Trends Report **before finalizing a new scoring
> rubric, including updated financial health tiers, and publishing a revised user guide** to
> accompany new benchmark data **later in 2026**.»

То есть на 11.09.2026 опубликованы **новые вопросы и шкалы, но не новая рубрика подсчёта
и не новые пороги тиров** (Financially Healthy / Coping / Vulnerable). Старый Score объявлен
действующим: «Current users of the FinHealth Score can rest assured that the original score is
still valid.» **Практический вывод для нас:** редакция 2021, уже записанная в Б.1, остаётся
единственным источником формулы; редакция 2026 меняет содержание вопросов, а не арифметику.

### Что ещё сказано про режим использования и про будущее

- 🔴 **Коммерческая имплементация закрыта эксклюзивным партнёром.** Дословно: «Organizations
  seeking to implement the FinHealth Score® in software or digital products should contact
  **Attune**, the **exclusive technology partner** for FinHealth Score® implementation.» Это
  ужесточение против редакции 2021 (там был просто контакт «schedule a demo»). Для нас:
  **брать FinHealth Score как методику в продукт нельзя без договора с Attune** — знак
  зарегистрирован, канал имплементации назван единственным.
- **Куда движется измерение (три заявленных направления):** (1) уточнение самого опросника
  (кластерный анализ для новых тиров); (2) **гибридная модель «balanced scorecard»** —
  самоотчёт + транзакционные/административные данные; (3) фреймворк измерения воздействия
  (impact measurement).
- **Прецеденты перевода на транзакционные данные, названные в брифе:** ING Netherlands
  «adapted the FinHealth Score framework into a **transactional data scorecard**»; **OCC
  Vital Signs (2024)** — три метрики по транзакционным данным: «**positive cash flow, liquidity
  buffers, and on-time payments**». Последнее прямо релевантно нам: это государственный
  (OCC, США) минимальный набор из трёх наблюдаемых величин, без опроса.
- **Кто ещё использует Score:** J.D. Power встроил методику в свою Financial Health and Advice
  Program; Habitat for Humanity — для оценки эффекта. Тестирование редакции 2026 шло двумя
  вендорами: **J.D. Power** (большая нерепрезентативная выборка клиентов финуслуг) и
  **NORC при Чикагском университете** (split-sample тест на национально репрезентативной выборке).
- Мировой контур: в 2025 **Global Findex Всемирного банка** добавил вопросы про финансовое
  здоровье; ООН назначила спецадвоката по финансовому здоровью (королева Максима, сентябрь 2024).

## ДОБОР Г7 — 🔴 «Карма» БКИ «Скоринг Бюро» (РФ): ближайший сосед на российском рынке — ✅ ДОБЫТО с первоисточника

**Что это.** Трекер финансового здоровья физлица от АО «БКИ СБ» («Скоринг Бюро»,
квалифицированное БКИ, реестр ЦБ № 078–00012–002, Москва, Каланчевская 16 стр. 1).
Запуск объявлен **17 февраля 2026**, презентация в Москве при поддержке фонда «Сколково»
(Sk Финтех Хаб) и Ассоциации развития финансовой грамотности.

**Каналы добычи.** `scoring.ru/karma` → `curl -sk`+UA **HTTP 200, 240 185 байт**;
`scoring.ru/karma-subscription` → **HTTP 200, 177 150 байт**;
`rustore.ru/catalog/app/com.creditbureau.app` → **HTTP 200, 362 878 байт**;
`sk.ru/news/...` → **HTTP 200, 34 423 байта**; `fintech.sk.ru/tpost/kfxl7oxl31-...` →
`WebFetch` **«self signed certificate»**, `curl -sk`+UA → **HTTP 200, 41 487 байт**.
`vedomosti.ru/business/news/2026/02/17/1176966-zdorovya-karma` → **HTTP 200, 207 993 байта**,
но **тело статьи не отрендерено** (JS/пейволл, в HTML только меню и лента новостей) —
цитат из Ведомостей не беру.

### 🔴 Поправка к заданию: компонентов НЕ десять, публично названы ПЯТЬ групп факторов

Задание добора говорило «10 компонентов». **На первоисточнике `scoring.ru/karma`
перечислено пять факторов**, дословно (блок «Как работает?» → «В основе оценки лежат
понятные факторы, отражающие финансовое поведение»):

> Кредитный рейтинг · Налоговые обязательства · Платежи ЖКХ · Штрафы · Банкротства

Та же пятёрка — в описании приложения в RuStore, дословно: «Он анализирует ваши платежи
по кредитам, налогам, ЖКУ, а также информацию о **штрафах и банкротствах**».
Число «10» ни на сайте, ни в сторе, ни в релизах «Сколково» не встречается.
🟡 **Цифра 10, которая в источниках ЕСТЬ** — это «мониторинг событий и рисков по **13
триггерам**» в подписке, и она про уведомления, а не про компоненты индекса.
Полный состав факторов и веса **не публикуются** — формулы в открытом доступе нет
(тот же режим закрытости, что у BBVA Health Score и у скоринговых баллов БКИ вообще).

### Что именно измеряется — и чем это отличается от нас

Дословно с `scoring.ru/karma`:

> «Карма **объективно и независимо** оценивает вашу финансовую дисциплину **за последние 3 года**»

Дословно из сводки Sk/пресс-релиза: «На основе этого формируется многомерный показатель…
**При этом доходы и сбережения не учитываются**».

Дословно, позиционирование от компании (Олег Лагуткин, гендиректор БКИ «Скоринг Бюро»):

> «Это не кредитный рейтинг, не оценка платёжеспособности и не банковский скоринг.
> Это персональный навигатор… Люди активно интересуются своей кредитной историей, но
> кредитный отчёт отражает, прежде всего, отношения клиента с кредитором — а это лишь
> одна составляющая, а не вся картина финансового здоровья в целом».

🔴 **Вывод по конкурентному контуру.** «Карма» — ретроспективный **индекс платёжной
дисциплины по данным БКИ и госисточников** (кредиты, ФНС, ЖКУ, ГИБДД/ФССП, банкротства).
Доходы, расходы, сбережения, цели и свободный денежный поток в него **не входят по
прямому заявлению разработчика**. Это значит: **пересечения по предмету расчёта у нас
с ней нет** — она считает, как человек платил в прошлом, мы распределяем то, что у него
свободно сейчас. Пересечение — **по рынку и по слову «финансовое здоровье»**: она первой
заняла в РФ и термин, и нишу «трекер финансового здоровья для физлица», и заняла её
именем крупного БКИ с доступом к данным, которых у нас нет и не будет.

### 🔴 Поправка к записи добора Г5: базовый продукт БЕСПЛАТНЫЙ, платная — надстройка

Запись «Скоринг Бюро продаёт физлицам трекер финансового здоровья за 299 ₽ первый месяц
и 499 ₽ далее» **неточна и её надо поправить**. По первоисточникам:

- Сам трекер «Карма» — **бесплатный**. Дословно (sk.ru, fintech.sk.ru): «Компания
  представила «Карму» — **бесплатный** цифровой сервис для оценки и улучшения финансового
  здоровья»; заголовок страницы `scoring.ru/karma`: «Карма — **бесплатный** трекер
  финансового здоровья «Скоринг Бюро»».
- Платная — отдельная подписка **«Карма Плюс»**: `scoring.ru/karma-subscription`, дословно
  «**30 дней за 299 ₽. Далее стоимость подписки 499 ₽**», в карточке — «Первые 30 дней
  299 ₽ / Далее 499 ₽/30 дн.». То есть **499 ₽ за 30 дней**, не за календарный месяц.
- Граница free/paid — дословно из FAQ той же страницы: «В бесплатной версии доступны
  **базовые инструменты и общая оценка финансового профиля**. В Карма Плюс появляются
  расширенные данные, мониторинг изменений, защита от мошеннических кредитов и
  рекомендации по улучшению финансового профиля».

**Полный состав подписки «Карма Плюс» (18 пунктов, четыре группы), дословно:**

| Группа | Пункты |
|---|---|
| Профиль | Безлимитные кредитные отчёты · Объяснение рейтинга («какие факторы влияют на рейтинг и что улучшить в первую очередь») · Долговая нагрузка и обязательства («структура обязательств и ближайшие платежи») · Справка о финансовом профиле |
| Контроль | Мониторинг событий и рисков **по 13 триггерам** · Уведомления о новых заявках · Запросы кредитной истории · Изменения рейтинга · Календарь ближайших платежей · Расширенные уведомления по СМС/email |
| Защита | Помощь специалиста в спорных ситуациях · Уведомления о подозрительной активности · Контроль доступа к кредитной истории |
| Улучшение | **Пошаговый план улучшения рейтинга** · **Прогноз изменения рейтинга** («оценим и подскажем, какие действия могут повлиять на рейтинг») · Поиск ошибок в истории · Помощь в составлении обращений · **Рекомендации по снижению нагрузки** («какие обязательства стоит закрыть или пересмотреть первыми») |

🔴 **«Персональные рекомендации» у них — это ровно две вещи, и одна из них наша.**
(1) «Пошаговый план улучшения **рейтинга**» — рекомендации о кредитной истории:
что исправить, какие ошибки оспорить, как поднять балл. (2) 🔴 **«Рекомендации по снижению
нагрузки: узнайте, какие обязательства стоит закрыть или пересмотреть первыми»** — это
**прямой сосед нашей очереди досрочного погашения**. Формально это подсказка о приоритете
закрытия обязательств, то есть тот же класс совета, что даёт наш Avalanche-фильтр. Отличия,
которые видны из описания: у них это (а) рекомендация по данным БКИ, без учёта свободного
денежного потока и резерва, (б) целевая функция — **кредитный рейтинг**, а не стоимость
обслуживания долга и не срок выхода из долга, (в) без расчёта альтернатив распределения.
Дословного текста рекомендаций из приложения не снято (требует авторизации через Госуслуги) —
см. НЕ ДОБЫТО.

Сформулированная ими польза (блок «Когда подписка Плюс особенно полезна»), дословный кейс,
ближайший к нам: «**Хотел взять кредит — сначала проверил шансы.** Посмотрел полную картину
по обязательствам и заранее понял, что стоит улучшить перед подачей заявки» — то есть их
сценарий *перед взятием* кредита, наш — *во время погашения*.

### Трекшн и качество — единственные публичные числа

RuStore, карточка `com.creditbureau.app` (**HTTP 200, 362 878 байт**, снято 11.09.2026):
**70 тыс.+ скачиваний**, рейтинг **4,3** при **258 оценках** и **57 отзывах**, размер 22,7 МБ,
версия **1.86 от 25.08.2026**, минимальная Android 9, возраст 0+, разработчик АО «БКИ СБ»,
поддержка `hotline@scoring.ru`. Отрицательный отзыв (Ольга, 27.07.2026), дословно: «Даёт
ложную информацию, при оспаривании ошибки молчат… Зато хорошо принимают деньги за отчёт».
🟡 Скачивания RuStore — только один стор из трёх (есть ещё Google Play и App Store);
суммарной установочной базы нет.

### Два побочных наблюдения, полезных нам напрямую

1. 🔴 **В подвале `scoring.ru` стоит дословно: «На информационном ресурсе применяются
   рекомендательные технологии»** — это исполнение ст. 10.2-2 149-ФЗ. То есть российский
   игрок нашего класса **публично квалифицировал свои подсказки как рекомендательные
   технологии** и поставил обязательное уведомление. Это прямой прецедент для нашего
   юрблока: спорить о том, «рекомендательная ли у нас технология», ближайший сосед
   не стал.
2. **Заявленные сценарии использования показателя за пределами финансов** (с сайта):
   аренда жилья, наём на работу, выбор няни/сиделки/репетитора, **сайты знакомств**,
   сделки с предоплатой; плюс B2B-контур «в найме Карма позволит проверить уровень
   финансовой надёжности будущих сотрудников». Их модель монетизации смотрит в сторону
   **шеринга показателя третьим лицам** (QR-код и справка), а не только в подписку.
   У нашего продукта такого контура нет, и это осознанная разница, а не пробел.

## ДОБОР Г7 — методики корпоративных индексов финансового здоровья

Сводка по шести названным в очереди организациям. Качество каждой строки помечено отдельно:
🟢 первоисточник открыт · 🟡 вторичный источник или сниппет · ❌ не добыто / опровергнуто.

### 🟢 Fidelity Financial Wellness Score — ДОБЫТО, формула публикуется

**Источник.** Fidelity Plan Sponsor WebStation, «Measuring and predicting financial wellness»,
`https://sponsorcqa.fidelity.com/pspublic/pca/psw/public/library/designbenefits/measuring_predicting_fw.html`
— `WebFetch` **HTTP 200** (страница отдалась, размер инструментом не печатается).

- **Четыре домена**, дословно: «budget, debt, savings/investment, and protection», каждый —
  «**25% each to the overall score, for a total of 100%**».
- **Шкала:** «The sum of all four domains yields a total score from **0 to 100**, where 0
  represents extreme financial distress and 100 indicates the maximum level of financial wellness».
- 🔴 **Ключевая особенность — смешение объективного и субъективного с ФИКСИРОВАННЫМИ весами**,
  дословно: «Overall, the **objective factors are assigned a total weight of 70%** and overall
  **subjective factors are weighted at 30%**». Внутри доменов объективная часть весит **20 %**
  у долга и сбережений/инвестиций и **15 %** у бюджета и защиты; субъективная — дополнение
  до 25 % (соответственно 5 % и 10 %).
- **Тиры** (🟡 из сводки выдачи, на открытой странице не подтверждены): Excellent 80–100,
  Good 60–79, Fair 40–59, Needs Attention 0–39. **Числа тиров считать непроверенными.**
- Число вопросов не публикуется.

**Чем полезно нам.** Это единственная из шести методик, где **веса компонентов названы
числами и опубликованы**, и где явно разведены объективная и субъективная части с заданной
пропорцией 70/30. Наш показатель состояния финансов целиком объективный — это отличие,
которое стоит уметь назвать, а не прятать.

### 🟢 Prudential «Prutection Score» — ДОБЫТО, формула отношения, но НЕ про финздоровье целиком

**Источник.** `https://www.prudential.com/employers/group-insurance/prutection-score`,
`WebFetch` **HTTP 200**.

- **Три риска**, дословно: «(1) premature death, (2) loss of income due to an illness or injury,
  (3) out-of-pocket expenses related to an illness or injury».
- **Формула**, дословно: «For each of these risks, the Prutection Score is the **ratio of Funds
  Available to Funds Needed**». Шкала **1–100**, «with 100 being the most prepared», тиры —
  «Baseline, Moderate, or Strong protection level».
- **Вход «доступно»:** «financial assets, spousal or partner income, investment income, Social
  Security benefits, and insurance benefits». **Вход «нужно»:** «age, marital status, number of
  children, income, essential monthly expenses» + таблицы смертности и госданные.
- 🔴 **Прямое ограничение применимости, заявленное самим Prudential:** результаты применимы
  только к группам и крупным демографиям — «**not to be used at an individual level**».

**Чем полезно нам.** Это не индекс благополучия, а **страховой gap-анализ**: отношение
«есть / надо». Формально это тот же класс, что наш расчёт достаточности резерва, и
оговорка «не для индивидуального уровня» — честное признание точности такой оценки
на одном домохозяйстве. Наш резервный блок считает по факту пользователя, а не по
демографическим таблицам, и в этом он сильнее.

### 🟡 Prudential «Financial Wellbeing Tracker» (Азия) — четыре столпа, формула не публикуется

Дословно из сводки выдачи: четыре столпа — «**Security Now**», «**Security in the Future**»,
«**Financial Freedom Now**», «**Financial Freedom in the Future**», общий индекс «measured out
of 100 points». Значения по возрасту (Prudential, исследование по Азии, публикация 05.03.2026):
**59,8 из 100** у 18–35 лет, **57,7** у 50–60 лет — то есть у Prudential благополучие
**снижается с возрастом**. 🟡 Первоисточник не открыт: `malaymail.com/.../452552` →
`WebFetch` **HTTP 403 Forbidden**; страница Prudential HK в выдаче есть, но не открывалась
(бюджет). Числа считать вторичными.

### 🔴❌ «Westpac Financial Health Index» — ПОСЫЛКА ОЧЕРЕДИ НЕ ПОДТВЕРЖДЕНА

Три поиска не дали ни одного документа с таким названием. У Westpac есть **Westpac–Melbourne
Institute Leading Index** и **Westpac Consumer Sentiment Index** — это **макроэкономические
индикаторы делового цикла и потребительских настроений**, а не индексы финансового здоровья
домохозяйства. Австралийский банковский индекс финансового благополучия, который, судя по
описанию, имелся в виду, — это **ANZ Roy Morgan Financial Wellbeing Indicator (FWBI)**,
и он добыт целиком (ниже). Это опровергнутая посылка, а не пробел добычи — тот же класс
ошибки, что «индекс НАФИ» в исходном задании.

### 🟢 ANZ Roy Morgan Financial Wellbeing Indicator (FWBI) — ДОБЫТО с техническим приложением

**Источник.** «ANZ Roy Morgan Financial Wellbeing Indicator, Quarterly Update: March 2023»,
`https://www.anz.com.au/content/dam/anzcomau/about-us/anz-financial-wellbeing-indicator-march-2023.pdf`
→ `curl -sk`+UA **HTTP 200, 649 075 байт**; `pdftotext -layout` → 49 855 символов.

- **Три компонента**: **Meeting commitments** · **Feeling comfortable** · **Resilience (for the
  future)**. Каждый — балл из 100; общий балл — их среднее (по описанию методики: «added
  together and divided by three»).
- 🔴 **Но в квартальном индикаторе это НЕ простое среднее.** Дословно, Technical Appendix:
  «The indicator is calculated by an **algorithm that transforms responses to these questions,
  weighing the relative importance of each component**. The algorithm was developed based on
  calibrated responses to the financial wellbeing questions in the **2017 and 2021 ANZ Financial
  Wellbeing Surveys**». То есть веса откалиброваны по отдельным волнам обследования и
  **сами по себе не опубликованы**.
- **Состав вопросов (дословно, Technical Appendix):**
  - *Meeting commitments:* «Meeting my bills and commitments is a struggle from time to time»;
    «In the past 12 months I have sometimes been unable to pay bills or loan commitments at the
    final reminder due to lack of money»; «I sometimes run short of money for food or other
    regular expenses».
  - *Feeling comfortable:* «I feel financially stable at the moment»; «I have planned enough to
    make sure I will be financially secure in the future»; «Would you say you and your family are
    better-off financially – or worse-off than you were at this time last year?»; «Looking ahead
    to this time next year…».
  - *Resilience:* **два расчётных показателя, не мнения** — (1) «Number of months' income in
    savings», считается из дохода домохозяйства до налогов и остатков на счетах; (2) «Managing
    a drop in income **by a third**», считается из дохода, остатков на счетах и
    **недельных расходов на всё хозяйство**.
- **Замеренные уровни (12-месячное скользящее, декабрь 2022):** общий индекс **54,2 из 100**
  (спот-минимум после COVID; сентябрь 2022 — 56,5); **Meeting commitments 69,3**;
  **Resilience for the future 52,3**; разброс по штатам — от **54,6** (минимум) до
  «+5,1 пункта к среднему по стране» (максимум).

🔴 **Прямо применимо к нам.** Третий компонент ANZ — «сколько месяцев дохода в сбережениях»
и «переживёт ли домохозяйство падение дохода на треть» — это **ровно та величина, которую
считает наш резервный блок**, и считается она у ANZ из тех же трёх входов (доход, остатки,
расходы). Внешнее подтверждение, что резерв в месяцах расходов/дохода — не наша выдумка,
а компонент национального индикатора крупного банка.

### 🟡 Morgan Stanley at Work Financial Wellness — только объём, не формула

По сводке выдачи: программа включает «a **12-question** financial assessment and score to
determine financial fitness» плюс «80+ articles». Состава вопросов, весов и шкалы в открытом
доступе не найдено; портал закрыт корпоративным доступом. ❌ Методика **не добыта**;
единственное надёжное — порядок величины опросника (12 вопросов против 8 у FinHealth Score).

### ❌ Discover и Truist — методик не найдено, причина точная

- **Discover.** Три поисковых прохода выводят либо на сторонние скоринг-приложения
  (`myfinancialwellnessscore.scoreapp.com` — не Discover), либо на общие обзоры. Собственного
  опубликованного «Discover Financial Wellness Score» с методикой в выдаче нет.
  **Не добыто; вероятно, посылка очереди неточна так же, как с Westpac.**
- **Truist.** Выдача даёт **Truist Confidence Account** — это счёт второго шанса
  (second-chance checking) с бесплатным финобразованием, оповещениями и кредитным
  мониторингом, **а не индекс**. Публичной методики «Truist financial confidence score»
  не найдено. **Не добыто.**

### 🟢 Banco de España, Box 2 — состав индикатора уязвимости ДОБЫТ ПОЛНОСТЬЮ

**Источник.** «Box 2. A composite indicator of aggregate household financial vulnerability»,
авторы **Fernando Nieto и Javier Martín**, в «Report on the Financial Situation of Households
and Firms, Second Half of 2024», стр. 34. Канал: `curl -sk`+UA по
`https://www.bde.es/f/webbe/SES/Secciones/Publicaciones/Informesituacionfinancierafamiliasyempresas/2024/S2/Files/SituacionFinanciera_Box2_022024.pdf`
→ **HTTP 200, 249 131 байт**; `pdftotext -layout` → 16 688 символов.

**Устройство — дословно:** индикатор «is constructed as the **arithmetic mean of the following
five sub-indicators**», следуя подходу ЕЦБ:

| № | Субиндикатор | Из чего считается (дословно) |
|---|---|---|
| 1 | **Debt servicing capacity** | «gross interest payments-to-income ratio, the saving ratio and expectations of personal financial situation over the next 12 months» |
| 2 | **Leverage** | «households' gross debt-to-income and gross debt-to-total assets ratios» |
| 3 | **Financing** | «the interest rate on households' outstanding amount of bank loans and the **credit impulse**, measured as the annual change in net credit flows as a share of GDP» |
| 4 | **Income** | «households' real income growth and the income-to-GDP ratio» |
| 5 | **Labour activity** | «the labour force participation rate and unemployment expectations» |

**Агрегация — дословно:** «Each of these sub-indicators is, in turn, a **simple arithmetic mean
of the individual indicators**. Each indicator is first **standardised against a reference
period** … converted into a common scale with a **mean of zero and a standard deviation of one**.
Therefore, the value of each indicator is a **z-score** … All variables are included with a sign
whereby **positive (negative) values can be interpreted as a higher (lower) degree of
vulnerability**». Референсный период — **2005 Q1 – 2024/2025 Q4** (в версии S2-2024 — 2005–2024).

**Оговорки и расхождения с ЕЦБ, названные авторами дословно:** «Strictly speaking, the debt
burden **should include principal repayments**» (то есть в знаменателе только проценты — это
признанное упрощение); «Unlike the ECB indicator, the short-term debt-to-long-term debt ratio
and the current financial assets-to-current liabilities ratio are **not included**, since in
Spain's case these variables are influenced by pension advances».

**Замеренные свойства (те же страницы):** корреляция индикатора с ростом ВВП **−0,6**
одновременно и **−0,7** с лагом в три квартала; с потребительской уверенностью **0,6**;
с качеством кредитного портфеля банков **0,8** одновременно. В 2024 Q3 индикатор был
«very close to 20-year lows» и в Испании, и в еврозоне.

🔴 **Два урока, прямо ложащихся на нашу матмодель.** (1) **Агрегация — равновзвешенное среднее
z-оценок, а не веса экспертов.** Центральный банк с полным доступом к данным выбрал самую
простую свёртку и явно об этом пишет — это аргумент того же класса, что «простая сумма ≈ IRT»
у CBA–MI, и он поддерживает нашу SAW-свёртку. (2) **Индикатор относительный, а не абсолютный:**
он меряет отклонение от среднего за референсный период, а не «хорошо/плохо» само по себе.
Любой показатель состояния финансов, построенный на z-оценках, теряет смысл без явно
названной базы сравнения.

### 🔴 Economic Record 2022, Comerton-Forde et al. — расхождение с нашей записью НАЙДЕНО

**Что добыто.** Журнальная версия за пейволлом Wiley (`r.jina.ai` по
`onlinelibrary.wiley.com/doi/abs/10.1111/1475-4932.12664` → **HTTP 200, 519 байт**, тело =
антибот-заглушка «Performing security verification» — прокси антибот Wiley НЕ пробил).
Реквизиты сняты через **OpenAlex API** (`api.openalex.org/works/doi:10.1111/1475-4932.12664`
→ **HTTP 200, 21 069 байт**): заголовок «**Measuring Financial Wellbeing with Self-Reported
and Bank-Record Data**», **том 98, выпуск 321, стр. 133–151**, `is_oa: true`, `oa_status:
hybrid`. Полный текст взят из депонированной версии **IZA Discussion Paper No. 13884,
ноябрь 2020** (`https://docs.iza.org/dp13884.pdf` → `curl -sk`+UA **HTTP 200, 1 930 633 байта**;
`pdftotext -layout` → 184 918 символов). Авторы: Carole Comerton-Forde (UNSW), John de New
(Melbourne Institute), Nicolás Salamanca (Melbourne Institute, IZA), David C. Ribar
(Georgia State, IZA), Andrea Nicastro (CBA), James Ross (CBA).

**🔴 Числа НЕ совпадают с тем, что записано в Б.3 по Technical Report № 1:**

| Величина | Записано у нас (Tech Report № 1) | IZA DP 13884 / журнальная версия |
|---|---|---|
| Корреляция Reported и Observed шкал | Spearman **ρ = 40 %** | **«a Spearman rank correlation of 46 per cent»** (повторено дважды) |
| Множитель Observed-шкалы | **100/9** (максимум суммы 9) | **100/19**, дословно: «multiplying the sum by **100/19** to produce a 0-100 scale with **20 possible outcomes**» |

То есть **Observed Financial Wellbeing Scale в журнальной версии другая** — с бо́льшим числом
градаций (20 исходов против 10) при тех же пяти пунктах банковской записи. Это ровно то,
что в разделе «Что не добыто» называлось «версия 2 Observed-шкалы»: она существует и она
здесь. Reported-шкала осталась **10-вопросной**.

**Числа надёжности, которых у нас не было (IZA DP 13884, дословно):**
- «The summative reported scale is correlated **99.2 percent** with the IRT empirical Bayes mean
  prediction, and the summative observed scale is correlated **98.0 percent** with the IRT
  empirical Bayes mean prediction.»
- «Cronbach's alpha coefficients of **0.92** (reported) and **0.85** (observed).»
- Средний балл Observed-шкалы в выборке — **54,0**, медиана **57,9**.

🔴 **Это усиливает главный аргумент раздела Б.3, а не ослабляет его:** простое суммирование
категориальных ответов воспроизводит полноценную IRT-модель с точностью **98–99 %**.
Для нас это прямое основание не усложнять свёртку показателя состояния финансов.
Одновременно — **правку в Б.3 надо внести**: ρ = 46 %, множитель 100/19, 20 исходов;
записанные там 40 % и 100/9 относятся к более ранней редакции Technical Report № 1
и в журнальной версии не действуют.

---

# ИТОГ ДОБОРА Г7 (11.09.2026)

Батч Г7 очереди `docs/research/queue/GAP_QUEUE.md` — «Конкуренты, индексы финансового
здоровья, каналы», 12 пунктов. Вахта работала одна, подагенты не запускались
(потолок «не более двух» соблюдён с запасом).

## Постатейно

| № | Пункт очереди | Статус | Где раздел |
|---|---|---|---|
| 1 | FinHealth Score, редакция 2026 | ✅ **добыт дословно** (28 стр., все 8 вопросов, весь перечень изменений) | `bank_patents_wellness_scoring`, «ДОБОР Г7 — FinHealth Score, редакция 2026» |
| 2 | Методики Westpac, Discover, Truist, Fidelity, Prudential, Morgan Stanley | 🟡 **частично: 2 из 6 с формулами** (Fidelity, Prudential Prutection), Westpac — посылка опровергнута и заменена на ANZ FWBI (добыт целиком), Morgan Stanley — только объём опросника, Discover и Truist — не найдены | там же, «методики корпоративных индексов» |
| 3 | Banco de España, Box 2 | ✅ **добыт полностью** (5 субиндикаторов, формула, оговорки, корреляции) | там же |
| 4 | Economic Record 2022, Comerton-Forde et al. | ✅ **добыт через IZA DP 13884 + OpenAlex**; 🔴 **найдено расхождение с нашей записью** | там же |
| 4а | Методика «Кармы» Скоринг Бюро (сверх очереди) | ✅ **добыт с первоисточника**; 🔴 две поправки к записи Г5 | там же, «Карма» |
| 5 | CAC MoneyLion, Acorns, Intuit/Credit Karma | 🟡 **MoneyLion — точно ($9/$16, 8-K SEC); Acorns — косвенно (LTV и LTV:CAC); Intuit — CAC не существует как метрика** | `competitor_marketing_positioning`, «ДОБОР Г7.2» |
| 6 | Starling round-ups, первоисточник | ✅ **добыт** (с `starlingbank.com`, причина недоступности `help.` установлена) | `banks_apac_neobanks`, «ДОБОР Г7.3» |
| 7 | KakaoBank: IR и механики | ✅ **IR добыт целиком через API сайта**; блог про теги не искался | там же |
| 8 | CPA-ставки банков и брокеров РФ | 🟡 **розничные ставки банки не раскрывают публично** (установлено, а не предположено); B2B-ставки добыты вторично; брокеры — реферальные подарки, не CPA | `telegram_channel`, «ДОБОР Г7.4» |
| 8а | Перечень РКН 10 000+ и Telegram (сверх очереди) | 🟡 регистрация каналов идёт, санкция описана; 🔴 **найден налоговый запрет на признание расхода** | там же |
| 9 | Статья Финуслуг про ипотеку и вклад | ✅ **добыта дословно**, но это **другая, переписанная статья 2026 года** с полным расчётом | `marketplaces_ds_practice_rf`, «ДОБОР Г7.5» |
| 10 | Data Fest 2024/2025/2026, Aha!, PyCon | 🟡 **Data Fest 2024 и 2025 проверены** (официальный список 34 секций); Aha! и PyCon не проверялись | там же |
| 11 | Практика по 211-ФЗ, письма ЦБ | ❌ **не добыто** (нет в открытых источниках); 🔴 закрыто с другой стороны — разграничением Финуслуг | там же |
| 12 | Хабр о «Финздоровье» | ✅ **добыт дословно**; 🔴 **это Т-Банк, а не Сбер** | там же |

**Счёт:** полностью закрыто **7 пунктов**, частично **4**, отрицательный результат с
точной причиной **1**. Плюс два пункта сверх очереди («Карма» и налоговый режим рекламы).

## 🔴 Что из добытого меняет картину конкуренции и позиционирования

1. 🔴 **Российских соседей с продуктом «финансовое здоровье» не один, а минимум три, и все
   крупнее нас.** (а) **«Карма» Скоринг Бюро** — бесплатный трекер + подписка «Карма Плюс»
   299 ₽/499 ₽ за 30 дней, 70 тыс.+ установок только в RuStore, за ним крупное БКИ.
   (б) **«Финздоровье» Т-Банка** — с августа 2024, пять параметров, внутри крупнейшего
   розничного банка. (в) **«Финансовое Здоровье» Финуслуг** (Московская биржа) — найдено
   в навигации, содержание ещё не снято. Формулировка «в РФ такого нет» больше не работает
   ни в каком виде; работать надо на различии предмета расчёта.
2. 🔴 **Поправка к записи добора Г5: «Карма» — БЕСПЛАТНАЯ, платная только надстройка.**
   299 ₽/499 ₽ — это подписка «Карма Плюс» (мониторинг, защита от мошеннических кредитов,
   безлимитные отчёты), а сам трекер и оценка бесплатны. И **компонентов не 10, а пять
   публично названных групп** (кредитный рейтинг, налоги, ЖКХ, штрафы, банкротства);
   число 13 в источниках есть, но это триггеры уведомлений.
3. 🔴 **Но предмет расчёта у «Кармы» другой, и это наша защита.** Прямое заявление
   разработчика: «доходы и сбережения не учитываются». Она меряет **платёжную дисциплину
   за 3 года по данным БКИ и госисточников**. Единственное пересечение — пункт подписки
   «Рекомендации по снижению нагрузки: какие обязательства стоит закрыть или пересмотреть
   первыми», и целевая функция там — **кредитный рейтинг**, а не стоимость обслуживания
   долга и не срок выхода из долга.
4. 🔴 **Т-Банк ещё в августе 2024 публично заявил план построить ровно наш продукт** —
   «планирование будущего финансового состояния… предсказать будущие расходы, составить
   реалистичный бюджет на следующий месяц, а также **запланировать финансовые цели и план
   по их достижению**» на сервисе ETNA. Реализовано это или нет — не проверено. Новизну
   надо формулировать не через «такого нет», а через «что устроено иначе»: распределение
   свободного потока между конкурирующими назначениями с объяснением выбора.
5. 🔴 **Бесплатный массовый контент уже отвечает на наш главный вопрос, и отвечает хорошо.**
   Статья Финуслуг от 18.08.2026 даёт точку равновесия «ипотека против вклада» с поправкой
   на НДФЛ (**14,5 % без налога, 12,6 % с налогом**), таблицу экономии по пяти ставкам,
   три сценария на живом примере и честное предупреждение, что 1,12 млн ₽ и 72 500 ₽
   сравнивать напрямую некорректно. Наше преимущество — не логика (она совпадает), а
   персонализация, охват всех долгов сразу и пересчёт при изменении входов.
6. 🔴 **Позиционирование «наш индекс — объективный» получило внешнюю опору.** Fidelity
   смешивает объективное и субъективное в пропорции **70/30**; FinHealth Score целиком
   самоотчётный и в редакции 2026 специально переписывает вопросы, чтобы **снизить
   оптимистическое смещение**; Т-Банк выдаёт запас прочности словами («меньше месяца /
   один-два / полгода и больше»). Наш показатель считается из фактических чисел
   пользователя — это осмысленное отличие, а не придирка.
7. 🔴 **Простая свёртка подтверждена ещё двумя независимыми источниками.** Banco de España
   (вслед за ЕЦБ) агрегирует пять субиндикаторов **равновзвешенным средним z-оценок**;
   Comerton-Forde et al. в журнальной версии: простая сумма коррелирует с полной
   IRT-моделью на **99,2 % (Reported)** и **98,0 % (Observed)**, α = 0,92 и 0,85.
   Аргумент за нашу SAW-свёртку усилен.
8. 🔴 **Правка, которую надо внести в Б.3 этого файла:** корреляция Reported и Observed
   шкал — **46 %**, а не 40 %; множитель Observed-шкалы — **100/19 при 20 исходах**,
   а не 100/9. Записанные значения относятся к Technical Report № 1; журнальная версия
   (Economic Record 98(321):133–151) даёт другие.
9. 🔴 **FinHealth Score нельзя взять в продукт без договора.** Редакция 2026 прямо
   называет **Attune** «the exclusive technology partner for FinHealth Score®
   implementation». Знак зарегистрирован, канал имплементации — единственный.
10. 🔴 **KakaoBank оказался не тем, чем считался.** По первоисточнику IR за 2Q26
    платформенная выручка — **25,3 из 829,0 млрд вон (≈3 %)** при процентной **83 %**,
    и расходы «Fee & Platform» (52,5) **вдвое больше** платформенной выручки. Три четверти
    платформенных денег — **сравнение кредитов (34 %) и реклама (31 %)**, то есть модель
    Credit Karma. Тезис «неободанк зарабатывает на платформе» в этом примере не
    подтверждается.
11. 🔴 **Против платного Telegram появился третий, финансовый довод.** По п. 44 ст. 270
    НК РФ расходы на рекламу на ресурсе иностранного лица, не исполнившего 236-ФЗ,
    **не уменьшают налог на прибыль**; Telegram Messenger, Inc. исполнил две обязанности
    из трёх («филиал/представительство» — «В стадии согласования»). Цепочка: письма
    Минфина 11.12.2024 № 03-03-06/1/125078 и 27.05.2025 № 03-03-06/3/51670 → письмо
    РКН 20.02.2025 № 03-72707 → письмо ФНС 27.02.2025 № СД-4-3/2042@. **Проверить
    проекцию на УСН отдельно.**
12. 🔴 **Разграничение по 211-ФЗ можно не выводить, а скопировать.** Финуслуги развели
    один сайт на две правовые зоны через **два юрлица**: сделки — ПАО «Московская Биржа»
    (оператор финансовой платформы, в реестре ЦБ с 27.08.2020, метка «Открытие онлайн на
    Финуслугах»), всё остальное — ООО «МБ Маркетплейс», **не оператор платформы**.
    Наш продукт целиком во второй зоне.
13. 🔴 **И ещё один прецедент, снимающий спор в юрблоке:** в подвале `scoring.ru` стоит
    «На информационном ресурсе применяются рекомендательные технологии» — ближайший
    российский сосед сам квалифицировал свои подсказки по ст. 10.2-2 149-ФЗ и поставил
    уведомление, спорить об этом не стал.
14. **Три опровергнутые посылки очереди** (не пробелы добычи): «Westpac Financial Health
    Index» — не существует, имелся в виду ANZ Roy Morgan FWBI; «Хабр о «Финздоровье»
    **Сбера**» — это Т-Банк; «10 компонентов Кармы» — публично названы пять групп.
    Это третий подряд добор, где часть задания оказалась неверной посылкой (ср. «индекс
    НАФИ» в исходном задании темы).
15. **Ориентиры юнит-экономики, которые теперь есть в цифрах:** CAC $9 (MoneyLion, fully
    loaded, включая бренд), CAC ≈$20–$71 (Acorns, производно), отток **1,3 %/мес**
    (Acorns), целевая доля S&M в выручке **40 %** (долгосрочная модель Acorns) против
    ~70 % (NerdWallet). Прямого переноса на РФ нет; переносима структура.

## Что осталось неизвестным после Г7

- Методики **Discover** и **Truist** — не найдены ни одним запросом; вероятно, посылка
  очереди неточна, как с Westpac.
- **Morgan Stanley at Work** — известен только объём (12 вопросов), формула закрыта
  корпоративным доступом.
- **Journal-версия Economic Record** за пейволлом Wiley (`r.jina.ai` → 200, но 519 байт
  антибот-заглушки); содержание взято из депонированной IZA-версии.
- **Prudential Financial Wellbeing Tracker** (Азия) — четыре столпа известны, формула нет;
  `malaymail` → 403.
- **Розничные CPA-ставки банков РФ и рублёвые CPA брокеров** — публично не раскрываются
  (повторный отрицательный результат).
- **Судебная и надзорная практика по 211-ФЗ, письма ЦБ** — в открытых источниках нет.
- **Письма ФНС о моменте признания дохода по Telegram Stars** — не существует;
  есть только экспертное мнение про момент конвертации в TON.
- **Дословный текст ТАСС** о регистрации Telegram-канала в перечне РКН — `WebFetch` 403.
- **Программы Aha! и PyCon Russia** — не проверялись, бюджет.
- **Блог KakaoBank про теги и заметки** — не искался; в английской IR-презентации 2Q26
  PFM как продукт не упоминается вовсе.
- **Сервис «Финансовое Здоровье» Финуслуг** — найден в навигации, содержание и цена не сняты.
- **Проекция п. 44 ст. 270 НК РФ на УСН «доходы минус расходы»** — не проверялась.


## ДОБОР Г15 — Г15.1(а): US12524803B1, USAA, «Financial autopilot» (2026-09-12)

Канал: `curl -sk --http1.1` с браузерным UA → `https://patents.google.com/patent/US12524803B1/en` → **HTTP 200, 202 629 байт**;
разбор HTML (itemprop `claims`, `description`, `applications`, `docdbFamily`, `legalEvents`). Сырой HTML —
`/private/tmp/g15/US12524803B1.html`. Проверка содержимого: формула 20 пунктов, 13 470 байт секции `claims`.

**Библиография.** Заявка US18/912,285, подана 2024-10-10; приоритет 2018-09-28 (провизорная US62/738,544);
выдан **2026-01-13**; правовое событие «STCF … PATENTED CASE» 2025-12-30; статус Google Patents — **Active**.
Правообладатель — United Services Automobile Association (USAA). Изобретатели — Nathan Mahoney, Luis Daniel Silva,
Gunjan C. Vijayvergia, Jason Paul Hendry. Continuation от US18/393,397 (US12141861B1).

**Семья (блок applications / docdbFamily Google Patents), все — «Financial autopilot», приоритет 2018-09-28:**
US16/585,519 → **US11127075B1** (выдан 2021-09-21, Active) · US17/410,473 → **US11861694B1** (выдан 2024-01-02,
Active, расч. истечение 2040-03-31) · US18/393,397 → **US12141861B1** (выдан 2024-11-12, Active) ·
US18/912,285 → **US12524803B1** (2026-01-13, Active). Страны: **только US**. RU/EA/WO/EP членов нет.

**Независимые пункты — 1 (способ), 8 (носитель), 15 (система); тексты операций совпадают. П. 1 дословно:**
> «1. A method implemented by a data processing system, comprising: receiving training data including (i) transaction histories of a plurality of users during a specific period of time, and (ii) for each of the plurality of users, data specifying expenses that occurred to the respective user during the specific period of time; training a neural network to predict an expense for a given transaction history using a supervised learning technique based on the training data, wherein the neural network is configured to receive as input the given transaction history and to process the input to generate an output that specifies a specified expense for the given transaction history, wherein the neural network comprises a plurality of artificial neurons that are connected through edges and are aggregated into a plurality of neural network layers comprising at least an input layer and an output layer, wherein each of the edges is configured to transmit a signal from one artificial neuron to another artificial neuron, and wherein an output of each of the plurality of artificial neurons is computed based on inputs of the artificial neuron in accordance with a plurality of weights; setting values of the plurality of weights based on the training of the neural network; and storing, in a hardware storage device, the trained neural network with the set values of the plurality of weights.»

П. 8 — «A non-transitory computer storage medium encoded with computer program instructions that when executed by one or
more computers cause the one or more computers to perform operations comprising:» + операции п. 1 слово в слово.
П. 15 — «A system comprising: one or more computers and one or more storage devices storing instructions that are
operable, when executed by the one or more computers, to cause the one or more computers to perform operations
comprising:» + те же операции.

**Где avalanche/snowball.** Счёт по тексту формулы (все 20 пунктов): avalanche **0**, snowball **0**, interest rate 0,
savings 0, goal 0, emergency 0; «neural» — 26. **В формуле их нет; только в описании**, одно место, дословно:
> «…the user can approve or modify the algorithmically suggested amount to be paid above the minimum payment and the system 100 will offer multiple debt reduction automation options. Examples, of algorithms include: debt snowball (highest interest paid off first), debt avalanche (lowest balance paid first) or a custom option all to be automatically paid according to a pre-agreed upon plan with the user.” In some implementations, the mathematical algorithm used includes to following: disposable income=income−(recurring transaction cashflow+debt re-payment+savings t…»

🔴 Побочно: в описании USAA **определения перепутаны** — «snowball» назван «highest interest paid off first»,
«avalanche» — «lowest balance paid first» (в общепринятом словаре наоборот). Для формулы значения не имеет —
слова в неё не вынесены.

**Сравнение по признакам с методом FINPILOT (признаки — §5 `fips_patent_clearance_2026-09-10.md`):**

| Признак независимого пункта US12524803B1 | У FINPILOT |
|---|---|
| (a) получение обучающих данных: истории транзакций **множества пользователей** за период + их расходы | **нет** — одно домохозяйство, популяции не собираем |
| (b) **обучение нейронной сети** с учителем предсказывать расход по истории транзакций | **нет** — SES + Монте-Карло, без обучаемых моделей |
| (c) структура сети: нейроны, рёбра, слои, веса | **нет** |
| (d) установка весов по итогам обучения | **нет** |
| (e) хранение обученной сети в аппаратном хранилище | **нет** |

Вывод исследователя (не заключение о патентной чистоте): независимые пункты US12524803B1 — это **обучение
нейросети предсказанию расходов** по популяции; распределения денег, долгов, погашения в них нет вовсе.
У FINPILOT отсутствуют все пять признаков. Формула **уже**, а не шире «перебора вариантов погашения».
Формулы трёх родительских патентов семьи разобраны ниже (Г15.1(в)), потому что в continuation-семье
широкий пункт мог остаться у родителя.

**Российский член.** DOCDB-семья — только US. Обратный поиск по RU-массиву (`POST searchplatform.rospatent.gov.ru/search`,
`ru_since_1994`): q = `"USAA" OR "United Services Automobile Association" OR "Юнайтед Сервисез Аутомобиль"` →
HTTP 200, 23 991 байт, total 2 — оба мимо (RU2670030C2 Яндекс; RU2644245C2 фармацевтика, KR), совпадение по
полному тексту, не заявитель. q = `US12524803 OR US11127075 OR US12393978 OR US11532041 OR US12361480 OR US20250335982` →
HTTP 200, 182 байта, **total 0**. **Российского и евразийского члена нет.**


## ДОБОР Г15 — Г15.2: US12393978B2, Capital One, «Systems and methods for debt management with spending recommendation» (2026-09-12)

Канал: `curl -sk --http1.1` → `https://patents.google.com/patent/US12393978B2/en` → **HTTP 200, 209 247 байт**;
секция `claims` 15 840 байт, 20 пунктов. Сырой HTML — `/private/tmp/g15/US12393978B2.html`.

**Библиография.** Заявка US18/394,321, подана 2023-12-22; приоритет **2020-07-08**; публикация заявки US20240127329A1
(2024-04-18); Notice of Allowance 2025-05-01; пошлина за выдачу 2025-07-30; PATENTED CASE 2025-08-06; выдан **2025-08-19**;
расчётное истечение **2040-08-09**; статус **Active**. Правообладатель — Capital One Services, LLC (Virginia); изобретатели —
Austin Walters, Vincent Pham, Jeremy Goodsitt (переуступка, reel/frame 065943/0517, effective 2020-07-08).
Continuation от US18/057,522 (US11893630B2).

**Семья (все — то же название, приоритет 2020-07-08):** US16/923,405 → US20220012803A1 → **US11532041B2**
(выдан 2022-12-20, Active, истечение 2040-09-03) · US18/057,522 → US20230093371A1 → **US11893630B2** (выдан 2024-02-06,
Active, истечение 2040-07-08) · US18/394,321 → US20240127329A1 → **US12393978B2**. Страны: **только US**.

**Независимые пункты — 1 (способ), 11 (система), 20 (способ). П. 1 дословно:**
> «1. A computer-implemented method for providing an adaptive goal management recommendation, the method comprising: receiving, by one or more processors, account information regarding a user; receiving, by the one or more processors and a chat bot feature of an interface of a user device, a query from the user, the query representing text or user voice data; in response to the query, presenting, by the one or more processors and the chat bot feature, a portion of the account information including categorized account information of the user; receiving, by the one or more processors and the chat bot feature, at least one goal preference of the user and at least one interests preference of the user; determining, by the one or more processors, using a trained machine learning model, one or more activities available to the user based on the at least one goal preference and the at least one interests preference of the user received via the chat bot feature, the trained machine learning model having been trained based on (i) training user data that includes information regarding goal preferences and interests preference data associated with persons other than the user; and (ii) training activities data that includes prior available activities data associated with persons other than the user, to learn relationships between the training user data and the training activities data, such that the trained machine learning model is configured to output one or more activities available to the user upon receipt of the at least one goal preference and the at least one interests preference of the user; determining, by the one or more processors, for each of the one or more activities available to the user, a respective estimated influence on the at least one goal preference; filtering, by the one or more processors, the one or more activities available to the user with a respective estimated influence greater than a threshold; and presenting, by the one or more processors and the chat bot feature, a recommendation of action relating to at least one activity of the filtered one or more activities, the recommendation being presented as a voice notification, text notification, graphic notification, or tactile notification.»

П. 11 — «A computer system for providing an adaptive goal management recommendation, the computer system comprising: a memory
having processor-readable instructions stored therein; and at least one processor configured to … perform a plurality of
functions, including functions for:» + операции п. 1 (без «by the one or more processors»).
П. 20 — операции п. 1 до фильтрации включительно, затем вместо последнего шага, дословно: «…determining, by the one or more
processors, a respective satisfaction value based on a respective monetary cost of each of the filtered one or more
activities available to the user; and presenting, by the one or more processors and the chat bot feature, a recommendation
of action based on ranking the determined satisfaction values.»

**Где avalanche/snowball.** Формула: avalanche 0, snowball 0, interest rate 0, «machine learning» 9, «goal» 23.
**Описание: avalanche 0, snowball 0** — слов нет вовсе. Несмотря на слово «debt» в названии, независимые пункты
этого члена семьи о долге не говорят: предмет — «adaptive goal management recommendation» через чат-бот.

**Сравнение по признакам с методом FINPILOT:**

| Признак независимого пункта US12393978B2 (п. 1 / п. 20) | У FINPILOT |
|---|---|
| (a) получение информации о счетах пользователя | **частично** — пользователь вводит доходы/долги/цели вручную; счета не подключаются (агрегации нет) |
| (b) **чат-бот** интерфейса: запрос текстом или голосом | **нет** |
| (c) показ категоризированной информации о счетах в ответ через чат-бот | **нет** |
| (d) получение через чат-бот предпочтений по цели **и по интересам** | **нет** (цели есть, «interests preference» нет; ввод — формы, не чат) |
| (e) **обученная ML-модель** на данных других людей выдаёт доступные «activities» | **нет** |
| (f) оценка влияния каждой activity на цель | **частично по форме** — оцениваем влияние альтернативы распределения на критерии, но не activity из ML |
| (g) фильтр activities по порогу влияния | **частично по форме** — у нас фильтр допустимости по инвариантам, не порог влияния на цель |
| (h) п. 1: показ рекомендации через чат-бот голосом/текстом/графикой/тактильно | **нет** (веб-интерфейс, не чат-бот) |
| (h') п. 20: «satisfaction value» по денежной стоимости activity + ранжирование | **частично по форме** — ранжируем SAW, но не activity, выданные ML |

Вывод исследователя (не заключение о патентной чистоте): формула **уже** и завязана на связку «чат-бот + обученная
на чужих данных ML-модель выбора activities». У FINPILOT нет (b), (c), (d), (e), (h) — пять признаков.
Формула перебора вариантов погашения не покрывает. Граница: вывод держится, пока в FINPILOT нет чат-бота
с ML-подбором действий; если появится разговорный интерфейс с обученной на пользователях моделью подбора, формулу
надо сверять заново (на экспортных рынках; в РФ семья не действует). Формулы родителей — ниже, Г15.2(б).

**Российский член.** DOCDB-семья — только US. RU-массив: q = `"Capital One" OR "Кэпитал Уан" OR "КЭПИТАЛ ВАН"` →
HTTP 200, 21 076 байт, total 4 — все мимо (RU2728953C1, RU2713761C1 — Сбербанк; RU2795371C1 — Группа АйБи;
RU2841233C1 — Яндекс; упоминания в тексте). Поиск по номерам семьи — total 0 (см. выше). **RU/EA-члена нет.**


## ДОБОР Г15 — Г15.1(б): US20250335982A1 и выданный родитель US12361480B1, Wells Fargo, «System and method for financial health robo-advisor» (2026-09-12)

Канал: `curl -sk --http1.1` → Google Patents. `US20250335982A1` → **HTTP 200, 228 532 байта** (формула 20 пп.);
`US12361480B1` → **HTTP 200, 235 557 байт** (формула 15 пп.). Сырые HTML — `/private/tmp/g15/`.

**Библиография.** US20250335982A1: заявка US19/264,619, подана 2025-07-09, приоритет **2022-11-10**, публикация
**2025-10-30**, статус **Pending** (последнее событие — «DOCKETED NEW CASE - READY FOR EXAMINATION», 2025-07-27);
continuation от US18/054,300. Родитель US18/054,300 (подан 2022-11-10) → **US12361480B1, выдан 2025-07-15, Active**.
Правообладатель — Wells Fargo Bank, N.A.; изобретатель — Cathy Ann Costa.
🔴 **Поправка к записи Г3:** в семье есть не только заявка, но и **ВЫДАННЫЙ патент US12361480B1** — Г3 его не видел.
**Семья:** только эти два US-документа (DOCDB). RU/EA/WO/EP нет.

**US20250335982A1 (заявка), независимые пп. 1, 17, 19 — операции совпадают. П. 1 дословно:**
> «1. A method, comprising: receiving, via a processor, a financial health goal from a user, wherein the financial health goal does not include an investment goal; training a machine learning model using historical peer transaction data and location data to identify spending patterns, wherein the training comprises: preprocessing anonymized user transaction histories and associated location data as training input; applying a selected machine learning algorithm to detect correlations between geographic locations and spending behaviors; and generating a trained neural network that predicts purchase probabilities based on a geographic location; monitoring, via a GPS system, one or more geographic locations of a user device; detecting that the user device has entered a predefined geographic area; inputting the geographic area data into the trained neural network to determine a probability of the user making a purchase that would impact the financial health goal; and generating, via the trained neural network, a preventative alert when the probability exceeds a threshold value.»

П. 17 — «A non-transitory machine-readable medium storing instructions that, when executed by a computer system, cause the
computer system to perform operations comprising:» + те же операции. П. 19 — «A system, comprising: a robo-advisor system
configured to:» + те же операции.

**US12361480B1 (выданный родитель), независимые пп. 1, 14, 15 — операции совпадают. П. 1 дословно:**
> «1. A method, comprising: receiving, via a processor, a financial health goal from a user, wherein the financial health goal does not include an investment goal; retrieving, from a data store, one or more financial health templates based on the financial health goal, wherein each of the one or more financial health templates comprise a trained artificial intelligence (AI) model having one or more neural networks trained from a dataset of anonymized peer financial transaction histories using a selected training algorithm, wherein the trained AI model is trained to identify one or more success patterns in the peer financial transaction histories that are predictive of achieving one or more specific financial health goals by training, via the processor, the one or more neural networks based on the selected training algorithm by providing the dataset of anonymized peer financial transaction histories as training input to the one or more neural networks; deriving, via the processor, a financial health advice action based on using the financial health goal as input to the trained AI model of the one or more financial health templates, wherein the trained AI model is configured to identify the one or more success patterns based on the financial health goal, wherein the financial health goal comprises increasing a credit score, reducing a discretionary spending, reducing a total spending, reducing a category of spending, achieving a savings goal amount, creating an emergency fund, repaying a loan, or a combination thereof; providing, via the processor, the financial health advice action, wherein the one or more financial health templates are created based on consumer financial data; monitoring, via a financial network, financial transactions of a user of the financial health advice action; determining, via the processor, that one or more of the financial transactions are not following the financial health advice action; and alerting, via the processor, the user that the financial health advice action is not being followed based on the determination, wherein the one or more financial health templates are created, via the processor, by: selecting a success metric; collecting the consumer financial data related to the success metric; deriving one or more financial success patterns from the consumer financial data by training the trained AI model; and storing the one or more financial success patterns as the trained AI model of the one or more financial health templates, wherein deriving the one or more financial success patterns from the consumer financial data by training the trained AI model based on the selected training algorithm comprises applying machine learning, deep learning, state vector machines, data mining, or a combination thereof, to extract the one or more financial success patterns from the consumer financial data, and wherein applying machine learning, deep learning, state vector machines, data mining, or the combination thereof, comprises creating the one or more neural networks and training the one or more neural networks to detect the one or more financial success patterns, extracting rules via data mining rule extraction, or a combination thereof.»

П. 14 — носитель, п. 15 — «A system, comprising: a robo-advisor system configured to:», операции те же.

**Где avalanche/snowball.** Счёт по формуле: A1 — avalanche 0, snowball 0 (machine learning 6, neural 15); B1 — avalanche 0,
snowball 0 (neural 15, emergency 5). **В формулах обоих нет.** В описании A1 — два упоминания, дословно:
> «…taking out a loan at lower interest rates to pay off a higher interest rate loan, setting up of an automatic payment, creating of a payment plan (e.g., loan payment plan, emergency fund payment plan), making a payment at a certain schedule (e.g., using the “snowball” method to pay off debts from smallest to largest, using the “avalanche” method to pay the debt with highest interest rate first), maintaining an account balance at a certain amount by setting spending limits, and so on. Once the user customizes a financial health plan, the robo-advisor system 102 can aid in the execution of the financial health plan via monit…»

В описании выданного B1 на странице Google Patents счёт avalanche/snowball = **0** (замер тем же скриптом) — то есть
абзац со словами есть только в тексте, опубликованном с continuation-заявкой. Причину (дополненное описание или
неполная OCR-страница родителя) не устанавливал.

**Сравнение по признакам с методом FINPILOT — выданный US12361480B1 (он ближе по предмету: цель «creating an emergency
fund, repaying a loan» прямо названа в формуле):**

| Признак независимого пункта US12361480B1 | У FINPILOT |
|---|---|
| (a) получение от пользователя финансовой цели, не инвестиционной | **есть** (цели, резерв, погашение) |
| (b) выборка из хранилища «financial health templates» по цели | **нет** |
| (c) шаблон содержит **обученную ИИ-модель с нейросетями** на обезличенных историях транзакций **других людей (peer)** | **нет** |
| (d) модель выявляет «success patterns», предсказывающие достижение цели | **нет** |
| (e) вывод «financial health advice action» подачей цели на вход обученной модели | **нет** — совет выводится расчётом (перебор 66 альтернатив, SAW), не моделью |
| (f) перечень целей: кредитный балл, траты, накопления, **резервный фонд, погашение кредита** | **частично** — предмет совпадает (резерв, долг), но это альтернатива внутри признака (e) |
| (g) **мониторинг транзакций пользователя через финансовую сеть** | **нет** — агрегации и мониторинга нет |
| (h) определение, что транзакции не следуют совету, и **оповещение** | **нет** |
| (i) создание шаблонов: метрика успеха → сбор данных потребителей → обучение → хранение | **нет** |
| (j) ML / deep learning / SVM / data mining, нейросети или извлечение правил | **нет** |

**US20250335982A1 (заявка):** признаки — цель; **обучение ML на peer-транзакциях и геолокации**; нейросеть вероятности
покупки по месту; **GPS-мониторинг** устройства; вход в заданную геозону; превентивное оповещение по порогу.
У FINPILOT есть только (a) цель; нет ни одного из остальных пяти.

Вывод исследователя (не заключение о патентной чистоте): обе формулы Wells Fargo **уже** метода «перебор вариантов
распределения»: выданная требует обученной на чужих транзакциях нейросетевой модели + мониторинга транзакций + оповещения
о неисполнении; заявка — геолокации и GPS. Ни одна не содержит перебора альтернатив, инвариантов, очерёдности погашения.
🔴 Граница: из всех разобранных в Г15 документов **US12361480B1 единственный, где в независимом пункте прямо стоят
«creating an emergency fund, repaying a loan»** — то есть предмет наш. Держит его от FINPILOT исключительно связка
«обученная на peer-данных модель + мониторинг транзакций + алерт о неисполнении». Если на экспортных рынках появится
модуль «следим за транзакциями и предупреждаем, что пользователь отклонился от плана» **вместе** с обучаемой моделью —
сверять заново. В РФ членов семьи нет.

**Российский член.** RU-массив: `"Wells Fargo" OR "Уэллс Фарго" OR "ВЕЛЛС ФАРГО"` → HTTP 200, 18 639 байт, total 3,
все мимо (RU2479864C1 — Дайер/Сибирски; RU2754240C1 — КуРэйт; RU2839053C1 — Сбербанк; упоминания в тексте).
По номерам семьи — total 0 (запрос выше). **RU/EA-члена нет.**


## ДОБОР Г15 — Г15.1(в): родительские патенты семьи USAA «Financial autopilot» (2026-09-12)

Зачем: в continuation-семье широкий пункт может стоять у родителя, а не у последнего члена. Каналы — Google Patents, curl:
`US11127075B1` HTTP 200, 243 005 байт (15 пп.); `US11861694B1` HTTP 200, 229 851 байт (18 пп.); `US12141861B1` HTTP 200,
228 258 байт (18 пп.). Все Active. Счёт по формулам всех трёх: avalanche 0, snowball 0, debt 0, interest 0, saving 0;
в описаниях всех трёх avalanche/snowball = 0 (абзац со словами есть только в US12524803B1).

**US11127075B1 (заявка US16/585,519 от 2019-09-27, выдан 2021-09-21), независимые пп. 1, 6, 11. П. 1 дословно:**
> «1. A method implemented by a data processing system, comprising: receiving training data including (i) transaction histories of a plurality of users during a specific period of time, and (ii) for each of the plurality of users, data specifying unexpected expenses that occurred to the respective user during the specific period of time; training a neural network to predict an unexpected expense for a given transaction history using a supervised learning technique based on the training data, wherein the neural network is configured to receive as input the given transaction history and to process the input to generate an output that specifies a specified expense for the given transaction history, wherein the neural network comprises a plurality of artificial neurons that are connected through edges and are aggregated into a plurality of neural network layers comprising at least an input layer and an output layer, wherein each of the edges is configured to transmit a signal from one artificial neuron to another artificial neuron, and wherein an output of each of the plurality of artificial neurons is computed by a specified function of a sum of inputs of the artificial neuron in accordance with a plurality of weights; setting values of the plurality of weights based on the training of the neural network; receiving new data indicating a list of historic transactions of a particular user from a plurality of financial institutions; based on the list of historic transactions, creating a plurality of categories using a clustering algorithm; generating a hierarchy among the plurality of categories; processing, by the data processing system, the new data using the plurality of artificial neurons in the trained neural network in accordance with the values of the plurality of weights to identify at least one specified expense for the particular user, wherein the artificial neurons in the input layer are configured to receive the new data as input and the artificial neurons in the output layer are configured to generate output that identifies the at least one specified expense; determining a plan to account for the at least one specified expense, wherein the plan comprises deducting a payment for the at least one specified expense from a lowest ranked category in the hierarchy; and automatically transferring, by the data processing system, an amount from a first account of the particular user to a second account of the particular user based on the plan.»
Пп. 6 (носитель) и 11 (система) — те же операции.

**US11861694B1 (заявка US17/410,473 от 2021-08-24, выдан 2024-01-02, расч. истечение 2040-03-31), независимые пп. 1, 7, 13.**
Отличие от US11127075B1: убраны кластеризация категорий, иерархия и «deducting … from a lowest ranked category»; остались
обучение нейросети на неожиданных расходах популяции → данные транзакций пользователя **«from a plurality of financial
institutions»** → выявление расхода → «determining a plan to account for the at least one specified expense; and
automatically transferring, by the data processing system, an amount from a first account of the particular user to a second
account of the particular user based on the plan.» (дословно, конец п. 1).

**US12141861B1 (заявка US18/393,397 от 2023-12-21, выдан 2024-11-12), независимые пп. 1, 7, 13.** Ещё шире по концовке:
«unexpected expenses» → «expenses»; нет «plurality of financial institutions»; нет автоперевода; п. 1 оканчивается,
дословно: «…receiving new data indicating a list of historic transactions of a particular user; processing, by the data
processing system, the new data using the plurality of artificial neurons in the trained neural network … to identify at
least one specified expense for the particular user …; and determining a plan to account for the at least one specified
expense.»

**Сравнение по признакам (для всей семьи USAA):** обязательный во всех независимых пунктах всех четырёх патентов блок —
**обучающие данные по множеству пользователей + обучение нейросети с учителем + структура сети с весами** (+ в двух
старших: агрегация транзакций из нескольких банков и **автоматический перевод между счетами** пользователя). У FINPILOT
нет ни обучаемой модели, ни популяционных данных, ни агрегации, ни автоперевода. Самый широкий член — US12141861B1
(«determining a plan to account for the specified expense») — всё равно требует, чтобы расход выявила обученная нейросеть.

Вывод исследователя: семья USAA к методу FINPILOT не подходит ни одним независимым пунктом: её ядро — предсказание
расхода нейросетью, а не распределение свободного потока. Граница: сверять заново, если FINPILOT начнёт
**предсказывать расходы обучаемой на пользователях нейросетью** (на экспортных рынках; в РФ членов нет).


## ДОБОР Г15 — Г15.2(б): родительские патенты семьи Capital One (2026-09-12)

Каналы — Google Patents, curl: `US11532041B2` HTTP 200, 311 768 байт (20 пп.); `US11893630B2` HTTP 200, 309 919 байт (20 пп.).
Оба Active. Счёт: avalanche 0, snowball 0 и в формулах, и в описаниях обоих.

**US11532041B2 (заявка US16/923,405 от 2020-07-08, публ. US20220012803A1, выдан 2022-12-20, истечение 2040-09-03) — ЕДИНСТВЕННЫЙ
член семьи, у которого родовое понятие «debt management recommendation». Независимые пп. 1, 11, 20. П. 1 дословно:**
> «1. A computer-implemented method for providing a debt management recommendation, the method comprising: generating, by one or more processors, a user interface of a user device associated with a user, the user interface including a navigation bar, a home view, a preference view, an activities view, and a chatbot feature; receiving, by one or more processors, financial information regarding a user; categorizing, by the one or more processors, transaction information of the user based on the financial information; receiving, by the one or more processors, via the chatbot feature of the user interface, a query from the user; in response to the query, presenting, by the one or more processors, via the chatbot feature of the user interface, a portion of the categorized transaction information of the user; receiving, by the one or more processors, information regarding at least one financial preference and at least one transaction preference of the user via the chatbot feature of the user interface; determining, by the one or more processors, using a trained machine learning model, one or more activities available to the user based on the at least one financial preference and the at least one transaction preference of the user, wherein the trained machine learning model is trained based on (i) training user data that includes information regarding financial preferences and transaction preference data associated with persons other than the user; and (ii) training activities data that includes prior available activities data associated with persons other than the user, to learn relationships between the training user data and the training activities data, such that the trained machine learning model is configured to determine one or more activities available to the user upon the input of the at least one financial preference and the at least one transaction preference of the user; calculating, by the one or more processors, for each of the one or more activities available to the user, an estimated influence on the at least one financial preference; presenting, by the one or more processors, via the chatbot feature of the user interface, the estimated influence on the at least one financial preference based on a user selected one of the one or more activities available to the user; filtering, by the one or more processors, the one or more activities available to the user with a positive estimated influence to the at least one financial preference; and presenting, by the one or more processors, via the chatbot feature of the user interface, a recommendation of action relating to the one of the one or more activities available to the user, wherein the recommendation of action relating to the one of the one or more activities available to the user is presented by at least one of voice notification, application notification, tactile notification, or graphic notification.»

П. 11 — система с теми же функциями. П. 20 — те же операции, плюс: запрос через чат-бот финансового и транзакционного
предпочтения, «assigning … an expected value to the at least one transaction preference», «calculating … a value of
satisfaction based on a monetary cost of the one or more activities … with positive estimated influence and the expected
value; ranking … based on the value of satisfaction; … recommending … one of the one or more activities … based on the
ranking» (дословные фрагменты).

**US11893630B2 (заявка US18/057,522 от 2022-11-21, выдан 2024-02-06, истечение 2040-07-08), независимые пп. 1, 11, 20** —
«adaptive goal management recommendation»; интерфейс с «navigation bar, a chat bot feature, and a text bar»; далее по
существу тот же набор, что у US12393978B2 (цель и «interests preference» через чат-бот → обученная на других людях
ML-модель → activities → оценка влияния → фильтр положительного влияния → рекомендация через чат-бот; п. 20 — satisfaction
value по денежной стоимости и ранжирование).

**Сравнение по признакам (вся семья Capital One):** обязательные во всех независимых пунктах трёх патентов признаки —
**чат-бот интерфейса** (запрос, показ категоризированных транзакций, сбор предпочтений) и **обученная на данных других
людей ML-модель, выдающая «activities»**. У FINPILOT нет ни того, ни другого. Совпадает у нас только общая схема
«оценить влияние варианта → отфильтровать → ранжировать» (п. 20 всех трёх), но она в формуле применена к
activities, выданным ML-моделью, и подаётся через чат-бот. Название «debt management» у US11532041B2 формулой не
раскрыто в сторону долга: ни ставок, ни очерёдности, ни сумм погашения в независимых пунктах нет.


## ДОБОР Г15 — Г15.3: соседние патенты с приоритетом от 2018 года (2026-09-12)

Канал: `GET https://patents.google.com/xhr/query?url=<urlencoded>&exp=` (curl, браузерный UA), `after=priority:20180101`,
`num=100`. Скрипт — `/private/tmp/g15/gpq.py`, ответы — `/private/tmp/g15/gpq_*.json`. Все запросы HTTP 200.

| # | Запрос | Байт | Всего | Новое против Г3 |
|---|---|---|---|---|
| Q1 | `("debt avalanche")` | 4 998 | 2 | US12524803B1 (USAA, разобран выше); US20250315893A1 (Insphire, уже в А.6) |
| Q2 | `("debt snowball")` | 5 042 | 2 | US12524803B1; **US20210142402A1 Capital One «Guidance Engine»** |
| Q3 | `(allocate) ("surplus cash flow" OR "surplus income" OR "excess cash") (debt) (savings goal)` | 35 849 | 18 | корпоративное казначейство, токенизация, CME; US20230401644A1 (Apriority); JP2025154093A (Money Forward) — ни одного про домохозяйство с распределением в формуле, кроме USAA |
| Q4 | `("emergency fund") ("debt payoff" OR "debt repayment" OR "pay down debt") (recommendation)` | 25 967 | 13 | US20240135456A1 (Ahora); **US11669897B2 Capital One «Guidance engine»**; US12254518B1 (Freedom Financial Network); WO2026074314A1 (1Finance); KR102121857B1 (RunInvest); остальное — CN/KR про корпорации |
| Q5 | `("multi-criteria" OR "multiple criteria" OR "weighted sum") (allocation) ("personal finance" OR household) (debt)` | 293 747 | 343 | шум (NFT, фитнес-трекеры, авиация); по предмету — US11783252B1 (Double Diamond), US11663668B1 (Diane Money), US11900227B1 (Gravystack) |
| Q6 | `("pay off" OR payoff) ("highest interest" OR "highest APR") ("emergency fund" OR "savings goal")` | 12 975 | 5 | US20250335982A1 (Wells Fargo); **US12008644B2 Capital One «Guidance engine»**; US12254518B1 |

Все кандидаты открыты на Google Patents (curl, HTTP 200, размеры ниже), формулы разобраны скриптом `claims.py`.

### 🔴 Г15.3(а): семья Capital One «Guidance engine: an automated system and method for providing financial guidance» — БЛИЖАЙШИЙ по признакам документ из всех найденных за Г3 и Г15

Страницы: US11023967B1 HTTP 200, 593 928 байт; US11669897B2 HTTP 200, 599 617; US12008644B2 HTTP 200, 624 118; публикации заявок
US20210142402A1 (741 646), US20210342939A1 (624 381), US20230252559A1 (632 641). Правообладатель — **Capital One Services, LLC**;
изобретатели — Katharine Schlesinger, John Rush, Zheyu Yang, Matthew Davis. Приоритет у всех — **2019-11-12**.

| Патент | Заявка, подача | Публикация заявки | Выдача | Статус |
|---|---|---|---|---|
| **US11023967B1** | US16/680,793, 2019-11-12 | US20210142402A1 (2021-05-13) | 2021-06-01 | Active; пошлина за 4-й год уплачена 2024-11-22 |
| **US11669897B2** | US17/322,968, 2021-05-18 (continuation) | US20210342939A1 (2021-11-04) | 2023-06-06 | Active; расчётное истечение **2040-01-10** |
| **US12008644B2** | US18/137,023, 2023-04-20 (continuation) | US20230252559A1 (2023-08-10) | 2024-06-11 | Active (PATENTED CASE 2024-05-22) |

Семья — **только US** (DOCDB: шесть US-документов). RU-массив: q = `US11023967 OR US11669897 OR US12008644 OR US20230252559 OR
US12254518 OR US20240135456` → HTTP 200, 184 байта, **total 0**; `"Capital One" OR "Кэпитал Уан" OR "Капитал Уан"` → total 4,
все мимо (Сбербанк ×2, Группа АйБи, Яндекс — упоминания). **RU/EA-члена нет.**

**Почему этот документ важнее Intuit, USAA, Wells Fargo.** Во всех прежних формулах обязательный признак — обучаемая
модель (ML/нейросеть). **Здесь ML нет** (счёт по формуле: «machine learning» 0, «neural» 0). Формула — детерминированный
«decision tree engine» над теми же величинами, что у нас: **ежемесячные расходы, ежемесячный доход, уровень резервного
фонда, уровень высокопроцентного долга** → «financial action». Счёт по формулам: emergency 46–55, debt 25–34, interest 26–37.

**US12008644B2 — самый широкий член семьи. Независимые пп. 1 (система), 11 (способ), 16 (носитель). П. 1 дословно:**
> «1. A system comprising: a data integration engine comprising: one or more first processors; and first memory storing first instructions that, when executed by the one or more first processors, cause the data integration engine to: determine user data associated with an estimated monthly expenses of a user, an estimated monthly income of the user, an estimated emergency fund level of the user, and an estimated high interest debt level of the user, wherein at least a portion of the user data is in a non-compliant format; and convert the portion of the user data in the non-compliant format into a compliant format; a decision tree engine comprising: one or more second processors; and second memory storing second instructions that, when executed by the one or more second processors, cause the decision tree engine to: receive, from the data integration engine, the user data having the converted portion; determine, based on the user data having the converted portion, a financial action for the user, wherein determining the financial action comprises determining results for each branch of a decision tree that associates the financial action with combinations of values of the estimated monthly expenses, the estimated monthly income, the estimated emergency fund level, and the estimated high interest debt level; and cause, via a guidance user interface, an output of the financial action.»

П. 11 — способ с теми же шагами **плюс**, дословно: «validating, by the data integration engine, the converted portion of the
user data by generating a plurality of test cases to test compliance of the converted portion of the user data and applying the
plurality of test cases to the converted portion of the user data; sending, by the data integration engine and to a decision tree
engine, the user data having the converted portion;» — далее как в п. 1. П. 16 — носитель, те же шаги, что в п. 11.

**US11669897B2, п. 1 (система; пп. 8 — способ, 15 — носитель, те же шаги), ключевые отличия от US12008644B2, дословно:**
«receive, via a guidance user interface, first input data … monthly expenses, monthly income, emergency fund level, or high interest
debt level; receive, from one or more data servers, second input data …; optimize the second input data by integrating the first
input data into the second input data; generate … first output data associated with an estimated committed monthly expenses …
wherein the estimated committed monthly expenses are associated with a total monthly fixed expense incurred by the user to cover
essential needs, and the estimated monthly income comprises a gross income or a net income; and generate … second output data
associated with an estimated emergency fund level of the user and an estimated high interest debt level of the user, wherein the
estimated emergency fund level is based on an amount of liquid assets available to cover the estimated committed monthly expenses,
and wherein the estimated high interest debt level is associated with one or more loans with interest rates above a pre-set
threshold;» → decision tree engine → «cause, via the guidance user interface, an output of the financial action, the estimated
committed monthly expenses, the estimated monthly income, the estimated emergency fund level, and the estimated high interest debt
level.» Формата «non-compliant» в этом члене нет, но есть **второй источник данных — внешние серверы** и их слияние с вводом.

**US11023967B1 (самый узкий), п. 1 (пп. 8, 15 — те же шаги):** всё, что в US11669897B2, **плюс** «non-compliant format» внешних данных,
валидация тест-кейсами, доход «gross, a net and a discretionary income» и **третий выход — confidence score**, дословно:
«data indicating a variability score for each of the estimated committed monthly expenses, the estimated monthly income, the
estimated emergency fund level, and the estimated high interest debt level, wherein the variability score is based on a ratio of an
interquartile range (IQR) or standard deviation to a value … and data indicating a reasonableness score for each of …» — и вывод
этого балла в интерфейс.

**Сравнение по признакам с методом FINPILOT (признаки метода — §5 `fips_patent_clearance_2026-09-10.md`; реализация кода не
сверялась — это граница вывода):**

| Признак независимого пункта | US12008644B2 п. 1 | US11669897B2 п. 1 | US11023967B1 п. 1 | У FINPILOT |
|---|---|---|---|---|
| (a) данные: расходы в месяц, доход в месяц, уровень резервного фонда, уровень высокопроцентного долга | да | да (+ «committed expenses» как обязательные на базовые нужды; резерв = ликвидные активы к обязательным расходам; долг = кредиты со ставкой выше порога) | да | **ЕСТЬ по существу**: доход, расходы, резерв, долги со ставками. «Высокопроцентный долг по порогу ставки» как отдельной величины у нас нет — долги упорядочиваются по ставке (Avalanche), а не делятся порогом |
| (b) часть данных в «non-compliant format» и конвертация в «compliant format» | да | нет | да | **НЕ ОПРЕДЕЛЕНО по канону метода** — зависит от того, считать ли нормализацию пользовательского ввода (разбор сумм, приведение типов) таким признаком. Нужна сверка с кодом и толкование поверенного |
| (c) валидация конвертированных данных генерацией тест-кейсов | только пп. 11, 16 | нет | да | **нет** в методе |
| (d) второй источник — внешние серверы данных, слияние с вводом | нет | да | да | **нет** — только ручной ввод, агрегации нет |
| (e) confidence score: variability (IQR или σ к значению) + reasonableness по каждой из четырёх величин | нет | нет | да | **нет** (Монте-Карло даёт интервал прогноза потока, но не балл вариабельности входов по IQR/σ) |
| (f) **decision tree engine**: действие определяется результатами **по каждой ветви дерева решений**, связывающего действие с **комбинациями значений** четырёх величин | да | да | да | **НЕТ по форме**: действие у нас не выбирается ветвлением по комбинациям значений, а получается перебором 66 альтернатив распределения, фильтром по инвариантам (Rt ≥ 0, ПДН ≤ 0,40) и ранжированием взвешенной суммой (SAW). Результат — доли распределения, а не одно «действие» из дерева |
| (g) вывод действия через «guidance user interface» | да | да (+ вывод четырёх величин) | да (+ confidence score) | **есть** |
| раздельные «engine» на разных процессорах/памяти (системный пункт) | да | да | да | формально: веб-сервис на одном сервере; значение этого признака — вопрос толкования |

**Вывод исследователя (не заключение о патентной чистоте).**
1. Это **первый найденный документ без ML, чей предмет совпадает с нашим почти полностью**: те же четыре входа, тот же
   жанр («что делать со свободными деньгами: резерв или высокопроцентный долг»), детерминированное правило. Он опровергает
   общий тезис прежних добор «все формулы соседей держатся на обучаемой модели».
2. Отличие FINPILOT от самого широкого члена (US12008644B2 п. 1) держится на **двух** признаках: (f) дерево решений
   по комбинациям значений против перебора альтернатив + инварианты + SAW и (b) конвертация «non-compliant format», наличие
   которой в нашей реализации по канону не определить. Если (b) у нас есть, отличие остаётся **одно — (f)**, и оно
   сводится к вопросу, эквивалентен ли наш перебор с фильтром и ранжированием «дереву решений» по смыслу формулы.
   Это вопрос для патентного поверенного США, не для исследователя.
3. **Территория:** семья только в US; RU/EA/WO/EP нет. На российский рынок документ не действует (ст. 1345 и ст. 1350 ГК РФ —
   патент США прав в РФ не создаёт); вывод «блокера в РФ нет в проверенном объёме» не меняется.
4. 🔴 **Для экспортных рынков (США)** US12008644B2 — **главный документ для сверки** перед любым запуском в США; истечение
   семьи — не раньше 2040-01-10 (по US11669897B2). И прямое следствие для продукта на любых рынках: **не реализовывать
   рекомендацию как дерево правил вида «если резерв меньше X месяцев обязательных расходов и есть долг со ставкой выше Y,
   то …» над этими четырьмя величинами** — именно такую конструкцию формула описывает дословно; перебор + инварианты + SAW
   от неё отличается по форме.

### Г15.3(б): прочие кандидаты — одна строка о сути

| Документ | Правообладатель, приоритет | Статус | Суть независимого пункта (по тексту формулы) | RU-член | Признаки, которых у FINPILOT нет |
|---|---|---|---|---|---|
| **US20240135456A1** «Personal financial management and coaching tool» (HTTP 200, 406 688 байт) | Ahora Inc., 2022-01-07 | **Pending**; окончательные отказы 2024-06-26 и 2026-01-30, заявка снова на экспертизе с 2026-04-30 | п. 1 дословно: «A method comprising: receiving financial data associated with a user; updating budget information based at least in part on the received financial data; determining a state of personal finance of the user based at least in part on the received financial data; facilitating presentation of the state of personal finance in association with the updated budget information via a graphical user interface (GUI); receiving goal information associated with the user, the goal information indicative of one or more financial goals of the user; determining progress of the one or more financial goals based at least in part on the state of personal finance; and facilitating presentation of a notification based at least in part on the progress of the one or more financial goals via the GUI.» | нет (семья только US; RU-поиск `"Ahora"` → 0) | 🔴 **формула очень широкая, совпадает с любым PFM**; у FINPILOT по канону есть приём данных, состояние финансов, GUI, цели; «updating budget information» и «notification based on progress» — зависят от реализации. Это заявка, прав не даёт; дважды отклонена окончательно. **Следить за выдачей** — на экспортных рынках |
| **US12254518B1** «Real-time individualized action plan for clients of a financial assistance service» (HTTP 200, 411 943) | Freedom Financial Network LLC, 2021-05-04 (семья: + US12333599B1) | Active | система: финданные → «personalized balance sheet and an individualized action plan … providing a set of priorities»; **в реальном времени** обнаруживает изменения через источник данных финсчёта пользователя, обновляет план, передаёт контент со ссылкой на ресурс для выполнения действия | нет | реальное время, подключение к источнику данных счёта, ссылка на исполнение действия |
| **US20230401644A1** «Systems and methods for conducting mass market holistic loan optimization» (HTTP 200, 384 576) | Apriority Financial Inc., 2022-06-13 | Pending | п. 1: профиль (доход, кредитный балл, активы, долговой портфель) → **получение котировок ставок** → «optimizer engine» → «optimum loan product or an optimum loan portfolio» | нет | котировки ставок кредиторов, подбор кредитного продукта (у нас нет подбора продуктов) |
| **US11783252B1** «Apparatus for generating resource allocation recommendations» (HTTP 200, 620 785) | Double Diamond Interests LLC, 2022-10-31 | Active | данные о **недвижимости** пользователя → метрика улучшения → **обученная ML-модель** распределения ресурсов | нет | недвижимость, ML |
| **US11663668B1** «Apparatus and method for generating a pecuniary program» (HTTP 200, 453 412) | Diane Money IP LLC, 2022-07-15 | Active | тренды в денежных данных → **ML-классификация** в приоритетный балл с переобучением → программа | нет | ML с переобучением |
| **US11900227B1** «Apparatus for producing a financial target strategy» (HTTP 200, 505 458) | Gravystack Inc., 2022-07-25 | Active | история + цель → **ML-модель** паттернов → рейтинг необходимости → скорректированная цель через вторую ML-модель | нет | две ML-модели |
| **WO2026074314A1** «Method and system for recommending a financial plan» (HTTP 200, 149 331) | 1Finance Private Ltd (Индия), 2024-10-02 | PCT, pending | **формула на странице не извлечена** (0 пунктов в разметке `claims`); в тексте есть «emergency», «interest» | PCT-стадия: 31-мес. срок для RU истекает ~2027-05-02 — **следить** | не определено — см. НЕ ДОБЫТО |
| **KR102121857B1** «Method for providing financial design service» (HTTP 200, 164 722) | 런인베스트 (RunInvest), 2018-05-02 | Active | формула на английской странице не извлечена (0 пунктов); в тексте «debt» ×6, «emergency» ×2 | нет (семья KR: + KR20190126682A) | не определено |
| US20250315893A1 (Insphire) | — | — | уже разобран в А.6 (RL-оптимизация) | — | — |

Глубоко разобран только документ, где алгоритм распределения/выбора действия — в независимом пункте без обучаемой модели
(Guidance engine). Apriority (оптимизатор) — предмет кредитный продукт, не распределение потока; разбирать глубже не стал.


# ИТОГ ДОБОРА Г15 (патенты, 12.09.2026)

| Пункт | Статус | Где раздел |
|---|---|---|
| **Г15.1** US12524803B1 (USAA) — формула, статус, семья, RU-член, сравнение | **добыт полностью** | «ДОБОР Г15 — Г15.1(а)» и «Г15.1(в)» (три родительских патента семьи) |
| **Г15.1** US20250335982A1 (Wells Fargo) — то же | **добыт полностью и расширен** | «Г15.1(б)»: разобрана не только заявка, но и **выданный родитель US12361480B1**, которого Г3 не видел |
| **Г15.2** US12393978B2 (Capital One, «debt management with spending recommendation») | **добыт полностью** | «Г15.2» + «Г15.2(б)» (родители US11532041B2 и US11893630B2) |
| **Г15.3** поиск соседних патентов с приоритетом от 2018 | **добыт**: 6 запросов к JSON-эндпоинту Google Patents, 9 новых документов разобрано | «Г15.3», глубоко — «Г15.3(а)» семья Capital One «Guidance engine» |

## 🔴 Прямой ответ на главный вопрос пункта

**1. Есть ли avalanche/snowball в НЕЗАВИСИМЫХ пунктах формул? — НЕТ. Ни у одного из проверенных.**
Машинный счёт по полному тексту формул (скрипт `/private/tmp/g15/claims.py`, все пункты каждого документа):

| Документ | avalanche в формуле | snowball в формуле | где слова есть |
|---|---|---|---|
| US12524803B1 (USAA, выдан 2026-01-13) | 0 | 0 | только в описании, один абзац (причём определения перепутаны: «snowball (highest interest paid off first), debt avalanche (lowest balance paid first)») |
| US11127075B1 / US11861694B1 / US12141861B1 (родители USAA) | 0 | 0 | в описаниях тоже 0 |
| US20250335982A1 (Wells Fargo, заявка) | 0 | 0 | только в описании, один абзац |
| US12361480B1 (Wells Fargo, выдан 2025-07-15) | 0 | 0 | в описании на странице Google Patents тоже 0 |
| US12393978B2 / US11893630B2 / US11532041B2 (Capital One, «debt management») | 0 | 0 | в описаниях 0 |
| US11023967B1 / US11669897B2 / US12008644B2 (Capital One, «Guidance engine») | 0 | 0 | в описаниях 0 |
| (для полноты, из Г3) US11544780B2 и CA3162417C (Intuit) | 0 | 0 | только в описании |

То есть картина Intuit из Г3 — «слова в описании, в формуле нет» — **подтверждена для всех остальных кандидатов**.
Ни одна проверенная формула не монополизирует ни Avalanche как очерёдность, ни перебор вариантов погашения вообще.

**2. Есть ли российский или евразийский член семьи? — НИ У ОДНОЙ ИЗ ТРЁХ СЕМЕЙ НЕТ.**
- USAA «Financial autopilot» — 4 патента, DOCDB-страны **только US**;
- Wells Fargo «financial health robo-advisor» — 2 документа, **только US**;
- Capital One «debt management with spending recommendation» — 3 патента + 2 публикации, **только US**;
- Capital One «Guidance engine» (найдена в Г15.3) — 3 патента + 3 публикации, **только US**.
Обратный поиск по RU-массиву (`POST searchplatform.rospatent.gov.ru/search`, `ru_since_1994`): по номерам всех семей —
HTTP 200, 182–184 байта, **total 0**; по именам правообладателей («USAA / United Services Automobile Association»,
«Wells Fargo», «Capital One», «Freedom Financial», «Ahora», «Apriority») — попадания только текстовые, в чужих RU-патентах
(Яндекс, Сбербанк, Группа АйБи и др.), ни одного документа этих компаний.

**3. Формула шире или уже «перебора вариантов погашения»? — УЖЕ, у всех, но по РАЗНЫМ причинам.**
- USAA — обучение нейросети предсказанию расхода (5 признаков, у нас нет ни одного);
- Wells Fargo — обученная на peer-транзакциях модель + мониторинг транзакций + алерт о неисполнении (у выданного B1);
  геолокация и GPS (у заявки);
- Capital One «debt management» — чат-бот + обученная на чужих данных ML-модель «activities»;
- Capital One «Guidance engine» — **без ML**, но через «decision tree engine» по комбинациям значений четырёх величин.

## 🔴 Меняется ли вывод «блокера нет в проверенном объёме»?

**Для рынка РФ — НЕТ, вывод не меняется и территориально усилен:** ни одна из четырёх разобранных в Г15 семей не имеет
российского или евразийского члена, ни один документ не действует в РФ. Новых RU-документов Г15 не нашёл (обратные поиски
дали 0). Вывод Г3 и Д12 остаётся в силе.

**Для экспортных рынков (США) — ДА, картина изменилась, и вот чем именно.**
1. 🔴 Найден документ, которого не было ни в Г3, ни в прежних доборах: **US12008644B2 (и семья US11023967B1 / US11669897B2),
   Capital One «Guidance engine», приоритет 2019-11-12, все Active, US11669897B2 действует до ~2040-01-10.** Это **первая
   найденная формула без машинного обучения**, работающая ровно с нашими четырьмя величинами — ежемесячные расходы,
   ежемесячный доход, уровень резервного фонда, уровень высокопроцентного долга — и выдающая «financial action».
   Отличие FINPILOT держится на признаке «decision tree engine … determining results for each branch of a decision tree
   that associates the financial action with combinations of values» (у нас — перебор 66 альтернатив, фильтр инвариантов,
   SAW) и на признаке конвертации «non-compliant format», наличие которого в нашей реализации по канону метода определить
   нельзя. Это **сравнение по признакам, а не заключение о патентной чистоте**; вопрос эквивалентности «перебор + SAW» и
   «дерево решений» — к патентному поверенному США.
2. Практическое следствие для продукта (решение — за владельцем): **не оформлять рекомендацию как дерево правил** вида
   «если резерв ниже X месяцев обязательных расходов и есть долг со ставкой выше порога Y — то действие Z» над этими
   четырьмя величинами; именно такая конструкция описана в формуле дословно.
3. Второе изменение: у Wells Fargo, кроме заявки, есть **выданный US12361480B1**, и в его независимом пункте прямо стоят
   цели «creating an emergency fund, repaying a loan» — то есть наш предмет. Держат его от FINPILOT обученная на
   peer-данных нейросетевая модель, мониторинг транзакций через финансовую сеть и алерт о неисполнении совета.
   Если продукт когда-нибудь получит связку «следим за транзакциями → предупреждаем об отклонении от плана» вместе
   с обучаемой моделью — сверять заново.
4. Опровергнут общий тезис прежних доборов «все соседние формулы держатся на обучаемой модели»: у «Guidance engine» её нет.

## НЕ ДОБЫТО в Г15 (с точными причинами)

- **Формула WO2026074314A1** (1Finance Private Ltd, Индия, приоритет 2024-10-02, «Method and system for recommending a
  financial plan») — страница Google Patents отдала HTTP 200, 149 331 байт, но секция `claims` содержит **0 пунктов**
  (у PCT-публикации формула в разметку не попала); Patentscope не пробовал — канал ранее давал оболочку без карточки.
  🔴 **Следить:** 31-месячный срок входа в нацфазу RU истекает около 2027-05-02.
- **Формула KR102121857B1** (RunInvest, приоритет 2018-05-02) — на английской странице `claims` пуст (0 пунктов),
  корейский оригинал не запрашивался; семья только KR.
- **Расчётная дата истечения US12008644B2 и US11023967B1** — на страницах Google Patents поля `expiration` нет
  (у US11669897B2 оно есть: 2040-01-10); терминальные дисклеймеры не проверялись.
- **Есть ли в реализации FINPILOT признак «конвертация non-compliant format → compliant format»** — по канону метода
  (`docs/math_model.md`, §5 `fips_patent_clearance_2026-09-10.md`) не определяется; сверка с кодом в объём Г15 не входила
  и относится к компетенции поверенного, а не исследователя.
- **INPADOC-семьи через Espacenet/OPS** — не запрашивались (Espacenet отдаёт Cloudflare, OPS без ключа 403, Lens 401 —
  по заданию не более одной попытки); использованы DOCDB-семьи Google Patents + обратный поиск по RU-массиву.
- **Заявки Capital One и Wells Fargo, поданные после 2025 года и ещё не опубликованные** — принципиально недоступны
  (18-месячный срок публикации); это ограничение метода, а не канала.

## ДОБОР Г25 (16.09.2026)

> Первый заход агента оборвался на лимите аккаунта (HTTP 429) до первой записи в файл.
> После смены аккаунта в контексте агента не осталось добытых фактов, поэтому переносить нечего.
> Работа начата заново, записи ниже сделаны по ходу.

### Г25.3 и Г25.4 — уже закрыты раньше, повторно не добывались

- **Формула CA3162417C** закрыта в «ДОБОР Г3 — Г3.1» этого файла: независимые пп. 1 и 9 приведены дословно,
  отличие от US11544780B2 одно — «and» вместо «or» в операции корреляции. Порядка погашения и распределения
  потока между долгами и накоплениями **в формуле нет**: avalanche, snowball и fireball упомянуты только в описании.
  Постановка «не закрыта по бюджету в Г7» в COVERAGE_AUDIT_3 устарела и опирается на строку 1281 файла.
- **Индикатор Banco de España** закрыт в «ДОБОР Г7», раздел «Banco de España, Box 2 — состав индикатора
  уязвимости ДОБЫТ ПОЛНОСТЬЮ»: это среднее арифметическое пяти субиндикаторов, HTTP 200, 249 131 байт.
  Постановка в аудите тоже устарела.

### Г25.2 — статус и расчётные сроки: Google Patents, 16.09.2026

Канал: `curl -sk --http1.1` с браузерным UA → `https://patents.google.com/patent/<N>/en`. Все 14 запросов дали
HTTP 200. Разбор полей `legalStatusIfi`, timeline (`events`), `legalEvents` (USPTO/CIPO) сделан скриптом.
«Adjusted» — Google учёл PTA; «Anticipated» — 20 лет от самой ранней непровизорной подачи без PTA.

| Документ | Байт | Приоритет | Подача | Статус | Истечение (Google) | Пошлины / события |
|---|---|---|---|---|---|---|
| US11127075B1 (USAA) | 243 005 | 2018-09-28 | 2019-09-27 | Active | 2039-09-27 anticipated | MAFP 4-й год уплачена 2025-03-21 |
| US11861694B1 (USAA, продолж.) | 229 851 | 2018-09-28 | 2021-08-24 | Active | **2040-03-31 adjusted** | выдан 2024-01-02 |
| US12141861B1 (USAA, продолж.) | 228 258 | 2018-09-28 | 2023-12-21 | Active | 2039-09-27 anticipated | выдан 2024-11-12 |
| US12524803B1 (USAA, продолж.) | 202 629 | 2018-09-28 | 2024-10-10 | Active | 2039-09-27 anticipated | выдан 2026-01-13 |
| US12361480B1 (Wells Fargo) | 235 557 | 2022-11-10 | 2022-11-10 | Active | 2042-11-10 anticipated | выдан 2025-07-15; **Certificate of correction 2026-03-10** |
| US20250335982A1 (Wells Fargo, продолж. US19/264,619) | 228 532 | 2022-11-10 | 2025-07-09 | **Pending** | — (при выдаче ~2042-11-10 + PTA) | заявка |
| US11532041B2 (Capital One, debt mgmt) | 311 768 | 2020-07-08 | 2020-07-08 | Active | **2040-09-03 adjusted** | выдан 2022-12-20; MAFP на странице нет (срок 3,5 года — 2026-06-20, льготные 6 мес. до 2026-12-20) |
| US11893630B2 (Capital One, продолж.) | 309 919 | 2020-07-08 | 2022-11-21 | Active | 2040-07-08 adjusted | выдан 2024-02-06 |
| US12393978B2 (Capital One, продолж.) | 209 247 | 2020-07-08 | 2023-12-22 | Active | **2040-08-09 adjusted** | выдан 2025-08-19 |
| US11023967B1 (Capital One, Guidance engine) | 593 928 | 2019-11-12 | 2019-11-12 | Active | 2039-11-12 anticipated | MAFP 4-й год уплачена 2024-11-22 |
| US11669897B2 (Guidance engine, продолж.) | 599 617 | 2019-11-12 | 2021-05-18 | Active | **2040-01-10 adjusted** | выдан 2023-06-06 |
| US12008644B2 (Guidance engine, продолж.) | 624 118 | 2019-11-12 | 2023-04-20 | Active | 2039-11-12 anticipated | выдан 2024-06-11 |
| US11544780B2 (Intuit) | 340 650 | 2020-07-23 | 2020-07-23 | Active | 2040-07-23 anticipated | выдан 2023-01-03; MAFP на странице нет (3,5 года — 2026-07-03, льготный период до 2027-01-03) |
| CA3162417C (Intuit) | 170 576 | 2020-07-23 | 2021-05-24 | Active | 2041-05-24 anticipated | «MF (PATENT, 4TH ANNIV.) - STANDARD», уплачена 2025-05-16 |

Наблюдения:
1. **Терминальных дисклеймеров Google Patents не показывает**: строка «disclaimer» на всех 14 страницах
   встречается 0 раз. Отсутствие записи **не доказывает**, что дисклеймера нет; проверка — по файлам USPTO, ниже.
2. У продолжений US11861694B1, US11669897B2 и US12393978B2 Google выводит «adjusted expiration» ПОЗЖЕ, чем у родителя.
   При терминальном дисклеймере срок продолжения режется до срока родителя: либо дисклеймера нет, либо Google его
   не учитывает.
3. Отсутствие MAFP за 3,5 года у US11532041B2 и US11544780B2 — **не признак прекращения**: льготный срок открыт,
   события USPTO подтягиваются с задержкой, статус Active.
4. Иностранные номера на этих страницах (CN116361542B, RU2568289C2 и т. п.) — **цитируемые и похожие документы,
   а не члены семьи**. Семья — только по блоку стран: у USAA, Wells Fargo, Capital One страны = **только US**;
   у Intuit — **AU, CA, EP, US, WO**. Совпадает с Г3 и Г15.

### Г25.2(б) — терминальные дисклеймеры и PTA по титульным листам патентов (16.09.2026)

**Каналы.**
- USPTO Patent Center: `patentcenter.uspto.gov/retrieval/public/v2/application/data?...` → HTTP 200, 17 430 байт.
  Это оболочка SPA без данных.
- USPTO ODP: `api.uspto.gov/api/v1/patent/applications/17322968/transactions` → **HTTP 401 «Unauthorized»**,
  нужен API-ключ.
- ppubs: сессия `POST /api/users/me/session` → 200, токен получен; `GET /api/pdf/downloadPdf/<N>` →
  **400 «Validation failure»**; `image-ppubs.uspto.gov/.../downloadPdf/<N>` → **403**, 520 байт.
- **Сработало:** PDF выданного патента по ссылке со страницы Google Patents
  (`patentimages.storage.googleapis.com/.../US<N>.pdf`), затем `pdftotext` и OCR титульного листа
  (`pdftoppm -r 250` + `tesseract`). У части PDF нет текстового слоя, поэтому OCR обязателен.
  На титульном листе USPTO печатает поле «(*) Notice» с числом дней PTA и, если дисклеймер подан,
  строкой «This patent is subject to a terminal disclaimer».

| Патент | PDF: HTTP / байт | Notice, дословно (OCR) | TD | Итоговый срок с учётом TD |
|---|---|---|---|---|
| US11127075B1 (USAA, корень) | 200 / 1 293 163 | «…extended or adjusted under 35 U.S.C. 154(b) by 0 days.» | нет | **2039-09-27** |
| US11861694B1 (USAA) | 200 / 894 724 | «…154(b) by 186 days. … This patent is subject to a terminal dis[claimer]» | **да** | Google пишет 2040-03-31 (с PTA), но TD ограничивает срок сроком родителя: **не позже 2039-09-27** |
| US12141861B1 (USAA) | 200 / 882 690 | «…154(b) by 0 days. This patent is subject to a terminal dis- claimer.» | **да** | **2039-09-27** |
| US12524803B1 (USAA) | PDF не добыт (ниже) | — | не установлено | не позже **2039-09-27**: 20 лет от подачи US16/585,519, PTA у продолжения не может продлить срок за пределы TD, если он есть; без TD — 2039-09-27 + PTA |
| US11532041B2 (Capital One, debt mgmt, корень) | 200 / 2 209 093 | «…154(b) by 57 days.» | нет | **2040-09-03** (совпадает с Google) |
| US11893630B2 (Capital One) | 200 / 1 597 258 | «…154(b) by 0 days.» | на титуле не обнаружено | **2040-07-08** |
| US12393978B2 (Capital One) | PDF не добыт | — | не установлено | Google: **2040-08-09 adjusted** (32 дня PTA); при TD — 2040-07-08 |
| US11023967B1 (Guidance engine, корень) | 200 / 2 854 309 | «…154(b) by 0 days» | нет | **2039-11-12** |
| US11669897B2 (Guidance engine) | 200 / 2 160 594 | «…154(b) by 59 days. This patent is subject to a terminal dis- claimer.» | **да** | Google пишет 2040-01-10, но TD ограничивает срок: **2039-11-12** |
| US12008644B2 (Guidance engine) | 200 / 2 064 652 | «…154(b) by 0 days. This patent is subject to a terminal dis- claimer.» | **да** | **2039-11-12** |
| US12361480B1 (Wells Fargo) | PDF не добыт | — | корень семьи, TD маловероятен | Google: **2042-11-10** |
| US11544780B2 (Intuit) | 200 / 2 173 358 | «…154(b) by 0 days.» | нет | **2040-07-23** |

**Поправка к Г15.** В разделе «Меняется ли вывод» записано «US11669897B2 действует до ~2040-01-10». С учётом
терминального дисклеймера на титуле это **неверно: срок ограничен 2039-11-12**, то есть сроком US11023967B1.
Ошибка унаследована от поля Google «Adjusted expiration», которое **терминальный дисклеймер не учитывает**
(та же картина у US11861694B1). Оговорка: TD ограничивает срок тем патентом, над которым подан.
Здесь это предполагаемо корень семьи, потому что продолжения одной линии; номер «reference patent» по
титульному листу не определяется, он есть только в file wrapper.

**Не добыто — PDF US12524803B1, US12361480B1, US12393978B2.** На их страницах Google Patents нет ссылки на PDF,
только эскизы чертежей. Пройдено: `patentimages.../pdfs/US<N>.pdf` → 403 (385 б XML);
`image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/<N>` → 403 (520 б);
`ppubs.uspto.gov/api/pdf/downloadPdf/<N>` с токеном сессии → 400 «Validation failure», без токена → 401;
ODP → 401, нужен ключ. На вывод это не влияет: верхняя граница срока у всех трёх определяется
20 годами от приоритетной непровизорной подачи плюс PTA из Google.

### Г25.1 — семьи по юрисдикциям: Google Patents (DOCDB) + Patentscope (WIPO), 16.09.2026

**(а) Google Patents, те же 14 страниц, блоки «Country Status», «Also Published As», «Family Applications».**
Дословно, по одной странице от семьи:
- Intuit, ID=76502839: «Country Status (5) … US ( 1 ) US11544780B2 · EP ( 1 ) EP4049226A1 · AU ( 1 ) AU2021311376A1 ·
  CA ( 1 ) CA3162417C · WO ( 1 ) WO2022020000A1».
- USAA, ID=77749118: «Country Status (1) … US ( 4 ) US11127075B1»; «Family Applications (4)»: US16/585,519,
  US17/410,473, US18/393,397, US18/912,285, все «Active».
- Capital One Guidance engine, ID=75847618: «Country Status (1) … US ( 3 ) US11023967B1»; «Family Applications (3)»:
  US16/680,793, US17/322,968, US18/137,023.
- Capital One debt mgmt, ID=79172715: «Country Status (1) … US ( 3 ) US11532041B2»; «Family Applications (3)»:
  US16/923,405 «Active 2040-09-03», US18/057,522 «Active 2040-07-08», US18/394,321 «Active 2040-08-09».
- Wells Fargo, ID=96385853: «Country Status (1) … US ( 2 ) US12361480B1»; «Family Applications (2)»:
  US18/054,300 «Active», US19/264,619 «Pending».

**(б) Patentscope — впервые.** Канал: `curl -sk --http1.1` с UA и cookie сессии, сначала GET
`https://patentscope.wipo.int/search/en/search.jsf` (200, 50 772 б), затем GET
`https://patentscope.wipo.int/search/en/result.jsf?query=<запрос>` (200, 140–230 КБ).
Без cookie тот же адрес дал **400**, 8 024 б. POST формы `simpleSearchForm` возвращает страницу поиска
без выдачи, потому что результаты подгружает JS. `r.jina.ai` на том же адресе дал 200, 6 969 б, с выдачей;
это не Cloudflare, прокси здесь работает.

Выдача по семьям, все офисы сразу:

| Запрос | HTTP / байт | Всего | Документы |
|---|---|---|---|
| `FP:(Intuit debt reduction)` | 200 / 189 686 | 5 | WO2022020000, US, EP, CA, AU — совпадает с DOCDB |
| `ALLNAMES:("United Services Automobile Association") AND EN_ALL:("financial autopilot")` | 200 / 183 215 | 4 | только US (4) |
| `EN_ALL:("financial autopilot")` (без заявителя) | 200 / 181 372 | 4 | те же 4 US |
| `ALLNAMES:("Capital One") AND EN_ALL:("guidance engine")` | 200 / 177 416 | 3 | только US (3) |
| `ALLNAMES:("Capital One") AND EN_ALL:("debt management" AND "spending recommendation")` | 200 / 179 284 | 3 | только US (3) |
| `EN_TI:("financial health robo-advisor")` | 200 / 171 039 | 2 | только US: «12361480 … US - 15.07.2025» и заявка |

Заявители по юрисдикциям (`CTR:<XX> AND ALLNAMES:("<имя>")`):

| | Intuit | USAA (полное имя) | Capital One | Wells Fargo |
|---|---|---|---|---|
| RU | 0 | 0 | 0 | 0 |
| EA | 0 | 0 | 0 | 0 |
| KZ | 0 | 0 | 0 | 0 |
| CN | 30; с `EN_ALL:(debt)` — **0** | 2: «Toggling biometric authentication», «…switching biometric authentication…» — не по теме | 222; с `EN_ALL:(debt OR "financial guidance" OR "emergency fund")` — 1 документ (страница-редирект, карточка не разобралась) | 2: «International trade finance blockchain system» и одна ошибка атрибуции — не по теме |
| EP | 393; с `EN_ALL:(debt)` — 5, из них по теме только **EP4049226** (та же семья, отозвана) | 0 | 802; с `(debt management OR financial guidance OR emergency fund) AND debt` — **0** | 5, все не по теме (платежи 2003, blockchain 2019 и т. п.) |

**Проверка покрытия коллекций** (иначе ноль ничего не значит):
- EA: `CTR:EA AND DP:[01.01.2023 TO 31.12.2026]` → **12 423** документа, свежие евразийские заявки. Коллекция живая.
- KZ: `CTR:KZ AND DP:[01.01.2020 TO 31.12.2026]` → **722**. Коллекция есть, но небольшая.
- CN и EP: сотни документов тех же заявителей, коллекции живые.
- 🔴 **RU — покрытие неполное по ИМЕНАМ.** `CTR:RU AND DP:[2020–2025]` → 218 113 документов, коллекция есть.
  Но `CTR:RU AND ALLNAMES:("Samsung")` → 694 документа, все датированы 1998–2003, а в диапазоне 2015–2025 → **0**;
  `CTR:RU AND ALLNAMES:("Mastercard")` → **0**, хотя у Mastercard заведомо есть RU-патенты. Значит, у свежих
  RU-документов имена в Patentscope записаны кириллицей или не индексированы латиницей.
  **Нули в строке RU из Patentscope НЕ являются доказательством**; RU проверяется по Роспатенту, ниже.

### Г25.1(в) — RU и СНГ (EA, KZ): поисковая платформа Роспатента, полевой поиск по правообладателю (16.09.2026)

**Канал.** Анонимный `POST https://searchplatform.rospatent.gov.ru/search`, JSON; python urllib без проверки TLS,
российский корневой сертификат НЕ ставился. Два открытия этого батча:
1. 🔴 **Простой `q` по правообладателю НЕ ищет.** Контроль: `{"q":"\"МАСТЕРКАРД\""}` → total **1**, и это не
   документ Mastercard. Значит, прежние обратные поиски Г3 и Г15 «по именам правообладателей» через `q`
   были **слабее, чем выглядели**. Их нули верны по итогу, но доказательной силы не имели.
2. Полевой фильтр нашёлся в `bundle.js` веб-интерфейса (3 980 184 б): `"filter":{"patent_holders:search":{"search":"<имя>"}}`
   и `"applicants:search"`. Варианты `*_norm:search` на контроле дают 0, их не используем.
3. Набор **`cis`** существует: HTTP 200, в выдаче EA, KZ, UA, UZ, GE. Наборы `ea`, `kz`, `ea_since_1996`,
   `kz_since_1993`, `cis_since_1994` → 400 «Search on unknown dataset requested.»

**Контроли (фильтр рабочий):**

| Набор | Имя | patent_holders | applicants |
|---|---|---|---|
| ru_since_1994 | МАСТЕРКАРД | **70** (468 155 б) | 44 |
| ru_since_1994 | Mastercard | **45** (латиница тоже ищется) | 0 |
| ru_since_1994 | Samsung / САМСУНГ | 3 572 / 3 579 | 723 / 3 768 |
| cis | Samsung / САМСУНГ | **7** (EA 2, UA 1, UZ 3, KZ 1) | 3 / 5 |
| cis | Mastercard | 0 | 4 (UA) |

**Семьи-кандидаты.** Limit 100, обе поля, оба набора. Все ответы HTTP 200, пустые — 184–189 байт:

| Семья | Варианты имени | ru_since_1994 | cis |
|---|---|---|---|
| Intuit | Intuit · ИНТУИТ · ИНТЬЮИТ | **0 / 0** во всех вариантах | **0 / 0** |
| Capital One | Capital One · КЭПИТАЛ ВАН · КЭПИТАЛ УАН · КАПИТАЛ ВАН | **0 / 0** | 0 / 0; единственное попадание «Capital One» в cis — GE0000005507B «СВЕТОИНФОРМАЦИОННЫЙ МОДУЛЬ», правообладатель «ИНФОГЛАС ГРУП» — ложное |
| Wells Fargo | Wells Fargo · ВЕЛЛС ФАРГО · УЭЛЛС ФАРГО | **0 / 0** | **0 / 0** |
| USAA | United Services Automobile · USAA | **0 / 0** | **0 / 0** |
| USAA | ЮНАЙТЕД СЕРВИСЕЗ · ЮНАЙТЕД СЕРВИСИЗ · ОТОМОБИЛ | 20–42 попадания, **все чужие**: «ДЗЕ ЮНАЙТЕД СТЕЙТС ОФ АМЕРИКА, ЭЗ РЕПРЕЗЕНТЕД БАЙ…», «ЧУНЦИН ЧАНГАН ОТОМОБИЛ КО.», «ХУНАНЬ САНИ…»; биотех и автопром | 1–6 попаданий, **все чужие** (правительство США, Бавариан Нордик и др.) |

Текстовые запросы через `q` по номеру PCT `"PCT/US2021/033871"`, по `"financial autopilot"`, `"финансовый автопилот"`,
`"погашения долга" "резервного фонда"` дали **0** в обоих наборах.

**ФИПС (fips.ru)** отдельно не опрашивался. Поисковая платформа Роспатента — официальная ИПС того же ведомства
на тех же данных `ru_since_1994`. Реестры ФИПС ищут по номеру документа, а номера у нас нет, потому что
искомых документов нет.

**Вывод по RU/ЕАЭС.** Проверка на рабочем полевом фильтре, подтверждённом контролями: **ни одного документа
Intuit, Capital One, Wells Fargo или USAA нет ни в RU (с 1994), ни в наборе СНГ (EA, KZ и др.)**. Patentscope
по EA и KZ даёт те же нули (Г25.1(б)). Сроки подачи с правом приоритета тоже закрыты. PCT-заявка есть только у Intuit (WO2022020000):
её 31 месяц для входа в национальную фазу RU/EA истёк 2023-02-23, вход в фазу RU не зарегистрирован (Г3.1).
У остальных семей PCT-заявки нет, поэтому действует только 12-месячный срок Парижской конвенции:
USAA — до 2019-09-28 (приоритет 2018-09-28), Capital One Guidance — до 2020-11-12, Capital One debt mgmt —
до 2021-07-08, Wells Fargo — до 2023-11-10. Все сроки давно истекли. **Новый член в RU/EA/KZ с правом приоритета
этих семей появиться уже не может.** Более поздняя самостоятельная подача в РФ была бы опорочена собственными
публикациями заявителя в US: отсутствие новизны по ГК РФ ст. 1350.

## ИТОГ Г25

🔴 **Прямой ответ: НЕТ. Ни у одной семьи-кандидата нет члена, действующего в РФ или ЕАЭС (RU, EA, KZ), и
появиться такой член с правом приоритета уже не может: все сроки истекли.** Проверено тремя независимыми
путями: DOCDB-семьи Google Patents, Patentscope (EA/KZ/CN/EP) и полевой поиск по правообладателю на платформе
Роспатента (`ru_since_1994` + `cis`), подтверждённый контролями.

| Семья | RU | EA | EP | CN | KZ | Статус и расчётная дата истечения (US/CA) | Риск для нас |
|---|---|---|---|---|---|---|---|
| **Intuit** «Customized credit card debt reduction plans»: US11544780B2, CA3162417C (+ AU, WO) | нет | нет | EP4049226A1 — **отозвана** (deemed withdrawn, 2022-12-13), не выдана | нет | нет | US Active, PTA 0, TD нет → **2040-07-23**; пошлина 3,5 года на странице не отмечена, льготный срок до 2027-01-03. CA Active → **2041-05-24**, пошлина 4-го года уплачена 2025-05-16 | РФ/ЕАЭС — **нет**. US/CA — низкий: независимые пункты требуют обучаемой модели и переобучения на обратной связи |
| **USAA** «Financial autopilot»: US11127075B1, US11861694B1, US12141861B1, US12524803B1 | нет | нет | нет | нет | нет | все Active; корень PTA 0 → **2039-09-27**; US11861694B1 (PTA 186 дн.) и US12141861B1 — с **терминальным дисклеймером** → не позже 2039-09-27; US12524803B1 — TD не установлен (PDF не добыт), верхняя граница 2039-09-27 + PTA | РФ/ЕАЭС — **нет**. US — низкий: нейросеть предсказания расхода |
| **Wells Fargo** «financial health robo-advisor»: US12361480B1 + заявка US20250335982A1 | нет | нет | нет | нет | нет | B1 Active → **2042-11-10**; certificate of correction 2026-03-10; заявка **Pending** — формула может измениться при выдаче | РФ/ЕАЭС — **нет**. US — следить за выдачей продолжения: это единственный живой пункт |
| **Capital One** «debt management with spending recommendation»: US11532041B2, US11893630B2, US12393978B2 | нет | нет | нет (EP-выдача по теме: 0) | нет | нет | все Active; корень PTA 57 дн. → **2040-09-03**; US11893630B2 → 2040-07-08; US12393978B2 → 2040-08-09 по Google, TD не установлен; пошлина 3,5 года корня на странице не отмечена, льготный срок до 2026-12-20 | РФ/ЕАЭС — **нет**. US — низкий: чат-бот + ML |
| **Capital One** «Guidance engine» (без ML): US11023967B1, US11669897B2, US12008644B2 | нет | нет | нет | нет | нет | все Active; корень PTA 0 → **2039-11-12**, пошлина 4-го года уплачена 2024-11-22; US11669897B2 (PTA 59 дн.) и US12008644B2 — **с терминальным дисклеймером** → **2039-11-12** | РФ/ЕАЭС — **нет**. US — **самый близкий документ**: не оформлять рекомендацию деревом правил над четырьмя величинами (вывод Г15 в силе) |

**Что изменилось против Г15.**
1. 🔴 **Поправка срока:** US11669897B2 действует **до 2039-11-12, а не до ~2040-01-10**. Поле Google «Adjusted expiration»
   не учитывает терминальный дисклеймер, напечатанный на титульном листе. То же у US11861694B1: 2039-09-27, а не 2040-03-31.
   Общее правило для будущих записей: срок продолжений брать с титульного листа, а не из поля Google.
2. 🔴 **Методическая поправка к Г3/Г15:** обратный поиск по правообладателю через `q` на платформе Роспатента
   правообладателей не ищет (контроль «МАСТЕРКАРД» → 1). Прежние нули верны, что подтверждено сейчас полевым
   фильтром `patent_holders:search`, но тогда доказательной силы не имели.
3. Patentscope по RU ищет по латинским именам неполно (Samsung 2015–2025 → 0, Mastercard → 0). RU-нули из
   Patentscope как доказательство не использовать.
4. Пункты Г25.3 (формула CA3162417C) и Г25.4 (Banco de España) были закрыты ещё в Г3.1 и Г7. Постановка в
   COVERAGE_AUDIT_3 устарела.

**Осталось неизвестным (с причиной).**
- Терминальные дисклеймеры у **US12524803B1, US12393978B2, US12361480B1**. PDF титульного листа не добыт:
  на Google Patents нет ссылки, `patentimages/pdfs` → 403, `image-ppubs` → 403, `ppubs` с токеном → 400,
  ODP → 401 (нужен ключ). На вывод по РФ не влияет; на US влияет только верхней границей срока (±32 дня PTA).
- «Reference patent» у поданных дисклеймеров. Он есть только в file wrapper USPTO (Patent Center — SPA, ODP — по ключу).
  Предположение «ограничен корнем семьи» не проверено.
- Уплата пошлин за 3,5 года у US11532041B2 (срок 2026-06-20) и US11544780B2 (2026-07-03) на страницах Google не
  отмечена. Это не признак прекращения: льготные сроки открыты, статус Active.
- ФИПС (fips.ru) отдельно не опрашивался, его заменяет ИПС Роспатента на тех же данных.


---

## ДОБОР Г30.4 — Exa (16.09.2026)

**Состояние каналов (коды, 16.09.2026):** Exa search — работает; Exa fetch — `patents.google.com/patent/KR102121857B1/ko` → **HTTP 200, полное описание на корейском**; `patentscope.wipo.int/search/en/detail.jsf?docId=WO2026074314` → **HTTP 200, но тело пустое** (только заголовок «WIPO - Search International and National Patent Collections» — SPA/JSF-оболочка, как и предполагал Г15). Подагентов: 0. Закрытое позже не переоткрывалось: Banco de España (закрыт в Г7), формула CA3162417C (Г3.1), RU/EA-нули (Г25, три независимых пути). USPTO ODP не пробовался осознанно — класс «нужен ключ владельца».

### Г30.4-П1 — 🔴 MaPS: вычислимый индекс НАЙДЕН (Б.5 был «сегментация есть, вычислимого индекса не добыто»)

Г30.3 пробовал MaPS через Exa fetch и получил `CRAWL_NOT_FOUND`; здесь взят **другой способ — Exa search по методике, а не по адресу**, и он сработал.

**Индекс существует, называется FWB score, шкала 0–100, считается по девяти вопросам.** Первоисточники: `https://www.aston.ac.uk/sites/default/files/2024-04/maps_reg_presentation_150224.pdf` и полный отчёт `…/2024-10/cpfw2_financial_wellbeing_and_deprivation_full_data_report.pdf` (оба Exa, 200). Дословно: «In the 2021 Adult Financial Wellbeing Survey, **an overall financial wellbeing score (FWB score, hereafter) ranging from 0 to 100 is constructed based on respondents' answers to the 9 golden questions**»; «The MaPS identified **9 questions** that are important for measuring personal financial wellbeing»; «An aggregate score (FWB score) has been created based on 9 questions, ranging from 0 to 100».

**Девять «золотых вопросов» дословно:**
1. «Overall, how satisfied are you with your financial circumstances?» (B1/B2, шкала 0–10)
2. «How confident are you at managing your money?» (B3, 0–10)
3. «How well are you keeping up with your bills and credit commitments at the moment?» (J1, 1 «Without difficulties» … 5 «With difficulties»)
4. «What is the biggest unexpected bill that you could pay?» (I9 — «either from money you already have, or money you could easily borrow in a way that you consider affordable»)
5. «How often do you save?» (G3)
6. «How often do you have to use a credit card, overdraft or borrow money to buy food or pay bills, because you've run out of money?» (NORB1_2)
7. «How long could you last without borrowing if [you] lost [your] main source of income?» (OEQF13)
8. «To what extent do you agree that you understand enough to make decisions about retirement?» (WASOU/H6_2)
9. «How much of a plan do you have for retirement finances?» (D5C)

**Национальные референсные значения** (самый депривированный квинтиль UK → наименее депривированный, дословно из таблицы): удовлетворённость 6,6 → 7,5; уверенность 7,7 → 8,7; «Have difficulties keeping up with bills» **63 % → 35 %**; «Cannot pay any unexpected bill» **18 % → 6 %**; «Save every month» **32 % → 46 %**; «Borrow money to pay for essentials (very/fairly often)» **22 % → 13 %**; «Could last no more than a month without borrowing if they lost their main income» **35 % → 14 %**; «Understand enough to make decisions about saving for retirement» 39 % → 51 %; «Have a rough or clear plan for retirement» 37 % → 58 %.
Ключевой вывод исследования дословно: «The relationship between deprivation and financial wellbeing is **primarily driven by income-related elements, rather than attitudinal elements**, of financial wellbeing.»

**Сегментация — тоже добыта с определением** (`https://doc.ukdataservice.ac.uk/doc/8454/mrdoc/pdf/8454_maps_fin_wellbeing_segmentation.pdf`): «three 'macro' segments remain (i.e. the '**Struggling**', '**Squeezed**' and '**Cushioned**'). The under-pinning **sub-segments (14 in total)** have been updated»; переменные в данных — `maps_seg_macro`, `maps_seg_micro`; список микросегментов дословно: «1a Struggling Younger Adults, 1b Struggling Credit Dependent, 1c Struggling Making Do, 1d Struggling Retirees, 2a Younger Squeezed, 2b Squeezed Families, 2c Squeezed Pre-Retired, 2d Squeezed Retired, 3a Cushioned Still at Home, 3b Cushioned Younger…, 3c Cushioned Settled Families, 3d Cushioned Confident Older Families, 3e Cushioned Empty Nesters, 3f Cushioned Retiring». Модель построена MaPS совместно с **CACI** (первая версия — Money Advice Service + CACI, 2016), обогащена переменными закредитованности из Financial Need survey и пенсионными из FCA Financial Lives Survey.

🔴 **Что это меняет у нас.** (1) Пункт Б.5 закрывается: у MaPS **есть** вычислимая метрика, а не только сегментация; наша запись «вычислимого индекса не добыто» была следствием непройденного канала, а не отсутствия индекса. (2) Состав девяти вопросов **почти совпадает с контурами нашей модели**: вопросы 4, 6, 7 — это резерв и его достаточность; 3 — долговая нагрузка; 5 — норма сбережений; 9 — цели. То есть государственный индикатор благополучия в UK построен на тех же трёх контурах, между которыми распределяет FINPILOT. Для обоснования выбора контуров это лучшая внешняя опора из добытых за кампанию — государственный стандарт, а не продукт конкурента. (3) 🔴 Оговорка о применимости: вопросы **субъективные** (самооценка по шкале 0–10), а у нас вход объективный (суммы, ставки, сроки). Индекс годится как **рамка обоснования выбора контуров и как шкала отчёта пользователю**, но не как формула расчёта. (4) Преемственность: «For 2025, the Financial Wellbeing Survey has been superseded by **MoneyView**» (12 000+ взрослых) — при ссылках на UK в юрблоке и в обосновании брать актуальное название.

### Г30.4-П2 — 🟡 KR102121857B1: корейский оригинал снят, формулы в нём нет, но раскрытие содержательно

Г15 записал: «на английской странице `claims` пуст (0 пунктов), корейский оригинал **не запрашивался**» — непроверенный пункт. Запрошен: `https://patents.google.com/patent/KR102121857B1/ko` → **HTTP 200**, полное описание на корейском.

Реквизиты дословно: «재무설계 서비스 제공 방법» («Метод предоставления услуги финансового планирования», англ. «METHOD FOR PROVIDING FINANCIAL DESIGN SERVICE»); заявка `KR1020180050923A`; изобретатель 박세라; заявитель **주식회사 런인베스트** (RunInvest Co., Ltd.); приоритет и подача **2018-05-02**; выдача **2020-06-11**; «Status **Active**»; «**2038-05-02** Anticipated expiration».

Формула изобретения (`claims`) **в корейской версии тоже не размечена** — Google Patents для этой публикации отдаёт описание, но не пункты. Однако описание содержит структуру решения дословно: «저장부가 고객에 대한 적어도 하나 이상의 고객 정보를 입력 받아 저장하는 단계» (блок хранения принимает и сохраняет информацию о клиенте); «통합부가 **스크래핑 기술**을 기반으로 상기 고객이 가입한 적어도 하나 이상의 금융 상품을 수집하여 리스트로 통합하는 단계» (блок интеграции **на основе технологии скрейпинга** собирает финансовые продукты клиента в единый список); «분석부가… 상기 고객의 재무 상태를 분석하는 단계» (анализ финансового состояния); «설계부가 상기 분석된 재무 상태를 기반으로 **적어도 하나 이상의 목적에 따라** 재무설계를 수행하는 설계 단계» (планирование **по одной или нескольким целям**); состав входных данных: «고객 정보는 인적사항, 가족정보, **자산 및 부채 현황**을 포함할 수 있다» (персональные данные, сведения о семье, **состояние активов и обязательств**).

🔴 **Существенно: в перечне фигур прямо назван долговой контур наряду с прочими** — «도 6a… **보장설계**» (страховое планирование), «도 6b… **은퇴설계**» (пенсионное), «도 6c… **부채설계**» (**планирование долга**), «도 6d… **종합설계**» (комплексное планирование). То есть документ 2018 года описывает **систему, которая по данным об активах и долгах, собранным скрейпингом, строит планы по нескольким целям, включая долговой**. Мотивация автора дословно: прежние программы «통합적 재무관리가 아니라 개별관리… 를 위한 목적으로 이용되고 있는 실정이다» (используются не для интегрированного, а для раздельного управления) — то же наблюдение, что и наше, сделанное в 2018-м в Корее.
🟡 **Риск для нас — низкий и локализованный.** Семья **только KR** (Г15), срок до 2038-05-02, действие ограничено Кореей; права в РФ она не создаёт. Но как **свидетельство приоритета идеи** документ значим: постановка «интегрированное планирование по нескольким целям, включая долг, из агрегированных данных» публично известна с 2018 года. **Вывод для формулировки новизны: на постановку задачи опираться нельзя, опора — только на метод (детерминированный расчёт распределения на множестве альтернатив с инвариантами).** Это тот же итог, что у Г30.1 и Г30.3, теперь подтверждённый и с корейской стороны. 🔴 Формула (объём притязаний) не добыта: каналы — Google Patents `en` (claims 0), **Google Patents `ko` (claims не размечены)**; остаются KIPRIS (`kipris.or.kr`, в этом доборе не пробовался) и корейский PDF.

### Г30.4-П3 — WO2026074314A1 (1Finance, Индия): ❌ не добыто, канал Patentscope подтверждённо непригоден

`patentscope.wipo.int/search/en/detail.jsf?docId=WO2026074314` через Exa → **HTTP 200, тело пустое** (только `<title>`). Это подтверждает гипотезу Г15 («Patentscope ранее давал оболочку без карточки»): страница строится JSF-скриптом после загрузки, и краулер получает каркас. Полный перечень пройденных каналов по формуле этого документа: Google Patents (200, 149 331 байт, секция `claims` — **0 пунктов**) → **Patentscope через Exa (200, пусто)**. Непройденное: национальные публикации семьи после входа в нацфазу (их ещё нет) и PDF-скан публикации WO. 🔴 **Срок слежения не меняется: 31-месячный срок входа в нацфазу RU истекает около 2027-05-02** — это единственный документ кампании, способный создать права в РФ, и он остаётся под наблюдением.

### Г30.4-П4 — Терминальные дисклеймеры US12524803B1 / US12393978B2 / US12361480B1: ❌ не пробовалось, класс «нужен владелец»

По прямому указанию задания не обходилось. Фиксирую состав препятствия как есть (из Г25): PDF титульного листа на Google Patents ссылки не имеет; `patentimages/pdfs` → 403; `image-ppubs` → 403; `ppubs` с токеном → 400; **USPTO ODP → 401, требуется API-ключ**. Ключ оформляется на заявителя — это действие владельца, а не исследователя. На вывод по РФ не влияет (в РФ членов семей нет вовсе), на US влияет только верхней границей срока ±32 дня PTA.

---

## ИТОГ Г30.4

**Файлов тронуто: 7. Подагентов: 0. Каналов добычи: Exa search + Exa fetch (основной), `curl -sk --http1.1` с браузерным UA (одна проверка RePEc-адресов).**

| Файл | Полностью добыто | Частично | Нет, с причиной |
|---|---|---|---|
| `desktop_web_catalogs_sweep` | К1 Capterra, К3 Lunch Money, К4 Empower, К5 DebtMeltPro, К6 Ray, К7 Maybe, К8 ЦФТ — **7** | К2 G2 (смежные страницы вместо категории) | К9 чарты Mac App Store (канала нет), К10 winget (нужен токен) |
| `app_stores_advisors_sweep` | А1 Toya AI, А2 Bright Money — **2** | — | А3 «Без Долгов» (нужна установка APK), А4 описания Google Play и листинг RuStore (ограничение канала) |
| `ru_auto_import_workarounds` | И1 политика Google по уведомлениям, И2 4PDA (канал открыт, содержимого нет), И3 требования RuStore — **3** | — | — |
| `telegram_channel` | Т1 охват TGStat, Т2 CPM финниши, Т3 экономика каналов — **3** | — | Т4 конверсия «канал → подписка» в РФ |
| `rf_household_finance_stats_v2` | С1 ложь RePEc о доступе, С2 содержательные аннотации 4 статей + открытый полный текст IJEBA 2019 + новая статья Мишура 2025 № 5 — **3** | полные тексты «Вопросов экономики» (аннотации есть, статьи нет) | SSRN Синякова (`CRAWL_LIVECRAWL_TIMEOUT`) |
| `debt_data_sources_rf` | Д1 Debt Payoff Planner (§4.4 был чистым непроверенным), Д2 Скоринг Бюро — **2** | — | Д3 ОКБ (четвёртый канал тоже не взял) |
| `bank_patents_wellness_scoring` | П1 MaPS FWB score 0–100 и 9 вопросов, П2 KR102121857B1 корейский оригинал — **2** | П2 формула KR не размечена и в `ko` | П3 WO2026074314A1 (Patentscope — оболочка), П4 терминальные дисклеймеры (нужен ключ владельца) |
| **ИТОГО** | **22 полностью** | **3 частично** | **8 нет, каждый с перечнем пройденных каналов** |

🔴 **Ошибка «отказ инструмента записан как отсутствие источника» — встретилась 9 раз:** Capterra («закрыты для всех каналов» → Exa отдала 200), Lunch Money (403 → 200), Empower (404 → **адрес был неверен**, `/financial-tools` вместо `/tools`), ЦФТ (`cft.group` не резолвится → вендор живёт на `cft.ru`), 4PDA (заглушка 1 932 Б → 200 с содержимым), `requirement-apps` RuStore («страница не снята» → снята), TGStat (403/401 → 200 с числами), `scoring.ru/credit-history` («страница не снята» → снята), MaPS («вычислимого индекса не добыто» → индекс есть, 9 вопросов, шкала 0–100). Плюс **два непроверенных пункта, где запросов не делалось вовсе**: §4.4 Debt Payoff Planner (прямо записано «бюджет исчерпан, кодов ответа нет») и корейский оригинал KR102121857B1.
🔴 **И один обратный случай — источник соврал об открытости:** RePEc печатает «Download Restriction: **no**» для статей «Вопросов экономики», а адрес `/viewFile/<id>/<file>` отдаёт **HTTP 302** на форму входа. Проверено дважды. Метаданные RePEc об открытости у этого издателя недостоверны.

### 🔴 СВОДКА ПО ВСЕМУ Г30 (подбатчи 1–4)

| Подбатч | Результат |
|---|---|
| Г30.1 наука-метод | **18** пунктов «не добыто» стали добытыми; среди них первоисточник, доказавший, что наш Avalanche не оптимален |
| Г30.2 макро и поведение | **10 полностью + 5 частично**; ошибка «отказ = нет источника» — **3 раза** |
| Г30.3 рынок и право | **22 полностью + 8 частично + 6 нет**; ошибка — **8 раз**; сверх очереди 6 новых пунктов |
| Г30.4 каталоги и каналы | **22 полностью + 3 частично + 8 нет**; ошибка — **9 раз** + 2 пункта, где запросов не делалось вовсе |
| **ВСЕГО** | 🔴 **72 пункта переведены из «не добыто» в добытые, 16 частично. Ошибка «отказ инструмента = отсутствие источника» встретилась 20 раз за четыре подбатча.** |

**Что из Г30.4 меняет канон, прогноз, новизну или юрблок** (правок в канон, формулировку новизны и код НЕ вношу — это материал для решения владельца):

1. 🔴 **Новизна — по объекту держится, по методу в долговом контуре сужается дальше.** За один подбатч разобраны **четыре** продукта, заявляющих метод сверх пары snowball/avalanche или близких к нашей постановке: **Ray** (формулирует ровно нашу задачу — «pause the Japan fund and throw that $440/mo at the Chase card», но решает генерацией LLM, не расчётом), **DebtMeltPro** (гибрид «ставка + размер остатка», правило качественное), **Debt Payoff Planner** (snowball/avalanche/custom с тремя пользовательскими порядками), **Toya AI**. Все **одноконтурные или недетерминированные**. 🔴 **Поправка к Г30.3: Toya AI не «не просто snowball или avalanche»** — её собственный FAQ описывает минимизацию процентов, то есть avalanche со сроками платежей. Ближайший по постановке — Ray, и у него под LLM **есть** детерминированный инструмент `calculate_debt_payoff`, а сообщество достроило форк с «deterministic debt payoff simulators». Формулировку новизны следует держать на **детерминированном распределении одного потока между тремя контурами на множестве альтернатив с инвариантами**, и явно отличать её от «LLM-советника с калькулятором под капотом».
2. 🔴 **Опора канона на российских микроданных.** Арженовский (ЦБ РФ, «Вопросы экономики» 2025 № 12): домохозяйства «prefer to reduce consumer spending in order to direct the **freed-up income to debt servicing and/or savings**» — по теории буферного запаса Кэрролла. Наша постановка «делить свободный поток между долгом и резервом» описана в литературе как **фактическое поведение россиян**, а не как инженерная конструкция. Плюс Мишура и др. 2025 № 5: потребкредит в РФ — фактор **дополнительной волатильности** потребления, половина эффекта отыгрывается за два года.
3. 🔴 **Обоснование выбора трёх контуров — государственный стандарт UK.** MaPS FWB score (0–100, 9 вопросов): резерв и его достаточность (вопросы 4, 6, 7), долговая нагрузка (3), норма сбережений (5), цели (9). Внешняя, не продуктовая, опора выбора контуров.
4. 🔴 **Калибровка и прогноз.** Абдураманов–Кузина: связь финграмотности со сбережениями **работает на вкладах и НЕ работает на фондовых инструментах и наличных** — дефолт резерва держать на депозите. Ниворожкина–Арженовский (IJEBA 2019, открытый полный текст): **единица наблюдения — домохозяйство, не человек** (гипотеза о важности индивидуальных характеристик не подтвердилась), и **скрытые доходы систематически занижены именно у плательщиков по кредитам** — предупреждение для калибровки на анкетных доходах.
5. 🔴 **Юрблок и продуктовые ограничения (новое, Google/RuStore):** `NOTIFICATION_LISTENER` и `READ_SMS` в приложении, установленном **мимо магазина**, → **Play Protect блокирует установку автоматически**; учёт финансов в списке разрешённых применений доступа к уведомлениям **отсутствует**; политика Google прямо относит к финансовым услугам «management or investment of money… **including personalized advice**» с обязательной декларацией; RuStore **запрещает чистую WebView-обёртку**. Это ограничения площадок, независимые от права РФ, но совпадающие с ним по смыслу.
6. 🟡 **Маркетинг-план: два числа требуют пересчёта.** Охват органического финансового Telegram-канала — **4–8 % подписчиков** (медиана 8,8 % по 18 каналам TGStat), а не 30 %; воронка, посчитанная на 30 %, завышает верх в 4–7 раз. CPM финансовой ниши — рабочий коридор **2 000–3 000 ₽**, цена поста в канале 10–50 тыс. подписчиков — **20 000–60 000 ₽**, +20–40 % в ноябре–декабре. Плюс: владелец канала платит **3 % рекламного сбора**, а наш расход на рекламу в Telegram налог на прибыль не уменьшает (Г7.4.0) — рынок обложен с обеих сторон.
7. 🟡 **Экономика класса продукта.** Maybe Finance: **200 платящих при 6 000 до безубыточности**, $400 000 в банке, 9 месяцев рантея, вывод основателя — «либо bootstrapped годами, либо десятки миллионов финансирования». Bright Money **выжил, сменив объект** на брокера кредитных предложений; Empower — на управление активами; ReadyForZero — продан Avant. 🔴 Все три выжившие траектории ведут в посредничество при продаже финпродуктов, а этот путь нам закрыт темами 18/19. Пустота ниши «чистый советник на подписке» объясняется экономикой, а не недосмотром рынка.

### ЗАДОЛЖЕННОСТЬ Г30.4 (непройденное, отдельным списком — не выдаётся за результат)

1. **Формула WO2026074314A1** (1Finance) — Google Patents `claims` 0, Patentscope через Exa пуст. Непробованное: PDF-скан публикации WO, национальные публикации после входа в нацфазу. **Следить до ~2027-05-02.**
2. **Формула KR102121857B1** — не размечена ни в `en`, ни в `ko`. Непробованное: **KIPRIS** (`kipris.or.kr`), корейский PDF.
3. **SSRN 10.2139/ssrn.5043646** (Синяков и др., «Financial Literacy and Responsible Financial Behaviour of Russian Households») — Exa fetch `CRAWL_LIVECRAWL_TIMEOUT`, повтор не делался. Вероятно, та самая линия Синякова, которую искал Г17.8.
4. **«Без Долгов»** — главная неопределённость Г13 не разрешима без установки APK. Действие владельца.
5. **ОКБ (`bki-okb.ru`)** — четыре канала исчерпаны, нужен headless-браузер.
6. **Конверсия «Telegram-канал → подписка финприложения» в РФ** — числа не существует ни в одном пройденном канале.
7. **Bonus Money и «Финансовая грамотность» из реестра ПО РФ** — страницы не открывались, классификация по названию (наследие Г14, в этом доборе не трогалось).
8. **Терминальные дисклеймеры трёх US-патентов** — требуется ключ USPTO ODP. **Действие владельца, обходить запрещено заданием.**

---

## ДОБОР Г31.2 — прокси (16.09.2026)

**Каналы на начало работы (парный замер, 16.09.2026):** `r.jina.ai` **без браузерного UA** на
`www.monarchmoney.com/pricing` → **HTTP 200, 5 509 байт** содержимого; тот же адрес через тот же
прокси **с UA Chrome/127** → **HTTP 403, 5 743 байта**, тело `<title>Just a moment...`.
🔴 Ошибка вызова прокси с UA подтверждена прямым замером. Exa (`mcp__exa__*`) — 🟢;
`curl` c UA — 🟢; **Wayback replay (`web.archive.org/web/<год>/<URL>`) — 🟢 работает**
(служебный CDX/API в предыдущих батчах лежал — это разные вещи).

### Г31.2-3. 🔴 MaPS Financial Fitness Tool — ВСЕ ДЕВЯТЬ ВОПРОСОВ ДОБЫТЫ ДОСЛОВНО (был отказ по четырём каналам)

**Прежний статус** (таблица «Что не добыто», строка 1274 этого файла и Г24.8(б) в
`competitors_2026_refresh_2026-09-12.md`): «`WebFetch` maps.org.uk → 403; `r.jina.ai` → 200, тело =
антибот-верификация; Б.5 остался на уровне сегментации; формулы FFT нет»; в Г24 добавлено
«`curl`+UA → PDF 403, 6 028 б; `r.jina.ai` → 200/542–555 б `Just a moment... This page maybe
requiring CAPTCHA`; Wayback лежит»; в Г30.3 — «Exa их не индексирует». **Сами 9 формулировок —
числились не добытыми.**

**Каналы 16.09.2026, по порядку:**

| Канал | Адрес | Код | Размер | Итог |
|---|---|---|---|---|
| `r.jina.ai` **без UA** | `…/maps-financial-fitness-tool-questionnaire.pdf` | 200 у прокси | **558 б** | тело `Title: Just a moment... / Warning: This page maybe requiring CAPTCHA` — 🔴 **не пробил; без UA результат тот же, что с UA** |
| `r.jina.ai` **без UA** | блог `…/how-we-developed-the-financial-fitness-tool` | 200 у прокси | **555 б** | то же, капча |
| `mcp__exa__web_fetch_exa` | блог | 200 | полный текст | 🟢 **добыто** (методика построения) |
| `mcp__exa__web_fetch_exa` | PDF опросника | — | — | `CRAWL_UNKNOWN_ERROR` |
| **Wayback replay** `web.archive.org/web/2024/<URL>` | PDF опросника | **HTTP 200** | **280 649 байт PDF** → `pdftotext -layout` → 13 665 знаков | 🟢 **ДОБЫТО ЦЕЛИКОМ**. Снимок **23.06.2024 20:21:43 GMT**, `x-archive-orig-last-modified: 12.04.2024 13:29:34 GMT` |

🔴 **Класс ошибки:** это НЕ ошибка вызова прокси (без UA прокси даёт ту же капчу Cloudflare —
значит защита у самого `maps.org.uk`, а не у прокси). Это **«отказ инструмента записан как
отсутствие источника»** по Wayback: в Г24 записано «Wayback лежит», и на этом пункт закрыли;
Wayback replay сегодня отдаёт файл с первого запроса.

#### Первичный материал — ДОСЛОВНО, PDF «Money and Pensions Service (MaPS) Financial Wellbeing Key Questions»

Служебная разметка документа (дословно):
> «Key / Blue – question numbers do not display to people answering the questions / RED –
> instructions, do not display to people answering the questions / Black Bold – Intro text to the
> demographics section to explain why it's there, display»

Вводная страница (дословно):
> «MAPS WILL NOT RECEIVE ANY PERSONALLY IDENTIFIABLE DATA. PARTNER ORGANISATIONS MAY ASK FOR THIS
> IF THEY FEEL IT'S NEEDED / USEFUL. IF SO THEY MUST TAKE THE NECESSARY STEPS IN TERMS OF DATA
> PROTECTION AND INFORMING RESPONDENTS.»
> «The Money & Pensions Service (MaPS) helps people manage their money… Once you've filled it in
> you will be given your **Financial Wellbeing score out of 100** and some links for useful
> information… The survey should take you **no more than 10 minutes** to complete.»

**Вопросы, дословно, с кодами и шкалами:**

1. **B1** — `ASK ALL, SINGLE CODE` 🔴 `NB THIS IS A WARM UP QUESTION - NO SCORING`:
   «How satisfied are you with your life nowadays?» — «Please answer on a scale of 0 to 10, where
   0 is 'not at all satisfied' and 10 is 'completely satisfied'». Коды 1–11 плюс «Don't Know» = 12.
2. **B2** — «How satisfied are you with your **overall financial circumstances**?» — та же шкала 0–10.
3. **B3** — «How **confident** do you feel managing your money?» — 0–10, «0 is 'not at all confident'
   and 10 is 'very confident'».
4. **J1** — «How well are you **keeping up with bills and credit commitments** at the moment?
   Are you…»; 🔴 инструкция: «IF POSSIBLE ALTERNATE THE ORDER THAT THE ANSWER CODES APPEAR…
   Answers – **50% selected at random** see codes in this order» — то есть порядок вариантов
   рандомизируется между респондентами, а коды 1…5 сохраняются. Варианты: «keeping up with all
   bills and commitments without any difficulties» (1) · «…but it is a struggle from time to time»
   (2) · «…but it is a constant struggle» (3) · «falling behind with some bills or credit
   commitments» (4) · «having real financial problems and have fallen behind with many bills or
   credit commitments» (5); плюс FIXED-коды 6 «Not applicable – don't have any bills or credit
   commitments», 7 «Don't know», 8 «Prefer not to say».
5. **I9** — «Imagine you/you and your partner have to pay an **unexpected bill within the next seven
   days** from today. What is the biggest bill you… could pay, either from money you already have,
   or money you could **easily borrow in a way that you consider affordable**? If you don't know the
   exact amount your best guess is fine.» Варианты: «None – I couldn't pay an unexpected bill» ·
   £50 · £100 · £300 · £500 · £1,000 · £2,500 · £5,000 · £10,000 · Don't know · Prefer not to say.
6. **G3** — «Which of these best describes **how often you usually save money**?»: Every month (1) ·
   Most months (2) · Some months, but not others (3) · Rarely/never (4) · Don't know (5).
7. **NORB10** — «How often do you **use a credit card, overdraft or borrow money to buy food or pay
   bills because you've run short of money**?»: Very often (1) · Fairly often (2) · Sometimes (3) ·
   Not very often (4) · Never (5) · Don't Know (6).
8. **OEQF13** — «If you **lost your main source of household income**, how long could your household
   continue to cover living expenses **without having to borrow any money or ask for help** from
   friends or family?»: Less than a week (1) · More than one week but less than a month (2) · More
   than a month but less than three months (3) · More than three months but less than six months (4)
   · **6 months or longer (5)** · Don't Know/prefer not to say (6).
9. **WASOU** — «Do you agree or disagree with the following statement? **I feel I understand enough
   about pensions to make decisions about saving for retirement**»: Strongly agree … Strongly
   disagree (1–5), Don't know (6).
10. **D5C** — «**How much of a plan do you have for your finances in retirement?**»: Clear plan (1) ·
    Rough plan (2) · Not much of a plan (3) · No plan at all (4) · Don't know (5).

**Демография (дословно, опциональная):** «IT IS UP TO THE ORGANISATION TO DECIDE WHAT DEMOGRAPHIC
QUESTIONS ARE APPROPRIATE FOR THEIR USE CASE. THESE ARE SUGGESTED / OPTIONAL QUESTIONS…»
A1 возраст (число) · A1a «Which of the following describes how you think of yourself?» (Male/Female/
In another way/Prefer not to say) · A5 форма владения жильём (7 вариантов + DK/PNTS, включая
«Own it with a mortgage», «Part own / part rent (shared ownership)») · HH4 «How many children aged
17 or under are financially dependent on you and / or your partner/spouse…» (0–20).

#### Методика построения FFT — дословно с блога MaPS (Exa, 200), опубликовано 12.04.2024

> «In 2022, we undertook analysis to create a set of nine focused questions…»

Пять шагов отбора (дословно):
> «Step 1: … only use those Enablers/Inhibiters and Behaviours that were **highly correlated** to
> either the "current financial wellbeing" or the "long term wellbeing" outcome blocks. This yielded
> **10 building blocks, comprising 42 measures**.»
> «Step 2: Using a **correlation matrix**, we screened this list further to remove **seven
> outliers**. This returned **35 measures**.»
> «Step 3: We tested the **scale reliability**… and went through successive reduction stages to
> maximise the **Cronbach's Alpha, at 0.92**. The result was an optimum set of **22 questions**…»
> «Step 4: … we created a simple overall **composite score** from the 22 questions, then used
> **step-wise regression** to find the questions that could most efficiently reflect the longer
> composite score.»
> «Step 5: Using an element of **judgement** to ensure that we covered the actual National Goals…
> we settled on **nine questions** that still retained a high Cronbach's Alpha, of **0.81**… We also
> aimed to ensure that the shortlisted questions aligned to the narrative definition of financial
> wellbeing, and were **income neutral**, if possible.»

🔴 **Принципы взвешивания — четыре, дословно (раньше в файле отсутствовали вовсе):**
> «Try to give **equal weight** to questions, except where valid rationale suggests merits for
> higher or lower weight»
> «**Higher weight for questions which are more like "Outcomes"** rather than behaviours or enablers»
> «Higher weight for questions with **longer answer code options** (to minimise the sensitivity of
> adjoining answer code options)»
> «Aim to yield a **non-skewed** summary statistic by scaling scores such that the **median answer
> code option was aligned to the mid-point of the item's maximum score**»

> «This scoring yields results on a scale of **0 to 100**, where the middle is close to the average
> of the UK population (i.e. around half the population would score under 50 and around half over 50).»
> «Our hope is that this new measure will help organisations **avoid re-inventing the wheel**…
> Should organisations wish to adopt the nine questions, then please get in touch with us via your
> MaPS regional partnership manager.»

Исходная база: «the building blocks comprise **over 80 different elements**»; данные — «our **2021
Adult Financial Wellbeing Survey**»; оценки доведены до «lower tier local authority, and
parliamentary constituency».

#### Выжимка — что меняется в блоке Б.5

1. 🟢 **Вывод Г7/Г24 подтверждён и теперь доказан первоисточником:** FFT — **субъективный
   опросник**, ни один из девяти вопросов не вычисляется по транзакциям. Три вопроса из девяти —
   прямо про наши контуры: **J1** (долговая нагрузка), **I9** (буфер на непредвиденный расход,
   включая «сколько мог бы занять по приемлемой цене»), **OEQF13** (сколько месяцев проживёт
   домохозяйство без дохода — это **наш резерв в месяцах расходов**, с верхней ступенью «6 months
   or longer»). Плюс **G3** — регулярность сбережений, **NORB10** — заём на еду и счета как маркер
   кризиса.
2. 🔴 **Внешняя, не продуктовая опора для выбора порога резерва.** Государственный британский
   инструмент меряет резерв **в месяцах покрытия расходов без займов и помощи**, с потолком шкалы
   на **6 месяцах**. Наш дефолт резерва оказывается в том же диапазоне, что и верхняя ступень
   национальной шкалы. Это аргумент в §обоснование целевого резерва, не правка канона.
3. 🔴 **Приём валидации, применимый к нашему опроснику:** сжатие длинного набора регрессией с
   контролем α Кронбаха (0,92 на 22 → 0,81 на 9) и **явные четыре принципа весов**, среди которых
   «выше вес исходам, ниже — поведению и enablers» и «шкалировать так, чтобы медианный вариант
   попадал в середину максимума». Последнее — готовая формулировка для защиты нашей нормировки
   от упрёка «шкала перекошена».
4. 🟡 **Чего в документе НЕТ:** числовых весов по каждому из девяти вопросов. Опубликованы
   принципы и шкала, но не таблица баллов (в PDF колонка «Points / Scoring» присутствует как
   заголовок, но **не заполнена** — заполняет организация-партнёр по методике MaPS).
   Точные веса — только по запросу к MaPS («get in touch… via your MaPS regional partnership
   manager»). Это остаётся не добытым и **не поисковая задача**.
5. ⚪ **Юрблок:** переиспользование девяти вопросов MaPS предполагает обращение к MaPS; документ
   прямо предупреждает партнёров об их собственной ответственности за защиту данных. Если мы
   когда-нибудь возьмём формулировки — это лицензионный вопрос, а не технический.

### Г31.2-4. Перепроверенные и НЕ сдвинувшиеся пункты этого файла

| Пункт | Каналы 16.09.2026 | Итог |
|---|---|---|
| **Economic Record 2022, Comerton-Forde et al.** (журнальная версия, CC BY-NC по Unpaywall) | `r.jina.ai` **без UA** на `onlinelibrary.wiley.com/doi/10.1111/1475-4932.12664` → **200 у прокси, 515 б**, «Just a moment… This page maybe requiring CAPTCHA»; то же на `/doi/pdfdirect/…` → **200, 525 б**; `mcp__exa__web_fetch_exa` → **`CRAWL_LIVECRAWL_TIMEOUT`** | ❌ не добыт. 🔴 **Не наша ошибка вызова:** без UA прокси даёт ту же капчу. Cloudflare Wiley. Остаётся действие владельца — одно скачивание PDF по DOI в браузере |
| **SSRN 3734752** (published version той же работы) | `r.jina.ai` **без UA** → **200 у прокси, 491 б**, «Just a moment… CAPTCHA» | ❌ не добыт; SSRN закрыт Cloudflare и без UA |
| **Реестр Роспатента / ФИПС** | не переоткрывался в этом подбатче | блокировка **по сети** (DDoS-Guard: «restricted access from your current network»), а не по UA — прокси этого класса не лечит; нужен доступ из РФ-сегмента или платный сервис |
| **CBA–MI Tech Reports № 2, 3, 5** | не переоткрывались | прежний замер показал **страницу логина Okta University of Melbourne** — это авторизация, а не антибот; прокси авторизацию не обходит |
| **Патенты WO2026074314A1 / KR102121857B1** | не переоткрывались | задолженность Г30.4, требует KIPRIS / PDF-скана WO, не прокси |

## ИТОГ Г31.2 — bank_patents_wellness_scoring

- Закрыт **1 пункт**, и он из числа самых давних: **MaPS FFT, все девять вопросов дословно
  плюс четыре принципа взвешивания**. Канал — **Wayback replay** (снимок 23.06.2024) после отказа
  прокси и Exa.
- **Нашей ошибкой вызова прокси не оказался ни один** пункт этого файла: без UA `maps.org.uk`,
  Wiley и SSRN отдают ту же капчу Cloudflare.
- 🔴 **Ошибка «отказ инструмента = отсутствие источника» — 1 раз** (Г24: «Wayback лежит» → сегодня
  Wayback отдаёт PDF с первой попытки). Это тот же класс, что вскрыл Г31.1.

---

## ДОБОР Г31.5 — отказ адреса (17.09.2026)

**Каналы (замер 17.09.2026):** прямой `curl -skL` с UA на `patents.google.com` **200** (оба документа) · `patentimages.storage.googleapis.com` **200** · Exa — в этом заходе не понадобилась. Разбор HTML — `python3` + регулярные выражения по `<section itemprop="claims">`.

Кандидаты — задолженность Г30.4 (стр. 2947–2955) и строка Г31.2 (стр. 3127): п. 1 формула WO2026074314A1, п. 2 формула KR102121857B1, п. 3 SSRN 5043646. Все три записаны как «не размечено / канал непригоден» по итогам одного способа чтения.

### Г31.5-K1. 🔴🟢 WO2026074314A1 (1Finance) — ФОРМУЛА ДОБЫТА ЦЕЛИКОМ, запись «0 пунктов» была ошибкой чтения

- `https://patents.google.com/patent/WO2026074314A1/en` — **HTTP 200, 149 331 б** — 🔴 **ровно тот же размер, что в Г15/Г30.4** (стр. 2527: «HTTP 200, 149 331; 0 пунктов в разметке `claims`»). Страница не менялась: секция `<section itemprop="claims">` в ней **есть и содержит 11 440 знаков, 22 пункта**. Прежний вывод опирался на счётчик разметки (или на markdown Exa), а не на текст секции. sha256 HTML `e48182eb206f3bfdb78bbcef62ea160e8ef43ec5c94d293c10fa5da81217440a`.
- Реквизиты со страницы: PCT/IB2024/060096; приоритет **2024-10-02**; подача 2024-10-15; публикация **2026-04-09**; ожидаемая дата в карточке 2027-04-02; изобретатели Animesh Hardia, Keval Bhanushali; «Method and system for recommending a financial plan».

**Пункт 1 ДОСЛОВНО:** «1. A computer-implemented method for providing a financial plan to a user, the method comprising: receiving, by one or more processors, a plurality of inputs related to a financial condition of the user; identifying, by the one or more processors, a profile of the user based on the plurality of inputs, wherein the profile comprises a money sign, a generation profile and a life stage of the user; applying, by the one or more processors, a financial behaviour model to the profile of the user and the plurality of inputs to obtain a financial score; and providing, by the one or more processors, the financial plan to the user based on the profile of the user, and a comparison of the financial score with an ideal financial score, wherein the ideal financial score is recommended by the financial behaviour model based on the profile of the user.»

**Пункт 8 ДОСЛОВНО (ключевой для нас):** «8. The method of claim 1, wherein the financial behaviour model comprises a matrix of a plurality of financial metrics, and a plurality of generation profiles for each life stage, wherein a generation profile for a life stage is mapped to a **weighted combination of the plurality of financial metrics** and wherein each financial metric is mapped to an **ideal value**; and wherein the weighted combination, the ideal value, a **minimum threshold, and a maximum threshold** of the each financial metric is based on the money sign, the generation profile, the life stage and one or more FIN01 **macroeconomic factors**, and wherein the weighted combination, the ideal value, the minimum threshold and maximum threshold of the each financial metric is **updated based on a change in the one or more macroeconomic factors**.»

**Пункты 2, 5, 12 ДОСЛОВНО (фрагменты):** «2. … the plurality of inputs comprise at least one of personal identification data, personal data, a lifestyle plan, a total income, a plurality of expenses, financial portfolio data, **emergency funds**, a life event, and a life interest of the user.» ; «5. … the life stage of the user is one of a building phase, a growth phase, a sustainability phase, a pre-retirement phase and a retirement phase…» ; «12. … the financial plan comprises one or more recommendations to increase the financial score to or beyond the ideal financial score, when the financial score deviates from the ideal financial score, and wherein the one or more recommendations is based on a set of predefined rules associated with the profile of the user.»
Пункты 13–22 — системный аналог 1–12; п. 19 повторяет обновление весов/порогов при «predefined change in one or more macroeconomic factors»; п. 22 — рекомендации **финансовых продуктов** для роста скоринга.

**Выжимка (по формуле, не по описанию).** Объект защиты — **скоринг финансового состояния**: профиль (психотип «money sign» + «generation profile» + стадия жизни) → взвешенная комбинация метрик с идеальными значениями и min/max порогами → сравнение фактического скоринга с идеальным → правила-рекомендации (в т. ч. продукты). **Распределения свободного денежного потока между альтернативами, перечисления альтернатив, долгового порядка погашения и инвариантов в формуле нет.**

### Г31.5-K2. 🟢 KR102121857B1 — ФОРМУЛА ДОБЫТА (7 пунктов, 2 исключены), запись «не размечена и в `ko`» — та же ошибка чтения

- `https://patents.google.com/patent/KR102121857B1/ko` — **HTTP 200, 124 867 б**, sha256 `49c172a18cf24852262fa2b61743d219acfd27855f090ecd5d1e6733e30baf5a`; `<section itemprop="claims">` — **7 блоков `class="claim"`, 1 699+ знаков**. Плюс официальный PDF публикации: `https://patentimages.storage.googleapis.com/8a/31/7a/86c61473b0d51c/KR102121857B1.pdf` — **HTTP 200, 1 169 261 б**, 14 стр., **с текстовым слоем** (шрифты Batang/Gulim, Identity-H; `pdftotext` → 31 908 б), sha256 `98c13bb8e5c1343c6742b8f7af55576bbd68f6d3292b14b9bffafc6850789e86`. KIPRIS не понадобился.

**Пункт 1 ДОСЛОВНО (корейский оригинал, фрагменты по существу):** «재무설계 서비스 제공 방법에 있어서, … 통합부가 복수개의 금융사에 접속하여 스크래핑한 금융 정보를 기반으로 상기 고객이 가입한 적어도 하나 이상의 금융 상품을 수집하여 리스트로 통합하는 단계; 분석부가 … **비상자금지표, 가계수지지표, 부채상환지표, 총부채부담지표, 보장성보험준비지표, 저축성향지표, 투자성향지표, 노후대비저축지표 및 금융자산비중지표의 9개의 재무 비율**을 분석항목으로 하여 각 재무비율 별 분석기준을 갖는 권장 가이드 라인에 따라 상기 고객의 재무 상태를 분석하는 단계; … 상기 권장 가이드 라인은 상기 9개의 재무비율 중 비상자금지표, 가계수지지표, 부채상환지표, 저축성향지표 및 투자성향지표에 대해서는 **연령 별로 상이하며**, 상기 분석하는 단계는 상기 고객의 소득 수준 대비 지출 비율의 적정성 여부를 점수로써 수치화 하고, 그 수치화 된 값을 기반으로 재무 상태에 대한 **등급을 산출**하는 것이고, … 상기 연령 별 권장 가이드 라인은 **연구 논문 및 고객 설문 결과를 토대로 산출되며**, 상기 재무설계는, 각 목적에 따라 설계 유형이 보장설계, 은퇴설계, 교육설계, 목돈설계, **부채설계**, 투자설계 및 종합설계로 분리되며, … 상기 은퇴설계는 … 시나리오 분석을 통해 복수개의 설계안 및 상기 복수개의 설계안 각각의 예상 결과를 표시하여 보여주며…»
Пункты 2 и 4 — «삭제» (исключены); 3 — «물가상승률, 기대수익률, 기대수명, 연금할인률, 시점 정보» (инфляция, ожидаемая доходность, ожидаемая продолжительность жизни, ставка дисконтирования аннуитета, момент времени); 5 — отчёт; 6 — «추천부가 금융 상품을 실시간으로 조회하고, 재무설계 결과에 대응하는 상품을 추천» (рекомендация продуктов); 7 — программа на носителе.

**Перевод сути п. 1 (мой):** способ: хранение сведений о клиенте → скрейпинг продуктов клиента из нескольких финорганизаций → анализ по **9 финансовым коэффициентам** (резервный фонд, баланс доходов-расходов, обслуживание долга, общая долговая нагрузка, страховая защита, склонность к сбережению, к инвестициям, пенсионные накопления, доля финактивов) против рекомендуемых нормативов, **5 из 9 нормативов зависят от возраста** и выведены «из научных статей и опросов клиентов»; адекватность расходов к доходу переводится в баллы и **грейд по таблице**; планирование по типам целей, включая **долговое**; комплексный план — пожизненный денежный поток и чистые активы; пенсионный — сценарный анализ.

**Выжимка.** Прежний вывод Г30.4-П2 по описанию **подтверждён формулой и сужен**: защищён скоринг-грейд по 9 коэффициентам с возрастными нормативами + типовые планы; распределения потока между альтернативами и порядка погашения в формуле нет.

### Г31.5-K3. SSRN 5043646 (Синяков и др.) — ЗАКРЫТ В ДРУГОМ ФАЙЛЕ

Задолженность Г30.4 п. 3 («Exa fetch timeout, повтор не делался») устарела: работа добыта как **Рабочий доклад Банка России № 132** в `behavioral_finance_field_2026-09-10.md`, Г30.2-16 (стр. 1662, `curl` 200). Повторно не добывалась.

## ИТОГ Г31.5 — bank_patents_wellness_scoring

3 кандидата, **3 закрыты**: WO2026074314A1 и KR102121857B1 — **прямой `curl` по тем же страницам Google Patents + разбор секции `claims` из HTML** (плюс официальный PDF KR с текстовым слоем); Patentscope и KIPRIS не понадобились. SSRN 5043646 — ссылкой.

🔴 **Что меняет НОВИЗНУ и юрблок (формулировку новизны не правлю — решение владельца):**
1. **WO2026074314A1 п. 8 и 19** защищают «взвешенную комбинацию финансовых метрик с идеальными значениями и min/max порогами, зависящими от профиля и стадии жизни, **обновляемыми при изменении макроэкономических факторов**». Это ближе к нашей конструкции (веса SAW по риск-профилю, пороги, макро в прогнозе), чем считалось, когда формула была «недоступна». Граница, по формуле: у них — **скоринг состояния и сравнение с идеальным скорингом**, у нас — **выбор распределения потока на множестве из 66 альтернатив с инвариантами**. Опора новизны на метод распределения (вывод Г30.4-П2) устояла; опора на «взвешенные метрики с профильными порогами» — **нет**.
2. Юрблок: срок входа в нацфазу RU по-прежнему ≈ **2027-05-02** (31 мес. от 2024-10-02). Если 1Finance войдёт в нацфазу РФ, формула в текущем виде на распределение потока не читается, но на **скоринг финансового здоровья с профильными весами** — читается. Любая будущая фича «оценка финансового здоровья с весами по профилю» требует сверки с п. 1/8/13/19.
3. KR102121857B1 (до 2038-05-02, только Корея): риска в РФ нет; как свидетельство — «возрастные нормативы коэффициентов из статей и опросов» и грейд по таблице известны с 2018 г.

**ЗАДОЛЖЕННОСТЬ по файлу:** п. 4–8 Г30.4 (APK «Без Долгов», ОКБ headless, конверсия Telegram, реестр ПО, ключ USPTO) — не класс Г31.5 (нужен владелец / другой инструмент), не брались.
