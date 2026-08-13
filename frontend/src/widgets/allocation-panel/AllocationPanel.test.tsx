import { describe, expect, it } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AllocationPanel } from "./AllocationPanel";
import type { PlanAlternative } from "@entities/plan-summary";

const TOTAL = 35000;

function alt(
  id: string,
  d: number,
  r: number,
  g: number,
  extra?: Partial<PlanAlternative>,
): PlanAlternative {
  return {
    id,
    name: id,
    x_obligations: (TOTAL * d) / 10,
    x_reserve: (TOTAL * r) / 10,
    x_goals: (TOTAL * g) / 10,
    utility: 0.7,
    Rt_new: TOTAL,
    Lt_new: 1.2,
    Dt_new: 0.3,
    ...extra,
  };
}

// Полная сетка 0..10 по долгу/целям (резерв — остаток), чтобы ползунки могли реально двигаться.
const FULL_GRID: PlanAlternative[] = [];
for (let d = 0; d <= 10; d++) {
  for (let g = 0; g <= 10 - d; g++) {
    FULL_GRID.push(alt(`a-${d}-${g}`, d, 10 - d - g, g));
  }
}
const BEST = { ...FULL_GRID.find((a) => a.id === "a-3-4")!, name: "Смешанное распределение" };

const ALT_RESERVE_ONLY: PlanAlternative = alt("a0200", 0, 10, 0, { name: "Всё в резерв" });

describe("AllocationPanel — составной столбец реагирует на ползунки «что если» (Э5, v8.11.0)", () => {
  it("по умолчанию показывает рекомендацию СППР и суммы best", () => {
    render(<AllocationPanel best={BEST} alternatives={FULL_GRID} />);
    expect(screen.getByText(/Рекомендация СППР \(Смешанное распределение\)/)).toBeInTheDocument();
    expect(screen.getByText(/Досрочное погашение — .*\(30%\)/)).toBeInTheDocument();
    expect(screen.getByText(/Цели — .*\(40%\)/)).toBeInTheDocument();
  });

  it("движение ползунка пересчитывает столбец/легенду и переключает текст на «гипотетический вариант»", () => {
    render(<AllocationPanel best={BEST} alternatives={FULL_GRID} />);
    // 30% -> 40%, цели остаются 40% (сумма не превышает 100%).
    fireEvent.change(screen.getByLabelText("Досрочное погашение"), { target: { value: "4" } });

    expect(screen.getByText(/Гипотетический вариант — не рекомендация СППР/)).toBeInTheDocument();
    expect(screen.getByText(/Досрочное погашение — .*\(40%\)/)).toBeInTheDocument();
  });

  it("кнопка «Вернуть рекомендацию» возвращает исходные суммы и текст рекомендации", async () => {
    render(<AllocationPanel best={BEST} alternatives={FULL_GRID} />);
    fireEvent.change(screen.getByLabelText("Досрочное погашение"), { target: { value: "4" } });
    await userEvent.click(screen.getByRole("button", { name: "Вернуть рекомендацию" }));

    expect(screen.getByText(/Рекомендация СППР \(Смешанное распределение\)/)).toBeInTheDocument();
    expect(screen.getByText(/Досрочное погашение — .*\(30%\)/)).toBeInTheDocument();
  });

  it("диаграмма Санкея (режим «подробно») строится из текущей позиции ползунков, не только из best", async () => {
    render(<AllocationPanel best={BEST} alternatives={FULL_GRID} />);
    fireEvent.change(screen.getByLabelText("Досрочное погашение"), { target: { value: "4" } });
    await userEvent.click(screen.getByRole("button", { name: "Подробно — диаграмма Санкея" }));
    // Санкей декоративен (aria-hidden) — проверяем, что блок вообще смонтирован после смены позиции.
    expect(document.querySelector(".fp-alloc-sankey")).toBeInTheDocument();
  });

  it("при единственной активной категории (вся сумма в резерв) — ни ползунков, ни переключателя Санкея нет", () => {
    render(<AllocationPanel best={ALT_RESERVE_ONLY} alternatives={[ALT_RESERVE_ONLY]} />);
    expect(screen.queryByText("Что если распределить иначе?")).not.toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Подробно — диаграмма Санкея" }),
    ).not.toBeInTheDocument();
  });

  it("дефицит (best=null) — fail-loud сообщение, без ползунков и без падений", () => {
    render(<AllocationPanel best={null} alternatives={[]} />);
    expect(screen.getByText("Плана распределения нет")).toBeInTheDocument();
    expect(screen.queryByText("Что если распределить иначе?")).not.toBeInTheDocument();
  });
});

describe("AllocationPanel — объяснение выбранного плана (батч 0.3/0.4, v8.13.5)", () => {
  const BEST_WITH_EXPLANATION: PlanAlternative = {
    ...BEST,
    explanation: {
      gains: ["Досрочно гасим 10 000 ₽ — самый дорогой кредит."],
      costs: ["2 000 ₽ не пошли в цели — они уже профинансированы."],
      insight:
        "Рекомендуем направить 30% на досрочку, 40% на цели. Решающим оказалось то, " +
        "насколько снизилась долговая нагрузка.",
      dominant_criterion: "Dt",
      counterfactual: {
        available: true,
        alternative_id: "a-2-5",
        utility_gap: 0.03,
        dominant_criterion: "Lt",
        text:
          "Следующий по оценке вариант отстаёт примерно на 3 из 100 баллов — в основном " +
          "тем, насколько выросла подушка безопасности.",
      },
    },
  };

  it("для рекомендации показывает insight, gains, costs и контрфакт", () => {
    render(<AllocationPanel best={BEST_WITH_EXPLANATION} alternatives={FULL_GRID} />);
    expect(screen.getByText(/Решающим оказалось то, насколько снизилась/)).toBeInTheDocument();
    expect(screen.getByText(/Досрочно гасим 10 000 ₽/)).toBeInTheDocument();
    expect(screen.getByText(/2 000 ₽ не пошли в цели/)).toBeInTheDocument();
    expect(screen.getByText(/Следующий по оценке вариант отстаёт/)).toBeInTheDocument();
  });

  it("после отклонения от рекомендации ползунком объяснение скрывается — оно только у best", () => {
    render(<AllocationPanel best={BEST_WITH_EXPLANATION} alternatives={FULL_GRID} />);
    fireEvent.change(screen.getByLabelText("Досрочное погашение"), { target: { value: "4" } });
    expect(screen.queryByText(/Решающим оказалось то,/)).not.toBeInTheDocument();
  });

  it("без explanation (старый кэш/ответ) — панель рендерится без объяснения, без падений", () => {
    render(<AllocationPanel best={BEST} alternatives={FULL_GRID} />);
    expect(screen.getByText(/Рекомендация СППР/)).toBeInTheDocument();
    expect(screen.queryByText(/Решающим оказалось то,/)).not.toBeInTheDocument();
  });

  it("контрфакт unavailable — параграф не рендерится", () => {
    const alt: PlanAlternative = {
      ...BEST,
      explanation: {
        gains: [],
        costs: [],
        insight: "Рекомендуем направить всё в резерв.",
        counterfactual: { available: false },
      },
    };
    render(<AllocationPanel best={alt} alternatives={FULL_GRID} />);
    expect(screen.getByText(/Рекомендуем направить всё в резерв/)).toBeInTheDocument();
    expect(screen.queryByText(/Следующий по оценке вариант/)).not.toBeInTheDocument();
  });
});
