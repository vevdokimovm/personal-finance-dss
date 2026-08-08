#!/bin/bash
# PreToolUse: Bash — заслон на необратимые команды.
# Урок Replit (июль 2025): текстовый запрет агент обходит рассуждением, хук — нет.
set -uo pipefail
H="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
input=$(cat)
cmd=$(printf '%s' "$input" | python3 "$H/_parse.py" tool_input.command) || exit 2
[ -z "$cmd" ] && exit 0

case "$cmd" in
  *"rm -rf"*|*"rm -fr"*|*"git push --force"*|*"git push -f"*|\
  *"git reset --hard"*|*"DROP TABLE"*|*"DROP DATABASE"*|*"TRUNCATE"*|\
  *"alembic downgrade"*|*"DELETE FROM"*|*"black ."*)
    echo "Заблокировано: необратимая или запрещённая правилами команда." >&2
    echo "Команда: $cmd" >&2
    echo "Предложи обратимую альтернативу и спроси владельца." >&2
    exit 2
    ;;
esac
exit 0
