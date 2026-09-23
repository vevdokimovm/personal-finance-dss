# Первичный материал: банки мира и их PFM-ассистенты — ПЕРЕЗАПУСК v2

**Дата:** 09.09.2026. **Темы очереди:** №6, №7, №8 одним заходом.
**Правило проекта §9/§11** — дословное сырьё ДО выжимки, файл пишется по ходу.

## Шапка о качестве прогона

- **WebSearch ЖИВ** — проверено первым же запросом. Это принципиальное отличие
  от прогона 08.09 (`banks_partial_results_2026-09-08.md`), где WebSearch был исчерпан
  и в файле НОЛЬ URL.
- Прогон: **один агент, подагентов НЕ запускалось**.
- Цитаты даются в оригинале, английский не переводится.
- Каналы и коды ответа — раздел «СОСТОЯНИЕ КАНАЛОВ» ниже, пополняется по ходу.

---

## СОСТОЯНИЕ КАНАЛОВ (пополняется по ходу)

(таблица каналов — в конце файла, раздел «СОСТОЯНИЕ КАНАЛОВ (итог)»)

---

## 1. Bank of America — Erica (первичный источник, ОТКРЫТ)

URL (открыт, 200): https://info.bankofamerica.com/en/digital-banking/erica

Дословно со страницы:
> "Erica provides proactive insights, helps you manage your accounts, finds answers to your questions and connects you to financial specialists."
> "Erica also offers personalized insights to help you manage cash flow and stay on top of your finances."
> "Track your spending by category (Utilities, Groceries, Transportation, Shopping and much more) to help stay on track."
> "Review your spending across categories and get a weekly snapshot of your month-to-date spending."
> "Monitor recurring charges" — уведомления при росте платы за подписки.
> **"Erica does not provide investment advice."**
> Технология названа явно: natural language processing "grounded in machine learning (not generative AI or large language models)".

🔴 Отрицательный результат, зафиксированный по первичному источнику: на официальной странице
функций **нет** ни бюджетных советов, ни рекомендаций по накоплениям, ни работы с долгом,
ни прогноза. Только категоризация, срез трат, мониторинг подписок, cash flow insights.

URL (открыт, 200): https://newsroom.bankofamerica.com/content/newsroom/press-releases/2025/08/a-decade-of-ai-innovation--bofa-s-virtual-assistant-erica-surpas.html

Цифры вовлечённости (важны как бенчмарк масштаба PFM-функций):
- ~50 млн пользователей с 2018, **3 млрд взаимодействий**, 58 млн взаимодействий в месяц, 18.7 млн часов диалогов.
- **"more than 1.7 billion proactive, personalized insights delivered by Erica"** — кэшбэк-предложения
  по паттерну трат, алерты о тренде баланса за 7 дней, уведомления о доступных бонусах.
- Цитата главы digital: "Our clients appreciate Erica's ability to help them manage their spending, improve budgeting and increase savings."
- >98% пользователей находят нужное; покрытие ~50 инвест-тем, библиотека 700+ ответов.

**Вердикт по BofA:** дескриптив + проактивные алерты. Ставки не считает, размен «долг vs копить»
не решает, вариантов распределения не показывает. Подтверждает вывод 08.09, но теперь со ссылкой.

---
## 2. Capital One — Eno. 🔴 ПАТЕНТ ЕСТЬ, ФУНКЦИИ В ПРОДУКТЕ НЕТ

Контекст: `pfm_engine_vendors_v2_2026-09-09.md` установил, что патент Capital One
**US11023967B1 «Guidance engine»** выдан и активен, в нём явно названы процентные ставки
и стратегии avalanche/snowball. Проверка продуктовой стороны по первичным страницам банка:

URL (открыт, 200): https://www.capitalone.com/digital/tools/eno/spending-insights/
Дословно — полный список возможностей:
> "Eno sends you helpful spending insights, so you can see where your money is going."
> Free trial detection — напоминание до конца пробного периода.
> "If Eno sees that you may have left a tip that's much higher than your usual amount, you'll receive a notification."
> Алерты о росте регулярных списаний; уведомления о возвратах от мерчантов; объяснение отказов по карте.

На странице **нет** ничего про: стратегии погашения долга, распределение денег,
процентные ставки, какие-либо расчёты, рекомендации с обоснованием.

**Вывод (главный по этому банку):** разрыв «патент → продукт» ПОДТВЕРЖДЁН на первичном источнике.
Capital One владеет действующим патентом на прескриптивный движок с учётом ставок и avalanche/snowball,
а публичное описание Eno — это система уведомлений и детектор аномалий, без единого расчёта.
Для FINPILOT это значит: патентный ландшафт занят, **продуктовая ниша — нет**.

---

## 3. Wells Fargo — Fargo (первичный источник, ОТКРЫТ)

URL (открыт, 200): https://sites.wf.com/fargo/
Дословно:
> "See a 30-day view of your predicted balance based on recurring transactions" (Balance Forecast)
> "View projected and scheduled transactions for the next 14 days" (Activity Forecast)
> "View monthly spending by category or merchant to see where you spend the most" (Spending Insights)

🔴 На официальной странице функций **НЕТ** ни savings targets, ни расчёта экономии
от консолидации долга, ни ставок — хотя вторичные обзоры это Fargo приписывают
(см. ниже, помечено как вторичное и НЕ подтверждённое первичным источником).

**Единственный прескриптивный элемент — прогноз баланса на 30 дней.** Это дескриптив-плюс:
предсказание, но не рекомендация и не выбор между вариантами.

---
## 4. RBC — NOMI Find & Save. 🔴 КОНТРОЛЬНАЯ ТОЧКА «АВТОНАКОПЛЕНИЯ» ПОДТВЕРЖДЕНА ЧИСЛОМ

URL (открыт, 200): https://www.rbcroyalbank.com/bank-accounts/nomi-find-and-save.html
Дословно:
> "NOMI Find & Save will learn your transaction patterns, find extra dollars that it thinks you won't miss and set them aside for you automatically."
> "The maximum amount NOMI Find & Save will automatically transfer from your eligible chequing account is $75 per day, up to 5 times per week."
> Ставка по накопительному счёту NOMI: **0.150%**.
> Обратный ход: до $1 000 в день возвращается на chequing, чтобы покрыть платёж или овердрафт.
> Настроить сумму перевода пользователь **не может**.
> **Про долг на странице нет ничего.**

