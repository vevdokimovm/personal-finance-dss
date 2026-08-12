import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { MetricsGrid } from "./MetricsGrid";
import type { PlanIndicators } from "@entities/plan-summary";

function indicators(partial: Partial<PlanIndicators>): PlanIndicators {
  return { Rt: 39500, Lt: 3, Dt: 0.2, BLR: 3.4, ...partial };
}

// Три карточки рендерятся рядом — querySelector без скоупа ловит первую
// попавшуюся (Ликвидность), не обязательно нужную. Скоупим по названию.
function cardByName(container: HTMLElement, name: string): HTMLElement {
  const card = [...container.querySelectorAll(".fp-metric-card")].find(
    (c) => c.querySelector(".fp-metric-name")?.textContent === name,
  );
  if (!card) throw new Error(`Карточка "${name}" не найдена`);
  return card as HTMLElement;
}

describe("MetricsGrid — пороговая раскраска ПДН (жёсткий инвариант канона v3.5.0, ≤0.40)", () => {
  it("Dt=0.347 (норма, anna) — без danger/warn на значении", () => {
    const { container } = render(<MetricsGrid indicators={indicators({ Dt: 0.347 })} />);
    const value = cardByName(container, "Долговая нагрузка (ПДН)").querySelector(
      ".fp-metric-value",
    );
    expect(value?.className).not.toContain("--danger");
    expect(value?.className).not.toContain("--warn");
  });

  it("Dt=0.822 (дефицит, pavel) — danger и на бейдже, и на значении", () => {
    const { container } = render(<MetricsGrid indicators={indicators({ Dt: 0.822 })} />);
    const card = cardByName(container, "Долговая нагрузка (ПДН)");
    expect(card.querySelector(".fp-metric-value")?.className).toContain("fp-metric-value--danger");
    expect(card.querySelector(".fp-metric-badge")?.className).toContain("fp-metric-badge--danger");
    expect(screen.getByText("превышен порог 40%")).toBeInTheDocument();
  });

  it("Dt=0.40 ровно на пороге — ещё не danger (строгое >, не >=, канон: инвариант Dt<=0.40)", () => {
    const { container } = render(<MetricsGrid indicators={indicators({ Dt: 0.4 })} />);
    const value = cardByName(container, "Долговая нагрузка (ПДН)").querySelector(
      ".fp-metric-value",
    );
    expect(value?.className).not.toContain("--danger");
  });

  it("Dt=0.37 (приближение к порогу) — warn (янтарный), не danger", () => {
    const { container } = render(<MetricsGrid indicators={indicators({ Dt: 0.37 })} />);
    const value = cardByName(container, "Долговая нагрузка (ПДН)").querySelector(
      ".fp-metric-value",
    );
    expect(value?.className).toContain("fp-metric-value--warn");
    expect(value?.className).not.toContain("--danger");
    expect(screen.getByText("порог 40%, близко")).toBeInTheDocument();
  });

  it("Dt=0.401 (только что превышен) — danger", () => {
    const { container } = render(<MetricsGrid indicators={indicators({ Dt: 0.401 })} />);
    const value = cardByName(container, "Долговая нагрузка (ПДН)").querySelector(
      ".fp-metric-value",
    );
    expect(value?.className).toContain("fp-metric-value--danger");
  });
});

describe("MetricsGrid — ликвидность и подушка: мягкие критерии канона, warn максимум, не danger", () => {
  // Канон v3.5.0 (docs/math_model.md): L_min=0 по умолчанию, отсев по
  // ликвидности МЯГКИЙ — в отличие от ПДН здесь нет жёсткого инварианта,
  // поэтому danger не применяется никогда, только warn ("внимание").
  it("Lt=0 (нет автономии) — warn на бейдже и значении, но не danger", () => {
    const { container } = render(<MetricsGrid indicators={indicators({ Lt: 0 })} />);
    const card = cardByName(container, "Ликвидность");
    expect(card.querySelector(".fp-metric-badge")?.className).toContain("fp-metric-badge--warn");
    expect(card.className).not.toContain("--danger");
    expect(card.querySelector(".fp-metric-value")?.className).not.toContain("--danger");
  });

  it("Lt=3 (норма) — без бейджа и без цвета на значении", () => {
    const { container } = render(<MetricsGrid indicators={indicators({ Lt: 3 })} />);
    const card = cardByName(container, "Ликвидность");
    expect(card.querySelector(".fp-metric-badge")).toBeNull();
    expect(card.querySelector(".fp-metric-value")?.className).toBe("fp-metric-value");
  });

  it("BLR=0.6 (мало) — warn-бейдж «мало», не danger", () => {
    const { container } = render(<MetricsGrid indicators={indicators({ BLR: 0.6 })} />);
    const card = cardByName(container, "Подушка со всеми накоплениями");
    expect(screen.getByText("мало")).toBeInTheDocument();
    expect(card.className).not.toContain("--danger");
  });

  it("BLR=3.4 (норма) — нейтральный бейдж «включая цели»", () => {
    render(<MetricsGrid indicators={indicators({ BLR: 3.4 })} />);
    expect(screen.getByText("включая цели")).toBeInTheDocument();
  });
});
