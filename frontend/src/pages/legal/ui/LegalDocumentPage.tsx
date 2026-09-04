import { useEffect, useRef } from "react";
import { Link, useParams } from "@tanstack/react-router";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { legalLink, useLegalDocument, useLegalDocuments } from "@entities/legal";
import { Button } from "@shared/ui";
import { extractErrorMessage } from "@shared/lib/api/extractErrorMessage";
import { formatDate } from "@shared/lib/date/formatDate";
import { t } from "@shared/lib/i18n/t";
import "./LegalDocumentPage.css";

/**
 * Страница юридического документа (остаток L7, v8.44.0).
 *
 * 🔴 Последнее препятствие к сносу Jinja. Футер (v8.40.0) ссылается на `/legal/privacy`,
 * `/legal/terms`, `/legal/cookies` — до этого батча это были Jinja-роуты, и снос
 * превратил бы требование 152-ФЗ в мёртвые ссылки.
 *
 * Текст приходит из `docs/legal/*.md` через API — из того же файла, что печатается
 * в `docx/` для предъявления. Перепечатать его во фронте было нельзя: разошёлся бы
 * с официальным пакетом на первой правке, и в споре пришлось бы доказывать, какая из
 * редакций показана человеку.
 */

/** Адрес (`/legal/privacy`) и ключ (`privacy_policy`) — разные строки. Сопоставление
 * берётся из реестра, а не из зашитой таблицы: реестр на бэкенде и есть источник правды
 * об адресах. Появится седьмой документ — он откроется сам, без правки фронта. */
function resolveSlug(
  registry: Record<string, { url: string }> | undefined,
  path: string,
): string | null {
  if (!registry) return null;
  const found = Object.entries(registry).find(([, doc]) => doc.url === path);
  return found ? found[0] : null;
}

/** Заголовок документа показан один раз. Каждый файл пакета начинается со своего `# …`,
 * и без этого на экране стояли бы два почти одинаковых заголовка подряд. Убирается
 * ровно первая строка-заголовок, текст документа не трогается. */
