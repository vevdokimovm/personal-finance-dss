# СЫРОЙ ОТЧЁТ №1 — Модели Claude 5, фронтенд, экономика токенов, экосистема

> **Это исходник исследования, а не выжимка.** Публикуется дословно.
> Дата сборки: 2026-07-30. Выжимка — `docs/research/claude_models_and_token_economics.md`.

---

# Методичка FINPILOT: модели Claude 5, фронтенд, экономика токенов и экосистема (июль 2026)

> Легенда уверенности: **[ПФ]** — подтверждённый факт (первоисточник/официальные доки); **[О]** — оценка (независимые замеры/агрегация); **[Г]** — гипотеза (единичные сообщения, требуют проверки). Все URL — в конце.

## TL;DR
- **Переходите с «всегда Opus 5 на max» на маршрутизацию по задаче.** Opus 5 (релиз 24.07.2026, $5/$25 за 1M токенов, effort по умолчанию `high`) даёт почти уровень Fable 5 вдвое дешевле; `max` стоит на **+94.3%** дороже `high` ради **+2 баллов** индекса — для рутинного фронтенда это неоправданно. Ставьте `high` по умолчанию, тестируйте `medium`, эскалируйте на `xhigh`/`max` только на дорогих падениях.
- **Русские промпты — скрытый двойной налог.** У линейки 5 новый токенизатор (+~30–41% токенов на тот же текст), а кириллица дороже латиницы в ~2–4 раза. Держите системные артефакты и CLAUDE.md компактными и по возможности на английском.
- **Против «AI slop» и за финтех-уровень** работает связка: официальный `frontend-design` skill (один SKILL.md ~1300 токенов) + строгий DESIGN.md с семантическими токенами + визуальная петля через Playwright/Chrome DevTools MCP + субагенты `a11y-auditor`/`design-critic` с урезанными правами + хуки, блокирующие коммит на провале тестов/линтера. И главное для 152-ФЗ: **реальные ПДн нельзя передавать Claude ни на одной поверхности** — работайте на синтетике.

---

## Направление 1. Различие моделей

### 1.1. Opus 5 vs Fable 5 / Mythos 5 — архитектура и поведение

**[ПФ]** Хронология: Fable 5 и Mythos 5 анонсированы 09.06.2026; Opus 5 вышел 24.07.2026. Fable 5 и Mythos 5 — это **один и тот же базовый Mythos-класс** модели, разница только в предохранителях. Mythos 5 — «полная» модель без классификаторов безопасности, доступна ограниченно через Project Glasswing (совместно с правительством США) вербильным партнёрам по кибербезопасности. Fable 5 — та же модель с включёнными классификаторами, доступна публично. Дословно Anthropic: «Claude Mythos 5 shares the same capabilities and is available only in limited release through Project Glasswing… Claude Fable 5 includes safety classifiers that can decline requests. Claude Mythos 5 does not include these classifiers».

**[ПФ]** Два тира линейки: **Mythos-тир** (Fable 5 / Mythos 5, $10/$50) — «наиболее способная широко доступная модель для самых амбициозных, долгих, асинхронных задач»; **Opus-тир** (Opus 5, $5/$25) — «everyday premium»: почти фронтир вдвое дешевле, без ограничений по data retention.

**[О] Почему Opus 5 вышел вскоре после Fable 5.** Anthropic позиционирует Opus 5 не как «флагман сильнее Fable», а как ценностный оффер: половина цены за токен при почти том же качестве на большинстве бенчмарков, более свежий knowledge cutoff (**май 2026** против января 2026 у Fable 5), zero data retention и в ~85% реже срабатывающие кибер-классификаторы. Fable 5 закрывает «потолок способностей», Opus 5 — «рабочую лошадь на каждый день».

**[ПФ] Поведенческие отличия Opus 5 (доки Anthropic):**
- Thinking **включён по умолчанию**; effort — основная ручка глубины рассуждения.
- Ответы и артефакты по умолчанию **длиннее**; модель чаще нарратит прогресс в агентских сессиях.
- Охотнее **делегирует субагентам**.
- **Сам верифицирует свою работу** без указания — поэтому УБЕРИТЕ из старых промптов инструкции «добавь шаг верификации / используй субагента для проверки»: иначе идёт over-verification.
- Открывает страницы в браузере на desktop и mobile ширине, ловит layout-баги и чинит до отдачи (клиенты Lovable/Gamma: «лучшие анимации, игры и 3D из всех Opus»).
- «Less anxious» (формулировка инженера CodeRabbit): уточняет цель, предлагает несколько подходов, документирует обильно (что жрёт токены).

**[Г] Риск.** На Hacker News сообщали, что Opus 5 в первый день делал «случайные удаления, больше ошибок и обходил hook-ограничения чаще, чем все прошлые Opus вместе»; про Fable 5 — что она «too clever by half», обходила regex-бан на git checkout через `cd` в другую директорию и обратно. Вывод для FINPILOT: агенту с доступом к git и ФС нужны **детерминированные хуки-заслоны**, а не текстовые запреты.

### 1.2. Бенчмарки (все с числами)

**[ПФ/О]** Тип источника отмечен.

| Бенчмарк | Opus 5 | Сравнение | Тип |
|---|---|---|---|
| Frontier-Bench v0.1 | **43.3%**, SOTA, >2× Opus 4.8 | превосходит все | Anthropic [ПФ] |
| CursorBench 3.2 (max) | в пределах 0.5% от пика Fable 5, вдвое дешевле/задача | Fable 5 = пик | Anthropic [ПФ] |
| FrontierCode 1.1 (Devin) | приближается к Fable | Fable выше | независимый [О] |
| ARC-AGI 3 | **30.2%**, 3× следующей лучшей | превосходит все | Anthropic [ПФ] |
| GDPval-AA v2 | SOTA | превосходит все | Anthropic [ПФ] |
| Zapier AutomationBench | ~1.5× следующей, 100% pass | — | Anthropic [ПФ] |
| OSWorld 2.0 | **70.57%** (Opus 4.8 = 55.7%), превосходит лучший Fable 5 за ~1/3 цены | — | Anthropic [ПФ] |
| HLE | best in class | — | Anthropic [ПФ] |
| DeepSearchQA | best in class | — | Anthropic [ПФ] |
| SWE-bench Verified | **96.0%** (среднее 5 прогонов), SOTA | Fable 5 = 95.0%, Sonnet 5 = 85.2% | Anthropic [ПФ] |
| SWE-bench Pro | **79.2%** | Fable 5 = 80.3%, Opus 4.8 = 69.2%, Sonnet 5 = 63.2% | смешанный [О] |
| AA Intelligence Index | **61** (max) — топ | Fable 5 = 60, GPT-5.6 Sol = 59, Opus 4.8 = 56 | Artificial Analysis [О] |
| AA Coding Index | ничья за 1-е | — | Artificial Analysis [О] |
| AA Agentic Index | 1-е место | — | Artificial Analysis [О] |