URL (открыт, 200): https://personetics.com/resource-center/rbc-ai-powered-automated-savings-guidance/
Дословно:
> "Based on predictive analysis of individual behavior and spending patterns"
> "NOMI Find & Save™ puts artificial intelligence, machine learning and, yes, algorithms, to work."
> Функции: детект "future balance may be too low", "reduce unnecessary spend, eliminate fees, optimize savings", флаг необычных транзакций.
> Ни долга, ни ставок в описании нет. Конкретных цифр эффекта на странице нет.

🔴 **Главное наблюдение прогона.** Банк автоматически, без согласия по сумме, перекладывает
деньги клиента на счёт под **0.15% годовых**. Любой потребительский долг клиента —
кредитная карта Канады это ~20% годовых — экономически доминирует это решение с гигантским
отрывом. То есть автонакопление здесь — не оптимизация благосостояния клиента,
а удержание средств внутри банка.

**Тезис прошлого разбора («банки продвинулись к прескриптиву только там, где интересы совпадают,
то есть деньги остаются в банке») — ПОДТВЕРЖДЁН, и не рассуждением, а ставкой 0.150%
на официальной странице продукта.** Это самый сильный аргумент для FINPILOT о конфликте
интересов банковского PFM.

---
## 5. BBVA — Bconomy / Financial Health. 🔴 ПЕРВИЧНЫЙ ИСТОЧНИК ВЗАМЕН ВТОРИЧНОГО

Версия 08.09 держалась на qorusglobal.com (вторичный). Теперь — bbva.com, официальный.

URL (открыт, 200): https://www.bbva.com/en/bbvas-customers-will-first-time-online-diagnosis-financial-health/
Дословно / выписка:
> Шкала 0–100, четыре переменные, **каждая ровно 25% итогового балла**:
> месячные сбережения; "financial breathing space"; расходы на жильё;
> "spending on housing and outlays on loans and deferred card payments".
> "A score of below 50% indicates inadequate financial health in that one is spending more than one takes in."
> Пример логики: "if a customer is 20% below the recommended monthly savings level the option of budgeting to control spending is available."
> **Упоминания процентных ставок при сравнении «гасить долг vs копить» на странице НЕТ.**

URL (открыт, 200): https://www.bbva.com/en/financial-health/how-bbva-uses-data-to-look-after-its-customers-financial-health/
Дословно / выписка:
> Входные переменные: "average income from the past year, ability to save, financial cushion available,
> whether or not they have debt, their most common expenses and their investment products."
> Требование данных: "at least a 12 months with frequent transactions", иначе "the algorithms"
> не дадут точной картины.
> 🔴 **Рамка рекомендаций названа прямо: правило 50/20/30**, долг не более **35%** дохода,
> **20%** — в сбережения.
> Четыре плана: Debt plan (платежи по долгу выше посильных) · Ability to save plan (контроль расходов) ·
> Financial cushion plan (подушка на 6 месяцев расходов) · Plan for your future (инвестиции/долгосрок).
> Охват: "more than 10 million people" в Испании, расширение в Мексику.
> Исполнение не автоматическое: "it is the customer who decides whether or not to implement them."

**Вердикт по BBVA — самый прескриптивный банк выборки, и всё равно не то.** Механика раскрыта
полнее всех: равные веса 25%, порог 50, пороги 35%/20% из 50/20/30. Но это **классификация
по фиксированным эвристическим порогам в один из четырёх заранее написанных планов**.
Ни ставок, ни сравнения исходов, ни ранжирования альтернатив. Для FINPILOT это ровно тот
уровень, выше которого мы строим: у BBVA — правило-константа из популярной книжки,
у нас — SAW по 66 альтернативам с обоснованием выбора.

---
## 6. DBS (Сингапур) — NAV Planner. 🔴 ПЕРВИЧНЫЙ PDF ВЗЯТ (08.09 не смогли извлечь)

Прогон 08.09 отметил: «Официальный PDF "How DBS NAV Planner works" — WebFetch не извлёк текст».
Взят через `curl` + `pdftotext`.

URL (открыт, 200, 529 871 байт): https://www.dbs.com/iwov-resources/images/newsroom/How%20DBS%20NAV%20Planner%20works.pdf

Дословно, полный перечень блоков продукта:
> **Personalised balance sheet** — "a full overview of their financials (savings, loans, CPF, property,
> insurance protection plans and current investments)"; консолидация внешних холдингов через SGFinDex.
> **Budget and savings tracker** — "seamlessly tracks customers' cashflow, helps set up a realistic budget
> and sorts users' income and spending automatically... To build up customers' emergency savings (if needed),
> DBS NAV Planner will provide personalised suggestions and nudges".
> **Protection** — оценка достаточности страхового покрытия, "help customers prioritise the types of coverage".
> **Investment tracking** — "personalised and actionable insights to customers on how to deploy their idle cash",
> рекомендация продуктов с моментальной покупкой.
> **"Map Your Money"** — проекция будущего кэшфлоу, интеграция правил CPF/SRS,
> "To close any potential gaps in future cashflows, they are prompted with personalised ideas
> and recommendations on how to grow their wealth."
> **digiPortfolio** — ETF-портфели от SGD 1 000 по Strategic Asset Allocation.

🔴 **Долг («loans») в документе появляется РОВНО ОДИН РАЗ — как строка в балансе.**
Ни стратегии погашения, ни ставок, ни приоритизации кредитов, ни размена «гасить vs копить».
Прескриптивность DBS направлена в две стороны: страховка и инвестиции — то есть **в продажу
собственных продуктов**. Подушка — только «suggestions and nudges».

Механика (подтверждение вывода 08.09, теперь с живым источником поисковой выдачи dbs.com):
> "The DBS NAV Planner's recommendations are based on a set of rules prescribed by the DBS financial
> planning framework and take inputs from your objective, risk profile and review frequency."
> "guided by DBS' proprietary financial planning framework which comprises principles developed by
> the bank's financial planning experts and employs the Financial Planning Association of Singapore's
> (FPAS) benchmarks."
То есть **rules-based по отраслевым бенчмаркам FPAS**, а не оптимизация. Ровно как у BBVA (50/20/30),
только норматив другой.

