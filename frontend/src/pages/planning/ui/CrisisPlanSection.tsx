import { Link } from "@tanstack/react-router";
import type { CrisisAction, CrisisPlan } from "@entities/plan-summary";
import { formatMoney, formatNumber, formatPercent } from "@shared/lib/money/formatMoney";
import { plural } from "@shared/lib/i18n/plural";
import { t } from "@shared/lib/i18n/t";
import "./CrisisPlanSection.css";

/**
 * Кризисный план: что делать, когда свободных денег нет (v9.1.0).
 *
 * 🔴 Считается с **v6.0.0** (`app/core/crisis.py`, канон §12) и до этого батча
 * не показывался никому: `grep crisis` по `frontend/src` давал ноль совпадений вне
 * сгенерированного клиента. Владелец, поручивший фичу, считал, что её нет, — он её
 * не видел.
 *
 * Тот же класс, что spending-advice до v8.54.0, и цена выше: человек в дефиците —
 * тот, кому продукт нужнее всего. Алгоритм отказывается строить обычный план
 * распределения (распределять нечего), и вместо разбора человек видел пустое место.
 */

/** Заголовок и объяснение по тяжести положения.
 *
 * 🔴 Ключи — РОВНО те, что отдаёт `crisis.py`: `recoverable_from_liquidity`,
 * `critical`, `cut_required`. Первая редакция объявляла несуществующий `manageable`,
 * и самый частый случай попадал в ветку «неизвестное значение», показывая верный текст
 * по совпадению — потому что дефолт был назначен тем же объектом. Первая правка дефолта
 * сломала бы основной сценарий бесшумно (design-critic).
 *
 * Тон различается намеренно: «поправимо одним ходом» и «запас меньше месяца» нельзя
 * описывать одним текстом, он был бы неверен в обе стороны.
 */
const SEVERITY: Record<string, { title: string; lead: string }> = {
  recoverable_from_liquidity: {
    title: "Свободных денег нет, но положение поправимо",
    lead:
      "Расходы и платежи по кредитам сейчас больше дохода. Накоплений хватает, чтобы " +
      "закрыть часть долга и развернуть поток обратно в плюс — план ниже.",
  },
  cut_required: {
    title: "Свободных денег не хватает",
    lead:
      "Расходы и платежи по кредитам больше дохода, поэтому обычный план распределения " +
      "не построить: распределять нечего. Ниже — что можно сделать, чтобы поток вернулся " +
      "в плюс.",
  },
  critical: {
    title: "Денег не хватает, и запас времени мал",
    lead:
      "Дохода не хватает на текущие расходы и платежи, а накоплений хватит ненадолго. " +
      "Действия ниже перечислены по силе — начинать стоит сверху.",
  },
};

/** Неизвестная тяжесть: нейтральный текст без обещаний.
 *
 * 🔴 Тяжесть передаётся ТОЛЬКО текстом (цвета сознательно нет), значит ошибка в тексте —
 * ошибка в единственном носителе смысла. Показать «средний» уровень при новом, более
 * строгом — занизить опасность, и человек не узнает об этом никогда.
 */
const UNKNOWN_SEVERITY = {
  title: "Свободных денег не хватает",
  lead:
    "Расходы и платежи по кредитам больше дохода. Ниже — что можно сделать, " +
    "чтобы поток вернулся в плюс.",
};

const MONTHS: [string, string, string] = ["месяц", "месяца", "месяцев"];

/** Куда идти делать это действие.
 *
 * 🔴 [IA-04] «no dead ends»: «поставьте цели на паузу» без ссылки заставляет человека
 * искать раздел самому — в состоянии, когда он и так в стрессе. Цифры без пути
 * к действию это тупик.
 */
const ACTION_LINKS: Record<string, { to: string; label: string }> = {
  cut_expenses: { to: "/transactions", label: "Посмотреть траты" },
  freeze_goals: { to: "/goals", label: "Открыть цели" },
  restructure_debt: { to: "/obligations", label: "Открыть кредиты" },
  close_debts_from_liquidity: { to: "/banks", label: "Открыть накопления" },
};

