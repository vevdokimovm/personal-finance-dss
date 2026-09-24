# Тема 42, угол 6 — доступность (a11y) финансовых таблиц и графиков. ПЕРВИЧНОЕ СЫРЬЁ

Дата снятия всех источников: **24.09.2026**. Синтеза нет, только дословные цитаты с URL.

---

## A. WCAG 2.1 (W3C Recommendation)

Источник: https://www.w3.org/TR/WCAG21/
Канал добычи: `WebFetch` (дал только пересказ, не дословно) → `curl` с браузерным UA → **403** →
`curl -s "https://r.jina.ai/https://www.w3.org/TR/WCAG21/"` → **HTTP 200, 189 304 байта**, полный текст.
Снято 24.09.2026.

### A.0 🔴 Что нормативно, а что нет — дословно

> «The main content of WCAG 2.1 is **normative** and defines requirements that impact conformance
> claims. Introductory material, appendices, sections marked as "non-normative", diagrams, examples,
> and notes are **informative** (non-normative). Non-normative material provides advisory information
> to help interpret the guidelines but does not create requirements that impact a conformance claim.»
> — https://www.w3.org/TR/WCAG21/#conformance (раздел 5 Conformance)

> «**Sufficient and Advisory Techniques** — For each of the _guidelines_ and _success criteria_ in the
> WCAG 2.1 document itself, the working group has also documented a wide variety of _techniques_.
> **The techniques are informative** and fall into two categories: those that are _sufficient_ for
> meeting the success criteria and those that are _advisory_. The advisory techniques go beyond what
> is required by the individual success criteria and allow authors to better address the guidelines.
> Some advisory techniques address accessibility barriers that are not covered by the testable success
> criteria. Where common failures are known, these are also documented.»
> — https://www.w3.org/TR/WCAG21/#wcag-2-layers-of-guidance

> «Content identified as "informative" or "non-normative" is **never required for conformance**.»
> — глоссарий, https://www.w3.org/TR/WCAG21/#dfn-normative

**Вывод для разметки ниже:** нормативны только тексты Success Criterion (SC) и глоссарные термины,
на которые они ссылаются. Всё из `Understanding/...` и `Techniques/...` — **информативно** (в т.ч.
H43, H51 и tutorial «Complex Images»).

### A.1 SC 1.1.1 Non-text Content (Level A) — НОРМАТИВНО

> «All non-text content that is presented to the user has a text alternative that serves the equivalent
> purpose, except for the situations listed below.
>
> **Controls, Input**
> If non-text content is a control or accepts user input, then it has a name that describes its purpose.
> (Refer to Success Criterion 4.1.2 for additional requirements for controls and content that accepts
> user input.)
>
> **Time-Based Media**
> If non-text content is time-based media, then text alternatives at least provide descriptive
> identification of the non-text content. (Refer to Guideline 1.2 for additional requirements for media.)
>
> **Test**
> If non-text content is a test or exercise that would be invalid if presented in text, then text
> alternatives at least provide descriptive identification of the non-text content.
>
> **Sensory**
> If non-text content is primarily intended to create a specific sensory experience, then text
> alternatives at least provide descriptive identification of the non-text content.
>
> **CAPTCHA**
> If the purpose of non-text content is to confirm that content is being accessed by a person rather
> than a computer, then text alternatives that identify and describe the purpose of the non-text content
> are provided, and alternative forms of CAPTCHA using output modes for different types of sensory
> perception are provided to accommodate different disabilities.
>
> **Decoration, Formatting, Invisible**
> If non-text content is pure decoration, is used only for visual formatting, or is not presented to
> users, then it is implemented in a way that it can be ignored by assistive technology.»
> — https://www.w3.org/TR/WCAG21/#non-text-content

Guideline 1.1 (текст руководства, нормативен как рамка):
> «Provide text alternatives for any non-text content so that it can be changed into other forms people
> need, such as large print, braille, speech, symbols or simpler language.»

### A.2 SC 1.3.1 Info and Relationships (Level A) — НОРМАТИВНО

> «Information, structure, and relationships conveyed through presentation can be programmatically
> determined or are available in text.»
> — https://www.w3.org/TR/WCAG21/#info-and-relationships

Guideline 1.3:
> «Create content that can be presented in different ways (for example simpler layout) without losing
> information or structure.»

### A.3 SC 1.4.1 Use of Color (Level A) — НОРМАТИВНО

> «Color is not used as the only visual means of conveying information, indicating an action, prompting
> a response, or distinguishing a visual element.
>
> **Note**
> This success criterion addresses color perception specifically. Other forms of perception are covered
> in Guideline 1.3 including programmatic access to color and other visual presentation coding.»
> — https://www.w3.org/TR/WCAG21/#use-of-color

Guideline 1.4:
> «Make it easier for users to see and hear content including separating foreground from background.»

### A.4 SC 1.4.3 Contrast (Minimum) (Level AA) — НОРМАТИВНО

> «The visual presentation of text and images of text has a contrast ratio of at least **4.5:1**, except
> for the following:
>
> **Large Text**
> Large-scale text and images of large-scale text have a contrast ratio of at least **3:1**;
>
> **Incidental**
> Text or images of text that are part of an inactive user interface component, that are pure decoration,
> that are not visible to anyone, or that are part of a picture that contains significant other visual
> content, have no contrast requirement.
>
> **Logotypes**
> Text that is part of a logo or brand name has no contrast requirement.»
> — https://www.w3.org/TR/WCAG21/#contrast-minimum

Глоссарные определения, на которые SC ссылается (нормативны):
- **large scale (text)** — «with at least **18 point or 14 point bold** or font size that would yield
  equivalent size for Chinese, Japanese and Korean (CJK) fonts» — https://www.w3.org/TR/WCAG21/#dfn-large-scale
- **contrast ratio** — «(L1 + 0.05) / (L2 + 0.05), where …» — https://www.w3.org/TR/WCAG21/#dfn-contrast-ratio

Для сравнения, SC 1.4.6 Contrast (Enhanced) (Level **AAA**) — 7:1, крупный текст 4.5:1 (в AA не входит).

### A.5 SC 1.4.4 Resize text (Level AA) — НОРМАТИВНО

> «Except for captions and images of text, text can be resized without assistive technology up to
> **200 percent** without loss of content or functionality.»
> — https://www.w3.org/TR/WCAG21/#resize-text

### A.6 SC 1.4.10 Reflow (Level AA) — НОРМАТИВНО 🔴 таблицы прямо в исключении

> «Content can be presented without loss of information or functionality, and without requiring scrolling
> in two dimensions for:
>
> *   Vertical scrolling content at a width equivalent to **320 CSS pixels**;
> *   Horizontal scrolling content at a height equivalent to **256 CSS pixels**.
>
> **Except for parts of the content which require two-dimensional layout for usage or meaning.**
>
> **Note 1**
> 320 CSS pixels is equivalent to a starting viewport width of 1280 CSS pixels wide at 400% zoom. For web
> content which is designed to scroll horizontally (e.g., with vertical text), 256 CSS pixels is equivalent
> to a starting viewport height of 1024 CSS pixels at 400% zoom.
>
> **Note 2**
> Examples of content which requires two-dimensional layout are images required for understanding (such as
> maps and diagrams), video, games, presentations, **data tables (not individual cells)**, and interfaces
> where it is necessary to keep toolbars in view while manipulating content. It is acceptable to provide
> two-dimensional scrolling for such parts of the content.»
> — https://www.w3.org/TR/WCAG21/#reflow

🔴 Обратить внимание: **«data tables (not individual cells)»** — исключение относится к таблице как
целому, но не даёт права на двумерный скролл внутри отдельной ячейки. И Note 2 — это **Note**,
то есть по разделу 5 Conformance формально информативная часть; нормативна фраза «Except for parts of
the content which require two-dimensional layout for usage or meaning».

