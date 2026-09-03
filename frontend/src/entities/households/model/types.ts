/**
 * Рукописных типов нет — только реэкспорт сгенерированных из контракта.
 *
 * Урок v8.31.1: рукописный тип пообещал больше контракта, TypeScript молчал из-за
 * каста, и дашборд падал в error boundary. У households схемы на бэкенде полноценные
 * (`app/schemas/household.py`), поэтому брать их даром — единственно верно.
 */
export type {
  HouseholdResponse,
  HouseholdMemberResponse,
  HouseholdInviteResponse,
  HouseholdCreate,
  InviteAcceptResponse,
} from "@shared/api/generated";
