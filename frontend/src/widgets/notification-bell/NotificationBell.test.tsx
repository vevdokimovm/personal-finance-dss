import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { NotificationBell } from "./NotificationBell";

const useUnreadCountMock = vi.fn();
const useNotificationsFeedMock = vi.fn();
const markReadMock = vi.fn();
const markAllReadMock = vi.fn();

vi.mock("@tanstack/react-router", () => ({ useNavigate: () => navigateMock }));

const navigateMock = vi.fn();

const useProfileMock = vi.fn();
vi.mock("@entities/profile", () => ({ useProfile: () => useProfileMock() }));

vi.mock("@entities/notifications", () => ({
  useUnreadCount: () => useUnreadCountMock(),
  useNotificationsFeed: () => useNotificationsFeedMock(),
  useMarkRead: () => ({ mutate: markReadMock, isPending: false }),
  useMarkAllRead: () => ({ mutate: markAllReadMock, isPending: false }),
}));

const item = (over: Partial<Record<string, unknown>> = {}) => ({
  id: 1,
  type: "budget_overrun",
  title: "Превышен бюджет «Продукты»",
  body: "Сводка за август: доход 180 000 ₽, расход 78 000 ₽",
  link: null,
  is_read: false,
  created_at: "2026-09-01T10:00:00",
  ...over,
});

beforeEach(() => {
  useProfileMock.mockReturnValue({
    data: { email: "anna@example.com" },
    error: null,
    isLoading: false,
  });
  useUnreadCountMock.mockReturnValue({ data: 0, error: null, isLoading: false });
  useNotificationsFeedMock.mockReturnValue({
    data: undefined,
    error: null,
    isLoading: false,
    refetch: vi.fn(),
  });
  markReadMock.mockClear();
  navigateMock.mockClear();
  markAllReadMock.mockClear();
});

