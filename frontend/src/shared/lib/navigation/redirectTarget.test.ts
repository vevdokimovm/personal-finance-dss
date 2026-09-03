import { describe, expect, it } from "vitest";
import { safeRedirect } from "./redirectTarget";

describe("safeRedirect", () => {
  it("сохраняет внутренний путь вместе с параметрами — иначе теряется токен приглашения", () => {
    expect(safeRedirect("/join?token=abc123")).toBe("/join?token=abc123");
  });

  it("пусто — некуда возвращать", () => {
    expect(safeRedirect(null)).toBeNull();
    expect(safeRedirect(undefined)).toBeNull();
    expect(safeRedirect("")).toBeNull();
  });

  /* Открытый редирект: ссылка на своём домене, уводящая на чужой, — рабочая схема
     фишинга. Проверяем весь набор обходов, а не только очевидный http://. */
  it("внешние адреса отвергаются", () => {
    expect(safeRedirect("https://evil.example")).toBeNull();
    expect(safeRedirect("//evil.example")).toBeNull();
    expect(safeRedirect("/\\evil.example")).toBeNull();
    expect(safeRedirect("javascript:alert(1)")).toBeNull();
    expect(safeRedirect("\n/join")).toBeNull();
  });
});
