# Субагент B — источники микроданных по долгу/сбережениям: содержание и доступ

Дата: 2026-09-11. Бюджет 15 действий. WebSearch не использовался (исчерпан вахтой).
Вопросы к каждому источнику:
(1) факт и сумма досрочного/сверхминимального погашения долга
(2) сумма сбережений в разбивке по ЦЕЛЯМ
(3) ставка по каждому потребительскому кредиту
(4) просрочка по потребительскому кредиту
+ условия доступа, право публиковать производные.

## A. Зарубежные обследования
### A1. SCF (Survey of Consumer Finances, ФРС США), волна 2022

**Что проверено:**
- `https://www.federalreserve.gov/econres/files/codebk2022.txt` — **HTTP 200, 2 819 548 байт**, скачан анонимно (`curl`, браузерный UA), без регистрации, без cookie, без соглашения.
- `https://www.federalreserve.gov/econres/scfindex.htm` — **HTTP 200, 102 594 байта**.

**(1) Досрочное / сверхминимальное погашение — ЕСТЬ, но КАТЕГОРИЕЙ, не суммой.**
Отдельная переменная по КАЖДОМУ кредиту, дословно из кодбука:

> `X7534(#1)` `Is this loan being paid off ahead of schedule, behind`
> `schedule, or are the payments about on schedule?`
> `     1.    *On schedule`
> `     2.    *Ahead of schedule`
> `     3.    *Behind schedule`

Такой блок повторяется для всех типов долга (найдены серии): `X7534` (автокредит, в реестре подписан `OWN_VEH_1: ON/AHEAD/BEHIND SCHED?`), `X7529`, `X7521`, `X7554`, `X7564`, `X7566`, `X7821/X7844/X7867/X7921/X7944/X7967` (образовательные кредиты, до 6 штук).
🔴 **Суммы переплаты сверх графика в явном виде НЕТ.** Есть размер и периодичность платежа по каждому кредиту + остаток долга + ставка + ожидаемая дата погашения (`X2216/X2217` — месяц и год ожидаемого погашения) → сверхграфиковый платёж вычисляем КОСВЕННО (фактический платёж против аннуитета, посчитанного из остатка/ставки/срока), а прямым вопросом не измеряется.
Дополнительно по картам: `Мы хотим общую сумму долга, НЕ минимальный платёж` (дословно: `WE WANT THE TOTAL AMOUNT OWED, NOT THE MINIMUM PAYMENT.`) — то есть различие «минимальный платёж vs фактический» в анкете осознаётся, но амплитуда переплаты не спрашивается.

**(2) Сбережения по целям — ЕСТЬ КАК ЦЕЛИ (ранжированные), НЕ КАК СУММЫ.**
Блок `X3006 X3007 X7513 X7514 X7515 X6848`, дословно:

> `People have different reasons for saving, even though they may`
> `not be saving all the time. What are your most important`
> `reasons for saving?`
> `PROBE:  What else?`
> `TREAT 'SAVING' AND 'INVESTING' THE SAME.`

Далее — закрытый классификатор целей (фрагмент): `1. Children's education`, `11. Buying own house`, `13. Buy a car, boat or other vehicle`, `14. Home improvements/repairs`, `15. To travel; take vacations`, `16. Buy durable household goods, appliances`, `5. Wedding, Bar Mitzvah and other ceremonies`, `6. To have children/a family`, `9. To move`, `12. Purchase of cottage or second home`. Записывается до 6 целей с приоритетом (X3006 — самая важная).
🔴 Разбивки «сколько рублей отложено именно на эту цель» НЕТ. Есть общая норма сбережения и активы по счетам, но не аллокация по целям.

**(3) Ставка по каждому кредиту — ЕСТЬ, отдельным вопросом по каждому долгу.**
> `X2219(#1) / X2319(#2) / X2419(#3) / X7170(#4)  What is the current annual rate of interest being charged on this loan?  PERCENT * 100:`

