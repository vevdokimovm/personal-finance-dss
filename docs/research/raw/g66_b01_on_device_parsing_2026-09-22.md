# Г66 / Б-01 — Где физически разбирается банковская выписка

Сырьё исследования. Дата: 2026-09-22. Тема заведена аудитом покрытия № 7, приоритет 1.

Постановка: правило владельца (выписки не покидают устройство) + вывод Г59 (идентификаторы
третьих лиц в каждой строке → ч. 14 ст. 13.11 КоАП, 10–15 млн ₽) против существующего кода
(`app/services/statement_parser.py`, серверный разбор на `pdfplumber 0.11.9`).

Ограничение: ML и LLM не используются ВООБЩЕ. Только формулы, правила, справочники.

## Журнал

### Ж-01. Свой код и свои прошлые замеры (локально, канал — файловая система, до веба)

`app/services/statement_parser.py`, 934 строки, `pdfplumber` — единственная PDF-библиотека,
импорт мягкий (`try/except ImportError`). Четыре точки входа PDF и **два разных приёма**:

| Банк | функция | приём | зависит ли от линий |
|---|---|---|---|
| Тинькофф | `parse_tinkoff_pdf` (стр. 409–435) | `page.extract_text()` → regex `_PDF_OP` построчно | **нет** |
| Сбер | `parse_sber_pdf` (стр. 629–637) | `page.extract_text()` → `_sber_text_to_transactions` | **нет** |
| ВТБ | `parse_vtb_pdf` (стр. 568–577) | `page.extract_tables()` без `table_settings` | **да** |
| Райффайзен | `parse_raiffeisen_pdf` (стр. 720–728) | `page.extract_tables()` без `table_settings` | **да** |

Плюс служебные, оба на `extract_text()`: `detect_pdf_bank` (стр. 846–856),
`pdf_non_statement_reason` (стр. 925–934).

🔴 Дословная строка кода, определяющая зависимость от линий (ВТБ и Райффайзен идентичны):

```python
with pdfplumber.open(io.BytesIO(raw)) as pdf:
    for page in pdf.pages:
        tables.extend(page.extract_tables())
```

`extract_tables()` без аргументов = дефолт pdfplumber `vertical_strategy="lines"` /
`horizontal_strategy="lines"`, то есть строится на графических примитивах (`lines`,
`rects`, `curves`), а не на тексте.

**Замер Г20 §1.2 дословно** (`pdf_statement_parsing_accuracy_2026-09-13.md`, стр. 1004–1033),
`pdfplumber 0.11.9`:

| Файл | знаков текста | найдено таблиц | строк в таблицах | мс |
|---|---|---|---|---|
| sber.pdf | 200 | **0** | 0 | 21 |
| tinkoff.pdf | 117 | **0** | 0 | 14 |
| vtb.pdf | 373 | 1 | 3 | 57 |
| raiffeisen.pdf | 266 | 1 | 4 | 34 |

> «**`extract_tables()` вернул 0 таблиц на sber.pdf и tinkoff.pdf** — там таблица без
> линий. То есть стратегия "дай pdfplumber найти таблицу" работает ровно на тех банках,
> которые рисуют рамку, и **не работает** на тех, кто верстает пробелами. У Сбера
> (по разбору Sberbank2Excel, раздел 2.1) рамок нет вовсе.»

**Вывод Г20 §1.4 дословно** (стр. ~1160), уже сделанный ДО этой темы:

> «Правильная единица извлечения — **слово с координатами, а не строка текста**;
> колонки задаются **якорями шапки**, а не кластеризацией всех x0.»

Это прямо определяет требование к браузерной библиотеке: нужен доступ (а) к словам
с координатами и (б) к графическим примитивам — иначе переносится только половина кода.

---

### Ж-02. pdf.js — что реально отдаёт (первоисточник: npm-реестр, jsDelivr, исходники Mozilla)

**Реквизиты пакета.** `curl https://registry.npmjs.org/pdfjs-dist` → 200:

```
dist-tags: {'latest': '6.3.289'}
latest: 6.3.289   license: Apache-2.0
deps: None                      ← ноль зависимостей
unpackedSize: 34781083          ← 34,78 МБ весь пакет (cmaps, шрифты, legacy, sourcemaps)
created:  2014-09-22T22:34:59Z
modified: 2026-08-29T12:52:28Z  ← живой, релиз меньше месяца назад
```

**Реальный вес того, что грузится в браузер** (jsDelivr API `data.jsdelivr.com/v1/packages/npm/pdfjs-dist@6.3.289`, файлы скачаны и сжаты локально `gzip -c | wc -c`):

| Файл | minified, байт | gzip, байт |
|---|---|---|
| `build/pdf.min.mjs` (основной поток) | 458 705 | **131 659** |
| `build/pdf.worker.min.mjs` (воркер) | 1 265 413 | **374 794** |
| **итого на загрузку** | **1 724 118 (1,64 МБ)** | **506 453 (494 КБ)** |

Для сравнения из того же листинга: `legacy/build/pdf.min.mjs` 518 555 и
`legacy/build/pdf.worker.min.mjs` 1 317 034 (сборка под старые браузеры — крупнее).
Плюс по требованию догружаются `cmaps/` (CJK) и `standard_fonts/` — для кириллических
выписок нужны стандартные шрифты, не CJK.

#### Ж-02а. `getTextContent` — текст с координатами, ДА

Типы взяты дословно из `types/src/display/api.d.ts` пакета `pdfjs-dist@6.3.289`
(66 756 байт, `cdn.jsdelivr.net`, 200):

```ts
export type TextItem = {
    str: string;          // - Text content.
    dir: string;          // - Text direction: 'ttb', 'ltr' or 'rtl'.
    transform: Array<any>;// - Transformation matrix.
    width: number;        // - Width in device space.
    height: number;       // - Height in device space.
    fontName: string;     // - Font name used by PDF.js for converted font.
    hasEOL: boolean;      // - Indicating if the text content is followed by a line-break.
};

export type TextContent = {
    items: Array<TextItem | TextMarkedContent>;
    styles: { [x: string]: TextStyle };   // TextStyle: ascent, descent, fontFamily, vertical
    lang: string | null;
};

export type getTextContentParameters = {
    includeMarkedContent?: boolean | undefined;   // default false
    disableNormalization?: boolean | undefined;   // default false
};
```

