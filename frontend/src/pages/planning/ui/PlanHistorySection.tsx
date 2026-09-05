import { useRef, useState } from "react";
import {
  usePlanHistory,
  useSavePlanSnapshot,
  useDeletePlanSnapshot,
  useRestorePlanSnapshot,
} from "@entities/plan-history";
import type { PlanSnapshotSummary } from "@entities/plan-history";
import { ConsentRequiredPanel } from "@entities/consents";
import { Button, ListSkeleton, StatePanel, toast } from "@shared/ui";
import { formatMoney, formatPercent } from "@shared/lib/money/formatMoney";
import { t } from "@shared/lib/i18n/t";
import { getConsentRequiredDetail } from "@shared/lib/api/extractErrorMessage";
import "./PlanHistorySection.css";

/** Сколько снимков показывать сразу. Остальные — по кнопке: сервер отдаёт до 50, и все
 * пятьдесят карточек дописались бы к самому длинному экрану продукта ([IA-06]). */
const VISIBLE_BY_DEFAULT = 5;

/** Порог ПДН из канона (`docs/math_model.md` §3). Здесь только для пометки строки
 * истории; расчёт и юридический дисклеймер живут в `MetricsGrid`. */
const DTI_LIMIT = 0.4;

/**
 * История сохранённых планов (P2.6, ROADMAP §8.2 «ГЛАВНОЕ», вторая из API-only фич).
 *
 * Бэкенд умел сохранять, отдавать и удалять снимки плана — на фронте этого не было
 * ни строкой. Тот же класс, что H1 и уведомления: функция есть, пути к ней нет.
 *
 * Секция живёт на `/planning`, где план и строится: сохранять снимок осмысленно ровно
 * там, где виден результат, который сохраняешь. Отдельный экран потребовал бы восьмого
 * пункта в навигации ради списка из нескольких строк.
 *
 * Схемы ответа заведены на бэкенде В ЭТОМ ЖЕ батче (`PlanSnapshotSummary` и остальные
 * вместо `dict[str, Any]`) — чтобы фронт реэкспортировал сгенерированный тип, а не
 * писал рукописный. Ровно рукописный тип и подвёл в v8.31.1.
 */
