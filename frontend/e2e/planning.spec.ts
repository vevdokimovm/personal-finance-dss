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

const PREFS_ANNA = {
  id: 1,
  l_min: 3,
  risk_tolerance: 3,
  horizon: 12,
  r_bench: 0.16,
  base_currency: "RUB",
  iis_type: "none",
  iis_contributed_this_year: 0,
};

test.beforeEach(async ({ page }) => {
  await page.route("**/api/planning/calculate", (route) => route.fulfill({ json: PLAN_ANNA }));
  await page.route("**/api/planning/forecast", (route) => route.fulfill({ json: FORECAST_ANNA }));
  await page.route("**/api/user-prefs", (route) => route.fulfill({ json: PREFS_ANNA }));
});

test("план распределения показывает риск-профиль и входные данные", async ({ page }) => {
  await page.goto("/planning");
  // Метка профиля теперь встречается дважды: в панели параметров (выбор) и в самом
  // плане (по чему он посчитан). Проверяем именно план — панель у неё свои тесты.
  await expect(page.locator(".fp-planning__risk-badge")).toContainText("Сбалансированный");
  await expect(page.getByText("12 опер. · 1 обяз. · 2 целей")).toBeVisible();
  // Слово «Резерв» встречается дважды: в легенде столбца и в подсказке к ползункам
  // «что если». Локатор сужен до легенды — там оно несёт сумму, ради которой тест
  // и написан; широкий /Резерв/ ловил оба и падал на strict mode.
  await expect(page.getByText(/^Резерв — /)).toBeVisible();
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
  // Метка профиля есть и в бейдже плана, и в панели параметров — проверяем бейдж.
  await expect(page.locator(".fp-planning__risk-badge")).toContainText("Сбалансированный");
});

/* 🔴 Параметры расчёта (v8.42.0). До этого батча риск-профиль в React изменить было
   нельзя вообще — контролы жили только в Jinja, и `planning.html` оставался единственным
   способом настроить план. Юнит-тесты проверяют логику черновика; браузер показывает,
   что цикл «выбрал → пересчитал → ушло на сервер» действительно замыкается. */
test("риск-профиль выбирается и уходит на сервер по кнопке (v8.42.0)", async ({ page }) => {
  let sent: Record<string, unknown> | null = null;
  await page.route("**/api/user-prefs", async (route) => {
    if (route.request().method() === "PATCH") {
      sent = route.request().postDataJSON();
      return route.fulfill({ json: { ...PREFS_ANNA, risk_tolerance: 5 } });
    }
    return route.fulfill({ json: PREFS_ANNA });
  });

  await page.goto("/planning");

  const settings = page.getByRole("region", { name: "Параметры расчёта" });
  await expect(settings.getByRole("radio", { name: "Сбалансированный" })).toBeChecked();

  // Выбор сам по себе НЕ пересчитывает: пересчёт тяжёлый, дёргать его на каждый клик
  // значит превратить настройку в подвисание.
  await settings.getByRole("radio", { name: "Агрессивный", exact: true }).check();
  expect(sent).toBeNull();
  await expect(page.getByText(/по прежним параметрам/)).toBeVisible();

  await settings.getByRole("button", { name: /Сохранить и пересчитать/ }).click();
  await expect.poll(() => sent).not.toBeNull();
  expect(sent).toMatchObject({ risk_tolerance: 5 });
});

test("ставка показана процентами, а уходит долей (v8.42.0)", async ({ page }) => {
  let sent: Record<string, unknown> | null = null;
  await page.route("**/api/user-prefs", async (route) => {
    if (route.request().method() === "PATCH") {
      sent = route.request().postDataJSON();
      return route.fulfill({ json: PREFS_ANNA });
    }
    return route.fulfill({ json: PREFS_ANNA });
  });

  await page.goto("/planning");

  const slider = page.getByLabel(/Ставка по накоплениям/);
  await expect(slider).toHaveValue("16");
  await slider.fill("20");
  await page.getByRole("button", { name: /Сохранить и пересчитать/ }).click();

  await expect.poll(() => sent).not.toBeNull();
  // Ошибка преобразования дала бы 2000% или 0.2% — и то, и другое молча исказит расчёт.
  expect(sent).toMatchObject({ r_bench: 0.2 });
});
