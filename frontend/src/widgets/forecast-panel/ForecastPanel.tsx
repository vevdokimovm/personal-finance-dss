import {
  Area,
  AreaChart,
  CartesianGrid,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { formatMoney } from "@shared/lib/money/formatMoney";
import { t } from "@shared/lib/i18n/t";
import type { ForecastResult } from "@entities/plan-summary";
import { buildForecastChartData } from "./buildForecastChartData";
import "@shared/ui/panel.css";
import "./ForecastPanel.css";

export function ForecastPanel({ forecast }: { forecast: ForecastResult }) {
  const chartData = buildForecastChartData(forecast);
  const last = chartData[chartData.length - 1];
  // Диапазон в подвале — только если API реально дал p10/p90 для последней
  // точки (не coalesced-заглушка buildForecastChartData: там ?? Rt подменяет
  // отсутствующий интервал нулевой шириной для стека графика, но в текстовом
  // подвале показывать "диапазон X-X" при фактическом отсутствии интервала
  // было бы вводящим в заблуждение — как и раньше, просто скрываем строку).
  const lastRaw = forecast.forecast[forecast.forecast.length - 1];
  const hasRange = lastRaw != null && lastRaw.Rt_p10 != null && lastRaw.Rt_p90 != null;

  return (
    <section className="fp-panel">
      <h2>{t("Прогноз резерва на {h} месяцев", { h: forecast.horizon })}</h2>
      <p className="fp-lede">
        {t("SES + Monte-Carlo, интервал 80% (p10–p90) вокруг медианного сценария.")}
      </p>

      {/* График декоративный (aria-hidden) — та же информация в таблице ниже полностью,
          не только последняя точка (WCAG 1.1.1, находка a11y-auditor №2). */}
      <div className="fp-forecast-chart" aria-hidden="true">
        <ResponsiveContainer>
          <AreaChart data={chartData} margin={{ top: 8, right: 8, bottom: 0, left: 0 }}>
            <CartesianGrid stroke="var(--c-border)" vertical={false} />
            <XAxis
              dataKey="period"
              tickFormatter={(v: number) => (v === 0 ? t("сейчас") : t("{n} мес", { n: v }))}
              tick={{ fill: "var(--c-text3)", fontSize: 11 }}
              axisLine={{ stroke: "var(--c-border)" }}
              tickLine={false}
            />
            <YAxis
              tick={{ fill: "var(--c-text3)", fontSize: 11 }}
              axisLine={false}
              tickLine={false}
              tickFormatter={(v: number) => formatMoney(v)}
              width={72}
            />
            <Tooltip
              // Только медиана (Rt) — p10/полоса служебные, полный диапазон
              // уже есть в table.sr-only ниже (aria-hidden на самом графике).
              formatter={(value, _name, entry) =>
                entry?.dataKey === "Rt" ? formatMoney(Number(value)) : ""
              }
              labelFormatter={(label) =>
                label === 0 ? t("сейчас") : t("{n} мес", { n: Number(label) })
              }
              contentStyle={{
                background: "var(--c-surface-up)",
                border: "var(--border-w) solid var(--c-border-hl)",
                borderRadius: "var(--r-sm)",
              }}
            />
            <Area
              type="monotone"
              dataKey="Rt_p10"
              stackId="range"
              stroke="none"
              fill="none"
              legendType="none"
              isAnimationActive={false}
            />
            <Area
              type="monotone"
              dataKey="Rt_band"
              stackId="range"
              stroke="none"
              fill="var(--c-accent-bg)"
              legendType="none"
              isAnimationActive={false}
            />
            <Line
              type="monotone"
              dataKey="Rt"
              stroke="var(--c-accent)"
              strokeWidth={2.5}
              dot={false}
              isAnimationActive={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <table className="sr-only">
        <caption>
          {t("Помесячный прогноз резерва — медиана и диапазон 80% (p10–p90) по каждому месяцу")}
        </caption>
        <thead>
          <tr>
            <th scope="col">{t("Месяц")}</th>
            <th scope="col">{t("Медиана")}</th>
            <th scope="col">{t("p10")}</th>
            <th scope="col">{t("p90")}</th>
          </tr>
        </thead>
        <tbody>
          {chartData.map((p) => (
            <tr key={p.period}>
              <td>{p.period === 0 ? t("сейчас") : t("{n} мес", { n: p.period })}</td>
              <td>{formatMoney(p.Rt)}</td>
              <td>{formatMoney(p.Rt_p10)}</td>
              <td>{formatMoney(p.Rt_p90)}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {last && (
        <div className="fp-forecast-foot">
          <span>
            {t("Медиана к {h} мес: {v}", { h: forecast.horizon, v: formatMoney(last.Rt) })}
          </span>
          {hasRange && (
            <span>
              {t("Диапазон (80%): {lo} – {hi}", {
                lo: formatMoney(last.Rt_p10),
                hi: formatMoney(last.Rt_p90),
              })}
            </span>
          )}
        </div>
      )}
    </section>
  );
}
