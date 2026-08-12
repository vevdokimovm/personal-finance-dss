#!/usr/bin/env bash
# =============================================================================
# finpilot_publish_public.sh — v2 (тег + релиз + описание)
#
# Сборка и публикация ПУБЛИЧНОГО зеркала (репо vevdokimovm/finpilot) из
# ПРИВАТНОГО монорепо (vevdokimovm/personal-finance-dss).
#
# Философия: whitelist / deny-by-default. Наружу уходит ТОЛЬКО то, что явно
# перечислено ниже. Всё остальное (WATCHLOG, мёрж-манифесты, реестры
# инцидентов, юр-вопросы, бизнес-анализ, опросы, секреты) не публикуется
# по определению — оно просто не входит в allow-list.
#
# Слои защиты:
#   sanitize_tree — обезличивание + PolyForm-лицензия + версия (перед guard);
#   GUARD 1/3 — запрещённые имена файлов; 2/3 — секрет-паттерны;
#   3/3 — личные имена и приватный репо в контенте;
#   guard_notes — тот же скан для ТЕКСТА релиза перед его публикацией.
#
# v2 (по аналогии с приватным finpilot_publish_private.sh): после push зеркало
# получает git-тег vX.Y.Z и оформленный GitHub Release с заголовком и
# описанием. Источник описания: tools/publish/public_release_notes.md
# (секции `## [X.Y.Z]`, написанные ДЛЯ публики) → при отсутствии секции
# генерируется нейтральная заготовка. CHANGELOG/WATCHLOG приватного репо
# НЕ используются: там внутренняя кухня (вахты, аккаунты, процесс).
#
# [!] АССЕТЫ К ПУБЛИЧНЫМ РЕЛИЗАМ НЕ ПРИКЛАДЫВАЮТСЯ. Архив finpilot_v*_intl.zip
#     содержит ПОЛНОЕ ПРИВАТНОЕ дерево (knowledge/, docs/, tools/) — прикрепить
#     его к публичному релизу = слить всё разом. Исходники зеркала GitHub
#     прикладывает к релизу сам (Source code zip/tar.gz).
#
# Запуск (из Downloads, как принято в проекте):
#   zsh ~/Downloads/finpilot_publish_public.sh            # dry-run (по умолчанию)
#   zsh ~/Downloads/finpilot_publish_public.sh build      # собрать staging, без push
#   zsh ~/Downloads/finpilot_publish_public.sh push       # сборка + commit + push + тег + релиз
#   zsh ~/Downloads/finpilot_publish_public.sh release    # только тег + релиз для версии в staging
#                                                         # (если push уже был, а релиз не оформился)
#
# Переопределение путей без правки скрипта:
#   FINPILOT_SRC=/path/to/private FINPILOT_STAGE=/path/to/stage \
#     zsh ~/Downloads/finpilot_publish_public.sh build
#
# Требования: git; для фазы релиза — gh (brew install gh && gh auth login).
# Без gh push/тег пройдут, релиз-фаза даст команду для ручного оформления.
# =============================================================================

set -euo pipefail

# ── КОНФИГ (проверь пути под свою машину) ────────────────────────────────────
# Приватное монорепо (источник):
SOURCE_REPO="${FINPILOT_SRC:-$HOME/PycharmProjects/personal-finance-dss}"
# Рабочая папка публичного зеркала (git-клон finpilot):
STAGING_DIR="${FINPILOT_STAGE:-$HOME/dev/finpilot-public}"
# Remote публичной репы. Практика проекта — HTTPS + токен (см.
# docs/mirror_publishing_guide.md §2.1); SSH из РФ требует порт 443.
PUBLIC_REMOTE="${FINPILOT_REMOTE:-https://github.com/vevdokimovm/finpilot.git}"
PUBLIC_BRANCH="${FINPILOT_BRANCH:-main}"
# Слаг репы для gh CLI (оформление релизов):
PUBLIC_REPO_SLUG="${FINPILOT_SLUG:-vevdokimovm/finpilot}"

