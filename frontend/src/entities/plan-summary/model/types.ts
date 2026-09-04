import type {
  Alternative,
  InputSummary,
  PlanningCalculateResponse,
  PlanningIndicators,
} from "@shared/api/generated";

/**
 * Типы `/api/planning/calculate` — РЕЭКСПОРТ сгенерированных из контракта (v8.40.0).
 *
 * 🔴 Долг закрыт. Раньше этот файл вёлся руками, и рукописные типы обещали БОЛЬШЕ, чем
 * гарантирует схема (`ranked`, `top3`, `Explanation.gains/costs` — все вне `required`).
 * TypeScript молчал, потому что `usePlan.ts` делал `data as unknown as CalculatePlanResult`:
 * каст выбрасывает сгенерированный тип и снимает всякую сверку с контрактом. Итог —
 * дашборд падал в error boundary на ответе, который контракт разрешает (v8.31.1).
 *
 * Повод закрыть долг именно сейчас: в ответ добавлено поле `disclaimer` (39-ФЗ, L5), и
 * рукописный тип о нём не знал — экран не смог бы показать обязательный по закону текст,
 * а компилятор сказал бы «свойства не существует» о поле, которое сервер отдаёт. Ровно
 * тот же класс ошибки, только с другой стороны.
 *
 * Что осталось рукописным и почему: `ForecastResult` — `/planning/forecast` до сих пор
 * размечен `-> dict[str, Any]`, в контракте у него `{[key: string]: unknown}`, и
 * реэкспортировать нечего. Это следующий кандидат на ту же операцию.
 */


/** Вклад критериев SAW в utility (батч 0.3, app/core/ranking.py::rank_alternatives) —
 * ключи служебные (Rt/Lt/Dt/Si), как у ExplanationDelta ниже; сумма ≈ utility. */
export interface WeightedScores {
  Rt: number;
  Lt: number;
  Dt: number;
  Si: number;
}

/** Что изменилось бы, чтобы победил другой вариант (батч 0.4) — сравнение с реально
 * посчитанным следующим по рангу вариантом, не гипотетический сценарий. */
export interface Counterfactual {
  available: boolean;
  alternative_id?: string | null;
  utility_gap?: number | null;
  /** Служебный ключ (Rt/Lt/Dt/Si) — человеческая формулировка уже в `text`. */
  dominant_criterion?: string | null;
  text?: string | null;
}

export interface Explanation {
  /* `gains`/`costs` — необязательные по контракту: в схеме `Explanation`
     (`docs/api/openapi.json`) в `required` стоит ТОЛЬКО `delta`. Пока здесь были
     обязательные массивы, `AllocationPanel` звал `.length` напрямую и падал на
     ответе без них — тот же класс, что `ranked` (v8.31.1). */
  gains?: string[];
  costs?: string[];
  insight: string;
  /** Служебный ключ доминирующего критерия — человеческая фраза уже вплетена в `insight`
   * («Решающим для оценки оказалось то, …»), отдельно рендерить не обязательно. */
  dominant_criterion?: string | null;
  counterfactual?: Counterfactual | null;
}





/* Алиасы на сгенерированные типы: имена, под которыми они уже разошлись по экранам,
   сохранены, чтобы правка не размазалась на десяток файлов. Определения — из контракта. */
export type PlanIndicators = PlanningIndicators;
export type PlanAlternative = Alternative;
export type PlanInputSummary = InputSummary;
export type CalculatePlanResult = PlanningCalculateResponse;

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
  /** Ставка капитализации баланса, фактически применённая (app/api/routes_planning.py::
   * get_forecast) — либо сценарий из запроса, либо реальная OCR (ключевая ЦБ после НДФЛ). */
  r_bench: number;
  /** "request" — сценарий «что если»; иначе источник реальной OCR
   * (app/services/cbr_rate.py::get_opportunity_cost_rate). */
  r_bench_source: string;
  /** Настоящая OCR НЕЗАВИСИМО от сценария — считается всегда, даже когда `r_bench` выше
   * это override из запроса. Нужна отдельно от `r_bench`: тот эхо'ит применённую ставку
   * (override ИЛИ реальную), одного поля недостаточно, чтобы после override узнать, к чему
   * возвращаться кнопкой «сбросить» (баг найден и исправлен при живой проверке в браузере). */
  real_r_bench: number;
}
