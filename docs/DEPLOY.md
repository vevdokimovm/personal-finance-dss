# FINPILOT — деплой на VPS (production)

> От чистого сервера до `https://твойдомен.ru`, доступного в интернете.
> Учтено: 152-ФЗ (данные граждан РФ на сервере в РФ), Docker Hub geo-blocked (мирроры),
> fail-loud прод-конфигурация, том БД переживает redeploy (BUG-010).

Предпосылки: VPS на **Ubuntu 24.04 LTS** в дата-центре РФ (2 vCPU / 2–4 ГБ RAM / 40+ ГБ SSD),
домен в зоне **.ru**, репозиторий на GitHub. Деплой ведётся в `/opt/finpilot`.

---

## Шаг 1. Сервер: пользователь, firewall, Docker

```bash
ssh root@<IP-сервера>

# Система
apt update && apt upgrade -y

# Отдельный пользователь (не работать под root постоянно)
adduser deploy && usermod -aG sudo deploy

# Firewall: только SSH, HTTP, HTTPS
ufw allow 22 && ufw allow 80 && ufw allow 443 && ufw enable
```

Установить Docker по официальной инструкции для Ubuntu. Из-за блокировки Docker Hub — настроить миррор:

```bash
# /etc/docker/daemon.json
{
  "registry-mirrors": ["https://dh-mirror.gitverse.ru", "https://dockerhub.timeweb.cloud"]
}
```

```bash
systemctl restart docker
docker --version && docker compose version
usermod -aG docker deploy    # дальше работаем под deploy
```

---

## Шаг 2. Код

```bash
sudo mkdir -p /opt/finpilot && sudo chown deploy:deploy /opt/finpilot
git clone https://github.com/vevdokimovm/personal-finance-dss.git /opt/finpilot
cd /opt/finpilot
```

---

## Шаг 3. Боевые переменные (.env)

```bash
cp .env.prod.example .env

# Сгенерировать стойкие секреты
openssl rand -hex 32   # → JWT_SECRET
openssl rand -hex 32   # → TOKEN_ENCRYPTION_KEY
openssl rand -hex 24   # → ADMIN_API_KEY
openssl rand -hex 24   # → POSTGRES_PASSWORD

nano .env              # заполнить DOMAIN, секреты, SMTP, LEGAL_*
```

`.env` **не коммитить** (он уже в `.gitignore`). Без обязательных секретов приложение
не стартует (fail-loud) — это by design, а не баг.

---

## Шаг 3.1. SMTP (почта) — настройка для РФ

Почта используется для писем: верификация email, сброс пароля, напоминания о целях,
дайджесты. Без SMTP приложение **работает** (graceful no-op): верификация идёт по ссылке
в ответе API, остальные письма просто не шлются. Для прода SMTP нужен.

**Чем отправлять (РФ).** Для своего домена-отправителя (`noreply@finpilot.ru`) есть два пути:

1. **Почта для домена** — Яндекс 360 или Mail.ru для бизнеса. Привязываешь домен, заводишь
   ящик `noreply@`, шлёшь через их SMTP. Просто и бесплатно на старте.
2. **Транзакционный сервис** (когда писем много) — Unisender Go, Mailopost, SMTP.bz и т.п.
   Лучшая доставляемость, аналитика, выше лимиты. Зарубежные (Mailgun/SendGrid) из РФ
   подключать рискованно — доступ нестабилен.

**Пример: Яндекс 360.** SMTP-сервер `smtp.yandex.ru`, порт `465` (SSL) или `587` (STARTTLS).
Пароль — **пароль приложения**, не основной пароль аккаунта: создаётся в Яндекс ID →
Безопасность → Пароли приложений → «Почта (SMTP)». При включённой 2FA это обязательно.

**Заполнение `.env`:**

```bash
SMTP_HOST=smtp.yandex.ru
SMTP_PORT=465
SMTP_USER=noreply@finpilot.ru
SMTP_PASSWORD=<пароль_приложения>      # НЕ основной пароль
SMTP_FROM=noreply@finpilot.ru
SMTP_USE_TLS=false                     # false = SSL (465); true = STARTTLS (587)
```

> Соответствие порт↔TLS: `SMTP_USE_TLS=false` → SSL, обычно порт `465`.
> `SMTP_USE_TLS=true` → STARTTLS, обычно порт `587`. Не перепутай — иначе отвалится
> рукопожатие и письма не уйдут (это улетит в лог как `Не удалось отправить письмо`).

**Доставляемость (чтобы письма не падали в спам).** В DNS домена настрой:
- **SPF** — TXT-запись, разрешающая отправку через выбранного провайдера.
- **DKIM** — подпись писем (ключ даёт провайдер).
- **DMARC** — политика для несоответствующих писем.

Провайдер (Яндекс/транзакционный) даёт точные значения этих записей в своей панели.

**Проверка после запуска:**
```bash
# Зарегистрировать тестовый аккаунт через UI или API и убедиться, что письмо дошло.
# Либо разовая ручная проверка прямо в контейнере:
docker compose -f docker-compose.prod.yml exec web python -c \
"from app.services.email_service import EmailService; \
print('sent:', EmailService().send_welcome('ТВОЙ_АДРЕС@example.com', 'Test'))"
# Ожидаемо: sent: True и письмо в ящике. sent: False → смотри логи (порт/TLS/пароль).
```

---

