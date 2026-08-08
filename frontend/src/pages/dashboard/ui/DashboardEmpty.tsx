import { Button } from "@shared/ui";
import { t } from "@shared/lib/i18n/t";

export function DashboardEmpty() {
  return (
    <main className="fp-dashboard">
      <h1 className="sr-only">{t("Финансовый обзор")}</h1>
      <div className="fp-state-panel">
        <h2>{t("Пока нет данных для обзора")}</h2>
        <p>
          {t(
            "Внесите операции за 1–2 месяца и добавьте кредиты и цели — тогда здесь появится план распределения свободных денег.",
          )}
        </p>
        <Button asChild variant="primary">
          <a href="/transactions">{t("Внести операции →")}</a>
        </Button>
      </div>
    </main>
  );
}
