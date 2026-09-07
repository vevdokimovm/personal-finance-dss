import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ExperimentsPage } from "./ExperimentsPage";

const { useExperimentsMock, useResultsMock, useProfileMock } = vi.hoisted(() => ({
  useExperimentsMock: vi.fn(),
  useResultsMock: vi.fn(),
  useProfileMock: vi.fn(),
}));

vi.mock("@entities/experiments", () => ({
  useExperiments: (enabled?: boolean) => useExperimentsMock(enabled),
  useExperimentResults: (keys: string[], enabled?: boolean) => useResultsMock(keys, enabled),
}));

vi.mock("@tanstack/react-router", () => ({
  Link: ({ children, to }: { children: React.ReactNode; to: string }) => (
    <a href={to}>{children}</a>
  ),
}));

vi.mock("@entities/profile", async () => {
  const actual = await vi.importActual<typeof import("@entities/profile")>("@entities/profile");
  return { ...actual, useProfile: () => useProfileMock() };
});

const EXPERIMENTS = [
  { key: "onboarding-copy", name: "Текст онбординга", status: "running", variants: [] },
];

/** Победитель с запасом: 20 % против 10 % на тысяче — разница реальная. */
const CLEAR_WINNER = {
  key: "onboarding-copy",
  status: "running",
  conversion_event: "plan_calculated",
  variants: [
    {
      variant: "control",
      assigned: 1000,
      converted: 100,
      conversion_rate: 0.1,
      is_control: true,
      uplift_pct: null,
      p_value: null,
      significant: false,
    },
    {
      variant: "short",
      assigned: 1000,
      converted: 200,
      conversion_rate: 0.2,
      is_control: false,
      uplift_pct: 100,
      p_value: 0.000001,
      significant: true,
    },
  ],
};

/** Шум: 12 % против 10 % на полусотне. Формально «больше», по существу — ничего. */
const NOISE = {
  key: "onboarding-copy",
  status: "running",
  conversion_event: "plan_calculated",
  variants: [
    {
      variant: "control",
      assigned: 50,
      converted: 5,
      conversion_rate: 0.1,
      is_control: true,
      uplift_pct: null,
      p_value: null,
      significant: false,
    },
    {
      variant: "short",
      assigned: 50,
      converted: 6,
      conversion_rate: 0.12,
      is_control: false,
      uplift_pct: 20,
      p_value: 0.74,
      significant: false,
    },
  ],
};

function idle<T>(data: T) {
  return { data, isLoading: false, isError: false, error: null };
}

beforeEach(() => {
  vi.clearAllMocks();
  useProfileMock.mockReturnValue(idle({ email: "owner@test.io", is_owner: true }));
  useExperimentsMock.mockReturnValue(idle(EXPERIMENTS));
  useResultsMock.mockReturnValue([idle(CLEAR_WINNER)]);
});