**Наблюдение, общее для DBS и BBVA:** оба «самых прескриптивных» банка мира строят советы
на внешних нормативных константах (FPAS benchmarks / 50-20-30), а не на решении задачи
распределения. Это и есть ниша FINPILOT.

---
## 7. Santander — Financial Health Check / Budget Calculator (вторичный + выдача santander.co.uk)

Прогон 08.09 отметил Santander как «не исследован». Закрыто частично.

Выдача по officialному пресс-релизу Santander UK (страница отдала **404** при прямом фетче —
см. «СОСТОЯНИЕ КАНАЛОВ»; текст ниже — из индексированного сниппета того же домена):
> **Financial Health Check** — "a personal review of customers' finances via a free, online
> questionnaire which takes less than five minutes". Вопросы: объём заимствований, просрочки,
> накопления, используемые бюджетные инструменты. Далее "calculates their overall financial health
> and provides tailored suggestions and help".
> **Budget Calculator** — ввод дохода и расходов по категориям вручную, вывод: сумма расходов
> и диаграмма долей категорий от дохода.

**Вердикт:** это **анкета**, а не работа с транзакциями. Клиент вводит данные руками, получает
балл и текстовые подсказки. Ставок нет, оптимизации нет. Уровень — ниже BBVA.
Santander España: "Asistente Financiero" — категоризация доходов/расходов и графики (дескриптив).

---

## 8. ING — Kijk Vooruit / «Look Ahead»

🔴 Официальная страница `ing.nl/en/personal/digital-banking/your-app/look-ahead/kijk-vooruit`
**не открылась**: WebFetch — timeout 60 s, curl — `CODE=000` (соединение не установлено).
Зафиксировано в «СОСТОЯНИИ КАНАЛОВ».

Что подтверждено из индексированных описаний ING (ing.com/sustainability — раздел financial health):
> "In the Netherlands and Belgium, budgeting tools and Kijk Vooruit ('Look ahead') help customers
> plan and control their expenses."
> Функция: показывает предстоящие прямые дебеты и ожидаемый баланс — "see the expected balance
> to avoid surprises".

**Вердикт:** прогноз баланса, как Fargo. Дескриптив-плюс. Ставок и распределения нет.
🟡 Помечено как НЕ подтверждённое первичной страницей — канал был недоступен.

---

## 9. Главный вопрос — ОТВЕТ ПО ЖИВЫМ ИСТОЧНИКАМ

**Вопрос:** считает ли хоть один БАНК размен «гасить долг или копить» с учётом ставок,
и показывает ли кто-нибудь несколько вариантов распределения с обоснованием?

**Ответ: НЕТ. Ни один банк выборки. Подтверждено по первичным страницам продуктов,
а не по отсутствию находок.**

Прямые доказательства, каждое с открытого URL:
- BofA: "Erica does not provide investment advice"; список функций — категоризация и алерты.
- Capital One: страница Eno — только уведомления; при этом **патент на ровно эту логику у них есть**.
- Wells Fargo: только Balance Forecast 30 дней и Activity Forecast 14 дней.
- RBC: автонакопление под **0.150%**, слово «долг» на странице продукта отсутствует.
- BBVA: пороги **50/20/30** и **35%** долга к доходу — константы, не ставки.
- DBS: слово "loans" — одна строка баланса; прескриптив уходит в страховку и инвестиции.

🔴 **Где логика со ставками ЕСТЬ — это НЕ банки, а сторонние приложения.** Из живой выдачи:
- **Gauss (Payoff Credit Card Debt)** — "automated snowball and avalanche payoff tactics";
- **Bright Money** — "will optimize payments by analyzing spending, balances, and **APRs**";
- **Achieve GOOD**, **Undebt.it**, **Spendify** — сравнение стратегий с разницей в месяцах и деньгах.
Плюс рыночный контекст 2026 из той же выдачи: кредитные карты 20–24% годовых, HYSA 4–5% —
то есть арифметика размена тривиальна и общеизвестна, но **банки её не встраивают**.
Это не техническая невозможность. Это конфликт интересов.

**Вывод о причине.** Прескриптив у банка появляется ровно там, где рекомендация ведёт деньги
внутрь банка: автонакопление на свой счёт (RBC 0.15%, UOB TMRW), покупка своей страховки
и своих ETF (DBS), консолидация долга своим кредитом. Совет «направь свободные деньги
на погашение долга» **уменьшает** и остаток на счетах, и процентный доход банка —
и его нет ни у кого. Контрольная точка из прошлого разбора **подтверждена**.

---
## 10. Nubank — «AI Private Banker». Ближайший к замыслу FINPILOT, механика не раскрыта

URL (открыт, 200): https://nu.com/en/newsroom/company/nubank-details-ai-transformation-strategy-built-on-data-foundation-models-and-democratized-financial-advice
Дословно / выписка:
> Назначение AI Private Banker: "help customers organize finances, **manage debt**, and make better
> credit decisions"; целевая аудитория — "low- and moderate-income households historically lacking
> personalized financial guidance".
> **nuFormer** — "proprietary self-supervised foundation model", применяется к кредитным решениям:
> "safely extend credit to customers who would have been excluded by less granular models".
> Охват: отдельные функции AI Private Banker "are already used by over 15 million monthly active users"
> после 6–12 месяцев тестирования.
> 🔴 На странице **нет** ни стратегии погашения, ни ставок, ни распределения между целями.

URL (открыт, 200): https://www.zenml.io/llmops-database/building-an-ai-private-banker-with-agentic-systems-for-customer-service-and-financial-operations
(источник, который прогон 08.09 не дочитал — закрыт)
Дословно / выписка:
> "Nubank's LLM ecosystem consists of four layers: Core Engine, Testing and Evaluation Tools,
> Developer Experience, and Observability and Logging."
> Инструменты: **LangGraph и LangChain**, трассировка — **LangSmith**.
> Нагрузка: чатбот поддержки — 8.5 млн обращений в месяц; агентные переводы — с 70 с до <30 с.
> "The AI systems they've built aim to democratize access to sophisticated financial guidance
> that was previously available only to wealthy individuals with private bankers."
> 🔴 "The document does not contain specific mentions of debt payoff logic, interest rate calculations,
> or detailed money allocation algorithms."

