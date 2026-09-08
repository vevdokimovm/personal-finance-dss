import { useRef } from "react";
import { useConsents, useGrantConsent, useWithdrawConsent } from "@entities/consents";
import type { ConsentType } from "@entities/consents";
import { useLegalDocuments } from "@entities/legal";
import { Button, StatePanel, toast } from "@shared/ui";
import { SessionExpiredPanel, isSessionExpired, toastMutationError } from "@entities/auth";
import { formatDate } from "@shared/lib/date/formatDate";
import { t } from "@shared/lib/i18n/t";
import "./ProfilePage.css";

/**
 * Экран выдачи и отзыва согласий — юр-требование L3 (v8.41.0).
 *
 * 🔴 Первая редакция знала ровно ОДНО согласие — `financial_data` — и была вшита в него
 * разметкой: заголовок, ссылка на документ, обработчики. Согласий три
 * (`app/core/legal.py::CONSENT_TYPES`), и остальные два человек не видел вовсе: отозвать
 * маркетинговое было невозможно, хотя 152-ФЗ даёт на это право. Требование L3 говорит
 * именно про экран согласий, а не про одно из них.
 *
 * Теперь список строится из ответа `/consents` — он несёт ВСЕ известные типы, включая
 * невыданные. Названия и адреса документов берутся из `/legal/documents`: ключи реестра
 * совпадают с типами согласий, и рукописная копия разошлась бы с бэкендом молча.
 *
 * `withdrawable` решает, показывать ли кнопку отзыва. Согласие-основание (обработка ПДн)
 * отозвать нельзя иначе как удалением аккаунта — кнопка там гарантированно дала бы 409,
 * то есть тупик ([IA-04]); вместо неё объяснение.
 */

/** Человеческие названия. Ключи реестра документов — служебные, а «Согласие на обработку
 * персональных данных» в заголовке строки читается тяжелее, чем «Персональные данные». */
const CONSENT_LABEL: Record<string, string> = {
  personal_data: "Персональные данные",
  financial_data: "Финансовые данные",
  marketing: "Рекламная рассылка",
};

function label(type: string): string {
  return CONSENT_LABEL[type] ?? type;
}

