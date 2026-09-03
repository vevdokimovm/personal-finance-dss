import { expect, test } from "@playwright/test";

/**
 * Реферальная программа в настоящем браузере (v8.37.0).
 *
 * Главное, чего юнит-тесты дать не могут: что ссылка `/register?ref=CODE`, которую
 * строит бэкенд, действительно доносит код до формы регистрации. До этого батча
 * `RegisterPage` параметр не читал — приглашение открывалось, регистрация проходила,
 * и не засчитывалась никому.
 */

const PROFILE = {
  id: "u1",
  email: "anna@example.com",
  display_name: "Анна",
  email_verified: true,
  created_at: "2026-01-15",
};

const REFERRAL = {
  referral_code: "ABC123",
  invite_url: "https://finpilot.ru/register?ref=ABC123",
  invited_count: 2,
  referred_by: null,
  milestones: [
    { threshold: 1, title: "Первое приглашение", reward: null, reached: true },
    { threshold: 3, title: "Тёплая компания", reward: null, reached: false },
  ],
  next_milestone: { threshold: 3, title: "Тёплая компания", remaining: 1 },
};

test("ссылка-приглашение видна на профиле", async ({ page }) => {
  await page.route("**/api/auth/me", (route) => route.fulfill({ json: PROFILE }));
  await page.route("**/api/notifications/unread-count", (route) =>
    route.fulfill({ json: { unread_count: 0 } }),
  );
  await page.route("**/api/consents", (route) => route.fulfill({ json: [] }));
  await page.route("**/api/referral/me", (route) => route.fulfill({ json: REFERRAL }));

  await page.goto("/profile");

  await expect(page.getByRole("heading", { name: "Приглашения друзей" })).toBeVisible();
  // Playwright не знает getByDisplayValue — сверяем значение самого поля.
  await expect(page.getByLabel("Ваша ссылка для друзей")).toHaveValue(
    "https://finpilot.ru/register?ref=ABC123",
  );
  await expect(page.getByText("Первое приглашение")).toBeVisible();
});

test("код из ссылки доезжает до запроса регистрации", async ({ page }) => {
  await page.route("**/api/auth/me", (route) =>
    route.fulfill({ status: 401, json: { detail: "Not authenticated" } }),
  );

  let sent: Record<string, unknown> | null = null;
  await page.route("**/api/auth/register", async (route) => {
    sent = route.request().postDataJSON();
    await route.fulfill({ json: { id: "u2", email: "boris@example.com" } });
  });

  // Ровно тот адрес, который строит `routes_referral.py::my_referral`.
  await page.goto("/register?ref=ABC123");

  await page.getByLabel("Email").fill("boris@example.com");
  await page.getByLabel("Пароль", { exact: true }).fill("Passw0rd!");
  await page.getByLabel(/согласие|обработку/i).check();
  await page.getByRole("button", { name: "Зарегистрироваться" }).click();

  await expect.poll(() => sent).not.toBeNull();
  expect(sent).toMatchObject({ referral_code: "ABC123" });
});
