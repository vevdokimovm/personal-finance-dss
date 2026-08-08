import { expect, test } from "@playwright/test";

const OBLIGATIONS = [
  {
    id: 1,
    name: "Ипотека",
    type: "mortgage",
    amount: 5000000,
    interest_rate: 0.078,
    monthly_payment: 45000,
    months_elapsed: 24,
    months_remaining: 96,
    payment_day: 5,
    term: 120,
  },
];

test("список обязательств показывает платёж и ставку", async ({ page }) => {
  await page.route("**/api/obligations", (route) => route.fulfill({ json: OBLIGATIONS }));
  await page.goto("/obligations");
  await expect(page.getByText("Ипотека")).toBeVisible();
  await expect(page.getByText("7,8%")).toBeVisible();
});

test("пустой список обязательств показывает состояние «обязательств нет»", async ({ page }) => {
  await page.route("**/api/obligations", (route) => route.fulfill({ json: [] }));
  await page.goto("/obligations");
  await expect(page.getByText("Обязательств нет")).toBeVisible();
});

test("ошибка загрузки обязательств — повтор восстанавливает список", async ({ page }) => {
  await page.route("**/api/obligations", (route) =>
    route.fulfill({ status: 500, json: { detail: "internal error" } }),
  );
  await page.goto("/obligations");
  await expect(page.getByRole("alert")).toContainText("Не получилось загрузить обязательства");

  await page.unroute("**/api/obligations");
  await page.route("**/api/obligations", (route) => route.fulfill({ json: OBLIGATIONS }));
  await page.getByRole("button", { name: "Повторить" }).click();
  await expect(page.getByText("Ипотека")).toBeVisible();
});
