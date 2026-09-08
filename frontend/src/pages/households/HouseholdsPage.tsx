import { useRef, useState } from "react";
import {
  useHouseholds,
  useHouseholdMembers,
  useHouseholdInvites,
  useCreateHousehold,
  useCreateInvite,
  useRevokeInvite,
  useRemoveMember,
  useLeaveHousehold,
  useDisbandHousehold,
} from "@entities/households";
import type { HouseholdResponse } from "@entities/households";
import { useProfile } from "@entities/profile";
import { Button, CopyLinkField, ListSkeleton, StatePanel, Modal, toast } from "@shared/ui";
import { formatDate } from "@shared/lib/date/formatDate";
import { t } from "@shared/lib/i18n/t";
import "@shared/ui/entityForm.css";
import "./HouseholdsPage.css";
import { toastMutationError } from "@entities/auth";

/**
 * Семейный доступ — households (P3.7, ROADMAP §8.2 «ГЛАВНОЕ», гипотеза H16).
 *
 * Бэкенд целиком существовал: двенадцать эндпоинтов со схемами — создание, участники,
 * приглашения, выход, роспуск. Фронта не было НИ СТРОКИ, то есть самая большая из
 * оставшихся дыр «функция есть, пути к ней нет».
 *
 * Названия ролей переведены здесь, а не показываются кодом из API: `owner`/`member`/
 * `viewer` — служебные значения контракта, пользователю они ничего не говорят ([CMP-03]).
 *
 * Устройство экрана повторяет остальные пять CRUD-экранов продукта ([CMP-01]): заголовок
 * и primary-кнопка в шапке, форма — в модалке, список — ниже. Первая редакция держала
 * форму создания раскрытой поверх списка, и единственный primary-CTA страницы уходил
 * инструменту, который нужен одну минуту за всё время жизни аккаунта (design-critic).
 */

/** Русские названия ролей. Отдельной картой, а не в JSX: одно понятие — одно слово,
 * и роль появляется в трёх местах (моя роль, роль участника, роль приглашения). */
const ROLE_LABEL: Record<string, string> = {
  owner: "Владелец",
  member: "Участник",
  viewer: "Наблюдатель",
};

const NAME_MAX = 255;

function roleLabel(role: string): string {
  return ROLE_LABEL[role] ?? role;
}

