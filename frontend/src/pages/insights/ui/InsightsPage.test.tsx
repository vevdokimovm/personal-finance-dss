import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { InsightsPage } from "./InsightsPage";

const { useOverviewMock, useFunnelMock, useProfileMock } = vi.hoisted(() => ({
  useOverviewMock: vi.fn(),
  useFunnelMock: vi.fn(),
  useProfileMock: vi.fn(),
}));

vi.mock("@entities/insights", () => ({
  useAnalyticsOverview: (enabled?: boolean) => useOverviewMock(enabled),
  useFunnel: (enabled?: boolean) => useFunnelMock(enabled),
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

const OVERVIEW = {
  period_days: 30,
  total_events: 1284,
  active_users: 37,
  event_counts: { login_success: 210, goal_created: 44, plan_calculated: 180 },
};

const FUNNEL = {
  period_days: 30,
  steps: [
    { step: "login_success", users: 100, conversion_pct: 100 },
    { step: "obligation_created", users: 62, conversion_pct: 62 },
    { step: "goal_created", users: 31, conversion_pct: 31 },
  ],
};

function idle<T>(data: T) {
  return { data, isLoading: false, isError: false, error: null };
}

beforeEach(() => {
  vi.clearAllMocks();
  useProfileMock.mockReturnValue(idle({ email: "owner@test.io", is_owner: true }));
  useOverviewMock.mockReturnValue(idle(OVERVIEW));
  useFunnelMock.mockReturnValue(idle(FUNNEL));
});

describe("InsightsPage — метрики продукта для владельца", () => {
  it("показывает сводку за период", () => {
    render(<InsightsPage />);
    /* 🔴 Люди и события — ЦЕЛЫЕ. `formatNumber` по умолчанию даёт одну десятую,
       и на экране стояло «37,0 активных пользователей»: считаемые сущности дробными
       не бывают, а в финтехе такое число убивает доверие ко всем остальным
       (design-critic). Регулярка `/37/` это пропускала — проверяем точный текст. */
    expect(screen.getByText("37")).toBeVisible();
    // Разряды разделены НЕРАЗРЫВНЫМ пробелом (`formatNumber`), и `toHaveTextContent`
    // его нормализует — сравниваем через собственный матчер по узлу.
    expect(
      screen.getByText((_, el) => el?.textContent === "1\u00a0284" && el.tagName === "DD"),
    ).toBeVisible();
  });

  /* 🔴 Воронка нужна не числами, а РАЗНИЦЕЙ между шагами: место, где отваливаются,
     и есть ответ на вопрос «что чинить». Проценты от первого шага показывает сервер. */
  it("показывает шаги воронки с конверсией", () => {
    render(<InsightsPage />);
    // «62 человека» есть и в ответе «где теряем», и в строке воронки — это ожидаемо.
    expect(screen.getAllByText(/62 человека/).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/31 человек/).length).toBeGreaterThan(0);
  });

  /* 🔴 Экран отвечает на вопрос «где теряем», а не показывает три ряда чисел.
     Потеря между шагами вычисляется здесь, а не в уме владельца (design-critic). */
  it("называет шаг с наибольшей потерей", () => {
    render(<InsightsPage />);
    // 100 → 62 это −38, 62 → 31 это −31: худший шаг первый переход.
    expect(screen.getByText(/Больше всего теряем/)).toBeVisible();
    // Название худшего шага — в блоке ответа; в воронке оно же, поэтому берём все.
    expect(screen.getAllByText(/Добавлен кредит/).length).toBeGreaterThan(0);
    // И потеря ПОСЧИТАНА, а не оставлена владельцу в уме: 100 → 62 это −38.
    expect(screen.getByText(/Не дошли 38 человек/)).toBeVisible();
  });

  /* Единица измерения обязательна: «Вход в аккаунт» в воронке это ЛЮДИ, а в списке
     событий — СОБЫТИЯ, и одна подпись над двумя разными числами читается как
     противоречие ([CMP-04]). */
  it("события и люди подписаны разными единицами", () => {
    render(<InsightsPage />);
    // «210 раз» — событие; «100 человек» — люди. Одна подпись над разными числами
    // без единиц читалась как противоречие.
    expect(screen.getByText("210 раз")).toBeVisible();
  });

  /* Подпись периода обязана соответствовать посчитанному. До v8.48.0 воронка считалась
     за всю историю, а над ней стояло «за последние 30 дней». */
  it("период воронки берётся из ответа, а не подразумевается", () => {
    useFunnelMock.mockReturnValue(idle({ ...FUNNEL, period_days: 7 }));
    render(<InsightsPage />);
    expect(screen.getByText(/7 дней/)).toBeVisible();
  });

  /* Названия событий приходят машинными (`login_success`) — для владельца продукта
     это читаемо, но по-русски понятнее, и перевод не мешает узнать исходный ключ. */
  it("переводит известные шаги на человеческий язык", () => {
    render(<InsightsPage />);
    // Название встречается и в воронке, и в списке событий — это ожидаемо,
    // поэтому проверяется наличие хотя бы одного, а не единственность.
    expect(screen.getAllByText(/Вход в аккаунт/).length).toBeGreaterThan(0);
  });

  /* Незнакомое событие показывается машинным ключом, а не пустотой: новый тип
     появляется в коде раньше, чем в словаре перевода. */
  it("неизвестный шаг показан ключом, а не пропущен", () => {
    useFunnelMock.mockReturnValue(
      idle({ steps: [{ step: "brand_new_event", users: 5, conversion_pct: 100 }] }),
    );
    render(<InsightsPage />);
    expect(screen.getByText("brand_new_event")).toBeVisible();
  });

  /* 🔴 Не владельцу экрана быть не должно: сервер отдаёт 403, и показывать страницу,
     которая гарантированно упрётся в отказ, — кнопка в тупик ([IA-04]). */
  it("не владельцу показывает отказ, а не пустые графики", () => {
    useProfileMock.mockReturnValue(idle({ email: "user@test.io", is_owner: false }));
    render(<InsightsPage />);
    expect(screen.getByText(/только владельцу продукта/)).toBeVisible();
    expect(screen.queryByText(/Больше всего теряем/)).not.toBeInTheDocument();
  });

  /* 🔴 И запрос НЕ уходит: сервер отдал бы 403, то есть каждый заход не-владельца
     давал бы гарантированный отказ в консоли и лишнюю нагрузку на аналитику.
     Проверяется аргумент `enabled`, а не только разметка: мутация «запрашивать всегда»
     не роняла ни одного теста, пока проверялся лишь вид экрана. */
  it("не владельцу запрос метрик даже не отправляется", () => {
    useProfileMock.mockReturnValue(idle({ email: "user@test.io", is_owner: false }));
    render(<InsightsPage />);
    expect(useOverviewMock).toHaveBeenCalledWith(false);
    expect(useFunnelMock).toHaveBeenCalledWith(false);
  });

  /* Загрузка — скелетон, как на остальных одиннадцати экранах: одноимённое состояние
     обязано выглядеть одинаково везде ([ST-02]/[ST-06], design-critic). */
  it("во время загрузки показывает скелетон, а не свой текст", () => {
    useOverviewMock.mockReturnValue({ data: undefined, isLoading: true, isError: false });
    const { container } = render(<InsightsPage />);
    expect(container.querySelector(".fp-skeleton, [class*=skeleton]")).not.toBeNull();
  });

  it("отказ объяснён и предлагает повтор", () => {
    useOverviewMock.mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
      error: new Error("network"),
      refetch: vi.fn(),
    });
    render(<InsightsPage />);
    expect(screen.getByText(/Не удалось загрузить/)).toBeVisible();
    // «Повторить» — как на остальных экранах, а не своя формулировка ([CMP-03]).
    expect(screen.getByRole("button", { name: /Повторить/ })).toBeVisible();
  });

  /* Пустая аналитика — нормальное состояние нового продукта, а не сбой. Показывать
     нули без объяснения значит заставить владельца гадать, сломано ли. */
  it("пустые данные объяснены, а не показаны нулями молча", () => {
    useOverviewMock.mockReturnValue(
      idle({ period_days: 30, total_events: 0, active_users: 0, event_counts: {} }),
    );
    // Пусто — только когда нет НИ событий, НИ воронки: иначе пустая сводка спрятала бы
    // воронку с данными (design-critic).
    useFunnelMock.mockReturnValue(idle({ period_days: 30, steps: [] }));
    render(<InsightsPage />);
    expect(screen.getByText(/событий за период пока нет/i)).toBeVisible();
  });

  /* Отказ в доступе блокирует работу целиком — объявлять его наравне с «загружаем…»
     значит рискнуть, что человек на скринридере его не услышит (a11y-auditor). */
  it("отказ в доступе объявляется как блокирующий, а не как статус", () => {
    useProfileMock.mockReturnValue(idle({ email: "user@test.io", is_owner: false }));
    render(<InsightsPage />);
    expect(screen.getByRole("alert")).toHaveTextContent(/Раздел закрыт/);
  });

  /* Пустая воронка — состояние, а не баг: события ещё не набрались. Пустой список
     без пояснения читается как поломка. */
  it("пустая воронка объяснена, а не показана пустым списком", () => {
    useFunnelMock.mockReturnValue(idle({ steps: [] }));
    render(<InsightsPage />);
    expect(screen.getByText(/Шаги воронки пока не набрали данных/)).toBeVisible();
  });
});

