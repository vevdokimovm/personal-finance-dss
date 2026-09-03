import { expect, test } from "@playwright/test";

/**
 * История планов в настоящем браузере (v8.34.0).
 *
 * Юнит-тесты мокают сущность целиком и потому не проверяют главного: что подтверждение
 * удаления действительно ловит фокус и закрывается по Esc (Radix Dialog), и что после
 * удаления фокус не проваливается в <body>. Именно это отличает «диалог показывается»
 * от «диалогом можно пользоваться с клавиатуры».
 */

const PROFILE = {
  id: "u1",
  email: "anna@example.com",
  display_name: "Анна",
  email_verified: true,
  created_at: "2026-01-15",
};

const PLAN = {
  risk_profile: "Сбалансированный",
  indicators: { Rt: 39500, Lt: 0, Dt: 0.3472, BLR: 3.4, It: 180000, Et: 78000, SigmaP: 62500 },
  top3: [
    {
      id: "a0100",
      name: "Всё в резерв",
      x_obligations: 0,
      x_reserve: 39500,
      x_goals: 0,
      utility: 0.8,
    },
  ],
  ranked: [],
  admissible_count: 1,
  alternatives_total: 1,
  input_summary: {
    income: 180000,
    expense: 78000,
    bliq: 0,
    transactions_count: 12,
    obligations_count: 1,
    goals_count: 0,
  },
};

const SNAPSHOT = {
  id: 7,
  created_at: "2026-09-01T10:00:00",
  risk_profile: "Сбалансированный",
  indicators: { Rt: 39500, Lt: 3.4, Dt: 0.3472, BLR: 3.4 },
  best: {
    name: "Всё в резерв",
    x_obligations: 0,
    x_reserve: 39500,
    x_goals: 0,
    utility: 0.8,
  },
  note: "до отпуска",
};

async function setup(page: import("@playwright/test").Page, history: unknown[]) {
  await page.route("**/api/auth/me", (route) => route.fulfill({ json: PROFILE }));
  await page.route("**/api/notifications/unread-count", (route) =>
    route.fulfill({ json: { unread_count: 0 } }),
  );
  await page.route("**/api/planning/calculate", (route) => route.fulfill({ json: PLAN }));
  await page.route("**/api/planning/forecast", (route) =>
    route.fulfill({ json: { current: {}, horizon: 12, forecast: [] } }),
  );
  await page.route("**/api/planning/history", (route) => {
    if (route.request().method() === "POST") {
      return route.fulfill({ json: { ...SNAPSHOT, top3: [] } });
    }
    return route.fulfill({ json: { items: history, count: history.length } });
  });
}

test("пустая история объясняет себя и предлагает сохранить план", async ({ page }) => {
  await setup(page, []);
  await page.goto("/planning");

  const section = page.getByRole("region", { name: "История планов" });
  await expect(section.getByText("Пока нет сохранённых планов")).toBeVisible();
  await expect(section.getByRole("button", { name: "Сохранить текущий план" })).toBeVisible();
});

test("снимок показывает дату, профиль и деньги по канону", async ({ page }) => {
  await setup(page, [SNAPSHOT]);
  await page.goto("/planning");

  const section = page.getByRole("region", { name: "История планов" });
  await expect(section.getByText("01.09.2026")).toBeVisible();
  await expect(section.getByText("до отпуска")).toBeVisible();

  // Неразрывный пробел разрядов и знак рубля — деньги идут через общий канон
  // `formatMoney`, а не собираются строкой на месте.
  const money = section.locator(".fp-plan-history__money").first();
  const rendered = await money.textContent();
  expect(rendered).toContain(" ₽");
  expect(rendered, "неразрывный пробел схлопнулся").not.toContain("39 500");
});

test("удаление требует подтверждения, Esc отменяет его (A11Y-06)", async ({ page }) => {
  await setup(page, [SNAPSHOT]);
  await page.goto("/planning");

  const trigger = page.getByRole("button", { name: /Удалить снимок от 01.09.2026/ });
  await trigger.click();

  const dialog = page.getByRole("dialog");
  await expect(dialog).toBeVisible();
  await expect(dialog).toContainText("Удалить снимок плана?");

  await page.keyboard.press("Escape");
  await expect(dialog).toHaveCount(0);
  // Снимок на месте — Esc отменяет, а не подтверждает.
  await expect(page.getByText("01.09.2026")).toBeVisible();
  await expect(trigger).toBeFocused();
});

test("подпись снимка ограничена и связана с полем по label", async ({ page }) => {
  await setup(page, []);
  await page.goto("/planning");

  const input = page.getByLabel("Подпись к снимку");
  await expect(input).toBeVisible();
  await expect(input).toHaveAttribute("maxlength", "500");
});

/* Удаление снимка обратимо с v8.38.0. Юнит-тест проверяет, что отмена ПРЕДЛОЖЕНА;
   только браузер показывает, что кнопка «Вернуть» действительно доходит до
   пользователя в тосте и что нажатие уходит на сервер. */
test("удалённый снимок возвращается кнопкой «Вернуть» (v8.38.0)", async ({ page }) => {
  await setup(page, [SNAPSHOT]);

  let restoreCalled = false;
  await page.route("**/api/planning/history/*/restore", async (route) => {
    restoreCalled = true;
    await route.fulfill({ json: SNAPSHOT });
  });
  await page.route("**/api/planning/history/*", async (route) => {
    if (route.request().method() === "DELETE") {
      return route.fulfill({ json: { status: "deleted", id: 7 } });
    }
    return route.fallback();
  });

  await page.goto("/planning");
  await page.getByRole("button", { name: /Удалить снимок от 01.09.2026/ }).click();
  await page
    .getByRole("dialog")
    .getByRole("button", { name: /Удалить снимок от 01.09.2026/ })
    .click();

  const undo = page.getByRole("button", { name: "Вернуть" });
  await expect(undo).toBeVisible();
  await undo.click();
  await expect.poll(() => restoreCalled).toBe(true);
});
