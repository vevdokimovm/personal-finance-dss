import { expect, test } from "@playwright/test";

/**
 * Выгрузка плана в настоящем браузере (v8.35.0).
 *
 * Юнит-тесты мокают `downloadFile` целиком и потому НЕ проверяют главного: что файл
 * действительно доходит до пользователя и приходит под именем, которое дал сервер.
 * Playwright ловит событие `download` — это единственный способ убедиться, что цепочка
 * fetch → blob → `<a download>` → клик реально срабатывает в браузере, а не только
 * в jsdom, где `click()` замокан.
 */

const PROFILE = {
  id: "u1",
  email: "anna@example.com",
  display_name: "Анна",
  email_verified: true,
  created_at: "2026-01-15",
};

const PLAN = {
  risk_profile: "Сбалансированный",
  indicators: { Rt: 39500, Lt: 0, Dt: 0.3472, BLR: 3.4, It: 180000, Et: 78000, SigmaP: 62500 },
  top3: [
    { id: "a0100", name: "Всё в резерв", x_obligations: 0, x_reserve: 39500, x_goals: 0, utility: 0.8 },
  ],
  ranked: [],
  admissible_count: 1,
  alternatives_total: 1,
  input_summary: {
    income: 180000, expense: 78000, bliq: 0,
    transactions_count: 12, obligations_count: 1, goals_count: 0,
  },
};

async function setup(page: import("@playwright/test").Page) {
  await page.route("**/api/auth/me", (route) => route.fulfill({ json: PROFILE }));
  await page.route("**/api/notifications/unread-count", (route) =>
    route.fulfill({ json: { unread_count: 0 } }),
  );
  await page.route("**/api/planning/calculate", (route) => route.fulfill({ json: PLAN }));
  await page.route("**/api/planning/forecast", (route) =>
    route.fulfill({ json: { current: {}, horizon: 12, forecast: [] } }),
  );
  await page.route("**/api/planning/history", (route) =>
    route.fulfill({ json: { items: [], count: 0 } }),
  );
}

test("CSV реально скачивается под именем от сервера", async ({ page }) => {
  await setup(page);
  await page.route("**/api/planning/export.csv", (route) =>
    route.fulfill({
      status: 200,
      headers: {
        "Content-Type": "text/csv; charset=utf-8",
        "Content-Disposition": 'attachment; filename="finpilot-plan-2026-09-03.csv"',
      },
      body: "показатель;значение\nRt;39500",
    }),
  );
  await page.goto("/planning");

  const [download] = await Promise.all([
    page.waitForEvent("download"),
    page.getByRole("button", { name: /CSV/ }).click(),
  ]);

  // Имя даёт СЕРВЕР (Content-Disposition), фронт его не выдумывает — иначе появился бы
  // второй источник правды об одном имени.
  expect(download.suggestedFilename()).toBe("finpilot-plan-2026-09-03.csv");
});

test("403 не скачивается файлом, а показывает панель согласия", async ({ page }) => {
  await setup(page);
  await page.route("**/api/planning/export.csv", (route) =>
    route.fulfill({
      status: 403,
      json: {
        detail: {
          code: "consent_required",
          consent_type: "financial_data",
          message: "Для работы с финансовыми данными нужно отдельное согласие.",
          document: { title: "Согласие", url: "/legal/financial-consent" },
        },
      },
    }),
  );
  await page.goto("/planning");

  let downloaded = false;
  page.on("download", () => {
    downloaded = true;
  });

  await page.getByRole("button", { name: /CSV/ }).click();

  // Главное: пользователь получает объяснение и кнопку, а НЕ файл `.csv` с текстом
  // ошибки внутри. Панель сознательно НЕ печатает серверный текст дословно (он
  // отправляет «в настройки профиля», а кнопка делает то же самое здесь) — поэтому
  // сверяем её собственный заголовок и действие, а не тело ответа.
  await expect(page.getByText("Нужно согласие на финансовые данные")).toBeVisible();
  await expect(page.getByRole("button", { name: /Дать согласие/ })).toBeVisible();
  expect(downloaded, "отказ скачался файлом — ровно то, что этот батч предотвращает").toBe(false);
});

test("после отказа сервера кнопки снова доступны — тупика нет", async ({ page }) => {
  await setup(page);
  await page.route("**/api/planning/export.pdf", (route) =>
    route.fulfill({ status: 500, json: { detail: "internal error" } }),
  );
  await page.goto("/planning");

  const pdf = page.getByRole("button", { name: /PDF/ });
  await pdf.click();
  await expect(pdf).toHaveAttribute("aria-busy", "false");
});