describe("ExperimentsPage — результаты A/B для владельца", () => {
  /* 🔴 Экран отвечает на ОДИН вопрос: катить вариант или нет. Таблица счётчиков
     этого не говорит, поэтому вывод стоит словами и первым. */
  it("называет победителя, когда разница значима", () => {
    render(<ExperimentsPage />);
    expect(screen.getByText(/Побеждает/)).toBeVisible();
    expect(screen.getAllByText(/short/).length).toBeGreaterThan(0);
  });

  /* 🔴 Главная защита экрана: на шуме победитель НЕ объявляется. Без этого
     владелец выкатит вариант по разнице, неотличимой от случайной. */
  it("на незначимой разнице говорит «данных мало», а не называет победителя", () => {
    useResultsMock.mockReturnValue([idle(NOISE)]);
    render(<ExperimentsPage />);
    expect(screen.queryByText(/Побеждает/)).not.toBeInTheDocument();
    expect(screen.getByText(/[Дд]анных пока мало|различить/)).toBeVisible();
  });

  it("показывает конверсию каждого варианта", () => {
    render(<ExperimentsPage />);
    expect(screen.getByText("10,0%")).toBeVisible();
    expect(screen.getByText("20,0%")).toBeVisible();
  });

  /* Контроль помечен: без этого непонятно, с чем сравнивают проценты. */
  it("помечает контрольный вариант", () => {
    render(<ExperimentsPage />);
    expect(screen.getByText(/контроль/i)).toBeVisible();
  });

  /* Не владельцу — отказ с выходом, как на экране метрик ([IA-02]). */
  it("не владельцу показывает отказ, а не пустую таблицу", () => {
    useProfileMock.mockReturnValue(idle({ email: "user@test.io", is_owner: false }));
    render(<ExperimentsPage />);
    expect(screen.getByRole("alert")).toHaveTextContent(/Раздел закрыт/);
    expect(screen.queryByText(/Побеждает/)).not.toBeInTheDocument();
  });

  /* 🔴 И запрос не уходит: сервер отдал бы 403 на каждый заход. Проверяется
     аргумент, а не разметка — мутация «запрашивать всегда» иначе проходит мимо. */
  it("не владельцу запросы не отправляются", () => {
    useProfileMock.mockReturnValue(idle({ email: "user@test.io", is_owner: false }));
    render(<ExperimentsPage />);
    expect(useExperimentsMock).toHaveBeenCalledWith(false);
  });

  it("во время загрузки показывает скелетон", () => {
    useExperimentsMock.mockReturnValue({ data: undefined, isLoading: true, isError: false });
    const { container } = render(<ExperimentsPage />);
    expect(container.querySelector(".fp-skeleton, [class*=skeleton]")).not.toBeNull();
  });

  it("отказ объяснён и предлагает повтор", () => {
    useExperimentsMock.mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
      error: new Error("network"),
      refetch: vi.fn(),
    });
    render(<ExperimentsPage />);
    expect(screen.getByText(/Не удалось загрузить/)).toBeVisible();
    expect(screen.getByRole("button", { name: /Повторить/ })).toBeVisible();
  });

  /* Пустой список — состояние нового продукта, а не сбой. */
  it("пустой список объяснён, а не показан пустой страницей", () => {
    useExperimentsMock.mockReturnValue(idle([]));
    useResultsMock.mockReturnValue([]);
    render(<ExperimentsPage />);
    expect(screen.getByText(/Экспериментов пока нет/)).toBeVisible();
  });
});

/**
 * Краевые случаи выбора победителя — непокрытый остаток экрана.
 *
 * 🔴 **Экран отвечает на вопрос «какой вариант лучше», и цена неверного ответа —
 * решение о продукте.** Значимость считает сервер (z-тест), но выбор победителя
 * из значимых делает фронт, и вот эти три случая он обязан пройти правильно:
 * победителя нет вовсе, «победа» с отрицательным приростом, несколько значимых.
 */
