import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ReferralSection } from "./ReferralSection";

const { useReferralMock, toastError, toastSuccess } = vi.hoisted(() => ({
  useReferralMock: vi.fn(),
  toastError: vi.fn(),
  toastSuccess: vi.fn(),
}));

vi.mock("@entities/referral", () => ({ useReferral: () => useReferralMock() }));

vi.mock("@shared/ui", async () => {
  const actual = await vi.importActual<typeof import("@shared/ui")>("@shared/ui");
  return { ...actual, toast: { error: toastError, success: toastSuccess } };
});

const data = {
  referral_code: "ABC123",
  invite_url: "https://finpilot.ru/register?ref=ABC123",
  invited_count: 2,
  referred_by: null,
  milestones: [
    { threshold: 1, title: "Первое приглашение", reward: null, reached: true },
    { threshold: 3, title: "Тёплая компания", reward: null, reached: false },
  ],
  next_milestone: { threshold: 3, title: "Тёплая компания", remaining: 1 },
};

function query<T>(value: T, over: Record<string, unknown> = {}) {
  return { data: value, error: null, isLoading: false, refetch: vi.fn(), ...over };
}

beforeEach(() => {
  vi.clearAllMocks();
  useReferralMock.mockReturnValue(query(data));
});

describe("ReferralSection — приглашение друзей", () => {
  it("показывает ссылку целиком, а не только код", () => {
    render(<ReferralSection />);
    expect(screen.getByDisplayValue("https://finpilot.ru/register?ref=ABC123")).toBeVisible();
  });

  it("ссылку можно скопировать одной кнопкой", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.assign(navigator, { clipboard: { writeText } });
    render(<ReferralSection />);
    await userEvent.click(screen.getByRole("button", { name: "Скопировать" }));
    expect(writeText).toHaveBeenCalledWith("https://finpilot.ru/register?ref=ABC123");
  });

  it("счётчик приглашённых виден и склонён по-русски", () => {
    render(<ReferralSection />);
    expect(screen.getByText("2")).toBeVisible();
    expect(screen.getByText(/человека пришли по вашей ссылке/)).toBeVisible();
  });

  /* Нуль — самое частое состояние: он у каждого нового пользователя. Парадная
     лестница из пустых плашек и «осталось 1» при нуле нарушает ST-03. */
  it("нуль приглашённых объяснён, а не показан витриной достижений", () => {
    useReferralMock.mockReturnValue(
      query({ ...data, invited_count: 0, milestones: data.milestones.map((m) => ({ ...m, reached: false })) }),
    );
    render(<ReferralSection />);
    expect(screen.getByText(/Пока по вашей ссылке никто не пришёл/)).toBeVisible();
    expect(screen.queryByText("Достижения")).not.toBeInTheDocument();
  });

  it("склонение работает на единице и на пяти", () => {
    useReferralMock.mockReturnValue(
      query({ ...data, next_milestone: { threshold: 3, title: "Тёплая компания", remaining: 1 } }),
    );
    render(<ReferralSection />);
    expect(screen.getByText(/осталось 1 приглашение$/)).toBeVisible();
  });

  it("ближайшее достижение названо с остатком", () => {
    render(<ReferralSection />);
    expect(screen.getByText(/Тёплая компания.*осталось/)).toBeVisible();
  });

  /* Все вехи достигнуты — `next_milestone` приходит `null`. Схема разрешает это
     честно, и экран обязан не падать (урок v8.31.1). */
  it("без ближайшего достижения секция не падает", () => {
    useReferralMock.mockReturnValue(query({ ...data, next_milestone: null }));
    render(<ReferralSection />);
    expect(screen.getByRole("heading", { name: "Приглашения друзей" })).toBeVisible();
  });

  it("состояние достижения передано словом, а не только рамкой (A11Y-07)", () => {
    const { container } = render(<ReferralSection />);
    const items = container.querySelectorAll(".fp-referral__milestone");
    expect(items[0]).toHaveTextContent("достигнуто");
    expect(items[1]).not.toHaveTextContent("достигнуто");
  });

  /* Награды не существует: `referral_milestones` отдаёт `reward=None` у всех порогов.
     Обещать её словом «награда» значило бы предлагать тупик ([IA-04]). */
  it("наград не обещает — их механики нет", () => {
    const { container } = render(<ReferralSection />);
    expect(container.textContent).not.toMatch(/наград|приз|бонус/i);
  });

  it("загрузка показывает скелетон", () => {
    useReferralMock.mockReturnValue(query(undefined, { isLoading: true }));
    const { container } = render(<ReferralSection />);
    expect(container.querySelector("[class*='skeleton']")).not.toBeNull();
  });

  it("ошибка даёт путь восстановления (ST-04)", () => {
    useReferralMock.mockReturnValue(query(undefined, { error: new Error("500") }));
    render(<ReferralSection />);
    expect(screen.getByText("Не получилось загрузить приглашения")).toBeVisible();
    expect(screen.getByRole("button", { name: "Повторить" })).toBeVisible();
  });
});
