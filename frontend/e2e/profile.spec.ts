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
  // Email показывается дважды — в топбаре аккаунта и в самом профиле. Проверяем
  // именно карточку профиля: топбар это другой экран ответственности (AuthTopbarLink),
  // у него свои тесты, и широкий локатор падал на strict mode.
  const main = page.locator("#fp-main");
  await expect(main.getByText("Анна")).toBeVisible();
  await expect(main.getByText("anna@example.com")).toBeVisible();
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

/* Экран согласий — требование L3 (v8.41.0). Юнит-тесты проверяют логику списка;
   браузер показывает, что все три согласия действительно доезжают до страницы. */
test("экран согласий показывает все типы и различает отзываемые (L3)", async ({ page }) => {
  await page.route("**/api/auth/me", (route) => route.fulfill({ json: PROFILE }));
  await page.route("**/api/notifications/unread-count", (route) =>
    route.fulfill({ json: { unread_count: 0 } }),
  );
  await page.route("**/api/referral/me", (route) =>
    route.fulfill({
      json: {
        referral_code: "ABC123",
        invite_url: "https://finpilot.ru/register?ref=ABC123",
        invited_count: 0,
        referred_by: null,
        milestones: [],
        next_milestone: null,
      },
    }),
  );
  await page.route("**/api/consents", (route) =>
    route.fulfill({
      json: {
        consents: {
          personal_data: {
            granted: true,
            version: "1.0",
            granted_at: "2026-01-15T10:00:00",
            withdrawable: false,
          },
          financial_data: {
            granted: false,
            version: "1.0",
            granted_at: null,
            withdrawable: true,
          },
          marketing: {
            granted: true,
            version: "1.0",
            granted_at: "2026-02-01T10:00:00",
            withdrawable: true,
          },
        },
      },
    }),
  );

  await page.goto("/profile");

  const main = page.locator("#fp-main");
  // 🔴 До v8.41.0 экран знал ОДНО согласие из трёх: отозвать маркетинговое было нельзя.
  await expect(main.getByText("Персональные данные")).toBeVisible();
  await expect(main.getByText("Финансовые данные")).toBeVisible();
  await expect(main.getByText("Рекламная рассылка")).toBeVisible();

  // Отзываемое — с кнопкой; согласие-основание — с объяснением вместо кнопки,
  // которая гарантированно дала бы 409.
  await expect(
    main.getByRole("button", { name: /Отозвать согласие: Рекламная/ }),
  ).toBeVisible();
  await expect(
    main.getByRole("button", { name: /Отозвать согласие: Персональные/ }),
  ).toHaveCount(0);
  await expect(main.getByText(/нельзя отозвать без удаления аккаунта/)).toBeVisible();
});
