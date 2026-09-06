import { describe, expect, it, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";

/**
 * A/B-эксперименты владельца. Тот же признак `is_owner`, что у метрик; `require_admin`
 * пропускает владельца без ключа.
 *
 * 🔴 **`useQueries`, а не запрос по клику** — единственное место в слое с параллельными
 * запросами. Экран отвечает на вопрос «какой эксперимент что показал», и ради ответа
 * по одному пришлось бы открыть каждый. Список короткий (единицы), цена приемлема;
 * станет длинным — здесь появится пагинация, а не ленивая загрузка по одному.
 */

const listExperiments = vi.fn();
const experimentResults = vi.fn();

vi.mock("@shared/api/generated", () => ({
  listExperimentsEndpointApiAdminExperimentsGet: (...a: unknown[]) => listExperiments(...a),
  experimentResultsEndpointApiAdminExperimentsKeyResultsGet: (...a: unknown[]) =>
    experimentResults(...a),
}));

const { useExperiments, useExperimentResults } = await import("./useExperiments");

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

describe("useExperiments", () => {
  it("не запрашивается у не-владельца", async () => {
    const { wrapper } = makeWrapper();
    renderHook(() => useExperiments(false), { wrapper });

    await new Promise((resolve) => setTimeout(resolve, 20));
    expect(listExperiments).not.toHaveBeenCalled();
  });

  it("владельцу отдаёт список", async () => {
    listExperiments.mockResolvedValue({ data: [{ key: "onboarding-v2" }] });
    const { wrapper } = makeWrapper();
    const { result } = renderHook(() => useExperiments(true), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(listExperiments).toHaveBeenCalledWith({ throwOnError: true });
  });
});

describe("useExperimentResults — результаты всех экспериментов сразу", () => {
  it("запрашивает КАЖДЫЙ ключ, а не первый", async () => {
    /* 🔴 Мутация «брать `keys[0]`» проходит типизацию и оставляет экран с одним
       результатом из трёх — молча: остальные строки просто не заполнятся. */
    experimentResults.mockResolvedValue({ data: { conversion: 0.12 } });
    const { wrapper } = makeWrapper();
    const { result } = renderHook(() => useExperimentResults(["a", "b", "c"], true), {
      wrapper,
    });

    await waitFor(() => expect(result.current.every((q) => q.isSuccess)).toBe(true));
    expect(experimentResults).toHaveBeenCalledTimes(3);
    for (const key of ["a", "b", "c"]) {
      expect(experimentResults).toHaveBeenCalledWith({ path: { key }, throwOnError: true });
    }
  });

  it("не запрашивается у не-владельца", async () => {
    const { wrapper } = makeWrapper();
    renderHook(() => useExperimentResults(["a", "b"], false), { wrapper });

    await new Promise((resolve) => setTimeout(resolve, 20));
    expect(experimentResults).not.toHaveBeenCalled();
  });

  it("пустой список ключей не даёт ни одного запроса", async () => {
    /* Экран без экспериментов — обычное состояние на старте продукта, не ошибка. */
    const { wrapper } = makeWrapper();
    const { result } = renderHook(() => useExperimentResults([], true), { wrapper });

    await new Promise((resolve) => setTimeout(resolve, 20));
    expect(result.current).toEqual([]);
    expect(experimentResults).not.toHaveBeenCalled();
  });
});
