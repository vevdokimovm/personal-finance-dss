# Г66/Б-01 — подагент «практика клиентского разбора выписок + правовая практика on-device (РФ)»

Дата: 2026-09-22. Зона: вопрос A (кто разбирает выписки на клиенте) и вопрос B
(гибридные схемы, российская правовая практика «обработки на устройстве»).
Pyodide и цена переноса — НЕ моя зона (второй подагент).

## Журнал

(записи дописываются после КАЖДОГО вызова, дословно, до выводов)

### Вызов 2 — `curl api.github.com/repos/<o>/<r>` (HTTP 200 по всем, кроме одного)

Дословный вывод (2026-09-22):

```
firefly-iii/data-importer  license AGPL-3.0   pushed_at 2026-09-21T13:52:20Z  archived false  stars 835
firefly-iii/firefly-iii    license AGPL-3.0   pushed_at 2026-09-22T04:18:11Z  archived false  stars 24691
actualbudget/actual        license MIT        pushed_at 2026-09-21T22:25:36Z  archived false  stars 29069
   desc: "A local-first personal finance app"
simonmichael/hledger       -> null (репозиторий по этому пути не отдан; hledger живёт на github.com/simonmichael/hledger,
                              проверить другим написанием — НЕ ДОБЫТО на этом вызове)
beancount/beancount        license GPL-2.0    pushed_at 2026-08-23T20:17:45Z  archived false  stars 6021
jbms/beancount-import      license GPL-2.0    pushed_at 2026-08-20T17:11:43Z  archived false  stars 471
   desc: "Web UI for semi-automatically importing external data into beancount"
maybe-finance/maybe        license AGPL-3.0   pushed_at 2025-07-24T22:20:44Z  archived TRUE   stars 54274
   -> 🔴 АРХИВИРОВАН, последний пуш 24.07.2025. Проект МЁРТВ как продукт.
ledger/ledger              license NOASSERTION pushed_at 2026-09-22T04:02:16Z archived false stars 6041
Gnucash/gnucash            license NOASSERTION pushed_at 2026-09-21T19:46:43Z archived false stars 4353
```

### Вызов 3 — Exa: «bank statement PDF to CSV converter that runs entirely in your browser»

Найдено ДЕВЯТЬ живых браузерных конвертёров выписок. Дословные цитаты с их страниц:

**1. Local Bank Statement Converter — https://localbankstatementconverter.com/**
Автор назван поимённо: Priyanshu Dangi. Код открыт:
https://github.com/PriyanshuDangi/localbankstatementconverter
Дословно с сайта: «Everything runs locally in your browser — your financial data never
touches a server.» · «Files are processed using WebAssembly inside your browser. Nothing is
uploaded. **Verify it yourself in the Network tab.**» · FAQ: «All PDF processing happens
entirely in your browser using WebAssembly technology (**Pyodide**).»
Дословно из README репозитория (АРХИТЕКТУРА — не маркетинг):
> «A privacy-first bank statement PDF to CSV converter that runs entirely in your browser.
> Your financial data never leaves your device — **there is no backend**.»
> 1. You drop a PDF into the page.
> 2. **Pyodide** (CPython compiled to WebAssembly) loads in a **Web Worker** and uses
>    **`pdfminer.six`** to extract text along with word coordinates and graphic elements
>    (rectangles, lines).
> 3. A **vanilla-JS parser** reconstructs the transaction table using a three-tier strategy:
>    - **Rectangle-based** — uses the PDF's drawn borders to find table cells.
>    - **Position-based** — falls back to word x/y coordinates and column alignment.
>    - **Text-based** — last-resort heuristic for plain-text statements.
> 4. CSV is generated in-browser and offered as a download.
> «No server, no analytics, no telemetry. A Service Worker caches the WASM runtime.»
> Признанное САМИМИ авторами ограничение: «The first time you upload a PDF, the page will
> spend **3–5 seconds downloading the Pyodide WASM runtime (~10 MB)** from the jsDelivr CDN.»
> Тестируемость: «The parser is plain ESM, so it can be tested directly in Node — no headless
> browser, no Pyodide. The pipeline has two stages: a Python extractor (mirrors what Pyodide
> does in the browser) writes .txt + .json per PDF, then a Node runner feeds those into the
> parser and compares output.»
🔴 Прямое попадание в тему Г66: чужой продукт РЕШИЛ ровно нашу задачу связкой
Pyodide + pdfminer.six в Web Worker, и трёхуровневая стратегия разбора таблицы
(рамки → координаты → текст) описана как рабочая. **Подтверждено кодом, не маркетингом.**

**2. freestatementtocsv.com** — «FreeStatementToCSV never uploads your files. Everything is
processed locally in your browser memory, so your data stays on your device.» Поддержка
PDF, CSV, XLSX. Код не заявлен — подтверждения кодом НЕТ.

**3. SoftZaR — https://softzar.com/bank-statement-converter/**
«Softzar performs 100% in-browser table extraction using WebAssembly and local JavaScript:
Raw Bank Text ──► Local RAM Regex Parser ──► ExcelJS (.xlsx) / CSV ──► Direct Download» ·
«100% Zero-Knowledge client-side privacy».
🔴 Признанное авторами ограничение, важное: разбора PDF там по сути НЕТ — пользователю
предлагают «open your PDF bank statement, select all text (Ctrl+A), copy, and paste it
directly into the input box above». То есть извлечение текста переложено на просмотрщик PDF
пользователя, а инструмент — только regex-парсер текста.