/** Склонение месяцев с учётом дробных значений.
 *
 * 🔴 `plural(Math.round(0.5))` давал «0,5 месяц»: в русском при дробном всегда
 * родительный единственного — «0,5 месяца», «4,5 месяца». Случай `runway < 1` — это
 * ровно ветка `critical` (`crisis.py`), то есть ошибка вылезала у самого напуганного
 * человека (design-critic).
 */
function monthsLabel(value: number): string {
  if (!Number.isInteger(value)) return "месяца";
  return plural(value, MONTHS);
}

/** Запас хода: дробный — с одним знаком, целый — без него.
 *
 * `formatNumber(1, 1)` даёт «1,0», и рядом со склонением по целому получалось
 * «1,0 месяц» — печатаем дробное, склоняем как целое. Человек говорит «два месяца»,
 * а не «2,0 месяца».
 */
function formatRunway(value: number): string {
  return Number.isInteger(value) ? String(value) : formatNumber(value, 1);
}

function ActionCard({ action }: { action: CrisisAction }) {
  const body = renderAction(action);
  if (!body) return null;
  const link = ACTION_LINKS[action.type];
  return (
    <li className="fp-crisis__action" data-testid={`fp-crisis-action-${action.type}`}>
      {body}
      {link && (
        <p className="fp-crisis__action-link">
          <Link to={link.to}>{t(link.label)} →</Link>
        </p>
      )}
    </li>
  );
}

/** Одно действие человеческим языком.
 *
 * 🔴 Карточка без ключевых полей НЕ рисуется: `?? 0` печатал «останется 0 ₽ в месяц»
 * и ««», 0 % годовых» с видом достоверных чисел. На деньгах ложная точность дороже
 * пропуска карточки ([ST-05]).
 *
 * Незнакомый `type` возвращает `null`, а не роняет разбор: модель может завести новый
 * вид действия раньше, чем фронт про него узнает, и терять из-за одной строки остальные
 * советы — худший исход на этом экране.
 */
function renderAction(action: CrisisAction) {
  switch (action.type) {
    case "close_debts_from_liquidity": {
      if (action.bliq_used == null || action.new_rt == null) return null;
      return (
        <>
          <h4 className="fp-crisis__action-title">{t("Закрыть кредит из накоплений")}</h4>
          <p>
            {t("Уйдёт {used}, останется {rest}.", {
              used: formatMoney(action.bliq_used, 0),
              rest: formatMoney(action.bliq_remaining ?? 0, 0),
            })}{" "}
            {/* Результат — суть хода: без него это просто «потратьте накопления». */}
            {t("После этого свободными останется {rt} в месяц.", {
              rt: formatMoney(action.new_rt, 0),
            })}
          </p>
        </>
      );
    }

    case "cut_expenses": {
      if (action.amount == null) return null;
      return (
        <>
          <h4 className="fp-crisis__action-title">{t("Сократить расходы")}</h4>
          <p>
            {t("Нужно {amount} — это {share} текущих трат.", {
              amount: formatMoney(action.amount, 0),
              share: formatPercent(action.share_of_expenses ?? 0, 0),
            })}
          </p>
          {action.max_affordable_expenses != null && (
            <p className="fp-crisis__note">
              {t("Потолок трат при нынешнем доходе — {ceiling} в месяц.", {
                ceiling: formatMoney(action.max_affordable_expenses, 0),
              })}
            </p>
          )}
        </>
      );
    }

    case "freeze_goals": {
      if (!action.goals?.length) return null;
      return (
        <>
          <h4 className="fp-crisis__action-title">{t("Поставить цели на паузу")}</h4>
          <p>
            {/* Перечисляем поимённо: «заморозьте цели» человек не может исполнить,
                не открыв другой экран и не решая, какие именно. */}
            {t("Пока поток отрицательный, пополнять их не из чего: {goals}.", {
              goals: action.goals.join(", "),
            })}
          </p>
        </>
      );
    }

    case "restructure_debt": {
      if (!action.loan || action.interest_rate == null) return null;
      return (
        <>
          <h4 className="fp-crisis__action-title">{t("Договориться с банком по кредиту")}</h4>
          <p>
            {/* 🔴 Ставка — ДОЛЯ (0.39 = 39%), как во всём продукте: `ObligationRow`
                и `AssetRow` зовут `formatPercent` без деления. Лишнее `/100` печатало
                «0,4 % годовых» — человек читал, что его самый дорогой кредит почти
                бесплатный (design-critic).

                Имя и ставка обязательны: «обратитесь в банк» нельзя исполнить,
                не вспомнив, какой из кредитов самый дорогой. Модель его уже выбрала. */}
            {t("Самый дорогой — «{loan}», {rate} годовых, платёж {payment} в месяц.", {
              loan: action.loan,
              rate: formatPercent(action.interest_rate, 1),
              payment: formatMoney(action.monthly_payment ?? 0, 0),
            })}
          </p>
          {action.options?.length ? (
            <p className="fp-crisis__note">
              {t("Что просить: {options}.", { options: action.options.join(", ") })}
            </p>
          ) : null}
        </>
      );
    }

    default:
      return null;
  }
}

