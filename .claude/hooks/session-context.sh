#!/bin/bash
# SessionStart: plain stdout становится контекстом, видимым Claude.
set -uo pipefail
root="${CLAUDE_PROJECT_DIR:-.}"
cd "$root" || exit 0
echo "Версия проекта: $(cat VERSION 2>/dev/null || echo неизвестна)"
echo "Ветка: $(git branch --show-current 2>/dev/null || echo вне-git)"
echo "Незакоммиченных файлов: $(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')"
canon_version=$(grep -m1 -oE "версия [0-9]+\.[0-9]+\.[0-9]+" docs/math_model.md 2>/dev/null | grep -oE "[0-9.]+")
echo "Канон матмодели: v${canon_version:-см. файл} (docs/math_model.md — стабильное имя, не переименовывается). v2.x запрещена."
echo "Перед сдачей батча обязателен python -m tools.preflight."
exit 0
