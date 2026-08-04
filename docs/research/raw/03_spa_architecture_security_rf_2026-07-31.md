# СЫРОЙ ОТЧЁТ №3 — Архитектура React SPA, безопасность, деплой в РФ, доменные паттерны

> **Это исходник исследования, а не выжимка.** Публикуется дословно.
> Дата сборки: 2026-07-31. Выжимка — `docs/research/frontend_architecture_and_security.md`.

---

# FINPILOT — Веха 8: методичка по фронтенду (этап 3, финальный)

**Даты и версии актуальны на 31 июля 2026. Метки уверенности: [ФАКТ] — подтверждено первоисточником; [ОЦЕНКА] — вывод из нескольких источников; [ГИПОТЕЗА] — экстраполяция. Полный список источников с URL — в конце (для архива проекта).**

## TL;DR
- **Стек под FINPILOT:** Vite + React 19 (React Compiler on) + TypeScript, TanStack Router + TanStack Query, Zustand для клиентского состояния, Recharts как база графиков + visx/ECharts точечно, KaTeX для формул, MSW v2 + Vitest + Playwright + Argos для тестов. Токены — httpOnly-refresh + in-memory access, строгий CSP на nonce, статика и бэкенд — на российском облаке (Yandex/Selectel/Timeweb) в РФ-регионе.
- **Ключевые риски:** срыв срока из-за недооценки (закладывай ×1.5–2), цепочка поставок npm (Shai-Hulud), CSP-конфликты с inline-стилями Radix, доступность npm-реестра из РФ. Все управляемы при дисциплине.
- **Бюджеты качества к запуску:** LCP < 2.5 c, INP < 200 мс, CLS < 0.1 (p75 реальных пользователей); initial JS дашборда — цель ≤ 250 КБ gzip.

## Key Findings

### Core Web Vitals 2026 [ФАКТ]
Пороги «good» на p75 реальных пользователей (CrUX, окно 28 дней): **LCP < 2.5 c, INP < 200 мс, CLS < 0.1**. INP заменил FID как метрику отзывчивости в марте 2024 (web.dev / Google Search Central) — любой гайд, всё ещё упоминающий FID, устарел. INP — самая часто проваливаемая метрика: **43% сайтов проваливают порог INP 200 мс** (DigitalApplied, 2026: «43% of sites still fail the 200ms INP threshold, making it the most commonly failed Core Web Vital in 2026»); по данным CrUX за май 2026 все три метрики одновременно проходят лишь около 55,9% origin'ов. Рекомендация ставить алерты на 80% порога: **INP > 160 мс, LCP > 2.0 c, CLS > 0.08**.

### Состояние (state management) [ФАКТ/ОЦЕНКА]
Разделение обязательно: **серверное состояние — TanStack Query, клиентское — Zustand**, URL-состояние — роутер. Размеры бандла (gzip, снимок bundlephobia май 2026): Zustand ~1.1 КБ, Jotai ~3.5 КБ, Redux Toolkit ~11–13.8 КБ. Zustand втрое нарастил загрузки за год (с 26.7M до ~72.9M/мес по данным npm API). Бенчмарк (dev.to, 4× CPU slowdown): initial parse time Zustand 8 мс, Jotai 9 мс, Redux Toolkit 34 мс; память на 1000 подписанных компонентов — Zustand 2.1 МБ, Jotai 1.8 МБ, RTK 3.2 МБ. **Для FINPILOT:** Zustand для UI-состояния (модалки, шаги мастера, тема), Jotai только если появится spreadsheet-подобное дерево зависимостей.

### Роутинг [ОЦЕНКА]
**TanStack Router** для client-heavy дашборда с типобезопасными search-params (валидация через Zod на этапе компиляции), бесшовная интеграция с TanStack Query (один кэш, одни devtools). React Router v7 — безопаснее для SSR/контент-сайтов и миграций с Remix, но полноценная типобезопасность только в framework mode (в SPA-режиме нужен ручной каст). Вывод для FINPILOT (SPA, один разработчик, аналитический дашборд): **TanStack Router** — типобезопасность окупается уже после ~30 маршрутов.

