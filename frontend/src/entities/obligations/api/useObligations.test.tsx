import { describe, expect, it, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";

/**
 * Второй хук слоя `entities` (см. `useBudgets.test.tsx` и
 * `docs/reports/testing/frontend_coverage.md`): слой покрыт на 7.2 % при 69.6 %
 * по фронту, и весь разрыв фронта против бэкенда сидит именно здесь.
 *
 * 🔴 **У обязательств цена ошибки выше, чем у бюджетов.** Обязательство — это долг:
 * ставка, минимальный платёж, остаток. Оно входит в расчёт ПДН и в Avalanche-фильтр,
 * то есть определяет, какой долг система предложит гасить первым. Список, показанный
 * из устаревшего кэша после правки ставки, означает совет, посчитанный по числам,
 * которых уже нет.
 *
 * Проверяется не работа react-query, а что передаёт наш код: путь, тело, ключ.
 */

const listObligations = vi.fn();
const createObligation = vi.fn();
const updateObligation = vi.fn();
const deleteObligation = vi.fn();
const restoreObligation = vi.fn();

vi.mock("@shared/api/generated", () => ({
  getObligationsEndpointApiObligationsGet: (...a: unknown[]) => listObligations(...a),
  createObligationEndpointApiObligationsPost: (...a: unknown[]) => createObligation(...a),
  updateObligationEndpointApiObligationsObligationIdPut: (...a: unknown[]) =>
    updateObligation(...a),
  deleteObligationEndpointApiObligationsObligationIdDelete: (...a: unknown[]) =>
    deleteObligation(...a),
  restoreObligationEndpointApiObligationsObligationIdRestorePost: (...a: unknown[]) =>
    restoreObligation(...a),
}));

const {
  useObligations,
  useCreateObligation,
  useUpdateObligation,
  useDeleteObligation,
  useRestoreObligation,
} = await import("./useObligations");

const QUERY_KEY = { queryKey: ["obligations", "list"] };

function makeWrapper() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  const wrapper = ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={client}>{children}</QueryClientProvider>
  );
  return { client, wrapper };
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("useObligations — чтение списка", () => {
  it("отдаёт список как есть", async () => {
    listObligations.mockResolvedValue({
      data: [{ id: 1, name: "Кредитка", interest_rate: 0.39 }],
    });
    const { wrapper } = makeWrapper();
    const { result } = renderHook(() => useObligations(), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(listObligations).toHaveBeenCalledWith({ throwOnError: true });
    expect(result.current.data).toHaveLength(1);
  });

  it("код ответа доезжает до потребителя", async () => {
    /* Экран обязательств за гейтом согласия на финданные: 403 здесь — штатный
       ответ, и он обязан отличаться от сетевой ошибки, иначе человеку предложат
       «Повторить» вместо «Дать согласие». */
    listObligations.mockRejectedValue({ detail: "Требуется согласие.", status: 403 });
    const { wrapper } = makeWrapper();
    const { result } = renderHook(() => useObligations(), { wrapper });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect((result.current.error as { status?: number })?.status).toBe(403);
  });
});

describe("useObligations — мутации обновляют список", () => {
  it("создание шлёт тело и инвалидирует список", async () => {
    createObligation.mockResolvedValue({ data: { id: 3 } });
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const { result } = renderHook(() => useCreateObligation(), { wrapper });
    /* Тело — полное по контракту: `amount` и `monthly_payment` обязательны.
       🔴 Ставка это ДОЛЯ (0.39 = 39 %), а не проценты. Ровно на этом сгорел PIT-031:
       тест был написан под то же неверное представление, что и код, и оба сошлись
       на 39 вместо 0.39 — зелёный тест поверх неверного расчёта. */
    const body = {
      name: "Кредитка",
      amount: 120000,
      monthly_payment: 8000,
      interest_rate: 0.39,
    };
    result.current.mutate(body);

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(createObligation).toHaveBeenCalledWith({ body, throwOnError: true });
    expect(invalidate).toHaveBeenCalledWith(QUERY_KEY);
  });

  it("правка кладёт id в путь, а не в тело", async () => {
    /* 🔴 Перепутать легко, и последствие тихое: `PUT /api/obligations/{id}` с id
       внутри тела ушёл бы не на тот адрес либо изменил бы не ту запись.
       Ставка и минимальный платёж входят в расчёт ПДН — правка не той строки
       меняет совет по всем долгам сразу. */
    updateObligation.mockResolvedValue({ data: { id: 5 } });
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const { result } = renderHook(() => useUpdateObligation(), { wrapper });
    result.current.mutate({ id: 5, body: { interest_rate: 0.25 } });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(updateObligation).toHaveBeenCalledWith({
      path: { obligation_id: 5 },
      body: { interest_rate: 0.25 },
      throwOnError: true,
    });
    expect(invalidate).toHaveBeenCalledWith(QUERY_KEY);
  });

  it("удаление возвращает id — на нём держится «отменить»", async () => {
    deleteObligation.mockResolvedValue({ data: null });
    const { wrapper } = makeWrapper();

    const { result } = renderHook(() => useDeleteObligation(), { wrapper });
    result.current.mutate(9);

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(deleteObligation).toHaveBeenCalledWith({
      path: { obligation_id: 9 },
      throwOnError: true,
    });
    expect(result.current.data).toBe(9);
  });

  it("восстановление делит ключ кэша с остальными мутациями", async () => {
    /* Общий ключ — решение, а не совпадение: разведи его, и список после «отменить»
       остался бы без восстановленного долга, то есть ПДН считался бы без него. */
    restoreObligation.mockResolvedValue({ data: { id: 9 } });
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const { result } = renderHook(() => useRestoreObligation(), { wrapper });
    result.current.mutate(9);

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(restoreObligation).toHaveBeenCalledWith({
      path: { obligation_id: 9 },
      throwOnError: true,
    });
    expect(invalidate).toHaveBeenCalledWith(QUERY_KEY);
  });

  it("провалившаяся мутация список не трогает", async () => {
    updateObligation.mockRejectedValue({ detail: "Ставка вне диапазона.", status: 422 });
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const { result } = renderHook(() => useUpdateObligation(), { wrapper });
    result.current.mutate({ id: 5, body: { interest_rate: 99 } });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(invalidate).not.toHaveBeenCalled();
  });
});
