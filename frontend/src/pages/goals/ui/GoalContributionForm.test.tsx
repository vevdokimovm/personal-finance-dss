import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { GoalContributionForm } from "./GoalContributionForm";

/**
 * «Внести прогресс» — операция, ПРИБАВЛЯЮЩАЯ к накопленному, а не перезаписывающая его.
 *
 * 🔴 **Отдельная форма заведена ради этого различия.** Общая правка цели меняет поля;
 * взнос добавляет сумму. Спутать их значит стереть накопленное за год одним взносом,
 * и человек не отменит это из интерфейса.
 *
 * Форма из одного поля, и ошибка показывается **у поля**, а не баннером: в такой форме
 * баннер читается как сбой продукта, а не как «вы не заполнили» (design-critic).
 */

const mutateAsync = vi.fn();
let mutationError: unknown = null;

vi.mock("@entities/goals", async () => {
  const actual = await vi.importActual<typeof import("@entities/goals")>("@entities/goals");
  return {
    ...actual,
    useAddGoalContribution: () => ({
      mutateAsync,
      isPending: false,
      error: mutationError,
    }),
  };
});

const toastSuccess = vi.fn();
vi.mock("@shared/ui", async () => {
  const actual = await vi.importActual<typeof import("@shared/ui")>("@shared/ui");
  return { ...actual, toast: { ...actual.toast, success: (m: string) => toastSuccess(m) } };
});

const goal = {
  id: 4,
  name: "Отпуск",
  target_amount: 200000,
  current_amount: 300000,
  deadline: null,
  category: "travel" as const,
  linked_asset_id: null,
  comment: null,
};

beforeEach(() => {
  vi.clearAllMocks();
  mutationError = null;
});

describe("GoalContributionForm", () => {
  it("🔴 шлёт ТОЛЬКО сумму — накопленное считает сервер", async () => {
    /* Если бы форма отправляла новое `current_amount`, она обязана была бы знать
       текущее — и рассинхронизировалась бы с сервером при любом параллельном взносе.
       Сложение на сервере это исключает. */
    mutateAsync.mockResolvedValue({ id: 4 });
    const user = userEvent.setup();
    render(<GoalContributionForm open onOpenChange={() => {}} goal={goal} />);

    await user.type(screen.getByLabelText(/сумма/i), "5000");
    await user.click(screen.getByRole("button", { name: /внести|сохран/i }));

    await waitFor(() => expect(mutateAsync).toHaveBeenCalled());
    expect(mutateAsync).toHaveBeenCalledWith({ id: 4, body: { amount: 5000 } });
  });

  it("нулевая сумма не отправляется, ошибка стоит у поля", async () => {
    const user = userEvent.setup();
    render(<GoalContributionForm open onOpenChange={() => {}} goal={goal} />);

    await user.type(screen.getByLabelText(/сумма/i), "0");
    await user.click(screen.getByRole("button", { name: /внести|сохран/i }));

    expect(mutateAsync).not.toHaveBeenCalled();
    await waitFor(() => expect(screen.getByLabelText(/сумма/i)).toHaveFocus());
  });

  it("успех закрывает модалку и очищает поле", async () => {
    /* Сумма, оставшаяся в поле, при следующем открытии предложит внести её повторно —
       и человек согласится, не глядя. */
    mutateAsync.mockResolvedValue({ id: 4 });
    const onOpenChange = vi.fn();
    const user = userEvent.setup();
    render(<GoalContributionForm open onOpenChange={onOpenChange} goal={goal} />);

    await user.type(screen.getByLabelText(/сумма/i), "5000");
    await user.click(screen.getByRole("button", { name: /внести|сохран/i }));

    await waitFor(() => expect(onOpenChange).toHaveBeenCalledWith(false));
    expect(toastSuccess).toHaveBeenCalled();
  });

  it("🔴 409 у цели, связанной с активом, не закрывает модалку", async () => {
    /* Связанная цель пополняется через свой актив — бэкенд отвечает 409. Закрыть
       форму значило бы спрятать объяснение: человек попробует ещё раз тем же путём. */
    mutateAsync.mockRejectedValue({ detail: "Цель связана с активом.", status: 409 });
    mutationError = { detail: "Цель связана с активом.", status: 409 };
    const onOpenChange = vi.fn();
    const user = userEvent.setup();
    render(<GoalContributionForm open onOpenChange={onOpenChange} goal={goal} />);

    await user.type(screen.getByLabelText(/сумма/i), "5000");
    await user.click(screen.getByRole("button", { name: /внести|сохран/i }));

    await waitFor(() => expect(mutateAsync).toHaveBeenCalled());
    expect(onOpenChange).not.toHaveBeenCalledWith(false);
    expect(screen.getByRole("alert")).toHaveTextContent(/актив/i);
  });

  it("отмена закрывает форму, ничего не отправив", async () => {
    const onOpenChange = vi.fn();
    render(<GoalContributionForm open onOpenChange={onOpenChange} goal={goal} />);

    await userEvent.click(screen.getByRole("button", { name: /отмена/i }));

    expect(mutateAsync).not.toHaveBeenCalled();
    expect(onOpenChange).toHaveBeenCalledWith(false);
  });
});
