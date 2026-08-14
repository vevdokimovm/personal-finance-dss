import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AuthTopbarLink } from "./AuthTopbarLink";

vi.mock("@tanstack/react-router", () => ({
  Link: ({ to, children }: { to: string; children: React.ReactNode }) => (
    <a href={to}>{children}</a>
  ),
}));

const useProfileMock = vi.fn();
const logoutMutateMock = vi.fn();
vi.mock("@entities/profile", () => ({
  useProfile: () => useProfileMock(),
  NotAuthenticatedError: class NotAuthenticatedError extends Error {},
}));
vi.mock("@entities/auth", () => ({
  useLogout: () => ({ mutate: logoutMutateMock, isPending: false }),
}));

describe("AuthTopbarLink — единственная входная точка к login/register из интерфейса", () => {
  it("гость (ошибка 401) — ссылка «Войти», не тупик", () => {
    useProfileMock.mockReturnValue({ data: undefined, isLoading: false, error: new Error("401") });
    render(<AuthTopbarLink />);
    expect(screen.getByRole("link", { name: "Войти" })).toHaveAttribute("href", "/login");
  });

  it("во время загрузки — ничего не показывает (не мигает «Войти» на долю секунды при реальном входе)", () => {
    useProfileMock.mockReturnValue({ data: undefined, isLoading: true, error: null });
    const { container } = render(<AuthTopbarLink />);
    expect(container.textContent).toBe("");
  });

  it("залогинен — email пользователя и кнопка «Выйти», не ссылка на вход", () => {
    useProfileMock.mockReturnValue({
      data: { email: "anna@example.com" },
      isLoading: false,
      error: null,
    });
    render(<AuthTopbarLink />);
    expect(screen.getByText("anna@example.com")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Выйти" })).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Войти" })).not.toBeInTheDocument();
  });

  it("клик «Выйти» вызывает мутацию логаута", async () => {
    useProfileMock.mockReturnValue({
      data: { email: "anna@example.com" },
      isLoading: false,
      error: null,
    });
    render(<AuthTopbarLink />);
    await userEvent.click(screen.getByRole("button", { name: "Выйти" }));
    expect(logoutMutateMock).toHaveBeenCalled();
  });

  it("после logout() рефетч /auth/me ловит 401, но TanStack Query держит старые data (stale-if-error) — топбар всё равно должен показать «Войти», не застрять на «Выйти» (реальный баг, пойман вручную в браузере)", () => {
    useProfileMock.mockReturnValue({
      data: { email: "anna@example.com" }, // старые данные ещё в кэше
      isLoading: false,
      error: new Error("401"), // но рефетч уже упал
    });
    render(<AuthTopbarLink />);
    expect(screen.getByRole("link", { name: "Войти" })).toHaveAttribute("href", "/login");
    expect(screen.queryByText("anna@example.com")).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Выйти" })).not.toBeInTheDocument();
  });
});