# ── Абсолютные пути к утилитам (правило 4: без опоры на PATH) ─────────────────
RM=/bin/rm
CP=/bin/cp
MKDIR=/bin/mkdir
FIND=/usr/bin/find
GREP=/usr/bin/grep
RSYNC=/usr/bin/rsync
DU=/usr/bin/du
WC=/usr/bin/wc
SORT=/usr/bin/sort
MKTEMP=/usr/bin/mktemp
SED=/usr/bin/sed
HEAD=/usr/bin/head
BASENAME=/usr/bin/basename
DIRNAME=/usr/bin/dirname
TR=/usr/bin/tr
CUT=/usr/bin/cut
PY3="$(command -v python3 || echo /usr/bin/python3)"
# git бывает и в /usr/bin, и в /usr/local/bin (brew) — резолвим:
GIT="$(command -v git || echo /usr/bin/git)"
# gh может отсутствовать — тогда релиз-фаза деградирует с подсказкой:
GH="$(command -v gh || true)"

TITLE_TMP="/tmp/fp_pub_public_title.txt"
NOTES_TMP="/tmp/fp_pub_public_notes.md"

# ── ALLOW-LIST: директории (копируются целиком, минус кэши) ───────────────────
ALLOW_DIRS=(
  app
  tests
  frontend
  alembic
  deploy
  nginx
  loadtest
  scripts
  .github
)

# ── ALLOW-LIST: файлы в корне ────────────────────────────────────────────────
ALLOW_FILES=(
  README.md
  LICENSE
  SECURITY.md
  Makefile
  Dockerfile
  docker-compose.yml
  docker-compose.prod.yml
  docker-entrypoint.sh
  .dockerignore
  gunicorn_conf.py
  run.py
  requirements.txt
  requirements-dev.txt
  pyproject.toml
  pytest.ini
  alembic.ini
  .coveragerc
  .flake8
  .mypy.ini
  .pylintrc
  .pre-commit-config.yaml
  .gitignore
  .env.example
  deploy/env.prod.example
)

# ── ALLOW-LIST: docs (МИНИМУМ — только нужное для запуска; правило v5.18.4) ───
# Внутренняя кухня разработки (процесс/CONTRIBUTING, баг-репорты, ADR, глоссарий,
# гайды, реестры инцидентов) НЕ публикуется — это конфиденциальная информация
# компании. IP-доки (мат-модель, диаграммы, UI-стандарт) закрыты (OPTIONAL ниже).
ALLOW_DOCS=(
  DEPLOY.md
  RELEASES.md
)

# ── OPTIONAL docs: раскрывают IP / стратегию. Раскомментируй осознанно ────────
# Это ядро продукта и планы. По умолчанию НЕ публикуются (конкуренты).
OPTIONAL_DOCS=(
  # math_model_v3_5_0.md          # математическая модель — ядро алгоритма (IP)
  # algorithm_stack.md            # стек алгоритмов (IP)
  # reference_profiles.md         # эталонные риск-профили (часть модели)
  # diagrams.md                   # архитектурные диаграммы
  # ui_ux_design_standard.md      # 88KB внутренний UI-стандарт
  # ROADMAP.md                    # дорожная карта / стратегия
  # testing_infrastructure.md     # внутренняя тестовая кухня
  # test_run_optimization.md
  # documentation_methodology.md
)

# ── MIRROR-EXTRAS: файлы ТОЛЬКО для зеркала (в приватном репо не работают) ────
# Пример: CodeQL бесплатен на публичных репо, на приватном без Advanced
# Security воркфлоу просто падал бы. Дерево extras накладывается поверх
# собранного зеркала ДО санитайзера (guard его тоже сканирует).
MIRROR_EXTRAS_DIR="$SOURCE_REPO/tools/publish/mirror_extras"

