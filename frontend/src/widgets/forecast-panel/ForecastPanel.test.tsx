import type { ReactElement, ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";
import { act, render, screen, waitFor } from "@testing-library/react";
import { Area } from "recharts";
import type { TooltipPayload } from "recharts/types/state/tooltipSlice";
import { ForecastPanel, ForecastTooltip } from "./ForecastPanel";
import { buildForecastChartData } from "./buildForecastChartData";
import type { ForecastResult } from "@entities/plan-summary";
import { makeForecast, makeForecastPoint } from "@shared/lib/test/forecastFixtures";

// Recharts НЕ рендерит <Area> как обычный React-компонент в DOM — AreaChart
// читает children через Children.map чисто для чтения props и рисует SVG
// сама, минуя обычный рендер. Поэтому мокать Area бесполезно (мок никогда
// не вызывается) и проверять пиксели в jsdom без ResizeObserver нестабильно.
// ForecastPanel — чистая функция без хуков: вызываем её напрямую и обходим
// возвращённое дерево React-элементов, находя реальные <Area> по type.
interface AreaLikeProps {
  children?: ReactNode;
  stackId?: string;
  fill?: string;
  /* `dataKey` — какое поле рисует Area. Добавлен в v8.48.0 вместе с проверкой, что
     полоса построена на ГРАНИЦАХ интервала, а не на медиане. */
  dataKey?: string;
}

function findElementsByType(
  node: ReactNode,
  type: unknown,
  out: ReactElement<AreaLikeProps>[] = [],
): ReactElement<AreaLikeProps>[] {
  if (node == null || typeof node !== "object") return out;
  if (Array.isArray(node)) {
    node.forEach((n) => findElementsByType(n, type, out));
    return out;
  }
  const el = node as ReactElement<AreaLikeProps>;
  if (el.type === type) out.push(el);
  if (el.props?.children) {
    findElementsByType(el.props.children, type, out);
  }
  return out;
}

const FORECAST_ANNA: ForecastResult = makeForecast({
  current: { Bt: 265000, Rt: 39500, Lt: 0, Dt: 0.347 },
  horizon: 12,
  forecast: [
    makeForecastPoint({ period: 6, Rt: 400000, Rt_p10: 350000, Rt_p90: 450000 }),
    makeForecastPoint({ period: 12, Rt: 813519, Rt_p10: 682866, Rt_p90: 952920 }),
  ],
  r_bench: 0.139,
  real_r_bench: 0.139,
  r_bench_source: "cbr_keyrate_post_tax",
});

// pavel — дефицит: p10/p90 ОБА отрицательные. Старый баг (Area без stackId,
// fill=var(--c-bg)) на этом фикстуре случайно не проявлялся визуально —
// проверка нужна именно на нём, не только на положительном anna.
const FORECAST_PAVEL: ForecastResult = makeForecast({
  current: { Bt: 50000, Rt: -63000, Lt: 0, Dt: 0.822 },
  horizon: 12,
  forecast: [
    makeForecastPoint({ period: 6, Rt: -350000, Rt_p10: -450000, Rt_p90: -280000 }),
    makeForecastPoint({ period: 12, Rt: -709583, Rt_p10: -823544, Rt_p90: -587992 }),
  ],
  r_bench: 0.139,
  real_r_bench: 0.139,
  r_bench_source: "cbr_keyrate_post_tax",
});

describe("buildForecastChartData", () => {
  it.each([
    ["anna (положительный домен)", FORECAST_ANNA],
    ["pavel (отрицательный домен, дефицит)", FORECAST_PAVEL],
  ])("Rt_p10 + Rt_band === Rt_p90 на каждой точке — %s", (_label, forecast) => {
    const data = buildForecastChartData(forecast);
    expect(data.length).toBeGreaterThan(0);
    for (const point of data) {
      expect(point.Rt_p10 + point.Rt_band).toBeCloseTo(point.Rt_p90, 6);
    }
  });

  it("Rt_band неотрицателен (p90 >= p10 всегда, по определению интервала)", () => {
    for (const forecast of [FORECAST_ANNA, FORECAST_PAVEL]) {
      for (const point of buildForecastChartData(forecast)) {
        expect(point.Rt_band).toBeGreaterThanOrEqual(0);
      }
    }
  });
});

// Три Area/Line на графике (Rt/Rt_band/Rt_p10, две служебные для стека закраски диапазона) —
// раньше recharts рисовал тултип-строку НА КАЖДУЮ, сырые dataKey утекали в интерфейс как есть
// («Rt_band :», «Rt_p10 :» пустой строкой). Мокаем то же множество записей, что реально даёт
// recharts на графике с тремя сериями в одной точке.
function mockPayload(): TooltipPayload {
  return [
    { dataKey: "Rt_p10", value: 350000, graphicalItemId: "a" },
    { dataKey: "Rt_band", value: 50000, graphicalItemId: "b" },
    { dataKey: "Rt", value: 400000, graphicalItemId: "c" },
  ] as unknown as TooltipPayload;
}

describe("ForecastPanel — предупреждение о дефиците", () => {
  /* 🔴 Найдено аудитом independent-expert 05.09.2026: `deficit_alert` — месяц, когда
     денег не хватит, — считался на бэкенде (`forecasting.py:157`), лежал в контракте
     и НЕ показывался нигде. CHANGELOG [8.48.0] сам называл его «самым важным, что
     прогноз умеет сказать»: починка типов сделала поле видимым для TypeScript,
     а экран под него не завели. Классический «замысел зафиксирован, кодом не стал». */

  it("называет месяц и сумму разрыва, когда дефицит предсказан", () => {
    render(
      <ForecastPanel
        forecast={makeForecast({
          deficit_alert: { period: 4, gap: 12000, pessimistic: false },
        })}
      />,
    );
    const alert = screen.getByRole("alert");
    // Месяц и сумма — оба обязаны быть в тексте: «денег не хватит» без «когда»
    // и «сколько» не даёт человеку ничего, кроме тревоги.
    expect(alert.textContent).toMatch(/4-м месяце/);
    expect(alert.textContent).toMatch(/12/);
    expect(alert.textContent).toMatch(/₽/);
  });

  /* Пессимистичный сценарий — другой смысл: дефицита в основном прогнозе нет,
     он появляется только в нижней границе интервала. Показывать оба одинаково
     значило бы пугать человека тем, что скорее всего не случится. */
  it("различает дефицит основного прогноза и пессимистичного сценария", () => {
    render(
      <ForecastPanel
        forecast={makeForecast({
          deficit_alert: { period: 5, gap: 3000, pessimistic: true },
        })}
      />,
    );
    expect(screen.getByRole("alert")).toHaveTextContent(/неблагоприятн|пессимистич/i);
  });

  it("молчит, когда дефицита не предвидится", () => {
    render(<ForecastPanel forecast={makeForecast()} />);
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });
});

describe("ForecastTooltip — только медиана, не сырые dataKey служебных серий", () => {
  it("не активен — ничего не рендерит", () => {
    const { container } = render(
      <ForecastTooltip active={false} payload={mockPayload()} label={6} />,
    );
    expect(container).toBeEmptyDOMElement();
  });

  it("из трёх записей payload (Rt/Rt_band/Rt_p10) рендерится ровно одна строка — медиана", () => {
    render(<ForecastTooltip active payload={mockPayload()} label={6} />);
    expect(screen.getByText("6 мес")).toBeInTheDocument();
    expect(screen.getByText(/400 000/)).toBeInTheDocument();
    // Раньше здесь были ещё «Rt_band :» и «Rt_p10 :» — служебные dataKey голым текстом.
    expect(screen.queryByText(/Rt_band/)).not.toBeInTheDocument();
    expect(screen.queryByText(/Rt_p10/)).not.toBeInTheDocument();
    expect(screen.queryByText(/350 000/)).not.toBeInTheDocument();
    expect(screen.queryByText(/50 000/)).not.toBeInTheDocument();
  });

  it("подпись медианы — через KaTeX (Rₜ), не голое «Rt» plain-текстом", async () => {
    render(<ForecastTooltip active payload={mockPayload()} label={6} />);
    await waitFor(() => {
      expect(document.querySelector(".katex")).toBeInTheDocument();
    });
  });

  it("сейчас (period=0) — не «0 мес»", () => {
    render(<ForecastTooltip active payload={mockPayload()} label={0} />);
    expect(screen.getByText("сейчас")).toBeInTheDocument();
  });
});

describe("ForecastPanel — конфигурация полосы p10-p90", () => {
  it.each([
    ["anna", FORECAST_ANNA],
    ["pavel (дефицит)", FORECAST_PAVEL],
  ])(
    "два Area делят один stackId, ни один не красит фигуру цветом фона — %s",
    (_label, forecast) => {
      const tree = ForecastPanel({ forecast });
      const areas = findElementsByType(tree, Area);

      expect(areas).toHaveLength(2);
      const stackIds = new Set(areas.map((a) => a.props.stackId));
      expect(stackIds.size).toBe(1);
      expect([...stackIds][0]).toBeTruthy();

      // Регресс-инвариант: ни у одной Area заливка не завязана на цвет фона
      // страницы/панели — старый баг держался ровно на этом совпадении цветов.
      for (const area of areas) {
        expect(area.props.fill).not.toBe("var(--c-bg)");
        expect(area.props.fill).not.toBe("var(--c-surface)");
      }
      // Ровно одна невидимая база и одна видимая полоса.
      const fills = areas.map((a) => a.props.fill).sort();
      expect(fills).toEqual(["none", "var(--c-accent-bg)"]);

      /* 🔴 И полоса построена на ГРАНИЦАХ интервала, а не на медиане. Проверка добавлена
         в v8.48.0: мутация `dataKey="Rt_p10"` → `"Rt"` не роняла ни одного теста, то есть
         коридор неопределённости мог схлопнуться в линию, и никто бы не заметил.
         Прогноз без коридора читается как обещание точной суммы — ровно то, чего
         вероятностный расчёт не даёт. */
      const keys = areas.map((a) => a.props.dataKey).sort();
      expect(keys).toEqual(["Rt_band", "Rt_p10"]);
    },
  );
});

describe("ForecastPanel — сценарий «что если» и живая область результата (design-critic/a11y-auditor, v8.24.0)", () => {
  it("пометка сценария появляется только когда r_bench_source === request, не при реальной ставке", () => {
    const { rerender } = render(<ForecastPanel forecast={FORECAST_ANNA} />);
    expect(screen.queryByText(/Сценарий «что если»/)).not.toBeInTheDocument();

    const overridden = { ...FORECAST_ANNA, r_bench: 0.25, r_bench_source: "request" };
    rerender(<ForecastPanel forecast={overridden} />);
    expect(
      screen.getByText(/Сценарий «что если»: график посчитан со ставкой 25,0%/),
    ).toBeInTheDocument();
  });

  // Не screen.getByRole("status") — тот же приём, что WhatIfSliders.test.tsx: sr-only регион
  // testing-library в jsdom иногда не засчитывает как accessible по вычисленным стилям.
  // formatMoney разделяет разряды неразрывным пробелом (U+00A0, канон денег проекта) —
  // нормализуем в обычный перед сравнением, иначе строковый литерал с обычным пробелом
  // никогда не совпадёт с реальным DOM.
  function anyStatusContains(text: string): boolean {
    return Array.from(document.querySelectorAll('[role="status"]')).some((el) =>
      el.textContent?.replace(/\u00a0/g, " ").includes(text),
    );
  }

  it("живая область объявляет обновлённый результат после дебаунса — не на первом рендере, не мгновенно", () => {
    vi.useFakeTimers();
    const { rerender } = render(
      <ForecastPanel
        forecast={FORECAST_ANNA}
        horizon={12}
        onHorizonChange={vi.fn()}
        rBench={undefined}
        onRBenchChange={vi.fn()}
      />,
    );
    expect(anyStatusContains("900 000")).toBe(false);

    const updated: ForecastResult = {
      ...FORECAST_ANNA,
      forecast: [makeForecastPoint({ period: 12, Rt: 900000, Rt_p10: 800000, Rt_p90: 1000000 })],
    };
    rerender(
      <ForecastPanel
        forecast={updated}
        horizon={12}
        onHorizonChange={vi.fn()}
        rBench={undefined}
        onRBenchChange={vi.fn()}
      />,
    );
    // Сразу после смены пропса ещё не объявлено — задержка, не каждое промежуточное значение.
    expect(anyStatusContains("900 000")).toBe(false);
    act(() => {
      vi.advanceTimersByTime(300);
    });
    expect(anyStatusContains("900 000")).toBe(true);
    vi.useRealTimers();
  });

  /* 🔴 `aria-hidden` скрывает график от скринридера, но НЕ убирает его содержимое из
     порядка обхода: Recharts вставляет внутрь фокусируемые узлы. Получается ловушка —
     Tab уводит фокус в элемент, о котором скринридер молчит, и пользователь не понимает,
     где он находится (WCAG 4.1.2, axe `aria-hidden-focus`).

     Найдено axe-тиром `full` после того, как он впервые реально исполнился: до v8.45.0
     тир не запускался (не было браузера нужной версии), а до этого проверял Jinja. */
  it("декоративный график не ловит фокус клавиатуры", () => {
    const { container } = render(<ForecastPanel forecast={FORECAST_ANNA} />);
    const chart = container.querySelector(".fp-forecast-chart");
    expect(chart).not.toBeNull();
    expect(chart).toHaveAttribute("aria-hidden", "true");
    // `inert` — единственное, что и скрывает от AT, и вынимает поддерево из Tab-порядка.
    expect(chart).toHaveAttribute("inert");
  });
});
