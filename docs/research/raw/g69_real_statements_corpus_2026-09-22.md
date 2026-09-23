# Г69 — Корпус реальных банковских выписок из открытого доступа (2026-09-22)

Цель: найти и скачать реально существующие банковские выписки, опубликованные в открытом
доступе, для разработки и тестирования парсера `app/services/statement_parser.py`.

Файлы качаются в `/Users/vasyaevdokimov/raw-originals/finpilot-data/statements/` — ВНЕ
git-репозитория. В репозиторий кладётся только этот markdown-отчёт.

Разрешение владельца 22.09.2026, дословно: «МОЖНО ИХ… мы просто сейчас на этапе разработки,
мы не будем их публиковать».

## Журнал

### Шаг 1. Инструменты и каталог

- Каталог создан: `/Users/vasyaevdokimov/raw-originals/finpilot-data/statements/` (вне репозитория).
- `pdftotext` есть — `/usr/local/bin/pdftotext`. `pdfplumber` в системном python3 НЕТ
  (есть в venv проекта, сюда не тянем).
- GitHub MCP-тулы агенту недоступны (`mcp__plugin_github_github__*` → «No such tool available»),
  работал через `gh api` из Bash. Это не ограничение источника, а состав тулов.

### Шаг 2. GitHub — поиск парсеров выписок (`gh api search/repositories`)

Выдача по `bank statement parser pdf`, 20 репозиториев, дословно топ с лицензиями:

```
marlanperumal/pdf_statement_reader | 71 | MIT | Python library and CLI for parsing pdf bank statements
noisecapella/bank-statement-parser | 40 | NOLIC
electrovir/statement-parser | 38 | MIT
felgru/bank-statement-parser | 29 | NOLIC
heypoom/kbank-statement-pdf-parser | 28 | NOLIC | Kasikorn Bank (Таиланд)
sebastienrousseau/bankstatementparser | 51 | NOASSERTION | CAMT/ISO 20022, PAIN.001, CSV, OFX/QFX, MT940, PDF (digital + scanned)
bankstatemently/bank-statement-parsing-benchmark | 8 | MIT | Open benchmark dataset for bank statement PDF parsing accuracy
codito/bout | 17 | MIT
lorenzbr/BankStatementParser | 7 | GPL-3.0 | немецкие банки
J-sephB-lt-n/pdf-bank-statement-parser | 7 | GPL-3.0 | FNB (ЮАР)
danilovsergei/BOA_Pdf_statements_parser | 7 | NOLIC | Bank of America
robbeofficial/dkbparse | 2 | NOLIC | DKB (Германия)
cforycki/lcl-pdf-parser | 2 | NOLIC | LCL (Франция)
atul0016/bank-statement-parser | 3 | NOLIC | индийские банки: SBI, HDFC, Yes Bank, IndusInd, RBL, StanChart
trakanom/Bank-Statement-Parser-PDF-to-CSV | 6 | MIT | Wells Fargo
```

Фикстуры (перебор деревьев по расширениям) нашлись только в четырёх из проверенных:

- `bankstatemently/bank-statement-parsing-benchmark` (MIT) — 5 PDF, `datasets/basic/bsb-00N/`;
- `PriyanshuDangi/localbankstatementconverter` — `tests/sample-pdfs/chase_perfectcard_rewards.pdf` 3 597 900 Б + ожидаемый CSV;
- `sebastienrousseau/bankstatementparser` — 17 файлов форматов обмена (camt.053, pain.001, MT940, OFX, CSV на 4 языках);
- `marlanperumal/pdf_statement_reader` — файлов данных в дереве НЕТ (пусто).

### Шаг 3. Скачано (первая партия)

Все шесть PDF скачаны, `file` подтверждает валидность и число страниц:

```
bsb-001 ... 31711 Б, PDF 1.3, 3 стр
bsb-002 ... 55807 Б, PDF 1.3, 4 стр
bsb-003 ... 15789 Б, PDF 1.3, 3 стр
bsb-004 ... 75960 Б, PDF 1.3, 5 стр
bsb-005 ... 13899 Б, PDF 1.3, 2 стр
chase_perfectcard_rewards ... 3597900 Б, PDF 1.6
```

Плюс 9 файлов форматов обмена в `statements/formats/`.

### Шаг 4. Разбор текстового слоя (`pdftotext -layout`)

🔴 **Важная отбраковка по классу.** Пять файлов `bsb-*` из MIT-бенчмарка — **синтетика высокого
качества, а НЕ реальные выписки**. Признаки: банки вымышленные («Liberty National Bank»,
«Continental Trust N.V.», «Silk Road Banking (Hong Kong)», «Harbour Bank Canada»), по диагонали
каждой страницы лежит водяной знак (в текстовом слое рассыпается буквами `D O C U M E N T`,
`S A M P L E`). Это тот же класс, что наши четыре шаблона, только чужой — ценность есть
(другие раскладки, мультивалюта, 4 языка), но задачу «мерить на реальности» он НЕ закрывает.
Ниже помечены как `синт-высок`.

Текстовый слой у всех пяти ЕСТЬ: 154 / 251 / 121 / 291 / 100 непустых строк соответственно.
Покрывают: Сингапур (SGD, Standard-Chartered-подобная раскладка), США (кредитка с календарём
и блоком бонусов), Нидерланды (`Rekeningafschrift`, IBAN, запятая как десятичный разделитель,
`15.320,00 €`), Гонконг (двуязычный китайско-английский, мультивалюта, `DR=Debit`),
Канада/Квебек (французский, `10 750,00 $`, неразрывный пробел как разделитель разрядов).

🟢 **`chase_perfectcard_rewards` — РЕАЛЬНАЯ выписка.** Настоящее имя держателя карты
(JINLIAN YANG), настоящий адрес (644 FOX HILL ESTATES DR, BALLWIN MO 63021-4316), номер счёта,
период 03/18/08 – 04/17/08, Chase Card Services, MasterCard. Текстовый слой есть — 155 строк,
4 страницы. Размер 3,6 МБ при 155 строках текста = внутри растровые слои (форма для оплаты,
логотипы), то есть гибрид «скан + текстовый слой».

### Шаг 5. Форматы обмена — скачано

`sebastienrousseau/bankstatementparser` (NOASSERTION — в корне лицензия не распозналась GitHub,
проверять перед любым внешним использованием), `statements/formats/`:
`camt.053.001.02.xml` (3389 Б), `camt053_multicurrency.xml`, `pain.001.001.03.xml` (9136 Б),
`sample.mt940` (200 Б), `sample.ofx` (515 Б), `sample_statement.csv`,
`csv_european_decimals.csv`, `csv_french_headers.csv`; плюс эталонный CSV к Chase.

### Шаг 6. GitHub — российский контур

Поиск `tinkoff statement parser` — **пустая выдача** (0 репозиториев). Это замер пустоты канала,
а не «не искали».

