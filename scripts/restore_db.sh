#!/usr/bin/env bash
#
# Восстановление БД FINPILOT из бэкапа (.sql.gz), парный к backup_db.sh.
# ОПАСНО: данные в целевой БД будут перезаписаны содержимым дампа.
#
# Использование:
#   ./scripts/restore_db.sh <файл.sql.gz> [PGDATABASE]
#
# Параметры окружения: PGHOST, PGPORT, PGUSER, PGPASSWORD (как в backup_db.sh).
#
set -euo pipefail

DUMP="${1:?укажи путь к дампу .sql.gz}"
[[ -f "$DUMP" ]] || { echo "Файл не найден: $DUMP" >&2; exit 1; }

export PGHOST="${PGHOST:-localhost}"
export PGPORT="${PGPORT:-5432}"
export PGUSER="${PGUSER:-finpilot}"
TARGET_DB="${2:-${PGDATABASE:-finpilot}}"

echo "[$(date '+%F %T')] Восстановление ${DUMP} → БД ${TARGET_DB}"
gunzip -c "$DUMP" | psql -v ON_ERROR_STOP=1 -d "$TARGET_DB"
echo "[$(date '+%F %T')] Готово"
