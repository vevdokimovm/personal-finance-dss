import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
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
});
