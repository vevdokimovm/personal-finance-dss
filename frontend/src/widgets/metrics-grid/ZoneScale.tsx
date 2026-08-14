export interface ZoneScaleZone {
  /** Верхняя граница зоны в единицах value (не %) — последняя зона тянется до max. */
  to: number;
  variant: "muted" | "warn" | "danger";
}

/**
 * Шкала с зонами (план вехи 8, Э5: «Месяцы автономии и ПДН — шкала с зонами»,
 * `frontend_milestone8_plan.md`). Чисто визуальное усиление уже доступного текстом числа
 * (крупное значение + бейдж в MetricCard рядом) — `aria-hidden`, как диаграмма Санкея в
 * AllocationPanel и график в ForecastPanel: то же число не дублируется в дереве доступности
 * дважды разными словами.
 */
export function ZoneScale({
  value,
  max,
  zones,
}: {
  value: number;
  max: number;
  zones: ZoneScaleZone[];
}) {
  const markerPct = (Math.min(Math.max(value, 0), max) / max) * 100;
  // reduce, не мутация счётчика в .map — react-hooks/immutability запрещает переприсваивать
  // внешнюю переменную внутри колбэка рендера (даже локальную, даже безопасную по факту).
  const segments = zones.reduce<{ from: number; to: number; variant: ZoneScaleZone["variant"] }[]>(
    (acc, zone) => [
      ...acc,
      {
        from: acc.length > 0 ? acc[acc.length - 1].to : 0,
        to: Math.min(zone.to, max),
        variant: zone.variant,
      },
    ],
    [],
  );

  return (
    <div className="fp-zone-scale" aria-hidden="true">
      <div className="fp-zone-scale__track">
        {segments.map((seg) => (
          <div
            key={seg.to}
            className={`fp-zone-scale__zone fp-zone-scale__zone--${seg.variant}`}
            style={{ width: `${Math.max(0, ((seg.to - seg.from) / max) * 100)}%` }}
          />
        ))}
      </div>
      <div className="fp-zone-scale__marker" style={{ left: `${markerPct}%` }} />
    </div>
  );
}
