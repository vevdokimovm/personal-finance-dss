import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { BudgetRow } from "./BudgetRow";

/**
 * Строка списка. Тот же паттерн обратимого удаления, что у `AssetRow`:
 * удалить сразу и предложить «Вернуть» вместо диалога подтверждения.
 *
 * 🔴 **Схема работает, только если «Вернуть» действительно возвращает.** Иначе продукт
 * выбрал худший из двух вариантов: и подтверждения нет, и восстановления нет.
 *
 * 🔴 **`onDeleted` переносит фокус:** строка исчезает вместе с кнопкой, на которой он
 * стоял, и без переноса проваливается в `<body>` (a11y-auditor, WCAG 2.4.3).
 */

const deleteMutate = vi.fn();
const restoreMutate = vi.fn();

vi.mock("@entities/budgets", () => ({
  useDeleteBudget: () => ({ mutate: deleteMutate, isPending: false }),
  useRestoreBudget: () => ({ mutate: restoreMutate, isPending: false }),
}));

vi.mock("@features/household-scope", () => ({
  SharedBadge: ({ householdId }: { householdId?: number | null }) =>
    householdId == null ? null : <span data-testid="shared-badge">Общая</span>,
}));

const { toastUndo, toastSuccess, toastError } = vi.hoisted(() => ({
  toastUndo: vi.fn(),
  toastSuccess: vi.fn(),
  toastError: vi.fn(),
}));
vi.mock("@shared/ui", async () => {
  const actual = await vi.importActual<typeof import("@shared/ui")>("@shared/ui");
  return {
    ...actual,
    toast: { ...actual.toast, undo: toastUndo, success: toastSuccess, error: toastError },
  };
});

const item = {
  id: 5,
  category: "Продукты",
  limit_amount: 15000,
  spent: 9000,
  pct: 60,
  over: false,
  household_id: null,
};

beforeEach(() => {
  vi.clearAllMocks();
});

describe("BudgetRow — удаление обратимо", () => {
  it("🔴 успешное удаление переносит фокус и предлагает отмену", async () => {
    deleteMutate.mockImplementation((_id: number, opts?: { onSuccess?: () => void }) =>
      opts?.onSuccess?.(),
    );
    const onDeleted = vi.fn();
    render(<BudgetRow budget={item} onEdit={() => {}} onDeleted={onDeleted} />);

    await userEvent.click(screen.getByRole("button", { name: /удалить/i }));

    expect(deleteMutate.mock.calls[0][0]).toBe(5);
    expect(onDeleted).toHaveBeenCalled();
    expect(toastUndo).toHaveBeenCalled();
  });

  it("🔴 «Вернуть» восстанавливает ту же запись", async () => {
    deleteMutate.mockImplementation((_id: number, opts?: { onSuccess?: () => void }) =>
      opts?.onSuccess?.(),
    );
    restoreMutate.mockImplementation((_id: number, opts?: { onSuccess?: () => void }) =>
      opts?.onSuccess?.(),
    );
    render(<BudgetRow budget={item} onEdit={() => {}} onDeleted={() => {}} />);

    await userEvent.click(screen.getByRole("button", { name: /удалить/i }));
    toastUndo.mock.calls[0][1]();

    expect(restoreMutate.mock.calls[0][0]).toBe(5);
    expect(toastSuccess).toHaveBeenCalled();
  });

  it("отказ восстановления сообщается", async () => {
    deleteMutate.mockImplementation((_id: number, opts?: { onSuccess?: () => void }) =>
      opts?.onSuccess?.(),
    );
    restoreMutate.mockImplementation((_id: number, opts?: { onError?: () => void }) =>
      opts?.onError?.(),
    );
    render(<BudgetRow budget={item} onEdit={() => {}} onDeleted={() => {}} />);

    await userEvent.click(screen.getByRole("button", { name: /удалить/i }));
    toastUndo.mock.calls[0][1]();

    expect(toastError).toHaveBeenCalled();
  });

  it("отказ удаления сообщается и фокус не трогает", async () => {
    deleteMutate.mockImplementation((_id: number, opts?: { onError?: () => void }) =>
      opts?.onError?.(),
    );
    const onDeleted = vi.fn();
    render(<BudgetRow budget={item} onEdit={() => {}} onDeleted={onDeleted} />);

    await userEvent.click(screen.getByRole("button", { name: /удалить/i }));

    expect(toastError).toHaveBeenCalled();
    expect(onDeleted).not.toHaveBeenCalled();
    expect(toastUndo).not.toHaveBeenCalled();
  });

  it("кнопка правки зовёт обработчик", async () => {
    const onEdit = vi.fn();
    render(<BudgetRow budget={item} onEdit={onEdit} onDeleted={() => {}} />);

    await userEvent.click(screen.getByRole("button", { name: /изменить|править/i }));
    expect(onEdit).toHaveBeenCalled();
  });
});
