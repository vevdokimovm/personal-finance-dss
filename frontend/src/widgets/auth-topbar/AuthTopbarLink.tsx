import { Link } from "@tanstack/react-router";
import { useProfile } from "@entities/profile";
import { useLogout } from "@entities/auth";
import { Button } from "@shared/ui";
import { t } from "@shared/lib/i18n/t";
import "./AuthTopbarLink.css";

/**
 * Единственная входная точка к /login и /register из интерфейса — без неё новые экраны
 * недостижимы (нет ссылки — не существует для пользователя). Раньше вход был JS-модалкой в
 * общем `base.html` легаси-вёрстки; когда семь экранов перенесли на React (Э3/Э4), общий
 * `base.html` остался только у нетронутых легаси-страниц, которые nginx больше не показывает
 * публично — модалка физически в коде, но недостижима с сайта.
 *
 * `useProfile()` уже существует (entities/profile, ProfilePage) — не второй параллельный
 * запрос на тот же GET /api/auth/me.
 */
export function AuthTopbarLink() {
  const { data, error, isLoading } = useProfile();
  const logout = useLogout();

  if (isLoading) return null;

  // TanStack Query держит последние успешные `data` даже когда рефетч упал (stale-if-error,
  // не очищает кэш на 401) — реальный баг, пойманный вручную в браузере: после logout()
  // /auth/me переотправляется, ловит 401 (cookie уже стёрта), но `data` осталась email
  // предыдущей сессии, и топбар продолжал показывать «Выйти» вместо «Войти». Проверка `error`
  // должна стоять раньше/вместе с `data`, не полагаться на то, что они взаимоисключающие.
  if (data && !error) {
    return (
      <span className="fp-auth-topbar">
        <span className="fp-auth-topbar__email">{data.email}</span>
        <Button
          variant="ghost"
          onClick={() => logout.mutate()}
          disabled={logout.isPending}
          aria-busy={logout.isPending}
        >
          {t("Выйти")}
        </Button>
      </span>
    );
  }

  // Гость (401) или сетевая ошибка — в обоих случаях ссылка на вход, не тупик молчания:
  // повторный клик по «Войти» и сама форма логина honest-но объяснит, если проблема в сети.
  return (
    <Link to="/login" className="fp-auth-topbar__login-link">
      {t("Войти")}
    </Link>
  );
}
