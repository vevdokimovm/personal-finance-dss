#!/usr/bin/env bash
#
# Запуск рассылки уведомлений FINPILOT (P0.6).
# Дёргает идемпотентный эндпоинт /api/notifications/run с админ-ключом.
# Вызывается systemd-timer'ом или cron на хосте.
#
# Требует в окружении (через EnvironmentFile=.env у systemd, либо export):
#   ADMIN_API_KEY        — админ-ключ (тот же, что у приложения)
#   FINPILOT_BASE_URL    — базовый URL (по умолчанию http://127.0.0.1:8000)
#
set -euo pipefail

: "${ADMIN_API_KEY:?ADMIN_API_KEY не задан (положи в .env)}"
BASE_URL="${FINPILOT_BASE_URL:-http://127.0.0.1:8000}"

echo "[$(date '+%F %T')] POST ${BASE_URL}/api/notifications/run"
curl -fsS -X POST "${BASE_URL}/api/notifications/run" \
    -H "X-Admin-Key: ${ADMIN_API_KEY}"
echo
echo "[$(date '+%F %T')] готово"
