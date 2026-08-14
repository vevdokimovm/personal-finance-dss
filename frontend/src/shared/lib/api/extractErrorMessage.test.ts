import { describe, expect, it } from "vitest";
import { extractErrorMessage } from "./extractErrorMessage";

describe("extractErrorMessage — текст ошибки API для пользователя", () => {
  it("HTTPException(detail=строка) — 400/401/403/409 — возвращает текст как есть", () => {
    expect(extractErrorMessage({ detail: "Неверный email или пароль." }, "запасной текст")).toBe(
      "Неверный email или пароль.",
    );
  });

  it("Pydantic 422 (detail — массив ValidationError) — берёт msg первой ошибки", () => {
    expect(
      extractErrorMessage(
        {
          detail: [{ msg: "String should have at least 8 characters", loc: ["body", "password"] }],
        },
        "запасной текст",
      ),
    ).toBe("String should have at least 8 characters");
  });

  it("сетевая ошибка / неопознанная форма — запасной текст, не падает", () => {
    expect(extractErrorMessage(new TypeError("Failed to fetch"), "запасной текст")).toBe(
      "запасной текст",
    );
    expect(extractErrorMessage(null, "запасной текст")).toBe("запасной текст");
    expect(extractErrorMessage(undefined, "запасной текст")).toBe("запасной текст");
  });

  it("detail — пустая строка или пустой массив — не выдаёт пустоту, запасной текст", () => {
    expect(extractErrorMessage({ detail: "" }, "запасной текст")).toBe("запасной текст");
    expect(extractErrorMessage({ detail: [] }, "запасной текст")).toBe("запасной текст");
  });
});
