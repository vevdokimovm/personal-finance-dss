#!/bin/zsh
# FINPILOT - установка инструментального контура вехи 8 (ADR-011).
# Запуск: zsh ~/Downloads/setup_claude_code_plugins.sh
# Идемпотентен: повторный запуск безопасен.

set -u

CLAUDE_BIN="$(/usr/bin/which claude 2>/dev/null || true)"

/bin/echo "=== FINPILOT: контур вехи 8 ==="

if [ -z "$CLAUDE_BIN" ]; then
  /bin/echo "[!] claude не найден в PATH."
  /bin/echo "    Установи Claude Code и повтори:  npm install -g @anthropic-ai/claude-code"
  exit 1
fi

/bin/echo "[i] claude: $CLAUDE_BIN"
"$CLAUDE_BIN" --version 2>/dev/null || true

# /design-sync требует Claude Code не ниже v2.1.181 - проверяем жёстко, не намёком
CC_VER="$("$CLAUDE_BIN" --version 2>/dev/null | /usr/bin/grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | /usr/bin/head -1)"
/bin/echo "[i] версия Claude Code: ${CC_VER:-неизвестна}"

ver_lt() {
  # возвращает 0, если $1 < $2
  [ "$1" = "$2" ] && return 1
  [ "$(printf '%s\n%s\n' "$1" "$2" | /usr/bin/sort -V | /usr/bin/head -1)" = "$1" ]
}

if [ -n "$CC_VER" ] && ver_lt "$CC_VER" "2.1.181"; then
  /bin/echo ""
  /bin/echo "[!] ВЕРСИЯ СТАРАЯ: $CC_VER < 2.1.181"
  /bin/echo "    Команды /design-sync и /design НЕ заработают - а на них стоит этап Э1 вехи 8."
  /bin/echo "    Обнови и запусти скрипт заново:"
  /bin/echo "        claude update          # <- ЭТО. Установка нативная."
  /bin/echo ""
  /bin/echo "    npm update -g НЕ обновляет нативную установку (даёт EACCES на corepack)."
  /bin/echo "    Если claude update падает на storage.googleapis.com - включи VPN:"
  /bin/echo "    обрыв сокета на середине это фильтрация на пути, а не поломка Claude Code."
  /bin/echo ""
  /bin/echo "    Плагины поставить всё равно можно - они от версии не зависят."
  /usr/bin/printf "    Продолжить установку плагинов на старой версии? [y/N] "
  read -r ANSWER
  case "$ANSWER" in
    [yY]*) /bin/echo "    Продолжаю." ;;
    *) /bin/echo "    Остановился. Обнови Claude Code и запусти скрипт снова."; exit 1 ;;
  esac
fi
/bin/echo ""

# --- Обязательные плагины -------------------------------------------------
REQUIRED=(
  frontend-design
  typescript-lsp
  playwright
  claude-code-setup
  claude-md-management
  security-guidance
)

# --- Полезные, ставятся по ходу -------------------------------------------
# code-review убран намеренно: дублирует pr-review-toolkit, два ревьюера
# жрут контекст и дают конфликтующие голоса (заход 7, направление 6).
OPTIONAL=(
  context7
  pr-review-toolkit
  playground
  skill-creator
  hookify
  pyright-lsp
  semgrep
  session-report
)

install_plugin() {
  local name="$1"
  /bin/echo "--> $name"
  "$CLAUDE_BIN" plugin install "$name" 2>&1 | /usr/bin/tail -n 2
}

/bin/echo "=== Обязательные ==="
for p in "${REQUIRED[@]}"; do
  install_plugin "$p"
done

# chrome-devtools живёт в ОТДЕЛЬНОМ маркетплейсе ChromeDevTools, не в официальном Anthropic.
# Установка из claude-plugins-official падает с "not found in any configured marketplace" -
# это не опечатка в имени, это другой источник. Проверено на логе владельца 2026-07-30.
/bin/echo ""
/bin/echo "=== Chrome DevTools (отдельный маркетплейс) ==="
"$CLAUDE_BIN" plugin marketplace add ChromeDevTools/chrome-devtools-mcp 2>&1 | /usr/bin/tail -n 2
"$CLAUDE_BIN" plugin install chrome-devtools-mcp@chrome-devtools-plugins 2>&1 | /usr/bin/tail -n 2

/bin/echo ""
/bin/echo "=== Полезные ==="
for p in "${OPTIONAL[@]}"; do
  install_plugin "$p"
done

/bin/echo ""
/bin/echo "=== Уборка ==="
# research-pipeline@local ссылается на локальный маркетплейс, которого нет.
# Не смертелен, но claude doctor будет краснеть, а ошибки в контуре копятся.
"$CLAUDE_BIN" plugin uninstall research-pipeline 2>/dev/null | /usr/bin/tail -n 1
"$CLAUDE_BIN" plugin marketplace remove local 2>/dev/null | /usr/bin/tail -n 1

/bin/echo ""
/bin/echo "=== Готово ==="
/bin/echo "Дальше в каталоге репозитория:"
/bin/echo "  claude"
/bin/echo "  /plugin          - проверить список"
/bin/echo "  claude doctor    - проверить, не раздут ли контекст"
/bin/echo ""
/bin/echo "Плагины сообщества без верификации Anthropic НЕ ставим - см. ADR-011 п.2.3."
/bin/echo "Если какой-то плагин не поставился - имя могло измениться;"
/bin/echo "поставь вручную через /plugin внутри Claude Code."
