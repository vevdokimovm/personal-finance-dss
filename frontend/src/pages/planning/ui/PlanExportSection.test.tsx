import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { PlanExportSection } from "./PlanExportSection";

// `vi.hoisted` обязателен: `vi.mock` поднимается выше объявлений модуля, и обычные
// `const` были бы ещё не инициализированы к моменту вызова фабрики. Тот же приём, что
// в тестах DashboardPage/PlanningPage.
const { downloadMock, toastError, toastSuccess, FakeDownloadError } = vi.hoisted(() => {
  class FakeDownloadError extends Error {
    status: number;
    detail?: unknown;
    constructor(status: number, detail?: unknown) {
      super("fail");
      this.status = status;
      this.detail = detail;
    }
  }
  return {
    downloadMock: vi.fn(),
    toastError: vi.fn(),
    toastSuccess: vi.fn(),
    FakeDownloadError,
  };
});

vi.mock("@shared/lib/download/downloadFile", () => ({
  downloadFile: (...args: unknown[]) => downloadMock(...args),
  DownloadError: FakeDownloadError,
}));

vi.mock("@shared/ui", async () => {
  const actual = await vi.importActual<typeof import("@shared/ui")>("@shared/ui");
  return { ...actual, toast: { error: toastError, success: toastSuccess } };
});

vi.mock("@entities/consents", () => ({
  ConsentRequiredPanel: ({ detail }: { detail: { message: string } }) => (
    <div role="alert">{detail.message}</div>
  ),
}));

beforeEach(() => {
  downloadMock.mockReset();
  downloadMock.mockResolvedValue("finpilot-plan-2026-09-03.csv");
  toastError.mockClear();
  toastSuccess.mockClear();
});

