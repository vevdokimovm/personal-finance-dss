import { useRef, useState } from "react";
import { ListSkeleton, StatePanel, Button } from "@shared/ui";
import { t } from "@shared/lib/i18n/t";
import { getConsentRequiredDetail } from "@shared/lib/api/extractErrorMessage";
import { useGoals, type Goal } from "@entities/goals";
import { ConsentRequiredPanel } from "@entities/consents";
import { SessionExpiredPanel, isSessionExpired } from "@entities/auth";
import { GoalRow } from "./ui/GoalRow";
import { GoalForm } from "./ui/GoalForm";
import { GoalContributionForm } from "./ui/GoalContributionForm";
import "./GoalsPage.css";

export function GoalsPage() {
  const query = useGoals();
  // undefined — модалка закрыта; null — создание; объект — правка этой записи.
  const [editing, setEditing] = useState<Goal | null | undefined>(undefined);
  // Отдельная модалка «внести прогресс» — независима от editing (см. ObligationsPage.tsx
  // для паттерна key-форсированного remount create/edit).
  const [contributing, setContributing] = useState<Goal | undefined>(undefined);
  const addButtonRef = useRef<HTMLButtonElement>(null);
  // Фокус после успешной выдачи согласия (a11y-auditor) — см. ObligationsPage.tsx.
  const headingRef = useRef<HTMLHeadingElement>(null);

  const addButton = (
    <Button ref={addButtonRef} variant="primary" onClick={() => setEditing(null)}>
      {t("Добавить цель")}
    </Button>
  );
  const modal = (
    <GoalForm
      key={editing?.id ?? "new"}
      open={editing !== undefined}
      onOpenChange={(open) => !open && setEditing(undefined)}
      goal={editing ?? undefined}
    />
  );
  const contributionModal = (
    <GoalContributionForm
      key={contributing?.id ?? "none"}
      open={contributing !== undefined}
      onOpenChange={(open) => !open && setContributing(undefined)}
      goal={contributing}
    />
  );

  if (query.isLoading) {
    return (
      <main className="fp-goals">
        <h1 ref={headingRef} tabIndex={-1}>
          {t("Цели")}
        </h1>
        <ListSkeleton rows={3} />
      </main>
    );
  }

  if (query.isError) {
    /* 🔴 401 — истёкшая сессия, а не сбой связи (гипотеза 7). Кнопка «Повторить»
       на нём возвращала бы 401 бесконечно, а совет проверить интернет при работающем
       интернете уводит человека чинить не то. `JWT_TTL_HOURS = 168` и refresh-токена
       нет — событие регулярное. */
    if (isSessionExpired(query.error)) {
      return (
        <main className="fp-goals">
          <h1 ref={headingRef} tabIndex={-1}>
            {t("Цели")}
          </h1>
          <SessionExpiredPanel redirectTo="/goals" />
        </main>
      );
    }
    const consentDetail = getConsentRequiredDetail(query.error);
    if (consentDetail) {
      return (
        <main className="fp-goals">
          <h1 ref={headingRef} tabIndex={-1}>
            {t("Цели")}
          </h1>
          <ConsentRequiredPanel
            detail={consentDetail}
            onGranted={() => void query.refetch().then(() => headingRef.current?.focus())}
          />
        </main>
      );
    }
    return (
      <main className="fp-goals">
        <h1 ref={headingRef} tabIndex={-1}>
          {t("Цели")}
        </h1>
        <StatePanel
          title={t("Не получилось загрузить цели")}
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

  const goals = query.data ?? [];

  if (goals.length === 0) {
    return (
      <main className="fp-goals">
        <h1 ref={headingRef} tabIndex={-1}>
          {t("Цели")}
        </h1>
        <StatePanel title={t("Целей пока нет")} action={addButton}>
          {t("Добавьте финансовую цель — план распределения начнёт откладывать на неё.")}
        </StatePanel>
        {modal}
      </main>
    );
  }

  return (
    <main className="fp-goals">
      <div className="fp-goals__head">
        <h1 ref={headingRef} tabIndex={-1}>
          {t("Цели")}
        </h1>
        {addButton}
      </div>
      <ul className="fp-goals__list">
        {goals.map((goal) => (
          <GoalRow
            key={goal.id}
            goal={goal}
            onEdit={() => setEditing(goal)}
            onContribute={() => setContributing(goal)}
            onDeleted={() => addButtonRef.current?.focus()}
          />
        ))}
      </ul>
      {modal}
      {contributionModal}
    </main>
  );
}
