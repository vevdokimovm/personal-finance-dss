import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { UseQueryResult } from "@tanstack/react-query";
import { GoalsPage } from "./GoalsPage";
import type { Goal } from "@entities/goals";

const useGoalsMock = vi.fn();
const createMutateAsyncMock = vi.fn();
const updateMutateAsyncMock = vi.fn();
const contributeMutateAsyncMock = vi.fn();
const restoreMutateMock = vi.fn();
// Мутация удаления реально вызывает onSuccess — иначе не проверить перенос фокуса
// (a11y-auditor, Батч 1: без этого фокус после удаления строки падает в <body>).
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

/* Панель истёкшей сессии — предмет своего файла тестов (`entities/auth`).
   Настоящая тянет `Link` из роутера, а с ним провайдер. `isSessionExpired`
   при этом НЕ мокается: именно она решает, какую ветку показать. */
vi.mock("@entities/auth", async () => {
  const actual = await vi.importActual<typeof import("@entities/auth")>("@entities/auth");
  return {
    ...actual,
    SessionExpiredPanel: () => <a href="/login">Войти заново</a>,
  };
});

vi.mock("@entities/consents", () => ({
  ConsentRequiredPanel: ({ detail }: { detail: { message: string } }) => (
    <div role="alert">{detail.message}</div>
  ),
}));

vi.mock("@entities/assets", () => ({
  useLiquidAssets: () => ({ data: [], isLoading: false, isError: false }),
}));

vi.mock("@entities/goals", async () => {
  const actual = await vi.importActual<typeof import("@entities/goals")>("@entities/goals");
  return {
    GOAL_CATEGORY_OPTIONS: actual.GOAL_CATEGORY_OPTIONS,
    GOAL_CATEGORY_LABEL: actual.GOAL_CATEGORY_LABEL,
    useGoals: () => useGoalsMock(),
    useCreateGoal: () => ({ mutateAsync: createMutateAsyncMock, isPending: false, error: null }),
    useUpdateGoal: () => ({ mutateAsync: updateMutateAsyncMock, isPending: false, error: null }),
    useAddGoalContribution: () => ({
      mutateAsync: contributeMutateAsyncMock,
      isPending: false,
      error: null,
    }),
    useDeleteGoal: () => ({ mutate: deleteMutateMock, isPending: false }),
    useRestoreGoal: () => ({ mutate: restoreMutateMock, isPending: false }),
  };
});

function queryResult(partial: Partial<UseQueryResult<Goal[]>>): UseQueryResult<Goal[]> {
  return {
    isLoading: false,
    isError: false,
    data: undefined,
    error: null,
    refetch: vi.fn(),
    ...partial,
  } as UseQueryResult<Goal[]>;
}

const GOAL: Goal = {
  id: 1,
  name: "Подушка безопасности",
  category: "safety",
  target_amount: 500000,
  current_amount: 125000,
  deadline: "2027-01-01",
  linked_asset_id: null,
};

const LINKED_GOAL: Goal = {
  ...GOAL,
  id: 2,
  name: "Отпуск (со вклада)",
  linked_asset_id: 7,
};

