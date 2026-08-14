import { describe, expect, it } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { Formula } from "./Formula";

describe("Formula — единая точка входа для переменных модели (KaTeX, ленивый чанк)", () => {
  it("рендерит fallback, пока тело формулы (katex) ещё не загружено", () => {
    render(<Formula tex="B_{liq}" fallback="B_liq" />);
    expect(screen.getByText("B_liq")).toBeInTheDocument();
    expect(document.querySelector(".katex")).not.toBeInTheDocument();
  });

  it("после загрузки чанка рендерит через KaTeX — не голым текстом с подчёркиванием", async () => {
    render(<Formula tex="B_{liq}" fallback="B_liq" />);
    await waitFor(() => {
      expect(document.querySelector(".katex")).toBeInTheDocument();
    });
    expect(screen.queryByText("B_liq")).not.toBeInTheDocument();
  });

  it("fallback опционален — без него формула тоже рендерится после загрузки чанка", async () => {
    render(<Formula tex="L_t" />);
    await waitFor(() => {
      expect(document.querySelector(".katex")).toBeInTheDocument();
    });
  });
});
