# ── Stage 1: builder — установка зависимостей в изолированный venv ──
FROM python:3.12-slim AS builder

WORKDIR /app
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# build-essential не нужен: весь стек ставится из готовых manylinux-wheel
# (psycopg[binary], cryptography, bcrypt, pillow, pydantic-core и т.д.).
# --only-binary=:all: запрещает компиляцию из sdist — сборка детерминирована
# и не зависит от apt-зеркал (устраняет «Hash Sum mismatch» при apt-get).
COPY requirements.txt .
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir --only-binary=:all: -r requirements.txt

# ── Stage 2: runtime — только venv и код, без сборочных инструментов ──
FROM python:3.12-slim AS runtime

WORKDIR /app
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ENVIRONMENT=production

RUN useradd --create-home --uid 1000 appuser

COPY --from=builder /opt/venv /opt/venv
COPY . .

RUN chmod +x docker-entrypoint.sh && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["gunicorn", "app.main:app", "-c", "gunicorn_conf.py"]
