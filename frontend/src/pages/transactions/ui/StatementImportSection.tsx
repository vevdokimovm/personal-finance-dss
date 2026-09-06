import { useRef, useState } from "react";
import { useBanks, useUploadStatement } from "@entities/bank-import";
import type { StatementUploadResult } from "@entities/bank-import";
import { Button, toast } from "@shared/ui";
import { formatMoney } from "@shared/lib/money/formatMoney";
import { isConsentRequired } from "@shared/lib/api/extractErrorMessage";
import { t } from "@shared/lib/i18n/t";
import "./StatementImportSection.css";

/**
 * Импорт банковской выписки (v8.43.0).
 *
 * 🔴 Последняя записывающая функция, жившая только в Jinja. `banks_router` из-за неё
 * оставался вне периметра `_FIN`: импорт выписки пачкой обрабатывал финансовые данные
 * БЕЗ согласия, тогда как ручное добавление одной операции его требовало. Гейт нельзя
 * было поставить раньше — `app.js` не умеет показать 403 (`grep "403|consent"` по нему
 * даёт ноль на 2658 строк). Разбор —
 * `docs/reports/decisions/2026-09-04_h3_and_jinja_removal_order.md`.
 *
 * Банк выбирается вручную, но для PDF сервер определяет его ПО СОДЕРЖИМОМУ и выбор
 * в списке считает запасным: ошибка в выпадающем списке отправляла выписку не в тот
 * парсер и давала пустой результат на исправном файле.
 */

/** Банки, для которых сервер умеет разбирать PDF (`routes_banks.py`: сообщение отказа).
 * Остальным PDF предлагать нельзя — человек загрузит и получит «не распознано»,
 * хотя файл исправен ([FRM-03]). */
const PDF_BANKS = new Set(["tinkoff", "vtb", "sber"]);