### A.7 SC 1.4.11 Non-text Contrast (Level AA) — НОРМАТИВНО 🔴 ключевое для графиков

> «The visual presentation of the following have a contrast ratio of at least **3:1** against adjacent
> color(s):
>
> **User Interface Components**
> Visual information required to identify user interface components and states, except for inactive
> components or where the appearance of the component is determined by the user agent and not modified
> by the author;
>
> **Graphical Objects**
> Parts of graphics **required to understand the content**, except when a particular presentation of
> graphics is essential to the information being conveyed.»
> — https://www.w3.org/TR/WCAG21/#non-text-contrast

### A.8 Смежные AA-критерии, задевающие таблицы и графики (сняты попутно, дословно)

SC **1.4.12 Text Spacing** (Level AA):
> «In content implemented using markup languages that support the following text style properties, no loss
> of content or functionality occurs by setting all of the following and by changing no other style property:
> *   Line height (line spacing) to at least 1.5 times the font size;
> *   Spacing following paragraphs to at least 2 times the font size;
> *   Letter spacing (tracking) to at least 0.12 times the font size;
> *   Word spacing to at least 0.16 times the font size.»
> — https://www.w3.org/TR/WCAG21/#text-spacing

SC **1.4.13 Content on Hover or Focus** (Level AA) — прямо про тултипы графиков:
> «Where receiving and then removing pointer hover or keyboard focus triggers additional content to become
> visible and then hidden, the following are true:
> **Dismissible** A mechanism is available to dismiss the additional content without moving pointer hover
> or keyboard focus, unless the additional content communicates an input error or does not obscure or
> replace other content;
> **Hoverable** If pointer hover can trigger the additional content, then the pointer can be moved over the
> additional content without the additional content disappearing;
> **Persistent** The additional content remains visible until the hover or focus trigger is removed, the
> user dismisses it, or its information is no longer valid.
> Exception: The visual presentation of the additional content is controlled by the user agent and is not
> modified by the author.
> **Note 2** Custom tooltips, sub-menus, and other nonmodal popups that display on hover and focus are
> examples of additional content covered by this criterion.»
> — https://www.w3.org/TR/WCAG21/#content-on-hover-or-focus

SC **1.3.3 Sensory Characteristics** (Level A):
> «Instructions provided for understanding and operating content do not rely solely on sensory
> characteristics of components such as shape, color, size, visual location, orientation, or sound.
> **Note** For requirements related to color, refer to Guideline 1.4.»
> — https://www.w3.org/TR/WCAG21/#sensory-characteristics

SC **1.3.4 Orientation** (Level AA):
> «Content does not restrict its view and operation to a single display orientation, such as portrait or
> landscape, unless a specific display orientation is essential.»
> — https://www.w3.org/TR/WCAG21/#orientation

---

## A.9 Understanding 1.4.11 Non-text Contrast — 🔴 ИНФОРМАТИВНО, но прямо разбирает графики

Источник: https://www.w3.org/WAI/WCAG21/Understanding/non-text-contrast.html
Канал: `curl -s https://r.jina.ai/...` → **HTTP 200, 51 760 байт**. Снято 24.09.2026.
Статус: **Understanding-документ не нормативен** (см. A.0).

> «The intent of this success criterion is to ensure that user interface components (i.e., controls) and
> meaningful graphics are distinguishable by people with moderately low vision. The requirements and
> rationale are similar to those for large text in 1.4.3 Contrast (Minimum). Note that this requirement
> does not apply to _inactive_ user interface components.»

### Что такое «graphical object» — дословно

> «The term "graphical object" applies to stand-alone icons such as a print icon (with no text), and the
> important parts of a more complex diagram **such as each line in a graph**. For simple graphics such as
> single-color icons the entire image is a graphical object. Images made up of multiple lines, colors and
> shapes will be made of multiple graphical objects, some of which are required for understanding.»

> «Not every graphical object needs to contrast with its surroundings — only those that are required for
> a user to understand what the graphic is conveying. Gestalt principles such as the "law of continuity"
> can be used to ignore minor overlaps with other graphical objects or colors.»

### Линейный график (Figure 38) — дословно

> «Figure 38. In order to understand the graph you need to discern the lines and shapes for each condition.
> To perceive the values of each line along the chart you need to discern the grey lines marking the
> graduated 100 value increments.
>
> The graphical objects are **the lines in the graph, including the background lines for the values, and
> the colored lines with shapes**.»
(иллюстрация: https://www.w3.org/WAI/WCAG21/Understanding/img/simple-line-graph.png)

### Круговая диаграмма (Figure 39) — дословно

> «Figure 39. To understand the pie chart you have to discern each slice of the pie chart from the others.
>
> The graphical objects are the slices of the pie (chart).
>
> **Note:** If the values of the pie chart slices were also presented in a conforming manner (see the Pie
> Charts example for details), the slices would not be required for understanding.»

### 🔴 Когда контраст 3:1 для графики НЕ требуется — дословно

> «The term "required for understanding" is used in the success criterion as many graphics do not need to
> meet the contrast requirements. If a person needs to perceive a graphic, or part of a graphic (a
> graphical object) in order to understand the content it should have sufficient contrast. However, that
> is not a requirement when:
>
> *   A graphic with text embedded or overlaid conveys the same information, such as labels _and_ values
>     on a chart.
> *   The graphic is for aesthetic purposes that does not require the user to see or understand it to
>     understand the content or use the functionality.
> *   **The information is available in another form, such as in a table that follows the graph, which
>     becomes visible when a "Long Description" button is pressed.**
> *   The graphic is part of a logo or brand name (which is considered "essential" to its presentation).»

### Ховер/фокус на сегментах графика (Figure 42) — дословно

> «Some graphics may have interactions that either vary the contrast, or display the information as text
> when you mouseover/tap/focus each graphical object. In order for someone to discern the graphics exist
> at all, **the unfocused default version must already have sufficiently contrasting colors or text**. For
> the area that receives focus, information can then be made available dynamically as pop-up text, or be
> foregrounded dynamically by increasing the contrast.»
> «Figure 42. A dynamic chart where the current 'slice' is hovered or focused, which activates the
> associated text display of the values and highlights the series»

### Инфографика (общий случай — любой график с данными) — дословно

> «Infographics can mean any graphic conveying data, such as a chart or diagram. On the web it is often
> used to indicate a large graphic with lots of statements, pictures, charts or other ways of conveying
> data. In the context of graphics contrast, **each item within such an infographic should be treated as
> a set of graphical objects**, regardless of whether it is in one file or separate files.»

> «An infographic can use text which meets the other criteria to minimize the number of graphical objects
> required for understanding. For example, using text with sufficient contrast to provide the values in a
> chart. **A long description would also be sufficient** because then the infographic is not relied upon
> for understanding.»

### Градиенты и процедура проверки — дословно

> «Gradients can reduce the apparent contrast between areas, and make it more difficult to test. The
> general principles is to identify the graphical object(s) required for understanding, and take the
> central color of that area. If you remove the adjacent color which does not have sufficient contrast,
> can you still identify and understand the graphical object?»

> «Identify each graphic on the page that includes information required for understanding the content
> (i.e., excluding graphics which have visible text for the same information, or are decorative) and:
> Check the contrast of the graphical object against its adjacent colors…»

### Соотношение 1.4.11 и 1.4.1 Use of Color — дословно

> «The Use of Color success criterion addresses changing **only the color** (hue) of an object or text
> without otherwise altering the object's form. The principle is that contrast ratio (the difference in
> brightness) can be used to distinguish text or graphics. For example, G183: Using a contrast ratio of at
> least 3:1 to distinguish inline text links from surrounding text is a technique to use a contrast ratio
> of 3:1 with surrounding text to distinguish links and controls. In that case the Working Group regards a
> link color that meets the 3:1 contrast ratio relative to the non-linked text color as satisfying the
> Success Criterion 1.4.1 Use of color since it is relying on contrast ratio as well as color (hue) to
> convey that the text is a link.»

