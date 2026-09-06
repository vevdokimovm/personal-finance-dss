import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
vi.mock("@tanstack/react-router", async () => {
  const actual =
    await vi.importActual<typeof import("@tanstack/react-router")>("@tanstack/react-router");
  return {
    ...actual,
    Link: ({ children, to }: { children: React.ReactNode; to: string }) => (
      <a href={to}>{children}</a>
    ),
  };
});

import { CrisisPlanSection } from "./CrisisPlanSection";
import type { CrisisPlan } from "@entities/plan-summary";

function plan(overrides: Partial<CrisisPlan> = {}): CrisisPlan {
  return {
    deficit: 5000,
    runway_months: 2.4,
    max_affordable_expenses: 13000,
    // 🔴 Значение из БЭКЕНДА (`crisis.py`): `recoverable_from_liquidity`, `critical`,
    // `cut_required`. Первая редакция подставляла `manageable`, которого не бывает,
    // и тест зеленел на ветке «неизвестное значение» — то есть проверял фолбэк,
    // а не основной сценарий (design-critic).
    severity: "cut_required",
    summary: "Расходы превышают доход на 5 000 ₽ в месяц.",
    actions: [],
    ...overrides,
  } as CrisisPlan;
}

/**
 * 🔴 Кризисный план существовал с v6.0.0 и не показывался НИКОМУ.
 *
 * `app/core/crisis.py` считает разбор для человека с отрицательным потоком: закрытие
 * кредита из ликвидности, сокращение расходов до нуля дефицита, потолок трат, заморозка
 * целей, реструктуризация самого дорогого кредита, запас хода. Охват — 9697/9697
 * дефицитных портретов. `grep crisis` по `frontend/src` давал **ноль** совпадений.
 *
 * Владелец, поручивший эту фичу, считал, что её нет: он её не видел.
 *
 * Цена выше, чем у spending-advice: человек в дефиците — тот, кому продукт нужнее всего.
 * Вместо разбора он видел пустое место там, где алгоритм отказался строить обычный план.
 */
describe("CrisisPlanSection — разбор при отрицательном потоке", () => {
  it("называет размер дефицита числом, а не «денег не хватает»", () => {
    render(<CrisisPlanSection plan={plan({ deficit: 5000 })} />);
    expect(screen.getByTestId("fp-crisis-deficit")).toHaveTextContent(/5\s?000/);
  });

  it("показывает запас хода в месяцах", () => {
    /* Runway — единственное число, отвечающее на вопрос «сколько у меня времени».
       Без него человек не знает, решать проблему сегодня или в течение полугода. */
    render(<CrisisPlanSection plan={plan({ runway_months: 2.4 })} />);
    expect(screen.getByTestId("fp-crisis-runway")).toHaveTextContent(/2[,.]4|2 месяц/i);
  });

  it("бессрочный запас хода не превращается в «0 месяцев»", () => {
    /* `runway_months` необязателен: при нулевом дефиците запас не определён,
       а ноль читается как «денег не осталось» — противоположное по смыслу. */
    render(<CrisisPlanSection plan={plan({ runway_months: null })} />);
    expect(screen.queryByTestId("fp-crisis-runway")).not.toBeInTheDocument();
  });

  it("показывает потолок трат — прямой ответ на «сколько можно тратить»", () => {
    render(<CrisisPlanSection plan={plan({ max_affordable_expenses: 13000 })} />);
    expect(screen.getByTestId("fp-crisis-ceiling")).toHaveTextContent(/13\s?000/);
  });
});

