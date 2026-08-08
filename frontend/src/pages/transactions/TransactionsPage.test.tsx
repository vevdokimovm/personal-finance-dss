import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { UseQueryResult } from "@tanstack/react-query";
import { TransactionsPage } from "./TransactionsPage";
import type { Transaction } from "@entities/transactions";

const { useTransactionsMock } = vi.hoisted(() => ({ useTransactionsMock: vi.fn() }));

vi.mock("@entities/transactions", async () => {
  const actual =
    await vi.importActual<typeof import("@entities/transactions")>("@entities/transactions");
  return { ...actual, useTransactions: useTransactionsMock };
});

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

  it("показывает пустое состояние без операций", () => {
    useTransactionsMock.mockReturnValue(queryResult({ data: [] }));
    render(<TransactionsPage />);
    expect(screen.getByText("Операций пока нет")).toBeInTheDocument();
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
});
