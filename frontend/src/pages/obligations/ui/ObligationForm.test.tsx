import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ObligationForm } from "./ObligationForm";

/**
 * 🔴 **Главное здесь — граница единиц измерения, и она уже один раз стоила дефекта.**
 *
 * Человек вводит ставку в **процентах** (39), модель хранит **долю** (0.39). Перевод
 * делает форма: `(Number(interestRatePct) || 0) / 100`. Это единственное место, где
 * две единицы встречаются, и ошибка здесь не видна ни в одном другом тесте: число
 * пройдёт валидацию, сохранится и молча уедет в Avalanche-фильтр, который выберет
 * не тот долг для досрочного погашения.
 *
 * `PIT-031` — про то же самое с другой стороны: тест был написан под то же неверное
 * представление, что и код, и оба сошлись на 39 вместо 0.39. Зелёный тест поверх
 * неверного расчёта. Поэтому проверка ниже сверяет именно **число, ушедшее в мутацию**,
 * а не то, что показано в поле.
 */

const createMutateAsync = vi.fn();
const updateMutateAsync = vi.fn();
let createError: unknown = null;

vi.mock("@entities/obligations", () => ({
  useCreateObligation: () => ({
    mutateAsync: createMutateAsync,
    isPending: false,
    error: createError,
  }),
  useUpdateObligation: () => ({
    mutateAsync: updateMutateAsync,
    isPending: false,
    error: null,
  }),
}));

vi.mock("@features/household-scope", () => ({ HouseholdScopeField: () => null }));

const toastSuccess = vi.fn();
vi.mock("@shared/ui", async () => {
  const actual = await vi.importActual<typeof import("@shared/ui")>("@shared/ui");
  return { ...actual, toast: { ...actual.toast, success: (m: string) => toastSuccess(m) } };
});

async function fillRequired(user: ReturnType<typeof userEvent.setup>) {
  await user.type(screen.getByLabelText(/название/i), "Кредитка");
  await user.type(screen.getByLabelText(/остаток долга|сумма/i), "120000");
  await user.type(screen.getByLabelText(/платёж/i), "8000");
}

beforeEach(() => {
  vi.clearAllMocks();
  createError = null;
});

describe("ObligationForm — ставка: проценты на экране, доля в модели", () => {
  it("🔴 введённые 39 % уходят как 0.39", async () => {
    createMutateAsync.mockResolvedValue({ id: 1 });
    const user = userEvent.setup();
    render(<ObligationForm open onOpenChange={() => {}} />);

    await fillRequired(user);
    await user.type(screen.getByLabelText(/ставк/i), "39");
    await user.click(screen.getByRole("button", { name: /сохранить|добавить/i }));

    await waitFor(() => expect(createMutateAsync).toHaveBeenCalled());
    expect(createMutateAsync.mock.calls[0][0].interest_rate).toBeCloseTo(0.39, 10);
  });

  it("пустая ставка — это 0, а не NaN", async () => {
    /* `Number("") === NaN`, и без `|| 0` в тело ушёл бы `NaN`: JSON сериализует его
       в `null`, бэкенд ответит 422, и человек увидит отказ на форме, где он просто
       не стал заполнять необязательное поле. */
    createMutateAsync.mockResolvedValue({ id: 1 });
    const user = userEvent.setup();
    render(<ObligationForm open onOpenChange={() => {}} />);

    await fillRequired(user);
    await user.click(screen.getByRole("button", { name: /сохранить|добавить/i }));

    await waitFor(() => expect(createMutateAsync).toHaveBeenCalled());
    expect(createMutateAsync.mock.calls[0][0].interest_rate).toBe(0);
  });
});

describe("ObligationForm — валидация ведёт к полю", () => {
  it("без названия фокус уходит в название", async () => {
    render(<ObligationForm open onOpenChange={() => {}} />);
    await userEvent.click(screen.getByRole("button", { name: /сохранить|добавить/i }));

    expect(createMutateAsync).not.toHaveBeenCalled();
    await waitFor(() => expect(screen.getByLabelText(/название/i)).toHaveFocus());
  });

  it("без платежа фокус уходит в платёж", async () => {
    /* Минимальный платёж входит в расчёт ПДН — без него обязательство бессмысленно
       для модели, и пропустить его нельзя. */
    const user = userEvent.setup();
    render(<ObligationForm open onOpenChange={() => {}} />);

    await user.type(screen.getByLabelText(/название/i), "Кредитка");
    await user.type(screen.getByLabelText(/остаток долга|сумма/i), "120000");
    await user.click(screen.getByRole("button", { name: /сохранить|добавить/i }));

    expect(createMutateAsync).not.toHaveBeenCalled();
    await waitFor(() => expect(screen.getByLabelText(/платёж/i)).toHaveFocus());
  });
});

describe("ObligationForm — ошибка сохранения", () => {
  it("модалка не закрывается, введённое остаётся", async () => {
    createMutateAsync.mockRejectedValue({ detail: "Ставка вне диапазона.", status: 422 });
    createError = { detail: "Ставка вне диапазона.", status: 422 };
    const onOpenChange = vi.fn();
    const user = userEvent.setup();
    render(<ObligationForm open onOpenChange={onOpenChange} />);

    await fillRequired(user);
    await user.click(screen.getByRole("button", { name: /сохранить|добавить/i }));

    await waitFor(() => expect(createMutateAsync).toHaveBeenCalled());
    expect(onOpenChange).not.toHaveBeenCalledWith(false);
    expect(screen.getByRole("alert")).toHaveTextContent(/ставк/i);
  });
});

describe("ObligationForm — правка", () => {
  const existing = {
    id: 9,
    name: "Кредитка",
    amount: 120000,
    interest_rate: 0.39,
    term: 12,
    monthly_payment: 8000,
    payment_day: 5,
    start_date: "2026-01-01T00:00:00Z",
    comment: null,
    // Считает бэкенд по сроку и дате старта; форма их не правит, но контракт требует.
    months_elapsed: 8,
    months_remaining: 4,
  };

  it("ставка показывается процентами, а хранится долей", () => {
    /* Обратный перевод при загрузке формы: 0.39 в модели — «39» на экране.
       Показать долю значило бы предложить человеку править 0.39 руками. */
    render(<ObligationForm open onOpenChange={() => {}} obligation={existing} />);
    expect(screen.getByLabelText(/ставк/i)).toHaveValue(39);
  });

  it("правка не шлёт household_id — владение записи не меняется", async () => {
    updateMutateAsync.mockResolvedValue({ id: 9 });
    render(<ObligationForm open onOpenChange={() => {}} obligation={existing} />);

    await userEvent.click(screen.getByRole("button", { name: /сохранить/i }));

    await waitFor(() => expect(updateMutateAsync).toHaveBeenCalled());
    const args = updateMutateAsync.mock.calls[0][0];
    expect(args.id).toBe(9);
    expect(args.body).not.toHaveProperty("household_id");
  });
});
