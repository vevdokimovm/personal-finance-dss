import { createFileRoute } from "@tanstack/react-router";
import { ResetPasswordPage } from "@pages/auth";

/** ?token= из ссылки в письме (routes_auth.py::forgot_password, reset_url). Опциональный,
 * не required — ResetPasswordPage сама объясняет отсутствие токена (fail-loud), не 404. */
export const Route = createFileRoute("/reset-password")({
  validateSearch: (search: Record<string, unknown>): { token?: string } => ({
    token: typeof search.token === "string" ? search.token : undefined,
  }),
  component: ResetPasswordPage,
});
