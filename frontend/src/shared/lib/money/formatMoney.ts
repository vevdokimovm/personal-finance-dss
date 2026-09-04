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

/**
 * @param fractionDigits — принудительная точность. По умолчанию действует порог
 * «копейки скрыты выше 100 000 ₽»: он осмыслен для ОДИНОЧНОГО числа, но для пары
 * однородных сумм рядом даёт разнобой — «Доходы: 180 000 ₽, расходы: 78 000,00 ₽»
 * читается как ошибка данных ([CMP-04], design-critic v8.43.0). Там, где суммы стоят
 * парой, точность задаётся явно и одинаково для обеих.
 */
export function formatMoney(amount: number, fractionDigits?: 0 | 2): string {
  const negative = amount < 0;
  const abs = Math.abs(amount);
  const hideKopecks = fractionDigits === undefined ? abs > 100_000 : fractionDigits === 0;

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
