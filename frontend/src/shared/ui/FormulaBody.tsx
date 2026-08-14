import katex from "katex";
import "katex/dist/katex.min.css";

/** Тело `<Formula>` — отдельный модуль, чтобы `katex` (~90 КБ gzip) грузился только там,
 * где реально есть формула, лениво (см. Formula.tsx). Не импортировать напрямую. */
export function FormulaBody({ tex, display = false }: { tex: string; display?: boolean }) {
  const html = katex.renderToString(tex, { throwOnError: false, displayMode: display });
  return <span dangerouslySetInnerHTML={{ __html: html }} />;
}
