import { formatMoney } from "@shared/lib/money/formatMoney";
import { t } from "@shared/lib/i18n/t";
import type { PlanAlternative } from "@entities/plan-summary";

/** Цвета по смыслу — как в текущем frontend/static/js/app.js (renderAllocationBar):
 * долг = red, резерв = amber, цели = green. Не только цветом (A11Y-07) — везде есть текст. */
export function AllocationPanel({ best }: { best: PlanAlternative }) {
  const total = best.x_obligations + best.x_reserve + best.x_goals;
  const pct = (value: number) => (total > 0 ? Math.round((value / total) * 100) : 0);

  return (
    <section className="fp-panel">
      <h2>{t("Куда пойдут свободные деньги")}</h2>
      <p className="fp-lede">
        {t("Рекомендация СППР ({name}), полезность U = {u}.", {
          name: best.name,
          u: best.utility.toFixed(2),
        })}
      </p>
      <div className="fp-alloc-bar">
        {best.x_obligations > 0 && (
          <div style={{ flex: pct(best.x_obligations), background: "var(--c-red)" }} />
        )}
        {best.x_reserve > 0 && (
          <div style={{ flex: pct(best.x_reserve), background: "var(--c-amber)" }} />
        )}
        {best.x_goals > 0 && (
          <div style={{ flex: pct(best.x_goals), background: "var(--c-green)" }} />
        )}
      </div>
      <div className="fp-alloc-legend">
        <span>
          <i className="fp-dot" style={{ background: "var(--c-red)" }} />
          {t("Досрочное погашение — {sum} ({pct}%)", {
            sum: formatMoney(best.x_obligations),
            pct: pct(best.x_obligations),
          })}
        </span>
        <span>
          <i className="fp-dot" style={{ background: "var(--c-amber)" }} />
          {t("Резерв — {sum} ({pct}%)", {
            sum: formatMoney(best.x_reserve),
            pct: pct(best.x_reserve),
          })}
        </span>
        <span>
          <i className="fp-dot" style={{ background: "var(--c-green)" }} />
          {t("Цели — {sum} ({pct}%)", { sum: formatMoney(best.x_goals), pct: pct(best.x_goals) })}
        </span>
      </div>
    </section>
  );
}
