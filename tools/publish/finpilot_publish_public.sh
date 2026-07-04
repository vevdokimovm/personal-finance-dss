#!/usr/bin/env bash
# =============================================================================
# finpilot_publish_public.sh
#
# Сборка ПУБЛИЧНОГО зеркала (репо vevdokimovm/finpilot) из ПРИВАТНОГО
# монорепо (vevdokimovm/personal-finance-dss).
#
# Философия: whitelist / deny-by-default. Наружу уходит ТОЛЬКО то, что явно
# перечислено ниже. Всё остальное (WATCHLOG, мёрж-манифесты, реестры
# инцидентов, юр-вопросы, бизнес-анализ, опросы, секреты) не публикуется
# по определению — оно просто не входит в allow-list.
#
# Второй слой защиты: guard-сканер прогоняет собранное дерево на паттерны
# ключей / приватных данных и падает, если что-то нашёл.
#
# Запуск (из Downloads, как принято в проекте):
#   zsh ~/Downloads/finpilot_publish_public.sh            # dry-run (по умолчанию)
#   zsh ~/Downloads/finpilot_publish_public.sh build      # собрать staging, без push
#   zsh ~/Downloads/finpilot_publish_public.sh push       # собрать + commit + push
#
# Переопределение путей без правки скрипта:
#   FINPILOT_SRC=/path/to/private FINPILOT_STAGE=/path/to/stage \
#     zsh ~/Downloads/finpilot_publish_public.sh build
# =============================================================================

set -euo pipefail

# ── КОНФИГ (проверь пути под свою машину) ────────────────────────────────────
# Приватное монорепо (источник):
SOURCE_REPO="${FINPILOT_SRC:-$HOME/PycharmProjects/personal-finance-dss}"
# Рабочая папка публичного зеркала (git-клон finpilot):
STAGING_DIR="${FINPILOT_STAGE:-$HOME/dev/finpilot-public}"
# Remote публичной репы:
PUBLIC_REMOTE="${FINPILOT_REMOTE:-git@github.com:vevdokimovm/finpilot.git}"
PUBLIC_BRANCH="${FINPILOT_BRANCH:-main}"

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
# git бывает и в /usr/bin, и в /usr/local/bin (brew) — резолвим:
GIT="$(command -v git || echo /usr/bin/git)"

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
  .env.prod.example
)

# ── ALLOW-LIST: docs (только нейтральная тех-документация) ───────────────────
ALLOW_DOCS=(
  README.md
  CONTRIBUTING.md
  GLOSSARY.md
  QA.md
  DEPLOY.md
  RELEASES.md
  engineering_practices.md
  adr_001_frontend_stack.md
  adr_002_datetime_storage.md
  adr_template.md
  bug_report_template.md
  incident_postmortem_guide.md
  investigation_report_guide.md
  requirements_guide.md
  ui_requirements_guide.md
  report_types.md
)

# ── OPTIONAL docs: раскрывают IP / стратегию. Раскомментируй осознанно ────────
# Это ядро продукта и планы. По умолчанию НЕ публикуются (конкуренты).
OPTIONAL_DOCS=(
  # math_model_v3_0_0.md          # математическая модель — ядро алгоритма (IP)
  # algorithm_stack.md            # стек алгоритмов (IP)
  # reference_profiles.md         # эталонные риск-профили (часть модели)
  # diagrams.md                   # архитектурные диаграммы
  # ui_ux_design_standard.md      # 88KB внутренний UI-стандарт
  # ROADMAP.md                    # дорожная карта / стратегия
  # testing_infrastructure.md     # внутренняя тестовая кухня
  # test_run_optimization.md
  # documentation_methodology.md
)

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
)

# ── Хелперы ──────────────────────────────────────────────────────────────────
log()  { /bin/echo ">> $*"; }
warn() { /bin/echo "!! $*" >&2; }
die()  { /bin/echo "XX $*" >&2; exit 1; }

resolve_version() {
  # Достаём APP_VERSION из app/config.py для сообщения коммита
  "$GREP" -Eo 'default="[0-9]+\.[0-9]+\.[0-9]+"' "$SOURCE_REPO/app/config.py" \
    | "$GREP" -Eo '[0-9]+\.[0-9]+\.[0-9]+' | /usr/bin/head -1
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
}

