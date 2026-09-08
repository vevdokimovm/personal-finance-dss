import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ConsentsSection } from "./ConsentsSection";

const { useConsentsMock, useLegalMock, grantMock, withdrawMock, toastError, toastUndo } =
  vi.hoisted(() => ({
    useConsentsMock: vi.fn(),
    useLegalMock: vi.fn(),
    grantMock: vi.fn(),
    withdrawMock: vi.fn(),
    toastError: vi.fn(),
    toastUndo: vi.fn(),
  }));

vi.mock("@entities/consents", () => ({
  useConsents: () => useConsentsMock(),
  useGrantConsent: () => ({ mutate: grantMock, isPending: false }),
  useWithdrawConsent: () => ({ mutate: withdrawMock, isPending: false }),
}));

vi.mock("@entities/legal", () => ({ useLegalDocuments: () => useLegalMock() }));

/* `SessionExpiredPanel` внутри секции ведёт человека на `/login` через `Link`, а тот
   без роутера падает на `isServer`. Тест проверяет НАЛИЧИЕ выхода, а не работу роутера —
   поэтому ссылка подменяется простым якорем, как в `SessionExpiredPanel.test.tsx`. */
vi.mock("@tanstack/react-router", async () => {
  const actual =
    await vi.importActual<typeof import("@tanstack/react-router")>("@tanstack/react-router");
  return {
    ...actual,
    Link: ({ children, to }: { children: React.ReactNode; to: string }) => (
      <a href={to}>{children}</a>
    ),
  };
});

vi.mock("@shared/ui", async () => {
  const actual = await vi.importActual<typeof import("@shared/ui")>("@shared/ui");
  return { ...actual, toast: { ...actual.toast, error: toastError, undo: toastUndo } };
});

/** Все три типа, как их отдаёт `/consents` — включая невыданные. */
const ALL_CONSENTS = {
  personal_data: {
    granted: true,
    version: "1.0",
    granted_at: "2026-01-15T10:00:00",
    withdrawable: false,
  },
  financial_data: { granted: false, version: "1.0", granted_at: null, withdrawable: true },
  marketing: {
    granted: true,
    version: "1.0",
    granted_at: "2026-02-01T10:00:00",
    withdrawable: true,
  },
};

const LEGAL = {
  documents: {
    personal_data: {
      title: "Согласие на обработку персональных данных",
      version: "1.0",
      effective_from: "2026-07-29",
      url: "/legal/consent",
    },
    financial_data: {
      title: "Согласие на обработку финансовых данных",
      version: "1.0",
      effective_from: "2026-07-29",
      url: "/legal/financial-consent",
    },
    marketing: {
      title: "Согласие на рекламную рассылку",
      version: "1.0",
      effective_from: "2026-07-29",
      url: "/legal/marketing-consent",
    },
  },
  disclaimer_39fz: "FINPILOT не является инвестиционным советником.",
};

beforeEach(() => {
  vi.clearAllMocks();
  useConsentsMock.mockReturnValue({ data: ALL_CONSENTS, isLoading: false, isError: false });
  useLegalMock.mockReturnValue({ data: LEGAL, error: null, isLoading: false });
});