function stripLeadingHeading(markdown: string): string {
  return markdown.replace(/^\s*#\s+.*\r?\n/, "");
}

/**
 * Таблица в обёртке, а не сама по себе.
 *
 * 🔴 Первая редакция ставила `display: block; overflow-x: auto` прямо на `<table>` —
 * и этим снимала с неё роль таблицы: скринридер переставал объявлять «таблица, N строк»
 * и терял навигацию по ячейкам (WCAG 1.3.1). Прокрутка переехала на обёртку, таблица
 * осталась таблицей. Обёртке дан `tabIndex` и имя: прокручиваемая область без фокуса
 * недостижима с клавиатуры (WCAG 2.1.1).
 */
const MARKDOWN_COMPONENTS = {
  table: ({ children, ...props }: React.ComponentPropsWithoutRef<"table">) => (
    <div
      className="fp-legal-page__table-wrap"
      tabIndex={0}
      role="group"
      aria-label={t("Таблица документа")}
    >
      <table {...props}>{children}</table>
    </div>
  ),
};

export function LegalDocumentPage() {
  const { doc } = useParams({ strict: false }) as { doc?: string };
  const registry = useLegalDocuments();
  const path = `/legal/${doc ?? ""}`;
  const slug = resolveSlug(registry.data?.documents, path);
  const document = useLegalDocument(slug);
  const headingRef = useRef<HTMLHeadingElement>(null);

  // 🔴 «Реестр ещё едет» и «такого документа нет» — разные состояния. Первая редакция
  // их путала и показывала гостю «документа нет» на исправной ссылке из футера, пока
  // реестр был в пути.
  const resolving = registry.isLoading || (slug === null && !registry.isError);
  const unknown = !registry.isLoading && !registry.isError && slug === null;

  const meta = registry.data?.documents[slug ?? ""];
  const title = meta?.title ?? t("Юридический документ");
  const resolved = slug !== null || unknown;

  /* Фокус переносится ОДИН раз — когда документ определён. Первая редакция вешала
     эффект на `slug` без условия: пока реестр ехал, `slug` был `null`, заголовок
     показывал общее «Юридический документ», фокус уезжал туда, а через мгновение
     переставлялся на настоящее название — скринридер перебивал сам себя
     (a11y-auditor). */
  useEffect(() => {
    if (resolved) headingRef.current?.focus();
  }, [resolved, slug]);

  /* Заголовок вкладки (WCAG 2.4.2). Три документа живут на трёх адресах, а во вкладках,
     истории и закладках都 назывались «FINPILOT» — различить их было нельзя. Сверять
     оферту с политикой в соседних вкладках — обычный сценарий именно здесь. */
  useEffect(() => {
    const previous = window.document.title;
    if (unknown) {
      window.document.title = `${t("Документ не найден")} — FINPILOT`;
    } else if (meta) {
      window.document.title = `${meta.title} — FINPILOT`;
    }
    return () => {
      window.document.title = previous;
    };
  }, [meta, unknown]);

  const siblings = Object.values(registry.data?.documents ?? {})
    .filter((doc) => doc.url !== path)
    .map((doc) => ({ title: doc.title, url: doc.url }));

  return (
    <main className="fp-legal-page">
      {/* Возврат — НАВЕРХУ, до текста. Внизу он оказывался за девяноста строками
          прокрутки, то есть практически не существовал на телефоне ([IA-02]). */}
      <p className="fp-legal-page__back">
        <Link to="/">{t("← На главную")}</Link>
      </p>

      <h1 ref={headingRef} tabIndex={-1}>
        {unknown ? t("Документ не найден") : title}
      </h1>

      {meta && (
        <p className="fp-legal-page__meta">
          {t("ред. {version} от {date}", {
            version: meta.version,
            date: formatDate(meta.effective_from),
          })}
        </p>
      )}

      {unknown && (
        <p className="fp-legal-page__note">
          {t("Такого документа нет. Возможно, ссылка устарела — все документы есть в футере.")}
        </p>
      )}

      {!unknown && (resolving || document.isLoading) && (
        <p className="fp-legal-page__note" role="status">
          {t("Загружаем документ…")}
        </p>
      )}

      {(registry.isError || document.isError) && !unknown && (
        <div className="fp-legal-page__note" role="alert">
          {/* 🔴 Диагноз берётся у сервера, а не выдумывается. Бэкенд на пропавший файл
              пакета отвечает 503 «Текст документа временно недоступен. Обратитесь
              в поддержку» — первая редакция выбрасывала это и подставляла «проверьте
              соединение», отправляя человека чинить исправный Wi-Fi (design-critic). */}
          <p>
            {extractErrorMessage(
              registry.error ?? document.error,
              t("Не удалось загрузить документ. Проверьте соединение и попробуйте снова."),
            )}
          </p>
          <Button
            variant="ghost"
            onClick={() => {
              void registry.refetch();
              void document.refetch();
            }}
          >
            {t("Попробовать снова")}
          </Button>
        </div>
      )}

      {document.data && (
        /* Разметка строится react-markdown БЕЗ `rehype-raw`: сырой HTML из текста
           не исполняется и в дерево не попадает. Источник доверенный (файл в репе),
           но доверие — дисциплина, а не механизм: документ, отредактированный через
           будущую админку, иначе стал бы XSS. */
        <article className="fp-legal-page__body">
          <ReactMarkdown remarkPlugins={[remarkGfm]} components={MARKDOWN_COMPONENTS}>
            {stripLeadingHeading(document.data.content)}
          </ReactMarkdown>
        </article>
      )}

      {/* Соседние документы. Jinja-версия давала переход между ними («См. также»),
          и он был потерян при переносе: политику и оферту сверяют друг с другом,
          возвращаться ради этого в футер через весь текст — лишний путь ([IA-04]). */}
      {siblings.length > 0 && (
        <nav className="fp-legal-page__siblings" aria-label={t("Другие документы")}>
          <p className="fp-legal-page__siblings-title">{t("Другие документы")}</p>
          <ul role="list">
            {siblings.map((doc) => (
              <li key={doc.url}>
                <Link {...legalLink(doc.url)}>{doc.title}</Link>
              </li>
            ))}
          </ul>
        </nav>
      )}
    </main>
  );
}