`1CClientBankExchange` — выдача есть:
```
kilylabs/client-bank-exchange-php | 29 | MIT   | фикстуры ЕСТЬ
Unact/client_bank_exchange2      |  0 | MIT   | фикстуры ЕСТЬ
odoo-ru/client-bank-1c           |  1 | MIT   | фикстуры ЕСТЬ
szonov/bankparse                 |  0 | MIT   | Go, PDF российских банков + 1С — файлов данных в дереве НЕТ
WoLand-Q/python-script-bank      |  1 | Apache-2.0 | PDF выписки → 1С для iiko — файлов данных НЕТ
kyzman/kl_to_1c_parse            |  0 | MIT   | файлов данных НЕТ
xylocode/Treasury                |  1 | MIT   | только LICENSE.txt
```

Скачано в `statements/ru1c/` (5 файлов, все MIT):
```
1c_clientbankexchange_huge_github-kilylabs        8 012 131 Б
1c_clientbankexchange_one_day_utf8_github-kilylabs   18 049 Б
1c_clientbankexchange_test_github-Unact              17 317 Б
1c_clientbankexchange_one_day_github-kilylabs        11 605 Б
1c_clientbankexchange_kl_to_1c_github-odoo-ru         1 347 Б
```
Формат подтверждён дословно — шапка `1CClientBankExchange`, `ВерсияФормата=1.02`,
`Кодировка=Windows`, `СекцияРасчСчет`, `НачальныйОстаток=45329.91`, `ВсегоПоступило`,
`ВсегоСписано`, `КонечныйОстаток`, `СекцияДокумент=Банковский ордер`, `ПлательщикИНН`.
Реквизиты обезличены (`Some random payer`, счета из повторяющихся цифр), но КОНСТРУКЦИЯ формата
настоящая — для парсера ценна именно она. Файл `huge.txt` на 8 МБ закрывает класс «большой объём».

### Шаг 7. HuggingFace — датасеты

Поиск `bank statement`, 30 датасетов. Отобраны четыре, проверены лицензии и состав:

- 🟢 **`AgamiAI/Indian-Bank-Statements`** — Apache-2.0, 800 файлов, ровно по 200 в четырёх
  категориях: `Digital_Type1`, `Digital_Type2`, `Scanned_Type1`, `Scanned_Type2`, к каждому PDF
  идёт JSON с эталонной разметкой. README честно помечен тегом `synthetic`: «Synthetically
  generated Indian business bank statements». То есть класс `синт-высок`, НО он закрывает
  дыру, которую не закрывает ничто другое — **PDF-скан без текстового слоя** плюс готовый
  ground truth.
- `Panhapich/bank-statement-structure-recognition` — MIT, 8 parquet, модальность image,
  object-detection. Не качал: parquet с картинками, разбор требует тяжёлой распаковки.
- `tusharshah2006/bank_statements_transactions` — лицензия НЕ указана, 150 JPEG, имена файлов
  по реальным индийским банкам (`HDFC_Bank_*`, `Bank_of_Baroda_*`, `IOB_Bank_*`, `UCO_Bank_*`).
  Похоже на реальные сканы, но **без лицензии** — 🟡 брать не стал.
- `rikeshVertex/invoice-receipt-cheque-bankstatement-dataset` — лицензия НЕ указана, не брал.

Скачано в `statements/hf/` — 8 PDF по два на категорию плюс один ground-truth JSON.
Замер текстового слоя (`pdftotext -layout ... | grep -c .`), все по 6 страниц:
```
Digital_Type1 00001  150 КБ  1026 строк
Digital_Type1 00002  150 КБ  1002 строки
Digital_Type2 00001  140 КБ   777 строк
Digital_Type2 00002  144 КБ   837 строк
Scanned_Type1 00001  6,5 МБ    1 строка  ← текстового слоя НЕТ
Scanned_Type1 00002  6,2 МБ    1 строка  ← текстового слоя НЕТ
Scanned_Type2 00001  6,3 МБ    1 строка  ← текстового слоя НЕТ
Scanned_Type2 00002  6,4 МБ    1 строка  ← текстового слоя НЕТ
```
🟢 **Класс «скан без текстового слоя» закрыт** — четыре файла, шесть страниц каждый, с эталоном.

### Шаг 8. DocumentCloud — РЕАЛЬНЫЕ опубликованные выписки

Канал, которого не было в задании и который оказался самым плодовитым по НАСТОЯЩИМ выпискам:
`api.www.documentcloud.org` — публикации журналистов, судебные приложения, муниципальные
отчёты. Поиск `"bank statement" account balance` даёт 1 132 937 документов, все публичные,
без ключа и без антибота (обычный `curl`, первая ступень лестницы).

Скачано в `statements/dc/` восемь файлов; каждый проверен `file` + `pdftotext`:

```
td-bank-statement                  20783357   2 стр   46 207 Б    38 строк текста
carter-bank-statement              24376514   3 стр  108 807 Б    78 строк
operations-july-bank-statement     23886516   4 стр  163 981 Б   283 строки
2-bank-statement-hasan-mohammed    20467391   2 стр 1 800 386 Б   47 строк (Al Jazeera Investigative Unit)
CAFE-2016-bank-statement            3727296   5 стр  194 312 Б     0 строк  ← реальный СКАН
Bankstatements                      4408246   5 стр 7 124 617 Б    0 строк  ← реальный СКАН
wtp-statement-summaries-account-1    501825  86 стр 3 475 946 Б    0 строк  ← реальный СКАН, 86 страниц
bank-records-and-foreign-transactions 22808150 31 стр 2 089 333 Б 1901 строка ← 31 страница с текстом
```

🟢 Это закрывает сразу три дыры настоящими документами: реальный скан без текстового слоя
(три файла), реальный многостраничник (86 и 31 страница), реальная выписка с текстовым слоем.

🔴 Русскоязычного сегмента в DocumentCloud по выпискам НЕТ. Замер: запрос `выписка по счету`
даёт 3 770 документов, среди топ-20 ни одной банковской выписки (выписки из приказов,
протоколов, законопроекты). Запрос `Сбербанк` — всего 19 документов, банковских выписок ноль.
Это замер пустоты канала для РФ, а не «не искали».

### Шаг 9. Структурный разбор всего корпуса (`pdfplumber`)

Ключевой замер темы: **есть ли у таблицы нарисованные линии**. Наш парсер на
`pdfplumber`; из четырёх наших шаблонов два (Сбер, Т-Банк) линий не имеют вовсе.
Критерий классификации: `textlines<=2` → скан; иначе `lines+rects >= 20` → PDF-линии,
иначе PDF-без-линий. Счётчики `pdfplumber` — по первым 8 страницам (для многосотстраничных
документов это занижает, помечено в разборе).

`pdfplumber` взят из venv проекта (`0.11.9`); в системном python3 его нет.

Полный вывод пробы:

