import { describe, expect, it, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";

/**
 * Десятый хук слоя `entities` (см. `docs/reports/testing/frontend_coverage.md`) —
 * самый крупный из непокрытых, 35 строк.
 *
 * 🔴 **Все девять мутаций отличаются друг от друга ровно одним: сбрасывать ли профиль.**
 * Cookie ставит и чистит бэкенд (`_set_auth_cookie`/`delete_cookie`), фронт только
 * говорит кэшу «кто я» перечитаться. Ошибка здесь не видна глазами: интерфейс покажет
 * прежнее состояние — топбар с именем после выхода или гостя после входа, — и человек
 * решит, что действие не сработало, и повторит его.
 *
 * Три группы, и границы между ними — решения, а не совпадения:
 *
 * 1. **Сбрасывают:** регистрация, второй фактор, выход, смена пароля, удаление аккаунта.
 * 2. **Сбрасывает УСЛОВНО:** вход — только когда сессия действительно заведена.
 * 3. **Не сбрасывают:** повторное письмо, «забыли пароль», сброс по ссылке —
 *    личность не изменилась, перечитывать нечего.
 */

const registerFn = vi.fn();
const loginFn = vi.fn();
const mfaVerifyFn = vi.fn();
const logoutFn = vi.fn();
const changePasswordFn = vi.fn();
const deleteAccountFn = vi.fn();
const resendFn = vi.fn();
const forgotFn = vi.fn();
const resetFn = vi.fn();

vi.mock("@shared/api/generated", () => ({
  registerApiAuthRegisterPost: (...a: unknown[]) => registerFn(...a),
  loginApiAuthLoginPost: (...a: unknown[]) => loginFn(...a),
  mfaVerifyApiAuthMfaVerifyPost: (...a: unknown[]) => mfaVerifyFn(...a),
  logoutApiAuthLogoutPost: (...a: unknown[]) => logoutFn(...a),
  changePasswordApiAuthChangePasswordPost: (...a: unknown[]) => changePasswordFn(...a),
  deleteAccountApiAuthMeDelete: (...a: unknown[]) => deleteAccountFn(...a),
  resendVerificationApiAuthResendVerificationPost: (...a: unknown[]) => resendFn(...a),
  forgotPasswordApiAuthForgotPasswordPost: (...a: unknown[]) => forgotFn(...a),
  resetPasswordApiAuthResetPasswordPost: (...a: unknown[]) => resetFn(...a),
}));

vi.mock("@entities/profile", () => ({ PROFILE_QUERY_KEY: ["profile", "me"] }));

const {
  useRegister,
  useLogin,
  useMfaVerify,
  useLogout,
  useChangePassword,
  useDeleteAccount,
  useResendVerification,
  useForgotPassword,
  useResetPassword,
} = await import("./useAuth");

const PROFILE_KEY = { queryKey: ["profile", "me"] };

function makeWrapper() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  const wrapper = ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={client}>{children}</QueryClientProvider>
  );
  return { client, wrapper };
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("useLogin — сброс профиля зависит от того, заведена ли сессия", () => {
  it("обычный вход сбрасывает «кто я»", async () => {
    loginFn.mockResolvedValue({ data: { access_token: "t", mfa_required: false } });
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const { result } = renderHook(() => useLogin(), { wrapper });
    result.current.mutate({ email: "a@test.io", password: "password123" });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(invalidate).toHaveBeenCalledWith(PROFILE_KEY);
  });

  it("🔴 вход с требованием второго фактора НЕ сбрасывает — cookie ещё нет", async () => {
    /* Главная проверка файла. При `mfa_required` бэкенд отдаёт короткоживущий
       `mfa_token` и НЕ ставит сессионную cookie (`routes_auth.py::login`).
       Инвалидация здесь заставила бы `GET /api/auth/me` сходить впустую и получить
       401 — то есть на экране ввода кода мигнула бы «сессия истекла» ровно в тот
       момент, когда человек правильно ввёл пароль. */
    loginFn.mockResolvedValue({ data: { access_token: "", mfa_required: true, mfa_token: "m" } });
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const { result } = renderHook(() => useLogin(), { wrapper });
    result.current.mutate({ email: "a@test.io", password: "password123" });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(invalidate).not.toHaveBeenCalled();
  });

  it("неверный пароль профиль не трогает", async () => {
    loginFn.mockRejectedValue({ detail: "Неверная пара логин/пароль.", status: 401 });
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const { result } = renderHook(() => useLogin(), { wrapper });
    result.current.mutate({ email: "a@test.io", password: "wrong" });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(invalidate).not.toHaveBeenCalled();
  });
});

