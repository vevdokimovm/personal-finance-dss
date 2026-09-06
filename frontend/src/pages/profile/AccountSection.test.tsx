import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AccountSection } from "./AccountSection";

const { changePasswordMock, deleteAccountMock } = vi.hoisted(() => ({
  changePasswordMock: vi.fn(),
  deleteAccountMock: vi.fn(),
}));

vi.mock("@entities/auth", async () => {
  const actual = await vi.importActual<typeof import("@entities/auth")>("@entities/auth");
  return {
    ...actual,
    useChangePassword: () => changePasswordMock(),
    useDeleteAccount: () => deleteAccountMock(),
  };
});

function idleMutation(overrides: Record<string, unknown> = {}) {
  return {
    mutate: vi.fn(),
    mutateAsync: vi.fn(),
    isPending: false,
    isError: false,
    error: null,
    ...overrides,
  };
}

beforeEach(() => {
  vi.clearAllMocks();
  changePasswordMock.mockReturnValue(idleMutation());
  deleteAccountMock.mockReturnValue(idleMutation());
});

/**
 * 🔴 Найдено аудитом independent-expert 05.09.2026: `POST /auth/change-password`
 * и `DELETE /auth/me` живут на бэкенде и **не имеют UI вообще**. При этом экран
 * согласий говорит пользователю «это согласие нельзя отозвать без удаления аккаунта»,
 * а юрреестр помечает L9 («удаление аккаунта и данных по запросу») выполненным —
 * по факту существования функции `crud.delete_user`, а не пути пользователя.
 *
 * То есть право по 152-ФЗ реализовано и недостижимо — буквальный повтор SEV1
 * `CONSENT-GATE-NO-UI`.
 */
describe("AccountSection — смена пароля", () => {
  it("форма смены пароля есть на экране", () => {
    render(<AccountSection />);
    expect(screen.getByLabelText(/текущий пароль/i)).toBeVisible();
    expect(screen.getByLabelText(/новый пароль/i)).toBeVisible();
  });

  it("предупреждает, что смена пароля завершит все сессии", () => {
    render(<AccountSection />);
    // Бэкенд гасит ВСЕ сессии, включая текущую (банковская планка). Человек, не
    // предупреждённый об этом, решит, что его «выкинуло» из-за ошибки.
    expect(screen.getByText(/придётся войти заново|все устройства|завершит/i)).toBeVisible();
  });

  it("отправляет оба пароля", async () => {
    const mutate = vi.fn();
    changePasswordMock.mockReturnValue(idleMutation({ mutate }));
    render(<AccountSection />);

    await userEvent.type(screen.getByLabelText(/текущий пароль/i), "oldpassword1");
    await userEvent.type(screen.getByLabelText(/новый пароль/i), "newpassword1");
    await userEvent.click(screen.getByRole("button", { name: /сменить пароль/i }));

    await waitFor(() =>
      expect(mutate).toHaveBeenCalledWith(
        expect.objectContaining({
          current_password: "oldpassword1",
          new_password: "newpassword1",
        }),
        expect.anything(),
      ),
    );
  });

  it("ошибка сервера показывается человеку, а не молчит", () => {
    changePasswordMock.mockReturnValue(
      idleMutation({ isError: true, error: new Error("Текущий пароль неверен.") }),
    );
    render(<AccountSection />);
    expect(screen.getByRole("alert")).toHaveTextContent(/пароль/i);
  });
});

