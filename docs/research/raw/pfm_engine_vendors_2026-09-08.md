# Первичный материал: вендоры PFM-движков (B2B), 08.09.2026

> Правило проекта §9 — дословный первичный материал ДО выжимки.
> Тема №11 очереди `docs/research/queue/RESEARCH_QUEUE.md`.
> Прогон: лид-агент + 2 субагента параллельно (жёсткий лимит владельца — не более двух).
> 🔴 Ограничение прогона: **бюджет WebSearch сессии был исчерпан (400/400) ещё до старта** —
> и у лид-агента, и у обоих субагентов. Весь материал добыт **только `WebFetch` по прямым
> или угаданным URL**. Это даёт системную слепую зону: источники, чей адрес не был известен
> заранее, не найдены в принципе. У лид-агента вдобавок не было `Bash` (`curl`, `pdftotext`
> недоступны); у субагентов `Bash` был.

---

## ЧАСТЬ A. Находки лид-агента (прямой WebFetch)

### A1. 🔴 Патент основателей Personetics — US20220253817A1

Найден через Google Patents XHR API (`patents.google.com/xhr/query?url=q%3Dpersonetics`),
поскольку обычная страница поиска рендерится JS и WebFetch её не видит.

Полный список выдачи по запросу `personetics`:

```json
[
  {"publication_number":"US9495331B2","title":"Advanced system and method for automated-context-aware-dialog with human users","assignee":"Personetics Technologies Ltd.","priority_date":"2011-09-19","filing_date":"2012-09-19","grant_date":"2016-11-15"},
  {"publication_number":"US20220253817A1","title":"Automated ai systems and methods for personalized savings or debt paydown","assignee":"David Sosna","priority_date":"2020-11-23","filing_date":"2021-11-23","publication_date":"2022-08-11"},
  {"publication_number":"WO2001040993A1","title":"Method and system for exchanging information","assignee":"Personetics Inc.","priority_date":"1999-12-01"},
  {"publication_number":"WO2001040957A1","title":"Communication system","assignee":"Personetics Inc.","priority_date":"1999-12-02"},
  {"publication_number":"RO132954A0","title":"Cloud-computing-type customer communication center","assignee":"Beia Cercetare S.R.L.","priority_date":"2018-07-25"}
]
```

Замечание: `WO2001040993A1` / `WO2001040957A1` числятся за «Personetics Inc.» 1999 года —
это **другая компания**, не израильская Personetics Technologies (основана 2010).
Субагент 1 независимо нашёл ещё `US9495962B2` того же семейства (диалоговые системы).
Итого у самой Personetics Technologies — **патенты про диалоговый интерфейс, а не про
финансовую математику**; вся раскрытая финансовая механика лежит в заявке основателя лично.

#### US20220253817A1 — метаданные

| Атрибут | Значение |
|---|---|
| Название | Automated AI systems and methods for personalized savings or debt paydown |
| Изобретатели | **David Sosna** (сооснователь и CEO Personetics), David Govrin, Jody Bhagat |
| Правообладатель | подано на физлиц, не на компанию |
| Приоритет | 2020-11-23 (провижнл US63/117,050) |
| Публикация | 2022-08-11 |
| Статус | **ABANDONED, 2023-11-16** |

#### Независимые пункты формулы (дословно)

**Claim 1 — автоматические сбережения:**
> "enabling a consumer to identify a source checking account for income deposits and an amount to
> save; linking the source checking account as a source of funds; determining an amount the customer
> is able save based on a balance forecast model predictions model; determining the amount the
> customer is able to save meets a customers request; and delivering an instructions to a bank to
> transfer a designated amount to a destination savings account."

**Claim 5 — ускоренное погашение долга:**
> "enabling a user to opt into accelerated debt paydown process by: identifying one or more current
> loans of the user; linking a source account in a source bank as a fund source; analyzing a user
> transaction data; identifying an amount the user can set aside towards debt paydown; and delivering
> an electronic instruction to the source bank to transfer a designated amount to paydown a loan
> principal of the one or more current loans."