export function ConsentsSection() {
  const query = useConsents();
  const legal = useLegalDocuments();
  const grant = useGrantConsent();
  const withdraw = useWithdrawConsent();
  // Фокус после смены статуса: кнопка размонтируется вместе с блоком статуса — без
  // явного переноса фокус проваливается в <body> (a11y-auditor).
  const statusRefs = useRef<Record<string, HTMLSpanElement | null>>({});

  /* 🔴 Ошибка не прячет секцию молча. Прежняя редакция сворачивала блок при ЛЮБОЙ
     ошибке одной строкой `return null` — а это единственный путь отзыва согласия
     в интерфейсе, и `routes_consents.py` прямо называет его недоступность нарушением
     152-ФЗ, а не дефектом интерфейса. Человек не мог отличить «функции нет»
     от «сеть моргнула»: экран просто оказывался без блока.

     Загрузка по-прежнему тиха: сообщать не о чем, пока ответ не пришёл. */
  if (query.isLoading) return null;

  if (query.isError || !query.data) {
    if (isSessionExpired(query.error)) {
      return (
        <section className="fp-profile-section">
          <h2>{t("Согласия")}</h2>
          <SessionExpiredPanel redirectTo="/profile" />
        </section>
      );
    }
    return (
      <section className="fp-profile-section">
        <h2>{t("Согласия")}</h2>
        <StatePanel
          title={t("Не получилось загрузить согласия")}
          role="alert"
          action={
            <Button variant="primary" onClick={() => void query.refetch?.()}>
              {t("Повторить")}
            </Button>
          }
        >
          {t(
            "Управление согласиями временно недоступно. Ваши согласия при этом не изменились — "
            + "повторите попытку или напишите в поддержку.",
          )}
        </StatePanel>
      </section>
    );
  }

  function handleGrant(type: ConsentType) {
    if (grant.isPending) return;
    grant.mutate(type, {
      onSuccess: () => statusRefs.current[type]?.focus(),
      onError: (error) => toastMutationError(error, t("Не получилось сохранить согласие. Попробуйте ещё раз.")),
    });
  }

  function handleWithdraw(type: ConsentType) {
    if (withdraw.isPending) return;
    withdraw.mutate(type, {
      onSuccess: () => {
        statusRefs.current[type]?.focus();
        // Тот же паттерн, что удаление сущности: отзыв согласия на финданные закрывает
        // шесть роутеров разом (_FIN, app/api/router.py) — отменяемость важна не меньше.
        toast.undo(t("Согласие «{name}» отозвано.", { name: label(type) }), () => {
          grant.mutate(type, {
            onError: (error) => toastMutationError(error, t("Не получилось восстановить согласие.")),
          });
        });
      },
      onError: (error) => toastMutationError(error, t("Не получилось отозвать согласие. Попробуйте ещё раз.")),
    });
  }

  const entries = Object.entries(query.data) as [ConsentType, (typeof query.data)[ConsentType]][];

  return (
    <section className="fp-profile__card" aria-labelledby="fp-consents-title">
      <h2 className="fp-profile__section-title" id="fp-consents-title">
        {t("Согласия")}
      </h2>
      <p className="fp-consents__lede">
        {t(
          "Здесь видно, какие согласия вы дали и когда. Любое, кроме основания обработки, " +
            "можно отозвать в один клик.",
        )}
      </p>

      <ul className="fp-consents" role="list">
        {entries.map(([type, state]) => {
          const document = legal.data?.documents[type];
          return (
            <li key={type} className="fp-consents__item">
              <div className="fp-profile__row">
                <span className="fp-profile__label">{label(type)}</span>
                <span
                  className="fp-profile__value"
                  ref={(node) => {
                    statusRefs.current[type] = node;
                  }}
                  tabIndex={-1}
                >
                  {/* Статус словом, а не только цветом бейджа ([A11Y-07]). */}
                  {state.granted ? (
                    <span>{t("Дано")}</span>
                  ) : (
                    <span className="fp-profile__badge">{t("Не дано")}</span>
                  )}
                  {state.granted && state.granted_at && (
                    <span className="fp-profile__value-secondary">
                      {" "}
                      — {formatDate(state.granted_at)}
                    </span>
                  )}
                </span>
              </div>

              {document && (
                <p className="fp-consent-doc-link">
                  <a href={document.url} target="_blank" rel="noreferrer">
                    {document.title}
                  </a>{" "}
                  <span className="fp-consents__version">
                    {t("ред. {version}", { version: state.version })}
                  </span>
                </p>
              )}

              <div className="fp-profile__actions">
                {state.granted ? (
                  state.withdrawable ? (
                    <Button
                      variant="danger"
                      aria-disabled={withdraw.isPending}
                      aria-busy={withdraw.isPending}
                      aria-label={t("Отозвать согласие: {name}", { name: label(type) })}
                      onClick={() => handleWithdraw(type)}
                    >
                      {withdraw.isPending ? t("Отзываем…") : t("Отозвать")}
                    </Button>
                  ) : (
                    <p className="fp-profile__hint">
                      {/* До v8.52.0 фраза отправляла в никуда: удаления аккаунта
                          в интерфейсе не существовало. Теперь секция «Аккаунт
                          и безопасность» стоит ниже на этой же странице, и текст
                          говорит, куда идти. */}
                      {t(
                        "Это согласие нельзя отозвать без удаления аккаунта — оно " +
                          "основание обработки. Удалить аккаунт можно ниже, в разделе " +
                          "«Аккаунт и безопасность».",
                      )}
                    </p>
                  )
                ) : (
                  <Button
                    variant="primary"
                    aria-disabled={grant.isPending}
                    aria-busy={grant.isPending}
                    aria-label={t("Дать согласие: {name}", { name: label(type) })}
                    onClick={() => handleGrant(type)}
                  >
                    {grant.isPending ? t("Даём согласие…") : t("Дать согласие")}
                  </Button>
                )}
              </div>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
