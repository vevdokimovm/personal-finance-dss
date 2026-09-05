/** Рукописных типов нет — реэкспорт сгенерированных из контракта.
 *
 * `SpendingAdviceResponse` и типы его коллекций заведены на бэкенде в этом же батче
 * ДО фронта (`app/schemas/spending.py`): эндпоинт был размечен `dict[str, Any]`,
 * то есть генератор выдал бы `unknown`, и форму пришлось бы дописывать руками —
 * ровно так появились двойные касты, снятые в v8.50.0. */
export type {
  SpendingAdviceResponse,
  SpendingAdviceSchema,
  CategoryStatsSchema,
  MerchantStatsSchema,
  TemporalPatternSchema,
  GoalImpactSchema,
} from "@shared/api/generated";