**Claim 8 — «мульти-интент», распределение между сбережением и долгом:**
> "recognizing any available funds in a primary checking account; linking to a source account for
> funds; enabling a customer to identify a destination account and a target loan to pay down;
> executing a batch process that analyzes customer transaction data; identifying an amount of the
> funds that a consumer is able to set aside with an allocation model; implementing an allocation
> model that: determines a first portion of the amount that is transferred to a saving account;
> determines a second portion of the amount versus paying down debt; delivering a set of electronic
> instructions to a relevant bank server..."

#### Механика по описанию патента

- **Balance-forecasting model** — прогноз «сколько денег понадобится на обязательные
  и необязательные расходы за период», по историческому кэшфлоу.
- **Сегментация на 5 сегментов** — пороговые правила:
  > "This segment is defined by a set of threshold-based rules... The eligibility model is applied
  > to the remaining population in order to segment the customers into two groups."
- **Модели предсказания «можно ли отложить»:**
  > "In order to identify eligible users and to recognize situations in which user balance is
  > sufficient for saving, state-of-the-art models are utilized (e.g. novel deep learning neural
  > networks as well as gradient boosting and logistic regression are used, etc.). Personetics models
  > yield highly accurate predictions that support various business decisions for new (e.g. unseen)
  > users' data in real time."
- **Приоритизация инсайтов — скоринг готового пула:**
  > "Insight prioritization 1102 can include a set of recommendation algorithms that use past user
  > interactions to adjust the score of each insight according to the context and the user's
  > preferences."
- **«Мульти-интент оптимизация» — чёрный ящик:**
  > "The multi-intent optimization process 600 can be combined with an allocation model that
  > determines how much to allocate to savings versus paying down debt in step 604."
  Формула сплита, критерий размена, веса — **не раскрыты нигде в документе**.
  Слово "optimization" встречается ~14 раз, но ни разу не описано как перебор вариантов.
- Пороги настраиваются банком:
  > "Balance-forecasting model solutions can be configured by a financial entity (e.g. bank) to set
  > thresholds for the number of times money movement occurs, amounts, and minimum balances."
- Прогноз повторяющихся платежей:
  > "Recurring pattern identification 902 can utilize a time series model that analyzes the historical
  > activity in an account and recognizes which transactions have a recurring pattern."
- 🔴 **В тексте патента НИ РАЗУ не встречаются "interest rate", "avalanche", "snowball"**
  (проверка субагента 1 по полному тексту).
- **Явно отсутствуют:** целевая функция, сравнение ставок, Монте-Карло, квантили p10–p90,
  риск-профиль пользователя, ранжирование нескольких вариантов распределения.
- Ограничение — только минимальный остаток: *"without risking the balance condition"*.

**Цитируемый прежний уровень техники:** US20150379488A1 (Clear Path Financial),
US20210125274A1 (KeyBank).

### A2. Патент KeyBank US20210125274A1 — «автосбережения и погашение долга»

Прочитан через freepatentsonline (Google Patents в момент запроса отдавал HTTP 503).

- Правообладатель: **KeyBank National Association**.
- Claim 1 дословно:
  > "A system for automatic savings, the system comprising: a first bank account belonging to a user,
  > a second bank account belonging to the user, a financial account belonging to the user, wherein
  > the financial account may be one of the first bank account or second bank account; wherein, a
  > preset amount of monetary funds is automatically transferred from the first bank account to the
  > second bank account when a transaction involving the financial account occurs."
- Выбор между savings mode и debt paydown mode — **ручной, пользователем в UI**
  («an option to select one of a savings mode or a debt paydown mode»).
- Ни сравнения ставок, ни анализа долгов, ни ранжирования вариантов. Механизм round-up-переводов.

### A3. Personetics Engage — продуктовая страница (personetics.com/personetics-engage/)

Дословные технические утверждения со страницы:

- *"analyzes the most current and predictive data to create a personalized list of actionable insights"*
- данные: *"user-specific data streams (including relationships, transactions, location, and behavior)"*
- **Приоритизация:** *"proprietary learning algorithm that identifies and ranks the most relevant
  insights"* — определяет, какие инсайты показать и в каком порядке.
