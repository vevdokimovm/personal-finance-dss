import { expect, test } from "@playwright/test";

/**
 * Мокаем сеть на границе /api/planning/*, а не поднимаем реальный бэкенд: playwright.config.ts
 * стартует только фронт (build+preview), бэкенд в CI-джобе `frontend` не поднят — полноценный
 * full-stack E2E (реальный uvicorn) отдельная задача, не часть этого пилота. Реальная интеграция
 * (Vite dev + живой бэкенд, cookie-сессия demo/load) проверена вручную браузером при сборке
 * экрана — фикстуры ниже дословно те же числа (профиль «anna», docs/reference_profiles.md).
 */
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
  forecast: [
    { period: 1, Rt: 79000, Rt_p10: 72000, Rt_p90: 86000 },
    { period: 12, Rt: 813519, Rt_p10: 682866, Rt_p90: 952920 },
  ],
};

test.beforeEach(async ({ page }) => {
  await page.route("**/api/planning/calculate", (route) => route.fulfill({ json: PLAN_ANNA }));
  await page.route("**/api/planning/forecast", (route) => route.fulfill({ json: FORECAST_ANNA }));
});

test("дашборд рендерит реальные показатели профиля anna", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator(".fp-hero-value")).toHaveText("39 500,00 ₽");
  await expect(page.getByText("34,7%")).toBeVisible();
  await expect(page.getByText(/Резерв/)).toBeVisible();
  await expect(page.getByText(/\(100%\)/)).toBeVisible();
  await expect(page.getByText(/Медиана к 12 мес/)).toBeVisible();
});

test("состояние ошибки показывается и повтор запроса работает", async ({ page }) => {
  await page.unroute("**/api/planning/calculate");
  await page.route("**/api/planning/calculate", (route) =>
    route.fulfill({ status: 500, json: { detail: "internal error" } }),
  );
  await page.goto("/");
  await expect(page.getByRole("alert")).toContainText("Не получилось загрузить обзор");

  await page.unroute("**/api/planning/calculate");
  await page.route("**/api/planning/calculate", (route) => route.fulfill({ json: PLAN_ANNA }));
  await page.getByRole("button", { name: "Повторить" }).click();
  await expect(page.locator(".fp-hero-value")).toHaveText("39 500,00 ₽");
});

test("пустое состояние показывается для нового пользователя", async ({ page }) => {
  await page.unroute("**/api/planning/calculate");
  await page.route("**/api/planning/calculate", (route) =>
    route.fulfill({
      json: {
        ...PLAN_ANNA,
        input_summary: { ...PLAN_ANNA.input_summary, income: 0, expense: 0 },
      },
    }),
  );
  await page.goto("/");
  await expect(page.getByText("Пока нет данных для обзора")).toBeVisible();
  await expect(page.getByRole("link", { name: "Внести операции →" })).toBeVisible();
});
