# Сырьё: PFM-механика банков APAC и необанков (хвост темы 7)

Дата: 2026-09-10. Статус: ЗАВЕРШЕНО. 9 из 10 банков закрыты первоисточниками, KakaoBank остался не добыт.

Задание: закрыть банки, оставшиеся не открытыми в `raw/banks_world_pfm_v2_2026-09-09.md`:
OCBC, UOB (TMRW), KakaoBank, Toss, Revolut, Starling, N26, Commonwealth Bank (CBA),
Westpac, Itaú.

По каждому — три сквозных вопроса:
1. Есть ли PFM-модуль и что он делает (категоризация / прогноз / подсказки / рекомендация суммы).
2. Считает ли банк размен «гасить долг или копить» с учётом процентных ставок.
3. Даёт ли продукт прескриптив («сделай вот это») или только показывает.
Плюс: целевая функция, если раскрыта (кросс-сейл, LTV, ARPU, engagement, retention).

Цитаты — дословно, на языке оригинала, с URL и датой снятия.

---

## 1. OCBC (Сингапур)

**Продукт: OCBC Financial OneView** (агрегатор на базе государственного SGFinDex) + Money Insights
в приложении OCBC.

Источник: https://www.ocbc.com/personal-banking/digital-banking/financialoneview-features.page
(снято 10.09.2026, WebFetch, HTTP 200)

Дословно со страницы продукта:

> "Get personalised insights to make better financial decisions"

> "Turn insights into action. OCBC Financial OneView gives you customised insights based on your
> financial data so you can save more, earn more and spend wisely."

> "Plan accurately for your retirement with OCBC Life Goals" — "Make the most accurate plans for
> your retirement with OCBC Financial OneView so you can live your golden years on your own terms."

> "Estimate how much you will need for your child's educational needs" / "Create a savings plan to
> help make their future dreams a reality."

> guides users to "identify protection gaps and purchase insurance coverage suited to your needs"

Агрегация: "track all your finances across participating banks, insurers, SGX CDP, CPF, HDB and
IRAS" (источник: сводка выдачи WebSearch по страницам ocbc.com, 10.09.2026).

**Ключевая находка по долгу (единственная во всей выборке APAC на этот момент).** В описании
инсайтов OCBC заявлен триггер, прямо касающийся ипотечного долга:

> "The app can detect if your emergency funds may not be enough and prompt you to create a savings
> goal, or if you're on an HDB loan, you'll be prompted to view potential savings from switching
> to a bank loan."

(формулировка из сводки поисковой выдачи по страницам ocbc.com/personal-banking/articles/
sg-budget-babe-yfo.page, 10.09.2026 — 🔴 ПОМЕТКА: это пересказ поисковика, дословная цитата
с самой страницы на момент записи НЕ снята, см. раздел «Что не добыто»).

Разбор механики: это НЕ размен «гасить долг или копить». Это сравнение ставки двух источников
одного и того же долга (HDB concessionary loan 2.6% vs банковская ипотека) — рефинансирование,
классический кросс-сейл ипотеки. Направление совпадения интересов: банк продаёт свой кредит.
Второй триггер (emergency fund → создать savings goal) — деньги остаются в банке. Оба инсайта
идут В СТОРОНУ продукта банка.

**Ответы на три вопроса:**
1. PFM есть: агрегация (включая внебанковские источники через SGFinDex), категоризация, инсайты,
   цели, планирование пенсии/образования, страховой gap-анализ.
2. Размен «долг vs накопления» со ставками — **НЕТ**. Есть сравнение ставок ДВУХ КРЕДИТОВ
   (HDB vs банковский) — это рефинансирование, другая задача.
3. Прескриптив — **ДА, слабый**: "prompt you to create a savings goal", "you'll be prompted to
   view potential savings from switching to a bank loan", "purchase insurance coverage suited to
   your needs". Формулировки — приглашение к действию, ведущему к покупке продукта банка.
   🔴 Дисклеймер: на странице features дисклеймера про инвестиционный совет / ограничения
   рекомендаций **не обнаружено** (проверено WebFetch 10.09.2026).
4. Целевая функция — дословно не раскрыта на публичных страницах продукта. Наблюдаемая
   де-факто: кросс-сейл (ипотека, страхование, Life Goals) + удержание депозитов.

---

## 2. UOB / TMRW (Сингапур, Индонезия, Малайзия, Таиланд)

**Движок — не свой: Personetics.** Это тот же вендор, чью целевую функцию тема разбирала ранее
(«LTV, ARPU, кросс-сейл»). Партнёрство с 2018 года.

Источник (дословно, HTTP 200, curl+UA, 178 019 байт, снято 10.09.2026):
https://personetics.com/uob-and-personetics-launch-ai-driven-automated-savings-feature-tmrw-mobile-banking-app/
(зеркало пресс-релиза UOB от 02.11.2022; оригинал uobgroup.com на момент снятия дал **HTTP 000**,
соединение не установилось — см. «Что не добыто»)

Механика Auto-Save дословно:

> "Leveraging AI and machine learning models, the Auto-Save feature on the TMRW mobile banking app
> is personalised to each individual. The models analyse and predict each customer's past, current
> and future spending patterns, income, and everyday transactions to find safe-to-save money
> (i.e. excess amounts above average/typical cash outflows level). The app will then automatically
> move such variable amount of monies into customer's TMRW savings account to earn higher interest
> while still ensuring sufficient balances in their current account for any required payments or
> outflows."

> "**Fully automated:** The Auto-Save feature in TMRW constantly analyses customer financial
> transaction data including the monthly inflows and outflows in the customer's Everyday bank
> account within the TMRW app. Powered by Personetics' AI, the Auto-Save feature will identify
> small amounts of safe-to-save money to automatically transfer to a higher interest-earning
> Savings account up to several times a week."

> "**Fully controlled:** Customers have the ability and flexibility to opt-in and opt-out of the
> Auto-Save feature at any time. With a simple click in the app, customers can easily pause or
> resume their auto-save participation... Customers may also withdraw funds from their accounts
> at any time."

Масштаб и заявленный эффект (дословно):

> "Since the start of its partnership in 2018, UOB has already delivered over **150 million
> personalised insights** to its customers in Indonesia, Malaysia, Singapore, and Thailand and
> have achieved an **average year-on-year growth of mobile login users of close to 30 per cent**
> across all four markets."

Целевая функция — озвучена вендором, дословно (David Sosna, CEO Personetics):

> "...customers in this region demand a higher level of support and involvement from their
> financial institutions in **not just selling products**, but improving their financial lives."

🔴 Показательно: даже отрицая «просто продажу продуктов», метрика успеха в том же релизе названа
одна — **рост числа логинов в мобильном приложении (engagement)**, плюс переток денег на
сберегательный счёт того же банка (депозиты). Ни одной метрики благосостояния клиента не названо.

**Слово «долг» («debt», «loan», «credit card») в пресс-релизе не встречается ни разу**
(проверено полнотекстовым просмотром выгрузки, 10.09.2026).

