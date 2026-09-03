import type { Ref } from "react";
import { Link } from "@tanstack/react-router";
import { Button, StatePanel } from "@shared/ui";
import { t } from "@shared/lib/i18n/t";

/** `mainRef` — опционален: нужен только когда эта ветка может стать местом посадки фокуса
 * после внешнего действия (напр. выдача согласия на dashboard, где refetch может
 * зарезолвиться в пустое состояние — иначе фокус проваливается в <body>, design-critic,
 * батч 2026-08-19). `tabIndex={-1}` на <main> — фокус программный, не таб-стоп. */
export function DashboardEmpty({ mainRef }: { mainRef?: Ref<HTMLElement> }) {
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
    </main>
  );
}