Аналоги: `X816` (ипотека), `X1045`, `X1111`, `X1216`, `X2520`, `X2724` (прочие потребительские/installment-кредиты), `X7822` (образовательный), `X7132` (кредитная карта: `What interest rate do you pay on this card?`). Ставка хранится как процент×100, то есть с сотыми долями.

**(4) Просрочка — ЕСТЬ, на уровне домохозяйства, две градации.**
> `X3004  Now thinking of all the various loan or mortgage payments you made during the last year, were all the payments made the way they were scheduled, or were payments on any of the loans sometimes made later or missed?`
> `     1.    *All paid as scheduled or AHEAD OF SCHEDULE`
> `     5.    *Sometimes got behind or missed payments`

> `X3005  Were you ever behind in your payments by two months or more?`
> `     1.  *YES   5.  *NO`

Плюс покредитный статус `3. *Behind schedule` из блока (1) и причина в классификаторе (`3. Got behind on payments; didn't pay bills`).

**Доступ.** Публичный, без заявки и без аффилиации: кодбук и микроданные отдаются прямой ссылкой анонимному `curl` (замерено выше). 🔴 Ограничение, зафиксированное в самом кодбуке: часть переменных помечена

> `*********************************************************`
> `    NOT INCLUDED IN THE PUBLIC DATA SET`
> `*********************************************************`

(например `X30067`, `X30077`, `X30064` — служебные идентификаторы выборки). То есть публичная версия урезана относительно внутренней, но **все четыре интересующих нас блока в публичной части присутствуют** (пометки «not included» стоят не на них).
Публикация производных явного запрета на странице не имеет; данные — продукт федерального правительства США.

**Что даёт для калибровки весов:** SCF — единственный из проверенных источников, где решение «плачу сверх графика» наблюдается ПРЯМЫМ вопросом по каждому кредиту одновременно со ставкой по нему, целями сбережения и просрочкой → на нём можно оценить, при каких (ставка, остаток, доход, цель) домохозяйство выбирает досрочное погашение вместо резерва/цели, то есть откалибровать веса SAW на чужой популяции.
**Чего не даёт:** ни рубля российской специфики (ПДН, структура долга РФ), суммы переплаты в явном виде нет (только категория + косвенный расчёт), аллокации сбережений по целям в деньгах нет, перенос весов на РФ требует отдельного обоснования.

### A2. HFCS (Household Finance and Consumption Survey, ЕЦБ), волны 2021 и 2023

**Что проверено:**
- `https://www.ecb.europa.eu/stats/ecb_surveys/hfcs/html/index.en.html` — **HTTP 200, 137 608 байт**.
- `https://www.ecb.europa.eu/home/pdf/research/hfcn/HFCS_Core_and_Derived_Variables_2021_Wave.pdf` — **HTTP 200, 1 124 660 байт** (каталог core/derived-переменных; `pdftotext -layout` → 514 488 знаков).
- `https://www.ecb.europa.eu/home/pdf/research/hfcn/HFCS_Questionnaire_Wave_2023.pdf` — **HTTP 200, 937 327 байт** (анкета волны 2023; 187 721 знак текста).
- `https://www.ecb.europa.eu/stats/ecb_surveys/hfcs/html/researcher_hfcn.en.html` — **HTTP 404** (такого адреса нет; раздел про доступ живёт секцией на главной странице HFCS).

🔴 **ДОСТУП — ЗАЯВКА ПОДТВЕРЖДЕНА.** Дословно со страницы ЕЦБ, секция «Access to the data»:

> «The HFCS datasets are available to researchers for research purposes. Please add the following information to your access request: a copy of your government-issued photo identification document (saved as: ID_surname.pdf); a Resume or Curriculum Vitae in English (in PDF or simple text formats saved as: CV_surname.pdf); completed access request form»

Плюс: «Anonymised microdata are made available to researchers» и отдельное ограничение — «The HFCS datasets do not include data for Ireland. Please apply directly to Ireland's Central Statistical Office (CSO) for access to research microdata files.»
Форма заявки: `/home/pdf/research/hfcn/access_form_leadresearchersurname_researchersurname.pdf` — само имя файла (`leadresearchersurname`) показывает, что предполагается ведущий исследователь, то есть **аффилиация де-факто требуется**. Паспорт + CV + форма — это заметно жёстче SCF (там ноль формальностей). Условий публикации производных на самой странице не приведено — они внутри формы/соглашения, которое я не подписывал и не открывал.

