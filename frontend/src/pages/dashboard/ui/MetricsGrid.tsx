import { MetricCard } from "./MetricCard";
import { formatNumber, formatPercent } from "@shared/lib/money/formatMoney";
import { t } from "@shared/lib/i18n/t";
import type { PlanIndicators } from "@entities/plan-summary";

const DTI_THRESHOLD = 0.4;

export function MetricsGrid({ indicators }: { indicators: PlanIndicators }) {
  const ltRisk = indicators.Lt < 1;
  const dtiGap = ((DTI_THRESHOLD - indicators.Dt) * 100).toFixed(1);

  return (
    <section className="fp-metrics">
      <MetricCard
        name={t("Ликвидность")}
        badge={ltRisk ? t("{n} мес. автономии", { n: formatNumber(indicators.Lt) }) : undefined}
        badgeVariant="warn"
        value={formatNumber(indicators.Lt)}
        caption={t("Месяцев жизни на свободном резерве (stock-based, B_liq/E).")}
      />
      <MetricCard
        name={t("Долговая нагрузка (ПДН)")}
        badge={t("порог 40%")}
        value={formatPercent(indicators.Dt)}
        caption={t("Доля дохода на кредиты. Запас {gap} п.п. до порога.", { gap: dtiGap })}
      />
      <MetricCard
        name={t("Подушка со всеми накоплениями")}
        badge={t("включая цели")}
        value={indicators.BLR != null ? formatNumber(indicators.BLR) : "—"}
        caption={t("Месяцев без дохода, если использовать все текущие накопления.")}
      />
    </section>
  );
}