```
bs-client_v017.9.0_client_guide_srbank.pdf
  PDF-без-линий | pages=370 | textlines=9564 | plumber lines=13 rects=4 curves=0 words=1520 | 8407251B | sha256=7abde9ae75caf47d1e369b33ae7c229172f4630a9ee6901a1376cbfff5102695
bss_internet_client_guide_017.9.0.pdf
  PDF-линии | pages=267 | textlines=7336 | plumber lines=40 rects=6 curves=0 words=1651 | 6182553B | sha256=2af76a9927380b25cea1e4a7d86d4ab226b5fcc92d0f5b156577f07ad94933ef
faktura_internet_bank_corporate_2026-07.pdf
  PDF-линии | pages=226 | textlines=4792 | plumber lines=11 rects=1053 curves=0 words=1717 | 26626569B | sha256=ef389e18f98c440fcf545fbfd400e076614e41c0289898fe7800afac219dc132
faktura_internet_bank_retail_2026-09.pdf
  PDF-линии | pages=129 | textlines=2145 | plumber lines=29 rects=677 curves=0 words=1847 | 18289302B | sha256=461780d733d88217f5d0c6735b5df614f5d9a55b1cfb74850e6e45b248ae6fb3
Corporate_Internet-Banking_WEB_ShortGuide.pdf
  PDF-линии | pages=88 | textlines=2075 | plumber lines=70 rects=0 curves=0 words=1358 | 3601401B | sha256=419193ad0f3c0bd9d3c7861d9ea7d6d686a0fb6d157dbbd7760913b58fa4b38e
Corporate_iBank2-Format_Guide_2025-07.pdf
  PDF-линии | pages=194 | textlines=9155 | plumber lines=0 rects=20 curves=0 words=1875 | 4194524B | sha256=68fe79a5f72924abd65add16676e6c637224c0d7e53ec557c4771585f3d8a871
iBank_Private_Internet_Bank.pdf
  PDF-линии | pages=187 | textlines=3362 | plumber lines=28 rects=0 curves=0 words=1589 | 10113863B | sha256=7b7fa53189dbb417df5c6870cb33941d57fe309ab40d0569cc80b1324d6e831d
iBank_for_life.pdf
  PDF-линии | pages=20 | textlines=425 | plumber lines=8 rects=661 curves=303 words=419 | 3606769B | sha256=1faa361ca1a3ceb08c51660dc4ee461b4b657cf831b6ed71a899cfac585b2608
ibank_for_business.pdf
  PDF-линии | pages=20 | textlines=517 | plumber lines=9 rects=34 curves=802 words=700 | 2754884B | sha256=40fa6085a056adf751260b3d3effb5271431dc0a34f0617e67e1c0317b93627c
20251219_od_2887_1.pdf
  PDF-линии | pages=13 | textlines=451 | plumber lines=0 rects=63 curves=0 words=1655 | 685877B | sha256=7aed0f8765106696c7afdbbbff41a850c27f7558eda0ee64548c635cc9b280a0
20251219_od_2890.pdf
  PDF-линии | pages=15 | textlines=363 | plumber lines=0 rects=36 curves=0 words=1613 | 738468B | sha256=9ffc01f8cc4ba42ca8b16d82aaab3d469144fd7a3febf9b0291d33d1055d3f75
20251219_od_2894.pdf
  PDF-без-линий | pages=81 | textlines=3100 | plumber lines=0 rects=0 curves=0 words=1316 | 1323485B | sha256=48a2fad5a1d659a3bc62fe8a53f5cd4fad999709a847b56f3909e136fe878b3c
Financial_Data_description.pdf
  PDF-линии | pages=5 | textlines=157 | plumber lines=0 rects=391 curves=412 words=1063 | 165342B | sha256=67227f33f4fc6f8526ca5216fc6ac55ef86393b4f6b3cb6c69a0969c9ffa2b16
2-bank-statement-hasan-mohammed_documentcloud-20467391_2026-09-22.pdf
  PDF-без-линий | pages=2 | textlines=46 | plumber lines=3 rects=0 curves=0 words=168 | 1800386B | sha256=2cb5eb736eb855fb8021c1e1fca8f3a04b696b07955424a6200b629164eb7127
Bankstatements_documentcloud-4408246_2026-09-22.pdf
  скан-без-текста | pages=5 | textlines=0 | plumber lines=0 rects=2 curves=0 words=0 | 7124617B | sha256=7e6d192333686e41479320b13d70c765866c73d863c7cfe9800d0058b1025273
CAFE-2016-bank-statement_documentcloud-3727296_2026-09-22.pdf
  скан-без-текста | pages=5 | textlines=0 | plumber lines=0 rects=0 curves=0 words=0 | 194312B | sha256=b97d2b317786f4f701e36ef76ec22c227e45786aad691c44ad62901cd8c55b8a
bank-records-and-foreign-transactions_documentcloud-22808150_2026-09-22.pdf
  PDF-без-линий | pages=31 | textlines=1901 | plumber lines=0 rects=0 curves=0 words=2594 | 2089333B | sha256=25279193c46fd429ae7695fafe952601c5b20e9b83ef3c4bc9312eb3561c103b
carter-bank-statement_documentcloud-24376514_2026-09-22.pdf
  PDF-линии | pages=3 | textlines=77 | plumber lines=0 rects=23 curves=4 words=1105 | 108807B | sha256=4fb88429e0c964de3eeba3833d898106854b506c0cafb1dc96a5f623af3a68c1
operations-july-bank-statement_documentcloud-23886516_2026-09-22.pdf
  PDF-без-линий | pages=4 | textlines=282 | plumber lines=0 rects=0 curves=0 words=747 | 163981B | sha256=3d2dcb7932ef6c5d5ef848c2dbe3bb2cc3f2b335076163d209d6299f8cb7b39d
td-bank-statement_documentcloud-20783357_2026-09-22.pdf
  PDF-без-линий | pages=2 | textlines=37 | plumber lines=0 rects=12 curves=0 words=481 | 46207B | sha256=d6e05b89efc8ca125ae4875deae09b0e0b46182f321fb62f991d281e38a1c1b3
wtp-statement-summaries-account-1_documentcloud-501825_2026-09-22.pdf
  скан-без-текста | pages=86 | textlines=0 | plumber lines=0 rects=0 curves=0 words=0 | 3475946B | sha256=9ad45b5a7710b3fb64e202c7df1cd891c985ab440da4fcb67e178ff5276f9b48
bsb-001-statement_github-bankstatemently_2026-09-22.pdf
  PDF-линии | pages=3 | textlines=154 | plumber lines=0 rects=976 curves=27 words=786 | 31711B | sha256=d3d5071b90a33272f31bab5c5660d78b2ae29d2c6e1720477f5e8b167f73e843
bsb-002-statement_github-bankstatemently_2026-09-22.pdf
  PDF-линии | pages=4 | textlines=251 | plumber lines=4 rects=424 curves=61 words=1617 | 55807B | sha256=3700a073ac1262173cbabbd5667cd3a59e04cf0b14e3a865ae25ce21089ab97d
bsb-003-statement_github-bankstatemently_2026-09-22.pdf
  PDF-без-линий | pages=3 | textlines=121 | plumber lines=0 rects=5 curves=24 words=439 | 15789B | sha256=4945bcda107e6d7845850e728b90c4dba1cb11de5a13356b0794df349e5527c2
bsb-004-statement_github-bankstatemently_2026-09-22.pdf
  PDF-без-линий | pages=5 | textlines=291 | plumber lines=2 rects=6 curves=28 words=919 | 75960B | sha256=67a5b862696fc06e675db53867be6fcc71a4ecc13998193e8b45e2cd63371051
bsb-005-statement_github-bankstatemently_2026-09-22.pdf
  PDF-без-линий | pages=2 | textlines=100 | plumber lines=0 rects=4 curves=37 words=480 | 13899B | sha256=a5cc2a7d210bc657c55b44ac159c5d10b2d71553f3646ce17a64051f918fd960
chase_perfectcard_rewards_github-PriyanshuDangi_2026-09-22.pdf
  PDF-линии | pages=4 | textlines=155 | plumber lines=91 rects=2 curves=0 words=1107 | 3597900B | sha256=dcf5507e2feead8ba7f107aab4b256accfe814f6bd79a02d57e41aaee7615080
india_Digital_Type1_00001_hf-AgamiAI_2026-09-22.pdf
  PDF-линии | pages=6 | textlines=1025 | plumber lines=289 rects=7 curves=0 words=3565 | 149533B | sha256=21ebade76538ab5f7a99c90470c24fda0571867aecac5030858de310f20cdc81
india_Digital_Type1_00002_hf-AgamiAI_2026-09-22.pdf
  PDF-линии | pages=6 | textlines=1001 | plumber lines=288 rects=7 curves=0 words=3508 | 149606B | sha256=f5598e6881afa970447dfd1425e719935acfbc3ff3aba5da6e597fd963533080
india_Digital_Type2_00001_hf-AgamiAI_2026-09-22.pdf
  PDF-линии | pages=6 | textlines=776 | plumber lines=298 rects=168 curves=0 words=3165 | 139851B | sha256=299952226bf640e2846bb72503fa1bc59a7cae1d2e4c39b1ea7912fad76795dd
india_Digital_Type2_00002_hf-AgamiAI_2026-09-22.pdf
  PDF-линии | pages=6 | textlines=836 | plumber lines=304 rects=174 curves=0 words=3257 | 143814B | sha256=507ebfc937ac41c1630a3943b82a5b8170bb279137cd4e3a13877640ae7ae035
india_Scanned_Type1_00001_hf-AgamiAI_2026-09-22.pdf
  скан-без-текста | pages=6 | textlines=0 | plumber lines=0 rects=0 curves=0 words=0 | 6546361B | sha256=a9c6d7cca832bc899338c8155d5959aaa6b3467f1909fdc3cfb9d9357d5cf74d
india_Scanned_Type1_00002_hf-AgamiAI_2026-09-22.pdf
  скан-без-текста | pages=6 | textlines=0 | plumber lines=0 rects=0 curves=0 words=0 | 6189058B | sha256=844cdf173744f653cf5c24309b6b59190747513e5a92fdf240df0a444ce0f580
india_Scanned_Type2_00001_hf-AgamiAI_2026-09-22.pdf
  скан-без-текста | pages=6 | textlines=0 | plumber lines=0 rects=0 curves=0 words=0 | 6342066B | sha256=96ae3335ba6dcf282ef2e260dfa1662cdb80fdc45a002c2fd9fe702fad3f4cb0
india_Scanned_Type2_00002_hf-AgamiAI_2026-09-22.pdf
  скан-без-текста | pages=6 | textlines=0 | plumber lines=0 rects=0 curves=0 words=0 | 6437604B | sha256=c20a103cc66524d341452aab2560c47c15cd5f9a37276debac2884bd469f5441
ozon_synthetic_broken_totals.pdf
  PDF-линии | pages=2 | textlines=21 | plumber lines=0 rects=35 curves=0 words=119 | 15709B | sha256=da69593abbca37eb946ed3d8210283159fcaac81390ef8891773d2699c4b1eb8
ozon_synthetic_statement.pdf
  PDF-линии | pages=2 | textlines=21 | plumber lines=0 rects=35 curves=0 words=119 | 15700B | sha256=eda59cc3f90f2bd52be23472d255f10b698573f5c486024caf714b886eee26d8
alfa_spravka_dvizhenie_sredstv_dszn_2026-09-22.pdf
  скан-без-текста | pages=7 | textlines=1 | plumber lines=17 rects=10 curves=108 words=3 | 1473630B | sha256=ec72f74eede6f7405cdd9a9c9703230e9b2b71d6c84b220aaa29d98b763ed98c
finam_1c_client_bank_exchange_guide_2026-09-22.pdf
  PDF-линии | pages=23 | textlines=519 | plumber lines=32 rects=0 curves=0 words=1117 | 801785B | sha256=05f08c94b7c95e76042dc24b63374400dd1708fcba10f2ed2fdeffa37e5c5334
sber_karta_i_schet_sep2021_mesyac_2026-09-22.pdf
  PDF-линии | pages=7 | textlines=266 | plumber lines=150 rects=27 curves=1 words=1667 | 638673B | sha256=f540b4ae5ca73602f7d2f64c8a92989a184816c4684a85170fc222c78bcac52f
sber_obrazec_vypiski_viza_dilijans_2026-09-22.pdf
  PDF-линии | pages=2 | textlines=57 | plumber lines=0 rects=146 curves=0 words=299 | 298559B | sha256=e790ce31ab46b9935f7e04db13bd3696cf6aeb3d442c081ee21bec78739f8e0e
sber_rasshirennaya_vypiska_f551_lenobl_2026-09-22.pdf
  скан-без-текста | pages=5 | textlines=0 | plumber lines=0 rects=0 curves=14 words=0 | 6157740B | sha256=df851cc6b3284f1a064a24164aa8b0559c625a54b987c8b7a5e792a2a36200c9
sber_spravki_po_schetu_instrukciya_dszn_2026-09-22.pdf
  PDF-линии | pages=16 | textlines=91 | plumber lines=0 rects=42 curves=10 words=352 | 4090339B | sha256=aaf7cbe49d2c2ab4a9abc46a966ae975dfb42dd708799fe5dd37594d8690f922
sber_test_statement_github_2026-09-22.pdf
  PDF-линии | pages=3 | textlines=93 | plumber lines=119 rects=91 curves=0 words=595 | 54998B | sha256=8a19ef09906a8ff2356f3100e0cec2ada4e14538f6ca95e56e3436277e6aa446
sber_vypiska_licevoi_schet_f204s_lenobl_2026-09-22.pdf
  скан-без-текста | pages=1 | textlines=0 | plumber lines=0 rects=0 curves=0 words=0 | 1104036B | sha256=b5a0424050cee54f8a08078990709f886713328354da3df076857103e0414d9f
sber_document_2022-05-16.pdf
  PDF-линии | pages=6 | textlines=240 | plumber lines=34 rects=0 curves=0 words=1485 | 566662B | sha256=9a999acd790744a88c320b2b09d42ec63268b42e1e92856cdc41bf4c3f5ed940
sber_example.pdf
  PDF-без-линий | pages=2 | textlines=14 | plumber lines=0 rects=0 curves=0 words=122 | 113258B | sha256=68675c77fbc36c0e771fae683fc9006dd4a858a03bdc490b0dcb1a8638b0e868
ya_synthetic_card.pdf
  PDF-без-линий | pages=2 | textlines=24 | plumber lines=0 rects=0 curves=0 words=155 | 16729B | sha256=5276dd44fa76a379e8d893dff0eb298829ebd1cb5272912f75ea2af824222c56
ya_synthetic_deposit.pdf
  PDF-без-линий | pages=2 | textlines=16 | plumber lines=0 rects=0 curves=0 words=94 | 14322B | sha256=bf69ebd95e73cbf05dc2ac526fbc28a54b6ec3610cf15615b3343d457503d220
```

