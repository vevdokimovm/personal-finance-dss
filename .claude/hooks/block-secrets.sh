#!/bin/bash
# PreToolUse: Edit|Write|Read — заслон на секреты и персональные данные (152-ФЗ).
# Блокирует ТОЛЬКО exit 2. exit 1 не блокирует — типовая ловушка.
set -uo pipefail
H="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
input=$(cat)
fp=$(printf '%s' "$input" | python3 "$H/_parse.py" tool_input.file_path) || exit 2
[ -z "$fp" ] && fp=$(printf '%s' "$input" | python3 "$H/_parse.py" tool_input.notebook_path)
[ -z "$fp" ] && exit 0

case "$fp" in
  *.env|*.env.*|*/.env|*/.env.*|*secret*|*Secret*|*SECRET*|\
  *credential*|*Credential*|*.pem|*.key|*.p12|*.pfx|*id_rsa*|\
  *.sqlite|*.sqlite3|*.db)
    echo "Заблокировано: доступ к секретам и боевым данным запрещён (152-ФЗ). Файл: $fp" >&2
    echo "Если нужен пример конфигурации — используй .env.example." >&2
    exit 2
    ;;
esac
exit 0
