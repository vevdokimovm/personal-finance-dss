import { expect, test } from "@playwright/test";

/**
 * Колокольчик уведомлений в настоящем браузере (v8.32.0).
 *
 * Юнит-тесты мокают Radix и потому НЕ проверяют главного, ради чего Popover и взят:
 * закрытие по Esc, закрытие по клику вне панели и возврат фокуса на триггер. Именно
 * это отличает «панель открывается» от «панель работает» — a11y-аудит нашёл отсутствие
 * всех трёх механик в первой, самописной версии.
 */

const PROFILE = {
  id: "u1",
  email: "anna@example.com",
  display_name: "Анна",
  email_verified: true,
  created_at: "2026-01-15",
};

const FEED = {
  items: [
    {
      id: 1,
      type: "budget_overrun",
      title: "Превышен бюджет «Продукты»",
      // Тело — ровно то, что отдаёт бэкенд после v8.32.0: неразрывные пробелы
      // разрядов и знак рубля через неразрывный пробел (`format_money`).
      body: "Сводка за август: доход 180\u00a0000,00\u00a0\u20bd, расход 78\u00a0000,00\u00a0\u20bd",
      link: "/goals",
      is_read: false,
      created_at: "2026-09-01T10:00:00",
    },
  ],
  unread_count: 1,
};

async function signIn(page: import("@playwright/test").Page) {
  await page.route("**/api/auth/me", (route) => route.fulfill({ json: PROFILE }));
  await page.route("**/api/notifications/unread-count", (route) =>
    route.fulfill({ json: { unread_count: FEED.unread_count } }),
  );
  await page.route("**/api/notifications/feed*", (route) => route.fulfill({ json: FEED }));
}

test("колокольчик показывает счётчик и открывает панель", async ({ page }) => {
  await signIn(page);
  await page.goto("/goals");

  const bell = page.getByRole("button", { name: /Уведомления/ });
  await expect(bell).toBeVisible();
  await expect(bell).toHaveAccessibleName("Уведомления, непрочитанных: 1");

  await bell.click();
  await expect(page.getByText("Превышен бюджет «Продукты»")).toBeVisible();
});

test("Esc закрывает панель и возвращает фокус на колокольчик (A11Y-06)", async ({ page }) => {
  await signIn(page);
  await page.goto("/goals");

  const bell = page.getByRole("button", { name: /Уведомления/ });
  await bell.click();
  await expect(page.getByText("Превышен бюджет «Продукты»")).toBeVisible();

  await page.keyboard.press("Escape");
  await expect(page.getByText("Превышен бюджет «Продукты»")).toHaveCount(0);
  // Фокус обязан вернуться на триггер: иначе он падает в <body>, и клавиатурный
  // пользователь теряет место — тот же класс, что чинили на «Прочитать все».
  await expect(bell).toBeFocused();
});

test("клик вне панели закрывает её", async ({ page }) => {
  await signIn(page);
  await page.goto("/goals");

  await page.getByRole("button", { name: /Уведомления/ }).click();
  await expect(page.getByText("Превышен бюджет «Продукты»")).toBeVisible();

  await page.locator("#fp-main").click({ position: { x: 5, y: 5 } });
  await expect(page.getByText("Превышен бюджет «Продукты»")).toHaveCount(0);
});

test("непрочитанное помечено словом, а не только цветом (A11Y-07)", async ({ page }) => {
  await signIn(page);
  await page.goto("/goals");

  await page.getByRole("button", { name: /Уведомления/ }).click();
  await expect(page.getByText("новое")).toBeVisible();
});

test("суммы в уведомлении доходят до экрана не искажёнными", async ({ page }) => {
  await signIn(page);
  await page.goto("/goals");

  await page.getByRole("button", { name: /Уведомления/ }).click();

  // Формат собирается на БЭКЕНДЕ (`format_money`, 12 тестов), потому что то же тело
  // уходит в email и Telegram. Здесь проверяется другое и не менее важное: что разметка
  // доносит его до экрана НЕ ИСКАЖАЯ — в частности не схлопывает неразрывный пробел
  // разрядов. Обычный пробел разорвал бы сумму переносом строки, и «180 000» на двух
  // строках прочиталось бы как два числа.
  const body = page.locator(".fp-bell__item-body");
  await expect(body).toBeVisible();
  const rendered = await body.textContent();
  expect(rendered).toContain("\u00a0\u20bd");
  expect(rendered).toContain("180\u00a0000,00");
  expect(rendered, "неразрывный пробел схлопнулся в обычный").not.toContain("180 000");
});

test("при отозванном согласии (403) колокольчика нет вовсе", async ({ page }) => {
  await page.route("**/api/auth/me", (route) => route.fulfill({ json: PROFILE }));
  await page.route("**/api/notifications/unread-count", (route) =>
    route.fulfill({
      status: 403,
      json: { detail: { code: "consent_required", consent_type: "financial_data" } },
    }),
  );
  await page.goto("/goals");

  await expect(page.getByRole("navigation", { name: "Основные разделы" })).toBeVisible();
  await expect(page.getByRole("button", { name: /Уведомления/ })).toHaveCount(0);
});

test("при аварии бэкенда (500) колокольчик остаётся — функция не исчезает молча", async ({
  page,
}) => {
  await page.route("**/api/auth/me", (route) => route.fulfill({ json: PROFILE }));
  await page.route("**/api/notifications/unread-count", (route) =>
    route.fulfill({ status: 500, json: { detail: "internal error" } }),
  );
  await page.goto("/goals");

  await expect(page.getByRole("button", { name: /Уведомления/ })).toBeVisible();
});