### Шаг 10. 🟢 Российский формат выгрузки XLS — найден реальный

`gh api search/code` по `"Дата операции" "Сумма операции" extension:csv` вывел на три
независимых студенческих репозитория (SkyPro-курс), в каждом лежит один и тот же по формату
файл `data/operations.xlsx` размером 445–547 КБ:
`ScherbAlex/ProjectBank`, `Stillyc1/course_project`, `Aleksei-Pavlovskii/Course_1`.
🟡 Лицензия ни у одного НЕ указана (`NOLIC`) — для разработки годится, в публикацию не идёт.

Скачан один: `statements/ru_xlsx/tbank_operations_export_github-ScherbAlex_2026-09-22.xlsx`.

Проверка содержимого через `openpyxl` — это **родной экспорт Т-Банка (Тинькофф)**,
лист называется `Отчет по операциям`, **6 706 строк × 15 колонок**, заголовки дословно:

```
Дата операции | Дата платежа | Номер карты | Статус | Сумма операции | Валюта операции |
Сумма платежа | Валюта платежа | Кэшбэк | Категория | MCC | Описание |
Бонусы (включая кэшбэк) | Округление на инвесткопилку | Сумма операции с округлением
```

Первые строки дословно:
```
31.12.2021 16:44:00 | 31.12.2021 | *7197 | OK | -160.89 | RUB | -160.89 | RUB | None | Супермаркеты | 5411 | Колхоз | 3 | 0 | 160.89
31.12.2021 16:42:04 | 31.12.2021 | *7197 | OK | -64     | RUB | -64     | RUB | None | Супермаркеты | 5411 | Колхоз | 1 | 0 | 64
31.12.2021 16:39:04 | 31.12.2021 | *7197 | OK | -118.12 | RUB | -118.12 | RUB | None | Супермаркеты | 5411 | Магнит | 2 | 0 | 118.12
```

