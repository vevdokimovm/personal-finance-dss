#!/bin/bash
# Stop: VERSION сдан (рабочее дерево грязное), а чекпоинт-архива в ~/Developer нет — блокирует.
#
# 🔴 Каталог сменён 03.09.2026 (v8.38.0). Деплойер читает архивы из
# `DIR="${1:-${BASE_ARTIFACTS:-$HOME/Developer}}"` (base-repo/templates/deploy.sh:103) —
# архив в ~/Downloads он не видит вовсе, и батч выглядит сданным, не будучи им.
# Сторож проверял старый каталог ещё после того, как правило поменяли в CLAUDE.md:
# отмена, дошедшая не всюду, — это не отмена, а расхождение.
# CLAUDE.md правило 10 / docs/session_continuity.md: архив — единственное подтверждение
# доставки между аккаунтами/чатами владельца; без него работа технически не передана.
# Ловит ТОЛЬКО механический случай (версия/изменения есть, архива для неё нет) — «естественные
# точки паузы» внутри батча без смены VERSION это правило распознать не может, там решение
# по-прежнему на агенте.
# stop_hook_active guard обязателен — та же причина, что в tests-gate.sh: без него блок
# зацикливается (Stop-хук сам порождает следующий Stop).
set -uo pipefail
H="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
input=$(cat)
active=$(printf '%s' "$input" | python3 "$H/_parse.py" stop_hook_active) || exit 0
{ [ "$active" = "True" ] || [ "$active" = "true" ]; } && exit 0

root="${CLAUDE_PROJECT_DIR:-.}"
cd "$root" || exit 0
command -v git >/dev/null 2>&1 || exit 0
command -v python3 >/dev/null 2>&1 || exit 0
[ -f VERSION ] || exit 0
version="$(tr -d ' \t\r\n' < VERSION)"
[ -n "$version" ] || exit 0

# Рабочее дерево чисто относительно последнего коммита (нет изменений, нет новых файлов
# без .gitignore-мусора) — нечего доставлять, не душним.
if git diff --quiet 2>/dev/null && git diff --cached --quiet 2>/dev/null \
  && [ -z "$(git ls-files -o --exclude-standard 2>/dev/null)" ]; then
  exit 0
fi

artifacts="${BASE_ARTIFACTS:-${HOME}/Developer}"
zip_name="personal-finance-dss-v${version}.zip"
[ -f "$artifacts/$zip_name" ] && exit 0

reason=$(cat <<EOF
Рабочее дерево не совпадает с последним коммитом (VERSION=${version}), а чекпоинт-архива
${artifacts}/${zip_name} нет. Правило 10 (CLAUDE.md) / docs/session_continuity.md: без архива
работа не считается переданной владельцу — сделай его перед тем как закончить ход:
  1. git ls-files -c -o --exclude-standard > /tmp/checkpoint_filelist.txt
  2. cd "${root}" && zip -q -X "${artifacts}/${zip_name}" -@ < /tmp/checkpoint_filelist.txt
     (без обёрточной директории — файлы прямо в корне архива)
  3. cp docs/WATCHLOG.md "${artifacts}/WATCHLOG-personal-finance-dss-v${version}.md"
  4. shasum -a 256 обоих файлов — sha256 в отчёт владельцу.
Если версия ещё не окончательная (черновик, не сдача батча) — обнови VERSION обратно на
предыдущую сданную, тогда архив для неё уже существует и этот блок не сработает.
EOF
)
printf '%s' "$reason" | python3 -c '
import json, sys
print(json.dumps({"decision": "block", "reason": sys.stdin.read()}, ensure_ascii=False))
'
exit 0
