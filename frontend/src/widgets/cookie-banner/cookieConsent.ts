/**
 * Хранение выбора по cookie (L6).
 *
 * Живёт в `localStorage`, а не на сервере, и это осознанно: баннер показывается ГОСТЮ,
 * у которого ещё нет аккаунта, — писать его выбор в базу некуда и незачем. Само согласие
 * на аналитические cookie к обработке персональных данных отношения не имеет: это
 * настройка браузера конкретного человека на конкретном устройстве.
 *
 * 🔴 Значение хранится ВМЕСТЕ С ВЕРСИЕЙ политики. Смена редакции обнуляет выбор:
 * согласие даётся на конкретный текст, и молча переносить его на новую редакцию —
 * ровно то, за что штрафуют. Версия приходит из `/legal/documents`, а не зашита здесь.
 */
const STORAGE_KEY = "fp-cookie-consent";

export type CookieChoice = "all" | "necessary";

type Stored = {
  choice: CookieChoice;
  /** Версия политики cookie, на которую человек согласился. */
  version: string;
  /** ISO-дата выбора — нужна, чтобы показать, когда именно он сделан. */
  decidedAt: string;
};

/** Что выбрано для ТЕКУЩЕЙ редакции политики. `null` — выбора ещё нет. */
export function readCookieChoice(currentVersion: string): Stored | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as Partial<Stored>;
    if (parsed.choice !== "all" && parsed.choice !== "necessary") return null;
    if (typeof parsed.version !== "string" || parsed.version !== currentVersion) {
      // Редакция сменилась — прежний выбор к ней не относится, спрашиваем заново.
      return null;
    }
    return {
      choice: parsed.choice,
      version: parsed.version,
      decidedAt: typeof parsed.decidedAt === "string" ? parsed.decidedAt : "",
    };
  } catch {
    // Приватный режим, отключённое хранилище, испорченный JSON. Отсутствие выбора —
    // безопасное состояние: баннер покажется снова, лишние cookie не поставятся.
    return null;
  }
}

export function saveCookieChoice(choice: CookieChoice, version: string): void {
  try {
    const value: Stored = { choice, version, decidedAt: new Date().toISOString() };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(value));
  } catch {
    // Записать не вышло — выбор действует до перезагрузки. Молча: сообщать
    // пользователю о недоступности его же localStorage бессмысленно, сделать
    // с этим он ничего не может.
  }
}

/** Забыть выбор — «изменить решение» из футера. */
export function clearCookieChoice(): void {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch {
    // см. выше
  }
}
