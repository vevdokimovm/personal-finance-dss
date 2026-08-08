/**
 * Заглушка под будущий i18n (docs/frontend_milestone8_plan.md, Шаг 2.2): все пользовательские
 * строки оборачиваются в t() сейчас, чтобы подключить реальную i18n-библиотеку позже без
 * прохода по всему дереву компонентов. Сегодня — тождественная функция, интерполяция позиционная.
 */
export function t(key: string, vars?: Record<string, string | number>): string {
  if (!vars) return key;
  return key.replace(/\{(\w+)\}/g, (match, name: string) =>
    name in vars ? String(vars[name]) : match,
  );
}
