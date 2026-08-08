import clsx from "clsx";
import { t } from "@shared/lib/i18n/t";
import "./skeleton.css";
import "./ListSkeleton.css";

/** Скелетон списка (N строк-заглушек) — общий для транзакций/обязательств/целей (Э4),
 * тот же shimmer-паттерн, что DashboardSkeleton (fp-skeleton, prefers-reduced-motion). */
export function ListSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <div role="status" aria-hidden="false">
      <span className="sr-only">{t("Загрузка списка…")}</span>
      <div className="fp-list-skeleton" aria-hidden="true">
        {Array.from({ length: rows }, (_, i) => (
          <div key={i} className="fp-list-skeleton__row">
            <div className={clsx("fp-skeleton", "fp-skel-row-primary")} />
            <div className={clsx("fp-skeleton", "fp-skel-row-secondary")} />
          </div>
        ))}
      </div>
    </div>
  );
}
