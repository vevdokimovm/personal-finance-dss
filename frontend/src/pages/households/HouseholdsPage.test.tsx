import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { HouseholdsPage } from "./HouseholdsPage";

const {
  useHouseholdsMock,
  useMembersMock,
  useInvitesMock,
  useProfileMock,
  createMock,
  inviteMock,
  revokeMock,
  removeMock,
  leaveMock,
  disbandMock,
  toastError,
  toastSuccess,
} = vi.hoisted(() => ({
  useHouseholdsMock: vi.fn(),
  useMembersMock: vi.fn(),
  useInvitesMock: vi.fn(),
  useProfileMock: vi.fn(),
  createMock: vi.fn(),
  inviteMock: vi.fn(),
  revokeMock: vi.fn(),
  removeMock: vi.fn(),
  leaveMock: vi.fn(),
  disbandMock: vi.fn(),
  toastError: vi.fn(),
  toastSuccess: vi.fn(),
}));

vi.mock("@entities/households", () => ({
  useHouseholds: () => useHouseholdsMock(),
  useHouseholdMembers: () => useMembersMock(),
  useHouseholdInvites: () => useInvitesMock(),
  useCreateHousehold: () => ({ mutate: createMock, isPending: false }),
  useCreateInvite: () => ({ mutate: inviteMock, isPending: false }),
  useRevokeInvite: () => ({ mutate: revokeMock, isPending: false }),
  useRemoveMember: () => ({ mutate: removeMock, isPending: false }),
  useLeaveHousehold: () => ({ mutate: leaveMock, isPending: false }),
  useDisbandHousehold: () => ({ mutate: disbandMock, isPending: false }),
}));

vi.mock("@entities/profile", () => ({
  useProfile: () => useProfileMock(),
}));

vi.mock("@shared/ui", async () => {
  const actual = await vi.importActual<typeof import("@shared/ui")>("@shared/ui");
  return { ...actual, toast: { error: toastError, success: toastSuccess } };
});

const owned = {
  id: 1,
  name: "Семья Петровых",
  owner_id: "u1",
  role: "owner",
  member_count: 2,
  created_at: "2026-09-01T10:00:00",
};
const joined = { ...owned, id: 2, name: "Дача", owner_id: "u9", role: "member", member_count: 3 };

const members = [
  { user_id: "u1", email: "anna@example.com", role: "owner", joined_at: "2026-09-01T10:00:00" },
  { user_id: "u2", email: "boris@example.com", role: "member", joined_at: "2026-09-02T10:00:00" },
];

function query<T>(data: T, over: Record<string, unknown> = {}) {
  return { data, error: null, isLoading: false, refetch: vi.fn(), ...over };
}

beforeEach(() => {
  vi.clearAllMocks();
  useHouseholdsMock.mockReturnValue(query([owned]));
  useMembersMock.mockReturnValue(query(members));
  useInvitesMock.mockReturnValue(query([]));
  useProfileMock.mockReturnValue(query({ id: "u1", email: "anna@example.com" }));
});

