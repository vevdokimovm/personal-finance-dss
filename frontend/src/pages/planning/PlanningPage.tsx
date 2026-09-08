import { useRef, useState } from "react";
import { Link } from "@tanstack/react-router";
import { usePlan, useForecast } from "@entities/plan-summary";
import { ListSkeleton, StatePanel, Button, Formula } from "@shared/ui";
import { formatMoney } from "@shared/lib/money/formatMoney";
import { t } from "@shared/lib/i18n/t";
import { getConsentRequiredDetail } from "@shared/lib/api/extractErrorMessage";
import { SessionExpiredPanel, isSessionExpired } from "@entities/auth";
import { ConsentRequiredPanel } from "@entities/consents";
import { MetricsGrid } from "@widgets/metrics-grid";
import { PlanExportSection } from "./ui/PlanExportSection";
import { PlanHistorySection } from "./ui/PlanHistorySection";
import { CrisisPlanSection } from "./ui/CrisisPlanSection";
import { AllocationPanel } from "@widgets/allocation-panel";
import { PlanSettingsSection } from "./ui/PlanSettingsSection";
import { ForecastPanel } from "@widgets/forecast-panel";
import { AlternativesBrowser } from "./ui/AlternativesBrowser";
import "./PlanningPage.css";

/** Полный план: та же пара usePlan/useForecast, что на dashboard (Э3) — не новая
 * сущность. Отличие от dashboard — не свёрнутая карточка, а полная разбивка
 * (риск-профиль, доходы/расходы/резерв входных данных), плюс браузер по всем
 * допустимым альтернативам (Э5, `AlternativesBrowser`) под свёрнутым top3. */
