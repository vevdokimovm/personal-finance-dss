import { MetricCard } from "./MetricCard";
import { ZoneScale } from "./ZoneScale";
import { formatNumber, formatPercent } from "@shared/lib/money/formatMoney";
import { t } from "@shared/lib/i18n/t";
import { Formula } from "@shared/ui";
import {
  DTI_THRESHOLD,
  DTI_WARN_THRESHOLD,
  DTI_LEGAL_DISCLAIMER_THRESHOLD,
} from "@entities/plan-summary";
import type { PlanIndicators } from "@entities/plan-summary";
import "./MetricsGrid.css";

// Ликвидность и «подушка» — МЯГКИЕ критерии канона (L_min=0 по умолчанию
// выключен, docs/math_model.md: "отсев по ликвидности мягкий").
// Поэтому здесь только warn (внимание), никогда danger — danger означал бы
// нарушение жёсткого инварианта, которого канон для этих метрик не задаёт.
const RUNWAY_WARN_THRESHOLD = 1;
// Верхняя граница шкалы автономии — канон не даёт точного потолка для Lt (в отличие от
// DTI_THRESHOLD), только качественный ориентир BLR «>6 избыток» (docs/math_model.md §3.5,
// норма Greninger 1996); используем то же число как разумный масштаб шкалы, не жёсткий порог.
const RUNWAY_SCALE_MAX = 6;
const DTI_SCALE_MAX = 0.6;

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
  const dtiLegalDisclaimer = indicators.Dt > DTI_LEGAL_DISCLAIMER_THRESHOLD;

  return (
    <section className="fp-metrics" aria-label={t("Ключевые показатели")}>
      <MetricCard
        name={t("Ликвидность")}
        badge={ltRisk ? t("{n} мес. автономии", { n: formatNumber(indicators.Lt) }) : undefined}
        badgeVariant={ltRisk ? "warn" : "muted"}
        value={formatNumber(indicators.Lt)}
        caption={
          <>
            <ZoneScale
              value={indicators.Lt}
              max={RUNWAY_SCALE_MAX}
              zones={[
                { to: RUNWAY_WARN_THRESHOLD, variant: "warn" },
                { to: RUNWAY_SCALE_MAX, variant: "muted" },
              ]}
            />
            {t("Месяцев без дохода, если использовать только свободный резерв (без целей).")}
            <span className="fp-metric-caption__formula">
              <Formula tex="L_t = \dfrac{B_{liq}}{\sum e}" fallback="Lt = Bliq / Σe" />
            </span>
          </>
        }
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
        caption={
          <>
            <ZoneScale
              value={indicators.Dt}
              max={DTI_SCALE_MAX}
              zones={[
                { to: DTI_WARN_THRESHOLD, variant: "muted" },
                { to: DTI_THRESHOLD, variant: "warn" },
                { to: DTI_SCALE_MAX, variant: "danger" },
              ]}
            />
            {t("Доля дохода на кредиты. Запас {gap} п.п. до порога.", { gap: dtiGap })}
            <span className="fp-metric-caption__formula">
              <Formula tex="D_t = \dfrac{\sum P}{I}" fallback="Dt = ΣP / I" />
            </span>
            {/* 601-ФЗ (с 01.01.2024): кредитор обязан письменно уведомить о рисках при ПДН
             * выше 50% — план вехи 8, Э5 требует спокойный дисклеймер на экране, не только
             * бейдж «превышен порог 40%» (тот про модельный инвариант 0.40, юридический
             * порог — отдельное число 0.50, docs/frontend_milestone8_plan.md). */}
            {dtiLegalDisclaimer && (
              <p className="fp-metric-disclaimer">
                {t(
                  "Доля дохода на платежи по кредитам выше 50%. С 2024 года закон обязывает в такой ситуации письменно предупреждать о повышенном риске — это стандартное уведомление, не оценка вашей платёжеспособности.",
                )}
              </p>
            )}
          </>
        }
      />
      <MetricCard
        name={t("Подушка со всеми накоплениями")}
        badge={blrRisk ? t("мало") : t("включая цели")}
        badgeVariant={blrRisk ? "warn" : "muted"}
        value={indicators.BLR != null ? formatNumber(indicators.BLR) : "—"}
        caption={
          <>
            {t("Месяцев без дохода, если использовать все текущие накопления.")}
            <span className="fp-metric-caption__formula">
              <Formula
                tex="BLR = \dfrac{B_t + B_t^{liq}}{\sum e}"
                fallback="BLR = (Bt + Btliq) / Σe"
              />
            </span>
          </>
        }
      />
    </section>
  );
}
