# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: dashboard.spec.ts >> дашборд рендерит реальные показатели профиля anna
- Location: e2e/dashboard.spec.ts:49:1

# Error details

```
Error: expect(locator).toHaveText(expected) failed

Locator: locator('.fp-hero-value')
Expected: "39 500,00 ₽"
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toHaveText" with timeout 5000ms
  - waiting for locator('.fp-hero-value')

```

```yaml
- strong: Something went wrong!
- button "Show Error"
```

# Test source

```ts
  1  | import { expect, test } from "@playwright/test";
  2  | 
  3  | /**
  4  |  * Мокаем сеть на границе /api/planning/*, а не поднимаем реальный бэкенд: playwright.config.ts
  5  |  * стартует только фронт (build+preview), бэкенд в CI-джобе `frontend` не поднят — полноценный
  6  |  * full-stack E2E (реальный uvicorn) отдельная задача, не часть этого пилота. Реальная интеграция
  7  |  * (Vite dev + живой бэкенд, cookie-сессия demo/load) проверена вручную браузером при сборке
  8  |  * экрана — фикстуры ниже дословно те же числа (профиль «anna», docs/reference_profiles.md).
  9  |  */
  10 | const PLAN_ANNA = {
  11 |   risk_profile: "Сбалансированный",
  12 |   indicators: { Rt: 39500, Lt: 0, Dt: 0.3472, BLR: 3.4, It: 180000, Et: 78000, SigmaP: 62500 },
  13 |   top3: [
  14 |     {
  15 |       id: "a0100",
  16 |       name: "Всё в резерв",
  17 |       x_obligations: 0,
  18 |       x_reserve: 39500,
  19 |       x_goals: 0,
  20 |       utility: 0.8,
  21 |     },
  22 |   ],
  23 |   admissible_count: 66,
  24 |   alternatives_total: 66,
  25 |   input_summary: {
  26 |     income: 180000,
  27 |     expense: 78000,
  28 |     bliq: 0,
  29 |     transactions_count: 12,
  30 |     obligations_count: 1,
  31 |     goals_count: 0,
  32 |   },
  33 | };
  34 | 
  35 | const FORECAST_ANNA = {
  36 |   current: { Bt: 265000, Rt: 39500, Lt: 0.281, Dt: 0.3472 },
  37 |   horizon: 12,
  38 |   forecast: [
  39 |     { period: 1, Rt: 79000, Rt_p10: 72000, Rt_p90: 86000 },
  40 |     { period: 12, Rt: 813519, Rt_p10: 682866, Rt_p90: 952920 },
  41 |   ],
  42 | };
  43 | 
  44 | test.beforeEach(async ({ page }) => {
  45 |   await page.route("**/api/planning/calculate", (route) => route.fulfill({ json: PLAN_ANNA }));
  46 |   await page.route("**/api/planning/forecast", (route) => route.fulfill({ json: FORECAST_ANNA }));
  47 | });
  48 | 
  49 | test("дашборд рендерит реальные показатели профиля anna", async ({ page }) => {
  50 |   await page.goto("/");
> 51 |   await expect(page.locator(".fp-hero-value")).toHaveText("39 500,00 ₽");
     |                                                ^ Error: expect(locator).toHaveText(expected) failed
  52 |   await expect(page.getByText("34,7%")).toBeVisible();
  53 |   await expect(page.getByText(/Резерв/)).toBeVisible();
  54 |   await expect(page.getByText(/\(100%\)/)).toBeVisible();
  55 |   await expect(page.getByText(/Медиана к 12 мес/)).toBeVisible();
  56 | });
  57 | 
  58 | test("состояние ошибки показывается и повтор запроса работает", async ({ page }) => {
  59 |   await page.unroute("**/api/planning/calculate");
  60 |   await page.route("**/api/planning/calculate", (route) =>
  61 |     route.fulfill({ status: 500, json: { detail: "internal error" } }),
  62 |   );
  63 |   await page.goto("/");
  64 |   await expect(page.getByRole("alert")).toContainText("Не получилось загрузить обзор");
  65 | 
  66 |   await page.unroute("**/api/planning/calculate");
  67 |   await page.route("**/api/planning/calculate", (route) => route.fulfill({ json: PLAN_ANNA }));
  68 |   await page.getByRole("button", { name: "Повторить" }).click();
  69 |   await expect(page.locator(".fp-hero-value")).toHaveText("39 500,00 ₽");
  70 | });
  71 | 
  72 | test("пустое состояние показывается для нового пользователя", async ({ page }) => {
  73 |   await page.unroute("**/api/planning/calculate");
  74 |   await page.route("**/api/planning/calculate", (route) =>
  75 |     route.fulfill({
  76 |       json: {
  77 |         ...PLAN_ANNA,
  78 |         input_summary: { ...PLAN_ANNA.input_summary, income: 0, expense: 0 },
  79 |       },
  80 |     }),
  81 |   );
  82 |   await page.goto("/");
  83 |   await expect(page.getByText("Пока нет данных для обзора")).toBeVisible();
  84 |   await expect(page.getByRole("link", { name: "Внести операции →" })).toBeVisible();
  85 | });
  86 | 
```