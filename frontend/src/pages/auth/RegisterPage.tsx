import { useState, type FormEvent } from "react";
import { useNavigate, useSearch, Link } from "@tanstack/react-router";
import { useRegister } from "@entities/auth";
import { Button, toast } from "@shared/ui";
import { t } from "@shared/lib/i18n/t";
import { safeRedirect } from "@shared/lib/navigation/redirectTarget";
import { extractErrorMessage } from "@shared/lib/api/extractErrorMessage";
import { AuthLayout } from "./AuthLayout";
import "./AuthLayout.css";

export function RegisterPage() {
  const navigate = useNavigate();
  // Куда вернуть после успеха. Пусто — на дашборд; `/join?token=...` — обратно
  // к приглашению, иначе приглашённый терял ссылку на входе (v8.36.0).
  const search = useSearch({ strict: false }) as { redirect?: string };
  const register = useRegister();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [consent, setConsent] = useState(false);
  const [newsletterOptIn, setNewsletterOptIn] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    try {
      await register.mutateAsync({
        email,
        password,
        display_name: displayName || undefined,
        consent,
        newsletter_opt_in: newsletterOptIn,
      });
      toast.success(t("Готово! Проверьте почту, чтобы подтвердить email."));
      navigate({ to: safeRedirect(search.redirect) ?? "/" });
    } catch {
      // Пароль не оставляем после неудачной попытки, email/имя/согласие — оставляем
      // (FRM-06): их повторный ввод раздражает больше, чем 8 символов пароля заново.
      setPassword("");
    }
  }

  const errorMessage = register.error
    ? extractErrorMessage(
        register.error,
        t("Не получилось зарегистрироваться. Попробуйте ещё раз."),
      )
    : null;

  return (
    <AuthLayout
      title={t("Регистрация")}
      lede={t(
        "Данные, которые вы уже внесли в гостевом режиме, останутся с вами после регистрации.",
      )}
      footer={
        <p>
          {t("Уже есть аккаунт? ")}
          <Link to="/login">{t("Войти")}</Link>
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
          <label htmlFor="register-email">{t("Email")}</label>
          <input
            id="register-email"
            type="email"
            autoComplete="email"
            inputMode="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>
        <div className="fp-auth-field">
          <label htmlFor="register-password">{t("Пароль")}</label>
          <input
            id="register-password"
            type="password"
            autoComplete="new-password"
            required
            minLength={8}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <p className="fp-auth-field__hint">{t("Минимум 8 символов.")}</p>
        </div>
        <div className="fp-auth-field">
          <label htmlFor="register-name">{t("Имя (необязательно)")}</label>
          <input
            id="register-name"
            type="text"
            autoComplete="name"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
          />
        </div>
        <label className="fp-auth-consent">
          <input
            type="checkbox"
            required
            checked={consent}
            onChange={(e) => setConsent(e.target.checked)}
          />
          {t("Согласен на обработку персональных данных (152-ФЗ)")}
        </label>
        <label className="fp-auth-consent">
          <input
            type="checkbox"
            checked={newsletterOptIn}
            onChange={(e) => setNewsletterOptIn(e.target.checked)}
          />
          {t("Подписаться на рассылку о продукте (необязательно)")}
        </label>
        <Button
          type="submit"
          variant="primary"
          disabled={register.isPending}
          aria-busy={register.isPending}
        >
          {register.isPending ? t("Регистрируем…") : t("Зарегистрироваться")}
        </Button>
      </form>
    </AuthLayout>
  );
}
