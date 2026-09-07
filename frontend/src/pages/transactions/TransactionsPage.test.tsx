import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { UseQueryResult } from "@tanstack/react-query";
import { TransactionsPage } from "./TransactionsPage";
import type { Transaction } from "@entities/transactions";

const useTransactionsMock = vi.fn();
const createMutateAsyncMock = vi.fn();
const updateMutateAsyncMock = vi.fn();
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

// Импорт выписки — своя секция со своими запросами и тестами
// (StatementImportSection.test.tsx); здесь проверяется список операций.
vi.mock("@entities/bank-import", () => ({
  useBanks: () => ({ data: [], error: null, isLoading: false }),
  useUploadStatement: () => ({ mutate: vi.fn(), isPending: false }),
}));

vi.mock("@entities/transactions", () => ({
  useTransactions: () => useTransactionsMock(),
  useCreateTransaction: () => ({
    mutateAsync: createMutateAsyncMock,
    isPending: false,
    error: null,
  }),
  useUpdateTransaction: () => ({
    mutateAsync: updateMutateAsyncMock,
    isPending: false,
    error: null,
  }),
  useDeleteTransaction: () => ({ mutate: deleteMutateMock, isPending: false }),
  useRestoreTransaction: () => ({ mutate: restoreMutateMock, isPending: false }),
}));

function queryResult(
  partial: Partial<UseQueryResult<Transaction[]>>,
): UseQueryResult<Transaction[]> {
  return {
    isLoading: false,
    isError: false,
    data: undefined,
    error: null,
    refetch: vi.fn(),
    ...partial,
  } as UseQueryResult<Transaction[]>;
}

const TX_INCOME: Transaction = {
  id: 1,
  date: "2026-08-01",
  type: "income",
  amount: 180000,
  category: "Зарплата",
  description: null,
};

const TX_EXPENSE: Transaction = {
  id: 2,
  date: "2026-08-03",
  type: "expense",
  amount: 4500,
  category: "Продукты",
  description: "Пятёрочка",
};

describe("TransactionsPage", () => {
  it("показывает скелетон, пока данные грузятся", () => {
    useTransactionsMock.mockReturnValue(queryResult({ isLoading: true }));
    render(<TransactionsPage />);
    expect(screen.getByText("Загрузка списка…")).toBeInTheDocument();
  });

  it("показывает состояние ошибки и повторяет запрос по клику", async () => {
    const refetch = vi.fn();
    useTransactionsMock.mockReturnValue(queryResult({ isError: true, refetch }));
    render(<TransactionsPage />);
    expect(screen.getByRole("alert")).toHaveTextContent("Не получилось загрузить операции");
    await userEvent.click(screen.getByRole("button", { name: "Повторить" }));
    expect(refetch).toHaveBeenCalledOnce();
  });

  it("403 гейт согласия — показывает ConsentRequiredPanel вместо общей ошибки соединения", () => {
    useTransactionsMock.mockReturnValue(
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
    render(<TransactionsPage />);
    expect(screen.getByRole("alert")).toHaveTextContent("Нужно согласие на финансовые данные.");
    expect(screen.queryByText("Не получилось загрузить операции")).not.toBeInTheDocument();
  });

  it("показывает пустое состояние без операций, с кнопкой добавления внутри панели", () => {
    useTransactionsMock.mockReturnValue(queryResult({ data: [] }));
    render(<TransactionsPage />);
    const panel = screen.getByText("Операций пока нет").closest(".fp-state-panel") as HTMLElement;
    expect(panel).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Добавить операцию" })).toBeInTheDocument();
  });

  it("рендерит список операций — доход и расход с разным знаком/цветом", () => {
    useTransactionsMock.mockReturnValue(queryResult({ data: [TX_INCOME, TX_EXPENSE] }));
    const { container } = render(<TransactionsPage />);
    expect(screen.getByText("Зарплата")).toBeInTheDocument();
    expect(screen.getByText("Продукты")).toBeInTheDocument();
    expect(screen.getByText("Пятёрочка")).toBeInTheDocument();

    const income = container.querySelector(".fp-transaction-row__amount--income");
    const expense = container.querySelector(".fp-transaction-row__amount--expense");
    expect(income?.textContent).toContain("+");
    expect(income?.textContent).toContain("180");
    expect(expense?.textContent).toContain("−");
    expect(expense?.textContent).toContain("4");
  });

  it("кнопка «Добавить операцию» открывает форму создания (пустые поля)", async () => {
    useTransactionsMock.mockReturnValue(queryResult({ data: [TX_EXPENSE] }));
    render(<TransactionsPage />);
    await userEvent.click(screen.getByRole("button", { name: "Добавить операцию" }));
    expect(screen.getByRole("heading", { name: "Новая операция" })).toBeInTheDocument();
    expect(screen.getByLabelText("Сумма, ₽ *")).toHaveValue(null);
  });

  it("кнопка «Изменить» на строке открывает форму, поля предзаполнены", async () => {
    useTransactionsMock.mockReturnValue(queryResult({ data: [TX_EXPENSE] }));
    render(<TransactionsPage />);
    await userEvent.click(screen.getByRole("button", { name: "Изменить" }));
    expect(screen.getByRole("heading", { name: "Изменить операцию" })).toBeInTheDocument();
    expect(screen.getByLabelText("Описание (необязательно)")).toHaveValue("Пятёрочка");
  });

  it("кнопка «Удалить» вызывает мутацию удаления и переносит фокус на «Добавить операцию»", async () => {
    useTransactionsMock.mockReturnValue(queryResult({ data: [TX_EXPENSE] }));
    render(<TransactionsPage />);
    await userEvent.click(screen.getByRole("button", { name: "Удалить «Пятёрочка»" }));
    expect(deleteMutateMock).toHaveBeenCalledWith(2, expect.any(Object));
    expect(screen.getByRole("button", { name: "Добавить операцию" })).toHaveFocus();
  });
});

describe("TransactionsPage — форма правки и истёкшая сессия", () => {
  it("форма правки открывается и закрывается, не оставляя выбранную запись", async () => {
    /* `key={editing?.id ?? "new"}` пересоздаёт форму при смене записи, а `onOpenChange`
       сбрасывает `editing`: без этого следующее «Добавить» открыло бы форму с чужими
       данными, и человек сохранил бы правку не туда. */
    useTransactionsMock.mockReturnValue(queryResult({ data: [TX_EXPENSE] }));
    render(<TransactionsPage />);

    await userEvent.click(screen.getAllByRole("button", { name: /изменить|править/i })[0]);
    expect(screen.getByRole("dialog")).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: /отмена/i }));
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("🔴 истёкшая сессия ведёт ко входу, а не к «Повторить»", () => {
    /* `JWT_TTL_HOURS = 168`, refresh-токена нет — 401 в середине работы регулярен.
       «Проверьте соединение» уводит чинить интернет, который работает. */
    useTransactionsMock.mockReturnValue(
      queryResult({
        isError: true,
        error: Object.assign(new Error("401"), { status: 401 }) as unknown as Error,
      }),
    );
    render(<TransactionsPage />);

    expect(screen.getByRole("link", { name: /Войти/i })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Повторить" })).not.toBeInTheDocument();
  });
});
