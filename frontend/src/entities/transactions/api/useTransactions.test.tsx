import { describe, expect, it, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";

/**
 * Четвёртый хук слоя `entities` (см. `docs/reports/testing/frontend_coverage.md`).
 *
 * 🔴 **Транзакции — вход всей модели.** Доход и расходы за месяц считаются по ним,
 * из них берётся свободный денежный поток, а из него — план распределения. Список,
 * показанный из устаревшего кэша, означает, что человек видит один набор операций,
 * а рекомендация посчитана по другому.
 *
 * Проверяется не работа react-query, а что передаёт наш код: путь, тело, ключ кэша.
 */

const listTransactions = vi.fn();
const createTransaction = vi.fn();
const updateTransaction = vi.fn();
const deleteTransaction = vi.fn();
const restoreTransaction = vi.fn();

vi.mock("@shared/api/generated", () => ({
  getTransactionsEndpointApiTransactionsGet: (...a: unknown[]) => listTransactions(...a),
  createTransactionEndpointApiTransactionsPost: (...a: unknown[]) => createTransaction(...a),
  updateTransactionEndpointApiTransactionsTransactionIdPut: (...a: unknown[]) =>
    updateTransaction(...a),
  deleteTransactionEndpointApiTransactionsTransactionIdDelete: (...a: unknown[]) =>
    deleteTransaction(...a),
  restoreTransactionEndpointApiTransactionsTransactionIdRestorePost: (...a: unknown[]) =>
    restoreTransaction(...a),
}));

const {
  useTransactions,
  useCreateTransaction,
  useUpdateTransaction,
  useDeleteTransaction,
  useRestoreTransaction,
} = await import("./useTransactions");

const QUERY_KEY = { queryKey: ["transactions", "list"] };

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

describe("useTransactions — чтение", () => {
  it("отдаёт список операций", async () => {
    listTransactions.mockResolvedValue({
      data: [{ id: 1, amount: -1200, category: "Продукты" }],
    });
    const { wrapper } = makeWrapper();
    const { result } = renderHook(() => useTransactions(), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(listTransactions).toHaveBeenCalledWith({ throwOnError: true });
    expect(result.current.data).toHaveLength(1);
  });

  it("код ответа сохраняется в ошибке", async () => {
    /* 403 от гейта согласия обязан отличаться от сетевой ошибки: иначе человеку
       предложат «Повторить» там, где нужна кнопка «Дать согласие». */
    listTransactions.mockRejectedValue({ detail: "Требуется согласие.", status: 403 });
    const { wrapper } = makeWrapper();
    const { result } = renderHook(() => useTransactions(), { wrapper });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect((result.current.error as { status?: number })?.status).toBe(403);
  });
});

describe("useTransactions — мутации", () => {
  it("создание шлёт тело и обновляет список", async () => {
    createTransaction.mockResolvedValue({ data: { id: 2 } });
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    /* 🔴 `type` обязателен по контракту, и это не формальность: направление
       операции задаётся ИМ, а не знаком суммы. Расход с положительной суммой
       и `type: "expense"` — валидная запись, и модель считает по `type`. */
    const body = {
      amount: 1200,
      type: "expense" as const,
      description: "Пятёрочка",
      date: "2026-09-06",
    };
    const { result } = renderHook(() => useCreateTransaction(), { wrapper });
    result.current.mutate(body);

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(createTransaction).toHaveBeenCalledWith({ body, throwOnError: true });
    expect(invalidate).toHaveBeenCalledWith(QUERY_KEY);
  });

  it("правка кладёт id в путь, а не в тело", async () => {
    /* Перепутать легко, и последствие тихое: изменилась бы не та операция,
       а месячные суммы поехали бы у обеих. */
    updateTransaction.mockResolvedValue({ data: { id: 8 } });
    const { wrapper } = makeWrapper();

    const { result } = renderHook(() => useUpdateTransaction(), { wrapper });
    result.current.mutate({ id: 8, body: { category: "Кафе" } });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(updateTransaction).toHaveBeenCalledWith({
      path: { transaction_id: 8 },
      body: { category: "Кафе" },
      throwOnError: true,
    });
  });

  it("удаление возвращает id, восстановление делит тот же ключ", async () => {
    deleteTransaction.mockResolvedValue({ data: null });
    restoreTransaction.mockResolvedValue({ data: { id: 8 } });
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const del = renderHook(() => useDeleteTransaction(), { wrapper });
    del.result.current.mutate(8);
    await waitFor(() => expect(del.result.current.isSuccess).toBe(true));
    expect(del.result.current.data).toBe(8);

    const restore = renderHook(() => useRestoreTransaction(), { wrapper });
    restore.result.current.mutate(8);
    await waitFor(() => expect(restore.result.current.isSuccess).toBe(true));

    expect(invalidate).toHaveBeenCalledTimes(2);
    expect(invalidate).toHaveBeenCalledWith(QUERY_KEY);
  });

  it("провалившаяся мутация список не трогает", async () => {
    createTransaction.mockRejectedValue({ detail: "Дата в будущем.", status: 422 });
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const { result } = renderHook(() => useCreateTransaction(), { wrapper });
    result.current.mutate({
      amount: 0,
      type: "expense" as const,
      description: "",
      date: "2099-01-01",
    });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(invalidate).not.toHaveBeenCalled();
  });
});
