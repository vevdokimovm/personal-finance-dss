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

  /* 🔴 Код ответа доезжает до обработчика ошибки (v9.1.0, нашёл `/code-review`).
     `client.gen.ts` при неуспехе делает `throw jsonError ?? textError` — бросается
     ТОЛЬКО тело, а `status` теряется. Значит любая проверка `error.status === 401`
     во всех хуках на этом клиенте всегда давала `false`:

     · `isSessionExpired` срабатывал лишь на `NotAuthenticatedError` из `useProfile`,
       и человек с истёкшей сессией на остальных экранах получал «Проверьте соединение»
       с кнопкой, возвращающей 401 по кругу;
     · `useSpendingAdvice` и `useNotifications` ретраили 401/403, вопреки собственным
       докстрокам «повторять осознанный отказ бессмысленно».

     Интерцептор — единственное место, где ещё виден сам `Response`. Правка здесь
     чинит все хуки разом; правка в каждом хуке разошлась бы при первом же новом. */
  client.interceptors.error.use((error, response) => {
    /* 🔴 Ответа может не быть вовсе (нашёл `/code-review`): `client.gen.ts` зовёт
       error-интерцепторы из `catch`, который покрывает и падение самого `fetch` —
       офлайн, отказ DNS, прерванный запрос. Там `response` ещё `undefined`, и обращение
       к `.status` подменило бы настоящую ошибку `TypeError`-ом у КАЖДОГО хука.
       Возвращаем ошибку как есть: `status` у неё и не существует, а разбор обрыва
       сети живёт в `useProfile`. */
    if (!response) {
      return error;
    }
    // Строке поле не присвоить — заворачиваем, иначе `status` пропадёт молча именно
    // там, где ответ не JSON: 502 от прокси, HTML от балансировщика.
    if (typeof error === "string") {
      return { detail: error, status: response.status };
    }
    if (error && typeof error === "object") {
      return { ...(error as object), status: response.status };
    }
    return { detail: String(error), status: response.status };
  });
}

export { client as apiClient };
