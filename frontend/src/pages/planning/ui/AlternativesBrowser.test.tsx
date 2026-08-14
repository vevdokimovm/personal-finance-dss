import { describe, expect, it } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AlternativesBrowser } from "./AlternativesBrowser";
import type { PlanAlternative } from "@entities/plan-summary";

const ALT: PlanAlternative = {
  id: "a-3-4",
  name: "Смешанное распределение",
  x_obligations: 10500,
  x_reserve: 10500,
  x_goals: 14000,
  utility: 0.7,
  Rt_new: 35000,
  Lt_new: 1.2,
  Dt_new: 0.3,
  is_recommended: true,
};

describe("AlternativesBrowser — оценка альтернативы без сырой формульной нотации (CMP-05, design-critic v8.10.0)", () => {
  it("после «Показать все» строка альтернативы несёт человеческую подпись «Оценка», не «U = »", async () => {
    render(<AlternativesBrowser alternatives={[ALT]} />);
    await userEvent.click(screen.getByRole("button", { name: /Показать все/ }));

    expect(screen.getByText(/Оценка 0,70/)).toBeInTheDocument();
    expect(screen.queryByText(/U = /)).not.toBeInTheDocument();
  });

  it("подписи сортировки набирают индекс юникодным подстрочным символом (Rₜ), не подчёркиванием (Rt) — <option> не рендерит KaTeX", async () => {
    render(<AlternativesBrowser alternatives={[ALT]} />);
    await userEvent.click(screen.getByRole("button", { name: /Показать все/ }));

    const options = screen.getAllByRole("option").map((o) => o.textContent);
    expect(options).toContain("Свободному потоку (Rₜ)");
    expect(options).toContain("Ликвидности (Lₜ)");
    expect(options.some((o) => o?.includes("Rt") || o?.includes("Lt"))).toBe(false);
  });

  it("метаданные строки (Rt/Lt) набраны через KaTeX, не голым текстом с подчёркиванием", async () => {
    render(<AlternativesBrowser alternatives={[ALT]} />);
    await userEvent.click(screen.getByRole("button", { name: /Показать все/ }));

    await waitFor(() => {
      expect(document.querySelectorAll(".fp-alt-row .katex").length).toBe(2); // Rt + Lt
    });
  });
});
