import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { UtilityFormula } from "./UtilityFormula";

const WEIGHTED_SCORES = { Rt: 0.05, Lt: 0.12, Dt: 0.34, Si: 0.03 };

describe("UtilityFormula — раскрываемая по клику формула оценки (CMP-05, design-critic v8.10.0)", () => {
  it("формула скрыта по умолчанию — только кнопка-переключатель, тело (и katex) не загружено", () => {
    render(<UtilityFormula weightedScores={WEIGHTED_SCORES} utility={0.54} />);
    expect(screen.getByRole("button", { name: "Показать формулу оценки" })).toBeInTheDocument();
    expect(document.querySelector(".katex")).not.toBeInTheDocument();
  });

  it("клик раскрывает формулу — тело подгружается лениво (не в основном бандле AllocationPanel)", async () => {
    render(<UtilityFormula weightedScores={WEIGHTED_SCORES} utility={0.54} />);
    await userEvent.click(screen.getByRole("button", { name: "Показать формулу оценки" }));

    expect(screen.getByRole("button", { name: "Скрыть формулу оценки" })).toBeInTheDocument();
    // Suspense — контент появляется асинхронно, после того как чанк UtilityFormulaBody загрузится.
    const katexNodes = await screen.findAllByText(
      (_, el) => el?.classList.contains("katex") ?? false,
    );
    expect(katexNodes.length).toBe(6); // 2 формулы + 4 символа критериев в легенде
  });

  it("кнопка помечена aria-expanded/aria-controls на реально раскрывающуюся область — не декоративную (в отличие от диаграммы Санкея)", async () => {
    render(<UtilityFormula weightedScores={WEIGHTED_SCORES} utility={0.54} />);
    const button = screen.getByRole("button", { name: "Показать формулу оценки" });
    expect(button).toHaveAttribute("aria-expanded", "false");
    await userEvent.click(button);
    expect(button).toHaveAttribute("aria-expanded", "true");
    const controlsId = button.getAttribute("aria-controls");
    // Контейнер с этим id смонтирован сразу по клику (не ждёт ленивую загрузку тела) —
    // aria-controls не должен указывать в пустоту, пока Suspense показывает fallback.
    expect(document.getElementById(controlsId!)).toBeInTheDocument();
  });
});
