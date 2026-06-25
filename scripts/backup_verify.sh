#!/usr/bin/env bash
#
# Проверка восстановимости бэкапа FINPILOT (P0.7).
# Бэкап, который ни разу не восстанавливали, — это не бэкап. Скрипт доказывает,
# что дамп реально разворачивается в рабочую БД:
#   1. берёт последний дамп из BACKUP_DIR (или делает свежий при MAKE_FRESH=1)
#   2. создаёт временную БД
#   3. восстанавливает в неё дамп
#   4. проверяет целостность (alembic_version, ключевые таблицы, читаемость)
#   5. удаляет временную БД (всегда, даже при ошибке)
#
# Использование:
#   ./scripts/backup_verify.sh [КАТАЛОГ_БЭКАПОВ]      # проверить последний бэкап
#   MAKE_FRESH=1 ./scripts/backup_verify.sh           # сделать свежий дамп и проверить
#
# Код выхода: 0 = бэкап валиден; !=0 = проблема (повесить на мониторинг/алерт).
#
set -euo pipefail

BACKUP_DIR="${1:-./backups}"
export PGHOST="${PGHOST:-localhost}"
export PGPORT="${PGPORT:-5432}"
export PGUSER="${PGUSER:-finpilot}"
SRC_DB="${PGDATABASE:-finpilot}"
VERIFY_DB="finpilot_verify_$(date +%Y%m%d_%H%M%S)"
CLEAN_DUMP=0

# 1. источник дампа
if [[ "${MAKE_FRESH:-0}" == "1" ]]; then
    DUMP="$(mktemp).sql.gz"
    echo "[verify] свежий дамп ${SRC_DB} → ${DUMP}"
    pg_dump --no-owner --no-privileges -d "$SRC_DB" | gzip > "$DUMP"
    CLEAN_DUMP=1
else
    DUMP="$(ls -1t "${BACKUP_DIR}"/finpilot_*.sql.gz 2>/dev/null | head -1 || true)"
    [[ -n "$DUMP" ]] || { echo "[verify] FAIL: в ${BACKUP_DIR} нет бэкапов finpilot_*.sql.gz" >&2; exit 1; }
    echo "[verify] проверяю последний бэкап: ${DUMP}"
fi

cleanup() {
    psql -d postgres -c "DROP DATABASE IF EXISTS ${VERIFY_DB};" >/dev/null 2>&1 || true
    [[ "$CLEAN_DUMP" == "1" && -f "$DUMP" ]] && rm -f "$DUMP"
}
trap cleanup EXIT

# 2. временная БД
createdb "$VERIFY_DB"

# 3. восстановление
gunzip -c "$DUMP" | psql -v ON_ERROR_STOP=1 -d "$VERIFY_DB" >/dev/null

# 4. проверки целостности
ALEMBIC=$(psql -tAc "SELECT count(*) FROM alembic_version;" -d "$VERIFY_DB")
TABLES=$(psql -tAc "SELECT count(*) FROM information_schema.tables WHERE table_schema='public';" -d "$VERIFY_DB")
USERS=$(psql -tAc "SELECT to_regclass('public.users') IS NOT NULL;" -d "$VERIFY_DB")

echo "[verify] таблиц: ${TABLES}, alembic_version строк: ${ALEMBIC}, users есть: ${USERS}"
if [[ "$TABLES" -gt 0 && "$ALEMBIC" -ge 1 && "$USERS" == "t" ]]; then
    echo "[verify] PASS — бэкап успешно восстановлен и прошёл проверку целостности"
    exit 0
else
    echo "[verify] FAIL — восстановленная БД не прошла проверку целостности" >&2
    exit 2
fi