# ── DENY-LIST: паттерны имён, которые НИКОГДА не должны утечь (двойная сетка) ──
# Даже если случайно попадут в allow — guard поймает по имени и уронит сборку.
DENY_NAME_PATTERNS=(
  'WATCHLOG.md'
  'merge_manifest_*.md'
  'merge_and_fork_guide.md'
  'incidents_summary.md'
  'investigations_summary.md'
  'legal_questions_for_lawyer.md'
  'pitfalls.md'
  'sandbox_runbook.md'
  'tool_call_channel_failures.md'
  '.env'
  '.env.prod'
  '.env.local'
  '*.db'
  '*.sqlite'
  '*.sqlite3'
  'finpilot_publish_public.sh'
  'public_release_notes.md'
)

# ── Секрет-паттерны (ERE, BSD-grep совместимо). Найдено → FAIL ────────────────
SECRET_PATTERNS=(
  'sk-ant-[A-Za-z0-9_-]{10,}'                 # Anthropic API / admin ключи
  'sk-[A-Za-z0-9]{32,}'                       # generic secret keys
  'AKIA[0-9A-Z]{16}'                          # AWS access key id
  'BEGIN [A-Z ]*PRIVATE KEY'                  # приватные ключи PEM
  'ghp_[A-Za-z0-9]{30,}'                      # GitHub personal token
  'eb2988ac-e9ba|bc43a107-d24a|a583ff32-acec' # твои Anthropic org id (M/J/S)
)

# ── Контент-паттерн приватности (GUARD 3/3 дерева И guard_notes релиза) ───────
# Реальное имя владельца (латиница+кириллица) и приватный монорепо не должны
# утечь. `vevdokimovm` в одиночку не флагаем — публичный логин.
NAME_RE='Vasilii|Evdokimov|Василий|Василия|Евдокимов|personal-finance-dss'
# Для ТЕКСТА релиза сетка шире: внутренняя кухня процесса (вахты, аккаунты,
# журнал, Claude) в публичном описании неуместна → FAIL, перепиши секцию.
NOTES_RE="$NAME_RE"'|WATCHLOG|вахт|аккаунт|Claude|клод'

# ── rsync excludes: мусор и локальные артефакты ──────────────────────────────
RSYNC_EXCLUDES=(
  --exclude '__pycache__'
  --exclude '*.py[cod]'
  --exclude '.mypy_cache'
  --exclude '.pytest_cache'
  --exclude '.hypothesis'
  --exclude '.ruff_cache'
  --exclude '__screenshots__'
  --exclude '*.db'
  --exclude '*.sqlite'
  --exclude '*.sqlite3'
  --exclude '.DS_Store'
  --exclude 'finpilot_publish_public.sh'   # сам публикатор не публикуется
  # [!] v8.1.0. Урок сборки v8.0.0: allow-list по КАТАЛОГУ пропускает всё, что в этот
  # каталог положат позже. deploy/ разрешён целиком — и вместе с ним чуть не уехал
  # универсальный деплойер с картой ВСЕХ репозиториев владельца. Ниже — точечные
  # исключения внутри разрешённых каталогов. Добавляя файл в allow-каталог, проверь,
  # не место ли ему здесь. Разбор — docs/public_mirror_state.md §5.
  --exclude 'publish'                      # deploy/publish/ — деплойер с картой репозиториев
  --exclude 'setup_claude_code_plugins.sh' # инструментальный контур агента
)

# ── Хелперы ──────────────────────────────────────────────────────────────────
log()  { /bin/echo ">> $*"; }
warn() { /bin/echo "!! $*" >&2; }
die()  { /bin/echo "XX $*" >&2; exit 1; }

