import { describe, expect, it, vi } from "vitest";
import { act, fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { WhatIfSliders } from "./WhatIfSliders";
import type { PlanAlternative } from "@entities/plan-summary";

const MATCH: PlanAlternative = {
  id: "a-3-4",
  name: "a-3-4",
  x_obligations: 11850,
  x_reserve: 11850,
  x_goals: 15800,
  utility: 0.7,
  Rt_new: 39500,
  Lt_new: 1.4,
  Dt_new: 0.31,
};

const MATCH_NEAR_THRESHOLD: PlanAlternative = { ...MATCH, id: "a-warn", Dt_new: 0.38 };

function baseProps() {
  return {
    hasDebtOption: true,
    hasGoalsOption: true,
    debtNotch: 3,
    goalsNotch: 4,
    onDebtChange: vi.fn(),
    onGoalsChange: vi.fn(),
    match: MATCH as PlanAlternative | undefined,
    isRecommended: true,
    onReset: vi.fn(),
  };
}

describe("WhatIfSliders — управляемый компонент (state и клампинг живут в AllocationPanel)", () => {
  it("рендерит оба ползунка на переданных значениях и результат для match", () => {
    render(<WhatIfSliders {...baseProps()} />);
    expect(screen.getByLabelText("Досрочное погашение")).toHaveValue("3");
    expect(screen.getByLabelText("Цели")).toHaveValue("4");
    expect(screen.getByText(/Свободный поток:/)).toBeInTheDocument();
    expect(screen.getByText("порог 40%")).toBeInTheDocument();
  });

  it("движение ползунка долга вызывает onDebtChange с новым notch", () => {
    const props = baseProps();
    render(<WhatIfSliders {...props} />);
    fireEvent.change(screen.getByLabelText("Досрочное погашение"), { target: { value: "5" } });
    expect(props.onDebtChange).toHaveBeenCalledWith(5);
  });

  it("движение ползунка целей вызывает onGoalsChange с новым notch", () => {
    const props = baseProps();
    render(<WhatIfSliders {...props} />);
    fireEvent.change(screen.getByLabelText("Цели"), { target: { value: "2" } });
    expect(props.onGoalsChange).toHaveBeenCalledWith(2);
  });

  it("показывает только доступные ползунки (hasDebtOption/hasGoalsOption)", () => {
    render(<WhatIfSliders {...baseProps()} hasGoalsOption={false} />);
    expect(screen.getByLabelText("Досрочное погашение")).toBeInTheDocument();
    expect(screen.queryByLabelText("Цели")).not.toBeInTheDocument();
  });

  it("бейдж «порог 40%, близко» — только когда Dt_new выше DTI_WARN_THRESHOLD (тот же порог, что MetricsGrid)", () => {
    render(<WhatIfSliders {...baseProps()} match={MATCH_NEAR_THRESHOLD} />);
    expect(screen.getByText("порог 40%, близко")).toBeInTheDocument();
  });

  it("match=undefined — сообщение о недоступности вместо Rt/Lt/ПДН, без падений", () => {
    render(<WhatIfSliders {...baseProps()} match={undefined} />);
    // Сообщение есть дважды по смыслу (видимый блок + sr-only живая область для скринридера).
    expect(screen.getAllByText(/не проходит проверку модели/).length).toBeGreaterThanOrEqual(1);
    expect(screen.queryByText(/Свободный поток:/)).not.toBeInTheDocument();
  });

  it("кнопка «Вернуть рекомендацию» показывается только при isRecommended=false и вызывает onReset", async () => {
    const props = baseProps();
    const { rerender } = render(<WhatIfSliders {...props} isRecommended={true} />);
    expect(screen.queryByRole("button", { name: "Вернуть рекомендацию" })).not.toBeInTheDocument();

    rerender(<WhatIfSliders {...props} isRecommended={false} />);
    const resetButton = screen.getByRole("button", { name: "Вернуть рекомендацию" });
    await userEvent.click(resetButton);
    expect(props.onReset).toHaveBeenCalledOnce();
  });

  it("max одного ползунка зависит от текущего значения другого — сумма никогда не превышает 100%", () => {
    render(<WhatIfSliders {...baseProps()} debtNotch={3} goalsNotch={4} />);
    expect(screen.getByLabelText("Досрочное погашение")).toHaveAttribute("max", "6"); // 10 - 4
    expect(screen.getByLabelText("Цели")).toHaveAttribute("max", "7"); // 10 - 3
  });

  it("живая область (aria-live) обновляется с задержкой — не на каждый пропс-рендер, иначе диктор отстаёт от быстрой смены отметок (a11y-auditor)", () => {
    vi.useFakeTimers();
    const props = baseProps();
    const { rerender } = render(<WhatIfSliders {...props} />);
    const liveRegion = () => document.querySelector('[role="status"].sr-only')!;
    expect(liveRegion().textContent).toContain("Свободный поток");

    rerender(<WhatIfSliders {...props} match={undefined} />);
    // Сразу после смены пропса живая область ещё не обновилась — задержка.
    expect(liveRegion().textContent).toContain("Свободный поток");

    act(() => {
      vi.advanceTimersByTime(400);
    });
    expect(liveRegion().textContent).toMatch(/не проходит проверку модели/);
    vi.useRealTimers();
  });
});