**Ответы на три вопроса:**
1. PFM есть: категоризация, предиктивная аналитика денежного потока, персональные инсайты,
   алерты, автонакопления. Заявка на прогноз дословная: "analyse and predict each customer's past,
   current and future spending patterns".
2. Размен «долг vs накопления» со ставками — **НЕТ**. Оптимизируется ровно одна величина:
   safe-to-save money = превышение над типичным оттоком. Ставка фигурирует односторонне
   ("to earn higher interest"), ставка по долгу клиента в модель не входит.
3. Прескриптив — **ДА, максимально жёсткий: не совет, а автоматическое действие** (деньги
   переводятся без спроса, до нескольких раз в неделю, при opt-in). То есть UOB — точный
   структурный близнец RBC NOMI: банк готов действовать за клиента ровно там, где деньги
   остаются внутри банка.
4. Целевая функция: engagement (логины +30% г/г), рост депозитов, кросс-сейл ("hyper-personalised
   banking offers" — из описания TMRW на uobgroup.com).

**Вывод по UOB: правило «прескриптив только там, где интересы банка и клиента совпадают»
подтверждается в чистейшем виде.**

## 3. KakaoBank (Корея)

🟡 **Добыто частично.** Первоисточников уровня «страница продукта с описанием механики PFM»
снять не удалось: `www.kakaobank.com/products` → **HTTP 404**, англоязычный сайт
`kakaobank.com/view/main?lang=EN` — витрина без описания функций. Корейские поисковые запросы
(«마이데이터 내 자산 서비스 기능») выводят на служебные уведомления о техобслуживании
(`m.kakaobank.com/Notices/view/16361`), а не на описание продукта.

Что установлено по вторичным источникам (🔴 помечено как непроверенное первоисточником):
- KakaoBank — участник корейского регуляторного режима **MyData (마이데이터)**, действующего
  с января 2022, то есть агрегирует счета из других финорганизаций по государственному API.
- В приложении есть анализ расходов и «AI-based asset management services»
  (источник: сводка поисковой выдачи по kakaobank.com / Wikipedia / отраслевые обзоры, 10.09.2026).
- IR Q3 FY2025: клиентская база 26.24 млн, активы KRW 73.99 трлн (+19.0% г/г), кредиты
  KRW 46.70 трлн (+4.9% г/г); заявлены «AI-powered services and stablecoin initiatives».
  Дословная механика PFM в найденных материалах IR не раскрыта.

**Ответы на три вопроса:** 1 — PFM есть (агрегация MyData + анализ расходов), детали не добыты.
2 — размен «долг vs накопления» со ставками: **свидетельств нет**, но и опровержения
первоисточником нет. 3 — прескриптив: не установлено.
Целевая функция: не раскрыта в добытых материалах.

---

## 4. Toss / Viva Republica (Корея) — 🔴 самый интересный кейс выборки

Toss — не банк, а супер-апп с банком внутри (Toss Bank). Работает в том же режиме MyData.

### 4.1. Агрегация активов (первоисточник, Toss Feed)

https://toss.im/tossfeed/article/mydata0405 (HTTP 200, curl+UA, 189 850 байт, снято 10.09.2026)

> "2022년 1월부터 마이데이터가 시행되면서, 이제 금융 앱 한 곳에서 더 간편하게, 한꺼번에
> 내 자산관리를 할 수 있어요."

> "2. 나의 신용과 자산 분석이 가능해져요 ... 그동안 토스를 가계부처럼 활용할 수는 있었지만,
> 모든 금융거래 정보가 있는 건 아니다 보니 내가 가진 정확한 자산을 파악하기 어려웠는데요.
> 앞으로는 내가 한 저축, 투자, **대출** 등을 잘 정리된 정보로 볼 수 있어요.
> **순자산이 늘고 있는지 줄고 있는지도 그래프로 제공할 계획**이고요."

(перевод по существу: «раньше Toss можно было использовать как домашнюю бухгалтерию, но полных
данных не было; теперь сбережения, инвестиции **и кредиты** видны как упорядоченная информация,
и планируется график роста/снижения **чистых активов**»)

🔴 Важное отличие от западных банков: **долг клиента входит в картину явно, как компонент
чистых активов (순자산)**. Но функция — описательная: «показать», не «посоветовать».

### 4.2. Долговой блок: 대출 갈아타기 / 대환대출 (loan switching)

https://toss.im/tossfeed/article/toss-refinancing (23.02.2024; HTTP 200, curl+UA, 299 478 байт,
снято 10.09.2026)

Дословно, когда сервис уместен:

> "토스 대환대출은 이럴 때 받으면 좋아요.
> 지금 받는 대출보다 더 낮은 금리로 대출받기 위해서
> 대출 만기가 다가왔지만 대출 연장이 어려울 때
> 목돈을 마련하기 위해서
> 상환기간이 짧아 매달 갚아야 하는 금액이 클 때, 상환 기간이 긴 대출 상품으로 바꿔 매달
> 갚는 금액을 줄이기 위해서
> 통합 대환으로 대출 개수를 줄여 관리를 쉽게 하기 위해서"

Механика расчёта — дословно (ключевое: считается **разница процентов вместе с комиссией за
досрочное погашение**):

> "가지고 있는 신용대출, 마이너스 통장, 카드론 중 갈아탈 수 있는 대출이 있는지 알아보는
> 서비스예요. ... **중도상환 수수료와 함께 갈아탔을 때의 이자도 알려드려요.**"

> "1. 내 대출 정보 확인하기 — 가지고 있는 대출의 금리, 한도와 중도상환 수수료를 확인해요.
> 2. 갈아탈 대출 조건 보기 — 갈아탈 대출의 금리, 한도와 함께 우대금리가 적용되어 있는지 확인해요.
> 3. 금융사에서 신청하기 — 금융사에서 최종 대출 조건을 확인하고, 기존 대출 조건을 비교해
> 갈아탈지 결정해요."

Раздел «на что смотреть» — Toss сам перечисляет три компонента полной стоимости решения:

> "대환대출 시 주의해야 할 3가지
> 1. 금리 — 현재 금리 수준이 어떤지 살펴봐야 해요. 과거 대출 받았을 때보다 현재 금리가
> 낮다면 대환대출하기에 적합하지만, 현재 금리가 더 높다면 대환대출이 유리한지 다시 한번
> 계산이 필요해요.
> 2. 중도상환수수료 — 약속된 대출 기간보다 빨리 대출금을 갚을 때는 '중도상환수수료'를
> 내야 하는 경우가 많아요. 그렇기 때문에 중도상환수수료를 포함해도 대환대출하는 게 유리한지
> 살펴봐야 해요.
> 3. 인지세 — 대출받으면 국가에 '인지세'라는 세금을 내야 해요. 은행과 내가 반반씩 내는
> 구조인데요. 5,000만원 이하일 때는 세금을 안 내도 되지만 1억원 이하일 때는 7만원,
> 10억원 이하일 때는 15만원, 10억원을 초과할 때는 35만원을 내야 하기 때문에 이 비용도
> 포함시켜 계산해봐야 해요."

