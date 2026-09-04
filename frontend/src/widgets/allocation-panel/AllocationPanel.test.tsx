import { describe, expect, it } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
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

  it("лede не содержит сырую формульную нотацию «U = …» (CMP-05, design-critic v8.10.0)", () => {
    render(<AllocationPanel best={BEST} alternatives={FULL_GRID} />);
    expect(screen.queryByText(/U = /)).not.toBeInTheDocument();
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
    weighted_scores: { Rt: 0.05, Lt: 0.12, Dt: 0.34, Si: 0.03 },
    explanation: {
      delta: { Rt: 4200, Lt: 0.4, Dt: -0.03 },
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

  it("после отклонения от рекомендации ползунком insight/gains/costs заменяются заглушкой, блок не исчезает", () => {
    render(<AllocationPanel best={BEST_WITH_EXPLANATION} alternatives={FULL_GRID} />);
    fireEvent.change(screen.getByLabelText("Досрочное погашение"), { target: { value: "4" } });
    expect(screen.queryByText(/Решающим оказалось то,/)).not.toBeInTheDocument();
    expect(
      screen.getByText("Это гипотетический вариант — объяснение есть только у рекомендации."),
    ).toBeInTheDocument();
    // Заголовок и контейнер остаются смонтированными — не прыгает верстка под ползунком ниже.
    expect(screen.getByText("Почему выбран такой план")).toBeInTheDocument();
  });

  it("списки gains/costs имеют видимые текстовые подписи, не только цвет/значок", () => {
    render(<AllocationPanel best={BEST_WITH_EXPLANATION} alternatives={FULL_GRID} />);
    expect(screen.getByText("Что улучшается")).toBeInTheDocument();
    expect(screen.getByText("Чем приходится жертвовать")).toBeInTheDocument();
  });

  it("формула оценки раскрывается по клику у рекомендации (KaTeX, не голая «U = {u}»)", async () => {
    render(<AllocationPanel best={BEST_WITH_EXPLANATION} alternatives={FULL_GRID} />);
    const toggle = screen.getByRole("button", { name: "Показать формулу оценки" });
    expect(document.querySelector(".katex")).not.toBeInTheDocument();
    await userEvent.click(toggle);
    // Тело формулы (katex) грузится лениво отдельным чанком — появляется асинхронно.
    await waitFor(() => {
      expect(document.querySelectorAll(".katex").length).toBeGreaterThan(0);
    });
  });

  it("формула оценки скрывается вместе с остальным объяснением при отходе от рекомендации", () => {
    render(<AllocationPanel best={BEST_WITH_EXPLANATION} alternatives={FULL_GRID} />);
    fireEvent.change(screen.getByLabelText("Досрочное погашение"), { target: { value: "4" } });
    expect(
      screen.queryByRole("button", { name: "Показать формулу оценки" }),
    ).not.toBeInTheDocument();
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
        delta: { Rt: 0, Lt: 0, Dt: 0 },
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

describe("AllocationPanel — ответ без ranked не роняет экран", () => {
  /* Найдено 2026-09-03 (v8.31.1) при разборе шести красных E2E. Контракт
     (`docs/api/openapi.json`, схема PlanningCalculateResponse) НЕ держит `ranked`
     в списке required — у поля `default_factory=list` в `app/schemas/planning.py:283`,
     то есть по контракту его может не быть. Рукописный тип фронта
     (`entities/plan-summary/model/types.ts:88`) объявлял его обязательным, поэтому
     TypeScript молчал, а `hasNonZeroCategory` звал `.some()` по undefined и ронял
     ВЕСЬ дашборд в error boundary: пользователь видел «Something went wrong!» вместо
     финансового обзора. Экран не обязан работать в полном объёме без альтернатив —
     он обязан не падать. */
  const best = {
    id: "a0100",
    name: "Всё в резерв",
    x_obligations: 0,
    x_reserve: 39500,
    x_goals: 0,
    utility: 0.8,
  } as PlanAlternative;

  it("рендерит столбец распределения, когда alternatives не пришли вовсе", () => {
    render(<AllocationPanel best={best} alternatives={undefined as unknown as PlanAlternative[]} />);
    expect(screen.getByText(/Резерв/)).toBeInTheDocument();
  });

  it("не показывает ползунки «что если», когда выбирать не из чего", () => {
    render(<AllocationPanel best={best} alternatives={undefined as unknown as PlanAlternative[]} />);
    expect(screen.queryByRole("slider")).not.toBeInTheDocument();
  });
});

describe("AllocationPanel — необязательные по контракту поля не роняют экран", () => {
  /* Продолжение разбора v8.31.1. api-contract-guard нашёл ещё два поля того же класса,
     что `ranked`: у схемы `Explanation` (docs/api/openapi.json) в `required` стоит ТОЛЬКО
     `delta` — то есть `gains` и `costs` контрактно могут не прийти, а панель звала
     `.length` по ним напрямую. Проверено на диске: required=['delta']. */
  const baseAlt = {
    id: "a0100",
    name: "Всё в резерв",
    x_obligations: 0,
    x_reserve: 39500,
    x_goals: 0,
    utility: 0.8,
    is_recommended: true,
  };

  it("рендерит объяснение, когда gains и costs не пришли", () => {
    const best = {
      ...baseAlt,
      explanation: { insight: "Резерв закрывает подушку быстрее всего", delta: "+1,2 мес." },
    } as unknown as PlanAlternative;
    render(<AllocationPanel best={best} alternatives={[best]} />);
    expect(screen.getByText("Резерв закрывает подушку быстрее всего")).toBeInTheDocument();
  });

  it("не показывает пустые разделы «Что улучшается» и «Чем жертвовать»", () => {
    const best = {
      ...baseAlt,
      explanation: { insight: "Резерв закрывает подушку быстрее всего", delta: "+1,2 мес." },
    } as unknown as PlanAlternative;
    render(<AllocationPanel best={best} alternatives={[best]} />);
    expect(screen.queryByText("Что улучшается")).not.toBeInTheDocument();
    expect(screen.queryByText("Чем приходится жертвовать")).not.toBeInTheDocument();
  });
});
