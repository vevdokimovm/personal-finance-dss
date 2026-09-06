import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TransactionForm } from "./TransactionForm";

/**
 * Форма операции — самая непокрытая часть фронта на момент v9.2.0 (37.8 % строк).
 *
 * 🔴 **Здесь три решения, каждое из которых ломается молча:**
 *
 * 1. **Фокус на первое неверное поле.** Человек нажал «Сохранить», ничего не произошло,
 *    сообщение об ошибке ниже линии сгиба — он не понял, что от него хотят.
 *    Требование a11y-auditor, и проверить его можно только тестом: глазами
 *    «фокус переехал» на большом экране не заметно.
 * 2. **Пустая строка превращается в `null`, а не уезжает как `""`.** Категория `""`
 *    на бэкенде — это категория с пустым именем, и она попадёт в отчёты и в бюджеты
 *    отдельной строкой.
 * 3. **Модалка НЕ закрывается при ошибке сохранения.** Закрыть значит потерять
 *    введённое: человек заполнял форму, получил отказ сервера и остался с пустым
 *    экраном без своих данных.
 */

const createMutateAsync = vi.fn();
const updateMutateAsync = vi.fn();
let createError: unknown = null;
let updateError: unknown = null;

vi.mock("@entities/transactions", () => ({
  useCreateTransaction: () => ({
    mutateAsync: createMutateAsync,
    isPending: false,
    error: createError,
  }),
  useUpdateTransaction: () => ({
    mutateAsync: updateMutateAsync,
    isPending: false,
    error: updateError,
  }),
}));

/* Выбор владельца записи — предмет своего файла тестов (`features/household-scope`).
   Настоящий компонент тянет `useHouseholds`, а с ним `QueryClientProvider`, ради поля,
   к утверждениям этого файла отношения не имеющего. Тот же приём, что в `BudgetsSection`. */
vi.mock("@features/household-scope", () => ({
  HouseholdScopeField: () => null,
}));

const toastSuccess = vi.fn();
vi.mock("@shared/ui", async () => {
  const actual = await vi.importActual<typeof import("@shared/ui")>("@shared/ui");
  return { ...actual, toast: { ...actual.toast, success: (m: string) => toastSuccess(m) } };
});

beforeEach(() => {
  vi.clearAllMocks();
  createError = null;
  updateError = null;
});

describe("TransactionForm — создание", () => {
  it("🔴 пустая сумма не отправляется, а фокус уходит в поле суммы", async () => {
    /* Без переноса фокуса человек жмёт «Сохранить», ничего не происходит,
       и он не знает, куда смотреть. */
    render(<TransactionForm open onOpenChange={() => {}} />);
    await userEvent.click(screen.getByRole("button", { name: /сохранить|добавить/i }));

    expect(createMutateAsync).not.toHaveBeenCalled();
    await waitFor(() => expect(screen.getByLabelText(/сумма/i)).toHaveFocus());
  });

  it("🔴 пустая категория уезжает как null, а не как пустая строка", async () => {
    /* Категория `""` на бэкенде — категория с пустым именем: она появится
       в отчётах и бюджетах отдельной строкой, и убрать её оттуда будет нечем. */
    createMutateAsync.mockResolvedValue({ id: 1 });
    render(<TransactionForm open onOpenChange={() => {}} />);

    await userEvent.type(screen.getByLabelText(/сумма/i), "1200");
    await userEvent.click(screen.getByRole("button", { name: /сохранить|добавить/i }));

    await waitFor(() => expect(createMutateAsync).toHaveBeenCalled());
    const body = createMutateAsync.mock.calls[0][0];
    expect(body.category).toBeNull();
    expect(body.description).toBeNull();
    expect(body.amount).toBe(1200);
  });

  it("дата уходит в ISO, а не как значение поля", async () => {
    /* Поле `<input type="date">` отдаёт `2026-09-06`; бэкенд ждёт полный ISO.
       Послать как есть — получить 422 на каждой операции. */
    createMutateAsync.mockResolvedValue({ id: 1 });
    render(<TransactionForm open onOpenChange={() => {}} />);

    await userEvent.type(screen.getByLabelText(/сумма/i), "500");
    await userEvent.click(screen.getByRole("button", { name: /сохранить|добавить/i }));

    await waitFor(() => expect(createMutateAsync).toHaveBeenCalled());
    expect(createMutateAsync.mock.calls[0][0].date).toMatch(/^\d{4}-\d{2}-\d{2}T/);
  });

  it("успех закрывает модалку и сообщает об этом", async () => {
    createMutateAsync.mockResolvedValue({ id: 1 });
    const onOpenChange = vi.fn();
    render(<TransactionForm open onOpenChange={onOpenChange} />);

    await userEvent.type(screen.getByLabelText(/сумма/i), "900");
    await userEvent.click(screen.getByRole("button", { name: /сохранить|добавить/i }));

    await waitFor(() => expect(onOpenChange).toHaveBeenCalledWith(false));
    expect(toastSuccess).toHaveBeenCalled();
  });
});

