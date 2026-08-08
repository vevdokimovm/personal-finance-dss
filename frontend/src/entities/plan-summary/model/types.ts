/**
 * Локальные типы для /api/planning/calculate и /api/planning/forecast — в OpenAPI-снимке
 * оба размечены `-> dict[str, Any]` (app/api/routes_planning.py), поэтому hey-api сгенерировал
 * их как `{[key: string]: unknown}`. Формы ниже сверены с реальным кодом бэкенда
 * (_compute_plan в routes_planning.py, forecast_indicators в services/forecasting.py), не
 * придуманы — если бэкенд обзаведётся строгой Pydantic-схемой для этих двух эндпоинтов,
 * этот файл станет не нужен.
 */

export interface PlanIndicators {
  Rt: number;
  Lt: number;
  Dt: number;
  BLR?: number | null;
  It?: number | null;
  Et?: number | null;
  SigmaP?: number | null;
}

export interface PlanAlternative {
  name: string;
  x_obligations: number;
  x_reserve: number;
  x_goals: number;
  utility: number;
}

export interface PlanInputSummary {
  income: number;
  expense: number;
  bliq: number;
  transactions_count: number;
  obligations_count: number;
  goals_count: number;
}

export interface CalculatePlanResult {
  indicators: PlanIndicators;
  top3: PlanAlternative[];
  admissible_count: number;
  alternatives_total: number;
  input_summary: PlanInputSummary;
  /** Метка риск-профиля ("Сбалансированный" и т. п., app/core/ranking.py RISK_PROFILES) — строка,
   * не число; бэкенд всегда её отдаёт (run_planning в app/services/planning.py). */
  risk_profile: string;
}

export interface ForecastPoint {
  period: number;
  Rt: number;
  Rt_p10?: number;
  Rt_p50?: number;
  Rt_p90?: number;
}

export interface ForecastResult {
  current: { Bt: number; Rt: number; Lt: number; Dt: number };
  horizon: number;
  forecast: ForecastPoint[];
}
