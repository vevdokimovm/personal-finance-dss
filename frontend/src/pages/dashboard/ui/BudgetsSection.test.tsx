import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { UseQueryResult } from "@tanstack/react-query";
import { BudgetsSection } from "./BudgetsSection";
import type { BudgetStatus } from "@entities/budgets";

const useBudgetStatusMock = vi.fn();
const createMutateAsyncMock = vi.fn();
const restoreMutateMock = vi.fn();
// Мутация удаления реально вызывает onSuccess — иначе не проверить перенос фокуса
// (a11y-auditor, тот же паттерн, что ObligationRow, Батч 1).
const deleteMutateMock = vi.fn((_id: number, opts?: { onSuccess?: () => void }) => {
  opts?.onSuccess?.();
});

/* Выбор владельца записи (v8.55.0) — предмет своего файла тестов
   (`features/household-scope`). Настоящий компонент тянет `useHouseholds`, а с ним
   `QueryClientProvider`, во ВСЕ тесты этой страницы ради поля, к их утверждениям
   отношения не имеющего. Мокнут маркером — тот же приём, что `DemoSandbox`
   в `DashboardPage.test.tsx`. */
vi.mock("@features/household-scope", () => ({
  HouseholdScopeField: () => null,
  // Признак общей записи проверяется своим файлом тестов; здесь он маркер, чтобы
  // утверждения о строке списка не зависели от загрузки списка семей.
  SharedBadge: ({ householdId }: { householdId?: number | null }) =>
    householdId == null ? null : <span data-testid="shared-badge">Общая</span>,
}));

vi.mock("@entities/consents", () => ({
  ConsentRequiredPanel: ({ detail }: { detail: { message: string } }) => (
    <div role="alert">{detail.message}</div>
  ),
}));

vi.mock("@entities/budgets", () => ({
  useBudgetStatus: () => useBudgetStatusMock(),
  useCreateBudget: () => ({
    mutateAsync: createMutateAsyncMock,
    isPending: false,
    error: null,
  }),
  useDeleteBudget: () => ({ mutate: deleteMutateMock, isPending: false }),
  useRestoreBudget: () => ({ mutate: restoreMutateMock, isPending: false }),
}));

function queryResult(
  partial: Partial<UseQueryResult<BudgetStatus[]>>,
): UseQueryResult<BudgetStatus[]> {
  return {
    isLoading: false,
    isError: false,
    data: undefined,
    error: null,
    refetch: vi.fn(),
    ...partial,
  } as UseQueryResult<BudgetStatus[]>;
}

const BUDGET_FOOD: BudgetStatus = {
  id: 1,
  category: "Продукты",
  limit_amount: 20000,
  spent: 12340,
  pct: 61.7,
  over: false,
};

const BUDGET_OVER: BudgetStatus = {
  id: 2,
  category: "Развлечения",
  limit_amount: 5000,
  spent: 7200,
  pct: 144,
  over: true,
};