describe("ConsentsSection — требование L3", () => {
  /* 🔴 Первая редакция знала ровно ОДНО согласие — `financial_data`. Остальные два
     человек не видел вовсе: отозвать маркетинговое было невозможно, хотя 152-ФЗ даёт
     на это право. */
  it("показывает ВСЕ согласия, а не одно", () => {
    render(<ConsentsSection />);
    expect(screen.getByText("Персональные данные")).toBeVisible();
    expect(screen.getByText("Финансовые данные")).toBeVisible();
    expect(screen.getByText("Рекламная рассылка")).toBeVisible();
  });

  it("новый тип согласия появляется сам, без правки кода", () => {
    useConsentsMock.mockReturnValue({
      data: {
        ...ALL_CONSENTS,
        biometrics: { granted: false, version: "1.0", granted_at: null, withdrawable: true },
      },
      isLoading: false,
      isError: false,
    });
    render(<ConsentsSection />);
    // Названия для нового типа ещё нет — показываем ключ, но НЕ прячем строку:
    // спрятанное согласие человек не сможет ни выдать, ни отозвать.
    expect(screen.getByText("biometrics")).toBeVisible();
  });

  it("статус передан словом, а не только цветом бейджа (A11Y-07)", () => {
    render(<ConsentsSection />);
    expect(screen.getByText("Не дано")).toHaveClass("fp-profile__badge");
    expect(screen.getAllByText("Дано")).toHaveLength(2);
  });

  it("ссылка на документ ведёт по адресу из реестра, а не зашита в код", () => {
    render(<ConsentsSection />);
    expect(screen.getByRole("link", { name: /Согласие на обработку финансовых/ })).toHaveAttribute(
      "href",
      "/legal/financial-consent",
    );
    expect(screen.getByRole("link", { name: /рекламную рассылку/ })).toHaveAttribute(
      "href",
      "/legal/marketing-consent",
    );
  });

  it("выдача согласия уходит с нужным типом", async () => {
    render(<ConsentsSection />);
    await userEvent.click(screen.getByRole("button", { name: /Дать согласие: Финансовые/ }));
    expect(grantMock.mock.calls[0][0]).toBe("financial_data");
  });

  it("отзыв согласия уходит с нужным типом", async () => {
    render(<ConsentsSection />);
    await userEvent.click(screen.getByRole("button", { name: /Отозвать согласие: Рекламная/ }));
    expect(withdrawMock.mock.calls[0][0]).toBe("marketing");
  });

  /* Согласие-основание отозвать нельзя иначе как удалением аккаунта — сервер ответит
     409. Кнопка, которая гарантированно откажет, это тупик ([IA-04]). */
  it("у неотзываемого согласия кнопки отзыва нет, но есть объяснение", () => {
    render(<ConsentsSection />);
    expect(
      screen.queryByRole("button", { name: /Отозвать согласие: Персональные/ }),
    ).not.toBeInTheDocument();
    expect(screen.getByText(/нельзя отозвать без удаления аккаунта/)).toBeVisible();
  });

  it("отзыв предлагает отмену — он закрывает шесть роутеров разом", async () => {
    withdrawMock.mockImplementation((_type, opts) => opts?.onSuccess?.());
    render(<ConsentsSection />);
    await userEvent.click(screen.getByRole("button", { name: /Отозвать согласие: Рекламная/ }));
    expect(toastUndo).toHaveBeenCalled();
    toastUndo.mock.calls[0][1]();
    expect(grantMock.mock.calls[0][0]).toBe("marketing");
  });

  it("редакция документа видна — согласие даётся на конкретный текст", () => {
    render(<ConsentsSection />);
    expect(screen.getAllByText("ред. 1.0")).toHaveLength(3);
  });

  it("согласия ещё грузятся — блок не падает и кнопок нет", () => {
    useConsentsMock.mockReturnValue({ data: undefined, isLoading: true, isError: false });
    render(<ConsentsSection />);
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });

  /* Реестр документов — второстепенный источник: без него статусы и кнопки обязаны
     работать, пропадают только ссылки на тексты. */
  it("без реестра документов согласия всё равно управляемы", () => {
    useLegalMock.mockReturnValue({ data: undefined, error: new Error("500"), isLoading: false });
    render(<ConsentsSection />);
    expect(screen.getByRole("button", { name: /Дать согласие: Финансовые/ })).toBeVisible();
  });
});

/**
 * Ветки отказа — непокрытый остаток секции.
 *
 * 🔴 **Отзыв согласия на финданные закрывает шесть роутеров разом** (`_FIN`).
 * Если запрос упал, а мы промолчали, человек уверен, что отозвал, — и продолжает
 * пользоваться продуктом, считая свои данные защищёнными. Это не UX-мелочь,
 * а расхождение между тем, что он решил, и тем, что произошло.
 */
