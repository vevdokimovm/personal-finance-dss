/**
 * Рукописных типов нет — только реэкспорт сгенерированных из контракта.
 *
 * Схемы `ReferralMe`/`ReferralMilestone` заведены на бэкенде в этом же батче ДО
 * появления фронта: до него эндпоинт был размечен `-> dict`, и фронту пришлось бы
 * писать рукописный тип с кастом — путь, которым родился дефект v8.31.1.
 */
export type { ReferralMe, ReferralMilestone, ReferralNextMilestone } from "@shared/api/generated";