🔴 **Это НЕ «поток текста» — это позиционированные элементы.** `transform` — матрица
`[a, b, c, d, e, f]`, где `e`/`f` = x/y базовой точки в device space, `width`/`height` —
габариты в device space. То есть эквивалент `page.get_text("words")` у pymupdf и
`page.extract_words()` у pdfplumber получается напрямую, без ML.

Две оговорки, обе из официальной документации Mozilla
(`mozilla.github.io/pdf.js/api/draft/module-pdfjsLib-PDFPageProxy.html`, WebFetch 200):

1. «All occurrences of whitespace will be replaced by standard spaces (0x20)» — то есть
   нормализация пробелов происходит всегда, а `disableNormalization: true` отключает
   только нормализацию текста в воркере (лигатуры, диакритика), не разбиение.
2. Единица `TextItem` — **не слово**: pdf.js отдаёт то, что лежит в одном операторе
   показа текста (`Tj`/`TJ`). Это может быть целая строка, может быть один глиф. Своя
   группировка в слова/колонки нужна в любом случае — ровно как и с pdfplumber.

#### Ж-02б. 🔴 ГЛАВНЫЙ ОТВЕТ: графические примитивы в pdf.js ЕСТЬ

Через второй публичный метод — `page.getOperatorList()`. Тип из того же `.d.ts`:

```ts
export type PDFOperatorList = {
    fnArray: Array<number>;   // - Array containing the operator functions.
    argsArray: Array<any>;    // - Array containing the arguments of the functions.
};
```

`OPS` — **публичный экспорт** сборки (проверено `tail -c 3000 pdf.min.mjs | grep`:
в списке `export{...}` присутствует `F as OPS`). Дословный фрагмент enum, извлечённый
из `build/pdf.min.mjs@6.3.289`:

```
... transform:12, moveTo:13, lineTo:14, curveTo:15, curveTo2:16, curveTo3:17,
closePath:18, rectangle:19, stroke:20, closeStroke:21, fill:22, eoFill:23,
fillStroke:24, eoFillStroke:25, closeFillStroke:26, closeEOFillStroke:27,
endPath:28, clip:29, eoClip:30, ... constructPath:91, setStrokeTransparent:92,
setFillTransparent:93, rawFillPath:94
```

То есть прямоугольники, линии и обводки в модели pdf.js существуют как операторы.

**НО отдаются они не по одному.** Исходник `src/core/evaluator.js` (master,
`raw.githubusercontent.com`, 200, 176 820 байт) — дословно, строки 2246–2285:

```js
case OPS.moveTo:
case OPS.lineTo:
case OPS.curveTo:
case OPS.curveTo2:
case OPS.curveTo3:
case OPS.closePath:
case OPS.rectangle:
  self.buildPath(fn, args, stateManager.state);
  continue;
case OPS.stroke:
case OPS.closeStroke:
case OPS.fill:
...
case OPS.endPath: {
  const { state: { pathBuffer, pathMinMax } } = stateManager;
  ...
  if (pathBuffer.length === 0) {
    operatorList.addOp(OPS.constructPath, [fn, [null], null]);
  } else {
    operatorList.addOp(OPS.constructPath, [
      fn,
      [new Float32Array(pathBuffer)],
      pathMinMax.slice(),
    ]);
```

И `buildPath` (строки 1408+) — прямоугольник разворачивается в путь и **сразу даёт bbox**:

```js
case OPS.rectangle: {
  const x = (state.currentPointX = args[0]);
  const y = (state.currentPointY = args[1]);
  const width = args[2]; const height = args[3];
  const xw = x + width; const yh = y + height;
  if (width === 0 || height === 0) {
    pathBuffer.push(DrawOPS.moveTo, x, y, DrawOPS.lineTo, xw, yh, DrawOPS.closePath);
  } else {
    pathBuffer.push(DrawOPS.moveTo, x, y, DrawOPS.lineTo, xw, y,
                    DrawOPS.lineTo, xw, yh, DrawOPS.lineTo, x, yh, DrawOPS.closePath);
  }
  Util.rectBoundingBox(x, y, xw, yh, minMax);
```

Кодировка `pathBuffer` — `DrawOPS` из `src/shared/util.js` (200), дословно:

```js
const DrawOPS = { moveTo: 0, lineTo: 1, curveTo: 2, quadraticCurveTo: 3, closePath: 4 };
```

**Что это значит на практике.** На каждый закрашенный/обведённый путь страницы приходит
одна запись `fnArray[i] === OPS.constructPath (91)` и
`argsArray[i] === [paintOp, [Float32Array координат], [minX, minY, maxX, maxY]]`, где
`paintOp` — `OPS.stroke` / `OPS.fill` / `OPS.endPath` и т. д. Из этого механически
восстанавливаются те же сущности, что pdfplumber зовёт `page.lines`, `page.rects`,
`page.edges`: горизонтальная линия = путь из двух точек с одинаковым `y`; рамка ячейки =
`rectangle`, развёрнутый в 4 `lineTo` + `closePath`; заливка-зебра = `constructPath`
с `paintOp = OPS.fill`.

🔴 **Прямой ответ на вопрос 2: приём «таблица по нарисованным линиям» ПЕРЕНОСИТСЯ.
Данные для него в браузере есть. Это переписывание, а не смена алгоритма.** Но переносится
он не как вызов одной функции, а как собственный слой: pdfplumber уже отдаёт готовые
объекты `{x0, x1, top, bottom, width, height, linewidth}`, а pdf.js отдаёт сырой
операторный поток, из которого их надо собрать самому.

**Три конкретные статьи расхода, которых у pdfplumber нет** (каждая — прямое следствие
процитированного кода, не оценка):

1. **CTM надо вести самому.** В `buildPath` координаты пишутся **как есть, из содержимого
   потока**: `Util.rectBoundingBox(x, y, xw, yh, minMax)` — умножения на текущую матрицу
   преобразования нет. Значит потребитель обязан держать стек `OPS.save (10)` /
   `OPS.restore (11)` / `OPS.transform (12)` и сам приводить координаты к странице —
   ровно то, что делает `CanvasGraphics` в `src/display/canvas.js`. У `TextItem`, наоборот,
   `transform` уже в device space — то есть **текст и графика приходят в РАЗНЫХ системах
   координат**, и их сведение — обязательная работа.