describe("BudgetsSection", () => {
  it("показывает скелетон, пока данные грузятся", () => {
    useBudgetStatusMock.mockReturnValue(queryResult({ isLoading: true }));
    render(<BudgetsSection />);
    expect(screen.getByText("Загрузка списка…")).toBeInTheDocument();
  });

  it("показывает состояние ошибки и повторяет запрос по клику", async () => {
    const refetch = vi.fn();
    useBudgetStatusMock.mockReturnValue(queryResult({ isError: true, refetch }));
    render(<BudgetsSection />);
    expect(screen.getByRole("alert")).toHaveTextContent("Не получилось загрузить бюджеты");
    await userEvent.click(screen.getByRole("button", { name: "Повторить" }));
    expect(refetch).toHaveBeenCalledOnce();
  });

  it("403 гейт согласия — показывает ConsentRequiredPanel вместо общей ошибки соединения", () => {
    useBudgetStatusMock.mockReturnValue(
      queryResult({
        isError: true,
        error: {
          detail: {
            code: "consent_required",
            consent_type: "financial_data",
            message: "Нужно согласие на финансовые данные.",
          },
        } as unknown as Error,
      }),
    );
    render(<BudgetsSection />);
    expect(screen.getByRole("alert")).toHaveTextContent("Нужно согласие на финансовые данные.");
    expect(screen.queryByText("Не получилось загрузить бюджеты")).not.toBeInTheDocument();
  });

  it("показывает пустое состояние без бюджетов, с кнопкой добавления внутри панели", () => {
    useBudgetStatusMock.mockReturnValue(queryResult({ data: [] }));
    render(<BudgetsSection />);
    const panel = screen.getByText("Бюджетов пока нет").closest(".fp-state-panel") as HTMLElement;
    expect(panel).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Добавить бюджет" })).toBeInTheDocument();
  });

  it("заголовок секции — h2, состояние пусто/ошибка — h3 (контур документа)", () => {
    useBudgetStatusMock.mockReturnValue(queryResult({ data: [] }));
    render(<BudgetsSection />);
    expect(
      screen.getByRole("heading", { level: 2, name: "Бюджеты по категориям" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { level: 3, name: "Бюджетов пока нет" }),
    ).toBeInTheDocument();
  });

  it("рендерит бюджет — категорию, потрачено, лимит, процент, без бейджа превышения", () => {
    useBudgetStatusMock.mockReturnValue(queryResult({ data: [BUDGET_FOOD] }));
    const { container } = render(<BudgetsSection />);
    expect(screen.getByText("Продукты")).toBeInTheDocument();
    expect(screen.getByText("12 340,00 ₽")).toBeInTheDocument(); // потрачено — главное число
    expect(screen.getByText("Лимит: 20 000,00 ₽")).toBeInTheDocument();
    expect(screen.getByText("61,7%")).toBeInTheDocument();
    expect(screen.queryByText("Превышен")).not.toBeInTheDocument();
    const fill = container.querySelector(".fp-budget-row__bar-fill") as HTMLElement;
    expect(fill.style.width).toBe("61.7%");
  });

  it("бюджет с превышением — бейдж «Превышен», полоса не шире 100%", () => {
    useBudgetStatusMock.mockReturnValue(queryResult({ data: [BUDGET_OVER] }));
    const { container } = render(<BudgetsSection />);
    expect(screen.getByText("Превышен")).toBeInTheDocument();
    const fill = container.querySelector(".fp-budget-row__bar-fill") as HTMLElement;
    expect(fill.style.width).toBe("100%"); // pct 144 — полоса капается на 100
    const bar = container.querySelector(".fp-budget-row__bar") as HTMLElement;
    expect(bar.dataset.over).toBe("true");
  });

  it("кнопка «Добавить бюджет» открывает форму создания (пустые поля, категория активна)", async () => {
    useBudgetStatusMock.mockReturnValue(queryResult({ data: [BUDGET_FOOD] }));
    render(<BudgetsSection />);
    await userEvent.click(screen.getByRole("button", { name: "Добавить бюджет" }));
    expect(screen.getByRole("heading", { name: "Новый бюджет" })).toBeInTheDocument();
    const categoryInput = screen.getByLabelText("Категория *");
    expect(categoryInput).toHaveValue("");
    expect(categoryInput).toBeEnabled();
  });

  it("кнопка «Изменить» открывает форму правки, категория предзаполнена и заблокирована", async () => {
    useBudgetStatusMock.mockReturnValue(queryResult({ data: [BUDGET_FOOD] }));
    render(<BudgetsSection />);
    await userEvent.click(screen.getByRole("button", { name: "Изменить" }));
    expect(screen.getByRole("heading", { name: "Изменить лимит бюджета" })).toBeInTheDocument();
    const categoryInput = screen.getByLabelText("Категория *");
    expect(categoryInput).toHaveValue("Продукты");
    expect(categoryInput).toBeDisabled();
    expect(screen.getByLabelText("Лимит в месяц, ₽ *")).toHaveValue(20000);
  });

  it("кнопка «Отмена» закрывает форму без сохранения", async () => {
    useBudgetStatusMock.mockReturnValue(queryResult({ data: [BUDGET_FOOD] }));
    render(<BudgetsSection />);
    await userEvent.click(screen.getByRole("button", { name: "Добавить бюджет" }));
    await userEvent.click(screen.getByRole("button", { name: "Отмена" }));
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    expect(createMutateAsyncMock).not.toHaveBeenCalled();
  });

  it("пустая категория не отправляет форму — видна ошибка у поля", async () => {
    useBudgetStatusMock.mockReturnValue(queryResult({ data: [BUDGET_FOOD] }));
    render(<BudgetsSection />);
    await userEvent.click(screen.getByRole("button", { name: "Добавить бюджет" }));
    await userEvent.click(screen.getByRole("button", { name: "Добавить" }));
    expect(screen.getByText("Укажите категорию.")).toBeInTheDocument();
    expect(createMutateAsyncMock).not.toHaveBeenCalled();
  });

  it("нулевой лимит не отправляет форму — видна ошибка у поля", async () => {
    useBudgetStatusMock.mockReturnValue(queryResult({ data: [BUDGET_FOOD] }));
    render(<BudgetsSection />);
    await userEvent.click(screen.getByRole("button", { name: "Добавить бюджет" }));
    await userEvent.type(screen.getByLabelText("Категория *"), "Транспорт");
    await userEvent.click(screen.getByRole("button", { name: "Добавить" }));
    expect(screen.getByText("Укажите лимит больше нуля.")).toBeInTheDocument();
    expect(createMutateAsyncMock).not.toHaveBeenCalled();
  });

  it("кнопка «Удалить» вызывает мутацию удаления и переносит фокус на «Добавить бюджет»", async () => {
    useBudgetStatusMock.mockReturnValue(queryResult({ data: [BUDGET_FOOD] }));
    render(<BudgetsSection />);
    await userEvent.click(screen.getByRole("button", { name: "Удалить «Продукты»" }));
    expect(deleteMutateMock).toHaveBeenCalledWith(1, expect.any(Object));
    expect(screen.getByRole("button", { name: "Добавить бюджет" })).toHaveFocus();
  });
});
