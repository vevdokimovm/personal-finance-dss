import { client } from "./generated/client.gen";

/**
 * Настраивает клиент, который реально использует сгенерированный SDK (src/shared/api/generated/,
 * hey-api) — client.gen.ts создаёт клиент с пустым конфигом, index.ts его не реэкспортирует,
 * поэтому конфигурируем именно этот инстанс напрямую. Вызывать один раз при старте (main.tsx),
 * до первого запроса.
 *
 * baseUrl относительный: dev — прокси Vite на 127.0.0.1:8000 (vite.config.ts), прод — nginx
 * маршрутизирует /api на FastAPI напрямую (docs/frontend_migration_plan.md §1.5).
 *
 * Авторизация — HttpOnly cookie (§1.3), credentials: "include" обязателен, иначе куки не летят
 * на кросс-origin dev-прокси. CSRF double-submit — Фаза 4 (§5), сейчас не нужен: SameSite=lax
 * + Origin-проверка уже стоят на бэке.
 */
export function configureApiClient(): void {
  client.setConfig({
    // Пусто, не "/api": пути в OpenAPI-снимке уже абсолютные и включают /api
    // (роутеры примонтированы с этим префиксом на бэкенде) — baseUrl="/api" даёт
    // /api/api/... и 403 на несуществующий путь (найдено вручную в браузере, не молча).
    baseUrl: "",
    credentials: "include",
  });
}

export { client as apiClient };
