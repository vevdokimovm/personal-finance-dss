import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { UseQueryResult } from "@tanstack/react-query";
import { DashboardPage } from "./DashboardPage";
import type { CalculatePlanResult, ForecastResult } from "@entities/plan-summary";
import { makeForecast, makeForecastPoint } from "@shared/lib/test/forecastFixtures";

const { useProfileMock, usePlanMock, useForecastMock } = vi.hoisted(() => ({
  useProfileMock: vi.fn(),
  usePlanMock: vi.fn(),
  useForecastMock: vi.fn(),
}));

vi.mock("@entities/plan-summary", async () => {
  const actual =
    await vi.importActual<typeof import("@entities/plan-summary")>("@entities/plan-summary");
  return { ...actual, usePlan: usePlanMock, useForecast: useForecastMock };
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

/* Профиль страница спрашивает ради ОДНОГО: гость сейчас или вошедший (от этого зависит,
   показывать ли гостевую песочницу в пустом состоянии). Настоящий хук потянул бы
   QueryClientProvider во все тесты страницы ради ветки, к их утверждениям отношения
   не имеющей. По умолчанию — вошедший: гостевую ветку проверяет отдельный тест. */
vi.mock("@entities/profile", async () => {
  const actual = await vi.importActual<typeof import("@entities/profile")>("@entities/profile");
  return { ...actual, useProfile: () => useProfileMock() };
});

/* Песочница — предмет своего файла тестов (`features/demo-sandbox`). Здесь она мокнута
   маркером: проверяется только то, что страница её показывает и кому. */
vi.mock("@features/demo-sandbox", () => ({
  DemoSandbox: ({ isGuest }: { isGuest?: boolean }) =>
    isGuest ? <div data-testid="demo-sandbox">песочница</div> : null,
}));

vi.mock("@entities/consents", () => ({
  ConsentRequiredPanel: ({ detail }: { detail: { message: string } }) => (
    <div role="alert">{detail.message}</div>
  ),
}));

// BudgetsSection (Батч 3) — самостоятельный запрос, для тестов DashboardPage не относящихся
// к бюджетам достаточно фиксированного пустого состояния; собственные состояния секции
// (загрузка/ошибка/согласие/список) покрыты BudgetsSection.test.tsx отдельно.
vi.mock("@entities/budgets", () => ({
  useBudgetStatus: () => ({
    isLoading: false,
    isError: false,
    data: [],
    error: null,
    refetch: vi.fn(),
  }),
  useCreateBudget: () => ({ mutateAsync: vi.fn(), isPending: false, error: null }),
  useDeleteBudget: () => ({ mutate: vi.fn(), isPending: false }),
  useRestoreBudget: () => ({ mutate: vi.fn(), isPending: false }),
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

const PLAN_ANNA: CalculatePlanResult = {
  bliq_preallocation: {},
  weights: { w_rt: 0.3, w_lt: 0.25, w_dt: 0.25, w_goals: 0.2, lt_target: 6 },
  rejected_count: 64,
  disclaimer: "FINPILOT не является инвестиционным советником.",
  risk_profile: "Сбалансированный",
  indicators: { Rt: 39500, Lt: 0, Dt: 0.347, BLR: 3.4, It: 180000, Et: 78000, SigmaP: 62500 },
  top3: [ALT_RESERVE],
  ranked: [ALT_RESERVE],
  admissible_count: 1,
  alternatives_total: 66,
  input_summary: {
    income: 180000,
    expense: 78000,
    bliq: 0,
    transactions_count: 12,
    obligations_count: 1,
    goals_count: 0,
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

/* Профиль по умолчанию — ВОШЕДШИЙ пользователь: гостевую ветку включает тот тест,
   которому она нужна. Сбрасывается перед каждым тестом, иначе состояние протекает
   между ними — первая редакция ставила гостя через `spyOn` и оставляла его следующему
   тесту, где он ломал прямо противоположное утверждение. */
beforeEach(() => {
  useProfileMock.mockReturnValue({ data: { email: "user@test.io" }, error: null });
});

describe("DashboardPage", () => {
  it("показывает скелетон, пока данные грузятся", () => {
    usePlanMock.mockReturnValue(queryResult({ isLoading: true }));
    useForecastMock.mockReturnValue(queryResult({ isLoading: true }));
    render(<DashboardPage />);
    expect(screen.getByText("Загрузка обзора…")).toBeInTheDocument();
  });

  it("показывает состояние ошибки и повторяет запрос по клику", async () => {
    const refetchPlan = vi.fn();
    const refetchForecast = vi.fn();
    usePlanMock.mockReturnValue(queryResult({ isError: true, refetch: refetchPlan }));
    useForecastMock.mockReturnValue(queryResult({ isError: true, refetch: refetchForecast }));
    render(<DashboardPage />);
    expect(screen.getByRole("alert")).toHaveTextContent("Не получилось загрузить обзор");
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
    render(<DashboardPage />);
    expect(screen.getByRole("alert")).toHaveTextContent("Нужно согласие на финансовые данные.");
    expect(screen.queryByText("Не получилось загрузить обзор")).not.toBeInTheDocument();
  });

  it("403 гейт согласия — заголовок видимый (design-critic: панель без якоря раздела)", () => {
    // На остальных состояниях dashboard h1 sr-only корректен — они сами себя называют
    // видимым текстом («Пока нет данных для обзора» и т.п.). Панель согласия — нет
    // («Нужно согласие», «Этот раздел...») — без видимого заголовка страницы это
    // осиротевшая карточка без контекста (design-critic, батч 2026-08-19).
    const consentError = {
      detail: { code: "consent_required", consent_type: "financial_data", message: "Нужно." },
    };
    usePlanMock.mockReturnValue(
      queryResult({ isError: true, error: consentError as unknown as Error }),
    );
    useForecastMock.mockReturnValue(
      queryResult({ isError: true, error: consentError as unknown as Error }),
    );
    render(<DashboardPage />);
    const heading = screen.getByRole("heading", { level: 1, name: "Финансовый обзор" });
    expect(heading).not.toHaveClass("sr-only");
  });

  it("показывает пустое состояние, когда доход и расход равны нулю (новый пользователь)", () => {
    const emptyPlan: CalculatePlanResult = {
      ...PLAN_ANNA,
      input_summary: { ...PLAN_ANNA.input_summary, income: 0, expense: 0 },
    };
    usePlanMock.mockReturnValue(queryResult({ data: emptyPlan }));
    useForecastMock.mockReturnValue(queryResult({ data: FORECAST_ANNA }));
    render(<DashboardPage />);
    expect(screen.getByText("Пока нет данных для обзора")).toBeInTheDocument();
  });

  /* 🔴 Гипотеза H10 независимого эксперта, подтверждена чтением кода 05.09.2026.
     Пустота определялась как `income === 0 && expense === 0` — то есть человек,
     внёсший ТОЛЬКО расходы, считался «непустым». А это типичный первый заход:
     импортировал выписку, зарплата приходит на другой счёт.

     Что он получал: полноценный экран плана и рекомендацию, посчитанную при нулевом
     доходе. `ensure_calculable` отдаёт 422 только при наличии обязательств — без них
     план считается и выглядит настоящим. Совет «отложите N рублей» человеку, чей доход
     системе неизвестен, — это не пустой экран, это неверный экран, и он хуже. */
  it("только расходы без доходов — подсказка, а не план по нулевому доходу", () => {
    const expensesOnly: CalculatePlanResult = {
      ...PLAN_ANNA,
      input_summary: { ...PLAN_ANNA.input_summary, income: 0, expense: 54000 },
    };
    usePlanMock.mockReturnValue(queryResult({ data: expensesOnly }));
    useForecastMock.mockReturnValue(queryResult({ data: FORECAST_ANNA }));
    render(<DashboardPage />);

    // Заголовок панели, а не любое вхождение слова: «доход» встречается и в тексте
    // подсказки, и в подписи кнопки — getByText нашёл бы три узла и упал бы на этом.
    expect(screen.getByRole("heading", { name: /не хватает доходов/i })).toBeVisible();
    expect(screen.queryByText(/Свободные деньги/i)).not.toBeInTheDocument();
  });

  it("только доходы без расходов — та же подсказка", () => {
    /* Обратный случай реже, но столь же неверен: план по расходам, которых система
       не видит, обещает свободных денег больше, чем есть. */
    const incomeOnly: CalculatePlanResult = {
      ...PLAN_ANNA,
      input_summary: { ...PLAN_ANNA.input_summary, income: 120000, expense: 0 },
    };
    usePlanMock.mockReturnValue(queryResult({ data: incomeOnly }));
    useForecastMock.mockReturnValue(queryResult({ data: FORECAST_ANNA }));
    render(<DashboardPage />);

    expect(screen.getByRole("heading", { name: /не хватает расходов/i })).toBeVisible();
    expect(screen.queryByText(/Свободные деньги/i)).not.toBeInTheDocument();
  });

  it("рендерит реальные показатели профиля anna при успехе", () => {
    usePlanMock.mockReturnValue(queryResult({ data: PLAN_ANNA }));
    useForecastMock.mockReturnValue(queryResult({ data: FORECAST_ANNA }));
    const { container } = render(<DashboardPage />);
    expect(container.querySelector(".fp-hero-value")).toHaveTextContent("39 500,00 ₽");
    expect(screen.getByText("34,7%")).toBeInTheDocument();
    expect(screen.getByText(/Резерв — 39 500,00 ₽ \(100%\)/)).toBeInTheDocument();
  });

  it("показывает fail-loud сообщение, когда top3 пуст (дефицит, кейс mikhail)", () => {
    const deficitPlan: CalculatePlanResult = {
      ...PLAN_ANNA,
      top3: [],
      ranked: [],
      admissible_count: 0,
    };
    usePlanMock.mockReturnValue(queryResult({ data: deficitPlan }));
    useForecastMock.mockReturnValue(queryResult({ data: FORECAST_ANNA }));
    render(<DashboardPage />);
    expect(screen.getByText("Плана распределения нет")).toBeInTheDocument();
  });

  /* 🔴 Связка «гость + пустой дашборд → песочница». Без неё человек без своих данных
     видит только предложение ввести сотню операций руками, хотя продукт умеет показать
     себя на десяти готовых портретах (README: «Демо за 30 секунд»). Вход был в Jinja
     и потерялся при переносе на React — найдено в v8.45.0. */
  it("гостю с пустым дашбордом предлагает посмотреть на примере", async () => {
    const { NotAuthenticatedError } =
      await vi.importActual<typeof import("@entities/profile")>("@entities/profile");
    useProfileMock.mockReturnValue({ data: undefined, error: new NotAuthenticatedError() });

    usePlanMock.mockReturnValue({
      data: { ...PLAN_ANNA, input_summary: { ...PLAN_ANNA.input_summary, income: 0, expense: 0 } },
      isLoading: false,
      isError: false,
    });
    render(<DashboardPage />);
    expect(screen.getByTestId("demo-sandbox")).toBeVisible();
  });

  /* Вошедшему песочница не нужна и вредна: сервер отдаёт ей 403, чтобы демо-данные
     не смешались с настоящими. */
  it("вошедшему с пустым дашбордом песочница не показывается", () => {
    usePlanMock.mockReturnValue({
      data: { ...PLAN_ANNA, input_summary: { ...PLAN_ANNA.input_summary, income: 0, expense: 0 } },
      isLoading: false,
      isError: false,
    });
    render(<DashboardPage />);
    expect(screen.queryByTestId("demo-sandbox")).not.toBeInTheDocument();
  });
});