/**
 * Отказы и неполные данные — непокрытый остаток экрана метрик.
 *
 * 🔴 **Экран владельца, и он читает по нему решения о продукте.** Пустое место
 * вместо воронки означает не «ноль пользователей», а «не загрузилось» — разница
 * определяет, будет ли владелец что-то менять в продукте.
 */
describe("InsightsPage — отказы и неполные данные", () => {
  it("сбой обеих загрузок даёт «Повторить», и она обновляет ОБА запроса", async () => {
    /* Метрики и воронка — два независимых запроса на одном экране. Повтор,
       обновляющий только один, оставит половину экрана в отказе. */
    const overviewRefetch = vi.fn();
    const funnelRefetch = vi.fn();
    useOverviewMock.mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
      error: new Error("500"),
      refetch: overviewRefetch,
    });
    useFunnelMock.mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
      error: new Error("500"),
      refetch: funnelRefetch,
    });
    render(<InsightsPage />);

    await userEvent.click(screen.getByRole("button", { name: /Повторить/ }));

    expect(overviewRefetch).toHaveBeenCalled();
    expect(funnelRefetch).toHaveBeenCalled();
  });

  it("пустая воронка не роняет экран", () => {
    /* `funnel.data?.steps ?? []` — у нового продукта событий ещё нет,
       и это обычное состояние, а не сбой. */
    useFunnelMock.mockReturnValue(idle({ period_days: 30, steps: [] }));
    expect(() => render(<InsightsPage />)).not.toThrow();
  });

  it("сводка без `period_days` берёт 30 по умолчанию, а не показывает пусто", () => {
    /* `data?.period_days ?? 30` — заголовок обязан назвать период при любом ответе:
       «Сводка за дней» читается как поломка вёрстки. Поле необязательно
       по контракту, значит случай достижим. */
    useOverviewMock.mockReturnValue(idle({ ...OVERVIEW, period_days: undefined }));
    render(<InsightsPage />);
    expect(screen.getByText(/Сводка за 30 дней/)).toBeInTheDocument();
  });

  it("пока грузится профиль — экран не решает, владелец перед ним или нет", () => {
    useProfileMock.mockReturnValue({
      data: undefined,
      isLoading: true,
      isError: false,
      error: null,
    });
    render(<InsightsPage />);
    expect(screen.queryByText(/нет доступа|только владельц/i)).not.toBeInTheDocument();
  });
});