**4. StatementSheet — https://statementsheet.app/** — 🔴 САМЫЙ ЧЕСТНЫЙ пример границы
клиент/сервер, дословно:
> «Parsing happens in your browser. We never receive your statement PDF. **When you export,
> only the parsed rows you can see are sent once to generate the file, then discarded.**
> Unreadable scanned pages go to cloud OCR **only if you explicitly click Send**.»
> «Free-tier metering stores **metadata only (page count, bank label, timestamp), never
> statement content**.»
Это ровно гибридная схема из вопроса B: разбор на клиенте, наружу — только то, что
пользователь видит, плюс метаданные без содержания.

**5. StatementSift — https://statementsift.com/** (публикация 2026-06-09)
«Parsing runs locally; incomplete balance evidence is marked for review.» Признание
ограничения дословно: «A [correct] balance does not prove every transaction is [captured]:
compare the original before import.» И честная оговорка про сеть: «**The browser may load
software and fonts online, while statement contents are processed locally.**»

**6. SanctumPDF — https://sanctumpdf.com/** — «It runs entirely in your browser… All
processing happens locally using WebAssembly». Экспорт в CSV, Excel, JSON, **OFX, QIF**.
Оговорка: в таблице сравнения указано «PDF bank statement conversion — Built in with **AI**»
— то есть заявление «100% browser-based» соседствует с ИИ-фичей, границу авторы не проводят.

**7. Refinata — https://refinata.com/tools/bank-statement-to-csv** — «100% In-Browser
(WebAssembly)» против «Cloud Competitors (iLovePDF, Smallpdf) — Uploaded to third-party
cloud server… Stored on cloud disks for 1–2 hours». Дословно: «Verify with Chrome DevTools:
exactly 0 bytes leave your computer.» Правовая привязка их же словами: «GDPR Article 44 &
HIPAA Safe».

**8. bankstatementconverter.us.com** — «The conversion runs entirely in your browser with
JavaScript. Nothing about your file is transmitted anywhere — **a strict content-security
policy even blocks the page from sending data out**.» 🔴 CSP как ТЕХНИЧЕСКОЕ доказательство
заявления — приём, который можно проверить со стороны.

**9. AccountantToolkit / Statement2CSV — https://accountanttoolkit.com/statement-to-csv**
(обновлено 30.03.2026). Дословно про библиотеку: «The tool reads a text-based PDF in the
browser **with PDF.js**, then rebuilds rough statement lines from positioned text items.»
Признанное авторами ограничение и план: «The current build is intentionally local-first.
**If the tool later needs OCR, saved jobs, or institution-specific rules, that is the point
to graduate into Cloudflare Pages Functions or a Worker-backed pipeline.**» ·
«If the PDF is image-only, paste OCR text first.»

### Вызов 4 — Exa: РФ, обработка ПДн на устройстве пользователя

🔴 Главная находка — **BIRCH LEGAL, обзор «Дня открытых дверей Роскомнадзора по вопросам
персональных данных (14 августа 2026 года)», https://birchlegal.ru/legal_alerts/3812/,
опубликовано 28.08.2026**. Дословные ответы экспертов РКН в изложении обзора:

> «Нет, если идентификатор относится не к субъекту, а к объекту: госномер/VIN-номер авто
> (к транспортному средству), номер лицевого счета (к жилому помещению), **номер телефона
> (к пользовательскому устройству). Однако в совокупности с ФИО и другими данными они
> становятся ПДн.**»

> «152-ФЗ **не известно разделение на операторов и обработчиков**. Российскому
> законодательству известно только понятие оператора. Соответственно, **любая организация,
> которая обрабатывает ПДн, является оператором**, на нее возлагаются все необходимые
> требования.»

> «Договор с оператором. Это ключевая ошибка – обработчики указывают согласие гражданина,
> но согласие дается оператору, а не обработчику. Более того, согласие выдается на поручение
> на обработку, оно **не равнозначно** согласию на обработку ПДн.»

> [про трансграничную передачу] «Нет, если **пользователь самостоятельно передает данные**
> зарубежной нейросети (в данном случае отношения площадка-пользователь). Трансграничная
> передача ПДн предполагает отношения «оператор-оператор», когда российский оператор сам
> передает данные иностранному оператору.»
🔴 Последняя цитата — ближайшая найденная аналогия к нашему вопросу: РКН признаёт, что
действие, совершённое САМИМ пользователем, не делает площадку стороной обработки-передачи.

