# FINPILOT — Инфраструктура тестирования

> Кому и зачем. Этот файл — карта всего, что есть в проекте по тестам: какие уровни,
> чем запускаются, как устроены три категории прогона (fast/full/deep), где PostgreSQL-матрица
> и почему мультибраузер живёт в CI, а не в песочнице. Прочитал — понимаешь систему целиком и
> знаешь, какой командой что гонять.

---

## 0. TL;DR

| Хочу | Команда |
|---|---|
| Быстро прогнать перед коммитом | `make test-fast` (unit + integration + property, покрытие ≥ 90%) |
| Полный прогон перед релизом | `make test-full` (визуал + live-a11y; мультибраузер — в CI) |
| Глубокий прогон (редко) | `make test-deep` (стресс-property + мутации) |
| E2E в браузере | `make e2e` (chromium) |
| Безопасность | `make security` (bandit + pip-audit) |
| Всё на PostgreSQL | задать `DATABASE_URL=postgresql+psycopg://...` перед `pytest` |

Маркеры: `fast`, `full`, `deep`, `e2e`, `property`. Отбор — `pytest -m <маркер>`.

---

## 1. Уровни тестов (что и зачем проверяет)

**Unit** — отдельные функции ядра и сервисов в изоляции. Базовый слой: `tests/test_*.py`
(например, `test_alternatives.py`, `test_metrics.py`, `test_avalanche.py`). Быстрые,
детерминированные, большинство тестов проекта здесь.

**Integration** — связки через реальный `TestClient` и реальную схему БД (схема строится
теми же Alembic-миграциями через startup приложения — заодно проверяется применимость
миграций). Файлы вида `test_api_*.py`, `test_*_integration.py`, `test_schema_session2.py`.

**Property-based** (`tests/test_core_properties.py`, маркер `property`) — математические
инварианты мат-модели на тысячах случайных входов через `hypothesis`. Не «несколько кейсов»,
а «свойство, которое обязано держаться для ВСЕХ входов»: `Rt(a) ≥ 0`, ПДН `Dt(a) ≤ 0.40`,
сумма долей альтернативы = 1, `|A| ≤ 66`, `U(a) ∈ [0,1]`, рекомендация = argmax, веса профилей
в сумме = 1 и т.д. Инварианты сверяются строго по `docs/math_model_v3_0_0.md`. Это самый
дешёвый способ поймать математическую регрессию, которую точечные кейсы пропускают.

**E2E** (`tests/e2e/`, маркер `e2e`) — браузерные сквозные сценарии через Playwright:
поднимается реальный uvicorn с изолированной БД, реальный браузер ходит по UI. Проверяют то,
что юнит не ловит — разрыв между UI и API. Покрывают dashboard, planning, auth/guest и базовые
CRUD-флоу (создать/удалить/восстановить obligations, goals, transactions). Урок BUG-CRUD:
удаление обязательства было сломано версиями при зелёных юнит-тестах — поэтому базовые CRUD
ОБЯЗАНЫ иметь E2E (правило §13 WATCHLOG).

**Visual regression** (`tests/full/test_visual_regression.py`, тир `full`) — скриншоты ключевых
страниц сравниваются с эталоном. Ловит «уехавшую» вёрстку и слетевшую тему, которые селекторные
тесты не видят. Эталоны привязаны к платформе рендера → генерируются и хранятся в CI.

**Live-a11y** (`tests/full/test_a11y_axe.py`, тир `full`) — промышленный движок axe-core в реальном
браузере проверяет WCAG 2.1 A/AA в РЕНДЕРЕ. Дополняет механический `test_a11y_mechanical.py`
(парсинг HTML) и контрастный `test_a11y_contrast.py` (токены в обеих темах).

**Load** (`loadtest/locustfile.py`) — нагрузочный сценарий locust. Базовый baseline снят в
песочнице (~110 RPS @ 60u, бутылочное горло — `calculate`); боевые числа снимаются на VPS тем же
сценарием. Smoke-прогон встроен в полный CI-тир.

**Security** — `bandit` (статанализ кода на уязвимые паттерны) + `pip-audit` (аудит CVE в
зависимостях). Запуск: `make security`; в CI — в полном тире.

**Mutation** (глубокий тир) — `mutmut` вносит мутации в `app/core` и проверяет, ловят ли их
тесты. Меряет не покрытие, а СИЛУ тестов. Редкий ручной прогон: `make mutation`.

---

## 2. Три категории прогона (как в проде)

Разработка не должна тормозить из-за тяжёлых проверок, поэтому тесты разведены по скорости и
частоте. Отбор — pytest-маркерами; конфиг — `.github/workflows/ci.yml`.

### (1) Быстрый — `fast` — каждый push/PR
unit + integration + property + e2e-smoke (chromium). Блокирующий гейт покрытия **90%**.
Матрица двух СУБД (см. §3). Это то, что обязано быть зелёным на каждом коммите.
```
make test-fast        # локально (без e2e-smoke)
pytest -m fast        # только быстрый набор
```
> Маркер `fast` навешивается **автоматически** на любой тест, не помеченный `full`/`deep`/`e2e`
> (хук `pytest_collection_modifyitems` в `tests/conftest.py`). Поэтому сотни unit/integration
> размечать вручную не нужно — они в быстром прогоне по умолчанию.

