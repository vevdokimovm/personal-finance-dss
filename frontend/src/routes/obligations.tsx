import { createFileRoute } from "@tanstack/react-router";
import { ObligationsPage } from "@pages/obligations";

export const Route = createFileRoute("/obligations")({
  component: ObligationsPage,
});
