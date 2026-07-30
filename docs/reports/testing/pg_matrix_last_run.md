# Матрица PostgreSQL — свидетельство о последнем прогоне

**Проверяется автоматически** (`tools/preflight.py`): если в `alembic/versions/`
появилась миграция новее упомянутой здесь, preflight предупреждает. Файл
обновляется вместе с прогоном, а не вместо него.

| Поле | Значение |
|---|---|
| Дата | 2026-07-30 |
| Версия кода | v7.6.0 |
| Последняя миграция | **0031** (`0031_financial_consent_backfill.py`) |
| СУБД | PostgreSQL 16.14 (Ubuntu, песочница) |
| `alembic upgrade head` | прошло, цепочка 0026 → 0031 |
| Внешний ключ | `user_consents_user_id_fkey → users(id)` создан |
| Обратимость | `downgrade 0029` → `upgrade head` и `downgrade 0030` → `upgrade head` прошли |
| Тесты на PostgreSQL | **141 / 141** (дельта ревизии) |
| Тесты на SQLite | **1473 / 1473** (ПОЛНЫЙ прогон) |

Группа прогона: `test_consents`, `test_auth`, `test_api_auth_flow`,
`test_api_crud`, `test_observability`.

**Найдено прогоном:** PG-only взаимная блокировка в `_reset_db()` —
`DROP TABLE` против соединения `idle in transaction`. Разбор —
`docs/reports/incidents/postgres_false_debt_repeat.md`.

**Рецепт подъёма PostgreSQL в песочнице** (две команды, повторно подтверждён):

```
apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq postgresql postgresql-contrib
pg_ctlcluster 16 main start
```
