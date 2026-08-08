import { describe, expect, it } from "vitest";
import { render } from "@testing-library/react";
import { DashboardSkeleton } from "./DashboardSkeleton";

describe("DashboardSkeleton", () => {
  it("резервирует место под AllocationPanel и ForecastPanel — 2 секции .fp-panel", () => {
    // Регресс-тест P1-4: skeleton раньше мокал только Hero+MetricsGrid, и при
    // loading -> loaded страница "прыгала" вниз на высоту двух панелей ниже.
    // Реальный DashboardPage при успехе рендерит ровно 2 .fp-panel
    // (AllocationPanel, ForecastPanel) — skeleton обязан резервировать столько же.
    const { container } = render(<DashboardSkeleton />);
    const panels = container.querySelectorAll(".fp-panel");
    expect(panels).toHaveLength(2);
  });

  it("оба заглушечных .fp-panel помечены aria-hidden (декоративные, как остальной skeleton)", () => {
    const { container } = render(<DashboardSkeleton />);
    const panels = container.querySelectorAll(".fp-panel");
    panels.forEach((panel) => expect(panel).toHaveAttribute("aria-hidden", "true"));
  });

  it("статус загрузки по-прежнему объявлен для скринридера", () => {
    const { getByText } = render(<DashboardSkeleton />);
    expect(getByText("Загрузка обзора…")).toBeInTheDocument();
  });
});