describe("AccountSection — фокус не теряется на асинхронных кнопках", () => {
  /* 🔴 Нативный `disabled` выводит элемент из дерева доступности В МОМЕНТ клика:
     фокус клавиатуры проваливается в `<body>` раньше, чем завершится запрос
     (a11y-auditor, WCAG 2.4.3). Паттерн `aria-disabled` документирован в `Button.css`
     и применён в `ConsentsSection` — эта секция его сначала не унаследовала.

     Тесты проверяют АТРИБУТ, а не поведение фокуса: jsdom не воспроизводит потерю
     фокуса при снятии элемента из дерева, и проверка «фокус на месте» была бы
     зелёной при любом варианте. Мутация «вернуть disabled» роняет эти три. */

  it("кнопка смены пароля остаётся фокусируемой во время запроса", () => {
    changePasswordMock.mockReturnValue(idleMutation({ isPending: true }));
    render(<AccountSection />);

    const button = screen.getByRole("button", { name: /меняем|сменить пароль/i });
    expect(button).not.toHaveAttribute("disabled");
    expect(button).toHaveAttribute("aria-disabled", "true");
    expect(button).toHaveAttribute("aria-busy", "true");
  });

  it("кнопка подтверждения удаления остаётся фокусируемой во время запроса", async () => {
    deleteAccountMock.mockReturnValue(idleMutation({ isPending: true }));
    render(<AccountSection />);

    await userEvent.click(screen.getByRole("button", { name: /удалить аккаунт/i }));
    const dialog = await screen.findByRole("dialog");
    const confirm = within(dialog).getByRole("button", { name: /удаляем|удалить навсегда/i });

    expect(confirm).not.toHaveAttribute("disabled");
    expect(confirm).toHaveAttribute("aria-disabled", "true");
  });

  it("повторный клик во время запроса не отправляет второе удаление", async () => {
    const mutate = vi.fn();
    deleteAccountMock.mockReturnValue(idleMutation({ mutate, isPending: true }));
    render(<AccountSection />);

    await userEvent.click(screen.getByRole("button", { name: /удалить аккаунт/i }));
    const dialog = await screen.findByRole("dialog");
    await userEvent.click(within(dialog).getByRole("button", { name: /удаляем/i }));

    // `aria-disabled` не блокирует событие браузером — блокирует обработчик.
    expect(mutate).not.toHaveBeenCalled();
  });
});

describe("AccountSection — удаление аккаунта", () => {
  /* 🔴 Удаление необратимо и стирает всё: операции, цели, кредиты, план. Кнопка,
     удаляющая это одним кликом, — то же, чем оказался `/demo/load` в v8.46.0. */
  it("не удаляет по одному клику — требует подтверждения", async () => {
    const mutate = vi.fn();
    deleteAccountMock.mockReturnValue(idleMutation({ mutate }));
    render(<AccountSection />);

    await userEvent.click(screen.getByRole("button", { name: /удалить аккаунт/i }));
    expect(mutate).not.toHaveBeenCalled();
  });

  it("подтверждение называет, что именно будет стёрто и что это навсегда", async () => {
    render(<AccountSection />);
    await userEvent.click(screen.getByRole("button", { name: /удалить аккаунт/i }));

    const dialog = await screen.findByRole("dialog");
    expect(dialog).toHaveTextContent(/безвозвратно|навсегда|нельзя отменить/i);
    expect(dialog).toHaveTextContent(/операци|цел|данны/i);
  });

  it("удаляет после подтверждения", async () => {
    const mutate = vi.fn();
    deleteAccountMock.mockReturnValue(idleMutation({ mutate }));
    render(<AccountSection />);

    await userEvent.click(screen.getByRole("button", { name: /удалить аккаунт/i }));
    const dialog = await screen.findByRole("dialog");
    await userEvent.click(
      within(dialog).getByRole("button", { name: /удалить навсегда|подтвердить/i }),
    );

    await waitFor(() => expect(mutate).toHaveBeenCalled());
  });

  it("отмена закрывает диалог и ничего не удаляет", async () => {
    const mutate = vi.fn();
    deleteAccountMock.mockReturnValue(idleMutation({ mutate }));
    render(<AccountSection />);

    await userEvent.click(screen.getByRole("button", { name: /удалить аккаунт/i }));
    const dialog = await screen.findByRole("dialog");
    await userEvent.click(within(dialog).getByRole("button", { name: /отмена/i }));

    expect(mutate).not.toHaveBeenCalled();
    await waitFor(() => expect(screen.queryByRole("dialog")).not.toBeInTheDocument());
  });

  /* Связь с отзывом согласия: экран согласий отправляет сюда, и человек должен
     понять, что попал в нужное место, а не гадать. */
  it("объясняет связь с отзывом согласия на обработку ПДн", () => {
    render(<AccountSection />);
    expect(screen.getByText(/соглас/i)).toBeVisible();
  });
});