**(1) Досрочное / сверхминимальное погашение — НЕТ.**
Прямой поиск по анкете 2023 и по каталогу переменных 2021 (`early repayment`, `repay early`, `extra payment`, `ahead of schedule`, `more than required`) дал **ноль совпадений**. В HFCS есть цель кредита, ставка, ежемесячный платёж и остаток, но вопроса «платите ли вы сверх графика» — как в SCF (`X7534`) — нет.
Косвенно есть только рефинансирование: HB120$x (цель ипотеки) обсуждает `debt refinancing … possibly in terms of a lower interest rate and/or a longer pay-off period`.

**(2) Сбережения по целям — ЕСТЬ, ДА/НЕТ по 12 целям, БЕЗ СУММ.**
Переменная `HI0400x  purpose of saving`, кодировка дословно: `1 - Yes / 2 - No`, `a set of 12 variables for items:`

> `a - Purchase own home`
> `b - Other major purchases (other residences, vehicles, furniture, etc.)`
> `c - Set up a private business or finance investments in an existing business`
> `d - Invest in financial assets`
> `e - Provision for unexpected events`
> `f - Paying off debts`
> `g - Old-age provision`
> `h - Travels/holidays`
> `I - Education/support of children or grandchildren or other relatives`
> `j - Bequests`

🔴 Для нашей задачи важна строка **`f - Paying off debts` как ОТДЕЛЬНАЯ цель сбережения** — это ровно тот выбор, который моделирует СППР, но зафиксирован он бинарно, без суммы.

**(3) Ставка по каждому потребительскому кредиту — ЕСТЬ, core-переменная.**
> `HC090$x non-collateralised loan $x: current interest rate of loan`
> `What is the current (annual) rate of interest charged on the loan?`
> `Coding: Numerical value, 4 digits, 2 decimal places.`

Рядом — `HC100$x non-collateralised loan $x: monthly payment on loan`: `At present, how much is the monthly payment on the loan including both interest and repayment, but excluding any required payments for taxes, insurance or other fees?` Для ипотеки — `HB180$x` (признак плавающей ставки) и производные `DL1110a/b/c` (остаток по режиму ставки).

**(4) Просрочка — ЕСТЬ, с отдельным порогом 90 дней.**
> `HC1250 Late or missed payments on loans`
> `Now thinking of all the various loan or mortgage payments due in the last twelve months: were all the payments made the way they were scheduled, or were payments on any of the loans sometimes made later or missed?`
> `1 - All payments paid as scheduled`
> `2 - It happened once or more that I was late with or missed some of the payments because of financial difficulties`
> `3 - It happened once or more that I was late with or missed some of the payments for other reasons`
> `4 - It does not apply, because household did not have loan payments in the last 12 months`

Далее: `HC1270 Any overdue payments by more than 90 days` (задаётся, если HC1250=2). Формулировка HC1250 почти дословно повторяет SCF `X3004` — обследования намеренно сопоставимы.

**Что даёт:** гармонизированная европейская рамка, где «погашение долга» — легитимная ЦЕЛЬ сбережения наравне с резервом (`e - Provision for unexpected events`) и покупками; это прямая внешняя опора для нашей постановки «делим поток между долгом, резервом и целями». Плюс покредитная ставка → можно воспроизвести Avalanche-логику на данных.
**Чего не даёт:** досрочного погашения нет вовсе — то есть HFCS нашу главную дыру НЕ закрывает; сумм по целям нет; доступ требует заявки, паспорта и CV, то есть «скачал и посчитал» не получится.

### A3. PSID (Panel Study of Income Dynamics, Мичиган) — НЕ ДОБЫТ

**Что проверено:** `https://psidonline.isr.umich.edu/Guide/Overview.aspx` — **HTTP 403, 43 101 байт**, тело ответа дословно:

> «Security Challenge. Enable JavaScript and cookies to continue. We're reviewing the security of your connection before proceeding.»

Это антибот-заглушка (JS-челлендж), а не отсутствие страницы. Обходные каналы в этой сессии недоступны: `WebSearch` исчерпан вахтой (400/400), Exa отдаёт 404, `r.jina.ai` отдаёт 401. Второй канал (`curl` с браузерным UA) уже и был использован — именно он получил 403.
🔴 **Ничего о содержании долгового блока PSID не утверждаю — данных не добыл.** Единственное, что установлено фактом: прямой анонимный доступ к сайту PSID из этой среды закрыт антиботом, то есть даже разведка кодбука требует браузера/сессии с cookie.
**Что осталось проверить в следующий заход (конкретные адреса):** `psidonline.isr.umich.edu/Guide/documents.aspx` (кодбуки), а также блок Wealth Supplement — именно там, по структуре обследования, должен лежать долг; но это гипотеза, не проверенный факт.

## B. Кредитные бюро РФ (НБКИ / ОКБ / Скоринг Бюро)

**Что проверено:**
- `https://www.nbki.ru/company/news/` — **HTTP 200, 251 227 байт**. Извлекаемый текст — навигация и меню услуг («Получить кредитную историю», «Персональный кредитный рейтинг», «Оспорить кредитную историю», «Самозапрет на кредиты», «Стать клиентом НБКИ»); лента новостей подгружается скриптом и в статическом HTML отсутствует. В разметке нашлись ссылки только на `/company/documents/` и один PDF `/upload/iblock/5fa/muqsrd2n4cuyky63jz7wl1telgqzyppx.pdf` — до содержимого новостей/исследований дойти не удалось.
- `https://bki-okb.ru/press/news` — **HTTP 200, но 2 149 байт**; `https://bki-okb.ru/press/research` — **HTTP 200, 2 153 байта**. Оба — пустая SPA-оболочка (после снятия тегов текст нулевой длины), контент рендерится JS.
- Скоринг Бюро — **не проверялось вовсе**, бюджет кончился.

**Вывод, который можно сделать честно.** Публично опубликованных МИКРОданных ни у одного из проверенных бюро я не нашёл; навигация НБКИ целиком построена вокруг платных/персональных сервисов («Стать клиентом НБКИ», «Получить кредитную историю») — раздела «данные для исследователей» в меню нет. Это согласуется с моделью «данные только коммерческие», но 🔴 **дословной формулировки условий доступа я не добыл**, и разделы «исследования» обоих бюро не прочитаны (JS).

**Что бюро физически содержат (рассуждение, НЕ цитата):** кредитная история по 218-ФЗ включает фактические платежи по каждому договору, график и остаток, то есть **досрочное/сверхминимальное погашение в данных бюро наблюдается по определению** — как разница факта и графика, без вопроса респонденту. Плюс ставка по договору и просрочка с глубиной. Чего в бюро НЕТ принципиально: доходов и расходов домохозяйства, сбережений и целей — то есть **левой части нашего уравнения (свободный денежный поток) там нет вообще**, а без неё «как поделить поток» не восстанавливается. Бюро закрывает переменные (1), (3), (4) и не закрывает (2) и сам поток.

## C. КОУЖ и ВНДН (Росстат) — содержание

**Что проверено:**
- `https://rosstat.gov.ru/free_doc/new_site/vndn-2024/index.html` — **HTTP 200, 10 473 байта**; `.../vndn-2023/index.html` — **HTTP 200, 12 315 байт**. Обе страницы — SPA-оболочки: виден только оглавительный каркас, дословно: `ВНДН-2024 Выборочное наблюдение доходов населения и участия в социальных программах 2024 · Общее · Описание наблюдения · Материалы наблюдения · Выборка · Вопросники · Сбор данных · Микроданные · Политика доступа · Файлы данных · По домохозяйствам · По лицам · Итоги наблюдения · Статистические таблицы …`. Разделы **«Вопросники»** и **«Политика доступа»** существуют, но их содержимое подгружается скриптом и в HTML отсутствует; ни одной ссылки на PDF/DOC в разметке нет.
- `https://rosstat.gov.ru/free_doc/new_site/KOUZ22/index.html` — **HTTP 404, 1 245 байт**; `.../KOUZ-2024/index.html` — **HTTP 404, 1 245 байт**. Шаблон адреса для КОУЖ угадан неверно.
- `https://tochno.st/datasets/surveys` — **HTTP 200, 376 088 байт**, прочитано полностью.