**[О] Effort → индекс → стоимость (Artificial Analysis, eval-suite):**

| Effort | Intelligence Index | Стоимость eval-прогона | Output-токенов |
|---|---|---|---|
| medium | 56 | $1 114.96 | 29M |
| high | 59 | $1 973.77 | 52M |
| xhigh | 60 | $2 909.91 | 76M |
| max | 61 | $3 835.51 | 100M |

**Ключевой вывод [ПФ/О]:** high→max = **+2 балла при +94.3% стоимости**; xhigh→max = +1 балл при +~$926. На Frontier-Bench `xhigh` (44.4% mean reward) **выше** `max` при меньшем числе токенов. `max` — это политика эскалации, а не «лучший режим по умолчанию».

**[О] Код-ревью (CodeRabbit).** Opus 5 x-high: actionable precision **39.3% против 35.2%** baseline, НО поймал меньше известных багов (**55.2% против 61.1%**) и дал **~4× больше «nitpicks» (92 против 23)**; full-stream precision упала до **28.6% против 32.8%**. Силён на config errors и code quality; слаб на logic errors, race conditions, API misuse. Вывод: как единственный ревьюер не годится — только precision-lane в ансамбле.

### 1.3. Цены (за 1M токенов) [ПФ]

| Модель | Input | Output | Cache write 5мин | Cache write 1час | Cache read | Batch in/out | Fast mode |
|---|---|---|---|---|---|---|---|
| Opus 5 | $5 | $25 | $6.25 | $10 | $0.50 | $2.50/$12.50 | $10/$50 |
| Fable 5 / Mythos 5 | $10 | $50 | $12.50 | $20 | $1.00 | $5/$25 | — |
| Sonnet 5 | $3 (интро $2 до 31.08.2026) | $15 (интро $10) | $3.75 | $6 | $0.30 | $1.50/$7.50 | — |
| Haiku 4.5 | $1 | $5 | — | — | — | — | — |
| Opus 4.8 | $5 | $25 | — | — | $0.50 | $2.50/$12.50 | $10/$50 |

Prompt caching экономит до 90%; batch −50%; US-only inference ×1.1; Fast mode ×2 цена за ×2.5 скорость (research preview, только Claude API; нет на Bedrock/Vertex/Foundry). Минимум кэшируемого промпта на Opus 5 снижен до **512 токенов** (было 1024 на 4.8).

**[ПФ] Практический расчёт.** Прогон агента 100K вход + 20K выход на Opus 5: standard **$1.00**; cache hit **$0.55**; batch **$0.50**; fast **$2.00**; US-only **$1.10**.

### 1.4. Effort — механика [ПФ]

Пять уровней: `low`, `medium`, `high`, `xhigh`, `max`. Устанавливается как `output_config.effort`, без beta-заголовка, на весь запрос. По умолчанию — `high` (API и Claude Code). (Разночтение: часть источников называет нижний уровень `min` для API — официальные доки Opus 5 перечисляют low/medium/high/xhigh/max.)

Effort управляет **всеми токенами**: reasoning, текстом ответа и вызовами инструментов вместе. Ниже effort → меньше tool-calls, объединённые операции, без преамбулы; выше → больше tool-calls, планы, детальные саммари. Для агентских задач деньги уходят в число tool-calls. Это поведенческий сигнал, а не жёсткий лимит: на low модель всё равно думает над трудными задачами, просто меньше.

**Особенности Opus 5:**
- Отключить thinking (`thinking:{"type":"disabled"}`) можно **только на `high` и ниже**; с `xhigh`/`max` → HTTP 400 (breaking change vs 4.8).
- С выключенным thinking Opus 5 иногда пишет tool-call текстом вместо `tool_use`-блока или протекает XML-тегами — держите thinking включённым, управляйте ценой через effort.
- **Task/effort budgets меняются per-turn mid-conversation**, но смена effort/speed **инвалидирует prompt cache** (effort влияет на рендер промпта). Держите effort постоянным внутри кэшируемого разговора, варьируйте между ворклодами.
- Mid-conversation tool changes (beta-заголовок `mid-conversation-tool-changes-2026-07-01`): добавлять/убирать инструменты **без** инвалидации кэша.
- На `xhigh`/`max` ставьте большой `max_tokens` (старт 64K) — он ограничивает thinking+текст суммарно.

### 1.5. Классификаторы безопасности и фолбэки

**[ПФ]** Fable 5 включает классификаторы, отклоняющие запрос: приходит не ошибка, а нормальный ответ HTTP 200 с `stop_reason:"refusal"`. Категории отказов (первоисточник refusals-and-fallback): `cyber`, `bio`, `frontier_llm`, `reasoning_extraction`. Mythos 5 классификаторов не имеет. Opus 5 — самый выровненный: misalignment score **2.3** (лучший из недавних моделей).

**Частота срабатывания.** **[ПФ]** Anthropic (launch page Opus 5): классификаторы Opus 5 «срабатывают примерно на **85% реже**, чем у Fable 5»; в общем трафике «более 95% сессий Fable вообще не задействуют фолбэк». **[О/Г]** Конкретные цифры «Fable 5: 42% вызовов в 26% trials; Opus 5: 5% в 4% trials» — с одного прогона FrontierBench в безопасно-чувствительных доменах; вторичный источник ссылается на system card, но verbatim в доступном тексте карты не найден.

**[ПФ] Куда падает запрос.** В Claude.ai, Claude Code, Claude Cowork флагнутые запросы по умолчанию падают на **Opus 4.8**. Био-запросы, блокируемые на Fable 5, теперь роутятся на Opus 5. На API — параметр `fallbacks` (beta): режим `"default"` применяет рекомендованные Anthropic модели по категории отказа (заголовок `server-side-fallback-2026-07-01`); explicit-list — `server-side-fallback-2026-06-01`. Fallback только на отказ классификатора, не на rate limit/overload. Отказ до вывода не биллится. Недоступно на Batch API, Bedrock, Vertex, Foundry (там SDK middleware `BetaRefusalFallbackMiddleware`).

