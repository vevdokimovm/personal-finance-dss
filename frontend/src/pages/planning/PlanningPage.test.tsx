import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { UseQueryResult } from "@tanstack/react-query";
import { PlanningPage } from "./PlanningPage";
import type { CalculatePlanResult, ForecastResult } from "@entities/plan-summary";
import { makeForecast, makeForecastPoint } from "@shared/lib/test/forecastFixtures";

const { usePlanMock, useForecastMock } = vi.hoisted(() => ({
  usePlanMock: vi.fn(),
  useForecastMock: vi.fn(),
}));

// Панель параметров расчёта — свой запрос и свои тесты (PlanSettingsSection.test.tsx);
// здесь проверяется сам план.
vi.mock("@entities/user-prefs", () => ({
  useUserPrefs: () => ({ data: undefined, error: null, isLoading: false, refetch: vi.fn() }),
  useUpdateUserPrefs: () => ({ mutate: vi.fn(), isPending: false }),
}));

vi.mock("@entities/plan-summary", async () => {
  const actual =
    await vi.importActual<typeof import("@entities/plan-summary")>("@entities/plan-summary");
  return {
    ...actual,
    usePlan: usePlanMock,
    useForecast: useForecastMock,
    // Ключевая ставка — запрос панели параметров; здесь проверяется сам план, и живой
    // хук ушёл бы в сеть без QueryClient.
    useKeyRate: () => ({ data: undefined }),
  };
});

vi.mock("@tanstack/react-router", async () => {
  // Экран получил <Link> вместо сырого <a href> (H13, v8.31.0). Настоящий Link требует
  // контекст роутера, которого в юнит-тесте страницы нет и быть не должно: сюда он попал
  // как деталь вёрстки CTA, а не как предмет проверки. Мок отдаёт <a href> — ровно то,
  // на что тесты и смотрели раньше, поэтому их утверждения не менялись.
  const actual =
    await vi.importActual<typeof import("@tanstack/react-router")>("@tanstack/react-router");
  return {
    ...actual,
    Link: ({ to, children, ...rest }: { to: string; children: React.ReactNode }) => (
      <a href={to} {...rest}>
        {children}
      </a>
    ),
  };
});

// PlanHistorySection (v8.34.0) — самостоятельный запрос истории; для тестов
// PlanningPage, не относящихся к истории, достаточно фиксированного пустого состояния.
// Собственные состояния секции (загрузка/ошибка/согласие/список/удаление) покрыты
// PlanHistorySection.test.tsx отдельно — тот же приём, что с BudgetsSection на дашборде.
// PlanExportSection (v8.35.0) — своё состояние скачивания и своя панель согласия;
// для тестов PlanningPage достаточно заглушки, поведение секции покрыто отдельно.
vi.mock("./ui/PlanExportSection", () => ({
  PlanExportSection: () => <section aria-label="Выгрузить план" />,
}));

vi.mock("@entities/plan-history", () => ({
  usePlanHistory: () => ({
    data: { items: [], count: 0 },
    error: null,
    isLoading: false,
    refetch: vi.fn(),
  }),
  useSavePlanSnapshot: () => ({ mutate: vi.fn(), isPending: false }),
  useDeletePlanSnapshot: () => ({ mutate: vi.fn(), isPending: false }),
  useRestorePlanSnapshot: () => ({ mutate: vi.fn(), isPending: false }),
}));

vi.mock("@entities/consents", () => ({
  ConsentRequiredPanel: ({ detail }: { detail: { message: string } }) => (
    <div role="alert">{detail.message}</div>
  ),
}));

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

const ALT_RESERVE = {
  id: "a0100",
  name: "Всё в резерв",
  x_obligations: 0,
  x_reserve: 39500,
  x_goals: 0,
  utility: 0.8,
  Rt_new: 0,
  Lt_new: 1.2,
  Dt_new: 0.347,
  is_recommended: true,
};
const ALT_DEBT = {
  id: "a1000",
  name: "Всё на погашение долга",
  x_obligations: 39500,
  x_reserve: 0,
  x_goals: 0,
  utility: 0.62,
  Rt_new: 0,
  Lt_new: 0.2,
  Dt_new: 0.28,
};

const PLAN_ANNA: CalculatePlanResult = {
  bliq_preallocation: {},
  weights: { w_rt: 0.3, w_lt: 0.25, w_dt: 0.25, w_goals: 0.2, lt_target: 6 },
  rejected_count: 64,
  disclaimer: "FINPILOT не является инвестиционным советником.",
  risk_profile: "Сбалансированный",
  indicators: { Rt: 39500, Lt: 0, Dt: 0.347, BLR: 3.4, It: 180000, Et: 78000, SigmaP: 62500 },
  top3: [ALT_RESERVE],
  ranked: [ALT_RESERVE, ALT_DEBT],
  admissible_count: 2,
  alternatives_total: 66,
  input_summary: {
    income: 180000,
    expense: 78000,
    bliq: 15000,
    transactions_count: 12,
    obligations_count: 1,
    goals_count: 2,
    liquid_assets_count: 2,
    r_bench: 0.16,
    r_bench_source: "key_rate",
    l_min: 3,
    risk_tolerance: 3,
  },
};

