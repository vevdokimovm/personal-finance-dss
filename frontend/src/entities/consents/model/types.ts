import type { ConsentState as GeneratedConsentState } from "@shared/api/generated";

/**
 * Тип состояния согласия — РЕЭКСПОРТ сгенерированного из контракта (v8.41.0).
 *
 * Раньше он писался руками: `/consents` был размечен `-> dict`, и генерировать было
 * нечего. Схема заведена на бэкенде в этом же батче — держать рядом рукописную копию
 * значит ждать, когда она разойдётся (урок v8.31.1: рукописный тип пообещал больше
 * контракта, TypeScript промолчал из-за каста, дашборд упал).
 */
export type ConsentState = GeneratedConsentState;

/** Типы согласий. Список ведётся руками сознательно: в контракте это ключи словаря
 * (`dict[str, ConsentState]`), а не перечисление — сгенерированный тип даёт `string`.
 * Источник правды — `CONSENT_TYPES` в `app/core/legal.py`; расхождение ловит гейт
 * `tests/test_consents_ui_covers_all_types.py`. */
export type ConsentType = "personal_data" | "financial_data" | "marketing";

export type ConsentsMap = Record<ConsentType, ConsentState>;
