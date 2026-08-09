import { useMemo, useState } from "react";
import { formatMoney, formatNumber, formatPercent } from "@shared/lib/money/formatMoney";
import { t } from "@shared/lib/i18n/t";
import { Button } from "@shared/ui";
import type { PlanAlternative } from "@entities/plan-summary";
import "@shared/ui/panel.css";
import "./AlternativesBrowser.css";

type SortKey = "recommended" | "Rt_new" | "Lt_new" | "Dt_new";

const SORTERS: Record<SortKey, (a: PlanAlternative, b: PlanAlternative) => number> = {
  // ranked уже отсортирован бэкендом по (floor_level, utility) — «по рекомендации» это
  // порядок как есть, без пересортировки на фронте.
  recommended: () => 0,
  Rt_new: (a, b) => b.Rt_new - a.Rt_new,
  Lt_new: (a, b) => b.Lt_new - a.Lt_new,
  // ПДН — чем меньше, тем лучше (жёсткий инвариант канона v3.0.0: Dt <= 0.40).
  Dt_new: (a, b) => a.Dt_new - b.Dt_new,
};

const SORT_LABELS: Record<SortKey, string> = {
  recommended: t("Рекомендации СППР"),
  Rt_new: t("Свободному потоку (Rt)"),
  Lt_new: t("Ликвидности (Lt)"),
  Dt_new: t("Долговой нагрузке (ПДН)"),
};

const PANEL_ID = "fp-alt-browser-panel";

/** Пункт Э5 плана вехи 8: по умолчанию top3 (AllocationPanel), «Показать все» раскрывает
 * полный ranked[] (до 66 при канонической сетке 10%) с сортировкой по критериям. Число в кнопке
 * и в списке — одно и то же `alternatives.length` (сам ranked), а не отдельный проп: два числа
 * из одного источника вместо двух источников, которые могли бы разойтись. */
export function AlternativesBrowser({ alternatives }: { alternatives: PlanAlternative[] }) {
  const [expanded, setExpanded] = useState(false);
  const [sortKey, setSortKey] = useState<SortKey>("recommended");

  const sorted = useMemo(() => [...alternatives].sort(SORTERS[sortKey]), [alternatives, sortKey]);

  if (alternatives.length === 0) {
    return null;
  }

  return (
    <section className="fp-panel fp-alt-browser">
      <div className="fp-alt-browser__head">
        <h2>{t("Все варианты распределения")}</h2>
        <Button
          variant="ghost"
          aria-expanded={expanded}
          aria-controls={PANEL_ID}
          onClick={() => setExpanded((v) => !v)}
        >
          {expanded ? (
            t("Свернуть")
          ) : (
            <>
              {t("Показать все ({n})", { n: alternatives.length })}
              <span aria-hidden="true"> →</span>
            </>
          )}
        </Button>
      </div>

      {expanded && (
        <div id={PANEL_ID}>
          <div className="fp-alt-browser__sort">
            <label htmlFor="fp-alt-sort">{t("Сортировать по")}</label>
            <select
              id="fp-alt-sort"
              value={sortKey}
              onChange={(e) => setSortKey(e.target.value as SortKey)}
            >
              <option value="recommended">{SORT_LABELS.recommended}</option>
              <option value="Rt_new">{SORT_LABELS.Rt_new}</option>
              <option value="Lt_new">{SORT_LABELS.Lt_new}</option>
              <option value="Dt_new">{SORT_LABELS.Dt_new}</option>
            </select>
          </div>
          {/* Список ниже полностью переупорядочивается при смене select — визуально это видно
           * под курсором, но screen reader об этом не узнает без явного объявления (WCAG 4.1.3).
           * Не делаем весь <ul> aria-live — тогда после каждой пересортировки диктор зачитывал бы
           * все 66 строк заново. */}
          <p className="sr-only" role="status" aria-live="polite">
            {t("Список отсортирован: {label}", { label: SORT_LABELS[sortKey] })}
          </p>

          <ul
            className="fp-alt-browser__list"
            aria-label={t("Варианты распределения, {n}", { n: alternatives.length })}
          >
            {sorted.map((alt) => (
              <li key={alt.id} className="fp-alt-row">
                <div className="fp-alt-row__head">
                  <span className="fp-alt-row__name">
                    {alt.name}
                    {alt.is_recommended && (
                      <span className="fp-alt-row__badge">{t("рекомендовано")}</span>
                    )}
                  </span>
                  <span className="fp-alt-row__utility">
                    {t("U = {u}", { u: formatNumber(alt.utility, 2) })}
                  </span>
                </div>
                <div className="fp-alt-row__meta">
                  <span>{t("Rt {v}", { v: formatMoney(alt.Rt_new) })}</span>
                  <span>{t("Lt {v} мес.", { v: formatNumber(alt.Lt_new) })}</span>
                  <span>{t("ПДН {v}", { v: formatPercent(alt.Dt_new) })}</span>
                </div>
                <div className="fp-alt-row__split">
                  <span>{t("Долг {v}", { v: formatMoney(alt.x_obligations) })}</span>
                  <span>{t("Резерв {v}", { v: formatMoney(alt.x_reserve) })}</span>
                  <span>{t("Цели {v}", { v: formatMoney(alt.x_goals) })}</span>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}
