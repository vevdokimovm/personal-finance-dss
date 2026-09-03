import { expect, test } from "@playwright/test";

/**
 * Семейный доступ и приём приглашения в настоящем браузере (v8.36.0).
 *
 * Главное, чего юнит-тесты дать не могут: что ссылка `/join?token=...`, которую
 * бэкенд кладёт в приглашение, действительно открывается. До этого батча роута не
 * существовало вовсе — приглашение вело в никуда.
 */

const PROFILE = {
  id: "u1",
  email: "anna@example.com",
  display_name: "Анна",
  email_verified: true,
  created_at: "2026-01-15",
};

const OWNED = {
  id: 1,
  name: "Семья Петровых",
  owner_id: "u1",
  role: "owner",
  member_count: 2,
  created_at: "2026-09-01T10:00:00",
};

async function signIn(page: import("@playwright/test").Page) {
  await page.route("**/api/auth/me", (route) => route.fulfill({ json: PROFILE }));
  await page.route("**/api/notifications/unread-count", (route) =>
    route.fulfill({ json: { unread_count: 0 } }),
  );
}

test("семейный доступ достижим из навигации", async ({ page }) => {
  await signIn(page);
  await page.route("**/api/households", (route) => route.fulfill({ json: [OWNED] }));
  await page.route("**/api/households/1/members", (route) => route.fulfill({ json: [] }));
  await page.route("**/api/households/1/invites", (route) => route.fulfill({ json: [] }));

  await page.goto("/planning");
  await page
    .getByRole("navigation", { name: "Основные разделы" })
    .getByRole("link", { name: "Семейный доступ" })
    .click();

  await expect(page).toHaveURL(/\/household$/);
  await expect(page.getByRole("heading", { level: 1, name: "Семейный доступ" })).toBeVisible();
});

test("ссылка приглашения открывается и принимается", async ({ page }) => {
  await signIn(page);
  await page.route("**/api/households", (route) => route.fulfill({ json: [] }));
  await page.route("**/api/households/invites/*/accept", (route) =>
    route.fulfill({ json: { household_id: 1, role: "member" } }),
  );

  // Ровно тот адрес, который строит бэкенд (`_invite_url`). До v8.36.0 роута не было —
  // пользователь упирался в пустоту.
  await page.goto("/join?token=abc123");

  await expect(page.getByText("Готово — вы в семейном доступе")).toBeVisible();
});

test("просроченное приглашение объясняет, что делать", async ({ page }) => {
  await signIn(page);
  await page.route("**/api/households", (route) => route.fulfill({ json: [] }));
  await page.route("**/api/households/invites/*/accept", (route) =>
    route.fulfill({ status: 400, json: { detail: "Приглашение недействительно" } }),
  );

  await page.goto("/join?token=expired");

  await expect(page.getByText("Приглашение не сработало")).toBeVisible();
  await expect(page.getByRole("link", { name: "К семейному доступу" })).toBeVisible();
});

test("ссылка без токена не притворяется рабочей", async ({ page }) => {
  await signIn(page);
  await page.route("**/api/households", (route) => route.fulfill({ json: [] }));

  await page.goto("/join");

  await expect(page.getByText("Ссылка неполная")).toBeVisible();
});

test("гостю предлагают войти, а не отказ", async ({ page }) => {
  await page.route("**/api/auth/me", (route) =>
    route.fulfill({ status: 401, json: { detail: "Not authenticated" } }),
  );
  await page.route("**/api/households", (route) => route.fulfill({ json: [] }));

  await page.goto("/join?token=abc123");

  await expect(page.getByText("Сначала войдите")).toBeVisible();

  // Токен обязан пережить вход: до v8.36.0 гость уходил на /login, адрес с токеном
  // терялся, и после входа человек оказывался на дашборде без семьи.
  // В шапке есть своя ссылка «Войти» — берём именно ту, что в панели приглашения.
  const signIn = page.getByRole("main").getByRole("link", { name: "Войти" });
  await expect(signIn).toHaveAttribute("href", /redirect=.*join.*abc123/);
  await signIn.click();
  await expect(page).toHaveURL(/\/login\?redirect=/);
  await expect(page).toHaveURL(/abc123/);
});
