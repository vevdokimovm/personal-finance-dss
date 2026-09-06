import { Link } from "@tanstack/react-router";
import { useExperiments, useExperimentResults } from "@entities/experiments";
import type { ExperimentResults, VariantResult } from "@entities/experiments";
import { useProfile } from "@entities/profile";
import { Button, ListSkeleton, StatePanel } from "@shared/ui";
import { extractErrorMessage } from "@shared/lib/api/extractErrorMessage";
import { formatNumber, formatPercent } from "@shared/lib/money/formatMoney";
import { t } from "@shared/lib/i18n/t";
import "./ExperimentsPage.css";

/**
 * Результаты A/B-экспериментов — экран владельца продукта (v8.49.0).
 *
 * Последний пункт §8.2 «ГЛАВНОЕ»: эксперименты жили только в API, посмотреть их
 * можно было через `curl`. Доступ — признак `is_owner`, тот же, что у метрик.
 *
 * 🔴 Экран отвечает на ОДИН вопрос: **катить вариант или нет.** Таблица
 * assigned/converted/rate на него не отвечает: 12 % против 10 % на полусотне
 * наблюдений выглядят как победа и ею не являются. Поэтому вывод стоит словами,
 * первым и самым крупным, а числа — под ним.
 */

/** Машинные имена событий — человеческим языком. Тот же словарь, что на экране
 * метрик: одно событие обязано называться одинаково на обоих экранах владельца
 * ([CMP-03]). Незнакомое показывается ключом — новый тип появляется в коде
 * раньше, чем в словаре. */
const EVENT_LABELS: Record<string, string> = {
  login_success: "Вход в аккаунт",
  user_registered: "Регистрация",
  obligation_created: "Добавлен кредит",
  goal_created: "Добавлена цель",
  transaction_created: "Добавлена операция",
  plan_calculated: "Рассчитан план",
  statement_imported: "Импортирована выписка",
};

/** Статус эксперимента по-русски: `running` в русском интерфейсе — машинное слово. */
const STATUS_LABELS: Record<string, string> = {
  draft: "черновик",
  running: "идёт",
  paused: "на паузе",
  stopped: "остановлен",
  finished: "завершён",
};

/** Победитель — значимо лучший вариант с наибольшим подъёмом. Ничьих не бывает:
 * если значимых нет, победителя нет, и это тоже ответ. */
function findWinner(variants: readonly VariantResult[]): VariantResult | null {
  let winner: VariantResult | null = null;
  for (const row of variants) {
    if (!row.significant || (row.uplift_pct ?? 0) <= 0) continue;
    if (winner === null || (row.uplift_pct ?? 0) > (winner.uplift_pct ?? 0)) {
      winner = row;
    }
  }
  return winner;
}

/** Сколько всего наблюдений в эксперименте — этим объясняется «данных мало». */
function totalAssigned(variants: readonly VariantResult[]): number {
  return variants.reduce((sum, row) => sum + row.assigned, 0);
}

/** Ключ эксперимента в безопасный HTML `id`.
 *
 * 🔴 Контракт разрешает в `key` что угодно длиной 1–64 (`Field(min_length=1,
 * max_length=64)`, без regex). Пробел внутри `id` делает его невалидным, а
 * `aria-labelledby` разбивает значение по пробелам и не находит цель — секция
 * теряет доступное имя целиком (a11y-auditor). Уникальность сохраняется:
 * `key` уникален по ограничению БД, а замена идёт по одному символу. */
function toDomId(key: string): string {
  return `fp-exp-${key.replace(/[^A-Za-z0-9_-]/g, "-")}`;
}

