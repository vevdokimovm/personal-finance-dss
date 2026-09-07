import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { SpendingPage } from "./SpendingPage";
import type { SpendingAdviceResponse } from "@entities/spending";

const { adviceMock } = vi.hoisted(() => ({ adviceMock: vi.fn() }));

/* Панель согласия — предмет своего файла тестов (`entities/consents`). Настоящая
   тянет `QueryClientProvider` во ВСЕ тесты страницы ради одной ветки; здесь она
   мокнута маркером, как `DemoSandbox` в `DashboardPage.test.tsx`, и проверяется
   только то, что страница показывает именно её, а не общий текст ошибки. */
vi.mock("@entities/consents", () => ({
  ConsentRequiredPanel: () => <button type="button">Дать согласие</button>,
}));

vi.mock("@entities/spending", async () => {
  const actual = await vi.importActual<typeof import("@entities/spending")>("@entities/spending");
  return { ...actual, useSpendingAdvice: () => adviceMock() };
});

function query(overrides: Record<string, unknown> = {}) {
  return {
    data: undefined,
    isLoading: false,
    isError: false,
    error: null,
    refetch: vi.fn().mockResolvedValue({}),
    ...overrides,
  };
}

function payload(overrides: Partial<SpendingAdviceResponse> = {}): SpendingAdviceResponse {
  return {
    current_period: "2026-09",
    months_window: 6,
    months_with_data: 6,
    advice: [],
    stats: [],
    merchant_insights: [],
    temporal_patterns: [],
    goal_impact: [],
    total_potential_saving: 0,
    ...overrides,
  } as SpendingAdviceResponse;
}

beforeEach(() => {
  vi.clearAllMocks();
  adviceMock.mockReturnValue(query({ data: payload() }));
});

/**
 * 🔴 Последний пункт §8.2 «ГЛАВНОЕ»: `GET /planning/spending-advice` живёт с мат-модели
 * v3.0.0 и не имеет фронта вовсе. Аудит `independent-expert` 05.09.2026 поймал вахту
 * на утверждении «§8.2 закрыт целиком» — чекбокс всё это время стоял пустым.
 *
 * Экран отвечает на один вопрос: **где я трачу больше своей нормы и сколько можно
 * вернуть.** Норма — медиана прошлых месяцев, а не среднее: один отпуск не должен
 * переписывать норму «Транспорта».
 */
describe("SpendingPage — вывод стоит первым", () => {
  it("показывает суммарную потенциальную экономию словами и числом", () => {
    adviceMock.mockReturnValue(
      query({
        data: payload({
          total_potential_saving: 7300,
          advice: [
            {
              category: "Кафе и рестораны",
              potential_saving: 5000,
              reason: "overspend",
              current: 20000,
              baseline: 15000,
              message: "В кафе ушло на 5 000 ₽ больше обычного",
            },
            {
              category: "Развлечения",
              potential_saving: 2300,
              reason: "discretionary",
              current: 9000,
              baseline: 9000,
              message: "Можно умеренно сократить",
            },
          ],
        }),
      }),
    );
    render(<SpendingPage />);

    // Сумма — первый ответ экрана: человек пришёл узнать «сколько», а не «в каких строках».
    expect(screen.getByTestId("fp-spending-total")).toHaveTextContent(/7\s?300/);
  });

  it("каждый совет называет категорию, норму и текущий расход", () => {
    adviceMock.mockReturnValue(
      query({
        data: payload({
          total_potential_saving: 5000,
          advice: [
            {
              category: "Кафе и рестораны",
              potential_saving: 5000,
              reason: "overspend",
              current: 20000,
              baseline: 15000,
              message: "В кафе ушло больше обычного",
            },
          ],
        }),
      }),
    );
    render(<SpendingPage />);

    const item = screen.getByTestId("fp-advice-Кафе и рестораны");
    // 🔴 Норма обязана стоять рядом с текущим: «потратил 20 000» без «обычно 15 000»
    // не даёт человеку повода что-то менять — это просто выписка.
    expect(item).toHaveTextContent(/20\s?000/);
    expect(item).toHaveTextContent(/15\s?000/);
  });

  it("аномалия помечена, а не спрятана в числах", () => {
    adviceMock.mockReturnValue(
      query({
        data: payload({
          stats: [
            {
              category: "Покупки",
              baseline: 10000,
              mad: 1200,
              current: 40000,
              z_score: 5.1,
              freq_month: 12,
              avg_check: 3333,
              share: 0.4,
              compressibility: 0.6,
              pain_score: 0.5,
              is_anomaly: true,
              months_observed: 6,
            },
          ],
        }),
      }),
    );
    render(<SpendingPage />);

    const row = screen.getByTestId("fp-stats-Покупки");
    expect(row).toHaveTextContent(/необычно|аномал|резко/i);
  });
});

