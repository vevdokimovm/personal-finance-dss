import { useRef } from "react";
import { ListSkeleton, StatePanel, Button } from "@shared/ui";
import { t } from "@shared/lib/i18n/t";
import { getConsentRequiredDetail } from "@shared/lib/api/extractErrorMessage";
import { useGoals } from "@entities/goals";
import { ConsentRequiredPanel } from "@entities/consents";
import { GoalRow } from "./ui/GoalRow";
import "./GoalsPage.css";

export function GoalsPage() {
  const query = useGoals();
  // Фокус после успешной выдачи согласия (a11y-auditor) — см. ObligationsPage.tsx.
  const headingRef = useRef<HTMLHeadingElement>(null);

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
        <StatePanel title={t("Целей пока нет")}>
          {t("Добавьте финансовую цель — план распределения начнёт откладывать на неё.")}
        </StatePanel>
      </main>
    );
  }

  return (
    <main className="fp-goals">
      <h1>{t("Цели")}</h1>
      <ul className="fp-goals__list">
        {goals.map((goal) => (
          <GoalRow key={goal.id} goal={goal} />
        ))}
      </ul>
    </main>
  );
}
