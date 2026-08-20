import { t } from "@shared/lib/i18n/t";
import type { GoalCategory } from "@shared/api/generated";

// Канон: app/core/recommendation.py::CATEGORY_LABELS / docs/math_model.md §11.1.
export const GOAL_CATEGORY_OPTIONS: { value: GoalCategory; label: string }[] = [
  { value: "income_growth", label: t("Рост дохода") },
  { value: "safety", label: t("Безопасность") },
  { value: "material", label: t("Материальная цель") },
  { value: "emotional", label: t("Эмоциональная цель") },
];

export const GOAL_CATEGORY_LABEL: Record<string, string> = Object.fromEntries(
  GOAL_CATEGORY_OPTIONS.map((opt) => [opt.value, opt.label]),
);