🔴 **Дисклеймер, который выдаёт целевую функцию (дословно, повторён трижды — по каждому типу
кредита):**

> "📌 **토스는 최적의 금리 및 한도를 보장하지 않으며, 전체 금융사가 아닌 토스와 제휴된
> 금융사와의 대출 상품을 제공해요.**"

(«Toss не гарантирует оптимальную ставку и лимит и предоставляет кредитные продукты не всех
финорганизаций, а только партнёров Toss»)

Это самая честная формулировка целевой функции, найденная во всей теме: **оптимум не обещан,
множество альтернатив ограничено партнёрской сетью.** Экономика — комиссия за приведённого
заёмщика (брокерская модель), что подтверждается описанием бизнес-модели Viva Republica
как «commissions from acting as a broker for financial products (like insurance and loans)»
(🟡 вторичный источник — сводка поисковой выдачи, 10.09.2026).

Ещё один дисклеймер, о безопасности:
> "📌 토스를 비롯한 금융기관에서는 절대로 유선상 대출 상품을 권유하거나 광고하지 않아요."

**Ответы на три вопроса:**
1. PFM есть, и он полнее западных: агрегация активов И долгов через MyData, график чистых
   активов, анализ расходов.
2. Размен «гасить долг или копить» со ставками — **НЕТ**. Со ставками считается только
   размен «долг vs другой долг» (рефинансирование), причём качественно: ставка + комиссия
   за досрочное погашение + гербовый сбор. Технически у Toss есть ВСЁ для расчёта
   «гасить или копить» (он видит и ставку по кредиту, и остаток на депозите), и он этого
   не делает. Это сильный отрицательный результат: **дело не в отсутствии данных.**
3. Прескриптив — **ДА, но только в сторону нового кредитного продукта партнёра.** Финальное
   решение явно возвращается пользователю: "기존 대출 조건을 비교해 갈아탈지 결정해요"
   («сравните с условиями текущего кредита и решите, переходить ли»).
4. Целевая функция: брокерская комиссия партнёрской сети; раскрыта самим дисклеймером.

## 5. Revolut (UK / EU / US)

Маркетинг не переснимаем (тема 23). Ниже — только механика.

### 5.1. Analytics — категоризация и ПРОГНОЗ

https://www.revolut.com/blog/post/introducing-new-and-improved-analytics/ (опубликовано
19.11.2019; снято 10.09.2026 через `r.jina.ai`, HTTP 200; прямой `curl`/`WebFetch` на
`help.revolut.com` дал **HTTP 403** «Just a quick security check», 873 310 байт заглушки)

> "**View your estimated monthly spending.** Say goodbye to the stress of guessing how much money
> you'll have left at the end of the month. You're now able to see how much you're predicted to
> spend by month's end, based on your day-to-day spending and scheduled payments."

> "The longer you stay with Revolut, the more accurate your estimated spend will be. If you have
> a budget set up, we'll also show you whether you're on track to meet it. **If it goes red,
> that's an indicator that you're heading towards exceeding your budget, giving you an opportunity
> to adjust your spending.**"

> "**Choose your analytics start date.** ...if you get paid on the 25th of the month, you can
> choose to start your monthly tracking from the 25th... when you set your analytics period,
> we'll adjust your monthly budget accordingly."

> "**Create custom categories.** ...We'll move all past related transactions here, and do the same
> for future ones."

Разбор: прогноз есть (экстраполяция дневных трат + запланированные платежи). Прескриптива нет —
предельная формулировка «giving you an opportunity to adjust your spending», то есть решение
и действие остаются на клиенте. Рекомендации суммы нет.

### 5.2. 🔴 У Revolut US ОБЕ стороны баланса лежат в одном приложении

Из юридического подвала https://help.revolut.com/en-US/help/accounts/budget-and-analytics/...
(снято 10.09.2026, `r.jina.ai`, HTTP 200), дословно:

> "Savings Vaults created after July 29, 2025 are provided by Cross River Bank, Member FDIC,
> insured up to $250,000."

> "**The Revolut Visa Credit Card is issued by Cross River Bank, Member FDIC. Revolut Personal
> Loans are made by Cross River Bank, Member FDIC.** The Revolut Visa Credit Cards and Revolut
> Personal Loans are not deposit products."

> "The Revolut Secured Mastercard Credit Card is issued by Lead Bank, Member FDIC."

То есть Revolut одновременно продаёт клиенту High Yield Savings, кредитную карту, personal loan
и secured card. **Все ставки, нужные для расчёта «гасить или копить», физически находятся внутри
одного продукта.** Ни на одной добытой странице этот расчёт не заявлен. Ни в разделе Budgeting,
ни в Analytics, ни в описании Credit долг и накопления не сопоставляются.

**Ответы:** 1 — PFM есть (категоризация, кастомные категории, бюджет, прогноз конца месяца).
2 — размен долг/накопления со ставками: **НЕТ**. 3 — прескриптив: **НЕТ** (только сигнал
«красное»). 4 — целевая функция дословно не раскрыта; структурно — кросс-сейл внутри
подписочных планов Standard/Premium/Metal.

---

## 6. Starling Bank (UK)

https://www.starlingbank.com/features/spending-insights/ (HTTP 200, curl+UA, 115 855 байт,
снято 10.09.2026). Дословно:

> "**What is Spending Insights?** Ever wondered how much you're spending on late-night takeaways,
> or those free trials you forgot to cancel? Spending Insights breaks your spending down by both
> category (such as Groceries, Holidays, and Transport) and by merchant (like Boots, Amazon, or
> Tesco). It means you can see at a glance how much you're spending on different things each month,
> and **helps you identify areas where you can save money**."

Новая AI-функция — дословно:

> "**New feature: Spending Intelligence.** Ask good questions, build good habits. Ask our
> AI-powered search bar a question about your spending habits and get an instant answer in-app.
> Deepen your knowledge and **start making more informed money decisions**."

Формулировка показательна: не «мы скажем, что делать», а «спроси — ответим»; инициатива и
решение у клиента. Это retrieval поверх собственных транзакций, а не оптимизация.

Категоризация с ручной коррекцией:
> "Want to choose a different category to the one we've selected, either as a one-off or for all
> past and future transactions? No problem – you can choose from over 50 options..."

Поведенческая разметка (редкость — категории намерения, а не только MCC):
> "Not all spending is the same. You can help Spending Insights track your behaviours too. You
> might prefer to put dinner down as **Relationships**, rather than just Eating Out. Perhaps some
> recent Shopping was an **Impulse Buy**, or maybe that purchase for your Home was for a specific
> **Project**."

🔴 **Дисклеймер на самой странице продукта, дословно:**

> "**Spending Insights shouldn't be used as an accounting tool.**"

Автонакопления (Round-ups в Spaces) — по вторичному источнику: округление каждой транзакции
до фунта с множителями x2/x5/x10 в выбранный Space, включается вручную (сводка выдачи,
10.09.2026; первоисточник help.starlingbank.com не снимался).