describe("ConsentsSection — что видно, когда действие не удалось", () => {
  it("отказ при выдаче согласия сообщается", async () => {
    useConsentsMock.mockReturnValue({ data: ALL_CONSENTS, isLoading: false, error: null });
    grantMock.mockImplementation((_type: string, opts?: { onError?: () => void }) =>
      opts?.onError?.(),
    );
    render(<ConsentsSection />);

    await userEvent.click(screen.getByRole("button", { name: /Дать согласие: Финансовые/ }));
    expect(toastError).toHaveBeenCalled();
  });

  it("🔴 отказ при отзыве сообщается — иначе человек думает, что отозвал", async () => {
    useConsentsMock.mockReturnValue({ data: ALL_CONSENTS, isLoading: false, error: null });
    withdrawMock.mockImplementation((_type: string, opts?: { onError?: () => void }) =>
      opts?.onError?.(),
    );
    render(<ConsentsSection />);

    await userEvent.click(screen.getByRole("button", { name: /Отозвать согласие: Рекламная/ }));
    expect(toastError).toHaveBeenCalled();
    expect(toastUndo).not.toHaveBeenCalled();
  });

  it("🔴 отказ при ВОССТАНОВЛЕНИИ через «Вернуть» тоже сообщается", async () => {
    /* Кнопка отмены создаёт впечатление обратимости. Если восстановление упало
       молча, человек уверен, что согласие вернулось, и не даст его заново —
       а шесть роутеров останутся закрытыми. */
    useConsentsMock.mockReturnValue({ data: ALL_CONSENTS, isLoading: false, error: null });
    withdrawMock.mockImplementation((_type: string, opts?: { onSuccess?: () => void }) =>
      opts?.onSuccess?.(),
    );
    grantMock.mockImplementation((_type: string, opts?: { onError?: () => void }) =>
      opts?.onError?.(),
    );
    render(<ConsentsSection />);

    await userEvent.click(screen.getByRole("button", { name: /Отозвать согласие: Рекламная/ }));
    expect(toastUndo).toHaveBeenCalled();
    // Нажимаем «Вернуть» — ToastProvider в юнит-тесте не смонтирован, зовём обработчик.
    toastUndo.mock.calls[0][1]();
    expect(toastError).toHaveBeenCalled();
  });
});

describe("ConsentsSection — ошибка не прячет право по 152-ФЗ молча", () => {
  /* 🔴 Гипотеза 4 независимого эксперта, 08.09.2026.
     Было: `if (query.isLoading || query.isError || !query.data) return null` —
     блок управления согласиями исчезал при ЛЮБОЙ ошибке, без единого слова.

     Это единственный путь отзыва согласия в интерфейсе, и `routes_consents.py`
     прямо пишет: невозможность отозвать согласие — нарушение 152-ФЗ, а не дефект
     интерфейса. Молчаливое исчезновение хуже ошибки: человек не понимает, что
     функция вообще существует, и не может отличить «права нет» от «сеть моргнула». */

  beforeEach(() => {
    useLegalMock.mockReturnValue({ data: [], isLoading: false });
  });

  it("🔴 при истёкшей сессии объясняет и даёт выход, а не исчезает", () => {
    useConsentsMock.mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
      error: { status: 401 },
    });

    render(<ConsentsSection />);

    expect(screen.getByText(/Сессия истекла/)).toBeInTheDocument();
  });

  it("🔴 при обычной ошибке говорит об этом и даёт повторить", async () => {
    const refetch = vi.fn();
    useConsentsMock.mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
      error: { status: 500 },
      refetch,
    });

    render(<ConsentsSection />);

    expect(screen.getByRole("alert")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: /Повторить/ }));
    expect(refetch).toHaveBeenCalled();
  });

  it("во время загрузки не показывает ни ошибку, ни пустоту", () => {
    useConsentsMock.mockReturnValue({ data: undefined, isLoading: true, isError: false });

    render(<ConsentsSection />);

    expect(screen.queryByRole("alert")).toBeNull();
  });
});

