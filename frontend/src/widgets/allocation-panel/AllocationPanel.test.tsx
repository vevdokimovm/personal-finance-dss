import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AllocationPanel } from "./AllocationPanel";
import type { PlanAlternative } from "@entities/plan-summary";

const ALT_MIXED: PlanAlternative = {
  id: "a0100",
  name: "Смешанное распределение",
  x_obligations: 10000,
  x_reserve: 20000,
  x_goals: 5000,
  utility: 0.7,
  Rt_new: 0,
  Lt_new: 1.2,
  Dt_new: 0.3,
};

const ALT_RESERVE_ONLY: PlanAlternative = {
  id: "a0200",
  name: "Всё в резерв",
  x_obligations: 0,
  x_reserve: 39500,
  x_goals: 0,
  utility: 0.8,
  Rt_new: 0,
  Lt_new: 1.2,
  Dt_new: 0.347,
};

describe("AllocationPanel — режим «подробно» (Санкей, Э5 плана вехи 8)", () => {
  it("по умолчанию диаграмма Санкея свёрнута, столбец всегда виден", () => {
    render(<AllocationPanel best={ALT_MIXED} />);
    expect(screen.getByRole("button", { name: "Подробно — диаграмма Санкея" })).toHaveAttribute(
      "aria-pressed",
      "false",
    );
    expect(screen.queryByText("Свернуть диаграмму")).not.toBeInTheDocument();
  });

  it("раскрывается по клику, кнопка меняет текст и aria-pressed", async () => {
    render(<AllocationPanel best={ALT_MIXED} />);
    const button = screen.getByRole("button", { name: "Подробно — диаграмма Санкея" });
    await userEvent.click(button);
    expect(screen.getByRole("button", { name: "Свернуть диаграмму" })).toHaveAttribute(
      "aria-pressed",
      "true",
    );
  });

  it("кнопка не использует aria-expanded/aria-controls — раскрываемый блок строго декоративен (aria-hidden), «раскрытие» для AT не происходит (находка a11y-auditor)", () => {
    render(<AllocationPanel best={ALT_MIXED} />);
    const button = screen.getByRole("button", { name: "Подробно — диаграмма Санкея" });
    expect(button).not.toHaveAttribute("aria-expanded");
    expect(button).not.toHaveAttribute("aria-controls");
  });

  it("при единственной активной категории (одна связь) переключатель не показывается — Санкей из одной линии не добавляет информации к столбцу", () => {
    render(<AllocationPanel best={ALT_RESERVE_ONLY} />);
    expect(
      screen.queryByRole("button", { name: "Подробно — диаграмма Санкея" }),
    ).not.toBeInTheDocument();
  });

  it("дефицит (best=null) — переключатель тоже не показывается", () => {
    render(<AllocationPanel best={null} />);
    expect(screen.queryByRole("button", { name: /Подробно/ })).not.toBeInTheDocument();
  });
});
