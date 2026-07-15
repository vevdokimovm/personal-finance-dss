# FINPILOT — Паспорт логотипа (Logo Guideline) v3.0

> Эталонный документ бренда. Фиксирует концепцию, точную анатомию, палитру, рабочие промпты и всё, что выстрадано в ходе подбора генерации.
> **v3.0 — главное обновление:** добавлены РАБОЧИЕ промпты для Gemini (проверены десятками прогонов), точная анатомия внутренней зоны штурвала, схема трёх монетных элементов, решение проблемы серого фона в Telegram. Это рабочая версия, по которой реально получается эталон.

---

## 0. TL;DR — если читать только одно

- Лого = **неоновый штурвал + дашборд (3 столбика) + 2 стрелки роста + 3 монетных элемента**, зелёно-лаймовый градиент, чёрный фон, свечение как у вывески.
- Генерится в **Gemini (gemini.google.com)**, не во мне. Я (Claude) картинки-неон не рисую — я пишу промпты, чищу фон, режу PNG, веду паспорт.
- **Рабочий промпт — в разделе 7.** Это итог长 подбора, бери его.
- **Главный рычаг точности — style reference** (прикрепить эталон-картинку к промпту), а не текст. Текст один даёт дрейф.
- Единственный эталон — файл проекта **`лого_высокое_качество.png`**. С него гонишь reference.

---

## 1. Концепция и смысл

Логотип строится вокруг одной идеи: **пользователь у руля своих финансов, а FINPILOT — его штурман**.

**FIN** (финансы) + **PILOT** (штурман, тот, кто ведёт). Продукт — алгоритмическая СППР: не управляет за тебя, а помогает держать курс. Центральный образ — **корабельный штурвал** (управление, навигация). Внутри — **растущий график и стрелки** (рост, прогресс). Вокруг — **монеты** (капитал, ликвидность) и **сетка-прицел** (точность, математика «под капотом»).

Сообщение бренда: *«Точный расчёт ведёт твои деньги вверх. Ты — у руля».*

---

## 2. Визуальная анатомия (выверено по эталону)

### 2.1. Штурвал (рамка)
- Стилизованный неоновый line-art штурвал, **НЕ реалистичный деревянный**.
- Чистый обод (одно кольцо, опц. тонкое второе внутри).
- **8 рукояток-капсул** (вытянутые скруглённые набалдашники) по ВНЕШНЕЙ стороне обода.
- **КРИТИЧНО: спицы НЕ заходят в центр.** Внутренняя зона свободна от спиц. Спицы видны только по ободу, не поверх графика. Это главная ошибка генераций — модель плодит спицы в центре и получается каша.

### 2.2. Внутри штурвала (только эти элементы, больше ничего)
- **3 столбика дашборда** — возрастают РАВНОМЕРНО слева направо, ровные, чистые.
- **2 стрелки роста** — выходят из зоны графика на северо-восток. Главная (длинная) — между спицами в зоне ~11–1 час; вторая (короче) — правее, между следующими спицами.
- **Горсть монет** — небольшая стопка на ~4.5 часа, у нижне-правого края ВНУТРИ обода.
- **NOTHING ELSE.** Центр не загромождён.

### 2.3. Три монетных элемента (это якорь, выверено)
1. **Северо-восток (~1.5 часа):** одиночная **монета на КОНЦЕ спицы**, вместо набалдашника. Это монета (с ребром/толщиной), НЕ лупа, НЕ просто круг.
2. **Юго-восток (~4.5 часа):** **стопка/горсть монет ВМЕСТО спицы** (спицы там нет, монеты заняли её место). Главная куча монет.
3. **Юго-запад (~7.5 часов):** спица ЕСТЬ (обычная), а рядом с ней лежит **ОДНА отдельная монета** (лежачий диск).

### 2.4. Периферия (hero-версия)
- Внешние концентрические круги + перекрестие (crosshair) по 4 сторонам — сетка-прицел.
- В иконках/фавиконе периферию убирать.

---

## 3. Стиль рисовки штурвала

Не фотореалистичный руль — **упрощённый чистый line-art силуэт**: чистый обод, рукоятки-капсулы со скруглёнными краями, геометрическая чистота, только контур (без заливок, без дерева, без текстур). Метафора: «технический чертёж штурвала под неоном».