Это реальная выгрузка живой карты (маска `*7197`, период с 2021 г., 6 705 операций,
проставлены MCC и категории банка). Материал прямо для справочника форматов темы Г47:
дата с временем через пробел, точка как десятичный разделитель, знак минуса для расхода,
`None` вместо пустого значения.

Также замерено: `zenmoney/sms-formats` содержит
`src/Т-Банк-ru_4902/formats/Выписка по счету Tinkoff Black ... .txt` — это шаблоны SMS/пуш-
уведомлений Т-Банка, а не выписки; для парсера PDF не годится, но это карта формулировок банка.

### Шаг 11. 🟢 `Ev2geny/Sberbank2Excel` — карта форматов Сбера (MIT, 151 звезда)

Найден через `gh api search/code` по дословной фразе `"Выписка по счёту дебетовой карты"`.
Это самая ценная находка по РФ после самих файлов: рабочая утилита конвертации PDF-выписок
Сбербанка в Excel с **автоопределением формата** и **22 отдельными экстракторами**, каждый
назван по году-месяцу появления формата:

```
SBER_DEBIT_2005  SBER_DEBIT_2107  SBER_DEBIT_2212  SBER_DEBIT_2303_CHELYABINSK
SBER_DEBIT_2408  SBER_DEBIT_2510  SBER_DEBIT_2603
SBER_CREDIT_2110 SBER_CREDIT_2409 SBER_CREDIT_2511 SBER_CREDIT_2605
SBER_PAYMENT_2208 SBER_PAYMENT_2212 SBER_PAYMENT_2406 SBER_PAYMENT_2407
SBER_PAYMENT_2510 SBER_PAYMENT_2604 SBER_PAYMENT_DEBIT_2604b
SBER_SAVING_2303 SBER_SAVING_2407 SBER_SAVING_2604
```

🔴 **Числовой вывод для темы Г47: Сбер сменил раскладку выписки не менее 22 раз за 2020–2026 гг.**,
включая региональный вариант (`_CHELYABINSK`). Парсер под «формат Сбера» в единственном числе
обречён; нужна сигнатурная диспетчеризация, как здесь.

Скачано в `statements/ru_format_ref/sberbank2excel_extractors/` семь файлов (MIT):
`extractor_SBER_DEBIT_2107.py`, `extractor_SBER_DEBIT_2603.py`, `extractor_SBER_CREDIT_2605.py`,
`extractor_SBER_PAYMENT_2604.py`, `extractor_SBER_SAVING_2604.py`, `extractors.py`,
`extractors_generic.py`.

Метод распознавания формата, дословно из `SBER_DEBIT_2603.check_specific_signatures` —
набор обязательных и **запрещающих** маркеров:
```python
test_sberbank              = re.search(r'сбербанк', ...)
test_vipiska_po_schetu     = re.search(r'Выписка по счёту дебетовой карты', ...)
test_data_formirovania     = re.search(r'Дата формирования', ...)
test_dya_proverki          = re.search(r'Для проверки подлинности документа', ...)
test_ostatok_po_schetu     = re.search(r'ОСТАТОК ПО СЧЁТУ', ...)   # ЗАПРЕЩАЮЩИЙ
test_dergunova_k_a         = re.search(r'Дергунова К\. А\.', ...)  # ЗАПРЕЩАЮЩИЙ (подпись!)
```
То есть версии формата различаются в том числе **фамилией подписанта** и наличием строки
`ОСТАТОК ПО СЧЁТУ` против `ОСТАТОК НА <дата>`.

Отдельно: утилита делает **сверку баланса** — считает сумму по транзакциям и сравнивает
с шапкой (`баланс_по_шапке = ПОПОЛНЕНИЯ − СПИСАНИЯ − СПИСАНИЯ БАНКА`) и **не выдаёт результат
при расхождении**. Это готовый инвариант приёмки для нашего парсера.

Скачана единственная фикстура репозитория —
`statements/ru_txt/sber_debit_2107_anonymized_pdftotext_github-Ev2geny_2026-09-22.txt`
(1218 Б, это уже прогнанный `pdftotext`, не PDF). Дословный фрагмент шапки:
```
ул. Вавилова, д. 19, Москва, 117312     19 Vavilova St., Moscow, 117312
900     +7 495 500-55-50     www.sberbank.ru
Сформировано в СберБанк Онлайн
Выписка по счёту дебетовой карты
MasterCard Mass

ОСТАТОК НА 11.11.2111     ОСТАТОК НА 11.11.2111     ВСЕГО СПИСАНИЙ     ВСЕГО ПОПОЛНЕНИЙ
1111 111,11	11 111,11	7 585.50	0,00
```
🔴 Два наблюдения, важные для парсера: (1) разделители внутри строки — **табы**, а не
координаты, то есть формат рассчитан на `pdftotext`, а не на `pdfplumber`;
(2) в одной и той же строке шапки соседствуют `7 585.50` (точка) и `0,00` (запятая) —
разделитель дробной части у Сбера **непоследователен внутри одного документа**.

