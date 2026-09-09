# YNAB Targets — механика, дословный ответ исследования

**Дата:** 08.09.2026. **Канал:** `/research` (base-kit:researcher), подагент «YNAB Targets mechanics».
**Статус:** первичный материал, сохранён ДО выжимки (правило проекта §9).
**Оговорка автора ответа:** страницы справки отдаются JS-шаблоном, WebFetch возвращал пустое
тело — материал тянулся через `curl` с распаковкой экранированного HTML из payload; тексты дословные.

---

## 1. Типы целей (Targets), актуальная модель

Источник: https://support.ynab.com/en_us/getting-started-with-targets-ryAEP08xC

Верхний уровень — не «типы», а **каденция**: `Weekly`, `Monthly`, `Yearly`, `Custom`
(цитата из https://support.ynab.com/how-to-use-targets-rk5kkI9ks: «Select how often you want
the target to repeat (its cadence): **Weekly, Monthly, Yearly, or Custom**. If you don't want
a target to repeat, choose the custom option»). Внутри каденции выбирается **behavior**.

**Weekly** — «Assign and spend up to this amount each week in a month… The total target amount
is based on which day you've chosen your week to "start over", and how many of those days are
in that month». То есть требуемое за месяц = недельная сумма × число выбранных дней недели в месяце.
- `"Set aside another..."` — «the target will prompt you to assign enough to meet the target for
  the full month, divided weekly. With this option, money will build up in the category over time»
  (остаток НЕ зачитывается, деньги копятся).
- `"Refill up to..."` — «the target will prompt you to refill funds used in the previous month,
  up to that month's target amount… you'll only assign enough to fill the category up to the
  target amount (based on how many weeks are in the month)».

**Monthly** — «Assign and spend up to this set amount each month. This target period follows
a calendar month».
- `"Set aside another..."` — «prompt you to assign the full amount of the monthly target again…
  money will build up in the category over time».
- `"Refill up to..."` — «prompt you to refill any funds that left the category in the previous
  month, up to that month's target amount».

**Yearly** — сумма к дате «By»; «Assign $600 for taxes by next year and the target will ask you
for **$50 each month**» → требуемое в месяц = сумма / число месяцев до даты. Повторяется
автоматически после прохождения месяца даты.
- `"Set aside another..."` — «Because "Set aside another" only tracks **what you assign (not what
  you spend)**, spending from the category won't affect the new target period».
- `"Refill up to..."` — «refill any funds that left the category in the previous year, up to that
  months target amount».
- Важное: «Since there can only be **one target in a category in a single month**, the new target
  period will start the month after the previous one ends».

**Custom** — «Assign and spend up to this amount by a given date. YNAB will prompt you to assign
a certain amount each month to stay on track to meet the target amount… custom targets can only
be set to repeat monthly or yearly». Три поведения:
- `"Set aside..."` — «prompt you to assign the full target amount by the due date… If the target
  repeats, you'll choose whether to "set aside another..." or "refill up to..."». Пример: «Assign
  $300 every six months… The target will ask you for $50 each month and reset every six months».
- `"Fill up to..."` — «the target will take into account **any currently available funds in the
  category** and prompt you to assign the remaining target amount by the due date».
- `"Have a balance of..."` — «the target will prompt you to assign money so **the Available balance
  of the category matches the target amount by the due date**. This target does not repeat, and it's
  not meant to be spent from before it's due». Дата опциональна.

**Biweekly не существует**: «There is no way to set biweekly targets in YNAB».

**Парные цели (только для категорий, связанных со счётом)** — https://support.ynab.com/en_us/paired-targets-BJJI8rdC5
- Credit Card Payment: `Pay Specific Amount Each Month` — «prompt you to assign a certain amount
  towards your balance each month, no matter what… The target doesn't care how much you've paid
  towards your balance, or how much you've added to it».
- Credit Card Payment: `Pay off Balance by Date` — «calculate a monthly amount to assign in order
  to pay off your credit card debt by a certain date… The balance you're paying off changes as you
  spend on the card, so **the amount needed to pay may be different every month. The amount will
  also adjust month to month if you are making slower or faster progress than your original plan**».
- Loan-категории: `Monthly Debt Payment` — «Calculations are based on an **amortization calculator**,
  so the interest rate for the loan needs to be entered… Any debt added to the loan account means
  you'll need to delete and create a new Debt Payment target, since this type of target doesn't take
  into account any new debt added after the target is created».

## 2. Недобор (underfunded)

