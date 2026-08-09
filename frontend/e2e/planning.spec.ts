import { expect, test } from "@playwright/test";

const PLAN_ANNA = {
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
      Rt_new: 0,
      Lt_new: 1.2,
      Dt_new: 0.3472,
      is_recommended: true,
    },
  ],
  ranked: [
    {
      id: "a0100",
      name: "Всё в резерв",
      x_obligations: 0,
      x_reserve: 39500,
      x_goals: 0,
      utility: 0.8,
      Rt_new: 0,
      Lt_new: 1.2,
      Dt_new: 0.3472,
      is_recommended: true,
    },
    {
      id: "a1000",
      name: "Всё на погашение долга",
      x_obligations: 39500,
      x_reserve: 0,
      x_goals: 0,
      utility: 0.62,
      Rt_new: 0,
      Lt_new: 0.2,
      Dt_new: 0.28,
    },
  ],
  admissible_count: 2,
  alternatives_total: 66,
  input_summary: {
    income: 180000,
    expense: 78000,
    bliq: 15000,
    transactions_count: 12,
    obligations_count: 1,
    goals_count: 2,
  },
};

const FORECAST_ANNA = {
  current: { Bt: 265000, Rt: 39500, Lt: 0.281, Dt: 0.3472 },
  horizon: 12,
  forecast: [{ period: 12, Rt: 813519, Rt_p10: 682866, Rt_p90: 952920 }],
};

test.beforeEach(async ({ page }) => {
  await page.route("**/api/planning/calculate", (route) => route.fulfill({ json: PLAN_ANNA }));
  await page.route("**/api/planning/forecast", (route) => route.fulfill({ json: FORECAST_ANNA }));
});

test("план распределения показывает риск-профиль и входные данные", async ({ page }) => {
  await page.goto("/planning");
  await expect(page.getByText("Сбалансированный")).toBeVisible();
  await expect(page.getByText("12 опер. · 1 обяз. · 2 целей")).toBeVisible();
  await expect(page.getByText(/Резерв/)).toBeVisible();
});

test("дефицит на /planning — fail-loud сообщение вместо аллокации", async ({ page }) => {
  await page.unroute("**/api/planning/calculate");
  await page.route("**/api/planning/calculate", (route) =>
    route.fulfill({ json: { ...PLAN_ANNA, top3: [], ranked: [], admissible_count: 0 } }),
  );
  await page.goto("/planning");
  await expect(page.getByText("Плана распределения нет")).toBeVisible();
});

test("браузер альтернатив: свёрнут по умолчанию, раскрывается и сортируется", async ({ page }) => {
  await page.goto("/planning");
  await expect(page.getByText("Всё на погашение долга")).not.toBeVisible();
  await page.getByRole("button", { name: "Показать все (2)" }).click();
  await expect(page.getByText("Всё на погашение долга")).toBeVisible();
  await expect(page.getByText("рекомендовано")).toBeVisible();

  await page.getByLabel("Сортировать по").selectOption("Долговой нагрузке (ПДН)");
  const rows = page.locator(".fp-alt-row__name");
  await expect(rows.first()).toContainText("Всё на погашение долга");
});

test("дашборд → «Построить план распределения →» ведёт на рабочий /planning", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("link", { name: "Построить план распределения →" }).click();
  await expect(page).toHaveURL(/\/planning$/);
  await expect(page.getByText("Сбалансированный")).toBeVisible();
});
