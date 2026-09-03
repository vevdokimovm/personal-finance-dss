import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { PlanHistorySection } from "./PlanHistorySection";

const usePlanHistoryMock = vi.fn();
const saveMock = vi.fn();
const deleteMock = vi.fn();

vi.mock("@entities/plan-history", () => ({
  usePlanHistory: () => usePlanHistoryMock(),
  useSavePlanSnapshot: () => ({ mutate: saveMock, isPending: false }),
  useDeletePlanSnapshot: () => ({ mutate: deleteMock, isPending: false }),
}));

vi.mock("@entities/consents", () => ({
  ConsentRequiredPanel: ({ detail }: { detail: { message: string } }) => (
    <div role="alert">{detail.message}</div>
  ),
}));

const snapshot = (over: Record<string, unknown> = {}) => ({
  id: 7,
  created_at: "2026-09-01T10:00:00",
  risk_profile: "Сбалансированный",
  indicators: { Rt: 39500, Lt: 3.4, Dt: 0.3472, BLR: 3.4 },
  best: {
    name: "Всё в резерв",
    x_obligations: 0,
    x_reserve: 39500,
    x_goals: 0,
    utility: 0.8,
  },
  note: "до отпуска",
  ...over,
});

beforeEach(() => {
  usePlanHistoryMock.mockReturnValue({
    data: { items: [], count: 0 },
    error: null,
    isLoading: false,
    refetch: vi.fn(),
  });
  saveMock.mockClear();
  deleteMock.mockClear();
});

describe("PlanHistorySection — история сохранённых планов", () => {
  it("у секции есть собственный заголовок (контур документа)", () => {
    render(<PlanHistorySection />);
    expect(screen.getByRole("heading", { name: "История планов" })).toBeInTheDocument();
  });

  it("загрузка показывает скелетон, а не пустоту (ST-02)", () => {
    usePlanHistoryMock.mockReturnValue({
      data: undefined,
      error: null,
      isLoading: true,
      refetch: vi.fn(),
    });
    const { container } = render(<PlanHistorySection />);
    expect(container.querySelector(".fp-skeleton, [class*='skeleton']")).not.toBeNull();
  });

  it("пусто — объясняет, что это и что сделать (ST-03)", () => {
    render(<PlanHistorySection />);
    expect(screen.getByText("Пока нет сохранённых планов")).toBeVisible();
    expect(screen.getByRole("button", { name: "Сохранить текущий план" })).toBeVisible();
  });

  it("ошибка даёт путь восстановления, а не только сообщение (ST-04)", () => {
    usePlanHistoryMock.mockReturnValue({
      data: undefined,
      error: new Error("500"),
      isLoading: false,
      refetch: vi.fn(),
    });
    render(<PlanHistorySection />);
    expect(screen.getByText("Не получилось загрузить историю планов")).toBeVisible();
    expect(screen.getByRole("button", { name: "Повторить" })).toBeVisible();
  });

  it("403 показывает панель согласия, а не общую ошибку", () => {
    usePlanHistoryMock.mockReturnValue({
      data: undefined,
      error: {
        detail: {
          code: "consent_required",
          consent_type: "financial_data",
          message: "Нужно согласие на обработку финансовых данных.",
          document: { title: "Согласие", url: "/legal/x" },
        },
      },
      isLoading: false,
      refetch: vi.fn(),
    });
    render(<PlanHistorySection />);
    expect(screen.getByRole("alert")).toHaveTextContent(/Нужно согласие/);
  });

  it("снимок показывает дату, профиль риска, свободные деньги и подпись", () => {
    usePlanHistoryMock.mockReturnValue({
      data: { items: [snapshot()], count: 1 },
      error: null,
      isLoading: false,
      refetch: vi.fn(),
    });
    const { container } = render(<PlanHistorySection />);
        // Время зависит от часового пояса машины (бэкенд отдаёт наивный UTC, показываем
    // локальное), поэтому сверяем дату и наличие времени, а не точную строку.
    expect(screen.getByText(/^01\.09\.2026, \d{2}:\d{2}$/)).toBeVisible();
    expect(screen.getByText("Сбалансированный")).toBeVisible();
    // Неразрывный пробел, а не обычный: `formatMoney` ставит именно его, и обычный
    // здесь означал бы, что деньги отформатированы мимо канона.
    // `toHaveTextContent` нормализует пробелы с ОБЕИХ сторон — в отличие от
    // `getByText`, который нормализует только DOM и потому промахивается мимо
    // неразрывного пробела, который ставит `formatMoney`.
    expect(container.querySelector(".fp-plan-history__money")).toHaveTextContent("39 500,00 ₽");
    expect(screen.getByText("до отпуска")).toBeVisible();
  });

  it("снимок без подписи не рисует пустую строку", () => {
    usePlanHistoryMock.mockReturnValue({
      data: { items: [snapshot({ note: null })], count: 1 },
      error: null,
      isLoading: false,
      refetch: vi.fn(),
    });
    const { container } = render(<PlanHistorySection />);
    expect(container.querySelector(".fp-plan-history__note")).toBeNull();
  });

  it("сохранение передаёт подпись, введённую пользователем", async () => {
    render(<PlanHistorySection />);
    await userEvent.type(screen.getByLabelText("Подпись к снимку"), "до отпуска");
    await userEvent.click(screen.getByRole("button", { name: "Сохранить текущий план" }));
    expect(saveMock.mock.calls[0][0]).toEqual({ note: "до отпуска" });
  });

  it("пустая подпись уходит как отсутствующая, а не пустой строкой", () => {
    // `note` в контракте необязателен; пустая строка — это не «без подписи»,
    // и в истории она выглядела бы как пустая строка вместо её отсутствия.
    render(<PlanHistorySection />);
    screen.getByRole("button", { name: "Сохранить текущий план" }).click();
    expect(saveMock.mock.calls[0][0]).toEqual({ note: null });
  });

  it("удаление спрашивает подтверждение, а не стирает по первому клику", async () => {
    usePlanHistoryMock.mockReturnValue({
      data: { items: [snapshot()], count: 1 },
      error: null,
      isLoading: false,
      refetch: vi.fn(),
    });
    render(<PlanHistorySection />);
    await userEvent.click(screen.getAllByRole("button", { name: /Удалить снимок/ })[0]);
    expect(deleteMock).not.toHaveBeenCalled();
    // В модалке кнопка называется датой снимка: при обходе документа списком кнопок
    // «Удалить» без уточнения неотличима от кнопок в списке ([A11Y-05]).
    const confirm = screen
      .getAllByRole("button", { name: /Удалить снимок от 01\.09\.2026/ })
      .at(-1)!;
    await userEvent.click(confirm);
    expect(deleteMock.mock.calls[0][0]).toBe(7);
  });
});

