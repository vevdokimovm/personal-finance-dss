import { describe, expect, it, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";

/**
 * 🔴 **Единственное место продукта, где ошибка приходит со статусом 200.**
 *
 * «Файл не распознан» — не сбой сервера, а результат работы: разбор выписки отработал
 * и ничего не нашёл. Поэтому ответ идёт `200` с полем `status: "error"`, и `throwOnError`
 * здесь **не спасает** — исключения не будет.
 *
 * Считать любой 200 успехом значит показать «импортировано» на нераспознанном файле
 * и сбросить кэш операций, плана и дашборда впустую: человек увидит те же числа
 * под надписью об успехе и решит, что импорт прошёл, а данные потерялись.
 */

const listBanks = vi.fn();
const uploadStatement = vi.fn();

vi.mock("@shared/api/generated", () => ({
  listBanksApiBanksListGet: (...a: unknown[]) => listBanks(...a),
  uploadStatementApiBanksUploadPost: (...a: unknown[]) => uploadStatement(...a),
}));

const { useBanks, useUploadStatement } = await import("./useBankImport");

function makeWrapper() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  const wrapper = ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={client}>{children}</QueryClientProvider>
  );
  return { client, wrapper };
}

const file = new File(["дата;сумма"], "statement.csv", { type: "text/csv" });

beforeEach(() => {
  vi.clearAllMocks();
});

describe("useBanks", () => {
  it("пустой список банков не роняет форму", async () => {
    listBanks.mockResolvedValue({ data: undefined });
    const { wrapper } = makeWrapper();
    const { result } = renderHook(() => useBanks(), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual([]);
  });
});

describe("useUploadStatement — 200 не означает успех", () => {
  it('🔴 при `status: "error"` кэш НЕ сбрасывается', async () => {
    /* Главная проверка файла. Мутация «инвалидировать всегда» проходит типизацию,
       выглядит проще и возвращает дефект: «импортировано» на нераспознанном файле. */
    uploadStatement.mockResolvedValue({
      data: { status: "error", message: "Формат не распознан", imported: 0 },
    });
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const { result } = renderHook(() => useUploadStatement(), { wrapper });
    result.current.mutate({ file, bankId: "tinkoff" });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    // Мутация «успешна» с точки зрения HTTP — и это ровно та ловушка.
    expect(result.current.data).toMatchObject({ status: "error" });
    expect(invalidate).not.toHaveBeenCalled();
  });

  it("при успехе сбрасывает всё, что считается от операций", async () => {
    /* Импорт добавляет операции, а от них считаются план и дашборд. Точечная
       инвалидация оставила бы экраны с устаревшими числами, и человек решил бы,
       что импорт не сработал. */
    uploadStatement.mockResolvedValue({ data: { status: "success", imported: 42 } });
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const { result } = renderHook(() => useUploadStatement(), { wrapper });
    result.current.mutate({ file, bankId: "tinkoff" });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(uploadStatement).toHaveBeenCalledWith({
      body: { file, bank_id: "tinkoff" },
      throwOnError: true,
    });
    for (const key of ["transactions", "plan", "analysis"]) {
      expect(invalidate).toHaveBeenCalledWith({ queryKey: [key] });
    }
  });
});
