import { useRef } from "react";
import { useSearch, Link } from "@tanstack/react-router";
import { ListSkeleton, StatePanel, Button, toast } from "@shared/ui";
import { t } from "@shared/lib/i18n/t";
import { formatDate } from "@shared/lib/date/formatDate";
import { useProfile, NotAuthenticatedError } from "@entities/profile";
import { useConsents, useGrantConsent, useWithdrawConsent } from "@entities/consents";
import "./ProfilePage.css";

/** Рабочий минимум согласия на финданные в профиле (ROADMAP §8.2) — не полный
 * экран L3 (текст согласия + версия/дата вместо полноценного юридического текста,
 * ссылка на документ ведёт на него отдельно). Без этого блока пользователь после
 * регистрации упирался в 403 (`consent_required`) на каждом финансовом экране без
 * единого способа выйти из тупика через интерфейс — эмпирически подтверждено
 * 2026-08-19, см. WATCHLOG. Загрузка/ошибка согласий — тихая (не блокирует
 * остальной профиль своим состоянием): само согласие важнее, чем красиво
 * показать, что его статус временно не смог загрузиться. */
function ConsentsSection() {
  const query = useConsents();
  const grant = useGrantConsent();
  const withdraw = useWithdrawConsent();
  // Фокус после смены статуса (a11y-auditor): кнопка «Дать согласие»/«Отозвать»
  // размонтируется вместе с блоком статуса — без явного переноса фокус проваливается
  // в <body> (тот же класс проблемы, что и в ConsentRequiredPanel/списках).
  const statusRef = useRef<HTMLSpanElement>(null);

  if (query.isLoading || query.isError || !query.data) return null;

  const financial = query.data.financial_data;

  function handleGrant() {
    if (grant.isPending) return;
    grant.mutate("financial_data", {
      onSuccess: () => statusRef.current?.focus(),
      onError: () => toast.error(t("Не получилось сохранить согласие. Попробуйте ещё раз.")),
    });
  }

  function handleWithdraw() {
    if (withdraw.isPending) return;
    withdraw.mutate("financial_data", {
      onSuccess: () => {
        statusRef.current?.focus();
        // Тот же паттерн, что удаление обязательства/актива (toastStore.ts) — отзыв
        // согласия закрывает шесть финансовых роутеров разом (_FIN, router.py), это
        // не мелочь, отменяемость важна не меньше, чем для удаления записи.
        toast.undo(t("Согласие на финансовые данные отозвано."), () => {
          grant.mutate("financial_data", {
            onError: () => toast.error(t("Не получилось восстановить согласие.")),
          });
        });
      },
      onError: () => toast.error(t("Не получилось отозвать согласие. Попробуйте ещё раз.")),
    });
  }

  return (
    <section className="fp-profile__card">
      <h2 className="fp-profile__section-title">{t("Согласия")}</h2>
      <div className="fp-profile__row">
        <span className="fp-profile__label">{t("Финансовые данные")}</span>
        <span className="fp-profile__value" ref={statusRef} tabIndex={-1}>
          {financial.granted ? (
            <span>{t("Дано")}</span>
          ) : (
            <span className="fp-profile__badge">{t("Не дано")}</span>
          )}
          {financial.granted && financial.granted_at && (
            <span className="fp-profile__value-secondary">
              {" "}
              — {formatDate(financial.granted_at)}
            </span>
          )}
        </span>
      </div>
      <p className="fp-consent-doc-link">
        <a href="/legal/financial-consent" target="_blank" rel="noreferrer">
          {t("Согласие на обработку финансовых данных")}
        </a>
      </p>
      <div className="fp-profile__actions">
        {financial.granted ? (
          financial.withdrawable ? (
            <Button
              variant="danger"
              aria-disabled={withdraw.isPending}
              aria-busy={withdraw.isPending}
              onClick={handleWithdraw}
            >
              {withdraw.isPending ? t("Отзываем…") : t("Отозвать")}
            </Button>
          ) : (
            <p className="fp-profile__hint">
              {t("Это согласие нельзя отозвать без удаления аккаунта — оно основание обработки.")}
            </p>
          )
        ) : (
          <Button
            variant="primary"
            aria-disabled={grant.isPending}
            aria-busy={grant.isPending}
            onClick={handleGrant}
          >
            {grant.isPending ? t("Даём согласие…") : t("Дать согласие")}
          </Button>
        )}
      </div>
    </section>
  );
}