export function PlanHistorySection() {
  const history = usePlanHistory();
  const save = useSavePlanSnapshot();
  const remove = useDeletePlanSnapshot();
  const restore = useRestorePlanSnapshot();
  const [note, setNote] = useState("");
  const [expanded, setExpanded] = useState(false);
  const saveButtonRef = useRef<HTMLButtonElement>(null);
  const listRef = useRef<HTMLUListElement>(null);

  const consent = getConsentRequiredDetail(history.error);
  const items = history.data?.items ?? [];
  const shown = expanded ? items : items.slice(0, VISIBLE_BY_DEFAULT);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (save.isPending) return;
    const trimmed = note.trim();
    save.mutate(
      // Пустая подпись уходит как отсутствующая: `note` в контракте необязателен,
      // и пустая строка — это не «без подписи», в списке она выглядела бы пустой строкой.
      { note: trimmed === "" ? null : trimmed },
      {
        onSuccess: () => {
          setNote("");
          toast.success(t("План сохранён в историю"));
        },
        onError: () => toast.error(t("Не получилось сохранить план. Попробуйте ещё раз.")),
      },
    );
  }

  function handleDelete(snapshot: PlanSnapshotSummary) {
    remove.mutate(snapshot.id, {
      onSuccess: () => {
        // После УДАЛЕНИЯ возвращать фокус на кнопку нельзя — её больше нет в DOM.
        // Список тоже исчезает, если удалён последний снимок, поэтому запасной якорь —
        // кнопка сохранения: она на экране всегда.
        (listRef.current ?? saveButtonRef.current)?.focus();
        // Отмена, а не просто уведомление: удаление обратимо (v8.38.0), и продукт
        // говорит об удалении одним языком на всех сущностях — у целей, активов,
        // обязательств, операций и бюджетов «Вернуть» есть давно.
        toast.undo(t("Снимок удалён"), () =>
          restore.mutate(snapshot.id, {
            onSuccess: () => toast.success(t("Снимок восстановлен")),
            onError: () =>
              toast.error(t("Не получилось восстановить снимок. Попробуйте ещё раз.")),
          }),
        );
      },
      onError: () => toast.error(t("Не получилось удалить снимок. Попробуйте ещё раз.")),
    });
  }

  return (
    <section className="fp-panel fp-plan-history" aria-labelledby="fp-plan-history-title">
      <h2 id="fp-plan-history-title">{t("История планов")}</h2>

      {consent ? (
        <ConsentRequiredPanel
          detail={consent}
          headingLevel={3}
          /* После выдачи согласия перезапрашиваем историю, а не весь экран: остальные
             секции планирования уже показаны и переспрашивать их незачем. */
          onGranted={() => void history.refetch()}
        />
      ) : (
        <>
          <p className="fp-lede">
            {t(
              "Снимок сохраняет показатели и рекомендованное распределение на момент " +
                "сохранения — чтобы позже увидеть, как изменилась картина. Сохраняется " +
                "план по текущему риск-профилю, а не подкрученное ползунками «что если».",
            )}
          </p>

          <form className="fp-plan-history__save" onSubmit={handleSubmit}>
            <div className="fp-entity-form__field fp-plan-history__field">
              <label htmlFor="fp-plan-history-note">{t("Подпись к снимку")}</label>
              <input
                id="fp-plan-history-note"
                type="text"
                maxLength={500}
                value={note}
                placeholder={t("например: до отпуска")}
                onChange={(e) => setNote(e.target.value)}
              />
            </div>
            {/* `ghost`, не `primary`: на этом экране акцент уже занят риск-бейджем и
                прогнозом, а сохранение снимка — не главная задача экрана ([IA-01],
                бриф §1.1 «акцент работает, только если его мало»). */}
            <Button
              ref={saveButtonRef}
              type="submit"
              variant="ghost"
              aria-busy={save.isPending}
              aria-disabled={save.isPending}
            >
              {save.isPending ? t("Сохраняем…") : t("Сохранить текущий план")}
            </Button>
          </form>

          {history.isLoading && <ListSkeleton rows={3} />}

          {history.error && !consent && (
            <StatePanel
              headingLevel={3}
              role="alert"
              title={t("Не получилось загрузить историю планов")}
              action={
                <Button variant="primary" onClick={() => history.refetch()}>
                  {t("Повторить")}
                </Button>
              }
            >
              {t("Проверьте соединение — сохранённые планы не потеряны.")}
            </StatePanel>
          )}

          {history.data && items.length === 0 && (
            <StatePanel headingLevel={3} title={t("Пока нет сохранённых планов")}>
              {t(
                "Сохраните текущий план, чтобы через месяц увидеть, что изменилось " +
                  "в свободных деньгах и долговой нагрузке.",
              )}
            </StatePanel>
          )}

          {items.length > 0 && (
            <>
              <ul className="fp-plan-history__list" role="list" tabIndex={-1} ref={listRef}>
                {shown.map((s) => (
                  <li key={s.id} className="fp-plan-history__item">
                    <div className="fp-plan-history__head">
                      <span className="fp-plan-history__date">{formatWhen(s.created_at)}</span>
                      <span className="fp-plan-history__profile">
                        {/* Без метки скринридер читает просто слово «Сбалансированный»
                            без указания, что это. Тот же приём уже применён к этой же
                            величине на самой странице плана ([A11Y-03]). */}
                        <span className="sr-only">{t("Риск-профиль: ")}</span>
                        {s.risk_profile}
                      </span>
                    </div>

                    <dl className="fp-plan-history__metrics">
                      <div>
                        <dt>{t("Свободные деньги")}</dt>
                        <dd className="fp-plan-history__money">
                          {formatMoney(s.indicators.Rt)}
                        </dd>
                      </div>
                      <div>
                        {/* ПДН показан, иначе снимок с нагрузкой 48% выглядел бы в истории
                            так же, как снимок с 12% — а секция обещает сравнение именно по
                            долговой нагрузке. Превышение порога помечено СЛОВОМ, не только
                            цветом ([A11Y-07]). */}
                        <dt>{t("Долговая нагрузка")}</dt>
                        <dd
                          className={
                            s.indicators.Dt > DTI_LIMIT
                              ? "fp-plan-history__dti fp-plan-history__dti--over"
                              : "fp-plan-history__dti"
                          }
                        >
                          {formatPercent(s.indicators.Dt)}
                          {s.indicators.Dt > DTI_LIMIT && (
                            <span className="fp-plan-history__over"> {t("выше порога")}</span>
                          )}
                        </dd>
                      </div>
                      <div>
                        <dt>{t("В резерв")}</dt>
                        <dd>{formatMoney(s.best.x_reserve)}</dd>
                      </div>
                      <div>
                        <dt>{t("На кредиты")}</dt>
                        <dd>{formatMoney(s.best.x_obligations)}</dd>
                      </div>
                      <div>
                        <dt>{t("На цели")}</dt>
                        <dd>{formatMoney(s.best.x_goals)}</dd>
                      </div>
                    </dl>

                    {s.note && <p className="fp-plan-history__note">{s.note}</p>}

                    <Button
                      variant="danger"
                      aria-disabled={remove.isPending}
                      onClick={() => !remove.isPending && handleDelete(s)}
                      /* Имя кнопки несёт дату: на экране их несколько, и «Удалить»
                         без уточнения в списке кнопок скринридера неразличимо ([A11Y-05]). */
                      aria-label={t("Удалить снимок от {date}", {
                        date: formatWhen(s.created_at),
                      })}
                    >
                      {t("Удалить")}
                    </Button>
                  </li>
                ))}
              </ul>

              {items.length > VISIBLE_BY_DEFAULT && (
                <Button variant="ghost" onClick={() => setExpanded((v) => !v)}>
                  {expanded
                    ? t("Свернуть список")
                    : t("Показать все ({n})", { n: items.length })}
                </Button>
              )}
            </>
          )}
        </>
      )}

    </section>
  );
}

