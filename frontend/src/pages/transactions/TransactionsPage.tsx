import { ListSkeleton, StatePanel, Button } from "@shared/ui";
import { t } from "@shared/lib/i18n/t";
import { useTransactions } from "@entities/transactions";
import { TransactionRow } from "./ui/TransactionRow";
import "./TransactionsPage.css";

export function TransactionsPage() {
  const query = useTransactions();

  if (query.isLoading) {
    return (
      <main className="fp-transactions">
        <h1>{t("Операции")}</h1>
        <ListSkeleton rows={6} />
      </main>
    );
  }

  if (query.isError) {
    return (
      <main className="fp-transactions">
        <h1>{t("Операции")}</h1>
        <StatePanel
          title={t("Не получилось загрузить операции")}
          role="alert"
          action={
            <Button variant="primary" onClick={() => void query.refetch()}>
              {t("Повторить")}
            </Button>
          }
        >
          {t("Проверьте соединение и попробуйте ещё раз. Если повторится — напишите в поддержку.")}
        </StatePanel>
      </main>
    );
  }

  const transactions = query.data ?? [];

  if (transactions.length === 0) {
    return (
      <main className="fp-transactions">
        <h1>{t("Операции")}</h1>
        <StatePanel title={t("Операций пока нет")}>
          {t("Добавьте доходы и расходы за 1–2 месяца — тогда СППР сможет построить план.")}
        </StatePanel>
      </main>
    );
  }

  return (
    <main className="fp-transactions">
      <h1>{t("Операции")}</h1>
      <p className="fp-transactions__legend">
        <span className="fp-dot" style={{ background: "var(--c-green)" }} />
        {t("доходы")}
        <span className="fp-dot" style={{ background: "var(--c-red)" }} />
        {t("расходы")}
      </p>
      <ul className="fp-transactions__list">
        {transactions.map((tx) => (
          <TransactionRow key={tx.id} transaction={tx} />
        ))}
      </ul>
    </main>
  );
}
