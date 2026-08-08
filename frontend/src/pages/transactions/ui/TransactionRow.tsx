import { formatMoney } from "@shared/lib/money/formatMoney";
import { formatDate } from "@shared/lib/date/formatDate";
import { t } from "@shared/lib/i18n/t";
import type { Transaction } from "@entities/transactions";

export function TransactionRow({ transaction }: { transaction: Transaction }) {
  const isIncome = transaction.type === "income";
  const sign = isIncome ? "+" : "−"; // A11Y-07: не только цветом — ещё и знаком/словом.
  return (
    <li className="fp-transaction-row">
      <div className="fp-transaction-row__main">
        <span className="fp-transaction-row__category">{transaction.category}</span>
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
    </li>
  );
}
