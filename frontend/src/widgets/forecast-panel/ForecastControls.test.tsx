import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ForecastControls } from "./ForecastControls";

function baseProps() {
  return {
    horizon: 12,
    onHorizonChange: vi.fn(),
    rBench: undefined as number | undefined,
    onRBenchChange: vi.fn(),
    realRBench: 0.139,
    isOverridden: false,
    isFetching: false,
  };
}

describe("ForecastControls — управляемый компонент (§8.4: горизонт + ставка r_bench)", () => {
  it("рендерит select горизонта на переданном значении с опциями 3/6/12/24", () => {
    render(<ForecastControls {...baseProps()} />);
    const select = screen.getByLabelText(/Горизонт/) as HTMLSelectElement;
    expect(select.value).toBe("12");
    expect(screen.getAllByRole("option").map((o) => (o as HTMLOptionElement).value)).toEqual([
      "3",
      "6",
      "12",
      "24",
    ]);
  });

  it("смена select горизонта вызывает onHorizonChange числом", async () => {
    const props = baseProps();
    render(<ForecastControls {...props} />);
    await userEvent.selectOptions(screen.getByLabelText(/Горизонт/), "24");
    expect(props.onHorizonChange).toHaveBeenCalledWith(24);
  });

  it("ползунок ставки стоит на реальной OCR, когда нет override", () => {
    render(<ForecastControls {...baseProps()} />);
    expect(screen.getByLabelText(/Ставка капитализации/)).toHaveValue("13.9");
  });

  it("движение ползунка обновляет видимый процент сразу (запятая, канон денег — CMP-04), но onRBenchChange — только после debounce", () => {
    vi.useFakeTimers();
    const props = baseProps();
    render(<ForecastControls {...props} />);
    fireEvent.change(screen.getByLabelText(/Ставка капитализации/), { target: { value: "20" } });
    // Не "20%" сырым числом — formatPercent даёт запятую и десятичный разряд всегда,
    // тот же формат, что кнопка "Сбросить" и весь остальной продукт.
    expect(screen.getByText("20,0%")).toBeInTheDocument();
    expect(screen.getByLabelText(/Ставка капитализации/)).toHaveAttribute(
      "aria-valuetext",
      "20,0%",
    );
    expect(props.onRBenchChange).not.toHaveBeenCalled();

    vi.advanceTimersByTime(500);
    expect(props.onRBenchChange).toHaveBeenCalledWith(0.2);
    vi.useRealTimers();
  });

  it("дробный шаг ползунка — точка не должна утечь мимо formatPercent (regression: design-critic поймал сырой JS-% на целых значениях, тест их не ловил)", () => {
    vi.useFakeTimers();
    render(<ForecastControls {...baseProps()} />);
    fireEvent.change(screen.getByLabelText(/Ставка капитализации/), { target: { value: "13.5" } });
    expect(screen.getByText("13,5%")).toBeInTheDocument();
    expect(screen.queryByText(/13\.5/)).not.toBeInTheDocument();
    vi.useRealTimers();
  });

  it("кнопка сброса показывается только при isOverridden, возвращает undefined + реальную ставку в слайдер, переносит фокус на ползунок", () => {
    vi.useFakeTimers();
    const props = { ...baseProps(), isOverridden: false };
    const { rerender } = render(<ForecastControls {...props} />);
    expect(screen.queryByRole("button", { name: /Сбросить/ })).not.toBeInTheDocument();

    rerender(<ForecastControls {...props} rBench={0.2} isOverridden={true} />);
    const resetButton = screen.getByRole("button", { name: /Сбросить/ });
    resetButton.focus();
    fireEvent.click(resetButton);
    expect(props.onRBenchChange).toHaveBeenCalledWith(undefined);
    const slider = screen.getByLabelText(/Ставка капитализации/);
    expect(slider).toHaveValue("13.9");
    // a11y-auditor: без явного переноса фокус после исчезновения кнопки улетает в <body>,
    // следующий Tab начинает обход страницы заново — переносим на сам ползунок.
    expect(slider).toHaveFocus();
    vi.useRealTimers();
  });

  it("isFetching — живая область сообщает о пересчёте", () => {
    render(<ForecastControls {...baseProps()} isFetching={true} />);
    expect(screen.getByRole("status")).toHaveTextContent(/Пересчит/);
  });
});
