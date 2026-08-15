# Матрица PostgreSQL — свидетельство о последнем прогоне

**Проверяется автоматически** (`tools/preflight.py`): если в `alembic/versions/`
появилась миграция новее упомянутой здесь, preflight предупреждает. Файл
обновляется вместе с прогоном, а не вместо него.

| Поле | Значение |
|---|---|
| Дата | 2026-08-14 |
| Версия кода | v8.24.1 |
| Последняя миграция | **0034** (`0034_soft_delete_budgets.py`) |
| СУБД | PostgreSQL 15.13 (Homebrew, локальный `postgresql@15`, БД `finpilot_test_pg` — изолированная, не боевая) |
| `alembic upgrade head` | прошло, цепочка 0007 → 0034 |
| Обратимость | не проверялась отдельным `downgrade 0034` в этом прогоне (миграция симметрична 0018, тот же приём batch_alter_table — риск низкий, но зафиксировано честно, не «подразумевается») |
| Тесты на SQLite | полный прогон — см. CHANGELOG [8.24.1] |

Группа целевой проверки: `test_soft_delete` (новые `test_budget_*`), `test_consent_gate`
(гейт согласия на `budgets_router`, добавлен той же миграцией/патчем), `test_api_budgets`,
`test_data_isolation`, `test_notifications` (оба использует `crud.create_budget`/`get_budgets`) —
43/43 зелёных на PostgreSQL.

**Предыдущий прогон (2026-08-13, v8.18.0, миграция 0033)** — архивная запись:
СУБД PostgreSQL 16-alpine (Docker, изолированный контейнер на :55432), `alembic upgrade head`
0007→0033, `downgrade 0033`→`upgrade head` прошли, группа `test_investment` (ADR-017).

**Более ранний прогон (2026-08-13, v8.17.0, миграция 0032)** — архивная запись:
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
