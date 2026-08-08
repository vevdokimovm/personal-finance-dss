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
    },
  ],
  admissible_count: 66,
  alternatives_total: 66,
  input_summary: {
    income: 180000,
    expense: 78000,
    bliq: 0,
    transactions_count: 12,
    obligations_count: 1,
    goals_count: 0,
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

test("тумблер темы переключает data-theme и переживает перезагрузку страницы", async ({ page }) => {
  await page.goto("/");
  const html = page.locator("html");
  const select = page.getByRole("combobox", { name: "Тема оформления" });

  await select.selectOption("light");
  await expect(html).toHaveAttribute("data-theme", "light");

  await select.selectOption("dark");
  await expect(html).toHaveAttribute("data-theme", "dark");

  // Выбор запомнен (Zustand persist -> localStorage) — переживает reload.
  await select.selectOption("light");
  await page.reload();
  await expect(html).toHaveAttribute("data-theme", "light");
  await expect(page.getByRole("combobox", { name: "Тема оформления" })).toHaveValue("light");
});

test("обе темы «Спокойный» реально достижимы и рендерят контент без ошибок", async ({ page }) => {
  await page.goto("/");
  const select = page.getByRole("combobox", { name: "Тема оформления" });

  await select.selectOption("dark");
  await expect(page.locator(".fp-hero-value")).toBeVisible();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");

  await select.selectOption("light");
  await expect(page.locator(".fp-hero-value")).toBeVisible();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
});
