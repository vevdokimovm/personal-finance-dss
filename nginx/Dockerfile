# ════════════════════════════════════════════════════════════════════════════
# FINPILOT — nginx: собранный SPA (React) + reverse proxy на FastAPI.
# Контекст сборки — КОРЕНЬ репозитория (docker-compose.prod.yml: context: .,
# dockerfile: nginx/Dockerfile), т.к. builder-стадии нужен frontend/.
# ════════════════════════════════════════════════════════════════════════════

# ── Stage 1: builder — прод-сборка SPA (Vite + TypeScript, vite build && tsc -b) ──
FROM node:22-alpine AS builder

WORKDIR /app

# Сначала манифесты — слой с зависимостями кэшируется отдельно от исходников.
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# ── Stage 2: runtime — nginx отдаёт dist/ статикой, шаблон конфига — из репозитория ──
FROM nginx:1.27-alpine

# Стоковый default.conf слушает 80 с server_name localhost — по алфавиту грузится
# раньше finpilot.conf и перехватывает запросы с Host: localhost (включая healthcheck
# контейнера, у которого нет причин знать реальный ${DOMAIN}), там нет /nginx-health →
# контейнер вечно "unhealthy" при абсолютно рабочем внешнем трафике. Убираем, чтобы
# наш конфиг был единственным на этот порт (де-факто default_server).
RUN rm -f /etc/nginx/conf.d/default.conf

COPY --from=builder /app/dist /usr/share/nginx/html