function ExperimentCard({ results, name }: { results: ExperimentResults; name?: string }) {
  const variants = results.variants ?? [];
  const winner = findWinner(variants);
  const total = totalAssigned(variants);
  const titleId = toDomId(results.key);

  return (
    <section className="fp-experiments__card" aria-labelledby={titleId}>
      <p className="fp-experiments__key">{results.key}</p>
      <h2 id={titleId}>{name || results.key}</h2>
      <p className="fp-experiments__meta">
        {t("Статус: {status} · целевое действие: {event}", {
          status: STATUS_LABELS[results.status] ?? results.status,
          event: results.conversion_event
            ? (EVENT_LABELS[results.conversion_event] ?? results.conversion_event)
            : t("не задано"),
        })}
      </p>

      {/* 🔴 Ответ первым, словами и крупно. Ниже — числа, на которых он основан. */}
      <div className="fp-experiments__answer">
        <p className="fp-experiments__eyebrow">{t("Что показал эксперимент")}</p>
        {winner ? (
          <p className="fp-experiments__verdict">
            {t("Побеждает вариант «{name}»: конверсия выше на {uplift}%.", {
              name: winner.variant,
              uplift: formatNumber(winner.uplift_pct ?? 0, 0),
            })}
          </p>
        ) : (
          <p className="fp-experiments__verdict is-inconclusive">
            {t(
              "Данных пока мало, чтобы различить варианты: разница не отличается от " +
                "случайной. Наблюдений — {n}.",
              { n: formatNumber(total, 0) },
            )}
          </p>
        )}
      </div>

      <div className="fp-experiments__scroll">
        <table className="fp-experiments__table">
          <caption className="sr-only">
            {t("Конверсия вариантов эксперимента {key}", { key: results.key })}
          </caption>
          <thead>
            <tr>
              <th scope="col">{t("Вариант")}</th>
              <th scope="col">{t("Показан")}</th>
              <th scope="col">{t("Дошли")}</th>
              <th scope="col">{t("Конверсия")}</th>
              <th scope="col">{t("Против контроля")}</th>
            </tr>
          </thead>
          <tbody>
            {variants.map((row) => {
              const isWinner = winner?.variant === row.variant;
              /* Прочерк ставится по двум РАЗНЫМ причинам, и озвучены они по-разному:
                 «контроль» — точка отсчёта, сравнивать не с чем по построению;
                 «нет данных» — выборка пуста, и это временно (a11y-auditor). */
              const noComparison =
                row.is_control || row.uplift_pct === null || row.uplift_pct === undefined;
              const dashReason = row.is_control
                ? t("точка отсчёта")
                : t("данных для сравнения нет");
              return (
                <tr key={row.variant} className={isWinner ? "is-winner" : undefined}>
                  <th scope="row">
                    {row.variant}
                    {row.is_control && <span className="fp-experiments__tag">{t("контроль")}</span>}
                    {/* Победитель помечен и в самой строке: при точечной навигации
                        по таблице скринридером человек попадает в строку, не читая
                        вывод выше (a11y-auditor). */}
                    {isWinner && <span className="sr-only">{t(" — победитель")}</span>}
                  </th>
                  <td>{formatNumber(row.assigned, 0)}</td>
                  <td>{formatNumber(row.converted, 0)}</td>
                  <td>{formatPercent(row.conversion_rate)}</td>
                  <td>
                    {/* Контроль сам с собой не сравнивается, и пустая выборка не даёт
                        ответа — в обоих случаях прочерк честнее нуля. Для скринридера
                        прочерк озвучен словами, иначе ячейка читается пустой. */}
                    {noComparison ? (
                      <>
                        <span className="fp-experiments__dash" aria-hidden="true">
                          —
                        </span>
                        <span className="sr-only">{dashReason}</span>
                      </>
                    ) : (
                      <span
                        className={
                          row.significant
                            ? "fp-experiments__uplift is-significant"
                            : "fp-experiments__uplift"
                        }
                      >
                        {t("{sign}{value}%", {
                          sign: (row.uplift_pct ?? 0) > 0 ? "+" : "",
                          value: formatNumber(row.uplift_pct ?? 0, 1),
                        })}
                        {!row.significant && (
                          <span className="fp-experiments__hint">
                            {t(" — в пределах случайной")}
                          </span>
                        )}
                      </span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export function ExperimentsPage() {
  const profile = useProfile();
  const isOwner = profile.data?.is_owner === true;
  const experiments = useExperiments(isOwner);
  const list = experiments.data ?? [];
  const keys = list.map((experiment) => experiment.key);
  const results = useExperimentResults(keys, isOwner);

  if (profile.isLoading) {
    return (
      <main className="fp-experiments">
        <h1>{t("A/B-эксперименты")}</h1>
        <ListSkeleton />
      </main>
    );
  }

  if (!isOwner) {
    return (
      <main className="fp-experiments">
        <h1>{t("A/B-эксперименты")}</h1>
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
            "Результаты экспериментов доступны только владельцу продукта: это данные " +
              "обо всех пользователях, а не о вашем плане.",
          )}
        </StatePanel>
      </main>
    );
  }

  if (experiments.isLoading) {
    return (
      <main className="fp-experiments">
        <h1>{t("A/B-эксперименты")}</h1>
        <ListSkeleton />
      </main>
    );
  }

  if (experiments.isError) {
    return (
      <main className="fp-experiments">
        <h1>{t("A/B-эксперименты")}</h1>
        <StatePanel
          role="alert"
          title={t("Не удалось загрузить эксперименты")}
          action={
            <Button variant="primary" onClick={() => void experiments.refetch()}>
              {t("Повторить")}
            </Button>
          }
        >
          {extractErrorMessage(experiments.error, t("Проверьте соединение и попробуйте снова."))}
        </StatePanel>
      </main>
    );
  }

  if (keys.length === 0) {
    return (
      <main className="fp-experiments">
        <h1>{t("A/B-эксперименты")}</h1>
        <StatePanel
          title={t("Экспериментов пока нет")}
          action={
            <Button asChild variant="ghost">
              <Link to="/">{t("На главную")}</Link>
            </Button>
          }
        >
          {t(
            "Здесь появится сравнение вариантов: сколько людей увидело каждый, " +
              "сколько дошло до целевого действия и можно ли верить разнице. " +
              "Эксперименты заводятся через API.",
          )}
        </StatePanel>
      </main>
    );
  }

  return (
    <main className="fp-experiments">
      <h1>{t("A/B-эксперименты")}</h1>
      <p className="fp-experiments__intro">
        {t(
          "Вывод считается сервером: разница объявляется реальной, только если она " +
            "не объясняется случайностью (p < 0,05).",
        )}
      </p>
      {results.map((query, index) => {
        const key = keys[index];
        if (query.isLoading) return <ListSkeleton key={key} />;
        if (query.isError || !query.data) {
          return (
            <StatePanel
              key={key}
              role="alert"
              title={t("Нет результатов по «{key}»", { key })}
              action={
                <Button variant="primary" onClick={() => void query.refetch()}>
                  {t("Повторить")}
                </Button>
              }
            >
              {extractErrorMessage(query.error, t("Проверьте соединение и попробуйте снова."))}
            </StatePanel>
          );
        }
        return <ExperimentCard key={key} results={query.data} name={list[index]?.name} />;
      })}
    </main>
  );
}
