import { describe, expect, it, beforeEach } from "vitest";
import { configureApiClient, apiClient } from "./client";

/**
 * 🔴 Нашёл `/code-review`: у ошибок сгенерированного клиента НЕТ поля `status`.
 *
 * `client.gen.ts` при неуспешном ответе делает `throw jsonError ?? textError` — бросается
 * только распарсенное тело (`{detail: "..."}`), код ответа теряется. Значит любая проверка
 * вида `error.status === 401` для всех хуков на этом клиенте всегда даёт `false`.
 *
 * Что от этого ломалось:
 * - `isSessionExpired` срабатывал только на `NotAuthenticatedError` из `useProfile`,
 *   а на остальных экранах человек с истёкшей сессией получал «Проверьте соединение»
 *   и кнопку «Повторить», возвращающую 401 по кругу — ровно тот сценарий, ради которого
 *   панель и заводилась (v9.1.0);
 * - `useSpendingAdvice` и `useNotifications` читают `error.status`, чтобы НЕ ретраить
 *   403/401, — и ретраили, вопреки собственным докстрокам.
 *
 * Тесты этого не ловили, потому что конструировали `{status: 401}` руками — фикстуру,
 * которой в рантайме не бывает (PIT-031: тест разделяет неверное представление с кодом).
 */
describe("configureApiClient — код ответа доезжает до обработчика ошибки", () => {
  beforeEach(() => {
    configureApiClient();
  });

  it("ставит error-интерцептор", () => {
    /* Без него `status` теряется в `client.gen.ts` навсегда: интерцептор —
       единственное место, где ещё виден сам `Response`. */
    expect(apiClient.interceptors.error).toBeDefined();
  });

  it("добавляет status к брошенному телу ответа", async () => {
    const fns = (apiClient.interceptors.error as unknown as { fns: unknown[] }).fns ?? [];
    const interceptor = fns.find(Boolean) as (
      error: unknown,
      response: Response,
    ) => Promise<unknown>;
    expect(interceptor).toBeTypeOf("function");

    const result = await interceptor({ detail: "Требуется аутентификация." }, {
      status: 401,
    } as Response);

    expect((result as { status?: number }).status).toBe(401);
    // Тело не теряется: `extractErrorMessage` и `getConsentRequiredDetail` читают `detail`.
    expect((result as { detail?: string }).detail).toBe("Требуется аутентификация.");
  });

  it("переживает обрыв сети, когда ответа нет вовсе", async () => {
    /* 🔴 Нашёл `/code-review` в моей же правке этого часа. `client.gen.ts` вызывает
       error-интерцепторы из `catch`, который покрывает и случай, когда упал сам `fetch`:
       офлайн, отказ DNS, прерванный запрос. Там `response` ещё `undefined`, и обращение
       к `response.status` бросало бы `TypeError`, ПОДМЕНЯЯ настоящую ошибку у каждого
       хука на клиенте.

       Заодно это делало мёртвым явный разбор обрыва сети в `useProfile`, где
       комментарий прямо говорит «response может быть undefined при обрыве сети». */
    const fns = (apiClient.interceptors.error as unknown as { fns: unknown[] }).fns ?? [];
    const interceptor = fns.find(Boolean) as (
      error: unknown,
      response: Response | undefined,
    ) => Promise<unknown>;

    const failure = new TypeError("Failed to fetch");
    const result = await interceptor(failure, undefined);

    // Ошибка возвращается как есть: подменять её выдуманным объектом значит скрыть
    // от хуков настоящую причину — а `status` тут и не существует.
    expect(result).toBe(failure);
  });

  it("строковую ошибку заворачивает в объект, не теряя текст", async () => {
    /* `client.gen.ts` бросает сырой текст, когда тело не JSON (502 от прокси, HTML
       от балансировщика). Строке нельзя присвоить поле — иначе `status` пропадёт
       молча именно там, где ошибка серверная. */
    const fns = (apiClient.interceptors.error as unknown as { fns: unknown[] }).fns ?? [];
    const interceptor = fns.find(Boolean) as (
      error: unknown,
      response: Response,
    ) => Promise<unknown>;

    const result = await interceptor("Bad Gateway", { status: 502 } as Response);

    expect((result as { status?: number }).status).toBe(502);
    expect((result as { detail?: string }).detail).toBe("Bad Gateway");
  });
});