describe("SpendingPage — мало данных объясняется словами", () => {
  /* 🔴 Модель требует минимум трёх завершённых месяцев (`MIN_MONTHS`). У нового
     пользователя их нет, и без объяснения экран выглядит сломанным: пустые списки
     и ноль экономии читаются как «продукт не работает», а не «данных пока мало». */
  it("объясняет, почему советов ещё нет", () => {
    adviceMock.mockReturnValue(query({ data: payload({ months_with_data: 1 }) }));
    render(<SpendingPage />);

    expect(screen.getByRole("status")).toHaveTextContent(/месяц/i);
  });

  it("не показывает нулевую экономию как достижение", () => {
    adviceMock.mockReturnValue(query({ data: payload({ months_with_data: 1 }) }));
    render(<SpendingPage />);

    expect(screen.queryByTestId("fp-spending-total")).not.toBeInTheDocument();
  });

  it("данных достаточно, но перерасхода нет — это хорошая новость, а не пустота", () => {
    adviceMock.mockReturnValue(query({ data: payload({ months_with_data: 6 }) }));
    render(<SpendingPage />);

    expect(screen.getByRole("status")).toHaveTextContent(/в пределах|норм/i);
  });
});

describe("SpendingPage — тренды и цели", () => {
  it("растущая категория названа направлением, а не знаком числа", () => {
    adviceMock.mockReturnValue(
      query({
        data: payload({
          temporal_patterns: [
            {
              category: "Подписки и сервисы",
              direction: "rising",
              slope_abs: 400,
              slope_pct: 8.5,
              baseline: 4700,
              months_observed: 6,
              message: "Подписки растут",
            },
          ],
        }),
      }),
    );
    render(<SpendingPage />);

    const trend = screen.getByTestId("fp-trend-Подписки и сервисы");
    // «+8.5 %» без слова «растёт» человек читает как долю, а не как направление.
    expect(trend).toHaveTextContent(/раст/i);
  });

  it("влияние на цель показано в месяцах, а не только в рублях", () => {
    adviceMock.mockReturnValue(
      query({
        data: payload({
          total_potential_saving: 5000,
          goal_impact: [
            {
              goal_name: "Подушка",
              remaining: 120000,
              months_to_deadline: 12,
              current_monthly: 10000,
              redirected_saving: 5000,
              eta_now: 12,
              eta_boosted: 8,
              months_earlier: 4,
              on_track: true,
              message: "Цель будет достигнута раньше",
            },
          ],
        }),
      }),
    );
    render(<SpendingPage />);

    const impact = screen.getByTestId("fp-goal-impact-Подушка");
    // Ради этого экран и нужен: экономия сама по себе абстрактна, «на 4 месяца раньше» — нет.
    expect(impact).toHaveTextContent(/4/);
    expect(impact).toHaveTextContent(/месяц/i);
  });

  it("цель без дедлайна не превращается в «0 месяцев»", () => {
    /* 🔴 `months_to_deadline`, `eta_now` и `months_earlier` необязательны и означают
       разное: бессрочную цель, отсутствие пополнений и невозможность посчитать выигрыш.
       Показать вместо любого из них ноль — сказать человеку неправду о его цели. */
    adviceMock.mockReturnValue(
      query({
        data: payload({
          total_potential_saving: 5000,
          goal_impact: [
            {
              goal_name: "Машина",
              remaining: 500000,
              months_to_deadline: null,
              current_monthly: 0,
              redirected_saving: 5000,
              eta_now: null,
              eta_boosted: 100,
              months_earlier: null,
              on_track: false,
              message: "Цель пока не пополняется",
            },
          ],
        }),
      }),
    );
    render(<SpendingPage />);

    const impact = screen.getByTestId("fp-goal-impact-Машина");
    expect(impact).not.toHaveTextContent(/0 месяц/);
    expect(impact).toHaveTextContent(/не пополня|без срока|срок не задан/i);
  });

  it("цель СО СРОКОМ не объявляется бессрочной, когда выигрыш округлился до нуля", () => {
    /* 🔴 Нашёл `/code-review ultra` в правке предыдущего часа. Фильтр
       `Math.round(earlier) >= 1` завели, чтобы не писать «на 0 месяцев раньше», —
       и он открыл ветку, недостижимую до него.

       По бэкенду (`spending_advice.py`) `months_earlier != null ⟹ eta_now != null`,
       значит `notFunded` здесь ложь; при `0 < earlier < 0.5` первая ветка отсекается,
       вторая не срабатывает, и код падает в «срок не задан» — при выставленном дедлайне.

       Правка, задуманная убрать одну неправду, начала говорить другую: продукт
       сообщает человеку про его собственную цель то, что тот сам опровергнет
       за две секунды. `months_to_deadline` — отдельное поле схемы, и отвечает
       за наличие срока именно оно. */
    adviceMock.mockReturnValue(
      query({
        data: payload({
          total_potential_saving: 500,
          goal_impact: [
            {
              goal_name: "Отпуск",
              remaining: 80000,
              months_to_deadline: 8.5,
              current_monthly: 9000,
              redirected_saving: 500,
              eta_now: 8.7,
              eta_boosted: 8.4,
              months_earlier: 0.3,
              on_track: true,
              message: "Цель будет достигнута чуть раньше",
            },
          ],
        }),
      }),
    );
    render(<SpendingPage />);

    const impact = screen.getByTestId("fp-goal-impact-Отпуск");
    expect(impact).not.toHaveTextContent(/срок не задан/i);
    expect(impact).not.toHaveTextContent(/0 месяц/);
    // Строка не исчезает целиком: сумма перенаправленной экономии остаётся полезной.
    expect(impact).toHaveTextContent(/500/);
  });

  it("бессрочная цель С пополнениями всё-таки называется бессрочной", () => {
    /* Обратная проверка: сузив ветку, легко потерять её законный случай.
       Здесь дедлайна нет (`months_to_deadline: null`), цель пополняется —
       и «срок не задан» это ровно то, что надо сказать. */
    adviceMock.mockReturnValue(
      query({
        data: payload({
          total_potential_saving: 500,
          goal_impact: [
            {
              goal_name: "Резерв",
              remaining: 60000,
              months_to_deadline: null,
              current_monthly: 5000,
              redirected_saving: 500,
              eta_now: 12,
              eta_boosted: 11.8,
              months_earlier: 0.2,
              on_track: true,
              message: "Бессрочная цель",
            },
          ],
        }),
      }),
    );
    render(<SpendingPage />);

    expect(screen.getByTestId("fp-goal-impact-Резерв")).toHaveTextContent(/срок не задан/i);
  });
});