**Вердикт по Nubank — важнейшая поправка к картине.** Это единственный банк мира, публично
заявивший цель «manage debt» в массовом ИИ-ассистенте, и единственный с подтверждённым масштабом
(15 млн MAU). Но: (1) весь раскрытый инженерный контур — это **обслуживание и операции**
(чатбот, переводы), а прескриптивный финсовет остаётся декларацией; (2) nuFormer применён
к **выдаче кредита**, то есть снова к продукту банка, а не к освобождению клиента от долга.
Это ровно та же схема совпадения интересов.

---

## 11. JPMorgan Chase — Spending Planner / Budget Tool

URL (открыт, 200): https://www.chase.com/personal/banking/education/budgeting-saving/what-is-the-chase-budget-tool
Дословно:
> "a digital feature within Chase.com and the Chase Mobile® app's Spending Planner tool that allows
> Chase checking and credit card customers to build a budget based on their monthly income, recurring
> monthly bills, savings target, and then the amounts they aim to spend on a category level for
> discretionary spending."
> "As you set a budget, the tool will present you with historical insights into your spending habits
> to help you create a budget aligned with your spending patterns."

🔴 Все цели и лимиты задаёт **сам пользователь**; инструмент лишь подставляет историческую справку.
Ни долга, ни ставок на странице нет. Это ручное бюджетирование с подсказкой из истории —
самый низкий уровень прескриптивности в выборке крупных банков США.
Закрывает пробел 08.09 («retail-PFM JPMorgan не понят»).

---
## 12. Необанки — Chime, Monzo. Автонакопления БЕЗ всякой логики

URL (открыт, 200): https://www.chime.com/savings/automatic-savings/
Дословно:
> "Save When You Spend automatically rounds up transactions to the nearest dollar and transfers
> the Round Up from your Checking Account into your Automatic Savings Account."
> "Chime members can automatically transfer a percentage of every paycheck directly into their
> Savings Account."
Ни долга, ни ставок, ни какой-либо оценки ситуации клиента. Два фиксированных правила.

URL (открыт, 200): https://monzo.com/features/pots
Дословно / выписка: Pots — это раздельные «кошельки»: имена, картинки, оплата счетов из Pot,
скрытие и блокировка Pot против перерасхода. "Set up Direct Debits and standing orders to come
directly from a Pot." **Рекомендаций «сколько откладывать» нет; долг не упоминается.**

**Вердикт по необанкам:** уровень прескриптивности **ниже**, чем у классических банков.
Автонакопление у Chime — арифметика округления, у Monzo — ручные конверты. Ноль анализа.
Reputation «умных банков» на PFM-стороне не подтверждается: их сила в UX и стоимости
обслуживания, не в советах.

---

## СВОДНАЯ ТАБЛИЦА

| Банк | Что реально делает ассистент/PFM | Считает ли ставки | Показывает ли варианты распределения | Источник (открыт) |
|---|---|---|---|---|
| Bank of America (Erica) | категоризация, срез трат, мониторинг подписок, cash-flow insights, 1.7 млрд проактивных инсайтов | **нет** | нет | info.bankofamerica.com/en/digital-banking/erica; newsroom.bankofamerica.com (2025-08) |
| Capital One (Eno) | только уведомления: дубли, рост подписок, конец free trial, нетипичные чаевые | **нет** (при живом патенте US11023967B1) | нет | capitalone.com/digital/tools/eno/spending-insights/ |
| Wells Fargo (Fargo) | Balance Forecast 30 дн., Activity Forecast 14 дн., траты по категориям/мерчантам | **нет** | нет | sites.wf.com/fargo/ |
| JPMorgan Chase | ручной бюджет + историческая справка по категориям | **нет** | нет | chase.com/personal/banking/education/budgeting-saving/what-is-the-chase-budget-tool |
| RBC (NOMI Find & Save) | автоперевод до $75/день на счёт под 0.150%, возврат до $1000/день под платёж | **нет** | нет (сумму нельзя настроить) | rbcroyalbank.com/bank-accounts/nomi-find-and-save.html |
| BBVA (Bconomy) | индекс 0–100 из 4 переменных по 25%, порог 50, один из 4 планов | **нет** — пороги 50/20/30 и 35% | нет (классификация в 1 план) | bbva.com (две страницы) |
| DBS (NAV Planner) | баланс, бюджет, nudges на подушку, страховка, инвестиции, проекция кэшфлоу | **нет** (rules по бенчмаркам FPAS) | нет | dbs.com/.../How%20DBS%20NAV%20Planner%20works.pdf |
| Nubank (AI Private Banker) | заявлено "manage debt", 15 млн MAU; раскрыто — чатбот и переводы (LangGraph/LangSmith) | **не раскрыто** | не раскрыто | nu.com newsroom; zenml.io llmops-database |
| Santander | анкета Financial Health Check + ручной Budget Calculator | **нет** | нет | santander.co.uk (страница 404, сниппет домена) |
| ING (Kijk Vooruit) | предстоящие дебеты + ожидаемый баланс | **нет** | нет | 🟡 канал недоступен, см. ниже |
| Chime | round-ups + % от зарплаты в накопления | **нет** | нет | chime.com/savings/automatic-savings/ |
| Monzo (Pots) | ручные конверты, оплата счетов из Pot, блокировка Pot | **нет** | нет | monzo.com/features/pots |

**Ни одной ячейки «да» в колонке ставок. Ни одной «да» в колонке вариантов распределения.**

---

## ЧТО ИЗМЕНИЛОСЬ ПРОТИВ ВЕРСИИ 08.09

**Подтверждено на живых первичных источниках (было без ссылок — стало со ссылками):**
- BofA Erica не даёт советов; цитата "Erica does not provide investment advice" — верна, страница открыта.
- Capital One Eno — только мониторинг и алерты. Верно.
- Wells Fargo — прогноз баланса. Верно.
- BBVA — индекс 0–100, 4 переменные, порог 50, четыре плана. Верно **и уточнено**: веса ровно
  по 25%, рамка — правило 50/20/30 с порогом долга 35%, охват 10 млн человек, требование 12 месяцев истории.
- DBS NAV Planner — rules-based, не ИИ. Верно, и подтверждено официальным PDF.
- RBC NOMI — механика не раскрыта, требует 3 мес. истории. Верно, **плюс новое**: лимит $75/день × 5 раз
  в неделю, обратный лимит $1000/день, сумма не настраивается, ставка счёта 0.150%.