resolve_version() {
  # Достаём APP_VERSION из app/config.py для коммита/тега/релиза
  "$GREP" -Eo 'default="[0-9]+\.[0-9]+\.[0-9]+"' "$SOURCE_REPO/app/config.py" \
    | "$GREP" -Eo '[0-9]+\.[0-9]+\.[0-9]+' | "$HEAD" -1
}

staging_version() {
  # Версия дерева, реально лежащего в staging (для режима release)
  "$GREP" -Eo 'default="[0-9]+\.[0-9]+\.[0-9]+"' "$STAGING_DIR/app/config.py" \
    | "$GREP" -Eo '[0-9]+\.[0-9]+\.[0-9]+' | "$HEAD" -1
}

git_retry() {
  # GitHub из РФ ловит TLS-таймауты — 3 попытки (практика проекта)
  local n=0
  until "$GIT" "$@"; do
    n=$((n + 1))
    [ "$n" -ge 3 ] && die "git $* — не удалось после 3 попыток"
    warn "git $* — попытка $n не прошла, повтор через 5с..."
    /bin/sleep 5
  done
}

gh_retry() {
  local n=0
  until "$GH" "$@"; do
    n=$((n + 1))
    [ "$n" -ge 3 ] && return 1
    warn "gh $* — попытка $n не прошла, повтор через 5с..."
    /bin/sleep 5
  done
}

# ── Сборка дерева в целевую папку (первый аргумент) ──────────────────────────
build_tree() {
  local dest="$1"
  [ -d "$SOURCE_REPO" ] || die "Источник не найден: $SOURCE_REPO (задай FINPILOT_SRC=...)"

  log "Копирую директории..."
  local d
  for d in "${ALLOW_DIRS[@]}"; do
    if [ -d "$SOURCE_REPO/$d" ]; then
      "$MKDIR" -p "$dest/$d"
      "$RSYNC" -a "${RSYNC_EXCLUDES[@]}" "$SOURCE_REPO/$d/" "$dest/$d/"
    else
      warn "нет директории $d — пропуск"
    fi
  done

  log "Копирую корневые файлы..."
  local f
  for f in "${ALLOW_FILES[@]}"; do
    if [ -f "$SOURCE_REPO/$f" ]; then
      "$CP" -p "$SOURCE_REPO/$f" "$dest/$f"
    else
      warn "нет файла $f — пропуск"
    fi
  done

  log "Копирую docs (нейтральная тех-документация)..."
  "$MKDIR" -p "$dest/docs"
  local doc
  for doc in "${ALLOW_DOCS[@]}"; do
    if [ -f "$SOURCE_REPO/docs/$doc" ]; then
      "$CP" -p "$SOURCE_REPO/docs/$doc" "$dest/docs/$doc"
    else
      warn "нет docs/$doc — пропуск"
    fi
  done
  for doc in "${OPTIONAL_DOCS[@]}"; do
    [ -f "$SOURCE_REPO/docs/$doc" ] && "$CP" -p "$SOURCE_REPO/docs/$doc" "$dest/docs/$doc"
  done

  if [ -d "$MIRROR_EXTRAS_DIR" ]; then
    log "Накладываю mirror-extras (файлы только для зеркала: CodeQL и т.п.)..."
    "$RSYNC" -a "${RSYNC_EXCLUDES[@]}" "$MIRROR_EXTRAS_DIR/" "$dest/"
  fi

  sanitize_tree "$dest"
}

