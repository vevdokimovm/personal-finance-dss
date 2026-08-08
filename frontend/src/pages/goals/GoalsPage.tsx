import { ListSkeleton, StatePanel, Button } from "@shared/ui";
import { t } from "@shared/lib/i18n/t";
import { useGoals } from "@entities/goals";
import { GoalRow } from "./ui/GoalRow";
import "./GoalsPage.css";

export function GoalsPage() {
  const query = useGoals();

  if (query.isLoading) {
    return (
      <main className="fp-goals">
        <h1>{t("Цели")}</h1>
        <ListSkeleton rows={3} />
      </main>
    );
  }

  if (query.isError) {
    return (
      <main className="fp-goals">
        <h1>{t("Цели")}</h1>
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
        <h1>{t("Цели")}</h1>
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
