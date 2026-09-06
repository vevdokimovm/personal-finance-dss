import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ConsentsSection } from "./ConsentsSection";

const { useConsentsMock, useLegalMock, grantMock, withdrawMock, toastError, toastUndo } =
  vi.hoisted(() => ({
    useConsentsMock: vi.fn(),
    useLegalMock: vi.fn(),
    grantMock: vi.fn(),
    withdrawMock: vi.fn(),
    toastError: vi.fn(),
    toastUndo: vi.fn(),
  }));

vi.mock("@entities/consents", () => ({
  useConsents: () => useConsentsMock(),
  useGrantConsent: () => ({ mutate: grantMock, isPending: false }),
  useWithdrawConsent: () => ({ mutate: withdrawMock, isPending: false }),
}));

vi.mock("@entities/legal", () => ({ useLegalDocuments: () => useLegalMock() }));

vi.mock("@shared/ui", async () => {
  const actual = await vi.importActual<typeof import("@shared/ui")>("@shared/ui");
  return { ...actual, toast: { ...actual.toast, error: toastError, undo: toastUndo } };
});

/** Все три типа, как их отдаёт `/consents` — включая невыданные. */
const ALL_CONSENTS = {
  personal_data: {
    granted: true,
    version: "1.0",
    granted_at: "2026-01-15T10:00:00",
    withdrawable: false,
  },
  financial_data: { granted: false, version: "1.0", granted_at: null, withdrawable: true },
  marketing: {
    granted: true,
    version: "1.0",
    granted_at: "2026-02-01T10:00:00",
    withdrawable: true,
  },
};

const LEGAL = {
  documents: {
    personal_data: {
      title: "Согласие на обработку персональных данных",
      version: "1.0",
      effective_from: "2026-07-29",
      url: "/legal/consent",
    },
    financial_data: {
      title: "Согласие на обработку финансовых данных",
      version: "1.0",
      effective_from: "2026-07-29",
      url: "/legal/financial-consent",
    },
    marketing: {
      title: "Согласие на рекламную рассылку",
      version: "1.0",
      effective_from: "2026-07-29",
      url: "/legal/marketing-consent",
    },
  },
  disclaimer_39fz: "FINPILOT не является инвестиционным советником.",
};

beforeEach(() => {
  vi.clearAllMocks();
  useConsentsMock.mockReturnValue({ data: ALL_CONSENTS, isLoading: false, isError: false });
  useLegalMock.mockReturnValue({ data: LEGAL, error: null, isLoading: false });
});

describe("ConsentsSection — требование L3", () => {
  /* 🔴 Первая редакция знала ровно ОДНО согласие — `financial_data`. Остальные два
     человек не видел вовсе: отозвать маркетинговое было невозможно, хотя 152-ФЗ даёт
     на это право. */
  it("показывает ВСЕ согласия, а не одно", () => {
    render(<ConsentsSection />);
    expect(screen.getByText("Персональные данные")).toBeVisible();
    expect(screen.getByText("Финансовые данные")).toBeVisible();
    expect(screen.getByText("Рекламная рассылка")).toBeVisible();
  });

  it("новый тип согласия появляется сам, без правки кода", () => {
    useConsentsMock.mockReturnValue({
      data: {
        ...ALL_CONSENTS,
        biometrics: { granted: false, version: "1.0", granted_at: null, withdrawable: true },
      },
      isLoading: false,
      isError: false,
    });
    render(<ConsentsSection />);
    // Названия для нового типа ещё нет — показываем ключ, но НЕ прячем строку:
    // спрятанное согласие человек не сможет ни выдать, ни отозвать.
    expect(screen.getByText("biometrics")).toBeVisible();
  });

  it("статус передан словом, а не только цветом бейджа (A11Y-07)", () => {
    render(<ConsentsSection />);
    expect(screen.getByText("Не дано")).toHaveClass("fp-profile__badge");
    expect(screen.getAllByText("Дано")).toHaveLength(2);
  });

  it("ссылка на документ ведёт по адресу из реестра, а не зашита в код", () => {
    render(<ConsentsSection />);
    expect(screen.getByRole("link", { name: /Согласие на обработку финансовых/ })).toHaveAttribute(
      "href",
      "/legal/financial-consent",
    );
    expect(screen.getByRole("link", { name: /рекламную рассылку/ })).toHaveAttribute(
      "href",
      "/legal/marketing-consent",
    );
  });

  it("выдача согласия уходит с нужным типом", async () => {
    render(<ConsentsSection />);
    await userEvent.click(screen.getByRole("button", { name: /Дать согласие: Финансовые/ }));
    expect(grantMock.mock.calls[0][0]).toBe("financial_data");
  });

  it("отзыв согласия уходит с нужным типом", async () => {
    render(<ConsentsSection />);
    await userEvent.click(screen.getByRole("button", { name: /Отозвать согласие: Рекламная/ }));
    expect(withdrawMock.mock.calls[0][0]).toBe("marketing");
  });

  /* Согласие-основание отозвать нельзя иначе как удалением аккаунта — сервер ответит
     409. Кнопка, которая гарантированно откажет, это тупик ([IA-04]). */
  it("у неотзываемого согласия кнопки отзыва нет, но есть объяснение", () => {
    render(<ConsentsSection />);
    expect(
      screen.queryByRole("button", { name: /Отозвать согласие: Персональные/ }),
    ).not.toBeInTheDocument();
    expect(screen.getByText(/нельзя отозвать без удаления аккаунта/)).toBeVisible();
  });

  it("отзыв предлагает отмену — он закрывает шесть роутеров разом", async () => {
    withdrawMock.mockImplementation((_type, opts) => opts?.onSuccess?.());
    render(<ConsentsSection />);
    await userEvent.click(screen.getByRole("button", { name: /Отозвать согласие: Рекламная/ }));
    expect(toastUndo).toHaveBeenCalled();
    toastUndo.mock.calls[0][1]();
    expect(grantMock.mock.calls[0][0]).toBe("marketing");
  });

  it("редакция документа видна — согласие даётся на конкретный текст", () => {
    render(<ConsentsSection />);
    expect(screen.getAllByText("ред. 1.0")).toHaveLength(3);
  });

  it("согласия ещё грузятся — блок не падает и кнопок нет", () => {
    useConsentsMock.mockReturnValue({ data: undefined, isLoading: true, isError: false });
    render(<ConsentsSection />);
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });

  /* Реестр документов — второстепенный источник: без него статусы и кнопки обязаны
     работать, пропадают только ссылки на тексты. */
  it("без реестра документов согласия всё равно управляемы", () => {
    useLegalMock.mockReturnValue({ data: undefined, error: new Error("500"), isLoading: false });
    render(<ConsentsSection />);
    expect(screen.getByRole("button", { name: /Дать согласие: Финансовые/ })).toBeVisible();
  });
});
