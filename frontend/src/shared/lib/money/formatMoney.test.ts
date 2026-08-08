import { describe, expect, it } from "vitest";
import { formatMoney, formatNumber, formatPercent } from "./formatMoney";

describe("formatMoney", () => {
  it("разделяет разряды неразрывным пробелом и ставит ₽ после числа", () => {
    expect(formatMoney(39500)).toBe("39 500,00 ₽");
  });

  it("показывает копейки запятой, когда сумма не превышает 100 000 ₽", () => {
    expect(formatMoney(1234.56)).toBe("1 234,56 ₽");
  });

  it("скрывает копейки, когда |сумма| больше 100 000 ₽", () => {
    expect(formatMoney(474000)).toBe("474 000 ₽");
  });

  it("округляет по ROUND_HALF_UP при скрытых копейках", () => {
    expect(formatMoney(474000.5)).toBe("474 001 ₽");
  });

  it("отрицательные суммы — минусом перед числом, не скобками", () => {
    expect(formatMoney(-3000)).toBe("-3 000,00 ₽");
  });

  it("отрицательные суммы выше порога тоже скрывают копейки", () => {
    expect(formatMoney(-150000)).toBe("-150 000 ₽");
  });

  it("ноль форматируется без минуса", () => {
    expect(formatMoney(0)).toBe("0,00 ₽");
  });
});

describe("formatNumber", () => {
  it("форматирует с одним знаком после запятой по умолчанию", () => {
    expect(formatNumber(3.4)).toBe("3,4");
  });

  it("группирует тысячи так же, как деньги", () => {
    expect(formatNumber(66000, 0)).toBe("66 000");
  });
});

describe("formatPercent", () => {
  it("конвертирует долю в проценты с запятой", () => {
    expect(formatPercent(0.347)).toBe("34,7%");
  });

  it("на пороге ПДН даёт ровно 40%", () => {
    expect(formatPercent(0.4)).toBe("40,0%");
  });
});
