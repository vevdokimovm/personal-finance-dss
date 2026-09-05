import { useEffect, useRef, useState } from "react";
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
import type { TooltipPayload } from "recharts/types/state/tooltipSlice";
import { formatMoney, formatNumber, formatPercent } from "@shared/lib/money/formatMoney";
import { t } from "@shared/lib/i18n/t";
import { Formula } from "@shared/ui";
import type { ForecastResult } from "@entities/plan-summary";
import { buildForecastChartData } from "./buildForecastChartData";
import { ForecastControls } from "./ForecastControls";
import "@shared/ui/panel.css";
import "./ForecastPanel.css";

/** Только поля, которые реально читаются — не родовой `TooltipContentProps<TValue,TName>`
 * (requires coordinate/accessibilityLayer/activeIndex и жёстко фиксирует generic-параметры,
 * которые `<Tooltip>` без явной аннотации выводит иначе — `tsc -b` в `npm run build` ловит
 * рассинхрон типов там, где обычный `tsc --noEmit` почему-то нет). */
interface ForecastTooltipProps {
  active?: boolean;
  payload?: TooltipPayload;
  label?: string | number;
}

/** Recharts по умолчанию рисует одну строку тултипа НА КАЖДУЮ серию графика (три Area/Line
 * ниже — Rt/Rt_band/Rt_p10, две служебные для стека закраски диапазона) — сырые имена
 * `dataKey` утекали в интерфейс как есть («Rt_band :», «Rt_p10 :» пустой строкой), потому
 * что прежний `formatter` умел спрятать только ЗНАЧЕНИЕ строки, не саму строку. Полный
 * диапазон уже есть в `table.sr-only` ниже — здесь показываем только медиану, одной строкой. */
export function ForecastTooltip({ active, payload, label }: ForecastTooltipProps) {
  if (!active) return null;
  const point = payload?.find((p) => p.dataKey === "Rt");
  if (!point || point.value == null) return null;
  return (
    <div className="fp-forecast-tooltip">
      <p className="fp-forecast-tooltip__label">
        {label === 0 ? t("сейчас") : t("{n} мес", { n: Number(label) })}
      </p>
      <p className="fp-forecast-tooltip__value">
        <span className="fp-forecast-tooltip__symbol">
          <Formula tex="R_t" fallback="Rt" />
        </span>
        {" = "}
        {formatMoney(Number(point.value))}
      </p>
    </div>
  );
}

/** `horizon`/`onHorizonChange`/`rBench`/`onRBenchChange` необязательны — без них (дашборд,
 * свёрнутая карточка Э3) панель просто показывает прогноз без контролов. С ними (страница
 * планирования, §8.4) появляется `ForecastControls` — управляемые горизонт+ставка живут у
 * вызывающего (тот же владелец, что `useForecast`), панель их не хранит. */
