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
