import { describe, expect, it, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";

/**
 * Пятый хук слоя `entities` (см. `docs/reports/testing/frontend_coverage.md`).
 *
 * 🔴 **Ликвидные активы задают инвариант, а не просто число.** Из них считается
 * `Lt` — покрытие резервом, и на нём стоит жёсткое ограничение модели `Rt ≥ 0`
 * (канон v3.9.0). Список из устаревшего кэша означает план, посчитанный от резерва,
 * которого уже нет: система предложит гасить долг деньгами, потраченными вчера.
 *
 * Проверяется не работа react-query, а что передаёт наш код: путь, тело, ключ кэша.
 */

const listAssets = vi.fn();
const addAsset = vi.fn();
const updateAsset = vi.fn();
const removeAsset = vi.fn();
const restoreAsset = vi.fn();

vi.mock("@shared/api/generated", () => ({
  listAssetsApiLiquidAssetsGet: (...a: unknown[]) => listAssets(...a),
  addAssetApiLiquidAssetsPost: (...a: unknown[]) => addAsset(...a),
  updateAssetApiLiquidAssetsAssetIdPut: (...a: unknown[]) => updateAsset(...a),
  removeAssetApiLiquidAssetsAssetIdDelete: (...a: unknown[]) => removeAsset(...a),
  restoreAssetApiLiquidAssetsAssetIdRestorePost: (...a: unknown[]) => restoreAsset(...a),
}));

const { useLiquidAssets, useCreateAsset, useUpdateAsset, useDeleteAsset, useRestoreAsset } =
  await import("./useLiquidAssets");

const QUERY_KEY = { queryKey: ["liquid-assets", "list"] };

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

describe("useLiquidAssets — чтение", () => {
  it("отдаёт список активов", async () => {
    listAssets.mockResolvedValue({ data: [{ id: 1, name: "Накопительный", amount: 120000 }] });
    const { wrapper } = makeWrapper();
    const { result } = renderHook(() => useLiquidAssets(), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(listAssets).toHaveBeenCalledWith({ throwOnError: true });
    expect(result.current.data).toHaveLength(1);
  });

  it("код ответа сохраняется в ошибке", async () => {
    listAssets.mockRejectedValue({ detail: "Требуется согласие.", status: 403 });
    const { wrapper } = makeWrapper();
    const { result } = renderHook(() => useLiquidAssets(), { wrapper });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect((result.current.error as { status?: number })?.status).toBe(403);
  });
});

describe("useLiquidAssets — мутации", () => {
  it("создание шлёт тело и обновляет список", async () => {
    addAsset.mockResolvedValue({ data: { id: 3 } });
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const body = { name: "Накопительный счёт", amount: 120000 };
    const { result } = renderHook(() => useCreateAsset(), { wrapper });
    result.current.mutate(body);

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(addAsset).toHaveBeenCalledWith({ body, throwOnError: true });
    expect(invalidate).toHaveBeenCalledWith(QUERY_KEY);
  });

  it("правка кладёт id в путь", async () => {
    /* 🔴 Правка суммы актива меняет `Lt` и, через него, всю рекомендацию.
       Изменить не ту строку — значит выдать план от резерва, которого нет. */
    updateAsset.mockResolvedValue({ data: { id: 6 } });
    const { wrapper } = makeWrapper();

    const { result } = renderHook(() => useUpdateAsset(), { wrapper });
    result.current.mutate({ id: 6, body: { amount: 90000 } });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(updateAsset).toHaveBeenCalledWith({
      path: { asset_id: 6 },
      body: { amount: 90000 },
      throwOnError: true,
    });
  });

  it("удаление возвращает id, восстановление делит тот же ключ", async () => {
    removeAsset.mockResolvedValue({ data: null });
    restoreAsset.mockResolvedValue({ data: { id: 6 } });
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const del = renderHook(() => useDeleteAsset(), { wrapper });
    del.result.current.mutate(6);
    await waitFor(() => expect(del.result.current.isSuccess).toBe(true));
    expect(del.result.current.data).toBe(6);

    const restore = renderHook(() => useRestoreAsset(), { wrapper });
    restore.result.current.mutate(6);
    await waitFor(() => expect(restore.result.current.isSuccess).toBe(true));

    expect(invalidate).toHaveBeenCalledTimes(2);
    expect(invalidate).toHaveBeenCalledWith(QUERY_KEY);
  });

  it("провалившаяся мутация список не трогает", async () => {
    addAsset.mockRejectedValue({ detail: "Сумма должна быть больше нуля.", status: 422 });
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const { result } = renderHook(() => useCreateAsset(), { wrapper });
    result.current.mutate({ name: "", amount: 0 });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(invalidate).not.toHaveBeenCalled();
  });
});