describe("CrisisPlanSection — действия читаются по своему виду", () => {
  it("сокращение расходов: сумма и на сколько это от текущих трат", () => {
    render(
      <CrisisPlanSection
        plan={plan({
          actions: [
            {
              type: "cut_expenses",
              amount: 5000,
              share_of_expenses: 0.28,
              max_affordable_expenses: 13000,
            },
          ],
        })}
      />,
    );
    const action = screen.getByTestId("fp-crisis-action-cut_expenses");
    expect(action).toHaveTextContent(/5\s?000/);
    expect(action).toHaveTextContent(/28/);
  });

  it("реструктуризация называет КОНКРЕТНЫЙ кредит, ставку и варианты", () => {
    /* 🔴 «Обратитесь в банк» без имени кредита и ставки — совет, который человек
       не может исполнить, не открыв другой экран и не вспомнив, какой из кредитов
       самый дорогой. Ради этого модель и выбирает приоритетный. */
    render(
      <CrisisPlanSection
        plan={plan({
          actions: [
            {
              type: "restructure_debt",
              loan: "Кредитная карта",
              // Ставка — ДОЛЯ: 0.39 = 39% годовых (`Numeric(6, 4)`). Подача 39
              // означала 3900% и скрыла лишнее деление на 100 в компоненте.
              interest_rate: 0.39,
              monthly_payment: 7000,
              options: ["рефинансирование", "реструктуризация", "кредитные каникулы"],
            },
          ],
        })}
      />,
    );
    const action = screen.getByTestId("fp-crisis-action-restructure_debt");
    expect(action).toHaveTextContent(/Кредитная карта/);
    expect(action).toHaveTextContent(/39/);
    expect(action).toHaveTextContent(/рефинансирован/i);
  });

  it("заморозка целей перечисляет, какие именно цели встают на паузу", () => {
    render(
      <CrisisPlanSection
        plan={plan({ actions: [{ type: "freeze_goals", goals: ["Отпуск", "Машина"] }] })}
      />,
    );
    const action = screen.getByTestId("fp-crisis-action-freeze_goals");
    expect(action).toHaveTextContent(/Отпуск/);
    expect(action).toHaveTextContent(/Машина/);
  });

  it("закрытие кредита из ликвидности показывает, что станет с потоком", () => {
    /* Балансовый ход имеет смысл, только если человек видит результат: поток
       разворачивается в плюс. Без `new_rt` это просто «потратьте накопления». */
    render(
      <CrisisPlanSection
        plan={plan({
          actions: [
            {
              type: "close_debts_from_liquidity",
              steps: [],
              bliq_used: 90000,
              bliq_remaining: 30000,
              new_rt: 1500,
              new_lt: 1.7,
            },
          ],
        })}
      />,
    );
    const action = screen.getByTestId("fp-crisis-action-close_debts_from_liquidity");
    expect(action).toHaveTextContent(/1\s?500/);
  });

  it("незнакомый вид действия не роняет экран", () => {
    /* Модель может завести новый тип раньше, чем фронт про него узнает.
       Уронить весь разбор из-за одной незнакомой строки — потерять и остальные
       советы, которые человеку нужны сейчас. */
    render(<CrisisPlanSection plan={plan({ actions: [{ type: "some_future_action" }] })} />);
    expect(screen.getByTestId("fp-crisis-deficit")).toBeInTheDocument();
  });
});

describe("CrisisPlanSection — числа не врут", () => {
  it("ставка печатается как есть, а не в сто раз меньше", () => {
    /* 🔴 `interest_rate` — доля (0.39 = 39%). Лишнее деление на 100 давало «0,4 %»
       на карточке «Договориться с банком»: человек в дефиците читал, что его самый
       дорогой кредит — под доли процента. Тот же класс уже ловится регресс-тестом
       на соседнем экране (`AssetsPage.test.tsx`), сюда он не доехал. */
    render(
      <CrisisPlanSection
        plan={plan({
          actions: [
            {
              type: "restructure_debt",
              loan: "Карта",
              interest_rate: 0.39,
              monthly_payment: 7000,
              options: ["рефинансирование"],
            },
          ],
        })}
      />,
    );
    const action = screen.getByTestId("fp-crisis-action-restructure_debt");
    expect(action).toHaveTextContent(/39/);
    expect(action).not.toHaveTextContent(/0,4\s?%/);
  });

  it("дробный запас хода склоняется как «месяца», а не «месяц»", () => {
    /* `plural(Math.round(0.5))` давал «0,5 месяц». В русском при дробном всегда
       родительный единственного. Случай `runway < 1` — это ровно ветка `critical`,
       то есть ошибка вылезала у самого напуганного человека. */
    render(<CrisisPlanSection plan={plan({ runway_months: 0.5 })} />);
    expect(screen.getByTestId("fp-crisis-runway")).toHaveTextContent(/0,5 месяца/);
  });

  it("целый запас хода склоняется по числу", () => {
    render(<CrisisPlanSection plan={plan({ runway_months: 1 })} />);
    expect(screen.getByTestId("fp-crisis-runway")).toHaveTextContent(/1 месяц(?!а)/);
  });

  it("действие без ключевых полей не рисуется выдуманными нулями", () => {
    /* 🔴 `?? 0` печатал «останется 0 ₽ в месяц» и ««», 0 % годовых» с видом
       достоверных чисел. На деньгах ложная точность дороже пропуска карточки. */
    render(<CrisisPlanSection plan={plan({ actions: [{ type: "restructure_debt" }] })} />);
    expect(screen.queryByTestId("fp-crisis-action-restructure_debt")).not.toBeInTheDocument();
  });
});