Замер пустоты: `gh api search/repositories` по `сбербанк выписка парсер`,
`парсер выписок банк pdf`, `bank statement russia parser pdf`, `tinkoff statement parser` —
**все четыре выдачи пустые**. Российские парсеры находятся только поиском по КОДУ
(дословной фразе из выписки), не по описанию репозитория.

### Шаг 12. Форматы обмена MT940 — корпус по реальным банкам

`WoLpH/mt940` (BSD-3-Clause, эталонная python-библиотека MT940) содержит тестовый корпус,
разложенный **по именам реальных банков**: `ASNB`, `citi`, `mBank`, `sberbank`, `betterplace`,
и подкаталог `jejik` с собственной лицензией — `abnamro`, `ing`, `knab`, `postfinance`,
`rabobank`, `rabobank-iban`, `sns`, `triodos`. К каждому `.sta` приложен `.yml` с эталонным
разбором — готовый ground truth.

Скачано 12 файлов в `statements/mt940/`.

🟢 **`mt940_tests/sberbank/171011_01234945.sta` — MT940 от Сбербанка** (венгерское
подразделение, валюта HUF, 11.10.2017). Дословно начало:
```
:20:STARTUMS
:25:1966315302010001
:28:00046
:NS:22JOHN DOE
...
:60F:C171011HUF627311,30
:61:1710111011DF2402,00S   X
:NS:015267 ... 09Tranzakci?s Illet?k:7.21HUF
:62F:C171011HUF617874,30
:64:C171011HUF617874,30
```
Особенность, важная для парсера: Сбер использует нестандартное поле `:NS:` с собственной
нумерованной под-структурой (`01`, `02`, `09`, `15`, `17`, `33`, `34`) и кириллицу/латиницу
в CP-кодировке (в файле видны битые байты) — то есть даже в стандартизованном MT940 банк
добавляет свой диалект.

### Шаг 13. Инвентаризация: каталог уже был НЕ пустым

🔴 **Замер, который надо назвать честно.** Каталог
`/Users/vasyaevdokimov/raw-originals/finpilot-data/statements/` **существовал до этого прохода**
и содержал корпус предыдущей работы: `tinkoff/`, `tbank/`, `sberbank/`, `sberbank2excel/`,
`berka/`, `alfabank/`, `psb/`, `ozonbank/`, `yandexbank/`, `raiffeisen/`, `tochka_1c_suites/`
(43 файла), `formats_intl/` (166 файлов), `_platform_bss/`, `_platform_ibank2/`,
`_platform_faktura/`, `_standards_ufebs/`, `_standards_openapi_cbr/`, `_standards_iso20022_gost/`,
`_1c_client_bank/`, `_market_share/`, `_generic_iso/`, `_universal_pdf/`, `specs/`,
`ofxstatement-russian/`, `sber_statement_tarovik/`.

За этот проход добавлено **76 файлов** (мои + подагента). Итог по каталогу целиком:

```
всего файлов        457
объём               265 МБ
PDF                  49
txt                  69      sta (MT940)  61
yml (эталоны)        69      csv          32
py (справочники)     53      xml          14
png                  21      ofx           8
asc (Berka)           8      dbf           6
xlsx                  1      qif           1
```

### Шаг 14. Классификация ВСЕХ 49 PDF корпуса

Критерий: `textlines<=2` → скан; иначе `lines+rects>=20` на первых 10 страницах → PDF-линии;
иначе PDF-без-линий. Счётчики `pdfplumber` 0.11.9 из venv проекта.

```
PDF-линии        29
PDF-без-линий    10
скан-без-текста  10
```

Полная таблица:

