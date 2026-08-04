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

---

## setup_claude_code_plugins.sh — инструментальный контур вехи 8

Ставит плагины Claude Code, зафиксированные в `docs/reports/adr/adr_011_milestone8_tooling.md` §2.3.
Идемпотентен: повторный запуск безопасен. Это единственное действие вехи 8, которое нельзя
выполнить из песочницы — плагины ставятся на машине разработчика.

```zsh
zsh ~/Downloads/setup_claude_code_plugins.sh
```

После установки в каталоге репозитория:

```
claude
/plugin          # проверить список
claude doctor    # проверить, не раздут ли контекст
```

Ставятся только плагины, проверенные Anthropic, и официальные MCP. Плагины сообщества без
верификации не ставятся сознательно: продукт обрабатывает персональные данные, и непроверенный
сторонний код в агентском цикле — не та экономия. Обоснование — ADR-011 §2.3.

Если плагин не поставился, имя могло измениться — поставить вручную через `/plugin`.