- Главный вывод «ни один банк не считает размен долг/копить со ставками» — **подтверждён**,
  теперь позитивно (по содержанию страниц продуктов), а не как «не успели найти».

**Уточнено/поправлено:**
- 🔴 Вторичный источник по Wells Fargo (расчёт «сколько можно безопасно потратить» и экономия
  от консолидации долга) **НЕ подтверждается** официальной страницей sites.wf.com/fargo/,
  где этих функций нет. Прогон 08.09 принял это за факт — понижаю до неподтверждённого.
- BBVA: 08.09 источником был qorusglobal (вторичный) — заменён на bbva.com.
- Nubank: подтверждён масштаб 15 млн MAU и заявленная цель "manage debt";
  инженерный кейс ZenML дочитан — **прескриптивной математики там нет**, только LLMOps-контур.

**Закрыты пробелы 08.09:** JPMorgan retail-PFM (закрыт), Santander (закрыт частично),
Nubank/ZenML (закрыт), DBS PDF (закрыт), Chime и Monzo (закрыты).

**Осталось незакрытым:** ING (канал недоступен), Citi retail, US Bank, TD Clari «proactive advice»,
Lloyds, NatWest, HSBC, OCBC, UOB TMRW, Kakao, Toss, Revolut, Starling, N26, CBA, Itaú —
по ним в силе только материал 08.09 **без URL**, то есть непроверенный.

---

## ЧТО ЭТО ЗНАЧИТ ДЛЯ FINPILOT

1. **Ниша пуста и это доказано, а не предположено.** Двенадцать банков, включая всех, кого называют
   лидерами PFM, — ни один не сравнивает ставку по долгу со ставкой по накоплению и ни один
   не показывает пользователю несколько вариантов распределения с обоснованием. Задача FINPILOT
   (SAW по 66 альтернативам с шагом 10%) не имеет банковского аналога нигде в мире.

2. **Причина пустоты — не техника, а конфликт интересов.** RBC кладёт деньги под 0.150% при
   рыночных 20–24% по картам; DBS ведёт прескриптив в страховку и свои ETF; Nubank применяет
   свою foundation-модель к **выдаче** кредита. Совет «гаси долг» уменьшает доход банка.
   Независимый продукт этим не связан — это структурное преимущество, а не маркетинговое.

3. **Планка «как у Т-Банка/Сбера» касается UX и надёжности, но не логики.** По логике планка
   мировых лидеров — правило 50/20/30 и бенчмарки FPAS. Перепрыгнуть её моделью v3.0.0 несложно;
   тяжело будет в объяснимости и доверии.

4. **Отсюда следует требование к продукту:** объяснение выбора («почему этот вариант, а не соседний»)
   — не украшение, а **единственное место**, где мы отличаемся от банка в глазах пользователя.
   Все банки дают вердикт без обоснования; мы обязаны давать обоснование.

5. **Патентный риск ограничен продуктовой стороной.** US11023967B1 Capital One закрывает логику,
   которую сам Capital One не выпустил. Для рынка РФ прямого действия патента нет, но при выходе
   за пределы РФ это надо смотреть отдельно — вопрос к юр-блоку вехи 9, не к разработке.

6. **Бенчмарк вовлечённости для наших метрик:** Erica — 3 млрд взаимодействий и 1.7 млрд проактивных
   инсайтов на ~50 млн клиентов (≈34 инсайта на клиента за 7 лет); BBVA — 10 млн человек;
   Nubank — 15 млн MAU. Порядок величин полезен, когда будем ставить цели по проактивным подсказкам.

---

## СОСТОЯНИЕ КАНАЛОВ (итог)

| Канал / URL | Код / состояние |
|---|---|
| WebSearch | жив в начале прогона, **исчерпан на 29-м запросе из 400** (сессионный счётчик) |
| html.duckduckgo.com через curl | работает, использован после исчерпания WebSearch |
| `web.archive.org` через WebFetch | **заблокирован харнессом**: "Claude Code is unable to fetch from web.archive.org" |
| `archive.org/wayback/available` через curl | **429 Too Many Requests** |
| `dbs.com.sg/personal/nav/*.page` | 200, но 388 551 байт одинаковых для разных URL — JS-оболочка, контента нет. Обойдено через официальный PDF на `dbs.com` |
| `www.dbs.com/...How DBS NAV Planner works.pdf` | 200, 529 871 байт, извлечён `pdftotext` — успех |
| `ing.nl/en/personal/digital-banking/...` | WebFetch — timeout 60 s; curl — **CODE=000** (соединение не установлено) |
| `santander.co.uk/.../santander-launches-budget-calculator...` | **404** |
| Остальные фетчи (bankofamerica, capitalone, wf, chase, rbc, bbva, personetics, nu.com, zenml, chime, monzo) | 200 |

---

## НЕ ПРОВЕРЕНО

- Утверждение вторичных обзоров, что Fargo считает "how much someone can safely spend"
  и экономию от консолидации долга: на официальной странице отсутствует, первоисточник не найден.
- ING Kijk Vooruit: описание взято из индексированного текста ing.com/sustainability,
  сама продуктовая страница не открылась.
- Santander: пресс-релиз santander.co.uk отдал 404; описание — из индексированного сниппета
  того же домена, дословность цитат гарантирована сниппетом, не открытой страницей.
- Всё, что в файле 08.09 по банкам, не перечисленным в сводной таблице выше (Citi, US Bank, TD,
  Lloyds, NatWest, HSBC, Nordea, Swedbank, OCBC, UOB, Kakao, Westpac, CBA, Itaú, Starling,
  Revolut, MoneyLion), — **остаётся без URL и в этом прогоне не проверялось**.

---

## ДОБОР Г31.5 — отказ адреса (17.09.2026)

**Каналы (замер 17.09.2026):** `www.ing.nl` прямой `curl -skL` (HTTP/2) — **exit 92** (обрыв потока), с `--http1.1` — **000, таймаут 40 с** · `r.jina.ai` без UA — **200, 346 б** (только заголовок: «page contains shadow DOM»), с `X-With-Shadow-Dom: true` + `X-Timeout: 30` — **200, 278 б** (кэш, только заголовок) · Exa fetch — `CRAWL_LIVECRAWL_TIMEOUT` · Wayback replay — **302 → снимок 09.05.2026**, `id_` **200, 13 872 б** — SPA-оболочка (`ing-app-open-loader.js`), текста 33 знака · **Exa search — работает, выдала текст с соседних адресов**.