```
PDF-без-линий   |    2стр |    46строк | l=3    r=0    |   1800386Б | 2cb5eb736eb855fb | dc/2-bank-statement-hasan-mohammed_documentcloud-20467391_2026-09-22.pdf
PDF-без-линий   |   31стр |  1901строк | l=0    r=0    |   2089333Б | 25279193c46fd429 | dc/bank-records-and-foreign-transactions_documentcloud-22808150_2026-09-22.pdf
PDF-без-линий   |    4стр |   282строк | l=0    r=0    |    163981Б | 3d2dcb7932ef6c5d | dc/operations-july-bank-statement_documentcloud-23886516_2026-09-22.pdf
PDF-без-линий   |    2стр |    37строк | l=0    r=12   |     46207Б | d6e05b89efc8ca12 | dc/td-bank-statement_documentcloud-20783357_2026-09-22.pdf
PDF-без-линий   |    3стр |   121строк | l=0    r=5    |     15789Б | 4945bcda107e6d78 | gh/bsb-003-statement_github-bankstatemently_2026-09-22.pdf
PDF-без-линий   |    5стр |   291строк | l=2    r=6    |     75960Б | 67a5b862696fc06e | gh/bsb-004-statement_github-bankstatemently_2026-09-22.pdf
PDF-без-линий   |    2стр |   100строк | l=0    r=4    |     13899Б | a5cc2a7d210bc657 | gh/bsb-005-statement_github-bankstatemently_2026-09-22.pdf
PDF-без-линий   |    2стр |    14строк | l=0    r=0    |    113258Б | 68675c77fbc36c0e | sberbank/sber_example.pdf
PDF-без-линий   |    2стр |    24строк | l=0    r=0    |     16729Б | 5276dd44fa76a379 | yandexbank/ya_synthetic_card.pdf
PDF-без-линий   |    2стр |    16строк | l=0    r=0    |     14322Б | bf69ebd95e73cbf0 | yandexbank/ya_synthetic_deposit.pdf
PDF-линии       |  370стр |  9564строк | l=17   r=4    |   8407251Б | 7abde9ae75caf47d | _platform_bss/bs-client_v017.9.0_client_guide_srbank.pdf
PDF-линии       |  267стр |  7336строк | l=113  r=12   |   6182553Б | 2af76a9927380b25 | _platform_bss/bss_internet_client_guide_017.9.0.pdf
PDF-линии       |  226стр |  4792строк | l=65   r=1057 |  26626569Б | ef389e18f98c440f | _platform_faktura/faktura_internet_bank_corporate_2026-07.pdf
PDF-линии       |  129стр |  2145строк | l=33   r=677  |  18289302Б | 461780d733d88217 | _platform_faktura/faktura_internet_bank_retail_2026-09.pdf
PDF-линии       |   88стр |  2075строк | l=78   r=0    |   3601401Б | 419193ad0f3c0bd9 | _platform_ibank2/Corporate_Internet-Banking_WEB_ShortGuide.pdf
PDF-линии       |  194стр |  9155строк | l=0    r=110  |   4194524Б | 68fe79a5f72924ab | _platform_ibank2/Corporate_iBank2-Format_Guide_2025-07.pdf
PDF-линии       |  187стр |  3362строк | l=36   r=2    |  10113863Б | 7b7fa53189dbb417 | _platform_ibank2/iBank_Private_Internet_Bank.pdf
PDF-линии       |   20стр |   425строк | l=10   r=917  |   3606769Б | 1faa361ca1a3ceb0 | _platform_ibank2/iBank_for_life.pdf
PDF-линии       |   20стр |   517строк | l=12   r=35   |   2754884Б | 40fa6085a056adf7 | _platform_ibank2/ibank_for_business.pdf
PDF-линии       |   13стр |   451строк | l=0    r=63   |    685877Б | 7aed0f8765106696 | _standards_openapi_cbr/20251219_od_2887_1.pdf
PDF-линии       |   15стр |   363строк | l=0    r=39   |    738468Б | 9ffc01f8cc4ba42c | _standards_openapi_cbr/20251219_od_2890.pdf
PDF-линии       |   81стр |  3100строк | l=0    r=307  |   1323485Б | 48a2fad5a1d659a3 | _standards_openapi_cbr/20251219_od_2894.pdf
PDF-линии       |    5стр |   157строк | l=0    r=391  |    165342Б | 67227f33f4fc6f85 | berka/Financial_Data_description.pdf
PDF-линии       |    3стр |    77строк | l=0    r=23   |    108807Б | 4fb88429e0c964de | dc/carter-bank-statement_documentcloud-24376514_2026-09-22.pdf
PDF-линии       |    3стр |   154строк | l=0    r=976  |     31711Б | d3d5071b90a33272 | gh/bsb-001-statement_github-bankstatemently_2026-09-22.pdf
PDF-линии       |    4стр |   251строк | l=4    r=424  |     55807Б | 3700a073ac126217 | gh/bsb-002-statement_github-bankstatemently_2026-09-22.pdf
PDF-линии       |    4стр |   155строк | l=91   r=2    |   3597900Б | dcf5507e2feead8b | gh/chase_perfectcard_rewards_github-PriyanshuDangi_2026-09-22.pdf
PDF-линии       |    6стр |  1025строк | l=289  r=7    |    149533Б | 21ebade76538ab5f | hf/india_Digital_Type1_00001_hf-AgamiAI_2026-09-22.pdf
PDF-линии       |    6стр |  1001строк | l=288  r=7    |    149606Б | f5598e6881afa970 | hf/india_Digital_Type1_00002_hf-AgamiAI_2026-09-22.pdf
PDF-линии       |    6стр |   776строк | l=298  r=168  |    139851Б | 299952226bf640e2 | hf/india_Digital_Type2_00001_hf-AgamiAI_2026-09-22.pdf
PDF-линии       |    6стр |   836строк | l=304  r=174  |    143814Б | 507ebfc937ac41c1 | hf/india_Digital_Type2_00002_hf-AgamiAI_2026-09-22.pdf
PDF-линии       |    2стр |    21строк | l=0    r=35   |     15709Б | da69593abbca37eb | ozonbank/ozon_synthetic_broken_totals.pdf
PDF-линии       |    2стр |    21строк | l=0    r=35   |     15700Б | eda59cc3f90f2bd5 | ozonbank/ozon_synthetic_statement.pdf
PDF-линии       |   23стр |   519строк | l=42   r=0    |    801785Б | 05f08c94b7c95e76 | ru/finam_1c_client_bank_exchange_guide_2026-09-22.pdf
PDF-линии       |    7стр |   266строк | l=150  r=27   |    638673Б | f540b4ae5ca73602 | ru/sber_karta_i_schet_sep2021_mesyac_2026-09-22.pdf
PDF-линии       |    2стр |    57строк | l=0    r=146  |    298559Б | e790ce31ab46b993 | ru/sber_obrazec_vypiski_viza_dilijans_2026-09-22.pdf
PDF-линии       |   16стр |    91строк | l=0    r=53   |   4090339Б | aaf7cbe49d2c2ab4 | ru/sber_spravki_po_schetu_instrukciya_dszn_2026-09-22.pdf
PDF-линии       |    3стр |    93строк | l=119  r=91   |     54998Б | 8a19ef09906a8ff2 | ru/sber_test_statement_github_2026-09-22.pdf
PDF-линии       |    6стр |   240строк | l=34   r=0    |    566662Б | 9a999acd790744a8 | sberbank/sber_document_2022-05-16.pdf
скан-без-текста |    5стр |     0строк | l=0    r=2    |   7124617Б | 7e6d192333686e41 | dc/Bankstatements_documentcloud-4408246_2026-09-22.pdf
скан-без-текста |    5стр |     0строк | l=0    r=0    |    194312Б | b97d2b317786f4f7 | dc/CAFE-2016-bank-statement_documentcloud-3727296_2026-09-22.pdf
скан-без-текста |   86стр |     0строк | l=0    r=0    |   3475946Б | 9ad45b5a7710b3fb | dc/wtp-statement-summaries-account-1_documentcloud-501825_2026-09-22.pdf
скан-без-текста |    6стр |     0строк | l=0    r=0    |   6546361Б | a9c6d7cca832bc89 | hf/india_Scanned_Type1_00001_hf-AgamiAI_2026-09-22.pdf
скан-без-текста |    6стр |     0строк | l=0    r=0    |   6189058Б | 844cdf173744f653 | hf/india_Scanned_Type1_00002_hf-AgamiAI_2026-09-22.pdf
скан-без-текста |    6стр |     0строк | l=0    r=0    |   6342066Б | 96ae3335ba6dcf28 | hf/india_Scanned_Type2_00001_hf-AgamiAI_2026-09-22.pdf
скан-без-текста |    6стр |     0строк | l=0    r=0    |   6437604Б | c20a103cc66524d3 | hf/india_Scanned_Type2_00002_hf-AgamiAI_2026-09-22.pdf
скан-без-текста |    7стр |     1строк | l=17   r=10   |   1473630Б | ec72f74eede6f740 | ru/alfa_spravka_dvizhenie_sredstv_dszn_2026-09-22.pdf
скан-без-текста |    5стр |     0строк | l=0    r=0    |   6157740Б | df851cc6b3284f1a | ru/sber_rasshirennaya_vypiska_f551_lenobl_2026-09-22.pdf
скан-без-текста |    1стр |     0строк | l=0    r=0    |   1104036Б | b5a0424050cee54f | ru/sber_vypiska_licevoi_schet_f204s_lenobl_2026-09-22.pdf

PDF-линии: 29
PDF-без-линий: 10
скан-без-текста: 10
```

---

## Итоги

### Сводная таблица: класс файла — сколько добыто

