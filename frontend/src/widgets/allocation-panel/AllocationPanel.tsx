import { formatMoney } from "@shared/lib/money/formatMoney";
import { t } from "@shared/lib/i18n/t";
import type { PlanAlternative } from "@entities/plan-summary";
import "@shared/ui/panel.css";
import "./AllocationPanel.css";

/** Цвета по смыслу — как в текущем frontend/static/js/app.js (renderAllocationBar):
 * долг = red, резерв = amber, цели = green. Не только цветом (A11Y-07) — везде есть текст.
 *
 * best=null — дефицит (top3 пуст): алгоритм не молчит, а явно объясняет, что рекомендации
 * нет (fail-loud), не отдельная ветка на каждой странице — используется и на dashboard,
 * и на planning (Э4 партия 2), чтобы текст не разошёлся между ними. */
export function AllocationPanel({ best }: { best: PlanAlternative | null }) {
  if (!best) {
    return (
      <section className="fp-panel">
        <h2>{t("Плана распределения нет")}</h2>
        <p className="fp-lede">
          {t(
            "Расходы и платежи превышают доход — свободных денег не остаётся, и алгоритм не выдаёт рекомендацию (fail-loud), а не молчит об этом.",
          )}
        </p>
      </section>
    );
  }

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
      <div className="fp-alloc-bar" role="presentation">
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
