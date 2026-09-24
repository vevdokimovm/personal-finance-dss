import { formatDate } from "@shared/lib/date/formatDate";
import { t } from "@shared/lib/i18n/t";
import { Button, toast } from "@shared/ui";
import { useDeleteGoal, useRestoreGoal, GOAL_CATEGORY_LABEL, type Goal } from "@entities/goals";
import { SharedBadge } from "@features/household-scope";
import { toastMutationError } from "@entities/auth";

const NBSP = " ";

/** Копейки решаются по БОЛЬШЕМУ из двух чисел (design-critic, Батч 2): иначе «накоплено» и
 * «цель» показывали разное число знаков («0,00 из 500 000») — пара, которую пользователь
 * сравнивает глазами, обязана быть в одном формате. Знак ₽ — один, в конце (skill
 * finpilot-money-format: после числа через НЕразрывный пробел). */
function formatMoneyPair(current: number, target: number): { current: string; target: string } {
  const hideKopecks = Math.max(Math.abs(current), Math.abs(target)) > 100_000;
  const fmt = (v: number) => {
    const fixed = hideKopecks ? Math.round(Math.abs(v)).toString() : Math.abs(v).toFixed(2);
    const [intPart, fracPart] = fixed.split(".");
    const grouped = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, NBSP);
    return fracPart !== undefined ? `${grouped},${fracPart}` : grouped;
  };
  return { current: fmt(current), target: fmt(target) };
}

export function GoalRow({
  goal,
  onEdit,
  onContribute,
  onDeleted,
}: {
  goal: Goal;
  onEdit: () => void;
  /** Не вызывается для целей с linked_asset_id — GoalsPage не рендерит для них кнопку. */
  onContribute: () => void;
  /** Фокус после удаления строки иначе проваливается в `<body>` (a11y-auditor, Батч 1,
   * WCAG 2.4.3) — строка исчезает из DOM вместе с кнопкой, на которой стоял фокус. */
  onDeleted: () => void;
}) {
  const deleteGoal = useDeleteGoal();
  const restoreGoal = useRestoreGoal();
  const isLinkedToAsset = goal.linked_asset_id != null;

  function handleDelete() {
    const name = goal.name;
    deleteGoal.mutate(goal.id, {
      onSuccess: () => {
        onDeleted();
        toast.undo(t("Цель «{name}» удалена.", { name }), () => {
          restoreGoal.mutate(goal.id, {
            onSuccess: () => toast.success(t("Цель «{name}» восстановлена.", { name })),
            onError: (error) =>
              toastMutationError(error, t("Не получилось восстановить. Попробуйте ещё раз.")),
          });
        });
      },
      onError: (error) =>
        toastMutationError(error, t("Не получилось удалить. Попробуйте ещё раз.")),
    });
  }

  const progress =
    goal.target_amount > 0
      ? Math.min(100, Math.round((goal.current_amount / goal.target_amount) * 100))
      : 0;
  const overdue = Boolean(goal.deadline) && new Date(goal.deadline!) < new Date() && progress < 100;
  const amounts = formatMoneyPair(goal.current_amount, goal.target_amount);
  const categoryLabel = GOAL_CATEGORY_LABEL[goal.category];

  return (
    <li className="fp-goal-row">
      <div className="fp-goal-row__head">
        <span className="fp-goal-row__name">{goal.name}</span>
        <SharedBadge householdId={goal.household_id} />
        {goal.deadline && (
          <span className="fp-goal-row__deadline">
            {formatDate(goal.deadline)}
            {overdue && (
              <span className="fp-goal-row__overdue">
                {NBSP}· {t("срок прошёл")}
              </span>
            )}
          </span>
        )}
      </div>
      {categoryLabel && <p className="fp-goal-row__category">{categoryLabel}</p>}
      <p className="fp-goal-row__amounts">
        <span className="fp-goal-row__amount-current">{amounts.current}</span>
        <span className="fp-goal-row__amount-secondary">
          {t("из {target} ₽ ({pct}%)", { target: amounts.target, pct: progress })}
        </span>
      </p>
      <div
        className="fp-goal-row__bar"
        role="progressbar"
        aria-valuenow={progress}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={t("Прогресс цели «{name}»", { name: goal.name })}
      >
        <div className="fp-goal-row__bar-fill" style={{ width: `${progress}%` }} />
      </div>
      {isLinkedToAsset && (
        <p className="fp-goal-row__linked-hint">
          {t("Прогресс выводится из баланса привязанного актива.")}
        </p>
      )}
      <div className="fp-goal-row__actions">
        <Button variant="ghost" onClick={onEdit}>
          {t("Изменить")}
        </Button>
        {!isLinkedToAsset && (
          <Button variant="primary" onClick={onContribute}>
            {t("Внести прогресс")}
          </Button>
        )}
        <Button
          variant="danger"
          onClick={handleDelete}
          disabled={deleteGoal.isPending}
          aria-label={t("Удалить «{name}»", { name: goal.name })}
        >
          {deleteGoal.isPending ? t("Удаляем…") : t("Удалить")}
        </Button>
      </div>
    </li>
  );
}