/**
 * Дата и время снимка.
 *
 * Бэкенд отдаёт НАИВНЫЙ UTC — `created_at.isoformat()` без суффикса `Z`
 * (`app/api/routes_planning.py`). `new Date("2026-09-01T10:00:00")` по спецификации
 * читает такую строку как ЛОКАЛЬНОЕ время, поэтому суффикс приходится дописывать
 * самим. Общий `shared/lib/date/formatDate` этого не делает: он пинит `timeZone: "UTC"`
 * при форматировании, что верно для дат без времени (там JS парсит как UTC), но для
 * строки со временем даёт ДВОЙНОЙ сдвиг — сначала парсинг как локальное, потом вывод
 * как UTC. Расхождение найдено тестом этой секции; для `formatDate` заведён пункт
 * в ROADMAP, здесь оно обойдено явно.
 *
 * Показываем в часовом поясе пользователя, а не в UTC: «сохранил в 13:30» и должно
 * читаться как 13:30.
 *
 * Время добавлено, потому что снимков за день можно сделать сколько угодно: список из
 * четырёх карточек с одной и той же датой нечитаем.
 */
function formatWhen(iso: string): string {
  const hasZone = /[Zz]|[+-]\d{2}:?\d{2}$/.test(iso);
  const d = new Date(hasZone ? iso : `${iso}Z`);
  if (Number.isNaN(d.getTime())) return iso;
  return new Intl.DateTimeFormat("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(d);
}
