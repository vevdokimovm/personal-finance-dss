import { describe, expect, it, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";

/**
 * Демо-режим — первый экран человека без своих данных, и единственная часть продукта,
 * рассчитанная **на гостя**.
 *
 * 🔴 **`POST /api/demo/load` сервер отдаёт вошедшему 403 — нарочно**, чтобы демо-портрет
 * не смешался с настоящими деньгами (`routes_demo.py::load_demo`). Инвалидация кэша
 * оставлена вызывающему: он знает, какие экраны показывает, а сбрасывать весь кэш
 * отсюда значило бы стереть чужие данные ради песочницы.
 */

const listCases = vi.fn();
const loadDemo = vi.fn();

vi.mock("@shared/api/generated", () => ({
  listCasesApiDemoCasesGet: (...a: unknown[]) => listCases(...a),
  loadDemoApiDemoLoadPost: (...a: unknown[]) => loadDemo(...a),
}));

const { useDemoCases, useLoadDemoCase } = await import("./useDemoCases");

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

describe("useDemoCases", () => {
  it("отдаёт список портретов", async () => {
    listCases.mockResolvedValue({ data: { cases: [{ key: "debt-heavy" }] } });
    const { wrapper } = makeWrapper();
    const { result } = renderHook(() => useDemoCases(), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(listCases).toHaveBeenCalledWith({ throwOnError: true });
  });

  it("не запрашивается, когда экран его не показывает", async () => {
    const { wrapper } = makeWrapper();
    renderHook(() => useDemoCases(false), { wrapper });

    await new Promise((resolve) => setTimeout(resolve, 20));
    expect(listCases).not.toHaveBeenCalled();
  });
});

describe("useLoadDemoCase", () => {
  it("портрет передаётся строкой запроса, а не телом", async () => {
    loadDemo.mockResolvedValue({ data: { loaded: true } });
    const { wrapper } = makeWrapper();

    const { result } = renderHook(() => useLoadDemoCase(), { wrapper });
    result.current.mutate({ caseKey: "debt-heavy" });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(loadDemo).toHaveBeenCalledWith({
      query: { case: "debt-heavy" },
      throwOnError: true,
    });
  });

  it("🔴 кэш НЕ сбрасывается — это решение, а не упущение", async () => {
    /* Хук не знает, что показывает экран. Сбросить весь кэш отсюда значило бы
       затронуть данные, к демо-песочнице отношения не имеющие. Инвалидацию делает
       вызывающий, и мутация «добавить invalidateQueries сюда» ловится этим тестом. */
    loadDemo.mockResolvedValue({ data: { loaded: true } });
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const { result } = renderHook(() => useLoadDemoCase(), { wrapper });
    result.current.mutate({ caseKey: "debt-heavy" });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(invalidate).not.toHaveBeenCalled();
  });

  it("403 вошедшему доезжает как 403", async () => {
    /* Сервер отказывает намеренно: демо-данные не должны смешаться с настоящими.
       Экран обязан объяснить это, а не показать общее «не вышло». */
    loadDemo.mockRejectedValue({ detail: "Демо доступно только гостю.", status: 403 });
    const { wrapper } = makeWrapper();

    const { result } = renderHook(() => useLoadDemoCase(), { wrapper });
    result.current.mutate({ caseKey: "debt-heavy" });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect((result.current.error as { status?: number })?.status).toBe(403);
  });
});