# ── Guard: имена из deny-list + секрет-паттерны. Любое совпадение → FAIL ──────
run_guard() {
  local dir="$1"
  local failed=0

  log "GUARD 1/2: проверка запрещённых имён..."
  local pat hit
  for pat in "${DENY_NAME_PATTERNS[@]}"; do
    hit="$("$FIND" "$dir" -type f -name "$pat" 2>/dev/null || true)"
    if [ -n "$hit" ]; then
      warn "ЗАПРЕЩЁННЫЙ ФАЙЛ просочился ($pat):"
      /bin/echo "$hit" >&2
      failed=1
    fi
  done

  log "GUARD 2/2: скан на секреты..."
  for pat in "${SECRET_PATTERNS[@]}"; do
    hit="$("$GREP" -rIE "$pat" "$dir" 2>/dev/null || true)"
    if [ -n "$hit" ]; then
      warn "СЕКРЕТ-ПАТТЕРН найден (/$pat/):"
      /bin/echo "$hit" | /usr/bin/head -20 >&2
      failed=1
    fi
  done

  [ "$failed" -eq 0 ] || die "GUARD ПРОВАЛЕН — публикация остановлена. Разберись выше."
  log "GUARD пройден: запрещённых файлов и секретов не найдено."
}

# ── Манифест: что реально уходит наружу ──────────────────────────────────────
print_manifest() {
  local dir="$1"
  /bin/echo ""
  /bin/echo "──────────── ЧТО УЙДЁТ В ПУБЛИЧНУЮ РЕПУ ────────────"
  /bin/echo "Корень:"
  "$FIND" "$dir" -maxdepth 1 -mindepth 1 -not -name '.git' \
    -exec /usr/bin/basename {} \; | "$SORT" | /usr/bin/sed 's/^/  /'
  /bin/echo "docs/:"
  "$FIND" "$dir/docs" -maxdepth 1 -type f -exec /usr/bin/basename {} \; \
    2>/dev/null | "$SORT" | /usr/bin/sed 's/^/  /'
  local files size
  files="$("$FIND" "$dir" -type f -not -path '*/.git/*' | "$WC" -l | /usr/bin/tr -d ' ')"
  size="$("$DU" -sh "$dir" 2>/dev/null | /usr/bin/cut -f1)"
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
  log "Dry-run ок. Реальная сборка: 'build', публикация: 'push'."
}

prepare_staging() {
  # Клонируем публичную репу один раз, дальше — обновляем рабочее дерево
  if [ ! -d "$STAGING_DIR/.git" ]; then
    log "Первый запуск: клонирую $PUBLIC_REMOTE → $STAGING_DIR"
    "$MKDIR" -p "$(/usr/bin/dirname "$STAGING_DIR")"
    git_retry clone "$PUBLIC_REMOTE" "$STAGING_DIR" || \
      die "Клон не удался. Создай репу finpilot на GitHub и проверь SSH-доступ."
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
  log "Проверь глазами, затем: cd '$STAGING_DIR' && git add -A && git commit && git push"
}

mode_push() {
  log "РЕЖИМ: push (сборка + commit + push в $PUBLIC_REMOTE)"
  prepare_staging
  build_tree "$STAGING_DIR"
  run_guard "$STAGING_DIR"
  print_manifest "$STAGING_DIR"

  cd "$STAGING_DIR"
  "$GIT" add -A
  if "$GIT" diff --cached --quiet; then
    log "Изменений нет — публиковать нечего."
    exit 0
  fi
  "$GIT" status --short

  /bin/echo ""
  /bin/echo -n "Публикую это в ПУБЛИЧНУЮ репу finpilot. Продолжить? [y/N] "
  local ans
  read -r ans
  [ "$ans" = "y" ] || [ "$ans" = "Y" ] || die "Отменено пользователем."

  local ver
  ver="$(resolve_version || echo unknown)"
  "$GIT" commit -m "Public mirror sync — v${ver}"
  git_retry push origin "HEAD:${PUBLIC_BRANCH}"
  log "Опубликовано: v${ver} → $PUBLIC_REMOTE ($PUBLIC_BRANCH)"
}

# ── main ─────────────────────────────────────────────────────────────────────
main() {
  local mode="${1:-check}"
  /bin/echo "FINPILOT public publisher"
  /bin/echo "  источник: $SOURCE_REPO"
  /bin/echo "  staging : $STAGING_DIR"
  /bin/echo "  remote  : $PUBLIC_REMOTE"
  /bin/echo ""
  case "$mode" in
    check) mode_check ;;
    build) mode_build ;;
    push)  mode_push  ;;
    *) die "Неизвестный режим '$mode'. Используй: check | build | push" ;;
  esac
}

main "$@"
