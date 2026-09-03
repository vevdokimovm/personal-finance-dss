import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { RegisterPage } from "./RegisterPage";

const navigateMock = vi.fn();
// Параметр `?redirect=` — возврат туда, откуда пришли (приглашение в семейный доступ).
const searchMock = vi.fn(() => ({}) as Record<string, string>);
vi.mock("@tanstack/react-router", () => ({
  useNavigate: () => navigateMock,
  useSearch: () => searchMock(),
  Link: ({ to, children }: { to: string; children: React.ReactNode }) => (
    <a href={to}>{children}</a>
  ),
}));

const mutateAsyncMock = vi.fn();
const useRegisterMock = vi.fn();
vi.mock("@entities/auth", () => ({
  useRegister: () => useRegisterMock(),
}));

function baseState() {
  return { mutateAsync: mutateAsyncMock, isPending: false, error: null };
}

describe("RegisterPage — регистрация (FRM/FB, 152-ФЗ)", () => {
  it("поля имеют видимые label; чекбокс согласия обязателен (required, FRM-02)", () => {
    useRegisterMock.mockReturnValue(baseState());
    render(<RegisterPage />);
    expect(screen.getByLabelText("Email")).toBeInTheDocument();
    expect(screen.getByLabelText("Пароль")).toBeInTheDocument();
    const consent = screen.getByLabelText(/Согласен на обработку персональных данных/);
    expect(consent).toBeRequired();
  });

  it("успешная регистрация — редирект на / и тост", async () => {
    mutateAsyncMock.mockResolvedValue({ access_token: "t", user: { email: "a@b.ru" } });
    useRegisterMock.mockReturnValue(baseState());
    render(<RegisterPage />);

    await userEvent.type(screen.getByLabelText("Email"), "anna@example.com");
    await userEvent.type(screen.getByLabelText("Пароль"), "password123");
    await userEvent.click(screen.getByLabelText(/Согласен на обработку персональных данных/));
    await userEvent.click(screen.getByRole("button", { name: "Зарегистрироваться" }));

    expect(mutateAsyncMock).toHaveBeenCalledWith(
      expect.objectContaining({
        email: "anna@example.com",
        password: "password123",
        consent: true,
      }),
    );
    expect(navigateMock).toHaveBeenCalledWith({ to: "/" });
  });

  it("email уже занят (409) — инлайн-баннер текстом бэкенда (FRM-04)", () => {
    useRegisterMock.mockReturnValue({
      mutateAsync: mutateAsyncMock,
      isPending: false,
      error: { detail: "Пользователь с таким email уже зарегистрирован." },
    });
    render(<RegisterPage />);
    expect(screen.getByRole("alert")).toHaveTextContent(
      "Пользователь с таким email уже зарегистрирован.",
    );
  });

  it("ссылка на вход присутствует — путь назад для тех, у кого уже есть аккаунт", () => {
    useRegisterMock.mockReturnValue(baseState());
    render(<RegisterPage />);
    expect(screen.getByRole("link", { name: /Войти/ })).toHaveAttribute("href", "/login");
  });

  it("подписка на рассылку — отдельный необязательный чекбокс, не склеен с обязательным согласием", () => {
    useRegisterMock.mockReturnValue(baseState());
    render(<RegisterPage />);
    const newsletter = screen.getByLabelText(/рассылку/);
    expect(newsletter).not.toBeRequired();
    expect(newsletter).not.toBeChecked();
  });
  /* 🔴 Реферальная ссылка — `/register?ref=CODE`, её строит `routes_referral.py`.
     Страница открывалась, но параметр не читался и в тело запроса не попадал: бэкенд
     принимает `referral_code`, фронт его не слал НИКОГДА. То есть приглашение
     открывалось, регистрация проходила — и не засчитывалась никому. Тот же класс, что
     мёртвый `/join` (v8.36.0), только злее: там пользователь упирался в пустоту и это
     было заметно, здесь всё выглядит рабочим. */
  it("реферальный код из адреса уходит в запрос — иначе приглашение не засчитается", async () => {
    searchMock.mockReturnValue({ ref: "ABC123" });
    // Вызовы накапливаются по всему файлу — сверяем последний, а не первый:
    // `calls[0]` принадлежал бы соседнему тесту.
    mutateAsyncMock.mockClear();
    mutateAsyncMock.mockResolvedValue({ id: "u1" });
    useRegisterMock.mockReturnValue(baseState());
    render(<RegisterPage />);
    await userEvent.type(screen.getByLabelText("Email"), "a@b.ru");
    await userEvent.type(screen.getByLabelText("Пароль"), "Passw0rd!");
    await userEvent.click(screen.getByLabelText(/согласие|обработку/i));
    await userEvent.click(screen.getByRole("button", { name: "Зарегистрироваться" }));
    expect(mutateAsyncMock.mock.calls.at(-1)?.[0]).toMatchObject({ referral_code: "ABC123" });
    searchMock.mockReturnValue({});
  });
});
