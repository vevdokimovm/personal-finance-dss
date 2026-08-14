import { useEffect, useId, useRef, useState } from "react";
import { formatPercent } from "@shared/lib/money/formatMoney";
import { t } from "@shared/lib/i18n/t";
import { Button } from "@shared/ui";
import "./ForecastControls.css";

const HORIZON_OPTIONS = [3, 6, 12, 24];
// Тот же паттерн, что WhatIfSliders (LIVE_ANNOUNCE_DEBOUNCE_MS) — но здесь задержка не только
// для озвучки, а и для самого запроса: не бомбить бэкенд Monte-Carlo пересчётом на каждый
// пиксель протаскивания ползунка.
const R_BENCH_DEBOUNCE_MS = 500;
const R_BENCH_MAX_PCT = 30;

function pct(fraction: number): number {
  return Math.round(fraction * 1000) / 10;
}

/** §8.4 «Улучшить UI прогнозирования»: горизонт (select — те же 3/6/12/24, что
 * ForecastRequest.horizon 1..24 на бэкенде) + ставка капитализации r_bench как сценарий
 * «что если» (WhatIfSliders — тот же приём, но здесь движение ползунка требует живого
 * пересчёта на бэкенде, не готовой альтернативы из уже посчитанного набора, поэтому
 * значение дебаунсится перед вызовом `onRBenchChange`, а не применяется мгновенно).
 * Управляемый компонент: горизонт/ставка живут в PlanningPage (тот же владелец, что
 * `useForecast`), этот компонент только рендерит и дебаунсит ввод.
 *
 * До сдачи design-critic и a11y-auditor нашли и починили: сырой JS-`%` вместо `formatPercent`
 * (десятичная точка рядом с канонической запятой — CMP-04); `isFetching` доходил только до
 * скринридера, зрячий пользователь 500 мс дебаунса + Monte-Carlo не видел вообще ничего (FB-01);
 * `flex:1` без `flex-basis` не давал полю ползунка перенестись на свою строку на узких экранах
 * (CMP-07); фокус после исчезновения кнопки «Сбросить» улетал в `<body>` вместо ползунка
 * (WCAG 2.4.3 по духу); accent-цвет ползунка совпадал с акцентом медианной линии графика
 * (правило 4 брифа — акцент занят результатом, не сценарием). */
