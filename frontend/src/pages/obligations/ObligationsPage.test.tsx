import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { UseQueryResult } from "@tanstack/react-query";
import { ObligationsPage } from "./ObligationsPage";
import type { Obligation } from "@entities/obligations";

const useObligationsMock = vi.fn();
const createMutateAsyncMock = vi.fn();
const updateMutateAsyncMock = vi.fn();
const restoreMutateMock = vi.fn();
// Мутация удаления реально вызывает onSuccess — иначе не проверить перенос фокуса
// (a11y-auditor, Батч 1: без этого фокус после удаления строки падает в <body>).
const deleteMutateMock = vi.fn((_id: number, opts?: { onSuccess?: () => void }) => {
  opts?.onSuccess?.();
});

vi.mock("@entities/consents", () => ({
  ConsentRequiredPanel: ({ detail }: { detail: { message: string } }) => (
    <div role="alert">{detail.message}</div>
  ),
}));

vi.mock("@entities/obligations", () => ({
  useObligations: () => useObligationsMock(),
  useCreateObligation: () => ({
    mutateAsync: createMutateAsyncMock,
    isPending: false,
    error: null,
  }),
  useUpdateObligation: () => ({
    mutateAsync: updateMutateAsyncMock,
    isPending: false,
    error: null,
  }),
  useDeleteObligation: () => ({ mutate: deleteMutateMock, isPending: false }),
  useRestoreObligation: () => ({ mutate: restoreMutateMock, isPending: false }),
}));

function queryResult(partial: Partial<UseQueryResult<Obligation[]>>): UseQueryResult<Obligation[]> {
  return {
    isLoading: false,
    isError: false,
    data: undefined,
    error: null,
    refetch: vi.fn(),
    ...partial,
  } as UseQueryResult<Obligation[]>;
}

const OBLIGATION: Obligation = {
  id: 1,
  name: "Ипотека",
  type: "mortgage",
  amount: 5000000,
  interest_rate: 0.078,
  monthly_payment: 45000,
  months_elapsed: 24,
  months_remaining: 96,
  payment_day: 5,
  term: 120,
};

describe("ObligationsPage", () => {
  it("показывает скелетон, пока данные грузятся", () => {
    useObligationsMock.mockReturnValue(queryResult({ isLoading: true }));
    render(<ObligationsPage />);
    expect(screen.getByText("Загрузка списка…")).toBeInTheDocument();
  });

  it("показывает состояние ошибки и повторяет запрос по клику", async () => {
    const refetch = vi.fn();
    useObligationsMock.mockReturnValue(queryResult({ isError: true, refetch }));
    render(<ObligationsPage />);
    expect(screen.getByRole("alert")).toHaveTextContent("Не получилось загрузить обязательства");
    await userEvent.click(screen.getByRole("button", { name: "Повторить" }));
    expect(refetch).toHaveBeenCalledOnce();
  });

  it("403 гейт согласия — показывает ConsentRequiredPanel вместо общей ошибки соединения", () => {
    useObligationsMock.mockReturnValue(
      queryResult({
        isError: true,
        error: {
          detail: {
            code: "consent_required",
            consent_type: "financial_data",
            message: "Нужно согласие на финансовые данные.",
          },
        } as unknown as Error,
      }),
    );
    render(<ObligationsPage />);
    expect(screen.getByRole("alert")).toHaveTextContent("Нужно согласие на финансовые данные.");
    expect(screen.queryByText("Не получилось загрузить обязательства")).not.toBeInTheDocument();
  });

  it("показывает пустое состояние без обязательств, с кнопкой добавления внутри панели", () => {
    useObligationsMock.mockReturnValue(queryResult({ data: [] }));
    render(<ObligationsPage />);
    const panel = screen.getByText("Обязательств нет").closest(".fp-state-panel") as HTMLElement;
    expect(panel).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Добавить обязательство" })).toBeInTheDocument();
  });

  it("рендерит обязательство — остаток долга, платёж, ставку, прогресс срока", () => {
    useObligationsMock.mockReturnValue(queryResult({ data: [OBLIGATION] }));
    const { container } = render(<ObligationsPage />);
    expect(screen.getByText("Ипотека")).toBeInTheDocument();
    expect(screen.getByText("5 000 000 ₽")).toBeInTheDocument(); // остаток долга — главное число
    expect(screen.getByText("7,8%")).toBeInTheDocument();
    expect(screen.getByText("24 из 120 мес.")).toBeInTheDocument();
    const fill = container.querySelector(".fp-obligation-row__bar-fill") as HTMLElement;
    expect(fill.style.width).toBe("20%"); // 24/120
  });

  it("кнопка «Добавить обязательство» открывает форму создания (пустые поля)", async () => {
    useObligationsMock.mockReturnValue(queryResult({ data: [OBLIGATION] }));
    render(<ObligationsPage />);
    await userEvent.click(screen.getByRole("button", { name: "Добавить обязательство" }));
    expect(screen.getByRole("heading", { name: "Новое обязательство" })).toBeInTheDocument();
    expect(screen.getByLabelText("Название *")).toHaveValue("");
  });

  it("кнопка «Изменить» на строке открывает форму, поля предзаполнены", async () => {
    useObligationsMock.mockReturnValue(queryResult({ data: [OBLIGATION] }));
    render(<ObligationsPage />);
    await userEvent.click(screen.getAllByRole("button", { name: "Изменить" })[0]);
    expect(screen.getByRole("heading", { name: "Изменить обязательство" })).toBeInTheDocument();
    expect(screen.getByLabelText("Название *")).toHaveValue("Ипотека");
  });

  it("кнопка «Отмена» закрывает форму без сохранения", async () => {
    useObligationsMock.mockReturnValue(queryResult({ data: [OBLIGATION] }));
    render(<ObligationsPage />);
    await userEvent.click(screen.getByRole("button", { name: "Добавить обязательство" }));
    await userEvent.click(screen.getByRole("button", { name: "Отмена" }));
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    expect(createMutateAsyncMock).not.toHaveBeenCalled();
  });

  it("пустое название не отправляет форму — видна ошибка у поля", async () => {
    useObligationsMock.mockReturnValue(queryResult({ data: [OBLIGATION] }));
    render(<ObligationsPage />);
    await userEvent.click(screen.getByRole("button", { name: "Добавить обязательство" }));
    await userEvent.click(screen.getByRole("button", { name: "Добавить" }));
    expect(screen.getByText("Укажите название.")).toBeInTheDocument();
    expect(createMutateAsyncMock).not.toHaveBeenCalled();
  });

  it("кнопка «Удалить» вызывает мутацию удаления и переносит фокус на «Добавить»", async () => {
    useObligationsMock.mockReturnValue(queryResult({ data: [OBLIGATION] }));
    render(<ObligationsPage />);
    await userEvent.click(screen.getByRole("button", { name: "Удалить «Ипотека»" }));
    expect(deleteMutateMock).toHaveBeenCalledWith(1, expect.any(Object));
    // Фокус не должен провалиться в <body> после исчезновения строки (a11y-auditor, Батч 1).
    expect(screen.getByRole("button", { name: "Добавить обязательство" })).toHaveFocus();
  });
});
