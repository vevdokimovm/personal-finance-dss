import { useState, type FormEvent } from "react";
import { useNavigate, useSearch, Link } from "@tanstack/react-router";
import { useResetPassword } from "@entities/auth";
import { Button, toast } from "@shared/ui";
import { t } from "@shared/lib/i18n/t";
import { extractErrorMessage } from "@shared/lib/api/extractErrorMessage";
import { AuthLayout } from "./AuthLayout";
import "./AuthLayout.css";

export function ResetPasswordPage() {
  const navigate = useNavigate();
  // strict:false — эта страница не завязана на конкретный файл-роут с validateSearch (первое
  // использование query-параметров в проекте вообще, см. reset-password.tsx), читает ?token=
  // как есть.
  const search = useSearch({ strict: false }) as { token?: string };
  const resetPassword = useResetPassword();
  const [newPassword, setNewPassword] = useState("");

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!search.token) return;
    await resetPassword.mutateAsync({ token: search.token, new_password: newPassword });
    toast.success(t("Пароль обновлён. Войдите с новым паролем."));
    navigate({ to: "/login" });
  }

  const errorMessage = resetPassword.error
    ? extractErrorMessage(
        resetPassword.error,
        t("Не получилось обновить пароль. Попробуйте ещё раз."),
      )
    : null;

  // Нет токена в ссылке — сразу объясняем, не показываем форму, которая гарантированно
  // упадёт на сабмите (fail-loud, не тихий тупик).
  if (!search.token) {
    return (
      <AuthLayout
        title={t("Сброс пароля")}
        footer={
          <p>
            <Link to="/forgot-password">{t("Запросить новую ссылку")}</Link>
          </p>
        }
      >
        <p className="fp-auth-banner" role="alert">
          {t("Ссылка недействительна — в ней нет токена сброса. Запросите новую.")}
        </p>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout
      title={t("Новый пароль")}
      footer={
        <p>
          <Link to="/forgot-password">{t("Запросить новую ссылку")}</Link>
        </p>
      }
    >
      <form className="fp-auth-form" onSubmit={handleSubmit}>
        {errorMessage && (
          <p className="fp-auth-banner" role="alert">
            {errorMessage}
          </p>
        )}
        <div className="fp-auth-field">
          <label htmlFor="reset-password">{t("Новый пароль")}</label>
          <input
            id="reset-password"
            type="password"
            autoComplete="new-password"
            required
            minLength={8}
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
          />
          <p className="fp-auth-field__hint">{t("Минимум 8 символов.")}</p>
        </div>
        <Button
          type="submit"
          variant="primary"
          disabled={resetPassword.isPending}
          aria-busy={resetPassword.isPending}
        >
          {resetPassword.isPending ? t("Сохраняем…") : t("Сохранить пароль")}
        </Button>
      </form>
    </AuthLayout>
  );
}