describe("SpendingPage — ошибка ведёт куда-то, а не в тупик", () => {
  it("ошибка предлагает повторить, а не чинить приложение самому", async () => {
    /* 🔴 [ST-04]: системная ошибка ОБЯЗАНА предлагать действие восстановления.
       Текст «попробуйте позже» действием не является — он перекладывает работу
       на человека (design-critic). */
    const refetch = vi.fn().mockResolvedValue({});
    adviceMock.mockReturnValue(query({ isError: true, error: { detail: "Сбой" }, refetch }));
    render(<SpendingPage />);

    await userEvent.click(screen.getByRole("button", { name: /повторить/i }));
    expect(refetch).toHaveBeenCalled();
  });

  it("отозванное согласие показано как согласие, а не как поломка", () => {
    /* Хук намеренно не ретраит 403: это осознанное «нет» сервера при отозванном
       согласии на финданные. Показывать его тем же «недоступно», что сетевой сбой,
       значит прятать от человека причину, которую продукт знает, — тупик [IA-04]. */
    adviceMock.mockReturnValue(
      query({
        isError: true,
        error: {
          detail: {
            code: "consent_required",
            consent_type: "financial_data",
            message: "Нужно согласие на обработку финансовых данных",
            document: { title: "Согласие", version: "1.0", url: "/legal/consent" },
          },
        },
      }),
    );
    render(<SpendingPage />);

    expect(screen.getByRole("button", { name: /дать согласие|согласи/i })).toBeInTheDocument();
  });
});