export function HouseholdsPage() {
  const households = useHouseholds();
  const create = useCreateHousehold();
  const [formOpen, setFormOpen] = useState(false);
  const [name, setName] = useState("");
  const [nameError, setNameError] = useState<string | null>(null);
  const headingRef = useRef<HTMLHeadingElement>(null);
  const createTriggerRef = useRef<HTMLButtonElement | null>(null);

  function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    const trimmed = name.trim();
    // Пустое имя не отправляем: бэкенд отверг бы его 422 (`min_length=1`). Но и молча
    // ничего не делать нельзя — немой клик читается как «экран сломался» ([FB-01]).
    if (trimmed === "") {
      setNameError(t("Введите название — по нему вы узнаете эту семью в списке."));
      return;
    }
    if (create.isPending) return;
    setNameError(null);
    create.mutate(trimmed, {
      onSuccess: () => {
        setName("");
        closeForm();
        toast.success(t("Семейный доступ создан"));
      },
      onError: (error) => toastMutationError(error, t("Не получилось создать. Попробуйте ещё раз.")),
    });
  }

  const items = households.data ?? [];

  const createButton = (
    <Button ref={createTriggerRef} variant="primary" onClick={() => setFormOpen(true)}>
      {t("Создать семейный доступ")}
    </Button>
  );

  /* 🔴 Одна точка закрытия формы, а не две (v9.3.0, нашёл тест). Кнопка «Отмена»
     звала `setFormOpen(false)` напрямую, минуя сброс ошибки в `onOpenChange`:
     сообщение «Введите название» переживало закрытие и встречало человека при
     следующем открытии — он решал, что предыдущая попытка что-то сломала.
     Два пути закрытия одного окна расходятся при первой же правке одного из них. */
  function closeForm() {
    setFormOpen(false);
    setNameError(null);
  }

  const formModal = (
    <Modal
      open={formOpen}
      onOpenChange={(open) => {
        if (!open) closeForm();
      }}
      title={t("Новый семейный доступ")}
      description={t("Общий план для нескольких человек. Участников добавите потом.")}
      returnFocusTo={() => createTriggerRef.current}
    >
      <form className="fp-entity-form" onSubmit={handleCreate} noValidate>
        <div className="fp-entity-form__field">
          <label htmlFor="fp-household-name">{t("Название")}</label>
          <input
            id="fp-household-name"
            type="text"
            maxLength={NAME_MAX}
            value={name}
            placeholder={t("например: Семья Петровых")}
            aria-invalid={nameError ? true : undefined}
            aria-describedby={nameError ? "fp-household-name-error" : "fp-household-name-hint"}
            onChange={(e) => {
              setName(e.target.value);
              if (nameError) setNameError(null);
            }}
          />
          {/* Ограничение показано ДО ввода, а не обрезкой на 256-м символе ([FRM-03]). */}
          <p id="fp-household-name-hint" className="fp-entity-form__hint">
            {t("До {n} символов", { n: NAME_MAX })}
          </p>
          {nameError && (
            <p id="fp-household-name-error" className="fp-entity-form__error" role="alert">
              {nameError}
            </p>
          )}
        </div>
        <div className="fp-entity-form__actions">
          <Button variant="ghost" type="button" onClick={closeForm}>
            {t("Отмена")}
          </Button>
          <Button
            type="submit"
            variant="primary"
            aria-busy={create.isPending}
            aria-disabled={create.isPending}
          >
            {create.isPending ? t("Создаём…") : t("Создать")}
          </Button>
        </div>
      </form>
    </Modal>
  );

  return (
    <main className="fp-households">
      <div className="fp-households__head">
        <h1 ref={headingRef} tabIndex={-1}>
          {t("Семейный доступ")}
        </h1>
        {households.data && items.length > 0 && createButton}
      </div>
      <p className="fp-households__lede">
        {t(
          "Общий финансовый портрет для нескольких человек: план строится по данным " +
            "всей семьи. Владелец приглашает участников ссылкой и может отозвать доступ.",
        )}
      </p>

      {households.isLoading && <ListSkeleton rows={2} />}

      {households.error && (
        <StatePanel
          role="alert"
          title={t("Не получилось загрузить семейный доступ")}
          action={
            <Button variant="primary" onClick={() => households.refetch()}>
              {t("Повторить")}
            </Button>
          }
        >
          {t("Проверьте соединение — данные не изменились.")}
        </StatePanel>
      )}

      {households.data && items.length === 0 && (
        <StatePanel title={t("Пока нет общего доступа")} action={createButton}>
          {t(
            "Создайте семейный доступ, чтобы вести финансы вместе: доходы, обязательства " +
              "и цели будут учитываться в одном плане.",
          )}
        </StatePanel>
      )}

      {items.map((household) => (
        <HouseholdCard
          key={household.id}
          household={household}
          // Карточка исчезает вместе с кнопкой, на которой стоял фокус, — без переноса
          // фокус проваливается в body и человек теряет место на странице ([A11Y-05]).
          onGone={() => headingRef.current?.focus()}
        />
      ))}

      {formModal}
    </main>
  );
}

/** Что подтверждаем. Одна модалка на карточку вместо трёх-четырёх: разные действия,
 * но одинаковый разговор — «вот что исчезнет, вот кнопка, вот отмена» ([CMP-01]). */
type Confirm = {
  title: string;
  description: string;
  body: string;
  confirmLabel: string;
  run: () => void;
  trigger: HTMLButtonElement | null;
};

