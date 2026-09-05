import { createFileRoute } from "@tanstack/react-router";
import { SpendingPage } from "@pages/spending";

/* Советы по расходам — раздел продукта, доступный каждому вошедшему (в отличие от
   `/insights` и `/experiments`, которые видит только владелец). Пункт меню обязателен:
   экран без входа кликом — тот же класс дефекта, что SEV1 `CONSENT-GATE-NO-UI`. */
export const Route = createFileRoute("/spending")({
  component: SpendingPage,
});
