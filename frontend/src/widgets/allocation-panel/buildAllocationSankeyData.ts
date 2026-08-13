import { t } from "@shared/lib/i18n/t";
import type { PlanAlternative } from "@entities/plan-summary";

export interface SankeyNodeDatum {
  name: string;
  /** Токен цвета узла/связи. Отсутствует у источника — рисуется нейтральным. */
  color?: string;
}

export interface SankeyLinkDatum {
  source: number;
  target: number;
  value: number;
}

export interface AllocationSankeyData {
  nodes: SankeyNodeDatum[];
  links: SankeyLinkDatum[];
}

const SOURCE_INDEX = 0;

/** Санкей рисует только положительные потоки — recharts не строит связь с value<=0,
 * поэтому категории с нулевой суммой не входят узлом (тот же принцип, что и в fp-alloc-bar:
 * там сегмент с pct=0 тоже не рендерится, `x > 0` перед каждым <div>).
 *
 * Принимает не обязательно `best` целиком — AllocationPanel зовёт эту же функцию и для текущей
 * позиции ползунков «что если» (не только для рекомендации), только с этими тремя полями. */
export function buildAllocationSankeyData(
  amounts: Pick<PlanAlternative, "x_obligations" | "x_reserve" | "x_goals">,
): AllocationSankeyData {
  const categories: (SankeyNodeDatum & { value: number })[] = [
    { name: t("Досрочное погашение"), color: "var(--c-red)", value: amounts.x_obligations },
    { name: t("Резерв"), color: "var(--c-amber)", value: amounts.x_reserve },
    { name: t("Цели"), color: "var(--c-green)", value: amounts.x_goals },
  ];

  const nodes: SankeyNodeDatum[] = [{ name: t("Свободные деньги") }];
  const links: SankeyLinkDatum[] = [];

  for (const { value, ...node } of categories) {
    if (value > 0) {
      nodes.push(node);
      links.push({ source: SOURCE_INDEX, target: nodes.length - 1, value });
    }
  }

  return { nodes, links };
}