function HouseholdCard({
  household,
  onGone,
}: {
  household: HouseholdResponse;
  onGone: () => void;
}) {
  const isOwner = household.role === "owner";
  const profile = useProfile();
  const members = useHouseholdMembers(household.id);
  const invites = useHouseholdInvites(household.id, isOwner);
  const invite = useCreateInvite();
  const revoke = useRevokeInvite();
  const removeMember = useRemoveMember();
  const leave = useLeaveHousehold();
  const disband = useDisbandHousehold();

  // Ссылки копятся списком, а не заменяют друг друга: сервер отдаёт каждую РОВНО один
  // раз, и второй клик по «Пригласить» затирал предыдущую ссылку насовсем, хотя
  // приглашение на сервере уже создано и висит (design-critic).
  const [inviteUrls, setInviteUrls] = useState<string[]>([]);
  const [inviteRole, setInviteRole] = useState<"member" | "viewer">("member");
  const [confirm, setConfirm] = useState<Confirm | null>(null);
  const headingRef = useRef<HTMLHeadingElement>(null);
  const nameId = `fp-household-${household.id}-name`;

  function handleInvite() {
    if (invite.isPending) return;
    invite.mutate(
      { householdId: household.id, role: inviteRole },
      {
        onSuccess: (created: { invite_url?: string | null }) => {
          if (created.invite_url) {
            setInviteUrls((prev) => [...prev, created.invite_url as string]);
          }
          toast.success(t("Ссылка приглашения готова"));
        },
        onError: (error) => toastMutationError(error, t("Не получилось создать приглашение.")),
      },
    );
  }

  return (
    <section className="fp-household" aria-labelledby={nameId}>
      <div className="fp-household__head">
        <h2 id={nameId} ref={headingRef} tabIndex={-1}>
          {household.name}
        </h2>
        <span
          className={
            isOwner ? "fp-household__role fp-household__role--owner" : "fp-household__role"
          }
        >
          {/* Роль словом, а не только цветом или позицией ([A11Y-07], [CMP-03]). */}
          <span className="sr-only">{t("Моя роль: ")}</span>
          {roleLabel(household.role)}
        </span>
      </div>
      <p className="fp-household__meta">
        {t("Участников: {n} · создан {date}", {
          n: household.member_count,
          date: formatDate(household.created_at),
        })}
      </p>

      <h3 className="fp-household__section-title">{t("Участники")}</h3>
      {members.isLoading && <ListSkeleton rows={2} />}
      {members.error && (
        // Молчаливая пустота здесь обманывает: счётчик выше говорит, что участники
        // есть, а список пуст ([ST-01]).
        <StatePanel
          role="alert"
          headingLevel={3}
          title={t("Участники не загрузились")}
          action={
            <Button variant="ghost" onClick={() => members.refetch()}>
              {t("Повторить")}
            </Button>
          }
        >
          {t("Список участников временно недоступен.")}
        </StatePanel>
      )}
      {members.data && (
        <ul className="fp-household__members" role="list">
          {members.data.map((member) => {
            const isMe = profile.data?.id === member.user_id;
            const who = member.email ?? member.user_id;
            return (
              <li key={member.user_id} className="fp-household__member">
                <span className="fp-household__email">
                  {who}
                  {/* Владелец видит четыре адреса и не должен вспоминать собственный,
                      чтобы не промахнуться кнопкой по соседу (design-critic). */}
                  {isMe && <span className="fp-household__me">{t(" — это вы")}</span>}
                </span>
                <span className="fp-household__member-role">{roleLabel(member.role)}</span>
                {isOwner && member.role !== "owner" && (
                  <Button
                    variant="danger"
                    aria-busy={removeMember.isPending}
                    aria-disabled={removeMember.isPending}
                    aria-label={t("Убрать участника {who}", { who })}
                    onClick={(e) =>
                      setConfirm({
                        title: t("Убрать участника?"),
                        description: t("Вернуть доступ можно будет только новым приглашением."),
                        body: t("{who} перестанет видеть общий план «{name}».", {
                          who,
                          name: household.name,
                        }),
                        confirmLabel: t("Убрать"),
                        trigger: e.currentTarget,
                        run: () =>
                          removeMember.mutate(
                            { householdId: household.id, userId: member.user_id },
                            {
                              onSuccess: () => {
                                setConfirm(null);
                                toast.success(t("Участник убран"));
                                // Строка исчезает вместе с кнопкой — возвращаем фокус
                                // на заголовок карточки, а не в пустоту.
                                headingRef.current?.focus();
                              },
                              onError: (error) => toastMutationError(error, t("Не получилось убрать участника.")),
                            },
                          ),
                      })
                    }
                  >
                    {t("Убрать")}
                  </Button>
                )}
              </li>
            );
          })}
        </ul>
      )}

      {isOwner && (
        <>
          <h3 className="fp-household__section-title">{t("Приглашения")}</h3>

          <div className="fp-household__actions">
            <div className="fp-entity-form__field fp-household__invite-role">
              <label htmlFor={`fp-invite-role-${household.id}`}>{t("Права")}</label>
              <select
                id={`fp-invite-role-${household.id}`}
                value={inviteRole}
                onChange={(e) => setInviteRole(e.target.value as "member" | "viewer")}
              >
                {/* Бэкенд принимает обе роли, а первая редакция экрана всегда слала
                    `member` — наблюдателя (доступ только на чтение) выдать было нельзя.
                    Ровно та дыра, которую этот экран и закрывает. */}
                <option value="member">{t("Участник — вносит данные")}</option>
                <option value="viewer">{t("Наблюдатель — только смотрит")}</option>
              </select>
            </div>
            <Button
              variant="ghost"
              aria-busy={invite.isPending}
              aria-disabled={invite.isPending}
              onClick={handleInvite}
            >
              {invite.isPending ? t("Создаём ссылку…") : t("Пригласить участника")}
            </Button>
          </div>

          {inviteUrls.length > 0 && (
            <div className="fp-household__invite" role="status">
              <p className="fp-household__invite-title">
                {t("Ссылка приглашения — показывается только сейчас")}
              </p>
              {inviteUrls.map((url) => (
                <CopyLinkField
                  key={url}
                  label={t("Ссылка приглашения в семейный доступ")}
                  url={url}
                  variant="primary"
                />
              ))}
              <p className="fp-household__invite-hint">
                {t(
                  "Отправьте её тому, кого приглашаете. Повторно сервер эту ссылку " +
                    "не покажет — уйдёте с экрана, и её придётся создавать заново.",
                )}
              </p>
            </div>
          )}

          {invites.error && (
            <StatePanel
              role="alert"
              headingLevel={3}
              title={t("Приглашения не загрузились")}
              action={
                <Button variant="ghost" onClick={() => invites.refetch()}>
                  {t("Повторить")}
                </Button>
              }
            >
              {t("Список приглашений временно недоступен.")}
            </StatePanel>
          )}

          {invites.data && invites.data.length === 0 && (
            <p className="fp-household__empty">{t("Открытых приглашений нет.")}</p>
          )}

          {invites.data && invites.data.length > 0 && (
            <ul className="fp-household__invites" role="list">
              {invites.data.map((item) => {
                const who = item.email ?? t("по ссылке");
                return (
                  <li key={item.id} className="fp-household__invite-row">
                    <span className="fp-household__email">{who}</span>
                    <span className="fp-household__member-role">{roleLabel(item.role)}</span>
                    <span className="fp-household__invite-status">
                      {t("ждёт ответа · до {date}", { date: formatDate(item.expires_at) })}
                    </span>
                    <Button
                      variant="danger"
                      aria-busy={revoke.isPending}
                      aria-disabled={revoke.isPending}
                      aria-label={t("Отозвать приглашение для {who}", { who })}
                      onClick={(e) =>
                        setConfirm({
                          title: t("Отозвать приглашение?"),
                          description: t("Отправленная ссылка перестанет работать."),
                          body: t("Приглашение для «{who}» больше нельзя будет принять.", {
                            who,
                          }),
                          confirmLabel: t("Отозвать"),
                          trigger: e.currentTarget,
                          run: () =>
                            revoke.mutate(
                              { householdId: household.id, inviteId: item.id },
                              {
                                onSuccess: () => {
                                  setConfirm(null);
                                  toast.success(t("Приглашение отозвано"));
                                  headingRef.current?.focus();
                                },
                                onError: (error) =>
                                  toastMutationError(error, t("Не получилось отозвать приглашение.")),
                              },
                            ),
                        })
                      }
                    >
                      {t("Отозвать")}
                    </Button>
                  </li>
                );
              })}
            </ul>
          )}
        </>
      )}

      <div className="fp-household__actions fp-household__actions--footer">
        {/* Владельцу «покинуть» не предлагается: бэкенд отвечает 400 — владелец либо
            распускает, либо остаётся. Кнопка, которая гарантированно откажет, это тупик. */}
        {isOwner ? (
          <Button
            variant="danger"
            aria-haspopup="dialog"
            onClick={(e) =>
              setConfirm({
                title: t("Распустить семейный доступ?"),
                description: t("Действие необратимо: восстановить его будет нельзя."),
                body: t(
                  "«{name}» исчезнет у всех участников, их доступ к общему плану прекратится.",
                  {
                    name: household.name,
                  },
                ),
                confirmLabel: t("Распустить навсегда"),
                trigger: e.currentTarget,
                run: () =>
                  disband.mutate(household.id, {
                    onSuccess: () => {
                      setConfirm(null);
                      toast.success(t("Семейный доступ распущен"));
                      onGone();
                    },
                    onError: (error) => toastMutationError(error, t("Не получилось распустить.")),
                  }),
              })
            }
          >
            {t("Распустить")}
          </Button>
        ) : (
          <Button
            variant="danger"
            aria-haspopup="dialog"
            onClick={(e) =>
              setConfirm({
                title: t("Покинуть семейный доступ?"),
                description: t("Вернуться можно будет только по новому приглашению."),
                body: t("Вы перестанете видеть общий план «{name}».", { name: household.name }),
                confirmLabel: t("Покинуть"),
                trigger: e.currentTarget,
                run: () =>
                  leave.mutate(household.id, {
                    onSuccess: () => {
                      setConfirm(null);
                      toast.success(t("Вы покинули семейный доступ"));
                      onGone();
                    },
                    onError: (error) => toastMutationError(error, t("Не получилось выйти.")),
                  }),
              })
            }
          >
            {t("Покинуть")}
          </Button>
        )}
      </div>

      <Modal
        open={confirm !== null}
        onOpenChange={(open) => !open && setConfirm(null)}
        title={confirm?.title ?? ""}
        description={confirm?.description ?? ""}
        // Триггер мог исчезнуть вместе со строкой — тогда возвращать фокус на него
        // нельзя, фокус уходит в body. `isConnected` отвечает именно на этот вопрос.
        returnFocusTo={() =>
          confirm?.trigger?.isConnected ? (confirm.trigger as HTMLElement) : null
        }
      >
        <p className="fp-household__confirm-target">{confirm?.body}</p>
        <div className="fp-household__confirm">
          <Button variant="ghost" onClick={() => setConfirm(null)}>
            {t("Отмена")}
          </Button>
          <Button
            variant="danger"
            aria-busy={
              disband.isPending || leave.isPending || removeMember.isPending || revoke.isPending
            }
            onClick={() => confirm?.run()}
          >
            {confirm?.confirmLabel}
          </Button>
        </div>
      </Modal>
    </section>
  );
}
