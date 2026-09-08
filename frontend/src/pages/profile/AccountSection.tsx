import { useRef, useState } from "react";
import { useChangePassword, useDeleteAccount } from "@entities/auth";
import { Button, Modal } from "@shared/ui";
import { extractErrorMessage } from "@shared/lib/api/extractErrorMessage";
import { SessionExpiredBanner, isSessionExpired } from "@entities/auth";
import { t } from "@shared/lib/i18n/t";
import "./AccountSection.css";

/**
 * Управление аккаунтом: смена пароля и удаление (v8.52.0).
 *
 * 🔴 Найдено аудитом independent-expert 05.09.2026: оба эндпоинта живут на бэкенде
 * (`POST /auth/change-password`, `DELETE /auth/me`) и **не имели UI вообще**.
 *
 * Удаление — не удобство, а путь исполнения права по 152-ФЗ: экран согласий рядом
 * говорит «согласие на обработку ПДн нельзя отозвать без удаления аккаунта», а юрреестр
 * помечает L9 выполненным по факту существования функции `crud.delete_user`. Право было
 * реализовано и недостижимо — буквальный повтор SEV1 `CONSENT-GATE-NO-UI`, когда гейт
 * согласия работал 26 дней без единого способа его пройти.
 */

const MIN_PASSWORD_LENGTH = 8;