**Определение обработки (то, с чем придётся мериться), дословно из п. 3 ст. 3 152-ФЗ**,
воспроизведено и в письме Минцифры от 12.05.2025 N П25-44929
(https://www.consultant.ru/document/cons_doc_LAW_511584/), и в ответе РКН от 24.03.2025
(https://storage.yandexcloud.net/comply-publicfiles/public/Otvet_RKN_24.03.2025_lokalizatsija.pdf):
> «под обработкой персональных данных понимается **любое действие (операция) или совокупность
> действий (операций), совершаемых с использованием средств автоматизации или без
> использования таких средств** с персональными данными, включая сбор, запись,
> систематизацию, накопление, хранение, уточнение (обновление, изменение), извлечение,
> использование, передачу (распространение, предоставление, доступ), обезличивание,
> блокирование, удаление, уничтожение персональных данных.»

**Ст. 1 ч. 1 152-ФЗ, сфера действия (https://minzdrav.gov.ru/documents/5402-federalnyy-zakon-152-fz-ot-27-iyulya-2006-g):**
> «…осуществляемой … юридическими лицами и физическими лицами с использованием средств
> автоматизации, в том числе в информационно-телекоммуникационных сетях, или без
> использования таких средств, если обработка персональных данных без использования таких
> средств соответствует характеру действий…»

**Определение оператора, ст. 3 152-ФЗ** (в изложении юрфирмы «Шмелева и Партнеры»,
https://shmeleva-partners.ru/administrativnoe-pravo/operator-personalnyh-dannyh-objazannosti-i-otvetstvennost-po-152-fz-v-2026-godu,
10.08.2026):
> «оператором признается лицо, которое **самостоятельно или совместно с другими лицами
> организует и осуществляет обработку** ПД, а также **определяет ее цели и состав действий**.
> Иначе говоря, оператор персональных данных контролирует «зачем» и «как» обрабатывается
> информация о человеке, **а не просто физически хранит файлы или предоставляет сервер**.»

**Обезличивание — действующий акт:** Приказ Роскомнадзора от 19.06.2025 N 140 «Об утверждении
требований к обезличиванию персональных данных и методов обезличивания…»,
https://www.consultant.ru/document/cons_doc_LAW_511184/2ff7a8c72de3994f30496a0ccbb1ddafdaddf518/
— отменил прежний Приказ РКН N 996 от 05.09.2013. 🔴 Для гибридной схемы (на сервер уходят
«обезличенные агрегаты») это НОРМАТИВНЫЙ текст, по которому будут мерить обезличивание.

**Мобильные приложения и 152-ФЗ** — https://shmeleva-partners.ru/administrativnoe-pravo/personalnye-dannye-v-mobilnom-prilozhenii-trebovanija-152-fz-dlja-razrabotchikov-i-vladelcev
(26.08.2026): «Нормы 152-ФЗ действуют в полном объеме, **даже если база минимальна и сбор
идет только через SDK и аналитику**.»

🔴 **Отрицательный результат по вопросу B.2 на этом вызове:** ни одного документа РКН,
судебного акта или разъяснения, ПРЯМО отвечающего «обработка на устройстве пользователя —
обработка ли оператором», найти не удалось. Найдены только общие определения и косвенная
аналогия из Дня открытых дверей 14.08.2026. Требуется добор.

### Вызов 5 — Bash: hledger + поиск кода по GitHub (`gh api search/code`), HTTP 200

`curl api.github.com/repos/simonmichael/hledger` → **301 Moved Permanently**, редирект на
`https://api.github.com/repositories/9301414` (репозиторий переименован/перемещён, НЕ мёртв;
класс 🟢 — не дошёл, потому что не следовал редиректу, `-L` не ставил).

`gh api search/code q='pdfjs-dist "bank statement" in:file'` → **total_count = 742**.
Первые совпадения: `katanaml/sparrow`, `potatameister/PaperKnife`, `open-mercato/open-mercato`
(`.ai/specs/SPEC-040-2026-02-22-document-parser-module.md`), `AJ/FinSight`,
`fire-tools-inc/app` (**`docs/pdf-import.md`**), `coolchigi/bank-statements-parser`.

`gh api search/code q='pdfjs "statement" parser extension:ts'` → **total_count = 613**.
Прямые попадания в «разбор ТАБЛИЦ выписки на TypeScript»:
```
patryksztuczka/cashworker-effect | apps/backend/src/modules/parsers/pko-statement-parser-service.ts
rudra-iitm/ledger                | lib/pdf/extract.ts
zenmoney/ZenPlugins              | src/plugins/simbank-kg/parser-pdf.ts
letehaha/budget-tracker          | packages/backend/src/services/import-export/statement-parser/text-extractor.unit.ts
viperrcrypto/PocketWatch         | src/lib/finance/statement-pdf-parser.ts
alston06/ExpenseTracker          | statement-parser-pdf.ts
diretoriaatacadao2026-sketch/financeiroatacadaodosvidros | src/lib/pdf-statement-parser.ts
sandgraal/compass                | electron/integrations/finance.ts
subscriptionmanager26-png/wealth-web | mobile-vendor/parser/statement-parser.node.ts
```
🔴 **Наблюдение, важное для Г66:** в выдаче 613 результатов по `pdfjs` + statement + `.ts`
бóльшая часть путей содержит `backend/`, `.node.ts`, `electron/` — то есть pdf.js берут
как JS-библиотеку разбора, но запускают её **на сервере/в Node/в Electron**, а не в браузере.
Чисто браузерных путей (`src/lib/...`) в верхней десятке два: `viperrcrypto/PocketWatch`
и `diretoriaatacadao2026-sketch/...`. Отдельно отмечу `zenmoney/ZenPlugins` — это плагины
российского Дзен-мани, и там `parser-pdf.ts` лежит в плагине банка (Киргизия), то есть
российский PFM-вендор разбирает PDF-выписки кодом на TypeScript в своём плагинном рантайме.

### Вызов 6 — Exa: Actual Budget, где происходит разбор импорта. ПОДТВЕРЖДЕНО ДОКОЙ И КОДОМ

**Официальная дока, https://actualbudget.org/docs/getting-started/sync/, дословно:**
> «Actual is a different kind of app. It stores all of your data on your installed Actual
> server by default AND **it stores all of your data on your local device**. That means it
> works regardless of your network connection, and you always have direct access to your
> data. **Your data never goes to any external servers that you don't choose.**»
> «For the super privacy-focused, it even allows for your data to be **end-to-end encrypted**
> so that **all your server is doing is passing around changes** that you make to your budget.»
> «Before your data leaves your device, it is encrypted using keys only you have.»
> 🔴 Честное ограничение, названное самими авторами: «**Data on your local device is still
> unencrypted.** We recommend full disk encryption if you are interested in local encryption.»
> И ещё одно: «…**the bank sync tokens (e.g. SimpleFIN, GoCardless) are stored separately on
> the server and** [не покрыты] **end-to-end encryption**.»

**Официальная дока API, https://actualbudget.org/docs/api/, дословно — это и есть
подтверждение архитектурой, а не маркетингом:**
> «While your data is stored on a server, **the server does not have the functionality for
> analyzing details of or modifying your budget.** As a result, **the API client contains all
> the code necessary to query your data and will work on a local copy.**»
> «The package also ships a **browser build**… Behind the scenes, `init` starts a **Web Worker**
> running the same budget engine the Actual web app uses, backed by **SQLite compiled to
> WebAssembly**. Your budget data is stored in the browser's **IndexedDB and stays on the
> device**.»
> Ограничение, названное авторами: «The engine uses **`SharedArrayBuffer`**, so the page that
> runs the API must be served **cross-origin isolated**: over HTTPS, with
> `Cross-Origin-Opener-Policy: same-origin` and `Cross-Origin-Embedder-Policy: require-corp`.
> **This is a hosting/server requirement (it cannot be bundled away).**»
🔴 Это прямое техническое требование к хостингу, которое наследует любой, кто повторит схему.

**Форматы импорта, https://actualbudget.org/docs/transactions/importing/:**
> «Actual supports importing **CSV, QIF, OFX, QFX and CAMT** files.»
PDF среди них НЕТ. Дедупликация: «This works best with OFX/QFX files since they provide rich
data about transactions. They provide an **id** that we can use to avoid importing duplicates.
After checking the id, Actual will look for transactions **around the same date, with the same
amount, and with a similar payee**.»

**Где физически лежит логика импорта — из issue #1085 (actualbudget/actual, 01.06.2023,
автор j-f1), дословно:**
> «Currently, an OFX or CSV file can only be imported **from the UI**… This change would
> require a refactor since **a portion of the import logic is currently in the [React]
> component**. Most important is the field mapping and date parsing for CSVs, but there are
> some other pieces of logic that should be **moved into `loot-core`**.»
🔴 Это и есть искомое подтверждение КОДОМ: разбор CSV/OFX у Actual живёт в клиентском
UI-компоненте и в `loot-core` (пакет, который «runs on any platform»), а не на сервере.
Сервер по их же словам «does not have the functionality for analyzing».

**Демо, доказывающее полностью браузерный путь: https://github.com/actualbudget/browser-app-demo**
> «A demo app showing how to use `@actual-app/api` **directly in the browser — no backend of
> your own**. It loads an Actual Budget file client-side… It uses the **browser build** of
> `@actual-app/api`, which **downloads your encrypted budget, decrypts it locally, and opens
> it as a SQLite database compiled to WebAssembly (persisted via IndexedDB)**.»
> «`api.importBudget(...)` — or load an Actual export (.zip) **with no server at all**.»

**Стороннее независимое описание архитектуры (davistroy/open-brain, ниже) —
`docs/ACTUAL_BUDGET_INTEGRATION.md`):** «Actual is **local-first / CRDT-sync**. There is
**no general REST API** on the server… The official Node client downloads the full budget into
a local SQLite cache dir… Changes **sync back** to the server as **CRDT messages**.»

### Вызов 7 — Bash: Firefly III data-importer README (HTTP 200, 6701 байт), hledger, GnuCash

**`firefly-iii/data-importer`, readme.md, дословно:**
> «The **Firefly III Data Importer** is built to help you import transactions into Firefly III.
> It is **separated from Firefly III for security and maintenance reasons**.»
> «The data importer **does not connect to your bank directly**. Instead, it uses **third party
> data providers**… Some of these providers are free of charge, others charge money.»
> «If you do not want to rely on third parties to import your data, you can import data using
> the following file formats: **CSV, CAMT.052, CAMT.053**.»
> «This application is for people who want to track their finances, keep an eye on their money
> **without having to upload their financial records to the cloud**.»
🔴 Вывод по месту разбора: у Firefly III разбор **СЕРВЕРНЫЙ**, но сервер — **свой,
самоходный (self-hosted)**. Это не «на клиенте», это «на своём сервере вместо чужого облака».
Формат PDF **не поддерживается вовсе** — только CSV и CAMT (ISO 20022 XML). Лицензия
**AGPL-3.0** (заражающая для SaaS: раздача по сети = обязанность отдать исходники).

`api.github.com/repositories/9301414` (редирект от `simonmichael/hledger`) →
**`hledgerorg/hledger`, лицензия GPL-3.0, pushed_at 2026-09-22T04:12:45Z, archived false,
4714 звёзд.** Живой. hledger/hledger-web — это **локальный веб-сервер на своей машине**
(`hledger-web` слушает localhost), то есть «локально», но не «в браузере»: разбор в Haskell
на стороне процесса. Лицензия GPL-3.0 — для SaaS менее опасна, чем AGPL, но для линковки
кода всё равно копилефт.

`Gnucash/gnucash` — лицензия в API отдаётся как `NOASSERTION` / «Other» (фактически GPL-2.0,
GitHub её не распознаёт по файлу). Десктопное приложение на C/C++, разбор OFX/QIF/CSV —
**локально на машине пользователя**, сервера нет вообще.

### Вызов 8 — Exa: РФ, локальная обработка и статус оператора. 🔴 ГЛАВНАЯ ПРАВОВАЯ НАХОДКА

**1. Судебная практика, максимально близкая к вопросу: дело № А40-12676/2024.**
Источник: https://www.abssp.ru/posts/04 (без даты публикации; постановление —
**27 марта 2025 года, Арбитражный суд Московского округа**; СНТ «Якорь» против Управления
Роскомнадзора по ЦФО). Дословно из изложения:
> «сбор персональных данных через интернет-сайт **не является автоматически обработкой
> с использованием средств автоматизации**, что освобождает оператора от обязанности
> уведомлять Роскомнадзор…»
> «Суд подчеркнул, что решающее значение при определении автоматизированной обработки имеет
> **не способ получения** персональных данных (например, через сайт), **а то, как эти данные
> обрабатываются после сбора**.»
> «Автоматизированной обработка признается, если **используемые программы самостоятельно
> переформатируют данные, выбирают их по заданным параметрам или передают третьим лицам
> без проверки человеком** каждого субъекта данных.»
> Нормативная опора: п. 1 и п. 2 Положения, утв. **Постановлением Правительства РФ
> от 15.09.2008 № 687**; ст. 22 ч. 2 п. 8 152-ФЗ.
> «Роскомнадзор **не предоставил данных** о том, что СНТ «Якорь» использует программное
> обеспечение, автоматически обрабатывающее персональные данные… Кассационный суд… указал,
> что этот вывод **не подтвержден доказательствами**.»
🔴 Прямо против нас работает критерий «программы самостоятельно переформатируют данные,
выбирают их по заданным параметрам» — разбор выписки это ровно и есть. Но работает ЗА нас
критерий «бремя доказывания автоматизации лежало на РКН» и «значение имеет то, что
происходит ПОСЛЕ сбора».

