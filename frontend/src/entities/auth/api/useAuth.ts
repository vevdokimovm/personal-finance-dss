import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  registerApiAuthRegisterPost,
  loginApiAuthLoginPost,
  mfaVerifyApiAuthMfaVerifyPost,
  changePasswordApiAuthChangePasswordPost,
  deleteAccountApiAuthMeDelete,
  logoutApiAuthLogoutPost,
  resendVerificationApiAuthResendVerificationPost,
  forgotPasswordApiAuthForgotPasswordPost,
  resetPasswordApiAuthResetPasswordPost,
} from "@shared/api/generated";
import { PROFILE_QUERY_KEY } from "@entities/profile";
import type {
  AuthResponse,
  ChangePasswordRequest,
  ForgotPasswordRequest,
  LoginRequest,
  MfaVerifyRequest,
  RegisterRequest,
  ResetPasswordRequest,
} from "../model/types";

/** Успешные register/login/logout кладут/чистят httpOnly-cookie сами (бэкенд,
 * `_set_auth_cookie`/`delete_cookie`) — здесь только инвалидируем кэш «кто я» (уже существует
 * как `entities/profile::useProfile`, не заводим второй параллельный запрос на тот же
 * GET /api/auth/me), чтобы топбар и защищённые запросы узнали о входе/выходе сразу. */
function useInvalidateProfile() {
  const queryClient = useQueryClient();
  return () => queryClient.invalidateQueries({ queryKey: PROFILE_QUERY_KEY });
}

export function useRegister() {
  const invalidate = useInvalidateProfile();
  return useMutation({
    mutationFn: async (body: RegisterRequest) => {
      const { data } = await registerApiAuthRegisterPost({ body, throwOnError: true });
      return data satisfies AuthResponse;
    },
    onSuccess: invalidate,
  });
}

export function useLogin() {
  const invalidate = useInvalidateProfile();
  return useMutation({
    mutationFn: async (body: LoginRequest) => {
      const { data } = await loginApiAuthLoginPost({ body, throwOnError: true });
      return data satisfies AuthResponse;
    },
    // mfa_required=true не заводит полную сессию (см. routes_auth.py::login) — инвалидировать
    // «кто я» в этом случае рано, там ещё нет cookie. Второй фактор вводится на том же
    // экране входа (v9.0.0) и завершается `useMfaVerify` ниже.
    onSuccess: (data) => {
      if (!data.mfa_required) invalidate();
    },
  });
}

/**
 * POST /api/auth/mfa/verify — обмен `mfa_token` на полную сессию (v9.0.0).
 *
 * 🔴 Гипотеза H9 независимого эксперта, подтверждена чтением кода. `/mfa/enroll`
 * и `/mfa/confirm` открыты любому пользователю, а войти с включённым вторым фактором
 * было НЕЛЬЗЯ: экран входа показывал уведомление без поля кода. Аккаунт, у которого
 * MFA когда-либо включали, запирался навсегда — `/mfa/disable` требует уже
 * аутентифицированной сессии, то есть выключить фактор может только тот, кто вошёл.
 *
 * Принимает и TOTP, и одноразовый recovery-код: схема `MfaVerifyRequest` допускает
 * до 16 символов, и это единственный выход при потерянном устройстве.
 */
export function useMfaVerify() {
  const invalidate = useInvalidateProfile();
  return useMutation({
    mutationFn: async (body: MfaVerifyRequest) => {
      const { data } = await mfaVerifyApiAuthMfaVerifyPost({ body, throwOnError: true });
      return data satisfies AuthResponse;
    },
    onSuccess: invalidate,
  });
}

export function useLogout() {
  const invalidate = useInvalidateProfile();
  return useMutation({
    mutationFn: async () => {
      await logoutApiAuthLogoutPost({ throwOnError: true });
    },
    onSuccess: invalidate,
  });
}

/**
 * Смена пароля (v8.52.0).
 *
 * 🔴 Эндпоинт жил на бэкенде без UI вовсе — найдено аудитом independent-expert
 * 05.09.2026. Скомпрометированный пароль сменить из интерфейса было нельзя, только
 * через «забыли пароль» и рабочий SMTP.
 *
 * Сервер гасит ВСЕ сессии, включая текущую (банковская планка, см. `routes_auth`),
 * поэтому после успеха профиль инвалидируется: интерфейс обязан немедленно перейти
 * в состояние «не авторизован», а не показывать данные из кеша.
 */
export function useChangePassword() {
  const invalidate = useInvalidateProfile();
  return useMutation({
    mutationFn: async (body: ChangePasswordRequest) => {
      const { data } = await changePasswordApiAuthChangePasswordPost({
        body,
        throwOnError: true,
      });
      return data;
    },
    onSuccess: invalidate,
  });
}

/**
 * Удаление аккаунта со всеми данными (v8.52.0).
 *
 * 🔴 Это путь исполнения права по 152-ФЗ: экран согласий говорит «отозвать согласие
 * на обработку ПДн можно только удалением аккаунта», а удаления в интерфейсе не было.
 * Право реализовано на бэкенде и недостижимо — повтор SEV1 `CONSENT-GATE-NO-UI`.
 */
export function useDeleteAccount() {
  const invalidate = useInvalidateProfile();
  return useMutation({
    mutationFn: async () => {
      const { data } = await deleteAccountApiAuthMeDelete({ throwOnError: true });
      return data;
    },
    onSuccess: invalidate,
  });
}

/**
 * Повторная отправка письма подтверждения (v8.52.0).
 *
 * 🔴 Бейдж «не подтверждён» стоял на профиле без единого действия рядом — найдено
 * аудитом independent-expert. На первом деплое без рабочего SMTP (а
 * `docs/deploy_owner_checklist.md` прямо предупреждает, что почта может не успеть)
 * все аккаунты остались бы «не подтверждён» навсегда, и починить это из интерфейса
 * было бы нельзя.
 */
export function useResendVerification() {
  return useMutation({
    mutationFn: async () => {
      const { data } = await resendVerificationApiAuthResendVerificationPost({
        throwOnError: true,
      });
      return data;
    },
  });
}

export function useForgotPassword() {
  return useMutation({
    mutationFn: async (body: ForgotPasswordRequest) => {
      const { data } = await forgotPasswordApiAuthForgotPasswordPost({ body, throwOnError: true });
      return data;
    },
  });
}

export function useResetPassword() {
  return useMutation({
    mutationFn: async (body: ResetPasswordRequest) => {
      const { data } = await resetPasswordApiAuthResetPasswordPost({ body, throwOnError: true });
      return data;
    },
  });
}
