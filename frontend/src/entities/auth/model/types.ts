/**
 * Локальные типы для слоя auth — по тому же принципу, что `entities/plan-summary/model/types.ts`:
 * реэкспорт сгенерированных типов под именами, которые действительно используются на фронте,
 * не придуманные заново.
 */
export type {
  AuthResponse,
  RegisterRequest,
  LoginRequest,
  ForgotPasswordRequest,
  ResetPasswordRequest,
} from "@shared/api/generated";
