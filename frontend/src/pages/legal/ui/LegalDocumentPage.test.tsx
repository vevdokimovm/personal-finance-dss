import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { LegalDocumentPage } from "./LegalDocumentPage";

const { useDocumentsMock, useDocumentMock, paramsMock } = vi.hoisted(() => ({
  useDocumentsMock: vi.fn(),
  useDocumentMock: vi.fn(),
  paramsMock: vi.fn(),
}));

/* Подменяются ТОЛЬКО запросы. `legalLink` берётся настоящий: это чистая функция
   разбора адреса, и подменять её значило бы проверять собственную выдумку вместо
   того, как ссылка строится на самом деле. */
vi.mock("@entities/legal", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@entities/legal")>()),
  useLegalDocuments: () => useDocumentsMock(),
  useLegalDocument: (slug: string | null) => useDocumentMock(slug),
}));

vi.mock("@tanstack/react-router", () => ({
  useParams: () => paramsMock(),
  /* Роутер подменён целиком: поднимать его ради разметки экрана дороже, чем стоит.
     `Link` собирает href из маршрута и параметров так же, как настоящий, — иначе
     проверялась бы разметка, которой в продукте нет. */
  Link: ({
    children,
    to,
    params,
  }: {
    children: React.ReactNode;
    to: string;
    params?: Record<string, string>;
  }) => (
    <a href={Object.entries(params ?? {}).reduce((p, [k, v]) => p.replace(`$${k}`, v), to)}>
      {children}
    </a>
  ),
}));

const REGISTRY = {
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
  },
  disclaimer_39fz: "FINPILOT не является инвестиционным советником.",
};

const CONTENT = {
  slug: "privacy_policy",
  title: "Политика обработки персональных данных",
  version: "1.0",
  effective_from: "2026-07-29",
  url: "/legal/privacy",
  content: "# Политика\n\nНастоящая Политика определяет порядок обработки.\n\n## 1. Общие положения\n\n1.1. Оператором выступает сервис FINPILOT.",
};

function idle<T>(data: T) {
  return { data, isLoading: false, isError: false, error: null };
}

beforeEach(() => {
  vi.clearAllMocks();
  paramsMock.mockReturnValue({ doc: "privacy" });
  useDocumentsMock.mockReturnValue(idle(REGISTRY));
  useDocumentMock.mockReturnValue(idle(CONTENT));
});