## Шаг 4. TLS-сертификат (ДО первого запуска)

nginx не стартует без сертификата, поэтому выпускаем его первым. Порт 80 пока свободен →
используем `--standalone`:

```bash
sudo apt install -y certbot
sudo certbot certonly --standalone -d твойдомен.ru -d www.твойдомен.ru
```

> Домен уже должен указывать на сервер: в панели регистратора создай **A-запись** `@` и `www`
> → IP сервера, дождись обновления DNS (от минут до пары часов). Проверка: `dig +short твойдомен.ru`.

Сертификат окажется в `/etc/letsencrypt/live/твойдомен.ru/` — его примонтирует nginx-контейнер.

---

## Шаг 5. Запуск

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

Поднимется три контейнера: `db` (PostgreSQL, том `finpilot_pgdata`), `web` (gunicorn, миграции
прогонятся автоматически на старте), `nginx` (80/443, TLS).

---

## Шаг 6. Проверка

```bash
docker compose -f docker-compose.prod.yml ps        # все три — healthy
docker compose -f docker-compose.prod.yml logs web  # нет ошибок старта, миграции прошли
curl -s http://127.0.0.1:8000/health                # {"status":"ok","database":"ok",...}
```

Открыть `https://твойдомен.ru` в браузере — должен отдаться сайт с валидным TLS.

---

## Шаг 7. Расписание (systemd timers)

Скопировать unit-файлы, поправить пути если проект не в `/opt/finpilot`:

```bash
sudo cp deploy/systemd/finpilot-*.{service,timer} /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now finpilot-notifications.timer finpilot-fx.timer finpilot-backup.timer
systemctl list-timers 'finpilot-*'                  # проверить расписание
```

Что делают: рассылка уведомлений/дайджеста (ежедневно 08:00), обновление курсов ЦБ
(по будням 12:30), бэкап БД (ежедневно 03:30). Все идемпотентны и читают `.env`.

> Альтернатива cron вместо systemd (если предпочитаешь):
> ```
> 0  8 * * *  cd /opt/finpilot && set -a && . ./.env && ./scripts/cron_notifications.sh >> /var/log/finpilot-notify.log 2>&1
> 30 12 * * 1-5 cd /opt/finpilot && set -a && . ./.env && ./scripts/cron_fx_refresh.sh  >> /var/log/finpilot-fx.log 2>&1
> 30 3 * * *  cd /opt/finpilot && set -a && . ./.env && PGHOST=127.0.0.1 PGUSER=finpilot PGDATABASE=finpilot PGPASSWORD="$POSTGRES_PASSWORD" ./scripts/backup_db.sh /var/backups/finpilot >> /var/log/finpilot-backup.log 2>&1
> ```

---

## Шаг 8. Проверка восстановимости бэкапа

Бэкап без проверки восстановления — не бэкап. Прогнать вручную и периодически (или повесить на timer):

```bash
cd /opt/finpilot
set -a && . ./.env && set +a
export PGHOST=127.0.0.1 PGUSER=finpilot PGDATABASE=finpilot PGPASSWORD="$POSTGRES_PASSWORD"

./scripts/backup_verify.sh /var/backups/finpilot     # PASS = бэкап разворачивается
```

Восстановление из конкретного дампа (если понадобится):
```bash
./scripts/restore_db.sh /var/backups/finpilot/finpilot_finpilot_YYYYMMDD_HHMMSS.sql.gz
```

---

## Шаг 9. Автообновление TLS

nginx занимает порт 80, поэтому renew — через webroot (директория `nginx/www` смонтирована в контейнер):

```bash
# тест обновления (ничего не меняет)
sudo certbot renew --dry-run --webroot -w /opt/finpilot/nginx/www

# после успешного обновления nginx должен перечитать сертификат — добавить hook:
echo 'docker compose -f /opt/finpilot/docker-compose.prod.yml exec nginx nginx -s reload' \
  | sudo tee /etc/letsencrypt/renewal-hooks/deploy/reload-finpilot-nginx.sh
sudo chmod +x /etc/letsencrypt/renewal-hooks/deploy/reload-finpilot-nginx.sh
```

Системный таймер `certbot.timer` (ставится с пакетом) сам запускает renew дважды в сутки.

---

## После запуска: что проверить на проде (чего нет в песочнице)

1. **SMTP** — зарегистрируйся, дойдёт ли письмо верификации; сброс пароля. Без рабочего SMTP
   подтверждение идёт по ссылке в ответе (self-hosted режим).
2. **Живой fetch курсов ЦБ** — `./scripts/cron_fx_refresh.sh`, проверь что курсы обновились
   (источник не `fallback`). cbr.ru доступен только с РФ-IP.
3. **БД переживает redeploy** — `docker compose -f docker-compose.prod.yml down && up -d`,
   убедись что аккаунты на месте (том `finpilot_pgdata`).
4. **Заголовки безопасности** — `curl -sI https://твойдомен.ru` содержит HSTS, X-Frame-Options и пр.

---

## Обновление версии (redeploy)

```bash
cd /opt/finpilot
git pull
docker compose -f docker-compose.prod.yml up -d --build   # миграции прогонятся сами
```

Данные сохраняются (том именованный). Перед обновлением — свежий бэкап (Шаг 8).

**Бюджет:** ~500–1000 ₽/мес (VPS) + ~300 ₽/год (домен). TLS — бесплатно (Let's Encrypt).
