import { usePlan, useForecast } from "@entities/plan-summary";
import { t } from "@shared/lib/i18n/t";
import { DashboardSkeleton } from "./ui/DashboardSkeleton";
import { DashboardEmpty } from "./ui/DashboardEmpty";
import { DashboardErrorState } from "./ui/DashboardErrorState";
import { Hero } from "./ui/Hero";
import { MetricsGrid } from "@widgets/metrics-grid";
import { AllocationPanel } from "@widgets/allocation-panel";
import { ForecastPanel } from "@widgets/forecast-panel";
import "./DashboardPage.css";

export function DashboardPage() {
  const planQuery = usePlan();
  const forecastQuery = useForecast(12);

  if (planQuery.isLoading || forecastQuery.isLoading) {
    return <DashboardSkeleton />;
  }

  if (planQuery.isError || forecastQuery.isError) {
    const retry = () => {
      void planQuery.refetch();
      void forecastQuery.refetch();
    };
    return <DashboardErrorState onRetry={retry} />;
  }

  const plan = planQuery.data;
  const forecast = forecastQuery.data;
  if (!plan || !forecast) {
    // TanStack Query гарантирует data при !isLoading && !isError, но TS об этом не знает.
    return <DashboardErrorState onRetry={() => void planQuery.refetch()} />;
  }

  const { input_summary } = plan;
  const isEmpty = input_summary.income === 0 && input_summary.expense === 0;
  if (isEmpty) {
    return <DashboardEmpty />;
  }

  return (
    <main className="fp-dashboard">
      <h1 className="sr-only">{t("Финансовый обзор")}</h1>
      <Hero plan={plan} />
      <MetricsGrid indicators={plan.indicators} />
      <AllocationPanel best={plan.top3[0] ?? null} alternatives={plan.ranked} />
      <ForecastPanel forecast={forecast} />
    </main>
  );
}
