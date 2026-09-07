import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AssetRow } from "./AssetRow";

/**
 * Строка списка активов. Тот же паттерн, что у обязательств, операций, целей
 * и бюджетов: удаление **обратимое**, с предложением отмены.
 *
 * 🔴 **Отмена здесь не украшение, а замена диалогу подтверждения.** Продукт выбрал
 * «удалить сразу + вернуть» вместо «подтвердите удаление»: первое дешевле для того,
 * кто удаляет осознанно, и не хуже для того, кто промахнулся. Но это работает, только
 * если «Вернуть» действительно возвращает — иначе выбран худший из двух вариантов.
 *
 * 🔴 **`onDeleted` переносит фокус.** Строка исчезает вместе с кнопкой, на которой он
 * стоял; без переноса фокус проваливается в `<body>`, и человек с клавиатурой теряет
 * место на странице (a11y-auditor, WCAG 2.4.3).
 *
 * 🔴 **Ставка — ДОЛЯ, а не проценты** (`Numeric(6,4)` в обеих таблицах). 0.14 на экране
 * обязано читаться как «14 % годовых»: голое число рядом с денежной суммой легко принять
 * за долю портфеля.
 */

const deleteMutate = vi.fn();
const restoreMutate = vi.fn();

vi.mock("@entities/assets", () => ({
  useDeleteAsset: () => ({ mutate: deleteMutate, isPending: false }),
  useRestoreAsset: () => ({ mutate: restoreMutate, isPending: false }),
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

const asset = {
  id: 3,
  name: "Накопительный",
  amount: 120000,
  interest_rate: 0.14,
  type: "savings_account" as const,
  comment: null,
  household_id: null,
};

beforeEach(() => {
  vi.clearAllMocks();
});

describe("AssetRow — что видно", () => {
  it("ставка показана процентами, а не долей", () => {
    render(<AssetRow asset={asset} onEdit={() => {}} onDeleted={() => {}} />);
    expect(screen.getByText(/14/)).toBeInTheDocument();
    expect(screen.getByText(/годовых/)).toBeInTheDocument();
  });

  it("тип переведён, а не показан служебным кодом", () => {
    /* `savings_account` — значение контракта, человеку оно ничего не говорит. */
    render(<AssetRow asset={asset} onEdit={() => {}} onDeleted={() => {}} />);
    expect(screen.getByText("Накопительный счёт")).toBeInTheDocument();
  });

  it("общий актив помечен, личный — нет", () => {
    const { rerender } = render(<AssetRow asset={asset} onEdit={() => {}} onDeleted={() => {}} />);
    expect(screen.queryByTestId("shared-badge")).not.toBeInTheDocument();

    rerender(
      <AssetRow asset={{ ...asset, household_id: 7 }} onEdit={() => {}} onDeleted={() => {}} />,
    );
    expect(screen.getByTestId("shared-badge")).toBeInTheDocument();
  });
});

describe("AssetRow — удаление обратимо", () => {
  it("🔴 успешное удаление переносит фокус и предлагает отмену", async () => {
    deleteMutate.mockImplementation((_id: number, opts?: { onSuccess?: () => void }) =>
      opts?.onSuccess?.(),
    );
    const onDeleted = vi.fn();
    render(<AssetRow asset={asset} onEdit={() => {}} onDeleted={onDeleted} />);

    await userEvent.click(screen.getByRole("button", { name: /удалить/i }));

    expect(deleteMutate.mock.calls[0][0]).toBe(3);
    expect(onDeleted).toHaveBeenCalled();
    expect(toastUndo).toHaveBeenCalled();
  });

  it("🔴 «Вернуть» действительно восстанавливает ТОТ ЖЕ актив", async () => {
    /* Если отмена вернёт не то или не сработает, выбранная схема «удалить сразу»
       оказывается хуже диалога подтверждения, который она заменила. */
    deleteMutate.mockImplementation((_id: number, opts?: { onSuccess?: () => void }) =>
      opts?.onSuccess?.(),
    );
    restoreMutate.mockImplementation((_id: number, opts?: { onSuccess?: () => void }) =>
      opts?.onSuccess?.(),
    );
    render(<AssetRow asset={asset} onEdit={() => {}} onDeleted={() => {}} />);

    await userEvent.click(screen.getByRole("button", { name: /удалить/i }));
    toastUndo.mock.calls[0][1]();

    expect(restoreMutate.mock.calls[0][0]).toBe(3);
    expect(toastSuccess).toHaveBeenCalled();
  });

  it("отказ восстановления сообщается — обратимость не всегда срабатывает", async () => {
    deleteMutate.mockImplementation((_id: number, opts?: { onSuccess?: () => void }) =>
      opts?.onSuccess?.(),
    );
    restoreMutate.mockImplementation((_id: number, opts?: { onError?: () => void }) =>
      opts?.onError?.(),
    );
    render(<AssetRow asset={asset} onEdit={() => {}} onDeleted={() => {}} />);

    await userEvent.click(screen.getByRole("button", { name: /удалить/i }));
    toastUndo.mock.calls[0][1]();

    expect(toastError).toHaveBeenCalled();
  });

  it("отказ удаления сообщается и фокус не трогает", async () => {
    /* Строка осталась на месте — переносить фокус некуда и незачем. */
    deleteMutate.mockImplementation((_id: number, opts?: { onError?: () => void }) =>
      opts?.onError?.(),
    );
    const onDeleted = vi.fn();
    render(<AssetRow asset={asset} onEdit={() => {}} onDeleted={onDeleted} />);

    await userEvent.click(screen.getByRole("button", { name: /удалить/i }));

    expect(toastError).toHaveBeenCalled();
    expect(onDeleted).not.toHaveBeenCalled();
    expect(toastUndo).not.toHaveBeenCalled();
  });

  it("кнопка правки зовёт обработчик", async () => {
    const onEdit = vi.fn();
    render(<AssetRow asset={asset} onEdit={onEdit} onDeleted={() => {}} />);

    await userEvent.click(screen.getByRole("button", { name: /изменить|править/i }));
    expect(onEdit).toHaveBeenCalled();
  });
});
