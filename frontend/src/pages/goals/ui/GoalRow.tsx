import { formatMoney } from "@shared/lib/money/formatMoney";
import { formatDate } from "@shared/lib/date/formatDate";
import { t } from "@shared/lib/i18n/t";
import type { Goal } from "@entities/goals";

export function GoalRow({ goal }: { goal: Goal }) {
  const progress =
    goal.target_amount > 0
      ? Math.min(100, Math.round((goal.current_amount / goal.target_amount) * 100))
      : 0;
  return (
    <li className="fp-goal-row">
      <div className="fp-goal-row__head">
        <span className="fp-goal-row__name">{goal.name}</span>
        {goal.deadline && (
          <span className="fp-goal-row__deadline">{formatDate(goal.deadline)}</span>
        )}
      </div>
      <p className="fp-goal-row__amounts">
        {t("{current} из {target} ({pct}%)", {
          current: formatMoney(goal.current_amount),
          target: formatMoney(goal.target_amount),
          pct: progress,
        })}
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
    </li>
  );
}
