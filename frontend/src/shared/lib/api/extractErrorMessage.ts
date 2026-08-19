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
 * Объектный detail (гейт согласия) здесь по-прежнему сводится к плоскому тексту — для мест
 * без кнопки (инлайн-баннер формы). Там, где нужна кликабельная кнопка «Дать согласие» —
 * `getConsentRequiredDetail()` ниже + `entities/consents/ui/ConsentRequiredPanel` (ROADMAP §8.2,
 * рабочий минимум вместо полного экрана L3).
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

/** Структурная форма 403 гейта согласия (`app/api/_consent_guard.py`) — для мест, которым
 * нужна кликабельная кнопка «Дать согласие» (`ConsentRequiredPanel`), не только текст.
 * Возвращает `null` для любой другой формы ошибки — вызывающий код решает, что показать
 * в этом случае (обычный `extractErrorMessage`), не эта функция. */
export interface ConsentRequiredDetail {
  consentType: string;
  message: string;
  documentTitle: string;
  documentUrl: string;
}

export function getConsentRequiredDetail(error: unknown): ConsentRequiredDetail | null {
  if (!error || typeof error !== "object" || !("detail" in error)) return null;
  const detail = (error as { detail: unknown }).detail;
  if (!detail || typeof detail !== "object") return null;
  const { code, consent_type, message, document } = detail as {
    code?: unknown;
    consent_type?: unknown;
    message?: unknown;
    document?: { title?: unknown; url?: unknown };
  };
  if (code !== "consent_required") return null;
  if (typeof consent_type !== "string" || typeof message !== "string") return null;
  return {
    consentType: consent_type,
    message,
    documentTitle: typeof document?.title === "string" ? document.title : "",
    documentUrl: typeof document?.url === "string" ? document.url : "",
  };
}
