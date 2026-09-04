import { expect, test } from "@playwright/test";

/**
 * Юридический контур фронта в настоящем браузере (v8.40.0): cookie-баннер (L6),
 * футер со ссылками на документы (L7), дисклеймер 39-ФЗ на экране плана (L5).
 *
 * Юнит-тесты проверяют логику каждого блока по отдельности. Только браузер показывает,
 * что блоки реально доезжают до страницы — включая гостевую, где их и требует закон.
 */

const LEGAL = {
  documents: {
    privacy_policy: {
      title: "Политика обработки персональных данных",
      version: "1.0",
      effective_from: "2026-07-29",
      url: "/legal/privacy",
    },
    cookie_policy: {
      title: "Политика использования файлов cookie",
      version: "1.0",
      effective_from: "2026-07-29",
      url: "/legal/cookies",
    },
  },
  disclaimer_39fz:
    "FINPILOT не является инвестиционным советником и не оказывает услуг по " +
    "инвестиционному консультированию.",
};

async function stubLegal(page: import("@playwright/test").Page) {
  await page.route("**/api/legal/documents", (route) => route.fulfill({ json: LEGAL }));
  await page.route("**/api/notifications/unread-count", (route) =>
    route.fulfill({ json: { unread_count: 0 } }),
  );
}