2. **`DrawOPS` не экспортирован.** В списке `export{...}` сборки `pdf.min.mjs` есть `OPS`,
   но `DrawOPS` отсутствует — значения `{0,1,2,3,4}` придётся зашить константами в свой
   код, то есть опереться на приватную деталь библиотеки.
3. 🔴 **Формат `constructPath` менялся между мажорами.** Сверено с
   `raw.githubusercontent.com/mozilla/pdf.js/v4.10.38/src/core/evaluator.js` (200,
   166 984 байта), строка 1437 дословно:
   ```js
   operatorList.addOp(OPS.constructPath, [[fn], args, minMax]);
   ```
   В v4 это `[[массив кодов операций], сырые аргументы, minMax]`; в v6 —
   `[paintOp, [Float32Array с DrawOPS-кодировкой], minMax]`. **Несовместимо.** То есть слой
   разбора графики привязывается к мажорной версии pdf.js и ломается при её смене молча —
   типы TypeScript этого не поймают, `argsArray` объявлен `Array<any>`.


---

### Ж-03. Альтернативы pdf.js — реквизиты с первоисточника (npm-реестр, jsDelivr, GitHub API)

`curl https://registry.npmjs.org/<пакет>` → 200 по каждому, дословные поля манифеста:

| Пакет | latest | Лицензия | Зависимости | unpackedSize | npm modified |
|---|---|---|---|---|---|
| `pdfjs-dist` | 6.3.289 | **Apache-2.0** | нет | 34 781 083 | 2026-08-29 |
| `pdf-lib` | 1.17.1 | MIT | 4 | 19 461 112 | **2022-05-12** |
| `mupdf` (mupdf.js) | 1.28.1 | **AGPL-3.0-or-later** | нет | 14 324 000 | 2026-09-06 |
| `@embedpdf/pdfium` | 2.15.1 | MIT (обёртка) | нет | 7 554 316 | 2026-09-16 |
| `@hyzyla/pdfium` | 2.1.13 | MIT (обёртка) | нет | 11 246 019 | 2026-05-12 |
| `pdfium.js` | 0.2.1-rc.1 | MIT | нет | 10 600 370 | 2024-01-20 |
| `unpdf` | 1.8.1 | MIT | нет | 2 141 399 | 2026-08-13 |
| `pyodide` | 314.0.7 | MPL-2.0 | 2 | 13 879 282 | 2026-09-16 |

#### `pdf-lib` — извлечения текста нет вообще, вопрос закрыт автором

`api.github.com/repos/Hopding/pdf-lib` → 200: `pushed_at 2024-07-17T12:18:51Z`,
`archived: false`, звёзд 8640, открытых issue 317, лицензия MIT. Релиза на npm нет
4 года, коммитов нет 2 года.

Ответ автора (Hopding) в issue #93 «Reading text contents of page», 2019-04-16, дословно:

> «Hello @matthopson. `pdf-lib` is primarily focused on creating and editing PDFs right now.
> **It does not currently have functionality to extract text content from them.** Though,
> this is functionality I've considered adding at some point in the future.
> For your use case, I'd suggest using `pdf.js` to extract text from the documents…»

Там же, 2026-05-13, пользователь LucBerge, спустя 7 лет:

> «6 years from your previous comment regarding text extraction, is there now a way to
> extract text? I couldn't find anything so far.»

Ответа автора на это нет. Поиск по репозиторию `«extract text»` даёт 11 issue, старейшая
открытая — #1209 от 2022-04-08. Вывод по факту: `pdf-lib` — библиотека СОЗДАНИЯ и правки
PDF, для чтения выписки не применима в принципе.

#### `mupdf.js` — лицензия AGPL-3.0-or-later

Поле `license` в npm-манифесте дословно: `AGPL-3.0-or-later`. Пакет живой
(publish 2026-09-06). AGPL §13 распространяет требование раскрытия исходников на
предоставление доступа по сети. Для закрытого коммерческого продукта — либо раскрытие
кода, либо коммерческая лицензия Artifex. Класс остатка: 🟡 вопрос денег и договора
(действие владельца), не техники.

#### PDFium через WASM — самый прямой доступ к геометрии из всех проверенных

`@embedpdf/pdfium@2.15.1`, MIT-обёртка над PDFium (Google/Chromium; лицензия самого
PDFium лежит отдельным файлом `LICENSE.pdfium`, 12 880 байт). Состав пакета
(jsDelivr API `data.jsdelivr.com/v1/packages/npm/@embedpdf/pdfium@2.15.1`, 200):

```
/dist/pdfium.wasm            4 646 932   ← 4,43 МБ, реальная цена загрузки
/dist/index.browser.js         293 211
/dist/vendor/functions.d.ts     58 293
/LICENSE                         1 075
/LICENSE.pdfium                 12 880
```

Экспортируемые функции — грепом по `functions.d.ts` (скачан, 200, 58 293 байта).

Текст: посимвольная геометрия, тоньше чем у pdf.js —

```
FPDFText_CountChars      FPDFText_GetCharBox       FPDFText_GetCharOrigin
FPDFText_GetText         FPDFText_GetLooseCharBox  FPDFText_GetCharAngle
FPDFText_GetFontSize     FPDFText_GetFontInfo      FPDFText_GetFontWeight
FPDFText_GetMatrix       FPDFText_GetFillColor     FPDFText_GetStrokeColor
FPDFText_CountRects      FPDFText_GetRect          FPDFText_GetBoundedText
FPDFText_IsGenerated     FPDFText_IsHyphen         FPDFText_HasUnicodeMapError
```

Графика: прямой доступ к объектам-путям, без реконструкции из потока операторов —

