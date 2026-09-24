# Тема 42 — сырьё подагента A (углы 3, 4, 6)

Снято 24.09.2026. Формат: дословная цитата + URL. Пересказ помечен `[пересказ]`.

---

## Угол 3. Числа и деньги в интерфейсе

### 3.1. CSS Fonts Module Level 4 — `font-variant-numeric` (первоисточник)

> Specifies control over numerical forms. The example below shows how some of these values can be combined to influence the rendering of tabular data with fonts that support these features. **Within normal paragraph text, proportional numbers are used while tabular numbers are used so that columns of numbers line up properly**

> `<numeric-figure-values> = [ lining-nums | oldstyle-nums ]`
> `<numeric-spacing-values> = [ proportional-nums | tabular-nums ]`
> `<numeric-fraction-values> = [ diagonal-fractions | stacked-fractions ]`

> Individual values have the following meanings:
> **normal** — None of the features listed below are enabled.
> **lining-nums** — Enables display of lining numerals (OpenType feature: `lnum`).
> **oldstyle-nums** — Enables display of old-style numerals (OpenType feature: `onum`).
> **proportional-nums** — Enables display of proportional numerals (OpenType feature: `pnum`).
> **tabular-nums** — Enables display of tabular numerals (OpenType feature: `tnum`).
> **diagonal-fractions** — Enables display of lining diagonal fractions (OpenType feature: `frac`).
> **stacked-fractions** — Enables display of lining stacked fractions (OpenType feature: `afrc`).
> **ordinal** — Enables display of letter forms used with ordinal numbers (OpenType feature: `ordn`).
> **slashed-zero** — Enables display of slashed zeros (OpenType feature: `zero`).

> Name: font-variant-numeric · Value: `normal | [ <numeric-figure-values> || <numeric-spacing-values> || <numeric-fraction-values> || ordinal || slashed-zero ]` · Initial: normal · Applies to: all elements and text · **Inherited: yes** · Computed value: as specified · Animation type: discrete

— источник: https://drafts.csswg.org/css-fonts-4/ (§6.7 «Numerical formatting: the font-variant-numeric property»; редакторская копия того же документа, что и https://www.w3.org/TR/css-fonts-4/ — w3.org отдаёт Cloudflare-челлендж на `curl`), снято 24.09.2026

[пересказ] Практический вывод для FINPILOT: `font-variant-numeric` наследуется, значит достаточно поставить `tabular-nums` на контейнер таблицы/денежного токена, а не на каждую ячейку; `slashed-zero` — отдельная опция, помогает отличать 0 от O в моноширинных суммах; `lining-nums` нужен, если шрифт по умолчанию отдаёт old-style (минускульные) цифры, которые в таблице прыгают по базовой линии.

### 3.2. GOV.UK Design System — таблицы с числами

> When comparing columns of numbers, align the numbers to the right in table cells.

> Use table headers to tell users what the rows and columns represent. Use the `scope` attribute to help users of assistive technology distinguish between row and column headers.

— источник: https://design-system.service.gov.uk/components/table/ , снято 24.09.2026

Реализация в коде самого дизайн-системы (govuk-frontend, `components/table/_mixin.scss`), дословно:

```scss
  .govuk-table__cell--numeric {
    @include base.govuk-font-tabular-numbers;
  }

  .govuk-table__header--numeric,
  .govuk-table__cell--numeric {
    text-align: right;
  }
```

— источник: https://raw.githubusercontent.com/alphagov/govuk-frontend/main/packages/govuk-frontend/src/govuk/components/table/_mixin.scss , снято 24.09.2026

[пересказ] То есть у GDS «числовая ячейка» = табличные цифры + выравнивание вправо, и это два разных класса: заголовок получает только выравнивание, ячейка — ещё и `tabular-nums`. В разметке это `format: "numeric"` у Nunjucks-макроса, то есть форматирование числа зашито в компонент таблицы, а не в прикладной код.

### 3.3. GOV.UK style guide — как писать числа и деньги

> Use the £ symbol: £75. Do not use decimals unless pence are included: £75.50 but not £75.00

> Use a 0 where there's no digit before the decimal point (for example, 0.5 not .5).

> Always use % with a number.

[пересказ] Остальное из той же статьи: числительные 2–9 цифрами в большинстве контекстов, «one» словом; число в начале предложения пишется словом; свыше 999 — запятая-разделитель тысяч (9,000); для отрицательных — знак минуса (−6); диапазоны через «to» («500 to 900», кроме таблиц); в таблицах — всегда цифры; для крупных денежных сумм слово полностью: £138 million, а не £138m; пенсы отдельно от фунтов пишутся словом («4 pence per minute»).

