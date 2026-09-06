import { describe, expect, it, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";

/**
 * Восьмой хук слоя `entities` (см. `docs/reports/testing/frontend_coverage.md`).
 *
 * 🔴 **Здесь инвалидация выходит за пределы своей сущности — и обязана.** Параметры
 * расчёта (риск-профиль, `Lmin`, ставка, горизонт) — это ВХОД модели: по ним считается
 * и план, и прогноз. Обновить один свой ключ и остановиться значит показать человеку
 * прежнюю рекомендацию после смены риск-профиля — и он решит, что настройка ни на что
 * не влияет.
 *
 * 🔴 **Инвалидируется префикс `["plan"]`, а не два ключа поимённо.** Расчёт лежит
 * в `["plan", "calculate"]`, прогноз — в `["plan", "forecast", horizon, rBench]`,
 * то есть его ключ содержит переменные части и поимённо не перечисляется вовсе.
 * Тест закрепляет именно префикс: замена на точный ключ выглядит аккуратнее
 * и оставила бы прогноз со старыми числами.
 */

const readPrefs = vi.fn();
const patchPrefs = vi.fn();

vi.mock("@shared/api/generated", () => ({
  readPrefsApiUserPrefsGet: (...a: unknown[]) => readPrefs(...a),
  patchPrefsApiUserPrefsPatch: (...a: unknown[]) => patchPrefs(...a),
}));

const { useUserPrefs, useUpdateUserPrefs } = await import("./useUserPrefs");

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

describe("useUserPrefs — чтение параметров расчёта", () => {
  it("отдаёт параметры как есть", async () => {
    readPrefs.mockResolvedValue({
      data: { risk_tolerance: 3, l_min: 50000, horizon_months: 12 },
    });
    const { wrapper } = makeWrapper();
    const { result } = renderHook(() => useUserPrefs(), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(readPrefs).toHaveBeenCalledWith({ throwOnError: true });
    expect(result.current.data).toMatchObject({ risk_tolerance: 3 });
  });
});

describe("useUpdateUserPrefs — правка входа модели пересчитывает вывод", () => {
  it("🔴 сбрасывает и сами параметры, и ВСЁ семейство ключей плана", async () => {
    patchPrefs.mockResolvedValue({ data: { risk_tolerance: 5 } });
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const { result } = renderHook(() => useUpdateUserPrefs(), { wrapper });
    result.current.mutate({ risk_tolerance: 5 });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(patchPrefs).toHaveBeenCalledWith({
      body: { risk_tolerance: 5 },
      throwOnError: true,
    });
    expect(invalidate).toHaveBeenCalledWith({ queryKey: ["user-prefs"] });
    /* Именно префикс: прогноз живёт в `["plan", "forecast", horizon, rBench]`,
       и точный ключ его не накрыл бы — экран остался бы со старым прогнозом
       под новым риск-профилем. */
    expect(invalidate).toHaveBeenCalledWith({ queryKey: ["plan"] });
  });

  it("PATCH шлёт только изменённое поле, а не весь набор", async () => {
    /* Частичное обновление — не стиль, а требование: послать весь объект значит
       перезаписать поля, которых человек не трогал, значениями из своего кэша. */
    patchPrefs.mockResolvedValue({ data: { l_min: 80000 } });
    const { wrapper } = makeWrapper();

    const { result } = renderHook(() => useUpdateUserPrefs(), { wrapper });
    result.current.mutate({ l_min: 80000 });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(patchPrefs).toHaveBeenCalledWith({
      body: { l_min: 80000 },
      throwOnError: true,
    });
  });

  it("провалившаяся правка ничего не сбрасывает", async () => {
    /* Сброс кэша плана на неудачной мутации — лишний полный пересчёт на сервере
       ради результата, который не изменился. */
    patchPrefs.mockRejectedValue({ detail: "Риск-профиль вне диапазона.", status: 422 });
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const { result } = renderHook(() => useUpdateUserPrefs(), { wrapper });
    result.current.mutate({ risk_tolerance: 99 });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(invalidate).not.toHaveBeenCalled();
  });
});
