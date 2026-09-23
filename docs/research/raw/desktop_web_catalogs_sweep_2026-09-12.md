# Г14 — Десктоп, веб и открытый код: сплошной обход каталогов (сырьё, 12.09.2026)

## Г14.0 — метод и каналы

- Разбор задачи: предмет — продукты вне мобильных магазинов (открытый код, скачиваемый десктоп,
  веб-SaaS, реестр РФ, стартапы в разработке, академические прототипы). Форма ответа — реестр
  с поштучной классификацией + таблица советников + прямой ответ.
- Классы: **трекер** (учёт, категории, отчёты); **планировщик** (бюджет/конверты/прогноз, решение
  принимает человек); **советник** (продукт сам вычисляет, куда направить деньги). Одноконтурный
  советник по долгам (avalanche/snowball-калькулятор, сам ранжирующий долги) отмечается отдельно,
  как в Г13.
- Классификация — по описанию/README целиком, с дословной цитатой. Фильтр по словам — только для
  сужения каталога до обозримого списка.
- Субагентов в этой теме: 0 (вся работа — машинные API + поштучное чтение самим лидером).
- Сырьё — `/private/tmp/g14/` (JSON-выдачи GitHub, Homebrew, iTunes, скрипты).

## Г14.1а — Maybe Finance: почему ушли из B2C и чем кончилось (первоисточники)

**Статус репозитория** (GitHub API, 12.09.2026): `maybe-finance/maybe` — `archived: true`,
последний push 2025-07-24, 54 285★, 5 680 форков. README дословно: «This repository is no longer
actively maintained. You can read more about this in our final release.»

**Хронология по первоисточникам (три поворота, а не один):**

1. **2021–2023, первая жизнь.** Failory, 18.01.2024 (вторичный разбор, цифры со слов основателя):
   привлекли $1,45 млн от 1 300 инвесторов через Republic; команда 8 человек, 18 месяцев
   разработки; на запуске «10,000+ waitlist members but only 50 paying customers», средняя
   подписка $15/мес; команда сокращена до 3; остаток ~$240 000 ушёл в пивот Detangle (legal tech).
   Причины по Failory: тайминг («the DIY approach to finances was now hard to sell» после краха
   рынка 2022), Plaid «promised a lot but didn't deliver», «aimed to solve every edge user case».
   HN-заголовки того же периода: «Maybe pivots to an AI finance chatbot» (05.05.2023),
   «To Investors and Customers: The Future of Maybe» (26.06.2023).
   https://newsletter.failory.com/p/3-reasons-maybe-failed
2. **Январь 2024 — открытие кода** («$1M personal finance and wealth management software now free
   and open-source», HN 12.01.2024, 47 очков) и перезапуск как коммерческий open-source
   (self-hosted бесплатно + платная облачная версия).
3. **22.07.2025 — пивот в B2B.** Пост Джоша Пигфорда (основатель, ранее Baremetrics), дословно
   (добыт через `api.fxtwitter.com`, x.com через jina заблокирован):
   > «We're about 6,000 paying customers short of breaking even, with only around 200 paying
   > customers currently, most of whom joined during the beta phases when the cost was
   > significantly lower.»
   > «The reality is that building a B2C personal finance platform is not only technically very
   > challenging, but incredibly slow to grow, and we can't tackle those challenges while creating
   > additional features people might be willing to pay for within the next 10-12 months (our
   > current runway).»
   > «I no longer believe a B2C personal finance app is our best bet for survival going forward.
   > The market's needs are too fragmented, and the feature set is too far from becoming valuable
   > for more affluent customers. I believe it either has to be completely bootstrapped for years
   > or have $10's of millions in funding to sustain and pour into growth.»
   > «We've got roughly $400,000 left in the bank.»
   > «We're pivoting to B2B financial forecasting & scenario planning tools. Specifically, we're
   > focusing on natural-language, generative-UI + UX for creating reports…»
   > FAQ: «What about going AI + mobile first? — I still think that's the best move for any new B2C
   > personal finance app… but we don't have the runway to pull it off.» «What about paying
   > subscribers? — We'll stop monthly billing and refund everyone's most recent payment.»
   https://x.com/Shpigford/status/1947725345244709240
4. **24.07.2025 — финальный релиз v0.6.0 «Farewell… Maybe»** (текст сохранён целиком:
   `/private/tmp/g14/maybe_final_release.md`, 13 680 символов). Ключевое дословно:
   > «our obligation as a company is to our investors… we've determined that continuing to build
   > this app is not our best chance at paying back our investors»
   > «Aside from the fact that growing a B2C SaaS app is challenging in its own right from a
   > business perspective…»
   > «The single biggest challenge with a personal finance app in 2025 is bank providers… most users
   > churn if even *one* of their banks is unsupported… Bank provider data being plain *wrong*»
   > «is the primary reason why "bootstrapping" a personal finance app with automated bank syncing
   > is an uphill battle. You need a lot of money and time to get this right.»
   > «We are open source, but in order to fix data bugs, we need to look at the data. If the user
   > can't share all the required information, we can't reproduce the issue.»
   Что продукт умел (из того же релиза): net worth, транзакции, бюджеты по категориям,
   AI-чат «that knows your finances and can answer questions», мультивалютность, правила, CSV.
   🔴 **Класс: трекер + бюджет + AI-чат вопросов-ответов. Расчёта распределения денег нет.**
   Философия дословно: «Most people need to know just a few important things… How much money do
   I have? Am I spending less than I'm earning?… we believe most users are satisfied with less».
   https://github.com/maybe-finance/maybe/releases/tag/v0.6.0
5. 🔴 **Начало 2026 — B2B-пивот ТОЖЕ не сработал, компания распущена.** Пигфорд, 31.03.2026:
   > «At the beginning of the year we made the decision to shut down Maybe Finance… we explored
   > a number of directions, from the original personal finance app through legal tech, marketing
   > automation, B2B finance, and financial APIs. None found the traction or economics needed to
   > build a sustainable, venture-backed business. We're now in the process of… liquidating all
   > assets.» «…the nearly 1,800 investors.»
   https://x.com/Shpigford/status/2038774838475805081
   Страница распродажи (Notion, опубл. 09.07.2026 по заголовку jina): «After five years, we're
   unfortunately dissolving Maybe Finance, Inc.»; на продажу 26 доменов (maybe.co, maybe.app,
   detangle.ai, meetsynth.ai), 40+ репозиториев, 100+ Figma-проектов; «we couldn't make the
   economics work as a venture-backed startup»; «Absolutely no user/employee/company data will
   be included»; приём предложений до 30.04.2026. https://maybefinance.notion.site/asset-sale

**Что стало с пользователями.** Платным подписчикам (≈200) — остановлено списание и возвращён
последний платёж (пост 22.07.2025). Self-hosted пользователи ушли в **community-форк `we-promise/sure`**
(«The personal finance app for everyone (by everyone)»): 9 866★, последний push 2026-09-12 —
**жив и активен** (GitHub API). Выход на HN 01.05.2026.

**Трактовка для FINPILOT (моя, не источника):**
- Maybe — не контрпример нашему жанру, а контрпример **трекеру с банковской синхронизацией
  на венчурных деньгах**: главной статьёй потерь назван Plaid и качество банковских данных.
  FINPILOT на ручном вводе этот класс затрат не несёт (но несёт трение ручного ввода).
- Число, пригодное для юнит-экономики: при $15/мес им нужно было ≈6 200 платящих, чтобы выйти
  в ноль при команде ~3–5 человек; реально было ~200 после 4 лет и 54 тыс. звёзд. **Звёзды
  на GitHub не конвертировались в платящих: 54 285★ → ~200 подписчиков (≈0,4 %).**
- 🔴 **Для тезиса «масштаб в B2B»: история Maybe его НЕ подтверждает.** B2B-пивот (прогнозирование
  для бизнеса) прожил ~5 месяцев и закончился роспуском. Причём пивотировали не в B2B2C
  (продажа PFM банкам/работодателям), а в другой продукт для другого покупателя — так что это
  свидетельство против «пивот спасает», а не прямая проверка нашего варианта B2B.

## Г14.1 — открытый код (GitHub)

**Срез.** 21 запрос к `api.github.com/search/repositories` (без токена, пауза 7 с): темы
`personal-finance` (4 589, 2 стр.), `budgeting` (1 368, 2 стр.), `money-management` (459), `debt` (129),
`finance-tracker` (726), `expense-tracker` (4 319), `personal-finance-management` (9); ключевые запросы
`debt payoff` (438), `debt snowball avalanche` (79), `debt avalanche` (111), `financial planning personal`
(1 122), `fire calculator` (1 017), `budget optimizer` (3 271), `cash flow allocation`, `financial planner`,
`zero-based budget`, `envelope budgeting` (469). Взято по топ-100 по звёздам с каждого.
**Итого 1 489 уникальных репозиториев** (`/private/tmp/g14/gh_all.json`). Из них:
- **134 с ≥100★** — описание каждого прочитано поштучно (`gh_big.tsv`);
- **716 с «плановыми» словами** (optimi/allocat/debt/payoff/snowball/avalanche/planner/advis/FIRE/forecast)
  — отфильтрованы ещё раз на ≥3★ и прочитаны поштучно (≈230 строк, из них ~60 — шум: оптимизация
  рекламных бюджетов, токенов LLM, облака, спутников — «budget» в другом смысле);
- **41 README скачан и прочитан** по кандидатам с признаками расчёта (`/private/tmp/g14/readme/`).
🔴 Урок метода подтвердился: запрос `budget optimizer` (3 271) почти целиком — маркетинг, LLM-токены
и облако; ни одного PFM-оптимизатора распределения он не дал.

### Классы среди 134 репозиториев с ≥100★ (поштучно по описанию)

| Класс | Сколько | Примеры с цитатой |
|---|---|---|
| Трекер / учёт (в т.ч. двойная запись) | ≈68 | Firefly III (24 588★, push 12.09.2026) «a personal finances manager»; ezbookkeeping (5 564★) «self-hosted personal finance app»; Money Manager Ex (2 264★, десктоп C++); Paisa (3 209★, ledger); Securo (3 303★, «Open-source personal finance manager. Self-hosted, privacy-first»); Sure (форк Maybe, 9 866★); Whisper Money (1 121★) «Understand your personal finances» |
| Планировщик (конверты/бюджет/прогноз, решает человек) | ≈17 | Actual Budget (28 711★) «A local-first personal finance app» — конвертный, есть шаблоны целей; budgetzero (656★) «zero-based budgeting»; OpenBudgeteer (973★) «Bucket Budgeting Principle»; MyFin (308★) «forecast your financial future»; YAFFA (108★) «focusing on the support of long term financial planning»; ignidash (280★) «AI-powered alternative to ProjectionLab for planning your long-term personal finances»; budget-board (884★) «working towards financial goals»; financial-freedom (2 922★) «open source alternative to Mint, YNAB»; helius (199★) «cashflow forecasting»; jelly-fin (102★) «manage your finances with forecasting» (мёртв, 2020) |
| Трекер инвестиций / wealth | 7 | Ghostfolio (9 283★) «Wealth Management Software»; Sossoldi (1 393★) «Net Worth tracking»; foliofox (129★) «AI-powered financial advisor… your portfolio» — советник по портфелю, не по бюджету |
| Трекер подписок / сплит | 7 | Wallos (8 488★), split-pro, abrechnung, wapy.dev, SubTracker |
| **AI-советник общего вида (LLM)** | **2** | **Ray Finance** (303★), Finance-Guru (317★, «family office engine… Agents propose. Typed code computes» — инвестиции) |
| Библиотеки / импорт / SDK / клиенты | ≈14 | monopoly, StatementSensei, ofxstatement, plaid2qif, ynab-sdk-js, pynYNAB, data-importer, bankmcp |
| Руководства / тексты / шум | ≈19 | financial_lessons, jch/personal-finance; KitchenOwl, TimeScribe, эмулятор TI Nspire, POS lakasir, syftr, маркетинг-аналитика |

