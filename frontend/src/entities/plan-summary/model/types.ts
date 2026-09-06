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
/* Кризисный план: реэкспорт из контракта (v9.1.0). Считался с v6.0.0 и не показывался
   никому — `grep crisis` по `frontend/src` давал ноль. */
export type { CrisisPlan, CrisisAction } from "@shared/api/generated";

export type PlanIndicators = PlanningIndicators;
export type PlanAlternative = Alternative;
export type PlanInputSummary = InputSummary;
export type CalculatePlanResult = PlanningCalculateResponse;

/* 🔴 `ForecastPoint` и `ForecastResult` были ПОСЛЕДНИМИ рукописными типами фронта.
   Заменены реэкспортом сгенерированных в v8.48.0, когда `/planning/forecast` получил
   схему (`ForecastResponse` на бэкенде).

   Заведение схемы показало, ЧЕГО рукописные типы не знали:
   · `ForecastPoint` описывал 5 полей из 12 — фронт не видел `income`, `expense`,
     `obligations`, `cash_flow`, `Bt`, `Lt`, `Dt` по месяцам, то есть весь состав
     прогноза, кроме свободного ресурса;
   · `ForecastResult` не знал `deficit_alert` (предупреждение о месяце, когда денег
     не хватит — самое важное, что прогноз умеет сказать), `trend`, `stable_baseline`
     и `method`.

   Это и есть довод за генерацию: рукописный тип показывает то, что помнил автор,
   и молчит обо всём остальном — компилятор при этом доволен. */
export type { ForecastPoint, ForecastResponse as ForecastResult } from "@shared/api/generated";
