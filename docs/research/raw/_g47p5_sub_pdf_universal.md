# Г47 П5.2 — универсальный разбор PDF-выписки банка без шаблона (сырьё, дословно/по фактам)

Статус: ЗАВЕРШЕНО (в рамках бюджета одного подагента, без вложенных подагентов).
Дата: 2026-09-17. Каналы: mcp__exa__web_search_exa, mcp__exa__web_fetch_exa (≈16 добывающих
вызовов из бюджета 30; WebSearch/WebFetch не понадобились — Exa отработала стабильно).

## 1. Восстановление таблицы по координатам символов

**Класс: документация библиотеки + баг-трекер (не научная статья).**

- **pdfplumber** (`jsvine/pdfplumber`, MIT, GitHub) — `TableFinder` (файл `pdfplumber/table.py`)
  дословно в коде: *«Largely borrowed from Anssi Nurminen's master's thesis... and inspired by
  Tabula»*. Параметры `vertical_strategy`/`horizontal_strategy` = `lines`/`lines_strict`/`text`/`explicit`;
  `snap_tolerance` — «параллельные линии в пределах snap_tolerance склеиваются в одну позицию»;
  `join_tolerance` — сегменты на одной бесконечной прямой с концами ближе join_tolerance
  объединяются; `intersection_tolerance` — ортогональные края в пределах допуска считаются
  пересекающимися; `min_words_vertical`/`min_words_horizontal` — для стратегии `text` нужно
  минимум столько слов с общим выравниванием, чтобы признать линию колонки.
  Источник: https://github.com/jsvine/pdfplumber (README, table.py, test_table.py).
