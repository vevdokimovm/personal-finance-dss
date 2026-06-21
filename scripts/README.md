# scripts/

## backup_db.sh — бэкап PostgreSQL

Создаёт сжатый дамп БД с временной меткой и ротацией.

```bash
chmod +x scripts/backup_db.sh
PGPASSWORD=... ./scripts/backup_db.sh /var/backups/finpilot
```

Параметры (окружение или `.env`): `PGHOST`, `PGPORT`, `PGUSER`, `PGDATABASE`, `PGPASSWORD`,
`BACKUP_RETENTION_DAYS` (по умолчанию 14).

### Расписание (cron, ежедневно в 03:30)

```cron
30 3 * * * /opt/finpilot/scripts/backup_db.sh /var/backups/finpilot >> /var/log/finpilot-backup.log 2>&1
```

### Восстановление из бэкапа

```bash
gunzip -c finpilot_finpilot_20260620_033000.sql.gz | psql -U finpilot -d finpilot
```

> Бэкапы по расписанию, их хранение вне сервера БД и регулярная проверка восстановления —
> зона ответственности эксплуатации (инфраструктура), а не приложения.