# ── Санитайзер: обезличивание + публичная лицензия + актуальная версия ────────
# Приватный репо держит MIT и реальное имя владельца в README/LICENSE/фикстурах.
# Наружу это уходить НЕ должно. Функция гоняется в конце сборки, ДО guard.
# BSD/macOS sed → синтаксис `sed -i ''`.
sanitize_tree() {
  local dest="$1"
  local ver; ver="$(resolve_version || echo 0.0.0)"
  log "SANITIZE: обезличивание + PolyForm-лицензия + версия ${ver}..."

  # 1. LICENSE: MIT (приват) → PolyForm Noncommercial (source-available наружу).
  #    Текст живёт в файле рядом со скриптом, чтобы не хардкодить в sh.
  if [ -f "$SOURCE_REPO/tools/publish/LICENSE_public_polyform.txt" ]; then
    "$CP" -p "$SOURCE_REPO/tools/publish/LICENSE_public_polyform.txt" "$dest/LICENSE"
  else
    warn "нет tools/publish/LICENSE_public_polyform.txt — LICENSE НЕ заменён на PolyForm!"
  fi

  # 2. README: приватный репо→finpilot, имя→FINPILOT, лицензия MIT→PolyForm, версия-бейдж.
  if [ -f "$dest/README.md" ]; then
    "$SED" -i '' \
      -e 's|vevdokimovm/personal-finance-dss|vevdokimovm/finpilot|g' \
      -e 's|© 2025 Vasilii Evdokimov|© 2025 FINPILOT|g' \
      -e 's|\[MIT\](LICENSE)|[PolyForm Noncommercial 1.0.0](LICENSE)|g' \
      -e 's|badge/license-MIT-green|badge/license-PolyForm%20Noncommercial-orange|g' \
      -e "s|badge/version-[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*|badge/version-${ver}|g" \
      "$dest/README.md"
  fi

  # 3. DEPLOY: приватный clone-URL → публичный.
  [ -f "$dest/docs/DEPLOY.md" ] && \
    "$SED" -i '' 's|vevdokimovm/personal-finance-dss|vevdokimovm/finpilot|g' "$dest/docs/DEPLOY.md"

  # 4. Тест-фикстуры: реальное имя в примерах выписок → нейтральное.
  "$GREP" -rIl 'Василий Максимович' "$dest" 2>/dev/null | while IFS= read -r f; do
    "$SED" -i '' 's|Е\. Василий Максимович|И. Иван Иванович|g' "$f"
  done

  # 5. Ссылки на НЕОПУБЛИКОВАННЫЕ внутренние документы. Добавлено в v8.1.0: три утечки
  #    из четырёх в сборке v8.0.0 были именно такими — не содержимое, а указатели на него.
  #    Штатный guard их не ловил, потому что искал имена, приватный URL и секреты.
  "$GREP" -rIl 'WATCHLOG' "$dest" 2>/dev/null | while IFS= read -r f; do
    "$SED" -i '' 's|WATCHLOG|внутренний журнал|g' "$f"
  done
  [ -f "$dest/README.md" ] && "$SED" -i '' \
    -e '/docs\/reports\/audits\//d' \
    -e 's|(React + TS, ADR-001)|(React + TypeScript)|g' "$dest/README.md"
  [ -f "$dest/docs/RELEASES.md" ] && "$SED" -i '' 's|ADR-001|решение по стеку фронтенда|g' \
    "$dest/docs/RELEASES.md"

  log "SANITIZE ок (LICENSE=PolyForm, имя/приватный-репо/внутренние ссылки обезличены, версия=${ver})."
}

