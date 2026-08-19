import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ConsentRequiredPanel } from "./ConsentRequiredPanel";
import type { ConsentRequiredDetail } from "@shared/lib/api/extractErrorMessage";

const grantMutateMock = vi.fn();
const grantStateMock = { isPending: false };
const { toastErrorMock } = vi.hoisted(() => ({ toastErrorMock: vi.fn() }));

vi.mock("../api/useConsents", () => ({
  useGrantConsent: () => ({
    mutate: grantMutateMock,
    get isPending() {
      return grantStateMock.isPending;
    },
  }),
}));

vi.mock("@shared/ui", async () => {
  const actual = await vi.importActual<typeof import("@shared/ui")>("@shared/ui");
  return { ...actual, toast: { ...actual.toast, error: toastErrorMock } };
});

const DETAIL: ConsentRequiredDetail = {
  consentType: "financial_data",
  message: "Для работы с финансовыми данными нужно отдельное согласие на их обработку.",
  documentTitle: "Согласие на обработку финансовых данных",
  documentUrl: "/legal/financial-consent",
};

describe("ConsentRequiredPanel", () => {
  beforeEach(() => {
    grantStateMock.isPending = false;
    grantMutateMock.mockReset();
  });

  it("показывает объяснение и ссылку на документ отдельной строкой (не внутри текста ошибки)", () => {
    render(<ConsentRequiredPanel detail={DETAIL} onGranted={vi.fn()} />);
    expect(screen.getByRole("alert")).toBeInTheDocument();
    // Полное accessible name включает sr-only «открывается в новой вкладке» (a11y-auditor).
    const link = screen.getByRole("link", { name: new RegExp(DETAIL.documentTitle) });
    expect(link).toHaveAttribute("href", "/legal/financial-consent");
  });

  it("текст панели НЕ отправляет туда же, куда ведёт кнопка (без «в настройках профиля»)", () => {
    // design-critic, этот батч: кнопка «Дать согласие» уже делает то же самое здесь и
    // сейчас — текст, отправляющий «в настройки профиля», противоречит кнопке под ним.
    render(<ConsentRequiredPanel detail={DETAIL} onGranted={vi.fn()} />);
    expect(screen.getByRole("alert")).not.toHaveTextContent("в настройках профиля");
  });

  it("кнопка «Дать согласие» вызывает мутацию с нужным consentType", async () => {
    render(<ConsentRequiredPanel detail={DETAIL} onGranted={vi.fn()} />);
    await userEvent.click(screen.getByRole("button", { name: "Дать согласие" }));
    expect(grantMutateMock).toHaveBeenCalledWith("financial_data", expect.any(Object));
  });

  it("успешная выдача согласия вызывает onGranted (перезапрос упавшего списка)", async () => {
    const onGranted = vi.fn();
    grantMutateMock.mockImplementation((_type: string, opts?: { onSuccess?: () => void }) => {
      opts?.onSuccess?.();
    });
    render(<ConsentRequiredPanel detail={DETAIL} onGranted={onGranted} />);
    await userEvent.click(screen.getByRole("button", { name: "Дать согласие" }));
    expect(onGranted).toHaveBeenCalledOnce();
  });

  it("неудача мутации — тост с ошибкой, не тишина (a11y-auditor: молча ничего не менялось)", async () => {
    grantMutateMock.mockImplementation((_type: string, opts?: { onError?: () => void }) => {
      opts?.onError?.();
    });
    render(<ConsentRequiredPanel detail={DETAIL} onGranted={vi.fn()} />);
    await userEvent.click(screen.getByRole("button", { name: "Дать согласие" }));
    expect(toastErrorMock).toHaveBeenCalledOnce();
  });

  it("во время мутации — aria-disabled (не нативный disabled, иначе фокус проваливается в <body>)", () => {
    grantStateMock.isPending = true;
    render(<ConsentRequiredPanel detail={DETAIL} onGranted={vi.fn()} />);
    const button = screen.getByRole("button", { name: "Даём согласие…" });
    expect(button).toHaveAttribute("aria-disabled", "true");
    expect(button).not.toBeDisabled();
  });

  it("повторный клик во время мутации не отправляет вторую мутацию", async () => {
    grantStateMock.isPending = true;
    render(<ConsentRequiredPanel detail={DETAIL} onGranted={vi.fn()} />);
    await userEvent.click(screen.getByRole("button", { name: "Даём согласие…" }));
    expect(grantMutateMock).not.toHaveBeenCalled();
  });

  it("без documentUrl — ссылка не рендерится", () => {
    render(
      <ConsentRequiredPanel
        detail={{ ...DETAIL, documentUrl: "", documentTitle: "" }}
        onGranted={vi.fn()}
      />,
    );
    expect(screen.queryByRole("link")).not.toBeInTheDocument();
  });
});