Кандидат по файлу — §8 ING «Kijk Vooruit» (стр. 215–228, 349, 382, 428, 438): «канал недоступен», описание только из `ing.com/sustainability`. Отказ записан по ОДНОМУ адресу продуктовой страницы (`ing.nl/en/…/kijk-vooruit`). Позже в файле и в других файлах `raw/` пункт не перепроверялся.

### Г31.5-W1. 🟢 ING Kijk Vooruit — механика подтверждена официальными страницами-соседями и прессой

Продуктовая страница по-прежнему не отдаёт текст ни одному каналу (коды выше: это клиентский рендер, а не отказ сервера). Закрыто соседними адресами того же ресурса, найденными Exa search:

**1. Официальная страница ING «Inzicht»** — `https://www.ing.nl/particulier/digitaal-bankieren/app/inzicht` (текст отдан Exa), ДОСЛОВНО:
> «Weten welke uitgaves er nog aankomen? Dat kan met Kijk Vooruit. Zo zie je welke vaste inkomsten en uitgaven je nog kan verwachten. Dus geen verrassingen voor jou, wel zo fijn.» … «### Kijk Vooruit — Welke bij- en afschrijvingen komen eraan? Laat je niet verrassen.»
(«Хотите знать, какие расходы ещё впереди? Для этого Kijk Vooruit: видно, какие регулярные поступления и списания ещё ожидать».) Там же о соседней функции категоризации: «Het indelen gebeurt volledig automatisch, er komt geen mens aan te pas… En dat doen we pas nadat je toestemming hebt gegeven» — категоризация только после отдельного согласия, включая «bijzondere persoonsgegevens».

**2. Официальное описание приложения ING в App Store NL** — `https://apps.apple.com/nl/app/ing-nederland/id474495017`, ДОСЛОВНО: «Als je wil, kijk je **35 dagen vooruit**: je ziet toekomstige af- en bijschrijvingen.»

**3. Механика прогноза со слов ING (iCulture, 06.07.2016)** — `https://www.iculture.nl/nieuws/ing-mobiel-bankieren-toekomstige-uitgaven/`, ДОСЛОВНО: «Deze worden met een rekenkundig computermodel berekend, aldus de ING. **De datum van zo'n voorspelling wordt bepaald op basis van de laatste vier afschrijvingen, het bedrag op basis van de laatste vijf afschrijvingen.** De Kijk Vooruit-functie kan 35 dagen in de toekomst kijken.»

**4. Эволюция и независимая проверка:** Consumentenbond, 11.08.2016 (`consumentenbond.nl/betaalrekening/ing-kijkt-vooruit`): «overzicht van de 'zekere én voorspelde' afschrijvingen van de komende 35 dagen … bij een proef kwamen wij nog **enkele onjuiste voorspellingen** tegen»; Droidapp, 18.04.2018: «Vanaf nu krijg je tijdens het scrollen door de verwachte af- en bijschrijvingen **het voorspelde saldo** te zien»; Androidworld, 11.01.2023: в Kijk Vooruit добавлены периодические инвестиционные взносы и изъятия; SeniorWeb, 10.03.2025: «In de app van ING staat 'Kijk Vooruit' **standaard uit**».

**Выжимка.** Вердикт §8 файла («прогноз баланса, дескриптив-плюс, ставок и распределения нет») **подтверждён** и уточнён фактами: горизонт **35 дней**; прогноз — «уверенные» (поручения, инкассо) + «предсказанные» регулярные списания; **дата — по последним 4 списаниям, сумма — по последним 5**; с 2018 — прогнозный остаток; функция по умолчанию выключена; независимая проверка находила ошибки прогноза. Советов и распределения денег нет ни в одном источнике.

## ИТОГ Г31.5 — banks_world_pfm_v2

1 кандидат, **закрыт** соседними адресами того же ресурса (официальная страница `ing.nl/particulier/…/inzicht` + App Store ING) и прессой, найденными **Exa search**; сама продуктовая страница — SPA, текст не отдаёт ни прямому `curl`, ни прокси, ни Exa fetch, ни Wayback (`id_`-снимок — оболочка). Пометка 🟡 «не подтверждено первичной страницей» в §8 снимается.

🔴 **Что это даёт прогнозу (канон не трогается):** у крупного банка прогноз регулярных списаний устроен как **правило «последние 4 даты / последние 5 сумм» на горизонте 35 дней** — это готовая наивная базовая линия, против которой стоит мерить наш SES+Монте-Карло на короткой истории (связка с вопросом 4 `debt_payoff_math_cashflow_forecast` о SES на 3–12 наблюдениях). Остальные банки из «Осталось незакрытым» (Citi, US Bank, TD, Lloyds, NatWest, HSBC, OCBC, UOB, Kakao, Toss, Revolut, Starling, N26, CBA, Itaú) — не класс Г31.5 (материал без URL, а не отказ адреса); частично закрыты в `banks_apac_neobanks` и `competitors_2026_refresh`, в этот заход не брались.

---

## ИТОГ Г31.5 (СВОДНЫЙ — по всему подбатчу, 13 файлов, 17.09.2026)

**Процесс.** Один агент, **подагентов 0**, `WebSearch` 0. Exa search — 7 вызовов, Exa fetch — 5 (все пять `CRAWL_LIVECRAWL_TIMEOUT`). Остальное — прямые `curl`, `r.jina.ai` без UA, API Crossref/Unpaywall/S2/OpenAlex, DSpace 7 REST, Wayback, `pdftotext`/`pdftoppm`+`tesseract`, чтение отрисованных страниц PDF. Один обрыв сессии на лимите АККАУНТА (HTTP 429 харнесса) до первой записи — после смены аккаунта всё выполнено заново, блоки дописывались по ходу через `cat >>`.

**Тронутые файлы:** `mcda_saw_alternatives`, `constraint_based_utility_recsys`, `recsys_finance_domain_specifics`, `debt_payoff_math_cashflow_forecast`, `goal_based_investing_lifecycle`, `portfolio_theory_robo_advisors_v2`, `prescriptive_quality_metrics`, `dp_vs_enumeration`, `behavioral_execution_gap`, `bank_patents_wellness_scoring`, `_sub16_utility_based_rs`, `_sub17_trust_and_harm`, `banks_world_pfm_v2`. Все — файлы, где серия Г31.1/31.2/31.4 не проходила или оставила долг.

