import { expect, test } from "@playwright/test";

/**
 * Гостевая песочница в настоящем браузере (v8.46.0).
 *
 * Юнит-тесты проверяют разметку при подменённых хуках. Только браузер показывает, что
 * гость реально доходит до портретов: пустой дашборд → песочница → подтверждение →
 * загрузка. Именно этот путь и потерялся при переносе фронта на React, причём незаметно
 * (PIT-020: проверки были, покрывали не то).
 *
 * Сеть мокается на границе `/api`, как в остальных спеках: `playwright.config.ts`
 * поднимает только фронт.
 */

const CASES = {
  cases: [
    {
      key: "anna",
      n: "1",
      name: "Анна Петрова, 36",
      role: "Маркетолог · Москва",
      tag: "Пограничный",
      accent: "amber",
      situation: "Доход 180 000 ₽, ипотека, автокредит и рассрочка, несколько целей.",
      expect: "Сначала гасим самый дорогой кредит, запас держим не ниже нормы.",
    },
    {
      key: "mikhail",
      n: "3",
      name: "Михаил, 49",
      role: "Своя мастерская · Казань",
      tag: "Критический",
      accent: "red",
      situation: "Четыре кредита, платежи съедают почти весь доход.",
      expect: "Система честно откажется советовать и покажет разбор ситуации.",
    },
  ],
  keys: ["anna", "mikhail"],
};

/** Пустой план: доход и расход нули — та ветка дашборда, где живёт песочница. */
const EMPTY_PLAN = {
  risk_profile: "Сбалансированный",
  indicators: { Rt: 0, Lt: 0, Dt: 0, BLR: 0, It: 0, Et: 0, SigmaP: 0 },
  top3: [],
  ranked: [],
  input_summary: { income: 0, expense: 0, obligations: 0, goals: 0 },
};

async function stubGuest(page: import("@playwright/test").Page) {
  // Гость: /auth/me отвечает 401 — это ожидаемый ответ, не сбой.
  await page.route("**/api/auth/me", (route) => route.fulfill({ status: 401, json: {} }));
  await page.route("**/api/planning/calculate**", (route) => route.fulfill({ json: EMPTY_PLAN }));
  await page.route("**/api/planning/forecast**", (route) =>
    route.fulfill({ json: { points: [], r_bench: 0.16, r_bench_source: "cbr" } }),
  );
  await page.route("**/api/demo/cases", (route) => route.fulfill({ json: CASES }));
  await page.route("**/api/notifications/unread-count", (route) =>
    route.fulfill({ json: { unread_count: 0 } }),
  );
  await page.route("**/api/legal/documents", (route) =>
    route.fulfill({ json: { documents: {}, disclaimer_39fz: "" } }),
  );
}

test("гость с пустым дашбордом видит демо-портреты", async ({ page }) => {
  await stubGuest(page);
  await page.goto("/dashboard");

  await expect(page.getByRole("heading", { name: /Посмотреть на примере/ })).toBeVisible();
  await expect(page.getByText(/1\. Анна Петрова, 36/)).toBeVisible();
  // «Что покажет расчёт» — до нажатия: иначе выбор портрета это лотерея.
  await expect(page.getByText(/Сначала гасим самый дорогой кредит/)).toBeVisible();
});

test("🔴 загрузка портрета требует подтверждения и честно называет последствие", async ({
  page,
}) => {
  await stubGuest(page);
  let loadCalled = false;
  await page.route("**/api/demo/load**", (route) => {
    loadCalled = true;
    return route.fulfill({ json: { detail: "ok" } });
  });

  await page.goto("/dashboard");
  await page.getByRole("button", { name: /Анна Петрова/ }).click();

  // Запрос НЕ ушёл: `/demo/load` стирает всё, что гость внёс, мимо отмены.
  expect(loadCalled).toBe(false);
  await expect(page.getByRole("dialog")).toBeVisible();
  await expect(page.getByText(/будет удалено|вернуть это будет нельзя/)).toBeVisible();

  await page.getByRole("button", { name: /Заменить и показать/ }).click();
  await expect.poll(() => loadCalled).toBe(true);
});

test("отказ от подтверждения ничего не грузит", async ({ page }) => {
  await stubGuest(page);
  let loadCalled = false;
  await page.route("**/api/demo/load**", (route) => {
    loadCalled = true;
    return route.fulfill({ json: { detail: "ok" } });
  });

  await page.goto("/dashboard");
  await page.getByRole("button", { name: /Анна Петрова/ }).click();
  await page.getByRole("button", { name: /Отмена/ }).click();

  await expect(page.getByRole("dialog")).toBeHidden();
  expect(loadCalled).toBe(false);
});

test("вошедшему песочница не показывается", async ({ page }) => {
  await stubGuest(page);
  // Перекрываем: теперь пользователь вошёл, и сервер отдал бы демо 403.
  await page.route("**/api/auth/me", (route) =>
    route.fulfill({ json: { id: "u1", email: "user@test.io", created_at: "2026-01-01T00:00:00" } }),
  );

  await page.goto("/dashboard");
  await expect(page.getByText(/Пока нет данных для обзора/)).toBeVisible();
  await expect(page.getByRole("heading", { name: /Посмотреть на примере/ })).toBeHidden();
});
