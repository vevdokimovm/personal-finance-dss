# Г33 — Инженерные стандарты: внешний бенчмарк (2026-09-17)

> **Состояние каналов (17.09.2026, замер в начале):** curl с браузерным UA — dora.dev 200, api.openalex.org 200, api.crossref.org 200, hh.ru 200, habr.com/ru/companies/tbank 200, **api.hh.ru 403** (API вакансий закрыт для анонимного запроса); r.jina.ai (без UA) → dora.dev 200. context7: `resolve-library-id FastAPI` → `/websites/fastapi_tiangolo` (работает). Exa (`mcp__exa__web_search_exa`) — работает, первый запрос вернул 5 результатов по DORA 2025. Подагентов не запускалось.

Правило файла: сырьё пишется по ходу, после каждого пункта. Цитаты — дословно на языке источника.

---

## П1. Шкалы зрелости доставки: DORA / Accelerate / SPACE

### DORA 2025 (Google), распределение ответов ~5000 респондентов
Источник: DORA 2025 State of AI-assisted Software Development (PDF в зеркале Thoughtworks: https://www.thoughtworks.com/content/dam/thoughtworks/documents/report/tw_report_state_of_ai_assisted_software_development_2025.pdf ; анонс https://cloud.google.com/blog/products/ai-machine-learning/announcing-the-2025-dora-report , 23.09.2025).

Дословно, определения (пять метрик с 2025 г. — добавлен rework rate):
- «Lead time for changes — The amount of time it takes for a change to go from committed to version control to deployed in production.»
- «Change fail rate — The ratio of deployments that require immediate intervention following a deployment.»
- «Deployment frequency — The number of deployments over a given period or the time between deployments.»
- «Rework rate — The ratio of deployments that are unplanned but happen as a result of an incident in production.»
- «Failed deployment recovery time — The time it takes to recover from a deployment that fails and requires immediate intervention.»

Важная смена рамки: с 2025 г. DORA **отказалась от кластеров low/medium/high/elite** в пользу семи «профилей команд»: «Simple software delivery metrics alone aren't sufficient… we conducted a cluster analysis that reveals seven common team profiles». Значит, «элита = деплой по требованию» теперь не официальная шкала, а распределение (перцентили) ниже.

Распределение (дословно из таблиц отчёта, «% at level | Top %»):
- Deployment frequency: «On demand (multiple deploys per day) 16.2% | 16.2%»; «Between once per day and once per week 21.9% | 44.6%»; «Between once per week and once per month 31.5% | 76.1%».
- Lead time: «Less than one hour 9.4%»; «Less than one day 15% | 24.4%»; «Between one day and one week 31.9% | 56.4%».
- Recovery time: «Less than one hour 21.3%»; «Less than one day 35.3% | 56.5%».
- Change failure rate: «0%-2% 8.5%»; «2%-4% 8.1% | 16.7%»; «4%-8% 19.6% | 36.2%»; «8%-16% 26% | 62.2%».

Прочтение для нас: верхний квартиль — деплой хотя бы раз в день–неделю, lead time < 1 дня, восстановление < 1 часа, CFR < 4–8 %. Ключевой вывод DORA 2025 (дословно из анонса): «Without robust control systems, like strong automated testing, mature version control practices, and fast feedback loops, an increase in change volume leads to instability». Для проекта, где большая часть кода пишется ИИ-ассистентом, это прямо про нас: DORA 2024 — «an estimated 1.5% reduction in software delivery throughput and an estimated 7.2% increase in software delivery instability for every 25% increase in AI adoption».

**Что у нас:** продакшена нет (запуск осенью 2026) → deployment frequency, CFR, recovery time **не измеримы в принципе**; lead time «коммит → прод» тоже. Измеримо сейчас только «коммит → зелёный CI». Вывод: DORA применима как **целевая планка на момент запуска**, а не как оценка сейчас.

---

## П0. Что у нас на самом деле (чтение репозитория, 17.09.2026, без запуска инструментов)

| Область | Факт | Файл |
|---|---|---|
| CI | 6 джоб: `preflight` (блок.), `core` (покрытие ядра ≥95 %), `fast` (матрица SQLite+PG16, ≥90 %), `lint` flake8+mypy, `pylint` (continue-on-error), `full` на тегах (мультибраузер E2E, визуал, a11y, **bandit, pip-audit, locust smoke 30 с**), `deep` еженедельно (стресс-property + **mutmut**) | `.github/workflows/ci.yml` |
| Мутации | Пилот Р1.0 16.09.2026 на 3 модулях ядра, балл **68,7 %** (WATCHLOG стр. 566). В CI `mutmut run … || true` — **балл нигде не гейтит** | `pyproject.toml [tool.mutmut]`, `ci.yml` |
| Линт | flake8 7.1, pylint 3.2.7, **mypy 1.3.0 (май 2023 — на 3+ года старше остального стека)**, ruff настроен в `pyproject.toml` (E,F,W,I), но **в `requirements-dev.txt` его нет** (постановка Г33 ошибочно числит его установленным) | `requirements-dev.txt`, `pyproject.toml`, `.pre-commit-config.yaml` |
| Pre-commit | гоняет **весь pytest и coverage на каждый коммит** (при полном прогоне ~25 мин) | `.pre-commit-config.yaml` |
| Контроль зависимостей | пины `==` в requirements; **нет Dependabot/Renovate** (`.github/` содержит только `workflows/`); pip-audit только на тегах | `.github/` |
| Наблюдаемость | `sentry-sdk[fastapi]` есть; `RequestLoggingMiddleware` с X-Request-ID; **нет OpenTelemetry, нет структурных (JSON) логов** — grep по `opentelemetry|structlog|JSONFormatter` в `app/` пусто; метрик Prometheus нет | `app/middleware.py`, `docs/slo.md` |
| Rate limit | свой middleware (INFRA-12), 429 | `app/middleware.py` |
| Идемпотентность | grep `idempoten` по `app/` — **пусто** | — |
| Фоновые задачи | FastAPI `BackgroundTasks` (почта), cron-скрипты на хосте; брокера очереди нет | `app/services/email_dispatch.py`, `scripts/cron_*.sh` |
| Кэш | БД-кэш ставки ЦБ, `lru_cache` в категоризации; Redis нет | `app/core/categorization.py` |
| Бэкап | `backup_db.sh`, `restore_db.sh`, **`backup_verify.sh`** (проверка восстановления есть) | `scripts/`, `docs/backup_restore.md` |
| Асинхронность | 8 `async def` против ~676 синхронных `def` в `app/` — по сути синхронный стек | `app/` |
| Деньги | `Decimal` встречается в 11 файлах, `Float`/`float(` в 36 (дефект класса Г20) | `app/` |
| API | OpenAPI → `@hey-api/openapi-ts` генерирует типы фронта; версия в пути только у B2B `/v1` | `frontend/openapi-ts.config.ts` |
| Фронт | React 19.2, TS 5.9, Vite 8, TanStack Router/Query, Zustand 5, Vitest 4, ESLint 10, Playwright | `frontend/package.json` |
| Деплой | один VPS, compose: nginx(TLS)+gunicorn+PG16, healthcheck, `restart: unless-stopped` | `docker-compose.prod.yml` |
| SLO | цели 99,5 %, p95 по классам — **измерение не заведено** (сами пишем «фиксируем факт на Locust», locust гоняется 30 с на 20 пользователях) | `docs/slo.md` |
| ADR | 17 ADR + шаблон | `docs/reports/adr/` |
| Слои | `.importlinter` **нет** — соблюдение слоёв машинно не проверяется | — |

🔴 **Находка о самом документе:** `docs/it_stack.md` §2–3 **устарел**: пишет «FastAPI 0.110», «Uvicorn 0.29», «SQLAlchemy 2.0.30», «Тесты (`tests/` пуст)», «нет Alembic», «нет Docker», «нет CI/CD». Фактически: FastAPI 0.136.3, SQLAlchemy 2.0.50, 201 тестовый файл, Alembic, Docker, 6 джоб CI. Документ, который должен быть ответом на «какой у нас стек», вводит в заблуждение. Цена правки — 1–2 ч.

---

## П2 + Часть C. Нормы метрик качества кода и тестов (с первоисточниками)

### C1. Покрытие строк (coverage)
1. **Google, «Code Coverage Best Practices»** (Arguelles, Ivanković, Bender, 07.08.2020, https://testing.googleblog.com/2020/08/code-coverage-best-practices.html , добыто через Exa `web_fetch_exa`; `WebFetch` и r.jina.ai отдали только обвязку страницы без тела):
   - «at Google we offer the general guidelines of 60% as "acceptable", 75% as "commendable" and 90% as "exemplary."»
   - «While project wide goals above 90% are most likely not worth it, per-commit coverage goals of 99% are reasonable, and 90% is a good lower threshold.»
   - «We should not be obsessing on how to get from 90% code coverage to 95%. The gains of increasing code coverage beyond a certain point are logarithmic.»
   - «Code coverage does not guarantee that the covered lines or branches have been tested correctly, it just guarantees that they have been executed by a test… A better technique to assess whether you're adequately exercising the lines your tests cover, and adequately asserting on failures, is mutation testing.»
   - «The level of testing you want/need for a set of code should be a function of (a) business impact/criticality of the code…»
2. **SonarQube, встроенный гейт «Sonar way»** (https://docs.sonarsource.com/sonarqube-community-build/quality-standards-administration/managing-quality-gates/introduction-to-quality-gates.md , curl 200; сверено со страницей, а не только с ответом их ассистента): «The Sonar way quality gate has four conditions: … New code test coverage is greater than or equal to 80.0% · Duplication in the new code is less than or equal to 3.0%»; «The conditions on duplication are ignored until the *number of new lines* is at least 20.» Важно: гейт — на **новый** код, не на весь проект.
3. **Inozemtseva & Holmes, ICSE 2014**, doi:10.1145/2568225.2568271 (411 цитирований по OpenAlex; PDF автора https://cs.uwaterloo.ca/~rtholmes/papers/icse_2014_inozemtseva.pdf , через Exa): «we generated 31,000 test suites for five systems consisting of up to 724,000 lines of source code… there is a low to moderate correlation between coverage and effectiveness when the number of test cases in the suite is controlled for… coverage, while useful for identifying under-tested parts of a program, should not be used as a quality target because it is not a good indicator of test suite effectiveness.» И: «we currently feel that mutation score may be a good substitute for coverage in this context».

**Что это значит у нас.** Аналогия: покрытие — это «сколько комнат обошёл охранник», а не «проверил ли он замки». Наш гейт ≥90 % на весь проект = «exemplary» по шкале Google, т.е. **не мало, а на верхней границе**, и выше него Google прямо не советует тянуть. Ядро ≥95 % оправдано тезисом «(a) business impact» — это сходится с нашим обоснованием в `ci.yml`. Разрыв не в числе, а в **виде гейта**: индустрия (Sonar, Google «per-commit… 99%… 90% lower threshold») гейтит **покрытие нового кода/дельту**, мы — абсолют по дереву. Абсолютный гейт позволяет новому модулю быть покрытым на 60 %, если старый код держит среднее. Цена перехода — `diff-cover` в CI, 2–3 ч.

### C2. Мутационный балл (mutation score)
1. **Stryker** (стандарт де-факто для JS/TS, https://stryker-mutator.io/docs/stryker-js/configuration/ ): пороги по умолчанию «{ high: 80, low: 60, break: null }»; «mutation score >= high: Awesome!», «mutation score < low: Danger!», и `break: null` — «the build will never fail based on mutation score thresholds». То есть даже инструмент по умолчанию **не валит сборку** по баллу.
2. **Google, Petrović et al., «Practical Mutation Testing at Scale: A view from Google», IEEE TSE 2021**, doi:10.1109/TSE.2021.3107634 (arXiv 2102.11378, PDF 200 → pdftotext): «it remains infeasibly expensive to compute the absolute mutation score for the codebase… we were also unable to find a good way to surface it to the developers in an actionable way, as it is neither concrete nor actionable, and it does not guide testing.» Их подход: «Mutation testing is done incrementally, mutating only changed code during code review»; «developers at Google initially classified 85% of reported mutants as unproductive»; фильтрация «improved the ratio of productive mutants from 15% to 89%». Масштаб: «more than 24,000 developers on more than 1,000 projects».
3. **Papadakis et al., ICSE 2018**, doi:10.1145/3180155.3180183: «all correlations between mutation scores and real fault detection are weak when controlling for test suite size… mutants provide good guidance for improving the fault detection of test suites, but their correlation with fault detection are weak.»

**Норма, честно:** общепризнанного «порога мутационного балла» **нет**. Есть (а) дефолт Stryker 60/80 как цветовая шкала, (б) позиция Google — абсолютный балл неинформативен, ценны **выжившие мутанты на изменённом коде в ревью**. Наши 68,7 % на трёх модулях ядра — «жёлтая зона» по Stryker. Разумная цель для ядра денежного расчёта — ≥80 % (зелёная зона), но **главное — список выживших мутантов как задачи на тесты**, а не число. Наш `|| true` в `deep` — правильно для балла, неправильно для процесса: выжившие мутанты никуда не попадают. Цена: 3–4 ч — выгрузка `mutmut results` в артефакт + «не хуже прошлого» (ratchet) на ядре.

### C3. Цикломатическая сложность (cyclomatic complexity, CC)
1. **NIST SP 500-235 «Structured Testing» (Watson & McCabe, 1996)**, doi:10.6028/NIST.SP.500-235 (PDF nvlpubs 200 → pdftotext, стр. текста ~1938): «The original limit of 10 as proposed by McCabe has significant supporting evidence, but limits as high as 15 have been used successfully as well. Limits over 10 should be reserved for projects that have several operational advantages over typical projects, for example experienced staff, formal design, a modern programming language, structured programming, code walkthroughs, and a comprehensive test plan.»
2. **radon** (стандартный инструмент Python, https://radon.readthedocs.io/en/latest/commandline.html ): «1 - 5 | A | low - simple block», «6 - 10 | B | low - well structured and stable block», «11 - 20 | C | moderate - slightly complex block», «21 - 30 | D | more than moderate», «31 - 40 | E | high - complex block, alarming», «41+ | F | very high - error-prone, unstable block». Индекс сопровождаемости (MI): «100 - 20 | A | Very high», «19 - 10 | B | Medium», «9 - 0 | C | Extremely low».
3. **SonarSource sonar-python**, `FunctionComplexityCheck.java` (github.com/SonarSource/sonar-python, через Exa): «private static final int DEFAULT_MAXIMUM_FUNCTION_COMPLEXITY_THRESHOLD = 15;». Когнитивная сложность — правило S3776, «raises an issue when the code cognitive complexity of a function is above a certain threshold» (значение порога со страницы правила не снято — страница рендерится JS; в оригинальной спецификации Sonar это тоже 15, но дословной цитаты у меня нет).

**Норма:** функция ≤10 (McCabe/NIST), допустимо ≤15 при сильном тест-плане — это как раз наш случай (TDD, 90 %). Предлагаемый порог для Р1: **CC ≤ 10 предупреждение, ≤ 15 блок (`xenon --max-absolute C`… т.е. ранг C=11–20 уже подозрителен; жёстко — ни одной функции ранга D и хуже)**. Наш СТАНДАРТ «функции не длиннее 50 строк» — близкий, но другой показатель.

### C4. Дублирование
Норма рынка — **≤3 % на новом коде** (Sonar way, выше), с минимумом 20 новых строк. Академического «порога» не нашёл и не выдумываю; 3 % — это дефолт самого распространённого коммерческого инструмента, не закон природы.

### Поправки к срезу П0 (после чтения `app/`)
- **Структурные логи ЕСТЬ**: `app/logging_config.py` — «JSON-логи в stdout — машиночитаемо и готово под агрегацию (Loki/ELK/Datadog)». Строка таблицы П0 «нет структурных (JSON) логов» неверна — grep искал не те имена. Нет — **сборщика** логов (Loki и т.п.) и OpenTelemetry.
- **i18n есть** (`app/i18n.py`), **A/B-контур есть** (`app/services/experiments.py`, `tests/test_experiment_results_contract.py`).
- **Контрактные тесты** — это наши тесты формы ответа (`tests/test_*_contract.py`, ≥10 файлов), не consumer-driven (Pact) и не генеративные по OpenAPI (Schemathesis). Для монолита с одним своим фронтом Pact не нужен (см. ниже).
- **Обратимость миграций проверяется** (`tests/test_migration_reversibility.py`); проверки дрейфа «модели ↔ миграции» (`alembic check`) grep не нашёл.
- **Sentry и ПДн** — разобрано в Г32 (`product_security_2026-09-17.md` стр. 308–334: `include_local_variables=True` по умолчанию, трансграничная передача по 152-ФЗ, если не самохост). Здесь не дублирую.

### П2 (остаток). Форма набора тестов
- **Пирамида, Google** (Mike Wacker, 22.04.2015, https://testing.googleblog.com/2015/04/just-say-no-to-more-end-to-end-tests.html , r.jina.ai 200): «As a good first guess, Google often suggests a 70/20/10 split: 70% unit tests, 20% integration tests, and 10% end-to-end tests. The exact mix will be different for each team, but in general, it should retain that pyramid shape.» Антипаттерн: «Inverted pyramid/ice cream cone. The team relies primarily on end-to-end tests».
- **Property-based** — у нас `hypothesis` + стресс-прогон в `deep`. Для денежного ядра это выше типичной рыночной практики (в вакансиях РФ-банков ниже его не встретил — см. П7).
- **Нагрузочное** — locust 30 с на 20 пользователях только на тегах. SLO-цели (`docs/slo.md`: 50 RPS, 10 параллельных `calculate`) этим прогоном **не проверяются** — профиль в 2,5 раза меньше цели и без порогов p95 как условия провала.
- **Контракт API** — `@hey-api/openapi-ts` из `openapi.json` + `api-contract-guard`. Отраслевой следующий шаг для монолита — генеративный фаззинг по схеме (Schemathesis), не Pact (Pact решает проблему независимых команд-потребителей, которой у нас нет).

**Вывод П2:** по составу видов тестов мы **выше** медианы; разрыв — (1) нагрузка не сверена с собственными SLO, (2) мутационный результат не превращается в задачи, (3) покрытие гейтится абсолютом, а не по новому коду. Соотношение unit/integration/e2e — замерить в Р1 (кол-во тестов по маркерам).

---

## П3. CI/CD и релизы

Нормы:
- **12-factor** (Adam Wiggins, https://12factor.net/ , Exa): методология для SaaS, которая «Minimize divergence between development and production, enabling continuous deployment» и «Use declarative formats for setup automation». Фактор X (dev/prod parity) — прямо против нашей схемы «локально SQLite, прод PostgreSQL»; мы компенсируем матрицей в CI, что является признанной полумерой.
- **Миграции без простоя — expand/contract** (Danilo Sato, martinfowler.com/bliki/ParallelChange.html , Exa): «Parallel change, also known as expand and contract, is a pattern to implement backward-incompatible changes to an interface in a safe manner, by breaking the change into three distinct phases: expand, migrate, and contract.»; «Database refactoring: … Most database refactorings follow the parallel change pattern»; «deployment techniques such as canary releases and BlueGreenDeployment are applications of the parallel change pattern».
- **Alembic о самом себе** (https://alembic.sqlalchemy.org/en/latest/autogenerate.html , r.jina.ai 200): «It is critical to note that **autogenerate is not intended to be perfect**. It is _always_ necessary to manually review and correct the **candidate migrations** that autogenerate produces.»
- **DORA** (П1): верхний квартиль деплоит минимум раз в неделю и восстанавливается < 1 ч — это требует **отката одной командой**.

Что у нас: preflight + матрица + ядро блокируют; линт — `lint` джоба (flake8+mypy) без `continue-on-error`, т.е. **блокирует**, а `docs/engineering_practices.md` §3 пишет «lint — ИНФОРМАЦИОННЫЙ (continue-on-error). flake8 / mypy / pylint» — **документ расходится с CI** (информационный теперь только pylint). SemVer + CHANGELOG + теги — есть. Один VPS, compose, `restart: unless-stopped`.

Норма для нашего размера (моё суждение на основе источников выше, помечено как суждение):
| Практика | Норма для соло-SaaS | У нас | Вердикт |
|---|---|---|---|
| Блокирующие тесты + линт на PR | да | да | ок |
| Отдельный staging | желательно (дешёвый) | `docs/sandbox_runbook.md` есть | ок/проверить |
| Expand/contract для схемы | да, с первого пользователя | не формализовано | **разрыв**, 2 ч на правило в `CONTRIBUTING` + пункт в `finpilot-alembic-migration` |
| `alembic check` (дрейф моделей) в CI | да, дёшево | нет | **разрыв**, 1 ч |
| Откат одной командой (предыдущий образ по тегу) | да | не нашёл документированного | проверить в `docs/DEPLOY.md`, 2–4 ч |
| Blue-green/canary | **нет** на одном VPS | нет | избыточно |
| Фича-флаги как сервис (LaunchDarkly/Unleash) | **нет**; конфиг-флаг достаточно | A/B-контур свой | избыточно |
| Обновление зависимостей ботом | да (бесплатно) | нет Dependabot/Renovate; mypy 1.3.0 (2023) | **разрыв**, 1 ч |
| pip-audit на каждый PR | да (секунды) | только на тегах | **разрыв**, 0,5 ч |
| Весь pytest в pre-commit | **нет** (25 мин на коммит) | да, в `.pre-commit-config.yaml` | **избыточно/вредно** |

---

## П4. 🔴 Наблюдаемость

Нормы:
- **Google SRE Book, «Monitoring Distributed Systems»** (https://sre.google/sre-book/monitoring-distributed-systems/ , r.jina.ai 200): «The four golden signals of monitoring are latency, traffic, errors, and saturation. If you can only measure four metrics of your user-facing system, focus on these four.» и «If you measure all four golden signals and page a human when one signal is problematic… your service will be at least decently covered by monitoring.»
- **Google SRE Workbook, «Implementing SLOs»** (https://sre.google/workbook/implementing-slos/ ): «the SLO is a target percentage and the error budget is 100% minus the SLO»; условие работы: «The organization has committed to using the error budget for decision making and prioritizing. This commitment is formalized in an error budget policy.»; «making all of your SLIs follow a consistent style… numerator, denominator, and threshold».
- **OpenTelemetry Python** (context7 `/websites/opentelemetry_io`, страница opentelemetry.io/docs/languages/python): «Currently, tracing and metrics components are considered stable, while logging support is in the development phase.» Инструментирование FastAPI — одна строка (context7 `/open-telemetry/opentelemetry-python-contrib`): `FastAPIInstrumentor.instrument_app(app)`, плюс `opentelemetry-instrumentation-sqlalchemy`.
- **Цены** (17.09.2026): Sentry Developer «For solo devs working on small projects — Free $0 — Limited to one user — Error Monitoring and Tracing — Alerts and notifications via email»; Team «$26/mo» (https://sentry.io/pricing/). **GlitchTip** — «compatible with Sentry client SDKs, but easier to run… open source… Run it on your server» (https://glitchtip.com/) — это путь самохоста в РФ-ЦОД, закрывающий 152-ФЗ-вопрос из Г32 без смены SDK.

Что у нас: JSON-логи в stdout, X-Request-ID, Sentry (опционально по DSN), цели SLO в документе. **Нет:** сбора метрик (Prometheus/OTel), дашборда четырёх сигналов, алертов, SLI-формул (числитель/знаменатель), политики бюджета ошибок кроме фразы «сгорел — фичи стоп», внешнего аптайм-пинга.

**Что значит у нас.** Аналогия: SLO без измерения — спидометр, нарисованный на приборной панели. Минимум для соло-SaaS на одном VPS (моё суждение): (1) внешний аптайм-чек `/health` (бесплатно — UptimeRobot/Healthchecks; или GlitchTip uptime) — **1 ч**; (2) GlitchTip самохост или Sentry с `before_send` — **3–4 ч** (VPS-ресурсы ~0 ₽ сверх текущего, если в том же compose; GlitchTip требует PG+Redis/Valkey); (3) метрики четырёх сигналов: `prometheus-fastapi-instrumentator` или OTel → Prometheus+Grafana в compose — **6–10 ч**, +~0,5–1 ГБ RAM на VPS; (4) SLI-формулы и алерт на выгорание бюджета — **2–3 ч**. Полный OTel-трейсинг с коллектором для монолита из одного процесса — **избыточен** на старте: трасса в монолите почти не добавляет к логу с request-id.

Уточнение к П3: `lint` в CI называется «Линтеры (flake8, mypy — блокируют)» и `continue-on-error` не имеет → блокирует (проверено `awk` по `ci.yml`). `docs/engineering_practices.md` §3 утверждает обратное — **документ устарел**. Процедуры отката в `docs/DEPLOY.md` grep («откат|rollback») не нашёл.

---

## П5 + Часть B. Архитектурные решения против внешних шкал

### B1. Форма ADR
- **Nygard, «Documenting Architecture Decisions»** (15.11.2011, https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions , r.jina.ai 200): разделы **Title, Context, Decision, Status, Consequences**. «Status: A decision may be "proposed"… or "accepted"… If a later ADR changes or reverses a decision, it may be marked as "deprecated" or "superseded" with a reference to its replacement.» «Consequences… All consequences should be listed here, not just the "positive" ones.» «The whole document should be one or two pages long.»
- **MADR 4.x** (https://adr.github.io/madr/ ): «Context and Problem Statement», «Decision Drivers» (опц.), «Considered Options», «Decision Outcome — Chosen option: "…", because …», «Consequences — Good, because… / Bad, because…», **«Confirmation — Describe how the implementation of/compliance with the ADR can/will be confirmed… E.g., a design/code review or a test with a library such as ArchUnit can help validate this.»**, «Pros and Cons of the Options».

Наш шаблон (`docs/reports/adr/adr_template.md`): Контекст · Решение · Альтернативы · Последствия + строка «Дата · Статус · Вахта/Батч». Все 17 ADR имеют статус; ADR-005 держит его разделом. **Сверка:** по Nygard — полное соответствие (+ у нас есть альтернативы, которых у Nygard нет). По MADR не хватает двух вещей: **Decision Drivers** (по каким критериям выбирали) и **Confirmation** (как машинно проверить, что решение соблюдается). Второе — главное: ADR-004 «слой данных», ADR-005 «где живёт движок» — это решения, которые можно проверить `import-linter`, но проверки нет. Статуса `superseded` ни у одного ADR нет — при 17 решениях за 2,5 месяца и сменах канона это подозрительно (либо ничего не пересматривалось, либо пересмотры не отражены). Цена: +раздел «Проверка» в шаблон, 0,5 ч; ретро-проход по 17 ADR, 2–3 ч.

### B2. Модульный монолит и слои
- **Shopify Engineering** («Deconstructing the Monolith», https://shopify.engineering/deconstructing-monolith-designing-software-maximizes-developer-productivity ): «We chose to evolve Shopify into a modular monolith, meaning that we would keep all of the code in one codebase, but ensure that boundaries were defined and respected between different components.»; «a different solution will make sense for an app depending on what phase of its growth it is in»; «We wanted a solution that increased modularity without increasing the number of deployment units».
- **import-linter** (https://import-linter.readthedocs.io/en/stable/ ): контракты типов forbidden / protected / **layers**, конфиг `[importlinter:contract:…]`.

У нас: монолит FastAPI со слоями `api/ services/ core/ database/ schemas/ ingestion/` (листинг `app/`). Для соло-SaaS до первой тысячи пользователей монолит — **норма**, микросервисы были бы избыточны (Shopify пришёл к модульному монолиту при многотысячной команде). **Разрыв:** границы «defined», но не «respected» машинно — `.importlinter` нет. Цена: контракт `layers` (api → services → core; core не импортирует api/database) — 1–2 ч + исправление найденных нарушений (неизвестно, мерит Р1).

### B3. Контракт API, идемпотентность, версии, пагинация
- **Идемпотентность — IETF draft-ietf-httpapi-idempotency-key-header-07** (15.10.2025, истекает 18.04.2026; статус — Internet-Draft, Standards Track, **ещё не RFC**; https://datatracker.ietf.org/doc/html/draft-ietf-httpapi-idempotency-key-header/ ): «The HTTP Idempotency-Key request header field can be used to make non-idempotent HTTP methods such as POST or PATCH fault-tolerant.»; «It is RECOMMENDED that a UUID [RFC4122] or a similar random identifier be used as an idempotency key.»; повтор с другим телом → «HTTP 422»; повтор во время обработки → «HTTP 409».
  У нас: grep `idempoten` по `app/` — пусто. **Где это важно у нас:** импорт выписки (двойной клик/ретрай сети = дубли транзакций → неверный расчёт свободного потока), создание долга/цели, B2B `/v1/analyze` (у внешнего клиента ретраи неизбежны). Цена: middleware + таблица ключей с TTL — 4–6 ч; для импорта выписки дешевле дедупликация по хешу файла (1–2 ч), если её ещё нет (проверить в Р1).
- **Контракт как источник правды:** OpenAPI → `@hey-api/openapi-ts` → типы фронта + `api-contract-guard` — это и есть рыночная практика «schema-first/code-first с генерацией клиента». Норма соблюдена.
- **Версионирование:** B2B под `/v1` (внешний контракт) — норма; внутренний API для собственного SPA без версии — тоже норма, пока фронт и бэк выкатываются вместе.
- **Деньги:** Decimal-дефект — Г20, не дублирую.

### B4. Шкала ISO/IEC 25010
- **ISO/IEC 25010:2023** (превью iTeh, https://cdn.standards.iteh.ai/samples/78176/13ff8ea97048443f99318920757df124/ISO-IEC-25010-2023.pdf ; карточка IEC https://webstore.iec.ch/en/publication/90024 , CHF 155): «The product quality model is composed of nine characteristics»; «Safety has been added as a quality characteristic with subcharacteristics, i.e. operational constraint, risk identification, fail safe, hazard warning and safe integration.— Usability and portability have [been] replaced with interaction capability and flexibility respectively.— Inclusivity and self-descriptiveness, resistance, and scalability have been added…»
- **В РФ действует ГОСТ Р ИСО/МЭК 25010-2015** (приказ Росстандарта от 29.05.2015 № 464-ст; https://allgosts.ru/35/080/gost_r_iso!mek_25010-2015), идентичный **старой** ISO/IEC 25010:2011: «сводит свойства качества системы/программного продукта к восьми характеристикам… функциональная пригодность, уровень производительности, совместимость, удобство пользования, надежность, защищенность, сопровождаемость и переносимость». Т.е. ГОСТ на одну редакцию отстаёт от ISO.

Сверка по 25010:2023 (моё суждение, по фактам П0):
| Характеристика | Что у нас подтверждает | Слабое место |
|---|---|---|
| Functional suitability (корректность) | канон модели, ядро ≥95 %, property-тесты, мутации | Decimal (Г20); мутации 68,7 % |
| Performance efficiency | SLO в документе | **не измерено** под целевой нагрузкой |
| Compatibility | OpenAPI, `/v1` | — |
| Interaction capability | стандарты UI, a11y-аудит, i18n | вне Г33 |
| Reliability (availability, fault tolerance, recoverability) | деградации, healthcheck, backup+verify | один VPS; отката нет в DEPLOY; нет аптайм-мониторинга |
| Security | Г32 | Г32 |
| Maintainability (modularity, analysability, testability) | слои, ADR, тесты | **сложность/дублирование/слои не мерены** (Р1) |
| Flexibility (scalability) | Docker, PG | синхронный стек, один процесс-хост |
| **Safety** (новая: risk identification, fail safe, hazard warning) | fail-loud, кризисный режим, инварианты Rt≥0, ПДН≤0,40 | для продукта, советующего о деньгах, это самая релевантная из новых характеристик — **у нас она де-факто есть, но не названа** |

---

## П8. Стандарты и своды: что применимо соло-команде

- **ГОСТ Р 56939-2024** «Защита информации. Разработка безопасного программного обеспечения. Общие требования» — действует с 20.12.2024 (приказ Росстандарта от 24.10.2024 № 1504-ст; https://base.garant.ru/410749342/ , https://protect.gost.ru/gost/details/f3818925-a96f-4f55-96e9-46b44720ee64 ). Дословно п. 4.14: «Конкретная совокупность процессов разработки безопасного ПО, подлежащая реализации разработчиком ПО, определяется требованиями нормативных правовых актов, национальных и отраслевых стандартов, технических заданий…» — т.е. **обязателен только там, где на него сослались** (сертификация ФСТЭК, госзаказ). П. 4.13: «средой разработки ПО должны быть обеспечены контроль версий разрабатываемого ПО, непрерывная интеграция разрабатываемого ПО, управление задачами, в том числе по отслеживанию ошибок в коде ПО». По перечню PVS-Studio (https://pvs-studio.ru/ru/pvs-studio/rbpo/): «Стандарт описывает 25 процессов», среди них «10. Статический анализ исходного кода», «16. Использование инструментов композиционного анализа», «18. Функциональное тестирование», «19. Нефункциональное тестирование», «23. Реагирование на информацию об уязвимостях». **Г32 этот ГОСТ не упоминает** (grep по `product_security_2026-09-17.md` пуст) — это пробел, важный для B2B-продаж банкам: банк-партнёр может потребовать соответствия РБПО. Для нас сейчас: не сертифицироваться, но разложить имеющееся (bandit = п.10, pip-audit = п.16, SECURITY.md = п.23) по номерам процессов — 2–3 ч, и это превращается в аргумент для B2B.
- **OWASP SAMM** (https://owaspsamm.org/model/ ): «OWASP SAMM defines five business functions and fifteen security practices» — Governance, Design, Implementation, Verification, Operations. Самооценка бесплатна (таблица), 3–4 ч; применимо соло, пересекается с ГОСТ Р 56939.
- **ГОСТ Р ИСО/МЭК 25010-2015** — см. B4; применим как словарь для раздела «качество» в B2B-документации и ТЗ, затрат не требует.
- **ГОСТ Р ИСО/МЭК 12207** и **ISO 27001** — процессные/управленческие своды для организаций; соло-разработчику до B2B-сделки с требованием сертификата — **избыточны**. 12207 и 27001 первоисточниками в этой сессии не открывал (платные), вывод основан на их назначении, известном по названиям и области применения, — помечаю как непроверенный дословно.

---

## П7. 🔴 Планка РФ-рынка: дословные требования к бэкенду (вакансии, выдача Exa 17.09.2026)

Оговорка о методе: api.hh.ru отдаёт 403 анонимно (замер в шапке), поэтому вакансии взяты через Exa со страниц карьерных сайтов банков и зеркал hh. Даты — дата публикации, где она видна; где не видна — «дата не указана, страница живая 17.09.2026».

### Т-Банк
1. **«Python-разработчик»**, hh.ru/vacancy/136346136, опубликовано **18.08.2026** (та же формулировка на tbank.ru/career/it/vacancy/kamensk-uralsky/python-middle/8f423232-…): «Понимаете принципы многопоточности и асинхронного программирования»; «Умеете писать читаемый и поддерживаемый код»; «**Знакомы с инструментами наблюдаемости: логирование, метрики, трассировка**»; «Понимаете принципы ООП, SOLID и основы функционального программирования»; «У вас есть опыт участия в code review»; «Будет преимуществом опыт проектирования распределённых систем и работы с Kubernetes».
2. **«Python-разработчик в команду ботзавода AI-центра»** (tbank.ru/career/it/back-end-razrabotka/python-razrabotchik-v-komandu-botzavoda-ai-centra/, дата не указана): «мы используем **FastAPI, Pydantic, SQLAlchemy**»; «Разрабатывали распределенные системы: Kafka, PostgreSQL, Redis, Elastic»; «внутренние инструменты работают с теми же гарантиями, что и внешние: **мониторинг, алертинг, SLA**».
3. **«Python-разработчик в команду Маршрутизации»** (tbank.ru/career/it/back-end-razrabotka/python-razrabotchik-v-komandu-marshrutizacii/): «Разбираетесь в Application Infrastructure: **VCS, CI/CD, Docker, Kubernetes, Observability**»; «Умеете проектировать сложные системы и выстраивать delivery-процессы».
4. **«Python-разработчик — проектирование ядра платформы»** (агрегатор jabka.work, 28.06.2026): «знакомы с Asyncio, Concurrency, FastAPI, Flask, Django, **Testing**»; «SQL Syntax, Indices, Transactions, Locks, Domain Design, Scaling Patterns»; «Обеспечивать качество кода: писать и поддерживать юнит-тесты, проводить код-ревью».

### Альфа-Банк
1. **«Middle Backend Python Developer»**, вакансия hh № 137444542 (зеркало nesiditsa.ru), **16.09.2026**: «Стек: Python (FastAPI, asyncio), Kafka, PostgreSQL, SQLAlchemy, Alembic, Redis, Docker, Kubernetes.»; «Поддерживать, улучшать и масштабировать работающие сервисы: **стабильность, наблюдаемость, отказоустойчивость**»; «Kafka — понимать… что происходит при сбое и **повторной доставке сообщений**».
2. **«Senior python developer»** (dreamjob.ru, вакансия hh 136012720, дата не указана): «Создавать и поддерживать **миграции базы данных с помощью Alembic**»; «Писать **unit-, integration- и API-тесты** для критически важного функционала»; «Диагностировать и устранять проблемы на основе **логов, метрик и трассировок**»; «Понимание безопасности API: OAuth 2.0, JWT, RBAC и управление секретами»; «Опыт **проектирования стабильных API-контрактов и версионирования API**»; «Опыт написания unit- и integration-тестов с использованием **pytest**»; «Понимание подходов к обработке ошибок, логированию и мониторингу».
3. **«Python разработчик/ ML»** (job.alfabank.ru/vacancies/moskva/remote-job/python-razrabotchik_-ml_35860, 08.06.2026): «Опыт разработки backend-приложений с использованием FastAPI и SQLAlchemy»; «Опыт работы с Docker, Git и CI/CD-процессами»; «Понимание принципов микросервисной архитектуры».
4. **«Fullstack-разработчик Python (платформа мониторинга моделей)»** (job.alfabank.ru/…_35653, 29.05.2026): «FastAPI… SQLAlchemy… **React и TypeScript**… Kafka… Docker и Git… Понимание CI/CD-процессов».

### Сбер (rabota.sber.ru)
1. **«Backend разработчик (Python)»** (rabota.sber.ru/search/backend-razrabotchik-python-4537209/, **10.08.2026**): «**Внедрять мониторинг (Prometheus, Grafana, VictoriaMetrics) и алерты**»; «Писать юнит-тесты и интеграционные тесты»; «Работать с очередями (RabbitMQ, Kafka)»; «Участвовать в код-ревью и формировании стандартов разработки»; «Python 3.x (FastAPI/Flask/Django — любой из)… Git, CI/CD… Docker, базовый Kubernetes».
2. **«Senior Python разработчик»** (…/senior-python-razrabotchik-4555549/, **13.08.2026**; тот же текст в …/python-razrabotchik-4551518/, 20.07.2026): «Стек технологий: Python 3.12+, FastAPI, gRPC/HTTP, Kafka, PostgreSQL… **Grafana/OpenTelemetry**, OpenShift, Jenkins»; «развивать платформу: **тестирование, CI/CD, мониторинг, трассировка, расходы**»; «инженерный вкус и **привычка мерить всё метриками**»; «практика работы с ML-системами в проде: фичи, офлайн/онлайн-оценка, **A/B**, наблюдаемость качества».
3. **«Python Backend Engineer (GenAI Data Governance)»** (…-4556395/, **18.08.2026**): «знание python (уверенный уровень: асинхронность, **типизация, тестирование**)»; «Redis (кэш, очереди, **rate-limiting**)»; «проектировании API сервисов (REST, документация через **Swagger/OpenAPI**)»; «очереди, **ретраи, кэширование**, контроль стоимости и латентности»; «Temporal (… Celery/Airflow опыт тоже подойдёт)».
4. **«Python Developer»** (…/python-developer-4547328/, **08.07.2026**): «практический опыт разработки кода с ИИ-агентами: Codex, Gemini, **Claude Code**, Qwen Code или аналоги»; «**умение критически оценивать и валидировать решения, сгенерированные AI-агентами**: находить ошибки, проверять корректность и границы применимости»; «участвовать в… ревью кода и **разборе инцидентов**».
5. **«Python Backend Engineer Middle (AI)»** (…-4549894/, **31.07.2026**): «выстраивать инфраструктуру на базе **Docker и Docker Compose**» — т.е. compose без Kubernetes встречается и в банке.

### Яндекс (yandex.ru/jobs, даты на страницах не указаны, страницы живые 17.09.2026)
1. **«Бэкенд-разработчик в Поиск»** (yandex.ru/jobs/vacancies/bekendrazrabotchik-v-poisk-48297) — **сценарии поиска финансовых продуктов**, то есть наш предмет: «Технологический стек: Python, C++, **FastAPI, SQLAlchemy, Pydantic**, Temporal, SQL, реляционные базы данных, LLM-инструменты.»; «**Понимаете принципы тестирования, мониторинга и эксплуатации бэкенд-сервисов**»; «Умеете проектировать API».
2. **«Разработчик на Python и Go в Яндекс ID»** (…-42788): «Умеете тестировать и сопровождать свой код»; «безопасность [персональных] данных для нас в приоритете».
3. **«Разработчик бэкенда на Python»** (…-46435): «Не боитесь многопоточного или асинхронного программирования»; «Отлично знаете алгоритмы и структуры данных»; плюс — «Владеете DevOps-навыками».

### Синтез П7: что планка «Т-Банк/Сбер/Альфа» реально требует от бэкенда
Частота по **16** вакансиям выше (Т1–Т4, А1–А4, С1–С5, Я1–Я3; подсчёт мой, по дословным фразам; пересчитано — первая редакция ошибочно писала «из 12»):
| Требование | Встречается | У нас |
|---|---|---|
| FastAPI (часто + SQLAlchemy/Pydantic/Alembic) | 11 из 16 | **есть — стек совпадает с рынком 1-в-1** |
| БД / PostgreSQL / SQL | 16 из 16 | есть |
| Тесты (unit/integration/API, pytest) | 8 из 16 | есть, выше медианы |
| Code review | 8 из 16 | соло — роль ревьюера закрывают агенты/чек-листы |
| Docker; CI/CD | 9 из 16 | есть |
| 🔴 **Наблюдаемость: логи + метрики + трассировка, алерты, Prometheus/Grafana/OTel** | **8 из 16** | **логи и Sentry — да; метрик, трасс, алертов — нет** |
| asyncio / асинхронность | 6 из 16 | 8 `async def` на ~676 `def` — **почти нет** |
| Брокер сообщений (Kafka/RabbitMQ) | 9 из 16 | нет — **для нашего масштаба не нужен** (см. «избыточное») |
| Kubernetes/OpenShift | 6 из 16 | нет — **для одного VPS не нужен** |
| Redis (кэш, rate-limit, очереди) | 4 из 16 | нет |
| Версионирование API / OpenAPI | 2 из 16 (явно) | есть (`/v1`, OpenAPI-генерация) |
| Валидация кода, написанного ИИ-агентами | 1 из 16 (Сбер) | это наш основной режим — сильная сторона, если её показать |

**Главное:** банковская планка в вакансиях — это **не «больше тестов»**, а **эксплуатация**: мониторинг, алерты, трассировка, разбор инцидентов, SLA. По тестам и стеку мы на уровне; по наблюдаемости — ниже. Kafka/K8s — признак **масштаба банка**, а не качества; их отсутствие у одного сервиса на VPS разрывом не является.

---

## Часть A. 🔴 Пригодность стека предмету и «чем такие продукты пишут в индустрии»

### A1. Стек PFM-приложений и робо-эдвайзеров (первоисточники — вакансии и инженерные блоги)
| Компания (тип) | Бэкенд | Фронт/прочее | Источник, дословно |
|---|---|---|---|
| **Monarch Money** (PFM, США; ближайший аналог нашего B2C) | **Python/Django**, GraphQL/Graphene, PostgreSQL, Redis | React/TypeScript, React Native; AWS, Terraform, Docker, ECS; CircleCI | jobs.ashbyhq.com/monarchmoney/a000b494-… (22.05.2025): «Back-End: Python/Django, GraphQL/Graphene, PostgreSQL, Redis»; «Front End: React/Typescript, React Native, Apollo (GraphQL)»; «CI/CD (Circle CI)». Команды: «Growth… rapid experimentation, a/b testing» |
| **Betterment** (робо-эдвайзер, США) | **Ruby on Rails** (прод), расчётное ядро на **Julia** (ранее R); исторически Java-монолит | React | betterment.com/engineering/why-betterment-is-using-julia (14.11.2021): «we're using Julia to power the projections and recommendations»; «our production code, which is mostly developed in Ruby»; «The Julia library we built for this purpose serves around 18 million requests per day»; «optimize and speed up our code by multiple orders of magnitude». Фоновые задачи: «a Ruby on Rails application at Betterment performed somewhere on the order of 10 million asynchronous tasks» — через **очередь в БД** (Delayed), не Kafka |
| **Wealthfront** (робо-эдвайзер, США) | **Java** (торговое ядро, QuickFIX/J), Ruby on Rails (веб) | React, Next.js, TypeScript, Turborepo; Sentry | eng.wealthfront.com (21.04.2026): «QuickFIX/J is a robust, open-source, Java-based FIX engine»; (02.09.2022): «Our core web application is driven by a tried-and-true Ruby on Rails server that serves React apps»; (27.02.2024): «our Sentry SDK settings for error tracking» |
| **Personetics** (B2B-движок финансовых инсайтов для банков) | **Java** (основной), Python (плюс), Kubernetes | AWS/Azure | builtin.com/job/backend-engineer/9105002: «5+ years of experience designing and building large-scale backend systems using Java»; «2+ years of experience working with Python (Advantage)»; «3+ years of hands-on experience with Kubernetes» |
| **Meniga** (B2B PFM для банков, Исландия/Европа) | **C#/.NET**, MSSQL или PostgreSQL; on-premise у банков | Kafka, Azure, K8s — «nice to have» | builtin.com/job/senior-net-engineer/9155851: «Must have: C# / .NET · MSSQL or PostgreSQL»; «Most systems are on premises at client sites»; «this is not CRUD territory»; «AI-native — you use AI tools… (Cursor & Claude Code)» |

**Вывод A1.** Разделение чёткое: **B2C-PFM** пишут на динамических языках с веб-фреймворком (Python/Django, Rails) + React/TS + PostgreSQL + Redis; **B2B-движки для банков** — на JVM/.NET (потому что их ставят в контур банка, где JVM/.NET — стандарт). Наш стек (Python/FastAPI + PostgreSQL + React/TS) **совпадает с B2C-лидером Monarch почти 1-в-1** (разница — FastAPI вместо Django, REST вместо GraphQL, нет Redis). В РФ-банках FastAPI+SQLAlchemy — самый частый бэкенд-стек в Python-вакансиях (П7, 11 из 16). Выбор стека **не является разрывом**; риск только в одном месте — если продукт пойдёт в B2B-поставку on-premise банкам, там ждут JVM (Personetics) или .NET (Meniga), но это решается контейнером и API, а не переписыванием.

### A2. Python для расчётного ядра: где предел
- Расчётное ядро Betterment — отдельный язык (Julia) **при 18 млн запросов/сутки**; у них причина — «two-language problem» (исследователи писали на R). Это аргумент о масштабе, а не о непригодности Python.
- **numpy** (https://numpy.org/doc/stable/user/whatisnumpy.html ): «the element-by-element operation is speedily executed by pre-compiled C code… at near-C speeds»; «Vectorization describes the absence of any explicit looping».
- У нас (`app/core/forecast.py`): `MC_SIMULATIONS = 1000`, генерация — `samples = [point + random.gauss(0.0, sigma_abs) for _ in range(n_sim)]` (стр. 114), numpy в проде не используется (в `requirements.txt` его нет, только в dev). 1000 гауссовых чисел на чистом Python — порядок **долей миллисекунды–миллисекунд** на выборку (оценка, не замер; замер — Р1). Бюджет `calculate` в `slo.md` — 1200 мс. **Вывод:** при 1000 симуляций numpy **не нужен**; нужен станет при росте до 10⁴–10⁵ симуляций × 66 альтернатив или многопериодной симуляции траекторий. Порог решения — замер p95 `calculate` в Р1: если ядро MC > 20 % бюджета — векторизовать (оценка работ 4–8 ч, +~20 МБ зависимость).
- 🔴 Попутная находка для Р1: стр. 109 `random.seed(seed)` сидирует **глобальный** генератор модуля `random`, тогда как стр. 129 уже использует локальный `random.Random(seed)`. Под gunicorn с потоками или при параллельных запросах глобальный seed — источник невоспроизводимости прогноза. Цена правки — < 1 ч. (Только констатация; код не трогал.)
- **Decimal и скорость** (Python 3.3 What's New, https://docs.python.org/3/whatsnew/3.3.html ): «The new C version of the decimal module integrates the high speed libmpdec library»; «Performance gains range from 10x for database applications to 100x for numerically intensive applications»; «The FloatOperation signal optionally enables stricter semantics for mixing floats and Decimals.» Значит, довод «Decimal медленный» с 2012 г. в основном снят (C-реализация по умолчанию), а `FloatOperation` — готовый механизм **ловить смешение float и Decimal** в тестах (включить ловушку в `decimal.getcontext().traps` в conftest) — дешёвая защита от класса дефекта Г20, 1–2 ч.

### A3. Две СУБД (SQLite + PostgreSQL)
12-factor (фактор X, dev/prod parity — см. П3) прямо против. Наша матрица в CI — компенсация, и она уже поймала два реальных FK-бага (`engineering_practices.md` §3: BUG-019, BUG-023). Рынок (Monarch, Альфа, Сбер) — PostgreSQL везде. **Вывод:** держать SQLite как **быструю локальную** БД допустимо только пока матрица зелёная; для прод-режима и E2E — только PG. Избыточным это не является, но это долг: каждая миграция — двойная проверка. Альтернатива дешевле по сопровождению — локальный PG в docker-compose + `pytest` с PG по умолчанию (цена — +время прогона; замерить в Р1).

### A4. FastAPI для расчётного, а не CRUD-сервиса
FastAPI/Starlette рассчитан на асинхронный ввод-вывод; у нас 8 `async def` на ~676 `def`. Синхронные обработчики FastAPI исполняет в пуле потоков — для CPU-ядра это нормально, но **GIL** делает параллельные `calculate` в одном процессе последовательными; масштабирование — числом воркеров gunicorn (у нас `gunicorn_conf.py` есть). Рынок в вакансиях требует asyncio в 6 из 16 — у нас это не разрыв функционально, но разрыв **в портфолио-смысле** (собеседование). Сравнение с Django (Monarch) — Django даёт админку и ORM-миграции «из коробки», FastAPI — OpenAPI-контракт, который мы и используем как источник правды. Для «API + SPA + генерация типов» FastAPI — обоснованный выбор.

### A5. React + TS для интерфейса объяснения решения
Monarch, Wealthfront, Альфа (fullstack-вакансия) — React/TypeScript. Выбор совпадает с рынком; задача «объяснить решение» — вопрос визуализации (у нас Recharts + visx + KaTeX по ADR-011), а не фреймворка.

---

## П6. 🔴 «Нет у нас — есть у рынка»: инвентаризация с ценой

Нормы для резервного копирования:
- **CISA, «Data Backup Options»** (https://www.cisa.gov/sites/default/files/publications/data_backup_options.pdf ): «follow the 3-2-1 rule: 3 – Keep 3 copies of any important file: 1 primary and 2 backups. 2 – Keep the files on 2 different media types… 1 – Store 1 copy offsite».
- **Google SRE Book, «Data Integrity»** (https://sre.google/sre-book/data-integrity/ ): «No one really _wants_ to make backups; what people _really_ want are _restores_.»; «Continuously test the recovery process as part of your normal operations»; «If recovery tests are a manual, staged event, testing becomes an unwelcome bit of drudgery… automate these tests whenever possible and then run them continuously.»

| Практика | У рынка (кто) | У нас | Вердикт и цена |
|---|---|---|---|
| Фоновая очередь задач | Betterment — очередь в БД, 10 млн задач/сутки; Сбер С3 — Temporal/Celery; банки — Kafka | `BackgroundTasks` (в процессе) + cron | **Разрыв малый.** `BackgroundTasks` теряет задачу при рестарте воркера. Для почты/уведомлений — терпимо. Если появится тяжёлый импорт/пересчёт — очередь в PG (как у Betterment; в Python — `procrastinate` или `arq`+Redis), 6–10 ч. Kafka — избыточна |
| Кэш (Redis) | Monarch, Альфа, Сбер (4 из 16) | БД-кэш ставки, `lru_cache` | **Не разрыв сейчас.** `lru_cache` — на процесс, при N воркерах gunicorn кэш не общий; для rate-limit это важнее (см. ниже) |
| Rate limit, общий для воркеров | Сбер С3 «Redis (…rate-limiting)» | свой middleware | 🔴 **Проверить в Р1:** если счётчик в памяти процесса, при N воркерах фактический лимит = N × заявленного. Redis в compose + общий счётчик — 3–4 ч, +~50 МБ RAM |
| Миграции без простоя (expand/contract) | Fowler/Sato (П3) | обратимость проверяется; правила expand/contract нет | 2 ч на правило + пункт скилла миграций |
| Резервные копии 3-2-1 + автоматическая проверка восстановления | CISA, Google SRE | ночной `pg_dump`, локально + офсайт в РФ-S3, шифрование age, RPO ≤ 24 ч, RTO ≤ 4 ч, `backup_verify.sh` | **Соответствует норме по замыслу.** Разрыв один: `backup_verify.sh` в cron-скриптах grep не нашёл — SRE требует «run them continuously». Поставить в cron еженедельно + алерт на провал — 1 ч |
| Контроль зависимостей | Dependabot/Renovate — бесплатно | пины, pip-audit только на тегах, mypy 1.3.0 (2023) | 1–1,5 ч |
| i18n | — | `app/i18n.py` есть | ок |
| Продуктовая аналитика | Monarch Growth-команда | `app/services/analytics.py` — событийный лог, воронка | ок |
| A/B-контур | Monarch, Сбер С2 | `app/services/experiments.py` | ок |
| Отказоустойчивость (HA) | банки — K8s, реплики | один VPS, SLO 99,5 % | **осознанно** и записано в `slo.md`; HA до платящих пользователей — избыточна |
| Метрики + алерты + аптайм | 8 из 16 вакансий | нет | 🔴 главный разрыв, см. П4: 10–15 ч |
| Процедура отката релиза | DORA (П1) | нет в `DEPLOY.md` | 2–4 ч |
| Идемпотентность POST | IETF draft (П5) | нет | 4–6 ч (или 1–2 ч дедуп импорта) |
| Машинная проверка слоёв | Shopify, import-linter | нет | 1–2 ч + исправления |
| Разбор инцидентов (postmortem) | Сбер С4 «разборе инцидентов» | диспетчер инцидентов упомянут в `slo.md` | шаблон постмортема — 0,5 ч |

Поправка к П6 (строка «Rate limit»): проверено — `app/middleware.py`: «Скользящее окно по IP… **In-memory: достаточно для single-instance деплоя**», а `gunicorn_conf.py:13`: `workers = int(os.getenv("WEB_CONCURRENCY", multiprocessing.cpu_count() * 2 + 1))`. Один инстанс ≠ один процесс: на VPS с 2 vCPU это 5 воркеров → фактический лимит до 5× заявленного. **Г32 это уже поймал** (`product_security_2026-09-17.md` стр. 402: «счётчик в памяти инстанса — при нескольких воркерах gunicorn лимит мягче в N раз»). Здесь — только подтверждение и цена (3–4 ч с Redis или 1–2 ч со счётчиком в PG).

### Дополнение к П1: SPACE
**Forsgren, Storey, Maddila, Zimmermann, Houck, Butler, «The SPACE of Developer Productivity»**, ACM Queue 2021 (https://queue.acm.org/detail.cfm?id=3454124 , r.jina.ai 200): «productivity cannot be reduced to a single dimension (or metric!)»; измерения — «satisfaction and well-being; performance; activity; communication and collaboration; and efficiency and flow»; «Activity metrics alone… should never be used in isolation either to reward or to penalize developers». Для соло-разработчика SPACE применима частично: «efficiency and flow» у нас уже меряется (`tools/timing_lab`, `docs/timing_reference.md`), «communication» — не про нас. Отдельного внедрения не требует.

---

## ИТОГ Г33

### Прямой ответ
**По стеку и тестам мы на уровне рынка или выше; по эксплуатации (наблюдаемость, откат, проверка SLO) — ниже планки, заявленной в CLAUDE.md.** Стек Python/FastAPI/SQLAlchemy/PostgreSQL + React/TS совпадает с B2C-PFM-лидером (Monarch Money) и с самым частым Python-стеком вакансий Т-Банка/Альфы/Сбера/Яндекса (FastAPI — 11 из 16). Набор видов тестов (property, мутации, мультибраузер, a11y, матрица двух СУБД) шире, чем требуют банковские вакансии. А вот 8 из 16 вакансий требуют «логи + метрики + трассировка, алерты», и здесь у нас есть только логи и Sentry. Второй класс проблем — **наши документы о себе устарели** (`it_stack.md`, `engineering_practices.md` §3): они недооценивают сделанное и поэтому непригодны как внешняя витрина.

**Процесс (прозрачно):** классификация — breadth-first (8 пунктов + 3 части, независимые). Подагентов — **0** (ограничение батча «лучше без них»; работа выполнена лидером последовательно). Внешние вызовы: Exa `web_search_exa` — 14, Exa `web_fetch_exa` — 2 (4 URL), context7 — 4 (2 resolve + 2 query), `WebFetch` — 4, `WebSearch` — 0, curl/r.jina.ai — ~25 страниц, OpenAlex — 5 запросов, PDF через curl+pdftotext — 2 (NIST, arXiv). Второго круга не было: противоречия между источниками разрешались на месте (сверка ответа ассистента Sonar со страницей документации; пересчёт вакансий 12→16).

### 🔴 Таблица разрывов
Цена в часах — оценка работы соло-разработчика с ИИ-ассистентом; деньги — прямые расходы (0 ₽ = open-source/бесплатный тариф).

| Практика / метрика | Норма рынка (источник) | Что у нас (файл) | Разрыв | Цена закрытия |
|---|---|---|---|---|
| 🔴 Метрики 4 золотых сигналов + алерты | «latency, traffic, errors, and saturation… page a human» (Google SRE Book); 8/16 вакансий РФ | нет; только JSON-логи + Sentry (`app/logging_config.py`, `app/observability.py`) | **большой** | 8–12 ч; 0 ₽ (Prometheus+Grafana в compose), +0,5–1 ГБ RAM на VPS |
| 🔴 Внешний аптайм-чек | SRE: SLO нужен SLI | нет | средний | 1 ч; 0 ₽ |
| 🔴 SLI-формулы и политика бюджета ошибок | «error budget policy» (SRE Workbook) | цели есть, формул и измерения нет (`docs/slo.md`) | средний | 2–3 ч; 0 ₽ |
| Нагрузочный тест против своих SLO | цели 50 RPS, 10 параллельных `calculate` (`slo.md`) | locust 20 польз./30 с, без порогов провала (`ci.yml` full) | средний | 3–4 ч; 0 ₽ |
| 🔴 Процедура отката релиза | DORA: восстановление < 1 ч — верхний квартиль | нет в `docs/DEPLOY.md` | средний | 2–4 ч; 0 ₽ |
| Error tracking без трансграничной передачи | GlitchTip самохост, совместим с Sentry SDK | Sentry SaaS по DSN; скраб не настроен (Г32) | средний (152-ФЗ) | 3–4 ч; 0 ₽ (самохост) или Sentry Free $0 + `before_send` |
| Гейт покрытия | Sonar way: ≥80 % на **новом** коде; Google: 60/75/90, выше 90 не гнаться, per-commit 90–99 % | ≥90 % абсолют по дереву; ядро ≥95 % (`.coveragerc`, `ci.yml`) | малый — **вид** гейта, не порог | 2–3 ч (`diff-cover`); 0 ₽ |
| Мутационное тестирование | Stryker: 60 жёлтый / 80 зелёный, по умолчанию не валит; Google — выжившие мутанты на изменённом коде | 68,7 % на 3 модулях ядра; `|| true`, результат никуда не идёт (`pyproject.toml`, `ci.yml` deep) | малый | 3–4 ч (артефакт + ratchet); 0 ₽ |
| Цикломатическая сложность | ≤10 (McCabe/NIST SP 500-235), до 15 при сильном тест-плане; Sonar Python default 15 | не мерена | неизвестен → Р1 | 1 ч на гейт после замера |
| Дублирование | ≤3 % на новом коде (Sonar way) | не мерено | неизвестен → Р1 | 1 ч на гейт |
| Машинная проверка слоёв | модульный монолит «boundaries defined and respected» (Shopify); import-linter `layers` | нет `.importlinter` | средний | 1–2 ч + исправления |
| ADR: «как проверить решение», статус «superseded» | MADR «Confirmation»; Nygard «superseded» | шаблон без «Проверки»; 0 из 17 ADR в статусе superseded | малый | 0,5 ч шаблон + 2–3 ч ретро-проход |
| Идемпотентность POST | IETF draft Idempotency-Key (UUID, 409/422) | нет (`app/`) | средний (импорт выписки, B2B) | 1–2 ч дедуп импорта; 4–6 ч полный механизм |
| Миграции без простоя | expand/contract (Fowler/Sato); Alembic: autogenerate «always… manually review» | обратимость тестируется; правила нет; `alembic check` нет | малый | 2–3 ч |
| Rate limit на N воркеров | Redis/общий счётчик (Сбер С3) | in-memory при `cpu*2+1` воркерах (`app/middleware.py`, `gunicorn_conf.py`) — **поймано в Г32** | средний | 1–4 ч |
| Обновление зависимостей | Dependabot/Renovate (бесплатно); pip-audit на PR | нет бота; pip-audit только на тегах; mypy 1.3.0 от 2023 | малый | 1,5 ч; 0 ₽ |
| Регулярная проверка восстановления | «Continuously test the recovery process» (SRE); 3-2-1 (CISA) | `backup_verify.sh` есть, в cron не найден; 3-2-1 соблюдено (`docs/backup_restore.md`) | малый | 1 ч |
| Ловушка смешения float/Decimal | `decimal.FloatOperation` (Python docs) | не включена; float в 36 файлах `app/` (Г20) | малый к Г20 | 1–2 ч |
| Глобальный seed MC | воспроизводимость при параллельных запросах | `random.seed(seed)` в `app/core/forecast.py:109` | малый | < 1 ч |
| РБПО (ГОСТ Р 56939-2024) для B2B | обязателен, только если на него сослались (п. 4.14) | не сопоставлено; Г32 ГОСТ не упоминает | малый сейчас, важен в B2B | 2–3 ч (матрица «25 процессов → что есть») |
| Документы о себе | — | `it_stack.md` §2–3 и `engineering_practices.md` §3 устарели | средний (репутационный) | 2–3 ч |
| Асинхронность (портфолио) | asyncio в 6/16 вакансий | 8 `async def` / ~676 `def` | нет функционально | не закрывать ради кода; обсуждать на собеседовании |

**Итого по 🔴-пунктам: ~20–27 ч и 0 ₽ прямых расходов** (плюс ресурсы VPS под Prometheus/Grafana/GlitchTip).

### Упустили важное
1. 🔴 **Наблюдаемость как измерение, а не документ:** метрики четырёх сигналов, алерты, аптайм-чек, SLI-формулы. `docs/slo.md` существует, но ни одна его цифра не измеряется.
2. 🔴 **Откат релиза** — процедуры нет, а DORA мерит именно время восстановления.
3. **Идемпотентность** импорта выписки и B2B-POST — двойной импорт даёт неверный расчёт свободного потока без единой ошибки в логах (тот же класс, что «тихо неверный совет» из обоснования порога ядра в `ci.yml`).
4. **Машинная проверка архитектурных решений** (import-linter; раздел «Проверка» в ADR). Сейчас 17 ADR — это намерения, а не проверяемые правила.
5. **ГОСТ Р 56939-2024** как язык для B2B-продаж банкам (пропущен и в Г32).
6. **Гейт по новому коду** (покрытие/дельта) вместо абсолюта по дереву.
7. **Устаревшие собственные документы** — `it_stack.md` утверждает, что нет тестов, Alembic, Docker и CI.

### Делаем избыточное для нашего размера
1. 🔴 **Весь pytest + coverage в pre-commit** (`.pre-commit-config.yaml`) — при полном прогоне ~25 мин на каждый коммит. Норма — быстрые проверки (ruff/flake8, mypy на изменённых файлах) в pre-commit, полный прогон — в CI. Этот обряд либо заставляет коммитить с `--no-verify`, либо съедает часы.
2. **Три линтера одного класса** (flake8 + pylint + ruff в `pyproject.toml`, но не установлен): ruff заменяет flake8 и isort и покрывает большую часть pylint. Держать три — тройная настройка и тройной шум. (Установку/замену делать не мне — это решение для Р1/владельца.)
3. **Мультибраузерные E2E (chromium + firefox + webkit) + визуальная регрессия на каждом теге** — для B2C-веба нормально перед релизом, но соло это дорогое сопровождение; достаточно chromium на PR и полного набора перед публичным релизом, что у нас по сути и есть. Пограничный пункт: оставить, но не расширять.
4. **Kafka, Kubernetes, микросервисы, blue-green/canary, сервис фича-флагов** — присутствуют в вакансиях банков (6–9 из 16), но это признак масштаба банка, а не качества. Их **у нас нет, и это правильно** — в список они включены, чтобы их не добавили из-за «планки Т-Банка».
5. **Полный OTel-трейсинг с коллектором** для монолита из одного процесса — избыточен до выделения второго сервиса; request-id в JSON-логах уже даёт 80 % пользы.
6. **Сертификация по ISO 27001 / процессы по ГОСТ Р ИСО/МЭК 12207** до B2B-сделки, которая их требует.
7. **Матрица SQLite + PostgreSQL** — не избыточна, пока ловит баги, но это долг; перевод локальной разработки на PG в compose снимает вторую СУБД вовсе (решать после замера времени прогона в Р1).

### Готовое задание для Р1 (замеры; инструменты, пороги)
| # | Метрика | Инструмент | Команда (набросок) | Порог «ок» / «плохо» | Источник порога |
|---|---|---|---|---|---|
| 1 | Цикломатическая сложность функций | `radon`, гейт `xenon` | `radon cc app tools -s -a -j`; `xenon app --max-absolute B --max-modules A --max-average A` | ни одной функции ранга D+ (CC>20); цель — ≤10 у 95 % функций; ранг C (11–20) — список на рефакторинг | NIST SP 500-235; radon; Sonar Python 15 |
| 2 | Индекс сопровождаемости (MI) | `radon mi` | `radon mi app -s -j` | все модули A (≥20); B/C — список | radon |
| 3 | Когнитивная сложность | `flake8-cognitive-complexity` или `complexipy` | `complexipy app` | ≤15 на функцию | Sonar S3776 (порог 15 не подтверждён дословно — отметить) |
| 4 | Дублирование | `jscpd` (Python + TS) | `npx jscpd app frontend/src --min-lines 5 --reporters json` | ≤3 % | Sonar way |
| 5 | Нарушения слоёв | `import-linter` | контракт `layers`: `app.api` → `app.services` → `app.core`; forbidden `app.core` → `app.api`, `app.database` | 0 нарушений | Shopify; MADR «Confirmation» |
| 6 | Мутационный балл ядра (полный, не пилот) | `mutmut` (уже настроен) | расширить `only_mutate` на `app/core/*` | ≥80 % зелёный, 60–80 жёлтый, <60 красный; главное — **список выживших** | Stryker defaults; Google TSE 2021 |
| 7 | Покрытие нового кода | `diff-cover` | `diff-cover coverage.xml --compare-branch=origin/main --fail-under=90` | ≥90 % на дельту | Google per-commit; Sonar ≥80 % |
| 8 | Покрытие ветвей (не только строк) | `coverage --branch` | в `.coveragerc` строки `branch` нет (grep 17.09.2026) — **покрытие ветвей сейчас выключено**; включить в ветке замера | зафиксировать число; порога не ставить до замера | Inozemtseva & Holmes: вид покрытия мало влияет |
| 9 | Форма пирамиды | pytest маркеры | `pytest --collect-only -q -m "<маркер>"` по unit/integration/e2e | ориентир 70/20/10 | Google 2015 |
| 10 | Безопасность кода и зависимостей | `bandit`, `pip-audit`, `npm audit` | как в `ci.yml` full, но на текущем дереве | 0 High; Medium — список | Г32; ГОСТ Р 56939 п.10, п.16 |
| 11 | Мёртвый код | `vulture` (Python), `knip` (TS) | `vulture app --min-confidence 80` | список, без порога | — |
| 12 | Типизация | `mypy` **актуальной версии** против 1.3.0 | `mypy app` на свежем mypy | 0 ошибок; разница версий — отдельный пункт | — |
| 13 | p95 `calculate` и доля Монте-Карло в нём | `locust` + `cProfile`/`pyinstrument` | профиль 10 параллельных `calculate` | p95 ≤ 1200 мс; MC ≤ 20 % → numpy не нужен | `docs/slo.md` |
| 14 | Смешение float/Decimal | `decimal.FloatOperation` в conftest (временно, в ветке замера) | прогон тестов ядра с ловушкой | 0 срабатываний в денежных путях | Python docs; Г20 |
| 15 | Rate limit при N воркерах | ручной тест: gunicorn `-w 4` + серия запросов | — | лимит соблюдается с точностью ×1, не ×N | Г32 стр. 402 |

### Осталось неизвестным
- Точный порог когнитивной сложности Sonar S3776 для Python дословно не снят (страница правила рендерится JS); в таблице Р1 помечено.
- ISO/IEC 12207 и ISO 27001 первоисточниками не открывались (платные); выводы о них — по назначению стандартов.
- Даты публикации части вакансий (Т-Банк Т2–Т3, Яндекс Я1–Я3, Альфа А2) на страницах не указаны — отмечено у каждой.
- Инженерные блоги Т-Банка/Сбера/Альфы на Хабре (кроме проверки доступности `habr.com/ru/companies/tbank/` — 200) по теме метрик качества не разбирались: бюджет ушёл на вакансии как на прямую формулировку планки. Кандидат на добор, если нужна планка по **процессу** (SLO, постмортемы) изнутри банков.
- Реальные значения сложности, дублирования, нарушений слоёв, доли MC в `calculate` — это Р1.
