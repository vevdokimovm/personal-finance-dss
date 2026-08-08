import type { ReactElement, ReactNode } from "react";
import { describe, expect, it } from "vitest";
import { Area } from "recharts";
import { ForecastPanel } from "./ForecastPanel";
import { buildForecastChartData } from "./buildForecastChartData";
import type { ForecastResult } from "@entities/plan-summary";

// Recharts НЕ рендерит <Area> как обычный React-компонент в DOM — AreaChart
// читает children через Children.map чисто для чтения props и рисует SVG
// сама, минуя обычный рендер. Поэтому мокать Area бесполезно (мок никогда
// не вызывается) и проверять пиксели в jsdom без ResizeObserver нестабильно.
// ForecastPanel — чистая функция без хуков: вызываем её напрямую и обходим
// возвращённое дерево React-элементов, находя реальные <Area> по type.
interface AreaLikeProps {
  children?: ReactNode;
  stackId?: string;
  fill?: string;
}

function findElementsByType(
  node: ReactNode,
  type: unknown,
  out: ReactElement<AreaLikeProps>[] = [],
): ReactElement<AreaLikeProps>[] {
  if (node == null || typeof node !== "object") return out;
  if (Array.isArray(node)) {
    node.forEach((n) => findElementsByType(n, type, out));
    return out;
  }
  const el = node as ReactElement<AreaLikeProps>;
  if (el.type === type) out.push(el);
  if (el.props?.children) {
    findElementsByType(el.props.children, type, out);
  }
  return out;
}

const FORECAST_ANNA: ForecastResult = {
  current: { Bt: 265000, Rt: 39500, Lt: 0, Dt: 0.347 },
  horizon: 12,
  forecast: [
    { period: 6, Rt: 400000, Rt_p10: 350000, Rt_p90: 450000 },
    { period: 12, Rt: 813519, Rt_p10: 682866, Rt_p90: 952920 },
  ],
};

// pavel — дефицит: p10/p90 ОБА отрицательные. Старый баг (Area без stackId,
// fill=var(--c-bg)) на этом фикстуре случайно не проявлялся визуально —
// проверка нужна именно на нём, не только на положительном anna.
const FORECAST_PAVEL: ForecastResult = {
  current: { Bt: 50000, Rt: -63000, Lt: 0, Dt: 0.822 },
  horizon: 12,
  forecast: [
    { period: 6, Rt: -350000, Rt_p10: -450000, Rt_p90: -280000 },
    { period: 12, Rt: -709583, Rt_p10: -823544, Rt_p90: -587992 },
  ],
};

describe("buildForecastChartData", () => {
  it.each([
    ["anna (положительный домен)", FORECAST_ANNA],
    ["pavel (отрицательный домен, дефицит)", FORECAST_PAVEL],
  ])("Rt_p10 + Rt_band === Rt_p90 на каждой точке — %s", (_label, forecast) => {
    const data = buildForecastChartData(forecast);
    expect(data.length).toBeGreaterThan(0);
    for (const point of data) {
      expect(point.Rt_p10 + point.Rt_band).toBeCloseTo(point.Rt_p90, 6);
    }
  });

  it("Rt_band неотрицателен (p90 >= p10 всегда, по определению интервала)", () => {
    for (const forecast of [FORECAST_ANNA, FORECAST_PAVEL]) {
      for (const point of buildForecastChartData(forecast)) {
        expect(point.Rt_band).toBeGreaterThanOrEqual(0);
      }
    }
  });
});

describe("ForecastPanel — конфигурация полосы p10-p90", () => {
  it.each([
    ["anna", FORECAST_ANNA],
    ["pavel (дефицит)", FORECAST_PAVEL],
  ])(
    "два Area делят один stackId, ни один не красит фигуру цветом фона — %s",
    (_label, forecast) => {
      const tree = ForecastPanel({ forecast });
      const areas = findElementsByType(tree, Area);

      expect(areas).toHaveLength(2);
      const stackIds = new Set(areas.map((a) => a.props.stackId));
      expect(stackIds.size).toBe(1);
      expect([...stackIds][0]).toBeTruthy();

      // Регресс-инвариант: ни у одной Area заливка не завязана на цвет фона
      // страницы/панели — старый баг держался ровно на этом совпадении цветов.
      for (const area of areas) {
        expect(area.props.fill).not.toBe("var(--c-bg)");
        expect(area.props.fill).not.toBe("var(--c-surface)");
      }
      // Ровно одна невидимая база и одна видимая полоса.
      const fills = areas.map((a) => a.props.fill).sort();
      expect(fills).toEqual(["none", "var(--c-accent-bg)"]);
    },
  );
});