**2. Единственный найденный материал, разбирающий АРХИТЕКТУРУ как способ не быть
оператором.** «Как законно избежать статуса оператора персональных данных», SEBERD IT Base,
https://seberd.ru/5599/, **18.04.2026**, дословно:
> «Цель — вот центральный критерий… существует более глубокая стратегия: обосновать, что
> в контексте вашей деятельности либо **отсутствует сам объект регулирования** (персональные
> данные для вас), либо **не совершается действие «обработка» в его юридическом понимании**.
> Например, **шифрование данных с ключом у клиента** или работа только с криптографическими
> хешами **может менять правовую природу информации в вашей инфраструктуре**.»
> «…если архитектура построена так, что заказчик самостоятельно управляет базой…, а ваше
> приложение лишь предоставляет ему интерфейс для работы с этой базой, **технически вы не
> обрабатываете ПДн в смысле 152-ФЗ. Ваша система выступает как проводник**, логику и цели
> обработки определяет клиент.»
> 🔴 И тут же названа цена: «Главный риск — административный. Роскомнадзор и суды **часто
> занимают расширительную позицию** в трактовке. Они **могут признать обработкой даже
> автоматическое кэширование IP-адресов на CDN**. Ваша защита — это не отрицание фактов,
> а их переквалификация через призму цели и возможностей. Однако **в спорной ситуации бремя
> доказывания ляжет именно на вас**. Потребуется привлекать экспертов, проводить
> IT-форензику, что дорого и долго.»
> Приведён замер по реальному эпизоду: «в 2021 году один из облачных провайдеров столкнулся
> с претензией Роскомнадзора по поводу хранения IP-адресов в логах балансировщика…
> Провайдеру удалось доказать, что эти данные хранились **менее часа**… Но **процесс
> доказательства занял несколько месяцев** и потребовал детального технического отчёта.»
> Рекомендация того же источника: «Часто более рациональным путём оказывается **не избегание
> статуса, а его точечное и контролируемое принятие**.»

