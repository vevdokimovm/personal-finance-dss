import { beforeEach, describe, expect, it, vi } from "vitest";
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

const useConsentsMock = vi.fn();
const grantMutateMock = vi.fn();
const withdrawMutateMock = vi.fn();

vi.mock("@entities/consents", () => ({
  useConsents: () => useConsentsMock(),
  useGrantConsent: () => ({ mutate: grantMutateMock, isPending: false }),
  useWithdrawConsent: () => ({ mutate: withdrawMutateMock, isPending: false }),
}));

const { toastErrorMock, toastUndoMock } = vi.hoisted(() => ({
  toastErrorMock: vi.fn(),
  toastUndoMock: vi.fn(),
}));

vi.mock("@shared/ui", async () => {
  const actual = await vi.importActual<typeof import("@shared/ui")>("@shared/ui");
  return {
    ...actual,
    toast: { ...actual.toast, error: toastErrorMock, undo: toastUndoMock },
  };
});

const CONSENTS_NOT_GRANTED = {
  financial_data: { granted: false, version: "1.0", granted_at: null, withdrawable: true },
};
const CONSENTS_GRANTED = {
  financial_data: {
    granted: true,
    version: "1.0",
    granted_at: "2026-08-19T12:00:00Z",
    withdrawable: true,
  },
};

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
  beforeEach(() => {
    useConsentsMock.mockReturnValue({
      data: CONSENTS_NOT_GRANTED,
      isLoading: false,
      isError: false,
    });
    grantMutateMock.mockReset();
    withdrawMutateMock.mockReset();
    toastErrorMock.mockClear();
    toastUndoMock.mockClear();
  });

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

  describe("блок «Согласия»", () => {
    it("согласие на финданные не дано — статус бейджем + кнопка «Дать согласие» + ссылка на документ", () => {
      useProfileMock.mockReturnValue(queryResult({ data: PROFILE }));
      render(<ProfilePage />);
      // "Не дано" — такой же по важности сигнал, как "не подтверждён" у email
      // (design-critic: раньше был обычным текстом, неотличимым от прочих значений).
      const status = screen.getByText("Не дано");
      expect(status).toHaveClass("fp-profile__badge");
      expect(screen.getByRole("button", { name: "Дать согласие" })).toBeInTheDocument();
      expect(
        screen.getByRole("link", { name: /Согласие на обработку финансовых/ }),
      ).toHaveAttribute("href", "/legal/financial-consent");
    });

    it("клик «Дать согласие» вызывает мутацию с типом financial_data", async () => {
      useProfileMock.mockReturnValue(queryResult({ data: PROFILE }));
      render(<ProfilePage />);
      await userEvent.click(screen.getByRole("button", { name: "Дать согласие" }));
      expect(grantMutateMock).toHaveBeenCalledWith("financial_data", expect.any(Object));
    });

    it("неудача выдачи согласия — тост с ошибкой (a11y-auditor: молча ничего не менялось)", async () => {
      grantMutateMock.mockImplementation((_type: string, opts?: { onError?: () => void }) => {
        opts?.onError?.();
      });
      useProfileMock.mockReturnValue(queryResult({ data: PROFILE }));
      render(<ProfilePage />);
      await userEvent.click(screen.getByRole("button", { name: "Дать согласие" }));
      expect(toastErrorMock).toHaveBeenCalledOnce();
    });

    it("согласие дано — статус «Дано» текстом (не бейдж), дата вторым планом, кнопка «Отозвать» danger", () => {
      useConsentsMock.mockReturnValue({
        data: CONSENTS_GRANTED,
        isLoading: false,
        isError: false,
      });
      useProfileMock.mockReturnValue(queryResult({ data: PROFILE }));
      render(<ProfilePage />);
      expect(screen.getByText("Дано")).not.toHaveClass("fp-profile__badge");
      const withdrawButton = screen.getByRole("button", { name: "Отозвать" });
      expect(withdrawButton).toHaveClass("fp-button--danger");
      expect(screen.queryByRole("button", { name: "Дать согласие" })).not.toBeInTheDocument();
    });

    it("клик «Отозвать» вызывает мутацию отзыва с типом financial_data", async () => {
      useConsentsMock.mockReturnValue({
        data: CONSENTS_GRANTED,
        isLoading: false,
        isError: false,
      });
      useProfileMock.mockReturnValue(queryResult({ data: PROFILE }));
      render(<ProfilePage />);
      await userEvent.click(screen.getByRole("button", { name: "Отозвать" }));
      expect(withdrawMutateMock).toHaveBeenCalledWith("financial_data", expect.any(Object));
    });

    it("успешный отзыв — undo-тост (тот же паттерн, что удаление обязательства/актива)", async () => {
      withdrawMutateMock.mockImplementation((_type: string, opts?: { onSuccess?: () => void }) => {
        opts?.onSuccess?.();
      });
      useConsentsMock.mockReturnValue({
        data: CONSENTS_GRANTED,
        isLoading: false,
        isError: false,
      });
      useProfileMock.mockReturnValue(queryResult({ data: PROFILE }));
      render(<ProfilePage />);
      await userEvent.click(screen.getByRole("button", { name: "Отозвать" }));
      expect(toastUndoMock).toHaveBeenCalledOnce();
    });

    it("неудача отзыва — тост с ошибкой", async () => {
      withdrawMutateMock.mockImplementation((_type: string, opts?: { onError?: () => void }) => {
        opts?.onError?.();
      });
      useConsentsMock.mockReturnValue({
        data: CONSENTS_GRANTED,
        isLoading: false,
        isError: false,
      });
      useProfileMock.mockReturnValue(queryResult({ data: PROFILE }));
      render(<ProfilePage />);
      await userEvent.click(screen.getByRole("button", { name: "Отозвать" }));
      expect(toastErrorMock).toHaveBeenCalledOnce();
    });

    it("withdrawable=false — кнопки «Отозвать» нет, но есть объяснение почему", () => {
      useConsentsMock.mockReturnValue({
        data: {
          financial_data: { ...CONSENTS_GRANTED.financial_data, withdrawable: false },
        },
        isLoading: false,
        isError: false,
      });
      useProfileMock.mockReturnValue(queryResult({ data: PROFILE }));
      render(<ProfilePage />);
      expect(screen.queryByRole("button", { name: "Отозвать" })).not.toBeInTheDocument();
      expect(screen.getByText(/нельзя отозвать/i)).toBeInTheDocument();
    });

    it("согласия ещё грузятся — блок не падает, кнопки нет", () => {
      useConsentsMock.mockReturnValue({ data: undefined, isLoading: true, isError: false });
      useProfileMock.mockReturnValue(queryResult({ data: PROFILE }));
      render(<ProfilePage />);
      expect(screen.queryByRole("button", { name: "Дать согласие" })).not.toBeInTheDocument();
      expect(screen.queryByRole("button", { name: "Отозвать" })).not.toBeInTheDocument();
    });
  });
});
