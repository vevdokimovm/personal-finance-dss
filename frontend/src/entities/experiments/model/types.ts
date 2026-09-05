/** Рукописных типов нет — реэкспорт сгенерированных из контракта.
 *
 * `ExperimentResults` и `VariantResult` заведены на бэкенде в этом же батче
 * ДО фронта: эндпоинт результатов был размечен `-> dict`. */
export type {
  ExperimentResponse,
  ExperimentResults,
  VariantResult,
} from "@shared/api/generated";
