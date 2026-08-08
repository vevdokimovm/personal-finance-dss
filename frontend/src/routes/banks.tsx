import { createFileRoute } from "@tanstack/react-router";
import { AssetsPage } from "@pages/assets";

/* Путь /banks — как в старой Jinja-версии (frontend/templates/banks.html), хотя
   экран показывает ликвидные активы, а не банковские подключения (заголовок
   страницы там же — «Ликвидные активы»). Оставлено ради непрерывности ссылок. */
export const Route = createFileRoute("/banks")({
  component: AssetsPage,
});
