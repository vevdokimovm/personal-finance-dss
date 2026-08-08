import { createFileRoute } from "@tanstack/react-router";
import { PlanningPage } from "@pages/planning";

export const Route = createFileRoute("/planning")({
  component: PlanningPage,
});