- **Триггерность:** *"Insights are triggered upon invocation, to ensure they account for the most
  recent customer activity."*
- **Самообучение:** *"learns from individual customer interactions to better prioritize insights"*,
  учитывает лайки/рейтинги.
- **Ядро — библиотека правил:** *"a rich library of pre-built insights"* плюс
  *"Content Editor that is a business user interface for managing pre-built insights and creating
  new insights using the Personetics framework"*.

> Единица ранжирования — **готовая подсказка (контент)**, а не вариант распределения денег.

### A4. Personetics Act — продуктовая страница (personetics.com/personetics-act/)

- Цели-накопления, несколько целей, *"advanced fund allocation capabilities"* между счетами.
- Способы пополнения: smart auto-save, pay-yourself-first, ручные переводы.
- Заявлено: *"hyper-personalized transfer recommendations based on cashflow analysis, risk level,
  and financial needs"* — упоминание «risk level» есть, раскрытия нет.
- Механика «safe-to-save» описана только через отзыв клиента:
  > "The amount that's being moved varies, from day to day. It moves and changes, according to the
  > patterns and the movement of money in the transaction account, always leaving a sufficient
  > balance to meet the need of that particular customer."

### A5. Кейс UOB TMRW (personetics.com/customer-stories/uob/)

- Объявлен **02.11.2022** на Singapore Fintech Festival, первый рынок — Индонезия, далее ASEAN.
- Механика: поиск *"safe-to-save money (i.e. excess amounts above average/typical cash outflows
  level)"*, анализ *"monthly inflows and outflows"*, предсказание
  *"each customer's past, current and future spending patterns, income, and everyday transactions"*.
- Переводы переменными суммами, *"up to several times a week"*, на счёт с более высокой ставкой.
- Масштаб: с 2018 UOB доставил *"over 150 million personalised insights"* (Индонезия, Малайзия,
  Сингапур, Таиланд); рост мобильных логинов ~30% г/г.
- Kevin Lam: *"one in two consumers in Indonesia highlighted that their top financial concern is the
  ability to put money aside for saving."*

> Safe-to-save дословно определён как «излишек над типичным уровнем оттока» — это **прогноз одной
> величины**, а не выбор из множества вариантов распределения.

### A6. Envestnet developer portal (developer.envestnet.com/products/)

16 продуктов, среди них дословно:

- **Goals** — "Provides a summary of the client's goals overtime. Allows for adjustments to be made
  to their goals."
- **Monte Carlo** — "Firms can display updated results of a client's financial goal plan anywhere on
  an advisor platform or client portal."
- **PlayZone** — "Provides the ability to interact with the existing financial goal plan to see how
  changes may impact the results."

> 🔴 У Envestnet **есть** и Монте-Карло, и what-if-сценарии — но в **advisor/wealth-контуре**
> (инвестиционный план по целям), а не в контуре распределения денежного потока. Это ровно
> та же граница, что зафиксирована по Vanguard ADV в разборе №5.

### A7. Bud Financial (thisisbud.com)

Продукты: **Enrich** (обогащение транзакций), **Drive** (аналитика/сегменты), **Engage** (PFM),
**Focus** (дашборд сотрудника), **Assess** (кредитная пригодность).
Дословно: *"98% accurate market-leading categorization"*; на уровне транзакции —
*"a complete understanding of category, merchant, regularity, location and more"*; портфельно —
*"dashboards, segments and triggers"*. Есть "Action Hub" — *"converts insights into trackable
actions"*. **Ни моделей, ни прогноза, ни долговой приоритизации на сайте не описано.**

### A8. Moneythor (moneythor.com/product/) — проверка лид-агентом

Страница называет *"Recommendations, Insights & Nudges"*, *"Fully Configurable Solution"*,
*"extensive library of tailored use cases"*. **Ни одного описания того, как решение принимается.**
`docs.moneythor.com` — DNS не резолвится (ENOTFOUND).

### A9. Yodlee — не найдено

- `developer.yodlee.com` — только общие фразы («Aggregate data...», «Turn data into intelligence»),
  списка продуктов нет.