```
FPDFPageObj_GetType        FPDFPageObj_GetBounds      FPDFPageObj_GetRotatedBounds
FPDFPageObj_GetMatrix      FPDFPageObj_GetStrokeWidth FPDFPageObj_GetStrokeColor
FPDFPageObj_GetFillColor   FPDFPageObj_GetDashArray   FPDFPageObj_GetDashCount
FPDFPath_CountSegments     FPDFPath_GetPathSegment    FPDFPath_GetDrawMode
FPDFPathSegment_GetType    FPDFPathSegment_GetPoint   FPDFPathSegment_GetClose
```

Это ближе к pdfplumber, чем pdf.js: `FPDFPageObj_GetBounds` + `FPDFPageObj_GetMatrix`
дают готовый прямоугольник в координатах страницы, `FPDFPageObj_GetStrokeWidth` — то же,
что поле `linewidth` в объектах `page.lines` у pdfplumber, `FPDFText_GetCharBox` —
посимвольные рамки, из которых слова собираются надёжнее, чем из `TextItem` pdf.js.
Отдельно `FPDFText_IsGenerated` помечает пробелы, ДОБАВЛЕННЫЕ движком, а не лежащие
в файле — прямой инструмент против ложных разделителей колонок.

Цена: 4,43 МБ `.wasm` против 494 КБ gzip у pdf.js — в 9 раз тяжелее.

---

### Ж-04. Дополнение к вопросу 2: у самого pdfplumber есть и БЕЗлинейная стратегия

Скачан `raw.githubusercontent.com/jsvine/pdfplumber/stable/pdfplumber/table.py`
(200, 24 367 байт). В нём, помимо работы с `edges` из графики, есть функции
`words_to_edges_h` (стр. 101) и `words_to_edges_v` (стр. 144) — то есть стратегия
`vertical_strategy="text"`, строящая границы колонок ИЗ СЛОВ, без единой линии.

🔴 Наш код этой стратегией не пользуется: `page.extract_tables()` вызывается без
`table_settings`, то есть на дефолте `"lines"`. Значит зависимость от линий — свойство
нашей НАСТРОЙКИ, а не библиотеки.

Второе наблюдение из того же файла: у `table.py` **ноль внешних импортов** — только
`itertools`, `dataclasses`, `operator`, `typing` и внутренние модули pdfplumber.
Алгоритм поиска таблицы (`TableFinder`, `snap_edges`, `join_edge_group`, `merge_edges`,
`edges_to_intersections`) — чистая геометрия над списком рёбер вида
`{x0, x1, top, bottom, orientation}`. Он переносим на TypeScript построчно и не требует
ни pdfminer, ни Python: ему нужен только список рёбер на входе.

---

### Ж-05. Вопрос 3 — Python в браузере (Pyodide): цепочка зависимостей и вес

**Реквизиты.** npm `pyodide` latest 314.0.7, лицензия **MPL-2.0**, modified 2026-09-16 —
проект живой. Замеры ниже сняты на стабильной CDN-раскладке `v0.28.3`
(`pyodide-lock.json` отдаёт `python: 3.13.2`, `platform: emscripten_4_0_9`,
`abi_version: 2025_0`, **343 пакета** в дистрибутиве).

**Цепочка зависимостей pdfplumber** (PyPI JSON API, 200 по каждому пакету, дословно
поле `requires_dist`):

```
pdfplumber 0.11.10   →  pdfminer.six==20260107 , Pillow>=12.2.0 , pypdfium2>=5.9.0
pdfminer.six 20260107 →  charset-normalizer>=2.0.0 , cryptography>=36.0.0
pypdfium2 5.13.0      →  (нет зависимостей, НО это бинарные колёса:
                          android / macosx / manylinux / musllinux — emscripten НЕТ)
```

Типы колёс: `pdfplumber-0.11.10-py3-none-any.whl` и
`pdfminer_six-20260107-py3-none-any.whl` — **оба чистый Python** (`py3-none-any`),
то есть ставятся куда угодно. `pypdfium2` и `Pillow` — бинарные.

**Что есть в самом Pyodide** (грепом по `pyodide-lock.json`, 109 732 байта, 200):

| Пакет | в Pyodide | версия | depends |
|---|---|---|---|
| `cryptography` | **есть** | 45.0.5 | `libopenssl`, `six`, `cffi` |
| `Pillow` | **есть** | 11.3.0 | — |
| `charset-normalizer` | **есть** | 3.4.2 | — |
| `micropip` | есть | 0.10.1 | — |
| `pdfminer.six` | **НЕТ** | — | — |
| `pdfplumber` | **НЕТ** | — | — |
| `pypdfium2` | **НЕТ** | — | — |

#### Ж-05а. Ключевая находка: бинарные зависимости pdfplumber не мешают нашему коду

Импорты `pypdfium2` и `PIL` живут ТОЛЬКО в `pdfplumber/display.py`
(скачан 200, 12 823 байта), строки 5–7 дословно:

```python
import PIL.Image
import PIL.ImageDraw
import pypdfium2  # type: ignore
```

`display.py` — это отрисовка страницы в картинку (`page.to_image()`). В `page.py`
(200, 25 391 байт) он подключается **лениво**: строка 78 — внутри `if TYPE_CHECKING:`,
строка 598 — внутри тела метода `to_image()`:

```python
def to_image(
    ...
    from .display import DEFAULT_RESOLUTION, PageImage
```

А `pdfplumber/__init__.py` (200) тянет только:

```python
import pdfminer
import pdfminer.pdftypes
from . import utils
from ._version import __version__
from .pdf import PDF
from .repair import repair
```

🔴 **Следствие, проверяемое:** `import pdfplumber` НЕ импортирует ни `pypdfium2`, ни
`PIL`. Обе точки, которые использует наш код (`extract_text()` и `extract_tables()`),
опираются исключительно на `pdfminer.*`. То есть в Pyodide путь существует:
`micropip.install("pdfplumber", deps=False)` + `micropip.install("pdfminer.six")`,
и требование `Pillow>=12.2.0` (Pyodide даёт 11.3.0) обходится тем же `deps=False`,
потому что Pillow нужен только `display.py`.

Ограничение на этом пути честное: `cryptography` — жёсткий импорт **уровня модуля**
в `pdfminer/pdfdocument.py` (200, 38 097 байт), строки 13–14 дословно:

```python
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
```

Его Pyodide поставляет (45.0.5 ≥ 36.0.0 — требование выполнено), так что блокировки нет,
но это ещё один мегабайт загрузки.