Живость: из PFM-продуктов с ≥1 000★ живы (push в сентябре 2026) все, кроме Maybe (архив), mintable
(2023), Expenso (2023), my-budget (2023), jakubgarfield/expenses (2024), range-of-motion/budget (2024).

### 🔴 Кандидаты с расчётом (README прочитан целиком или по разделам)

**1. Ray Finance — `cdinnison/ray-finance` (303★, MIT, создан 10.03.2026, push 01.08.2026), CLI + сайт rayfinance.app.**
Самое близкое к нам по ПОЗИЦИОНИРОВАНИЮ во всём срезе. Дословно:
> «Other finance apps show you what you spent. Ray tells you what to do.»
> «Dashboards show. Ray tells. Monarch, Copilot, YNAB, Mint — they sort your transactions into pie charts
> and call it insight. You still have to figure out what to do next.»
> Пример ответа: «You've got $34,200 across two cards and a car loan. At $95k with a baby coming in March,
> pause the Japan fund and throw that $440/mo at the Chase card — it's at 24.9%.»
> «CFO personality — Ray doesn't list options. It tells you what it would do and why»
Механика: Plaid/Bridge → локальный SQLite (AES-256) → **LLM API** (Anthropic/OpenAI/Ollama), профиль
в `~/.ray/context.md`. Детерминированного оптимизатора распределения в README нет — совет генерирует
модель. Цена: self-hosted $0 (свой ключ, «~$1–3/month in AI provider costs»), **Ray Pro $10/мес**.
Аудитория: npm `ray-finance` — **3 954 скачивания с 01.01 по 11.09.2026, 54 за последний месяц**;
сайт: «94 installs this month». Жив, но затухает. Только США/Канада/ЕС (Plaid/Bridge).
Класс: **советник общего вида на LLM** (долг + цели в одном ответе — да; резерв — упоминается; расчёт
не детерминированный, объяснение — текст модели). Прямой аналог Origin AI Advisor из Г11 в открытом коде.

**2. Fiduciary — `weklund/fiduciary` (10★, MIT, июль 2026).** Claude Code skills + Plaid CLI + SQLite.
> «You: "Should I pay off my credit card or keep cash reserves?" Advisor: walks your actual balances and
> rates through a priority framework, accounts for your constraints, gives a specific recommendation with
> the math»
Класс: советник на LLM-агенте (долг vs резерв — да). Не продукт, а набор навыков для разработчика.

**3. Класс «Claude/агент-скиллы по личным финансам» (2026) — новый класс, в Г13 не виден вовсе:**
zubair-trabzada/ai-finance-claude (61★): «Debt Payoff Strategy — avalanche vs snowball comparison»,
«prioritized action plan»; googlarz/finance-assistant (42★): «real math, not AI guesses… debt
avalanche/snowball, FIRE with 10,000-path Monte Carlo», модуль «Debt Optimizer»; openaccountant/skills
(68★): отдельные скиллы `debt-payoff`, `emergency-fund`, `zero-based-budget`;
dungnotnull/comprehensive-finance-consultant-agent-skill (6★): «13 deterministic calculator engines (debt
avalanche…)», «prioritizedRecommendations»; cjpatten/canadian-finance-planner-skill (54★), satasuk03/
thai-personal-finance-planner (19★): «Phased action plan — Stabilize (emergency fund + high-rate debt) →
Build… → Accelerate». 🔴 **Это ближайшее к нашей логике «резерв + дорогой долг сначала», но в виде
фиксированной лестницы (как Ramsey), исполняемой LLM, а не расчёта.** Аудитория — десятки звёзд.

**4. Одноконтурные калькуляторы долга (детерминированные):**
- `Aparajith24/better-debt` (12★, авг. 2026): «avalanche vs. snowball strategies (and an optimal,
  prepayment-cap-aware strategy when a loan penalizes paying it down too fast)», true APR для «flat rate»,
  проверка оферты перед подписанием: вердикт «GOOD_TIME / TIGHT / NOT_RECOMMENDED». Только долги.
- `Luigi-PastorePica/FreeD` (4★, 2026): «calculate and recommend which [debt]… where to allocate money
  above the minimum payments». Только долги, ранняя стадия.
- `cwinland/DebtPaymentPlan` (15★, 2022), `bradymholt/debt-paydown-calculator` (12★, 2018),
  `AndraeRay/debt-snowball` (9★, 2015), `seanrmilligan/avalanche` (5★, 2018), `bertvandepoel/tabby`
  (74★, 2022, «manage debt» между людьми — не то), `rback37/debt-world` (5★, 3D-город, «not a financial
  adviser»), `mrwade/tanstack-db…` (37★ — демо фреймворка на примере калькулятора долга).
- `jackob25-PTPCS/Envelopes` (5★): конверты Ramsey + «Snowball and Avalanche planners».

**5. Пограничные «несколько контуров рядом»:**
- `apowell656/gnucash-financial-radar` (7★, GPL-2.0, push 02.09.2026) — отчёты для GnuCash: «Emergency
  fund progress», «Budget Report with Sinking Funds», долги по «Snowball… Avalanche… Custom priority»,
  и «collapsed monthly funding recommendation» для целей. **Три контура рядом, но каждый отдельным
  отчётом; выбора между ними нет.** Планировщик.
- `oofangoo/personal-finance-planner` (23★, мёртв с 08.2025): «prioritize financial goals… smart
  allocation», «Monthly allocation breakdown». Только цели по приоритету пользователя.
- `solid-logic-studios/bucketwise-planner` (16★): Barefoot Investor — **фиксированные доли**
  «60% Daily Expenses, 10% Splurge, 10% Smile, 20% Fire Extinguisher» + snowball + опц. AI-советник.
  Распределение есть, но константное, не расчётное.
- `LucasFernandesCS/finance-planner` (5★, июнь 2026): описание «managing income, fixed and variable
  expenses, debts, reserves, and shared financial goals» — **три контура в описании**, README —
  только инструкция сборки (БД `family_dreams`). Спорно: механика не раскрыта, стадия — каркас.
- `hail2victors/n8n-Actual-Automation` (131★): «envelope auto-funding» для Actual — автоматизация
  правил пользователя.
- `Marcin99b/Predictor` (7★): «How long until I have 6 months of expenses saved?» — прогноз, не выбор.

**Итог Г14.1:** в открытом коде **нет** проекта, который детерминированно распределяет свободный
остаток между досрочным погашением (по ставке), резервом и целями. Есть: (а) LLM-советники общего
вида — Ray (единственный с продуктом и ценой), Fiduciary, пачка агент-скиллов 2026 года; (б) калькуляторы
одного контура долга; (в) планировщики, где три контура лежат рядом, но решает человек (GnuCash Radar,
Actual с шаблонами целей). Самый массовый пласт (Firefly, Actual, Maybe/Sure, ezbookkeeping) — учёт.

## Г14.2 — софт, который качают с сайта (Homebrew Cask) и Mac App Store

### Homebrew Cask (реестр macOS-софта со своих сайтов)
**Срез:** `formulae.brew.sh/api/cask.json` — HTTP 200, 18 784 449 байт, **7 712 casks**; установки за
365 дней — `analytics/cask-install/365d.json` (23 330 строк). Два прохода фильтра: (1) финансовые слова →
**67 кандидатов**; (2) расширенный (pay/bill/coin/wallet/fund/account/subscription + имена известных PFM:
MoneyWiz, Money Pro, Chronicle, Lunch Money, Tiller, YNAB, HomeBank, KMyMoney…) → ещё **77**. Описание
и домашняя страница каждого из 144 прочитаны. Второй проход **не дал ни одной новой PFM-программы**:
там криптокошельки (Electrum, Trezor, Monero…), шум (4K Stogram, «Monarch» — это Spotlight-лаунчер
monarchlauncher.com, **не Monarch Money**) и каталог Setapp (подписка на набор приложений — отдельный
канал, не продукт).

**PFM-программы в Homebrew (все, по установкам за год):**

| Cask | Установок/год | Описание cask (дословно) | Класс |
|---|---|---|---|
| gnucash | 1 761 | «Double-entry accounting program» | трекер (двойная запись) |
| actual | 889 | «Privacy-focused app for managing your finances» | планировщик (конверты) — открытый код, см. Г14.1 |
| copilot-money | 757 | «Track and budget money» | трекер + бюджет — разобран в Г11/Г13 |
| moneymoney | 607 | «German banking and financial management software» | трекер (банкинг DE) |
| quicken | 363 | «Personal finance manager» | трекер + планы (Quicken Classic Mac) |
| banking-4 | 250 | «German accounting software» | трекер (банкинг DE) |
| banktivity | 149 | «App to manage bank accounts in one place» | трекер + бюджет |
| mmex | 107 | «Money management application» | трекер (открытый код) |
| moneydance | 105 | «Personal financial management application focused on privacy» | трекер |
| buckets | 81 (+3 beta) | «Budgeting tool» | планировщик (конверты), budgetwithbuckets.com |
| moneymanager | 67 | «Finance manager» — realbyteapps.com | трекер (Realbyte, есть в папке владельца, Г11) |
| grisbi | 23 | «Personal financial management program» (**cask отключён**) | трекер |
| pecunia | 10 | «Online banking app with support for HBCI» | трекер (банкинг DE) |
| prudent | 5 | «Integrated environment for your personal and family ledger» | трекер (plain-text ledger) |

Рядом, но не PFM: инвестиции (portfolioperformance 971, wealthfolio 293, rotki 226), торговые терминалы
(tradingview 3 887, webull, longbridge, ths…), налоги (WISO Steuer, TurboTax, IRPF), счета-фактуры
(GrandTotal, Billy, Billings Pro), CashNotify (Stripe/PayPal в меню-баре), QuickBooks Desktop.
🔴 **Советников в Homebrew: 0.** Весь скачиваемый macOS-PFM — это учёт и конверты; самый массовый
продукт жанра (GnuCash) ставят ~1 800 раз в год через brew. Абсолютные числа — только пользователи
Homebrew с включённой аналитикой, это нижняя граница, не охват.

