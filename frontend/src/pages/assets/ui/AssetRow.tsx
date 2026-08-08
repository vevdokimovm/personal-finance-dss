import { formatMoney, formatPercent } from "@shared/lib/money/formatMoney";
import { t } from "@shared/lib/i18n/t";
import type { LiquidAsset } from "@entities/assets";

const TYPE_LABELS: Record<string, string> = {
  deposit: "Депозит",
  savings_account: "Накопительный счёт",
  cash: "Кэш",
};

export function AssetRow({ asset }: { asset: LiquidAsset }) {
  return (
    <li className="fp-asset-row">
      <div className="fp-asset-row__main">
        <span className="fp-asset-row__name">{asset.name}</span>
        <span className="fp-asset-row__type">{TYPE_LABELS[asset.type] ?? asset.type}</span>
      </div>
      <span className="fp-asset-row__rate">
        {/* interest_rate — доля (0.14 = 14%), как в ObligationResponse (Numeric(6,4) в обеих
            таблицах, app/database/models.py) — НЕ проценты, несмотря на то что старая Jinja-форма
            брала ввод 0-100 (конвертация была на стороне формы/роута, не в хранимых данных). */}
        {formatPercent(asset.interest_rate)}
        <span className="sr-only">{t("годовых")}</span>
      </span>
      <span className="fp-asset-row__amount">{formatMoney(asset.amount)}</span>
    </li>
  );
}
