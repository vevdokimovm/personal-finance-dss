import { ListSkeleton, StatePanel, Button } from "@shared/ui";
import { t } from "@shared/lib/i18n/t";
import { useObligations } from "@entities/obligations";
import { ObligationRow } from "./ui/ObligationRow";
import "./ObligationsPage.css";

export function ObligationsPage() {
  const query = useObligations();

  if (query.isLoading) {
    return (
      <main className="fp-obligations">
        <h1>{t("Кредиты и обязательства")}</h1>
        <ListSkeleton rows={4} />
      </main>
    );
  }

  if (query.isError) {
    return (
      <main className="fp-obligations">
        <h1>{t("Кредиты и обязательства")}</h1>
        <StatePanel
          title={t("Не получилось загрузить обязательства")}
          role="alert"
          action={
            <Button variant="primary" onClick={() => void query.refetch()}>
              {t("Повторить")}
            </Button>
          }
        >
          {t("Проверьте соединение и попробуйте ещё раз. Если повторится — напишите в поддержку.")}
        </StatePanel>
      </main>
    );
  }

  const obligations = query.data ?? [];

  if (obligations.length === 0) {
    return (
      <main className="fp-obligations">
        <h1>{t("Кредиты и обязательства")}</h1>
        <StatePanel title={t("Обязательств нет")}>
          {t("Если есть кредиты или рассрочки — добавьте их, план распределения учтёт платежи.")}
        </StatePanel>
      </main>
    );
  }

  return (
    <main className="fp-obligations">
      <h1>{t("Кредиты и обязательства")}</h1>
      <ul className="fp-obligations__list">
        {obligations.map((ob) => (
          <ObligationRow key={ob.id} obligation={ob} />
        ))}
      </ul>
    </main>
  );
}