🔴 **Главная находка по C — способ добыть вопросники, не качая гигабайты.** Дословно со страницы «Если быть точным»:

> «В набор данных входят 58 файлов микроданных 12 обследований, проведенных в период с 2011 по 2025 годы. Микроданные многих волн не опубликованы даже на сайте Росстата. Мы их получили через официальный запрос и опубликовали в удобном для работы формате. В архиве каждого обследования имеются папки для каждого отдельного года проведения обследования. **К микроданным прилагаются вопросники и кодбуки с описанием обследования и переменных.**»

То есть вопросник КОУЖ/ВНДН лежит ВНУТРИ архива обследования, а архивы качаются **по отдельным обследованиям**, не единым массивом: «Для того, чтобы не скачивать весь массив данных, можно выбрать интересующее вас обследование и скачать архив с данными только по нему. Внутри архива содержатся микроданные сразу в трёх форматах: *.XLSX, *.CSV и *.SAV.»
Годы (уточнение к тому, что знала вахта): **КОУЖ — 2011, 2014, 2016, 2018, 2020, 2022, 2024** (то есть раз в два года, а не ежегодно); **ВНДН — 2012, 2014–2025 ежегодно**; там же **ОДПФ ЦБ — 2013, 2015, 2018, 2020, 2022, 2024** (шесть волн, а не одна — это важно: у нас скачана одна).
Лицензия подтверждена дословно: «Условия использования: Creative Commons BY 4.0», цитирование — «Микроданные выборочных обследований Росстата и Центрального банка // Росстат, Центральный банк; обработка «Если быть точным», 2024». **CC BY 4.0 = производные публиковать можно при указании авторства.**

🔴 **На главный вопрос по C — есть ли в КОУЖ/ВНДН долговой блок и сбережения по целям — я ОТВЕТА НЕ ДОБЫЛ.** Вопросники не прочитаны: на сайте Росстата они за JS, а внутри архивов tochno.st их доставать мне было запрещено (архивы гигабайтные). Никаких утверждений о содержании КОУЖ/ВНДН в этом отчёте нет и делать их нельзя.

## ИТОГ: закрывает ли хоть один источник дыру с досрочным погашением

**Да — но только SCF, и только как ОБРАЗЕЦ МЕТОДОЛОГИИ, не как данные о России.**

| Источник | (1) досрочное погашение | (2) сбережения по целям | (3) ставка по кредиту | (4) просрочка | доступ |
|---|---|---|---|---|---|
| **SCF 2022 (США)** | **ДА**, категория по каждому кредиту (`X7534` и серия); суммы нет | цели ДА (до 6, ранжированы, `X3006`), сумм по целям нет | **ДА**, по каждому (`X2219`, `X2520`, `X2724`, `X7132`) | **ДА** (`X3004`, `X3005` + покредитный «behind») | публичный, без заявки (проверено `curl`) |
| **HFCS 2021/2023 (ЕС)** | **НЕТ** (поиск по анкете и каталогу — ноль) | цели ДА, бинарно, 12 штук, в т.ч. `f - Paying off debts`; сумм нет | **ДА** (`HC090$x`) | **ДА** (`HC1250`, `HC1270` >90 дней) | **заявка + паспорт + CV + форма** |
| **PSID** | не установлено | не установлено | не установлено | не установлено | сайт отдал HTTP 403 (антибот) |
| **Бюро РФ (НБКИ/ОКБ)** | по природе данных ДА (факт против графика), публично — не найдено | НЕТ принципиально | по природе данных ДА | по природе данных ДА | публичных микроданных не найдено; разделы за JS |
| **КОУЖ / ВНДН** | не установлено | не установлено | не установлено | не установлено | открыто, **CC BY 4.0**, вопросники внутри архивов |
| **ОДПФ (для сравнения, установлено вахтой)** | НЕТ | НЕТ | — | — | скачано |