- `www.yodlee.com/data-analytics` — есть Credit Solutions и Business Financial Management,
  **описания cash-flow-анализа / FinCheck / прогноза нет**.
- `www.envestnet.com/solutions/data-aggregation-analytics` — HTTP 404.
- Историческая гипотеза о продуктах «Cashflow Analysis» / «FinCheck» **не подтверждена и не
  опровергнута** — это утверждение о поиске, не о вендоре.

### A10. Что лид-агенту прочитать не удалось

- `patents.google.com/patent/US20210125274A1/en` — HTTP 503 (обошёл через freepatentsonline).
- Все последующие XHR-запросы к Google Patents (meniga, moneythor, общий запрос по
  «debt paydown savings optimization allocation») — **HTTP 503**, антибот-лимит.
  Второго канала не было (нет `Bash`/`curl`).
- freepatentsonline по assignee Meniga/Moneythor/Strands — 97 совпадений, в первых 50
  ни одного с этими правообладателями; страницы 2–3 не просмотрены. **Вывод не сделан.**

---

## ЧАСТЬ B. Отчёт субагента 1 — insight/advice-движки (дословно)

> Зона: Personetics (глубина), Meniga, Strands, Moneythor, Dreams, Flybits, Abe.ai,
> Cinch Financial, Wealthy/Nomi, Kasisto. Бюджет израсходован (~24 вызова), 36 tool_uses.

### Personetics

**1. Что продают:** модульная платформа: **Act** (Smart Savings Journeys — автонакопления/
автопогашение долга), **Enrich** (категоризация транзакций), **Engage** (персонализированные
инсайты), **Engagement Builder** (no-code конструктор инсайтов для банка). https://www.personetics.com/

**2. Заявленная математика:** на сайте — только маркетинг («AI-powered», без деталей).
Патентный поиск дал 3 релевантных патента + 1 патент основателя лично:
`US9495331B2` / `US9495962B2` — диалоговая система (relevance score для topic-to-topic таблицы),
НЕ финансовая оптимизация; `US20220253817A1` — единственный источник с раскрытым механизмом.

**3. Центральный вопрос (перебор/ранжирование или if-then) — смешанная картина:**
- eligibility-сегментация — **чистые threshold-правила** (Segment 1–5), не ML;
- прогноз «сколько можно отложить» — **ML-регрессия/классификация**, не оптимизация;
- insight prioritization — **скоринг готового пула** («use past user interactions to adjust the
  score of each insight»), формулировка близка к contextual bandit, но это не enumerate-and-rank;
- «multi-intent optimization» (сбережения vs долг) — **заявлено как optimization, раскрыто как
  чёрный ящик**: одна модель выдаёт один сплит, формулы/весов нет.

**4. Долги:** 🔴 в патенте **ни разу** нет "interest rate", "avalanche", "snowball" — механизм
автопогашения долга не учитывает ставку явно.

**5. Прогноз:** "balance forecast model" — deep learning / gradient boosting / logistic regression;
архитектура, горизонт и квантили не раскрыты, **p10–p90 не упоминается вовсе**.

**6. Клиенты:** BMO, Santander, Huntington Bank, Scotiabank, Akbank, KBC Bank, **UOB**, Discount
Bank, Citizens Bank, Synovus, Truist, RBC Royal Bank, BNP Paribas, Erste Group, BPI и др.
Результаты: Scotiabank 73% engagement / 5 млн пользователей; Akbank 450 млн инсайтов в год,
approval rate 86%; MyState Bank — AU$1.4 млн сбережений за год.

**7. Модель продажи:** явно не раскрыта (косвенно B2B SaaS/лицензия + no-code консоль банку).

### Moneythor
Модульная платформа: категоризация, бюджеты/цели, «115+ use cases», predictive-рекомендации.
Заявлены Predictive AI (ML для cash flow forecasting), Generative AI («Code/Content Sidekick»),
Conversational AI, **Agentic AI** («LLM-based decisioning»). Конкретной математики нет нигде —
только категории технологий. Долги отдельно не упомянуты. Cash flow forecasting — «advanced
algorithms and machine learning» без деталей. Клиенты: DBS, NAB, BNZ, Standard Chartered, Citi,
ANZ, Chiba Bank, Ogaki Kyoritsu Bank. https://www.moneythor.com/

