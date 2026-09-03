/**
 * Рукописных типов здесь НЕТ и не должно быть — только реэкспорт сгенерированных.
 *
 * Урок v8.31.1: `entities/plan-summary` вёлся руками, обещал больше контракта
 * (`ranked`, `top3`, `Explanation.gains/costs` объявлены обязательными, хотя в схеме
 * они вне `required`), TypeScript молчал из-за каста — и дашборд падал в error boundary
 * на ответе, который контракт прямо разрешает. Остальные сущности (`goals`,
 * `obligations`, `assets`, `transactions`, `profile`, `auth`) реэкспортируют
 * сгенерированный тип и расхождений не имеют. Уведомления идут по второму пути.
 */
export type { NotificationFeed, NotificationOut } from "@shared/api/generated";
