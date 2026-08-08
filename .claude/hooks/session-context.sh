#!/bin/bash
# SessionStart: plain stdout становится контекстом, видимым Claude.
set -uo pipefail
root="${CLAUDE_PROJECT_DIR:-.}"
cd "$root" || exit 0
echo "Версия проекта: $(cat VERSION 2>/dev/null || echo неизвестна)"
echo "Ветка: $(git branch --show-current 2>/dev/null || echo вне-git)"
echo "Незакоммиченных файлов: $(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')"
echo "Канон матмодели: v3.0.0 (docs/math_model_v3_0_0.md). v2.x запрещена."
echo "Перед сдачей батча обязателен python -m tools.preflight."
exit 0
