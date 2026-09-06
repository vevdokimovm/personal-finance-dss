import { useRef } from "react";
import { useSpendingAdvice } from "@entities/spending";
import type {
  CategoryStatsSchema,
  GoalImpactSchema,
  SpendingAdviceSchema,
  TemporalPatternSchema,
} from "@entities/spending";
import { ConsentRequiredPanel } from "@entities/consents";
import { SessionExpiredPanel, isSessionExpired } from "@entities/auth";
import { Button, ListSkeleton, StatePanel } from "@shared/ui";
import { extractErrorMessage, getConsentRequiredDetail } from "@shared/lib/api/extractErrorMessage";
import { formatMoney } from "@shared/lib/money/formatMoney";
import { pluralize } from "@shared/lib/i18n/plural";
import { t } from "@shared/lib/i18n/t";
import "./SpendingPage.css";

/**
 * Советы по расходам — последний пункт §8.2 «ГЛАВНОЕ» (v8.54.0).
 *
 * `GET /planning/spending-advice` живёт с мат-модели v3.0.0 и не имел фронта вовсе:
 * три слоя анализа считались и не показывались никому. Аудит `independent-expert`
 * 05.09.2026 поймал вахту на утверждении «§8.2 закрыт целиком» — чекбокс всё это
 * время стоял пустым.
 *
 * 🔴 Экран отвечает на один вопрос: **где я трачу больше своей нормы и сколько можно
 * вернуть.** Поэтому сумма экономии стоит первой и самой крупной, а разбор — под ней.
 * Норма категории — медиана прошлых месяцев (не среднее) и MAD вместо сигмы: один
 * отпуск не должен переписывать норму «Транспорта».
 */

/** Модель требует минимум трёх завершённых месяцев (`MIN_MONTHS` в
 * `app/core/spending_advice.py`). Меньше — норму считать не из чего, и это надо
 * сказать словами: пустой экран человек читает как поломку продукта. */
const MIN_MONTHS = 3;

const MONTHS: [string, string, string] = ["месяц", "месяца", "месяцев"];

/** Причина совета человеческим языком. `overspend` и `discretionary` — машинные
 * слова модели, и в русском интерфейсе им не место ([CMP-03]). */
const REASON_LABELS: Record<string, string> = {
  overspend: "перерасход против нормы",
  discretionary: "необязательные траты",
};

function AdviceCard({ item }: { item: SpendingAdviceSchema }) {
  return (
    <li className="fp-spending__advice" data-testid={`fp-advice-${item.category}`}>
      <p className="fp-spending__advice-head">
        <span className="fp-spending__category">{item.category}</span>
        {/* 🔴 Число НЕ акцентное: акцентный зелёный держит только итоговая сумма.
            Пять советов — пять зелёных чисел, и итог перестаёт быть ответом
            (design-critic; бриф §1.1 «акцент работает, только если его мало»). */}
        <span className="fp-spending__saving">{formatMoney(item.potential_saving, 0)}</span>
      </p>
      <p className="fp-spending__message">{item.message}</p>
      {/* 🔴 Норма стоит рядом с текущим расходом всегда. «Потратили 20 000 ₽» без
          «обычно 15 000 ₽» — это выписка, а не повод что-то менять. Сравнение —
          суть карточки, поэтому набрано телом, а не третичной подписью. */}
      <p className="fp-spending__compare">
        {t("Сейчас")} {formatMoney(item.current, 0)}
        <span aria-hidden="true"> · </span>
        {t("обычно")} {formatMoney(item.baseline, 0)}
      </p>
      <p className="fp-spending__numbers">{t(REASON_LABELS[item.reason] ?? item.reason)}</p>
    </li>
  );
}

function StatsRow({ row }: { row: CategoryStatsSchema }) {
  return (
    <li className="fp-spending__stats-row" data-testid={`fp-stats-${row.category}`}>
      <span className="fp-spending__category">{row.category}</span>
      <span className="fp-spending__numbers">
        {t("Сейчас")} {formatMoney(row.current, 0)}
        <span aria-hidden="true"> · </span>
        {t("норма")} {formatMoney(row.baseline, 0)}
      </span>
      {/* Аномалия названа словом, а не оставлена внутри z-score: число 5.1 не говорит
          человеку ничего, «необычно много» говорит всё (WCAG 1.4.1 — не одним цветом). */}
      {row.is_anomaly && (
        <span className="fp-spending__flag">{t("необычно много для этой категории")}</span>
      )}
    </li>
  );
}