describe("PlanHistorySection — длинная история и ПДН", () => {
  const many = Array.from({ length: 7 }, (_, i) =>
    snapshot({ id: i + 1, created_at: `2026-09-0${i + 1}T10:00:00` }),
  );

  it("показывает первые пять снимков, остальные — по кнопке (IA-06)", async () => {
    usePlanHistoryMock.mockReturnValue({
      data: { items: many, count: many.length },
      error: null,
      isLoading: false,
      refetch: vi.fn(),
    });
    render(<PlanHistorySection />);
    expect(screen.getAllByRole("listitem")).toHaveLength(5);

    await userEvent.click(screen.getByRole("button", { name: "Показать все (7)" }));
    expect(screen.getAllByRole("listitem")).toHaveLength(7);
  });

  it("короткий список не предлагает разворачивание", () => {
    usePlanHistoryMock.mockReturnValue({
      data: { items: [snapshot()], count: 1 },
      error: null,
      isLoading: false,
      refetch: vi.fn(),
    });
    render(<PlanHistorySection />);
    expect(screen.queryByRole("button", { name: /Показать все/ })).not.toBeInTheDocument();
  });

  it("превышенный порог ПДН помечен СЛОВОМ, а не только цветом (A11Y-07)", () => {
    usePlanHistoryMock.mockReturnValue({
      data: {
        items: [snapshot({ indicators: { Rt: 39500, Lt: 3.4, Dt: 0.48, BLR: 3.4 } })],
        count: 1,
      },
      error: null,
      isLoading: false,
      refetch: vi.fn(),
    });
    render(<PlanHistorySection />);
    expect(screen.getByText("выше порога")).toBeVisible();
  });

  it("нагрузка в пределах порога словом не помечается", () => {
    usePlanHistoryMock.mockReturnValue({
      data: { items: [snapshot()], count: 1 },
      error: null,
      isLoading: false,
      refetch: vi.fn(),
    });
    render(<PlanHistorySection />);
    expect(screen.queryByText("выше порога")).not.toBeInTheDocument();
  });

  it("подтверждение показывает, КАКОЙ снимок удаляют, видимым текстом (FRM-07)", async () => {
    usePlanHistoryMock.mockReturnValue({
      data: { items: [snapshot()], count: 1 },
      error: null,
      isLoading: false,
      refetch: vi.fn(),
    });
    const { container } = render(<PlanHistorySection />);
    await userEvent.click(screen.getAllByRole("button", { name: /Удалить снимок/ })[0]);
    const target = container.ownerDocument.querySelector(".fp-plan-history__confirm-target");
    expect(target).not.toBeNull();
    expect(target).toHaveTextContent(/01\.09\.2026, \d{2}:\d{2}/);
  });
});
