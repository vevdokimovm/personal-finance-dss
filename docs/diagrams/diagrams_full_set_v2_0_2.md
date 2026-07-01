# FINPILOT — Полный комплект диаграмм и схем

> **Документ-комплект для ВКР.** Содержит 20 диаграмм по продукту FINPILOT (СППР в персональных финансах), разбитых по разделам выпускной работы. Для каждой диаграммы дан исходный код (Mermaid / PlantUML / DBML / Graphviz), указано **в какое приложение его вставить** для качественного рендера, и привязка к разделу ВКР.
>
> Все диаграммы построены **по реальному коду** из `app/` — не по абстрактному описанию.

---

## Как пользоваться

| Формат кода | Куда вставлять для рендера | Зачем |
|---|---|---|
| **Mermaid** | GitHub/GitLab README, Obsidian, Notion, [mermaid.live](https://mermaid.live), draw.io (Arrange → Insert → Advanced → Mermaid) | Быстро, версионируется, для черновика и README |
| **PlantUML** | [plantuml.com/plantuml](https://www.plantuml.com/plantuml), плагин PyCharm "PlantUML Integration", VS Code "PlantUML" | Серьёзные UML для ВКР (Use Case с include/extend, Class) |
| **DBML** | [dbdiagram.io](https://dbdiagram.io) → экспорт в PNG/PDF/SQL | Схема БД сразу в картинку И в SQL DDL |
| **Graphviz (DOT)** | [dreampuf.github.io/GraphvizOnline](https://dreampuf.github.io/GraphvizOnline) | Графы зависимостей |
| **draw.io (.drawio)** | [app.diagrams.net](https://app.diagrams.net) → File → Open | Готовые ГОСТ-блок-схемы в папке `drawio/` — открыл и сразу чистый вид |

**Для ВКР по 09.03.01 рекомендация:** ГОСТ-блок-схемы (раздел «Алгоритмическое обеспечение») открывай из готовых `.drawio` файлов — они уже оформлены по ГОСТ 19.701-90. Остальное рендери из Mermaid/PlantUML/DBML.

---

## Навигация

**Технические диаграммы (под разделы ВКР):**
1. [IDEF0 — функциональный контекст](#1-idef0--функциональный-контекст) · *анализ области*
2. [Use Case — диаграмма вариантов использования](#2-use-case--диаграмма-вариантов-использования) · *требования*
3. [C4 Level 1 — System Context](#3-c4-level-1--system-context) · *архитектура*
4. [C4 Level 2 — Containers](#4-c4-level-2--containers) · *архитектура*
5. [C4 Level 3 — Components](#5-c4-level-3--components) · *архитектура*
6. [ER-диаграмма базы данных](#6-er-диаграмма-базы-данных-dbml) · *данные*
7. [Sequence — полный цикл планирования](#7-sequence--полный-цикл-планирования) · *поведение*
8. [Sequence — импорт банковской выписки](#8-sequence--импорт-банковской-выписки) · *поведение*
9. [Блок-схема ГОСТ — главный pipeline](#9-блок-схема-гост--главный-pipeline-алгоритма) · *алгоритм ⭐*
10. [Блок-схема ГОСТ — Avalanche + OCR](#10-блок-схема-гост--avalanche--ocr-фильтр) · *алгоритм ⭐*
11. [Блок-схема ГОСТ — взвешенная Si](#11-блок-схема-гост--взвешенная-обеспеченность-целей-si) · *алгоритм ⭐*
12. [Блок-схема ГОСТ — SES + Monte-Carlo](#12-блок-схема-гост--прогноз-ses--monte-carlo) · *алгоритм ⭐*
13. [UML Class — диаграмма классов](#13-uml-class--диаграмма-классов) · *реализация*
14. [State Machine — жизненный цикл альтернативы](#14-state-machine--жизненный-цикл-альтернативы) · *поведение*
15. [Graphviz — граф зависимостей модулей](#15-graphviz--граф-зависимостей-модулей) · *реализация*

**Бизнес-методологии (из методички):**
16. [PDCA — цикл Деминга](#16-pdca--цикл-деминга) · *улучшение продукта*
17. [BPMN 2.0 — бизнес-процесс](#17-bpmn-20--бизнес-процесс-получения-рекомендации) · *процесс*
18. [EPC — событийная цепочка](#18-epc--событийная-цепочка-планирования) · *процесс*
19. [VSM — поток создания ценности](#19-vsm--поток-создания-ценности) · *Lean*
20. [DMAIC — цикл Six Sigma](#20-dmaic--цикл-снижения-дефектов-рекомендаций) · *качество*

---

# 1. IDEF0 — функциональный контекст

**Раздел ВКР:** анализ предметной области. **Нотация:** IDEF0 (функциональное моделирование).
**Что показывает:** систему как функцию A0 с входами/выходами/управлением/механизмами (ICOM).
**Рендер:** Mermaid → GitHub/Obsidian. Для строгого IDEF0 с туннелями — Ramus Educational или Bizagi (см. методичку, российские инструменты).

```mermaid
flowchart LR
    subgraph A0["A0: Поддержать принятие финансового решения"]
        direction TB
        FUNC["Сгенерировать и ранжировать<br/>альтернативы распределения Rt"]
    end

    I1["Транзакции It, Ej"] -->|Вход| FUNC
    I2["Обязательства O, цели G"] -->|Вход| FUNC
    I3["Ликвидная позиция Bliq"] -->|Вход| FUNC

    C1["Профиль риска R (веса)"] -->|Управление| FUNC
    C2["Пороги: Lmin, Dmax, r_bench"] -->|Управление| FUNC
    C3["ГОСТ / нормы Greninger, ЦБ РФ"] -->|Управление| FUNC

    FUNC -->|Выход| O1["Оптимальная альтернатива a*"]
    FUNC -->|Выход| O2["Top-3 + объяснения"]
    FUNC -->|Выход| O3["Показатели Rt, Lt, Dt, BLR"]

    M1["Алгоритм SAW + Avalanche"] -.->|Механизм| FUNC
    M2["FastAPI + SQLAlchemy"] -.->|Механизм| FUNC
```

> **ICOM-расшифровка:** Inputs (слева) — данные пользователя; Controls (сверху) — профиль риска и пороговые ограничения, управляющие логикой; Outputs (справа) — рекомендация; Mechanisms (снизу) — чем реализуется.

---

# 2. Use Case — диаграмма вариантов использования

**Раздел ВКР:** постановка задачи / требования. **Нотация:** UML Use Case.
**Рендер:** **PlantUML** (нужны `include`/`extend`) → plantuml.com/plantuml или плагин PyCharm.

```plantuml
@startuml
left to right direction
skinparam packageStyle rectangle
skinparam actorStyle awesome

actor "Пользователь" as User
actor "Банк (CSV/API)" as Bank

rectangle FINPILOT {
  usecase "Вести транзакции" as UC1
  usecase "Вести обязательства" as UC2
  usecase "Вести цели накопления" as UC3
  usecase "Вести ликвидные активы" as UC4
  usecase "Настроить профиль риска\nи пороги" as UC5
  usecase "Импортировать выписку" as UC6
  usecase "Получить рекомендацию\n(полный цикл СППР)" as UC7
  usecase "Посмотреть дашборд\nпоказателей" as UC8
  usecase "Построить прогноз\nRt/Lt/Dt" as UC9

  usecase "Рассчитать базовые\nпоказатели" as UC10
  usecase "Применить Avalanche\n+ OCR-фильтр" as UC11
  usecase "Ранжировать по SAW" as UC12
}

User --> UC1
User --> UC2
User --> UC3
User --> UC4
User --> UC5
User --> UC6
User --> UC7
User --> UC8
User --> UC9

UC6 ..> Bank : <<include>>
UC7 ..> UC10 : <<include>>
UC7 ..> UC11 : <<include>>
UC7 ..> UC12 : <<include>>
UC8 ..> UC10 : <<include>>
UC9 ..> UC10 : <<include>>
UC7 ..> UC9 : <<extend>>
@enduml
```

---

# 3. C4 Level 1 — System Context

**Раздел ВКР:** проектирование архитектуры. **Нотация:** C4 (Context).
**Что показывает:** систему целиком и её окружение — кто пользуется и с чем связана.
**Рендер:** Mermaid (поддерживает `C4Context`) → mermaid.live или GitHub.

```mermaid
C4Context
    title FINPILOT — System Context

    Person(user, "Пользователь", "Физлицо, планирующее личные финансы")

    System(finpilot, "FINPILOT", "СППР: распределение свободного потока между долгом, резервом и целями")

    System_Ext(bank, "Банковская выписка", "CSV/Excel из Тинькофф, Сбер, Альфа, ВТБ и др.")

    Rel(user, finpilot, "Вводит данные, получает рекомендации", "HTTPS / Web UI")
    Rel(user, bank, "Выгружает выписку")
    Rel(bank, finpilot, "Импорт транзакций", "CSV upload")
```

---

# 4. C4 Level 2 — Containers

**Раздел ВКР:** проектирование архитектуры. **Нотация:** C4 (Container).
**Что показывает:** из каких разворачиваемых блоков состоит система.
**Рендер:** Mermaid → mermaid.live. Для презентации красивее — D2 или draw.io.

```mermaid
C4Container
    title FINPILOT — Containers

    Person(user, "Пользователь", "")

    Container_Boundary(c1, "FINPILOT") {
        Container(web, "Web-фронтенд", "Jinja2 + ванильный JS", "7 страниц: dashboard, planning, transactions, obligations, goals, banks")
        Container(api, "Backend API", "Python 3, FastAPI, Uvicorn", "REST API: /api/* — роутеры по сущностям + /planning/calculate")
        Container(core, "Ядро алгоритма", "Python (app/core, app/services)", "6-этапный pipeline СППР")
        ContainerDb(db, "База данных", "SQLite / PostgreSQL (SQLAlchemy 2.0)", "5 таблиц: transactions, obligations, goals, liquid_assets, user_prefs")
    }

    System_Ext(bank, "Банк CSV/Excel", "")

    Rel(user, web, "Использует", "HTTPS")
    Rel(web, api, "Вызывает", "JSON/REST")
    Rel(api, core, "Делегирует расчёт")
    Rel(api, db, "Читает/пишет", "SQLAlchemy ORM")
    Rel(bank, api, "Импорт выписки", "multipart/form-data")
```

---

# 5. C4 Level 3 — Components

**Раздел ВКР:** проектирование архитектуры. **Нотация:** C4 (Component).
**Что показывает:** внутреннее устройство ядра — модули `app/core` и `app/services` и их связи.
**Рендер:** Mermaid → mermaid.live.

```mermaid
flowchart TB
    subgraph API["app/api — REST-слой"]
        RP["routes_planning.py"]
        RR["routes_recommendation.py"]
    end

    subgraph SVC["app/services — оркестрация"]
        PLAN["planning.py<br/>run_planning()"]
        PIPE["pipeline.py<br/>run_pipeline()"]
        FCST["forecasting.py<br/>forecast_indicators()"]
        PARSE["statement_parser.py"]
        BANK["bank_api.py"]
    end

    subgraph CORE["app/core — алгоритмическое ядро"]
        PREP["preprocessing.py"]
        MET["metrics.py<br/>Rt, Lt, Dt, BLR, Si"]
        ALT["alternatives.py<br/>generate + evaluate"]
        AVA["avalanche.py<br/>OCR-фильтр"]
        GOAL["goals_priority.py<br/>Si + prealloc Bliq"]
        FILT["filtering.py"]
        RANK["ranking.py<br/>SAW + профили"]
        REC["recommendation.py<br/>NLG-объяснения"]
        FC["forecast.py<br/>SES + Monte-Carlo"]
    end

    subgraph DB["app/database"]
        CRUD["crud.py"]
        MODELS["models.py"]
    end

    RP --> PLAN
    RP --> FCST
    RR --> PIPE
    PLAN --> PREP & MET & ALT & FILT & RANK & REC & GOAL
    PIPE --> PREP & MET & REC
    ALT --> AVA & GOAL
    FCST --> FC
    PLAN --> CRUD
    CRUD --> MODELS
```

---

# 6. ER-диаграмма базы данных (DBML)

**Раздел ВКР:** проектирование данных. **Нотация:** ER + DBML.
**Что показывает:** 5 таблиц БД по `app/database/models.py`.
**Рендер:** **dbdiagram.io** — вставь код, получишь картинку + кнопка Export to PostgreSQL.

> ⚠️ В коде таблицы не связаны внешними ключами (модель «один пользователь = одна БД»). Ниже — концептуальная связь через `user_prefs` как единый контекст пользователя, для наглядности в ВКР.

```dbml
Table transactions {
  id integer [pk, increment]
  amount float [not null]
  category varchar(255) [not null]
  type varchar(20) [not null, note: 'income | expense']
  date datetime [not null]
  is_synced boolean [not null, default: false]
}

Table obligations {
  id integer [pk, increment]
  name varchar(255) [not null, default: 'Обязательство']
  amount float [not null, note: 'остаток тела долга']
  interest_rate float [not null, default: 0, note: 'годовая ставка rk']
  term integer [not null, default: 0, note: 'остаточный срок, мес']
  monthly_payment float [not null, note: 'аннуитетный платёж Pk']
  payment_day integer [not null, default: 1]
  comment text [null]
}

Table goals {
  id integer [pk, increment]
  name varchar(255) [not null]
  target_amount float [not null, note: 'целевая сумма']
  current_amount float [not null, default: 0]
  deadline datetime [not null]
  category varchar(32) [not null, default: 'material', note: 'income_growth | safety | material | emotional']
  comment text [null]
}

Table liquid_assets {
  id integer [pk, increment]
  name varchar(255) [not null, default: 'Депозит']
  amount float [not null, default: 0]
  interest_rate float [not null, default: 0]
  type varchar(32) [not null, default: 'deposit']
  comment text [null]
}

Table user_prefs {
  id integer [pk, default: 1]
  l_min float [not null, default: 0, note: 'минимальная Lt']
  risk_tolerance integer [not null, default: 3, note: 'профиль риска 1..5']
  horizon integer [not null, default: 12]
  r_bench float [not null, default: 0.14, note: 'OCR — порог Avalanche']
}
```

---

# 7. Sequence — полный цикл планирования

**Раздел ВКР:** проектирование поведения. **Нотация:** UML Sequence.
**Что показывает:** что происходит при `POST /api/planning/calculate` — от запроса до рекомендации.
**Рендер:** Mermaid → mermaid.live / GitHub.

```mermaid
sequenceDiagram
    actor U as Пользователь
    participant API as routes_planning
    participant DB as crud
    participant PR as preprocessing
    participant PL as planning.run_planning
    participant GP as goals_priority
    participant ALT as alternatives
    participant AV as avalanche
    participant F as filtering
    participant R as ranking
    participant REC as recommendation

    U->>API: POST /planning/calculate {risk, l_min, r_bench}
    API->>DB: get_user_prefs / transactions / obligations / goals / assets
    DB-->>API: данные
    API->>PR: prepare_data(...)
    PR-->>API: нормализованные данные + active_goals
    API->>PL: run_planning(income, expense, obls, goals, bliq, ...)

    PL->>GP: preallocate_from_bliq(bliq, goals)
    GP-->>PL: bliq_after, closed_goals, active_goals
    PL->>PL: расчёт Rt, Lt, Dt, BLR
    PL->>ALT: generate_alternatives(Rt+, ...)
    ALT-->>PL: 21 альтернатива

    loop для каждой альтернативы
        PL->>ALT: evaluate_alternative(a)
        ALT->>AV: allocate_obligations_avalanche(x_obl, obls, r_bench)
        AV-->>ALT: x_eff, new_obls, x_unused
        ALT->>GP: calculate_goals_si(x_goals, goals)
        GP-->>ALT: Si, allocation
        ALT-->>PL: a + {Rt', Lt', Dt', Si}
    end

    PL->>F: filter_alternatives(...)
    F-->>PL: admissible, rejected
    PL->>R: rank_alternatives(admissible, risk)
    R-->>PL: ranked (a* первый)
    PL->>REC: explain_alternative(top-3)
    REC-->>PL: gains / costs / insight
    PL-->>API: {indicators, top3, best, ranked, ...}
    API-->>U: JSON с рекомендацией
```

---

# 8. Sequence — импорт банковской выписки

**Раздел ВКР:** проектирование поведения. **Нотация:** UML Sequence.
**Что показывает:** загрузку CSV-выписки и её разбор в транзакции.
**Рендер:** Mermaid → mermaid.live / GitHub.

```mermaid
sequenceDiagram
    actor U as Пользователь
    participant API as routes_banks
    participant SP as statement_parser
    participant P as parse_bank_statement
    participant DB as crud

    U->>API: POST /banks/import {file, bank_id}
    API->>SP: parse_bank_statement(content, bank_id)
    SP->>P: выбор парсера по bank_id<br/>(tinkoff/sber/universal)

    loop по строкам CSV
        P->>P: _get_field(row, candidates)
        P->>P: _parse_date() + нормализация суммы
        P->>P: тип = expense если сумма < 0, иначе income
    end

    P-->>SP: list[transaction dict]
    SP-->>API: распарсенные транзакции
    loop для каждой транзакции
        API->>DB: create_transaction(is_synced=True)
    end
    DB-->>API: сохранено
    API-->>U: {imported: N, transactions}
```

---

# 9. Блок-схема ГОСТ — главный pipeline алгоритма

**Раздел ВКР:** алгоритмическое обеспечение ⭐ (ядро работы). **Нотация:** ГОСТ 19.701-90.
**Что показывает:** все 6 этапов СППР от ввода данных до выбора `a*`.
**Рендер для ВКР:** открой готовый файл **`drawio/01_main_pipeline_GOST.drawio`** в [app.diagrams.net](https://app.diagrams.net) — уже оформлен ГОСТ-фигурами (терминатор, процесс, решение-ромб, параллелограмм ввода/вывода, предопределённый процесс). Ниже Mermaid — для README/черновика.

```mermaid
flowchart TD
    A([Начало]) --> B[/Ввод: It, Ej, O, G, Bliq, профиль R/]
    B --> C[Этап 1. Предобработка:<br/>нормализация, фильтр активных целей]
    C --> D[Этап 2. Расчёт показателей<br/>CFt, Rt, Lt, Dt, BLR, Si]
    D --> E{Rt > 0?}
    E -- Нет --> F[/Дефицитный бюджет:<br/>структурный диагноз Fail-loud/]
    F --> Z([Конец])
    E -- Да --> G[Этап 4.0. Разовое закрытие близких<br/>целей из Bliq при Σ ≤ 0.5·Bliq]
    G --> H[Этап 4. Генерация 21 альтернативы<br/>stars-and-bars, шаг 20%]
    H --> I[/для каждой альтернативы a ∈ A/]
    I --> J[[Этап 4b. Avalanche + OCR<br/>см. схему 10]]
    J --> K[[Взвешенная Si<br/>см. схему 11]]
    K --> L[Пересчёт Rt', Lt', Dt']
    L --> M{Альтернативы<br/>кончились?}
    M -- Нет --> I
    M -- Да --> N[Этап 5. Фильтрация:<br/>Rt'≥0, Lt'≥Lmin, Dt'≤Dmax]
    N --> O{A' ≠ ∅?}
    O -- Нет --> P[/Нет допустимых:<br/>ослабить ограничения/]
    P --> Z
    O -- Да --> Q[Этап 6. Min-max нормализация +<br/>свёртка U a = Σ wk·критерий SAW]
    Q --> R[a* = argmax U a]
    R --> S[/Вывод: a*, top-3 + объяснения/]
    S --> Z
```

---

# 10. Блок-схема ГОСТ — Avalanche + OCR-фильтр

**Раздел ВКР:** алгоритмическое обеспечение ⭐. **Нотация:** ГОСТ 19.701-90.
**Что показывает:** распределение досрочки `x_obl` между кредитами по убыванию ставки с отсечением дешёвых долгов (NPV-правило).
**Рендер для ВКР:** **`drawio/02_avalanche_GOST.drawio`** в app.diagrams.net.

```mermaid
flowchart TD
    A([Начало: allocate_obligations_avalanche]) --> B[/Ввод: x_obl, обязательства O, r_bench/]
    B --> C{x_obl ≤ 0<br/>или O пуст?}
    C -- Да --> D[x_eff = 0, x_unused = x_obl]
    D --> Z([Конец])
    C -- Нет --> E[OCR-фильтр:<br/>targets = k : rk ≥ r_bench]
    E --> F{targets пуст?}
    F -- Да --> G[Досрочка невыгодна NPV-правило:<br/>x_eff = 0, x_unused → в цели]
    G --> Z
    F -- Нет --> H[Сортировать targets<br/>по убыванию ставки]
    H --> I[remaining = x_obl]
    I --> J[/для каждого loan в targets/]
    J --> K{remaining ≤ 0?}
    K -- Да --> R[x_eff = x_obl − remaining<br/>x_unused = remaining]
    K -- Нет --> L[apply = min remaining, остаток<br/>new_amount = остаток − apply<br/>new_payment пропорц. остатку<br/>remaining −= apply]
    L --> M{Кредиты<br/>кончились?}
    M -- Нет --> J
    M -- Да --> R
    R --> Z
```

---

# 11. Блок-схема ГОСТ — взвешенная обеспеченность целей Si

**Раздел ВКР:** алгоритмическое обеспечение ⭐. **Нотация:** ГОСТ 19.701-90.
**Что показывает:** расчёт Si с учётом категории цели (вес) и срочности (близость дедлайна) + распределение `x_goals`.
**Рендер для ВКР:** **`drawio/03_goals_si_GOST.drawio`** в app.diagrams.net.

```mermaid
flowchart TD
    A([Начало: calculate_goals_si]) --> B[/Ввод: x_goals, цели G, today/]
    B --> C{x_goals ≤ 0<br/>или G пуст?}
    C -- Да --> D[Si = 0, allocation = пусто]
    D --> Z([Конец])
    C -- Нет --> E[Для каждой цели с остатком > 0:<br/>urgency = max 1, 12/мес_до_дедлайна<br/>weight = вес категории<br/>priority = weight · urgency]
    E --> F[total_priority = Σ priority]
    F --> G{total_priority ≤ 0?}
    G -- Да --> D
    G -- Нет --> H[Для каждой цели:<br/>share = priority / total<br/>x_s = min x_goals·share, остаток<br/>накопить weighted_x, weighted_total]
    H --> I[Si = min weighted_x/weighted_total, 1.0]
    I --> J[/Вывод: Si, allocation/]
    J --> Z
```

---

# 12. Блок-схема ГОСТ — прогноз SES + Monte-Carlo

**Раздел ВКР:** алгоритмическое обеспечение ⭐. **Нотация:** ГОСТ 19.701-90.
**Что показывает:** точечный прогноз через экспоненциальное сглаживание + доверительный интервал [p10..p90] методом Монте-Карло с растущей σ.
**Рендер:** Mermaid → mermaid.live (готового draw.io нет — при необходимости перерисуй по этому черновику в ГОСТ-вид).

```mermaid
flowchart TD
    A([Начало: forecast_indicators]) --> B[/Ввод: balance, It, Ej, ΣP, горизонт H/]
    B --> C{Есть история<br/>≥ 2 точек?}
    C -- Нет --> D[build_history_from_current:<br/>синтетическая история 6 точек]
    C -- Да --> E[Использовать реальную историю]
    D --> F
    E --> F[SES α=0.3: точечный прогноз<br/>It+h, Ej+h, ΣP+h]
    F --> G[/для h = 1..H/]
    G --> H[CF_h = I_h − E_h<br/>Bt_h = Bt_h-1 + CF_h − P_h форм.35<br/>Rt_h, Lt_h, Dt_h]
    H --> I{h < H?}
    I -- Да --> G
    I -- Нет --> J[Monte-Carlo N=1000:<br/>σ h = σ0·√ 1+0.5h<br/>для каждого h → выборка]
    J --> K[Квантили p10, p50, p90<br/>= интервал 80% CI]
    K --> L[detect_trend:<br/>improving / stable / deteriorating]
    L --> M[/Вывод: прогноз + CI + тренд/]
    M --> Z([Конец])
```

---

# 13. UML Class — диаграмма классов

**Раздел ВКР:** реализация. **Нотация:** UML Class.
**Что показывает:** ORM-модели (`models.py`) + ключевые функциональные модули ядра как «классы-сервисы».
**Рендер:** Mermaid → mermaid.live. Для строгого UML с видимостью — PlantUML.

```mermaid
classDiagram
    class Transaction {
        +int id
        +float amount
        +str category
        +str type
        +datetime date
        +bool is_synced
    }
    class Obligation {
        +int id
        +str name
        +float amount
        +float interest_rate
        +int term
        +float monthly_payment
        +int payment_day
    }
    class Goal {
        +int id
        +str name
        +float target_amount
        +float current_amount
        +datetime deadline
        +str category
    }
    class LiquidAsset {
        +int id
        +str name
        +float amount
        +float interest_rate
        +str type
    }
    class UserPrefs {
        +int id
        +float l_min
        +int risk_tolerance
        +int horizon
        +float r_bench
    }

    class PlanningService {
        +run_planning() dict
    }
    class Metrics {
        +calculate_rt() float
        +calculate_lt() float
        +calculate_dt() float
        +calculate_blr() float
    }
    class Alternatives {
        +generate_alternatives() list
        +evaluate_alternative() dict
    }
    class Avalanche {
        +allocate_obligations_avalanche() tuple
    }
    class GoalsPriority {
        +calculate_goals_si() tuple
        +preallocate_from_bliq() tuple
    }
    class Ranking {
        +RISK_PROFILES dict
        +rank_alternatives() list
    }

    PlanningService ..> Metrics : использует
    PlanningService ..> Alternatives
    PlanningService ..> GoalsPriority
    PlanningService ..> Ranking
    Alternatives ..> Avalanche
    Alternatives ..> GoalsPriority
    PlanningService ..> Obligation : читает
    PlanningService ..> Goal
    PlanningService ..> Transaction
    PlanningService ..> UserPrefs
    PlanningService ..> LiquidAsset
```

---

# 14. State Machine — жизненный цикл альтернативы

**Раздел ВКР:** проектирование поведения. **Нотация:** UML State Machine.
**Что показывает:** как одна альтернатива проходит этапы от генерации до статуса «рекомендована/отклонена».
**Рендер:** Mermaid → mermaid.live / GitHub.

```mermaid
stateDiagram-v2
    [*] --> Generated: generate_alternatives()
    Generated --> Evaluated: evaluate_alternative()<br/>Avalanche + Si + пересчёт Rt'/Lt'/Dt'

    Evaluated --> Admissible: проходит фильтр<br/>Rt'≥0 ∧ Lt'≥Lmin ∧ Dt'≤Dmax
    Evaluated --> Rejected: нарушено ограничение

    Admissible --> Ranked: rank_alternatives()<br/>расчёт U(a) по SAW

    Ranked --> Recommended: U(a) максимальна<br/>(a* = первая в списке)
    Ranked --> NotSelected: U(a) не максимальна

    Recommended --> Explained: explain_alternative()<br/>gains / costs / insight

    Rejected --> [*]
    NotSelected --> [*]
    Explained --> [*]
```

---

# 15. Graphviz — граф зависимостей модулей

**Раздел ВКР:** реализация (приложение). **Нотация:** Graphviz DOT.
**Что показывает:** направленный граф импортов между пакетами проекта.
**Рендер:** [dreampuf.github.io/GraphvizOnline](https://dreampuf.github.io/GraphvizOnline) — вставь, получишь PNG/SVG.

```dot
digraph FINPILOT {
    rankdir=TB;
    node [shape=box, style="rounded,filled", fontname="Helvetica"];

    subgraph cluster_api {
        label="app/api"; style=filled; color="#dae8fc";
        router; routes_planning; routes_recommendation; routes_banks;
    }
    subgraph cluster_services {
        label="app/services"; style=filled; color="#d5e8d4";
        planning; pipeline; forecasting; statement_parser; bank_api;
    }
    subgraph cluster_core {
        label="app/core"; style=filled; color="#fff2cc";
        preprocessing; metrics; alternatives; avalanche;
        goals_priority; filtering; ranking; recommendation; forecast;
    }
    subgraph cluster_db {
        label="app/database"; style=filled; color="#f8cecc";
        crud; models; db;
    }

    router -> routes_planning -> planning;
    router -> routes_recommendation -> pipeline;
    router -> routes_banks -> statement_parser;
    routes_banks -> bank_api;
    routes_planning -> forecasting;

    planning -> preprocessing;
    planning -> metrics;
    planning -> alternatives;
    planning -> filtering;
    planning -> ranking;
    planning -> recommendation;
    planning -> goals_priority;
    pipeline -> preprocessing;
    pipeline -> metrics;
    pipeline -> recommendation;
    forecasting -> forecast;

    alternatives -> avalanche;
    alternatives -> goals_priority;

    planning -> crud -> models -> db;
    bank_api -> crud;
}
```

---

# 16. PDCA — цикл Деминга

**Методология:** PDCA (цикл непрерывного улучшения). **Раздел ВКР:** организация работ / улучшение продукта.
**Что показывает:** как итеративно улучшать качество рекомендаций FINPILOT.
**Рендер:** Mermaid → mermaid.live.

```mermaid
flowchart LR
    P["PLAN<br/>Гипотеза: новые веса профиля<br/>повысят релевантность.<br/>Метрика: % принятых рекомендаций"]
    D["DO<br/>Внедрить новые веса<br/>для 1 профиля риска<br/>на тестовой выборке"]
    C["CHECK<br/>Замерить долю принятых a*<br/>на 385 респондентах,<br/>сравнить с базой"]
    A["ACT<br/>Лучше → закрепить веса.<br/>Хуже → откатить,<br/>новая гипотеза"]

    P --> D --> C --> A --> P

    style P fill:#dae8fc,stroke:#6c8ebf
    style D fill:#d5e8d4,stroke:#82b366
    style C fill:#fff2cc,stroke:#d6b656
    style A fill:#f8cecc,stroke:#b85450
```

> **Привязка к FINPILOT:** параметры модели (`r_bench=0.14`, веса профилей, шаг дискретизации) — кандидаты на PDCA-итерации. Каждый прогон валидации на выборке респондентов = один виток Check.

---

# 17. BPMN 2.0 — бизнес-процесс получения рекомендации

**Методология:** BPMN 2.0 (= ISO/IEC 19510). **Раздел ВКР:** бизнес-процессы.
**Что показывает:** процесс «пользователь → рекомендация» с дорожками (кто что делает).
**Рендер для качества:** **Camunda Modeler** или **bpmn.io** (настоящие пулы и иконки). Mermaid ниже — упрощённо.

```mermaid
flowchart LR
    S((Старт)) --> T1[Пользователь вводит<br/>доходы, расходы, долги, цели]
    T1 --> G1{Данные<br/>полные?}
    G1 -- Нет --> T2[Запросить недостающее]
    T2 --> T1
    G1 -- Да --> T3[Система: расчёт показателей<br/>Rt, Lt, Dt, BLR]
    T3 --> G2{Rt > 0?}
    G2 -- Нет --> T4[Выдать диагноз<br/>дефицита бюджета]
    T4 --> E2((Конец))
    G2 -- Да --> T5[Система: генерация<br/>и фильтрация альтернатив]
    T5 --> T6[Система: ранжирование SAW<br/>+ объяснение top-3]
    T6 --> T7[Пользователь<br/>изучает рекомендацию]
    T7 --> E1((Конец))

    style S fill:#d5e8d4,stroke:#82b366
    style E1 fill:#f8cecc,stroke:#b85450
    style E2 fill:#f8cecc,stroke:#b85450
    style G1 fill:#fff2cc,stroke:#d6b656
    style G2 fill:#fff2cc,stroke:#d6b656
```

> **Для ВКР в BPMN-нотации:** перенеси в Camunda Modeler, раздели на 2 пула (Lane «Пользователь» и Lane «FINPILOT»), задачи пользователя пометь как User Task, системные — как Service Task. Шлюзы — эксклюзивные (X).

---

# 18. EPC — событийная цепочка планирования

**Методология:** EPC (ARIS, событийная цепочка процессов). **Раздел ВКР:** бизнес-процессы.
**Что показывает:** строгое чередование «событие → функция → событие». Распространена в SAP/корпоративном мире РФ.
**Рендер:** Mermaid → mermaid.live. Строгий EPC — в ARIS Express или Bizagi.

```mermaid
flowchart TD
    E1([Событие:<br/>данные введены]) --> F1[Функция:<br/>рассчитать показатели]
    F1 --> E2([Событие:<br/>показатели получены])
    E2 --> X1{XOR}
    X1 --> E3([Событие:<br/>Rt ≤ 0])
    X1 --> E4([Событие:<br/>Rt > 0])
    E3 --> F2[Функция:<br/>выдать диагноз дефицита]
    F2 --> E7([Событие:<br/>процесс завершён])
    E4 --> F3[Функция:<br/>сгенерировать альтернативы]
    F3 --> E5([Событие:<br/>21 альтернатива готова])
    E5 --> F4[Функция:<br/>фильтрация + ранжирование]
    F4 --> E6([Событие:<br/>a* определена])
    E6 --> F5[Функция:<br/>сформировать объяснение]
    F5 --> E7

    style E1 fill:#e1d5e7,stroke:#9673a6
    style E2 fill:#e1d5e7,stroke:#9673a6
    style E3 fill:#e1d5e7,stroke:#9673a6
    style E4 fill:#e1d5e7,stroke:#9673a6
    style E5 fill:#e1d5e7,stroke:#9673a6
    style E6 fill:#e1d5e7,stroke:#9673a6
    style E7 fill:#e1d5e7,stroke:#9673a6
    style X1 fill:#fff2cc,stroke:#d6b656
```

> **Нотация EPC:** шестиугольники-события (лиловые) и прямоугольники-функции (зелёные) строго чередуются. Оператор XOR = исключающее ветвление по знаку Rt.

---

# 19. VSM — поток создания ценности

**Методология:** Value Stream Mapping (Lean). **Раздел ВКР:** оптимизация процесса / Lean.
**Что показывает:** шаги обработки запроса + время каждого + где «потери» (ожидание).
**Рендер:** Mermaid → mermaid.live. Классический VSM с иконками — в Lucidchart/draw.io (шаблон VSM).

```mermaid
flowchart LR
    subgraph PT["Процессное время (Process Time)"]
        direction LR
        S1["Загрузка данных<br/>из БД<br/>~5 мс"]
        S2["Предобработка<br/>~1 мс"]
        S3["Расчёт<br/>показателей<br/>~0.5 мс"]
        S4["Генерация +<br/>оценка 21 альт.<br/>~1.7 мс"]
        S5["Фильтр +<br/>ранжирование<br/>~0.3 мс"]
        S6["Сериализация<br/>JSON ответа<br/>~2 мс"]
    end

    S1 -->|wait| S2 -->|wait| S3 --> S4 --> S5 -->|wait| S6

    PT --> SUM["Итого ~20 мс с БД и API<br/>чистый алгоритм ~1.7 мс<br/>Узкое место: I/O БД + сериализация"]

    style S4 fill:#fff2cc,stroke:#d6b656
    style SUM fill:#d5e8d4,stroke:#82b366
```

> **Вывод VSM:** ядро алгоритма (1.7 мс) — не узкое место. Основное время — на I/O базы и сериализацию. Точка оптимизации (Lean): кэширование запросов к БД, а не ускорение математики.

---

# 20. DMAIC — цикл снижения дефектов рекомендаций

**Методология:** DMAIC (Six Sigma). **Раздел ВКР:** управление качеством.
**Что показывает:** структурированный цикл устранения «дефектных» рекомендаций (отклонённых пользователем).
**Рендер:** Mermaid → mermaid.live.

```mermaid
flowchart LR
    D1["DEFINE<br/>Дефект = рекомендация a*,<br/>которую пользователь отверг.<br/>Цель: снизить долю отказов"]
    D2["MEASURE<br/>Замер на выборке<br/>385 респондентов:<br/>baseline % отказов"]
    D3["ANALYZE<br/>Причины: неверные веса?<br/>r_bench? нерелевантные<br/>категории целей?"]
    D4["IMPROVE<br/>Скорректировать параметры,<br/>прогнать на user-portraits,<br/>сравнить экспертную оценку"]
    D5["CONTROL<br/>Зафиксировать параметры,<br/>добавить мониторинг<br/>метрики в продакшн"]

    D1 --> D2 --> D3 --> D4 --> D5

    style D1 fill:#dae8fc,stroke:#6c8ebf
    style D2 fill:#d5e8d4,stroke:#82b366
    style D3 fill:#fff2cc,stroke:#d6b656
    style D4 fill:#ffe6cc,stroke:#d79b00
    style D5 fill:#f8cecc,stroke:#b85450
```

> **Привязка к FINPILOT:** в проекте уже есть артефакты для Measure/Analyze — `FINPILOT_6_User-Portraits_с_вычислениями` и `Экспертная_оценка_6_user-cases`. Это готовая база для DMAIC-цикла валидации алгоритма.

---

## Сводная таблица: диаграмма → раздел ВКР → инструмент

| № | Диаграмма | Нотация | Раздел ВКР | Инструмент рендера |
|---|---|---|---|---|
| 1 | Функциональный контекст | IDEF0 | Анализ области | Mermaid / Ramus |
| 2 | Варианты использования | UML Use Case | Требования | **PlantUML** |
| 3 | System Context | C4 L1 | Архитектура | Mermaid |
| 4 | Containers | C4 L2 | Архитектура | Mermaid |
| 5 | Components | C4 L3 | Архитектура | Mermaid |
| 6 | Схема БД | ER / DBML | Данные | **dbdiagram.io** |
| 7 | Цикл планирования | UML Sequence | Поведение | Mermaid |
| 8 | Импорт выписки | UML Sequence | Поведение | Mermaid |
| 9 | Главный pipeline ⭐ | ГОСТ 19.701-90 | Алгоритмы | **draw.io (файл)** |
| 10 | Avalanche + OCR ⭐ | ГОСТ 19.701-90 | Алгоритмы | **draw.io (файл)** |
| 11 | Взвешенная Si ⭐ | ГОСТ 19.701-90 | Алгоритмы | **draw.io (файл)** |
| 12 | SES + Monte-Carlo ⭐ | ГОСТ 19.701-90 | Алгоритмы | Mermaid |
| 13 | Классы | UML Class | Реализация | Mermaid / PlantUML |
| 14 | Жизненный цикл альтернативы | UML State Machine | Поведение | Mermaid |
| 15 | Граф зависимостей | Graphviz | Реализация | GraphvizOnline |
| 16 | PDCA | Цикл Деминга | Улучшение | Mermaid |
| 17 | Бизнес-процесс | BPMN 2.0 | Процессы | **Camunda/bpmn.io** |
| 18 | Событийная цепочка | EPC (ARIS) | Процессы | Mermaid / ARIS |
| 19 | Поток ценности | VSM (Lean) | Оптимизация | Mermaid / Lucidchart |
| 20 | Снижение дефектов | DMAIC (Six Sigma) | Качество | Mermaid |

---

## Файлы в комплекте

```
finpilot_diagrams/
├── FINPILOT_диаграммы.md          ← этот документ (все 20 диаграмм + код)
└── drawio/
    ├── 01_main_pipeline_GOST.drawio   ← открой в app.diagrams.net
    ├── 02_avalanche_GOST.drawio       ← открой в app.diagrams.net
    └── 03_goals_si_GOST.drawio        ← открой в app.diagrams.net
```

**Как открыть .drawio:** зайди на [app.diagrams.net](https://app.diagrams.net) → File → Open from → Device → выбери файл. Откроется готовая ГОСТ-схема, можно экспортировать в PNG/PDF/SVG (File → Export as) для вставки в ВКР.