export function AccountSection() {
  const changePassword = useChangePassword();
  const deleteAccount = useDeleteAccount();

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [changed, setChanged] = useState(false);
  const [confirmOpen, setConfirmOpen] = useState(false);
  /* Фокус возвращается на кнопку, открывшую диалог: Radix не знает триггера, когда
     модалка управляется пропом `open`, и увёл бы фокус в `<body>` (WCAG 2.4.3). */
  const deleteButtonRef = useRef<HTMLButtonElement>(null);

  const canSubmit =
    currentPassword.length > 0 &&
    newPassword.length >= MIN_PASSWORD_LENGTH &&
    !changePassword.isPending;

  return (
    <section className="fp-account" aria-labelledby="fp-account-title">
      <h2 id="fp-account-title">{t("Аккаунт и безопасность")}</h2>

      <form
        className="fp-account__form"
        onSubmit={(event) => {
          event.preventDefault();
          if (!canSubmit) return;
          changePassword.mutate(
            { current_password: currentPassword, new_password: newPassword },
            {
              onSuccess: () => {
                setChanged(true);
                setCurrentPassword("");
                setNewPassword("");
              },
            },
          );
        }}
      >
        <h3 className="fp-account__subtitle">{t("Смена пароля")}</h3>
        {/* 🔴 Предупреждение обязательно и до кнопки: сервер гасит ВСЕ сессии, включая
            текущую (банковская планка, а не поведение Google/GitHub). Человек, не
            предупреждённый заранее, прочитает выход как сбой. */}
        <p className="fp-account__hint">
          {t(
            "После смены пароля все сессии завершатся, включая эту — придётся войти " +
              "заново на всех устройствах.",
          )}
        </p>

        <label className="fp-account__label" htmlFor="fp-current-password">
          {t("Текущий пароль")}
        </label>
        <input
          id="fp-current-password"
          className="fp-account__input"
          type="password"
          autoComplete="current-password"
          value={currentPassword}
          onChange={(event) => setCurrentPassword(event.target.value)}
        />

        <label className="fp-account__label" htmlFor="fp-new-password">
          {t("Новый пароль")}
        </label>
        <input
          id="fp-new-password"
          className="fp-account__input"
          type="password"
          autoComplete="new-password"
          minLength={MIN_PASSWORD_LENGTH}
          value={newPassword}
          onChange={(event) => setNewPassword(event.target.value)}
          aria-describedby="fp-new-password-hint"
        />
        <p id="fp-new-password-hint" className="fp-account__hint">
          {t("Не короче {n} символов.", { n: MIN_PASSWORD_LENGTH })}
        </p>

        {changePassword.isError &&
          (isSessionExpired(changePassword.error) ? (
            /* 🔴 401 здесь — истёкшая сессия, и «попробуйте ещё раз» отправляет по кругу.
               Это право L9 по 152-ФЗ: тупик именно на смене пароля и удалении аккаунта
               дороже, чем на обычной форме. */
            <SessionExpiredBanner />
          ) : (
            <p className="fp-account__error" role="alert">
              {extractErrorMessage(
                changePassword.error,
                t("Не удалось сменить пароль. Попробуйте ещё раз."),
              )}
            </p>
          ))}
        {changed && !changePassword.isError && (
          <p className="fp-account__ok" role="status">
            {t("Пароль обновлён. Войдите заново с новым паролем.")}
          </p>
        )}

        {/* 🔴 `aria-disabled`, а не нативный `disabled`: нативный выводит элемент
            из дерева доступности В МОМЕНТ клика, и фокус клавиатуры проваливается
            в `<body>` раньше, чем завершится запрос. Паттерн документирован
            в `Button.css` и применён в `ConsentsSection` — эта секция его
            не унаследовала (a11y-auditor). Клик игнорируется обработчиком,
            а не браузером. */}
        <Button
          type="submit"
          variant="primary"
          aria-disabled={!canSubmit}
          aria-busy={changePassword.isPending}
        >
          {changePassword.isPending ? t("Меняем…") : t("Сменить пароль")}
        </Button>
      </form>

      <div className="fp-account__danger">
        <h3 className="fp-account__subtitle">{t("Удаление аккаунта")}</h3>
        <p className="fp-account__hint">
          {t(
            "Удаление стирает всё: операции, кредиты, цели, планы и сам аккаунт. " +
              "Это единственный способ отозвать согласие на обработку персональных " +
              "данных — оно основание обработки, пока аккаунт существует.",
          )}
        </p>

        {deleteAccount.isError &&
          (isSessionExpired(deleteAccount.error) ? (
            /* 🔴 401 здесь — истёкшая сессия, и «попробуйте ещё раз» отправляет по кругу.
               Это право L9 по 152-ФЗ: тупик именно на смене пароля и удалении аккаунта
               дороже, чем на обычной форме. */
            <SessionExpiredBanner />
          ) : (
            <p className="fp-account__error" role="alert">
              {extractErrorMessage(
                deleteAccount.error,
                t("Не удалось удалить аккаунт. Попробуйте ещё раз."),
              )}
            </p>
          ))}

        {/* 🔴 Кнопка НЕ удаляет: она открывает подтверждение. Необратимое действие
            в один клик — то же, чем оказался `/demo/load` в v8.46.0, только здесь
            стирается всё и навсегда. */}
        <Button ref={deleteButtonRef} variant="danger" onClick={() => setConfirmOpen(true)}>
          {t("Удалить аккаунт")}
        </Button>
      </div>

      <Modal
        open={confirmOpen}
        onOpenChange={setConfirmOpen}
        title={t("Удалить аккаунт навсегда?")}
        description={t("Подтверждение необратимого удаления аккаунта и всех данных.")}
        returnFocusTo={() => deleteButtonRef.current}
      >
        <p>
          {t(
            "Будут безвозвратно удалены все ваши данные: операции, кредиты, цели, " +
              "ликвидные активы, бюджеты, сохранённые планы и сам аккаунт. " +
              "Отменить это нельзя, восстановить — тоже.",
          )}
        </p>
        <div className="fp-account__actions">
          <Button variant="ghost" onClick={() => setConfirmOpen(false)}>
            {t("Отмена")}
          </Button>
          {/* Внутри focus-trap модалки потеря фокуса особенно дорога: он логически
              покидает диалог, пока запрос ещё идёт, — и это на необратимом действии,
              которое человек совершает в стрессе. */}
          <Button
            variant="danger"
            aria-disabled={deleteAccount.isPending}
            aria-busy={deleteAccount.isPending}
            onClick={() => {
              if (deleteAccount.isPending) return;
              deleteAccount.mutate(undefined, { onSuccess: () => setConfirmOpen(false) });
            }}
          >
            {deleteAccount.isPending ? t("Удаляем…") : t("Удалить навсегда")}
          </Button>
        </div>
      </Modal>
    </section>
  );
}