/** GET /api/auth/verify (ссылка в письме) редиректит сюда с ?verified=1|0 — не отдельный
 * экран (routes_auth.py::verify_email), только баннер поверх уже существующего профиля. */
function VerifiedBanner() {
  const search = useSearch({ strict: false }) as { verified?: string };
  if (search.verified === "1") {
    return (
      <p className="fp-profile__banner fp-profile__banner--success" role="status">
        {t("Email подтверждён.")}
      </p>
    );
  }
  if (search.verified === "0") {
    return (
      <p className="fp-profile__banner" role="alert">
        {t("Ссылка подтверждения недействительна или устарела — не получилось подтвердить email.")}
      </p>
    );
  }
  return null;
}

/** Профиль — единственная запись текущего пользователя, не список: "пусто" не имеет
 * смысла для синглтона. Состояний четыре, но не как у списков (loading/empty/error/
 * success) — здесь loading/неаутентифицирован/error/success: неаутентифицирован —
 * не ошибка (401 ожидаем для гостя, useProfile.ts), а отдельная ветка БЕЗ кнопки
 * "Повторить" — эндпоинт не даст другого ответа, пока нет экрана входа (которого
 * в приложении пока нет), и молчаливый цикл retry без объяснения — сам по себе
 * находка a11y-auditor (Э4 партия 2, P1: тупик для пользователей экранных
 * дикторов). role="status" (не "alert") — это не сбой, а ожидаемое состояние. */
export function ProfilePage() {
  const query = useProfile();

  if (query.isLoading) {
    return (
      <main className="fp-profile">
        <h1>{t("Профиль")}</h1>
        <ListSkeleton rows={2} />
      </main>
    );
  }

  if (query.error instanceof NotAuthenticatedError) {
    return (
      <main className="fp-profile">
        <h1>{t("Профиль")}</h1>
        <StatePanel
          title={t("Нужно войти в систему")}
          action={
            <Button variant="primary" asChild>
              <Link to="/login">{t("Войти")}</Link>
            </Button>
          }
        >
          {t("Профиль доступен только после входа.")}
        </StatePanel>
      </main>
    );
  }

  if (query.isError || !query.data) {
    return (
      <main className="fp-profile">
        <h1>{t("Профиль")}</h1>
        <StatePanel
          title={t("Не получилось загрузить профиль")}
          role="alert"
          action={
            <Button variant="primary" onClick={() => void query.refetch()}>
              {t("Повторить")}
            </Button>
          }
        >
          {t("Проверьте соединение и попробуйте ещё раз. Если повторится — напишите в поддержку.")}
        </StatePanel>
      </main>
    );
  }

  const profile = query.data;

  return (
    <main className="fp-profile">
      <h1>{t("Профиль")}</h1>
      <VerifiedBanner />
      <section className="fp-profile__card">
        <div className="fp-profile__row">
          <span className="fp-profile__label">{t("Имя")}</span>
          <span className="fp-profile__value">{profile.display_name ?? t("Не указано")}</span>
        </div>
        <div className="fp-profile__row">
          <span className="fp-profile__label">{t("Email")}</span>
          <span className="fp-profile__value">
            {profile.email}
            {!profile.email_verified && (
              <span className="fp-profile__badge">{t("не подтверждён")}</span>
            )}
          </span>
        </div>
        {profile.created_at && (
          <div className="fp-profile__row">
            <span className="fp-profile__label">{t("В FINPILOT с")}</span>
            <span className="fp-profile__value">{formatDate(profile.created_at)}</span>
          </div>
        )}
      </section>
      <ConsentsSection />
    </main>
  );
}
