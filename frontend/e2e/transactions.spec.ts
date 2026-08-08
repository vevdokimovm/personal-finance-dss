import { expect, test } from "@playwright/test";

const TRANSACTIONS = [
  { id: 1, date: "2026-08-01", type: "income", amount: 180000, category: "Зарплата" },
  {
    id: 2,
    date: "2026-08-03",
    type: "expense",
    amount: 4500,
    category: "Продукты",
    description: "Пятёрочка",
  },
];

test("список операций рендерит доход и расход", async ({ page }) => {
  await page.route("**/api/transactions", (route) => route.fulfill({ json: TRANSACTIONS }));
  await page.goto("/transactions");
  await expect(page.getByText("Зарплата")).toBeVisible();
  await expect(page.getByText("Продукты")).toBeVisible();
  await expect(page.locator(".fp-transaction-row__amount--income")).toContainText("+");
  await expect(page.locator(".fp-transaction-row__amount--expense")).toContainText("−");
});

test("пустой список операций показывает состояние «операций нет»", async ({ page }) => {
  await page.route("**/api/transactions", (route) => route.fulfill({ json: [] }));
  await page.goto("/transactions");
  await expect(page.getByText("Операций пока нет")).toBeVisible();
});

test("ошибка загрузки операций — повтор восстанавливает список", async ({ page }) => {
  await page.route("**/api/transactions", (route) =>
    route.fulfill({ status: 500, json: { detail: "internal error" } }),
  );
  await page.goto("/transactions");
  await expect(page.getByRole("alert")).toContainText("Не получилось загрузить операции");

  await page.unroute("**/api/transactions");
  await page.route("**/api/transactions", (route) => route.fulfill({ json: TRANSACTIONS }));
  await page.getByRole("button", { name: "Повторить" }).click();
  await expect(page.getByText("Зарплата")).toBeVisible();
});

test("пустое состояние дашборда ведёт на /transactions рабочей ссылкой", async ({ page }) => {
  await page.route("**/api/planning/calculate", (route) =>
    route.fulfill({
      json: {
        risk_profile: "Сбалансированный",
        indicators: { Rt: 0, Lt: 0, Dt: 0 },
        top3: [],
        admissible_count: 0,
        alternatives_total: 66,
        input_summary: {
          income: 0,
          expense: 0,
          bliq: 0,
          transactions_count: 0,
          obligations_count: 0,
          goals_count: 0,
        },
      },
    }),
  );
  await page.route("**/api/planning/forecast", (route) =>
    route.fulfill({ json: { current: { Bt: 0, Rt: 0, Lt: 0, Dt: 0 }, horizon: 12, forecast: [] } }),
  );
  await page.route("**/api/transactions", (route) => route.fulfill({ json: [] }));

  await page.goto("/");
  await page.getByRole("link", { name: "Внести операции →" }).click();
  await expect(page).toHaveURL(/\/transactions$/);
  await expect(page.getByText("Операций пока нет")).toBeVisible();
});
