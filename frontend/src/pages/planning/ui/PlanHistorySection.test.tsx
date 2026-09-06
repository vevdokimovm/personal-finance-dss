import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { PlanHistorySection } from "./PlanHistorySection";

const usePlanHistoryMock = vi.fn();
const saveMock = vi.fn();
const deleteMock = vi.fn();
const restoreMock = vi.fn();

// `vi.mock` поднимается выше объявлений, поэтому мок создаётся через `vi.hoisted`:
// обычная `const` даёт ReferenceError до инициализации.
const { undoMock, toastSuccess, toastError } = vi.hoisted(() => ({
  undoMock: vi.fn(),
  toastSuccess: vi.fn(),
  toastError: vi.fn(),
}));
// ToastProvider в юнит-тесте не смонтирован, поэтому кнопки «Вернуть» в DOM нет.
// Проверяем контракт вызова: удаление ОБЯЗАНО предложить отмену и отдать в неё
// восстановление именно этого снимка.
vi.mock("@shared/ui", async () => {
  const actual = await vi.importActual<typeof import("@shared/ui")>("@shared/ui");
  return {
    ...actual,
    toast: { ...actual.toast, undo: undoMock, success: toastSuccess, error: toastError },
  };
});

vi.mock("@entities/plan-history", () => ({
  usePlanHistory: () => usePlanHistoryMock(),
  useSavePlanSnapshot: () => ({ mutate: saveMock, isPending: false }),
  useDeletePlanSnapshot: () => ({ mutate: deleteMock, isPending: false }),
  useRestorePlanSnapshot: () => ({ mutate: restoreMock, isPending: false }),
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
  restoreMock.mockClear();
  undoMock.mockClear();
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

  /* 🔴 Модалка подтверждения снята в v8.56.0. Она стояла с обоснованием
     «restore-эндпоинта для снимков нет, вернуть удалённое нечем» — и это обоснование
     отпало в v8.38.0, когда появились `POST /planning/history/{id}/restore`
     и `useRestorePlanSnapshot`. Комментарий, текст модалки и `description` остались
     от прежнего состояния кода на восемнадцать версий.

     У остальных ПЯТИ сущностей (цели, активы, обязательства, операции, бюджеты)
     удаление идёт сразу и предлагает «Вернуть». Модалка на шестой — расхождение,
     а не осознанная защита: она не защищает ни от чего, чего не защищает undo. */
  it("удаляет сразу, без подтверждения — как остальные пять сущностей", async () => {
    deleteMock.mockImplementation((_id, opts) => opts?.onSuccess?.());
    usePlanHistoryMock.mockReturnValue({
      data: { items: [snapshot()], count: 1 },
      error: null,
      isLoading: false,
      refetch: vi.fn(),
    });
    render(<PlanHistorySection />);
    await userEvent.click(screen.getAllByRole("button", { name: /Удалить снимок/ })[0]);

    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
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

  it("нигде не обещает, что восстановить снимок нельзя", () => {
    /* 🔴 Продукт не должен пугать необратимостью там, где действие обратимо: человек
       читает «восстановить будет нельзя», отказывается от удаления и копит снимки,
       которых не хотел. Неверная надпись меняет его решение — это дороже лишнего клика,
       ради которого модалка и стояла. */
    usePlanHistoryMock.mockReturnValue({
      data: { items: [snapshot()], count: 1 },
      error: null,
      isLoading: false,
      refetch: vi.fn(),
    });
    render(<PlanHistorySection />);
    expect(
      screen.queryByText(/необратим|восстановить.*нельзя|нельзя.*восстановить/i),
    ).not.toBeInTheDocument();
  });
  /* Удаление снимка обратимо с v8.38.0. До этого продукт говорил на двух языках:
     у целей, активов, обязательств, операций и бюджетов «Вернуть» было, у истории
     планов — нет, хотя данные в базе оставались. */
  it("удаление предлагает «Вернуть», и отмена восстанавливает снимок", async () => {
    deleteMock.mockImplementation((_id, opts) => opts?.onSuccess?.());
    usePlanHistoryMock.mockReturnValue({
      data: { items: [snapshot()], count: 1 },
      error: null,
      isLoading: false,
      refetch: vi.fn(),
    });
    render(<PlanHistorySection />);
    await userEvent.click(screen.getAllByRole("button", { name: /Удалить снимок/ })[0]);

    expect(undoMock).toHaveBeenCalledWith("Снимок удалён", expect.any(Function));
    undoMock.mock.calls[0][1]();
    expect(restoreMock.mock.calls[0][0]).toBe(7);
  });
});

/**
 * Ветки отказа — непокрытый остаток секции на момент v9.2.0.
 *
 * 🔴 **Снимок плана человек делает перед решением о деньгах**: «сохраню, как есть,
 * а потом сравню». Молчание после клика читается как «сохранено», и он уйдёт со
 * страницы, потеряв состояние, ради которого и нажимал.
 */
describe("PlanHistorySection — что видно, когда действие не удалось", () => {
  it("отказ при сохранении снимка сообщается", async () => {
    usePlanHistoryMock.mockReturnValue({
      data: { items: [] },
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    });
    saveMock.mockImplementation((_body: unknown, opts?: { onError?: () => void }) =>
      opts?.onError?.(),
    );
    render(<PlanHistorySection />);

    await userEvent.click(screen.getByRole("button", { name: /Сохранить снимок|Сохранить/ }));

    expect(toastError).toHaveBeenCalled();
    expect(toastSuccess).not.toHaveBeenCalled();
  });

  it("успех при сохранении очищает заметку — она относилась к прошлому снимку", async () => {
    /* Заметка, оставшаяся в поле, уедет во второй снимок и опишет не то состояние. */
    usePlanHistoryMock.mockReturnValue({
      data: { items: [] },
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    });
    saveMock.mockImplementation((_body: unknown, opts?: { onSuccess?: () => void }) =>
      opts?.onSuccess?.(),
    );
    render(<PlanHistorySection />);

    const note = screen.getByLabelText(/Подпись к снимку/i);
    await userEvent.type(note, "До отпуска");
    await userEvent.click(screen.getByRole("button", { name: /Сохранить снимок|Сохранить/ }));

    expect(toastSuccess).toHaveBeenCalled();
    expect(note).toHaveValue("");
  });

  it("🔴 отказ при восстановлении сообщается — «Вернуть» не всегда срабатывает", async () => {
    /* Кнопка отмены создаёт впечатление обратимости. Если восстановление упало,
       а мы промолчали, человек уверен, что снимок вернулся, — и не сделает новый. */
    usePlanHistoryMock.mockReturnValue({
      data: { items: [snapshot()] },
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    });
    deleteMock.mockImplementation((_id: number, opts?: { onSuccess?: () => void }) =>
      opts?.onSuccess?.(),
    );
    restoreMock.mockImplementation((_id: number, opts?: { onError?: () => void }) =>
      opts?.onError?.(),
    );
    render(<PlanHistorySection />);

    await userEvent.click(screen.getAllByRole("button", { name: /Удалить снимок/ })[0]);
    undoMock.mock.calls[0][1]();

    expect(toastError).toHaveBeenCalled();
  });
});
