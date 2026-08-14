/**
 * Текст ошибки API для показа пользователю — единая точка, не копипаста по формам.
 *
 * Бэкенд отдаёт ошибки в двух формах (FastAPI): `HTTPException(detail="текст")` —
 * `{detail: string}` (неверный пароль, email уже занят, недействительный токен и т.п.,
 * уже человеческим языком на русском) — и автоматическая валидация Pydantic (422) —
 * `{detail: [{msg, loc, ...}]}`. Генерируемые TS-типы (`shared/api/generated`) документируют
 * из OpenAPI-снимка только 422 на каждый эндпоинт (`HttpValidationError`) — но на рантайме
 * реально прилетают и 400/401/403/409 с тем же `{detail: string}`, просто не заведённые в
 * типовой union конкретного эндпоинта. Поэтому разбираем форму по факту, не по типу.
 */
export function extractErrorMessage(error: unknown, fallback: string): string {
  if (error && typeof error === "object" && "detail" in error) {
    const detail = (error as { detail: unknown }).detail;
    if (typeof detail === "string" && detail.length > 0) {
      return detail;
    }
    if (Array.isArray(detail) && detail.length > 0) {
      const first = detail[0] as { msg?: unknown };
      if (typeof first.msg === "string" && first.msg.length > 0) {
        return first.msg;
      }
    }
  }
  return fallback;
}
