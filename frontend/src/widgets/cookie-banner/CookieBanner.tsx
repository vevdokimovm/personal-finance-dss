import { useEffect, useState } from "react";
import { useLegalDocuments } from "@entities/legal";
import { Button } from "@shared/ui";
import { Link } from "@tanstack/react-router";
import { legalLink } from "@entities/legal";
import { t } from "@shared/lib/i18n/t";
import { readCookieChoice, saveCookieChoice, type CookieChoice } from "./cookieConsent";
import "./CookieBanner.css";

/**
 * Баннер выбора cookie — юр-требование L6.
 *
 * Требование сформулировано жёстко: **раздельный выбор** «принять всё» и «только
 * необходимые». Одна кнопка «Ок» согласием не является.
 *
 * 🔴 Обе кнопки — ОДНОГО веса и одной ширины. Первая редакция дала согласию `primary`
 * (зелёная заливка), отказу `ghost` и добавила автофокус на согласии: три преимущества
 * подряд у одного варианта. Комментарий рядом при этом утверждал, что кнопки равны —
 * код противоречил сам себе, а получался ровно тот тёмный паттерн, против которого
 * требование и написано (design-critic).
 *
 * 🔴 Фокус при появлении НЕ перехватывается. `role="region"` — ландшафтный регион, а не
 * модалка: скринридер найдёт его landmark-навигацией, а принудительный `focus()` прервал
 * бы чтение и увёл человека оттуда, где он был (a11y-auditor).
 *
 * Выбор привязан к ВЕРСИИ политики (`cookieConsent.ts`): смена редакции спрашивает
 * заново, потому что согласие даётся на конкретный текст.
 */
export function CookieBanner() {
  const legal = useLegalDocuments();
  const version = legal.data?.documents.cookie_policy?.version;
  // Выбор, сделанный ПРЯМО СЕЙЧАС. Прежнее решение в состоянии не хранится: оно
  // выводится из `localStorage` при рендере, без синхронизации эффектом.
  const [justChose, setJustChose] = useState(false);
  const [node, setNode] = useState<HTMLDivElement | null>(null);

  // 🔴 Неизвестная версия — это ОТСУТСТВИЕ выбора, а не согласие. Первая редакция
  // трактовала её как «решение принято»: сетевая ошибка молча отключала требование
  // (fail-open), и аналитические cookie ставились бы без спроса.
  const decided = version ? readCookieChoice(version) !== null : false;
  // Показывать баннер до ответа сервера всё равно нельзя: версия неизвестна, и выбор
  // не к чему было бы привязать.
  const visible = Boolean(version) && !decided && !justChose;

  // Пока баннер виден, страница получает снизу его высоту. Без этого фиксированный
  // баннер накрывает футер с юридическими ссылками (L6 гасил бы L7), а тосты садятся
  // ровно на кнопки выбора. Меряем реальную высоту: на узком экране баннер растёт.
  useEffect(() => {
    const root = document.documentElement;
    if (!visible || !node) {
      root.style.removeProperty("--cookie-banner-h");
      return;
    }
    const apply = () => root.style.setProperty("--cookie-banner-h", `${node.offsetHeight}px`);
    apply();
    const observer = new ResizeObserver(apply);
    observer.observe(node);
    return () => {
      observer.disconnect();
      root.style.removeProperty("--cookie-banner-h");
    };
  }, [visible, node]);

  if (!visible) return null;

  function choose(choice: CookieChoice) {
    saveCookieChoice(choice, version as string);
    setJustChose(true);
    // Кнопка, на которой стоял фокус, размонтируется — без переноса фокус упадёт
    // в <body>, и клавиатурный пользователь начнёт обход документа заново.
    document.getElementById("fp-main")?.focus();
  }

  return (
    <div
      ref={setNode}
      className="fp-cookie-banner"
      // `region`, а не `dialog`: баннер не запирает страницу — читать её до выбора можно,
      // это уведомление с действием, а не окно блокировки.
      role="region"
      aria-label={t("Использование файлов cookie")}
    >
      <div className="fp-cookie-banner__body">
        <p className="fp-cookie-banner__text">
          {t(
            "Необходимые cookie нужны для работы сайта: вход, безопасность, ваши " +
              "настройки. Аналитические помогают находить и устранять ошибки. " +
              "Выберите, что разрешить.",
          )}{" "}
          {/* `Link` с v8.44.0: тексты документов переехали в React, и полная
              перезагрузка ради чтения политики больше не нужна — она стирала
              введённое на форме под баннером. */}
          <Link {...legalLink("/legal/cookies")} className="fp-cookie-banner__link">
            {t("Политика cookie")}
          </Link>
        </p>
        <div className="fp-cookie-banner__actions">
          {/* Один вариант оформления на обе кнопки: отказ не должен быть дороже
              согласия ни кликом, ни вниманием ([CMP-02], [IA-01]). */}
          <Button variant="ghost" onClick={() => choose("all")}>
            {t("Принять всё")}
          </Button>
          <Button variant="ghost" onClick={() => choose("necessary")}>
            {t("Только необходимые")}
          </Button>
        </div>
      </div>
    </div>
  );
}