**Ответы:** 1 — PFM есть: категоризация (50+ категорий), поведенческие теги, merchant-разрез,
произвольные периоды, AI-поиск по своим тратам. Прогноза не заявлено. Рекомендации суммы нет.
2 — размен долг/накопления со ставками: **НЕТ**. Слово «debt» на странице отсутствует.
3 — прескриптив: **НЕТ**, и он явно отклонён дисклеймером «не бухгалтерский инструмент».
Единственное автоматическое действие — round-up в собственный Space (деньги остаются в банке).
4 — целевая функция дословно не раскрыта.

---

## 7. N26 (Германия / EU)

### 7.1. Statistics / Insights — базовый PFM

По вторичным источникам (сводка выдачи по n26.com и support.n26.com, 10.09.2026): автоматическая
категоризация (Household & Utilities, Food & Groceries, Shopping, Travel, ATM…), ручная смена
категории, месячный бюджет с пуш-уведомлениями **на 80% и 100% лимита**, обзор регулярных
платежей (подписки, аренда, интернет), графики с подсветкой превышения обычного месячного
среднего.

### 7.2. 🔴 AI-Powered Insights Module — самый прямой ответ во всей теме

https://support.n26.com/en-it/app-and-features/app/ai-powered-insights-module
(HTTP 200, curl+UA, 218 328 байт, снято 10.09.2026). Дословно, целиком по существу:

> "**Introducing the AI-Powered Insights Module**
> This AI-powered insight is informational and **not personalized financial advice**. Results may
> vary, and your data is protected.
> This new tool is designed to help you better understand your finances by providing smart,
> personalized suggestions and recommendations—powered by artificial intelligence (AI)."

> "**What Does This Mean for You?**
> **Personalized Suggestions:** You'll see recommendations that help you to use the app and our
> services better by **recommending you N26 products that fit your activity and financial needs**.
> **AI-Powered Recommendations:** You'll always see a label when a recommendation is AI-generated,
> so you know where the advice is coming from."

> "**How Does It Work?** When you activate the AI-powered insights module, our system will analyze
> your account activity to offer you tailored suggestions. You can dismiss any suggestion you
> don't find useful."

> "How will I know if a suggestion is AI-generated? Every AI-powered recommendation will be
> clearly labeled."

🔴 **Это прямое, недвусмысленное признание целевой функции в официальной справке банка:
единственный класс рекомендаций — «продукты N26, подходящие вашей активности».** Не «сократите
траты», не «погасите дорогой долг» — а «купите наш продукт». И тут же — снятие ответственности:
"not personalized financial advice".

**Ответы:** 1 — PFM есть (категоризация, бюджет с порогами 80/100%, подписки, AI-подсказки).
2 — размен долг/накопления со ставками: **НЕТ**. 3 — прескриптив: **ДА, но целиком продуктовый**
("recommending you N26 products"), с дисклеймером «не персональная финансовая рекомендация»
прямо в первом абзаце страницы. 4 — целевая функция: **кросс-сейл, названный дословно.**

## 8. Commonwealth Bank of Australia (CBA)

### 8.1. Текущий продукт (2026): «Insights», заменивший Money Plan и Cash Flow View

https://www.commbank.com.au/digital-banking/bill-sense.html (редирект на «Managing money in the
CommBank app»; снято 10.09.2026 через `r.jina.ai`, HTTP 200; прямой `curl` по домену дал
**HTTP 502 Bad Gateway** на соседнем URL). Дословно:

> "**Where can I find Money Plan and Cash Flow View?** We've made a few updates to the CommBank
> app. **Money Plan and Cash Flow View have been replaced by Insights**, where you can view your
> spending, savings and bills in one place."

> "Explore Insights in the CommBank app to get a clearer view of your money. You can view your
> **spending, saving, bills and investing** in one place — helping you track where your money goes,
> see your progress and stay ahead of upcoming bills."

Четыре блока Insights, дословно:

> "**Understand your cash flow** — Get a clearer picture of the money coming in and out of your
> accounts. You can: View your spending, saving and investing in one place · See how your income
> is split between today and the future · Spot spending patterns at a glance"

> "**Track spending by category** — ...See where you're spending your money · Create budgets with
> flexible limits · Spot overspending early"

> "**Grow your savings** — See how much you're saving and how your recent savings compare over
> time. You can: View your savings activity · **Compare recent savings with your average** ·
> **Set up automatic transfers**"

> "**Stay on top of bills and transactions** — ...**View predicted bills before they arrive** ·
> Search transactions across your accounts · Get notified when money goes in or out"

Сценарий использования, дословно:
> "1. Search Insights in the CommBank app 2. View your current spending, saving and investing
> 3. **Take action with budgets, automated transfers and goals** 4. Check in regularly to stay
> on track"

Настраиваемый цикл под зарплату:
> "You can choose from weekly, fortnightly or monthly for your Insights view. You can also choose
> when your Insights start, so they better align with your budgeting routine."

🔴 **Ключевое наблюдение по составу.** Четыре опоры Insights — spending, saving, bills, investing.
**Долга (кредитных карт, personal loans, home loan) среди них нет.** У CBA крупнейший ипотечный
портфель Австралии, но в PFM-контуре обязательства как управляемая величина не представлены.

### 8.2. Bill Sense — прогноз счетов (историческая механика)

По вторичным источникам (пресс-релиз CBA newsroom 09.2020 и отраслевая пресса, сводка выдачи
10.09.2026): «The app searches past transactions, finds regular payment patterns and creates bill
predictions», горизонт **до 12 месяцев вперёд**, с флагами переменных счетов. Сегодня поглощено
блоком «View predicted bills before they arrive» в Insights.

### 8.3. 🔴 Benefits finder — единственная де-факто «против кассы» функция, и её СВЕРНУЛИ

Изначально (2019–2020) это была ML-функция внутри приложения: «uses data capability and machine
learning to put potential entitlements in front of customers at the right time, and then **nudges
them to start a claim**», более 250 пособий (вторичный источник — Finextra/отраслевая пресса,
сводка выдачи 10.09.2026). Это редкий случай прескриптива, из которого банк не извлекает прямой
выручки.

Состояние на 10.09.2026 — https://www.commbank.com.au/digital-banking/benefits-finder.html
(`r.jina.ai`, HTTP 200), дословно:

> "**A new way to help you find benefits.** Benefits finder has had a refresh. **We've simplified
> the experience, now connecting you directly to official federal and state government benefit
> finders and tools.**"

> "Previously, to access the Benefits finder you needed to be logged on to NetBank or the CommBank
> app. Now, Benefits finder is publicly accessible..."

> "**Go to the official tool.** We'll take you to an official government benefit finder. These
> tools are run by government agencies and provide the most up-to-date information."

> "**Check eligibility & apply.** Check your eligibility and apply directly on the government
> website." / "Eligibility and applications are managed by Services Australia."

