import type { ReactNode } from "react";

export interface MetricCardProps {
  name: string;
  badge?: ReactNode;
  badgeVariant?: "warn" | "danger" | "muted";
  /** Цвет самого числа. По умолчанию — цвет бейджа (badgeVariant), можно
   * задать отдельно (напр. бейдж нейтральный, а число уже в зоне внимания). */
  valueVariant?: "warn" | "danger" | "none";
  value: string;
  caption: string;
}

export function MetricCard({
  name,
  badge,
  badgeVariant = "muted",
  valueVariant,
  value,
  caption,
}: MetricCardProps) {
  const resolvedValueVariant =
    valueVariant ?? (badgeVariant === "warn" || badgeVariant === "danger" ? badgeVariant : "none");
  return (
    <article className="fp-metric-card">
      <div className="fp-metric-head">
        <span className="fp-metric-name">{name}</span>
        {badge && (
          <span className={`fp-metric-badge fp-metric-badge--${badgeVariant}`}>{badge}</span>
        )}
      </div>
      <div
        className={
          resolvedValueVariant === "none"
            ? "fp-metric-value"
            : `fp-metric-value fp-metric-value--${resolvedValueVariant}`
        }
      >
        {value}
      </div>
      <div className="fp-metric-caption">{caption}</div>
    </article>
  );
}
