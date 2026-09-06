import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { LoginPage } from "./LoginPage";

const { loginMock, verifyMock, navigateMock } = vi.hoisted(() => ({
  loginMock: vi.fn(),
  verifyMock: vi.fn(),
  navigateMock: vi.fn(),
}));

vi.mock("@entities/auth", async () => {
  const actual = await vi.importActual<typeof import("@entities/auth")>("@entities/auth");
  return { ...actual, useLogin: () => loginMock(), useMfaVerify: () => verifyMock() };
});

vi.mock("@tanstack/react-router", async () => {
  const actual =
    await vi.importActual<typeof import("@tanstack/react-router")>("@tanstack/react-router");
  return {
    ...actual,
    useNavigate: () => navigateMock,
    useSearch: () => ({}),
    Link: ({ children, ...rest }: { children: React.ReactNode }) => <a {...rest}>{children}</a>,
  };
});

function mutation(overrides: Record<string, unknown> = {}) {
  return {
    mutate: vi.fn(),
    mutateAsync: vi.fn().mockResolvedValue({ mfa_required: false }),
    isPending: false,
    isError: false,
    error: null,
    ...overrides,
  };
}

async function submitCredentials() {
  await userEvent.type(screen.getByLabelText(/email|почт/i), "anna@example.com");
  await userEvent.type(screen.getByLabelText(/пароль/i), "password123");
  await userEvent.click(screen.getByRole("button", { name: /войти/i }));
}

beforeEach(() => {
  vi.clearAllMocks();
  loginMock.mockReturnValue(mutation());
  verifyMock.mockReturnValue(mutation());
});

/**
 * 🔴 Гипотеза H9 независимого эксперта, подтверждена чтением кода 05.09.2026.
 *
 * `POST /auth/mfa/enroll` и `/mfa/confirm` открыты любому пользователю, а войти
 * с включённым MFA было НЕЛЬЗЯ: `LoginPage` на `mfa_required` показывал уведомление
 * без поля кода. Комментарий обосновывал это тем, что «в UI пока нет способа включить
 * MFA вообще, ветка практически недостижима» — но недостижима она только из SPA;
 * прямой вызов API, тест или ранняя Jinja-версия (снесена в v8.23.0) её достигают.
 *
 * **Цена:** аккаунт, у которого MFA когда-либо включали, заперт навсегда. Войти нельзя,
 * а `/mfa/disable` требует уже аутентифицированной сессии — то есть выключить второй
 * фактор может только тот, кто уже вошёл. Восстановление возможно лишь правкой базы
 * руками, и на проде это означает потерю доступа к своим финансовым данным.
 */
describe("LoginPage — второй фактор при входе", () => {
  it("на mfa_required показывает поле для кода, а не уведомление", async () => {
    loginMock.mockReturnValue(
      mutation({ mutateAsync: vi.fn().mockResolvedValue({ mfa_required: true, mfa_token: "t1" }) }),
    );
    render(<LoginPage />);
    await submitCredentials();

    expect(await screen.findByLabelText(/код|подтвержд/i)).toBeVisible();
  });

  it("отправляет код вместе с mfa_token, полученным от логина", async () => {
    const mfaVerify = vi.fn().mockResolvedValue({ mfa_required: false });
    loginMock.mockReturnValue(
      mutation({ mutateAsync: vi.fn().mockResolvedValue({ mfa_required: true, mfa_token: "t1" }) }),
    );
    verifyMock.mockReturnValue(mutation({ mutateAsync: mfaVerify }));
    render(<LoginPage />);
    await submitCredentials();

    await userEvent.type(await screen.findByLabelText(/код|подтвержд/i), "123456");
    await userEvent.click(screen.getByRole("button", { name: /подтвердить|войти/i }));

    /* 🔴 `mfa_token` — краткоживущий промежуточный токен; без него сервер не знает,
       чей код проверяет. Отправить один код, потеряв токен, — 401 без объяснения. */
    await waitFor(() =>
      expect(mfaVerify).toHaveBeenCalledWith(
        expect.objectContaining({ mfa_token: "t1", code: "123456" }),
      ),
    );
  });

  it("принимает recovery-код, а не только шестизначный TOTP", async () => {
    /* Recovery-код — единственный выход, когда телефон потерян. Валидация,
       требующая ровно шесть цифр, отрезала бы его и вернула запертый аккаунт
       (схема `MfaVerifyRequest` допускает до 16 символов). */
    const mfaVerify = vi.fn().mockResolvedValue({ mfa_required: false });
    loginMock.mockReturnValue(
      mutation({ mutateAsync: vi.fn().mockResolvedValue({ mfa_required: true, mfa_token: "t1" }) }),
    );
    verifyMock.mockReturnValue(mutation({ mutateAsync: mfaVerify }));
    render(<LoginPage />);
    await submitCredentials();

    await userEvent.type(await screen.findByLabelText(/код|подтвержд/i), "a1b2-c3d4-e5f6");
    await userEvent.click(screen.getByRole("button", { name: /подтвердить|войти/i }));

    await waitFor(() =>
      expect(mfaVerify).toHaveBeenCalledWith(expect.objectContaining({ code: "a1b2-c3d4-e5f6" })),
    );
  });

  it("объясняет, что делать при потерянном устройстве", async () => {
    loginMock.mockReturnValue(
      mutation({ mutateAsync: vi.fn().mockResolvedValue({ mfa_required: true, mfa_token: "t1" }) }),
    );
    render(<LoginPage />);
    await submitCredentials();

    // Без этой подсказки человек с потерянным телефоном считает аккаунт потерянным,
    // хотя recovery-коды ему выдавались при включении MFA.
    expect(await screen.findByText(/резервн|восстановлен/i)).toBeVisible();
  });

  it("неверный код показан как ошибка, а форма кода остаётся на экране", async () => {
    /* 🔴 Уводить обратно на логин после неверного кода — заставлять вводить пароль
       заново и получать НОВЫЙ `mfa_token`. Человек, ошибившийся цифрой, оказывается
       в начале пути. */
    loginMock.mockReturnValue(
      mutation({ mutateAsync: vi.fn().mockResolvedValue({ mfa_required: true, mfa_token: "t1" }) }),
    );
    verifyMock.mockReturnValue(
      mutation({
        isError: true,
        error: { detail: "Неверный код." },
        mutateAsync: vi.fn().mockRejectedValue(new Error("bad")),
      }),
    );
    render(<LoginPage />);
    await submitCredentials();

    const field = await screen.findByLabelText(/код|подтвержд/i);
    await userEvent.type(field, "000000");
    await userEvent.click(screen.getByRole("button", { name: /подтвердить|войти/i }));

    expect(screen.getByRole("alert")).toHaveTextContent(/код/i);
    expect(screen.getByLabelText(/код|подтвержд/i)).toBeVisible();
  });

  it("обычный вход без MFA не изменился", async () => {
    /* Тест против переусердствования: второй фактор не должен появляться у тех,
       у кого он выключен, — а это подавляющее большинство. */
    render(<LoginPage />);
    await submitCredentials();

    await waitFor(() => expect(navigateMock).toHaveBeenCalled());
    expect(screen.queryByLabelText(/код подтверждения/i)).not.toBeInTheDocument();
  });
});