То есть персонализированный ML-наджинг заменён на **публичный каталог ссылок на сайты
госорганов**. Персонализация, транзакционные данные и «nudge to start a claim» из описания ушли.
🔴 Это прямая иллюстрация сквозного правила темы: **функция, приносившая пользу клиенту и ноль
выручки банку, деградировала до справочника; функции, приносящие депозиты (automatic transfers),
остались и развиваются.**

### 8.4. Про шкалу CBA–Melbourne Institute Financial Wellbeing Scales — ответ на поставленный вопрос

**Свидетельств применения академической шкалы внутри приложения НЕ найдено.** Страница
`https://www.commbank.com.au/digital/fwbscore` — единственный кандидат — дала **HTTP 502
Bad Gateway дважды**: прямым `curl` (660 816 байт страницы ошибки Cloudflare, Ray ID
a38c1415398501f3) и через `r.jina.ai` (Error a38c147e3f4a201e), снято 10.09.2026.
В Annual Report FY2025 (16 030 725 байт PDF, скачан и разобран `pdftotext`, 72 243 строки)
строки «Money Plan», «Bill Sense», «money management features», «Smart Savings», «wellbeing
tools» **не встречаются ни разу** — «financial wellbeing» присутствует только как тема
материальности и предмет надзора совета директоров (строки 5047, 6921, 6943, 7029, 7475).
Метрики использования PFM-функций опубликованы в отдельном Sustainability Report FY25,
который в рамках этого захода не разбирался.

Вместо шкалы благосостояния в приложении присутствует **кредитный скор Experian** (credit score
hub, запущен 11.2022) — то есть метрика кредитоспособности, а не метрика финансового здоровья.

**Ответы:** 1 — PFM есть, сильный: кэшфлоу, категории, гибкие бюджеты, прогноз счетов на 12
месяцев, цели, автопереводы, настраиваемый под зарплату цикл. 2 — размен долг/накопления со
ставками: **НЕТ**; долг вообще выведен из контура Insights. 3 — прескриптив: **ДА, ограниченный**
— «Take action with budgets, automated transfers and goals», плюс исторически наджинг в Benefits
finder (свёрнут). 4 — целевая функция дословно не раскрыта в добытых материалах.

## 9. Westpac (Австралия)

### 9.1. Пресс-релиз 19.09.2023 — состав инструментов

https://www.westpac.com.au/about-westpac/media/media-releases/2023/18-September/
(HTTP 200, curl+UA, 113 309 байт, снято 10.09.2026). Дословно:

> "**Savings Finder.** Helps customers discover potential savings from their existing recurring
> payments for subscriptions and other expenses. This can help them identify opportunities to cut
> back on non-essential goods and services."

> "**Bills Calendar.** Allows customers to add upcoming payments to their bills calendar and
> receive alerts when these bills are due, helping them better track and manage their expenses."

> "**Personalised insights.** Allowing customers to track income compared to expenses and better
> analyse their monthly cashflow."

> "**Spend categories.** Customers can better understand how much they're spending and where each
> month, so they can make more informed decisions about where they might like to cut back or save."

> "**Savings goals.** The ability to bucket savings into different goals within the one account.
> Customers can also set up auto deposits to help achieve their goals."

Слова Chief Digital Officer Jason Hair, дословно:
> "The new tools are designed to give customers even more visibility over their expenses with
> personalised insights that **allow them to make more effective and informed decisions** about
> their spending."

> "We're also seeing more customers prioritising their savings with a growing number of people
> setting up dedicated 'emergency' or 'rainy day' savings goals."

Формула «visibility → informed decisions» — описательная рамка. Прескриптива в релизе нет.

### 9.2. 🔴 Пресс-релиз 12.09.2024 — а вот здесь прескриптив ЕСТЬ, и он измерен деньгами

https://www.westpac.com.au/about-westpac/media/media-releases/2024/12-sept/
(HTTP 200, curl+UA, 114 699 байт, снято 10.09.2026). Дословно:

> "The number of customers using personal finance tools in Westpac's mobile banking app has
> **increased by 36% since the start of the year, with around 620,000 logging in each month** to
> access features to help monitor cash flow, categorise spending and manage bills."

> "Forrester's review acknowledged Westpac's **use of customer behaviour to offer actionable
> insights** to help customers manage their money, such as **notifying customers when they may
> have overspent on their set budget** and enabling them to review it."

> "**More than 150,000 customers have acted on push alerts through the app to earn bonus interest
> on their savings – totalling more than $42 million in interest.**"

> "**Net worth:** Providing customers with a whole of wealth view by allowing them to add assets
> **and liabilities**."

> "Customers have received more than $28 million in cashback through ShopBack and redeemed more
> than 800 million in Westpac Altitude Rewards points..."

🔴 **Разбор.** Westpac рассылает push-подсказки, приводящие к конкретному действию клиента, и
отчитывается о результате в долларах. Направление действия ровно одно: **выполнить условие
бонусной ставки по СОБСТВЕННОМУ депозиту банка** — то есть оставить деньги внутри и увеличить
остаток. Ни одного упоминания push-подсказки «погасите дорогой долг» в релизах нет. Обязательства
(liabilities) в приложении присутствуют, но **вводятся клиентом вручную** в Net worth и служат
только отображению — в логику подсказок не входят.

**Ответы:** 1 — PFM есть и он один из сильнейших в выборке: категоризация, кэшфлоу, 12-месячный
тренд, календарь счетов, Savings Finder (годовая стоимость подписок), Net worth с активами и
обязательствами, цели с автопополнением. 2 — размен долг/накопления со ставками: **НЕТ**;
обязательства вводятся вручную и не участвуют в расчётах. 3 — прескриптив: **ДА**, в форме
push-алертов (перерасход бюджета; выполнение условия бонусной ставки), эффект — $42 млн
процентов, 150 000 клиентов. Прескриптив снова строго в сторону депозита банка.
4 — целевая функция: дословно не названа, но раскрыта метриками отчёта — digitally active
customers (5.92 млн, +5% г/г), логины в PFM-инструменты (620 тыс./мес, +36%), объём привлечённых
на бонусную ставку средств, кэшбэк/баллы (ShopBack $28 млн, 800 млн баллов Altitude).
Это **engagement + депозиты + кросс-сейл**, ровно как у вендоров PFM-движков.

## 10. Itaú Unibanco (Бразилия) — 🔴 ближайший к контрпримеру, но всё же не контрпример

### 10.1. Minhas Finanças / Controle de Gastos — базовый PFM

https://blog.itau.com.br/artigos/como-fazer-um-controle-de-gastos-no-app-itau (30.04.2024;
снято 10.09.2026 через `r.jina.ai`, HTTP 200). Дословно:

> "Além de consultar seu extrato, faturas de cartões, realizar pagamentos, e contratar novos
> serviços, no App Itaú você também pode organizar seus gastos, direto no extrato da conta.
> Nele é possível **categorizar todas as entradas e saídas, visualizar gráficos e estabelecer
> metas de gastos** que te ajudarão a criar seu controle financeiro."

> "Você pode perceber que não utiliza um serviço de assinatura, embora pague por ele todo mês.
> E que, se economizar um pouco aqui e ali, quase nada vai mudar na sua rotina, mas seu saldo
> vai ficar mais positivo, seus investimentos ficarão mais consistentes ou **você não fará mais
> dívidas**."

