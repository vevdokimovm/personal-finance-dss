import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { LoginPage } from "./LoginPage";

const navigateMock = vi.fn();
vi.mock("@tanstack/react-router", () => ({
  useNavigate: () => navigateMock,
  Link: ({ to, children }: { to: string; children: React.ReactNode }) => (
    <a href={to}>{children}</a>
  ),
}));

const mutateAsyncMock = vi.fn();
const useLoginMock = vi.fn();
vi.mock("@entities/auth", () => ({
  useLogin: () => useLoginMock(),
}));

function baseLoginState() {
  return {
    mutateAsync: mutateAsyncMock,
    isPending: false,
    error: null,
  };
}

describe("LoginPage — вход (FRM/FB, ui_ux_design_standard.md)", () => {
  it("поля email/пароль имеют видимые постоянные label (FRM-02, не только placeholder)", () => {
    useLoginMock.mockReturnValue(baseLoginState());
    render(<LoginPage />);
    expect(screen.getByLabelText("Email")).toBeInTheDocument();
    expect(screen.getByLabelText("Пароль")).toBeInTheDocument();
  });

  it("успешный вход — редирект на / и тост, без mfa_required", async () => {
    mutateAsyncMock.mockResolvedValue({ access_token: "t", mfa_required: false });
    useLoginMock.mockReturnValue(baseLoginState());
    render(<LoginPage />);

    await userEvent.type(screen.getByLabelText("Email"), "anna@example.com");
    await userEvent.type(screen.getByLabelText("Пароль"), "password123");
    await userEvent.click(screen.getByRole("button", { name: "Войти" }));

    expect(mutateAsyncMock).toHaveBeenCalledWith({
      email: "anna@example.com",
      password: "password123",
    });
    expect(navigateMock).toHaveBeenCalledWith({ to: "/" });
  });

  it("ошибка (неверный пароль) — инлайн-баннер текстом (FRM-04), email не сбрасывается (FRM-06)", async () => {
    useLoginMock.mockReturnValue({
      mutateAsync: mutateAsyncMock,
      isPending: false,
      error: { detail: "Неверный email или пароль." },
    });
    render(<LoginPage />);
    await userEvent.type(screen.getByLabelText("Email"), "anna@example.com");
    expect(screen.getByRole("alert")).toHaveTextContent("Неверный email или пароль.");
    expect(screen.getByLabelText("Email")).toHaveValue("anna@example.com");
  });

  it("во время отправки кнопка заблокирована и меняет текст — защита от двойного сабмита (FRM-05)", () => {
    useLoginMock.mockReturnValue({ mutateAsync: mutateAsyncMock, isPending: true, error: null });
    render(<LoginPage />);
    const button = screen.getByRole("button", { name: "Входим…" });
    expect(button).toBeDisabled();
    expect(button).toHaveAttribute("aria-busy", "true");
  });

  it("ссылки на регистрацию и «забыли пароль» присутствуют — иначе экран тупиковый", () => {
    useLoginMock.mockReturnValue(baseLoginState());
    render(<LoginPage />);
    expect(screen.getByRole("link", { name: /Зарегистрироваться/ })).toHaveAttribute(
      "href",
      "/register",
    );
    expect(screen.getByRole("link", { name: /Забыли пароль/ })).toHaveAttribute(
      "href",
      "/forgot-password",
    );
  });
});