describe("CrisisPlanSection — тяжесть положения видна, а не только описана", () => {
  it("критическое положение помечено на секции", () => {
    /* Спокойный тон — не значит плоский. `critical` (накоплений меньше чем на месяц)
       и `recoverable_from_liquidity` (решается одним ходом) выглядели побайтово
       одинаково. `data-severity` даёт CSS второй канал сверх текста — без заливки
       и без паники, но и без потери сигнала. */
    const { container } = render(<CrisisPlanSection plan={plan({ severity: "critical" })} />);
    expect(container.querySelector("[data-severity='critical']")).not.toBeNull();
  });

  it("незнакомая тяжесть не выдаётся за среднюю", () => {
    /* Тяжесть здесь передаётся ТОЛЬКО текстом, значит ошибка в тексте — ошибка
       в единственном носителе смысла. Молча показать «средний» уровень при новом,
       более строгом — занизить опасность. */
    const { container } = render(<CrisisPlanSection plan={plan({ severity: "unknown_level" })} />);
    expect(container.querySelector("[data-severity='unknown_level']")).not.toBeNull();
  });
});

describe("CrisisPlanSection — действия ведут туда, где их делают", () => {
  it("заморозка целей ведёт на экран целей", () => {
    /* [IA-04]: цифры есть, действия нет — тупик. «Поставьте цели на паузу» без
       ссылки заставляет человека искать раздел самому, в состоянии стресса. */
    render(
      <CrisisPlanSection plan={plan({ actions: [{ type: "freeze_goals", goals: ["Отпуск"] }] })} />,
    );
    const action = screen.getByTestId("fp-crisis-action-freeze_goals");
    expect(action.querySelector("a")).toHaveAttribute("href", "/goals");
  });

  it("сокращение расходов ведёт на операции", () => {
    render(
      <CrisisPlanSection
        plan={plan({
          actions: [{ type: "cut_expenses", amount: 5000, share_of_expenses: 0.28 }],
        })}
      />,
    );
    const action = screen.getByTestId("fp-crisis-action-cut_expenses");
    expect(action.querySelector("a")).toHaveAttribute("href", "/transactions");
  });

  it("реструктуризация ведёт на кредиты", () => {
    render(
      <CrisisPlanSection
        plan={plan({
          actions: [
            {
              type: "restructure_debt",
              loan: "Карта",
              interest_rate: 0.39,
              monthly_payment: 7000,
              options: ["рефинансирование"],
            },
          ],
        })}
      />,
    );
    const action = screen.getByTestId("fp-crisis-action-restructure_debt");
    expect(action.querySelector("a")).toHaveAttribute("href", "/obligations");
  });
});

describe("CrisisPlanSection — тон", () => {
  it("не показывается при отсутствии плана", () => {
    const { container } = render(<CrisisPlanSection plan={null} />);
    expect(container.textContent).toBe("");
  });

  it("объясняет, почему обычного плана нет", () => {
    /* Человек пришёл за распределением свободных денег и не получил его.
       Без объяснения он решит, что продукт сломался, — а свободных денег
       просто нет, и это сам по себе ответ. */
    render(<CrisisPlanSection plan={plan()} />);
    expect(
      screen.getByRole("heading", { name: /денег не хватает|дефицит|свободных денег/i }),
    ).toBeVisible();
  });
});
