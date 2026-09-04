import type { Ref } from "react";
import { Link } from "@tanstack/react-router";
import { DemoSandbox } from "@features/demo-sandbox";
import { Button, StatePanel } from "@shared/ui";
import { t } from "@shared/lib/i18n/t";

/** `mainRef` — опционален: нужен только когда эта ветка может стать местом посадки фокуса
 * после внешнего действия (напр. выдача согласия на dashboard, где refetch может
 * зарезолвиться в пустое состояние — иначе фокус проваливается в <body>, design-critic,
 * батч 2026-08-19). `tabIndex={-1}` на <main> — фокус программный, не таб-стоп. */
/* 🔴 Гостю здесь показывать нечего, кроме предложения ввести сотню операций руками —
   а у продукта есть десять готовых портретов, которые считает настоящий движок
   (README: «Демо за 30 секунд»). Вход в них был в Jinja и потерялся при переносе
   на React (найдено в v8.45.0). Пустой дашборд — ровно то место, где человек
   упирается, поэтому песочница живёт здесь, а не отдельной страницей.

   `isGuest` приходит пропом, а не выясняется здесь: компонент презентационный, и
   собственный запрос в нём заставил бы каждый его тест поднимать QueryClientProvider
   ради ветки, к пустому состоянию отношения не имеющей. */
export function DashboardEmpty({
  mainRef,
  isGuest = false,
}: {
  mainRef?: Ref<HTMLElement>;
  isGuest?: boolean;
}) {
  return (
    <main className="fp-dashboard" ref={mainRef} tabIndex={mainRef ? -1 : undefined}>
      <h1 className="sr-only">{t("Финансовый обзор")}</h1>
      <StatePanel
        title={t("Пока нет данных для обзора")}
        action={
          <Button asChild variant="primary">
            <Link to="/transactions">{t("Внести операции →")}</Link>
          </Button>
        }
      >
        {t(
          "Внесите операции за 1–2 месяца и добавьте кредиты и цели — тогда здесь появится план распределения свободных денег.",
        )}
      </StatePanel>
      <DemoSandbox isGuest={isGuest} />
    </main>
  );
}
