import { useRef, useState } from "react";
import { ListSkeleton, StatePanel, Button } from "@shared/ui";
import { t } from "@shared/lib/i18n/t";
import { getConsentRequiredDetail } from "@shared/lib/api/extractErrorMessage";
import { useTransactions, type Transaction } from "@entities/transactions";
import { ConsentRequiredPanel } from "@entities/consents";
import { TransactionRow } from "./ui/TransactionRow";
import { TransactionForm } from "./ui/TransactionForm";
import { StatementImportSection } from "./ui/StatementImportSection";
import "./TransactionsPage.css";

export function TransactionsPage() {
  const query = useTransactions();
  // undefined — модалка закрыта; null — создание; объект — правка этой записи.
  const [editing, setEditing] = useState<Transaction | null | undefined>(undefined);
  const addButtonRef = useRef<HTMLButtonElement>(null);
  // Фокус после успешной выдачи согласия (a11y-auditor) — см. ObligationsPage.tsx.
  const headingRef = useRef<HTMLHeadingElement>(null);

  const addButton = (
    <Button ref={addButtonRef} variant="primary" onClick={() => setEditing(null)}>
      {t("Добавить операцию")}
    </Button>
  );
  const modal = (
    <TransactionForm
      key={editing?.id ?? "new"}
      open={editing !== undefined}
      onOpenChange={(open) => !open && setEditing(undefined)}
      transaction={editing ?? undefined}
    />
  );

  if (query.isLoading) {
    return (
      <main className="fp-transactions">
        <h1 ref={headingRef} tabIndex={-1}>
          {t("Операции")}
        </h1>
        <ListSkeleton rows={6} />
      </main>
    );
  }

  if (query.isError) {
    const consentDetail = getConsentRequiredDetail(query.error);
    if (consentDetail) {
      return (
        <main className="fp-transactions">
          <h1 ref={headingRef} tabIndex={-1}>
            {t("Операции")}
          </h1>
          <ConsentRequiredPanel
            detail={consentDetail}
            onGranted={() => void query.refetch().then(() => headingRef.current?.focus())}
          />
        </main>
      );
    }
    return (
      <main className="fp-transactions">
        <h1 ref={headingRef} tabIndex={-1}>
          {t("Операции")}
        </h1>
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
        <h1 ref={headingRef} tabIndex={-1}>
          {t("Операции")}
        </h1>
        <StatePanel title={t("Операций пока нет")} action={addButton}>
          {t("Добавьте доходы и расходы за 1–2 месяца — тогда СППР сможет построить план.")}
        </StatePanel>
        {/* Импорт особенно нужен ИМЕННО здесь: человеку без операций проще загрузить
            выписку, чем вводить сотню строк руками. */}
        <StatementImportSection />
        {modal}
      </main>
    );
  }

  return (
    <main className="fp-transactions">
      <div className="fp-transactions__head">
        <h1 ref={headingRef} tabIndex={-1}>
          {t("Операции")}
        </h1>
        {addButton}
      </div>
      <ul className="fp-transactions__list">
        {transactions.map((tx) => (
          <TransactionRow
            key={tx.id}
            transaction={tx}
            onEdit={() => setEditing(tx)}
            onDeleted={() => addButtonRef.current?.focus()}
          />
        ))}
      </ul>
      {/* Импорт — НИЖЕ списка, когда операции уже есть: главное содержание экрана это они,
          и вспомогательная форма не должна отжимать их вниз (design-critic). В пустой ветке
          наоборот — там списка нет, и загрузить выписку проще, чем ввести сотню строк. */}
      <StatementImportSection />
      {modal}
    </main>
  );
}
