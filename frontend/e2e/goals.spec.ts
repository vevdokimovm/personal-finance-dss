import { expect, test } from "@playwright/test";

const GOALS = [
  {
    id: 1,
    name: "Подушка безопасности",
    category: "reserve",
    target_amount: 500000,
    current_amount: 125000,
    deadline: "2027-01-01",
  },
];

test("список целей показывает прогресс-бар", async ({ page }) => {
  await page.route("**/api/goals", (route) => route.fulfill({ json: GOALS }));
  await page.goto("/goals");
  await expect(page.getByText("Подушка безопасности")).toBeVisible();
  const bar = page.getByRole("progressbar", { name: /Подушка безопасности/ });
  await expect(bar).toHaveAttribute("aria-valuenow", "25");
});

test("пустой список целей показывает состояние «целей нет»", async ({ page }) => {
  await page.route("**/api/goals", (route) => route.fulfill({ json: [] }));
  await page.goto("/goals");
  await expect(page.getByText("Целей пока нет")).toBeVisible();
});

test("ошибка загрузки целей — повтор восстанавливает список", async ({ page }) => {
  await page.route("**/api/goals", (route) =>
    route.fulfill({ status: 500, json: { detail: "internal error" } }),
  );
  await page.goto("/goals");
  await expect(page.getByRole("alert")).toContainText("Не получилось загрузить цели");

  await page.unroute("**/api/goals");
  await page.route("**/api/goals", (route) => route.fulfill({ json: GOALS }));
  await page.getByRole("button", { name: "Повторить" }).click();
  await expect(page.getByText("Подушка безопасности")).toBeVisible();
});
