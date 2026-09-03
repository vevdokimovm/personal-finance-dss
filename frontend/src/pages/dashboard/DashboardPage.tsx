import { useRef, type Ref } from "react";
import { usePlan, useForecast } from "@entities/plan-summary";
import { t } from "@shared/lib/i18n/t";
import { getConsentRequiredDetail } from "@shared/lib/api/extractErrorMessage";
import { ConsentRequiredPanel } from "@entities/consents";
import { DashboardSkeleton } from "./ui/DashboardSkeleton";
import { DashboardEmpty } from "./ui/DashboardEmpty";
import { DashboardErrorState } from "./ui/DashboardErrorState";
import { Hero } from "./ui/Hero";
import { MetricsGrid } from "@widgets/metrics-grid";
import { AllocationPanel } from "@widgets/allocation-panel";
import { ForecastPanel } from "@widgets/forecast-panel";
import { BudgetsSection } from "./ui/BudgetsSection";
import "./DashboardPage.css";

export function DashboardPage() {
  const planQuery = usePlan();
  const forecastQuery = useForecast(12);
  // Фокус после успешной выдачи согласия (a11y-auditor, тот же паттерн, что
  // ObligationsPage/AssetsPage/GoalsPage/TransactionsPage) — типизирован по HTMLElement
  // (не HTMLHeadingElement), потому что точка посадки не всегда h1: если после согласия
  // dashboard разрешится в Empty/Error, фокус уходит на их <main> (design-critic).
  const headingRef = useRef<HTMLElement>(null);

  if (planQuery.isLoading || forecastQuery.isLoading) {
    return <DashboardSkeleton />;
  }

  if (planQuery.isError || forecastQuery.isError) {
    const consentDetail =
      getConsentRequiredDetail(planQuery.error) ?? getConsentRequiredDetail(forecastQuery.error);
    if (consentDetail) {
      const onGranted = () => {
        // Оба refetch дожидаются друг друга ПЕРЕД переносом фокуса (design-critic, батч
        // 2026-08-19): раньше forecast ждали, а plan — нет, и если plan ещё не успевал
        // зарезолвиться, компонент оставался в isLoading (Skeleton, без ref) — фокус падал
        // в <body>. mainRef ниже — запасная точка посадки, если результат — Empty/Error.
        void Promise.all([planQuery.refetch(), forecastQuery.refetch()]).then(() =>
          headingRef.current?.focus(),
        );
      };
      return (
        <main className="fp-dashboard">
          <h1 ref={headingRef as Ref<HTMLHeadingElement>} tabIndex={-1}>
            {t("Финансовый обзор")}
          </h1>
          <ConsentRequiredPanel detail={consentDetail} onGranted={onGranted} />
        </main>
      );
    }
    const retry = () => {
      void planQuery.refetch();
      void forecastQuery.refetch();
    };
    return <DashboardErrorState onRetry={retry} mainRef={headingRef} />;
  }

  const plan = planQuery.data;
  const forecast = forecastQuery.data;
  if (!plan || !forecast) {
    // TanStack Query гарантирует data при !isLoading && !isError, но TS об этом не знает.
    return <DashboardErrorState onRetry={() => void planQuery.refetch()} mainRef={headingRef} />;
  }

  const { input_summary } = plan;
  const isEmpty = input_summary.income === 0 && input_summary.expense === 0;
  if (isEmpty) {
    return <DashboardEmpty mainRef={headingRef} />;
  }

  return (
    <main className="fp-dashboard">
      <h1 className="sr-only" ref={headingRef as Ref<HTMLHeadingElement>} tabIndex={-1}>
        {t("Финансовый обзор")}
      </h1>
      <Hero plan={plan} />
      <MetricsGrid indicators={plan.indicators} />
      <AllocationPanel best={plan.top3?.[0] ?? null} alternatives={plan.ranked} />
      <ForecastPanel forecast={forecast} />
      <BudgetsSection />
    </main>
  );
}