export function ForecastControls({
  horizon,
  onHorizonChange,
  rBench,
  onRBenchChange,
  realRBench,
  isOverridden,
  isFetching = false,
}: {
  horizon: number;
  onHorizonChange: (horizon: number) => void;
  rBench: number | undefined;
  onRBenchChange: (rBench: number | undefined) => void;
  realRBench: number;
  isOverridden: boolean;
  isFetching?: boolean;
}) {
  const horizonId = useId();
  const rBenchId = useId();
  const hintId = useId();
  const realMarkId = useId();
  const rBenchInputRef = useRef<HTMLInputElement>(null);

  const [sliderPct, setSliderPct] = useState(() => pct(rBench ?? realRBench));
  // Реальная ставка обновляется прогнозом (например, ключевая ЦБ подтянулась заново) —
  // ползунок следует за ней, только пока сценарий не переопределён вручную. Синхронизация —
  // прямо в теле рендера (React: «Adjusting state when a prop changes»), не в useEffect: без
  // лишнего цикла рендера и без react-hooks/set-state-in-effect. `isOverridden` не нужен в
  // зависимости — активный override меняет sliderPct через handleSliderChange/handleReset
  // напрямую, этот блок только подхватывает ДРЕЙФ реальной ставки, когда override не активен.
  const [trackedRealRBench, setTrackedRealRBench] = useState(realRBench);
  if (!isOverridden && realRBench !== trackedRealRBench) {
    setTrackedRealRBench(realRBench);
    setSliderPct(pct(realRBench));
  }

  const debounceRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  useEffect(() => () => clearTimeout(debounceRef.current), []);

  function scheduleCommit(nextPct: number) {
    clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      onRBenchChange(nextPct / 100);
    }, R_BENCH_DEBOUNCE_MS);
  }

  function handleSliderChange(nextPct: number) {
    setSliderPct(nextPct);
    scheduleCommit(nextPct);
  }

  function handleReset() {
    clearTimeout(debounceRef.current);
    setSliderPct(pct(realRBench));
    onRBenchChange(undefined);
    // a11y-auditor: кнопка «Сбросить» размонтируется сразу после клика (isOverridden станет
    // false) — без явного переноса фокус улетает в <body>, следующий Tab начинает обход
    // страницы заново. Переносим на сам ползунок — тот же элемент, что пользователь и так
    // настраивал, разумное продолжение обхода.
    rBenchInputRef.current?.focus();
  }

  return (
    <div className="fp-forecast-controls">
      <p id={hintId} className="fp-forecast-controls__hint">
        {t(
          "Горизонт и ставка ниже — сценарий «что если», не решение СППР. Результат обновится в графике, таблице и подписи ниже.",
        )}
      </p>
      <div className="fp-forecast-controls__row">
        <div className="fp-forecast-controls__field">
          <label htmlFor={horizonId}>{t("Горизонт")}</label>
          <select
            id={horizonId}
            value={horizon}
            aria-describedby={hintId}
            onChange={(e) => onHorizonChange(Number(e.target.value))}
          >
            {HORIZON_OPTIONS.map((h) => (
              <option key={h} value={h}>
                {t("{h} мес.", { h })}
              </option>
            ))}
          </select>
        </div>

        <div className="fp-forecast-controls__field fp-forecast-controls__field--slider">
          <div className="fp-forecast-controls__slider-head">
            <label htmlFor={rBenchId}>{t("Ставка капитализации")}</label>
            <span className="fp-forecast-controls__slider-value">
              <span aria-hidden="true">{formatPercent(sliderPct / 100)}</span>
              {isOverridden && (
                <Button
                  variant="ghost"
                  className="fp-forecast-controls__reset"
                  onClick={handleReset}
                >
                  {t("Сбросить к реальной ({v})", { v: formatPercent(realRBench) })}
                </Button>
              )}
            </span>
          </div>
          <input
            ref={rBenchInputRef}
            id={rBenchId}
            type="range"
            min={0}
            max={R_BENCH_MAX_PCT}
            step={0.5}
            value={sliderPct}
            list={realMarkId}
            aria-describedby={hintId}
            aria-valuetext={formatPercent(sliderPct / 100)}
            onChange={(e) => handleSliderChange(Number(e.target.value))}
          />
          {/* Засечка на треке в позиции настоящей ставки — ориентир, откуда сценарий отклонился
           * (native <datalist>, не рисуем позицию вручную). Деградирует незаметно там, где
           * браузер тики не рисует — края диапазона всё равно подписаны текстом ниже. */}
          <datalist id={realMarkId}>
            <option value={pct(realRBench)} />
          </datalist>
          <div className="fp-forecast-controls__slider-scale" aria-hidden="true">
            <span>{t("{pct}%", { pct: 0 })}</span>
            <span>{t("{pct}%", { pct: R_BENCH_MAX_PCT })}</span>
          </div>
        </div>
      </div>

      {/* Видимый признак пересчёта — не только sr-only: без него 500 мс дебаунса плюс раунд-трип
       * Monte-Carlo зрячий пользователь не видит вообще ничего, пока график не дёрнется скачком
       * (design-critic, FB-01/ST-02). Текст занимает место всегда (не появляется/пропадает),
       * чтобы соседние элементы не прыгали каждое движение ползунка. */}
      <p className="fp-forecast-controls__status" role="status" aria-live="polite">
        {isFetching ? t("Пересчитываю прогноз…") : ""}
      </p>
    </div>
  );
}