test("гость видит cookie-баннер с раздельным выбором (L6)", async ({ page }) => {
  await stubLegal(page);
  await page.route("**/api/auth/me", (route) =>
    route.fulfill({ status: 401, json: { detail: "Not authenticated" } }),
  );

  await page.goto("/login");

  // Оба варианта видимы сразу: отказ стоит ровно одного клика, как и согласие.
  await expect(page.getByRole("button", { name: "Принять всё" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Только необходимые" })).toBeVisible();

  await page.getByRole("button", { name: "Только необходимые" }).click();
  await expect(page.getByRole("button", { name: "Принять всё" })).toHaveCount(0);

  // Перезагрузка не спрашивает заново: выбор сохранён вместе с редакцией политики.
  await page.reload();
  await expect(page.getByRole("button", { name: "Принять всё" })).toHaveCount(0);
});

test("футер с документами есть на гостевой странице (L7)", async ({ page }) => {
  await stubLegal(page);
  await page.route("**/api/auth/me", (route) =>
    route.fulfill({ status: 401, json: { detail: "Not authenticated" } }),
  );

  await page.goto("/login");

  const footer = page.getByRole("navigation", { name: "Юридические документы" });
  await expect(footer.getByRole("link", { name: /персональных данных/ })).toHaveAttribute(
    "href",
    "/legal/privacy",
  );
  await expect(footer.getByRole("link", { name: /cookie/ })).toHaveAttribute(
    "href",
    "/legal/cookies",
  );
  // Редакция видна: согласие даётся на конкретный текст. Дата по-русски, и когда
  // редакция у всех документов одна — она сказана один раз под списком, а не повторена
  // у каждого (design-critic, v8.40.0).
  await expect(page.getByText("ред. 1.0 от 29.07.2026")).toBeVisible();
  // Отзыв согласия существует не только в комментарии.
  await expect(page.getByRole("button", { name: "Настройки cookie" })).toBeVisible();
});

test("дисклеймер 39-ФЗ стоит на экране рекомендаций (L5)", async ({ page }) => {
  await stubLegal(page);
  await page.route("**/api/auth/me", (route) =>
    route.fulfill({
      json: { id: "u1", email: "anna@example.com", email_verified: true, created_at: "2026-01-15" },
    }),
  );
  await page.route("**/api/planning/calculate", (route) =>
    route.fulfill({
      json: {
        risk_profile: "Сбалансированный",
        indicators: { Rt: 39500, Lt: 4, Dt: 0.34, BLR: 3.4 },
        bliq_preallocation: {},
        weights: { w_rt: 0.3, w_lt: 0.25, w_dt: 0.25, w_goals: 0.2, lt_target: 6 },
        top3: [],
        ranked: [],
        rejected: [],
        admissible_count: 0,
        alternatives_total: 0,
        rejected_count: 0,
        input_summary: {
          income: 180000,
          expense: 78000,
          bliq: 15000,
          transactions_count: 12,
          obligations_count: 1,
          goals_count: 2,
          liquid_assets_count: 2,
          r_bench: 0.16,
          r_bench_source: "key_rate",
          l_min: 3,
          risk_tolerance: 3,
        },
        disclaimer: LEGAL.disclaimer_39fz,
      },
    }),
  );

  await page.route("**/api/planning/forecast", (route) =>
    route.fulfill({
      json: {
        current: { Bt: 265000, Rt: 39500, Lt: 4, Dt: 0.34 },
        horizon: 12,
        forecast: [{ period: 12, Rt: 813519 }],
      },
    }),
  );

  await page.goto("/planning");

  // 🔴 Проверяем ИМЕННО блок на экране плана, а не любое вхождение текста на странице.
  // Пока дисклеймер дублировался в футере, этот тест был зелёным по ложной причине:
  // он находил футерное вхождение и не заметил бы отсутствия текста там, где его
  // требует L5 — рядом с рекомендацией.
  const disclaimer = page.getByRole("region", { name: "Важно о рекомендации" });
  await expect(disclaimer).toBeVisible();
  await expect(disclaimer).toContainText("не является инвестиционным советником");
});

/* 🔴 Экран документа в НАСТОЯЩЕМ браузере (v8.44.0). Юнит-тесты проверяют разметку
   при подменённом роутере; только браузер показывает, что маршрут `/legal/$doc`
   действительно отвечает по адресу из реестра, markdown превращается в разметку,
   а переход из футера не перезагружает приложение. */
const PRIVACY_TEXT = `# Политика в отношении обработки персональных данных

Настоящая Политика определяет порядок обработки персональных данных.

## 1. Общие положения и сведения об Операторе

1.1. Оператором выступает сервис FINPILOT.

| | |
|---|---|
| **Оператор** | сервис FINPILOT |
| **E-mail для обращений** | finpilot.help@proton.me |
`;

async function stubDocumentOn(
  target: import("@playwright/test").Page | import("@playwright/test").BrowserContext,
) {
  await target.route("**/api/legal/documents/privacy_policy", (route) =>
    route.fulfill({
      json: {
        slug: "privacy_policy",
        title: "Политика обработки персональных данных",
        version: "1.0",
        effective_from: "2026-07-29",
        url: "/legal/privacy",
        content: PRIVACY_TEXT,
      },
    }),
  );
}

test("гость открывает политику из футера и читает настоящий текст (L7)", async ({ page }) => {
  await stubLegal(page);
  await stubDocumentOn(page);
  await page.route("**/api/auth/me", (route) => route.fulfill({ status: 401, json: {} }));

  await page.goto("/login");
  await page.getByRole("link", { name: /Политика обработки персональных данных/ }).click();

  // Текст документа, а не заглушка и не пустая страница.
  await expect(page.getByText(/Оператором выступает сервис FINPILOT/)).toBeVisible();
  // Markdown стал разметкой: раздел — настоящий заголовок.
  await expect(page.getByRole("heading", { name: /1\. Общие положения/ })).toBeVisible();
  // Таблица осталась таблицей, несмотря на прокрутку по горизонтали.
  await expect(page.getByRole("table")).toBeVisible();
  // Заголовок вкладки называет документ (WCAG 2.4.2).
  await expect(page).toHaveTitle(/Политика обработки персональных данных/);
});

/* 🔴 Проверяется ИМЕННО SPA-навигация, а не сохранение формы. Форму от потери спасает
   не `Link`, а отдельная ссылка у чекбокса согласия с `target="_blank"`: при переходе
   в той же вкладке React размонтирует страницу регистрации, и введённое исчезает
   одинаково что с `Link`, что с `<a href>`. `Link` убирает полную перезагрузку
   приложения — не больше и не меньше. */
test("переход на документ не перезагружает приложение", async ({ page }) => {
  await stubLegal(page);
  await stubDocumentOn(page);
  await page.route("**/api/auth/me", (route) => route.fulfill({ status: 401, json: {} }));

  await page.goto("/register");
  // Метка на объекте окна переживает SPA-навигацию и гибнет при полной перезагрузке.
  await page.evaluate(() => {
    (window as unknown as { __spa?: boolean }).__spa = true;
  });

  await page
    .getByRole("link", { name: /Политика обработки персональных данных/ })
    .first()
    .click();
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
  expect(await page.evaluate(() => (window as unknown as { __spa?: boolean }).__spa)).toBe(true);
});

/* Согласие, данное без возможности прочитать текст здесь же, — неинформированное.
   Ссылка открывает документ НОВОЙ вкладкой: в той же заполненная форма потерялась бы. */
test("политику можно прочитать прямо из формы регистрации, не потеряв введённое", async ({
  page,
  context,
}) => {
  /* Заглушки — на КОНТЕКСТ, а не на страницу: документ открывается новой вкладкой,
     и `page.route` на неё не распространяется — вкладка ушла бы за настоящим API. */
  await context.route("**/api/legal/documents", (route) => route.fulfill({ json: LEGAL }));
  await stubDocumentOn(context);
  await context.route("**/api/notifications/unread-count", (route) =>
    route.fulfill({ json: { unread_count: 0 } }),
  );
  await context.route("**/api/auth/me", (route) => route.fulfill({ status: 401, json: {} }));

  await page.goto("/register");
  await page.getByLabel("Email").fill("keep-me@test.io");

  const [documentTab] = await Promise.all([
    context.waitForEvent("page"),
    page.getByRole("link", { name: /прочитать политику/i }).click(),
  ]);
  await documentTab.waitForLoadState();
  await expect(documentTab.getByText(/Оператором выступает сервис FINPILOT/)).toBeVisible();

  // Исходная вкладка нетронута: введённое на месте.
  await expect(page.getByLabel("Email")).toHaveValue("keep-me@test.io");
});
