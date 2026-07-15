#!/usr/bin/env bash
set -e

# При PostgreSQL дожидаемся готовности БД перед миграциями.
if [[ "${DATABASE_URL}" == postgresql* ]]; then
  echo "Ожидание PostgreSQL..."
  python - <<'PY'
import os, sys, time
import sqlalchemy as sa

url = os.environ["DATABASE_URL"]
for _ in range(30):
    try:
        sa.create_engine(url).connect().close()
        print("PostgreSQL готова.")
        sys.exit(0)
    except Exception:
        time.sleep(1)
sys.exit("PostgreSQL недоступна после ожидания.")
PY
fi

# Применяем миграции схемы (идемпотентно).
alembic upgrade head

exec "$@"
