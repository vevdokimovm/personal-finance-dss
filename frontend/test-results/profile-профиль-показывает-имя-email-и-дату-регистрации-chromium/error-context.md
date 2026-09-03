# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: profile.spec.ts >> профиль показывает имя, email и дату регистрации
- Location: e2e/profile.spec.ts:11:1

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByText('anna@example.com')
Expected: visible
Error: strict mode violation: getByText('anna@example.com') resolved to 2 elements:
    1) <span class="fp-auth-topbar__email">anna@example.com</span> aka getByRole('banner').getByText('anna@example.com')
    2) <span class="fp-profile__value">anna@example.com</span> aka locator('#fp-main').getByText('anna@example.com')

Call log:
  - Expect "toBeVisible" with timeout 5000ms
  - waiting for getByText('anna@example.com')

```

# Page snapshot

```yaml
- generic [ref=e2]:
  - link "Перейти к содержимому" [ref=e3] [cursor=pointer]:
    - /url: "#fp-main"
  - banner [ref=e4]:
    - generic [ref=e5]:
      - generic [ref=e6]:
        - generic [ref=e7]: anna@example.com
        - button "Выйти" [ref=e8] [cursor=pointer]
      - generic [ref=e9]:
        - generic [ref=e10]: Тема оформления
        - combobox "Тема оформления" [ref=e11] [cursor=pointer]:
          - option "Светлая"
          - option "Тёмная"
          - option "Как в системе" [selected]
    - navigation "Основные разделы" [ref=e12]:
      - list [ref=e13]:
        - listitem [ref=e14]:
          - link "Финансовый обзор" [ref=e15] [cursor=pointer]:
            - /url: /
        - listitem [ref=e16]:
          - link "План распределения" [ref=e17] [cursor=pointer]:
            - /url: /planning
        - listitem [ref=e18]:
          - link "Операции" [ref=e19] [cursor=pointer]:
            - /url: /transactions
        - listitem [ref=e20]:
          - link "Кредиты и обязательства" [ref=e21] [cursor=pointer]:
            - /url: /obligations
        - listitem [ref=e22]:
          - link "Цели" [ref=e23] [cursor=pointer]:
            - /url: /goals
        - listitem [ref=e24]:
          - link "Ликвидные активы" [ref=e25] [cursor=pointer]:
            - /url: /banks
        - listitem [ref=e26]:
          - link "Профиль" [ref=e27] [cursor=pointer]:
            - /url: /profile
  - main [ref=e29]:
    - heading "Профиль" [level=1] [ref=e30]
    - generic [ref=e31]:
      - generic [ref=e32]:
        - generic [ref=e33]: Имя
        - generic [ref=e34]: Анна
      - generic [ref=e35]:
        - generic [ref=e36]: Email
        - generic [ref=e37]: anna@example.com
      - generic [ref=e38]:
        - generic [ref=e39]: В FINPILOT с
        - generic [ref=e40]: 15.01.2026
  - region "Notifications (F8)":
    - list
```

# Test source

```ts
  1  | import { expect, test } from "@playwright/test";
  2  | 
  3  | const PROFILE = {
  4  |   id: "u1",
  5  |   email: "anna@example.com",
  6  |   display_name: "Анна",
  7  |   email_verified: true,
  8  |   created_at: "2026-01-15",
  9  | };
  10 | 
  11 | test("профиль показывает имя, email и дату регистрации", async ({ page }) => {
  12 |   await page.route("**/api/auth/me", (route) => route.fulfill({ json: PROFILE }));
  13 |   await page.goto("/profile");
  14 |   await expect(page.getByText("Анна")).toBeVisible();
> 15 |   await expect(page.getByText("anna@example.com")).toBeVisible();
     |                                                    ^ Error: expect(locator).toBeVisible() failed
  16 | });
  17 | 
  18 | // 401 — ожидаемый исход в гостевом режиме (auth/me требует аутентификации, в отличие
  19 | // от transactions/obligations/goals/liquid-assets) — отдельная ветка от сетевой
  20 | // ошибки, без кнопки "Повторить" (a11y-auditor, Э4 партия 2, P1: одинаковое
  21 | // сообщение для 401 и сбоя давало тупиковый retry-цикл без объяснения причины).
  22 | test("неаутентифицированный доступ (401) — отдельное сообщение, без «Повторить»", async ({
  23 |   page,
  24 | }) => {
  25 |   await page.route("**/api/auth/me", (route) =>
  26 |     route.fulfill({ status: 401, json: { detail: "Not authenticated" } }),
  27 |   );
  28 |   await page.goto("/profile");
  29 |   await expect(page.getByText("Нужно войти в систему")).toBeVisible();
  30 |   await expect(page.getByRole("alert")).toHaveCount(0);
  31 |   await expect(page.getByRole("button", { name: "Повторить" })).toHaveCount(0);
  32 | });
  33 | 
  34 | test("сетевая ошибка (500) — состояние ошибки, повтор работает", async ({ page }) => {
  35 |   await page.route("**/api/auth/me", (route) =>
  36 |     route.fulfill({ status: 500, json: { detail: "internal error" } }),
  37 |   );
  38 |   await page.goto("/profile");
  39 |   await expect(page.getByRole("alert")).toContainText("Не получилось загрузить профиль");
  40 | 
  41 |   await page.unroute("**/api/auth/me");
  42 |   await page.route("**/api/auth/me", (route) => route.fulfill({ json: PROFILE }));
  43 |   await page.getByRole("button", { name: "Повторить" }).click();
  44 |   await expect(page.getByText("Анна")).toBeVisible();
  45 | });
  46 | 
```