### Kasisto (KAI / KAIgentic)
Смещение в сторону **agentic conversational AI поверх LLM** (собственная «KAI-GPT» + GPT),
«multi-agent architecture», «predictive engagement». Банки-клиенты в контенте не названы.
Ни долговой приоритизации, ни автонакоплений, ни прогноза потоков — это conversational-слой,
не advice-engine. https://kasisto.com/

### Flybits
**Контекстный/оркестрационный слой**, не рекомендательный движок: «Perspective-Aware AI (PAI)»
заявлена как **neuro-symbolic AI**, «Inference Routing System» для маршрутизации между моделями.
Финансовых рекомендаций/автонакоплений/долговой приоритизации нет — triggers/journey orchestration
и merchant-funded offers. Клиенты: TD Bank, CIBC, Simplii, Banorte, ATB Financial, FAB, Dubai First.
https://www.flybits.com/

### Meniga
Разделы сайта: Enrichment, Insights, Financial Engagement, **Smart Savings**,
**Cashflow Forecasting**, Open Banking, Agentic Banking, Hyper-Personalisation.
Заявлений о математике на главной нет (только «AI-driven personalisation»); детали, вероятно,
в закрытых Insight Papers — **не получены**. 30+ банков-клиентов (Европа, MENA, Азия).
Кейсы: **UOB** (гейм-механики, +50% MAU), UniCredit, moey!. Новый продукт — «Fini» (financial
intelligence layer для банковских AI-ассистентов, 2026). https://www.meniga.com/

### Dreams (Швеция) — статус изменился
🔴 `getdreams.com` сейчас — **чисто D2C-приложение** (сберегательный счёт через партнёра Svea Bank;
механики The Thief, Autopilot, Ostrich, Moon Cycle, групповые накопления ~40 тыс. пользователей).
**Никаких упоминаний B2B-лицензирования банкам, партнёрств с ICA Banken/Swedbank и ни одной
технической детали алгоритма.** Домен `dreams.se` редиректит на `bank.se` — независимый сервис
сравнения кредитов. Компания либо свернула B2B, либо сменила бренд; подтвердить без WebSearch
не удалось.

### Не относятся к классу / не удалось исследовать
- **Abe.ai** — `abe.ai` редиректит на `yodlee.com/fintech/conversational-ai`: поглощён
  Envestnet/Yodlee, самостоятельно как вендор не существует.
- **Cinch Financial** — домен не резолвится (timeout). Считается мёртвым, свежим источником
  не подтверждено.
- **Strands** — `getstrands.com` недоступен и через WebFetch, и через `curl`
  (TLS handshake failure). Ни одной страницы получить не удалось.
- **Wealthy/Nomi (NatWest)** — прямой URL пресс-релиза дал 404, WebSearch недоступен →
  **ничего не найдено фетчем**.

### Что оказалось только маркетингом
Практически все публичные страницы (Personetics, Moneythor, Kasisto, Flybits, Meniga) используют
«AI-powered», «advanced algorithms», «agentic AI» без единой формулы, метода или архитектуры.
Реальная механика видна **только в патентном материале Personetics**.

### Что НЕ найдено (явно)
- Ни один вендор класса не раскрывает публично метод погашения долга по ставке
  (avalanche/snowball); в единственном первичном источнике эти термины отсутствуют вовсе.
- Ни у одного не найдено описания перебора дискретных альтернатив распределения (аналог 66/SAW) —
  везде либо один output модели, либо scoring существующего пула.
- Квантильный прогноз (p10–p90) не упомянут ни у одного вендора.
- Контент Strands не получен вообще; статус Wealthy/Nomi и B2B-модель Cinch не подтверждены.
- Патентный поиск по Personetics возможно неполон из-за ограничений XHR API.

---

## ЧАСТЬ C. Отчёт субагента 2 — агрегаторы и аналитика (дословно)

> Зона: Yodlee, MX, Tink, Salt Edge, Plaid, TrueLayer, Yapily, Emma, Snoop + соседи.
> 25 вызовов инструментов, WebSearch недоступен всю сессию.

