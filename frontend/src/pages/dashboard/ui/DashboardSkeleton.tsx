import clsx from "clsx";
import { t } from "@shared/lib/i18n/t";
import "@shared/ui/skeleton.css";

/** Загрузка — TOK-06/A11Y-09: скелетон, не спиннер; уважает prefers-reduced-motion (см. CSS).
 * role="status" (не aria-live на узле с уже готовым содержимым при монтировании) — надёжнее
 * озвучивается NVDA/JAWS в связке с большинством браузеров (a11y-auditor, находка №5). */
export function DashboardSkeleton() {
  return (
    <main className="fp-dashboard">
      <h1 className="sr-only">{t("Финансовый обзор")}</h1>
      <div role="status">
        <span className="sr-only">{t("Загрузка обзора…")}</span>
      </div>
      <div className="fp-hero" aria-hidden="true">
        <div className={clsx("fp-skeleton", "fp-skel-eyebrow")} />
        <div className={clsx("fp-skeleton", "fp-skel-hero-value")} />
        <div className={clsx("fp-skeleton", "fp-skel-hero-sub")} />
      </div>
      <div className="fp-metrics" aria-hidden="true">
        {[0, 1, 2].map((i) => (
          <div key={i} className="fp-metric-card">
            <div className={clsx("fp-skeleton", "fp-skel-metric-label")} />
            <div className={clsx("fp-skeleton", "fp-skel-metric-value")} />
          </div>
        ))}
      </div>
      {/* Заглушки под AllocationPanel и ForecastPanel — без них loading короче
          loaded и страница «прыгает» на их высоту при появлении данных. */}
      <div className="fp-panel" aria-hidden="true">
        <div className={clsx("fp-skeleton", "fp-skel-panel-title")} />
        <div className={clsx("fp-skeleton", "fp-skel-panel-lede")} />
        <div className={clsx("fp-skeleton", "fp-skel-alloc-bar")} />
      </div>
      <div className="fp-panel" aria-hidden="true">
        <div className={clsx("fp-skeleton", "fp-skel-panel-title")} />
        <div className={clsx("fp-skeleton", "fp-skel-panel-lede")} />
        <div className={clsx("fp-skeleton", "fp-skel-chart")} />
      </div>
    </main>
  );
}