**3. Кто оператор — критерий «цели и средства», не «где лежит файл».**
ГАРАНТ.РУ, https://www.garant.ru/consult/business/1862845/, **10.09.2025**, дословно:
> «лицо признается оператором персональных данных **вне зависимости от какой-либо
> регистрации**, наличия или отсутствия специальных разрешений и т.п., **а в силу самого
> факта осуществления им деятельности по обработке** персональных данных.»
> «…**хостинг-провайдер, предоставляющий вычислительные мощности, фактически также
> осуществляет обработку персональных данных**, с той лишь разницей, что он делает это
> по поручению оператора. **Тот факт, что данные действия он осуществляет автоматически,
> не опровергает указанный вывод.**»
🔴 Это опасная для нас аналогия: «автоматически, без участия человека» — не аргумент.

b-152.ru, https://b-152.ru/kto-obyazan-soblyudat-152-fz, **28.08.2025**, дословно:
> «оператором является **не тот, кто физически нажимает кнопку «отправить», а тот, кто
> принимает решение**: какие данные собирать… зачем они нужны… как обрабатывать и хранить…»
> «Если вы — лицо, определяющее цели и средства обработки (**даже если формально не храните
> данные у себя**), то вы — оператор персональных данных.»
🔴 **Прямое возражение против идеи «разбор на клиенте снимает статус оператора».**
Формулировка «даже если формально не храните данные у себя» бьёт ровно в нашу схему.

cisoclub.ru, https://cisoclub.ru/model-operator-obrabotchik-personalnyh-dannyh-jekspertnyj-analiz-praktika-i-osobennosti-pravoprimenenija/, **05.11.2025**:
> «российский закон часто оставляет отдельные понятия и роли **не вполне чётко
> определёнными**, что создаёт пространство для различных интерпретаций.»
> «В российском законе ФЗ-152 **отсутствует чёткое определение понятия «обработчик
> персональных данных»**.»

