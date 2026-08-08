import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { UseQueryResult } from "@tanstack/react-query";
import { PlanningPage } from "./PlanningPage";
import type { CalculatePlanResult, ForecastResult } from "@entities/plan-summary";

const { usePlanMock, useForecastMock } = vi.hoisted(() => ({
  usePlanMock: vi.fn(),
  useForecastMock: vi.fn(),
}));

vi.mock("@entities/plan-summary", async () => {
  const actual =
    await vi.importActual<typeof import("@entities/plan-summary")>("@entities/plan-summary");
  return { ...actual, usePlan: usePlanMock, useForecast: useForecastMock };
});

function queryResult<T>(partial: Partial<UseQueryResult<T>>): UseQueryResult<T> {
  return {
    isLoading: false,
    isError: false,
    data: undefined,
    error: null,
    refetch: vi.fn(),
    ...partial,
  } as UseQueryResult<T>;
}

const PLAN_ANNA: CalculatePlanResult = {
  risk_profile: "Сбалансированный",
  indicators: { Rt: 39500, Lt: 0, Dt: 0.347, BLR: 3.4, It: 180000, Et: 78000, SigmaP: 62500 },
  top3: [{ name: "Всё в резерв", x_obligations: 0, x_reserve: 39500, x_goals: 0, utility: 0.8 }],
  admissible_count: 66,
  alternatives_total: 66,
  input_summary: {
    income: 180000,
    expense: 78000,
    bliq: 15000,
    transactions_count: 12,
    obligations_count: 1,
    goals_count: 2,
  },
};

const FORECAST_ANNA: ForecastResult = {
  current: { Bt: 265000, Rt: 39500, Lt: 0, Dt: 0.347 },
  horizon: 12,
  forecast: [{ period: 12, Rt: 813519, Rt_p10: 682866, Rt_p90: 952920 }],
};

describe("PlanningPage", () => {
  it("показывает скелетон, пока данные грузятся", () => {
    usePlanMock.mockReturnValue(queryResult({ isLoading: true }));
    useForecastMock.mockReturnValue(queryResult({ isLoading: true }));
    render(<PlanningPage />);
    expect(screen.getByText("Загрузка списка…")).toBeInTheDocument();
  });

  it("показывает состояние ошибки и повторяет запрос по клику", async () => {
    const refetchPlan = vi.fn();
    const refetchForecast = vi.fn();
    usePlanMock.mockReturnValue(queryResult({ isError: true, refetch: refetchPlan }));
    useForecastMock.mockReturnValue(queryResult({ isError: true, refetch: refetchForecast }));
    render(<PlanningPage />);
    expect(screen.getByRole("alert")).toHaveTextContent("Не получилось загрузить план");
    await userEvent.click(screen.getByRole("button", { name: "Повторить" }));
    expect(refetchPlan).toHaveBeenCalledOnce();
    expect(refetchForecast).toHaveBeenCalledOnce();
  });

  it("показывает пустое состояние для нового пользователя", () => {
    const emptyPlan: CalculatePlanResult = {
      ...PLAN_ANNA,
      input_summary: { ...PLAN_ANNA.input_summary, income: 0, expense: 0 },
    };
    usePlanMock.mockReturnValue(queryResult({ data: emptyPlan }));
    useForecastMock.mockReturnValue(queryResult({ data: FORECAST_ANNA }));
    render(<PlanningPage />);
    expect(screen.getByText("Пока нет данных для плана")).toBeInTheDocument();
  });

  it("рендерит полный план: риск-профиль, входные данные, метрики, аллокацию", () => {
    usePlanMock.mockReturnValue(queryResult({ data: PLAN_ANNA }));
    useForecastMock.mockReturnValue(queryResult({ data: FORECAST_ANNA }));
    render(<PlanningPage />);
    expect(screen.getByText("Сбалансированный")).toBeInTheDocument();
    expect(screen.getByText("15 000,00 ₽")).toBeInTheDocument(); // B_liq
    expect(screen.getByText("12 опер. · 1 обяз. · 2 целей")).toBeInTheDocument();
    expect(screen.getByText("34,7%")).toBeInTheDocument(); // MetricsGrid ПДН
    expect(screen.getByText(/Резерв — 39 500,00 ₽ \(100%\)/)).toBeInTheDocument();
  });

  it("дефицит (top3 пуст) — fail-loud сообщение вместо AllocationPanel", () => {
    const deficitPlan: CalculatePlanResult = { ...PLAN_ANNA, top3: [], admissible_count: 0 };
    usePlanMock.mockReturnValue(queryResult({ data: deficitPlan }));
    useForecastMock.mockReturnValue(queryResult({ data: FORECAST_ANNA }));
    render(<PlanningPage />);
    expect(screen.getByText("Плана распределения нет")).toBeInTheDocument();
  });
});
