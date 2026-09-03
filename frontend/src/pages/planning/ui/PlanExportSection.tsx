import { useRef, useState } from "react";
import { ConsentRequiredPanel } from "@entities/consents";
import { Button, toast } from "@shared/ui";
import { downloadFile, DownloadError } from "@shared/lib/download/downloadFile";
import { getConsentRequiredDetail } from "@shared/lib/api/extractErrorMessage";
import type { ConsentRequiredDetail } from "@shared/lib/api/extractErrorMessage";
import { t } from "@shared/lib/i18n/t";
import "./PlanExportSection.css";

/**
 * Выгрузка плана распределения (ROADMAP §8.2 «ГЛАВНОЕ», третья из API-only фич).
 *
 * Три эндпоинта (`/planning/export.csv|xlsx|pdf`) существовали и на фронте не были
 * представлены ни строкой — тот же класс, что H1, уведомления и история планов.
 *
 * Скачивание идёт через `fetch` и blob, а не простой ссылкой, и это не усложнение:
 * экспорт стоит за гейтом согласия, при отозванном согласии сервер отвечает 403 с
 * JSON-телом, и ссылка скачала бы этот JSON файлом с расширением `.csv`. Пользователь
 * получил бы «отчёт» с текстом ошибки внутри и узнал бы об этом, только открыв файл.
 * Подробнее — докстрока `shared/lib/download/downloadFile.ts`.
 *
 * Имя файла берётся из `Content-Disposition`: сервер уже собирает его с датой
 * (`finpilot-plan-2026-09-03.csv`), и повторять эту логику на фронте значило бы держать
 * два источника правды об одном имени.
 */

/** Форматы в порядке ожидаемой частоты: таблица для работы, Excel для бухгалтера,
 * PDF для показа. `label` несёт и расширение, и назначение — «CSV» само по себе
 * пользователю ничего не говорит ([CMP-03]). */
const FORMATS = [
  {
    key: "csv",
    url: "/api/planning/export.csv",
    label: "CSV — таблица для работы",
    fallback: "finpilot-plan.csv",
  },
  {
    key: "xlsx",
    url: "/api/planning/export.xlsx",
    label: "Excel — .xlsx с форматированием",
    fallback: "finpilot-plan.xlsx",
  },
  {
    key: "pdf",
    url: "/api/planning/export.pdf",
    label: "PDF — для печати и показа",
    fallback: "finpilot-plan.pdf",
  },
] as const;

export function PlanExportSection() {
  const [busy, setBusy] = useState<string | null>(null);
  const [consent, setConsent] = useState<ConsentRequiredDetail | null>(null);
  const [status, setStatus] = useState("");
  const headingRef = useRef<HTMLHeadingElement>(null);

  async function handleDownload(format: (typeof FORMATS)[number]) {
    // Второй клик по тому же формату во время запроса не шлёт второй запрос: файл
    // собирается на сервере полным пересчётом плана, и дубль стоит этого пересчёта.
    if (busy) return;
    setBusy(format.key);
    setConsent(null);
    setStatus(t("Готовим файл…"));
    try {
      const name = await downloadFile(format.url, { fallbackName: format.fallback });
      // Успех обязан быть подтверждён ([FB-03]) и ОБЪЯВЛЕН (WCAG 4.1.3). Плашка
      // загрузок браузера подтверждением не считается: это чужой UI, в Safari она
      // мигает и прячется, а при настройке «скачивать без спроса» её нет вовсе.
      // Асимметрия «отказ говорит, успех молчит» — худший из вариантов.
      setStatus(t("Файл {name} готов и сохранён в загрузки.", { name }));
      toast.success(t("Файл {name} сохранён", { name }));
    } catch (error) {
      const detail =
        error instanceof DownloadError ? getConsentRequiredDetail({ detail: error.detail }) : null;
      setStatus("");
      if (detail) {
        // Отсутствие согласия — не сбой, а состояние с понятным выходом: показываем
        // панель, а не тост. Тост исчезает, а путь к согласию нужен на экране.
        setConsent(detail);
        // Кнопка, на которой был фокус, сейчас размонтируется вместе со всем блоком —
        // без переноса фокус провалился бы в <body>, и пользователь потерял бы место
        // на странице (WCAG 2.4.3). Тот же приём уже применён на самой PlanningPage.
        requestAnimationFrame(() => headingRef.current?.focus());
      } else {
        toast.error(t("Не получилось выгрузить план. Попробуйте ещё раз."));
      }
    } finally {
      // В `finally`: после отказа кнопка обязана снова стать доступной, иначе экран
      // превращается в тупик ([IA-04]).
      setBusy(null);
    }
  }

  return (
    <section className="fp-panel fp-plan-export" aria-labelledby="fp-plan-export-title">
      <h2 id="fp-plan-export-title" ref={headingRef} tabIndex={-1}>
        {t("Выгрузить план")}
      </h2>
      <p className="fp-lede">
        {t(
          "Тот же план, что выше: показатели, рекомендованное распределение и допустимые " +
            "варианты. Файл собирается на сервере в момент нажатия, поэтому отражает " +
            "текущие данные, а не то, что было при открытии страницы.",
        )}
      </p>

      {consent ? (
        <ConsentRequiredPanel
          detail={consent}
          headingLevel={3}
          onGranted={() => setConsent(null)}
        />
      ) : (
        <div className="fp-plan-export__actions">
          {FORMATS.map((format) => (
            <Button
              key={format.key}
              variant="ghost"
              aria-busy={busy === format.key}
              /* `aria-disabled` на ВСЕ три, пока идёт любое скачивание: обработчик
                 блокирует клик по любой из них, и без этого признака две соседние
                 кнопки выглядели бы рабочими, а нажатие не давало бы ничего — ни
                 визуально, ни озвученно (WCAG 4.1.2). Именно `aria-disabled`, а не
                 нативный `disabled`: тот выбрасывает кнопку из дерева доступности
                 прямо под фокусом — общий выбор проекта, см. Button.css. */
              aria-disabled={busy !== null}
              onClick={() => void handleDownload(format)}
            >
              {/* Подпись формата СОХРАНЯЕТСЯ во время работы: заменять её на
                  «Готовим файл…» значило бы менять доступное имя, по которому
                  пользователь эту кнопку и нашёл. Ход операции сообщает
                  live-область ниже. */}
              {t(format.label)}
            </Button>
          ))}
        </div>
      )}

      {/* Ход и итог операции — вежливой live-областью, а не сменой подписи кнопки:
          подпись это доступное ИМЯ, и менять его на статус нельзя. */}
      <p className="sr-only" role="status" aria-live="polite">
        {status}
      </p>
    </section>
  );
}
