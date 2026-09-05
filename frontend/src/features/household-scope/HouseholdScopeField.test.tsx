import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { HouseholdScopeField } from "./HouseholdScopeField";

const { householdsMock } = vi.hoisted(() => ({ householdsMock: vi.fn() }));

vi.mock("@entities/households", async () => {
  const actual =
    await vi.importActual<typeof import("@entities/households")>("@entities/households");
  return { ...actual, useHouseholds: () => householdsMock() };
});

function listQuery(data: unknown, overrides: Record<string, unknown> = {}) {
  return { data, isLoading: false, isError: false, error: null, ...overrides };
}

beforeEach(() => {
  vi.clearAllMocks();
  householdsMock.mockReturnValue(listQuery([{ id: 7, name: "Семья", role: "owner" }]));
});

/**
 * 🔴 Пункт №5 аудита `independent-expert` 05.09.2026: «Семейный доступ» существует
 * и не делает общим ничего. `household_id` заведён в схемах и колонках пяти сущностей,
 * а формы про него не знают вовсе — то есть право поделиться реализовано и недостижимо.
 * Тот же класс, что SEV1 `CONSENT-GATE-NO-UI`.
 *
 * Контрол один на все пять форм: пять копий разошлись бы при первой правке, а разнобой
 * в том, как продукт спрашивает «чьё это», человек читает как разные функции.
 */
describe("HouseholdScopeField — выбор владельца записи", () => {
  it("по умолчанию запись личная", () => {
    /* 🔴 Умолчание НЕ семейное, даже когда household ровно один: подставить его
       значило бы раздать родственникам данные, которых человек им не показывал. */
    const onChange = vi.fn();
    render(<HouseholdScopeField value={null} onChange={onChange} idPrefix="asset" />);

    const select = screen.getByLabelText(/кому принадлеж|чья запись|доступ/i);
    expect(select).toHaveValue("");
  });

  it("предлагает household-ы, куда человек может писать", () => {
    render(<HouseholdScopeField value={null} onChange={vi.fn()} idPrefix="asset" />);
    expect(screen.getByRole("option", { name: /Семья/ })).toBeInTheDocument();
  });

  it("выбор отдаёт числовой id, а не строку из DOM", async () => {
    /* `<select>` всегда отдаёт строку; отправить "7" вместо 7 значит получить 422
       от Pydantic — ошибка, которую видно только на живом запросе. */
    const onChange = vi.fn();
    render(<HouseholdScopeField value={null} onChange={onChange} idPrefix="asset" />);

    await userEvent.selectOptions(screen.getByLabelText(/кому принадлеж|чья запись|доступ/i), "7");
    expect(onChange).toHaveBeenCalledWith(7);
  });

  it("возврат к личной записи отдаёт null, а не ноль и не пустую строку", async () => {
    const onChange = vi.fn();
    render(<HouseholdScopeField value={7} onChange={onChange} idPrefix="asset" />);

    await userEvent.selectOptions(screen.getByLabelText(/кому принадлеж|чья запись|доступ/i), "");
    expect(onChange).toHaveBeenCalledWith(null);
  });

  it("объясняет, что значит общая запись", () => {
    render(<HouseholdScopeField value={null} onChange={vi.fn()} idPrefix="asset" />);
    // Человек должен понимать последствие ДО выбора: общая запись видна другим людям.
    expect(screen.getByText(/увидят|видна|участник/i)).toBeInTheDocument();
  });
});

describe("HouseholdScopeField — когда делиться не с кем", () => {
  it("нет household-ов — контрола нет вовсе", () => {
    /* Пустой выпадающий список — тупик [IA-04]: человек видит вопрос, на который
       не может ответить. Пока семьи нет, поля быть не должно. */
    householdsMock.mockReturnValue(listQuery([]));
    const { container } = render(
      <HouseholdScopeField value={null} onChange={vi.fn()} idPrefix="asset" />,
    );
    expect(container.textContent).toBe("");
  });

  it("список ещё грузится — контрола нет, а не пустой выбор", () => {
    householdsMock.mockReturnValue(listQuery(undefined, { isLoading: true }));
    const { container } = render(
      <HouseholdScopeField value={null} onChange={vi.fn()} idPrefix="asset" />,
    );
    expect(container.textContent).toBe("");
  });

  it("список не загрузился — форма не ломается из-за необязательного поля", () => {
    /* 🔴 Семейный доступ — дополнение к записи, а не её условие. Отказ его загрузить
       не должен мешать человеку сохранить свою операцию. */
    householdsMock.mockReturnValue(listQuery(undefined, { isError: true }));
    const { container } = render(
      <HouseholdScopeField value={null} onChange={vi.fn()} idPrefix="asset" />,
    );
    expect(container.textContent).toBe("");
  });
});

describe("HouseholdScopeField — права внутри семьи", () => {
  it("household, где человек только смотрит, в списке не предлагается", () => {
    /* `can_write_household` пропускает owner и member, но не viewer. Показать viewer'у
       такой вариант — предложить действие, которое сервер гарантированно отвергнет
       (403), то есть тупик [IA-04]. */
    householdsMock.mockReturnValue(
      listQuery([
        { id: 7, name: "Семья", role: "viewer" },
        { id: 8, name: "Родители", role: "member" },
      ]),
    );
    render(<HouseholdScopeField value={null} onChange={vi.fn()} idPrefix="asset" />);

    expect(screen.queryByRole("option", { name: /Семья/ })).not.toBeInTheDocument();
    expect(screen.getByRole("option", { name: /Родители/ })).toBeInTheDocument();
  });
});