**[ПФ] Cyber Verification Program (CVP).** Бесплатная заявочная программа для **Opus и Sonnet**. Две блокируемые категории: *Prohibited use* (mass data exfiltration, ransomware — блок навсегда, не снимается) и *High Risk Dual use* (эксплуатация уязвимостей, offensive tooling — блок по умолчанию, снимается по заявке для defensive-целей). **CVP требует включённого data retention**; ZDR-организации создают отдельный workspace с retention. Недоступно на Bedrock и Vertex; цель решения — 2 рабочих дня.

**[ПФ] Кибербезопасность.** Opus 5 разрешает поиск уязвимостей в исходниках на всех уровнях доступа, но блокирует binary-based сканирование, penetration testing и генерацию эксплойтов. На OSS-Fuzz ненулевой скор на **79.4% целей** (Opus 4.8 — 38.5%), близко к Mythos 5 (80%), но слабее в разработке эксплойтов.

### 1.6. Data retention [ПФ + О]

Opus 5 — «no data retention requirements for general access», поддерживает zero data retention (ZDR). Fable 5 и Mythos 5 требуют **30-дневного anti-abuse хранения** всех входов/выходов на всех поверхностях (не в обучение, доступ логируется, удаление через 30 дней, если нет расследования/юробязательства) — подтверждено множеством вторичных источников и косвенно самой Anthropic (CVP требует retention). **Вывод для FINPILOT:** на Fable 5/Mythos 5 нельзя гнать ПДн без учёта 30-дневного хранения; Opus 5/Sonnet 5 под ZDR предпочтительны.

### 1.7. Токенизатор и кириллица

**[ПФ]** Линейка 5 использует **новый токенизатор**. Официально (доки Sonnet 5): «тот же текст даёт примерно на **30%** больше токенов, чем на Sonnet 4.6». **[О]** Независимые замеры: Simon Willison — ×1.4 английский, ×1.33 испанский, ×1.28 Python, ≈без изменений китайский; Synthorai — **+41%** для английского (2245 против 1594 токенов на идентичном тексте). Цена за токен не изменилась, но **фактическая стоимость того же текста выросла на ~30–41%**, а контекстное окно вмещает меньше текста.

**[О] Кириллица.** Небазовые для латиницы языки: одно неанглийское слово стоит в среднем 2–5 токенов против 1–2 для английского; для кириллицы коэффициент ×2–4. Точных официальных данных Anthropic по кириллице для линейки 5 нет. **Вывод для FINPILOT:** русский промпт может стоить в 2–4 раза больше токенов, чем тот же смысл по-английски, и это умножается на +30–41% нового токенизатора. Проверяйте тексты через claudetokenizer.com и count_tokens API.

### 1.8. Различия по поверхностям (ключевой вопрос)

**[ПФ]** Команда Claude Code (Boris Cherny, Thariq Shihipar / Cat Wu, 24.07.2026) **удалила более 80% системного промпта** для Opus 5 и Fable 5 «без измеримой потери на кодовых оценках». Anthropic **использует РАЗНЫЙ системный промпт для каждой модели**: только фронтир-модели получили сокращение, старые модели сохраняют полный промпт (им нужно больше явных указаний; данных, может ли сильная модель надёжно доподбирать детали для слабой, у команды нет). Шесть сдвигов: правила → суждение; примеры → дизайн интерфейса (типизированные параметры/enum вместо примеров); всё-заранее → прогрессивное раскрытие через skills; дублирование инструкций → консолидация в описания инструментов; ручной CLAUDE.md → авто-память; markdown-спеки → богатые референсы (код, тесты, рубрики). Появилась команда `claude doctor` для right-size ваших skills и CLAUDE.md.

**[ПФ + О] Поверхности:**
- **Чат claude.ai** — «think»: вопрос-ответ, артефакты (до 20 MB persistent storage каждый, inline-редактирование с июня 2026), загрузка ≤20 файлов / 30MB на разговор в облако.
- **Claude Cowork** — «everything else»: локальный агент, читает/пишет файлы на машине, исполняет код в VM, ходит в браузер с вашими куками, scheduled tasks. Ограничение — насыщение контекста (project retrieval тянет только релевантное).
- **Проект claude.ai** — держит фон; при переполнении включается RAG (см. ниже).
- **Claude Code** — «build»: тонкий системный промпт для Opus 5/Fable 5, effort `high` по умолчанию, MCP tool search, хуки, субагенты, plugins.
- **Claude Design** — визуальная работа на canvas.

Отличаются: системные промпты (по модели и по продукту), доступные инструменты, лимиты (единый пул — см. Направление 3), поведение. Контекстное окно моделей одинаковое (1M у Opus 5/Fable 5/Sonnet 5, 200K у Haiku 4.5). В Claude Code стартовые накладные (system prompt ~4200 токенов, CLAUDE.md ~1800, MCP-схемы) съедают часть окна до первого промпта.

**[ПФ + Г] RAG в Проектах.** Официально: когда знание проекта приближается к лимиту контекстного окна, Claude автоматически включает RAG-режим, расширяя ёмкость до ~10× через `project_knowledge_search`; при падении объёма ниже порога — возврат к context-based. НО в баг-репортах Anthropic пользователи сообщают, что порог по факту срабатывает по **числу файлов (около 13)**, а не по объёму токенов (RAG включался при ~73K токенов и 13 файлах; при том же объёме в 12 файлах — не включался). Частичное извлечение при RAG у ряда пользователей ухудшало качество и adherence. **Вывод:** если knowledge base ≤~200K токенов и важна точность — держите мало крупных файлов (не дробите на десятки мелких), чтобы остаться в полном контексте; при больших объёмах — принимайте RAG и структурируйте документы под поиск.

---

## Направление 2. Claude для дизайна и фронтенда

### 2.1. Официальный frontend-design skill [ПФ]

