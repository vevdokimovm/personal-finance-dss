import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ForgotPasswordPage } from "./ForgotPasswordPage";

vi.mock("@tanstack/react-router", () => ({
  Link: ({ to, children }: { to: string; children: React.ReactNode }) => (
    <a href={to}>{children}</a>
  ),
}));

const mutateAsyncMock = vi.fn();
const useForgotPasswordMock = vi.fn();
vi.mock("@entities/auth", () => ({
  useForgotPassword: () => useForgotPasswordMock(),
}));

function baseState() {
  return { mutateAsync: mutateAsyncMock, isPending: false, error: null };
}

describe("ForgotPasswordPage — запрос сброса пароля", () => {
  it("email — видимый label (FRM-02)", () => {
    useForgotPasswordMock.mockReturnValue(baseState());
    render(<ForgotPasswordPage />);
    expect(screen.getByLabelText("Email")).toBeInTheDocument();
  });

  it("после отправки — нейтральное сообщение независимо от существования email (закрытая энумерация, как на бэке)", async () => {
    mutateAsyncMock.mockResolvedValue({
      detail: "Если аккаунт с таким email существует, на него отправлена ссылка для сброса пароля.",
      reset_url: null,
    });
    useForgotPasswordMock.mockReturnValue(baseState());
    render(<ForgotPasswordPage />);

    await userEvent.type(screen.getByLabelText("Email"), "anna@example.com");
    await userEvent.click(screen.getByRole("button", { name: "Отправить ссылку" }));

    expect(mutateAsyncMock).toHaveBeenCalledWith({ email: "anna@example.com" });
    expect(await screen.findByText(/Если аккаунт с таким email существует/)).toBeInTheDocument();
    // Форма скрывается после успеха — повторный сабмит не имеет смысла, поле не нужно.
    expect(screen.queryByLabelText("Email")).not.toBeInTheDocument();
  });

  it("ссылка назад на вход присутствует", () => {
    useForgotPasswordMock.mockReturnValue(baseState());
    render(<ForgotPasswordPage />);
    expect(screen.getByRole("link", { name: /Вернуться ко входу/ })).toHaveAttribute(
      "href",
      "/login",
    );
  });
});
