# СЫРОЙ ОТЧЁТ №2 — Слой Skills/Connectors/Plugins в claude.ai, дизайн-язык финтехов РФ, миграция Jinja2 → React

> **Это исходник исследования, а не выжимка.** Публикуется дословно.
> Дата сборки: 2026-07-31. Повод — скриншоты владельца с каталогом Directory внутри claude.ai,
> который в первом заходе не был исследован вообще (изучался только маркетплейс Claude Code).
> Выжимка — `docs/research/claude_skills_and_fintech_design.md`.

---

# FINPILOT · Веха 8: методичка второго этапа исследования

> Легенда: **[Ф]** — подтверждённый факт (первоисточник/офиц. документация); **[О]** — оценка (независимые замеры/агрегация); **[Г]** — гипотеза/интерпретация. Полный список источников с URL — в конце.

## TL;DR
- **Skills в claude.ai** **[Ф]** — переносимый открытый формат (папка + `SKILL.md` с YAML-фронтматтером), работающий по принципу прогрессивного раскрытия: на старте грузятся только метаданные (~100 токенов/скилл), тело (≤5k токенов) — по триггеру, референсы — по требованию. Официальный плагин **Design** (v1.2.0, репозиторий `anthropics/knowledge-work-plugins`) содержит 7 скиллов (`accessibility-review`, `design-critique`, `design-handoff`, `design-system`, `research-synthesis` и др.) и 9 MCP-серверов — это ядро инструментария для вехи 8.
- **Эталон качества** российских финтехов сводится к воспроизводимым правилам **[Ф]**: табличные цифры (`font-variant-numeric: tabular-nums`), рубль после числа через неразрывный пробел, красный для убытка/просрочки, но **никогда только цветом** (WCAG 1.4.1 Level A = основа ГОСТ Р 52872-2019), спокойный официальный тон-оф-войс, прогнозы — диапазонами/веерными графиками, а не ложно-точными числами.
- **Миграция Jinja2 → React** должна идти по паттерну strangler fig (страница за страницей за реверс-прокси) **[Ф]**, с типизированным клиентом из OpenAPI (рекомендация — hey-api либо orval для TanStack Query + Zod) **[Г]**, проверкой контракта в CI и тестовой пирамидой Vitest + Playwright + визуальная регрессия; обязательны экранные требования 152-ФЗ (согласие по правилам с 1 сентября 2025) и уведомление о рисках при ПДН > 50%.

## Key Findings

