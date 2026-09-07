import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { BudgetForm } from "./BudgetForm";

/**
 * Форма бюджета — единственная в продукте, где создание и правка идут ОДНИМ
 * эндпоинтом: `POST /api/budgets` работает upsert-ом по категории.
 *
 * 🔴 **Отсюда её особенность: при правке категория заблокирована.** Сменить её значит
 * создать второй бюджет, а не переименовать первый, — и человек получил бы дубль
 * вместо правки. Бэкенд ключ-замену не поддерживает (v9.2.0: попытка сменить владение
 * отвечает 409 по той же причине).
 */

const createMutateAsync = vi.fn();
let mutationError: unknown = null;

vi.mock("@entities/budgets", () => ({
  useCreateBudget: () => ({
    mutateAsync: createMutateAsync,
    isPending: false,
    error: mutationError,
  }),
}));

vi.mock("@features/household-scope", () => ({ HouseholdScopeField: () => null }));

const toastSuccess = vi.fn();
vi.mock("@shared/ui", async () => {
  const actual = await vi.importActual<typeof import("@shared/ui")>("@shared/ui");
  return { ...actual, toast: { ...actual.toast, success: (m: string) => toastSuccess(m) } };
});

const budget = {
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
  mutationError = null;
});

describe("BudgetForm — создание", () => {
  it("шлёт категорию и лимит", async () => {
    createMutateAsync.mockResolvedValue({ id: 1 });
    const user = userEvent.setup();
    render(<BudgetForm open onOpenChange={() => {}} />);

    await user.type(screen.getByLabelText(/категор/i), "Кафе");
    await user.type(screen.getByLabelText(/Лимит в месяц/), "7000");
    await user.click(screen.getByRole("button", { name: /сохранить|добавить|создать/i }));

    await waitFor(() => expect(createMutateAsync).toHaveBeenCalled());
    const body = createMutateAsync.mock.calls[0][0];
    expect(body.category).toBe("Кафе");
    expect(body.limit_amount).toBe(7000);
  });

  it("нулевой лимит не отправляется", async () => {
    /* Бюджет на ноль рублей превышен в момент создания и будет краснеть всегда —
       это не ограничение, а постоянный упрёк. */
    const user = userEvent.setup();
    render(<BudgetForm open onOpenChange={() => {}} />);

    await user.type(screen.getByLabelText(/категор/i), "Кафе");
    await user.type(screen.getByLabelText(/Лимит в месяц/), "0");
    await user.click(screen.getByRole("button", { name: /сохранить|добавить|создать/i }));

    expect(createMutateAsync).not.toHaveBeenCalled();
  });

  it("пустая категория не отправляется", async () => {
    const user = userEvent.setup();
    render(<BudgetForm open onOpenChange={() => {}} />);

    await user.type(screen.getByLabelText(/Лимит в месяц/), "7000");
    await user.click(screen.getByRole("button", { name: /сохранить|добавить|создать/i }));

    expect(createMutateAsync).not.toHaveBeenCalled();
  });
});

describe("BudgetForm — правка", () => {
  it("🔴 категория заблокирована: смена создала бы дубль, а не переименование", async () => {
    /* `POST /api/budgets` — upsert ПО КАТЕГОРИИ. Отправить другую категорию значит
       завести вторую строку, оставив первую нетронутой. Форма закрывает этот путь
       на входе, потому что бэкенд ключ-замену не поддерживает. */
    render(<BudgetForm open onOpenChange={() => {}} budget={budget} />);
    expect(screen.getByLabelText(/категор/i)).toBeDisabled();
  });

  it("правка лимита НЕ шлёт household_id — владение не меняется", async () => {
    /* Симметрично v9.2.0: при правке поле отсутствует, и бэкенд трактует это
       как «не трогай владение». Отправить его значило бы запросить смену,
       на которую сервер ответит 409. */
    createMutateAsync.mockResolvedValue({ id: 5 });
    const user = userEvent.setup();
    render(<BudgetForm open onOpenChange={() => {}} budget={budget} />);

    await user.clear(screen.getByLabelText(/Лимит в месяц/));
    await user.type(screen.getByLabelText(/Лимит в месяц/), "20000");
    await user.click(screen.getByRole("button", { name: /сохранить/i }));

    await waitFor(() => expect(createMutateAsync).toHaveBeenCalled());
    expect(createMutateAsync.mock.calls[0][0]).not.toHaveProperty("household_id");
  });
});

describe("BudgetForm — ошибка сохранения", () => {
  it("модалка не закрывается, ошибка видна", async () => {
    createMutateAsync.mockRejectedValue({ detail: "Категория уже занята.", status: 409 });
    mutationError = { detail: "Категория уже занята.", status: 409 };
    const onOpenChange = vi.fn();
    const user = userEvent.setup();
    render(<BudgetForm open onOpenChange={onOpenChange} />);

    await user.type(screen.getByLabelText(/категор/i), "Кафе");
    await user.type(screen.getByLabelText(/Лимит в месяц/), "7000");
    await user.click(screen.getByRole("button", { name: /сохранить|добавить|создать/i }));

    await waitFor(() => expect(createMutateAsync).toHaveBeenCalled());
    expect(onOpenChange).not.toHaveBeenCalledWith(false);
    expect(screen.getByRole("alert")).toBeInTheDocument();
  });
});
