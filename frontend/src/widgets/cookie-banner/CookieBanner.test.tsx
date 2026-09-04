import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { CookieBanner } from "./CookieBanner";
import { readCookieChoice, saveCookieChoice, clearCookieChoice } from "./cookieConsent";

const { useLegalMock } = vi.hoisted(() => ({ useLegalMock: vi.fn() }));
vi.mock("@entities/legal", () => ({ useLegalDocuments: () => useLegalMock() }));

const LEGAL = {
  documents: {
    cookie_policy: {
      title: "Политика использования файлов cookie",
      version: "1.0",
      effective_from: "2026-07-29",
      url: "/legal/cookies",
    },
  },
  disclaimer_39fz: "FINPILOT не является инвестиционным советником.",
};

beforeEach(() => {
  vi.clearAllMocks();
  localStorage.clear();
  useLegalMock.mockReturnValue({ data: LEGAL, error: null, isLoading: false });
});

describe("CookieBanner — требование L6", () => {
  /* Требование сформулировано жёстко: РАЗДЕЛЬНЫЙ выбор. Одна кнопка «Ок» согласием
     не является — отказ должен стоить ровно одного клика, как и согласие. */
  it("предлагает оба варианта сразу, ни один не спрятан", () => {
    render(<CookieBanner />);
    expect(screen.getByRole("button", { name: "Принять всё" })).toBeVisible();
    expect(screen.getByRole("button", { name: "Только необходимые" })).toBeVisible();
  });

  it("ссылка на политику cookie ведёт на живой адрес (L7)", () => {
    render(<CookieBanner />);
    expect(screen.getByRole("link", { name: "Политика cookie" })).toHaveAttribute(
      "href",
      "/legal/cookies",
    );
  });

  it("после выбора баннер исчезает и не возвращается", async () => {
    const { unmount } = render(<CookieBanner />);
    await userEvent.click(screen.getByRole("button", { name: "Только необходимые" }));
    expect(screen.queryByRole("button", { name: "Принять всё" })).not.toBeInTheDocument();

    unmount();
    render(<CookieBanner />);
    expect(screen.queryByRole("button", { name: "Принять всё" })).not.toBeInTheDocument();
  });

  it("отказ сохраняется именно как отказ, а не как согласие", async () => {
    render(<CookieBanner />);
    await userEvent.click(screen.getByRole("button", { name: "Только необходимые" }));
    expect(readCookieChoice("1.0")?.choice).toBe("necessary");
  });

  /* 🔴 Согласие даётся на КОНКРЕТНУЮ редакцию. Молча переносить его на новый текст —
     ровно то, за что штрафуют. */
  it("смена редакции политики спрашивает заново", () => {
    saveCookieChoice("all", "1.0");
    useLegalMock.mockReturnValue({
      data: {
        ...LEGAL,
        documents: { cookie_policy: { ...LEGAL.documents.cookie_policy, version: "2.0" } },
      },
      error: null,
      isLoading: false,
    });
    render(<CookieBanner />);
    expect(screen.getByRole("button", { name: "Принять всё" })).toBeVisible();
  });

  /* До ответа сервера версия политики неизвестна — показать баннер значило бы мигнуть
     им у того, кто уже выбрал. */
  it("без ответа реестра баннер не показывается", () => {
    useLegalMock.mockReturnValue({ data: undefined, error: null, isLoading: true });
    render(<CookieBanner />);
    expect(screen.queryByRole("button", { name: "Принять всё" })).not.toBeInTheDocument();
  });
});

describe("cookieConsent — хранение выбора", () => {
  it("испорченное хранилище читается как отсутствие выбора, а не как согласие", () => {
    localStorage.setItem("fp-cookie-consent", "{не json");
    expect(readCookieChoice("1.0")).toBeNull();
  });

  it("чужое значение выбора не принимается", () => {
    localStorage.setItem("fp-cookie-consent", JSON.stringify({ choice: "yes", version: "1.0" }));
    expect(readCookieChoice("1.0")).toBeNull();
  });

  it("выбор можно забыть — «изменить решение»", () => {
    saveCookieChoice("all", "1.0");
    clearCookieChoice();
    expect(readCookieChoice("1.0")).toBeNull();
  });

  it("дата выбора сохраняется — её спросят при разбирательстве", () => {
    saveCookieChoice("all", "1.0");
    expect(readCookieChoice("1.0")?.decidedAt).not.toBe("");
  });
});
