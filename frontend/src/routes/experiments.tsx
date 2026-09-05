import { createFileRoute } from "@tanstack/react-router";
import { ExperimentsPage } from "@pages/experiments";

/* Результаты A/B — экран владельца (`is_owner`), как и метрики. Пункт меню живёт
   в `OWNER_NAV_ITEMS`: он виден только владельцу, остальным сервер отдаёт 403,
   и показывать такой пункт всем значило бы вести в гарантированный отказ ([IA-04]). */
export const Route = createFileRoute("/experiments")({
  component: ExperimentsPage,
});
