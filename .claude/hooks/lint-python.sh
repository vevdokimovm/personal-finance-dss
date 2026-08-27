#!/bin/bash
# PostToolUse: информативный линт Python. Не блокирует, stderr виден модели.
set -uo pipefail
H="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fp=$(cat | python3 "$H/_parse.py" tool_input.file_path) || exit 0
[ -z "$fp" ] && exit 0
case "$fp" in *.py) ;; *) exit 0 ;; esac
root="${CLAUDE_PROJECT_DIR:-.}"
cd "$root" || exit 0
flake8 --config="$root/.flake8" -- "$fp" 2>&1 | head -20 >&2
exit 0
