import { useState } from "react";
import { useSearch, Link } from "@tanstack/react-router";
import { ListSkeleton, StatePanel, Button } from "@shared/ui";
import { t } from "@shared/lib/i18n/t";
import { ReferralSection } from "./ReferralSection";
import { AccountSection } from "./AccountSection";
import { ConsentsSection } from "./ConsentsSection";
import { formatDate } from "@shared/lib/date/formatDate";
import { useProfile, NotAuthenticatedError } from "@entities/profile";
import { useResendVerification } from "@entities/auth";
import "./ProfilePage.css";


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
  const resendVerification = useResendVerification();
  /* Одноразовость в состоянии, а не в `isSuccess`: письмо ушло — повторять незачем,
     и кнопка, остающаяся активной, провоцирует спамить себе почту. */
  const [resendSent, setResendSent] = useState(false);

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
              <>
                <span className="fp-profile__badge">{t("не подтверждён")}</span>
                {/* 🔴 Бейдж-проблема обязан нести действие. До v8.52.0 он стоял один:
                    человек видел, что что-то не так, и не мог ничего сделать —
                    `resend-verification` жил на бэкенде и не вызывался ниоткуда. */}
                <Button
                  variant="ghost"
                  aria-disabled={resendVerification.isPending || resendSent}
                  aria-busy={resendVerification.isPending}
                  onClick={() => {
                    if (resendVerification.isPending || resendSent) return;
                    resendVerification.mutate(undefined, {
                      onSuccess: () => setResendSent(true),
                    });
                  }}
                >
                  {resendSent ? t("Письмо отправлено") : t("Отправить письмо ещё раз")}
                </Button>
              </>
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
      <ReferralSection />
      <ConsentsSection />
      {/* Секция аккаунта — ПОСЛЕ согласий: экран согласий отправляет сюда за отзывом
          согласия на ПДн («нельзя отозвать без удаления аккаунта»), и путь должен
          вести вниз по странице, а не вверх (v8.52.0). */}
      <AccountSection />
    </main>
  );
}