**4. Что суды считают НЕ персональными данными — полезные границы.**
ВС РФ (изложение ЦПО групп, https://pravorf.ru/blog/verhovnyy-sud-otkazalsya-priznat-personalnymi-dannymi-kontakty-litsa-bez-privyazki-k-fio-1, 24.08.2023):
> «ВС РФ согласился… что **сами по себе номер телефона и адрес электронной почты не являются
> персональными данными**, так как они не могут с точностью определить конкретное физическое
> лицо… **Форма не содержит полей для идентификации физического лица, таких как полные ФИО
> или иные реквизиты** (паспортные данные, ИНН, СНИЛС…).»
🔴 Для Г66 это важно наоборот: в выписке **ФИО получателя И телефон СБП стоят рядом**,
то есть ровно та «совокупность», при которой и ВС, и РКН признают ПДн.

IP-адрес, h-cons.ru, https://h-cons.ru/stati/yavlyaetsya-li-ip-adres-personalnymi-dannymi,
**16.09.2026**: «РКН склонен считать связку IP+cookie персональными данными и выносит
предписания. **Суды в большинстве случаев эти предписания отменяют. Но судиться дороже,
чем выполнить требования.**»

**5. Российский аналог «клиентской обработки» с проверкой в DevTools** — ProPDF,
https://propdf.io/ru/blog/pdf-privacy-client-side-processing, **01.05.2026**, по-русски:
> «Обработка на стороне клиента означает, что JavaScript в вашем браузере выполняет всю
> работу. **Ваши файлы никогда не покидают устройство. Сервер доставляет код; ваш компьютер
> его выполняет. Это фундаментальное архитектурное различие, а не просто политика
> конфиденциальности.**»
> «Вы можете убедиться в этом сами. Откройте Инструменты разработчика (F12) и наблюдайте
> за вкладкой «Сеть»…»

**6. Смежное, свежее и с числами:** Хабр, «Вставил договор в ChatGPT — что нарушил.
Разбор по 152-ФЗ с цифрами и делами», https://habr.com/ru/articles/1082750/, **16.09.2026**:
> «Обработка, несовместимая с целью сбора, — это ровно формулировка части 1 [ст. 13.11 КоАП].
> **Юрлицу 150–300 тысяч.**»
> «**27 июля 2026 Бабушкинский районный суд Москвы** признал законным увольнение…
> Формулировка суда: «**выгрузка сведений, составляющих коммерческую тайну, в систему
> искусственного интеллекта DeepSeek является разглашением таких сведений**».»
> «Суд приравнял отправку в нейросеть **к передаче третьему лицу**. Не к «использованию
> инструмента». К передаче.»
> Автор фиксирует отрицательный результат: «**судов по 152-ФЗ из-за нейросетей я не нашёл
> ни одного**… Потому что снаружи это не видно.»

### Вызов 9 — Exa: дословные формулировки политик про «данные не покидают устройство»

🔴 **Найдено ПРЯМОЕ ПРОТИВОРЕЧИЕ между двумя политиками — самая ценная находка блока B.3.**
Два приложения с одинаковой архитектурой (обработка на устройстве) занимают
ПРОТИВОПОЛОЖНЫЕ правовые позиции о том, кто контролёр:

**Flow Recovery, https://www.flowrecovery.app/en-gb/privacy-policy — «мы НЕ контролёр»:**
> «Health and biometric data that Flow Recovery processes on your device is not transmitted
> to our servers for that processing, and we do not access it. **We are not the data
> controller for that on-device processing under applicable data protection law.** The table
> below sets out the legal bases that apply **only to the limited processing where we do
> receive or process personal data**.»
> «Flow Recovery processes all of your health and biometric data **entirely on your device**.
> We do not collect, transmit, store, or have access to your health data on any server.»
> Приём, достойный копирования: таблица «Data Type | **Where It Lives** | **Do We Have
> Access?**», где по каждой строке стоит «Your device only | No», и только у e-mail — «Our
> email service provider | Yes (only your email)».

**NeatPass, https://neatpass.app/privacy — «мы КОНТРОЛЁР, но доступа нет»:**
> «From a GDPR perspective, **we act as controller for this processing because we define
> the purpose and functionality of the App.** However, the personal data contained in your
> tickets **remains exclusively on your device and is not accessible to us.** We do not
> receive, store, or have any means to access your ticket content on our servers.»
> «**The legal basis for this on-device processing is Article 6(1)(b) GDPR**, as it is
> necessary to provide the core functionality of the App that you have requested.»
> Проверяемость: «**You can verify this by using the App offline** — pass creation works
> without any internet connection.»
> 🔴 Гибридная граница, описанная точнее всех: «Your tickets and documents: Processed on your
> device only—content never leaves your device · **Cryptographic hashes for pass signing:
> Transmitted to our signing server (hashes only, no personal content)** · Device identifier
> for security: Transmitted (pseudonymous, **but personal data**) · IP address and request
> metadata: Processed **transiently**.» И честное исключение: «**Bug reports are an exception
> to our general "data never leaves your device" principle.**»

🔴 **Позиция NeatPass ближе к российскому праву**: она совпадает с критерием «определяет
цели и средства» из ст. 3 152-ФЗ и с формулировкой b-152 «даже если формально не храните
данные у себя». Позиция Flow Recovery («мы не контролёр») — более смелая и в РФ,
где нет разделения оператор/обработчик (см. РКН 14.08.2026 выше), выглядит уязвимее.

**Другие рабочие формулировки границы «что остаётся / что уходит»:**

SteadiDay, https://www.steadiday.com/privacy.html — образец перечисления по позициям:
> «**What syncs when signed in:** Medications, tasks, check-ins, and activity summaries…
> **What does not enter account sync:** Apple Health and Health Connect records **other than
> the optional daily step count**, source photos, and insurance card details.»
> «Health data is NEVER uploaded to external servers (**with the exception that daily step
> counts may be included in activity summaries** synced to our servers if you sign in and
> enable activity sharing).»

RepsForReels, https://repsforreels.app/privacy — эталон «наружу уходит одно число»:
> «All of this health data is processed **entirely on your device** to calculate how much
> screen time you've earned. **Only the resulting earned screen-time amount (a number) is
> saved to your account** so your balance syncs… **Your raw health data (calories, steps,
> workouts) never leaves your device** and is never stored on our servers.»
🔴 Это **буквально искомая гибридная схема**: сырьё на устройстве, на сервер — один
производный скаляр. Ровно то, что нужно СППР: на сервере агрегаты/категории, не строки.

Geode, https://geodeclarity.com/privacy/, 11.12.2025 — самая сильная риторика + честная
оговорка о частичной границе:
> «**Policies can change. Physics cannot.** Geode is built so that we cannot access your
> recordings or transcripts. **There is no technical pathway** for your content to leave your
> device.»
> Но тут же: «On Mac, AI summaries are also generated fully on-device; **on other platforms,
> only the text transcript (never the audio) is sent to the cloud** to generate your summary.»

Simple Fitness, https://simplefitness.ai/privacy/ — схема «ключ на устройстве, шифротекст
в облаке» (ровно то, что SEBERD назвал «шифрование с ключом у клиента»):
> «Sensitive fields (such as blood test data) are encrypted using **AES-256-GCM** before
> storage. **Your encryption key is stored securely in the iOS Keychain on your device and
> never leaves your device.**»

Vaulti, https://vaultiapp.com/privacy: «Your entries are stored locally in a **sandboxed
database** on your device… **Other apps cannot access Vaulti's data.**»
ChronoPill, https://chronopill.com/privacy.html, 20.04.2026: «**By default, 100% of your
medication data is stored locally on your iPhone and is never transmitted to our servers.**» ·
«Your Health Profile is Sensitive PI and is used **only on your device — never transmitted,
inferred, profiled, or disclosed**. (CPRA §1798.121)»
Athyx, https://www.athyx.com/privacy: «**On-device processing for camera video and raw sensor
signals, so the most sensitive inputs stay on your phone.**»
WakedUp, https://wakedupprivacy.netlify.app/: «**We do not operate servers that store** your
alarms, missions, photos, streaks, or other personal data.» · «Because personal data is kept
on your device rather than on our servers, **the primary protection of your data is the
security of your own device**.» — честное признание переноса риска на пользователя.

🟡 **Отрицательный результат:** дословных цитат из ПЕРВОИСТОЧНИКОВ Apple (apple.com/legal/
privacy, поддержка Apple Health) и Signal в этой выдаче не оказалось — Exa вернула политики
сторонних приложений, использующих HealthKit. Класс 🟢 (наша недоработка, канал не пройден:
прямой `WebFetch`/браузер по `apple.com/legal/privacy` и `signal.org/legal/` не делался).

### Вызов 10 — Bash `curl` с браузерным UA: Apple Health & Privacy. HTTP 200, 118 826 байт

https://www.apple.com/legal/privacy/data/en/health-app/ — дословно:
> «The Health app is designed to protect your information and **enable you to choose what you
> share**… **You are in control over which data is stored in the Health app and which data is
> shared with third-party apps** and people you [choose].»
> «**When your device is locked with a passcode, Touch ID, or Face ID, all of your health and
> fitness data in the Health app — other than your Medical ID — is encrypted and inaccessible
> by default.**»
> «You can choose to use iCloud to keep your data up to date across your devices, choose to
> back up your data to an **iTunes encrypted backup** on your computer, or choose to share
> your data. The Health app also gives you the ability to **export a copy** of your Health app
> data.»
🔴 Замечание: Apple формулирует не «данные не покидают устройство», а **«вы контролируете,
что именно уходит» + «в покое зашифровано»**. То есть флагман индустрии выбрал НЕ абсолютную
формулировку, а контроль пользователя и шифрование. Для нашей политики это ориентир
осторожности: абсолютное «никогда не покидает» брать только там, где это буквально так.
🟢 Signal (`signal.org/legal/`) в этом заходе не запрашивался — канал не пройден.

---

## Сводка по вопросу A (таблица)

| Продукт | Где разбор | Чем | Лицензия | Живой | Подтверждено кодом? |
|---|---|---|---|---|---|
| **localbankstatementconverter** (PriyanshuDangi) | **браузер** | **Pyodide + pdfminer.six** в Web Worker; таблица — vanilla-JS, 3 уровня (рамки→координаты→текст) | не указана в выдаче (репо открыт) | да | **ДА** — README описывает пайплайн, «there is no backend» |
| **Actual Budget** (`actualbudget/actual`) | **браузер / устройство** (`loot-core` + SQLite в WASM, IndexedDB) | свои парсеры CSV/QIF/OFX/QFX/CAMT в UI-компоненте | **MIT** | да (пуш 21.09.2026) | **ДА** — дока API «server does not have the functionality for analyzing», issue #1085 «import logic is currently in the component», `browser-app-demo` |
| **Firefly III + data-importer** | **свой сервер** (self-hosted PHP), НЕ клиент | CSV, CAMT.052/053; PDF нет | **AGPL-3.0** | да (21–22.09.2026) | ДА — отдельное приложение «separated for security reasons» |
| **hledger / hledger-web** | локальный процесс на машине (веб-UI поверх localhost) | Haskell-парсеры CSV/журнала | **GPL-3.0** | да (22.09.2026, 4714★) | частично (архитектура известна, код не читался) |
| **GnuCash** | **десктоп**, сервера нет | C/C++ импортёры OFX/QIF/CSV (libofx, AqBanking) | GPL-2.0 (API: NOASSERTION) | да (21.09.2026) | частично |
| **Beancount / beancount-import** | **локально** (CLI + локальный web-UI) | Python-импортёры | **GPL-2.0** | да (авг. 2026) | частично |
| **ledger-cli** | **десктоп/CLI** | C++ | NOASSERTION | да (22.09.2026) | частично |
| **Maybe Finance** | — | — | AGPL-3.0 | 🔴 **НЕТ — архив, пуш 24.07.2025** | н/д |
| **StatementSheet** | браузер + узкий канал наружу | не раскрыт | проприетарное | да | НЕТ (только заявление, но заявление детализировано) |
| **AccountantToolkit / Statement2CSV** | **браузер** | **PDF.js**, «positioned text items» | проприетарное | да (30.03.2026) | частично (библиотека названа) |
| **Refinata / SanctumPDF / bankstatementconverter.us.com / freestatementtocsv / StatementSift** | браузер (заявление) | WASM / JS, у одного CSP как гарантия | проприетарные | да | НЕТ — маркетинг, кода нет |
| **SoftZaR** | браузер, но **PDF не разбирает** — просит скопировать текст вручную | regex по вставленному тексту | проприетарное | да | н/д |

**Признанные САМИМИ авторами ограничения клиентской схемы (сводно):**
1. вес рантайма: Pyodide ≈ **10 МБ**, первая загрузка **3–5 с** (localbankstatementconverter);
2. `SharedArrayBuffer` требует **cross-origin isolation** (COOP/COEP), «**cannot be bundled
   away**», это требование к хостингу (Actual);
3. сканы/картинки клиентская схема не берёт — либо просят вставить OCR-текст вручную
   (AccountantToolkit), либо просят явное согласие на облачный OCR (StatementSheet);
4. локальные данные **не зашифрованы** — «We recommend full disk encryption» (Actual);
5. рост фич ломает модель: «If the tool later needs OCR, saved jobs, or institution-specific
   rules, **that is the point to graduate into** Cloudflare Pages Functions or a Worker-backed
   pipeline» (AccountantToolkit) — честное признание предела чистого клиента;
6. «browser may load software and fonts online» (StatementSift) — абсолютного «нуля трафика»
   не бывает, если код приходит из сети.

## Сводка по вопросу B

**B.1 — где отрасль проводит границу (проверяемые образцы):**
- «сырьё на устройстве → наружу один производный скаляр» — RepsForReels («**Only the
  resulting earned screen-time amount (a number) is saved to your account**»);
- «наружу только те строки, что пользователь ВИДИТ, и только по его действию» —
  StatementSheet («only the parsed rows you can see are sent **once**… then discarded»);
- «метаданные без содержания» — StatementSheet («page count, bank label, timestamp, **never
  statement content**»);
- «перечислить пофамильно, что синкается и что НЕ синкается» — SteadiDay;
- «ключ у клиента, шифротекст в облаке» — Simple Fitness (AES-256-GCM + Keychain),
  Actual (E2E, «all your server is doing is passing around changes»);
- «хеши вместо содержимого» — NeatPass (на сервер уходят только криптохеши для подписи);
- проверяемость заявления: DevTools Network (5 продуктов), **CSP как технический запрет
  исходящих** (bankstatementconverter.us.com), работа офлайн (NeatPass, Actual).

**B.2 — Россия. Прямого ответа регулятора НЕТ.** Ни разъяснения РКН, ни судебного акта,
прямо отвечающего «обработка на устройстве пользователя — обработка ли оператором»,
за этот заход не найдено. Найденное — только косвенное, и оно **делится надвое**:
- *против нас*: ст. 3 п. 2 152-ФЗ (оператор = кто определяет цели и средства); b-152
  «**даже если формально не храните данные у себя**, вы — оператор»; ГАРАНТ «то, что действия
  осуществляются автоматически, **не опровергает**»; РКН 14.08.2026 «152-ФЗ **не известно
  разделение на операторов и обработчиков**»; SEBERD «РКН и суды **часто занимают
  расширительную позицию**… могут признать обработкой даже кэширование IP на CDN»;
- *за нас*: А40-12676/2024 (АС МО, 27.03.2025) — критерий автоматизации оценивается по тому,
  **что происходит после сбора**, и бремя доказывания — на РКН; РКН 14.08.2026 про нейросети
  — «**нет, если пользователь самостоятельно передаёт данные**… отношения площадка-пользователь»;
  SEBERD — архитектура «проводник» и «шифрование с ключом у клиента» **меняет правовую
  природу информации в вашей инфраструктуре»**; ВС РФ 2023 — идентификаторы без ФИО не ПДн.
Нормативная рамка для гибрида: **Приказ РКН от 19.06.2025 № 140** (требования и методы
обезличивания, заменил № 996 от 2013) и **ПП РФ от 15.09.2008 № 687** (неавтоматизированная
обработка).

**B.3 — формулировки политик:** см. вызов 9. Ключевое — **противоречие двух позиций**:
Flow Recovery «**We are not the data controller for that on-device processing**» против
NeatPass «**we act as controller… because we define the purpose and functionality of the App**,
however the data remains exclusively on your device». Apple же не использует абсолютную
формулировку вовсе: «you are in control over which data is stored… and which data is shared»
+ шифрование в покое.

## Что осталось недобытым

| Пункт | Класс | Причина |
|---|---|---|
| Разъяснение РКН / судебный акт РФ ПРЯМО про обработку на устройстве пользователя | 🟢 | не пройдены каналы: `pd.rkn.gov.ru`, `rkn.gov.ru` поиском по разъяснениям, `sudact.ru`/`kad.arbitr.ru` по ключевым словам, `zakon.ru`, Digital Rights Center, РАЭК. Возможно, такого документа нет вовсе — но это пока не доказано |
| Signal `signal.org/legal/` — дословные формулировки о локальной обработке | 🟢 | канал не запускался ни разу |
| Чтение исходников Actual (`loot-core`, компонент импорта) построчно | 🟢 | подтверждено докой + issue, но файл/строка не процитированы |
| Лицензия `PriyanshuDangi/localbankstatementconverter` | 🟢 | `api.github.com/repos/.../license` не запрашивался |
| `hledger-web` — чем именно и где разбирает; GnuCash-импортёры по коду | 🟢 | только архитектурное знание, кода не читал |
| Российские браузерные конвертёры выписок (сбербанковские/тинькоффские PDF) | 🟢 | запрос делался только на английском |
| Расширения браузера для разбора выписок (Chrome Web Store) | 🟢 | канал не пройден |
| Открытие любого из 9 конвертёров в браузере и проверка вкладки Network (их же предложение) | 🟢 | браузер не запускался; проверка «заявление или правда» сделана по коду только для двух продуктов |

🔴 Ни одного источника класса «недоступен по вине сайта» не встретилось: все запрошенные
адреса отвечали (единственный не-200 — 301 редирект GitHub API, следствие переименования
репозитория, обошёлся `-L`).


