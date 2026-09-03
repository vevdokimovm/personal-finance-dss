# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: planning.spec.ts >> план распределения показывает риск-профиль и входные данные
- Location: e2e/planning.spec.ts:68:1

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByText(/Резерв/)
Expected: visible
Error: strict mode violation: getByText(/Резерв/) resolved to 2 elements:
    1) <span>…</span> aka getByText('Резерв — 39 500,00 ₽ (100%)')
    2) <p class="fp-whatif__hint">Подвиньте ползунки — столбец и суммы выше пересчи…</p> aka getByText('Подвиньте ползунки — столбец и суммы выше пересчитаются, «Резерв» — остаток')

Call log:
  - Expect "toBeVisible" with timeout 5000ms
  - waiting for getByText(/Резерв/)

```

# Page snapshot

```yaml
- generic [active] [ref=e1]:
  - generic [ref=e2]:
    - link "Перейти к содержимому" [ref=e3] [cursor=pointer]:
      - /url: "#fp-main"
    - banner [ref=e4]:
      - generic [ref=e6]:
        - generic [ref=e7]: Тема оформления
        - combobox "Тема оформления" [ref=e8] [cursor=pointer]:
          - option "Светлая"
          - option "Тёмная"
          - option "Как в системе" [selected]
    - main [ref=e10]:
      - generic [ref=e11]:
        - heading "План распределения" [level=1] [ref=e12]
        - generic [ref=e13]:
          - generic [ref=e14]: "Риск-профиль:"
          - text: Сбалансированный
      - generic [ref=e15]:
        - generic [ref=e16]:
          - term [ref=e17]: Доходы
          - definition [ref=e18]: 180 000 ₽
        - generic [ref=e19]:
          - term [ref=e20]: Расходы
          - definition [ref=e21]: 78 000,00 ₽
        - generic [ref=e22]:
          - term [ref=e23]: Свободный резерв (B_liq)
          - definition [ref=e24]: 15 000,00 ₽
        - generic [ref=e25]:
          - term [ref=e26]: Учтено
          - definition [ref=e27]: 12 опер. · 1 обяз. · 2 целей
      - region "Ключевые показатели" [ref=e28]:
        - article [ref=e29]:
          - generic [ref=e30]:
            - generic [ref=e31]: Ликвидность
            - generic [ref=e32]: 0,0 мес. автономии
          - generic [ref=e33]: 0,0
          - generic [ref=e34]:
            - text: Месяцев без дохода, если использовать только свободный резерв (без целей).
            - generic [ref=e40]: Lt = Bliq / Σe
        - article [ref=e41]:
          - generic [ref=e42]:
            - generic [ref=e43]: Долговая нагрузка (ПДН)
            - generic [ref=e44]: порог 40%
          - generic [ref=e45]: 34,7%
          - generic [ref=e46]:
            - text: Доля дохода на кредиты. Запас 5.3 п.п. до порога.
            - generic [ref=e55]:
              - math [ref=e57]:
                - generic [ref=e59]:
                  - generic [ref=e60]:
                    - generic [ref=e61]: D
                    - generic [ref=e62]: t
                  - generic [ref=e63]: =
                  - generic [ref=e65]:
                    - generic [ref=e66]:
                      - generic [ref=e67]: ∑
                      - generic [ref=e68]: P
                    - generic [ref=e69]: I
              - generic [ref=e70]:
                - generic [ref=e71]:
                  - generic [ref=e72]:
                    - text: D
                    - generic [ref=e73]: t
                  - text: =
                - generic [ref=e86]:
                  - generic [ref=e87]: I
                  - generic [ref=e89]: ∑ P
        - article [ref=e93]:
          - generic [ref=e94]:
            - generic [ref=e95]: Подушка со всеми накоплениями
            - generic [ref=e96]: включая цели
          - generic [ref=e97]: 3,4
          - generic [ref=e98]:
            - text: Месяцев без дохода, если использовать все текущие накопления.
            - generic [ref=e101]:
              - math [ref=e103]:
                - generic [ref=e105]:
                  - generic [ref=e106]: B
                  - generic [ref=e107]: L
                  - generic [ref=e108]: R
                  - generic [ref=e109]: =
                  - generic [ref=e111]:
                    - generic [ref=e112]:
                      - generic [ref=e113]:
                        - generic [ref=e114]: B
                        - generic [ref=e115]: t
                      - generic [ref=e116]: +
                      - generic [ref=e117]:
                        - generic [ref=e118]: B
                        - generic [ref=e119]: t
                        - generic [ref=e120]:
                          - generic [ref=e121]: l
                          - generic [ref=e122]: i
                          - generic [ref=e123]: q
                    - generic [ref=e124]:
                      - generic [ref=e125]: ∑
                      - generic [ref=e126]: e
              - generic [ref=e127]:
                - generic [ref=e128]: BLR =
                - generic [ref=e134]:
                  - generic [ref=e135]: ∑ e
                  - generic [ref=e137]:
                    - generic [ref=e138]:
                      - text: B
                      - generic [ref=e139]: t
                    - text: +
                    - generic [ref=e147]:
                      - text: B
                      - generic [ref=e151]:
                        - generic [ref=e152]: t
                        - generic [ref=e153]: liq
      - generic [ref=e161]:
        - heading "Куда пойдут свободные деньги" [level=2] [ref=e162]
        - paragraph [ref=e163]: Рекомендация СППР (Всё в резерв).
        - generic [ref=e165]:
          - generic [ref=e166]: Досрочное погашение — 0,00 ₽ (0%)
          - generic [ref=e168]: Резерв — 39 500,00 ₽ (100%)
          - generic [ref=e170]: Цели — 0,00 ₽ (0%)
        - generic [ref=e172]:
          - heading "Что если распределить иначе?" [level=3] [ref=e174]
          - paragraph [ref=e175]: Подвиньте ползунки — столбец и суммы выше пересчитаются, «Резерв» — остаток.
          - generic [ref=e177]:
            - generic [ref=e178]:
              - generic [ref=e179]: Досрочное погашение
              - generic [ref=e180]: 0%
            - slider "Досрочное погашение" [ref=e181]: "0"
          - generic [ref=e182]:
            - generic [ref=e183]: "Свободный поток: 0,00 ₽"
            - generic [ref=e184]: "Ликвидность: 1,2 мес."
            - generic [ref=e185]:
              - text: "ПДН: 34,7%"
              - generic [ref=e186]: порог 40%
          - status [ref=e187]: Свободный поток 0,00 ₽, ликвидность 1,2 мес., ПДН 34,7%.
      - generic [ref=e189]:
        - heading "Все варианты распределения" [level=2] [ref=e190]
        - button "Показать все (2)" [ref=e191] [cursor=pointer]:
          - text: Показать все (2)
          - generic [ref=e192]: →
      - generic [ref=e193]:
        - heading "Прогноз резерва на 12 месяцев" [level=2] [ref=e194]
        - paragraph [ref=e195]: SES + Monte-Carlo, интервал 80% (p10–p90) вокруг медианного сценария.
        - generic [ref=e196]:
          - paragraph [ref=e197]: Горизонт и ставка ниже — сценарий «что если», не решение СППР. Результат обновится в графике, таблице и подписи ниже.
          - generic [ref=e198]:
            - generic [ref=e199]:
              - generic [ref=e200]: Горизонт
              - combobox "Горизонт" [ref=e201] [cursor=pointer]:
                - option "3 мес."
                - option "6 мес."
                - option "12 мес." [selected]
                - option "24 мес."
            - generic [ref=e202]:
              - generic [ref=e203]:
                - generic [ref=e204]: Ставка капитализации
                - generic [ref=e205]: NaN%
              - slider "Ставка капитализации" [ref=e207]: "15"
              - generic [ref=e208]:
                - generic [ref=e209]: 0%
                - generic [ref=e210]: 30%
          - status [ref=e211]
        - status [ref=e212]
        - application [ref=e216]:
          - generic [ref=e233]:
            - generic [ref=e234]:
              - generic [ref=e235]: сейчас
              - generic [ref=e237]: 12 мес
            - generic [ref=e239]:
              - generic [ref=e240]: 0,00 ₽
              - generic [ref=e242]: 250 000 ₽
              - generic [ref=e244]: 500 000 ₽
              - generic [ref=e246]: 750 000 ₽
              - generic [ref=e248]: 1 000 000 ₽
        - table [ref=e250]:
          - caption [ref=e251]: Помесячный прогноз резерва — медиана и диапазон 80% (p10–p90) по каждому месяцу
          - rowgroup [ref=e252]:
            - row [ref=e253]:
              - columnheader "Месяц" [ref=e254]
              - columnheader "Медиана" [ref=e255]
              - columnheader "p10" [ref=e256]
              - columnheader "p90" [ref=e257]
          - rowgroup [ref=e258]:
            - row [ref=e259]:
              - cell "сейчас" [ref=e260]
              - cell "39 500,00 ₽" [ref=e261]
              - cell "39 500,00 ₽" [ref=e262]
              - cell "39 500,00 ₽" [ref=e263]
            - row [ref=e264]:
              - cell "12 мес" [ref=e265]
              - cell "813 519 ₽" [ref=e266]
              - cell "682 866 ₽" [ref=e267]
              - cell "952 920 ₽" [ref=e268]
        - generic [ref=e269]:
          - generic [ref=e270]: "Медиана к 12 мес: 813 519 ₽"
          - generic [ref=e271]: "Диапазон (80%): 682 866 ₽ – 952 920 ₽"
    - region "Notifications (F8)":
      - list
  - generic [ref=e272]: 0,00 ₽
