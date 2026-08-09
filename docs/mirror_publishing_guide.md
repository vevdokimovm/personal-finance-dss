# Руководство по публикации зеркала `finpilot` (внутреннее)

> **Приватный документ.** В паблик-зеркало НЕ уходит (нет в allow-list публикатора).
> Здесь всё про доступы, ключи и пуш публичной репы. Механика сборки — в
> `tools/publish/finpilot_publish_public.sh`, контракт «что и почему» — в
> `docs/public_mirror_manifest.md`. Меняешь состав — меняешь все три.

Публичное зеркало: **https://github.com/vevdokimovm/finpilot** (Public, PolyForm Noncommercial).
Приватный источник: `vevdokimovm/personal-finance-dss`.

---

## 1. GitHub-токен (Personal Access Token)

Для пуша по HTTPS обычный пароль GitHub не принимает — нужен токен (это как одноразовый пароль).

**Создать новый:**
1. Прямая ссылка: <https://github.com/settings/tokens>
   (или: аватарка справа сверху → **Settings** → внизу слева **Developer settings** →
   **Personal access tokens** → **Tokens (classic)**).
2. **Generate new token** → **Generate new token (classic)**.
3. Note: `finpilot`. Expiration: на вкус (можно `No expiration`, тогда живёт пока не удалишь).
4. Галка ТОЛЬКО на **`repo`** (верхний жирный чекбокс — выделит все подпункты). Больше ничего.
5. Внизу **Generate token** → **скопировать `ghp_…` сразу** (показывается ОДИН раз).

**Где он потом:** на GitHub его больше не видно (только звёздочки). После первого удачного
пуша он лежит в **Keychain** Mac (включён `git config --global credential.helper osxkeychain`).
Приложение **«Связка ключей»** → поиск `github.com`.

**Пересоздать (протух / потерял / скомпрометирован):** удали старый на
<https://github.com/settings/tokens> (кнопка **Delete**) и сделай новый по шагам выше.
Если git начнёт ругаться на старый из кейчейна — `git credential-osxkeychain erase` (введи
`host=github.com`, `protocol=https`, пустая строка) или удали запись `github.com` в «Связке ключей».

> **Токен = пароль. Никогда не вставляй его в чат, коммит, скрипт или скриншот.** В публикатор
> секреты не зашиваются — GUARD 2/3 специально роняет сборку на секрет-паттернах.

---

## 2. Пуш публичной репы

### 2.1. Через HTTPS + токен (просто, рекомендую)
```bash
git config --global credential.helper osxkeychain     # один раз — запомнит токен
git remote set-url origin https://github.com/vevdokimovm/finpilot.git
git push -u origin main
```
Спросит: `Username` → `vevdokimovm`; `Password` → **вставь токен** `ghp_…`
(в консоли невидимый — просто Cmd+V и Enter).

### 2.2. Через SSH (если предпочитаешь ключи вместо токена)
В РФ порт 22 к GitHub часто режется (`Connection closed ... port 22`). Лечится SSH через 443 —
один раз в `~/.ssh/config`:
```
Host github.com
  HostName ssh.github.com
  Port 443
  User git
```
Ключ должен быть привязан к аккаунту: `cat ~/.ssh/id_ed25519.pub` → GitHub → Settings →
**SSH and GPG keys** → New SSH key. Проверка: `ssh -T git@github.com` (ждём «Hi vevdokimovm!»).
Нет ключа — `ssh-keygen -t ed25519 -C "email"` + `ssh-add --apple-use-keychain ~/.ssh/id_ed25519`.

> Историческая заметка: первый публичный пуш (v5.18.3, 2026-07-04) прошёл по HTTPS+токен —
> SSH-ключ на тот момент не был привязан. Порт 443 соединение пробил, дело было только в ключе.

---

## 3. Публикатор `tools/publish/finpilot_publish_public.sh`

Собирает публичное дерево из приватного монорепо. Философия — **whitelist / deny-by-default**:
наружу уходит ТОЛЬКО перечисленное в allow-list, всё остальное не публикуется по определению.

**Запуск (из `~/Downloads`, скачанным .sh):**
```bash
zsh ~/Downloads/finpilot_publish_public.sh          # dry-run: показать что уйдёт + guard
zsh ~/Downloads/finpilot_publish_public.sh build    # собрать staging (~/dev/finpilot-public), без push
zsh ~/Downloads/finpilot_publish_public.sh push     # собрать + commit + push (git-retry под РФ-TLS встроен)
```
Пути под свою машину переопределяются без правки скрипта: `FINPILOT_SRC=... FINPILOT_STAGE=...`.

**Что уходит наружу (allow-list):** `app/`, `tests/`, `alembic/`, `frontend/`, инфра
(`deploy/ nginx/ loadtest/ scripts/ .github/`, Docker*, gunicorn, run.py, Makefile),
конфиги качества (`pyproject/pytest/.flake8/.mypy/.pylintrc/.pre-commit/.coveragerc`,
`requirements*`), env-шаблоны (`.env.example`, `deploy/env.prod.example`), корневые
`README/LICENSE/SECURITY.md`, и из `docs/` — **только `DEPLOY.md` + `RELEASES.md`**.

**Что НЕ уходит:** `knowledge/**` целиком, `tools/**`, `docs/` кроме двух выше (весь процесс,
баг-репорты, ADR, глоссарий, гайды, реестры, IP-доки: мат-модель/диаграммы/UI-стандарт),
`WATCHLOG/ROADMAP/roadmap_archive`, `CHANGELOG`, `LEGAL.md`, юр/операционная внутрянка,
`.env*` (кроме example), БД, кэши.

**Санитайзер (`sanitize_tree`, гоняется в конце сборки, ДО guard):**
1. `LICENSE` → **PolyForm Noncommercial** (в приватном репо MIT; текст — `tools/publish/LICENSE_public_polyform.txt`).
2. `README`: `personal-finance-dss`→`finpilot`, `© Vasilii Evdokimov`→`© FINPILOT`,
   `[MIT]`→`[PolyForm…]`, бейдж лицензии, бейдж версии → актуальная из `app/config.py`.
3. `docs/DEPLOY.md`: приватный clone-URL → публичный.
4. Тест-фикстуры: реальное имя в примерах выписок → `И. Иван Иванович`.

**GUARD (роняет сборку при любом совпадении):**
- **1/3** — запрещённые имена файлов (WATCHLOG, merge_manifest, реестры, `.env`, БД, сам публикатор).
- **2/3** — секрет-паттерны (Anthropic/AWS/GitHub-токены, PEM, org-id).
- **3/3** — личное имя (латиница+кириллица) и приватный репо в КОНТЕНТЕ. `vevdokimovm` в
  одиночку не флагается — это публичный логин.

> `vevdokimovm` (логин) в URL — норма. Флагается только реальное ФИО и ссылка на приватный монорепо.

---

## 4. После пуша
Отметить в `docs/ROADMAP.md` и `docs/WATCHLOG.md` §0: зеркало живо, дата, версия.
Версия коммита берётся из `app/config.py` автоматически (`Public mirror sync — vX.Y.Z`).
