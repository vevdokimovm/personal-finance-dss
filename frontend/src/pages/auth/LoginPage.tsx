import { useState, type FormEvent } from "react";
import { useNavigate, Link } from "@tanstack/react-router";
import { useLogin } from "@entities/auth";
import { Button, toast } from "@shared/ui";
import { t } from "@shared/lib/i18n/t";
import { extractErrorMessage } from "@shared/lib/api/extractErrorMessage";
import { AuthLayout } from "./AuthLayout";
import "./AuthLayout.css";

export function LoginPage() {
  const navigate = useNavigate();
  const login = useLogin();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  // MFA-код при входе — вне периметра этого батча (в UI пока нет способа включить MFA
  // вообще, см. план). Ветка технически возможна (бэкенд её отдаёт) — не молчим о ней
  // (fail-loud), а честно объясняем, а не падаем и не делаем вид, что вход прошёл.
  const [mfaNotice, setMfaNotice] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setMfaNotice(false);
    try {
      const result = await login.mutateAsync({ email, password });
      if (result.mfa_required) {
        setMfaNotice(true);
        return;
      }
      toast.success(t("Добро пожаловать!"));
      navigate({ to: "/" });
    } catch {
      // Пароль не оставляем в поле после неверной попытки (общепринятая практика для
      // логин-форм) — email оставляем, его повторный ввод раздражает больше (FRM-06).
      setPassword("");
    }
  }

  const errorMessage = login.error
    ? extractErrorMessage(login.error, t("Не получилось войти. Попробуйте ещё раз."))
    : null;

  return (
    <AuthLayout
      title={t("Вход")}
      footer={
        <>
          <p>
            {t("Нет аккаунта? ")}
            <Link to="/register">{t("Зарегистрироваться")}</Link>
          </p>
          <p>
            <Link to="/forgot-password">{t("Забыли пароль?")}</Link>
          </p>
        </>
      }
    >
      <form className="fp-auth-form" onSubmit={handleSubmit} noValidate={false}>
        {errorMessage && (
          <p className="fp-auth-banner" role="alert">
            {errorMessage}
          </p>
        )}
        {mfaNotice && (
          <p className="fp-auth-banner" role="alert">
            {t(
              "На этом аккаунте включена двухфакторная защита — экран ввода кода пока не готов в этой версии интерфейса.",
            )}
          </p>
        )}
        <div className="fp-auth-field">
          <label htmlFor="login-email">{t("Email")}</label>
          <input
            id="login-email"
            type="email"
            autoComplete="email"
            inputMode="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>
        <div className="fp-auth-field">
          <label htmlFor="login-password">{t("Пароль")}</label>
          <input
            id="login-password"
            type="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        <Button
          type="submit"
          variant="primary"
          disabled={login.isPending}
          aria-busy={login.isPending}
        >
          {login.isPending ? t("Входим…") : t("Войти")}
        </Button>
      </form>
    </AuthLayout>
  );
}