### (2) Полный — `full` — перед релизом/тегом (и вручную)
Мультибраузерные E2E (chromium + firefox + webkit) + визуальная регрессия + live-a11y +
security (bandit + pip-audit) + нагрузочный smoke (locust).
```
make test-full        # визуал + live-a11y (нужен браузер)
pytest -m full
```

### (3) Глубокий — `deep` — редко/вручную (и еженедельно по cron)
Стресс-property (`tests/deep/`, тысячи примеров) + мутационное тестирование ядра.
```
make test-deep
pytest -m deep
```

В CI: `fast` и `lint` — на push/PR; `full` — на тегах `v*` и `workflow_dispatch`; `deep` — на
`schedule` (понедельник 03:00 UTC) и `workflow_dispatch`.

---

## 3. PostgreSQL-матрица (обязательна, не опциональна)

SQLite молча игнорирует нарушения внешних ключей — на нём проходят тесты, которые ловит только
PostgreSQL (корень BUG-019/023). Поэтому ЛЮБОЕ схемное изменение проверяется на PG. `conftest.py`
уважает внешний `DATABASE_URL` и гоняет тот же набор тестов на боевой СУБД.

В CI быстрый job идёт матрицей `db: [sqlite, postgresql]` (сервис `postgres:16`).

Локально/в песочнице PG поднимается так (apt доступен; `cbr.ru`/деплой — нет):
```sh
# update падает на стороннем nodesource-репо (403) — ставим напрямую, ubuntu-репы рабочие
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq postgresql postgresql-contrib
pg_ctlcluster 16 main start
su postgres -c "psql -c \"CREATE USER finpilot WITH PASSWORD 'finpilot' SUPERUSER;\""
su postgres -c "psql -c \"CREATE DATABASE finpilot_test OWNER finpilot;\""
DATABASE_URL="postgresql+psycopg://finpilot:finpilot@localhost:5432/finpilot_test" \
  SECRET_KEY=x ./.venv/bin/python -m pytest
```
Драйвер — `psycopg[binary]` (формат строки `postgresql+psycopg://`, psycopg3).

> Property-тесты ядра DB-агностичны (чистая математика, без БД) — их результат на SQLite и PG
> идентичен. PG-матрица критична для схемных/FK-изменений; для батча без миграций (как property
> и тесты) она остаётся валидной с последнего схемного изменения.

---

## 4. E2E-движки и почему мультибраузер только в CI

E2E браузер-агностичны: `pytest -m e2e --browser chromium|firefox|webkit`. Флаги запуска
(`--no-sandbox --disable-dev-shm-usage --disable-gpu`) применяются только к chromium и зашиты в
`tests/e2e/conftest.py`.

**В песочнице доступен только chromium.** Playwright раздаёт сборки firefox/webkit ИСКЛЮЧИТЕЛЬНО
со своего Azure-CDN (`cdn.playwright.dev`, `playwright.download.prss.microsoft.com`), который вне
сетевого allowlist песочницы (403) — та же категория ограничения, что `cbr.ru`. Это проверено по
всем каналам (GitHub releases — 404, npm-пакет бинарей не содержит, системный firefox несовместим
с juggler-протоколом Playwright, apt даёт только либы); подробности — в разборе
`FINPILOT_browsers_sandbox_incident.md`. Поэтому:
- быстрый прогон гоняет E2E-smoke на **chromium** (в песочнице и в CI);
- полный тир гоняет **chromium + firefox + webkit** в CI, где CDN доступен.

Тесты при этом полностью браузер-агностичны: добавить движок = добавить флаг `--browser`.

---

## 5. Грабли запуска в песочнице (кратко)

Полностью — `FINPILOT_Claude_sandbox_runbook.md`. Главное: shell — dash (POSIX, не bash);
вывод pytest — в ФАЙЛ, не в пайп; длинные прогоны — в фон через `setsid` + опрос файла-маркера
(`returncode -1` с пустым выводом — это способ вызова, а не смерть песочницы); chromium — только
с `--no-sandbox`.

---

## 6. Карта файлов

| Путь | Тир | Что |
|---|---|---|
| `tests/test_*.py` | fast | unit + integration (основной объём) |
| `tests/test_core_properties.py` | fast (`property`) | property-инварианты ядра (hypothesis) |
| `tests/e2e/` | e2e | браузерные сквозные (dashboard/planning/auth/CRUD) |
| `tests/full/test_visual_regression.py` | full | скриншот-регрессия |
| `tests/full/test_a11y_axe.py` | full | live-a11y через axe-core |
| `tests/deep/test_property_stress.py` | deep | стресс-property (тысячи примеров) |
| `loadtest/locustfile.py` | — | нагрузочный сценарий |
| `.github/workflows/ci.yml` | — | конфиг трёх категорий |
| `Makefile` | — | цели `test-fast/full/deep`, `security`, `mutation`, `e2e` |
| `pytest.ini` | — | маркеры + дефолтный отбор (`not e2e and not full and not deep`) |
| `.coveragerc` | — | источник `app`, порог `fail_under = 90` |