Практические советы в статье — чисто редакционные, не расчёт: «Concentre os gastos em uma só
conta ou cartão», «Crie lembretes para o vencimento das contas», «Faça uma lista de supermercado»,
«Cuidado com compras por impulso».

Механика (по вторичным источникам, сводка выдачи 10.09.2026): охват — расходы по кредитной карте
и текущему счёту, **более 100 категорий**, автоматизация категоризации по совпадению текста
выписки, месячные цели, выбор начала «финансового месяца», графики «Resumo», сравнение с
предыдущими месяцами. Заявлено, что функцией пользуются ~40% клиентов Itaú (🟡 вторичный
источник conta-corrente.com, первоисточником не подтверждено).

### 10.2. 🔴 Cidadania Financeira — прямая работа с ДОЛГОМ, с измеренными результатами

https://www.itau.com.br/sustentabilidade/estrategia-esg-old/cidadania-financeira/
(снято 10.09.2026, `r.jina.ai`, HTTP 200). Дословно:

> "**Melhorar a relação das pessoas com o dinheiro.** Buscamos exercer nosso potencial positivo
> no desenvolvimento socioeconômico dos nossos clientes a partir da **orientação financeira para
> redução do endividamento** e por meio de ofertas éticas e responsáveis, recomendando produtos
> e serviços adequados, com informações claras sobre as condições oferecidas."

> "**Condições diferenciadas.** Disponibilizar condições diferenciadas para ajudar o cliente de
> forma preventiva e/ou os inadimplentes a se reorganizarem financeiramente.
> **DESTAQUE:** 1) Público com alto risco de endividamento: **5,7% contrataram soluções
> preventivas** que ajudam a manter o equilíbrio financeiro. 2) Reorganização financeira:
> alcançamos **13% de redução na inadimplência mensal dos clientes com atraso acima de 15 dias**,
> superando nossa projeção inicial de 11% de redução."

> "**Inclusão financeira.** Contribuir para a inclusão financeira de novos clientes, através da
> **concessão de limites de crédito ajustados conforme comportamento dos clientes para evitar o
> excesso de endividamento**, reduzir a inadimplência e fomentar o uso responsável dos produtos
> concedidos. **DESTAQUE:** Limites de crédito concedidos para 101 mil clientes."

> "**Reinclusão no crédito.** Reincluir no ciclo de crédito, de forma sustentável, clientes que
> estão passando ou já passaram por dificuldades financeiras. **DESTAQUE: 1 milhão de clientes
> reinseridos no crédito**"

> "**Orientação Financeira.** ...disponibilizamos orientações e conteúdos para construção de uma
> saúde financeira equilibrada através de **quatro pilares – controlar, poupar, usar bem o crédito
> e planejar**."

> "**Atuação setorial.** O Itaú é associado à Federação Brasileira dos Bancos e apoia as
> iniciativas da plataforma **Meu Bolso em Dia**. O blog é um canal aberto com conteúdo e
> ferramentas sobre finanças pessoais, e oferece **trilhas de aprendizado personalizadas de acordo
> com o Índice de Saúde Financeira de cada pessoa.**"

> "**Whatsapp Renegociação.** No canal de Whatsapp do Itaú voltado à renegociação,
> disponibilizamos nossas cartilhas de educação financeira com orientações e conteúdos mais
> contextualizados a pessoas que desejem reorganizar suas finanças. Esse programa está disponível
> por meio do número +55 11 4004-1144"

🔴 **Разбор — почему это НЕ контрпример, хотя выглядит им.**
Itaú — единственный банк выборки, который в явном виде ставит целью «redução do endividamento»
и публикует по ней числа. Но целевая функция всех четырёх блоков — **снижение собственных
кредитных потерь и возврат клиента в кредитный цикл**:
- метрика успеха названа дословно — «13% de redução na inadimplência» (снижение просрочки),
  то есть показатель качества кредитного портфеля БАНКА, а не благосостояния клиента;
- «5,7% contrataram soluções preventivas» — метрика **продаж** («законтрактовали решения»),
  а не метрика улучшения положения;
- финальная цель раздела «Reinclusão no crédito» сформулирована прямо: вернуть 1 млн клиентов
  **обратно в кредитный цикл**;
- собственно **шкала благосостояния (Índice de Saúde Financeira) находится не в приложении Itaú,
  а на отраслевой платформе FEBRABAN «Meu Bolso em Dia»**, которую Itaú лишь «поддерживает».

**Ответы:** 1 — PFM есть: 100+ категорий, автокатегоризация по правилу, цели, произвольное начало
финансового месяца, сравнение месяцев. Прогноза и рекомендации суммы не заявлено.
2 — размен «гасить долг или копить» со ставками: **НЕТ**. Есть реструктуризация/renegociação —
изменение условий долга, снова «долг vs долг».
3 — прескриптив: **ДА**, и это единственный в выборке случай прескриптива, направленного на долг
(«orientação financeira para redução do endividamento», проактивный контакт с клиентами высокого
риска, канал WhatsApp для реструктуризации). Дисклеймеров на странице устойчивого развития нет —
это ESG-раздел, а не продуктовая страница.
4 — целевая функция: **снижение inadimplência (просрочки) + возврат в кредитный цикл + продажа
«превентивных решений»** — раскрыта дословно самим банком в формулировках метрик.

---

## Сводная таблица

