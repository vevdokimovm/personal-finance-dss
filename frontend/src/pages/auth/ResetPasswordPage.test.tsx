import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ResetPasswordPage } from "./ResetPasswordPage";

const navigateMock = vi.fn();
let searchMock: { token?: string } = { token: "valid-token-123" };
vi.mock("@tanstack/react-router", () => ({
  useNavigate: () => navigateMock,
  useSearch: () => searchMock,
  Link: ({ to, children }: { to: string; children: React.ReactNode }) => (
    <a href={to}>{children}</a>
  ),
}));

const mutateAsyncMock = vi.fn();
const useResetPasswordMock = vi.fn();
vi.mock("@entities/auth", () => ({
  useResetPassword: () => useResetPasswordMock(),
}));

function baseState() {
  return { mutateAsync: mutateAsyncMock, isPending: false, error: null };
}

describe("ResetPasswordPage — установка нового пароля по токену из ссылки", () => {
  it("без ?token= в URL — сразу объясняет проблему, не показывает форму (fail-loud)", () => {
    searchMock = {};
    useResetPasswordMock.mockReturnValue(baseState());
    render(<ResetPasswordPage />);
    expect(screen.getByRole("alert")).toHaveTextContent(/Ссылка недействительна/);
    expect(screen.queryByLabelText("Новый пароль")).not.toBeInTheDocument();
  });

  it("с валидным ?token= — форма нового пароля, поле с видимым label (FRM-02)", () => {
    searchMock = { token: "valid-token-123" };
    useResetPasswordMock.mockReturnValue(baseState());
    render(<ResetPasswordPage />);
    expect(screen.getByLabelText("Новый пароль")).toBeInTheDocument();
  });

  it("успешный сброс — передаёт токен из URL, ведёт на /login", async () => {
    searchMock = { token: "valid-token-123" };
    mutateAsyncMock.mockResolvedValue({ detail: "Пароль обновлён." });
    useResetPasswordMock.mockReturnValue(baseState());
    render(<ResetPasswordPage />);

    await userEvent.type(screen.getByLabelText("Новый пароль"), "newpassword123");
    await userEvent.click(screen.getByRole("button", { name: "Сохранить пароль" }));

    expect(mutateAsyncMock).toHaveBeenCalledWith({
      token: "valid-token-123",
      new_password: "newpassword123",
    });
    expect(navigateMock).toHaveBeenCalledWith({ to: "/login" });
  });

  it("недействительный/истёкший токен (400 от бэкенда) — инлайн-баннер текстом (FRM-04)", () => {
    searchMock = { token: "expired-token" };
    useResetPasswordMock.mockReturnValue({
      mutateAsync: mutateAsyncMock,
      isPending: false,
      error: { detail: "Ссылка для сброса недействительна или истекла." },
    });
    render(<ResetPasswordPage />);
    expect(screen.getByRole("alert")).toHaveTextContent(
      "Ссылка для сброса недействительна или истекла.",
    );
  });
});
