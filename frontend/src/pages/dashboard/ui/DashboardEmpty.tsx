import { Button, StatePanel } from "@shared/ui";
import { t } from "@shared/lib/i18n/t";

export function DashboardEmpty() {
  return (
    <main className="fp-dashboard">
      <h1 className="sr-only">{t("Финансовый обзор")}</h1>
      <StatePanel
        title={t("Пока нет данных для обзора")}
        action={
          <Button asChild variant="primary">
            <a href="/transactions">{t("Внести операции →")}</a>
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
