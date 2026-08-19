import type { Ref } from "react";
import { Button, StatePanel } from "@shared/ui";
import { t } from "@shared/lib/i18n/t";

/** mainRef — см. DashboardEmpty.tsx: место посадки фокуса, если refetch после выдачи
 * согласия зарезолвится в ошибку, а не в успех. */
export function DashboardErrorState({
  onRetry,
  mainRef,
}: {
  onRetry: () => void;
  mainRef?: Ref<HTMLElement>;
}) {
  return (
    <main className="fp-dashboard" ref={mainRef} tabIndex={mainRef ? -1 : undefined}>
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