# ── Guard: имена из deny-list + секрет-паттерны. Любое совпадение → FAIL ──────
run_guard() {
  local dir="$1"
  local failed=0

  log "GUARD 1/3: проверка запрещённых имён..."
  local pat hit
  for pat in "${DENY_NAME_PATTERNS[@]}"; do
    hit="$("$FIND" "$dir" -type f -name "$pat" 2>/dev/null || true)"
    if [ -n "$hit" ]; then
      warn "ЗАПРЕЩЁННЫЙ ФАЙЛ просочился ($pat):"
      /bin/echo "$hit" >&2
      failed=1
    fi
  done

  log "GUARD 2/3: скан на секреты..."
  for pat in "${SECRET_PATTERNS[@]}"; do
    hit="$("$GREP" -rIE "$pat" "$dir" 2>/dev/null || true)"
    if [ -n "$hit" ]; then
      warn "СЕКРЕТ-ПАТТЕРН найден (/$pat/):"
      /bin/echo "$hit" | "$HEAD" -20 >&2
      failed=1
    fi
  done

  log "GUARD 3/3: скан на личные имена и приватный репо (правило безымянности)..."
  hit="$("$GREP" -rIE "$NAME_RE" "$dir" 2>/dev/null || true)"
  if [ -n "$hit" ]; then
    warn "ЛИЧНОЕ ИМЯ / ПРИВАТНЫЙ РЕПО в дереве — санитайзер пропустил, добавь правило:"
    /bin/echo "$hit" | "$HEAD" -20 >&2
    failed=1
  fi

  [ "$failed" -eq 0 ] || die "GUARD ПРОВАЛЕН — публикация остановлена. Разберись выше."
  log "GUARD пройден: запрещённых файлов, секретов, имён — не найдено."
}

# ── Описание релиза: public_release_notes.md → генерируемая заготовка ─────────
# Пишет заголовок в $TITLE_TMP, тело в $NOTES_TMP. Никогда не берёт текст из
# приватных CHANGELOG/WATCHLOG — только из файла, написанного ДЛЯ публики.
extract_public_notes() {
  local ver="$1"
  local notes_src="$SOURCE_REPO/tools/publish/public_release_notes.md"
  "$PY3" - "$ver" "$notes_src" "$TITLE_TMP" "$NOTES_TMP" <<'PY'
import re, sys, datetime

ver, src, ft, fn = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]

title, body = None, None
try:
    txt = open(src, encoding="utf-8").read()
    m = re.search(r"^## \[" + re.escape(ver) + r"\][^\n]*$", txt, re.M)
    if m:
        header = m.group(0)
        hdr = re.sub(r"^## \[[^\]]*\]", "", header).strip()
        parts = [p.strip() for p in re.split(r"\s+[\u2014\u2013-]\s+", hdr) if p.strip()]
        title = parts[-1] if parts else ""
        nxt = re.search(r"^## \[", txt[m.end():], re.M)
        body = (txt[m.end():m.end() + nxt.start()] if nxt else txt[m.end():]).strip("\n")
except OSError:
    pass

if not body:
    # Заготовка по умолчанию: нейтрально, безымянно, без внутренней кухни.
    title = "public mirror sync"
    today = datetime.date.today().isoformat()
    body = (
        f"## {today}\n\n"
        "Синхронизация публичного зеркала с основной линией разработки.\n\n"
        "В составе: движок рекомендаций (SAW, Debt Avalanche, SES + Monte-Carlo),\n"
        "FastAPI-бэкенд, тесты четырёх уровней (fast/full/deep/e2e), миграции Alembic,\n"
        "Docker-инфраструктура и трёхуровневый CI.\n\n"
        "История версий продукта: `docs/RELEASES.md`. "
        "Лицензия: PolyForm Noncommercial 1.0.0."
    )

open(ft, "w", encoding="utf-8").write(f"FINPILOT v{ver} \u2014 {title}".strip(" \u2014"))
open(fn, "w", encoding="utf-8").write(body + "\n")
PY
}

guard_notes() {
  # Текст релиза публичен так же, как дерево — гоняем через ту же сетку + шире.
  local hit
  hit="$("$GREP" -IE "$NOTES_RE" "$NOTES_TMP" "$TITLE_TMP" 2>/dev/null || true)"
  if [ -n "$hit" ]; then
    warn "ОПИСАНИЕ РЕЛИЗА содержит приватное (имя/кухня процесса):"
    /bin/echo "$hit" | "$HEAD" -10 >&2
    die "Перепиши секцию в tools/publish/public_release_notes.md без внутренней кухни."
  fi
  log "guard_notes пройден: описание релиза чистое."
}

