# Survey — international (English) edition

> Что это. Пакет для запуска **англоязычной версии** исследовательского опроса FINPILOT
> («Как Вы выбираете куда направить свои деньги?») для иностранной аудитории. Ядро —
> скрипт `finpilot_survey_en.gs`, который **сам строит готовую Google-форму** (все 62 вопроса,
> 7 разделов) — руками ничего создавать не нужно. Этот файл: как запустить скрипт, таблица
> соответствий RU↔EN для сверки перевода, и принятые решения по переводу.

> **История версий.** Это **v2** (внесена v5.25.0, мёрж параллельной вахты) — она **заменяет**
> первую генерацию v5.19.0, где суммы намеренно оставались в ₽ «ради сопоставимости волн».
> Решение пересмотрено: сопоставимость обеспечивают **пропорции кейса**, а не валюта, — а
> ₽-форма для иностранного респондента бессмысленна. ₽-вариант не потерян: git-история и
> архивы ≤ `finpilot_v5_24_0_intl.zip`. Источник вопросника — `../raw/survey_questionnaire_62q.pdf`.

---

## 1. Как получить готовую форму (2 минуты)

1. Открой `https://script.google.com` → **New project**.
2. Удали пример, вставь весь файл `finpilot_survey_en.gs`.
3. **Run** → функция `buildSurveyForm`.
4. Google попросит авторизацию (скрипт создаёт форму на твоём Drive) → **Allow**.
5. По завершении смотри **Execution log**: там печатается **EDIT-ссылка** (редактировать) и
   **SHARE-ссылка** (давать респондентам).

Форма создаётся на английском, с прогресс-баром, разбитая на 7 секций как оригинал.

---

## 2. Принятые решения по переводу (важно — сверь)

1. **Валюта — USD ($), под иностранную аудиторию.** Суммы **пере-заякорены с сохранением
   пропорций** кейса (доход : обязательные : кредит : цель : свободные), а не по буквальному курсу —
   так сценарий остаётся релевантным и калибровка исследования не ломается. Кейс Q26: доход
   **$4,000/мес**, обязательные **$2,500** (те же 62.5%), кредит **$3,000** под 20% (мин. платёж
   **$200/мес**), цель **$5,000**, резерв **$750**, свободно в конце месяца **$1,500**. Согласованы:
   Q43 (пример-описание), Q48 (ценник: до $2 / $2–5 / $5–10 / разово $15–30 / % от сэкономленного),
   Q59 (доход: <$1,000 … >$12,000, $4,000 — середина как в кейсе), Q13 (пример фикс-суммы $500/мес).
   Для **€** те же числа работают 1:1 — достаточно заменить знак `$`.
2. **Мусорные/троллинг-варианты вычищены.** В выгрузке ответов были шуточные опции (например в
   семейном положении — «Воробушек», «хуй его знает»; в доходе-инструменте — «Мозг», «Счёты»).
   В форму вошли **только реальные варианты** оригинала.
3. **Ранжирование (Q14)** собрано как сетка 1–5. API Apps Script **не умеет** включать «Ограничить
   один ответ на столбец» — если нужен строгий ранкинг (одно число в столбце), включи это вручную
   в редакторе формы для Q14. Иначе респондент сможет поставить одинаковый ранг нескольким строкам.
4. **Флаги «обязательный»** повторяют помеченные `*` в оригинале; остальные — необязательные.
5. **«Другое» (Other)** добавлено там, где в оригинале был свободный вариант «Другое:».
6. Проверка внимательности **Q47 (7 звёзд)** оставлена как шкала 1–7 (просьба выбрать 7).

---

## 3. Билингвальный референс (RU → EN), в порядке формы

Тип: **SC** single-choice · **MC** multi-choice (checkbox) · **SCALE** линейная шкала · **GRID** сетка ·
**RANK** сетка-ранжирование · **TXT** короткий текст · **PARA** абзац. `*` — обязательный. `+O` — есть «Другое».

**Раздел 1. Как Вы сейчас управляете финансами / How you currently manage your finances**

