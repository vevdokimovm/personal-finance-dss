import { Suspense, lazy, type ReactNode } from "react";

/**
 * Единая точка входа для переменных и формул модели в интерфейсе (`docs/math_model.md`).
 * Раньше такие обозначения либо утекали в UI голым текстом с подчёркиванием («B_liq/E»,
 * «Rt» — CMP-05, дёшево и непонятно), либо их приходилось стирать вовсе, потому что
 * статический импорт `katex` (~90 КБ gzip) раздувал бандл каждой страницы, где мелькала хоть
 * одна переменная (найдено на AllocationPanel — vite build поймал chunk >500 КБ).
 *
 * Решение — здесь: тело рендера (`FormulaBody`) лежит в отдельном ленивом чанке, подгружается
 * один раз при первом использовании ГДЕ УГОДНО в приложении и остаётся в кэше браузера для
 * всех следующих формул на этой и других страницах. Использовать `<Formula tex="..." />` для
 * ЛЮБОЙ переменной модели, а не голый текст с подчёркиванием и не plain-text буквы.
 */
const LazyFormulaBody = lazy(() =>
  import("./FormulaBody").then((m) => ({ default: m.FormulaBody })),
);

export function Formula({
  tex,
  display = false,
  fallback = null,
}: {
  tex: string;
  display?: boolean;
  fallback?: ReactNode;
}) {
  return (
    <Suspense fallback={fallback}>
      <LazyFormulaBody tex={tex} display={display} />
    </Suspense>
  );
}
