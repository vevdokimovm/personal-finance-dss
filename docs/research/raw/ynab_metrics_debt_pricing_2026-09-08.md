# YNAB — Age of Money, долговые инструменты, цена. Дословный ответ исследования

**Дата:** 08.09.2026. **Канал:** `/research` (base-kit:researcher), 5 субагентов в двух кругах.
**Статус:** первичный материал, сохранён ДО выжимки (правило проекта §9, PIT-013).

**Канальная особенность, определившая результат:** `support.ynab.com` отдаётся JS-шаблоном,
и `WebFetch` возвращает пустое тело. Всё существенное вытянуто через `curl` с распаковкой HTML.
🔴 Именно из-за этого предыдущий проход счёл формулу Age of Money недокументированной.

---

## 1. Age of Money — алгоритм

🔴 **Формула ОПИСАНА официально.** Прежнее утверждение выжимки «справка не даёт алгоритма» неверно.

**Окно расчёта:**
> «Age of Money considers your last ten outflow cash transactions (including credit card payments)
> and asks, "How long were the dollars used for those transactions sitting around in your accounts,
> on average?"»

Второе подтверждение там же:
> «The Age of Money calculation requires ten outflow cash transactions, so it may be that you haven't
> made that many cash transactions since starting your spending plan.»

То есть окно — **не календарное, а событийное: последние 10 расходных cash-транзакций**
(https://support.ynab.com/en_us/age-of-money-H1ZS84W1s).

**Что исключено:** «(Transfers and starting balances aren't considered in these calculations.)»

**Карты:** «Your Age of Money is based on cash spending. If you use your credit card for most of your
purchases, it's normal for your Age of Money to stagnate until you pay your card or make some more
cash purchases» — свайп картой не событие, событием становится платёж по карте.

**Нерегулярность (только по расходам):** «if you recently did some spending that exhausted the last
few pennies of a paycheck from a couple of months ago, your Age of Money can drop suddenly, even though
you didn't do anything rash!» Поведение при нерегулярном **доходе** нигде не описано.

**Сопоставление доллара с датой прихода — реверс-инжиниринг, НЕ официально:** автор независимой
реализации (`kevinburke/ynab-go`) утверждает, что простого FIFO нет: «YNAB uses a weighted average
to calculate age of money for a single transaction that spans multiple buckets»; формулы весов
не приводит.

**Задвинули ли показатель — да, но не убрали:** метрика перенесена с главного экрана бюджета
в отдельный раздел **Reflect** (следует из инструкций доступа в актуальной справке: iOS/Android —
вкладка Reflect; веб — Reflect в левом сайдбаре). Community-подтверждение с датой: issue «Move Age
of Money back to the top» от 15.04.2025 в Toolkit for YNAB
(https://github.com/toolkit-for-ynab/toolkit-for-ynab/issues/3586).

🔴 **Показатель жив как first-class-сущность**, а не доживает в UI — он есть в официальном
OpenAPI-контракте, в объекте месяца:
```yaml
age_of_money:
  type: [integer, "null"]
  description: The Age of Money as of the month
  format: int32
```
Возвращается через `GET /budgets/{budget_id}/months` (https://api.ynab.com/papi/open_api_spec.yaml).

**Установить НЕ удалось:** точную дату и официальное объявление переноса в Reflect (проверены блог
и два слага справки — «не найдено в проверенных местах», не «не существует»); механику весов при
транзакции из нескольких «корзин»; обработку возвратов (refund); поведение при нерегулярном доходе;
входит ли «Ready to Assign».

---

## 2. Долговые инструменты — совет или калькулятор

🔴 **Ранжирования «какой долг гасить первым» софт YNAB не производит нигде.** Все четыре артефакта
работают по одному кредиту за раз и считают то, что человек ввёл сам.

| Артефакт | Вердикт |
|---|---|
| Loan Payoff Simulator | только моделирует ввод, один кредит |
| Student Loan Planner | не отдельный инструмент — те же Loan Accounts на пачке кредитов; только учёт |
| Loan Accounts | амортизация одного кредита; сумму или дату выбирает пользователь |
| Debt Payment targets | чистый калькулятор |

Решающая улика — **их собственный блог описывает межкредитное решение как ручной перебор**:
«Need to decide between putting a bonus toward your mortgage or your student loans? **Try both.**»
(https://www.ynab.com/blog/ynab-loan-planner). Человек прогоняет симулятор дважды и сравнивает
глазами — софт своего порядка не предлагает.

Loan Accounts: «Enter a monthly payment amount and YNAB will calculate how much interest you'll save
and the payoff date for your loan. If you'd prefer, you can select a payoff da[te]…»
(https://support.ynab.com/en_us/loan-accounts-a-guide-HkNSkPHJi). В обе стороны свободную переменную
задаёт пользователь.

Student Loans — только механика представления: «We recommend leaving the loan payment category
unpaired when dealing with multiple student loans»
(https://support.ynab.com/en_us/student-loans-in-ynab-a-guide-B1rUVwKSs). Ни слова о приоритизации.

🔴 **Отдельно и строго врозь: редакционный совет у них ЕСТЬ, и он — snowball.**
> «We recommend choosing your smallest debt as the one to blast into oblivion first… This approach
> is called the Debt Snowball Method. While there are other effective methods… this is the one we
> recommend with a gold star.»
> «We recommend the Snowball Method in debt payoff. Focus on the smallest balance first.»
(https://www.ynab.com/guide/how-to-get-out-of-debt)

Это **текст, написанный человеком в гайде**, никак не связанный с вычислениями продукта. Софт даёт
числа, блог даёт мнение, и они не сведены в одну функцию.

**Установить НЕ удалось:** очевидцев (Reddit/обзоры), описывающих экран, — ни одного, так что
«нет ранжирования» держится на текстах YNAB, а не на наблюдении живого продукта; платный ли отдельно
симулятор; строится ли где-нибудь совмещённый график по нескольким долгам.

---

## 3. Цена и модель подписки, 2026

С живой страницы https://www.ynab.com/pricing, снято 08.09.2026:

- **$14.99/мес** или **$109/год** (экономия $70), плюс налог.
- **Бесплатного тарифа нет.** Только триал.
- **Триал 34 дня, карта не требуется** при регистрации напрямую; оговорка YNAB: «third-party app
  stores may require credit card information when signing up for a trial»
  (https://www.ynab.com/our-free-34-day-trial).
- **Студентам — год бесплатно** (College Program, нужна справка). Рефералка: по месяцу обеим сторонам,
  не действует при покупке через Apple.
- **Одна подписка — до 6 человек** (YNAB Together).
- **Региональных цен нет вовсе:** «YNAB is priced in US dollars. Exchange rates are not reflected
  in the price.» Проверявший агент имел австралийскую точку выхода и всё равно видел USD.

**Про рубль и РФ — наполовину открыто.** Валюта задаётся одна на бюджет, без автоконвертации
(https://support.ynab.com/en_us/using-multiple-currencies-in-ynab-a-guide-SyBF6PHno) — но список валют
там не перечислен, поэтому есть ли RUB в пикере, неизвестно. Direct Import (Plaid) покрывает США,
Канаду и 18 стран Европы — **России в закрытом перечне нет**
(https://support.ynab.com/en_us/direct-import-in-europe-Syae1z_A9); ручной ввод и файловый импорт
работают из любой страны. В ToS (https://www.ynab.com/terms) нет пункта про Россию — только шаблонная
экспортная оговорка; при этом отдельные terms для UK/Switzerland/EEA существуют.

**Установить НЕ удалось:** пройдёт ли российская карта оплату; есть ли RUB в пикере; официальный
список языков интерфейса — попавшееся утверждение «YNAB поддерживает русский» при трассировке
оказалось **подменой**: русский есть у стороннего расширения Toolkit for YNAB (Crowdin), а не у самой
YNAB; дату последнего повышения цены (вторичные источники дают $50 → $84 → $99 → $109 и переход
$11.99 → $14.99 «в конце 2024», без первичного подтверждения); цифру $179/год в Apple App Store.

---

## Побочные находки по гигиене репозитория (агент не правил — не его поручение)

- `docs/research/raw/README.md` — таблица обрывается на пункте 12, строки про `ynab_targets_mechanics_2026-09-08.md` нет.
- `docs/research/sources_registry.md` — ни одной ссылки на YNAB.
- `docs/research/competitors/README.md` обещает подкаталог `raw/`, которого в `competitors/` нет.
