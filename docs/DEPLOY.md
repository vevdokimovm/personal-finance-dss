# FINPILOT — деплой на VPS (production)

> 🔴 **Прежде чем выполнять команды отсюда — `docs/deploy_owner_checklist.md`.**
> Там перечислено, что должно быть на руках до первой команды: домен, VPS, DNS,
> рабочий SMTP. Половина этих пунктов требует денег или ожидания в несколько дней,
> и обнаружить нехватку посреди вечера деплоя значит встать на неделю.

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
cp deploy/env.prod.example .env

# Сгенерировать стойкие секреты
openssl rand -hex 32   # → JWT_SECRET
openssl rand -hex 24   # → ADMIN_API_KEY
openssl rand -hex 24   # → POSTGRES_PASSWORD

# TOKEN_ENCRYPTION_KEY — ОБЯЗАТЕЛЬНО через Fernet.generate_key(), не openssl rand:
# формат ключа строгий (32 url-safe base64 байта), hex-строка не подходит и уронит
# приложение при старте (TokenCipher.__init__ -> ValueError, до fail-loud проверки).
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"  # → TOKEN_ENCRYPTION_KEY

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
прогонятся автоматически на старте), `nginx` (80/443, TLS). `nginx` собирается из своего
`Dockerfile` (`nginx/Dockerfile`) — на стадии сборки внутри контейнера прогоняется прод-сборка
SPA (`npm ci && npm run build` в `frontend/`), готовый `dist/` копируется в образ. Руками
`npm run build` на хосте запускать не нужно — `docker compose up --build` делает это сам.

---

## Шаг 5.1. Кто что отдаёт (nginx: SPA vs FastAPI)

Веха 8 перенесла основные экраны (дашборд, планирование, операции, обязательства, цели,
банки, профиль) на React SPA; второстепенные (контакты, юр-документы, восстановление пароля,
гостевая песочница валидации) и весь API остаются на FastAPI/Jinja. `nginx/templates/finpilot.conf.template`
разводит это так:

- **SPA (статика из `nginx`-образа, `/usr/share/nginx/html`):** `/`, `/planning`, `/transactions`,
  `/obligations`, `/goals`, `/banks`, `/profile`, `/assets/*` (хэшированные JS/CSS, кэш на год).
  Все эти пути отдают `index.html`, роутинг — на клиенте (TanStack Router).
- **FastAPI (`proxy_pass` на `web:8000`) — всё остальное по умолчанию:** `/api/*`, `/v1/*` (B2B),
  `/health`, `/docs`/`/openapi.json`, `/static/*` (статика Jinja-страниц), `/contacts`,
  `/legal/*`, `/validation`. Специально НЕ перечислены поимённо в конфиге — location `/` ловит их
  как fallback, поэтому новый бэкенд-роут (включая `/docs`) не требует правки nginx.
  `/reset-password`/`/forgot-password` — теперь SPA (regex ниже), не FastAPI-фолбэк: React-версии
  живут с v8.22.0, Jinja-роуты `app/main.py` снесены вместе с остальными перенесёнными экранами
  (v8.23.0, ниже).

**Если во фронте появляется новый корневой SPA-экран** (`frontend/src/routes/*.tsx`) — добавь
его в regex `location ~ ^/(planning|transactions|...)` конфига, иначе nginx проксирует путь
в FastAPI, где для перенесённых на React экранов Jinja-роута уже может не быть (см. ниже).

**Важно: regex выше уже перехватывает `planning`/`transactions`/`obligations`/`goals`/`banks`/
`profile` на nginx-уровне — это значит, что их Jinja-версии в `app/main.py` в проде НЕ
достижимы обычным доменным трафиком уже сейчас, только через `127.0.0.1:8000` в обход nginx.**
React-версии этих шести — read-only (нет форм создания/редактирования, только
`profile`/`forgot-password`/`reset-password` — полный паритет). Jinja-роуты сохранены (не снесены
v8.23.0 — снесены только `profile`/`forgot-password`/`reset-password`/мёртвый `templates/
index.html`, полный разбор и найденная при исполнении ошибка первого прохода —
`docs/reports/decisions/2026-08-14_jinja_frontend_removal.md`) именно как этот аварийный
доступ — единственный путь до форм создания операции/обязательства/цели/актива/бюджета, пока
React их не получил. Само по себе то, что nginx уже прячет эти формы от обычного доменного
трафика, — отдельный, более старый вопрос (regex стоял ДО v8.22.0/v8.23.0), не предмет этого
батча; если владелец не подтверждал этот пробел раньше — стоит проверить отдельно.
`contacts.html`/`legal/*.html`/`validation.html` и общая `base.html`/`app.js`/`auth.js` остаются
на Jinja до React-замены — снос остатка запланирован как часть Э6.

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

1. **SMTP** — зарегистрируйся, дойдёт ли письмо верификации; сброс пароля.
   🔴 **Оговорка «без рабочего SMTP подтверждение идёт по ссылке в ответе» БОЛЬШЕ
   НЕ ВЕРНА (v9.6.0).** На проде ссылка в ответ не кладётся вовсе: иначе любой, знающий
   чужой адрес, менял бы чужой пароль запросом `forgot-password`. И само приложение
   с пустым SMTP на проде теперь не поднимается — старт-гард требует почту, потому что
   без неё пользователь теряет единственный путь восстановления доступа, получая при этом
   ответ «ссылка отправлена».
2. **Живой fetch курсов ЦБ** — `./scripts/cron_fx_refresh.sh`, проверь что курсы обновились
   (источник не `fallback`). Важно: cbr.ru **отдаёт 403 на IP многих дата-центров**
   (DDoS-защита) — фетч работает только с IP, который ЦБ не блокирует (обычно РФ-хостинг).
   Если на VPS курсы стабильно остаются `fallback` — причина чаще в этом, а не в коде:
   проверь вручную `curl -A "Mozilla/5.0" https://www.cbr.ru/scripts/XML_daily.asp`; если 403 —
   нужен другой IP/хостинг. Запасной источник — зеркало `cbr-xml-daily.ru` (отдаёт идентичный
   формат XML_daily), но для фин-продукта полагаться на стороннее зеркало решай осознанно —
   оно вне твоего контроля. При недоступности поведение безопасно: приложение не падает,
   берёт последние известные курсы из БД.
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
