import { describe, expect, it } from "vitest";
import { extractErrorMessage, getConsentRequiredDetail } from "./extractErrorMessage";

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

  it("гейт согласия (403, detail — объект {code, consent_type, document, message}) — message + ссылка на документ", () => {
    expect(
      extractErrorMessage(
        {
          detail: {
            code: "consent_required",
            consent_type: "financial_data",
            document: {
              title: "Согласие на обработку финансовых данных",
              version: "1.0",
              url: "/legal/financial-consent",
            },
            message:
              "Для работы с финансовыми данными нужно отдельное согласие на их обработку. Его можно дать в настройках профиля.",
          },
        },
        "запасной текст",
      ),
    ).toBe(
      "Для работы с финансовыми данными нужно отдельное согласие на их обработку. Его можно дать в настройках профиля. (/legal/financial-consent)",
    );
  });

  it("объектный detail без document.url — только message, без хвоста в скобках", () => {
    expect(
      extractErrorMessage(
        { detail: { code: "consent_required", message: "Нужно согласие." } },
        "запасной текст",
      ),
    ).toBe("Нужно согласие.");
  });

  it("объектный detail без message — запасной текст, не «[object Object]»", () => {
    expect(extractErrorMessage({ detail: { code: "consent_required" } }, "запасной текст")).toBe(
      "запасной текст",
    );
  });
});

describe("getConsentRequiredDetail — структурная сверка 403 гейта согласия (не текст)", () => {
  it("гейт согласия — возвращает consentType/message/documentTitle/documentUrl", () => {
    expect(
      getConsentRequiredDetail({
        detail: {
          code: "consent_required",
          consent_type: "financial_data",
          document: {
            title: "Согласие на обработку финансовых данных",
            version: "1.0",
            url: "/legal/financial-consent",
          },
          message: "Нужно согласие.",
        },
      }),
    ).toEqual({
      consentType: "financial_data",
      message: "Нужно согласие.",
      documentTitle: "Согласие на обработку финансовых данных",
      documentUrl: "/legal/financial-consent",
    });
  });

  it("объектный detail без document — documentTitle/documentUrl пустые строки, не падает", () => {
    expect(
      getConsentRequiredDetail({
        detail: { code: "consent_required", consent_type: "financial_data", message: "Нужно." },
      }),
    ).toEqual({
      consentType: "financial_data",
      message: "Нужно.",
      documentTitle: "",
      documentUrl: "",
    });
  });

  it("другой код ошибки (не consent_required) — null", () => {
    expect(getConsentRequiredDetail({ detail: { code: "other", message: "x" } })).toBeNull();
  });

  it("строковый detail (обычная HTTPException) — null", () => {
    expect(getConsentRequiredDetail({ detail: "Неверный пароль." })).toBeNull();
  });

  it("сетевая ошибка / null / undefined — null, не падает", () => {
    expect(getConsentRequiredDetail(new TypeError("Failed to fetch"))).toBeNull();
    expect(getConsentRequiredDetail(null)).toBeNull();
    expect(getConsentRequiredDetail(undefined)).toBeNull();
  });

  it("consent_required без consent_type/message — null (форма не годная для панели)", () => {
    expect(getConsentRequiredDetail({ detail: { code: "consent_required" } })).toBeNull();
  });
});
