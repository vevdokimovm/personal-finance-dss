import { describe, expect, it } from "vitest";
import { readdirSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

/**
 * Маршруты: проверяется НАША логика в них, а не работа роутера.
 *
 * 🔴 **Почему не рендер каждого маршрута.** Файл маршрута — это декларация
 * `createFileRoute("/path")({ component })`. Тест вида «компонент подставился»
 * проверяет TanStack Router, а не нас: он не найдёт ни одного дефекта, который
 * может внести автор маршрута, зато поднимет процент покрытия. Это накрутка,
 * и заводить её нельзя — покрытие должно означать «проверено», а не «выполнено».
 *
 * **Что здесь ЕСТЬ нашего и потому проверяется:**
 *
 * 1. **`validateSearch`** — единственная логика, которую пишет автор маршрута.
 *    Она объявляет, какие параметры строки запроса маршрут принимает, и молча
 *    отбрасывает всё, что не описано. Ошибка в ней роняет `tsc` (типизированный
 *    `to`) либо теряет параметр в рантайме — ровно это и случилось в v9.2.0
 *    с `?redirect=` и `?ref=` у `/login`.
 * 2. **Полнота набора маршрутов** — каждый экран продукта обязан иметь файл.
 *    Отсутствующий маршрут делает экран недостижимым: класс `CONSENT-GATE-NO-UI`
 *    и `/join`, которого не существовало при живой серверной ссылке на него.
 */

const ROUTES_DIR = dirname(fileURLToPath(import.meta.url));

function routeFiles(): string[] {
  return readdirSync(ROUTES_DIR)
    .filter((name) => name.endsWith(".tsx") && !name.endsWith(".test.tsx"))
    .map((name) => name.replace(/\.tsx$/, ""));
}

describe("Набор маршрутов покрывает экраны продукта", () => {
  it("🔴 каждый экран навигации имеет свой файл маршрута", () => {
    /* Экран без маршрута недостижим кликом ниоткуда — тот же класс, что
       `CONSENT-GATE-NO-UI`: функция есть, пути к ней нет, и молчат обе стороны. */
    const files = routeFiles();
    for (const screen of [
      "dashboard",
      "transactions",
      "obligations",
      "goals",
      "planning",
      "profile",
      "spending",
      "household",
      "join",
      "banks",
      "insights",
    ]) {
      expect(files, `нет маршрута для экрана /${screen}`).toContain(screen);
    }
  });

  it("🔴 маршрут входа существует — на него ведут все ссылки восстановления", () => {
    expect(routeFiles()).toContain("login");
    expect(routeFiles()).toContain("register");
    expect(routeFiles()).toContain("reset-password");
  });
});

describe("validateSearch объявляет параметры, которые реально ходят", () => {
  function source(name: string): string {
    return readFileSync(join(ROUTES_DIR, `${name}.tsx`), "utf-8");
  }

  it("🔴 /login принимает и redirect, и ref", () => {
    /* Оба параметра ходили с v8.x и работали молча — роутер без `validateSearch`
       принимает любой набор. Первое же объявление превратило молчаливое согласие
       в проверяемый список, и объявить один, забыв второй, значит потерять его
       в рантайме: `RegisterPage` ходит `<Link to="/login" search={{ ref }}>`. */
    const text = source("login");
    expect(text).toContain("validateSearch");
    expect(text).toContain("redirect");
    expect(text).toContain("ref");
  });

  it("🔴 /reset-password принимает token из письма", () => {
    /* Ссылка собирается на сервере (`routes_auth.py::forgot_password`, `reset_url`).
       Не объявить параметр — значит выбросить токен и показать человеку форму,
       которая не может сработать. */
    const text = source("reset-password");
    expect(text).toContain("validateSearch");
    expect(text).toContain("token");
  });

  it("параметр объявлен НЕобязательным, а не required", () => {
    /* `required` дал бы 404 вместо экрана: страница сама объясняет отсутствие токена
       (fail-loud), и это полезнее пустой ошибки роутера. */
    expect(source("reset-password")).toMatch(/token\?:/);
  });
});
