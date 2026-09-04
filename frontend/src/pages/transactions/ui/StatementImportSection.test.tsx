import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { StatementImportSection } from "./StatementImportSection";

const { useBanksMock, uploadMock, toastError } = vi.hoisted(() => ({
  useBanksMock: vi.fn(),
  uploadMock: vi.fn(),
  toastError: vi.fn(),
}));

vi.mock("@entities/bank-import", () => ({
  useBanks: () => useBanksMock(),
  useUploadStatement: () => ({ mutate: uploadMock, isPending: false }),
}));

vi.mock("@shared/ui", async () => {
  const actual = await vi.importActual<typeof import("@shared/ui")>("@shared/ui");
  return { ...actual, toast: { ...actual.toast, error: toastError } };
});

const BANKS = [
  { id: "tinkoff", name: "Тинькофф" },
  { id: "sber", name: "Сбербанк" },
];

function file(name = "statement.csv") {
  return new File(["date,amount\n"], name, { type: "text/csv" });
}

beforeEach(() => {
  vi.clearAllMocks();
  useBanksMock.mockReturnValue({ data: BANKS, error: null, isLoading: false });
});

describe("StatementImportSection — импорт выписки", () => {
  it("предлагает банки из списка сервера, а не зашитые в код", () => {
    render(<StatementImportSection />);
    expect(screen.getByRole("option", { name: "Тинькофф" })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "Сбербанк" })).toBeInTheDocument();
  });

  it("отправляет файл и выбранный банк", async () => {
    render(<StatementImportSection />);
    await userEvent.selectOptions(screen.getByLabelText("Банк"), "sber");
    await userEvent.upload(screen.getByLabelText("Файл выписки"), file());
    await userEvent.click(screen.getByRole("button", { name: "Импортировать" }));
    expect(uploadMock.mock.calls[0][0]).toMatchObject({ bankId: "sber" });
    expect(uploadMock.mock.calls[0][0].file.name).toBe("statement.csv");
  });

  /* Немой клик читается как «экран сломался» ([FB-01]). */
  it("без файла не отправляет и объясняет, чего не хватает", async () => {
    render(<StatementImportSection />);
    await userEvent.click(screen.getByRole("button", { name: "Импортировать" }));
    expect(uploadMock).not.toHaveBeenCalled();
    expect(toastError).toHaveBeenCalled();
  });

  /* 🔴 Ошибка разбора приходит со статусом 200 и `status: "error"`. Считать любой 200
     успехом значило бы показать «импортировано» на нераспознанном файле. */
  it("нераспознанный файл показан как ОТКАЗ, а не как успех", async () => {
    uploadMock.mockImplementation((_args, opts) =>
      opts?.onSuccess?.({
        status: "error",
        message: "Не удалось распознать транзакции.",
      }),
    );
    render(<StatementImportSection />);
    await userEvent.upload(screen.getByLabelText("Файл выписки"), file("bad.csv"));
    await userEvent.click(screen.getByRole("button", { name: "Импортировать" }));

    expect(screen.getByText("Импорт не прошёл")).toBeVisible();
    expect(screen.queryByText("Готово")).not.toBeInTheDocument();
    expect(screen.getByText(/Не удалось распознать/)).toBeVisible();
  });

  it("успешный импорт показывает итоги суммами, а не числом строк", async () => {
    uploadMock.mockImplementation((_args, opts) =>
      opts?.onSuccess?.({
        status: "success",
        message: "Импортировано 42 операции",
        added_count: 42,
        skipped_duplicates: 3,
        total_income: 180000,
        total_expense: 78000,
      }),
    );
    render(<StatementImportSection />);
    await userEvent.upload(screen.getByLabelText("Файл выписки"), file());
    await userEvent.click(screen.getByRole("button", { name: "Импортировать" }));

    expect(screen.getByText("Готово")).toBeVisible();
    expect(screen.getByText(/Импортировано 42 операции/)).toBeVisible();
    // Деньги — по канону: НЕРАЗРЫВНЫЙ пробел как разделитель тысяч, ₽ после числа,
    // копейки скрыты выше 100 000 (`formatMoney`). Сверяем `textContent` напрямую:
    // `toHaveTextContent` нормализует пробелы и NBSP от обычного не отличит — а тут
    // проверяется именно он.
    const totals = screen.getByText(/Доходы:/).textContent ?? "";
    expect(totals).toContain("180\u00a0000,00\u00a0₽");
    expect(totals).toContain("78\u00a0000,00\u00a0₽");
  });

  /* Расхождение итогов — предупреждение, а не отказ: операции УЖЕ импортированы,
     блокировать человека из-за нашей же ошибки чтения итогов хуже, чем предупредить. */
  it("расхождение итогов предупреждает, но не выдаётся за отказ", async () => {
    uploadMock.mockImplementation((_args, opts) =>
      opts?.onSuccess?.({
        status: "success",
        message: "Импортировано 10 операций",
        added_count: 10,
        total_income: 1000,
        total_expense: 500,
        reconciliation: {
          status: "mismatch",
          message: "расход: распознано 78 000,00 ₽, банк заявляет 81 240,00 ₽",
        },
      }),
    );
    render(<StatementImportSection />);
    await userEvent.upload(screen.getByLabelText("Файл выписки"), file());
    await userEvent.click(screen.getByRole("button", { name: "Импортировать" }));

    expect(screen.getByText("Готово")).toBeVisible();
    // 🔴 Показываем ЧИСЛО расхождения от сервера, а не родовое «проверьте операции»:
    // без числа совет не на что опереть (design-critic).
    expect(screen.getByText(/банк заявляет 81 240,00/)).toBeVisible();
  });

  it("сошедшиеся итоги лишним предупреждением не пугают", async () => {
    uploadMock.mockImplementation((_args, opts) =>
      opts?.onSuccess?.({
        status: "success",
        message: "Импортировано 10 операций",
        added_count: 10,
        total_income: 1000,
        total_expense: 500,
        reconciliation: { status: "ok" },
      }),
    );
    render(<StatementImportSection />);
    await userEvent.upload(screen.getByLabelText("Файл выписки"), file());
    await userEvent.click(screen.getByRole("button", { name: "Импортировать" }));
    expect(screen.queryByText(/не сошлись/)).not.toBeInTheDocument();
  });

  /* Ответ и отказ — в ОДНОМ месте. Первая редакция клала разбор инлайном, а сеть тостом
     в углу: одна операция, два разных места ответа ([ST-06], design-critic). */
  it("сеть отказала — ответ там же, где был бы успех", async () => {
    uploadMock.mockImplementation((_args, opts) => opts?.onError?.(new Error("network")));
    render(<StatementImportSection />);
    await userEvent.upload(screen.getByLabelText("Файл выписки"), file());
    await userEvent.click(screen.getByRole("button", { name: "Импортировать" }));
    expect(screen.getByText("Импорт не прошёл")).toBeVisible();
    expect(screen.getByText(/Проверьте соединение/)).toBeVisible();
  });

  it("подсказка объясняет, что для PDF банк определяется по файлу", () => {
    render(<StatementImportSection />);
    expect(screen.getByText(/банк определяется по самому файлу/)).toBeVisible();
  });
  /* 🔴 У сверки ТРИ исхода. `unavailable` — «сверять было нечем» (CSV без контрольных
     итогов, PDF банка без профиля сверки), это ПОЛНОСТЬЮ успешный импорт. Первая
     редакция считала расхождением всё, что не `ok`, и гнала человека вручную
     перепроверять сотню строк на исправном файле (design-critic). */
  it("«сверять было нечем» — не расхождение и не повод пугать", async () => {
    uploadMock.mockImplementation((_args, opts) =>
      opts?.onSuccess?.({
        status: "success",
        message: "Импортировано 10 операций",
        added_count: 10,
        total_income: 1000,
        total_expense: 500,
        reconciliation: { status: "unavailable", message: "" },
      }),
    );
    render(<StatementImportSection />);
    await userEvent.upload(screen.getByLabelText("Файл выписки"), file());
    await userEvent.click(screen.getByRole("button", { name: "Импортировать" }));

    expect(screen.getByText("Готово")).toBeVisible();
    expect(screen.queryByText(/не сошлись/)).not.toBeInTheDocument();
    // И не выдаём за сверенное: «не сверялось» и «сверено, сходится» — разное.
    expect(screen.queryByText(/сходится/)).not.toBeInTheDocument();
  });

  /* Сошедшаяся сверка — самый сильный сигнал доверия, который продукт умеет дать
     по импорту. В первой редакции он был потерян. */
  it("сошедшаяся сверка показана прямо", async () => {
    uploadMock.mockImplementation((_args, opts) =>
      opts?.onSuccess?.({
        status: "success",
        message: "Импортировано 10 операций",
        added_count: 10,
        total_income: 1000,
        total_expense: 500,
        reconciliation: { status: "ok", message: "сходится" },
      }),
    );
    render(<StatementImportSection />);
    await userEvent.upload(screen.getByLabelText("Файл выписки"), file());
    await userEvent.click(screen.getByRole("button", { name: "Импортировать" }));
    expect(screen.getByText(/Сверено с итогами банка/)).toBeVisible();
  });

  /* Во время второй попытки на экране висело «Готово» от первой, а при её отказе —
     зелёное подтверждение того, чего не произошло. */
  it("новая попытка гасит прошлый результат", async () => {
    uploadMock.mockImplementation((_args, opts) =>
      opts?.onSuccess?.({ status: "success", message: "Импортировано 5", added_count: 5 }),
    );
    render(<StatementImportSection />);
    await userEvent.upload(screen.getByLabelText("Файл выписки"), file());
    await userEvent.click(screen.getByRole("button", { name: "Импортировать" }));
    expect(screen.getByText("Готово")).toBeVisible();

    uploadMock.mockImplementation((_args, opts) => opts?.onError?.(new Error("network")));
    await userEvent.upload(screen.getByLabelText("Файл выписки"), file("second.csv"));
    await userEvent.click(screen.getByRole("button", { name: "Импортировать" }));
    expect(screen.queryByText("Готово")).not.toBeInTheDocument();
  });

  /* Сервер разбирает PDF только у трёх банков и сам это говорит в отказе. Общая
     подсказка «CSV, XLSX или PDF» отправляла клиента Альфы за предсказуемым отказом. */
  it("подсказка формата зависит от банка", async () => {
    render(<StatementImportSection />);
    expect(screen.getByText(/Тинькофф: CSV, XLSX или PDF/)).toBeVisible();
    await userEvent.selectOptions(screen.getByLabelText("Банк"), "sber");
    expect(screen.getByText(/Сбербанк: CSV, XLSX или PDF/)).toBeVisible();
  });

  it("банку без разбора PDF его не предлагаем", async () => {
    useBanksMock.mockReturnValue({
      data: [...BANKS, { id: "alfa", name: "Альфа-Банк" }],
      error: null,
      isLoading: false,
    });
    render(<StatementImportSection />);
    await userEvent.selectOptions(screen.getByLabelText("Банк"), "alfa");
    expect(screen.getByText(/PDF этот банк пока не разбирает/)).toBeVisible();
  });

  /* Согласие могли отозвать в другой вкладке — тогда придёт 403, и «проверьте
     соединение» будет неправдой. */
  it("отзыв согласия объяснён по существу, а не как сбой сети", async () => {
    uploadMock.mockImplementation((_args, opts) =>
      opts?.onError?.({ detail: { code: "consent_required", consent_type: "financial_data" } }),
    );
    render(<StatementImportSection />);
    await userEvent.upload(screen.getByLabelText("Файл выписки"), file());
    await userEvent.click(screen.getByRole("button", { name: "Импортировать" }));
    expect(screen.getByText(/Согласие на обработку финансовых данных отозвано/)).toBeVisible();
  });
});
