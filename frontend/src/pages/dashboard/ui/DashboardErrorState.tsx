import { Button, StatePanel } from "@shared/ui";
import { t } from "@shared/lib/i18n/t";

export function DashboardErrorState({ onRetry }: { onRetry: () => void }) {
  return (
    <main className="fp-dashboard">
      <h1 className="sr-only">{t("Финансовый обзор")}</h1>
      <StatePanel
        title={t("Не получилось загрузить обзор")}
        role="alert"
        action={
          <Button variant="primary" onClick={onRetry}>
            {t("Повторить")}
          </Button>
        }
      >
        {t("Проверьте соединение и попробуйте ещё раз. Если повторится — напишите в поддержку.")}
      </StatePanel>
    </main>
  );
}