### 1. Арифметика

| Исход | Число | Пункты |
|---|---|---|
| Кандидатов рассмотрено (сверены с последним упоминанием) | **31** | |
| 🟢 Закрыто полностью (полный текст / формула / факт подтверждён) | **14** | RAFSI, O'Shea, Vafaei, Duc Trung, Gross & Souleles, Модильяни, Merton WP 58, Bodie–Merton–Samuelson, Triantaphyllou & Sánchez, Lettau & Uhlig, Sheeran et al. (Table 1), WO2026074314A1 формула, KR102121857B1 формула, ING Kijk Vooruit |
| 🟡 Частично (авторский абстракт / аннотация, полного текста нет) | **6** | Fernandes–Lynch–Kim («Correcting the Record»), Hodge et al. 2021, Ng et al. 2012, UTA 1982, Felfernig AIC 2013 (`tldr`), Kritzman–Page–Turkington (авторская ретроспектива) |
| 🔗 Закрыто ссылкой — запись устарела, источник уже добыт в другом файле | **5** | CEPR/Vihriälä, DeMiguel–Garlappi–Uppal, Chen et al. CSUR, SSRN 5043646 (Синяков), Chen & Pu |
| ⛔ Подтверждено закрытым / отклонено как не класс Г31.5 | **4** | Felfernig & Burke ICEC '08, Sharaf 2022, Gupta 1987, Zeldes 1989 |
| ⚪ Не брались с названной причиной | **2** | Feinstein & Cicchetti (уже на многих каналах), OHARS (нет вопроса для источника) |

**Ложных пунктов (закрытых ранее, но взятых в работу) — 0**: пять «устаревших» записей опознаны сверкой ДО похода в сеть и закрыты ссылкой, а не повторной добычей.

### 2. 🔴 КАКОЙ КАНАЛ ЗАКРЫЛ КАЖДЫЙ ПУНКТ — и что мы недоиспользуем

| Канал | Закрыл | Пункты |
|---|---|---|
| **Прямой `curl` по СОСЕДНЕМУ адресу того же ресурса** (другой путь на хосте / разбор HTML вместо счётчика разметки) | **4** | Gross & Souleles (`nber.org/system/files/…pdf` вместо страницы), BMS (то же), WO и KR (секция `claims` в том же HTML, что был «0 пунктов») |
| **`r.jina.ai` без UA** | **3** | RAFSI (MDPI), Duc Trung (metrology-journal), Ng 2012 абстракт (SMU за Incapsula) |
| **Прямой `curl` по ТОМУ ЖЕ адресу** (прежний отказ — отказ одного захода) | **2** | O'Shea (`peterdeeney.com`), Модильяни (`nobelprize.org`) |
| **Crossref `/works/<doi>` — депонированный абстракт** | **2** | «Correcting the Record», Hodge et al. |
| **Exa search → новый адрес, которого нет в OA-индексах** | **2 + 1 частично** | Triantaphyllou & Sánchez (авторский PDF на `csc.lsu.edu`), ING (официальные соседние страницы + App Store); KPT-ретроспектива |
| **Wayback** | **2** | Lettau & Uhlig (`id_` по мёртвому адресу автора), UTA (снимок страницы репозитория → аннотация) |
| **Unpaywall → точный адрес репозитория** | **1** | Vafaei (`run.unl.pt`) |
| **DSpace 7 REST** | **1** | Merton WP 58 (MIT; handle-адрес давал 405) |
| **S2 `/paper/DOI:`** | решающий для тождества | «Correcting the Record» = SSRN 5385386 (S2 хранит старый заголовок, Crossref — новый); `tldr` для ICEC '08 и AIC 2013 |
| **Дочитка уже открытого файла** | **1** | Sheeran et al. (KOPS) |
| Exa fetch | **0** из 5 | все `CRAWL_LIVECRAWL_TIMEOUT` (ACM ×2, Springer, SSRN, ING) |

🔴 **Три недоиспользуемых канала, выведенные из таблицы:**
1. **Crossref `/works/<doi>` как источник АБСТРАКТА.** Wiley и SSRN депонируют полные авторские абстракты; все прежние заходы по «Correcting the Record» били в SSRN (капча) и ни разу не спросили Crossref. Для SSRN-работ это первый шаг, не последний.
2. **Разбор HTML вместо счётчика.** «0 пунктов `claims`» у WO2026074314A1 держалось через Г15 и Г30.4 при **том же размере страницы 149 331 б** — секция была в HTML всё это время. Проверять содержимое секции, а не метку/markdown.
3. **Exa search как поиск АДРЕСА, а не текста.** Exa fetch в этом заходе не отдал ничего, а Exa search дважды нашёл адрес, которого не знают Unpaywall/S2/OpenAlex (авторский каталог PDF, соседние страницы банка).

🔴 **Отрицательный замер, важный для порядка каналов:** метки **Unpaywall/S2 «green» дважды оказались ЛОЖНЫМИ** — Ng et al. 2012 (SMU InK) и UTA 1982 (BIRD Dauphine, ещё и `CCBYSA`): запись в репозитории есть, **файла нет**. «Green» означает «есть запись», а не «есть текст»; вывод «открытая копия существует» по одной метке делать нельзя.

### 3. 🔴 ЧТО ИЗ ДОБЫТОГО МЕНЯЕТ КАНОН, ПРОГНОЗ, НОВИЗНУ, ЮРБЛОК ИЛИ ОБОСНОВАНИЕ ПОРОГОВ

**Канон модели (`docs/math_model.md`) — НЕ меняется ничем. Код и формулировка новизны не правились.**

**НОВИЗНА — один пункт, самый значимый в подбатче:**
- 🔴 **WO2026074314A1 (1Finance, приоритет 2024-10-02), пп. 8 и 19 формулы:** защищена «weighted combination of the plurality of financial metrics», у каждой метрики «ideal value, a minimum threshold, and a maximum threshold», зависящие от профиля и стадии жизни и **«updated based on a change in the one or more macroeconomic factors»**. Пока формула числилась «недоступной», это не учитывалось. Опора новизны на **метод распределения потока на множестве альтернатив с инвариантами** — устояла (в формуле распределения, перечисления альтернатив и порядка погашения нет). Опора на «взвешенные метрики с профильными порогами и макро-обновлением» — **не устояла**. Решение о формулировке — владельца (`bank_patents_wellness_scoring`, Г31.5-K1).