> «This success criterion does not require that changes in color that differentiate between states of an
> individual component meet the 3:1 contrast ratio when they do not appear next to each other. For example,
> there is not a new requirement that visited links contrast with the default color, or that mouse hover
> indicators contrast with the default state. However, the component must not lose contrast with the
> adjacent colors, and non-text indicators such as the check in a checkbox, or an arrow graphic indicating
> a menu is selected or open must have sufficient contrast to the adjacent colors.»

---

## A.10 Understanding 1.4.1 Use of Color — про легенды графиков (ИНФОРМАТИВНО)

Источник: https://www.w3.org/WAI/WCAG21/Understanding/use-of-color.html
Канал: `r.jina.ai` → HTTP 200, 12 230 байт. Снято 24.09.2026.

Пример с легендой (дословно):
> «**An examination.** Students view an SVG image of a chemical compound and identify the chemical
> elements present based **both** on the colors used, as well as numbers next to each element. **A legend
> shows the color and number for each type of element.** Sighted users who cannot perceive all the color
> differences can still understand the image by relying on the numbers.»

Пример с формой (дословно):
> «A form contains both required and optional fields. Instructions at the top of the form explain that
> required fields are labeled with red text and also with an icon. Users who cannot perceive the
> difference between the optional field labels and the red labels for the required fields will still be
> able to see the icon next to the red labels.»

---

## A.11 Техники для таблиц — 🔴 ИНФОРМАТИВНЫ (оговорка процитирована ниже)

### Общая оговорка W3C, повторяемая в шапке каждой техники — дословно

> «**Techniques are examples of ways to meet Web Content Accessibility Guidelines (WCAG). They are not
> required to meet WCAG. Content can satisfy the normative requirements of WCAG even if it does not use
> any of the documented techniques.** See About WCAG Techniques.»
> — https://www.w3.org/WAI/WCAG21/Techniques/html/H43 и https://www.w3.org/WAI/WCAG21/Techniques/html/H51

Шапка раздела техник: «WCAG 2.1 Techniques — **Examples of ways to meet WCAG; not required**».

### H51: Using table markup to present tabular information

Источник: https://www.w3.org/WAI/WCAG21/Techniques/html/H51 (`r.jina.ai`, HTTP 200, 5 496 байт, 24.09.2026)

> «This technique relates to 1.3.1 Info and Relationships (**Sufficient** when used for making information
> and relationships conveyed through presentation programmatically determinable). This technique applies
> to HTML.»

> «The objective of this technique is to present tabular information in a way that preserves relationships
> within the information even when users cannot see the table or the presentation format is changed.
> **Information is considered tabular when logical relationships among text, numbers, images, or other data
> exist in two dimensions (vertical and horizontal).** These relationships are represented in columns and
> rows, and the columns and rows must be recognizable in order for the logical relationships to be
> perceived.»

> «Using the `table` element with the child elements `tr`, `th`, and `td` makes these relationships
> perceivable. Techniques such as inserting tabs to create columns or using the `pre` element are purely
> visual, and visually implied logical relationships are lost if the user cannot see the table or the
> visual presentation is changed.»

> «Simple tables generally have only one level of headers for columns and/or one level of headers on the
> rows. Usually, for simple tables, row 1 column 1 is either blank or describes the contents of the entire
> column 1. Row 1 columns are not blank (i.e., they contain "column headings"), describe the contents of
> the entire column… Column 1 rows are usually not blank, they often contain "row headings" which describe
> the contents of the entire row…»

> «Screen readers speak header information that changes as the user navigates the table. Thus, when screen
> reader users move to left or right along a row, they will hear the day of the week (the column header)
> followed by the appointment (if any). They will hear the time interval as they move up or down within the
> same column.»

Образец разметки из техники (`scope="row"` на заголовках строк):
```html
<table>
  <tr>
    <th>Time</th>
    <th>Monday</th>
    <th>Tuesday</th>
    …
  </tr>
  <tr>
    <th scope="row">8:00-9:00</th>
    <td>Meet with Sam</td>
    …
  </tr>
</table>
```

### H43: Using id and headers attributes to associate data cells with header cells in data tables

Источник: https://www.w3.org/WAI/WCAG21/Techniques/html/H43 (`r.jina.ai`, HTTP 200, 3 895 байт, 24.09.2026)

> «This technique relates to 1.3.1 Info and Relationships (**Sufficient** when used for making information
> and relationships conveyed through presentation programmatically determinable).»

> «The objective of this technique is to associate each data cell (in a data table) with the appropriate
> headers. This technique adds a `headers` attribute to each data cell (`td` element). It also adds an `id`
> attribute to any cell used as a header for other cells. The `headers` attribute of a cell contains a list
> of the `id` attributes of the associated header cells. If there is more than one `id`, they are separated
> by spaces.»

> «This technique is used when data cells are associated with **more than one row and/or one column
> header**. This allows screen readers to speak the headers associated with each data cell when the
> relationships are too complex to be identified using the `th` element alone or the `th` element with the
> `scope` attribute. Using this technique also makes these complex relationships perceivable when the
> presentation format changes.»

> «This technique is **not recommended for layout tables** since its use implies a relationship between
> cells that is not meaningful when tables are used for layout.»

Процедура проверки (дословно):
> «1. Check for layout tables: determine whether the content has a relationship with other content in both
> its column and its row. If "no", the table is a layout table. If "yes", the table is a data table.
> 2. For data tables, check that any cell that is associated with more than one row and/or one column header
> contains a `headers` attribute that lists the `id` for all headers associated with that cell.
> 3. For data tables where any cell contains an `id` or `headers` attribute: … Check that each `id` listed
> in the `headers` attribute of the data cell matches the `id` attribute of a cell that is used as a header
> element. … Check that all `id`s are unique (that is, no two elements in the page have the same `id`).»

Связанное Test Rule (не обязательно для соответствия — дословно):
> «The following are Test Rules related to this Technique. **It is not necessary to use these particular
> Test Rules to check for conformance with WCAG**, but they are defined and approved test methods.
> * Headers attribute specified on a cell refers to cells in the same table element»

---

## A.12 WAI Tutorial «Complex Images» — 🔴 ИНФОРМАТИВНО, но прямо про графики и таблицу как альтернативу

Источник: https://www.w3.org/WAI/tutorials/images/complex/
Канал: `r.jina.ai` → HTTP 200, 5 777 байт. Дата публикации страницы по заголовку ответа: **Wed, 23 Sep 2026 16:57:59 GMT**. Снято 24.09.2026.

> «There are situations where the composition of an image is important and needs to be provided in the long
> description. For example, **the sequence of colors used and the relative heights of the columns in a bar
> chart** may be relevant information about the structure of the chart, in addition to the actual values and
> trends that it depicts.»

> «Complex images can be difficult to understand by many people – especially those with low vision, learning
> disabilities, and limited subject-matter experience. **Make long descriptions available to everyone** to
> reach a wider audience with your content. For example, show the description as part of the main content.
> It may also be possible to reduce unnecessary complexity in your images and make them easier to understand
> for everyone.»

> «It is also good practice to refer to and summarize more complex images from the accompanying text. For
> example, a reference such as "The following graph shows that visitors were lost in the first quarter, but
> the numbers recovered in the second quarter" helps to point out the relevant information that the image is
> intended to present.»