export function CrisisPlanSection({ plan }: { plan?: CrisisPlan | null }) {
  if (!plan) return null;

  const { title, lead } = SEVERITY[plan.severity] ?? UNKNOWN_SEVERITY;
  const runway = plan.runway_months;
  const actions = plan.actions ?? [];

  return (
    <section
      className="fp-panel fp-crisis"
      aria-labelledby="fp-crisis-title"
      /* 🔴 Второй канал сверх текста. Спокойный тон — не значит плоский: `critical`
         и `recoverable_from_liquidity` выглядели побайтово одинаково, при том что одно
         решается одним ходом, а во втором накоплений меньше чем на месяц. Атрибут даёт
         CSS различить их без красной заливки и без паники (design-critic). */
      data-severity={plan.severity}
    >
      {/* Появление секции объявляется программе чтения: она возникает ровно в момент,
          когда пересчитанный план впервые оказался дефицитным, а фокус в это время
          остаётся на контролах настроек выше (WCAG 4.1.3, a11y-auditor). Объявляем
          факт, а не весь разбор — иначе диктор зачитает секцию целиком. */}
      <p className="sr-only" role="status" aria-live="polite">
        {t("Свободных денег не хватает: показан разбор, что можно сделать.")}
      </p>

      <h2 id="fp-crisis-title">{t(title)}</h2>
      <p className="fp-lede">{t(lead)}</p>

      <dl className="fp-crisis__facts">
        {/* 🔴 Дефицит — главный показатель экрана ([IA-01]): он ответ на вопрос
            «насколько всё плохо» и единица измерения всего ниже — карточка сокращения
            расходов печатает ровно эту же сумму. */}
        <div className="fp-crisis__fact fp-crisis__fact--primary">
          <dt>{t("Не хватает в месяц")}</dt>
          <dd data-testid="fp-crisis-deficit">{formatMoney(plan.deficit, 0)}</dd>
        </div>
        {/* Запас хода необязателен: при нулевом дефиците он не определён, а ноль
            читается как «денег не осталось» — противоположное по смыслу. */}
        {runway != null && (
          <div className="fp-crisis__fact">
            <dt>{t("Хватит накоплений на")}</dt>
            <dd data-testid="fp-crisis-runway">
              {formatRunway(runway)} {monthsLabel(runway)}
            </dd>
          </div>
        )}
        <div className="fp-crisis__fact">
          <dt>{t("Можно тратить в месяц")}</dt>
          <dd data-testid="fp-crisis-ceiling">{formatMoney(plan.max_affordable_expenses, 0)}</dd>
        </div>
      </dl>

      {/* 🔴 `actions` необязателен ПО КОНТРАКТУ: у поля есть `default_factory=list`
          на бэкенде, значит в OpenAPI оно не попадает в `required`, и генератор
          выводит `actions?: CrisisAction[]`. Обращение к `.length` напрямую роняло
          `tsc` в CI, где сборка идёт от снимка контракта. Список пустой и список
          отсутствующий здесь означают одно — показывать нечего. */}
      {actions.length > 0 && (
        <>
          <h3 className="fp-crisis__actions-title">{t("Что можно сделать")}</h3>
          {/* `role="list"` обязателен при `list-style: none`: WebKit снимает роль списка,
              и VoiceOver не объявит «список, N элементов» (a11y-auditor). Тот же приём
              уже применён в `PlanHistorySection`. */}
          <ul className="fp-crisis__actions" role="list">
            {actions.map((action, index) => (
              <ActionCard key={`${action.type}-${index}`} action={action} />
            ))}
          </ul>
        </>
      )}
    </section>
  );
}