**Общий вывод по зоне:** ни у одного вендора не нашлось перебора вариантов + ранжирования по
критериям. Везде — либо агрегация + категоризация («труба»), либо пороговые/триггерные инсайты
и дашборды, максимум с ML-классификацией транзакций. Прогнозный слой есть только у MX (в очень
общем виде) и у Tink (прогноз recurring-платежей, не баланса целиком).

### MX (docs.mx.com)
1. Агрегация, категоризация, PFM-виджеты (Spending, Budgets, Cash Flow), библиотека «Insights».
2. `Monthly Cashflow Profile` возвращает `budgeted_income`, `budgeted_expenses`,
   `estimated_goals_contribution`, но формула расчёта публично не документирована —
   https://docs.mx.com/api-reference/platform-api/reference/monthly-cashflow-profile.md
3. **Перебора/ранжирования НЕТ.** Insights Library, категория «Plan» — календарные и статусные
   уведомления (налоговые дедлайны, «Spending Plan Created»). Категория «Save» (15 инсайтов) —
   пороговые триггеры вокруг emergency fund («Save An Extra $100», «Monthly Emergency Fund
   Review») — https://docs.mx.com/products/experience/insights/library/index.md
4. Долги: приоритизации погашения/ставок не обнаружено.
5. Прогноз: «predictive financial insights», метод не раскрыт
   (https://docs.mx.com/products/experience/insights/index.md). Продукта с именем
   «Predicted Finances» в текущей документации не нашёл (возможно переименован — не подтверждено).
6/7. Клиенты и pricing не проверялись.

### Plaid (plaid.com/docs)
1. Assets/Income/Liabilities (андеррайтинг), Signal (риск возврата ACH-дебета), Enrich, Consumer Report.
2. Enrich: категоризация по Personal Finance Categories, мерчант, лого, гео. Метод не раскрыт,
   только «all input fields... are used to analyze transactions» — https://plaid.com/docs/enrich/
3. **НЕТ.** Ни один продукт не описывает перебор сценариев/ранжирование.
4. Liabilities отдаёт баланс и ставки по кредитам, но без приоритизации погашения.
5. Прогноза не обнаружено (Signal — риск-скоринг транзакции).

### Tink (Visa)
1. Data Enrichment: категоризация, recurring transactions, merchant mapping.
2. 🔴 Единственный в зоне с явным упоминанием ML: «Smart categorisation based on machine learning
   models, including a user feedback loop allowing for better accuracy» —
   https://tink.com/products/data-enrichment/
3. **Перебора нет.** Есть «Predicted Recurring Transactions» — прогноз конкретных будущих платежей.
4. Долги: не обнаружено.
5. «Forecast upcoming transactions to help users prevent overspend. Including all fixed
   commitments» — прогноз известных обязательств, не Монте-Карло/SES по общему потоку.

### Salt Edge
1. Data Aggregation, Data Enrichment, Merchant Identification, Financial Insights («360° view of
   customers' finances»), Open Banking compliance/payments/AML.
2. Математика не раскрыта на маркетинговых страницах.
3. **НЕТ** упоминаний forecasting / recommendation engine / scenario ranking на продуктовой странице.
   (`developer.saltedge.com` отдельно не проверялся.)

### TrueLayer
1. Payments, Data (аккаунты/баланс/история), Signup+, Verification. Чистая труба + Pay by Bank.
2. Аналитического слоя нет вовсе.
3. **НЕТ.** Вне класса «слой поверх транзакций».

### Yapily
1. Payments (включая VRP), Data (Account Information), «Data Plus» — Transaction Categorisation
   & Data Enrichment.
2. Заявляет «real-time cash flow forecasting and insights» в контексте accounting-решений —
   похоже, это описание того, что делают их клиенты, а не собственный движок. Формулировка
   расплывчата, нужна доп. проверка.
3. **НЕТ** явного перебора/ранжирования у самого Yapily.

### Emma (emma-app.com)
Агрегация счетов, бюджеты, категоризация, поиск «wasteful subscriptions», savings goals,
инвестиции от £1. Математика не раскрыта. **Нет** упоминаний balance forecasting, debt payoff
optimization, ranking — только трекинг и подписки.

### Snoop (snoop.app)
Агрегация, категоризация по мерчанту, бюджеты, сберегательный счёт, bill-switching рекомендации,
мониторинг кредитного скоринга. «AI-powered» в маркетинге, механики нет. Дословно:
«Snoop will highlight anything that needs your attention, from daily account balances to bill
increases – and can even warn you when your bills may not be covered» — это триггер/алерт,
не прогноз и не оптимизация. Долгов и forecasting-движка нет.
Монетизация: комиссия от switching-сервисов, анонимизированные данные, подписка Snoop Plus.

### Envestnet | Yodlee
Прямой доступ к developer-порталу/продуктовым страницам не получен
(`www.envestnet.com/yodlee/products` — 404). Историческая документация «Cashflow Analysis» /
«FinCheck» **не подтверждена**. Требует отдельного прохода.

### Finicity / Mastercard
`mastercard.us` — HTTP 403 (антибот). Не проверено.

### Bud Financial, Ntropy, Nordigen/GoCardless, Basiq, Akoya, ForwardLane
Субагентом не проверялись (бюджет). Bud проверен лид-агентом — см. A7.

### Дословные цитаты, где раскрыта механика
- Tink: «Smart categorisation based on machine learning models, including a user feedback loop
  allowing for better accuracy and a personalised experience.» — https://tink.com/products/data-enrichment/
- Tink: «Forecast upcoming transactions to help users prevent overspend. Including all fixed
  commitments.» — там же.
- Plaid Enrich: «all input fields, not just `description`, are used to analyze transactions» —
  https://plaid.com/docs/enrich/
- Snoop: «Snoop will highlight anything that needs your attention, from daily account balances to
  bill increases – and can even warn you when your bills may not be covered.» — https://www.snoop.app/

### Только маркетинг
MX «Financial Insights» («dynamic, personalized, and predictive financial insights»),
Salt Edge «Financial Insights» («360° view»), Yapily «real-time cash flow forecasting»,
Snoop «AI-powered» — всё без деталей алгоритма.

### Явный список «не найдено»
- Ни у одного вендора зоны — перебора вариантов распределения потока / SAW-подобной свёртки.
- Ни у одного — avalanche/snowball-приоритизации долгов как продукта с API.
- MX «Predicted Finances» как отдельный именованный продукт не подтверждён.
- Yodlee (developer docs, FinCheck, Cashflow Analysis) — не проверено.
- Finicity/Mastercard Cash Flow Insights — не проверено (403).
- Патенты Yodlee/MX/Plaid — не проверено (антибот-блок Google Patents).
- Клиентская база, масштаб и pricing почти по всем вендорам не проверены.

---

## ЧАСТЬ D. Противоречия между источниками и незакрытые дыры

1. **Расхождения между субагентами не обнаружено** — оба независимо пришли к одному ответу
   на центральный вопрос (перебора вариантов нет ни у кого), и оба нашли одно и то же
   ограничение метода (WebSearch недоступен).
2. **Внутреннее противоречие внутри Personetics:** маркетинг Act говорит про
   «hyper-personalized transfer recommendations based on cashflow analysis, **risk level**,
   and financial needs», а патент основателя не содержит ни риск-профиля, ни ставок, ни
   критерия размена. Раскрытый первоисточник беднее рекламы — но это не доказывает, что
   в проде нет большего.
3. **Незакрытое (честно «неизвестно»):** Strands целиком; Yodlee/FinCheck; патенты Meniga,
   Moneythor, MX, Plaid, Yodlee; закрытые Insight Papers Meniga; статус B2B-модели Dreams;
   Wealthy/Nomi NatWest; Finicity/Mastercard; Bud/Ntropy/Basiq/Akoya на уровне docs.
4. **Главная методическая оговорка:** отсутствие поиска означает, что найдено только то,
   чей адрес был угадан. Утверждения вида «ни у кого нет» здесь — это утверждения о
   **публично раскрытом**, а не о содержимом закрытых B2B-движков.
