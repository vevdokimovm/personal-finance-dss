import type { TransactionResponse } from "@shared/api/generated";

/** Псевдоним сгенерированного типа — TransactionResponse уже строго типизирован
 * бэкендом (не dict[str, Any], как planning/*), переизобретать поля не нужно. */
export type Transaction = TransactionResponse;