# ── Тег + GitHub Release для версии (идемпотентно) ────────────────────────────
publish_release() {
  local ver="$1" tag="v$1"
  cd "$STAGING_DIR"

  # 1. Тег. Существующий не перетираем (история зеркала неприкасаема).
  if "$GIT" rev-parse "$tag" >/dev/null 2>&1; then
    log "Тег $tag уже есть — пропуск тегирования."
  else
    "$GIT" tag "$tag"
    git_retry push origin "$tag"
    log "Тег $tag создан и запушен."
  fi

  # 2. Релиз через gh. Нет gh — даём ручную команду и выходим без ошибки.
  if [ -z "$GH" ]; then
    warn "gh не установлен — релиз не оформлен. Вручную:"
    warn "  brew install gh && gh auth login"
    warn "  gh release create $tag -R $PUBLIC_REPO_SLUG --title '...' --notes-file notes.md --latest"
    return 0
  fi
  "$GH" auth status >/dev/null 2>&1 || {
    warn "gh не авторизован (gh auth login) — релиз не оформлен, тег уже на месте."
    return 0
  }

  extract_public_notes "$ver"
  guard_notes
  local title; title="$(/bin/cat "$TITLE_TMP")"

  # [!] Никаких `gh release upload` здесь быть не должно — см. шапку про ассеты.
  if "$GH" release view "$tag" -R "$PUBLIC_REPO_SLUG" >/dev/null 2>&1; then
    gh_retry release edit "$tag" -R "$PUBLIC_REPO_SLUG" \
        --title "$title" --notes-file "$NOTES_TMP" --latest >/dev/null \
      && log "Релиз $tag обновлён: $title" \
      || warn "Релиз $tag не обновился (таймаут РФ?) — запусти режим release ещё раз."
  else
    gh_retry release create "$tag" -R "$PUBLIC_REPO_SLUG" \
        --title "$title" --notes-file "$NOTES_TMP" --latest >/dev/null \
      && log "Релиз $tag создан: $title" \
      || warn "Релиз $tag не создался (таймаут РФ?) — запусти режим release ещё раз."
  fi
}

# ── Манифест: что реально уходит наружу ──────────────────────────────────────
print_manifest() {
  local dir="$1"
  /bin/echo ""
  /bin/echo "──────────── ЧТО УЙДЁТ В ПУБЛИЧНУЮ РЕПУ ────────────"
  /bin/echo "Корень:"
  "$FIND" "$dir" -maxdepth 1 -mindepth 1 -not -name '.git' \
    -exec "$BASENAME" {} \; | "$SORT" | "$SED" 's/^/  /'
  /bin/echo "docs/:"
  "$FIND" "$dir/docs" -maxdepth 1 -type f -exec "$BASENAME" {} \; \
    2>/dev/null | "$SORT" | "$SED" 's/^/  /'
  local files size
  files="$("$FIND" "$dir" -type f -not -path '*/.git/*' | "$WC" -l | "$TR" -d ' ')"
  size="$("$DU" -sh "$dir" 2>/dev/null | "$CUT" -f1)"
  /bin/echo "────────────────────────────────────────────────────"
  /bin/echo "Файлов: $files | Размер: $size"
  /bin/echo ""
}

# ── Режимы ───────────────────────────────────────────────────────────────────
mode_check() {
  log "РЕЖИМ: dry-run (ничего не пушится, git не трогается)"
  local tmp
  tmp="$("$MKTEMP" -d)"
  # shellcheck disable=SC2064
  trap "$RM -rf '$tmp'" EXIT
  build_tree "$tmp"
  run_guard "$tmp"
  print_manifest "$tmp"
  local ver; ver="$(resolve_version || echo unknown)"
  extract_public_notes "$ver"
  guard_notes
  log "Заголовок релиза будет: $(/bin/cat "$TITLE_TMP")"
  log "Dry-run ок. Реальная сборка: 'build', публикация: 'push'."
}

