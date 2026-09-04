import { useMemo, useState } from "react";
import { formatMoney, formatNumber, formatPercent } from "@shared/lib/money/formatMoney";
import { t } from "@shared/lib/i18n/t";
import { Button, Formula } from "@shared/ui";
import type { PlanAlternative } from "@entities/plan-summary";
import "@shared/ui/panel.css";
import "./AlternativesBrowser.css";

type SortKey = "recommended" | "Rt_new" | "Lt_new" | "Dt_new";

const SORTERS: Record<SortKey, (a: PlanAlternative, b: PlanAlternative) => number> = {
  // ranked уже отсортирован бэкендом по (floor_level, utility) — «по рекомендации» это
  // порядок как есть, без пересортировки на фронте.
  recommended: () => 0,
  // 🔴 `?? 0` не «на всякий случай»: в контракте `Rt_new`/`Lt_new`/`Dt_new` вне
  // `required` (v8.40.0, переход на сгенерированные типы это обнажил). Раньше здесь
  // стояло голое вычитание — на ответе без показателя выходил NaN, а сортировка с NaN
  // в компараторе даёт не «странный порядок», а произвольный: реализация сортировки
  // вправе вести себя как угодно при несогласованном компараторе.
  Rt_new: (a, b) => (b.Rt_new ?? 0) - (a.Rt_new ?? 0),
  Lt_new: (a, b) => (b.Lt_new ?? 0) - (a.Lt_new ?? 0),
  // ПДН — чем меньше, тем лучше (жёсткий инвариант канона, docs/math_model.md §3: Dt <= 0.40).
  Dt_new: (a, b) => (a.Dt_new ?? 0) - (b.Dt_new ?? 0),
};

// Юникодный подстрочный индекс (U+209C, не буква "т" уменьшенным кеглем) — максимум
// типографики, доступный внутри нативного <option>: браузер не рендерит там ни KaTeX,
// ни любой другой HTML/React-компонент, только текстовый узел (единственное место в этом
// проходе, где переменную нельзя набрать через <Formula>, см. shared/ui/Formula.tsx).
const SORT_LABELS: Record<SortKey, string> = {
  recommended: t("Рекомендации СППР"),
  Rt_new: t("Свободному потоку (Rₜ)"),
  Lt_new: t("Ликвидности (Lₜ)"),
  Dt_new: t("Долговой нагрузке (ПДН)"),
};

const PANEL_ID = "fp-alt-browser-panel";

/** Пункт Э5 плана вехи 8: по умолчанию top3 (AllocationPanel), «Показать все» раскрывает
 * полный ranked[] (до 66 при канонической сетке 10%) с сортировкой по критериям. Число в кнопке
 * и в списке — одно и то же `alternatives.length` (сам ranked), а не отдельный проп: два числа
 * из одного источника вместо двух источников, которые могли бы разойтись. */
/* Стабильная ссылка на пустой список: литерал `?? []` создавал бы новый массив на каждом
   рендере, и `useMemo` ниже пересортировывал бы данные вхолостую при каждом обновлении
   (поймано react-hooks/exhaustive-deps). */
const EMPTY_ALTERNATIVES: PlanAlternative[] = [];

export function AlternativesBrowser({
  /* Опционально по контракту (`CalculatePlanResult.ranked` — вне `required` схемы
     PlanningCalculateResponse). Пустой список у этого компонента уже был штатным
     состоянием ниже, поэтому отсутствие данных сводится к нему, а не к падению. */
  alternatives,
}: {
  alternatives?: PlanAlternative[];
}) {
  const alts = alternatives ?? EMPTY_ALTERNATIVES;
  const [expanded, setExpanded] = useState(false);
  const [sortKey, setSortKey] = useState<SortKey>("recommended");

  const sorted = useMemo(() => [...alts].sort(SORTERS[sortKey]), [alts, sortKey]);

  if (alts.length === 0) {
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
              {t("Показать все ({n})", { n: alts.length })}
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
            aria-label={t("Варианты распределения, {n}", { n: alts.length })}
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
                  {/* Раньше «U = {u}» — сырая формульная нотация без объяснения (CMP-05,
                   * design-critic v8.10.0); человеческая подпись вместо переменной модели.
                   * Раскрываемая формула — только у рекомендации в AllocationPanel
                   * (UtilityFormula), не на каждой из 66 строк этого списка. */}
                  <span className="fp-alt-row__utility">
                    {alt.utility == null
                      ? t("Оценка недоступна")
                      : t("Оценка {u}", { u: formatNumber(alt.utility, 2) })}
                  </span>
                </div>
                {/* Показатели вне `required` контракта — отсутствующий не выдумываем
                    нулём в подписи: «Rt 0 ₽» и «нет данных» значат разное. */}
                <div className="fp-alt-row__meta">
                  <span>
                    <Formula tex="R_t" fallback="Rt" />{" "}
                    {alt.Rt_new == null ? t("нет данных") : formatMoney(alt.Rt_new)}
                  </span>
                  <span>
                    <Formula tex="L_t" fallback="Lt" />{" "}
                    {alt.Lt_new == null
                      ? t("нет данных")
                      : `${formatNumber(alt.Lt_new)} ${t("мес.")}`}
                  </span>
                  <span>
                    {alt.Dt_new == null
                      ? t("ПДН нет данных")
                      : t("ПДН {v}", { v: formatPercent(alt.Dt_new) })}
                  </span>
                </div>
                {/* У долей есть дефолт 0.0 в схеме (`app/schemas/planning.py`), в
                    `required` их нет только поэтому — ноль здесь смысл сохраняет:
                    «на это направление не идёт ничего». */}
                <div className="fp-alt-row__split">
                  <span>{t("Долг {v}", { v: formatMoney(alt.x_obligations ?? 0) })}</span>
                  <span>{t("Резерв {v}", { v: formatMoney(alt.x_reserve ?? 0) })}</span>
                  <span>{t("Цели {v}", { v: formatMoney(alt.x_goals ?? 0) })}</span>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}