1. **Skills — единая сущность на всех поверхностях [Ф].** Один формат `SKILL.md` работает в claude.ai (чат, Cowork), Claude Code и через Claude API. В claude.ai скиллы ставятся через Customize → Skills → «Browse skills» (единый Directory с тремя вкладками Skills/Connectors/Plugins). Требуется включённая возможность «Code execution and file creation».
2. **Прогрессивное раскрытие ≠ нулевой расход [Ф].** По документации: метаданные ~100 токенов/скилл, тело ≤5k, референсы — по требованию. НО есть подтверждённый баг Claude Code (issue #14882): скиллы грузят полный объём тела при старте, а не только фронтматтер — при множестве плагинов «50k+ tokens before any conversation starts». Риск для Project knowledge.
3. **Плагин Design — главный инструмент вехи 8 [Ф]:** 7 скиллов, 9 MCP (Figma, Slack, Linear, Asana, Atlassian и др.), Apache-2.0, последний коммит 23 апреля 2026.
4. **Российские финтехи дают открытые дизайн-системы [Ф]:** Т-Банк — Taiga UI (Angular, open source), Sber — Nova + супергарнитура SB (50 начертаний), Альфа-Банк — открытая дизайн-система (mobile-first). Все три публикуют статьи на Хабре.
5. **152-ФЗ ужесточён с 1 сентября 2025 [Ф]:** согласие должно быть «конкретным, предметным, информированным, сознательным и однозначным»; штрафы за нарушение — от 300 до 700 тыс. руб. за первое нарушение и от 1 до 1,5 млн руб. за повторное (ст. 13.11 КоАП РФ, ред. с 30.05.2025).
6. **ПДН [Ф]:** с 1 января 2024 (601-ФЗ) кредитор обязан письменно уведомлять заёмщика о рисках, если рассчитанное значение ПДН превышает 50%.

## Details

### НАПРАВЛЕНИЕ 1 — Слой Skills / Connectors / Plugins в claude.ai

#### 1.1. Что такое Agent Skills [Ф]
Skills — «lightweight, open format for extending AI agent capabilities». Ядро — папка с файлом `SKILL.md` (обязательный YAML-фронтматтер: `name` + `description`; опционально `scripts/`, `references/`, `assets/`, `evals/`). Anthropic называет их взаимозаменяемо «Agent Skills» или «Skills».

Структура:
```
my-skill/
├── SKILL.md      # обязательно: метаданные + инструкции
├── scripts/      # опционально: исполняемый код (Python/JS/Bash)
├── references/   # опционально: доп. документация
├── assets/       # опционально: шаблоны, ресурсы
└── evals/        # рекомендуется: тесты
```

**Прогрессивное раскрытие (3 уровня):**

| Уровень | Что грузится | Когда | Токены |
|---|---|---|---|
| 1. Метаданные | name + description | всегда, на старте | ~100/скилл (иногда ~60) |
| 2. Тело SKILL.md | полные инструкции | по триггеру | ≤5 000 |
| 3. Референсы | скрипты, данные, шаблоны | по требованию | практически без лимита |

Экономия: проект с 8 скиллами занимает ~500 токенов на старте вместо ~70 000 (оценка Dotzlaw) **[О]**.

**Важное предупреждение [Ф]:** GitHub issue #14882 в `anthropics/claude-code` — скиллы в Claude Code показывают полный объём тела в `/context` при старте (например, «Skill Development: 5.5k tokens»), а не только фронтматтер. При множестве плагинов — «50k+ tokens before any conversation starts». Для claude.ai официально заявлено прогрессивное раскрытие, но за расходом контекста в Проекте надо следить эмпирически.

**Лимиты [Ф]:** спецификация Agent Skills допускает `description` до 1024 символов, но **claude.ai ограничивает 200 символами**; `name` — до 64 символов, строчные буквы/цифры/дефисы, должен совпадать с именем папки; SKILL.md рекомендуется держать <500 строк.

**Где работают [Ф]:** чат (веб и вкладка Chat в Desktop), Cowork, Claude API, Claude Code. В Claude Design — отдельная поверхность Anthropic Labs (текст → прототип). Функция «Record a skill» (июль 2026) записывает экран/клики/голос и превращает в скилл.

#### 1.2. Разбор официальных скиллов Anthropic

| Скилл | Что делает [Ф] | Польза для FINPILOT |
|---|---|---|
| **canvas-design** | Статичная визуальная графика (.png/.pdf), «философия → выражение», 90% визуал/10% текст | Маркетинговые материалы, не UI |
| **web-artifacts-builder** | React 18 + TS + Tailwind + shadcn/ui, 40+ компонентов Radix/shadcn, `init-artifact.sh`, `bundle-artifact.sh`, Parcel | **Прямо релевантен** — прототипирование React-компонентов на том же стеке |
| **frontend-design** | Продакшн-UI против «AI slop»: жирная типографика, доминирующий цвет 60–70%, запрещены Inter/дефолт-градиенты | Эталон борьбы с шаблонностью |
| **mcp-builder** | Создание MCP-серверов, 4 фазы (research → implementation → review → 10 eval-вопросов), TypeScript | Если понадобится свой connector к бэкенду FINPILOT |
| **theme-factory** | 10 готовых тем (Ocean Depths, Modern Minimalist, Tech Innovation…), палитра + пары шрифтов | Быстрый старт цветовых токенов |
| **brand-guidelines** | Бренд Anthropic: Dark #141413, Light #faf9f5, Orange #d97757, Blue #6a9bcc, Green #788c5d; шрифты Poppins (заголовки), Lora (текст) | Референс: форкнуть, вписать бренд FINPILOT |
| **learn** | Обучающий режим | Онбординг |
| **skill-creator** | Каркас новых скиллов + eval-тесты, `run_loop.py` (оптимизация description на 20 запросах) | Создание собственных скиллов FINPILOT |
| **doc-coauthoring** | 3 фазы: gather → refine → reader test | Документация проекта |
| **internal-comms** | 3P-апдейты, статусы, инциденты | Отчётность |
| **webapp-testing** | Playwright: тест локальных веб-приложений, «reconnaissance-then-action», ждать `networkidle` | **Прямо релевантен** — E2E-тесты вехи 8 |
| **xlsx / docx / pptx / pdf** | Документные скиллы (source-available). Для xlsx: формулы вместо значений, цветокод финмоделей (синий=ввод, чёрный=формула, зелёный=внутр. ссылка, красный=внешняя) | Экспорт финотчётов |

Числа установок из задачи (canvas-design ~1.7 млн и т.д.) — данные Directory claude.ai; в открытых зеркалах маркетплейса Claude Code фигурируют другие цифры (например, 160.6k у скиллов knowledge-work). Помечаю как **оценку [О]** — точные счётчики видны только в самом Directory.

#### 1.3. Официальный плагин Design [Ф]
Репозиторий **`anthropics/knowledge-work-plugins`**, плагин `design`, версия 1.2.0, Apache-2.0, последний коммит 23 апреля 2026. Описание: «Accelerate design workflows from research to handoff: run accessibility audits, critique designs, manage design systems, write UX copy, synthesize user research, and generate handoff specs.»

**7 скиллов внутри:**
- `accessibility-review` — WCAG 2.1 AA аудит (контраст, клавиатура, размер тач-таргетов, скринридеры) перед handoff;
- `design-critique` — структурный фидбэк по usability/иерархии/консистентности (принимает Figma-ссылку/скриншот);
- `design-handoff` — спека для разработки: layout, дизайн-токены, пропсы компонентов, состояния, брейкпоинты, edge-cases, анимации;
- `design-system` — аудит/документирование/расширение дизайн-системы (ищет несогласованность имён, хардкод-значения);
- `research-synthesis` — синтез пользовательских исследований;
- +2 (UX writing и др.).

**9 MCP-серверов:** Slack, Figma, Linear, Asana, Atlassian, Notion, Jira и др. Safety-сигнал: «External network access».

**Отличие от `frontend-design` [Г]:** `frontend-design` — отдельный скилл/плагин для Claude Code, ориентированный на генерацию продакшн-кода UI и борьбу с «AI slop». Плагин `Design` — это дизайн-**процесс** (критика, аудит, handoff, research), а не генератор кода. Для вехи 8 они комплементарны: Design для аудита/критики/handoff, `frontend-design`/`web-artifacts-builder` — для генерации React-кода.

**Другие плагины Anthropic [Ф]:** Engineering (снижение рутины/документация), Productivity (у Василия установлен), Data, Product-management (v1.2.0 — фичи-спеки, роадмапы, синтез research), Legal. Для разработки применимы Engineering и Product-management.

#### 1.4. Connectors в claude.ai [Ф]
Connectors = «плумбинг»: доступ Claude к внешним приложениям/данным поверх MCP. Каталог — 841 MCP-интеграция (данные awesome-claude-connectors, **оценка [О]**). Remote-коннекторы (remote MCP over HTTPS) работают на всех поверхностях; desktop-расширения (локальный MCP) — только Claude Desktop и Claude Code, не на вебе/мобиле.

- **Filesystem** (`@modelcontextprotocol/server-filesystem`): чтение/запись локальных файлов; требует Claude for Desktop + Node.js; риск — data exfiltration через prompt injection (PromptArmor). Мобильные ОС слишком закрыты для локального файлового доступа.
- **Control Chrome** — автоматизация браузера, вкладки, скрейпинг.
- **pdf-viewer**, **PowerPoint by Anthropic**, **Word by Anthropic**.
- **Apify** — веб-скрейпинг.
- **Desktop Commander** — файловые/процессные операции, требует Desktop.
- **Windows-MCP** — управление Windows (у Василия Intel Mac — неприменимо).

Риск безопасности [Ф]: «a malicious Skill can direct Claude to invoke tools or execute code in ways that don't match the Skill's stated purpose» → возможна эксфильтрация данных. Использовать только доверенные скиллы/коннекторы, аудировать SKILL.md, скрипты и внешние зависимости. Расход токенов: MCP-инструменты грузят описания заранее (в отличие от скиллов) — это и есть аргумент «скиллы экономнее MCP».

#### 1.5. Создание собственного скилла для claude.ai — пошагово [Ф]
1. Включить Settings → Capabilities → «Code execution and file creation».
2. Создать папку `my-skill/` с `SKILL.md` (YAML: `name` ≤64 симв. = имени папки; `description` ≤200 симв. для claude.ai).
3. Тело <500 строк; детали — в `references/`, скрипты — в `scripts/` (зависимости объявить: `dependencies: python>=3.8, pandas>=1.5.0`).
4. Заархивировать в ZIP так, чтобы **папка скилла была корнем архива** (не файлы россыпью, не обёртка-подпапка).
5. Customize → Skills → «+» → «Create skill» → загрузить ZIP → включить тумблер → протестировать промптом.
6. Итерация: в чате открыть файлы скилла сбоку, выделить текст → «Edit with Claude».

**Ограничения [Ф]:** загруженные скиллы приватны для аккаунта (если не Team/Enterprise с provisioning). Скиллы из Directory — view-only (нельзя редактировать, только скачать копию). Версионирование — вручную (свой git/ZIP); внутри Проекта скиллы доступны, если включены в Customize.

#### 1.6. Взаимодействие с Project knowledge [Г]
Скиллы и Project knowledge конкурируют за контекстное окно. Скиллы спроектированы экономными (прогрессивное раскрытие), но при баге полной загрузки тел (#14882) множество включённых скиллов/плагинов съедают десятки тысяч токенов до начала работы, что уменьшает бюджет под Project knowledge и может влиять на порог включения RAG. **Рекомендация:** держать включёнными только релевантные вехе 8 скиллы, остальные выключать тумблером.

### НАПРАВЛЕНИЕ 2 — Дизайн-язык российских финтехов

#### 2.1. Дизайн-системы [Ф]
- **Т-Банк (Тинькофф) — Taiga UI**: большая open-source библиотека компонентов на Angular, разрабатывалась внутри несколько лет до публичного релиза, есть локализация (12+ языков силами сообщества), контракт CSS-переменных, компонент `Sensitive` (скрывает баланс при записи экрана). Экосистема: Maskito (маскирование полей, >300 тыс. загрузок npm, применяется и в других банках РФ).
- **Сбер — дизайн-система Nova / SBER Design**: супергарнитура SB (50 начертаний, сделана Paratype), обширная палитра для светлой/тёмной темы, 200+ команд, 75 млн клиентов. Platform V UI Kit (СберТех) — двухуровневая система токенов (референсный + системный уровни, семантические токены).
- **Альфа-Банк**: открытая дизайн-система, mobile-first, «делать как можно больше элементов в коде, всё тестировать, добавлять в библиотеку только проверенные элементы». Активные публикации на Хабре про Discovery-этап и тёмные стороны дизайн-систем.

#### 2.2. Подача финансовых данных [Ф]
- **Табличные (моноширинные) цифры**: `font-variant-numeric: tabular-nums` (OpenType `tnum`) — цифры одинаковой ширины, выравниваются по разрядам в колонках. MDN: «tabular-nums включает цифры одинаковой ширины». Doka.guide: три сценария — «финансы, таймеры, таблицы». Контраст с `proportional-nums` (pnum, дефолт), который ломает выравнивание.
- **Формат рубля** (Ководство Артемия Лебедева, § 116, verbatim): «Знак рубля всегда должен стоять через пробел после числа»; лучший вариант сокращения — «руб.». Десятичный разделитель — запятая; разделитель разрядов — неразрывный (желательно тонкий) пробел, не запятая. Пример: `1 234,56 ₽`. Символ ₽ = U+20BD (Unicode 7.0, 16 июня 2014). Тонкий пробел U+2009, неразрывный U+00A0, узкий неразрывный U+202F. Доллар — наоборот, перед числом без пробела.
- **Отрицательные значения**: красный — ожидаемая конвенция для убытка в РФ-финтехе (подтверждено фидбэком пользователей T-Bank Invest, требовавших заменить нестандартный фиолетовый на красный). Но — см. accessibility ниже.

#### 2.3. Тревожные/негативные данные без паники [Ф]
- **WCAG 1.4.1 «Use of Color» (Level A)** = базовое обязательное требование, положено в основу ГОСТ Р 52872-2019: «Color is not used as the only visual means of conveying information». Масштаб: National Eye Institute (цит. Section508.gov) — «Approximately 1 in 12 men and approximately 1 in 200 women experience color blindness». Практика: цвет + второй индикатор (иконка, знак −, метка, рамка, паттерн). QA: проверять UI в grayscale и симуляторе дальтонизма (Stark, Coblis).
- **Nielsen Norman Group (Error-Message Guidelines, 14 мая 2023)**: «never use exclusively color or animation to indicate errors»; «Design errors based on their impact» — сильный красный + модаль резервировать для настоящих блокеров, для мягких/информационных негативов — нейтральный стиль (пример Kohl's «without conventional red formatting»). Преждевременные ошибки — «hostile pattern».
- **Тон-оф-войс**: официальный регистр, «вы», спокойно, точно, без обесценивания долга. T-Bank прямо даёт анти-пример неформального обращения о просрочке; Sber — «заботливая, спокойная, экспертная» тональность; Альфа-Банк — «ощущение надёжности и стабильности».

#### 2.4. Прогнозы и неопределённость [Ф]
- **Не показывать ложно-точное одиночное число** — показывать диапазон, расширяющийся с горизонтом. Использовать **prediction intervals** (не confidence intervals). Роб Хайндман (robjhyndman.com/hyndsight/intervals): «confidence intervals for the mean are much narrower than prediction intervals ... Instead of the interval containing 95% of the probability space for the future observation, it contained only about 20%»; для узких PI — «nominal 95% intervals may only provide coverage between 71% and 87%».
- **Веерные графики (fan charts)** — эталон Банка Англии. Britton, Fisher & Whitley (BoE Quarterly Bulletin 1998): «Since February 1996, the Bank's inflation forecast has been published ... in what is now known as 'the fan chart'», цель — «without suggesting a degree of precision that would be spurious». Эмпирика (BoE Staff Working Paper 2026 «Anchors aweigh?»): «fan charts are well understood and perform best at jointly conveying both expectations and uncertainty», публика систематически недооценивает неопределённость, веер это исправляет.
- **Реализация [Г]**: сплошная историческая линия → пунктир/затенённая проекционная полоса; вложенные полосы 80% и 95% через прозрачность; множители: 80%→1.28, 90%→1.64, 95%→1.96 (ŷ ± c·σ̂). В visx/Recharts — стек полупрозрачных area-полос вокруг центральной линии, расширяющихся к горизонту.

#### 2.5. Регуляторные требования к интерфейсу [Ф]
- **152-ФЗ (ред. с 1 сентября 2025)**: согласие «конкретное, предметное, информированное, сознательное и однозначное» (ч. 1 ст. 9); объём ПДн соответствует целям (ч. 2 ст. 5, минимизация); согласие на распространение — по требованиям Роскомнадзора (Приказ № 18 от 24.02.2021). Штрафы (ст. 13.11 КоАП РФ, ред. с 30.05.2025, ФЗ от 30.11.2024 № 420-ФЗ): от 300 до 700 тыс. руб. за первое нарушение и от 1 до 1,5 млн руб. за повторное; за неуведомление РКН — до 300 тыс. руб. (ч. 10 ст. 13.11); за утечку — оборотные штрафы. Практика: отдельный несовмещённый чекбокс согласия (не пред-отмеченный), ссылка на политику, цель обработки на экране.
- **ПДН**: Банк России (cbr.ru/finstab/instruments/pti): «1 января 2024 года вступил в силу Федеральный закон от 29.12.2022 № 601-ФЗ ... закрепивший ... обязанность ... уведомлять заемщика в письменной форме о существующих рисках в случае, если рассчитанное значение ПДН превышает 50%». Расчёт по Указанию Банка России от 16.10.2023 № 6579-У. Для FINPILOT: если ПДН пользователя > 50% — на экране обязателен спокойный дисклеймер о рисках.
- **Реклама финуслуг**: ограничения по 38-ФЗ «О рекламе» (полная стоимость, отсутствие вводящих в заблуждение обещаний доходности).
- **Доступность**: ГОСТ Р 52872-2019 (базируется на WCAG 2.1), распространяется на приложения и пользовательские интерфейсы.

### НАПРАВЛЕНИЕ 3 — Миграция серверного рендеринга на SPA

#### 3.1. Стратегия strangler fig [Ф + Г]
Инкрементально, страница за страницей, оба фронтенда живут параллельно за маршрутизирующим прокси/фасадом. Прокси решает, какой запрос отдать старому Jinja2, а какой — новому React. Каждая мигрированная страница уходит в прод независимо → снижение риска, ранний фидбэк. Ключевые ошибки: игнорировать прокси-слой (спагетти-интеграция), пытаться «big bang».

Для FINPILOT (FastAPI жив) **[Г]**:
- FastAPI отдаёт и Jinja2-шаблоны (легаси), и статику собранного Vite-бандла; постранично переключать роуты на React.
- Сессии/куки: сохранить единый механизм аутентификации; React ходит в тот же FastAPI, куки HttpOnly, SameSite.
- CSRF: при переходе на SPA + токены настроить CSRF-защиту для мутирующих запросов; TanStack Query отправляет заголовки.
- Статика: Vite-манифест, хешированные ассеты, отдельный префикс, чтобы не конфликтовать со старой статикой.

#### 3.2. Типизированный клиент из OpenAPI (2026) [Ф]

| Инструмент | Что даёт | Runtime-валидация | Для FINPILOT |
|---|---|---|---|
| **openapi-typescript + openapi-fetch** | Только типы + лёгкий (2 КБ) fetch-обёртка, zero-runtime | Нет (доверяет типам) | Минимализм; нет проверки payload |
| **hey-api (@hey-api/openapi-ts)** | SDK + Zod-схемы + TanStack Query хуки, 20+ плагинов; используют Vercel, PayPal | Да (через Zod) | **Рекомендация** — по отзывам «by far superior», есть runtime-валидация |
| **orval** | Хуки TanStack Query + Zod + MSW-моки; сплит по тегам | Да | Хорош, если нужны MSW-моки; генерирует много файлов |
| **Kubb** | Плагинный, SDK для всех API | Да | Альтернатива |

Интеграция: FastAPI автогенерирует OpenAPI → codegen → типы + Zod + `useQuery`/`useMutation` хуки. **Проверка контракта в CI**: сохранять эталонный `openapi.json`, в CI генерировать заново и `diff` — при расхождении фейлить сборку (ловит рассинхрон бэкенд/фронтенд заранее). Zod даёт runtime-валидацию ответов — критично для финансовых данных.

#### 3.3. Тестовая пирамида фронтенда финтеха [Г]
- **Vitest + Testing Library** — юниты компонентов/хуков/утилит форматирования денег (основание пирамиды).
- **Playwright** — E2E критических флоу (вход, согласие 152-ФЗ, ключевые финансовые сценарии); скилл `webapp-testing` помогает.
- **Визуальная регрессия** — Playwright screenshots или Storybook + Chromatic для дизайн-системы (ловит регрессии таблиц/графиков).
- **Гейты в CI**: типы (tsc), lint, contract-diff, покрытие. Существующее требование бэкенда 90% покрытия — на фронтенде разумно держать высокое покрытие на бизнес-логике (форматирование, расчёты, Zod-схемы), но не гнаться за 90% на верстке; критические пути закрывать E2E.

#### 3.4. Типовые ошибки миграции [Г]
- Потеря SEO/доступности при переходе на CSR (для внутреннего кабинета менее критично).
- Рассинхрон контракта API → ловить contract-diff в CI + Zod.
- Дубли состояния (сервер vs клиент) → TanStack Query как единый слой серверного состояния.
- Регрессии форматирования чисел/валюты → юнит-тесты на форматтеры + tabular-nums.
- Потеря CSRF/сессии при смене архитектуры аутентификации.
- «AI slop» единообразие → использовать frontend-design принципы.

### НАПРАВЛЕНИЕ 4 — Экосистема Claude (июль 2026) и советы

#### 4.1. Свежие изменения [Ф]
- **23 июля 2026**: релиз Claude Opus 5 (топ-модель для сложных reasoning/coding).
- Chat и Cowork объединены в один вид (тумблер сверху).
- **«Record a skill»** — запись экрана/кликов/голоса → скилл.
- Cowork доступен на вебе и мобиле (июль 2026), remote-исполнение в облачных песочницах по умолчанию, scheduled tasks server-side.
- Единый Directory (Skills/Connectors/Plugins) с 31 марта 2026.
- **Claude Design** (Anthropic Labs, 17 апреля 2026): текст/Figma/кодовая база → рабочий прототип/дизайн-система/лендинг; интеграция с Claude Code.
- Analytics API: скиллы отдают свой usage/cost, новые эндпоинты по adoption плагинов и созданию артефактов.
- Риск токенов Cowork **[Ф]**: одна задача = много обычных чатов; Pro-лимиты тратятся быстро (у Василия 4 аккаунта Pro — планировать нагрузку).

#### 4.2. Что сказал бы независимый эксперт разработчику-одиночке [Г]
1. **Не переписывать всё сразу.** Strangler fig, начать с одной некритичной страницы, доказать пайплайн (codegen → тесты → визрегрессия), потом масштабировать.
2. **Контракт — единственный источник правды.** OpenAPI → типы + Zod, contract-diff в CI. Это защищает соло-разработчика от тихих регрессий сильнее любого код-ревью.
3. **Дизайн-систему — сначала токены.** theme-factory/brand-guidelines как старт, потом Radix/shadcn. Табличные цифры и форматтеры денег — с первого дня.
4. **Compliance — не в конце.** Экран согласия 152-ФЗ и дисклеймер ПДН>50% заложить в дизайн-систему как переиспользуемые компоненты сразу.
5. **Скиллы под контролем контекста.** Включать только нужные (Design, web-artifacts-builder, webapp-testing), остальные выключать — беречь бюджет Project knowledge.
6. **Дедлайн осень 2026 — резать скоуп, не качество.** Приоритет — критические финансовые флоу с полным тестовым покрытием и accessibility; второстепенные экраны можно оставить на Jinja2 до следующей вехи.

## Recommendations

**Этап 0 (сейчас, 1–2 недели):**
- Включить и оставить включёнными только: плагин **Design**, скиллы **web-artifacts-builder**, **webapp-testing**, **theme-factory**; проверить `/context`, выключить лишнее.
- Настроить codegen: попробовать **hey-api** (SDK + Zod + TanStack Query) на текущем FastAPI OpenAPI; сохранить эталонный `openapi.json`.
- Заложить форматтеры денег (comma-decimal, NBSP-разряды, ₽ после числа через узкий неразрывный пробел) + `font-variant-numeric: tabular-nums` в дизайн-токены.

**Этап 1 (миграция, итеративно):**
- Reverse-proxy маршрутизация: одна пилотная страница на React, остальное — Jinja2.
- CI-гейты: tsc, contract-diff (fail при расхождении), Vitest coverage на бизнес-логике, Playwright на критических флоу, визрегрессия дизайн-системы.
- Компоненты 152-ФЗ (несовмещённый чекбокс согласия) и ПДН-дисклеймер (>50%) — как переиспользуемые.

**Этап 2 (качество финтеха):**
- Веерные графики прогнозов (visx/Recharts, вложенные полосы 80/95%, расширение к горизонту), никакого ложно-точного числа.
- Негативные данные: красный + иконка/знак (никогда только цвет), спокойный официальный тон; QA в grayscale + Stark.
- `accessibility-review` скиллом перед каждым handoff; цель — WCAG 2.1 AA / ГОСТ Р 52872-2019.

**Пороги, меняющие план:**
- Если `/context` показывает >30–40k токенов на скиллах в Проекте → выключить часть, вынести знания в Project knowledge.
- Если contract-diff падает часто → зафиксировать версионирование API.
- Если E2E на критических флоу нестабильны → не выпускать страницу в прод (гейт).

## Caveats
- **Числа установок скиллов** (canvas-design ~1.7 млн и т.д.) — из Directory claude.ai; в открытых зеркалах цифры иные **[О]**. Точные счётчики видны только в самом интерфейсе.
- **Прогрессивное раскрытие**: для claude.ai официально заявлено, но баг #14882 (Claude Code) показывает полную загрузку тел — поведение в Проектах claude.ai стоит проверить эмпирически через `/context`.
- **Дизайн-системы Сбера/Альфа** частично закрыты/меняются; ссылки — на открытые части и статьи Хабра.
- Часть источников по ToV и codegen — блоги/vendor, не академия; отмечена конвергенция мнений.
- BoE Staff Working Paper 2026 и материалы 2026 года — свежие; перед цитированием в проде проверить финальные формулировки.
- Штрафы 152-ФЗ и КоАП приводятся по вторичным разборам (Гарант, Контур, data-sec.ru, БУХ.1С) — перед юридически значимым применением сверить с актуальной редакцией КоАП РФ.

## Источники (URL для архива проекта)

**Направление 1 — Skills / Connectors / Plugins**
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- https://claude.com/docs/skills/how-to
- https://support.claude.com/en/articles/12512180-use-skills-in-claude
- https://support.claude.com/en/articles/12512198-how-to-create-custom-skills
- https://support.claude.com/en/articles/14328846-browse-skills-connectors-and-plugins-in-one-directory
- https://support.claude.com/en/articles/11725091-when-to-use-desktop-and-web-connectors
- https://support.claude.com/en/articles/11176164-use-connectors-to-extend-claude-s-capabilities
- https://github.com/anthropics/skills
- https://github.com/anthropics/skills/blob/main/skills/brand-guidelines/SKILL.md
- https://github.com/anthropics/skills/blob/main/skills/canvas-design/SKILL.md
- https://agentskills.io/home
- https://www.claudepluginhub.com/plugins/anthropics-design-design
- https://claude.com/plugins/design
- https://claude-world.com/articles/anthropic-official-skills-complete-guide/
- https://github.com/anthropics/claude-code/issues/14882
- https://towardsdatascience.com/claude-skills-and-subagents-escaping-the-prompt-engineering-hamster-wheel/
- https://dotzlaw.com/insights/claude-skills/
- https://beginnersinai.org/claude-skills-connectors-plugins/
- https://github.com/rdmgator12/awesome-claude-connectors
- https://www.promptarmor.com/connectors/filesystem
- https://mcpservers.org/agent-skills/anthropic/theme-factory
- https://www.analyticsvidhya.com/blog/2026/07/how-to-create-custom-skills-in-claude/

**Направление 4 — экосистема Claude июль 2026**
- https://go9x.com/blog/claude-updates
- https://releasebot.io/updates/anthropic/claude
- https://claudecowork.im/plugins
- https://suprmind.ai/hub/claude/features/
- https://amitray.com/claude-total-ecosystem-chat-code-cowork-design-skills-connectors-plugins/

**Направление 2 — дизайн российских финтехов**
- https://habr.com/ru/company/tinkoff/blog/536866/
- https://habr.com/ru/companies/tbank/articles/782924/
- https://www.tbank.ru/career/technologies/taiga-ui/
- https://www.sberbank.ru/promo/nova/
- https://info.paratype.ru/sber-type-system/
- https://habr.com/ru/companies/sberbank/articles/895306/
- https://habr.com/ru/companies/alfa/articles/841332/
- https://habr.com/ru/companies/alfa/articles/492010/
- https://habr.com/ru/company/ruvds/blog/478324/
- https://habr.com/ru/post/312422/
- https://awdee.ru/complex-tables-design/
- https://www.artlebedev.ru/kovodstvo/sections/116/
- https://developer.mozilla.org/ru/docs/Web/CSS/Reference/Properties/font-variant-numeric
- https://doka.guide/css/font-variant-numeric/
- https://ru.wikipedia.org/wiki/Символ_российского_рубля
- https://www.boia.org/wcag2/cp/1.4.1
- https://www.section508.gov
- https://www.nngroup.com/articles/error-message-guidelines/
- https://robjhyndman.com/hyndsight/intervals/
- https://www.bankofengland.co.uk/quarterly-bulletin/1998
- https://www.bankofengland.co.uk/working-paper/2026/anchors-aweigh-the-effect-of-communicating-forecast-uncertainty
- https://guyabel.github.io/fanplot/articles/02_boe.html
- https://feedback.tinkoff.ru/mobile_invest/topic/8387
- https://secrets.tbank.ru/glossarij/chto-takoe-tov-brenda/
- https://sberbusiness.live/publications/chto-takoe-tone-of-voice-i-zachem-on-nuzhen-biznesu

**Регуляторика**
- https://normativ.kontur.ru/document?moduleId=1&documentId=501173
- https://www.garant.ru/article/1862510/
- https://kontur.ru/articles/1577
- https://cbr.ru/finstab/instruments/pti/
- http://www.cbr.ru/explan/dfs_pdnz/dfs_pdnz_6579-u/
- https://base.garant.ru/73664694/
- https://simai-portal-iblock.storage.yandexcloud.net/iblock/8a9/8a966994dcf1bf710812b13b672e29a0/gost-52872-2019.pdf

**Направление 3 — миграция и codegen**
- https://dev.to/nyaomaru/which-openapi-codegen-should-you-choose-openapi-typescript-vs-hey-api-vs-orval-vs-kubb-100p
- https://saschb2b.com/blog/typesafe-api-codegen-2026
- https://heyapi.dev/docs/openapi/typescript/plugins/tanstack-query
- https://orval.dev/
- https://tanstack.com/query/latest/docs/framework/react/community/community-projects
- https://oneuptime.com/blog/post/2026-01-30-strangler-fig-pattern/view
- https://www.leanderhoedt.dev/blog/strangler-fig