#### Ж-05б. Вес Pyodide — замер, а не оценка

Скачано с `cdn.jsdelivr.net/pyodide/v0.28.3/full/`, обычной загрузкой и с
`Accept-Encoding: br, gzip` (как получает браузер):

| Файл | без сжатия | по сети (br) |
|---|---|---|
| `pyodide.asm.wasm` | 8 645 967 (8,25 МБ) | **2 667 808 (2,54 МБ)** |
| `python_stdlib.zip` | 2 416 866 (2,30 МБ) | **2 379 766 (2,27 МБ)** |
| `pyodide.asm.js` | 1 073 033 (1,02 МБ) | **226 208 (221 КБ)** |
| **ядро итого** | **12 135 866 (11,57 МБ)** | **5 273 782 (5,03 МБ)** |

`python_stdlib.zip` почти не жмётся — это уже zip.

Сверх ядра докачиваются колёса (это zip-архивы, дополнительное сжатие даёт ~0):

| Колесо | байт |
|---|---|
| `pdfminer_six-20260107-py3-none-any.whl` (PyPI) | **6 592 252 (6,29 МБ)** |
| `cryptography-45.0.5-cp313-abi3-pyodide_2025_0_wasm32.whl` | **944 749 (923 КБ)** |
| `pdfplumber-0.11.10-py3-none-any.whl` (PyPI) | 60 047 |
| плюс `cffi`, `six`, `libopenssl`, `charset-normalizer`, `micropip` | не замерены отдельно |

🔴 **Итог по весу: ~12,9 МБ по сети против 494 КБ у pdf.js — в 26 раз больше.**
Основной вклад сверх ядра даёт сам `pdfminer.six` (6,29 МБ) — колесо тяжёлое из-за
встроенных CMap-ресурсов.

**Второе ограничение, отдельно от веса:** `micropip` ставит колёса **с PyPI по сети
из браузера пользователя**. То есть путь Pyodide либо требует похода на `pypi.org`
во время работы приложения, либо все колёса надо класть на свой домен и ставить
по прямым URL. Первое — внешняя зависимость в рантайме, второе — +12,9 МБ статики
в свою раздачу.

#### Ж-05в. Официальная оценка самого проекта Pyodide

`pyodide.org/en/stable/project/roadmap.html` (WebFetch, 200; страница подписана
**Version 314.0.7**), раздел «Reducing download sizes and initialization times», дословно:

> «At present a first load of Pyodide requires a 6.4 MB download, and the environment
> initialization takes 4 to 5 seconds.»

Это оценка **голого рантайма**, без `pdfminer.six` (ещё 6,29 МБ). Мой замер по сети
дал 5,03 МБ на ядро — расхождение с их «6,4 МБ» объясняется составом (они, судя по
всему, считают без brotli-сжатия части файлов и/или другой набор ассетов). Цифра «4–5 с
инициализации» — это ПОСЛЕ загрузки, то есть время компиляции WASM и старта интерпретатора.

---

### Ж-06. Вопрос 4 — кто так уже делает (результат первого подагента)

Полное сырьё с кодами ответов и дословными цитатами — в отдельном файле:
`docs/research/raw/_g66_sub_practice_2026-09-22.md` (610 строк, 13 вызовов, 0 источников,
недоступных по вине сайта).

🔴 **Прямое попадание — чужой открытый продукт решает нашу задачу нашим же стеком.**
`PriyanshuDangi/localbankstatementconverter` (`localbankstatementconverter.com`).
Реквизиты, доснято мной `api.github.com/repos/PriyanshuDangi/localbankstatementconverter`
→ 200: **лицензия MIT**, `pushed_at 2026-04-25T16:26:02Z`, `archived: false`, язык
JavaScript, звёзд 1 (то есть код настоящий, но аудитории у него нет — на репутацию
проекта опираться нельзя, только на приём).

Устройство по его README (цитаты — в файле подагента): **Pyodide + `pdfminer.six`
в Web Worker**, «there is no backend»; таблица разбирается **тремя уровнями**:
нарисованные рамки PDF → координаты слов и колонки → текстовая эвристика. То есть
ровно та трёхуровневая лестница, которую независимо даёт наш Г20 (§1.2 линии, §1.4
слова с координатами, текст как последний рубеж). Отдельно ценно: парсер вынесен
в чистый ESM и **тестируется в Node без headless-браузера и без Pyodide** (Python-экстрактор
пишет `.txt`+`.json`, Node-раннер сравнивает выход) — готовая схема тестирования
для нашего TDD.

Второе подтверждение архитектуры, не маркетинговое: **Actual Budget** (MIT, пуш
21.09.2026) — разбор CSV/QIF/OFX/QFX/CAMT на устройстве, `loot-core` + SQLite-в-WASM
+ IndexedDB; дока API дословно: «the server does not have the functionality for
analyzing details of or modifying your budget».

Важный отрицательный результат: **Firefly III + data-importer** — разбор на СВОЁМ сервере
(self-hosted PHP), не на клиенте, и **PDF не поддерживается вовсе** (только CSV и
CAMT.052/053), лицензия AGPL-3.0. То есть в списке-эталоне, заданном темой, Firefly III
нашу задачу НЕ решает.
И: **Maybe Finance** — репозиторий **архивирован**, последний пуш 24.07.2025.

Наблюдение подагента по поиску кода на GitHub, важное для оценки зрелости приёма:
`pdfjs-dist + "bank statement"` даёт 742 попадания, но «большинство путей содержат
`backend/`, `.node.ts`, `electron/` — pdf.js берут как библиотеку, но запускают
на сервере/в Node, не в браузере». То есть разбор выписки именно В БРАУЗЕРЕ — редкий
приём, а не индустриальный стандарт.

---

### Ж-07. Вопрос 5 — цена переноса на клиент, по замерам

#### Ж-07а. Вес загрузки — сведённая таблица трёх путей

