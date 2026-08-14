import { useState, type FormEvent } from "react";
import { Link } from "@tanstack/react-router";
import { useForgotPassword } from "@entities/auth";
import { Button } from "@shared/ui";
import { t } from "@shared/lib/i18n/t";
import { extractErrorMessage } from "@shared/lib/api/extractErrorMessage";
import { AuthLayout } from "./AuthLayout";
import "./AuthLayout.css";

export function ForgotPasswordPage() {
  const forgotPassword = useForgotPassword();
  const [email, setEmail] = useState("");
  // Бэкенд отдаёт один и тот же нейтральный текст независимо от того, существует ли email
  // (закрытая энумерация — routes_auth.py: "Энумерация закрыта"), берём его как есть, не
  // придумываем свой — один источник текста.
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const result = await forgotPassword.mutateAsync({ email });
    setSuccessMessage(
      result.detail ??
        t("Если аккаунт с таким email существует, на него отправлена ссылка для сброса пароля."),
    );
  }

  const errorMessage = forgotPassword.error
    ? extractErrorMessage(
        forgotPassword.error,
        t("Не получилось отправить запрос. Попробуйте ещё раз."),
      )
    : null;

  return (
    <AuthLayout
      title={t("Забыли пароль?")}
      lede={
        successMessage
          ? undefined
          : t("Укажите email, на который зарегистрирован аккаунт — пришлём ссылку для сброса.")
      }
      footer={
        <p>
          <Link to="/login">{t("Вернуться ко входу")}</Link>
        </p>
      }
    >
      {successMessage ? (
        <p className="fp-auth-banner fp-auth-banner--success" role="status">
          {successMessage}
        </p>
      ) : (
        <form className="fp-auth-form" onSubmit={handleSubmit}>
          {errorMessage && (
            <p className="fp-auth-banner" role="alert">
              {errorMessage}
            </p>
          )}
          <div className="fp-auth-field">
            <label htmlFor="forgot-email">{t("Email")}</label>
            <input
              id="forgot-email"
              type="email"
              autoComplete="email"
              inputMode="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <Button
            type="submit"
            variant="primary"
            disabled={forgotPassword.isPending}
            aria-busy={forgotPassword.isPending}
          >
            {forgotPassword.isPending ? t("Отправляем…") : t("Отправить ссылку")}
          </Button>
        </form>
      )}
    </AuthLayout>
  );
}