describe("useMfaVerify — вторая половина входа", () => {
  it("успешный код сбрасывает профиль: вот теперь сессия есть", async () => {
    /* 🔴 Гипотеза H9 аудита: до v9.0.0 войти с включённым вторым фактором было
       нельзя вовсе, а `/mfa/disable` требует уже аутентифицированной сессии —
       аккаунт запирался навсегда. Этот хук и есть выход из ловушки. */
    mfaVerifyFn.mockResolvedValue({ data: { access_token: "t", mfa_required: false } });
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const { result } = renderHook(() => useMfaVerify(), { wrapper });
    result.current.mutate({ mfa_token: "m", code: "123456" });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(mfaVerifyFn).toHaveBeenCalledWith({
      body: { mfa_token: "m", code: "123456" },
      throwOnError: true,
    });
    expect(invalidate).toHaveBeenCalledWith(PROFILE_KEY);
  });

  it("recovery-код идёт тем же путём", async () => {
    /* Схема допускает до 16 символов именно ради recovery-кода `XXXX-XXXX`:
       при потерянном устройстве это единственный вход. Отдельного хука нет
       и не нужно — эндпоинт принимает оба вида. */
    mfaVerifyFn.mockResolvedValue({ data: { access_token: "t", mfa_required: false } });
    const { wrapper } = makeWrapper();

    const { result } = renderHook(() => useMfaVerify(), { wrapper });
    result.current.mutate({ mfa_token: "m", code: "dead-beef" });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(mfaVerifyFn).toHaveBeenCalledWith({
      body: { mfa_token: "m", code: "dead-beef" },
      throwOnError: true,
    });
  });
});

describe("Действия, меняющие состояние сессии, — сбрасывают профиль", () => {
  it("регистрация", async () => {
    registerFn.mockResolvedValue({ data: { access_token: "t", mfa_required: false } });
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const { result } = renderHook(() => useRegister(), { wrapper });
    result.current.mutate({ email: "new@test.io", password: "password123", consent: true });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(invalidate).toHaveBeenCalledWith(PROFILE_KEY);
  });

  it("выход", async () => {
    logoutFn.mockResolvedValue({ data: null });
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const { result } = renderHook(() => useLogout(), { wrapper });
    result.current.mutate();

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(invalidate).toHaveBeenCalledWith(PROFILE_KEY);
  });

  it("🔴 смена пароля — сервер гасит ВСЕ сессии, включая текущую", async () => {
    /* Банковская планка (`routes_auth`): после смены пароля недействительна и та
       сессия, из которой его меняли. Не сбросить профиль значит показывать данные
       из кэша под уже мёртвым токеном — интерфейс обязан немедленно перейти
       в «не авторизован». */
    changePasswordFn.mockResolvedValue({ data: { status: "ok" } });
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const { result } = renderHook(() => useChangePassword(), { wrapper });
    result.current.mutate({ current_password: "old12345", new_password: "new123456" });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(invalidate).toHaveBeenCalledWith(PROFILE_KEY);
  });

  it("🔴 удаление аккаунта — путь исполнения права по 152-ФЗ", async () => {
    /* Экран согласий говорит «отозвать согласие на обработку ПДн можно только
       удалением аккаунта». До v8.52.0 удаления в интерфейсе не было: право
       реализовано на бэкенде и недостижимо — повтор SEV1 `CONSENT-GATE-NO-UI`. */
    deleteAccountFn.mockResolvedValue({ data: { status: "deleted" } });
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const { result } = renderHook(() => useDeleteAccount(), { wrapper });
    result.current.mutate();

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(invalidate).toHaveBeenCalledWith(PROFILE_KEY);
  });
});

describe("Действия, не меняющие личность, — профиль не трогают", () => {
  it("повторное письмо подтверждения", async () => {
    /* 🔴 Бейдж «не подтверждён» стоял на профиле без единого действия рядом.
       На деплое без рабочего SMTP все аккаунты остались бы «не подтверждён»
       навсегда. Но сама отправка письма ничего в личности не меняет —
       сбрасывать кэш незачем. */
    resendFn.mockResolvedValue({ data: { sent: true } });
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const { result } = renderHook(() => useResendVerification(), { wrapper });
    result.current.mutate();

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(invalidate).not.toHaveBeenCalled();
  });

  it("«забыли пароль» и сброс по ссылке", async () => {
    /* Оба вызываются, когда человек НЕ авторизован: перечитывать «кто я» нечего,
       и запрос ушёл бы в 401 на глазах у того, кто и так не вошёл. */
    forgotFn.mockResolvedValue({ data: { sent: true } });
    resetFn.mockResolvedValue({ data: { status: "ok" } });
    const { client, wrapper } = makeWrapper();
    const invalidate = vi.spyOn(client, "invalidateQueries");

    const forgot = renderHook(() => useForgotPassword(), { wrapper });
    forgot.result.current.mutate({ email: "a@test.io" });
    await waitFor(() => expect(forgot.result.current.isSuccess).toBe(true));

    const reset = renderHook(() => useResetPassword(), { wrapper });
    reset.result.current.mutate({ token: "tok", new_password: "new123456" });
    await waitFor(() => expect(reset.result.current.isSuccess).toBe(true));

    expect(invalidate).not.toHaveBeenCalled();
  });
});