- **Что ломается по факту из issue/discussion pdfplumber (#448, tests):** без явных линий
  (`vertical_strategy: text`) алгоритм путает лишние столбцы, склеенный текст типа "Sector Region"
  не режется на 2 колонки без `explicit_vertical_lines`; для многострочных ячеек и заголовков,
  выровненных по правому краю (числа), автор pdfplumber прямо пишет: *«Text-based vertical
  separators are a challenging problem as it is very difficult to make them work for all the
  tables»* — рекомендованный обход: взять x-координаты заголовков и передать их как
  `explicit_vertical_lines`.
- **PyMuPDF vs pdfplumber vs Camelot vs Tabula, замер на РЕАЛЬНОЙ выписке банка** (класс: блог
  инженера, не рецензируемая публикация, но с числами и датой 2026-05-24):
  5-страничная цифровая выписка, 250 строк транзакций, колонки разделены пробелами, без линий.
  Результат (dev.to, «Tabula vs Camelot vs pdfplumber in 2026»):
  Tabula(stream) 247/250 строк (3 длинных описания слились со следующей строкой);
  Camelot(lattice) 0/250 (нет линий — неверный режим для этого документа);
  Camelot(stream) 238/250 (12 строк с описанием >~60 символов потеряны);
  pdfplumber(default) 241/250 (9 строк пропущены из-за допуска колонки);
  pdfplumber(tuned) 250/250, но потребовалось ~20 минут ручной подстройки `table_settings`.
  Источник: https://dev.to/martin_pdfexcel/tabula-vs-camelot-vs-pdfplumber-in-2026-which-python-library-actually-wins-22kn
  🔴 Это единственный найденный замер именно на банковской выписке, а не на счетах/научных
  таблицах — держать в уме, что это блог, не пер-ревью.
- Что конкретно ломает разбор по координатам (сведено из pdfplumber issues + Camelot wiki):
  многострочные ячейки (описание транзакции переносится на 2 строки — парсер видит 2 строки
  таблицы вместо одной); слитые колонки при `vertical_strategy=text` без явных линий (напр.
  "CENTRAL KMA" в одной ячейке при отсутствии разделителя); отсутствие линий-разделителей вообще
  (Camelot lattice даёт 0 таблиц); повёрнутые страницы (Camelot wiki: `rotated.pdf` — у pdfplumber
  «output unusable», у pdf-table-extract тоже); лигатуры/пробелы внутри чисел ломают
  `extract_words` (числа "1 234,56" распадаются на разные "слова" без ручного склеивания через
  x_tolerance).

## 2. Кластеризация x-координат / поиск колонок без шаблона

**Класс: научные статьи (классика document layout analysis) + магистерская диссертация + код.**

- **Nagy & Seth (1984)** — «Hierarchical representation of optically scanned documents»,
  Likarska sprava, 1984, (8):29-35 — первая формулировка X-Y tree decomposition для разметки
  страницы (рекурсивное деление на прямоугольники чередующимися горизонтальными/вертикальными
  разрезами). Класс: научная статья (базовая, без прямых числовых замеров).
- **Ha, Haralick & Phillips (1995)**, «Recursive X-Y cut using bounding boxes of connected
  components», Proc. 3rd ICDAR, pp. 952-955, DOI 10.1109/icdar.1995.602059 — классическая
  реализация X-Y cut через bounding boxes связных компонент вместо пиксельного анализа,
  на Sparc-10 сегментация страницы 300 dpi занимает ~1 секунду. Алгоритм: расчёт проекционных
  профилей (horizontal/vertical projection) → разрез в самой широкой "долине" (valley) профиля,
  превышающей порог V_thr, привязанный к размеру доминирующего шрифта → рекурсия, пока разрезы
  возможны. Полный текст (PDF): https://www.haralick.org/conferences/71280952.pdf
- **Hu, Kashi, Lopresti & Wilfong**, «Table Structure Recognition and Its Evaluation», SPIE
  Document Recognition and Retrieval VIII, San Jose, 2001 — упомянута как ref [5] в связанной
  статье; в ней впервые «hierarchical clustering использовалась для идентификации колонок, затем
  spatial+lexical критерии — для классификации заголовков» (цитата из вторичного источника,
  прямой PDF не добыт в этом проходе — см. «Недобытое»).
- **Coarse-to-fine table detection (Wang/Haralick group, ~2000-2001)** — «Automatic Table Ground
  Truth Generation and A Background-analysis-based Table Structure Extraction Method»
  (haralick.org/conferences/12630528.pdf, класс: научная статья, есть числовой замер):
  на 1125 страниц документов с 518 таблицами и 10941 ячейками — **~90% cell correct detection
  rate**. Метод: сначала находят большие горизонтальные "пустые блоки" (large horizontal blank
  blocks) как кандидаты в таблицы → статистическая проверка (3 признака: доля площади больших
  вертикальных пустых блоков к площади таблицы и т.п.) → внутри таблицы делают **вертикальную
  проекцию на уровне слов** — пики и "долины" проекции размечают границы колонок (это и есть
  прямой пример «определения колонок по гистограмме пробелов» из вопроса).
- **M-XY tree / PDF-TREX-предшественник, Firenze (ICDAR'99)** — расширение X-Y tree для счетов
  (invoices): разрезы не только по пробелам, но и по линиям-разделителям; пороги (какой разрыв
  считать разрезом) вычисляются от среднего размера символа страницы (`Ch`, `Cw`), не фиксированы.
  Источник: https://flore.unifi.it/retrieve/e398c37e-85c4-179a-e053-3705fe0a4cff/ICDAR99a.pdf
  (класс: научная статья).
- **Nurminen (2013), Тампере (TUT), магистерская диссертация "Algorithmic Extraction of Data in
  Tables in PDF Documents"** — https://trepo.tuni.fi/handle/123456789/21520 (21 цитирование).
  🔴 ПОДТВЕРЖДЕНО дословно в исходном коде и Tabula, и pdfplumber: `pdfplumber/table.py` содержит
  комментарий *«Largely borrowed from Anssi Nurminen's master's thesis... and inspired by
  Tabula»*; в `tabula-java` алгоритм называется `NurminenDetectionAlgorithm.java`
  (github.com/tabulapdf/tabula-java). Метод (из обсуждения issue tabula-extractor #16, псевдокод
  автора): найти все пересечения линий (crossing-points), отсортировать сверху вниз/слева
  направо, для каждой точки искать другие точки пересечения строго ниже/правее по той же
  вертикали/горизонтали и проверять существование ребра между ними → если все 4 стороны
  подтверждены, фиксируется прямоугольник-ячейка. Отдельно (`calculateExtendedEdges` /
  `TextEdges` в NurminenDetectionAlgorithm.java) — определение колонок по **текстовым краям**:
  для каждого текстового фрагмента строки считаются left/mid/right x-координаты и накапливаются
  в карту `Map<Integer, List<TextChunk>>`; когда число текстовых фрагментов, разделяющих одну и
  ту же x-координату (`REQUIRED_TEXT_LINES_FOR_EDGE`), достаточно велико — это и есть «колонка без
  явных линий», найденная методом группировки одинаковых x-координат (де-факто 1D кластеризация
  по значению координаты, не по расстоянию/DBSCAN, а по точному совпадению после округления
  `Math.floor`).
- Явных публикаций/замеров именно с DBSCAN/иерархической кластеризацией x-координат ЛЕВЫХ краёв
  слов (в смысле scikit-learn стиля алгоритмов) под table-detection в этом проходе НЕ найдено —
  индустриальный код (Tabula/pdfplumber) использует не ML-кластеризацию, а **точное совпадение
  округлённых координат + порог "минимум N строк на одном крае"**, что эквивалентно
  1D-кластеризации с фиксированным допуском (`snap_tolerance`/`join_tolerance` у pdfplumber,
  `CELL_CORNER_DISTANCE_MAXIMUM` у Tabula-java), но без вероятностной модели.
- **pdf2table (Yildiz), PDF-TREX (Oro & Ruffolo), T-Recs (Kieninger)** — 🔴 не добыты дословно в
  этом проходе (см. «Недобытое»); упоминаются как классика в связанных статьях по X-Y cut,
  но полный текст/абстракт не получен через доступные каналы за отведённые попытки.

## 3. Распознавание семантики колонок по содержимому

**Класс: открытый код (несколько независимых проектов) + блог инженера + научная статья (LLM-based,
для контраста «с обучением» против «без обучения»).**

- **PennyRush (класс: блог инженера, dev.to, 2026-09-13)** — прямой пример нетренируемой типизации:
  *«it hunts for the header row instead of assuming row zero. It scores each line on whether it
  contains a date-like column, a money-like column (amount, debit, credit, withdrawal, deposit),
  and a description-like column (narration, particulars, payee, memo, and so on). Banks all name
  these differently, so the matching is fuzzy on purpose»*. Дальше — обработка знака: *«handles the
  amount-versus-separate-debit-and-credit case (a debit becomes a negative amount, a credit stays
  positive)»*; парсинг сумм переживает валютные символы, разделители тысяч, `Rs.`/`INR`/`USD`,
  скобки как отрицательное число (бухгалтерская нотация). Источник:
  https://dev.to/royalpinto007/parsing-bank-statements-in-memory-keep-the-fields-store-nothing-else-1hj5
- **rbrtjns90/statement_organizer** (🔴 лицензия **GPL v3.0** — стоп для закрытого продукта FINPILOT,
  можно использовать как референс метода, не как код) — `geometry_extractor.py` содержит
  описанный в README приём: *«transaction amounts right-align at fixed x-coordinates per bank. The
  extractor clusters word positions to detect columns — far more reliable than line-based regex»*.
  Это прямой пример использования **выравнивания** (числа по правому краю) как признака семантики
  колонки, без обучения. `layout_profiles.py` хранит декларативные позиции колонок по банку, но сам
  геометрический экстрактор работает и без профиля, кластеризуя позиции слов.
  Источник: https://github.com/rbrtjns90/statement_organizer/
- **isaacrowntree/ledger** (MIT) — `etl/parsers/pdf_layout.py`: *«keeps each word's horizontal
  position and recovers the column from its right edge — the columns are right-aligned, so right
  edges stay put while left edges drift with the width of the number… The column anchors are read
  from each statement's own header row»*. Формулировка в README прямо называет банковскую практику,
  ради которой это нужно: *«CBA, Bankwest and HSBC's everyday accounts print debits and credits in
  separate columns as bare positive numbers, so flattening a page to text loses the only thing that
  tells a $10 fee from a $10 refund»* — то есть колонка (её позиция), а не текст рядом со значением,
  несёт знак операции. Источник: https://github.com/isaacrowntree/ledger
- **statement-normalizer (Maxed-OSS, Apache-2.0)** — «fuzzy header detection with a broad alias
  table covering the real-world headers from Chase, Bank of America, Wells Fargo, Amex, Capital
  One, Discover» — это гибридный подход: сначала пытается сопоставить заголовок по таблице
  синонимов (не по одному фиксированному имени), при неудаче — вероятно эвристика по содержимому
  (текст неполный, детали не добыты дословно — см. «Недобытое»). Явное **нормализующее правило
  знака**: *«All amounts are normalized to one sign convention (debits negative, credits positive)
  regardless of how the source expressed direction»* — то есть парсер сам умеет по контексту
  формата (раздельные Debit/Credit колонки, скобки, конечный минус) восстанавливать знак без
  обучения. Источник: https://github.com/maxed-oss/statement-normalizer
- **banking-statements (PyPI, версия 0.11.0)** — использует **саму running-balance колонку как
  дополнительный инвариант парсинга**, а не только для отображения: *«Capital One checking rows
  expose a running balance. The processor uses that reported balance as an additional parser
  invariant: reconstructed activity must produce the exact balance transition reported by the
  statement»* — это форма семантической типизации «эта колонка — running balance, потому что её
  дельты построчно совпадают с суммой соседней колонки транзакции», то есть определение роли
  колонки через её АРИФМЕТИЧЕСКУЮ СВЯЗЬ с другой колонкой, а не по имени заголовка.
  Источник: https://pypi.org/project/banking-statements/0.11.0/
- **Контраст «с обучением» (для понимания, что теряет неML-подход):** ZTab, «Zero-shot Column Type
  Annotation for Relational Tables» (arXiv, класс: научная статья, препринт) — типизация колонок
  через fine-tuned LLM и «class prototypes», без заголовков колонки вообще, с сопоставлением по
  косинусной близости эмбеддингов. Это НЕ безмодельный метод (прямо противоречит решению владельца
  «ML не используется») — приведено только как маркер того, что более сложные ML-подходы существуют
  и решают более общую задачу (открытый набор типов, не только 4 предопределённых — дата/сумма/
  описание/баланс), но численных замеров на банковских выписках у этой статьи нет.
  Источник (черновик/препринт, не финальная публикация с проверенным DOI): https://arxiv.org/pdf/2603.11436v1
- **Вывод по подвопросу 3:** ни один из добытых открытых проектов не использует «долю ячеек,
  парсящихся как число» или «монотонность колонки» напрямую как явную формулу для определения
  СЕМАНТИКИ (кроме banking-statements, где это неявно происходит через сверку с running balance) —
  доминирующий паттерн в реальном опенсорсе: (а) fuzzy-соответствие заголовка по словарю синонимов
  на нескольких языках/банках, и только при провале — (б) геометрический признак (правое
  выравнивание чисел = сумма/баланс, левое = описание), плюс (в) финальная проверка through
  reconciliation (раздел 4) как способ отличить «эта колонка — running balance» от «эта колонка —
  просто ещё одна сумма».

## 4. Самопроверка сходимостью остатков (ГЛАВНЫЙ подвопрос)

**Класс: документация опенсорсных бухгалтерских систем (первичный источник, не вторичный пересказ).**

- **Beancount / Fava** (`balance` directive). Официальная документация (beancount.github.io,
  beancount.io) дословно: *«Both Beancount and Ledger implement balance assertions. These provide
  the system with checkpoints it can use to verify the integrity of the data entry»*. Семантика:
  «assert that the inventory of account X contains exactly N units of CCY **at the end of** day
  D» технически реализовано как проверка **на начало следующего дня** (Beancount проверяет
  «balance before any transactions on this date are applied» — то есть привязка к file-order/date
  разная у Ledger и Beancount, см. ниже).
  **Формулировка правила реконсиляции с банком (FAQ, дословно):**
  *«Add a `balance` assertion for the statement's closing figure, dated the day after the closing
  date. Balance assertions are evaluated at the start of their date, so the next morning's
  assertion is what includes every transaction through the last statement day.»*
  **Что делает система при несходимости:** `bean-check` печатает `Balance failed` и **завершается
  с ненулевым кодом возврата** (дословно: *«prints nothing and exits 0 when clean, and lists every
  error and exits non-zero otherwise»*) — то есть **жёсткий отказ (fail loud)**, а не
  предупреждение и не частичный импорт.
  **Исправление несходимости** — директива `pad`: автоматически вычисляет разницу и проводит её
  через `Equity:Opening-Balances`, но документация прямо предупреждает: *«Use this with caution,
  as it can hide larger problems. Explicit adjustments are generally safer»* — то есть
  автоисправление считается опасной практикой, а не рекомендуемой.
  Источники: https://beancount.github.io/docs/balance_assertions_in_beancount/ ,
  https://beancount.io/docs/faq , https://beancount.io/docs/introduction-to-beancount ,
  https://beancount.io/docs/Solutions/analytics
- **Различие семантики Ledger vs Beancount** (важно для формулировки нашего правила):
  Beancount — **date-based** assertions: сортирует все директивы и проверяет баланс «на начало
  дня» (order-independent от места в файле, но не поддерживает внутридневные assertions).
  Ledger — **file-order (file-based)** assertions: держит running balance по мере парсинга файла
  и проверяет **в точке файла**, где стоит assertion — то есть **не** независим от порядка записи.
  hledger — «largely compatible with ledger, largely interconvertible with beancount»; поддерживает
  свой `balance` + флаг `-s/--strict` для дополнительных проверок и `--ignore-assertions`.
  Источник: https://beancount.github.io/docs/balance_assertions_in_beancount/ (секция сравнения),
  https://github.com/simonmichael/hledger/blob/e1899e09/hledger/hledger.1 (man-страница).
- **hledger `check` команда** — man-страница дословно перечисляет проверяемые инварианты:
  *«Are all transactions balanced? Do all balance assertions pass?»*; с флагом `-s/--strict`
  включаются дополнительные проверки. `--ignore-assertions` — явный флаг отключения проверки
  (то есть индустриальная практика допускает и режим «без проверки», не только строгий отказ).
- **Fava** — веб-интерфейс поверх Beancount, использует те же `balance`-assertions;
  добавляет визуальный индикатор свежести (`fava-uptodate-indication` metadata) — цвет счёта
  (зелёный/жёлтый/красный) отражает, насколько recent balance-check покрывает последние записи.
  Это ближайший аналог «предупреждения», а не отказа — UI-слой поверх того же жёсткого ассерта.
- **ofxstatement** (kedder/ofxstatement, GitHub, 357 звёзд на момент замера, лицензия — см. репо)
  — конвертирует проприетарные банковские выписки (CSV и др.) в OFX для импорта в GnuCash/HomeBank.
  Плагин `ofxstatement-mt940` явно работает с полем **Closing Balance (MT940 tag 62/62F)**: опция
  `end_date_derived_from_statements` — если *«MT940 Closing Balance(tag 62) has a date before the
  latest Statement Line (tag 61) date»*, можно взять более позднюю из двух дат. Это подтверждает,
  что **закрывающий остаток из формата явно используется как поле метаданных**, но по добытым
  материалам ofxstatement **не отклоняет импорт** при несходимости — расхождение проверяется уже
  на стороне GnuCash/Beancount через `balance`-директиву после конвертации, а не внутри самого
  конвертера. 🔴 Прямого текста «ofxstatement сверяет входящий+обороты=исходящий и падает при
  ошибке» в добытых материалах НЕТ — вывод сделан по архитектуре (парсер только конвертирует
  формат, проверка выносится в бухгалтерскую систему-потребитель).
  Источники: https://github.com/kedder/ofxstatement/ , https://gpaulissen.github.io/ofxstatement-mt940/
- **GnuCash** — упомянут как целевая система импорта у ofxstatement; отдельного текста про
  встроенную формулу «остаток_вход + кредит − дебет = остаток_исход» как явную self-check внутри
  GnuCash importer в этом проходе НЕ добыт (см. «Недобытое»).
- **Вывод по бухгалтерским DSL:** индустриальный паттерн, подтверждённый дословно в двух
  независимых открытых системах (Beancount и hledger) — **assertion на объявленный закрывающий
  остаток из источника (выписки) + жёсткий отказ всего процесса при несовпадении**
  (`bean-check` → exit non-zero; hledger `check` → аналогично, отключаемо только явным флагом).
  Автоисправление (`pad`) в документации прямо помечено как рискованная практика, не как норма.
  Ни одна из добытых систем не описывает «частичный импорт» как штатный ответ на несходимость —
  это или полный отказ, или (в hledger) явно выключенная проверка.

### 🔴 Прямая находка — специализированные open-source парсеры банковских выписок используют ИМЕННО эту формулу как ядро своей архитектуры

Найдено **семь независимых открытых проектов** (не связаны друг с другом, разные авторы,
2025-2026), у каждого из которых «сходимость остатков» — это не побочная фича, а центральная
идея всей архитектуры. Это прямой, недвусмысленный ответ на главный подвопрос: индустрия УЖЕ
широко использует ровно то правило, которое сформулировано в задании.

| Проект | Лицензия | Формула / механизм | Что происходит при несходимости |
|---|---|---|---|
| `sebastienrousseau/bankstatementparser` (45★) | «Other» (не MIT/Apache — 🔴 проверить текст лицензии отдельно перед использованием кода) | `verify_balance()`: `opening + credits − debits == closing`; статусы `VERIFIED`/`DISCREPANCY`/`UNVERIFIABLE`/`FAILED`; `verify_continuity()` — отдельная проверка непрерывности; `verify_balance_multi_currency()` — то же правило раздельно по валютам, чтобы мультивалютная выписка не давала ложный `DISCREPANCY` | Явный статус-код на транзакцию/партию, не исключение — «мягкий» отказ с диагностикой |
| `isaacrowntree/ledger` (MIT) | **Anchor check**: между двумя выписками сумма транзакций между ними должна равняться изменению печатного closing balance; **Running-balance chain check**: `previous_balance + amount == current_balance` построчно, локализует ошибку до конкретной строки (инвертированный знак даёт дрейф ровно в 2×сумму) | `REFUSED — statement does not account for its own printed balances; nothing was ingested` — **полный отказ приёма файла**, дословная цитата из README |
| `veer0608/moneytrail` (MIT) | `chain`: построчный проход по running balance, каждая строка сдвигает баланс ровно на свою сумму; `totals`: `opening + credits − debits == closing`. Для карточных выписок без running balance — `summary`: `previous − payments + purchases + fees == total due` (та же идея, другая формула) | Печатает конкретную строку и величину расхождения; «money is an integer count of paise… a statement either reconciles to the paisa or it does not» — жёсткий бинарный вердикт, никаких float |
| `rbrtjns90/statement_organizer` (GPL v3.0 🔴 стоп-лицензия) | 4 стратегии реконсиляции под тип выписки: `charges_total` (кредитки), `balance_equation` (`PreviousBalance + Charges − Payments + Interest + Fees = NewBalance`), `running_balance_chain`, `deposits_withdrawals` | «If the sum doesn't match, the extraction is **flagged — never silently wrong**»; при провале детерминированной проверки — таргетированный AI-ремонт (не наш случай, ML исключён) |
| `boscorat/bank_statement_parser` (MIT) | «Checks and balances — automatic validation of opening/closing balances, payment totals, and running balances against statement header values» (детали формулы не процитированы дословно — общая формулировка) | Не процитировано дословно в добытом фрагменте — см. «Недобытое» |
| `Maxed-OSS/statement-normalizer` (Apache-2.0) | Не central reconciliation engine (это нормализатор форматов), но **нормализует знак** так, чтобы сумма транзакций была пригодна для внешней сверки: «debits negative, credits positive regardless of source direction» | Н/П — сверка вынесена за пределы этого инструмента |
| `bankstract` (PyPI 0.3.0, лицензия не зафиксирована в добытом фрагменте) | Два взаимодополняющих режима: **Row-wise** (`prev.balance ± debit/credit == curr.balance`, есть running balance) и **Totals-based** (банки без баланса, например PalmPay — читает `Total Money In`/`Total Money Out` из шапки и сверяет с суммой распознанных строк) | Row-wise: `ReconciliationError` с индексом строки; оба режима существуют специально «to catch silently-dropped rows — the failure mode of naive PDF parsers» (дословно) |
| `banking-statements` (PyPI 0.11.0, лицензия не зафиксирована в добытом фрагменте) | **Разные формулы для активных и пассивных счетов** — явно предупреждает, что для долговых продуктов (кредитка/кредит) знак операции в формуле обратный: `opening + debits − credits = closing` (долг растёт от списаний), тогда как для расчётных счетов `opening + credits − debits = closing`. Дополнительно — сверка running balance как независимый инвариант ДО общей сверки по сумме | «A mismatch does not rewrite the parsed statement» — то есть **automatic-pad категорически исключён из архитектуры**, разница просто репортится (`difference`, `reconciled: bool`) |

🔴 **Главная находка для формулировки нашего правила: формула НЕ универсальна по знаку.**
`banking-statements` прямо документирует, что для счетов-активов (checking/savings) правило
`opening + credits − debits = closing`, а для счетов-обязательств (кредитная карта, кредит,
line of credit) — **обратное**: `opening + debits − credits = closing`, потому что списание
увеличивает долг, а не уменьшает остаток. Наивная реализация одной и той же формулы для всех
типов счетов даст систематический `DISCREPANCY` на любой кредитной выписке. Источник:
https://pypi.org/project/banking-statements/0.11.0/
🔴 **Вторая находка:** ДВА независимых проекта (`moneytrail`, `bankstatementparser`) отдельно
проверяют **множественность валют** и **непрерывность (continuity)** как отдельные инварианты
от базовой суммы — то есть «просто одна формула» на практике декомпозируется индустрией минимум
на 3 независимые проверки: (1) арифметика итогов, (2) построчная цепочка running balance,
(3) непрерывность между соседними выписками/файлами (chain across statements, не только внутри
одного файла) — у `isaacrowntree/ledger` это называется «Anchor check» и явно описано как
«works even for sources that print no per-record balance», то есть решает и случай выписок БЕЗ
running balance колонки вовсе, сверяя только конечные точки между последовательными периодами.
🔴 **Третья находка:** ни один из семи проектов не восстанавливает автоматически исходные данные
при несходимости молча — везде либо жёсткий отказ (`REFUSED`, `ReconciliationError`), либо явный
флаг/статус на выходе (`DISCREPANCY`, `flagged`, `reconciled: false`), который дальше в пайплайне
требует либо ручного вмешательства, либо (там, где авторы допускают ML — не наш случай)
таргетированного AI-ремонта одной конкретной цифры, а не переразбора всего документа.

Источники (все — открытый код на GitHub/PyPI, класс: открытый код, не научная публикация):
https://github.com/sebastienrousseau/bankstatementparser ,
https://github.com/isaacrowntree/ledger ,
https://github.com/veer0608/moneytrail ,
https://github.com/rbrtjns90/statement_organizer ,
https://github.com/boscorat/bank_statement_parser ,
https://github.com/maxed-oss/statement-normalizer ,
https://pypi.org/project/bankstract/0.3.0/ ,
https://pypi.org/project/banking-statements/0.11.0/

## 5. Открытые реализации и замеры на незнакомых вёрстках (лицензии, точность)

**Класс: смешанный — документация, независимый бенчмарк (arXiv, 2024), блоги (2026).**

### Таблица известных инструментов с лицензиями (обязательный маркер GPL-стоп)

| Инструмент | Лицензия | ML внутри | Замер / бенчмарк |
|---|---|---|---|
| Camelot | **MIT** | нет (геометрия: lattice/stream), опционально neural `flavor="ml"` | см. ниже, ICDAR-2013-подобный набор + arXiv-2024 |
| Tabula / tabula-py | **MIT** (сама библиотека; JRE-зависимость) | нет | см. ниже |
| pdfplumber | **MIT** | нет | см. ниже |
| PyMuPDF | **AGPL / коммерческая** 🔴 | нет (rule-based режим) | arXiv-2024 (только текст, не table specifically в этой таблице) |
| gmft | MIT (по таблице сравнения Camelot-доков) | да, PyTorch-модель | не встречен отдельный бенчмарк в этом проходе |
| unstructured.io | Apache 2.0 | опционально (Chipper/detectron2 OCR) | arXiv-2024 (как «Unstructured») |
| tablers (Rust+Python) | MIT | нет | см. таблицу ICDAR ниже (F1 0.750 vs Camelot 0.778) |
| Microsoft Table Transformer (TATR) | **MIT** (репо `microsoft/table-transformer`) | да, DETR-based | PubTables-1M, см. числа ниже |
| Docling (IBM) | **MIT** (репо `docling-project/docling`, дословно из статьи и README) | да, TableFormer (vision-transformer) | TEDS >91% на FinTabNet в режиме ACCURATE (источник — независимый разбор, не первичная публикация авторов, см. ниже) |
| Marker (datalab) | 🔴 **GPL** на код + модельные веса под модифицированной AI Pubs Open Rail-M (свободно для исследований/личного использования/стартапов <$2M выручки/финансирования, иначе нужна платная коммерческая лицензия) — двойной стоп для закрытого продукта без покупки лицензии | да | FinTabNet (TEDS-подобная метрика): marker=0.816, marker+use_llm=0.907, gemini=0.829 (99 таблиц) |
| PaddleOCR / PP-Structure | **Apache 2.0** (репо `PaddlePaddle/PaddleOCR`, 81679★ на момент замера) | да | PubTabNet: TableRec-RARE Acc=71.73%/TEDS=93.88%; **SLANet Acc=76.31%/TEDS=95.89%** (779мс и 766мс/изображение на CPU) — официальный бенчмарк проекта |
| img2table (`xavctn/img2table`) | **MIT**, 895★ | нет своего ML-детектора таблиц (чистый OpenCV: контуры+линии), но подключается к любому OCR-бэкенду (Tesseract/PaddleOCR/docTR/EasyOCR/RapidOCR/Surya/облачные) для текста внутри найденных ячеек | Собственных числовых бенчмарков в README не найдено; авторы прямо предупреждают: «Table detection using only OpenCV processing can have some limitations. If the library fails to detect tables, you may check CNN / LLM based solutions» — то есть САМИ признают геометрический подход слабее ML на сложных случаях |
| docTR | упомянут только как OCR-плагин внутри img2table в этом проходе — отдельно не проверен, см. «Недобытое» | да | не добыто отдельно |
| Table Transformer / Nougat | см. выше (TATR) | — | см. выше |

🔴 **Лицензия PyMuPDF — GPL/AGPL-семейство с коммерческой альтернативой** — для закрытого
продукта FINPILOT это стоп-флаг по строке 5 запроса (юридически запрещена бесплатная GPL-ветка
без покупки коммерческой лицензии Artifex). Источник таблицы сравнения:
https://camelot-py.readthedocs.io/en/latest/user/comparison.html (класс: официальная
документация проекта Camelot, актуальная на момент чтения).

### Числовые замеры

**PubTables-1M / TATR (класс: научная статья + официальный репозиторий, числа воспроизводимы).**
Источник: Smock, Pesala, Abraham, «PubTables-1M: Towards Comprehensive Table Extraction From
Unstructured Documents», CVPR 2022 (openaccess.thecvf.com) + `microsoft/table-transformer` README.
- Table Detection (DETR R18 на PubTables-1M): AP50=0.995, AP75=0.989, AP=0.970, AR=0.985.
- Table Structure Recognition (TATR-v1.0 на PubTables-1M): AP50=0.970, AP75=0.941, AP=0.902,
  AR=0.935, **GriTS-Top=0.9849, GriTS-Con=0.9850, GriTS-Loc=0.9786, Acc-Con=0.8243**.
- Сравнение Faster R-CNN vs DETR на TSR+FA (канонические данные, все таблицы): Faster R-CNN
  AccCon=0.1039 / GriTSTop=0.8616; DETR AccCon=0.8138 / GriTSTop=0.9845 — разрыв между
  классическим детектором и transformer-моделью на этой задаче кратный (AccCon почти ×8).
- GriTS метрика опубликована отдельно: Smock, Pesala, Abraham, «GriTS: Grid table similarity
  metric for table structure recognition», ICDAR 2023 (Springer), pp. 535-549 — класс: научная
  статья, вводит метрику как обобщение 2D-LCS/2D-MSS (полиномиальная эвристика для NP-hard задачи).

**🔴 Безмодельный геометрический разбор ПРОТИВ ML-разбора — прямое сравнение, класс: научная
статья (arXiv 2024, независимый академический бенчмарк, НЕ маркетинг вендора).**
Источник: «A Comparative Study of PDF Parsing Tools Across Diverse Document Categories»,
arXiv:2410.09871 (2024), 10 инструментов × 6 категорий документов (DocLayNet dataset), 400
сбалансированных документов на категорию, Jaccard-порог 0.75 для геометрических инструментов,
IoU 0.60/0.70 для TATR.
Таблица F1/Precision/Recall по категории **Financial** (ближе всего к банковским выпискам):
- Camelot: F1=0.1012, Precision=0.5763, Recall=0.0555
- pdfplumber: F1=0.0623, Precision=0.0596, Recall=0.6530
- PyMuPDF (rule-based): F1=0.1794, Precision=0.1863, Recall=0.1729
- Tabula: F1=0.2432, Precision=0.2740, Recall=0.2186
- **TATR@60 (ML): F1=0.7857, Precision=0.8430, Recall=0.7357**
- TATR@70 (ML): F1=0.7422, Precision=0.7963, Recall=0.6949
🔴 **Главное число для решения владельца о «ML не используется»:** на категории Financial разрыв
между лучшим безмодельным инструментом (Tabula, F1=0.2432) и ML-моделью TATR@60 (F1=0.7857) —
**F1 отличается более чем в 3 раза** (0.7857 / 0.2432 ≈ 3.23×). На категории Scientific разрыв ещё
больше (TATR@60 F1=0.9134 против Camelot F1=0.3392 — ≈2.7×, но pdfplumber там F1=0.0623 — почти
15×). На категории Tender, наоборот, безмодельный Camelot почти догоняет TATR (F1=0.8279 против
TATR@60 F1=0.7496) — то есть **разрыв сильно зависит от типа документа**, не универсален.
Полный текст: https://arxiv.org/html/2410.09871

**Camelot lattice/stream vs Tabula vs pdfplumber vs tablers, на ICDAR-2013-подобном наборе
(класс: официальная документация Camelot, собственный бенчмарк-скрипт `bench/benchmark_icdar.py`,
маркирован автором как «независимая MIT-реализация», TEDS-колонка помечена как «difflib cell-text
proxy, читать относительно»):**
67 born-digital, ruled-heavy PDF. F1/TEDS/row/col/время:
- camelot lattice (engine=combined): F1=0.778, TEDS=0.789, row=0.762, col=0.829, время=101с
- camelot lattice (engine=vector): F1=0.766, TEDS=0.784, row=0.748, col=0.806, время=13с
- tablers (Rust): F1=0.750, TEDS=0.724, row=0.657, col=0.741, время=1.5с (~67× быстрее combined)
Источник: https://camelot-py.readthedocs.io/en/latest/user/comparison.html
🔴 Важная оговорка самого источника: этот бенчмарк измеряет только табличные F1/TEDS-подобные
метрики на РУЧНОМ наборе разработчика Camelot, а не на независимом академическом датасете —
ниже по доверию, чем arXiv:2410.09871 и PubTables-1M/CVPR2022, которые рецензируемые.

**Camelot vs Tabula, качественное сравнение (класс: официальный wiki проекта, не количественный
бенчмарк):** *«We found that Camelot works better than Tabula in all Lattice cases. Tabula does
better table detection for Stream cases, but it still fails to give good parsing output»*.
Источник: https://github.com/camelot-dev/camelot/wiki/Comparison-with-other-PDF-Table-Extraction-libraries-and-tools

**Docling (IBM) — детали (класс: научная статья/технический отчёт arXiv 2408.09869 и 2501.17887 +
официальный README, MIT).** Дословно про причину появления Docling (важно как независимое
подтверждение проблем раздела 1): *«we faced major obstacles with all of them for different
reasons, among which were restrictive licensing (e.g. pymupdf) or poor speed or unrecoverable
quality issues, such as merged text cells across far-apart text tokens or table columns (pypdfium,
PyPDF)»*. Табличная модель — **TableFormer** (vision-transformer, IBM Research), обучена на
DocBank/PubTabNet/FinTabNet; типичная таблица обрабатывается 2-6 секунд на CPU. Сравнение лицензий
конкурентов в независимом разборе (spheron.network, класс: блог, но с таблицей фактов):
Docling MIT / **Marker GPL-3.0** / MinerU Apache-2.0-с-условиями (требуется согласие на скачивание
весов PDF-Extract-Kit). TEDS Docling на FinTabNet (ACCURATE mode) — **>91%** против **~75-80%** у
Marker (базовое, без `--use_llm`) на том же бенчмарке — источник этого сравнения: блог, не
первичная публикация авторов Docling/Marker, поэтому доверие ниже, чем к цифрам из README Marker
и статьи Docling по отдельности. Источники: https://arxiv.org/html/2408.09869v3 ,
https://arxiv.org/pdf/2501.17887 , https://github.com/docling-project/docling/blob/main/README.md ,
https://github.com/datalab-to/marker/blob/main/README.md (лицензия и цифры FinTabNet — из README
Marker дословно), https://www.spheron.network/blog/self-host-document-intelligence-docling-marker-mineru-rag-guide/
(класс: блог, сравнительная таблица, независимая от вендоров).