- Индикация: «If your target is underfunded, a **yellow** available amount will be shown in the
  category» (https://support.ynab.com/how-to-use-targets-rk5kkI9ks).
- Недобор **не переносится отдельной сущностью**: «If you look to a future month, you will not see
  the target repeat… **YNAB will not recalculate the target until the new month begins**».
- Механика переноса зависит от behavior, а не от «долга»: «If you choose the "Set aside another..."
  behavior, the target will prompt you to assign the entire target amount again, even if funds from
  the previous month weren't fully spent and have rolled over. If you choose the "Refill up to..."
  behavior, the target will only ask you to replace **what you spent or unassigned** last period».
- Явный **пересчёт растущего взноса при отставании** документирован только для `Pay off Balance
  by Date` и косвенно для custom-с-датой («to stay on track»). Дословной формулы вида
  «(цель − доступно)/оставшиеся месяцы» справка **не приводит**.
- Оговорки, важные для реализации:
  - «Leftover funds don't count toward "Refill up to" targets **until the new month begins**».
  - «Refunds… **aren't counted towards a target**… Once the target period rolls over, any refund
    money still in the category will then count towards the next target period».
  - «Yearly targets track funds set aside **across the full target period** — not just what's
    currently in the category».
  - Редактирование цели ретроактивно: «Editing a target will change it in **all instances** of that
    target, in prior and future months».

## 3. Поведение остатка

Названий «Set Aside / Refill up to / Set to Zero» как триады в актуальной справке нет. Актуальный
набор: `Set aside another...`, `Refill up to...` (weekly/monthly/yearly) и `Set aside...` /
`Fill up to...` / `Have a balance of...` (custom). «Set to Zero» — старая терминология goals;
ближайшие живые сущности — Auto-Assign `Reset Available Amount` и `Reset Assigned Amount`.
Ещё есть **snooze** цели; для кредитных: «Credit card targets can't be snoozed».

## 4. Перерасход категории

Источники: https://support.ynab.com/en_us/overspending-in-ynab-a-guide-ryWoxEyi ·
https://support.ynab.com/en_us/credit-card-overspending-an-overview-HkMGpSbJs

Автоматически **не покрывается** — деньги переносит пользователь («If you select a future month,
YNAB will cover overspending from money you've assigned in the future»).

- **Cash (красный)**: «you've spent more than you have in a category using a cash account». Перенос:
  «YNAB does this by **subtracting cash overspending from Ready to Assign in the following month**…
  If you had planned to move money from another category to cover the overspending, that adjustment
  is **no longer possible once the month ends**».
- **Credit (жёлтый)**: «Without enough money in the category, the overspent dollars **won't move to
  the Credit Card Payment category**—you now have debt on the card». И: «**Overspending on a credit
  card does not roll over when the month rolls over**» — вместо этого «uncovered credit overspending
  **increases the credit card balance** when the month rolls over».
- Смешанный случай: «If you spent with both cash and credit cards in your overspent category,
  **YNAB takes the cash out first**… a blend of overspending types will show as red».
- Покрытие задним числом: «If you have overspent categories in a previous month, your Credit Card
  Payment category will have an "Underfunded" alert… **move money directly to the Credit Card Payment
  category in the current month**».
- При покрытии в текущем месяце: «The previously overspent funds will also **automatically move back
  to your Credit Card Payment category**».
- Обратная связь с целью по карте: «If there is overspending on the card that isn't covered, then when
  the month rolls over and that additional balance is absorbed into the card, **the next month's target
  prompt will be more**».

## 5. Подсказки продукта (Auto-Assign)

Источники: https://support.ynab.com/en_us/auto-assign-a-guide-r1gBNbBJo ·
https://support.ynab.com/en_us/underfunded-a-guide-BJwPhQO09

Шесть кнопок на web и mobile: **Underfunded, Assigned Last Month, Spent Last Month, Average Assigned,
Average Spent, Reduce Overfunding**; плюс две только на web: **Reset Available Amount, Reset Assigned
Amount**. Average Assigned/Spent — «rolling average… up to the last 12 months… the current month's plan
is excluded». Reduce Overfunding — «any excess funds above what is needed for your current targets will
be moved up to Ready to Assign». Перед применением показывается preview, есть Undo.

**Порядок приоритета Underfunded** (дословный список):
1. «Categories with **overspending** (this will not only cover overspending but also fully fund any
   targets that are set in the overspent categories)».
2. «**Scheduled Transactions** and, in order of due date, Weekly targets and Monthly targets with
   a specific due date selected».
3. «All **Monthly targets with "End of Month"** selected».
4. «**Custom targets with a due date in a future month** (prioritized in order of due date)».
5. «**Credit Card payoff targets**, any Credit Card Payment Scheduled Transactions, and Credit Card
   Payment categories with an Underfunded alert».
6. Тай-брейк: «Underfunded logic will apply in a **top-to-bottom order** of your categories».

Останов: «If Ready to Assign reaches $0.00 at any point in this order, the funding will automatically stop».

**Игнорируются логикой**: «Categories with a "**Have a Balance" target that don't have a due date**»;
категории без цели (если нет Scheduled Transaction / Underfunded Alert); категории с **snoozed** целью
и без Scheduled Transactions.

Прогресс-бары (https://support.ynab.com/en_us/progress-bars-a-guide-SkDEhot09): секций 1 (месяц/период),
2 (перенос + назначенное в этом месяце, только для `set aside another`), 4–6 (недельные цели по неделям);
цвета: зелёный — цель закрыта, жёлтый — назначено, но цель не выполнена, серый — не финансировано,
красный — перерасход.

---

## Что установить НЕ удалось (дословно из ответа)

1. Точной формулы пересчёта требуемого месячного взноса при отставании для НЕ-парных целей с датой
   (yearly / custom by date) — справка даёт только пример «$600 → $50 в месяц» и формулировку
   «to stay on track»; прямого утверждения «взнос растёт при отставании» для них нет (оно есть только
   для `Pay off Balance by Date`).
2. Точной арифметики для weekly-цели, когда выбранный день недели встречается в месяце 5 раз, кроме
   общего указания «YNAB will occasionally prompt you to set aside more than you need».
3. Машинных названий/полей API для behavior — смотрелась только справка, не API-документация.
4. Релиз-нот с датами введения текущей терминологии — бюджет вызовов исчерпан на справке.
