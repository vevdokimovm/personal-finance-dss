import { describe, expect, it, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";

/**
 * Шестой хук слоя `entities` (см. `docs/reports/testing/frontend_coverage.md`).
 *
 * 🔴 **У согласий инвалидация устроена НЕ как у остальных сущностей, и это решение,
 * а не небрежность.** Согласие на финданные открывает разом шесть роутеров
 * (`_FIN`, `app/api/router.py`), и точечная инвалидация одного списка оставила бы
 * остальные пять в устаревшем error-состоянии: человек дал согласие, а транзакции,
 * цели, активы, обязательства и уведомления продолжают показывать «Требуется согласие».
 *
 * Поэтому здесь `invalidateQueries()` **без аргументов** — сбрасывается весь кэш.
 * Согласие меняется редко, и цена полного сброса ниже цены поддерживать список ключей
 * шести сущностей, который разойдётся при добавлении седьмой.
 *
 * Тест закрепляет именно это: «оптимизация» до точечного ключа выглядит улучшением
 * и возвращает дефект, невидимый до тех пор, пока кто-то не даст согласие в живом
 * продукте и не увидит пять экранов с отказом.
 */

const getConsents = vi.fn();
const grantConsent = vi.fn();
const withdrawConsent = vi.fn();

vi.mock("@shared/api/generated", () => ({
  getConsentsApiConsentsGet: (...a: unknown[]) => getConsents(...a),
  grantApiConsentsConsentTypePost: (...a: unknown[]) => grantConsent(...a),
  withdrawApiConsentsConsentTypeDelete: (...a: unknown[]) => withdrawConsent(...a),
}));

const { useConsents, useGrantConsent, useWithdrawConsent } = await import("./useConsents");

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

describe("useConsents — чтение состояния", () => {
  it("разворачивает ответ до карты согласий", async () => {
    /* Бэкенд отдаёт `{consents: {...}}`, а потребителям нужна сама карта:
       разворот живёт в хуке, чтобы каждый экран не повторял его у себя. */
    getConsents.mockResolvedValue({
      data: { consents: { financial_data: true, marketing: false } },
    });
    const { wrapper } = makeWrapper();
    const { result } = renderHook(() => useConsents(), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual({ financial_data: true, marketing: false });
  });
});

describe("useGrantConsent / useWithdrawConsent — сбрасывают ВЕСЬ кэш", () => {
  it("выдача согласия инвалидирует всё, а не один ключ", async () => {
    /* 🔴 Главная проверка файла. `invalidateQueries()` без аргументов означает
       «перечитать всё»; вызов с `{queryKey: [...]}` оставил бы пять из шести
       сущностей в устаревшем отказе. */
    grantConsent.mockResolvedValue({ data: { granted: true } });
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const { result } = renderHook(() => useGrantConsent(), { wrapper });
    result.current.mutate("financial_data");

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(grantConsent).toHaveBeenCalledWith({
      path: { consent_type: "financial_data" },
      throwOnError: true,
    });
    expect(invalidate).toHaveBeenCalledWith();
  });

  it("отзыв тоже сбрасывает всё и возвращает тип согласия", async () => {
    /* Отзыв симметричен выдаче: шесть роутеров начинают отвечать 403, и экраны,
       оставшиеся с данными в кэше, показывали бы то, к чему доступ уже закрыт. */
    withdrawConsent.mockResolvedValue({ data: null });
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const { result } = renderHook(() => useWithdrawConsent(), { wrapper });
    result.current.mutate("financial_data");

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(withdrawConsent).toHaveBeenCalledWith({
      path: { consent_type: "financial_data" },
      throwOnError: true,
    });
    expect(result.current.data).toBe("financial_data");
    expect(invalidate).toHaveBeenCalledWith();
  });

  it("провалившаяся выдача кэш не трогает", async () => {
    grantConsent.mockRejectedValue({ detail: "Неизвестный тип согласия.", status: 422 });
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const { result } = renderHook(() => useGrantConsent(), { wrapper });
    result.current.mutate("marketing");

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(invalidate).not.toHaveBeenCalled();
  });
});
