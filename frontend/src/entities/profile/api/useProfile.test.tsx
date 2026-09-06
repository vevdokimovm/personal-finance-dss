import { describe, expect, it, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";

/**
 * 🔴 **Единственный хук с `throwOnError: false`, и это не стиль, а необходимость.**
 *
 * `GET /api/auth/me` отвечает 401 гостю и человеку с истёкшей сессией. Отличить 401
 * от сетевого сбоя можно только имея доступ к `response.status` — а он теряется, если
 * позволить клиенту бросить исключение. От этого различия зависит, что увидит человек:
 * «Войти заново» или «Повторить».
 *
 * 🔴 **`NotAuthenticatedError` распознаётся ПО ИМЕНИ, а не через `instanceof`** (v9.1.0).
 * Импорт класса из `entities/profile` в `entities/auth` нарушил бы слоистость FSD,
 * а сравнение конструкторов ломается при дублировании модуля в сборке. Имя переживает
 * и то, и другое — и тест закрепляет именно имя.
 *
 * 🔴 **Обрыв сети до ответа: `response` — `undefined`.** `fetch` бросает раньше, чем
 * появляется `Response`, и обращение к `response.status` без `?.` дало бы `TypeError`,
 * подменяющий настоящую причину. Это тот же класс, что дефект error-интерцептора,
 * найденный `/code-review` в v9.1.0.
 */

const meRequest = vi.fn();

vi.mock("@shared/api/generated", () => ({
  meApiAuthMeGet: (...a: unknown[]) => meRequest(...a),
}));

const { useProfile, NotAuthenticatedError, PROFILE_QUERY_KEY } = await import("./useProfile");

function makeWrapper() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  const wrapper = ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={client}>{children}</QueryClientProvider>
  );
  return { client, wrapper };
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("useProfile", () => {
  it("ключ кэша — общий и стабильный", () => {
    /* Его читают топбар и все auth-хуки, которые инвалидируют профиль после входа
       и выхода. Строковый литерал в двух местах разъехался бы при первой правке. */
    expect(PROFILE_QUERY_KEY).toEqual(["profile", "me"]);
  });

  it("успешный ответ отдаёт профиль", async () => {
    meRequest.mockResolvedValue({ data: { id: "u-1", email: "a@test.io" }, error: null });
    const { wrapper } = makeWrapper();
    const { result } = renderHook(() => useProfile(), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(meRequest).toHaveBeenCalledWith({ throwOnError: false });
    expect(result.current.data).toMatchObject({ email: "a@test.io" });
  });

  it("🔴 401 превращается в NotAuthenticatedError — по ИМЕНИ", async () => {
    meRequest.mockResolvedValue({
      data: undefined,
      error: { detail: "Требуется аутентификация." },
      response: { status: 401 },
    });
    const { wrapper } = makeWrapper();
    const { result } = renderHook(() => useProfile(), { wrapper });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(result.current.error).toBeInstanceOf(NotAuthenticatedError);
    /* Проверка имени стоит рядом с `instanceof` намеренно: `isSessionExpired`
       в `entities/auth` смотрит именно на имя, и переименование класса сломало бы
       распознавание истёкшей сессии молча. */
    expect((result.current.error as Error).name).toBe("NotAuthenticatedError");
  });

  it("🔴 обрыв сети до ответа не подменяется 401", async () => {
    /* `response` здесь `undefined`. Без `?.` было бы `TypeError`, и человек получил бы
       «войдите заново» при живой сессии и мёртвом интернете — то есть пошёл бы вводить
       пароль вместо того, чтобы подождать связи. */
    const networkError = new TypeError("Failed to fetch");
    meRequest.mockResolvedValue({ data: undefined, error: networkError, response: undefined });
    const { wrapper } = makeWrapper();
    const { result } = renderHook(() => useProfile(), { wrapper });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(result.current.error).toBe(networkError);
    expect(result.current.error).not.toBeInstanceOf(NotAuthenticatedError);
  });

  it("прочие коды пробрасываются как есть", async () => {
    /* 500 — не истёкшая сессия. Показать «войдите заново» на падении сервера значит
       отправить человека вводить пароль там, где он ничем не поможет. */
    const serverError = { detail: "Внутренняя ошибка." };
    meRequest.mockResolvedValue({
      data: undefined,
      error: serverError,
      response: { status: 500 },
    });
    const { wrapper } = makeWrapper();
    const { result } = renderHook(() => useProfile(), { wrapper });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(result.current.error).toBe(serverError);
  });
});