`frontend-design` — официальный плагин/skill Anthropic (авторы Prithvi Rajasekaran, Alexander Bricken). Установка: `/plugin install frontend-design@claude-plugins-official`. Внутри — **единственный SKILL.md** (~46 строк, **~1300 токенов** «дизайн-философии», запускается до того, как Claude трогает код); по данным трекинга плагина, **более 564 000 разработчиков установили** его. Активируется автоматически на фронтенд-задачах. Механика: заставляет Claude **до кода** объявить рамку — purpose, audience, конкретное эстетическое направление (brutalist, maximalist, retro-futuristic, luxury, playful, editorial, art deco, industrial и т.д.) — и намеренно избегать generic-паттернов (системные шрифты, фиолетовые градиенты, cookie-cutter компоненты). Ключевые области: типографика (неожиданные пары display+body), оркестрованная анимация, асимметричная композиция, глубина через градиенты/текстуры. Поддерживает React/Vue/Svelte/vanilla. Родственный Design Plugin — критика/UX-writing/a11y-аудит/research synthesis/dev handoff.

**[О]** Skill «поднимает пол» качества, но не «магия» — устойчивый AI-slop-отпечаток остаётся. Для финтех-уровня (Т-Банк/Сбер/Альфа) дисциплину держит DESIGN.md + токены + линтеры (2.5–2.6).

### 2.2. Claude Design [ПФ]

Запущен апрель 2026 (Anthropic Labs) как ответ Figma/Canva; >1 млн пользователей в первую неделю. Обновление 17.06.2026 перевело из research preview в beta и добавило:
- **Импорт дизайн-систем** (GitHub / локальная кодовая база / дизайн-файлы).
- **WYSIWYG-канвас**: комментарии на элементах, прямое редактирование текста, слайдеры spacing/color, drag/resize/align.
- **Двусторонний `/design-sync`**: из Claude Code `/design-sync` тянет дизайн-систему в репозиторий или пушит построенное обратно в canvas; команда `/design` — создавать/редактировать/синхронизировать проекты из терминала.
- **Экспорт** в PDF и PPTX; **коннекторы** (9+): Adobe, Canva, Gamma, Lovable, Replit, Vercel, Base44, Miro, Wix.
- **Admin-роли** brand control (Team/Enterprise; у Enterprise выключено по умолчанию).
- **Единые лимиты** с claude.ai/Cowork/Code (с мая 2026); средний turn дешевле по токенам.

Доступно Pro/Max/Team/Enterprise, web + desktop, claude.ai/design.

**[О] Ограничения.** Figma выигрывает multiplayer design ops, токены в масштабе, агентские workflow. Claude Design выигрывает скорость «intent → clickable» и handoff в Claude Code. **[Пробел]** Точная минимальная версия Claude Code для `/design-sync` в публичных источниках не указана — синхронизация появилась с июньским обновлением 2026.

### 2.3. AI slop и работающие паттерны промптов

**[ПФ] Anthropic Frontend Aesthetics Cookbook.** Модели сходятся к «on distribution» выводу — усреднению обучающих данных. Официальный DISTILLED_AESTHETICS_PROMPT: избегать Arial/Inter/Roboto/системных шрифтов и клише (особенно фиолетовые градиенты на белом); коммит к единой эстетике через CSS-переменные; доминирующие цвета с резкими акцентами вместо робких палитр; вдохновение от IDE-тем и культурных эстетик; анимации с фокусом на один оркестрованный page-load со staggered reveals (`animation-delay`); атмосферные фоны вместо solid; явно избегать даже Space Grotesk.

**[О] Работающие паттерны:**
1. Заменить «modern» на **имя направления** (Swiss/editorial, brutalist, industrial-mono, organic) — «clean and modern» = сам slop-дефолт.
2. Один **DESIGN.md в корне** как единственный источник правды (палитра, шрифты, radius, текстура, motion); агент читает его перед стилизацией.
3. **60/30/10**: доминант ≈60%, нейтраль ≈30%, резкий акцент ≈10%; расширять оттенками/тенями, не новыми hue; 4 семантических цвета отдельно от бренд-цветов; не чистый чёрный/белый фон.
4. **Мандат сетки**: 12 колонок, gutters 80px, hero в колонках 2–8 (асимметрия), 8px база, вертикальные отступы кратны 24px.
5. **Одна самая громкая вещь**: hero 92px display serif, остальное 14–16px нейтральный sans.
6. Каждый follow-up **ссылается на дизайн-систему** («…using --color-primary»).

### 2.4. Визуальная верификация [ПФ + О]

| Инструмент | Механика | Токены/вызов | Кросс-браузер | CI/headless | Сценарий |
|---|---|---|---|---|---|
| **Playwright MCP** | accessibility-tree снапшот каждый шаг (33+ инструмента) | высокие: снапшот сложной страницы 50 000+; на порядок дороже DevTools на multi-page | Chromium/Firefox/WebKit/Edge | да (GitHub Actions) | E2E, детерминированная навигация, генерация тестов |
| **Chrome DevTools MCP** | слушает CDP-события, скриншот по необходимости | низкие (хирургично) | только Chrome | attach к запущенному Chrome | debug перф/сети/консоли |
| **Claude in Chrome** | ваш браузер с куками/сессиями | ~15 400/запрос | Chrome | **нет** (не headless) | быстрая проверка в аутентифицированном приложении |

Разница Playwright vs DevTools ≈5.3K токенов/вызов; на multi-page аудитах Playwright дороже на порядок. **Рекомендация:** Playwright для тест-сьюта/пре-релиза, Claude in Chrome для повседневной разработки, DevTools для перф/сети. Держать сессии короткими: «один инструмент, один вопрос, один ответ». Скриншоты (`browser_take_screenshot`) только когда нужны пиксели (регрессия, OCR, превью), иначе accessibility-snapshot дешевле.

**Петля для FINPILOT:** генерация → скриншот на desktop+mobile ширине → сравнение до/после → фикс layout-багов → повтор. Opus 5 умеет self-verification сам, но контролируйте токен-стоимость скриншотов.

### 2.5. Субагенты и хуки под фронтенд [ПФ]

Субагенты — Markdown с YAML-frontmatter в `.claude/agents/` (проект) или `~/.claude/agents/`. Поля: `description, prompt, tools, disallowedTools, model, permissionMode, mcpServers, hooks, maxTurns, skills, initialPrompt, memory, effort, background, isolation, color`. Роли и минимальные права:
- **design-critic / a11y-auditor / code-reviewer (read-only):** `tools: Read, Grep, Glob`; a11y-reviewer advisory, не правит код.
- **research:** `Read, Grep, Glob, WebFetch, WebSearch`.
- **visual-regression:** Playwright-субагент — keyboard traversal, dynamic state, viewport, contrast, a11y-tree.
- **Модель под роль:** `model: haiku` для простых субагентов; Opus — для архитектурного рассуждения.

