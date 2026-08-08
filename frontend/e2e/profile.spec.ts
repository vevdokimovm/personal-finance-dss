import { expect, test } from "@playwright/test";

const PROFILE = {
  id: "u1",
  email: "anna@example.com",
  display_name: "Анна",
  email_verified: true,
  created_at: "2026-01-15",
};

test("профиль показывает имя, email и дату регистрации", async ({ page }) => {
  await page.route("**/api/auth/me", (route) => route.fulfill({ json: PROFILE }));
  await page.goto("/profile");
  await expect(page.getByText("Анна")).toBeVisible();
  await expect(page.getByText("anna@example.com")).toBeVisible();
});

// 401 — ожидаемый исход в гостевом режиме (auth/me требует аутентификации, в отличие
// от transactions/obligations/goals/liquid-assets) — отдельная ветка от сетевой
// ошибки, без кнопки "Повторить" (a11y-auditor, Э4 партия 2, P1: одинаковое
// сообщение для 401 и сбоя давало тупиковый retry-цикл без объяснения причины).
test("неаутентифицированный доступ (401) — отдельное сообщение, без «Повторить»", async ({
  page,
}) => {
  await page.route("**/api/auth/me", (route) =>
    route.fulfill({ status: 401, json: { detail: "Not authenticated" } }),
  );
  await page.goto("/profile");
  await expect(page.getByText("Нужно войти в систему")).toBeVisible();
  await expect(page.getByRole("alert")).toHaveCount(0);
  await expect(page.getByRole("button", { name: "Повторить" })).toHaveCount(0);
});

test("сетевая ошибка (500) — состояние ошибки, повтор работает", async ({ page }) => {
  await page.route("**/api/auth/me", (route) =>
    route.fulfill({ status: 500, json: { detail: "internal error" } }),
  );
  await page.goto("/profile");
  await expect(page.getByRole("alert")).toContainText("Не получилось загрузить профиль");

  await page.unroute("**/api/auth/me");
  await page.route("**/api/auth/me", (route) => route.fulfill({ json: PROFILE }));
  await page.getByRole("button", { name: "Повторить" }).click();
  await expect(page.getByText("Анна")).toBeVisible();
});
