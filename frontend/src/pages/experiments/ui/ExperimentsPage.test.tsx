import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
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
  Link: ({ children, to }: { children: React.ReactNode; to: string }) => <a href={to}>{children}</a>,
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
