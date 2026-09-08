import { formatMoney, formatNumber } from "@shared/lib/money/formatMoney";
import { t } from "@shared/lib/i18n/t";
import { Button, toast } from "@shared/ui";
import { useDeleteBudget, useRestoreBudget, type BudgetStatus } from "@entities/budgets";
import { SharedBadge } from "@features/household-scope";
import { toastMutationError } from "@entities/auth";

export function BudgetRow({
  budget,
  onEdit,
  onDeleted,
}: {
  budget: BudgetStatus;
  onEdit: () => void;
  /** Фокус после удаления строки иначе проваливается в `<body>` (тот же паттерн, что
   * ObligationRow/AssetRow, a11y-auditor, WCAG 2.4.3). */
  onDeleted: () => void;
}) {
  const deleteBudget = useDeleteBudget();
  const restoreBudget = useRestoreBudget();

  function handleDelete() {
    const category = budget.category;
    deleteBudget.mutate(budget.id, {
      onSuccess: () => {
        onDeleted();
        toast.undo(t("Бюджет «{category}» удалён.", { category }), () => {
          restoreBudget.mutate(budget.id, {
            onSuccess: () => toast.success(t("Бюджет «{category}» восстановлен.", { category })),
            onError: (error) => toastMutationError(error, t("Не получилось восстановить. Попробуйте ещё раз.")),
          });
        });
      },
      onError: (error) => toastMutationError(error, t("Не получилось удалить. Попробуйте ещё раз.")),
    });
  }

  const barWidth = Math.min(100, Math.max(0, budget.pct));
  return (
    <li className="fp-budget-row">
      <div className="fp-budget-row__head">
        <span className="fp-budget-row__category">{budget.category}</span>
        <SharedBadge householdId={budget.household_id} />
        {/* Потрачено — главное число строки: лимит сам по себе не говорит, где сейчас
            пользователь относительно него (design-critic, тот же принцип, что остаток
            долга в ObligationRow, Батч 1). */}
        <span className="fp-budget-row__spent">{formatMoney(budget.spent)}</span>
      </div>
      <div className="fp-budget-row__meta">
        <span>{t("Лимит: {v}", { v: formatMoney(budget.limit_amount) })}</span>
        <span>{formatNumber(budget.pct, 1)}%</span>
        {budget.over && (
          <span className="fp-budget-row__badge fp-budget-row__badge--over">{t("Превышен")}</span>
        )}
      </div>
      <div
        className="fp-budget-row__bar"
        role="presentation"
        data-over={budget.over ? "true" : undefined}
      >
        <div className="fp-budget-row__bar-fill" style={{ width: `${barWidth}%` }} />
      </div>
      <div className="fp-budget-row__actions">
        <Button variant="ghost" onClick={onEdit}>
          {t("Изменить")}
        </Button>
        <Button
          variant="danger"
          onClick={handleDelete}
          disabled={deleteBudget.isPending}
          aria-label={t("Удалить «{category}»", { category: budget.category })}
        >
          {deleteBudget.isPending ? t("Удаляем…") : t("Удалить")}
        </Button>
      </div>
    </li>
  );
}