describe("SpendingPage — одни ворота на все блоки", () => {
  it("при нехватке данных не показывает советы под сообщением о нехватке данных", () => {
    /* 🔴 Иначе экран одновременно говорит «советы появятся, когда наберётся история»
       и показывает их список — сообщает человеку неправду о нём самом. */
    adviceMock.mockReturnValue(
      query({
        data: payload({
          months_with_data: 1,
          advice: [
            {
              category: "Кафе и рестораны",
              potential_saving: 5000,
              reason: "overspend",
              current: 20000,
              baseline: 15000,
              message: "Больше обычного",
            },
          ],
          stats: [
            {
              category: "Кафе и рестораны",
              baseline: 15000,
              mad: 900,
              current: 20000,
              z_score: 4,
              freq_month: 10,
              avg_check: 2000,
              share: 0.2,
              compressibility: 1,
              pain_score: 0.3,
              is_anomaly: true,
              months_observed: 1,
            },
          ],
        }),
      }),
    );
    render(<SpendingPage />);

    expect(screen.queryByTestId("fp-advice-Кафе и рестораны")).not.toBeInTheDocument();
    expect(screen.queryByTestId("fp-stats-Кафе и рестораны")).not.toBeInTheDocument();
  });
});

describe("SpendingPage — склонение и объявление результата", () => {
  it("не печатает «на 1 месяца раньше»", () => {
    adviceMock.mockReturnValue(
      query({
        data: payload({
          goal_impact: [
            {
              goal_name: "Подушка",
              remaining: 10000,
              months_to_deadline: 2,
              current_monthly: 5000,
              redirected_saving: 5000,
              eta_now: 2,
              eta_boosted: 1,
              months_earlier: 1,
              on_track: true,
              message: "",
            },
          ],
        }),
      }),
    );
    render(<SpendingPage />);

    const impact = screen.getByTestId("fp-goal-impact-Подушка");
    expect(impact).toHaveTextContent(/1 месяц раньше/);
    expect(impact).not.toHaveTextContent(/1 месяца/);
  });

  it("готовый разбор объявляется программе чтения экрана (WCAG 4.1.3)", () => {
    /* Ветки «мало данных» и «в пределах нормы» объявляет `StatePanel`. Главный
       случай экрана не объявлялся ничем: человек, оставшийся на заголовке во время
       скелетона, не узнавал, что расчёт кончился (a11y-auditor). */
    adviceMock.mockReturnValue(
      query({
        data: payload({
          total_potential_saving: 7300,
          advice: [
            {
              category: "Кафе и рестораны",
              potential_saving: 7300,
              reason: "overspend",
              current: 20000,
              baseline: 15000,
              message: "Больше обычного",
            },
          ],
        }),
      }),
    );
    render(<SpendingPage />);

    expect(screen.getByRole("status")).toHaveTextContent(/7\s?300/);
  });
});

describe("SpendingPage — состояния запроса", () => {
  it("загрузка показывает скелетон, а не пустой экран", () => {
    adviceMock.mockReturnValue(query({ isLoading: true }));
    render(<SpendingPage />);
    expect(screen.getByTestId("fp-spending-loading")).toBeInTheDocument();
  });

  it("ошибка объясняется и предлагает повтор", () => {
    adviceMock.mockReturnValue(
      query({ isError: true, error: { detail: "Требуется согласие на обработку" } }),
    );
    render(<SpendingPage />);

    const panel = screen.getByRole("alert");
    expect(panel).toHaveTextContent(/соглас/i);
  });

  it("окно анализа подписано числом из ответа, а не хардкодом", () => {
    adviceMock.mockReturnValue(query({ data: payload({ months_window: 3 }) }));
    render(<SpendingPage />);

    const header = screen.getByTestId("fp-spending-window");
    expect(within(header).getByText(/3/)).toBeInTheDocument();
  });
});

describe("SpendingPage — направление тренда и неполные данные", () => {
  it("🔴 падающая категория подписана «снижается», а не только стрелкой", () => {
    /* Направление, показанное лишь цветом или стрелкой, недоступно скринридеру
       и дальтонику ([A11Y-07]). «−8.5 %» без слова человек читает как долю,
       а не как изменение. */
    adviceMock.mockReturnValue(
      query({
        data: payload({
          temporal_patterns: [
            {
              category: "Кафе",
              direction: "falling" as const,
              slope_abs: -1200,
              slope_pct: -8.5,
              baseline: 14000,
              months_observed: 6,
              message: "Траты на кафе снижаются",
            },
          ],
        }),
      }),
    );
    render(<SpendingPage />);

    expect(screen.getByText(/снижается/)).toBeInTheDocument();
  });

  it("ответ без советов и трендов не роняет экран", () => {
    /* Оба массива необязательны: у человека с ровными тратами советов может
       не быть вовсе, и это нормальный результат анализа, а не сбой. */
    adviceMock.mockReturnValue(
      query({ data: payload({ advice: undefined, temporal_patterns: undefined }) }),
    );
    expect(() => render(<SpendingPage />)).not.toThrow();
  });
});
