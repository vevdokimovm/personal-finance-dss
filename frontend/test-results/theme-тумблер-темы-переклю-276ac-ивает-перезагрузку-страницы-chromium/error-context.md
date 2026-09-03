# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: theme.spec.ts >> тумблер темы переключает data-theme и переживает перезагрузку страницы
- Location: e2e/theme.spec.ts:39:1

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: locator.selectOption: Test timeout of 30000ms exceeded.
Call log:
  - waiting for getByRole('combobox', { name: 'Тема оформления' })
    - locator resolved to <select id="_r_0_" class="fp-theme-toggle__select">…</select>
  - attempting select option action
    - waiting for element to be visible and enabled
  - element was detached from the DOM, retrying

```

# Page snapshot

```yaml
- generic [ref=e4]:
  - strong [ref=e5]: Something went wrong!
  - button "Show Error" [ref=e6]
```

# Test source

```ts
  1  | import { expect, test } from "@playwright/test";
  2  | 
  3  | const PLAN_ANNA = {
  4  |   risk_profile: "Сбалансированный",
  5  |   indicators: { Rt: 39500, Lt: 0, Dt: 0.3472, BLR: 3.4, It: 180000, Et: 78000, SigmaP: 62500 },
  6  |   top3: [
  7  |     {
  8  |       id: "a0100",
  9  |       name: "Всё в резерв",
  10 |       x_obligations: 0,
  11 |       x_reserve: 39500,
  12 |       x_goals: 0,
  13 |       utility: 0.8,
  14 |     },
  15 |   ],
  16 |   admissible_count: 66,
  17 |   alternatives_total: 66,
  18 |   input_summary: {
  19 |     income: 180000,
  20 |     expense: 78000,
  21 |     bliq: 0,
  22 |     transactions_count: 12,
  23 |     obligations_count: 1,
  24 |     goals_count: 0,
  25 |   },
  26 | };
  27 | 
  28 | const FORECAST_ANNA = {
  29 |   current: { Bt: 265000, Rt: 39500, Lt: 0.281, Dt: 0.3472 },
  30 |   horizon: 12,
  31 |   forecast: [{ period: 12, Rt: 813519, Rt_p10: 682866, Rt_p90: 952920 }],
  32 | };
  33 | 
  34 | test.beforeEach(async ({ page }) => {
  35 |   await page.route("**/api/planning/calculate", (route) => route.fulfill({ json: PLAN_ANNA }));
  36 |   await page.route("**/api/planning/forecast", (route) => route.fulfill({ json: FORECAST_ANNA }));
  37 | });
  38 | 
  39 | test("тумблер темы переключает data-theme и переживает перезагрузку страницы", async ({ page }) => {
  40 |   await page.goto("/");
  41 |   const html = page.locator("html");
  42 |   const select = page.getByRole("combobox", { name: "Тема оформления" });
  43 | 
> 44 |   await select.selectOption("light");
     |                ^ Error: locator.selectOption: Test timeout of 30000ms exceeded.
  45 |   await expect(html).toHaveAttribute("data-theme", "light");
  46 | 
  47 |   await select.selectOption("dark");
  48 |   await expect(html).toHaveAttribute("data-theme", "dark");
  49 | 
  50 |   // Выбор запомнен (Zustand persist -> localStorage) — переживает reload.
  51 |   await select.selectOption("light");
  52 |   await page.reload();
  53 |   await expect(html).toHaveAttribute("data-theme", "light");
  54 |   await expect(page.getByRole("combobox", { name: "Тема оформления" })).toHaveValue("light");
  55 | });
  56 | 
  57 | test("обе темы «Спокойный» реально достижимы и рендерят контент без ошибок", async ({ page }) => {
  58 |   await page.goto("/");
  59 |   const select = page.getByRole("combobox", { name: "Тема оформления" });
  60 | 
  61 |   await select.selectOption("dark");
  62 |   await expect(page.locator(".fp-hero-value")).toBeVisible();
  63 |   await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  64 | 
  65 |   await select.selectOption("light");
  66 |   await expect(page.locator(".fp-hero-value")).toBeVisible();
  67 |   await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
  68 | });
  69 | 
```