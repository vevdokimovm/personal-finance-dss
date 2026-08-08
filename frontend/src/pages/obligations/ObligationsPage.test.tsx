import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { UseQueryResult } from "@tanstack/react-query";
import { ObligationsPage } from "./ObligationsPage";
import type { Obligation } from "@entities/obligations";

const { useObligationsMock } = vi.hoisted(() => ({ useObligationsMock: vi.fn() }));

vi.mock("@entities/obligations", async () => {
  const actual =
    await vi.importActual<typeof import("@entities/obligations")>("@entities/obligations");
  return { ...actual, useObligations: useObligationsMock };
});

function queryResult(partial: Partial<UseQueryResult<Obligation[]>>): UseQueryResult<Obligation[]> {
  return {
    isLoading: false,
    isError: false,
    data: undefined,
    error: null,
    refetch: vi.fn(),
    ...partial,
  } as UseQueryResult<Obligation[]>;
}

const OBLIGATION: Obligation = {
  id: 1,
  name: "Ипотека",
  type: "mortgage",
  amount: 5000000,
  interest_rate: 0.078,
  monthly_payment: 45000,
  months_elapsed: 24,
  months_remaining: 96,
  payment_day: 5,
  term: 120,
};

describe("ObligationsPage", () => {
  it("показывает скелетон, пока данные грузятся", () => {
    useObligationsMock.mockReturnValue(queryResult({ isLoading: true }));
    render(<ObligationsPage />);
    expect(screen.getByText("Загрузка списка…")).toBeInTheDocument();
  });

  it("показывает состояние ошибки и повторяет запрос по клику", async () => {
    const refetch = vi.fn();
    useObligationsMock.mockReturnValue(queryResult({ isError: true, refetch }));
    render(<ObligationsPage />);
    expect(screen.getByRole("alert")).toHaveTextContent("Не получилось загрузить обязательства");
    await userEvent.click(screen.getByRole("button", { name: "Повторить" }));
    expect(refetch).toHaveBeenCalledOnce();
  });

  it("показывает пустое состояние без обязательств", () => {
    useObligationsMock.mockReturnValue(queryResult({ data: [] }));
    render(<ObligationsPage />);
    expect(screen.getByText("Обязательств нет")).toBeInTheDocument();
  });

  it("рендерит обязательство — платёж, ставку, прогресс срока", () => {
    useObligationsMock.mockReturnValue(queryResult({ data: [OBLIGATION] }));
    const { container } = render(<ObligationsPage />);
    expect(screen.getByText("Ипотека")).toBeInTheDocument();
    expect(screen.getByText("7,8%")).toBeInTheDocument();
    expect(screen.getByText("24 из 120 мес.")).toBeInTheDocument();
    const fill = container.querySelector(".fp-obligation-row__bar-fill") as HTMLElement;
    expect(fill.style.width).toBe("20%"); // 24/120
  });
});
