import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";
import { downloadFile, filenameFromDisposition } from "./downloadFile";

describe("filenameFromDisposition — имя файла даёт сервер, а не фронт", () => {
  it("берёт filename из заголовка", () => {
    expect(filenameFromDisposition('attachment; filename="finpilot-plan-2026-09-03.csv"'))
      .toBe("finpilot-plan-2026-09-03.csv");
  });

  it("понимает filename* с процентным кодированием (RFC 5987)", () => {
    expect(
      filenameFromDisposition("attachment; filename*=UTF-8''%D0%BF%D0%BB%D0%B0%D0%BD.csv"),
    ).toBe("план.csv");
  });

  it("filename* приоритетнее filename — он и заведён для не-ASCII", () => {
    expect(
      filenameFromDisposition(
        "attachment; filename=\"plan.csv\"; filename*=UTF-8''%D0%BF%D0%BB%D0%B0%D0%BD.csv",
      ),
    ).toBe("план.csv");
  });

  it("без заголовка возвращает null, а не выдуманное имя", () => {
    expect(filenameFromDisposition(null)).toBeNull();
    expect(filenameFromDisposition("attachment")).toBeNull();
  });
});

describe("downloadFile — скачивание с настоящей обработкой отказов", () => {
  const clicked: string[] = [];
  let createdUrls = 0;
  let revokedUrls = 0;

  beforeEach(() => {
    clicked.length = 0;
    createdUrls = 0;
    revokedUrls = 0;
    globalThis.URL.createObjectURL = vi.fn(() => {
      createdUrls += 1;
      return `blob:test-${createdUrls}`;
    });
    globalThis.URL.revokeObjectURL = vi.fn(() => {
      revokedUrls += 1;
    });
    vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(function (
      this: HTMLAnchorElement,
    ) {
      clicked.push(this.download);
    });
  });

  afterEach(() => vi.restoreAllMocks());

  function fetchOk(disposition = 'attachment; filename="plan.csv"') {
    return vi.fn(async () => ({
      ok: true,
      status: 200,
      headers: new Headers({ "Content-Disposition": disposition }),
      blob: async () => new Blob(["a;b"], { type: "text/csv" }),
      json: async () => ({}),
    })) as unknown as typeof fetch;
  }

  it("скачивает под именем, которое дал сервер", async () => {
    await downloadFile("/api/planning/export.csv", { fetchImpl: fetchOk() });
    expect(clicked).toEqual(["plan.csv"]);
  });

  it("подставляет запасное имя, если сервер его не дал", async () => {
    await downloadFile("/api/planning/export.csv", {
      fetchImpl: fetchOk("attachment"),
      fallbackName: "finpilot-plan.csv",
    });
    expect(clicked).toEqual(["finpilot-plan.csv"]);
  });

  it("освобождает blob-URL, но ОТЛОЖЕННО — синхронный revoke убивает скачивание", async () => {
    vi.useFakeTimers();
    try {
      await downloadFile("/api/planning/export.csv", { fetchImpl: fetchOk() });
      // Сразу после клика blob ещё жив: браузер только начинает скачивание.
      expect(revokedUrls).toBe(0);
      vi.runAllTimers();
      expect(revokedUrls).toBe(1);
    } finally {
      vi.useRealTimers();
    }
  });

  it("возвращает имя файла — экрану нужно назвать его в подтверждении", async () => {
    const name = await downloadFile("/api/planning/export.csv", { fetchImpl: fetchOk() });
    expect(name).toBe("plan.csv");
  });

  it("credentials: include — авторизация в HttpOnly cookie, без него 401", async () => {
    const spy = fetchOk();
    await downloadFile("/api/planning/export.csv", { fetchImpl: spy });
    expect(spy).toHaveBeenCalledWith(
      "/api/planning/export.csv",
      expect.objectContaining({ credentials: "include" }),
    );
  });

  /* 🔴 Главное, ради чего скачивание идёт через fetch, а не простой ссылкой: при
     отозванном согласии сервер отвечает 403 JSON-ом. Ссылка скачала бы этот JSON
     файлом с расширением .csv — пользователь получил бы «отчёт», внутри которого
     текст ошибки. Здесь отказ поднимается наверх и превращается в понятное сообщение. */
  it("403 не скачивается файлом, а поднимается как ошибка с телом", async () => {
    const detail = { code: "consent_required", consent_type: "financial_data" };
    const fetchForbidden = vi.fn(async () => ({
      ok: false,
      status: 403,
      headers: new Headers(),
      blob: async () => new Blob([]),
      json: async () => ({ detail }),
    })) as unknown as typeof fetch;

    await expect(
      downloadFile("/api/planning/export.csv", { fetchImpl: fetchForbidden }),
    ).rejects.toMatchObject({ status: 403, detail });
    expect(clicked).toEqual([]);
  });

  it("500 тоже не скачивается, а сообщает статус", async () => {
    const fetchFail = vi.fn(async () => ({
      ok: false,
      status: 500,
      headers: new Headers(),
      blob: async () => new Blob([]),
      json: async () => {
        throw new Error("не JSON");
      },
    })) as unknown as typeof fetch;

    await expect(
      downloadFile("/api/planning/export.csv", { fetchImpl: fetchFail }),
    ).rejects.toMatchObject({ status: 500 });
    expect(clicked).toEqual([]);
  });
});
