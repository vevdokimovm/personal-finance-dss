import { useState } from "react";
import { Layer, ResponsiveContainer, Sankey, Tooltip } from "recharts";
import type { SankeyLinkProps, SankeyNode, SankeyNodeProps } from "recharts";
import { formatMoney, formatNumber } from "@shared/lib/money/formatMoney";
import { t } from "@shared/lib/i18n/t";
import { Button } from "@shared/ui";
import type { PlanAlternative } from "@entities/plan-summary";
import { buildAllocationSankeyData } from "./buildAllocationSankeyData";
import {
  GRID_NOTCHES,
  findMatchingAlternative,
  hasNonZeroCategory,
  notchesOf,
} from "./findMatchingAlternative";
import { WhatIfSliders } from "./WhatIfSliders";
import "@shared/ui/panel.css";
import "./AllocationPanel.css";

type ColoredSankeyNode = SankeyNode & { color?: string };

// Recharts принимает margin только числом (px) — CSS-токен сюда не подставить. Значение
// подобрано под самую длинную подпись категории («Досрочное погашение», fontSize 11 в диаграмме),
// это метрика текста, а не отступ со шкалы --sp-*; синхронизировано с --chart-sankey-min-width
// в tokens.css (тот же множитель заложен и там).
const SANKEY_LABEL_MARGIN = 130;

/** Узел рисуется сам — дефолтный рендер recharts красит узлы магическим `#0088fe`
 * (запрещено правилом «только токены») и не подписывает их вовсе. */
// Источник — самый левый узел (align="justify" даёт исходную колонку слева, целевую справа),
// поэтому его подпись уходит НАРУЖУ влево, подписи целей — НАРУЖУ вправо (design-critic: было
// перепутано местами, обе подписи лежали поверх цветных лент в центре, а поля margin.left/right
// вокруг оставались пустыми).
function AllocationSankeyNode({ x, y, width, height, payload }: SankeyNodeProps) {
  const node = payload as ColoredSankeyNode;
  const isSource = node.color == null;
  return (
    <Layer>
      <rect x={x} y={y} width={width} height={height} fill={node.color ?? "var(--c-border-hl)"} />
      <text
        x={isSource ? x - 8 : x + width + 8}
        y={y + height / 2}
        textAnchor={isSource ? "end" : "start"}
        dominantBaseline="middle"
        fontSize={11}
        fill="var(--c-text2)"
      >
        {node.name}
      </text>
    </Layer>
  );
}

/** Связь красится цветом узла-цели (та же красный/жёлтый/зелёный семантика, что в fp-alloc-bar
 * выше) — дефолтный рендер recharts даёт магический `stroke: #333`. */
function AllocationSankeyLink({
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourceControlX,
  targetControlX,
  linkWidth,
  payload,
}: SankeyLinkProps) {
  const target = payload.target as ColoredSankeyNode;
  return (
    <path
      d={`M${sourceX},${sourceY} C${sourceControlX},${sourceY} ${targetControlX},${targetY} ${targetX},${targetY}`}
      fill="none"
      stroke={target.color ?? "var(--c-border-hl)"}
      strokeWidth={linkWidth}
      strokeOpacity={0.35}
    />
  );
}

/** Цвета по смыслу — как в текущем frontend/static/js/app.js (renderAllocationBar):
 * долг = red, резерв = amber, цели = green. Не только цветом (A11Y-07) — везде есть текст.
 *
 * best=null — дефицит (top3 пуст): алгоритм не молчит, а явно объясняет, что рекомендации
 * нет (fail-loud), не отдельная ветка на каждой странице — используется и на dashboard,
 * и на planning (Э4 партия 2), чтобы текст не разошёлся между ними.
 *
 * `alternatives` — полный `ranked[]` того же плана (та же коллекция, что уходит в
 * AlternativesBrowser на /planning). Столбец, легенда и диаграмма Санкея ниже реагируют на
 * ползунки «что если» (WhatIfSliders) — это ОДИН интерактивный составной столбец, не
 * рекомендация сверху и отдельная песочница снизу (план вехи 8, Э5: «составной столбец плюс
 * ползунки «что если»» — design-critic поймал именно рассинхрон этих двух половин как блокер
 * v8.11.0). AllocationPanel новых чисел не считает — только ищет готовую, уже посчитанную
 * бэкендом альтернативу в `alternatives` (findMatchingAlternative), канон математики заморожен
 * до решения владельца. */
