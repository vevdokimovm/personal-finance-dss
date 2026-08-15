/**
 * Текст ошибки API для показа пользователю — единая точка, не копипаста по формам.
 *
 * Бэкенд отдаёт ошибки в трёх формах (FastAPI): `HTTPException(detail="текст")` —
 * `{detail: string}` (неверный пароль, email уже занят, недействительный токен и т.п.,
 * уже человеческим языком на русском) — автоматическая валидация Pydantic (422) —
 * `{detail: [{msg, loc, ...}]}` — и гейт согласия на финданные (403, `app/api/_consent_guard.py`)
 * — `{detail: {code, consent_type, document: {title, version, url}, message}}`, машиночитаемый
 * объект. Генерируемые TS-типы (`shared/api/generated`) документируют из OpenAPI-снимка только
 * 422 на каждый эндпоинт (`HttpValidationError`) — но на рантайме реально прилетают и 400/401/
 * 403/409 в разных формах, не заведённых в типовой union конкретного эндпоинта. Поэтому
 * разбираем форму по факту, не по типу.
 *
 * Объектный detail — временный минимум ДО экрана согласия по 403 (ROADMAP §8.2, L3): просто
 * текст + ссылка на документ плоской строкой (toast — plain text, не рендерит ссылки), не
 * кликабельная кнопка «дать согласие». Полный экран заменит этот путь позже, не сейчас.
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
    if (detail && typeof detail === "object") {
      const { message, document } = detail as {
        message?: unknown;
        document?: { url?: unknown };
      };
      if (typeof message === "string" && message.length > 0) {
        const url = document && typeof document.url === "string" ? document.url : null;
        return url ? `${message} (${url})` : message;
      }
    }
  }
  return fallback;
}
