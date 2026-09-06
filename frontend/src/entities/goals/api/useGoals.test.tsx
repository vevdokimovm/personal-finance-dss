import { describe, expect, it, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";

/**
 * Третий хук слоя `entities` (см. `docs/reports/testing/frontend_coverage.md`).
 *
 * 🔴 **У целей есть операция, какой нет у остальных сущностей: «внести прогресс».**
 * Она ПРИБАВЛЯЕТ к `current_amount`, а не перезаписывает его — решение владельца,
 * отдельное действие вместо общей правки. Спутать её с `useUpdateGoal` значит
 * заменить накопленное на внесённое: человек копил год, внёс 5000 и увидел 5000
 * вместо 305000. Потеря невосстановима из интерфейса.
 *
 * Поэтому здесь проверяется не только ключ кэша, но и **что мутации ходят разными
 * путями**: `PUT /api/goals/{id}` против `POST /api/goals/{id}/contributions`.
 */

const listGoals = vi.fn();
const createGoal = vi.fn();
const updateGoal = vi.fn();
const addContribution = vi.fn();
const deleteGoal = vi.fn();
const restoreGoal = vi.fn();

vi.mock("@shared/api/generated", () => ({
  listGoalsApiGoalsGet: (...a: unknown[]) => listGoals(...a),
  createGoalEndpointApiGoalsPost: (...a: unknown[]) => createGoal(...a),
  updateGoalEndpointApiGoalsGoalIdPut: (...a: unknown[]) => updateGoal(...a),
  addGoalContributionEndpointApiGoalsGoalIdContributionsPost: (...a: unknown[]) =>
    addContribution(...a),
  deleteGoalEndpointApiGoalsGoalIdDelete: (...a: unknown[]) => deleteGoal(...a),
  restoreGoalEndpointApiGoalsGoalIdRestorePost: (...a: unknown[]) => restoreGoal(...a),
}));

const {
  useGoals,
  useCreateGoal,
  useUpdateGoal,
  useAddGoalContribution,
  useDeleteGoal,
  useRestoreGoal,
} = await import("./useGoals");

const QUERY_KEY = { queryKey: ["goals", "list"] };

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

describe("useGoals — чтение", () => {
  it("отдаёт список целей", async () => {
    listGoals.mockResolvedValue({ data: [{ id: 1, name: "Подушка" }] });
    const { wrapper } = makeWrapper();
    const { result } = renderHook(() => useGoals(), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(listGoals).toHaveBeenCalledWith({ throwOnError: true });
    expect(result.current.data).toHaveLength(1);
  });

  it("код ответа сохраняется в ошибке", async () => {
    listGoals.mockRejectedValue({ detail: "Требуется согласие.", status: 403 });
    const { wrapper } = makeWrapper();
    const { result } = renderHook(() => useGoals(), { wrapper });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect((result.current.error as { status?: number })?.status).toBe(403);
  });
});

describe("useAddGoalContribution — прибавляет, а не перезаписывает", () => {
  it("идёт СВОИМ путём, не через обновление цели", async () => {
    /* 🔴 Главная проверка файла. `POST /api/goals/{id}/contributions` прибавляет
       к накопленному; `PUT /api/goals/{id}` перезаписывает поля. Перепутать их —
       значит стереть накопленное за год одним взносом, и человек этого не отменит. */
    addContribution.mockResolvedValue({ data: { id: 1, current_amount: 305000 } });
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const { result } = renderHook(() => useAddGoalContribution(), { wrapper });
    result.current.mutate({ id: 4, body: { amount: 5000 } });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(addContribution).toHaveBeenCalledWith({
      path: { goal_id: 4 },
      body: { amount: 5000 },
      throwOnError: true,
    });
    expect(updateGoal).not.toHaveBeenCalled();
    expect(invalidate).toHaveBeenCalledWith(QUERY_KEY);
  });

  it("409 у цели, связанной с активом, доезжает как 409", async () => {
    /* Цель с `linked_asset_id` пополняется через актив, а не напрямую — бэкенд
       отвечает 409. Экран обязан объяснить это, а не показать общее «не вышло»,
       поэтому код ответа должен сохраниться. */
    addContribution.mockRejectedValue({
      detail: "Цель связана с активом.",
      status: 409,
    });
    const { wrapper } = makeWrapper();
    const { result } = renderHook(() => useAddGoalContribution(), { wrapper });
    result.current.mutate({ id: 4, body: { amount: 5000 } });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect((result.current.error as { status?: number })?.status).toBe(409);
  });
});

describe("useGoals — остальные мутации", () => {
  it("создание шлёт тело по контракту", async () => {
    createGoal.mockResolvedValue({ data: { id: 2 } });
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const body = { name: "Отпуск", target_amount: 200000 };
    const { result } = renderHook(() => useCreateGoal(), { wrapper });
    result.current.mutate(body);

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(createGoal).toHaveBeenCalledWith({ body, throwOnError: true });
    expect(invalidate).toHaveBeenCalledWith(QUERY_KEY);
  });

  it("правка кладёт id в путь", async () => {
    updateGoal.mockResolvedValue({ data: { id: 2 } });
    const { wrapper } = makeWrapper();

    const { result } = renderHook(() => useUpdateGoal(), { wrapper });
    result.current.mutate({ id: 2, body: { name: "Отпуск в горах" } });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(updateGoal).toHaveBeenCalledWith({
      path: { goal_id: 2 },
      body: { name: "Отпуск в горах" },
      throwOnError: true,
    });
  });

  it("удаление возвращает id, восстановление делит тот же ключ", async () => {
    deleteGoal.mockResolvedValue({ data: null });
    restoreGoal.mockResolvedValue({ data: { id: 3 } });
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const del = renderHook(() => useDeleteGoal(), { wrapper });
    del.result.current.mutate(3);
    await waitFor(() => expect(del.result.current.isSuccess).toBe(true));
    expect(del.result.current.data).toBe(3);

    const restore = renderHook(() => useRestoreGoal(), { wrapper });
    restore.result.current.mutate(3);
    await waitFor(() => expect(restore.result.current.isSuccess).toBe(true));

    expect(invalidate).toHaveBeenCalledTimes(2);
    expect(invalidate).toHaveBeenCalledWith(QUERY_KEY);
  });

  it("провалившаяся мутация список не трогает", async () => {
    createGoal.mockRejectedValue({ detail: "Сумма должна быть больше нуля.", status: 422 });
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const { result } = renderHook(() => useCreateGoal(), { wrapper });
    result.current.mutate({ name: "", target_amount: 0 });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(invalidate).not.toHaveBeenCalled();
  });
});