---

## 4. Цветовая система

| Роль | Название | HEX | Применение |
|---|---|---|---|
| Фон | **Pure Black** | `#000000` | Подложка (см. примечание про фон ниже) |
| База | **Neon Green** | `#2BFF88` | Основной неон, низ-лево градиента |
| Акцент | **Neon Lime** | `#D4FF3D` | Жёлто-лаймовый акцент, верх-право градиента |
| Текст | **White** | `#FFFFFF` | Леттеринг отдельно от эмблемы |

**Градиент линий:** по диагонали — зелёный (#2BFF88) низ-лево → лайм (#D4FF3D) верх-право.
**Свечение:** мягкий неоновый glow того же цвета, эффект вывески.

### Примечание про фон (ВАЖНО — решение проблемы Telegram)
Раньше на фоне `#0E1F1C` (тёмный слейт) свечение подсвечивало углы, и в Telegram аватарка выглядела с **серой рамкой**. Решение:
- Генерить на **чистом чёрном `#000000`** с большим запасом (padding), чтобы glow не доходил до углов.
- При финальной обработке **углы добиваются в абсолютный `#000000`** (это делает Claude кодом перед нарезкой).
- Так серой рамки в ТГ не возникает.

---

## 5. Версии логотипа

| Версия | Состав | Где |
|---|---|---|
| **Hero** | Полная: штурвал + дашборд + 2 стрелки + 3 монеты + сетка-прицел + свечение | Обложки, обои, презентации (≥512px) |
| **Icon** | Ядро + монеты на спицах, без внешней сетки | Аватарка, app icon, соцсети (128–512px) |
| **Favicon** | Только ядро (штурвал + 3 столбика + стрелки) | Сайт, ≤32px. На мелком детали сливаются — нужна отдельная упрощённая версия |

---

## 6. Где и как генерить

- Движок: **Gemini (gemini.google.com)**. Поддерживает прикрепление картинки-референса.
- **Claude НЕ генерит неон-картинки.** Claude умеет: SVG-вектор (чистая геометрия, не «вывеска»), чистку фона, нарезку PNG, ведение паспорта.
- **Разрешение в Gemini не задаётся точно** — он режет в ~1024px и слушается скорее aspect ratio + «intended use», чем числа пикселей. Поэтому: генеришь ОДНУ сочную мастер-картинку, а нарезку под носители делает Claude из неё.
- Для нарезки/чистки фона/удаления вотермарка Gemini — отдавай картинку Claude.

---

## 7. РАБОЧИЙ ПРОМПТ (Hero, финальная версия)

> Это итог長ого подбора (промпты #1→#2→#3→финал). Главные правки, которые довели до эталона: гашение реализма штурвала, 3 монетных элемента прямым текстом, чистый центр без спиц, чёрный фон с padding.
>
> **Как использовать для максимальной точности:** прикрепи эталон `лого_высокое_качество.png` как style reference + вставь этот текст. Без референса текст один тоже работает, но с бóльшим дрейфом. Гони пачкой 6–12 штук, выбирай лучшую.

```
A premium neon line-art emblem for a fintech product called FINPILOT.
A ship's steering wheel (helm) framing a clean financial dashboard inside.
Faint outer measurement circles and a subtle crosshair reticle frame the emblem.

INSIDE THE WHEEL (important — keep this area CLEAN, only these elements):
- A rising bar chart of exactly 3 bars, increasing evenly in height from left
  to right. Clean, evenly spaced, simple.
- TWO upward arrows rising from the chart toward the upper-right: the main
  (longer) arrow passes out between the spokes around the 11-to-1 o'clock gap;
  the second (shorter) arrow is to its right, between the next spokes.
- A small stack of coins at about the 4.5 o'clock position, just inside the
  lower-right rim.
- NOTHING ELSE inside. The central area is uncluttered.

HELM WHEEL (the frame):
- Stylized neon line-art ship's wheel, NOT a realistic wooden one
- A clean rim (one ring, optionally a thin second inner ring)
- 8 spoke-handles as smooth rounded capsule knobs around the OUTSIDE of the rim
- IMPORTANT: the spokes do NOT cross into the center — the inner dashboard area
  stays clear of spokes. Spokes are only visible around the rim, not over the
  chart.

COIN ELEMENTS (three, follow exactly):
- NORTH-EAST (~1.5 o'clock): a single round COIN at the END of that spoke-
  handle, replacing its knob (a coin, NOT a magnifier).
- SOUTH-EAST (~4.5 o'clock): the coin stack described above (inside the rim).
- SOUTH-WEST (~7.5 o'clock): the spoke-handle is present, and ONE single coin
  lies flat next to it.

STYLE:
- Neon glow line-art, glowing tube-light strokes, like a neon sign
- Color gradient from neon green (#2BFF88) bottom-left to lime-yellow (#D4FF3D)
  top-right
- Soft outer glow around all lines
- Background: pure black (#000000), solid and even, generous black padding so
  the glow does not reach the corners
- High detail, sharp, cinematic, premium

COMPOSITION:
- Emblem centered, square 1:1 format, high resolution

STRICT EXCLUSIONS (do NOT include):
- No spokes crossing over the central dashboard area
- No extra bars, no extra arrows, no clutter inside the wheel
- No realistic wooden wheel, no wood texture, no carved baluster handles
- No text or letters, no human figures, no realistic photo elements
- Keep the neon line-art aesthetic only
```

### Если штурвал упорно лезет спицами в центр
Усиль строкой: `only the rim and outer handles of the wheel are shown, the wheel's inner spokes are hidden behind the dashboard`.

---

## 8. История подбора промптов (что мы выяснили — чтобы не повторять ошибки)

### 8.1. Полный текст промпта #1 (базовый)

```
A premium neon line-art emblem for a fintech product called FINPILOT.
Central image: a ship's steering wheel (helm) fused with a rising bar chart and bold upward arrows growing through it. Small stacks of coins to the lower right. Faint outer measurement circles and a subtle crosshair reticle framing the emblem.
STYLE:
- Neon glow line-art, glowing tube-light strokes, like a neon sign
- Color gradient from neon green (#2BFF88) at bottom-left to lime-yellow (#D4FF3D) at top-right
- Soft outer glow around all lines
- Background: very dark deep-slate teal (#0E1F1C), almost black but not pure black
- High detail, sharp, cinematic
COMPOSITION:
- Emblem centered, symmetrical helm wheel with 8 handles
- Square 1:1 format, high resolution
STRICT EXCLUSIONS (do NOT include):
- No text or letters
- No human figures
- No realistic photo elements
- Keep the neon line-art aesthetic only
```

### 8.2. Полный текст промпта #2 (+ HELM STYLE + COIN DETAILS)

```
A premium neon line-art emblem for a fintech product called FINPILOT.
Central image: a ship's steering wheel (helm) fused with a rising bar chart
of three clean bars and two bold upward arrows growing through it toward the
upper-right. Small stacks of coins to the lower right. Faint outer measurement
circles and a subtle crosshair reticle framing the emblem.
HELM WHEEL STYLE (important):
- Simplified, stylized line-art wheel, NOT a realistic wooden ship's wheel
- Double concentric rim (two clean parallel circles)
- Spoke-handles are smooth elongated rounded capsules (pill-shaped knobs),
  NOT carved wooden balusters, no wood grain, no realistic turned details
- Flat clean center hub, no heavy machinery in the middle
COIN DETAILS (important):
- On the upper-right spoke (~1.5 o'clock position): a small round COIN sits
  at the end of the handle instead of a knob
- At the lower-right spoke (~4.5 o'clock position): a small lying stack of
  coins replaces that handle
STYLE:
- Neon glow line-art, glowing tube-light strokes, like a neon sign
- Color gradient from neon green (#2BFF88) at bottom-left to lime-yellow
  (#D4FF3D) at top-right
- Soft outer glow around all lines
- Background: very dark deep-slate teal (#0E1F1C), almost black but not pure black
- High detail, sharp, cinematic, premium
COMPOSITION:
- Emblem centered, helm wheel with handles around the rim
- The three bars stay clean and readable in the center, not tangled
- Square 1:1 format, high resolution
STRICT EXCLUSIONS (do NOT include):
- No realistic wooden wheel, no wood texture, no carved baluster handles
- No text or letters
- No human figures
- No realistic photo elements
- Keep the neon line-art aesthetic only
```

> Промпт #3 и финальный — это эволюция #2 (см. раздел 7 для финального текста). #3 = #2 + три монеты прямым текстом + 8 спиц + чёрный фон. Финал = #3 + блок INSIDE THE WHEEL (чистый центр, спицы не в центр).

### 8.3. Сводка эволюции

| Промпт | Что давал | Вывод |
|---|---|---|
| **#1** (базовый, «8 handles») | Стабильный, сочный, но **центр переусложнён** (каша), монет на спицах нет, штурвал реалистично-деревянный | Хорошая база по вайбу, но без монет и с кашей |
| **#2** (+ HELM STYLE + COIN DETAILS) | Появились монеты на спицах ✅, центр чище. Но блок про обод спровоцировал **ЕЩЁ больше спиц/колец** | Монеты заработали, но штурвал переусложнился |
| **#3** (+ 3 монеты явно, 8 спиц, чёрный фон) | **Все 3 монеты на местах** ✅, фон чёрный без серой рамки ✅, заметно стабильнее | Почти эталон |
| **Финал** (+ INSIDE THE WHEEL, спицы не в центр) | Чистый центр, только 3 столбика + 2 стрелки + монетка | Текущая рабочая версия (раздел 7) |

**Ключевые уроки:**
1. Слова `minimalist / app icon / simple / readable at small sizes` → Gemini делает плоскую слабую иконку. **Убирать их.** Для богатой картинки: `premium, high detail, cinematic, neon sign, glowing tube light`.
2. Чем больше описываешь обод штурвала — тем больше лишних спиц/колец модель насыпает. Держать обод коротко, а центр защищать явным «spokes do NOT cross into center».
3. Монеты на конкретных позициях (часах) — самое капризное. Из пачки выбирать где легло правильно. Референс-картинка надёжнее текста.
4. Фон чёрный + padding = нет серой рамки в ТГ.
5. Разрешение Gemini не слушает — нарезку делает Claude.

---

## 9. Финальная обработка (делает Claude)

После выбора лучшей генерации Claude:
1. **Чистит фон** — все тёмные пиксели (<18 по всем каналам) → абсолютный `#000000`, свечение не трогает.
2. **Убирает вотермарк Gemini** (ромбик в правом нижнем углу) — закрашивает зону ~115px.
3. **Режет PNG** под носители: 1024 / 512 / 256 / 128 / 64 / 32 / 16.
4. Мастер хранится в 2048×2048.

---

## 10. Эталонный ассет

| Файл | Назначение |
|---|---|
| `лого_высокое_качество.png` | **Единственный эталон бренда.** Источник style reference для всех генераций. Неоновый штурвал на чёрном фоне, все 3 монетных элемента на местах. |

> Это эталон, по которому сверяется любая новая генерация. PNG под носители (1024, 512, 256, 128 и т.д.) нарезаются из выбранной генерации по запросу — отдельными постоянными ассетами пока не зафиксированы.

---

## 11. Do / Don't

**Do:**
- Держать ядро неизменным: штурвал + 3 столбика (равномерно растущие) + 2 стрелки на СВ + 3 монеты
- Помнить 3 монеты: СВ на спице, ЮВ вместо спицы, ЮЗ рядом со спицей
- Центр держать ЧИСТЫМ, спицы не пускать внутрь
- Генерить на чёрном с padding, фон добивать в #000000
- Подавать эталон `лого_высокое_качество.png` как style reference
- Нарезку и чистку отдавать Claude

**Don't:**
- Не писать `minimalist/simple/app icon` в промпте hero — убивает картинку
- Не пускать спицы в центр (каша)
- Не путать монету на спице с лупой/кругом
- Не делать 1 стрелку (их 2; 1 — только фавикон)
- Не использовать слейт-фон для аватарок (серая рамка в ТГ)
- Не менять штурвал на другой символ — это якорь
- Не ждать от Gemini точного разрешения

---

## 12. Что осталось доделать (открытые задачи)

1. **Довести внутрянку до идеала** — последний прогон финального промпта (раздел 7) с защитой центра от спиц. Выбрать лучшую генерацию.
2. **Упрощённая фавиконка** (16–32px) — отдельная версия, где детали не сливаются: только штурвал + 3 столбика + 1 стрелка, жирные линии.
3. **Векторный SVG иконки** — для бесконечного масштабирования и мелких размеров без генерации (опционально, делает Claude).