**Официальные параметры pdfplumber `TableSettings`** (для раздела 1, но релевантно и здесь по
классу материала — исходный код, не документация): `snap_tolerance`, `join_tolerance`,
`intersection_tolerance`, `min_words_vertical/horizontal`, `edge_min_length` — источник:
https://github.com/jsvine/pdfplumber/blob/stable/pdfplumber/table.py

## 6. Механизм сбора новых вёрсток без утечки данных (schema fingerprinting)

**Класс: смешанный — независимый разбор (mlsystemsreview.com, thalvi.app — блоги с претензией на
техническую точность), open-source репозиторий с явной архитектурой (GitHub, MIT-подобный проект
`vul-os/slipscan`), документация вендора (Salt Edge).**

- **Термин «schema fingerprinting» / «layout fingerprint» дословно у крупных агрегаторов
  (Plaid/Yodlee/Salt Edge/Tink/Nordigen) в этом проходе НЕ НАЙДЕН** — они в 2024-2026 годах
  практически полностью ушли от «парсинга PDF-выписок» к **OAuth/Open Banking API** (структурированные
  данные, не документ). Это меняет саму постановку вопроса: у них нет проблемы «новая вёрстка PDF»,
  потому что банк отдаёт JSON/XML через API, а не PDF-документ для геометрического парсинга.
  Источник (класс: независимый разбор со ссылками на первичные источники, дата 2026-04-05):
  https://thalvi.app/resources/guides/how-finance-apps-access-bank-data/ — *«Plaid switched
  those... Section 1033 rulemaking formally codifies data rights. Most... Bank of America, Wells
  Fargo, Capital One... APIs that Plaid consumes»*; аналогично
  https://mlsystemsreview.com/plaid-bank-api-design/: *«The long-term [trend] is open-banking
  APIs... scraping nowhere [to go]»*, «for credential-based, Plaid's backend stores encrypted
  credentials because it must re-login to refresh data. In the latter [OAuth], Plaid stores only
  refresh tokens».
