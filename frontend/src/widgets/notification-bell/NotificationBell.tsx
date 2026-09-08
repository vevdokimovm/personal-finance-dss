import * as Popover from "@radix-ui/react-popover";
import { useState } from "react";
import { useNavigate } from "@tanstack/react-router";
import {
  useUnreadCount,
  useNotificationsFeed,
  useMarkRead,
  useMarkAllRead,
} from "@entities/notifications";
import type { NotificationOut } from "@entities/notifications";
import { Button, ListSkeleton, StatePanel } from "@shared/ui";
import { t } from "@shared/lib/i18n/t";
import { isConsentRequired } from "@shared/lib/api/extractErrorMessage";
import { useProfile } from "@entities/profile";
import "./NotificationBell.css";
import { toastMutationError } from "@entities/auth";

/**
 * Колокольчик уведомлений в топбаре (ROADMAP §8.2 «ГЛАВНОЕ», первая из API-only фич).
 *
 * Бэкенд ленты существовал с P2.3 и на фронте не был представлен ни строкой: лента,
 * счётчик непрочитанного и отметка о прочтении жили только в API. Тот же класс, что H1 —
 * функция есть, пути к ней у пользователя нет.
 *
 * Панель построена на Radix Popover, а не на условном рендере, и это не вкусовщина:
 * своими силами пришлось бы писать Esc, закрытие по клику вне, возврат фокуса на триггер,
 * `aria-haspopup`/`aria-controls` и обход края экрана — Radix даёт всё это, и проект уже
 * пошёл этим путём для `Modal` (Radix Dialog вместо самописной ловушки фокуса).
 * Обход края здесь не теоретический: колокольчик стоит ЛЕВЕЕ аккаунта и переключателя
 * темы, поэтому панель шириной 360 на узком экране уезжала бы за левую границу.
 *
 * При отозванном согласии виджет исчезает целиком, а не показывает панель согласия.
 * Уведомления попали под гейт в этом же батче (они несут суммы — «Сводка за месяц:
 * доход …, расход …»), то есть 403 здесь штатный ответ. Но колокольчик стоит на КАЖДОМ
 * экране: панель согласия отсюда повторялась бы поверх всего продукта, что хуже
 * молчания. Путь к согласию есть и достижим кликом с v8.31.0 — «Профиль» в каркасе.
 */