### Графики [ФАКТ]
Размеры (gzip): @visx/xychart ~49 КБ (или ~15 КБ при минимальной сборке отдельных примитивов), Lightweight Charts ~60 КБ, Chart.js core ~92 КБ, Nivo ~143 КБ, ApexCharts ~164 КБ, ECharts ~100–359 КБ (tree-shakeable до ~100 КБ при импорте нужных типов). Recharts — самый скачиваемый React-график (48.9M/нед), на нём базируется shadcn/ui charts. **Рекомендация FINPILOT:** Recharts как основа (стек-бары для SAW-распределения, линии сценариев), visx для веерного графика Монте-Карло с доверительным интервалом (полный контроль над band-областью), ECharts точечно для Санкея (денежный поток) и больших рядов (>10k точек, Canvas). Lightweight Charts не нужен (нет свечей). Лицензии: Recharts/visx/Chart.js — MIT, ECharts/Lightweight Charts — Apache-2.0.

### Виртуализация [ФАКТ]
@tanstack/react-virtual — headless, официально рекомендуемая связка с TanStack Table (виртуализация НЕ встроена в Table). react-virtuoso — богатый API из коробки (динамические высоты, sticky-заголовки, группы, infinite scroll). react-window — лёгкий, но фиксированные высоты и почти без активной разработки. **Для FINPILOT:** TanStack Table уже в стеке → TanStack Virtual. Порог включения — примерно от 100+ строк в DOM; нужна для длинных списков транзакций и графика погашения по месяцам, а не для 66 альтернатив.

### Формулы [ФАКТ]
**KaTeX** — синхронный рендер без reflow, self-contained (без зависимостей, легко бандлится), серверный/build-time пререндер через `katex.renderToString`. Полный вес ~347,5 КБ (JS + шрифты), но рендерится быстрее MathJax. MathJax 3 — шире покрытие LaTeX, лучше a11y (MathML, речь, брайль), но тяжелее (полный бандл ~5 МБ). Последний релиз KaTeX — v0.16.22 (апрель 2025). **Для FINPILOT:** KaTeX с server-side/build-time пререндером формул модели → браузер получает готовый HTML, не тянет JS ради статичных формул.

### React Compiler [ФАКТ]
**React Compiler v1.0 stable вышел 7 октября 2025** (react.dev, авторы Lauren Tan, Joe Savona, Mofei Zhang; анонс на React Conf 2025). С середины 2026 включён по умолчанию в свежих шаблонах Vite (vite-plugin-react), Next.js 16, Expo SDK 54+. Мемоизирует на уровне выражений (точнее ручной), поддерживает React 17+ через `react-compiler-runtime` shim. Meta: 60–70% проблем производительности — от отсутствующей/неверной мемоизации; внутренние бенчмарки — сокращение лишних ре-рендеров на 20–40%. Ручные useMemo/useCallback ещё нужны для сторонних библиотек (конфиги графиков), внешних стора без useSyncExternalStore, тяжёлых вычислений. **Вывод:** включить компилятор, ручную мемоизацию оставить только вокруг Recharts/visx-конфигов и Монте-Карло расчётов. Компилятор не заменяет useTransition/useDeferredValue.

