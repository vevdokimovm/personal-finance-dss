import { Link } from "@tanstack/react-router";
import { useAnalyticsOverview, useFunnel } from "@entities/insights";
import type { FunnelStep } from "@entities/insights";
import { useProfile } from "@entities/profile";
import { Button, ListSkeleton, StatePanel } from "@shared/ui";
import { extractErrorMessage } from "@shared/lib/api/extractErrorMessage";
import { formatNumber } from "@shared/lib/money/formatMoney";
import { t } from "@shared/lib/i18n/t";
import "./InsightsPage.css";

/**
 * Метрики продукта: где теряем людей (v8.48.0).
 *
 * Экран для ВЛАДЕЛЬЦА продукта, не для пользователя. Решение владельца 04.09.2026:
 * доступ даёт признак `is_owner` на аккаунте, а не ключ в браузере — ключ пришлось бы
 * держать в `localStorage`, то есть завести секрет за пределами `.env`.
 *
 * 🔴 Экран отвечает на ОДИН вопрос: «что чинить». Первая редакция ставила самым крупным
 * кеглем «активных пользователей» и «событий всего» — метрики, по которым чинить нечего,
 * — а падение между шагами лежало серым мелким текстом и не было вычислено вовсе
 * (design-critic). Теперь главное — шаг с наибольшей потерей.
 */

/** Машинные имена событий — человеческим языком. Незнакомое показывается как есть:
 * новый тип появляется в коде раньше, чем в словаре, и ключ лучше пустой строки. */
const STEP_LABELS: Record<string, string> = {
  login_success: "Вход в аккаунт",
  register_success: "Регистрация",
  obligation_created: "Добавлен кредит",
  goal_created: "Добавлена цель",
  transaction_created: "Добавлена операция",
  plan_calculated: "Рассчитан план",
  statement_imported: "Импортирована выписка",
};

/** «1 человек», «2 человека», «5 человек» — иначе «62 человек» читается как опечатка. */
function people(n: number): string {
  const value = formatNumber(n, 0);
  const mod10 = n % 10;
  const mod100 = n % 100;
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) {
    return t("{n} человека", { n: value });
  }
  return t("{n} человек", { n: value });
}

/** Шаг с наибольшей потерей — то, ради чего экран и открывают. */
function worstDrop(steps: readonly FunnelStep[]): { step: FunnelStep; lost: number } | null {
  let worst: { step: FunnelStep; lost: number } | null = null;
  for (let i = 1; i < steps.length; i += 1) {
    const lost = steps[i - 1].users - steps[i].users;
    if (lost > 0 && (worst === null || lost > worst.lost)) {
      worst = { step: steps[i], lost };
    }
  }
  return worst;
}