function TrendRow({ row }: { row: TemporalPatternSchema }) {
  const rising = row.direction === "rising";
  return (
    <li className="fp-spending__trend" data-testid={`fp-trend-${row.category}`}>
      <span className="fp-spending__category">{row.category}</span>
      {/* Направление словом: «+8,5 %» человек читает как долю, а не как рост. */}
      <span>{rising ? t("растёт") : t("снижается")}</span>
      <span className="fp-spending__numbers">
        {formatMoney(Math.abs(row.slope_abs), 0)} {t("в месяц")}
      </span>
    </li>
  );
}

function GoalImpactRow({ row, index }: { row: GoalImpactSchema; index: number }) {
  /* 🔴 Три поля необязательны и означают разное: бессрочную цель, отсутствие
     пополнений вовсе и невозможность посчитать выигрыш. Подставить ноль в любое
     из них — сказать человеку неправду о его собственной цели. */
  const earlier = row.months_earlier;
  const notFunded = row.eta_now === null;
  /* 🔴 Наличие срока определяется СВОИМ полем, а не выводится из выигрыша
     (нашёл `/code-review ultra`). Фильтр `Math.round(earlier) >= 1` ниже открыл
     ветку, до него недостижимую: при `0 < earlier < 0.5` цель пополняется
     (`eta_now` посчитан, значит `notFunded` ложь), первая ветка отсекается —
     и подпись «срок не задан» доставалась цели с выставленным дедлайном.
     Правка, убравшая одну неправду, сказала бы другую. */
  const hasDeadline = row.months_to_deadline !== null && row.months_to_deadline !== undefined;
  return (
    <li
      className="fp-spending__goal"
      data-testid={`fp-goal-impact-${row.goal_name}`}
      data-index={index}
    >
      <span className="fp-spending__category">{row.goal_name}</span>
      {/* 🔴 Округление до нуля отсекается (нашёл `/code-review`): бэкенд не фильтрует
          малые значения, и `months_earlier = 0.2` давало «на 0 месяцев раньше» —
          выигрыш, поданный как выигрыш, которого нет. Тот же класс, что решение
          не подставлять ноль вместо отсутствующего поля. */}
      {earlier !== null && earlier !== undefined && Math.round(earlier) >= 1 ? (
        /* Склонение через `pluralize`: «на 1 месяца раньше» в главной формулировке
           выигрыша читается как сломанный шаблон, а это единственная фраза, ради
           которой блок целей и существует. */
        <span>{t("на {n} раньше", { n: pluralize(Math.round(earlier), MONTHS) })}</span>
      ) : notFunded ? (
        <span>{t("цель пока не пополняется — экономию можно направить на неё")}</span>
      ) : hasDeadline /* Срок есть, а выигрыш меньше половины месяца: сказать про него нечего,
           и молчание честнее любой из двух подписей. Строка не пропадает —
           сумма перенаправленной экономии ниже остаётся. */ ? null : (
        <span>{t("срок не задан")}</span>
      )}
      <span className="fp-spending__numbers">
        {t("свободно")} {formatMoney(row.redirected_saving, 0)} {t("в месяц")}
      </span>
    </li>
  );
}

