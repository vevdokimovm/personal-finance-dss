import { createFileRoute } from "@tanstack/react-router";
import { ForgotPasswordPage } from "@pages/auth";

export const Route = createFileRoute("/forgot-password")({
  component: ForgotPasswordPage,
});