export function InsightsPage() {
  const profile = useProfile();
  const isOwner = profile.data?.is_owner === true;
  const overview = useAnalyticsOverview(isOwner);
  const funnel = useFunnel(isOwner);

  if (profile.isLoading) {
    return (
      <main className="fp-insights">
        <h1>{t("Метрики продукта")}</h1>
        <ListSkeleton />
      </main>
    );
  }

  /* Не владельцу — честный отказ С ВЫХОДОМ. Раздела нет в его меню, и оставить человека
     на экране без обозначенного возврата значит завести в тупик ([IA-02]). */
  if (!isOwner) {
    return (
      <main className="fp-insights">
        <h1>{t("Метрики продукта")}</h1>
        <StatePanel
          role="alert"
          title={t("Раздел закрыт")}
          action={
            <Button asChild variant="primary">
              <Link to="/">{t("На главную")}</Link>
            </Button>
          }
        >
          {t(
            "Метрики продукта доступны только владельцу продукта: это данные обо всех " +
              "пользователях, а не о вашем плане.",
          )}
        </StatePanel>
      </main>
    );
  }

  if (overview.isLoading || funnel.isLoading) {
    return (
      <main className="fp-insights">
        <h1>{t("Метрики продукта")}</h1>
        <ListSkeleton />
      </main>
    );
  }

  if (overview.isError || funnel.isError) {
    return (
      <main className="fp-insights">
        <h1>{t("Метрики продукта")}</h1>
        <StatePanel
          role="alert"
          title={t("Не удалось загрузить метрики")}
          action={
            <Button
              variant="primary"
              onClick={() => {
                void overview.refetch();
                void funnel.refetch();
              }}
            >
              {t("Повторить")}
            </Button>
          }
        >
          {extractErrorMessage(
            overview.error ?? funnel.error,
            t("Проверьте соединение и попробуйте снова."),
          )}
        </StatePanel>
      </main>
    );
  }

  const data = overview.data;
  const steps = funnel.data?.steps ?? [];
  const funnelDays = funnel.data?.period_days ?? data?.period_days ?? 30;
  const worst = worstDrop(steps);
  /* Пусто, только если нет НИ событий, НИ воронки: считать по одному счётчику значило бы
     спрятать воронку из-за пустой сводки (design-critic). */
  const isEmpty = (!data || data.total_events === 0) && steps.length === 0;

  return (
    <main className="fp-insights">
      <h1>{t("Метрики продукта")}</h1>

      {isEmpty ? (
        <StatePanel
          title={t("Событий за период пока нет")}
          action={
            <Button asChild variant="ghost">
              <Link to="/">{t("На главную")}</Link>
            </Button>
          }
        >
          {t(
            "Продукт ещё не набрал действий пользователей. Здесь появятся: сколько людей " +
              "заходит, на каком шаге они останавливаются и что делают чаще всего. " +
              "События пишутся автоматически — как только пойдут первые, они будут тут.",
          )}
        </StatePanel>
      ) : (
        <>
          {/* 🔴 Ответ первым и самым крупным: где теряем. «Активных пользователей»
              и «событий всего» — метрики, по которым чинить нечего, и они ниже. */}
          {worst && (
            <section className="fp-insights__answer" aria-labelledby="fp-worst-title">
              <h2 id="fp-worst-title">{t("Больше всего теряем здесь")}</h2>
              <p className="fp-insights__worst">
                {STEP_LABELS[worst.step.step] ?? worst.step.step}
              </p>
              <p className="fp-insights__worst-note">
                {t("Не дошли {lost} — осталось {left} из тех, кто начал.", {
                  lost: people(worst.lost),
                  left: people(worst.step.users),
                })}
              </p>
            </section>
          )}

          <section aria-labelledby="fp-funnel-title">
            <h2 id="fp-funnel-title">{t("Воронка за {n} дней", { n: funnelDays })}</h2>
            <p className="fp-insights__note">
              {t(
                "Это воронка завершения шагов, а не порядок во времени: на каждом шаге — " +
                  "люди, прошедшие все предыдущие.",
              )}
            </p>
            {steps.length === 0 && (
              <p className="fp-insights__note">{t("Шаги воронки пока не набрали данных.")}</p>
            )}
            <ol className="fp-insights__funnel">
              {steps.map((step) => {
                const isWorst = worst?.step.step === step.step;
                return (
                  <li key={step.step} className={isWorst ? "is-worst" : undefined}>
                    <span className="fp-insights__step">
                      {STEP_LABELS[step.step] ?? step.step}
                    </span>
                    {/* Полоса декоративна: значение продублировано текстом. Акцентный
                        цвет — только у худшего шага, иначе акцент на каждой строке
                        и не выделяет ничего (бриф §1.1). */}
                    <span className="fp-insights__bar" aria-hidden="true">
                      <span style={{ width: `${step.conversion_pct}%` }} />
                    </span>
                    <span className="fp-insights__value">
                      {t("{users} · {pct}%", {
                        users: people(step.users),
                        pct: formatNumber(step.conversion_pct, 0),
                      })}
                    </span>
                  </li>
                );
              })}
            </ol>
          </section>

          <section aria-labelledby="fp-summary-title">
            <h2 id="fp-summary-title">
              {t("Сводка за {n} дней", { n: data?.period_days ?? 30 })}
            </h2>
            <dl className="fp-insights__summary">
              <div>
                <dt>{t("Активных пользователей")}</dt>
                <dd>{formatNumber(data?.active_users ?? 0, 0)}</dd>
              </div>
              <div>
                <dt>{t("Событий всего")}</dt>
                <dd>{formatNumber(data?.total_events ?? 0, 0)}</dd>
              </div>
            </dl>
          </section>

          <section aria-labelledby="fp-events-title">
            <h2 id="fp-events-title">{t("Действия")}</h2>
            <p className="fp-insights__note">
              {t("Сколько раз произошло действие — не сколько людей его сделали.")}
            </p>
            <dl className="fp-insights__events">
              {/* Сортировка по убыванию: порядок из словаря произволен и меняется между
                  ответами, из-за чего числа прыгали бы по сетке между заходами. */}
              {Object.entries(data?.event_counts ?? {})
                .sort(([, a], [, b]) => b - a)
                .map(([key, count]) => (
                  <div key={key}>
                    <dt>{STEP_LABELS[key] ?? key}</dt>
                    <dd>{t("{n} раз", { n: formatNumber(count, 0) })}</dd>
                  </div>
                ))}
            </dl>
          </section>
        </>
      )}
    </main>
  );
}