export function StatementImportSection() {
  const banks = useBanks();
  const upload = useUploadStatement();
  const [bankId, setBankId] = useState("tinkoff");
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<StatementUploadResult | null>(null);
  const [networkError, setNetworkError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const resultRef = useRef<HTMLDivElement>(null);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (upload.isPending) return;
    if (!file) {
      // Немой клик читается как «экран сломался» ([FB-01]).
      toast.error(t("Выберите файл выписки."));
      fileInputRef.current?.focus();
      return;
    }
    // 🔴 Прошлый результат гасим ДО отправки. Иначе во время второй попытки на экране
    // висит «Готово» от первой, а при её отказе — зелёное подтверждение того, чего
    // не произошло (design-critic).
    setResult(null);
    setNetworkError(null);
    upload.mutate(
      { file, bankId },
      {
        onSuccess: (data) => {
          setResult(data);
          if (data.status === "success") {
            setFile(null);
            if (fileInputRef.current) fileInputRef.current.value = "";
          }
        },
        onError: (error) => {
          // Ответ и отказ — в одном месте, а не «разбор инлайном, сеть тостом» ([ST-06]).
          setNetworkError(
            isConsentRequired(error)
              ? t("Согласие на обработку финансовых данных отозвано. Выдайте его в профиле.")
              : t("Не получилось загрузить файл. Проверьте соединение и попробуйте снова."),
          );
          resultRef.current?.focus();
        },
      },
    );
  }

  const failed = result?.status === "error" || networkError !== null;
  const reconciliation = result?.reconciliation as
    { status?: string; message?: string } | null | undefined;
  // 🔴 У сверки ТРИ исхода (`statement_reconcile.py`): `ok` — сошлось, `mismatch` —
  // расхождение, `unavailable` — сверять было нечем (CSV без контрольных итогов, PDF
  // банка без профиля сверки). Первая редакция считала расхождением всё, что не `ok`,
  // и пугала жёлтым предупреждением на полностью исправном импорте (design-critic).
  const mismatch = reconciliation?.status === "mismatch";
  const reconciled = reconciliation?.status === "ok";

  const bankName = banks.data?.find((bank) => bank.id === bankId)?.name ?? bankId;
  const pdfSupported = PDF_BANKS.has(bankId);

  return (
    <section className="fp-panel fp-statement-import" aria-labelledby="fp-import-title">
      <h2 id="fp-import-title">{t("Импорт выписки")}</h2>
      <p className="fp-lede">
        {t(
          "Загрузите выписку из банка — операции добавятся в список. Повторная загрузка " +
            "того же файла дублей не создаст.",
        )}
      </p>

      <form className="fp-statement-import__form" onSubmit={handleSubmit}>
        <div className="fp-entity-form__field">
          <label htmlFor="fp-import-bank">{t("Банк")}</label>
          <select
            id="fp-import-bank"
            value={bankId}
            aria-describedby="fp-import-bank-hint"
            /* Пока список не пришёл, опции с этим value в DOM ещё нет — поле осталось бы
               без определяемого значения (WCAG 4.1.2, a11y-auditor). */
            disabled={banks.isLoading}
            onChange={(e) => setBankId(e.target.value)}
          >
            {(banks.data ?? []).map((bank) => (
              <option key={bank.id} value={bank.id}>
                {bank.name}
              </option>
            ))}
          </select>
          <p className="fp-entity-form__hint" id="fp-import-bank-hint">
            {banks.isLoading
              ? t("Загружаем список банков…")
              : t("Для PDF банк определяется по самому файлу — выбор здесь запасной.")}
          </p>
        </div>

        <div className="fp-entity-form__field">
          <label htmlFor="fp-import-file">{t("Файл выписки")}</label>
          <input
            id="fp-import-file"
            ref={fileInputRef}
            type="file"
            accept=".csv,.xlsx,.pdf,.txt"
            aria-describedby="fp-import-file-hint"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />
          {/* Формат зависит от банка: сервер разбирает PDF только у трёх. Общая подсказка
              «CSV, XLSX или PDF» отправляла бы клиента Альфы за предсказуемым отказом. */}
          <p className="fp-entity-form__hint" id="fp-import-file-hint">
            {pdfSupported
              ? t("{bank}: CSV, XLSX или PDF.", { bank: bankName })
              : t("{bank}: CSV или XLSX. PDF этот банк пока не разбирает.", { bank: bankName })}
          </p>
        </div>

        {/* `ghost`: главное действие экрана «Операции» — добавить операцию, и primary
            принадлежит ей. Два акцента спорят друг с другом ([IA-01]). */}
        <Button
          type="submit"
          variant="ghost"
          aria-busy={upload.isPending}
          aria-disabled={upload.isPending}
        >
          {upload.isPending ? t("Импортируем…") : t("Импортировать")}
        </Button>
      </form>

      {/* 🔴 Отдельный постоянный live-регион под ход работы. Разбор большого PDF занимает
          заметное время, а `aria-busy` — состояние, а не событие: между кликом и ответом
          незрячий пользователь слышал тишину, неотличимую от зависания (a11y-auditor). */}
      <div aria-live="polite" className="sr-only">
        {upload.isPending ? t("Импортируем выписку, подождите…") : ""}
      </div>

      {/* Роль узла ПОСТОЯННА. Первая редакция переключала её между `status` и `alert`
          на смонтированном узле и вкладывала внутрь `StatePanel` с такой же ролью —
          вложенные live-регионы ведут себя по-разному в разных связках браузер+AT,
          и второе сообщение могло пропасть, а первое звучало исправно. */}
      <div ref={resultRef} tabIndex={-1} role="status" className="fp-statement-import__result">
        {networkError && (
          <div className="fp-statement-import__card fp-statement-import__card--error">
            <p className="fp-statement-import__title">{t("Импорт не прошёл")}</p>
            <p className="fp-statement-import__text">{networkError}</p>
          </div>
        )}

        {result && (
          <div
            className={
              failed
                ? "fp-statement-import__card fp-statement-import__card--error"
                : "fp-statement-import__card fp-statement-import__card--ok"
            }
          >
            <p className="fp-statement-import__title">
              {failed ? t("Импорт не прошёл") : t("Готово")}
            </p>
            <p className="fp-statement-import__text">{result.message}</p>

            {result.status === "success" && (
              <p className="fp-statement-import__totals">
                {/* Обе суммы одной точностью: разнобой в паре однородных чисел читается
                    как ошибка данных ([CMP-04]). */}
                {t("Доходы: {income}, расходы: {expense}.", {
                  income: formatMoney(result.total_income ?? 0, 2),
                  expense: formatMoney(result.total_expense ?? 0, 2),
                })}
              </p>
            )}

            {/* Сверка с итогами, объявленными в самой выписке. Положительный исход —
                самый сильный сигнал доверия, который продукт умеет дать по импорту,
                и он был потерян в первой редакции. */}
            {reconciled && (
              <p className="fp-statement-import__reconciled">
                {t("Сверено с итогами банка — сходится.")}
              </p>
            )}

            {mismatch && (
              <p className="fp-statement-import__warn">
                {/* Число расхождения даёт сервер («распознано 78 000 ₽, банк заявляет
                    81 240 ₽»). Без него «проверьте операции» — совет без опоры. */}
                {reconciliation?.message ||
                  t("Итоги выписки не сошлись с импортом — проверьте операции.")}
              </p>
            )}
          </div>
        )}
      </div>
    </section>
  );
}