— источник: https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/style-guides/a-to-z-style-guide/ (бывший https://www.gov.uk/guidance/style-guide/a-to-z-of-gov-uk-style , 301-редирект), снято 24.09.2026

🔴 Прямо применимо к FINPILOT: правило «не показывать `,00`, если копеек нет» — у GDS это норма, а не вкус. Для нашего формата это значит: 12 500 ₽, а не 12 500,00 ₽, кроме случаев, когда в колонке есть суммы с копейками и нужна разрядная сетка.

### 3.4. 🔴 CLDR, локаль `ru` — канонический формат денег (первоисточник)

Символы локали `ru`, дословно из CLDR (`cldr-numbers-full/main/ru/numbers.json`, `symbols-numberSystem-latn`):

> `{"decimal": ",", "group": " ", "list": ";", "percentSign": "%", "plusSign": "+", "minusSign": "-", "approximatelySign": "≈", "exponential": "E", "superscriptingExponent": "×", "perMille": "‰", "infinity": "∞", "nan": "не число", "timeSeparator": ":"}`

🔴 Кодовые точки проверены побайтово, а не на глаз:
- `group` = **U+00A0 NO-BREAK SPACE** (`['0xa0']`) — разделитель разрядов в русской локали это **неразрывный пробел**, не обычный пробел и не U+202F;
- `decimal` = `,` (U+002C);
- `minusSign` = `-` (U+002D HYPHEN-MINUS), **не** U+2212 MINUS SIGN.

Форматы чисел, дословно:

> `decimalFormats.standard` = `#,##0.###`
> `currencyFormats.standard` = `#,##0.00 ¤`
> `currencyFormats.accounting` = `#,##0.00 ¤`

Кодовые точки паттерна валюты: `['0x23','0x2c','0x23','0x23','0x30','0x2e','0x30','0x30','0xa0','0xa4']` — то есть **число, затем U+00A0, затем знак валюты (¤)**. Знак валюты идёт ПОСЛЕ числа, отделён неразрывным пробелом.

`currencySpacing` (правило вставки пробела между числом и знаком валюты), дословно:

> `"beforeCurrency": {"currencyMatch": "[[:^S:]&[:^Z:]]", "surroundingMatch": "[:digit:]", "insertBetween": " "}`
> `"afterCurrency": {"currencyMatch": "[[:^S:]&[:^Z:]]", "surroundingMatch": "[:digit:]", "insertBetween": " "}`

— источник: https://raw.githubusercontent.com/unicode-org/cldr-json/main/cldr-json/cldr-numbers-full/main/ru/numbers.json (официальный JSON-дистрибутив CLDR консорциума Unicode, `unicode-org/cldr-json`), снято 24.09.2026

Реквизиты рубля в CLDR (`currencies.json`, `ru` → `RUB`), дословно:

> `{"displayName": "российский рубль", "displayName-count-one": "российский рубль", "displayName-count-few": "российских рубля", "displayName-count-many": "российских рублей", "displayName-count-other": "российского рубля", "symbol": "₽", "symbol-alt-narrow": "₽"}`

— источник: https://raw.githubusercontent.com/unicode-org/cldr-json/main/cldr-json/cldr-numbers-full/main/ru/currencies.json , снято 24.09.2026

Знак рубля в базе символов Unicode (UCD, `UnicodeData.txt`), дословная строка:

> `20BD;RUBLE SIGN;Sc;0;ET;;;;;N;;;;;`

Для сравнения — сопутствующие символы, дословно:

> `00A0;NO-BREAK SPACE;Zs;0;CS;<noBreak> 0020;;;;N;NON-BREAKING SPACE;;;;`
> `202F;NARROW NO-BREAK SPACE;Zs;0;CS;<noBreak> 0020;;;;N;;;;;`
> `20AC;EURO SIGN;Sc;0;ET;;;;;N;;;;;`

— источник: https://www.unicode.org/Public/UCD/latest/ucd/UnicodeData.txt , снято 24.09.2026

🔴 Что из этого следует прямо для FINPILOT (совпадение с правилом §6 CLAUDE.md подтверждено первоисточником): формат `12 500,00 ₽` = `#,##0.00` + U+00A0 + U+20BD, где U+00A0 стоит И между разрядами, И перед знаком рубля. Категория U+20BD — `Sc` (Symbol, currency), то есть это именно валютный символ, а не буква; плюрализация слова «рубль» в CLDR четырёхформенная (one/few/many/other), поэтому текстовые подписи вида «5 рублей» нельзя собирать конкатенацией — нужен plural-rules движок (`Intl.PluralRules('ru')`).

[пересказ] Практический вывод по реализации: `Intl.NumberFormat('ru-RU', {style:'currency', currency:'RUB'})` даёт ровно этот паттерн из CLDR, включая U+00A0; ручная сборка строки почти наверняка подставит обычный пробел U+0020 и сломает перенос строки между числом и знаком рубля.
