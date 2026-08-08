/**
 * Вывод денег пользователю — правила из skill finpilot-money-format:
 * неразрывный пробел как разделитель разрядов, запятая как десятичный разделитель,
 * знак рубля после числа через неразрывный пробел, копейки скрыты при |sum| > 100 000 ₽,
 * отрицательные — минусом перед числом, не скобками.
 *
 * Форматирование — только на границе представления; бэкенд отдаёт число в рублях (не копейках),
 * округлённое до 2 знаков (round(x, 2) в routes_planning.py) — здесь их не пересчитываем.
 */
const NBSP = " ";

export function formatMoney(amount: number): string {
  const negative = amount < 0;
  const abs = Math.abs(amount);
  const hideKopecks = abs > 100_000;

  const fixed = hideKopecks ? Math.round(abs).toString() : abs.toFixed(2);
  const [intPart, fracPart] = fixed.split(".");

  const grouped = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, NBSP);
  const withFraction = fracPart !== undefined ? `${grouped},${fracPart}` : grouped;

  return `${negative ? "-" : ""}${withFraction}${NBSP}₽`;
}

/** Число без знака валюты — те же разделители, для показателей вроде Lt (месяцы). */
export function formatNumber(value: number, fractionDigits = 1): string {
  const fixed = value.toFixed(fractionDigits);
  const [intPart, fracPart] = fixed.split(".");
  const grouped = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, NBSP);
  return fracPart !== undefined ? `${grouped},${fracPart}` : grouped;
}

/** Проценты из доли (0.347 -> "34,7%"). */
export function formatPercent(fraction: number, fractionDigits = 1): string {
  return `${(fraction * 100).toFixed(fractionDigits).replace(".", ",")}%`;
}
