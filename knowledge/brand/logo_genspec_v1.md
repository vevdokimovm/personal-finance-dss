# FINPILOT — Logo Generation Spec (v1)

> Канонический промпт для стабильной генерации лого в Gemini.
> Эталон: `лого_высокое_качество.png` (первый из пяти рендеров).
> Принцип: reference задаёт композицию → промпт добивает детали числами → негатив-лист ловит дефолты модели.

---

## Как использовать (порядок обязателен)

1. **Прикрепи эталон** `лого_высокое_качество.png` прямо к запросу в Gemini.
2. **Поставь переключающую фразу** перед основным промптом — она переводит модель из режима «рисую с нуля» в режим «работаю от картинки»:

   > Using the attached image as the exact style and composition reference, recreate this emblem keeping its layout, the 8-spoke helm, bars, arrows and coins identical. Reproduce it on a pure black background. Then apply:

3. **Вставь основной промпт** (ниже) сразу за этой фразой, одним куском.
4. **Итерация при сбое:** картинку НЕ отцепляешь. Меняешь только одну строку под конкретный косяк → генеришь заново. Спека растёт против наблюдаемых факапов, не переписывается целиком.

---

## Основной промпт (copy-paste, EN)

```
A single neon line-art emblem, dead-centered, perfectly symmetrical, on a pure solid black background (#000000).

SUBJECT — a ship's steering wheel (helm) as the central container:
- Double concentric circular rim (two parallel outlines forming the wheel ring).
- Exactly 8 cylindrical spokes radiating outward at even 45° intervals, each spoke ending in a rounded knob tip.

INSIDE the wheel ring:
- A bar chart of 4 vertical bars ascending in height from left to right, drawn as hollow outlines only.
- Two upward arrows pointing to the top-right on a diagonal — one longer, one shorter — each with a clear triangular arrowhead, crossing over the wheel.

AROUND the lower-right of the wheel:
- Two short stacks of coins (cylindrical discs) plus one or two single coin rings, hollow outline only.
- One small circle on a short stem near the upper-right spoke.

STYLE:
- Pure neon line-art. Every shape is a hollow stroke — NO solid fills, NO shading, NO color filling any shape.
- Thin double-stroke lines mimicking neon glass tubing, with a soft outer glow / bloom around every line.
- The STROKE color itself transitions smoothly from neon green (#39FF14) at the bottom-left to yellow-lime chartreuse (#CCFF00) at the top-right. Green dominant. Shapes stay hollow.

FRAMING (subtle, thin, low-opacity green):
- Four crosshair tick marks at the top, bottom, left and right edges (N/S/E/W).
- One or two faint thin concentric circles enclosing the emblem.

COMPOSITION: emblem fills ~80% of a square frame, generous black margin, dead-centered.

DO NOT include: any background other than pure black; any solid fill inside any shape; drop shadows or 3D shading; realistic textures or photorealism; any text, letters, numbers or watermark; more or fewer than 8 spokes; any colors outside the green-to-yellow range; blur or out-of-focus areas; a rounded-square app-icon frame; more than one emblem or any duplicates.
```

---

## Залоченные параметры (источник стабильности)

| Параметр | Значение | Зачем зафиксировано |
|---|---|---|
| Фон | чистый чёрный `#000000` | главное требование, без вариаций |
| Рукояти штурвала | ровно 8, через 45° | самая частая зона разброса у модели |
| Обод | двойной концентрический | держит «неоновую трубку» |
| Столбцы графика | 4, по возрастанию слева направо | убирает «сколько баров?» |
| Стрелки | 2 вверх-вправо, длинная + короткая | фиксирует траекторию роста |
| Монеты | 2 стопки + 1–2 кольца, низ-право | без них уезжает композиция |
| Стиль | line-art, только контур, без заливки | ловит дефолт «залить цветом» |
| Градиент штриха | green `#39FF14` → chartreuse `#CCFF00` | зелёный доминирует |
| Каркас | кресты N/S/E/W + бледные круги | эффект прибора/приборки |
| Кадр | эмблема ~80%, центр, квадрат | стабильные поля |

---

## Слабые зоны (следить, лочить в следующих версиях)

- **Кружок на ножке справа сверху** — на эталоне сам по себе мутный (лупа или монета?). Первый кандидат поплыть. Решение по смыслу → жёсткая строка в промпт.
- **Перекрытие стрелок и правых рукоятей** — справа всё плотно, модель может «слипать» элементы.
- **Хвосты монет** — число колец/стопок может гулять; при необходимости задать точно.

---

## Про повторяемость (seed)

- **AI Studio / API:** если доступно поле `seed` — залочь его. Тогда «тот же промпт + тот же seed» даёт почти идентичную картинку.
- **Приложение Gemini:** `seed` обычно недоступен → вся стабильность держится на reference-картинке из шага 1. Без неё каждый запуск — лотерея заново.

---

## Журнал итераций

| Версия | Что менялось | Под какой сбой |
|---|---|---|
| v1 | базовая спека | — |
| | | |
