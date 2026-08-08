#!/bin/bash
# Stop: «готово» только если тесты зелёные.
# Проверка stop_hook_active ОБЯЗАТЕЛЬНА — без неё бесконечный цикл (кап 8 блоков).
set -uo pipefail
H="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
input=$(cat)
active=$(printf '%s' "$input" | python3 "$H/_parse.py" stop_hook_active) || exit 0
[ "$active" = "True" ] || [ "$active" = "true" ] && exit 0

root="${CLAUDE_PROJECT_DIR:-.}"
cd "$root" || exit 0
[ -f logs/agent-audit.jsonl ] || exit 0
grep -q '"tool": *"\(Edit\|Write\|MultiEdit\)"' logs/agent-audit.jsonl 2>/dev/null || exit 0

PYBIN="$root/.venv/bin/python3"
[ -x "$PYBIN" ] || PYBIN="python3"
if ! "$PYBIN" -m pytest -q -x > /tmp/finpilot-gate.log 2>&1; then
  python3 -c '
import json
tail = open("/tmp/finpilot-gate.log", errors="replace").read().splitlines()[-15:]
print(json.dumps({"decision": "block", "reason":
    "Тесты падают — задача не завершена. Почини и прогони снова.\n"
    + "\n".join(tail) + "\nПолный лог: /tmp/finpilot-gate.log"}, ensure_ascii=False))
'
fi
exit 0
