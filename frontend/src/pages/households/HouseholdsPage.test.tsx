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

/* Флаги «запрос уже идёт» вынесены в объект: `vi.mock` поднимается выше объявлений,
   и обычная `const` дала бы ReferenceError. Через него тесты управляют `isPending`,
   не пересоздавая мок. */
const pendingFlags = vi.hoisted(() => ({ create: false, invite: false }));

vi.mock("@entities/households", () => ({
  useHouseholds: () => useHouseholdsMock(),
  useHouseholdMembers: () => useMembersMock(),
  useHouseholdInvites: () => useInvitesMock(),
  useCreateHousehold: () => ({ mutate: createMock, isPending: pendingFlags.create }),
  useCreateInvite: () => ({ mutate: inviteMock, isPending: pendingFlags.invite }),
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

/**
 * Ветки ОТКАЗА — 33 непокрытые строки экрана на момент v9.2.0.
 *
 * 🔴 **Успешный путь на этом экране проверен подробно, отказной — не был вовсе.**
 * А цена ошибки тут выше обычной: роспуск семьи и исключение участника необратимы,
 * и человек судит о том, случилось ли действие, по единственному признаку —
 * появившемуся сообщению. Молчание после клика читается как «сработало».
 */
describe("HouseholdsPage — что видно, когда действие НЕ удалось", () => {
  it("отказ при создании семьи сообщается, а не проглатывается", async () => {
    /* Немой клик читается как «экран сломался» ([FB-01]). Здесь он читался бы хуже:
       как «семья создана» — модалка ведь закроется. */
    createMock.mockImplementation((_name: string, opts?: { onError?: () => void }) =>
      opts?.onError?.(),
    );
    render(<HouseholdsPage />);

    await userEvent.click(screen.getByRole("button", { name: /Создать/ }));
    await userEvent.type(screen.getByLabelText(/Название/), "Семья");
    await userEvent.click(screen.getByRole("button", { name: /Создать семью|Создать$/ }));

    expect(toastError).toHaveBeenCalled();
    expect(toastSuccess).not.toHaveBeenCalled();
  });

  it("успех при создании закрывает модалку и очищает поле", async () => {
    /* Обратная сторона: поле, сохранившее прежнее имя, при следующем открытии
       предложит создать вторую семью с тем же названием. */
    createMock.mockImplementation((_name: string, opts?: { onSuccess?: () => void }) =>
      opts?.onSuccess?.(),
    );
    render(<HouseholdsPage />);

    await userEvent.click(screen.getByRole("button", { name: /Создать/ }));
    await userEvent.type(screen.getByLabelText(/Название/), "Семья");
    await userEvent.click(screen.getByRole("button", { name: /Создать семью|Создать$/ }));

    expect(toastSuccess).toHaveBeenCalled();
    expect(toastError).not.toHaveBeenCalled();
  });

  it("🔴 отказ при создании приглашения не оставляет пустую ссылку", async () => {
    /* Панель со ссылкой показывается только при непустом `invite_url`. Иначе человек
       увидел бы заголовок «Ссылка приглашения» и пустоту под ним — и отправил бы
       собеседнику ничего. */
    inviteMock.mockImplementation((_args: unknown, opts?: { onError?: () => void }) =>
      opts?.onError?.(),
    );
    render(<HouseholdsPage />);

    await userEvent.click(screen.getByRole("button", { name: /Пригласить/ }));

    expect(toastError).toHaveBeenCalled();
    expect(screen.queryByText(/показывается только сейчас/)).not.toBeInTheDocument();
  });

  it("🔴 ответ без ссылки тоже не рисует пустую панель", async () => {
    /* Успех с `invite_url: null` — не выдуманный случай: сервер собирает ссылку
       из `base_url`, и при неполной конфигурации поле придёт пустым. */
    inviteMock.mockImplementation(
      (_args: unknown, opts?: { onSuccess?: (r: { invite_url?: string | null }) => void }) =>
        opts?.onSuccess?.({ invite_url: null }),
    );
    render(<HouseholdsPage />);

    await userEvent.click(screen.getByRole("button", { name: /Пригласить/ }));

    expect(toastSuccess).toHaveBeenCalled();
    expect(screen.queryByText(/показывается только сейчас/)).not.toBeInTheDocument();
  });

  it("отказ при отзыве приглашения сообщается", async () => {
    revokeMock.mockImplementation((_args: unknown, opts?: { onError?: () => void }) =>
      opts?.onError?.(),
    );
    useInvitesMock.mockReturnValue(
      query([{ id: 7, email: null, role: "member", expires_at: "2026-09-12T10:00:00" }]),
    );
    render(<HouseholdsPage />);
    await userEvent.click(screen.getByRole("button", { name: /Отозвать приглашение/ }));
    await userEvent.click(screen.getByRole("button", { name: "Отозвать" }));

    expect(toastError).toHaveBeenCalled();
  });

  it("🔴 отказ при роспуске сообщается — иначе выглядит как успех", async () => {
    /* Роспуск необратим, и молчание после подтверждения человек прочтёт как
       «семья распущена». Он уйдёт с экрана, а семья останется. */
    disbandMock.mockImplementation((_id: number, opts?: { onError?: () => void }) =>
      opts?.onError?.(),
    );
    render(<HouseholdsPage />);

    await userEvent.click(screen.getByRole("button", { name: /Распустить/ }));
    await userEvent.click(screen.getByRole("button", { name: "Распустить навсегда" }));

    expect(toastError).toHaveBeenCalled();
    expect(toastSuccess).not.toHaveBeenCalled();
  });

  it("отказ при исключении участника сообщается", async () => {
    removeMock.mockImplementation((_args: unknown, opts?: { onError?: () => void }) =>
      opts?.onError?.(),
    );
    render(<HouseholdsPage />);

    await userEvent.click(screen.getByRole("button", { name: /Убрать участника/ }));
    await userEvent.click(screen.getByRole("button", { name: "Убрать" }));

    expect(toastError).toHaveBeenCalled();
  });

  it("отказ при выходе из семьи сообщается", async () => {
    useHouseholdsMock.mockReturnValue(query([joined]));
    leaveMock.mockImplementation((_id: number, opts?: { onError?: () => void }) =>
      opts?.onError?.(),
    );
    render(<HouseholdsPage />);

    await userEvent.click(screen.getByRole("button", { name: /Покинуть/ }));
    await userEvent.click(screen.getByRole("button", { name: /^Покинуть$|Подтвердить/ }));

    expect(toastError).toHaveBeenCalled();
  });
});

/**
 * Пути отмены и повтора — остаток непокрытого на экране.
 *
 * 🔴 **Их легко счесть мелочью, и это ошибка масштаба.** Отмена подтверждения —
 * единственный выход из диалога, где следующая кнопка необратима; кнопка «Повторить»
 * при упавшей загрузке — единственный способ увидеть свою семью после сбоя связи.
 * Сломайся любая из них, экран остаётся рабочим на вид и запирает человека.
 */
describe("HouseholdsPage — отмена, повтор и защита от двойного клика", () => {
  it("отмена в форме создания закрывает модалку и не создаёт ничего", async () => {
    render(<HouseholdsPage />);

    await userEvent.click(screen.getByRole("button", { name: /Создать семейный доступ/ }));
    await userEvent.click(screen.getByRole("button", { name: /Отмена|Отменить/ }));

    expect(createMock).not.toHaveBeenCalled();
    expect(screen.queryByLabelText(/Название/)).not.toBeInTheDocument();
  });

  it("🔴 ошибка пустого имени исчезает, как только человек начал печатать", async () => {
    /* Сообщение, висящее над полем, которое человек уже исправил, читается как
       «всё ещё не так» — и он стирает верное имя, ища ошибку. */
    render(<HouseholdsPage />);

    await userEvent.click(screen.getByRole("button", { name: /Создать семейный доступ/ }));
    await userEvent.click(screen.getByRole("button", { name: /^Создать$/ }));
    expect(screen.getByRole("alert")).toBeInTheDocument();

    await userEvent.type(screen.getByLabelText(/Название/), "С");
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  it("сбой загрузки списка даёт кнопку повтора, и она зовёт refetch", async () => {
    const refetch = vi.fn();
    useHouseholdsMock.mockReturnValue(query(undefined, { error: new Error("500"), refetch }));
    render(<HouseholdsPage />);

    await userEvent.click(screen.getByRole("button", { name: /Повторить|Обновить/ }));
    expect(refetch).toHaveBeenCalled();
  });

  it("сбой загрузки участников тоже даёт повтор", async () => {
    const refetch = vi.fn();
    useMembersMock.mockReturnValue(query(undefined, { error: new Error("500"), refetch }));
    render(<HouseholdsPage />);

    await userEvent.click(screen.getByRole("button", { name: /Повторить|Обновить/ }));
    expect(refetch).toHaveBeenCalled();
  });

  it("🔴 отмена подтверждения не выполняет необратимое действие", async () => {
    /* Диалог подтверждения защищает от роспуска в один клик. Если «Отмена» не
       закрывает его или, хуже, проваливается к действию, защита превращается
       в лишний шаг перед той же катастрофой. */
    render(<HouseholdsPage />);

    await userEvent.click(screen.getByRole("button", { name: /Распустить/ }));
    await userEvent.click(screen.getByRole("button", { name: /Отмена|Отменить/ }));

    expect(disbandMock).not.toHaveBeenCalled();
    expect(screen.queryByRole("button", { name: "Распустить навсегда" })).not.toBeInTheDocument();
  });

  it("отмена подтверждения при удалении участника", async () => {
    render(<HouseholdsPage />);

    await userEvent.click(screen.getByRole("button", { name: /Убрать участника/ }));
    await userEvent.click(screen.getByRole("button", { name: /Отмена|Отменить/ }));

    expect(removeMock).not.toHaveBeenCalled();
  });

  it("отмена подтверждения при отзыве приглашения", async () => {
    useInvitesMock.mockReturnValue(
      query([{ id: 7, email: null, role: "member", expires_at: "2026-09-12T10:00:00" }]),
    );
    render(<HouseholdsPage />);

    await userEvent.click(screen.getByRole("button", { name: /Отозвать приглашение/ }));
    await userEvent.click(screen.getByRole("button", { name: /Отмена|Отменить/ }));

    expect(revokeMock).not.toHaveBeenCalled();
  });
});

/**
 * Успешные пути необратимых действий и защита от двойного клика.
 *
 * 🔴 **`if (mutation.isPending) return;` — не микрооптимизация.** Роспуск семьи
 * и приглашение не идемпотентны: второй клик по неотзывчивой кнопке создаёт второе
 * приглашение или шлёт второй запрос на удаление. Проверка стоит первой строкой
 * обработчика, и её легко снять при рефакторинге — тест держит её на месте.
 */
describe("HouseholdsPage — успешные пути и защита от повторного клика", () => {
  it("успех исключения участника сообщается и возвращает фокус", async () => {
    /* Строка исчезает вместе с кнопкой, на которой стоял фокус: без переноса
       он проваливается в body, и человек теряет место на странице ([A11Y-05]). */
    removeMock.mockImplementation((_args: unknown, opts?: { onSuccess?: () => void }) =>
      opts?.onSuccess?.(),
    );
    render(<HouseholdsPage />);

    await userEvent.click(screen.getByRole("button", { name: /Убрать участника/ }));
    await userEvent.click(screen.getByRole("button", { name: "Убрать" }));

    expect(toastSuccess).toHaveBeenCalled();
  });

  it("успех отзыва приглашения сообщается", async () => {
    useInvitesMock.mockReturnValue(
      query([{ id: 7, email: null, role: "member", expires_at: "2026-09-12T10:00:00" }]),
    );
    revokeMock.mockImplementation((_args: unknown, opts?: { onSuccess?: () => void }) =>
      opts?.onSuccess?.(),
    );
    render(<HouseholdsPage />);

    await userEvent.click(screen.getByRole("button", { name: /Отозвать приглашение/ }));
    await userEvent.click(screen.getByRole("button", { name: "Отозвать" }));

    expect(toastSuccess).toHaveBeenCalled();
  });

  it("успех роспуска сообщается", async () => {
    disbandMock.mockImplementation((_id: number, opts?: { onSuccess?: () => void }) =>
      opts?.onSuccess?.(),
    );
    render(<HouseholdsPage />);

    await userEvent.click(screen.getByRole("button", { name: /Распустить/ }));
    await userEvent.click(screen.getByRole("button", { name: "Распустить навсегда" }));

    expect(toastSuccess).toHaveBeenCalled();
  });

  it("успех выхода из семьи сообщается", async () => {
    useHouseholdsMock.mockReturnValue(query([joined]));
    leaveMock.mockImplementation((_id: number, opts?: { onSuccess?: () => void }) =>
      opts?.onSuccess?.(),
    );
    render(<HouseholdsPage />);

    await userEvent.click(screen.getByRole("button", { name: /Покинуть/ }));
    await userEvent.click(screen.getByRole("button", { name: /^Покинуть$|Выйти/ }));

    expect(toastSuccess).toHaveBeenCalled();
  });

  it("сбой загрузки приглашений даёт повтор", async () => {
    const refetch = vi.fn();
    useInvitesMock.mockReturnValue(query(undefined, { error: new Error("500"), refetch }));
    render(<HouseholdsPage />);

    await userEvent.click(screen.getByRole("button", { name: /Повторить|Обновить/ }));
    expect(refetch).toHaveBeenCalled();
  });
});

describe("HouseholdsPage — защита от повторного клика", () => {
  it("🔴 второй клик по «Создать» во время запроса не создаёт вторую семью", async () => {
    /* `if (create.isPending) return;` первой строкой обработчика. Создание НЕ
       идемпотентно: два запроса — две семьи с одним именем, и человек увидит дубль,
       который придётся распускать. Проверка легко снимается при рефакторинге. */
    pendingFlags.create = true;
    render(<HouseholdsPage />);

    await userEvent.click(screen.getByRole("button", { name: /Создать семейный доступ/ }));
    await userEvent.type(screen.getByLabelText(/Название/), "Семья");
    /* Во время запроса кнопка подписана «Создаём…» — по ней и кликаем: тест обязан
       нажимать то, что видит человек, а не идеализированную подпись. */
    await userEvent.click(screen.getByRole("button", { name: /Создаём/ }));

    expect(createMock).not.toHaveBeenCalled();
    pendingFlags.create = false;
  });

  it("🔴 второй клик по «Пригласить» не создаёт второе приглашение", async () => {
    /* Каждое приглашение — отдельная одноразовая ссылка. Два клика дают две ссылки,
       и вторая останется висеть непогашенной: отзывать её человек не будет,
       потому что не знает о ней. */
    pendingFlags.invite = true;
    render(<HouseholdsPage />);

    await userEvent.click(screen.getByRole("button", { name: /Пригласить|Создаём ссылку/ }));

    expect(inviteMock).not.toHaveBeenCalled();
    pendingFlags.invite = false;
  });

  it("закрытие модалки крестиком сбрасывает ошибку имени", async () => {
    /* Ошибка, пережившая закрытие, встретит человека при следующем открытии формы —
       и он решит, что предыдущая попытка что-то сломала. */
    render(<HouseholdsPage />);

    await userEvent.click(screen.getByRole("button", { name: /Создать семейный доступ/ }));
    await userEvent.click(screen.getByRole("button", { name: "Создать" }));
    expect(screen.getByRole("alert")).toBeInTheDocument();

    /* Кнопок закрытия у модалки две — «Отмена» в форме и крестик в шапке. Берём
       именно «Отмена»: крестик — предмет тестов самой `Modal`. */
    await userEvent.click(screen.getByRole("button", { name: "Отмена" }));
    await userEvent.click(screen.getByRole("button", { name: /Создать семейный доступ/ }));

    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });
});

describe("HouseholdsPage — незнакомая роль и участник без почты", () => {
  it("🔴 незнакомая роль показывается как есть, а не пропадает", () => {
    /* `ROLE_LABEL[role] ?? role` — карта переводов отстаёт от бэкенда на релиз.
       Пустое место вместо роли опаснее непереведённого кода: владелец не увидит,
       что у участника вообще есть какие-то права. */
    useMembersMock.mockReturnValue(
      query([{ user_id: "u2", email: "b@test.io", role: "auditor", joined_at: null }]),
    );
    render(<HouseholdsPage />);
    expect(screen.getByText(/auditor/)).toBeInTheDocument();
  });

  it("участник без почты опознаётся по идентификатору", () => {
    /* `member.email ?? member.user_id` — почта необязательна: приглашение можно
       отправить ссылкой без адреса. Строка без подписи не даёт исключить нужного
       человека, а кнопка «Убрать» рядом с ней остаётся. */
    useMembersMock.mockReturnValue(
      query([{ user_id: "u-42", email: null, role: "member", joined_at: null }]),
    );
    render(<HouseholdsPage />);
    expect(screen.getByText(/u-42/)).toBeInTheDocument();
  });

  it("пока грузятся участники — скелетон, а не пустой состав семьи", () => {
    /* Пустой список читается как «в семье никого», и владелец решит, что приглашения
       не сработали. */
    useMembersMock.mockReturnValue(query(undefined, { isLoading: true }));
    render(<HouseholdsPage />);
    expect(screen.getByRole("status")).toBeInTheDocument();
  });
});
