import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AssetForm } from "./AssetForm";

/**
 * Ликвидные активы задают `Lt` — покрытие резервом, на котором стоит жёсткий инвариант
 * модели `Rt ≥ 0`. Ошибка в сумме здесь не остаётся в форме: она меняет весь план.
 *
 * 🔴 Та же граница единиц, что у обязательств: ставка вводится в **процентах**,
 * хранится **долей**. См. `ObligationForm.test.tsx` и `PIT-031`.
 */

const createMutateAsync = vi.fn();
const updateMutateAsync = vi.fn();
let createError: unknown = null;

vi.mock("@entities/assets", () => ({
  useCreateAsset: () => ({
    mutateAsync: createMutateAsync,
    isPending: false,
    error: createError,
  }),
  useUpdateAsset: () => ({ mutateAsync: updateMutateAsync, isPending: false, error: null }),
}));

vi.mock("@features/household-scope", () => ({ HouseholdScopeField: () => null }));

const toastSuccess = vi.fn();
vi.mock("@shared/ui", async () => {
  const actual = await vi.importActual<typeof import("@shared/ui")>("@shared/ui");
  return { ...actual, toast: { ...actual.toast, success: (m: string) => toastSuccess(m) } };
});

beforeEach(() => {
  vi.clearAllMocks();
  createError = null;
});

describe("AssetForm — создание", () => {
  it("🔴 ставка 7 % уходит как 0.07", async () => {
    createMutateAsync.mockResolvedValue({ id: 1 });
    const user = userEvent.setup();
    render(<AssetForm open onOpenChange={() => {}} />);

    await user.type(screen.getByLabelText(/название/i), "Накопительный");
    await user.type(screen.getByLabelText(/сумма/i), "120000");
    await user.type(screen.getByLabelText(/ставк/i), "7");
    await user.click(screen.getByRole("button", { name: /сохранить|добавить/i }));

    await waitFor(() => expect(createMutateAsync).toHaveBeenCalled());
    const body = createMutateAsync.mock.calls[0][0];
    expect(body.interest_rate).toBeCloseTo(0.07, 10);
    expect(body.amount).toBe(120000);
  });

  it("пустой комментарий уезжает как null", async () => {
    createMutateAsync.mockResolvedValue({ id: 1 });
    const user = userEvent.setup();
    render(<AssetForm open onOpenChange={() => {}} />);

    await user.type(screen.getByLabelText(/название/i), "Вклад");
    await user.type(screen.getByLabelText(/сумма/i), "50000");
    await user.click(screen.getByRole("button", { name: /сохранить|добавить/i }));

    await waitFor(() => expect(createMutateAsync).toHaveBeenCalled());
    expect(createMutateAsync.mock.calls[0][0].comment).toBeNull();
  });

  it("без названия фокус уходит в название", async () => {
    render(<AssetForm open onOpenChange={() => {}} />);
    await userEvent.click(screen.getByRole("button", { name: /сохранить|добавить/i }));

    expect(createMutateAsync).not.toHaveBeenCalled();
    await waitFor(() => expect(screen.getByLabelText(/название/i)).toHaveFocus());
  });

  it("🔴 нулевая сумма не сохраняется", async () => {
    /* Актив на ноль рублей — не актив: он войдёт в `Lt` нулём, но займёт строку
       в списке и создаст впечатление резерва, которого нет. */
    const user = userEvent.setup();
    render(<AssetForm open onOpenChange={() => {}} />);

    await user.type(screen.getByLabelText(/название/i), "Пустой");
    await user.type(screen.getByLabelText(/сумма/i), "0");
    await user.click(screen.getByRole("button", { name: /сохранить|добавить/i }));

    expect(createMutateAsync).not.toHaveBeenCalled();
    await waitFor(() => expect(screen.getByLabelText(/сумма/i)).toHaveFocus());
  });
});

describe("AssetForm — ошибка сохранения", () => {
  it("модалка не закрывается", async () => {
    createMutateAsync.mockRejectedValue({ detail: "Сумма слишком велика.", status: 422 });
    createError = { detail: "Сумма слишком велика.", status: 422 };
    const onOpenChange = vi.fn();
    const user = userEvent.setup();
    render(<AssetForm open onOpenChange={onOpenChange} />);

    await user.type(screen.getByLabelText(/название/i), "Вклад");
    await user.type(screen.getByLabelText(/сумма/i), "99999999999");
    await user.click(screen.getByRole("button", { name: /сохранить|добавить/i }));

    await waitFor(() => expect(createMutateAsync).toHaveBeenCalled());
    expect(onOpenChange).not.toHaveBeenCalledWith(false);
    expect(screen.getByRole("alert")).toBeInTheDocument();
  });
});

describe("AssetForm — правка", () => {
  const existing = {
    id: 3,
    name: "Накопительный",
    amount: 120000,
    interest_rate: 0.07,
    type: "deposit" as const,
    comment: null,
  };

  it("ставка показывается процентами", () => {
    render(<AssetForm open onOpenChange={() => {}} asset={existing} />);
    expect(screen.getByLabelText(/ставк/i)).toHaveValue(7);
  });

  it("правка не шлёт household_id", async () => {
    updateMutateAsync.mockResolvedValue({ id: 3 });
    render(<AssetForm open onOpenChange={() => {}} asset={existing} />);

    await userEvent.click(screen.getByRole("button", { name: /сохранить/i }));

    await waitFor(() => expect(updateMutateAsync).toHaveBeenCalled());
    expect(updateMutateAsync.mock.calls[0][0].body).not.toHaveProperty("household_id");
  });
});
