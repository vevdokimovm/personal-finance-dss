import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { SessionExpiredPanel } from "./SessionExpiredPanel";
import { isSessionExpired } from "../lib/isSessionExpired";

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
 * 🔴 Остаток гипотезы 7 независимого эксперта.
 *
 * `JWT_TTL_HOURS = 168`, refresh-токена в проекте нет — значит 401 в середине работы
 * это регулярное событие, а не экзотика. Разбирал его **только** профиль; семь других
 * экранов показывали «Проверьте соединение и попробуйте ещё раз» с кнопкой «Повторить»,
 * которая возвращала бы 401 бесконечно.
 *
 * Одновременно `AppNav` убирает меню при любой ошибке — экран визуально «ломается»
 * без объяснения, и единственная подсказка «Войти» прячется в топбаре.
 *
 * Сценарий: через неделю после входа человек заполняет форму кредита, жмёт «Сохранить»,
 * получает совет проверить интернет — при работающем интернете.
 */
describe("isSessionExpired — распознаёт истёкшую сессию", () => {
  it("401 — это истёкшая сессия", () => {
    expect(isSessionExpired({ status: 401 })).toBe(true);
  });

  it("403 — НЕ истёкшая сессия", () => {
    /* 🔴 403 отдаёт гейт согласия на финданные, и у него свой экран
       (`ConsentRequiredPanel`) с кнопкой «Дать согласие». Спутать их значит
       предложить войти заново тому, кто уже вошёл. */
    expect(isSessionExpired({ status: 403 })).toBe(false);
  });

  it("сетевая ошибка — не истёкшая сессия", () => {
    /* Здесь «Повторить» осмысленно: связь могла восстановиться. Показать
       «войдите заново» при обрыве сети — отправить человека вводить пароль
       вместо того, чтобы нажать одну кнопку. */
    expect(isSessionExpired(new TypeError("Failed to fetch"))).toBe(false);
    expect(isSessionExpired(null)).toBe(false);
  });

  it("500 — не истёкшая сессия", () => {
    expect(isSessionExpired({ status: 500 })).toBe(false);
  });

  it("NotAuthenticatedError из useProfile — тоже истёкшая сессия", () => {
    /* 🔴 Два вида одной ошибки. Хуки на сгенерированном клиенте отдают объект
       со `status`; `useProfile` читает `response.status` сам (ему нужно отличить
       гостя от сбоя) и бросает свой класс. Распознавание только по `status`
       пропустило бы половину случаев — а именно профиль решает, показывать ли меню. */
    const error = Object.assign(new Error("401"), { name: "NotAuthenticatedError" });
    expect(isSessionExpired(error)).toBe(true);
  });

  it("обычный Error с текстом «401» истёкшей сессией НЕ считается", () => {
    /* Текст сообщения ничего не значит для кода: судить по нему — сравнивать строки
       вместо поведения. Именно так был написан прежний тест навигации. */
    expect(isSessionExpired(new Error("401"))).toBe(false);
  });
});

describe("SessionExpiredPanel — объясняет и даёт выход", () => {
  it("говорит, что сессия истекла, а не что сломался интернет", () => {
    render(<SessionExpiredPanel />);
    expect(screen.getByRole("alert")).toHaveTextContent(/сесси|войти заново|истек/i);
  });

  it("даёт ссылку на вход — единственный работающий выход", () => {
    /* Кнопка «Повторить» на 401 возвращает 401 бесконечно: это не восстановление,
       а петля. Выход один — войти заново. */
    render(<SessionExpiredPanel />);
    const link = screen.getByRole("link", { name: /войти/i });
    expect(link).toHaveAttribute("href", expect.stringContaining("/login"));
  });

  it("возвращает человека туда, где он был", () => {
    /* Без `redirect` он после входа попадёт на дашборд и будет искать экран,
       с которого его выбило, — а на нём осталась несохранённая работа. */
    render(<SessionExpiredPanel redirectTo="/obligations" />);
    const link = screen.getByRole("link", { name: /войти/i });
    expect(link.getAttribute("href")).toContain("redirect=%2Fobligations");
  });

  it("предупреждает, что несохранённое потеряется", () => {
    /* Человек заполнял форму кредита; уходя на вход, он потеряет введённое.
       Молчать об этом — дать ему уйти и обнаружить потерю после возврата. */
    render(<SessionExpiredPanel />);
    expect(screen.getByRole("alert")).toHaveTextContent(/несохранённ|заполненн|потеря/i);
  });
});