describe("NotificationBell — колокольчик в топбаре", () => {
  it("есть кнопка с доступным именем", () => {
    render(<NotificationBell />);
    expect(screen.getByRole("button", { name: /Уведомления/ })).toBeInTheDocument();
  });

  it("непрочитанные показываются числом, а не только точкой (A11Y-07)", () => {
    useUnreadCountMock.mockReturnValue({ data: 3, error: null, isLoading: false });
    render(<NotificationBell />);
    expect(screen.getByRole("button", { name: "Уведомления, непрочитанных: 3" })).toBeVisible();
    expect(screen.getByText("3")).toBeVisible();
  });

  it("ноль непрочитанных — бейдж не рисуется, имя без числа", () => {
    render(<NotificationBell />);
    expect(screen.getByRole("button", { name: "Уведомления" })).toBeInTheDocument();
  });

  /* 🔴 Главное поведение батча. `_FIN` на роутере уведомлений (v8.32.0) означает 403
     при отозванном согласии. Колокольчик стоит в топбаре НА КАЖДОМ экране — показать
     здесь панель согласия было бы хуже молчания: она повторялась бы поверх всего
     продукта. Путь к согласию есть и он достижим кликом с v8.31.0 — «Профиль»
     в навигационном каркасе. Поэтому при отказе колокольчик исчезает целиком. */
  it("согласие не выдано (403) — колокольчика нет вовсе, а не панель согласия в топбаре", () => {
    useUnreadCountMock.mockReturnValue({
      data: undefined,
      error: { detail: { code: "consent_required", consent_type: "financial_data" } },
      isLoading: false,
    });
    const { container } = render(<NotificationBell />);
    expect(container.textContent).toBe("");
  });

  it("во время загрузки счётчика место зарезервировано, а не схлопнуто", () => {
    useUnreadCountMock.mockReturnValue({ data: undefined, error: null, isLoading: true });
    const { container } = render(<NotificationBell />);
    // Ни кнопки, ни текста — но место занято, иначе соседние контролы топбара
    // прыгали бы на каждом холодном старте.
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
    expect(container.querySelector(".fp-bell__placeholder")).not.toBeNull();
  });

  it("авария бэкенда (500) НЕ прячет колокольчик — иначе функция исчезает без пути назад", () => {
    useUnreadCountMock.mockReturnValue({
      data: undefined,
      error: { detail: "internal error" },
      isLoading: false,
    });
    render(<NotificationBell />);
    expect(screen.getByRole("button", { name: /Уведомления/ })).toBeInTheDocument();
  });

  it("клик по уведомлению со ссылкой ведёт на связанный экран (IA-04)", async () => {
    useNotificationsFeedMock.mockReturnValue({
      data: { items: [item({ link: "/goals" })], unread_count: 1 },
      error: null,
      isLoading: false,
      refetch: vi.fn(),
    });
    render(<NotificationBell />);
    await userEvent.click(screen.getByRole("button", { name: /Уведомления/ }));
    await userEvent.click(screen.getByRole("button", { name: /Превышен бюджет/ }));
    expect(navigateMock).toHaveBeenCalledWith({ to: "/goals" });
  });

  it("непрочитанное помечено СЛОВОМ, а не только цветом (A11Y-07)", async () => {
    useNotificationsFeedMock.mockReturnValue({
      data: { items: [item()], unread_count: 1 },
      error: null,
      isLoading: false,
      refetch: vi.fn(),
    });
    render(<NotificationBell />);
    await userEvent.click(screen.getByRole("button", { name: /Уведомления/ }));
    expect(screen.getByText("новое")).toBeVisible();
  });

  it("иконка — не эмодзи (бриф запрещает их в продукте)", () => {
    const { container } = render(<NotificationBell />);
    expect(container.querySelector("svg.fp-bell__icon")).not.toBeNull();
    expect(container.textContent).not.toMatch(/[\u{1F300}-\u{1FAFF}]/u);
  });

  it("клик открывает панель и показывает уведомления", async () => {
    useUnreadCountMock.mockReturnValue({ data: 1, error: null, isLoading: false });
    useNotificationsFeedMock.mockReturnValue({
      data: { items: [item()], unread_count: 1 },
      error: null,
      isLoading: false,
      refetch: vi.fn(),
    });
    render(<NotificationBell />);
    await userEvent.click(screen.getByRole("button", { name: /Уведомления/ }));
    expect(screen.getByText("Превышен бюджет «Продукты»")).toBeVisible();
  });

  it("пустая лента объясняет себя текстом, а не остаётся пустотой (ST-03)", async () => {
    useNotificationsFeedMock.mockReturnValue({
      data: { items: [], unread_count: 0 },
      error: null,
      isLoading: false,
      refetch: vi.fn(),
    });
    render(<NotificationBell />);
    await userEvent.click(screen.getByRole("button", { name: /Уведомления/ }));
    expect(screen.getByText("Пока нет уведомлений")).toBeVisible();
  });

  it("ошибка ленты не остаётся молчанием (ST-04)", async () => {
    useNotificationsFeedMock.mockReturnValue({
      data: undefined,
      error: new Error("500"),
      isLoading: false,
      refetch: vi.fn(),
    });
    render(<NotificationBell />);
    await userEvent.click(screen.getByRole("button", { name: /Уведомления/ }));
    expect(screen.getByText("Не получилось загрузить уведомления")).toBeVisible();
    expect(screen.getByRole("button", { name: "Повторить" })).toBeVisible();
  });

  it("«Прочитать все» видно только когда есть непрочитанные", async () => {
    useNotificationsFeedMock.mockReturnValue({
      data: { items: [item({ is_read: true })], unread_count: 0 },
      error: null,
      isLoading: false,
      refetch: vi.fn(),
    });
    render(<NotificationBell />);
    await userEvent.click(screen.getByRole("button", { name: /Уведомления/ }));
    expect(screen.queryByRole("button", { name: "Прочитать все" })).not.toBeInTheDocument();
  });

  it("клик по непрочитанному отмечает его прочитанным", async () => {
    useUnreadCountMock.mockReturnValue({ data: 1, error: null, isLoading: false });
    useNotificationsFeedMock.mockReturnValue({
      data: { items: [item()], unread_count: 1 },
      error: null,
      isLoading: false,
      refetch: vi.fn(),
    });
    render(<NotificationBell />);
    await userEvent.click(screen.getByRole("button", { name: /Уведомления/ }));
    await userEvent.click(screen.getByRole("button", { name: /Превышен бюджет/ }));
    expect(markReadMock.mock.calls[0][0]).toBe(1);
  });

  it("прочитанное не переотмечается — лишний запрос на каждый клик не нужен", async () => {
    useNotificationsFeedMock.mockReturnValue({
      data: { items: [item({ is_read: true })], unread_count: 0 },
      error: null,
      isLoading: false,
      refetch: vi.fn(),
    });
    render(<NotificationBell />);
    await userEvent.click(screen.getByRole("button", { name: /Уведомления/ }));
    await userEvent.click(screen.getByRole("button", { name: /Превышен бюджет/ }));
    expect(markReadMock).not.toHaveBeenCalled();
  });
});

describe("NotificationBell — гость", () => {
  it("неавторизованному колокольчик не показывается", () => {
    useProfileMock.mockReturnValue({ data: undefined, error: new Error("401"), isLoading: false });
    const { container } = render(<NotificationBell />);
    expect(container.textContent).toBe("");
  });

  it("stale-if-error: старые data профиля при упавшем рефетче — колокольчика нет", () => {
    // Тот же класс, что баг топбара: TanStack Query держит последние успешные data,
    // когда рефетч упал на 401, поэтому `data` в одиночку проверять нельзя.
    useProfileMock.mockReturnValue({
      data: { email: "anna@example.com" },
      error: new Error("401"),
      isLoading: false,
    });
    const { container } = render(<NotificationBell />);
    expect(container.textContent).toBe("");
  });
});