export function SpendingPage() {
  const query = useSpendingAdvice();
  /* Фокус на заголовок после успешной выдачи согласия и после повтора запроса:
     иначе он улетает в начало документа, и человек ищет, где он оказался
     (тот же приём и та же причина, что в `AssetsPage`). */
  const headingRef = useRef<HTMLHeadingElement>(null);

  const heading = (
    <h1 ref={headingRef} tabIndex={-1}>
      {t("Советы по расходам")}
    </h1>
  );

  if (query.isLoading) {
    return (
      <main className="fp-spending">
        {heading}
        <div data-testid="fp-spending-loading">
          <ListSkeleton rows={3} />
        </div>
      </main>
    );
  }

  if (query.isError || !query.data) {
    /* 🔴 403 «согласие на финданные отозвано» — не поломка, а известный системе отказ
       с понятным выходом. Показывать его тем же «недоступно», что сетевую ошибку,
       значит прятать от человека причину, которую продукт знает. */
    /* 401 — истёкшая сессия: «Повторить» вернул бы её бесконечно (гипотеза 7). */
    if (isSessionExpired(query.error)) {
      return (
        <main className="fp-spending">
          {heading}
          <SessionExpiredPanel redirectTo="/spending" />
        </main>
      );
    }
    const consentDetail = getConsentRequiredDetail(query.error);
    if (consentDetail) {
      return (
        <main className="fp-spending">
          {heading}
          <ConsentRequiredPanel
            detail={consentDetail}
            onGranted={() => void query.refetch().then(() => headingRef.current?.focus())}
          />
        </main>
      );
    }
    return (
      <main className="fp-spending">
        {heading}
        <StatePanel
          title={t("Не удалось посчитать советы")}
          role="alert"
          action={
            <Button
              variant="primary"
              onClick={() => void query.refetch().then(() => headingRef.current?.focus())}
            >
              {t("Повторить")}
            </Button>
          }
        >
          {extractErrorMessage(
            query.error,
            t("Разбор трат сейчас недоступен. Проверьте соединение и попробуйте ещё раз."),
          )}
        </StatePanel>
      </main>
    );
  }

  const data = query.data;
  /* 🔴 Одни ворота на ВСЕ блоки, а не только на итог. Иначе при `months_with_data < 3`
     и непустом `advice` экран сказал бы «советы появятся, когда наберётся история»
     и тут же показал бы их список — сообщил бы человеку неправду о самом себе. */
  const enoughData = data.months_with_data >= MIN_MONTHS;
  const advice = enoughData ? (data.advice ?? []) : [];
  const stats = enoughData ? (data.stats ?? []) : [];
  const trends = enoughData ? (data.temporal_patterns ?? []) : [];
  const goalImpact = enoughData ? (data.goal_impact ?? []) : [];

  return (
    <main className="fp-spending">
      {heading}
      <p className="fp-spending__window" data-testid="fp-spending-window">
        {t("Разбор за последние {window}, текущий период {period}", {
          window: pluralize(data.months_window, MONTHS),
          period: data.current_period,
        })}
      </p>

      {/* Сумма — первый ответ экрана: человек пришёл узнать «сколько», а не
          «в каких строках». Показывается только когда она существует: ноль в крупной
          рамке выглядит достижением, которого не было. */}
      {/* 🔴 WCAG 4.1.3. Ветки «мало данных» и «в пределах нормы» объявляются сами —
          их рисует `StatePanel` с `role="status"`. Главный случай экрана, ради которого
          он и открыт, не объявлялся ничем: человек, оставшийся на заголовке во время
          скелетона, не узнавал, что расчёт кончился (a11y-auditor). Объявляем ИТОГ,
          а не весь список: иначе диктор зачитал бы все карточки заново. */}
      {advice.length > 0 && (
        <p className="sr-only" role="status" aria-live="polite">
          {t("Разбор готов: можно освободить {sum} в месяц, категорий с перерасходом — {n}", {
            sum: formatMoney(data.total_potential_saving, 0),
            n: advice.length,
          })}
        </p>
      )}

      {advice.length > 0 && (
        <p className="fp-spending__total" data-testid="fp-spending-total">
          {t("Можно освободить")} <strong>{formatMoney(data.total_potential_saving, 0)}</strong>{" "}
          {t("в месяц")}
        </p>
      )}

      {!enoughData && (
        <StatePanel title={t("Данных пока мало")}>
          {t(
            "Норма расходов считается по завершённым месяцам, и их нужно минимум три. " +
              "Сейчас есть {n} — советы появятся, когда наберётся история.",
            { n: pluralize(data.months_with_data, MONTHS) },
          )}
        </StatePanel>
      )}

      {enoughData && advice.length === 0 && (
        <StatePanel title={t("Расходы в пределах вашей нормы")}>
          {t(
            "Перерасхода по категориям не видно: траты держатся около привычного уровня. " +
              "Это хорошая новость, а не отсутствие данных.",
          )}
        </StatePanel>
      )}

      {advice.length > 0 && (
        <>
          <h2>{t("Где можно сократить")}</h2>
          <ul className="fp-spending__list">
            {advice.map((item) => (
              <AdviceCard key={item.category} item={item} />
            ))}
          </ul>
        </>
      )}

      {goalImpact.length > 0 && (
        <>
          <h2>{t("Что это даст целям")}</h2>
          {/* Ради этого блока экран и существует: экономия сама по себе абстрактна,
              «цель на четыре месяца раньше» — нет. Поэтому он и советы держат рамку
              и поверхность, а справочные разделы ниже идут простыми строками. */}
          <ul className="fp-spending__list">
            {/* Ключ с индексом: `Goal.name` в БД — обычный `String(255)` без
                уникальности, две цели с одним именем давали дублирующиеся ключи
                (React переиспользует не тот узел) и коллизию `data-testid`. */}
            {goalImpact.map((row, index) => (
              <GoalImpactRow key={`${row.goal_name}-${index}`} row={row} index={index} />
            ))}
          </ul>
        </>
      )}

      {trends.length > 0 && (
        <>
          <h2>{t("Куда движутся траты")}</h2>
          <ul className="fp-spending__list fp-spending__list--plain">
            {trends.map((row) => (
              <TrendRow key={row.category} row={row} />
            ))}
          </ul>
        </>
      )}

      {stats.length > 0 && (
        <>
          <h2>{t("Разбор по категориям")}</h2>
          <ul className="fp-spending__list fp-spending__list--plain">
            {stats.map((row) => (
              <StatsRow key={row.category} row={row} />
            ))}
          </ul>
        </>
      )}
    </main>
  );
}