- **Данные о продаже транзакционных данных (важно для контраста с нашей архитектурой
  «не выгружаем содержимое»):** Yodlee продавала обезличенные транзакционные данные хедж-фондам
  (Point72 Asset Management) — продукты Predictive Revenue Signals / Shopping Insights, покрытие
  30M+ деидентифицированных пользователей, подписка $50k–$4M за фонд/год (WSJ, август 2015).
  Plaid — после иска на $58M (2022, In re Plaid Inc. Privacy Litigation, N.D. Cal.) — по политике
  **не продаёт** транзакционные данные третьим лицам, только SaaS-модель.
  Источник: https://thalvi.app/resources/guides/how-finance-apps-access-bank-data/
- **Salt Edge** — документация (docs.saltedge.com) даёт только общее: *«All sensitive data is
  encrypted using 2048-bit keys… none of the transmitted credentials are stored in the system as
  plain text»* — ничего конкретного про накопление шаблонов вёрстки. Класс: официальная
  документация, но не по нужной теме.
- **Открытый пример архитектуры «структура да, данные нет» — `vul-os/slipscan`**
  (класс: открытый код, README/docs в репозитории, лицензия не зафиксирована в добытом фрагменте —
  см. «Недобытое»). Прямая релевантность вопросу — они формализуют ИМЕННО «схему маппинга колонок
  как отдельные от данных сущности»:
  *«downloaded statement CSVs are the way in — and the mappings that parse them are
  **region-profile data**: a catalog of named, region-tagged column mappings
  (`crates/slipscan-ingest/src/bank/presets.rs`)»*. Три уровня: (1) готовые пресеты под конкретный
  банк (`za-fnb`, `za-standard`, …), (2) общее семейство `generic` под типовые раскладки колонок
  (дата/описание/сумма-со-знаком или дата/описание/дебет/кредит, разные конвенции дат и
  разделителей), (3) `CustomMappingSpec` — декларативная спецификация (индексы колонок, формат
  даты, стиль десятичных, разделитель, дебет/кредит или сумма-со-знаком) для любого нового банка.
  Это структурно ОЧЕНЬ близко к нашему «фиксируем геометрию/заголовки, не значения» — но у них
  это про CSV-колонки, не про PDF-геометрию/шрифтовые метрики.
  Источник: https://github.com/vul-os/slipscan/blob/main/docs/BANK-ADAPTERS.md