export function NotificationBell() {
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  // Авторизация определяется тем же способом, что в навигационном каркасе и топбаре:
  // отдельным запросом профиля, а не угадыванием статуса брошенной ошибки. Клиент
  // статус на ошибку не кладёт — попытка ловить 401 по нему молча не работала.
  const profile = useProfile();
  const unread = useUnreadCount();
  // Лента тянется только когда панель открыта: закрытому бейджу хватает счётчика.
  const feed = useNotificationsFeed(open);
  const markRead = useMarkRead();
  const markAllRead = useMarkAllRead();

  if (profile.isLoading || unread.isLoading) {
    // Место резервируется, а не схлопывается: иначе появление виджета сдвигало бы
    // соседние контролы топбара на каждом холодном старте.
    return <span className="fp-bell__placeholder" aria-hidden="true" />;
  }

  // Гость: уведомлений у него нет по определению. Условие дословно то же, что в
  // `AppNav` и `AuthTopbarLink` — включая проверку `error` рядом с `data`, потому что
  // TanStack Query держит последние успешные данные при упавшем рефетче.
  if (!profile.data || profile.error) return null;

  // Согласие не выдано — виджет исчезает: панель согласия в топбаре повторялась бы на
  // каждом экране, что хуже молчания, а путь к согласию есть в «Профиле».
  // Проверка по КОДУ отказа, а не по полноте тела: e2e поймал, что зависимость от
  // необязательных полей оставляла колокольчик видимым при 403.
  if (isConsentRequired(unread.error)) return null;

  // Всё остальное — авария бэкенда или сеть. Там колокольчик ОСТАЁТСЯ: у 403 есть путь
  // решения, у 500 его нет, и молча стирать функцию значило бы оставить пользователя
  // без пути назад ([ST-04]).

  const count = unread.data ?? 0;
  const label = count > 0 ? t("Уведомления, непрочитанных: {n}", { n: count }) : t("Уведомления");

  function openLink(n: NotificationOut) {
    if (!n.is_read) {
      markRead.mutate(n.id, {
        onError: (error) => toastMutationError(error, t("Не получилось отметить уведомление прочитанным.")),
      });
    }
    // `link` есть в контракте и бэкенд его заполняет (`/goals`, `/planning`). Без
    // перехода строка была бы немым кликом, а уведомление «Превышен бюджет» —
    // тупиком, не ведущим к бюджетам ([IA-04], [FB-01]).
    if (n.link) {
      setOpen(false);
      navigate({ to: n.link });
    }
  }

  return (
    <Popover.Root open={open} onOpenChange={setOpen}>
      <Popover.Trigger asChild>
        <Button
          variant="ghost"
          className="fp-bell__trigger"
          aria-label={label}
          /* Смена числа непрочитанных объявляется скринридеру: без этого новое
             уведомление меняло доступное имя кнопки молча, и узнать о нём можно было,
             только вернувшись на неё фокусом ([FB-05]). */
          aria-live="polite"
        >
          <BellIcon />
          {/* Число, а не точка: «сколько именно» — часть смысла, и оно продублировано
              в доступном имени кнопки ([A11Y-07]). */}
          {count > 0 && (
            <span className="fp-bell__badge" aria-hidden="true">
              {count > 99 ? "99+" : count}
            </span>
          )}
        </Button>
      </Popover.Trigger>

      <Popover.Portal>
        <Popover.Content
          className="fp-bell__panel"
          align="end"
          sideOffset={8}
          collisionPadding={8}
          aria-label={t("Уведомления")}
        >
          <div className="fp-bell__head">
            <p className="fp-bell__title">{t("Уведомления")}</p>
            {(feed.data?.unread_count ?? 0) > 0 && (
              <Button
                variant="ghost"
                className="fp-bell__mark-all"
                aria-busy={markAllRead.isPending}
                onClick={() =>
                  markAllRead.mutate(undefined, {
                    onError: (error) =>
                      toastMutationError(error, t("Не получилось отметить уведомления прочитанными.")),
                    // Фокус уводится на триггер ДО того, как кнопка исчезнет: она
                    // рендерится по `unread_count > 0`, и после успеха размонтируется —
                    // сфокусированный узел пропал бы, уронив фокус в <body> (тот же
                    // класс, что чинили комментарием в Button.css).
                    onSuccess: () => setOpen(false),
                  })
                }
              >
                {t("Прочитать все")}
              </Button>
            )}
          </div>

          {feed.isLoading && <ListSkeleton rows={3} />}

          {feed.error && (
            <StatePanel
              headingLevel={3}
              title={t("Не получилось загрузить уведомления")}
              action={
                <Button variant="primary" onClick={() => feed.refetch()}>
                  {t("Повторить")}
                </Button>
              }
            >
              {t("Проверьте соединение — данные не изменились, попробуйте ещё раз.")}
            </StatePanel>
          )}

          {feed.data && feed.data.items.length === 0 && (
            <StatePanel headingLevel={3} title={t("Пока нет уведомлений")}>
              {t("Здесь появятся напоминания о дедлайнах целей и превышении бюджета.")}
            </StatePanel>
          )}

          {feed.data && feed.data.items.length > 0 && (
            <ul className="fp-bell__list" role="list">
              {feed.data.items.map((n: NotificationOut) => (
                <li key={n.id}>
                  <button
                    type="button"
                    className={n.is_read ? "fp-bell__item" : "fp-bell__item fp-bell__item--unread"}
                    onClick={() => openLink(n)}
                  >
                    <span className="fp-bell__item-head">
                      <span className="fp-bell__item-title">{n.title}</span>
                      {/* Нецветовой признак непрочитанного для ЗРЯЧЕГО пользователя:
                          заливка и грань — оба цветовые каналы, и дальтонику не давали
                          ничего ([A11Y-07]). Метка словом решает это без иконографии. */}
                      {!n.is_read && <span className="fp-bell__new">{t("новое")}</span>}
                    </span>
                    <span className="fp-bell__item-body">{n.body}</span>
                    <span className="fp-bell__item-date">{formatWhen(n.created_at)}</span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </Popover.Content>
      </Popover.Portal>
    </Popover.Root>
  );
}

/** Дата уведомления. Лента без времени нечитаема: «Превышен бюджет» — сегодня или в мае? */
function formatWhen(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "";
  return d.toLocaleDateString("ru-RU", { day: "2-digit", month: "2-digit", year: "numeric" });
}

/** Иконка колокольчика. Inline-SVG, а не эмодзи: эмодзи запрещены брифом (§6), рисуются
 * цветным растром поверх монохромного языка, не наследуют `currentColor` и меняют размер
 * от платформы. Тот же приём, что в `shared/ui/Modal.tsx`. */
function BellIcon() {
  return (
    <svg
      className="fp-bell__icon"
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      focusable="false"
    >
      <path d="M18 8a6 6 0 1 0-12 0c0 7-3 9-3 9h18s-3-2-3-9" />
      <path d="M13.7 21a2 2 0 0 1-3.4 0" />
    </svg>
  );
}