describe("TransactionForm — ошибка сохранения", () => {
  it("🔴 модалка НЕ закрывается: введённое не должно пропасть", async () => {
    /* Закрыть форму на ошибке значит стереть работу человека и оставить его
       перед пустым экраном. Ошибка показывается баннером внутри формы. */
    createMutateAsync.mockRejectedValue({ detail: "Дата в будущем.", status: 422 });
    createError = { detail: "Дата в будущем.", status: 422 };
    const onOpenChange = vi.fn();
    render(<TransactionForm open onOpenChange={onOpenChange} />);

    await userEvent.type(screen.getByLabelText(/сумма/i), "700");
    await userEvent.click(screen.getByRole("button", { name: /сохранить|добавить/i }));

    await waitFor(() => expect(createMutateAsync).toHaveBeenCalled());
    expect(onOpenChange).not.toHaveBeenCalledWith(false);
    expect(screen.getByRole("alert")).toHaveTextContent(/дата/i);
  });
});

describe("TransactionForm — правка", () => {
  const existing = {
    id: 42,
    amount: 1500,
    type: "expense" as const,
    date: "2026-09-01T00:00:00Z",
    category: "Продукты",
    description: "Пятёрочка",
  };

  it("поля заполнены значениями операции", () => {
    render(<TransactionForm open onOpenChange={() => {}} transaction={existing} />);
    expect(screen.getByLabelText(/сумма/i)).toHaveValue(1500);
  });

  it("🔴 правка НЕ шлёт household_id — владение записи не меняется", async () => {
    /* Симметрично бюджетам (v9.2.0): переезд записи между личным и общим —
       операция, которой продукт не делает. Отправить поле при правке значило бы
       предложить бэкенду сменить владение, чего он не поддерживает. */
    updateMutateAsync.mockResolvedValue({ id: 42 });
    render(<TransactionForm open onOpenChange={() => {}} transaction={existing} />);

    await userEvent.click(screen.getByRole("button", { name: /сохранить/i }));

    await waitFor(() => expect(updateMutateAsync).toHaveBeenCalled());
    const args = updateMutateAsync.mock.calls[0][0];
    expect(args.id).toBe(42);
    expect(args.body).not.toHaveProperty("household_id");
  });
});

describe("TransactionForm — направление операции", () => {
  it("🔴 доход и расход различаются полем `type`, а не знаком суммы", async () => {
    /* Расход с положительной суммой и `type: "expense"` — валидная запись, и модель
       считает по `type`. Выводить направление из знака значило бы завести второй,
       неявный источник истины: 1200 в поле стало бы то доходом, то расходом
       в зависимости от того, поставил ли человек минус. */
    createMutateAsync.mockResolvedValue({ id: 1 });
    const user = userEvent.setup();
    render(<TransactionForm open onOpenChange={() => {}} />);

    await user.type(screen.getByLabelText(/сумма/i), "5000");
    /* Тип — радиогруппа, а не выпадающий список: два варианта, оба должны быть
       видны сразу. Выбор мышью, как у человека. */
    await user.click(screen.getByLabelText("Доход"));
    await user.click(screen.getByRole("button", { name: /сохранить|добавить/i }));

    await waitFor(() => expect(createMutateAsync).toHaveBeenCalled());
    const body = createMutateAsync.mock.calls[0][0];
    expect(body.type).toBe("income");
    expect(body.amount).toBe(5000);
  });

  it("категория и описание доезжают обрезанными", async () => {
    /* Пробелы по краям превращают «Продукты» и «Продукты » в две разные категории
       в отчётах, и человек увидит их отдельными строками, не понимая почему. */
    createMutateAsync.mockResolvedValue({ id: 1 });
    const user = userEvent.setup();
    render(<TransactionForm open onOpenChange={() => {}} />);

    await user.type(screen.getByLabelText(/сумма/i), "300");
    await user.type(screen.getByLabelText(/категор/i), "  Продукты  ");
    await user.click(screen.getByRole("button", { name: /сохранить|добавить/i }));

    await waitFor(() => expect(createMutateAsync).toHaveBeenCalled());
    expect(createMutateAsync.mock.calls[0][0].category).toBe("Продукты");
  });
});