- **PennyRush (Android+Next.js+Supabase, класс: блог инженера-разработчика, dev.to,
  дата 2026-09-13)** — прямая формулировка политики «в память и выбросить», близкая к нашему
  вопросу о нехранении содержимого: *«the file is read into memory, parsed into candidate
  transactions, and then dropped by the client flow. It is never written to disk, object storage,
  analytics, or logs. What persists is only the saved activity fields: amount, date, merchant,
  note, type, and category»*. Обнаружение заголовка колонки — по эвристике, не по фиксированному
  индексу: *«it hunts for the header row instead of assuming row zero. It scores each line on
  whether it contains a date-like column, a money-like column..., and a description-like column»*.
  Это отвечает и на подвопрос 3 (см. ниже) — пример неML-типизации колонок по контенту, но
  зафиксирован только текстовый CSV/receipt-OCR кейс, не PDF-таблица.
  Источник: https://dev.to/royalpinto007/parsing-bank-statements-in-memory-keep-the-fields-store-nothing-else-1hj5
- **docparser / bankstatementconverter.com / DocuClipper — privacy policy на предмет
  «schema fingerprinting» 🔴 НЕ ПРОВЕРЕНО в этом проходе** — прямой доступ к их privacy policy
  не был добыт (см. «Недобытое»).