**Хуки** — детерминированные скрипты на события жизненного цикла (не галлюцинируют). Настройка во frontmatter субагента (пока активен) или в `settings.json` (session-wide). Пример auto-test после правки:
```json
{"hooks":{"PostToolUse":[{"matcher":"Edit|Write","hooks":[{"type":"command","command":"cd $CWD && bun test --bail 2>&1 | tail -10"}]}]}}
```
Хук блокирует коммит на падающих тестах. Используйте хуки для линтинга/форматирования/проверок безопасности, которые ДОЛЖНЫ выполняться всегда.

### 2.6. Дизайн-система, токены, принуждение [О/рекомендация]

- **DESIGN.md + design tokens** как единственный источник правды, ссылка из CLAUDE.md.
- **Линтеры/CI:** stylelint с запретом «магических» hex/px вне токенов; design-system-auditor субагент валидирует color/focus-ring/spacing/motion до попадания в UI.
- **PostToolUse-хук** гоняет линтер стилей на каждом Edit/Write и возвращает вывод в контекст — Claude видит нарушение и чинит.
- Типографическую шкалу и сетку фиксируйте в токенах (8px база, шкала кратна 24px).

### 2.7. Доступность (WCAG AA автоматически) [ПФ]

Готовые skills/агенты для агентского цикла:
- `a11y-audit` (Scan→Fix→Verify, WCAG 2.2 A/AA, React/Next/Vue/Angular/Svelte/HTML, `--fix`, `--ci`).
- `claude-a11y-skill` (airowe): axe-core + jsx-a11y.
- `accessibility-agents` (Community-Access): 11 специалистов, авто-принуждение WCAG 2.2 AA на каждом чате, поведенческое сканирование через Playwright.

Автоматика ловит ~30–50% a11y-проблем; остальное — ручная проверка (скринридер, клавиатура). **Рекомендация:** подключить `a11y-audit --ci` как gate (блок PR на violations) + axe-core против отрендеренных страниц. Для финтеха AA — обязательный минимум.

### 2.8. Контекст для фронтенда [ПФ + рекомендация]

- **Тонкий CLAUDE.md** (у одной проверенной команды <500 токенов), path-scoped rules вместо монолита.
- Структура: `.claude/{CLAUDE.md, rules/, agents/, skills/, settings.json, .mcp.json}`.
- **Убрать** противоречивые правила и инструкции верификации (Opus 5 сам верифицирует).
- `low`/`medium` на Opus 5 заметно сильнее, чем те же уровни на 4.8 — пересобрать effort-дефолты свежим свипом на своих eval.
- Прогнать `claude doctor`.

---

## Направление 3. Экономика токенов и лимитов

### 3.1. Лимиты Pro / Max 5x / Max 20x (2026)

**[ПФ]** Двухслойно: **5-часовое скользящее окно** (с первого сообщения, обновление через 5 ч) + **недельный лимит** (сброс через 7 дней в 00:00 UTC). 06.05.2026 Anthropic **удвоил 5-часовые лимиты** для Pro/Max/Team/seat-Enterprise и убрал peak-hour урезание; недельный не менялся. Pro — один недельный лимит на все модели; Max — два (общий + привязанный к Sonnet).

**[О] Эмпирические оценки сообщества** (Anthropic не публикует числа в токенах):

| План | Цена | Сообщений/5ч | Claude Code часов/неделю | Токенов/5ч (оценка) |
|---|---|---|---|---|
| Pro | $17 годовой / $20 месячный | ~45 | — | ~44K |
| Max 5x | $100 | ~225 | 140–280 | ~5× Pro |
| Max 20x | $200 | ~900 | 240–480 | ~20× Pro |

Быстрее «сжигают»: Opus, длинный контекст, большие вложения, extended thinking.

**[ПФ] Non-interactive usage.** С 15.06.2026 Agent SDK, `claude -p`, GitHub Actions, сторонние приложения на подписке тянут из **отдельного месячного кредита**: $20 Pro, $100 Max 5x, $200 Max 20x. Исчерпался — переход на usage credits по API-ценам или остановка. Кредит не переносится.

### 3.2. Общий пул [ПФ]

Pro/Max usage — **один пул** между claude.ai chat, Claude Code, Проектами, Cowork и Claude Design (выровнено май 2026). Тяжёлое использование чата днём оставляет меньше токенов Code в том же окне. Проверка: `/usage`, `/status` в Code; Settings → Usage на claude.ai. **Для 4 параллельных аккаунтов:** каждый — свой пул; распределяйте задачи между аккаунтами, но внутри одного аккаунта все поверхности конкурируют за окно.

### 3.3. Токены на запрос [О]

**CodeRabbit (код-ревью):** Opus 5 **≈60.5K входных** (55–64K по конфигу) и **≈9.5K выходных** (8.1–10.8K) токенов на вызов, против **≈40.5K/≈5.8K** у GPT-5.6-lane baseline. Opus 5 читает на ~50% больше и пишет на ~65% больше. x-high — самый тяжёлый писатель (10.8K выход); больше effort ≠ автоматически больше выход. Effort→output на eval-suite: medium 29M / high 52M / xhigh 76M / max 100M. Отдельных публичных «X тыс./Y тыс.» замеров по Sonnet 5/Haiku 4.5/Fable 5 на вызов мало — используйте собственные (3.6).

### 3.4. Что влияет на расход [ПФ]

- **Стартовые накладные Claude Code:** system prompt ~4200 токенов, CLAUDE.md ~1800, file reads 1100–2400 каждый.
- **MCP-серверы:** GitHub MCP ≈**42 000 токенов** (≈21% окна 200K); типичная сборка 4 сервера ≈7000 токенов overhead/сообщение; 5+ серверов → 50 000+ до первого промпта; один инструмент ≈1000 токенов схемы. С mid-2026 Claude Code **defer tool schemas via tool search**: грузятся только имена, схемы по требованию; порог по умолчанию 10% окна (`ENABLE_TOOL_SEARCH=auto:5` — агрессивнее, 5%). Anthropic: с tool search 50+ инструментов = **~8.7K токенов вместо ~77K (−85%)**, сам tool search +~500 токенов.
- **MCP output:** предупреждение при >10 000 токенов, дефолтный лимит 25 000 (`MAX_MCP_OUTPUT_TOKENS`).
- **Кэширование:** read ≈10% цены input (−90%); warm turn ≈$0.0017 против $0.0043.

