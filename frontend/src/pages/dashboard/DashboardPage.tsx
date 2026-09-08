import { useRef, type Ref } from "react";
import { usePlan, useForecast } from "@entities/plan-summary";
import { t } from "@shared/lib/i18n/t";
import { getConsentRequiredDetail } from "@shared/lib/api/extractErrorMessage";
import { ConsentRequiredPanel } from "@entities/consents";
import { NotAuthenticatedError, useProfile } from "@entities/profile";
import { DashboardSkeleton } from "./ui/DashboardSkeleton";
import { DashboardEmpty, type EmptyReason } from "./ui/DashboardEmpty";
import { DashboardErrorState } from "./ui/DashboardErrorState";
import { Hero } from "./ui/Hero";
import { MetricsGrid } from "@widgets/metrics-grid";
import { AllocationPanel } from "@widgets/allocation-panel";
import { ForecastPanel } from "@widgets/forecast-panel";
import { BudgetsSection } from "./ui/BudgetsSection";
import "./DashboardPage.css";

/** Какого куска данных не хватает для осмысленного плана.
 *
 * `null` — хватает обоих. Порядок проверок неважен: состояния взаимоисключающие
 * по построению (ноль дохода и ноль расхода одновременно — это «ничего нет»).
 */
function getEmptyReason(income: number, expense: number): EmptyReason | null {
  if (income === 0 && expense === 0) return "nothing";
  if (income === 0) return "no-income";
  if (expense === 0) return "no-expense";
  return null;
}

export function DashboardPage() {
  /* Гостевой режим определяет страница, а не пустое состояние: она уже держит запросы
     и знает контекст. `/auth/me` отвечает 401 гостю — это ожидаемый ответ, не сбой
     (`entities/profile`). */
  const profileQuery = useProfile();
  const isGuest = profileQuery.error instanceof NotAuthenticatedError;
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
  /* 🔴 Считать план можно, только когда известны ОБЕ стороны (H10). Пустой профиль,
     «только расходы» и «только доходы» — три разных состояния с разными подсказками:
     человеку надо сказать, чего именно не хватает, а не «данных нет». */
  const emptyReason = getEmptyReason(input_summary.income, input_summary.expense);
  if (emptyReason) {
    return <DashboardEmpty mainRef={headingRef} isGuest={isGuest} reason={emptyReason} />;
  }

  return (
    <main className="fp-dashboard">
      <h1 className="sr-only" ref={headingRef as Ref<HTMLHeadingElement>} tabIndex={-1}>
        {t("Финансовый обзор")}
      </h1>
      <Hero plan={plan} />
      <MetricsGrid indicators={plan.indicators} />
      {/* `rejected` — причины пустого плана. Без него панель называла бы одну
          предполагаемую причину («расходы превышают доход») при любой из них. */}
      <AllocationPanel
        best={plan.top3?.[0] ?? null}
        alternatives={plan.ranked}
        rejected={plan.rejected}
      />
      <ForecastPanel forecast={forecast} />
      <BudgetsSection />
    </main>
  );
}