### Mac App Store
**Срез:** 28 поисковых запросов `entity=macSoftware` (14 запросов × `country=us|ru`: personal finance,
budget, money manager, debt payoff, expense tracker, home accounting, financial planning, net worth,
budgeting software, «бюджет», «домашняя бухгалтерия», «учет расходов», «финансы», «долги») →
**735 уникальных Mac-приложений, из них 616 — жанр «Финансы»**. Описание каждого из 616 прогнано по
признакам расчёта (avalanche/snowball/emergency fund/recommend/advis/allocat/подушк/досрочн/погашени/
долг/совет/распредел/резерв) → **130 совпадений, прочитаны поштучно** (`/private/tmp/g14/mas/hits.txt`);
плюс топ-60 по числу оценок прочитан отдельно — там крупные трекеры без «плановых» слов.
🔴 **Чарты Mac App Store по жанру не отдаются:** `itunes.apple.com/<cc>/rss/topfreemacapps/.../genre=N/json`
вернул 0 позиций для всех N от 12001 до 12022, тогда как без жанра — 5 из 5. То есть «срез популярного»
по категории «Финансы» для Mac классическим RSS невозможен; сплошной обход — только поиском.

**Крупные по оценкам (топ, поштучно):** CoinStats (85 428, крипта), Currency converter (70 883),
Copilot Money (30 247 — Г11/Г13), **Loan Calculator – Debt Planner** (22 497; кредитный калькулятор:
«how extra payments can save you thousands», «7 bonus calculators including credit card payoff» —
калькулятор, не советник), Spending Tracker (19 400, трекер), MoneyCoach AI Budget Planner (2 645;
«Personalised Budgets — Smart budgets that will help you save money» — трекер с умными бюджетами),
MoneyWiz 2026 (2 155; «Tracking for bank and credit accounts, loans and debts, budgets and goals» —
трекер), Alzex Finance (1 009 + 715; «Учет долгов и кредитов» — трекер, российский разработчик),
Budget Planner – Money Flow (737, трекер), iFinance 5 (143, $19.99, трекер), Banktivity (139, трекер),
Foreseenly (169; «Check how a purchase or extra debt payment affects the weeks and months ahead» —
прогноз баланса, решает человек), Fleur («Учет Доходы и Расходы», 323 — трекер, есть в Г13).

