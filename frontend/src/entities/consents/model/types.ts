export type ConsentType = "personal_data" | "financial_data" | "marketing";

export interface ConsentState {
  granted: boolean;
  version: string;
  granted_at: string | null;
  withdrawable: boolean;
}

export type ConsentsMap = Record<ConsentType, ConsentState>;
