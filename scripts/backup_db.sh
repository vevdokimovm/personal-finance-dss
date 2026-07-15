#!/usr/bin/env bash
#
# Бэкап PostgreSQL FINPILOT (P1.5).
#
# Использование:
#   ./scripts/backup_db.sh [КАТАЛОГ_БЭКАПОВ]
#
# Параметры через окружение (или .env на сервере):
#   PGHOST (localhost), PGPORT (5432), PGUSER (finpilot), PGDATABASE (finpilot),
#   PGPASSWORD (пароль), BACKUP_RETENTION_DAYS (14).
#
# Расписание (пример crontab — ежедневно в 03:30):
#   30 3 * * * /opt/finpilot/scripts/backup_db.sh /var/backups/finpilot >> /var/log/finpilot-backup.log 2>&1
#
set -euo pipefail

BACKUP_DIR="${1:-./backups}"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-14}"

export PGHOST="${PGHOST:-localhost}"
export PGPORT="${PGPORT:-5432}"
export PGUSER="${PGUSER:-finpilot}"
export PGDATABASE="${PGDATABASE:-finpilot}"

mkdir -p "$BACKUP_DIR"
STAMP="$(date +%Y%m%d_%H%M%S)"
OUTFILE="${BACKUP_DIR}/finpilot_${PGDATABASE}_${STAMP}.sql.gz"

echo "[$(date '+%F %T')] Бэкап ${PGDATABASE} → ${OUTFILE}"
pg_dump --no-owner --no-privileges | gzip > "$OUTFILE"
echo "[$(date '+%F %T')] Готово: $(du -h "$OUTFILE" | cut -f1)"

# Ротация: удаляем бэкапы старше RETENTION_DAYS дней.
find "$BACKUP_DIR" -name 'finpilot_*.sql.gz' -mtime +"${RETENTION_DAYS}" -delete
echo "[$(date '+%F %T')] Ротация: удалены бэкапы старше ${RETENTION_DAYS} дн."
