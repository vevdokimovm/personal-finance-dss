import { usePlan, useForecast } from "@entities/plan-summary";
import { ListSkeleton, StatePanel, Button } from "@shared/ui";
import { formatMoney } from "@shared/lib/money/formatMoney";
import { t } from "@shared/lib/i18n/t";
import { MetricsGrid } from "@widgets/metrics-grid";
import { AllocationPanel } from "@widgets/allocation-panel";
import { ForecastPanel } from "@widgets/forecast-panel";
import { AlternativesBrowser } from "./ui/AlternativesBrowser";
import "./PlanningPage.css";

/** Полный план: та же пара usePlan/useForecast, что на dashboard (Э3) — не новая
 * сущность. Отличие от dashboard — не свёрнутая карточка, а полная разбивка
 * (риск-профиль, доходы/расходы/резерв входных данных), плюс браузер по всем
 * допустимым альтернативам (Э5, `AlternativesBrowser`) под свёрнутым top3. */
export function PlanningPage() {
  const planQuery = usePlan();
  const forecastQuery = useForecast(12);

  if (planQuery.isLoading || forecastQuery.isLoading) {
    return (
      <main className="fp-planning">
        <h1>{t("План распределения")}</h1>
        <ListSkeleton rows={4} />
      </main>
    );
  }

  if (planQuery.isError || forecastQuery.isError) {
    const retry = () => {
      void planQuery.refetch();
      void forecastQuery.refetch();
    };
    return (
      <main className="fp-planning">
        <h1>{t("План распределения")}</h1>
        <StatePanel
          title={t("Не получилось загрузить план")}
          role="alert"
          action={
            <Button variant="primary" onClick={retry}>
              {t("Повторить")}
            </Button>
          }
        >
          {t("Проверьте соединение и попробуйте ещё раз. Если повторится — напишите в поддержку.")}
        </StatePanel>
      </main>
    );
  }

  const plan = planQuery.data;
  const forecast = forecastQuery.data;
  if (!plan || !forecast) {
    return (
      <main className="fp-planning">
        <h1>{t("План распределения")}</h1>
        <StatePanel
          title={t("Не получилось загрузить план")}
          role="alert"
          action={
            <Button variant="primary" onClick={() => void planQuery.refetch()}>
              {t("Повторить")}
            </Button>
          }
        >
          {t("Проверьте соединение и попробуйте ещё раз. Если повторится — напишите в поддержку.")}
        </StatePanel>
      </main>
    );
  }

  const { input_summary } = plan;
  const isEmpty = input_summary.income === 0 && input_summary.expense === 0;
  if (isEmpty) {
    return (
      <main className="fp-planning">
        <h1>{t("План распределения")}</h1>
        <StatePanel
          title={t("Пока нет данных для плана")}
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

  return (
    <main className="fp-planning">
      <div className="fp-planning__head">
        <h1>{t("План распределения")}</h1>
        <span className="fp-planning__risk-badge">
          <span className="sr-only">{t("Риск-профиль: ")}</span>
          {plan.risk_profile}
        </span>
      </div>
      <dl className="fp-planning__inputs">
        <div>
          <dt>{t("Доходы")}</dt>
          <dd>{formatMoney(input_summary.income)}</dd>
        </div>
        <div>
          <dt>{t("Расходы")}</dt>
          <dd>{formatMoney(input_summary.expense)}</dd>
        </div>
        <div>
          <dt>{t("Свободный резерв (B_liq)")}</dt>
          <dd>{formatMoney(input_summary.bliq)}</dd>
        </div>
        <div>
          <dt>{t("Учтено")}</dt>
          <dd>
            {t("{tx} опер. · {ob} обяз. · {g} целей", {
              tx: input_summary.transactions_count,
              ob: input_summary.obligations_count,
              g: input_summary.goals_count,
            })}
          </dd>
        </div>
      </dl>
      <MetricsGrid indicators={plan.indicators} />
      <AllocationPanel best={plan.top3[0] ?? null} alternatives={plan.ranked} />
      <AlternativesBrowser alternatives={plan.ranked} />
      <ForecastPanel forecast={forecast} />
    </main>
  );
}
