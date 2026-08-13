import { describe, expect, it } from "vitest";
import { findMatchingAlternative, hasNonZeroCategory, notchesOf } from "./findMatchingAlternative";
import type { PlanAlternative } from "@entities/plan-summary";

const TOTAL = 39500;

function alt(
  id: string,
  x_obligations: number,
  x_reserve: number,
  x_goals: number,
): PlanAlternative {
  return {
    id,
    name: id,
    x_obligations,
    x_reserve,
    x_goals,
    utility: 0.5,
    Rt_new: 0,
    Lt_new: 1,
    Dt_new: 0.3,
  };
}

// Полная сетка 0/10/.../100 по долгу и целям, где сумма <= 100% (резерв — остаток).
const FULL_GRID: PlanAlternative[] = [];
for (let d = 0; d <= 10; d++) {
  for (let g = 0; g <= 10 - d; g++) {
    const r = 10 - d - g;
    FULL_GRID.push(alt(`a-${d}-${g}`, (TOTAL * d) / 10, (TOTAL * r) / 10, (TOTAL * g) / 10));
  }
}

describe("notchesOf", () => {
  it("округляет долю категории до ближайшей из 10 отметок сетки", () => {
    expect(notchesOf(alt("x", 11850, 15800, 11850), TOTAL)).toEqual({ debt: 3, goals: 3 });
  });
});

describe("hasNonZeroCategory", () => {
  it("false, если ни одна альтернатива не выделяет категории денег вовсе (нет обязательств/целей)", () => {
    const onlyReserve = [alt("a0100", 0, TOTAL, 0)];
    expect(hasNonZeroCategory(onlyReserve, "x_obligations")).toBe(false);
    expect(hasNonZeroCategory(onlyReserve, "x_goals")).toBe(false);
  });

  it("true, если хотя бы одна альтернатива выделяет категории ненулевую сумму", () => {
    expect(hasNonZeroCategory(FULL_GRID, "x_obligations")).toBe(true);
    expect(hasNonZeroCategory(FULL_GRID, "x_goals")).toBe(true);
  });
});

describe("findMatchingAlternative", () => {
  it("находит точное совпадение по отметкам долга/целей на полной сетке", () => {
    const match = findMatchingAlternative(FULL_GRID, TOTAL, 3, 4);
    expect(match).toBeDefined();
    expect(match!.x_obligations).toBeCloseTo((TOTAL * 3) / 10);
    expect(match!.x_goals).toBeCloseTo((TOTAL * 4) / 10);
    expect(match!.x_reserve).toBeCloseTo((TOTAL * 3) / 10);
  });

  it("undefined — точка не прошла отсев модели и отсутствует в ranked (не баг ползунка)", () => {
    // Урезанная сетка без всех точек с долгом >= 80% — как если бы модель отсеяла их по ПДН.
    const filtered = FULL_GRID.filter((a) => notchesOf(a, TOTAL).debt < 8);
    expect(findMatchingAlternative(filtered, TOTAL, 9, 0)).toBeUndefined();
  });

  it("undefined при total <= 0 — не делит на ноль", () => {
    expect(findMatchingAlternative(FULL_GRID, 0, 3, 3)).toBeUndefined();
  });
});
