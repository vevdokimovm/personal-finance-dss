import { Link } from "@tanstack/react-router";
import { useProfile } from "@entities/profile";
import { t } from "@shared/lib/i18n/t";
import { APP_NAV_ITEMS } from "./navItems";
import "./AppNav.css";

/**
 * Постоянный навигационный каркас продукта ([IA-02] `docs/ui_ux_design_standard.md`).
 *
 * До этого компонента каркаса в SPA не было ВООБЩЕ: топбар состоял из `AuthTopbarLink` +
 * `ThemeToggle`, все `<Link>` продукта вели только на `/login`/`/register`/`/forgot-password`,
 * а переходы между финансовыми экранами существовали в трёх местах сырыми `<a href>`
 * (`Hero`, `DashboardEmpty`, `PlanningPage`). Следствие: `/obligations`, `/goals`, `/banks`
 * и `/profile` были недостижимы кликом ниоткуда — а в `/profile` живёт отзыв согласия на
 * обработку финансовых данных, то есть право по 152-ФЗ было реализовано и недоступно.
 * Тот же класс, что SEV1 `CONSENT-GATE-NO-UI` (`docs/reports/incidents/
 * consent_gate_no_ui_dead_end_incident.md`), только шире и не про согласие.
 * Гипотеза H1 independent-expert, подтверждена чтением кода в v8.30.2.
 */
export function AppNav() {
  const { data, error, isLoading } = useProfile();

  if (isLoading) return null;

  // Условие дословно то же, что в `AuthTopbarLink`, и по той же причине: TanStack Query
  // держит последние успешные `data` даже когда рефетч упал (stale-if-error, кэш на 401 не
  // чистится). Проверять `data` в одиночку — воспроизвести баг, пойманный в браузере на
  // топбаре. Гостю каркас не показываем сознательно: все семь экранов за гейтом согласия
  // или авторизации, семь ссылок в 403 — это семь тупиков ([IA-04] no dead ends).
  if (!data || error) return null;

  return (
    <nav className="fp-app-nav" aria-label={t("Основные разделы")}>
      <ul className="fp-app-nav__list">
        {APP_NAV_ITEMS.map(({ to, label }) => (
          <li key={to}>
            <Link
              to={to}
              className="fp-app-nav__link"
              activeProps={{ "aria-current": "page" }}
              /* Точное совпадение нужно только корню: иначе `/` подсвечивался бы активным
                 на КАЖДОМ экране, потому что все пути начинаются со слэша. */
              activeOptions={to === "/" ? { exact: true } : undefined}
            >
              {t(label)}
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  );
}
