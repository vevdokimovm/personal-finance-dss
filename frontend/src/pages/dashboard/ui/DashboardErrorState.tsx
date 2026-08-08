import { Button } from "@shared/ui";
import { t } from "@shared/lib/i18n/t";

export function DashboardErrorState({ onRetry }: { onRetry: () => void }) {
  return (
    <main className="fp-dashboard">
      <h1 className="sr-only">{t("Финансовый обзор")}</h1>
      <div className="fp-state-panel" role="alert">
        <h2>{t("Не получилось загрузить обзор")}</h2>
        <p>
          {t("Проверьте соединение и попробуйте ещё раз. Если повторится — напишите в поддержку.")}
        </p>
        <Button variant="primary" onClick={onRetry}>
          {t("Повторить")}
        </Button>
      </div>
    </main>
  );
}