- **Вывод по подвопросу 6:** прямого индустриального термина «schema/layout fingerprinting»
  у банковских агрегаторов не обнаружено, потому что крупные игроки решили проблему «нового
  банка» переходом на API, а не сбором PDF-шаблонов. Ближайшая параллель по духу (структура
  отдельно от данных, версионируемый каталог пресетов) — открытый проект-парсер CSV-выписок
  (`slipscan`), не PDF-парсер и не банк/агрегатор в привычном смысле.

## Недобытое и причина

Ничего из этого не добыто из-за исчерпания бюджета (бюджет не исчерпан — осталось ~14 из 30
добывающих вызовов); причина в каждом случае — либо материал оказался вторичным/малорелевантным
после первого прохода поиска и не стал приоритетом, либо канал не был опробован в отведённое время:

1. **pdf2table (Yildiz), PDF-TREX (Oro & Ruffolo), T-Recs (Kieninger)** — упомянуты как классика
   в связанных статьях по X-Y cut (раздел 2), но их собственный полный текст/абстракт не запрошен
   отдельно. Не критично для ответа: метод (проекционные профили + эвристики) уже подтверждён
   тремя другими первоисточниками (Nagy&Seth, Ha/Haralick, Nurminen/Tabula).
2. **Hu, Kashi, Lopresti & Wilfong (2001), «Table Structure Recognition and Its Evaluation»** —
   цитата о нём взята из вторичного источника (статья Wang/Haralick), прямой PDF не получен.