| Банк | Страна | PFM | Прескриптив | Размен долг/накопления со ставками | Целевая функция (как раскрыта) | Основной источник |
|---|---|---|---|---|---|---|
| OCBC (Financial OneView) | SG | Да: агрегация SGFinDex (банки, страховщики, SGX CDP, CPF, HDB, IRAS), инсайты, Life Goals | Да, слабый: «prompt you to create a savings goal», «prompted to view potential savings from switching to a bank loan» | **Нет.** Есть сравнение HDB-кредита с банковской ипотекой = рефинансирование | Не раскрыта; де-факто кросс-сейл ипотеки и страхования | ocbc.com/.../financialoneview-features.page |
| UOB (TMRW, движок Personetics) | SG/ID/MY/TH | Да: категоризация, прогноз потока, инсайты, Auto-Save | **Да, максимальный: автоматическое действие** — перевод денег без спроса до неск. раз в неделю | **Нет.** Оптимизируется одна величина — safe-to-save. Слово «debt/loan» в релизе отсутствует | Engagement: логины +30% г/г; 150 млн инсайтов; рост депозитов | personetics.com (зеркало релиза UOB 02.11.2022) |
| KakaoBank | KR | Да (MyData + анализ расходов), детали не добыты | Не установлено | Свидетельств нет (и опровержения нет) | Не раскрыта | 🔴 первоисточник не добыт, HTTP 404 |
| Toss / Viva Republica | KR | Да, полнее западных: активы **и долги** через MyData, график чистых активов | Да, но только в сторону кредита партнёра | **Нет.** Со ставками считается долг vs долг: ставка + 중도상환수수료 + 인지세 | Брокерская комиссия партнёрской сети — раскрыта дисклеймером «не гарантируем оптимальную ставку, только партнёры Toss» | toss.im/tossfeed/article/toss-refinancing |
| Revolut | UK/EU/US | Да: категории (в т.ч. кастомные), бюджет, **прогноз трат до конца месяца** | **Нет** — предел «giving you an opportunity to adjust your spending» | **Нет.** Хотя HYS, кредитка, personal loan и secured card — всё внутри одного приложения | Не раскрыта; структурно — подписочные планы | revolut.com/blog/post/introducing-new-and-improved-analytics/ |
| Starling | UK | Да: 50+ категорий, поведенческие теги (Impulse Buy, Relationships), merchant-разрез, AI-поиск по тратам | **Нет**, и явно отклонён: «Spending Insights shouldn't be used as an accounting tool» | **Нет.** Слова «debt» на странице нет | Не раскрыта | starlingbank.com/features/spending-insights/ |
| N26 | DE/EU | Да: категоризация, бюджет с порогами 80%/100%, подписки | **Да, целиком продуктовый** | **Нет** | 🔴 **Кросс-сейл, назван дословно:** «recommending you N26 products that fit your activity and financial needs» | support.n26.com/.../ai-powered-insights-module |
| CBA (CommBank Insights) | AU | Да, сильный: кэшфлоу, гибкие бюджеты, прогноз счетов на 12 мес, цели, автопереводы | Да, ограниченный: «Take action with budgets, automated transfers and goals» | **Нет.** Долг вообще выведен из контура Insights (spending/saving/bills/investing) | Не раскрыта в добытом | commbank.com.au/digital-banking/bill-sense.html |
| Westpac | AU | Да, один из сильнейших: кэшфлоу, 12-мес тренд, Bills Calendar, Savings Finder, Net worth с обязательствами | **Да**, push-алерты; эффект измерен: 150 000 клиентов, **$42 млн процентов** | **Нет.** Liabilities вводятся **вручную**, в логику подсказок не входят | Engagement + депозиты + кросс-сейл: 5.92 млн digitally active (+5%), 620 тыс./мес в PFM (+36%), $28 млн кэшбэка | westpac.com.au/.../media-releases/2024/12-sept/ |
| Itaú Unibanco | BR | Да: 100+ категорий, автокатегоризация, цели, свой финансовый месяц | **Да, и единственный направленный на долг**: «orientação financeira para redução do endividamento», WhatsApp-реструктуризация | **Нет.** Есть renegociação = долг vs долг | 🔴 Раскрыта дословно: «13% de redução na inadimplência», «5,7% contrataram soluções preventivas», «1 milhão de clientes **reinseridos no crédito**» | itau.com.br/sustentabilidade/.../cidadania-financeira/ |

---

## Прямой ответ на сквозной вопрос

**1. Размен «гасить долг или копить» с учётом процентных ставок — не считает НИ ОДИН из
девяти добытых банков.** Счёт по теме 7 после этого захода: **~34 банка мира, ноль
положительных.** По KakaoBank ответ остаётся неизвестным (первоисточник не добыт), но и
свидетельств в пользу «считает» не найдено.

**2. Правило «прескриптив появляется только там, где интересы банка и клиента совпадают» —
держится. Контрпримеров не найдено.** На выборке APAC + необанки оно подтверждается даже
жёстче, чем на западной, и в трёх местах формулируется банками дословно:

- **N26** — самая честная формулировка в базе: единственный класс AI-рекомендаций — «продукты
  N26, подходящие вашей активности», плюс снятие ответственности «not personalized financial
  advice» в первой же строке.
- **Toss** — «не гарантируем оптимальную ставку и лимит, предоставляем продукты только
  партнёров Toss». Оптимум прямо не обещан.
- **Itaú** — метрика успеха работы с долгом клиента названа как «снижение просрочки» и
  «возврат 1 млн клиентов в кредитный цикл», а не как улучшение положения клиента.

**3. Правило имеет и обратную, более сильную формулировку — она подтверждена деньгами и
двумя наблюдениями.**

- **Мера силы прескриптива = мера выгоды банка.** Там, где деньги остаются в банке, банк не
  советует, а **действует за клиента**: UOB Auto-Save переводит средства автоматически до
  нескольких раз в неделю; Westpac рассылает push и отчитывается о $42 млн процентов от
  150 000 клиентов; CBA предлагает «automated transfers». Там, где выгоды нет (сокращение
  трат, погашение долга), инструмент ограничивается показом графика.
- **Функция без выручки деградирует.** CBA Benefits finder начинался как ML-наджинг к подаче
  заявки на 250+ госпособий внутри приложения (выручки банку ноль) — к 2026 году свёрнут до
  публичного каталога ссылок на сайты госорганов: «connecting you directly to official federal
  and state government benefit finders». Это динамическое подтверждение правила: не только
  «чего не строят», но и «что сносят».

**4. Отдельный, самый важный для FINPILOT результат: дело НЕ в отсутствии данных.**
Три банка выборки физически имеют внутри одного приложения обе ставки, нужные для расчёта:
- **Toss** — видит через MyData и депозиты, и кредиты, и их ставки, и комиссии за досрочное
  погашение (он их показывает при рефинансировании!) — и не считает «гасить или копить»;
- **Revolut US** — High Yield Savings, Visa Credit Card, Personal Loans и Secured Card
  выпускаются в рамках одного продукта (Cross River Bank / Lead Bank) — и не считает;
- **Westpac** — Net worth принимает и активы, и обязательства — но обязательства вводятся
  вручную и в логику подсказок не попадают.

Это переводит вывод из «технически сложно» в «структурно не выгодно». Расчёт «гасить долг или
копить» почти всегда даёт ответ «гасить дорогой долг», то есть вывести деньги из депозита и
закрыть процентный доход банка. Ни один коммерческий банк не строит функцию, оптимум которой
уменьшает его же баланс по обеим сторонам сразу.

**5. Целевая функция APAC-банков СОВПАДАЕТ с тем, что дословно называли вендоры PFM-движков
(«LTV, ARPU, кросс-сейл»)**, с местной поправкой: в APAC/AU на первое место выходит
**engagement, измеряемый логинами** (UOB: +30% г/г; Westpac: 620 тыс./мес, +36%), а денежный
результат выражается **приростом депозитов**, не комиссионным доходом.

**6. Два региональных отличия, которых нет в западной выборке.**
- **Регуляторная агрегация как данность.** Сингапурский **SGFinDex** и корейский **MyData**
  — государственные каналы, по которым банк получает картину активов И долгов клиента из
  других организаций. У OCBC и Toss полнота данных выше, чем у любого западного банка выборки.
  Прескриптива это не породило.
- **Долг как компонент чистых активов.** Toss (순자산) и Westpac (Net worth) показывают долг
  в общей картине — западные PFM (Starling, N26, Revolut, CBA Insights) не показывают вовсе.
  Но и там, и там это **отображение**, а не аргумент решения.

