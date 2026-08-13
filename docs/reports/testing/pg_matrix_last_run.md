# Матрица PostgreSQL — свидетельство о последнем прогоне

**Проверяется автоматически** (`tools/preflight.py`): если в `alembic/versions/`
появилась миграция новее упомянутой здесь, preflight предупреждает. Файл
обновляется вместе с прогоном, а не вместо него.

| Поле | Значение |
|---|---|
| Дата | 2026-08-13 |
| Версия кода | v8.17.0 |
| Последняя миграция | **0032** (`0032_plan_advice_events.py`) |
| СУБД | PostgreSQL 16-alpine (Docker, изолированный контейнер на :55432, не боевая БД) |
| `alembic upgrade head` | прошло, цепочка 0007 → 0032 (контейнер поднят с чистого образа) |
| Обратимость | `downgrade 0032` → `upgrade head` прошли |
| Тесты на PostgreSQL | **50 / 50** (дельта ревизии) |
| Тесты на SQLite | **1581 / 1581, 2 known-fail на счётчиках ревизии (починены в этом же батче)** (ПОЛНЫЙ прогон) |

Группа прогона: `test_api_telemetry` (новые эндпоинты 0032), `test_consents`,
`test_api_crud` (регрессия на существующих финансовых роутерах).

**Предыдущий прогон (2026-07-30, v7.6.0, миграция 0031)** — архивная запись:
141/141 на PostgreSQL, 1473/1473 на SQLite (полный), группа `test_consents`,
`test_auth`, `test_api_auth_flow`, `test_api_crud`, `test_observability`.
Найдено тогда: PG-only взаимная блокировка в `_reset_db()` — `DROP TABLE`
против соединения `idle in transaction`. Разбор —
`docs/reports/incidents/postgres_false_debt_repeat.md`.

**Рецепт подъёма PostgreSQL в песочнице** (две команды, повторно подтверждён):

```
apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq postgresql postgresql-contrib
pg_ctlcluster 16 main start
```
