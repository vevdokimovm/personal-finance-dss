import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ObligationRow } from "./ObligationRow";

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

vi.mock("@entities/obligations", () => ({
  useDeleteObligation: () => ({ mutate: deleteMutate, isPending: false }),
  useRestoreObligation: () => ({ mutate: restoreMutate, isPending: false }),
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
  id: 9,
  name: "Кредитка",
  amount: 120000,
  interest_rate: 0.39,
  term: 12,
  monthly_payment: 8000,
  payment_day: 5,
  months_elapsed: 8,
  months_remaining: 4,
  comment: null,
  household_id: null,
};

beforeEach(() => {
  vi.clearAllMocks();
});

describe("ObligationRow — удаление обратимо", () => {
  it("🔴 успешное удаление переносит фокус и предлагает отмену", async () => {
    deleteMutate.mockImplementation((_id: number, opts?: { onSuccess?: () => void }) =>
      opts?.onSuccess?.(),
    );
    const onDeleted = vi.fn();
    render(<ObligationRow obligation={item} onEdit={() => {}} onDeleted={onDeleted} />);

    await userEvent.click(screen.getByRole("button", { name: /удалить/i }));

    expect(deleteMutate.mock.calls[0][0]).toBe(9);
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
    render(<ObligationRow obligation={item} onEdit={() => {}} onDeleted={() => {}} />);

    await userEvent.click(screen.getByRole("button", { name: /удалить/i }));
    toastUndo.mock.calls[0][1]();

    expect(restoreMutate.mock.calls[0][0]).toBe(9);
    expect(toastSuccess).toHaveBeenCalled();
  });

  it("отказ восстановления сообщается", async () => {
    deleteMutate.mockImplementation((_id: number, opts?: { onSuccess?: () => void }) =>
      opts?.onSuccess?.(),
    );
    restoreMutate.mockImplementation((_id: number, opts?: { onError?: () => void }) =>
      opts?.onError?.(),
    );
    render(<ObligationRow obligation={item} onEdit={() => {}} onDeleted={() => {}} />);

    await userEvent.click(screen.getByRole("button", { name: /удалить/i }));
    toastUndo.mock.calls[0][1]();

    expect(toastError).toHaveBeenCalled();
  });

  it("отказ удаления сообщается и фокус не трогает", async () => {
    deleteMutate.mockImplementation((_id: number, opts?: { onError?: () => void }) =>
      opts?.onError?.(),
    );
    const onDeleted = vi.fn();
    render(<ObligationRow obligation={item} onEdit={() => {}} onDeleted={onDeleted} />);

    await userEvent.click(screen.getByRole("button", { name: /удалить/i }));

    expect(toastError).toHaveBeenCalled();
    expect(onDeleted).not.toHaveBeenCalled();
    expect(toastUndo).not.toHaveBeenCalled();
  });

  it("кнопка правки зовёт обработчик", async () => {
    const onEdit = vi.fn();
    render(<ObligationRow obligation={item} onEdit={onEdit} onDeleted={() => {}} />);

    await userEvent.click(screen.getByRole("button", { name: /изменить|править/i }));
    expect(onEdit).toHaveBeenCalled();
  });
});