describe("HouseholdsPage — семейный доступ", () => {
  it("заголовок экрана совпадает с пунктом навигации (CMP-03)", () => {
    render(<HouseholdsPage />);
    expect(screen.getByRole("heading", { level: 1, name: "Семейный доступ" })).toBeVisible();
  });

  it("загрузка показывает скелетон", () => {
    useHouseholdsMock.mockReturnValue(query(undefined, { isLoading: true }));
    const { container } = render(<HouseholdsPage />);
    expect(container.querySelector("[class*='skeleton']")).not.toBeNull();
  });

  it("пусто — объясняет, что это даёт, и предлагает создать (ST-03)", () => {
    useHouseholdsMock.mockReturnValue(query([]));
    render(<HouseholdsPage />);
    expect(screen.getByText("Пока нет общего доступа")).toBeVisible();
    expect(screen.getByRole("button", { name: "Создать семейный доступ" })).toBeVisible();
  });

  it("ошибка даёт путь восстановления (ST-04)", () => {
    useHouseholdsMock.mockReturnValue(query(undefined, { error: new Error("500") }));
    render(<HouseholdsPage />);
    expect(screen.getByText("Не получилось загрузить семейный доступ")).toBeVisible();
    expect(screen.getByRole("button", { name: "Повторить" })).toBeVisible();
  });

  it("создание идёт через модалку, как на остальных экранах продукта (CMP-01)", async () => {
    useHouseholdsMock.mockReturnValue(query([]));
    render(<HouseholdsPage />);
    // До нажатия формы на экране нет — единственный primary-CTA не занят
    // инструментом, который нужен одну минуту за всё время жизни аккаунта.
    expect(screen.queryByLabelText("Название")).not.toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Создать семейный доступ" }));
    await userEvent.type(await screen.findByLabelText("Название"), "Семья Петровых");
    await userEvent.click(screen.getByRole("button", { name: "Создать" }));
    expect(createMock.mock.calls[0][0]).toBe("Семья Петровых");
  });

  /* Немой клик читается как «экран сломался», особенно для человека, который в продукте
     впервые ([FB-01], [FRM-04]). Бэкенд ответил бы на пустое имя 422. */
  it("пустое имя не отправляется и объясняет, чего не хватает", async () => {
    useHouseholdsMock.mockReturnValue(query([]));
    render(<HouseholdsPage />);
    await userEvent.click(screen.getByRole("button", { name: "Создать семейный доступ" }));
    await userEvent.click(await screen.findByRole("button", { name: "Создать" }));
    expect(createMock).not.toHaveBeenCalled();
    expect(screen.getByRole("alert")).toHaveTextContent("Введите название");
    expect(screen.getByLabelText("Название")).toHaveAttribute("aria-invalid", "true");
  });

  it("моя роль показана СЛОВОМ и с пояснением для скринридера (A11Y-07)", () => {
    const { container } = render(<HouseholdsPage />);
    const badge = container.querySelector(".fp-household__role");
    // Слово «Владелец» встречается и в строке участника — сверяем именно бейдж
    // моей роли, а не первое совпадение по документу.
    expect(badge).toHaveTextContent("Моя роль:");
    expect(badge).toHaveTextContent("Владелец");
  });

  it("роль переведена, а не показана служебным кодом контракта (CMP-03)", () => {
    useHouseholdsMock.mockReturnValue(query([joined]));
    const { container } = render(<HouseholdsPage />);
    expect(container.querySelector(".fp-household__role")).toHaveTextContent("Участник");
    // `owner`/`member`/`viewer` — значения контракта, пользователю они ничего не говорят.
    expect(container.textContent).not.toMatch(/\bmember\b|\bowner\b|\bviewer\b/);
  });

  it("участники показаны с ролями", () => {
    render(<HouseholdsPage />);
    expect(screen.getByText("boris@example.com")).toBeVisible();
  });

  it("собственная строка помечена — чтобы не промахнуться кнопкой по соседу", () => {
    const { container } = render(<HouseholdsPage />);
    const rows = container.querySelectorAll(".fp-household__member");
    expect(rows[0]).toHaveTextContent("это вы");
    expect(rows[1]).not.toHaveTextContent("это вы");
  });

  /* Владелец не может «покинуть» — бэкенд отвечает 400. Показывать кнопку, которая
     гарантированно откажет, значит предлагать тупик ([IA-04]). */
  it("владельцу предлагается распустить, а не покинуть", () => {
    render(<HouseholdsPage />);
    expect(screen.getByRole("button", { name: /Распустить/ })).toBeVisible();
    expect(screen.queryByRole("button", { name: /Покинуть/ })).not.toBeInTheDocument();
  });

  it("участнику предлагается покинуть, а не распустить", () => {
    useHouseholdsMock.mockReturnValue(query([joined]));
    render(<HouseholdsPage />);
    expect(screen.getByRole("button", { name: /Покинуть/ })).toBeVisible();
    expect(screen.queryByRole("button", { name: /Распустить/ })).not.toBeInTheDocument();
  });

  it("роспуск требует подтверждения — восстановить нечем", async () => {
    render(<HouseholdsPage />);
    await userEvent.click(screen.getByRole("button", { name: /Распустить/ }));
    expect(disbandMock).not.toHaveBeenCalled();
    await userEvent.click(screen.getByRole("button", { name: "Распустить навсегда" }));
    expect(disbandMock.mock.calls[0][0]).toBe(1);
  });

  /* Удаление участника необратимо ровно так же, как роспуск: вернуть можно только
     новым приглашением. Один клик на это права не даёт ([FRM-07], [FB-03]). */
  it("удаление участника требует подтверждения", async () => {
    render(<HouseholdsPage />);
    await userEvent.click(screen.getByRole("button", { name: /Убрать участника/ }));
    expect(removeMock).not.toHaveBeenCalled();
    await userEvent.click(screen.getByRole("button", { name: "Убрать" }));
    expect(removeMock.mock.calls[0][0]).toEqual({ householdId: 1, userId: "u2" });
  });

  it("отзыв приглашения требует подтверждения", async () => {
    useInvitesMock.mockReturnValue(
      query([{ id: 7, email: null, role: "member", expires_at: "2026-09-12T10:00:00" }]),
    );
    render(<HouseholdsPage />);
    await userEvent.click(screen.getByRole("button", { name: /Отозвать приглашение/ }));
    expect(revokeMock).not.toHaveBeenCalled();
    await userEvent.click(screen.getByRole("button", { name: "Отозвать" }));
    expect(revokeMock.mock.calls[0][0]).toEqual({ householdId: 1, inviteId: 7 });
  });

  it("приглашение показывает ссылку — она приходит РОВНО один раз", async () => {
    inviteMock.mockImplementation((_args, opts) =>
      opts?.onSuccess?.({ invite_url: "https://finpilot.ru/join?token=abc123" }),
    );
    render(<HouseholdsPage />);
    await userEvent.click(screen.getByRole("button", { name: /Пригласить/ }));
    await waitFor(() =>
      expect(screen.getByDisplayValue("https://finpilot.ru/join?token=abc123")).toBeVisible(),
    );
    // Появление блока объявляется, иначе незрячий пользователь не узнает, что ссылка
    // возникла и исчезнет навсегда (WCAG 4.1.3).
    expect(screen.getByRole("status")).toHaveTextContent("показывается только сейчас");
  });

  /* Сервер отдаёт ссылку один раз. Вторая ссылка, затирающая первую, уничтожает
     единственный экземпляр — приглашение при этом уже создано и висит. */
  it("вторая ссылка не затирает первую", async () => {
    let n = 0;
    inviteMock.mockImplementation((_args, opts) =>
      opts?.onSuccess?.({ invite_url: `https://finpilot.ru/join?token=t${++n}` }),
    );
    render(<HouseholdsPage />);
    await userEvent.click(screen.getByRole("button", { name: /Пригласить/ }));
    await userEvent.click(screen.getByRole("button", { name: /Пригласить/ }));
    expect(screen.getByDisplayValue("https://finpilot.ru/join?token=t1")).toBeVisible();
    expect(screen.getByDisplayValue("https://finpilot.ru/join?token=t2")).toBeVisible();
  });

  /* Бэкенд принимает и `viewer` (доступ только на чтение). Первая редакция всегда слала
     `member`, то есть наблюдателя выдать было нельзя — ровно та дыра «бэкенд умеет,
     пути нет», ради которой экран и заведён. */
  it("роль приглашения выбирается, а не зашита в код", async () => {
    render(<HouseholdsPage />);
    await userEvent.selectOptions(screen.getByLabelText("Права"), "viewer");
    await userEvent.click(screen.getByRole("button", { name: /Пригласить/ }));
    expect(inviteMock.mock.calls[0][0]).toEqual({ householdId: 1, role: "viewer" });
  });

  it("участник не видит приглашений — бэкенд отдал бы 403", () => {
    useHouseholdsMock.mockReturnValue(query([joined]));
    render(<HouseholdsPage />);
    expect(screen.queryByRole("button", { name: /Пригласить/ })).not.toBeInTheDocument();
  });

  it("сбой загрузки участников виден, а не выглядит пустым списком (ST-01)", () => {
    useMembersMock.mockReturnValue(query(undefined, { error: new Error("403") }));
    render(<HouseholdsPage />);
    expect(screen.getByText("Участники не загрузились")).toBeVisible();
  });
});
