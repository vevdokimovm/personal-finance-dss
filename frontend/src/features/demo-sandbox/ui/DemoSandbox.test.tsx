import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { DemoSandbox } from "./DemoSandbox";

const { useCasesMock, usePreviewMock, loadMock, invalidateMock, toastError } = vi.hoisted(() => ({
  useCasesMock: vi.fn(),
  usePreviewMock: vi.fn(),
  loadMock: vi.fn(),
  invalidateMock: vi.fn(),
  toastError: vi.fn(),
}));

vi.mock("@entities/demo", () => ({
  useDemoCases: () => useCasesMock(),
  useLoadDemoCase: () => ({ mutate: loadMock, isPending: false }),
  useDemoPreview: (key: string | null) => usePreviewMock(key),
}));

vi.mock("@tanstack/react-query", async () => {
  const actual =
    await vi.importActual<typeof import("@tanstack/react-query")>("@tanstack/react-query");
  return { ...actual, useQueryClient: () => ({ invalidateQueries: invalidateMock }) };
});

vi.mock("@shared/ui", async () => {
  const actual = await vi.importActual<typeof import("@shared/ui")>("@shared/ui");
  return { ...actual, toast: { ...actual.toast, error: toastError } };
});

const CASES = [
  {
    key: "anna",
    n: "1",
    name: "Анна Петрова, 36",
    role: "Маркетолог · Москва",
    tag: "Пограничный",
    accent: "amber",
    situation: "Доход 180 000 ₽, ипотека и автокредит, несколько целей.",
    expect: "Avalanche гасит дорогой долг, ликвидность держится выше нормы.",
  },
  {
    key: "mikhail",
    n: "3",
    name: "Михаил, 49",
    role: "Своя мастерская · Казань",
    tag: "Критический",
    accent: "red",
    situation: "Четыре кредита, платежи съедают почти весь доход.",
    expect: "Fail-loud: структурный диагноз вместо «красивой» рекомендации.",
  },
];

const PREVIEW = {
  metrics: { income_total: 180000, expense_total: 78000, free_resource: 39500, Lt: 0.5, Dt: 0.35 },
  plan: {
    risk_profile: "Сбалансированный",
    best: {
      explanation: {
        insight: "Рекомендуем направить 100% в подушку безопасности (39 500 ₽).",
        gains: ["В подушку откладываем 39 500 ₽ — это около 0,5 месяца расходов."],
        costs: [],
      },
    },
  },
  forecast: { trend: "improving", horizon: 6, current: { Rt: 39500 } },
};

beforeEach(() => {
  vi.clearAllMocks();
  usePreviewMock.mockReturnValue({ data: undefined, isLoading: false, isError: false });
  useCasesMock.mockReturnValue({
    data: { cases: CASES, keys: CASES.map((c) => c.key) },
    isLoading: false,
    isError: false,
    error: null,
  });
});

