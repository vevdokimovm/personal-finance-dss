import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { UseQueryResult } from "@tanstack/react-query";
import { GoalsPage } from "./GoalsPage";
import type { Goal } from "@entities/goals";

const { useGoalsMock } = vi.hoisted(() => ({ useGoalsMock: vi.fn() }));

vi.mock("@entities/goals", async () => {
  const actual = await vi.importActual<typeof import("@entities/goals")>("@entities/goals");
  return { ...actual, useGoals: useGoalsMock };
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
  category: "reserve",
  target_amount: 500000,
  current_amount: 125000,
  deadline: "2027-01-01",
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

  it("показывает пустое состояние без целей", () => {
    useGoalsMock.mockReturnValue(queryResult({ data: [] }));
    render(<GoalsPage />);
    expect(screen.getByText("Целей пока нет")).toBeInTheDocument();
  });

  it("рендерит цель с прогресс-баром (25%)", () => {
    useGoalsMock.mockReturnValue(queryResult({ data: [GOAL] }));
    render(<GoalsPage />);
    expect(screen.getByText("Подушка безопасности")).toBeInTheDocument();
    const bar = screen.getByRole("progressbar", { name: /Подушка безопасности/ });
    expect(bar).toHaveAttribute("aria-valuenow", "25");
  });
});