export function ForecastPanel({
  forecast,
  horizon,
  onHorizonChange,
  rBench,
  onRBenchChange,
  isFetching = false,
}: {
  forecast: ForecastResult;
  horizon?: number;
  onHorizonChange?: (horizon: number) => void;
  rBench?: number;
  onRBenchChange?: (rBench: number | undefined) => void;
  isFetching?: boolean;
}) {
  const chartData = buildForecastChartData(forecast);
  const last = chartData[chartData.length - 1];
  // Диапазон в подвале — только если API реально дал p10/p90 для последней
  // точки (не coalesced-заглушка buildForecastChartData: там ?? Rt подменяет
  // отсутствующий интервал нулевой шириной для стека графика, но в текстовом
  // подвале показывать "диапазон X-X" при фактическом отсутствии интервала
  // было бы вводящим в заблуждение — как и раньше, просто скрываем строку).
  const lastRaw = forecast.forecast[forecast.forecast.length - 1];
  const hasRange = lastRaw != null && lastRaw.Rt_p10 != null && lastRaw.Rt_p90 != null;
  const showControls = onHorizonChange != null && onRBenchChange != null;
  const isOverridden = forecast.r_bench_source === "request";

  return (
    <section className="fp-panel">
      <h2>{t("Прогноз резерва на {h} месяцев", { h: forecast.horizon })}</h2>
      <p className="fp-lede">
        {t("SES + Monte-Carlo, интервал 80% (p10–p90) вокруг медианного сценария.")}
      </p>
      {/* Без этой строки единственный признак того, что график больше не считает по реальной
       * ставке — появление кнопки «Сбросить» под ползунком в другом месте экрана (design-critic,
       * правило 7: условная информация не держится на одном слабом признаке). */}
      {isOverridden && (
        <p className="fp-lede">
          {t("Сценарий «что если»: график посчитан со ставкой {v}, не решение СППР.", {
            v: formatPercent(forecast.r_bench),
          })}
        </p>
      )}

      {/* 🔴 Предупреждение о дефиците — самое важное, что прогноз умеет сказать, и до
          v8.51.0 оно не показывалось нигде: поле считалось на бэкенде и лежало
          в контракте (аудит independent-expert 05.09.2026). Стоит ДО графика: человек,
          у которого через четыре месяца не хватит денег, должен узнать об этом раньше,
          чем начнёт разглядывать коридор. */}
      {forecast.deficit_alert && (
        <p className="fp-forecast__deficit" role="alert">
          {forecast.deficit_alert.pessimistic
            ? t(
                "При неблагоприятном сценарии на {n}-м месяце не хватит {gap}. " +
                  "В основном прогнозе дефицита нет — это нижняя граница интервала.",
                {
                  n: formatNumber(forecast.deficit_alert.period, 0),
                  gap: formatMoney(forecast.deficit_alert.gap),
                },
              )
            : t("На {n}-м месяце денег не хватит: разрыв {gap}.", {
                n: formatNumber(forecast.deficit_alert.period, 0),
                gap: formatMoney(forecast.deficit_alert.gap),
              })}
        </p>
      )}

      {showControls && (
        <ForecastControls
          horizon={horizon ?? forecast.horizon}
          onHorizonChange={onHorizonChange}
          rBench={rBench}
          onRBenchChange={onRBenchChange}
          realRBench={forecast.real_r_bench}
          isOverridden={isOverridden}
          isFetching={isFetching}
        />
      )}
      {/* Компонент-обёртка с хуками отдельно от ForecastPanel: ForecastPanel.test.tsx вызывает
       * ForecastPanel(...) напрямую как функцию (не через render()), чтобы прочитать дерево
       * <Area> без ResizeObserver — хуки в самом ForecastPanel сломали бы этот приём. JSX-ссылка
       * на дочерний компонент безопасна: React вызывает его функцию только при реальном
       * рендере/монтировании, которого в том тесте нет. */}
      {showControls && <ForecastResultAnnouncer forecast={forecast} lastMedian={last?.Rt} />}

      {/* График декоративный (aria-hidden) — та же информация в таблице ниже полностью,
          не только последняя точка (WCAG 1.1.1, находка a11y-auditor №2).

          🔴 `inert` обязателен рядом с `aria-hidden`: Recharts вставляет внутрь
          фокусируемые узлы, и один `aria-hidden` создавал ловушку — Tab уводил фокус
          в элемент, о котором скринридер молчит, и человек терял позицию на странице
          (WCAG 4.1.2, axe `aria-hidden-focus`). `inert` вынимает поддерево из порядка
          обхода целиком. Найдено axe-тиром `full`, когда он впервые реально исполнился
          (v8.45.0): до этого браузера нужной версии не было, и тир молча не запускался. */}
      <div className="fp-forecast-chart" aria-hidden="true" inert>
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
            <Tooltip content={ForecastTooltip} />
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

/** Живая область объявляет ГОТОВЫЙ результат после пересчёта (a11y-auditor: `ForecastControls`
 * объявляет только факт «идёт пересчёт», после завершения область немела — цифры узнать можно
 * было только вручную дойдя до таблицы/подвала). Тот же паттерн debounce, что
 * `WhatIfSliders.describeResult` — не на первом рендере (иначе объявляет саму загрузку страницы,
 * которую и так видно), с задержкой, чтобы не диктовать каждое промежуточное значение при
 * протяжке ползунка, только устоявшийся итог. */
function ForecastResultAnnouncer({
  forecast,
  lastMedian,
}: {
  forecast: ForecastResult;
  lastMedian: number | undefined;
}) {
  const isFirstRender = useRef(true);
  const [announced, setAnnounced] = useState("");

  useEffect(() => {
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }
    const timer = setTimeout(() => {
      setAnnounced(
        lastMedian != null
          ? t("Прогноз обновлён: медиана к {h} мес — {v}.", {
              h: forecast.horizon,
              v: formatMoney(lastMedian),
            })
          : "",
      );
    }, 300);
    return () => clearTimeout(timer);
  }, [forecast, lastMedian]);

  return (
    <p className="sr-only" role="status" aria-live="polite">
      {announced}
    </p>
  );
}
