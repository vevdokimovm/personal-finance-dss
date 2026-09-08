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

/* `SessionExpiredPanel` внутри секции ведёт человека на `/login` через `Link`, а тот
   без роутера падает на `isServer`. Тест проверяет НАЛИЧИЕ выхода, а не работу роутера —
   поэтому ссылка подменяется простым якорем, как в `SessionExpiredPanel.test.tsx`. */
vi.mock("@tanstack/react-router", async () => {
  const actual =
    await vi.importActual<typeof import("@tanstack/react-router")>("@tanstack/react-router");
  return {
    ...actual,
    Link: ({ children, to }: { children: React.ReactNode; to: string }) => (
      <a href={to}>{children}</a>
    ),
  };
});

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

/**
 * Ветки отказа — непокрытый остаток секции.
 *
 * 🔴 **Отзыв согласия на финданные закрывает шесть роутеров разом** (`_FIN`).
 * Если запрос упал, а мы промолчали, человек уверен, что отозвал, — и продолжает
 * пользоваться продуктом, считая свои данные защищёнными. Это не UX-мелочь,
 * а расхождение между тем, что он решил, и тем, что произошло.
 */
describe("ConsentsSection — что видно, когда действие не удалось", () => {
  it("отказ при выдаче согласия сообщается", async () => {
    useConsentsMock.mockReturnValue({ data: ALL_CONSENTS, isLoading: false, error: null });
    grantMock.mockImplementation((_type: string, opts?: { onError?: () => void }) =>
      opts?.onError?.(),
    );
    render(<ConsentsSection />);

    await userEvent.click(screen.getByRole("button", { name: /Дать согласие: Финансовые/ }));
    expect(toastError).toHaveBeenCalled();
  });

  it("🔴 отказ при отзыве сообщается — иначе человек думает, что отозвал", async () => {
    useConsentsMock.mockReturnValue({ data: ALL_CONSENTS, isLoading: false, error: null });
    withdrawMock.mockImplementation((_type: string, opts?: { onError?: () => void }) =>
      opts?.onError?.(),
    );
    render(<ConsentsSection />);

    await userEvent.click(screen.getByRole("button", { name: /Отозвать согласие: Рекламная/ }));
    expect(toastError).toHaveBeenCalled();
    expect(toastUndo).not.toHaveBeenCalled();
  });

  it("🔴 отказ при ВОССТАНОВЛЕНИИ через «Вернуть» тоже сообщается", async () => {
    /* Кнопка отмены создаёт впечатление обратимости. Если восстановление упало
       молча, человек уверен, что согласие вернулось, и не даст его заново —
       а шесть роутеров останутся закрытыми. */
    useConsentsMock.mockReturnValue({ data: ALL_CONSENTS, isLoading: false, error: null });
    withdrawMock.mockImplementation((_type: string, opts?: { onSuccess?: () => void }) =>
      opts?.onSuccess?.(),
    );
    grantMock.mockImplementation((_type: string, opts?: { onError?: () => void }) =>
      opts?.onError?.(),
    );
    render(<ConsentsSection />);

    await userEvent.click(screen.getByRole("button", { name: /Отозвать согласие: Рекламная/ }));
    expect(toastUndo).toHaveBeenCalled();
    // Нажимаем «Вернуть» — ToastProvider в юнит-тесте не смонтирован, зовём обработчик.
    toastUndo.mock.calls[0][1]();
    expect(toastError).toHaveBeenCalled();
  });
});

describe("ConsentsSection — ошибка не прячет право по 152-ФЗ молча", () => {
  /* 🔴 Гипотеза 4 независимого эксперта, 08.09.2026.
     Было: `if (query.isLoading || query.isError || !query.data) return null` —
     блок управления согласиями исчезал при ЛЮБОЙ ошибке, без единого слова.

     Это единственный путь отзыва согласия в интерфейсе, и `routes_consents.py`
     прямо пишет: невозможность отозвать согласие — нарушение 152-ФЗ, а не дефект
     интерфейса. Молчаливое исчезновение хуже ошибки: человек не понимает, что
     функция вообще существует, и не может отличить «права нет» от «сеть моргнула». */

  beforeEach(() => {
    useLegalMock.mockReturnValue({ data: [], isLoading: false });
  });

  it("🔴 при истёкшей сессии объясняет и даёт выход, а не исчезает", () => {
    useConsentsMock.mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
      error: { status: 401 },
    });

    render(<ConsentsSection />);

    expect(screen.getByText(/Сессия истекла/)).toBeInTheDocument();
  });

  it("🔴 при обычной ошибке говорит об этом и даёт повторить", async () => {
    const refetch = vi.fn();
    useConsentsMock.mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
      error: { status: 500 },
      refetch,
    });

    render(<ConsentsSection />);

    expect(screen.getByRole("alert")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: /Повторить/ }));
    expect(refetch).toHaveBeenCalled();
  });

  it("во время загрузки не показывает ни ошибку, ни пустоту", () => {
    useConsentsMock.mockReturnValue({ data: undefined, isLoading: true, isError: false });

    render(<ConsentsSection />);

    expect(screen.queryByRole("alert")).toBeNull();
  });
});
