/**
 * Рукописных типов здесь НЕТ — только реэкспорт сгенерированных из контракта.
 *
 * Урок v8.31.1: `entities/plan-summary` вёлся руками, пообещал `ranked` и `top3`
 * обязательными (хотя схема их не требует), TypeScript молчал из-за каста — и дашборд
 * падал в error boundary на ответе, который контракт разрешает.
 *
 * Чтобы не повторять, схемы для истории планов заведены на БЭКЕНДЕ до появления фронта
 * (v8.34.0: `PlanSnapshotSummary`/`PlanSnapshotDetail`/`PlanHistoryList` вместо
 * `dict[str, Any]`), и фронт просто берёт сгенерированный тип.
 */
export type {
  PlanHistoryList,
  PlanSnapshotSummary,
  PlanSnapshotDetail,
} from "@shared/api/generated";