| Путь | что грузится | по сети | во сколько раз к pdf.js |
|---|---|---|---|
| **pdf.js** | `pdf.min.mjs` + `pdf.worker.min.mjs`, gzip | **494 КБ** | ×1 |
| **PDFium WASM** | `pdfium.wasm` 4 646 932 + `index.browser.js` 293 211 | **~4,7 МБ** (без сжатия) | ×9 |
| **Pyodide + pdfminer.six** | ядро 5 273 782 (br) + `pdfminer.six` 6 592 252 + `cryptography` 944 749 + `pdfplumber` 60 047 + мелочь | **~12,9 МБ** | ×26 |

#### Ж-07б. Время до первого разбора

- Pyodide: **4–5 с инициализации** после загрузки — цифра самого проекта (roadmap,
  Version 314.0.7). Автор `localbankstatementconverter` независимо пишет «3–5 seconds
  downloading the Pyodide WASM runtime (~10 MB)» — это про загрузку, то есть суммарно
  первый запуск ощутимо дольше обоих слагаемых.
- pdf.js: отдельной цифры старта нет — воркер поднимается вместе с 494 КБ, отдельного
  этапа «инициализация рантайма» у него нет в принципе.
- 🔴 **Замера скорости РАЗБОРА на слабом устройстве не найдено ни для одного пути.**
  Опорная точка, которая у нас есть, — Г20 §1.3: на десктопе `pdfplumber` даёт
  14–57 мс на страницу, `pymupdf` 3,5–14,5 мс. Перенос этих чисел на мобильный браузер
  через WASM — **догадка, а не замер**; своей цифры нет. Класс остатка: 🟢 (наш замер
  не сделан — воспроизводится на своих же шаблонах `app/data/statement_templates/`).

#### Ж-07в. OCR сканов — отдельная и самая дорогая статья

Замеры (npm-реестр и прямые загрузки, коды 200):

| Артефакт | размер | лицензия |
|---|---|---|
| `tesseract.js` 7.0.0 | 1 411 341 unpacked | Apache-2.0 |
| `tesseract.js-core` 6.1.2 | 30 606 788 unpacked | Apache-2.0 |
| `tesseract-core-simd-lstm.wasm` (самый лёгкий вариант ядра) | **2 871 377** | — |
| `tesseract-core-simd.wasm` | 3 469 078 | — |
| `rus.traineddata` из `tessdata_fast` | **3 861 738 (3,68 МБ)** | Apache-2.0 |
| `rus.traineddata` из `tessdata` (полный) | **19 920 885 (19,0 МБ)** | Apache-2.0 |

То есть минимальная русскоязычная OCR в браузере = ~2,9 МБ ядра + 3,7 МБ словаря
= **~6,6 МБ сверх** любого из трёх путей выше, и это на быстрой модели; на полной —
~22,9 МБ. `tesseract.js` последний раз публиковался 2025-12-15 (т. е. ~9 месяцев назад).

Отдельная поправка: два продукта из разбора подагента признают, что **сканы клиент
не берёт вовсе** — либо «вставьте OCR-текст вручную», либо явное согласие пользователя
на облачный OCR. То есть отрасль на этом месте либо отказывается от функции, либо
осознанно рвёт принцип «ничего не уходит».

#### Ж-07г. Три статьи расхода, у которых нет цены в мегабайтах

Их называют сами авторы клиентских продуктов (цитаты в файле подагента):

1. **Парсер нельзя чинить централизованно.** Серверный `statement_parser.py` правится
   деплоем; клиентский приезжает пользователю только с релизом фронтенда и кэшем
   Service Worker. У нас в Г20 зафиксировано, что **у Сбера 20 форматов выписки,
   из них 5 новых только за 2026 год** — то есть парсер правится часто, и это
   регулярная, а не разовая задача.
2. **Отладка чужого сбоя без файла.** Прямое следствие правила владельца: выписку,
   на которой сломался парсер, нам не пришлют. Признание того же класса у NeatPass,
   дословно: «Bug reports are an exception to our general "data never leaves your
   device" principle» — то есть даже продукт с абсолютной формулировкой делает для
   баг-репортов исключение.
3. **Требование к хостингу.** Actual, дословно: `SharedArrayBuffer` требует
   cross-origin isolation (COOP/COEP), «this is a hosting/server requirement,
   **it cannot be bundled away**». Это заголовки на раздаче, а не код.

---

### Ж-08. Вопрос 6 — гибрид и правовая рамка. Сырьё подагента + МОЯ ПРАВКА его вывода

Основной массив — в `docs/research/raw/_g66_sub_practice_2026-09-22.md` (образцы
формулировок «что остаётся на устройстве / что уходит», перечень продуктов, цитаты
из политик Apple Health, Actual, NeatPass, Flow Recovery, StatementSheet).

Главный отрицательный результат подагента, я его подтверждаю: **прямого разъяснения
Роскомнадзора или судебного акта РФ, отвечающего на вопрос «обработка на устройстве
пользователя — обработка ли оператором», не найдено.** Класс остатка: 🟢 (каналы
`pd.rkn.gov.ru`, `sudact.ru`, `kad.arbitr.ru`, `zakon.ru` не пройдены до конца),
но вероятно, что документа нет вовсе.

#### Ж-08а. 🔴 ПРАВКА: подагент неверно передал исход дела А40-12676/2024

Подагент подал его как довод «за нас». Я сверил по двум первоисточникам —
`consultant.ru` (карточка Постановления АС Московского округа от 27.03.2025
№ Ф05-1552/2025 по делу № А40-12676/2024) и `n-pdn.ru/judical/...`, плюс карточка
движения дела на `base.garant.ru/66323504/`. Хронология дословно с карточки ГАРАНТа:

```
05.07.2024  Решение Арбитражного суда г. Москвы N А40-12676/2024
19.11.2024  Постановление Девятого ААС N 09АП-55619/2024
27.03.2025  Постановление Арбитражного суда Московского округа N Ф05-1552/2025
Истец: СНТ "ЯКОРЬ"   Ответчик: УПРАВЛЕНИЕ РОСКОМНАДЗОРА ПО ЦФО
```

Резолютивная часть кассации, дословно (consultant.ru, карточка дела):

> «Решение: **В удовлетворении требования отказано**, поскольку уполномоченный орган
> по защите прав субъектов персональных данных имеет право запрашивать у физических
> или юридических лиц информацию, необходимую для реализации своих полномочий…»

И дословно из мотивировки (n-pdn.ru, текст постановления):

