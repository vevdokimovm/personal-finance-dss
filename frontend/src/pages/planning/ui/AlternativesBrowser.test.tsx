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

/**
 * Сортировки и пропущенные показатели — непокрытый остаток обозревателя.
 *
 * 🔴 **Все поля метрик необязательны по контракту** (`PlanAlternative`), и это не
 * формальность: бэкенд не считает `Rt_new` для альтернатив, нарушающих инвариант.
 * Подставить ноль вместо отсутствующего значения значит показать «резерв 0 ₽» там,
 * где резерв не посчитан вовсе, — и человек сравнит несравнимое.
 */
describe("AlternativesBrowser — сортировки", () => {
  const A = {
    ...ALT,
    id: "a",
    name: "Первая",
    utility: 0.4,
    Rt_new: 10000,
    Lt_new: 0.5,
    Dt_new: 0.5,
  };
  const B = {
    ...ALT,
    id: "b",
    name: "Вторая",
    utility: 0.9,
    Rt_new: 90000,
    Lt_new: 2.0,
    Dt_new: 0.1,
  };

  async function sortBy(label: RegExp | string) {
    render(<AlternativesBrowser alternatives={[A, B]} />);
    await userEvent.click(screen.getByRole("button", { name: /Показать все/ }));
    await userEvent.selectOptions(
      screen.getByRole("combobox"),
      screen.getByRole("option", { name: label }),
    );
  }

  it("по резерву — больше значит выше", async () => {
    /* Резерв — «подушка после хода»: чем больше, тем безопаснее, и сортировка
       обязана ставить безопасное первым. */
    await sortBy(/Rₜ|резерв/i);
    const rows = screen.getAllByRole("listitem");
    expect(rows[0]).toHaveTextContent("Вторая");
  });

  it("🔴 по долговой нагрузке — МЕНЬШЕ значит выше", async () => {
    /* Единственная метрика с обратным порядком: ПДН — это плохо, и «лучшая»
       альтернатива здесь та, у которой он ниже. Перепутать направление значит
       предложить человеку самый закредитованный вариант как рекомендуемый. */
    await sortBy(/Dₜ|нагрузк|ПДН/i);
    const rows = screen.getAllByRole("listitem");
    expect(rows[0]).toHaveTextContent("Вторая");
  });

  it("по покрытию — больше значит выше", async () => {
    await sortBy(/Lₜ|покрыт/i);
    const rows = screen.getAllByRole("listitem");
    expect(rows[0]).toHaveTextContent("Вторая");
  });
});

describe("AlternativesBrowser — непосчитанные показатели", () => {
  it("🔴 отсутствующая метрика показывается как «нет данных», а не как ноль", async () => {
    /* Ноль — это значение, «не посчитано» — его отсутствие. Показать одно вместо
       другого значит соврать о результате расчёта: человек сравнит альтернативу
       с нулевым резервом и альтернативу без резерва как равные. */
    const partial = {
      ...ALT,
      id: "p",
      name: "Без метрик",
      utility: null,
      Rt_new: null,
      Dt_new: null,
    };
    render(<AlternativesBrowser alternatives={[partial]} />);
    await userEvent.click(screen.getByRole("button", { name: /Показать все/ }));

    expect(screen.getAllByText(/нет данных/).length).toBeGreaterThan(0);
    expect(screen.queryByText(/Оценка 0,00/)).not.toBeInTheDocument();
  });

  it("пустой список альтернатив не роняет экран", () => {
    /* `alternatives` необязателен по контракту: расчёт мог не дать ни одной
       допустимой альтернативы (все нарушают инвариант `Rt ≥ 0`). */
    expect(() => render(<AlternativesBrowser />)).not.toThrow();
  });
});

describe("AlternativesBrowser — суммы распределения без значений", () => {
  it("🔴 непосчитанная доля показывается нулём, а покрытие — «нет данных»", async () => {
    /* Разница намеренная. Доля распределения «не задана» и «ноль» — одно и то же:
       на это направление не идёт ничего (`x_* = 0.0` — дефолт схемы, v8.40.0).
       А `Lt_new` без значения — не «покрытия нет», а «покрытие не посчитано»,
       и подставить туда ноль значит объявить альтернативу опасной без оснований. */
    const bare = {
      ...ALT,
      id: "bare",
      name: "Без сумм",
      x_obligations: null,
      x_reserve: null,
      x_goals: null,
      Lt_new: null,
    } as unknown as PlanAlternative;
    render(<AlternativesBrowser alternatives={[bare]} />);
    // Суммы распределения видны только в раскрытом списке.
    await userEvent.click(screen.getByRole("button", { name: /Показать все/ }));

    expect(screen.getByText(/Долг 0/)).toBeInTheDocument();
    expect(screen.getByText(/Резерв 0/)).toBeInTheDocument();
    expect(screen.getAllByText(/нет данных/).length).toBeGreaterThan(0);
  });
});