describe("LegalDocumentPage — текст юридического документа", () => {
  /* 🔴 Адрес в ссылке (`/legal/privacy`) и ключ документа (`privacy_policy`) — РАЗНЫЕ
     строки. Сопоставление берётся из реестра, а не из зашитой в код таблицы: реестр
     на бэкенде и есть единственный источник правды об адресах. Появится седьмой
     документ — он откроется сам, без правки фронта. */
  it("разрешает документ по адресу через реестр, а не по зашитой таблице", () => {
    render(<LegalDocumentPage />);
    expect(useDocumentMock).toHaveBeenCalledWith("privacy_policy");
  });

  it("показывает текст документа", () => {
    render(<LegalDocumentPage />);
    expect(screen.getByText(/Настоящая Политика определяет порядок/)).toBeVisible();
  });

  /* Markdown рендерится как разметка: заголовки разделов должны быть заголовками,
     иначе документ на 97 строк читается сплошной простынёй и по нему нельзя
     ориентироваться ни глазами, ни скринридером ([A11Y-04]). */
  it("заголовки разделов — настоящие заголовки, а не строки текста", () => {
    render(<LegalDocumentPage />);
    expect(screen.getByRole("heading", { name: /1\. Общие положения/ })).toBeVisible();
  });

  /* Редакция и дата — юридически значимы: по ним доказывают, на что человек согласился. */
  it("показывает редакцию и дату вступления в силу", () => {
    render(<LegalDocumentPage />);
    expect(screen.getByText(/ред\. 1\.0 от 29\.07\.2026/)).toBeVisible();
  });

  /* 🔴 Пока текст едет, показывать пустую страницу нельзя: снаружи она неотличима от
     документа, которого нет, — и человек «ознакомился» с пустотой. */
  it("во время загрузки объясняет, что происходит", () => {
    useDocumentMock.mockReturnValue({ data: undefined, isLoading: true, isError: false });
    render(<LegalDocumentPage />);
    expect(screen.getByText(/Загружаем/)).toBeVisible();
  });

  /* Отказ сети на юридическом документе — не косметика: человек не может исполнить
     обязанность ознакомиться. Нужен и внятный текст, и путь дальше. */
  it("отказ объяснён и предлагает повтор", () => {
    useDocumentMock.mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
      error: new Error("network"),
    });
    render(<LegalDocumentPage />);
    expect(screen.getByText(/Не удалось загрузить документ/)).toBeVisible();
    expect(screen.getByRole("button", { name: /Попробовать снова/ })).toBeVisible();
  });

  /* Несуществующий адрес не должен молча показывать пустоту или крутить загрузку
     вечно: реестр пришёл, совпадения нет — это ответ, а не ожидание. */
  it("неизвестный адрес — честное «документа нет», а не вечная загрузка", () => {
    paramsMock.mockReturnValue({ doc: "no-such-document" });
    render(<LegalDocumentPage />);
    expect(screen.getByText(/Такого документа нет/)).toBeVisible();
    expect(useDocumentMock).toHaveBeenCalledWith(null);
  });

  /* Пока реестр не приехал, сопоставить адрес не с чем — но это ЗАГРУЗКА, а не
     «документа нет». Первая редакция путала эти состояния и показывала гостю
     «такого документа нет» на исправной ссылке из футера. */
  it("реестр ещё едет — это загрузка, а не отсутствие документа", () => {
    useDocumentsMock.mockReturnValue({ data: undefined, isLoading: true, isError: false });
    render(<LegalDocumentPage />);
    expect(screen.queryByText(/Такого документа нет/)).not.toBeInTheDocument();
    expect(screen.getByText(/Загружаем/)).toBeVisible();
  });

  /* Документ открывают по ссылке из футера, часто до входа. Уйти с него должно быть
     можно, не нажимая «назад» в браузере. */
  it("даёт вернуться в приложение", () => {
    render(<LegalDocumentPage />);
    expect(screen.getByRole("link", { name: /На главную/ })).toBeVisible();
  });

  /* 🔴 Разметка из markdown вставляется как HTML — значит, содержимое обязано быть
     обезврежено. Источник доверенный (файл в репозитории), но правило «доверенный
     источник» держится на дисциплине, а не на коде: один документ, отредактированный
     через будущую админку, превратил бы это в XSS. */
  it("скрипт в тексте документа не исполняется", () => {
    useDocumentMock.mockReturnValue(
      idle({ ...CONTENT, content: 'Текст <script>window.__pwned = 1</script> дальше.' }),
    );
    const { container } = render(<LegalDocumentPage />);
    expect(container.querySelector("script")).toBeNull();
    expect((window as unknown as { __pwned?: number }).__pwned).toBeUndefined();
  });

  /* 🔴 Диагноз берётся у сервера. Бэкенд на пропавший файл пакета отвечает 503
     «Обратитесь в поддержку», а первая редакция выбрасывала это и подставляла
     «проверьте соединение» — человек шёл чинить исправный Wi-Fi (design-critic). */
  it("сообщение сервера не подменяется своим", () => {
    useDocumentMock.mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
      error: { detail: "Текст документа временно недоступен. Обратитесь в поддержку." },
    });
    render(<LegalDocumentPage />);
    expect(screen.getByText(/Обратитесь в поддержку/)).toBeVisible();
    expect(screen.queryByText(/Проверьте соединение/)).not.toBeInTheDocument();
  });

  /* Заголовок вкладки (WCAG 2.4.2): три документа на трёх адресах назывались во
     вкладках одинаково, и сверять оферту с политикой в соседних вкладках было
     невозможно — а это обычный сценарий именно здесь. */
  it("название документа попадает в заголовок вкладки", () => {
    render(<LegalDocumentPage />);
    expect(window.document.title).toContain("Политика обработки персональных данных");
  });

  /* Переход между документами был в Jinja-версии («См. также») и потерялся при
     переносе: политику и оферту сверяют друг с другом ([IA-04]). */
  it("даёт перейти к соседнему документу, не возвращаясь в футер", () => {
    render(<LegalDocumentPage />);
    expect(screen.getByRole("link", { name: "Пользовательское соглашение" })).toBeVisible();
    // Себя в списке соседей быть не должно.
    expect(
      screen.queryAllByRole("link", { name: "Политика обработки персональных данных" }),
    ).toHaveLength(0);
  });

  /* 🔴 `display: block` на самой таблице снимает с неё роль таблицы для скринридера
     (WCAG 1.3.1). Прокрутка живёт на обёртке, и обёртка достижима с клавиатуры
     (WCAG 2.1.1) — прокрутить её мышью было можно, табом нельзя (a11y-auditor). */
  it("таблица остаётся таблицей, а прокрутка достижима с клавиатуры", () => {
    useDocumentMock.mockReturnValue(
      idle({ ...CONTENT, content: "| A | B |\n|---|---|\n| 1 | 2 |" }),
    );
    const { container } = render(<LegalDocumentPage />);
    expect(screen.getByRole("table")).toBeInTheDocument();
    const wrap = container.querySelector(".fp-legal-page__table-wrap");
    expect(wrap).toHaveAttribute("tabindex", "0");
  });

  /* Заголовок страницы должен остаться единственным `h1`: `stripLeadingHeading`
     вырезает собственный заголовок документа, и если он не совпадёт с ожидаемой
     формой (BOM, комментарий, фронтматтер), на экране окажутся два `h1`. */
  it("на экране ровно один заголовок первого уровня", () => {
    render(<LegalDocumentPage />);
    expect(screen.getAllByRole("heading", { level: 1 })).toHaveLength(1);
  });

  /* Возврат — до текста, а не после: внизу он оказывался за всей прокруткой
     документа, то есть на телефоне практически не существовал ([IA-02]). */
  it("возврат стоит выше текста документа", () => {
    const { container } = render(<LegalDocumentPage />);
    const back = container.querySelector(".fp-legal-page__back");
    const body = container.querySelector(".fp-legal-page__body");
    expect(back).not.toBeNull();
    expect(body).not.toBeNull();
    expect(back!.compareDocumentPosition(body!) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  });
});