Пример 1 — столбчатая диаграмма (дословно):
> «In this example, a bar chart of website visitor statistics has the short description "Bar chart showing
> monthly and total visitors for the first quarter 2025 for sites 1 to 3", provided through the `alt`
> attribute of the image. The long description provides detailed information, including scales, values,
> relationships and trends that are represented visually. For example, the long description can point out
> the declining values for site 1, consistent values for site 2, and increasing values for site 3 that are
> encoded in the bar chart.»

Три подхода (дословные заголовки и суть):
> «**Approach 1:** A text link to the long description adjacent to the image … All web browsers and
> assistive technologies support this approach. The long descriptions are available to everyone, including
> search engines and other programs. However, the link is not associated with the image in a semantic way.»
> «The HTML5 `<figure>` and `<figcaption>` elements can be used to group image and link semantically. Adding
> `role="group"` to the figure maintains backward compatibility…»

> «**Approach 2:** Describing the location of the long description in the `alt` attribute. When a long
> description is provided on the same web page as an image, its location can be described using the `alt`
> attribute of the image.»

> «**Approach 3:** Structurally associating the image and its adjacent long description (HTML5). The HTML5
> `<figure>` element can be used to enclose both the image and its long description. **The long description
> (presented as headings, text, and a table)** is wrapped in the `<figcaption>` element.»

🔴 Ограничение `aria-describedby` — дословно (прямо запрещает таблицу как значение describedby):
> «The WAI-ARIA `aria-describedby` attribute can be used to link to a description of the image that is
> provided anywhere on the same web page. The value of the attribute is the `id` of the element that
> provides the long description.
>
> **Important:** The element referenced by `aria-describedby` is treated as one continuous paragraph of
> text. **Screen readers and other assistive technology do not have access to structural information, such
> as any headings and tables.** They will read out or provide the text of any contained elements without
> indicating their structural relationships, and without the corresponding navigation mechanisms. As a
> result, this approach only works for long descriptions that are text-only, without needing structural
> information as was needed in the previous example.»

---

# B. ГОСТ Р 52872-2019 (РФ)

Полное наименование: **«Интернет-ресурсы и другая информация, представленная в электронно-цифровой
форме. Приложения для стационарных и мобильных устройств, иные пользовательские интерфейсы.
Требования доступности для людей с инвалидностью и других лиц с ограничениями жизнедеятельности»**
(англ. «Internet resources and other digital content. Software applications and user interfaces.
Accessibility requirements for persons with disabilities and other special needs»). ОКС 11.180.30.

