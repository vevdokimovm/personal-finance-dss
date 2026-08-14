import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { UtilityFormulaBody } from "./UtilityFormulaBody";

const WEIGHTED_SCORES = { Rt: 0.05, Lt: 0.12, Dt: 0.34, Si: 0.03 };

describe("UtilityFormulaBody — рендер формулы через KaTeX, не голым текстом «U = {u}» (CMP-05)", () => {
  it("рендерит и символьную, и инстанцированную числами формулу через KaTeX", () => {
    render(<UtilityFormulaBody weightedScores={WEIGHTED_SCORES} utility={0.54} />);
    const katexNodes = document.querySelectorAll(".katex");
    expect(katexNodes.length).toBe(2); // символьная + инстанцированная числами

    const body = document.querySelector(".fp-utility-formula__body")!;
    // Числа реально подставлены (не заглушка) — ищем в MathML-annotation (сырой TeX-источник).
    expect(body.textContent).toContain("0{,}05");
    expect(body.textContent).toContain("0{,}54");
  });

  it("расшифровка служебных ключей Rt/Lt/Dt/Si — человеческим языком, не голыми буквами", () => {
    render(<UtilityFormulaBody weightedScores={WEIGHTED_SCORES} utility={0.54} />);
    expect(screen.getByText(/свободный поток/)).toBeInTheDocument();
    expect(screen.getByText(/подушка безопасности/)).toBeInTheDocument();
    expect(screen.getByText(/долговая нагрузка/)).toBeInTheDocument();
    expect(screen.getByText(/продвижение целей/)).toBeInTheDocument();
  });
});
