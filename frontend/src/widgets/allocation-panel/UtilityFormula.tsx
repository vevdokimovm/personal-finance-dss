import { Suspense, lazy, useId, useState } from "react";
import { t } from "@shared/lib/i18n/t";
import { Button } from "@shared/ui";
import type { WeightedScores } from "@entities/plan-summary";
import "./UtilityFormula.css";

/**
 * Раскрываемая по клику формула оценки — план вехи 8, Э5 («Формулы модели — KaTeX,
 * раскрываются по клику»). Закрывает находку design-critic v8.10.0 (CMP-05): голая запись
 * «U = {u}» в лede AllocationPanel — формульная нотация без объяснения, показанная как
 * обычный текст. По умолчанию формула скрыта — «почему» несёт insight/gains/costs рядом
 * (человеческий язык, FR-01); эта панель — техническая деталь для тех, кто её хочет.
 *
 * Тело со `katex` — отдельный чанк (см. UtilityFormulaBody.tsx): не платить бандлом библиотеки
 * формул на каждом визите /dashboard и /planning ради опциональной детали по клику меньшинства.
 */
const UtilityFormulaBody = lazy(() =>
  import("./UtilityFormulaBody").then((m) => ({ default: m.UtilityFormulaBody })),
);

export function UtilityFormula({
  weightedScores,
  utility,
}: {
  weightedScores: WeightedScores;
  utility: number;
}) {
  const [expanded, setExpanded] = useState(false);
  const panelId = useId();

  return (
    <div className="fp-utility-formula">
      <Button
        variant="ghost"
        className="fp-utility-formula__toggle"
        aria-expanded={expanded}
        aria-controls={panelId}
        onClick={() => setExpanded((v) => !v)}
      >
        {expanded ? t("Скрыть формулу оценки") : t("Показать формулу оценки")}
      </Button>
      {expanded && (
        <div id={panelId}>
          <Suspense fallback={<p className="fp-utility-formula__loading">{t("Загрузка…")}</p>}>
            <UtilityFormulaBody weightedScores={weightedScores} utility={utility} />
          </Suspense>
        </div>
      )}
    </div>
  );
}
