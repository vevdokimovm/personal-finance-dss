import { describe, expect, it } from "vitest";
import { render } from "@testing-library/react";
import { ZoneScale } from "./ZoneScale";

describe("ZoneScale — визуальная шкала с зонами (план вехи 8, Э5)", () => {
  it("декоративна — aria-hidden, число уже доступно текстом рядом (badge/value в MetricCard)", () => {
    const { container } = render(
      <ZoneScale value={2} max={6} zones={[{ to: 6, variant: "muted" }]} />,
    );
    expect(container.querySelector(".fp-zone-scale")).toHaveAttribute("aria-hidden", "true");
  });

  it("зоны делят дорожку пропорционально диапазону (0-1 warn, 1-6 muted при max=6)", () => {
    const { container } = render(
      <ZoneScale
        value={2}
        max={6}
        zones={[
          { to: 1, variant: "warn" },
          { to: 6, variant: "muted" },
        ]}
      />,
    );
    const zones = container.querySelectorAll(".fp-zone-scale__zone");
    expect(zones).toHaveLength(2);
    expect(zones[0]).toHaveClass("fp-zone-scale__zone--warn");
    expect((zones[0] as HTMLElement).style.width).toBe(`${(1 / 6) * 100}%`);
    expect(zones[1]).toHaveClass("fp-zone-scale__zone--muted");
    expect((zones[1] as HTMLElement).style.width).toBe(`${((6 - 1) / 6) * 100}%`);
  });

  it("маркер стоит на позиции value/max, не на границе зоны", () => {
    const { container } = render(
      <ZoneScale value={3} max={6} zones={[{ to: 6, variant: "muted" }]} />,
    );
    const marker = container.querySelector(".fp-zone-scale__marker") as HTMLElement;
    expect(marker.style.left).toBe("50%");
  });

  it("значение за пределами max — маркер прижимается к правому краю, не вылезает за 100%", () => {
    const { container } = render(
      <ZoneScale value={0.9} max={0.6} zones={[{ to: 0.6, variant: "danger" }]} />,
    );
    const marker = container.querySelector(".fp-zone-scale__marker") as HTMLElement;
    expect(marker.style.left).toBe("100%");
  });

  it("отрицательное значение — маркер прижимается к левому краю, не уходит в минус", () => {
    const { container } = render(
      <ZoneScale value={-1} max={6} zones={[{ to: 6, variant: "muted" }]} />,
    );
    const marker = container.querySelector(".fp-zone-scale__marker") as HTMLElement;
    expect(marker.style.left).toBe("0%");
  });
});
