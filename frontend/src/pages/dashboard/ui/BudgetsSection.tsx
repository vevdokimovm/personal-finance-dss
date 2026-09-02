import { useRef, useState } from "react";
import { ListSkeleton, StatePanel, Button } from "@shared/ui";
import { t } from "@shared/lib/i18n/t";
import { getConsentRequiredDetail } from "@shared/lib/api/extractErrorMessage";
import { useBudgetStatus, type BudgetStatus } from "@entities/budgets";
import { ConsentRequiredPanel } from "@entities/consents";
import { BudgetRow } from "./BudgetRow";
import { BudgetForm } from "./BudgetForm";
import "./BudgetsSection.css";

/** Секция «Бюджеты по категориям» на дашборде (Батч 3 CRUD-паритета, ROADMAP §8.2, «Бюджет
 * (dashboard) — создание/правка»). Самостоятельный запрос (GET /api/budgets/status), не часть
 * usePlan/useForecast — падение здесь не должно блокировать остальной обзор, поэтому у секции
 * СВОИ загрузка/ошибка/согласие/пусто, не общий гейт DashboardPage. h2 держится видимым во ВСЕХ
 * состояниях (тот же принцип, что h1 на ObligationsPage/GoalsPage) — вложенные StatePanel/
 * ConsentRequiredPanel получают headingLevel=3, чтобы не давать два h2 подряд без текста
 * между ними (контур документа, design-critic). */
export function BudgetsSection() {
  const query = useBudgetStatus();
  // undefined — модалка закрыта; null — создание; объект — правка этого бюджета.
  const [editing, setEditing] = useState<BudgetStatus | null | undefined>(undefined);
  const addButtonRef = useRef<HTMLButtonElement>(null);
  const headingRef = useRef<HTMLHeadingElement>(null);

  const addButton = (
    <Button ref={addButtonRef} variant="primary" onClick={() => setEditing(null)}>
      {t("Добавить бюджет")}
    </Button>
  );
  // key форсирует remount при смене цели редактирования — тот же приём, что ObligationForm
  // (Батч 1): без него форма не сбрасывает значения при переключении между записями.
  const modal = (
    <BudgetForm
      key={editing?.id ?? "new"}
      open={editing !== undefined}
      onOpenChange={(open) => !open && setEditing(undefined)}
      budget={editing ?? undefined}
    />
  );

  if (query.isLoading) {
    return (
      <section className="fp-panel fp-budgets">
        <h2 ref={headingRef} tabIndex={-1}>
          {t("Бюджеты по категориям")}
        </h2>
        <ListSkeleton rows={3} />
      </section>
    );
  }

  if (query.isError) {
    const consentDetail = getConsentRequiredDetail(query.error);
    if (consentDetail) {
      return (
        <section className="fp-panel fp-budgets">
          <h2 ref={headingRef} tabIndex={-1}>
            {t("Бюджеты по категориям")}
          </h2>
          <ConsentRequiredPanel
            detail={consentDetail}
            headingLevel={3}
            onGranted={() => void query.refetch().then(() => headingRef.current?.focus())}
          />
        </section>
      );
    }
    return (
      <section className="fp-panel fp-budgets">
        <h2 ref={headingRef} tabIndex={-1}>
          {t("Бюджеты по категориям")}
        </h2>
        <StatePanel
          title={t("Не получилось загрузить бюджеты")}
          role="alert"
          headingLevel={3}
          action={
            <Button variant="primary" onClick={() => void query.refetch()}>
              {t("Повторить")}
            </Button>
          }
        >
          {t("Проверьте соединение и попробуйте ещё раз. Если повторится — напишите в поддержку.")}
        </StatePanel>
      </section>
    );
  }

  const budgets = query.data ?? [];

  if (budgets.length === 0) {
    return (
      <section className="fp-panel fp-budgets">
        <h2 ref={headingRef} tabIndex={-1}>
          {t("Бюджеты по категориям")}
        </h2>
        <StatePanel title={t("Бюджетов пока нет")} headingLevel={3} action={addButton}>
          {t("Задайте месячный лимит по категории — здесь будет видно, сколько уже потрачено.")}
        </StatePanel>
        {modal}
      </section>
    );
  }

  return (
    <section className="fp-panel fp-budgets">
      <div className="fp-budgets__head">
        <h2 ref={headingRef} tabIndex={-1}>
          {t("Бюджеты по категориям")}
        </h2>
        {addButton}
      </div>
      <ul className="fp-budgets__list">
        {budgets.map((b) => (
          <BudgetRow
            key={b.id}
            budget={b}
            onEdit={() => setEditing(b)}
            onDeleted={() => addButtonRef.current?.focus()}
          />
        ))}
      </ul>
      {modal}
    </section>
  );
}