prepare_staging() {
  # Клонируем публичную репу один раз, дальше — обновляем рабочее дерево
  if [ ! -d "$STAGING_DIR/.git" ]; then
    log "Первый запуск: клонирую $PUBLIC_REMOTE → $STAGING_DIR"
    "$MKDIR" -p "$("$DIRNAME" "$STAGING_DIR")"
    git_retry clone "$PUBLIC_REMOTE" "$STAGING_DIR" || \
      die "Клон не удался. Создай репу finpilot на GitHub и проверь доступ (токен)."
  fi
  # Чистим рабочее дерево (кроме .git) — гарантия что удалённые файлы уйдут
  log "Очищаю рабочее дерево staging (кроме .git)..."
  "$FIND" "$STAGING_DIR" -mindepth 1 -maxdepth 1 -not -name '.git' \
    -exec "$RM" -rf {} +
}

mode_build() {
  log "РЕЖИМ: build (staging собирается, git-push НЕ выполняется)"
  prepare_staging
  build_tree "$STAGING_DIR"
  run_guard "$STAGING_DIR"
  print_manifest "$STAGING_DIR"
  log "Staging готов: $STAGING_DIR"
  log "Проверь глазами, затем: zsh ~/Downloads/finpilot_publish_public.sh push"
}

mode_push() {
  log "РЕЖИМ: push (сборка + commit + push + тег + релиз в $PUBLIC_REMOTE)"
  prepare_staging
  build_tree "$STAGING_DIR"
  run_guard "$STAGING_DIR"
  print_manifest "$STAGING_DIR"

  local ver
  ver="$(resolve_version || echo unknown)"

  cd "$STAGING_DIR"
  "$GIT" add -A
  if "$GIT" diff --cached --quiet; then
    log "Изменений нет — коммитить нечего. Проверяю тег/релиз для v${ver}..."
    publish_release "$ver"
    exit 0
  fi
  "$GIT" status --short

  /bin/echo ""
  /bin/echo -n "Публикую это в ПУБЛИЧНУЮ репу finpilot (+тег v${ver} и релиз). Продолжить? [y/N] "
  local ans
  read -r ans
  [ "$ans" = "y" ] || [ "$ans" = "Y" ] || die "Отменено пользователем."

  "$GIT" commit -m "Public mirror sync — v${ver}"
  git_retry push origin "HEAD:${PUBLIC_BRANCH}"
  log "Опубликовано: v${ver} → $PUBLIC_REMOTE ($PUBLIC_BRANCH)"

  publish_release "$ver"
}

mode_release() {
  # Дооформление: тег + релиз для версии, УЖЕ лежащей в staging (без пересборки).
  # Кейс: push прошёл, а релиз упал на таймауте / gh не был установлен.
  log "РЕЖИМ: release (только тег + релиз, без пересборки)"
  [ -d "$STAGING_DIR/.git" ] || die "Staging не найден: $STAGING_DIR — сначала 'push'."
  local ver
  ver="$(staging_version || true)"
  [ -n "$ver" ] || die "Не смог прочитать версию из $STAGING_DIR/app/config.py"
  log "Версия в staging: v${ver}"
  publish_release "$ver"
}

# ── main ─────────────────────────────────────────────────────────────────────
main() {
  local mode="${1:-check}"
  /bin/echo "FINPILOT public publisher v2"
  /bin/echo "  источник: $SOURCE_REPO"
  /bin/echo "  staging : $STAGING_DIR"
  /bin/echo "  remote  : $PUBLIC_REMOTE"
  /bin/echo "  репа gh : $PUBLIC_REPO_SLUG"
  /bin/echo ""
  case "$mode" in
    check)   mode_check   ;;
    build)   mode_build   ;;
    push)    mode_push    ;;
    release) mode_release ;;
    *) die "Неизвестный режим '$mode'. Используй: check | build | push | release" ;;
  esac
}

main "$@"
