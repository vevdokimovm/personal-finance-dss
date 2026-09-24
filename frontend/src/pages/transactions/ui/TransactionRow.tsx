import { formatMoney } from "@shared/lib/money/formatMoney";
import { formatDate } from "@shared/lib/date/formatDate";
import { t } from "@shared/lib/i18n/t";
import { Button, toast } from "@shared/ui";
import {
  useDeleteTransaction,
  useRestoreTransaction,
  type Transaction,
} from "@entities/transactions";
import { SharedBadge } from "@features/household-scope";
import { toastMutationError } from "@entities/auth";

export function TransactionRow({
  transaction,
  onEdit,
  onDeleted,
}: {
  transaction: Transaction;
  onEdit: () => void;
  /** Фокус после удаления строки иначе проваливается в `<body>` (a11y-auditor, Батч 1,
   * WCAG 2.4.3) — строка исчезает из DOM вместе с кнопкой, на которой стоял фокус. */
  onDeleted: () => void;
}) {
  const isIncome = transaction.type === "income";
  const sign = isIncome ? "+" : "−"; // A11Y-07: не только цветом — ещё и знаком/словом.
  const deleteTransaction = useDeleteTransaction();
  const restoreTransaction = useRestoreTransaction();

  function handleDelete() {
    const label = transaction.description || transaction.category;
    deleteTransaction.mutate(transaction.id, {
      onSuccess: () => {
        onDeleted();
        toast.undo(t("Операция «{label}» удалена.", { label }), () => {
          restoreTransaction.mutate(transaction.id, {
            onSuccess: () => toast.success(t("Операция «{label}» восстановлена.", { label })),
            onError: (error) =>
              toastMutationError(error, t("Не получилось восстановить. Попробуйте ещё раз.")),
          });
        });
      },
      onError: (error) =>
        toastMutationError(error, t("Не получилось удалить. Попробуйте ещё раз.")),
    });
  }

  return (
    <li className="fp-transaction-row">
      <div className="fp-transaction-row__main">
        <span className="fp-transaction-row__category">{transaction.category}</span>
        <SharedBadge householdId={transaction.household_id} />
        {transaction.description && (
          <span className="fp-transaction-row__description">{transaction.description}</span>
        )}
      </div>
      <span className="fp-transaction-row__date">{formatDate(transaction.date)}</span>
      <span
        className={
          isIncome ? "fp-transaction-row__amount--income" : "fp-transaction-row__amount--expense"
        }
      >
        <span className="sr-only">{isIncome ? t("доход") : t("расход")}</span>
        {sign}
        {formatMoney(transaction.amount)}
      </span>
      <div className="fp-transaction-row__actions">
        <Button variant="ghost" onClick={onEdit}>
          {t("Изменить")}
        </Button>
        <Button
          variant="danger"
          onClick={handleDelete}
          disabled={deleteTransaction.isPending}
          aria-label={t("Удалить «{label}»", {
            label: transaction.description || transaction.category,
          })}
        >
          {deleteTransaction.isPending ? t("Удаляем…") : t("Удалить")}
        </Button>
      </div>
    </li>
  );
}
