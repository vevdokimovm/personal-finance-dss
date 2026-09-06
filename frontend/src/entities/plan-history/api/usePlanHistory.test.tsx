import { describe, expect, it, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";

/**
 * Девятый хук слоя `entities` (см. `docs/reports/testing/frontend_coverage.md`).
 *
 * 🔴 **Снимок плана — единственная сущность, которую бэкенд считает ЗАНОВО, а не
 * принимает готовой.** Экран не отправляет то, что показал: он шлёт параметры,
 * и модель пересчитывает по ним. Иначе в историю попало бы отображённое, а не то,
 * что даёт модель, — и снимок перестал бы быть свидетельством.
 *
 * 🔴 **Отмена удаления заведена в v8.38.0 и не была декоративной:** удаление снимка
 * было мягким и раньше, но вернуть его пользователь не мог никак — единственная
 * сущность продукта без отмены, при том что у целей, активов, обязательств, операций
 * и бюджетов она есть. Данные лежали в базе и были недостижимы: «сказали, что удалили,
 * а на деле спрятали».
 */

const listHistory = vi.fn();
const saveSnapshot = vi.fn();
const deleteSnapshot = vi.fn();
const restoreSnapshot = vi.fn();

vi.mock("@shared/api/generated", () => ({
  listPlanHistoryApiPlanningHistoryGet: (...a: unknown[]) => listHistory(...a),
  savePlanHistoryApiPlanningHistoryPost: (...a: unknown[]) => saveSnapshot(...a),
  deletePlanHistoryApiPlanningHistorySnapshotIdDelete: (...a: unknown[]) => deleteSnapshot(...a),
  restorePlanHistoryApiPlanningHistorySnapshotIdRestorePost: (...a: unknown[]) =>
    restoreSnapshot(...a),
}));

const { usePlanHistory, useSavePlanSnapshot, useDeletePlanSnapshot, useRestorePlanSnapshot } =
  await import("./usePlanHistory");

const QUERY_KEY = { queryKey: ["plan-history"] };

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

describe("usePlanHistory — чтение", () => {
  it("отдаёт список снимков", async () => {
    listHistory.mockResolvedValue({ data: { items: [{ id: 1, note: "До отпуска" }] } });
    const { wrapper } = makeWrapper();
    const { result } = renderHook(() => usePlanHistory(), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(listHistory).toHaveBeenCalledWith({ throwOnError: true });
    expect(result.current.data).toMatchObject({ items: [{ id: 1 }] });
  });
});

describe("useSavePlanSnapshot — шлёт ПАРАМЕТРЫ, а не готовый план", () => {
  it("тело содержит заметку и риск-профиль, и ничего больше", async () => {
    /* 🔴 Проверка закрепляет решение бэкенда: снимок пересчитывается по параметрам,
       чтобы быть согласованным сам с собом. Отправь сюда посчитанные суммы —
       и в истории оказалось бы то, что показал экран, а не то, что даёт модель. */
    saveSnapshot.mockResolvedValue({ data: { id: 11 } });
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const body = { note: "До отпуска", risk_tolerance: 3 };
    const { result } = renderHook(() => useSavePlanSnapshot(), { wrapper });
    result.current.mutate(body);

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(saveSnapshot).toHaveBeenCalledWith({ body, throwOnError: true });
    expect(invalidate).toHaveBeenCalledWith(QUERY_KEY);
  });

  it("снимок без заметки — законный случай", async () => {
    /* Заметка необязательна: человек сохраняет «как есть», чтобы вернуться позже.
       Требовать её значило бы мешать ровно в тот момент, когда он торопится. */
    saveSnapshot.mockResolvedValue({ data: { id: 12 } });
    const { wrapper } = makeWrapper();

    const { result } = renderHook(() => useSavePlanSnapshot(), { wrapper });
    result.current.mutate({ note: null, risk_tolerance: null });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(saveSnapshot).toHaveBeenCalledWith({
      body: { note: null, risk_tolerance: null },
      throwOnError: true,
    });
  });
});

describe("Удаление и отмена — обе половины одной пары", () => {
  it("удаление идёт своим путём и обновляет список", async () => {
    deleteSnapshot.mockResolvedValue({ data: { id: 11 } });
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const { result } = renderHook(() => useDeletePlanSnapshot(), { wrapper });
    result.current.mutate(11);

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(deleteSnapshot).toHaveBeenCalledWith({
      path: { snapshot_id: 11 },
      throwOnError: true,
    });
    expect(invalidate).toHaveBeenCalledWith(QUERY_KEY);
  });

  it("🔴 отмена существует и делит ключ с удалением", async () => {
    /* Проверка стоит отдельно намеренно. До v8.38.0 удаление было мягким, а отмены
       не было вовсе: данные лежали в базе и были недостижимы. Тест, падающий при
       удалении `useRestorePlanSnapshot`, — единственное, что мешает вернуть
       то состояние «сказали, что удалили, а на деле спрятали». */
    restoreSnapshot.mockResolvedValue({ data: { id: 11 } });
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const { result } = renderHook(() => useRestorePlanSnapshot(), { wrapper });
    result.current.mutate(11);

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(restoreSnapshot).toHaveBeenCalledWith({
      path: { snapshot_id: 11 },
      throwOnError: true,
    });
    expect(invalidate).toHaveBeenCalledWith(QUERY_KEY);
  });

  it("провалившееся удаление список не трогает", async () => {
    deleteSnapshot.mockRejectedValue({ detail: "Снимок не найден.", status: 404 });
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const { result } = renderHook(() => useDeletePlanSnapshot(), { wrapper });
    result.current.mutate(999);

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(invalidate).not.toHaveBeenCalled();
  });
});