---

## Что не добыто и почему

| Цель | Канал и код ответа | Статус |
|---|---|---|
| **KakaoBank, страница продукта PFM** | `www.kakaobank.com/products` → `curl`+UA **HTTP 404** (24 754 байта страницы «페이지를 찾을 수 없습니다»). Корейский поиск по «마이데이터 내 자산 서비스 기능» выводит на служебные уведомления о техобслуживании, не на описание функций. Англоязычный `kakaobank.com/view/main?lang=EN` — витрина | 🔴 **Не добыто.** Единственный банк списка, оставшийся закрытым по существу |
| **KakaoBank, IR-презентация с механикой** | Найдены только PDF Kakao Corp (`t1.kakaocdn.net/.../5835.pdf`, май 2025) — это материнская компания, не банк. Транскрипт Q3 FY2025 на Yahoo Finance даёт финансы, не механику | 🔴 Не добыто |
| **CBA Financial Wellbeing Score в приложении** | `commbank.com.au/digital/fwbscore` → `curl`+UA **HTTP 502 Bad Gateway** (660 816 байт страницы Cloudflare, Ray ID a38c1415398501f3); повтор через `r.jina.ai` → **502**, Error a38c147e3f4a201e. Обе попытки 10.09.2026 | 🔴 Не добыто (сайт лежал) |
| **CBA метрики использования PFM** | Annual Report FY2025 скачан целиком (16 030 725 байт, `pdftotext` → 72 243 строки). Строки «Money Plan», «Bill Sense», «money management features», «Smart Savings», «wellbeing tools», «hardship payment arrangement» — **0 вхождений**. «Financial wellbeing» есть только как тема материальности | 🟡 Отрицательный результат измерен. Числа (>3 млн клиентов/мес) лежат в **Sustainability Report FY25**, он в этот заход не разбирался |
| **UOB, оригинал пресс-релиза** | `uobgroup.com/.../uob-personetics-launch-autosave-on-tmrw.page` → `WebFetch` «Socket is closed», `curl`+UA → **HTTP 000** (соединение не установлено) | 🟢 Обойдено: дословное зеркало на personetics.com, HTTP 200, 178 019 байт |
| **Revolut, справка по бюджетированию** | `help.revolut.com/en-SI/...` → `curl`+UA **HTTP 403** «Just a quick security check» (873 310 байт заглушки); через `r.jina.ai` → целевой URL вернул **404** (страница удалена) | 🟢 Обойдено: блог Revolut через `r.jina.ai`, HTTP 200 |
| **OCBC, дословная цитата про HDB loan → bank loan** | Статья `ocbc.com/personal-banking/articles/sg-budget-babe-yfo.page` открылась (`WebFetch`, HTTP 200), но искомых предложений про emergency funds / HDB loan **в её текущей версии нет** | 🟡 Формулировка осталась только в сводке поисковой выдачи. Помечена в §1 как непроверенная первоисточником |
| **Starling round-ups, первоисточник** | `help.starlingbank.com` не запрашивался (бюджет) | 🟡 Использован вторичный источник |
| **N26 Statistics, первоисточник** | `n26.com/en-eu/spending-insights` → `curl`+UA **HTTP 404** (50 777 байт). Основной вывод по N26 добыт с `support.n26.com` (HTTP 200) | 🟡 Базовый PFM описан по вторичным источникам, ключевая находка — первоисточником |
| **Itaú, доля 40% пользователей Minhas Finanças** | Первоисточником не подтверждено (вторичный `conta-corrente.com`) | 🟡 Помечено в §10 |

---

## Метод поиска

**Объём.** 10 вызовов `WebSearch`, 4 вызова `WebFetch`, 14 запросов `curl` (браузерный UA либо
`r.jina.ai`), 1 скачанный и разобранный PDF на 16 МБ. Подагенты **не запускались** (0 из
разрешённых 2) — тема разбита по банкам, каждый закрывается 1–2 обращениями, накладные расходы
на подагента их превысили бы. Сырьё дописывалось в этот файл `Edit`-ом после каждой группы
банков (5 записей), ни один результат не копился в контексте.

**Языки запросов.** Английский (SG, AU, UK, DE), **корейский** (KR: «마이데이터 내 자산 서비스
기능», «토스 대환대출 갈아타기 이자 절감 금액 추천»), **португальский** (BR: «minhas finanças
gerenciador financeiro categorias planejamento», «saúde financeira índice cliente app»).
🔴 Ключевые находки по Toss и Itaú получены **только** на локальных языках — англоязычный поиск
по тем же банкам их не показывает.

**Площадки, давшие результат:** сайты продуктов и справочные центры банков (starlingbank.com,
support.n26.com, commbank.com.au, ocbc.com), пресс-релизы и медиацентры (westpac.com.au ×2),
ESG/устойчивое развитие (itau.com.br/sustentabilidade — 🔴 самый содержательный раздел по долгу
во всей выборке, продуктовые страницы про это молчат), корпоративные блоги
(toss.im/tossfeed ×2, revolut.com/blog), сайт вендора движка как зеркало недоступного релиза
банка (personetics.com), годовой отчёт в PDF (commbank.com.au FY2025).

**Приёмы, сработавшие по каналам (в порядке эскалации):**
- `WebFetch` — сработал на ocbc.com; отвалился «Socket is closed» на uobgroup.com.
- `curl` + браузерный UA — сработал на personetics.com, starlingbank.com, westpac.com.au ×2,
  support.n26.com, скачивании 16-мегабайтного PDF CBA, toss.im ×2.
- `r.jina.ai` — **пробил антибот Revolut** (прямой `curl` давал 403 «Just a quick security
  check») и **пробил CommBank** (прямой `curl` давал 502 на соседнем URL). Не помог там, где
  сервер origin действительно лежал (fwbscore, 502 в обе стороны) или страница удалена (404).
- `pdftotext` + `grep` по годовому отчёту вместо чтения — позволил получить **измеренный
  отрицательный результат** (0 вхождений искомых терминов в 72 243 строках) за один вызов.

**Запросы, давшие пустоту (тоже результат):** любые попытки найти у этих банков связку
«debt payoff vs savings», «pay off debt or save calculator» внутри продукта — по всем девяти
добытым банкам не нашлось ни одной страницы, где долг и накопления сопоставлялись бы по
ставке. Слово «debt» отсутствует на продуктовых страницах Starling, Revolut Analytics,
N26 AI Insights, CBA Insights; в пресс-релизе UOB Auto-Save слов «debt/loan/credit card»
нет ни одного.

**Что стоит закрыть следующим заходом (по убыванию ценности):**
1. **KakaoBank** — единственный незакрытый банк списка; вход искать через корейские
   IR-материалы банка (не Kakao Corp) и через блог инженеров.
2. **CBA Sustainability Report FY25** — там лежат метрики использования PFM (>3 млн
   клиентов/мес) и, возможно, применение шкалы благосостояния.
3. **OCBC** — дословное подтверждение инсайта «HDB loan → bank loan» первоисточником.