**Канал добычи:** `curl -s "https://r.jina.ai/https://docs.cntd.ru/document/1200170471"` → **HTTP 422**;
угаданные URL на `files.stroyinf.ru` и `meganorm.ru` → 200, но «Страница не найдена» / 404 (URL были
угаданы, а не найдены поиском) → **Exa** (`web_search_exa`) нашла живые копии → PDF взят
`curl -sk --http1.1` с браузерным UA с **https://www.cposo.ru/images/2024/52872-2019.pdf** →
**HTTP 200, 435 367 байт**, разобран `pdftotext` → **215 870 символов** текста.
PDF представляет собой распечатку официального текста с сайта tiflocentre.ru (колонтитул
«https://tiflocentre.ru/documents/gost-r-52872-2019.php», дата печати 23.08.2024), 46 страниц.
Снято 24.09.2026.

## B.0 🔴 ПРОВЕРКА ДАТЫ ВВЕДЕНИЯ — в задании было «01.06.2020», это НЕВЕРНО

Дословно из текста стандарта:
> «**Дата введения — 2020—04—01**»
> — https://meganorm.ru/Data2/1/4293727/4293727086.pdf (официальное издание Стандартинформ 2019)

Дословно из приказа Росстандарта:
> «1. Утвердить национальный стандарт Российской Федерации ГОСТ Р 52872-2019 "Интернет-ресурсы и
> другая информация, представленная в электронно-цифровой форме. Приложения для стационарных и
> мобильных устройств, иные пользовательские интерфейсы. Требования доступности для людей с
> инвалидностью и других лиц с ограничениями жизнедеятельности", **с датой введения стандарта в
> действие с 1 апреля 2020 года, взамен ГОСТ Р 52872-2012**.»
> — Приказ Росстандарта от 29.08.2019 № 589-ст, https://pravo.ppt.ru/prikaz/rosstandart/n-589-st-222210

Гарант:
> «Дата введения — 1 апреля 2020 г. … Текст ГОСТа приводится по официальному изданию Стандартинформ,
> Москва, 2019 г. … Текст ГОСТа приводится с учётом **поправки, опубликованной в ИУС "Национальные
> стандарты", 2020 г., N 3**»
> — https://base.garant.ru/73664694/

Статус на 24.08.2026 по данным Тифлоцентра: **действующий**
> «Дата введения в действие: 01.04.2020 Статус на 24.08.2026: Действующий»
> — https://tiflocentre.ru/documents/gost-r-52872-2019.php

🔴 **Итог: 01.04.2020, а не 01.06.2020.** Действует с поправкой (ИУС 2020 № 3).

## B.1 Предисловие — статус документа и правила применения (дословно)

> «Предисловие
> 1. РАЗРАБОТАН Федеральным государственным унитарным предприятием «Российский научно-технический
> центр информации по стандартизации, метрологии и оценке соответствия» (ФГУП «СТАНДАРТИНФОРМ») и
> авторским коллективом независимых экспертов в составе: Ю.А.Божор, В.Н.Довыденков, А.В.Зеленов,
> А.Н.Камынин, А.Д.Попко, В.В.Рудницкая
> 2. ВНЕСЕН Техническим комитетом по стандартизации ТК 381 «Технические средства и услуги для
> инвалидов и других маломобильных групп населения»
> 3. УТВЕРЖДЕН И ВВЕДЕН В ДЕЙСТВИЕ Приказом Федерального агентства по техническому регулированию и
> метрологии от 29 августа 2019 г. N 589-ст
> 4. **ВЗАМЕН ГОСТ Р 52872-2012**
>
> **Правила применения настоящего стандарта установлены в статье 26 Федерального закона от 29 июня
> 2015 г. N 162-ФЗ "О стандартизации в Российской Федерации".** Информация об изменениях к настоящему
> стандарту публикуется в ежегодном (по состоянию на 1 января текущего года) информационном указателе
> "Национальные стандарты"…»

🔴 **Важно для угла 6:** в предисловии **НЕТ строки «МОД/IDT/NEQ»** (обычная для гармонизированных
ГОСТов пометка о степени соответствия зарубежному стандарту). Поиск по тексту (`grep` на «модифицированн»,
«степень соответствия», «МОД», «IDT», «NEQ») дал **ноль совпадений**. Связь с WCAG 2.1 заявлена не
в предисловии, а во **Введении**, и в форме «за основу был взят» (см. B.2).

## B.2 Введение — соотношение с WCAG 2.1 (дословно)

> «**При разработке настоящего стандарта за основу был взят актуальный на этот момент документ
> Web Content Accessibility Guidelines (WCAG) 2.1 [1], созданный и сопровождаемый международной
> организацией World Wide Web Consortium.** Этот документ содержит требования и рекомендации,
> учитывающие как актуальные тенденции в сфере вспомогательных технологий, так и многолетний опыт
> становления Интернета и его самого популярного сегмента — «мировой паутины» (WWW) — в качестве
> доступного информационного пространства.»

Чем ГОСТ шире WCAG — дословно:
> «В настоящем стандарте требования и рекомендации распространяются **не только на доступность
> веб-контента, но и на доступность любой информации, представленной в электронно-цифровой форме**,
> для взаимодействия с которой используются те же самые или схожие технологии. По этой причине для
> целей настоящего стандарта был выбран более общий термин, а именно «доступность цифрового контента»,
> причем, **в отличие от WCAG**, также обобщенным считается источник такого контента, которым может
> быть и веб-ресурс, и кабельная сеть, по которой транслируется видео, и приложение, пользовательский
> интерфейс которого реализован с применением HTML или похожего языка разметки.»

Структура (калька с WCAG: 4 принципа, 13 положений, критерии, 3 уровня) — дословно:
> «Требования настоящего стандарта изложены в форме принципов и положений, а критерии их выполнения
> представлены в виде проверяемых утверждений, не привязанных к определенной информационной технологии.
> **Принципы.** В основе доступности цифрового контента лежат четыре принципа: контент должен быть
> воспринимаемым, управляемым, понятным и надежным.
> **Положения.** Положения разработаны в соответствии с принципами. **13 положений** представляют собой
> основные цели… Выполнение этих положений невозможно проверить, однако они задают общие рамки…»

> «**Критерии выполнения.** Для каждого положения приведены проверяемые критерии его успешного
> применения, что позволяет использовать настоящий стандарт для проверки соответствия доступности
> цифрового контента определенному уровню. **Это может быть важно при разработке спецификаций и дизайна
> пользовательских интерфейсов, при составлении соглашений о закупках, при подготовке технических
> заданий, нормативных актов или коммерческих договоров.** Для удовлетворения потребностей различных
> групп пользователей в различных ситуациях стандарт определяет три уровня соответствия:
> **A (приемлемый), AA (высокий) и AAA (наивысший)**.»

🔴 Эта фраза — единственное место, где ГОСТ сам называет механизм своей обязательности:
через **закупки, техзадания, нормативные акты и коммерческие договоры**.

## B.3 Раздел 1 «Область применения» (дословно)

> «**1 Область применения.** Настоящий стандарт предназначен для использования лицами, ответственными
> за планирование, проектирование, разработку, приобретение и оценку различного рода устройств и
> систем, содержащих человеко-ориентированные пользовательские интерфейсы для представления
> электронно-цифровой информации (цифрового контента). Настоящий стандарт содержит требования и
> рекомендации, позволяющие представить цифровой контент таким образом, чтобы он был доступен для
> пользователей с ограничениями жизнедеятельности, включая людей с инвалидностью, временной потерей
> трудоспособности и пожилых людей. Настоящий стандарт охватывает вопросы, связанные с разработкой
> цифрового контента, взаимодействовать с которым указанным пользователям придется в различных
> условиях: на учебном или рабочем месте, дома, в общественном транспорте, на любых объектах
> социальной, инженерной транспортной инфраструктуры и т. д.
>
> На основании требований и рекомендаций настоящего стандарта может быть подготовлен подробный проект
> для разработки конкретного вида цифрового контента с поддержкой доступности. Если существует
> стандарт, регламентирующий требования доступности конкретного вида цифрового контента, то он может
> быть использован в сочетании с настоящим стандартом.
>
> **Примечание** — Настоящий стандарт является высокоуровневым стандартом, применимым ко всем видам
> цифрового контента, имеющего человеко-ориентированное представление, поэтому требования доступности,
> **специфические для конкретных видов цифрового контента, не рассматриваются**.»

Область охвата ограничений (Введение, дословно):
> «Требования стандарта учитывают широкий спектр расстройств функций организма и связанные с ними
> ограничения жизнедеятельности, в том числе: нарушение зрения, нарушение слуха, нарушение
> опорно-двигательного аппарата, нарушение речи, нарушение ментальной сферы, трудности в обучении и
> неврологические нарушения… Требования стандарта также учитывают возрастные изменения…»

> «Требования настоящего стандарта относятся **не только к ресурсам, размещенным в глобальной сети
> Интернет**, но и к электронно-цифровой информации, распространяемой в сетях передачи данных
> предприятий, организаций и сообществ, пользователями которых могут оказаться люди с инвалидностью
> или люди преклонного возраста.»

## B.4 Критерии ГОСТа, релевантные таблицам и графикам — ДОСЛОВНО

Нумерация критериев в ГОСТе **совпадает** с WCAG 2.1 (1.4.3 = 1.4.3 и т. д.), формулировки — перевод
с небольшими расхождениями (см. B.5).

### 4.1.1 Положение 1.1 Текстовая версия / Критерий 1.1.1 Нетекстовый контент (Уровень А)

> «**Необходимо предоставить текстовую версию любого нетекстового контента** так, чтобы ее можно было
> преобразовать в другие формы, необходимые пользователям, например увеличенный шрифт, шрифт Брайля,
> речь, специальные знаки или упрощенный язык.
>
> **Критерий успешного применения 1.1.1 Нетекстовый контент (Уровень А)**
> Весь нетекстовый контент, представленный пользователю, имеет эквивалентную текстовую версию, кроме
> описанных ниже случаев:
> — **элементы управления, ввод информации:** если нетекстовый контент является элементом управления
> или полем для ввода информации, то он имеет название, описывающее его назначение…;
> — **медиаконтент, ограниченный по времени:** … текстовая версия представляет собой, как минимум,
> краткое описание нетекстового контента…;
> — **тест:** если нетекстовый контент является тестом или упражнением, которые потеряют свою
> функциональность, если будут представлены в виде текста, то текстовая версия представляет собой,
> как минимум, краткое описание нетекстового контента;
> — **сенсорное восприятие:** если нетекстовый контент в первую очередь предназначен для получения
> специфического сенсорного опыта, то текстовая версия представляет собой, как минимум, краткое
> описание нетекстового контента;
> — **капча:** …;
> — **оформление, форматирование, невидимый контент:** если нетекстовый контент используется
> исключительно с целью оформления, визуального форматирования или вообще невидим пользователям, то
> он представлен таким образом, чтобы вспомогательные технологии могли его игнорировать.»

🔴 **Расхождение с WCAG, замеченное в тексте:** в перекрёстной ссылке ГОСТ пишет «**см. Критерий
успешного применения 1.1.2**», тогда как WCAG 2.1 в том же месте ссылается на **SC 4.1.2 Name, Role,
Value**. Критерия 1.1.2 в структуре стандарта нет — похоже на опечатку перевода/вёрстки в снятой копии.

### 4.1.3 Положение 1.3 Адаптируемость / Критерий 1.3.1 Информация и смысловые связи (Уровень А)

> «**Необходимо создавать контент, который можно представить различными способами без потери информации
> или структуры.**
> **Критерий успешного применения 1.3.1 Информация и смысловые связи (Уровень А)**
> Информация, структура и смысловые связи, представляемые пользователям, могут быть **программно
> определены** или доступны в текстовой версии.»

Критерий 1.3.3 (Уровень А):
> «Инструкции, предоставляемые для понимания и управления контентом, не опираются только на
> характеристики компонентов, воспринимаемые органами чувств пользователей, а именно на форму, цвет,
> размер, визуальное расположение, ориентацию и звук.
> Примечание — Относительно требований, касающихся использования цвета, см. положение 1.4.»

Критерий 1.3.4 Ориентация (Уровень АА):
> «Вид и функционал контента не ограничивается только одной ориентацией изображения на экране (книжной
> или альбомной), кроме тех случаев, когда определенная ориентация необходима для корректного
> отображения и использования контента. К случаям… относятся, например, следующие: **банковский чек**,
> приложение для фортепиано, слайды для показа на проекторе или телевизоре, содержимое виртуальной
> реальности…»

### 4.1.4 Положение 1.4 Различимость / Критерий 1.4.1 Использование цвета (Уровень А)

> «Необходимо максимально упростить пользователям возможность просматривать и прослушивать контент,
> в том числе отделяя первостепенную информацию от фоновой.
>
> **Критерий успешного применения 1.4.1 Использование цвета (Уровень А)**
> **Цвет не используется в качество [sic] единственного визуального средства передачи информации,
> обозначения действия, запроса на обратную связь или различения визуального элемента.**
> Примечание — Этот критерий относится только к восприятию цвета. Другие формы восприятия, включая
> программный доступ к цвету и другим типам кодирования визуального отображения, описываются в
> положении 1.3.»

(«в качество» — опечатка в снятом тексте, сохранена дословно.)

### Критерий 1.4.3 Контрастность (минимальные требования) (Уровень АА)

> «Визуальное отображение текстовой информации и текст на изображениях имеют **коэффициент
> контрастности не менее 4.5:1**, кроме следующих случаев:
> — **увеличенный текст:** укрупненная текстовая информация и графическое представление текста имеют
> коэффициент контрастности **не менее 3:1**;
> — **дополнительная информация:** требования по соблюдению определенной контрастности не применяются
> к тексту или графическому представлению текста, которые являются частью неактивных компонентов
> пользовательского интерфейса, или которые выполняют чисто декоративные функции, никому не видны или
> являются частью изображения, передающего более важную визуальную информацию;
> — **логотипы:** требования по соблюдению определенной контрастности не применяются к тексту,
> являющемуся частью логотипа или названия торговой марки.»

🔴 В отличие от WCAG, конкретные кегли (18 pt / 14 pt bold) в ТЕКСТЕ самого критерия ГОСТа
не приведены — они вынесены в определение термина «укрупненная текстовая информация» в разделе 3
(в снятой копии термин присутствует как отдельная статья раздела 3, полностью не выгружался).

### Критерий 1.4.4 Изменение размера текста (Уровень АА)

> «Размер шрифта текста, кроме титров и графического представления текста, может быть изменен без
> применения вспомогательных технологий **до 200 %** без потери контента или функциональности.»

### Критерий 1.4.10 Изменение формата (Уровень АА) — 🔴 ТАБЛИЦЫ В ИСКЛЮЧЕНИИ

> «Контент отображается без потери информации или функциональности и без необходимости прокрутки
> экрана в двух направлениях при соблюдении следующих условий:
> — данные расположены по вертикали с шириной, соответствующей **320 пикселям CSS**;
> — данные расположены по горизонтали с высотой, соответствующей **256 пикселям CSS**.
> **За исключением контента, требующего двухмерного макета страницы для пользования страницей или
> передачи смысла.**
>
> Примечания
> 1. 320 пикселей CSS соответствуют ширине первоначальной области просмотра в 1280 пикселей CSS при
> 400-процентном увеличении. Для контента, разработанного с горизонтальной прокруткой (например, для
> текста, ориентированного по вертикали), 256 пикселей CSS соответствуют ширине первоначальной области
> просмотра 1024 пикселя при 400-процентном увеличении.
> 2. Примерами контента, требующего двухмерного макета страницы, являются: **картинки, карты, диаграммы,
> видеоизображения, игры, презентации, таблицы данных и интерфейсы, предполагающие наличие панели
> инструментов для использования контента.**»

🔴 **Расхождение с WCAG:** в WCAG Note 2 стоит уточнение «data tables **(not individual cells)**» —
в русском тексте ГОСТа оговорки «(не отдельные ячейки)» **НЕТ**, сказано просто «таблицы данных».
Также в примечании 1 ГОСТа сказано «256 пикселей CSS соответствуют **ширине** первоначальной области
просмотра 1024 пикселя», тогда как в WCAG — «**height** of 1024 CSS pixels»: ошибка перевода
(«ширина» вместо «высота»).

### Критерий 1.4.11 Контрастность нетекстовой информации (Уровень АА) — 🔴 ГРАФИКИ

> «Визуальное отображение нижеперечисленных элементов имеет **коэффициент контрастности не менее 3:1**
> по сравнению с фоновым цветом/цветами:
> — **компоненты пользовательского интерфейса:** визуальная информация, необходимая для идентификации
> компонентов пользовательского интерфейса или динамических форм, кроме неактивных компонентов, или
> когда вид компонента определяется пользовательским приложением и не может быть изменен разработчиком
> контента;
> — **графические объекты: графические изображения, необходимые для понимания контента, кроме случаев,
> когда определенная форма графического изображения необходима для передачи информации.**»

### Критерий 1.4.12 Интервалы в тексте (Уровень АА)

> «В контенте, передаваемом с помощью языков разметки, которые соответствуют нижеизложенным стилевым
> характеристикам текста, не происходит потеря данных или функциональности при соблюдении всех
> нижеуказанных критериев и неизменности всех остальных стилевых характеристик:
> — межстрочный интервал — как минимум в полтора раза больше размера шрифта;
> — интервал между абзацами — как минимум в два раза больше размера шрифта;
> — интервал между буквами составляет как минимум 0.12 от размера шрифта;
> — интервал между словами составляет как минимум 0.16 от размера шрифта.»

### Для справки — АAA-уровни (в AA не входят)

Критерий 1.4.6 Контрастность (расширенные требования) (Уровень ААА):
> «Визуальное отображение текстовой информации и графическое представление текста имеют коэффициент
> контрастности **не менее 7:1**… увеличенный текст: … **не менее 4,5:1**…»

Критерий 1.4.8 Визуальное отображение (Уровень ААА) — то, что часто путают с «версией для слабовидящих»:
> «Для визуального отображения текстовых блоков должен быть доступен механизм для достижения
> нижеследующего:
> — **цвета основного и фонового содержимого могут быть выбраны пользователем**;
> — ширина строки — не более 80 символов или глифов (40 — в китайском, японском и корейском языках);
> — текст не выровнен по ширине строки (одновременно по правому и левому полям);
> — межстрочный интервал внутри абзаца — не менее 1.5 интервалов, а интервал между абзацами — по
> крайней мере в 1.5 раза больше, чем межстрочный интервал внутри абзаца;
> — размер шрифта текста может быть изменен без применения вспомогательных технологий до 200 % таким
> образом, что пользователю не придется применять горизонтальную прокрутку для чтения строки в
> полноэкранном режиме.»

## B.5 🔴 «Версия для слабовидящих» — что реально в редакции 2019

Поиск по полному тексту (215 870 символов) на «слабовидящ» дал **единственное** попадание — и оно
не является требованием, а описывает вспомогательные технологии:
> «Вспомогательные технологии, актуальные для настоящего стандарта, включают в себя, но не
> ограничиваются: программы увеличения экрана, которые, как правило, содержат и другие инструменты,
> помогающие лучше воспринимать визуальную информацию **слабовидящим пользователям (имеющим остаточное
> зрение)**, пользователям с нарушением восприятия…»
— раздел 3, примечание к термину «вспомогательные технологии» (3.1.13)

🔴 **Отдельного требования «спецверсия сайта для слабовидящих» в редакции 2019 в тексте НЕТ.** Вместо
него действует общий механизм WCAG-типа — «соответствующая альтернативная версия»:

> «**5. Правила оценки на соответствие.** Этот раздел содержит правила оценки контента на соответствие
> настоящему стандарту. Для того чтобы контент или его страница соответствовали настоящему стандарту,
> должны выполняться все нижеперечисленные требования.
> **5.1 Уровень соответствия.** Один из нижеуказанных уровней соответствия достигается полностью:
> — для соответствия уровню А (минимальный уровень соответствия) страница удовлетворяет всем критериям
> успешного применения уровня А **или предоставляется соответствующая альтернативная версия**;
> — для соответствия уровню АА страница удовлетворяет всем критериям успешного применения уровня А и
> уровня АА **или предоставляется соответствующая альтернативная версия уровня АА**;
> — для соответствия уровню ААА страница удовлетворяет всем критериям успешного применения уровня А,
> уровня АА и уровня ААА или предоставляется соответствующая альтернативная версия уровня ААА.
>
> Примечания
> 1. Хотя говорить о соответствии можно только по достижении вышеуказанных уровней, разработчиков
> призывают отражать любые успехи по соответствию критериям успешного применения всех уровней,
> превышающих достигнутый уровень соответствия.
> 2. **Не рекомендуется требовать соответствия уровню ААА в качестве общепринятой политики** в отношении
> всех источников цифрового контента целиком, так как для некоторых типов контента невозможно
> достижение всех критериев успешного применения уровня ААА.»

Термин «соответствующая альтернативная версия» определён в 3.1.72 (в снятой копии — строка 866,
полный текст определения выгружен частично; примечания к нему, дословно):
> «3. Если существуют версии на разных языках, соответствующая альтернативная версия должна быть…»
> «5. Соответствующая альтернативная версия **не обязана размещаться в некоторой области соответствия
> или на том** [же ресурсе — обрыв строки в снятой копии]»

## B.6 Что ГОСТ говорит про таблицы напрямую

Полнотекстовый поиск на «таблиц» по всем 215 870 символам дал **6 попаданий**, и ни одно из них
не является отдельным требованием к разметке таблиц (`th`, `scope`, `headers`) — в отличие от
WCAG-техник H43/H51, которых в ГОСТе нет вовсе (техники W3C в стандарт не переносились):

1. 3.1.10 «блок информации»:
   > «Примечание — Блок информации может состоять из одного и более параграфов и включать в себя
   > графику, **таблицы**, списки и встроенные блоки информации.»
2. 3.1.13 «вспомогательные технологии», примечание 1:
   > «…дополнительные механизмы навигации и ориентирования, а также трансформации контента (например,
   > для **более удобного пользования таблицами**).»
3. 3.1.58 «программно определенный контекст ссылки», примечание 1:
   > «Например, в HTML такого рода информация включает текст, который находится в том же абзаце, списке,
   > **ячейке таблицы**, что и ссылка, или в **заголовке или строке таблицы**, связанных с ячейкой,
   > содержащей ссылку.»
4–5. упоминания «таблицы стилей» (авторские / пользовательские) — к данным не относятся;
6. критерий 1.4.10, примечание 2 (см. выше): «…презентации, **таблицы данных** и интерфейсы…».

🔴 **Вывод сырья (не синтез, а констатация поиска):** требование к таблицам в ГОСТе реализуется
через общий критерий **1.3.1 «Информация и смысловые связи»** («структура и смысловые связи … могут
быть программно определены»), а не через отдельный пункт. Конкретные приёмы (`<th>`, `scope`,
`headers`/`id`) в ГОСТе не описаны — их источник только WCAG-техники H43/H51, которые сами по себе
информативны (см. A.11).

---

# C. Юридический статус ГОСТа: добровольность и случаи обязательности

## C.1 Федеральный закон от 29.06.2015 № 162-ФЗ «О стандартизации в Российской Федерации», статья 26 — ДОСЛОВНО

Источник: https://www.consultant.ru/document/cons_doc_LAW_181810/0b41c80a4b380c5845a29b37afa6f49390738b18/
Редакция: **от 04.08.2026** (как указано на странице КонсультантПлюс на 24.09.2026).
Канал: `r.jina.ai` → **HTTP 401** → **Exa `web_fetch_exa`** → текст получен. Снято 24.09.2026.

> «**Статья 26. Общие правила применения документов национальной системы стандартизации**
>
> 1. **Документы национальной системы стандартизации применяются на добровольной основе** одинаковым
> образом и в равной мере независимо от страны и (или) места происхождения продукции (товаров, работ,
> услуг), **если иное не установлено законодательством Российской Федерации**.
>
> 2. Условия применения международных стандартов, региональных стандартов, межгосударственных
> стандартов, региональных сводов правил, стандартов иностранных государств, сводов правил иностранных
> государств, в результате применения которых на добровольной основе обеспечивается соблюдение
> требований утвержденного технического регламента или которые содержат правила и методы исследований
> (испытаний) и измерений, в том числе правила отбора образцов, необходимые для применения и исполнения
> утвержденного технического регламента и осуществления оценки соответствия, устанавливаются в
> соответствии с Федеральным законом от 27 декабря 2002 года N 184-ФЗ "О техническом регулировании".
>
> 3. 🔴 **Применение национального стандарта является ОБЯЗАТЕЛЬНЫМ для изготовителя и (или)
> исполнителя в случае публичного заявления о соответствии продукции национальному стандарту**, в том
> числе в случае применения обозначения национального стандарта в маркировке, в эксплуатационной или
> иной документации, и (или) маркировки продукции знаком национальной системы стандартизации.»

🔴 **Ключевой факт для FINPILOT, как он сформулирован в законе:** ГОСТ Р 52872-2019 применяется
добровольно — **но в момент, когда продукт публично заявляет «соответствует ГОСТ Р 52872-2019»**
(на сайте, в документации, в маркетинге, в описании в реестре ПО), **соблюдение стандарта становится
обязательным по п. 3 ст. 26**.

Соседняя норма, названная в оглавлении закона (текст не выгружался):
> «Статья 27. Применение ссылок на национальные стандарты и информационно-технические справочники
> в нормативных правовых актах»
> — https://www.consultant.ru/document/cons_doc_LAW_181810/

## C.2 Второй механизм обязательности — по тексту самого ГОСТа

Введение ГОСТ Р 52872-2019 (дословно, повтор из B.2, здесь как юридическое основание):
> «…что позволяет использовать настоящий стандарт для проверки соответствия доступности цифрового
> контента определенному уровню. Это может быть важно **при разработке спецификаций и дизайна
> пользовательских интерфейсов, при составлении соглашений о закупках, при подготовке технических
> заданий, нормативных актов или коммерческих договоров**.»

То есть по самому тексту стандарта путей к обязательности три: **закупка/контракт**, **техническое
задание**, **нормативный правовой акт** со ссылкой на ГОСТ.

---

# D. Предшественник — ГОСТ Р 52872-2012, и что из него ИСЧЕЗЛО в редакции 2019

Наименование 2012 года: **«Интернет-ресурсы. Требования доступности для инвалидов по зрению»**
(утв. и введён в действие Приказом Росстандарта от 29.11.2012 № 1789-ст). Базировался на **WCAG 2.0**
(в 2019-м базой стал WCAG 2.1). Отменён с 01.04.2020 («ВЗАМЕН ГОСТ Р 52872-2012», см. B.1).

Источники (снято 24.09.2026, канал — Exa `web_search_exa`):
https://base.garant.ru/70719822/ · https://tiflocentre.ru/download/gost-r-52872-2012.pdf ·
https://internet-law.ru/documents/prod/gost-r_gosudarstvennyj-standart/49/gost_93379.html ·
https://slabovid.ru/uploads/gost-52872-2012.pdf

Дословно из редакции 2012:
> «**4.5** Для полноценного доступа инвалидов по зрению к интернет-ресурсам информация должна быть
> представлена в виде текста.»

> «**5.1.1 Текстовая версия.** Интернет-ресурс должен содержать текстовую версию всего нетекстового
> контента для отображения этого контента в альтернативных форматах, удобных для **инвалидов по зрению**
> (увеличенный шрифт, шрифт Брайля, возможность доступа с использованием синтезаторов речи)…»

> «**5.1.2 Объем контента.** Часто посещаемые страницы по своему объему должны быть **не более 2—3
> экранов текста. Число ссылок на странице должно быть не более 15** (уровень ААА).»

> «**5.1.3 Графические файлы.** Графический файл, несущий смысловую нагрузку, должен быть снабжен
> поясняющим текстом. Для этого при включении в веб-страницу ссылки на графический файл (язык HTML)
> необходимо указать данный поясняющий текст **в атрибуте ALT** (уровень А).»

> «**5.1.4 Флэш-изображения.** При размещении на странице графических изображений данного формата
> необходимо предусмотреть возможность перехода на страницу с аналогичной информацией, в которой данные
> объекты отсутствуют. Эта возможность должна быть реализована размещением на странице с флэш-объектами
> соответствующей текстовой гиперссылки (уровень А).»

> «**5.1.6.1 Информация и взаимосвязи.** Визуально отображенные информация, структура и взаимосвязи
> могут быть программно определены или доступны в текстовой версии (уровень А).»

🔴 **Ближайшее к «спецверсии для слабовидящих» в редакции 2012** — требование текстового дубля
страницы (цитата по internet-law.ru, фрагмент выдачи Exa, в исходнике с обрывами):
> «…если вышеуказанные [требования] не могут быть удовлетворены никаким другим путем, то пользователю
> должна быть предоставлена **[тексто]вая страница с эквивалентной информацией и функциональностью.
> Обновление этой текстовой страницы должно идти параллельно с обновлением главной**»

Механизм уровней соответствия в 2012 году (дословно) — по существу тот же, что в 2019:
> «Уровень А. Для достижения соответствия Уровню А (минимальный уровень доступности) веб-страница
> выполняет все критерии уровня А **или пользователям доступна соответствующая альтернативная версия
> этой веб-страницы**; Уровень АА… или пользователям доступна соответствующая на уровне АА
> альтернативная версия этой веб-страницы…»

### Что изменилось (констатация по текстам, без синтеза)

| Признак | ГОСТ Р 52872-**2012** | ГОСТ Р 52872-**2019** |
|---|---|---|
| Основа | WCAG **2.0** | WCAG **2.1** («за основу был взят», B.2) |
| Аудитория по названию | «для **инвалидов по зрению**» | «для людей с инвалидностью и **других лиц с ограничениями жизнедеятельности**» |
| Предмет | «Интернет-ресурсы» | интернет-ресурсы + **приложения** для стационарных и мобильных устройств, иные интерфейсы |
| Своя нумерация | да (4.5, 5.1.1, 5.1.2, 5.1.3…) | нет — **нумерация критериев совпадает с WCAG** (1.1.1, 1.4.3, 1.4.11…) |
| Собственные числовые нормы РФ | есть: «не более 2—3 экранов», «не более 15 ссылок», требование к флэш, требование `ALT` | **отсутствуют** — числа только из WCAG (4.5:1, 3:1, 200 %, 320/256 px) |
| Текстовая копия страницы | есть (5.1.1 + требование текстовой страницы-дубля) | **как отдельного требования НЕТ**; заменено общим механизмом «соответствующая альтернативная версия» (5.1) |

🔴 **Прямой ответ на вопрос задания «осталось ли это в редакции 2019»:** требование отдельной
спецверсии для слабовидящих в тексте 2019 года **не найдено** — полнотекстовый поиск по 215 870
символам дал одно попадание слова «слабовидящ», и то в описании вспомогательных технологий (B.5).

---

# НЕ ДОБЫТО

Дата проверки по всем строкам — **24.09.2026**.

| Источник | Что хотели | Каналы и коды | Классификация |
|---|---|---|---|
| `docs.cntd.ru/document/1200170471` (ГОСТ Р 52872-2019) | официальная копия текста | `r.jina.ai` → **HTTP 422** (единственный канал; `WebFetch`, `curl` с UA и браузер **не пробовались**) | 🟢 **исполнимо, не сделано** — каналы не пройдены. Не потребовалось: полный текст добыт с `cposo.ru` (PDF, 435 367 байт). |
| `protect.gost.ru` / `rst.gov.ru` (официальная витрина Росстандарта) | официальный текст и карточка стандарта | **не пробовались вовсе** — бюджет в 15 действий исчерпан на добыче полного текста и статьи 26 | 🟢 **исполнимо, не сделано** |
| `publication.pravo.gov.ru` | приказ Росстандарта № 589-ст в официальном опубликовании | **не пробовался** | 🟢 **исполнимо, не сделано.** Текст приказа добыт с `pravo.ppt.ru` (вторичный источник), реквизиты сверены с предисловием ГОСТа — совпадают. |
| `base.garant.ru/71108018/...` (162-ФЗ, ст. 26) | текст статьи по Гаранту | `r.jina.ai` → 200, но **691 байт** (JS-редирект, содержимого нет); Exa `web_fetch_exa` → вернул только тело JS-редиректа | 🟢 **исполнимо, не сделано.** Не потребовалось: статья 26 полностью добыта с КонсультантПлюс через Exa. |
| `files.stroyinf.ru/Data/730/73018.pdf`, `meganorm.ru/Data2/1/4293727/4293727621.htm` | текст ГОСТа | `r.jina.ai` → **200**, но «Страница не найдена» / «404» | 🟡 **URL были УГАДАНЫ, а не найдены поиском** — это ошибка вахты, а не недоступность сайта. Рабочий URL на `meganorm.ru` существует: `https://meganorm.ru/Data2/1/4293727/4293727086.pdf` (найден через Exa, не выгружался — текст уже был). |
| Определение термина «укрупненная текстовая информация» (разд. 3 ГОСТа) | точные кегли РФ-аналога 18pt/14pt bold | из 215 870 символов PDF выгружены только разделы предисловия, введения, 1, части 3 и 4.1, 5.1 — конкретная статья раздела 3 **не извлекалась** | 🟢 **исполнимо, не сделано** — PDF лежит на диске: `/private/tmp/claude-501/.../scratchpad/gost.txt`, добирается одной командой `grep`. Файл в scratchpad, сессионный. |
| Полное определение 3.1.72 «соответствующая альтернативная версия» | дословно целиком | извлечены только примечания 3 и 5 (обрывы строк при `pdftotext`) | 🟢 **исполнимо, не сделано** — там же, в `gost.txt`. |
| `Understanding` для 1.4.10 Reflow, 1.4.3, 1.4.4, 1.3.1 | развёрнутые пояснения W3C | **не запрашивались** — бюджет | 🟢 **исполнимо, не сделано.** Канал рабочий: `r.jina.ai` даёт 200 на все `w3.org/WAI/WCAG21/Understanding/*`. |
| Требования Минцифры, делающие ГОСТ обязательным (приказы, ПП РФ, требования к ГИС/реестру ПО) | нормы со ссылкой на ГОСТ Р 52872-2019 | **не искались** — бюджет исчерпан | 🟢 **исполнимо, не сделано.** Добыты только два механизма обязательности: п. 3 ст. 26 162-ФЗ (публичное заявление о соответствии) и самоописание ГОСТа (закупки/ТЗ/НПА/договоры). |

**Поломок сайтов (единственная законная причина «НЕДОСТУПЕН») — НЕ ЗАФИКСИРОВАНО НИ ОДНОЙ.**
**Пунктов, требующих действия владельца (логин/оплата/капча), — НЕТ.** Капчи за сессию не встретилось,
браузер не открывался, вкладок не оставлено.

## Замеченные расхождения (для протокола, не выводы)

1. **Дата введения ГОСТа: в задании стояло 01.06.2020 — верно 01.04.2020** (три независимых источника, B.0).
2. **В WCAG 1.4.10 Note 2 есть «data tables (not individual cells)», в русском ГОСТе — просто «таблицы данных»**, оговорка про отдельные ячейки утрачена (B.4).
3. **Ошибка перевода в примечании 1 к критерию 1.4.10 ГОСТа:** «256 пикселей CSS соответствуют **ширине** первоначальной области просмотра 1024 пикселя» — в оригинале WCAG «**height** of 1024 CSS pixels».
4. **Перекрёстная ссылка в критерии 1.1.1 ГОСТа:** «см. Критерий успешного применения **1.1.2**» — в WCAG в этом месте **4.1.2 Name, Role, Value**; критерия 1.1.2 в стандарте не существует.
5. **Опечатка в критерии 1.4.1 ГОСТа:** «Цвет не используется **в качество** единственного визуального средства» (сохранена дословно).
