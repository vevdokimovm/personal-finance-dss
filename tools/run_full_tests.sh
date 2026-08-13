#!/usr/bin/env bash
# Полный прогон тестов с ЖИВЫМ прогрессом (PIT-016, ROADMAP §«Сквозные правила» п.6).
#
# Проблема, которую решает: pytest в фоне через `| tail -N` (без -f) не стримит —
# tail без -f ждёт EOF и печатает хвост только в конце, весь долгий прогон выглядит
# как зависший процесс. Здесь pytest пишет НЕБУФЕРИЗОВАННО (`python -u`) прямо в
# файл журнала — его можно смотреть `tail -f` или инструментом Monitor в реальном
# времени, без обёртки в tail без -f.
#
# Итоговый счёт — всегда из --junitxml (правило §3 ROADMAP: не парсить лог на глаз).
#
# Использование:
#   tools/run_full_tests.sh                  # свой лог/xml с меткой времени
#   tools/run_full_tests.sh mybatch           # логи с префиксом mybatch
#   tail -f /tmp/finpilot_pytest_<...>.log    # живой прогресс в другом терминале
#   # или из Claude Code: Monitor({command: "tail -f <лог> | grep --line-buffered ..."})
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || exit 1

LABEL="${1:-$(date +%Y%m%d_%H%M%S)}"
LOG="/tmp/finpilot_pytest_${LABEL}.log"
XML="/tmp/finpilot_pytest_${LABEL}.xml"

PYBIN="$ROOT/.venv/bin/python3"
[ -x "$PYBIN" ] || PYBIN="python3"

echo "Лог (живой прогресс — tail -f):  $LOG"
echo "JUnit (источник итога — §3):     $XML"
echo

"$PYBIN" -u -m pytest -q --junitxml="$XML" > "$LOG" 2>&1
code=$?

echo
if [ "$code" -eq 0 ]; then
  echo "OK — детали: $XML"
else
  echo "ПРОВАЛ (exit $code) — детали: $XML, лог: $LOG"
fi
"$PYBIN" - "$XML" <<'PYEOF'
import re
import sys

# Regex по атрибутам первого <testsuite ...>, не XML-парсер: файл наш
# собственный (junitxml, сгенерирован pytest только что), но парсер —
# лишняя поверхность (XXE-класс уязвимостей) там, где хватает четырёх чисел.
path = sys.argv[1]
try:
    with open(path, encoding="utf-8") as f:
        head = f.read(4096)
except FileNotFoundError:
    sys.exit(0)
match = re.search(r"<testsuite\b[^>]*>", head)
if not match:
    sys.exit(0)
tag = match.group()
fields = ("tests", "errors", "failures", "skipped")
values = {
    field: (re.search(rf'{field}="([^"]*)"', tag) or [None, "?"])[1]
    for field in fields
}
print(" ".join(f"{k}={v}" for k, v in values.items()))
PYEOF

exit "$code"