3. **docTR как самостоятельный инструмент** (не как OCR-плагин внутри img2table) — лицензия и
   собственные бенчмарки таблично не сверены отдельно.
4. **docparser, bankstatementconverter.com, statementconverter.com, DocuClipper — privacy policy**
   дословно НЕ прочитаны в этом проходе (подвопрос 6). Общий вывод по подвопросу 6 сделан на основе
   независимых разборов агрегаторов (Plaid/Yodlee/Salt Edge) и одного открытого проекта
   (`slipscan`), а не на прямом чтении privacy policy конвертеров выписок.
5. **GnuCash — внутренняя формула реконсиляции импортёра** (именно текст из документации/кода
   GnuCash Import Matcher) не процитирована дословно — GnuCash упомянут только как целевая система
   для `ofxstatement`, не как первичный источник по своей собственной логике сверки.
6. **Лицензии `bankstract` и `banking-statements`** (PyPI) не зафиксированы дословно (страницы
   PyPI, откуда взяты формулы, не содержали явного поля License в добытом фрагменте) — перед
   использованием кода этих двух пакетов лицензию нужно проверить отдельно (`pip show` / repo).
7. **Лицензия `sebastienrousseau/bankstatementparser` = «Other»** (не MIT/Apache/GPL по метаданным
   GitHub) — точный текст лицензии не прочитан; 🔴 перед любым использованием кода этого проекта
   нужно открыть файл LICENSE в репозитории и проверить формулировки.
8. **boscorat/bank_statement_parser** — общая формулировка «checks and balances… against statement
   header values» процитирована, но точная формула (знак, обработка кредитных vs дебетовых счетов)
   не добыта дословно из кода/документации проекта.
9. **ZTab (arXiv 2603.11436v1)** — статус публикации (препринт/конференция, дата) не уточнён;
   приведена только как контрастный пример ML-подхода, числовые метрики на банковских данных
   отсутствуют в добытом фрагменте.
10. **WebSearch/WebFetch не пробовались вовсе** в этом проходе — по инструкции считались «сегодня
    практически мертвы»; весь объём добыт через `mcp__exa__web_search_exa`, что оказалось
    полностью рабочим каналом без единого отказа за ~16 вызовов.
