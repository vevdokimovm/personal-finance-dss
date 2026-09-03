import { useEffect, useRef, useState } from "react";
import { Link, useSearch } from "@tanstack/react-router";
import { useAcceptInvite } from "@entities/households";
import { useProfile } from "@entities/profile";
import { Button, ListSkeleton, StatePanel } from "@shared/ui";
import { t } from "@shared/lib/i18n/t";
import "./HouseholdsPage.css";

/**
 * Приём приглашения по ссылке — `/join?token=...`.
 *
 * 🔴 Этого экрана НЕ СУЩЕСТВОВАЛО, хотя бэкенд строил ссылку на него с самого начала:
 * `routes_households.py::_invite_url` собирает `base_url + "/join?token=..."`, и владелец
 * копировал этот адрес приглашаемому. Роута в SPA не было — приглашение в семейный
 * доступ вело в никуда. Второй случай класса H12 (первый — `link="/budgets"` в
 * уведомлениях, v8.34.0); гейт `tests/test_spa_navigation_reachability.py` расширен,
 * чтобы ловить ЛЮБУЮ собранную на сервере ссылку, а не только уведомления.
 *
 * Гостю показываем не отказ, а путь: приглашение принимается от имени аккаунта, значит
 * сначала вход. Токен при этом не теряется по-настоящему, а не на словах — он уезжает
 * в `?redirect=` и возвращает человека сюда же после входа или регистрации
 * (`safeRedirect`, `LoginPage`/`RegisterPage`). Первая редакция этого экрана обещала
 * сохранность токена текстом, а код терял адрес на переходе — обещание без механизма.
 */
export function JoinPage() {
  const search = useSearch({ strict: false }) as { token?: string };
  const token = search.token;
  const profile = useProfile();
  const accept = useAcceptInvite();
  const resultRef = useRef<HTMLDivElement>(null);
  const [done, setDone] = useState(false);
  const [failed, setFailed] = useState(false);

  // Куда вернуться после входа. Собирается здесь, а не в ссылке напрямую, чтобы
  // токен кодировался маршрутизатором, а не руками.
  const backHere = token ? `/join?token=${encodeURIComponent(token)}` : "/join";

  const isGuest = !profile.isLoading && (!profile.data || Boolean(profile.error));

  // Принимаем автоматически, как только известно, что пользователь вошёл: он уже
  // сделал осознанное действие — открыл присланную ссылку, и просить второй раз
  // «подтвердите» значит добавить шаг без смысла.
  useEffect(() => {
    if (!token || !profile.data || profile.error || accept.isPending || done || failed) return;
    accept.mutate(token, {
      onSuccess: () => setDone(true),
      onError: () => setFailed(true),
    });
    // `accept` намеренно не в зависимостях: объект мутации новый на каждый рендер,
    // и включение его дало бы бесконечный цикл запросов.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, profile.data, profile.error]);

  // Фокус переносим на панель результата, а не на неизменный h1: заголовок страницы
  // одинаков при успехе и при отказе и сам по себе ничего не сообщает (a11y-auditor).
  useEffect(() => {
    if (done || failed) resultRef.current?.focus();
  }, [done, failed]);

  return (
    <main className="fp-households fp-join">
      <h1>{t("Приглашение в семейный доступ")}</h1>

      {!token && (
        <StatePanel role="alert" title={t("Ссылка неполная")}>
          {t(
            "В адресе нет кода приглашения. Попросите отправителя прислать ссылку целиком — " +
              "она заканчивается на «?token=…».",
          )}
        </StatePanel>
      )}

      {token && profile.isLoading && (
        <div role="status" aria-label={t("Проверяем вход")}>
          <ListSkeleton rows={1} />
        </div>
      )}

      {token && isGuest && (
        <StatePanel
          title={t("Сначала войдите")}
          action={
            <div className="fp-join__actions">
              <Button variant="primary" asChild>
                <Link to="/login" search={{ redirect: backHere }}>
                  {t("Войти")}
                </Link>
              </Button>
              <Button variant="ghost" asChild>
                <Link to="/register" search={{ redirect: backHere }}>
                  {t("Зарегистрироваться")}
                </Link>
              </Button>
            </div>
          }
        >
          {t(
            "Приглашение принимается от имени аккаунта. Войдите или зарегистрируйтесь — " +
              "приглашение сохранится, и вы вернётесь сюда же.",
          )}
        </StatePanel>
      )}

      {token && profile.data && !profile.error && accept.isPending && (
        <div role="status" aria-label={t("Принимаем приглашение")}>
          <ListSkeleton rows={1} />
        </div>
      )}

      {done && (
        <div ref={resultRef} tabIndex={-1} className="fp-join__result">
          <StatePanel
            role="status"
            title={t("Готово — вы в семейном доступе")}
            action={
              <Button variant="primary" asChild>
                <Link to="/household">{t("Открыть семейный доступ")}</Link>
              </Button>
            }
          >
            {t("Теперь общий план учитывает и ваши данные.")}
          </StatePanel>
        </div>
      )}

      {failed && (
        <div ref={resultRef} tabIndex={-1} className="fp-join__result">
          <StatePanel
            role="alert"
            title={t("Приглашение не сработало")}
            action={
              <Button variant="primary" asChild>
                <Link to="/household">{t("К семейному доступу")}</Link>
              </Button>
            }
          >
            {/* Причин у отказа три, и пользователю важна не та, что в коде ответа, а что
                делать дальше — поэтому перечислены человеческим языком ([ST-04]). */}
            {t(
              "Ссылка могла устареть, быть отозванной или уже использованной. " +
                "Попросите отправителя создать новую.",
            )}
          </StatePanel>
        </div>
      )}
    </main>
  );
}
