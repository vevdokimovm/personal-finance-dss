import { MetricCard } from "./MetricCard";
import { formatNumber, formatPercent } from "@shared/lib/money/formatMoney";
import { t } from "@shared/lib/i18n/t";
import { DTI_THRESHOLD, DTI_WARN_THRESHOLD } from "@entities/plan-summary";
import type { PlanIndicators } from "@entities/plan-summary";
import "./MetricsGrid.css";

// Ликвидность и «подушка» — МЯГКИЕ критерии канона (L_min=0 по умолчанию
// выключен, docs/math_model.md: "отсев по ликвидности мягкий").
// Поэтому здесь только warn (внимание), никогда danger — danger означал бы
// нарушение жёсткого инварианта, которого канон для этих метрик не задаёт.
const RUNWAY_WARN_THRESHOLD = 1;

export function MetricsGrid({ indicators }: { indicators: PlanIndicators }) {
  const ltRisk = indicators.Lt < RUNWAY_WARN_THRESHOLD;
  const dtiGap = ((DTI_THRESHOLD - indicators.Dt) * 100).toFixed(1);
  const dtiVariant: "danger" | "warn" | "muted" =
    indicators.Dt > DTI_THRESHOLD
      ? "danger"
      : indicators.Dt > DTI_WARN_THRESHOLD
        ? "warn"
        : "muted";
  const blrRisk = indicators.BLR != null && indicators.BLR < RUNWAY_WARN_THRESHOLD;

  return (
    <section className="fp-metrics" aria-label={t("Ключевые показатели")}>
      <MetricCard
        name={t("Ликвидность")}
        badge={ltRisk ? t("{n} мес. автономии", { n: formatNumber(indicators.Lt) }) : undefined}
        badgeVariant={ltRisk ? "warn" : "muted"}
        value={formatNumber(indicators.Lt)}
        caption={t("Месяцев жизни на свободном резерве (stock-based, B_liq/E).")}
      />
      <MetricCard
        name={t("Долговая нагрузка (ПДН)")}
        badge={
          dtiVariant === "danger"
            ? t("превышен порог 40%")
            : dtiVariant === "warn"
              ? t("порог 40%, близко")
              : t("порог 40%")
        }
        badgeVariant={dtiVariant}
        value={formatPercent(indicators.Dt)}
        caption={t("Доля дохода на кредиты. Запас {gap} п.п. до порога.", { gap: dtiGap })}
      />
      <MetricCard
        name={t("Подушка со всеми накоплениями")}
        badge={blrRisk ? t("мало") : t("включая цели")}
        badgeVariant={blrRisk ? "warn" : "muted"}
        value={indicators.BLR != null ? formatNumber(indicators.BLR) : "—"}
        caption={t("Месяцев без дохода, если использовать все текущие накопления.")}
      />
    </section>
  );
}