> «…постановление Девятого арбитражного апелляционного суда от 19.11.2024 **подлежит
> отмене**, а решение Арбитражного суда города Москвы от 05.07.2024 — **оставлению в силе**.»

🔴 **То есть СНТ «Якорь» дело ПРОИГРАЛО**, а не выиграло. Формулировка подагента
«бремя доказывания автоматизации суд возложил на РКН, который его не вынес» относится
к ОДНОМУ выводу внутри акта, а не к исходу.

При этом сам вывод про автоматизацию кассация действительно подтвердила, дословно:

> «Вывод суда первой инстанции об осуществлении товариществом обработки персональных
> данных с использованием средств автоматизации основан лишь на том обстоятельстве,
> что сбор персональных данных осуществляется с помощью вычислительной техники через
> сайт в информационно-телекоммуникационной сети Интернет, однако каких-либо
> доказательств, подтверждающих, что товариществом используется программа,
> осуществляющая обработку персональных данных в автоматизированном режиме без участия
> человека, материалы дела не содержат.»

> «**Данный вывод суда апелляционной инстанции является верным.** Однако судом
> апелляционной инстанции не учтено следующее…» — дальше кассация отменяет по другому
> основанию: письмо РКН носило «лишь информационный характер».

**Что из этого можно брать, а что нельзя.** Брать можно тезис: «сбор через сайт сам по
себе не равен автоматизированной обработке, доказывать автоматизацию должен РКН».
Нельзя брать: будто суд поддержал оператора — он отказал ему. Плюс фактура дела от нашей
далека: СНТ ведёт реестр членов вручную по 217-ФЗ, «в отношении членов СНТ, а не
неопределённого круга лиц». У нас программа именно «самостоятельно переформатирует
данные и выбирает их по заданным параметрам» — то есть по критерию ЭТОГО ЖЕ акта наш
разбор выписки автоматизирован **где бы он ни выполнялся**. Довод в нашу пользу этот
акт даёт слабый.

#### Ж-08б. Побочная, но точная находка: порог ч. 14 ст. 13.11 КоАП дословно

Постановление Девятого ААС от 03.06.2026 № 09АП-15707/2026 по делу № А40-351064/2025
(ООО «ЮКИДС»), карточка `consultant.ru` (base=MARB, n=3119581). Дословно:

> «Ввиду наличия в скомпрометированной базе данных **более ста тысяч субъектов
> персональных данных и (или) более одного миллиона идентификаторов**, указанные
> действия образуют состав административного правонарушения по ч. 14 ст. 13.11 КоАП РФ.»

Это прямо подтверждает счётную посылку темы Г59 (10 000 пользователей × >100 строк =
>1 млн идентификаторов на сервере). Фактура дела: утечка ~500 000 строк из «Битрикс 24»,
состав — по объёму идентификаторов, а не по тяжести данных.

#### Ж-08в. Канал `rkn.gov.ru` — попытка и код

`curl -s "https://r.jina.ai/https://rkn.gov.ru/personal-data/p663/"` → **422**,
683 байта, тело — ошибка самого прокси, дословно:
`"Failed to goto https://rkn.gov.ru/personal-data/p663/: TimeoutError: page.goto:
Timeout 15000ms exceeded"`. Это таймаут прокси, не отказ сайта. Ступень «браузер»
по этому домену — ниже.

#### Ж-08г. Браузер по доменам РКН — ступень пройдена, результат отрицательный и точный

Канал: `chrome-devtools new_page` / `navigate_page` / `evaluate_script`. Вкладка закрыта
за собой (`close_page`), чужие не тронуты.

| URL | что вернул браузер |
|---|---|
| `rkn.gov.ru/personal-data/p663/` | страница живёт, заголовок **«Страница не найдена»** (адрес устарел) |
| `rkn.gov.ru/personal-data/` | то же — **«Страница не найдена»**, раздела с таким адресом нет |
| `pd.rkn.gov.ru/` | **открылся полностью**, «Портал персональных данных — Обращения граждан» |
| `pd.rkn.gov.ru/code/` | **открылся**, «Кодекс добросовестных практик» / «Кодекс этической деятельности (работы) в сети Интернет», 5 608 знаков текста |

🔴 **Домены РКН доступны и не блокируют нас** — «не добыто по вине сайта» здесь незаконно.
Отрицательный результат другой: **на Портале персональных данных РАЗДЕЛА С РАЗЪЯСНЕНИЯМИ
НЕТ ВОВСЕ.** Полное меню портала, снятое с `take_snapshot`: Главная · Об уполномоченном
органе · Кодекс добросовестных практик · Реестр нарушителей · Реестр операторов ·
Инциденты (утечки ПД) · Трансграничная передача · Молодежная палата Консультативного
совета · Согласие на обработку ПД, разрешенных для распространения. Ни FAQ, ни
«разъяснения», ни «методические рекомендации».

Попутно снятое число с главной портала, дословно: «В настоящее время в реестре содержится
информация о **2 651 718** операторах персональных данных».

Текст «Кодекса добросовестных практик» проверен программно на ключевые слова темы
(`evaluate_script` по `document.body.innerText`), результат дословно:

```
устройств: нет | локальн: нет | на стороне клиента: нет | браузер: нет |
обезличив: нет | минимизац: нет
```

То есть Кодекс вопроса об обработке на устройстве не касается ни единым словом.

**Вывод по каналу:** отсутствие позиции регулятора по on-device обработке — это теперь
не «мы не искали», а замеренный факт по двум официальным доменам. Класс остатка
понижаю с 🟢 до 🟢-частично: остались `sudact.ru` / `kad.arbitr.ru` (поиск практики
по ключевым словам) и профильные юрфирмы; сам регулятор проверен.

---

## Итог: ответы на шесть вопросов темы

