import { formatMoney, formatPercent } from "@shared/lib/money/formatMoney";
import { t } from "@shared/lib/i18n/t";
import { Button, toast } from "@shared/ui";
import { useDeleteObligation, useRestoreObligation, type Obligation } from "@entities/obligations";
import { SharedBadge } from "@features/household-scope";

export function ObligationRow({
  obligation,
  onEdit,
  onDeleted,
}: {
  obligation: Obligation;
  onEdit: () => void;
  /** Фокус после удаления строки иначе проваливается в `<body>` (a11y-auditor, Батч 1,
   * WCAG 2.4.3) — строка исчезает из DOM вместе с кнопкой, на которой стоял фокус. */
  onDeleted: () => void;
}) {
  const deleteObligation = useDeleteObligation();
  const restoreObligation = useRestoreObligation();

  function handleDelete() {
    const name = obligation.name;
    deleteObligation.mutate(obligation.id, {
      onSuccess: () => {
        onDeleted();
        toast.undo(t("Обязательство «{name}» удалено.", { name }), () => {
          restoreObligation.mutate(obligation.id, {
            onSuccess: () => toast.success(t("Обязательство «{name}» восстановлено.", { name })),
            onError: () => toast.error(t("Не получилось восстановить. Попробуйте ещё раз.")),
          });
        });
      },
      onError: () => toast.error(t("Не получилось удалить. Попробуйте ещё раз.")),
    });
  }

  const progress =
    obligation.term > 0
      ? Math.min(100, Math.round((obligation.months_elapsed / obligation.term) * 100))
      : 0;
  return (
    <li className="fp-obligation-row">
      <div className="fp-obligation-row__head">
        <span className="fp-obligation-row__name">{obligation.name}</span>
        <SharedBadge householdId={obligation.household_id} />
        {/* Остаток долга — главное число строки (design-critic, Батч 1): форма делает его
            обязательным полем первого порядка, а строка списка его не показывала вообще —
            единственный способ проверить введённое число был открыть форму правки заново. */}
        <span className="fp-obligation-row__amount">{formatMoney(obligation.amount)}</span>
      </div>
      <div className="fp-obligation-row__meta">
        <span>
          {formatMoney(obligation.monthly_payment)}
          <span className="fp-obligation-row__payment-unit">{t("/мес")}</span>
        </span>
        <span>{formatPercent(obligation.interest_rate)}</span>
        <span>
          {t("{elapsed} из {term} мес.", {
            elapsed: obligation.months_elapsed,
            term: obligation.term,
          })}
        </span>
      </div>
      <div className="fp-obligation-row__bar" role="presentation">
        <div className="fp-obligation-row__bar-fill" style={{ width: `${progress}%` }} />
      </div>
      <div className="fp-obligation-row__actions">
        <Button variant="ghost" onClick={onEdit}>
          {t("Изменить")}
        </Button>
        <Button
          variant="danger"
          onClick={handleDelete}
          disabled={deleteObligation.isPending}
          aria-label={t("Удалить «{name}»", { name: obligation.name })}
        >
          {deleteObligation.isPending ? t("Удаляем…") : t("Удалить")}
        </Button>
      </div>
    </li>
  );
}