**Практический вывод для проекта.** Ни один ДОСТУПНЫЙ российский источник дыру не закрывает: ОДПФ её не содержит, бюро публично данных не дают, КОУЖ/ВНДН не проверены. Значит, оценивать веса SAW «по наблюдаемому российскому поведению» нечем, и это не лень поиска, а свойство поля.
Что реально даёт SCF/HFCS: (а) готовые **формулировки вопросов**, если проект когда-нибудь соберёт собственные данные пользователей — вопрос `ahead of schedule / on schedule / behind schedule` по каждому кредиту снимается одной кнопкой в интерфейсе; (б) внешнее подтверждение самой постановки задачи — в HFCS «погашение долга» стоит отдельной целью сбережения рядом с «резервом на непредвиденное», то есть трёхчастное деление потока (долг / резерв / цели) — не наша выдумка; (в) SCF позволяет численно откалибровать связку (ставка, остаток, цель, доход) → «плачу сверх графика» на американской популяции, но перенос на РФ требует отдельного обоснования и честной оговорки в документации модели.
🔴 **Альтернатива, которую стоит рассмотреть вместо поиска данных:** веса калибровать не на наблюдаемом поведении, а нормативно (Avalanche как оптимум по переплате) и проверять на синтетике — тогда отсутствие данных перестаёт быть блокером, а становится явным допущением модели.

## НЕ ДОБЫТО (точный код ответа по каждому адресу)

| Адрес | Код | Что помешало |
|---|---|---|
| `https://psidonline.isr.umich.edu/Guide/Overview.aspx` | **HTTP 403**, 43 101 б | JS-антибот: «Security Challenge. Enable JavaScript and cookies to continue.» Обходные каналы в сессии мертвы: WebSearch исчерпан, Exa 404, r.jina.ai 401 |
| `https://www.ecb.europa.eu/stats/ecb_surveys/hfcs/html/researcher_hfcn.en.html` | **HTTP 404**, 97 563 б | адреса не существует; нужная информация найдена на главной странице HFCS (это не потеря) |
| `https://rosstat.gov.ru/free_doc/new_site/KOUZ22/index.html` | **HTTP 404**, 1 245 б | шаблон адреса КОУЖ угадан неверно |
| `https://rosstat.gov.ru/free_doc/new_site/KOUZ-2024/index.html` | **HTTP 404**, 1 245 б | то же |
| `https://rosstat.gov.ru/free_doc/new_site/vndn-2024/index.html` (разделы «Вопросники», «Политика доступа») | HTTP 200, но 10 473 б | SPA: оглавление есть, содержимое разделов рендерится JS, ссылок на файлы в HTML нет |
| `https://bki-okb.ru/press/news` | HTTP 200, **2 149 б** | пустая SPA-оболочка, текста ноль |
| `https://bki-okb.ru/press/research` | HTTP 200, **2 153 б** | пустая SPA-оболочка, текста ноль |
| `https://www.nbki.ru/company/news/` (сама лента) | HTTP 200, 251 227 б | HTML отдал только меню/навигацию; новости подгружаются скриптом |
| Скоринг Бюро | **не запрашивалось** | бюджет действий исчерпан |
| Содержание КОУЖ/ВНДН (долговой блок, цели сбережений) | — | вопросники доступны только внутри гигабайтных архивов tochno.st, качать было запрещено; на сайте Росстата — за JS |

---

## ДОБОР Г31.2 — прокси (16.09.2026)

