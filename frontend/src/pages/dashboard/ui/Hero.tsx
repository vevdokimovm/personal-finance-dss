import { Button } from "@shared/ui";
import { formatMoney } from "@shared/lib/money/formatMoney";
import { t } from "@shared/lib/i18n/t";
import type { CalculatePlanResult } from "@entities/plan-summary";

export function Hero({ plan }: { plan: CalculatePlanResult }) {
  const { indicators, input_summary } = plan;
  return (
    <section className="fp-hero">
      <div className="fp-eyebrow">{t("Свободные деньги в этом месяце")}</div>
      <div className="fp-hero-value">{formatMoney(indicators.Rt)}</div>
      <p className="fp-hero-sub">
        {t(
          "Столько остаётся после доходов, обязательных расходов и платежей по кредитам. План ниже показывает, куда эти деньги пойдут.",
        )}
      </p>
      <div className="fp-hero-stats">
        <div>
          <span className="fp-hero-stat-label">{t("Доходы")}</span>
          <span className="fp-hero-stat-value">{formatMoney(input_summary.income)}</span>
        </div>
        <div>
          <span className="fp-hero-stat-label">{t("Расходы")}</span>
          <span className="fp-hero-stat-value">{formatMoney(input_summary.expense)}</span>
        </div>
        <div>
          <span className="fp-hero-stat-label">{t("Платежи по кредитам")}</span>
          <span className="fp-hero-stat-value">{formatMoney(indicators.SigmaP ?? 0)}</span>
        </div>
      </div>
      <Button asChild variant="primary" className="fp-hero-cta">
        <a href="/planning">{t("Построить план распределения →")}</a>
      </Button>
    </section>
  );
}
