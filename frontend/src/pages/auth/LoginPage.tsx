import { useState, type FormEvent } from "react";
import { useNavigate, useSearch, Link } from "@tanstack/react-router";
import { useLogin, useMfaVerify } from "@entities/auth";
import { Button, toast } from "@shared/ui";
import { t } from "@shared/lib/i18n/t";
import { safeRedirect } from "@shared/lib/navigation/redirectTarget";
import { extractErrorMessage } from "@shared/lib/api/extractErrorMessage";
import { AuthLayout } from "./AuthLayout";
import "./AuthLayout.css";

export function LoginPage() {
  const navigate = useNavigate();
  // Куда вернуть после успеха. Пусто — на дашборд; `/join?token=...` — обратно
  // к приглашению, иначе приглашённый терял ссылку на входе (v8.36.0).
  const search = useSearch({ strict: false }) as { redirect?: string };
  const login = useLogin();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const mfaVerify = useMfaVerify();
  /* 🔴 Второй фактор вводится ЗДЕСЬ же (v9.0.0), гипотеза H9 независимого эксперта.
     Раньше на `mfa_required` показывалось уведомление без поля кода, и аккаунт
     с включённым MFA запирался навсегда: `/mfa/enroll` открыт любому, а `/mfa/disable`
     требует уже аутентифицированной сессии — выключить фактор может только тот, кто
     вошёл. Восстановление оставалось лишь правкой базы руками.

     `mfaToken` краткоживущий и хранится ТОЛЬКО в состоянии компонента: класть его
     в localStorage значило бы оставить обходной путь второго фактора на диске. */
  const [mfaToken, setMfaToken] = useState<string | null>(null);
  const [mfaCode, setMfaCode] = useState("");

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setMfaToken(null);
    try {
      const result = await login.mutateAsync({ email, password });
      if (result.mfa_required && result.mfa_token) {
        setMfaToken(result.mfa_token);
        return;
      }
      toast.success(t("Добро пожаловать!"));
      navigate({ to: safeRedirect(search.redirect) ?? "/" });
    } catch {
      // Пароль не оставляем в поле после неверной попытки (общепринятая практика для
      // логин-форм) — email оставляем, его повторный ввод раздражает больше (FRM-06).
      setPassword("");
    }
  }

  const errorMessage = login.error
    ? extractErrorMessage(login.error, t("Не получилось войти. Попробуйте ещё раз."))
    : null;
  const mfaErrorMessage = mfaVerify.error
    ? extractErrorMessage(mfaVerify.error, t("Не удалось проверить код. Попробуйте ещё раз."))
    : null;

  async function handleMfaSubmit(e: FormEvent) {
    e.preventDefault();
    if (!mfaToken) return;
    try {
      await mfaVerify.mutateAsync({ mfa_token: mfaToken, code: mfaCode.trim() });
      toast.success(t("Добро пожаловать!"));
      navigate({ to: safeRedirect(search.redirect) ?? "/" });
    } catch {
      /* 🔴 Экран кода НЕ закрываем: увести обратно на пароль после опечатки значит
         заставить войти заново и получить НОВЫЙ `mfa_token`. Человек, ошибившийся
         цифрой, оказался бы в начале пути. Чистим только само поле. */
      setMfaCode("");
    }
  }

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
      {mfaToken ? (
        <form className="fp-auth-form" onSubmit={handleMfaSubmit} noValidate={false}>
          {mfaErrorMessage && (
            <p className="fp-auth-banner" role="alert">
              {mfaErrorMessage}
            </p>
          )}
          <div className="fp-auth-field">
            <label htmlFor="login-mfa-code">{t("Код подтверждения")}</label>
            <input
              id="login-mfa-code"
              type="text"
              /* `one-time-code` даёт автоподстановку из СМС/менеджера паролей.
                 Тип `text`, а не `number`: recovery-код содержит буквы и дефисы. */
              autoComplete="one-time-code"
              autoFocus
              required
              value={mfaCode}
              onChange={(e) => setMfaCode(e.target.value)}
              aria-describedby="login-mfa-hint"
            />
            <p id="login-mfa-hint" className="fp-auth-field__hint">
              {t(
                "Код из приложения-аутентификатора. Устройство недоступно — введите " +
                  "любой резервный код восстановления, выданный при включении защиты.",
              )}
            </p>
          </div>
          <Button
            type="submit"
            variant="primary"
            disabled={mfaVerify.isPending}
            aria-busy={mfaVerify.isPending}
          >
            {mfaVerify.isPending ? t("Проверяем…") : t("Подтвердить")}
          </Button>
        </form>
      ) : (
      <form className="fp-auth-form" onSubmit={handleSubmit} noValidate={false}>
        {errorMessage && (
          <p className="fp-auth-banner" role="alert">
            {errorMessage}
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
      )}
    </AuthLayout>
  );
}
