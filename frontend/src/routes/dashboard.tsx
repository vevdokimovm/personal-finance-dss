import { createFileRoute, redirect } from "@tanstack/react-router";

/**
 * `/dashboard` → `/`.
 *
 * 🔴 Адрес существовал в Jinja (`app/main.py` отдавал по нему ту же страницу, что и `/`)
 * и умер вместе со снятием Jinja-роутов в v8.45.0: в React дашборд живёт на `/`, а сюда
 * приходил catch-all и показывал приложение с пустым маршрутом. Ссылок на `/dashboard`
 * в продукте не осталось, но остались закладки, история браузера и внешние ссылки —
 * для них это была бы страница «не найдено» на главном экране продукта.
 *
 * Найдено при написании e2e песочницы: тест ходил на `/dashboard` и получал «Not Found».
 */
export const Route = createFileRoute("/dashboard")({
  beforeLoad: () => {
    throw redirect({ to: "/", replace: true });
  },
});
