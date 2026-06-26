# FINPILOT — Архитектурные диаграммы

> Стабильные диаграммы, отражающие фундамент системы: слои приложения, модель данных,
> математический конвейер ядра, развёртывание и связи компонентов, жизненный цикл запроса,
> аутентификацию и карту фронта. Это «медленные» вещи — математика зафиксирована в
> `math_model_v3_0_0.md` (v3.0.0), структура сущностей и слоёв устоялась.
> Диаграммы построены **по коду** (`app/`), а не по намерению. Формат — Mermaid (рендерится
> в GitHub и большинстве IDE). При изменении кода, влияющего на схему, диаграмму обновляем
> в том же батче.
>
> Содержание: [1. Архитектура слоёв](#1-архитектура-слоёв) ·
> [2. Модель данных (ER)](#2-модель-данных-er) ·
> [3. Конвейер ядра (9 шагов)](#3-конвейер-ядра-9-шагов) ·
> [4. Поток запроса `/calculate`](#4-поток-запроса-apiplanningcalculate) ·
> [5. Развёртывание и компоненты](#5-развёртывание-и-компоненты) ·
> [6. Жизненный цикл запроса](#6-жизненный-цикл-запроса-middleware-конвейер) ·
> [7. Аутентификация и сессия](#7-аутентификация-и-сессия) ·
> [8. Карта фронта](#8-карта-фронта-страницы-и-навигация)

---

## 1. Архитектура слоёв

Однонаправленная зависимость: HTTP → сервисы → ядро/БД. Ядро (`app/core/`) не знает о
вебе и не ходит в БД — чистые функции над переданными данными (это и делает его
тестируемым и переиспользуемым).

```mermaid
flowchart TD
    Client["Браузер / API-клиент"]

    subgraph HTTP["app/api/ — HTTP-слой (FastAPI)"]
        Routes["routes_*.py<br/>auth · transactions · planning · goals ·<br/>obligations · liquid_assets · banks · b2b · analytics"]
        MW["middleware.py · _guards.py<br/>CSRF · rate-limit · security-заголовки"]
    end

    subgraph SVC["app/services/ — прикладные сервисы"]
        Planning["planning.py — оркестрация расчёта"]
        Spending["spending.py — советы по тратам"]
        Ingestion["ingestion/ — парсеры выписок<br/>CSV · XLSX · PDF · 1C"]
        Infra["cache · currency · cbr_rate/fx ·<br/>event_logger · email_service · analytics"]
    end

    subgraph CORE["app/core/ — математическое ядро (чистые функции)"]
        direction LR
        Pipeline["preprocessing · metrics · forecast ·<br/>alternatives · avalanche · goals_priority ·<br/>filtering · ranking · recommendation"]
        Support["categorization · envelopes · money · spending_advice"]
    end

    subgraph DATA["app/database/ — данные"]
        CRUD["crud.py"]
        Models["models.py (SQLAlchemy 2.0)"]
        DB[("PostgreSQL / SQLite")]
    end

    Schemas["app/schemas/ — Pydantic v2 (валидация I/O)"]

    Client --> MW --> Routes
    Routes --> Schemas
    Routes --> Planning
    Routes --> Spending
    Routes --> Ingestion
    Routes --> CRUD
    Planning --> Pipeline
    Planning --> CRUD
    Planning --> Infra
    Spending --> Support
    CRUD --> Models --> DB
```

---

## 2. Модель данных (ER)

Финансовое ядро. `User` — корень владения (почти у всех таблиц есть `user_id`; гостевой
режим = `user_id IS NULL`). `Transaction`, `Obligation`, `Goal`, `LiquidAsset` несут
soft-delete (`is_deleted` / `deleted_at`). Историю несут дочерние `ObligationPayment` и
`GoalContribution`. `Recommendation` — снимки выданных планов, `Event` — аналитика воронки.

```mermaid
erDiagram
    User ||--o{ Transaction : "владеет"
    User ||--o{ Obligation : "владеет"
    User ||--o{ Goal : "владеет"
    User ||--o{ LiquidAsset : "владеет"
    User ||--o| UserPrefs : "настройки"
    User ||--o{ Recommendation : "история планов"
    User ||--o{ Event : "аналитика"
    User ||--o{ Scenario : "сценарии"

    Category ||--o{ Transaction : "категоризует"
    Obligation ||--o{ ObligationPayment : "платежи"
    Goal ||--o{ GoalContribution : "взносы"
    LiquidAsset |o--o{ Goal : "конверт (linked_asset, SET NULL)"
    Recommendation ||--o{ Scenario : "what-if"

    User {
        string id PK
        string email
        string password_hash
    }
    Transaction {
        int id PK
        string user_id FK
        int category_id FK
        float amount
        bool is_deleted
        datetime deleted_at
    }
    Obligation {
        int id PK
        string user_id FK
        float amount
        float interest_rate
        float monthly_payment
        bool is_deleted
    }
    Goal {
        int id PK
        string user_id FK
        int linked_asset_id FK
        float target_amount
        float current_amount
        bool is_deleted
    }
    LiquidAsset {
        int id PK
        string user_id FK
        float amount
        float interest_rate
        bool is_deleted
    }
    ObligationPayment {
        int id PK
        int obligation_id FK
        float amount
    }
    GoalContribution {
        int id PK
        int goal_id FK
        float amount
    }
    Recommendation {
        int id PK
        string user_id FK
    }
    Scenario {
        int id PK
        string user_id FK
        int recommendation_id FK
    }
```

> Второстепенные таблицы (вне ядра планирования) на схеме опущены для читаемости:
> `Budget`, `FxRate`, `PlaidToken`, `ManualSnapshot`, `NotificationLog`, `Category`-справочник.

---

## 3. Конвейер ядра (9 шагов)

Главный алгоритм — **стек именованных методов**, а не одна формула (подробно по шагам:
`algorithm_stack.md`; параметры — `math_model_v3_0_0.md`). Шаги 1–2 — учёт,
3 — прогноз, 4–8 — выбор, 9 — объяснение.

```mermaid
flowchart TD
    In["Транзакции · обязательства · цели · активы · prefs"]

    S1["1 · Препроцессинг<br/><code>preprocessing.py</code><br/>агрегация, очистка, валюта"]
    S2["2 · Базовые метрики<br/><code>metrics.py</code><br/>CF → Rt=CF−ΣP · Lt=B_liq/Σe (мес) · Dt=ПДН · BLR"]
    S3["3 · Прогноз<br/><code>forecast.py</code><br/>SES + Monte-Carlo, интервал 80% [p10..p90]"]
    S4["4 · Предобработка B_liq<br/><code>goals_priority.py</code>"]
    S5["5 · Генерация альтернатив<br/><code>alternatives.py</code><br/>stars-and-bars, шаг 10% → 66 комбинаций"]
    S6["6 · Оценка вариантов<br/><code>avalanche.py</code> (Debt Avalanche + OCR) +<br/><code>goals_priority.py</code> (цели: категория × срочность)"]
    S7["7 · Фильтрация<br/><code>filtering.py</code><br/>жёсткие инварианты: Rt≥0 · ПДН≤0.40 · L_min (выкл по умолч.)"]
    S8["8 · Ранжирование SAW<br/><code>ranking.py</code><br/>min-max нормализация → свёртка по весам профиля риска"]
    S9["9 · Объяснение<br/><code>recommendation.py</code><br/>лучшее распределение + обоснование + топ-3"]
    Out["План: Rt/Lt/Dt/BLR · распределение · прогноз · альтернативы"]

    In --> S1 --> S2 --> S3 --> S4 --> S5 --> S6 --> S7 --> S8 --> S9 --> Out
```

---

## 4. Поток запроса `/api/planning/calculate`

Как HTTP-запрос проходит слои до ядра и обратно. `run_planning` (шаги 5–8 конвейера) обёрнут
TTL-кэшем по отпечатку эффективных входов; логирование воронки выполняется **на каждый**
вызов, даже при попадании в кэш (поэтому кэш — вокруг расчёта, не вокруг роута).

```mermaid
sequenceDiagram
    autonumber
    participant C as Клиент
    participant R as routes_planning
    participant P as services/planning
    participant Rate as cbr_rate (+fallback 0.14)
    participant Core as core (конвейер)
    participant Cache as TTLCache
    participant Log as event_logger

    C->>R: POST /calculate (risk, l_min, overrides)
    R->>P: _compute_plan(payload, prefs)
    P->>P: prepare_data + конвертация валют
    P->>Rate: r_bench = ключевая ЦБ × (1−НДФЛ)
    P->>Cache: отпечаток эффективных входов?
    alt попадание
        Cache-->>P: кэшированный результат (deepcopy)
    else промах
        P->>Core: run_planning (альтернативы → оценка → фильтр → SAW)
        Core-->>P: лучший план + альтернативы
        P->>Cache: сохранить
    end
    P-->>R: результат
    R->>Log: log_recommendation + log_event (всегда)
    R-->>C: JSON (план, метрики, прогноз)
```

---

## 5. Развёртывание и компоненты

Как части системы связаны в проде. Сервер — единый процесс FastAPI под uvicorn (SSR-шаблоны
+ статика + API в одном приложении). Внешние зависимости немногочисленны и заменяемы; их
недоступность не роняет приложение (ставка ЦБ имеет фолбэк, письма/мониторинг — опциональны).

```mermaid
flowchart LR
    subgraph Client["Клиент (браузер)"]
        UI["Jinja2 SSR-страницы +<br/>vanilla JS: app.js, auth.js<br/>токен в localStorage"]
    end

    subgraph Server["Сервер — uvicorn · FastAPI (один процесс)"]
        MW["Middleware-цепочка"]
        Routes["Роуты: страницы (HTML) · /api/* · /v1/analyze (B2B)"]
        Svc["Сервисы + ядро (app/core)"]
    end

    subgraph Data["Хранилище"]
        DB[("PostgreSQL (прод)<br/>SQLite (dev)")]
    end

    subgraph Ext["Внешние сервисы (заменяемы, с деградацией)"]
        CBR["cbr-xml-daily.ru<br/>ставка ЦБ → r_bench<br/>(фолбэк 0.14)"]
        SMTP["SMTP<br/>письма: verify, сброс пароля"]
        Sentry["Sentry<br/>мониторинг ошибок"]
    end

    UI -->|"HTTPS: HTML + JSON API<br/>Authorization: Bearer"| MW
    MW --> Routes --> Svc
    Svc --> DB
    Svc -. "ставка (с кэшем)" .-> CBR
    Svc -. "уведомления" .-> SMTP
    Server -. "события ошибок" .-> Sentry
```

---

## 6. Жизненный цикл запроса (middleware-конвейер)

Любой HTTP-запрос проходит сквозь цепочку middleware до роута и обратно. Порядок —
обратный регистрации в `main.py` (последний `add_middleware` оборачивает снаружи). Это
стабильный инфраструктурный слой, общий для страниц и API.

```mermaid
flowchart TD
    Req["HTTP-запрос"]
    L1["RequestLoggingMiddleware<br/>лог + request-id"]
    L2["CORSMiddleware<br/>проверка origin"]
    L3["SecurityHeadersMiddleware<br/>заголовки безопасности (+HSTS в проде)"]
    L4["CSRFMiddleware<br/>проверка origin для мутаций"]
    L5["RateLimitMiddleware<br/>лимит частоты"]
    Router["Роут-хендлер:<br/>HTML-страница · /api/* · /v1/analyze"]
    Resp["HTTP-ответ"]

    Req --> L1 --> L2 --> L3 --> L4 --> L5 --> Router
    Router -->|"ответ идёт обратно сквозь цепочку"| Resp
```

---

## 7. Аутентификация и сессия

Гостевой режим — первоклассный: без токена приложение работает с данными `user_id IS NULL`.
Регистрация и вход возвращают Bearer-токен сразу; подтверждение email — фоновое (письмо через
SMTP) и вход не блокирует. Токен хранится в localStorage и подставляется в `Authorization`.

```mermaid
sequenceDiagram
    autonumber
    participant U as Браузер (auth.js)
    participant API as /api/auth
    participant DB as БД
    participant Mail as SMTP

    Note over U,API: Гость — без токена, данные user_id = NULL

    rect rgb(232, 245, 233)
    Note over U: Регистрация
    U->>API: POST /register {email, password, consent}
    API->>DB: создать пользователя
    API-->>U: access_token (Bearer) — сразу
    API-)Mail: письмо подтверждения (фоном, не блокирует)
    end

    rect rgb(232, 240, 245)
    Note over U: Вход
    U->>API: POST /login {email, password}
    API->>DB: проверить пароль
    API-->>U: access_token
    end

    Note over U: токен → localStorage

    U->>API: GET /me (Authorization: Bearer)
    API-->>U: профиль → шапка показывает email + «Выход»

    U->>API: POST /logout → токен очищается, снова гость
```

---

## 8. Карта фронта (страницы и навигация)

Тонкий SSR-фронт: один каркас `base.html` (навигация + модалка авторизации + подключение JS),
от которого наследуются все страницы. Логика — два модуля: `app.js` (страницы, расчёты,
CRUD-вызовы API) и `auth.js` (модалка входа/регистрации). Набор страниц давно стабилен.

```mermaid
flowchart TD
    Base["base.html — каркас<br/>навигация · модалка #auth-modal · подключение app.js + auth.js"]

    subgraph Core["Рабочие страницы"]
        Index["/ — index (главная)"]
        Dash["/dashboard — обзор"]
        Plan["/planning — планирование (СППР)"]
        Tx["/transactions — операции"]
        Obl["/obligations — обязательства"]
        Goals["/goals — цели"]
        Banks["/banks — импорт выписок"]
        Val["/validation — проверка на портретах"]
        Profile["/profile — профиль и настройки"]
    end

    subgraph Legal["Юридические / служебные"]
        Privacy["/legal/privacy · /legal/terms · /legal/consent"]
        Contacts["/contacts — реквизиты оператора"]
        Reset["/reset-password · forgot_password"]
    end

    subgraph JS["JS-модули"]
        AppJs["app.js — логика страниц, расчёты, вызовы /api/*"]
        AuthJs["auth.js — модалка авторизации, Bearer-токен"]
    end

    Base --> Core
    Base --> Legal
    Base -.-> JS
```
