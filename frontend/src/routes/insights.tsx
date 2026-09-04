import { createFileRoute } from "@tanstack/react-router";
import { InsightsPage } from "@pages/insights";

/* Метрики продукта — экран владельца (`is_owner`). В навигацию НЕ добавляется:
   каркас показывается всем вошедшим, а этот раздел доступен одному человеку, и пункт
   меню, ведущий в отказ, — тупик ([IA-04]). Владелец заходит по прямому адресу;
   гейт разграничения — `tests/test_owner_access.py`. */
export const Route = createFileRoute("/insights")({
  component: InsightsPage,
});
