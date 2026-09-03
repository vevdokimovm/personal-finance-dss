import { createFileRoute } from "@tanstack/react-router";
import { HouseholdsPage } from "@pages/households";

export const Route = createFileRoute("/household")({
  component: HouseholdsPage,
});
