import { expect, test } from "@playwright/test";

// interest_rate — доля (0.14 = 14%), не проценты — см. AssetsPage.test.tsx для обоснования.
const ASSETS = [
  { id: 1, name: "Депозит в Сбере", type: "savings_account", amount: 300000, interest_rate: 0.14 },
];

test("список ликвидных активов показывает сумму и ставку", async ({ page }) => {
  await page.route("**/api/liquid-assets", (route) => route.fulfill({ json: ASSETS }));
  await page.goto("/banks");
  await expect(page.getByText("Депозит в Сбере")).toBeVisible();
  await expect(page.getByText("14,0%")).toBeVisible();
});

test("пустой список активов показывает состояние «активов нет»", async ({ page }) => {
  await page.route("**/api/liquid-assets", (route) => route.fulfill({ json: [] }));
  await page.goto("/banks");
  await expect(page.getByText("Активов пока нет")).toBeVisible();
});

test("ошибка загрузки активов — повтор восстанавливает список", async ({ page }) => {
  await page.route("**/api/liquid-assets", (route) =>
    route.fulfill({ status: 500, json: { detail: "internal error" } }),
  );
  await page.goto("/banks");
  await expect(page.getByRole("alert")).toContainText("Не получилось загрузить активы");

  await page.unroute("**/api/liquid-assets");
  await page.route("**/api/liquid-assets", (route) => route.fulfill({ json: ASSETS }));
  await page.getByRole("button", { name: "Повторить" }).click();
  await expect(page.getByText("Депозит в Сбере")).toBeVisible();
});
