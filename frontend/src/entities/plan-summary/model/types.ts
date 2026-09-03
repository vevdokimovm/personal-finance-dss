/**
 * Локальные типы для /api/planning/calculate и /api/planning/forecast.
 *
 * ОБНОВЛЕНО v8.31.1 — прежняя редакция этого комментария УСТАРЕЛА и вводила в
 * заблуждение. Она утверждала, что оба эндпоинта размечены `-> dict[str, Any]` и потому
 * не типизированы в снимке. Для `/forecast` это по-прежнему верно
 * (`{[key: string]: unknown}` в `types.gen.ts`), а для **`/calculate` — уже нет**: в
 * контракте есть полная схема `PlanningCalculateResponse` со вложенными `Alternative`,
 * `PlanningIndicators`, `InputSummary`, `Weights`, `BliqPreallocation`.
 *
 * Из-за устаревшего комментария файл продолжали вести руками, и рукописные типы стали
 * обещать БОЛЬШЕ, чем гарантирует схема (`ranked`, `top3`, `Explanation.gains/costs` —
 * все вне `required`). TypeScript при этом молчал, потому что `usePlan.ts` делает
 * `data as unknown as CalculatePlanResult` — каст выбрасывает сгенерированный тип и
 * снимает всякую сверку с контрактом. Итог: экран падал в error boundary на ответе,
 * который контракт разрешает.
 *
 * Правильное решение — генерировать этот тип из `PlanningCalculateResponse`, как уже
 * сделано для `entities/goals`, `obligations`, `assets`, `transactions`, `profile`, `auth`
 * (там простой реэкспорт сгенерированного типа, и расхождений нет). Это структурная
 * замена, вынесена в ROADMAP §8.2 отдельным пунктом; здесь пока приведена в соответствие
 * ОБЯЗАТЕЛЬНОСТЬ полей — то, из-за чего падал экран.
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

export interface PlanAlternative {
  id: string;
  name: string;
  x_obligations: number;
  x_reserve: number;
  x_goals: number;
  /** SAW-полезность альтернативы (app/core/ranking.py rank_alternatives), 0..1. */
  utility: number;
  /** Свободный поток/ликвидность/ПДН ПОСЛЕ применения альтернативы (evaluate_alternative). */
  Rt_new: number;
  Lt_new: number;
  Dt_new: number;
  /** Только у одной альтернативы в ranked — лучшая по (floor_level, utility). */
  is_recommended?: boolean;
  weighted_scores?: WeightedScores;
  /** Только у top3 — explain_alternative() вызывается лишь для них (app/services/planning.py).
   * У произвольного элемента ranked[] (гипотетическая позиция ползунков «что если») — не будет. */
  explanation?: Explanation | null;
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
  /* Тоже вне `required` схемы `PlanningCalculateResponse` — проверено на диске.
     `plan.top3[0] ?? null` защищал только результат индексации, но не сам массив:
     на ответе без `top3` падало ещё до рендера панели, роняя и Dashboard, и Planning. */
  top3?: PlanAlternative[];
  /** Все допустимые альтернативы (после фильтра §5), отсортированные по (floor_level, utility) —
   * до 66 при канонической сетке шага 10% (app/core/alternatives.py generate_alternatives).
   * top3 — НЕ буквально ranked[:3]: строится из distinct_ranked, дедуплицированного по
   * эффективному распределению (app/services/planning.py, _effective_signature), плюс
   * explanation. top3[0] и ranked[0] всегда совпадают (первый элемент дедупликация не
   * выбрасывает), начиная со второго — позиции могут разойтись.
   *
   * ОПЦИОНАЛЬНОЕ, и это не осторожность, а контракт: в схеме
   * `PlanningCalculateResponse` (`docs/api/openapi.json`) поля НЕТ в `required` —
   * у него `default_factory=list` в `app/schemas/planning.py:283`. Пока здесь стояло
   * обязательное `PlanAlternative[]`, рукописный тип обещал больше, чем гарантирует
   * бэкенд: TypeScript молчал, а `AllocationPanel` звал `.some()` по undefined и ронял
   * весь дашборд в error boundary. Найдено 2026-09-03, v8.31.1. */
  ranked?: PlanAlternative[];
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
