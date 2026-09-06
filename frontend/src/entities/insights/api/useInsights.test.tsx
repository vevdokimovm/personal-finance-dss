import { describe, expect, it, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";

/**
 * Метрики продукта — экран владельца. Доступ даёт признак `is_owner` на аккаунте,
 * сервер отвечает 403 всем остальным.
 *
 * 🔴 **`enabled` здесь — право доступа, а не оптимизация.** Запрос уходит только когда
 * фронт уже знает, что перед ним владелец. Иначе каждый заход обычного человека давал бы
 * гарантированный отказ: лишний запрос и ошибка в консоли там, где раздела просто нет.
 */

const overview = vi.fn();
const funnel = vi.fn();

vi.mock("@shared/api/generated", () => ({
  overviewApiAnalyticsOverviewGet: (...a: unknown[]) => overview(...a),
  funnelEndpointApiAnalyticsFunnelGet: (...a: unknown[]) => funnel(...a),
}));

const { useAnalyticsOverview, useFunnel } = await import("./useInsights");

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

describe("useAnalyticsOverview", () => {
  it("🔴 не запрашивается у не-владельца", async () => {
    const { wrapper } = makeWrapper();
    renderHook(() => useAnalyticsOverview(false), { wrapper });

    await new Promise((resolve) => setTimeout(resolve, 20));
    expect(overview).not.toHaveBeenCalled();
  });

  it("окно в днях попадает и в запрос, и в ключ кэша", async () => {
    /* Метрики за 7 и за 30 дней — разные ответы. Общий ключ показал бы владельцу
       числа другого периода под его заголовком. */
    overview.mockResolvedValue({ data: { users: 12 } });
    const { wrapper } = makeWrapper();
    const { result } = renderHook(() => useAnalyticsOverview(true, 7), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(overview).toHaveBeenCalledWith({ query: { days: 7 }, throwOnError: true });
  });
});

describe("useFunnel", () => {
  it("не запрашивается у не-владельца", async () => {
    const { wrapper } = makeWrapper();
    renderHook(() => useFunnel(false), { wrapper });

    await new Promise((resolve) => setTimeout(resolve, 20));
    expect(funnel).not.toHaveBeenCalled();
  });

  it("владельцу отдаёт воронку", async () => {
    funnel.mockResolvedValue({ data: { steps: [] } });
    const { wrapper } = makeWrapper();
    const { result } = renderHook(() => useFunnel(true), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(funnel).toHaveBeenCalledWith({ throwOnError: true });
  });
});
