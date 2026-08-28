#!/bin/bash
# PostToolUse: хардкод цветов и размеров мимо токенов дизайн-системы.
# Блокирует ТОЛЬКО exit 2. exit 1 не блокирует — типовая ловушка (см. block-secrets.sh).
# docs/frontend_milestone8_plan.md, Шаг 4: «ни одного хардкоденного цвета и ни одного px
# вне токенов». До вехи 8 хук существовал, но только предупреждал (exit 0) — теперь блокирует.
set -uo pipefail
H="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fp=$(cat | python3 "$H/_parse.py" tool_input.file_path) || exit 2
[ -z "$fp" ] && exit 0
case "$fp" in *.css|*.ts|*.tsx) ;; *) exit 0 ;; esac
case "$fp" in *tokens.css|*/generated/*) exit 0 ;; esac
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0
# @media-условия и чистые строки-комментарии — исключение: CSS не пускает custom property
# в условие @media (ограничение языка, не обходной путь), а строка-комментарий не рендерится.
hits=$(grep -nE '#[0-9a-fA-F]{3,8}\b|[^-a-zA-Z][0-9]+px' -- "$fp" 2>/dev/null \
  | grep -vE '^[0-9]+:\s*(/\*|\*|//)' \
  | grep -vE '^[0-9]+:[^:]*@media' \
  | head -20)
if [ -n "$hits" ]; then
  echo "Заблокировано: хардкод-цвет или px мимо токенов в $fp (TOK-01/TOK-04)." >&2
  echo "$hits" >&2
  echo "Используй переменную из src/app/styles/tokens.css. Единица не в px (ch/rem/%) — тоже" >&2
  echo "магическое число, если не связана с реальной пропорцией (напр. читаемая ширина строки)." >&2
  exit 2
fi
exit 0