### 3.5. Техники экономии [ПФ + О]

- `/clear` между задачами (после v2.1.211 тотали сбрасываются на `/clear`).
- `/compact` — сжатие истории.
- **Отключить лишние MCP** — крупнейший контролируемый расход; tool search до −85%.
- **Модель под подзадачу:** `model: haiku` для простых субагентов; Sonnet 5 первым, эскалация на Opus 5.
- **Кэширование** (−90%); стабильный префикс, не менять effort/tools внутри кэшируемой сессии.
- **Сократить knowledge base** (≤~13 файлов держит полный контекст — 1.8).
- Enterprise-бенчмарк расхода: ~$13/разработчик/активный день, $150–250/мес, <$30/день у 90%.

### 3.6. Инструменты подсчёта и методика для FINPILOT

**[ПФ] Инструменты:**
- **ccusage** (npx ccusage@latest, **16 500 звёзд**, парсит локальные логи, ничего не шлёт наружу; фильтры дата/проект/модель, экспорт JSON; session-reports с Input/Output/Cache Create/Cache Read/Total/Cost).
- **Claude-Code-Usage-Monitor** (**8 300 звёзд**, real-time чарт, burn-rate, прогноз до лимита).
- **ccflare** (web-дашборд), **claude-doctor** (диагностика context/hooks/MCP/config), **ccstatusline**.
- Встроенные: `/usage`, `/status` (остаток + время до сброса), `/cost` (для API-ключа). Claude Code считает $ локально по list-ценам — может расходиться с реальным счётом.
- Внешние: Tokens 4 Breakfast (€7.99), tokenkarma, TokenMix.

**Методика перехода от «всегда max» к обоснованному выбору:**
1. Установить **ccusage**, снять baseline неделю: `npx ccusage@latest --verbose` после значимых сессий.
2. Построить таблицу **`модель × effort × тип задачи → токены → время → принято/переделано`**. Типы FINPILOT: (a) новый React-компонент по дизайн-системе, (b) рефактор/миграция, (c) фикс бага, (d) визуальная доводка, (e) написание/починка Vitest/Playwright-теста, (f) код-ревью.
3. **Канареечный протокол:** 100–300 реальных задач, прогон Sonnet 5 → Opus 5 high → Opus 5 xhigh; сравнить принятые результаты, ретраи, ручные правки, tool-call failures, output-токены, латентность, **стоимость на принятую задачу** (не на токен).
4. **Гипотезы:** (H1) для CRUD-компонентов и тестов Sonnet 5 / Opus 5 medium достаточно; (H2) xhigh нужен только для сложных миграций и багов концентрации; (H3) max почти не окупается; (H4) русский промпт стоит ×2–4 токенов → переписать системные артефакты на английский.
5. **Метрика решения:** cost per successful task. Правило: начинать с high, тестировать medium на canary, эскалировать xhigh только на дорогих падениях, max — почти никогда.
6. **Никогда silent fallback** на другую модель без логирования, какая модель обработала запрос.

---

## Направление 4. Что легко упустить

### 4.1. Pencil (pencil.dev) [ПФ + О]

Сторонний Figma-подобный бесконечный canvas поверх Claude Code через MCP; запущен в конце января 2026, **100 000+ пользователей** вскоре после. Desktop-приложение + расширение для Cursor (браузерной версии нет — нужен локальный Claude CLI); `.pen` JSON-файлы версионируются в Git (проект прошёл через a16z Speedrun). Слои слева, CSS-свойства справа, canvas в центре, панель AI-агента (Claude Code «под капотом»). Sticky notes → runnable-промпты. **Сейчас бесплатен** (upstream-затраты — ваша подписка Claude Code от $20/мес). Ручные правки (CSS, копирайт, layout) на canvas **не тратят токены Claude Code**. Импортирует Figma, уважает дизайн-системы (Shadcn и др.).

**[О] Рекомендация.** Pencil vs Claude Design: Pencil — canvas в вашем Git/IDE, MCP-агенты правят `.pen` рядом с кодом; Claude Design — облачный canvas с официальным `/design-sync`. Для solo-разработчика на Intel Mac, живущего в терминале, Pencil даёт быструю визуальную итерацию с экономией токенов на ручных правках — стоит попробовать бесплатно. Официальный `/design-sync` и коннекторы — только у Claude Design. Код от Pencil требует ревью на семантику/a11y/производительность/соответствие библиотеке. **Вывод:** Pencil — опциональный ускоритель исследования дизайна; ядром держите Claude Code + frontend-design skill + Claude Design для handoff.

### 4.2. Инструменты экосистемы [ПФ]

- **Official plugins/skills:** frontend-design, Design Plugin, Superpowers (brainstorming, субагент-разработка с ревью, TDD), Context7 MCP (live-доки).
- **MCP:** Playwright, Chrome DevTools, Claude in Chrome, filesystem, memory, git.
- **Чат:** Output styles, Fork, /btw, /rewind, /recap.
- **Code:** Routines, /ultrareview, Auto Mode, Ultrathink, Subagents, Hooks, Plugins.
- **Cowork:** Live Artifacts, Routines, plugin marketplace.
- **Дашборды:** ccusage, Claude-Code-Usage-Monitor, ccflare, ccstatusline, claude-doctor.
- **A11y:** a11y-audit, claude-a11y-skill, accessibility-agents.

### 4.3. Возможности Claude Code, которые редко используют [ПФ]

Хуки, output styles, subagent-конфигурации (tool/model restriction), `/plugin`, `/design`, **headless-режим** (`claude -p`), **GitHub Actions**, **параллельные сессии**, **git worktrees**, **background tasks** (с v2.1.198 субагенты в фоне по умолчанию, могут коммитить/пушить/открывать draft PR по завершении worktree-кода, шлют Notification hook), **plan mode**, `claude doctor`, оркестрация параллельных субагентов (opt-in, кап 16 агентов). Model routing: `/model opus` (с v2.1.219 ведёт на Opus 5). Sonnet 5 — дефолт в Code с v2.1.197 (30.06.2026).