export function PlanningPage() {
  const planQuery = usePlan();
  // §8.4: горизонт/ставка «что если» живут здесь — тот же владелец, что useForecast (плюс
  // ForecastPanel остаётся управляемым компонентом, как AllocationPanel/WhatIfSliders).
  const [horizon, setHorizon] = useState(12);
  const [rBench, setRBench] = useState<number | undefined>(undefined);
  const forecastQuery = useForecast(horizon, rBench);
  // Фокус после успешной выдачи согласия (a11y-auditor) — см. ObligationsPage.tsx.
  const headingRef = useRef<HTMLHeadingElement>(null);

  if (planQuery.isLoading || forecastQuery.isLoading) {
    return (
      <main className="fp-planning">
        <h1 ref={headingRef} tabIndex={-1}>
          {t("План распределения")}
        </h1>
        <ListSkeleton rows={4} />
      </main>
    );
  }

  if (planQuery.isError || forecastQuery.isError) {
    /* 🔴 401 — истёкшая сессия, а не сбой связи (гипотеза 7). «Повторить» на нём
       возвращает 401 бесконечно, а совет проверить интернет при работающем интернете
       уводит чинить не то. */
    if (isSessionExpired(planQuery.error) || isSessionExpired(forecastQuery.error)) {
      return (
        <main className="fp-planning">
          <h1 ref={headingRef} tabIndex={-1}>
            {t("План распределения")}
          </h1>
          <SessionExpiredPanel redirectTo="/planning" />
        </main>
      );
    }
    const consentDetail =
      getConsentRequiredDetail(planQuery.error) ?? getConsentRequiredDetail(forecastQuery.error);
    if (consentDetail) {
      const onGranted = () => {
        void planQuery.refetch();
        void forecastQuery.refetch().then(() => headingRef.current?.focus());
      };
      return (
        <main className="fp-planning">
          <h1 ref={headingRef} tabIndex={-1}>
            {t("План распределения")}
          </h1>
          <ConsentRequiredPanel detail={consentDetail} onGranted={onGranted} />
        </main>
      );
    }
    const retry = () => {
      void planQuery.refetch();
      void forecastQuery.refetch();
    };
    return (
      <main className="fp-planning">
        <h1 ref={headingRef} tabIndex={-1}>
          {t("План распределения")}
        </h1>
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
        <h1 ref={headingRef} tabIndex={-1}>
          {t("План распределения")}
        </h1>
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
        <h1 ref={headingRef} tabIndex={-1}>
          {t("План распределения")}
        </h1>
        <StatePanel
          title={t("Пока нет данных для плана")}
          action={
            <Button asChild variant="primary">
              <Link to="/transactions">{t("Внести операции →")}</Link>
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
        <h1 ref={headingRef} tabIndex={-1}>
          {t("План распределения")}
        </h1>
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
          <dt>
            {t("Свободный резерв")} (<Formula tex="B_{liq}" fallback="B_liq" />)
          </dt>
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
      {/* Настройка идёт ПЕРЕД результатом: иначе непонятно, чем управляют ползунки.
          До v8.42.0 этих контролов в React не было вовсе — риск-профиль, главный параметр
          модели, менялся только в Jinja. */}
      <PlanSettingsSection
        /* Пересчёт после сохранения настроек идёт ЗДЕСЬ, а не внутри панели: без этого
           признака панель объявляла успех по ответу PATCH — то есть до того, как план
           реально пересчитан (design-critic). */
        planPending={planQuery.isFetching || forecastQuery.isFetching}
      />
      <MetricsGrid indicators={plan.indicators} />
      {/* 🔴 Дисклеймер 39-ФЗ — ПЕРЕД распределением, а не в подвале страницы (L5).
          Человек принимает решение о деньгах, глядя на рекомендацию; предупреждение,
          до которого надо доскроллить, требования не выполняет. Текст берётся из поля
          ответа — не перепечатывается здесь, иначе разойдётся с каноном при первой же
          правке юридического текста. */}
      {plan.disclaimer && (
        /* `role="note"` заменена на регион с меткой: `note` не объявляется сама и
           не попадает в landmark-навигацию — юридически значимый текст доставался бы
           только тому, кто дочитает страницу линейно (a11y-auditor).
           `<section aria-label>` даёт роль `region`; `<aside>` дал бы `complementary`
           («отступление в стороне»), а предупреждение о самой рекомендации — часть
           основного содержания, а не отступление. Расхождение поймал браузерный тест. */
        <section className="fp-planning__disclaimer" aria-label={t("Важно о рекомендации")}>
          <p className="fp-planning__disclaimer-title">{t("Важно")}</p>
          <p className="fp-planning__disclaimer-text">{plan.disclaimer}</p>
        </section>
      )}
      {/* 🔴 Кризисный план стоит ПЕРЕД распределением (v9.1.0). Когда свободных денег
          нет, обычный план не построить — распределять нечего, и `AllocationPanel` ниже
          покажет пустоту. Человек в дефиците должен первым делом увидеть разбор, а не
          проскроллить пустой блок в поисках ответа.

          План считался с v6.0.0 и не показывался никому: `grep crisis` по `frontend/src`
          давал ноль совпадений. Тот же класс, что spending-advice до v8.54.0. */}
      <CrisisPlanSection plan={plan.crisis_plan} />
      {/* 🔴 При кризисном плане панель распределения НЕ рисуется (design-critic).
          `top3` в этом случае пуст, и панель показывает своё «плана нет» — с внутренним
          термином «fail-loud» в тексте. Человек в дефиците получал подряд два объяснения
          одного факта разными словами, второе — жаргоном разработки. Кризисный разбор
          заменяет пустую панель, а не соседствует с ней. */}
      {!plan.crisis_plan && (
        <>
          {/* `rejected` нужен ровно для пустого плана: панель объясняет пустоту
              настоящей причиной из ответа, а не одной предполагаемой. */}
          <AllocationPanel
            best={plan.top3?.[0] ?? null}
            alternatives={plan.ranked}
            rejected={plan.rejected}
          />
          <AlternativesBrowser alternatives={plan.ranked} />
        </>
      )}
      <ForecastPanel
        forecast={forecast}
        horizon={horizon}
        onHorizonChange={setHorizon}
        rBench={rBench}
        onRBenchChange={setRBench}
        isFetching={forecastQuery.isFetching}
      />
      {/* Выгрузка — перед историей: она про ТЕКУЩИЙ план, который выше, а история про
          прошлое. Обе живут здесь, а не отдельными экранами: и сохранять снимок, и
          выгружать файл осмысленно ровно там, где виден результат. */}
      <PlanExportSection />
      {/* История — последней секцией: она про прошлое, а экран начинается с сегодняшнего
          плана. Живёт здесь, а не отдельным экраном, потому что сохранять снимок
          осмысленно ровно там, где виден результат, который сохраняешь; отдельный экран
          потребовал бы восьмого пункта навигации ради списка из нескольких строк. */}
      <PlanHistorySection />
    </main>
  );
}
