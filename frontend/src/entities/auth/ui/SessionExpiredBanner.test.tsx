import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { SessionExpiredBanner } from "./SessionExpiredBanner";

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

/**
 * 🔴 Незакрытая половина гипотезы 7 (найдено сквозным сценарием пункта E, v9.5.0).
 *
 * v9.1.0 разобрал 401 на **загрузке** экрана: `query.isError` → `SessionExpiredPanel`.
 * Путь **отправки формы** остался прежним — `extractErrorMessage` сводит 401 к тексту
 * «Не получилось сохранить. Попробуйте ещё раз.», и повтор возвращает 401 бесконечно.
 *
 * Сценарий назван дословно в шапке `SessionExpiredPanel.test.tsx`: «через неделю после
 * входа человек заполняет форму кредита, жмёт „Сохранить“, получает совет проверить
 * интернет». Починили тогда экран, на котором он это читает, а не форму, в которой жмёт.
 *
 * Отдельный компонент от `SessionExpiredPanel`: тот занимает весь экран вместо контента,
 * здесь же форма с уже введёнными данными остаётся на месте — стирать её незачем,
 * а увести человека надо.
 */
describe("SessionExpiredBanner — выход из формы с умершей сессией", () => {
  it("объясняет, что дело не в связи", () => {
    render(<SessionExpiredBanner />);
    expect(screen.getByRole("alert").textContent).toMatch(/сесси/i);
  });

  it("🔴 даёт ссылку на вход, а не кнопку «Повторить»", () => {
    render(<SessionExpiredBanner />);
    expect(screen.getByRole("link", { name: /Войти заново/ })).toHaveAttribute(
      "href",
      "/login",
    );
    expect(screen.queryByRole("button", { name: /Повторить/ })).toBeNull();
  });

  it("не советует чинить интернет", () => {
    render(<SessionExpiredBanner />);
    expect(screen.getByRole("alert").textContent).not.toMatch(/соединение/i);
  });
});
