import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { GoalForm } from "./GoalForm";

/**
 * 🔴 **У цели есть поле, которого нет ни у одной другой сущности: связь с активом.**
 *
 * Связанная цель пополняется через свой актив, а не напрямую — бэкенд отвечает 409
 * на попытку внести взнос вручную. Значит выбор здесь определяет, будет ли у человека
 * работать кнопка «внести прогресс» на экране целей.
 *
 * Пустой выбор обязан превратиться в `null`, а не в `0` или `NaN`: `linked_asset_id: 0`
 * означает «актив с id 0», которого нет, и цель молча привяжется к несуществующему.
 *
 * 🔴 **`current_amount: 0` шлётся только при СОЗДАНИИ.** В правке его нет намеренно:
 * послать ноль при редактировании значило бы обнулить накопленное — ровно тот дефект,
 * от которого отделена операция «внести прогресс» (см. `useGoals.test.tsx`).
 */

const createMutateAsync = vi.fn();
const updateMutateAsync = vi.fn();
let createError: unknown = null;

vi.mock("@entities/goals", async () => {
  const actual = await vi.importActual<typeof import("@entities/goals")>("@entities/goals");
  return {
    ...actual,
    useCreateGoal: () => ({
      mutateAsync: createMutateAsync,
      isPending: false,
      error: createError,
    }),
    useUpdateGoal: () => ({ mutateAsync: updateMutateAsync, isPending: false, error: null }),
  };
});

/* Список активов нужен форме только для выпадающего списка связи. Настоящий хук
   потянул бы `QueryClientProvider` во все тесты файла ради одного поля. */
vi.mock("@entities/assets", () => ({
  useLiquidAssets: () => ({
    data: [{ id: 3, name: "Накопительный", amount: 120000 }],
    isSuccess: true,
    isLoading: false,
  }),
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

describe("GoalForm — создание", () => {
  it("🔴 связь с активом не выбрана — уходит null, а не 0", async () => {
    /* `linked_asset_id: 0` означает «актив с id 0»: цель привязалась бы
       к несуществующему, и внести прогресс вручную стало бы нельзя (409),
       а через актив — некуда. Тупик, из которого нет выхода в интерфейсе. */
    createMutateAsync.mockResolvedValue({ id: 1 });
    const user = userEvent.setup();
    render(<GoalForm open onOpenChange={() => {}} />);

    await user.type(screen.getByLabelText(/название/i), "Отпуск");
    await user.type(screen.getByLabelText(/сумма цели|целевая сумма/i), "200000");
    await user.click(screen.getByRole("button", { name: /сохранить|добавить/i }));

    await waitFor(() => expect(createMutateAsync).toHaveBeenCalled());
    const body = createMutateAsync.mock.calls[0][0];
    expect(body.linked_asset_id).toBeNull();
    expect(body.deadline).toBeNull();
    expect(body.comment).toBeNull();
  });

  it("новая цель начинается с нуля накоплений", async () => {
    createMutateAsync.mockResolvedValue({ id: 1 });
    const user = userEvent.setup();
    render(<GoalForm open onOpenChange={() => {}} />);

    await user.type(screen.getByLabelText(/название/i), "Машина");
    await user.type(screen.getByLabelText(/сумма цели|целевая сумма/i), "500000");
    await user.click(screen.getByRole("button", { name: /сохранить|добавить/i }));

    await waitFor(() => expect(createMutateAsync).toHaveBeenCalled());
    expect(createMutateAsync.mock.calls[0][0].current_amount).toBe(0);
  });

  it("без названия фокус уходит в название", async () => {
    render(<GoalForm open onOpenChange={() => {}} />);
    await userEvent.click(screen.getByRole("button", { name: /сохранить|добавить/i }));

    expect(createMutateAsync).not.toHaveBeenCalled();
    await waitFor(() => expect(screen.getByLabelText(/название/i)).toHaveFocus());
  });

  it("нулевая сумма цели не сохраняется", async () => {
    /* Цель на ноль рублей достигнута в момент создания — она засоряет план
       и отнимает долю распределения ни на что. */
    const user = userEvent.setup();
    render(<GoalForm open onOpenChange={() => {}} />);

    await user.type(screen.getByLabelText(/название/i), "Пустая");
    await user.type(screen.getByLabelText(/сумма цели|целевая сумма/i), "0");
    await user.click(screen.getByRole("button", { name: /сохранить|добавить/i }));

    expect(createMutateAsync).not.toHaveBeenCalled();
  });
});

describe("GoalForm — правка", () => {
  const existing = {
    id: 4,
    name: "Отпуск",
    target_amount: 200000,
    current_amount: 305000,
    deadline: null,
    category: "travel" as const,
    linked_asset_id: null,
    comment: null,
  };

  it("🔴 правка НЕ шлёт current_amount — накопленное неприкосновенно", async () => {
    /* Послать сюда ноль (или значение из формы) значило бы стереть накопленное
       за год. Именно ради этого «внести прогресс» вынесено в отдельную операцию,
       которая ПРИБАВЛЯЕТ. */
    updateMutateAsync.mockResolvedValue({ id: 4 });
    render(<GoalForm open onOpenChange={() => {}} goal={existing} />);

    await userEvent.click(screen.getByRole("button", { name: /сохранить/i }));

    await waitFor(() => expect(updateMutateAsync).toHaveBeenCalled());
    const args = updateMutateAsync.mock.calls[0][0];
    expect(args.id).toBe(4);
    expect(args.body).not.toHaveProperty("current_amount");
    expect(args.body).not.toHaveProperty("household_id");
  });
});

describe("GoalForm — ошибка сохранения", () => {
  it("модалка не закрывается", async () => {
    createMutateAsync.mockRejectedValue({ detail: "Такая цель уже есть.", status: 409 });
    createError = { detail: "Такая цель уже есть.", status: 409 };
    const onOpenChange = vi.fn();
    const user = userEvent.setup();
    render(<GoalForm open onOpenChange={onOpenChange} />);

    await user.type(screen.getByLabelText(/название/i), "Отпуск");
    await user.type(screen.getByLabelText(/сумма цели|целевая сумма/i), "200000");
    await user.click(screen.getByRole("button", { name: /сохранить|добавить/i }));

    await waitFor(() => expect(createMutateAsync).toHaveBeenCalled());
    expect(onOpenChange).not.toHaveBeenCalledWith(false);
    expect(screen.getByRole("alert")).toBeInTheDocument();
  });
});
