import { useEffect, useId, useState } from "react";
import { formatMoney, formatNumber, formatPercent } from "@shared/lib/money/formatMoney";
import { t } from "@shared/lib/i18n/t";
import { Button } from "@shared/ui";
import { DTI_WARN_THRESHOLD } from "@entities/plan-summary";
import type { PlanAlternative } from "@entities/plan-summary";
import { GRID_NOTCHES } from "./findMatchingAlternative";
import "./WhatIfSliders.css";

const LIVE_ANNOUNCE_DEBOUNCE_MS = 400;
const PCT_PER_NOTCH = 100 / GRID_NOTCHES;

/** Текст для скринридера — отдельно от видимого результата (тот обновляется мгновенно на
 * каждый рендер, этот — с задержкой, см. комментарий у aria-live ниже). */
function describeResult(match: PlanAlternative | undefined): string {
  if (!match) {
    return t(
      "Такое распределение не проходит проверку модели (например, превысило бы порог ПДН 40%) — недоступно.",
    );
  }
  const warn = match.Dt_new > DTI_WARN_THRESHOLD ? t(", близко к порогу 40%") : "";
  return t("Свободный поток {rt}, ликвидность {lt} мес., ПДН {dt}{warn}.", {
    rt: formatMoney(match.Rt_new),
    lt: formatNumber(match.Lt_new),
    dt: formatPercent(match.Dt_new),
    warn,
  });
}

/** Пункт Э5 плана вехи 8: «составной столбец плюс ползунки «что если»» — сам столбец и легенда
 * (в AllocationPanel) реагируют на эти же ползунки, это не отдельная песочница сбоку (было
 * найдено design-critic как блокер v8.11.0: столбец оставался заморожен на рекомендации, пока
 * ползунки показывали другие числа рядом). Компонент управляемый — состояние (debtNotch/
 * goalsNotch) и клампинг живут в AllocationPanel, чтобы одни и те же числа приводили в движение
 * и столбец, и диаграмму Санкея, и этот блок результата. */
export function WhatIfSliders({
  hasDebtOption,
  hasGoalsOption,
  debtNotch,
  goalsNotch,
  onDebtChange,
  onGoalsChange,
  match,
  isRecommended,
  onReset,
}: {
  hasDebtOption: boolean;
  hasGoalsOption: boolean;
  debtNotch: number;
  goalsNotch: number;
  onDebtChange: (notch: number) => void;
  onGoalsChange: (notch: number) => void;
  match: PlanAlternative | undefined;
  isRecommended: boolean;
  onReset: () => void;
}) {
  const debtId = useId();
  const goalsId = useId();

  // Живая область не объявляет КАЖДУЮ из 11 отметок ползунка — при автоповторе стрелки на
  // клавиатуре это очередь из объявлений подряд, скринридер отстаёт от реальной позиции
  // (a11y-auditor, v8.11.0). Видимый результат ниже обновляется без задержки — задержка только
  // в озвучке.
  const [announced, setAnnounced] = useState(() => describeResult(match));
  useEffect(() => {
    const timer = setTimeout(() => setAnnounced(describeResult(match)), LIVE_ANNOUNCE_DEBOUNCE_MS);
    return () => clearTimeout(timer);
  }, [match]);

  return (
    <div className="fp-whatif">
      <div className="fp-whatif__head">
        <h3>{t("Что если распределить иначе?")}</h3>
        {!isRecommended && (
          <Button variant="ghost" className="fp-whatif__reset" onClick={onReset}>
            {t("Вернуть рекомендацию")}
          </Button>
        )}
      </div>
      <p className="fp-whatif__hint">
        {t("Подвиньте ползунки — столбец и суммы выше пересчитаются, «Резерв» — остаток.")}
      </p>
      <div className="fp-whatif__sliders">
        {hasDebtOption && (
          <div className="fp-whatif__slider fp-whatif__slider--debt">
            <div className="fp-whatif__slider-head">
              <label htmlFor={debtId}>{t("Досрочное погашение")}</label>
              <span aria-hidden="true">{debtNotch * PCT_PER_NOTCH}%</span>
            </div>
            <input
              id={debtId}
              type="range"
              min={0}
              max={GRID_NOTCHES - goalsNotch}
              step={1}
              value={debtNotch}
              aria-valuetext={t("{pct}%", { pct: debtNotch * PCT_PER_NOTCH })}
              onChange={(e) => onDebtChange(Number(e.target.value))}
            />
          </div>
        )}
        {hasGoalsOption && (
          <div className="fp-whatif__slider fp-whatif__slider--goals">
            <div className="fp-whatif__slider-head">
              <label htmlFor={goalsId}>{t("Цели")}</label>
              <span aria-hidden="true">{goalsNotch * PCT_PER_NOTCH}%</span>
            </div>
            <input
              id={goalsId}
              type="range"
              min={0}
              max={GRID_NOTCHES - debtNotch}
              step={1}
              value={goalsNotch}
              aria-valuetext={t("{pct}%", { pct: goalsNotch * PCT_PER_NOTCH })}
              onChange={(e) => onGoalsChange(Number(e.target.value))}
            />
          </div>
        )}
      </div>

      <div className="fp-whatif__result">
        {match ? (
          <>
            <span>{t("Свободный поток: {v}", { v: formatMoney(match.Rt_new) })}</span>
            <span>{t("Ликвидность: {v} мес.", { v: formatNumber(match.Lt_new) })}</span>
            <span className="fp-whatif__dti">
              {t("ПДН: {v}", { v: formatPercent(match.Dt_new) })}
              <span
                className={`fp-whatif__badge fp-whatif__badge--${
                  match.Dt_new > DTI_WARN_THRESHOLD ? "warn" : "muted"
                }`}
              >
                {match.Dt_new > DTI_WARN_THRESHOLD ? t("порог 40%, близко") : t("порог 40%")}
              </span>
            </span>
          </>
        ) : (
          <span className="fp-whatif__unavailable">
            {t(
              "Такое распределение не проходит проверку модели (например, превысило бы порог ПДН 40%) — недоступно.",
            )}
          </span>
        )}
      </div>
      {/* Не весь блок результата — иначе каждое движение ползунка целиком перечитывалось бы
       * диктором; тот же паттерн, что у пересортировки в AlternativesBrowser.tsx. */}
      <p className="sr-only" role="status" aria-live="polite">
        {announced}
      </p>
    </div>
  );
}
