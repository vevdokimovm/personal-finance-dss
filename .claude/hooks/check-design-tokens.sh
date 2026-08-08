#!/bin/bash
# PostToolUse: хардкод цветов и размеров мимо токенов дизайн-системы.
set -uo pipefail
H="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fp=$(cat | python3 "$H/_parse.py" tool_input.file_path) || exit 0
[ -z "$fp" ] && exit 0
case "$fp" in *.css|*.ts|*.tsx) ;; *) exit 0 ;; esac
case "$fp" in *tokens*) exit 0 ;; esac
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0
hits=$(grep -nE '#[0-9a-fA-F]{3,8}\b|[^-a-z][0-9]+px' -- "$fp" 2>/dev/null | head -20)
[ -n "$hits" ] && { echo "Хардкод мимо токенов в $fp:" >&2; echo "$hits" >&2; }
exit 0
