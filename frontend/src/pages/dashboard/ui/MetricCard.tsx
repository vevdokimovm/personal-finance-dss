import type { ReactNode } from "react";

export interface MetricCardProps {
  name: string;
  badge?: ReactNode;
  badgeVariant?: "warn" | "muted";
  value: string;
  caption: string;
}

export function MetricCard({
  name,
  badge,
  badgeVariant = "muted",
  value,
  caption,
}: MetricCardProps) {
  return (
    <article className="fp-metric-card">
      <div className="fp-metric-head">
        <span className="fp-metric-name">{name}</span>
        {badge && (
          <span className={`fp-metric-badge fp-metric-badge--${badgeVariant}`}>{badge}</span>
        )}
      </div>
      <div className="fp-metric-value">{value}</div>
      <div className="fp-metric-caption">{caption}</div>
    </article>
  );
}
