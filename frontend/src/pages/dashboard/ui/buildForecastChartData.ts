import type { ForecastResult } from "@entities/plan-summary";

export interface ForecastChartPoint {
  period: number;
  Rt: number;
  Rt_p10: number;
  Rt_p90: number;
  /** p90-p10, дельта для верхнего стекированного Area (сама полоса). */
  Rt_band: number;
}

/** Полоса p10-p90 рисуется ДВУМЯ стекированными Area с общим stackId:
 * невидимая база (Rt_p10, fill="none") + видимая дельта (Rt_band = p90-p10)
 * поверх неё. Recharts стек — чистое накопление по порядку рядов, без
 * разделения по знаку, поэтому это корректно и на отрицательном домене
 * (дефицит, Rt_p10/p90 < 0), и на положительном — в отличие от прежней
 * техники «второй Area цветом фона поверх» (без stackId рисовала фигуру от
 * нуля, а не от p10, и держалась на случайном совпадении --c-bg с фоном
 * панели: в тёмной теме заливала весь график сплошным цветом). Отдельный
 * файл от компонента — чтобы проверять инвариант Rt_p10+Rt_band=Rt_p90
 * юнит-тестом без рендера SVG.
 */
export function buildForecastChartData(forecast: ForecastResult): ForecastChartPoint[] {
  return [
    {
      period: 0,
      Rt: forecast.current.Rt,
      Rt_p10: forecast.current.Rt,
      Rt_p90: forecast.current.Rt,
      Rt_band: 0,
    },
    ...forecast.forecast.map((p) => {
      const p10 = p.Rt_p10 ?? p.Rt;
      const p90 = p.Rt_p90 ?? p.Rt;
      return { period: p.period, Rt: p.Rt, Rt_p10: p10, Rt_p90: p90, Rt_band: p90 - p10 };
    }),
  ];
}
