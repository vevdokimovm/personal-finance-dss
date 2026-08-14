import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { UseQueryResult } from "@tanstack/react-query";
import { ProfilePage } from "./ProfilePage";
import { NotAuthenticatedError } from "@entities/profile";
import type { UserProfile } from "@entities/profile";

const { useProfileMock } = vi.hoisted(() => ({ useProfileMock: vi.fn() }));
let searchMock: { verified?: string } = {};

vi.mock("@entities/profile", async () => {
  const actual = await vi.importActual<typeof import("@entities/profile")>("@entities/profile");
  return { ...actual, useProfile: useProfileMock };
});

vi.mock("@tanstack/react-router", async () => {
  const actual =
    await vi.importActual<typeof import("@tanstack/react-router")>("@tanstack/react-router");
  return {
    ...actual,
    useSearch: () => searchMock,
    Link: ({ to, children }: { to: string; children: React.ReactNode }) => (
      <a href={to}>{children}</a>
    ),
  };
});

function queryResult(partial: Partial<UseQueryResult<UserProfile>>): UseQueryResult<UserProfile> {
  return {
    isLoading: false,
    isError: false,
    data: undefined,
    error: null,
    refetch: vi.fn(),
    ...partial,
  } as UseQueryResult<UserProfile>;
}

const PROFILE: UserProfile = {
  id: "u1",
  email: "anna@example.com",
  display_name: "Анна",
  email_verified: true,
  created_at: "2026-01-15",
};

describe("ProfilePage", () => {
  it("показывает скелетон, пока данные грузятся", () => {
    useProfileMock.mockReturnValue(queryResult({ isLoading: true }));
    render(<ProfilePage />);
    expect(screen.getByText("Загрузка списка…")).toBeInTheDocument();
  });

  it("показывает состояние сетевой ошибки и повторяет запрос", async () => {
    const refetch = vi.fn();
    useProfileMock.mockReturnValue(
      queryResult({ isError: true, error: new Error("network"), refetch }),
    );
    render(<ProfilePage />);
    expect(screen.getByRole("alert")).toHaveTextContent("Не получилось загрузить профиль");
    await userEvent.click(screen.getByRole("button", { name: "Повторить" }));
    expect(refetch).toHaveBeenCalledOnce();
  });

  it("неаутентифицирован (401) — отдельная ветка без кнопки «Повторить», со ссылкой на вход", () => {
    // a11y-auditor, Э4 партия 2, P1: одинаковое сообщение для 401 и сетевого сбоя
    // давало тупиковый цикл retry без объяснения для пользователей экранных дикторов.
    useProfileMock.mockReturnValue(
      queryResult({ isError: true, error: new NotAuthenticatedError() }),
    );
    render(<ProfilePage />);
    expect(screen.getByText("Нужно войти в систему")).toBeInTheDocument();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Повторить" })).not.toBeInTheDocument();
    // Раньше здесь честно писали «экран входа ещё не готов» — теперь он есть, ссылка ведёт туда.
    expect(screen.getByRole("link", { name: "Войти" })).toHaveAttribute("href", "/login");
  });

  it("?verified=1 — баннер об успешном подтверждении email (GET /api/auth/verify редиректит сюда)", () => {
    searchMock = { verified: "1" };
    useProfileMock.mockReturnValue(queryResult({ data: PROFILE }));
    render(<ProfilePage />);
    expect(screen.getByRole("status")).toHaveTextContent("Email подтверждён");
    searchMock = {};
  });

  it("?verified=0 — баннер о неудачном подтверждении (истёкшая/использованная ссылка)", () => {
    searchMock = { verified: "0" };
    useProfileMock.mockReturnValue(queryResult({ data: PROFILE }));
    render(<ProfilePage />);
    expect(screen.getByRole("alert")).toHaveTextContent("не получилось подтвердить");
    searchMock = {};
  });

  it("без ?verified= — баннера подтверждения нет вовсе", () => {
    searchMock = {};
    useProfileMock.mockReturnValue(queryResult({ data: PROFILE }));
    render(<ProfilePage />);
    expect(screen.queryByText(/подтвержд/i)).not.toBeInTheDocument();
  });

  it("рендерит данные профиля — имя, email, дату регистрации", () => {
    useProfileMock.mockReturnValue(queryResult({ data: PROFILE }));
    render(<ProfilePage />);
    expect(screen.getByText("Анна")).toBeInTheDocument();
    expect(screen.getByText("anna@example.com")).toBeInTheDocument();
    expect(screen.queryByText("не подтверждён")).not.toBeInTheDocument();
  });

  it("email не подтверждён — показывает бейдж", () => {
    useProfileMock.mockReturnValue(queryResult({ data: { ...PROFILE, email_verified: false } }));
    render(<ProfilePage />);
    expect(screen.getByText("не подтверждён")).toBeInTheDocument();
  });

  it("имя не указано — плейсхолдер вместо пустой строки", () => {
    useProfileMock.mockReturnValue(queryResult({ data: { ...PROFILE, display_name: null } }));
    render(<ProfilePage />);
    expect(screen.getByText("Не указано")).toBeInTheDocument();
  });
});
