import type { ForecastPoint, ForecastResult } from "@entities/plan-summary";

/**
 * Фабрика точки прогноза для тестов.
 *
 * 🔴 Заведена в v8.48.0, когда `ForecastPoint` перестал быть рукописным и стал
 * приезжать из контракта. Компилятор сразу показал, что фикстуры описывали **пять полей
 * из двенадцати**: тесты работали с прогнозом, в котором нет ни доходов, ни расходов,
 * ни обязательств по месяцам — то есть проверяли поведение на данных, которых сервер
 * никогда не присылает.
 *
 * Дописывать недостающие поля в каждый объект руками значило бы получить ту же проблему
 * при следующем изменении схемы, только в двадцати местах. Фабрика даёт полную точку
 * и позволяет переопределить ровно то, что проверяет конкретный тест.
 */
export function makeForecastPoint(overrides: Partial<ForecastPoint> = {}): ForecastPoint {
  return {
    period: 1,
    Bt: 265000,
    income: 180000,
    expense: 78000,
    obligations: 62500,
    cash_flow: 102000,
    Rt: 39500,
    Lt: 0.5,
    Dt: 0.35,
    Rt_p10: 30000,
    Rt_p50: 39500,
    Rt_p90: 49000,
    ...overrides,
  };
}

/**
 * Фабрика полного ответа прогноза.
 *
 * Та же причина, что у `makeForecastPoint`, уровнем выше: рукописный `ForecastResult`
 * не знал `trend`, `stable_baseline`, `method` и `deficit_alert`, поэтому фикстуры
 * тестов их не содержали — и тесты проверяли экран на ответе, которого сервер
 * не присылает.
 *
 * `deficit_alert` по умолчанию отсутствует: это нормальный исход («дефицита
 * не предвидится»), а тест про предупреждение передаёт его явно.
 */
export function makeForecast(overrides: Partial<ForecastResult> = {}): ForecastResult {
  return {
    current: { Bt: 265000, Rt: 39500, Lt: 0.5, Dt: 0.35 },
    horizon: 6,
    forecast: [makeForecastPoint()],
    trend: "stable",
    stable_baseline: {
      recurring_income: 180000,
      recurring_expense: 78000,
      recurring_cash_flow: 102000,
      income_share: 1,
      expense_share: 1,
    },
    method: { point: "holt", interval: "monte-carlo" },
    r_bench: 0.139,
    r_bench_source: "cbr_keyrate_post_tax",
    real_r_bench: 0.139,
    ...overrides,
  };
}
