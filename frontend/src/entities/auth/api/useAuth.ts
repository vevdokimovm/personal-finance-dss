import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  registerApiAuthRegisterPost,
  loginApiAuthLoginPost,
  logoutApiAuthLogoutPost,
  forgotPasswordApiAuthForgotPasswordPost,
  resetPasswordApiAuthResetPasswordPost,
} from "@shared/api/generated";
import { PROFILE_QUERY_KEY } from "@entities/profile";
import type {
  AuthResponse,
  ForgotPasswordRequest,
  LoginRequest,
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
    // «кто я» в этом случае рано, там ещё нет cookie. MFA-экран — вне периметра этого батча
    // (в UI пока нет способа включить MFA вообще, ветка практически недостижима).
    onSuccess: (data) => {
      if (!data.mfa_required) invalidate();
    },
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
