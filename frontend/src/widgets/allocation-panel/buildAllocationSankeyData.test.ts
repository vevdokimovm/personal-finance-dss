import { describe, expect, it } from "vitest";
import { buildAllocationSankeyData } from "./buildAllocationSankeyData";
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

describe("buildAllocationSankeyData", () => {
  it("три активные категории — один источник и три узла-цели с верными связями", () => {
    const data = buildAllocationSankeyData(ALT_MIXED);
    expect(data.nodes).toEqual([
      { name: "Свободные деньги" },
      { name: "Досрочное погашение", color: "var(--c-red)" },
      { name: "Резерв", color: "var(--c-amber)" },
      { name: "Цели", color: "var(--c-green)" },
    ]);
    expect(data.links).toEqual([
      { source: 0, target: 1, value: 10000 },
      { source: 0, target: 2, value: 20000 },
      { source: 0, target: 3, value: 5000 },
    ]);
  });

  it("категории с нулевой суммой не становятся узлами — только активная связь", () => {
    const data = buildAllocationSankeyData(ALT_RESERVE_ONLY);
    expect(data.nodes).toEqual([
      { name: "Свободные деньги" },
      { name: "Резерв", color: "var(--c-amber)" },
    ]);
    expect(data.links).toEqual([{ source: 0, target: 1, value: 39500 }]);
  });

  it("индекс target в links всегда указывает на реально существующий узел в nodes", () => {
    for (const alt of [ALT_MIXED, ALT_RESERVE_ONLY]) {
      const data = buildAllocationSankeyData(alt);
      for (const link of data.links) {
        expect(link.target).toBeLessThan(data.nodes.length);
        expect(link.source).toBe(0);
        expect(link.value).toBeGreaterThan(0);
      }
    }
  });
});