describe("DemoSandbox — гостевая песочница", () => {
  /* 🔴 Функция была в Jinja и потерялась при переносе на React (найдено в v8.45.0).
     README рекламирует «Демо за 30 секунд» как самый быстрый способ понять продукт —
     и это правда: данные считает реальный движок. Без этого входа посетитель без своих
     данных видит пустой дашборд и предложение ввести сотню операций руками. */
  it("показывает портреты с именем, ситуацией и ожидаемым результатом", () => {
    render(<DemoSandbox />);
    // Номер портрета рядом с именем: по нему сравнивают и говорят «начни с первого».
    expect(screen.getByText(/1\. Анна Петрова, 36/)).toBeVisible();
    expect(screen.getByText(/ипотека и автокредит/)).toBeVisible();
    // «Что покажет алгоритм» — до нажатия: человек выбирает похожего на себя, а не гадает.
    expect(screen.getByText(/Avalanche гасит дорогой долг/)).toBeVisible();
  });

  it("загружает выбранный портрет — после подтверждения", async () => {
    render(<DemoSandbox />);
    await userEvent.click(screen.getByRole("button", { name: /Михаил, 49/ }));
    await userEvent.click(screen.getByRole("button", { name: /Заменить и показать/ }));
    expect(loadMock.mock.calls[0][0]).toMatchObject({ caseKey: "mikhail" });
  });

  /* 🔴 После загрузки данные на экранах старые, пока кеш не сброшен. Человек нажимает
     «показать» и видит прежнюю пустоту — выглядит как сломанная кнопка. */
  it("после загрузки сбрасывает кеш, а не оставляет старые данные", async () => {
    loadMock.mockImplementation((_args, opts) => opts?.onSuccess?.({ detail: "ok" }));
    render(<DemoSandbox />);
    await userEvent.click(screen.getByRole("button", { name: /Анна Петрова/ }));
    await userEvent.click(screen.getByRole("button", { name: /Заменить и показать/ }));
    expect(invalidateMock).toHaveBeenCalled();
  });

  /* Портреты различаются по тяжести ситуации, и ярлык — единственное, что видно
     до чтения описания. Цвет приходит с сервера семантическим словом, не хексом. */
  it("ярлык ситуации показан и различает портреты", () => {
    render(<DemoSandbox />);
    expect(screen.getByText("Пограничный")).toBeVisible();
    expect(screen.getByText("Критический")).toBeVisible();
  });

  it("во время загрузки списка объясняет, что происходит", () => {
    useCasesMock.mockReturnValue({ data: undefined, isLoading: true, isError: false });
    render(<DemoSandbox />);
    expect(screen.getByText(/Загружаем/)).toBeVisible();
  });

  /* Отказ сети не должен превращать вход в продукт в пустое место: гость и так
     не понимает, что здесь должно было быть. */
  it("отказ объяснён и предлагает повтор", () => {
    useCasesMock.mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
      error: new Error("network"),
      refetch: vi.fn(),
    });
    render(<DemoSandbox />);
    expect(screen.getByText(/Не удалось загрузить/)).toBeVisible();
    expect(screen.getByRole("button", { name: /Попробовать снова/ })).toBeVisible();
  });

  /* 🔴 Сервер отдаёт 403 вошедшему: песочница не смешивается с настоящими данными
     (`routes_demo.py`). Показывать её вошедшему — это кнопка, ведущая в отказ. */
  it("вошедшему пользователю песочница не показывается", () => {
    render(<DemoSandbox isGuest={false} />);
    expect(screen.queryByText(/Анна Петрова, 36/)).not.toBeInTheDocument();
  });

  /* 🔴 Подпись обязана говорить ПРАВДУ о последствии. Первая редакция обещала
     «ваши они не заменят и никуда не сохранятся» — оба утверждения ложные:
     `/demo/load` вызывает `_clear_all` и жёстко удаляет всё, что гость успел внести,
     мимо мягкого удаления и отмены (`routes_demo.py:503`). Гость, набравший свои
     операции без регистрации, терял их одним нажатием (design-critic). */
  it("честно предупреждает, что демо ЗАМЕНИТ введённое", () => {
    render(<DemoSandbox />);
    expect(screen.getByText(/заменят всё, что вы уже внесли/)).toBeVisible();
  });

  /* Действие деструктивно и необратимо — значит спрашиваем подтверждение, а не грузим
     молча по одному клику ([FRM-07]). */
  it("перед заменой данных спрашивает подтверждение", async () => {
    render(<DemoSandbox />);
    await userEvent.click(screen.getByRole("button", { name: /Анна Петрова/ }));
    expect(loadMock).not.toHaveBeenCalled();
    /* Роль `dialog`, а не `alertdialog`: общая модалка продукта (`shared/ui/Modal`)
       даёт `dialog`, и заводить вторую реализацию ради одного экрана значило бы
       развести два диалога подтверждения в одном продукте ([CMP-01]). */
    expect(screen.getByRole("dialog")).toBeVisible();

    await userEvent.click(screen.getByRole("button", { name: /Заменить и показать/ }));
    expect(loadMock).toHaveBeenCalled();
  });

  it("отказ от подтверждения ничего не меняет", async () => {
    render(<DemoSandbox />);
    await userEvent.click(screen.getByRole("button", { name: /Анна Петрова/ }));
    await userEvent.click(screen.getByRole("button", { name: /Отмена/ }));
    expect(loadMock).not.toHaveBeenCalled();
  });

  /* 🔴 Грузится ОДИН портрет — гаснуть должен он, а не все десять. Первая редакция
     вешала `disabled` на весь список: экран читался как «всё сломалось», и было
     непонятно, какой именно портрет грузится ([FB-02]). */
  it("во время загрузки показывает, КАКОЙ портрет грузится", async () => {
    loadMock.mockImplementation(() => undefined);
    render(<DemoSandbox pendingKey="anna" />);
    expect(screen.getByRole("button", { name: /Анна Петрова/ })).toHaveAttribute(
      "aria-busy",
      "true",
    );
    expect(screen.getByRole("button", { name: /Михаил, 49/ })).not.toHaveAttribute("aria-busy");
  });

  /* 🔴 Предпросмотр — то, ради чего эта функция вообще возвращена из Jinja. Загрузка
     портрета СТИРАЕТ данные гостя мимо отмены, и без расчёта до нажатия человек выбирал
     вслепую по абзацу прозы. Сначала смотрит — потом решает. */
  it("расчёт портрета показывается ДО загрузки", async () => {
    usePreviewMock.mockReturnValue({ data: PREVIEW, isLoading: false, isError: false });
    render(<DemoSandbox />);

    // Кнопка своя у каждого портрета — берём первую (Анна).
    await userEvent.click(screen.getAllByRole("button", { name: /Показать расчёт/ })[0]);
    // Объяснение человеческим языком, а не голые числа: по нему и выбирают.
    expect(screen.getByText(/Рекомендуем направить 100%/)).toBeVisible();
    // И ничего не загрузилось: предпросмотр не трогает данные.
    expect(loadMock).not.toHaveBeenCalled();
  });

  /* Считать все десять портретов заранее — десять прогонов Монте-Карло ради того,
     что человек, скорее всего, не откроет. Запрос уходит по раскрытию. */
  it("расчёт не запрашивается, пока карточку не раскрыли", () => {
    render(<DemoSandbox />);
    expect(usePreviewMock).toHaveBeenCalledWith(null);
  });

  it("во время расчёта объясняет, что происходит", async () => {
    usePreviewMock.mockReturnValue({ data: undefined, isLoading: true, isError: false });
    render(<DemoSandbox />);
    await userEvent.click(screen.getAllByRole("button", { name: /Показать расчёт/ })[0]);
    expect(screen.getByText(/Считаем/)).toBeVisible();
  });
});