describe("PlanExportSection — выгрузка плана", () => {
  it("у секции свой заголовок", () => {
    render(<PlanExportSection />);
    expect(screen.getByRole("heading", { name: "Выгрузить план" })).toBeInTheDocument();
  });

  it("предлагает три формата, и у каждого понятное имя", () => {
    render(<PlanExportSection />);
    expect(screen.getByRole("button", { name: /CSV/ })).toBeVisible();
    expect(screen.getByRole("button", { name: /Excel/ })).toBeVisible();
    expect(screen.getByRole("button", { name: /PDF/ })).toBeVisible();
  });

  it("CSV идёт на свой адрес", async () => {
    render(<PlanExportSection />);
    await userEvent.click(screen.getByRole("button", { name: /CSV/ }));
    expect(downloadMock.mock.calls[0][0]).toBe("/api/planning/export.csv");
  });

  it("Excel идёт на xlsx, а не на csv", async () => {
    render(<PlanExportSection />);
    await userEvent.click(screen.getByRole("button", { name: /Excel/ }));
    expect(downloadMock.mock.calls[0][0]).toBe("/api/planning/export.xlsx");
  });

  it("PDF идёт на pdf", async () => {
    render(<PlanExportSection />);
    await userEvent.click(screen.getByRole("button", { name: /PDF/ }));
    expect(downloadMock.mock.calls[0][0]).toBe("/api/planning/export.pdf");
  });

  it("во время скачивания кнопка сообщает о работе и не даёт нажать второй раз", async () => {
    let release: () => void = () => {};
    downloadMock.mockImplementation(
      () => new Promise<void>((resolve) => (release = resolve)),
    );
    render(<PlanExportSection />);
    const csv = screen.getByRole("button", { name: /CSV/ });
    await userEvent.click(csv);

    expect(csv).toHaveAttribute("aria-busy", "true");
    // Подпись формата НЕ подменяется статусом: это доступное имя кнопки.
    expect(csv).toHaveAccessibleName(/CSV/);
    await userEvent.click(csv);
    // Второй клик во время запроса не должен слать второй запрос: файл собирается
    // на сервере, и дубль стоит полного пересчёта плана.
    expect(downloadMock).toHaveBeenCalledTimes(1);

    release();
    await waitFor(() => expect(csv).toHaveAttribute("aria-busy", "false"));
  });

  it("остальные форматы помечены недоступными, пока идёт скачивание (4.1.2)", async () => {
    // Обработчик блокирует клик по ЛЮБОЙ кнопке, пока идёт запрос. Без aria-disabled
    // соседние выглядели бы рабочими, а нажатие не давало бы ничего — ни визуально,
    // ни озвученно.
    downloadMock.mockImplementation(() => new Promise<void>(() => {}));
    render(<PlanExportSection />);
    await userEvent.click(screen.getByRole("button", { name: /CSV/ }));
    const pdf = screen.getByRole("button", { name: /PDF/ });
    expect(pdf).toHaveAttribute("aria-busy", "false");
    expect(pdf).toHaveAttribute("aria-disabled", "true");
  });

  it("успех объявляется live-областью (WCAG 4.1.3)", async () => {
    render(<PlanExportSection />);
    await userEvent.click(screen.getByRole("button", { name: /CSV/ }));
    await waitFor(() =>
      expect(screen.getByRole("status")).toHaveTextContent(/finpilot-plan-2026-09-03\.csv/),
    );
  });

  it("403 уводит фокус на заголовок секции, а не в body (WCAG 2.4.3)", async () => {
    downloadMock.mockRejectedValue(
      new FakeDownloadError(403, {
        code: "consent_required",
        consent_type: "financial_data",
        message: "Нужно согласие.",
        document: { title: "Согласие", url: "/legal/x" },
      }),
    );
    render(<PlanExportSection />);
    await userEvent.click(screen.getByRole("button", { name: /CSV/ }));
    await waitFor(() =>
      expect(screen.getByRole("heading", { name: "Выгрузить план" })).toHaveFocus(),
    );
  });

  /* Смысл того, что скачивание идёт через fetch: отказ виден как отказ. */
  it("403 показывает панель согласия, а не молчание и не битый файл", async () => {
    downloadMock.mockRejectedValue(
      new FakeDownloadError(403, {
        code: "consent_required",
        consent_type: "financial_data",
        message: "Нужно согласие на обработку финансовых данных.",
        document: { title: "Согласие", url: "/legal/x" },
      }),
    );
    render(<PlanExportSection />);
    await userEvent.click(screen.getByRole("button", { name: /CSV/ }));
    await waitFor(() =>
      expect(screen.getByRole("alert")).toHaveTextContent(/Нужно согласие/),
    );
    expect(toastError).not.toHaveBeenCalled();
  });

  it("500 показывает тост, а не панель согласия", async () => {
    downloadMock.mockRejectedValue(new FakeDownloadError(500));
    render(<PlanExportSection />);
    await userEvent.click(screen.getByRole("button", { name: /PDF/ }));
    await waitFor(() => expect(toastError).toHaveBeenCalled());
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  it("после отказа кнопка снова доступна — тупика нет", async () => {
    downloadMock.mockRejectedValue(new FakeDownloadError(500));
    render(<PlanExportSection />);
    const csv = screen.getByRole("button", { name: /CSV/ });
    await userEvent.click(csv);
    await waitFor(() => expect(csv).toHaveAttribute("aria-busy", "false"));
  });

  it("успех подтверждается ВИДИМО и с именем файла (FB-03)", async () => {
    // Плашка загрузок браузера подтверждением не считается: чужой UI, в Safari мигает
    // и прячется, при «скачивать без спроса» её нет вовсе. Асимметрия «отказ говорит,
    // успех молчит» — худший из вариантов.
    render(<PlanExportSection />);
    await userEvent.click(screen.getByRole("button", { name: /CSV/ }));
    await waitFor(() => expect(toastSuccess).toHaveBeenCalled());
    expect(String(toastSuccess.mock.calls[0][0])).toContain("finpilot-plan-2026-09-03.csv");
  });
});
