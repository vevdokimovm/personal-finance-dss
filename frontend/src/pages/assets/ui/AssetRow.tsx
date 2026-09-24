import { formatMoney, formatPercent } from "@shared/lib/money/formatMoney";
import { t } from "@shared/lib/i18n/t";
import { Button, toast } from "@shared/ui";
import { useDeleteAsset, useRestoreAsset, type LiquidAsset } from "@entities/assets";
import { SharedBadge } from "@features/household-scope";
import { toastMutationError } from "@entities/auth";

const TYPE_LABELS: Record<string, string> = {
  deposit: "Депозит",
  savings_account: "Накопительный счёт",
  cash: "Кэш",
};

export function AssetRow({
  asset,
  onEdit,
  onDeleted,
}: {
  asset: LiquidAsset;
  onEdit: () => void;
  /** Фокус после удаления строки иначе проваливается в `<body>` (a11y-auditor, Батч 1,
   * WCAG 2.4.3) — та же находка, что в ObligationRow.tsx. */
  onDeleted: () => void;
}) {
  const deleteAsset = useDeleteAsset();
  const restoreAsset = useRestoreAsset();

  function handleDelete() {
    const name = asset.name;
    deleteAsset.mutate(asset.id, {
      onSuccess: () => {
        onDeleted();
        toast.undo(t("Актив «{name}» удалён.", { name }), () => {
          restoreAsset.mutate(asset.id, {
            onSuccess: () => toast.success(t("Актив «{name}» восстановлен.", { name })),
            onError: (error) =>
              toastMutationError(error, t("Не получилось восстановить. Попробуйте ещё раз.")),
          });
        });
      },
      onError: (error) =>
        toastMutationError(error, t("Не получилось удалить. Попробуйте ещё раз.")),
    });
  }

  return (
    <li className="fp-asset-row">
      <div className="fp-asset-row__main">
        <span className="fp-asset-row__name">{asset.name}</span>
        <SharedBadge householdId={asset.household_id} />
        <span className="fp-asset-row__type">{TYPE_LABELS[asset.type] ?? asset.type}</span>
      </div>
      <span className="fp-asset-row__rate">
        {/* interest_rate — доля (0.14 = 14%), как в ObligationResponse (Numeric(6,4) в обеих
            таблицах, app/database/models.py) — НЕ проценты, несмотря на то что старая Jinja-форма
            брала ввод 0-100 (конвертация была на стороне формы/роута, не в хранимых данных).
            «годовых» видимо, не только sr-only (design-critic, Батч 1) — рядом с денежной суммой
            голое число легко прочитать как долю портфеля. */}
        {formatPercent(asset.interest_rate)}{" "}
        <span className="fp-asset-row__rate-unit">{t("годовых")}</span>
      </span>
      <span className="fp-asset-row__amount">{formatMoney(asset.amount)}</span>
      <div className="fp-asset-row__actions">
        <Button variant="ghost" onClick={onEdit}>
          {t("Изменить")}
        </Button>
        <Button
          variant="danger"
          onClick={handleDelete}
          disabled={deleteAsset.isPending}
          aria-label={t("Удалить «{name}»", { name: asset.name })}
        >
          {deleteAsset.isPending ? t("Удаляем…") : t("Удалить")}
        </Button>
      </div>
    </li>
  );
}