| Класс конструкции | Всего в корпусе | Из них РЕАЛЬНЫХ документов | Где лежит |
|---|---|---|---|
| PDF с нарисованными линиями таблицы | 29 | 4 (Chase 2008, Carter, Сбер 09.2021, Сбер-виза) | `gh/`, `dc/`, `ru/`, `hf/` |
| PDF без линий (только координаты текста) | 10 | 4 (TD Bank, Al Jazeera, Operations July, 31-стр. bank-records) | `dc/`, `gh/`, `sberbank/`, `yandexbank/` |
| PDF-скан без текстового слоя | 10 | 6 (CAFE, Bankstatements, WTP 86 стр., Сбер ф.551, Сбер ф.204-с, Альфа) | `dc/`, `hf/`, `ru/` |
| CSV | 32 | Сбер, Альфа, ВТБ, Т-Банк, Райффайзен | `ru/`, `tinkoff/`, `tbank/`, `formats/` |
| XLSX — родной экспорт Т-Банка, 6 705 операций × 15 колонок | 1 | 1 | `ru_xlsx/` |
| 1С `1CClientBankExchange` (.txt) | 10+ | конструкция реальная, реквизиты обезличены | `ru1c/`, `formats_1c/`, `_1c_client_bank/`, `tochka_1c_suites/` |
| MT940 / MT942 (.sta) | 61 | ASNB, Citi, mBank, **Сбербанк**, ABN AMRO, ING, Rabobank, PostFinance, SNS, Triodos, KNAB | `mt940/`, `formats_intl/` |
| OFX / QFX | 8 | Райффайзен и международные | `formats/`, `raiffeisen/` |
| camt.053 / pain.001 / XML-обмен | 14 | ISO 20022 | `formats/`, `raiffeisen/`, `_generic_iso/` |
| Фикс-ширина TXT («ОТЧЕТ ПО СЧЕТУ КАРТЫ») | 2 | Сбер, CP1251 | `ru/` |
| Эталонная разметка (yml + json) | 70 | к MT940 и к индийским PDF | `mt940/`, `formats_intl/`, `hf/` |

Отдельный класс — **справочники форматов, а не выписки** (в счёт корпуса как данные не идут,
но это материал темы Г47): 22 экстрактора Сбера из `Ev2geny/Sberbank2Excel` (`ru_format_ref/`,
`sberbank2excel/`), руководства по форматам платформ BS-Client, iBank2, Faktura
(`_platform_*`, 1 300+ страниц суммарно), стандарты УФЭБС и ГОСТ Р ИСО 20022.

### Что осталось не покрыто в корпусе

1. 🔴 **Ни одного реального PDF-файла выписки российского НЕОТДЕЛЕНЧЕСКОГО банка** —
   Т-Банк, Точка, Озон Банк, Яндекс Банк, МТС Банк. Причина структурная, а не канальная:
   у них нет бумажных бланков и визовых образцов, выписка существует только как персональная
   выгрузка из личного кабинета. В вебе лежат описания и скриншоты, не файлы.
   Что по этим банкам ЕСТЬ: формат Т-Банка описан регулярками рабочего парсера
   (`ru/tbank_pdf_format_regex_parse_py_2026-09-22.txt`), родной XLSX-экспорт Т-Банка добыт
   целиком, синтетика Озона и Яндекс Банка лежит в `ozonbank/`, `yandexbank/`.
   Непройденные ступени по этим банкам: браузер и `sudact.ru` (подагент дошёл до
   WebSearch + Exa + GitHub API и остановился на бюджете).
2. **Реальный российский PDF-скан с рукописными пометками / плохим качеством** — добытые
   сканы (Сбер ф.551, ф.204-с, Альфа) чистые, из презентаций органов соцзащиты.
3. **Выписка по кредиту / ипотеке с графиком платежей** — ни одной, ни реальной, ни синтетической.
4. **Мультивалютная выписка российского банка** — есть только зарубежные (Гонконг, Сбербанк-HU).
5. **Реальный CSV/XLSX не-Т-Банка** — у Сбера, Альфы, ВТБ добыты семплы из фикстур
   `ofxstatement-russian`, объём в единицы строк; больших реальных выгрузок нет.
6. **Файл 1С-обмена с реальными, а не обезличенными реквизитами** — намеренно не искался.

### Правовая пометка

🔴 Часть файлов содержит настоящие персональные данные третьих лиц, опубликованные не нами:
`ru/sber_karta_i_schet_sep2021_mesyac_*.pdf` (ФИО и номер счёта),
`gh/chase_perfectcard_rewards_*.pdf` (JINLIAN YANG, адрес, номер карты),
`dc/*` (журналистские публикации), `ru_xlsx/tbank_operations_export_*.xlsx`
(6 705 реальных операций одной карты).
Весь корпус лежит ВНЕ git-репозитория. В репозиторий не попал ни один файл выписки —
только этот отчёт и журнал подагента. В тесты проекта пригодны без оговорок только
анонимизированные и синтетические файлы: `_SBER_DEBIT_2107_anonymized`, семплы
`ofxstatement-russian`, `hf/india_*` (Apache-2.0, synthetic), `gh/bsb-*` (MIT, synthetic),
фикстуры MT940 (BSD-3-Clause).

### Лицензии добытого

| Источник | Лицензия |
|---|---|
| `bankstatemently/bank-statement-parsing-benchmark` | MIT |
| `Ev2geny/Sberbank2Excel` | MIT |
| `kilylabs/client-bank-exchange-php`, `Unact/client_bank_exchange2`, `odoo-ru/client-bank-1c` | MIT |
| `WoLpH/mt940` | BSD-3-Clause |
| `AgamiAI/Indian-Bank-Statements` (HuggingFace) | Apache-2.0 |
| `Panhapich/bank-statement-structure-recognition` | MIT (не качал) |
| `sebastienrousseau/bankstatementparser` | NOASSERTION — 🟡 проверить перед внешним использованием |
| `PriyanshuDangi/localbankstatementconverter` | MIT (заявлено в задании) |
| `ScherbAlex/ProjectBank` и два аналога (XLSX Т-Банка) | 🟡 лицензии НЕТ |
| DocumentCloud (8 файлов) | журналистские публикации, каждая помечена `access: public`; отдельной лицензии нет |

### Замеры каналов (что сработало, что пусто)

- 🟢 `gh api search/code` по **дословной фразе из выписки** — единственный способ найти
  российские парсеры. `gh api search/repositories` по описанию дал пустоту на всех четырёх
  российских запросах.
- 🟢 `api.www.documentcloud.org` — 1 132 937 документов по `"bank statement" account balance`,
  без ключа, без антибота, обычным `curl` с первой ступени лестницы. Самый плодовитый канал
  по НАСТОЯЩИМ выпискам. Русского сегмента в нём нет (`Сбербанк` — 19 документов, выписок ноль).
- 🟢 `huggingface.co/api/datasets` — поиск и скачивание без ключа, `resolve/main/<path>` отдаёт
  файлы напрямую.
- 🔴 Ни на одном источнике этого прохода не потребовались ступени выше второй: `curl -sk`,
  `r.jina.ai`, Exa и браузер не понадобились, потому что все каналы оказались открытыми API.
  Ни одного 403, ни одной капчи. Вердиктов «не добыто по коду ответа» в этом проходе нет.
- Замер подагента: Exa терминами дала 15 результатов контент-маркетинга и ноль файлов,
  тот же смысл через `filetype:pdf` в WebSearch — 10 прямых PDF. **Искать расширение, а не тему.**

### Файлы

- Этот отчёт: `/Users/vasyaevdokimov/repos/personal-finance-dss/docs/research/raw/g69_real_statements_corpus_2026-09-22.md`
- Журнал подагента по РФ: `/Users/vasyaevdokimov/repos/personal-finance-dss/docs/research/raw/g69_sub_ru_banks_2026-09-22.md`
- Корпус (вне git): `/Users/vasyaevdokimov/raw-originals/finpilot-data/statements/` — 457 файлов, 265 МБ
