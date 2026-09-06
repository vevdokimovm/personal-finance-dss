import { describe, expect, it, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";

/**
 * 🔴 **Та же политика ретрая, что у колокольчика, и по той же причине.** Эндпоинт
 * за периметром `_FIN`: при отозванном согласии отвечает 403. Повторять осознанное
 * «нет» бессмысленно — повторять имеет смысл сетевой сбой.
 *
 * Политика опирается на `error.status`, которого до v9.1.0 **не существовало**:
 * сгенерированный клиент бросал только тело ответа, код терялся, и проверка
 * `status === 403` всегда давала false. Докстрока обещала «не ретраим», код ретраил,
 * и заметить это глазами было нельзя.
 *
 * Поэтому здесь проверяется **число вызовов**: оно отличает «не повторяет»
 * от «повторяет и всё равно падает».
 */

const spendingAdvice = vi.fn();

vi.mock("@shared/api/generated", () => ({
  spendingAdviceEndpointApiPlanningSpendingAdviceGet: (...a: unknown[]) => spendingAdvice(...a),
}));

const { useSpendingAdvice, DEFAULT_MONTHS } = await import("./useSpendingAdvice");

function makeWrapper() {
  /* Ретрай НЕ отключается в клиенте: политика живёт в хуке, и подменять её здесь
     значило бы проверять настройку теста вместо кода. */
  const client = new QueryClient();
  const wrapper = ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={client}>{children}</QueryClientProvider>
  );
  return { client, wrapper };
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("useSpendingAdvice", () => {
  it("окно по умолчанию совпадает с бэкендом", () => {
    /* Константа продублирована сознательно (`months: int = 6` на сервере). Подпись
       периода на экране берётся ИЗ ОТВЕТА (`months_window`), а не отсюда, поэтому
       расхождение видно сразу, а не превращается во вранье в заголовке. */
    expect(DEFAULT_MONTHS).toBe(6);
  });

  it("окно попадает и в запрос, и в ключ кэша", async () => {
    /* Окно в ключе — не формальность: анализ за 3 и за 12 месяцев это разные ответы,
       и общий ключ показал бы человеку данные другого периода под его заголовком. */
    spendingAdvice.mockResolvedValue({ data: { months_window: 12, categories: [] } });
    const { wrapper } = makeWrapper();
    const { result } = renderHook(() => useSpendingAdvice(12), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(spendingAdvice).toHaveBeenCalledWith({
      query: { months: 12 },
      throwOnError: true,
    });
  });

  it("🔴 403 не повторяется — согласие отозвано, повтор ничего не изменит", async () => {
    spendingAdvice.mockRejectedValue({ detail: "Требуется согласие.", status: 403 });
    const { wrapper } = makeWrapper();
    const { result } = renderHook(() => useSpendingAdvice(), { wrapper });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(spendingAdvice).toHaveBeenCalledTimes(1);
  });

  it("🔴 401 тоже не повторяется", async () => {
    spendingAdvice.mockRejectedValue({ detail: "Требуется аутентификация.", status: 401 });
    const { wrapper } = makeWrapper();
    const { result } = renderHook(() => useSpendingAdvice(), { wrapper });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(spendingAdvice).toHaveBeenCalledTimes(1);
  });

  it("а сетевой сбой повторяется", async () => {
    /* Обратная сторона: политика, не повторяющая ничего, лишила бы экран
       единственного случая, где повтор осмыслен. */
    spendingAdvice.mockRejectedValue(new TypeError("Failed to fetch"));
    const { wrapper } = makeWrapper();
    const { result } = renderHook(() => useSpendingAdvice(), { wrapper });

    await waitFor(() => expect(result.current.isError).toBe(true), { timeout: 5000 });
    expect(spendingAdvice.mock.calls.length).toBeGreaterThan(1);
  });
});
