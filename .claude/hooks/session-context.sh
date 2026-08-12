#!/bin/bash
# SessionStart: plain stdout становится контекстом, видимым Claude.
set -uo pipefail
root="${CLAUDE_PROJECT_DIR:-.}"
cd "$root" || exit 0
echo "Версия проекта: $(cat VERSION 2>/dev/null || echo неизвестна)"
echo "Ветка: $(git branch --show-current 2>/dev/null || echo вне-git)"
echo "Незакоммиченных файлов: $(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')"
canon_file=$(grep -L "SUPERSEDED" docs/math_model_v*.md 2>/dev/null | sort -V | tail -1)
canon_version=$(basename "${canon_file:-неизвестен}" .md | sed -E 's/math_model_v([0-9]+)_([0-9]+)_([0-9]+)/\1.\2.\3/')
echo "Канон матмодели: v${canon_version} (${canon_file:-см. docs/model/model_history.md}). v2.x запрещена."
echo "Перед сдачей батча обязателен python -m tools.preflight."
exit 0