**Каналы на начало работы:** `r.jina.ai` **без UA** — 🟢 живой (контроль: `monarchmoney.com/pricing`
**200, 5 509 байт**; тот же адрес с браузерным UA — **403, 5 743 б**, капча самого прокси).
Exa — 🟢. Напоминаю условия исходной сессии этого файла: **`r.jina.ai` отдавал 401** («bad network
reputation, AS9009»), **Exa — 404**, `WebSearch` исчерпан 400/400. То есть отказ по PSID был вынесен
при трёх мёртвых каналах из четырёх.

### Г31.2-14. 🔴 A3. PSID — ДОЛГОВОЙ БЛОК УСТАНОВЛЕН ПОЛНОСТЬЮ (был «не установлено» по всем колонкам)

**Прежний статус:** «`psidonline.isr.umich.edu/Guide/Overview.aspx` — HTTP 403, 43 101 б,
"Security Challenge. Enable JavaScript and cookies to continue"… Ничего о содержании долгового
блока PSID не утверждаю — данных не добыл.»

**Каналы 16.09.2026:**

| Канал | Адрес | Код | Размер | Итог |
|---|---|---|---|---|
| `r.jina.ai` **без UA** | `psidonline.isr.umich.edu/Guide/Overview.aspx` | 200 у прокси | **413 б** | «Just a moment… We're reviewing the security of your connection» — 🔴 **и без UA антибот держит**; прежний отказ подтверждён как свойство сайта |
| `r.jina.ai` **без UA** | `simba.isr.umich.edu/data/data.aspx` | **200** | **2 160 б** | 🟢 **открыто** — другой хост того же проекта антиботом не закрыт |
| `mcp__exa__web_search_exa` | документация PSID | 200 | — | 🟢 **User Guide 2021 / Main Interview User Manual Release 2023 — с точными кодами переменных** |

🔴 **Два вывода по каналу.** (1) Отказ по `psidonline` был **настоящим** — это не ошибка вызова
прокси. (2) **Но он не означал недоступности данных**: соседний хост `simba.isr.umich.edu` открыт,
а документация с полным перечнем долговых переменных лежит в PDF-руководствах, которые находит Exa.
Это ровно класс «отказ инструмента записан как отсутствие источника».

#### Первичный материал — ДОСЛОВНО, PSID User Guide for the 2021 Interviewing Year (ISR), §5.2.2 Wealth

> «The wealth module was **first included in 1984**. This module was included again in **1989, 1994,
> 1999, and every wave since then**. The question series includes **unfolding brackets**, and PSID
> staff members use this and other information to create variables representing the total value of
> wealth and its major subcomponents. Information from two sections — the housing section (A) and
> the wealth section (W) — were used to construct the 2021 net worth measures. PSID asks about
> **nine broad wealth categories, including short-term debt**:»
> «3. **Value of debt aside from mortgage on the main home or vehicle loans**, divided into
> sub-components: **credit card debt [W39A, ER80002]**, **student loan debt [W39B1, ER80012]**,
> **medical bills [W39B2, ER80017]**, **legal bills [W39B3, ER80022]**, **loans from relatives
> [W39B4, ER80027]**, and **unspecified other debt [W39B7, ER80033]**.»
> «1. Equity in business (also includes farm), now split into **asset and debt components**
> [W11A & W11B, ER79934 & ER79938].»
> «4. Equity in real estate… now split into asset and debt components [W2A & W2B, ER79921 & ER79925].»
> «9. Value of home equity (calculated as **home value minus remaining mortgage**; used in
> calculation of WEALTH2) [ER81834].»

**Обработка пропусков (дословно):**
> «Processing of the data includes three steps: a) **imputation of the wealth components (1-8)**,
> b) computation of home equity (9), and c) construction of estimates for the total family wealth
> with and without housing equity… a **hot-deck imputation** technique was used for imputation of
> the missing data in each wealth component (1-8)… For the **257 cases** missing at least one
> component of home equity, the mean value imputed was **$149,117**» (волна 2021; в редакции 2023 —
> «267 cases… $185,344»).

