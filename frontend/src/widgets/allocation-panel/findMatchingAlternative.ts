import type { PlanAlternative } from "@entities/plan-summary";

/** Сетка альтернатив — фиксированный шаг 10% (app/core/alternatives.py), 11 отметок 0..10 на
 * каждую категорию (0%, 10%, …, 100%). Ползунки «что если» работают в тех же отметках, не в
 * произвольных процентах — так поиск совпадения точный, без сравнения чисел с плавающей точкой. */
export const GRID_NOTCHES = 10;

function notchOf(amount: number, total: number): number {
  return Math.round((amount / total) * GRID_NOTCHES);
}

/** Долг/цели — категории, которые иногда отсутствуют в сетке целиком (нет обязательств/целей —
 * app/core/alternatives.py фильтрует все точки с этой категорией > 0). Если ни одна альтернатива
 * не предлагает ненулевую долю категории, соответствующий ползунок незачем показывать. */
export function hasNonZeroCategory(
  alternatives: PlanAlternative[],
  category: "x_obligations" | "x_goals",
): boolean {
  return alternatives.some((alt) => alt[category] > 0);
}

export function notchesOf(alt: PlanAlternative, total: number): { debt: number; goals: number } {
  return { debt: notchOf(alt.x_obligations, total), goals: notchOf(alt.x_goals, total) };
}

/** undefined — гипотетическая точка не прошла отсев модели (например, ПДН превысил бы 40%,
 * жёсткий инвариант канона) и не попала в `ranked`: это не баг ползунка, а честный ответ
 * «модель не считает такое распределение допустимым». */
export function findMatchingAlternative(
  alternatives: PlanAlternative[],
  total: number,
  debtNotch: number,
  goalsNotch: number,
): PlanAlternative | undefined {
  if (total <= 0) return undefined;
  return alternatives.find((alt) => {
    const n = notchesOf(alt, total);
    return n.debt === debtNotch && n.goals === goalsNotch;
  });
}
