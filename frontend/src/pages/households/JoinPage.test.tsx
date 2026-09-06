import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { JoinPage } from "./JoinPage";

/**
 * Экран приёма приглашения — `/join?token=…`.
 *
 * 🔴 **Его не существовало вовсе**, хотя бэкенд строил ссылку на него с самого начала
 * (`routes_households.py::_invite_url`): владелец копировал адрес приглашаемому,
 * и приглашение вело в никуда. Второй случай класса H12 — ссылка, собранная на сервере,
 * без роута на фронте.
 *
 * 🔴 **Гостю показывается путь, а не отказ, и токен переживает вход по-настоящему.**
 * Первая редакция обещала сохранность токена ТЕКСТОМ, а код терял адрес на переходе —
 * обещание без механизма. Поэтому проверка ниже смотрит на `search` ссылок «Войти»
 * и «Зарегистрироваться», а не на слова в панели.
 *
 * 🔴 **Приглашение принимается САМО, без второй кнопки «подтвердите».** Человек уже
 * сделал осознанное действие — открыл присланную ссылку; просить подтверждение
 * второй раз значит добавить шаг без смысла. Автоматический вызов легко сломать
 * правкой зависимостей эффекта, и заметить это можно только тестом.
 */

const acceptMutate = vi.fn();
let acceptPending = false;
let profileState: { data?: unknown; error?: unknown; isLoading: boolean } = {
  data: { id: "u-1" },
  error: null,
  isLoading: false,
};
let searchState: { token?: string } = { token: "tok-123" };

vi.mock("@tanstack/react-router", () => ({
  useSearch: () => searchState,
  Link: ({
    to,
    search,
    children,
  }: {
    to: string;
    search?: Record<string, string>;
    children: React.ReactNode;
  }) => {
    /* Мок собирает href из `to` и `search` — как настоящий роутер. Брать только `to`
       значило бы потерять `redirect` и не заметить возвращения того самого дефекта,
       ради которого экран и переписывали. */
    const query = new URLSearchParams(search ?? {}).toString();
    return <a href={query ? `${to}?${query}` : to}>{children}</a>;
  },
}));

vi.mock("@entities/households", () => ({
  useAcceptInvite: () => ({ mutate: acceptMutate, isPending: acceptPending }),
}));

vi.mock("@entities/profile", () => ({
  useProfile: () => profileState,
}));

beforeEach(() => {
  vi.clearAllMocks();
  acceptPending = false;
  profileState = { data: { id: "u-1" }, error: null, isLoading: false };
  searchState = { token: "tok-123" };
});

describe("JoinPage — ссылка без кода", () => {
  it("объясняет, что именно не так со ссылкой", () => {
    /* «Ошибка» тут бесполезна: человек не может починить чужую ссылку, не зная,
       чего в ней не хватает. Панель называет признак — «?token=…». */
    searchState = {};
    render(<JoinPage />);

    expect(screen.getByRole("alert")).toHaveTextContent(/token/i);
    expect(acceptMutate).not.toHaveBeenCalled();
  });
});

describe("JoinPage — гость", () => {
  beforeEach(() => {
    profileState = { data: undefined, error: null, isLoading: false };
  });

  it("🔴 обе ссылки уносят токен в redirect", async () => {
    render(<JoinPage />);

    const login = screen.getByRole("link", { name: /войти/i });
    const register = screen.getByRole("link", { name: /регистр/i });
    for (const link of [login, register]) {
      const href = link.getAttribute("href") ?? "";
      expect(href).toContain("redirect=");
      // Токен закодирован целиком: `/join?token=tok-123` внутри параметра.
      expect(decodeURIComponent(href)).toContain("/join?token=tok-123");
    }
  });

  it("приглашение не принимается за гостя", () => {
    /* Принять от имени несуществующего аккаунта нечем — запрос ушёл бы в 401
       и человек увидел бы отказ вместо предложения войти. */
    render(<JoinPage />);
    expect(acceptMutate).not.toHaveBeenCalled();
  });

  it("гостем считается и тот, у кого сессия истекла", () => {
    /* `profile.error` при живом `data` из кэша — истёкшая сессия. Показать ей
       «принимаем приглашение» значит крутить запрос, который вернёт 401. */
    profileState = { data: { id: "u-1" }, error: { status: 401 }, isLoading: false };
    render(<JoinPage />);

    expect(screen.getByRole("link", { name: /войти/i })).toBeInTheDocument();
    expect(acceptMutate).not.toHaveBeenCalled();
  });
});

describe("JoinPage — вошедший", () => {
  it("🔴 приглашение принимается САМО, без второй кнопки", async () => {
    render(<JoinPage />);
    await waitFor(() => expect(acceptMutate).toHaveBeenCalled());
    expect(acceptMutate.mock.calls[0][0]).toBe("tok-123");
  });

  it("успех ведёт на экран семейного доступа", async () => {
    acceptMutate.mockImplementation((_token, opts) => opts?.onSuccess?.());
    render(<JoinPage />);

    await waitFor(() => expect(screen.getByRole("status")).toBeInTheDocument());
    expect(screen.getByRole("link", { name: /семейный доступ/i })).toHaveAttribute(
      "href",
      "/household",
    );
  });

  it("🔴 отказ объясняет причины ЧЕЛОВЕЧЕСКИ и даёт выход", async () => {
    /* Причин три — устарела, отозвана, использована, — и человеку важен не код
       ответа, а что делать дальше: попросить новую ссылку ([ST-04]). */
    acceptMutate.mockImplementation((_token, opts) => opts?.onError?.());
    render(<JoinPage />);

    await waitFor(() => expect(screen.getByRole("alert")).toBeInTheDocument());
    const panel = screen.getByRole("alert");
    expect(panel).toHaveTextContent(/устареть|отозван|использован/i);
    expect(screen.getByRole("link", { name: /семейному доступу/i })).toBeInTheDocument();
  });

  it("пока идёт приём — состояние ожидания, а не пустой экран", () => {
    /* Ищем по ПОДПИСИ, а не по роли: `role="status"` на экране может быть несколько
       (ожидание профиля и ожидание приёма), и `getByRole` падает на неоднозначности,
       сообщая про тест, а не про предмет. */
    acceptPending = true;
    render(<JoinPage />);
    expect(screen.getByLabelText("Принимаем приглашение")).toBeInTheDocument();
  });

  it("пока грузится профиль — тоже ожидание, и приглашение ещё не принимается", () => {
    /* Принять до того, как известно, кто перед нами, значит рискнуть отправить
       запрос за гостя и сжечь одноразовый токен приглашения. */
    profileState = { data: undefined, error: null, isLoading: true };
    render(<JoinPage />);

    expect(screen.getByLabelText("Проверяем вход")).toBeInTheDocument();
    expect(acceptMutate).not.toHaveBeenCalled();
  });
});
