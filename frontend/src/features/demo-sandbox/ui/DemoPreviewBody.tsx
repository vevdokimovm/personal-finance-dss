import type { DemoPreview } from "@entities/demo";
import { formatMoney } from "@shared/lib/money/formatMoney";
import { t } from "@shared/lib/i18n/t";

/**
 * Тело предпросмотра портрета: что покажет расчёт, ещё до загрузки данных.
 *
 * 🔴 Порядок блоков — от ответа к обоснованию, а не наоборот. Человек пришёл узнать
 * «что мне посоветуют», а не «какие у портрета метрики»: сначала рекомендация словами,
 * потом числа, на которых она построена. Обратный порядок был в Jinja-версии и заставлял
 * читать таблицу, чтобы добраться до смысла.
 *
 * `metrics`, `plan` и `forecast` приходят свободными объектами — их форму задаёт движок,
 * и у неё есть свои схемы в `/planning/*` (см. `DemoPreview` на бэкенде). Поэтому здесь
 * читаются только те поля, что реально показываются, с явными запасными значениями:
 * предпросмотр не должен падать целиком из-за одного отсутствующего числа.
 */

interface Explanation {
  insight?: string;
  gains?: string[];
  costs?: string[];
}

function explanationOf(plan: DemoPreview["plan"]): Explanation {
  const best = (plan as { best?: { explanation?: Explanation } }).best;
  return best?.explanation ?? {};
}

function metricOf(metrics: DemoPreview["metrics"], key: string): number | null {
  const value = (metrics as Record<string, unknown>)[key];
  return typeof value === "number" ? value : null;
}

/** Тренд прогноза словом, а не английским ключом движка. */
const TRENDS: Record<string, string> = {
  improving: "доход растёт",
  declining: "доход снижается",
  stable: "доход ровный",
};

export function DemoPreviewBody({ preview }: { preview: DemoPreview }) {
  const explanation = explanationOf(preview.plan);
  const free = metricOf(preview.metrics, "free_resource");
  const income = metricOf(preview.metrics, "income_total");
  const expense = metricOf(preview.metrics, "expense_total");
  const trend = (preview.forecast as { trend?: string }).trend;

  return (
    <div className="fp-demo__preview-body">
      {/* Ответ первым: ради него и открывают. */}
      {explanation.insight && <p className="fp-demo__insight">{explanation.insight}</p>}

      {explanation.gains && explanation.gains.length > 0 && (
        <ul className="fp-demo__gains">
          {explanation.gains.map((gain) => (
            <li key={gain}>{gain}</li>
          ))}
        </ul>
      )}

      {/* 🔴 Отказ советовать — не пустое место, а результат: при дефиците система
          сознательно не выдаёт распределение (fail-loud). Без этой строки экран
          выглядел бы сломанным именно на портретах, ради которых его и смотрят. */}
      {!explanation.insight && (
        <p className="fp-demo__insight">
          {t(
            "Для этого портрета система не предлагает распределение: свободных денег нет, " +
              "и вместо «красивой» рекомендации она покажет разбор ситуации.",
          )}
        </p>
      )}

      <dl className="fp-demo__metrics">
        {income !== null && (
          <div>
            <dt>{t("Доход")}</dt>
            <dd>{formatMoney(income)}</dd>
          </div>
        )}
        {expense !== null && (
          <div>
            <dt>{t("Расходы")}</dt>
            <dd>{formatMoney(expense)}</dd>
          </div>
        )}
        {free !== null && (
          <div>
            <dt>{t("Свободные деньги")}</dt>
            <dd>{formatMoney(free)}</dd>
          </div>
        )}
        {trend && TRENDS[trend] && (
          <div>
            <dt>{t("Прогноз")}</dt>
            <dd>{t(TRENDS[trend])}</dd>
          </div>
        )}
      </dl>
    </div>
  );
}