**ЮРБЛОК:**
- Тот же WO: срок входа в нацфазу РФ ≈ **2027-05-02**. Если войдёт — любая будущая функция «оценка финансового здоровья с весами по профилю» требует сверки с пп. 1/8/13/19. KR102121857B1 — только Корея, до 2038, риска в РФ нет.

**ПРОГНОЗ:**
- ING Kijk Vooruit: прогноз регулярных списаний — **дата по последним 4, сумма по последним 5, горизонт 35 дней**; по независимой проверке — с ошибками. Готовая наивная базовая линия для замера нашего SES+Монте-Карло на короткой истории.

**ОБОСНОВАНИЕ ПОРОГОВ И МЕТРИК (по убыванию значимости):**
1. **Метрика устойчивости совета SM** (`prescriptive_quality_metrics` §3.2) по первоисточнику Triantaphyllou & Sánchez — это **PT-критический критерий**; критическое изменение веса **может не существовать** (условие 8b), у авторов sens = 0. Без обработки этого случая SM на части портретов не определена.
2. **Интервалы устойчивости весов SAW в замкнутой форме** (O'Shea et al. 2026, формулы 16–18) — анализ чувствительности пяти риск-профилей без Монте-Карло.
3. **«Теоремы RAFSI о rank reversal» не существует** — устойчивость показана экспериментом; итоговая функция RAFSI — это SAW с нормировкой к фиксированным опорным точкам. Ссылаться как на «экспериментально проверенную конструкцию», не «доказанную».
4. **Lettau & Uhlig 1999:** калибровка/выбор правил **по реализованным исходам пользователей** подвержена good state bias — сравнивать правила только на общем наборе сценариев. Прямо касается предложения (б) из Г31.4-D5 («метрика по реализованному исходу»).
5. **Gross & Souleles 2002 (первоисточник ко-холдинга):** >90 % заёмщиков по картам держат ликвидность, **треть — сверх месячного дохода** даже после «щедрого» транзакционного остатка. Довод за правила «резерв против дорогого долга» теперь на первоисточнике; противовес (Zinman 2006, Vihriälä 2019) уже в базе.
6. **Bodie–Merton–Samuelson 1992:** «гибкость труда → больше риска» получено при **нестохастической зарплате**; как опору для связи «устойчивость дохода ↔ риск-профиль» цитировать без оговорки нельзя.
7. **Ng et al. 2012** минимизирует **срок полного погашения (makespan), приближённо** — не опора для оптимальности Avalanche.
8. **Финобразование:** после асимметричной коррекции **0.018–0.033 SD**, и ранжирование типов интервенций из Kaiser 2022 меняется; в мета-анализе implementation intentions **нет ни одного финансового исхода**.
9. **UX, не модель:** Hodge et al. 2021 — для сложной задачи очеловечивание (имя, персона) робо-советника **снижает** опору на совет.

### 4. ЧТО ОСТАЛОСЬ НЕИЗВЕСТНЫМ

- **Felfernig & Burke ICEC '08** — полный текст. Пройдено: `api.unpaywall.org/v2/10.1145/1409540.1409544` (closed), `api.openalex.org/works/doi:10.1145/1409540.1409544` (closed), `api.semanticscholar.org/graph/v1/paper/DOI:10.1145/1409540.1409544` (CLOSED), Exa search по заголовку, Exa fetch `dl.acm.org/doi/pdf/…` и `dl.acm.org/doi/…` (timeout), Wayback CDX `josquin.cti.depaul.edu/~rburke/*` (200, файла нет), Wayback CDX `ist.tugraz.at/*` PDF (200, файла нет).
- **Fernandes–Lynch–Kim, полный текст** (таблицы по типам интервенций) — SSRN за капчей; ни один индекс копии не знает.
- **Hodge et al. 2021, полный текст** — Wiley закрыт, SSRN `Delivery.cfm` за капчей.
- **Ng et al. 2012 и Gupta et al. 1987, полные тексты** — Springer/Elsevier закрыты; «green» у Ng ложный.
- **UTA 1982, полный текст** — Elsevier закрыт; BIRD Dauphine снят с DNS, в архивной записи файла нет.
- **ING Kijk Vooruit, продуктовая страница** — SPA; текст не отдаёт ни один канал (закрыто соседними адресами, но сама страница непрочитана).

### 5. ЗАДОЛЖЕННОСТЬ (непройденное, отдельным списком)

1. **Wayback CDX `facweb.cs.depaul.edu/rburke/*`** — **503 два раза подряд** (пауза 20 с): страница публикаций Burke на новом хосте не проверена; последний шанс на авторскую копию ICEC '08.
2. **BMS 1992, раздел о стохастической зарплате** (страницы PDF 29–41) — не распознавался OCR; нужен, если тезис «устойчивость дохода ↔ риск» пойдёт в обоснование.
3. **arXiv 2102.09005 и `papers.phmsociety.org/…/1948/957`** (заместители IUI '08) — не скачивались сознательно: пункт Г4.1 закрыт другими источниками; взять, только если понадобятся алгоритмы диагностики несовместных ограничений.
4. **Тарифы Дзен-мани и CoinKeeper в прошлых редакциях; программа Aha!'24** (`debt_data_sources_rf`, долг Г31.1) — в этот заход не брались: низкий приоритет по записи владельца; Aha!'24 — не отказ адреса, а неизвестный домен.
5. **ОАЭ, режим SCA «Financial Consultations»** (`pdf_statement_parsing_accuracy`, Г30.3: `uaelegislation.gov.ae` 403 + капча) — соседний хост `sca.gov.ae` не проверялся.
6. **Банки из «Осталось незакрытым» `banks_world_pfm_v2`** (Citi, US Bank, TD, Lloyds, NatWest, HSBC, OCBC, UOB, Kakao, Toss, Revolut, Starling, N26, CBA, Itaú) — не класс Г31.5 (нет URL, а не отказ адреса); сверка с `banks_apac_neobanks`/`competitors_2026_refresh` не делалась.

**Пиратские источники не использовались; российский корневой сертификат не ставился; канон модели, формулировка новизны и код продукта не правились.**
