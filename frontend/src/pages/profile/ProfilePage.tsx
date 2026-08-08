import { ListSkeleton, StatePanel, Button } from "@shared/ui";
import { t } from "@shared/lib/i18n/t";
import { formatDate } from "@shared/lib/date/formatDate";
import { useProfile, NotAuthenticatedError } from "@entities/profile";
import "./ProfilePage.css";

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
        <StatePanel title={t("Нужно войти в систему")}>
          {t(
            "Профиль доступен только после входа. Экран входа для этой версии интерфейса ещё не готов.",
          )}
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
    </main>
  );
}
