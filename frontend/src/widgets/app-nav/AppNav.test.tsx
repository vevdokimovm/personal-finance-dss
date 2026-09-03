import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { AppNav } from "./AppNav";
import { APP_NAV_ITEMS } from "./navItems";

/* Мок Link отдаёт activeProps атрибутом, чтобы проверить именно то, что компонент
   ПЕРЕДАЁТ роутеру (aria-current на активном пункте), не подменяя собой сам роутер:
   вычисление «какой пункт активен» — работа TanStack Router, её тут не тестируем. */
vi.mock("@tanstack/react-router", () => ({
  Link: ({
    to,
    children,
    activeProps,
    className,
  }: {
    to: string;
    children: React.ReactNode;
    activeProps?: Record<string, string>;
    className?: string;
  }) => (
    <a href={to} className={className} data-active-current={activeProps?.["aria-current"]}>
      {children}
    </a>
  ),
}));

const useProfileMock = vi.fn();
vi.mock("@entities/profile", () => ({
  useProfile: () => useProfileMock(),
}));

const authorized = { data: { email: "anna@example.com" }, isLoading: false, error: null };

describe("AppNav — постоянный навигационный каркас (IA-02)", () => {
  it("залогинен: есть landmark <nav> с доступным именем", () => {
    useProfileMock.mockReturnValue(authorized);
    render(<AppNav />);
    expect(screen.getByRole("navigation", { name: "Основные разделы" })).toBeInTheDocument();
  });

  it.each(APP_NAV_ITEMS)(
    "залогинен: раздел «$label» достижим ссылкой на $to",
    ({ to, label }) => {
      useProfileMock.mockReturnValue(authorized);
      render(<AppNav />);
      expect(screen.getByRole("link", { name: label })).toHaveAttribute("href", to);
    },
  );

  it("залогинен: покрыты ВСЕ семь экранов продукта — недостижимого кликом раздела не осталось", () => {
    useProfileMock.mockReturnValue(authorized);
    render(<AppNav />);
    const hrefs = screen
      .getAllByRole("link")
      .map((a) => a.getAttribute("href"))
      .sort();
    expect(hrefs).toEqual(
      ["/", "/planning", "/transactions", "/obligations", "/goals", "/banks", "/profile"].sort(),
    );
  });

  it("активный раздел помечается aria-current, не только цветом (IA-02, A11Y-07)", () => {
    useProfileMock.mockReturnValue(authorized);
    render(<AppNav />);
    for (const link of screen.getAllByRole("link")) {
      expect(link).toHaveAttribute("data-active-current", "page");
    }
  });

  it("гость (401): навигации нет — семь ссылок в гейт-403 были бы тупиками (IA-04)", () => {
    useProfileMock.mockReturnValue({ data: undefined, isLoading: false, error: new Error("401") });
    const { container } = render(<AppNav />);
    expect(container.textContent).toBe("");
  });

  it("во время загрузки профиля навигация не мигает", () => {
    useProfileMock.mockReturnValue({ data: undefined, isLoading: true, error: null });
    const { container } = render(<AppNav />);
    expect(container.textContent).toBe("");
  });

  it("stale-if-error: старые data в кэше при упавшем рефетче — навигации нет (тот же класс, что баг топбара)", () => {
    useProfileMock.mockReturnValue({
      data: { email: "anna@example.com" },
      isLoading: false,
      error: new Error("401"),
    });
    const { container } = render(<AppNav />);
    expect(container.textContent).toBe("");
  });

  it("подписи разделов дословно совпадают с h1 своих экранов (CMP-03)", () => {
    // Разнобой «Обязательства» в меню vs «Кредиты и обязательства» в заголовке — ровно то,
    // что стандарт запрещает: одно понятие обязано называться одним словом везде.
    expect(APP_NAV_ITEMS.map((i) => i.label)).toEqual([
      "Финансовый обзор",
      "План распределения",
      "Операции",
      "Кредиты и обязательства",
      "Цели",
      "Ликвидные активы",
      "Профиль",
    ]);
  });
});
