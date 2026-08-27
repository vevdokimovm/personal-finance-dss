#!/usr/bin/env bash
#
# Обновление курсов валют с ЦБ РФ (P0.6, P0.3).
# Дёргает /api/fx/refresh с админ-ключом. При недоступности cbr.ru курсы в БД
# не затираются (источник fallback) — это поведение приложения.
#
# Требует в окружении (EnvironmentFile=.env у systemd, либо export):
#   ADMIN_API_KEY        — админ-ключ
#   FINPILOT_BASE_URL    — базовый URL (по умолчанию http://127.0.0.1:8000)
#
set -euo pipefail

: "${ADMIN_API_KEY:?ADMIN_API_KEY не задан (положи в .env)}"
BASE_URL="${FINPILOT_BASE_URL:-http://127.0.0.1:8000}"

echo "[$(date '+%F %T')] POST ${BASE_URL}/api/fx/refresh"
curl -fsS -X POST "${BASE_URL}/api/fx/refresh" \
    -H "X-Admin-Key: ${ADMIN_API_KEY}"
echo
echo "[$(date '+%F %T')] готово"