```

# Test source

```ts
  1   | import { expect, test } from "@playwright/test";
  2   | 
  3   | const PLAN_ANNA = {
  4   |   risk_profile: "Сбалансированный",
  5   |   indicators: { Rt: 39500, Lt: 0, Dt: 0.3472, BLR: 3.4, It: 180000, Et: 78000, SigmaP: 62500 },
  6   |   top3: [
  7   |     {
  8   |       id: "a0100",
  9   |       name: "Всё в резерв",
  10  |       x_obligations: 0,
  11  |       x_reserve: 39500,
  12  |       x_goals: 0,
  13  |       utility: 0.8,
  14  |       Rt_new: 0,
  15  |       Lt_new: 1.2,
  16  |       Dt_new: 0.3472,
  17  |       is_recommended: true,
  18  |     },
  19  |   ],
  20  |   ranked: [
  21  |     {
  22  |       id: "a0100",
  23  |       name: "Всё в резерв",
  24  |       x_obligations: 0,
  25  |       x_reserve: 39500,
  26  |       x_goals: 0,
  27  |       utility: 0.8,
  28  |       Rt_new: 0,
  29  |       Lt_new: 1.2,
  30  |       Dt_new: 0.3472,
  31  |       is_recommended: true,
  32  |     },
  33  |     {
  34  |       id: "a1000",
  35  |       name: "Всё на погашение долга",
  36  |       x_obligations: 39500,
  37  |       x_reserve: 0,
  38  |       x_goals: 0,
  39  |       utility: 0.62,
  40  |       Rt_new: 0,
  41  |       Lt_new: 0.2,
  42  |       Dt_new: 0.28,
  43  |     },
  44  |   ],
  45  |   admissible_count: 2,
  46  |   alternatives_total: 66,
  47  |   input_summary: {
  48  |     income: 180000,
  49  |     expense: 78000,
  50  |     bliq: 15000,
  51  |     transactions_count: 12,
  52  |     obligations_count: 1,
  53  |     goals_count: 2,
  54  |   },
  55  | };
  56  | 
  57  | const FORECAST_ANNA = {
  58  |   current: { Bt: 265000, Rt: 39500, Lt: 0.281, Dt: 0.3472 },
  59  |   horizon: 12,
  60  |   forecast: [{ period: 12, Rt: 813519, Rt_p10: 682866, Rt_p90: 952920 }],
  61  | };
  62  | 
  63  | test.beforeEach(async ({ page }) => {
  64  |   await page.route("**/api/planning/calculate", (route) => route.fulfill({ json: PLAN_ANNA }));
  65  |   await page.route("**/api/planning/forecast", (route) => route.fulfill({ json: FORECAST_ANNA }));
  66  | });
  67  | 
  68  | test("план распределения показывает риск-профиль и входные данные", async ({ page }) => {
  69  |   await page.goto("/planning");
  70  |   await expect(page.getByText("Сбалансированный")).toBeVisible();
  71  |   await expect(page.getByText("12 опер. · 1 обяз. · 2 целей")).toBeVisible();
> 72  |   await expect(page.getByText(/Резерв/)).toBeVisible();
      |                                          ^ Error: expect(locator).toBeVisible() failed
  73  | });
  74  | 
  75  | test("дефицит на /planning — fail-loud сообщение вместо аллокации", async ({ page }) => {
  76  |   await page.unroute("**/api/planning/calculate");
  77  |   await page.route("**/api/planning/calculate", (route) =>
  78  |     route.fulfill({ json: { ...PLAN_ANNA, top3: [], ranked: [], admissible_count: 0 } }),
  79  |   );
  80  |   await page.goto("/planning");
  81  |   await expect(page.getByText("Плана распределения нет")).toBeVisible();
  82  | });
  83  | 
  84  | test("браузер альтернатив: свёрнут по умолчанию, раскрывается и сортируется", async ({ page }) => {
  85  |   await page.goto("/planning");
  86  |   await expect(page.getByText("Всё на погашение долга")).not.toBeVisible();
  87  |   await page.getByRole("button", { name: "Показать все (2)" }).click();
  88  |   await expect(page.getByText("Всё на погашение долга")).toBeVisible();
  89  |   await expect(page.getByText("рекомендовано")).toBeVisible();
  90  | 
  91  |   await page.getByLabel("Сортировать по").selectOption("Долговой нагрузке (ПДН)");
  92  |   const rows = page.locator(".fp-alt-row__name");
  93  |   await expect(rows.first()).toContainText("Всё на погашение долга");
  94  | });
  95  | 
  96  | test("дашборд → «Построить план распределения →» ведёт на рабочий /planning", async ({ page }) => {
  97  |   await page.goto("/");
  98  |   await page.getByRole("link", { name: "Построить план распределения →" }).click();
  99  |   await expect(page).toHaveURL(/\/planning$/);
  100 |   await expect(page.getByText("Сбалансированный")).toBeVisible();
  101 | });
  102 | 
```