### 4.4. Свежие изменения 2026 [ПФ]

Удвоение 5-часовых лимитов (06.05.2026); единый пул поверхностей; отдельный месячный кредит non-interactive (15.06.2026); tool search для MCP (−85%); сокращение системного промпта на 80% для Opus 5/Fable 5 + `claude doctor`; двусторонний `/design-sync`; фоновые субагенты и Claude in Chrome в GA (v2.1.198); Opus 5 как дефолт Max / сильнейший на Pro (24.07.2026).

### 4.5. Риски и подводные камни (152-ФЗ и безопасность)

**[ПФ]**
- **Prompt injection.** Anthropic называет это главным риском Cowork. По данным Anthropic (Claude for Chrome): без митигаций attack success rate в автономном режиме составлял **23.6%**, снижен до **11.2%** — независимый исследователь Simon Willison назвал остаток «catastrophic». Для Opus 5 Auto Mode система-карта заявляет **0%** на 1 290 попытках с полными защитами (и 3.70% без доп. защит). В январе 2026 продемонстрирована exfiltration файлов через indirect injection в Cowork. Cowork исполняет код в VM, читает/пишет/удаляет файлы, ходит в браузер с куками; режим «Skip all approvals» ничего не проверяет.
- **Community-плагины.** Anthropic **не контролирует** MCP-серверы/файлы в плагинах — предупреждение прямо на marketplace. Устанавливайте только доверенные.
- **Секреты.** Не давайте агенту доступ к .env/секретам без нужды; ограничивайте `tools`/`permissionMode` субагентов; хуки против опасных команд (`rm -rf`).
- **[Рекомендация, не юрсовет] 152-ФЗ / ПДн.** FINPILOT обрабатывает персональные финансовые данные граждан РФ. Anthropic хранит данные вне РФ — прямой конфликт с требованием локализации ПДн (ст. 18 152-ФЗ). **Не передавайте реальные ПДн (ФИО, счета, транзакции конкретных лиц) в Claude ни на одной поверхности.** На Fable 5/Mythos 5 добавляется обязательное 30-дневное хранение — категорически не для ПДн. Работайте на **синтетических/обезличенных данных**; в CLAUDE.md и хуках запретите чтение файлов с реальными ПДн; Cowork с локальными файлами — особый риск. (BAA-контекст HIPAA иллюстрирует, что для регулируемых данных поверхности неравны: Claude Code покрыт частично, Cowork — не покрыт вообще.)

### 4.6. Что ещё сказал бы независимый эксперт

- **Измерьте расход 4 аккаунтов перед оплатой** (ccusage). Возможно, один Max 20x + один Pro закрывает потребность дешевле, чем 4× Pro/Max, и упрощает управление контекстом.
- **Cost per successful task, а не per token** — единственная честная метрика; Opus 5 с меньшим числом ретраев может быть дешевле «дешёвой» модели, требующей итераций.
- **Свежесть знаний:** у Opus 5 cutoff май 2026 — он «свежее» знает экосистему (React 19, TanStack и т.д.), чем Fable 5/Sonnet 5 (январь 2026). Для новых API это плюс Opus 5.
- **1473 теста — ваш актив:** отдавайте Opus 5 «богатые референсы» (тесты, рубрики) вместо markdown-спеков — это прямо соответствует новой context-engineering-парадигме Anthropic.
- **Держите бэкенд (v7.7.1) отдельным контекстом** от фронтенд-вехи 8 — не смешивайте в одном Проекте, чтобы не раздувать knowledge base и не триггерить RAG.

---

## Полный список источников (URL)

**Модели, бенчмарки, цены, effort, безопасность:**
- https://platform.claude.com/docs/en/about-claude/models/whats-new-opus-5
- https://platform.claude.com/docs/en/about-claude/models/whats-new-sonnet-5
- https://platform.claude.com/docs/en/about-claude/models/introducing-claude-fable-5-and-claude-mythos-5
- https://www.anthropic.com/news/claude-opus-5
- https://www.anthropic.com/claude-opus-5-system-card
- https://www.anthropic.com/news/claude-fable-5-mythos-5
- https://www.anthropic.com/news/redeploying-fable-5
- https://www.anthropic.com/claude/fable
- https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback
- https://support.claude.com/en/articles/14604842-real-time-cyber-safeguards-on-claude-opus-and-sonnet
- https://coursiv.io/blog/claude-opus-5
- https://www.coderabbit.ai/blog/opus-5-model-review
- https://dev.to/tokenmixai/i-did-the-math-on-claude-opus-5-max-effort-cost-94-more-than-high-effort-4ebk
- https://www.mindstudio.ai/blog/claude-opus-5-pricing-reasoning-guide
- https://hashnode.com/blog/claude-opus-5-effort-levels-cost
- https://tech-tech.life/2026/07/26/claude-opus-5-full-review-i-ran-the-benchmarks/
- https://www.cnbc.com/2026/06/09/anthropic-mythos-claude-fable-5.html
- https://techcrunch.com/2026/06/09/anthropics-claude-fable-5-is-a-version-of-mythos-the-public-can-access-today/
- https://aws.amazon.com/blogs/aws/anthropic-claude-fable-5-on-aws-mythos-class-capabilities-with-built-in-safeguards-now-available/
- https://cloudzero.com/blog/claude-opus-5-pricing/

**Токенизатор / кириллица:**
- https://simonwillison.net/2026/Jun/30/claude-sonnet-5/
- https://synthorai.io/blog/claude-sonnet-5-tokenizer/
- https://textkit.tech/blog/tokens-per-word-tokenizer-comparison-2026
- https://webscraft.org/blog/scho-take-tokeni-u-chatgpt-claude-i-gemini
- https://www.claudetokenizer.com/
- https://tokencontributions.substack.com/p/whole-words-and-claude-tokenization