| # | Тип | RU (оригинал) | EN |
|---|---|---|---|
| 1 | MC*+O | Что используете для учёта финансов? | What do you use to track your finances? |
| 2 | SC | Сколько банков используете в повседневной жизни? | How many banks do you use in daily life? |
| 3 | MC* | Что именно у Вас есть в этих банках? | What exactly do you have in these banks? |
| 4 | SC* | Как часто заглядываете в свои финансы? | How often do you check your finances? |
| 5 | SC | Использовали ли ИИ-ассистент конкретно для финансов? | Have you used an AI assistant specifically for financial questions? |
| 6 | MC | Что мешает доверять ИИ-ассистенту в финансах? | What stops you from trusting an AI assistant with financial questions? |
| 7 | SC* | Как долго пользуетесь этим инструментом? | How long have you used this tool? |
| 8 | MC*+O | Чем реально помогает текущий инструмент? | How does your current tool actually help you? |
| 9 | MC*+O | Что раздражает в интерфейсе финансовых приложений? | What annoys you about the interface of finance apps? |
| 10 | MC+O | Чего инструмент НЕ умеет, но Вы бы хотели? | What can your current tool NOT do that you'd want? |
| 11 | SC | Почему перестали пользоваться приложением/не начали? | Why did you stop using a finance app, or never start? |

**Раздел 2. Как Вы принимаете финансовые решения / How you make financial decisions**

| # | Тип | RU | EN |
|---|---|---|---|
| 12 | SC* | Как выбираете куда направить деньги? | When you have several options — how do you choose? |
| 13 | MC+O | Используете ли правило для распределения денег? | Do you use any rule for allocating money? |
| 14 | RANK | Приоритет свободных денег в конце месяца (1–5) | In what priority do you use free month-end money? (rank 1–5) |
| 15 | MC | Что случалось из-за отсутствия инструмента? | What has happened because you didn't have a proper tool? |
| 16 | MC+O | К кому/чему обращаетесь за финансовым советом? | When you need advice — what/whom do you turn to? |
| 17 | SC | Следовали ли совету банка/приложения? | If a bank or app gave advice — did you follow it? |
| 18 | MC+O | В каком формате удобнее получать совет? | In what format do you prefer to receive advice? |

**Раздел 3. Конкретный кейс — последняя ситуация выбора / A specific last-choice case**

| # | Тип | RU | EN |
|---|---|---|---|
| 19 | SC | Сколько времени ушло на то решение? | How long did that decision take you? |
| 20 | SCALE* | Насколько уверены что решение оптимально? (1–5) | How confident are you it was optimal? (1–5) |
| 21 | SC | Как часто возникают такие ситуации выбора? | How often do such choice situations arise? |
| 22 | SC | Сколько вариантов обычно сравниваете? | How many options do you usually compare? |
| 23 | SCALE | Как сейчас оцениваете результат? (1–5) | How do you rate its result now? (1–5) |
| 24 | MC+O | Если результат отличался — что повлияло? | If the result differed — what influenced it? |
| 25 | PARA | (Доп.) Расскажите историю подробнее | (Optional) Tell the story in more detail |
| 26 | SC | Кейс: доход $4k, долг, цель — куда $1,500? | Scenario: income $4,000, a loan, a goal — where do $1,500 go? |
| 27 | SC* | На что опирались выбирая ответ? | What did you base that answer on? |

**Раздел 4. Финансовая ситуация / Your financial situation**

