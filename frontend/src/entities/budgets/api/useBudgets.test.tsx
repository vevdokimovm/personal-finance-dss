import { describe, expect, it, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";

/**
 * Слой `entities/<сущность>/api` покрыт на **7.2 %** строк при 68.6 % по фронту в целом
 * (замер v9.2.0, `npm run test:coverage`). Это худший слой — и единственный,
 * который разговаривает с бэкендом: здесь живут ключи кэша, инвалидация
 * и разбор ответа.
 *
 * 🔴 **Почему дыра именно здесь дороже прочих.** Ошибка в ключе инвалидации ничего
 * не роняет и не видна глазами: запрос уходит, ответ приходит, экран показывает
 * **старые** данные. Человек добавил бюджет, увидел прежний список и добавил ещё раз.
 * Класс «работает, но показывает не то» ручная проверка не ловит вовсе.
 *
 * Здесь проверяется НЕ то, что react-query умеет делать запросы — это его работа, —
 * а что передаёт наш код: правильный путь, правильное тело, правильный ключ.
 */

const budgetStatusGet = vi.fn();
const addBudget = vi.fn();
const removeBudget = vi.fn();
const restoreBudget = vi.fn();

vi.mock("@shared/api/generated", () => ({
  budgetStatusApiBudgetsStatusGet: (...args: unknown[]) => budgetStatusGet(...args),
  addBudgetApiBudgetsPost: (...args: unknown[]) => addBudget(...args),
  removeBudgetApiBudgetsBudgetIdDelete: (...args: unknown[]) => removeBudget(...args),
  restoreBudgetEndpointApiBudgetsBudgetIdRestorePost: (...args: unknown[]) =>
    restoreBudget(...args),
}));

const { useBudgetStatus, useCreateBudget, useDeleteBudget, useRestoreBudget } =
  await import("./useBudgets");

function makeWrapper() {
  /* `retry: false` — иначе проверка ошибки ждёт три повтора с паузами и падает
     по таймауту, сообщая про время вместо предмета. */
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

describe("useBudgetStatus", () => {
  it("берёт план-факт, а не голый список бюджетов", async () => {
    /* Докстрока хука объясняет выбор эндпоинта: строке списка нужны spent/pct/over,
       которых в `BudgetResponse` нет. Тест закрепляет решение — подмена на
       `GET /api/budgets` прошла бы типизацию и убрала бы проценты с экрана. */
    budgetStatusGet.mockResolvedValue({
      data: [{ id: 1, category: "Продукты", spent: 500 }],
    });

    const { wrapper } = makeWrapper();
    const { result } = renderHook(() => useBudgetStatus(), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(budgetStatusGet).toHaveBeenCalledWith({ throwOnError: true });
    expect(result.current.data).toHaveLength(1);
  });

  it("пустой ответ отдаёт массивом, а не undefined", async () => {
    /* 🔴 `data ?? []` в хуке — не косметика: потребители зовут `.map` сразу.
       Без подстановки пустой экран падал бы целиком вместо «пока пусто». */
    budgetStatusGet.mockResolvedValue({ data: undefined });

    const { wrapper } = makeWrapper();
    const { result } = renderHook(() => useBudgetStatus(), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual([]);
  });

  it("ошибку не проглатывает и сохраняет код ответа", async () => {
    /* `status` в ошибке появился только в v9.1.0 (error-интерцептор): до него
       `error.status === 403` всегда давало false, и хуки ретраили то, что
       ретраить нельзя. Проверка закрепляет, что код доезжает до потребителя. */
    budgetStatusGet.mockRejectedValue({ detail: "Требуется согласие.", status: 403 });

    const { wrapper } = makeWrapper();
    const { result } = renderHook(() => useBudgetStatus(), { wrapper });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect((result.current.error as { status?: number })?.status).toBe(403);
  });
});

describe("useCreateBudget", () => {
  it("шлёт тело как есть и обновляет список после успеха", async () => {
    /* 🔴 Инвалидация — главное, что здесь ломается незаметно. На бэке
       `POST /api/budgets` работает upsert-ом по категории: правка лимита это
       повторный POST. Без инвалидации человек увидит СТАРЫЙ лимит после правки
       и решит, что форма не сработала. */
    addBudget.mockResolvedValue({ data: { id: 7 } });
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const { result } = renderHook(() => useCreateBudget(), { wrapper });
    result.current.mutate({ category: "Продукты", limit_amount: 15000 });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(addBudget).toHaveBeenCalledWith({
      body: { category: "Продукты", limit_amount: 15000 },
      throwOnError: true,
    });
    expect(invalidate).toHaveBeenCalledWith({ queryKey: ["budgets", "status"] });
  });

  it("при ошибке список не трогает", async () => {
    /* Инвалидация на провалившейся мутации — лишний запрос и мигание экрана там,
       где ничего не изменилось. */
    addBudget.mockRejectedValue(new Error("422"));
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const { result } = renderHook(() => useCreateBudget(), { wrapper });
    result.current.mutate({ category: "", limit_amount: -1 });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(invalidate).not.toHaveBeenCalled();
  });
});

describe("useDeleteBudget и useRestoreBudget", () => {
  it("удаление передаёт id путём и возвращает его вызвавшему", async () => {
    /* Возврат id — не формальность: строка списка показывает «отменить» именно
       для того бюджета, который только что удалили. */
    removeBudget.mockResolvedValue({ data: null });
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const { result } = renderHook(() => useDeleteBudget(), { wrapper });
    result.current.mutate(42);

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(removeBudget).toHaveBeenCalledWith({
      path: { budget_id: 42 },
      throwOnError: true,
    });
    expect(result.current.data).toBe(42);
    expect(invalidate).toHaveBeenCalledWith({ queryKey: ["budgets", "status"] });
  });

  it("восстановление ходит по своему пути и делит ключ кэша с удалением", async () => {
    /* 🔴 Общий ключ — решение, а не совпадение: разведи их, и экран после «отменить»
       показал бы список без восстановленного бюджета. Оба ожидания стоят рядом
       намеренно, чтобы правка ключа в одном хуке роняла проверку сразу. */
    restoreBudget.mockResolvedValue({ data: { id: 42 } });
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const { result } = renderHook(() => useRestoreBudget(), { wrapper });
    result.current.mutate(42);

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(restoreBudget).toHaveBeenCalledWith({
      path: { budget_id: 42 },
      throwOnError: true,
    });
    expect(invalidate).toHaveBeenCalledWith({ queryKey: ["budgets", "status"] });
  });
});