describe("ExperimentsPage — когда победителя нет или он не один", () => {
  it("🔴 значимый вариант с ОТРИЦАТЕЛЬНЫМ приростом победителем не считается", () => {
    /* Значимость говорит «разница не случайна», а не «стало лучше». Значимо худший
       вариант — это результат, но объявить его победителем значит предложить
       раскатать ухудшение на всех. */
    useResultsMock.mockReturnValue([
      {
        data: {
          ...CLEAR_WINNER,
          variants: [
            { ...CLEAR_WINNER.variants[0] },
            {
              ...CLEAR_WINNER.variants[1],
              conversion_rate: 0.05,
              uplift_pct: -50,
              significant: true,
            },
          ],
        },
        isLoading: false,
        error: null,
      },
    ]);
    render(<ExperimentsPage />);

    expect(screen.queryByText(/победител|выигрыв/i)).not.toBeInTheDocument();
  });

  it("из двух значимых выбирается тот, у кого прирост больше", () => {
    useResultsMock.mockReturnValue([
      {
        data: {
          ...CLEAR_WINNER,
          variants: [
            { ...CLEAR_WINNER.variants[0] },
            { ...CLEAR_WINNER.variants[1], variant: "short", uplift_pct: 40, significant: true },
            { ...CLEAR_WINNER.variants[1], variant: "long", uplift_pct: 90, significant: true },
          ],
        },
        isLoading: false,
        error: null,
      },
    ]);
    render(<ExperimentsPage />);

    /* Ищем ВЕРДИКТ, а не любое вхождение имени: вариант перечислен ещё
       и в таблице, и `getByText(/long/)` падает на неоднозначности. */
    expect(screen.getByText(/Побеждает вариант «long»/)).toBeInTheDocument();
  });

  it("эксперимент без вариантов не роняет экран", () => {
    /* Только что заведённый эксперимент — обычное состояние, а не ошибка:
       данные появятся, когда через него пройдут люди. */
    useResultsMock.mockReturnValue([
      {
        data: { key: "onboarding-copy", status: "running", variants: undefined },
        isLoading: false,
        error: null,
      },
    ]);
    expect(() => render(<ExperimentsPage />)).not.toThrow();
  });

  it("пока грузятся результаты — скелетон, а не пустое место", () => {
    useResultsMock.mockReturnValue([{ data: undefined, isLoading: true, error: null }]);
    render(<ExperimentsPage />);
    expect(screen.getByRole("status")).toBeInTheDocument();
  });

  it("пока грузится профиль — экран не решает, владелец перед ним или нет", () => {
    /* Показать «нет доступа» до того, как известно, кто смотрит, значит выгнать
       владельца с его же экрана на секунду загрузки. */
    useProfileMock.mockReturnValue({ data: undefined, isLoading: true, error: null });
    render(<ExperimentsPage />);
    expect(screen.queryByText(/нет доступа|только владельц/i)).not.toBeInTheDocument();
  });
});

describe("ExperimentsPage — незнакомые значения и отказы загрузки", () => {
  it("🔴 неизвестный статус показывается как есть, а не пропадает", () => {
    /* `STATUS_LABELS[...] ?? status` — карта переводов пишется руками и всегда
       отстаёт от бэкенда на один релиз. Показать сырой код хуже перевода,
       но несравнимо лучше пустоты: владелец хотя бы увидит, что статус есть. */
    useResultsMock.mockReturnValue([
      { data: { ...CLEAR_WINNER, status: "paused_by_owner" }, isLoading: false, error: null },
    ]);
    render(<ExperimentsPage />);
    expect(screen.getByText(/paused_by_owner/)).toBeInTheDocument();
  });

  it("эксперимент без имени подписан ключом", () => {
    /* `name || results.key` — имя необязательно; ключ есть всегда и однозначен. */
    useExperimentsMock.mockReturnValue({
      data: [{ key: "onboarding-copy", name: "", status: "running", variants: [] }],
      isLoading: false,
      error: null,
    });
    render(<ExperimentsPage />);
    // Ключ встречается и в заголовке, и в подписи ниже — берём заголовок.
    expect(screen.getByRole("heading", { name: "onboarding-copy" })).toBeInTheDocument();
  });

  it("сбой загрузки списка даёт повтор", async () => {
    const refetch = vi.fn();
    useExperimentsMock.mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
      error: new Error("500"),
      refetch,
    });
    useResultsMock.mockReturnValue([]);
    render(<ExperimentsPage />);

    await userEvent.click(screen.getByRole("button", { name: /Повторить/ }));
    expect(refetch).toHaveBeenCalled();
  });

  it("сбой результатов ОДНОГО эксперимента не роняет остальные", async () => {
    /* Результаты грузятся по одному запросу на эксперимент. Общий экран ошибки
       спрятал бы работающие эксперименты за отказом одного. */
    const refetch = vi.fn();
    useResultsMock.mockReturnValue([{ data: undefined, isLoading: false, isError: true, refetch }]);
    render(<ExperimentsPage />);

    await userEvent.click(screen.getByRole("button", { name: /Повторить/ }));
    expect(refetch).toHaveBeenCalled();
  });
});
