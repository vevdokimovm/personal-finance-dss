import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { SharedBadge } from "./SharedBadge";

const { householdsMock } = vi.hoisted(() => ({ householdsMock: vi.fn() }));

vi.mock("@entities/households", async () => {
  const actual =
    await vi.importActual<typeof import("@entities/households")>("@entities/households");
  return { ...actual, useHouseholds: () => householdsMock() };
});

beforeEach(() => {
  vi.clearAllMocks();
  householdsMock.mockReturnValue({
    data: [{ id: 7, name: "Семья", role: "owner" }],
    isLoading: false,
    isError: false,
  });
});

/**
 * 🔴 Вторая половина находки design-critic: выбор «поделиться» сделан, а состояние
 * записи после сохранения нигде не читается. Поле `household_id` доезжает до ответов
 * всех пяти сущностей и не показывается ни в одном списке — то есть человек выбрал
 * семью и проверить это может только сравнив списки с родственником.
 *
 * Тот же класс дефекта, который этот батч и чинил: право реализовано, в интерфейсе
 * не видно ([FB-03], [ST-01]).
 */
describe("SharedBadge — общая запись видна как общая", () => {
  it("личная запись не помечается ничем", () => {
    const { container } = render(<SharedBadge householdId={null} />);
    expect(container.textContent).toBe("");
  });

  it("общая запись названа словом, а не только цветом", () => {
    /* 🔴 [A11Y-07]/WCAG 1.4.1: цветной кружок без подписи не сообщает ничего тому,
       кто его не различает, — а речь о том, видят ли запись посторонние люди. */
    render(<SharedBadge householdId={7} />);
    expect(screen.getByText(/общая/i)).toBeInTheDocument();
  });

  it("называет, С КЕМ именно запись общая", () => {
    /* У человека может быть несколько семей: «общая» без имени не отвечает
       на вопрос, кто эту строку видит. */
    render(<SharedBadge householdId={7} />);
    expect(screen.getByText(/Семья/)).toBeInTheDocument();
  });

  it("неизвестный household всё равно помечен общим", () => {
    /* Список семей мог не загрузиться или человека уже исключили из семьи.
       Промолчать здесь — показать общую запись как личную, то есть соврать
       про доступ к деньгам. Имя опускаем, факт — нет. */
    householdsMock.mockReturnValue({ data: [], isLoading: false, isError: true });
    render(<SharedBadge householdId={7} />);
    expect(screen.getByText(/общая/i)).toBeInTheDocument();
  });
});
