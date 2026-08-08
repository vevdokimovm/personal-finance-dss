#!/bin/bash
# Stop: «готово» только если быстрый срез тестов зелёный.
# Проверка stop_hook_active ОБЯЗАТЕЛЬНА — без неё бесконечный цикл (кап 8 блоков).
#
# Полная суита (1512 тестов, 25-30 мин) сюда НЕ идёт — она превышала таймаут хука
# (10 мин) и хук молча пропускал всё (fail-open, гейт не работал). Здесь — быстрый
# срез до ~90 c: тесты, относящиеся к файлам, изменённым в этой сессии
# (logs/agent-audit.jsonl + _affected_tests.py), плюс маркер `property`
# (инварианты матмодели, hypothesis). Таймаут по фазам — в _run_test_slice.py
# (subprocess.run(timeout=...), не shell `timeout(1)` — его нет на голом macOS).
# Полная суита остаётся в церемонии батча (python -m tools.preflight).
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

session_id=$(printf '%s' "$input" | python3 "$H/_parse.py" session_id)
# bash 3.2 на macOS не знает mapfile/readarray (bash 4+) — читаем циклом.
affected=()
while IFS= read -r line; do
  [ -n "$line" ] && affected+=("$line")
done < <("$PYBIN" "$H/_affected_tests.py" "$session_id" 2>/dev/null)

# set -u + "${affected[@]}" на пустом массиве падает "unbound variable" в bash
# 3.2 (баг чинён только в 4.4+, а macOS до сих пор шлёт 3.2) — ветвим явно.
if [ "${#affected[@]}" -gt 0 ]; then
  "$PYBIN" "$H/_run_test_slice.py" "$PYBIN" "${affected[@]}"
else
  "$PYBIN" "$H/_run_test_slice.py" "$PYBIN"
fi
exit 0
