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

  it.each(APP_NAV_ITEMS)("залогинен: раздел «$label» достижим ссылкой на $to", ({ to, label }) => {
    useProfileMock.mockReturnValue(authorized);
    render(<AppNav />);
    expect(screen.getByRole("link", { name: label })).toHaveAttribute("href", to);
  });

  it("залогинен: покрыты ВСЕ экраны продукта — недостижимого кликом раздела не осталось", () => {
    useProfileMock.mockReturnValue(authorized);
    render(<AppNav />);
    const hrefs = screen
      .getAllByRole("link")
      .map((a) => a.getAttribute("href"))
      .sort();
    expect(hrefs).toEqual(
      [
        "/",
        "/planning",
        "/transactions",
        "/spending",
        "/obligations",
        "/goals",
        "/banks",
        "/household",
        "/profile",
      ].sort(),
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
      // Форма ошибки та же, что бросает `useProfile` на 401 (`NotAuthenticatedError`),
      // а не произвольный Error с текстом «401»: текст сообщения ничего не значит
      // для кода, и тест на нём проверял бы совпадение строк, а не поведение.
      error: Object.assign(new Error("401"), { name: "NotAuthenticatedError" }),
    });
    const { container } = render(<AppNav />);
    expect(container.textContent).toBe("");
  });

  /* 🔴 Остаток гипотезы 7. `if (!data || error) return null` убирал меню при ЛЮБОЙ
     ошибке профиля — включая сетевую, когда человек вошёл и данные лежат в кэше
     (TanStack Query держит последние успешные `data` при упавшем рефетче).
     Экран визуально «ломался» без объяснения: разделы исчезали из-за моргнувшей сети. */
  it("сетевая ошибка при живой сессии НЕ убирает навигацию", () => {
    useProfileMock.mockReturnValue({
      data: { email: "anna@example.com", is_owner: false },
      error: new TypeError("Failed to fetch"),
      isLoading: false,
    });
    render(<AppNav />);
    expect(screen.getByRole("navigation")).toBeInTheDocument();
  });

  it("401 убирает навигацию — человек больше не вошёл", () => {
    /* Обратная сторона: при истёкшей сессии разделы за гейтом отдадут 401/403,
       и семь ссылок превратятся в семь тупиков ([IA-04]). Объяснение даёт
       `SessionExpiredPanel` на самом экране, а не меню. */
    useProfileMock.mockReturnValue({
      data: { email: "anna@example.com", is_owner: false },
      error: { status: 401 },
      isLoading: false,
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
      "Советы по расходам",
      "Кредиты и обязательства",
      "Цели",
      "Ликвидные активы",
      "Семейный доступ",
      "Профиль",
    ]);
  });
});