describe("GoalsPage", () => {
  it("показывает скелетон, пока данные грузятся", () => {
    useGoalsMock.mockReturnValue(queryResult({ isLoading: true }));
    render(<GoalsPage />);
    expect(screen.getByText("Загрузка списка…")).toBeInTheDocument();
  });

  it("показывает состояние ошибки и повторяет запрос по клику", async () => {
    const refetch = vi.fn();
    useGoalsMock.mockReturnValue(queryResult({ isError: true, refetch }));
    render(<GoalsPage />);
    expect(screen.getByRole("alert")).toHaveTextContent("Не получилось загрузить цели");
    await userEvent.click(screen.getByRole("button", { name: "Повторить" }));
    expect(refetch).toHaveBeenCalledOnce();
  });

  it("403 гейт согласия — показывает ConsentRequiredPanel вместо общей ошибки соединения", () => {
    useGoalsMock.mockReturnValue(
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
    render(<GoalsPage />);
    expect(screen.getByRole("alert")).toHaveTextContent("Нужно согласие на финансовые данные.");
    expect(screen.queryByText("Не получилось загрузить цели")).not.toBeInTheDocument();
  });

  it("показывает пустое состояние без целей, с кнопкой добавления внутри панели", () => {
    useGoalsMock.mockReturnValue(queryResult({ data: [] }));
    render(<GoalsPage />);
    const panel = screen.getByText("Целей пока нет").closest(".fp-state-panel") as HTMLElement;
    expect(panel).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Добавить цель" })).toBeInTheDocument();
  });

  it("рендерит цель с прогресс-баром (25%)", () => {
    useGoalsMock.mockReturnValue(queryResult({ data: [GOAL] }));
    render(<GoalsPage />);
    expect(screen.getByText("Подушка безопасности")).toBeInTheDocument();
    const bar = screen.getByRole("progressbar", { name: /Подушка безопасности/ });
    expect(bar).toHaveAttribute("aria-valuenow", "25");
  });

  it("кнопка «Добавить цель» открывает форму создания (пустые поля)", async () => {
    useGoalsMock.mockReturnValue(queryResult({ data: [GOAL] }));
    render(<GoalsPage />);
    await userEvent.click(screen.getByRole("button", { name: "Добавить цель" }));
    expect(screen.getByRole("heading", { name: "Новая цель" })).toBeInTheDocument();
    expect(screen.getByLabelText("Название *")).toHaveValue("");
  });

  it("кнопка «Изменить» открывает форму, поля предзаполнены (без current_amount)", async () => {
    useGoalsMock.mockReturnValue(queryResult({ data: [GOAL] }));
    render(<GoalsPage />);
    await userEvent.click(screen.getByRole("button", { name: "Изменить" }));
    expect(screen.getByRole("heading", { name: "Изменить цель" })).toBeInTheDocument();
    expect(screen.getByLabelText("Название *")).toHaveValue("Подушка безопасности");
    expect(screen.queryByLabelText(/current_amount/)).not.toBeInTheDocument();
  });

  it("кнопка «Внести прогресс» открывает форму с одним полем «сумма»", async () => {
    useGoalsMock.mockReturnValue(queryResult({ data: [GOAL] }));
    render(<GoalsPage />);
    await userEvent.click(screen.getByRole("button", { name: "Внести прогресс" }));
    expect(screen.getByRole("heading", { name: "Внести прогресс" })).toBeInTheDocument();
    await userEvent.type(screen.getByLabelText("Сумма, ₽ *"), "5000");
    await userEvent.click(screen.getByRole("button", { name: "Внести" }));
    expect(contributeMutateAsyncMock).toHaveBeenCalledWith({
      id: 1,
      body: { amount: 5000 },
    });
  });

  it("для цели с linked_asset_id нет кнопки «Внести прогресс» — есть пояснение", () => {
    useGoalsMock.mockReturnValue(queryResult({ data: [LINKED_GOAL] }));
    render(<GoalsPage />);
    expect(screen.queryByRole("button", { name: "Внести прогресс" })).not.toBeInTheDocument();
    expect(
      screen.getByText("Прогресс выводится из баланса привязанного актива."),
    ).toBeInTheDocument();
  });

  it("кнопка «Удалить» вызывает мутацию удаления и переносит фокус на «Добавить цель»", async () => {
    useGoalsMock.mockReturnValue(queryResult({ data: [GOAL] }));
    render(<GoalsPage />);
    await userEvent.click(screen.getByRole("button", { name: "Удалить «Подушка безопасности»" }));
    expect(deleteMutateMock).toHaveBeenCalledWith(1, expect.any(Object));
    expect(screen.getByRole("button", { name: "Добавить цель" })).toHaveFocus();
  });
});

describe("GoalsPage — форма правки и истёкшая сессия", () => {
  it("форма правки открывается и закрывается, не оставляя выбранную запись", async () => {
    /* `key={editing?.id ?? "new"}` пересоздаёт форму при смене записи, а `onOpenChange`
       сбрасывает `editing`: без этого следующее «Добавить» открыло бы форму с чужими
       данными, и человек сохранил бы правку не туда. */
    useGoalsMock.mockReturnValue(queryResult({ data: [GOAL] }));
    render(<GoalsPage />);

    await userEvent.click(screen.getAllByRole("button", { name: /изменить|править/i })[0]);
    expect(screen.getByRole("dialog")).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: /отмена/i }));
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("🔴 истёкшая сессия ведёт ко входу, а не к «Повторить»", () => {
    /* `JWT_TTL_HOURS = 168`, refresh-токена нет — 401 в середине работы регулярен.
       «Проверьте соединение» уводит чинить интернет, который работает. */
    useGoalsMock.mockReturnValue(
      queryResult({
        isError: true,
        error: Object.assign(new Error("401"), { status: 401 }) as unknown as Error,
      }),
    );
    render(<GoalsPage />);

    expect(screen.getByRole("link", { name: /Войти/i })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Повторить" })).not.toBeInTheDocument();
  });
});