| # | Тип | RU | EN |
|---|---|---|---|
| 28 | SC | Что описывает поведение после обязательных платежей? | What describes your behavior after mandatory payments? |
| 29 | SC*+O | По какому принципу откладываете деньги? | On what principle do you set money aside? |
| 30 | SC | Распределяете по «конвертам»/счетам? | Do you split money into "envelopes"/accounts? |
| 31 | SC | На какой срок реально планируете финансы? | How far ahead can you realistically plan? |
| 32 | SC | Есть ли финансовая цель на ближайший год? | Do you have a financial goal for the coming year? |
| 33 | MC (≤3) | Самые важные мотивы сбережений? | Which saving motives are most important? (up to 3) |
| 34 | SC* | Уровень финансовой грамотности? | How would you rate your financial literacy? |
| 35 | SC | Есть ли кредит/рассрочка/долг сейчас? | Do you currently have a loan/installment/debt? |
| 36 | SC | Бывало ли неясно: гасить долг или копить? | Ever unsure whether to repay debt early or save? |
| 37 | MC+O | Какие чувства при мысли о финансах? | What feelings do you have about your finances? |
| 38 | SCALE | Насколько выражена финансовая тревожность? (1–5) | How strong is your finance-related anxiety? (1–5) |
| 39 | SC* | Как часто остаются свободные деньги в конце месяца? | How often is there free money at month-end? |
| 40 | SC | Как часто переживаете забыть обязательный платёж? | How often do you worry about forgetting a payment? |
| 41 | SC | Насколько хватит сбережений при потере дохода? | How long would savings last if you lost income? |

**Раздел 5. Идея инструмента / The tool idea**

| # | Тип | RU | EN |
|---|---|---|---|
| 42 | GRID | Важность критериев (доходность/ликвидность/долг/безопасность) 1–5 | Importance of criteria (yield/liquidity/debt/safety) 1–5 |
| 43 | SC | Был бы полезен инструмент, считающий за Вас? | Would a tool that calculates for you be useful? |
| 44 | MC+O | Что должно быть в таком инструменте? | What should such a tool have? |
| 45 | MC | Что заставит доверять совету помощника? | What would make you trust the assistant's advice? |
| 46 | MC | На каком устройстве/формате удобнее? | On what device/format would it be convenient? |
| 47 | SCALE* | Проверка внимательности — выберите 7 звёзд (1–7) | Attention check — select 7 stars (1–7) |
| 48 | SC | Сколько готовы платить в месяц? | How much would you pay per month? |
| 49 | SC | Какой системе (ИИ / формулы) доверитесь больше? | Which system (AI / formulas) would you trust more? |
| 50 | SC | Что важнее в финансовом советнике? | What's more important in a financial advisor? |
| 51 | GRID* | Доверили бы ИИ задачи? (Да/Нет/Не уверен) | Would you trust an AI with these tasks? (Yes/No/Not sure) |
| 52 | PARA | (Доп.) Опишите идеальный помощник | (Optional) Describe your ideal assistant |

**Раздел 6. О Вас / About you**

| # | Тип | RU | EN |
|---|---|---|---|
| 53 | SC* | Пол | Gender |
| 54 | SC* | Возраст | Age |
| 55 | SC*+O | Образование | Education |
| 56 | SC*+O | Семейное положение | Marital status |
| 57 | MC* | Статус (студент/найм/…) | Status (student/employed/…) |
| 58 | SC | Где живёте? | Where do you live? |
| 59 | SC | Примерный доход в месяц? | Approximate monthly income? |
| 60 | SC | Уровень материального положения | Material situation |

**Раздел 7. Напоследок / Finally**

| # | Тип | RU | EN |
|---|---|---|---|
| 61 | TXT | Email для уведомления о запуске | Email for a launch notification |
| 62 | PARA | (Доп.) Что важного я не спросил? | (Optional) What important thing did I not ask? |

---

## 4. Итог

62 вопроса + 7 секций, типы сохранены 1:1 с оригиналом (34 SC · 17 MC · 3 GRID · 4 SCALE · 1 TXT ·
3 PARA). Синтаксис скрипта проверен. Единственное ручное действие после генерации — при желании
включить «один ответ на столбец» для ранжирования Q14 (ограничение API, см. §2.3).

> **Одной строкой:** вставь `finpilot_survey_en.gs` в `script.google.com` и запусти
> `buildSurveyForm` — получишь готовую англоязычную Google-форму опроса (все 62 вопроса, 7 секций,
> типы 1:1 с оригиналом, мусорные варианты вычищены, валюта — USD с сохранением пропорций кейса);
> сверить перевод можно по таблице RU↔EN выше.
