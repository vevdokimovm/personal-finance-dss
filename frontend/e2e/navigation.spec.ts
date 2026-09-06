import { expect, test } from "@playwright/test";

/**
 * Навигационный каркас в настоящем браузере (v8.31.0, гипотеза H1 independent-expert).
 *
 * Юнит-тесты `AppNav.test.tsx` мокают `Link` и потому НЕ проверяют главное: что переход
 * действительно происходит внутри SPA, без перезагрузки документа. Именно это отличало
 * дефект H13 от обычной опечатки — три сырых `<a href>` работали визуально правильно
 * и при этом роняли кэш TanStack Query на каждом клике.
 */

const PROFILE = {
  id: "u1",
  email: "anna@example.com",
  display_name: "Анна",
  email_verified: true,
  created_at: "2026-01-15",
};

/** Каркас показывается только авторизованному — гостю все финансовые экраны отдают 401/403. */
async function signIn(page: import("@playwright/test").Page) {
  await page.route("**/api/auth/me", (route) => route.fulfill({ json: PROFILE }));
}

const SECTIONS = [
  { path: "/", label: "Финансовый обзор" },
  { path: "/planning", label: "План распределения" },
  { path: "/transactions", label: "Операции" },
  { path: "/obligations", label: "Кредиты и обязательства" },
  { path: "/goals", label: "Цели" },
  { path: "/banks", label: "Ликвидные активы" },
  { path: "/profile", label: "Профиль" },
];

test("все семь разделов достижимы кликом из каркаса", async ({ page }) => {
  await signIn(page);
  await page.goto("/profile");

  const nav = page.getByRole("navigation", { name: "Основные разделы" });
  await expect(nav).toBeVisible();

  for (const { path, label } of SECTIONS) {
    await expect(nav.getByRole("link", { name: label })).toHaveAttribute("href", path);
  }
});

test("активный раздел помечен aria-current на своём экране", async ({ page }) => {
  await signIn(page);
  await page.goto("/goals");

  const nav = page.getByRole("navigation", { name: "Основные разделы" });
  await expect(nav.getByRole("link", { name: "Цели" })).toHaveAttribute("aria-current", "page");
  // Корень не должен подсвечиваться на каждом экране: все пути начинаются со слэша,
  // поэтому у него activeOptions={{ exact: true }}.
  await expect(nav.getByRole("link", { name: "Финансовый обзор" })).not.toHaveAttribute(
    "aria-current",
    "page",
  );
});

test("переход по каркасу идёт внутри SPA, без перезагрузки документа (H13)", async ({ page }) => {
  await signIn(page);
  await page.goto("/profile");

  // Метка на объекте window переживает клиентскую навигацию и НЕ переживает
  // перезагрузку документа — прямая проверка того, что переход не сырой <a href>.
  await page.evaluate(() => {
    (window as unknown as { __spaMarker?: number }).__spaMarker = 42;
  });

  await page
    .getByRole("navigation", { name: "Основные разделы" })
    .getByRole("link", {
      name: "Цели",
    })
    .click();

  await expect(page).toHaveURL(/\/goals$/);
  const marker = await page.evaluate(
    () => (window as unknown as { __spaMarker?: number }).__spaMarker,
  );
  expect(marker, "документ перезагрузился — переход ушёл мимо роутера").toBe(42);
});

test("гость каркаса не видит — семь ссылок в гейт-403 были бы тупиками", async ({ page }) => {
  await page.route("**/api/auth/me", (route) =>
    route.fulfill({ status: 401, json: { detail: "Not authenticated" } }),
  );
  await page.goto("/login");

  await expect(page.getByRole("navigation", { name: "Основные разделы" })).toHaveCount(0);
});

test("skip-link уводит фокус мимо девяти контролов шапки (WCAG 2.4.1)", async ({ page }) => {
  await signIn(page);
  await page.goto("/goals");
  // Дождаться гидратации: без этого document.querySelector ниже отрабатывает по пустому
  // документу и возвращает null — тест «проходил бы» по несуществующей разметке.
  await expect(page.getByRole("navigation", { name: "Основные разделы" })).toBeVisible();

  // Проверяем позицию в DOM, а не «сколько раз нажать Tab»: в headless первое нажатие
  // тратится на вход фокуса в документ, и счётчик нажатий тест бы расшатывал.
  // Значение имеет именно то, что до skip-link нет ни одного фокусируемого элемента.
  const firstFocusableClass = await page.evaluate(() => {
    const el = document.querySelector(
      'a[href],button,input,select,textarea,[tabindex]:not([tabindex="-1"])',
    );
    return el ? el.className : null;
  });
  expect(firstFocusableClass, "skip-link обязан быть первым в tab-порядке").toContain(
    "fp-skip-link",
  );

  const skip = page.getByRole("link", { name: "Перейти к содержимому" });
  await skip.focus();
  // Не «есть в разметке», а «видна, когда нужна»: скрытая через display/visibility
  // ссылка выпала бы из tab-порядка и отменила бы собственный смысл.
  await expect(skip).toBeVisible();

  await page.keyboard.press("Enter");
  await expect(page.locator("#fp-main")).toBeFocused();
});

test("skip-link не занимает место в шапке, пока по нему не пришёл фокус", async ({ page }) => {
  await signIn(page);
  await page.goto("/goals");

  const skip = page.getByRole("link", { name: "Перейти к содержимому" });
  const nav = page.getByRole("navigation", { name: "Основные разделы" });
  const skipBox = await skip.boundingBox();
  const navBox = await nav.boundingBox();
  expect(skipBox, "skip-link должен существовать в разметке").not.toBeNull();
  expect(navBox).not.toBeNull();
  // Уведён над верхней кромкой окна, а не спрятан из дерева доступности.
  expect(skipBox!.y + skipBox!.height).toBeLessThanOrEqual(navBox!.y);
});

test("активный пункт не меняет ширину — каркас не перестраивается между экранами (H13-смежное)", async ({
  page,
}) => {
  await signIn(page);

  await page.goto("/goals");
  const nav = page.getByRole("navigation", { name: "Основные разделы" });
  const inactive = await nav.getByRole("link", { name: "Операции" }).boundingBox();

  await page.goto("/transactions");
  const active = await nav.getByRole("link", { name: "Операции" }).boundingBox();

  await expect(nav.getByRole("link", { name: "Операции" })).toHaveAttribute("aria-current", "page");
  expect(
    Math.abs(active!.width - inactive!.width),
    "ширина активного пункта уехала — перенос строк будет прыгать при переходах",
  ).toBeLessThan(1);
});