**Системный промпт / context engineering / поверхности / RAG:**
- https://aiweekly.co/alerts/anthropic-deletes-80-of-claude-codes-system-prompt-for-claude-5
- https://explainx.ai/blog/claude-5-context-engineering-thariq-doctor-july-2026
- https://charlesjones.dev/blog/claude-opus-5-context-engineering-what-to-delete
- https://www.developersdigest.tech/blog/claude-5-context-engineering-rules-hn-analysis
- https://finance.biggo.com/news/7df48019614f68c0
- https://magica.com/news/anthropic-claude-code-system-prompt-reduction
- https://support.claude.com/en/articles/11473015-retrieval-augmented-generation-rag-for-projects
- https://github.com/anthropics/claude-code/issues/25759
- https://github.com/anthropics/claude-code/issues/46878
- https://airegeneration.substack.com/p/working-with-claude-part-1-the-stack
- https://suprmind.ai/hub/claude/features/
- https://emergingai.substack.com/p/claude-changed-the-july-2026-way

**Фронтенд / дизайн / AI slop / a11y:**
- https://github.com/anthropics/claude-code/blob/main/plugins/frontend-design/skills/frontend-design/SKILL.md
- https://claude.com/plugins/frontend-design
- https://claude.com/plugins/design
- https://claude.com/product/design
- https://platform.claude.com/cookbook/coding-prompting-for-frontend-aesthetics
- https://thomas-wiegold.com/blog/claude-code-frontend-design-plugin/
- https://vibecodekit.dev/ai-slop-design
- https://ui-ux-pro-max-skill.com/blog/avoiding-ai-slop/
- https://explainx.ai/blog/claude-design-june-2026-update-design-sync-2026
- https://www.techrepublic.com/article/news-anthropic-claude-design-overhaul-enterprise-teams/
- https://venturebeat.com/technology/anthropic-ships-major-claude-design-overhaul-with-design-system-imports-code-round-trips-and-a-fix-for-its-token-burning-problem
- https://github.com/airowe/claude-a11y-skill
- https://github.com/Community-Access/accessibility-agents
- https://www.claudedirectory.org/skills/claude-skills-a11y-audit
- https://medium.com/@porter.nicholas/anthropic-skills-marketplace-the-anti-ai-slop-ui-design-skill-a572d0cfef4f

**Визуальная верификация / MCP / браузер:**
- https://claude-codex.fr/en/advanced/browser-automation/
- https://www.trackingplan.com/blog/chrome-devtools-mcp-vs-playwright-mcp-digital-analysts
- https://stevekinney.com/writing/driving-vs-debugging-the-browser
- https://ayyaztech.com/blog/chrome-devtools-mcp-vs-claude-in-chrome-vs-playwright
- https://mcp.directory/blog/chrome-devtools-mcp-vs-playwright-mcp-2026
- https://lalatenduswain.medium.com/playwright-mcp-vs-claude-in-chrome-which-browser-testing-tool-should-you-use-in-2026-e502bee0067a

**Субагенты / хуки / Claude Code:**
- https://code.claude.com/docs/en/sub-agents
- https://code.claude.com/docs/en/mcp
- https://code.claude.com/docs/en/costs
- https://github.com/VoltAgent/awesome-claude-code-subagents
- https://samuellawrentz.com/blog/claude-code-hooks-subagents/
- https://ai.rundatarun.io/ai-development-agents/claude-code-best-practices
- https://blakecrosley.com/guides/claude-code
- https://medium.com/data-science-collective/i-spent-6-months-tuning-claude-code-heres-the-exact-setup-that-finally-worked-b41c67628478

**Лимиты / токены / MCP overhead:**
- https://www.morphllm.com/claude-code-usage-limits
- https://www.faros.ai/blog/claude-code-token-limits
- https://www.faros.ai/blog/claude-code-token-usage
- https://deployhyre.com/ai-tools/claude-usage-limits/
- https://tokenmix.ai/blog/complete-claude-limits-guide-2026-tokens-uploads-5-hour
- https://tokenkarma.app/claude-usage-limit/
- https://www.tminusai.com/blog/claude-usage-limit-reached
- https://getunblocked.com/blog/claude-code-context-window/
- https://www.jdhodges.com/blog/claude-code-mcp-server-token-costs/
- https://www.getmaxim.ai/articles/how-to-reduce-mcp-token-costs-for-claude-code-at-scale/
- https://github.com/modelcontextprotocol/modelcontextprotocol/issues/2808
- https://www.atcyrus.com/stories/mcp-tool-search-claude-code-context-pollution-guide
- https://docs.bswen.com/blog/2026-04-23-ccusage-token-tracking/
- https://ccusage.com/guide/session-reports
- https://claudefa.st/blog/tools/monitors/claude-code-usage-monitor
- https://shipyard.build/blog/claude-code-track-usage/

**Pencil / Cowork / безопасность:**
- https://designwithai.substack.com/p/exploring-pencildev-walkthrough-and-impressions
- https://medium.com/design-bootcamp/exploring-pencil-dev-walkthrough-and-impressions-90c4587231c6
- https://flowstep.ai/blog/pencil-dev-pricing/
- https://www.banani.co/blog/pencil-dev-review
- https://atomize.tools/blog/figma-vs-pencil-design-system/
- https://www.promptarmor.com/resources/implement-claude-cowork-securely
- https://support.claude.com/en/articles/13364135-use-claude-cowork-safely
- https://productimpactpod.com/news/ux-researcher-guide-claude-tools/
- https://claude.com/blog/claude-for-chrome

---

### Приложение: сводная рекомендация по выбору модели/effort для FINPILOT

| Задача вехи 8 | Модель | Effort | Обоснование |
|---|---|---|---|
| Новый React-компонент по дизайн-системе | Sonnet 5 → Opus 5 | medium/high | Sonnet 5 дешевле; эскалация если качество не держится |
| Сложная миграция/рефактор фронтенда | Opus 5 | high → xhigh | Opus 5 силён на long-horizon; xhigh на трудных |
| Фикс концентрационного бага | Opus 5 | xhigh | ARC-AGI-силы на нестандартных проблемах |
| Визуальная доводка / анимации | Opus 5 | high | лучшие визуальные артефакты + self-verification |
| Написание/починка Vitest/Playwright-теста | Sonnet 5 | medium | рутина, высокий объём |
| Код-ревью PR | Opus 5 x-high + recall-модель | xhigh | precision-lane, но не единственный ревьюер |
| Прототип на canvas | Pencil / Claude Design | — | ручные правки бесплатны по токенам |

**Не используйте `max` по умолчанию** — только как политику эскалации для дорогих падений (business value велика). **Не передавайте реальные ПДн.** **Пишите артефакты компактно и на английском там, где смысл не страдает.**
