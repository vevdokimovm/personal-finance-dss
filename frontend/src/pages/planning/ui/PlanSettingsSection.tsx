import { useState } from "react";
import { useUserPrefs, useUpdateUserPrefs } from "@entities/user-prefs";
import { useKeyRate } from "@entities/plan-summary";
import { Button, ListSkeleton, StatePanel, toast } from "@shared/ui";
import { t } from "@shared/lib/i18n/t";
import { formatNumber, formatPercent } from "@shared/lib/money/formatMoney";
import "./PlanSettingsSection.css";

/**
 * Параметры расчёта плана — риск-профиль, минимальная ликвидность, ставка по накоплениям.
 *
 * 🔴 До v8.42.0 изменить их в React было НЕЛЬЗЯ ВООБЩЕ. Контролы жили только в Jinja
 * (`frontend/templates/planning.html:19-51`), и `planning.html` оставался единственным
 * способом настроить план под себя. Риск-профиль при этом — центральный параметр
 * матмодели: он задаёт веса SAW и целевую ликвидность (`app/core/ranking.py::RISK_PROFILES`,
 * пять профилей). Человек в React-версии видел рекомендацию, рассчитанную по чужому
 * умолчанию, и повлиять на неё не мог.
 *
 * Это же держало снос Jinja: разбор `2026-08-14_jinja_frontend_removal.md` назвал
 * контролы плана вторым условием снятия Группы 2, и оно не было выполнено, хотя
 * CRUD-паритет 5/5 закрыт с v8.30.0.
 *
 * Применение — явной кнопкой, а не по каждому движению ползунка.
 *
 * 🔴 Обоснование исправлено после разбора design-critic. Первая редакция ссылалась на
 * тяжесть пересчёта — довод ЛОЖНЫЙ: на этом же экране `ForecastControls` гоняет тот же
 * Монте-Карло живьём с дебаунсом 500 мс. Настоящая причина другая и весомее: в Jinja
 * контролы были параметрами ОДНОГО запроса, а здесь PATCH пишет ПОСТОЯННЫЕ настройки
 * профиля — они дальше действуют на дашборде, в экспорте и в сохранённых снимках плана.
 * Запись настроек по движению ползунка была бы записью того, чего человек не выбирал.
 *
 * Поэтому же кнопка называется «Сохранить и пересчитать»: подпись «Пересчитать» описывала
 * половину действия и умалчивала о необратимой записи.
 */

/** Подписи риск-профилей — те же, что в каноне (`RISK_PROFILES[i].label`). Ведутся здесь,
 * потому что бэкенд отдаёт их только внутри готового плана, а выбрать профиль нужно ДО
 * расчёта. Расхождение ловит гейт `tests/test_risk_profiles_ui.py`. */
const RISK_LABELS: Record<number, string> = {
  1: "Консервативный",
  2: "Умеренно-консервативный",
  3: "Сбалансированный",
  4: "Умеренно-агрессивный",
  5: "Агрессивный",
};

/** Что означает выбор — человеческим языком, а не через веса SAW. */
const RISK_HINTS: Record<number, string> = {
  1: "Сначала подушка безопасности, цели подождут",
  2: "Осторожно: запас важнее скорости",
  3: "Поровну между запасом, долгами и целями",
  4: "Быстрее к целям, запас поменьше",
  5: "Максимум в цели и долги, минимальный запас",
};

const RISK_VALUES = [1, 2, 3, 4, 5];