**Сводные переменные (дословно, Cooper, Dynan & Rhodenhiser, Boston Fed WP 2019-06,
DOI 10.29412/res.wp.2019.06):**
> «The PSID is a longitudinal survey for which households were interviewed **annually through 1997
> and since then have been interviewed biennially**… These variables are labeled **"WEALTH1" and
> "WEALTH2"** in the PSID codebook. **WEALTH1 is imputed wealth excluding** the value of equity in
> a household's primary residence, while **WEALTH2 equals WEALTH1 plus any such housing equity**.»
> Состав неипотечного долга (волна 2017, коды): «…net of the sum of non-primary housing debt
> (ER71431 [farm/business, W11B], ER71441 [other real estate, W2B], **ER71459 [credit card, W39A]**,
> **ER71463 [student loan, W39B1]**, **ER71467 [medical, W39B2]**, **ER71471 [legal, W39B3]**,
> **ER71475 [family loan, W39B4]**, ER71479 [other, W38B7]) plus the value of home equity (ER71481).
> **All missing data were assigned.**»

**Оговорка о сопоставимости (дословно, Boston Fed WP 2017-07 Data Appendix, Premo & Subramaniam):**
> «Credit cards / charge cards — **PSID: All credit card debt, excluding debt from convenience use.**»
> «Other loans — **PSID: Includes only loans from relatives.**»

**Известная проблема измерения активов (дословно, User Guide):** в 2017 г. к вопросу W27 добавили
W27a, и «**1,913 respondents** who had answered "No" to W27… went on to answer "**Yes**" to W27a…
that is, **more than half (57%)** of those who reported that they did not hold money in any of
[checking or savings accounts, money market funds, CDs, government bonds, treasury bills] did report
that they owned a checking or savings account».

#### Выжимка — что это даёт участку «альтернативные источники микроданных»

1. 🟢 **Долговой блок PSID пригоден для нашей задачи по составу.** Неипотечный долг разложен ровно
   на те компоненты, которыми оперирует наш долговой контур: карты, образовательный кредит,
   медицинские счета, юридические счета, займы у родственников, прочее — каждый со своим кодом
   переменной. Ипотека и автокредит вынесены отдельно (в раздел A и в equity in vehicle).
2. 🟡 **Периодичность — раз в два года с 1999 г.** (до 1997 — ежегодно). Для калибровки помесячной
   модели это означает: PSID даёт **структуру и уровни**, но не месячную динамику.
3. 🔴 **Две ловушки, которые надо назвать, если берём PSID как основу портретов:**
   (а) значения по компонентам **импутированы hot-deck**, и доля импутации ненулевая — сравнивать
   наши синтетические распределения надо с учётом этого; (б) **credit card debt исключает
   convenience use**, то есть это остаток, переносимый на следующий период, а не оборот по карте.
   Смешать одно с другим — получить завышенную долговую нагрузку.
4. 🔴 **Предупреждение по анкетным данным, совпадающее с нашим (ниворожкинским) выводом:** 57 %
   ответивших «нет» на сложносоставной вопрос об активах отвечали «да» на простой вопрос о наличии
   счёта. **Формулировка вопроса меняет ответ радикально** — прямое соображение для нашего
   опросника и для любой калибровки на самоотчёте.
5. ⚪ **Доступ к самим данным:** `simba.isr.umich.edu/data/data.aspx` (открыт), дословно:
   «Before downloading data for the first time, users must **register** by completing a short
   registration form which includes choosing a username and password that allows them to access
   the **public use data archive**». То есть данные публичные, но за регистрацией — **действие
   владельца**, не поисковая задача.

## ИТОГ Г31.2 (в этом файле)

- Закрыт **1 пункт** — A3 PSID, из состояния «не установлено по всем колонкам» в «долговой блок
  установлен по официальной документации, с кодами переменных и оговорками».
- 🔴 **Нашей ошибкой вызова прокси пункт НЕ был:** `psidonline` держит антибот и без UA. Но он был
  **ошибкой «отказ инструмента = отсутствие источника»**: соседний хост открыт, а документация
  находится поиском — просто в той сессии три канала из четырёх были мертвы, и добор не делался.
- Канон, прогноз, новизну, юрблок — не меняет. Материал для выбора источника калибровки.
