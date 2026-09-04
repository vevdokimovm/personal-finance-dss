import { useLegalDocuments } from "@entities/legal";
import { formatDate } from "@shared/lib/date/formatDate";
import { t } from "@shared/lib/i18n/t";
import { clearCookieChoice } from "@widgets/cookie-banner";
import "./LegalFooter.css";

/**
 * Футер со ссылками на юридические документы — требование L7.
 *
 * Стоит на КАЖДОЙ странице, включая гостевые: до входа человек читает оферту и политику
 * чаще, чем после. Поэтому футер живёт в `__root.tsx`, а не в отдельных экранах.
 *
 * Список берётся из `/legal/documents`: реестр на бэкенде (`app/core/legal.py`) —
 * единственный источник правды об адресах и редакциях. Появится седьмой документ —
 * он появится в футере сам.
 *
 * 🔴 При отказе сети футер НЕ исчезает. Первая редакция возвращала `null` на любой
 * ошибке: юридические ссылки пропадали со всех страниц разом, то есть сетевой сбой молча
 * отключал требование (fail-open, design-critic). Адреса документов постоянны и не
 * секретны — запасной список гарантирует, что ссылки есть всегда; редакции при этом
 * не показываются, потому что выдумывать их нельзя.
 */

/** Запасной список — только адреса и названия, без версий: их знает лишь сервер. */
const FALLBACK_DOCUMENTS: { title: string; url: string }[] = [
  { title: "Политика обработки персональных данных", url: "/legal/privacy" },
  { title: "Пользовательское соглашение", url: "/legal/terms" },
  { title: "Политика использования файлов cookie", url: "/legal/cookies" },
];

export function LegalFooter() {
  const legal = useLegalDocuments();

  const documents = legal.data
    ? Object.entries(legal.data.documents).map(([key, doc]) => ({
        key,
        title: doc.title,
        url: doc.url,
        edition: t("ред. {version} от {date}", {
          version: doc.version,
          date: formatDate(doc.effective_from),
        }),
      }))
    : FALLBACK_DOCUMENTS.map((doc) => ({ ...doc, key: doc.url, edition: null }));

  // Все редакции совпадают — говорим это один раз под списком, а не повторяем
  // одинаковую строку у каждого из шести документов (design-critic).
  const editions = new Set(documents.map((doc) => doc.edition));
  const sharedEdition = editions.size === 1 ? [...editions][0] : null;

  return (
    <footer className="fp-legal-footer">
      <nav className="fp-legal-footer__nav" aria-label={t("Юридические документы")}>
        <ul className="fp-legal-footer__list" role="list">
          {documents.map((doc) => (
            <li key={doc.key} className="fp-legal-footer__item">
              {/* Вся строка — одна ссылка: цель нажатия набирает высоту сама, а редакция
                  попадает в доступное имя и звучит при обходе по Tab ([A11Y-09]). */}
              <a href={doc.url} className="fp-legal-footer__link">
                <span className="fp-legal-footer__title">{doc.title}</span>
                {!sharedEdition && doc.edition && (
                  <span className="fp-legal-footer__meta">{doc.edition}</span>
                )}
              </a>
            </li>
          ))}
        </ul>
      </nav>

      <div className="fp-legal-footer__row">
        {sharedEdition && <span className="fp-legal-footer__meta">{sharedEdition}</span>}
        {/* 🔴 Отзыв согласия на аналитику. Без этой кнопки решение по cookie было
            необратимым: `clearCookieChoice` существовал и не вызывался нигде, кроме
            тестов, — то есть «изменить решение» было обещано комментарием и не
            существовало в продукте (design-critic). */}
        <button
          type="button"
          className="fp-legal-footer__reset"
          onClick={() => {
            clearCookieChoice();
            // Баннер читает хранилище при рендере — перезагрузка возвращает выбор.
            window.location.reload();
          }}
        >
          {t("Настройки cookie")}
        </button>
      </div>
    </footer>
  );
}