const FORECAST_ANNA: ForecastResult = makeForecast({
  current: { Bt: 265000, Rt: 39500, Lt: 0, Dt: 0.347 },
  horizon: 12,
  forecast: [makeForecastPoint({ period: 12, Rt: 813519, Rt_p10: 682866, Rt_p90: 952920 })],
  r_bench: 0.139,
  real_r_bench: 0.139,
  r_bench_source: "cbr_keyrate_post_tax",
});

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

  it("403 гейт согласия — показывает ConsentRequiredPanel вместо общей ошибки соединения", () => {
    const consentError = {
      detail: {
        code: "consent_required",
        consent_type: "financial_data",
        message: "Нужно согласие на финансовые данные.",
      },
    };
    usePlanMock.mockReturnValue(
      queryResult({ isError: true, error: consentError as unknown as Error }),
    );
    useForecastMock.mockReturnValue(
      queryResult({ isError: true, error: consentError as unknown as Error }),
    );
    render(<PlanningPage />);
    expect(screen.getByRole("alert")).toHaveTextContent("Нужно согласие на финансовые данные.");
    expect(screen.queryByText("Не получилось загрузить план")).not.toBeInTheDocument();
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
    const deficitPlan: CalculatePlanResult = {
      ...PLAN_ANNA,
      top3: [],
      ranked: [],
      admissible_count: 0,
    };
    usePlanMock.mockReturnValue(queryResult({ data: deficitPlan }));
    useForecastMock.mockReturnValue(queryResult({ data: FORECAST_ANNA }));
    render(<PlanningPage />);
    expect(screen.getByText("Плана распределения нет")).toBeInTheDocument();
  });

  it("дефицит — браузер альтернатив не рендерится (ranked пуст)", () => {
    const deficitPlan: CalculatePlanResult = {
      ...PLAN_ANNA,
      top3: [],
      ranked: [],
      admissible_count: 0,
    };
    usePlanMock.mockReturnValue(queryResult({ data: deficitPlan }));
    useForecastMock.mockReturnValue(queryResult({ data: FORECAST_ANNA }));
    render(<PlanningPage />);
    expect(screen.queryByText("Все варианты распределения")).not.toBeInTheDocument();
  });

  it("браузер альтернатив свёрнут по умолчанию, разворачивается по клику", async () => {
    usePlanMock.mockReturnValue(queryResult({ data: PLAN_ANNA }));
    useForecastMock.mockReturnValue(queryResult({ data: FORECAST_ANNA }));
    render(<PlanningPage />);
    expect(screen.queryByText("Всё на погашение долга")).not.toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Показать все (2)" }));
    expect(screen.getByText("Всё на погашение долга")).toBeInTheDocument();
    expect(screen.getByText("рекомендовано")).toBeInTheDocument();
  });

  it("браузер альтернатив пересортировывает список по выбранному критерию", async () => {
    usePlanMock.mockReturnValue(queryResult({ data: PLAN_ANNA }));
    useForecastMock.mockReturnValue(queryResult({ data: FORECAST_ANNA }));
    render(<PlanningPage />);
    await userEvent.click(screen.getByRole("button", { name: "Показать все (2)" }));

    const names = () =>
      screen
        .getAllByRole("listitem")
        .map((li) => li.querySelector(".fp-alt-row__name")?.firstChild?.textContent);
    expect(names()).toEqual(["Всё в резерв", "Всё на погашение долга"]);

    await userEvent.selectOptions(
      screen.getByLabelText("Сортировать по"),
      "Долговой нагрузке (ПДН)",
    );
    // ALT_DEBT.Dt_new=0.28 < ALT_RESERVE.Dt_new=0.347 — при сортировке по ПДН (по возрастанию)
    // долговой вариант уходит первым.
    expect(names()).toEqual(["Всё на погашение долга", "Всё в резерв"]);
  });
  /* 🔴 Требование L5: дисклеймер 39-ФЗ выводится НА САМОЙ странице рекомендаций, а не
     только в оферте — человек принимает решение о деньгах здесь. Текст берётся из поля
     ответа: перепечатанный во фронте разошёлся бы с каноном при первой правке. */
  it("дисклеймер 39-ФЗ показан на экране плана и взят из ответа (L5)", () => {
    render(<PlanningPage />);
    expect(screen.getByText(PLAN_ANNA.disclaimer)).toBeVisible();
  });

  it("дисклеймер стоит ДО распределения, а не в подвале страницы", () => {
    const { container } = render(<PlanningPage />);
    const disclaimer = container.querySelector(".fp-planning__disclaimer");
    const allocation = screen.getByRole("heading", { name: "Куда пойдут свободные деньги" });
    expect(disclaimer).not.toBeNull();
    // Порядок в DOM: предупреждение, до которого надо доскроллить, требования не
    // выполняет — оно должно попасться раньше рекомендации.
    expect(
      disclaimer!.compareDocumentPosition(allocation!) & Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBeTruthy();
  });
});
