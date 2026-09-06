import { createFileRoute } from "@tanstack/react-router";
import { LoginPage } from "@pages/auth";

type LoginSearch = {
  redirect?: string;
  ref?: string;
};

/**
 * 🔴 `validateSearch` объявляет `?redirect=` типом, а не только на словах.
 *
 * Параметр использовался с v8.x (приглашение в семейный доступ ведёт гостя
 * на `/login?redirect=/join?token=...`), читался через `useSearch` и покрыт
 * тестами — но маршрут о нём не знал. Из-за этого `<Link to={`/login${search}`}>`
 * в `SessionExpiredPanel` не проходил `tsc`: типизированный `to` не принимает
 * произвольную строку, и **CI падал на typecheck**, хотя код работал.
 *
 * Обход через шаблонную строку выглядел безобиднее объявления и был хуже:
 * он прятал параметр от системы типов, оставляя её правой.
 *
 * Проверка значения здесь намеренно слабая — только «строка или нет». Защита
 * от открытого редиректа живёт в `safeRedirect` (`@shared/lib/navigation`)
 * и остаётся там: маршрут отвечает за форму параметра, а не за доверие к нему.
 *
 * 🔴 `ref` — реферальный код, и он попал сюда не сразу: объявление одного `redirect`
 * сломало `RegisterPage`, которая уже ходила `<Link to="/login" search={{ ref }}>`.
 * Пока `validateSearch` не было, роутер принимал ЛЮБОЙ набор параметров, и оба
 * использования жили молча. Первое же объявление превращает молчаливое согласие
 * в проверяемый список — и обязано перечислить всё, что действительно ходит.
 */
export const Route = createFileRoute("/login")({
  component: LoginPage,
  validateSearch: (search: Record<string, unknown>): LoginSearch => ({
    redirect: typeof search.redirect === "string" ? search.redirect : undefined,
    ref: typeof search.ref === "string" ? search.ref : undefined,
  }),
});