describe("ConsentsSection — устаревшая редакция видна и подтверждается", () => {
  /* 🔴 Шестой случай класса `CONSENT-GATE-NO-UI`, найден третьим проходом аудита
     08.09.2026 — через СУТКИ после того, как он был заведён предыдущим батчем.

     v9.6.0 научил бэкенд считать `is_current`/`current_version` и положил их
     в контракт «чтобы фронт показал». Фронт не показывал: экран печатал
     `ред. {state.version}` — редакцию, на которую человек когда-то согласился, —
     и ничем не отличал её от действующей.

     Полутора десятков версий на этот раз не понадобилось: хватило одного дня.
     Значит дело не в забывчивости, а в отсутствии механической сверки — и гейт,
     заведённый в тот же день против этого класса, схему `ConsentState` в периметр
     не включал. */

  beforeEach(() => {
    useLegalMock.mockReturnValue({ data: LEGAL, error: null, isLoading: false });
  });

  const OUTDATED = {
    ...ALL_CONSENTS,
    personal_data: {
      ...ALL_CONSENTS.personal_data,
      version: "1.0",
      current_version: "2.0",
      is_current: false,
    },
  };

  it("🔴 говорит, что согласие дано на прежнюю редакцию", () => {
    useConsentsMock.mockReturnValue({ data: OUTDATED, isLoading: false, isError: false });

    render(<ConsentsSection />);

    expect(screen.getByText(/действует ред\. 2\.0/i)).toBeInTheDocument();
  });

  it("🔴 даёт подтвердить новую редакцию — иначе расхождение неустранимо", async () => {
    /* Для `personal_data` обходного пути нет вовсе: тип неотзываемый, отозвать
       и выдать заново нельзя. Кнопка здесь — единственный выход. */
    useConsentsMock.mockReturnValue({ data: OUTDATED, isLoading: false, isError: false });

    render(<ConsentsSection />);

    const confirm = screen.getByRole("button", {
      name: /Подтвердить новую редакцию: Персональные данные/,
    });
    await userEvent.click(confirm);
    expect(grantMock).toHaveBeenCalledWith("personal_data", expect.anything());
  });

  it("на актуальной редакции лишнего не показывает", () => {
    const current = {
      ...ALL_CONSENTS,
      personal_data: {
        ...ALL_CONSENTS.personal_data,
        current_version: "1.0",
        is_current: true,
      },
    };
    useConsentsMock.mockReturnValue({ data: current, isLoading: false, isError: false });

    render(<ConsentsSection />);

    expect(screen.queryByText(/действует ред\./i)).toBeNull();
    expect(screen.queryByRole("button", { name: /Подтвердить новую редакцию/ })).toBeNull();
  });

  it("старый ответ без новых полей не ломает экран", () => {
    /* Совместимость: ответ, собранный до v9.6.0, полей не несёт — экран обязан
       работать как раньше, а не решать, что всё устарело. */
    useConsentsMock.mockReturnValue({ data: ALL_CONSENTS, isLoading: false, isError: false });

    render(<ConsentsSection />);

    expect(screen.queryByText(/действует ред\./i)).toBeNull();
  });
});

describe("ConsentsSection — отзыв не исчезает при смене редакции", () => {
  /* 🔴 Дефект, внесённый ЧАСОМ РАНЬШЕ в этом же батче и найденный четвёртым проходом
     аудита. Ветка «Подтвердить новую редакцию» поглощала ветку отзыва: пока
     `is_current === false`, отозвать маркетинговое или финансовое согласие из
     интерфейса было нельзя вообще — единственная кнопка предлагала согласиться ещё раз.

     Условие писалось «под personal_data» (тип неотзываемый, у него отзыва и нет),
     но типов не различало, а `withdrawable` в этой ветке не читался вовсе.

     🔴 Шапка этого же файла описывает ровно такой дефект как уже случившийся:
     «отозвать маркетинговое было невозможно, хотя 152-ФЗ даёт на это право». Он
     вернулся — теперь условно, по флагу расхождения редакций. Регулятор читает это
     как понуждение к повторному согласию: чтобы отозвать, сначала согласись заново. */

  beforeEach(() => {
    useLegalMock.mockReturnValue({ data: LEGAL, error: null, isLoading: false });
  });

  const OUTDATED_WITHDRAWABLE = {
    ...ALL_CONSENTS,
    marketing: {
      ...ALL_CONSENTS.marketing,
      version: "1.0",
      current_version: "2.0",
      is_current: false,
    },
  };

  it("🔴 отзываемое согласие можно отозвать и при устаревшей редакции", () => {
    useConsentsMock.mockReturnValue({
      data: OUTDATED_WITHDRAWABLE,
      isLoading: false,
      isError: false,
    });

    render(<ConsentsSection />);

    expect(
      screen.getByRole("button", { name: /Отозвать согласие: Рекламная рассылка/ }),
    ).toBeInTheDocument();
  });

  it("и подтвердить новую редакцию — тоже, оба действия доступны сразу", () => {
    useConsentsMock.mockReturnValue({
      data: OUTDATED_WITHDRAWABLE,
      isLoading: false,
      isError: false,
    });

    render(<ConsentsSection />);

    expect(
      screen.getByRole("button", { name: /Подтвердить новую редакцию: Рекламная рассылка/ }),
    ).toBeInTheDocument();
  });

  it("у неотзываемого типа кнопки отзыва по-прежнему нет", () => {
    /* `personal_data` отозвать нельзя иначе как удалением аккаунта — кнопка там
       гарантированно дала бы 409, то есть тупик. */
    const outdatedPersonal = {
      ...ALL_CONSENTS,
      personal_data: {
        ...ALL_CONSENTS.personal_data,
        current_version: "2.0",
        is_current: false,
      },
    };
    useConsentsMock.mockReturnValue({
      data: outdatedPersonal,
      isLoading: false,
      isError: false,
    });

    render(<ConsentsSection />);

    expect(
      screen.queryByRole("button", { name: /Отозвать согласие: Персональные данные/ }),
    ).toBeNull();
  });
});

