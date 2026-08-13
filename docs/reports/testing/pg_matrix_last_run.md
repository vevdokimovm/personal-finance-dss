# Матрица PostgreSQL — свидетельство о последнем прогоне

**Проверяется автоматически** (`tools/preflight.py`): если в `alembic/versions/`
появилась миграция новее упомянутой здесь, preflight предупреждает. Файл
обновляется вместе с прогоном, а не вместо него.

| Поле | Значение |
|---|---|
| Дата | 2026-08-13 |
| Версия кода | v8.18.0 |
| Последняя миграция | **0033** (`0033_user_prefs_iis_status.py`) |
| СУБД | PostgreSQL 16-alpine (Docker, изолированный контейнер на :55432, не боевая БД) |
| `alembic upgrade head` | прошло, цепочка 0007 → 0033 (контейнер поднят с чистого образа) |
| Обратимость | `downgrade 0033` → `upgrade head` прошли |
| Тесты на SQLite | полный прогон, зелёный (см. CHANGELOG [8.18.0]) |

Группа целевой проверки: `test_investment` (ADR-017, `estimate_iis_deduction` +
красная линия), миграция 0033 (upgrade/downgrade/upgrade на SQLite и Postgres).

**Предыдущий прогон (2026-08-13, v8.17.0, миграция 0032)** — архивная запись:
50/50 на PostgreSQL (`test_api_telemetry`/`test_consents`/`test_api_crud`),
1581/1581 на SQLite (полный, 2 known-fail на счётчиках ревизии в том же батче).

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