| № | Вопрос | Ответ по замерам |
|---|---|---|
| 1 | Чем в браузере разбирают PDF без ML | **pdf.js** (`pdfjs-dist@6.3.289`, Apache-2.0, 0 зависимостей, 494 КБ gzip) отдаёт позиционированные `TextItem` (`transform`, `width`, `height`) и операторный поток. **`pdf-lib` отпадает** — текст не извлекает вообще (ответ автора, issue #93), npm-релиза нет с 2022. **`mupdf.js` отпадает по лицензии** — AGPL-3.0-or-later. **PDFium через WASM** (`@embedpdf/pdfium@2.15.1`, MIT-обёртка, BSD-3 ядро) — самый богатый API, цена 4,43 МБ `.wasm` |
| 2 | 🔴 Переносится ли приём с линиями | **ДА, переносится. Это переписывание, а не смена алгоритма.** pdf.js: `getOperatorList()` → `OPS.constructPath (91)` с аргументами `[paintOp, [Float32Array], [minX,minY,maxX,maxY]]`. PDFium: прямее — `FPDFPageObj_GetType` / `FPDFPageObj_GetBounds` / `FPDFPageObj_GetStrokeWidth` / `FPDFPath_GetPathSegment`. **Цена у pdf.js: CTM надо вести самому** (в `buildPath` координаты не умножаются на матрицу, тогда как у `TextItem` уже device space), `DrawOPS` не экспортирован, и **формат `constructPath` менялся между v4 и v6 несовместимо**. Плюс отдельно: зависимость от линий — свойство НАШЕЙ настройки (`extract_tables()` на дефолте `"lines"`), у pdfplumber есть и `"text"`-стратегия (`words_to_edges_h/v`), а `table.py` с нулём внешних импортов переносим на TypeScript построчно |
| 3 | Python в браузере | Путь **существует и уже применён чужим продуктом**. `pdfminer.six` — чистый Python (`py3-none-any`), в Pyodide не входит, но ставится `micropip`. Блокирующих бинарных зависимостей нет: `pypdfium2` и `PIL` импортируются только в `display.py`, а `page.py` подключает его лениво — значит `micropip.install("pdfplumber", deps=False)` работает. `cryptography` (жёсткий импорт в `pdfminer/pdfdocument.py`) Pyodide даёт (45.0.5). **Цена: ~12,9 МБ по сети** (ядро 5,03 МБ br + `pdfminer.six` 6,29 МБ + `cryptography` 923 КБ) **и 4–5 с инициализации** (цифра самого проекта) |
| 4 | Кто так уже делает | **`PriyanshuDangi/localbankstatementconverter` — MIT, пуш 25.04.2026, делает ровно нашу задачу ровно третьим путём**: Pyodide + `pdfminer.six` в Web Worker, «there is no backend», таблица тремя уровнями (рамки → координаты слов → текст) — совпадает с независимым выводом нашего Г20. Звёзд 1: приём проверен, репутация нет. **Actual Budget** (MIT, живой) — подтверждённый кодом local-first. **Firefly III — НЕ клиент** (свой сервер) и **PDF не умеет вовсе**. **Maybe Finance — архивирован**. По коду GitHub: pdf.js берут для выписок часто, но запускают в `backend/`/`electron/`, не в браузере |
| 5 | Цена решения | Загрузка: 494 КБ (pdf.js) / ~4,7 МБ (PDFium) / ~12,9 МБ (Pyodide). OCR сканов сверху: **~6,6 МБ** минимум (`tesseract-core-simd-lstm.wasm` 2 871 377 + `rus.traineddata` fast 3 861 738) или ~22,9 МБ на полной модели. Скорость разбора на слабом устройстве — **своего замера нет**, опора только на десктопные 14–57 мс/страница из Г20. Неизмеримые статьи: парсер чинится только релизом (а у Сбера 20 форматов, 5 новых за 2026), сбой чужой выписки не воспроизвести, `SharedArrayBuffer` требует COOP/COEP на раздаче |
| 6 | Гибрид и право РФ | **Позиции регулятора по on-device обработке НЕ СУЩЕСТВУЕТ** — проверено браузером: на `pd.rkn.gov.ru` раздела разъяснений нет в принципе, в «Кодексе добросовестных практик» слов «устройство», «локальн», «браузер», «обезличив» нет ни одного. 🔴 **Довод подагента про дело А40-12676/2024 мною исправлен: СНТ «Якорь» дело ПРОИГРАЛО**, кассация отменила апелляцию и оставила в силе первую инстанцию; вывод про неавтоматизированность подтверждён, но по критерию того же акта («программы самостоятельно переформатируют данные, выбирают по заданным параметрам») наш разбор автоматизирован где угодно. Точный порог ч. 14 ст. 13.11 КоАП подтверждён дословно по делу ЮКИДС: «более ста тысяч субъектов и (или) более одного миллиона идентификаторов». Образцы отраслевых формулировок границы — в файле подагента |

## Класс остатка

🔴 **Недоступных источников (поломка сайта) — НОЛЬ.** Все домены, к которым обращались,
отвечали.

🟡 **Действие владельца** — один пункт: коммерческая лицензия Artifex, если когда-нибудь
понадобится `mupdf.js` (AGPL-3.0-or-later несовместим с закрытым продуктом). Сейчас
не нужна — есть MIT/Apache-2.0 альтернативы.

🟢 **Наша невыполненная работа:**
1. **Своего замера скорости нет ни для одного пути.** Воспроизводимо на своих же
   `app/data/statement_templates/{sber,tinkoff,vtb,raiffeisen}.pdf` — те же четыре файла,
   на которых снят Г20. Пока перенос чисел с десктопа в браузер — догадка.
2. Не проверено, **сколько `constructPath`-записей** даёт реальная выписка ВТБ/Райффайзена
   и восстанавливаются ли из них те же рёбра, что видит pdfplumber. Это единственная
   проверка, которая превращает «переносится по документации» в «переносится по факту».
3. Исходники `localbankstatementconverter` построчно не читались — взят README. Там лежит
   готовая реализация трёхуровневого разбора под MIT.
4. `sudact.ru` / `kad.arbitr.ru` по ключевым словам «обработка на устройстве пользователя»
   не пройдены; профильные юрфирмы (Digital Rights Center, РАЭК) — тоже.
5. Восемь пунктов остатка первого подагента — в конце его файла
   `_g66_sub_practice_2026-09-22.md`, в том числе: код Actual построчно, российские
   браузерные конвертёры выписок на русском языке, расширения Chrome Web Store,
   проверка вкладки Network у заявляющих «no upload» конвертёров.
