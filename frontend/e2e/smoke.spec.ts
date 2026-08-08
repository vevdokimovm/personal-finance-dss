import { expect, test } from "@playwright/test";

test("каркас открывается и рендерит плейсхолдер", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "FINPILOT — каркас вехи 8" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Проверка каркаса" })).toBeVisible();
});