describe("ConsentsSection — все сочетания состояния дают действие", () => {
  /* 🔴 Перебор вместо примеров. Ветвление переписывалось дважды за час, и первый раз
     дало состояние без единого действия (кнопка отзыва исчезала при устаревшей
     редакции). Перечисление сочетаний ловит такое механически, а не по догадке
     о том, какой случай проверить. */

  beforeEach(() => {
    useLegalMock.mockReturnValue({ data: LEGAL, error: null, isLoading: false });
  });

  const CASES: Array<[boolean, boolean, boolean]> = [];
  for (const granted of [true, false]) {
    for (const isCurrent of [true, false]) {
      for (const withdrawable of [true, false]) {
        CASES.push([granted, isCurrent, withdrawable]);
      }
    }
  }

  it.each(CASES)(
    "granted=%s is_current=%s withdrawable=%s — человеку есть что сделать",
    (granted, isCurrent, withdrawable) => {
      useConsentsMock.mockReturnValue({
        data: {
          ...ALL_CONSENTS,
          marketing: {
            granted,
            version: "1.0",
            current_version: isCurrent ? "1.0" : "2.0",
            is_current: isCurrent,
            granted_at: granted ? "2026-02-01T10:00:00" : null,
            withdrawable,
          },
        },
        isLoading: false,
        isError: false,
      });

      render(<ConsentsSection />);

      const marketingActions = [
        ...screen.queryAllByRole("button", { name: /Рекламная рассылка/ }),
      ];
      /* `queryAllByText`, а не `queryByText`: подсказку про неотзываемое согласие
         показывает и `personal_data`, и множественное совпадение бросало бы
         исключение — тест падал бы на собственной ошибке, а не на дефекте. */
      const hints = screen.queryAllByText(/нельзя отозвать без удаления аккаунта/);
      expect(
        marketingActions.length > 0 || hints.length > 0,
        `состояние granted=${granted} is_current=${isCurrent} ` +
          `withdrawable=${withdrawable} не даёт ни одного действия и не объясняет почему`,
      ).toBe(true);
    },
  );

  it("🔴 двух primary-кнопок рядом не бывает", () => {
    /* Подтверждение редакции и «Дать согласие» — обе primary. Если бы они могли
       появиться вместе, экран предлагал бы два одинаково выглядящих действия
       с разным смыслом. */
    useConsentsMock.mockReturnValue({
      data: {
        ...ALL_CONSENTS,
        marketing: {
          granted: false,
          version: "1.0",
          current_version: "2.0",
          is_current: false,
          granted_at: null,
          withdrawable: true,
        },
      },
      isLoading: false,
      isError: false,
    });

    render(<ConsentsSection />);

    expect(
      screen.queryByRole("button", { name: /Подтвердить новую редакцию: Рекламная/ }),
    ).toBeNull();
    expect(
      screen.getByRole("button", { name: /Дать согласие: Рекламная рассылка/ }),
    ).toBeInTheDocument();
  });
});
