import { useMemo } from "react";
import katex from "katex";
import "katex/dist/katex.min.css";
import { t } from "@shared/lib/i18n/t";
import type { WeightedScores } from "@entities/plan-summary";

/**
 * Тело раскрытой формулы — вынесено из UtilityFormula.tsx в отдельный чанк (см. `lazy()` там):
 * `katex` — это ~90 КБ gzip, и статический импорт сверху файла утягивал его в общий чанк
 * `AllocationPanel`, который используется и на /dashboard, и на /planning (vite build поймал
 * chunk >500 КБ на этом импорте). Формула — опциональная техническая деталь по клику
 * меньшинства, а не то, за что должен платить каждый визит страницы.
 *
 * Символьная часть (docs/math_model.md §8, канон SAW) не зависит от альтернативы — рендерится
 * один раз при загрузке ЭТОГО чанка (первый клик «Показать формулу»), не на каждый повторный
 * клик того же пользователя.
 */
const SYMBOLIC_FORMULA_HTML = katex.renderToString(
  String.raw`U(a) = w_R\,\hat{R}_n(a) + w_L\,\hat{L}_n(a) + w_D\,(1-\hat{D}_n(a)) + w_S\,\hat{S}_n(a)`,
  { throwOnError: false, displayMode: true },
);

// Та же формулировка, что app/core/recommendation.py::CRITERION_LABELS — не импортируется
// через границу Python/TypeScript, синхронизируется вручную при правке одного из двух мест.
// Символ рядом — не голое «Rt» plain-текстом (выглядело как отладочный вывод, не типографика),
// а тот же KaTeX-рендер, что и в формуле выше: R_t с настоящим подстрочным индексом.
const CRITERION_ITEMS: { key: keyof WeightedScores; symbol: string; label: string }[] = [
  { key: "Rt", symbol: "R_t", label: t("свободный поток") },
  { key: "Lt", symbol: "L_t", label: t("подушка безопасности") },
  { key: "Dt", symbol: "D_t", label: t("долговая нагрузка") },
  { key: "Si", symbol: "S_i", label: t("продвижение целей") },
];

const CRITERION_SYMBOL_HTML: Record<keyof WeightedScores, string> = Object.fromEntries(
  CRITERION_ITEMS.map(({ key, symbol }) => [
    key,
    katex.renderToString(symbol, { throwOnError: false, displayMode: false }),
  ]),
) as Record<keyof WeightedScores, string>;

function toKatexNumber(value: number): string {
  return value.toFixed(2).replace(".", "{,}");
}

export function UtilityFormulaBody({
  weightedScores,
  utility,
}: {
  weightedScores: WeightedScores;
  utility: number;
}) {
  // Числа альтернативы меняются (движение ползунков «что если» пересчитывает activeAlt в
  // AllocationPanel) — символьная часть выше нет, поэтому инстанцированную часть считаем
  // отдельно и только при изменении входных чисел, не на каждый рендер панели.
  const instantiatedHtml = useMemo(
    () =>
      katex.renderToString(
        String.raw`U(a) = ${toKatexNumber(weightedScores.Rt)} + ${toKatexNumber(weightedScores.Lt)} + ${toKatexNumber(weightedScores.Dt)} + ${toKatexNumber(weightedScores.Si)} = ${toKatexNumber(utility)}`,
        { throwOnError: false, displayMode: true },
      ),
    [weightedScores.Rt, weightedScores.Lt, weightedScores.Dt, weightedScores.Si, utility],
  );

  return (
    <div className="fp-utility-formula__body">
      <div
        className="fp-utility-formula__katex"
        dangerouslySetInnerHTML={{ __html: SYMBOLIC_FORMULA_HTML }}
      />
      <div
        className="fp-utility-formula__katex"
        dangerouslySetInnerHTML={{ __html: instantiatedHtml }}
      />
      <ul className="fp-utility-formula__legend" role="list">
        {CRITERION_ITEMS.map(({ key, label }) => (
          <li key={key}>
            <span
              className="fp-utility-formula__legend-symbol"
              dangerouslySetInnerHTML={{ __html: CRITERION_SYMBOL_HTML[key] }}
            />
            <span className="fp-utility-formula__legend-label">{label}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