### Безопасность [ФАКТ]
- **Токены:** access-токен (типично 15 мин) — только in-memory (переменная модуля auth-сервиса / React state), refresh-токен (7–30 дней) — httpOnly + Secure + SameSite cookie, ротация при каждом обновлении. Best practice стабилен с ~2020 (OWASP, Auth0, IETF OAuth WG). Идеал для финтеха — **BFF-паттерн:** токены не попадают в браузер вовсе, сессия управляется на сервере.
- **CSP:** Radix использует inline-стили (react-remove-scroll и др.) → строгий `style-src 'self'` ломает Dialog/ScrollArea (radix issues #2057, #3063, discussion #3130). Обходы: nonce на style-теги там, где поддерживается, либо на переходный период `style-src 'unsafe-inline'` (задокументировать как техдолг). `'unsafe-eval'` — никогда в проде.
- **Цепочка поставок:** волна **Shai-Hulud** — самораспространяющийся npm-червь. **V1** (обнаружен JFrog/ReversingLabs 15–16 сентября 2025) — 187 пакетов и кража ~$50 млн в криптовалюте. **V2 «The Second Coming»** (Zscaler ThreatLabz, 24 ноября 2025): «the campaign had compromised over 700 npm packages, created more than 27,000 malicious GitHub repositories, and exposed approximately 14,000 secrets across 487 organizations» — исполнение на pre-install, персистентный бэкдор через self-hosted GitHub Actions runners, «dead man's switch» с удалением home-директории. **Mini Shai-Hulud** (Microsoft Security, 11 мая 2026) — 170+ npm и 2 PyPI пакета, первая атака одновременно по двум реестрам. Червь крадёт секреты через TruffleHog. **Защита для одиночки:** lock-файл + `--ignore-scripts`, пиннинг точных версий, npm audit, Socket.dev, provenance, задержка обновлений на несколько дней после релиза.

### 152-ФЗ и российский деплой [ФАКТ]
С 1 сентября 2025 расширены полномочия РКН/ФСТЭК/ФСБ, ужесточена локализация: первичный сбор, запись, систематизация, накопление, хранение ПДн россиян — только в базах, физически расположенных в РФ (ст. 18(5) 152-ФЗ, 242-ФЗ). Зарубежные сервисы (Google Analytics, Google Fonts CDN, Mailchimp, Notion), обрабатывающие/передающие ПДн, фактически под запретом. Штрафы за нарушение локализации — до 18 млн ₽. Cookie в связке с другими данными считаются ПДн → нужен cookie-баннер. Статика (JS/CSS без ПДн) формально не подпадает под локализацию, но для финтеха всё равно держим на РФ-инфраструктуре (устойчивость к блокировкам, отказ от внешних CDN/шрифтов, отсутствие вопросов к referrer/IP-логам).

### Российское облако/CDN (цены 2026) [ФАКТ/ОЦЕНКА]
- **Yandex Object Storage:** бесплатно каждый месяц 1 ГБ хранения + 10 000 PUT + 100 000 GET + 100 ГБ egress; далее egress ~1.68 ₽/ГБ (тир до 1 ТБ), хранение STANDARD в примере доков ~2,38 ₽/ГБ/мес (cold ~0,63 ₽/ГБ), трафик хранилище→CDN бесплатен. Yandex Cloud CDN на движке G-Core Labs; «Облако 152-ФЗ» ФСТЭК-аттестовано, УЗ-1.
- **Selectel:** S3 от ~0,81 ₽/ГБ/мес, внутренний трафик бесплатен, тройная репликация Tier III; VPS/VDS от 200 ₽/мес; НДС 22%; ФЗ-152, PCI DSS, ФСТЭК (приказы №17/№21). #1 в рейтинге CNews по облачным хранилищам 2026.
- **Timeweb Cloud:** S3 egress 100 ГБ/мес бесплатно, далее standard 1 ₽/ГБ, cold 1.5 ₽/ГБ, запросы включены в тариф; VPS от ~450 ₽/мес (минимальное пополнение 50 ₽); УЗ-1, реестр РФ ПО (№15725); есть App Platform для деплоя React из Git.
- **VK Cloud:** Hotbox/Icebox S3, УЗ-1, Tier III; точных 2026-цен подтвердить не удалось (страница не отдаётся поиском).
- **Cloud.ru/SberCloud, Cloud4Y** — тоже УЗ-1/ФСТЭК.
- **Вывод:** дешевле всего — Timeweb S3 или Selectel S3; максимум фич — Yandex Object Storage + Cloud CDN. Бэкенд с ПДн — VPS Selectel/Timeweb в РФ-регионе. Оператор ПДн (Василий/юрлицо) сам отвечает за локализацию и регистрацию в РКН — провайдер лишь даёт заключение о соответствии.

### npm из РФ [ФАКТ/ОЦЕНКА]
Зеркала: registry.npmmirror.com, GitVerse (npm-mirror.gitverse.ru), mirror.yandex.ru. Для устойчивости и защиты от Shai-Hulud — **свой прокси-реестр** (Verdaccio, Nexus Sonatype OSS, GitLab npm registry, Reposilite): кэширует зависимости, изолирует от прямых компрометаций. В Docker-сборке — прописать зеркало в `.npmrc`, кэшировать зависимости отдельными слоями.

### Тестирование [ФАКТ]
- **Визуальная регрессия:** Chromatic (Storybook-native, free 5000 снимков/мес, далее от $179/мес Starter; только Chrome стабильно, Firefox/Safari в бете), Percy (free 5000, usage-based через BrowserStack, AI Visual Review Agent с конца 2025), Argos (open-source, GitHub-native, free tier, платно от ~$30/мес), Lost Pixel/BackstopJS/reg-suit/Playwright screenshots — бесплатны/self-hosted. **Для одиночки:** Playwright screenshots + Argos (GitHub-native, дёшево, перцептивный диф) или полностью локальный Lost Pixel.
- **MSW v2:** перехват на сетевом уровне, одни хендлеры в Vitest (setupServer) и Playwright/браузере (setupWorker). Типобезопасность через generics `http.get<PathParams, RequestBody, ResponseBody>`; hey-api генерирует MSW-хендлеры и Zod-валидируемые фикстуры из OpenAPI. Обязательно `await worker.start()` (иначе гонка) и `resetHandlers()` после каждого теста.
- **Playwright:** фикстуры аутентификации через `storageState` (залогиниться один раз, переиспользовать), параллелизация по воркерам, трассировки (trace viewer) для флаки-тестов.
- **a11y:** axe-core / Playwright axe / Storybook a11y ловят ~30–40% проблем автоматически; клавиатура, фокус, скринридер, смысл alt — только вручную.

### Онбординг финтеха [ФАКТ]
**Средний drop-off онбординга финтеха — 68%** (рост с 63% в 2020 и 40% в 2016; опрос Signicat «The Battle to Onboard» среди 7600 потребителей в 14 европейских странах: «68% of consumers have abandoned a financial services application mid-onboarding»). Документ-загрузка — крупнейшая точка отказа (до 50% отказов у необанков). Прогрессивное раскрытие, честный прогресс-бар («Шаг 2 из 4», оценка времени «~4 минуты»), микрокопия «зачем эти данные / что с ними / сколько займёт» у чувствительных полей. Пользователей, попросивших перезагрузить документ, втрое чаще бросают.

### Дизайн-токены [ФАКТ]
Трёхуровневая модель: primitive (`blue-500: #3b82f6`) → semantic (`color-interactive-default: blue-500`) → component (`button-bg: color-interactive-default`). Компоненты ссылаются только на свои токены; component→semantic→primitive. Здоровая система — **<150 семантических токенов** (если разработчик ищет токен вместо того, чтобы предсказать имя — их слишком много). Style Dictionary 4.0 генерирует CSS-переменные + TypeScript-декларации (`typescript/es6-declarations`), формат DTCG (W3C) стабилен и поддержан Figma Variables, Style Dictionary, Theo, Token Transformer. `outputReferences: true` сохраняет ссылки токенов в выводе. Тёмная тема — отдельные наборы semantic-токенов (`themes/light.json`, `themes/dark.json`), НЕ дублируя primitive-палитру.

### Российские PFM-приложения [ФАКТ/ОЦЕНКА]
Дзен-мани — автосинхронизация с банками (карты, вклады, кредиты, ИИС, брокерские, крипто), от 99 ₽; главные жалобы (Startpack, appvisor): ошибки синхронизации, вендор-лок данных, ошибки в расчётах финальных значений, проблемы с мультивалютностью. CoinKeeper — узнаваемый интерфейс с перетаскиванием монет, рейтинг App Store 4,5, от 149 ₽; воспринимается «скорее как игра, чем инструмент». У Сбера (SBOL) и Т-Банка — встроенная аналитика в банковских приложениях. **Ниша FINPILOT:** объяснимая многокритериальная оптимизация (SAW) + прогнозы Монте-Карло + план распределения свободного потока — то, чего нет у трекеров расходов, которые лишь фиксируют прошлое.

## Details

### Направление 1. Архитектура SPA

**Структура проекта.** Feature-Sliced Design (FSD) — де-факто стандарт 2026 для масштабируемых React-приложений. Слои: `app/` → `pages/` → `widgets/` → `features/` → `entities/` → `shared/`. Правило зависимостей (Unidirectional Encapsulated Flow): слой видит только нижележащие; slice не импортирует соседний slice того же слоя (общее выносить в entities/shared, желательно с ESLint-проверкой границ). Colocation — держать компонент, стили, тест, типы, хуки в одной папке. Barrel-файлы (`index.ts` как публичный API слайса) полезны для инкапсуляции, НО признанный антипаттерн при злоупотреблении: ломают tree-shaking, замедляют сборку, в RSC помечают серверные компоненты как клиентские. Для FINPILOT (SPA, без RSC) barrel-и на уровне публичного API фич — ок, глубокие barrel-и внутри — нет.

Рекомендуемая структура:
```
src/
  app/            # провайдеры, роутер, глобальные стили, темы
  pages/          # маршрутные страницы (дашборд, онбординг, детали плана)
  widgets/        # композиции: SAW-распределение, Монте-Карло-панель
  features/       # действия: смена сценария, ползунки распределения
  entities/       # доменные модели: план, долг, цель, денежный поток
  shared/         # ui-kit (shadcn), api-клиент из OpenAPI, токены, утилиты
```

**Роутинг.** TanStack Router: типобезопасные пути/параметры/search-params, loader'ы данных, интеграция с TanStack Query через один кэш, devtools прямо в приложении. Разбиение кода — по маршрутам через `lazyRouteComponent`.

**Графики (детально).**

| Библиотека | Bundle (gzip) | Рендер | Веер/CI | Санкей | Лицензия |
|---|---|---|---|---|---|
| Recharts | умеренный (SVG-нода на точку) | SVG | через Area/composed | нет | MIT |
| visx (@visx/xychart) | ~49 КБ (мин. ~15 КБ) | SVG | да (полный контроль) | да (кастом) | MIT |
| ECharts | ~100–359 КБ (tree-shake) | Canvas | да | да (нативно) | Apache-2.0 |
| Nivo | ~143 КБ | SVG/Canvas | да | да | MIT |
| Lightweight Charts | ~60 КБ | Canvas | нет | нет | Apache-2.0 |
| Chart.js | ~92 КБ core | Canvas | плагины | нет | MIT |

Для прогнозов Монте-Карло (веерный график с 80% доверительным интервалом): **visx** — band-область (10-й/90-й перцентиль) + медианная линия, полный контроль над легендой. Для денежного потока (свободный поток → долги/резерв/цели): **ECharts Sankey** нативно или составные стек-бары Recharts. Для больших рядов (график погашения по месяцам, >10k точек) — Canvas (ECharts). Recharts деградирует на больших рядах, т.к. каждая точка — SVG-нода.

**Бюджеты бандла.** Целевой initial JS дашборда — [ОЦЕНКА] ≤ 250 КБ gzip; разбиение по маршрутам через динамический import; анализ через rollup-plugin-visualizer; tree-shaking Radix (импорт по компонентам) и Recharts (импорт нужных чартов). Ставить гейт в CI: лимит на вес чанков (size-limit / bundlesize).

**i18n и PWA заранее.** [ОЦЕНКА] Выбрать i18n-библиотеку с ленивой загрузкой словарей (react-i18next или lingui — оба поддерживают code-splitting переводов) сразу и обернуть все строки в `t()` с самого начала — иначе позже переписывать весь UI. PWA — Vite PWA plugin (на Workbox); заранее заложить архитектуру: service worker кэширует статику по хэшу файлов (precache-манифест), но НЕ кэширует API-ответы с ПДн; конфликт SW с версионированием ассетов решается автоматическим precache-манифестом Workbox с хэшами.

### Направление 2. Безопасность (детально)

**CSP пошагово (FastAPI + Vite + React):**
1. FastAPI middleware генерирует nonce на каждый запрос (128+ бит из CSPRNG): `secrets.token_urlsafe(16)`.
2. Подставляет nonce в index.html (шаблон) и в заголовок: `Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-{n}'; style-src 'self' 'nonce-{n}'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'; connect-src 'self'`.
3. Проблема Radix inline-стилей — передавать nonce туда, где библиотека поддерживает, либо на переходный период `style-src 'self' 'unsafe-inline'` (задокументировать как техдолг). `'unsafe-eval'` — никогда в проде.
4. Nonce меняется на каждую загрузку страницы (nonce = number used **once**). Для статичных скриптов предпочтительнее hash, а не nonce.

**Полный набор заголовков для финтеха [ОЦЕНКА]:**
- `Strict-Transport-Security: max-age=63072000; includeSubDomains; preload`
- `X-Frame-Options: DENY` + `frame-ancestors 'none'` (CSP)
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: camera=(), microphone=(), geolocation=()`
- `X-Content-Type-Options: nosniff`
- COOP `same-origin` / COEP `require-corp` (если нужна cross-origin isolation).

**CSRF при переходе с Jinja2 на SPA:** SameSite=Lax/Strict на refresh-куке покрывает большинство. Для мутаций через куки — double submit cookie или синхронизирующий токен. При in-memory access-токене в заголовке `Authorization` CSRF на API-эндпоинты неактуален (куки не автоприкрепляются к таким запросам) — синхронизирующий токен там избыточен.

**XSS в React:** опасны `dangerouslySetInnerHTML`, ссылки `javascript:`, инъекции в SVG и в конфиги графиков. Markdown рендерить только через санитайзер (DOMPurify). Пользовательский ввод в графики — валидировать/экранировать.

**Секреты во Vite:** только переменные с префиксом `VITE_` попадают в клиентский бандл — туда НЕЛЬЗЯ класть секреты. Все ключи API — на бэкенде. Типовая утечка — случайно назвать секрет `VITE_...`.

**152-ФЗ на клиенте [ОЦЕНКА]:** логировать действия пользователя (аудит), тайм-аут сессии, повторная аутентификация на чувствительных операциях (смена плана, рекомендации по крупным суммам). На клиенте нельзя долговременно хранить ПДн и токены в localStorage.

### Направление 3. Сборка и деплой

**FastAPI vs Nginx для раздачи бандла [ОЦЕНКА]:** для продакшена — Nginx (или отдельный статик-хостинг): gzip+brotli, кэш иммутабельных ассетов (хэш в имени, `Cache-Control: max-age=31536000, immutable`), `index.html` — `no-cache`, fallback всех маршрутов на index.html (`try_files $uri /index.html`). FastAPI раздаёт только API. Для минимализма одиночки допустимо FastAPI StaticFiles на старте, но Nginx предпочтителен по производительности и кэшированию. Типовой прод-контейнер: multi-stage Docker (build → `nginx:alpine` с COPY `build/client`).

**Мониторинг:** Sentry self-hosted (в РФ-контуре) для ошибок и Web Vitals без утечки ПДн; настроить PII-scrubbing.

### Направление 4. Производительность

Гейты в CI: Lighthouse CI (пороги LCP/INP/CLS), лимит на размер бандла (size-limit / bundlesize), отслеживание регрессии веса чанков. INP — приоритет: разбивать длинные задачи, `useTransition`/`useDeferredValue` для тяжёлых пересчётов (Монте-Карло, SAW). Замерять по полевым данным (CrUX / RUM), а не только Lighthouse — лабораторные тесты систематически недооценивают провалы CWV в SPA. Диагностика — React DevTools Profiler. Высшая отдача — структурная: code-splitting по маршрутам, виртуализация списков, а не россыпь мемоизации.

### Направление 5. Доменные UI-паттерны

- **SAW-распределение** свободного потока: составной стек-бар (доли: долги/резерв/цели) + ползунки «что если»; сравнение альтернатив — таблица с сортировкой по критериям. Санкей понятен не всем неподготовленным — давать как «продвинутый вид».
- **66 альтернатив:** режим «Рекомендовано» по умолчанию (топ-3) + «Показать все» с прогрессивным раскрытием и сортировкой; не вываливать 66 карточек сразу.
- **Лавина долгов:** график погашения по месяцам, две линии «с советом»/«без совета», подпись экономии на процентах крупной цифрой.
- **Монте-Карло 80% CI:** веерный график (медиана + band 10–90%), формулировки «в 8 из 10 сценариев результат в этом диапазоне», избегать «гарантированно/точно»; легенда простыми словами.
- **Месяцы автономии / долговая нагрузка:** gauge/зоны риска (зелёная/жёлтая/красная) с явными порогами.
- **Доверие:** объяснимость каждой рекомендации («почему это»), прозрачность модели (формулы KaTeX по клику), дисклеймеры (не индивидуальная инвестиционная рекомендация), отказ от чёрного ящика.

### Направления 6–8

**Дизайн-токены** — Style Dictionary 4 (DTCG JSON → CSS vars + TS-типы), синхронизация с Claude Design через единый DTCG-файл-источник; разделять DTCG-выгрузку дизайн-инструмента и семантический слой кода, чтобы рефакторинг семантики не трогал вывод дизайн-тула.

**Тестирование** — 90% покрытие оправдано на доменной логике (расчёты SAW/Монте-Карло, форматтеры валют/процентов), вредно на тонкой UI-разметке (гонка за цифрой ради цифры); контрактное тестирование фронт↔бэк через OpenAPI + MSW-хендлеры, сгенерированные из схемы (hey-api). a11y — axe-core/Playwright axe ловит ~30–40% проблем автоматически, остальное — вручную.

**Процесс одиночки:** оценка сроков ×1.5–2, реестр рисков, ранние индикаторы (проскальзывание вех, рост флаки-тестов). Замена код-ревью — автоматические гейты (typecheck, ESLint, тесты, size-limit, a11y, визрегрессия) + ИИ-ревьюер + чек-листы; непокрытым остаётся продуктовая логика и UX-суждение. Резать объём: онбординг и дашборд обязаны быть на React к запуску; второстепенные страницы (справка, настройки, юр. тексты) можно оставить на Jinja2 (strangler fig). Перед запуском фин-продукта часто забывают: юр. дисклеймеры/согласия 152-ФЗ, регистрацию оператора ПДн в РКН, план отката, поддержку и обработку обращений пользователей.

## Recommendations

1. **Немедленно (перед первой строкой кода):** зафиксировать стек — Vite + React 19 (Compiler on), TanStack Router + Query, Zustand, Recharts+visx+ECharts, KaTeX, MSW v2, Vitest+Playwright+Argos. Настроить FSD-структуру, i18n-обёртку строк, дизайн-токены Style Dictionary. Поднять приватный npm-прокси (Verdaccio) с зеркалом, включить `--ignore-scripts` и пиннинг версий (защита от Shai-Hulud).
2. **Спринты 1–2:** онбординг (≤4 шагов, честный прогресс-бар, микрокопия) + скелет дашборда; CSP на nonce из FastAPI; httpOnly refresh + in-memory access; полный набор security-заголовков.
3. **Спринты 3–5:** SAW-распределение (стек-бар + ползунки), Монте-Карло веер (visx), лавина долгов, сравнение 66 альтернатив с прогрессивным раскрытием; KaTeX-формулы по клику для объяснимости.
4. **Перед запуском:** Lighthouse CI гейты + size-limit, self-hosted Sentry, деплой статики на Yandex/Selectel/Timeweb в РФ-регионе, бэкенд-VPS в РФ, регистрация оператора ПДн, дисклеймеры/согласия, план отката, канал поддержки.
5. **Пороги пересмотра:** если INP p75 > 200 мс — разбивать задачи / виртуализировать / useTransition; если initial JS > 250 КБ gzip — агрессивнее code-split; если срок вехи проскальзывает >20% — резать объём на Jinja2; если Shai-Hulud-подобный инцидент затрагивает зависимость — откат по lock-файлу и ротация всех токенов.

## Caveats
- Часть чисел по графикам и облачным ценам — из вторичных источников и примеров доков; перед закупкой сверять с калькуляторами провайдеров. [ОЦЕНКА]
- Темы FastAPI-vs-Nginx (детальные конфиги), выбор конкретной i18n-библиотеки и PWA-конфликты кэширования не удалось добить веб-поиском (бюджет исчерпан) — рекомендации даны на основе устоявшейся практики и первоисточников по смежным вопросам. [ОЦЕНКА]
- Цены Yandex Cloud менялись 1 мая 2025 и, по форумным упоминаниям, с 1 июля 2026 — проверять актуальные тарифы. [ГИПОТЕЗА по датам]
- Данные CrUX (55,9% origin'ов проходят все три CWV) — снимок мая 2026; метрика дрейфует. [ФАКТ на дату]

## Источники (URL для архива проекта)

**Core Web Vitals / производительность**
- https://www.corewebvitals.io/core-web-vitals
- https://www.digitalapplied.com/blog/core-web-vitals-2026-inp-lcp-cls-optimization-guide
- https://webhelpagency.com/blog/core-web-vitals-2026/
- https://technovapartners.com/en/insights/core-web-vitals-guide-2026

**Состояние / роутинг / React Compiler**
- https://betterstack.com/community/guides/scaling-nodejs/zustand-vs-redux-toolkit-vs-jotai/
- https://dev.to/jsgurujobs/state-management-in-2026-zustand-vs-jotai-vs-redux-toolkit-vs-signals-2gge
- https://tech-insider.org/zustand-vs-redux-2026/
- https://saschb2b.com/blog/react-state-management-2026
- https://devtoolbox.blog/tanstack-router-vs-react-router-v7-2026/
- https://www.pkgpulse.com/guides/react-router-v7-vs-tanstack-router-2026
- https://medium.com/ekino-france/tanstack-router-vs-react-router-v7-32dddc4fcd58
- https://ilirivezaj.com/guides/react-performance-guide
- https://www.sitepoint.com/react-20-compiler-usememo-changes/
- https://stevekinney.com/courses/react-performance/usememo-usecallback-in-react-19
- https://pavanrangani.com/blog/react-compiler-automatic-memoization-guide

**Графики / виртуализация / формулы**
- https://apexcharts.com/blog/state-of-javascript-charting-2026/
- https://blog.logrocket.com/best-react-chart-libraries-2026/
- https://chenguangliang.com/en/posts/blog152_react-chart-libraries-comparison/
- https://www.usedatabrain.com/blog/react-chart-libraries
- https://chartts.com/blog/best-react-chart-libraries-2026
- https://www.pkgpulse.com/guides/tanstack-virtual-vs-react-window-vs-react-virtuoso-2026
- https://tanstack.com/table/v8/docs/guide/virtualization
- https://en.wikipedia.org/wiki/KaTeX
- https://biggo.com/news/202511040733_KaTeX_MathJax_Web_Rendering_Comparison
- https://www.intmath.com/cg5/katex-mathjax-comparison.php

**Архитектура / FSD**
- https://feature-sliced.design/
- https://softaims.com/blog/scalable-react-architecture-patterns-2026
- https://medium.com/@albert_barsegyan/the-best-react-js-architecture-for-2026-domain-driven-feature-sliced-design-87f6e25d13fe
- https://dev.to/algoorgoal/feature-sliced-design-review-22k0

**Безопасность / CSP / токены / npm supply chain**
- https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/nonce
- https://www.stackhawk.com/blog/react-content-security-policy-guide-what-it-is-and-how-to-enable-it/
- https://oneuptime.com/blog/post/2026-01-15-content-security-policy-csp-react/view
- https://github.com/radix-ui/primitives/issues/2057
- https://github.com/radix-ui/primitives/issues/3063
- https://github.com/radix-ui/primitives/discussions/3130
- https://github.com/remix-run/react-router/discussions/14306
- https://auth0.com/docs/secure/security-guidance/data-security/token-storage
- https://mojoauth.com/blog/session-storage-vs-localstorage-cookies-code
- https://www.codestudy.net/blog/where-to-store-the-refresh-token-on-the-client/
- https://www.zscaler.com/blogs/security-research/shai-hulud-v2-poses-risk-npm-supply-chain
- https://www.microsoft.com/en-us/security/blog/2025/12/09/shai-hulud-2-0-guidance-for-detecting-investigating-and-defending-against-the-supply-chain-attack/
- https://unit42.paloaltonetworks.com/npm-supply-chain-attack/
- https://www.aikido.dev/blog/shai-hulud-strikes-again-hitting-zapier-ensdomains
- https://www.securityweek.com/640-npm-packages-infected-in-new-shai-hulud-supply-chain-attack/
- https://access.redhat.com/security/supply-chain-attacks-NPM-packages

**152-ФЗ / российское облако / npm-зеркала**
- https://www.business.ru/article/5705-152-fz-o-personalnyh-dannyh-gg
- https://linkodium.com/news/novye-trebovaniya-roskomnadzora-po-zakonu-152-fz-na-30-maya-2025-goda/
- https://wcr-consulting.com/blog/2026/03/13/lokalizaciya-baz-dannyh-personalnyh-dannyh/
- https://bigpanda.pro/blog/152-fz-instrukciya
- https://stakhanovets.ru/blog/152-fz-o-zashhite-personalnyh-dannyh-trebovaniya-i-shtrafy-v-2026-godu/
- https://cloud.yandex.ru/docs/storage/pricing
- https://cloud.yandex.ru/docs/cdn/pricing
- https://cloud.yandex.ru/solutions/152-fz
- https://selectel.ru/services/cloud/storage/
- https://selectel.ru/services/cloud/vps-vds/
- https://selectel.ru/prices/
- https://timeweb.cloud/services/vds-vps
- https://timeweb.cloud/docs/s3-storage/tariffication
- https://timeweb.cloud/solutions/152fz
- https://cloud.ru/docs/s3e/ug/topics/pricing
- https://gitverse.ru/docs/artifactory/registry-mirrors/npm-mirror/
- https://getautonoma.com/blog/npm-outage-january-2026
- https://habr.com/en/articles/739298/comments

**Тестирование / MSW / визуальная регрессия**
- https://qaskills.sh/blog/msw-mock-service-worker-testing-guide-2026
- https://qaskills.sh/blog/vitest-browser-mode-mock-service-worker
- https://npmx.dev/package/hey-api-playwright
- https://www.pkgpulse.com/guides/best-npm-packages-api-testing-mocking-2026
- https://delta-qa.com/en/blog/top-10-visual-testing-tools-2026/
- https://delta-qa.com/en/blog/chromatic-vs-percy-comparison-2026/
- https://www.youngurbanproject.com/best-visual-testing-tools/
- https://crosscheck.cloud/blogs/percy-vs-applitools-vs-chromatic-visual-regression-testing/

**Дизайн-токены**
- https://www.npmjs.com/package/style-dictionary
- https://www.npmjs.com/package/style-dictionary-utils
- https://www.webtoolshub.online/blog/css-variables-design-tokens-dark-mode-system-2026
- https://typestyles.dev/docs/style-dictionary/

**Онбординг / PFM / доменные паттерны**
- https://qubstudio.com/blog/digital-onboarding-fintech/
- https://zigment.ai/blog/7-ways-to-reduce-fintech-onboarding-drop-off-in-2026
- https://www.convertcart.com/blog/conversion-rate-optimization-statistics
- https://getperspective.ai/blog/fintech-customer-experience-2026-onboarding-trust-drop-off
- https://hi-tech.mail.ru/articles/145793-luchshie-prilozheniya-dlya-ucheta-finansov/
- https://startpack.ru/compare/zenmoney/coinkeeper
- https://a2is.ru/catalog/uchyot-lichnykh-finansov/compare/coinkeeper/zen-money
- https://scilead.ru/article/11411-sravnitelnij-analiz-mobilnikh-prilozhenij-dl
- https://appvisor.ru/app/ios/dzenmani-uchet-raskhodov-6995/