export function PlanSettingsSection({ planPending = false }: { planPending?: boolean }) {
  const prefs = useUserPrefs();
  const update = useUpdateUserPrefs();
  // 🔴 «Идёт работа» — это PATCH ПЛЮС последующий пересчёт плана. Первая редакция
  // смотрела только на PATCH: тост «План пересчитан» выскакивал по ответу настроек,
  // когда тяжёлый пересчёт ещё не начинался, а предупреждение «план по прежним
  // параметрам» исчезало ровно тогда, когда оно было правдой (design-critic).
  const busy = update.isPending || planPending;
  // Ключевая ставка ЦБ — ориентир по умолчанию для `r_bench`. Берётся с сервера, а не
  // зашита числом: ставка меняется, а зашитая устареет молча.
  const keyRateQuery = useKeyRate();
  const keyRate = keyRateQuery.data?.key_rate ?? null;

  // Черновик: человек двигает ползунки, видит значения сразу, а расчёт запускает сам.
  // 🔴 `null` означает «не трогал» — тогда показывается сохранённое значение. Синхронизации
  // эффектом здесь НЕТ: она давала лишний каскад рендеров (тот же класс, что в
  // CookieBanner), а главное — затирала бы уже сделанный человеком выбор ответом
  // фонового запроса.
  const [risk, setRisk] = useState<number | null>(null);
  const [lMin, setLMin] = useState<number | null>(null);
  const [rBench, setRBench] = useState<number | null>(null);

  if (prefs.isLoading) return <ListSkeleton rows={3} />;

  if (prefs.error || !prefs.data) {
    return (
      <StatePanel
        role="alert"
        title={t("Не получилось загрузить параметры расчёта")}
        action={
          <Button variant="ghost" onClick={() => prefs.refetch()}>
            {t("Повторить")}
          </Button>
        }
      >
        {t("План показан по прежним параметрам — они не изменились.")}
      </StatePanel>
    );
  }

  const saved = prefs.data;
  const currentRisk = risk ?? saved.risk_tolerance;
  const currentLMin = lMin ?? saved.l_min;
  const currentRBench = rBench ?? saved.r_bench;

  const dirty =
    currentRisk !== saved.risk_tolerance ||
    currentLMin !== saved.l_min ||
    currentRBench !== saved.r_bench;

  function apply() {
    if (busy || !dirty) return;
    update.mutate(
      { risk_tolerance: currentRisk, l_min: currentLMin, r_bench: currentRBench },
      {
        onSuccess: () => toast.success(t("План пересчитан по новым параметрам")),
        onError: () => toast.error(t("Не получилось сохранить параметры. Попробуйте ещё раз.")),
      },
    );
  }

  return (
    <section className="fp-panel fp-plan-settings" aria-labelledby="fp-plan-settings-title">
      <h2 id="fp-plan-settings-title">{t("Параметры расчёта")}</h2>
      <p className="fp-lede">
        {t(
          "От них зависит рекомендация: насколько беречь запас, сколько держать в ликвидности " +
            "и под какую ставку копить.",
        )}
      </p>

      <fieldset className="fp-plan-settings__group">
        <legend className="fp-plan-settings__legend">{t("Риск-профиль")}</legend>
        {/* Радиокнопки, а не пять <button>: выбор один из пяти — нативная семантика даёт
            клавиатурную навигацию стрелками и озвучку «2 из 5» бесплатно ([A11Y-03]).
            🔴 Без вложенного `role="radiogroup"`: `<fieldset>` с `<legend>` уже даёт роль
            группы с тем же именем, и два слоя подряд объявляли контекст дважды —
            «Риск-профиль, группа → Риск-профиль, группа радиокнопок» (a11y-auditor). */}
        <div className="fp-plan-settings__risks" aria-describedby="fp-risk-hint">
          {RISK_VALUES.map((value) => (
            <label key={value} className="fp-plan-settings__risk">
              <input
                type="radio"
                name="risk-profile"
                value={value}
                checked={currentRisk === value}
                onChange={() => setRisk(value)}
              />
              <span className="fp-plan-settings__risk-label">{RISK_LABELS[value]}</span>
            </label>
          ))}
        </div>
        {/* Связана с группой через `aria-describedby`: иначе переключающийся стрелками
            услышит название профиля, но не смысл выбора (a11y-auditor). */}
        <p className="fp-plan-settings__hint" id="fp-risk-hint">
          {RISK_HINTS[currentRisk]}
        </p>
      </fieldset>

      <div className="fp-plan-settings__field">
        {/* Термин канона — «ликвидность» (так же названа метрика ниже, MetricsGrid).
            «Запас» рядом со «свободным резервом» на том же экране указывал бы на разные
            величины похожими словами ([CMP-03], design-critic). */}
        <label htmlFor="fp-lmin">{t("Минимальная ликвидность, мес. расходов")}</label>
        {/* `<span>`, а не `<output>`: у `output` неявная роль `status`, и три live-региона
            на одной панели соревновались бы за озвучку. Значение слайдера уже
            объявляется через `aria-valuetext`. */}
        <span className="fp-plan-settings__value">{formatNumber(currentLMin, 1)}</span>
        <input
          id="fp-lmin"
          type="range"
          min={0}
          max={10}
          step={0.5}
          value={currentLMin}
          /* Нативный `aria-valuenow` — голое число («3»), без единицы. При навигации
             стрелками AT озвучит именно его, а «3» и «3 месяца» это разное. */
          aria-valuetext={t("{n} мес. расходов", { n: formatNumber(currentLMin, 1) })}
          onChange={(e) => setLMin(Number(e.target.value))}
        />
        <p className="fp-plan-settings__hint">
          {/* 🔴 Прежний текст врал на краю шкалы: при `l_min = 0` отсев по ликвидности
              выключен ВОВСЕ (`app/core/filtering.py:26`), а нижняя граница резерва живёт
              отдельной константой `RESERVE_FLOOR_MONTHS = 2.0`. Человек ставил 0 и читал
              про «жёсткое ограничение», которого в этот момент нет (design-critic). */}
          {currentLMin === 0
            ? t(
                "При нуле отсев по ликвидности выключен: план не будет отбрасывать " +
                  "варианты из-за низкого запаса. Резерв всё равно не опустится ниже " +
                  "двух месяцев — это встроенный минимум модели.",
              )
            : t("Варианты, оставляющие запас ниже этого уровня, план не предложит.")}
        </p>
      </div>

      <div className="fp-plan-settings__field">
        {/* «Параметр расчёта», а не просто «ставка»: на том же экране есть сценарная
            ставка в прогнозе, и одинаковые имена у разных величин путают ([CMP-03]). */}
        <label htmlFor="fp-rbench">{t("Ставка по накоплениям — параметр расчёта")}</label>
        <span className="fp-plan-settings__value">{formatPercent(currentRBench)}</span>
        <input
          id="fp-rbench"
          type="range"
          min={0}
          max={30}
          step={0.5}
          /* В контракте ставка — доля (0…1), на экране проценты: человек говорит «16%»,
             а не «0.16». Преобразование здесь, а не в модели. */
          value={Math.round(currentRBench * 1000) / 10}
          aria-valuetext={t("{n} годовых", { n: formatPercent(currentRBench) })}
          onChange={(e) => setRBench(Number(e.target.value) / 100)}
        />
        <p className="fp-plan-settings__hint">
          {t("Под неё считается рост запаса.")}{" "}
          {/* Jinja давала кнопку «Ставка ЦБ»; без неё обещание «по умолчанию ключевая»
              было просто текстом — вернуться к этому значению ползунком нельзя. */}
          {keyRate !== null && Math.abs(currentRBench - keyRate) > 1e-9 && (
            <button
              type="button"
              className="fp-plan-settings__link"
              onClick={() => setRBench(keyRate)}
            >
              {t("Взять ключевую ставку ЦБ ({n})", { n: formatPercent(keyRate) })}
            </button>
          )}
        </p>
      </div>

      <div className="fp-plan-settings__actions">
        <Button
          variant="primary"
          aria-busy={busy}
          aria-disabled={busy || !dirty}
          /* Кнопка неактивна, пока нечего пересчитывать — но «недоступно» без причины
             это загадка. Объяснение живёт в соседнем узле и всегда в DOM. */
          aria-describedby="fp-plan-settings-state"
          onClick={apply}
        >
          {busy ? t("Считаем…") : t("Сохранить и пересчитать")}
        </Button>
        {/* 🔴 Узел ВСЕГДА в DOM, меняется только текст. Первая редакция монтировала и
            размонтировала его на каждый переход `dirty` — а у слайдеров шаг 0.5, и
            сохранённое значение лежит ровно на сетке: человек, нащупывающий значение
            рядом с дефолтом, пересекал границу туда-обратно много раз за секунды.
            Повторная ВСТАВКА live-региона озвучивается по-разному в NVDA/JAWS/VoiceOver,
            и часть из них прочитала бы сообщение на каждое пересечение (a11y-auditor). */}
        {dirty && !busy && (
          /* 🔴 Откат к сохранённым. Без него настройка необратима на глазок: если
             сохранённая ставка не лежит на шаге 0.5 (например, подтянута из вклада —
             16,3%), вернуться к ней ползунком нельзя вообще, и черновик залипает
             «грязным» навсегда ([FRM-07], design-critic). */
          <Button
            variant="ghost"
            onClick={() => {
              setRisk(null);
              setLMin(null);
              setRBench(null);
            }}
          >
            {t("Вернуть сохранённые")}
          </Button>
        )}
        <p className="fp-plan-settings__dirty" id="fp-plan-settings-state" role="status">
          {busy
            ? t("Пересчитываем план по новым параметрам…")
            : dirty
              ? t("План ниже — по прежним параметрам.")
              : t("Измените параметр, чтобы пересчитать план.")}
        </p>
      </div>
    </section>
  );
}