**Одноконтурные калькуляторы долга на Mac (десктопные сборки, 2021–2026):** Debt Descent (5 оценок;
«runs both standard methods at once: Snowball… Avalanche»), **DebtLens** ($2.99; «View Snowball and
Avalanche side by side, with a recommendation based on your saved accounts» — сам выбирает метод:
одноконтурный советник), Triage: Debt Payoff & Budget («Compare avalanche versus snowball… never miss
a 0% promo expiration»), The Silo («Payoff plans: avalanche or snowball, with an extra-per-month lever»),
PayoffRoute («See the next payment and this month's route first»), Debt-Free: Payoff Planner, Guaca,
Nexpen, PennyFi ($4.99), Debtinator ($19.99, 2017: «we're trying to show you how to pay it off your
way»), Pay It Down ($14.99, 2021), SAFE Budgeting, BillRunway, FLO, Finance Register ($29.99), Cash Flow
Tool. Все — выбор метода человеком, кроме DebtLens (рекомендует метод).

**Пограничные «несколько контуров рядом» (описание прочитано целиком):**
- **Thrive: Budget & Money Manager** (1 оценка, 08.2026): «Zero-based budgeting… Emergency fund tracking
  with a target and a fund-the-gap plan. • Debt payoff with a clear, dated burndown. • Giving goals» —
  три контура, но в конвертном бюджете, распределяет человек. Планировщик.
- **MoneyWell** (moneywell.app): «helps you direct your extra money to debt reduction and savings so you
  end up with a nice cash buffer for emergencies», «telling you how much you need to save in each bucket
  category to meet your goals» — **ближе всех на Mac по словам**: цель — те же три направления, но
  механика — конверты с суммой «сколько надо в конверт до цели», без выбора между долгом и резервом.
  Планировщик (спорно — «telling you how much» уже рекомендация суммы, но по цели, заданной человеком).
- **4Ducks** (3 оценки): «a single monthly figure — what's safe to spend, and what you can set aside»,
  «pay down debt and watch a real debt-free date arrive» — «сколько можно отложить», без распределения.
- **Rizq Studio** (1 оценка): «RISK SCORE… based on four key factors: savings rate, debt burden,
  emergency fund coverage, and income stability. Actionable recommendations help you improve», симулятор
  «Pay Off vs. Invest» — индекс + рекомендации (как «Финздоровье» Т-Банка), расчёта распределения нет.
- **Cash Flow Tool**: «Savings Builder… a percentage of your income, a percentage of your monthly surplus,
  or a fixed amount» + «Debt Payoff Planner… Avalanche… Snowball» — правила задаёт человек.
- **Robobudget** (atoms.co.za): «plan income, living expenses, debt repayments and savings in one clear
  monthly view… See your projected surplus or shortfall», «does not provide financial advice».
Российский сегмент Mac: Alzex Finance, «Карманы: Семейный бюджет», SayMoney, «Мои деньги Pro», Fleur,
MyFinance Pro (кредитный калькулятор: «аннуитет, дифференцированные платежи…»), «Платежи по процентам»
— **все трекеры или кредитные калькуляторы; советника на Mac в русской выдаче нет.**

**Итог Г14.2:** Homebrew 144 кандидата → 14 PFM → **0 советников**. Mac App Store 616 финансовых →
130 поштучно + топ-60 → **1 одноконтурный советник по долгам (DebtLens), 0 трёхконтурных**. Ближайшее
по замыслу — MoneyWell и Thrive (три направления есть, но распределяет человек в конвертах).
Пересечения с Г13: Copilot, MoneyCoach, MoneyWiz, Fleur, Money Manager (Realbyte) — большинство
Mac-сборок это те же iOS-продукты; новых советников десктоп не добавил.

## Г14.4 — Windows и Linux: winget, Chocolatey, Flathub, Snap, Википедия

- **Flathub.** Категории API — строчные freedesktop: `audiovideo, development, education, healthfitness,
  game, graphics, network, office, science, system, utility` (`/api/v2/collection/category` → HTTP 200).
  Причина прежнего 422 — имени `Finance` в перечне нет вовсе, подкатегория `office/subcategories/Finance`
  → 404. Рабочий путь: `category/office` (248 приложений) + `POST /api/v2/search` («finance», «budget»,
  «money», «accounting»). **52 уникальных финансово-похожих, описание каждого прочитано.** PFM (по
  установкам за месяц): HomeBank 2 428 («Personal accounting for everyone»), Actual Budget 2 243, MMEX
  1 567, KMyMoney 1 240 («double-entry bookkeeping»), Portfolio Performance 1 130, Denaro 910 («Manage
  your personal finances»), Skrooge 391, Eqonomize! 317, Maxint 282 (инвестиции, робо-эдвайзер),
  Cosmic money 277, AloxBook 228, Fingrom 176, Grisbi 171, Fava 145, Buckets 142, Sugar Labs «Finance»
  121 («Learn financial planning basics» — обучалка). Остальное — криптоузлы, калькуляторы, счета-фактуры,
  заметки. **Советников: 0.**
- **Chocolatey** (`/api/v2/Search()` по budget/finance/money/debt, HTTP 200). **18 уникальных пакетов,
  PFM среди них 8:** KMyMoney (36 567 скачиваний), Portfolio Performance (30 568), HomeBank (18 654),
  bunqDesktop, moneyGuru (3 840, «double-entry»), Moneydance (3 505), hledger, Money Manager EX, Grisbi.
  По `debt` — 0 пакетов (527 байт пустой выдачи). **Советников: 0.**
- **winget.** Прямого поиска по `microsoft/winget-pkgs` без токена нет (GitHub code search требует
  авторизации); взят зеркальный индекс `api.winget.run/v2/packages?query=` (HTTP 200) — **112 пакетов,
  поиск нечёткий** (MongoDB, Garmin и т.п. — шум). PFM: MyMoney.Net (Lovett Software, .NET), KMyMoney,
  HomeBank. 🔴 Оговорка: winget.run — сторонний и, возможно, неполный индекс; отрицательный результат
  по нему слабее, чем по Homebrew.
- **Snap Store** (`api.snapcraft.io/v2/snaps/find`, заголовок `Snap-Device-Series: 16`, HTTP 200):
  **164 уникальных, прочитаны все названия и описания**; по `category=finance` — отдельно. PFM: KMyMoney,
  MMEX, GnuCash (2 сборки), Monento («track expenses and incomes»), SimpleBudget (конверты), Finanças
  (2026), SayMoney, pesapanga (Кения), Eqonomize, 1st Money, catetin.ai (AI-трекер чеков),
  vsingh-actual (Actual). Пограничные: **«Robot Financial Advisor»** — по описанию это разбор XBRL-отчётов
  компаний с SEC EDGAR, **не личные финансы** (ложноположительное по названию); **Redee Clear** «Credit
  Card payoff scheduler» (2023) — калькулятор по картам; DailyBu («what amount of money can be spent in
  day / week» — дневной лимит, как «Тяжеловато»); Retirement Scenarios (пенсионный Монте-Карло).
  **Советников по бюджету: 0.**
- **Википедия «List of personal finance software»** (API `action=parse`, 11 486 символов вики-текста):
  два раздела — открытые (GnuCash, HomeBank, KMyMoney, Ledger…) и проприетарные (Banktivity, Mint.com,
  Moneydance, Moneyspire, MoneyWiz, Personal Capital, Quicken, YNAB). **Список короткий и устаревший**
  (Mint закрыт в 2024, Personal Capital переименован в Empower) — российских программ («Домашняя
  бухгалтерия», «Дребеденьги») в нём нет. Новых кандидатов не дал.

**Итог Г14.4:** Windows/Linux-реестры — это кладбище и заповедник **учётных программ с двойной записью**
(GnuCash, KMyMoney, HomeBank, MMEX, Skrooge, Grisbi, moneyGuru). Ни одного советника; единственный
растущий новый продукт в них — Actual Budget (конверты).

## Г14.6 — в стадии разработки: Y Combinator, Product Hunt

### Y Combinator (открытое зеркало каталога `yc-oss.github.io/api`)
`industries/fintech.json` (HTTP 200, 1,1 МБ) + `tags/fintech.json` (1,2 МБ) → **896 уникальных
fintech-компаний YC**; `tags/personal-finance.json` → 404 (такого тега в зеркале нет). Фильтр по
one-liner + long_description (personal finance/budget/debt/payoff/financial advisor/savings/consumer) →
**186 совпадений, прочитаны поштучно** (`/private/tmp/g14/yc/hits.txt`). Основная масса — займы, BNPL,
необанки развивающихся рынков, коллекторы, трейдинг. Относящиеся к нашему жанру (long_description прочитан):

| Компания | Батч, статус | Что делает (дословно) | Класс |
|---|---|---|---|
| **Gauss** (gauss.money, 16 чел.) | W22, Active | «AI credit agent that automatically lowers the cost of consumers' debt… executes refinances or restructurings… automatically pay off any expensive balance on connected cards from an instantly originated line of credit» | исполнитель по долгам + кредитор (как Bright Money: монетизация займом) |
| **Maxi** (usemaxi.app, 2 чел.) | W23, Active | «iMessage-based, AI-native agent for your personal finances… proactively texts you to help cancel subscriptions, identify split expenses… keeps you in line with your budgets» | трекер-агент |
| **Autonomous** (becomeautonomous.com, 8 чел.) | F25, Active | «superintelligent financial advisor at 0% advisory fees» — счета 401k/IRA/брокерские, налоговый лосс-харвестинг | советник по инвестициям для состоятельных |
| Astor | S25, Active | «AI investment advisor for retail investors» | инвестиции |
| Envelope | S23, Active | «budgeting app with built-in checking and debit cards… organize real money into digital envelopes» | планировщик + банк |
| Finku (Индонезия, 20 чел.) | W22, Active | «recommends ways for user to achieve their goals faster… helped 1 million Indonesian» | трекер + рекомендации |
| **Mine** (usemine.com, 18 чел.) | S21, **Inactive** | «credit-builder… budgeting… MoneyGPT, the money assistant» | умер |
| **Path** (path.me) | S19, **Inactive** | «a money manager who… makes sure you don't f**k up your financial future in your 20's — all for $20/mo» | советник-подписка, умер |
| **Ready For Zero** | S10, **Inactive** | «online financial tools for managing debt automatically… paid down over $250 million… acquired by Avant» | планировщик долгов → продан кредитору |
| Truebill | W16, Acquired | → Rocket Money (Г11) | трекер |
| Honeydue | S17, Acquired | бюджет для пар | трекер |
| FutureAdvisor | S10, Acquired (BlackRock) | робо-эдвайзер | инвестиции |
| Tranqui Finanzas | S19, Active | «debt collection company» (Латам) | коллектор, не советник |
| Palus Finance | W26, Active | «Your startup's financial advisor» | B2B |

🔴 **Наблюдение:** в YC-портфеле 2022–2026 **нет ни одной компании «советник по распределению
бюджета для частного лица»**. Все живые проекты в долговой теме монетизируются через **кредит**
(Gauss — выдаёт линию, Ready For Zero продан Avant), а советники-подписки (Path $20/мес, Mine) —
Inactive. Это та же картина, что в Г13 (Bright Money ушёл в займы, Clerkie умер).

### Product Hunt (канал частично)
- **SuperMoney** (supermoney.com, веб) — PH 03.03.2026, **179 голосов, #5 дня**, «Your money stress,
  solved by AI»; PH-описание: «money-saving actions, helps optimize debt, identifies better options».
  Сайт: «Spending analysis, debt strategy, savings advice. Just ask.», «Better rates find you»,
  «Trusted by 2 million members since 2013». 🔴 **SuperMoney — старый маркетплейс финансовых продуктов
  (сравнение займов/карт)**; AI-советник надстроен над лидогенерацией. Класс: советник-чат при
  маркетплейсе (как Сбер/Финуслуги в Г11) — механика разбиения денег не раскрыта.
- **Embr** (iOS, 2025) — «Plan your path to debt freedom», 102 голоса; сравнение минимальных и
  дополнительных платежей, визуализация. Одноконтурный калькулятор.
- **DebtMeltPro** — в дневном лидерборде PH 06.04.2026 («compare debt payoff strategies»), страница
  не открывалась; **PayOffPlan** (launches.uicomet.com) — «free debt payoff planner that compares
  snowball vs avalanche». Одноконтурные калькуляторы.
- 🔴 **Сплошного обхода PH не было:** GraphQL API Product Hunt требует токен разработчика, категория
  не листается без авторизации. Взяты только 2 поисковых запроса + 2 страницы. Отрицательный вывод по
  PH слабый.

**Итог Г14.6:** новое в разработке 2025–2026 — это (а) LLM-советники (Ray, SuperMoney, Maxi, класс
агент-скиллов из Г14.1) и (б) россыпь одноконтурных debt-калькуляторов (Embr, DebtMeltPro, PayOffPlan,
DebtLens, Debt Descent). Трёхконтурного расчётного советника в стадии запуска не найдено.

## Г14.3 — веб-сервисы и SaaS-каталоги

**Каталоги.** 🔴 **G2 и Capterra закрыты для всех каналов:** `curl` с браузерным UA → HTTP 403
(`capterra.com/budgeting-software/` 5 677 байт заглушки, `/personal-finance-software/` 403,
`g2.com/categories/personal-finance` 403); `WebFetch` → 404/403; `r.jina.ai` → HTTP 200 и **0 байт**
на четырёх страницах подряд (Capterra ×2, G2, GetApp) — прокси в этот час отдавал пустоту на любые
адреса (exit 56 на первой серии). Exa в этой сессии как инструмент недоступен. **Не добыто.**
Добыто:
- **AlternativeTo, «You Need A Budget alternatives»** (`WebFetch`, HTTP 200) — 12 позиций: Sure,
  Actual Budget, MoneyManager Ex (95 лайков), HomeBank (144), Dime, Paisa, Recurring Expense Tracker,
  Waterfly III, Flow, Fungible («Terminal-based personal finance manager with automatic Plaid sync»),
  Firefly III, KMyMoney. **Все — трекеры/конверты открытого кода**, пересекаются с Г14.1/Г14.4.
- **SaaSHub, «best personal finance software»** — 12 позиций: YNAB, Mint (закрыт), «Monarch»
  (каталог перепутал с WordPress-плагином), HomeBank, Rocket Money, GnuCash, Splitwise, Money Manager
  Ex, Quicken, Actual Budget, Plaid (B2B), PocketGuard. Итог WebFetch-разбора дословно: «None of the
  listed products explicitly claim to recommend splitting money between debt payoff, emergency
  savings, and goals.»

**Веб-сервисы, не разобранные в Г11/Г13** (главные страницы, `WebFetch`, 12.09.2026):

| Сервис | Цитата | Класс |
|---|---|---|
| **PocketSmith** (pocketsmith.com, веб + приложения) | «Know where your money is going»; «Cash flow forecasts (up to 60 years into the future)» | трекер + долгий прогноз; распределения нет; цены на странице нет |
| **Quicken Simplifi** (веб + iOS/Android) | «starts with your monthly income, subtracts your bills & subscriptions, and generates a personalized Spending Plan»; поддерживает «zero-based budgeting, envelope budgeting, 50-30-20»; «Include your savings goals in your plan» | планировщик: остаток считает, **куда направить — решает пользователь**; метода погашения нет; $3.99/мес при годовой оплате (обычно $6.99) |
| **Tiller** (tiller.com) | «Your Financial Life in a Spreadsheet, Automatically Updated Each Day»; «Foundation Template for budgets, expenses, debt, and net worth tracking» | фид в таблицу; советов нет; шаблоны сообщества (в т.ч. debt snowball) — на главной не упомянуты, не проверено |
| **Lunch Money** (lunchmoney.app) | `WebFetch` → 403; `curl` → 200 и 0 байт | **не добыто** |
| **Empower** (ex Personal Capital) | `WebFetch` → 404 по `/personal-investors/tools`; `curl` → 301 и 0 байт | **не добыто**; по Г11/общеизвестному — бесплатный дашборд как воронка в управление капиталом за % от активов |
| Monarch, Copilot, Origin, YNAB Web, Rocket Money | — | разобраны в Г11, не переразбирались |
| Moneydance, GnuCash, Banktivity, Buckets | — | десктоп, см. Г14.2/Г14.4 |

**Итог Г14.3:** в веб-SaaS западного рынка картина та же, что в Г11: планировщики (Simplifi,
YNAB, Monarch), трекеры с прогнозом (PocketSmith, Tiller) и один «советник по замыслу» на LLM
(Origin; к нему в открытом коде добавился Ray, в маркетплейсах — SuperMoney). **Сервиса, который
расчётом делит остаток между досрочным погашением, резервом и целями, в каталогах нет**; оба
каталога, где он мог бы найтись под «Budgeting Software» (G2, Capterra), закрыты для всех каналов.

## Г14.7 — академические и некоммерческие прототипы

**Академия (OpenAlex API, 3 запроса, 75 первых выдач прочитаны по заголовкам).** Выдача почти
целиком — макроэкономика и финансы домохозяйств как наука; **работающих систем поддержки решений
для частного лица с публичным прототипом не найдено.** Два релевантных текста (аннотации сняты):
- **de Zarzà, de Curtò, Roig, Calafate (2023)**, «Optimized Financial Planning: Integrating Individual
  and Cooperative Budgeting Models with LLM Recommendations», *AI* (MDPI) 5(1), doi 10.3390/ai5010006,
  Goethe-Universität Frankfurt, 45 цитирований. Дословно: «an optimization framework for individual
  budget allocation, aiming to maximize savings by efficiently distributing monthly income among
  various expense categories», расширение на домохозяйство; «the LLM provides initial feasible
  solutions to our optimization problems». 🔴 **Ближайшая к нам по постановке научная работа в этой
  теме: оптимизация распределения дохода + LLM.** Отличие: целевая функция — максимум сбережений
  по категориям расходов; **долгов со ставками, резерва как отдельного контура и инвариантов нет**;
  продукта нет — статья с численным экспериментом. В репозитории ранее **не упоминалась** (grep по
  `docs/research/raw` на Zarz — пусто).
- **Vaduka и др. (KIIT University, 2024)**, «Optimizing Personal Finance Management through AI-Driven
  Decision Support Systems», TENSYMP 2024, doi 10.1109/tensymp61132.2024.10752249, 13 цитирований —
  обзорно-позиционная статья («AI-driven systems offer a promising solution…»), прототипа нет.
- Прочие академические источники по рекомендательным системам и DSS в финансах (Felfernig & Burke,
  Fano & Kurth, MCDA, GBI) разобраны в темах 13–17 (`constraint_based_utility_recsys_2026-09-09.md`,
  `mcda_saw_alternatives_2026-09-09.md`, `recsys_finance_domain_specifics_2026-09-09.md`) — не
  дублировались.

**Некоммерческие и государственные.** CFPB (США) — просветительские материалы («Your Money, Your
Goals», «Creating a savings first aid kit», отчёт «Emergency Savings and Financial Security», 2022),
**интерактивного инструмента, который считает «долг или резерв», у CFPB нет**; советы в выдаче —
последовательность «starter cushion first, aggressive debt payoff second, full emergency fund third»
(Alliant Credit Union, Discover — эмитенты, не НКО). Россия: поиск по fincult.info (ЦБ) калькулятора
«погасить досрочно или копить подушку» — **не найдено**; в выдаче только кредитные калькуляторы
досрочного погашения (Финуслуги, «Спроси.Дом.РФ», КонсультантПлюс, calcus.ru) — однокритериальные
(экономия процентов), без резерва и целей. Sugar Labs «Finance» (Flathub) — обучалка «Learn financial
planning basics» для детей.

**Итог Г14.7:** в науке ближайшая постановка — de Zarzà et al. (2023), но без долгового контура;
у регуляторов и НКО — тексты и однокритериальные калькуляторы. Прототипа, решающего нашу задачу,
нет. Отрицательный вывод средней силы: OpenAlex-поиск был по трём формулировкам, не систематический обзор.

## Г14.5 — реестр отечественного ПО (reestr.digital.gov.ru)

**Канал.** На странице реестра (`curl -sk --http1.1` + браузерный UA, HTTP 200, 1 090 069 байт) найдена
ссылка **`/reestr/?export=registry` — полная выгрузка реестра**: HTTP 200, **161 381 070 байт XML**
(`application/octet-stream; charset=Windows-1251`, кириллица — числовыми сущностями), `genDate=
"2026.09.12 01:37"`. Разобрана потоково (`xml.etree.iterparse`, `/private/tmp/g14/ru/parse.py`):
**32 523 записи**. Поля записи: `registrationNumber`, `name`, `previousAlternativeName`, `owner`
(название, ИНН, ОГРН), `softwareClass code=` (классификатор приказа № 486), `descriptionLink`,
`inclusionDate`, `excluded`. 🔴 Это новый приём канала: ранее (`tails_cbr_mr_software_registry_2026-09-10.md`)
реестр отдавал таймаут через зарубежный VPN, сейчас отдаётся целиком одной выгрузкой.

**Два прохода.** (1) Названия и прежние названия по словам «бюджет / личн* финанс / домашн* / семейн*
бюджет / учёт расходов / финансов* помощник|советник|планир|здоров / копилк / сбережен / долг / погашен /
PFM / money / Дзен / CoinKeeper / Дребеденьги / FINPILOT» → **230 совпадений**; отсев государственного
и корпоративного бюджетирования, банков, энергетики, медицины, «Домашний Инженер 3D» и т.п. → **144**,
прочитаны поштучно. (2) Обратная проверка по известным российским PFM и их правообладателям (Дзен-мани,
ZenMoney, CoinKeeper, Дребеденьги, «Тяжеловато», «Без долгов», «Домашняя бухгалтерия», «личный/семейный
бюджет», «кошелёк», «копилка») → **13 совпадений**, все прочитаны.

**Результат.** Из 144 почти все — **бюджеты государства и организаций** («КС Бюджет», «БАРС.Бюджет»,
«Парус-Бюджет», «Бюджет-СМАРТ», «ИТС: Система Бюджет», «VK Budgeting» — FinOps облака, «Синтегро Смарт
Бюджет», «Система финансового планирования» Ростелекома). Относящиеся к частному лицу:

| Рег. № | ПО | Правообладатель | Класс | Что это на деле | Класс по нашей шкале |
|---|---|---|---|---|---|
| 15623 | **«Домашняя бухгалтерия»** | Козловский П. В. (Keepsoft) | 05.05 | «Приложение для учета расходов и доходов семейного бюджета, долгов и контроля домашних финансов»; Windows/iOS/Android; «более 4 000 000 раз» скачано | трекер |
| 34016 | **«Финансовый помощник»** | ООО «ТЕХНОКАП» (Иннополис, ИНН 1683024849), включено 18.06.2026 | 12.11 | по функциональному описанию (PDF 1,2 МБ, `pdftotext`): «Информационная система экспертной помощи по кредитной истории… предоставлением клиентам результатов консультации по расшифровке кредитного отчета, полученного от Квалифицированных Бюро кредитных Историй»; роли клиент/эксперт/администратор, платная услуга | **сервис разбора кредитной истории человеком-экспертом, не советник по бюджету** (ложноположительное по названию) |
| 27222 | «Инвесткопилка» | АО «ТБанк» | 12.11 | модуль банка (накопления/инвестиции) | банковский продукт |
| 18507 | «Обогащение PFM» | ООО «Эвотор ОФД» | 02.06 | обогащение данных чеков для PFM банков (`platformaofd.ru/bigdataproducts-pfm`) | B2B-данные, сосед по PFM-движку |
| 13534 | «Кредитный калькулятор с досрочным погашением для Android» | Тачков Д. Е. (ИП/физлицо) | 12.20 | кредитный калькулятор | калькулятор |
| 10867 / 10294 | «Погашение кредитов» (Android / iOS) | ЗАО «ЦФТ» | 12.20 | **исключены из реестра**; домен `cft.group` не резолвится (ENOTFOUND), в Wayback страница не архивирована | не определено (по названию — сервис платежей по кредитам) |
| 28822 / 34372 / 6674 | «Кошелёк.ру», «Кошелёк» (Бесконтакт) | — | 12.11 / 12.20 | кошельки/платёжные, карты лояльности | не PFM |
| 34224 | Bonus Money | ООО «Мобильные информационные технологии» | 09.09 | по классу — CRM/лояльность; страница не открывалась | не PFM (по классу) |
| 28002 | «Финансовая грамотность» | ООО «Стендап Инновации» (playstand.ru) | 05.01 | обучающий контент; не открывалось | обучалка |
| 8519 | «Бюджет+» | Мажирин А. В. | 12.20 | по описанию (`xn--90agdd0axpf8hg.xn--p1ai`, HTTP 200): «Учет и анализ объектов недвижимости в организации: Заказ данных в Росреестре…» | **не про бюджет вовсе** |
| 7065 | «БФТ. Бюджет для граждан» | ООО «БФТ» | 12.16 | портал открытого бюджета региона | госинформирование |

🔴 **Прямой ответ по реестру:** **ни одного советника по личным финансам в реестре нет.** Из массовых
российских PFM в реестре есть **только «Домашняя бухгалтерия» (Keepsoft)**; **Дзен-мани, CoinKeeper,
Дребеденьги, «Тяжеловато», «Без долгов» в реестре отсутствуют** (обратная проверка по названию и
правообладателю — ноль). То есть потребительский PFM-сегмент РФ в реестр практически не ходит — для
FINPILOT место в реестре (связка с Г9) будет почти пустым соседством в классе 12.11; ближайшие соседи
по классу — банковские модули («Инвесткопилка») и сервис разбора кредитной истории («Финансовый
помощник» ТЕХНОКАП). Оговорка: поиск по названиям; продукт, названный абстрактно (например «Платформа X»),
мог не попасть — сплошное чтение 32 523 названий не делалось.

## ИТОГ Г14

### Сколько просмотрено и классифицировано

| Канал | Видно в выдаче (уникальных) | Прочитано поштучно (описание/README) | PFM-продуктов | Советников |
|---|---|---|---|---|
| GitHub (21 запрос по темам и словам) | 1 489 | 134 (≥100★) + ≈230 (плановые слова, ≥3★) + 41 README | ≈110 | 2 LLM-продукта (Ray, Fiduciary) + 6 агент-скиллов + 2 по долгу (better-debt, FreeD) + 1 с константными долями (bucketwise) |
| Homebrew Cask (из 7 712) | 144 кандидата | 144 | 14 | 0 |
| Mac App Store (28 запросов US/RU) | 735 (616 «Финансы») | 130 полных совпадений + топ-60 + 8 описаний целиком | ≈400 | 1 по долгу (DebtLens) |
| Flathub | 52 | 52 | 17 | 0 |
| Chocolatey | 18 | 18 | 9 | 0 |
| winget (зеркало winget.run) | 112 | 112 названий | 3 | 0 |
| Snap Store | 164 | 164 | 13 | 0 |
| Википедия «List of personal finance software» | 14 | 14 | 14 | 0 |
| AlternativeTo + SaaSHub | 24 | 24 | 20 | 0 |
| Веб-сервисы (главные страницы) | 5 | 3 добыто | 3 | 0 |
| Y Combinator (fintech, 896) | 186 совпадений | 186 | ≈12 в жанре | 1 исполнитель по долгу с кредитом (Gauss) |
| Product Hunt | 4 | 4 | 4 | 1 LLM при маркетплейсе (SuperMoney) |
| Реестр ПО РФ (из 32 523) | 243 | 144 + 13 | 1 («Домашняя бухгалтерия») | 0 |
| Академия (OpenAlex) | 75 | 75 заголовков, 2 аннотации | — | 0 прототипов (1 близкая постановка) |
| **ИТОГО** | **≈ 3 270 уникальных** (без 7 712 casks и 32 523 записей реестра, прошедших машинный фильтр) | **≈ 1 400 поштучно** | — | **14** (см. таблицу) |

**Советников, покрывающих все три контура (долг + резерв + цели) расчётом: 0.**

### 🔴 Таблица советников

| Название | Платформа | Что считает | Долги / резерв / цели | Объяснение | Цена | Жив ли |
|---|---|---|---|---|---|---|
| **Ray Finance** (rayfinance.app, `cdinnison/ray-finance`, 303★) | CLI (npm), macOS/Linux, открытый код MIT | LLM по данным Plaid/Bridge + профилю → «what it would do and why» | долг — да (пример с картой 24,9 %), цели — да («pause the Japan fund»), резерв — в тексте; **без детерминированного расчёта** | текст LLM | self-host $0 (+$1–3 LLM), Pro **$10/мес** | жив (push 01.08.2026), npm 54/мес — затухает |
| **Fiduciary** (`weklund/fiduciary`, 10★) | Claude Code skills + Plaid CLI, локально | «walks your actual balances and rates through a priority framework… specific recommendation with the math» | долг vs резерв — да; цели — нет данных | текст агента | $0 (свой LLM) | создан 07.2026, push 05.07 |
| Агент-скиллы по личным финансам (ai-finance-claude 61★, finance-assistant 42★, openaccountant/skills 68★, canadian-finance-planner 54★, thai-personal-finance-planner 19★, comprehensive-finance-consultant 6★) | Claude Code / агенты | avalanche vs snowball, emergency fund, «Phased action plan — Stabilize (emergency fund + high-rate debt) → Build → Accelerate» | все три — **фиксированной лестницей**, не оптимизацией | текст LLM + детерминированные калькуляторы у части | $0 | 2026, живы |
| **SuperMoney** (supermoney.com, PH 03.03.2026) | веб | «Spending analysis, debt strategy, savings advice. Just ask.» | заявлено долг + сбережения; механика не раскрыта | чат | бесплатно; монетизация — маркетплейс продуктов («Better rates find you») | жив, «2 million members since 2013» (маркетплейс) |
| **DebtLens** | Mac/iOS | «Snowball and Avalanche side by side, with a recommendation based on your saved accounts» | только долг | сравнение сроков и процентов | $2.99 | 08.2026, 0 оценок |
| **better-debt** (`Aparajith24`, 12★) | веб (Next.js), открытый код | avalanche / snowball / «optimal, prepayment-cap-aware»; true APR; вердикт оферты «GOOD_TIME / TIGHT / NOT_RECOMMENDED» | только долг | таблицы + красные флаги | $0 | 08.2026 |
| **FreeD** (`Luigi-PastorePica`, 4★) | открытый код | «recommend which [debt]… where to allocate money above the minimum payments» | только долг | — | $0 | ранняя стадия |
| **Gauss** (YC W22, 16 чел.) | мобильное/веб | «automatically lowers the cost of consumers' debt… pay off any expensive balance… from an instantly originated line of credit» | только долг; **исполняет сам через свой кредит** | — | монетизация кредитом | Active |
| **Bucketwise Planner** (16★) | веб, Docker | Barefoot Investor: «60% Daily Expenses, 10% Splurge, 10% Smile, 20% Fire Extinguisher» + snowball + опц. AI | все три — **константные доли** | методика книги | $0 | push 06.2026 |

Пограничные (**не** советники, распределяет человек): MoneyWell («direct your extra money to debt
reduction and savings… nice cash buffer for emergencies»), Thrive (конверты + «fund-the-gap plan» для
резерва + дата погашения), GnuCash Financial Radar (три отчёта рядом), Quicken Simplifi (Spending Plan
считает остаток), Rizq Studio (индекс + «Actionable recommendations»), Cash Flow Tool (правило
«% of monthly surplus» задаёт человек).

### 🔴 Прямой ответ: есть ли в вебе, на десктопе или в открытом коде продукт, решающий задачу FINPILOT целиком

**Нет.** Ни в одном из 14 каналов не найден продукт, который по введённым доходам, расходам, долгам со
ставками и целям **вычисляет**, сколько в этом месяце направить на досрочное погашение (по ставке), сколько
в резерв и сколько в цели, и объясняет почему. Найдено три класса-заменителя: (1) **LLM-советники общего
вида** — дают совет на все три направления, но без детерминированного расчёта, воспроизводимости и
инвариантов (Ray, SuperMoney, Fiduciary, агент-скиллы; в Г11 — Origin); (2) **одноконтурные советники по
долгу** (DebtLens, better-debt, FreeD, Gauss; в Г13 — Toya, Spendify, Bright Money); (3) **правила-лестницы
и константные доли** (Barefoot 60/10/10/20, «Stabilize → Build → Accelerate»). Вывод совпадает с Г11 и Г13,
получен третьим независимым набором каналов — это усиливает его. Пласт, в котором такой продукт логичнее
всего было бы ждать (открытый код, 1 489 репозиториев по теме), дал только LLM-обёртки и калькуляторы.

### 🔴 Что ближе всего к FINPILOT и чем мы отличаемся

- **Ray Finance** — ближе всех по **позиционированию**: «Other finance apps show you what you spent. Ray
  tells you what to do.» — почти наша формулировка ценности, и пример ответа Ray — ровно наш тип решения
  («пауза цели, $440/мес на карту под 24,9 %»). **Отличия:** (а) решение выдаёт LLM, а не объявленная
  модель — нет воспроизводимости, нельзя проверить инварианты (Rt ≥ 0, ПДН ≤ 0,40), нет 66 альтернатив и
  прогноза с интервалом; (б) рынок США/Канады/ЕС через Plaid/Bridge — к РФ неприменим; (в) CLI для
  технарей, а не веб; (г) спрос низкий: ~4 тыс. установок npm за 8 месяцев, 54 за последний месяц.
- **de Zarzà et al. (2023)** — ближе всех по **постановке** (оптимизация распределения месячного дохода
  + LLM как источник начального решения). Отличие: максимизируются сбережения по категориям расходов,
  долгов со ставками и резерва как отдельного контура нет, продукта нет.
- **MoneyWell / Thrive** — ближе всех по **набору направлений** на десктопе (долг, подушка, цели в одном
  окне). Отличие: конверты, решение за человеком; FINPILOT делает выбор между направлениями сам.
- **better-debt** — ближе всех по **качеству долгового расчёта** (true APR, ограничения на досрочку,
  проверка оферты). Отличие: только долг. 🔴 Идея проверки оферты «перед подписанием» и учёта лимитов
  досрочного погашения по договору — у нас в модели не видна; стоит сверить (не правка канона, а вопрос).

**Формулировка отличия, пригодная без правки канона:** на всём срезе совет «куда направить деньги» даётся
либо **текстом языковой модели**, либо **калькулятором одного направления**, либо **фиксированной
лестницей**; воспроизводимого расчёта, который выбирает между досрочкой, резервом и целями одной свёрткой
с объявленными ограничениями, не найдено ни у кого — ни в вебе, ни на десктопе, ни в открытом коде.

### 🔴 Что говорит история Maybe Finance про жизнеспособность B2C в нашем жанре

1. **Maybe был не в нашем жанре** — трекер с банковской синхронизацией и AI-чатом, без расчёта
   распределения. Его смерть — прямое свидетельство против **трекера на Plaid с венчурными деньгами**,
   косвенное — против B2C-PFM вообще.
2. **Числа, которые можно брать в юнит-экономику:** ~200 платящих после 4 лет при 54 285★ на GitHub
   (**звёзды ≠ платящие, конверсия ≈ 0,4 %**); точка безубыточности названа основателем как ~6 200
   платящих при $15/мес для команды из нескольких человек; первая жизнь — 10 000+ в листе ожидания →
   50 платящих на запуске.
3. **Главная статья затрат — банковские данные** («The single biggest challenge… is bank providers… most
   users churn if even one of their banks is unsupported»). FINPILOT на ручном вводе этот риск не несёт,
   но платит трением ввода — обратная сторона того же выбора.
4. **Мнение основателя о B2C, дословно:** «either has to be completely bootstrapped for years or have
   $10's of millions in funding»; «The market's needs are too fragmented». Лучшим ходом для нового B2C он
   назвал «AI + mobile first».
5. 🔴 **Для нашего тезиса «масштаб в B2B» Maybe — свидетельство против, а не за:** B2B-пивот (прогнозы
   для бизнеса, июль 2025) не нашёл «traction or economics» и к началу 2026 закончился роспуском компании
   и распродажей активов (домены, 40+ репозиториев, Figma), 31.03.2026. Оговорка: они ушли в **другой**
   продукт для другого покупателя, а не в B2B2C-продажу того же PFM банкам — прямой проверкой нашего
   варианта это не является.
6. **Пользователи не пропали, а ушли в форк:** `we-promise/sure` — 9 866★, живой (push 12.09.2026). Спрос
   на бесплатный self-hosted трекер есть; спроса платить за него — нет.
7. Параллельная картина из YC (Г14.6) и Г13: живые продукты в долговой теме монетизируются **кредитом**
   (Gauss, Bright Money, Ready For Zero → Avant), советники-подписки (Path $20/мес, Mine, Clerkie, Savvy)
   — мертвы. Единственный живой платный LLM-советник в открытом коде (Ray, $10/мес) — с затухающими
   установками.

### Что осталось неизвестным / НЕ ДОБЫТО

1. **G2, Capterra, GetApp** — 403 на `curl` с браузерным UA и на `WebFetch`, `r.jina.ai` отдал HTTP 200
   и 0 байт на все четыре страницы; Exa в этой сессии как инструмент недоступен. Категории «Personal
   Finance / Budgeting Software» не просмотрены.
2. **Lunch Money** (`WebFetch` 403, `curl` 200/0 байт) и **Empower** (404 / 301 без тела) — не добыты.
3. **Product Hunt** — сплошной обход невозможен без токена GraphQL API; взяты 2 поиска и 2 страницы.
   Страница DebtMeltPro не открывалась.
4. **winget** — официальный репозиторий `microsoft/winget-pkgs` без токена GitHub не ищется (code search
   требует авторизации); взято стороннее зеркало winget.run с нечётким поиском.
5. **Чарты Mac App Store по жанру** — классический RSS для `*macapps` с `genre=` отдаёт 0 позиций на всех
   жанрах 12001–12022; «популярное» по категории на Mac не снимается.
6. **«Погашение кредитов» (ЦФТ)** — исключено из реестра, домен `cft.group` не резолвится, Wayback не
   архивировал; **Bonus Money** и «Финансовая грамотность» (реестр) — классифицированы по классу ПО и
   названию, страницы не открывались.
7. **Механика Ray изнутри** — только README и сайт; есть ли под LLM какой-либо детерминированный слой
   приоритизации, не проверено (код не читался).
8. **Подробный разбор Пигфорда о закрытии Maybe** обещан («I'll write more about all of this in the
   future»), на 12.09.2026 не найден; отток ~200 платных подписчиков (куда ушли) не известен.
9. **Реестр ПО** — отбор по названиям; продукт с абстрактным названием мог не попасть (сплошное чтение
   32 523 названий не делалось).
10. Ни один продукт не устанавливался — всё по заявленным описаниям, README и сайтам.

### Служебное

- Субагентов: **0**. Все каналы — машинные API и прямое чтение лидером.
- `WebSearch`: **5 вызовов** (Maybe; PH AI advisor; PH debt payoff; CFPB; fincult). Бюджет поиска не исчерпан.
- `WebFetch`: ~25; `curl`: GitHub API ~25 запросов, iTunes Search 28, Homebrew 2, Flathub 7, Chocolatey 4,
  Snap 11, winget.run 3, yc-oss 3, OpenAlex 5, fxtwitter 2, HN Algolia 1, npm 2, реестр 2 (страница +
  выгрузка 161 МБ).
- 🔴 **Новые приёмы канала:** (1) **реестр ПО РФ отдаёт полную выгрузку** `reestr.digital.gov.ru/reestr/
  ?export=registry` (161 МБ XML, 32 523 записи) — `curl -sk --http1.1` + UA; (2) **x.com закрыт для jina**
  (AbuseAlleviationError), посты читаются через `api.fxtwitter.com/<user>/status/<id>` целиком, включая
  длинные; (3) **Flathub**: категории строчные freedesktop (`office`, не `Finance`), поиск —
  `POST /api/v2/search`; (4) **Snap Store**: `api.snapcraft.io/v2/snaps/find` с заголовком
  `Snap-Device-Series: 16`; (5) **YC**: открытое зеркало `yc-oss.github.io/api/industries/fintech.json`;
  (6) **npm downloads** (`api.npmjs.org/downloads/point/<период>/<пакет>`) — объективный счётчик
  аудитории для CLI-продуктов.
- Сырьё: `/private/tmp/g14/` — `gh_*.json`, `gh_big.tsv`, `gh_kw.tsv`, `readme/`, `cask.json`,
  `cask365.json`, `brew_cand*.tsv`, `mas/`, `linux/`, `win/`, `yc/`, `ru/` (выгрузка реестра, `hits.json`,
  `technocap.txt`), `acad/`, `maybe_final_release.md`.

---

## ДОБОР Г30.4 — Exa (16.09.2026)

**Состояние каналов на старте (коды ответов, замер 16.09.2026):** `mcp__exa__web_search_exa` — **работает** (смоук: запрос по Lunch Money, 3 результата); `mcp__exa__web_fetch_exa` — **работает частично по доменам**: `capterra.com/budgeting-software/` → **200, полный текст** (Exa пробила антибот, который в Г14.3 отдавал 403 на `curl`+UA, 403/404 на `WebFetch` и 200/0 байт на `r.jina.ai`); `g2.com/categories/personal-finance` → **CRAWL_UNKNOWN_ERROR**; `capterra.com/personal-finance-software/` → **CRAWL_UNKNOWN_ERROR**; `getapp.com/finance-accounting-software/personal-finance/` → **CRAWL_UNKNOWN_ERROR**; `empower.com/personal-investors/tools` → **CRAWL_NOT_FOUND**; `empower.com/personal-wealth/free-financial-tools` → **CRAWL_LIVECRAWL_TIMEOUT**. Подагентов: 0.

### Г30.4-К1 — Capterra «Budgeting Software»: 🟢 ДОБЫТО, но категория оказалась B2B

`https://www.capterra.com/budgeting-software/` через `mcp__exa__web_fetch_exa` — **HTTP 200**, выдано 6 000 симв. среза (страница целиком больше), заголовок дословно: «Best Budgeting Software 2026 | Capterra», «Last updated on April 15, 2026».

Дословный состав первых ~25 позиций категории: **NetSuite** («NetSuite Planning and Budgeting is used by companies worldwide to meet organization-wide business budgeting and planning needs»), **Power ON**, **Tradogram**, **Yooz**, **FinAlyzer**, **QuickBooks Online**, **Xero**, **Procore**, **Workday HCM**, **QuickBooks Online Advanced**, **TimeSolv Legal Billing**, **Sage Intacct**, **Sage Accounting**, **Deltek Vision**, **Quicken** («Rental property and personal finances management solution with tenant information tracking, income management, and expense tracking»), **Sage 50 Accounting**, **Sage 100**, **SAP S/4HANA Cloud**, **Zoho Sprints**, **Teampay**, **Precoro**, **Moss**, **Workday Adaptive Planning**, **LivePlan**, **Datarails**.

🔴 **Находка, меняющая трактовку Г14.3.** Вахта Г14.3 записала: «оба каталога, где он мог бы найтись под „Budgeting Software“ (G2, Capterra), закрыты для всех каналов» — то есть оставила открытой возможность, что искомый класс продуктов там есть. Категория открыта и оказалась **целиком корпоративной (ERP, FP&A, закупки, расчёт зарплаты)**. Единственный продукт с личными финансами в описании — **Quicken**, и тот позиционируется через управление арендной недвижимостью. **Продукта, распределяющего свободные деньги между досрочным погашением, резервом и целями, в категории нет.** Отрицательный результат теперь измерен, а не предположен.

### Г30.4-К2 — G2 «Personal Finance»: 🟡 ЧАСТИЧНО, прямая страница категории не берётся и Exa

Прямой фетч `g2.com/categories/personal-finance` → `CRAWL_UNKNOWN_ERROR` (Exa). Поиском через Exa снят смежный срез:
- **`https://ai.g2.com/marketplace/?tag=personal-finance`** («Best AI Tools for Personal Finance | G2»), дословный состав: **Fix My Life AI**; **Spendlog** — «Local-first expense tracking & invoicing in Claude Code—no cloud, no accounts»; **Expense Mcp**; **Kniru** — «AI-powered personal finance management and analysis—free forever»; **RAFA AI** — «AI-powered investment insights and portfolio management agents»; плюс «AI-powered expense and subscription tracker – no bank login needed».
- **`https://www.g2.com/best-software-companies/top-financial-services`** («Best Financial Services Software Products 2026»), дословно: «Out of 3,369 total products in this category, and 33 that were eligible for the 2026 Best Software Awards, here are the 25 best software products». Состав — B2B целиком (Agentforce Financial Services, The Mortgage Office, Morningstar Direct, Betterment Advisor Solutions, Koyfin, Asset-Map, LoanPro и т. п.).
- **`https://www.g2.com/best-software-companies/top-accounting-and-finance`**, дословно: «Out of 4,961 total products in this category, and 246 that were eligible for the 2026 Best Software Awards, here are the 50 best software products» — тоже целиком B2B (SAP Concur, BILL, Sage Intacct, Agicap, Expensify…).

**Вывод по К2:** G2 как каталог **B2B-ориентирован структурно**; «personal finance» у него живёт в отдельном AI-маркетплейсе, и там тоже ни одного советника по распределению — трекеры и инвестиционные ассистенты. Совпадает с итогом Г11/Г13/Г14. Страница `categories/personal-finance` дословно **не добыта**; каналы пройдены: `curl`+UA (403, Г14.3), `WebFetch` (403/404, Г14.3), `r.jina.ai` (200/0 байт, Г14.3), **Exa fetch (CRAWL_UNKNOWN_ERROR), Exa search (дала три смежные страницы вместо неё)**.

### Г30.4-К3 — Lunch Money: 🟢 ДОБЫТО (в Г14.3 было «не добыто»)

`https://lunchmoney.app/` через Exa — **HTTP 200**, полный текст главной. Дословно: «Delightfully simple personal finance & budgeting»; «Made for you, the modern-day spender»; «Trusted and loved across 30+ countries». Четыре заявленных блока функций дословно: «See the big picture» (Import directly from your banks · Upload transactions via CSVs · Automate imports with the developer API · Connect your crypto wallets and ledgers); «Surface spending habits» (Set monthly budgets per category · Split and group transactions · Track recurring expenses automatically · Search and filter transactions quickly); «Simplify your finances» (multicurrency · категории · теги · «Automate your workflow with the rules engine»); «Improve financial awareness» (детальная статистика · net worth month over month · query tool · спутник-приложение).

Цены — `https://lunchmoney.app/pricing` (Exa search, полный текст): «Monthly Subscription $10»; «Annual Subscription — Set your own price! $100»; «Start with a risk-free 30-day trial»; «Your price is locked in for life»; «Since launching in 2019, Lunch Money has become an internationally used app. With our users' support and our lean company structure, we were able to achieve profitability within the first few years of business»; «Now, we have decided to prioritize accessibility to our app and deprioritize maximizing profits».

**Классификация:** **трекер с многовалютностью и API**. Ни погашения долга, ни резерва, ни целей, ни распределения остатка — в заявленных функциях нет вовсе. Не конкурент по объекту. 🟡 Вторичный источник (MakerStack, обзор 20.03.2026, 7,6/10) добавляет: «It is not trying to be a full financial planning suite. It does one thing well: help you understand where your money goes»; «No native mobile app (responsive web only)»; «Budgeting is basic compared to envelope-style tools like YNAB» — **не аудировано, обзорный сайт**; вторичка расходится с первоисточником по сроку триала (14 дней против «30-day trial» на сайте) — верен первоисточник.

### Г30.4-К4 — Empower: 🟢 ДОБЫТО (в Г14.3 было «не добыто»; прежний адрес был неверен)

Рабочий адрес — **`https://www.empower.com/personal-investors/financial-tools`** (а не `/tools`, по которому Г14.3 получил 404): Exa fetch → **HTTP 200**, полный текст. Дословно: «Empower Personal Dashboard™ — Financial freedom starts here»; «Best budget app for tracking wealth and spending¹ January 2026» (сноска: «NerdWallet, "The Best Budget Apps for 2026" January 2026»); «Best Budgeting App for Tracking Net Worth³ 2025».

🔴 **Главное для нашей новизны — состав инструментов дословно:**
- Основные: **Portfolio analysis** («See how your portfolio performs. Understand your risk level, and where your money is invested»); **Retirement planning**; **Budgeting & cash flow**; **Net worth**.
- В блоке «People also use»: **Tax filing**; **Transactions**; **Savings Planner** («Stress-test your savings strategy to fund what matters in your life»); **Debt Paydown** («See everything you owe in one place as you track your progress to pay down debt»); **Emergency Fund** («Plan for the unexpected so you always have money on hand»).

**Это прямое подтверждение нашей рамки новизны по объекту, и оно сильнее прежних:** у Empower присутствуют **все три наших контура по отдельности** — погашение долга, резерв, цели-накопления — и **ни одного механизма, который делит один и тот же свободный рубль между ними**. Debt Paydown заявлен как «видеть всё, что должен, и отслеживать прогресс» (учёт и трекинг), а не как расчёт порядка и суммы. Плюс дословная оговорка модели монетизации: «Real people answer your money questions... get help from professionals for your next move⁴» — то есть **решение переносится на человека-консультанта**, дашборд остаётся воронкой. Это ровно то, что Г11 записывал «по общеизвестному»; теперь есть первоисточник.

### Г30.4-К5 — Product Hunt, DebtMeltPro: 🟢 ДОБЫТО (п. 3 списка «не добыто» Г14)

`https://www.producthunt.com/products/debtmeltpro` через Exa — **HTTP 200**, страница целиком с обсуждением. Дословно: «DebtMeltPro is a free online debt payoff calculator that helps you compare Snowball, Avalanche, and Hybrid strategies in real time. Add your debts to see your exact payoff timeline, total interest saved, and the best repayment plan. No signup required—simple, fast, and built for real-life debt management.» Статус: «Free»; «Launch tags: Productivity• Fintech»; «Launched 5mo ago» (то есть ~апрель 2026); «DebtMeltPro Info Launched in 2026»; «111 followers»; «No reviews yet»; адрес — `debtmeltpro.com/tools/debt-payoff`.

🔴 **Содержательная находка — автор описывает «гибрид» дословно** (ответ основателя Aditya Dubey на вопрос «How does it decide which debts to prioritize»): «Our hybrid strategy combines both interest rate (like Avalanche) and balance size (like Snowball) to optimise payoff. 1. It prioritises higher-interest debts to reduce overall interest 2. While also factoring in smaller balances to create quick wins and keep momentum. So it's essentially a balance between cost efficiency and motivation.» Ограничение, признанное автором: «Right now, the calculator assumes fixed interest rates for simplicity».

**Как это ложится на нашу рамку.** Это **второй после Toya AI (Г30.3) продукт, публично заявляющий метод сверх пары snowball/avalanche**, и первый, где механика гибрида описана словами автора. Но: (1) чистый **однокантурный калькулятор долгов** — ни резерва, ни целей, ни свободного денежного потока; (2) без входа и без учёта; (3) правило гибрида качественное, не формализованное (веса не названы), фиксированные ставки. Зазор по объекту (три контура из одного потока) устоял; зазор «никто не идёт дальше snowball/avalanche в долговом контуре» **продолжает сужаться** — теперь два независимых свидетельства за две недели добора.

### Г30.4-К6 — Механика Ray изнутри: 🟢 ДОБЫТО (п. 7 списка «не добыто» Г14) — детерминированный слой ЕСТЬ

Каналы: Exa search → репозиторий `https://github.com/cdinnison/ray-finance` (200), файл `src/ai/agent.ts` (200), сайт `https://rayfinance.app/` (200), индекс кода `https://deepwiki.com/cdinnison/ray-finance` (Exa fetch, **HTTP 200**, ~4 200 симв., «Last indexed: 10 May 2026 (180b35)»).

**Ответ на вопрос Г14 «есть ли под LLM детерминированный слой приоритизации» — ДА, но узкий.** DeepWiki дословно: «The AI subsystem uses a tool-calling loop. When you ask a question, the agent selects from a suite of tools (e.g., `get_net_worth`, `calculate_debt_payoff`) to fetch data from your local DB before generating a response.» То есть **`calculate_debt_payoff` — детерминированный инструмент**, считает расчёт погашения; решение же о том, *куда направить деньги*, принимает LLM в свободной форме. Подтверждение из истории версий: `https://github.com/cdinnison/ray-finance/compare/v0.4.2...v0.5.0`, дословно коммит **«939e667 fix: AI debt-payoff cascade + get_transactions account column/filter»**.

Дословный перечень подписей инструментов из `src/ai/agent.ts` (константа `TOOL_LABELS`): `get_net_worth`, `get_accounts`, `get_transactions`, `get_spending_summary`, `get_budgets`, `set_budget`, `get_goals`, `set_goal`, `get_score`, `get_recurring`, `get_alerts`, `save_memory`, `update_context`. 🔴 **Существенно: в этом перечне подписей `calculate_debt_payoff` НЕТ** — он в общем реестре инструментов (30+ по сайту: «Ray has 30+ tools that query your real bank data, run the math, and hand you the next move»), но не в списке «человекочитаемых меток спиннера». Архитектура ответа — агентный цикл на Anthropic/OpenAI/Ollama с PII-редактированием (`redact`/`unredact`), `MAX_TOOL_STEPS`, историей 30 сообщений с обрезкой по 24 000 символов.

**Как Ray формулирует ровно нашу задачу** (README и сайт, дословно, пример ответа): «You've got $34,200 across two cards and a car loan. At $95k with a baby coming in March, **pause the Japan fund and throw that $440/mo at the Chase card** — it's at 24.9%. That clears it by September and frees up $340/mo before the baby arrives.» 🔴 Это **дословно наш объект: цель против долга из одного потока**, с выбором в пользу долга по ставке. Но механизм — суждение LLM в диалоге, не расчёт на множестве альтернатив: ни весов, ни ранжирования вариантов, ни инвариантов; воспроизводимости ответа нет по устройству. **Зазор по методу (детерминированный расчёт вместо генерации) сохраняется; зазор по постановке задачи у Ray уже закрыт** — это самый близкий к нам продукт из найденных за всю кампанию по формулировке, что подтверждает Г30.3 (Toya AI) с другой стороны.

Цены Ray (сайт, дословно): «Ray has two plans. The free plan is fully open source (MIT licensed)... You pay your provider directly for AI usage, which is typically $1–3/month... Ray Pro is $10/month». Ограничение канала данных, признанное автором: «Plaid production access requires a business entity, isn't guaranteed, and takes 1–2 weeks if approved».

🆕 **Сверх очереди — форк с детерминированным слоем:** `https://github.com/loudsun1997/SenseiFi`, дословно: «This fork includes a Sensei-Fi decision layer on top of Ray... Highlights include BNPL cash-pressure ledgering, purchase consultant flows, VPU tracking, strategic friction, APR promo-term modeling, a local web dashboard/chat surface, and **deterministic debt payoff simulators**.» То есть сообщество само достраивает под LLM детерминированный контур — независимое подтверждение, что чисто генеративный советник недостаточен. Код форка не читался.

### Г30.4-К7 — Закрытие Maybe Finance: 🟢 ДОБЫТО с числами (п. 8 списка «не добыто» Г14), частично

Каналы: Exa search (первоисточники), Г18 закрывал часть — здесь добраны **числа и причина**, которых в Г14 не было.

**Josh Pigford, LinkedIn, 16.08.2025** (`https://www.linkedin.com/posts/joshpigford_tldr-maybe-is-pivoting-to-ai-based-b2b-business-activity-7362504170282655744-YHN5`), дословно:
- «We're about **6,000 paying customers short of breaking even, with only around 200 paying customers currently**, most of whom joined during the beta phases when the cost was significantly lower.»
- «The reality is that building a B2C personal finance platform is not only technically very challenging, but incredibly slow to grow, and we can't tackle those challenges while creating additional features people might be willing to pay for within the next **9 months (our current runway)**.»
- «I no longer believe a B2C personal finance app is our best bet for survival. The market's needs are too fragmented, and the feature set is too far from becoming valuable for more affluent customers. I believe it **either has to be completely bootstrapped for years or have $10's of millions in funding** to sustain and pour into growth.»
- «We've [got] roughly **$400,000 in the bank**.» · «We sunset the current version of Maybe. Again. No more giant B2C personal finance app. The economics just don't make sense for us.» · «We're pivoting to B2B financial forecasting & scenario planning tools.»
- Продолжение — **Maybe Investor Update, 02.09.2025**: «Just six weeks ago I sent an email out to some **25,000 investors, customers and newsletter subscribers**... And now here we are with an MVP and paying customers!»

**Обещанный «подробный разбор» — найден, это раздел «Recap, Reflections» в финальном релизе** `https://github.com/maybe-finance/maybe/releases/tag/v0.6.0` (Exa, 200). Дословно по главным причинам:
- «Tools like Plaid promise a lot but simply don't deliver for "net worth" tools like Maybe that need consistent data across dozens of financial data sources.»
- «Bank provider data being plain *wrong* (there is a surprisingly large amount of this)»; «Idiosyncracies of each financial institution (everyone reports their data a little differently)».
- «Needless to say, this is a *massive* challenge for anyone building a personal finance app and is the primary reason why "bootstrapping" a personal finance app with automated bank syncing is an uphill battle. **You need a lot of money and time to get this right.**»
- 🔴 Инженерный урок, прямо релевантный нашей архитектуре: «Every view of the app touches nearly *all* the user's data. If *any* piece of data is *wrong*, every view in the app is wrong. There is nowhere to hide in a personal finance app, and even the slightest change to the *date* of a historical transaction propagates upstream and affects the net worth graph, account sidebar trends, metrics, budgets, and pretty much every other view of the app!» Их решение — «hybrid event-sourced»: факты (transactions, trades, valuations) в БД, синк в фоновых задачах, запись в кэш-таблицы (`balances`, `holdings`), дословный размен: «improved performance, but at the *cost* of data consistency».
- Про открытый код и приватность: «We are open source, but in order to fix data bugs, we need to look at the data. If the user can't share all the required information, we can't reproduce the issue.»

**Ретроспектива первого закрытия (2023)** — тред Pigford, `https://threadreaderapp.com/thread/1747085524618424501.html`, дословно: «by the time we decided to shut it down we had **a couple thousand dollars in monthly recurring revenue**, but with our team of 8, that wasn't going to cut it»; «previously, we had a major human component. **every account came with your own certified financial advisor**. that's not only expensive from an employment perspective, but it also brings with it **a LOT of financial regulatory overhead**... that's no longer a part of the app.» 🔴 Последнее — прямое подтверждение нашей юридической рамки: **человек-советник в контуре = регуляторная нагрузка, и это убивало экономику дважды**.

**Осталось неизвестным по К7:** куда ушли ~200 платных подписчиков после сансета — ни одного источника ни в одном канале (Exa search, 1 запрос; ранее WebSearch в Г14). Отдельного поста «I'll write more about all of this in the future» сверх раздела в релизе v0.6.0 не существует на 16.09.2026.

### Г30.4-К8 — «Погашение кредитов» (ЦФТ): 🟢 ДОБЫТО (п. 6 Г14) — это платёжный сервис, а не советник

Г14 записал: «исключено из реестра, домен `cft.group` не резолвится, Wayback не архивировал». Exa нашла и продукт, и рабочий домен.

1. **Домен вендора — `cft.ru`, а не `cft.group`** (Exa search, страница `https://www.cft.ru/` — «Центр Финансовых Технологий. Программное обеспечение»). Ошибка Г14 — в адресе, не в доступности.
2. **Что это за продукт — дословно из каталога решений ЦФТ** (`https://ru.readkong.com/page/centr-finansovy-te-nologiy-3261361`, Exa, 200): раздел «СИСТЕМА "ЗОЛОТАЯ КОРОНА"» → «**"Золотая Корона – Погашение кредитов"** — koronapay.com. Сервис для оплаты кредитов, займов, внесения денежных средств на счет, пополнения карт Visa, Masterсard и "Мир" клиентами любого банка и крупнейших микрофинансовых организаций России». Заявленные свойства дословно: «Широкая сеть обслуживания»; «Высокая скорость зачисления денежных средств (min – мгновенно, max – 3 рабочих дня)»; «Оплата кредитов банков с отозванными лицензиями»; «Онлайн-оплата через сайт koronapay.com или бесплатное мобильное приложение "Золотая Корона – Погашение кредитов"».
3. Подтверждение классом смежных продуктов: «ЦФТ-Устройство самообслуживания» (CNews, 12.03.2013) — ПО для банкоматов, «включая открытие вкладов, пополнение счетов, погашение кредитов».

🟢 **Вывод: "Погашение кредитов" — платёжный шлюз (внести деньги в счёт кредита чужого банка), не инструмент выбора порядка и суммы погашения.** Гипотеза Г14 о возможном скрытом конкуренте в реестре ПО по этой записи **снята**. **Bonus Money** и «Финансовая грамотность» из реестра в этом доборе не открывались — остаются классифицированными по названию (см. задолженность).

### Г30.4-К9 — Чарты Mac App Store по жанру: ❌ НЕ БЕРЁТСЯ, причина не в антиботе

Пункт 5 Г14. Это дефект **самого API Apple** (классический RSS `…/rss/topfreemacapps/genre=<id>/json` отдаёт 0 позиций для жанров 12001–12022), а не блокировка доступа. Exa — поисковик по вебу, чужой RSS-эндпоинт она не чинит; пробовать её здесь бессмысленно по устройству канала. Пройденные каналы: `curl` по классическому RSS (Г14, 0 позиций на всех жанрах), `curl` по Marketing Tools API (Г14), **Exa — не применима к задаче**. Пункт переводится из «не добыто» в **«канал отсутствует»** — по Mac App Store сплошной чарт по жанру не публикуется вовсе.

### Г30.4-К10 — winget: ❌ КЛАСС «НУЖЕН ВЛАДЕЛЕЦ»

Пункт 4 Г14: code search по `microsoft/winget-pkgs` требует токен GitHub. Это не блокировка канала, а требование учётных данных — тот же класс, что USPTO ODP API в патентном блоке. Exa индексирует веб-страницы репозитория, но не даёт полнотекстового поиска по 10 000+ манифестов. Не пробовалось обходить сознательно.

## ИТОГ Г30.4 (этот файл)

**7 полностью, 1 частично, 2 нет с причиной.** Добыто: Capterra «Budgeting Software» (категория оказалась целиком B2B — отрицательный результат теперь измерен), Lunch Money (трекер, распределения нет), Empower (🔴 все три контура присутствуют по отдельности, механизма выбора между ними нет — прямая опора нашей новизны по объекту), DebtMeltPro (гибрид «ставка + остаток» словами автора), механика Ray (🔴 детерминированный инструмент `calculate_debt_payoff` под LLM есть; постановка задачи у Ray совпадает с нашей, метод — нет), закрытие Maybe с числами (200 платящих при 6 000 до безубыточности, $400 тыс., 9 мес. рантея), «Погашение кредитов» ЦФТ (платёжный шлюз «Золотая Корона», не советник). Частично: G2 (страница категории не берётся и Exa; сняты три смежные страницы, вывод тот же). Нет: чарты Mac App Store по жанру (канала не существует), winget (нужен токен GitHub — действие владельца). Сводный итог по всему Г30 — в `bank_patents_wellness_scoring_2026-09-09.md`.