export function AllocationPanel({
  best,
  alternatives,
}: {
  best: PlanAlternative | null;
  alternatives: PlanAlternative[];
}) {
  const [detailed, setDetailed] = useState(false);
  const total = best ? best.x_obligations + best.x_reserve + best.x_goals : 0;
  const recommendedNotches = best ? notchesOf(best, total) : { debt: 0, goals: 0 };
  const [debtNotch, setDebtNotch] = useState(recommendedNotches.debt);
  const [goalsNotch, setGoalsNotch] = useState(recommendedNotches.goals);

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

  const hasDebtOption = hasNonZeroCategory(alternatives, "x_obligations");
  const hasGoalsOption = hasNonZeroCategory(alternatives, "x_goals");
  const canShowWhatIf = hasDebtOption || hasGoalsOption;

  // Ползунки независимы, но их сумма не может превышать GRID_NOTCHES (резерв не может стать
  // отрицательным) — при движении одного досчитываем клампом второй, а не только через атрибут
  // max (иначе React-state второго ползунка останется устаревшим и резерв уйдёт в минус).
  function onDebtChange(next: number) {
    setDebtNotch(next);
    setGoalsNotch((g) => Math.min(g, GRID_NOTCHES - next));
  }
  function onGoalsChange(next: number) {
    setGoalsNotch(next);
    setDebtNotch((d) => Math.min(d, GRID_NOTCHES - next));
  }
  function resetToRecommended() {
    setDebtNotch(recommendedNotches.debt);
    setGoalsNotch(recommendedNotches.goals);
  }

  const reserveNotch = GRID_NOTCHES - debtNotch - goalsNotch;
  const isRecommended =
    debtNotch === recommendedNotches.debt && goalsNotch === recommendedNotches.goals;
  const activeAlt = findMatchingAlternative(alternatives, total, debtNotch, goalsNotch);

  const debtAmount = (total * debtNotch) / GRID_NOTCHES;
  const reserveAmount = (total * reserveNotch) / GRID_NOTCHES;
  const goalsAmount = (total * goalsNotch) / GRID_NOTCHES;

  const sankeyData = buildAllocationSankeyData({
    x_obligations: debtAmount,
    x_reserve: reserveAmount,
    x_goals: goalsAmount,
  });
  // Санкей из одной связи — то же самое, что уже показывает столбец выше, ничего не добавляет.
  const canShowSankey = sankeyData.links.length > 1;

  return (
    <section className="fp-panel">
      <h2>{t("Куда пойдут свободные деньги")}</h2>
      <p className="fp-lede">
        {isRecommended
          ? t("Рекомендация СППР ({name}), полезность U = {u}.", {
              name: best.name,
              u: formatNumber(best.utility, 2),
            })
          : t("Гипотетический вариант — не рекомендация СППР.")}
      </p>

      {/* Объяснение — только у best (explain_alternative вызывается лишь для top3,
       * app/services/planning.py); произвольная позиция ползунков «что если» его не
       * несёт, поэтому показываем только пока пользователь не отошёл от рекомендации. */}
      {isRecommended && best.explanation && (
        <div className="fp-alloc-explanation">
          <p className="fp-alloc-explanation__insight">{best.explanation.insight}</p>
          {best.explanation.gains.length > 0 && (
            <ul className="fp-alloc-explanation__list fp-alloc-explanation__list--gains">
              {best.explanation.gains.map((g, i) => (
                <li key={i}>{g}</li>
              ))}
            </ul>
          )}
          {best.explanation.costs.length > 0 && (
            <ul className="fp-alloc-explanation__list fp-alloc-explanation__list--costs">
              {best.explanation.costs.map((c, i) => (
                <li key={i}>{c}</li>
              ))}
            </ul>
          )}
          {best.explanation.counterfactual?.available && best.explanation.counterfactual.text && (
            <p className="fp-alloc-explanation__counterfactual">
              {best.explanation.counterfactual.text}
            </p>
          )}
        </div>
      )}
      <div className="fp-alloc-bar" role="presentation">
        {debtNotch > 0 && <div style={{ flex: debtNotch, background: "var(--c-red)" }} />}
        {reserveNotch > 0 && <div style={{ flex: reserveNotch, background: "var(--c-amber)" }} />}
        {goalsNotch > 0 && <div style={{ flex: goalsNotch, background: "var(--c-green)" }} />}
      </div>
      <div className="fp-alloc-legend">
        <span>
          <i className="fp-dot" style={{ background: "var(--c-red)" }} />
          {t("Досрочное погашение — {sum} ({pct}%)", {
            sum: formatMoney(debtAmount),
            pct: debtNotch * 10,
          })}
        </span>
        <span>
          <i className="fp-dot" style={{ background: "var(--c-amber)" }} />
          {t("Резерв — {sum} ({pct}%)", {
            sum: formatMoney(reserveAmount),
            pct: reserveNotch * 10,
          })}
        </span>
        <span>
          <i className="fp-dot" style={{ background: "var(--c-green)" }} />
          {t("Цели — {sum} ({pct}%)", { sum: formatMoney(goalsAmount), pct: goalsNotch * 10 })}
        </span>
      </div>

      {canShowWhatIf && (
        <WhatIfSliders
          hasDebtOption={hasDebtOption}
          hasGoalsOption={hasGoalsOption}
          debtNotch={debtNotch}
          goalsNotch={goalsNotch}
          onDebtChange={onDebtChange}
          onGoalsChange={onGoalsChange}
          match={activeAlt}
          isRecommended={isRecommended}
          onReset={resetToRecommended}
        />
      )}

      {canShowSankey && (
        <>
          {/* aria-pressed, не aria-expanded/aria-controls: блок ниже строго декоративный
           * (aria-hidden) и для AT никогда не «раскрывается» — expanded-семантика была бы
           * ложью о том, что у кнопки есть эффект в дереве доступности (находка a11y-auditor). */}
          <Button
            variant="ghost"
            className="fp-alloc-toggle"
            aria-pressed={detailed}
            onClick={() => setDetailed((v) => !v)}
          >
            {detailed ? t("Свернуть диаграмму") : t("Подробно — диаграмма Санкея")}
          </Button>
          {detailed && (
            // Столбец и легенда выше — уже полный и всегда видимый источник этих же чисел
            // текстом (и реагируют на те же ползунки); диаграмма ниже строго декоративная (как
            // fp-forecast-chart в ForecastPanel). overflow-x на внешнем блоке + min-width на
            // внутреннем (--chart-sankey-min-width) — на узких экранах диаграмма становится
            // горизонтально прокручиваемой, а не сплющивает подписи категорий друг на друга.
            <div className="fp-alloc-sankey" aria-hidden="true">
              <div className="fp-alloc-sankey__inner">
                <ResponsiveContainer>
                  <Sankey
                    data={sankeyData}
                    node={AllocationSankeyNode}
                    link={AllocationSankeyLink}
                    nodeWidth={12} // --sp-3
                    nodePadding={32} // --sp-6
                    margin={{
                      top: 8, // --sp-2
                      bottom: 8, // --sp-2
                      left: SANKEY_LABEL_MARGIN,
                      right: SANKEY_LABEL_MARGIN,
                    }}
                  >
                    <Tooltip
                      formatter={(value) => formatMoney(Number(value))}
                      contentStyle={{
                        background: "var(--c-surface-up)",
                        border: "var(--border-w) solid var(--c-border-hl)",
                        borderRadius: "var(--r-sm)",
                        padding: "var(--sp-2) var(--sp-3)",
                        color: "var(--c-text)",
                      }}
                    />
                  </Sankey>
                </ResponsiveContainer>
              </div>
            </div>
          )}
        </>
      )}
    </section>
  );
}
