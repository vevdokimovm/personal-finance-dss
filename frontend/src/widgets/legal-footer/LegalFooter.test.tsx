import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { LegalFooter } from "./LegalFooter";

const { useLegalMock } = vi.hoisted(() => ({ useLegalMock: vi.fn() }));
/* Подменяются только запросы: `legalLink` — чистая функция разбора адреса,
   и подменять её значило бы проверять свою выдумку вместо настоящей ссылки. */
vi.mock("@entities/legal", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@entities/legal")>()),
  useLegalDocuments: () => useLegalMock(),
}));
/* Роутер подменён: поднимать его ради футера дороже, чем стоит. `Link` собирает href
   из маршрута и параметров так же, как настоящий, — иначе проверялась бы разметка,
   которой в продукте нет. */
vi.mock("@tanstack/react-router", () => ({
  Link: ({
    children,
    to,
    params,
    ...rest
  }: {
    children: React.ReactNode;
    to: string;
    params?: Record<string, string>;
  }) => (
    <a
      href={Object.entries(params ?? {}).reduce((p, [k, v]) => p.replace(`$${k}`, v), to)}
      {...rest}
    >
      {children}
    </a>
  ),
}));


const LEGAL = {
  documents: {
    privacy_policy: {
      title: "Политика обработки персональных данных",
      version: "1.0",
      effective_from: "2026-07-29",
      url: "/legal/privacy",
    },
    terms_of_service: {
      title: "Пользовательское соглашение",
      version: "1.0",
      effective_from: "2026-07-29",
      url: "/legal/terms",
    },
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
  useLegalMock.mockReturnValue({ data: LEGAL, error: null, isLoading: false });
});

describe("LegalFooter — требование L7", () => {
  it("все документы реестра доступны ссылкой", () => {
    render(<LegalFooter />);
    expect(screen.getByRole("link", { name: /персональных данных/ })).toHaveAttribute(
      "href",
      "/legal/privacy",
    );
    expect(screen.getByRole("link", { name: /соглашение/ })).toHaveAttribute(
      "href",
      "/legal/terms",
    );
    expect(screen.getByRole("link", { name: /cookie/ })).toHaveAttribute("href", "/legal/cookies");
  });

  /* Список берётся из реестра, а не пишется руками: рукописная копия разошлась бы
     с бэкендом молча. Новый документ обязан появиться сам. */
  it("новый документ реестра появляется в футере без правки кода", () => {
    useLegalMock.mockReturnValue({
      data: {
        ...LEGAL,
        documents: {
          ...LEGAL.documents,
          data_processing: {
            title: "Поручение на обработку",
            version: "1.0",
            effective_from: "2026-09-01",
            url: "/legal/processing",
          },
        },
      },
      error: null,
      isLoading: false,
    });
    render(<LegalFooter />);
    expect(screen.getByRole("link", { name: /Поручение/ })).toBeVisible();
  });

  /* По 152-ФЗ согласие даётся на конкретную редакцию — человек должен видеть, какая
     действует сейчас. Дата в ru-RU, а не ISO ([CMP-04]). */
  it("редакция показана и записана по-русски", () => {
    render(<LegalFooter />);
    expect(screen.getByText(/ред\. 1\.0 от 29\.07\.2026/)).toBeVisible();
  });

  /* Все шесть документов делят одну редакцию — повторять одинаковую строку у каждого
     значит превращать футер в шум (design-critic). */
  it("одинаковая редакция сказана один раз, а не у каждого документа", () => {
    const { container } = render(<LegalFooter />);
    const editions = container.querySelectorAll(".fp-legal-footer__meta");
    expect(editions).toHaveLength(1);
  });

  it("разные редакции показаны поштучно", () => {
    useLegalMock.mockReturnValue({
      data: {
        ...LEGAL,
        documents: {
          ...LEGAL.documents,
          cookie_policy: { ...LEGAL.documents.cookie_policy, version: "2.0" },
        },
      },
      error: null,
      isLoading: false,
    });
    const { container } = render(<LegalFooter />);
    expect(container.querySelectorAll(".fp-legal-footer__meta").length).toBeGreaterThan(1);
  });

  /* 🔴 Сетевой сбой не вправе отключать юр-требование: ссылки обязаны быть на каждой
     странице. Редакции при этом не выдумываются — их знает только сервер. */
  it("при отказе реестра ссылки остаются, а редакции не выдумываются", () => {
    useLegalMock.mockReturnValue({ data: undefined, error: new Error("500"), isLoading: false });
    const { container } = render(<LegalFooter />);
    expect(screen.getByRole("link", { name: /персональных данных/ })).toHaveAttribute(
      "href",
      "/legal/privacy",
    );
    expect(container.querySelectorAll(".fp-legal-footer__meta")).toHaveLength(0);
  });

  /* Решение по cookie обязано быть обратимым. `clearCookieChoice` существовал и не
     вызывался нигде, кроме тестов — «изменить решение» было обещано и не существовало. */
  it("настройки cookie можно открыть заново", () => {
    render(<LegalFooter />);
    expect(screen.getByRole("button", { name: "Настройки cookie" })).toBeVisible();
  });
});
