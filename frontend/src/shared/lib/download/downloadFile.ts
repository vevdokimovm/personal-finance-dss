/**
 * Скачивание файла с бэкенда — через `fetch` и blob, а НЕ простой ссылкой.
 *
 * Авторизация в проекте — HttpOnly cookie (`shared/api/client.ts`), поэтому
 * `<a href="/api/planning/export.csv" download>` формально сработал бы: cookie летит
 * на same-origin навигацию. Но у ссылки нет обработки отказа. Экспорт стоит за гейтом
 * согласия (`_FIN` на `planning_router` и `export_router` с v8.27.0), и при отозванном
 * согласии сервер отвечает **403 с JSON-телом**. Ссылка скачала бы этот JSON файлом
 * с расширением `.csv` — пользователь получил бы «отчёт», внутри которого текст ошибки,
 * и узнал бы об этом, открыв файл. Тот же исход у 500 и у сетевого сбоя.
 *
 * Поэтому: запрос, проверка статуса, и только на успехе — blob и скачивание. Отказ
 * поднимается наверх как `DownloadError` с телом, чтобы экран показал панель согласия
 * или тост, а не подсунул битый файл.
 */

/** Отказ скачивания. Несёт статус и разобранное тело — по ним экран решает, что показать. */
export class DownloadError extends Error {
  constructor(
    readonly status: number,
    readonly detail?: unknown,
  ) {
    super(`Скачивание не удалось: ${status}`);
    this.name = "DownloadError";
  }
}

/**
 * Имя файла из `Content-Disposition`. Имя даёт СЕРВЕР, а не фронт: там оно уже
 * собрано с датой (`finpilot-plan-2026-09-03.csv`), и дублировать эту логику значило бы
 * держать два источника правды об одном имени.
 *
 * `filename*` (RFC 5987) приоритетнее `filename`: он для этого и заведён — несёт
 * не-ASCII в процентном кодировании, тогда как `filename` в таких случаях содержит
 * урезанную ASCII-версию для старых клиентов.
 */
export function filenameFromDisposition(disposition: string | null): string | null {
  if (!disposition) return null;

  const extended = /filename\*\s*=\s*UTF-8''([^;]+)/i.exec(disposition);
  if (extended) {
    try {
      return decodeURIComponent(extended[1].trim());
    } catch {
      // Битое кодирование — не повод падать: ниже попробуем обычный filename.
    }
  }

  const plain = /filename\s*=\s*"?([^";]+)"?/i.exec(disposition);
  return plain ? plain[1].trim() : null;
}

/** Потолок ожидания. PDF собирается полным пересчётом плана, поэтому щедрый — но
 * конечный: без него подвисший сервер оставлял бы «Готовим файл…» навсегда, а кнопки
 * заблокированными, то есть секция превращалась бы в тупик без выхода ([ST-02]
 * прямо требует таймаут вместо вечного спиннера). */
const TIMEOUT_MS = 60_000;

export interface DownloadOptions {
  /** Имя, если сервер не прислал `Content-Disposition`. */
  fallbackName?: string;
  /** Подмена `fetch` — только для тестов. */
  fetchImpl?: typeof fetch;
  /** Потолок ожидания, мс. */
  timeoutMs?: number;
}

/** Возвращает имя, под которым файл ушёл — чтобы экран мог назвать его в подтверждении,
 * а не сообщать безымянный успех. */
export async function downloadFile(url: string, options: DownloadOptions = {}): Promise<string> {
  const doFetch = options.fetchImpl ?? fetch;
  const response = await doFetch(url, {
    // Обязателен: авторизация в HttpOnly cookie, без него 401 (та же причина,
    // что у настройки сгенерированного клиента).
    credentials: "include",
    signal: AbortSignal.timeout(options.timeoutMs ?? TIMEOUT_MS),
  });

  if (!response.ok) {
    let detail: unknown;
    try {
      detail = ((await response.json()) as { detail?: unknown }).detail;
    } catch {
      // Тело не JSON (или пустое) — статуса достаточно, чтобы показать сообщение.
    }
    throw new DownloadError(response.status, detail);
  }

  const blob = await response.blob();
  const name = filenameFromDisposition(response.headers.get("Content-Disposition"))
    ?? options.fallbackName
    ?? "finpilot-export";

  const href = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = href;
  link.download = name;
  // Ссылка ВСТАВЛЯЕТСЯ в документ, а не кликается отсоединённой: Firefox не
  // запускает скачивание по клику на якоре вне DOM. Скрыта, чтобы не влиять на
  // раскладку и не попадать в порядок обхода.
  link.style.display = "none";
  document.body.appendChild(link);
  link.click();
  link.remove();

  // Освобождение ОТЛОЖЕНО, а не синхронно следом за кликом. Синхронный
  // `revokeObjectURL` успевает убить blob раньше, чем браузер начнёт скачивание —
  // и тогда файла нет, ошибки нет, обратной связи нет: пользователь нажимает трижды
  // и уходит. Найдено design-critic; из всех находок батча эта единственная делала
  // фичу молча неработающей.
  setTimeout(() => URL.revokeObjectURL(href), 0);

  return name;
}
